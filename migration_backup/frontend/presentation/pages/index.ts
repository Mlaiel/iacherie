/**
 * 📄 Pages System Enterprise - Dynamic Routing & Page Management
 * 
 * @fileoverview Advanced page routing and component management system
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @copyright 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
 */

import { ComponentType, ReactNode } from 'react';

export interface PageConfig {
  id: string;
  path: string;
  title: string;
  description?: string;
  component: ComponentType<any>;
  layout?: ComponentType<any>;
  middleware?: PageMiddleware[];
  meta?: PageMeta;
  permissions?: string[];
  cache?: {
    enabled: boolean;
    duration: number; // seconds
    key?: string;
  };
}

export interface PageMeta {
  title?: string;
  description?: string;
  keywords?: string[];
  ogTitle?: string;
  ogDescription?: string;
  ogImage?: string;
  canonical?: string;
  robots?: string;
}

export interface PageMiddleware {
  name: string;
  execute: (context: PageContext) => Promise<PageMiddlewareResult>;
  priority: number;
}

export interface PageMiddlewareResult {
  continue: boolean;
  redirect?: string;
  data?: any;
  error?: string;
}

export interface PageContext {
  path: string;
  query: Record<string, string>;
  user?: any;
  session?: any;
  headers: Record<string, string>;
  timestamp: number;
}

export interface RouteMatch {
  page: PageConfig;
  params: Record<string, string>;
  query: Record<string, string>;
}

export interface PageLoadResult {
  component: ComponentType<any>;
  props: any;
  meta: PageMeta;
  error?: string;
}

export class PageSystem {
  private pages: Map<string, PageConfig> = new Map();
  private routes: Array<{ pattern: RegExp; config: PageConfig }> = [];
  private cache: Map<string, { data: PageLoadResult; expires: number }> = new Map();
  private middleware: PageMiddleware[] = [];

  /**
   * Register a new page
   */
  registerPage(config: PageConfig): void {
    this.pages.set(config.id, config);
    
    // Create route pattern for path matching
    const pattern = this.createRoutePattern(config.path);
    this.routes.push({ pattern, config });
    
    // Sort routes by specificity (more specific routes first)
    this.routes.sort((a, b) => {
      const aSpecificity = this.calculateSpecificity(a.config.path);
      const bSpecificity = this.calculateSpecificity(b.config.path);
      return bSpecificity - aSpecificity;
    });
  }

  /**
   * Register global middleware
   */
  registerMiddleware(middleware: PageMiddleware): void {
    this.middleware.push(middleware);
    this.middleware.sort((a, b) => a.priority - b.priority);
  }

  /**
   * Match a path to a page configuration
   */
  matchRoute(path: string): RouteMatch | null {
    for (const route of this.routes) {
      const match = route.pattern.exec(path);
      if (match) {
        const params = this.extractParams(route.config.path, match);
        const query = this.extractQuery(path);
        
        return {
          page: route.config,
          params,
          query
        };
      }
    }
    return null;
  }

  /**
   * Load a page with all processing
   */
  async loadPage(path: string, context: Partial<PageContext> = {}): Promise<PageLoadResult> {
    const match = this.matchRoute(path);
    if (!match) {
      return {
        component: this.getNotFoundComponent(),
        props: {},
        meta: { title: 'Page Not Found' },
        error: 'Page not found'
      };
    }

    const fullContext: PageContext = {
      path,
      query: match.query,
      headers: {},
      timestamp: Date.now(),
      ...context
    };

    try {
      // Check cache first
      const cached = this.getCachedPage(match.page, fullContext);
      if (cached) {
        return cached;
      }

      // Execute middleware
      const middlewareResult = await this.executeMiddleware(match.page, fullContext);
      if (!middlewareResult.continue) {
        if (middlewareResult.redirect) {
          return this.createRedirectResult(middlewareResult.redirect);
        }
        return {
          component: this.getErrorComponent(),
          props: { error: middlewareResult.error },
          meta: { title: 'Error' },
          error: middlewareResult.error
        };
      }

      // Load the page component
      const result = await this.loadPageComponent(match.page, match.params, fullContext, middlewareResult.data);
      
      // Cache the result if caching is enabled
      if (match.page.cache?.enabled) {
        this.cachePageResult(match.page, fullContext, result);
      }

      return result;
    } catch (error: any) {
      return {
        component: this.getErrorComponent(),
        props: { error: error.message },
        meta: { title: 'Error' },
        error: error.message
      };
    }
  }

  /**
   * Get all registered pages
   */
  getPages(): PageConfig[] {
    return Array.from(this.pages.values());
  }

  /**
   * Get page by ID
   */
  getPageById(id: string): PageConfig | undefined {
    return this.pages.get(id);
  }

  /**
   * Generate page URL with parameters
   */
  generateURL(pageId: string, params: Record<string, string> = {}): string {
    const page = this.pages.get(pageId);
    if (!page) {
      throw new Error(`Page not found: ${pageId}`);
    }

    let url = page.path;
    for (const [key, value] of Object.entries(params)) {
      url = url.replace(`:${key}`, encodeURIComponent(value));
    }

    return url;
  }

  /**
   * Preload a page for performance
   */
  async preloadPage(pageId: string): Promise<void> {
    const page = this.pages.get(pageId);
    if (!page) return;

    try {
      // Preload the component if it's a dynamic import
      if (typeof page.component === 'function') {
        await page.component;
      }
    } catch (error) {
      console.warn(`Failed to preload page: ${pageId}`, error);
    }
  }

  /**
   * Clear page cache
   */
  clearCache(pageId?: string): void {
    if (pageId) {
      const page = this.pages.get(pageId);
      if (page) {
        for (const key of this.cache.keys()) {
          if (key.startsWith(`${page.id}:`)) {
            this.cache.delete(key);
          }
        }
      }
    } else {
      this.cache.clear();
    }
  }

  /**
   * Private helper methods
   */
  private createRoutePattern(path: string): RegExp {
    // Convert Next.js-style paths to regex patterns
    const pattern = path
      .replace(/\[([^\]]+)\]/g, '([^/]+)') // Dynamic segments
      .replace(/\*/g, '.*'); // Catch-all segments
    
    return new RegExp(`^${pattern}$`);
  }

  private calculateSpecificity(path: string): number {
    // More specific paths (fewer dynamic segments) get higher scores
    const segments = path.split('/').filter(s => s.length > 0);
    let score = segments.length * 10;
    
    for (const segment of segments) {
      if (segment.startsWith(':') || segment.includes('[')) {
        score -= 5; // Dynamic segments are less specific
      } else {
        score += 5; // Static segments are more specific
      }
    }
    
    return score;
  }

  private extractParams(pathPattern: string, match: RegExpExecArray): Record<string, string> {
    const params: Record<string, string> = {};
    const segments = pathPattern.split('/').filter(s => s.length > 0);
    let paramIndex = 1;

    for (const segment of segments) {
      if (segment.startsWith(':')) {
        const paramName = segment.substring(1);
        params[paramName] = decodeURIComponent(match[paramIndex] || '');
        paramIndex++;
      } else if (segment.includes('[')) {
        const paramName = segment.replace(/[\[\]]/g, '');
        params[paramName] = decodeURIComponent(match[paramIndex] || '');
        paramIndex++;
      }
    }

    return params;
  }

  private extractQuery(path: string): Record<string, string> {
    const query: Record<string, string> = {};
    const queryStart = path.indexOf('?');
    
    if (queryStart !== -1) {
      const queryString = path.substring(queryStart + 1);
      const pairs = queryString.split('&');
      
      for (const pair of pairs) {
        const [key, value] = pair.split('=');
        if (key) {
          query[decodeURIComponent(key)] = decodeURIComponent(value || '');
        }
      }
    }
    
    return query;
  }

  private async executeMiddleware(page: PageConfig, context: PageContext): Promise<PageMiddlewareResult> {
    const allMiddleware = [...this.middleware, ...(page.middleware || [])];
    let combinedData: any = {};

    for (const middleware of allMiddleware) {
      try {
        const result = await middleware.execute(context);
        if (!result.continue) {
          return result;
        }
        if (result.data) {
          combinedData = { ...combinedData, ...result.data };
        }
      } catch (error: any) {
        return {
          continue: false,
          error: `Middleware error: ${error.message}`
        };
      }
    }

    return {
      continue: true,
      data: combinedData
    };
  }

  private async loadPageComponent(
    page: PageConfig,
    params: Record<string, string>,
    context: PageContext,
    middlewareData: any
  ): Promise<PageLoadResult> {
    const props = {
      params,
      query: context.query,
      ...middlewareData
    };

    const meta: PageMeta = {
      title: page.title,
      description: page.description,
      ...page.meta
    };

    return {
      component: page.component,
      props,
      meta
    };
  }

  private getCachedPage(page: PageConfig, context: PageContext): PageLoadResult | null {
    if (!page.cache?.enabled) return null;

    const cacheKey = this.generateCacheKey(page, context);
    const cached = this.cache.get(cacheKey);
    
    if (cached && cached.expires > Date.now()) {
      return cached.data;
    }

    return null;
  }

  private cachePageResult(page: PageConfig, context: PageContext, result: PageLoadResult): void {
    if (!page.cache?.enabled) return;

    const cacheKey = this.generateCacheKey(page, context);
    const expires = Date.now() + (page.cache.duration * 1000);
    
    this.cache.set(cacheKey, { data: result, expires });
  }

  private generateCacheKey(page: PageConfig, context: PageContext): string {
    const baseKey = page.cache?.key || `${page.id}:${context.path}`;
    const queryKey = Object.keys(context.query).sort().map(k => `${k}=${context.query[k]}`).join('&');
    return `${baseKey}?${queryKey}`;
  }

  private createRedirectResult(redirectPath: string): PageLoadResult {
    return {
      component: this.getRedirectComponent(),
      props: { to: redirectPath },
      meta: { title: 'Redirecting...' }
    };
  }

  private getNotFoundComponent(): ComponentType<any> {
    return () => null; // Would return actual 404 component
  }

  private getErrorComponent(): ComponentType<any> {
    return () => null; // Would return actual error component
  }

  private getRedirectComponent(): ComponentType<any> {
    return () => null; // Would return actual redirect component
  }
}

// Singleton instance
export const pageSystem = new PageSystem();

// React hooks for pages
export function usePageSystem() {
  const loadPage = async (path: string, context?: Partial<PageContext>) => {
    return pageSystem.loadPage(path, context);
  };

  const generateURL = (pageId: string, params?: Record<string, string>) => {
    return pageSystem.generateURL(pageId, params);
  };

  const preloadPage = (pageId: string) => {
    return pageSystem.preloadPage(pageId);
  };

  return { loadPage, generateURL, preloadPage };
}

export function usePage(pageId: string) {
  const page = pageSystem.getPageById(pageId);
  
  const navigate = (params?: Record<string, string>) => {
    if (page) {
      const url = pageSystem.generateURL(pageId, params);
      // Would integrate with router here
      console.log(`Navigate to: ${url}`);
    }
  };

  return { page, navigate };
}

export default PageSystem;