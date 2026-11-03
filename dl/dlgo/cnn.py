"""落子預測（policy）CNN 與權重檔的存讀。

訓練（train_cnn.py）和下棋的 agent（dlgo/agent/predict.py）共用這裡的定義，
兩邊的網路結構才會一致。依賴 torch，所以沒有放進 dlgo/__init__.py。
"""
import torch
from torch import nn


class GoCNN(nn.Module):
    """全卷積的落子預測網路。

    每層卷積都用 padding 保持盤面大小，最後用 1x1 卷積把每個點壓成一個分數，
    攤平後就是 H*W 個落點的 logits。沒有全連接層，參數少，盤面大小也不寫死。
    """

    def __init__(self, num_planes, channels=64, num_layers=6):
        super().__init__()
        layers = [nn.Conv2d(num_planes, channels, 5, padding=2), nn.BatchNorm2d(channels), nn.ReLU()]
        for _ in range(num_layers - 1):
            layers += [nn.Conv2d(channels, channels, 3, padding=1), nn.BatchNorm2d(channels), nn.ReLU()]
        self.body = nn.Sequential(*layers)
        self.head = nn.Conv2d(channels, 1, 1)

    def forward(self, x):
        # x：(B, num_planes, H, W) → (B, H*W)
        return self.head(self.body(x)).flatten(1)


def save_model(path, model, config):
    # 除了權重，也存建模型需要的設定，推論時才能建出一樣的網路、用一樣的編碼器
    torch.save({'model': model.state_dict(), 'config': config}, path)


def load_model(path, device='cpu'):
    """回傳 (model, config)。model 已切到 eval 模式。"""
    checkpoint = torch.load(path, map_location=device)
    config = checkpoint['config']
    model = GoCNN(config['num_planes'], config['channels'], config['layers']).to(device)
    model.load_state_dict(checkpoint['model'])
    model.eval()
    return model, config
