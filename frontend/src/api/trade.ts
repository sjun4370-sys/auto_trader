export interface OrderData {
  id: number;
  symbol: string;
  side: string;
  order_type: string;
  quantity: number;
  price?: number;
  filled_price?: number;
  status: string;
  order_id?: string;
  created_at: string;
  filled_at?: string;
}

export interface TradeRequest {
  symbol: string;
  side: string;
  order_type: string;
  quantity: number;
  price?: number;
}

export const tradeApi = {
  createOrder: (data: TradeRequest, accountId: number) =>
    api.post<OrderData>('/trade/order', data, { params: { account_id: accountId } }),
  getOrders: (symbol?: string, limit = 50) =>
    api.get<OrderData[]>('/trade/orders', { params: { symbol, limit } }),
  getOrder: (id: number) => api.get<OrderData>(`/trade/order/${id}`),
  cancelOrder: (id: number) => api.delete(`/trade/order/${id}`),
};
