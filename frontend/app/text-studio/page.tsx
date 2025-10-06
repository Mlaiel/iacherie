'use client';
import { useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, FileText, Sparkles, Loader2, Copy, Download, DollarSign, Zap, Info } from 'lucide-react';

interface TextMetadata {
  provider: string;
  model: string;
  tokens?: number;
  cost?: number;
  orchestration?: {
    reasoning: string;
    savings: number;
    quality: number;
  };
}

export default function TextStudioPage() {
  const [prompt, setPrompt] = useState('');
  const [provider, setProvider] = useState<'auto' | 'openai' | 'claude' | 'gemini' | 'cohere'>('auto');
  const [model, setModel] = useState('auto');
  const [type, setType] = useState<'chat' | 'article' | 'marketing' | 'technical' | 'creative'>('article');
  const [length, setLength] = useState<'short' | 'medium' | 'long'>('medium');
  const [quality, setQuality] = useState<'draft' | 'standard' | 'premium' | 'ultra'>('standard');
  const [temperature, setTemperature] = useState(0.7);
  const [maxTokens, setMaxTokens] = useState(1000);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<string | null>(null);
  const [metadata, setMetadata] = useState<TextMetadata | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const PROVIDERS_INFO = {
    auto: {
      name: '🎼 Maestro (Auto)',
      desc: 'Sélection intelligente - Meilleure qualité au coût le plus bas',
      cost: 'Variable',
      color: 'from-purple-500 to-pink-500'
    },
    gemini: {
      name: '💰 Gemini 2.5 Flash',
      desc: 'Champion coût/qualité - 1M tokens context',
      cost: '$0.075',
      color: 'from-green-500 to-emerald-500'
    },
    openai: {
      name: '⚡ OpenAI GPT',
      desc: 'Rapide et polyvalent',
      cost: '$0.15-$2.50',
      color: 'from-blue-500 to-cyan-500'
    },
    claude: {
      name: '🧠 Claude Sonnet 4',
      desc: 'Meilleur raisonnement',
      cost: '$3.00',
      color: 'from-purple-600 to-indigo-600'
    },
    cohere: {
      name: '🔷 Cohere Command-A',
      desc: 'Alternative solide',
      cost: '$0.50',
      color: 'from-orange-500 to-red-500'
    }
  };

  const MODELS = {
    openai: ['auto', 'gpt-4o', 'gpt-4o-mini', 'gpt-3.5-turbo'],
    claude: ['auto', 'claude-sonnet-4.5-20241022', 'claude-3-opus-20240229'],
    gemini: ['auto', 'gemini-2.5-flash', 'gemini-pro'],
    cohere: ['auto', 'command-a-03-2025']
  };

  const generateText = async () => {
    if (!prompt.trim()) {
      setError('Veuillez entrer un prompt');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);
    setMetadata(null);

    try {
      const payload = {
        prompt: prompt.trim(),
        provider,
        model: model !== 'auto' ? model : undefined,
        type,
        length,
        quality,
        temperature,
        maxTokens
      };

      console.log('📝 Génération texte avec orchestration:', payload);

      const response = await fetch('/api/generate/text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (!data.success) {
        throw new Error(data.error || 'Échec de génération');
      }

      setResult(data.text);
      setMetadata({
        provider: data.provider,
        model: data.model,
        tokens: data.usage?.total_tokens,
        cost: data.cost,
        orchestration: data.orchestration
      });

    } catch (err: any) {
      console.error('❌ Erreur:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    if (result) {
      navigator.clipboard.writeText(result);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/" className="p-2 hover:bg-gray-100 rounded-lg transition">
                <ArrowLeft className="h-5 w-5" />
              </Link>
              <FileText className="h-8 w-8 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                  Text Studio Pro
                </h1>
                <p className="text-sm text-gray-500">IA Textuelle - 5 Providers Orchestrés</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-semibold">
                🎼 74 APIs Orchestrées
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
            <div className="bg-white rounded-xl shadow-lg p-6 border border-blue-100">
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                💭 Prompt / Instructions
              </label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Décrivez ce que vous voulez générer... (article, script, description, code, etc.)"
                className="w-full h-32 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              />
              <div className="mt-2 text-xs text-gray-500">
                {prompt.length} caractères
              </div>
            </div>

            {/* Provider & Quality */}
            <div className="bg-white rounded-xl shadow-lg p-6 border border-blue-100">
              <div className="grid grid-cols-2 gap-4">
                
                {/* Provider */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    🎯 Provider
                  </label>
                  <select
                    value={provider}
                    onChange={(e) => {
                      setProvider(e.target.value as any);
                      setModel('auto');
                    }}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="auto">🎼 Auto (Intelligent)</option>
                    <option value="gemini">💰 Gemini (Économique)</option>
                    <option value="openai">⚡ OpenAI GPT</option>
                    <option value="claude">🧠 Claude</option>
                    <option value="cohere">🔷 Cohere</option>
                  </select>
                  {provider !== 'auto' && (
                    <div className="mt-2 text-xs">
                      <span className={`px-2 py-1 rounded-full bg-gradient-to-r ${PROVIDERS_INFO[provider].color} text-white`}>
                        {PROVIDERS_INFO[provider].cost}
                      </span>
                    </div>
                  )}
                </div>

                {/* Quality */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    💎 Qualité
                  </label>
                  <select
                    value={quality}
                    onChange={(e) => setQuality(e.target.value as any)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="draft">Draft</option>
                    <option value="standard">Standard</option>
                    <option value="premium">Premium</option>
                    <option value="ultra">Ultra</option>
                  </select>
                </div>

              </div>
            </div>

            {/* Type & Length */}
            <div className="bg-white rounded-xl shadow-lg p-6 border border-blue-100">
              <div className="grid grid-cols-2 gap-4">
                
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    📋 Type de contenu
                  </label>
                  <select
                    value={type}
                    onChange={(e) => setType(e.target.value as any)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="chat">💬 Chat/Conversation</option>
                    <option value="article">📄 Article/Blog</option>
                    <option value="marketing">📢 Marketing/Pub</option>
                    <option value="technical">🔧 Technique/Code</option>
                    <option value="creative">🎨 Créatif/Story</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    📏 Longueur
                  </label>
                  <select
                    value={length}
                    onChange={(e) => setLength(e.target.value as any)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="short">Court (~100 mots)</option>
                    <option value="medium">Moyen (~500 mots)</option>
                    <option value="long">Long (~1000+ mots)</option>
                  </select>
                </div>

              </div>
            </div>

            {/* Modèle manuel */}
            {provider !== 'auto' && (
              <div className="bg-white rounded-xl shadow-lg p-6 border border-blue-100">
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  🤖 Modèle spécifique (optionnel)
                </label>
                <select
                  value={model}
                  onChange={(e) => setModel(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  {(MODELS[provider as keyof typeof MODELS] || ['auto']).map(m => (
                    <option key={m} value={m}>
                      {m === 'auto' ? '🎯 Auto (Recommandé)' : m}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* Advanced */}
            {showAdvanced && (
              <div className="bg-white rounded-xl shadow-lg p-6 border border-blue-100">
                <h3 className="font-semibold text-gray-700 mb-4">⚙️ Paramètres Avancés</h3>
                <div className="space-y-4">
                  
                  <div>
                    <label className="block text-sm text-gray-700 mb-2">
                      🎨 Température (créativité): {temperature}
                    </label>
                    <input
                      type="range"
                      min="0"
                      max="2"
                      step="0.1"
                      value={temperature}
                      onChange={(e) => setTemperature(parseFloat(e.target.value))}
                      className="w-full"
                    />
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>Précis</span>
                      <span>Équilibré</span>
                      <span>Créatif</span>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm text-gray-700 mb-2">
                      📊 Max Tokens: {maxTokens}
                    </label>
                    <input
                      type="range"
                      min="100"
                      max="4000"
                      step="100"
                      value={maxTokens}
                      onChange={(e) => setMaxTokens(parseInt(e.target.value))}
                      className="w-full"
                    />
                  </div>

                </div>
              </div>
            )}

            <button
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="text-sm text-blue-600 hover:text-blue-700"
            >
              {showAdvanced ? '▲ Masquer' : '▼ Afficher'} les paramètres avancés
            </button>

            {/* Bouton Generate */}
            <button
              onClick={generateText}
              disabled={loading || !prompt.trim()}
              className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-4 rounded-xl font-semibold hover:from-blue-700 hover:to-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed shadow-lg flex items-center justify-center space-x-2"
            >
              {loading ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  <span>Génération en cours...</span>
                </>
              ) : (
                <>
                  <Sparkles className="h-5 w-5" />
                  <span>Générer avec {provider === 'auto' ? 'Maestro' : PROVIDERS_INFO[provider].name.split(' ')[1]}</span>
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
                  L'orchestrateur sélectionnera automatiquement le meilleur provider selon votre qualité et use case pour maximiser les économies.
                </p>
              </div>
            )}

            {/* Metadata */}
            {metadata && (
              <div className="bg-white rounded-xl shadow-lg p-6 border border-blue-100">
                <h3 className="font-semibold text-gray-700 mb-3">📊 Informations</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Provider:</span>
                    <span className="font-semibold">{metadata.provider}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Modèle:</span>
                    <span className="font-mono text-xs">{metadata.model}</span>
                  </div>
                  {metadata.tokens && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Tokens:</span>
                      <span>{metadata.tokens}</span>
                    </div>
                  )}
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
                        <div className="text-xs bg-blue-50 p-2 rounded">
                          {metadata.orchestration.reasoning}
                        </div>
                      </div>
                      {metadata.orchestration.savings > 0 && (
                        <div className="flex items-center space-x-2 text-green-600">
                          <DollarSign className="h-4 w-4" />
                          <span className="text-sm font-semibold">
                            Économie: ${metadata.orchestration.savings.toFixed(3)}
                          </span>
                        </div>
                      )}
                    </>
                  )}
                </div>
              </div>
            )}

            {/* Result */}
            {result && (
              <div className="bg-white rounded-xl shadow-lg p-6 border border-blue-100">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold text-gray-700">✨ Résultat</h3>
                  <div className="flex space-x-2">
                    <button
                      onClick={copyToClipboard}
                      className="p-2 hover:bg-gray-100 rounded-lg transition"
                      title="Copier"
                    >
                      <Copy className="h-4 w-4 text-gray-600" />
                    </button>
                  </div>
                </div>
                <div className="prose prose-sm max-w-none">
                  <div className="whitespace-pre-wrap text-gray-700 text-sm leading-relaxed">
                    {result}
                  </div>
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
