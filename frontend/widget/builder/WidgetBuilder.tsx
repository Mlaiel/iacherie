/**
 * Widget Builder - Interactive Widget Configuration Tool
 * 
 * Allows users to build and customize embeddable widgets
 * Provides live preview and generates embed code
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

'use client';

import React, { useState } from 'react';
import { 
  CogIcon,
  EyeIcon,
  ClipboardDocumentIcon,
  CheckIcon
} from '@heroicons/react/24/outline';
import { EmbeddableWidget } from '../index';

export function WidgetBuilder() {
  const [widgetConfig, setWidgetConfig] = useState({
    type: 'analytics' as 'analytics' | 'protection' | 'content',
    apiKey: '',
    userId: '',
    theme: 'light' as 'light' | 'dark',
    size: 'medium' as 'small' | 'medium' | 'large',
    showTitle: true,
    customColors: {
      primary: '#3b82f6',
      secondary: '#8b5cf6',
      background: '#ffffff',
      text: '#1f2937'
    }
  });

  const [activeTab, setActiveTab] = useState<'config' | 'preview' | 'code'>('config');
  const [copied, setCopied] = useState(false);

  const generateEmbedCode = () => {
    const configString = JSON.stringify({
      ...widgetConfig,
      customColors: widgetConfig.customColors
    }, null, 2);

    return `<!-- Ainflue Widget -->
<div id="ainflue-widget"></div>
<script>
  // Load Ainflue Widget Script
  (function() {
    const script = document.createElement('script');
    script.src = 'https://cdn.ainflue.com/widget.js';
    script.onload = function() {
      AinfluceWidget.render('ainflue-widget', ${configString});
    };
    document.head.appendChild(script);
  })();
</script>`;
  };

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(generateEmbedCode());
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Erreur lors de la copie:', err);
    }
  };

  const handleConfigChange = (key: string, value: any) => {
    setWidgetConfig(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleColorChange = (colorKey: string, value: string) => {
    setWidgetConfig(prev => ({
      ...prev,
      customColors: {
        ...prev.customColors,
        [colorKey]: value
      }
    }));
  };

  const tabs = [
    { id: 'config', label: 'Configuration', icon: CogIcon },
    { id: 'preview', label: 'Aperçu', icon: EyeIcon },
    { id: 'code', label: 'Code d\'intégration', icon: ClipboardDocumentIcon }
  ];

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6">
          <h2 className="text-2xl font-bold mb-2">Constructeur de Widget Ainflue</h2>
          <p className="text-blue-100">
            Créez et personnalisez votre widget embeddable en quelques clics
          </p>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200">
          <nav className="flex">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center space-x-2 px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600 bg-blue-50'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <tab.icon className="h-4 w-4" />
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>

        {/* Content */}
        <div className="p-6">
          {activeTab === 'config' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Configuration Form */}
              <div className="space-y-6">
                <h3 className="text-lg font-semibold text-gray-900">Configuration du Widget</h3>
                
                {/* Widget Type */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Type de widget
                  </label>
                  <select
                    value={widgetConfig.type}
                    onChange={(e) => handleConfigChange('type', e.target.value)}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="analytics">Analytics</option>
                    <option value="protection">Protection</option>
                    <option value="content">Contenu</option>
                  </select>
                </div>

                {/* API Configuration */}
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Clé API
                    </label>
                    <input
                      type="text"
                      value={widgetConfig.apiKey}
                      onChange={(e) => handleConfigChange('apiKey', e.target.value)}
                      placeholder="Votre clé API Ainflue"
                      className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      ID Utilisateur
                    </label>
                    <input
                      type="text"
                      value={widgetConfig.userId}
                      onChange={(e) => handleConfigChange('userId', e.target.value)}
                      placeholder="Votre ID utilisateur"
                      className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                </div>

                {/* Appearance */}
                <div className="space-y-4">
                  <h4 className="font-medium text-gray-900">Apparence</h4>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Thème
                      </label>
                      <select
                        value={widgetConfig.theme}
                        onChange={(e) => handleConfigChange('theme', e.target.value)}
                        className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      >
                        <option value="light">Clair</option>
                        <option value="dark">Sombre</option>
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Taille
                      </label>
                      <select
                        value={widgetConfig.size}
                        onChange={(e) => handleConfigChange('size', e.target.value)}
                        className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      >
                        <option value="small">Petit</option>
                        <option value="medium">Moyen</option>
                        <option value="large">Grand</option>
                      </select>
                    </div>
                  </div>

                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="showTitle"
                      checked={widgetConfig.showTitle}
                      onChange={(e) => handleConfigChange('showTitle', e.target.checked)}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label htmlFor="showTitle" className="ml-2 text-sm text-gray-700">
                      Afficher le titre
                    </label>
                  </div>
                </div>

                {/* Custom Colors */}
                <div className="space-y-4">
                  <h4 className="font-medium text-gray-900">Couleurs personnalisées</h4>
                  
                  <div className="grid grid-cols-2 gap-4">
                    {Object.entries(widgetConfig.customColors).map(([key, value]) => (
                      <div key={key}>
                        <label className="block text-sm font-medium text-gray-700 mb-2 capitalize">
                          {key === 'primary' ? 'Primaire' : 
                           key === 'secondary' ? 'Secondaire' :
                           key === 'background' ? 'Arrière-plan' : 'Texte'}
                        </label>
                        <div className="flex items-center space-x-2">
                          <input
                            type="color"
                            value={value}
                            onChange={(e) => handleColorChange(key, e.target.value)}
                            className="w-12 h-8 border border-gray-300 rounded cursor-pointer"
                          />
                          <input
                            type="text"
                            value={value}
                            onChange={(e) => handleColorChange(key, e.target.value)}
                            className="flex-1 border border-gray-300 rounded-md px-3 py-1 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Live Preview */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Aperçu en temps réel</h3>
                <div className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                  <EmbeddableWidget
                    type={widgetConfig.type}
                    config={widgetConfig}
                  />
                </div>
              </div>
            </div>
          )}

          {activeTab === 'preview' && (
            <div className="text-center">
              <h3 className="text-lg font-semibold text-gray-900 mb-6">Aperçu du Widget</h3>
              <div className="max-w-md mx-auto border border-gray-200 rounded-lg overflow-hidden">
                <EmbeddableWidget
                  type={widgetConfig.type}
                  config={widgetConfig}
                />
              </div>
            </div>
          )}

          {activeTab === 'code' && (
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Code d'intégration</h3>
                <button
                  onClick={copyToClipboard}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-md transition-colors ${
                    copied 
                      ? 'bg-green-100 text-green-700' 
                      : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
                  }`}
                >
                  {copied ? (
                    <>
                      <CheckIcon className="h-4 w-4" />
                      <span>Copié!</span>
                    </>
                  ) : (
                    <>
                      <ClipboardDocumentIcon className="h-4 w-4" />
                      <span>Copier</span>
                    </>
                  )}
                </button>
              </div>
              
              <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm overflow-x-auto">
                <pre>{generateEmbedCode()}</pre>
              </div>
              
              <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                <h4 className="font-medium text-blue-900 mb-2">Instructions d'installation:</h4>
                <ol className="text-sm text-blue-800 space-y-1">
                  <li>1. Copiez le code d'intégration ci-dessus</li>
                  <li>2. Collez-le dans votre page HTML où vous voulez afficher le widget</li>
                  <li>3. Remplacez la clé API et l'ID utilisateur par vos vraies valeurs</li>
                  <li>4. Le widget apparaîtra automatiquement sur votre site</li>
                </ol>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}