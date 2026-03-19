import api from './index'

export interface StrategyData {
  id: number;
  name: string;
  strategy_type: string;
  config: Record<string, any>;
  is_active: boolean;
  total_pnl: number;
  win_rate: number;
  created_at: string;
}

export interface StrategyCreate {
  name: string;
  strategy_type: string;
  config: Record<string, any>;
}

export const strategyApi = {
  list: (config?: { signal?: AbortSignal }) => api.get<StrategyData[]>('/strategies', config),
  get: (id: number) => api.get<StrategyData>(`/strategies/${id}`),
  create: (data: StrategyCreate) => api.post<StrategyData>('/strategies', data),
  update: (id: number, data: StrategyCreate) =>
    api.patch<StrategyData>(`/strategies/${id}`, data),
  delete: (id: number) => api.delete(`/strategies/${id}`),
  start: (id: number) => api.post(`/strategies/${id}/start`),
  stop: (id: number) => api.post(`/strategies/${id}/stop`),
};
