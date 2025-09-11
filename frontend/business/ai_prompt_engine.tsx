/**
 * 🎯 AI Prompt Engineering System - Advanced Prompt Management & Optimization
 * 
 * @fileoverview Enterprise prompt engineering system for AI provider optimization
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @copyright 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
 */

'use client';

import React, { useState, useCallback, useEffect, createContext, useContext } from 'react';
import {
  SparklesIcon,
  CogIcon,
  ChartBarIcon,
  DocumentTextIcon,
  PlayIcon,
  PauseIcon,
  BeakerIcon,
  ClipboardDocumentIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';

// === PROMPT TYPES ===

export interface PromptTemplate {
  id: string;
  name: string;
  description?: string;
  category: 'creative' | 'analytical' | 'conversational' | 'technical' | 'business' | 'educational';
  content: string;
  variables: PromptVariable[];
  tags: string[];
  provider: AIProvider;
  model: string;
  parameters: ModelParameters;
  performance: PromptPerformance;
  versions: PromptVersion[];
  isActive: boolean;
  createdAt: number;
  updatedAt: number;
  author: string;
}

export interface PromptVariable {
  name: string;
  type: 'text' | 'number' | 'boolean' | 'select' | 'multiline';
  description?: string;
  required: boolean;
  defaultValue?: any;
  options?: string[];
  validation?: {
    min?: number;
    max?: number;
    pattern?: string;
  };
}

export interface AIProvider {
  id: string;
  name: string;
  apiEndpoint: string;
  models: AIModel[];
  rateLimit: RateLimit;
  pricing: PricingInfo;
  capabilities: ProviderCapability[];
  status: 'active' | 'inactive' | 'limited';
}

export interface AIModel {
  id: string;
  name: string;
  description?: string;
  maxTokens: number;
  costPer1kTokens: number;
  capabilities: ModelCapability[];
  parameters: ModelParameterDefinition[];
}

export interface ModelParameters {
  temperature?: number;
  maxTokens?: number;
  topP?: number;
  topK?: number;
  frequencyPenalty?: number;
  presencePenalty?: number;
  stopSequences?: string[];
  customParameters?: Record<string, any>;
}

export interface ModelParameterDefinition {
  name: string;
  type: 'number' | 'boolean' | 'string' | 'array';
  description: string;
  min?: number;
  max?: number;
  defaultValue: any;
  step?: number;
}

export interface PromptPerformance {
  totalExecutions: number;
  successRate: number;
  averageResponseTime: number;
  averageTokenUsage: number;
  averageQualityScore: number;
  lastExecuted?: number;
  costPerExecution: number;
  errorTypes: Record<string, number>;
}

export interface PromptVersion {
  id: string;
  version: string;
  content: string;
  parameters: ModelParameters;
  performance: PromptPerformance;
  createdAt: number;
  changelog?: string;
}

export interface PromptExecution {
  id: string;
  promptId: string;
  input: Record<string, any>;
  output: string;
  metadata: ExecutionMetadata;
  performance: ExecutionPerformance;
  timestamp: number;
  status: 'success' | 'error' | 'timeout';
  error?: string;
}

export interface ExecutionMetadata {
  provider: string;
  model: string;
  parameters: ModelParameters;
  tokensUsed: number;
  cost: number;
  requestId?: string;
}

export interface ExecutionPerformance {
  responseTime: number;
  qualityScore?: number;
  relevanceScore?: number;
  creativityScore?: number;
  coherenceScore?: number;
}

export interface RateLimit {
  requestsPerMinute: number;
  tokensPerMinute: number;
  concurrentRequests: number;
}

export interface PricingInfo {
  inputTokens: number;
  outputTokens: number;
  currency: string;
}

export interface ProviderCapability {
  type: 'text_generation' | 'image_generation' | 'code_generation' | 'analysis' | 'translation';
  supported: boolean;
  quality: 'low' | 'medium' | 'high' | 'excellent';
}

export interface ModelCapability {
  type: 'reasoning' | 'creativity' | 'factual' | 'conversational' | 'technical' | 'multilingual';
  level: 'basic' | 'intermediate' | 'advanced' | 'expert';
}

export interface PromptOptimization {
  originalPrompt: string;
  optimizedPrompt: string;
  improvements: OptimizationImprovement[];
  expectedGains: {
    qualityIncrease: number;
    speedIncrease: number;
    costReduction: number;
  };
  confidence: number;
}

export interface OptimizationImprovement {
  type: 'clarity' | 'specificity' | 'structure' | 'examples' | 'constraints' | 'context';
  description: string;
  impact: 'low' | 'medium' | 'high';
}

// === PROMPT CONTEXT ===

interface PromptContextValue {
  templates: PromptTemplate[];
  providers: AIProvider[];
  executions: PromptExecution[];
  selectedTemplate: PromptTemplate | null;
  isExecuting: boolean;
  createTemplate: (template: Omit<PromptTemplate, 'id' | 'createdAt' | 'updatedAt' | 'performance' | 'versions'>) => string;
  updateTemplate: (templateId: string, updates: Partial<PromptTemplate>) => void;
  deleteTemplate: (templateId: string) => void;
  executePrompt: (templateId: string, variables: Record<string, any>) => Promise<PromptExecution>;
  optimizePrompt: (templateId: string) => Promise<PromptOptimization>;
  selectTemplate: (templateId: string) => void;
  getTemplateAnalytics: (templateId: string) => TemplateAnalytics;
  exportTemplate: (templateId: string) => void;
  importTemplate: (templateData: any) => string;
}

const PromptContext = createContext<PromptContextValue | null>(null);

export const usePromptSystem = () => {
  const context = useContext(PromptContext);
  if (!context) {
    throw new Error('usePromptSystem must be used within a PromptProvider');
  }
  return context;
};

export interface TemplateAnalytics {
  totalExecutions: number;
  successRate: number;
  averageScore: number;
  costAnalysis: CostAnalysis;
  performanceTrend: PerformanceDataPoint[];
  topErrors: ErrorAnalysis[];
  recommendations: string[];
}

export interface CostAnalysis {
  totalCost: number;
  costPerExecution: number;
  projectedMonthlyCost: number;
  costByProvider: Record<string, number>;
}

export interface PerformanceDataPoint {
  timestamp: number;
  responseTime: number;
  qualityScore: number;
  cost: number;
}

export interface ErrorAnalysis {
  type: string;
  count: number;
  percentage: number;
  lastOccurred: number;
}

// === PROMPT PROVIDER ===

interface PromptProviderProps {
  children: React.ReactNode;
  apiEndpoint?: string;
}

export const PromptProvider: React.FC<PromptProviderProps> = ({
  children,
  apiEndpoint = '/api/v1/prompts'
}) => {
  const [templates, setTemplates] = useState<PromptTemplate[]>(DEFAULT_TEMPLATES);
  const [providers, setProviders] = useState<AIProvider[]>(DEFAULT_PROVIDERS);
  const [executions, setExecutions] = useState<PromptExecution[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<PromptTemplate | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);

  const createTemplate = useCallback((templateData: Omit<PromptTemplate, 'id' | 'createdAt' | 'updatedAt' | 'performance' | 'versions'>) => {
    const newTemplate: PromptTemplate = {
      ...templateData,
      id: `template_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      performance: {
        totalExecutions: 0,
        successRate: 0,
        averageResponseTime: 0,
        averageTokenUsage: 0,
        averageQualityScore: 0,
        costPerExecution: 0,
        errorTypes: {}
      },
      versions: [{
        id: 'v1.0.0',
        version: '1.0.0',
        content: templateData.content,
        parameters: templateData.parameters,
        performance: {
          totalExecutions: 0,
          successRate: 0,
          averageResponseTime: 0,
          averageTokenUsage: 0,
          averageQualityScore: 0,
          costPerExecution: 0,
          errorTypes: {}
        },
        createdAt: Date.now()
      }],
      createdAt: Date.now(),
      updatedAt: Date.now()
    };

    setTemplates(prev => [...prev, newTemplate]);
    return newTemplate.id;
  }, []);

  const updateTemplate = useCallback((templateId: string, updates: Partial<PromptTemplate>) => {
    setTemplates(prev => prev.map(template => 
      template.id === templateId 
        ? { ...template, ...updates, updatedAt: Date.now() }
        : template
    ));
  }, []);

  const deleteTemplate = useCallback((templateId: string) => {
    setTemplates(prev => prev.filter(template => template.id !== templateId));
    if (selectedTemplate?.id === templateId) {
      setSelectedTemplate(null);
    }
  }, [selectedTemplate]);

  const executePrompt = useCallback(async (templateId: string, variables: Record<string, any>): Promise<PromptExecution> => {
    const template = templates.find(t => t.id === templateId);
    if (!template) {
      throw new Error('Template not found');
    }

    setIsExecuting(true);

    try {
      // Interpolate variables into prompt
      let interpolatedPrompt = template.content;
      template.variables.forEach(variable => {
        const value = variables[variable.name] || variable.defaultValue || '';
        interpolatedPrompt = interpolatedPrompt.replace(
          new RegExp(`\\{\\{${variable.name}\\}\\}`, 'g'),
          String(value)
        );
      });

      const startTime = Date.now();
      
      // Mock API call (in real implementation, this would call the actual AI provider)
      await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));
      
      const responseTime = Date.now() - startTime;
      const mockTokens = Math.floor(Math.random() * 500) + 100;
      const mockCost = (mockTokens / 1000) * 0.002; // $0.002 per 1k tokens
      
      const execution: PromptExecution = {
        id: `exec_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        promptId: templateId,
        input: variables,
        output: generateMockResponse(interpolatedPrompt),
        metadata: {
          provider: template.provider.name,
          model: template.model,
          parameters: template.parameters,
          tokensUsed: mockTokens,
          cost: mockCost,
          requestId: `req_${Date.now()}`
        },
        performance: {
          responseTime,
          qualityScore: Math.random() * 0.3 + 0.7, // 0.7-1.0
          relevanceScore: Math.random() * 0.2 + 0.8,
          creativityScore: Math.random() * 0.4 + 0.6,
          coherenceScore: Math.random() * 0.2 + 0.8
        },
        timestamp: Date.now(),
        status: Math.random() > 0.05 ? 'success' : 'error', // 95% success rate
        error: Math.random() > 0.05 ? undefined : 'Rate limit exceeded'
      };

      setExecutions(prev => [...prev, execution]);
      
      // Update template performance
      updateTemplatePerformance(templateId, execution);
      
      return execution;
    } finally {
      setIsExecuting(false);
    }
  }, [templates]);

  const updateTemplatePerformance = useCallback((templateId: string, execution: PromptExecution) => {
    setTemplates(prev => prev.map(template => {
      if (template.id !== templateId) return template;

      const newTotalExecutions = template.performance.totalExecutions + 1;
      const successCount = template.performance.totalExecutions * (template.performance.successRate / 100) + 
                          (execution.status === 'success' ? 1 : 0);
      
      return {
        ...template,
        performance: {
          ...template.performance,
          totalExecutions: newTotalExecutions,
          successRate: (successCount / newTotalExecutions) * 100,
          averageResponseTime: (template.performance.averageResponseTime * template.performance.totalExecutions + execution.performance.responseTime) / newTotalExecutions,
          averageTokenUsage: (template.performance.averageTokenUsage * template.performance.totalExecutions + execution.metadata.tokensUsed) / newTotalExecutions,
          averageQualityScore: execution.performance.qualityScore ? 
            (template.performance.averageQualityScore * template.performance.totalExecutions + execution.performance.qualityScore) / newTotalExecutions : 
            template.performance.averageQualityScore,
          costPerExecution: (template.performance.costPerExecution * template.performance.totalExecutions + execution.metadata.cost) / newTotalExecutions,
          lastExecuted: execution.timestamp
        }
      };
    }));
  }, []);

  const optimizePrompt = useCallback(async (templateId: string): Promise<PromptOptimization> => {
    const template = templates.find(t => t.id === templateId);
    if (!template) {
      throw new Error('Template not found');
    }

    // Mock optimization (in real implementation, this would use AI to optimize the prompt)
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    return {
      originalPrompt: template.content,
      optimizedPrompt: generateOptimizedPrompt(template.content),
      improvements: [
        {
          type: 'clarity',
          description: 'Added specific instructions for output format',
          impact: 'high'
        },
        {
          type: 'examples',
          description: 'Included example outputs for better understanding',
          impact: 'medium'
        },
        {
          type: 'constraints',
          description: 'Added length constraints for more focused responses',
          impact: 'medium'
        }
      ],
      expectedGains: {
        qualityIncrease: 15,
        speedIncrease: 8,
        costReduction: 12
      },
      confidence: 0.85
    };
  }, [templates]);

  const selectTemplate = useCallback((templateId: string) => {
    const template = templates.find(t => t.id === templateId);
    setSelectedTemplate(template || null);
  }, [templates]);

  const getTemplateAnalytics = useCallback((templateId: string): TemplateAnalytics => {
    const template = templates.find(t => t.id === templateId);
    const templateExecutions = executions.filter(e => e.promptId === templateId);
    
    if (!template) {
      return {
        totalExecutions: 0,
        successRate: 0,
        averageScore: 0,
        costAnalysis: { totalCost: 0, costPerExecution: 0, projectedMonthlyCost: 0, costByProvider: {} },
        performanceTrend: [],
        topErrors: [],
        recommendations: []
      };
    }

    const totalCost = templateExecutions.reduce((sum, exec) => sum + exec.metadata.cost, 0);
    const averageScore = templateExecutions.length > 0 ? 
      templateExecutions.reduce((sum, exec) => sum + (exec.performance.qualityScore || 0), 0) / templateExecutions.length : 0;

    return {
      totalExecutions: template.performance.totalExecutions,
      successRate: template.performance.successRate,
      averageScore: averageScore * 100,
      costAnalysis: {
        totalCost,
        costPerExecution: template.performance.costPerExecution,
        projectedMonthlyCost: template.performance.costPerExecution * 30 * template.performance.totalExecutions,
        costByProvider: { [template.provider.name]: totalCost }
      },
      performanceTrend: templateExecutions.slice(-10).map(exec => ({
        timestamp: exec.timestamp,
        responseTime: exec.performance.responseTime,
        qualityScore: exec.performance.qualityScore || 0,
        cost: exec.metadata.cost
      })),
      topErrors: Object.entries(template.performance.errorTypes).map(([type, count]) => ({
        type,
        count,
        percentage: (count / template.performance.totalExecutions) * 100,
        lastOccurred: Date.now() - Math.random() * 86400000 // Mock last occurrence
      })),
      recommendations: generateRecommendations(template)
    };
  }, [templates, executions]);

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
    a.download = `${template.name.replace(/[^a-z0-9]/gi, '_')}_prompt.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [templates]);

  const importTemplate = useCallback((templateData: any) => {
    try {
      const template: PromptTemplate = {
        ...templateData.template,
        id: `template_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        createdAt: Date.now(),
        updatedAt: Date.now()
      };

      setTemplates(prev => [...prev, template]);
      return template.id;
    } catch (error) {
      console.error('Failed to import template:', error);
      return '';
    }
  }, []);

  const contextValue: PromptContextValue = {
    templates,
    providers,
    executions,
    selectedTemplate,
    isExecuting,
    createTemplate,
    updateTemplate,
    deleteTemplate,
    executePrompt,
    optimizePrompt,
    selectTemplate,
    getTemplateAnalytics,
    exportTemplate,
    importTemplate
  };

  return (
    <PromptContext.Provider value={contextValue}>
      {children}
    </PromptContext.Provider>
  );
};

// === UTILITY FUNCTIONS ===

function generateMockResponse(prompt: string): string {
  const responses = [
    "This is a generated response based on your prompt. The AI has processed your request and provided this comprehensive answer.",
    "Based on the provided prompt, here's a detailed response that addresses the key points and requirements you've specified.",
    "The AI system has analyzed your prompt and generated this response with careful consideration of the context and parameters.",
    "Here's a thoughtful response that incorporates the elements from your prompt while maintaining high quality and relevance."
  ];
  
  return responses[Math.floor(Math.random() * responses.length)];
}

function generateOptimizedPrompt(originalPrompt: string): string {
  return `${originalPrompt}\n\nPlease provide your response in a clear, structured format with specific examples where applicable. Limit your response to 200 words for conciseness.`;
}

function generateRecommendations(template: PromptTemplate): string[] {
  const recommendations = [];
  
  if (template.performance.successRate < 90) {
    recommendations.push("Consider adding more specific instructions to improve success rate");
  }
  
  if (template.performance.averageResponseTime > 3000) {
    recommendations.push("Try reducing prompt complexity to improve response time");
  }
  
  if (template.performance.averageQualityScore < 0.8) {
    recommendations.push("Add examples or constraints to improve output quality");
  }
  
  if (template.performance.costPerExecution > 0.01) {
    recommendations.push("Consider using a more cost-effective model or optimizing token usage");
  }
  
  return recommendations;
}

// === DEFAULT DATA ===

const DEFAULT_PROVIDERS: AIProvider[] = [
  {
    id: 'openai',
    name: 'OpenAI',
    apiEndpoint: 'https://api.openai.com/v1',
    models: [
      {
        id: 'gpt-4',
        name: 'GPT-4',
        description: 'Most capable GPT-4 model',
        maxTokens: 8192,
        costPer1kTokens: 0.03,
        capabilities: [
          { type: 'reasoning', level: 'expert' },
          { type: 'creativity', level: 'advanced' },
          { type: 'factual', level: 'expert' }
        ],
        parameters: [
          { name: 'temperature', type: 'number', description: 'Controls randomness', min: 0, max: 2, defaultValue: 0.7, step: 0.1 },
          { name: 'max_tokens', type: 'number', description: 'Maximum tokens to generate', min: 1, max: 8192, defaultValue: 1000, step: 1 }
        ]
      }
    ],
    rateLimit: {
      requestsPerMinute: 60,
      tokensPerMinute: 90000,
      concurrentRequests: 10
    },
    pricing: {
      inputTokens: 0.03,
      outputTokens: 0.06,
      currency: 'USD'
    },
    capabilities: [
      { type: 'text_generation', supported: true, quality: 'excellent' },
      { type: 'code_generation', supported: true, quality: 'high' },
      { type: 'analysis', supported: true, quality: 'excellent' }
    ],
    status: 'active'
  }
];

const DEFAULT_TEMPLATES: PromptTemplate[] = [
  {
    id: 'creative-writing',
    name: 'Creative Writing Assistant',
    description: 'Helps generate creative content with specified tone and style',
    category: 'creative',
    content: 'Write a {{word_count}} word {{content_type}} about {{topic}} in a {{tone}} tone. Make it {{style}} and engaging for {{audience}}.',
    variables: [
      { name: 'word_count', type: 'number', description: 'Number of words', required: true, defaultValue: 500 },
      { name: 'content_type', type: 'select', description: 'Type of content', required: true, options: ['story', 'article', 'blog post', 'essay'] },
      { name: 'topic', type: 'text', description: 'Main topic or theme', required: true },
      { name: 'tone', type: 'select', description: 'Writing tone', required: true, options: ['professional', 'casual', 'humorous', 'serious', 'friendly'] },
      { name: 'style', type: 'text', description: 'Writing style', required: false, defaultValue: 'informative' },
      { name: 'audience', type: 'text', description: 'Target audience', required: false, defaultValue: 'general public' }
    ],
    tags: ['writing', 'creative', 'content'],
    provider: DEFAULT_PROVIDERS[0],
    model: 'gpt-4',
    parameters: {
      temperature: 0.8,
      maxTokens: 1000,
      topP: 0.9
    },
    performance: {
      totalExecutions: 42,
      successRate: 95.2,
      averageResponseTime: 2340,
      averageTokenUsage: 756,
      averageQualityScore: 0.87,
      lastExecuted: Date.now() - 3600000,
      costPerExecution: 0.0234,
      errorTypes: { 'rate_limit': 2 }
    },
    versions: [],
    isActive: true,
    createdAt: Date.now() - 86400000 * 7,
    updatedAt: Date.now() - 3600000,
    author: 'Fahed Mlaiel'
  }
];

export default PromptProvider;