import argparse
import contextlib
import glob
import io
import os
from urllib.request import urlretrieve

import numpy as np

from dlgo.data.index_processor import KGSIndex
from dlgo.data.parallel_processor import GoDataProcessor
from dlgo.data.sampling import Sampler

DATA_DIR = 'data'


# 只下載抽到的棋局所在的壓縮檔，不像 load_go_data() 會下載全部 55 個
def download_needed(samples, file_info):
    urls = {info['filename']: info['url'] for info in file_info}
    os.makedirs(DATA_DIR, exist_ok=True)
    for filename in sorted(set(name for name, _ in samples)):
        path = DATA_DIR + '/' + filename
        if os.path.isfile(path):
            continue
        print('下載 ' + filename)
        urlretrieve(urls[filename], path)


# 跟 load_go_data() 相同的步驟：編碼抽到的棋局，再合併成 data/<data_type>_features.npy 和 _labels.npy
def build(processor, data_type, samples, file_info, chunks_only):
    download_needed(samples, file_info)
    processor.map_to_workers(data_type, samples)
    if chunks_only:
        # 不合併：consolidate_games 會把全部資料讀進記憶體，資料大時會爆。訓練時用 ChunkDataset 逐塊讀
        files = []
        for zip_name in sorted(set(name for name, _ in samples)):
            prefix = zip_name.replace('.tar.gz', '') + data_type
            files += glob.glob(DATA_DIR + '/' + prefix + '_features_*.npy')
        total = sum(np.load(f, mmap_mode='r').shape[0] for f in files)   # mmap 只讀檔頭
        print('%s: %d 盤 → %d 個分塊檔，共 %d 個盤面（未合併）' % (data_type, len(samples), len(files), total))
        return
    features, labels = processor.consolidate_games(data_type, samples)
    print('%s: %d 盤 → features %s, labels %s' % (data_type, len(samples), features.shape, labels.shape))


def main():
    parser = argparse.ArgumentParser(description='從 KGS 真人棋譜產生訓練資料')
    parser.add_argument('--games', '-n', type=int, default=10, help='抽幾盤訓練棋局')
    parser.add_argument('--encoder', '-e', default='sevenplane', help='oneplane、sevenplane、simple 或 tenplane')
    parser.add_argument('--test', action='store_true', help='一併產生固定的 100 盤測試資料（約需下載 15 個檔案）')
    parser.add_argument('--chunks-only', action='store_true',
                        help='只產生分塊檔、不合併成 train_features.npy，資料大時用（訓練改用 ChunkDataset）')
    args = parser.parse_args()

    # KGSIndex 和 Sampler 會把 55 個檔名逐行印出來，這裡把它們關掉
    with contextlib.redirect_stdout(io.StringIO()):
        file_info = KGSIndex(data_directory=DATA_DIR).file_info
        sampler = Sampler(data_dir=DATA_DIR)
        train_samples = sampler.draw_data('train', args.games)
        test_samples = sampler.draw_data('test', None)

    processor = GoDataProcessor(encoder=args.encoder, data_directory=DATA_DIR)
    build(processor, 'train', train_samples, file_info, args.chunks_only)
    if args.test:
        build(processor, 'test', test_samples, file_info, args.chunks_only)


if __name__ == '__main__':
    main()
