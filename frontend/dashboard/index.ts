/**
 * Dashboard Exports - Consolidated dashboard components
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

// Dashboard Core Components
export { Dashboard } from '../components/dashboard_core/Dashboard';
export { default as CreatorDashboard } from '../components/dashboard_core/CreatorDashboard';
export { DashboardNavigation } from '../components/dashboard_core/DashboardNavigation';

// Dashboard Sub-components
export { MetricCard } from '../components/dashboard/MetricCard';
export { ProtectionStatus } from '../components/dashboard/ProtectionStatus';
export { RecentActivity } from '../components/dashboard/RecentActivity';
export { RevenueChart } from '../components/dashboard_analytics/RevenueChart';
export { RealTimeAnalytics } from '../components/dashboard_analytics/RealTimeAnalytics';
export { ContentPreview } from '../components/dashboard_content/ContentPreview';
export { VisualPortfolioManagement as VisualPortfolio } from '../components/dashboard_content/VisualPortfolio';
export { ContentPlanningCalendar as ContentCalendar } from '../components/dashboard_content/ContentCalendar';

// Dashboard Navigation Configuration
export const DASHBOARD_NAVIGATION = [
  {
    id: 'dashboard',
    name: 'Dashboard',
    label: 'Dashboard',
    href: '/dashboard',
    icon: 'HomeIcon',
    description: 'Overview of your content, protection, and earnings'
  },
  {
    id: 'content',
    name: 'Content',
    label: 'Content',
    href: '/dashboard/content',
    icon: 'FolderIcon',
    description: 'Manage your uploaded content and track performance'
  },
  {
    id: 'protection',
    name: 'Protection',
    label: 'Protection',
    href: '/dashboard/protection',
    icon: 'ShieldCheckIcon',
    description: 'Monitor and manage your content protection'
  },
  {
    id: 'analytics',
    name: 'Analytics',
    label: 'Analytics',
    href: '/dashboard/analytics',
    icon: 'ChartBarIcon',
    description: 'Comprehensive insights into your content performance'
  },
  {
    id: 'monetization',
    name: 'Monetization',
    label: 'Monetization',
    href: '/dashboard/monetization',
    icon: 'CurrencyDollarIcon',
    description: 'Manage your revenue streams and payment settings'
  },
];