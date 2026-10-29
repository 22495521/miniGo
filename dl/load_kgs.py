import argparse
import contextlib
import io
import os
from urllib.request import urlretrieve

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
def build(processor, data_type, samples, file_info):
    download_needed(samples, file_info)
    processor.map_to_workers(data_type, samples)
    features, labels = processor.consolidate_games(data_type, samples)
    print('%s: %d 盤 → features %s, labels %s' % (data_type, len(samples), features.shape, labels.shape))


def main():
    parser = argparse.ArgumentParser(description='從 KGS 真人棋譜產生訓練資料')
    parser.add_argument('--games', '-n', type=int, default=10, help='抽幾盤訓練棋局')
    parser.add_argument('--encoder', '-e', default='sevenplane', help='oneplane、sevenplane、simple 或 tenplane')
    parser.add_argument('--test', action='store_true', help='一併產生固定的 100 盤測試資料（約需下載 15 個檔案）')
    args = parser.parse_args()

    # KGSIndex 和 Sampler 會把 55 個檔名逐行印出來，這裡把它們關掉
    with contextlib.redirect_stdout(io.StringIO()):
        file_info = KGSIndex(data_directory=DATA_DIR).file_info
        sampler = Sampler(data_dir=DATA_DIR)
        train_samples = sampler.draw_data('train', args.games)
        test_samples = sampler.draw_data('test', None)

    processor = GoDataProcessor(encoder=args.encoder, data_directory=DATA_DIR)
    build(processor, 'train', train_samples, file_info)
    if args.test:
        build(processor, 'test', test_samples, file_info)


if __name__ == '__main__':
    main()
