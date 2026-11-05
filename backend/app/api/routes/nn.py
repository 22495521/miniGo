from fastapi import APIRouter

from app.core.config import settings
from app.schemas.nn import NNPlayRequest, NNPlayResponse, NNStatus
from app.services import bots
from app.services.game import Game
from app.services.nn import move_candidates

router = APIRouter(prefix="/nn", tags=["nn"])


@router.get("/status")
def status() -> NNStatus:
    """模型是否已載入，以及支援的棋盤大小。"""
    return NNStatus(ready=bots.nn_agent is not None, board_size=settings.nn_board_size)


@router.post("/play")
def play(req: NNPlayRequest) -> NNPlayResponse:
    """替輪到的一方下這一手，再回傳下一方每個點的機率。

    神經網路不會自己下，要下哪一手由前端從 candidates 挑，再用同一支 API 送回來。
    """
    agent = bots.get_nn_agent(req.size)
    game = Game.replay(req.size, req.moves)
    game.play(req.move)
    candidates = move_candidates(game, agent)
    return NNPlayResponse(**game.to_response().model_dump(), candidates=candidates)
