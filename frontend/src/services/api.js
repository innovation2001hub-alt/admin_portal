import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  // Login
  login: async (employeeId, password) => {
    try {
      const response = await api.post('/auth/login/', {
        employee_id: employeeId,
        password,
      });
      
      if (response.data.token) {
        localStorage.setItem('token', response.data.token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
      }
      
      return response.data;
    } catch (error) {
      throw error.response?.data || { error: 'Login failed' };
    }
  },

  // Logout
  logout: async () => {
    try {
      await api.post('/auth/logout/');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    }
  },

  // Get current user
  getCurrentUser: async () => {
    try {
      const response = await api.get('/auth/current-user/');
      return response.data;
    } catch (error) {
      throw error.response?.data || { error: 'Failed to fetch user' };
    }
  },

  // Check if user is authenticated
  isAuthenticated: () => {
    return !!localStorage.getItem('token');
  },

  // Get stored user
  getUser: () => {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  },
};

// Approval Workflow API
export const approvalsAPI = {
  // Create new approval request
  create: async (requestType, title, description, payload = {}) => {
    try {
      const response = await api.post('/approvals/', {
        request_type: requestType,
        title,
        description,
        payload,
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || { error: 'Failed to create request' };
    }
  },

  // Get all approvals (with filters)
  getAll: async (filters = {}) => {
    try {
      const response = await api.get('/approvals/', { params: filters });
      return response.data;
    } catch (error) {
      throw error.response?.data || { error: 'Failed to fetch approvals' };
    }
  },

  // Get single approval
  get: async (id) => {
    try {
      const response = await api.get(`/approvals/${id}/`);
      return response.data;
    } catch (error) {
      throw error.response?.data || { error: 'Failed to fetch approval' };
    }
  },

  // Get my requests (MAKER)
  getMyRequests: async () => {
    try {
      console.log('Fetching my requests from:', `${API_URL}/approvals/my-requests/`);
      const response = await api.get('/approvals/my-requests/');
      console.log('My requests response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Error fetching my requests:', error.response || error);
      throw error.response?.data || { error: `Failed to fetch your requests: ${error.message}` };
    }
  },

  // Get pending queue (CHECKER)
  getPendingQueue: async () => {
    try {
      console.log('Fetching pending queue from:', `${API_URL}/approvals/pending-queue/`);
      const response = await api.get('/approvals/pending-queue/');
      console.log('Pending queue response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Error fetching pending queue:', error.response || error);
      throw error.response?.data || { error: `Failed to fetch pending queue: ${error.message}` };
    }
  },

  // Get statistics
  getStatistics: async () => {
    try {
      const response = await api.get('/approvals/statistics/');
      return response.data;
    } catch (error) {
      throw error.response?.data || { error: 'Failed to fetch statistics' };
    }
  },

  // Approve request
  approve: async (id, remarks = '') => {
    try {
      const response = await api.post(`/approvals/${id}/approve/`, {
        remarks,
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || { error: 'Failed to approve request' };
    }
  },

  // Reject request
  reject: async (id, remarks = '') => {
    try {
      const response = await api.post(`/approvals/${id}/reject/`, {
        remarks,
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || { error: 'Failed to reject request' };
    }
  },
};

export default api;
