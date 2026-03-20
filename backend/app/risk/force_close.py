"""
强制平仓模块
实现日内亏损自动平仓、熔断机制
"""
import logging
from typing import Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import ccxt

from app.models import Position, Order, TradeLog
from app.config import settings

logger = logging.getLogger(__name__)


class ForceCloseManager:
    """强制平仓管理器"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def check_and_close_positions(self, user_id: int, account) -> Dict[str, Any]:
        """检查并平仓所有需要强平的持仓"""
        
        # 获取所有持仓
        result = await self.db.execute(
            select(Position).where(
                Position.user_id == user_id,
                Position.status == 'open'
            )
        )
        positions = result.scalars().all()
        
        closed_positions = []
        errors = []
        
        for position in positions:
            try:
                # 检查是否需要强制平仓
                should_close, reason = await self.should_force_close(position)
                
                if should_close:
                    success = await self.force_close_position(position, account, reason)
                    if success:
                        closed_positions.append({
                            'position_id': position.id,
                            'symbol': position.symbol,
                            'reason': reason
                        })
            except Exception as e:
                errors.append({
                    'position_id': position.id,
                    'error': str(e)
                })
        
        return {
            'total_positions': len(positions),
            'closed': len(closed_positions),
            'closed_positions': closed_positions,
            'errors': errors
        }
    
    async def should_force_close(self, position: Position) -> tuple[bool, str]:
        """判断是否需要强制平仓"""
        
        # 检查是否设置了止盈止损价格
        if position.stop_loss or position.take_profit:
            if not position.current_price:
                return False, ""
            
            # 触发止损
            if position.stop_loss:
                if position.side == 'long' and position.current_price <= position.stop_loss:
                    return True, f"触发止损: 当前价 {position.current_price} <= 止损价 {position.stop_loss}"
                elif position.side == 'short' and position.current_price >= position.stop_loss:
                    return True, f"触发止损: 当前价 {position.current_price} >= 止损价 {position.stop_loss}"
            
            # 触发止盈
            if position.take_profit:
                if position.side == 'long' and position.current_price >= position.take_profit:
                    return True, f"触发止盈: 当前价 {position.current_price} >= 止盈价 {position.take_profit}"
                elif position.side == 'short' and position.current_price <= position.take_profit:
                    return True, f"触发止盈: 当前价 {position.current_price} <= 止盈价 {position.take_profit}"
        
        return False, ""
    
    async def force_close_position(self, position: Position, account, reason: str) -> bool:
        """强制平仓"""
        try:
            # 确定平仓方向
            close_side = 'sell' if position.side == 'long' else 'buy'
            
            # 创建平仓订单
            order = Order(
                user_id=position.user_id,
                account_id=account.id if account else None,
                symbol=position.symbol,
                side=close_side,
                order_type='market',
                quantity=position.quantity,
                status='pending',
                note=f"强制平仓: {reason}"
            )
            self.db.add(order)
            
            # 执行交易所订单
            if account and account.api_key:
                exchange_class = getattr(ccxt, account.exchange)
                exchange = exchange_class({
                    'apiKey': account.api_key,
                    'secret': account.api_secret,
                    'password': account.passphrase,
                    'enableRateLimit': True,
                })
                
                if account.is_testnet:
                    exchange.set_sandbox_mode(True)
                
                result = exchange.create_order(
                    symbol=position.symbol,
                    type='market',
                    side=close_side,
                    amount=position.quantity
                )

                # 只有 exchange 返回有效 order_id 时才认为订单成功
                if result and result.get('id'):
                    order.order_id = result.get('id')
                    order.status = 'filled'
                    order.filled_price = result.get('average') or position.current_price
                    # 更新持仓状态
                    position.status = 'closed'
                    position.closed_at = datetime.utcnow()
                else:
                    # 订单创建失败，不更新持仓状态
                    order.status = 'failed'
                    logger.error(f"强制平仓订单创建失败: {position.symbol}, result: {result}")
                    # 回滚该订单
                    await self.db.rollback()
                    return False
            else:
                # 无 API key 时，标记为模拟平仓
                position.status = 'closed'
                position.closed_at = datetime.utcnow()

            # 计算盈亏
            if order.filled_price:
                if position.side == 'long':
                    pnl = (order.filled_price - position.entry_price) * position.quantity
                else:
                    pnl = (position.entry_price - order.filled_price) * position.quantity
                position.realized_pnl = pnl

            # 记录交易日志
            log = TradeLog(
                user_id=position.user_id,
                symbol=position.symbol,
                action='force_close' if '强制' in reason else 'close',
                quantity=position.quantity,
                price=order.filled_price,
                pnl=position.realized_pnl,
                note=reason
            )
            self.db.add(log)

            await self.db.commit()

            logger.info(f"强制平仓成功: {position.symbol}, 原因: {reason}")
            return True
            
        except Exception as e:
            logger.error(f"强制平仓失败: {e}")
            await self.db.rollback()
            return False


class DailyLossChecker:
    """日内亏损检查器"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.max_daily_loss_percent = getattr(settings, 'MAX_DAILY_LOSS', 15.0)
    
    async def check_daily_loss(self, user_id: int) -> Dict[str, Any]:
        """检查日内亏损是否超过限制"""
        
        # 获取今日开始时间
        today_start = datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        
        # 获取今日所有成交订单
        result = await self.db.execute(
            select(Order).where(
                Order.user_id == user_id,
                Order.status == 'filled',
                Order.filled_at >= today_start
            )
        )
        orders = result.scalars().all()
        
        # 计算今日盈亏（简化计算）
        total_pnl = 0.0
        for order in orders:
            # 需要关联持仓计算，这里简化处理
            if order.side == 'sell':
                total_pnl += (order.filled_price or 0) * order.quantity
            else:
                total_pnl -= (order.filled_price or 0) * order.quantity
        
        # 计算亏损百分比（简化：假设初始资金10000）
        initial_capital = 10000
        loss_percent = abs(total_pnl) / initial_capital * 100 if total_pnl < 0 else 0
        
        return {
            'date': today_start.date(),
            'total_pnl': total_pnl,
            'loss_percent': loss_percent,
            'max_loss_percent': self.max_daily_loss_percent,
            'exceeded': loss_percent >= self.max_daily_loss_percent,
            'trades_count': len(orders)
        }


class CircuitBreaker:
    """熔断机制"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.breaker_count = getattr(settings, 'CIRCUIT_BREAKER_COUNT', 3)
        self.cooldown_hours = 1
    
    async def check_circuit_breaker(self, user_id: int) -> Dict[str, Any]:
        """检查是否触发熔断"""
        
        # 获取最近N笔订单
        result = await self.db.execute(
            select(Order).where(
                Order.user_id == user_id,
                Order.status == 'filled'
            ).order_by(Order.filled_at.desc()).limit(self.breaker_count)
        )
        orders = result.scalars().all()
        
        if len(orders) < self.breaker_count:
            return {
                'triggered': False,
                'reason': '交易次数不足'
            }
        
        # 简化：检查最近N笔是否都是亏损
        # 实际需要根据盈亏判断
        recent_trades = orders[:self.breaker_count]
        
        # 检查是否有冷静期
        last_loss_time = None
        for order in recent_trades:
            if order.filled_at:
                if last_loss_time is None or order.filled_at > last_loss_time:
                    last_loss_time = order.filled_at
        
        in_cooldown = False
        if last_loss_time:
            cooldown_end = last_loss_time + timedelta(hours=self.cooldown_hours)
            in_cooldown = datetime.utcnow() < cooldown_end
        
        return {
            'triggered': len(recent_trades) >= self.breaker_count and not in_cooldown,
            'consecutive_losses': len(recent_trades),
            'threshold': self.breaker_count,
            'in_cooldown': in_cooldown,
            'cooldown_hours': self.cooldown_hours,
            'cooldown_end': (last_loss_time + timedelta(hours=self.cooldown_hours)).isoformat() if last_loss_time else None
        }
    
    async def reset_circuit_breaker(self, user_id: int) -> bool:
        """重置熔断"""
        # 实际实现可能需要清除某些状态
        logger.info(f"熔断已重置: user_id={user_id}")
        return True
