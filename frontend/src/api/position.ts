import api from './index'

export interface PositionData {
  id: number;
  symbol: string;
  side: string;
  quantity: number;
  entry_price: number;
  current_price?: number;
  leverage: number;
  unrealized_pnl: number;
  stop_loss?: number;
  take_profit?: number;
  status: string;
  opened_at: string;
}

export const positionApi = {
  list: (status?: string) =>
    api.get<PositionData[]>('/positions', { params: { status } }),
  get: (id: number) => api.get<PositionData>(`/positions/${id}`),
  close: (id: number) => api.post(`/positions/close/${id}`),
};
