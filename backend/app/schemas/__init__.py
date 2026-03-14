"""Pydantic Schemas"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


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
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    passphrase: Optional[str] = None
    is_testnet: bool = True


class AccountResponse(BaseModel):
    id: int
    exchange: str
    account_name: Optional[str]
    is_testnet: bool
    is_active: bool
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
