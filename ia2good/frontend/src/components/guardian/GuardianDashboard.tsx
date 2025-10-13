import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { SOSButton } from './SOSButton';
import { HazardAlert, AlertHistory, Hazard } from './HazardAlert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Activity, Shield, MessageSquare, Settings, TrendingUp } from 'lucide-react';

interface GuardianDashboardProps {
  userId: string;
}

export const GuardianDashboard: React.FC<GuardianDashboardProps> = ({ userId }) => {
  const [isActive, setIsActive] = useState(true);
  const [recentAlerts, setRecentAlerts] = useState<Hazard[]>([]);
  const [currentHazard, setCurrentHazard] = useState<Hazard | null>(null);
  const [stats, setStats] = useState({
    totalAlerts: 0,
    sosTriggered: 0,
    detectionAccuracy: 0,
    activeDays: 0,
  });

  // Mock data - replace with real API calls
  useEffect(() => {
    // Simulate loading stats
    setStats({
      totalAlerts: 47,
      sosTriggered: 2,
      detectionAccuracy: 94.2,
      activeDays: 28,
    });

    // Simulate loading recent alerts
    const mockAlerts: Hazard[] = [
      {
        id: '1',
        hazard_type: 'vehicle_horn',
        confidence: 0.95,
        urgency: 'HIGH',
        alert_message: '⚠️ VÉHICULE PROCHE',
        timestamp: new Date(Date.now() - 3600000).toISOString(),
      },
      {
        id: '2',
        hazard_type: 'siren',
        confidence: 0.89,
        urgency: 'MEDIUM',
        alert_message: '🚨 Sirène détectée',
        timestamp: new Date(Date.now() - 7200000).toISOString(),
      },
      {
        id: '3',
        hazard_type: 'door_knock',
        confidence: 0.82,
        urgency: 'LOW',
        alert_message: '🚪 Quelqu\'un frappe',
        timestamp: new Date(Date.now() - 10800000).toISOString(),
      },
    ];
    setRecentAlerts(mockAlerts);
  }, [userId]);

  const handleSOSTrigger = async () => {
    console.log('SOS Triggered!');
    // TODO: Call API to trigger SOS
    // POST /guardian/sos/trigger
    alert('🆘 SOS DÉCLENCHÉ! Contacts d\'urgence notifiés.');
  };

  const handleSOSCancel = () => {
    console.log('SOS Cancelled');
    // TODO: Call API to cancel SOS
    // PUT /guardian/sos/{alert_id}/cancel
  };

  const toggleDetection = () => {
    setIsActive(!isActive);
    // TODO: Start/stop audio detection
  };

  return (
    <div className="container mx-auto p-4 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold mb-2">🛡️ Guardian</h1>
          <p className="text-gray-600 text-lg">Assistant de protection et d'accessibilité</p>
        </div>
        <Badge
          variant={isActive ? 'default' : 'secondary'}
          className="text-lg px-4 py-2 cursor-pointer"
          onClick={toggleDetection}
        >
          <Activity className="w-4 h-4 mr-2" />
          {isActive ? 'Détection Active' : 'Détection Inactive'}
        </Badge>
      </div>

      {/* Current Hazard Alert */}
      {currentHazard && (
        <HazardAlert hazard={currentHazard} onDismiss={() => setCurrentHazard(null)} />
      )}

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* SOS Button - Left Column */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle className="text-center text-2xl">Urgence</CardTitle>
            </CardHeader>
            <CardContent className="flex justify-center py-8">
              <SOSButton
                size="large"
                onTrigger={handleSOSTrigger}
                onCancel={handleSOSCancel}
              />
            </CardContent>
          </Card>

          {/* Statistics */}
          <Card className="mt-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                Statistiques
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Alertes totales</span>
                <span className="text-2xl font-bold">{stats.totalAlerts}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">SOS déclenchés</span>
                <span className="text-2xl font-bold text-red-600">{stats.sosTriggered}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Précision</span>
                <span className="text-2xl font-bold text-green-600">
                  {stats.detectionAccuracy}%
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Jours actifs</span>
                <span className="text-2xl font-bold">{stats.activeDays}</span>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Panel - Right Columns */}
        <div className="lg:col-span-2">
          <Tabs defaultValue="alerts" className="w-full">
            <TabsList className="grid w-full grid-cols-3 text-lg">
              <TabsTrigger value="alerts" className="text-base">
                <Shield className="w-4 h-4 mr-2" />
                Alertes
              </TabsTrigger>
              <TabsTrigger value="communication" className="text-base">
                <MessageSquare className="w-4 h-4 mr-2" />
                Communication
              </TabsTrigger>
              <TabsTrigger value="settings" className="text-base">
                <Settings className="w-4 h-4 mr-2" />
                Paramètres
              </TabsTrigger>
            </TabsList>

            <TabsContent value="alerts" className="mt-4">
              <Card>
                <CardHeader>
                  <CardTitle>Historique des Alertes</CardTitle>
                </CardHeader>
                <CardContent>
                  {recentAlerts.length > 0 ? (
                    <AlertHistory alerts={recentAlerts} />
                  ) : (
                    <div className="text-center py-12 text-gray-500">
                      <Shield className="w-16 h-16 mx-auto mb-4 opacity-50" />
                      <p className="text-lg">Aucune alerte récente</p>
                      <p className="text-sm">La détection est active et surveille votre environnement</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="communication" className="mt-4">
              <Card>
                <CardHeader>
                  <CardTitle>Outils de Communication</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-12">
                    <MessageSquare className="w-16 h-16 mx-auto mb-4 text-blue-500" />
                    <p className="text-lg mb-4">Accédez aux outils de communication</p>
                    <p className="text-sm text-gray-600 mb-6">
                      Speech-to-Text, Text-to-Speech, et traduction en temps réel
                    </p>
                    <a
                      href="/guardian/communication"
                      className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                      Ouvrir l'interface de communication
                    </a>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="settings" className="mt-4">
              <Card>
                <CardHeader>
                  <CardTitle>Accès Rapide aux Paramètres</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-12">
                    <Settings className="w-16 h-16 mx-auto mb-4 text-gray-500" />
                    <p className="text-lg mb-4">Configurez votre expérience Guardian</p>
                    <p className="text-sm text-gray-600 mb-6">
                      Personnalisez les alertes, contacts d'urgence, et préférences d'accessibilité
                    </p>
                    <a
                      href="/guardian/settings"
                      className="inline-block px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
                    >
                      Ouvrir les paramètres
                    </a>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Actions Rapides</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <button
              onClick={toggleDetection}
              className="p-6 border-2 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <Activity className={`w-8 h-8 mx-auto mb-2 ${isActive ? 'text-green-600' : 'text-gray-400'}`} />
              <p className="text-sm font-medium">
                {isActive ? 'Désactiver' : 'Activer'} Détection
              </p>
            </button>

            <a
              href="/guardian/communication"
              className="p-6 border-2 rounded-lg hover:bg-gray-50 transition-colors text-center"
            >
              <MessageSquare className="w-8 h-8 mx-auto mb-2 text-blue-600" />
              <p className="text-sm font-medium">Communication</p>
            </a>

            <a
              href="/guardian/settings"
              className="p-6 border-2 rounded-lg hover:bg-gray-50 transition-colors text-center"
            >
              <Settings className="w-8 h-8 mx-auto mb-2 text-gray-600" />
              <p className="text-sm font-medium">Paramètres</p>
            </a>

            <a
              href="/guardian/history"
              className="p-6 border-2 rounded-lg hover:bg-gray-50 transition-colors text-center"
            >
              <TrendingUp className="w-8 h-8 mx-auto mb-2 text-purple-600" />
              <p className="text-sm font-medium">Historique</p>
            </a>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
