# 策略运行监控实现计划

## 功能概述
实现策略的实时运行监控，包括：
1. 策略调度引擎 - 使用 APScheduler 执行策略
2. 策略状态管理 - 启动/停止/暂停
3. 策略运行日志 - 记录执行过程
4. 实时监控接口 - 持仓/盈亏/信号

## 实现任务

### 1. 策略执行引擎 (app/engine/)
- strategy_engine.py - 策略执行器基类
- grid_engine.py - 网格策略执行器

### 2. 调度器 (app/scheduler/)
- scheduler.py - APScheduler 调度器管理

### 3. 数据模型 (app/models/)
- 添加 StrategyRun 记录策略运行状态

### 4. API 扩展 (app/api/)
- strategy_runs.py - 策略运行记录 API
- strategy_stats.py - 策略实时统计

### 5. WebSocket (app/websocket/)
- manager.py - 实时推送策略状态

## 进度
- [ ] 策略执行引擎
- [ ] 调度器
- [ ] 数据模型
- [ ] API 接口
- [ ] WebSocket 实时推送
