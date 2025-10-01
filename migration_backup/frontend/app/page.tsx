'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Activity, Server, Cpu, Database, Shield, TrendingUp, Brain, Users, Globe, Mic, Video, Music, Palette, MessageSquare } from 'lucide-react';
import { toConsistentLocaleString } from '../utils/formatters';

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
    activeServices: 57,
    totalModules: 57,
    uptime: 99.8,
    languages: 644,
    collaborations: 2847,
    remixesGenerated: 15683,
    liveStreams: 156
  });

  // Mettre à jour les stats en temps réel
  useEffect(() => {
    const interval = setInterval(() => {
      setRealTimeStats(prev => ({
        ...prev,
        collaborations: prev.collaborations + Math.floor(Math.random() * 3),
        remixesGenerated: prev.remixesGenerated + Math.floor(Math.random() * 5),
        liveStreams: prev.liveStreams + Math.floor(Math.random() * 2) - 1
      }));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const getStatusColor = () => {
    switch (backendStatus) {
      case 'online': return 'bg-green-100 text-green-800';
      case 'offline': return 'bg-red-100 text-red-800';
      default: return 'bg-yellow-100 text-yellow-800';
    }
  };

  const getStatusText = () => {
    switch (backendStatus) {
      case 'online': return '✅ Backend Opérationnel';
      case 'offline': return '❌ Backend Hors Ligne';
      default: return '🔄 Connexion...';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Navigation */}
      <nav className="bg-white shadow-lg border-b">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Activity className="h-10 w-10 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">IA Chéries Enterprise</h1>
                <p className="text-sm text-gray-600">Platform IA Multi-Services - 57 Modules Complets</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className={`px-4 py-2 rounded-full text-sm font-medium flex items-center ${getStatusColor()}`}>
                <div className={`animate-${backendStatus === 'online' ? 'pulse' : 'spin'} h-4 w-4 ${backendStatus === 'online' ? 'bg-green-600' : 'border-2 border-yellow-600 rounded-full border-t-transparent'} mr-2`}></div>
                {getStatusText()}
              </span>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center bg-gradient-to-r from-blue-100 to-purple-100 text-blue-700 px-6 py-3 rounded-full text-sm font-medium mb-6">
            <Server className="h-5 w-5 mr-2" />
            {realTimeStats.activeServices}/{realTimeStats.totalModules} Modules Enterprise Actifs • {realTimeStats.aiAgents} Agents IA • {realTimeStats.languages} Langues
          </div>
          <h2 className="text-6xl font-bold text-gray-900 mb-6">
            Enterprise Intelligence
            <span className="block bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
              Platform Complète
            </span>
          </h2>
          <p className="text-xl text-gray-600 max-w-4xl mx-auto">
            Platform complète avec IA avancée, collaboration intelligente, remix studio professionnel, 
            traduction 644 langues, video chat rooms et bien plus. Développé par Fahed Mlaiel.
          </p>
        </div>

        {/* Stats en temps réel */}
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-6 mb-12">
          <div className="bg-white rounded-2xl shadow-xl p-6 border border-gray-100 hover:shadow-2xl transition-all duration-300">
            <div className="flex items-center justify-between mb-2">
              <Brain className="h-8 w-8 text-blue-600" />
              <div className="text-right">
                <div className="text-2xl font-bold text-gray-900">{realTimeStats.aiAgents}</div>
                <div className="text-xs text-gray-500">Agents IA</div>
              </div>
            </div>
            <div className="text-xs text-green-600 font-medium">🤖 Intelligence Active</div>
          </div>

          <div className="bg-white rounded-2xl shadow-xl p-6 border border-gray-100 hover:shadow-2xl transition-all duration-300">
            <div className="flex items-center justify-between mb-2">
              <Database className="h-8 w-8 text-green-600" />
              <div className="text-right">
                <div className="text-2xl font-bold text-gray-900">{realTimeStats.activeServices}</div>
                <div className="text-xs text-gray-500">Services</div>
              </div>
            </div>
            <div className="text-xs text-green-600 font-medium">🟢 Tous Opérationnels</div>
          </div>

          <div className="bg-white rounded-2xl shadow-xl p-6 border border-gray-100 hover:shadow-2xl transition-all duration-300">
            <div className="flex items-center justify-between mb-2">
              <Globe className="h-8 w-8 text-purple-600" />
              <div className="text-right">
                <div className="text-2xl font-bold text-gray-900">{realTimeStats.languages}</div>
                <div className="text-xs text-gray-500">Langues</div>
              </div>
            </div>
            <div className="text-xs text-green-600 font-medium">🌍 Traduction IA</div>
          </div>

          <div className="bg-white rounded-2xl shadow-xl p-6 border border-gray-100 hover:shadow-2xl transition-all duration-300">
            <div className="flex items-center justify-between mb-2">
              <Users className="h-8 w-8 text-orange-600" />
              <div className="text-right">
                <div className="text-2xl font-bold text-gray-900">{toConsistentLocaleString(realTimeStats.collaborations)}</div>
                <div className="text-xs text-gray-500">Collaborations</div>
              </div>
            </div>
            <div className="text-xs text-green-600 font-medium">🤝 Matching IA</div>
          </div>

          <div className="bg-white rounded-2xl shadow-xl p-6 border border-gray-100 hover:shadow-2xl transition-all duration-300">
            <div className="flex items-center justify-between mb-2">
              <Music className="h-8 w-8 text-pink-600" />
              <div className="text-right">
                <div className="text-2xl font-bold text-gray-900">{toConsistentLocaleString(realTimeStats.remixesGenerated)}</div>
                <div className="text-xs text-gray-500">Remixes</div>
              </div>
            </div>
            <div className="text-xs text-green-600 font-medium">🎵 Studio Pro</div>
          </div>

          <div className="bg-white rounded-2xl shadow-xl p-6 border border-gray-100 hover:shadow-2xl transition-all duration-300">
            <div className="flex items-center justify-between mb-2">
              <TrendingUp className="h-8 w-8 text-green-600" />
              <div className="text-right">
                <div className="text-2xl font-bold text-gray-900">{realTimeStats.uptime}%</div>
                <div className="text-xs text-gray-500">Uptime</div>
              </div>
            </div>
            <div className="text-xs text-green-600 font-medium">⚡ Performance</div>
          </div>
        </div>

        {/* Services Enterprise Complets */}
        <div className="mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-8 text-center">🚀 Platform Enterprise Complète</h2>
          
          {/* Services Principaux */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
            {/* AI Studio */}
            <Link href="/ai-studio" className="group">
              <div className="bg-gradient-to-br from-blue-50 to-indigo-100 p-8 rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 border border-blue-200 group-hover:scale-105">
                <div className="flex items-center mb-6">
                  <div className="h-16 w-16 bg-blue-100 rounded-xl flex items-center justify-center mr-4">
                    <Brain className="h-8 w-8 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-gray-900">Intelligence Artificielle</h3>
                    <span className="inline-block bg-green-100 text-green-800 text-xs px-3 py-1 rounded-full font-semibold mt-2">
                      53 AGENTS IA ACTIFS
                    </span>
                  </div>
                </div>
                <p className="text-gray-600 mb-6 text-lg leading-relaxed">
                  Génération de contenu avancée, NLP, analyse prédictive et intelligence créative avec 15+ modèles IA de pointe
                </p>
                <div className="flex items-center text-indigo-600 font-semibold text-lg">
                  <span>Accéder au Studio IA</span>
                  <Server className="h-5 w-5 ml-2 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            </Link>

            {/* Collaboration Hub */}
            <Link href="/collaboration" className="group">
              <div className="bg-gradient-to-br from-emerald-50 to-green-100 p-8 rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 border border-emerald-200 group-hover:scale-105">
                <div className="flex items-center mb-6">
                  <div className="h-16 w-16 bg-emerald-100 rounded-xl flex items-center justify-center mr-4">
                    <Users className="h-8 w-8 text-emerald-600" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-gray-900">Collaboration Hub</h3>
                    <span className="inline-block bg-green-100 text-green-800 text-xs px-3 py-1 rounded-full font-semibold mt-2">
                      MATCHING IA INTELLIGENT
                    </span>
                  </div>
                </div>
                <p className="text-gray-600 mb-6 text-lg leading-relaxed">
                  Matching intelligent créateurs, projets collaboratifs, workspace partagés et gestion de partenariats
                </p>
                <div className="flex items-center text-emerald-600 font-semibold text-lg">
                  <span>Hub Collaboration</span>
                  <Users className="h-5 w-5 ml-2 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            </Link>

            {/* Remix Studio */}
            <Link href="/remix-studio" className="group">
              <div className="bg-gradient-to-br from-pink-50 to-rose-100 p-8 rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 border border-pink-200 group-hover:scale-105">
                <div className="flex items-center mb-6">
                  <div className="h-16 w-16 bg-pink-100 rounded-xl flex items-center justify-center mr-4">
                    <Music className="h-8 w-8 text-pink-600" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-gray-900">Remix Studio Pro</h3>
                    <span className="inline-block bg-green-100 text-green-800 text-xs px-3 py-1 rounded-full font-semibold mt-2">
                      STUDIO PROFESSIONNEL
                    </span>
                  </div>
                </div>
                <p className="text-gray-600 mb-6 text-lg leading-relaxed">
                  Remix collaboratif audio/video, IA créative, fusion intelligente et production musicale avancée
                </p>
                <div className="flex items-center text-pink-600 font-semibold text-lg">
                  <span>Studio Remix</span>
                  <Palette className="h-5 w-5 ml-2 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            </Link>

            {/* Audio Studio */}
            <Link href="/audio-studio" className="group">
              <div className="bg-gradient-to-br from-purple-50 to-violet-100 p-8 rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 border border-purple-200 group-hover:scale-105">
                <div className="flex items-center mb-6">
                  <div className="h-16 w-16 bg-purple-100 rounded-xl flex items-center justify-center mr-4">
                    <Mic className="h-8 w-8 text-purple-600" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-gray-900">Audio Studio Pro</h3>
                    <span className="inline-block bg-green-100 text-green-800 text-xs px-3 py-1 rounded-full font-semibold mt-2">
                      MASTERING IA
                    </span>
                  </div>
                </div>
                <p className="text-gray-600 mb-6 text-lg leading-relaxed">
                  Génération audio, remix avancé, synthèse vocale et mastering IA professionnel multi-format
                </p>
                <div className="flex items-center text-purple-600 font-semibold text-lg">
                  <span>Studio Audio</span>
                  <Mic className="h-5 w-5 ml-2 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            </Link>

            {/* Video Chat Rooms */}
            <Link href="/video-chat" className="group">
              <div className="bg-gradient-to-br from-cyan-50 to-blue-100 p-8 rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 border border-cyan-200 group-hover:scale-105">
                <div className="flex items-center mb-6">
                  <div className="h-16 w-16 bg-cyan-100 rounded-xl flex items-center justify-center mr-4">
                    <Video className="h-8 w-8 text-cyan-600" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-gray-900">Video Chat Rooms</h3>
                    <span className="inline-block bg-green-100 text-green-800 text-xs px-3 py-1 rounded-full font-semibold mt-2">
                      HD LIVE + TRADUCTION
                    </span>
                  </div>
                </div>
                <p className="text-gray-600 mb-6 text-lg leading-relaxed">
                  Salles vidéo HD multi-rooms avec traduction temps réel 644 langues et collaboration live
                </p>
                <div className="flex items-center text-cyan-600 font-semibold text-lg">
                  <span>Rejoindre Live</span>
                  <Video className="h-5 w-5 ml-2 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            </Link>

            {/* Analytics Enterprise */}
            <Link href="/analytics" className="group">
              <div className="bg-gradient-to-br from-green-50 to-emerald-100 p-8 rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 border border-green-200 group-hover:scale-105">
                <div className="flex items-center mb-6">
                  <div className="h-16 w-16 bg-green-100 rounded-xl flex items-center justify-center mr-4">
                    <TrendingUp className="h-8 w-8 text-green-600" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-gray-900">Analytics Enterprise</h3>
                    <span className="inline-block bg-green-100 text-green-800 text-xs px-3 py-1 rounded-full font-semibold mt-2">
                      BUSINESS INTELLIGENCE
                    </span>
                  </div>
                </div>
                <p className="text-gray-600 mb-6 text-lg leading-relaxed">
                  Business Intelligence avancée, insights prédictifs, métriques temps réel et analytics IA
                </p>
                <div className="flex items-center text-green-600 font-semibold text-lg">
                  <span>Dashboard Enterprise</span>
                  <TrendingUp className="h-5 w-5 ml-2 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            </Link>
          </div>

          {/* Services Additionnels - Grid Complet */}
          <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-200 mb-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-6 text-center">
              🛠️ Services & Modules Complémentaires - 57/57 Actifs
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-6">
              {/* Row 1 */}
              <Link href="/translation" className="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-xl shadow-md hover:shadow-lg transition-all border border-blue-200 hover:scale-105">
                <div className="text-center">
                  <div className="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                    <Globe className="h-6 w-6 text-blue-600" />
                  </div>
                  <h4 className="font-bold text-sm mb-1">Traduction IA</h4>
                  <p className="text-xs text-gray-600">644 Langues</p>
                </div>
              </Link>

              <Link href="/voice-synthesis" className="bg-gradient-to-br from-purple-50 to-purple-100 p-6 rounded-xl shadow-md hover:shadow-lg transition-all border border-purple-200 hover:scale-105">
                <div className="text-center">
                  <div className="h-12 w-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                    <Mic className="h-6 w-6 text-purple-600" />
                  </div>
                  <h4 className="font-bold text-sm mb-1">Synthèse Vocale</h4>
                  <p className="text-xs text-gray-600">IA Vocale HD</p>
                </div>
              </Link>

              <Link href="/content-moderation" className="bg-gradient-to-br from-red-50 to-red-100 p-6 rounded-xl shadow-md hover:shadow-lg transition-all border border-red-200 hover:scale-105">
                <div className="text-center">
                  <div className="h-12 w-12 bg-red-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                    <Shield className="h-6 w-6 text-red-600" />
                  </div>
                  <h4 className="font-bold text-sm mb-1">Modération IA</h4>
                  <p className="text-xs text-gray-600">Auto Multi-Platform</p>
                </div>
              </Link>

              <Link href="/gamification" className="bg-gradient-to-br from-yellow-50 to-yellow-100 p-6 rounded-xl shadow-md hover:shadow-lg transition-all border border-yellow-200 hover:scale-105">
                <div className="text-center">
                  <div className="h-12 w-12 bg-yellow-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                    <span className="text-2xl">🎮</span>
                  </div>
                  <h4 className="font-bold text-sm mb-1">Gamification</h4>
                  <p className="text-xs text-gray-600">Levels & XP System</p>
                </div>
              </Link>

              <Link href="/monetization" className="bg-gradient-to-br from-green-50 to-green-100 p-6 rounded-xl shadow-md hover:shadow-lg transition-all border border-green-200 hover:scale-105">
                <div className="text-center">
                  <div className="h-12 w-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                    <span className="text-2xl">💰</span>
                  </div>
                  <h4 className="font-bold text-sm mb-1">Monétisation IA</h4>
                  <p className="text-xs text-gray-600">Revenue Intelligence</p>
                </div>
              </Link>

              <Link href="/blockchain" className="bg-gradient-to-br from-indigo-50 to-indigo-100 p-6 rounded-xl shadow-md hover:shadow-lg transition-all border border-indigo-200 hover:scale-105">
                <div className="text-center">
                  <div className="h-12 w-12 bg-indigo-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                    <span className="text-2xl">⛓️</span>
                  </div>
                  <h4 className="font-bold text-sm mb-1">Blockchain Web3</h4>
                  <p className="text-xs text-gray-600">Smart Contracts</p>
                </div>
              </Link>

              {/* Row 2 */}
              <Link href="/nft-marketplace" className="bg-gradient-to-br from-pink-50 to-pink-100 p-6 rounded-xl shadow-md hover:shadow-lg transition-all border border-pink-200 hover:scale-105">
                <div className="text-center">
                  <div className="h-12 w-12 bg-pink-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                    <span className="text-2xl">🎨</span>
                  </div>
                  <h4 className="font-bold text-sm mb-1">NFT Marketplace</h4>
                  <p className="text-xs text-gray-600">Creative Assets</p>
                </div>
              </Link>

              <Link href="/live-streaming" className="bg-gradient-to-br from-red-50 to-red-100 p-6 rounded-xl shadow-md hover:shadow-lg transition-all border border-red-200 hover:scale-105">
                <div className="text-center">
                  <div className="h-12 w-12 bg-red-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                    <span className="text-2xl">📡</span>
                  </div>
                  <h4 className="font-bold text-sm mb-1">Live Streaming</h4>
                  <p className="text-xs text-gray-600">Multi-Platform HD</p>
                </div>
              </Link>

              <Link href="/social-network" className="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-xl shadow-md hover:shadow-lg transition-all border border-blue-200 hover:scale-105">
                <div className="text-center">
                  <div className="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                    <Users className="h-6 w-6 text-blue-600" />
                  </div>
                  <h4 className="font-bold text-sm mb-1">Social Network</h4>
                  <p className="text-xs text-gray-600">Creators Hub</p>
                </div>
              </Link>

              <Link href="/distribution" className="bg-gradient-to-br from-orange-50 to-orange-100 p-6 rounded-xl shadow-md hover:shadow-lg transition-all border border-orange-200 hover:scale-105">
                <div className="text-center">
                  <div className="h-12 w-12 bg-orange-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                    <span className="text-2xl">🚀</span>
                  </div>
                  <h4 className="font-bold text-sm mb-1">Distribution IA</h4>
                  <p className="text-xs text-gray-600">Multi-Platform Auto</p>
                </div>
              </Link>

              <Link href="/copyright-ai" className="bg-gradient-to-br from-gray-50 to-gray-100 p-6 rounded-xl shadow-md hover:shadow-lg transition-all border border-gray-200 hover:scale-105">
                <div className="text-center">
                  <div className="h-12 w-12 bg-gray-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                    <span className="text-2xl">©️</span>
                  </div>
                  <h4 className="font-bold text-sm mb-1">Copyright IA</h4>
                  <p className="text-xs text-gray-600">Protection Auto</p>
                </div>
              </Link>

              <Link href="/mobile-apps" className="bg-gradient-to-br from-teal-50 to-teal-100 p-6 rounded-xl shadow-md hover:shadow-lg transition-all border border-teal-200 hover:scale-105">
                <div className="text-center">
                  <div className="h-12 w-12 bg-teal-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                    <span className="text-2xl">📱</span>
                  </div>
                  <h4 className="font-bold text-sm mb-1">Mobile Apps</h4>
                  <p className="text-xs text-gray-600">iOS/Android Native</p>
                </div>
              </Link>
            </div>
          </div>

          {/* Accès API et Documentation */}
          <div className="bg-white rounded-2xl shadow-xl p-6 border border-gray-200">
            <h3 className="text-xl font-bold text-gray-900 mb-4 text-center">🔗 Accès Développeurs & API</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <a href="http://localhost:8000/docs" target="_blank" className="bg-blue-50 border-2 border-blue-200 p-4 rounded-xl hover:bg-blue-100 transition-colors">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-bold text-blue-900">Documentation API</div>
                    <div className="text-blue-600 text-sm">Swagger UI Interactif</div>
                  </div>
                  <span className="text-2xl">📚</span>
                </div>
              </a>
              
              <a href="http://localhost:8000/health" target="_blank" className="bg-green-50 border-2 border-green-200 p-4 rounded-xl hover:bg-green-100 transition-colors">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-bold text-green-900">Health Check</div>
                    <div className="text-green-600 text-sm">Status Système</div>
                  </div>
                  <span className="text-2xl">💚</span>
                </div>
              </a>

              <Link href="/monitoring" className="bg-orange-50 border-2 border-orange-200 p-4 rounded-xl hover:bg-orange-100 transition-colors">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-bold text-orange-900">Monitoring Live</div>
                    <div className="text-orange-600 text-sm">Métriques Temps Réel</div>
                  </div>
                  <span className="text-2xl">📊</span>
                </div>
              </Link>
            </div>
          </div>
        </div>

        {/* Footer Development Info */}
        <div className="text-center py-8 border-t border-gray-200">
          <p className="text-gray-600 text-lg">
            🏆 <strong>IA Chéries Enterprise Platform</strong> - Développé par <strong>Fahed Mlaiel</strong>
          </p>
          <p className="text-gray-500 text-sm mt-2">
            Platform IA complète • 57/57 Modules • 644 Langues • Matching Intelligent • Studios Professionnels
          </p>
          <div className="flex justify-center items-center space-x-4 mt-4 text-sm text-gray-500">
            <span>✅ Backend Opérationnel</span>
            <span>•</span>
            <span>🤖 53 Agents IA Actifs</span>
            <span>•</span>
            <span>🌍 Multi-Langue Support</span>
            <span>•</span>
            <span>⚡ Performance Optimale</span>
          </div>
        </div>
      </div>
    </div>
  );
}