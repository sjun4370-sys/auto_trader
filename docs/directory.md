# 目录结构

```
okx_auto_trader/
├── backend/                    # 后端
│   ├── app/
│   │   ├── api/              # API路由
│   │   │   ├── __init__.py
│   │   │   ├── auth.py              # 认证API
│   │   │   ├── accounts.py          # 账户API
│   │   │   ├── market.py            # 行情API
│   │   │   ├── trade.py             # 交易API
│   │   │   ├── positions.py         # 持仓API
│   │   │   ├── strategies.py        # 策略API
│   │   │   ├── risk.py              # 风控API
│   │   │   ├── ai.py                # AI API
│   │   │   ├── statistics.py        # 统计API
│   │   │   └── deps.py              # 依赖注入
│   │   ├── models/             # 数据模型
│   │   │   └── __init__.py
│   │   ├── schemas/            # Pydantic模型
│   │   │   └── __init__.py
│   │   ├── config.py           # 配置
│   │   ├── database.py         # 数据库
│   │   └── main.py             # 入口
│   ├── data/                   # 数据目录
│   ├── .env.example           # 环境变量示例
│   └── requirements.txt        # 依赖
│
├── frontend/                   # 前端
│   ├── src/
│   │   ├── api/               # API调用
│   │   │   ├── index.ts
│   │   │   ├── auth.ts
│   │   │   ├── account.ts
│   │   │   ├── market.ts
│   │   │   ├── trade.ts
│   │   │   ├── position.ts
│   │   │   └── strategy.ts
│   │   ├── components/        # 组件
│   │   │   ├── Header.tsx
│   │   │   └── Sidebar.tsx
│   │   ├── pages/            # 页面
│   │   │   ├── Login.tsx
│   │   │   ├── Register.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Market.tsx
│   │   │   ├── Trade.tsx
│   │   │   ├── Positions.tsx
│   │   │   ├── Strategies.tsx
│   │   │   ├── Statistics.tsx
│   │   │   └── AIAssistant.tsx
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── package.json
│   └── vite.config.ts
│
├── docs/                       # 文档
│   ├── architecture.md
│   ├── api.md
│   ├── database.md
│   ├── directory.md
│   ├── ENV.md
│   ├── COMMANDS.md
│   ├── RUNBOOK.md
│   └── CONTRIBUTING.md
│
├── hooks/                      # 钩子配置
│   ├── hooks.json
│   └── README.md
│
├── .gitignore
├── README.md
└── CLAUDE.md
```
