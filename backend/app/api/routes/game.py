from fastapi import APIRouter

from app.schemas.game import GameResponse, PlayRequest, StateRequest
from app.services.game import Game

router = APIRouter(prefix="/game", tags=["game"])


@router.post("/state")
def get_state(req: StateRequest) -> GameResponse:
    """依落子紀錄回傳目前盤面，用於開新局與悔棋。"""
    return Game.replay(req.size, req.moves).to_response()


@router.post("/play")
def play(req: PlayRequest) -> GameResponse:
    """下一手；機器人模式下，RandomBot（白）會接著回一手。"""
    game = Game.replay(req.size, req.moves)
    game.play_turn(req.move, req.mode)
    return game.to_response()
