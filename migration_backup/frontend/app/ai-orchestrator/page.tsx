'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';

interface AIAgent {
  id: string;
  name: string;
  category: string;
  description: string;
  status?: 'active' | 'idle' | 'error';
}

interface AgentCategories {
  [key: string]: string[];
}

export default function AIAgentsPage() {
  const [agents, setAgents] = useState<AIAgent[]>([]);
  const [categories, setCategories] = useState<AgentCategories>({});
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        setLoading(true);
        
        // Récupérer tous les agents depuis le vrai backend
        const response = await fetch('http://localhost:8000/ai-agents');
        if (response.ok) {
          const data = await response.json();
          setAgents(data.agents || []);
        }

        // Récupérer les catégories depuis /ai-agents
        const categoriesResponse = await fetch('http://localhost:8000/ai-agents');
        if (categoriesResponse.ok) {
          const categoriesData = await categoriesResponse.json();
          if (categoriesData.categories) {
            setCategories(categoriesData.categories);
          }
        }

      } catch (err) {
        setError('Erreur de connexion au backend');
        console.error('Erreur:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchAgents();
    
    // Actualiser toutes les 5 secondes
    const interval = setInterval(fetchAgents, 5000);
    return () => clearInterval(interval);
  }, []);

  const runAgent = async (agentId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/ai-agents/${agentId}/run`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({})
      });
      
      if (response.ok) {
        alert(`Agent ${agentId} démarré avec succès !`);
      } else {
        alert(`Erreur lors du démarrage de l'agent ${agentId}`);
      }
    } catch (error) {
      alert(`Erreur de connexion : ${error}`);
    }
  };

  const filteredAgents = selectedCategory === 'all' 
    ? agents 
    : agents.filter(agent => agent.category === selectedCategory);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-xl text-gray-600">Chargement des agents IA...</p>
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
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                🤖 AI Agents Orchestrator
              </h1>
              <p className="text-gray-600 mt-1">
                53+ agents IA spécialisés en temps réel
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <Link href="/real-platform" 
                    className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                ← Retour au Dashboard
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        
        {/* Stats rapides */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="text-2xl font-bold text-blue-600">{agents.length}</div>
            <div className="text-gray-600 text-sm">Agents Disponibles</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="text-2xl font-bold text-green-600">
              {agents.filter(a => a.status === 'active').length}
            </div>
            <div className="text-gray-600 text-sm">Agents Actifs</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="text-2xl font-bold text-orange-600">{Object.keys(categories).length}</div>
            <div className="text-gray-600 text-sm">Catégories</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="text-2xl font-bold text-purple-600">100%</div>
            <div className="text-gray-600 text-sm">Disponibilité</div>
          </div>
        </div>

        {/* Filtres par catégorie */}
        <div className="mb-8">
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setSelectedCategory('all')}
              className={`px-4 py-2 rounded-lg font-medium ${
                selectedCategory === 'all'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 border hover:bg-gray-50'
              }`}
            >
              Tous ({agents.length})
            </button>
            {Object.entries(categories).map(([category, agents]) => (
              <button
                key={category}
                onClick={() => setSelectedCategory(category)}
                className={`px-4 py-2 rounded-lg font-medium capitalize ${
                  selectedCategory === category
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-700 border hover:bg-gray-50'
                }`}
              >
                {category} ({agents.length})
              </button>
            ))}
          </div>
        </div>

        {/* Liste des agents */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredAgents.map((agent) => (
            <div key={agent.id} className="bg-white p-6 rounded-lg shadow-sm border hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center">
                  <div className="text-2xl mr-3">
                    {agent.category === 'analysis' ? '🔍' :
                     agent.category === 'security' ? '🛡️' :
                     agent.category === 'processing' ? '⚙️' :
                     agent.category === 'utility' ? '🔧' :
                     agent.category === 'content' ? '📝' :
                     agent.category === 'business' ? '💼' : '🤖'}
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{agent.name}</h3>
                    <span className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded capitalize">
                      {agent.category}
                    </span>
                  </div>
                </div>
                <div className={`w-3 h-3 rounded-full ${
                  agent.status === 'active' ? 'bg-green-400' :
                  agent.status === 'error' ? 'bg-red-400' : 'bg-gray-400'
                }`}></div>
              </div>
              
              <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                {agent.description}
              </p>
              
              <div className="flex space-x-2">
                <button
                  onClick={() => runAgent(agent.id)}
                  className="flex-1 bg-blue-600 text-white px-3 py-2 rounded text-sm hover:bg-blue-700"
                >
                  Démarrer
                </button>
                <button className="px-3 py-2 text-gray-600 border rounded text-sm hover:bg-gray-50">
                  Info
                </button>
              </div>
            </div>
          ))}
        </div>

        {filteredAgents.length === 0 && (
          <div className="text-center py-12">
            <div className="text-gray-400 text-6xl mb-4">🤖</div>
            <p className="text-gray-600">Aucun agent trouvé dans cette catégorie</p>
          </div>
        )}

        {/* Catégories détaillées depuis le backend */}
        {Object.keys(categories).length > 0 && (
          <div className="mt-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">📋 Catégories Backend</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {Object.entries(categories).map(([category, agentNames]) => (
                <div key={category} className="bg-white p-4 rounded-lg shadow-sm border">
                  <h3 className="font-semibold text-gray-900 mb-3 capitalize flex items-center">
                    <span className="text-lg mr-2">
                      {category === 'content' ? '📝' :
                       category === 'security' ? '🛡️' :
                       category === 'business' ? '💼' :
                       category === 'technical' ? '⚙️' : '🔧'}
                    </span>
                    {category}
                  </h3>
                  <div className="space-y-1">
                    {agentNames.map((agentName: string, idx: number) => (
                      <div key={idx} className="text-sm text-blue-600 bg-blue-50 px-2 py-1 rounded">
                        {agentName}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}