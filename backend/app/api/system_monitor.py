"""系统监控API"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.api.deps import get_current_user, get_db
from app.risk.system_monitor import SystemMonitor, quick_connection_check

router = APIRouter(prefix="/system-monitor", tags=["系统监控"])


@router.get("/status")
async def get_system_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取系统状态
    返回系统运行状态、交易所连接状态、待处理订单数等信息
    """
    monitor = SystemMonitor(db)
    status = await monitor.get_system_status()
    return status


@router.get("/connection-check")
async def check_connection(
    exchange: str = Query("okx", description="交易所ID，如 okx, binance 等"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    检查交易所连接状态
    """
    monitor = SystemMonitor(db)
    result = await monitor.check_exchange_connection(exchange)
    return result


@router.get("/connection-quick")
async def quick_check_connection(
    exchange: str = Query("okx", description="交易所ID")
):
    """
    快速检查交易所连接状态（不记录数据库）
    """
    result = await quick_connection_check(exchange)
    return result


@router.get("/pending-orders")
async def get_pending_orders(
    user_id: Optional[int] = Query(None, description="用户ID，不传则查询所有"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取未完成订单列表
    """
    monitor = SystemMonitor(db)

    # 如果传了user_id，检查权限
    target_user_id = user_id if user_id and current_user.is_superuser else current_user.id

    orders = await monitor.get_pending_orders(target_user_id)

    return {
        "count": len(orders),
        "orders": [
            {
                "id": o.id,
                "symbol": o.symbol,
                "side": o.side,
                "quantity": o.quantity,
                "status": o.status,
                "order_id": o.order_id,
                "created_at": o.created_at.isoformat() if o.created_at else None
            }
            for o in orders
        ]
    }


@router.post("/cancel-pending-orders")
async def cancel_pending_orders(
    user_id: Optional[int] = Query(None, description="用户ID，不传则取消当前用户订单"),
    account_id: Optional[int] = Query(None, description="账户ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    撤销所有未完成订单
    通常在检测到交易所连接失败时调用
    """
    # 权限检查
    target_user_id = user_id if user_id and current_user.is_superuser else current_user.id

    monitor = SystemMonitor(db)
    result = await monitor.cancel_pending_orders(
        user_id=target_user_id,
        account_id=account_id
    )
    return result


@router.post("/service-start")
async def record_service_start(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    记录服务启动
    用于服务启动时调用
    """
    monitor = SystemMonitor(db)
    status = await monitor.record_service_start()
    return {
        "message": "服务启动已记录",
        "status": status.status
    }


@router.post("/service-stop")
async def record_service_stop(
    reason: str = Query("manual", description="停止原因"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    记录服务停止
    用于服务停止时调用
    """
    monitor = SystemMonitor(db)
    status = await monitor.record_service_stop(reason)
    return {
        "message": "服务停止已记录",
        "status": status.status,
        "reason": reason
    }


@router.post("/check-recovery")
async def check_recovery(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    检查服务恢复状态
    当服务从错误/停止状态恢复时调用，检查并处理宕机期间的状态
    """
    monitor = SystemMonitor(db)
    recovery_info = await monitor.check_and_recover()
    return recovery_info
