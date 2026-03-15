"""策略调度器"""
import asyncio
import logging
from typing import Dict, Optional
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import ccxt

from app.models import Strategy, StrategyRun, ExchangeAccount
from app.engine.strategy_engine import get_strategy_engine
from app.engine.grid_engine import GridTradingEngine

logger = logging.getLogger(__name__)


class StrategyScheduler:
    """策略调度器管理类"""
    
    _instance: Optional["StrategyScheduler"] = None
    _scheduler: Optional[AsyncIOScheduler] = None
    _running_strategies: Dict[int, bool] = {}  # strategy_id -> is_running
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._scheduler is None:
            self._scheduler = AsyncIOScheduler()
    
    def start(self):
        """启动调度器"""
        if not self._scheduler.running:
            self._scheduler.start()
            logger.info("策略调度器已启动")
    
    def stop(self):
        """停止调度器"""
        if self._scheduler.running:
            self._scheduler.shutdown()
            logger.info("策略调度器已停止")
    
    async def start_strategy(self, strategy_id: int, db: AsyncSession, user_id: int = None):
        """启动策略"""
        # 获取策略配置
        result = await db.execute(
            select(Strategy).where(Strategy.id == strategy_id)
        )
        strategy = result.scalar_one_or_none()
        
        if not strategy:
            raise ValueError(f"策略 {strategy_id} 不存在")
        
        if strategy.id in self._running_strategies:
            raise ValueError(f"策略 {strategy_id} 已在运行中")
        
        # 获取用户ID
        if user_id is None:
            user_id = strategy.user_id
        
        # 创建策略运行记录
        run = StrategyRun(
            strategy_id=strategy_id,
            status="running",
            started_at=datetime.utcnow()
        )
        db.add(run)
        await db.commit()
        await db.refresh(run)
        
        # 设置运行状态
        self._running_strategies[strategy_id] = True
        
        # 添加定时任务
        interval_minutes = strategy.config.get("interval_minutes", 5)
        
        job_id = f"strategy_{strategy_id}"
        
        self._scheduler.add_job(
            self._execute_strategy,
            trigger=IntervalTrigger(minutes=interval_minutes),
            args=[strategy_id, strategy.strategy_type, strategy.config, db, run.id, user_id],
            id=job_id,
            replace_existing=True
        )
        
        strategy.is_active = True
        await db.commit()
        
        logger.info(f"策略 {strategy_id} 已启动，执行间隔 {interval_minutes} 分钟")
        
        return {"message": "策略已启动", "run_id": run.id}
    
    async def stop_strategy(self, strategy_id: int, db: AsyncSession):
        """停止策略"""
        if strategy_id not in self._running_strategies:
            raise ValueError(f"策略 {strategy_id} 未在运行")
        
        # 移除定时任务
        job_id = f"strategy_{strategy_id}"
        self._scheduler.remove_job(job_id)
        
        # 更新运行状态
        self._running_strategies.pop(strategy_id)
        
        # 更新策略状态
        result = await db.execute(
            select(Strategy).where(Strategy.id == strategy_id)
        )
        strategy = result.scalar_one_or_none()
        
        if strategy:
            strategy.is_active = False
            await db.commit()
        
        # 更新运行记录
        run_result = await db.execute(
            select(StrategyRun).where(
                StrategyRun.strategy_id == strategy_id,
                StrategyRun.status == "running"
            )
        )
        run = run_result.scalar_one_or_none()
        
        if run:
            run.status = "stopped"
            run.ended_at = datetime.utcnow()
            await db.commit()
        
        logger.info(f"策略 {strategy_id} 已停止")
        
        return {"message": "策略已停止"}
    
    async def _execute_strategy(self, strategy_id: int, strategy_type: str, 
                                config: dict, db: AsyncSession, run_id: int, user_id: int = None):
        """执行策略的定时任务"""
        if strategy_id not in self._running_strategies:
            return
        
        try:
            # 网格策略使用专用引擎
            if strategy_type == 'grid':
                # 获取用户的交易账户
                if user_id:
                    account_result = await db.execute(
                        select(ExchangeAccount).where(
                            ExchangeAccount.user_id == user_id,
                            ExchangeAccount.is_active == True
                        ).limit(1)
                    )
                    account = account_result.scalar_one_or_none()
                    
                    if not account or not account.api_key:
                        logger.warning(f"策略 {strategy_id}: 未找到交易账户")
                        return
                    
                    # 创建交易所实例
                    exchange_class = getattr(ccxt, account.exchange)
                    exchange = exchange_class({
                        'apiKey': account.api_key,
                        'secret': account.api_secret,
                        'password': account.passphrase,
                        'enableRateLimit': True,
                    })
                    
                    if account.is_testnet:
                        exchange.set_sandbox_mode(True)
                    
                    # 使用网格引擎
                    grid_engine = GridTradingEngine(strategy_id, config, db)
                    await grid_engine.initialize(exchange)
                    
                    symbol = config.get('symbol', 'BTC/USDT')
                    result = await grid_engine.run_grid_strategy(symbol)
                else:
                    result = {'status': 'error', 'error': '缺少用户ID'}
            else:
                # 其他策略使用通用引擎
                engine = get_strategy_engine(strategy_type, strategy_id, config, db)
                result = await engine.run()
            
            # 更新运行记录
            run_result = await db.execute(
                select(StrategyRun).where(StrategyRun.id == run_id)
            )
            run = run_result.scalar_one_or_none()
            
            if run:
                run.last_executed_at = datetime.utcnow()
                run.execution_count += 1
                
                if result.get("status") == "executed":
                    run.orders_count += result.get("count", 0)
                
                await db.commit()
            
            logger.info(f"策略 {strategy_id} 执行完成: {result}")
            
        except Exception as e:
            logger.error(f"策略 {strategy_id} 执行错误: {e}")
            
            # 记录错误
            run_result = await db.execute(
                select(StrategyRun).where(StrategyRun.id == run_id)
            )
            run = run_result.scalar_one_or_none()
            
            if run:
                run.error_message = str(e)
                await db.commit()
    
    def is_strategy_running(self, strategy_id: int) -> bool:
        """检查策略是否在运行"""
        return strategy_id in self._running_strategies
    
    def get_running_strategies(self) -> list:
        """获取所有运行中的策略"""
        return list(self._running_strategies.keys())


# 全局调度器实例
scheduler = StrategyScheduler()
