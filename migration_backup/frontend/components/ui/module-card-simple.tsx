/**
 * 🎯 COMPOSANT MODULE CARD SIMPLIFIÉ
 * Solution rapide pour corriger les erreurs TypeScript
 * 
 * @author Fahed Mlaiel - Expert Multi-Role Implementation
 */

'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { CheckCircle, XCircle, AlertTriangle, Clock, Activity } from 'lucide-react';

// Types simplifiés
export interface SimpleModuleCardProps {
  title: string;
  status: 'active' | 'inactive' | 'error' | 'maintenance' | 'enabled' | 'monitoring' | 'tracking' | 'collecting' | 'running' | 'generating';
  metrics?: Record<string, any>;
  health?: number;
}

export interface SimpleSystemHealthProps {
  overallHealth: number;
  activeModules: number;
  totalModules: number;
  criticalIssues: number;
}

// Badge variants étendus
const statusVariants = {
  'active': 'default',
  'inactive': 'secondary',
  'error': 'destructive',
  'maintenance': 'outline',
  'enabled': 'default',
  'monitoring': 'default',
  'tracking': 'default',
  'collecting': 'default',
  'running': 'default',
  'generating': 'default'
} as const;

const statusIcons = {
  'active': CheckCircle,
  'inactive': XCircle,
  'error': AlertTriangle,
  'maintenance': Clock,
  'enabled': CheckCircle,
  'monitoring': Activity,
  'tracking': Activity,
  'collecting': Activity,
  'running': Activity,
  'generating': Activity
};

export const SimpleModuleCard: React.FC<SimpleModuleCardProps> = ({ 
  title, 
  status, 
  metrics = {},
  health 
}) => {
  const StatusIcon = statusIcons[status] || Activity;
  
  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center justify-between text-lg">
          {title}
          <Badge variant={statusVariants[status] as any}>
            <StatusIcon className="w-3 h-3 mr-1" />
            {status}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {health !== undefined && (
          <div className="mb-4">
            <div className="flex justify-between text-sm mb-1">
              <span>Health</span>
              <span>{health}%</span>
            </div>
            <Progress value={health} className="h-2" />
          </div>
        )}
        
        {Object.keys(metrics).length > 0 && (
          <div className="space-y-2">
            {Object.entries(metrics).slice(0, 4).map(([key, value]) => (
              <div key={key} className="flex justify-between text-sm">
                <span className="text-gray-600">{key}:</span>
                <span className="font-medium">{String(value)}</span>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export const SimpleSystemHealthIndicator: React.FC<SimpleSystemHealthProps> = ({
  overallHealth,
  activeModules,
  totalModules,
  criticalIssues
}) => {
  const healthColor = overallHealth >= 80 ? 'text-green-600' : 
                     overallHealth >= 60 ? 'text-yellow-600' : 'text-red-600';
  
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-lg">System Health</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span>Overall Health</span>
            <span className={`font-bold ${healthColor}`}>{overallHealth}%</span>
          </div>
          <Progress value={overallHealth} className="h-2" />
          
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-600">Active:</span>
              <span className="ml-1 font-medium">{activeModules}/{totalModules}</span>
            </div>
            <div>
              <span className="text-gray-600">Issues:</span>
              <span className="ml-1 font-medium">{criticalIssues}</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};