from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class IllegalMoveError(ValueError):
    """落子紀錄或這一手不合法，回 400 給前端顯示。"""


class ModelNotReadyError(RuntimeError):
    """神經網路模型還沒設定或載入失敗，回 503。"""


# 例外類別 → HTTP 狀態碼
STATUS_CODES: dict[type[Exception], int] = {
    IllegalMoveError: 400,
    ModelNotReadyError: 503,
}


def register_exception_handlers(app: FastAPI) -> None:
    for exc_class, status_code in STATUS_CODES.items():

        async def handler(request: Request, exc: Exception, status_code: int = status_code):
            return JSONResponse(status_code=status_code, content={"detail": str(exc)})

        app.add_exception_handler(exc_class, handler)
