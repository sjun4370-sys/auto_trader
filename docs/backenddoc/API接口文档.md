# API 接口文档

## 认证方式
- JWT Token (Bearer Token)
- Header: `Authorization: Bearer <token>`

## 基础路径
`/api/v1`

---

## 1. 认证接口 (Auth)

### POST /api/v1/auth/register
注册用户

**请求体:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

**响应:**
```json
{
  "id": 1,
  "username": "string",
  "email": "string",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00"
}
```

### POST /api/v1/auth/login
用户登录

**请求体:**
```json
{
  "username": "string",
  "password": "string"
}
```

**响应:**
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

### GET /api/v1/auth/me
获取当前用户信息

**响应:**
```json
{
  "id": 1,
  "username": "string",
  "email": "string",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00"
}
```

---

## 2. 账户接口 (Accounts)

### GET /api/v1/accounts
获取账户列表

**响应:**
```json
[
  {
    "id": 1,
    "exchange": "okx",
    "account_name": "string",
    "is_testnet": true,
    "is_active": true,
    "created_at": "2024-01-01T00:00:00"
  }
]
```

### POST /api/v1/accounts
创建账户

**请求体:**
```json
{
  "exchange": "okx",
  "account_name": "string",
  "api_key": "string",
  "api_secret": "string",
  "passphrase": "string",
  "is_testnet": true
}
```

### GET /api/v1/accounts/{account_id}
获取账户详情

### PATCH /api/v1/accounts/{account_id}
更新账户

### DELETE /api/v1/accounts/{account_id}
删除账户

---

## 3. 行情接口 (Market) - 无需认证

### GET /api/v1/market/tickers
获取多个币种行情

**查询参数:**
- `symbols`: 逗号分隔的币种列表 (可选)

### GET /api/v1/market/ticker/{symbol}
获取单个币种行情

**路径参数:**
- `symbol`: 交易对 (如 BTC/USDT)

### GET /api/v1/market/kline/{symbol}
获取K线数据

**路径参数:**
- `symbol`: 交易对

**查询参数:**
- `timeframe`: 时间框架 (1m, 5m, 15m, 1h, 4h, 1d)
- `limit`: 数量限制 (默认100)

### GET /api/v1/market/orderbook/{symbol}
获取订单簿

**路径参数:**
- `symbol`: 交易对

**查询参数:**
- `limit`: 订单数量限制 (默认10)

---

## 4. 交易接口 (Trade)

### POST /api/v1/trade/order
创建订单

**查询参数:**
- `account_id`: 账户ID

**请求体:**
```json
{
  "symbol": "BTC/USDT",
  "side": "buy",
  "order_type": "market",
  "quantity": 0.01,
  "price": 50000
}
```

### GET /api/v1/trade/orders
获取订单列表

**查询参数:**
- `symbol`: 交易对 (可选)
- `limit`: 数量限制

### GET /api/v1/trade/order/{order_id}
获取订单详情

### DELETE /api/v1/trade/order/{order_id}
取消订单

---

## 5. 持仓接口 (Positions)

### GET /api/v1/positions
获取持仓列表

**查询参数:**
- `status`: 持仓状态 (open, closed)

### GET /api/v1/positions/{position_id}
获取持仓详情

### POST /api/v1/positions/close/{position_id}
平仓

---

## 6. 策略接口 (Strategies)

### GET /api/v1/strategies
获取策略列表

### POST /api/v1/strategies
创建策略

**请求体:**
```json
{
  "name": "string",
  "strategy_type": "grid",
  "config": {}
}
```

### GET /api/v1/strategies/{strategy_id}
获取策略详情

### PATCH /api/v1/strategies/{strategy_id}
更新策略

### DELETE /api/v1/strategies/{strategy_id}
删除策略

### POST /api/v1/strategies/{strategy_id}/start
启动策略

### POST /api/v1/strategies/{strategy_id}/stop
停止策略

---

## 7. 风控接口 (Risk)

### GET /api/v1/risk/check
风控检查

### GET /api/v1/risk/positions
仓位限制查询

### GET /api/v1/risk/config
获取风控配置

---

## 8. 统计接口 (Statistics)

### GET /api/v1/statistics
获取统计数据

---

## 9. AI 接口 (AI)

### POST /api/v1/ai/signal
获取AI交易信号

**请求体:**
```json
{
  "symbol": "BTC/USDT",
  "timeframe": "1h"
}
```

### POST /api/v1/ai/chat
AI对话

**请求体:**
```json
{
  "message": "string"
}
```

### GET /api/v1/ai/analysis/{symbol}
AI分析

**路径参数:**
- `symbol`: 交易对

---

## 10. AI 对话助手接口 (AI-Chat)

### POST /api/v1/ai-chat/ask
AI对话提问

**请求体:**
```json
{
  "message": "string"
}
```

### GET /api/v1/ai-chat/history
获取对话历史

**查询参数:**
- `limit`: 数量限制

### DELETE /api/v1/ai-chat/history
清空对话历史

### GET /api/v1/ai-chat/stats
获取对话统计

---

## 11. AI 信号接口 (AI-Signals)

### POST /api/v1/ai-signals
创建AI信号

**请求体:**
```json
{
  "symbol": "BTC/USDT",
  "signal_type": "buy",
  "price": 50000,
  "confidence": 0.8,
  "reason": "string"
}
```

### GET /api/v1/ai-signals
获取AI信号列表

**查询参数:**
- `symbol`: 交易对 (可选)
- `signal_type`: 信号类型 (可选)
- `status`: 状态 (可选)
- `limit`: 数量限制

### GET /api/v1/ai-signals/latest
获取最新信号

**查询参数:**
- `symbol`: 交易对 (可选)
- `limit`: 数量限制

### GET /api/v1/ai-signals/{signal_id}
获取信号详情

### PATCH /api/v1/ai-signals/{signal_id}
更新信号状态

### DELETE /api/v1/ai-signals/{signal_id}
删除信号

### POST /api/v1/ai-signals/push
推送AI信号

**请求体:**
```json
{
  "symbol": "BTC/USDT",
  "signal_type": "buy",
  "price": 50000,
  "confidence": 0.8,
  "reason": "string"
}
```

### POST /api/v1/ai-signals/execute/{signal_id}
执行AI信号

---

## 12. 数据分析接口 (Analytics)

### GET /api/v1/analytics
获取交易数据分析

**查询参数:**
- `days`: 天数
- `symbol`: 交易对 (可选)

### GET /api/v1/analytics/summary
获取分析摘要

---

## 13. 策略监控接口 (Strategy-Monitor)

### GET /api/v1/strategy-monitor/runs/{strategy_id}
获取策略运行历史

### GET /api/v1/strategy-monitor/runs/{strategy_id}/latest
获取策略最新运行状态

### GET /api/v1/strategy-monitor/stats/{strategy_id}
获取策略详细统计

### GET /api/v1/strategy-monitor/dashboard
获取监控仪表盘

### GET /api/v1/strategy-monitor/positions
获取所有持仓

### GET /api/v1/strategy-monitor/orders/recent
获取最近订单

**查询参数:**
- `limit`: 数量限制

---

## 14. 条件单接口 (Conditional-Orders)

### POST /api/v1/conditional-orders/stop-loss-take-profit
设置止盈止损

**请求体:**
```json
{
  "position_id": 1,
  "stop_loss": 45000,
  "take_profit": 55000
}
```

### GET /api/v1/conditional-orders/stop-loss-take-profit/{position_id}
获取止盈止损

### DELETE /api/v1/conditional-orders/stop-loss-take-profit/{position_id}
删除止盈止损

### POST /api/v1/conditional-orders/orders
创建条件单

**请求体:**
```json
{
  "symbol": "BTC/USDT",
  "side": "buy",
  "order_type": "limit",
  "quantity": 0.01,
  "price": 50000,
  "trigger_price": 49000
}
```

### GET /api/v1/conditional-orders/orders
获取条件单列表

**查询参数:**
- `active_only`: 仅活跃 (可选)

### DELETE /api/v1/conditional-orders/orders/{order_id}
取消条件单

---

## 15. 仓位提醒接口 (Position-Alerts)

### POST /api/v1/position-alerts/
创建仓位提醒

**请求体:**
```json
{
  "symbol": "BTC/USDT",
  "alert_type": "price_above",
  "threshold": 50000
}
```

### GET /api/v1/position-alerts/
获取仓位提醒列表

**查询参数:**
- `symbol`: 交易对 (可选)

### GET /api/v1/position-alerts/check/{symbol}
检查是否触发提醒

### DELETE /api/v1/position-alerts/{alert_id}
删除仓位提醒

### POST /api/v1/position-alerts/{alert_id}/toggle
启用/禁用提醒

---

## 16. 系统监控接口 (System-Monitor)

### GET /api/v1/system-monitor/status
获取系统状态

### GET /api/v1/system-monitor/connection-check
检查交易所连接

**查询参数:**
- `exchange`: 交易所名称

### GET /api/v1/system-monitor/connection-quick
快速检查连接

**查询参数:**
- `exchange`: 交易所名称

### GET /api/v1/system-monitor/pending-orders
获取未完成订单

**查询参数:**
- `user_id`: 用户ID

### POST /api/v1/system-monitor/cancel-pending-orders
撤销所有未完成订单

**请求体:**
```json
{
  "user_id": 1,
  "account_id": 1
}
```

### POST /api/v1/system-monitor/service-start
记录服务启动

### POST /api/v1/system-monitor/service-stop
记录服务停止

**请求体:**
```json
{
  "reason": "string"
}
```

### POST /api/v1/system-monitor/check-recovery
检查恢复状态

---

## 17. 策略优化器接口 (Strategy-Optimizer)

### GET /api/v1/strategy-optimizer/analyze/{strategy_id}
分析策略表现

**查询参数:**
- `days`: 分析天数

### GET /api/v1/strategy-optimizer/history/{strategy_id}
获取优化历史

**查询参数:**
- `limit`: 数量限制

---

## 18. 策略推荐接口 (Strategy-Recommendation)

### GET /api/v1/strategy-recommendation/analyze
分析市场

**查询参数:**
- `symbol`: 交易对
- `timeframe`: 时间框架

### GET /api/v1/strategy-recommendation/analyze-and-recommend
分析并推荐

**查询参数:**
- `symbol`: 交易对
- `timeframe`: 时间框架

### GET /api/v1/strategy-recommendation/history
获取推荐历史

**查询参数:**
- `symbol`: 交易对 (可选)
- `limit`: 数量限制

### GET /api/v1/strategy-recommendation/{recommendation_id}
获取推荐详情

---

## 19. 通知管理接口 (Notifications)

### POST /api/v1/notifications/
创建通知

**请求体:**
```json
{
  "title": "string",
  "content": "string",
  "notification_type": "trade",
  "level": "info"
}
```

### GET /api/v1/notifications/
获取通知列表

**查询参数:**
- `notification_type`: 通知类型 (可选)
- `level`: 级别 (可选)
- `is_read`: 已读状态 (可选)
- `page`: 页码
- `page_size`: 每页数量

### GET /api/v1/notifications/unread-count
获取未读数量

### GET /api/v1/notifications/stats
获取通知统计

### GET /api/v1/notifications/{notification_id}
获取通知详情

### POST /api/v1/notifications/{notification_id}/read
标记已读

### POST /api/v1/notifications/read-all
全部标记已读

### DELETE /api/v1/notifications/{notification_id}
删除通知

### DELETE /api/v1/notifications/
清空通知

**查询参数:**
- `read_only`: 仅已读 (可选)

---

## 错误码

| 错误码 | 说明 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 认证失败 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 422 | 验证错误 |
| 500 | 服务器错误 |
