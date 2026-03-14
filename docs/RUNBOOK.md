# 运行手册

## 快速开始

### 1. 克隆项目
```bash
git clone <repository-url>
cd okx_auto_trader
```

### 2. 启动后端
```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\\Scripts\\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 复制环境配置
cp .env.example .env

# 启动服务
uvicorn app.main:app --reload
```

后端服务将在 http://localhost:8000 运行

### 3. 启动前端
```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将在 http://localhost:3000 运行

## Docker 部署

### 构建并运行
```bash
docker-compose up -d
```

## 首次配置

1. 访问 http://localhost:3000
2. 注册新用户
3. 在"账户"页面添加交易所API
4. 建议先使用测试网模式

## 常见问题

### 数据库初始化失败
确保 `backend/data` 目录存在且有写权限

### CORS 错误
检查前端 `vite.config.ts` 中的代理配置

### 交易失败
1. 检查API密钥是否正确
2. 确认是否为测试网模式
3. 查看错误日志

## API 文档

启动后访问:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
