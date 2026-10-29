# CLAUDE.md

本檔案提供 Claude Code 在此專案中工作的指引，涵蓋整個 repo（包括 `dl/`）。詳細內容拆在 `docs/`，在下方逐一匯入。專案只有這一份 CLAUDE.md 和根目錄的 README.md，不要在子資料夾另開。

- 使用者以繁體中文溝通，commit 訊息與程式註解都用繁體中文。
- **不要自己 commit。** 做完後回報改了什麼，由使用者決定何時 commit；只有使用者明確要求時才執行 `git commit`。
- miniGO 是圍棋對弈網站：`frontend/`（Vue 3 + TypeScript）、`backend/`（FastAPI，uv 管理），以及圍棋 AI 與訓練程式 `dl/`。有兩種模式：隨機機器人（玩家執黑對 RandomBot）與練習模式（沒有機器人，玩家輪流下黑白），棋盤可選 9、13、19 路。
- 修改程式時，若影響到下列文件描述的內容（資料夾、API、慣例、指令），同步更新對應的 `docs/*.md`；新增主題時在 `docs/` 開新檔案並加進下方清單。

## 文件

- 資料夾結構與職責：@docs/structure.md
- 架構、API 與圍棋引擎：@docs/architecture.md
- 程式慣例：@docs/conventions.md
- 深度學習（dl/：棋盤、編碼器、資料管線）：@docs/dl.md
- 指令、驗證與 Windows 環境：@docs/development.md

`docs/encoders.md` 是給人看的編碼器範例，刻意不匯入；需要時再讀。
