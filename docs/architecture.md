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
- `POST /api/nn/play {size, moves, move}`：玩家（黑）下一手，神經網路（白）接著回一手。模型未載入回 503，`size` 與 `NN_BOARD_SIZE` 不同回 400。前端的「神經網路」頁籤（`/nn`）用這兩支 API；前端的 `Mode` 多了 `'nn'`，但送給 `/api/game/play` 的只有 `bot`、`practice`（`api/game.ts` 的 `GameMode`）。

回傳格式定義在 `backend/app/schemas/game.py`，前端型別在 `frontend/src/api/game.ts`，兩邊要同步修改。容易弄錯的地方：

- 座標與 `dlgo.utils.COLS` 相同（跳過 I），第 1 行在最下面；但回傳的 `board[0]` 是最上面一行（第 size 行）。
- `captures.b` 是黑棋提掉的白子數。
- 非法的手回 400，`detail` 是中文訊息，前端直接顯示。盤面與規則以後端為準，前端不做規則判斷。

## 圍棋引擎（dl/ 的 dlgo）

棋盤規則與機器人來自 `dl/` 的 `dlgo` 套件，後端以 uv 的 editable path dependency 引入（`backend/pyproject.toml` 的 `[tool.uv.sources]` 指向 `../dl`）。`dl/` 是獨立的 uv 專案，細節見 dl.md。

- `dl/` 的修改後端會直接用到，但 `fastapi dev` 只監看 `backend/`，改了 dlgo 要手動重啟後端。
- 不要把 dlgo 的程式複製進 `backend/`；也不要為了網站去改 `dl/`，除非使用者要求。
- `Desktop/go_example` 是搬家前的舊資料夾，只當備份，不要再修改或引用它。
- 一律使用 `dlgo.goboard_fast`。`RandomBot` 回傳的是 `dlgo.goboard.Move`，`services/game.py` 會轉成 `goboard_fast.Move`，不要混用。
- 計分是 `dlgo.scoring` 的數子法、貼目 7.5，不判斷死子。
## 機器人

所有機器人都是 dlgo 的 `Agent`（提供 `select_move(game_state)`），集中在 `services/bots.py`；`Game.play_turn(text, bot)` 收到 `None` 就是練習模式。

- 隨機機器人：`random_bot`，由 `bot_for_mode()` 對應到 `/api/game/play` 的 `mode`。
- 神經網路：後端啟動時（`main.py` 的 lifespan）呼叫 `load_nn_agent()` 載入一次。`.env` 沒設定 `NN_MODEL_PATH` 時不載入，`/api/nn` 回 503；設定了就由 `build_nn_agent()` 用 `dlgo.agent.predict.load_prediction_agent` 讀 `dl/train_cnn.py` 存的權重檔（例如 `NN_MODEL_PATH=../dl/models/cnn_simple_5300.pt`，相對於 `backend/`）。編碼器與棋盤大小記在權重檔裡；棋盤大小跟 `NN_BOARD_SIZE` 不同時啟動就報錯。權重檔不進 git。
- 因此後端的一般相依有 **torch**（`dl/` 那邊只是 dev 相依）。`dlgo.agent.predict` 只在 `build_nn_agent()` 裡 import，沒設定模型時不會載入 torch。換模型只要改 `.env` 並重啟後端（`fastapi dev` 不會因 `.env` 改變而重載）。
- `NN_BOARD_SIZE` 在 `Settings` 裡是 `int` 加驗證，不能用 `Literal[9, 13, 19]`：從 `.env` 讀到的是字串，Literal 不會轉型，啟動會失敗。
