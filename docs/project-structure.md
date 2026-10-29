# 資料夾結構

新增檔案時照這裡的分工放；結構有變動時同步更新本檔。

```
miniGO/
├── CLAUDE.md                 AI 指引入口，其餘內容從 docs/ 匯入
├── README.md                 給人看的簡介與啟動方式
├── docs/                     給 AI 的專案文件，每個主題一個檔案
├── backend/                  FastAPI（uv 管理）
│   ├── pyproject.toml        相依與 ruff 設定；[tool.uv.sources] 指向 ../../go_example
│   ├── .env.example          設定範本（.env 不進版控）
│   └── app/
│       ├── main.py           建立 app、掛 CORS、例外處理與 router，不放業務邏輯
│       ├── core/
│       │   ├── config.py     Settings（pydantic-settings，讀 .env）
│       │   └── exceptions.py 業務例外與轉成 HTTP 回應的 handler
│       ├── api/
│       │   ├── router.py     彙整所有 router，統一掛在 /api 下
│       │   └── routes/       每個功能一個檔案
│       │       ├── health.py GET  /api/health
│       │       └── game.py   POST /api/game/state、/api/game/play
│       ├── schemas/          Pydantic request／response 模型，依功能分檔
│       │   └── game.py
│       └── services/         業務邏輯，依功能分檔
│           └── game.py       用 dlgo 重下落子紀錄、機器人回一手
└── frontend/                 Vue 3 + TypeScript + Vite
    ├── vite.config.ts        /api 代理到 http://localhost:8000
    └── src/
        ├── main.ts           建立 app、掛 Pinia 與 router
        ├── App.vue           只放 <RouterView />
        ├── router/index.ts   路由表
        ├── api/              呼叫後端的函式與回傳型別，依功能分檔
        │   └── game.ts
        ├── stores/           Pinia store，依功能分檔
        │   └── game.ts       對局狀態（落子紀錄）與動作
        ├── components/       可重用元件，不直接呼叫 API
        │   └── GoBoard.vue   SVG 棋盤
        ├── views/            對應路由的頁面
        │   └── HomeView.vue  對局頁面與側邊面板
        └── assets/main.css   全域樣式與 CSS 變數（含深色模式）
```

外部相依：同層的 `../go_example`（圍棋引擎 `dlgo`），見 [go-engine.md](go-engine.md)。
