"""策略执行引擎基类"""
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class StrategyEngine(ABC):
    """策略执行器基类"""
    
    def __init__(self, strategy_id: int, config: Dict[str, Any], db: AsyncSession):
        self.strategy_id = strategy_id
        self.config = config
        self.db = db
        self.is_running = False
        self.last_error: Optional[str] = None
        self.last_run_time: Optional[datetime] = None
        
    @abstractmethod
    async def execute(self) -> Dict[str, Any]:
        """执行策略逻辑，返回执行结果"""
        pass
    
    @abstractmethod
    async def check_signals(self) -> List[Dict[str, Any]]:
        """检查交易信号"""
        pass
    
    async def run(self):
        """策略运行主循环"""
        try:
            self.is_running = True
            self.last_run_time = datetime.utcnow()
            
            # 检查信号
            signals = await self.check_signals()
            
            # 执行策略
            if signals:
                result = await self.execute()
                return result
                
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"策略 {self.strategy_id} 执行错误: {e}")
        finally:
            self.is_running = False
    
    async def stop(self):
        """停止策略"""
        self.is_running = False
        logger.info(f"策略 {self.strategy_id} 已停止")


class GridStrategyEngine(StrategyEngine):
    """网格策略执行器"""
    
    async def check_signals(self) -> List[Dict[str, Any]]:
        """检查网格交易信号"""
        signals = []
        symbol = self.config.get("symbol", "BTC/USDT")
        
        # 获取当前价格
        # 这里需要调用market API获取价格
        # 简化实现：
        current_price = 50000  # 模拟价格
        
        grid_count = self.config.get("grid_count", 10)
        grid_spacing = self.config.get("grid_spacing", 0.01)  # 1%
        
        # 计算网格价格区间
        lower = current_price * (1 - grid_count * grid_spacing)
        upper = current_price * (1 + grid_count * grid_spacing)
        
        # 生成网格信号
        for i in range(grid_count):
            buy_price = lower + (i * grid_spacing * current_price)
            sell_price = buy_price * (1 + grid_spacing)
            
            if current_price <= buy_price * 1.001:  # 接近买入价
                signals.append({
                    "type": "buy",
                    "price": buy_price,
                    "side": "below",
                    "grid_level": i
                })
            elif current_price >= sell_price * 0.999:  # 接近卖出价
                signals.append({
                    "type": "sell", 
                    "price": sell_price,
                    "side": "above",
                    "grid_level": i
                })
        
        return signals
    
    async def execute(self) -> Dict[str, Any]:
        """执行网格策略"""
        signals = await self.check_signals()
        
        if not signals:
            return {"status": "no_signal", "message": "当前无交易信号"}
        
        executed_orders = []
        for signal in signals:
            # 这里调用trade API下单
            order = {
                "strategy_id": self.strategy_id,
                "signal": signal,
                "executed_at": datetime.utcnow().isoformat()
            }
            executed_orders.append(order)
        
        return {
            "status": "executed",
            "orders": executed_orders,
            "count": len(executed_orders)
        }


class TrendStrategyEngine(StrategyEngine):
    """趋势跟踪策略执行器"""
    
    async def check_signals(self) -> List[Dict[str, Any]]:
        """检查趋势交易信号"""
        signals = []
        
        # 获取K线数据
        symbol = self.config.get("symbol", "BTC/USDT")
        timeframe = self.config.get("timeframe", "1h")
        
        # 简化：使用技术指标计算
        # 实际需要获取K线数据并计算MA, RSI, MACD等
        
        # 模拟信号
        import random
        if random.random() > 0.7:
            signals.append({
                "type": "buy" if random.random() > 0.5 else "sell",
                "reason": "ma_cross",
                "confidence": random.uniform(0.6, 0.9)
            })
        
        return signals
    
    async def execute(self) -> Dict[str, Any]:
        """执行趋势策略"""
        signals = await self.check_signals()
        
        if not signals:
            return {"status": "no_signal"}
        
        return {
            "status": "executed",
            "signals": signals
        }


class DCAStrategyEngine(StrategyEngine):
    """定投策略执行器"""
    
    async def check_signals(self) -> List[Dict[str, Any]]:
        """检查定投信号"""
        signals = []
        
        # 检查是否到了定投时间
        interval = self.config.get("interval_hours", 24)
        
        # 简化：每次都返回买入信号
        signals.append({
            "type": "buy",
            "amount": self.config.get("amount", 100),
            "reason": "dca"
        })
        
        return signals
    
    async def execute(self) -> Dict[str, Any]:
        """执行定投策略"""
        signals = await self.check_signals()
        
        return {
            "status": "executed",
            "dca_orders": len(signals)
        }


def get_strategy_engine(strategy_type: str, strategy_id: int, config: Dict[str, Any], db: AsyncSession) -> StrategyEngine:
    """根据策略类型获取对应的执行器"""
    engines = {
        "grid": GridStrategyEngine,
        "trend": TrendStrategyEngine,
        "dca": DCAStrategyEngine,
    }
    
    engine_class = engines.get(strategy_type, StrategyEngine)
    return engine_class(strategy_id, config, db)
