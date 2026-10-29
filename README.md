# miniGO

Vue 3 前端 + FastAPI 後端的圍棋對弈網站，可以對隨機機器人或練習模式（自己下黑白），棋盤有 9、13、19 路。

圍棋引擎（`dlgo`）與訓練程式放在 `dl/`，後端以 uv 的 editable path dependency 引入。

## 結構

```
miniGO/
├── frontend/   Vue 3 + TypeScript + Vite + Pinia + Vue Router
├── backend/    FastAPI，以 uv 管理 Python 相依
├── dl/         圍棋 AI（dlgo）、資料管線與訓練資料，獨立的 uv 專案
└── docs/       架構、API、慣例等說明（也是給 Claude Code 的指引）
```

## 啟動網站

後端（http://localhost:8000）：

```bash
cd backend
uv sync
uv run fastapi dev
```

API 文件：http://localhost:8000/docs

前端（http://localhost:5173）：

```bash
cd frontend
npm install
npm run dev
```

前端的 `/api` 請求會由 Vite 代理到後端的 8000 埠。

## 深度學習（dl/）

圍棋 AI 的程式：棋盤規則、編碼器與訓練資料管線。`dl/` 是獨立的 uv 專案（Python 3.12），以下指令都在 `dl/` 裡執行。

```bash
cd dl
uv sync
```

### 產生訓練資料

從 KGS 圍棋伺服器（https://u-go.net/gamerecords/）下載真人棋譜（19x19），編碼成訓練資料：

```bash
uv run python load_kgs.py                       # 抽 10 盤，用 sevenplane 編碼
uv run python load_kgs.py -n 100 -e tenplane    # 抽 100 盤，用 tenplane 編碼
uv run python load_kgs.py -n 100 --test         # 一併產生測試資料
```

| 參數 | 意思 | 預設 |
|---|---|---|
| `-n`、`--games` | 抽幾**盤棋**（不是幾個盤面） | 10 |
| `-e`、`--encoder` | `oneplane`、`sevenplane`、`simple` 或 `tenplane` | `sevenplane` |
| `--test` | 一併產生固定的 100 盤測試資料 | 不產生 |

產出 `data/train_features.npy`（盤面，`(盤面數, 層數, 19, 19)`）與 `data/train_labels.npy`（落點，one-hot，`(盤面數, 361)`），訓練時直接 `np.load`。每次執行都會覆蓋上一次的結果；同樣的 `-n` 每次會抽到同樣的棋局。一盤棋大約 180 個盤面，用 sevenplane 時 100 盤約 180 MB。

另外 `generated_games/` 有一份 9x9、已用 oneplane 編碼好的自我對弈資料，可以直接 `np.load`。

### 檢查訓練資料

```bash
uv run python check_data.py data/train_features.npy data/train_labels.npy
```

自動判斷編碼器，檢查格式、圍棋規則（例如答案沒有下在已有棋子的位置）和各層內容是否一致，失敗時列出是第幾個盤面。

### 編碼器

| 編碼器 | 形狀（19x19） | 內容 |
|---|---|---|
| `oneplane` | `(1, 19, 19)` | 只有棋子位置 |
| `sevenplane` | `(7, 19, 19)` | 棋子位置 + 氣數 + 打劫，以自己／對手區分 |
| `simple` | `(11, 19, 19)` | 棋子位置 + 氣數 + 輪到誰 + 打劫，以黑／白區分 |
| `tenplane` | `(10, 19, 19)` | 棋子位置 + 不能下的點 + 輪到誰 + 最近 4 手，以黑／白區分（論文的做法） |

每一層的定義與盤面範例見 [docs/encoders.md](docs/encoders.md)。
