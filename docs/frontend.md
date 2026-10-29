# 前端慣例

- 使用 `<script setup lang="ts">` 的 Composition API；`@/` 指向 `frontend/src/`。
- 呼叫後端一律透過 `src/api/` 的函式，用相對路徑 `/api/...`（Vite 會代理到 8000）。元件不直接呼叫 `fetch`。
- 狀態放 Pinia store（`src/stores/`），用 setup store 寫法。對局只保存 `moves`，盤面以後端回傳的為準，前端不做規則判斷。
- 悔棋是退回到上一次輪到黑棋（玩家）的時候：手數為偶數時刪兩手，奇數時刪一手。
- `GoBoard.vue` 只負責畫棋盤並發出 `play` 事件，已有棋子的點不會發出事件，其他合法性由後端判斷。
- 顏色都用 `src/assets/main.css` 的 CSS 變數，深色模式在同一檔的 `prefers-color-scheme: dark` 裡覆寫；不要在元件裡寫死顏色（棋子漸層除外）。
- Prettier：不加分號、單引號、行寬 100。
