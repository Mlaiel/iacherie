'use client';

/**
 * 🔍 ENTERPRISE MONITORING PAGE - Frontend Integration Complete
 * Page dashboard principale pour monitoring enterprise iaCherie
 * Author: Fahed Mlaiel - Frontend Lead + DevOps Implementation
 */

import React, { Suspense } from 'react';
import { Activity, Server, AlertTriangle, Database, Shield, Cpu } from 'lucide-react';
import EnterpriseMonitoringDashboard from '@/components/dashboard/EnterpriseMonitoring';

// Composant de chargement pour Suspense
const MonitoringLoader: React.FC = () => (
  <div className="min-h-screen bg-gray-50 p-6">
    <div className="max-w-7xl mx-auto">
      <div className="animate-pulse">
        {/* Header skeleton */}
        <div className="mb-8">
          <div className="flex items-center mb-4">
            <div className="h-8 w-8 bg-gray-200 rounded mr-3"></div>
            <div className="h-8 w-64 bg-gray-200 rounded"></div>
          </div>
          <div className="h-4 w-96 bg-gray-200 rounded"></div>
        </div>
        
        {/* Metrics cards skeleton */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <div className="h-4 w-24 bg-gray-200 rounded mb-2"></div>
                  <div className="h-8 w-16 bg-gray-200 rounded"></div>
                </div>
                <div className="h-12 w-12 bg-gray-200 rounded"></div>
              </div>
              <div className="h-2 w-full bg-gray-200 rounded"></div>
            </div>
          ))}
        </div>
        
        {/* Modules grid skeleton */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
            <div key={i} className="bg-white rounded-lg shadow-md p-4">
              <div className="flex items-center justify-between mb-3">
                <div className="h-5 w-32 bg-gray-200 rounded"></div>
                <div className="h-6 w-16 bg-gray-200 rounded-full"></div>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <div className="h-3 w-12 bg-gray-200 rounded"></div>
                  <div className="h-3 w-20 bg-gray-200 rounded"></div>
                </div>
                <div className="flex justify-between">
                  <div className="h-3 w-16 bg-gray-200 rounded"></div>
                  <div className="h-3 w-12 bg-gray-200 rounded"></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  </div>
);

// Composant d'erreur pour le monitoring
const MonitoringError: React.FC<{ error?: string }> = ({ error }) => (
  <div className="min-h-screen bg-gray-50 p-6">
    <div className="max-w-7xl mx-auto">
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center mb-4">
          <AlertTriangle className="h-8 w-8 text-red-500 mr-3" />
          <div>
            <h1 className="text-2xl font-bold text-red-800">Erreur de Monitoring</h1>
            <p className="text-red-600 mt-1">
              Impossible de charger le dashboard de monitoring enterprise
            </p>
          </div>
        </div>
        
        {error && (
          <div className="bg-red-100 border border-red-300 rounded p-4 mb-4">
            <p className="text-sm text-red-700 font-mono">{error}</p>
          </div>
        )}
        
        <div className="space-y-4">
          <h3 className="font-medium text-red-800">Actions suggérées:</h3>
          <ul className="list-disc list-inside text-red-700 space-y-2">
            <li>Vérifier que le backend de monitoring est démarré</li>
            <li>Contrôler la connectivité réseau</li>
            <li>Examiner les logs du système</li>
            <li>Redémarrer les services de monitoring</li>
          </ul>
          
          <div className="flex space-x-4 mt-6">
            <button 
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
            >
              Actualiser la page
            </button>
            <button 
              onClick={() => window.history.back()}
              className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
            >
              Retour
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
);

// Composant de statistiques rapides
const QuickStats: React.FC = () => (
  <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 rounded-xl mb-8">
    <div className="flex items-center justify-between">
      <div>
        <h2 className="text-2xl font-bold flex items-center">
          <Activity className="h-6 w-6 mr-2" />
          iaCherie Enterprise Monitoring
        </h2>
        <p className="text-blue-100 mt-1">
          Surveillance temps réel de l'infrastructure complète
        </p>
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        <div className="text-center">
          <div className="flex items-center justify-center mb-1">
            <Server className="h-5 w-5 mr-1" />
            <span className="text-sm font-medium">Services</span>
          </div>
          <div className="text-2xl font-bold">57</div>
        </div>
        <div className="text-center">
          <div className="flex items-center justify-center mb-1">
            <Database className="h-5 w-5 mr-1" />
            <span className="text-sm font-medium">Modules</span>
          </div>
          <div className="text-2xl font-bold">8/57</div>
        </div>
      </div>
    </div>
  </div>
);

// Page principale du monitoring
const MonitoringPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center">
                <Activity className="h-8 w-8 text-blue-600 mr-2" />
                <span className="text-xl font-bold text-gray-900">Enterprise Monitoring</span>
              </div>
              
              <nav className="hidden md:flex space-x-6">
                <a 
                  href="#overview" 
                  className="text-gray-600 hover:text-blue-600 transition-colors"
                >
                  Vue d'ensemble
                </a>
                <a 
                  href="#modules" 
                  className="text-gray-600 hover:text-blue-600 transition-colors"
                >
                  Modules
                </a>
                <a 
                  href="#alerts" 
                  className="text-gray-600 hover:text-blue-600 transition-colors"
                >
                  Alertes
                </a>
                <a 
                  href="#reports" 
                  className="text-gray-600 hover:text-blue-600 transition-colors"
                >
                  Rapports
                </a>
              </nav>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm text-gray-600">Temps réel</span>
              </div>
              
              <button className="p-2 text-gray-400 hover:text-gray-600 transition-colors">
                <Shield className="h-5 w-5" />
              </button>
              <button className="p-2 text-gray-400 hover:text-gray-600 transition-colors">
                <Cpu className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </div>
      
      {/* Contenu principal */}
      <div className="max-w-7xl mx-auto p-6">
        <QuickStats />
        
        {/* Dashboard de monitoring avec Suspense */}
        <Suspense fallback={<MonitoringLoader />}>
          <div id="overview">
            <EnterpriseMonitoringDashboard />
          </div>
        </Suspense>
        
        {/* Section informations supplémentaires */}
        <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Activity className="h-5 w-5 text-blue-500 mr-2" />
              Modules Implémentés
            </h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <span className="font-medium text-green-800">AI Services</span>
                <span className="text-green-600 font-semibold">100%</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <span className="font-medium text-green-800">Analytics Services</span>
                <span className="text-green-600 font-semibold">100%</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <span className="font-medium text-green-800">Audio Processing</span>
                <span className="text-green-600 font-semibold">100%</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <span className="font-medium text-green-800">Security Services</span>
                <span className="text-green-600 font-semibold">100%</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                <span className="font-medium text-blue-800">Enterprise Monitoring</span>
                <span className="text-blue-600 font-semibold">Actif</span>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Server className="h-5 w-5 text-purple-500 mr-2" />
              Architecture Enterprise
            </h3>
            <div className="space-y-3 text-sm text-gray-600">
              <div className="flex justify-between">
                <span>Backend Python:</span>
                <span className="font-semibold">6,202 fichiers</span>
              </div>
              <div className="flex justify-between">
                <span>Frontend React/Next.js:</span>
                <span className="font-semibold">308 fichiers</span>
              </div>
              <div className="flex justify-between">
                <span>Microservices:</span>
                <span className="font-semibold">430+ services</span>
              </div>
              <div className="flex justify-between">
                <span>IA/ML Components:</span>
                <span className="font-semibold">1,114 composants</span>
              </div>
              <div className="flex justify-between">
                <span>Kubernetes Manifests:</span>
                <span className="font-semibold">349 manifests</span>
              </div>
              <div className="flex justify-between">
                <span>Docker Containers:</span>
                <span className="font-semibold">37 containers</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Footer */}
      <footer className="bg-white border-t mt-12">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between text-sm text-gray-500">
            <div>
              © 2025 iaCherie Enterprise Monitoring - Fahed Mlaiel Implementation
            </div>
            <div className="flex space-x-4">
              <span>Version 1.0</span>
              <span>•</span>
              <span>Multi-Expert Architecture</span>
              <span>•</span>
              <span>Production Ready</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default MonitoringPage;