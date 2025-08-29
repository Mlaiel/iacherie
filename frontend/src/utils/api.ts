/**
 * API Utilities - Frontend API communication helpers
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import axios from 'axios';

// API Base Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('authToken') : null;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized - redirect to login
      if (typeof window !== 'undefined') {
        localStorage.removeItem('authToken');
        window.location.href = '/auth/login';
      }
    }
    return Promise.reject(error);
  }
);

// API Functions
export const api = {
  // Dashboard APIs
  dashboard: {
    getMetrics: () => apiClient.get('/dashboard/metrics'),
    getRecentActivity: () => apiClient.get('/dashboard/activity'),
  },

  // Upload APIs
  upload: {
    uploadFile: (file: File, config?: any) => {
      const formData = new FormData();
      formData.append('file', file);
      return apiClient.post('/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        ...config,
      });
    },
    getUploadStatus: (uploadId: string) => apiClient.get(`/upload/status/${uploadId}`),
  },

  // Content APIs
  content: {
    getLibrary: (params?: any) => apiClient.get('/content/library', { params }),
    getContent: (id: string) => apiClient.get(`/content/${id}`),
    updateContent: (id: string, data: any) => apiClient.put(`/content/${id}`, data),
    deleteContent: (id: string) => apiClient.delete(`/content/${id}`),
    searchContent: (query: string, filters?: any) => 
      apiClient.get('/content/search', { params: { q: query, ...filters } }),
  },

  // Protection APIs
  protection: {
    getFingerprints: () => apiClient.get('/protection/fingerprints'),
    getViolations: (params?: any) => apiClient.get('/protection/violations', { params }),
    reportViolation: (data: any) => apiClient.post('/protection/violations', data),
    sendDMCA: (violationId: string) => apiClient.post(`/protection/dmca/${violationId}`),
  },

  // Analytics APIs
  analytics: {
    getRevenueData: (timeframe?: string) => 
      apiClient.get('/analytics/revenue', { params: { timeframe } }),
    getPlatformStats: () => apiClient.get('/analytics/platforms'),
    getPerformanceMetrics: () => apiClient.get('/analytics/performance'),
  },

  // User APIs
  user: {
    getProfile: () => apiClient.get('/user/profile'),
    updateProfile: (data: any) => apiClient.put('/user/profile', data),
    getSettings: () => apiClient.get('/user/settings'),
    updateSettings: (data: any) => apiClient.put('/user/settings', data),
  },

  // Auth APIs
  auth: {
    login: (credentials: { email: string; password: string }) => 
      apiClient.post('/auth/login', credentials),
    register: (userData: any) => apiClient.post('/auth/register', userData),
    logout: () => apiClient.post('/auth/logout'),
    refreshToken: () => apiClient.post('/auth/refresh'),
  },
};

// Utility functions
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export const formatDuration = (seconds: number): string => {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

export const formatCurrency = (amount: number, currency = 'USD'): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
  }).format(amount);
};

export const formatDate = (date: string | Date): string => {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(new Date(date));
};

export const formatDateTime = (date: string | Date): string => {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(date));
};

export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void => {
  let timeout: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
};

export const getFileType = (filename: string): 'audio' | 'video' | 'image' | 'document' => {
  const ext = filename.split('.').pop()?.toLowerCase();
  
  const audioExts = ['mp3', 'wav', 'flac', 'aac', 'm4a', 'ogg'];
  const videoExts = ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm'];
  const imageExts = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp'];
  
  if (audioExts.includes(ext || '')) return 'audio';
  if (videoExts.includes(ext || '')) return 'video';
  if (imageExts.includes(ext || '')) return 'image';
  return 'document';
};

export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const validatePassword = (password: string): {
  isValid: boolean;
  errors: string[];
} => {
  const errors: string[] = [];
  
  if (password.length < 8) {
    errors.push('Password must be at least 8 characters long');
  }
  if (!/[A-Z]/.test(password)) {
    errors.push('Password must contain at least one uppercase letter');
  }
  if (!/[a-z]/.test(password)) {
    errors.push('Password must contain at least one lowercase letter');
  }
  if (!/\d/.test(password)) {
    errors.push('Password must contain at least one number');
  }
  if (!/[!@#$%^&*]/.test(password)) {
    errors.push('Password must contain at least one special character');
  }
  
  return {
    isValid: errors.length === 0,
    errors,
  };
};

export default api;