# 命令参考

## 后端命令

### 安装依赖
```bash
cd backend
pip install -r requirements.txt
```

### 启动开发服务器
```bash
uvicorn app.main:app --reload
```

### 运行测试
```bash
pytest
```

## 前端命令

### 安装依赖
```bash
cd frontend
npm install
```

### 启动开发服务器
```bash
npm run dev
```

### 构建生产版本
```bash
npm run build
```

## Docker 命令

### 构建镜像
```bash
docker build -t okx-auto-trader .
```

### 运行容器
```bash
docker run -p 8000:8000 -p 3000:3000 okx-auto-trader
```

## 常用 curl 命令

### 认证
```bash
# 注册
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"password123"}'

# 登录
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"password123"}'
```

### 行情
```bash
# 获取行情
curl -X GET http://localhost:8000/api/v1/market/tickers

# 获取K线
curl -X GET "http://localhost:8000/api/v1/market/kline/BTC/USDT?timeframe=1h&limit=100"
```

### 交易
```bash
# 下单
curl -X POST http://localhost:8000/api/v1/trade/order?account_id=1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"symbol":"BTC/USDT","side":"buy","order_type":"market","quantity":0.01}'

# 查询订单
curl -X GET http://localhost:8000/api/v1/trade/orders \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 持仓
```bash
# 获取持仓
curl -X GET http://localhost:8000/api/v1/positions \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 策略
```bash
# 获取策略
curl -X GET http://localhost:8000/api/v1/strategies \
  -H "Authorization: Bearer YOUR_TOKEN"
```
