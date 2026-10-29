from typing import Literal

from pydantic import BaseModel

Stone = Literal["b", "w"]
BoardSize = Literal[9, 13, 19]
# bot：玩家執黑對機器人；practice：沒有機器人，玩家輪流下黑白兩方
Mode = Literal["bot", "practice"]


class StateRequest(BaseModel):
    size: BoardSize = 9
    moves: list[str] = []


class PlayRequest(StateRequest):
    mode: Mode = "bot"
    move: str


class Captures(BaseModel):
    b: int
    w: int


class GameResponse(BaseModel):
    size: int
    moves: list[str]
    # board[0] 是棋盤最上面那一行（第 size 行），board[i][j] 為 "b"、"w" 或 None
    board: list[list[Stone | None]]
    next_player: Stone
    last_move: str | None
    # 各方提掉對手幾顆子
    captures: Captures
    is_over: bool
    # 終局結果，例如 "B+3.5"、"W+R"；對局中為 None
    result: str | None
