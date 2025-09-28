/**
 * 🎯 FINANCIAL SERVICES HOOKS - ENTERPRISE FINANCIAL MANAGEMENT
 * Hooks spécialisés pour la gestion financière enterprise
 * 
 * @author Fahed Mlaiel - Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + DevOps
 * @date 25 Septembre 2025
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import { apiClient, API_ENDPOINTS, type APIResponse } from '@/lib/api-client';

// ============================================================================
// TYPES POUR FINANCIAL SERVICES
// ============================================================================

export interface PaymentProcessor {
  id: string;
  name: string;
  provider: 'Stripe' | 'PayPal' | 'Square' | 'Adyen';
  status: 'active' | 'inactive' | 'error';
  region: string;
  currency: string;
  transactionVolume: number;
  successRate: number;
  avgProcessingTime: number;
  fees: {
    percentage: number;
    fixed: number;
  };
}

export interface RevenueStream {
  id: string;
  name: string;
  type: 'subscription' | 'commission' | 'advertising' | 'licensing';
  amount: number;
  currency: string;
  growth: number;
  forecast: number;
  contributors: number;
}

export interface FinancialMetrics {
  totalRevenue: number;
  monthlyRecurring: number;
  transactionVolume: number;
  payoutsPending: number;
  commissionsEarned: number;
  operationalCosts: number;
  netProfit: number;
  paymentSuccessRate: number;
}

export interface CreatorPayout {
  id: string;
  creatorId: string;
  creatorName: string;
  amount: number;
  currency: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  scheduledDate: string;
  method: string;
  earnings: {
    content: number;
    referrals: number;
    subscriptions: number;
    total: number;
  };
}

// ============================================================================
// HOOK PRINCIPAL FINANCIAL SERVICES
// ============================================================================

export const useFinancialServices = () => {
  const [data, setData] = useState<APIResponse>({ data: null, loading: true, error: null, status: null });
  const [processors, setProcessors] = useState<PaymentProcessor[]>([]);
  const [revenueStreams, setRevenueStreams] = useState<RevenueStream[]>([]);
  const [metrics, setMetrics] = useState<FinancialMetrics | null>(null);
  const [payouts, setPayouts] = useState<CreatorPayout[]>([]);

  const fetchFinancialServices = useCallback(async () => {
    try {
      setData(prev => ({ ...prev, loading: true, error: null }));
      
      const [servicesResponse, processorsResponse, revenueResponse, metricsResponse, payoutsResponse] = await Promise.all([
        apiClient.get(API_ENDPOINTS.FINANCIAL + '/status'),
        apiClient.get(API_ENDPOINTS.FINANCIAL + '/processors'),
        apiClient.get(API_ENDPOINTS.FINANCIAL + '/revenue'),
        apiClient.get(API_ENDPOINTS.FINANCIAL + '/metrics'),
        apiClient.get(API_ENDPOINTS.FINANCIAL + '/payouts')
      ]);

      setData({ data: servicesResponse, loading: false, error: null, status: 200 });
      setProcessors((processorsResponse as any)?.processors || []);
      setRevenueStreams((revenueResponse as any)?.streams || []);
      setMetrics(metricsResponse as FinancialMetrics);
      setPayouts((payoutsResponse as any)?.payouts || []);
      
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
    fetchFinancialServices();
    
    // Auto-refresh every 60 seconds pour les données financières
    const interval = setInterval(fetchFinancialServices, 60000);
    return () => clearInterval(interval);
  }, [fetchFinancialServices]);

  return {
    ...data,
    processors,
    revenueStreams,
    metrics,
    payouts,
    refetch: fetchFinancialServices,
    
    // Payment Processing
    processPayment: async (paymentData: any) => {
      return apiClient.post(API_ENDPOINTS.FINANCIAL + '/payments/process', paymentData);
    },
    
    refundPayment: async (paymentId: string, reason: string) => {
      return apiClient.post(API_ENDPOINTS.FINANCIAL + `/payments/${paymentId}/refund`, { reason });
    },
    
    // Payout Management
    schedulePayout: async (creatorId: string, amount: number) => {
      return apiClient.post(API_ENDPOINTS.FINANCIAL + '/payouts/schedule', { creatorId, amount });
    },
    
    processPayout: async (payoutId: string) => {
      return apiClient.post(API_ENDPOINTS.FINANCIAL + `/payouts/${payoutId}/process`);
    },
    
    // Revenue Analytics
    getRevenueAnalytics: async (period: string) => {
      return apiClient.get(`${API_ENDPOINTS.FINANCIAL}/analytics/revenue?period=${period}`);
    },
    
    // Financial Reports
    generateReport: async (type: string, params: any) => {
      return apiClient.post(API_ENDPOINTS.FINANCIAL + `/reports/${type}`, params);
    },
    
    // Tax Management
    getTaxCalculations: async (period: string) => {
      return apiClient.get(`${API_ENDPOINTS.FINANCIAL}/tax/calculations?period=${period}`);
    }
  };
};

// ============================================================================
// HOOK POUR PAYMENT PROCESSING MONITORING
// ============================================================================

export const usePaymentProcessing = () => {
  const [processors, setProcessors] = useState<PaymentProcessor[]>([]);
  const [transactions, setTransactions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPaymentData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [processorsResponse, transactionsResponse] = await Promise.all([
        apiClient.get(API_ENDPOINTS.FINANCIAL + '/processors'),
        apiClient.get(API_ENDPOINTS.FINANCIAL + '/transactions/recent')
      ]);
      
      setProcessors((processorsResponse as any)?.processors || []);
      setTransactions((transactionsResponse as any)?.transactions || []);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPaymentData();
    
    // Real-time updates every 30 seconds
    const interval = setInterval(fetchPaymentData, 30000);
    return () => clearInterval(interval);
  }, [fetchPaymentData]);

  return {
    processors,
    transactions,
    loading,
    error,
    refetch: fetchPaymentData,
    
    // Processor Management
    enableProcessor: async (processorId: string) => {
      return apiClient.post(API_ENDPOINTS.FINANCIAL + `/processors/${processorId}/enable`);
    },
    
    disableProcessor: async (processorId: string) => {
      return apiClient.post(API_ENDPOINTS.FINANCIAL + `/processors/${processorId}/disable`);
    },
    
    updateProcessorConfig: async (processorId: string, config: any) => {
      return apiClient.put(API_ENDPOINTS.FINANCIAL + `/processors/${processorId}/config`, config);
    }
  };
};

// ============================================================================
// HOOK POUR CREATOR PAYOUTS
// ============================================================================

export const useCreatorPayouts = () => {
  const [payouts, setPayouts] = useState<CreatorPayout[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPayouts = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiClient.get(API_ENDPOINTS.FINANCIAL + '/payouts');
      setPayouts((response as any)?.payouts || []);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPayouts();
  }, [fetchPayouts]);

  return {
    payouts,
    loading,
    error,
    refetch: fetchPayouts,
    
    // Payout Operations
    approvePayout: async (payoutId: string) => {
      const result = await apiClient.post(API_ENDPOINTS.FINANCIAL + `/payouts/${payoutId}/approve`);
      await fetchPayouts(); // Refresh data
      return result;
    },
    
    rejectPayout: async (payoutId: string, reason: string) => {
      const result = await apiClient.post(API_ENDPOINTS.FINANCIAL + `/payouts/${payoutId}/reject`, { reason });
      await fetchPayouts(); // Refresh data
      return result;
    },
    
    calculateEarnings: async (creatorId: string, period: string) => {
      return apiClient.get(`${API_ENDPOINTS.FINANCIAL}/creators/${creatorId}/earnings?period=${period}`);
    }
  };
};