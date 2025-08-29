/**
 * Dashboard Hook - Custom hook for dashboard data management
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import { useState, useEffect, useCallback } from 'react';
import { api } from '@/utils/api';

interface DashboardMetrics {
  totalContent: number;
  protectedFiles: number;
  monthlyRevenue: number;
  activeMonitoring: number;
  totalViolations: number;
  resolvedViolations: number;
  revenueGrowth: number;
  contentGrowth: number;
}

interface RecentActivity {
  id: string;
  type: 'upload' | 'violation' | 'payment' | 'protection';
  message: string;
  timestamp: string;
  status?: 'success' | 'warning' | 'error';
}

interface UseDashboardReturn {
  metrics: DashboardMetrics | null;
  recentActivity: RecentActivity[];
  loading: boolean;
  error: string | null;
  refreshMetrics: () => Promise<void>;
  refreshActivity: () => Promise<void>;
  refresh: () => Promise<void>;
}

export const useDashboard = (): UseDashboardReturn => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refreshMetrics = useCallback(async () => {
    try {
      const response = await api.dashboard.getMetrics();
      setMetrics(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch dashboard metrics');
      console.error('Error fetching metrics:', err);
    }
  }, []);

  const refreshActivity = useCallback(async () => {
    try {
      const response = await api.dashboard.getRecentActivity();
      setRecentActivity(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch recent activity');
      console.error('Error fetching activity:', err);
    }
  }, []);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      await Promise.all([refreshMetrics(), refreshActivity()]);
    } finally {
      setLoading(false);
    }
  }, [refreshMetrics, refreshActivity]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return {
    metrics,
    recentActivity,
    loading,
    error,
    refreshMetrics,
    refreshActivity,
    refresh,
  };
};

export default useDashboard;