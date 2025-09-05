/**
 * API Service for Ainflue Backend
 */

const API_BASE_URL = 'http://127.0.0.1:8000';

class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request(endpoint: string, options: RequestInit = {}): Promise<any> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const defaultOptions: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, defaultOptions);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      }
      
      return await response.text();
    } catch (error) {
      console.error(`API Request failed for ${endpoint}:`, error);
      throw error;
    }
  }

  // Health Check
  async getHealth(): Promise<any> {
    return this.request('/health');
  }

  // Content Management
  async getContent(): Promise<any> {
    return this.request('/api/v1/content');
  }

  async uploadContent(file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    
    return this.request('/api/v1/content/upload', {
      method: 'POST',
      body: formData,
      headers: {}, // Remove Content-Type header to let browser set it with boundary
    });
  }

  // AI Agents
  async getAgents(): Promise<any> {
    return this.request('/api/v1/agents');
  }

  async runAgent(agentId: string, data?: any): Promise<any> {
    return this.request(`/api/v1/agents/${agentId}/run`, {
      method: 'POST',
      body: JSON.stringify(data || {}),
    });
  }

  // Crawlers
  async getCrawlers(): Promise<any> {
    return this.request('/api/v1/crawlers');
  }

  async runCrawler(crawlerId: string, data?: any): Promise<any> {
    return this.request(`/api/v1/crawlers/${crawlerId}/run`, {
      method: 'POST',
      body: JSON.stringify(data || {}),
    });
  }

  // Violations
  async getViolations(): Promise<any> {
    return this.request('/api/v1/violations');
  }

  // Analytics
  async getRevenue(): Promise<any> {
    return this.request('/api/v1/analytics/revenue');
  }

  async getMetrics(): Promise<any> {
    return this.request('/api/v1/analytics/metrics');
  }

  // Authentication
  async login(email: string, password: string): Promise<any> {
    return this.request('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  async logout(): Promise<any> {
    return this.request('/api/v1/auth/logout', {
      method: 'POST',
    });
  }

  // Protection
  async protectContent(contentId: string, protectionLevel: string): Promise<any> {
    return this.request(`/api/v1/content/${contentId}/protect`, {
      method: 'POST',
      body: JSON.stringify({ protection_level: protectionLevel }),
    });
  }

  // Monitoring
  async getMonitoringStatus(): Promise<any> {
    return this.request('/api/v1/monitoring/status');
  }

  // Alerts
  async getAlerts(): Promise<any> {
    return this.request('/api/v1/alerts');
  }

  // Fingerprinting
  async generateFingerprint(contentId: string): Promise<any> {
    return this.request(`/api/v1/content/${contentId}/fingerprint`, {
      method: 'POST',
    });
  }

  // Earnings
  async getEarnings(): Promise<any> {
    return this.request('/api/v1/analytics/earnings');
  }
}

export const apiService = new ApiService();
