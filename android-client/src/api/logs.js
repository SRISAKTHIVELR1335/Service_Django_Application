import apiClient from './client';
import { ENDPOINTS, APP_VERSION } from './config';

export const logsApi = {
  getLogs: async (page = 1, perPage = 20, filters = {}) => {
    try {
      const params = { page, per_page: perPage, ...filters };
      const response = await apiClient.get(ENDPOINTS.LOGS.LIST, { params });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to load logs');
    }
  },

  uploadLog: async (logData) => {
    try {
      const payload = {
        ...logData,
        client_version: APP_VERSION,
        executed_at: new Date().toISOString(),
      };
      const response = await apiClient.post(ENDPOINTS.LOGS.UPLOAD, payload);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to upload log');
    }
  },

  getStats: async () => {
    try {
      const response = await apiClient.get(ENDPOINTS.LOGS.STATS);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to get stats');
    }
  },
};
