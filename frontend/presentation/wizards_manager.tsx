/**
 * 🧙‍♂️ Wizards Manager Enterprise - Multi-Step Workflow Management
 * 
 * @fileoverview Advanced wizard system for complex multi-step workflows
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @copyright 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
 */

'use client';

import React, { useState, useCallback, useEffect, createContext, useContext } from 'react';
import { ChevronLeftIcon, ChevronRightIcon, CheckIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';

// === WIZARD TYPES & INTERFACES ===

export interface WizardStep {
  id: string;
  title: string;
  description?: string;
  component: React.ComponentType<WizardStepProps>;
  validation?: (data: any) => WizardValidationResult;
  optional?: boolean;
  visible?: (data: any) => boolean;
  estimatedTime?: number; // minutes
  order: number;
}

export interface WizardConfig {
  id: string;
  title: string;
  description?: string;
  steps: WizardStep[];
  allowSkip?: boolean;
  allowBack?: boolean;
  autoSave?: boolean;
  saveInterval?: number; // ms
  onComplete?: (data: any) => Promise<void>;
  onCancel?: () => void;
  onSave?: (data: any) => Promise<void>;
}

export interface WizardStepProps {
  data: any;
  updateData: (updates: any) => void;
  nextStep: () => void;
  previousStep: () => void;
  isFirst: boolean;
  isLast: boolean;
  canProceed: boolean;
}

export interface WizardValidationResult {
  isValid: boolean;
  errors: string[];
  warnings?: string[];
}

export interface WizardState {
  currentStepIndex: number;
  data: any;
  completedSteps: Set<string>;
  validationResults: Map<string, WizardValidationResult>;
  isDirty: boolean;
  isLoading: boolean;
}

// === WIZARD CONTEXT ===

interface WizardContextValue {
  config: WizardConfig;
  state: WizardState;
  updateState: (updates: Partial<WizardState>) => void;
  updateData: (updates: any) => void;
  nextStep: () => void;
  previousStep: () => void;
  goToStep: (index: number) => void;
  validateCurrentStep: () => WizardValidationResult;
  completeWizard: () => Promise<void>;
  cancelWizard: () => void;
}

const WizardContext = createContext<WizardContextValue | null>(null);

export const useWizard = () => {
  const context = useContext(WizardContext);
  if (!context) {
    throw new Error('useWizard must be used within a WizardProvider');
  }
  return context;
};

// === WIZARD PROVIDER ===

interface WizardProviderProps {
  config: WizardConfig;
  initialData?: any;
  children: React.ReactNode;
}

export const WizardProvider: React.FC<WizardProviderProps> = ({
  config,
  initialData = {},
  children
}) => {
  const [state, setState] = useState<WizardState>({
    currentStepIndex: 0,
    data: initialData,
    completedSteps: new Set(),
    validationResults: new Map(),
    isDirty: false,
    isLoading: false
  });

  // Auto-save functionality
  useEffect(() => {
    if (!config.autoSave || !state.isDirty) return;

    const saveTimeout = setTimeout(async () => {
      if (config.onSave) {
        try {
          await config.onSave(state.data);
          setState(prev => ({ ...prev, isDirty: false }));
        } catch (error) {
          console.error('Auto-save failed:', error);
        }
      }
    }, config.saveInterval || 5000);

    return () => clearTimeout(saveTimeout);
  }, [state.data, state.isDirty, config.autoSave, config.saveInterval, config.onSave]);

  const updateState = useCallback((updates: Partial<WizardState>) => {
    setState(prev => ({ ...prev, ...updates }));
  }, []);

  const updateData = useCallback((updates: any) => {
    setState(prev => ({
      ...prev,
      data: { ...prev.data, ...updates },
      isDirty: true
    }));
  }, []);

  const validateCurrentStep = useCallback(() => {
    const currentStep = config.steps[state.currentStepIndex];
    if (!currentStep?.validation) {
      return { isValid: true, errors: [] };
    }
    
    const result = currentStep.validation(state.data);
    setState(prev => ({
      ...prev,
      validationResults: new Map(prev.validationResults).set(currentStep.id, result)
    }));
    
    return result;
  }, [config.steps, state.currentStepIndex, state.data]);

  const nextStep = useCallback(() => {
    const validation = validateCurrentStep();
    if (!validation.isValid) return;

    const currentStep = config.steps[state.currentStepIndex];
    const newCompletedSteps = new Set(state.completedSteps);
    newCompletedSteps.add(currentStep.id);

    setState(prev => ({
      ...prev,
      currentStepIndex: Math.min(prev.currentStepIndex + 1, config.steps.length - 1),
      completedSteps: newCompletedSteps
    }));
  }, [config.steps, state.currentStepIndex, state.completedSteps, validateCurrentStep]);

  const previousStep = useCallback(() => {
    if (!config.allowBack) return;
    
    setState(prev => ({
      ...prev,
      currentStepIndex: Math.max(prev.currentStepIndex - 1, 0)
    }));
  }, [config.allowBack]);

  const goToStep = useCallback((index: number) => {
    if (index < 0 || index >= config.steps.length) return;
    
    setState(prev => ({
      ...prev,
      currentStepIndex: index
    }));
  }, [config.steps.length]);

  const completeWizard = useCallback(async () => {
    try {
      setState(prev => ({ ...prev, isLoading: true }));
      
      if (config.onComplete) {
        await config.onComplete(state.data);
      }
    } catch (error) {
      console.error('Wizard completion failed:', error);
      throw error;
    } finally {
      setState(prev => ({ ...prev, isLoading: false }));
    }
  }, [config.onComplete, state.data]);

  const cancelWizard = useCallback(() => {
    if (config.onCancel) {
      config.onCancel();
    }
  }, [config.onCancel]);

  const contextValue: WizardContextValue = {
    config,
    state,
    updateState,
    updateData,
    nextStep,
    previousStep,
    goToStep,
    validateCurrentStep,
    completeWizard,
    cancelWizard
  };

  return (
    <WizardContext.Provider value={contextValue}>
      {children}
    </WizardContext.Provider>
  );
};

// === WIZARD COMPONENTS ===

interface WizardNavigationProps {
  className?: string;
}

export const WizardNavigation: React.FC<WizardNavigationProps> = ({ className }) => {
  const { config, state, nextStep, previousStep, validateCurrentStep } = useWizard();
  const currentStep = config.steps[state.currentStepIndex];
  const isFirst = state.currentStepIndex === 0;
  const isLast = state.currentStepIndex === config.steps.length - 1;
  
  const validation = state.validationResults.get(currentStep.id) || { isValid: true, errors: [] };
  const canProceed = validation.isValid;

  return (
    <div className={`flex justify-between items-center p-4 border-t bg-gray-50 ${className}`}>
      <button
        onClick={previousStep}
        disabled={isFirst || !config.allowBack}
        className="flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <ChevronLeftIcon className="w-4 h-4 mr-2" />
        Previous
      </button>

      <div className="text-sm text-gray-500">
        Step {state.currentStepIndex + 1} of {config.steps.length}
      </div>

      <button
        onClick={nextStep}
        disabled={!canProceed}
        className="flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isLast ? 'Complete' : 'Next'}
        {!isLast && <ChevronRightIcon className="w-4 h-4 ml-2" />}
      </button>
    </div>
  );
};

interface WizardProgressProps {
  className?: string;
}

export const WizardProgress: React.FC<WizardProgressProps> = ({ className }) => {
  const { config, state } = useWizard();
  const progressPercentage = ((state.currentStepIndex + 1) / config.steps.length) * 100;

  return (
    <div className={`p-4 ${className}`}>
      <div className="flex justify-between items-center mb-2">
        <h3 className="text-lg font-medium text-gray-900">{config.title}</h3>
        <span className="text-sm text-gray-500">
          {Math.round(progressPercentage)}% complete
        </span>
      </div>
      
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
          style={{ width: `${progressPercentage}%` }}
        />
      </div>

      <div className="flex justify-between mt-4">
        {config.steps.map((step, index) => {
          const isCompleted = state.completedSteps.has(step.id);
          const isCurrent = index === state.currentStepIndex;
          const isAccessible = index <= state.currentStepIndex;

          return (
            <div
              key={step.id}
              className={`flex flex-col items-center ${isAccessible ? 'cursor-pointer' : 'cursor-not-allowed'}`}
              onClick={() => isAccessible && useWizard().goToStep(index)}
            >
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                isCompleted
                  ? 'bg-green-500 text-white'
                  : isCurrent
                  ? 'bg-blue-600 text-white'
                  : isAccessible
                  ? 'bg-gray-300 text-gray-600'
                  : 'bg-gray-100 text-gray-400'
              }`}>
                {isCompleted ? (
                  <CheckIcon className="w-5 h-5" />
                ) : (
                  index + 1
                )}
              </div>
              <span className={`mt-1 text-xs ${
                isCurrent ? 'text-blue-600 font-medium' : 'text-gray-500'
              }`}>
                {step.title}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

interface WizardStepContentProps {
  className?: string;
}

export const WizardStepContent: React.FC<WizardStepContentProps> = ({ className }) => {
  const { config, state, updateData, nextStep, previousStep, validateCurrentStep } = useWizard();
  const currentStep = config.steps[state.currentStepIndex];
  const validation = state.validationResults.get(currentStep.id);

  if (!currentStep) return null;

  const isFirst = state.currentStepIndex === 0;
  const isLast = state.currentStepIndex === config.steps.length - 1;
  const canProceed = !validation || validation.isValid;

  const StepComponent = currentStep.component;

  return (
    <div className={`flex-1 p-6 ${className}`}>
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">{currentStep.title}</h2>
        {currentStep.description && (
          <p className="mt-2 text-gray-600">{currentStep.description}</p>
        )}
        {currentStep.estimatedTime && (
          <p className="mt-1 text-sm text-gray-500">
            Estimated time: {currentStep.estimatedTime} minutes
          </p>
        )}
      </div>

      {validation && !validation.isValid && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
          <div className="flex">
            <ExclamationTriangleIcon className="w-5 h-5 text-red-400" />
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">
                Please fix the following errors:
              </h3>
              <ul className="mt-2 text-sm text-red-700 list-disc list-inside">
                {validation.errors.map((error, index) => (
                  <li key={index}>{error}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      <StepComponent
        data={state.data}
        updateData={updateData}
        nextStep={nextStep}
        previousStep={previousStep}
        isFirst={isFirst}
        isLast={isLast}
        canProceed={canProceed}
      />
    </div>
  );
};

// === MAIN WIZARD COMPONENT ===

interface WizardManagerProps {
  config: WizardConfig;
  initialData?: any;
  className?: string;
}

export const WizardManager: React.FC<WizardManagerProps> = ({
  config,
  initialData,
  className
}) => {
  return (
    <WizardProvider config={config} initialData={initialData}>
      <div className={`min-h-screen bg-gray-50 flex flex-col ${className}`}>
        <WizardProgress className="bg-white border-b" />
        <WizardStepContent className="flex-1" />
        <WizardNavigation />
      </div>
    </WizardProvider>
  );
};

// === PREDEFINED WIZARD CONFIGURATIONS ===

export const CONTENT_UPLOAD_WIZARD: WizardConfig = {
  id: 'content-upload',
  title: 'Content Upload Wizard',
  description: 'Upload and configure your content with AI processing',
  allowBack: true,
  autoSave: true,
  steps: [
    {
      id: 'file-selection',
      title: 'Select Files',
      description: 'Choose your content files to upload',
      component: () => <div>File selection component</div>,
      order: 0,
      validation: (data) => ({
        isValid: data.files && data.files.length > 0,
        errors: data.files?.length ? [] : ['Please select at least one file']
      })
    },
    {
      id: 'metadata',
      title: 'Content Metadata',
      description: 'Add title, description, and tags',
      component: () => <div>Metadata form component</div>,
      order: 1,
      validation: (data) => ({
        isValid: data.title && data.title.length > 0,
        errors: data.title ? [] : ['Title is required']
      })
    },
    {
      id: 'ai-processing',
      title: 'AI Processing',
      description: 'Configure AI enhancement options',
      component: () => <div>AI processing options</div>,
      order: 2,
      optional: true
    },
    {
      id: 'protection',
      title: 'Content Protection',
      description: 'Set up content protection and monitoring',
      component: () => <div>Protection settings</div>,
      order: 3
    },
    {
      id: 'review',
      title: 'Review & Submit',
      description: 'Review your settings and submit',
      component: () => <div>Review component</div>,
      order: 4
    }
  ]
};

export const COLLABORATION_WIZARD: WizardConfig = {
  id: 'collaboration-setup',
  title: 'Collaboration Setup',
  description: 'Set up a new collaboration project',
  allowBack: true,
  steps: [
    {
      id: 'project-details',
      title: 'Project Details',
      component: () => <div>Project details form</div>,
      order: 0
    },
    {
      id: 'collaborators',
      title: 'Add Collaborators',
      component: () => <div>Collaborator selection</div>,
      order: 1
    },
    {
      id: 'permissions',
      title: 'Set Permissions',
      component: () => <div>Permission settings</div>,
      order: 2
    },
    {
      id: 'timeline',
      title: 'Project Timeline',
      component: () => <div>Timeline setup</div>,
      order: 3
    }
  ]
};

export default WizardManager;