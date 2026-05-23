/**
 * Admin service — wraps all admin panel API calls.
 * All endpoints require is_staff=True JWT token.
 *
 * Copy this file into your React project's src/api/ directory.
 */

import api from "./axiosInstance";
import { ENDPOINTS } from "./config";

// ---------------------------------------------------------------------------
// Dashboard
// ---------------------------------------------------------------------------
export const getDashboardStats = async () => {
  const response = await api.get(ENDPOINTS.adminDashboard);
  return response.data;
};

// ---------------------------------------------------------------------------
// Admin Settings (admin profile)
// ---------------------------------------------------------------------------
export const getAdminSettings = async () => {
  const response = await api.get(ENDPOINTS.adminSettings);
  return response.data;
};

/**
 * Update admin profile. Accepts name, email, avatar (File).
 * Automatically uses multipart/form-data when avatar is a File.
 * @param {{ name?, email?, avatar?: File }} data
 */
export const updateAdminSettings = async (data) => {
  const formData = new FormData();
  Object.entries(data).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      formData.append(key, value);
    }
  });
  const response = await api.patch(ENDPOINTS.adminSettings, formData);
  return response.data;
};

// ---------------------------------------------------------------------------
// Orders
// ---------------------------------------------------------------------------
/**
 * @param {{ status?: string, search?: string }} params
 */
export const getAdminOrders = async (params = {}) => {
  const response = await api.get(ENDPOINTS.adminOrders, { params });
  return response.data;
};

/**
 * Update order status.
 * @param {number} id
 * @param {string} status  — pending | confirmed | in_progress | delivered | cancelled
 */
export const updateOrderStatus = async (id, orderStatus) => {
  const response = await api.patch(ENDPOINTS.adminOrderStatus(id), {
    status: orderStatus,
  });
  return response.data;
};

export const deleteOrder = async (id) => {
  const response = await api.delete(ENDPOINTS.adminOrder(id));
  return response.data;
};

// ---------------------------------------------------------------------------
// Projects
// ---------------------------------------------------------------------------
/**
 * @param {{ status?: string, search?: string }} params
 */
export const getAdminProjects = async (params = {}) => {
  const response = await api.get(ENDPOINTS.adminProjects, { params });
  return response.data;
};

export const getAdminProject = async (id) => {
  const response = await api.get(ENDPOINTS.adminProject(id));
  return response.data;
};

/**
 * Create a project. Accepts multipart/form-data (thumbnail is a File).
 * @param {{ title, description?, status?, thumbnail?: File, owner?: number }} data
 */
export const createAdminProject = async (data) => {
  const formData = new FormData();
  Object.entries(data).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      formData.append(key, value);
    }
  });
  const response = await api.post(ENDPOINTS.adminProjects, formData);
  return response.data;
};

/**
 * Update a project. All fields optional.
 * @param {number} id
 * @param {{ title?, description?, status?, thumbnail?: File, owner?: number }} data
 */
export const updateAdminProject = async (id, data) => {
  const formData = new FormData();
  Object.entries(data).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      formData.append(key, value);
    }
  });
  const response = await api.patch(ENDPOINTS.adminProject(id), formData);
  return response.data;
};

export const deleteAdminProject = async (id) => {
  const response = await api.delete(ENDPOINTS.adminProject(id));
  return response.data;
};

// ---------------------------------------------------------------------------
// Coupons
// ---------------------------------------------------------------------------
/**
 * @param {{ is_active?: boolean, search?: string }} params
 */
export const getAdminCoupons = async (params = {}) => {
  const response = await api.get(ENDPOINTS.adminCoupons, { params });
  return response.data;
};

export const getAdminCoupon = async (id) => {
  const response = await api.get(ENDPOINTS.adminCoupon(id));
  return response.data;
};

/**
 * Create a coupon.
 * Required: code, discount_value, valid_from, valid_until
 * Optional: discount_type, description, min_order_amount, max_uses, is_active
 *
 * Dates must be ISO 8601 strings, e.g. "2026-06-01T00:00:00Z"
 *
 * @param {{
 *   code: string,
 *   discount_value: number,
 *   valid_from: string,
 *   valid_until: string,
 *   discount_type?: "percentage"|"fixed",
 *   description?: string,
 *   min_order_amount?: number,
 *   max_uses?: number|null,
 *   is_active?: boolean
 * }} data
 */
export const createAdminCoupon = async (data) => {
  const response = await api.post(ENDPOINTS.adminCoupons, data);
  return response.data;
};

/**
 * Update a coupon. All fields optional.
 * @param {number} id
 * @param {object} data
 */
export const updateAdminCoupon = async (id, data) => {
  const response = await api.patch(ENDPOINTS.adminCoupon(id), data);
  return response.data;
};

export const deleteAdminCoupon = async (id) => {
  const response = await api.delete(ENDPOINTS.adminCoupon(id));
  return response.data;
};
