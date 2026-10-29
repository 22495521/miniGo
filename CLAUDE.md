# CLAUDE.md

本檔案提供 Claude Code 在此專案中工作的指引。

## 專案概觀

miniGO 是全端專案，分為兩個獨立子專案：

- `frontend/` — Vue 3 + TypeScript + Vite，含 Vue Router、Pinia、ESLint、Prettier
- `backend/` — FastAPI，Python 相依一律由 **uv** 管理

## 常用指令

後端（在 `backend/` 執行）：

```bash
uv sync                                          # 安裝相依
uv add <package>                                 # 新增套件（不要用 pip）
uv add --dev <package>                           # 新增開發相依
uv run uvicorn app.main:app --reload --port 8000 # 啟動開發伺服器
uv run pytest                                    # 跑測試
uv run ruff check . && uv run ruff format .      # lint 與格式化
```

前端（在 `frontend/` 執行）：

```bash
npm install
npm run dev          # 開發伺服器，port 5173
npm run build        # 型別檢查 + production build
npm run lint
npm run format
```

## 慣例

- **Python 一律透過 uv**，不要使用 `pip`、`python -m venv`，也不要手動編輯 `uv.lock`。
- 後端程式碼放在 `backend/app/`，測試放在 `backend/tests/`，匯入一律從 `app.` 開頭。
- 設定值集中在 `backend/app/config.py` 的 `Settings`，由 `.env` 讀取；新增設定時同步更新 `.env.example`。
- 所有後端路由掛在 `/api` 前綴下；Vite 已把 `/api` 代理到 `http://localhost:8000`，前端呼叫時用相對路徑即可。
- 前端使用 `<script setup lang="ts">` 的 Composition API；`@/` 指向 `frontend/src/`。
- 不要提交 `.env`、`.venv/`、`node_modules/`、`dist/`。

## 完成前的驗證

改到後端就跑 `uv run pytest` 與 `uv run ruff check .`；改到前端就跑 `npm run build` 與 `npm run lint`。確認通過後再回報完成。
