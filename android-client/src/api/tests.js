import apiClient from './client';
import { ENDPOINTS } from './config';

export const testsApi = {
  getTests: async (vehicleId = null, testType = null) => {
    try {
      const params = {};
      if (vehicleId) params.vehicle_id = vehicleId;
      if (testType) params.type = testType;
      
      const response = await apiClient.get(ENDPOINTS.TESTS.LIST, { params });
      return response.data.tests || [];
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to load tests');
    }
  },

  getTest: async (id) => {
    try {
      const response = await apiClient.get(ENDPOINTS.TESTS.DETAIL(id));
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to load test');
    }
  },
};
