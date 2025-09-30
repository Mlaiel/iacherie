/**
 * 🎯 INFRASTRUCTURE SERVICES HOOKS - ENTERPRISE INFRASTRUCTURE MANAGEMENT
 * Hooks spécialisés pour la gestion infrastructure enterprise
 * 
 * @author Fahed Mlaiel - Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + DevOps
 * @date 25 Septembre 2025
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import { apiClient, API_ENDPOINTS, type APIResponse } from '@/lib/api-client';

// ============================================================================
// TYPES POUR INFRASTRUCTURE SERVICES
// ============================================================================

export interface SystemResource {
  id: string;
  name: string;
  type: 'CPU' | 'Memory' | 'Storage' | 'Network';
  usage: number;
  capacity: number;
  threshold: {
    warning: number;
    critical: number;
  };
  trend: 'increasing' | 'decreasing' | 'stable';
}

export interface ServiceInstance {
  id: string;
  name: string;
  service: string;
  status: 'running' | 'stopped' | 'error' | 'restarting';
  health: number;
  cpu: number;
  memory: number;
  uptime: string;
  requests: number;
  errors: number;
  lastRestart: string;
  replicas: {
    desired: number;
    available: number;
    ready: number;
  };
}

export interface InfrastructureMetrics {
  totalNodes: number;
  activeNodes: number;
  totalCPU: number;
  usedCPU: number;
  totalMemory: number;
  usedMemory: number;
  totalStorage: number;
  usedStorage: number;
  networkTraffic: {
    incoming: number;
    outgoing: number;
  };
  alerts: {
    critical: number;
    warning: number;
    info: number;
  };
}

export interface AutoScalingPolicy {
  id: string;
  service: string;
  metric: 'CPU' | 'Memory' | 'RequestRate';
  threshold: number;
  minReplicas: number;
  maxReplicas: number;
  scaleUpCooldown: number;
  scaleDownCooldown: number;
  enabled: boolean;
}

// ============================================================================
// HOOK PRINCIPAL INFRASTRUCTURE SERVICES
// ============================================================================

export const useInfrastructureServices = () => {
  const [data, setData] = useState<APIResponse>({ data: null, loading: true, error: null, status: null });
  const [resources, setResources] = useState<SystemResource[]>([]);
  const [services, setServices] = useState<ServiceInstance[]>([]);
  const [metrics, setMetrics] = useState<InfrastructureMetrics | null>(null);
  const [policies, setPolicies] = useState<AutoScalingPolicy[]>([]);

  const fetchInfrastructureServices = useCallback(async () => {
    try {
      setData(prev => ({ ...prev, loading: true, error: null }));
      
      const [servicesResponse, resourcesResponse, instancesResponse, metricsResponse, policiesResponse] = await Promise.all([
        apiClient.get(API_ENDPOINTS.INFRASTRUCTURE + '/status'),
        apiClient.get(API_ENDPOINTS.INFRASTRUCTURE + '/resources'),
        apiClient.get(API_ENDPOINTS.INFRASTRUCTURE + '/services'),
        apiClient.get(API_ENDPOINTS.INFRASTRUCTURE + '/metrics'),
        apiClient.get(API_ENDPOINTS.INFRASTRUCTURE + '/scaling/policies')
      ]);

      setData({ data: servicesResponse, loading: false, error: null, status: 200 });
      setResources((resourcesResponse as any)?.resources || []);
      setServices((instancesResponse as any)?.services || []);
      setMetrics(metricsResponse as InfrastructureMetrics);
      setPolicies((policiesResponse as any)?.policies || []);
      
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
    fetchInfrastructureServices();
    
    // Real-time monitoring every 15 seconds
    const interval = setInterval(fetchInfrastructureServices, 15000);
    return () => clearInterval(interval);
  }, [fetchInfrastructureServices]);

  return {
    ...data,
    resources,
    services,
    metrics,
    policies,
    refetch: fetchInfrastructureServices,
    
    // Service Management
    restartService: async (serviceId: string) => {
      return apiClient.post(API_ENDPOINTS.INFRASTRUCTURE + `/services/${serviceId}/restart`);
    },
    
    scaleService: async (serviceId: string, replicas: number) => {
      return apiClient.post(API_ENDPOINTS.INFRASTRUCTURE + `/services/${serviceId}/scale`, { replicas });
    },
    
    deployService: async (serviceConfig: any) => {
      return apiClient.post(API_ENDPOINTS.INFRASTRUCTURE + '/services/deploy', serviceConfig);
    },
    
    // Resource Management
    allocateResources: async (resourceConfig: any) => {
      return apiClient.post(API_ENDPOINTS.INFRASTRUCTURE + '/resources/allocate', resourceConfig);
    },
    
    optimizeResources: async () => {
      return apiClient.post(API_ENDPOINTS.INFRASTRUCTURE + '/resources/optimize');
    },
    
    // Auto-scaling Management
    updateScalingPolicy: async (policyId: string, policy: Partial<AutoScalingPolicy>) => {
      return apiClient.put(API_ENDPOINTS.INFRASTRUCTURE + `/scaling/policies/${policyId}`, policy);
    },
    
    createScalingPolicy: async (policy: Omit<AutoScalingPolicy, 'id'>) => {
      return apiClient.post(API_ENDPOINTS.INFRASTRUCTURE + '/scaling/policies', policy);
    },
    
    // System Operations
    getSystemHealth: async () => {
      return apiClient.get(API_ENDPOINTS.INFRASTRUCTURE + '/health');
    },
    
    triggerBackup: async (type: string) => {
      return apiClient.post(API_ENDPOINTS.INFRASTRUCTURE + '/backup', { type });
    },
    
    getAlerts: async () => {
      return apiClient.get(API_ENDPOINTS.INFRASTRUCTURE + '/alerts');
    }
  };
};

// ============================================================================
// HOOK POUR MONITORING DES RESSOURCES
// ============================================================================

export const useResourceMonitoring = () => {
  const [resources, setResources] = useState<SystemResource[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchResources = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiClient.get(API_ENDPOINTS.INFRASTRUCTURE + '/resources/monitoring');
      setResources((response as any)?.resources || []);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchResources();
    
    // Real-time monitoring every 10 seconds
    const interval = setInterval(fetchResources, 10000);
    return () => clearInterval(interval);
  }, [fetchResources]);

  return {
    resources,
    loading,
    error,
    refetch: fetchResources,
    
    // Resource Operations
    setResourceThreshold: async (resourceId: string, thresholds: any) => {
      return apiClient.put(API_ENDPOINTS.INFRASTRUCTURE + `/resources/${resourceId}/thresholds`, thresholds);
    },
    
    getResourceHistory: async (resourceId: string, period: string) => {
      return apiClient.get(`${API_ENDPOINTS.INFRASTRUCTURE}/resources/${resourceId}/history?period=${period}`);
    }
  };
};

// ============================================================================
// HOOK POUR CONTAINER ORCHESTRATION
// ============================================================================

export const useContainerOrchestration = () => {
  const [containers, setContainers] = useState<any[]>([]);
  const [clusters, setClusters] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchOrchestrationData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [containersResponse, clustersResponse] = await Promise.all([
        apiClient.get(API_ENDPOINTS.INFRASTRUCTURE + '/containers'),
        apiClient.get(API_ENDPOINTS.INFRASTRUCTURE + '/clusters')
      ]);
      
      setContainers((containersResponse as any)?.containers || []);
      setClusters((clustersResponse as any)?.clusters || []);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchOrchestrationData();
  }, [fetchOrchestrationData]);

  return {
    containers,
    clusters,
    loading,
    error,
    refetch: fetchOrchestrationData,
    
    // Container Management
    deployContainer: async (containerSpec: any) => {
      return apiClient.post(API_ENDPOINTS.INFRASTRUCTURE + '/containers/deploy', containerSpec);
    },
    
    stopContainer: async (containerId: string) => {
      return apiClient.post(API_ENDPOINTS.INFRASTRUCTURE + `/containers/${containerId}/stop`);
    },
    
    getContainerLogs: async (containerId: string) => {
      return apiClient.get(API_ENDPOINTS.INFRASTRUCTURE + `/containers/${containerId}/logs`);
    },
    
    // Cluster Management
    addNode: async (nodeSpec: any) => {
      return apiClient.post(API_ENDPOINTS.INFRASTRUCTURE + '/clusters/nodes', nodeSpec);
    },
    
    removeNode: async (nodeId: string) => {
      return apiClient.delete(API_ENDPOINTS.INFRASTRUCTURE + `/clusters/nodes/${nodeId}`);
    }
  };
};