from typing import Literal

from pydantic import BaseModel, Field

Stone = Literal["b", "w"]


class StateRequest(BaseModel):
    size: int = Field(default=9, ge=5, le=19)
    moves: list[str] = []


class PlayRequest(StateRequest):
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
