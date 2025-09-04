/**
 * Monetization Redux Slice - State management for monetization and revenue
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';

// Types for monetization data
export interface RevenueStream {
  id: string;
  platform: string;
  type: 'subscription' | 'ads' | 'licensing' | 'direct';
  monthlyRevenue: number;
  growth: number;
  status: 'active' | 'pending' | 'inactive';
  lastPayment?: string;
  nextPayment?: string;
}

export interface PaymentMethod {
  id: string;
  type: 'bank' | 'paypal' | 'crypto';
  name: string;
  details: string;
  isDefault: boolean;
  status: 'verified' | 'pending' | 'failed';
  lastUsed?: string;
}

export interface MonetizationSettings {
  autoWithdraw: boolean;
  minimumPayout: number;
  preferredCurrency: string;
  taxSettings: {
    enabled: boolean;
    taxRate: number;
    taxRegion: string;
  };
  notificationSettings: {
    paymentReceived: boolean;
    monthlyReports: boolean;
    lowBalance: boolean;
  };
}

export interface RevenueAnalytics {
  totalRevenue: number;
  monthlyGrowth: number;
  topPlatform: string;
  averageRPM: number; // Revenue per mile
  conversionRate: number;
  pendingPayments: number;
}

export interface PaymentHistory {
  id: string;
  amount: number;
  currency: string;
  platform: string;
  date: string;
  status: 'completed' | 'pending' | 'failed';
  paymentMethod: string;
}

export interface MonetizationData {
  revenueStreams: RevenueStream[];
  paymentMethods: PaymentMethod[];
  settings: MonetizationSettings;
  analytics: RevenueAnalytics;
  paymentHistory: PaymentHistory[];
  totalRevenue: number;
}

export interface MonetizationState {
  data: MonetizationData | null;
  loading: boolean;
  error: string | null;
  savingSettings: boolean;
  processingPayment: boolean;
  lastUpdated: string | null;
}

const initialState: MonetizationState = {
  data: null,
  loading: false,
  error: null,
  savingSettings: false,
  processingPayment: false,
  lastUpdated: null,
};

// Async thunks for API calls
export const fetchMonetizationData = createAsyncThunk(
  'monetization/fetchData',
  async () => {
    // Simulate API call - replace with actual API
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    return {
      revenueStreams: [
        {
          id: '1',
          platform: 'YouTube',
          type: 'ads' as const,
          monthlyRevenue: 8500,
          growth: 15.2,
          status: 'active' as const,
          lastPayment: '2024-01-15',
          nextPayment: '2024-02-15'
        },
        {
          id: '2',
          platform: 'Spotify',
          type: 'subscription' as const,
          monthlyRevenue: 6200,
          growth: 8.7,
          status: 'active' as const,
          lastPayment: '2024-01-10',
          nextPayment: '2024-02-10'
        },
        {
          id: '3',
          platform: 'Direct Licensing',
          type: 'licensing' as const,
          monthlyRevenue: 4500,
          growth: 22.1,
          status: 'active' as const,
          lastPayment: '2024-01-20',
          nextPayment: '2024-02-20'
        },
        {
          id: '4',
          platform: 'Patreon',
          type: 'direct' as const,
          monthlyRevenue: 3200,
          growth: -2.3,
          status: 'active' as const,
          lastPayment: '2024-01-01',
          nextPayment: '2024-02-01'
        }
      ],
      paymentMethods: [
        {
          id: '1',
          type: 'bank' as const,
          name: 'Primary Bank Account',
          details: '****1234',
          isDefault: true,
          status: 'verified' as const,
          lastUsed: '2024-01-15'
        },
        {
          id: '2',
          type: 'paypal' as const,
          name: 'PayPal Account',
          details: 'mlaiel@live.de',
          isDefault: false,
          status: 'verified' as const,
          lastUsed: '2024-01-10'
        }
      ],
      settings: {
        autoWithdraw: true,
        minimumPayout: 100,
        preferredCurrency: 'USD',
        taxSettings: {
          enabled: true,
          taxRate: 25,
          taxRegion: 'EU'
        },
        notificationSettings: {
          paymentReceived: true,
          monthlyReports: true,
          lowBalance: false
        }
      },
      analytics: {
        totalRevenue: 22400,
        monthlyGrowth: 12.8,
        topPlatform: 'YouTube',
        averageRPM: 2.45,
        conversionRate: 3.2,
        pendingPayments: 1250
      },
      paymentHistory: [
        {
          id: '1',
          amount: 8500,
          currency: 'USD',
          platform: 'YouTube',
          date: '2024-01-15',
          status: 'completed' as const,
          paymentMethod: 'Primary Bank Account'
        },
        {
          id: '2',
          amount: 6200,
          currency: 'USD',
          platform: 'Spotify',
          date: '2024-01-10',
          status: 'completed' as const,
          paymentMethod: 'PayPal Account'
        },
        {
          id: '3',
          amount: 4500,
          currency: 'USD',
          platform: 'Direct Licensing',
          date: '2024-01-20',
          status: 'pending' as const,
          paymentMethod: 'Primary Bank Account'
        }
      ],
      totalRevenue: 22400
    } as MonetizationData;
  }
);

export const addPaymentMethod = createAsyncThunk(
  'monetization/addPaymentMethod',
  async (paymentMethod: Omit<PaymentMethod, 'id'>) => {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    return {
      ...paymentMethod,
      id: Math.random().toString(36).substr(2, 9),
    } as PaymentMethod;
  }
);

export const updateSettings = createAsyncThunk(
  'monetization/updateSettings',
  async (settings: Partial<MonetizationSettings>) => {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 800));
    
    return settings;
  }
);

export const processWithdrawal = createAsyncThunk(
  'monetization/processWithdrawal',
  async ({ amount, paymentMethodId }: { amount: number; paymentMethodId: string }) => {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    return {
      id: Math.random().toString(36).substr(2, 9),
      amount,
      currency: 'USD',
      platform: 'Manual Withdrawal',
      date: new Date().toISOString().split('T')[0],
      status: 'pending' as const,
      paymentMethod: paymentMethodId
    } as PaymentHistory;
  }
);

const monetizationSlice = createSlice({
  name: 'monetization',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    updateRevenueStream: (state, action: PayloadAction<{ id: string; updates: Partial<RevenueStream> }>) => {
      if (state.data) {
        const index = state.data.revenueStreams.findIndex(stream => stream.id === action.payload.id);
        if (index !== -1) {
          state.data.revenueStreams[index] = { 
            ...state.data.revenueStreams[index], 
            ...action.payload.updates 
          };
        }
      }
    },
    setDefaultPaymentMethod: (state, action: PayloadAction<string>) => {
      if (state.data) {
        state.data.paymentMethods.forEach(method => {
          method.isDefault = method.id === action.payload;
        });
      }
    },
    removePaymentMethod: (state, action: PayloadAction<string>) => {
      if (state.data) {
        state.data.paymentMethods = state.data.paymentMethods.filter(
          method => method.id !== action.payload
        );
      }
    },
    updateAnalytics: (state, action: PayloadAction<Partial<RevenueAnalytics>>) => {
      if (state.data) {
        state.data.analytics = { ...state.data.analytics, ...action.payload };
      }
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch monetization data
      .addCase(fetchMonetizationData.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchMonetizationData.fulfilled, (state, action) => {
        state.loading = false;
        state.data = action.payload;
        state.lastUpdated = new Date().toISOString();
      })
      .addCase(fetchMonetizationData.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch monetization data';
      })
      // Add payment method
      .addCase(addPaymentMethod.pending, (state) => {
        state.processingPayment = true;
      })
      .addCase(addPaymentMethod.fulfilled, (state, action) => {
        state.processingPayment = false;
        if (state.data) {
          state.data.paymentMethods.push(action.payload);
        }
      })
      .addCase(addPaymentMethod.rejected, (state, action) => {
        state.processingPayment = false;
        state.error = action.error.message || 'Failed to add payment method';
      })
      // Update settings
      .addCase(updateSettings.pending, (state) => {
        state.savingSettings = true;
      })
      .addCase(updateSettings.fulfilled, (state, action) => {
        state.savingSettings = false;
        if (state.data) {
          state.data.settings = { ...state.data.settings, ...action.payload };
        }
      })
      .addCase(updateSettings.rejected, (state, action) => {
        state.savingSettings = false;
        state.error = action.error.message || 'Failed to update settings';
      })
      // Process withdrawal
      .addCase(processWithdrawal.pending, (state) => {
        state.processingPayment = true;
      })
      .addCase(processWithdrawal.fulfilled, (state, action) => {
        state.processingPayment = false;
        if (state.data) {
          state.data.paymentHistory.unshift(action.payload);
          // Update total revenue (subtract withdrawal)
          state.data.totalRevenue -= action.payload.amount;
        }
      })
      .addCase(processWithdrawal.rejected, (state, action) => {
        state.processingPayment = false;
        state.error = action.error.message || 'Failed to process withdrawal';
      });
  },
});

export const { 
  clearError, 
  updateRevenueStream, 
  setDefaultPaymentMethod, 
  removePaymentMethod, 
  updateAnalytics 
} = monetizationSlice.actions;

export default monetizationSlice.reducer;

// Selectors
export const selectMonetizationData = (state: { monetization: MonetizationState }) => state.monetization.data;
export const selectMonetizationLoading = (state: { monetization: MonetizationState }) => state.monetization.loading;
export const selectMonetizationError = (state: { monetization: MonetizationState }) => state.monetization.error;
export const selectRevenueStreams = (state: { monetization: MonetizationState }) => state.monetization.data?.revenueStreams;
export const selectPaymentMethods = (state: { monetization: MonetizationState }) => state.monetization.data?.paymentMethods;
export const selectMonetizationSettings = (state: { monetization: MonetizationState }) => state.monetization.data?.settings;
export const selectRevenueAnalytics = (state: { monetization: MonetizationState }) => state.monetization.data?.analytics;
export const selectPaymentHistory = (state: { monetization: MonetizationState }) => state.monetization.data?.paymentHistory;
export const selectTotalRevenue = (state: { monetization: MonetizationState }) => state.monetization.data?.totalRevenue;