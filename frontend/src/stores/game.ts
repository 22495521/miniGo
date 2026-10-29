import { ref } from 'vue'
import { defineStore } from 'pinia'
import { fetchState, playMove, type BoardSize, type GameState, type Mode } from '@/api/game'

export const useGameStore = defineStore('game', () => {
  const mode = ref<Mode>('bot')
  const size = ref<BoardSize>(9)
  const state = ref<GameState | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

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
  function setMode(value: Mode) {
    if (value === mode.value && state.value) return
    mode.value = value
    return newGame()
  }

  function setSize(value: BoardSize) {
    if (value === size.value && state.value) return
    size.value = value
    return newGame()
  }

  function play(move: string) {
    if (loading.value || !state.value || state.value.is_over) return
    return run(() => playMove(size.value, moves(), move, mode.value))
  }

  // 練習模式退一手；機器人模式退回到上一次輪到黑棋（玩家）的時候
  function undo() {
    const n = moves().length
    if (loading.value || n === 0) return
    const keep = mode.value === 'practice' ? n - 1 : Math.max(0, n % 2 === 0 ? n - 2 : n - 1)
    return run(() => fetchState(size.value, moves().slice(0, keep)))
  }

  return { mode, size, state, loading, error, newGame, setMode, setSize, play, undo }
})
