"""
系统风控模块
实现交易所连接状态监控、连接失败自动撤销订单、服务宕机备援功能
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import ccxt

from app.models import SystemStatus
from app.config import settings

logger = logging.getLogger(__name__)


class SystemMonitor:
    """系统监控器"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_status(self) -> SystemStatus:
        """获取或创建系统状态记录"""
        result = await self.db.execute(
            select(SystemStatus).order_by(SystemStatus.id.desc()).limit(1)
        )
        status = result.scalar_one_or_none()

        if not status:
            status = SystemStatus(
                status="running",
                exchange_status="unknown",
                last_heartbeat=datetime.utcnow()
            )
            self.db.add(status)
            await self.db.commit()
            await self.db.refresh(status)

        return status

    async def update_status(
        self,
        status: Optional[str] = None,
        exchange_status: Optional[str] = None,
        error_message: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> SystemStatus:
        """更新系统状态"""
        system_status = await self.get_or_create_status()

        if status:
            system_status.status = status
        if exchange_status:
            system_status.exchange_status = exchange_status
        if error_message:
            system_status.error_message = error_message
        if metadata:
            system_status.extra_data = metadata

        system_status.last_heartbeat = datetime.utcnow()
        system_status.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(system_status)

        return system_status

    async def check_exchange_connection(self, exchange_id: str = "okx") -> Dict[str, Any]:
        """检查交易所连接状态"""
        result = {
            "exchange": exchange_id,
            "connected": False,
            "latency_ms": None,
            "error": None,
            "timestamp": datetime.utcnow().isoformat()
        }

        try:
            exchange_class = getattr(ccxt, exchange_id)
            exchange = exchange_class({
                'enableRateLimit': True,
                'timeout': 10000,
            })

            # 尝试获取服务器时间测试连接
            start_time = datetime.utcnow()
            await exchange.fetch_time()
            latency = (datetime.utcnow() - start_time).total_seconds() * 1000

            result["connected"] = True
            result["latency_ms"] = round(latency, 2)

            logger.info(f"交易所 {exchange_id} 连接正常, 延迟: {latency}ms")

        except Exception as e:
            result["error"] = str(e)
            logger.error(f"交易所 {exchange_id} 连接失败: {e}")

        # 更新数据库状态
        system_status = await self.get_or_create_status()
        system_status.exchange_status = "connected" if result["connected"] else "disconnected"
        system_status.last_connection_check = datetime.utcnow()
        if result["error"]:
            system_status.error_message = result["error"]

        await self.db.commit()

        return result

    async def get_pending_orders(self, user_id: int = None) -> list:
        """获取未完成订单"""
        from app.models import Order

        query = select(Order).where(
            Order.status.in_(['pending', 'open'])
        )

        if user_id:
            query = query.where(Order.user_id == user_id)

        result = await self.db.execute(query)
        orders = result.scalars().all()

        # 更新待处理订单计数
        system_status = await self.get_or_create_status()
        system_status.pending_orders_count = len(orders)
        await self.db.commit()

        return orders

    async def cancel_pending_orders(
        self,
        user_id: Optional[int] = None,
        account_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """撤销未完成订单"""
        from app.models import Order, ExchangeAccount

        # 获取未完成订单
        query = select(Order).where(
            Order.status.in_(['pending', 'open'])
        )

        if user_id:
            query = query.where(Order.user_id == user_id)
        if account_id:
            query = query.where(Order.account_id == account_id)

        result = await self.db.execute(query)
        orders = result.scalars().all()

        cancelled_orders = []
        failed_cancellations = []

        for order in orders:
            try:
                # 获取账户信息
                if order.account_id:
                    account = await self.db.get(ExchangeAccount, order.account_id)
                    if account and account.api_key and order.order_id:
                        # 使用ccxt取消订单
                        exchange_class = getattr(ccxt, account.exchange or "okx")
                        exchange = exchange_class({
                            'apiKey': account.api_key,
                            'secret': account.api_secret,
                            'enableRateLimit': True,
                        })
                        if account.passphrase:
                            exchange.password = account.passphrase

                        await exchange.cancel_order(order.order_id, order.symbol)

                # 更新订单状态
                order.status = 'cancelled'
                order.error_message = '系统风控: 交易所连接失败,自动撤销'
                cancelled_orders.append({
                    'order_id': order.id,
                    'symbol': order.symbol,
                    'side': order.side,
                    'quantity': order.quantity
                })

            except Exception as e:
                logger.error(f"撤销订单 {order.id} 失败: {e}")
                failed_cancellations.append({
                    'order_id': order.id,
                    'error': str(e)
                })

        await self.db.commit()

        # 更新系统状态
        system_status = await self.get_or_create_status()
        system_status.pending_orders_count = len(orders) - len(cancelled_orders)
        await self.db.commit()

        return {
            'total_orders': len(orders),
            'cancelled': len(cancelled_orders),
            'failed': len(failed_cancellations),
            'cancelled_orders': cancelled_orders,
            'failed_cancellations': failed_cancellations
        }

    async def record_service_start(self, metadata: Optional[Dict] = None) -> SystemStatus:
        """记录服务启动"""
        system_status = await self.update_status(
            status="running",
            exchange_status="unknown",
            metadata=metadata
        )
        logger.info("系统服务已启动")
        return system_status

    async def record_service_stop(self, reason: str = "manual") -> SystemStatus:
        """记录服务停止"""
        system_status = await self.update_status(
            status="stopped",
            error_message=reason
        )
        logger.info(f"系统服务已停止: {reason}")
        return system_status

    async def check_and_recover(self) -> Dict[str, Any]:
        """服务恢复检查 - 检查并处理服务宕机期间的状态"""
        recovery_info = {
            "recovered": False,
            "actions_taken": [],
            "timestamp": datetime.utcnow().isoformat()
        }

        system_status = await self.get_or_create_status()

        # 检查是否是恢复场景（服务从error/stopped变为running）
        if system_status.status in ["error", "stopped"]:
            recovery_info["previous_status"] = system_status.status
            recovery_info["last_heartbeat"] = system_status.last_heartbeat.isoformat() if system_status.last_heartbeat else None

            # 如果服务恢复运行，检查是否需要处理之前未完成的订单
            if system_status.last_heartbeat:
                downtime = datetime.utcnow() - system_status.last_heartbeat
                recovery_info["downtime_seconds"] = downtime.total_seconds()

                # 如果宕机时间超过5分钟，检查未完成订单
                if downtime.total_seconds() > 300:
                    # 先检查连接状态
                    connection_check = await self.check_exchange_connection()
                    recovery_info["connection_status"] = connection_check

                    if connection_check["connected"]:
                        # 获取宕机期间的订单状态
                        pending = await self.get_pending_orders()
                        if pending:
                            recovery_info["pending_orders_count"] = len(pending)
                            # 可选：自动撤销或重新尝试
                            # 这里选择记录等待用户处理
                            recovery_info["actions_taken"].append(
                                f"检测到 {len(pending)} 个未完成订单,建议检查订单状态"
                            )

            # 更新为运行状态
            system_status.status = "running"
            await self.db.commit()
            recovery_info["recovered"] = True
            recovery_info["actions_taken"].append("系统状态已更新为运行中")

        return recovery_info

    async def get_system_status(self) -> Dict[str, Any]:
        """获取完整的系统状态"""
        system_status = await self.get_or_create_status()

        # 获取连接状态
        connection_status = await self.check_exchange_connection()

        return {
            "system": {
                "status": system_status.status,
                "last_heartbeat": system_status.last_heartbeat.isoformat() if system_status.last_heartbeat else None,
                "uptime": self._calculate_uptime(system_status.last_heartbeat),
                "created_at": system_status.created_at.isoformat() if system_status.created_at else None,
            },
            "exchange": {
                "status": system_status.exchange_status,
                "connection": connection_status,
                "last_check": system_status.last_connection_check.isoformat() if system_status.last_connection_check else None,
            },
            "orders": {
                "pending_count": system_status.pending_orders_count,
                "last_check": system_status.last_order_check.isoformat() if system_status.last_order_check else None,
            },
            "error": system_status.error_message,
            "metadata": system_status.extra_data,
        }

    def _calculate_uptime(self, last_heartbeat: Optional[datetime]) -> Optional[float]:
        """计算运行时间（秒）"""
        if not last_heartbeat:
            return None
        return (datetime.utcnow() - last_heartbeat).total_seconds()


# 独立的连接检查函数（不依赖数据库会话）
async def quick_connection_check(exchange_id: str = "okx") -> Dict[str, Any]:
    """快速检查交易所连接状态"""
    result = {
        "exchange": exchange_id,
        "connected": False,
        "latency_ms": None,
        "error": None,
        "timestamp": datetime.utcnow().isoformat()
    }

    try:
        exchange_class = getattr(ccxt, exchange_id)
        exchange = exchange_class({
            'enableRateLimit': True,
            'timeout': 10000,
        })

        start_time = datetime.utcnow()
        await exchange.fetch_time()
        latency = (datetime.utcnow() - start_time).total_seconds() * 1000

        result["connected"] = True
        result["latency_ms"] = round(latency, 2)

    except Exception as e:
        result["error"] = str(e)

    return result
