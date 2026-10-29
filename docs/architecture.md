# 架構

## 無狀態後端

後端不保存棋局。前端 store（`stores/game.ts`）保存落子紀錄 `moves`（如 `["E5","C3","pass"]`），每次請求都整串送給後端；後端從空棋盤重下（`services/game.py` 的 `Game.replay`），同時驗證每一手都合法。

不能只傳盤面快照，因為打劫判定需要歷史盤面。重下只要毫秒等級，不用為了效能改成後端保存狀態。之後要存檔時，再把同樣的 move list 存進資料庫即可。

## API

- `POST /api/game/state {size, moves}`：回傳盤面，用於開新局與悔棋。
- `POST /api/game/play {size, moves, move}`：玩家（黑）下一手，沒終局的話機器人（白）接著回一手。`move` 可以是 `E5`、`pass`、`resign`。

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
- 機器人是 `services/game.py` 模組層級的 `bot`。之後換成訓練好的模型時改這裡，推論用的編碼器必須跟訓練時相同（直接用 `dlgo.encoders`）。
