"""用訓練好的落子預測 CNN 下棋。

依賴 torch，所以沒有放進 dlgo/agent/__init__.py，要用
from dlgo.agent.predict import load_prediction_agent。
"""
import numpy as np
import torch

from dlgo import goboard_fast as goboard
from dlgo.agent.base import Agent
from dlgo.agent.helpers import is_point_an_eye
from dlgo.cnn import load_model
from dlgo.encoders.base import get_encoder_by_name


class PredictionAgent(Agent):
    def __init__(self, model, encoder, board_size):
        super().__init__()
        self.model = model
        self.encoder = encoder
        self.board_size = board_size   # 模型訓練時的棋盤大小，只能下這個大小的棋

    @torch.no_grad()
    def predict(self, game_state):
        """回傳每個落點的機率（長度 H*W），索引跟 encoder.encode_point 一致。"""
        x = torch.from_numpy(np.asarray(self.encoder.encode(game_state), dtype=np.float32))
        logits = self.model(x.unsqueeze(0))[0]
        return torch.softmax(logits, dim=0).numpy()

    def select_move(self, game_state):
        probs = self.predict(game_state)
        # 照機率由高到低試，挑第一個合法、而且不是填自己眼的點。
        # 模型只學過「人會下哪裡」，不懂規則，所以機率最高的點可能不能下
        for index in np.argsort(-probs):
            point = self.encoder.decode_point_index(int(index))
            move = goboard.Move.play(point)
            if game_state.is_valid_move(move) and \
                    not is_point_an_eye(game_state.board, point, game_state.next_player):
                return move
        return goboard.Move.pass_turn()


def load_prediction_agent(model_path, device='cpu'):
    """讀 train_cnn.py 存的權重檔，用訓練時相同的編碼器建立 agent。"""
    model, config = load_model(model_path, device)
    encoder = get_encoder_by_name(config['encoder'], config['board_size'])
    return PredictionAgent(model, encoder, config['board_size'])
