"""数据模型"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    accounts = relationship("ExchangeAccount", back_populates="user", cascade="all, delete-orphan")
    positions = relationship("Position", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    strategies = relationship("Strategy", back_populates="user", cascade="all, delete-orphan")


class ExchangeAccount(Base):
    """交易所账户模型"""
    __tablename__ = "exchange_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exchange = Column(String(20), nullable=False)  # okx, binance, etc.
    account_name = Column(String(50))
    api_key = Column(String(255))
    api_secret = Column(String(255))
    passphrase = Column(String(255))  # For OKX
    is_testnet = Column(Boolean, default=True)  # Testnet by default
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    user = relationship("User", back_populates="accounts")
    positions = relationship("Position", back_populates="account", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="account", cascade="all, delete-orphan")

    @property
    def has_api_credentials(self) -> bool:
        """是否已配置可交易密钥"""
        return bool((self.api_key or "").strip() and (self.api_secret or "").strip())


class Position(Base):
    """持仓模型"""
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("exchange_accounts.id"), nullable=True)
    symbol = Column(String(20), nullable=False)  # BTC/USDT
    side = Column(String(10), nullable=False)  # long, short
    quantity = Column(Float, nullable=False)
    entry_price = Column(Float, nullable=False)
    current_price = Column(Float)
    leverage = Column(Integer, default=1)
    unrealized_pnl = Column(Float, default=0.0)
    realized_pnl = Column(Float, default=0.0)
    stop_loss = Column(Float)  # 止损价格
    take_profit = Column(Float)  # 止盈价格
    status = Column(String(20), default="open")  # open, closed, liquidated
    opened_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime)

    # 关联
    user = relationship("User", back_populates="positions")
    account = relationship("ExchangeAccount", back_populates="positions")


class Order(Base):
    """订单模型"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("exchange_accounts.id"), nullable=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=True)  # 策略ID
    symbol = Column(String(20), nullable=False)
    side = Column(String(10), nullable=False)  # buy, sell
    order_type = Column(String(20), nullable=False)  # market, limit
    quantity = Column(Float, nullable=False)
    price = Column(Float)  # For limit orders
    filled_price = Column(Float)  # Actual fill price
    status = Column(String(20), default="pending")  # pending, filled, cancelled, failed
    order_id = Column(String(100))  # Exchange order ID
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    filled_at = Column(DateTime)

    # 关联
    user = relationship("User", back_populates="orders")
    account = relationship("ExchangeAccount", back_populates="orders")


class Strategy(Base):
    """策略模型"""
    __tablename__ = "strategies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    strategy_type = Column(String(50), nullable=False)  # grid, dca, trend, ai
    config = Column(JSON)  # Strategy configuration
    is_active = Column(Boolean, default=False)
    total_pnl = Column(Float, default=0.0)
    win_rate = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    user = relationship("User", back_populates="strategies")
    runs = relationship("StrategyRun", back_populates="strategy", cascade="all, delete-orphan")


class StrategyRun(Base):
    """策略运行记录模型"""
    __tablename__ = "strategy_runs"

    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=False)
    status = Column(String(20), default="pending")  # pending, running, completed, stopped, error
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)
    last_executed_at = Column(DateTime)
    execution_count = Column(Integer, default=0)
    orders_count = Column(Integer, default=0)
    error_message = Column(Text)
    
    # 关联
    strategy = relationship("Strategy", back_populates="runs")


class TradeLog(Base):
    """交易日志模型"""
    __tablename__ = "trade_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    symbol = Column(String(20))
    action = Column(String(20), nullable=False)  # buy, sell, stop_loss, take_profit
    quantity = Column(Float)
    price = Column(Float)
    pnl = Column(Float)  # Profit/Loss
    note = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class AIChatHistory(Base):
    """AI对话历史模型"""
    __tablename__ = "ai_chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关联
    user = relationship("User")
