"""策略推荐API"""
import math
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
import ccxt

from app.database import get_db
from app.models import User, StrategyRecommendation
from app.schemas import (
    StrategyRecommendationResponse,
    StrategyRecommendationRequest,
    MarketAnalysis,
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/strategy-recommendation", tags=["策略推荐"])


def create_okx_exchange() -> ccxt.okx:
    """创建配置好的OKX交易所实例"""
    exchange = ccxt.okx({
        'enableRateLimit': True,
        'options': {'defaultType': 'swap'}
    })
    exchange.timeout = 10000
    return exchange


def calculate_volatility(closes: List[float]) -> float:
    """计算波动率（标准差百分比）"""
    if len(closes) < 2:
        return 0.0

    mean = sum(closes) / len(closes)
    variance = sum((x - mean) ** 2 for x in closes) / len(closes)
    std_dev = math.sqrt(variance)

    if mean == 0:
        return 0.0
    return (std_dev / mean) * 100


def calculate_rsi(closes: List[float], period: int = 14) -> float:
    """计算RSI指标"""
    if len(closes) < period + 1:
        return 50.0

    gains = []
    losses = []
    for i in range(1, len(closes)):
        change = closes[i] - closes[i - 1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))

    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period

    if avg_loss == 0:
        return 100.0

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_ma(closes: List[float], period: int) -> float:
    """计算移动平均线"""
    if len(closes) < period:
        return closes[-1] if closes else 0.0
    return sum(closes[-period:]) / period


def calculate_volume_change(volumes: List[float]) -> float:
    """计算成交量变化率"""
    if len(volumes) < 2:
        return 0.0

    avg_volume = sum(volumes[:-1]) / (len(volumes) - 1)
    if avg_volume == 0:
        return 0.0

    return ((volumes[-1] - avg_volume) / avg_volume) * 100


def calculate_trend_strength(closes: List[float], ma20: float, ma50: float) -> float:
    """计算趋势强度"""
    if not closes or ma20 == 0:
        return 0.0

    # 基于价格与均线的偏离度计算趋势强度
    current_price = closes[-1]
    price_deviation = abs(current_price - ma20) / ma20 * 100

    # 考虑短期和长期均线的相对位置
    if ma50 > 0:
        ma_cross = (ma20 - ma50) / ma50 * 100
    else:
        ma_cross = 0.0

    # 综合计算趋势强度 (-100 到 100)
    trend_strength = (price_deviation * 0.6 + ma_cross * 0.4)
    return max(-100, min(100, trend_strength))


def determine_market_condition(
    volatility: float,
    trend_strength: float,
    rsi: float,
    volume_change: float,
) -> tuple[str, str]:
    """判断市场条件

    Returns:
        (market_condition, description)
    """
    # 高波动市场
    if volatility > 5:
        if volume_change > 30:
            return "volatile", "高波动市场"
        return "volatile", "波动性较高"

    # 强势上涨
    if trend_strength > 15 and rsi < 70:
        return "trending_up", "上涨趋势"

    # 强势下跌
    if trend_strength < -15 and rsi > 30:
        return "trending_down", "下跌趋势"

    # RSI超买超卖判断
    if rsi > 70:
        return "trending_down", "超买区域"
    if rsi < 30:
        return "trending_up", "超卖区域"

    # 横盘整理
    if abs(trend_strength) < 10 and volatility < 3:
        return "sideways", "横盘整理"

    # 稳定市场
    if volatility < 2:
        return "stable", "稳定市场"

    return "sideways", "中性市场"


def recommend_strategy(
    market_condition: str,
    volatility: float,
    trend_strength: float,
    rsi: float,
) -> tuple[str, float, str]:
    """根据市场条件推荐策略

    Returns:
        (strategy_type, confidence, reason)
    """
    strategies = {
        "trending_up": {
            "strategy": "trend_following",
            "confidence": 0.85,
            "reason": "市场处于上涨趋势，适合趋势跟踪策略",
        },
        "trending_down": {
            "strategy": "trend_following",
            "confidence": 0.80,
            "reason": "市场处于下跌趋势，适合做空趋势策略",
        },
        "volatile": {
            "strategy": "grid",
            "confidence": 0.75,
            "reason": "市场波动较大，适合网格交易策略",
        },
        "sideways": {
            "strategy": "grid",
            "confidence": 0.70,
            "reason": "市场横盘整理，适合网格交易策略",
        },
        "stable": {
            "strategy": "dca",
            "confidence": 0.65,
            "reason": "市场稳定，适合定投策略",
        },
    }

    # 特殊处理超买超卖情况
    if rsi > 75:
        return "mean_reversion", 0.75, "RSI超买，可能回调，适合均值回归策略"
    if rsi < 25:
        return "mean_reversion", 0.75, "RSI超卖，可能反弹，适合均值回归策略"

    result = strategies.get(market_condition, strategies["stable"])
    return result["strategy"], result["confidence"], result["reason"]


@router.get("/analyze", response_model=MarketAnalysis)
async def analyze_market(
    symbol: str = Query("BTC/USDT", description="交易对"),
    timeframe: str = Query("1h", description="时间框架"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """分析市场并推荐策略"""
    exchange = create_okx_exchange()

    # 获取K线数据
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=50)

    if not ohlcv:
        return {"error": "无法获取K线数据"}

    # 提取数据
    closes = [k[4] for k in ohlcv]
    volumes = [k[5] for k in ohlcv]
    current_price = closes[-1]
    open_price = ohlcv[0][1]

    # 计算各项指标
    volatility = calculate_volatility(closes[-20:])
    rsi = calculate_rsi(closes)
    ma20 = calculate_ma(closes, 20)
    ma50 = calculate_ma(closes, 50) if len(closes) >= 50 else ma20
    volume_change = calculate_volume_change(volumes)
    trend_strength = calculate_trend_strength(closes, ma20, ma50)

    # 计算涨跌幅
    change_percent = ((current_price - open_price) / open_price) * 100

    # 判断市场条件
    market_condition, condition_desc = determine_market_condition(
        volatility, trend_strength, rsi, volume_change
    )

    return {
        "symbol": symbol,
        "price": current_price,
        "change_percent": change_percent,
        "volatility": volatility,
        "volume": volumes[-1],
        "volume_change": volume_change,
        "trend_strength": trend_strength,
        "market_condition": market_condition,
        "rsi": rsi,
        "ma20": ma20,
        "ma50": ma50,
    }


@router.get("/analyze-and-recommend")
async def analyze_and_recommend(
    symbol: str = Query("BTC/USDT", description="交易对"),
    timeframe: str = Query("1h", description="时间框架"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """分析市场并返回策略推荐（同时保存推荐记录）"""
    exchange = create_okx_exchange()

    # 获取K线数据
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=100)
    except Exception as e:
        return {"error": f"获取行情数据失败: {str(e)}"}

    if not ohlcv:
        return {"error": "无法获取K线数据"}

    # 提取数据
    closes = [k[4] for k in ohlcv]
    volumes = [k[5] for k in ohlcv]
    current_price = closes[-1]
    open_price = ohlcv[0][1]

    # 计算各项指标
    volatility = calculate_volatility(closes[-20:])
    rsi = calculate_rsi(closes)
    ma20 = calculate_ma(closes, 20)
    ma50 = calculate_ma(closes, 50) if len(closes) >= 50 else ma20
    volume_change = calculate_volume_change(volumes)
    trend_strength = calculate_trend_strength(closes, ma20, ma50)

    # 计算涨跌幅
    change_percent = ((current_price - open_price) / open_price) * 100

    # 判断市场条件
    market_condition, condition_desc = determine_market_condition(
        volatility, trend_strength, rsi, volume_change
    )

    # 获取推荐策略
    strategy_type, confidence, reason = recommend_strategy(
        market_condition, volatility, trend_strength, rsi
    )

    # 保存推荐记录
    recommendation = StrategyRecommendation(
        user_id=current_user.id,
        symbol=symbol,
        recommended_strategy=strategy_type,
        market_condition=market_condition,
        confidence=confidence,
        price=current_price,
        volatility=volatility,
        volume=volumes[-1],
        volume_change=volume_change,
        trend_strength=trend_strength,
        reason=f"{condition_desc} - {reason}",
    )
    db.add(recommendation)
    await db.commit()
    await db.refresh(recommendation)

    return {
        "recommendation_id": recommendation.id,
        "symbol": symbol,
        "price": current_price,
        "change_percent": change_percent,
        "market_condition": market_condition,
        "condition_description": condition_desc,
        "volatility": volatility,
        "rsi": round(rsi, 2),
        "ma20": round(ma20, 2),
        "ma50": round(ma50, 2),
        "volume_change": round(volume_change, 2),
        "trend_strength": round(trend_strength, 2),
        "recommended_strategy": strategy_type,
        "confidence": confidence,
        "reason": f"{condition_desc} - {reason}",
        "suggested_config": _get_strategy_config(strategy_type, symbol, current_price),
    }


def _get_strategy_config(strategy_type: str, symbol: str, price: float) -> dict:
    """获取策略建议配置"""
    configs = {
        "grid": {
            "strategy_type": "grid",
            "symbol": symbol,
            "grid_levels": 10,
            "price_range_percent": 5,
            "order_amount": 100,
            "price_precision": 2,
            "quantity_precision": 4,
        },
        "trend_following": {
            "strategy_type": "trend",
            "symbol": symbol,
            "timeframe": "1h",
            "entry_threshold": 0.5,
            "exit_threshold": -0.3,
            "stop_loss_percent": 2,
            "position_size_percent": 10,
        },
        "dca": {
            "strategy_type": "dca",
            "symbol": symbol,
            "investment_amount": 100,
            "purchase_interval_hours": 24,
            "target_positions": 10,
            "stop_loss_percent": 15,
        },
        "mean_reversion": {
            "strategy_type": "mean_reversion",
            "symbol": symbol,
            "timeframe": "1h",
            "rsi_oversold": 30,
            "rsi_overbought": 70,
            "position_size_percent": 20,
            "stop_loss_percent": 3,
            "take_profit_percent": 5,
        },
    }
    return configs.get(strategy_type, {})


@router.get("/history", response_model=List[StrategyRecommendationResponse])
async def get_recommendation_history(
    symbol: Optional[str] = Query(None, description="交易对筛选"),
    limit: int = Query(20, le=100, description="返回数量"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取推荐历史记录"""
    query = select(StrategyRecommendation).where(
        StrategyRecommendation.user_id == current_user.id
    )

    if symbol:
        query = query.where(StrategyRecommendation.symbol == symbol)

    query = query.order_by(desc(StrategyRecommendation.created_at)).limit(limit)

    result = await db.execute(query)
    recommendations = result.scalars().all()

    return recommendations


@router.get("/{recommendation_id}", response_model=StrategyRecommendationResponse)
async def get_recommendation(
    recommendation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取单条推荐详情"""
    result = await db.execute(
        select(StrategyRecommendation).where(
            StrategyRecommendation.id == recommendation_id,
            StrategyRecommendation.user_id == current_user.id,
        )
    )
    recommendation = result.scalar_one_or_none()

    if not recommendation:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="推荐记录不存在",
        )

    return recommendation
