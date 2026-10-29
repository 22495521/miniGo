# 深度學習（dl/）

圍棋 AI 的程式：棋盤規則、編碼器與訓練資料管線。`dl/` 是獨立的 uv 專案，網站後端如何引用它見 architecture.md。

- 深度學習框架用 **PyTorch**。資料處理只用 numpy，例如 one-hot 用 `np.eye(n, dtype="float32")[y]`。
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
- `load_go_data()` 一開始就會下載全部 55 個 KGS 壓縮檔。`load_kgs.py` 為了避開這點，自己依序呼叫 `Sampler.draw_data` → 只下載需要的檔案 → `map_to_workers` → `consolidate_games`。
- `generator.DataGenerator` 有 `data_type` 參數，決定讀訓練或測試的分塊檔（寫死成 `'train'` 的話，測試 generator 會讀到訓練資料）。它照分塊順序輸出、不會打亂，每個分塊最後不滿 `batch_size` 的部分會被丟掉。資料放得進記憶體時，改用 `np.load` 加上 `DataLoader(shuffle=True)`。
- `Sampler` 的亂數種子固定是 1337，同樣的抽樣盤數每次都抽到同樣的棋局。
- 每個非讓子棋局的第一手（空棋盤）刻意不存成樣本。
- `parallel_processor.py` 的行為：合併檔存成 `data/<train|test>_features.npy` / `_labels.npy`；pass 不計入樣本數；最後不滿 1024 的分塊也會存；每次都重新處理壓縮檔並先刪掉舊分塊，刻意不用快取，因為分塊檔沒有記錄抽到哪些棋局、用哪個編碼器。

## 訓練資料

- `data/`：KGS 棋譜與 `load_kgs.py` 的產出，不進 git。
- `generated_games/`：MCTS 自我對弈資料，9x9、oneplane 編碼，不進 git。`features-40k.npy` 是 `(N, 1, 9, 9)`；`features-20` / `features-200` 少了平面那一維，是 `(N, 9, 9)`，使用前要 reshape。labels 是 81 維 one-hot。
