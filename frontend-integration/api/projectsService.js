/**
 * Projects service — public catalogue + user project CRUD.
 * Uses FormData for create/update so thumbnail file uploads work correctly.
 */

import api from "./axiosInstance";
import { ENDPOINTS } from "./config";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Build a FormData from a plain object.
 * Skips undefined/null values so we don't accidentally clear fields.
 * File objects (thumbnail) are appended as-is.
 */
const toFormData = (data) => {
  const formData = new FormData();
  Object.entries(data).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      formData.append(key, value);
    }
  });
  return formData;
};

// ---------------------------------------------------------------------------
// Public catalogue (no auth required)
// ---------------------------------------------------------------------------

export const getProjects = async () => {
  const response = await api.get(ENDPOINTS.projects);
  return response.data;
};

export const getProject = async (id) => {
  const response = await api.get(ENDPOINTS.project(id));
  return response.data;
};

// ---------------------------------------------------------------------------
// Authenticated CRUD
// ---------------------------------------------------------------------------

/**
 * Create a project.
 * @param {{
 *   title: string,
 *   description?: string,
 *   status?: string,
 *   price?: number,
 *   thumbnail?: File
 * }} data
 */
export const createProject = async (data) => {
  // Use FormData so thumbnail (File) is sent as multipart/form-data
  const response = await api.post(ENDPOINTS.projects, toFormData(data));
  return response.data;
};

/**
 * Update a project (partial — only send changed fields).
 * @param {number} id
 * @param {{
 *   title?: string,
 *   description?: string,
 *   status?: string,
 *   price?: number,
 *   thumbnail?: File
 * }} data
 */
export const updateProject = async (id, data) => {
  const response = await api.patch(ENDPOINTS.project(id), toFormData(data));
  return response.data;
};

export const deleteProject = async (id) => {
  await api.delete(ENDPOINTS.project(id));
};
