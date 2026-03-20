"""统计API"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta

from app.database import get_db
from app.models import User, Order, Position
from app.schemas import StatisticsResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/statistics", tags=["统计"])


@router.get("", response_model=StatisticsResponse)
async def get_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取统计数据"""
    # 总交易次数
    total_trades_result = await db.execute(
        select(func.count(Order.id)).where(Order.user_id == current_user.id)
    )
    total_trades = total_trades_result.scalar() or 0

    # 盈利交易次数
    winning_trades_result = await db.execute(
        select(func.count(Order.id)).where(
            Order.user_id == current_user.id,
            Order.status == 'filled'
        )
    )
    winning_trades = winning_trades_result.scalar() or 0

    # 亏损交易次数
    losing_trades = total_trades - winning_trades

    # 胜率
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

    # TODO: 计算实际盈亏数据（当前返回0占位）
    total_pnl = 0.0
    today_pnl = 0.0
    avg_profit = 0.0
    avg_loss = 0.0

    return StatisticsResponse(
        total_pnl=total_pnl,
        today_pnl=today_pnl,
        win_rate=win_rate,
        total_trades=total_trades,
        winning_trades=winning_trades,
        losing_trades=losing_trades,
        avg_profit=avg_profit,
        avg_loss=avg_loss,
    )
