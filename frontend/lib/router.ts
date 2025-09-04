/**
 * Simple Router Library
 */

interface Route {
  path: string;
  handler: (params: Record<string, string>) => void;
}

class Router {
  private routes: Route[] = [];
  private currentPath: string = '';

  constructor() {
    window.addEventListener('popstate', () => this.handleRoute());
    this.handleRoute();
  }

  addRoute(path: string, handler: (params: Record<string, string>) => void): void {
    this.routes.push({ path, handler });
  }

  navigate(path: string): void {
    window.history.pushState({}, '', path);
    this.handleRoute();
  }

  replace(path: string): void {
    window.history.replaceState({}, '', path);
    this.handleRoute();
  }

  back(): void {
    window.history.back();
  }

  forward(): void {
    window.history.forward();
  }

  private handleRoute(): void {
    const path = window.location.pathname;
    this.currentPath = path;

    const matchedRoute = this.findMatchingRoute(path);
    if (matchedRoute) {
      const params = this.extractParams(matchedRoute.route.path, path);
      matchedRoute.route.handler(params);
    }
  }

  private findMatchingRoute(path: string): { route: Route; params: Record<string, string> } | null {
    for (const route of this.routes) {
      const params = this.extractParams(route.path, path);
      if (params !== null) {
        return { route, params };
      }
    }
    return null;
  }

  private extractParams(routePath: string, actualPath: string): Record<string, string> | null {
    const routeParts = routePath.split('/').filter(Boolean);
    const actualParts = actualPath.split('/').filter(Boolean);

    if (routeParts.length !== actualParts.length) {
      return null;
    }

    const params: Record<string, string> = {};

    for (let i = 0; i < routeParts.length; i++) {
      const routePart = routeParts[i];
      const actualPart = actualParts[i];

      if (routePart.startsWith(':')) {
        const paramName = routePart.substring(1);
        params[paramName] = actualPart;
      } else if (routePart !== actualPart) {
        return null;
      }
    }

    return params;
  }

  getCurrentPath(): string {
    return this.currentPath;
  }

  getRoutes(): Route[] {
    return [...this.routes];
  }
}

export { Router };
export default Router;
