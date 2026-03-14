"""API路由"""
from fastapi import APIRouter

from app.api import (
    auth,
    accounts,
    market,
    trade,
    positions,
    strategies,
    risk,
    ai,
    statistics,
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(accounts.router)
api_router.include_router(market.router)
api_router.include_router(trade.router)
api_router.include_router(positions.router)
api_router.include_router(strategies.router)
api_router.include_router(risk.router)
api_router.include_router(ai.router)
api_router.include_router(statistics.router)
