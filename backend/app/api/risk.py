"""风控API"""
from fastapi import APIRouter, Depends
from app.models import User
from app.api.deps import get_current_user

router = APIRouter(prefix="/risk", tags=["风控"])


@router.get("/check")
async def risk_check(current_user: User = Depends(get_current_user)):
    """风控检查"""
    # TODO: 实现风控检查逻辑
    return {
        "status": "ok",
        "max_position_percent": 10.0,
        "max_leverage": 3,
        "stop_loss_percent": 5.0,
        "max_daily_loss": 15.0,
    }


@router.get("/positions")
async def position_limits(current_user: User = Depends(get_current_user)):
    """仓位限制查询"""
    return {
        "max_position_percent": 10.0,
        "default_leverage": 3,
    }
