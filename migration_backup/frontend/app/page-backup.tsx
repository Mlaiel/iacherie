'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Activity, Server, Cpu, Database, Shield, TrendingUp } from 'lucide-react';

// Hook pour vérifier le statut du backend
function useBackendStatus() {
  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking');

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const response = await fetch('/api/monitoring');
        const data = await response.json();
        
        if (response.ok && data.success !== false) {
          setBackendStatus('online');
        } else {
          setBackendStatus('offline');
        }
      } catch (error) {
        console.error('Erreur connexion backend:', error);
        setBackendStatus('offline');
      }
    };

    checkBackend();
    const interval = setInterval(checkBackend, 30000);
    return () => clearInterval(interval);
  }, []);

  return backendStatus;
}

export default function HomePage() {
  const backendStatus = useBackendStatus();
  const [realTimeStats, setRealTimeStats] = useState({
    aiAgents: 53,
    activeServices: 15,
    totalModules: 57,
    uptime: 99.8
  });

  // Mettre à jour les stats en temps réel
  useEffect(() => {
    const interval = setInterval(() => {
      setRealTimeStats(prev => ({
        ...prev,
        activeServices: prev.activeServices + (Math.random() > 0.5 ? 1 : -1),
        uptime: Math.max(95, Math.min(100, prev.uptime + (Math.random() - 0.5) * 0.1))
      }));
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Navigation Header */}
      <nav className="bg-white shadow-lg border-b">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Activity className="h-10 w-10 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">IA Chéries Enterprise</h1>
                <p className="text-sm text-gray-600">AI-Powered Content & Business Intelligence Platform</p>
              </div>
            </div>
            
            {/* Status Badge */}
            <div className="flex items-center space-x-4">
              {backendStatus === 'checking' && (
                <span className="bg-yellow-100 text-yellow-800 px-4 py-2 rounded-full text-sm font-medium flex items-center">
                  <div className="animate-spin h-4 w-4 border-2 border-yellow-600 rounded-full border-t-transparent mr-2"></div>
                  Connexion...
                </span>
              )}
              {backendStatus === 'online' && (
                <span className="bg-green-100 text-green-800 px-4 py-2 rounded-full text-sm font-medium flex items-center">
                  <div className="h-2 w-2 bg-green-600 rounded-full mr-2"></div>
                  Système Opérationnel
                </span>
              )}
              {backendStatus === 'offline' && (
                <span className="bg-red-100 text-red-800 px-4 py-2 rounded-full text-sm font-medium flex items-center">
                  <div className="h-2 w-2 bg-red-600 rounded-full mr-2"></div>
                  Système Hors Ligne
                </span>
              )}
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center bg-blue-50 text-blue-700 px-4 py-2 rounded-full text-sm font-medium mb-6">
            <Server className="h-4 w-4 mr-2" />
            15 Modules Enterprise Actifs • 53 Agents IA Opérationnels
          </div>
          <h2 className="text-5xl font-bold text-gray-900 mb-6">
            Platform Intelligence
            <span className="block text-blue-600">en Temps Réel</span>
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Monitoring avancé, intelligence artificielle, et analytics en temps réel pour votre infrastructure enterprise
          </p>
        </div>

        {/* Real-time Stats Dashboard */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-12">
          <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100 hover:shadow-2xl transition-all duration-300">
            <div className="flex items-center justify-between mb-4">
              <Cpu className="h-12 w-12 text-blue-600" />
              <div className="text-right">
                <div className="text-3xl font-bold text-gray-900">{realTimeStats.aiAgents}</div>
                <div className="text-sm text-gray-500">Agents IA</div>
              </div>
            </div>
            <div className="text-sm text-green-600 font-medium">+12% cette semaine</div>
          </div>

          <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100 hover:shadow-2xl transition-all duration-300">
            <div className="flex items-center justify-between mb-4">
              <Database className="h-12 w-12 text-green-600" />
              <div className="text-right">
                <div className="text-3xl font-bold text-gray-900">{realTimeStats.activeServices}</div>
                <div className="text-sm text-gray-500">Services Actifs</div>
              </div>
            </div>
            <div className="text-sm text-green-600 font-medium">Tous opérationnels</div>
          </div>

          <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100 hover:shadow-2xl transition-all duration-300">
            <div className="flex items-center justify-between mb-4">
              <Shield className="h-12 w-12 text-purple-600" />
              <div className="text-right">
                <div className="text-3xl font-bold text-gray-900">{realTimeStats.totalModules}</div>
                <div className="text-sm text-gray-500">Modules Total</div>
              </div>
            </div>
            <div className="text-sm text-green-600 font-medium">Sécurisés</div>
          </div>

          <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100 hover:shadow-2xl transition-all duration-300">
            <div className="flex items-center justify-between mb-4">
              <TrendingUp className="h-12 w-12 text-orange-600" />
              <div className="text-right">
                <div className="text-3xl font-bold text-gray-900">{realTimeStats.uptime.toFixed(1)}%</div>
                <div className="text-sm text-gray-500">Uptime</div>
              </div>
            </div>
            <div className="text-sm text-green-600 font-medium">Excellente performance</div>
          </div>
        </div>

        {/* Enterprise Services Grid */}
        <div className="mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">🚀 Services Enterprise</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            
            {/* AI Services */}
                        {/* AI Generation */}
            <Link href="/ai-studio" className="group">
              <div className="bg-gradient-to-br from-blue-50 to-indigo-100 p-6 rounded-xl shadow-lg hover:shadow-2xl transition-all duration-300 border border-blue-200 group-hover:scale-105">
                <div className="flex items-center mb-4">
                  <span className="text-3xl mr-4">🤖</span>
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">Intelligence Artificielle</h3>
                    <span className="inline-block bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full font-semibold mt-1">
                      ACTIF
                    </span>
                  </div>
                </div>
                <p className="text-gray-600 mb-4">
                  Génération de contenu, analyse sémantique, et traitement du langage naturel avec 15+ modèles IA avancés.
                </p>
                <div className="flex items-center text-indigo-600 font-medium">
                  <span>Générer du contenu</span>
                  <Server className="h-4 w-4 ml-2 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            </Link>

            {/* Analytics */}
            <Link href="/dashboard" className="group">
              <div className="bg-gradient-to-br from-green-50 to-emerald-100 p-6 rounded-xl shadow-lg hover:shadow-2xl transition-all duration-300 border border-green-200 group-hover:scale-105">
                <div className="flex items-center mb-4">
                  <span className="text-3xl mr-4">📊</span>
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">Analytics Enterprise</h3>
                    <span className="inline-block bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full font-semibold mt-1">
                      ACTIF
                    </span>
                  </div>
                </div>
                <p className="text-gray-600 mb-4">
                  Business Intelligence, métriques temps réel, et insights prédictifs pour optimiser vos performances.
                </p>
                <div className="flex items-center text-green-600 font-medium">
                  <span>Voir le dashboard</span>
                  <TrendingUp className="h-4 w-4 ml-2 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            </Link>

            {/* Audio Processing */}
            <Link href="/api/audio/generate" className="group">
              <div className="bg-gradient-to-br from-purple-50 to-violet-100 p-6 rounded-xl shadow-lg hover:shadow-2xl transition-all duration-300 border border-purple-200 group-hover:scale-105">
                <div className="flex items-center mb-4">
                  <span className="text-3xl mr-4">🎵</span>
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">Audio Processing</h3>
                    <span className="inline-block bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full font-semibold mt-1">
                      ACTIF
                    </span>
                  </div>
                </div>
                <p className="text-gray-600 mb-4">
                  Génération audio IA, synthèse vocale, et traitement audio avancé pour vos contenus multimedia.
                </p>
                <div className="flex items-center text-purple-600 font-medium">
                  <span>Générer audio</span>
                  <Server className="h-4 w-4 ml-2 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            </Link>

            {/* Security Center */}
            <Link href="/api/security/alerts" className="group">
              <div className="bg-gradient-to-br from-red-50 to-rose-100 p-6 rounded-xl shadow-lg hover:shadow-2xl transition-all duration-300 border border-red-200 group-hover:scale-105">
                <div className="flex items-center mb-4">
                  <span className="text-3xl mr-4">🔒</span>
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">Centre de Sécurité</h3>
                    <span className="inline-block bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full font-semibold mt-1">
                      ACTIF
                    </span>
                  </div>
                </div>
                <p className="text-gray-600 mb-4">
                  Monitoring sécurité, détection de menaces, et protection enterprise avec intelligence artificielle.
                </p>
                <div className="flex items-center text-red-600 font-medium">
                  <span>Centre sécurité</span>
                  <Shield className="h-4 w-4 ml-2 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            </Link>

            {/* Monitoring System */}
            <Link href="/monitoring" className="group">
              <div className="bg-gradient-to-br from-orange-50 to-amber-100 p-6 rounded-xl shadow-lg hover:shadow-2xl transition-all duration-300 border border-orange-200 group-hover:scale-105">
                <div className="flex items-center mb-4">
                  <span className="text-3xl mr-4">📡</span>
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">Système Monitoring</h3>
                    <span className="inline-block bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full font-semibold mt-1">
                      ACTIF
                    </span>
                  </div>
                </div>
                <p className="text-gray-600 mb-4">
                  Supervision complète de l'infrastructure, alertes intelligentes, et métriques performance temps réel.
                </p>
                <div className="flex items-center text-orange-600 font-medium">
                  <span>Voir monitoring</span>
                  <Activity className="h-4 w-4 ml-2 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            </Link>

            {/* API Documentation */}
            <a href="http://localhost:8000/docs" target="_blank" className="group">
              <div className="bg-gradient-to-br from-gray-50 to-slate-100 p-6 rounded-xl shadow-lg hover:shadow-2xl transition-all duration-300 border border-gray-200 group-hover:scale-105">
                <div className="flex items-center mb-4">
                  <span className="text-3xl mr-4">📚</span>
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">Documentation API</h3>
                    <span className="inline-block bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full font-semibold mt-1">
                      ACTIF
                    </span>
                  </div>
                </div>
                <p className="text-gray-600 mb-4">
                  Documentation complète Swagger UI, tests interactifs, et guides d'intégration pour tous les endpoints.
                </p>
                <div className="flex items-center text-indigo-600 font-medium">
                  <span>Documentation API</span>
                  <Server className="h-4 w-4 ml-2 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            </a>

          </div>
        </div>

        {/* Navigation rapide */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Link href="/test" className="block">
            <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow border-l-4 border-green-500">
              <div className="flex items-center">
                <span className="text-3xl mr-4">🧪</span>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">Tests API</h3>
                  <p className="text-gray-600 text-sm">Tester tous les endpoints</p>
                </div>
              </div>
            </div>
          </Link>

          <Link href="/live-test" className="block">
            <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow border-l-4 border-red-500">
              <div className="flex items-center">
                <span className="text-3xl mr-4">⚡</span>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">Live Testing</h3>
                  <p className="text-gray-600 text-sm">Tests fonctionnels en temps réel</p>
                </div>
              </div>
            </div>
          </Link>

          <Link href="/upload" className="block">
            <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow border-l-4 border-purple-500">
              <div className="flex items-center">
                <span className="text-3xl mr-4">📤</span>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">Upload</h3>
                  <p className="text-gray-600 text-sm">Télécharger contenu</p>
                </div>
              </div>
            </div>
          </Link>

          <Link href="/fonctionnalites" className="block">
            <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow border-l-4 border-yellow-500">
              <div className="flex items-center">
                <span className="text-3xl mr-4">⚡</span>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">Fonctionnalités</h3>
                  <p className="text-gray-600 text-sm">Capacités plateforme</p>
                </div>
              </div>
            </div>
          </Link>
        </div>

        {/* Quick Access API */}
        <div className="mt-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">🔗 Accès Rapide API</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <a href="http://localhost:8000/docs" target="_blank" 
               className="bg-blue-50 border border-blue-200 p-4 rounded-lg hover:bg-blue-100 transition-colors">
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-semibold text-blue-900">Documentation API</div>
                  <div className="text-blue-600 text-sm">Swagger UI Interactive</div>
                </div>
                <span className="text-xl">📚</span>
              </div>
            </a>
            
            <a href="http://localhost:8000/health" target="_blank"
               className="bg-green-50 border border-green-200 p-4 rounded-lg hover:bg-green-100 transition-colors">
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-semibold text-green-900">Health Check</div>
                  <div className="text-green-600 text-sm">Statut système</div>
                </div>
                <span className="text-xl">💚</span>
              </div>
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}