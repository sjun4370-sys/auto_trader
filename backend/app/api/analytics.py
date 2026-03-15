"""交易数据分析API"""
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.database import get_db
from app.models import User, Order, Position, TradeLog
from app.schemas import (
    AnalyticsResponse,
    TrendData,
    SymbolData,
    SideData,
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/analytics", tags=["数据分析"])


def calculate_pnl_from_orders(orders: list) -> float:
    """从订单列表计算盈亏"""
    # 按交易对分组计算
    symbol_trades = defaultdict(lambda: {"buy": [], "sell": []})

    for order in orders:
        if order.status != "filled" or not order.filled_price:
            continue
        symbol_trades[order.symbol][order.side].append({
            "quantity": order.quantity,
            "price": order.filled_price,
        })

    total_pnl = 0.0
    for symbol, trades in symbol_trades.items():
        buy_volume = sum(t["quantity"] * t["price"] for t in trades["buy"])
        sell_volume = sum(t["quantity"] * t["price"] for t in trades["sell"])
        # 简化计算：卖 - 买
        total_pnl += sell_volume - buy_volume

    return total_pnl


@router.get("", response_model=AnalyticsResponse)
async def get_analytics(
    days: int = Query(30, ge=1, le=365, description="分析天数"),
    symbol: Optional[str] = Query(None, description="交易对筛选"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取交易数据分析"""

    # 时间范围
    start_date = datetime.utcnow() - timedelta(days=days)

    # 基础筛选条件
    order_filters = [
        Order.user_id == current_user.id,
        Order.status == "filled",
        Order.filled_at >= start_date,
    ]
    if symbol:
        order_filters.append(Order.symbol == symbol)

    # 获取订单列表
    result = await db.execute(
        select(Order).where(and_(*order_filters))
    )
    orders = result.scalars().all()

    # 获取平仓仓位
    position_filters = [
        Position.user_id == current_user.id,
        Position.status == "closed",
        Position.closed_at >= start_date,
    ]
    if symbol:
        position_filters.append(Position.symbol == symbol)

    result = await db.execute(
        select(Position).where(and_(*position_filters))
    )
    closed_positions = result.scalars().all()

    # 获取所有仓位（用于统计）
    all_positions_result = await db.execute(
        select(Position).where(Position.user_id == current_user.id)
    )
    all_positions = all_positions_result.scalars().all()
    open_positions = sum(1 for p in all_positions if p.status == "open")
    closed_count = sum(1 for p in all_positions if p.status == "closed")

    # 计算总体统计
    total_trades = len(orders)
    winning_trades = 0
    losing_trades = 0
    total_pnl = 0.0

    # 按交易对和日期分组
    symbol_stats = defaultdict(lambda: {
        "trades": 0,
        "pnl": 0.0,
        "wins": 0,
    })

    daily_stats = defaultdict(lambda: {
        "trades": 0,
        "pnl": 0.0,
    })

    side_stats = defaultdict(lambda: {
        "trades": 0,
        "pnl": 0.0,
        "wins": 0,
    })

    # 计算每个订单的盈亏（简化计算：假设每个卖出订单都有对应的买入）
    # 实际应用中需要更复杂的配对逻辑
    order_by_symbol = defaultdict(list)
    for order in orders:
        if order.filled_at:
            date_key = order.filled_at.strftime("%Y-%m-%d")
            order_by_symbol[order.symbol].append(order)

    # 计算每个交易对的盈亏
    for sym, sym_orders in order_by_symbol.items():
        buy_total = 0.0
        sell_total = 0.0
        buy_count = 0
        sell_count = 0

        for order in sym_orders:
            if order.side == "buy":
                buy_total += order.quantity * (order.filled_price or 0)
                buy_count += 1
            else:
                sell_total += order.quantity * (order.filled_price or 0)
                sell_count += 1

        # 计算该交易对的盈亏
        pnl = sell_total - buy_total

        if pnl > 0:
            winning_trades += 1
            symbol_stats[sym]["wins"] += 1
        elif pnl < 0:
            losing_trades += 1

        symbol_stats[sym]["trades"] = len(sym_orders)
        symbol_stats[sym]["pnl"] += pnl
        total_pnl += pnl

        # 统计买卖方向
        for order in sym_orders:
            date_key = order.filled_at.strftime("%Y-%m-%d") if order.filled_at else ""
            side = order.side

            side_stats[side]["trades"] += 1
            if order.side == "sell":
                # 简化：卖单盈利 = 卖出 - 对应买入
                side_stats[side]["pnl"] += order.quantity * (order.filled_price or 0)

    # 使用仓位已实现盈亏
    realized_pnl = sum(p.realized_pnl for p in closed_positions)
    if realized_pnl != 0:
        total_pnl = realized_pnl

    # 计算胜率
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

    # 计算平均盈利/亏损
    avg_profit = total_pnl / winning_trades if winning_trades > 0 else 0
    avg_loss = total_pnl / losing_trades if losing_trades != 0 else 0

    # 计算盈亏比
    profit_loss_ratio = abs(avg_profit / avg_loss) if avg_loss != 0 else 0

    # 构建交易对分析数据
    symbols_data = []
    for sym, stats in symbol_stats.items():
        sym_trades = stats["trades"]
        sym_wins = stats["wins"]
        sym_pnl = stats["pnl"]

        symbols_data.append(SymbolData(
            symbol=sym,
            total_pnl=round(sym_pnl, 2),
            trades=sym_trades,
            win_rate=round(sym_wins / sym_trades * 100, 2) if sym_trades > 0 else 0,
            avg_profit=round(sym_pnl / sym_wins, 2) if sym_wins > 0 else 0,
            avg_loss=round(sym_pnl / (sym_trades - sym_wins), 2) if sym_trades > sym_wins else 0,
        ))

    # 按盈亏排序
    symbols_data.sort(key=lambda x: x.total_pnl, reverse=True)

    # 构建多空分析数据
    sides_data = []
    for side, stats in side_stats.items():
        sides_data.append(SideData(
            side=side,
            total_pnl=round(stats["pnl"], 2),
            trades=stats["trades"],
            win_rate=round(stats["wins"] / stats["trades"] * 100, 2) if stats["trades"] > 0 else 0,
        ))

    # 构建趋势数据（按日期）
    trends_data = []
    # 获取最近N天的数据
    for i in range(days):
        date = (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")

        # 获取该日期的订单
        day_start = datetime.strptime(date, "%Y-%m-%d")
        day_end = day_start + timedelta(days=1)

        day_orders_result = await db.execute(
            select(Order).where(
                and_(
                    Order.user_id == current_user.id,
                    Order.status == "filled",
                    Order.filled_at >= day_start,
                    Order.filled_at < day_end,
                )
            )
        )
        day_orders = day_orders_result.scalars().all()

        day_pnl = 0.0
        for order in day_orders:
            if order.side == "sell" and order.filled_price:
                day_pnl += order.quantity * order.filled_price

        # 减去买入成本
        for order in day_orders:
            if order.side == "buy" and order.filled_price:
                day_pnl -= order.quantity * order.filled_price

        trends_data.append(TrendData(
            date=date,
            pnl=round(day_pnl, 2),
            trades=len(day_orders),
        ))

    # 按日期排序
    trends_data.sort(key=lambda x: x.date)

    # 计算最大回撤
    max_drawdown = 0.0
    cumulative_pnl = 0.0
    peak_pnl = 0.0

    for trend in trends_data:
        cumulative_pnl += trend.pnl
        if cumulative_pnl > peak_pnl:
            peak_pnl = cumulative_pnl
        drawdown = peak_pnl - cumulative_pnl
        if drawdown > max_drawdown:
            max_drawdown = drawdown

    return AnalyticsResponse(
        total_pnl=round(total_pnl, 2),
        total_trades=total_trades,
        winning_trades=winning_trades,
        losing_trades=losing_trades,
        win_rate=round(win_rate, 2),
        avg_profit=round(avg_profit, 2),
        avg_loss=round(avg_loss, 2),
        profit_loss_ratio=round(profit_loss_ratio, 2),
        trends=trends_data,
        symbols=symbols_data[:10],  # 最多返回前10个交易对
        sides=sides_data,
        max_drawdown=round(max_drawdown, 2),
        open_positions=open_positions,
        closed_positions=closed_count,
    )


@router.get("/summary")
async def get_analytics_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取分析摘要（快速接口）"""

    # 总订单数
    total_orders_result = await db.execute(
        select(func.count(Order.id)).where(Order.user_id == current_user.id)
    )
    total_orders = total_orders_result.scalar() or 0

    # 已完成订单
    filled_orders_result = await db.execute(
        select(func.count(Order.id)).where(
            and_(
                Order.user_id == current_user.id,
                Order.status == "filled"
            )
        )
    )
    filled_orders = filled_orders_result.scalar() or 0

    # 持仓数
    open_positions_result = await db.execute(
        select(func.count(Position.id)).where(
            and_(
                Position.user_id == current_user.id,
                Position.status == "open"
            )
        )
    )
    open_positions = open_positions_result.scalar() or 0

    # 总盈亏
    positions_result = await db.execute(
        select(Position).where(Position.user_id == current_user.id)
    )
    positions = positions_result.scalars().all()
    total_realized_pnl = sum(p.realized_pnl for p in positions)
    total_unrealized_pnl = sum(p.unrealized_pnl for p in positions)

    return {
        "total_orders": total_orders,
        "filled_orders": filled_orders,
        "open_positions": open_positions,
        "total_realized_pnl": round(total_realized_pnl, 2),
        "total_unrealized_pnl": round(total_unrealized_pnl, 2),
        "total_pnl": round(total_realized_pnl + total_unrealized_pnl, 2),
    }
