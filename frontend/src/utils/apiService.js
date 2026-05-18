// apiService.js
import axios from 'axios';
import axiosRetry from 'axios-retry';

// Create an axios instance with base configuration
const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000',
  timeout: 120000, // 120 seconds timeout (increased for AI processing)
  headers: {
    'Content-Type': 'application/json',
  }
});

// Configure automated retry logic
axiosRetry(apiClient, { 
  retries: 3, 
  retryDelay: axiosRetry.exponentialDelay,
  retryCondition: (error) => {
    // Retry on network errors or 5xx server errors
    return axiosRetry.isNetworkOrIdempotentRequestError(error) || 
           (error.response && error.response.status >= 500);
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
    const TOTAL_TIMEOUT = 180000; // 3 minutes total timeout
    const startTime = Date.now();

    // Step 1: submit the request
    try {
      const { data: task } = await apiClient.post('/api/housing-recommendations', inputData);
      const taskId = task.task_id;

      // Step 2: SSE (primary real-time update method)
      let result = await new Promise((resolve, reject) => {
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
          } catch (err) {
            finish(reject, new Error('Error parsing advisor updates'));
          }
        };

        es.onerror = () => {
          // Don't reject immediately, allow fallback to polling
          finish(resolve, null);
        };

        // Safety timeout for SSE — fallback to polling if it takes too long to connect/update
        setTimeout(() => finish(resolve, null), 45000); 
      });

      if (result) return result;

      // Step 3: Polling fallback (if SSE failed or timed out)
      while (Date.now() - startTime < TOTAL_TIMEOUT) {
        await new Promise(r => setTimeout(r, 2000));
        
        try {
          const { data } = await apiClient.get(`/api/tasks/${taskId}/status`);
          if (onProgress) onProgress(data.current_step, data.progress);
          
          if (data.status === 'completed') return data.result;
          if (data.status === 'failed') throw new Error(data.error || 'Task failed');
        } catch (pollError) {
          // If polling itself fails, we might want to retry a few times
          console.error('Polling error:', pollError);
        }
      }

      throw new Error('The advisor is taking longer than expected. Please try again or simplify your request.');
    } catch (error) {
      if (error.code === 'ECONNABORTED') {
        throw new Error('Connection timeout. The server is busy processing your request.');
      }
      throw error;
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