/**
 * Business Logic Hooks - Production Grade
 * Custom React hooks for business operations
 * @module lib/hooks/business
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import { useContentStore, Content, ContentType, ProcessingStatus } from '@/lib/store/content';
import { useApplicationStore, NotificationLevel } from '@/lib/store/application';

/**
 * Content generation request
 */
interface ContentGenerationRequest {
  type: ContentType;
  prompt: string;
  model?: string;
  parameters?: Record<string, any>;
}

/**
 * Hook: Generate AI content
 */
export function useContentGeneration() {
  const addContent = useContentStore((state) => state.addContent);
  const updateContent = useContentStore((state) => state.updateContent);
  const addNotification = useApplicationStore((state) => state.addNotification);
  
  return useMutation({
    mutationFn: async (request: ContentGenerationRequest) => {
      return apiClient.post<Content>('/api/v1/content/generate', request);
    },
    onMutate: (variables) => {
      // Optimistic update
      const tempContent: Content = {
        id: `temp-${Date.now()}`,
        type: variables.type,
        title: `Generating ${variables.type.toLowerCase()}...`,
        status: ProcessingStatus.QUEUED,
        progress: 0,
        metadata: {
          aiGenerated: true,
          model: variables.model,
          prompt: variables.prompt,
        },
        tags: [],
        createdAt: Date.now(),
        updatedAt: Date.now(),
        createdBy: 'current-user',
      };
      
      addContent(tempContent);
      return { tempId: tempContent.id };
    },
    onSuccess: (data, variables, context) => {
      // Replace temp content with real one
      if (context) {
        useContentStore.getState().removeContent(context.tempId);
        addContent(data);
      }
      
      addNotification({
        level: NotificationLevel.SUCCESS,
        title: 'Content Generated',
        message: `Your ${data.type.toLowerCase()} has been generated successfully.`,
      });
    },
    onError: (error, variables, context) => {
      if (context) {
        updateContent(context.tempId, {
          status: ProcessingStatus.FAILED,
        });
      }
      
      addNotification({
        level: NotificationLevel.ERROR,
        title: 'Generation Failed',
        message: error instanceof Error ? error.message : 'Failed to generate content',
      });
    },
  });
}

/**
 * Hook: Fetch user content list
 */
export function useContentList() {
  return useQuery({
    queryKey: ['content', 'list'],
    queryFn: () => apiClient.get<Content[]>('/api/v1/content'),
    staleTime: 60 * 1000, // 1 minute
  });
}

/**
 * Hook: Fetch single content details
 */
export function useContentDetails(id: string) {
  return useQuery({
    queryKey: ['content', 'details', id],
    queryFn: () => apiClient.get<Content>(`/api/v1/content/${id}`),
    enabled: !!id,
  });
}

/**
 * Hook: Delete content
 */
export function useContentDeletion() {
  const queryClient = useQueryClient();
  const removeContent = useContentStore((state) => state.removeContent);
  const addNotification = useApplicationStore((state) => state.addNotification);
  
  return useMutation({
    mutationFn: (id: string) => apiClient.delete(`/api/v1/content/${id}`),
    onSuccess: (_, id) => {
      removeContent(id);
      queryClient.invalidateQueries({ queryKey: ['content'] });
      
      addNotification({
        level: NotificationLevel.SUCCESS,
        title: 'Content Deleted',
        message: 'Content has been removed successfully.',
      });
    },
    onError: (error) => {
      addNotification({
        level: NotificationLevel.ERROR,
        title: 'Deletion Failed',
        message: error instanceof Error ? error.message : 'Failed to delete content',
      });
    },
  });
}

/**
 * Analytics metrics
 */
interface AnalyticsMetrics {
  totalContent: number;
  contentByType: Record<ContentType, number>;
  processingQueue: number;
  successRate: number;
  storageUsed: number;
  apiCallsToday: number;
  creditsRemaining: number;
}

/**
 * Hook: Fetch analytics metrics
 */
export function useAnalyticsMetrics() {
  return useQuery({
    queryKey: ['analytics', 'metrics'],
    queryFn: () => apiClient.get<AnalyticsMetrics>('/api/v1/analytics/metrics'),
    refetchInterval: 30 * 1000, // Refetch every 30 seconds
  });
}

/**
 * AI model configuration
 */
interface AIModelConfig {
  id: string;
  name: string;
  type: 'text' | 'image' | 'audio' | 'video';
  provider: string;
  costPerRequest: number;
  averageLatency: number;
  available: boolean;
}

/**
 * Hook: Fetch available AI models
 */
export function useAIModels(type?: 'text' | 'image' | 'audio' | 'video') {
  return useQuery({
    queryKey: ['ai-models', type],
    queryFn: () => apiClient.get<AIModelConfig[]>('/api/v1/ai/models', { type }),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * User subscription info
 */
interface SubscriptionInfo {
  tier: string;
  status: 'active' | 'expired' | 'cancelled';
  expiresAt: number;
  credits: {
    total: number;
    used: number;
    remaining: number;
  };
  limits: {
    contentPerMonth: number;
    storageGB: number;
    apiCallsPerDay: number;
  };
  usage: {
    contentThisMonth: number;
    storageUsedGB: number;
    apiCallsToday: number;
  };
}

/**
 * Hook: Fetch subscription info
 */
export function useSubscription() {
  return useQuery({
    queryKey: ['subscription', 'info'],
    queryFn: () => apiClient.get<SubscriptionInfo>('/api/v1/subscription'),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

/**
 * Hook: Upgrade subscription
 */
export function useSubscriptionUpgrade() {
  const queryClient = useQueryClient();
  const addNotification = useApplicationStore((state) => state.addNotification);
  
  return useMutation({
    mutationFn: (tier: string) => 
      apiClient.post('/api/v1/subscription/upgrade', { tier }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subscription'] });
      
      addNotification({
        level: NotificationLevel.SUCCESS,
        title: 'Subscription Upgraded',
        message: 'Your subscription has been upgraded successfully.',
      });
    },
    onError: (error) => {
      addNotification({
        level: NotificationLevel.ERROR,
        title: 'Upgrade Failed',
        message: error instanceof Error ? error.message : 'Failed to upgrade subscription',
      });
    },
  });
}

/**
 * Real-time collaboration session
 */
interface CollaborationSession {
  id: string;
  contentId: string;
  participants: Array<{
    id: string;
    name: string;
    avatar?: string;
    cursor?: { x: number; y: number };
  }>;
  locked: boolean;
  lockedBy?: string;
}

/**
 * Hook: Collaboration session
 */
export function useCollaborationSession(contentId: string) {
  return useQuery({
    queryKey: ['collaboration', 'session', contentId],
    queryFn: () => 
      apiClient.get<CollaborationSession>(`/api/v1/collaboration/session/${contentId}`),
    enabled: !!contentId,
    refetchInterval: 5 * 1000, // Refetch every 5 seconds for real-time updates
  });
}
