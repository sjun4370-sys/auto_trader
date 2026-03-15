"""AI买卖信号推送API"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import User, AISignal
from app.schemas import AISignalCreate, AISignalUpdate, AISignalResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/ai-signals", tags=["AI Signals"])


@router.post("", response_model=AISignalResponse, status_code=status.HTTP_201_CREATED)
async def create_signal(
    signal_data: AISignalCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建AI买卖信号"""
    # 验证信号类型
    if signal_data.signal_type not in ["buy", "sell", "hold"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="signal_type 必须是 buy, sell 或 hold"
        )

    # 创建信号记录
    signal = AISignal(
        user_id=current_user.id,
        symbol=signal_data.symbol,
        signal_type=signal_data.signal_type,
        price=signal_data.price,
        confidence=signal_data.confidence,
        reason=signal_data.reason,
        status="pending"
    )

    db.add(signal)
    await db.commit()
    await db.refresh(signal)

    return signal


@router.get("", response_model=List[AISignalResponse])
async def get_signals(
    symbol: Optional[str] = None,
    signal_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取AI信号列表"""
    query = select(AISignal).where(AISignal.user_id == current_user.id)

    if symbol:
        query = query.where(AISignal.symbol == symbol)

    if signal_type:
        query = query.where(AISignal.signal_type == signal_type)

    if status:
        query = query.where(AISignal.status == status)

    query = query.order_by(desc(AISignal.created_at)).limit(limit)

    result = await db.execute(query)
    signals = result.scalars().all()

    return signals


@router.get("/latest", response_model=List[AISignalResponse])
async def get_latest_signals(
    symbol: Optional[str] = None,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取最新的AI信号"""
    query = select(AISignal).where(AISignal.user_id == current_user.id)

    if symbol:
        query = query.where(AISignal.symbol == symbol)

    query = query.where(AISignal.status == "pending").order_by(desc(AISignal.created_at)).limit(limit)

    result = await db.execute(query)
    signals = result.scalars().all()

    return signals


@router.get("/{signal_id}", response_model=AISignalResponse)
async def get_signal(
    signal_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取AI信号详情"""
    result = await db.execute(
        select(AISignal).where(
            AISignal.id == signal_id,
            AISignal.user_id == current_user.id
        )
    )
    signal = result.scalar_one_or_none()

    if not signal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="信号不存在"
        )

    return signal


@router.patch("/{signal_id}", response_model=AISignalResponse)
async def update_signal(
    signal_id: int,
    signal_data: AISignalUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新AI信号状态"""
    result = await db.execute(
        select(AISignal).where(
            AISignal.id == signal_id,
            AISignal.user_id == current_user.id
        )
    )
    signal = result.scalar_one_or_none()

    if not signal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="信号不存在"
        )

    # 更新状态
    if signal_data.status:
        if signal_data.status not in ["pending", "executed", "expired", "cancelled"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="status 必须是 pending, executed, expired 或 cancelled"
            )
        signal.status = signal_data.status
        if signal_data.status == "executed":
            signal.executed_at = datetime.utcnow()

    await db.commit()
    await db.refresh(signal)

    return signal


@router.delete("/{signal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_signal(
    signal_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除AI信号"""
    result = await db.execute(
        select(AISignal).where(
            AISignal.id == signal_id,
            AISignal.user_id == current_user.id
        )
    )
    signal = result.scalar_one_or_none()

    if not signal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="信号不存在"
        )

    await db.delete(signal)
    await db.commit()

    return None


@router.post("/push")
async def push_signal(
    symbol: str,
    signal_type: str,
    price: float,
    confidence: float = 0.5,
    reason: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """推送AI信号（简化版API）"""
    if signal_type not in ["buy", "sell", "hold"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="signal_type 必须是 buy, sell 或 hold"
        )

    signal = AISignal(
        user_id=current_user.id,
        symbol=symbol,
        signal_type=signal_type,
        price=price,
        confidence=confidence,
        reason=reason,
        status="pending"
    )

    db.add(signal)
    await db.commit()
    await db.refresh(signal)

    return {
        "message": "信号推送成功",
        "signal_id": signal.id,
        "symbol": signal.symbol,
        "signal_type": signal.signal_type,
        "price": signal.price,
        "confidence": signal.confidence,
        "reason": signal.reason,
        "created_at": signal.created_at
    }


@router.post("/execute/{signal_id}")
async def execute_signal(
    signal_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """执行AI信号（标记为已执行）"""
    result = await db.execute(
        select(AISignal).where(
            AISignal.id == signal_id,
            AISignal.user_id == current_user.id
        )
    )
    signal = result.scalar_one_or_none()

    if not signal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="信号不存在"
        )

    if signal.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"信号状态为 {signal.status}，无法执行"
        )

    signal.status = "executed"
    signal.executed_at = datetime.utcnow()

    await db.commit()
    await db.refresh(signal)

    return {
        "message": "信号已执行",
        "signal_id": signal.id,
        "symbol": signal.symbol,
        "signal_type": signal.signal_type,
        "executed_at": signal.executed_at
    }
