<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { RouterLink } from 'vue-router'
import { BOARD_SIZES } from '@/api/game'
import { useGameStore } from '@/stores/game'

const game = useGameStore()
const { size, loading } = storeToRefs(game)
</script>

<template>
  <header class="navbar">
    <div class="inner">
      <RouterLink to="/" class="brand">miniGO</RouterLink>

      <nav class="modes" aria-label="對局模式">
        <RouterLink :to="{ name: 'bot' }">隨機機器人</RouterLink>
        <RouterLink :to="{ name: 'practice' }">練習模式</RouterLink>
      </nav>

      <div class="sizes" role="group" aria-label="棋盤大小">
        <button
          v-for="s in BOARD_SIZES"
          :key="s"
          :class="{ active: s === size }"
          :aria-pressed="s === size"
          :disabled="loading"
          @click="game.setSize(s)"
        >
          {{ s }}×{{ s }}
        </button>
      </div>
    </div>
  </header>
</template>

<style scoped>
.navbar {
  position: sticky;
  top: 0;
  z-index: 10;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
}

.inner {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px 20px;
  max-width: 1040px;
  margin: 0 auto;
  padding: 10px 16px;
}

.brand {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 0.02em;
  color: var(--text);
  text-decoration: none;
}

.modes {
  display: flex;
  gap: 4px;
  margin-right: auto;
}

.modes a {
  padding: 6px 12px;
  border-radius: 8px;
  color: var(--text-muted);
  text-decoration: none;
  font-size: 15px;
  transition:
    background-color 0.15s,
    color 0.15s;
}

.modes a:hover {
  background: var(--surface-hover);
  color: var(--text);
}

.modes a.router-link-active {
  background: var(--surface-hover);
  color: var(--text);
  font-weight: 600;
}

.sizes {
  display: flex;
  padding: 3px;
  border-radius: 10px;
  background: var(--bg);
  border: 1px solid var(--border);
}

.sizes button {
  font: inherit;
  font-size: 14px;
  font-variant-numeric: tabular-nums;
  padding: 4px 10px;
  border: 0;
  border-radius: 7px;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
}

.sizes button:hover:not(:disabled) {
  color: var(--text);
}

.sizes button.active {
  background: var(--accent);
  color: var(--accent-text);
}

.sizes button:disabled {
  cursor: not-allowed;
}
</style>
