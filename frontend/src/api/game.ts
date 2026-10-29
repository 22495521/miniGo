export type Stone = 'b' | 'w'
// bot：玩家執黑對機器人；practice：沒有機器人，玩家輪流下黑白兩方
export type Mode = 'bot' | 'practice'
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

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`/api/game${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  const data = await res.json()
  if (!res.ok) {
    throw new Error(typeof data.detail === 'string' ? data.detail : '請求失敗')
  }
  return data as T
}

export function fetchState(size: BoardSize, moves: string[]) {
  return post<GameState>('/state', { size, moves })
}

export function playMove(size: BoardSize, moves: string[], move: string, mode: Mode) {
  return post<GameState>('/play', { size, moves, move, mode })
}
