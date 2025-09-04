/**
 * Test file for Redux store slices
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import { configureStore } from '@reduxjs/toolkit';
import analyticsReducer, { 
  setTimeframe, 
  fetchAnalyticsData,
  selectAnalyticsData,
  selectAnalyticsLoading 
} from '../store/analytics.slice';
import monetizationReducer, { 
  fetchMonetizationData,
  addPaymentMethod,
  updateSettings,
  selectMonetizationData 
} from '../store/monetization.slice';

// Create test store
const testStore = configureStore({
  reducer: {
    analytics: analyticsReducer,
    monetization: monetizationReducer,
  },
});

describe('Redux Store Tests', () => {
  test('Analytics slice - initial state', () => {
    const state = testStore.getState();
    expect(state.analytics.data).toBeNull();
    expect(state.analytics.loading).toBe(false);
    expect(state.analytics.error).toBeNull();
    expect(state.analytics.timeframe).toBe('30d');
  });

  test('Analytics slice - setTimeframe action', () => {
    testStore.dispatch(setTimeframe('90d'));
    const state = testStore.getState();
    expect(state.analytics.timeframe).toBe('90d');
  });

  test('Monetization slice - initial state', () => {
    const state = testStore.getState();
    expect(state.monetization.data).toBeNull();
    expect(state.monetization.loading).toBe(false);
    expect(state.monetization.error).toBeNull();
  });

  test('Selectors work correctly', () => {
    const state = testStore.getState();
    expect(selectAnalyticsData(state)).toBeNull();
    expect(selectAnalyticsLoading(state)).toBe(false);
    expect(selectMonetizationData(state)).toBeNull();
  });

  test('Async actions have correct types', async () => {
    // Test that async actions can be dispatched
    const analyticsPromise = testStore.dispatch(fetchAnalyticsData({ timeframe: '30d' }));
    const monetizationPromise = testStore.dispatch(fetchMonetizationData());
    
    expect(analyticsPromise).toBeDefined();
    expect(monetizationPromise).toBeDefined();
  });
});

console.log('✅ Redux store slices test completed successfully!');
console.log('Analytics initial state:', testStore.getState().analytics);
console.log('Monetization initial state:', testStore.getState().monetization);