"""
现货网格交易引擎 (v2 - PR测试)
实现完整的网格交易逻辑，包括：
1. 网格价格计算
2. 订单执行
3. 止盈止损
4. 持仓管理

使用说明:
1. 创建策略时设置 strategy_type='grid'
2. 配置参数:
   - symbol: 交易对 (如 BTC/USDT)
   - grid_count: 网格数量
   - grid_spacing: 网格间距 (如 0.01 = 1%)
   - position_size: 每格仓位大小
   - stop_loss_percent: 止损比例
   - take_profit_percent: 止盈比例
3. 启动策略后会自动执行网格交易
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Strategy, Position, Order
from app.config import settings

logger = logging.getLogger(__name__)


class GridTradingEngine:
    """现货网格交易引擎"""
    
    def __init__(self, strategy_id: int, config: Dict[str, Any], db: AsyncSession):
        self.strategy_id = strategy_id
        self.config = config
        self.db = db
        self.exchange = None
        
    async def initialize(self, exchange):
        """初始化交易所连接"""
        self.exchange = exchange
        
    async def get_current_price(self, symbol: str) -> float:
        """获取当前市场价格"""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker['last']
        except Exception as e:
            logger.error(f"获取价格失败: {e}")
            # 返回配置中的参考价格
            return self.config.get('reference_price', 50000)
    
    def calculate_grid_prices(self, current_price: float) -> Dict[str, Any]:
        """计算网格价格区间"""
        grid_count = self.config.get('grid_count', 10)
        grid_spacing = self.config.get('grid_spacing', 0.01)  # 1%
        position_size = self.config.get('position_size', 0.01)  # 仓位大小
        max_position = self.config.get('max_position', 0.1)  # 最大仓位
        
        # 计算价格区间
        price_range = current_price * grid_spacing * grid_count
        lower_price = current_price - price_range / 2
        upper_price = current_price + price_range / 2
        
        # 生成网格
        grid_prices = []
        for i in range(grid_count):
            price = lower_price + (i * (price_range / grid_count))
            grid_prices.append({
                'level': i,
                'buy_price': price,
                'sell_price': price * (1 + grid_spacing),
                'quantity': position_size,
                'active': True
            })
        
        return {
            'current_price': current_price,
            'lower_price': lower_price,
            'upper_price': upper_price,
            'grid_prices': grid_prices,
            'max_position': max_position
        }
    
    async def check_and_execute_orders(self, symbol: str, grid_info: Dict) -> List[Dict]:
        """检查并执行网格订单"""
        executed_orders = []
        current_price = grid_info['current_price']
        grids = grid_info['grid_prices']
        
        # 获取当前持仓
        position = await self.get_position(symbol)
        current_qty = position['quantity'] if position else 0
        max_qty = grid_info['max_position']
        
        for grid in grids:
            if not grid['active']:
                continue
                
            buy_price = grid['buy_price']
            sell_price = grid['sell_price']
            qty = grid['quantity']
            
            # 买入条件：价格触及买入价且未超过最大仓位
            if current_price <= buy_price * 1.001 and current_qty + qty <= max_qty:
                order = await self.execute_order(symbol, 'buy', qty, buy_price)
                if order:
                    executed_orders.append(order)
                    current_qty += qty
                    logger.info(f"网格买入: {symbol} @ {buy_price}, 数量: {qty}")
            
            # 卖出条件：价格触及卖出价且有持仓
            elif current_price >= sell_price * 0.999 and current_qty >= qty:
                order = await self.execute_order(symbol, 'sell', qty, sell_price)
                if order:
                    executed_orders.append(order)
                    current_qty -= qty
                    logger.info(f"网格卖出: {symbol} @ {sell_price}, 数量: {qty}")
        
        return executed_orders
    
    async def get_position(self, symbol: str) -> Optional[Dict]:
        """获取当前持仓"""
        result = await self.db.execute(
            select(Position).where(
                Position.symbol == symbol,
                Position.status == 'open'
            )
        )
        pos = result.scalar_one_or_none()
        
        if pos:
            return {
                'id': pos.id,
                'quantity': pos.quantity,
                'entry_price': pos.entry_price,
                'side': pos.side
            }
        return None
    
    async def execute_order(self, symbol: str, side: str, quantity: float, 
                          price: Optional[float] = None) -> Optional[Dict]:
        """执行订单"""
        try:
            # 创建本地订单记录
            order = Order(
                strategy_id=self.strategy_id,
                symbol=symbol,
                side=side,
                order_type='limit' if price else 'market',
                quantity=quantity,
                price=price,
                status='pending'
            )
            self.db.add(order)
            await self.db.commit()
            await self.db.refresh(order)
            
            # 执行交易所订单
            order_params = {
                'symbol': symbol,
                'type': 'limit' if price else 'market',
                'side': side,
                'amount': quantity,
            }
            if price:
                order_params['price'] = price
            
            result = self.exchange.create_order(**order_params)
            
            # 更新订单状态
            order.order_id = result.get('id')
            order.status = result.get('status', 'open')
            order.filled_price = result.get('average') or price
            await self.db.commit()
            
            return {
                'order_id': order.id,
                'exchange_order_id': result.get('id'),
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'price': price,
                'status': order.status
            }
            
        except Exception as e:
            logger.error(f"订单执行失败: {e}")
            return None
    
    async def check_stop_loss_take_profit(self, symbol: str) -> Optional[Dict]:
        """检查止盈止损"""
        position = await self.get_position(symbol)
        if not position:
            return None
        
        current_price = await self.get_current_price(symbol)
        
        # 计算盈亏
        entry_price = position['entry_price']
        quantity = position['quantity']
        
        if position['side'] == 'long':
            pnl_percent = (current_price - entry_price) / entry_price * 100
        else:
            pnl_percent = (entry_price - current_price) / entry_price * 100
        
        # 检查止损
        stop_loss = self.config.get('stop_loss_percent', 5)
        if pnl_percent <= -stop_loss:
            return {
                'action': 'stop_loss',
                'reason': f'亏损 {abs(pnl_percent):.2f}%, 触发止损',
                'symbol': symbol,
                'quantity': quantity
            }
        
        # 检查止盈
        take_profit = self.config.get('take_profit_percent', 10)
        if pnl_percent >= take_profit:
            return {
                'action': 'take_profit',
                'reason': f'盈利 {pnl_percent:.2f}%, 触发止盈',
                'symbol': symbol,
                'quantity': quantity
            }
        
        return None
    
    async def execute_stop_loss_take_profit(self, action_info: Dict) -> Dict:
        """执行止盈止损"""
        symbol = action_info['symbol']
        quantity = action_info['quantity']
        
        position = await self.get_position(symbol)
        if not position:
            return {'status': 'no_position'}
        
        # 平仓（反向操作）
        side = 'sell' if position['side'] == 'long' else 'buy'
        current_price = await self.get_current_price(symbol)
        
        order = await self.execute_order(symbol, side, quantity, current_price)
        
        if order:
            # 更新持仓状态
            pos = await self.db.get(Position, position['id'])
            if pos:
                pos.status = 'closed'
                pos.closed_at = datetime.utcnow()
                await self.db.commit()
            
            logger.info(f"{action_info['action']}: 平仓 {symbol}, 数量: {quantity}")
        
        return {
            'status': 'executed',
            'action': action_info['action'],
            'order': order
        }
    
    async def run_grid_strategy(self, symbol: str) -> Dict[str, Any]:
        """运行网格策略"""
        try:
            # 1. 获取当前价格
            current_price = await self.get_current_price(symbol)
            
            # 2. 计算网格
            grid_info = self.calculate_grid_prices(current_price)
            
            # 3. 检查止盈止损
            sl_tp = await self.check_stop_loss_take_profit(symbol)
            if sl_tp:
                result = await self.execute_stop_loss_take_profit(sl_tp)
                return {
                    'status': 'sl_tp_triggered',
                    'action': sl_tp['action'],
                    'result': result
                }
            
            # 4. 执行网格订单
            orders = await self.check_and_execute_orders(symbol, grid_info)
            
            return {
                'status': 'executed',
                'current_price': current_price,
                'orders_count': len(orders),
                'orders': orders
            }
            
        except Exception as e:
            logger.error(f"网格策略执行失败: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }


class GridStrategyConfig:
    """网格策略配置验证"""
    
    @staticmethod
    def validate(config: Dict[str, Any]) -> tuple[bool, str]:
        """验证策略配置"""
        required = ['symbol', 'grid_count', 'grid_spacing', 'position_size']
        
        for field in required:
            if field not in config:
                return False, f"缺少必需字段: {field}"
        
        # 验证数值范围
        if config.get('grid_count', 0) < 2:
            return False, "网格数量至少为2"
        
        if config.get('grid_spacing', 0) <= 0 or config.get('grid_spacing', 1) > 0.1:
            return False, "网格间距应在0-10%之间"
        
        if config.get('position_size', 0) <= 0:
            return False, "仓位大小必须大于0"
        
        return True, "配置有效"


# 默认网格策略配置
DEFAULT_GRID_CONFIG = {
    'grid_count': 10,           # 网格数量
    'grid_spacing': 0.01,       # 网格间距 1%
    'position_size': 0.01,       # 每格仓位 0.01 BTC
    'max_position': 0.1,         # 最大仓位 0.1 BTC
    'stop_loss_percent': 5,      # 止损 5%
    'take_profit_percent': 10,   # 止盈 10%
    'reference_price': 50000,     # 参考价格
}
