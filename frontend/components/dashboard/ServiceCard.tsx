/**
 * 🎯 SERVICE CARD COMPONENT
 * Composant réutilisable pour afficher les informations d'un service
 * 
 * @author Fahed Mlaiel - Expert Multi-Role Implementation
 */

'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { 
  Activity, 
  AlertTriangle, 
  CheckCircle2, 
  XCircle, 
  Clock,
  TrendingUp,
  TrendingDown,
  Minus
} from 'lucide-react';

export interface ServiceMetrics {
  cpu: number;
  memory: number;
  disk: number;
  network: number;
  requests: number;
  errors: number;
  latency: number;
  uptime: number;
}

export interface ServiceData {
  id: string;
  name: string;
  description: string;
  status: 'running' | 'stopped' | 'error' | 'starting' | 'maintenance';
  health: 'healthy' | 'warning' | 'critical' | 'unknown';
  version: string;
  endpoint: string;
  port?: number;
  metrics: ServiceMetrics;
  lastUpdate: string;
  dependencies: string[];
  tags: string[];
}

interface ServiceCardProps {
  service: ServiceData;
  onStart?: (serviceId: string) => void;
  onStop?: (serviceId: string) => void;
  onRestart?: (serviceId: string) => void;
  onViewLogs?: (serviceId: string) => void;
  onViewMetrics?: (serviceId: string) => void;
  compact?: boolean;
}

export const ServiceCard: React.FC<ServiceCardProps> = ({
  service,
  onStart,
  onStop,
  onRestart,
  onViewLogs,
  onViewMetrics,
  compact = false
}) => {
  // Fonction pour obtenir l'icône de statut
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return <CheckCircle2 className="w-4 h-4 text-green-500" />;
      case 'error':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'starting':
        return <Clock className="w-4 h-4 text-blue-500" />;
      case 'maintenance':
        return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
      default:
        return <Minus className="w-4 h-4 text-gray-500" />;
    }
  };

  // Fonction pour obtenir la couleur de santé
  const getHealthColor = (health: string) => {
    switch (health) {
      case 'healthy':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'warning':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  // Fonction pour obtenir la tendance
  const getTrendIcon = (value: number, threshold: number = 80) => {
    if (value > threshold) {
      return <TrendingUp className="w-3 h-3 text-red-500" />;
    } else if (value < 50) {
      return <TrendingDown className="w-3 h-3 text-green-500" />;
    }
    return <Minus className="w-3 h-3 text-gray-500" />;
  };

  if (compact) {
    return (
      <Card className="h-full">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              {getStatusIcon(service.status)}
              <CardTitle className="text-sm font-medium">{service.name}</CardTitle>
            </div>
            <Badge className={getHealthColor(service.health)}>
              {service.health}
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="flex justify-between text-xs">
            <span>CPU: {service.metrics.cpu}%</span>
            <span>Mem: {service.metrics.memory}%</span>
            <span className={service.metrics.uptime > 99 ? 'text-green-600' : 'text-red-600'}>
              {service.metrics.uptime.toFixed(1)}%
            </span>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="h-full hover:shadow-lg transition-shadow duration-200">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {getStatusIcon(service.status)}
            <div>
              <CardTitle className="text-lg">{service.name}</CardTitle>
              <CardDescription className="text-sm mt-1">
                {service.description}
              </CardDescription>
            </div>
          </div>
          <div className="flex flex-col items-end space-y-2">
            <Badge className={getHealthColor(service.health)}>
              {service.health}
            </Badge>
            <Badge variant="outline" className="text-xs">
              v{service.version}
            </Badge>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Métriques principales */}
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">CPU</span>
              <div className="flex items-center space-x-1">
                <span className="text-sm font-medium">{service.metrics.cpu}%</span>
                {getTrendIcon(service.metrics.cpu)}
              </div>
            </div>
            <Progress value={service.metrics.cpu} className="h-2" />
          </div>

          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Memory</span>
              <div className="flex items-center space-x-1">
                <span className="text-sm font-medium">{service.metrics.memory}%</span>
                {getTrendIcon(service.metrics.memory)}
              </div>
            </div>
            <Progress value={service.metrics.memory} className="h-2" />
          </div>

          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Network</span>
              <div className="flex items-center space-x-1">
                <span className="text-sm font-medium">{service.metrics.network} MB/s</span>
                <Activity className="w-3 h-3 text-blue-500" />
              </div>
            </div>
            <Progress value={(service.metrics.network / 100) * 100} className="h-2" />
          </div>

          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Uptime</span>
              <span className={`text-sm font-medium ${
                service.metrics.uptime > 99 ? 'text-green-600' : 'text-red-600'
              }`}>
                {service.metrics.uptime.toFixed(2)}%
              </span>
            </div>
            <Progress value={service.metrics.uptime} className="h-2" />
          </div>
        </div>

        {/* Statistiques de performance */}
        <div className="border-t pt-4">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-lg font-semibold text-blue-600">
                {service.metrics.requests.toLocaleString()}
              </div>
              <div className="text-xs text-gray-500">Requests/min</div>
            </div>
            <div>
              <div className="text-lg font-semibold text-red-600">
                {service.metrics.errors}
              </div>
              <div className="text-xs text-gray-500">Errors</div>
            </div>
            <div>
              <div className="text-lg font-semibold text-green-600">
                {service.metrics.latency}ms
              </div>
              <div className="text-xs text-gray-500">Latency</div>
            </div>
          </div>
        </div>

        {/* Informations techniques */}
        <div className="border-t pt-4 space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Endpoint:</span>
            <code className="text-xs bg-gray-100 px-2 py-1 rounded">
              {service.endpoint}
              {service.port && `:${service.port}`}
            </code>
          </div>
          
          {service.dependencies.length > 0 && (
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Dependencies:</span>
              <span className="text-xs">{service.dependencies.length} services</span>
            </div>
          )}

          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Last Update:</span>
            <span className="text-xs text-gray-500">
              {new Date(service.lastUpdate).toLocaleString()}
            </span>
          </div>
        </div>

        {/* Tags */}
        {service.tags.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {service.tags.map((tag, index) => (
              <Badge key={index} variant="secondary" className="text-xs">
                {tag}
              </Badge>
            ))}
          </div>
        )}

        {/* Actions */}
        <div className="border-t pt-4 flex flex-wrap gap-2">
          {service.status === 'stopped' && onStart && (
            <Button 
              variant="default" 
              size="sm"
              onClick={() => onStart(service.id)}
              className="flex-1"
            >
              Start
            </Button>
          )}
          
          {service.status === 'running' && onStop && (
            <Button 
              variant="destructive" 
              size="sm"
              onClick={() => onStop(service.id)}
              className="flex-1"
            >
              Stop
            </Button>
          )}

          {onRestart && (
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => onRestart(service.id)}
              className="flex-1"
            >
              Restart
            </Button>
          )}

          {onViewLogs && (
            <Button 
              variant="ghost" 
              size="sm"
              onClick={() => onViewLogs(service.id)}
            >
              Logs
            </Button>
          )}

          {onViewMetrics && (
            <Button 
              variant="ghost" 
              size="sm"
              onClick={() => onViewMetrics(service.id)}
            >
              Metrics
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default ServiceCard;