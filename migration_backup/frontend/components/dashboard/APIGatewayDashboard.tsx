/**
 * 🎯 API GATEWAY ENTERPRISE DASHBOARD
 * Interface complète pour la gestion du gateway API
 * 
 * @author Fahed Mlaiel - Expert Multi-Role Implementation
 */

'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Switch } from '@/components/ui/switch';
import { Progress } from '@/components/ui/progress';
import { 
  Globe, 
  Shield, 
  Activity, 
  Settings, 
  BarChart3, 
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Clock,
  Zap,
  Lock,
  Unlock,
  TrendingUp,
  TrendingDown,
  Users,
  Database,
  Network
} from 'lucide-react';

import { ServiceCard, ServiceData } from './ServiceCard';
import { MetricsPanel } from './MetricsPanel';

interface APIRoute {
  id: string;
  path: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  service: string;
  enabled: boolean;
  rateLimitRpm: number;
  authRequired: boolean;
  currentRpm: number;
  avgResponseTime: number;
  errorRate: number;
  totalRequests: number;
  lastAccess: string;
}

interface LoadBalancer {
  id: string;
  name: string;
  algorithm: 'round-robin' | 'least-connections' | 'weighted' | 'ip-hash';
  instances: LoadBalancerInstance[];
  status: 'active' | 'inactive' | 'error';
  totalRequests: number;
  avgResponseTime: number;
}

interface LoadBalancerInstance {
  id: string;
  url: string;
  weight: number;
  status: 'healthy' | 'unhealthy' | 'maintenance';
  currentConnections: number;
  responseTime: number;
}

interface SecurityConfig {
  corsEnabled: boolean;
  corsOrigins: string[];
  rateLimitGlobal: number;
  authenticationRequired: boolean;
  jwtValidation: boolean;
  apiKeyValidation: boolean;
  ipWhitelist: string[];
  ipBlacklist: string[];
  ddosProtection: boolean;
}

const APIGatewayDashboard: React.FC = () => {
  const [routes, setRoutes] = useState<APIRoute[]>([]);
  const [loadBalancers, setLoadBalancers] = useState<LoadBalancer[]>([]);
  const [securityConfig, setSecurityConfig] = useState<SecurityConfig | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedTab, setSelectedTab] = useState('overview');
  const [searchTerm, setSearchTerm] = useState('');

  // Services du gateway
  const gatewayServices: ServiceData[] = [
    {
      id: 'api-gateway-main',
      name: 'API Gateway Main',
      description: 'Service principal de routage',
      status: 'running',
      health: 'healthy',
      version: '2.1.0',
      endpoint: '/api/gateway',
      port: 8080,
      metrics: {
        cpu: 35,
        memory: 68,
        disk: 45,
        network: 125,
        requests: 2340,
        errors: 3,
        latency: 45,
        uptime: 99.9
      },
      lastUpdate: '2025-09-25T10:30:00Z',
      dependencies: ['redis', 'postgres', 'auth-service'],
      tags: ['gateway', 'routing', 'production']
    },
    {
      id: 'rate-limiter',
      name: 'Rate Limiter',
      description: 'Service de limitation de débit',
      status: 'running',
      health: 'healthy',
      version: '1.5.2',
      endpoint: '/api/rate-limit',
      port: 8081,
      metrics: {
        cpu: 25,
        memory: 42,
        disk: 30,
        network: 85,
        requests: 1890,
        errors: 1,
        latency: 12,
        uptime: 99.8
      },
      lastUpdate: '2025-09-25T10:25:00Z',
      dependencies: ['redis'],
      tags: ['rate-limit', 'security']
    },
    {
      id: 'auth-middleware',
      name: 'Auth Middleware',
      description: 'Middleware d\'authentification',
      status: 'running',
      health: 'warning',
      version: '3.0.1',
      endpoint: '/api/auth',
      port: 8082,
      metrics: {
        cpu: 55,
        memory: 78,
        disk: 35,
        network: 95,
        requests: 3450,
        errors: 8,
        latency: 78,
        uptime: 99.5
      },
      lastUpdate: '2025-09-25T10:20:00Z',
      dependencies: ['jwt-service', 'user-db'],
      tags: ['auth', 'security', 'middleware']
    },
    {
      id: 'load-balancer',
      name: 'Load Balancer',
      description: 'Répartiteur de charge',
      status: 'running',
      health: 'healthy',
      version: '2.3.0',
      endpoint: '/api/load-balancer',
      port: 8083,
      metrics: {
        cpu: 20,
        memory: 35,
        disk: 25,
        network: 450,
        requests: 5670,
        errors: 2,
        latency: 25,
        uptime: 99.95
      },
      lastUpdate: '2025-09-25T10:35:00Z',
      dependencies: ['health-check-service'],
      tags: ['load-balancer', 'distribution']
    }
  ];

  // Initialisation des données
  useEffect(() => {
    const initializeData = async () => {
      setIsLoading(true);
      
      // Simulation de chargement des données
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Routes API simulées
      const mockRoutes: APIRoute[] = [
        {
          id: '1',
          path: '/api/ai-services/*',
          method: 'GET',
          service: 'ai-services',
          enabled: true,
          rateLimitRpm: 1000,
          authRequired: true,
          currentRpm: 645,
          avgResponseTime: 125,
          errorRate: 0.2,
          totalRequests: 125430,
          lastAccess: '2025-09-25T10:35:00Z'
        },
        {
          id: '2',
          path: '/api/analytics/*',
          method: 'POST',
          service: 'analytics-services',
          enabled: true,
          rateLimitRpm: 500,
          authRequired: true,
          currentRpm: 234,
          avgResponseTime: 78,
          errorRate: 0.1,
          totalRequests: 89750,
          lastAccess: '2025-09-25T10:34:30Z'
        },
        {
          id: '3',
          path: '/api/content/upload',
          method: 'POST',
          service: 'content-services',
          enabled: false,
          rateLimitRpm: 100,
          authRequired: true,
          currentRpm: 0,
          avgResponseTime: 0,
          errorRate: 0,
          totalRequests: 0,
          lastAccess: 'Never'
        },
        {
          id: '4',
          path: '/api/auth/login',
          method: 'POST',
          service: 'auth-service',
          enabled: true,
          rateLimitRpm: 200,
          authRequired: false,
          currentRpm: 156,
          avgResponseTime: 95,
          errorRate: 2.1,
          totalRequests: 45620,
          lastAccess: '2025-09-25T10:35:15Z'
        }
      ];

      // Load balancers simulés
      const mockLoadBalancers: LoadBalancer[] = [
        {
          id: '1',
          name: 'AI Services LB',
          algorithm: 'round-robin',
          status: 'active',
          totalRequests: 125430,
          avgResponseTime: 125,
          instances: [
            {
              id: '1',
              url: 'ai-service-1:8080',
              weight: 100,
              status: 'healthy',
              currentConnections: 45,
              responseTime: 120
            },
            {
              id: '2',
              url: 'ai-service-2:8080',
              weight: 100,
              status: 'healthy',
              currentConnections: 38,
              responseTime: 130
            },
            {
              id: '3',
              url: 'ai-service-3:8080',
              weight: 50,
              status: 'maintenance',
              currentConnections: 0,
              responseTime: 0
            }
          ]
        }
      ];

      // Configuration sécurité simulée
      const mockSecurityConfig: SecurityConfig = {
        corsEnabled: true,
        corsOrigins: ['https://app.iacheries.com', 'https://dashboard.iacheries.com'],
        rateLimitGlobal: 10000,
        authenticationRequired: true,
        jwtValidation: true,
        apiKeyValidation: true,
        ipWhitelist: ['192.168.1.0/24', '10.0.0.0/8'],
        ipBlacklist: ['192.168.1.100', '10.0.0.50'],
        ddosProtection: true
      };

      setRoutes(mockRoutes);
      setLoadBalancers(mockLoadBalancers);
      setSecurityConfig(mockSecurityConfig);
      setIsLoading(false);
    };

    initializeData();
  }, []);

  // Filtrage des routes
  const filteredRoutes = routes.filter(route =>
    route.path.toLowerCase().includes(searchTerm.toLowerCase()) ||
    route.service.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Stats globales
  const totalRequests = routes.reduce((sum, route) => sum + route.totalRequests, 0);
  const totalCurrentRpm = routes.reduce((sum, route) => sum + route.currentRpm, 0);
  const avgResponseTime = routes.length > 0 
    ? routes.reduce((sum, route) => sum + route.avgResponseTime, 0) / routes.length 
    : 0;
  const avgErrorRate = routes.length > 0 
    ? routes.reduce((sum, route) => sum + route.errorRate, 0) / routes.length 
    : 0;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Globe className="w-8 h-8 animate-spin mx-auto mb-4" />
          <p>Chargement du gateway API...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center space-x-3">
              <Globe className="w-8 h-8 text-blue-600" />
              <span>API Gateway Enterprise</span>
            </h1>
            <p className="text-gray-600 mt-2">
              Gestion centralisée des routes, sécurité et répartition de charge
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <Badge variant="secondary" className="flex items-center space-x-1">
              <Activity className="w-3 h-3" />
              <span>16 Services Actifs</span>
            </Badge>
            <Button>
              <Settings className="w-4 h-4 mr-2" />
              Configuration
            </Button>
          </div>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Requests</CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{totalRequests.toLocaleString()}</div>
              <div className="flex items-center text-xs text-muted-foreground">
                <TrendingUp className="w-3 h-3 text-green-500 mr-1" />
                <span>+12.5% depuis hier</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Requests/min</CardTitle>
              <Zap className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{totalCurrentRpm.toLocaleString()}</div>
              <div className="flex items-center text-xs text-muted-foreground">
                <Activity className="w-3 h-3 text-blue-500 mr-1" />
                <span>En temps réel</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Avg Response</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{Math.round(avgResponseTime)}ms</div>
              <div className="flex items-center text-xs text-muted-foreground">
                <TrendingDown className="w-3 h-3 text-green-500 mr-1" />
                <span>-5% depuis 1h</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Error Rate</CardTitle>
              <AlertTriangle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{avgErrorRate.toFixed(2)}%</div>
              <div className="flex items-center text-xs text-muted-foreground">
                <CheckCircle2 className="w-3 h-3 text-green-500 mr-1" />
                <span>Excellent</span>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Navigation Tabs */}
        <Tabs value={selectedTab} onValueChange={setSelectedTab}>
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="overview">Vue d'ensemble</TabsTrigger>
            <TabsTrigger value="routes">Routes API</TabsTrigger>
            <TabsTrigger value="load-balancer">Load Balancer</TabsTrigger>
            <TabsTrigger value="security">Sécurité</TabsTrigger>
            <TabsTrigger value="services">Services</TabsTrigger>
          </TabsList>

          {/* Overview */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Routes les plus utilisées</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {routes
                      .filter(r => r.enabled)
                      .sort((a, b) => b.totalRequests - a.totalRequests)
                      .slice(0, 5)
                      .map(route => (
                        <div key={route.id} className="flex items-center justify-between p-3 border rounded">
                          <div>
                            <div className="flex items-center space-x-2">
                              <Badge variant={route.method === 'GET' ? 'default' : 'secondary'}>
                                {route.method}
                              </Badge>
                              <code className="text-sm">{route.path}</code>
                            </div>
                            <div className="text-sm text-gray-500 mt-1">
                              Service: {route.service}
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="font-medium">{route.totalRequests.toLocaleString()}</div>
                            <div className="text-sm text-gray-500">requests</div>
                          </div>
                        </div>
                      ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Status des Load Balancers</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {loadBalancers.map(lb => (
                      <div key={lb.id} className="p-4 border rounded">
                        <div className="flex items-center justify-between mb-3">
                          <div>
                            <h4 className="font-medium">{lb.name}</h4>
                            <p className="text-sm text-gray-500">
                              Algorithm: {lb.algorithm}
                            </p>
                          </div>
                          <Badge variant={lb.status === 'active' ? 'default' : 'destructive'}>
                            {lb.status}
                          </Badge>
                        </div>
                        <div className="space-y-2">
                          {lb.instances.map(instance => (
                            <div key={instance.id} className="flex items-center justify-between text-sm">
                              <span>{instance.url}</span>
                              <div className="flex items-center space-x-2">
                                <span>{instance.currentConnections} conn.</span>
                                <div className={`w-2 h-2 rounded-full ${
                                  instance.status === 'healthy' ? 'bg-green-500' :
                                  instance.status === 'maintenance' ? 'bg-yellow-500' : 'bg-red-500'
                                }`} />
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Métriques en temps réel */}
            <MetricsPanel 
              serviceId="api-gateway-main" 
              serviceName="API Gateway"
              realTime={true}
            />
          </TabsContent>

          {/* Routes API */}
          <TabsContent value="routes" className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Gestion des Routes API</CardTitle>
                  <Button>Ajouter Route</Button>
                </div>
                <div className="flex items-center space-x-4 mt-4">
                  <Input
                    placeholder="Rechercher une route..."
                    value={searchTerm}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearchTerm(e.target.value)}
                    className="max-w-sm"
                  />
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {filteredRoutes.map(route => (
                    <div key={route.id} className="p-4 border rounded hover:bg-gray-50">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <Badge variant={route.method === 'GET' ? 'default' : 'secondary'}>
                            {route.method}
                          </Badge>
                          <code className="font-mono text-sm">{route.path}</code>
                          <Badge variant="outline">{route.service}</Badge>
                          {route.authRequired && (
                            <Lock className="w-4 h-4 text-yellow-600" />
                          )}
                        </div>
                        <div className="flex items-center space-x-4">
                          <Switch checked={route.enabled} />
                          <Button variant="ghost" size="sm">
                            <Settings className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-5 gap-4 mt-4 text-sm">
                        <div>
                          <span className="text-gray-500">Rate Limit:</span>
                          <div className="font-medium">{route.rateLimitRpm}/min</div>
                        </div>
                        <div>
                          <span className="text-gray-500">Current:</span>
                          <div className="font-medium">{route.currentRpm}/min</div>
                        </div>
                        <div>
                          <span className="text-gray-500">Response Time:</span>
                          <div className="font-medium">{route.avgResponseTime}ms</div>
                        </div>
                        <div>
                          <span className="text-gray-500">Error Rate:</span>
                          <div className={`font-medium ${route.errorRate > 1 ? 'text-red-600' : 'text-green-600'}`}>
                            {route.errorRate}%
                          </div>
                        </div>
                        <div>
                          <span className="text-gray-500">Total:</span>
                          <div className="font-medium">{route.totalRequests.toLocaleString()}</div>
                        </div>
                      </div>
                      
                      <Progress 
                        value={(route.currentRpm / route.rateLimitRpm) * 100} 
                        className="mt-2 h-2"
                      />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Services */}
          <TabsContent value="services" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {gatewayServices.map(service => (
                <ServiceCard key={service.id} service={service} />
              ))}
            </div>
          </TabsContent>

          {/* Autres onglets à implémenter... */}
        </Tabs>
      </div>
    </div>
  );
};

export default APIGatewayDashboard;