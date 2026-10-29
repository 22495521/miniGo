from fastapi import APIRouter

from app.api.routes import game, health, nn

api_router = APIRouter(prefix="/api")
api_router.include_router(health.router)
api_router.include_router(game.router)
api_router.include_router(nn.router)
