/**
 * Demo page for new components
 * 
 * Demonstrates available components in the platform
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

'use client';

import React, { useState, useEffect } from 'react';
import { useAppContext } from '../providers';

const ComponentDemo: React.FC = () => {
  const { state, refreshMetrics } = useAppContext();
  const [activeDemo, setActiveDemo] = useState<string>('metrics');

  useEffect(() => {
    refreshMetrics();
  }, [refreshMetrics]);

  const renderDemo = () => {
    switch (activeDemo) {
      case 'metrics':
        return (
          <div className="bg-white rounded-lg p-6 shadow">
            <h3 className="text-lg font-semibold mb-4">Platform Metrics</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div className="bg-blue-50 p-4 rounded">
                <div className="text-2xl font-bold text-blue-600">{state.metrics.total_content}</div>
                <div className="text-sm text-gray-600">Total Content</div>
              </div>
              <div className="bg-green-50 p-4 rounded">
                <div className="text-2xl font-bold text-green-600">{state.metrics.protected_files}</div>
                <div className="text-sm text-gray-600">Protected Files</div>
              </div>
              <div className="bg-purple-50 p-4 rounded">
                <div className="text-2xl font-bold text-purple-600">${state.metrics.monthly_revenue}</div>
                <div className="text-sm text-gray-600">Monthly Revenue</div>
              </div>
            </div>
          </div>
        );
      case 'content':
        return (
          <div className="bg-white rounded-lg p-6 shadow">
            <h3 className="text-lg font-semibold mb-4">Content Overview</h3>
            {state.content.length === 0 ? (
              <p className="text-gray-500">No content uploaded yet.</p>
            ) : (
              <div className="space-y-3">
                {state.content.slice(0, 5).map((item) => (
                  <div key={item.id} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                    <div>
                      <div className="font-medium">{item.name}</div>
                      <div className="text-sm text-gray-500">{item.type} - {item.status}</div>
                    </div>
                    <div className="text-sm text-gray-600">
                      {(item.size / 1024 / 1024).toFixed(2)} MB
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        );
      case 'system':
        return (
          <div className="bg-white rounded-lg p-6 shadow">
            <h3 className="text-lg font-semibold mb-4">System Status</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span>Application Status</span>
                <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-sm">Operational</span>
              </div>
              <div className="flex items-center justify-between">
                <span>User Session</span>
                <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-sm">
                  {state.isAuthenticated ? 'Authenticated' : 'Guest'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span>Theme</span>
                <span className="px-2 py-1 bg-gray-100 text-gray-800 rounded text-sm capitalize">
                  {state.theme}
                </span>
              </div>
            </div>
          </div>
        );
      default:
        return <div>Select a demo from the sidebar</div>;
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Ainflue Platform Demo</h1>
          <p className="text-gray-600">
            Showcase of enterprise features and components
          </p>
        </div>

        <div className="flex gap-6">
          {/* Sidebar */}
          <div className="w-64 bg-white rounded-lg shadow p-4">
            <nav className="space-y-2">
              {[
                { id: 'metrics', label: 'Platform Metrics' },
                { id: 'content', label: 'Content Management' },
                { id: 'system', label: 'System Status' }
              ].map((item) => (
                <button
                  key={item.id}
                  onClick={() => setActiveDemo(item.id)}
                  className={`w-full text-left px-3 py-2 rounded transition-colors ${
                    activeDemo === item.id
                      ? 'bg-blue-50 text-blue-700 font-medium'
                      : 'text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  {item.label}
                </button>
              ))}
            </nav>
          </div>

          {/* Main Content */}
          <div className="flex-1">
            {renderDemo()}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ComponentDemo;

  const components = {
    media: {
      name: 'Media Uploader',
      component: <MediaUploader />
    },
    protection: {
      name: 'AI Protection',
      component: <CopyrightManager />
    },
    collaboration: {
      name: 'Collaboration Hub',
      component: <CollaborationHub />
    },
    analytics: {
      name: 'Analytics Dashboard',
      component: <AnalyticsView />
    },
    monetization: {
      name: 'Monetization Center',
      component: <MonetizationPanel />
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Ainflue Components Demo
          </h1>
          <p className="text-gray-600">
            Explore the new advanced React components for the Ainflue platform
          </p>
        </div>

        {/* Component Selector */}
        <div className="mb-8">
          <div className="flex flex-wrap gap-4">
            {Object.entries(components).map(([key, component]) => (
              <button
                key={key}
                onClick={() => setActiveComponent(key)}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  activeComponent === key
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                }`}
              >
                {component.name}
              </button>
            ))}
          </div>
        </div>

        {/* Component Display */}
        <div className="bg-white rounded-lg shadow-sm border min-h-[600px]">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">
              {components[activeComponent as keyof typeof components].name}
            </h2>
          </div>
          <div className="p-6">
            {components[activeComponent as keyof typeof components].component}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ComponentDemo;