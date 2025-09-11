/**
 * 🎨 Layout System Enterprise - Dynamic Layout Management
 * 
 * @fileoverview Advanced layout system for responsive and adaptive UI
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @copyright 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
 */

import { ComponentType, ReactNode } from 'react';

export interface LayoutConfig {
  id: string;
  name: string;
  component: ComponentType<LayoutProps>;
  breakpoints?: ResponsiveBreakpoints;
  variants?: LayoutVariant[];
  slots?: LayoutSlot[];
  metadata?: LayoutMetadata;
  dependencies?: string[];
}

export interface LayoutProps {
  children: ReactNode;
  variant?: string;
  responsive?: boolean;
  theme?: string;
  data?: any;
}

export interface ResponsiveBreakpoints {
  mobile: number;    // max width for mobile
  tablet: number;    // max width for tablet
  desktop: number;   // min width for desktop
  largeDesktop: number; // min width for large desktop
}

export interface LayoutVariant {
  id: string;
  name: string;
  description?: string;
  conditions?: LayoutCondition[];
  overrides?: Partial<LayoutConfig>;
}

export interface LayoutCondition {
  type: 'viewport' | 'user' | 'device' | 'feature' | 'time';
  operator: 'equals' | 'not_equals' | 'greater_than' | 'less_than' | 'contains';
  value: any;
}

export interface LayoutSlot {
  id: string;
  name: string;
  required: boolean;
  defaultContent?: ReactNode;
  constraints?: {
    maxWidth?: number;
    maxHeight?: number;
    minWidth?: number;
    minHeight?: number;
  };
}

export interface LayoutMetadata {
  author: string;
  version: string;
  description: string;
  tags: string[];
  createdAt: number;
  updatedAt: number;
}

export interface ViewportInfo {
  width: number;
  height: number;
  deviceType: 'mobile' | 'tablet' | 'desktop' | 'large-desktop';
  orientation: 'portrait' | 'landscape';
  pixelRatio: number;
}

export interface LayoutContext {
  viewport: ViewportInfo;
  user?: any;
  theme: string;
  features: string[];
  timestamp: number;
}

export interface LayoutRenderResult {
  component: ComponentType<LayoutProps>;
  props: LayoutProps;
  variant?: LayoutVariant;
  optimizations: LayoutOptimization[];
}

export interface LayoutOptimization {
  type: 'performance' | 'accessibility' | 'seo' | 'responsive';
  applied: string[];
  skipped: string[];
  reason?: string;
}

export class LayoutManager {
  private layouts: Map<string, LayoutConfig> = new Map();
  private activeLayout: string | null = null;
  private context: LayoutContext | null = null;
  private cache: Map<string, LayoutRenderResult> = new Map();

  /**
   * Register a new layout
   */
  registerLayout(config: LayoutConfig): void {
    this.layouts.set(config.id, config);
    console.log(`[Layout] Registered layout: ${config.name} (${config.id})`);
  }

  /**
   * Set the current layout context
   */
  setContext(context: LayoutContext): void {
    this.context = context;
    this.clearCache(); // Clear cache when context changes
  }

  /**
   * Render a layout with optimizations
   */
  renderLayout(layoutId: string, children: ReactNode, options: {
    variant?: string;
    responsive?: boolean;
    theme?: string;
    data?: any;
  } = {}): LayoutRenderResult {
    const layout = this.layouts.get(layoutId);
    if (!layout) {
      throw new Error(`Layout not found: ${layoutId}`);
    }

    // Check cache first
    const cacheKey = this.generateCacheKey(layoutId, options);
    const cached = this.cache.get(cacheKey);
    if (cached) {
      return { ...cached, props: { ...cached.props, children } };
    }

    const context = this.context || this.getDefaultContext();
    
    // Find the best variant for current context
    const variant = this.selectVariant(layout, context, options.variant);
    
    // Apply optimizations
    const optimizations = this.applyOptimizations(layout, context, variant);
    
    // Build final props
    const props: LayoutProps = {
      children,
      variant: variant?.id,
      responsive: options.responsive !== false,
      theme: options.theme || context.theme,
      data: options.data
    };

    const result: LayoutRenderResult = {
      component: layout.component,
      props,
      variant,
      optimizations
    };

    // Cache the result
    this.cache.set(cacheKey, result);
    
    return result;
  }

  /**
   * Get responsive layout for current viewport
   */
  getResponsiveLayout(layoutId: string, children: ReactNode): LayoutRenderResult {
    const layout = this.layouts.get(layoutId);
    if (!layout) {
      throw new Error(`Layout not found: ${layoutId}`);
    }

    const context = this.context || this.getDefaultContext();
    const breakpoints = layout.breakpoints || this.getDefaultBreakpoints();
    
    // Determine responsive variant based on viewport
    let responsiveVariant = 'desktop';
    if (context.viewport.width <= breakpoints.mobile) {
      responsiveVariant = 'mobile';
    } else if (context.viewport.width <= breakpoints.tablet) {
      responsiveVariant = 'tablet';
    } else if (context.viewport.width >= breakpoints.largeDesktop) {
      responsiveVariant = 'large-desktop';
    }

    return this.renderLayout(layoutId, children, {
      variant: responsiveVariant,
      responsive: true
    });
  }

  /**
   * Optimize layout for performance
   */
  optimizeLayout(layoutId: string): LayoutOptimization[] {
    const layout = this.layouts.get(layoutId);
    if (!layout) {
      return [];
    }

    const optimizations: LayoutOptimization[] = [];
    
    // Performance optimizations
    const performanceOpt: LayoutOptimization = {
      type: 'performance',
      applied: [],
      skipped: []
    };
    
    // Check for lazy loading opportunities
    if (layout.slots && layout.slots.length > 3) {
      performanceOpt.applied.push('lazy-load-slots');
    }
    
    // Check for code splitting opportunities
    if (layout.variants && layout.variants.length > 2) {
      performanceOpt.applied.push('code-splitting');
    }
    
    optimizations.push(performanceOpt);

    // Accessibility optimizations
    const a11yOpt: LayoutOptimization = {
      type: 'accessibility',
      applied: ['aria-labels', 'keyboard-navigation'],
      skipped: []
    };
    optimizations.push(a11yOpt);

    // Responsive optimizations
    const responsiveOpt: LayoutOptimization = {
      type: 'responsive',
      applied: ['fluid-typography', 'flexible-grids'],
      skipped: []
    };
    optimizations.push(responsiveOpt);

    return optimizations;
  }

  /**
   * Get all registered layouts
   */
  getLayouts(): LayoutConfig[] {
    return Array.from(this.layouts.values());
  }

  /**
   * Get layout by ID
   */
  getLayoutById(layoutId: string): LayoutConfig | undefined {
    return this.layouts.get(layoutId);
  }

  /**
   * Switch to a different layout
   */
  switchLayout(layoutId: string): void {
    if (!this.layouts.has(layoutId)) {
      throw new Error(`Layout not found: ${layoutId}`);
    }
    
    this.activeLayout = layoutId;
    this.clearCache();
    console.log(`[Layout] Switched to layout: ${layoutId}`);
  }

  /**
   * Get current active layout
   */
  getActiveLayout(): string | null {
    return this.activeLayout;
  }

  /**
   * Clear layout cache
   */
  clearCache(): void {
    this.cache.clear();
  }

  /**
   * Private helper methods
   */
  private selectVariant(
    layout: LayoutConfig,
    context: LayoutContext,
    preferredVariant?: string
  ): LayoutVariant | undefined {
    if (!layout.variants) return undefined;

    // If a specific variant is requested, try to use it
    if (preferredVariant) {
      const variant = layout.variants.find(v => v.id === preferredVariant);
      if (variant && this.checkConditions(variant.conditions || [], context)) {
        return variant;
      }
    }

    // Find the best matching variant based on conditions
    for (const variant of layout.variants) {
      if (this.checkConditions(variant.conditions || [], context)) {
        return variant;
      }
    }

    // Return first variant as fallback
    return layout.variants[0];
  }

  private checkConditions(conditions: LayoutCondition[], context: LayoutContext): boolean {
    return conditions.every(condition => {
      switch (condition.type) {
        case 'viewport':
          return this.checkViewportCondition(condition, context.viewport);
        case 'device':
          return this.checkDeviceCondition(condition, context.viewport);
        case 'user':
          return this.checkUserCondition(condition, context.user);
        case 'feature':
          return this.checkFeatureCondition(condition, context.features);
        case 'time':
          return this.checkTimeCondition(condition, context.timestamp);
        default:
          return true;
      }
    });
  }

  private checkViewportCondition(condition: LayoutCondition, viewport: ViewportInfo): boolean {
    switch (condition.operator) {
      case 'greater_than':
        return viewport.width > condition.value;
      case 'less_than':
        return viewport.width < condition.value;
      case 'equals':
        return viewport.deviceType === condition.value;
      default:
        return true;
    }
  }

  private checkDeviceCondition(condition: LayoutCondition, viewport: ViewportInfo): boolean {
    switch (condition.operator) {
      case 'equals':
        return viewport.deviceType === condition.value;
      case 'not_equals':
        return viewport.deviceType !== condition.value;
      default:
        return true;
    }
  }

  private checkUserCondition(condition: LayoutCondition, user: any): boolean {
    if (!user) return false;
    
    switch (condition.operator) {
      case 'equals':
        return user[condition.value.key] === condition.value.value;
      case 'contains':
        return user[condition.value.key]?.includes(condition.value.value);
      default:
        return true;
    }
  }

  private checkFeatureCondition(condition: LayoutCondition, features: string[]): boolean {
    switch (condition.operator) {
      case 'contains':
        return features.includes(condition.value);
      case 'not_equals':
        return !features.includes(condition.value);
      default:
        return true;
    }
  }

  private checkTimeCondition(condition: LayoutCondition, timestamp: number): boolean {
    const hour = new Date(timestamp).getHours();
    
    switch (condition.operator) {
      case 'greater_than':
        return hour > condition.value;
      case 'less_than':
        return hour < condition.value;
      default:
        return true;
    }
  }

  private applyOptimizations(
    layout: LayoutConfig,
    context: LayoutContext,
    variant?: LayoutVariant
  ): LayoutOptimization[] {
    const optimizations: LayoutOptimization[] = [];

    // Mobile optimizations
    if (context.viewport.deviceType === 'mobile') {
      optimizations.push({
        type: 'performance',
        applied: ['reduce-animations', 'compress-images'],
        skipped: []
      });
    }

    // Accessibility optimizations
    optimizations.push({
      type: 'accessibility',
      applied: ['focus-management', 'screen-reader-support'],
      skipped: []
    });

    return optimizations;
  }

  private getDefaultContext(): LayoutContext {
    return {
      viewport: {
        width: 1200,
        height: 800,
        deviceType: 'desktop',
        orientation: 'landscape',
        pixelRatio: 1
      },
      theme: 'default',
      features: [],
      timestamp: Date.now()
    };
  }

  private getDefaultBreakpoints(): ResponsiveBreakpoints {
    return {
      mobile: 768,
      tablet: 1024,
      desktop: 1200,
      largeDesktop: 1920
    };
  }

  private generateCacheKey(layoutId: string, options: any): string {
    return `${layoutId}:${JSON.stringify(options)}:${this.context?.viewport.width || 0}`;
  }
}

// Singleton instance
export const layoutManager = new LayoutManager();

// React hooks for layouts
export function useLayoutManager() {
  const renderLayout = (layoutId: string, children: ReactNode, options?: any) => {
    return layoutManager.renderLayout(layoutId, children, options);
  };

  const getResponsiveLayout = (layoutId: string, children: ReactNode) => {
    return layoutManager.getResponsiveLayout(layoutId, children);
  };

  const switchLayout = (layoutId: string) => {
    layoutManager.switchLayout(layoutId);
  };

  return { renderLayout, getResponsiveLayout, switchLayout };
}

export function useResponsiveLayout() {
  const getViewportInfo = (): ViewportInfo => {
    if (typeof window === 'undefined') {
      return {
        width: 1200,
        height: 800,
        deviceType: 'desktop',
        orientation: 'landscape',
        pixelRatio: 1
      };
    }

    const width = window.innerWidth;
    const height = window.innerHeight;
    
    let deviceType: ViewportInfo['deviceType'] = 'desktop';
    if (width <= 768) deviceType = 'mobile';
    else if (width <= 1024) deviceType = 'tablet';
    else if (width >= 1920) deviceType = 'large-desktop';

    return {
      width,
      height,
      deviceType,
      orientation: width > height ? 'landscape' : 'portrait',
      pixelRatio: window.devicePixelRatio || 1
    };
  };

  const updateContext = () => {
    const viewport = getViewportInfo();
    layoutManager.setContext({
      viewport,
      theme: 'default',
      features: [],
      timestamp: Date.now()
    });
  };

  return { getViewportInfo, updateContext };
}

export default LayoutManager;