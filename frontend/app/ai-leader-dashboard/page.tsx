'use client';

import { useState, useEffect } from 'react';
import { Brain, Zap, TrendingUp, CheckCircle, AlertCircle, Activity, Target, Cpu } from 'lucide-react';

interface AgentStatus {
  phase: string;
  autonomy_percentage: number;
  total_api_calls_observed: number;
  total_api_calls_replaced: number;
  apis_tracked: number;
  capabilities_ready: number;
  is_fully_autonomous: boolean;
  ready_capabilities: any[];
}

interface Capability {
  name: string;
  type: string;
  accuracy: number;
  quality: number;
  speed: number;
  training_progress: number;
  ready_for_production: boolean;
  matches_api_quality: boolean;
  better_than_api: boolean;
}

interface LearningData {
  api_name: string;
  api_type: string;
  training_samples: number;
  success_rate: number;
  model_accuracy: number;
  is_available: boolean;
  consecutive_failures: number;
  avg_latency: number;
  avg_quality: number;
  cost_per_request: number;
}

export default function AILeaderDashboard() {
  const [agentStatus, setAgentStatus] = useState<AgentStatus | null>(null);
  const [capabilities, setCapabilities] = useState<Capability[]>([]);
  const [learningData, setLearningData] = useState<LearningData[]>([]);
  const [autonomyMetrics, setAutonomyMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'capabilities' | 'learning' | 'metrics'>('overview');

  useEffect(() => {
    fetchAllData();
    const interval = setInterval(fetchAllData, 5000); // Refresh every 5s
    return () => clearInterval(interval);
  }, []);

  const fetchAllData = async () => {
    try {
      const [statusRes, capRes, learningRes, metricsRes] = await Promise.all([
        fetch('http://localhost:8000/ai-leader/status'),
        fetch('http://localhost:8000/ai-leader/capabilities'),
        fetch('http://localhost:8000/ai-leader/learning-data'),
        fetch('http://localhost:8000/ai-leader/autonomy-metrics')
      ]);

      const statusData = await statusRes.json();
      const capData = await capRes.json();
      const learningDataRes = await learningRes.json();
      const metricsData = await metricsRes.json();

      setAgentStatus(statusData.agent);
      setCapabilities(capData.capabilities || []);
      setLearningData(learningDataRes.learning_data || []);
      setAutonomyMetrics(metricsData.metrics);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching AI Leader data:', error);
      setLoading(false);
    }
  };

  const getPhaseColor = (phase: string) => {
    switch (phase) {
      case 'learning': return 'text-blue-400';
      case 'backup': return 'text-yellow-400';
      case 'autonomous': return 'text-green-400';
      case 'evolution': return 'text-purple-400';
      default: return 'text-gray-400';
    }
  };

  const getPhaseIcon = (phase: string) => {
    switch (phase) {
      case 'learning': return '🎓';
      case 'backup': return '🔄';
      case 'autonomous': return '🚀';
      case 'evolution': return '✨';
      default: return '🤖';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 flex items-center justify-center">
        <div className="text-white text-xl">Chargement de l'AI Leader Agent...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 text-white p-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-4 mb-4">
          <Brain className="w-12 h-12 text-purple-400" />
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
              AI Leader Agent Dashboard
            </h1>
            <p className="text-gray-400">Agent IA Autonome et Auto-Apprenant</p>
          </div>
        </div>

        {/* Phase actuelle */}
        {agentStatus && (
          <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <span className="text-4xl">{getPhaseIcon(agentStatus.phase)}</span>
                <div>
                  <div className="text-sm text-gray-400">Phase Actuelle</div>
                  <div className={`text-2xl font-bold ${getPhaseColor(agentStatus.phase)}`}>
                    {agentStatus.phase.toUpperCase()}
                  </div>
                </div>
              </div>
              
              <div className="flex items-center gap-8">
                <div className="text-center">
                  <div className="text-3xl font-bold text-green-400">
                    {(agentStatus.autonomy_percentage * 100).toFixed(1)}%
                  </div>
                  <div className="text-sm text-gray-400">Autonomie</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-blue-400">
                    {agentStatus.capabilities_ready}
                  </div>
                  <div className="text-sm text-gray-400">Capacités Prêtes</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-purple-400">
                    {agentStatus.apis_tracked}
                  </div>
                  <div className="text-sm text-gray-400">APIs Observées</div>
                </div>
              </div>
            </div>

            {/* Barre de progression autonomie */}
            <div className="mt-6">
              <div className="flex justify-between text-sm mb-2">
                <span>Progression vers Autonomie Complète</span>
                <span>{(agentStatus.autonomy_percentage * 100).toFixed(1)}%</span>
              </div>
              <div className="w-full h-3 bg-gray-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all duration-500"
                  style={{ width: `${agentStatus.autonomy_percentage * 100}%` }}
                />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6">
        {(['overview', 'capabilities', 'learning', 'metrics'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-6 py-3 rounded-xl font-medium transition-all ${
              activeTab === tab
                ? 'bg-purple-500 text-white'
                : 'bg-white/10 text-gray-400 hover:bg-white/20'
            }`}
          >
            {tab === 'overview' && '📊 Vue d\'ensemble'}
            {tab === 'capabilities' && '🎯 Capacités'}
            {tab === 'learning' && '📚 Apprentissage'}
            {tab === 'metrics' && '📈 Métriques'}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && agentStatus && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Stats Cards */}
          <div className="bg-gradient-to-br from-blue-500/20 to-blue-600/20 rounded-2xl p-6 border border-blue-500/30">
            <Activity className="w-8 h-8 text-blue-400 mb-3" />
            <div className="text-3xl font-bold mb-1">{agentStatus.total_api_calls_observed}</div>
            <div className="text-sm text-gray-400">Appels API Observés</div>
          </div>

          <div className="bg-gradient-to-br from-green-500/20 to-green-600/20 rounded-2xl p-6 border border-green-500/30">
            <CheckCircle className="w-8 h-8 text-green-400 mb-3" />
            <div className="text-3xl font-bold mb-1">{agentStatus.total_api_calls_replaced}</div>
            <div className="text-sm text-gray-400">Appels Remplacés</div>
          </div>

          <div className="bg-gradient-to-br from-purple-500/20 to-purple-600/20 rounded-2xl p-6 border border-purple-500/30">
            <Cpu className="w-8 h-8 text-purple-400 mb-3" />
            <div className="text-3xl font-bold mb-1">{agentStatus.capabilities_ready}</div>
            <div className="text-sm text-gray-400">Capacités Prêtes</div>
          </div>

          <div className="bg-gradient-to-br from-yellow-500/20 to-yellow-600/20 rounded-2xl p-6 border border-yellow-500/30">
            <Target className="w-8 h-8 text-yellow-400 mb-3" />
            <div className="text-3xl font-bold mb-1">{agentStatus.apis_tracked}</div>
            <div className="text-sm text-gray-400">APIs Trackées</div>
          </div>

          {/* Ready Capabilities */}
          <div className="col-span-full bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
            <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
              <CheckCircle className="w-6 h-6 text-green-400" />
              Capacités Prêtes pour Production
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {agentStatus.ready_capabilities.map((cap, idx) => (
                <div key={idx} className="bg-green-500/20 rounded-xl p-4 border border-green-500/30">
                  <div className="font-medium mb-2">{cap.name}</div>
                  <div className="text-sm text-gray-400 mb-3">{cap.type}</div>
                  <div className="space-y-1">
                    <div className="flex justify-between text-sm">
                      <span>Accuracy:</span>
                      <span className="text-green-400">{(cap.accuracy * 100).toFixed(1)}%</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Quality:</span>
                      <span className="text-blue-400">{(cap.quality * 100).toFixed(1)}%</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Speed:</span>
                      <span className="text-purple-400">{cap.speed.toFixed(1)} req/s</span>
                    </div>
                  </div>
                  {cap.better_than_api && (
                    <div className="mt-2 text-xs text-green-400 flex items-center gap-1">
                      <Zap className="w-3 h-3" />
                      Meilleur que l'API externe
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Capabilities Tab */}
      {activeTab === 'capabilities' && (
        <div className="space-y-4">
          {capabilities.map((cap, idx) => (
            <div key={idx} className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-xl font-bold">{cap.name}</h3>
                  <p className="text-sm text-gray-400">{cap.type}</p>
                </div>
                <div className="flex items-center gap-2">
                  {cap.ready_for_production && (
                    <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-sm">
                      ✅ Production Ready
                    </span>
                  )}
                  {cap.better_than_api && (
                    <span className="px-3 py-1 bg-purple-500/20 text-purple-400 rounded-full text-sm">
                      ⚡ Meilleur que API
                    </span>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-4 gap-4 mb-4">
                <div>
                  <div className="text-sm text-gray-400 mb-1">Accuracy</div>
                  <div className="text-2xl font-bold text-green-400">{(cap.accuracy * 100).toFixed(1)}%</div>
                </div>
                <div>
                  <div className="text-sm text-gray-400 mb-1">Quality</div>
                  <div className="text-2xl font-bold text-blue-400">{(cap.quality * 100).toFixed(1)}%</div>
                </div>
                <div>
                  <div className="text-sm text-gray-400 mb-1">Speed</div>
                  <div className="text-2xl font-bold text-purple-400">{cap.speed.toFixed(1)} req/s</div>
                </div>
                <div>
                  <div className="text-sm text-gray-400 mb-1">Progress</div>
                  <div className="text-2xl font-bold text-yellow-400">{(cap.training_progress * 100).toFixed(1)}%</div>
                </div>
              </div>

              {/* Progress bar */}
              <div className="w-full h-2 bg-gray-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all duration-500"
                  style={{ width: `${cap.training_progress * 100}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Learning Tab */}
      {activeTab === 'learning' && (
        <div className="space-y-4">
          {learningData.map((data, idx) => (
            <div key={idx} className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-xl font-bold">{data.api_name}</h3>
                  <p className="text-sm text-gray-400">{data.api_type}</p>
                </div>
                <div className="flex items-center gap-2">
                  {data.is_available ? (
                    <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-sm flex items-center gap-1">
                      <CheckCircle className="w-4 h-4" />
                      Disponible
                    </span>
                  ) : (
                    <span className="px-3 py-1 bg-red-500/20 text-red-400 rounded-full text-sm flex items-center gap-1">
                      <AlertCircle className="w-4 h-4" />
                      Indisponible
                    </span>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <div className="text-sm text-gray-400 mb-1">Échantillons</div>
                  <div className="text-xl font-bold">{data.training_samples}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-400 mb-1">Taux de Succès</div>
                  <div className="text-xl font-bold text-green-400">{(data.success_rate * 100).toFixed(1)}%</div>
                </div>
                <div>
                  <div className="text-sm text-gray-400 mb-1">Accuracy Modèle</div>
                  <div className="text-xl font-bold text-blue-400">{(data.model_accuracy * 100).toFixed(1)}%</div>
                </div>
                <div>
                  <div className="text-sm text-gray-400 mb-1">Coût/Requête</div>
                  <div className="text-xl font-bold text-yellow-400">${data.cost_per_request.toFixed(4)}</div>
                </div>
              </div>

              {data.consecutive_failures > 0 && (
                <div className="mt-4 p-3 bg-red-500/20 rounded-lg flex items-center gap-2 text-red-400">
                  <AlertCircle className="w-5 h-5" />
                  <span>{data.consecutive_failures} échecs consécutifs</span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Metrics Tab */}
      {activeTab === 'metrics' && autonomyMetrics && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
            <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
              <TrendingUp className="w-6 h-6 text-green-400" />
              Métriques d'Autonomie
            </h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Pourcentage d'Autonomie</span>
                <span className="text-2xl font-bold text-green-400">
                  {(autonomyMetrics.autonomy_percentage * 100).toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Couverture APIs</span>
                <span className="text-2xl font-bold text-blue-400">
                  {(autonomyMetrics.api_coverage * 100).toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Réduction de Coût</span>
                <span className="text-2xl font-bold text-purple-400">
                  {autonomyMetrics.cost_reduction_percentage}%
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Autonomie Complète</span>
                <span className="text-2xl">
                  {autonomyMetrics.is_fully_autonomous ? '✅' : '⏳'}
                </span>
              </div>
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
            <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
              <Activity className="w-6 h-6 text-purple-400" />
              Statistiques d'Utilisation
            </h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Appels Observés</span>
                <span className="text-2xl font-bold text-blue-400">
                  {autonomyMetrics.total_calls_observed}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Appels Remplacés</span>
                <span className="text-2xl font-bold text-green-400">
                  {autonomyMetrics.total_calls_replaced}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Économies Estimées</span>
                <span className="text-2xl font-bold text-yellow-400">
                  ${autonomyMetrics.estimated_savings.toFixed(2)}
                </span>
              </div>
            </div>
          </div>

          <div className="col-span-full bg-gradient-to-r from-purple-500/20 to-pink-500/20 rounded-2xl p-8 border border-purple-500/30">
            <div className="text-center">
              <Brain className="w-16 h-16 text-purple-400 mx-auto mb-4" />
              <h3 className="text-2xl font-bold mb-2">
                {autonomyMetrics.is_fully_autonomous ? '🎉 Agent Totalement Autonome !' : '⏳ En route vers l\'Autonomie'}
              </h3>
              <p className="text-gray-400 mb-6">
                {autonomyMetrics.is_fully_autonomous
                  ? 'L\'agent gère maintenant tout sans APIs externes requises'
                  : `Encore ${(100 - autonomyMetrics.autonomy_percentage * 100).toFixed(1)}% avant l'autonomie complète`}
              </p>
              <div className="w-full h-4 bg-gray-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all duration-1000"
                  style={{ width: `${autonomyMetrics.autonomy_percentage * 100}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
