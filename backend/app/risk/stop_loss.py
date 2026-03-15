"""
风控模块 - 止盈止损执行器
实现自动止损止盈逻辑
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import ccxt

from app.models import Position, Order
from app.config import settings

logger = logging.getLogger(__name__)


class StopLossTakeProfitExecutor:
    """止盈止损执行器"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def check_all_positions(self, user_id: int) -> Dict[str, Any]:
        """检查所有持仓的止盈止损"""
        result = await self.db.execute(
            select(Position).where(
                Position.user_id == user_id,
                Position.status == 'open'
            )
        )
        positions = result.scalars().all()
        
        triggered = []
        for pos in positions:
            action = await self.check_position(pos)
            if action:
                triggered.append(action)
                await self.execute_action(action)
        
        return {
            'checked': len(positions),
            'triggered': len(triggered),
            'actions': triggered
        }
    
    async def check_position(self, position: Position) -> Optional[Dict]:
        """检查单个持仓是否触发止盈止损"""
        if not position.current_price:
            return None
        
        entry_price = position.entry_price
        current_price = position.current_price
        
        # 计算盈亏比例
        if position.side == 'long':
            pnl_percent = (current_price - entry_price) / entry_price * 100
        else:  # short
            pnl_percent = (entry_price - current_price) / entry_price * 100
        
        # 检查止损
        if position.stop_loss:
            if position.side == 'long' and current_price <= position.stop_loss:
                return {
                    'type': 'stop_loss',
                    'position_id': position.id,
                    'symbol': position.symbol,
                    'action': 'close',
                    'reason': f'价格 {current_price} 触及止损价 {position.stop_loss}'
                }
            elif position.side == 'short' and current_price >= position.stop_loss:
                return {
                    'type': 'stop_loss',
                    'position_id': position.id,
                    'symbol': position.symbol,
                    'action': 'close',
                    'reason': f'价格 {current_price} 触及止损价 {position.stop_loss}'
                }
        
        # 检查止盈
        if position.take_profit:
            if position.side == 'long' and current_price >= position.take_profit:
                return {
                    'type': 'take_profit',
                    'position_id': position.id,
                    'symbol': position.symbol,
                    'action': 'close',
                    'reason': f'价格 {current_price} 触及止盈价 {position.take_profit}'
                }
            elif position.side == 'short' and current_price <= position.take_profit:
                return {
                    'type': 'take_profit',
                    'position_id': position.id,
                    'symbol': position.symbol,
                    'action': 'close',
                    'reason': f'价格 {current_price} 触及止盈价 {position.take_profit}'
                }
        
        # 检查百分比止损
        stop_loss_percent = getattr(settings, 'STOP_LOSS_PERCENT', 5.0)
        if pnl_percent <= -stop_loss_percent:
            return {
                'type': 'stop_loss_percent',
                'position_id': position.id,
                'symbol': position.symbol,
                'action': 'close',
                'reason': f'亏损 {abs(pnl_percent):.2f}%, 触发 {stop_loss_percent}% 止损'
            }
        
        # 检查百分比止盈
        take_profit_percent = getattr(settings, 'TAKE_PROFIT_PERCENT', 10.0)
        if pnl_percent >= take_profit_percent:
            return {
                'type': 'take_profit_percent',
                'position_id': position.id,
                'symbol': position.symbol,
                'action': 'close',
                'reason': f'盈利 {pnl_percent:.2f}%, 触发 {take_profit_percent}% 止盈'
            }
        
        return None
    
    async def execute_action(self, action: Dict) -> bool:
        """执行止盈止损操作"""
        try:
            position_id = action['position_id']
            symbol = action['symbol']
            
            # 获取持仓
            position = await self.db.get(Position, position_id)
            if not position or position.status != 'open':
                return False
            
            # 获取用户账户
            from app.models import ExchangeAccount
            result = await self.db.execute(
                select(ExchangeAccount).where(
                    ExchangeAccount.user_id == position.user_id,
                    ExchangeAccount.is_active == True
                ).limit(1)
            )
            account = result.scalar_one_or_none()
            
            if not account or not account.api_key:
                logger.warning(f"用户 {position.user_id} 没有有效的交易账户")
                return False
            
            # 创建平仓订单
            close_side = 'sell' if position.side == 'long' else 'buy'
            
            order = Order(
                user_id=position.user_id,
                account_id=account.id,
                symbol=symbol,
                side=close_side,
                order_type='market',
                quantity=position.quantity,
                status='pending',
                note=f"{action['type']}: {action['reason']}"
            )
            self.db.add(order)
            
            # 尝试执行交易所订单
            try:
                exchange_class = getattr(ccxt, account.exchange)
                exchange = exchange_class({
                    'apiKey': account.api_key,
                    'secret': account.api_secret,
                    'password': account.passphrase,
                    'enableRateLimit': True,
                })
                
                if account.is_testnet:
                    exchange.set_sandbox_mode(True)
                
                # 市价平仓
                result = exchange.create_order(
                    symbol=symbol,
                    type='market',
                    side=close_side,
                    amount=position.quantity
                )
                
                order.order_id = result.get('id')
                order.status = 'filled'
                order.filled_price = result.get('average') or position.current_price
                
            except Exception as e:
                order.status = 'failed'
                order.error_message = str(e)
                logger.error(f"止盈止损订单执行失败: {e}")
            
            # 更新持仓状态
            position.status = 'closed'
            position.closed_at = datetime.utcnow()
            
            # 计算实际盈亏
            if order.filled_price:
                if position.side == 'long':
                    pnl = (order.filled_price - position.entry_price) * position.quantity
                else:
                    pnl = (position.entry_price - order.filled_price) * position.quantity
                position.realized_pnl = pnl
            
            await self.db.commit()
            
            logger.info(f"止盈止损执行成功: {action['type']}, {symbol}, {action['reason']}")
            return True
            
        except Exception as e:
            logger.error(f"止盈止损执行失败: {e}")
            await self.db.rollback()
            return False


class RiskControlChecker:
    """风控检查器"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def check_daily_loss(self, user_id: int) -> Optional[Dict]:
        """检查日内亏损是否超过限制"""
        max_daily_loss = getattr(settings, 'MAX_DAILY_LOSS', 15.0)  # 15%
        
        # 获取今日平仓的订单
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        result = await self.db.execute(
            select(Order).where(
                Order.user_id == user_id,
                Order.status == 'filled',
                Order.filled_at >= today_start
            )
        )
        orders = result.scalars().all()
        
        # 计算今日盈亏
        total_pnl = 0.0
        for order in orders:
            # 这里需要关联持仓计算盈亏，简化处理
            pass
        
        # 返回是否触发限制
        return {
            'triggered': False,  # 需要完善计算逻辑
            'total_pnl': total_pnl,
            'max_loss_percent': max_daily_loss
        }
    
    async def check_circuit_breaker(self, user_id: int) -> Dict:
        """检查熔断机制 - 连续止损次数"""
        circuit_breaker_count = getattr(settings, 'CIRCUIT_BREAKER_COUNT', 3)
        
        # 获取最近 N 次亏损交易
        recent_orders = await self.db.execute(
            select(Order).where(
                Order.user_id == user_id,
                Order.status == 'filled',
                Order.side.in_(['sell', 'buy'])  # 需要根据实际盈亏判断
            ).order_by(Order.filled_at.desc()).limit(circuit_breaker_count)
        )
        orders = recent_orders.scalars().all()
        
        # 简化：假设最近 N 次都是止损
        loss_count = len(orders)
        
        return {
            'triggered': loss_count >= circuit_breaker_count,
            'consecutive_losses': loss_count,
            'threshold': circuit_breaker_count,
            'cooldown_hours': 1  # 冷静期1小时
        }
