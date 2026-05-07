import api from './api';

export const login = async (credentials) => {
  const response = await api.post('/auth/login/', credentials);
  return response.data;
};

export const logout = async () => {
  const response = await api.post('/auth/logout/');
  return response.data;
};

export const refreshToken = async (refreshToken) => {
  const response = await api.post('/auth/token/refresh/', {
    refresh: refreshToken
  });
  return response.data;
};

export const getCurrentUser = async () => {
  const response = await api.get('/auth/me/');
  return response.data;
};
