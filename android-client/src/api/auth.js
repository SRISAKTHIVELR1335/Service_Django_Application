import apiClient from './client';
import { ENDPOINTS } from './config';

export const authApi = {
  login: async (email, password) => {
    try {
      const response = await apiClient.post(ENDPOINTS.AUTH.LOGIN, {
        email,
        password,
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Login failed');
    }
  },

  register: async (firstName, lastName, email, password) => {
    try {
      const response = await apiClient.post(ENDPOINTS.AUTH.REGISTER, {
        first_name: firstName,
        last_name: lastName,
        email,
        password,
      });
      return { success: true, message: response.data.message };
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Registration failed');
    }
  },

  getProfile: async () => {
    try {
      const response = await apiClient.get(ENDPOINTS.AUTH.ME);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to get profile');
    }
  },
};
