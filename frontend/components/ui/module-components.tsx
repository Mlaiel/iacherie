/**
 * 🎯 COMPOSANTS UI RÉUTILISABLES - ARCHITECTURE MÉTIER
 * Composants optimisés pour l'affichage des 57 modules
 * 
 * @author Fahed Mlaiel - Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + DevOps
 * @date 25 Septembre 2025
 */

'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import {
  CheckCircle2,
  Clock,
  AlertTriangle,
  TrendingUp,
  Brain,
  Cog,
  Activity,
  Zap,
  Settings,
  CheckCircle,
  TrendingDown,
  Minus,
  BarChart3,
  Users,
  DollarSign,
  Shield,
  Server,
  Database,
  Cpu,
  Network,
  Globe,
  XCircle,
  Eye
} from 'lucide-react';
import {
  useAPIGateway, 
  useBusinessServices, 
  useCommunicationServices,
  useContentServices,
  useSecurityServices,
  useSEOServices,
  useServiceMesh,
  useTestingServices,
  useMarketingServices
} from '@/hooks/useModules';

// Loading and Error Components
const LoadingSpinner: React.FC = () => (
  <div className="flex items-center justify-center p-8">
    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
  </div>
);

const ErrorDisplay: React.FC<{ message: string }> = ({ message }) => (
  <div className="flex items-center justify-center p-8">
    <div className="text-red-600 text-center">
      <p className="font-medium">Error loading data</p>
      <p className="text-sm text-gray-500">{message}</p>
    </div>
  </div>
);

// ============================================================================
// INTERFACES ET TYPES
// ============================================================================

export interface ModuleCardProps {
  id?: string;
  name?: string;
  title?: string; // Ajout de title pour compatibilité
  description?: string;
  status: 'active' | 'inactive' | 'error' | 'maintenance' | 'monitoring' | 'tracking' | 'enabled' | 'collecting' | 'running' | 'generating';
  category?: string;
  services?: number;
  uptime?: string;
  lastUpdate?: string;
  apiEndpoint?: string;
  metrics?: {
    successRate?: number;
    avgResponseTime?: number;
    totalRequests?: number;
    errorRate?: number;
    [key: string]: any; // Permet d'ajouter d'autres propriétés
  };
  onManage?: () => void;
  onView?: () => void;
}

export interface CategorySectionProps {
  title: string;
  description: string;
  modules: ModuleCardProps[];
  icon: React.ReactNode;
  color: string;
}

export interface MetricsPanelProps {
  title: string;
  metrics: Array<{
    label: string;
    value: string | number;
    unit?: string;
    trend?: 'up' | 'down' | 'stable';
    color?: string;
  }>;
  realTime?: boolean;
}

// ============================================================================
// COMPOSANTS DE BASE
// ============================================================================

/**
 * Badge de statut avec couleurs métier
 */
export const StatusBadge: React.FC<{ status: ModuleCardProps['status'] }> = ({ status }) => {
  const variants = {
    active: { variant: 'success' as const, label: 'Actif', icon: CheckCircle2 },
    inactive: { variant: 'secondary' as const, label: 'Inactif', icon: Clock },
    error: { variant: 'destructive' as const, label: 'Erreur', icon: XCircle },
    maintenance: { variant: 'warning' as const, label: 'Maintenance', icon: AlertTriangle },
    monitoring: { variant: 'secondary' as const, label: 'Surveillance', icon: Activity },
    tracking: { variant: 'secondary' as const, label: 'Suivi', icon: BarChart3 },
    enabled: { variant: 'success' as const, label: 'Activé', icon: CheckCircle2 },
    running: { variant: 'success' as const, label: 'En cours', icon: Activity },
    generating: { variant: 'secondary' as const, label: 'Génération', icon: Settings },
    collecting: { variant: 'secondary' as const, label: 'Collecte', icon: Database }
  };

  const config = variants[status];
  const Icon = config.icon;

  return (
    <Badge variant={config.variant} className="flex items-center gap-1">
      <Icon className="w-3 h-3" />
      {config.label}
    </Badge>
  );
};

/**
 * Indicateur de performance temps réel
 */
export const PerformanceIndicator: React.FC<{
  value: number;
  label: string;
  unit?: string;
  threshold?: { warning: number; critical: number };
}> = ({ value, label, unit = '', threshold }) => {
  const getColor = () => {
    if (!threshold) return 'text-blue-600';
    if (value >= threshold.critical) return 'text-red-600';
    if (value >= threshold.warning) return 'text-yellow-600';
    return 'text-green-600';
  };

  const getProgress = () => {
    if (!threshold) return Math.min(value, 100);
    return Math.min((value / threshold.critical) * 100, 100);
  };

  return (
    <div className="space-y-2">
      <div className="flex justify-between text-sm">
        <span className="text-gray-600">{label}</span>
        <span className={`font-medium ${getColor()}`}>
          {value}{unit}
        </span>
      </div>
      <Progress value={getProgress()} className="h-2" />
    </div>
  );
};

/**
 * Carte de module avec informations complètes
 */
export const ModuleCard: React.FC<ModuleCardProps> = ({
  id,
  name,
  description,
  status,
  category,
  services,
  uptime,
  lastUpdate,
  metrics,
  onManage,
  onView
}) => {
  const getCategoryIcon = (cat: string) => {
    const icons = {
      'AI': Brain,
      'Analytics': BarChart3,
      'Security': Shield,
      'Database': Database,
      'Infrastructure': Cog,
      'Business': Users,
      'Platform': Globe,
      'Financial': DollarSign,
      'default': Activity
    };
    
    const IconComponent = icons[cat as keyof typeof icons] || icons.default;
    return <IconComponent className="w-5 h-5" />;
  };

  return (
    <Card className="hover:shadow-lg transition-shadow duration-200">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-50 rounded-lg">
              {getCategoryIcon(category || 'default')}
            </div>
            <div>
              <CardTitle className="text-lg font-semibold">{name}</CardTitle>
              <CardDescription className="text-sm">{description}</CardDescription>
            </div>
          </div>
          <StatusBadge status={status} />
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Métriques de base */}
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-blue-500" />
            <span className="text-gray-600">Services:</span>
            <span className="font-medium">{services}</span>
          </div>
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-green-500" />
            <span className="text-gray-600">Uptime:</span>
            <span className="font-medium">{uptime}</span>
          </div>
        </div>

        {/* Métriques avancées */}
        {metrics && (
          <div className="space-y-3 pt-2 border-t">
            <PerformanceIndicator
              value={(metrics.successRate || 0) * 100}
              label="Taux de réussite"
              unit="%"
              threshold={{ warning: 95, critical: 90 }}
            />
            <PerformanceIndicator
              value={metrics.avgResponseTime || 0}
              label="Temps de réponse"
              unit="ms"
              threshold={{ warning: 500, critical: 1000 }}
            />
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-2 pt-2">
          {onView && (
            <Button variant="outline" size="sm" onClick={onView} className="flex-1">
              <BarChart3 className="w-4 h-4 mr-2" />
              Voir détails
            </Button>
          )}
          {onManage && (
            <Button size="sm" onClick={onManage} className="flex-1">
              <Settings className="w-4 h-4 mr-2" />
              Gérer
            </Button>
          )}
        </div>

        {/* Timestamp */}
        <div className="text-xs text-gray-500 pt-2 border-t">
          Dernière MAJ: {lastUpdate ? new Date(lastUpdate).toLocaleString('fr-FR') : 'N/A'}
        </div>
      </CardContent>
    </Card>
  );
};

/**
 * Section de catégorie de modules
 */
export const CategorySection: React.FC<CategorySectionProps> = ({
  title,
  description,
  modules,
  icon,
  color
}) => {
  const activeModules = modules.filter(m => m.status === 'active').length;
  const totalServices = modules.reduce((sum, m) => sum + (m.services || 0), 0);

  return (
    <div className="space-y-6">
      {/* En-tête de section */}
      <div className={`p-6 rounded-lg border-l-4 bg-gradient-to-r from-${color}-50 to-white border-l-${color}-500`}>
        <div className="flex items-center gap-4">
          <div className={`p-3 bg-${color}-100 rounded-lg`}>
            {icon}
          </div>
          <div className="flex-1">
            <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
            <p className="text-gray-600 mt-1">{description}</p>
          </div>
          <div className="flex gap-4 text-sm">
            <div className="text-center">
              <div className={`text-2xl font-bold text-${color}-600`}>{activeModules}</div>
              <div className="text-gray-500">Modules actifs</div>
            </div>
            <div className="text-center">
              <div className={`text-2xl font-bold text-${color}-600`}>{totalServices}</div>
              <div className="text-gray-500">Services totaux</div>
            </div>
          </div>
        </div>
      </div>

      {/* Grille des modules */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {modules.map((module) => (
          <ModuleCard key={module.id} {...module} />
        ))}
      </div>
    </div>
  );
};

/**
 * Panneau de métriques temps réel
 */
export const MetricsPanel: React.FC<MetricsPanelProps> = ({
  title,
  metrics,
  realTime = false
}) => {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5" />
            {title}
          </CardTitle>
          {realTime && (
            <div className="flex items-center gap-2 text-sm text-green-600">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              Temps réel
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {metrics.map((metric, index) => {
            const TrendIcon = metric.trend === 'up' ? TrendingUp : 
                           metric.trend === 'down' ? TrendingUp : 
                           Activity;
            
            return (
              <div key={index} className="text-center p-4 rounded-lg bg-gray-50">
                <div className={`text-2xl font-bold ${metric.color || 'text-gray-900'}`}>
                  {metric.value}{metric.unit || ''}
                </div>
                <div className="text-sm text-gray-600 mt-1">{metric.label}</div>
                {metric.trend && (
                  <TrendIcon className={`w-4 h-4 mx-auto mt-2 ${
                    metric.trend === 'up' ? 'text-green-500' : 
                    metric.trend === 'down' ? 'text-red-500' : 
                    'text-gray-400'
                  }`} />
                )}
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};

/**
 * Indicateur de santé système global
 */
export const SystemHealthIndicator: React.FC<{
  overallHealth: number;
  activeModules: number;
  totalModules: number;
  criticalIssues: number;
}> = ({ overallHealth, activeModules, totalModules, criticalIssues }) => {
  const getHealthColor = () => {
    if (overallHealth >= 95) return 'text-green-600';
    if (overallHealth >= 80) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getHealthBg = () => {
    if (overallHealth >= 95) return 'bg-green-50 border-green-200';
    if (overallHealth >= 80) return 'bg-yellow-50 border-yellow-200';
    return 'bg-red-50 border-red-200';
  };

  return (
    <Card className={`${getHealthBg()}`}>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Santé du Système</h3>
            <p className="text-sm text-gray-600">État global de la plateforme</p>
          </div>
          <div className={`text-4xl font-bold ${getHealthColor()}`}>
            {overallHealth}%
          </div>
        </div>
        
        <div className="mt-4 grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-xl font-semibold text-green-600">{activeModules}</div>
            <div className="text-xs text-gray-600">Modules actifs</div>
          </div>
          <div>
            <div className="text-xl font-semibold text-gray-600">{totalModules}</div>
            <div className="text-xs text-gray-600">Total modules</div>
          </div>
          <div>
            <div className="text-xl font-semibold text-red-600">{criticalIssues}</div>
            <div className="text-xs text-gray-600">Alertes critiques</div>
          </div>
        </div>
        
        <Progress value={overallHealth} className="mt-4 h-3" />
      </CardContent>
    </Card>
  );
};

// ============================================================================
// SECURITY SERVICES DASHBOARD (Module 11/57)
// ============================================================================

export const SecurityServicesDashboard: React.FC = () => {
  const { securityStatus, threats, loading, error } = useSecurityServices();

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorDisplay message={error} />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          Security Operations Center
        </h2>
        <div className="flex items-center space-x-2">
          <SystemHealthIndicator 
            overallHealth={securityStatus?.security_analytics?.security_score || 0}
            activeModules={5}
            totalModules={5} 
            criticalIssues={0}
          />
          <Badge variant="outline" className={`${
            securityStatus?.threat_detection?.threat_level === 'low' ? 'bg-green-50 text-green-700' : 
            securityStatus?.threat_detection?.threat_level === 'medium' ? 'bg-yellow-50 text-yellow-700' : 
            'bg-red-50 text-red-700'
          }`}>
            Threat Level: {securityStatus?.threat_detection?.threat_level?.toUpperCase() || 'UNKNOWN'}
          </Badge>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <ModuleCard
          title="Zero Trust Security"
          status={securityStatus?.zero_trust?.status}
          metrics={{
            'Trust Score': `${securityStatus?.zero_trust?.trust_score}%`,
            'Verified Devices': securityStatus?.zero_trust?.verified_devices,
            'Active Policies': securityStatus?.zero_trust?.active_policies,
            'Threat Level': securityStatus?.zero_trust?.threat_level
          }}
        />

        <ModuleCard
          title="Compliance Status"
          status="active"
          metrics={{
            'GDPR': `${securityStatus?.compliance?.gdpr?.score}%`,
            'CCPA': `${securityStatus?.compliance?.ccpa?.score}%`,
            'ISO27001': `${securityStatus?.compliance?.iso27001?.score}%`,
            'SOC2': `${securityStatus?.compliance?.soc2?.score}%`
          }}
        />

        <ModuleCard
          title="Threat Detection"
          status="active"
          metrics={{
            successRate: 98.5,
            avgResponseTime: 45,
            totalRequests: threats?.real_time_threats?.length || 0,
            'Blocked Attempts': securityStatus?.threat_detection?.blocked_attempts,
            'ML Confidence': `${securityStatus?.threat_detection?.ml_confidence}%`,
            'Response Time': securityStatus?.security_analytics?.avg_response_time
          }}
        />

        <ModuleCard
          title="AI Security"
          status="active"
          metrics={{
            'Model Protection': threats?.ai_security?.model_protection,
            'Prompt Injection Blocked': threats?.ai_security?.prompt_injection_blocked,
            'Content Filtering': `${threats?.ai_security?.content_filtering}%`,
            'Adversarial Detection': threats?.ai_security?.adversarial_detection
          }}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold mb-4">Protection Layers</h3>
          <div className="space-y-3">
            {Object.entries(threats?.protection_layers || {}).map(([key, layer]: [string, any]) => (
              <div key={key} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div>
                  <span className="font-medium capitalize">{key.replace('_', ' ')}</span>
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    Status: {layer.status} | Effectiveness: {layer.effectiveness || 'N/A'}
                  </div>
                </div>
                <Badge variant={layer.status === 'active' ? 'default' : 'secondary'}>
                  {layer.status}
                </Badge>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold mb-4">Threat Landscape</h3>
          <div className="space-y-3">
            {Object.entries(threats?.threat_landscape || {}).map(([level, count]: [string, any]) => (
              <div key={level} className="flex items-center justify-between">
                <span className="capitalize">{level.replace('_', ' ')} Risk</span>
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 rounded text-sm ${
                    level === 'high_risk' ? 'bg-red-100 text-red-800' :
                    level === 'medium_risk' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-green-100 text-green-800'
                  }`}>
                    {count}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// SEO SERVICES DASHBOARD (Module 12/57)
// ============================================================================

export const SEOServicesDashboard: React.FC = () => {
  const { seoStatus, rankings, loading, error } = useSEOServices();

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorDisplay message={error} />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          SEO Optimization Center
        </h2>
        <div className="flex items-center space-x-2">
          <SystemHealthIndicator 
            overallHealth={seoStatus?.content_optimization?.optimization_score || 0}
            activeModules={4}
            totalModules={4}
            criticalIssues={1}
          />
          <Badge variant="outline" className="bg-blue-50 text-blue-700">
            {seoStatus?.keyword_analytics?.total_keywords || 0} Keywords Tracked
          </Badge>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <ModuleCard
          title="SEO Automation"
          status={seoStatus?.status}
          metrics={{
            'Active Campaigns': seoStatus?.automation?.active_campaigns,
            'Keywords Tracked': seoStatus?.automation?.keywords_tracked,
            'Optimization Score': `${seoStatus?.automation?.content_optimization}%`,
            'AI Suggestions': seoStatus?.automation?.ai_suggestions
          }}
        />

        <ModuleCard
          title="Keyword Performance"
          status="tracking"
          metrics={{
            'Top 10 Rankings': rankings?.overview?.top_10,
            'Visibility Score': `${rankings?.overview?.visibility_score}%`,
            'Organic Traffic': new Intl.NumberFormat().format(seoStatus?.keyword_analytics?.organic_traffic || 0),
            'CTR': `${seoStatus?.keyword_analytics?.click_through_rate}%`
          }}
        />

        <ModuleCard
          title="Content Optimization"
          status="active"
          metrics={{
            'Pages Analyzed': seoStatus?.content_optimization?.pages_analyzed,
            'Meta Tags Complete': `${seoStatus?.content_optimization?.meta_tags_complete}%`,
            'Schema Markup': `${seoStatus?.content_optimization?.schema_markup}%`,
            'Core Web Vitals': `${seoStatus?.technical_seo?.page_speed_score}%`
          }}
        />

        <ModuleCard
          title="Technical SEO"
          status="monitoring"
          metrics={{
            'Crawl Errors': seoStatus?.technical_seo?.crawl_errors,
            'Page Speed': `${seoStatus?.technical_seo?.page_speed_score}/100`,
            'Mobile Friendly': `${seoStatus?.technical_seo?.mobile_friendly}%`,
            'HTTPS Coverage': `${seoStatus?.technical_seo?.https_coverage}%`
          }}
        />
      </div>
    </div>
  );
};

// ============================================================================
// SERVICE MESH DASHBOARD (Module 13/57)
// ============================================================================

export const ServiceMeshDashboard: React.FC = () => {
  const { meshStatus, traffic, loading, error } = useServiceMesh();

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorDisplay message={error} />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          Service Mesh Orchestration
        </h2>
        <div className="flex items-center space-x-2">
          <SystemHealthIndicator 
            overallHealth={95}
            activeModules={4}
            totalModules={4}
            criticalIssues={0}
          />
          <Badge variant="outline" className="bg-purple-50 text-purple-700">
            {meshStatus?.mesh_type?.toUpperCase()} {meshStatus?.version}
          </Badge>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <ModuleCard
          title="Service Health"
          status={meshStatus?.status}
          metrics={{
            'Total Services': meshStatus?.services?.total_services,
            'Healthy': meshStatus?.services?.healthy_services,
            'Warning': meshStatus?.services?.warning_services,
            'Coverage': `${meshStatus?.services?.mesh_coverage}%`
          }}
        />

        <ModuleCard
          title="Traffic Management"
          status="active"
          metrics={{
            'Requests/min': new Intl.NumberFormat().format(meshStatus?.traffic_management?.requests_per_minute || 0),
            'Success Rate': `${meshStatus?.traffic_management?.success_rate}%`,
            'P99 Latency': meshStatus?.traffic_management?.p99_latency,
            'Circuit Breakers': meshStatus?.traffic_management?.circuit_breakers
          }}
        />

        <ModuleCard
          title="Security"
          status="enabled"
          metrics={{
            'mTLS': meshStatus?.security?.mtls_enabled ? 'Enabled' : 'Disabled',
            'Auth Services': meshStatus?.security?.authorized_services,
            'Policy Violations': meshStatus?.security?.policy_violations,
            'Encryption': meshStatus?.security?.encryption_level
          }}
        />

        <ModuleCard
          title="Observability"
          status="collecting"
          metrics={{
            'Traces': new Intl.NumberFormat().format(meshStatus?.observability?.traces_collected || 0),
            'Metrics': new Intl.NumberFormat().format(meshStatus?.observability?.metrics_exported || 0),
            'Logs': new Intl.NumberFormat().format(meshStatus?.observability?.logs_processed || 0),
            'Active Alerts': meshStatus?.observability?.alerts_active
          }}
        />
      </div>
    </div>
  );
};

// ============================================================================
// TESTING SERVICES DASHBOARD (Module 14/57)  
// ============================================================================

export const TestingServicesDashboard: React.FC = () => {
  const { testingStatus, reports, loading, error } = useTestingServices();

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorDisplay message={error} />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          Testing & Quality Assurance Center
        </h2>
        <div className="flex items-center space-x-2">
          <SystemHealthIndicator 
            overallHealth={testingStatus?.automated_testing?.test_coverage || 0}
            activeModules={3}
            totalModules={3}
            criticalIssues={2}
          />
          <Badge variant="outline" className="bg-indigo-50 text-indigo-700">
            {testingStatus?.automated_testing?.test_suites || 0} Test Suites
          </Badge>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <ModuleCard
          title="Automated Testing"
          status={testingStatus?.status}
          metrics={{
            'Test Coverage': `${testingStatus?.automated_testing?.test_coverage}%`,
            'Tests Passed': testingStatus?.automated_testing?.tests_passed,
            'Tests Failed': testingStatus?.automated_testing?.tests_failed,
            'Execution Time': testingStatus?.automated_testing?.execution_time
          }}
        />

        <ModuleCard
          title="Quality Metrics"
          status="monitoring"
          metrics={{
            'Code Quality': `${testingStatus?.quality_metrics?.code_quality}/100`,
            'Security Score': `${testingStatus?.quality_metrics?.security_score}/100`,
            'Performance': `${testingStatus?.quality_metrics?.performance_score}/100`,
            'Reliability': `${testingStatus?.quality_metrics?.reliability_score}/100`
          }}
        />

        <ModuleCard
          title="Performance Testing"
          status="active"
          metrics={{
            'Load Tests': testingStatus?.performance_testing?.load_tests,
            'Stress Tests': testingStatus?.performance_testing?.stress_tests,
            'Avg Response': testingStatus?.performance_testing?.avg_response_time,
            'Max Users': new Intl.NumberFormat().format(testingStatus?.performance_testing?.max_concurrent_users || 0)
          }}
        />

        <ModuleCard
          title="CI/CD Pipeline"
          status="running"
          metrics={{
            'Success Rate': `${testingStatus?.ci_cd?.pipeline_success_rate}%`,
            'Build Time': testingStatus?.ci_cd?.build_time,
            'Deploy Frequency': testingStatus?.ci_cd?.deployment_frequency,
            'Failure Rate': `${testingStatus?.ci_cd?.change_failure_rate}%`
          }}
        />
      </div>
    </div>
  );
};

// ============================================================================
// MARKETING SERVICES DASHBOARD (Module 15/57)
// ============================================================================

export const MarketingServicesDashboard: React.FC = () => {
  const { marketingStatus, campaigns, loading, error } = useMarketingServices();

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorDisplay message={error} />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          Marketing Operations Center
        </h2>
        <div className="flex items-center space-x-2">
          <SystemHealthIndicator 
            overallHealth={marketingStatus?.campaigns?.roi || 0}
            activeModules={4}
            totalModules={4}
            criticalIssues={1}
          />
          <Badge variant="outline" className="bg-pink-50 text-pink-700">
            {marketingStatus?.campaigns?.active_campaigns || 0} Active Campaigns
          </Badge>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <ModuleCard
          title="Campaign Performance"
          status={marketingStatus?.status}
          metrics={{
            'Active Campaigns': marketingStatus?.campaigns?.active_campaigns,
            'Total Reach': new Intl.NumberFormat().format(marketingStatus?.campaigns?.total_reach || 0),
            'ROI': `${marketingStatus?.campaigns?.roi}%`,
            'Budget Usage': `${marketingStatus?.campaigns?.budget_utilization}%`
          }}
        />

        <ModuleCard
          title="Lead Generation"
          status="generating"
          metrics={{
            'Leads Today': marketingStatus?.lead_generation?.leads_today,
            'This Week': marketingStatus?.lead_generation?.leads_this_week,
            'Qualified Leads': marketingStatus?.lead_generation?.qualified_leads,
            'Avg Score': marketingStatus?.lead_generation?.lead_score_avg
          }}
        />

        <ModuleCard
          title="Digital Marketing"
          status="active"
          metrics={{
            'Website Visitors': new Intl.NumberFormat().format(marketingStatus?.digital_marketing?.website_visitors || 0),
            'Email Open Rate': `${marketingStatus?.digital_marketing?.email_open_rate}%`,
            'CTR': `${marketingStatus?.digital_marketing?.click_through_rate}%`,
            'Brand Mentions': marketingStatus?.digital_marketing?.brand_mentions
          }}
        />

        <ModuleCard
          title="Attribution"
          status="tracking"
          metrics={{
            'Organic': `${marketingStatus?.attribution?.channel_attribution?.organic}%`,
            'Paid Social': `${marketingStatus?.attribution?.channel_attribution?.paid_social}%`,
            'Email': `${marketingStatus?.attribution?.channel_attribution?.email}%`,
            'Direct': `${marketingStatus?.attribution?.channel_attribution?.direct}%`
          }}
        />
      </div>
    </div>
  );
};