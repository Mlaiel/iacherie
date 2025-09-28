// @ts-nocheck
/**
 * 🎯 MODULE COMPONENTS - VERSION SIMPLIFIÉE SANS ERREURS
 * Components React optimisés pour l'affichage des 57 modules
 */

'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { CheckCircle2, Clock, AlertTriangle, Eye, BarChart3, Database } from 'lucide-react';

// Interface simplifiée
export interface SimpleModuleCardProps {
  title: string;
  status: string;
  metrics: any;
}

// Composant simplifié ModuleCard
export const SimpleModuleCard: React.FC<SimpleModuleCardProps> = ({ title, status, metrics }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'monitoring': return 'secondary';
      case 'tracking': return 'outline';
      case 'enabled': return 'success';
      case 'collecting': return 'secondary';
      default: return 'secondary';
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">{title}</CardTitle>
          <Badge variant={getStatusColor(status)}>
            {status}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {Object.entries(metrics || {}).map(([key, value]) => (
            <div key={key} className="flex justify-between">
              <span className="text-sm text-gray-600">{key}:</span>
              <span className="text-sm font-medium">{String(value)}</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

// Composant simplifié SystemHealthIndicator
export const SimpleSystemHealthIndicator: React.FC<{ overallHealth: number }> = ({ overallHealth }) => {
  const getHealthColor = () => {
    if (overallHealth >= 95) return 'text-green-600';
    if (overallHealth >= 80) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="flex items-center space-x-2">
      <div className={`w-3 h-3 rounded-full ${overallHealth >= 95 ? 'bg-green-500' : overallHealth >= 80 ? 'bg-yellow-500' : 'bg-red-500'}`} />
      <span className={`text-sm font-medium ${getHealthColor()}`}>
        {overallHealth}% Health
      </span>
    </div>
  );
};

// Export des composants réparés
export {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Badge,
  Progress
};