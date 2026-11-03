"""各模式使用的機器人。

所有機器人都是 dlgo 的 Agent，提供 select_move(game_state)。
"""

from dlgo.agent.base import Agent
from dlgo.agent.naive import RandomBot

from app.core.config import settings
from app.core.exceptions import IllegalMoveError, ModelNotReadyError
from app.schemas.game import Mode

random_bot = RandomBot()

# 神經網路 agent，由 load_nn_agent() 在後端啟動時載入一次
nn_agent: Agent | None = None


def bot_for_mode(mode: Mode) -> Agent | None:
    """練習模式沒有機器人，回傳 None。"""
    return random_bot if mode == "bot" else None


def load_nn_agent() -> None:
    global nn_agent
    if not settings.nn_model_path:
        return
    nn_agent = build_nn_agent(settings.nn_model_path)


def build_nn_agent(model_path: str) -> Agent:
    """讀 dl/train_cnn.py 存的權重檔，建立落子預測 agent。

    編碼器與棋盤大小記在權重檔裡，agent 會用訓練時相同的編碼器。
    torch 很大，只在有設定模型時才 import。
    """
    from dlgo.agent.predict import load_prediction_agent

    agent = load_prediction_agent(model_path)
    if agent.board_size != settings.nn_board_size:
        raise ValueError(
            f"{model_path} 是用 {agent.board_size} 路棋盤訓練的，"
            f"但 NN_BOARD_SIZE={settings.nn_board_size}"
        )
    return agent


def get_nn_agent(size: int) -> Agent:
    if nn_agent is None:
        raise ModelNotReadyError("神經網路模型尚未設定")
    if size != settings.nn_board_size:
        raise IllegalMoveError(f"神經網路模型只支援 {settings.nn_board_size} 路棋盤")
    return nn_agent
