// apiService.js
import axios from 'axios';

// Create an axios instance with base configuration
const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000',
  timeout: 120000, // 120 seconds timeout (increased for AI processing)
  headers: {
    'Content-Type': 'application/json',
  }
});

// Request interceptor to add auth token if available
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle global errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access - maybe redirect to login
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API endpoints
const apiService = {
  // Get housing recommendations based on user input
  getHousingRecommendations: async (inputData, onProgress) => {
    const BASE = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000';

    // Step 1: submit
    const { data: task } = await apiClient.post('/api/housing-recommendations', inputData);
    const taskId = task.task_id;

    // Step 2: SSE (primary)
    const sseResult = await new Promise((resolve, reject) => {
      let settled = false;
      const es = new EventSource(`${BASE}/api/tasks/${taskId}/stream`);

      const finish = (fn, val) => {
        if (settled) return;
        settled = true;
        es.close();
        fn(val);
      };

      es.onmessage = (e) => {
        try {
          const data = JSON.parse(e.data);
          if (data.error) return finish(reject, new Error(data.error));
          if (onProgress) onProgress(data.current_step, data.progress);
          if (data.status === 'completed') finish(resolve, data.result);
          if (data.status === 'failed') finish(reject, new Error(data.error || 'Task failed'));
        } catch { finish(reject, new Error('SSE parse error')); }
      };

      es.onerror = () => finish(reject, new Error('SSE connection failed'));

      // Safety timeout — fall through to polling if SSE stalls for 90s
      setTimeout(() => finish(reject, new Error('SSE timeout')), 90000);
    }).catch(() => null); // null signals fallback

    if (sseResult) return sseResult;

    // Step 3: polling fallback
    while (true) {
      await new Promise(r => setTimeout(r, 1500));
      const { data } = await apiClient.get(`/api/tasks/${taskId}/status`);
      if (onProgress) onProgress(data.current_step, data.progress);
      if (data.status === 'completed') return data.result;
      if (data.status === 'failed') throw new Error(data.error || 'Task failed');
    }
  },

  // User authentication
  login: async (credentials) => {
    try {
      const response = await apiClient.post('/api/auth/login', credentials);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  register: async (userData) => {
    try {
      const response = await apiClient.post('/api/auth/register', userData);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Get user profile
  getUserProfile: async () => {
    try {
      const response = await apiClient.get('/api/profile');
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  }
};

export default apiService;