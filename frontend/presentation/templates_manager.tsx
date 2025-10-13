/**
 * 📄 Templates Manager Enterprise - Dynamic Content Template System
 * 
 * @fileoverview Advanced template management for content creation workflows
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @copyright 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
 */

'use client';

import React, { useState, useCallback, useMemo, createContext, useContext } from 'react';
import { 
  DocumentTextIcon, 
  PencilIcon, 
  TrashIcon, 
  DocumentDuplicateIcon,
  EyeIcon,
  StarIcon,
  TagIcon,
  ClockIcon,
  UserIcon
} from '@heroicons/react/24/outline';

// === TEMPLATE TYPES & INTERFACES ===

export interface TemplateField {
  id: string;
  name: string;
  type: 'text' | 'textarea' | 'number' | 'date' | 'select' | 'multiselect' | 'file' | 'rich-text' | 'boolean';
  label: string;
  placeholder?: string;
  required?: boolean;
  defaultValue?: any;
  validation?: TemplateFieldValidation;
  options?: { value: any; label: string }[];
  conditional?: {
    field: string;
    value: any;
    operator: 'equals' | 'not_equals' | 'contains' | 'greater_than' | 'less_than';
  };
}

export interface TemplateFieldValidation {
  min?: number;
  max?: number;
  pattern?: string;
  custom?: (value: any) => string | null;
}

export interface Template {
  id: string;
  name: string;
  description?: string;
  category: string;
  tags: string[];
  fields: TemplateField[];
  layout: TemplateLayout;
  preview?: string;
  thumbnail?: string;
  author: string;
  createdAt: number;
  updatedAt: number;
  version: string;
  isPublic: boolean;
  usageCount: number;
  rating: number;
  metadata?: {
    estimatedTime?: number; // minutes
    difficulty?: 'beginner' | 'intermediate' | 'professional';
    industry?: string[];
    language?: string;
  };
}

export interface TemplateLayout {
  type: 'form' | 'grid' | 'wizard' | 'custom';
  columns?: number;
  sections?: TemplateSection[];
  customCSS?: string;
}

export interface TemplateSection {
  id: string;
  title: string;
  description?: string;
  fields: string[];
  collapsible?: boolean;
  defaultExpanded?: boolean;
}

export interface TemplateCategory {
  id: string;
  name: string;
  description?: string;
  icon?: string;
  color?: string;
  templateCount: number;
}

export interface TemplateFilter {
  category?: string;
  tags?: string[];
  author?: string;
  difficulty?: string;
  industry?: string;
  search?: string;
  sortBy?: 'name' | 'created' | 'updated' | 'usage' | 'rating';
  sortDirection?: 'asc' | 'desc';
}

export interface TemplateInstance {
  id: string;
  templateId: string;
  data: Record<string, any>;
  createdAt: number;
  updatedAt: number;
  name?: string;
  status: 'draft' | 'completed' | 'published';
}

// === TEMPLATE CONTEXT ===

interface TemplateContextValue {
  templates: Template[];
  categories: TemplateCategory[];
  instances: TemplateInstance[];
  currentTemplate: Template | null;
  currentInstance: TemplateInstance | null;
  filter: TemplateFilter;
  setFilter: (filter: TemplateFilter) => void;
  selectTemplate: (template: Template) => void;
  createInstance: (templateId: string, initialData?: any) => string;
  updateInstance: (instanceId: string, data: Record<string, any>) => void;
  deleteInstance: (instanceId: string) => void;
  duplicateTemplate: (templateId: string) => string;
  deleteTemplate: (templateId: string) => void;
  exportTemplate: (templateId: string) => void;
  importTemplate: (templateData: any) => string;
}

const TemplateContext = createContext<TemplateContextValue | null>(null);

export const useTemplates = () => {
  const context = useContext(TemplateContext);
  if (!context) {
    throw new Error('useTemplates must be used within a TemplateProvider');
  }
  return context;
};

// === TEMPLATE PROVIDER ===

interface TemplateProviderProps {
  children: React.ReactNode;
  initialTemplates?: Template[];
  initialCategories?: TemplateCategory[];
}

export const TemplateProvider: React.FC<TemplateProviderProps> = ({
  children,
  initialTemplates = DEFAULT_TEMPLATES,
  initialCategories = DEFAULT_CATEGORIES
}) => {
  const [templates, setTemplates] = useState<Template[]>(initialTemplates);
  const [categories, setCategories] = useState<TemplateCategory[]>(initialCategories);
  const [instances, setInstances] = useState<TemplateInstance[]>([]);
  const [currentTemplate, setCurrentTemplate] = useState<Template | null>(null);
  const [currentInstance, setCurrentInstance] = useState<TemplateInstance | null>(null);
  const [filter, setFilter] = useState<TemplateFilter>({});

  const selectTemplate = useCallback((template: Template) => {
    setCurrentTemplate(template);
  }, []);

  const createInstance = useCallback((templateId: string, initialData: any = {}) => {
    const template = templates.find(t => t.id === templateId);
    if (!template) return '';

    const instanceId = `instance_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const newInstance: TemplateInstance = {
      id: instanceId,
      templateId,
      data: initialData,
      createdAt: Date.now(),
      updatedAt: Date.now(),
      status: 'draft'
    };

    setInstances(prev => [...prev, newInstance]);
    setCurrentInstance(newInstance);
    
    // Update template usage count
    setTemplates(prev => prev.map(t => 
      t.id === templateId ? { ...t, usageCount: t.usageCount + 1 } : t
    ));

    return instanceId;
  }, [templates]);

  const updateInstance = useCallback((instanceId: string, data: Record<string, any>) => {
    setInstances(prev => prev.map(instance => 
      instance.id === instanceId 
        ? { ...instance, data: { ...instance.data, ...data }, updatedAt: Date.now() }
        : instance
    ));

    if (currentInstance?.id === instanceId) {
      setCurrentInstance(prev => prev ? { 
        ...prev, 
        data: { ...prev.data, ...data }, 
        updatedAt: Date.now() 
      } : null);
    }
  }, [currentInstance]);

  const deleteInstance = useCallback((instanceId: string) => {
    setInstances(prev => prev.filter(instance => instance.id !== instanceId));
    if (currentInstance?.id === instanceId) {
      setCurrentInstance(null);
    }
  }, [currentInstance]);

  const duplicateTemplate = useCallback((templateId: string) => {
    const template = templates.find(t => t.id === templateId);
    if (!template) return '';

    const newTemplateId = `template_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const duplicatedTemplate: Template = {
      ...template,
      id: newTemplateId,
      name: `${template.name} (Copy)`,
      createdAt: Date.now(),
      updatedAt: Date.now(),
      usageCount: 0,
      rating: 0
    };

    setTemplates(prev => [...prev, duplicatedTemplate]);
    return newTemplateId;
  }, [templates]);

  const deleteTemplate = useCallback((templateId: string) => {
    setTemplates(prev => prev.filter(template => template.id !== templateId));
    if (currentTemplate?.id === templateId) {
      setCurrentTemplate(null);
    }
  }, [currentTemplate]);

  const exportTemplate = useCallback((templateId: string) => {
    const template = templates.find(t => t.id === templateId);
    if (!template) return;

    const exportData = {
      template,
      exportedAt: Date.now(),
      version: '1.0'
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${template.name.replace(/[^a-z0-9]/gi, '_')}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [templates]);

  const importTemplate = useCallback((templateData: any) => {
    try {
      const template: Template = {
        ...templateData.template,
        id: `template_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        createdAt: Date.now(),
        updatedAt: Date.now(),
        usageCount: 0
      };

      setTemplates(prev => [...prev, template]);
      return template.id;
    } catch (error) {
      console.error('Failed to import template:', error);
      return '';
    }
  }, []);

  const contextValue: TemplateContextValue = {
    templates,
    categories,
    instances,
    currentTemplate,
    currentInstance,
    filter,
    setFilter,
    selectTemplate,
    createInstance,
    updateInstance,
    deleteInstance,
    duplicateTemplate,
    deleteTemplate,
    exportTemplate,
    importTemplate
  };

  return (
    <TemplateContext.Provider value={contextValue}>
      {children}
    </TemplateContext.Provider>
  );
};

// === TEMPLATE COMPONENTS ===

interface TemplateListProps {
  className?: string;
  onSelect?: (template: Template) => void;
}

export const TemplateList: React.FC<TemplateListProps> = ({ className, onSelect }) => {
  const { templates, filter, categories } = useTemplates();

  const filteredTemplates = useMemo(() => {
    return templates.filter(template => {
      if (filter.category && template.category !== filter.category) return false;
      if (filter.tags && !filter.tags.some(tag => template.tags.includes(tag))) return false;
      if (filter.author && template.author !== filter.author) return false;
      if (filter.difficulty && template.metadata?.difficulty !== filter.difficulty) return false;
      if (filter.search) {
        const searchLower = filter.search.toLowerCase();
        return template.name.toLowerCase().includes(searchLower) ||
               template.description?.toLowerCase().includes(searchLower) ||
               template.tags.some(tag => tag.toLowerCase().includes(searchLower));
      }
      return true;
    }).sort((a, b) => {
      const { sortBy = 'name', sortDirection = 'asc' } = filter;
      let comparison = 0;
      
      switch (sortBy) {
        case 'name':
          comparison = a.name.localeCompare(b.name);
          break;
        case 'created':
          comparison = a.createdAt - b.createdAt;
          break;
        case 'updated':
          comparison = a.updatedAt - b.updatedAt;
          break;
        case 'usage':
          comparison = a.usageCount - b.usageCount;
          break;
        case 'rating':
          comparison = a.rating - b.rating;
          break;
      }
      
      return sortDirection === 'desc' ? -comparison : comparison;
    });
  }, [templates, filter]);

  return (
    <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 ${className}`}>
      {filteredTemplates.map(template => (
        <TemplateCard
          key={template.id}
          template={template}
          onClick={() => onSelect?.(template)}
        />
      ))}
    </div>
  );
};

interface TemplateCardProps {
  template: Template;
  onClick?: () => void;
}

export const TemplateCard: React.FC<TemplateCardProps> = ({ template, onClick }) => {
  const { duplicateTemplate, deleteTemplate, exportTemplate } = useTemplates();
  const category = DEFAULT_CATEGORIES.find(c => c.id === template.category);

  return (
    <div className="bg-white rounded-lg border border-gray-200 hover:border-gray-300 transition-colors cursor-pointer">
      <div onClick={onClick} className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">{template.name}</h3>
            <p className="text-sm text-gray-600 mb-3">{template.description}</p>
          </div>
          {template.thumbnail && (
            <img 
              src={template.thumbnail} 
              alt={template.name}
              className="w-16 h-16 object-cover rounded-lg ml-4"
            />
          )}
        </div>

        <div className="flex items-center mb-3">
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
            category?.color ? `bg-${category.color}-100 text-${category.color}-800` : 'bg-gray-100 text-gray-800'
          }`}>
            {category?.name || template.category}
          </span>
          <div className="flex items-center ml-3">
            <StarIcon className="w-4 h-4 text-yellow-400 mr-1" />
            <span className="text-sm text-gray-600">{template.rating.toFixed(1)}</span>
          </div>
        </div>

        <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
          <div className="flex items-center">
            <UserIcon className="w-4 h-4 mr-1" />
            {template.author}
          </div>
          <div className="flex items-center">
            <ClockIcon className="w-4 h-4 mr-1" />
            {template.metadata?.estimatedTime || 15} min
          </div>
        </div>

        <div className="flex flex-wrap gap-1 mb-4">
          {template.tags.slice(0, 3).map(tag => (
            <span 
              key={tag}
              className="inline-flex items-center px-2 py-1 rounded-md text-xs bg-gray-100 text-gray-700"
            >
              <TagIcon className="w-3 h-3 mr-1" />
              {tag}
            </span>
          ))}
          {template.tags.length > 3 && (
            <span className="text-xs text-gray-500">+{template.tags.length - 3} more</span>
          )}
        </div>
      </div>

      <div className="flex items-center justify-between p-4 bg-gray-50 rounded-b-lg">
        <div className="text-sm text-gray-500">
          Used {template.usageCount} times
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              exportTemplate(template.id);
            }}
            className="p-1 text-gray-400 hover:text-gray-600"
            title="Export template"
          >
            <DocumentTextIcon className="w-4 h-4" />
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              duplicateTemplate(template.id);
            }}
            className="p-1 text-gray-400 hover:text-gray-600"
            title="Duplicate template"
          >
            <DocumentDuplicateIcon className="w-4 h-4" />
          </button>
          {!template.isPublic && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                deleteTemplate(template.id);
              }}
              className="p-1 text-gray-400 hover:text-red-600"
              title="Delete template"
            >
              <TrashIcon className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

interface TemplateFilterProps {
  className?: string;
}

export const TemplateFilter: React.FC<TemplateFilterProps> = ({ className }) => {
  const { filter, setFilter, categories } = useTemplates();

  return (
    <div className={`bg-white p-6 rounded-lg border border-gray-200 ${className}`}>
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Filter Templates</h3>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Search</label>
          <input
            type="text"
            value={filter.search || ''}
            onChange={(e) => setFilter({ ...filter, search: e.target.value })}
            placeholder="Search templates..."
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
          <select
            value={filter.category || ''}
            onChange={(e) => setFilter({ ...filter, category: e.target.value || undefined })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Categories</option>
            {categories.map(category => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Difficulty</label>
          <select
            value={filter.difficulty || ''}
            onChange={(e) => setFilter({ ...filter, difficulty: e.target.value || undefined })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Levels</option>
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="professional">Professional</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Sort By</label>
          <div className="flex space-x-2">
            <select
              value={filter.sortBy || 'name'}
              onChange={(e) => setFilter({ ...filter, sortBy: e.target.value as any })}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="name">Name</option>
              <option value="created">Created</option>
              <option value="updated">Updated</option>
              <option value="usage">Usage</option>
              <option value="rating">Rating</option>
            </select>
            <select
              value={filter.sortDirection || 'asc'}
              onChange={(e) => setFilter({ ...filter, sortDirection: e.target.value as any })}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="asc">↑</option>
              <option value="desc">↓</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  );
};

// === MAIN TEMPLATES MANAGER ===

interface TemplatesManagerProps {
  className?: string;
  onTemplateSelect?: (template: Template) => void;
}

export const TemplatesManager: React.FC<TemplatesManagerProps> = ({
  className,
  onTemplateSelect
}) => {
  return (
    <TemplateProvider>
      <div className={`max-w-7xl mx-auto p-6 ${className}`}>
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Content Templates</h1>
          <p className="text-gray-600">
            Choose from our collection of professional templates to streamline your content creation process.
          </p>
        </div>

        <div className="grid grid-cols-12 gap-6">
          <div className="col-span-12 lg:col-span-3">
            <TemplateFilter />
          </div>
          
          <div className="col-span-12 lg:col-span-9">
            <TemplateList onSelect={onTemplateSelect} />
          </div>
        </div>
      </div>
    </TemplateProvider>
  );
};

// === DEFAULT DATA ===

const DEFAULT_CATEGORIES: TemplateCategory[] = [
  {
    id: 'content-creation',
    name: 'Content Creation',
    description: 'Templates for various content types',
    templateCount: 15
  },
  {
    id: 'social-media',
    name: 'Social Media',
    description: 'Social media post templates',
    templateCount: 8
  },
  {
    id: 'marketing',
    name: 'Marketing',
    description: 'Marketing campaign templates',
    templateCount: 12
  },
  {
    id: 'documentation',
    name: 'Documentation',
    description: 'Technical documentation templates',
    templateCount: 6
  }
];

const DEFAULT_TEMPLATES: Template[] = [
  {
    id: 'blog-post-template',
    name: 'Blog Post Template',
    description: 'Professional blog post template with SEO optimization',
    category: 'content-creation',
    tags: ['blog', 'seo', 'writing'],
    fields: [
      {
        id: 'title',
        name: 'title',
        type: 'text',
        label: 'Blog Title',
        required: true,
        validation: { min: 10, max: 100 }
      },
      {
        id: 'content',
        name: 'content',
        type: 'rich-text',
        label: 'Blog Content',
        required: true
      }
    ],
    layout: {
      type: 'form',
      sections: [
        {
          id: 'basic',
          title: 'Essential Information',
          fields: ['title', 'content']
        }
      ]
    },
    author: 'Fahed Mlaiel',
    createdAt: Date.now() - 86400000,
    updatedAt: Date.now(),
    version: '1.0',
    isPublic: true,
    usageCount: 42,
    rating: 4.8,
    metadata: {
      estimatedTime: 30,
      difficulty: 'intermediate'
    }
  }
];

export default TemplatesManager;