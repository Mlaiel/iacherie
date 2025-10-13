'use client';
import { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
import { ArrowLeft, Music, Play, Pause, Download, Mic, Settings, Sparkles, Loader2, Volume2, Info, Zap, DollarSign } from 'lucide-react';

// Types pour l'API
interface VoiceInfo {
  name: string;
  description: string;
  gender: string;
  language: string;
}

interface AudioMetadata {
  provider: string;
  voice: string;
  voiceInfo: VoiceInfo;
  model: string;
  format: string;
  size: number;
  duration?: number;
  speed?: number;
  settings?: {
    stability?: number;
    similarity_boost?: number;
    style?: number;
    use_speaker_boost?: boolean;
  };
  generatedAt: string;
  cost?: number;
  orchestration?: {
    reasoning: string;
    savings: number;
    quality: number;
  };
}

interface AudioResponse {
  success: boolean;
  audio: string;
  metadata: AudioMetadata;
  error?: string;
}

export default function AudioStudioPage() {
  // États
  const [text, setText] = useState('');
  const [provider, setProvider] = useState<'auto' | 'openai' | 'elevenlabs' | 'google' | 'spotify' | 'freesound' | 'shazam'>('auto');
  const [voice, setVoice] = useState('');
  const [model, setModel] = useState('auto');
  const [speed, setSpeed] = useState(1.0);
  const [pitch, setPitch] = useState(0);
  const [quality, setQuality] = useState<'draft' | 'standard' | 'premium' | 'ultra'>('standard');
  const [stability, setStability] = useState(0.5);
  const [similarityBoost, setSimilarityBoost] = useState(0.75);
  const [style, setStyle] = useState(0);
  const [loading, setLoading] = useState(false);
  const [audioData, setAudioData] = useState<string | null>(null);
  const [metadata, setMetadata] = useState<AudioMetadata | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [useCase, setUseCase] = useState<'podcast' | 'voice-over' | 'marketing' | 'chat'>('podcast');
  
  const audioRef = useRef<HTMLAudioElement>(null);

  // Voix disponibles
  const OPENAI_VOICES = [
    { id: 'alloy', name: 'Alloy', desc: 'Voix neutre et claire', gender: '⚪', cost: '$0.015' },
    { id: 'echo', name: 'Echo', desc: 'Voix masculine profonde', gender: '👨', cost: '$0.015' },
    { id: 'fable', name: 'Fable', desc: 'Voix narrative', gender: '⚪', cost: '$0.015' },
    { id: 'onyx', name: 'Onyx', desc: 'Voix masculine autoritaire', gender: '👨', cost: '$0.015' },
    { id: 'nova', name: 'Nova', desc: 'Voix féminine dynamique', gender: '👩', cost: '$0.015' },
    { id: 'shimmer', name: 'Shimmer', desc: 'Voix féminine douce', gender: '👩', cost: '$0.015' },
  ];

  const ELEVENLABS_VOICES = [
    { id: 'EXAVITQu4vr4xnSDxMaL', name: 'Sarah', desc: 'Voix professionnelle premium', gender: '👩', cost: '$0.18' },
    { id: '21m00Tcm4TlvDq8ikWAM', name: 'Rachel', desc: 'Voix narrative premium', gender: '👩', cost: '$0.18' },
    { id: 'AZnzlk1XvdvUeBnXmlld', name: 'Domi', desc: 'Voix confiante premium', gender: '👩', cost: '$0.18' },
    { id: 'ErXwobaYiN019PkySvjV', name: 'Antoni', desc: 'Voix chaleureuse premium', gender: '👨', cost: '$0.18' },
    { id: 'VR6AewLTigWG4xSOukaG', name: 'Arnold', desc: 'Voix forte premium', gender: '👨', cost: '$0.18' },
  ];

  const GOOGLE_VOICES = [
    { id: 'fr-FR-Neural2-A', name: 'Française A', desc: 'Voix féminine neural', gender: '👩', cost: '$0.016' },
    { id: 'fr-FR-Neural2-B', name: 'Français B', desc: 'Voix masculine neural', gender: '👨', cost: '$0.016' },
    { id: 'en-US-Neural2-A', name: 'Anglais US A', desc: 'Voix féminine US', gender: '👩', cost: '$0.016' },
    { id: 'en-GB-Neural2-A', name: 'Anglais UK A', desc: 'Voix féminine UK', gender: '👩', cost: '$0.016' },
    { id: 'en-GB-Neural2-B', name: 'Anglais UK B', desc: 'Voix masculine UK', gender: '👨', cost: '$0.016' },
  ];

  const PROVIDERS_INFO = {
    auto: {
      name: '🎼 Maestro (Auto)',
      desc: 'Sélection intelligente - Meilleure qualité au coût le plus bas',
      icon: '🤖',
      color: 'from-purple-500 to-pink-500'
    },
    openai: {
      name: '⚡ OpenAI TTS',
      desc: 'Rapide et économique - $0.015/génération',
      icon: '💰',
      color: 'from-green-500 to-emerald-500'
    },
    elevenlabs: {
      name: '👑 ElevenLabs',
      desc: 'Qualité premium avec clonage vocal - $0.18/génération',
      icon: '💎',
      color: 'from-purple-600 to-indigo-600'
    },
    google: {
      name: '🌍 Google Cloud TTS',
      desc: 'Multilingue avec contrôle pitch - $0.016/génération',
      icon: '🎛️',
      color: 'from-blue-500 to-cyan-500'
    },
    spotify: {
      name: '🎵 Spotify',
      desc: 'Recherche musicale gratuite',
      icon: '🆓',
      color: 'from-green-600 to-teal-500'
    },
    freesound: {
      name: '🔊 FreeSound',
      desc: 'Bibliothèque d\'effets sonores gratuite',
      icon: '🆓',
      color: 'from-orange-500 to-red-500'
    },
    shazam: {
      name: '🎼 Shazam',
      desc: 'Reconnaissance musicale - $0.001/requête',
      icon: '🔍',
      color: 'from-blue-600 to-purple-600'
    }
  };

  // Génération audio
  const generateAudio = async () => {
    if (!text.trim()) {
      setError('Veuillez entrer du texte');
      return;
    }

    setLoading(true);
    setError(null);
    setAudioData(null);
    setMetadata(null);

    try {
      const payload: any = {
        text: text.trim(),
        provider,
        quality,
        useCase
      };

      // Paramètres communs
      if (speed !== 1.0) payload.speed = speed;

      // Paramètres selon provider
      if (provider === 'openai' || (provider === 'auto' && quality !== 'ultra')) {
        if (voice) payload.voice = voice;
        if (model && model !== 'auto') payload.model = model;
      }

      if (provider === 'elevenlabs' || (provider === 'auto' && quality === 'ultra')) {
        if (voice) payload.voice = voice;
        if (model && model !== 'auto') payload.model = model;
        if (showAdvanced) {
          payload.stability = stability;
          payload.similarity_boost = similarityBoost;
          payload.style = style;
          payload.use_speaker_boost = true;
        }
      }

      if (provider === 'google') {
        if (voice) payload.voice = voice;
        if (pitch !== 0) payload.pitch = pitch;
      }

      console.log('🎙️ Génération audio avec orchestration:', payload);

      const response = await fetch('/api/generate/audio', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data: AudioResponse = await response.json();

      if (!data.success) {
        throw new Error(data.error || 'Échec de génération audio');
      }

      setAudioData(data.audio);
      setMetadata(data.metadata);
      
      // Log orchestration info
      if (data.metadata.orchestration) {
        console.log('🎼 ORCHESTRATION:', data.metadata.orchestration);
      }
      
      // Auto-play
      setTimeout(() => {
        if (audioRef.current) {
          audioRef.current.play();
          setIsPlaying(true);
        }
      }, 100);

    } catch (err: any) {
      console.error('❌ Erreur:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Contrôles audio
  const togglePlay = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const downloadAudio = () => {
    if (audioData) {
      const link = document.createElement('a');
      link.href = `data:audio/mpeg;base64,${audioData}`;
      link.download = `audio-${Date.now()}.mp3`;
      link.click();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50">
      {/* Header */}
      <div className="bg-white shadow-lg border-b border-purple-100">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/" className="text-gray-600 hover:text-purple-600 transition">
                <ArrowLeft className="h-5 w-5" />
              </Link>
              <Mic className="h-8 w-8 text-purple-600" />
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                  Audio Studio Pro
                </h1>
                <p className="text-sm text-gray-500">TTS Professionnel pour Créateurs & Influenceurs</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-semibold">
                ⚡ OpenAI + ElevenLabs
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Panel gauche - Configuration */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Texte à générer */}
            <div className="bg-white rounded-xl shadow-lg p-6 border border-purple-100">
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                📝 Texte à transformer en audio
              </label>
              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Entrez votre texte ici... (pour podcast, narration, vidéo, publicité, etc.)"
                className="w-full h-32 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
              />
              <div className="mt-2 text-xs text-gray-500">
                {text.length} caractères • ~{Math.ceil(text.length / 15)} secondes estimées
              </div>
            </div>

            {/* Provider et Voix */}
            <div className="bg-white rounded-xl shadow-lg p-6 border border-purple-100">
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
                      setVoice('');
                    }}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  >
                    <option value="auto">🤖 Auto (Intelligent)</option>
                    <option value="openai">⚡ OpenAI (Rapide)</option>
                    <option value="elevenlabs">👑 ElevenLabs (Premium)</option>
                  </select>
                </div>

                {/* Qualité */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    💎 Qualité
                  </label>
                  <select
                    value={quality}
                    onChange={(e) => setQuality(e.target.value as any)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  >
                    <option value="standard">Standard</option>
                    <option value="hd">HD (Haute Définition)</option>
                    <option value="premium">Premium (Maximum)</option>
                  </select>
                </div>

              </div>
            </div>

            {/* Sélection de voix */}
            {(provider === 'openai' || provider === 'auto') && (
              <div className="bg-white rounded-xl shadow-lg p-6 border border-purple-100">
                <label className="block text-sm font-semibold text-gray-700 mb-3">
                  🎤 Voix OpenAI
                </label>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {OPENAI_VOICES.map((v) => (
                    <button
                      key={v.id}
                      onClick={() => setVoice(v.id)}
                      className={`p-3 rounded-lg border-2 transition text-left ${
                        voice === v.id
                          ? 'border-purple-600 bg-purple-50'
                          : 'border-gray-200 hover:border-purple-300'
                      }`}
                    >
                      <div className="font-semibold text-sm flex items-center space-x-1">
                        <span>{v.gender}</span>
                        <span>{v.name}</span>
                      </div>
                      <div className="text-xs text-gray-500 mt-1">{v.desc}</div>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {provider === 'elevenlabs' && (
              <div className="bg-white rounded-xl shadow-lg p-6 border border-purple-100">
                <label className="block text-sm font-semibold text-gray-700 mb-3">
                  👑 Voix ElevenLabs Premium
                </label>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {ELEVENLABS_VOICES.map((v) => (
                    <button
                      key={v.id}
                      onClick={() => setVoice(v.id)}
                      className={`p-3 rounded-lg border-2 transition text-left ${
                        voice === v.id
                          ? 'border-purple-600 bg-purple-50'
                          : 'border-gray-200 hover:border-purple-300'
                      }`}
                    >
                      <div className="font-semibold text-sm flex items-center space-x-1">
                        <span>{v.gender}</span>
                        <span>{v.name}</span>
                      </div>
                      <div className="text-xs text-gray-500 mt-1">{v.desc}</div>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Paramètres avancés */}
            <div className="bg-white rounded-xl shadow-lg p-6 border border-purple-100">
              <button
                onClick={() => setShowAdvanced(!showAdvanced)}
                className="flex items-center space-x-2 text-sm font-semibold text-gray-700 mb-4"
              >
                <Settings className="h-4 w-4" />
                <span>Paramètres Avancés</span>
                <span className="text-xs text-gray-500">({showAdvanced ? 'masquer' : 'afficher'})</span>
              </button>

              {showAdvanced && (
                <div className="space-y-4">
                  
                  {/* Vitesse (OpenAI) */}
                  {(provider === 'openai' || provider === 'auto') && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        ⚡ Vitesse: {speed.toFixed(2)}x
                      </label>
                      <input
                        type="range"
                        min="0.25"
                        max="4"
                        step="0.05"
                        value={speed}
                        onChange={(e) => setSpeed(parseFloat(e.target.value))}
                        className="w-full"
                      />
                      <div className="flex justify-between text-xs text-gray-500 mt-1">
                        <span>0.25x (Très lent)</span>
                        <span>1x (Normal)</span>
                        <span>4x (Très rapide)</span>
                      </div>
                    </div>
                  )}

                  {/* ElevenLabs avancé */}
                  {provider === 'elevenlabs' && (
                    <>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          🎚️ Stability: {stability.toFixed(2)}
                        </label>
                        <input
                          type="range"
                          min="0"
                          max="1"
                          step="0.01"
                          value={stability}
                          onChange={(e) => setStability(parseFloat(e.target.value))}
                          className="w-full"
                        />
                        <p className="text-xs text-gray-500 mt-1">Plus stable = voix constante</p>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          🔊 Similarity Boost: {similarityBoost.toFixed(2)}
                        </label>
                        <input
                          type="range"
                          min="0"
                          max="1"
                          step="0.01"
                          value={similarityBoost}
                          onChange={(e) => setSimilarityBoost(parseFloat(e.target.value))}
                          className="w-full"
                        />
                        <p className="text-xs text-gray-500 mt-1">Plus haut = voix plus fidèle</p>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          🎭 Style/Expression: {style.toFixed(2)}
                        </label>
                        <input
                          type="range"
                          min="0"
                          max="1"
                          step="0.01"
                          value={style}
                          onChange={(e) => setStyle(parseFloat(e.target.value))}
                          className="w-full"
                        />
                        <p className="text-xs text-gray-500 mt-1">Plus haut = plus expressif</p>
                      </div>
                    </>
                  )}

                </div>
              )}
            </div>

            {/* Bouton Générer */}
            <button
              onClick={generateAudio}
              disabled={loading || !text.trim()}
              className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white py-4 rounded-xl font-semibold text-lg shadow-lg hover:shadow-xl transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              {loading ? (
                <>
                  <Loader2 className="h-6 w-6 animate-spin" />
                  <span>Génération en cours...</span>
                </>
              ) : (
                <>
                  <Sparkles className="h-6 w-6" />
                  <span>Générer Audio Professionnel</span>
                </>
              )}
            </button>

          </div>

          {/* Panel droit - Lecteur & Métadonnées */}
          <div className="space-y-6">
            
            {/* Lecteur Audio */}
            <div className="bg-white rounded-xl shadow-lg p-6 border border-purple-100">
              <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
                <Volume2 className="h-5 w-5 text-purple-600" />
                <span>Lecteur Audio</span>
              </h3>

              {audioData ? (
                <div className="space-y-4">
                  <div className="bg-gradient-to-br from-purple-100 to-pink-100 rounded-lg p-8 flex items-center justify-center">
                    <button
                      onClick={togglePlay}
                      className="bg-white rounded-full p-6 shadow-lg hover:shadow-xl transition"
                    >
                      {isPlaying ? (
                        <Pause className="h-12 w-12 text-purple-600" />
                      ) : (
                        <Play className="h-12 w-12 text-purple-600" />
                      )}
                    </button>
                  </div>

                  <audio
                    ref={audioRef}
                    src={`data:audio/mpeg;base64,${audioData}`}
                    onEnded={() => setIsPlaying(false)}
                  />

                  <button
                    onClick={downloadAudio}
                    className="w-full bg-purple-600 text-white py-3 rounded-lg font-semibold flex items-center justify-center space-x-2 hover:bg-purple-700 transition"
                  >
                    <Download className="h-5 w-5" />
                    <span>Télécharger MP3</span>
                  </button>
                </div>
              ) : (
                <div className="bg-gray-50 rounded-lg p-8 text-center text-gray-400">
                  <Music className="h-16 w-16 mx-auto mb-4 opacity-50" />
                  <p>Générez un audio pour le voir ici</p>
                </div>
              )}
            </div>

            {/* Métadonnées */}
            {metadata && (
              <div className="bg-white rounded-xl shadow-lg p-6 border border-purple-100">
                <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
                  <Info className="h-5 w-5 text-purple-600" />
                  <span>Informations</span>
                </h3>
                
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Provider:</span>
                    <span className="font-semibold">{metadata.provider}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Voix:</span>
                    <span className="font-semibold">{metadata.voiceInfo.name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Genre:</span>
                    <span className="font-semibold">{metadata.voiceInfo.gender}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Modèle:</span>
                    <span className="font-semibold">{metadata.model}</span>
                  </div>
                  {metadata.speed && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Vitesse:</span>
                      <span className="font-semibold">{metadata.speed}x</span>
                    </div>
                  )}
                  <div className="flex justify-between">
                    <span className="text-gray-600">Taille:</span>
                    <span className="font-semibold">{(metadata.size / 1024).toFixed(1)} KB</span>
                  </div>
                  {metadata.duration && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Durée:</span>
                      <span className="font-semibold">{metadata.duration}s</span>
                    </div>
                  )}
                  
                  {metadata.settings && (
                    <div className="pt-3 border-t border-gray-200">
                      <div className="text-xs text-gray-500 mb-2">Paramètres ElevenLabs:</div>
                      {metadata.settings.stability && (
                        <div className="flex justify-between text-xs">
                          <span>Stability:</span>
                          <span>{metadata.settings.stability}</span>
                        </div>
                      )}
                      {metadata.settings.similarity_boost && (
                        <div className="flex justify-between text-xs">
                          <span>Similarity:</span>
                          <span>{metadata.settings.similarity_boost}</span>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Erreur */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700 text-sm">
                <strong>❌ Erreur:</strong> {error}
              </div>
            )}

          </div>

        </div>
      </div>
    </div>
  );
}
