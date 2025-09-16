'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';

export default function HomePage() {
  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking');

  useEffect(() => {
    const checkBackend = async () => {
      try {
        // Utilise l'API route Next.js au lieu d'appeler directement le backend
        const response = await fetch('/api/backend-health');
        const data = await response.json();
        
        if (response.ok && data.status === 'online') {
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
    // Vérifie toutes les 30 secondes
    const interval = setInterval(checkBackend, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            🚀 Ainflue Enterprise Platform
          </h1>
          <p className="text-xl text-gray-600 mb-6">
            AI-Powered Content Protection & Monetization
          </p>
          
          {/* Backend Status */}
          <div className="inline-block">
            {backendStatus === 'checking' && (
              <span className="bg-yellow-100 text-yellow-800 px-4 py-2 rounded-lg text-base font-medium">
                � Vérification du backend...
              </span>
            )}
            {backendStatus === 'online' && (
              <span className="bg-green-100 text-green-800 px-4 py-2 rounded-lg text-base font-medium">
                ✅ Backend connecté (localhost:8000)
              </span>
            )}
            {backendStatus === 'offline' && (
              <span className="bg-red-100 text-red-800 px-4 py-2 rounded-lg text-base font-medium">
                ❌ Backend déconnecté
              </span>
            )}
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
          <div className="bg-white p-6 rounded-lg shadow-md text-center">
            <div className="text-2xl mb-2">🤖</div>
            <div className="text-2xl font-bold text-blue-600">53</div>
            <div className="text-gray-600">Agents IA</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md text-center">
            <div className="text-2xl mb-2">🕷️</div>
            <div className="text-2xl font-bold text-green-600">117</div>
            <div className="text-gray-600">Crawlers</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md text-center">
            <div className="text-2xl mb-2">🛡️</div>
            <div className="text-2xl font-bold text-purple-600">7</div>
            <div className="text-gray-600">Modules Enterprise</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md text-center">
            <div className="text-2xl mb-2">📊</div>
            <div className="text-2xl font-bold text-orange-600">100%</div>
            <div className="text-gray-600">Opérationnel</div>
          </div>
        </div>

        {/* Navigation Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Link href="/test" className="block">
            <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow border-l-4 border-blue-500">
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

          <Link href="/dashboard" className="block">
            <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow border-l-4 border-green-500">
              <div className="flex items-center">
                <span className="text-3xl mr-4">📊</span>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">Dashboard</h3>
                  <p className="text-gray-600 text-sm">Monitoring et analytics</p>
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

          <Link href="/realtime" className="block">
            <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow border-l-4 border-red-500">
              <div className="flex items-center">
                <span className="text-3xl mr-4">⚡</span>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">Temps Réel</h3>
                  <p className="text-gray-600 text-sm">Monitoring live</p>
                </div>
              </div>
            </div>
          </Link>

          <Link href="/gamification" className="block">
            <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow border-l-4 border-indigo-500">
              <div className="flex items-center">
                <span className="text-3xl mr-4">🎮</span>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">Gamification</h3>
                  <p className="text-gray-600 text-sm">Système récompenses</p>
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
