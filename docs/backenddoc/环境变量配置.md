# 环境变量配置

## 后端配置

| 变量名 | 必需 | 说明 | 默认值 |
|--------|------|------|--------|
| `APP_NAME` | 否 | 应用名称 | OKX Auto Trader |
| `APP_VERSION` | 否 | 版本号 | 1.0.0 |
| `DEBUG` | 否 | 调试模式 | true |
| `DATABASE_URL` | 否 | 数据库连接 | sqlite+aiosqlite:///./data/okx_trader.db |
| `SECRET_KEY` | 是 | JWT 签名密钥 | your-secret-key-change-in-production |
| `ALGORITHM` | 否 | JWT 算法 | HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 否 | Token 过期时间(分钟) | 1440 (24小时) |
| `DEFAULT_EXCHANGE` | 否 | 默认交易所 | okx |
| `OKX_API_BASE_URL` | 否 | OKX API 地址 | https://www.okx.com |
| `MAX_POSITION_PERCENT` | 否 | 单币种最大仓位占比 | 10.0 |
| `DEFAULT_LEVERAGE` | 否 | 默认杠杆 | 3 |
| `STOP_LOSS_PERCENT` | 否 | 止损比例 | 5.0 |
| `MAX_DAILY_LOSS` | 否 | 日内最大亏损 | 15.0 |
| `CIRCUIT_BREAKER_COUNT` | 否 | 熔断连续止损次数 | 3 |
| `OPENAI_API_KEY` | 否 | OpenAI API 密钥 | (空) |
| `OPENAI_MODEL` | 否 | OpenAI 模型 | gpt-4 |

## 配置示例

复制 `backend/.env.example` 为 `backend/.env` 并修改：

```bash
cp backend/.env.example backend/.env
```

## 安全注意事项

- **生产环境必须修改 `SECRET_KEY`**
- 不要提交 `.env` 文件到版本控制
- API 密钥等敏感信息只存在服务端
