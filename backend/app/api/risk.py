"""风控API"""
from fastapi import APIRouter, Depends
from app.models import User
from app.api.deps import get_current_user

router = APIRouter(prefix="/risk", tags=["风控"])


@router.get("/check")
async def risk_check(current_user: User = Depends(get_current_user)):
    """
    风控检查 - 检查用户当前风险状态

    TODO: 实现真实风控检查逻辑（持仓、杠杆、亏损等）
    当前: 返回静态配置值
    """
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


@router.get("/config")
async def risk_config(current_user: User = Depends(get_current_user)):
    """获取风控配置"""
    return {
        "max_position_percent": 10.0,
        "max_leverage": 3,
        "stop_loss_percent": 5.0,
        "take_profit_percent": 10.0,
        "max_daily_loss": 15.0,
        "max_consecutive_losses": 3,
        "cooling_period_minutes": 60,
        "enable_circuit_breaker": True,
        "max_open_orders": 10,
    }
