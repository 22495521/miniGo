# 深度學習（dl/）

圍棋 AI 的程式：棋盤規則、編碼器與訓練資料管線。`dl/` 是獨立的 uv 專案，網站後端如何引用它見 architecture.md。

- 深度學習框架用 **PyTorch**，放在 `dl/` 的 dev 相依（`uv add --dev`）：`dl/` 裡 `uv sync` 會裝，把 `dl/` 當套件引用的網站後端不會裝。資料處理只用 numpy，例如 one-hot 用 `np.eye(n, dtype="float32")[y]`。
- `dlgo/gosgf/` 改自 gomill，是第三方程式，檔頭的出處標示要保留。

## 棋盤

`goboard_slow.py`、`goboard.py`、`goboard_fast.py` 都提供 `Move`、`GoString`、`Board`、`GameState`，介面相同：

- `goboard_slow.py`：最初的版本，打劫時比對整個盤面。目前沒有程式使用，留作學習紀錄。
- `goboard.py`：加上 Zobrist hashing。編碼器和 `RandomBot` 用的是它的 `Move`。
- `goboard_fast.py`：最佳化版，用預先算好的鄰點／角點表，依賴 `scoring.py` 和 `utils.MoveAge`。資料管線與網站後端都用它。

`zobrist.py` 是 `generate_zobrist.py` 產生的，不要手動編輯。它的 key 包含 `None`（空點），因為 `goboard_fast.py` 需要。

座標：`gotypes.Point(row, col)` 從 1 開始，numpy 陣列從 0 開始，所以編碼時是 `Point(r + 1, c + 1)`。`utils.print_board` 把第 1 行印在最下面，但 numpy 陣列的第 0 列在最上面。

## 編碼器（`dlgo/encoders/`）

`base.Encoder` 定義介面：`encode(game_state)` 回傳 `(num_planes, H, W)`；`encode_point` / `decode_point_index` 在 `Point` 與整數 `row_idx * width + col_idx` 之間轉換。`get_encoder_by_name(name, size)` 用 importlib 載入 `dlgo.encoders.<name>` 並呼叫模組層級的 `create(board_size)`，所以每個編碼器都必須提供 `create`。`encoders/__init__.py` 會 import 全部編碼器，新增時要加進去，刪除時也要從那裡拿掉，否則所有編碼器都載入失敗。

- `oneplane`：`(1, H, W)`，自己 = 1、對手 = -1、空點 = 0。
- `sevenplane`：`(7, H, W)`，0/1。第 0–2 層是自己剩 1、2、≥3 氣的棋子，第 3–5 層是對手的，第 6 層是打劫不能下的空點。
- `simple`：`(11, H, W)`，0/1，**以黑／白區分**。第 0–3 層是黑子剩 1、2、3、≥4 氣，第 4–7 層是白子，第 8／9 層在輪到黑／白時整層填 1，第 10 層是打劫。
- `tenplane`：`(10, H, W)`，依照使用者提供的論文（陽明交大 2024 碩士論文，ViT 模仿人類棋手）表 3.1 自己寫的，以黑／白區分：0 黑、1 白、2 不能下（含已有棋子、自殺、打劫）、3 輪到黑時整層 1、4 全 1、5 空點、6–9 最近 1–4 手的落點（沿著 `previous_state` / `last_move` 往回找）。資料管線擺讓子時，`last_move` 會是座標 tuple 而不是 `Move`，所以要用 `getattr(move, 'is_play', False)` 判斷。

除了 `simple` 和 `tenplane`，編碼器都以「自己／對手」區分（輪到下棋的一方是自己）。`sevenplane` 和 `simple` 依賴 `GoString.num_liberties` 和 `GameState.does_move_violate_ko`。

## 資料管線（`dlgo/data/`）

`index_processor.KGSIndex` 抓 KGS（https://u-go.net/gamerecords/）清單並下載 `.tar.gz` → `sampling.Sampler` 抽出訓練／測試棋局（測試集固定寫在 `test_samples.py`）→ `parallel_processor.GoDataProcessor` 用 `gosgf` 解析 SGF，以 `goboard_fast` 重下每一手，再用編碼器產生 features/labels（多個 process 平行處理）。

- 入口是 `load_kgs.py`，`parallel_processor.py` 和編碼器本身不能直接執行。
- 用到 multiprocessing，在 Windows 上呼叫端必須放在 `if __name__ == '__main__':` 裡。
- `load_go_data()` 一開始就會下載全部 55 個 KGS 壓縮檔。`load_kgs.py` 為了避開這點，自己依序呼叫 `Sampler.draw_data` → 只下載需要的檔案 → `map_to_workers` → `consolidate_games`。加 `--chunks-only` 時跳過 `consolidate_games`，只留分塊檔。
- `consolidate_games` 會把全部分塊讀進記憶體、labels 轉 one-hot 再合併，尖峰約是資料量的 2 倍，資料大時會爆。資料放不進記憶體時用 `--chunks-only` 加 `ChunkDataset`。
- `generator.DataGenerator` 有 `data_type` 參數，決定讀訓練或測試的分塊檔（寫死成 `'train'` 的話，測試 generator 會讀到訓練資料）。它照分塊順序輸出、不會打亂，每個分塊最後不滿 `batch_size` 的部分會被丟掉。PyTorch 訓練改用 `ChunkDataset`。
- `chunk_dataset.ChunkDataset(files, shuffle)`：PyTorch 的 `IterableDataset`，DataGenerator 的 PyTorch 版。一次只 `np.load` 一個分塊，回傳 float32 盤面與整數落點（直接給 `CrossEntropyLoss`）。分塊檔清單用 `find_chunk_files(data_dir, samples, data_type)` 取得，它只找 `samples` 所在壓縮檔的分塊（`data/` 可能留著別次產生的分塊，不能 glob 全部），所以訓練時要用跟 `load_kgs.py -n` 相同的盤數重新呼叫 `Sampler.draw_data`。直接傳檔案清單是為了能把訓練分塊再切出驗證集。每個 epoch 打亂分塊順序與塊內順序，但同一個 batch 只來自一兩個分塊，不是完全隨機。`num_workers > 0` 時用 `get_worker_info()` 把分塊檔**先固定切分再各自打亂**（先打亂再切會因各 worker 亂數不同而重疊）；沒有 `__len__`，`DataLoader` 不能設 `shuffle=True`。依賴 torch，所以沒放進 `dlgo/data/__init__.py`，要用 `from dlgo.data.chunk_dataset import ChunkDataset`。
- `Sampler` 的亂數種子固定是 1337，同樣的抽樣盤數每次都抽到同樣的棋局。
- 每個非讓子棋局的第一手（空棋盤）刻意不存成樣本。
- `parallel_processor.py` 的行為：分塊檔存成 features `int8`、labels `int16`（落點索引）。`process_zip` 會先開一個裝下該壓縮檔所有抽到棋局的陣列才切塊，用預設 float64 時盤數多（例如 5000 盤）會讓多個 worker 合計耗盡記憶體、分塊檔也大 8 倍；讀取端（`ChunkDataset`、`DataGenerator`、`consolidate_games`）都會轉成 float32。合併檔存成 `data/<train|test>_features.npy` / `_labels.npy`；pass 不計入樣本數；最後不滿 1024 的分塊也會存；每次都重新處理壓縮檔並先刪掉舊分塊，刻意不用快取，因為分塊檔沒有記錄抽到哪些棋局、用哪個編碼器。

## 訓練（`train_cnn.py`）

- 落子預測（policy）網路 `GoCNN`：全卷積，第一層 5x5、其餘 3x3，都有 BatchNorm + ReLU 並用 padding 保持盤面大小，最後 1x1 卷積壓成每點一個分數、攤平成 `H*W` 個 logits。不接全連接層，所以盤面大小不寫死。
- 資料用 `ChunkDataset` 逐塊讀分塊檔，需要先 `load_kgs.py --chunks-only`（或一般模式，分塊檔一樣會留著）。`-n`、`-e` 必須跟 `load_kgs.py` 相同：`-n` 決定抽到哪些棋局；分塊檔沒有記錄編碼器，所以啟動時用第一筆資料的形狀跟 `-e` 的 `encoder.shape()` 比對，不同就停止。測試分塊也要檢查：它只有加 `--test` 才會重新產生，換編碼器後沒加 `--test` 會留著舊編碼器的測試分塊，不先檢查會訓練完才在測試時出錯。
- 資料分三份，用途不能混：**訓練集**更新權重；**驗證集**從訓練分塊以固定種子切出 `--val-ratio`（預設 0.1，以分塊檔為單位），每輪評估一次、保留驗證準確率最好的一輪；**測試集**是固定 100 盤（`load_kgs.py --test`），全部訓練完才用最好的模型評估一次，不參與挑模型。沒有測試分塊時跳過測試。分塊檔太少切不出驗證集時會停止。以分塊切驗證集時，跨兩個分塊的那盤棋會同時出現在訓練與驗證，影響很小。
- 程式依階段分成 `load_datasets` → `train_one_epoch`（訓練）→ `evaluate`（驗證與測試共用，`model.eval()` + `no_grad`）→ `save_model` / `load_model`，`main` 依序呼叫。
- 存檔是 dict：`model`（state_dict）與 `config`（`encoder`、`board_size`、`num_planes`、`channels`、`layers`），用 `load_model(path, device)` 讀回。預設存到 `models/cnn_<編碼器>_<盤數>.pt`。
- `GoCNN`、`save_model`、`load_model` 定義在 `dlgo/cnn.py`，之後下棋的 agent 也要引用同一份，改網路結構只改那裡。依賴 torch，所以沒放進 `dlgo/__init__.py`。舊的權重檔要跟當時的結構相符才讀得回來。
- 判斷 `DataLoader` 是否存在要寫 `is not None`：包 `IterableDataset` 的 `DataLoader` 沒有長度，當成 bool 會呼叫 `len()` 而出錯。

## 訓練資料

- `data/`：KGS 棋譜與 `load_kgs.py` 的產出，不進 git。
- 產生方式：`uv run python load_kgs.py -n <盤數> -e <編碼器> [--test] [--chunks-only]`；`--test` 另外產生固定 100 盤測試集（約多下載 15 個檔）。KGS 棋譜只有 19 路。
- `generated_games/`：MCTS 自我對弈資料，9x9、oneplane 編碼，不進 git。`features-40k.npy` 是 `(N, 1, 9, 9)`；`features-20` / `features-200` 少了平面那一維，是 `(N, 9, 9)`，使用前要 reshape。labels 是 81 維 one-hot。這些檔案是外部產生的，repo 裡沒有產生它們的腳本。
