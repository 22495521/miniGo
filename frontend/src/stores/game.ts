import { ref } from 'vue'
import { defineStore } from 'pinia'
import {
  fetchNNStatus,
  fetchState,
  playMove,
  playNN,
  type BoardSize,
  type GameState,
  type Mode,
} from '@/api/game'

export const useGameStore = defineStore('game', () => {
  const mode = ref<Mode>('bot')
  const size = ref<BoardSize>(9)
  const state = ref<GameState | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  // 神經網路只支援模型訓練時的棋盤大小，進入 nn 模式時向後端查詢
  const nnBoardSize = ref<BoardSize>(19)

  // 切換模式或棋盤大小時，忽略還沒回來的舊請求
  let requestId = 0

  async function run(request: () => Promise<GameState>) {
    const id = ++requestId
    loading.value = true
    error.value = null
    try {
      const result = await request()
      if (id === requestId) state.value = result
    } catch (e) {
      if (id === requestId) error.value = e instanceof Error ? e.message : String(e)
    } finally {
      if (id === requestId) loading.value = false
    }
  }

  const moves = () => state.value?.moves ?? []

  function newGame() {
    return run(() => fetchState(size.value, []))
  }

  // 切換模式或棋盤大小都會開新局
  async function setMode(value: Mode) {
    if (value === mode.value && state.value) return
    mode.value = value
    if (value !== 'nn') return newGame()

    // 神經網路模式：先確認模型已載入，並換成模型支援的棋盤大小
    let ready = false
    try {
      const status = await fetchNNStatus()
      nnBoardSize.value = status.board_size
      ready = status.ready
    } catch {
      // 查不到狀態時照樣開局，下棋時後端會回錯誤訊息
    }
    if (mode.value !== 'nn') return // 等待期間已切到別的模式
    size.value = nnBoardSize.value
    await newGame()
    if (!ready && mode.value === 'nn') {
      error.value = '神經網路模型尚未載入：在 backend/.env 設定 NN_MODEL_PATH 後重啟後端'
    }
  }

  function setSize(value: BoardSize) {
    if (value === size.value && state.value) return
    if (mode.value === 'nn' && value !== nnBoardSize.value) return
    size.value = value
    return newGame()
  }

  function play(move: string) {
    if (loading.value || !state.value || state.value.is_over) return
    const m = mode.value
    return run(() =>
      m === 'nn' ? playNN(size.value, moves(), move) : playMove(size.value, moves(), move, m),
    )
  }

  // 練習模式退一手；有機器人的模式（隨機、神經網路）退回到上一次輪到黑棋（玩家）的時候
  function undo() {
    const n = moves().length
    if (loading.value || n === 0) return
    const keep = mode.value === 'practice' ? n - 1 : Math.max(0, n % 2 === 0 ? n - 2 : n - 1)
    return run(() => fetchState(size.value, moves().slice(0, keep)))
  }

  return {
    mode,
    size,
    state,
    loading,
    error,
    nnBoardSize,
    newGame,
    setMode,
    setSize,
    play,
    undo,
  }
})
