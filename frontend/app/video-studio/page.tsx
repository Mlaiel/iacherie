'use client';

import React, { useState } from 'react';
import { Video, Wand2, Film, Upload, Youtube, Play, Download, Sparkles, Zap, Clock, DollarSign, CheckCircle } from 'lucide-react';

interface VideoProvider {
  id: string;
  name: string;
  icon: string;
  description: string;
  cost: string;
  quality: number;
  speed: string;
  features: string[];
  useCase: string;
  color: string;
}

export default function VideoStudio() {
  const [selectedProvider, setSelectedProvider] = useState<string>('auto');
  const [prompt, setPrompt] = useState('');
  const [duration, setDuration] = useState(5);
  const [quality, setQuality] = useState<'draft' | 'standard' | 'hd' | 'ultra'>('standard');
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState<any>(null);

  const providers: VideoProvider[] = [
    {
      id: 'auto',
      name: 'Maestro Auto',
      icon: '🎼',
      description: 'Sélection automatique du meilleur provider selon vos critères',
      cost: 'Variable',
      quality: 95,
      speed: 'Intelligent',
      features: ['75-97% économies', 'Qualité optimale', 'Fallback automatique'],
      useCase: 'Recommandé pour tous usages',
      color: 'from-purple-500 to-pink-500'
    },
    {
      id: 'runwayml',
      name: 'RunwayML Gen-3',
      icon: '🚀',
      description: 'Génération vidéo IA ultra-premium - Text-to-Video',
      cost: '$10.00/10s',
      quality: 100,
      speed: '2-3 min',
      features: ['Ultra HD', 'IA avancée', '680 crédits disponibles', 'Cinématique'],
      useCase: 'Vidéos IA uniques, publicités premium',
      color: 'from-red-500 to-orange-500'
    },
    {
      id: 'pexels',
      name: 'Pexels Video',
      icon: '🎬',
      description: 'Stock videos HD professionnels gratuits',
      cost: 'GRATUIT',
      quality: 85,
      speed: 'Instantané',
      features: ['HD/4K', 'Illimité', 'Pas de watermark', 'Commercial OK'],
      useCase: 'Stock footage, B-roll, backgrounds',
      color: 'from-green-500 to-teal-500'
    },
    {
      id: 'vimeo',
      name: 'Vimeo Pro',
      icon: '📹',
      description: 'Hébergement vidéo professionnel avec analytics',
      cost: '$0.02/GB',
      quality: 90,
      speed: 'Rapide',
      features: ['Privé/Public', 'Analytics', 'Embed', 'Pas de pub'],
      useCase: 'Hébergement, portfolio, client reviews',
      color: 'from-blue-500 to-cyan-500'
    },
    {
      id: 'loom',
      name: 'Loom',
      icon: '🎥',
      description: 'Screen recording & video messaging',
      cost: '$0.01/min',
      quality: 88,
      speed: 'Temps réel',
      features: ['Screen+Webcam', 'Transcription', 'Partage facile', 'CTA'],
      useCase: 'Tutoriels, démos, feedback vidéo',
      color: 'from-purple-500 to-indigo-500'
    },
    {
      id: 'youtube',
      name: 'YouTube',
      icon: '▶️',
      description: 'Streaming & analytics gratuit',
      cost: 'GRATUIT',
      quality: 92,
      speed: 'Rapide',
      features: ['SEO intégré', 'Analytics', 'Monétisation', 'Live streaming'],
      useCase: 'Publication, audience building',
      color: 'from-red-600 to-red-700'
    }
  ];

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      alert('Veuillez entrer un prompt');
      return;
    }

    setGenerating(true);
    setResult(null);

    try {
      const response = await fetch('/api/generate/video', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: prompt.trim(),
          provider: selectedProvider,
          duration,
          quality,
          type: 'generation'
        })
      });

      const data = await response.json();
      
      if (data.success) {
        setResult(data);
      } else {
        alert(`Erreur: ${data.error}`);
      }
    } catch (error) {
      console.error('Erreur génération vidéo:', error);
      alert('Erreur lors de la génération');
    } finally {
      setGenerating(false);
    }
  };

  const selectedProviderData = providers.find(p => p.id === selectedProvider);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-4 mb-4">
            <div className="p-4 bg-gradient-to-br from-red-500 to-orange-500 rounded-2xl">
              <Video className="w-12 h-12 text-white" />
            </div>
            <div>
              <h1 className="text-5xl font-bold text-white mb-2">Video Studio</h1>
              <p className="text-xl text-white/70">5 Providers • IA + Stock + Hébergement • Maestro Orchestration</p>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-4 gap-4">
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-4 border border-white/20">
              <div className="text-3xl font-bold text-white">5</div>
              <div className="text-white/60 text-sm">APIs Vidéo</div>
            </div>
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-4 border border-white/20">
              <div className="text-3xl font-bold text-green-400">680</div>
              <div className="text-white/60 text-sm">Crédits RunwayML</div>
            </div>
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-4 border border-white/20">
              <div className="text-3xl font-bold text-blue-400">∞</div>
              <div className="text-white/60 text-sm">Stock Gratuit</div>
            </div>
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-4 border border-white/20">
              <div className="text-3xl font-bold text-purple-400">95%</div>
              <div className="text-white/60 text-sm">Économies Maestro</div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Panel - Configuration */}
          <div className="lg:col-span-2 space-y-6">
            {/* Provider Selection */}
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
              <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
                <Wand2 className="w-6 h-6" />
                Sélection Provider
              </h2>
              
              <div className="grid grid-cols-2 gap-4">
                {providers.map((provider) => (
                  <button
                    key={provider.id}
                    onClick={() => setSelectedProvider(provider.id)}
                    className={`p-4 rounded-xl transition-all text-left ${
                      selectedProvider === provider.id
                        ? `bg-gradient-to-br ${provider.color} text-white shadow-lg scale-105`
                        : 'bg-white/5 text-white/70 hover:bg-white/10 border border-white/20'
                    }`}
                  >
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-3xl">{provider.icon}</span>
                      <div className="flex-1">
                        <div className="font-bold text-lg">{provider.name}</div>
                        <div className={`text-xs ${selectedProvider === provider.id ? 'text-white/80' : 'text-white/50'}`}>
                          {provider.cost}
                        </div>
                      </div>
                      {selectedProvider === provider.id && (
                        <CheckCircle className="w-5 h-5" />
                      )}
                    </div>
                    
                    {/* Quality Bar */}
                    <div className="mb-2">
                      <div className="h-1.5 bg-white/20 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-white"
                          style={{ width: `${provider.quality}%` }}
                        />
                      </div>
                      <div className={`text-xs mt-1 ${selectedProvider === provider.id ? 'text-white/80' : 'text-white/50'}`}>
                        Qualité: {provider.quality}/100
                      </div>
                    </div>

                    <div className={`text-xs ${selectedProvider === provider.id ? 'text-white/80' : 'text-white/50'}`}>
                      {provider.description}
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Prompt Input */}
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
              <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
                <Film className="w-6 h-6" />
                Prompt Vidéo
              </h2>

              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder={
                  selectedProvider === 'runwayml' 
                    ? "Ex: A cinematic shot of a spaceship flying through a neon-lit cyberpunk city..."
                    : selectedProvider === 'pexels'
                    ? "Ex: mountain landscape sunset timelapse"
                    : "Décrivez votre vidéo ou ce que vous recherchez..."
                }
                className="w-full h-32 bg-white/5 border border-white/20 rounded-xl p-4 text-white placeholder-white/40 resize-none focus:outline-none focus:border-purple-500"
              />

              <div className="grid grid-cols-2 gap-4 mt-4">
                {/* Duration */}
                <div>
                  <label className="text-white/70 text-sm mb-2 block flex items-center gap-2">
                    <Clock className="w-4 h-4" />
                    Durée (secondes)
                  </label>
                  <select
                    value={duration}
                    onChange={(e) => setDuration(Number(e.target.value))}
                    className="w-full bg-white/5 border border-white/20 rounded-xl p-3 text-white focus:outline-none focus:border-purple-500"
                    disabled={selectedProvider === 'pexels' || selectedProvider === 'youtube'}
                  >
                    <option value={5}>5 secondes</option>
                    <option value={10}>10 secondes</option>
                    <option value={15}>15 secondes</option>
                    <option value={30}>30 secondes</option>
                    <option value={60}>1 minute</option>
                  </select>
                </div>

                {/* Quality */}
                <div>
                  <label className="text-white/70 text-sm mb-2 block flex items-center gap-2">
                    <Sparkles className="w-4 h-4" />
                    Qualité
                  </label>
                  <select
                    value={quality}
                    onChange={(e) => setQuality(e.target.value as any)}
                    className="w-full bg-white/5 border border-white/20 rounded-xl p-3 text-white focus:outline-none focus:border-purple-500"
                  >
                    <option value="draft">Draft (rapide)</option>
                    <option value="standard">Standard</option>
                    <option value="hd">HD</option>
                    <option value="ultra">Ultra (4K)</option>
                  </select>
                </div>
              </div>

              {/* Generate Button */}
              <button
                onClick={handleGenerate}
                disabled={generating || !prompt.trim()}
                className={`w-full mt-6 py-4 rounded-xl font-bold text-lg transition-all flex items-center justify-center gap-3 ${
                  generating || !prompt.trim()
                    ? 'bg-white/10 text-white/40 cursor-not-allowed'
                    : `bg-gradient-to-r ${selectedProviderData?.color} text-white hover:scale-105 shadow-lg`
                }`}
              >
                {generating ? (
                  <>
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white" />
                    Génération en cours...
                  </>
                ) : (
                  <>
                    <Play className="w-6 h-6" />
                    Générer Vidéo
                  </>
                )}
              </button>
            </div>

            {/* Result */}
            {result && (
              <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                <h2 className="text-2xl font-bold text-white mb-4">Résultat</h2>
                
                {result.videoUrl && (
                  <video
                    src={result.videoUrl}
                    controls
                    className="w-full rounded-xl mb-4"
                  />
                )}

                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-white/5 rounded-xl p-4">
                    <div className="text-white/60 text-sm mb-1">Provider</div>
                    <div className="text-white font-bold">{result.provider}</div>
                  </div>
                  <div className="bg-white/5 rounded-xl p-4">
                    <div className="text-white/60 text-sm mb-1">Coût</div>
                    <div className="text-green-400 font-bold">${result.cost?.toFixed(3) || '0.000'}</div>
                  </div>
                  <div className="bg-white/5 rounded-xl p-4">
                    <div className="text-white/60 text-sm mb-1">Durée</div>
                    <div className="text-white font-bold">{result.duration}s</div>
                  </div>
                  <div className="bg-white/5 rounded-xl p-4">
                    <div className="text-white/60 text-sm mb-1">Qualité</div>
                    <div className="text-white font-bold">{result.quality}</div>
                  </div>
                </div>

                {result.savings > 0 && (
                  <div className="mt-4 bg-green-500/20 border border-green-500/30 rounded-xl p-4">
                    <div className="flex items-center gap-2 text-green-400">
                      <DollarSign className="w-5 h-5" />
                      <span className="font-bold">
                        Économie: ${result.savings.toFixed(2)} ({Math.round(result.savingsPercent)}%)
                      </span>
                    </div>
                    <div className="text-green-300 text-sm mt-1">{result.reasoning}</div>
                  </div>
                )}

                <button className="w-full mt-4 bg-blue-500 hover:bg-blue-600 text-white py-3 rounded-xl font-bold flex items-center justify-center gap-2">
                  <Download className="w-5 h-5" />
                  Télécharger Vidéo
                </button>
              </div>
            )}
          </div>

          {/* Right Panel - Provider Details */}
          <div className="space-y-6">
            {selectedProviderData && (
              <>
                {/* Selected Provider Card */}
                <div className={`bg-gradient-to-br ${selectedProviderData.color} rounded-2xl p-6 text-white shadow-2xl`}>
                  <div className="text-5xl mb-4">{selectedProviderData.icon}</div>
                  <h3 className="text-2xl font-bold mb-2">{selectedProviderData.name}</h3>
                  <p className="text-white/90 mb-4">{selectedProviderData.description}</p>
                  
                  <div className="space-y-3">
                    <div className="flex items-center justify-between bg-white/10 rounded-lg p-3">
                      <span className="text-white/80">Coût</span>
                      <span className="font-bold">{selectedProviderData.cost}</span>
                    </div>
                    <div className="flex items-center justify-between bg-white/10 rounded-lg p-3">
                      <span className="text-white/80">Qualité</span>
                      <span className="font-bold">{selectedProviderData.quality}/100</span>
                    </div>
                    <div className="flex items-center justify-between bg-white/10 rounded-lg p-3">
                      <span className="text-white/80">Vitesse</span>
                      <span className="font-bold">{selectedProviderData.speed}</span>
                    </div>
                  </div>
                </div>

                {/* Features */}
                <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                  <h3 className="text-xl font-bold text-white mb-4">Fonctionnalités</h3>
                  <div className="space-y-2">
                    {selectedProviderData.features.map((feature, i) => (
                      <div key={i} className="flex items-center gap-2 text-white/80">
                        <CheckCircle className="w-4 h-4 text-green-400" />
                        <span>{feature}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Use Case */}
                <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                  <h3 className="text-xl font-bold text-white mb-4">Cas d'usage</h3>
                  <p className="text-white/80">{selectedProviderData.useCase}</p>
                </div>

                {/* Maestro Info */}
                {selectedProvider === 'auto' && (
                  <div className="bg-gradient-to-br from-purple-500/20 to-pink-500/20 backdrop-blur-lg rounded-2xl p-6 border border-purple-500/30">
                    <div className="flex items-center gap-2 mb-3">
                      <Zap className="w-6 h-6 text-yellow-400" />
                      <h3 className="text-xl font-bold text-white">Maestro Auto</h3>
                    </div>
                    <p className="text-white/80 text-sm">
                      Le système Maestro analyse votre demande et sélectionne automatiquement 
                      le meilleur provider pour optimiser qualité et coût. Économies moyennes: 75-95%.
                    </p>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
