
import glob
import random

import numpy as np
import torch
from torch.utils.data import IterableDataset, get_worker_info


def find_chunk_files(data_directory, samples, data_type='train'):
    """找出這些棋局所在壓縮檔的分塊檔（只找 samples 用到的壓縮檔，data/ 裡可能還有別次產生的分塊）。"""
    zip_names = sorted(set(file_name for file_name, index in samples))
    files = []
    for zip_name in zip_names:
        prefix = zip_name.replace('.tar.gz', '') + data_type
        files += sorted(glob.glob(data_directory + '/' + prefix + '_features_*.npy'))
    if not files:
        raise FileNotFoundError('找不到 %s 的分塊檔，先執行 load_kgs.py' % data_type)
    return files


class ChunkDataset(IterableDataset):
    def __init__(self, files, shuffle=True):
        # 只記住分塊檔的路徑，不讀任何資料
        self.files = list(files)
        self.shuffle = shuffle

    def __iter__(self):
        files = self.files
        # num_workers > 0 時每個 worker 都會跑一次 __iter__，要把分塊檔分給各個 worker，不然資料會重複。
        # 先固定切分再各自打亂，如果先打亂再切，各 worker 的亂數不同，會切出重疊的檔案
        worker = get_worker_info()
        if worker is not None:
            files = files[worker.id::worker.num_workers]

        files = list(files)
        if self.shuffle:
            random.shuffle(files)   # 每個 epoch 打亂分塊順序（PyTorch 會替每個 worker 設不同的種子）

        for feature_file in files:
            x = np.load(feature_file)   # 一次只讀一塊進記憶體
            y = np.load(feature_file.replace('features', 'labels'))
            order = torch.randperm(len(x)).tolist() if self.shuffle else range(len(x))
            for i in order:   # 塊內也打亂
                yield torch.from_numpy(x[i].astype(np.float32)), int(y[i])
            # 下一輪迴圈 x 指向新的一塊，舊的這塊沒有變數引用，就會被釋放
