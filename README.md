# miniGO

Vue 3 前端 + FastAPI 後端的全端專案。

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
