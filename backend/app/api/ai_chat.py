"""AI对话助手API"""
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from openai import AsyncOpenAI

from app.models import User, AIChatHistory
from app.api.deps import get_current_user, get_db
from app.config import settings

router = APIRouter(prefix="/ai-chat", tags=["AI Chat"])


# ==================== Pydantic 模型 ====================

class AskRequest(BaseModel):
    """提问请求"""
    message: str
    context: Optional[dict] = None  # 可选的上下文信息


class AskResponse(BaseModel):
    """提问响应"""
    answer: str
    timestamp: str


class ChatMessage(BaseModel):
    """对话消息"""
    role: str
    content: str
    created_at: datetime


class HistoryResponse(BaseModel):
    """历史记录响应"""
    messages: List[ChatMessage]
    total: int


# ==================== AI 服务 ====================

async def get_openai_client() -> Optional[AsyncOpenAI]:
    """获取 OpenAI 客户端"""
    if not settings.OPENAI_API_KEY:
        return None
    return AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def generate_ai_response(
    client: AsyncOpenAI,
    user_message: str,
    chat_history: List[dict],
    context: Optional[dict] = None
) -> str:
    """生成AI回复"""

    # 构建系统提示
    system_prompt = """你是一个专业的虚拟货币交易助手，专门帮助用户解答关于交易、策略和市场方面的问题。

你可以帮助用户：
1. 解释交易策略（如网格交易、趋势跟踪、DCA等）
2. 分析市场行情和趋势
3. 解答关于OKX交易所的问题
4. 提供交易风险管理建议
5. 解释技术指标和K线形态

请用简洁、专业的中文回答问题。如果问题与交易无关，请礼貌地引导用户回到交易话题。"""

    # 如果有额外上下文，添加到系统提示
    if context:
        context_info = []
        if "positions" in context:
            positions = context["positions"]
            if positions:
                pos_info = ", ".join([f"{p['symbol']}: {p['quantity']}@{p['entry_price']}" for p in positions[:3]])
                context_info.append(f"当前持仓: {pos_info}")
        if "balance" in context:
            context_info.append(f"账户余额: {context['balance']}")
        if "strategies" in context:
            strategies = context["strategies"]
            if strategies:
                strat_info = ", ".join([s["name"] for s in strategies[:3]])
                context_info.append(f"运行中的策略: {strat_info}")

        if context_info:
            system_prompt += f"\n\n用户当前状态:\n" + "\n".join(context_info)

    # 构建消息列表
    messages = [{"role": "system", "content": system_prompt}]

    # 添加历史记录（限制最近10条）
    for msg in chat_history[-10:]:
        messages.append({"role": msg["role"], "content": msg["content"]})

    # 添加当前问题
    messages.append({"role": "user", "content": user_message})

    try:
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=1000,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI服务暂时不可用: {str(e)}"


async def generate_simple_response(user_message: str, chat_history: List[dict]) -> str:
    """生成简单回复（当没有配置API Key时）"""

    # 简单的关键词匹配回复
    message_lower = user_message.lower()

    # 交易相关关键词
    if any(kw in message_lower for kw in ["交易", "买入", "卖出", "止损", "止盈"]):
        return """关于交易策略，我可以提供以下建议：

1. **网格交易**: 在震荡行情中设置价格区间，每个区间买入卖出，适合波动稳定的币种
2. **趋势跟踪**: 跟随大势，低买高卖，适合有明显趋势的行情
3. **DCA定投**: 定期定额买入，降低成本，适合长期投资

如需详细了解某个策略，请告诉我具体策略名称。"""

    if any(kw in message_lower for kw in ["网格", "grid"]):
        return """网格交易是一种在震荡行情中盈利的策略：

1. 设置价格区间（最高价和最低价）
2. 将区间分成若干网格
3. 每个网格价格买入一定数量
4. 价格每上涨一格卖出，每下跌一格买入
5. 赚取震荡收益

注意：网格交易不适合单边上涨或下跌的行情。"""

    if any(kw in message_lower for kw in ["策略", "strategy"]):
        return """当前支持的交易策略包括：

1. **现货网格**: 震荡行情中的自动交易
2. **合约网格**: 带杠杆的网格交易
3. **DCA定投**: 定期定额买入
4. **趋势跟踪**: 跟随趋势顺势交易
5. **P0风控**: 止盈止损和条件单

您想了解哪个策略的详细用法？"""

    if any(kw in message_lower for kw in ["市场", "行情", "价格", "分析"]):
        return """市场分析需要结合多个方面：

1. **基本面分析**: 关注项目进展、团队动态、宏观经济
2. **技术分析**: K线形态、均线、MACD、RSI等指标
3. **资金流向**: 观察大单和主力资金动向
4. **市场情绪**: 恐惧贪婪指数、社交媒体热度

建议结合多种分析方法做出交易决策。"""

    if any(kw in message_lower for kw in ["帮助", "help", "能做什么"]):
        return """我可以帮助您：

1. 解答交易策略相关问题
2. 解释市场行情和技术指标
3. 提供风险管理建议
4. 回答关于OKX交易所的操作问题
5. 帮助您理解各种交易概念

请告诉我您想了解什么？"""

    # 默认回复
    default_responses = [
        "感谢您的提问！您可以问我关于交易策略、市场分析、风险管理等方面的问题。",
        "我是一个专业的交易助手，专门帮助解答交易相关问题。请问有什么可以帮助您的？",
        "您可以询问具体的交易策略、市场行情分析或者风险管理建议。",
    ]

    import random
    return random.choice(default_responses)


# ==================== API 端点 ====================

@router.post("/ask", response_model=AskResponse)
async def ask_question(
    request: AskRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """AI对话 - 提问"""
    user_message = request.message.strip()

    if not user_message:
        raise HTTPException(status_code=400, detail="问题不能为空")

    # 获取用户最近的对话历史
    result = await db.execute(
        select(AIChatHistory)
        .where(AIChatHistory.user_id == current_user.id)
        .order_by(desc(AIChatHistory.created_at))
        .limit(20)
    )
    history_records = result.scalars().all()

    # 转换为消息列表
    chat_history = [
        {"role": msg.role, "content": msg.content}
        for msg in reversed(history_records)
    ]

    # 生成AI回复
    client = await get_openai_client()

    if client and settings.OPENAI_API_KEY:
        ai_response = await generate_ai_response(
            client=client,
            user_message=user_message,
            chat_history=chat_history,
            context=request.context
        )
    else:
        ai_response = await generate_simple_response(user_message, chat_history)

    # 保存用户消息
    user_msg = AIChatHistory(
        user_id=current_user.id,
        role="user",
        content=user_message
    )
    db.add(user_msg)

    # 保存AI回复
    assistant_msg = AIChatHistory(
        user_id=current_user.id,
        role="assistant",
        content=ai_response
    )
    db.add(assistant_msg)

    await db.commit()

    return AskResponse(
        answer=ai_response,
        timestamp=datetime.utcnow().isoformat()
    )


@router.get("/history", response_model=HistoryResponse)
async def get_chat_history(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取对话历史"""
    # 限制最大数量
    limit = min(limit, 100)

    # 获取对话历史
    result = await db.execute(
        select(AIChatHistory)
        .where(AIChatHistory.user_id == current_user.id)
        .order_by(desc(AIChatHistory.created_at))
        .limit(limit)
    )
    history_records = result.scalars().all()

    # 转换为响应格式（反转顺序使最早的消息在前）
    messages = [
        ChatMessage(
            role=msg.role,
            content=msg.content,
            created_at=msg.created_at
        )
        for msg in reversed(history_records)
    ]

    # 获取总数
    count_result = await db.execute(
        select(AIChatHistory)
        .where(AIChatHistory.user_id == current_user.id)
    )
    total = len(count_result.scalars().all())

    return HistoryResponse(
        messages=messages,
        total=total
    )


@router.delete("/history")
async def clear_chat_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """清空对话历史"""
    # 删除用户的所有对话历史
    result = await db.execute(
        select(AIChatHistory)
        .where(AIChatHistory.user_id == current_user.id)
    )
    records = result.scalars().all()

    for record in records:
        await db.delete(record)

    await db.commit()

    return {"message": "对话历史已清空"}


@router.get("/stats")
async def get_chat_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取对话统计信息"""
    # 统计对话数量
    result = await db.execute(
        select(AIChatHistory)
        .where(AIChatHistory.user_id == current_user.id)
    )
    total_messages = len(result.scalars().all())

    # 统计用户消息数量
    user_result = await db.execute(
        select(AIChatHistory)
        .where(
            AIChatHistory.user_id == current_user.id,
            AIChatHistory.role == "user"
        )
    )
    user_messages = len(user_result.scalars().all())

    # 统计AI回复数量
    assistant_result = await db.execute(
        select(AIChatHistory)
        .where(
            AIChatHistory.user_id == current_user.id,
            AIChatHistory.role == "assistant"
        )
    )
    assistant_messages = len(assistant_result.scalars().all())

    return {
        "total_messages": total_messages,
        "user_messages": user_messages,
        "assistant_messages": assistant_messages,
        "ai_available": bool(settings.OPENAI_API_KEY)
    }
