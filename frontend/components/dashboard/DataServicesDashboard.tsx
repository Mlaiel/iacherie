/**
 * 🎯 DATA SERVICES COMPONENTS - ENTERPRISE DATA MANAGEMENT UI
 * Composants spécialisés pour l'affichage des services de données
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
  Database,
  Activity,
  BarChart3,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Zap,
  TrendingUp,
  Shield,
  Settings,
  Play,
  Pause,
  RotateCcw
} from 'lucide-react';
import { useDataServices, useETLPipelines, useDataWarehouseMonitoring, type DataPipeline, type DataWarehouse, type DataGovernance } from '@/hooks/useDataServices';

// ============================================================================
// COMPOSANT PRINCIPAL DATA SERVICES DASHBOARD
// ============================================================================

export function DataServicesDashboard() {
  const { data, pipelines, warehouses, governance, loading, error, refetch } = useDataServices();

  if (loading) {
    return (
      <div className="animate-pulse space-y-4">
        <div className="h-8 bg-gray-200 rounded mb-4"></div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-32 bg-gray-200 rounded-lg"></div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <h3 className="text-red-800 font-semibold">Erreur Data Services</h3>
        <p className="text-red-600 mt-2">{error}</p>
        <Button onClick={refetch} className="mt-4">Réessayer</Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
          <Database className="h-8 w-8 text-blue-600" />
          Data Services Dashboard
        </h2>
        <div className="flex gap-2">
          <Badge variant="outline" className="bg-blue-50">
            {pipelines.length} Pipelines
          </Badge>
          <Badge variant="outline" className="bg-green-50">
            {warehouses.length} Warehouses
          </Badge>
        </div>
      </div>

      {/* Métriques principales */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <DataMetricCard
          title="Pipelines Actifs"
          value={pipelines.filter(p => p.status === 'running').length}
          total={pipelines.length}
          icon={<Activity className="h-6 w-6" />}
          color="blue"
        />
        <DataMetricCard
          title="Warehouses Sains"
          value={warehouses.filter(w => w.connections < w.maxConnections * 0.8).length}
          total={warehouses.length}
          icon={<Database className="h-6 w-6" />}
          color="green"
        />
        <DataMetricCard
          title="Qualité Données"
          value={governance ? Math.round(governance.data_quality) : 0}
          unit="%"
          icon={<CheckCircle2 className="h-6 w-6" />}
          color="purple"
        />
        <DataMetricCard
          title="Compliance Score"
          value={governance ? Math.round(governance.compliance_score) : 0}
          unit="%"
          icon={<Shield className="h-6 w-6" />}
          color="orange"
        />
      </div>

      {/* Pipelines ETL */}
      <ETLPipelinesSection pipelines={pipelines} />

      {/* Data Warehouses */}
      <DataWarehousesSection warehouses={warehouses} />

      {/* Governance Dashboard */}
      {governance && <DataGovernanceSection governance={governance} />}
    </div>
  );
}

// ============================================================================
// COMPOSANTS MÉTRIQUES
// ============================================================================

interface DataMetricCardProps {
  title: string;
  value: number;
  total?: number;
  unit?: string;
  icon: React.ReactNode;
  color: 'blue' | 'green' | 'purple' | 'orange';
}

function DataMetricCard({ title, value, total, unit = '', icon, color }: DataMetricCardProps) {
  const colorClasses = {
    blue: 'text-blue-600 bg-blue-50',
    green: 'text-green-600 bg-green-50',
    purple: 'text-purple-600 bg-purple-50',
    orange: 'text-orange-600 bg-orange-50'
  };

  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600">{title}</p>
            <p className="text-2xl font-bold text-gray-900">
              {value}{unit}{total ? `/${total}` : ''}
            </p>
          </div>
          <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
            {icon}
          </div>
        </div>
        {total && (
          <div className="mt-4">
            <Progress value={(value / total) * 100} className="h-2" />
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// ============================================================================
// SECTION PIPELINES ETL
// ============================================================================

function ETLPipelinesSection({ pipelines }: { pipelines: DataPipeline[] }) {
  const { startPipeline, stopPipeline } = useDataServices();

  const handlePipelineAction = async (pipelineId: string, action: 'start' | 'stop') => {
    try {
      if (action === 'start') {
        await startPipeline(pipelineId);
      } else {
        await stopPipeline(pipelineId);
      }
    } catch (error) {
      console.error(`Failed to ${action} pipeline:`, error);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Zap className="h-5 w-5" />
          Pipelines ETL
        </CardTitle>
        <CardDescription>
          Gestion et monitoring des pipelines de données
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {pipelines.map((pipeline) => (
            <PipelineCard
              key={pipeline.id}
              pipeline={pipeline}
              onAction={handlePipelineAction}
            />
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

function PipelineCard({ 
  pipeline, 
  onAction 
}: { 
  pipeline: DataPipeline; 
  onAction: (id: string, action: 'start' | 'stop') => void;
}) {
  const getStatusColor = (status: DataPipeline['status']) => {
    switch (status) {
      case 'running': return 'bg-green-100 text-green-800';
      case 'stopped': return 'bg-gray-100 text-gray-800';
      case 'error': return 'bg-red-100 text-red-800';
      case 'scheduled': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="border rounded-lg p-4 space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h4 className="font-semibold">{pipeline.name}</h4>
          <Badge className={getStatusColor(pipeline.status)}>
            {pipeline.status}
          </Badge>
          <Badge variant="outline">{pipeline.type}</Badge>
        </div>
        <div className="flex gap-2">
          {pipeline.status === 'stopped' ? (
            <Button
              size="sm"
              variant="outline"
              onClick={() => onAction(pipeline.id, 'start')}
            >
              <Play className="h-4 w-4" />
            </Button>
          ) : (
            <Button
              size="sm"
              variant="outline"
              onClick={() => onAction(pipeline.id, 'stop')}
            >
              <Pause className="h-4 w-4" />
            </Button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
        <div>
          <span className="text-gray-600">Source:</span>
          <div className="font-medium">{pipeline.source}</div>
        </div>
        <div>
          <span className="text-gray-600">Records:</span>
          <div className="font-medium">{pipeline.recordsProcessed.toLocaleString()}</div>
        </div>
        <div>
          <span className="text-gray-600">Success Rate:</span>
          <div className="font-medium">{(pipeline.performance.success_rate * 100).toFixed(1)}%</div>
        </div>
        <div>
          <span className="text-gray-600">Throughput:</span>
          <div className="font-medium">{pipeline.performance.throughput}/sec</div>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// SECTION DATA WAREHOUSES
// ============================================================================

function DataWarehousesSection({ warehouses }: { warehouses: DataWarehouse[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Database className="h-5 w-5" />
          Data Warehouses
        </CardTitle>
        <CardDescription>
          Monitoring et performance des entrepôts de données
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {warehouses.map((warehouse) => (
            <WarehouseCard key={warehouse.id} warehouse={warehouse} />
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

function WarehouseCard({ warehouse }: { warehouse: DataWarehouse }) {
  const connectionUsage = (warehouse.connections / warehouse.maxConnections) * 100;
  const storageUsage = (warehouse.storage.used / warehouse.storage.total) * 100;

  return (
    <div className="border rounded-lg p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h4 className="font-semibold">{warehouse.name}</h4>
        <Badge variant="outline">{warehouse.type}</Badge>
      </div>

      <div className="space-y-3">
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span>Connexions</span>
            <span>{warehouse.connections}/{warehouse.maxConnections}</span>
          </div>
          <Progress value={connectionUsage} className="h-2" />
        </div>

        <div>
          <div className="flex justify-between text-sm mb-1">
            <span>Storage</span>
            <span>{warehouse.storage.used}GB/{warehouse.storage.total}GB</span>
          </div>
          <Progress value={storageUsage} className="h-2" />
        </div>

        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-600">Avg Query Time:</span>
            <div className="font-medium">{warehouse.queryPerformance.avgQueryTime}ms</div>
          </div>
          <div>
            <span className="text-gray-600">Slow Queries:</span>
            <div className="font-medium">{warehouse.queryPerformance.slowQueries}</div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// SECTION DATA GOVERNANCE
// ============================================================================

function DataGovernanceSection({ governance }: { governance: DataGovernance }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Shield className="h-5 w-5" />
          Data Governance
        </CardTitle>
        <CardDescription>
          Conformité et qualité des données
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600">{governance.compliance_score}%</div>
            <div className="text-sm text-gray-600">Compliance Score</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600">{governance.data_quality}%</div>
            <div className="text-sm text-gray-600">Data Quality</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-600">{governance.policies}</div>
            <div className="text-sm text-gray-600">Active Policies</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-orange-600">{governance.audit_logs.toLocaleString()}</div>
            <div className="text-sm text-gray-600">Audit Logs</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-red-600">{governance.privacy_violations}</div>
            <div className="text-sm text-gray-600">Privacy Violations</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-gray-600">{governance.retention_policies}</div>
            <div className="text-sm text-gray-600">Retention Policies</div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}