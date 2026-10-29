# 開發與驗證

## 指令

```bash
# backend/
uv sync                                      # 安裝相依
uv add <package>                             # 新增套件（--dev 為開發相依）
uv run fastapi dev                           # 開發伺服器，port 8000，熱重載
uv run ruff check . && uv run ruff format .  # lint 與格式化

# frontend/
npm install
npm run dev                                  # 開發伺服器，port 5173
npm run build                                # 型別檢查 + production build
npm run lint && npm run format
```

## 完成前的驗證

- 改到後端：`uv run ruff check .`。
- 改到前端：`npm run build` 與 `npm run lint`。
- 專案刻意不寫自動化測試。改到 API 時，對執行中的後端實際打 `/api/game/state`、`/api/game/play` 確認行為。

## Windows 環境

- 使用者通常已在 VS Code 終端機開著後端（8000）與前端（5173）。不要關掉或重啟它們，直接對它們測試；需要另開伺服器時改用別的 port，用完要關掉。
- `C:\nvm4w\nodejs\npm.ps1`、`npx.ps1` 已改名成 `.bak`，讓 PowerShell 不改 Execution Policy 也能用 `npm.cmd`。用 nvm 切換 Node 版本後可能要再改一次。
- Git Bash 裡 Python 輸出中文會變亂碼（cp950），執行時加 `PYTHONIOENCODING=utf-8`，或改用 PowerShell。
- Desktop 本身也是 git repo，miniGO 是巢狀的獨立 repo，git 指令要在 miniGO 裡執行。
