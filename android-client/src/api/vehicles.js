import apiClient from './client';
import { ENDPOINTS } from './config';

export const vehiclesApi = {
  getVehicles: async (category = null) => {
    try {
      const params = category ? { category } : {};
      const response = await apiClient.get(ENDPOINTS.VEHICLES.LIST, { params });
      return response.data.vehicles || [];
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to load vehicles');
    }
  },

  getVehicle: async (id) => {
    try {
      const response = await apiClient.get(ENDPOINTS.VEHICLES.DETAIL(id));
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to load vehicle');
    }
  },

  getCategories: async () => {
    try {
      const response = await apiClient.get(`${ENDPOINTS.VEHICLES.LIST}/categories`);
      return response.data.categories || [];
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to load categories');
    }
  },
};
