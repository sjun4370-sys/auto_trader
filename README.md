# OKX Auto Trader

基于 Python FastAPI + React 的虚拟货币 AI 自动交易系统

## 特性

- **用户认证** - 安全注册/登录系统，支持 JWT Token 认证
- **账户管理** - 多交易所账户添加、编辑、删除
- **实时行情** - 市场数据实时获取与展示
- **交易功能** - 支持市价单、限价单、条件单等下单方式
- **持仓管理** - 实时持仓监控与盈亏分析
- **策略交易** - 创建、启动、停止交易策略
- **网格交易** - 内置网格交易引擎，自动进行套利
- **风控系统** - 止损、强平机制保障资金安全
- **AI 助手** - AI 智能信号分析与聊天功能
- **数据分析** - 交易数据统计与可视化

## 技术栈

### 后端

| 技术 | 说明 |
|------|------|
| Python 3.10+ | 编程语言 |
| FastAPI | Web 框架 |
| SQLAlchemy | ORM |
| SQLite | 数据库 |
| CCXT | 交易所集成 |
| Pydantic | 数据验证 |
| JWT | 用户认证 |

### 前端

| 技术 | 版本 | 说明 |
|------|------|------|
| React | 18.2.0 | UI 框架 |
| TypeScript | 5.3.0 | 类型系统 |
| Vite | 5.0.0 | 构建工具 |
| Ant Design | 5.12.0 | UI 组件库 |
| React Router | 6.21.0 | 路由管理 |
| Axios | 1.6.0 | HTTP 客户端 |
| Recharts | 2.10.0 | 图表库 |
| Dayjs | 1.11.10 | 日期处理 |

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- npm 或 yarn

### 后端启动

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt
或
python -m pip install -r requirements.txt

# 复制环境配置
cp .env.example .env

# 启动服务
uvicorn app.main:app --reload
```

后端服务将在 http://localhost:8000 运行

### 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将在 http://localhost:3000 运行

### 首次配置

1. 访问 http://localhost:3000
2. 注册新用户
3. 在「账户」页面添加交易所 API
4. 建议先使用测试网模式进行测试

## 项目结构

```
okx_auto_trader/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── api/              # API 路由
│   │   │   ├── auth.py            # 认证接口
│   │   │   ├── accounts.py        # 账户接口
│   │   │   ├── market.py         # 行情接口
│   │   │   ├── trade.py          # 交易接口
│   │   │   ├── positions.py      # 持仓接口
│   │   │   ├── strategies.py     # 策略接口
│   │   │   ├── risk.py           # 风控接口
│   │   │   ├── ai.py             # AI 接口
│   │   │   ├── statistics.py     # 统计接口
│   │   │   └── ...
│   │   ├── engine/             # 交易引擎
│   │   │   ├── strategy_engine.py
│   │   │   └── grid_engine.py
│   │   ├── risk/              # 风控模块
│   │   ├── config.py          # 配置
│   │   ├── database.py        # 数据库
│   │   └── main.py            # 入口
│   ├── data/                  # 数据目录
│   └── requirements.txt        # 依赖
│
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── api/             # API 接口
│   │   │   ├── account.ts
│   │   │   ├── auth.ts
│   │   │   ├── market.ts
│   │   │   ├── position.ts
│   │   │   ├── strategy.ts
│   │   │   └── trade.ts
│   │   ├── pages/           # 页面组件
│   │   │   ├── Login.tsx
│   │   │   ├── Register.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Market.tsx
│   │   │   ├── Trade.tsx
│   │   │   ├── Positions.tsx
│   │   │   ├── Strategies.tsx
│   │   │   ├── Accounts.tsx
│   │   │   ├── Statistics.tsx
│   │   │   └── AIAssistant.tsx
│   │   ├── components/       # 公共组件
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
│
├── docs/                      # 项目文档
├── CLAUDE.md                  # AI 辅助开发指南
└── README.md                  # 项目说明
```

## 功能模块

### 后端 API 模块

| 模块 | 功能 |
|------|------|
| auth | 用户注册、登录、JWT 认证 |
| accounts | 交易所账户管理 |
| market | 市场行情数据 |
| trade | 交易下单、订单管理 |
| positions | 持仓查询与管理 |
| strategies | 策略创建、启动、停止 |
| strategy_monitor | 策略运行监控 |
| strategy_optimizer | 策略优化 |
| strategy_recommendation | 策略推荐 |
| risk | 风控规则管理 |
| ai | AI 信号分析 |
| ai_chat | AI 聊天功能 |
| ai_signals | AI 交易信号 |
| analytics | 数据分析 |
| statistics | 统计报表 |
| system_monitor | 系统监控 |
| notifications | 通知管理 |
| position_alerts | 持仓警报 |
| conditional_orders | 条件单 |

### 前端页面

| 页面 | 功能 |
|------|------|
| 登录/注册 | 用户认证 |
| 仪表盘 | 总览账户状态 |
| 市场 | 实时行情查看 |
| 交易 | 下单、撤单 |
| 持仓 | 当前持仓监控 |
| 账户 | 交易所账户管理 |
| 策略 | 交易策略管理 |
| 统计 | 交易数据分析 |
| AI 助手 | AI 智能分析 |

## 命令参考

### 后端命令

```bash
# 安装依赖
cd backend
pip install -r requirements.txt

# 启动开发服务器
uvicorn app.main:app --reload

# 运行测试
pytest
```

### 前端命令

```bash
# 安装依赖
cd frontend
npm install

# 启动开发服务器
npm run dev

# 类型检查和构建生产版本
npm run build

# 预览构建结果
npm run preview

# E2E 测试
npm run test:e2e

# E2E 测试（UI模式）
npm run test:e2e:ui
```

## 环境变量

| 变量 | 必填 | 说明 | 示例 |
|------|------|------|------|
| `APP_NAME` | 否 | 应用名称 | `OKX Auto Trader` |
| `APP_VERSION` | 否 | 版本号 | `1.0.0` |
| `DEBUG` | 否 | 调试模式 | `true`, `false` |
| `DATABASE_URL` | 是 | 数据库连接URL | `sqlite+aiosqlite:///./data/okx_trader.db` |
| `SECRET_KEY` | 是 | JWT密钥 | `your-secret-key-change-in-production` |
| `ALGORITHM` | 否 | JWT算法 | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 否 | Token过期时间(分钟) | `1440` |
| `DEFAULT_EXCHANGE` | 否 | 默认交易所 | `okx` |
| `OKX_API_BASE_URL` | 否 | OKX API地址 | `https://www.okx.com` |
| `MAX_POSITION_PERCENT` | 否 | 最大持仓比例 | `10.0` |
| `DEFAULT_LEVERAGE` | 否 | 默认杠杆 | `3` |
| `STOP_LOSS_PERCENT` | 否 | 止损比例 | `5.0` |
| `MAX_DAILY_LOSS` | 否 | 日内最大亏损 | `15.0` |
| `CIRCUIT_BREAKER_COUNT` | 否 | 熔断次数 | `3` |
| `OPENAI_API_KEY` | 否 | OpenAI API密钥 | - |
| `OPENAI_MODEL` | 否 | OpenAI模型 | `gpt-4` |

## API 文档

后端服务启动后访问：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 常见问题

### 数据库初始化失败

确保 `backend/data` 目录存在且有写权限

### CORS 错误

检查前端 `vite.config.ts` 中的代理配置

### 交易失败

1. 检查 API 密钥是否正确
2. 确认是否为测试网模式
3. 查看错误日志

## 贡献指南

详见 [CONTRIBUTING.md](./CONTRIBUTING.md)

## 许可证

MIT License

Copyright (c) 2024 OKX Auto Trader

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
