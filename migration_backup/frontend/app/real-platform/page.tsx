'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';

interface BackendSystemStatus {
  platform: string;
  status: string;
  version: string;
  uptime: number;
  components: {
    ai_orchestrator: {
      available: boolean;
      agents_count: number;
      types: string[];
    };
    collaboration_system: {
      available: boolean;
      features: string[];
    };
    websocket_manager: {
      available: boolean;
      features: string[];
    };
    microservices: {
      total_count: number;
      categories: Record<string, any>;
    };
    remix_studios: {
      available: boolean;
      features: string[];
    };
  };
}

interface AIAgentsData {
  status: string;
  total_agents: number;
  agents?: any[];
  categories?: Record<string, string[]>;
}

export default function RealPlatformDashboard() {
  const [systemStatus, setSystemStatus] = useState<BackendSystemStatus | null>(null);
  const [aiAgents, setAIAgents] = useState<AIAgentsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRealData = async () => {
      try {
        setLoading(true);
        
        // Récupérer le statut système complet
        const systemResponse = await fetch('http://localhost:8000/system/status');
        if (systemResponse.ok) {
          const systemData = await systemResponse.json();
          setSystemStatus(systemData);
        }

        // Récupérer les agents IA
        const aiResponse = await fetch('http://localhost:8000/ai-agents');
        if (aiResponse.ok) {
          const aiData = await aiResponse.json();
          setAIAgents(aiData);
        }

      } catch (err) {
        setError('Erreur de connexion au backend');
        console.error('Erreur:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchRealData();
    
    // Actualiser toutes les 10 secondes
    const interval = setInterval(fetchRealData, 10000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-xl text-gray-600">Chargement des données temps réel...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center bg-red-50 p-8 rounded-lg border border-red-200">
          <h2 className="text-2xl font-bold text-red-800 mb-4">❌ Erreur de Connexion</h2>
          <p className="text-red-600">{error}</p>
          <button 
            onClick={() => window.location.reload()} 
            className="mt-4 bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
          >
            Réessayer
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header avec statut temps réel */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                🚀 {systemStatus?.platform || 'IA Chéries Enterprise Platform'}
              </h1>
              <p className="text-gray-600 mt-1">
                Version {systemStatus?.version || 'N/A'} - Uptime: {
                  systemStatus?.uptime ? Math.round(systemStatus.uptime / 60) : 0
                } minutes
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <div className={`px-4 py-2 rounded-lg font-medium ${
                systemStatus?.status === 'operational' 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-yellow-100 text-yellow-800'
              }`}>
                {systemStatus?.status === 'operational' ? '✅ Opérationnel' : '⚠️ En cours'}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        
        {/* Stats en temps réel */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center">
              <div className="text-3xl mr-4">🤖</div>
              <div>
                <div className="text-2xl font-bold text-blue-600">
                  {aiAgents?.total_agents || systemStatus?.components.ai_orchestrator.agents_count || 0}
                </div>
                <div className="text-gray-600 text-sm">Agents IA Actifs</div>
                <div className="text-xs text-green-600 mt-1">
                  {aiAgents?.status === '✅ ACTIVE' ? 'Orchestrateur actif' : 'Initialisation...'}
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center">
              <div className="text-3xl mr-4">🔧</div>
              <div>
                <div className="text-2xl font-bold text-green-600">
                  {systemStatus?.components.microservices.total_count || 680}
                </div>
                <div className="text-gray-600 text-sm">Microservices</div>
                <div className="text-xs text-blue-600 mt-1">Architecture distribuée</div>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center">
              <div className="text-3xl mr-4">🤝</div>
              <div>
                <div className="text-2xl font-bold text-purple-600">
                  {systemStatus?.components.collaboration_system.available ? 'ACTIF' : 'OFF'}
                </div>
                <div className="text-gray-600 text-sm">Collaboration IA</div>
                <div className="text-xs text-purple-600 mt-1">Matching créateurs</div>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center">
              <div className="text-3xl mr-4">💬</div>
              <div>
                <div className="text-2xl font-bold text-orange-600">
                  {systemStatus?.components.websocket_manager.available ? 'LIVE' : 'OFF'}
                </div>
                <div className="text-gray-600 text-sm">WebSocket</div>
                <div className="text-xs text-orange-600 mt-1">Temps réel</div>
              </div>
            </div>
          </div>
        </div>

        {/* Catégories d'agents IA */}
        {aiAgents?.categories && (
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">🤖 Catégories d'Agents IA</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {Object.entries(aiAgents.categories).map(([category, agents]) => (
                <div key={category} className="bg-white p-4 rounded-lg shadow-sm border">
                  <h3 className="font-semibold text-gray-900 mb-2 capitalize">{category}</h3>
                  <div className="space-y-1">
                    {agents.map((agent: string, idx: number) => (
                      <div key={idx} className="text-sm text-blue-600">• {agent}</div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Actions rapides */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h2 className="text-xl font-bold text-gray-900 mb-4">⚡ Actions Rapides</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <a href="http://localhost:8000/docs" target="_blank" 
               className="bg-blue-50 border border-blue-200 p-3 rounded hover:bg-blue-100 text-center">
              <div className="text-2xl mb-1">📚</div>
              <div className="text-sm font-medium text-blue-900">API Docs</div>
            </a>
            
            <a href="http://localhost:8000/health" target="_blank"
               className="bg-green-50 border border-green-200 p-3 rounded hover:bg-green-100 text-center">
              <div className="text-2xl mb-1">💚</div>
              <div className="text-sm font-medium text-green-900">Health</div>
            </a>

            <a href="http://localhost:8000/system/status" target="_blank"
               className="bg-purple-50 border border-purple-200 p-3 rounded hover:bg-purple-100 text-center">
              <div className="text-2xl mb-1">🔍</div>
              <div className="text-sm font-medium text-purple-900">Status</div>
            </a>

            <Link href="/api-tester"
               className="bg-orange-50 border border-orange-200 p-3 rounded hover:bg-orange-100 text-center">
              <div className="text-2xl mb-1">🧪</div>
              <div className="text-sm font-medium text-orange-900">Test API</div>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}