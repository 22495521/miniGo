# 資料夾結構

只記到資料夾層級，檔案清單直接看程式。新增檔案照這裡的分工放；資料夾職責有變動時同步更新本檔。

```
miniGO/
├── CLAUDE.md, docs/      給 AI 的指引（docs/encoders.md 例外，是給人看的範例）
├── dl/                  圍棋 AI 與訓練，獨立的 uv 專案，見 dl.md
│   ├── dlgo/            棋盤、計分、agent、encoders/、data/（資料管線）、gosgf/（SGF 解析）
│   ├── load_kgs.py、check_data.py、generate_zobrist.py   可直接執行的腳本
│   └── data/、generated_games/   訓練資料，不進 git
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

後端引用 `dl/` 的 `dlgo` 作為圍棋引擎，見 architecture.md。
