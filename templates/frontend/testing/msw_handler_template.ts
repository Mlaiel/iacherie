/**
 * @fileoverview Enterprise Mock Service Worker (MSW) Handlers Template
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

import { rest } from 'msw';
import { setupWorker } from 'msw/browser';
import { setupServer } from 'msw/node';

// ==================== TYPES & INTERFACES ====================

interface User {
  id: string;
  username: string;
  email: string;
  displayName: string;
  avatar: string;
  verified: boolean;
  createdAt: string;
}

interface Content {
  id: string;
  title: string;
  description: string;
  type: 'audio' | 'video' | 'image' | 'document';
  url: string;
  thumbnailUrl: string;
  duration?: number;
  fileSize: number;
  status: 'draft' | 'published' | 'private';
  createdAt: string;
  performance: {
    views: number;
    likes: number;
    shares: number;
    revenue: number;
  };
}

interface Analytics {
  totalViews: number;
  totalRevenue: number;
  engagement: number;
  growth: number;
  topContent: Content[];
}

interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  error?: string;
}

// ==================== MOCK DATA GENERATORS ====================

const generateUser = (overrides: Partial<User> = {}): User => ({
  id: Math.random().toString(36).substr(2, 9),
  username: 'testuser',
  email: 'test@example.com',
  displayName: 'Test User',
  avatar: 'https://api.placeholder.pics/150x150',
  verified: false,
  createdAt: new Date().toISOString(),
  ...overrides
});

const generateContent = (overrides: Partial<Content> = {}): Content => ({
  id: Math.random().toString(36).substr(2, 9),
  title: 'Sample Content',
  description: 'This is a sample content item',
  type: 'audio',
  url: '/content/sample.mp3',
  thumbnailUrl: 'https://api.placeholder.pics/300x200',
  duration: 180,
  fileSize: 1024000,
  status: 'published',
  createdAt: new Date().toISOString(),
  performance: {
    views: 1000,
    likes: 100,
    shares: 50,
    revenue: 25.50
  },
  ...overrides
});

const generateAnalytics = (): Analytics => ({
  totalViews: 10000,
  totalRevenue: 1250.75,
  engagement: 78.5,
  growth: 12.3,
  topContent: [
    generateContent({ title: 'Top Content 1', performance: { views: 5000, likes: 500, shares: 250, revenue: 125.25 } }),
    generateContent({ title: 'Top Content 2', performance: { views: 3000, likes: 300, shares: 150, revenue: 75.50 } }),
    generateContent({ title: 'Top Content 3', performance: { views: 2000, likes: 200, shares: 100, revenue: 50.00 } })
  ]
});

// ==================== API HANDLERS ====================

// Authentication Handlers
const authHandlers = [
  // Login
  rest.post('/api/auth/login', async (req, res, ctx) => {
    const { email, password } = await req.json();
    
    // Simulate validation
    if (!email || !password) {
      return res(
        ctx.status(400),
        ctx.json<ApiResponse<null>>({
          success: false,
          error: 'Email and password are required'
        })
      );
    }

    if (email === 'admin@iacherie.com' && password === 'admin123') {
      return res(
        ctx.delay(1000), // Simulate network delay
        ctx.json<ApiResponse<{ user: User; token: string }>>({
          success: true,
          data: {
            user: generateUser({
              email: 'admin@iacherie.com',
              username: 'admin',
              displayName: 'Admin User',
              verified: true
            }),
            token: 'mock-jwt-token-12345'
          }
        })
      );
    }

    return res(
      ctx.status(401),
      ctx.delay(1000),
      ctx.json<ApiResponse<null>>({
        success: false,
        error: 'Invalid credentials'
      })
    );
  }),

  // Register
  rest.post('/api/auth/register', async (req, res, ctx) => {
    const userData = await req.json();
    
    return res(
      ctx.delay(1500),
      ctx.json<ApiResponse<{ user: User; token: string }>>({
        success: true,
        data: {
          user: generateUser(userData),
          token: 'mock-jwt-token-67890'
        }
      })
    );
  }),

  // Logout
  rest.post('/api/auth/logout', (req, res, ctx) => {
    return res(
      ctx.json<ApiResponse<null>>({
        success: true,
        data: null
      })
    );
  }),

  // Refresh Token
  rest.post('/api/auth/refresh', (req, res, ctx) => {
    return res(
      ctx.json<ApiResponse<{ token: string }>>({
        success: true,
        data: {
          token: 'mock-refreshed-jwt-token'
        }
      })
    );
  })
];

// User Management Handlers
const userHandlers = [
  // Get current user
  rest.get('/api/user/me', (req, res, ctx) => {
    const authHeader = req.headers.get('Authorization');
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res(
        ctx.status(401),
        ctx.json<ApiResponse<null>>({
          success: false,
          error: 'Unauthorized'
        })
      );
    }

    return res(
      ctx.json<ApiResponse<User>>({
        success: true,
        data: generateUser({
          username: 'current_user',
          displayName: 'Current User',
          verified: true
        })
      })
    );
  }),

  // Update user profile
  rest.put('/api/user/profile', async (req, res, ctx) => {
    const updates = await req.json();
    
    return res(
      ctx.delay(500),
      ctx.json<ApiResponse<User>>({
        success: true,
        data: generateUser(updates)
      })
    );
  }),

  // Get user by ID
  rest.get('/api/users/:userId', (req, res, ctx) => {
    const { userId } = req.params;
    
    return res(
      ctx.json<ApiResponse<User>>({
        success: true,
        data: generateUser({ id: userId as string })
      })
    );
  }),

  // Search users
  rest.get('/api/users/search', (req, res, ctx) => {
    const query = req.url.searchParams.get('q');
    const limit = parseInt(req.url.searchParams.get('limit') || '10');
    
    const users = Array.from({ length: Math.min(limit, 5) }, (_, i) => 
      generateUser({
        username: `user_${i + 1}`,
        displayName: `User ${i + 1} ${query || ''}`
      })
    );

    return res(
      ctx.json<ApiResponse<User[]>>({
        success: true,
        data: users
      })
    );
  })
];

// Content Management Handlers
const contentHandlers = [
  // Get user content
  rest.get('/api/content', (req, res, ctx) => {
    const page = parseInt(req.url.searchParams.get('page') || '1');
    const limit = parseInt(req.url.searchParams.get('limit') || '10');
    const type = req.url.searchParams.get('type');
    
    let content = Array.from({ length: limit }, (_, i) => 
      generateContent({ 
        title: `Content Item ${(page - 1) * limit + i + 1}`,
        type: type as any || 'audio'
      })
    );

    return res(
      ctx.json<ApiResponse<{ content: Content[]; total: number; page: number }>>({
        success: true,
        data: {
          content,
          total: 100,
          page
        }
      })
    );
  }),

  // Create content
  rest.post('/api/content', async (req, res, ctx) => {
    const contentData = await req.json();
    
    return res(
      ctx.delay(2000), // Simulate upload/processing time
      ctx.status(201),
      ctx.json<ApiResponse<Content>>({
        success: true,
        data: generateContent(contentData)
      })
    );
  }),

  // Get content by ID
  rest.get('/api/content/:contentId', (req, res, ctx) => {
    const { contentId } = req.params;
    
    return res(
      ctx.json<ApiResponse<Content>>({
        success: true,
        data: generateContent({ id: contentId as string })
      })
    );
  }),

  // Update content
  rest.put('/api/content/:contentId', async (req, res, ctx) => {
    const { contentId } = req.params;
    const updates = await req.json();
    
    return res(
      ctx.json<ApiResponse<Content>>({
        success: true,
        data: generateContent({ id: contentId as string, ...updates })
      })
    );
  }),

  // Delete content
  rest.delete('/api/content/:contentId', (req, res, ctx) => {
    return res(
      ctx.json<ApiResponse<null>>({
        success: true,
        data: null
      })
    );
  }),

  // Upload content file
  rest.post('/api/content/upload', (req, res, ctx) => {
    return res(
      ctx.delay(3000), // Simulate file upload
      ctx.json<ApiResponse<{ url: string; fileId: string }>>({
        success: true,
        data: {
          url: '/uploads/mock-file-url.mp3',
          fileId: 'file-123456'
        }
      })
    );
  })
];

// Analytics Handlers
const analyticsHandlers = [
  // Get analytics overview
  rest.get('/api/analytics/overview', (req, res, ctx) => {
    const timeRange = req.url.searchParams.get('timeRange') || '30d';
    
    return res(
      ctx.delay(800),
      ctx.json<ApiResponse<Analytics>>({
        success: true,
        data: generateAnalytics()
      })
    );
  }),

  // Get content performance
  rest.get('/api/analytics/content/:contentId', (req, res, ctx) => {
    const { contentId } = req.params;
    
    return res(
      ctx.json<ApiResponse<{
        views: Array<{ date: string; count: number }>;
        engagement: Array<{ date: string; rate: number }>;
        revenue: Array<{ date: string; amount: number }>;
      }>>({
        success: true,
        data: {
          views: Array.from({ length: 30 }, (_, i) => ({
            date: new Date(Date.now() - (29 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
            count: Math.floor(Math.random() * 1000) + 100
          })),
          engagement: Array.from({ length: 30 }, (_, i) => ({
            date: new Date(Date.now() - (29 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
            rate: Math.random() * 100
          })),
          revenue: Array.from({ length: 30 }, (_, i) => ({
            date: new Date(Date.now() - (29 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
            amount: Math.random() * 50
          }))
        }
      })
    );
  })
];

// Collaboration Handlers
const collaborationHandlers = [
  // Get collaboration requests
  rest.get('/api/collaborations', (req, res, ctx) => {
    const status = req.url.searchParams.get('status');
    
    const collaborations = Array.from({ length: 5 }, (_, i) => ({
      id: `collab-${i + 1}`,
      title: `Collaboration Request ${i + 1}`,
      description: `Exciting collaboration opportunity ${i + 1}`,
      requester: generateUser({ username: `requester_${i + 1}` }),
      status: status || 'pending',
      createdAt: new Date().toISOString(),
      projectDetails: {
        type: 'music_production',
        budget: 500 + i * 100,
        deadline: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString()
      }
    }));

    return res(
      ctx.json<ApiResponse<typeof collaborations>>({
        success: true,
        data: collaborations
      })
    );
  }),

  // Create collaboration request
  rest.post('/api/collaborations', async (req, res, ctx) => {
    const collaborationData = await req.json();
    
    return res(
      ctx.status(201),
      ctx.json<ApiResponse<{
        id: string;
        title: string;
        status: string;
      }>>({
        success: true,
        data: {
          id: 'new-collab-123',
          title: collaborationData.title,
          status: 'pending'
        }
      })
    );
  }),

  // Respond to collaboration
  rest.post('/api/collaborations/:collabId/respond', async (req, res, ctx) => {
    const { collabId } = req.params;
    const { action } = await req.json();
    
    return res(
      ctx.json<ApiResponse<{ status: string }>>({
        success: true,
        data: {
          status: action === 'accept' ? 'accepted' : 'declined'
        }
      })
    );
  })
];

// Error Simulation Handlers
const errorHandlers = [
  // Simulate server error
  rest.get('/api/error/server', (req, res, ctx) => {
    return res(
      ctx.status(500),
      ctx.json<ApiResponse<null>>({
        success: false,
        error: 'Internal server error'
      })
    );
  }),

  // Simulate network timeout
  rest.get('/api/error/timeout', (req, res, ctx) => {
    return res(
      ctx.delay('infinite') // This will cause a timeout
    );
  }),

  // Simulate rate limiting
  rest.get('/api/error/rate-limit', (req, res, ctx) => {
    return res(
      ctx.status(429),
      ctx.json<ApiResponse<null>>({
        success: false,
        error: 'Too many requests'
      })
    );
  })
];

// ==================== HANDLERS COLLECTION ====================

export const handlers = [
  ...authHandlers,
  ...userHandlers,
  ...contentHandlers,
  ...analyticsHandlers,
  ...collaborationHandlers,
  ...errorHandlers
];

// ==================== MSW SETUP ====================

// Browser setup for development/storybook
export const worker = setupWorker(...handlers);

// Node.js setup for testing
export const server = setupServer(...handlers);

// ==================== HELPER FUNCTIONS ====================

/**
 * Start MSW for browser environment
 */
export const startMSW = async () => {
  if (typeof window !== 'undefined') {
    return worker.start({
      onUnhandledRequest: 'warn'
    });
  }
};

/**
 * Stop MSW
 */
export const stopMSW = () => {
  if (typeof window !== 'undefined') {
    worker.stop();
  } else {
    server.close();
  }
};

/**
 * Reset handlers to default state
 */
export const resetMSW = () => {
  if (typeof window !== 'undefined') {
    worker.resetHandlers();
  } else {
    server.resetHandlers();
  }
};

/**
 * Add runtime handler
 */
export const addHandler = (...newHandlers: Parameters<typeof rest.get>[]) => {
  if (typeof window !== 'undefined') {
    worker.use(...newHandlers);
  } else {
    server.use(...newHandlers);
  }
};

// ==================== SCENARIO HELPERS ====================

/**
 * Configure MSW for specific test scenarios
 */
export const scenarios = {
  // Successful operations
  success: () => {
    resetMSW();
  },

  // Network errors
  networkError: () => {
    addHandler(
      rest.get('/api/*', (req, res, ctx) => {
        return res.networkError('Network connection failed');
      }),
      rest.post('/api/*', (req, res, ctx) => {
        return res.networkError('Network connection failed');
      })
    );
  },

  // Slow responses
  slowNetwork: () => {
    addHandler(
      rest.get('/api/*', (req, res, ctx) => {
        return res(
          ctx.delay(5000),
          ctx.json({ success: true, data: null })
        );
      })
    );
  },

  // Authentication errors
  authError: () => {
    addHandler(
      rest.get('/api/*', (req, res, ctx) => {
        return res(
          ctx.status(401),
          ctx.json<ApiResponse<null>>({
            success: false,
            error: 'Authentication required'
          })
        );
      })
    );
  },

  // Empty responses
  emptyData: () => {
    addHandler(
      rest.get('/api/content', (req, res, ctx) => {
        return res(
          ctx.json<ApiResponse<{ content: Content[]; total: number; page: number }>>({
            success: true,
            data: {
              content: [],
              total: 0,
              page: 1
            }
          })
        );
      })
    );
  }
};

// ==================== EXPORTS ====================

export default {
  handlers,
  worker,
  server,
  startMSW,
  stopMSW,
  resetMSW,
  addHandler,
  scenarios,
  // Mock data generators
  generateUser,
  generateContent,
  generateAnalytics
};

// Type exports for external use
export type {
  User,
  Content,
  Analytics,
  ApiResponse
};