/**
 * Orders service — CRUD for the authenticated user's orders.
 */

import api from "./axiosInstance";
import { ENDPOINTS } from "./config";

export const getOrders = async () => {
  const response = await api.get(ENDPOINTS.orders);
  return response.data;
};

export const getOrder = async (id) => {
  const response = await api.get(ENDPOINTS.order(id));
  return response.data;
};

export const createOrder = async (data) => {
  const response = await api.post(ENDPOINTS.orders, data);
  return response.data;
};

export const updateOrder = async (id, data) => {
  const response = await api.patch(ENDPOINTS.order(id), data);
  return response.data;
};

export const deleteOrder = async (id) => {
  await api.delete(ENDPOINTS.order(id));
};
