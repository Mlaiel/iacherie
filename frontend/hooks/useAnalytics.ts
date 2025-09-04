/**
 * Analytics Hook - Custom hook for analytics data management
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import { useState, useEffect, useCallback } from 'react';
import { api } from '../utils/api';

interface AnalyticsData {
  revenue: {
    total: number;
    monthly: number;
    growth: number;
  };
  platforms: {
    name: string;
    earnings: number;
    percentage: number;
  }[];
  performance: {
    views: number;
    engagement: number;
    conversion: number;
  };
}

export const useAnalytics = (timeframe: string = '30d') => {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAnalytics = useCallback(async () => {
    try {
      setLoading(true);
      const [revenue, platforms, performance] = await Promise.all([
        api.analytics.getRevenueData(timeframe),
        api.analytics.getPlatformStats(),
        api.analytics.getPerformanceMetrics(),
      ]);

      setData({
        revenue: revenue.data,
        platforms: platforms.data,
        performance: performance.data,
      });
      setError(null);
    } catch (err) {
      setError('Failed to fetch analytics data');
      console.error('Analytics error:', err);
    } finally {
      setLoading(false);
    }
  }, [timeframe]);

  useEffect(() => {
    fetchAnalytics();
  }, [fetchAnalytics]);

  return {
    data,
    loading,
    error,
    refetch: fetchAnalytics,
  };
};

export default useAnalytics;