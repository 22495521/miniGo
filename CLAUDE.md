# CLAUDE.md

本檔案提供 Claude Code 在此專案中工作的指引。

- 使用者以繁體中文溝通，commit 訊息與程式註解都用繁體中文。

## 專案概觀

miniGO 是全端專案，分為兩個獨立子專案：

- `frontend/` — Vue 3 + TypeScript + Vite，含 Vue Router、Pinia、ESLint、Prettier
- `backend/` — FastAPI，Python 相依一律由 **uv** 管理

目前功能：9x9 圍棋，玩家執黑對 RandomBot（白）。

## 圍棋引擎來自 go_example

棋盤規則與機器人用的是同層 `../go_example` 裡的 `dlgo` 套件，以 editable path dependency 引入（見 `backend/pyproject.toml` 的 `[tool.uv.sources]`）。在 go_example 改的程式 miniGO 會直接用到，但 `fastapi dev` 只監看 `backend/`，改了 dlgo 要手動重啟後端。不要把 dlgo 的檔案複製進 miniGO。

- 一律使用 `dlgo.goboard_fast`。`dlgo.agent.naive.RandomBot` 回傳的是 `dlgo.goboard.Move`，`app/services/game.py` 會轉成 `goboard_fast.Move`。
- 計分是 `dlgo.scoring` 的數子法、貼目 7.5，不判斷死子。
- 機器人是 `services/game.py` 模組層級的 `bot`，之後換成訓練好的模型時只要改這裡。

## 架構：無狀態後端

後端不保存棋局。前端（Pinia store `frontend/src/stores/game.ts`）保存落子紀錄 `moves`（如 `["E5","C3","pass"]`），每次請求都整串送給後端，後端從空棋盤重下（`services/game.py` 的 `Game.replay`），同時驗證每一手都合法。不能只傳盤面快照，因為打劫判定需要歷史盤面。

- `POST /api/game/state {size, moves}`：回傳盤面，用於開新局與悔棋。
- `POST /api/game/play {size, moves, move}`：玩家（黑）下一手，沒終局的話機器人接著回一手。
- 座標格式與 `dlgo.utils.COLS` 相同（跳過 I），第 1 行在最下面。回傳的 `board[0]` 是最上面一行（第 size 行）。
- 非法的手回 400，`detail` 是中文訊息，前端直接顯示。
- `captures.b` 是黑棋提掉的白子數。

前端檔案分工：

- `src/api/game.ts`：API 型別與 fetch 函式。
- `src/stores/game.ts`：對局狀態與動作（新局、落子、悔棋），悔棋是退回到上一次輪到黑棋的時候。
- `src/components/GoBoard.vue`：SVG 棋盤，只負責畫和發出 `play` 事件，不做規則判斷。
- `src/views/HomeView.vue`：對局頁面與側邊面板。
- 顏色都用 `src/assets/main.css` 的 CSS 變數，深色模式在同一檔的 `prefers-color-scheme: dark` 裡覆寫。

## 常用指令

後端（在 `backend/` 執行）：

```bash
uv sync                                      # 安裝相依
uv add <package>                             # 新增套件（不要用 pip）
uv add --dev <package>                       # 新增開發相依
uv run fastapi dev                           # 開發伺服器（自動找到 app/main.py，port 8000，熱重載）
uv run fastapi run                           # 正式模式啟動
uv run ruff check . && uv run ruff format .  # lint 與格式化
```

前端（在 `frontend/` 執行）：

```bash
npm install
npm run dev          # 開發伺服器，port 5173
npm run build        # 型別檢查 + production build
npm run lint
npm run format
```

## 慣例

- **Python 一律透過 uv**，不要使用 `pip`、`python -m venv`，也不要手動編輯 `uv.lock`。
- 後端程式碼放在 `backend/app/`，匯入一律從 `app.` 開頭，依職責分資料夾：
  - `main.py`：只負責建立 app、掛 middleware、例外處理與 router，不放業務邏輯。
  - `core/`：設定（`config.py`）與共用例外（`exceptions.py`）。
  - `api/routes/`：每個功能一個檔案，只做「收 request → 呼叫 service → 回 response」；新的 router 要加進 `api/router.py`（統一掛在 `/api` 下）。
  - `schemas/`：Pydantic 的 request／response 模型，依功能分檔。
  - `services/`：業務邏輯，例如 `services/game.py` 用 dlgo 重建對局。
  - 業務錯誤在 service 裡丟 `IllegalMoveError` 之類的例外，由 `core/exceptions.py` 的 handler 統一轉成 HTTP 回應，route 裡不寫 try/except。
- 設定值集中在 `backend/app/core/config.py` 的 `Settings`，由 `.env` 讀取；新增設定時同步更新 `.env.example`。
- 所有後端路由掛在 `/api` 前綴下；Vite 已把 `/api` 代理到 `http://localhost:8000`，前端呼叫時用相對路徑即可。
- 前端使用 `<script setup lang="ts">` 的 Composition API；`@/` 指向 `frontend/src/`。
- 不要提交 `.env`、`.venv/`、`node_modules/`、`dist/`。

## 完成前的驗證

改到後端就跑 `uv run ruff check .`；改到前端就跑 `npm run build` 與 `npm run lint`。確認通過後再回報完成。

專案刻意不寫自動化測試。改到 API 時，對執行中的後端實際打 `/api/game/state`、`/api/game/play` 確認行為。

## 開發環境（Windows）

- 使用者通常已在 VS Code 終端機開著後端（8000）與前端（5173）。不要關掉或重啟它們，直接對它們測試；需要另開伺服器時改用別的 port，用完要關掉。
- 這台機器的 `C:
vm4w
odejs
pm.ps1`、`npx.ps1` 已改名成 `.bak`，讓 PowerShell 在不改 Execution Policy 的情況下改用 `npm.cmd`。用 nvm 切換 Node 版本後可能要再改一次。
- Git Bash 裡 Python 輸出中文會變亂碼（cp950），執行時加上 `PYTHONIOENCODING=utf-8`，或改用 PowerShell。
