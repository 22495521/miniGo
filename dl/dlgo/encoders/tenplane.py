import numpy as np

from dlgo.encoders.base import Encoder
from dlgo.goboard import Move
from dlgo.gotypes import Player, Point


BLACK = 0         # 黑子
WHITE = 1         # 白子
INVALID = 2       # 不能下的位置：已經有棋子、自殺、打劫
TURN = 3          # 輪到黑下時整層都是 1，輪到白下時整層都是 0
ONES = 4          # 整層都是 1，讓模型分得出棋盤邊界
EMPTY = 5         # 空點
RECENT = 6        # 6-9：最近 4 手的落點，第 6 層是最近一手
NUM_RECENT = 4


class TenPlaneEncoder(Encoder):
    def __init__(self, board_size):
        self.board_width, self.board_height = board_size
        self.num_planes = RECENT + NUM_RECENT

    def name(self):
        return 'tenplane'

    def encode(self, game_state):
        board_tensor = np.zeros(self.shape())
        board_tensor[ONES] = 1
        if game_state.next_player == Player.black:
            board_tensor[TURN] = 1

        for r in range(self.board_height):
            for c in range(self.board_width):
                p = Point(row=r + 1, col=c + 1)
                color = game_state.board.get(p)
                if color == Player.black:
                    board_tensor[BLACK][r][c] = 1
                    board_tensor[INVALID][r][c] = 1
                elif color == Player.white:
                    board_tensor[WHITE][r][c] = 1
                    board_tensor[INVALID][r][c] = 1
                else:
                    board_tensor[EMPTY][r][c] = 1
                    move = Move.play(p)
                    if game_state.is_move_self_capture(game_state.next_player, move) or \
                            game_state.does_move_violate_ko(game_state.next_player, move):
                        board_tensor[INVALID][r][c] = 1

        # 從目前的盤面往回找最近 4 手；pass 那一手的層留空
        state = game_state
        for i in range(NUM_RECENT):
            if state is None or state.last_move is None:
                break
            move = state.last_move
            # 資料管線擺讓子時，last_move 是座標 tuple 而不是 Move，這裡略過
            if getattr(move, 'is_play', False):
                board_tensor[RECENT + i][move.point.row - 1][move.point.col - 1] = 1
            state = state.previous_state
        return board_tensor

    def encode_point(self, point):
        return self.board_width * (point.row - 1) + (point.col - 1)

    def decode_point_index(self, index):
        row = index // self.board_width
        col = index % self.board_width
        return Point(row=row + 1, col=col + 1)

    def num_points(self):
        return self.board_width * self.board_height

    def shape(self):
        return self.num_planes, self.board_height, self.board_width


def create(board_size):
    return TenPlaneEncoder(board_size)
