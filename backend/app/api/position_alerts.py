"""
仓位管理提醒 API
实现自动加仓/减仓提醒功能

API Endpoints:
- POST /api/v1/position-alerts - 创建仓位提醒
- GET /api/v1/position-alerts - 获取提醒列表
- GET /api/v1/position-alerts/check/{symbol} - 检查是否触发
- DELETE /api/v1/position-alerts/{id} - 删除提醒
- POST /api/v1/position-alerts/{id}/toggle - 启用/禁用提醒
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.database import get_db
from app.models import User, Position
from app.api.deps import get_current_user

router = APIRouter(prefix="/position-alerts", tags=["仓位提醒"])


# ============ Schemas ============

class PositionAlertCreate(BaseModel):
    """创建仓位提醒"""
    symbol: str
    alert_type: str  # increase, decrease, threshold
    threshold_percent: float  # 阈值百分比
    enabled: bool = True


class PositionAlertResponse(BaseModel):
    id: int
    symbol: str
    alert_type: str
    threshold_percent: float
    enabled: bool
    created_at: datetime

    class Config:
        from_attributes = True


# 模拟提醒存储（实际应存入数据库）
_position_alerts = {}


@router.post("/", response_model=PositionAlertResponse)
async def create_position_alert(
    data: PositionAlertCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建仓位提醒"""
    
    # 验证阈值
    if data.threshold_percent <= 0 or data.threshold_percent > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="阈值必须在0-100之间"
        )
    
    # 创建提醒
    alert_id = len(_position_alerts) + 1
    alert = {
        "id": alert_id,
        "user_id": current_user.id,
        "symbol": data.symbol,
        "alert_type": data.alert_type,
        "threshold_percent": data.threshold_percent,
        "enabled": data.enabled,
        "created_at": datetime.utcnow()
    }
    
    key = f"{current_user.id}_{data.symbol}"
    if key not in _position_alerts:
        _position_alerts[key] = []
    _position_alerts[key].append(alert)
    
    return PositionAlertResponse(**alert)


@router.get("/", response_model=List[PositionAlertResponse])
async def list_position_alerts(
    symbol: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取仓位提醒列表"""
    
    alerts = []
    for key, user_alerts in _position_alerts.items():
        for alert in user_alerts:
            if alert["user_id"] == current_user.id:
                if symbol is None or alert["symbol"] == symbol:
                    alerts.append(PositionAlertResponse(**alert))
    
    return alerts


@router.get("/check/{symbol}")
async def check_position_alerts(
    symbol: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """检查是否触发仓位提醒"""
    
    # 获取当前持仓
    result = await db.execute(
        select(Position).where(
            Position.user_id == current_user.id,
            Position.symbol == symbol,
            Position.status == "open"
        )
    )
    positions = result.scalars().all()
    
    # 计算总仓位
    total_value = sum(p.quantity * (p.current_price or p.entry_price) for p in positions)
    total_capital = 10000
    position_percent = (total_value / total_capital * 100) if total_capital > 0 else 0
    
    key = f"{current_user.id}_{symbol}"
    alerts = _position_alerts.get(key, [])
    
    triggered = []
    for alert in alerts:
        if not alert["enabled"]:
            continue
        
        threshold = alert["threshold_percent"]
        alert_type = alert["alert_type"]
        
        if alert_type == "threshold" and position_percent >= threshold:
            triggered.append({
                "alert_id": alert["id"],
                "type": "threshold",
                "message": f"仓位已达到 {position_percent:.2f}%，超过阈值 {threshold}%",
                "current_percent": position_percent
            })
        elif alert_type == "increase" and position_percent >= threshold:
            triggered.append({
                "alert_id": alert["id"],
                "type": "increase",
                "message": f"仓位增加至 {position_percent:.2f}%，触发提醒",
                "current_percent": position_percent
            })
        elif alert_type == "decrease" and position_percent <= threshold:
            triggered.append({
                "alert_id": alert["id"],
                "type": "decrease",
                "message": f"仓位下降至 {position_percent:.2f}%，触发提醒",
                "current_percent": position_percent
            })
    
    return {
        "symbol": symbol,
        "position_percent": position_percent,
        "triggered_alerts": triggered
    }


@router.delete("/{alert_id}")
async def delete_position_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除仓位提醒"""
    
    deleted = False
    for key, alerts in list(_position_alerts.items()):
        for i, alert in enumerate(alerts):
            if alert["id"] == alert_id and alert["user_id"] == current_user.id:
                del alerts[i]
                deleted = True
                break
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="提醒不存在"
        )
    
    return {"message": "提醒已删除"}


@router.post("/{alert_id}/toggle")
async def toggle_position_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """启用/禁用仓位提醒"""
    
    for key, alerts in _position_alerts.items():
        for alert in alerts:
            if alert["id"] == alert_id and alert["user_id"] == current_user.id:
                alert["enabled"] = not alert["enabled"]
                return {
                    "message": f"提醒已{'启用' if alert['enabled'] else '禁用'}",
                    "enabled": alert["enabled"]
                }
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="提醒不存在"
    )
