# 圍棋引擎（go_example 的 dlgo）

棋盤規則與機器人用的是同層 `../go_example` 裡的 `dlgo` 套件（跟著《Deep Learning and the Game of Go》實作的學習專案，有自己的 CLAUDE.md）。

- 以 editable path dependency 引入，見 `backend/pyproject.toml` 的 `[tool.uv.sources]`。在 go_example 改的程式 miniGO 會直接用到。
- `fastapi dev` 只監看 `backend/`，改了 dlgo 要手動重啟後端。
- 不要把 dlgo 的檔案複製進 miniGO，也不要為了 miniGO 去改 go_example，除非使用者要求。

## 使用上的注意

- 一律使用 `dlgo.goboard_fast`。`dlgo.agent.naive.RandomBot` 回傳的是 `dlgo.goboard.Move`，`services/game.py` 會轉成 `goboard_fast.Move`，不要混用不同模組的 `Move`。
- 計分是 `dlgo.scoring` 的數子法、貼目 7.5，不判斷死子。
- 機器人是 `services/game.py` 模組層級的 `bot`。之後換成 go_example 訓練好的 PyTorch 模型時只要改這裡；模型推論用的編碼器必須跟訓練時相同，直接用 `dlgo.encoders`。
