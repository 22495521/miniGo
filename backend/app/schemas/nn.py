from typing import Literal

from pydantic import BaseModel

from app.schemas.game import GameResponse, StateRequest


class NNPlayRequest(StateRequest):
    move: str


class NNStatus(BaseModel):
    ready: bool
    # 模型只支援這個棋盤大小
    board_size: int


# 不能下的原因：已有棋子、自殺、打劫
IllegalReason = Literal["occupied", "suicide", "ko"]


class MoveCandidate(BaseModel):
    # 座標，例如 "Q16"
    move: str
    # 只在「可以下的點」之間重新分配的機率，可下的點加總為 1；不能下的點固定為 0
    prob: float
    # 模型原本的輸出（softmax），361 個點加總為 1，不能下的點也有值
    raw_prob: float
    legal: bool
    # legal 為 false 時說明原因，可以下時為 None
    reason: IllegalReason | None
    # 可以下，但會填掉自己的眼（通常不該下，由前端決定要不要跳過）
    own_eye: bool


class NNPlayResponse(GameResponse):
    # 輪到的一方每個點的機率：可以下的依 prob 由高到低排在前面，不能下的排在後面。
    # 對局結束時是空的
    candidates: list[MoveCandidate]
