import apiClient from './client';
import { ENDPOINTS, APP_VERSION } from './config';

export const versionsApi = {
  getLatestVersions: async () => {
    try {
      const response = await apiClient.get(ENDPOINTS.VERSIONS.LATEST);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to get versions');
    }
  },

  checkForUpdates: async (platform = 'android') => {
    try {
      const response = await apiClient.post(ENDPOINTS.VERSIONS.CHECK, {
        platform,
        current_version: APP_VERSION,
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to check updates');
    }
  },
};
