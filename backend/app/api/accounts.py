"""账户API"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import User, ExchangeAccount
from app.schemas import AccountCreate, AccountResponse, AccountUpdate
from app.api.deps import get_current_user

router = APIRouter(prefix="/accounts", tags=["账户"])


@router.get("", response_model=List[AccountResponse])
async def get_accounts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取账户列表"""
    result = await db.execute(
        select(ExchangeAccount).where(ExchangeAccount.user_id == current_user.id)
    )
    accounts = result.scalars().all()
    return accounts


@router.post("", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    account_data: AccountCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建账户"""
    if not account_data.api_key.strip() or not account_data.api_secret.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="创建交易账户时必须提供 api_key 和 api_secret"
        )

    account = ExchangeAccount(
        user_id=current_user.id,
        exchange=account_data.exchange,
        account_name=account_data.account_name,
        api_key=account_data.api_key.strip(),
        api_secret=account_data.api_secret.strip(),
        passphrase=account_data.passphrase,
        is_testnet=account_data.is_testnet
    )
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return account


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取账户详情"""
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
    return account


@router.patch("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: int,
    account_data: AccountUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新账户"""
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

    update_data = account_data.model_dump(exclude_unset=True)

    if "exchange" in update_data and update_data["exchange"] is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="exchange cannot be null"
        )

    for field, value in update_data.items():
        setattr(account, field, value)

    await db.commit()
    await db.refresh(account)
    return account


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除账户"""
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

    await db.delete(account)
    await db.commit()
