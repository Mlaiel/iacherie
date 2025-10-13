/**
 * 🎯 DATA SERVICES HOOKS - ENTERPRISE DATA MANAGEMENT
 * Hooks spécialisés pour la gestion des données enterprise
 * 
 * @author Fahed Mlaiel - Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + DevOps
 * @date 25 Septembre 2025
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import { apiClient, API_ENDPOINTS, type APIResponse } from '@/lib/api-client';

// ============================================================================
// TYPES POUR DATA SERVICES
// ============================================================================

export interface DataPipeline {
  id: string;
  name: string;
  status: 'running' | 'stopped' | 'error' | 'scheduled';
  type: 'ETL' | 'ELT' | 'Stream' | 'Batch';
  source: string;
  destination: string;
  lastRun: string;
  nextRun?: string;
  recordsProcessed: number;
  errorRate: number;
  performance: {
    throughput: number;
    latency: number;
    success_rate: number;
  };
}

export interface DataWarehouse {
  id: string;
  name: string;
  type: 'PostgreSQL' | 'MongoDB' | 'ElasticSearch' | 'Redis';
  size: string;
  connections: number;
  maxConnections: number;
  queryPerformance: {
    avgQueryTime: number;
    slowQueries: number;
    totalQueries: number;
  };
  storage: {
    used: number;
    total: number;
    growth_rate: number;
  };
}

export interface DataGovernance {
  policies: number;
  compliance_score: number;
  data_quality: number;
  privacy_violations: number;
  audit_logs: number;
  retention_policies: number;
}

// ============================================================================
// HOOK PRINCIPAL DATA SERVICES
// ============================================================================

export const useDataServices = () => {
  const [data, setData] = useState<APIResponse>({ data: null, loading: true, error: null, status: null });
  const [pipelines, setPipelines] = useState<DataPipeline[]>([]);
  const [warehouses, setWarehouses] = useState<DataWarehouse[]>([]);
  const [governance, setGovernance] = useState<DataGovernance | null>(null);

  const fetchDataServices = useCallback(async () => {
    try {
      setData(prev => ({ ...prev, loading: true, error: null }));
      
      const [servicesResponse, pipelinesResponse, warehousesResponse, governanceResponse] = await Promise.all([
        apiClient.get(API_ENDPOINTS.DATA + '/status'),
        apiClient.get(API_ENDPOINTS.DATA + '/pipelines'),
        apiClient.get(API_ENDPOINTS.DATA + '/warehouses'),
        apiClient.get(API_ENDPOINTS.DATA + '/governance')
      ]);

      setData({ data: servicesResponse, loading: false, error: null, status: 200 });
      setPipelines((pipelinesResponse as any)?.pipelines || []);
      setWarehouses((warehousesResponse as any)?.warehouses || []);
      setGovernance(governanceResponse as DataGovernance);
      
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
    fetchDataServices();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchDataServices, 30000);
    return () => clearInterval(interval);
  }, [fetchDataServices]);

  return {
    ...data,
    pipelines,
    warehouses,
    governance,
    refetch: fetchDataServices,
    
    // Pipeline Management
    startPipeline: async (pipelineId: string) => {
      return apiClient.post(API_ENDPOINTS.DATA + `/pipelines/${pipelineId}/start`);
    },
    
    stopPipeline: async (pipelineId: string) => {
      return apiClient.post(API_ENDPOINTS.DATA + `/pipelines/${pipelineId}/stop`);
    },
    
    createPipeline: async (pipelineConfig: Partial<DataPipeline>) => {
      return apiClient.post(API_ENDPOINTS.DATA + '/pipelines', pipelineConfig);
    },
    
    // Data Quality Management
    runDataQualityCheck: async (dataset: string) => {
      return apiClient.post(API_ENDPOINTS.DATA + '/quality/check', { dataset });
    },
    
    // Governance Functions
    updateGovernancePolicy: async (policy: any) => {
      return apiClient.put(API_ENDPOINTS.DATA + '/governance/policies', policy);
    },
    
    getAuditLogs: async (filters?: any) => {
      const endpoint = filters ? `${API_ENDPOINTS.DATA}/audit/logs?${new URLSearchParams(filters)}` : `${API_ENDPOINTS.DATA}/audit/logs`;
      return apiClient.get(endpoint);
    },
    
    // Data Warehouse Operations
    optimizeWarehouse: async (warehouseId: string) => {
      return apiClient.post(API_ENDPOINTS.DATA + `/warehouses/${warehouseId}/optimize`);
    },
    
    getWarehouseMetrics: async (warehouseId: string) => {
      return apiClient.get(API_ENDPOINTS.DATA + `/warehouses/${warehouseId}/metrics`);
    }
  };
};

// ============================================================================
// HOOK POUR ETL PIPELINES SPÉCIFIQUES
// ============================================================================

export const useETLPipelines = () => {
  const [pipelines, setPipelines] = useState<DataPipeline[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchETLPipelines = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiClient.get(API_ENDPOINTS.DATA + '/etl/pipelines');
      setPipelines((response as any)?.pipelines || []);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchETLPipelines();
  }, [fetchETLPipelines]);

  return {
    pipelines,
    loading,
    error,
    refetch: fetchETLPipelines,
    
    // ETL Operations
    runETLJob: async (jobConfig: any) => {
      return apiClient.post(API_ENDPOINTS.DATA + '/etl/run', jobConfig);
    },
    
    scheduleETLJob: async (jobId: string, schedule: string) => {
      return apiClient.post(API_ENDPOINTS.DATA + `/etl/${jobId}/schedule`, { schedule });
    },
    
    getETLLogs: async (jobId: string) => {
      return apiClient.get(API_ENDPOINTS.DATA + `/etl/${jobId}/logs`);
    }
  };
};

// ============================================================================
// HOOK POUR DATA WAREHOUSE MONITORING
// ============================================================================

export const useDataWarehouseMonitoring = () => {
  const [warehouses, setWarehouses] = useState<DataWarehouse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchWarehouseData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiClient.get(API_ENDPOINTS.DATA + '/warehouses/monitoring');
      setWarehouses((response as any)?.warehouses || []);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchWarehouseData();
    
    // Real-time monitoring every 15 seconds
    const interval = setInterval(fetchWarehouseData, 15000);
    return () => clearInterval(interval);
  }, [fetchWarehouseData]);

  return {
    warehouses,
    loading,
    error,
    refetch: fetchWarehouseData,
    
    // Warehouse Operations
    analyzePerformance: async (warehouseId: string) => {
      return apiClient.get(API_ENDPOINTS.DATA + `/warehouses/${warehouseId}/performance`);
    },
    
    optimizeQueries: async (warehouseId: string) => {
      return apiClient.post(API_ENDPOINTS.DATA + `/warehouses/${warehouseId}/optimize-queries`);
    },
    
    getStorageAnalytics: async (warehouseId: string) => {
      return apiClient.get(API_ENDPOINTS.DATA + `/warehouses/${warehouseId}/storage`);
    }
  };
};