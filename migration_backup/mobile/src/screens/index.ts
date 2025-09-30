/**
 * Mobile Screens Index - Export all mobile screens
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

export { default as HomeScreen } from './HomeScreen';
export { default as DashboardScreen } from './DashboardScreen';
export { default as UploadScreen } from './UploadScreen';
export { default as AnalyticsScreen } from './AnalyticsScreen';
export { default as SettingsScreen } from './SettingsScreen';

// Screen type definitions for navigation
export type ScreenNames = 
  | 'Home'
  | 'Dashboard'
  | 'Upload'
  | 'Analytics' 
  | 'Settings'
  | 'Protection'
  | 'Monetization';

export interface ScreenParams {
  Home: undefined;
  Dashboard: undefined;
  Upload: undefined;
  Analytics: undefined;
  Settings: undefined;
  Protection: undefined;
  Monetization: undefined;
}