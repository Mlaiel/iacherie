/**
 * Dashboard Components Index
 * 
 * Organized dashboard components with maximum 12 files per directory
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

// Analytics Components
export { default as AnalyticsView } from '../dashboard_analytics/AnalyticsView';
export { default as RealTimeAnalytics } from '../dashboard_analytics/RealTimeAnalytics';
export { default as RevenueChart } from '../dashboard_analytics/RevenueChart';

// Content Components
export { default as ContentCalendar } from '../dashboard_content/ContentCalendar';
export { default as ContentPreview } from '../dashboard_content/ContentPreview';
export { default as VisualPortfolio } from '../dashboard_content/VisualPortfolio';

// Management Components
export { default as CollaborationHub } from '../dashboard_management/CollaborationHub';
export { default as MonetizationPanel } from '../dashboard_management/MonetizationPanel';
export { default as ProtectionCenter } from '../dashboard_management/ProtectionCenter';
export { default as SettingsManager } from '../dashboard_management/SettingsManager';

// Core Dashboard Components (remaining in root)
export { default as CreatorDashboard } from './CreatorDashboard';
export { default as Dashboard } from './Dashboard';
export { default as DashboardNavigation } from './DashboardNavigation';
export { default as MetricCard } from './MetricCard';
export { default as ProtectionStatus } from './ProtectionStatus';
export { default as RecentActivity } from './RecentActivity';