"""
通知管理 API
实现用户通知功能，包括通知列表、标记已读、删除等
"""
from typing import List, Optional
from datetime import datetime
from enum import Enum
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.models import User
from app.api.deps import get_current_user

router = APIRouter(prefix="/notifications", tags=["通知管理"])


# ============ 枚举类型 ============

class NotificationType(str, Enum):
    """通知类型"""
    POSITION = "position"  # 仓位提醒
    RISK = "risk"  # 风控提醒
    TRADE = "trade"  # 交易通知
    STRATEGY = "strategy"  # 策略通知
    SYSTEM = "system"  # 系统通知
    ALERT = "alert"  # 通用提醒


class NotificationLevel(str, Enum):
    """通知级别"""
    INFO = "info"  # 信息
    WARNING = "warning"  # 警告
    ERROR = "error"  # 错误
    SUCCESS = "success"  # 成功


# ============ Schemas ============

class NotificationCreate(BaseModel):
    """创建通知"""
    title: str
    content: str
    notification_type: NotificationType = NotificationType.SYSTEM
    level: NotificationLevel = NotificationLevel.INFO
    related_id: Optional[int] = None  # 关联ID（如策略ID、仓位ID等）
    related_type: Optional[str] = None  # 关联类型


class NotificationResponse(BaseModel):
    """通知响应"""
    id: int
    title: str
    content: str
    notification_type: str
    level: str
    is_read: bool
    related_id: Optional[int] = None
    related_type: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationUpdate(BaseModel):
    """更新通知状态"""
    is_read: Optional[bool] = None


class NotificationStats(BaseModel):
    """通知统计"""
    total: int
    unread: int
    read: int
    by_type: dict
    by_level: dict


# 模拟通知存储（实际应存入数据库）
_notifications = {}
_notification_id_counter = 0


def _get_user_notifications(user_id: int) -> List[dict]:
    """获取用户的所有通知"""
    return _notifications.get(user_id, [])


def _add_notification(user_id: int, notification: dict) -> dict:
    """添加通知到用户列表"""
    global _notification_id_counter
    if user_id not in _notifications:
        _notifications[user_id] = []

    notification["id"] = _notification_id_counter + 1
    notification["created_at"] = datetime.utcnow()
    notification["is_read"] = False

    _notifications[user_id].insert(0, notification)  # 新通知放在最前面
    _notification_id_counter += 1

    return notification


@router.post("/", response_model=NotificationResponse)
async def create_notification(
    data: NotificationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建通知（用于系统内部创建通知或测试）"""
    notification = {
        "user_id": current_user.id,
        "title": data.title,
        "content": data.content,
        "notification_type": data.notification_type.value,
        "level": data.level.value,
        "related_id": data.related_id,
        "related_type": data.related_type,
    }

    result = _add_notification(current_user.id, notification)
    return NotificationResponse(**result)


@router.get("/", response_model=List[NotificationResponse])
async def list_notifications(
    notification_type: Optional[NotificationType] = None,
    level: Optional[NotificationLevel] = None,
    is_read: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取通知列表"""
    notifications = _get_user_notifications(current_user.id)

    # 过滤
    if notification_type:
        notifications = [n for n in notifications if n["notification_type"] == notification_type.value]
    if level:
        notifications = [n for n in notifications if n["level"] == level.value]
    if is_read is not None:
        notifications = [n for n in notifications if n["is_read"] == is_read]

    # 分页
    start = (page - 1) * page_size
    end = start + page_size
    paginated = notifications[start:end]

    return [NotificationResponse(**n) for n in paginated]


@router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取未读通知数量"""
    notifications = _get_user_notifications(current_user.id)
    unread_count = sum(1 for n in notifications if not n["is_read"])
    return {"unread_count": unread_count}


@router.get("/stats", response_model=NotificationStats)
async def get_notification_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取通知统计"""
    notifications = _get_user_notifications(current_user.id)

    total = len(notifications)
    unread = sum(1 for n in notifications if not n["is_read"])
    read = total - unread

    # 按类型统计
    by_type = {}
    for n in notifications:
        t = n["notification_type"]
        by_type[t] = by_type.get(t, 0) + 1

    # 按级别统计
    by_level = {}
    for n in notifications:
        l = n["level"]
        by_level[l] = by_level.get(l, 0) + 1

    return NotificationStats(
        total=total,
        unread=unread,
        read=read,
        by_type=by_type,
        by_level=by_level
    )


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取单个通知详情"""
    notifications = _get_user_notifications(current_user.id)
    for n in notifications:
        if n["id"] == notification_id:
            return NotificationResponse(**n)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="通知不存在"
    )


@router.post("/{notification_id}/read")
async def mark_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """标记通知为已读"""
    notifications = _get_user_notifications(current_user.id)
    for n in notifications:
        if n["id"] == notification_id:
            n["is_read"] = True
            return {"message": "已标记为已读", "notification": NotificationResponse(**n)}

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="通知不存在"
    )


@router.post("/read-all")
async def mark_all_as_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """标记所有通知为已读"""
    notifications = _get_user_notifications(current_user.id)
    count = 0
    for n in notifications:
        if not n["is_read"]:
            n["is_read"] = True
            count += 1

    return {"message": f"已标记 {count} 条通知为已读", "count": count}


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除通知"""
    notifications = _get_user_notifications(current_user.id)
    for i, n in enumerate(notifications):
        if n["id"] == notification_id:
            del notifications[i]
            return {"message": "通知已删除"}

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="通知不存在"
    )


@router.delete("/")
async def delete_all_notifications(
    read_only: bool = Query(False, description="是否只删除已读通知"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """清空通知"""
    notifications = _get_user_notifications(current_user.id)
    if read_only:
        # 只删除已读
        original_count = len(notifications)
        notifications[:] = [n for n in notifications if not n["is_read"]]
        deleted = original_count - len(notifications)
    else:
        # 删除全部
        deleted = len(notifications)
        notifications.clear()

    return {"message": f"已删除 {deleted} 条通知", "deleted": deleted}


# ============ 辅助函数：创建系统通知 ============

async def create_system_notification(
    user_id: int,
    title: str,
    content: str,
    notification_type: NotificationType = NotificationType.SYSTEM,
    level: NotificationLevel = NotificationLevel.INFO,
    related_id: Optional[int] = None,
    related_type: Optional[str] = None
):
    """创建系统通知的辅助函数"""
    notification = {
        "user_id": user_id,
        "title": title,
        "content": content,
        "notification_type": notification_type.value,
        "level": level.value,
        "related_id": related_id,
        "related_type": related_type,
    }
    return _add_notification(user_id, notification)
