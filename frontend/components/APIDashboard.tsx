/**
 * Dashboard API - Visualisation complète des 72 APIs
 * Affiche statistiques, coûts, utilisation, recommendations
 */

'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';

interface DashboardData {
  overview: {
    totalAPIs: number;
    usedAPIs: number;
    unusedAPIs: number;
    utilizationRate: string;
    totalRequests: number;
    totalCost: string;
    estimatedSavings: string;
    avgResponseTime: string;
  };
  apisByCategory: Record<string, number>;
  topAPIs: Array<{
    name: string;
    requests: number;
    successRate: string;
    avgResponseTime: string;
    cost: string;
  }>;
  problematicAPIs: Array<{
    name: string;
    errorRate: string;
    totalErrors: number;
  }>;
  performanceByType: Record<string, {
    count: number;
    avgResponseTime: number;
    totalCost: number;
  }>;
  recommendations: string[];
}

export default function APIDashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState('7d');

  useEffect(() => {
    fetchDashboardData();
  }, [period]);

  const fetchDashboardData = async () => {
    try {
      const response = await fetch(`/api/analytics/dashboard?period=${period}`);
      const result = await response.json();
      if (result.success) {
        setData(result);
      }
    } catch (error) {
      console.error('Error fetching dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="p-8">
        <p className="text-destructive">Erreur lors du chargement des données</p>
      </div>
    );
  }

  return (
    <div className="p-8 space-y-8 bg-background">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-4xl font-bold">📊 Dashboard APIs</h1>
          <p className="text-muted-foreground">Gestion intelligente des 72 APIs</p>
        </div>
        <select
          value={period}
          onChange={(e) => setPeriod(e.target.value)}
          className="px-4 py-2 border rounded-lg"
        >
          <option value="7d">7 derniers jours</option>
          <option value="30d">30 derniers jours</option>
          <option value="90d">90 derniers jours</option>
        </select>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Utilisation</CardTitle>
            <CardDescription>Taux d'utilisation global</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{data.overview.utilizationRate}%</div>
            <Progress value={parseFloat(data.overview.utilizationRate)} className="mt-2" />
            <p className="text-sm text-muted-foreground mt-2">
              {data.overview.usedAPIs} / {data.overview.totalAPIs} APIs actives
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Coût Total</CardTitle>
            <CardDescription>Période sélectionnée</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">${data.overview.totalCost}</div>
            <p className="text-sm text-green-500 mt-2">
              💰 Économies: ${data.overview.estimatedSavings}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Requêtes</CardTitle>
            <CardDescription>Total des appels API</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{data.overview.totalRequests.toLocaleString()}</div>
            <p className="text-sm text-muted-foreground mt-2">
              Temps moyen: {data.overview.avgResponseTime}ms
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>APIs Inutilisées</CardTitle>
            <CardDescription>Opportunités d'économie</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-orange-500">{data.overview.unusedAPIs}</div>
            <p className="text-sm text-muted-foreground mt-2">
              APIs à optimiser ou désactiver
            </p>
          </CardContent>
        </Card>
      </div>

      {/* APIs par Catégorie */}
      <Card>
        <CardHeader>
          <CardTitle>📦 APIs par Catégorie</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(data.apisByCategory).map(([category, count]) => (
              <div key={category} className="text-center p-4 bg-secondary rounded-lg">
                <div className="text-2xl font-bold">{count}</div>
                <div className="text-sm text-muted-foreground capitalize">{category}</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Top APIs */}
      <Card>
        <CardHeader>
          <CardTitle>🏆 Top 10 APIs</CardTitle>
          <CardDescription>Par nombre de requêtes</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {data.topAPIs.map((api, index) => (
              <div key={api.name} className="flex items-center justify-between p-3 bg-secondary rounded-lg">
                <div className="flex items-center gap-3">
                  <Badge variant="outline">#{index + 1}</Badge>
                  <div>
                    <div className="font-semibold">{api.name}</div>
                    <div className="text-sm text-muted-foreground">
                      {api.requests.toLocaleString()} requêtes · {api.successRate}% succès
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-bold">${api.cost}</div>
                  <div className="text-sm text-muted-foreground">{api.avgResponseTime}ms</div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Performance par Type */}
      <Card>
        <CardHeader>
          <CardTitle>⚡ Performance par Type</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {Object.entries(data.performanceByType).map(([type, perf]) => (
              <div key={type} className="p-4 bg-secondary rounded-lg">
                <div className="text-lg font-semibold capitalize mb-2">{type}</div>
                <div className="space-y-1 text-sm">
                  <div>APIs: {perf.count}</div>
                  <div>Temps moyen: {perf.avgResponseTime.toFixed(0)}ms</div>
                  <div>Coût: ${perf.totalCost.toFixed(2)}</div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* APIs à Problèmes */}
      {data.problematicAPIs.length > 0 && (
        <Card className="border-destructive">
          <CardHeader>
            <CardTitle className="text-destructive">⚠️ APIs à Problèmes</CardTitle>
            <CardDescription>Taux d'erreur élevé ({">"} 5%)</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {data.problematicAPIs.map((api) => (
                <div key={api.name} className="flex justify-between items-center p-3 bg-destructive/10 rounded-lg">
                  <span className="font-semibold">{api.name}</span>
                  <div className="text-right">
                    <Badge variant="destructive">{api.errorRate}% erreurs</Badge>
                    <div className="text-sm text-muted-foreground mt-1">
                      {api.totalErrors} erreurs totales
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Recommendations */}
      <Card>
        <CardHeader>
          <CardTitle>💡 Recommandations</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {data.recommendations.map((rec, index) => (
              <div key={index} className="p-3 bg-secondary rounded-lg">
                {rec}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
