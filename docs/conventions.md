# 程式慣例

格式（Prettier、ruff）交給工具處理，這裡只記工具管不到的規則。

## 後端

- **Python 一律透過 uv**，不要使用 `pip`、`python -m venv`，也不要手動編輯 `uv.lock`。
- route 只做「收 request → 呼叫 service → 回 response」；規則判斷放在 service（例如輪到誰由 `Game.play_turn()` 檢查）。
- service 遇到業務錯誤就丟 `core/exceptions.py` 裡的例外，由那裡的 handler 統一轉成 HTTP 回應，route 裡不寫 try/except。新增例外時加進同檔的 `STATUS_CODES`（例外類別 → 狀態碼）。
- 設定值放在 `core/config.py` 的 `Settings`，由 `.env` 讀取；新增設定時同步更新 `.env.example`。

## 前端

- 使用 `<script setup lang="ts">` 的 Composition API。
- 呼叫後端一律透過 `src/api/` 的函式，用相對路徑 `/api/...`（Vite 會代理到 8000）。
- 顏色都用 `main.css` 的 CSS 變數，不要在元件裡寫死（棋子漸層除外）。
- 模式與棋盤大小存在 game store；模式由路由（`/bot`、`/practice`）決定，兩個路由共用 `GameView.vue`。切換模式或大小都會開新局。
- 悔棋：練習模式退一手；機器人模式退回到上一次輪到黑棋（玩家）的時候（手數為偶數時刪兩手，奇數時刪一手）。
