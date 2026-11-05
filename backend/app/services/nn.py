"""用神經網路算出輪到的一方每個點的落子機率，並標出哪些點不能下。

要下哪一手由前端決定，後端只提供機率與是否可下。
"""

from typing import TYPE_CHECKING

from dlgo import goboard_fast as goboard
from dlgo.agent.helpers import is_point_an_eye

from app.schemas.nn import IllegalReason, MoveCandidate
from app.services.game import Game

if TYPE_CHECKING:
    # torch 很大，只在型別檢查時 import
    from dlgo.agent.predict import PredictionAgent


def move_candidates(game: Game, agent: "PredictionAgent") -> list[MoveCandidate]:
    state = game.state
    if state.is_over():
        return []

    raw = agent.predict(state)  # 361 個點的機率，索引跟 encoder.encode_point 一致
    player = state.next_player

    candidates = []
    for index, raw_prob in enumerate(raw):
        point = agent.encoder.decode_point_index(index)
        move = goboard.Move.play(point)
        reason = illegal_reason(state, player, move)
        candidates.append(
            MoveCandidate(
                move=Game.format_move(move),
                prob=0.0,
                raw_prob=float(raw_prob),
                legal=reason is None,
                reason=reason,
                own_eye=reason is None and is_point_an_eye(state.board, point, player),
            )
        )

    # 把不能下的點排除掉，剩下的重新分配成加總為 1
    legal_total = sum(c.raw_prob for c in candidates if c.legal)
    if legal_total > 0:
        for c in candidates:
            if c.legal:
                c.prob = c.raw_prob / legal_total

    # 可以下的在前（依 prob 由高到低），不能下的在後（依模型原本的機率）
    candidates.sort(key=lambda c: (not c.legal, -c.raw_prob))
    return candidates


def illegal_reason(state, player, move) -> IllegalReason | None:
    """跟 GameState.is_valid_move 的判斷相同，但分開回傳原因。"""
    if state.board.get(move.point) is not None:
        return "occupied"
    if state.is_move_self_capture(player, move):
        return "suicide"
    if state.does_move_violate_ko(player, move):
        return "ko"
    return None
