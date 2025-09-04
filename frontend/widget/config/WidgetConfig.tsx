/**
 * Widget Configuration - Settings and Management
 * 
 * Provides configuration interface for widget settings
 * Manages API keys, permissions, and widget preferences
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

'use client';

import React, { useState } from 'react';
import { 
  KeyIcon,
  ShieldCheckIcon,
  CogIcon,
  DocumentDuplicateIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

export function WidgetConfig() {
  const [apiKey, setApiKey] = useState('');
  const [settings, setSettings] = useState({
    allowedDomains: [''],
    maxRequests: 1000,
    cacheTime: 300,
    enableAnalytics: true,
    enableProtection: true,
    enableContent: true
  });

  const [activeTab, setActiveTab] = useState<'api' | 'permissions' | 'settings'>('api');

  const generateApiKey = () => {
    const newKey = 'ak_' + Math.random().toString(36).substr(2, 32);
    setApiKey(newKey);
  };

  const addDomain = () => {
    setSettings(prev => ({
      ...prev,
      allowedDomains: [...prev.allowedDomains, '']
    }));
  };

  const updateDomain = (index: number, value: string) => {
    setSettings(prev => ({
      ...prev,
      allowedDomains: prev.allowedDomains.map((domain, i) => i === index ? value : domain)
    }));
  };

  const removeDomain = (index: number) => {
    setSettings(prev => ({
      ...prev,
      allowedDomains: prev.allowedDomains.filter((_, i) => i !== index)
    }));
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-6">
          <h2 className="text-2xl font-bold mb-2">Configuration des Widgets</h2>
          <p className="text-purple-100">
            Gérez vos clés API et paramètres de sécurité
          </p>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200">
          <nav className="flex">
            <button
              onClick={() => setActiveTab('api')}
              className={`flex items-center space-x-2 px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'api'
                  ? 'border-purple-500 text-purple-600 bg-purple-50'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <KeyIcon className="h-4 w-4" />
              <span>Clés API</span>
            </button>
            
            <button
              onClick={() => setActiveTab('permissions')}
              className={`flex items-center space-x-2 px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'permissions'
                  ? 'border-purple-500 text-purple-600 bg-purple-50'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <ShieldCheckIcon className="h-4 w-4" />
              <span>Permissions</span>
            </button>
            
            <button
              onClick={() => setActiveTab('settings')}
              className={`flex items-center space-x-2 px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'settings'
                  ? 'border-purple-500 text-purple-600 bg-purple-50'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <CogIcon className="h-4 w-4" />
              <span>Paramètres</span>
            </button>
          </nav>
        </div>

        {/* Content */}
        <div className="p-6">
          {activeTab === 'api' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Gestion des Clés API</h3>
                
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
                  <div className="flex items-start space-x-3">
                    <ExclamationTriangleIcon className="h-5 w-5 text-yellow-600 mt-0.5" />
                    <div>
                      <h4 className="text-sm font-medium text-yellow-800">Important</h4>
                      <p className="text-sm text-yellow-700 mt-1">
                        Gardez vos clés API secrètes. Ne les partagez jamais publiquement ou dans votre code front-end.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Clé API Principale
                    </label>
                    <div className="flex space-x-2">
                      <input
                        type="text"
                        value={apiKey}
                        onChange={(e) => setApiKey(e.target.value)}
                        placeholder="Votre clé API sera affichée ici"
                        className="flex-1 border border-gray-300 rounded-md px-3 py-2 bg-gray-50 font-mono text-sm"
                        readOnly
                      />
                      <button
                        onClick={generateApiKey}
                        className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors"
                      >
                        Générer
                      </button>
                    </div>
                  </div>

                  {apiKey && (
                    <div className="flex items-center space-x-2 text-sm text-gray-600">
                      <DocumentDuplicateIcon className="h-4 w-4" />
                      <span>Clé générée avec succès. Copiez-la et conservez-la en sécurité.</span>
                    </div>
                  )}
                </div>

                <div className="mt-8">
                  <h4 className="font-medium text-gray-900 mb-4">Statistiques d'utilisation</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-gray-50 rounded-lg p-4">
                      <div className="text-2xl font-bold text-gray-900">0</div>
                      <div className="text-sm text-gray-600">Requêtes aujourd'hui</div>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <div className="text-2xl font-bold text-gray-900">0</div>
                      <div className="text-sm text-gray-600">Widgets actifs</div>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <div className="text-2xl font-bold text-gray-900">∞</div>
                      <div className="text-sm text-gray-600">Limite mensuelle</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'permissions' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Domaines Autorisés</h3>
                <p className="text-sm text-gray-600 mb-4">
                  Spécifiez les domaines autorisés à utiliser vos widgets. Laissez vide pour autoriser tous les domaines.
                </p>

                <div className="space-y-3">
                  {settings.allowedDomains.map((domain, index) => (
                    <div key={index} className="flex space-x-2">
                      <input
                        type="text"
                        value={domain}
                        onChange={(e) => updateDomain(index, e.target.value)}
                        placeholder="exemple.com"
                        className="flex-1 border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                      />
                      {settings.allowedDomains.length > 1 && (
                        <button
                          onClick={() => removeDomain(index)}
                          className="px-3 py-2 text-red-600 hover:text-red-800 transition-colors"
                        >
                          Supprimer
                        </button>
                      )}
                    </div>
                  ))}
                  
                  <button
                    onClick={addDomain}
                    className="text-purple-600 hover:text-purple-800 text-sm font-medium"
                  >
                    + Ajouter un domaine
                  </button>
                </div>
              </div>

              <div>
                <h4 className="font-medium text-gray-900 mb-4">Types de Widgets Autorisés</h4>
                <div className="space-y-3">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={settings.enableAnalytics}
                      onChange={(e) => setSettings(prev => ({ ...prev, enableAnalytics: e.target.checked }))}
                      className="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">Widget Analytics</span>
                  </label>
                  
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={settings.enableProtection}
                      onChange={(e) => setSettings(prev => ({ ...prev, enableProtection: e.target.checked }))}
                      className="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">Widget Protection</span>
                  </label>
                  
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={settings.enableContent}
                      onChange={(e) => setSettings(prev => ({ ...prev, enableContent: e.target.checked }))}
                      className="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">Widget Contenu</span>
                  </label>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'settings' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Paramètres Avancés</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Limite de requêtes par heure
                    </label>
                    <input
                      type="number"
                      value={settings.maxRequests}
                      onChange={(e) => setSettings(prev => ({ ...prev, maxRequests: parseInt(e.target.value) }))}
                      className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      0 = illimité
                    </p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Durée de cache (secondes)
                    </label>
                    <input
                      type="number"
                      value={settings.cacheTime}
                      onChange={(e) => setSettings(prev => ({ ...prev, cacheTime: parseInt(e.target.value) }))}
                      className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Temps de mise en cache des données
                    </p>
                  </div>
                </div>
              </div>

              <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
                <button className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition-colors">
                  Annuler
                </button>
                <button className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors">
                  Enregistrer
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}