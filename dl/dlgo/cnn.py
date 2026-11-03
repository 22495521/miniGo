"""落子預測（policy）CNN 與權重檔的存讀。

訓練（train_cnn.py）和下棋的 agent（dlgo/agent/predict.py）共用這裡的定義，
兩邊的網路結構才會一致。依賴 torch，所以沒有放進 dlgo/__init__.py。
"""
import re

import torch
import torch.nn as nn
import torch.nn.functional as F


# ============================================================
# 模型
# ============================================================
class GoCNN(nn.Module):
    """全卷積的落子預測網路：6 層卷積 + 1x1 輸出層。

    輸入 (B, num_planes, 19, 19)，輸出 (B, 361)：每個落點一個分數（logits）。
    每層卷積都用 padding 保持 19x19 的大小，所以不用池化、也沒有全連接層。
    """

    def __init__(self, num_planes, channels=64):
        super().__init__()
        self.conv1 = nn.Conv2d(num_planes, channels, 5, padding=2)   # 第一層看 5x5
        self.bn1 = nn.BatchNorm2d(channels)
        self.conv2 = nn.Conv2d(channels, channels, 3, padding=1)     # 之後每層看 3x3
        self.bn2 = nn.BatchNorm2d(channels)
        self.conv3 = nn.Conv2d(channels, channels, 3, padding=1)
        self.bn3 = nn.BatchNorm2d(channels)
        self.conv4 = nn.Conv2d(channels, channels, 3, padding=1)
        self.bn4 = nn.BatchNorm2d(channels)
        self.conv5 = nn.Conv2d(channels, channels, 3, padding=1)
        self.bn5 = nn.BatchNorm2d(channels)
        self.conv6 = nn.Conv2d(channels, channels, 3, padding=1)
        self.bn6 = nn.BatchNorm2d(channels)
        self.head = nn.Conv2d(channels, 1, 1)                        # 每個點壓成一個分數

    def forward(self, x):
        x = F.relu(self.bn1(self.conv1(x)))   # (B, channels, 19, 19)
        x = F.relu(self.bn2(self.conv2(x)))
        x = F.relu(self.bn3(self.conv3(x)))
        x = F.relu(self.bn4(self.conv4(x)))
        x = F.relu(self.bn5(self.conv5(x)))
        x = F.relu(self.bn6(self.conv6(x)))
        x = self.head(x)                      # (B, 1, 19, 19)
        x = torch.flatten(x, 1)               # (B, 361)
        return x


# ============================================================
# 模型存取
# ============================================================
def save_model(path, model, config):
    """儲存權重與建模型需要的設定（編碼器、棋盤大小、通道數），推論時才能建出一樣的網路"""
    torch.save({'model': model.state_dict(), 'config': config}, path)
    print(f'模型已儲存: {path}')


def load_model(path, device='cpu'):
    """載入權重，回傳 (model, config)。model 已切到 eval 模式。"""
    checkpoint = torch.load(path, map_location=device)
    config = checkpoint['config']
    model = GoCNN(config['num_planes'], config['channels']).to(device)
    model.load_state_dict(_rename_old_keys(checkpoint['model']))
    model.eval()
    print(f'已載入模型: {path}')
    return model, config


def _rename_old_keys(state_dict):
    """舊版 GoCNN 用 nn.Sequential，權重名稱是 body.0、body.1、body.3…，換成 conv1、bn1、conv2…。

    Sequential 裡每層依序是 Conv、BatchNorm、ReLU，所以第 i 個 Conv 在 body.(3i)、BatchNorm 在 body.(3i+1)。
    """
    renamed = {}
    for key, value in state_dict.items():
        match = re.match(r'body\.(\d+)\.(.+)', key)
        if match:
            index, rest = int(match.group(1)), match.group(2)
            layer = 'conv' if index % 3 == 0 else 'bn'
            key = '%s%d.%s' % (layer, index // 3 + 1, rest)
        renamed[key] = value
    return renamed
