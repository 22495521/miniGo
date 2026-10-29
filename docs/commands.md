# 常用指令與驗證

後端（在 `backend/` 執行）：

```bash
uv sync                                      # 安裝相依
uv add <package>                             # 新增套件（不要用 pip）
uv add --dev <package>                       # 新增開發相依
uv run fastapi dev                           # 開發伺服器（自動找到 app/main.py，port 8000，熱重載）
uv run fastapi run                           # 正式模式啟動
uv run ruff check . && uv run ruff format .  # lint 與格式化
```

前端（在 `frontend/` 執行）：

```bash
npm install
npm run dev          # 開發伺服器，port 5173
npm run build        # 型別檢查 + production build
npm run lint
npm run format
```

## 完成前的驗證

- 改到後端：跑 `uv run ruff check .`。
- 改到前端：跑 `npm run build` 與 `npm run lint`。
- 專案刻意不寫自動化測試。改到 API 時，對執行中的後端實際打 `/api/game/state`、`/api/game/play` 確認行為。

確認通過後再回報完成。
