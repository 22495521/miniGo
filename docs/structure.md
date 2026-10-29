# 資料夾結構

只記到資料夾層級，檔案清單直接看程式。新增檔案照這裡的分工放；資料夾職責有變動時同步更新本檔。

```
miniGO/
├── CLAUDE.md, docs/      給 AI 的指引
├── backend/app/          FastAPI，匯入一律從 app. 開頭
│   ├── main.py           只建立 app、掛 middleware、例外處理與 router
│   ├── core/             設定（config.py）與業務例外及其 handler（exceptions.py）
│   ├── api/routes/       每個功能一個 router，彙整在 api/router.py，統一掛在 /api 下
│   ├── schemas/          Pydantic request／response 模型，依功能分檔
│   └── services/         規則與業務邏輯，依功能分檔
└── frontend/src/         Vue 3 + TypeScript，@/ 指向這裡
    ├── api/              呼叫後端的函式與回傳型別，依功能分檔
    ├── stores/           Pinia setup store，依功能分檔
    ├── components/       可重用元件，不直接呼叫 API
    ├── views/            對應路由的頁面
    └── assets/main.css   全域樣式與 CSS 變數（含深色模式）
```

外部相依：同層的 `../go_example`（圍棋引擎 `dlgo`），見 architecture.md。
