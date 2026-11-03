from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "miniGO API"
    cors_origins: list[str] = ["http://localhost:5173"]

    # 神經網路權重檔路徑；沒設定時 /api/nn 回 503
    nn_model_path: str | None = None
    # 模型訓練時用的棋盤大小，/api/nn 只接受這個大小
    # 不用 Literal[9, 13, 19]：.env 讀進來是字串 "19"，Literal 不會轉成整數，會驗證失敗
    nn_board_size: int = 19

    @field_validator("nn_board_size")
    @classmethod
    def check_board_size(cls, value: int) -> int:
        if value not in (9, 13, 19):
            raise ValueError("NN_BOARD_SIZE 只能是 9、13 或 19")
        return value


settings = Settings()
