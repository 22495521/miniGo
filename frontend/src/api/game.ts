export type Stone = 'b' | 'w'
// bot：玩家執黑對隨機機器人；practice：沒有機器人，玩家輪流下黑白兩方；
// nn：玩家執黑對神經網路（走 /api/nn，只支援模型訓練時的棋盤大小）
export type Mode = 'bot' | 'practice' | 'nn'
// /api/game/play 的 mode 只有這兩種，對應後端 schemas/game.py 的 Mode
export type GameMode = Exclude<Mode, 'nn'>
export type BoardSize = 9 | 13 | 19

export const BOARD_SIZES: BoardSize[] = [9, 13, 19]

export interface GameState {
  size: number
  moves: string[]
  // board[0] 是棋盤最上面那一行
  board: (Stone | null)[][]
  next_player: Stone
  last_move: string | null
  captures: Record<Stone, number>
  is_over: boolean
  result: string | null
}

export interface NNStatus {
  // 後端是否已載入模型（backend/.env 的 NN_MODEL_PATH）
  ready: boolean
  // 模型只支援這個棋盤大小
  board_size: BoardSize
}

async function request<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(`/api${path}`, {
    method: body === undefined ? 'GET' : 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body),
  })
  const data = await res.json()
  if (!res.ok) {
    throw new Error(typeof data.detail === 'string' ? data.detail : '請求失敗')
  }
  return data as T
}

export function fetchState(size: BoardSize, moves: string[]) {
  return request<GameState>('/game/state', { size, moves })
}

export function playMove(size: BoardSize, moves: string[], move: string, mode: GameMode) {
  return request<GameState>('/game/play', { size, moves, move, mode })
}

export function fetchNNStatus() {
  return request<NNStatus>('/nn/status')
}

// 玩家（黑）下一手，神經網路（白）接著回一手
export function playNN(size: BoardSize, moves: string[], move: string) {
  return request<GameState>('/nn/play', { size, moves, move })
}
