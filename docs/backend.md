# 後端慣例

- **Python 一律透過 uv**，不要使用 `pip`、`python -m venv`，也不要手動編輯 `uv.lock`。
- 匯入一律從 `app.` 開頭。檔案放哪裡見 [project-structure.md](project-structure.md)。
- 分層：
  - `api/routes/` 只做「收 request → 呼叫 service → 回 response」，通常兩三行。新的 router 要加進 `api/router.py`。
  - 規則與業務邏輯都放 `services/`，例如「是不是黑棋的回合」由 `Game.play_turn()` 檢查。
  - request／response 模型放 `schemas/`。
- 錯誤處理：service 丟 `IllegalMoveError` 之類的例外，由 `core/exceptions.py` 的 handler 統一轉成 HTTP 回應，route 裡不寫 try/except。新的業務例外也定義在 `core/exceptions.py` 並註冊 handler。
- 設定值集中在 `core/config.py` 的 `Settings`，由 `.env` 讀取；新增設定時同步更新 `.env.example`。
- 所有路由都在 `/api` 前綴下。
- ruff 設定在 `pyproject.toml`（行寬 100，規則 E、F、I、UP）。
