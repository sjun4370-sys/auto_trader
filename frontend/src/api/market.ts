import api from './index'

export interface Ticker {
  symbol: string;
  last: number;
  high: number;
  low: number;
  volume: number;
  change: number;
  change_percent: number;
}

export interface KLine {
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export const marketApi = {
  getTickers: (config?: { signal?: AbortSignal; symbols?: string }) =>
    api.get('/market/tickers', { params: { symbols: config?.symbols }, ...config }),
  getTicker: (symbol: string) => api.get<Ticker>(`/market/ticker/${symbol}`),
  getKline: (symbol: string, timeframe = '1h', limit = 100) =>
    api.get<KLine[]>(`/market/kline/${symbol}`, { params: { timeframe, limit } }),
};
