# CLAUDE.md

本檔案提供 Claude Code 在此專案中工作的指引。詳細內容拆在 `docs/`，在下方逐一匯入。

- 使用者以繁體中文溝通，commit 訊息與程式註解都用繁體中文。
- miniGO 是圍棋對弈網站：`frontend/`（Vue 3 + TypeScript）與 `backend/`（FastAPI，uv 管理）。目前是 9x9，玩家執黑對 RandomBot（白）。
- 修改程式時，若影響到下列文件描述的內容（資料夾、API、慣例、指令），同步更新對應的 `docs/*.md`；新增主題時在 `docs/` 開新檔案並加進下方清單。

## 文件

- 資料夾結構與職責：@docs/structure.md
- 架構、API 與圍棋引擎：@docs/architecture.md
- 程式慣例：@docs/conventions.md
- 指令、驗證與 Windows 環境：@docs/development.md
