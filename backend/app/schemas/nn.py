from pydantic import BaseModel

from app.schemas.game import StateRequest


class NNPlayRequest(StateRequest):
    move: str


class NNStatus(BaseModel):
    ready: bool
    # 模型只支援這個棋盤大小
    board_size: int
