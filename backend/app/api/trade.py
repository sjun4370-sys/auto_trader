"""交易API"""
import ccxt
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.database import get_db
from app.models import User, ExchangeAccount, Order
from app.schemas import OrderCreate, OrderResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/trade", tags=["交易"])


def get_exchange(account: ExchangeAccount):
    """获取交易所实例"""
    exchange_class = getattr(ccxt, account.exchange)
    exchange = exchange_class({
        'apiKey': account.api_key,
        'secret': account.api_secret,
        'password': account.passphrase,
        'enableRateLimit': True,
    })

    # 设置测试网
    if account.is_testnet:
        exchange.set_sandbox_mode(True)

    return exchange


@router.post("/order", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    account_id: int = Query(..., description="账户ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建订单"""
    # 获取账户
    result = await db.execute(
        select(ExchangeAccount).where(
            ExchangeAccount.id == account_id,
            ExchangeAccount.user_id == current_user.id
        )
    )
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="账户不存在"
        )

    if not account.api_key or not account.api_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="账户未配置API密钥"
        )

    # 创建订单记录
    order = Order(
        user_id=current_user.id,
        account_id=account.id,
        symbol=order_data.symbol,
        side=order_data.side,
        order_type=order_data.order_type,
        quantity=order_data.quantity,
        price=order_data.price,
        status="pending"
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)

    # 执行交易
    try:
        exchange = get_exchange(account)

        order_params = {
            'symbol': order_data.symbol,
            'type': order_data.order_type,
            'side': order_data.side,
            'amount': order_data.quantity,
        }

        if order_data.order_type == 'limit' and order_data.price:
            order_params['price'] = order_data.price

        result = exchange.create_order(**order_params)

        # 更新订单状态
        order.order_id = result.get('id')
        order.status = result.get('status', 'filled')
        order.filled_price = result.get('average') or result.get('price')
        order.filled_at = result.get('datetime')

        await db.commit()
        await db.refresh(order)

    except Exception as e:
        order.status = 'failed'
        order.error_message = str(e)
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"交易失败: {str(e)}"
        )

    return order


@router.get("/orders", response_model=List[OrderResponse])
async def get_orders(
    symbol: str = Query(None),
    limit: int = Query(50, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取订单列表"""
    query = select(Order).where(Order.user_id == current_user.id)

    if symbol:
        query = query.where(Order.symbol == symbol)

    query = query.order_by(Order.created_at.desc()).limit(limit)

    result = await db.execute(query)
    orders = result.scalars().all()

    return orders


@router.get("/order/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取订单详情"""
    result = await db.execute(
        select(Order).where(
            Order.id == order_id,
            Order.user_id == current_user.id
        )
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )

    return order


@router.delete("/order/{order_id}")
async def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """取消订单"""
    result = await db.execute(
        select(Order).where(
            Order.id == order_id,
            Order.user_id == current_user.id
        )
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )

    if order.status not in ['pending', 'open']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="订单无法取消"
        )

    # 尝试取消交易所订单
    if order.order_id:
        try:
            account = await db.get(ExchangeAccount, order.account_id)
            if account and account.api_key:
                exchange = get_exchange(account)
                exchange.cancel_order(order.order_id, order.symbol)
        except Exception:
            pass  # 忽略取消失败

    order.status = 'cancelled'
    await db.commit()

    return {"message": "订单已取消"}
