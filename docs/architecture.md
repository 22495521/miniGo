# 架構：無狀態後端

後端不保存棋局。前端（`frontend/src/stores/game.ts`）保存落子紀錄 `moves`（如 `["E5","C3","pass"]`），每次請求都整串送給後端；後端從空棋盤重下（`services/game.py` 的 `Game.replay`），同時驗證每一手都合法。

不能只傳盤面快照，因為打劫判定需要歷史盤面。重下的成本很低（19x19 三百手約毫秒等級），不用為了效能改成後端保存狀態。

## API

| 端點 | Body | 用途 |
|---|---|---|
| `POST /api/game/state` | `{size, moves}` | 回傳盤面，用於開新局與悔棋 |
| `POST /api/game/play` | `{size, moves, move}` | 玩家（黑）下一手，沒終局的話機器人（白）接著回一手 |
| `GET /api/health` | — | 健康檢查 |

回傳格式定義在 `backend/app/schemas/game.py`，前端對應的型別在 `frontend/src/api/game.ts`，兩邊要同步修改。

- `move` 可以是座標（`E5`）、`pass` 或 `resign`。
- 座標格式與 `dlgo.utils.COLS` 相同（跳過 I），第 1 行在最下面。
- 回傳的 `board[0]` 是棋盤最上面一行（第 size 行），值為 `"b"`、`"w"` 或 `null`。
- `captures.b` 是黑棋提掉的白子數。
- `result` 在終局時是 `"B+3.5"`、`"W+R"` 之類的字串，對局中為 `null`。
- 非法的手回 400，`detail` 是中文訊息，前端直接顯示。

## 之後要存檔時

在落子紀錄之外加上資料庫（例如 SQLite），存的格式一樣是 move list，不需要改動現有的 API。
