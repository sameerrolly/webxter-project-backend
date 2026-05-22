/**
 * Auth service — wraps all authentication API calls.
 */

import api from "./axiosInstance";
import { ENDPOINTS } from "./config";
import { setTokens, clearTokens } from "./axiosInstance";
import axios from "axios";

// ---------------------------------------------------------------------------
// Register
// ---------------------------------------------------------------------------
/**
 * @param {{ email, first_name, last_name, password, password2 }} data
 * @returns {{ message, user, tokens: { access, refresh } }}
 */
export const register = async (data) => {
  const response = await axios.post(ENDPOINTS.register, data);
  const { user, tokens } = response.data;
  setTokens(tokens);
  localStorage.setItem("user", JSON.stringify(user));
  return response.data;
};

// ---------------------------------------------------------------------------
// Login
// ---------------------------------------------------------------------------
/**
 * @param {{ email, password }} credentials
 * @returns {{ access, refresh, user }}
 */
export const login = async ({ email, password }) => {
  const response = await axios.post(ENDPOINTS.login, { email, password });
  const { access, refresh, user } = response.data;
  setTokens({ access, refresh });
  localStorage.setItem("user", JSON.stringify(user));
  return response.data;
};

// ---------------------------------------------------------------------------
// Logout
// ---------------------------------------------------------------------------
export const logout = async () => {
  try {
    const refresh = localStorage.getItem("refresh_token");
    if (refresh) {
      await api.post(ENDPOINTS.logout, { refresh });
    }
  } finally {
    clearTokens();
  }
};

// ---------------------------------------------------------------------------
// Get profile
// ---------------------------------------------------------------------------
export const getProfile = async () => {
  const response = await api.get(ENDPOINTS.profile);
  // Keep localStorage in sync with the latest server data
  localStorage.setItem("user", JSON.stringify(response.data));
  return response.data;
};

// ---------------------------------------------------------------------------
// Update profile
// ---------------------------------------------------------------------------
/**
 * Sends profile data as multipart/form-data so file uploads (avatar) work.
 * Pass a plain object — this function handles FormData conversion automatically.
 *
 * @param {{ first_name?, last_name?, bio?, avatar?: File }} data
 * @returns {Promise<UserProfile>} Full updated profile with absolute avatar URL
 */
export const updateProfile = async (data) => {
  const formData = new FormData();

  Object.entries(data).forEach(([key, value]) => {
    // Skip undefined/null values so we don't accidentally clear fields
    if (value !== undefined && value !== null) {
      formData.append(key, value);
    }
  });

  // Do NOT set Content-Type manually — axios must set it automatically
  // so the multipart boundary is included (e.g. multipart/form-data; boundary=----xyz)
  const response = await api.patch(ENDPOINTS.profile, formData);

  // Persist the full updated profile (includes absolute avatar URL)
  localStorage.setItem("user", JSON.stringify(response.data));
  return response.data;
};

// ---------------------------------------------------------------------------
// Upload avatar (dedicated helper — uses the same profile PATCH endpoint)
// ---------------------------------------------------------------------------
/**
 * Upload only the avatar image.
 *
 * @param {File} file  — the image File object from an <input type="file">
 * @returns {Promise<UserProfile>} Full updated profile with absolute avatar URL
 */
export const uploadAvatar = async (file) => {
  const formData = new FormData();
  formData.append("avatar", file);

  // Do NOT set Content-Type — axios sets it with the correct boundary
  const response = await api.patch(ENDPOINTS.avatar, formData);

  localStorage.setItem("user", JSON.stringify(response.data));
  return response.data;
};

// ---------------------------------------------------------------------------
// Change password
// ---------------------------------------------------------------------------
/**
 * @param {{ old_password, new_password, new_password2 }} data
 */
export const changePassword = async (data) => {
  const response = await api.post(ENDPOINTS.changePassword, data);
  return response.data;
};

// ---------------------------------------------------------------------------
// Get current user from localStorage (no network call)
// ---------------------------------------------------------------------------
export const getCurrentUser = () => {
  const user = localStorage.getItem("user");
  return user ? JSON.parse(user) : null;
};

// ---------------------------------------------------------------------------
// Check if user is authenticated
// ---------------------------------------------------------------------------
export const isAuthenticated = () => {
  return !!localStorage.getItem("access_token");
};
