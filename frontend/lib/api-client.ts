/**
 * 🎯 API CLIENT ENTERPRISE - ARCHITECTURE CONSOLIDÉE
 * Client API unifié pour les 57 modules backend
 * 
 * @author Fahed Mlaiel - Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + DevOps
 * @date 25 Septembre 2025
 */

'use client';

// Configuration API centralisée
export const API_CONFIG = {
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  timeout: 10000,
  retryCount: 3,
  retryDelay: 1000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  }
} as const;

// Types centralisés pour tous les modules
export interface APIResponse<T = any> {
  data: T | null;
  loading: boolean;
  error: string | null;
  status: number | null;
  timestamp?: string;
}

export interface ModuleStatus {
  id: string;
  name: string;
  status: 'active' | 'inactive' | 'error' | 'maintenance';
  health: number; // 0-100
  uptime: string;
  lastUpdate: string;
  services: number;
  apiEndpoint: string;
}

export interface ServiceMetrics {
  totalRequests: number;
  successRate: number;
  avgResponseTime: number;
  errorRate: number;
  activeConnections: number;
}

// API Client Enterprise Class
export class EnterpriseAPIClient {
  private baseURL: string;
  private headers: Record<string, string>;
  private timeout: number;

  constructor(config: typeof API_CONFIG = API_CONFIG) {
    this.baseURL = config.baseURL;
    this.headers = { ...config.headers };
    this.timeout = config.timeout;
  }

  // Authentification
  setAuthToken(token: string): void {
    this.headers['Authorization'] = `Bearer ${token}`;
  }

  // Méthode GET générique
  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>('GET', endpoint);
  }

  // Méthode POST générique
  async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>('POST', endpoint, data);
  }

  // Méthode PUT générique
  async put<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>('PUT', endpoint, data);
  }

  // Méthode DELETE générique
  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>('DELETE', endpoint);
  }

  // Méthode de requête centrale avec retry logic
  private async request<T>(method: string, endpoint: string, data?: any): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const options: RequestInit = {
      method,
      headers: this.headers,
      signal: AbortSignal.timeout(this.timeout),
    };

    if (data && (method === 'POST' || method === 'PUT')) {
      options.body = JSON.stringify(data);
    }

    try {
      const response = await fetch(url, options);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API Request failed: ${method} ${endpoint}`, error);
      throw error;
    }
  }

  // WebSocket connection pour real-time updates
  connectWebSocket(endpoint: string, onMessage: (data: any) => void): WebSocket {
    const wsURL = this.baseURL.replace('http', 'ws') + endpoint;
    const ws = new WebSocket(wsURL);

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (error) {
        console.error('WebSocket message parsing error:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    return ws;
  }
}

// Instance singleton du client API
export const apiClient = new EnterpriseAPIClient();

// API Endpoints pour tous les modules (selon architecture)
export const API_ENDPOINTS = {
  // PHASE 1: MICROSERVICES ARCHITECTURE
  AI_SERVICES: '/api/ai-services',
  ANALYTICS: '/api/analytics',
  API_GATEWAY: '/api/gateway',
  BUSINESS: '/api/business',
  COMMUNICATION: '/api/communication',
  CONTENT: '/api/content',
  DATA: '/api/data',
  FINANCIAL: '/api/financial',
  INFRASTRUCTURE: '/api/infrastructure',
  PLATFORMS: '/api/platforms',
  SECURITY: '/api/security',
  SEO: '/api/seo',
  SERVICE_MESH: '/api/service-mesh',
  TESTING: '/api/testing',
  MARKETING: '/api/marketing',

  // PHASE 2: BACKEND CORE MODULES
  CORE: '/api/core',
  DATABASE: '/api/database',
  API_LAYER: '/api/api-layer',
  AI_CORE: '/api/ai-core',
  AI_MODELS: '/api/ai-models',
  PROMPTS: '/api/prompts',
  AI_PROTECTION: '/api/ai-protection',
  BUSINESS_LOGIC: '/api/business-logic',
  MONETIZATION: '/api/monetization',
  COLLABORATION: '/api/collaboration',
  GAMIFICATION: '/api/gamification',
  AUDIO: '/api/audio',
  MEDIA: '/api/media',
  MEDIA_PROCESSING: '/api/media-processing',
  DISTRIBUTION: '/api/distribution',
  SEO_ENGINE: '/api/seo-engine',
  EDGE: '/api/edge',
  BUSINESS_INTELLIGENCE: '/api/business-intelligence',
  MONITORING: '/api/monitoring',
  COMPLIANCE: '/api/compliance',
  SECURITY_SYSTEMS: '/api/security-systems',
  BLOCKCHAIN: '/api/blockchain',
  QUANTUM: '/api/quantum',
  MOBILE: '/api/mobile',
  WEB: '/api/web',
  INTEGRATIONS: '/api/integrations',
  MARKETPLACE: '/api/marketplace',
  LANGUAGES: '/api/languages',
  AVATARS: '/api/avatars',
  COLLECTORS: '/api/collectors',
  CONFIG: '/api/config',
  CORE_SERVICES: '/api/core-services',
  ORCHESTRATION: '/api/orchestration',
  ENTERPRISE: '/api/enterprise',
  PLATFORM_CORE: '/api/platform-core',

  // PHASE 3: MODULES COMPLÉMENTAIRES
  TEMPLATES: '/api/templates',
  TEST_FRAMEWORK: '/api/test-framework',
  SCRIPTS: '/api/scripts',
  WORKFLOW: '/api/workflow',
  VALIDATION: '/api/validation',
  REPORTS: '/api/reports',
  UTILS: '/api/utils'
} as const;

// Fonctions utilitaires pour chaque module
export const ModuleAPI = {
  // Status général de tous les modules
  async getAllModulesStatus(): Promise<ModuleStatus[]> {
    return apiClient.get('/api/status/modules');
  },

  // Métriques générales
  async getSystemMetrics(): Promise<ServiceMetrics> {
    return apiClient.get('/api/metrics/system');
  },

  // Health check global
  async healthCheck(): Promise<{ status: string; modules: Record<string, boolean> }> {
    return apiClient.get('/api/health');
  }
};