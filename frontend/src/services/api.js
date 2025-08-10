import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'https://localhost';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token to all requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token expiration
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid - clear it and redirect to login
      localStorage.removeItem('authToken');
      // Only redirect if we're not already on login/register pages
      if (!window.location.pathname.includes('/login') && !window.location.pathname.includes('/register')) {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export const uploadFile = async (file, csvFormat = '3-column', dateFormat = 'MM/DD/YYYY') => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('csv_format', csvFormat);
  formData.append('date_format', dateFormat);

  try {
    const response = await apiClient.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};

export const getJobStatus = async (jobId) => {
  try {
    const response = await apiClient.get(`/status/${jobId}`);
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};

export const downloadProcessedFile = async (jobId) => {
  try {
    const response = await apiClient.get(`/download/${jobId}`, {
      responseType: 'blob',
    });
    return response;
  } catch (error) {
    throw handleApiError(error);
  }
};

export const getAllJobs = async (limit = 20, offset = 0) => {
  try {
    const response = await apiClient.get(`/jobs?limit=${limit}&offset=${offset}`);
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};

// Helper function to handle API errors
const handleApiError = (error) => {
  if (error.response) {
    // The request was made and the server responded with a status code
    // that falls out of the range of 2xx
    return {
      status: error.response.status,
      message: error.response.data.detail || 'An error occurred with the API',
      data: error.response.data,
    };
  } else if (error.request) {
    // The request was made but no response was received
    return {
      status: 0,
      message: 'No response received from the server. Check your network connection.',
      data: null,
    };
  } else {
    // Something happened in setting up the request that triggered an Error
    return {
      status: 0,
      message: error.message || 'An error occurred while setting up the request',
      data: null,
    };
  }
};

// Authentication API functions
export const loginUser = async (email, password) => {
  try {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await apiClient.post('/auth/jwt/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};

export const registerUser = async (email, password) => {
  try {
    const response = await apiClient.post('/auth/register', {
      email,
      password,
    });
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};

export const getCurrentUser = async () => {
  try {
    const response = await apiClient.get('/users/me');
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};

export const verifyUserEmail = async (token) => {
  try {
    const response = await apiClient.post('/auth/verify', {
      token,
    });
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};

export const resendVerificationEmail = async (email) => {
  try {
    const response = await apiClient.post('/auth/request-verify-token', {
      email,
    });
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};

export const logoutUser = async () => {
  try {
    const response = await apiClient.post('/auth/jwt/logout');
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};
