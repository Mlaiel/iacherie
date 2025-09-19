/**
 * 🧪 API Client Tests - HTTP Client Testing Suite
 * 
 * @fileoverview Test suite for API client with authentication and error handling
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @role Testing Expert + Backend Senior
 * @copyright 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
 */

import { jest } from '@jest/globals';
import axios from 'axios';
import { ApiClient } from '../../../core/api/apiClient';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn()
};
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

describe('ApiClient', () => {
  let apiClient: ApiClient;
  let mockAxiosInstance: any;

  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock axios instance
    mockAxiosInstance = {
      get: jest.fn(),
      post: jest.fn(),
      put: jest.fn(),
      patch: jest.fn(),
      delete: jest.fn(),
      interceptors: {
        request: { use: jest.fn() },
        response: { use: jest.fn() }
      }
    };
    
    mockedAxios.create.mockReturnValue(mockAxiosInstance);
    
    apiClient = new ApiClient({
      baseURL: 'http://localhost:8000',
      timeout: 5000
    });
  });

  describe('Initialization', () => {
    test('should create axios instance with correct config', () => {
      expect(mockedAxios.create).toHaveBeenCalledWith({
        baseURL: 'http://localhost:8000',
        timeout: 5000,
        withCredentials: true,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          'X-Client-Version': '2.0.0',
          'X-Client-Platform': 'web'
        }
      });
    });

    test('should setup request and response interceptors', () => {
      expect(mockAxiosInstance.interceptors.request.use).toHaveBeenCalled();
      expect(mockAxiosInstance.interceptors.response.use).toHaveBeenCalled();
    });
  });

  describe('Authentication', () => {
    test('should set auth token', () => {
      const token = 'test-token';
      apiClient.setAuthToken(token);
      
      expect(localStorageMock.setItem).toHaveBeenCalledWith('access_token', token);
    });

    test('should clear auth token', () => {
      apiClient.clearAuthToken();
      
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('access_token');
    });

    test('should get auth token', () => {
      localStorageMock.getItem.mockReturnValue('stored-token');
      
      const token = apiClient.getAuthToken();
      
      expect(token).toBe('stored-token');
      expect(localStorageMock.getItem).toHaveBeenCalledWith('access_token');
    });
  });

  describe('HTTP Methods', () => {
    const mockResponse = {
      data: {
        success: true,
        data: { id: 1, name: 'Test' },
        message: 'Success'
      }
    };

    test('should make GET request', async () => {
      mockAxiosInstance.get.mockResolvedValue(mockResponse);
      
      const result = await apiClient.get('/test');
      
      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/test', undefined);
      expect(result).toEqual(mockResponse.data);
    });

    test('should make POST request', async () => {
      const data = { name: 'Test' };
      mockAxiosInstance.post.mockResolvedValue(mockResponse);
      
      const result = await apiClient.post('/test', data);
      
      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/test', data, undefined);
      expect(result).toEqual(mockResponse.data);
    });

    test('should make PUT request', async () => {
      const data = { id: 1, name: 'Updated' };
      mockAxiosInstance.put.mockResolvedValue(mockResponse);
      
      const result = await apiClient.put('/test/1', data);
      
      expect(mockAxiosInstance.put).toHaveBeenCalledWith('/test/1', data, undefined);
      expect(result).toEqual(mockResponse.data);
    });

    test('should make PATCH request', async () => {
      const data = { name: 'Patched' };
      mockAxiosInstance.patch.mockResolvedValue(mockResponse);
      
      const result = await apiClient.patch('/test/1', data);
      
      expect(mockAxiosInstance.patch).toHaveBeenCalledWith('/test/1', data, undefined);
      expect(result).toEqual(mockResponse.data);
    });

    test('should make DELETE request', async () => {
      mockAxiosInstance.delete.mockResolvedValue(mockResponse);
      
      const result = await apiClient.delete('/test/1');
      
      expect(mockAxiosInstance.delete).toHaveBeenCalledWith('/test/1', undefined);
      expect(result).toEqual(mockResponse.data);
    });
  });

  describe('File Upload', () => {
    test('should upload file with FormData', async () => {
      const file = new File(['test'], 'test.txt', { type: 'text/plain' });
      const mockResponse = {
        data: {
          success: true,
          data: { fileId: 'file-123', url: 'http://example.com/file.txt' }
        }
      };
      
      mockAxiosInstance.post.mockResolvedValue(mockResponse);
      
      const result = await apiClient.uploadFile('/upload', file);
      
      expect(mockAxiosInstance.post).toHaveBeenCalledWith(
        '/upload',
        expect.any(FormData),
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          },
          onUploadProgress: undefined
        }
      );
      expect(result).toEqual(mockResponse.data);
    });

    test('should handle upload progress callback', async () => {
      const file = new File(['test'], 'test.txt', { type: 'text/plain' });
      const progressCallback = jest.fn();
      const mockResponse = {
        data: { success: true, data: { fileId: 'file-123' } }
      };
      
      mockAxiosInstance.post.mockResolvedValue(mockResponse);
      
      await apiClient.uploadFile('/upload', file, progressCallback);
      
      expect(mockAxiosInstance.post).toHaveBeenCalledWith(
        '/upload',
        expect.any(FormData),
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          },
          onUploadProgress: progressCallback
        }
      );
    });
  });

  describe('Health Check', () => {
    test('should perform basic health check', async () => {
      const mockResponse = {
        data: { success: true, data: { status: 'healthy' } }
      };
      
      mockAxiosInstance.get.mockResolvedValue(mockResponse);
      
      const result = await apiClient.healthCheck();
      
      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/health');
      expect(result).toEqual(mockResponse.data);
    });

    test('should perform detailed health check', async () => {
      const mockResponse = {
        data: { 
          success: true, 
          data: { 
            status: 'healthy',
            database: 'connected',
            redis: 'connected'
          } 
        }
      };
      
      mockAxiosInstance.get.mockResolvedValue(mockResponse);
      
      const result = await apiClient.detailedHealthCheck();
      
      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/health/detailed');
      expect(result).toEqual(mockResponse.data);
    });
  });

  describe('Error Handling', () => {
    test('should handle network errors', async () => {
      const networkError = new Error('Network Error');
      mockAxiosInstance.get.mockRejectedValue(networkError);
      
      await expect(apiClient.get('/test')).rejects.toThrow('Network Error');
    });

    test('should handle HTTP errors', async () => {
      const httpError = {
        response: {
          status: 404,
          data: {
            error: true,
            message: 'Not Found',
            status_code: 404
          }
        }
      };
      
      mockAxiosInstance.get.mockRejectedValue(httpError);
      
      await expect(apiClient.get('/test')).rejects.toEqual(httpError);
    });
  });

  describe('Request Configuration', () => {
    test('should accept custom config for requests', async () => {
      const customConfig = {
        headers: { 'Custom-Header': 'value' },
        timeout: 10000
      };
      const mockResponse = {
        data: { success: true, data: 'test' }
      };
      
      mockAxiosInstance.get.mockResolvedValue(mockResponse);
      
      await apiClient.get('/test', customConfig);
      
      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/test', customConfig);
    });

    test('should handle request parameters', async () => {
      const config = {
        params: { page: 1, limit: 10 }
      };
      const mockResponse = {
        data: { success: true, data: [] }
      };
      
      mockAxiosInstance.get.mockResolvedValue(mockResponse);
      
      await apiClient.get('/test', config);
      
      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/test', config);
    });
  });

  describe('Performance', () => {
    test('should handle multiple concurrent requests', async () => {
      const mockResponse = {
        data: { success: true, data: 'test' }
      };
      
      mockAxiosInstance.get.mockResolvedValue(mockResponse);
      
      const promises = Array.from({ length: 10 }, () => 
        apiClient.get('/test')
      );
      
      const results = await Promise.all(promises);
      
      expect(results).toHaveLength(10);
      expect(mockAxiosInstance.get).toHaveBeenCalledTimes(10);
      results.forEach(result => {
        expect(result).toEqual(mockResponse.data);
      });
    });

    test('should handle rapid sequential requests', async () => {
      const mockResponse = {
        data: { success: true, data: 'test' }
      };
      
      mockAxiosInstance.get.mockResolvedValue(mockResponse);
      
      const startTime = performance.now();
      
      for (let i = 0; i < 20; i++) {
        await apiClient.get(`/test/${i}`);
      }
      
      const endTime = performance.now();
      
      // Should complete quickly
      expect(endTime - startTime).toBeLessThan(1000);
      expect(mockAxiosInstance.get).toHaveBeenCalledTimes(20);
    });
  });
});

export { ApiClient };