/**
 * Projects service — CRUD for the authenticated user's projects.
 */

import api from "./axiosInstance";
import { ENDPOINTS } from "./config";

export const getProjects = async () => {
  const response = await api.get(ENDPOINTS.projects);
  return response.data;
};

export const getProject = async (id) => {
  const response = await api.get(ENDPOINTS.project(id));
  return response.data;
};

export const createProject = async (data) => {
  const response = await api.post(ENDPOINTS.projects, data);
  return response.data;
};

export const updateProject = async (id, data) => {
  const response = await api.patch(ENDPOINTS.project(id), data);
  return response.data;
};

export const deleteProject = async (id) => {
  await api.delete(ENDPOINTS.project(id));
};
