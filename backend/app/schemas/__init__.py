"""Pydantic Schemas"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, model_validator


# ==================== Auth ====================
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


# ==================== Account ====================
class AccountCreate(BaseModel):
    exchange: str
    account_name: Optional[str] = None
    api_key: str = Field(..., min_length=1)
    api_secret: str = Field(..., min_length=1)
    passphrase: Optional[str] = None
    is_testnet: bool = True

    @model_validator(mode="after")
    def validate_api_credentials(self):
        if not self.api_key.strip() or not self.api_secret.strip():
            raise ValueError("api_key 和 api_secret 不能为空")
        return self


class AccountUpdate(BaseModel):
    exchange: Optional[str] = None
    account_name: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    passphrase: Optional[str] = None
    is_testnet: Optional[bool] = None
    is_active: Optional[bool] = None

    @model_validator(mode="after")
    def validate_exchange_not_null(self):
        if "exchange" in self.model_fields_set and self.exchange is None:
            raise ValueError("exchange cannot be null")
        return self


class AccountResponse(BaseModel):
    id: int
    exchange: str
    account_name: Optional[str]
    is_testnet: bool
    is_active: bool
    has_api_credentials: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Market ====================
class TickerResponse(BaseModel):
    symbol: str
    last: float
    high: float
    low: float
    volume: float
    change: float
    change_percent: float


class KLineResponse(BaseModel):
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float


# ==================== Trade ====================
class OrderCreate(BaseModel):
    symbol: str
    side: str  # buy, sell
    order_type: str  # market, limit
    quantity: float
    price: Optional[float] = None


class OrderResponse(BaseModel):
    id: int
    symbol: str
    side: str
    order_type: str
    quantity: float
    price: Optional[float]
    filled_price: Optional[float]
    status: str
    order_id: Optional[str]
    created_at: datetime
    filled_at: Optional[datetime]

    class Config:
        from_attributes = True


# ==================== Position ====================
class PositionResponse(BaseModel):
    id: int
    symbol: str
    side: str
    quantity: float
    entry_price: float
    current_price: Optional[float]
    leverage: int
    unrealized_pnl: float
    stop_loss: Optional[float]
    take_profit: Optional[float]
    status: str
    opened_at: datetime

    class Config:
        from_attributes = True


# ==================== Strategy ====================
class StrategyCreate(BaseModel):
    name: str
    strategy_type: str
    config: dict


class StrategyResponse(BaseModel):
    id: int
    name: str
    strategy_type: str
    config: dict
    is_active: bool
    total_pnl: float
    win_rate: float
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Statistics ====================
class StatisticsResponse(BaseModel):
    total_pnl: float
    today_pnl: float
    win_rate: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_profit: float
    avg_loss: float


# ==================== AI Signals ====================
class AISignalCreate(BaseModel):
    symbol: str
    signal_type: str  # buy, sell, hold
    price: float
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    reason: Optional[str] = None


class AISignalUpdate(BaseModel):
    status: Optional[str] = None  # pending, executed, expired, cancelled


class AISignalResponse(BaseModel):
    id: int
    symbol: str
    signal_type: str
    price: float
    confidence: float
    reason: Optional[str]
    status: str
    executed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Analytics ====================
class TrendData(BaseModel):
    date: str
    pnl: float
    trades: int


class SymbolData(BaseModel):
    symbol: str
    total_pnl: float
    trades: int
    win_rate: float
    avg_profit: float
    avg_loss: float


class SideData(BaseModel):
    side: str
    total_pnl: float
    trades: int
    win_rate: float


class AnalyticsResponse(BaseModel):
    # 总体统计
    total_pnl: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    avg_profit: float
    avg_loss: float
    profit_loss_ratio: float  # 盈亏比

    # 趋势数据
    trends: List[TrendData]

    # 交易对分析
    symbols: List[SymbolData]

    # 多空分析
    sides: List[SideData]

    # 最大回撤
    max_drawdown: float

    # 持仓统计
    open_positions: int
    closed_positions: int


# ==================== Strategy Recommendation ====================
class MarketAnalysis(BaseModel):
    """市场分析结果"""
    symbol: str
    price: float
    change_percent: float
    volatility: float
    volume: float
    volume_change: float
    trend_strength: float
    market_condition: str
    rsi: Optional[float] = None
    ma20: Optional[float] = None
    ma50: Optional[float] = None


class StrategyRecommendationResponse(BaseModel):
    """策略推荐响应"""
    id: int
    symbol: str
    recommended_strategy: str
    market_condition: str
    confidence: float
    price: float
    volatility: Optional[float]
    volume: Optional[float]
    volume_change: Optional[float]
    trend_strength: Optional[float]
    reason: Optional[str]
    is_applied: bool
    created_at: datetime

    class Config:
        from_attributes = True


class StrategyRecommendationRequest(BaseModel):
    """策略推荐请求"""
    symbol: str = Field(default="BTC/USDT", description="交易对")
    timeframe: str = Field(default="1h", description="时间框架")
