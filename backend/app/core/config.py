from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "miniGO API"
    cors_origins: list[str] = ["http://localhost:5173"]

    # 神經網路權重檔路徑；沒設定時 /api/nn 回 503
    nn_model_path: str | None = None
    # 模型訓練時用的棋盤大小，/api/nn 只接受這個大小
    nn_board_size: Literal[9, 13, 19] = 19


settings = Settings()
