import { ref } from 'vue'
import { defineStore } from 'pinia'
import { fetchState, playMove, type GameState } from '@/api/game'

export const useGameStore = defineStore('game', () => {
  const size = 9
  const state = ref<GameState | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function run(request: () => Promise<GameState>) {
    loading.value = true
    error.value = null
    try {
      state.value = await request()
    } catch (e) {
      error.value = e instanceof Error ? e.message : String(e)
    } finally {
      loading.value = false
    }
  }

  const moves = () => state.value?.moves ?? []

  function newGame() {
    return run(() => fetchState(size, []))
  }

  function play(move: string) {
    if (loading.value || !state.value || state.value.is_over) return
    return run(() => playMove(size, moves(), move))
  }

  // 退回到上一次輪到黑棋（玩家）的時候
  function undo() {
    const n = moves().length
    if (loading.value || n === 0) return
    const keep = Math.max(0, n % 2 === 0 ? n - 2 : n - 1)
    return run(() => fetchState(size, moves().slice(0, keep)))
  }

  return { state, loading, error, newGame, play, undo }
})
