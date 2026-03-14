# API 文档

## 认证

### 认证方式
- JWT Token (Bearer Token)
- Header: `Authorization: Bearer <token>`

## 接口列表

### 认证接口

#### POST /api/v1/auth/register
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

#### POST /api/v1/auth/login
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

#### GET /api/v1/auth/me
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

### 账户接口

#### GET /api/v1/accounts
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

#### POST /api/v1/accounts
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

### 行情接口

#### GET /api/v1/market/tickers
获取多个币种行情

**查询参数:**
- `symbols`: 逗号分隔的币种列表

#### GET /api/v1/market/ticker/{symbol}
获取单个币种行情

#### GET /api/v1/market/kline/{symbol}
获取K线数据

**查询参数:**
- `timeframe`: 时间框架 (1m, 5m, 15m, 1h, 4h, 1d)
- `limit`: 数量限制

### 交易接口

#### POST /api/v1/trade/order
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

#### GET /api/v1/trade/orders
获取订单列表

#### DELETE /api/v1/trade/order/{order_id}
取消订单

### 持仓接口

#### GET /api/v1/positions
获取持仓列表

**查询参数:**
- `status`: 持仓状态 (open, closed)

#### POST /api/v1/positions/close/{position_id}
平仓

### 策略接口

#### GET /api/v1/strategies
获取策略列表

#### POST /api/v1/strategies
创建策略

#### POST /api/v1/strategies/{strategy_id}/start
启动策略

#### POST /api/v1/strategies/{strategy_id}/stop
停止策略

### 风控接口

#### GET /api/v1/risk/check
风控检查

### AI接口

#### POST /api/v1/ai/signal
获取AI交易信号

#### POST /api/v1/ai/chat
AI对话

### 统计接口

#### GET /api/v1/statistics
获取统计数据

## 错误码

| 错误码 | 说明 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 认证失败 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 500 | 服务器错误 |
