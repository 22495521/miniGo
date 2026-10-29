# miniGO

Vue 3 前端 + FastAPI 後端的圍棋對弈網站，目前是 9x9 對 RandomBot。

圍棋引擎（`dlgo`）來自同層的 `../go_example`，後端以 uv 的 editable path dependency 引入，所以兩個資料夾要放在一起。

## 結構

```
miniGO/
├── frontend/   Vue 3 + TypeScript + Vite + Pinia + Vue Router
└── backend/    FastAPI，以 uv 管理 Python 相依
```

## 啟動

後端（http://localhost:8000）：

```bash
cd backend
uv sync
uv run fastapi dev
```

前端（http://localhost:5173）：

```bash
cd frontend
npm install
npm run dev
```

前端的 `/api` 請求會由 Vite 代理到後端的 8000 埠。

更多說明（架構、API、資料夾分工）見 [`docs/`](docs/)。
