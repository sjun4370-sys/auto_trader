"""
条件单模块 - 止盈止损设置
实现用户自定义止盈止损条件单
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import User, Position
from app.api.deps import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/conditional-orders", tags=["条件单"])


# ============ Schemas ============

class StopLossTakeProfitCreate(BaseModel):
    """创建止盈止损条件单"""
    symbol: str
    position_id: int
    stop_loss_price: Optional[float] = None
    take_profit_price: Optional[float] = None
    stop_loss_percent: Optional[float] = None
    take_profit_percent: Optional[float] = None


class StopLossTakeProfitResponse(BaseModel):
    id: int
    symbol: str
    position_id: int
    stop_loss_price: Optional[float]
    take_profit_price: Optional[float]
    stop_loss_percent: Optional[float]
    take_profit_percent: Optional[float]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ConditionalOrderCreate(BaseModel):
    """创建条件单"""
    symbol: str
    side: str  # buy, sell
    order_type: str  # market, limit
    quantity: float
    price: Optional[float] = None
    
    # 触发条件
    condition_type: str  # price_above, price_below, percentage_change
    condition_value: float
    
    # 有效期
    expires_at: Optional[datetime] = None


class ConditionalOrderResponse(BaseModel):
    id: int
    user_id: int
    symbol: str
    side: str
    order_type: str
    quantity: float
    price: Optional[float]
    condition_type: str
    condition_value: float
    is_active: bool
    is_triggered: bool
    expires_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ============ 止盈止损设置 ============

@router.post("/stop-loss-take-profit", response_model=StopLossTakeProfitResponse)
async def set_stop_loss_take_profit(
    data: StopLossTakeProfitCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """设置持仓的止盈止损"""
    
    # 验证持仓是否存在
    position = await db.get(Position, data.position_id)
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="持仓不存在"
        )
    
    if position.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限操作此持仓"
        )
    
    if position.status != 'open':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="持仓已平仓"
        )
    
    # 验证价格
    if data.stop_loss_price and data.take_profit_price:
        if position.side == 'long':
            if data.stop_loss_price >= position.entry_price:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="止损价必须低于开仓价"
                )
            if data.take_profit_price <= position.entry_price:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="止盈价必须高于开仓价"
                )
        else:  # short
            if data.stop_loss_price <= position.entry_price:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="止损价必须高于开仓价"
                )
            if data.take_profit_price >= position.entry_price:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="止盈价必须低于开仓价"
                )
    
    # 更新持仓的止盈止损设置
    if data.stop_loss_price:
        position.stop_loss = data.stop_loss_price
    if data.take_profit_price:
        position.take_profit = data.take_profit_price
    
    await db.commit()
    await db.refresh(position)
    
    return StopLossTakeProfitResponse(
        id=position.id,
        symbol=position.symbol,
        position_id=position.id,
        stop_loss_price=position.stop_loss,
        take_profit_price=position.take_profit,
        stop_loss_percent=data.stop_loss_percent,
        take_profit_percent=data.take_profit_percent,
        is_active=True,
        created_at=position.opened_at
    )


@router.get("/stop-loss-take-profit/{position_id}", response_model=StopLossTakeProfitResponse)
async def get_stop_loss_take_profit(
    position_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取持仓的止盈止损设置"""
    
    position = await db.get(Position, position_id)
    if not position or position.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="持仓不存在"
        )
    
    return StopLossTakeProfitResponse(
        id=position.id,
        symbol=position.symbol,
        position_id=position.id,
        stop_loss_price=position.stop_loss,
        take_profit_price=position.take_profit,
        stop_loss_percent=None,
        take_profit_percent=None,
        is_active=True,
        created_at=position.opened_at
    )


@router.delete("/stop-loss-take-profit/{position_id}")
async def delete_stop_loss_take_profit(
    position_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除止盈止损设置"""
    
    position = await db.get(Position, position_id)
    if not position or position.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="持仓不存在"
        )
    
    position.stop_loss = None
    position.take_profit = None
    
    await db.commit()
    
    return {"message": "止盈止损设置已删除"}


# ============ 条件单 ============

@router.post("/orders", response_model=ConditionalOrderResponse)
async def create_conditional_order(
    data: ConditionalOrderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    创建条件单

    TODO: 实现持久化存储条件单到数据库
    TODO: 实现条件单触发检查定时任务
    当前: 仅验证输入，不保存数据
    """

    # 验证条件
    if data.condition_type == 'price_above' and data.condition_value <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="价格必须大于0"
        )

    if data.condition_type == 'price_below' and data.condition_value <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="价格必须大于0"
        )

    if data.condition_type == 'percentage_change':
        if data.condition_value < 0 or data.condition_value > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="涨跌幅必须在0-100之间"
            )

    # TODO: 保存到数据库
    return ConditionalOrderResponse(
        id=1,
        user_id=current_user.id,
        symbol=data.symbol,
        side=data.side,
        order_type=data.order_type,
        quantity=data.quantity,
        price=data.price,
        condition_type=data.condition_type,
        condition_value=data.condition_value,
        is_active=True,
        is_triggered=False,
        expires_at=data.expires_at,
        created_at=datetime.utcnow()
    )


@router.get("/orders")
async def list_conditional_orders(
    active_only: bool = True,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取条件单列表

    TODO: 从数据库查询实际保存的条件单
    当前: 返回空列表
    """
    # TODO: 从数据库查询
    return []


@router.delete("/orders/{order_id}")
async def cancel_conditional_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    取消条件单

    TODO: 从数据库删除实际保存的条件单
    当前: 返回假成功响应
    """
    return {"message": "条件单已取消"}
