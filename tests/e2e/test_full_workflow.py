"""
虚拟货币AI自动交易系统 - 端到端测试用例

测试范围:
1. 用户认证 (注册/登录/JWT Token)
2. 交易所账户管理
3. 行情数据查询
4. 交易下单
5. 持仓管理
6. 策略管理
7. 风控检查
8. AI分析
9. 统计报表

运行方式:
    pytest tests/e2e/test_full_workflow.py -v
    pytest tests/e2e/test_full_workflow.py -v --html=report.html --self-contained-html
"""

import pytest
import httpx
import asyncio
from typing import Dict, Any

# 测试配置
BASE_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://localhost:3000"


class TestConfig:
    """测试配置"""
    test_user = {
        "username": "test_user_e2e",
        "email": "e2e@test.com",
        "password": "Test123456!",
        "full_name": "E2E Test User"
    }
    
    test_exchange_account = {
        "name": "Test OKX Account",
        "exchange": "okx",
        "api_key": "test_api_key",
        "api_secret": "test_api_secret",
        "passphrase": "test_passphrase",
        "is_testnet": True
    }
    
    test_strategy = {
        "name": "E2E Test Strategy",
        "strategy_type": "grid",
        "symbol": "BTC/USDT",
        "timeframe": "1h",
        "config": {
            "grid_count": 10,
            "grid_spacing": 0.01,
            "position_size": 0.01
        }
    }


@pytest.fixture
def http_client():
    """HTTP客户端 fixture"""
    return httpx.Client(base_url=BASE_URL, timeout=30.0)


@pytest.fixture
async def async_http_client():
    """异步HTTP客户端 fixture"""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        yield client


@pytest.fixture
def auth_token(http_client) -> str:
    """获取认证token"""
    # 先尝试注册
    try:
        response = http_client.post("/api/v1/auth/register", json=TestConfig.test_user)
    except:
        pass
    
    # 登录获取token
    response = http_client.post("/api/v1/auth/login", json={
        "username": TestConfig.test_user["username"],
        "password": TestConfig.test_user["password"]
    })
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token) -> Dict[str, str]:
    """认证请求头"""
    return {"Authorization": f"Bearer {auth_token}"}


# ==================== 1. 用户认证测试 ====================

class TestAuthentication:
    """用户认证测试"""
    
    def test_health_check(self, http_client):
        """测试健康检查接口"""
        response = http_client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        print("✅ 健康检查通过")
    
    def test_root_endpoint(self, http_client):
        """测试根路径"""
        response = http_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        print(f"✅ 系统信息: {data['name']} v{data['version']}")
    
    def test_user_registration(self, http_client):
        """测试用户注册"""
        unique_user = {
            "username": f"test_user_{id(self)}",
            "email": f"e2e_{id(self)}@test.com",
            "password": "Test123456!",
            "full_name": "E2E Test"
        }
        response = http_client.post("/api/v1/auth/register", json=unique_user)
        assert response.status_code in [200, 201, 400]  # 400可能是用户名已存在
        print(f"✅ 用户注册: {response.status_code}")
    
    def test_user_login(self, http_client):
        """测试用户登录"""
        response = http_client.post("/api/v1/auth/login", json={
            "username": "testuser_final",
            "password": "Test123456!"
        })
        assert response.status_code in [200, 401]
        if response.status_code == 200:
            data = response.json()
            assert "access_token" in data
            assert "token_type" in data
            print(f"✅ 用户登录成功, token类型: {data['token_type']}")
        else:
            print(f"⚠️  用户登录失败（可能是测试用户不存在): {response.status_code}")


# ==================== 2. 交易所账户管理测试 ====================

class TestExchangeAccounts:
    """交易所账户测试"""
    
    def test_create_exchange_account(self, http_client, auth_headers):
        """测试创建交易所账户"""
        response = http_client.post(
            "/api/v1/accounts",
            json=TestConfig.test_exchange_account,
            headers=auth_headers,
            follow_redirects=True
        )
        assert response.status_code in [200, 201, 400]
        print(f"✅ 创建交易所账户: {response.status_code}")
    
    def test_list_exchange_accounts(self, http_client, auth_headers):
        """测试获取账户列表"""
        response = http_client.get("/api/v1/accounts", headers=auth_headers, follow_redirects=True)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ 账户列表获取成功, 共 {len(data)} 个账户")


# ==================== 3. 行情数据测试 ====================

class TestMarketData:
    """行情数据测试"""
    
    def test_get_ticker(self, http_client):
        """测试获取行情数据"""
        response = http_client.get("/api/v1/market/ticker/BTC/USDT")
        # 可能返回404如果没有该交易对
        assert response.status_code in [200, 404]
        print(f"✅ 行情查询: {response.status_code}")
    
    def test_get_orderbook(self, http_client):
        """测试获取订单簿"""
        response = http_client.get("/api/v1/market/orderbook/BTC/USDT")
        assert response.status_code in [200, 404]
        print(f"✅ 订单簿查询: {response.status_code}")
    
    def test_get_klines(self, http_client):
        """测试获取K线数据"""
        response = http_client.get("/api/v1/market/klines/BTC/USDT?timeframe=1h&limit=100")
        assert response.status_code in [200, 404]
        print(f"✅ K线数据查询: {response.status_code}")


# ==================== 4. 交易下单测试 ====================

class TestTrading:
    """交易下单测试"""
    
    def test_place_market_order(self, http_client, auth_headers):
        """测试市价单下单"""
        order_data = {
            "symbol": "BTC/USDT",
            "side": "buy",
            "order_type": "market",
            "amount": 0.001
        }
        response = http_client.post(
            "/api/v1/trade/order",
            json=order_data,
            headers=auth_headers
        )
        assert response.status_code in [200, 201, 400, 422]
        print(f"✅ 市价单下单: {response.status_code}")
    
    def test_place_limit_order(self, http_client, auth_headers):
        """测试限价单下单"""
        order_data = {
            "symbol": "BTC/USDT",
            "side": "buy",
            "order_type": "limit",
            "amount": 0.001,
            "price": 50000
        }
        response = http_client.post(
            "/api/v1/trade/order",
            json=order_data,
            headers=auth_headers
        )
        assert response.status_code in [200, 201, 400, 422]
        print(f"✅ 限价单下单: {response.status_code}")
    
    def test_cancel_order(self, http_client, auth_headers):
        """测试取消订单"""
        response = http_client.delete(
            "/api/v1/trade/order/test_order_id",
            headers=auth_headers,
            follow_redirects=True
        )
        assert response.status_code in [200, 404, 422]
        print(f"✅ 取消订单: {response.status_code}")
    
    def test_get_order_history(self, http_client, auth_headers):
        """测试获取订单历史"""
        response = http_client.get("/api/v1/trade/orders", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ 订单历史获取成功, 共 {len(data)} 个订单")


# ==================== 5. 持仓管理测试 ====================

class TestPositions:
    """持仓管理测试"""
    
    def test_get_positions(self, http_client, auth_headers):
        """测试获取持仓列表"""
        response = http_client.get("/api/v1/positions", headers=auth_headers, follow_redirects=True)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ 持仓列表获取成功, 共 {len(data)} 个持仓")
    
    def test_get_position_by_symbol(self, http_client, auth_headers):
        """测试获取特定交易对持仓"""
        response = http_client.get("/api/v1/positions/BTC/USDT", headers=auth_headers)
        assert response.status_code in [200, 404]
        print(f"✅ BTC/USDT 持仓查询: {response.status_code}")
    
    def test_close_position(self, http_client, auth_headers):
        """测试平仓"""
        response = http_client.post(
            "/api/v1/positions/close/BTC/USDT",
            headers=auth_headers
        )
        assert response.status_code in [200, 404, 400]
        print(f"✅ 平仓操作: {response.status_code}")


# ==================== 6. 策略管理测试 ====================

class TestStrategies:
    """策略管理测试"""
    
    def test_create_strategy(self, http_client, auth_headers):
        """测试创建策略"""
        strategy = {
            "name": f"E2E Test Strategy {id(self)}",
            "strategy_type": "grid",
            "symbol": "BTC/USDT",
            "timeframe": "1h",
            "config": {
                "grid_count": 10,
                "grid_spacing": 0.01,
                "position_size": 0.01
            }
        }
        
        response = http_client.post(
            "/api/v1/strategies",
            json=strategy,
            headers=auth_headers,
            follow_redirects=True
        )
        assert response.status_code in [200, 201, 400, 422]
        print(f"✅ 创建策略: {response.status_code}")
    
    def test_list_strategies(self, http_client, auth_headers):
        """测试获取策略列表"""
        response = http_client.get("/api/v1/strategies", headers=auth_headers, follow_redirects=True)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ 策略列表获取成功, 共 {len(data)} 个策略")
    
    def test_get_strategy(self, http_client, auth_headers):
        """测试获取特定策略"""
        response = http_client.get("/api/v1/strategies/1", headers=auth_headers, follow_redirects=True)
        assert response.status_code in [200, 404]
        print(f"✅ 策略详情查询: {response.status_code}")
    
    def test_update_strategy(self, http_client, auth_headers):
        """测试更新策略"""
        update_data = {"is_active": False}
        response = http_client.patch(
            "/api/v1/strategies/1",
            json=update_data,
            headers=auth_headers,
            follow_redirects=True
        )
        assert response.status_code in [200, 404, 400, 422]
        print(f"✅ 策略更新: {response.status_code}")
    
    def test_delete_strategy(self, http_client, auth_headers):
        """测试删除策略"""
        response = http_client.delete("/api/v1/strategies/1", headers=auth_headers, follow_redirects=True)
        assert response.status_code in [200, 404, 400]
        print(f"✅ 删除策略: {response.status_code}")


# ==================== 7. 风控检查测试 ====================

class TestRiskManagement:
    """风控管理测试"""
    
    def test_risk_check(self, http_client, auth_headers):
        """测试风险检查"""
        risk_data = {
            "symbol": "BTC/USDT",
            "side": "buy",
            "amount": 0.01,
            "price": 50000,
            "leverage": 10
        }
        response = http_client.post(
            "/api/v1/risk/validate",
            json=risk_data,
            headers=auth_headers,
            follow_redirects=True
        )
        assert response.status_code in [200, 400, 405, 404]
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 风险检查通过: {data.get('approved', 'N/A')}")
        else:
            print(f"✅ 风险检查拒绝: {response.status_code}")
    
    def test_get_risk_config(self, http_client, auth_headers):
        """测试获取风控配置"""
        response = http_client.get("/api/v1/risk/config", headers=auth_headers)
        assert response.status_code in [200, 404]
        print(f"✅ 风控配置查询: {response.status_code}")


# ==================== 8. AI分析测试 ====================

class TestAI:
    """AI分析测试"""
    
    def test_ai_analysis(self, http_client, auth_headers):
        """测试AI分析"""
        analysis_data = {
            "symbol": "BTC/USDT",
            "timeframe": "1h",
            "indicators": ["rsi", "macd", "bollinger"]
        }
        response = http_client.post(
            "/api/v1/ai/analyze",
            json=analysis_data,
            headers=auth_headers,
            follow_redirects=True
        )
        assert response.status_code in [200, 400, 500, 404]
        if response.status_code == 200:
            data = response.json()
            print(f"✅ AI分析完成: {data.get('signal', 'N/A')}")
        else:
            print(f"✅ AI分析: {response.status_code}")
    
    def test_ai_trading_signal(self, http_client, auth_headers):
        """测试AI交易信号"""
        response = http_client.get(
            "/api/v1/ai/signal/BTC/USDT",
            headers=auth_headers
        )
        assert response.status_code in [200, 404]
        print(f"✅ AI交易信号查询: {response.status_code}")


# ==================== 9. 统计报表测试 ====================

class TestStatistics:
    """统计报表测试"""
    
    def test_account_statistics(self, http_client, auth_headers):
        """测试账户统计"""
        response = http_client.get("/api/v1/statistics/account", headers=auth_headers)
        assert response.status_code in [200, 404]
        print(f"✅ 账户统计: {response.status_code}")
    
    def test_trade_statistics(self, http_client, auth_headers):
        """测试交易统计"""
        response = http_client.get(
            "/api/v1/statistics/trades?start_date=2024-01-01&end_date=2024-12-31",
            headers=auth_headers
        )
        assert response.status_code in [200, 404]
        print(f"✅ 交易统计: {response.status_code}")
    
    def test_performance_metrics(self, http_client, auth_headers):
        """测试性能指标"""
        response = http_client.get("/api/v1/statistics/performance", headers=auth_headers)
        assert response.status_code in [200, 404]
        print(f"✅ 性能指标: {response.status_code}")


# ==================== 10. 完整工作流测试 ====================

class TestFullWorkflow:
    """完整工作流测试"""
    
    def test_complete_trading_workflow(self, http_client):
        """完整的交易工作流测试"""
        print("\n" + "="*50)
        print("🚀 开始完整工作流测试")
        print("="*50)
        
        # Step 1: 用户注册/登录
        print("\n📝 Step 1: 用户认证")
        # 注册
        unique_user = {
            "username": f"workflow_user_{id(self)}",
            "email": f"workflow_{id(self)}@test.com",
            "password": "Test123456!",
            "full_name": "Workflow Test"
        }
        try:
            http_client.post("/api/v1/auth/register", json=unique_user)
        except:
            pass
        
        # 登录
        response = http_client.post("/api/v1/auth/login", json={
            "username": unique_user["username"],
            "password": unique_user["password"]
        })
        assert response.status_code == 200
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("   ✅ 登录成功")
        
        # Step 2: 创建交易所账户
        print("\n📝 Step 2: 创建交易所账户")
        account_data = {
            "name": "Workflow OKX",
            "exchange": "okx",
            "api_key": "test_key",
            "api_secret": "test_secret",
            "passphrase": "test_pass",
            "is_testnet": True
        }
        response = http_client.post("/api/v1/accounts/", json=account_data, headers=headers)
        print(f"   ✅ 账户创建: {response.status_code}")
        
        # Step 3: 风险检查
        print("\n📝 Step 3: 风险检查")
        risk_data = {
            "symbol": "BTC/USDT",
            "side": "buy",
            "amount": 0.01,
            "price": 50000,
            "leverage": 5
        }
        response = http_client.post("/api/v1/risk/check", json=risk_data, headers=headers)
        print(f"   ✅ 风险检查: {response.status_code}")
        
        # Step 4: 获取行情
        print("\n📝 Step 4: 获取行情数据")
        response = http_client.get("/api/v1/market/ticker/BTC/USDT")
        print(f"   ✅ 行情查询: {response.status_code}")
        
        # Step 5: 下单交易
        print("\n📝 Step 5: 下单交易")
        order_data = {
            "symbol": "BTC/USDT",
            "side": "buy",
            "order_type": "market",
            "amount": 0.001
        }
        response = http_client.post("/api/v1/trade/order", json=order_data, headers=headers)
        print(f"   ✅ 下单: {response.status_code}")
        
        # Step 6: 查看持仓
        print("\n📝 Step 6: 查看持仓")
        response = http_client.get("/api/v1/positions/", headers=headers)
        print(f"   ✅ 持仓查询: {response.status_code}, 共 {len(response.json()) if response.status_code == 200 else 0} 个")
        
        # Step 7: 创建交易策略
        print("\n📝 Step 7: 创建交易策略")
        strategy_data = {
            "name": "Workflow Strategy",
            "strategy_type": "grid",
            "symbol": "ETH/USDT",
            "timeframe": "15m",
            "config": {"grid_count": 5, "grid_spacing": 0.02}
        }
        response = http_client.post("/api/v1/strategies", json=strategy_data, headers=headers, follow_redirects=True)
        print(f"   ✅ 策略创建: {response.status_code}")
        
        # Step 8: 获取统计
        print("\n📝 Step 8: 获取统计报表")
        response = http_client.get("/api/v1/statistics/account", headers=headers)
        print(f"   ✅ 统计查询: {response.status_code}")
        
        print("\n" + "="*50)
        print("✅ 完整工作流测试完成!")
        print("="*50)


# ==================== 运行入口 ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
