'use client';

import { useState, useEffect } from 'react';

interface Agent {
  id: number;
  name: string;
  type: string;
  status: string;
}

interface Crawler {
  name: string;
  crawlers: number;
  status: string;
}

export default function LiveTestPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [crawlers, setCrawlers] = useState<Crawler[]>([]);
  const [backendStatus, setBackendStatus] = useState<string>('checking');
  const [actionResult, setActionResult] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    checkBackendAndLoadData();
    // Auto-refresh every 30 seconds
    const interval = setInterval(checkBackendAndLoadData, 30000);
    return () => clearInterval(interval);
  }, []);

  const checkBackendAndLoadData = async () => {
    setLoading(true);
    try {
      // Check backend health via our API route
      const healthResponse = await fetch('/api/backend-health');
      const healthData = await healthResponse.json();
      
      if (healthData.status === 'online') {
        setBackendStatus('✅ Connected & Ready');
        
        // Load agents via API route
        const agentsResponse = await fetch('/api/agents');
        const agentsData = await agentsResponse.json();
        setAgents(agentsData.agents?.slice(0, 12) || []);
        
        // Load crawlers via API route  
        const crawlersResponse = await fetch('/api/crawlers');
        const crawlersData = await crawlersResponse.json();
        setCrawlers(crawlersData.platforms?.slice(0, 8) || []);
        
        setActionResult('✅ Toutes les données chargées - Prêt pour les tests!');
      } else {
        setBackendStatus('❌ Disconnected');
        setActionResult('❌ Backend non accessible');
      }
    } catch (error) {
      setBackendStatus('❌ Connection Error');
      setActionResult(`❌ Erreur de connexion: ${error}`);
      console.error('Error:', error);
    }
    setLoading(false);
  };

  const executeTest = async (testType: string, param?: any) => {
    setLoading(true);
    setActionResult(`🔄 Test en cours: ${testType}...`);
    
    try {
      let response;
      let result;
      
      switch (testType) {
        case 'start-agent':
          response = await fetch('/api/agent-action', { 
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ agentId: param, action: 'start' })
          });
          result = await response.json();
          setActionResult(`✅ Agent ${param} démarré: ${result.message || result.error || 'Success'}`);
          break;
          
        case 'stop-agent':
          response = await fetch('/api/agent-action', { 
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ agentId: param, action: 'stop' })
          });
          result = await response.json();
          setActionResult(`⏹️ Agent ${param} arrêté: ${result.message || result.error || 'Success'}`);
          break;
          
        case 'start-crawler':
          response = await fetch(`http://localhost:8000/crawlers/${param}/start`, { method: 'POST' });
          result = await response.json();
          setActionResult(`🚀 Crawler ${param} démarré: ${result.message || 'Success'}`);
          break;
          
        case 'analytics':
          response = await fetch('/api/analytics');
          result = await response.json();
          setActionResult(`📊 Analytics récupérées:\n${JSON.stringify(result, null, 2)}`);
          break;
          
        case 'revenue':
          response = await fetch('http://localhost:8000/analytics/revenue');
          result = await response.json();
          setActionResult(`💰 Revenue analytics:\n${JSON.stringify(result, null, 2)}`);
          break;
          
        case 'threats':
          response = await fetch('http://localhost:8000/protection/threats');
          result = await response.json();
          setActionResult(`🛡️ Threat protection:\n${JSON.stringify(result, null, 2)}`);
          break;
          
        default:
          setActionResult(`❌ Test inconnu: ${testType}`);
      }
      
      // Refresh data after any action
      await checkBackendAndLoadData();
      
    } catch (error) {
      setActionResult(`❌ Erreur test ${testType}: ${error}`);
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            🧪 Live Testing - Ainflue Enterprise Platform
          </h1>
          <div className="mb-4">
            <span className={`px-6 py-3 rounded-lg text-lg font-medium ${
              backendStatus.includes('✅') 
                ? 'bg-green-100 text-green-800' 
                : 'bg-red-100 text-red-800'
            }`}>
              {backendStatus}
            </span>
          </div>
          <div className="flex justify-center space-x-4">
            <button 
              onClick={checkBackendAndLoadData}
              disabled={loading}
              className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 disabled:opacity-50"
            >
              {loading ? '🔄 Loading...' : '🔄 Refresh All'}
            </button>
            <button 
              onClick={() => window.open('/api/docs', '_blank')}
              className="bg-purple-500 text-white px-6 py-2 rounded-lg hover:bg-purple-600"
            >
              📚 API Docs
            </button>
          </div>
        </div>

        {/* Action Result Display */}
        {actionResult && (
          <div className="mb-6 p-4 bg-white border-l-4 border-blue-500 rounded-r-lg shadow-sm">
            <h3 className="font-semibold text-gray-800 mb-2">🎯 Résultat du Test:</h3>
            <pre className="text-sm text-gray-700 overflow-x-auto whitespace-pre-wrap">{actionResult}</pre>
          </div>
        )}

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
          {/* AI Agents Testing */}
          <div className="bg-white p-6 rounded-xl shadow-lg">
            <h2 className="text-2xl font-semibold mb-6 text-gray-800">
              🤖 AI Agents ({agents.length}/53)
            </h2>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {agents.map((agent) => (
                <div key={agent.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
                  <div className="flex-1">
                    <div className="font-medium text-gray-900">{agent.name}</div>
                    <div className="text-sm text-gray-600">{agent.type}</div>
                    <div className={`text-xs px-2 py-1 rounded-full inline-block mt-1 ${
                      agent.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {agent.status}
                    </div>
                  </div>
                  <div className="flex space-x-2 ml-4">
                    <button 
                      onClick={() => executeTest('start-agent', agent.id)}
                      disabled={loading}
                      className="bg-green-500 text-white px-3 py-2 rounded-md text-sm hover:bg-green-600 disabled:opacity-50"
                    >
                      ▶️ Start
                    </button>
                    <button 
                      onClick={() => executeTest('stop-agent', agent.id)}
                      disabled={loading}
                      className="bg-red-500 text-white px-3 py-2 rounded-md text-sm hover:bg-red-600 disabled:opacity-50"
                    >
                      ⏹️ Stop
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Platform Crawlers Testing */}
          <div className="bg-white p-6 rounded-xl shadow-lg">
            <h2 className="text-2xl font-semibold mb-6 text-gray-800">
              🕷️ Platform Crawlers
            </h2>
            <div className="space-y-3">
              {crawlers.map((crawler) => (
                <div key={crawler.name} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
                  <div className="flex-1">
                    <div className="font-medium text-gray-900">{crawler.name}</div>
                    <div className="text-sm text-gray-600">{crawler.crawlers} crawlers disponibles</div>
                    <div className={`text-xs px-2 py-1 rounded-full inline-block mt-1 ${
                      crawler.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {crawler.status}
                    </div>
                  </div>
                  <button 
                    onClick={() => executeTest('start-crawler', crawler.name)}
                    disabled={loading}
                    className="bg-blue-500 text-white px-4 py-2 rounded-md text-sm hover:bg-blue-600 disabled:opacity-50"
                  >
                    🚀 Start
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Analytics & Monitoring Tests */}
        <div className="mt-8 bg-white p-6 rounded-xl shadow-lg">
          <h2 className="text-2xl font-semibold mb-6 text-gray-800">📊 Analytics & Monitoring Tests</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            <button 
              onClick={() => executeTest('analytics')}
              disabled={loading}
              className="bg-purple-500 text-white p-4 rounded-lg hover:bg-purple-600 disabled:opacity-50 text-center"
            >
              <div className="text-xl mb-1">📈</div>
              <div className="text-sm">Performance</div>
            </button>
            <button 
              onClick={() => executeTest('revenue')}
              disabled={loading}
              className="bg-green-500 text-white p-4 rounded-lg hover:bg-green-600 disabled:opacity-50 text-center"
            >
              <div className="text-xl mb-1">💰</div>
              <div className="text-sm">Revenue</div>
            </button>
            <button 
              onClick={() => executeTest('threats')}
              disabled={loading}
              className="bg-red-500 text-white p-4 rounded-lg hover:bg-red-600 disabled:opacity-50 text-center"
            >
              <div className="text-xl mb-1">🛡️</div>
              <div className="text-sm">Security</div>
            </button>
            <button 
              onClick={() => window.open('/api/backend-health', '_blank')}
              className="bg-blue-500 text-white p-4 rounded-lg hover:bg-blue-600 text-center"
            >
              <div className="text-xl mb-1">💚</div>
              <div className="text-sm">Health</div>
            </button>
            <button 
              onClick={() => window.open('http://localhost:8000/', '_blank')}
              className="bg-indigo-500 text-white p-4 rounded-lg hover:bg-indigo-600 text-center"
            >
              <div className="text-xl mb-1">🏠</div>
              <div className="text-sm">API Root</div>
            </button>
            <button 
              onClick={checkBackendAndLoadData}
              disabled={loading}
              className="bg-yellow-500 text-white p-4 rounded-lg hover:bg-yellow-600 disabled:opacity-50 text-center"
            >
              <div className="text-xl mb-1">🔄</div>
              <div className="text-sm">Refresh</div>
            </button>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="mt-8 grid grid-cols-2 md:grid-cols-4 gap-6">
          <div className="bg-gradient-to-r from-blue-500 to-blue-600 text-white p-6 rounded-xl text-center">
            <div className="text-3xl font-bold">{agents.length}</div>
            <div className="text-blue-100">Agents Loaded</div>
          </div>
          <div className="bg-gradient-to-r from-green-500 to-green-600 text-white p-6 rounded-xl text-center">
            <div className="text-3xl font-bold">{crawlers.reduce((sum, c) => sum + c.crawlers, 0)}</div>
            <div className="text-green-100">Total Crawlers</div>
          </div>
          <div className="bg-gradient-to-r from-purple-500 to-purple-600 text-white p-6 rounded-xl text-center">
            <div className="text-3xl font-bold">8</div>
            <div className="text-purple-100">Enterprise Modules</div>
          </div>
          <div className="bg-gradient-to-r from-orange-500 to-orange-600 text-white p-6 rounded-xl text-center">
            <div className="text-3xl font-bold">100%</div>
            <div className="text-orange-100">Ready to Test</div>
          </div>
        </div>
      </div>
    </div>
  );
}