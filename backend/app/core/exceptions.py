from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class IllegalMoveError(ValueError):
    """落子紀錄或這一手不合法，回 400 給前端顯示。"""


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(IllegalMoveError)
    async def illegal_move_handler(request: Request, exc: IllegalMoveError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": str(exc)})
