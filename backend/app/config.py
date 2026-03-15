"""应用配置"""
import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""

    # 应用
    APP_NAME: str = "OKX Auto Trader"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 数据库 - 自动转换为绝对路径
    DATABASE_URL: str = ""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.DATABASE_URL:
            db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "okx_trader.db")
            self.DATABASE_URL = f"sqlite+aiosqlite:///{db_path.replace(chr(92), '/')}"

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # 交易所
    DEFAULT_EXCHANGE: str = "okx"
    OKX_API_BASE_URL: str = "https://www.okx.com"

    # 风控
    MAX_POSITION_PERCENT: float = 10.0  # 单币种最大仓位占比
    DEFAULT_LEVERAGE: int = 3  # 默认杠杆
    STOP_LOSS_PERCENT: float = 5.0  # 止损比例
    MAX_DAILY_LOSS: float = 15.0  # 日内最大亏损
    CIRCUIT_BREAKER_COUNT: int = 3  # 熔断连续止损次数

    # AI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4"

    class Config:
        env_file = ".env"
        extra = "allow"


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


settings = get_settings()
