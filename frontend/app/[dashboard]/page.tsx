'use client';

import { notFound } from 'next/navigation';
import { DashboardNavigation } from '@/components/dashboard/DashboardNavigation';
import { 
  DASHBOARD_COMPONENTS,
  Dashboard,
  CreatorDashboard,
  ProtectionCenter,
  AnalyticsView,
  CollaborationHub,
  MonetizationPanel,
  SettingsManager,
  UploadWizard,
  ContentLibrary
} from '@/../dashboard';

// Map component names to actual components
const componentMap = {
  Dashboard,
  CreatorDashboard,
  ProtectionCenter,
  AnalyticsView,
  CollaborationHub,
  MonetizationPanel,
  SettingsManager,
  UploadWizard,
  ContentLibrary,
} as const;

interface DashboardPageProps {
  params: {
    dashboard: string;
  };
}

export default function DashboardPage({ params }: DashboardPageProps) {
  const { dashboard } = params;
  
  // Get the component name from the routing map
  const componentName = DASHBOARD_COMPONENTS[dashboard as keyof typeof DASHBOARD_COMPONENTS];
  
  if (!componentName) {
    notFound();
  }
  
  // Get the actual component
  const Component = componentMap[componentName as keyof typeof componentMap];
  
  if (!Component) {
    notFound();
  }
  
  return (
    <div className="min-h-screen bg-gray-50">
      <DashboardNavigation />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Component />
      </div>
    </div>
  );
}