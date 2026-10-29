from dlgo.gotypes import Player
from fastapi import APIRouter, HTTPException

from app.game import Game, IllegalMoveError
from app.schemas import GameResponse, PlayRequest, StateRequest

router = APIRouter(prefix="/api/game", tags=["game"])


@router.post("/state")
def get_state(req: StateRequest) -> GameResponse:
    """依落子紀錄回傳目前盤面，用於開新局與悔棋。"""
    try:
        return Game.replay(req.size, req.moves).to_response()
    except IllegalMoveError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/play")
def play(req: PlayRequest) -> GameResponse:
    """玩家（黑）下一手，對局沒結束的話 RandomBot（白）接著回一手。"""
    try:
        game = Game.replay(req.size, req.moves)
        if game.state.next_player != Player.black:
            raise IllegalMoveError("現在不是黑棋的回合")
        game.play(req.move)
    except IllegalMoveError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    if not game.state.is_over():
        game.play_bot()
    return game.to_response()
