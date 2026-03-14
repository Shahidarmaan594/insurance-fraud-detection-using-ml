/**
 * API client for Insurance Fraud Detection backend.
 */

import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

const client = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

// Retry logic for failed requests
client.interceptors.response.use(
  (res) => res,
  async (err) => {
    const config = err.config;
    if (!config || !config.retry) {
      config.retry = 0;
    }
    if (config.retry >= 2) {
      return Promise.reject(err);
    }
    config.retry += 1;
    await new Promise((r) => setTimeout(r, 1000));
    return client(config);
  }
);

export const api = {
  getClaims: (params = {}) =>
    client.get('/api/claims', { params }),

  getClaim: (claimId) =>
    client.get(`/api/claims/${claimId}`),

  createClaim: (data) =>
    client.post('/api/claims', data),

  updateClaimStatus: (claimId, status) =>
    client.put(`/api/claims/${claimId}/status`, { status }),

  predictFraud: (data) =>
    client.post('/api/predict-fraud', data),

  getStatistics: () =>
    client.get('/api/statistics'),

  getModelInfo: () =>
    client.get('/api/model-info'),

  exportClaimsCsv: () =>
    client.get('/api/export/claims/csv', { responseType: 'blob' }),
};

export default client;
