'use client';
import { useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, Image as ImageIcon, Sparkles, Loader2, Download, DollarSign, Zap } from 'lucide-react';

interface ImageMetadata {
  provider: string;
  model?: string;
  cost?: number;
  quality: string;
  size?: string;
  orchestration?: {
    reasoning: string;
    savings: number;
    quality: number;
  };
}

export default function ImageStudioPage() {
  const [prompt, setPrompt] = useState('');
  const [provider, setProvider] = useState<string>('auto');
  const [style, setStyle] = useState('realistic');
  const [quality, setQuality] = useState<'draft' | 'standard' | 'premium' | 'ultra'>('standard');
  const [size, setSize] = useState('1024x1024');
  const [loading, setLoading] = useState(false);
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [metadata, setMetadata] = useState<ImageMetadata | null>(null);
  const [error, setError] = useState<string | null>(null);

  const MODELS = {
    // 🆓 MODÈLES INTERNES (GRATUITS)
    internal: [
      { id: 'internal-diffusion-xl', name: '🆓 AI Leader Diffusion XL', desc: 'Ultra qualité - GRATUIT', cost: 0, quality: 'ultra' },
      { id: 'internal-sdxl-turbo', name: '� AI Leader SDXL Turbo', desc: 'Très rapide - GRATUIT', cost: 0, quality: 'high' },
      { id: 'internal-image-pro', name: '🆓 AI Leader Image Pro', desc: 'Haute qualité - GRATUIT', cost: 0, quality: 'high' },
      { id: 'internal-photorealistic', name: '🆓 AI Leader Photo-Réaliste', desc: 'Ultra réaliste - GRATUIT', cost: 0, quality: 'ultra' },
      { id: 'internal-artistic', name: '🆓 AI Leader Artistique', desc: 'Style artistique - GRATUIT', cost: 0, quality: 'high' },
      { id: 'internal-anime', name: '🆓 AI Leader Anime', desc: 'Style anime - GRATUIT', cost: 0, quality: 'high' },
    ],
    // 💰 APIs EXTERNES (PAYANTES)
    external: [
      { id: 'dall-e-3', name: '💰 DALL-E 3', desc: 'OpenAI haute qualité', cost: 0.040, quality: 'high' },
      { id: 'dall-e-3-hd', name: '💰 DALL-E 3 HD', desc: 'OpenAI ultra qualité', cost: 0.080, quality: 'ultra' },
      { id: 'dall-e-2', name: '💰 DALL-E 2', desc: 'OpenAI économique', cost: 0.020, quality: 'medium' },
      { id: 'stability-sd-xl', name: '💰 Stable Diffusion XL', desc: 'Stability AI', cost: 0.030, quality: 'high' },
      { id: 'leonardo-xl', name: '💰 Leonardo XL', desc: 'Bon rapport qualité/prix', cost: 0.012, quality: 'high' },
      { id: 'midjourney-v6', name: '💰 Midjourney v6', desc: 'Premium artistique', cost: 0.040, quality: 'ultra' },
    ],
    auto: { id: 'auto', name: '🎼 Maestro Auto-Select', desc: 'Sélection intelligente - Privilégie GRATUIT', cost: 'Variable', quality: 'optimal' }
  };

  const PROVIDERS_INFO = {
    auto: {
      name: '🎼 Maestro (Auto)',
      desc: 'Sélection intelligente - Privilégie GRATUIT puis meilleur prix',
      cost: 'Variable',
      color: 'from-purple-500 to-pink-500'
    }
  };

  const STYLES = [
    { id: 'realistic', name: 'Réaliste', icon: '📷' },
    { id: 'artistic', name: 'Artistique', icon: '🎨' },
    { id: 'cartoon', name: 'Cartoon', icon: '🎭' },
    { id: '3d', name: '3D Render', icon: '🎲' },
    { id: 'anime', name: 'Anime', icon: '⭐' },
    { id: 'abstract', name: 'Abstrait', icon: '🌀' }
  ];

  const SIZES = [
    '512x512',
    '1024x1024',
    '1792x1024', // 16:9
    '1024x1792'  // 9:16
  ];

  const generateImage = async () => {
    if (!prompt.trim()) {
      setError('Veuillez entrer une description');
      return;
    }

    setLoading(true);
    setError(null);
    setImageUrl(null);
    setMetadata(null);

    try {
      // Amélioration du prompt pour être ultra-précis avec toutes les langues
      const enhancedPrompt = `${prompt.trim()}. Ultra-précis: respectez EXACTEMENT chaque détail, couleur, objet, position, style et ambiance décrits. Multilingue supporté: français, anglais, arabe, dialectes, mélanges. Générez précisément ce qui est demandé sans ajout ni modification.`;

      const payload = {
        prompt: enhancedPrompt,
        model: provider, // Utiliser model au lieu de model_id
        style,
        quality,
        size,
        prefer_internal: provider.startsWith('internal-') ? true : provider === 'auto'
      };

      console.log('🎨 Génération image ultra-précise:', payload);

      const response = await fetch('/api/generate/image', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (!data.success) {
        throw new Error(data.error || 'Échec de génération image');
      }

      setImageUrl(data.imageUrl);
      setMetadata({
        provider: data.provider,
        model: data.model,
        cost: data.cost,
        quality: data.quality,
        size: size,
        orchestration: data.orchestration
      });

    } catch (err: any) {
      console.error('❌ Erreur:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const downloadImage = () => {
    if (imageUrl) {
      const link = document.createElement('a');
      link.href = imageUrl;
      link.download = `ai-image-${Date.now()}.png`;
      link.click();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-purple-50 to-indigo-50">
      
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/" className="p-2 hover:bg-gray-100 rounded-lg transition">
                <ArrowLeft className="h-5 w-5" />
              </Link>
              <ImageIcon className="h-8 w-8 text-pink-600" />
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-pink-600 to-purple-600 bg-clip-text text-transparent">
                  Image Studio Pro
                </h1>
                <p className="text-sm text-gray-500">🆓 7 Modèles Internes GRATUITS + 6 APIs Externes | Multilingue</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-semibold">
                � 7 Modèles GRATUITS
              </span>
              <span className="px-3 py-1 bg-pink-100 text-pink-700 rounded-full text-xs font-semibold">
                13 Modèles Total
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Panel gauche - Configuration */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Prompt */}
            <div className="bg-white rounded-xl shadow-lg p-6 border border-pink-100">
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                🎨 Description de l'image
              </label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Décrivez l'image que vous voulez créer... (ex: un chat mignon qui joue avec une balle colorée)"
                className="w-full h-32 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent resize-none"
              />
              <div className="mt-2 text-xs text-gray-500">
                {prompt.length} caractères
              </div>
            </div>

            {/* Provider & Quality */}
            <div className="bg-white rounded-xl shadow-lg p-6 border border-pink-100">
              <div className="grid grid-cols-1 gap-6">
                
                {/* Modèle */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-3">
                    🤖 Modèle AI
                  </label>
                  
                  {/* Auto Select */}
                  <div className="mb-4">
                    <button
                      onClick={() => setProvider('auto')}
                      className={`w-full p-4 rounded-lg border-2 transition text-left ${
                        provider === 'auto'
                          ? 'border-purple-500 bg-purple-50'
                          : 'border-gray-200 hover:border-purple-300'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-semibold text-gray-900">{MODELS.auto.name}</div>
                          <div className="text-xs text-gray-600 mt-1">{MODELS.auto.desc}</div>
                        </div>
                        <div className="text-sm font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                          OPTIMAL
                        </div>
                      </div>
                    </button>
                  </div>

                  {/* Modèles Internes GRATUITS */}
                  <div className="mb-4">
                    <div className="text-xs font-bold text-green-600 mb-2 uppercase tracking-wide">
                      � Modèles Internes (GRATUITS - Privilégiés)
                    </div>
                    <div className="grid grid-cols-1 gap-2">
                      {MODELS.internal.map((model) => (
                        <button
                          key={model.id}
                          onClick={() => setProvider(model.id)}
                          className={`p-3 rounded-lg border-2 transition text-left ${
                            provider === model.id
                              ? 'border-green-500 bg-green-50'
                              : 'border-gray-200 hover:border-green-300'
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex-1">
                              <div className="font-semibold text-sm text-gray-900">{model.name}</div>
                              <div className="text-xs text-gray-600 mt-1">{model.desc}</div>
                            </div>
                            <div className="ml-3 flex items-center gap-2">
                              <span className="px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs font-bold">
                                {model.cost === 0 ? 'GRATUIT' : `$${model.cost}`}
                              </span>
                              <span className="text-xs text-gray-500">{model.quality}</span>
                            </div>
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* APIs Externes PAYANTES */}
                  <div>
                    <div className="text-xs font-bold text-orange-600 mb-2 uppercase tracking-wide">
                      💰 APIs Externes (Payantes)
                    </div>
                    <div className="grid grid-cols-1 gap-2">
                      {MODELS.external.map((model) => (
                        <button
                          key={model.id}
                          onClick={() => setProvider(model.id)}
                          className={`p-3 rounded-lg border-2 transition text-left ${
                            provider === model.id
                              ? 'border-orange-500 bg-orange-50'
                              : 'border-gray-200 hover:border-orange-300'
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex-1">
                              <div className="font-semibold text-sm text-gray-900">{model.name}</div>
                              <div className="text-xs text-gray-600 mt-1">{model.desc}</div>
                            </div>
                            <div className="ml-3 flex items-center gap-2">
                              <span className="px-2 py-1 bg-orange-100 text-orange-700 rounded-full text-xs font-bold">
                                ${model.cost.toFixed(3)}
                              </span>
                              <span className="text-xs text-gray-500">{model.quality}</span>
                            </div>
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Quality */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    💎 Qualité
                  </label>
                  <select
                    value={quality}
                    onChange={(e) => setQuality(e.target.value as any)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500"
                  >
                    <option value="draft">Draft (test rapide)</option>
                    <option value="standard">Standard</option>
                    <option value="premium">Premium</option>
                    <option value="ultra">Ultra HD</option>
                  </select>
                </div>

              </div>
            </div>

            {/* Style */}
            <div className="bg-white rounded-xl shadow-lg p-6 border border-pink-100">
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                🎭 Style Artistique
              </label>
              <div className="grid grid-cols-3 gap-3">
                {STYLES.map((s) => (
                  <button
                    key={s.id}
                    onClick={() => setStyle(s.id)}
                    className={`p-3 rounded-lg border-2 transition text-center ${
                      style === s.id
                        ? 'border-pink-600 bg-pink-50'
                        : 'border-gray-200 hover:border-pink-300'
                    }`}
                  >
                    <div className="text-2xl mb-1">{s.icon}</div>
                    <div className="text-sm font-medium">{s.name}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Size */}
            <div className="bg-white rounded-xl shadow-lg p-6 border border-pink-100">
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                📐 Dimensions
              </label>
              <div className="grid grid-cols-4 gap-3">
                {SIZES.map((s) => (
                  <button
                    key={s}
                    onClick={() => setSize(s)}
                    className={`p-3 rounded-lg border-2 transition text-center ${
                      size === s
                        ? 'border-pink-600 bg-pink-50'
                        : 'border-gray-200 hover:border-pink-300'
                    }`}
                  >
                    <div className="text-xs font-medium">{s}</div>
                    <div className="text-xs text-gray-500 mt-1">
                      {s === '1792x1024' && '16:9'}
                      {s === '1024x1792' && '9:16'}
                      {s === '1024x1024' && '1:1'}
                      {s === '512x512' && 'Mini'}
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Bouton Generate */}
            <button
              onClick={generateImage}
              disabled={loading || !prompt.trim()}
              className="w-full bg-gradient-to-r from-pink-600 to-purple-600 text-white py-4 rounded-xl font-semibold hover:from-pink-700 hover:to-purple-700 transition disabled:opacity-50 disabled:cursor-not-allowed shadow-lg flex items-center justify-center space-x-2"
            >
              {loading ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  <span>Génération en cours...</span>
                </>
              ) : (
                <>
                  <Sparkles className="h-5 w-5" />
                  <span>Générer avec {
                    provider === 'auto' ? 'Maestro Auto' : 
                    [...MODELS.internal, ...MODELS.external].find(m => m.id === provider)?.name.split(' ')[1] || 'AI'
                  }</span>
                </>
              )}
            </button>

          </div>

          {/* Panel droit - Résultat */}
          <div className="space-y-6">
            
            {/* Orchestration Info */}
            {provider === 'auto' && (
              <div className="bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl shadow-lg p-6 text-white">
                <div className="flex items-center space-x-2 mb-3">
                  <Sparkles className="h-5 w-5" />
                  <h3 className="font-semibold">Mode Maestro</h3>
                </div>
                <p className="text-sm text-white/90">
                  L'orchestrateur sélectionnera automatiquement le meilleur provider pour votre qualité et style, avec des économies jusqu'à 90%.
                </p>
              </div>
            )}

            {/* Metadata */}
            {metadata && (
              <div className="bg-white rounded-xl shadow-lg p-6 border border-pink-100">
                <h3 className="font-semibold text-gray-700 mb-3">📊 Informations</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Provider:</span>
                    <span className="font-semibold">{metadata.provider}</span>
                  </div>
                  {metadata.model && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Modèle:</span>
                      <span className="text-xs font-mono">{metadata.model}</span>
                    </div>
                  )}
                  <div className="flex justify-between">
                    <span className="text-gray-600">Qualité:</span>
                    <span className="font-semibold">{metadata.quality}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Dimensions:</span>
                    <span>{metadata.size}</span>
                  </div>
                  {metadata.cost && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Coût:</span>
                      <span className="font-semibold text-green-600">${metadata.cost.toFixed(3)}</span>
                    </div>
                  )}
                  {metadata.orchestration && (
                    <>
                      <div className="pt-3 mt-3 border-t border-gray-200">
                        <div className="text-xs text-gray-600 mb-1">Orchestration:</div>
                        <div className="text-xs bg-pink-50 p-2 rounded">
                          {metadata.orchestration.reasoning}
                        </div>
                      </div>
                      {metadata.orchestration.savings > 0 && (
                        <div className="flex items-center space-x-2 text-green-600">
                          <DollarSign className="h-4 w-4" />
                          <span className="text-sm font-semibold">
                            Économie: ${metadata.orchestration.savings.toFixed(3)} ({Math.round((metadata.orchestration.savings / (metadata.cost! + metadata.orchestration.savings)) * 100)}%)
                          </span>
                        </div>
                      )}
                    </>
                  )}
                </div>
              </div>
            )}

            {/* Image Result */}
            {imageUrl && (
              <div className="bg-white rounded-xl shadow-lg p-6 border border-pink-100">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold text-gray-700">✨ Image Générée</h3>
                  <button
                    onClick={downloadImage}
                    className="p-2 hover:bg-gray-100 rounded-lg transition"
                    title="Télécharger"
                  >
                    <Download className="h-4 w-4 text-gray-600" />
                  </button>
                </div>
                <div className="rounded-lg overflow-hidden">
                  <img
                    src={imageUrl}
                    alt="Generated"
                    className="w-full h-auto"
                  />
                </div>
              </div>
            )}

            {/* Error */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-xl p-4">
                <p className="text-sm text-red-600">❌ {error}</p>
              </div>
            )}

          </div>

        </div>
      </div>

    </div>
  );
}
