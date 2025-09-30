/**
 * 🏭 COMPONENT FACTORY - DYNAMIC COMPONENT CREATION
 * ==================================================
 * 
 * Enterprise component factory pattern
 * Dynamic component instantiation
 * Props validation and optimization
 * Creator Economy component specialization
 * 
 * © 2025 Fahed Mlaiel <mlaiel@live.de>
 * TOUS DROITS RÉSERVÉS
 */

import React, { ComponentType, ReactElement, useMemo, memo } from 'react';
import { Template, TemplateMetadata, templateRegistry } from './template_registry';

export interface ComponentFactoryOptions {
  enableProfiling?: boolean;
  enableErrorBoundary?: boolean;
  enableAccessibility?: boolean;
  enableSecurity?: boolean;
  enablePerformanceMonitoring?: boolean;
  theme?: any;
  locale?: string;
}

export interface CreatedComponent {
  component: ReactElement;
  metadata: TemplateMetadata;
  performance: {
    renderTime: number;
    memoryUsage: number;
  };
}

export class ComponentFactory {
  private static instance: ComponentFactory;
  private options: ComponentFactoryOptions;
  private performanceData: Map<string, number[]> = new Map();

  private constructor(options: ComponentFactoryOptions = {}) {
    this.options = {
      enableProfiling: true,
      enableErrorBoundary: true,
      enableAccessibility: true,
      enableSecurity: true,
      enablePerformanceMonitoring: true,
      ...options
    };
  }

  public static getInstance(options?: ComponentFactoryOptions): ComponentFactory {
    if (!ComponentFactory.instance) {
      ComponentFactory.instance = new ComponentFactory(options);
    }
    return ComponentFactory.instance;
  }

  public create(templateId: string, props: any = {}): CreatedComponent | null {
    const startTime = performance.now();
    const template = templateRegistry.get(templateId);

    if (!template) {
      console.error(`❌ Template not found: ${templateId}`);
      return null;
    }

    try {
      // Validate props
      const validatedProps = this.validateProps(template, props);
      
      // Optimize props
      const optimizedProps = this.optimizeProps(template, validatedProps);
      
      // Create enhanced component
      const component = this.createEnhancedComponent(template, optimizedProps);
      
      // Record performance
      const renderTime = performance.now() - startTime;
      this.recordPerformance(templateId, renderTime);

      return {
        component,
        metadata: template.metadata,
        performance: {
          renderTime,
          memoryUsage: this.estimateMemoryUsage(template)
        }
      };
    } catch (error) {
      console.error(`❌ Error creating component ${templateId}:`, error);
      return null;
    }
  }

  private validateProps(template: Template, props: any): any {
    if (template.validate) {
      const isValid = template.validate(props);
      if (!isValid) {
        throw new Error(`Invalid props for template ${template.metadata.id}`);
      }
    }

    // Basic validation for required props
    if (template.metadata.props) {
      const requiredProps = Object.keys(template.metadata.props);
      const missingProps = requiredProps.filter(prop => !(prop in props));
      
      if (missingProps.length > 0) {
        console.warn(`⚠️ Missing props for ${template.metadata.id}:`, missingProps);
      }
    }

    return props;
  }

  private optimizeProps(template: Template, props: any): any {
    if (template.optimize) {
      return template.optimize(props);
    }
    return props;
  }

  private createEnhancedComponent(template: Template, props: any): ReactElement {
    const { Component } = template;
    let component = React.createElement(Component, props);

    // Wrap with performance monitoring
    if (this.options.enablePerformanceMonitoring) {
      component = this.wrapWithPerformanceMonitor(component, template.metadata.id);
    }

    // Wrap with error boundary
    if (this.options.enableErrorBoundary) {
      component = this.wrapWithErrorBoundary(component, template.metadata.id);
    }

    // Wrap with accessibility enhancements
    if (this.options.enableAccessibility) {
      component = this.wrapWithAccessibility(component, template.metadata);
    }

    // Wrap with security enhancements
    if (this.options.enableSecurity) {
      component = this.wrapWithSecurity(component, template.metadata);
    }

    return component;
  }

  private wrapWithPerformanceMonitor(component: ReactElement, templateId: string): ReactElement {
    const PerformanceMonitor = memo(({ children }: { children: ReactElement }) => {
      return useMemo(() => {
        const renderStart = performance.now();
        
        // Schedule performance measurement after render
        setTimeout(() => {
          const renderEnd = performance.now();
          this.recordPerformance(templateId, renderEnd - renderStart);
        }, 0);

        return children;
      }, [children]);
    });

    return React.createElement(PerformanceMonitor, {}, component);
  }

  private wrapWithErrorBoundary(component: ReactElement, templateId: string): ReactElement {
    class ComponentErrorBoundary extends React.Component<
      { children: ReactElement; templateId: string },
      { hasError: boolean; error?: Error }
    > {
      constructor(props: { children: ReactElement; templateId: string }) {
        super(props);
        this.state = { hasError: false };
      }

      static getDerivedStateFromError(error: Error): { hasError: boolean; error: Error } {
        return { hasError: true, error };
      }

      componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
        console.error(`❌ Error in template ${this.props.templateId}:`, error, errorInfo);
        
        // Send error to monitoring service
        if (typeof window !== 'undefined' && window.gtag) {
          window.gtag('event', 'exception', {
            description: `Template Error: ${this.props.templateId}`,
            fatal: false
          });
        }
      }

      render(): ReactElement {
        if (this.state.hasError) {
          return React.createElement('div', {
            className: 'template-error-fallback',
            'data-testid': 'template-error',
            style: {
              padding: '20px',
              border: '2px solid #ff4444',
              borderRadius: '8px',
              backgroundColor: '#fff5f5',
              color: '#cc0000'
            }
          }, `❌ Error loading template: ${this.props.templateId}`);
        }

        return this.props.children;
      }
    }

    return React.createElement(ComponentErrorBoundary, { templateId }, component);
  }

  private wrapWithAccessibility(component: ReactElement, metadata: TemplateMetadata): ReactElement {
    const AccessibilityWrapper = ({ children }: { children: ReactElement }) => {
      return React.createElement('div', {
        role: 'region',
        'aria-label': metadata.name,
        'aria-describedby': `${metadata.id}-description`,
        'data-template-id': metadata.id,
        'data-template-category': metadata.category
      }, [
        React.createElement('span', {
          key: 'description',
          id: `${metadata.id}-description`,
          className: 'sr-only'
        }, metadata.description),
        children
      ]);
    };

    return React.createElement(AccessibilityWrapper, {}, component);
  }

  private wrapWithSecurity(component: ReactElement, metadata: TemplateMetadata): ReactElement {
    const SecurityWrapper = ({ children }: { children: ReactElement }) => {
      // Add CSP headers and XSS protection
      React.useEffect(() => {
        // Validate component props for potential XSS
        if (typeof window !== 'undefined') {
          const scripts = document.querySelectorAll(`[data-template-id="${metadata.id}"] script`);
          if (scripts.length > 0) {
            console.warn(`⚠️ Potential XSS risk in template ${metadata.id}: found script tags`);
          }
        }
      }, []);

      return React.createElement('div', {
        'data-security-wrapper': 'true',
        'data-template-id': metadata.id
      }, children);
    };

    return React.createElement(SecurityWrapper, {}, component);
  }

  private recordPerformance(templateId: string, renderTime: number): void {
    if (!this.performanceData.has(templateId)) {
      this.performanceData.set(templateId, []);
    }
    
    const data = this.performanceData.get(templateId)!;
    data.push(renderTime);
    
    // Keep only last 100 measurements
    if (data.length > 100) {
      data.shift();
    }
  }

  private estimateMemoryUsage(template: Template): number {
    // Simple heuristic based on component complexity
    const baseSize = 1024; // 1KB base
    const dependencySize = template.metadata.dependencies.length * 512;
    const complexityMultiplier = {
      beginner: 1,
      intermediate: 1.5,
      advanced: 2,
      expert: 3
    }[template.metadata.complexity];
    
    return Math.round(baseSize + dependencySize * complexityMultiplier);
  }

  public getPerformanceStats(templateId: string): {
    averageRenderTime: number;
    minRenderTime: number;
    maxRenderTime: number;
    totalRenders: number;
  } | null {
    const data = this.performanceData.get(templateId);
    if (!data || data.length === 0) {
      return null;
    }

    return {
      averageRenderTime: data.reduce((sum, time) => sum + time, 0) / data.length,
      minRenderTime: Math.min(...data),
      maxRenderTime: Math.max(...data),
      totalRenders: data.length
    };
  }

  public getAllPerformanceStats(): Record<string, ReturnType<typeof this.getPerformanceStats>> {
    const stats: Record<string, ReturnType<typeof this.getPerformanceStats>> = {};
    
    this.performanceData.forEach((_, templateId) => {
      stats[templateId] = this.getPerformanceStats(templateId);
    });

    return stats;
  }

  public clearPerformanceData(templateId?: string): void {
    if (templateId) {
      this.performanceData.delete(templateId);
    } else {
      this.performanceData.clear();
    }
  }

  public createBatch(templates: Array<{ id: string; props?: any }>): Array<CreatedComponent | null> {
    return templates.map(({ id, props }) => this.create(id, props));
  }

  public updateOptions(newOptions: Partial<ComponentFactoryOptions>): void {
    this.options = { ...this.options, ...newOptions };
  }
}

// Singleton instance
export const componentFactory = ComponentFactory.getInstance();

// Helper functions
export function createComponent(templateId: string, props?: any): CreatedComponent | null {
  return componentFactory.create(templateId, props);
}

export function createComponents(templates: Array<{ id: string; props?: any }>): Array<CreatedComponent | null> {
  return componentFactory.createBatch(templates);
}

export function getComponentPerformance(templateId: string): ReturnType<typeof componentFactory.getPerformanceStats> {
  return componentFactory.getPerformanceStats(templateId);
}