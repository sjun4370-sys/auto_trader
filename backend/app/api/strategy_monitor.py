"""策略运行监控 API"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta

from app.database import get_db
from app.models import User, Strategy, StrategyRun, Position, Order
from app.api.deps import get_current_user
from app.schemas import BaseModel

router = APIRouter(prefix="/strategy-monitor", tags=["策略监控"])


# Schemas
class StrategyRunResponse(BaseModel):
    id: int
    strategy_id: int
    status: str
    started_at: datetime
    ended_at: Optional[datetime]
    last_executed_at: Optional[datetime]
    execution_count: int
    orders_count: int
    error_message: Optional[str]

    class Config:
        from_attributes = True


class StrategyStatsResponse(BaseModel):
    strategy_id: int
    strategy_name: str
    is_running: bool
    total_runs: int
    active_run: Optional[dict]
    total_orders: int
    total_pnl: float
    positions: List[dict]
    recent_trades: List[dict]

    class Config:
        from_attributes = True


class DashboardResponse(BaseModel):
    total_strategies: int
    running_strategies: int
    total_positions: int
    total_pnl: float
    today_pnl: float
    active_strategies: List[dict]

    class Config:
        from_attributes = True


@router.get("/runs/{strategy_id}", response_model=List[StrategyRunResponse])
async def get_strategy_runs(
    strategy_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取策略运行历史"""
    result = await db.execute(
        select(StrategyRun)
        .where(StrategyRun.strategy_id == strategy_id)
        .order_by(StrategyRun.started_at.desc())
        .limit(50)
    )
    runs = result.scalars().all()
    return runs


@router.get("/runs/{strategy_id}/latest")
async def get_latest_run(
    strategy_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取策略最新运行状态"""
    result = await db.execute(
        select(StrategyRun)
        .where(StrategyRun.strategy_id == strategy_id)
        .order_by(StrategyRun.started_at.desc())
        .limit(1)
    )
    run = result.scalar_one_or_none()
    
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="暂无运行记录"
        )
    
    return {
        "id": run.id,
        "status": run.status,
        "started_at": run.started_at.isoformat() if run.started_at else None,
        "last_executed_at": run.last_executed_at.isoformat() if run.last_executed_at else None,
        "execution_count": run.execution_count,
        "orders_count": run.orders_count,
        "error_message": run.error_message
    }


@router.get("/stats/{strategy_id}", response_model=StrategyStatsResponse)
async def get_strategy_stats(
    strategy_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取策略详细统计"""
    # 获取策略
    strategy_result = await db.execute(
        select(Strategy).where(
            Strategy.id == strategy_id,
            Strategy.user_id == current_user.id
        )
    )
    strategy = strategy_result.scalar_one_or_none()
    
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="策略不存在"
        )
    
    # 获取运行记录
    runs_result = await db.execute(
        select(StrategyRun).where(StrategyRun.strategy_id == strategy_id)
    )
    runs = runs_result.scalars().all()
    
    # 获取活跃运行
    active_run = None
    for run in runs:
        if run.status == "running":
            active_run = {
                "id": run.id,
                "started_at": run.started_at.isoformat(),
                "execution_count": run.execution_count,
                "orders_count": run.orders_count
            }
            break
    
    # 获取持仓
    positions_result = await db.execute(
        select(Position).where(
            Position.user_id == current_user.id,
            Position.status == "open"
        )
    )
    positions = positions_result.scalars().all()
    
    positions_data = []
    total_pnl = 0.0
    for pos in positions:
        pnl = pos.unrealized_pnl or 0
        total_pnl += pnl
        positions_data.append({
            "id": pos.id,
            "symbol": pos.symbol,
            "side": pos.side,
            "quantity": pos.quantity,
            "entry_price": pos.entry_price,
            "current_price": pos.current_price,
            "unrealized_pnl": pnl
        })
    
    # 获取最近交易
    trades_result = await db.execute(
        select(Order).where(
            Order.user_id == current_user.id
        )
        .order_by(Order.created_at.desc())
        .limit(10)
    )
    trades = trades_result.scalars().all()
    
    recent_trades = []
    for trade in trades:
        recent_trades.append({
            "id": trade.id,
            "symbol": trade.symbol,
            "side": trade.side,
            "quantity": trade.quantity,
            "price": trade.filled_price or trade.price,
            "status": trade.status,
            "created_at": trade.created_at.isoformat()
        })
    
    return {
        "strategy_id": strategy.id,
        "strategy_name": strategy.name,
        "is_running": strategy.is_active,
        "total_runs": len(runs),
        "active_run": active_run,
        "total_orders": sum(r.orders_count for r in runs),
        "total_pnl": strategy.total_pnl,
        "positions": positions_data,
        "recent_trades": recent_trades
    }


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取监控仪表盘"""
    # 统计策略
    strategies_result = await db.execute(
        select(func.count(Strategy.id)).where(Strategy.user_id == current_user.id)
    )
    total_strategies = strategies_result.scalar() or 0
    
    running_result = await db.execute(
        select(func.count(Strategy.id)).where(
            Strategy.user_id == current_user.id,
            Strategy.is_active == True
        )
    )
    running_strategies = running_result.scalar() or 0
    
    # 统计持仓
    positions_result = await db.execute(
        select(func.count(Position.id)).where(
            Position.user_id == current_user.id,
            Position.status == "open"
        )
    )
    total_positions = positions_result.scalar() or 0
    
    # 计算总盈亏
    pnl_result = await db.execute(
        select(func.sum(Position.unrealized_pnl)).where(
            Position.user_id == current_user.id,
            Position.status == "open"
        )
    )
    total_pnl = pnl_result.scalar() or 0.0
    
    # 今日盈亏（简化：取最近24小时）
    yesterday = datetime.utcnow() - timedelta(days=1)
    today_orders_result = await db.execute(
        select(Order).where(
            Order.user_id == current_user.id,
            Order.created_at >= yesterday,
            Order.status == "filled"
        )
    )
    today_orders = today_orders_result.scalars().all()
    
    today_pnl = 0.0
    for order in today_orders:
        # 简化计算：假设每笔交易盈亏为0
        pass
    
    # 获取运行中的策略详情
    active_strategies_result = await db.execute(
        select(Strategy).where(
            Strategy.user_id == current_user.id,
            Strategy.is_active == True
        )
    )
    active_strategies = active_strategies_result.scalars().all()
    
    active_list = []
    for s in active_strategies:
        active_list.append({
            "id": s.id,
            "name": s.name,
            "type": s.strategy_type,
            "total_pnl": s.total_pnl
        })
    
    return {
        "total_strategies": total_strategies,
        "running_strategies": running_strategies,
        "total_positions": total_positions,
        "total_pnl": total_pnl,
        "today_pnl": today_pnl,
        "active_strategies": active_list
    }


@router.get("/positions")
async def get_all_positions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取所有持仓"""
    result = await db.execute(
        select(Position).where(
            Position.user_id == current_user.id,
            Position.status == "open"
        )
    )
    positions = result.scalars().all()
    
    total_pnl = 0.0
    positions_data = []
    
    for pos in positions:
        pnl = pos.unrealized_pnl or 0
        total_pnl += pnl
        positions_data.append({
            "id": pos.id,
            "symbol": pos.symbol,
            "side": pos.side,
            "quantity": pos.quantity,
            "entry_price": pos.entry_price,
            "current_price": pos.current_price,
            "leverage": pos.leverage,
            "unrealized_pnl": pnl,
            "pnl_percent": (pnl / (pos.entry_price * pos.quantity) * 100) if pos.entry_price and pos.quantity else 0
        })
    
    return {
        "positions": positions_data,
        "total_pnl": total_pnl,
        "count": len(positions_data)
    }


@router.get("/orders/recent")
async def get_recent_orders(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取最近订单"""
    result = await db.execute(
        select(Order).where(Order.user_id == current_user.id)
        .order_by(Order.created_at.desc())
        .limit(limit)
    )
    orders = result.scalars().all()
    
    orders_data = []
    for order in orders:
        orders_data.append({
            "id": order.id,
            "symbol": order.symbol,
            "side": order.side,
            "type": order.order_type,
            "quantity": order.quantity,
            "price": order.filled_price or order.price,
            "status": order.status,
            "created_at": order.created_at.isoformat()
        })
    
    return {
        "orders": orders_data,
        "count": len(orders_data)
    }
