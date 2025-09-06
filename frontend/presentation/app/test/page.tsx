'use client';

import { useState, useEffect } from 'react';

interface TestResult {
  status: 'loading' | 'success' | 'error';
  data?: any;
  error?: string;
}

export default function TestPage() {
  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking');
  const [testResults, setTestResults] = useState<Record<string, TestResult>>({});

  const checkBackendStatus = async () => {
    try {
      setBackendStatus('checking');
      const response = await fetch('http://127.0.0.1:8000/health');
      if (response.ok) {
        setBackendStatus('online');
      } else {
        setBackendStatus('offline');
      }
    } catch (error) {
      setBackendStatus('offline');
    }
  };

  const runTest = async (endpoint: string, name: string) => {
    try {
      setTestResults(prev => ({ ...prev, [name]: { status: 'loading' } }));
      const response = await fetch(`http://127.0.0.1:8000${endpoint}`);
      const data = await response.json();
      setTestResults(prev => ({ ...prev, [name]: { status: 'success', data } }));
    } catch (error) {
      setTestResults(prev => ({ ...prev, [name]: { status: 'error', error: error instanceof Error ? error.message : String(error) } }));
    }
  };

  useEffect(() => {
    checkBackendStatus();
  }, []);

  const tests = [
    // Agents IA (53 Agents)
    { name: "Liste Complète des Agents", endpoint: "/api/v1/agents", category: "Agents IA" },
    { name: "Agents d'Analyse", endpoint: "/api/v1/agents/category/analysis", category: "Agents IA" },
    { name: "Agents de Protection", endpoint: "/api/v1/agents/category/protection", category: "Agents IA" },
    { name: "Exécuter Agent d'Analyse", endpoint: "/api/v1/agents/content_analyzer/run", category: "Agents IA" },
    { name: "Détection Copyright", endpoint: "/api/v1/agents/copyright_detector/run", category: "Agents IA" },
    
    // Crawlers (117 Crawlers)
    { name: "Liste des Crawlers", endpoint: "/api/v1/crawlers", category: "Crawlers" },
    { name: "Crawlers YouTube", endpoint: "/api/v1/crawlers/platform/youtube", category: "Crawlers" },
    { name: "Crawlers Instagram", endpoint: "/api/v1/crawlers/platform/instagram", category: "Crawlers" },
    { name: "Crawlers TikTok", endpoint: "/api/v1/crawlers/platform/tiktok", category: "Crawlers" },
    { name: "Crawlers Spotify", endpoint: "/api/v1/crawlers/platform/spotify", category: "Crawlers" },
    { name: "Scan Violations", endpoint: "/api/v1/crawlers/violations/scan", category: "Crawlers" },
    
    // Distribution
    { name: "Distribution YouTube", endpoint: "/api/v1/agents/youtube_distributor/run", category: "Distribution" },
    { name: "Distribution Instagram", endpoint: "/api/v1/agents/instagram_distributor/run", category: "Distribution" },
    { name: "Distribution TikTok", endpoint: "/api/v1/agents/tiktok_distributor/run", category: "Distribution" },
    { name: "Distribution Spotify", endpoint: "/api/v1/agents/spotify_distributor/run", category: "Distribution" },
    
    // Protection
    { name: "Violations Détectées", endpoint: "/api/v1/violations", category: "Protection" },
    { name: "Générer Empreinte", endpoint: "/api/v1/agents/fingerprint_generator/run", category: "Protection" },
    { name: "Takedown Automatique", endpoint: "/api/v1/agents/takedown_agent/run", category: "Protection" },
    
    // Analytics
    { name: "Analytics Revenus", endpoint: "/api/v1/analytics/revenue", category: "Analytics" },
    { name: "Métriques Générales", endpoint: "/api/v1/analytics/metrics", category: "Analytics" },
    { name: "Optimisation Revenus", endpoint: "/api/v1/agents/revenue_optimizer/run", category: "Analytics" },
    
    // Monitoring
    { name: "Statut Système", endpoint: "/api/v1/monitoring/status", category: "Monitoring" },
    { name: "Alertes Système", endpoint: "/api/v1/monitoring/alerts", category: "Monitoring" },
    { name: "Health Check", endpoint: "/health", category: "Monitoring" },
  ];

  const categories = Array.from(new Set(tests.map(t => t.category)));

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">🎵 Ainflue - Plateforme Complète</h1>
          <p className="text-gray-600">53 Agents IA • 117 Crawlers • Distribution Multi-Plateformes • Protection Avancée</p>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">Statut Backend</h2>
              <p className="text-sm text-gray-600">http://127.0.0.1:8000</p>
            </div>
            <div className="flex items-center space-x-3">
              <div className={`w-3 h-3 rounded-full ${
                backendStatus === 'online' ? 'bg-green-500' : 
                backendStatus === 'offline' ? 'bg-red-500' : 'bg-yellow-500'
              }`}></div>
              <span className={`font-medium ${
                backendStatus === 'online' ? 'text-green-600' : 
                backendStatus === 'offline' ? 'text-red-600' : 'text-yellow-600'
              }`}>
                {backendStatus === 'online' ? 'En ligne' : 
                 backendStatus === 'offline' ? 'Hors ligne' : 'Vérification...'}
              </span>
              <button
                onClick={checkBackendStatus}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm"
              >
                Vérifier
              </button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <h3 className="text-lg font-semibold text-blue-600">53 Agents IA</h3>
            <p className="text-sm text-gray-600">Analyse, Protection, Distribution</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <h3 className="text-lg font-semibold text-purple-600">117 Crawlers</h3>
            <p className="text-sm text-gray-600">YouTube, Instagram, TikTok, etc.</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <h3 className="text-lg font-semibold text-green-600">Distribution</h3>
            <p className="text-sm text-gray-600">15 Plateformes sociales</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <h3 className="text-lg font-semibold text-orange-600">Protection IA</h3>
            <p className="text-sm text-gray-600">Anti-piratage avancé</p>
          </div>
        </div>

        <div className="space-y-6">
          {categories.map(category => (
            <div key={category} className="bg-white rounded-lg shadow-sm">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">{category}</h3>
              </div>
              <div className="p-6">
                <div className="grid gap-3">
                  {tests.filter(t => t.category === category).map((test) => {
                    const result = testResults[test.name];
                    return (
                      <div key={test.name} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
                        <div className="flex-1">
                          <h4 className="font-medium text-gray-900">{test.name}</h4>
                          <p className="text-sm text-gray-600">{test.endpoint}</p>
                          {result && result.status === 'success' && (
                            <div className="mt-2">
                              <details className="cursor-pointer">
                                <summary className="text-xs text-blue-600">Voir réponse</summary>
                                <pre className="mt-1 p-2 bg-gray-100 rounded text-xs overflow-auto max-h-32">
                                  {JSON.stringify(result.data, null, 2)}
                                </pre>
                              </details>
                            </div>
                          )}
                          {result && result.status === 'error' && (
                            <p className="mt-1 text-xs text-red-600">Erreur: {result.error}</p>
                          )}
                        </div>
                        <div className="flex items-center space-x-3">
                          {result && (
                            <span className="text-sm">
                              {result.status === 'success' ? '✅' : 
                               result.status === 'error' ? '❌' : '⏳'}
                            </span>
                          )}
                          <button
                            onClick={() => runTest(test.endpoint, test.name)}
                            disabled={backendStatus !== 'online' || (result && result.status === 'loading')}
                            className="px-4 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                          >
                            {result && result.status === 'loading' ? 'Test...' : 'Tester'}
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
