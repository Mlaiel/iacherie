/**
 * Analytics Redux Slice - State management for analytics data
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';

// Types for analytics data
export interface AnalyticsRevenue {
  month: string;
  amount: number;
}

export interface AnalyticsContentViews {
  month: string;
  views: number;
}

export interface PlatformDistribution {
  platform: string;
  percentage: number;
  color: string;
}

export interface TopPerformingContent {
  name: string;
  views: number;
  revenue: number;
  id: string;
}

export interface AnalyticsMetrics {
  totalRevenue: number;
  totalViews: number;
  averageEngagement: number;
  contentCount: number;
  growthRate: number;
}

export interface LiveStats {
  currentViewers: number;
  revenueToday: number;
  newFollowersToday: number;
  engagementRate1h: number;
}

export interface AnalyticsData {
  revenue: AnalyticsRevenue[];
  contentViews: AnalyticsContentViews[];
  platformDistribution: PlatformDistribution[];
  topPerformingContent: TopPerformingContent[];
  metrics: AnalyticsMetrics;
  liveStats: LiveStats;
}

export interface AnalyticsState {
  data: AnalyticsData | null;
  loading: boolean;
  error: string | null;
  timeframe: '7d' | '30d' | '90d' | '1y';
  selectedPlatforms: string[];
  lastUpdated: string | null;
}

const initialState: AnalyticsState = {
  data: null,
  loading: false,
  error: null,
  timeframe: '30d',
  selectedPlatforms: [],
  lastUpdated: null,
};

// Async thunks for API calls
export const fetchAnalyticsData = createAsyncThunk(
  'analytics/fetchData',
  async ({ timeframe, platforms }: { timeframe: string; platforms?: string[] }) => {
    // Simulate API call - replace with actual API
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    return {
      revenue: [
        { month: 'Jan', amount: 12000 },
        { month: 'Feb', amount: 15000 },
        { month: 'Mar', amount: 18000 },
        { month: 'Apr', amount: 22000 },
        { month: 'May', amount: 19000 },
        { month: 'Jun', amount: 24580 }
      ],
      contentViews: [
        { month: 'Jan', views: 125000 },
        { month: 'Feb', views: 145000 },
        { month: 'Mar', views: 162000 },
        { month: 'Apr', views: 198000 },
        { month: 'May', views: 178000 },
        { month: 'Jun', views: 215000 }
      ],
      platformDistribution: [
        { platform: 'YouTube', percentage: 45, color: 'bg-red-500' },
        { platform: 'Spotify', percentage: 25, color: 'bg-green-500' },
        { platform: 'SoundCloud', percentage: 15, color: 'bg-orange-500' },
        { platform: 'Apple Music', percentage: 10, color: 'bg-gray-700' },
        { platform: 'Others', percentage: 5, color: 'bg-blue-500' }
      ],
      topPerformingContent: [
        { id: '1', name: 'Track_Final_Master.mp3', views: 125000, revenue: 3200 },
        { id: '2', name: 'Album_Intro_Video.mp4', views: 98000, revenue: 2800 },
        { id: '3', name: 'Behind_Scenes.mp4', views: 87000, revenue: 2100 },
        { id: '4', name: 'Acoustic_Version.mp3', views: 76000, revenue: 1900 }
      ],
      metrics: {
        totalRevenue: 24580,
        totalViews: 215000,
        averageEngagement: 12.5,
        contentCount: 48,
        growthRate: 18.2,
      },
      liveStats: {
        currentViewers: 2450,
        revenueToday: 125.75,
        newFollowersToday: 45,
        engagementRate1h: 0.067,
      }
    } as AnalyticsData;
  }
);

export const fetchLiveStats = createAsyncThunk(
  'analytics/fetchLiveStats',
  async () => {
    // Simulate real-time API call
    await new Promise(resolve => setTimeout(resolve, 500));
    
    return {
      currentViewers: Math.floor(Math.random() * 5000) + 1000,
      revenueToday: Math.floor(Math.random() * 200) + 50,
      newFollowersToday: Math.floor(Math.random() * 100) + 10,
      engagementRate1h: Math.random() * 0.1 + 0.02,
    } as LiveStats;
  }
);

const analyticsSlice = createSlice({
  name: 'analytics',
  initialState,
  reducers: {
    setTimeframe: (state, action: PayloadAction<'7d' | '30d' | '90d' | '1y'>) => {
      state.timeframe = action.payload;
    },
    setSelectedPlatforms: (state, action: PayloadAction<string[]>) => {
      state.selectedPlatforms = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
    updateLiveStats: (state, action: PayloadAction<Partial<LiveStats>>) => {
      if (state.data) {
        state.data.liveStats = { ...state.data.liveStats, ...action.payload };
      }
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch analytics data
      .addCase(fetchAnalyticsData.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchAnalyticsData.fulfilled, (state, action) => {
        state.loading = false;
        state.data = action.payload;
        state.lastUpdated = new Date().toISOString();
      })
      .addCase(fetchAnalyticsData.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch analytics data';
      })
      // Fetch live stats
      .addCase(fetchLiveStats.pending, (state) => {
        // Don't set loading for live stats to avoid UI flicker
      })
      .addCase(fetchLiveStats.fulfilled, (state, action) => {
        if (state.data) {
          state.data.liveStats = action.payload;
        }
      })
      .addCase(fetchLiveStats.rejected, (state, action) => {
        // Silently handle live stats errors
        console.warn('Failed to fetch live stats:', action.error.message);
      });
  },
});

export const { setTimeframe, setSelectedPlatforms, clearError, updateLiveStats } = analyticsSlice.actions;
export default analyticsSlice.reducer;

// Selectors
export const selectAnalyticsData = (state: { analytics: AnalyticsState }) => state.analytics.data;
export const selectAnalyticsLoading = (state: { analytics: AnalyticsState }) => state.analytics.loading;
export const selectAnalyticsError = (state: { analytics: AnalyticsState }) => state.analytics.error;
export const selectAnalyticsTimeframe = (state: { analytics: AnalyticsState }) => state.analytics.timeframe;
export const selectAnalyticsMetrics = (state: { analytics: AnalyticsState }) => state.analytics.data?.metrics;
export const selectLiveStats = (state: { analytics: AnalyticsState }) => state.analytics.data?.liveStats;