"""用落子紀錄重建 dlgo 的對局，並轉成 API 回傳格式。

後端不保存棋局，每次請求都從空棋盤把 moves 重下一遍。
"""

from dlgo import goboard_fast as goboard
from dlgo.agent.naive import RandomBot
from dlgo.gotypes import Player, Point
from dlgo.scoring import compute_game_result
from dlgo.utils import COLS

from app.core.exceptions import IllegalMoveError
from app.schemas.game import Captures, GameResponse

PLAYER_CODE = {Player.black: "b", Player.white: "w"}

bot = RandomBot()


class Game:
    def __init__(self, size: int):
        self.size = size
        self.state = goboard.GameState.new_game(size)
        self.moves: list[str] = []
        self.captures = {Player.black: 0, Player.white: 0}

    @classmethod
    def replay(cls, size: int, moves: list[str]) -> "Game":
        game = cls(size)
        for i, text in enumerate(moves, start=1):
            try:
                game.play(text)
            except IllegalMoveError as e:
                raise IllegalMoveError(f"第 {i} 手 {text}：{e}") from e
        return game

    def play(self, text: str) -> None:
        move = self.parse_move(text)
        if self.state.is_over():
            raise IllegalMoveError("對局已經結束")
        if not self.state.is_valid_move(move):
            raise IllegalMoveError("這裡不能下（已有棋子、自殺或打劫）")
        self.apply(move)

    def play_turn(self, text: str) -> None:
        """玩家（黑）下一手，對局沒結束的話機器人（白）接著回一手。"""
        if self.state.next_player != Player.black:
            raise IllegalMoveError("現在不是黑棋的回合")
        self.play(text)
        if not self.state.is_over():
            self.play_bot()

    def play_bot(self) -> None:
        move = bot.select_move(self.state)
        # RandomBot 回傳的是 dlgo.goboard.Move，轉成 goboard_fast 的 Move
        self.apply(goboard.Move(point=move.point, is_pass=move.is_pass, is_resign=move.is_resign))

    def apply(self, move: goboard.Move) -> None:
        player = self.state.next_player
        opponent_before = self.count_stones(player.other)
        self.state = self.state.apply_move(move)
        self.captures[player] += opponent_before - self.count_stones(player.other)
        self.moves.append(self.format_move(move))

    def parse_move(self, text: str) -> goboard.Move:
        text = text.strip().upper()
        if text == "PASS":
            return goboard.Move.pass_turn()
        if text == "RESIGN":
            return goboard.Move.resign()
        try:
            point = Point(row=int(text[1:]), col=COLS.index(text[0]) + 1)
        except (ValueError, IndexError):
            raise IllegalMoveError("看不懂的座標，請用 E5、pass 或 resign") from None
        if not self.state.board.is_on_grid(point):
            raise IllegalMoveError("超出棋盤範圍")
        return goboard.Move.play(point)

    @staticmethod
    def format_move(move: goboard.Move) -> str:
        if move.is_pass:
            return "pass"
        if move.is_resign:
            return "resign"
        return f"{COLS[move.point.col - 1]}{move.point.row}"

    def count_stones(self, player: Player) -> int:
        board = self.state.board
        return sum(
            board.get(Point(row=r, col=c)) == player
            for r in range(1, self.size + 1)
            for c in range(1, self.size + 1)
        )

    def result(self) -> str | None:
        if not self.state.is_over():
            return None
        if self.state.last_move.is_resign:
            # 認輸後輪到的一方就是贏家
            return f"{PLAYER_CODE[self.state.next_player].upper()}+R"
        return str(compute_game_result(self.state))

    def to_response(self) -> GameResponse:
        board = self.state.board
        return GameResponse(
            size=self.size,
            moves=self.moves,
            board=[
                [PLAYER_CODE.get(board.get(Point(row=r, col=c))) for c in range(1, self.size + 1)]
                for r in range(self.size, 0, -1)
            ],
            next_player=PLAYER_CODE[self.state.next_player],
            last_move=self.moves[-1] if self.moves else None,
            captures=Captures(b=self.captures[Player.black], w=self.captures[Player.white]),
            is_over=self.state.is_over(),
            result=self.result(),
        )
