# 架構

## 無狀態後端

後端不保存棋局。前端 store（`stores/game.ts`）保存落子紀錄 `moves`（如 `["E5","C3","pass"]`），每次請求都整串送給後端；後端從空棋盤重下（`services/game.py` 的 `Game.replay`），同時驗證每一手都合法。

不能只傳盤面快照，因為打劫判定需要歷史盤面。重下只要毫秒等級，不用為了效能改成後端保存狀態。之後要存檔時，再把同樣的 move list 存進資料庫即可。

## API

- `POST /api/game/state {size, moves}`：回傳盤面，用於開新局與悔棋。
- `POST /api/game/play {size, moves, move, mode}`：下一手，`move` 可以是 `E5`、`pass`、`resign`。
  - `mode: "bot"`（預設）：只能在輪到黑棋時下，沒終局的話機器人（白）接著回一手。
  - `mode: "practice"`：沒有機器人，替輪到的一方下這一手。
- `size` 只接受 9、13、19（`schemas/game.py` 的 `BoardSize`），其他值回 422。
- `GET /api/nn/status`：神經網路模型是否已載入（`ready`）與支援的棋盤大小。
- `POST /api/nn/play {size, moves, move}`：玩家（黑）下一手，神經網路（白）接著回一手。模型未載入回 503，`size` 與 `NN_BOARD_SIZE` 不同回 400。前端尚未串接。

回傳格式定義在 `backend/app/schemas/game.py`，前端型別在 `frontend/src/api/game.ts`，兩邊要同步修改。容易弄錯的地方：

- 座標與 `dlgo.utils.COLS` 相同（跳過 I），第 1 行在最下面；但回傳的 `board[0]` 是最上面一行（第 size 行）。
- `captures.b` 是黑棋提掉的白子數。
- 非法的手回 400，`detail` 是中文訊息，前端直接顯示。盤面與規則以後端為準，前端不做規則判斷。

## 圍棋引擎（go_example 的 dlgo）

棋盤規則與機器人來自同層 `../go_example` 的 `dlgo` 套件，以 uv 的 editable path dependency 引入（`backend/pyproject.toml` 的 `[tool.uv.sources]`）。

- go_example 的修改 miniGO 會直接用到，但 `fastapi dev` 只監看 `backend/`，改了 dlgo 要手動重啟後端。
- 不要把 dlgo 複製進 miniGO，也不要為了 miniGO 去改 go_example，除非使用者要求。
- 一律使用 `dlgo.goboard_fast`。`RandomBot` 回傳的是 `dlgo.goboard.Move`，`services/game.py` 會轉成 `goboard_fast.Move`，不要混用。
- 計分是 `dlgo.scoring` 的數子法、貼目 7.5，不判斷死子。
## 機器人

所有機器人都是 dlgo 的 `Agent`（提供 `select_move(game_state)`），集中在 `services/bots.py`；`Game.play_turn(text, bot)` 收到 `None` 就是練習模式。

- 隨機機器人：`random_bot`，由 `bot_for_mode()` 對應到 `/api/game/play` 的 `mode`。
- 神經網路：後端啟動時（`main.py` 的 lifespan）呼叫 `load_nn_agent()` 載入一次。`.env` 沒設定 `NN_MODEL_PATH` 時不載入，`/api/nn` 回 503；設定了就呼叫 `build_nn_agent()`，目前尚未實作，會在啟動時直接報錯。
- 接上模型的步驟：在 go_example 的 `dlgo/agent/` 寫好神經網路 agent（載入權重、用訓練時相同的編碼器、過濾不合法的點）→ 在 `build_nn_agent()` 裡 import 並建立 → `.env` 設定 `NN_MODEL_PATH` 與 `NN_BOARD_SIZE`。權重檔不進 git。
