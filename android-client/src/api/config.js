export const API_BASE_URL = 'https://nirix-diagnostics.example.com';

export const API_TIMEOUT = 30000;

export const ENDPOINTS = {
  AUTH: {
    LOGIN: '/api/auth/login',
    REGISTER: '/api/auth/register',
    ME: '/api/auth/me',
  },
  VEHICLES: {
    LIST: '/api/vehicles',
    DETAIL: (id) => `/api/vehicles/${id}`,
  },
  TESTS: {
    LIST: '/api/tests',
    DETAIL: (id) => `/api/tests/${id}`,
  },
  BUNDLES: {
    LIST: '/api/testbundle',
    LATEST: (vehicleId) => `/api/testbundle/latest/${vehicleId}`,
    DOWNLOAD: (id) => `/api/testbundle/download/${id}`,
  },
  VERSIONS: {
    LATEST: '/api/versions/latest',
    CHECK: '/api/versions/check',
  },
  LOGS: {
    LIST: '/api/logs',
    UPLOAD: '/api/logs',
    STATS: '/api/logs/stats',
  },
  SETTINGS: {
    THEME: '/api/settings/theme',
    CAN_DRIVERS: '/api/settings/can-drivers',
  },
};

export const APP_VERSION = '1.0.0';
