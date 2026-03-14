# 虚拟货币AI自动交易系统

基于 Python FastAPI + React 的虚拟货币自动交易系统

## 技术栈

- 后端: Python FastAPI
- 前端: React + TypeScript + Ant Design
- 数据库: SQLite
- 交易所SDK: CCXT

## 快速开始

### 后端启动

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # 配置环境变量
uvicorn app.main:app --reload
```

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

## API 文档

启动后访问 http://localhost:8000/docs 查看 Swagger 文档
