/**
 * API Service - Mobile API communication service
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import axios, { AxiosInstance, AxiosResponse } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-community/netinfo';

class ApiService {
  private api: AxiosInstance;
  private baseURL: string;

  constructor() {
    this.baseURL = __DEV__ 
      ? 'http://10.0.2.2:8000/api'  // Android emulator localhost
      : 'https://api.ainflue.com';
    
    this.api = axios.create({
      baseURL: this.baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor
    this.api.interceptors.request.use(
      async (config) => {
        // Check network connectivity
        const netInfo = await NetInfo.fetch();
        if (!netInfo.isConnected) {
          throw new Error('No internet connection');
        }

        // Add auth token
        const token = await AsyncStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }

        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.api.interceptors.response.use(
      (response: AxiosResponse) => {
        return response;
      },
      async (error) => {
        if (error.response?.status === 401) {
          // Token expired, clear storage and redirect to login
          await AsyncStorage.multiRemove(['auth_token', 'user_data']);
          // Navigation to login would be handled by the app
        }
        return Promise.reject(error);
      }
    );
  }

  // Authentication
  async login(email: string, password: string) {
    const response = await this.api.post('/auth/login', { email, password });
    const { token, user } = response.data;
    
    await AsyncStorage.multiSet([
      ['auth_token', token],
      ['user_data', JSON.stringify(user)],
    ]);
    
    return response.data;
  }

  async logout() {
    await this.api.post('/auth/logout');
    await AsyncStorage.multiRemove(['auth_token', 'user_data']);
  }

  async refreshToken() {
    const response = await this.api.post('/auth/refresh');
    const { token } = response.data;
    await AsyncStorage.setItem('auth_token', token);
    return token;
  }

  // Dashboard
  async getDashboardMetrics() {
    const response = await this.api.get('/dashboard/metrics');
    return response.data;
  }

  async getRecentActivity() {
    const response = await this.api.get('/dashboard/activity');
    return response.data;
  }

  // Content Management
  async uploadContent(formData: FormData, onProgress?: (progress: number) => void) {
    const response = await this.api.post('/content/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = (progressEvent.loaded / progressEvent.total) * 100;
          onProgress(progress);
        }
      },
    });
    return response.data;
  }

  async getContentLibrary(page = 1, limit = 20) {
    const response = await this.api.get(`/content/library?page=${page}&limit=${limit}`);
    return response.data;
  }

  async deleteContent(contentId: string) {
    const response = await this.api.delete(`/content/${contentId}`);
    return response.data;
  }

  // Protection
  async getProtectionStatus() {
    const response = await this.api.get('/protection/status');
    return response.data;
  }

  async getViolationAlerts() {
    const response = await this.api.get('/protection/violations');
    return response.data;
  }

  async reportViolation(violationData: any) {
    const response = await this.api.post('/protection/report', violationData);
    return response.data;
  }

  // Analytics
  async getAnalytics(timeframe = '30d') {
    const response = await this.api.get(`/analytics/overview?timeframe=${timeframe}`);
    return response.data;
  }

  async getRevenueData(timeframe = '30d') {
    const response = await this.api.get(`/analytics/revenue?timeframe=${timeframe}`);
    return response.data;
  }

  async getPerformanceMetrics(timeframe = '30d') {
    const response = await this.api.get(`/analytics/performance?timeframe=${timeframe}`);
    return response.data;
  }

  // User Profile
  async getUserProfile() {
    const response = await this.api.get('/user/profile');
    return response.data;
  }

  async updateUserProfile(profileData: any) {
    const response = await this.api.put('/user/profile', profileData);
    return response.data;
  }

  async updateUserSettings(settings: any) {
    const response = await this.api.put('/user/settings', settings);
    return response.data;
  }

  // Notifications
  async getNotifications(page = 1, limit = 20) {
    const response = await this.api.get(`/notifications?page=${page}&limit=${limit}`);
    return response.data;
  }

  async markNotificationRead(notificationId: string) {
    const response = await this.api.put(`/notifications/${notificationId}/read`);
    return response.data;
  }

  async markAllNotificationsRead() {
    const response = await this.api.put('/notifications/mark-all-read');
    return response.data;
  }

  // Subscription & Billing
  async getSubscriptionInfo() {
    const response = await this.api.get('/billing/subscription');
    return response.data;
  }

  async updatePaymentMethod(paymentData: any) {
    const response = await this.api.put('/billing/payment-method', paymentData);
    return response.data;
  }

  // Search
  async searchContent(query: string, filters: any = {}) {
    const response = await this.api.post('/search/content', { query, filters });
    return response.data;
  }

  // Collaboration
  async getCollaborations() {
    const response = await this.api.get('/collaborations');
    return response.data;
  }

  async createCollaboration(collaborationData: any) {
    const response = await this.api.post('/collaborations', collaborationData);
    return response.data;
  }

  async updateCollaboration(collaborationId: string, data: any) {
    const response = await this.api.put(`/collaborations/${collaborationId}`, data);
    return response.data;
  }

  // Error handling helpers
  handleApiError(error: any) {
    if (error.response) {
      // Server responded with error status
      return {
        status: error.response.status,
        message: error.response.data?.message || 'Server error occurred',
        data: error.response.data,
      };
    } else if (error.request) {
      // Request was made but no response received
      return {
        status: 0,
        message: 'Network error - please check your connection',
        data: null,
      };
    } else {
      // Something else happened
      return {
        status: -1,
        message: error.message || 'An unexpected error occurred',
        data: null,
      };
    }
  }

  // Network status
  async isOnline(): Promise<boolean> {
    const netInfo = await NetInfo.fetch();
    return netInfo.isConnected || false;
  }

  // Cache management
  async clearCache() {
    // Implementation would depend on caching strategy
    console.log('Cache cleared');
  }
}

export default new ApiService();