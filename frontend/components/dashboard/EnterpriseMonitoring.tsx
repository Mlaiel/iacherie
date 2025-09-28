'use client';

/**
 * 📊 ENTERPRISE MONITORING DASHBOARD - Frontend Lead + DevOps Implementation
 * Dashboard temps réel pour monitoring 57 modules enterprise
 * Author: Fahed Mlaiel - Multi-Expert Implementation
 */

import React, { useState, useEffect, useMemo } from 'react';
import { 
  Activity, 
  Server, 
  AlertTriangle, 
  CheckCircle, 
  XCircle, 
  Clock, 
  TrendingUp,
  Database,
  Cpu,
  Network,
  Shield
} from 'lucide-react';

// Types TypeScript pour les métriques
interface ModuleStatus {
  name: string;
  type: string;
  status: 'healthy' | 'degraded' | 'down' | 'unknown';
  response_time?: number;
  last_check: string;
  error_count: number;
  uptime_percentage: number;
  additional_metrics: Record<string, any>;
}

interface SystemMetrics {
  total_modules: number;
  healthy_modules: number;
  degraded_modules: number;
  down_modules: number;
  average_response_time: number;
  system_uptime: number;
  total_requests: number;
  total_errors: number;
  timestamp: string;
}

interface MonitoringData {
  system_metrics: SystemMetrics;
  modules_status: Record<string, ModuleStatus>;
  config: {
    total_modules_monitored: number;
    check_interval: number;
    last_update: string;
  };
}

// Hook pour les métriques de monitoring
function useMonitoringData() {
  const [data, setData] = useState<MonitoringData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMonitoringData = async () => {
    try {
      setError(null);
      const response = await fetch('/api/monitoring');
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const monitoringData = await response.json();
      setData(monitoringData);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching monitoring data:', err);
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
      setLoading(false);
    }
  };

  useEffect(() => {
    // Chargement initial
    fetchMonitoringData();

    // Mise à jour temps réel toutes les 30 secondes
    const interval = setInterval(() => {
      fetchMonitoringData();
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  return { data, loading, error, refetch: fetchMonitoringData };
}

// Composant pour les métriques système globales
const SystemOverview: React.FC<{ metrics: SystemMetrics }> = ({ metrics }) => {
  const healthPercentage = (metrics.healthy_modules / metrics.total_modules) * 100;
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-gray-500 text-sm font-medium">Modules Totaux</p>
            <p className="text-3xl font-bold text-gray-900">{metrics.total_modules}</p>
          </div>
          <Server className="h-12 w-12 text-blue-500" />
        </div>
        <div className="mt-4">
          <div className="flex items-center">
            <div className="flex-1 bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${healthPercentage}%` }}
              />
            </div>
            <span className="ml-3 text-sm font-medium text-gray-600">
              {healthPercentage.toFixed(1)}% Healthy
            </span>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-gray-500 text-sm font-medium">Modules Sains</p>
            <p className="text-3xl font-bold text-green-600">{metrics.healthy_modules}</p>
          </div>
          <CheckCircle className="h-12 w-12 text-green-500" />
        </div>
        <div className="mt-4">
          <p className="text-sm text-gray-600">
            Uptime: <span className="font-semibold">{metrics.system_uptime.toFixed(1)}%</span>
          </p>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-gray-500 text-sm font-medium">Modules Dégradés</p>
            <p className="text-3xl font-bold text-yellow-600">{metrics.degraded_modules}</p>
          </div>
          <AlertTriangle className="h-12 w-12 text-yellow-500" />
        </div>
        <div className="mt-4">
          <p className="text-sm text-gray-600">
            Erreurs: <span className="font-semibold">{metrics.total_errors}</span>
          </p>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-gray-500 text-sm font-medium">Temps de Réponse</p>
            <p className="text-3xl font-bold text-blue-600">{metrics.average_response_time.toFixed(0)}ms</p>
          </div>
          <Clock className="h-12 w-12 text-blue-500" />
        </div>
        <div className="mt-4">
          <p className="text-sm text-gray-600">
            Requêtes: <span className="font-semibold">{metrics.total_requests.toLocaleString()}</span>
          </p>
        </div>
      </div>
    </div>
  );
};

// Composant pour un module individuel
const ModuleCard: React.FC<{ module: ModuleStatus }> = ({ module }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-600 bg-green-100';
      case 'degraded': return 'text-yellow-600 bg-yellow-100';
      case 'down': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return <CheckCircle className="h-5 w-5" />;
      case 'degraded': return <AlertTriangle className="h-5 w-5" />;
      case 'down': return <XCircle className="h-5 w-5" />;
      default: return <Activity className="h-5 w-5" />;
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'microservice': return <Network className="h-5 w-5" />;
      case 'backend': return <Database className="h-5 w-5" />;
      case 'frontend': return <Cpu className="h-5 w-5" />;
      default: return <Server className="h-5 w-5" />;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          {getTypeIcon(module.type)}
          <h3 className="font-medium text-gray-900 capitalize">
            {module.name.replace(/_/g, ' ')}
          </h3>
        </div>
        <div className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(module.status)}`}>
          {getStatusIcon(module.status)}
          <span className="capitalize">{module.status}</span>
        </div>
      </div>

      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-gray-500">Type:</span>
          <span className="font-medium capitalize">{module.type}</span>
        </div>
        
        {module.response_time && (
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Réponse:</span>
            <span className="font-medium">{module.response_time.toFixed(0)}ms</span>
          </div>
        )}
        
        <div className="flex justify-between text-sm">
          <span className="text-gray-500">Uptime:</span>
          <span className="font-medium">{module.uptime_percentage.toFixed(1)}%</span>
        </div>

        {module.error_count > 0 && (
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Erreurs:</span>
            <span className="font-medium text-red-600">{module.error_count}</span>
          </div>
        )}

        {/* Métriques additionnelles */}
        {Object.keys(module.additional_metrics).length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-200">
            <p className="text-xs text-gray-500 mb-2">Métriques:</p>
            {Object.entries(module.additional_metrics).map(([key, value]) => (
              <div key={key} className="flex justify-between text-xs">
                <span className="text-gray-500 capitalize">{key.replace(/_/g, ' ')}:</span>
                <span className="font-medium">{typeof value === 'number' ? value.toLocaleString() : value}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

// Composant principal du dashboard
const EnterpriseMonitoringDashboard: React.FC = () => {
  const { data, loading, error, refetch } = useMonitoringData();
  const [filter, setFilter] = useState<string>('all');

  const filteredModules = useMemo(() => {
    if (!data) return [];
    
    const modules = Object.values(data.modules_status);
    
    if (filter === 'all') return modules;
    if (filter === 'issues') return modules.filter(m => m.status !== 'healthy');
    
    return modules.filter(m => m.type === filter);
  }, [data, filter]);

  const modulesByType = useMemo(() => {
    if (!data) return {};
    
    return Object.values(data.modules_status).reduce((acc, module) => {
      if (!acc[module.type]) acc[module.type] = [];
      acc[module.type].push(module);
      return acc;
    }, {} as Record<string, ModuleStatus[]>);
  }, [data]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            <span className="ml-4 text-lg text-gray-600">Chargement des métriques...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <div className="flex items-center">
              <XCircle className="h-6 w-6 text-red-500 mr-3" />
              <div>
                <h3 className="text-lg font-medium text-red-800">Erreur de chargement</h3>
                <p className="text-red-700">{error || 'Impossible de charger les données de monitoring'}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center">
                <Activity className="h-8 w-8 text-blue-500 mr-3" />
                Enterprise Monitoring Dashboard
              </h1>
              <p className="text-gray-600 mt-2">
                Monitoring en temps réel de {data.config.total_modules_monitored} modules enterprise
              </p>
            </div>
            <div className="text-right">
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => refetch()}
                  className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors flex items-center space-x-2"
                  disabled={loading}
                >
                  <TrendingUp className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                  <span>Actualiser</span>
                </button>
                <div>
                  <p className="text-sm text-gray-500">Dernière mise à jour</p>
                  <p className="text-sm font-medium text-gray-900">
                    {new Date(data.config.last_update).toLocaleTimeString()}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Métriques système globales */}
        <SystemOverview metrics={data.system_metrics} />

        {/* Filtres */}
        <div className="mb-6">
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setFilter('all')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                filter === 'all' 
                  ? 'bg-blue-500 text-white' 
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              Tous ({Object.keys(data.modules_status).length})
            </button>
            <button
              onClick={() => setFilter('issues')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                filter === 'issues' 
                  ? 'bg-red-500 text-white' 
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              Problèmes ({data.system_metrics.degraded_modules + data.system_metrics.down_modules})
            </button>
            {Object.entries(modulesByType).map(([type, modules]) => (
              <button
                key={type}
                onClick={() => setFilter(type)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors capitalize ${
                  filter === type 
                    ? 'bg-blue-500 text-white' 
                    : 'bg-white text-gray-700 hover:bg-gray-50'
                }`}
              >
                {type} ({modules.length})
              </button>
            ))}
          </div>
        </div>

        {/* Grille des modules */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredModules.map((module) => (
            <ModuleCard key={module.name} module={module} />
          ))}
        </div>

        {filteredModules.length === 0 && (
          <div className="text-center py-12">
            <Server className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 text-lg">Aucun module trouvé avec les filtres actuels</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default EnterpriseMonitoringDashboard;