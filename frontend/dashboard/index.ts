/**
 * Dashboard Components Index - Export all dashboard components
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

// Export all dashboard components
export { default as CreatorDashboard } from './creator_dashboard';
export { default as ProtectionCenter } from './protection_center';
export { default as AnalyticsView } from './analytics_view';
export { default as CollaborationHub } from './collaboration_hub';
export { default as MonetizationPanel } from './monetization_panel';
export { default as SettingsManager } from './settings_manager';

// Export upload components
export { default as UploadWizard } from '../components/upload_wizard';
export { default as ContentLibrary } from '../components/content_library';

// Re-export existing components for compatibility
export { Dashboard } from '../src/components/dashboard/Dashboard';
export { MetricCard } from '../src/components/dashboard/MetricCard';
export { ProtectionStatus } from '../src/components/dashboard/ProtectionStatus';
export { RecentActivity } from '../src/components/dashboard/RecentActivity';
export { RevenueChart } from '../src/components/dashboard/RevenueChart';

/**
 * Dashboard Component Map - For dynamic routing
 */
export const DASHBOARD_COMPONENTS = {
  // Main dashboard
  'dashboard': 'Dashboard',
  'creator-dashboard': 'CreatorDashboard',
  
  // Protection
  'protection': 'ProtectionCenter',
  'protection-center': 'ProtectionCenter',
  
  // Analytics
  'analytics': 'AnalyticsView',
  'analytics-view': 'AnalyticsView',
  
  // Collaboration
  'collaboration': 'CollaborationHub',
  'collaboration-hub': 'CollaborationHub',
  
  // Monetization
  'monetization': 'MonetizationPanel',
  'revenue': 'MonetizationPanel',
  
  // Content Management
  'upload': 'UploadWizard',
  'content': 'ContentLibrary',
  'library': 'ContentLibrary',
  
  // Settings
  'settings': 'SettingsManager',
  'preferences': 'SettingsManager'
} as const;

/**
 * Navigation items for the new dashboard
 */
export const DASHBOARD_NAVIGATION = [
  {
    name: 'Creator Dashboard',
    href: '/creator-dashboard',
    component: 'CreatorDashboard',
    icon: 'HomeIcon',
    description: 'Overview of your content, protection, and earnings'
  },
  {
    name: 'Protection Center',
    href: '/protection',
    component: 'ProtectionCenter',
    icon: 'ShieldCheckIcon',
    description: 'Monitor and manage your content protection'
  },
  {
    name: 'Analytics View',
    href: '/analytics',
    component: 'AnalyticsView',
    icon: 'ChartBarIcon',
    description: 'Comprehensive insights into your content performance'
  },
  {
    name: 'Collaboration Hub',
    href: '/collaboration',
    component: 'CollaborationHub',
    icon: 'UsersIcon',
    description: 'Manage your team and collaborative projects'
  },
  {
    name: 'Monetization Panel',
    href: '/monetization',
    component: 'MonetizationPanel',
    icon: 'CurrencyDollarIcon',
    description: 'Manage your revenue streams and payment settings'
  },
  {
    name: 'Upload Wizard',
    href: '/upload',
    component: 'UploadWizard',
    icon: 'CloudArrowUpIcon',
    description: 'Upload and protect your content in just a few steps'
  },
  {
    name: 'Content Library',
    href: '/content',
    component: 'ContentLibrary',
    icon: 'DocumentTextIcon',
    description: 'Manage your uploaded content and track performance'
  },
  {
    name: 'Settings Manager',
    href: '/settings',
    component: 'SettingsManager',
    icon: 'CogIcon',
    description: 'Manage your account settings and preferences'
  }
] as const;