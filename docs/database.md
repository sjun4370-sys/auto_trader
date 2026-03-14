# 数据库设计

## 表结构

### users - 用户表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| username | VARCHAR(50) | 用户名，唯一 |
| email | VARCHAR(100) | 邮箱，唯一 |
| password_hash | VARCHAR(255) | 密码哈希 |
| is_active | BOOLEAN | 是否激活 |
| is_superuser | BOOLEAN | 是否管理员 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### exchange_accounts - 交易所账户表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| user_id | INTEGER | 外键，用户ID |
| exchange | VARCHAR(20) | 交易所标识 |
| account_name | VARCHAR(50) | 账户名称 |
| api_key | VARCHAR(255) | API Key |
| api_secret | VARCHAR(255) | API Secret |
| passphrase | VARCHAR(255) | 交易密码(OKX) |
| is_testnet | BOOLEAN | 是否测试网 |
| is_active | BOOLEAN | 是否激活 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### positions - 持仓表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| user_id | INTEGER | 外键，用户ID |
| account_id | INTEGER | 外键，账户ID |
| symbol | VARCHAR(20) | 交易对 |
| side | VARCHAR(10) | 方向(long/short) |
| quantity | FLOAT | 数量 |
| entry_price | FLOAT | 开仓价 |
| current_price | FLOAT | 当前价 |
| leverage | INTEGER | 杠杆倍数 |
| unrealized_pnl | FLOAT | 未实现盈亏 |
| realized_pnl | FLOAT | 已实现盈亏 |
| stop_loss | FLOAT | 止损价 |
| take_profit | FLOAT | 止盈价 |
| status | VARCHAR(20) | 状态(open/closed/liquidated) |
| opened_at | DATETIME | 开仓时间 |
| closed_at | DATETIME | 平仓时间 |

### orders - 订单表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| user_id | INTEGER | 外键，用户ID |
| account_id | INTEGER | 外键，账户ID |
| symbol | VARCHAR(20) | 交易对 |
| side | VARCHAR(10) | 方向(buy/sell) |
| order_type | VARCHAR(20) | 订单类型(market/limit) |
| quantity | FLOAT | 数量 |
| price | FLOAT | 价格(限价单) |
| filled_price | FLOAT | 成交价 |
| status | VARCHAR(20) | 状态 |
| order_id | VARCHAR(100) | 交易所订单ID |
| error_message | TEXT | 错误信息 |
| created_at | DATETIME | 创建时间 |
| filled_at | DATETIME | 成交时间 |

### strategies - 策略表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| user_id | INTEGER | 外键，用户ID |
| name | VARCHAR(100) | 策略名称 |
| strategy_type | VARCHAR(50) | 策略类型 |
| config | JSON | 策略配置 |
| is_active | BOOLEAN | 是否运行 |
| total_pnl | FLOAT | 总盈亏 |
| win_rate | FLOAT | 胜率 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### trade_logs - 交易日志表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| user_id | INTEGER | 外键，用户ID |
| symbol | VARCHAR(20) | 交易对 |
| action | VARCHAR(20) | 操作类型 |
| quantity | FLOAT | 数量 |
| price | FLOAT | 价格 |
| pnl | FLOAT | 盈亏 |
| note | TEXT | 备注 |
| created_at | DATETIME | 创建时间 |
