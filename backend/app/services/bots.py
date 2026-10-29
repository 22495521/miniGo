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
    """模型訓練好之後在這裡建立 agent。

    agent 本身建議寫在 go_example 的 dlgo/agent/（例如 dlgo/agent/predict.py），
    負責載入權重、用訓練時相同的編碼器編碼盤面、過濾不合法的點後選出一手。
    這裡只負責 import 並建立它，例如：

        from dlgo.agent.predict import load_prediction_agent
        return load_prediction_agent(model_path)
    """
    raise NotImplementedError(
        f"已設定 NN_MODEL_PATH={model_path}，但 app/services/bots.py 的 build_nn_agent() 還沒實作"
    )


def get_nn_agent(size: int) -> Agent:
    if nn_agent is None:
        raise ModelNotReadyError("神經網路模型尚未設定")
    if size != settings.nn_board_size:
        raise IllegalMoveError(f"神經網路模型只支援 {settings.nn_board_size} 路棋盤")
    return nn_agent
