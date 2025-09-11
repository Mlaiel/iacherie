/**
 * 🔄 Flows Manager - Enterprise Business Flow UI Components
 * 
 * @fileoverview Advanced UI flows for complex business processes and user journeys
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @copyright 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
 */

import React, { useState, useCallback, useRef, useEffect } from 'react';
import { 
  PlayIcon, 
  PauseIcon, 
  StopIcon, 
  ChevronRightIcon,
  ChevronLeftIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  UserIcon
} from '@heroicons/react/24/outline';

export interface FlowStep {
  id: string;
  title: string;
  description: string;
  type: 'action' | 'decision' | 'input' | 'wait' | 'validation' | 'completion';
  status: 'pending' | 'active' | 'completed' | 'failed' | 'skipped';
  component?: React.ComponentType<FlowStepProps>;
  validation?: (data: any) => Promise<ValidationResult>;
  data?: any;
  position: { x: number; y: number };
  connections: string[];
}

export interface FlowDefinition {
  id: string;
  name: string;
  description: string;
  category: 'onboarding' | 'content_creation' | 'monetization' | 'collaboration' | 'analytics';
  steps: FlowStep[];
  metadata: FlowMetadata;
}

export interface FlowMetadata {
  estimatedDuration: number; // minutes
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  prerequisites: string[];
  outcomes: string[];
  tags: string[];
}

export interface FlowExecution {
  id: string;
  flowId: string;
  currentStepId: string;
  status: 'running' | 'paused' | 'completed' | 'failed';
  progress: number; // 0-100
  data: Record<string, any>;
  startedAt: number;
  completedAt?: number;
  logs: FlowLog[];
}

export interface FlowLog {
  timestamp: number;
  stepId: string;
  action: string;
  data?: any;
}

export interface FlowStepProps {
  step: FlowStep;
  execution: FlowExecution;
  onNext: (data?: any) => void;
  onPrevious: () => void;
  onComplete: (data?: any) => void;
  onSkip: () => void;
  onRetry: () => void;
}

export interface ValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

/**
 * Predefined Business Flows
 */

// Content Creation Flow
export const ContentCreationFlow: FlowDefinition = {
  id: 'content_creation_v2',
  name: 'Content Creation Wizard',
  description: 'Step-by-step content creation with AI assistance',
  category: 'content_creation',
  steps: [
    {
      id: 'content_type',
      title: 'Choose Content Type',
      description: 'Select the type of content you want to create',
      type: 'decision',
      status: 'pending',
      position: { x: 100, y: 100 },
      connections: ['content_upload', 'ai_generation'],
      data: {
        options: [
          { id: 'upload', label: 'Upload Existing Content', icon: '📁' },
          { id: 'ai_generate', label: 'AI-Generated Content', icon: '🤖' },
          { id: 'record_live', label: 'Record Live', icon: '🎙️' },
          { id: 'collaborative', label: 'Collaborative Creation', icon: '👥' }
        ]
      }
    },
    {
      id: 'content_upload',
      title: 'Upload Content',
      description: 'Upload your audio, video, or image files',
      type: 'input',
      status: 'pending',
      position: { x: 300, y: 50 },
      connections: ['metadata_input'],
      component: ContentUploadStep
    },
    {
      id: 'ai_generation',
      title: 'AI Content Generation',
      description: 'Generate content using AI with your prompts',
      type: 'action',
      status: 'pending',
      position: { x: 300, y: 150 },
      connections: ['metadata_input'],
      component: AIGenerationStep
    },
    {
      id: 'metadata_input',
      title: 'Content Details',
      description: 'Add title, description, tags, and other metadata',
      type: 'input',
      status: 'pending',
      position: { x: 500, y: 100 },
      connections: ['ai_enhancement'],
      component: MetadataInputStep,
      validation: async (data) => {
        const errors = [];
        if (!data.title || data.title.length < 3) errors.push('Title must be at least 3 characters');
        if (!data.description) errors.push('Description is required');
        return { isValid: errors.length === 0, errors, warnings: [] };
      }
    },
    {
      id: 'ai_enhancement',
      title: 'AI Enhancement',
      description: 'Apply AI enhancements to improve content quality',
      type: 'action',
      status: 'pending',
      position: { x: 700, y: 100 },
      connections: ['preview_review'],
      component: AIEnhancementStep
    },
    {
      id: 'preview_review',
      title: 'Preview & Review',
      description: 'Review your content before publishing',
      type: 'validation',
      status: 'pending',
      position: { x: 900, y: 100 },
      connections: ['publish_options'],
      component: PreviewReviewStep
    },
    {
      id: 'publish_options',
      title: 'Publishing Options',
      description: 'Choose where and how to publish your content',
      type: 'decision',
      status: 'pending',
      position: { x: 1100, y: 100 },
      connections: ['completion'],
      component: PublishOptionsStep
    },
    {
      id: 'completion',
      title: 'Content Published',
      description: 'Your content has been successfully published',
      type: 'completion',
      status: 'pending',
      position: { x: 1300, y: 100 },
      connections: [],
      component: CompletionStep
    }
  ],
  metadata: {
    estimatedDuration: 15,
    difficulty: 'beginner',
    prerequisites: ['verified_account'],
    outcomes: ['published_content', 'analytics_tracking', 'monetization_setup'],
    tags: ['content', 'ai', 'publishing', 'wizard']
  }
};

// User Onboarding Flow
export const UserOnboardingFlow: FlowDefinition = {
  id: 'user_onboarding_v3',
  name: 'Creator Onboarding Journey',
  description: 'Complete onboarding flow for new creators',
  category: 'onboarding',
  steps: [
    {
      id: 'welcome',
      title: 'Welcome to Ainflue',
      description: 'Get started with the creator economy platform',
      type: 'action',
      status: 'pending',
      position: { x: 100, y: 100 },
      connections: ['profile_setup'],
      component: WelcomeStep
    },
    {
      id: 'profile_setup',
      title: 'Setup Your Profile',
      description: 'Tell us about yourself and your creative work',
      type: 'input',
      status: 'pending',
      position: { x: 300, y: 100 },
      connections: ['creator_type'],
      component: ProfileSetupStep
    },
    {
      id: 'creator_type',
      title: 'Choose Creator Type',
      description: 'Select your primary content creation focus',
      type: 'decision',
      status: 'pending',
      position: { x: 500, y: 100 },
      connections: ['preferences'],
      data: {
        options: [
          { id: 'musician', label: 'Musician', icon: '🎵', description: 'Create and share music' },
          { id: 'blogger', label: 'Blogger', icon: '✍️', description: 'Write and publish articles' },
          { id: 'photographer', label: 'Photographer', icon: '📸', description: 'Share visual content' },
          { id: 'podcaster', label: 'Podcaster', icon: '🎙️', description: 'Audio content creation' },
          { id: 'video_creator', label: 'Video Creator', icon: '🎬', description: 'Video content production' }
        ]
      }
    },
    {
      id: 'preferences',
      title: 'Customize Preferences',
      description: 'Set your content preferences and monetization goals',
      type: 'input',
      status: 'pending',
      position: { x: 700, y: 100 },
      connections: ['ai_recommendations'],
      component: PreferencesStep
    },
    {
      id: 'ai_recommendations',
      title: 'AI-Powered Recommendations',
      description: 'Get personalized recommendations based on your profile',
      type: 'action',
      status: 'pending',
      position: { x: 900, y: 100 },
      connections: ['first_content'],
      component: AIRecommendationsStep
    },
    {
      id: 'first_content',
      title: 'Create Your First Content',
      description: 'Upload or create your first piece of content',
      type: 'input',
      status: 'pending',
      position: { x: 1100, y: 100 },
      connections: ['community_intro'],
      component: FirstContentStep
    },
    {
      id: 'community_intro',
      title: 'Join the Community',
      description: 'Connect with other creators and explore collaboration opportunities',
      type: 'action',
      status: 'pending',
      position: { x: 1300, y: 100 },
      connections: ['onboarding_complete'],
      component: CommunityIntroStep
    },
    {
      id: 'onboarding_complete',
      title: 'Welcome to the Creator Economy!',
      description: 'You\'re all set to start creating and earning',
      type: 'completion',
      status: 'pending',
      position: { x: 1500, y: 100 },
      connections: [],
      component: OnboardingCompleteStep
    }
  ],
  metadata: {
    estimatedDuration: 25,
    difficulty: 'beginner',
    prerequisites: [],
    outcomes: ['complete_profile', 'first_content', 'community_connection', 'monetization_setup'],
    tags: ['onboarding', 'profile', 'community', 'getting_started']
  }
};

/**
 * Flow Step Components
 */

const ContentUploadStep: React.FC<FlowStepProps> = ({ step, execution, onNext }) => {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    setSelectedFiles(files);
  };

  const handleNext = () => {
    if (selectedFiles.length > 0) {
      onNext({ files: selectedFiles });
    }
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow-lg">
      <h3 className="text-xl font-semibold mb-4">{step.title}</h3>
      <p className="text-gray-600 mb-6">{step.description}</p>
      
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept="audio/*,video/*,image/*"
          onChange={handleFileSelect}
          className="hidden"
        />
        
        <div className="mb-4">
          <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
            <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </div>
        
        <p className="text-lg text-gray-600 mb-2">Drop files here or click to browse</p>
        <p className="text-sm text-gray-400 mb-4">Supports audio, video, and image files up to 500MB</p>
        
        <button
          onClick={() => fileInputRef.current?.click()}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Browse Files
        </button>
      </div>

      {selectedFiles.length > 0 && (
        <div className="mt-6">
          <h4 className="font-medium mb-3">Selected Files:</h4>
          <div className="space-y-2">
            {selectedFiles.map((file, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="font-medium">{file.name}</span>
                <span className="text-sm text-gray-500">{(file.size / 1024 / 1024).toFixed(2)} MB</span>
              </div>
            ))}
          </div>
          
          <button
            onClick={handleNext}
            className="mt-4 w-full px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center justify-center"
          >
            Continue with Selected Files
            <ChevronRightIcon className="ml-2 h-5 w-5" />
          </button>
        </div>
      )}
    </div>
  );
};

const AIGenerationStep: React.FC<FlowStepProps> = ({ step, onNext }) => {
  const [prompt, setPrompt] = useState('');
  const [contentType, setContentType] = useState('audio');
  const [generating, setGenerating] = useState(false);

  const handleGenerate = async () => {
    if (!prompt.trim()) return;
    
    setGenerating(true);
    
    // Simulate AI generation
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    setGenerating(false);
    onNext({ 
      generated: true, 
      prompt, 
      contentType,
      generatedContent: {
        url: '/generated/content.mp3',
        type: contentType,
        duration: 180
      }
    });
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow-lg">
      <h3 className="text-xl font-semibold mb-4">{step.title}</h3>
      <p className="text-gray-600 mb-6">{step.description}</p>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Content Type</label>
          <select
            value={contentType}
            onChange={(e) => setContentType(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="audio">Audio/Music</option>
            <option value="image">Image/Artwork</option>
            <option value="text">Text/Blog Post</option>
            <option value="video">Video Script</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">AI Generation Prompt</label>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Describe what you want to create..."
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <button
          onClick={handleGenerate}
          disabled={!prompt.trim() || generating}
          className="w-full px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
        >
          {generating ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
              Generating Content...
            </>
          ) : (
            <>
              Generate with AI
              <ChevronRightIcon className="ml-2 h-5 w-5" />
            </>
          )}
        </button>
      </div>
    </div>
  );
};

const MetadataInputStep: React.FC<FlowStepProps> = ({ step, execution, onNext }) => {
  const [metadata, setMetadata] = useState({
    title: '',
    description: '',
    tags: [] as string[],
    category: '',
    privacy: 'public'
  });

  const handleNext = async () => {
    if (step.validation) {
      const validation = await step.validation(metadata);
      if (!validation.isValid) {
        alert(validation.errors.join('\n'));
        return;
      }
    }
    
    onNext(metadata);
  };

  const addTag = (tag: string) => {
    if (tag && !metadata.tags.includes(tag)) {
      setMetadata(prev => ({
        ...prev,
        tags: [...prev.tags, tag]
      }));
    }
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow-lg">
      <h3 className="text-xl font-semibold mb-4">{step.title}</h3>
      <p className="text-gray-600 mb-6">{step.description}</p>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Title *</label>
          <input
            type="text"
            value={metadata.title}
            onChange={(e) => setMetadata(prev => ({ ...prev, title: e.target.value }))}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Enter a compelling title..."
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Description *</label>
          <textarea
            value={metadata.description}
            onChange={(e) => setMetadata(prev => ({ ...prev, description: e.target.value }))}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Describe your content..."
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
          <select
            value={metadata.category}
            onChange={(e) => setMetadata(prev => ({ ...prev, category: e.target.value }))}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">Select a category</option>
            <option value="music">Music</option>
            <option value="podcast">Podcast</option>
            <option value="video">Video</option>
            <option value="blog">Blog</option>
            <option value="photo">Photography</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Tags</label>
          <div className="flex flex-wrap gap-2 mb-2">
            {metadata.tags.map((tag, index) => (
              <span key={index} className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full">
                {tag}
              </span>
            ))}
          </div>
          <input
            type="text"
            placeholder="Add tags (press Enter)"
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                addTag(e.currentTarget.value);
                e.currentTarget.value = '';
              }
            }}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Privacy</label>
          <select
            value={metadata.privacy}
            onChange={(e) => setMetadata(prev => ({ ...prev, privacy: e.target.value }))}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="public">Public</option>
            <option value="unlisted">Unlisted</option>
            <option value="private">Private</option>
            <option value="members_only">Members Only</option>
          </select>
        </div>

        <button
          onClick={handleNext}
          disabled={!metadata.title || !metadata.description}
          className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
        >
          Continue to Enhancement
          <ChevronRightIcon className="ml-2 h-5 w-5" />
        </button>
      </div>
    </div>
  );
};

// Placeholder components for other steps
const AIEnhancementStep: React.FC<FlowStepProps> = ({ step, onNext }) => (
  <div className="p-6 bg-white rounded-lg shadow-lg">
    <h3 className="text-xl font-semibold mb-4">{step.title}</h3>
    <p className="text-gray-600 mb-6">{step.description}</p>
    <button onClick={() => onNext()} className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
      Apply AI Enhancement
    </button>
  </div>
);

const PreviewReviewStep: React.FC<FlowStepProps> = ({ step, onNext }) => (
  <div className="p-6 bg-white rounded-lg shadow-lg">
    <h3 className="text-xl font-semibold mb-4">{step.title}</h3>
    <p className="text-gray-600 mb-6">{step.description}</p>
    <button onClick={() => onNext()} className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700">
      Approve & Continue
    </button>
  </div>
);

const PublishOptionsStep: React.FC<FlowStepProps> = ({ step, onNext }) => (
  <div className="p-6 bg-white rounded-lg shadow-lg">
    <h3 className="text-xl font-semibold mb-4">{step.title}</h3>
    <p className="text-gray-600 mb-6">{step.description}</p>
    <button onClick={() => onNext()} className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700">
      Publish Now
    </button>
  </div>
);

const CompletionStep: React.FC<FlowStepProps> = ({ step, onComplete }) => (
  <div className="p-6 bg-white rounded-lg shadow-lg text-center">
    <CheckCircleIcon className="h-16 w-16 text-green-500 mx-auto mb-4" />
    <h3 className="text-xl font-semibold mb-4">{step.title}</h3>
    <p className="text-gray-600 mb-6">{step.description}</p>
    <button onClick={() => onComplete()} className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700">
      Complete
    </button>
  </div>
);

// Onboarding step components (placeholders)
const WelcomeStep: React.FC<FlowStepProps> = ({ step, onNext }) => (
  <div className="p-6 bg-white rounded-lg shadow-lg text-center">
    <h3 className="text-2xl font-bold mb-4">Welcome to Ainflue! 🎉</h3>
    <p className="text-gray-600 mb-6">Let's get you set up as a creator</p>
    <button onClick={() => onNext()} className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
      Get Started
    </button>
  </div>
);

const ProfileSetupStep: React.FC<FlowStepProps> = ({ step, onNext }) => (
  <div className="p-6 bg-white rounded-lg shadow-lg">
    <h3 className="text-xl font-semibold mb-4">{step.title}</h3>
    <p className="text-gray-600 mb-6">{step.description}</p>
    <button onClick={() => onNext()} className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
      Complete Profile
    </button>
  </div>
);

const PreferencesStep: React.FC<FlowStepProps> = ({ step, onNext }) => (
  <div className="p-6 bg-white rounded-lg shadow-lg">
    <h3 className="text-xl font-semibold mb-4">{step.title}</h3>
    <p className="text-gray-600 mb-6">{step.description}</p>
    <button onClick={() => onNext()} className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
      Save Preferences
    </button>
  </div>
);

const AIRecommendationsStep: React.FC<FlowStepProps> = ({ step, onNext }) => (
  <div className="p-6 bg-white rounded-lg shadow-lg">
    <h3 className="text-xl font-semibold mb-4">{step.title}</h3>
    <p className="text-gray-600 mb-6">{step.description}</p>
    <button onClick={() => onNext()} className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700">
      View Recommendations
    </button>
  </div>
);

const FirstContentStep: React.FC<FlowStepProps> = ({ step, onNext }) => (
  <div className="p-6 bg-white rounded-lg shadow-lg">
    <h3 className="text-xl font-semibold mb-4">{step.title}</h3>
    <p className="text-gray-600 mb-6">{step.description}</p>
    <button onClick={() => onNext()} className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700">
      Create Content
    </button>
  </div>
);

const CommunityIntroStep: React.FC<FlowStepProps> = ({ step, onNext }) => (
  <div className="p-6 bg-white rounded-lg shadow-lg">
    <h3 className="text-xl font-semibold mb-4">{step.title}</h3>
    <p className="text-gray-600 mb-6">{step.description}</p>
    <button onClick={() => onNext()} className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
      Join Community
    </button>
  </div>
);

const OnboardingCompleteStep: React.FC<FlowStepProps> = ({ step, onComplete }) => (
  <div className="p-6 bg-white rounded-lg shadow-lg text-center">
    <CheckCircleIcon className="h-16 w-16 text-green-500 mx-auto mb-4" />
    <h3 className="text-2xl font-bold mb-4">{step.title}</h3>
    <p className="text-gray-600 mb-6">{step.description}</p>
    <button onClick={() => onComplete()} className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700">
      Start Creating!
    </button>
  </div>
);

/**
 * Main Flow Manager Component
 */
export interface FlowsManagerProps {
  className?: string;
}

export const FlowsManager: React.FC<FlowsManagerProps> = ({ className = '' }) => {
  const [availableFlows] = useState<FlowDefinition[]>([
    ContentCreationFlow,
    UserOnboardingFlow
  ]);
  
  const [activeExecution, setActiveExecution] = useState<FlowExecution | null>(null);
  const [selectedFlow, setSelectedFlow] = useState<FlowDefinition | null>(null);

  const startFlow = useCallback((flow: FlowDefinition) => {
    const execution: FlowExecution = {
      id: `exec_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      flowId: flow.id,
      currentStepId: flow.steps[0].id,
      status: 'running',
      progress: 0,
      data: {},
      startedAt: Date.now(),
      logs: [{
        timestamp: Date.now(),
        stepId: flow.steps[0].id,
        action: 'flow_started'
      }]
    };
    
    setActiveExecution(execution);
    setSelectedFlow(flow);
  }, []);

  const handleStepNext = useCallback((data?: any) => {
    if (!activeExecution || !selectedFlow) return;

    const currentStepIndex = selectedFlow.steps.findIndex(s => s.id === activeExecution.currentStepId);
    const nextStepIndex = currentStepIndex + 1;
    
    if (nextStepIndex < selectedFlow.steps.length) {
      const nextStep = selectedFlow.steps[nextStepIndex];
      setActiveExecution(prev => prev ? {
        ...prev,
        currentStepId: nextStep.id,
        progress: Math.round((nextStepIndex / selectedFlow.steps.length) * 100),
        data: { ...prev.data, [activeExecution.currentStepId]: data },
        logs: [...prev.logs, {
          timestamp: Date.now(),
          stepId: nextStep.id,
          action: 'step_advanced',
          data
        }]
      } : null);
    } else {
      // Flow completed
      setActiveExecution(prev => prev ? {
        ...prev,
        status: 'completed',
        progress: 100,
        completedAt: Date.now(),
        data: { ...prev.data, [activeExecution.currentStepId]: data }
      } : null);
    }
  }, [activeExecution, selectedFlow]);

  const handleStepComplete = useCallback((data?: any) => {
    if (!activeExecution) return;
    
    setActiveExecution(prev => prev ? {
      ...prev,
      status: 'completed',
      progress: 100,
      completedAt: Date.now(),
      data: { ...prev.data, [activeExecution.currentStepId]: data }
    } : null);
  }, [activeExecution]);

  const resetFlow = useCallback(() => {
    setActiveExecution(null);
    setSelectedFlow(null);
  }, []);

  if (activeExecution && selectedFlow) {
    const currentStep = selectedFlow.steps.find(s => s.id === activeExecution.currentStepId);
    const StepComponent = currentStep?.component;

    return (
      <div className={`flows-manager ${className}`}>
        {/* Progress Header */}
        <div className="bg-white shadow-sm border-b p-4">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-xl font-semibold">{selectedFlow.name}</h2>
              <p className="text-gray-600">{selectedFlow.description}</p>
            </div>
            <button
              onClick={resetFlow}
              className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
            >
              Exit Flow
            </button>
          </div>
          
          {/* Progress Bar */}
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${activeExecution.progress}%` }}
            />
          </div>
          <div className="flex justify-between text-sm text-gray-500 mt-2">
            <span>Step {selectedFlow.steps.findIndex(s => s.id === activeExecution.currentStepId) + 1} of {selectedFlow.steps.length}</span>
            <span>{activeExecution.progress}% Complete</span>
          </div>
        </div>

        {/* Current Step */}
        <div className="p-6">
          {currentStep && StepComponent && (
            <StepComponent
              step={currentStep}
              execution={activeExecution}
              onNext={handleStepNext}
              onPrevious={() => {}} // TODO: Implement
              onComplete={handleStepComplete}
              onSkip={() => {}} // TODO: Implement
              onRetry={() => {}} // TODO: Implement
            />
          )}
        </div>
      </div>
    );
  }

  return (
    <div className={`flows-manager ${className}`}>
      <div className="p-6">
        <h2 className="text-2xl font-bold mb-6">Business Flows</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {availableFlows.map((flow) => (
            <div key={flow.id} className="bg-white rounded-lg shadow-lg p-6 border border-gray-200">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-semibold">{flow.name}</h3>
                <span className={`px-3 py-1 text-sm rounded-full ${
                  flow.metadata.difficulty === 'beginner' ? 'bg-green-100 text-green-800' :
                  flow.metadata.difficulty === 'intermediate' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {flow.metadata.difficulty}
                </span>
              </div>
              
              <p className="text-gray-600 mb-4">{flow.description}</p>
              
              <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                <span className="flex items-center">
                  <ClockIcon className="h-4 w-4 mr-1" />
                  ~{flow.metadata.estimatedDuration} min
                </span>
                <span>{flow.steps.length} steps</span>
              </div>
              
              <div className="flex flex-wrap gap-2 mb-4">
                {flow.metadata.tags.slice(0, 3).map((tag) => (
                  <span key={tag} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                    {tag}
                  </span>
                ))}
              </div>
              
              <button
                onClick={() => startFlow(flow)}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center"
              >
                Start Flow
                <PlayIcon className="ml-2 h-4 w-4" />
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default FlowsManager;