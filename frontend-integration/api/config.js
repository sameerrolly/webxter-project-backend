/**
 * Central API configuration.
 * Copy this entire `api/` folder into your React project's `src/` directory.
 *
 * Backend: http://127.0.0.1:8000
 * Frontend: http://localhost:5173
 */

export const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

export const ENDPOINTS = {
  // Auth
  register:       `${API_BASE_URL}/auth/register/`,
  login:          `${API_BASE_URL}/auth/login/`,
  refresh:        `${API_BASE_URL}/auth/token/refresh/`,
  logout:         `${API_BASE_URL}/auth/logout/`,
  profile:        `${API_BASE_URL}/auth/profile/`,
  // Avatar upload uses the same profile PATCH endpoint (multipart/form-data)
  avatar:         `${API_BASE_URL}/auth/profile/`,
  changePassword: `${API_BASE_URL}/auth/change-password/`,

  // Projects
  projects:       `${API_BASE_URL}/projects/`,
  project:        (id) => `${API_BASE_URL}/projects/${id}/`,

  // Orders
  orders:         `${API_BASE_URL}/orders/`,
  order:          (id) => `${API_BASE_URL}/orders/${id}/`,
};
