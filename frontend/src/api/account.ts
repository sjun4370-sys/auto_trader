import api from './index'

export interface AccountData {
  id: number;
  exchange: string;
  account_name?: string;
  api_key?: string;
  api_secret?: string;
  passphrase?: string;
  is_testnet: boolean;
  is_active: boolean;
  has_api_credentials: boolean;
  created_at: string;
}

export const accountApi = {
  list: (config?: { signal?: AbortSignal }) => api.get<AccountData[]>('/accounts', config),
  get: (id: number) => api.get<AccountData>(`/accounts/${id}`),
  create: (data: Partial<AccountData>) => api.post('/accounts', data),
  update: (id: number, data: Partial<AccountData>) => api.patch(`/accounts/${id}`, data),
  delete: (id: number) => api.delete(`/accounts/${id}`),
};
