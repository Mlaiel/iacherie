'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';

export default function HomePage() {
  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking');

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const response = await fetch('http://localhost:8000/health');
        if (response.ok) {
          setBackendStatus('online');
        } else {
          setBackendStatus('offline');
        }
      } catch (error) {
        setBackendStatus('offline');
      }
    };

    checkBackend();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            🚀 Ainflue Enterprise Platform
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            AI-Powered Content Protection & Monetization Platform
          </p>
          
          {/* Backend Status */}
          <div className="inline-flex items-center px-4 py-2 rounded-full text-sm font-medium mb-8">
            {backendStatus === 'checking' && (
              <span className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full">
                🔍 Vérification du backend...
              </span>
            )}
            {backendStatus === 'online' && (
              <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full">
                ✅ Backend connecté (localhost:8000)
              </span>
            )}
            {backendStatus === 'offline' && (
              <span className="bg-red-100 text-red-800 px-3 py-1 rounded-full">
                ❌ Backend déconnecté
              </span>
            )}
          </div>
        </div>

        {/* Navigation Cards */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
          <Link href="/test" className="group">
            <div className="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300 border border-gray-200 group-hover:border-blue-300">
              <div className="text-3xl mb-4">🧪</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Tests Intégration</h3>
              <p className="text-gray-600">Tester la connexion backend et les API</p>
            </div>
          </Link>

          <Link href="/dashboard" className="group">
            <div className="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300 border border-gray-200 group-hover:border-blue-300">
              <div className="text-3xl mb-4">📊</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Dashboard Admin</h3>
              <p className="text-gray-600">Monitoring des 53 agents IA et 117 crawlers</p>
            </div>
          </Link>

          <Link href="/fonctionnalites" className="group">
            <div className="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300 border border-gray-200 group-hover:border-blue-300">
              <div className="text-3xl mb-4">⚡</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Fonctionnalités</h3>
              <p className="text-gray-600">Découvrir les capacités de la plateforme</p>
            </div>
          </Link>

          <Link href="/upload" className="group">
            <div className="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300 border border-gray-200 group-hover:border-blue-300">
              <div className="text-3xl mb-4">📤</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Upload Content</h3>
              <p className="text-gray-600">Télécharger et protéger votre contenu</p>
            </div>
          </Link>

          <Link href="/realtime" className="group">
            <div className="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300 border border-gray-200 group-hover:border-blue-300">
              <div className="text-3xl mb-4">⚡</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Temps Réel</h3>
              <p className="text-gray-600">Monitoring en temps réel</p>
            </div>
          </Link>

          <Link href="/gamification" className="group">
            <div className="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300 border border-gray-200 group-hover:border-blue-300">
              <div className="text-3xl mb-4">🎮</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Gamification</h3>
              <p className="text-gray-600">Système de récompenses et achievements</p>
            </div>
          </Link>
        </div>

        {/* Enterprise Features */}
        <div className="mt-16 text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-8">🏭 Modules Enterprise</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4 max-w-4xl mx-auto">
            <div className="bg-white p-4 rounded-lg shadow border border-gray-200">
              <div className="text-2xl mb-2">🔐</div>
              <div className="font-semibold">Sécurité</div>
              <div className="text-sm text-gray-600">AES-256-GCM, GDPR</div>
            </div>
            <div className="bg-white p-4 rounded-lg shadow border border-gray-200">
              <div className="text-2xl mb-2">🎯</div>
              <div className="font-semibold">Microservices</div>
              <div className="text-sm text-gray-600">mTLS, Service Mesh</div>
            </div>
            <div className="bg-white p-4 rounded-lg shadow border border-gray-200">
              <div className="text-2xl mb-2">🤖</div>
              <div className="font-semibold">AI/ML Pipeline</div>
              <div className="text-sm text-gray-600">53 Agents IA</div>
            </div>
            <div className="bg-white p-4 rounded-lg shadow border border-gray-200">
              <div className="text-2xl mb-2">🚀</div>
              <div className="font-semibold">DevOps Auto</div>
              <div className="text-sm text-gray-600">CI/CD, K8s</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
