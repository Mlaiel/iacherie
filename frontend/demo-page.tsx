/**
 * Demo Page - Showcase of New Frontend Components
 * 
 * Demonstrates the three main frontend components:
 * 1. Dashboard Temps Réel
 * 2. Interface Mobile
 * 3. Widget Embarquable
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

'use client';

import React, { useState } from 'react';
import { EmbeddableWidget } from './widget';
import { MobileInterface } from './mobile';
import { LiveMetricsGrid } from './app/realtime/components/LiveMetricsGrid';
import { ActivityStream } from './app/realtime/components/ActivityStream';
import { PerformanceChart } from './app/realtime/components/PerformanceChart';

export default function DemoPage() {
  const [activeDemo, setActiveDemo] = useState<'realtime' | 'mobile' | 'widget'>('realtime');

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-6">
            <h1 className="text-3xl font-bold text-gray-900">
              Nouvelles Composants Frontend - Ainflue
            </h1>
            <p className="mt-2 text-lg text-gray-600">
              Démonstration des trois nouveaux modules frontend implémentés
            </p>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            <button
              onClick={() => setActiveDemo('realtime')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeDemo === 'realtime'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              📊 Dashboard Temps Réel
            </button>
            <button
              onClick={() => setActiveDemo('mobile')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeDemo === 'mobile'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              📱 Interface Mobile
            </button>
            <button
              onClick={() => setActiveDemo('widget')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeDemo === 'widget'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              🔗 Widget Embarquable
            </button>
          </nav>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeDemo === 'realtime' && (
          <div className="space-y-8">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                Dashboard Temps Réel
              </h2>
              <p className="text-gray-600 max-w-2xl mx-auto">
                Interface de surveillance en temps réel avec métriques live, flux d'activité 
                et graphiques interactifs. Mise à jour automatique toutes les 3 secondes.
              </p>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <LiveMetricsGrid />
              <ActivityStream />
            </div>
            
            <PerformanceChart />
          </div>
        )}

        {activeDemo === 'mobile' && (
          <div className="space-y-8">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                Interface Mobile
              </h2>
              <p className="text-gray-600 max-w-2xl mx-auto mb-8">
                Interface mobile native avec navigation tactile, pull-to-refresh, 
                support PWA et adaptation automatique à l'orientation.
              </p>
            </div>
            
            <div className="max-w-sm mx-auto bg-gray-900 rounded-3xl p-2">
              <div className="bg-white rounded-2xl overflow-hidden" style={{ height: '600px' }}>
                <div className="transform scale-75 origin-top" style={{ height: '800px' }}>
                  <MobileInterface />
                </div>
              </div>
            </div>
          </div>
        )}

        {activeDemo === 'widget' && (
          <div className="space-y-8">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                Widgets Embarquables
              </h2>
              <p className="text-gray-600 max-w-2xl mx-auto">
                Widgets personnalisables pour intégration sur sites externes. 
                Trois types disponibles avec builder visuel et génération de code.
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="text-center">
                <h3 className="font-semibold text-gray-900 mb-4">Analytics Widget</h3>
                <EmbeddableWidget
                  type="analytics"
                  config={{
                    apiKey: "demo-key",
                    userId: "demo-user",
                    theme: "light",
                    size: "medium",
                    showTitle: true
                  }}
                />
              </div>
              
              <div className="text-center">
                <h3 className="font-semibold text-gray-900 mb-4">Protection Widget</h3>
                <EmbeddableWidget
                  type="protection"
                  config={{
                    apiKey: "demo-key",
                    userId: "demo-user",
                    theme: "light",
                    size: "medium",
                    showTitle: true
                  }}
                />
              </div>
              
              <div className="text-center">
                <h3 className="font-semibold text-gray-900 mb-4">Content Widget</h3>
                <EmbeddableWidget
                  type="content"
                  config={{
                    apiKey: "demo-key",
                    userId: "demo-user",
                    theme: "light",
                    size: "medium",
                    showTitle: true
                  }}
                />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="bg-white border-t mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-gray-600">
            <p>
              ✅ <strong>Implémentation complète</strong> des trois modules frontend manquants
            </p>
            <p className="mt-2 text-sm">
              Dashboard Temps Réel • Interface Mobile • Widgets Embarquables
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}