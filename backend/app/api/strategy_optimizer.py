"""策略优化器 API"""
import statistics
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from datetime import datetime, timedelta

from app.database import get_db
from app.models import User, Strategy, StrategyRun, Position, Order, TradeLog, OptimizationHistory
from app.api.deps import get_current_user
from app.schemas import BaseModel

router = APIRouter(prefix="/strategy-optimizer", tags=["策略优化器"])


# ==================== Schemas ====================
class OptimizationSuggestion(BaseModel):
    """优化建议"""
    type: str  # 参数调整建议类型
    field: str  # 调整的参数名称
    current_value: Any  # 当前值
    suggested_value: Any  # 建议值
    reason: str  # 建议原因
    priority: str  # 优先级: high, medium, low


class PerformanceMetrics(BaseModel):
    """性能指标"""
    total_pnl: float
    win_rate: float
    total_trades: int
    avg_trade_pnl: float
    max_drawdown: float
    sharpe_ratio: float
    profit_factor: float
    avg_holding_time: float
    total_volume: float


class StrategyAnalysisResponse(BaseModel):
    """策略分析响应"""
    strategy_id: int
    strategy_name: str
    strategy_type: str
    analysis_period: Dict[str, str]  # 分析时间段
    performance: PerformanceMetrics
    suggestions: List[OptimizationSuggestion]
    analyzed_at: str


class OptimizationHistoryResponse(BaseModel):
    """优化历史记录"""
    id: int
    strategy_id: int
    analysis_period_start: str
    analysis_period_end: str
    performance_snapshot: Dict[str, Any]
    suggestions_count: int
    created_at: str

    class Config:
        from_attributes = True


# ==================== 分析逻辑 ====================
async def analyze_strategy_performance(
    db: AsyncSession,
    strategy_id: int,
    user_id: int,
    days: int = 30
) -> Dict[str, Any]:
    """
    分析策略表现

    Args:
        db: 数据库会话
        strategy_id: 策略ID
        user_id: 用户ID
        days: 分析天数

    Returns:
        分析结果字典
    """
    # 获取策略
    strategy_result = await db.execute(
        select(Strategy).where(
            Strategy.id == strategy_id,
            Strategy.user_id == user_id
        )
    )
    strategy = strategy_result.scalar_one_or_none()

    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="策略不存在"
        )

    # 计算时间范围
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days)

    # 获取相关订单
    orders_result = await db.execute(
        select(Order).where(
            Order.user_id == user_id,
            Order.strategy_id == strategy_id,
            Order.created_at >= start_time,
            Order.status == "filled"
        )
    )
    orders = orders_result.scalars().all()

    # 获取交易日志
    trade_logs_result = await db.execute(
        select(TradeLog).where(
            TradeLog.user_id == user_id,
            TradeLog.created_at >= start_time
        )
    )
    trade_logs = trade_logs_result.scalars().all()

    # 计算性能指标
    total_trades = len(orders)
    winning_trades = 0
    losing_trades = 0
    total_pnl = 0.0
    total_profit = 0.0
    total_loss = 0.0
    trade_pnls = []
    volumes = []

    for order in orders:
        # 简化计算：从订单中获取交易量
        volume = (order.filled_price or order.price or 0) * order.quantity
        volumes.append(volume)

    for log in trade_logs:
        if log.pnl is not None:
            total_pnl += log.pnl
            trade_pnls.append(log.pnl)
            if log.pnl > 0:
                winning_trades += 1
                total_profit += log.pnl
            elif log.pnl < 0:
                losing_trades += 1
                total_loss += abs(log.pnl)

    # 计算胜率
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0.0

    # 计算平均盈亏
    avg_trade_pnl = total_pnl / total_trades if total_trades > 0 else 0.0
    avg_profit = total_profit / winning_trades if winning_trades > 0 else 0.0
    avg_loss = total_loss / losing_trades if losing_trades > 0 else 0.0

    # 计算盈亏比
    profit_factor = total_profit / total_loss if total_loss > 0 else 0.0

    # 计算最大回撤（简化版）
    max_drawdown = 0.0
    cumulative = 0.0
    peak = 0.0
    for pnl in trade_pnls:
        cumulative += pnl
        if cumulative > peak:
            peak = cumulative
        drawdown = peak - cumulative
        if drawdown > max_drawdown:
            max_drawdown = drawdown

    # 计算夏普比率（简化版）
    if len(trade_pnls) > 1:
        returns = trade_pnls
        avg_return = statistics.mean(returns)
        std_return = statistics.stdev(returns) if len(returns) > 1 else 1.0
        sharpe_ratio = (avg_return / std_return * (252 ** 0.5)) if std_return > 0 else 0.0
    else:
        sharpe_ratio = 0.0

    # 计算平均持仓时间（简化）
    avg_holding_time = 0.0

    # 总交易量
    total_volume = sum(volumes)

    return {
        "strategy": strategy,
        "start_time": start_time,
        "end_time": end_time,
        "total_trades": total_trades,
        "winning_trades": winning_trades,
        "losing_trades": losing_trades,
        "total_pnl": total_pnl,
        "win_rate": win_rate,
        "avg_trade_pnl": avg_trade_pnl,
        "avg_profit": avg_profit,
        "avg_loss": avg_loss,
        "profit_factor": profit_factor,
        "max_drawdown": max_drawdown,
        "sharpe_ratio": sharpe_ratio,
        "avg_holding_time": avg_holding_time,
        "total_volume": total_volume
    }


def generate_optimization_suggestions(
    analysis: Dict[str, Any],
    strategy: Strategy
) -> List[OptimizationSuggestion]:
    """
    根据分析结果生成优化建议

    Args:
        analysis: 分析结果
        strategy: 策略对象

    Returns:
        优化建议列表
    """
    suggestions = []
    config = strategy.config or {}

    # 1. 胜率分析
    win_rate = analysis.get("win_rate", 0)
    if win_rate < 40:
        suggestions.append(OptimizationSuggestion(
            type="win_rate",
            field="win_rate",
            current_value=f"{win_rate:.1f}%",
            suggested_value="40-50%",
            reason="胜率过低，建议优化入场条件或增加过滤条件",
            priority="high"
        ))
    elif win_rate > 70:
        suggestions.append(OptimizationSuggestion(
            type="win_rate",
            field="risk_reward",
            current_value="high_win_rate",
            suggested_value="保持并适当扩大仓位",
            reason="胜率很高，可以考虑适当增加仓位比例",
            priority="medium"
        ))

    # 2. 盈亏比分析
    profit_factor = analysis.get("profit_factor", 0)
    if profit_factor < 1.0:
        suggestions.append(OptimizationSuggestion(
            type="profit_factor",
            field="take_profit",
            current_value=f"{profit_factor:.2f}",
            suggested_value="1.5+",
            reason="盈亏比小于1，建议调整止盈止损比例",
            priority="high"
        ))
    elif profit_factor > 2.0 and win_rate < 30:
        suggestions.append(OptimizationSuggestion(
            type="profit_factor",
            field="stop_loss",
            current_value=f"{profit_factor:.2f}",
            suggested_value="保持现有设置",
            reason="盈亏比优秀但胜率较低，保持当前策略",
            priority="low"
        ))

    # 3. 最大回撤分析
    max_drawdown = analysis.get("max_drawdown", 0)
    total_pnl = analysis.get("total_pnl", 0)
    if total_pnl > 0 and max_drawdown > abs(total_pnl) * 0.5:
        suggestions.append(OptimizationSuggestion(
            type="drawdown",
            field="max_position_size",
            current_value=f"{max_drawdown:.2f}",
            suggested_value=f"{abs(total_pnl) * 0.3:.2f}",
            reason="最大回撤过高，建议减少单笔仓位比例",
            priority="high"
        ))

    # 4. 交易频率分析
    total_trades = analysis.get("total_trades", 0)
    days = (analysis["end_time"] - analysis["start_time"]).days or 1
    trades_per_day = total_trades / days
    if trades_per_day > 10:
        suggestions.append(OptimizationSuggestion(
            type="trade_frequency",
            field="min_interval",
            current_value=f"{trades_per_day:.1f}次/天",
            suggested_value="5次/天",
            reason="交易频率过高，可能增加手续费和滑点成本",
            priority="medium"
        ))
    elif trades_per_day < 0.1 and total_trades < 3:
        suggestions.append(OptimizationSuggestion(
            type="trade_frequency",
            field="entry_conditions",
            current_value=f"{trades_per_day:.1f}次/天",
            suggested_value="适当放宽条件",
            reason="交易频率过低，可能错过交易机会",
            priority="medium"
        ))

    # 5. 策略类型特定建议
    strategy_type = strategy.strategy_type
    if strategy_type == "grid":
        # 网格策略建议
        grid_spacing = config.get("grid_spacing", 0.02)
        if grid_spacing < 0.01:
            suggestions.append(OptimizationSuggestion(
                type="grid_spacing",
                field="grid_spacing",
                current_value=f"{grid_spacing*100:.1f}%",
                suggested_value="1-2%",
                reason="网格间距过小，可能导致频繁开单",
                priority="high"
            ))
        elif grid_spacing > 0.05:
            suggestions.append(OptimizationSuggestion(
                type="grid_spacing",
                field="grid_spacing",
                current_value=f"{grid_spacing*100:.1f}%",
                suggested_value="2-3%",
                reason="网格间距过大，可能难以成交",
                priority="medium"
            ))

        # 网格数量
        grid_num = config.get("grid_num", 10)
        if grid_num > 20:
            suggestions.append(OptimizationSuggestion(
                type="grid_count",
                field="grid_num",
                current_value=grid_num,
                suggested_value=10,
                reason="网格数量过多，资金利用率低",
                priority="medium"
            ))
        elif grid_num < 5:
            suggestions.append(OptimizationSuggestion(
                type="grid_count",
                field="grid_num",
                current_value=grid_num,
                suggested_value=10,
                reason="网格数量过少，盈利空间有限",
                priority="medium"
            ))

    elif strategy_type == "dca":
        # 策略建议
        dca_levels = config.get("dca_levels", 3)
        if dca_levels < 3:
            suggestions.append(OptimizationSuggestion(
                type="dca_levels",
                field="dca_levels",
                current_value=dca_levels,
                suggested_value=3,
                reason="定投层级过少，建议增加以平滑成本",
                priority="medium"
            ))

        dca_interval = config.get("dca_interval", 24)
        if dca_interval < 6:
            suggestions.append(OptimizationSuggestion(
                type="dca_interval",
                field="dca_interval",
                current_value=f"{dca_interval}小时",
                suggested_value="12-24小时",
                reason="定投间隔过短，建议拉长以降低手续费",
                priority="low"
            ))

    elif strategy_type == "trend":
        # 趋势策略建议
        stop_loss = config.get("stop_loss_percent", 0.02)
        if stop_loss < 0.01:
            suggestions.append(OptimizationSuggestion(
                type="stop_loss",
                field="stop_loss_percent",
                current_value=f"{stop_loss*100:.1f}%",
                suggested_value="2-3%",
                reason="止损设置过小，容易被市场噪音触发",
                priority="high"
            ))
        elif stop_loss > 0.1:
            suggestions.append(OptimizationSuggestion(
                type="stop_loss",
                field="stop_loss_percent",
                current_value=f"{stop_loss*100:.1f}%",
                suggested_value="3-5%",
                reason="止损设置过大，单笔亏损风险过高",
                priority="high"
            ))

    # 6. 如果没有交易记录
    if total_trades == 0:
        suggestions.append(OptimizationSuggestion(
            type="no_trades",
            field="strategy_status",
            current_value="无交易",
            suggested_value="检查策略配置",
            reason="策略没有产生任何交易，可能是配置问题或市场条件不适合",
            priority="high"
        ))

    # 7. 通用建议
    if not suggestions:
        suggestions.append(OptimizationSuggestion(
            type="general",
            field="keep_current",
            current_value="良好",
            suggested_value="保持当前设置",
            reason="策略表现良好，无需调整",
            priority="low"
        ))

    return suggestions


# ==================== API 路由 ====================
@router.get("/analyze/{strategy_id}", response_model=StrategyAnalysisResponse)
async def analyze_strategy(
    strategy_id: int,
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    分析策略表现并给出优化建议

    Args:
        strategy_id: 策略ID
        days: 分析天数（默认30天）
    """
    # 分析策略表现
    analysis = await analyze_strategy_performance(db, strategy_id, current_user.id, days)

    # 生成优化建议
    suggestions = generate_optimization_suggestions(analysis, analysis["strategy"])

    # 保存优化历史
    optimization_record = OptimizationHistory(
        user_id=current_user.id,
        strategy_id=strategy_id,
        analysis_period_start=analysis["start_time"],
        analysis_period_end=analysis["end_time"],
        performance_snapshot={
            "total_pnl": analysis["total_pnl"],
            "win_rate": analysis["win_rate"],
            "total_trades": analysis["total_trades"],
            "profit_factor": analysis["profit_factor"],
            "max_drawdown": analysis["max_drawdown"],
            "sharpe_ratio": analysis["sharpe_ratio"]
        },
        suggestions=[s.model_dump() for s in suggestions],
        suggestions_count=len(suggestions)
    )
    db.add(optimization_record)
    await db.commit()

    return {
        "strategy_id": analysis["strategy"].id,
        "strategy_name": analysis["strategy"].name,
        "strategy_type": analysis["strategy"].strategy_type,
        "analysis_period": {
            "start": analysis["start_time"].isoformat(),
            "end": analysis["end_time"].isoformat()
        },
        "performance": PerformanceMetrics(
            total_pnl=analysis["total_pnl"],
            win_rate=analysis["win_rate"],
            total_trades=analysis["total_trades"],
            avg_trade_pnl=analysis["avg_trade_pnl"],
            max_drawdown=analysis["max_drawdown"],
            sharpe_ratio=analysis["sharpe_ratio"],
            profit_factor=analysis["profit_factor"],
            avg_holding_time=analysis["avg_holding_time"],
            total_volume=analysis["total_volume"]
        ),
        "suggestions": suggestions,
        "analyzed_at": datetime.utcnow().isoformat()
    }


@router.get("/history/{strategy_id}", response_model=List[OptimizationHistoryResponse])
async def get_optimization_history(
    strategy_id: int,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取策略优化历史记录

    Args:
        strategy_id: 策略ID
        limit: 返回记录数量（默认10条）
    """
    # 验证策略存在
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

    # 获取优化历史
    history_result = await db.execute(
        select(OptimizationHistory).where(
            OptimizationHistory.strategy_id == strategy_id,
            OptimizationHistory.user_id == current_user.id
        ).order_by(desc(OptimizationHistory.created_at)).limit(limit)
    )
    history = history_result.scalars().all()

    return [
        OptimizationHistoryResponse(
            id=h.id,
            strategy_id=h.strategy_id,
            analysis_period_start=h.analysis_period_start.isoformat(),
            analysis_period_end=h.analysis_period_end.isoformat(),
            performance_snapshot=h.performance_snapshot,
            suggestions_count=h.suggestions_count,
            created_at=h.created_at.isoformat()
        )
        for h in history
    ]
