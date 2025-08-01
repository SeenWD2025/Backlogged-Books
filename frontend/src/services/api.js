import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

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
