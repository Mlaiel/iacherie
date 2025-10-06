'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { 
  Wand2, Mic, Image, FileText, Video, Music, Users, Trophy, 
  TrendingUp, Share2, ShoppingBag, Brain, Shield, Activity,
  Zap, Upload, Bell, GitBranch, Layers, Globe, Sparkles,
  Palette, MessageSquare, BarChart3, Target, Rocket, Crown
} from 'lucide-react';

interface FeatureCard {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  status: 'active' | 'partial' | 'coming-soon';
  progress: number;
  route?: string;
  category: 'creation' | 'collaboration' | 'business' | 'analytics' | 'infrastructure' | 'intelligence';
  apis: string[];
  features: string[];
}

export default function SuperDashboard() {
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  const features: FeatureCard[] = [
    // CRÉATION (100% Actifs)
    {
      id: 'audio-studio',
      title: '🎤 Audio Studio',
      description: '6 providers TTS, orchestration automatique, 644+ langues',
      icon: <Mic className="w-8 h-8" />,
      status: 'active',
      progress: 100,
      route: '/audio-studio',
      category: 'creation',
      apis: ['OpenAI TTS', 'ElevenLabs', 'Google TTS', 'Spotify', 'FreeSound', 'Shazam'],
      features: ['TTS Premium', 'Clonage voix', '100+ langues', 'Maestro Auto']
    },
    {
      id: 'text-studio',
      title: '📝 Text Studio',
      description: '5 LLMs, génération intelligente, multilingue',
      icon: <FileText className="w-8 h-8" />,
      status: 'active',
      progress: 100,
      route: '/text-studio',
      category: 'creation',
      apis: ['Gemini 2.5', 'GPT-4o', 'Claude Sonnet 4', 'Cohere', 'Mixtral'],
      features: ['Articles', 'Scripts', 'Emails', 'Posts sociaux']
    },
    {
      id: 'image-studio',
      title: '🎨 Image Studio',
      description: '6 providers, génération HD, styles multiples',
      icon: <Image className="w-8 h-8" />,
      status: 'active',
      progress: 100,
      route: '/image-studio',
      category: 'creation',
      apis: ['DALL-E 3', 'Leonardo', 'Replicate', 'Unsplash', 'Pexels', 'Freepik'],
      features: ['HD/4K', '10+ styles', 'Inpainting', 'Upscaling']
    },
    {
      id: 'video-studio',
      title: '🎬 Video Studio',
      description: '5 providers vidéo, IA + Stock + Hébergement',
      icon: <Video className="w-8 h-8" />,
      status: 'active',
      progress: 100,
      route: '/video-studio',
      category: 'creation',
      apis: ['RunwayML Gen-3', 'Pexels Video', 'Vimeo', 'Loom', 'YouTube'],
      features: ['IA Text-to-Video', 'Stock HD gratuit', 'Hébergement pro', 'Screen recording']
    },

    // AI LEADER AGENT (100% ACTIVE)
    {
      id: 'ai-leader',
      title: '🤖 AI Leader',
      description: 'Autonomous AI learning from all APIs to replace them',
      icon: <Brain className="w-8 h-8" />,
      status: 'active',
      progress: 100,
      route: '/ai-leader',
      category: 'intelligence',
      apis: ['Learning System', 'Internal Models', 'Auto-Training', 'Fallback Manager'],
      features: ['Learn from APIs', 'Auto-Fallback', 'Full Autonomy', '90% Cost Savings']
    },

    // REMIX & TRANSFORMATION (0% UI)
    {
      id: 'remix-studio',
      title: '🔄 Remix Studio',
      description: 'Transformer et remixer vos contenus existants',
      icon: <Layers className="w-8 h-8" />,
      status: 'coming-soon',
      progress: 0,
      route: '/remix-studio',
      category: 'creation',
      apis: ['RunwayML', 'Leonardo', 'OpenAI', 'ElevenLabs'],
      features: ['Mashup vidéo', 'Style transfer', 'Voice remix', 'Multi-sources']
    },

    // COLLABORATION (20% UI)
    {
      id: 'collaboration',
      title: '👥 Collaboration',
      description: 'Co-édition temps réel, commentaires, présence',
      icon: <Users className="w-8 h-8" />,
      status: 'partial',
      progress: 20,
      route: '/collaboration',
      category: 'collaboration',
      apis: ['WebSocket', 'Redis', 'Supabase'],
      features: ['Curseurs temps réel', 'Commentaires', 'Permissions', 'Locks']
    },
    {
      id: 'video-chat',
      title: '📹 Video Rooms',
      description: 'Visioconférence multi-participants avec screen share',
      icon: <Video className="w-8 h-8" />,
      status: 'partial',
      progress: 30,
      route: '/video-chat-rooms',
      category: 'collaboration',
      apis: ['Loom', 'Vimeo', 'Twilio'],
      features: ['Streaming HD', 'Screen share', 'Recording', 'Chat intégré']
    },

    // BUSINESS & MONÉTISATION (40% UI)
    {
      id: 'marketplace',
      title: '🛍️ Marketplace',
      description: 'Vendez vos créations, templates et services',
      icon: <ShoppingBag className="w-8 h-8" />,
      status: 'partial',
      progress: 40,
      route: '/marketplace',
      category: 'business',
      apis: ['Stripe (À configurer)', 'PayPal (À configurer)'],
      features: ['Vente contenus', 'Templates', 'Abonnements', 'Commission auto']
    },
    {
      id: 'distribution',
      title: '📤 Distribution',
      description: 'Publiez sur 10+ réseaux sociaux simultanément',
      icon: <Share2 className="w-8 h-8" />,
      status: 'partial',
      progress: 10,
      route: '/distribution',
      category: 'business',
      apis: ['YouTube', 'Facebook', 'Instagram', 'Twitter', 'Reddit'],
      features: ['Cross-posting', 'Scheduling', 'Analytics', 'Auto-format']
    },
    {
      id: 'ai-matching',
      title: '🧠 AI Matching',
      description: 'Matching créateurs-marques intelligent',
      icon: <Brain className="w-8 h-8" />,
      status: 'partial',
      progress: 60,
      route: '/ai-matching',
      category: 'business',
      apis: ['Pinecone', 'OpenAI', 'Algolia'],
      features: ['Score compatibilité', 'Recommendations', 'Audience analysis']
    },

    // GAMIFICATION (0% UI)
    {
      id: 'gamification',
      title: '🏆 Gamification',
      description: 'Points, badges, leaderboards, challenges',
      icon: <Trophy className="w-8 h-8" />,
      status: 'coming-soon',
      progress: 0,
      route: '/gamification',
      category: 'business',
      apis: ['Mixpanel', 'Supabase', 'Redis'],
      features: ['Badges', 'Niveaux', 'Leaderboards', 'Challenges', 'Trophées']
    },

    // ANALYTICS & SEO (30% UI)
    {
      id: 'seo-analytics',
      title: '📊 SEO & Analytics',
      description: 'Optimisation SEO automatique et analytics avancés',
      icon: <TrendingUp className="w-8 h-8" />,
      status: 'partial',
      progress: 30,
      route: '/seo-analytics',
      category: 'analytics',
      apis: ['Google Analytics', 'PageSpeed', 'TextRazor'],
      features: ['Audit SEO', 'Meta-tags', 'PageSpeed', 'Social previews']
    },
    {
      id: 'monitoring',
      title: '📈 Monitoring',
      description: 'Dashboard enterprise avec métriques temps réel',
      icon: <Activity className="w-8 h-8" />,
      status: 'active',
      progress: 100,
      route: '/enterprise-dashboard',
      category: 'analytics',
      apis: ['Custom', 'Sentry', 'Mixpanel'],
      features: ['Métriques live', 'Alertes', 'Logs', 'Performance']
    },

    // INFRASTRUCTURE (0-20% UI)
    {
      id: 'orchestration',
      title: '🎼 Maestro',
      description: 'Orchestration intelligente des 74 APIs',
      icon: <Wand2 className="w-8 h-8" />,
      status: 'active',
      progress: 100,
      route: '/ai-orchestrator',
      category: 'infrastructure',
      apis: ['74 APIs'],
      features: ['Sélection auto', '75-97% économies', 'Fallback', 'Quality scoring']
    },
    {
      id: 'multilingual',
      title: '🌍 Multilingue',
      description: '644+ langues et dialectes partout',
      icon: <Globe className="w-8 h-8" />,
      status: 'active',
      progress: 100,
      route: '/translation',
      category: 'infrastructure',
      apis: ['DeepL', 'Google Translate', 'LibreTranslate'],
      features: ['644+ langues', 'Auto-détection', 'Voix multilingues', 'Traduction temps réel']
    },
    {
      id: 'upload',
      title: '⬆️ Upload Manager',
      description: 'Upload massif avec tagging automatique IA',
      icon: <Upload className="w-8 h-8" />,
      status: 'partial',
      progress: 50,
      route: '/upload',
      category: 'infrastructure',
      apis: ['Supabase', 'Vision AI'],
      features: ['Drag & drop', 'Multi-upload', 'Auto-tag', 'CDN']
    },
    {
      id: 'notifications',
      title: '🔔 Notifications',
      description: 'Centre de notifications push temps réel',
      icon: <Bell className="w-8 h-8" />,
      status: 'coming-soon',
      progress: 20,
      route: '/notifications',
      category: 'infrastructure',
      apis: ['Supabase Realtime', 'Twilio', 'SendGrid (À configurer)'],
      features: ['Push', 'Email', 'SMS', 'Mentions', 'Alerts']
    },
    {
      id: 'security',
      title: '🛡️ Security',
      description: 'Détection de menaces et audit sécurité',
      icon: <Shield className="w-8 h-8" />,
      status: 'coming-soon',
      progress: 10,
      route: '/security',
      category: 'infrastructure',
      apis: ['Sentry', 'Custom threat detection'],
      features: ['Threat detection', 'IP blocking', 'Audit logs', 'RGPD']
    },
    {
      id: 'devops',
      title: '⚙️ DevOps',
      description: 'Monitoring CI/CD et déploiements',
      icon: <GitBranch className="w-8 h-8" />,
      status: 'coming-soon',
      progress: 0,
      route: '/devops',
      category: 'infrastructure',
      apis: ['GitHub Actions', 'Sentry'],
      features: ['CI/CD', 'Health checks', 'Logs', 'Rollback']
    },
    {
      id: 'ml-audio',
      title: '🎚️ ML Audio',
      description: 'Processing audio avancé avec ML',
      icon: <Music className="w-8 h-8" />,
      status: 'coming-soon',
      progress: 0,
      route: '/ml-audio',
      category: 'infrastructure',
      apis: ['Whisper', 'Custom ML'],
      features: ['Noise reduction', 'Enhancement', 'Transcription', 'Stems']
    },
    {
      id: 'performance',
      title: '⚡ Performance',
      description: 'Optimisation automatique des performances',
      icon: <Zap className="w-8 h-8" />,
      status: 'coming-soon',
      progress: 0,
      route: '/performance',
      category: 'infrastructure',
      apis: ['PageSpeed', 'Custom'],
      features: ['Lazy load', 'Code splitting', 'Cache', 'Lighthouse']
    }
  ];

  const categories = [
    { id: 'all', label: 'Toutes', icon: <Sparkles className="w-4 h-4" /> },
    { id: 'creation', label: 'Création', icon: <Palette className="w-4 h-4" /> },
    { id: 'collaboration', label: 'Collaboration', icon: <Users className="w-4 h-4" /> },
    { id: 'business', label: 'Business', icon: <Target className="w-4 h-4" /> },
    { id: 'analytics', label: 'Analytics', icon: <BarChart3 className="w-4 h-4" /> },
    { id: 'infrastructure', label: 'Infrastructure', icon: <Layers className="w-4 h-4" /> }
  ];

  const filteredFeatures = selectedCategory === 'all' 
    ? features 
    : features.filter(f => f.category === selectedCategory);

  const stats = {
    total: features.length,
    active: features.filter(f => f.status === 'active').length,
    partial: features.filter(f => f.status === 'partial').length,
    coming: features.filter(f => f.status === 'coming-soon').length,
    avgProgress: Math.round(features.reduce((sum, f) => sum + f.progress, 0) / features.length)
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-950 via-purple-900 to-pink-900 p-8">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-5xl font-bold text-white mb-2 flex items-center gap-3">
                <Crown className="w-12 h-12 text-yellow-400" />
                iAChérie Enterprise
              </h1>
              <p className="text-white/80 text-xl">74 APIs • 19 Fonctionnalités • 644+ Langues</p>
            </div>
            <div className="text-right">
              <div className="text-6xl font-bold text-white">{stats.avgProgress}%</div>
              <div className="text-white/60">Complétion Moyenne</div>
            </div>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-4 gap-4">
            <div className="bg-green-500/20 rounded-xl p-4 border border-green-500/30">
              <div className="text-3xl font-bold text-green-400">{stats.active}</div>
              <div className="text-green-300 text-sm">✅ Actives</div>
            </div>
            <div className="bg-yellow-500/20 rounded-xl p-4 border border-yellow-500/30">
              <div className="text-3xl font-bold text-yellow-400">{stats.partial}</div>
              <div className="text-yellow-300 text-sm">⚠️ Partielles</div>
            </div>
            <div className="bg-purple-500/20 rounded-xl p-4 border border-purple-500/30">
              <div className="text-3xl font-bold text-purple-400">{stats.coming}</div>
              <div className="text-purple-300 text-sm">🚀 Bientôt</div>
            </div>
            <div className="bg-blue-500/20 rounded-xl p-4 border border-blue-500/30">
              <div className="text-3xl font-bold text-blue-400">{stats.total}</div>
              <div className="text-blue-300 text-sm">📊 Total</div>
            </div>
          </div>
        </div>
      </div>

      {/* Category Filter */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="flex gap-3 flex-wrap">
          {categories.map(cat => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              className={`px-6 py-3 rounded-xl font-medium transition-all flex items-center gap-2 ${
                selectedCategory === cat.id
                  ? 'bg-white text-purple-900 shadow-lg scale-105'
                  : 'bg-white/10 text-white hover:bg-white/20 border border-white/20'
              }`}
            >
              {cat.icon}
              {cat.label}
            </button>
          ))}
        </div>
      </div>

      {/* Features Grid */}
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredFeatures.map(feature => (
            <div
              key={feature.id}
              className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 hover:border-white/40 transition-all hover:scale-105 relative overflow-hidden"
            >
              {/* Status Badge */}
              <div className="absolute top-4 right-4">
                {feature.status === 'active' && (
                  <span className="px-3 py-1 bg-green-500/20 text-green-300 rounded-full text-xs font-bold border border-green-500/30">
                    ✅ ACTIF
                  </span>
                )}
                {feature.status === 'partial' && (
                  <span className="px-3 py-1 bg-yellow-500/20 text-yellow-300 rounded-full text-xs font-bold border border-yellow-500/30">
                    ⚠️ PARTIEL
                  </span>
                )}
                {feature.status === 'coming-soon' && (
                  <span className="px-3 py-1 bg-purple-500/20 text-purple-300 rounded-full text-xs font-bold border border-purple-500/30">
                    🚀 BIENTÔT
                  </span>
                )}
              </div>

              {/* Icon */}
              <div className="text-white mb-4">
                {feature.icon}
              </div>

              {/* Title & Description */}
              <h3 className="text-2xl font-bold text-white mb-2">{feature.title}</h3>
              <p className="text-white/70 mb-4 text-sm">{feature.description}</p>

              {/* Progress Bar */}
              <div className="mb-4">
                <div className="flex justify-between text-xs text-white/60 mb-1">
                  <span>Complétion</span>
                  <span>{feature.progress}%</span>
                </div>
                <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                  <div 
                    className={`h-full transition-all ${
                      feature.progress === 100 ? 'bg-green-500' :
                      feature.progress >= 50 ? 'bg-yellow-500' :
                      'bg-purple-500'
                    }`}
                    style={{ width: `${feature.progress}%` }}
                  />
                </div>
              </div>

              {/* APIs */}
              <div className="mb-4">
                <div className="text-xs text-white/60 mb-2">APIs ({feature.apis.length})</div>
                <div className="flex flex-wrap gap-2">
                  {feature.apis.slice(0, 3).map((api, i) => (
                    <span key={i} className="px-2 py-1 bg-blue-500/20 text-blue-300 rounded text-xs border border-blue-500/30">
                      {api}
                    </span>
                  ))}
                  {feature.apis.length > 3 && (
                    <span className="px-2 py-1 bg-white/10 text-white/60 rounded text-xs">
                      +{feature.apis.length - 3}
                    </span>
                  )}
                </div>
              </div>

              {/* Features */}
              <div className="mb-4">
                <div className="text-xs text-white/60 mb-2">Fonctionnalités</div>
                <div className="space-y-1">
                  {feature.features.slice(0, 3).map((feat, i) => (
                    <div key={i} className="text-xs text-white/80 flex items-center gap-2">
                      <div className="w-1 h-1 bg-white/60 rounded-full" />
                      {feat}
                    </div>
                  ))}
                </div>
              </div>

              {/* Action Button */}
              {feature.route ? (
                <Link
                  href={feature.route}
                  className={`block text-center py-3 rounded-xl font-bold transition-all ${
                    feature.status === 'active'
                      ? 'bg-green-500 hover:bg-green-600 text-white'
                      : feature.status === 'partial'
                      ? 'bg-yellow-500 hover:bg-yellow-600 text-white'
                      : 'bg-purple-500 hover:bg-purple-600 text-white'
                  }`}
                >
                  {feature.status === 'active' ? '🚀 Ouvrir' :
                   feature.status === 'partial' ? '👀 Voir démo' :
                   '⏳ Bientôt disponible'}
                </Link>
              ) : (
                <div className="text-center py-3 rounded-xl font-bold bg-white/5 text-white/40 border border-white/10">
                  En développement
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Footer CTA */}
      <div className="max-w-7xl mx-auto mt-12">
        <div className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 backdrop-blur-lg rounded-2xl p-8 border border-white/20 text-center">
          <Rocket className="w-16 h-16 text-white mx-auto mb-4" />
          <h2 className="text-3xl font-bold text-white mb-2">
            19 Fonctionnalités Entreprise
          </h2>
          <p className="text-white/80 text-xl mb-6">
            Infrastructure complète • 74 APIs • Orchestration IA • Multilingue
          </p>
          <div className="flex gap-4 justify-center">
            <Link
              href="/enterprise-dashboard"
              className="px-8 py-4 bg-white text-purple-900 rounded-xl font-bold hover:scale-105 transition-all"
            >
              📊 Dashboard Enterprise
            </Link>
            <Link
              href="/ai-orchestrator"
              className="px-8 py-4 bg-purple-500 text-white rounded-xl font-bold hover:scale-105 transition-all"
            >
              🎼 Maestro Orchestrator
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
