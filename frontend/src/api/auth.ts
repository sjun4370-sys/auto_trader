import api from './index'

export interface LoginData {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export const authApi = {
  login: (data: LoginData) => api.post<AuthResponse>('/auth/login', data),
  register: (data: RegisterData) => api.post('/auth/register', data),
  getMe: () => api.get('/auth/me'),
};
