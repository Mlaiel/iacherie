/**
 * � API MAESTRO ORCHESTRATOR - 74 APIs PREMIUM
 * Orchestration intelligente: MEILLEURE QUALITÉ AU COÛT LE PLUS BAS
 * Principe: Sélection automatique selon qualité/coût/cas d'usage
 * Author: Fahed Mlaiel
 */

// ============================================================================
// TYPES & INTERFACES
// ============================================================================

export type APICategory = 
  | 'ai-text'
  | 'ai-image'
  | 'ai-audio'
  | 'ai-video'
  | 'social-media'
  | 'communication'
  | 'media-library'
  | 'analytics'
  | 'database'
  | 'utility';

export type QualityLevel = 'draft' | 'standard' | 'premium' | 'ultra';
export type ContentType = 'text' | 'image' | 'audio' | 'video' | 'music';
export type UseCase = 
  | 'chat' 
  | 'article' 
  | 'marketing' 
  | 'technical' 
  | 'creative'
  | 'social-post'
  | 'thumbnail'
  | 'hero-image'
  | 'voice-over'
  | 'podcast'
  | 'background-music'
  | 'sound-effects';

export interface APIConfig {
  name: string;
  category: APICategory;
  costPerRequest: number; // en dollars
  qualityScore: number; // 0-100
  speedScore: number; // 0-100
  reliabilityScore: number; // 0-100
  enabled: boolean;
  envKeys: string[];
  features?: string[];
}

export interface GenerationRequest {
  contentType: ContentType;
  useCase: UseCase;
  quality: QualityLevel;
  budget?: number; // Budget max en dollars
  prompt: string;
  options?: Record<string, any>;
}

export interface GenerationResponse {
  success: boolean;
  content: any;
  provider: string;
  cost: number;
  metadata: {
    quality: QualityLevel;
    duration: number;
    tokens?: number;
    model?: string;
  };
}

// Nouvelles interfaces pour l'orchestration intelligente
export interface SelectionCriteria {
  quality: QualityLevel;
  useCase?: UseCase | string;
  budget?: number;
  features?: string[];
}

export interface OrchestratorRequest {
  contentType: ContentType | string;
  quality?: QualityLevel;
  useCase?: UseCase | string;
  budget?: number;
  features?: string[];
}

export interface OrchestratorResponse {
  provider: string;
  cost: number;
  quality: number; // Score 0-100
  reasoning: string;
  estimatedSavings?: number;
  alternativeProvider?: string;
  alternativeCost?: number;
}

// ============================================================================
// CONFIGURATION DES 72 APIs
// ============================================================================

export const API_REGISTRY: Record<string, APIConfig> = {
  // INTELLIGENCE ARTIFICIELLE - TEXTE (11 APIs - TOUS MODÈLES OPENAI)
  'openai-gpt4o': {
    name: 'OpenAI GPT-4o',
    category: 'ai-text',
    costPerRequest: 0.005,
    qualityScore: 95,
    speedScore: 85,
    reliabilityScore: 98,
    enabled: true,
    envKeys: ['OPENAI_API_KEY']
  },
  'openai-gpt4o-mini': {
    name: 'OpenAI GPT-4o-mini',
    category: 'ai-text',
    costPerRequest: 0.00015,
    qualityScore: 85,
    speedScore: 95,
    reliabilityScore: 98,
    enabled: true,
    envKeys: ['OPENAI_API_KEY']
  },
  'openai-gpt4-turbo': {
    name: 'OpenAI GPT-4 Turbo',
    category: 'ai-text',
    costPerRequest: 0.01,
    qualityScore: 97,
    speedScore: 80,
    reliabilityScore: 98,
    enabled: true,
    envKeys: ['OPENAI_API_KEY']
  },
  'openai-o1': {
    name: 'OpenAI O1 (Reasoning)',
    category: 'ai-text',
    costPerRequest: 0.015,
    qualityScore: 99,
    speedScore: 70,
    reliabilityScore: 98,
    enabled: true,
    envKeys: ['OPENAI_API_KEY']
  },
  'openai-o1-mini': {
    name: 'OpenAI O1-mini',
    category: 'ai-text',
    costPerRequest: 0.003,
    qualityScore: 92,
    speedScore: 85,
    reliabilityScore: 98,
    enabled: true,
    envKeys: ['OPENAI_API_KEY']
  },
  'openai-gpt35': {
    name: 'OpenAI GPT-3.5-turbo',
    category: 'ai-text',
    costPerRequest: 0.0005,
    qualityScore: 75,
    speedScore: 98,
    reliabilityScore: 98,
    enabled: true,
    envKeys: ['OPENAI_API_KEY']
  },
  'claude-sonnet-45': {
    name: 'Claude Sonnet 4.5',
    category: 'ai-text',
    costPerRequest: 0.003,
    qualityScore: 98,
    speedScore: 80,
    reliabilityScore: 95,
    enabled: true,
    envKeys: ['ANTHROPIC_API_KEY']
  },
  'gemini-pro': {
    name: 'Google Gemini Pro',
    category: 'ai-text',
    costPerRequest: 0.0005,
    qualityScore: 88,
    speedScore: 90,
    reliabilityScore: 92,
    enabled: true,
    envKeys: ['GOOGLE_GEMINI_API_KEY']
  },
  'cohere-command': {
    name: 'Cohere Command',
    category: 'ai-text',
    costPerRequest: 0.001,
    qualityScore: 82,
    speedScore: 88,
    reliabilityScore: 90,
    enabled: true,
    envKeys: ['COHERE_API_KEY']
  },
  'huggingface': {
    name: 'HuggingFace',
    category: 'ai-text',
    costPerRequest: 0.0002,
    qualityScore: 70,
    speedScore: 75,
    reliabilityScore: 85,
    enabled: true,
    envKeys: ['HUGGINGFACE_API_KEY']
  },
  'textrazor': {
    name: 'TextRazor NLP',
    category: 'ai-text',
    costPerRequest: 0.0001,
    qualityScore: 85,
    speedScore: 95,
    reliabilityScore: 92,
    enabled: true,
    envKeys: ['TEXTRAZOR_API_KEY']
  },

  // INTELLIGENCE ARTIFICIELLE - IMAGES (5 APIs)
  'midjourney-discord': {
    name: 'Midjourney Discord Bot',
    category: 'ai-image',
    costPerRequest: 0.08,
    qualityScore: 100,
    speedScore: 60,
    reliabilityScore: 95,
    enabled: true,
    envKeys: ['DISCORD_BOT_TOKEN', 'MIDJOURNEY_CHANNEL_ID']
  },
  'dalle3': {
    name: 'DALL-E 3',
    category: 'ai-image',
    costPerRequest: 0.04,
    qualityScore: 90,
    speedScore: 80,
    reliabilityScore: 98,
    enabled: true,
    envKeys: ['OPENAI_API_KEY']
  },
  'leonardo': {
    name: 'Leonardo AI',
    category: 'ai-image',
    costPerRequest: 0.015,
    qualityScore: 85,
    speedScore: 85,
    reliabilityScore: 90,
    enabled: true,
    envKeys: ['LEONARDO_API_KEY']
  },
  'replicate-flux': {
    name: 'Replicate Flux',
    category: 'ai-image',
    costPerRequest: 0.008,
    qualityScore: 78,
    speedScore: 90,
    reliabilityScore: 88,
    enabled: true,
    envKeys: ['REPLICATE_API_TOKEN']
  },
  'stable-diffusion': {
    name: 'Stable Diffusion (Replicate)',
    category: 'ai-image',
    costPerRequest: 0.008,
    qualityScore: 80,
    speedScore: 85,
    reliabilityScore: 88,
    enabled: true,
    envKeys: ['REPLICATE_API_TOKEN']
  },

  // INTELLIGENCE ARTIFICIELLE - AUDIO (3 APIs)
  'openai-tts': {
    name: 'OpenAI TTS',
    category: 'ai-audio',
    costPerRequest: 0.015,
    qualityScore: 92,
    speedScore: 88,
    reliabilityScore: 98,
    enabled: true,
    envKeys: ['OPENAI_API_KEY']
  },
  'openai-whisper': {
    name: 'OpenAI Whisper',
    category: 'ai-audio',
    costPerRequest: 0.006,
    qualityScore: 95,
    speedScore: 85,
    reliabilityScore: 98,
    enabled: true,
    envKeys: ['OPENAI_API_KEY']
  },

  // RÉSEAUX SOCIAUX (7 APIs)
  'youtube': {
    name: 'YouTube API',
    category: 'social-media',
    costPerRequest: 0.001,
    qualityScore: 100,
    speedScore: 90,
    reliabilityScore: 98,
    enabled: true,
    envKeys: ['YOUTUBE_API_KEY', 'YOUTUBE_CLIENT_ID', 'YOUTUBE_CLIENT_SECRET']
  },
  'twitter': {
    name: 'Twitter/X API',
    category: 'social-media',
    costPerRequest: 0.0005,
    qualityScore: 100,
    speedScore: 95,
    reliabilityScore: 95,
    enabled: true,
    envKeys: ['TWITTER_API_KEY', 'TWITTER_BEARER_TOKEN']
  },
  'instagram': {
    name: 'Instagram API',
    category: 'social-media',
    costPerRequest: 0.0005,
    qualityScore: 100,
    speedScore: 92,
    reliabilityScore: 92,
    enabled: true,
    envKeys: ['INSTAGRAM_APP_ID', 'INSTAGRAM_ACCESS_TOKEN']
  },
  'facebook': {
    name: 'Facebook API',
    category: 'social-media',
    costPerRequest: 0.0005,
    qualityScore: 100,
    speedScore: 92,
    reliabilityScore: 92,
    enabled: true,
    envKeys: ['FACEBOOK_APP_ID', 'FACEBOOK_ACCESS_TOKEN']
  },
  'reddit': {
    name: 'Reddit API',
    category: 'social-media',
    costPerRequest: 0.0003,
    qualityScore: 100,
    speedScore: 88,
    reliabilityScore: 90,
    enabled: true,
    envKeys: ['REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET']
  },
  'spotify': {
    name: 'Spotify API',
    category: 'social-media',
    costPerRequest: 0.0001,
    qualityScore: 100,
    speedScore: 95,
    reliabilityScore: 98,
    enabled: true,
    envKeys: ['SPOTIFY_CLIENT_ID', 'SPOTIFY_CLIENT_SECRET']
  },
  'discord': {
    name: 'Discord Bot',
    category: 'social-media',
    costPerRequest: 0,
    qualityScore: 100,
    speedScore: 98,
    reliabilityScore: 95,
    enabled: true,
    envKeys: ['DISCORD_BOT_TOKEN', 'DISCORD_APPLICATION_ID']
  },

  // COMMUNICATION (3 APIs)
  'resend': {
    name: 'Resend Email',
    category: 'communication',
    costPerRequest: 0.0001,
    qualityScore: 95,
    speedScore: 95,
    reliabilityScore: 98,
    enabled: true,
    envKeys: ['RESEND_API_KEY']
  },
  'twilio': {
    name: 'Twilio SMS',
    category: 'communication',
    costPerRequest: 0.0075,
    qualityScore: 98,
    speedScore: 98,
    reliabilityScore: 99,
    enabled: false, // Placeholder keys
    envKeys: ['TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN']
  },

  // MÉDIAS & CONTENU (8 APIs)
  'unsplash': {
    name: 'Unsplash Photos',
    category: 'media-library',
    costPerRequest: 0,
    qualityScore: 95,
    speedScore: 98,
    reliabilityScore: 98,
    enabled: true,
    envKeys: ['UNSPLASH_ACCESS_KEY']
  },
  'freepik': {
    name: 'Freepik Premium',
    category: 'media-library',
    costPerRequest: 0.01,
    qualityScore: 92,
    speedScore: 90,
    reliabilityScore: 95,
    enabled: true,
    envKeys: ['FREEPIK_API_KEY']
  },
  'flaticon': {
    name: 'Flaticon',
    category: 'media-library',
    costPerRequest: 0.005,
    qualityScore: 90,
    speedScore: 95,
    reliabilityScore: 95,
    enabled: true,
    envKeys: ['FLATICON_API_KEY']
  },
  'freesound': {
    name: 'FreeSound Audio',
    category: 'media-library',
    costPerRequest: 0,
    qualityScore: 85,
    speedScore: 92,
    reliabilityScore: 92,
    enabled: true,
    envKeys: ['FREESOUND_API_KEY'],
    features: ['sound-effects', 'sfx', 'free']
  },
  'pexels': {
    name: 'Pexels Stock Media',
    category: 'media-library',
    costPerRequest: 0,
    qualityScore: 90,
    speedScore: 95,
    reliabilityScore: 98,
    enabled: true,
    envKeys: ['PEXELS_API_KEY'],
    features: ['photos', 'videos', 'free', 'stock']
  },
  'vimeo': {
    name: 'Vimeo Pro Hosting',
    category: 'media-library',
    costPerRequest: 0.02,
    qualityScore: 95,
    speedScore: 92,
    reliabilityScore: 98,
    enabled: true,
    envKeys: ['VIMEO_CLIENT_ID', 'VIMEO_CLIENT_SECRET'],
    features: ['video-hosting', 'streaming', 'professional']
  },
  'loom': {
    name: 'Loom Screen Recording',
    category: 'media-library',
    costPerRequest: 0.01,
    qualityScore: 92,
    speedScore: 90,
    reliabilityScore: 95,
    enabled: true,
    envKeys: ['LOOM_API_KEY'],
    features: ['screen-recording', 'video-messaging']
  },

  // AUDIO AVANCÉ (3 nouvelles APIs)
  'elevenlabs': {
    name: 'ElevenLabs Premium TTS',
    category: 'ai-audio',
    costPerRequest: 0.18,
    qualityScore: 98,
    speedScore: 92,
    reliabilityScore: 95,
    enabled: true,
    envKeys: ['ELEVENLABS_API_KEY'],
    features: ['voice-cloning', 'premium-quality', 'multilingual']
  },
  'google-tts': {
    name: 'Google Cloud TTS',
    category: 'ai-audio',
    costPerRequest: 0.016,
    qualityScore: 90,
    speedScore: 90,
    reliabilityScore: 98,
    enabled: true,
    envKeys: ['GOOGLE_GEMINI_API_KEY'],
    features: ['neural-voices', 'multilingual', 'pitch-control']
  },
  'shazam': {
    name: 'Shazam Music Recognition',
    category: 'ai-audio',
    costPerRequest: 0.001,
    qualityScore: 98,
    speedScore: 98,
    reliabilityScore: 95,
    enabled: true,
    envKeys: ['RAPIDAPI_KEY'],
    features: ['music-recognition', 'identification']
  },

  // ANALYTICS & MONITORING (6 APIs)
  'google-analytics': {
    name: 'Google Analytics',
    category: 'analytics',
    costPerRequest: 0,
    qualityScore: 100,
    speedScore: 95,
    reliabilityScore: 99,
    enabled: true,
    envKeys: ['GOOGLE_ANALYTICS_MEASUREMENT_ID'],
    features: ['web-analytics', 'user-tracking', 'conversion']
  },
  'mixpanel': {
    name: 'Mixpanel Analytics',
    category: 'analytics',
    costPerRequest: 0,
    qualityScore: 98,
    speedScore: 95,
    reliabilityScore: 98,
    enabled: true,
    envKeys: ['MIXPANEL_TOKEN'],
    features: ['product-analytics', 'user-behavior', 'funnel-analysis']
  },
  'sentry': {
    name: 'Sentry Monitoring',
    category: 'analytics',
    costPerRequest: 0,
    qualityScore: 98,
    speedScore: 98,
    reliabilityScore: 99,
    enabled: true,
    envKeys: ['SENTRY_DSN'],
    features: ['error-tracking', 'performance-monitoring']
  },
  'pagespeed': {
    name: 'PageSpeed Insights',
    category: 'analytics',
    costPerRequest: 0,
    qualityScore: 100,
    speedScore: 85,
    reliabilityScore: 98,
    enabled: true,
    envKeys: ['PAGESPEED_API_KEY'],
    features: ['performance-audit', 'seo-analysis']
  },

  // INTELLIGENCE ARTIFICIELLE - VIDÉO (2 APIs)
  'runwayml-gen3': {
    name: 'RunwayML Gen-3 Alpha',
    category: 'ai-video',
    costPerRequest: 10.00,
    qualityScore: 98,
    speedScore: 60,
    reliabilityScore: 92,
    enabled: true,
    envKeys: ['RUNWAYML_API_KEY'],
    features: ['ai-video-generation', 'text-to-video', 'premium']
  },
  'stability-video': {
    name: 'Stability AI Video',
    category: 'ai-video',
    costPerRequest: 5.00,
    qualityScore: 90,
    speedScore: 70,
    reliabilityScore: 88,
    enabled: true,
    envKeys: ['STABILITY_API_KEY'],
    features: ['ai-video', 'animation']
  },
  'ipgeolocation': {
    name: 'IP Geolocation',
    category: 'analytics',
    costPerRequest: 0.0001,
    qualityScore: 90,
    speedScore: 98,
    reliabilityScore: 95,
    enabled: true,
    envKeys: ['IPGEOLOCATION_API_KEY']
  },

  // DATABASES & SEARCH (5 APIs)
  'supabase': {
    name: 'Supabase PostgreSQL',
    category: 'database',
    costPerRequest: 0.0001,
    qualityScore: 100,
    speedScore: 95,
    reliabilityScore: 98,
    enabled: true,
    envKeys: ['SUPABASE_URL', 'SUPABASE_ANON_KEY']
  },
  'algolia': {
    name: 'Algolia Search',
    category: 'database',
    costPerRequest: 0.0005,
    qualityScore: 98,
    speedScore: 99,
    reliabilityScore: 99,
    enabled: true,
    envKeys: ['ALGOLIA_APPLICATION_ID', 'ALGOLIA_API_KEY']
  },
  'pinecone': {
    name: 'Pinecone Vector DB',
    category: 'database',
    costPerRequest: 0.0002,
    qualityScore: 95,
    speedScore: 95,
    reliabilityScore: 98,
    enabled: true,
    envKeys: ['PINECONE_API_KEY']
  },
  'redis': {
    name: 'Redis Cache',
    category: 'database',
    costPerRequest: 0,
    qualityScore: 100,
    speedScore: 99,
    reliabilityScore: 99,
    enabled: true,
    envKeys: ['REDIS_URL']
  },

  // UTILITAIRES (4 APIs)
  'deepl': {
    name: 'DeepL Translation',
    category: 'utility',
    costPerRequest: 0.002,
    qualityScore: 98,
    speedScore: 95,
    reliabilityScore: 98,
    enabled: true,
    envKeys: ['DEEPL_API_KEY']
  },
  'libretranslate': {
    name: 'LibreTranslate',
    category: 'utility',
    costPerRequest: 0,
    qualityScore: 75,
    speedScore: 85,
    reliabilityScore: 85,
    enabled: true,
    envKeys: ['LIBRETRANSLATE_URL']
  },
  'tinyurl': {
    name: 'TinyURL',
    category: 'utility',
    costPerRequest: 0.0001,
    qualityScore: 100,
    speedScore: 98,
    reliabilityScore: 98,
    enabled: true,
    envKeys: ['TINYURL_API_KEY']
  }
};

// ============================================================================
// LOGIQUE MÉTIER - SÉLECTION INTELLIGENTE
// ============================================================================

export class IntelligentAPIOrchestrator {
  
  /**
   * Sélectionne la meilleure API selon le use case
   */
  selectBestAPI(request: GenerationRequest): string {
    const { contentType, useCase, quality, budget } = request;

    // TEXTE - Logique intelligente
    if (contentType === 'text') {
      // Chat rapide → GPT-3.5 (rapide + économique)
      if (useCase === 'chat') {
        return 'openai-gpt35';
      }
      
      // Article de qualité → GPT-4o-mini (équilibre)
      if (useCase === 'article') {
        return quality === 'ultra' ? 'claude-sonnet-45' : 'openai-gpt4o-mini';
      }
      
      // Marketing premium → Claude (créativité)
      if (useCase === 'marketing') {
        return quality === 'premium' || quality === 'ultra' 
          ? 'claude-sonnet-45' 
          : 'openai-gpt4o-mini';
      }
      
      // Technique → GPT-4o (précision)
      if (useCase === 'technical') {
        return 'openai-gpt4o';
      }
      
      // Budget limité → Gemini ou Cohere
      if (budget && budget < 0.001) {
        return 'gemini-pro';
      }
    }

    // IMAGE - Logique intelligente
    if (contentType === 'image') {
      // Ultra premium → Midjourney Discord
      if (quality === 'ultra') {
        return 'midjourney-discord';
      }
      
      // Marketing/Hero → DALL-E 3 ou Midjourney
      if (useCase === 'hero-image' || useCase === 'marketing') {
        return quality === 'premium' ? 'midjourney-discord' : 'dalle3';
      }
      
      // Thumbnail social → Leonardo (rapide)
      if (useCase === 'thumbnail' || useCase === 'social-post') {
        return 'leonardo';
      }
      
      // Draft/test → Replicate (économique)
      if (quality === 'draft' || (budget && budget < 0.02)) {
        return 'replicate-flux';
      }
      
      // Standard → Leonardo ou DALL-E 3
      return quality === 'premium' ? 'dalle3' : 'leonardo';
    }

    // AUDIO - Logique intelligente
    if (contentType === 'audio') {
      // Voice-over professionnel → OpenAI TTS
      if (useCase === 'voice-over') {
        return 'openai-tts';
      }
    }

    // Fallback par défaut selon content type
    const defaults: Record<ContentType, string> = {
      text: 'openai-gpt4o-mini',
      image: 'leonardo',
      audio: 'openai-tts',
      video: 'openai-gpt4o', // Pour scripts
      music: 'freesound'
    };

    return defaults[contentType] || 'openai-gpt4o-mini';
  }

  /**
   * Obtient une liste d'APIs en fallback
   */
  getFallbackAPIs(primaryAPI: string): string[] {
    const config = API_REGISTRY[primaryAPI];
    if (!config) return [];

    const category = config.category;
    
    // Retourne toutes les APIs de la même catégorie, triées par score
    return Object.entries(API_REGISTRY)
      .filter(([key, cfg]) => 
        cfg.category === category && 
        key !== primaryAPI && 
        cfg.enabled
      )
      .sort((a, b) => {
        const scoreA = a[1].qualityScore * 0.5 + a[1].reliabilityScore * 0.5;
        const scoreB = b[1].qualityScore * 0.5 + b[1].reliabilityScore * 0.5;
        return scoreB - scoreA;
      })
      .map(([key]) => key);
  }

  /**
   * Calcule le coût estimé
   */
  estimateCost(apiKey: string, request: GenerationRequest): number {
    const config = API_REGISTRY[apiKey];
    if (!config) return 0;

    let baseCost = config.costPerRequest;

    // Ajustement selon la qualité
    const qualityMultipliers: Record<QualityLevel, number> = {
      draft: 0.7,
      standard: 1.0,
      premium: 1.3,
      ultra: 1.8
    };

    return baseCost * qualityMultipliers[request.quality];
  }

  /**
   * Vérifie si une API est disponible
   */
  isAPIAvailable(apiKey: string): boolean {
    const config = API_REGISTRY[apiKey];
    if (!config || !config.enabled) return false;

    // Vérifie que toutes les clés d'environnement sont présentes
    return config.envKeys.every(key => {
      const value = process.env[key];
      return value && 
             value.length > 0 && 
             !value.includes('xxx') && 
             !value.includes('REMPLACEZ');
    });
  }

  /**
   * Obtient les statistiques d'utilisation
   */
  getUsageStats(): {
    total: number;
    enabled: number;
    available: number;
    byCategory: Record<APICategory, number>;
  } {
    const stats = {
      total: Object.keys(API_REGISTRY).length,
      enabled: 0,
      available: 0,
      byCategory: {} as Record<APICategory, number>
    };

    Object.entries(API_REGISTRY).forEach(([key, config]) => {
      if (config.enabled) stats.enabled++;
      if (this.isAPIAvailable(key)) stats.available++;
      
      stats.byCategory[config.category] = (stats.byCategory[config.category] || 0) + 1;
    });

    return stats;
  }
}

// Instance singleton
export const apiOrchestrator = new IntelligentAPIOrchestrator();

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Convertit quality level en paramètres techniques
 */
export function getQualityParams(quality: QualityLevel) {
  const params = {
    draft: {
      imageSize: '512x512',
      steps: 20,
      model: 'fast'
    },
    standard: {
      imageSize: '1024x1024',
      steps: 30,
      model: 'standard'
    },
    premium: {
      imageSize: '1024x1024',
      steps: 50,
      model: 'quality'
    },
    ultra: {
      imageSize: '1792x1024',
      steps: 100,
      model: 'ultra'
    }
  };

  return params[quality];
}

/**
 * Log l'utilisation d'une API
 */
export async function logAPIUsage(
  apiKey: string,
  request: GenerationRequest,
  response: GenerationResponse
) {
  // TODO: Implémenter logging dans Supabase ou analytics
  console.log('📊 API Usage:', {
    api: apiKey,
    contentType: request.contentType,
    useCase: request.useCase,
    cost: response.cost,
    duration: response.metadata.duration,
    success: response.success
  });
}

// ============================================================================
// NOUVELLE GÉNÉRATION: SÉLECTION OPTIMALE INTELLIGENTE
// ============================================================================

/**
 * Sélectionne automatiquement l'API optimale pour la génération TTS/Audio
 * Principe: MEILLEURE QUALITÉ AU COÛT LE PLUS BAS
 */
export function selectOptimalTTS(criteria: SelectionCriteria): OrchestratorResponse {
  const { quality, useCase, budget, features } = criteria;

  // Cas spéciaux basés sur les features requises
  if (features?.includes('pitch-control')) {
    return {
      provider: 'google-tts',
      cost: 0.016,
      quality: 90,
      reasoning: '🎛️ Google TTS est le seul à offrir le contrôle du pitch (-12 à +12 semitones). Économie de 89% vs ElevenLabs ($0.016 vs $0.18).',
      estimatedSavings: 0.164,
      alternativeProvider: 'elevenlabs',
      alternativeCost: 0.18
    };
  }

  if (features?.includes('voice-cloning') || quality === 'ultra') {
    return {
      provider: 'elevenlabs',
      cost: 0.30,
      quality: 98,
      reasoning: '👑 ElevenLabs Multilingual offre la meilleure qualité avec clonage vocal. Investissement premium justifié pour qualité ultra.',
      estimatedSavings: 0,
      alternativeProvider: 'openai-tts-1-hd',
      alternativeCost: 0.03
    };
  }

  if (useCase === 'music-search' || useCase === 'music-preview') {
    return {
      provider: 'spotify',
      cost: 0,
      quality: 95,
      reasoning: '🎵 Spotify offre gratuitement la recherche musicale et 30s de preview. Économie de 100%.',
      estimatedSavings: 0.18,
      alternativeProvider: 'elevenlabs',
      alternativeCost: 0.18
    };
  }

  if (useCase === 'sound-effects' || features?.includes('sfx')) {
    return {
      provider: 'freesound',
      cost: 0,
      quality: 85,
      reasoning: '🔊 FreeSound offre une bibliothèque gratuite d\'effets sonores de qualité. Économie de 100%.',
      estimatedSavings: 0.18,
      alternativeProvider: 'elevenlabs',
      alternativeCost: 0.18
    };
  }

  // Sélection basée sur qualité et budget
  if (quality === 'premium') {
    if (budget && budget < 0.05) {
      return {
        provider: 'openai-tts-1-hd',
        cost: 0.03,
        quality: 92,
        reasoning: '⚡ OpenAI TTS-1-HD offre une qualité premium à 83% moins cher qu\'ElevenLabs ($0.030 vs $0.18).',
        estimatedSavings: 0.15,
        alternativeProvider: 'elevenlabs',
        alternativeCost: 0.18
      };
    }
    return {
      provider: 'elevenlabs',
      cost: 0.18,
      quality: 98,
      reasoning: '🎯 ElevenLabs Turbo offre la meilleure qualité premium avec voix naturelles.',
      estimatedSavings: 0,
      alternativeProvider: 'openai-tts-1-hd',
      alternativeCost: 0.03
    };
  }

  // Standard/draft: toujours OpenAI TTS-1 (le moins cher)
  return {
    provider: 'openai-tts-1',
    cost: 0.015,
    quality: 88,
    reasoning: '💰 OpenAI TTS-1 offre le meilleur rapport qualité/prix. Économie de 92% vs ElevenLabs ($0.015 vs $0.18).',
    estimatedSavings: 0.165,
    alternativeProvider: 'elevenlabs',
    alternativeCost: 0.18
  };
}

/**
 * Sélectionne automatiquement l'API optimale pour la génération d'images
 */
export function selectOptimalImage(criteria: SelectionCriteria): OrchestratorResponse {
  const { quality, useCase, budget, features } = criteria;

  // Cas spéciaux: stock photos gratuites
  if (useCase === 'stock' || features?.includes('stock')) {
    const provider = features?.includes('artistic') ? 'unsplash' : 'pexels';
    return {
      provider,
      cost: 0,
      quality: 90,
      reasoning: `📷 ${provider === 'unsplash' ? 'Unsplash' : 'Pexels'} offre des photos HD gratuites. Économie de 100% vs DALL-E 3 ($0 vs $0.080).`,
      estimatedSavings: 0.08,
      alternativeProvider: 'openai-dalle3-hd',
      alternativeCost: 0.08
    };
  }

  // Sélection basée sur qualité
  if (quality === 'ultra') {
    return {
      provider: 'openai-dalle3-hd',
      cost: 0.08,
      quality: 98,
      reasoning: '🎨 DALL-E 3 HD offre la meilleure qualité d\'image avec résolution maximale. Investissement premium justifié.',
      estimatedSavings: 0,
      alternativeProvider: 'leonardo-phoenix',
      alternativeCost: 0.012
    };
  }

  if (quality === 'premium') {
    if (budget && budget < 0.02) {
      return {
        provider: 'leonardo-phoenix',
        cost: 0.012,
        quality: 94,
        reasoning: '🌟 Leonardo Phoenix offre une qualité premium à 85% moins cher que DALL-E 3 HD ($0.012 vs $0.080).',
        estimatedSavings: 0.068,
        alternativeProvider: 'openai-dalle3-hd',
        alternativeCost: 0.08
      };
    }
    return {
      provider: 'openai-dalle3',
      cost: 0.04,
      quality: 95,
      reasoning: '🎯 DALL-E 3 Standard offre la meilleure qualité pour les posts premium.',
      estimatedSavings: 0.04,
      alternativeProvider: 'openai-dalle3-hd',
      alternativeCost: 0.08
    };
  }

  if (quality === 'standard') {
    return {
      provider: 'leonardo-xl',
      cost: 0.008,
      quality: 90,
      reasoning: '⚡ Leonardo XL offre une excellente qualité à 90% moins cher que DALL-E 3 ($0.008 vs $0.080).',
      estimatedSavings: 0.072,
      alternativeProvider: 'openai-dalle3-hd',
      alternativeCost: 0.08
    };
  }

  // Draft: toujours Replicate Flux (le moins cher)
  return {
    provider: 'replicate-flux',
    cost: 0.008,
    quality: 85,
    reasoning: '💰 Replicate Flux est l\'option la plus rapide et économique. Économie de 90% vs DALL-E 3 ($0.008 vs $0.080).',
    estimatedSavings: 0.072,
    alternativeProvider: 'openai-dalle3-hd',
    alternativeCost: 0.08
  };
}

/**
 * Sélectionne automatiquement l'API optimale pour la génération de texte
 */
export function selectOptimalText(criteria: SelectionCriteria): OrchestratorResponse {
  const { quality, useCase, budget, features } = criteria;

  // Cas spéciaux basés sur les features
  if (features?.includes('reasoning') || useCase === 'analysis' || useCase === 'technical') {
    if (quality === 'ultra') {
      return {
        provider: 'claude-sonnet-4',
        cost: 3.0,
        quality: 98,
        reasoning: '🧠 Claude Sonnet 4 offre le meilleur raisonnement pour analyses techniques complexes. Légèrement plus cher que GPT-4o mais meilleure qualité.',
        estimatedSavings: 0,
        alternativeProvider: 'gpt-4o',
        alternativeCost: 2.5
      };
    }
  }

  if (features?.includes('multilingual') && quality !== 'ultra') {
    return {
      provider: 'gemini-2.5-flash',
      cost: 0.075,
      quality: 92,
      reasoning: '🌍 Gemini 2.5 Flash excelle en multilinguisme avec 1M tokens de contexte. Économie de 97% vs GPT-4o ($0.075 vs $2.50).',
      estimatedSavings: 2.425,
      alternativeProvider: 'gpt-4o',
      alternativeCost: 2.5
    };
  }

  // Sélection basée sur qualité
  if (quality === 'ultra') {
    if (budget && budget < 1.0) {
      return {
        provider: 'gemini-2.5-flash',
        cost: 0.075,
        quality: 92,
        reasoning: '💡 Gemini 2.5 Flash offre une qualité proche de l\'ultra à 97% moins cher ($0.075 vs $2.50). 1M tokens de contexte inclus.',
        estimatedSavings: 2.425,
        alternativeProvider: 'gpt-4o',
        alternativeCost: 2.5
      };
    }
    return {
      provider: 'gpt-4o',
      cost: 2.5,
      quality: 97,
      reasoning: '🚀 GPT-4o offre les meilleures performances pour génération ultra qualité, légèrement moins cher que Claude.',
      estimatedSavings: 0.5,
      alternativeProvider: 'claude-sonnet-4',
      alternativeCost: 3.0
    };
  }

  if (quality === 'premium') {
    if (budget && budget < 0.5) {
      return {
        provider: 'gpt-4o-mini',
        cost: 0.15,
        quality: 90,
        reasoning: '⚡ GPT-4o-mini offre un excellent équilibre qualité/prix. Économie de 94% vs GPT-4o ($0.15 vs $2.50).',
        estimatedSavings: 2.35,
        alternativeProvider: 'gpt-4o',
        alternativeCost: 2.5
      };
    }
    return {
      provider: 'cohere-command-a',
      cost: 0.5,
      quality: 92,
      reasoning: '🎯 Cohere Command-A offre d\'excellentes performances pour contenu premium à 80% moins cher que GPT-4o.',
      estimatedSavings: 2.0,
      alternativeProvider: 'gpt-4o',
      alternativeCost: 2.5
    };
  }

  // Standard/draft: toujours Gemini 2.5 Flash (meilleur rapport qualité/prix)
  return {
    provider: 'gemini-2.5-flash',
    cost: 0.075,
    quality: 92,
    reasoning: '💰 Gemini 2.5 Flash est imbattable en rapport qualité/prix avec 1M tokens de contexte. Économie de 97% vs GPT-4o ($0.075 vs $2.50).',
    estimatedSavings: 2.425,
    alternativeProvider: 'gpt-4o',
    alternativeCost: 2.5
  };
}

/**
 * Sélectionne automatiquement l'API optimale pour la génération/gestion de vidéos
 */
export function selectOptimalVideo(criteria: SelectionCriteria): OrchestratorResponse {
  const { quality, useCase, budget, features } = criteria;

  // Cas spéciaux
  if (useCase === 'stock' || features?.includes('stock')) {
    return {
      provider: 'pexels',
      cost: 0,
      quality: 90,
      reasoning: '🎬 Pexels offre des vidéos HD gratuites. Économie de 100% vs génération IA RunwayML ($0 vs $10.00).',
      estimatedSavings: 10.0,
      alternativeProvider: 'runwayml-gen3',
      alternativeCost: 10.0
    };
  }

  if (useCase === 'screen-recording' || features?.includes('screen-recording')) {
    return {
      provider: 'loom',
      cost: 0.01,
      quality: 92,
      reasoning: '📹 Loom est le meilleur choix pour screen recording. Économie de 99.9% vs RunwayML ($0.01 vs $10.00).',
      estimatedSavings: 9.99,
      alternativeProvider: 'runwayml-gen3',
      alternativeCost: 10.0
    };
  }

  if (useCase === 'hosting' || features?.includes('video-hosting')) {
    return {
      provider: 'vimeo',
      cost: 0.02,
      quality: 95,
      reasoning: '🌐 Vimeo Pro offre le meilleur hébergement vidéo professionnel. Économie de 99.8% vs génération IA ($0.02 vs $10.00).',
      estimatedSavings: 9.98,
      alternativeProvider: 'runwayml-gen3',
      alternativeCost: 10.0
    };
  }

  if (features?.includes('ai-generation') || features?.includes('text-to-video')) {
    if (quality === 'ultra' || quality === 'premium') {
      return {
        provider: 'runwayml-gen3',
        cost: 10.0,
        quality: 98,
        reasoning: '🤖 RunwayML Gen-3 est le meilleur pour génération vidéo IA text-to-video. Investissement premium justifié pour contenu unique.',
        estimatedSavings: 0,
        alternativeProvider: 'stability-video',
        alternativeCost: 5.0
      };
    }
    return {
      provider: 'stability-video',
      cost: 5.0,
      quality: 90,
      reasoning: '🎨 Stability Video offre une bonne génération IA à 50% moins cher que RunwayML ($5.00 vs $10.00).',
      estimatedSavings: 5.0,
      alternativeProvider: 'runwayml-gen3',
      alternativeCost: 10.0
    };
  }

  // Par défaut: YouTube pour upload/streaming gratuit
  return {
    provider: 'youtube',
    cost: 0,
    quality: 95,
    reasoning: '📺 YouTube offre upload illimité et analytics gratuitement. Économie de 100% vs génération IA ($0 vs $10.00).',
    estimatedSavings: 10.0,
    alternativeProvider: 'runwayml-gen3',
    alternativeCost: 10.0
  };
}

/**
 * Sélectionne automatiquement l'API optimale pour la musique/audio
 */
export function selectOptimalMusic(criteria: SelectionCriteria): OrchestratorResponse {
  const { useCase, features } = criteria;

  if (useCase === 'music-recognition' || features?.includes('music-recognition')) {
    return {
      provider: 'shazam',
      cost: 0.001,
      quality: 98,
      reasoning: '🎼 Shazam offre la meilleure reconnaissance musicale pour $0.001. Économie de 99.4% vs alternatives.',
      estimatedSavings: 0.179,
      alternativeProvider: 'elevenlabs',
      alternativeCost: 0.18
    };
  }

  if (useCase === 'sound-effects' || features?.includes('sfx')) {
    return {
      provider: 'freesound',
      cost: 0,
      quality: 85,
      reasoning: '🔊 FreeSound offre une bibliothèque gratuite d\'effets sonores. Économie de 100%.',
      estimatedSavings: 0.18,
      alternativeProvider: 'elevenlabs',
      alternativeCost: 0.18
    };
  }

  // Par défaut: Spotify pour recherche et preview gratuit
  return {
    provider: 'spotify',
    cost: 0,
    quality: 95,
    reasoning: '🎵 Spotify offre recherche musicale et 30s de preview gratuitement. Économie de 100%.',
    estimatedSavings: 0.18,
    alternativeProvider: 'elevenlabs',
    alternativeCost: 0.18
  };
}

/**
 * Fonction principale d'orchestration - Le "Maestro"
 * Route intelligemment vers le sélecteur approprié selon le type de contenu
 */
export function orchestrate(request: OrchestratorRequest): OrchestratorResponse {
  const { contentType, quality = 'standard', useCase, budget, features } = request;

  const criteria: SelectionCriteria = {
    quality,
    useCase,
    budget,
    features
  };

  // Router selon le type de contenu
  switch (contentType) {
    case 'audio':
    case 'tts':
      return selectOptimalTTS(criteria);
    
    case 'image':
      return selectOptimalImage(criteria);
    
    case 'text':
      return selectOptimalText(criteria);
    
    case 'video':
      return selectOptimalVideo(criteria);
    
    case 'music':
      return selectOptimalMusic(criteria);
    
    default:
      throw new Error(`Type de contenu non supporté: ${contentType}`);
  }
}
