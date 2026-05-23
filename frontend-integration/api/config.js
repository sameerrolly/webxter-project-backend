/**
 * Central API configuration.
 * Copy this entire `api/` folder into your React project's `src/` directory.
 *
 * Backend: http://127.0.0.1:8000
 * Frontend: http://localhost:5173
 */

export const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

export const ENDPOINTS = {
  // -------------------------------------------------------------------------
  // Auth
  // -------------------------------------------------------------------------
  register:       `${API_BASE_URL}/auth/register/`,
  login:          `${API_BASE_URL}/auth/login/`,
  refresh:        `${API_BASE_URL}/auth/token/refresh/`,
  logout:         `${API_BASE_URL}/auth/logout/`,
  profile:        `${API_BASE_URL}/auth/profile/`,
  avatar:         `${API_BASE_URL}/auth/avatar/`,          // PATCH — upload/replace
  avatarRemove:   `${API_BASE_URL}/auth/avatar/remove/`,   // DELETE — remove avatar
  changePassword: `${API_BASE_URL}/auth/change-password/`,

  // -------------------------------------------------------------------------
  // Public project catalogue
  // GET  /api/v1/projects/      — all active/completed projects (React project page)
  // POST /api/v1/projects/      — create project (owner = logged-in user)
  // -------------------------------------------------------------------------
  projects:       `${API_BASE_URL}/projects/`,
  project:        (id) => `${API_BASE_URL}/projects/${id}/`,

  // -------------------------------------------------------------------------
  // Orders (user-scoped)
  // -------------------------------------------------------------------------
  orders:         `${API_BASE_URL}/orders/`,
  order:          (id) => `${API_BASE_URL}/orders/${id}/`,

  // -------------------------------------------------------------------------
  // Admin panel  (all require is_staff=True)
  // -------------------------------------------------------------------------
  adminDashboard:   `${API_BASE_URL}/admin/dashboard/`,
  adminSettings:    `${API_BASE_URL}/admin/settings/`,

  // Projects CRUD
  adminProjects:    `${API_BASE_URL}/admin/projects/`,
  adminProject:     (id) => `${API_BASE_URL}/admin/projects/${id}/`,

  // Project media gallery
  adminProjectMedia:       (projectId) => `${API_BASE_URL}/admin/projects/${projectId}/media/`,
  adminProjectMediaItem:   (projectId, mediaId) => `${API_BASE_URL}/admin/projects/${projectId}/media/${mediaId}/`,

  // Orders — list + status update + delete
  adminOrders:      `${API_BASE_URL}/admin/orders/`,
  adminOrder:       (id) => `${API_BASE_URL}/admin/orders/${id}/`,
  adminOrderStatus: (id) => `${API_BASE_URL}/admin/orders/${id}/status/`,

  // Coupons CRUD
  adminCoupons:     `${API_BASE_URL}/admin/coupons/`,
  adminCoupon:      (id) => `${API_BASE_URL}/admin/coupons/${id}/`,
};
