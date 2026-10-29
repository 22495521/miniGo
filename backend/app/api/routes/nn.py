from fastapi import APIRouter

from app.core.config import settings
from app.schemas.game import GameResponse
from app.schemas.nn import NNPlayRequest, NNStatus
from app.services import bots
from app.services.game import Game

router = APIRouter(prefix="/nn", tags=["nn"])


@router.get("/status")
def status() -> NNStatus:
    """模型是否已載入，以及支援的棋盤大小。"""
    return NNStatus(ready=bots.nn_agent is not None, board_size=settings.nn_board_size)


@router.post("/play")
def play(req: NNPlayRequest) -> GameResponse:
    """玩家（黑）下一手，對局沒結束的話神經網路（白）接著回一手。"""
    agent = bots.get_nn_agent(req.size)
    game = Game.replay(req.size, req.moves)
    game.play_turn(req.move, agent)
    return game.to_response()
