# 開發環境（Windows）

- 使用者通常已在 VS Code 終端機開著後端（8000）與前端（5173）。不要關掉或重啟它們，直接對它們測試；需要另開伺服器時改用別的 port，用完要關掉。
- 這台機器的 `C:\nvm4w\nodejs\npm.ps1`、`npx.ps1` 已改名成 `.bak`，讓 PowerShell 在不改 Execution Policy 的情況下改用 `npm.cmd`。用 nvm 切換 Node 版本後可能要再改一次。
- Git Bash 裡 Python 輸出中文會變亂碼（cp950），執行時加上 `PYTHONIOENCODING=utf-8`，或改用 PowerShell。
- Desktop 本身也是一個 git repo，miniGO 是巢狀的獨立 repo；git 指令要在 miniGO 裡執行。
