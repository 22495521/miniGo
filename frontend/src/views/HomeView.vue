<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import GoBoard from '@/components/GoBoard.vue'
import { useGameStore } from '@/stores/game'

const game = useGameStore()
const { state, loading, error } = storeToRefs(game)

onMounted(() => {
  if (!state.value) game.newGame()
})

const status = computed(() => {
  const s = state.value
  if (!s) return ''
  if (s.is_over) return resultText(s.result)
  if (loading.value) return '機器人思考中…'
  return s.next_player === 'b' ? '輪到你（黑）' : '輪到機器人（白）'
})

function resultText(result: string | null) {
  if (!result) return '對局結束'
  const [winner, margin] = result.split('+')
  const who = winner === 'B' ? '你（黑）' : '機器人（白）'
  return margin === 'R' ? `${who}中盤勝` : `${who}勝 ${margin} 目`
}

const lastMoves = computed(() => {
  const moves = state.value?.moves ?? []
  return moves
    .map((move, i) => ({ n: i + 1, move, color: i % 2 === 0 ? 'b' : 'w' }))
    .slice(-10)
    .reverse()
})
</script>

<template>
  <main class="page">
    <section class="board-wrap">
      <GoBoard
        v-if="state"
        :board="state.board"
        :last-move="state.last_move"
        :disabled="loading || state.is_over"
        @play="game.play"
      />
    </section>

    <aside class="panel">
      <header>
        <h1>miniGO</h1>
        <p class="sub">9×9 · 你執黑，對手是 RandomBot</p>
      </header>

      <p class="status" :class="{ over: state?.is_over }" aria-live="polite">{{ status }}</p>
      <p v-if="error" class="error" role="alert">{{ error }}</p>

      <dl v-if="state" class="stats">
        <div>
          <dt><span class="dot b" />黑提子</dt>
          <dd>{{ state.captures.b }}</dd>
        </div>
        <div>
          <dt><span class="dot w" />白提子</dt>
          <dd>{{ state.captures.w }}</dd>
        </div>
        <div>
          <dt>手數</dt>
          <dd>{{ state.moves.length }}</dd>
        </div>
      </dl>

      <div class="actions">
        <button :disabled="loading || !state || state.is_over" @click="game.play('pass')">
          虛手（Pass）
        </button>
        <button :disabled="loading || !state?.moves.length" @click="game.undo()">悔棋</button>
        <button :disabled="loading || !state || state.is_over" @click="game.play('resign')">
          認輸
        </button>
        <button class="primary" :disabled="loading" @click="game.newGame()">新對局</button>
      </div>

      <section v-if="lastMoves.length" class="history">
        <h2>最近幾手</h2>
        <ol>
          <li v-for="m in lastMoves" :key="m.n">
            <span class="n">{{ m.n }}</span>
            <span class="dot" :class="m.color" />
            <span>{{ m.move }}</span>
          </li>
        </ol>
      </section>

      <p class="note">雙方連續虛手即終局，以數子法計算（貼目 7.5）。不會判斷死子。</p>
    </aside>
  </main>
</template>

<style scoped>
.page {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 24px;
  max-width: 1040px;
  margin: 0 auto;
  padding: 24px 16px 48px;
}

@media (min-width: 860px) {
  .page {
    grid-template-columns: minmax(0, 620px) 1fr;
    align-items: start;
    padding-top: 40px;
  }
}

.board-wrap {
  width: 100%;
  max-width: 620px;
  margin: 0 auto;
}

.panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

h1 {
  font-size: 28px;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.sub {
  color: var(--text-muted);
  font-size: 14px;
}

.status {
  font-size: 18px;
  font-weight: 600;
  padding: 12px 14px;
  border-radius: 10px;
  background: var(--surface);
  border: 1px solid var(--border);
}

.status.over {
  border-color: var(--accent);
}

.error {
  color: var(--danger);
  font-size: 14px;
}

.stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.stats div {
  padding: 10px 12px;
  border-radius: 10px;
  background: var(--surface);
  border: 1px solid var(--border);
}

.stats dt {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--text-muted);
  font-size: 13px;
}

.stats dd {
  font-size: 22px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: 1px solid #555;
}

.dot.b {
  background: #111;
}

.dot.w {
  background: #f5f5f0;
}

.actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

button {
  font: inherit;
  font-size: 15px;
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text);
  cursor: pointer;
  transition: background-color 0.15s;
}

button:hover:not(:disabled) {
  background: var(--surface-hover);
}

button:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

button.primary {
  background: var(--accent);
  border-color: var(--accent);
  color: var(--accent-text);
}

button.primary:hover:not(:disabled) {
  background: var(--accent-hover);
}

.history h2 {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-muted);
  margin-bottom: 6px;
}

.history ol {
  list-style: none;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(88px, 1fr));
  gap: 4px 12px;
  font-variant-numeric: tabular-nums;
}

.history li {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
}

.history .n {
  color: var(--text-muted);
  min-width: 2.2em;
  text-align: right;
}

.note {
  color: var(--text-muted);
  font-size: 13px;
  line-height: 1.6;
}
</style>
