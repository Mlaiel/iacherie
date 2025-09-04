/**
 * HTTP Client Library
 */

interface RequestConfig {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  headers?: Record<string, string>;
  body?: any;
  timeout?: number;
}

interface Response<T = any> {
  data: T;
  status: number;
  headers: Headers;
}

class HTTPClient {
  private baseURL: string;
  private defaultHeaders: Record<string, string>;

  constructor(baseURL: string = '', defaultHeaders: Record<string, string> = {}) {
    this.baseURL = baseURL;
    this.defaultHeaders = defaultHeaders;
  }

  private async request<T>(endpoint: string, config: RequestConfig = {}): Promise<Response<T>> {
    const url = `${this.baseURL}${endpoint}`;
    const headers = { ...this.defaultHeaders, ...config.headers };
    
    const controller = new AbortController();
    const timeoutId = config.timeout 
      ? setTimeout(() => controller.abort(), config.timeout)
      : null;

    try {
      const response = await fetch(url, {
        method: config.method || 'GET',
        headers,
        body: config.body ? JSON.stringify(config.body) : undefined,
        signal: controller.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP Error: ${response.status}`);
      }

      const data = await response.json();
      
      return {
        data,
        status: response.status,
        headers: response.headers,
      };
    } finally {
      if (timeoutId) clearTimeout(timeoutId);
    }
  }

  get<T>(endpoint: string, config?: Omit<RequestConfig, 'method' | 'body'>) {
    return this.request<T>(endpoint, { ...config, method: 'GET' });
  }

  post<T>(endpoint: string, body?: any, config?: Omit<RequestConfig, 'method' | 'body'>) {
    return this.request<T>(endpoint, { ...config, method: 'POST', body });
  }

  put<T>(endpoint: string, body?: any, config?: Omit<RequestConfig, 'method' | 'body'>) {
    return this.request<T>(endpoint, { ...config, method: 'PUT', body });
  }

  delete<T>(endpoint: string, config?: Omit<RequestConfig, 'method' | 'body'>) {
    return this.request<T>(endpoint, { ...config, method: 'DELETE' });
  }
}

export { HTTPClient };
export default HTTPClient;
