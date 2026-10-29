<script setup lang="ts">
import { computed, ref } from 'vue'
import type { Stone } from '@/api/game'

const props = defineProps<{
  board: (Stone | null)[][]
  lastMove: string | null
  disabled: boolean
}>()

const emit = defineEmits<{ play: [coord: string] }>()

const COLS = 'ABCDEFGHJKLMNOPQRST'
const CELL = 40
const MARGIN = 40

const size = computed(() => props.board.length)
const span = computed(() => CELL * (size.value - 1))
const viewSize = computed(() => span.value + MARGIN * 2)
const lines = computed(() => Array.from({ length: size.value }, (_, i) => MARGIN + i * CELL))

const starPoints = computed(() => {
  const n = size.value
  if (n < 9) return []
  const edge = n >= 13 ? 3 : 2
  const far = n - 1 - edge
  const mid = (n - 1) / 2
  const pts: [number, number][] = [
    [edge, edge],
    [edge, far],
    [far, edge],
    [far, far],
  ]
  if (n % 2 === 1) pts.push([mid, mid])
  if (n >= 19) pts.push([edge, mid], [far, mid], [mid, edge], [mid, far])
  return pts
})

// board[i][j]：i = 0 是最上面一行，也就是第 size 行
const coordOf = (i: number, j: number) => `${COLS[j]}${size.value - i}`
const pos = (index: number) => MARGIN + index * CELL

const stones = computed(() =>
  props.board.flatMap((row, i) =>
    row.flatMap((stone, j) => (stone ? [{ i, j, stone, coord: coordOf(i, j) }] : [])),
  ),
)

const hover = ref<{ i: number; j: number } | null>(null)

function onClick(i: number, j: number) {
  if (props.disabled || props.board[i]?.[j]) return
  emit('play', coordOf(i, j))
}
</script>

<template>
  <svg
    class="board"
    :class="{ disabled }"
    :viewBox="`0 0 ${viewSize} ${viewSize}`"
    role="img"
    aria-label="圍棋棋盤"
    @mouseleave="hover = null"
  >
    <defs>
      <radialGradient id="stone-b" cx="35%" cy="35%" r="65%">
        <stop offset="0%" stop-color="#5a5a5a" />
        <stop offset="100%" stop-color="#0d0d0d" />
      </radialGradient>
      <radialGradient id="stone-w" cx="35%" cy="35%" r="65%">
        <stop offset="0%" stop-color="#ffffff" />
        <stop offset="100%" stop-color="#cfcac0" />
      </radialGradient>
    </defs>

    <rect class="wood" :width="viewSize" :height="viewSize" rx="6" />

    <g class="grid">
      <line v-for="p in lines" :key="`h${p}`" :x1="MARGIN" :x2="MARGIN + span" :y1="p" :y2="p" />
      <line v-for="p in lines" :key="`v${p}`" :y1="MARGIN" :y2="MARGIN + span" :x1="p" :x2="p" />
    </g>

    <circle
      v-for="[i, j] in starPoints"
      :key="`s${i}-${j}`"
      class="star"
      :cx="pos(j)"
      :cy="pos(i)"
      r="4"
    />

    <g class="labels">
      <template v-for="(_, k) in size" :key="`l${k}`">
        <text :x="pos(k)" :y="MARGIN / 2">{{ COLS[k] }}</text>
        <text :x="pos(k)" :y="viewSize - MARGIN / 2">{{ COLS[k] }}</text>
        <text :x="MARGIN / 2" :y="pos(k)">{{ size - k }}</text>
        <text :x="viewSize - MARGIN / 2" :y="pos(k)">{{ size - k }}</text>
      </template>
    </g>

    <circle
      v-if="hover && !disabled && !board[hover.i]?.[hover.j]"
      class="ghost"
      :cx="pos(hover.j)"
      :cy="pos(hover.i)"
      :r="CELL * 0.46"
      fill="url(#stone-b)"
    />

    <g v-for="s in stones" :key="s.coord">
      <circle
        class="stone"
        :cx="pos(s.j)"
        :cy="pos(s.i)"
        :r="CELL * 0.46"
        :fill="`url(#stone-${s.stone})`"
      />
      <circle
        v-if="s.coord === lastMove"
        class="last"
        :class="s.stone"
        :cx="pos(s.j)"
        :cy="pos(s.i)"
        :r="CELL * 0.16"
      />
    </g>

    <g class="hits">
      <template v-for="(row, i) in board" :key="`r${i}`">
        <rect
          v-for="(_, j) in row"
          :key="`c${i}-${j}`"
          :x="pos(j) - CELL / 2"
          :y="pos(i) - CELL / 2"
          :width="CELL"
          :height="CELL"
          @mouseenter="hover = { i, j }"
          @click="onClick(i, j)"
        />
      </template>
    </g>
  </svg>
</template>

<style scoped>
.board {
  display: block;
  width: 100%;
  height: auto;
  user-select: none;
}

.wood {
  fill: var(--board-wood);
}

.grid line {
  stroke: var(--board-line);
  stroke-width: 1.2;
}

.star {
  fill: var(--board-line);
}

.labels text {
  fill: var(--board-label);
  font-size: 13px;
  text-anchor: middle;
  dominant-baseline: central;
}

.stone {
  filter: drop-shadow(1px 2px 1.5px rgb(0 0 0 / 0.35));
}

.ghost {
  opacity: 0.4;
  pointer-events: none;
}

.last {
  fill: none;
  stroke-width: 2.5;
}

.last.b {
  stroke: #f2f2f2;
}

.last.w {
  stroke: #1a1a1a;
}

.hits rect {
  fill: transparent;
  cursor: pointer;
}

.board.disabled .hits rect {
  cursor: default;
}
</style>
