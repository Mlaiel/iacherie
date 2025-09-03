/**
 * Demo page for new components
 * 
 * Demonstrates all the new components in action
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

'use client';

import React, { useState } from 'react';
import MediaUploader from '../components/MediaUploader';
import AIProtection from '../components/AIProtection';
import CollaborationHub from '../components/CollaborationHub';
import Analytics from '../components/Analytics';
import Monetization from '../components/Monetization';

const ComponentDemo: React.FC = () => {
  const [activeComponent, setActiveComponent] = useState<string>('media');

  const components = {
    media: {
      name: 'Media Uploader',
      component: <MediaUploader />
    },
    protection: {
      name: 'AI Protection',
      component: <AIProtection />
    },
    collaboration: {
      name: 'Collaboration Hub',
      component: <CollaborationHub />
    },
    analytics: {
      name: 'Analytics Dashboard',
      component: <Analytics />
    },
    monetization: {
      name: 'Monetization Center',
      component: <Monetization />
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