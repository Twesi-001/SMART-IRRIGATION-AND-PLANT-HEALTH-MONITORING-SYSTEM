import axios from 'axios';
import { 
  DashboardSummary, 
  LoginResponse, 
  SensorReading, 
  SensorNode,
  Prediction,
  Alert
} from '../types';

// ✅ HARDCODED - forces use of proxy
const API_URL = '/api';
const API_KEY = import.meta.env.VITE_API_KEY || 'A0Wt_9n-2o7uL1MNuzsrUTCD2BioR_Fq3ZF1BnVK7gw';

console.log('API_URL:', API_URL); // Should show "/api"

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth endpoints
export const authService = {
  login: (username: string, password: string) =>
    api.post<LoginResponse>('/auth/login', { username, password }),
  register: (username: string, password: string, email?: string, role?: string) =>
    api.post('/auth/register', { username, password, email, role }),
};

// Dashboard endpoints
export const dashboardService = {
  getSummary: (nodeId: number = 1) =>
    api.get<DashboardSummary>(`/dashboard/summary?node_id=${nodeId}`),
  getAllNodes: () =>
    api.get<DashboardSummary[]>('/dashboard/nodes'),
};

// Readings endpoints
export const readingsService = {
  getReadings: (nodeId: number = 1, limit: number = 100) =>
    api.get<SensorReading[]>(`/readings/history?node_id=${nodeId}&limit=${limit}`),
  getLatest: (nodeId: number = 1) =>
    api.get<SensorReading>(`/readings/live?node_id=${nodeId}`),
  postReading: (data: { node_id: number; soil_moisture: number; temperature: number; humidity: number }) =>
    api.post('/readings', data, { headers: { 'X-API-Key': API_KEY } }),
  getStats: (nodeId: number = 1) =>
    api.get(`/readings/stats/${nodeId}`),
};

// Predictions endpoints
export const predictionsService = {
  getHistory: (nodeId: number = 1, limit: number = 100) =>
    api.get<Prediction[]>(`/predictions/history?node_id=${nodeId}&limit=${limit}`),
  getLatest: (nodeId: number = 1) =>
    api.get<Prediction>(`/predictions/latest?node_id=${nodeId}`),
  predict: (data: { node_id: number; soil_moisture: number; temperature: number; humidity: number }) =>
    api.post('/predictions/predict', data, { headers: { 'X-API-Key': API_KEY } }),
};

// Pump endpoints
export const pumpService = {
  getStatus: (nodeId: number = 1) =>
    api.get(`/pump/${nodeId}/status`),
  toggle: (nodeId: number = 1) =>
    api.post(`/pump/${nodeId}/toggle`),
  getHistory: (nodeId: number = 1, limit: number = 100) =>
    api.get(`/pump/history?node_id=${nodeId}&limit=${limit}`),
};

// Node endpoints
export const nodeService = {
  getAll: () =>
    api.get<SensorNode[]>('/nodes'),
  getById: (id: number) =>
    api.get<SensorNode>(`/nodes/${id}`),
  getStatus: (id: number) =>
    api.get(`/nodes/${id}/status`),
};

// Alert endpoints
export const alertService = {
  getAll: (nodeId: number = 1) =>
    api.get<Alert[]>(`/alerts?node_id=${nodeId}`),
  getUnresolved: (nodeId?: number) =>
    api.get<Alert[]>(`/alerts/unresolved${nodeId ? `?node_id=${nodeId}` : ''}`),
  resolve: (alertId: number) =>
    api.post(`/alerts/${alertId}/resolve`),
  create: (data: { node_id: number; alert_type: string; message: string; severity: string }) =>
    api.post('/alerts', data, { headers: { 'X-API-Key': API_KEY } }),
};

export default api;