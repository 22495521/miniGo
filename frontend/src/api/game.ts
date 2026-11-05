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

// 神經網路對某一點的評估，對應後端 schemas/nn.py 的 MoveCandidate
export interface MoveCandidate {
  move: string
  // 只在可以下的點之間重新分配的機率（可下的點加總為 1）；不能下的點為 0
  prob: number
  // 模型原本的輸出，不能下的點也有值
  raw_prob: number
  legal: boolean
  // 不能下的原因：已有棋子、自殺、打劫
  reason: 'occupied' | 'suicide' | 'ko' | null
  // 可以下，但會填掉自己的眼
  own_eye: boolean
}

export interface NNPlayResponse extends GameState {
  // 輪到的一方每個點的評估：可以下的依 prob 由高到低在前，不能下的在後；對局結束時是空的
  candidates: MoveCandidate[]
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

// 替輪到的一方下這一手，回傳盤面與下一方每個點的機率。神經網路不會自己下，由前端挑
export function playNN(size: BoardSize, moves: string[], move: string) {
  return request<NNPlayResponse>('/nn/play', { size, moves, move })
}
