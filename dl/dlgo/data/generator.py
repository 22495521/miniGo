import glob
import numpy as np


class DataGenerator:
    def __init__(self, data_directory, samples, data_type='train'):
        self.data_directory = data_directory
        self.samples = samples
        self.data_type = data_type  # 'train' 或 'test'，決定讀哪一組分塊檔
        self.files = set(file_name for file_name, index in samples)
        self.num_samples = None

    def get_num_samples(self, batch_size=128, num_classes=19 * 19):
        if self.num_samples is not None:
            return self.num_samples
        else:
            self.num_samples = 0
            for X, y in self._generate(batch_size=batch_size, num_classes=num_classes):
                self.num_samples += X.shape[0]
            return self.num_samples

    def _generate(self, batch_size, num_classes):
        for zip_file_name in self.files:
            # 依 data_type 讀對應的分塊檔，寫死成 'train' 的話測試 generator 會讀到訓練資料
            file_name = zip_file_name.replace('.tar.gz', '') + self.data_type
            base = self.data_directory + '/' + file_name + '_features_*.npy'
            for feature_file in glob.glob(base):
                label_file = feature_file.replace('features', 'labels')
                x = np.load(feature_file)
                y = np.load(label_file)
                x = x.astype('float32')
                y = np.eye(num_classes, dtype="float32")[y.astype(int)]
                while x.shape[0] >= batch_size:
                    x_batch, x = x[:batch_size], x[batch_size:]
                    y_batch, y = y[:batch_size], y[batch_size:]
                    yield x_batch, y_batch


    def generate(self, batch_size=128, num_classes=19 * 19):
        while True:
            for item in self._generate(batch_size, num_classes):
                yield item
