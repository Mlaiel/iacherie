/**
 * @fileoverview Enterprise Jest Mock Template Collection
 * @version 1.0.0
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @copyright 2025 Fahed Mlaiel - All Rights Reserved
 * @license Proprietary - Unauthorized use prohibited
 * 
 * 🚨 INTELLECTUAL PROPERTY WARNING:
 * This code is the exclusive property of Fahed Mlaiel.
 * Unauthorized copying, modification, distribution, or commercial use
 * without explicit written permission is strictly prohibited.
 * Violation will result in immediate legal action.
 */

import { jest } from '@jest/globals';

// ==================== TYPES & INTERFACES ====================

interface MockResponse<T = any> {
  data: T;
  status: number;
  statusText: string;
  headers: Record<string, string>;
}

interface MockError {
  message: string;
  code?: string;
  status?: number;
}

interface APIEndpoint {
  url: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  response: any;
  delay?: number;
  shouldFail?: boolean;
  error?: MockError;
}

interface WebSocketMock {
  url: string;
  readyState: number;
  send: jest.MockedFunction<(data: string) => void>;
  close: jest.MockedFunction<() => void>;
  addEventListener: jest.MockedFunction<(event: string, handler: Function) => void>;
  removeEventListener: jest.MockedFunction<(event: string, handler: Function) => void>;
}

// ==================== MOCK FACTORIES ====================

/**
 * Creates a comprehensive mock for HTTP client (axios, fetch, etc.)
 */
export const createHTTPClientMock = () => {
  const mockAxios = {
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
    patch: jest.fn(),
    request: jest.fn(),
    create: jest.fn(() => mockAxios),
    defaults: {
      headers: {
        common: {},
        get: {},
        post: {},
        put: {},
        delete: {},
        patch: {}
      },
      timeout: 10000,
      baseURL: ''
    },
    interceptors: {
      request: {
        use: jest.fn(),
        eject: jest.fn()
      },
      response: {
        use: jest.fn(),
        eject: jest.fn()
      }
    }
  };

  // Setup default successful responses
  mockAxios.get.mockResolvedValue({ data: {}, status: 200, statusText: 'OK' });
  mockAxios.post.mockResolvedValue({ data: {}, status: 201, statusText: 'Created' });
  mockAxios.put.mockResolvedValue({ data: {}, status: 200, statusText: 'OK' });
  mockAxios.delete.mockResolvedValue({ data: {}, status: 204, statusText: 'No Content' });
  mockAxios.patch.mockResolvedValue({ data: {}, status: 200, statusText: 'OK' });

  return mockAxios;
};

/**
 * Creates mock responses for specific API endpoints
 */
export const createAPIEndpointMocks = (endpoints: APIEndpoint[]) => {
  const mockClient = createHTTPClientMock();

  endpoints.forEach(endpoint => {
    const method = endpoint.method.toLowerCase() as keyof typeof mockClient;
    const mockMethod = mockClient[method] as jest.MockedFunction<any>;

    if (endpoint.shouldFail) {
      mockMethod.mockRejectedValueOnce(endpoint.error || new Error('API Error'));
    } else {
      const response: MockResponse = {
        data: endpoint.response,
        status: 200,
        statusText: 'OK',
        headers: { 'content-type': 'application/json' }
      };

      if (endpoint.delay) {
        mockMethod.mockImplementationOnce(
          () => new Promise(resolve => 
            setTimeout(() => resolve(response), endpoint.delay)
          )
        );
      } else {
        mockMethod.mockResolvedValueOnce(response);
      }
    }
  });

  return mockClient;
};

/**
 * Creates mock for WebSocket connections
 */
export const createWebSocketMock = (url: string): WebSocketMock => {
  const mockWebSocket = {
    url,
    readyState: 1, // OPEN
    send: jest.fn(),
    close: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    onopen: null,
    onclose: null,
    onmessage: null,
    onerror: null
  } as any;

  // Simulate connection events
  const simulateEvent = (type: string, data?: any) => {
    const event = { type, data, target: mockWebSocket };
    
    // Call event listeners
    if (mockWebSocket[`on${type}`]) {
      mockWebSocket[`on${type}`](event);
    }
    
    // Call addEventListener callbacks
    mockWebSocket.addEventListener.mock.calls
      .filter(([eventType]) => eventType === type)
      .forEach(([, handler]) => handler(event));
  };

  // Add helper methods for testing
  (mockWebSocket as any).simulateOpen = () => simulateEvent('open');
  (mockWebSocket as any).simulateMessage = (data: any) => simulateEvent('message', data);
  (mockWebSocket as any).simulateClose = () => simulateEvent('close');
  (mockWebSocket as any).simulateError = (error: any) => simulateEvent('error', error);

  return mockWebSocket;
};

/**
 * Creates mock for local storage
 */
export const createLocalStorageMock = () => {
  const store: Record<string, string> = {};

  return {
    getItem: jest.fn((key: string) => store[key] || null),
    setItem: jest.fn((key: string, value: string) => { store[key] = value; }),
    removeItem: jest.fn((key: string) => { delete store[key]; }),
    clear: jest.fn(() => { Object.keys(store).forEach(key => delete store[key]); }),
    length: Object.keys(store).length,
    key: jest.fn((index: number) => Object.keys(store)[index] || null),
    // Helper for testing
    _getStore: () => ({ ...store }),
    _setStore: (newStore: Record<string, string>) => {
      Object.keys(store).forEach(key => delete store[key]);
      Object.assign(store, newStore);
    }
  };
};

/**
 * Creates mock for media elements (audio, video)
 */
export const createMediaElementMock = () => {
  const mockMedia = {
    // Properties
    currentTime: 0,
    duration: 100,
    paused: true,
    ended: false,
    muted: false,
    volume: 1,
    playbackRate: 1,
    src: '',
    
    // Methods
    play: jest.fn().mockResolvedValue(undefined),
    pause: jest.fn(),
    load: jest.fn(),
    canPlayType: jest.fn().mockReturnValue('maybe'),
    
    // Events
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
    
    // Helper methods for testing
    simulateTimeUpdate: (time: number) => {
      mockMedia.currentTime = time;
      const event = new Event('timeupdate');
      mockMedia.addEventListener.mock.calls
        .filter(([eventType]) => eventType === 'timeupdate')
        .forEach(([, handler]) => handler(event));
    },
    
    simulateEnded: () => {
      mockMedia.ended = true;
      mockMedia.paused = true;
      const event = new Event('ended');
      mockMedia.addEventListener.mock.calls
        .filter(([eventType]) => eventType === 'ended')
        .forEach(([, handler]) => handler(event));
    },
    
    simulateError: (error: any) => {
      const event = Object.assign(new Event('error'), { error });
      mockMedia.addEventListener.mock.calls
        .filter(([eventType]) => eventType === 'error')
        .forEach(([, handler]) => handler(event));
    }
  };

  return mockMedia;
};

/**
 * Creates mock for File API
 */
export const createFileMock = (
  name: string, 
  content: string, 
  type: string = 'text/plain'
) => {
  const file = new Blob([content], { type });
  Object.defineProperty(file, 'name', { value: name });
  Object.defineProperty(file, 'lastModified', { value: Date.now() });
  Object.defineProperty(file, 'size', { value: content.length });
  
  return file as File;
};

/**
 * Creates mock for FileReader API
 */
export const createFileReaderMock = () => {
  const mockFileReader = {
    result: null,
    error: null,
    readyState: 0,
    
    readAsText: jest.fn(),
    readAsDataURL: jest.fn(),
    readAsArrayBuffer: jest.fn(),
    readAsBinaryString: jest.fn(),
    abort: jest.fn(),
    
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    
    // Helper methods for testing
    simulateLoad: (result: any) => {
      mockFileReader.result = result;
      mockFileReader.readyState = 2; // DONE
      const event = Object.assign(new Event('load'), { target: mockFileReader });
      mockFileReader.addEventListener.mock.calls
        .filter(([eventType]) => eventType === 'load')
        .forEach(([, handler]) => handler(event));
    },
    
    simulateError: (error: any) => {
      mockFileReader.error = error;
      mockFileReader.readyState = 2; // DONE
      const event = Object.assign(new Event('error'), { target: mockFileReader });
      mockFileReader.addEventListener.mock.calls
        .filter(([eventType]) => eventType === 'error')
        .forEach(([, handler]) => handler(event));
    }
  };

  return mockFileReader;
};

/**
 * Creates mock for Intersection Observer API
 */
export const createIntersectionObserverMock = () => {
  const mockIntersectionObserver = {
    observe: jest.fn(),
    unobserve: jest.fn(),
    disconnect: jest.fn(),
    root: null,
    rootMargin: '0px',
    thresholds: [0],
    
    // Helper for testing
    simulateIntersection: (entries: any[]) => {
      const callback = mockIntersectionObserver._callback;
      if (callback) {
        callback(entries, mockIntersectionObserver);
      }
    },
    
    _callback: null as any
  };

  // Mock constructor
  (global as any).IntersectionObserver = jest.fn().mockImplementation((callback) => {
    mockIntersectionObserver._callback = callback;
    return mockIntersectionObserver;
  });

  return mockIntersectionObserver;
};

/**
 * Creates mock for ResizeObserver API
 */
export const createResizeObserverMock = () => {
  const mockResizeObserver = {
    observe: jest.fn(),
    unobserve: jest.fn(),
    disconnect: jest.fn(),
    
    // Helper for testing
    simulateResize: (entries: any[]) => {
      const callback = mockResizeObserver._callback;
      if (callback) {
        callback(entries, mockResizeObserver);
      }
    },
    
    _callback: null as any
  };

  // Mock constructor
  (global as any).ResizeObserver = jest.fn().mockImplementation((callback) => {
    mockResizeObserver._callback = callback;
    return mockResizeObserver;
  });

  return mockResizeObserver;
};

/**
 * Creates mock for Geolocation API
 */
export const createGeolocationMock = () => {
  const mockGeolocation = {
    getCurrentPosition: jest.fn(),
    watchPosition: jest.fn().mockReturnValue(1),
    clearWatch: jest.fn(),
    
    // Helper methods for testing
    simulatePosition: (position: GeolocationPosition) => {
      const successCallback = mockGeolocation.getCurrentPosition.mock.calls[0]?.[0];
      if (successCallback) {
        successCallback(position);
      }
    },
    
    simulateError: (error: GeolocationPositionError) => {
      const errorCallback = mockGeolocation.getCurrentPosition.mock.calls[0]?.[1];
      if (errorCallback) {
        errorCallback(error);
      }
    }
  };

  Object.defineProperty(global.navigator, 'geolocation', {
    value: mockGeolocation,
    writable: true
  });

  return mockGeolocation;
};

/**
 * Creates mock for Notification API
 */
export const createNotificationMock = () => {
  const mockNotification = {
    permission: 'default' as NotificationPermission,
    requestPermission: jest.fn().mockResolvedValue('granted' as NotificationPermission),
    
    // Helper methods for testing
    setPermission: (permission: NotificationPermission) => {
      mockNotification.permission = permission;
    }
  };

  const MockNotificationConstructor = jest.fn().mockImplementation((title, options) => ({
    title,
    ...options,
    close: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    onclick: null,
    onclose: null,
    onerror: null,
    onshow: null
  }));

  Object.defineProperty(MockNotificationConstructor, 'permission', {
    get: () => mockNotification.permission
  });

  Object.defineProperty(MockNotificationConstructor, 'requestPermission', {
    value: mockNotification.requestPermission
  });

  (global as any).Notification = MockNotificationConstructor;

  return { mockNotification, MockNotificationConstructor };
};

// ==================== MOCK DATA GENERATORS ====================

/**
 * Generates mock user data
 */
export const generateMockUser = (overrides: Partial<any> = {}) => ({
  id: '1',
  username: 'testuser',
  email: 'test@example.com',
  displayName: 'Test User',
  avatar: 'https://api.placeholder.pics/150x150',
  verified: false,
  createdAt: new Date().toISOString(),
  ...overrides
});

/**
 * Generates mock content data
 */
export const generateMockContent = (overrides: Partial<any> = {}) => ({
  id: '1',
  title: 'Test Content',
  description: 'This is test content',
  type: 'audio',
  url: '/test-content.mp3',
  thumbnailUrl: 'https://api.placeholder.pics/300x200',
  duration: 120,
  fileSize: 1024000,
  createdAt: new Date().toISOString(),
  status: 'published',
  ...overrides
});

/**
 * Generates mock analytics data
 */
export const generateMockAnalytics = (overrides: Partial<any> = {}) => ({
  views: 1000,
  likes: 100,
  shares: 50,
  comments: 25,
  engagement: 75.5,
  revenue: 150.00,
  ...overrides
});

// ==================== UTILITY FUNCTIONS ====================

/**
 * Creates a promise that resolves after a delay
 */
export const createDelayedPromise = <T>(value: T, delay: number = 100): Promise<T> => {
  return new Promise(resolve => setTimeout(() => resolve(value), delay));
};

/**
 * Creates a promise that rejects after a delay
 */
export const createDelayedRejection = (error: any, delay: number = 100): Promise<never> => {
  return new Promise((_, reject) => setTimeout(() => reject(error), delay));
};

/**
 * Mocks console methods for testing
 */
export const mockConsole = () => {
  const originalConsole = { ...console };
  
  const mockMethods = {
    log: jest.fn(),
    warn: jest.fn(),
    error: jest.fn(),
    info: jest.fn(),
    debug: jest.fn()
  };

  Object.assign(console, mockMethods);

  return {
    ...mockMethods,
    restore: () => Object.assign(console, originalConsole)
  };
};

/**
 * Mocks Date.now() and other date methods
 */
export const mockDate = (fixedDate: Date | string | number) => {
  const originalDate = Date;
  const mockDate = new Date(fixedDate);
  
  const MockDateConstructor = jest.fn().mockImplementation((...args) => {
    if (args.length === 0) {
      return mockDate;
    }
    return new originalDate(...args);
  });

  MockDateConstructor.now = jest.fn().mockReturnValue(mockDate.getTime());
  MockDateConstructor.UTC = originalDate.UTC;
  MockDateConstructor.parse = originalDate.parse;

  (global as any).Date = MockDateConstructor;

  return {
    mockDate,
    restore: () => { (global as any).Date = originalDate; }
  };
};

/**
 * Mocks Math.random() for predictable testing
 */
export const mockMathRandom = (values: number[] | number) => {
  const originalRandom = Math.random;
  let index = 0;
  
  const mockRandom = jest.fn().mockImplementation(() => {
    if (Array.isArray(values)) {
      const value = values[index % values.length];
      index++;
      return value;
    }
    return values;
  });

  Math.random = mockRandom;

  return {
    mockRandom,
    restore: () => { Math.random = originalRandom; }
  };
};

// ==================== EXPORTS ====================

export default {
  createHTTPClientMock,
  createAPIEndpointMocks,
  createWebSocketMock,
  createLocalStorageMock,
  createMediaElementMock,
  createFileMock,
  createFileReaderMock,
  createIntersectionObserverMock,
  createResizeObserverMock,
  createGeolocationMock,
  createNotificationMock,
  generateMockUser,
  generateMockContent,
  generateMockAnalytics,
  createDelayedPromise,
  createDelayedRejection,
  mockConsole,
  mockDate,
  mockMathRandom
};

// Type exports
export type {
  MockResponse,
  MockError,
  APIEndpoint,
  WebSocketMock
};