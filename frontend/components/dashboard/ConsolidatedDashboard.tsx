/**
 * 🎯 DASHBOARD ENTERPRISE CONSOLIDÉ - 57 MODULES INTEGRATION
 * Dashboard principal respectant l'architecture métier logique
 * 
 * @author Fahed Mlaiel - Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + DevOps
 * @date 25 Septembre 2025
 */

'use client';

import React, { useState, useMemo } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { 
  Search, 
  Filter, 
  Brain,
  BarChart3,
  Shield,
  Database,
  Cog,
  Users,
  Globe,
  DollarSign,
  Zap,
  Settings,
  Activity,
  Layers,
  Network,
  TestTube
} from 'lucide-react';

// Composants UI
import {
  CategorySection,
  MetricsPanel,
  SystemHealthIndicator,
  type ModuleCardProps
} from '@/components/ui/module-components';

// Hooks
import {
  useSystemMonitoring,
  useAPIGateway,
  useBusinessServices,
  useCommunicationServices,
  useContentServices,
  useDatabaseManagement,
  useAICore,
  useSecuritySystems
} from '@/hooks/useModules';

// ============================================================================
// CONFIGURATION DES MODULES SELON L'ARCHITECTURE MÉTIER
// ============================================================================

const MODULE_CATEGORIES = {
  // PHASE 1: MICROSERVICES ARCHITECTURE (15 modules prioritaires)
  MICROSERVICES: {
    title: 'Architecture Microservices',
    description: 'Services distribués et orchestration enterprise',
    icon: <Network className="w-6 h-6" />,
    color: 'blue',
    modules: [
      'ai-services', 'analytics', 'api-gateway', 'business', 'communication',
      'content', 'data', 'financial', 'infrastructure', 'platforms',
      'security', 'seo', 'service-mesh', 'testing', 'marketing'
    ]
  },
  
  // PHASE 2: BACKEND CORE MODULES (35 modules métier)
  CORE_BUSINESS: {
    title: 'Modules Métier Core',
    description: 'Logique métier et intelligence artificielle',
    icon: <Brain className="w-6 h-6" />,
    color: 'purple',
    modules: [
      'core', 'database', 'api-layer', 'ai-core', 'ai-models',
      'prompts', 'ai-protection', 'business-logic', 'monetization',
      'collaboration', 'gamification', 'audio', 'media', 'media-processing',
      'distribution', 'seo-engine', 'edge', 'business-intelligence'
    ]
  },

  ADVANCED_SYSTEMS: {
    title: 'Systèmes Avancés',
    description: 'Technologies avancées et compliance',
    icon: <Shield className="w-6 h-6" />,
    color: 'green',
    modules: [
      'monitoring', 'compliance', 'security-systems', 'blockchain',
      'quantum', 'mobile', 'web', 'integrations', 'marketplace',
      'languages', 'avatars', 'collectors', 'config', 'core-services',
      'orchestration', 'enterprise', 'platform-core'
    ]
  },

  // PHASE 3: MODULES COMPLÉMENTAIRES (7 modules utilitaires)
  UTILITIES: {
    title: 'Modules Utilitaires',
    description: 'Outils et frameworks de support',
    icon: <Cog className="w-6 h-6" />,
    color: 'gray',
    modules: [
      'templates', 'test-framework', 'scripts', 'workflow',
      'validation', 'reports', 'utils'
    ]
  }
} as const;

// ============================================================================
// COMPOSANT PRINCIPAL
// ============================================================================

export default function ConsolidatedEnterpriseDashboard() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('overview');

  // Hooks pour les données en temps réel
  const { modules, metrics, loading, error } = useSystemMonitoring();
  const apiGateway = useAPIGateway();
  const businessServices = useBusinessServices();
  const communicationServices = useCommunicationServices();
  const contentServices = useContentServices();
  const databaseManagement = useDatabaseManagement();
  const aiCore = useAICore();
  const securitySystems = useSecuritySystems();

  // Calculs des métriques globales
  const globalMetrics = useMemo(() => {
    if (!modules || !metrics) return null;

    const activeModules = modules.filter(m => m.status === 'active').length;
    const totalServices = modules.reduce((sum, m) => sum + m.services, 0);
    const overallHealth = Math.round((activeModules / modules.length) * 100);
    const criticalIssues = modules.filter(m => m.status === 'error').length;

    return {
      overallHealth,
      activeModules,
      totalModules: modules.length,
      totalServices,
      criticalIssues,
      avgResponseTime: metrics.avgResponseTime,
      successRate: metrics.successRate * 100,
      totalRequests: metrics.totalRequests
    };
  }, [modules, metrics]);

  // Filtrage des modules
  const filteredModules = useMemo(() => {
    if (!modules) return {};

    const filtered = modules.filter(module => {
      const matchesSearch = module.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           module.id.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesCategory = !selectedCategory || 
        Object.entries(MODULE_CATEGORIES).some(([key, config]) => 
          key === selectedCategory && config.modules.includes(module.id as never)
        );

      return matchesSearch && matchesCategory;
    });

    // Regrouper par catégorie
    const grouped = Object.entries(MODULE_CATEGORIES).reduce((acc, [key, config]) => {
      acc[key] = {
        ...config,
        modules: filtered.filter(module => config.modules.includes(module.id as never))
      };
      return acc;
    }, {} as Record<string, any>);

    return grouped;
  }, [modules, searchTerm, selectedCategory]);

  if (loading) {
    return (
      <div className="p-6 space-y-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-32 bg-gray-200 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
          <h3 className="text-red-800 font-semibold">Erreur de connexion</h3>
          <p className="text-red-600 mt-2">{error}</p>
          <Button onClick={() => window.location.reload()} className="mt-4">
            Recharger
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                🏗️ iacherie Enterprise Dashboard
              </h1>
              <p className="text-gray-600 mt-1">
                Monitoring et gestion des 57 modules enterprise
              </p>
            </div>
            
            {globalMetrics && (
              <div className="flex items-center gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">
                    {globalMetrics.activeModules}
                  </div>
                  <div className="text-sm text-gray-500">Modules actifs</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {globalMetrics.totalServices}
                  </div>
                  <div className="text-sm text-gray-500">Services totaux</div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Contenu principal */}
      <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">
        
        {/* Métriques globales */}
        {globalMetrics && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="md:col-span-1">
              <SystemHealthIndicator
                overallHealth={globalMetrics.overallHealth}
                activeModules={globalMetrics.activeModules}
                totalModules={globalMetrics.totalModules}
                criticalIssues={globalMetrics.criticalIssues}
              />
            </div>
            
            <div className="md:col-span-3">
              <MetricsPanel
                title="Métriques Temps Réel"
                realTime={true}
                metrics={[
                  {
                    label: 'Requêtes totales',
                    value: globalMetrics.totalRequests.toLocaleString(),
                    color: 'text-blue-600',
                    trend: 'up'
                  },
                  {
                    label: 'Taux de réussite',
                    value: globalMetrics.successRate.toFixed(1),
                    unit: '%',
                    color: 'text-green-600',
                    trend: 'stable'
                  },
                  {
                    label: 'Temps de réponse',
                    value: globalMetrics.avgResponseTime,
                    unit: 'ms',
                    color: 'text-yellow-600',
                    trend: 'down'
                  },
                  {
                    label: 'Services actifs',
                    value: globalMetrics.totalServices,
                    color: 'text-purple-600',
                    trend: 'up'
                  }
                ]}
              />
            </div>
          </div>
        )}

        {/* Navigation par onglets */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="overview" className="flex items-center gap-2">
              <Activity className="w-4 h-4" />
              Vue d'ensemble
            </TabsTrigger>
            <TabsTrigger value="microservices" className="flex items-center gap-2">
              <Network className="w-4 h-4" />
              Microservices
            </TabsTrigger>
            <TabsTrigger value="core-business" className="flex items-center gap-2">
              <Brain className="w-4 h-4" />
              Métier Core
            </TabsTrigger>
            <TabsTrigger value="advanced-systems" className="flex items-center gap-2">
              <Shield className="w-4 h-4" />
              Systèmes Avancés
            </TabsTrigger>
            <TabsTrigger value="utilities" className="flex items-center gap-2">
              <Cog className="w-4 h-4" />
              Utilitaires
            </TabsTrigger>
          </TabsList>

          {/* Filtres et recherche */}
          <div className="flex gap-4 items-center justify-between bg-white p-4 rounded-lg border">
            <div className="flex gap-4 flex-1">
              <div className="relative flex-1 max-w-md">
                <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Rechercher un module..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
              
              <Button 
                variant="outline"
                onClick={() => setSearchTerm('')}
                disabled={!searchTerm}
              >
                Effacer
              </Button>
            </div>

            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Filter className="w-4 h-4" />
              {Object.values(filteredModules).reduce((sum, category) => sum + category.modules.length, 0)} modules affichés
            </div>
          </div>

          {/* Contenu des onglets */}
          <TabsContent value="overview" className="space-y-8">
            {Object.entries(filteredModules).map(([key, category]) => (
              category.modules.length > 0 && (
                <CategorySection
                  key={key}
                  title={category.title}
                  description={category.description}
                  modules={category.modules}
                  icon={category.icon}
                  color={category.color}
                />
              )
            ))}
          </TabsContent>

          <TabsContent value="microservices" className="space-y-8">
            {filteredModules.MICROSERVICES?.modules.length > 0 && (
              <CategorySection
                title={filteredModules.MICROSERVICES.title}
                description={filteredModules.MICROSERVICES.description}
                modules={filteredModules.MICROSERVICES.modules}
                icon={filteredModules.MICROSERVICES.icon}
                color={filteredModules.MICROSERVICES.color}
              />
            )}
          </TabsContent>

          <TabsContent value="core-business" className="space-y-8">
            {filteredModules.CORE_BUSINESS?.modules.length > 0 && (
              <CategorySection
                title={filteredModules.CORE_BUSINESS.title}
                description={filteredModules.CORE_BUSINESS.description}
                modules={filteredModules.CORE_BUSINESS.modules}
                icon={filteredModules.CORE_BUSINESS.icon}
                color={filteredModules.CORE_BUSINESS.color}
              />
            )}
          </TabsContent>

          <TabsContent value="advanced-systems" className="space-y-8">
            {filteredModules.ADVANCED_SYSTEMS?.modules.length > 0 && (
              <CategorySection
                title={filteredModules.ADVANCED_SYSTEMS.title}
                description={filteredModules.ADVANCED_SYSTEMS.description}
                modules={filteredModules.ADVANCED_SYSTEMS.modules}
                icon={filteredModules.ADVANCED_SYSTEMS.icon}
                color={filteredModules.ADVANCED_SYSTEMS.color}
              />
            )}
          </TabsContent>

          <TabsContent value="utilities" className="space-y-8">
            {filteredModules.UTILITIES?.modules.length > 0 && (
              <CategorySection
                title={filteredModules.UTILITIES.title}
                description={filteredModules.UTILITIES.description}
                modules={filteredModules.UTILITIES.modules}
                icon={filteredModules.UTILITIES.icon}
                color={filteredModules.UTILITIES.color}
              />
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}