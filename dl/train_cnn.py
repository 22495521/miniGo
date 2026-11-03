"""用 CNN 訓練落子預測網路：輸入盤面，輸出每個落點的分數。

資料分成三份，用途不同：
    訓練集  KGS 抽出的 -n 盤棋（扣掉驗證集）        → 更新模型權重
    驗證集  從訓練分塊切出 --val-ratio 的比例        → 每輪訓練完評估一次，挑出最好的那一輪存檔
    測試集  固定的 100 盤（load_kgs.py --test 產生） → 全部訓練完才評估一次，回報最終成績

用法（-n、-e 要跟 load_kgs.py 相同）：
    uv run python load_kgs.py -n 100 -e tenplane --chunks-only --test
    uv run python train_cnn.py -n 100 -e tenplane --epochs 10
"""
import argparse
import contextlib
import io
import os
import random
import time

import torch
from torch import nn
from torch.utils.data import DataLoader

from dlgo.cnn import GoCNN, load_model, save_model   # 網路定義與存讀檔跟下棋的 agent 共用
from dlgo.data.chunk_dataset import ChunkDataset, find_chunk_files
from dlgo.data.sampling import Sampler
from dlgo.encoders.base import get_encoder_by_name

DATA_DIR = 'data'
MODEL_DIR = 'models'


# ============================================================
# 資料
# ============================================================

def load_datasets(num_games, val_ratio):
    """回傳 (訓練集, 驗證集, 測試集)。沒有測試分塊時，測試集是 None。"""
    # 用跟 load_kgs.py 相同的方式抽樣，才會找到同一批棋局的分塊（Sampler 的亂數種子固定）
    with contextlib.redirect_stdout(io.StringIO()):   # Sampler 會逐行印出檔名，關掉
        sampler = Sampler(data_dir=DATA_DIR)
        train_samples = sampler.draw_data('train', num_games)
        test_samples = sampler.draw_data('test', None)

    # 以分塊檔為單位切出驗證集。固定種子打亂，每次切法都一樣
    files = find_chunk_files(DATA_DIR, train_samples, 'train')
    random.Random(0).shuffle(files)
    num_val = max(1, round(len(files) * val_ratio))
    if num_val >= len(files):
        raise SystemExit('只有 %d 個分塊檔，不夠切出驗證集，請增加 -n' % len(files))
    train_set = ChunkDataset(files[num_val:], shuffle=True)
    val_set = ChunkDataset(files[:num_val], shuffle=False)

    try:
        test_set = ChunkDataset(find_chunk_files(DATA_DIR, test_samples, 'test'), shuffle=False)
    except FileNotFoundError:
        test_set = None

    return train_set, val_set, test_set


def check_encoder(dataset, encoder_name, name, hint):
    """分塊檔沒有記錄是哪個編碼器產生的，用第一筆資料的形狀跟 -e 比對。回傳單筆形狀。"""
    x, _ = next(iter(dataset))
    shape = tuple(x.shape)   # (num_planes, H, W)
    expected = tuple(get_encoder_by_name(encoder_name, shape[1]).shape())
    if shape != expected:
        raise SystemExit('%s分塊檔的形狀 %s 跟編碼器 %s 的 %s 不同。%s'
                         % (name, shape, encoder_name, expected, hint))
    return shape


def make_loader(dataset, batch_size, workers, device):
    # IterableDataset 不能設 shuffle=True，打亂由 ChunkDataset 自己做
    return DataLoader(dataset, batch_size=batch_size, num_workers=workers, pin_memory=(device == 'cuda'))


# ============================================================
# 訓練與評估
# ============================================================
PRINT_EVERY = 1000   # 每幾個 batch 印一次平均 loss（一輪約 7000 個 batch）


def train_one_epoch(model, loader, loss_fn, optimizer, device, epoch):
    """跑過一次訓練集、更新權重。回傳 (平均 loss, 正確數, 總數)"""
    model.train()
    running_loss = 0.0
    total_loss = 0.0
    correct = 0
    total = 0

    for i, (inputs, labels) in enumerate(loader):
        inputs, labels = inputs.to(device), labels.to(device)

        # zero the parameter gradients
        optimizer.zero_grad()

        # forward + backward + optimize
        outputs = model(inputs)
        loss = loss_fn(outputs, labels)
        loss.backward()
        optimizer.step()

        # print statistics
        running_loss += loss.item()
        total_loss += loss.item() * labels.size(0)
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()
        if i % PRINT_EVERY == PRINT_EVERY - 1:
            print(f'[{epoch}, {i + 1:5d}] loss: {running_loss / PRINT_EVERY:.3f}')
            running_loss = 0.0

    return total_loss / total, correct, total


@torch.no_grad()
def evaluate(model, loader, loss_fn, device):
    """不更新權重，只算 loss 和正確數（驗證集、測試集共用）。回傳 (平均 loss, 正確數, 總數)"""
    model.eval()   # BatchNorm 改用訓練時累積的統計值
    test_loss = 0.0
    correct = 0
    total = 0

    for inputs, labels in loader:
        inputs, labels = inputs.to(device), labels.to(device)

        outputs = model(inputs)
        loss = loss_fn(outputs, labels)

        test_loss += loss.item() * labels.size(0)
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()

    return test_loss / total, correct, total


def result_text(loss, correct, total):
    return f'loss: {loss:.3f} | Accuracy: {100. * correct / total:.2f}% ({correct}/{total})'


# ============================================================
# 主程式
# ============================================================

def parse_args():
    parser = argparse.ArgumentParser(description='用 CNN 訓練落子預測網路')
    parser.add_argument('--games', '-n', type=int, default=10, help='訓練盤數，要跟 load_kgs.py -n 相同')
    parser.add_argument('--encoder', '-e', default='sevenplane', help='編碼器，要跟 load_kgs.py -e 相同')
    parser.add_argument('--epochs', type=int, default=10)
    parser.add_argument('--batch-size', type=int, default=128)
    parser.add_argument('--lr', type=float, default=1e-3)
    parser.add_argument('--channels', type=int, default=64, help='每層卷積的通道數')
    parser.add_argument('--val-ratio', type=float, default=0.1, help='從訓練分塊切出多少比例當驗證集')
    parser.add_argument('--workers', type=int, default=2, help='DataLoader 的 worker 數，0 表示在主程式讀')
    parser.add_argument('--out', default=None, help='權重存檔路徑，預設 models/cnn_<編碼器>_<盤數>.pt')
    return parser.parse_args()


def main():
    args = parse_args()
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    out = args.out or os.path.join(MODEL_DIR, 'cnn_%s_%d.pt' % (args.encoder, args.games))
    os.makedirs(os.path.dirname(out) or '.', exist_ok=True)

    # ---- 1. 準備資料 ----
    train_set, val_set, test_set = load_datasets(args.games, args.val_ratio)
    num_planes, height, width = check_encoder(
        train_set, args.encoder, '訓練', '-e 要跟 load_kgs.py 一樣，或用 load_kgs.py -e %s 重新產生' % args.encoder)
    if test_set is not None:
        # 測試分塊只有加 --test 才會重新產生，換編碼器後可能還是舊的，先檢查，免得訓練完才在測試時出錯
        check_encoder(test_set, args.encoder, '測試',
                      '測試分塊是用別的編碼器產生的，load_kgs.py 加 --test 重新產生')
    train_loader = make_loader(train_set, args.batch_size, args.workers, device)
    val_loader = make_loader(val_set, args.batch_size * 2, args.workers, device)

    print(f'使用裝置: {device}，盤面 {(num_planes, height, width)}')
    print('分塊檔：訓練 %d、驗證 %d、測試 %s'
          % (len(train_set.files), len(val_set.files), len(test_set.files) if test_set is not None else '無'))

    # ---- 2. 建立模型 ----
    config = {'encoder': args.encoder, 'board_size': height, 'num_planes': num_planes,
              'channels': args.channels}
    model = GoCNN(num_planes, args.channels).to(device)   # 層數寫死在 dlgo/cnn.py（6 層）
    loss_fn = nn.CrossEntropyLoss()   # labels 是落點索引，直接用，不需要 one-hot
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)

    # ---- 3. 訓練：每輪訓練完用驗證集評估，保留驗證準確率最好的那一輪 ----
    best_val_acc = -1.0
    for epoch in range(1, args.epochs + 1):
        start = time.time()
        train_loss, train_correct, train_total = train_one_epoch(model, train_loader, loss_fn, optimizer, device, epoch)
        val_loss, val_correct, val_total = evaluate(model, val_loader, loss_fn, device)

        print(f'[Epoch {epoch} Train] {result_text(train_loss, train_correct, train_total)}')
        print(f'[Epoch {epoch} Val  ] {result_text(val_loss, val_correct, val_total)}  ({time.time() - start:.0f} 秒)')
        val_acc = val_correct / val_total
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            save_model(out, model, config)

    print('Finished Training')
    print(f'最好的驗證準確率: {100. * best_val_acc:.2f}%，模型存在 {out}')

    # ---- 4. 測試：載入最好的模型，用沒看過的測試集評估一次 ----
    if test_set is None:
        print('沒有測試資料，跳過測試（load_kgs.py 加 --test 產生）')
        return
    best_model, _ = load_model(out, device)
    test_loader = make_loader(test_set, args.batch_size * 2, args.workers, device)
    print('開始評估...')
    test_loss, test_correct, test_total = evaluate(best_model, test_loader, loss_fn, device)
    print(f'\n[Test Result] {result_text(test_loss, test_correct, test_total)}')
    print('Finished Testing')


if __name__ == '__main__':   # Windows 上 DataLoader 用多個 worker 時一定要有
    main()
