/**
 * 🎯 PLATFORM SERVICES HOOKS - 65+ PLATFORMS INTEGRATION
 * Hooks spécialisés pour la gestion des 65+ plateformes
 * 
 * @author Fahed Mlaiel - Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + DevOps
 * @date 25 Septembre 2025
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import { apiClient, API_ENDPOINTS, type APIResponse } from '@/lib/api-client';

// ============================================================================
// TYPES POUR PLATFORM SERVICES
// ============================================================================

export interface Platform {
  id: string;
  name: string;
  category: 'Social Media' | 'Music Streaming' | 'Video Platform' | 'Podcast' | 'Blog' | 'E-commerce';
  status: 'connected' | 'disconnected' | 'error' | 'syncing';
  apiStatus: 'healthy' | 'degraded' | 'down';
  lastSync: string;
  syncFrequency: string;
  contentCount: number;
  engagement: {
    views: number;
    likes: number;
    shares: number;
    comments: number;
  };
  reach: number;
  revenue?: number;
  apiLimits: {
    used: number;
    total: number;
    resetTime: string;
  };
}

export interface ContentDistribution {
  id: string;
  contentId: string;
  title: string;
  platforms: string[];
  status: 'scheduled' | 'publishing' | 'published' | 'failed';
  publishDate: string;
  results: {
    [platformId: string]: {
      status: 'success' | 'failed' | 'pending';
      url?: string;
      error?: string;
      engagement?: {
        views: number;
        interactions: number;
      };
    };
  };
}

export interface PlatformAnalytics {
  platformId: string;
  platformName: string;
  period: string;
  metrics: {
    totalViews: number;
    totalEngagement: number;
    followerGrowth: number;
    reachGrowth: number;
    conversionRate: number;
    revenue: number;
  };
  topContent: Array<{
    id: string;
    title: string;
    views: number;
    engagement: number;
  }>;
}

export interface SyncSchedule {
  id: string;
  platformId: string;
  frequency: 'real-time' | 'hourly' | 'daily' | 'weekly';
  nextSync: string;
  enabled: boolean;
  lastResult: 'success' | 'failed' | 'partial';
}

// ============================================================================
// HOOK PRINCIPAL PLATFORM SERVICES
// ============================================================================

export const usePlatformServices = () => {
  const [data, setData] = useState<APIResponse>({ data: null, loading: true, error: null, status: null });
  const [platforms, setPlatforms] = useState<Platform[]>([]);
  const [distributions, setDistributions] = useState<ContentDistribution[]>([]);
  const [analytics, setAnalytics] = useState<PlatformAnalytics[]>([]);
  const [schedules, setSchedules] = useState<SyncSchedule[]>([]);

  const fetchPlatformServices = useCallback(async () => {
    try {
      setData(prev => ({ ...prev, loading: true, error: null }));
      
      const [servicesResponse, platformsResponse, distributionsResponse, analyticsResponse, schedulesResponse] = await Promise.all([
        apiClient.get(API_ENDPOINTS.PLATFORMS + '/status'),
        apiClient.get(API_ENDPOINTS.PLATFORMS + '/list'),
        apiClient.get(API_ENDPOINTS.PLATFORMS + '/distributions'),
        apiClient.get(API_ENDPOINTS.PLATFORMS + '/analytics'),
        apiClient.get(API_ENDPOINTS.PLATFORMS + '/sync/schedules')
      ]);

      setData({ data: servicesResponse, loading: false, error: null, status: 200 });
      setPlatforms((platformsResponse as any)?.platforms || []);
      setDistributions((distributionsResponse as any)?.distributions || []);
      setAnalytics((analyticsResponse as any)?.analytics || []);
      setSchedules((schedulesResponse as any)?.schedules || []);
      
    } catch (error) {
      setData({ 
        data: null, 
        loading: false, 
        error: error instanceof Error ? error.message : 'Unknown error', 
        status: 500 
      });
    }
  }, []);

  useEffect(() => {
    fetchPlatformServices();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchPlatformServices, 30000);
    return () => clearInterval(interval);
  }, [fetchPlatformServices]);

  return {
    ...data,
    platforms,
    distributions,
    analytics,
    schedules,
    refetch: fetchPlatformServices,
    
    // Platform Connection Management
    connectPlatform: async (platformId: string, credentials: any) => {
      return apiClient.post(API_ENDPOINTS.PLATFORMS + `/${platformId}/connect`, credentials);
    },
    
    disconnectPlatform: async (platformId: string) => {
      return apiClient.post(API_ENDPOINTS.PLATFORMS + `/${platformId}/disconnect`);
    },
    
    testConnection: async (platformId: string) => {
      return apiClient.post(API_ENDPOINTS.PLATFORMS + `/${platformId}/test`);
    },
    
    // Content Distribution
    scheduleDistribution: async (contentId: string, platforms: string[], publishDate: string) => {
      return apiClient.post(API_ENDPOINTS.PLATFORMS + '/distribute', {
        contentId,
        platforms,
        publishDate
      });
    },
    
    publishNow: async (contentId: string, platforms: string[]) => {
      return apiClient.post(API_ENDPOINTS.PLATFORMS + '/publish', {
        contentId,
        platforms
      });
    },
    
    cancelDistribution: async (distributionId: string) => {
      return apiClient.post(API_ENDPOINTS.PLATFORMS + `/distributions/${distributionId}/cancel`);
    },
    
    // Platform Sync Management
    triggerSync: async (platformId: string) => {
      return apiClient.post(API_ENDPOINTS.PLATFORMS + `/${platformId}/sync`);
    },
    
    updateSyncSchedule: async (scheduleId: string, schedule: Partial<SyncSchedule>) => {
      return apiClient.put(API_ENDPOINTS.PLATFORMS + `/sync/schedules/${scheduleId}`, schedule);
    },
    
    // Analytics & Reporting
    getPlatformAnalytics: async (platformId: string, period: string) => {
      return apiClient.get(`${API_ENDPOINTS.PLATFORMS}/${platformId}/analytics?period=${period}`);
    },
    
    getCrossPlatformReport: async (period: string) => {
      return apiClient.get(`${API_ENDPOINTS.PLATFORMS}/reports/cross-platform?period=${period}`);
    },
    
    // API Rate Limiting
    getAPIUsage: async (platformId: string) => {
      return apiClient.get(API_ENDPOINTS.PLATFORMS + `/${platformId}/api-usage`);
    }
  };
};

// ============================================================================
// HOOK POUR CONTENT DISTRIBUTION
// ============================================================================

export const useContentDistribution = () => {
  const [distributions, setDistributions] = useState<ContentDistribution[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDistributions = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiClient.get(API_ENDPOINTS.PLATFORMS + '/distributions');
      setDistributions((response as any)?.distributions || []);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDistributions();
    
    // Real-time updates every 15 seconds for active distributions
    const interval = setInterval(fetchDistributions, 15000);
    return () => clearInterval(interval);
  }, [fetchDistributions]);

  return {
    distributions,
    loading,
    error,
    refetch: fetchDistributions,
    
    // Distribution Operations
    retryFailedDistribution: async (distributionId: string, platformId: string) => {
      return apiClient.post(API_ENDPOINTS.PLATFORMS + `/distributions/${distributionId}/retry/${platformId}`);
    },
    
    getDistributionLogs: async (distributionId: string) => {
      return apiClient.get(API_ENDPOINTS.PLATFORMS + `/distributions/${distributionId}/logs`);
    }
  };
};

// ============================================================================
// HOOK POUR PLATFORM ANALYTICS
// ============================================================================

export const usePlatformAnalytics = () => {
  const [analyticsData, setAnalyticsData] = useState<PlatformAnalytics[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAnalytics = useCallback(async (period: string = '7d') => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiClient.get(`${API_ENDPOINTS.PLATFORMS}/analytics?period=${period}`);
      setAnalyticsData((response as any)?.analytics || []);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAnalytics();
  }, [fetchAnalytics]);

  return {
    analyticsData,
    loading,
    error,
    refetch: fetchAnalytics,
    
    // Analytics Operations
    getDetailedAnalytics: async (platformId: string, period: string) => {
      return apiClient.get(`${API_ENDPOINTS.PLATFORMS}/${platformId}/analytics/detailed?period=${period}`);
    },
    
    exportAnalytics: async (platformIds: string[], period: string, format: 'csv' | 'xlsx') => {
      return apiClient.post(API_ENDPOINTS.PLATFORMS + '/analytics/export', {
        platformIds,
        period,
        format
      });
    },
    
    getEngagementTrends: async (platformId: string, period: string) => {
      return apiClient.get(`${API_ENDPOINTS.PLATFORMS}/${platformId}/trends?period=${period}`);
    }
  };
};

// ============================================================================
// HOOK POUR PLATFORM SPECIFIC OPERATIONS
// ============================================================================

export const usePlatformSpecific = (platformId: string) => {
  const [platformData, setPlatformData] = useState<Platform | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPlatformData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiClient.get(API_ENDPOINTS.PLATFORMS + `/${platformId}`);
      setPlatformData(response as Platform);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, [platformId]);

  useEffect(() => {
    if (platformId) {
      fetchPlatformData();
    }
  }, [platformId, fetchPlatformData]);

  return {
    platform: platformData,
    loading,
    error,
    refetch: fetchPlatformData,
    
    // Platform-specific operations
    updatePlatformSettings: async (settings: any) => {
      return apiClient.put(API_ENDPOINTS.PLATFORMS + `/${platformId}/settings`, settings);
    },
    
    getPlatformContent: async () => {
      return apiClient.get(API_ENDPOINTS.PLATFORMS + `/${platformId}/content`);
    },
    
    syncPlatformContent: async () => {
      return apiClient.post(API_ENDPOINTS.PLATFORMS + `/${platformId}/sync-content`);
    }
  };
};