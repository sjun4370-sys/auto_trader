"""行情API"""
import ccxt
from typing import List, Optional
from fastapi import APIRouter, Query
from app.config import settings

router = APIRouter(prefix="/market", tags=["行情"])


def get_exchange(exchange_id: str = None):
    """获取交易所实例"""
    exchange_id = exchange_id or settings.DEFAULT_EXCHANGE
    exchange_class = getattr(ccxt, exchange_id)
    return exchange_class({
        'enableRateLimit': True,
    })


@router.get("/tickers")
async def get_tickers(
    symbols: Optional[str] = Query(None, description="逗号分隔的币种列表")
):
    """获取多个币种行情"""
    exchange = get_exchange()

    if symbols:
        symbol_list = [s.strip() for s in symbols.split(',')]
    else:
        # 默认主流币种
        symbol_list = [
            'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT',
            'XRP/USDT', 'ADA/USDT', 'AVAX/USDT', 'DOGE/USDT'
        ]

    tickers = {}
    for symbol in symbol_list:
        try:
            ticker = exchange.fetch_ticker(symbol)
            tickers[symbol] = {
                'symbol': symbol,
                'last': ticker['last'],
                'high': ticker['high'],
                'low': ticker['low'],
                'volume': ticker['baseVolume'],
                'change': ticker.get('change', 0),
                'change_percent': ticker.get('percentage', 0),
            }
        except Exception as e:
            tickers[symbol] = {'error': str(e)}

    return tickers


@router.get("/ticker/{symbol}")
async def get_ticker(symbol: str):
    """获取单个币种行情"""
    exchange = get_exchange()

    try:
        ticker = exchange.fetch_ticker(symbol)
        return {
            'symbol': symbol,
            'last': ticker['last'],
            'high': ticker['high'],
            'low': ticker['low'],
            'volume': ticker['baseVolume'],
            'change': ticker.get('change', 0),
            'change_percent': ticker.get('percentage', 0),
            'bid': ticker['bid'],
            'ask': ticker['ask'],
            'timestamp': ticker['timestamp'],
        }
    except Exception as e:
        return {'error': str(e)}


@router.get("/kline/{symbol}")
async def get_kline(
    symbol: str,
    timeframe: str = Query("1h", description="时间框架: 1m, 5m, 15m, 1h, 4h, 1d"),
    limit: int = Query(100, le=1000)
):
    """获取K线数据"""
    exchange = get_exchange()

    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        return [
            {
                'timestamp': k[0],
                'open': k[1],
                'high': k[2],
                'low': k[3],
                'close': k[4],
                'volume': k[5],
            }
            for k in ohlcv
        ]
    except Exception as e:
        return {'error': str(e)}


@router.get("/orderbook/{symbol}")
async def get_orderbook(symbol: str, limit: int = Query(20, le=100)):
    """获取订单簿"""
    exchange = get_exchange()

    try:
        orderbook = exchange.fetch_order_book(symbol, limit)
        return orderbook
    except Exception as e:
        return {'error': str(e)}
