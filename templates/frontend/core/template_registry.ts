/**
 * 🏭 FRONTEND TEMPLATE REGISTRY - ENTERPRISE MANAGEMENT
 * ======================================================
 * 
 * Centralized registry for all frontend templates
 * Dynamic template discovery and management
 * Creator Economy specialized templates
 * 
 * © 2025 Fahed Mlaiel <mlaiel@live.de>
 * TOUS DROITS RÉSERVÉS
 */

import { ComponentType, ReactElement } from 'react';

export interface TemplateMetadata {
  id: string;
  name: string;
  description: string;
  category: TemplateCategory;
  framework: Framework;
  tags: string[];
  version: string;
  author: string;
  createdAt: Date;
  updatedAt: Date;
  complexity: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  dependencies: string[];
  props?: Record<string, any>;
  examples?: string[];
  documentation?: string;
}

export type TemplateCategory = 
  | 'core'
  | 'components'
  | 'layout'
  | 'mobile'
  | 'creator-economy'
  | 'state-management'
  | 'animation'
  | 'testing'
  | 'styling'
  | 'visualization'
  | 'security'
  | 'i18n'
  | 'performance'
  | 'utilities';

export type Framework = 'react' | 'vue' | 'angular' | 'svelte' | 'universal';

export interface Template {
  metadata: TemplateMetadata;
  component: ComponentType<any>;
  render?: (props?: any) => ReactElement;
  validate?: (props: any) => boolean;
  optimize?: (props: any) => any;
}

export class FrontendTemplateRegistry {
  private static instance: FrontendTemplateRegistry;
  private templates: Map<string, Template> = new Map();
  private categories: Map<TemplateCategory, Set<string>> = new Map();
  private frameworks: Map<Framework, Set<string>> = new Map();

  private constructor() {
    this.initializeCategories();
    this.initializeFrameworks();
  }

  public static getInstance(): FrontendTemplateRegistry {
    if (!FrontendTemplateRegistry.instance) {
      FrontendTemplateRegistry.instance = new FrontendTemplateRegistry();
    }
    return FrontendTemplateRegistry.instance;
  }

  private initializeCategories(): void {
    const categories: TemplateCategory[] = [
      'core', 'components', 'layout', 'mobile', 'creator-economy',
      'state-management', 'animation', 'testing', 'styling',
      'visualization', 'security', 'i18n', 'performance', 'utilities'
    ];
    
    categories.forEach(category => {
      this.categories.set(category, new Set());
    });
  }

  private initializeFrameworks(): void {
    const frameworks: Framework[] = ['react', 'vue', 'angular', 'svelte', 'universal'];
    
    frameworks.forEach(framework => {
      this.frameworks.set(framework, new Set());
    });
  }

  public register(template: Template): void {
    const { id, category, framework } = template.metadata;
    
    if (this.templates.has(id)) {
      console.warn(`Template with id "${id}" already exists. Overwriting...`);
    }

    this.templates.set(id, template);
    this.categories.get(category)?.add(id);
    this.frameworks.get(framework)?.add(id);

    console.log(`✅ Registered template: ${id} (${category}/${framework})`);
  }

  public get(id: string): Template | undefined {
    return this.templates.get(id);
  }

  public getByCategory(category: TemplateCategory): Template[] {
    const templateIds = this.categories.get(category) || new Set();
    return Array.from(templateIds)
      .map(id => this.templates.get(id))
      .filter((template): template is Template => template !== undefined);
  }

  public getByFramework(framework: Framework): Template[] {
    const templateIds = this.frameworks.get(framework) || new Set();
    return Array.from(templateIds)
      .map(id => this.templates.get(id))
      .filter((template): template is Template => template !== undefined);
  }

  public search(query: {
    category?: TemplateCategory;
    framework?: Framework;
    tags?: string[];
    complexity?: string;
    search?: string;
  }): Template[] {
    let results = Array.from(this.templates.values());

    if (query.category) {
      results = results.filter(t => t.metadata.category === query.category);
    }

    if (query.framework) {
      results = results.filter(t => t.metadata.framework === query.framework);
    }

    if (query.tags && query.tags.length > 0) {
      results = results.filter(t => 
        query.tags!.some(tag => t.metadata.tags.includes(tag))
      );
    }

    if (query.complexity) {
      results = results.filter(t => t.metadata.complexity === query.complexity);
    }

    if (query.search) {
      const searchLower = query.search.toLowerCase();
      results = results.filter(t =>
        t.metadata.name.toLowerCase().includes(searchLower) ||
        t.metadata.description.toLowerCase().includes(searchLower) ||
        t.metadata.tags.some(tag => tag.toLowerCase().includes(searchLower))
      );
    }

    return results;
  }

  public getAllTemplates(): Template[] {
    return Array.from(this.templates.values());
  }

  public getCategories(): TemplateCategory[] {
    return Array.from(this.categories.keys());
  }

  public getFrameworks(): Framework[] {
    return Array.from(this.frameworks.keys());
  }

  public getStats(): {
    total: number;
    byCategory: Record<TemplateCategory, number>;
    byFramework: Record<Framework, number>;
  } {
    const byCategory = {} as Record<TemplateCategory, number>;
    const byFramework = {} as Record<Framework, number>;

    this.categories.forEach((templateIds, category) => {
      byCategory[category] = templateIds.size;
    });

    this.frameworks.forEach((templateIds, framework) => {
      byFramework[framework] = templateIds.size;
    });

    return {
      total: this.templates.size,
      byCategory,
      byFramework
    };
  }

  public validate(): { isValid: boolean; errors: string[] } {
    const errors: string[] = [];
    
    this.templates.forEach((template, id) => {
      if (!template.metadata.name) {
        errors.push(`Template ${id} missing name`);
      }
      
      if (!template.metadata.description) {
        errors.push(`Template ${id} missing description`);
      }
      
      if (!template.component) {
        errors.push(`Template ${id} missing component`);
      }
    });

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  public exportMetadata(): TemplateMetadata[] {
    return Array.from(this.templates.values()).map(t => t.metadata);
  }

  public clear(): void {
    this.templates.clear();
    this.categories.forEach(set => set.clear());
    this.frameworks.forEach(set => set.clear());
  }
}

// Singleton instance
export const templateRegistry = FrontendTemplateRegistry.getInstance();

// Helper functions
export function registerTemplate(template: Template): void {
  templateRegistry.register(template);
}

export function getTemplate(id: string): Template | undefined {
  return templateRegistry.get(id);
}

export function searchTemplates(query: Parameters<typeof templateRegistry.search>[0]): Template[] {
  return templateRegistry.search(query);
}

export function getTemplatesByCategory(category: TemplateCategory): Template[] {
  return templateRegistry.getByCategory(category);
}

export function getTemplatesByFramework(framework: Framework): Template[] {
  return templateRegistry.getByFramework(framework);
}