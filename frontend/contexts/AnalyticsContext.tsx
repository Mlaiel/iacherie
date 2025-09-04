/**
 * Analytics Context - Analytics data management context
 */

import { createContext, useContext, ReactNode, useState, useEffect } from 'react';

interface AnalyticsData {
  revenue: {
    total: number;
    monthly: number;
    growth: number;
  };
  content: {
    uploads: number;
    protected: number;
    violations: number;
  };
  platforms: Array<{
    name: string;
    revenue: number;
    growth: number;
  }>;
}

interface AnalyticsContextType {
  data: AnalyticsData | null;
  isLoading: boolean;
  timeframe: string;
  setTimeframe: (timeframe: string) => void;
  refreshData: () => Promise<void>;
}

const AnalyticsContext = createContext<AnalyticsContextType | undefined>(undefined);

export function AnalyticsProvider({ children }: { children: ReactNode }) {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [timeframe, setTimeframe] = useState('30d');

  const refreshData = async () => {
    setIsLoading(true);
    try {
      // Mock data - in real app would fetch from API
      await new Promise(resolve => setTimeout(resolve, 1000));
      setData({
        revenue: { total: 12500, monthly: 2500, growth: 15.3 },
        content: { uploads: 156, protected: 142, violations: 8 },
        platforms: [
          { name: 'YouTube', revenue: 7500, growth: 12.5 },
          { name: 'Spotify', revenue: 3200, growth: 18.2 },
          { name: 'Instagram', revenue: 1800, growth: 8.7 },
        ],
      });
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    refreshData();
  }, [timeframe]);

  return (
    <AnalyticsContext.Provider value={{
      data,
      isLoading,
      timeframe,
      setTimeframe,
      refreshData,
    }}>
      {children}
    </AnalyticsContext.Provider>
  );
}

export const useAnalytics = () => {
  const context = useContext(AnalyticsContext);
  if (!context) {
    throw new Error('useAnalytics must be used within an AnalyticsProvider');
  }
  return context;
};
