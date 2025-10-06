/**
 * 🎵 PROFESSIONAL AUDIO GENERATION API FOR INFLUENCERS & CREATORS
 * Features: Multi-provider TTS, Voice cloning, Music search, Audio effects
 * Providers: OpenAI TTS, ElevenLabs, Google Cloud TTS, Spotify Music
 * Author: Fahed Mlaiel
 */

import { NextRequest, NextResponse } from 'next/server';
import { orchestrate } from '@/lib/api-orchestrator';
import { detectLanguage, translateText, getBestVoiceForLanguage, ALL_LANGUAGES } from '@/lib/language-manager';
import OpenAI from 'openai';

const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
const ELEVENLABS_API_KEY = process.env.ELEVENLABS_API_KEY;
const GOOGLE_GEMINI_API_KEY = process.env.GOOGLE_GEMINI_API_KEY;
const SPOTIFY_CLIENT_ID = process.env.SPOTIFY_CLIENT_ID;
const SPOTIFY_CLIENT_SECRET = process.env.SPOTIFY_CLIENT_SECRET;
const FREESOUND_API_KEY = process.env.FREESOUND_API_KEY;
const RAPIDAPI_KEY = process.env.RAPIDAPI_KEY;
const RAPIDAPI_HOST = process.env.RAPIDAPI_HOST;

// Vérification des clés
console.log("🎵 PROFESSIONAL AUDIO APIs:");
console.log("OpenAI TTS:", OPENAI_API_KEY ? `✅ ${OPENAI_API_KEY.substring(0, 20)}...` : "❌ Manquante");
console.log("ElevenLabs:", ELEVENLABS_API_KEY ? `✅ ${ELEVENLABS_API_KEY.substring(0, 20)}...` : "❌ Manquante");
console.log("Google Cloud TTS:", GOOGLE_GEMINI_API_KEY ? "✅ Configurée" : "❌ Manquante");
console.log("Spotify:", SPOTIFY_CLIENT_ID ? "✅ Configuré" : "❌ Manquant");
console.log("FreeSound:", FREESOUND_API_KEY ? "✅ Configurée" : "❌ Manquante");
console.log("Shazam (RapidAPI):", RAPIDAPI_KEY ? "✅ Configurée" : "❌ Manquante");

// VOIX DISPONIBLES PAR PROVIDER
const AVAILABLE_VOICES = {
  openai: {
    alloy: { name: 'Alloy', description: 'Voix neutre et claire', gender: 'neutral', language: 'multilingual' },
    echo: { name: 'Echo', description: 'Voix masculine profonde', gender: 'male', language: 'multilingual' },
    fable: { name: 'Fable', description: 'Voix narrative', gender: 'neutral', language: 'multilingual' },
    onyx: { name: 'Onyx', description: 'Voix masculine autoritaire', gender: 'male', language: 'multilingual' },
    nova: { name: 'Nova', description: 'Voix féminine dynamique', gender: 'female', language: 'multilingual' },
    shimmer: { name: 'Shimmer', description: 'Voix féminine douce', gender: 'female', language: 'multilingual' }
  },
  elevenlabs: {
    'EXAVITQu4vr4xnSDxMaL': { name: 'Sarah (Premium)', description: 'Voix féminine professionnelle', gender: 'female', language: 'english' },
    '21m00Tcm4TlvDq8ikWAM': { name: 'Rachel (Premium)', description: 'Voix narrative féminine', gender: 'female', language: 'english' },
    'AZnzlk1XvdvUeBnXmlld': { name: 'Domi (Premium)', description: 'Voix féminine confiante', gender: 'female', language: 'english' },
    'ErXwobaYiN019PkySvjV': { name: 'Antoni (Premium)', description: 'Voix masculine chaleureuse', gender: 'male', language: 'english' },
    'VR6AewLTigWG4xSOukaG': { name: 'Arnold (Premium)', description: 'Voix masculine forte', gender: 'male', language: 'english' }
  },
  google: {
    'en-US-Neural2-A': { name: 'Google US Female', description: 'Voix féminine américaine naturelle', gender: 'female', language: 'en-US' },
    'en-US-Neural2-C': { name: 'Google US Male', description: 'Voix masculine américaine naturelle', gender: 'male', language: 'en-US' },
    'en-GB-Neural2-A': { name: 'Google UK Female', description: 'Voix féminine britannique', gender: 'female', language: 'en-GB' },
    'fr-FR-Neural2-A': { name: 'Google FR Female', description: 'Voix féminine française naturelle', gender: 'female', language: 'fr-FR' },
    'fr-FR-Neural2-B': { name: 'Google FR Male', description: 'Voix masculine française naturelle', gender: 'male', language: 'fr-FR' },
  }
};

// MODÈLES DISPONIBLES
const AVAILABLE_MODELS = {
  openai: ['tts-1', 'tts-1-hd'],
  elevenlabs: ['eleven_monolingual_v1', 'eleven_multilingual_v2', 'eleven_turbo_v2'],
  google: ['Neural2', 'Studio', 'Wavenet']
};

interface AudioRequest {
  text: string;
  provider?: 'openai' | 'elevenlabs' | 'google' | 'spotify' | 'freesound' | 'shazam' | 'auto';
  voice?: string;
  model?: string;
  // Options avancées pour créateurs
  speed?: number; // 0.25 - 4.0
  pitch?: number; // -12 to +12 semitones
  format?: 'mp3' | 'wav' | 'ogg' | 'aac';
  quality?: 'standard' | 'hd' | 'premium';
  stability?: number; // 0-1 (ElevenLabs)
  similarity_boost?: number; // 0-1 (ElevenLabs)
  style?: number; // 0-1 (ElevenLabs)
  use_speaker_boost?: boolean; // ElevenLabs
  // Spotify options
  query?: string; // Pour recherche musique
  genre?: string;
  mood?: string;
  limit?: number;
  // Shazam options
  audioUrl?: string; // URL audio pour reconnaissance
}

// GÉNÉRATION TTS OPENAI PROFESSIONNELLE
async function generateWithOpenAITTS(
  text: string, 
  options: {
    voice?: string;
    model?: string;
    speed?: number;
    format?: string;
  } = {}
) {
  if (!OPENAI_API_KEY) {
    throw new Error('❌ OpenAI API key non configurée');
  }

  const voice = options.voice || 'alloy';
  const model = options.model || 'tts-1';
  const speed = options.speed || 1.0;

  // Validation de la voix
  if (!AVAILABLE_VOICES.openai[voice as keyof typeof AVAILABLE_VOICES.openai]) {
    throw new Error(`Voix OpenAI invalide. Voix disponibles: ${Object.keys(AVAILABLE_VOICES.openai).join(', ')}`);
  }

  console.log(`🎙️ GÉNÉRATION OPENAI TTS - Voix: ${voice}, Modèle: ${model}, Vitesse: ${speed}x`);
  
  const openai = new OpenAI({ apiKey: OPENAI_API_KEY });
  
  try {
    const mp3Response = await openai.audio.speech.create({
      model: model as 'tts-1' | 'tts-1-hd',
      voice: voice as any,
      input: text,
      speed: Math.max(0.25, Math.min(4.0, speed)), // Limite 0.25-4.0
    });

    const arrayBuffer = await mp3Response.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);
    
    const voiceInfo = AVAILABLE_VOICES.openai[voice as keyof typeof AVAILABLE_VOICES.openai];
    
    return {
      success: true,
      audioBuffer: buffer,
      provider: 'openai',
      voice: voice,
      voiceInfo: voiceInfo,
      model: model,
      speed: speed,
      format: 'mp3',
      size: buffer.length,
      duration: Math.ceil(text.length / 15), // Estimation
    };
  } catch (error: any) {
    console.error("❌ Erreur OpenAI TTS:", error);
    throw new Error(`OpenAI TTS: ${error.message}`);
  }
}

// GÉNÉRATION TTS ELEVENLABS PROFESSIONNELLE
async function generateWithElevenLabsTTS(
  text: string,
  options: {
    voice?: string;
    model?: string;
    stability?: number;
    similarity_boost?: number;
    style?: number;
    use_speaker_boost?: boolean;
  } = {}
) {
  if (!ELEVENLABS_API_KEY) {
    throw new Error('❌ ElevenLabs API key non configurée');
  }

  const voiceId = options.voice || 'EXAVITQu4vr4xnSDxMaL';
  const model = options.model || 'eleven_multilingual_v2';
  const stability = options.stability !== undefined ? options.stability : 0.5;
  const similarity_boost = options.similarity_boost !== undefined ? options.similarity_boost : 0.75;
  const style = options.style !== undefined ? options.style : 0;
  const use_speaker_boost = options.use_speaker_boost !== undefined ? options.use_speaker_boost : true;

  console.log(`🎙️ GÉNÉRATION ELEVENLABS TTS - Voix: ${voiceId}, Modèle: ${model}`);
  
  try {
    const response = await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${voiceId}`, {
      method: 'POST',
      headers: {
        'Accept': 'audio/mpeg',
        'Content-Type': 'application/json',
        'xi-api-key': ELEVENLABS_API_KEY,
      },
      body: JSON.stringify({
        text: text,
        model_id: model,
        voice_settings: {
          stability: Math.max(0, Math.min(1, stability)),
          similarity_boost: Math.max(0, Math.min(1, similarity_boost)),
          style: Math.max(0, Math.min(1, style)),
          use_speaker_boost: use_speaker_boost
        }
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`ElevenLabs error: ${response.status} - ${errorText}`);
    }

    const arrayBuffer = await response.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);
    
    const voiceInfo = AVAILABLE_VOICES.elevenlabs[voiceId as keyof typeof AVAILABLE_VOICES.elevenlabs];
    
    return {
      success: true,
      audioBuffer: buffer,
      provider: 'elevenlabs',
      voice: voiceId,
      voiceInfo: voiceInfo || { name: 'Custom', description: 'Voix personnalisée' },
      model: model,
      format: 'mp3',
      size: buffer.length,
      settings: {
        stability,
        similarity_boost,
        style,
        use_speaker_boost
      }
    };
  } catch (error: any) {
    console.error("❌ Erreur ElevenLabs:", error);
    throw new Error(`ElevenLabs TTS: ${error.message}`);
  }
}

// GÉNÉRATION TTS GOOGLE CLOUD PROFESSIONNELLE
async function generateWithGoogleTTS(
  text: string,
  options: {
    voice?: string;
    speed?: number;
    pitch?: number;
  } = {}
) {
  if (!GOOGLE_GEMINI_API_KEY) {
    throw new Error('❌ Google API key non configurée');
  }

  const voice = options.voice || 'fr-FR-Neural2-A';
  const speed = options.speed || 1.0;
  const pitch = options.pitch || 0;

  console.log(`🎙️ GÉNÉRATION GOOGLE TTS - Voix: ${voice}, Vitesse: ${speed}x, Pitch: ${pitch}`);

  try {
    // Google Cloud Text-to-Speech API
    const response = await fetch(`https://texttospeech.googleapis.com/v1/text:synthesize?key=${GOOGLE_GEMINI_API_KEY}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        input: { text },
        voice: {
          languageCode: voice.split('-').slice(0, 2).join('-'),
          name: voice
        },
        audioConfig: {
          audioEncoding: 'MP3',
          speakingRate: speed,
          pitch: pitch
        }
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Google TTS error: ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    const buffer = Buffer.from(data.audioContent, 'base64');
    
    const voiceInfo = AVAILABLE_VOICES.google[voice as keyof typeof AVAILABLE_VOICES.google] || 
      { name: 'Google Voice', description: 'Voix Google Cloud', gender: 'neutral', language: voice };

    return {
      success: true,
      audioBuffer: buffer,
      provider: 'google',
      voice: voice,
      voiceInfo: voiceInfo,
      model: 'Neural2',
      format: 'mp3',
      size: buffer.length,
      speed: speed,
      pitch: pitch,
      duration: Math.ceil(text.length / 15)
    };
  } catch (error: any) {
    console.error("❌ Erreur Google TTS:", error);
    throw new Error(`Google TTS: ${error.message}`);
  }
}

// RECHERCHE MUSIQUE SPOTIFY
async function searchSpotifyMusic(options: {
  query?: string;
  genre?: string;
  mood?: string;
  limit?: number;
}) {
  if (!SPOTIFY_CLIENT_ID || !SPOTIFY_CLIENT_SECRET) {
    throw new Error('❌ Spotify credentials non configurées');
  }

  console.log(`🎵 RECHERCHE SPOTIFY - Query: ${options.query}, Genre: ${options.genre}`);

  try {
    // 1. Obtenir token d'accès
    const authResponse = await fetch('https://accounts.spotify.com/api/token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic ' + Buffer.from(`${SPOTIFY_CLIENT_ID}:${SPOTIFY_CLIENT_SECRET}`).toString('base64')
      },
      body: 'grant_type=client_credentials'
    });

    if (!authResponse.ok) {
      throw new Error('Erreur authentification Spotify');
    }

    const authData = await authResponse.json();
    const accessToken = authData.access_token;

    // 2. Rechercher musique
    const searchQuery = options.query || options.genre || options.mood || 'popular music';
    const limit = options.limit || 10;

    const searchResponse = await fetch(
      `https://api.spotify.com/v1/search?q=${encodeURIComponent(searchQuery)}&type=track&limit=${limit}`,
      {
        headers: {
          'Authorization': `Bearer ${accessToken}`
        }
      }
    );

    if (!searchResponse.ok) {
      throw new Error('Erreur recherche Spotify');
    }

    const searchData = await searchResponse.json();
    
    const tracks = searchData.tracks.items.map((track: any) => ({
      id: track.id,
      name: track.name,
      artist: track.artists[0].name,
      album: track.album.name,
      preview_url: track.preview_url,
      duration_ms: track.duration_ms,
      popularity: track.popularity,
      spotify_url: track.external_urls.spotify,
      image: track.album.images[0]?.url
    }));

    return {
      success: true,
      provider: 'spotify',
      tracks: tracks,
      total: searchData.tracks.total
    };
  } catch (error: any) {
    console.error("❌ Erreur Spotify:", error);
    throw new Error(`Spotify: ${error.message}`);
  }
}

// RECHERCHE EFFETS SONORES FREESOUND
async function searchFreeSound(query: string, limit: number = 10) {
  if (!FREESOUND_API_KEY) {
    throw new Error('❌ FreeSound API key non configurée');
  }

  console.log(`🔊 RECHERCHE FREESOUND - Query: ${query}`);

  try {
    const response = await fetch(
      `https://freesound.org/apiv2/search/text/?query=${encodeURIComponent(query)}&token=${FREESOUND_API_KEY}&page_size=${limit}&fields=id,name,duration,preview-hq-mp3,download,username,tags`
    );

    if (!response.ok) {
      throw new Error('Erreur recherche FreeSound');
    }

    const data = await response.json();
    
    const sounds = data.results.map((sound: any) => ({
      id: sound.id,
      name: sound.name,
      duration: sound.duration,
      preview_url: sound.previews['preview-hq-mp3'],
      download_url: sound.download,
      author: sound.username,
      tags: sound.tags
    }));

    return {
      success: true,
      provider: 'freesound',
      sounds: sounds,
      total: data.count
    };
  } catch (error: any) {
    console.error("❌ Erreur FreeSound:", error);
    throw new Error(`FreeSound: ${error.message}`);
  }
}

// RECONNAISSANCE MUSICALE SHAZAM
async function recognizeMusicShazam(audioUrl?: string) {
  if (!RAPIDAPI_KEY) {
    throw new Error('❌ RapidAPI key non configurée');
  }

  console.log(`🎵 RECONNAISSANCE SHAZAM - Audio URL: ${audioUrl || 'N/A'}`);

  try {
    // Shazam - Recherche de chansons populaires
    const response = await fetch('https://shazam.p.rapidapi.com/charts/track', {
      method: 'GET',
      headers: {
        'X-RapidAPI-Key': RAPIDAPI_KEY,
        'X-RapidAPI-Host': RAPIDAPI_HOST || 'shazam.p.rapidapi.com'
      }
    });

    if (!response.ok) {
      throw new Error('Erreur reconnaissance Shazam');
    }

    const data = await response.json();
    
    const tracks = data.tracks?.slice(0, 10).map((track: any) => ({
      key: track.key,
      title: track.title,
      subtitle: track.subtitle,
      artist: track.subtitle,
      share_url: track.share?.href,
      image: track.images?.coverart,
      shazam_url: track.url,
      genres: track.genres
    })) || [];

    return {
      success: true,
      provider: 'shazam',
      tracks: tracks,
      total: tracks.length
    };
  } catch (error: any) {
    console.error("❌ Erreur Shazam:", error);
    throw new Error(`Shazam: ${error.message}`);
  }
}

// HANDLER POST PROFESSIONNEL
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { 
      text, 
      provider = 'openai', 
      voice,
      model,
      speed,
      pitch, // Note: pitch n'est pas encore supporté nativement, nécessitera post-traitement
      format = 'mp3',
      quality = 'standard',
      stability,
      similarity_boost,
      style,
      use_speaker_boost
    } = body as AudioRequest;

    if (!text) {
      return NextResponse.json(
        { success: false, error: 'Le texte est requis' },
        { status: 400 }
      );
    }

    console.log(`🎵 GÉNÉRATION AUDIO PROFESSIONNELLE
      Provider: ${provider}
      Voice: ${voice || 'auto'}
      Model: ${model || 'auto'}
      Speed: ${speed || 1.0}x
      Quality: ${quality}
      Format: ${format}`);

    let result;

    try {
      switch (provider) {
        case 'openai':
          result = await generateWithOpenAITTS(text, {
            voice: voice || 'alloy',
            model: quality === 'hd' || quality === 'premium' ? 'tts-1-hd' : (model || 'tts-1'),
            speed: speed,
            format: format
          });
          break;

        case 'elevenlabs':
          result = await generateWithElevenLabsTTS(text, {
            voice: voice || 'EXAVITQu4vr4xnSDxMaL',
            model: model || 'eleven_multilingual_v2',
            stability: stability,
            similarity_boost: similarity_boost,
            style: style,
            use_speaker_boost: use_speaker_boost
          });
          break;

        case 'google':
          result = await generateWithGoogleTTS(text, {
            voice: voice || 'fr-FR-Neural2-A',
            speed: speed,
            pitch: pitch
          });
          break;

        case 'spotify':
          // Recherche musicale Spotify
          const { query, genre, mood, limit } = body;
          result = await searchSpotifyMusic({ query, genre, mood, limit });
          break;

        case 'freesound':
          // Recherche effets sonores
          result = await searchFreeSound(text, body.limit || 10);
          break;

        case 'shazam':
          // Reconnaissance musicale
          result = await recognizeMusicShazam(body.audioUrl);
          break;

        case 'auto':
        default:
          // ========================================
          // 🎼 ORCHESTRATION INTELLIGENTE AUDIO
          // ========================================
          console.log('🎼 MAESTRO AUDIO: Sélection intelligente...');
          
          // Déterminer les features demandées
          const features: string[] = [];
          if (pitch !== undefined && pitch !== 0) features.push('pitch-control');
          if (stability !== undefined || similarity_boost !== undefined) features.push('voice-cloning');
          if (body.query || body.genre) features.push('music-search');
          if (text.toLowerCase().includes('sound effect') || text.toLowerCase().includes('sfx')) features.push('sfx');
          
          // Déterminer le useCase
          let useCase = 'podcast';
          if (features.includes('music-search')) useCase = 'music-search';
          else if (features.includes('sfx')) useCase = 'sound-effects';
          else if (quality === 'premium' || quality === 'hd') useCase = 'voice-over';
          
          // Orchestration
          const orchestrationResult = orchestrate({
            contentType: 'audio',
            quality: quality === 'hd' ? 'premium' : (quality as 'draft' | 'standard' | 'premium' | 'ultra'),
            useCase,
            features,
            budget: quality === 'premium' ? undefined : 0.05
          });

          console.log(`✅ MAESTRO AUDIO: ${orchestrationResult.provider} sélectionné`);
          console.log(`💰 ${orchestrationResult.reasoning}`);
          if (orchestrationResult.estimatedSavings) {
            console.log(`💵 Économie: $${orchestrationResult.estimatedSavings.toFixed(3)}`);
          }

          // Exécuter selon le provider orchestré
          const selectedProvider = orchestrationResult.provider;
          
          if (selectedProvider === 'openai-tts-1' || selectedProvider === 'openai-tts-1-hd') {
            result = await generateWithOpenAITTS(text, {
              voice: voice || 'alloy',
              model: selectedProvider === 'openai-tts-1-hd' ? 'tts-1-hd' : 'tts-1',
              speed: speed,
              format: format
            });
          } else if (selectedProvider === 'elevenlabs') {
            result = await generateWithElevenLabsTTS(text, {
              voice: voice || 'EXAVITQu4vr4xnSDxMaL',
              model: model || 'eleven_multilingual_v2',
              stability: stability,
              similarity_boost: similarity_boost,
              style: style,
              use_speaker_boost: use_speaker_boost
            });
          } else if (selectedProvider === 'google-tts') {
            result = await generateWithGoogleTTS(text, {
              voice: voice || 'fr-FR-Neural2-A',
              speed: speed,
              pitch: pitch
            });
          } else {
            // Par défaut OpenAI (plus rapide et moins cher)
            result = await generateWithOpenAITTS(text, {
              voice: voice || 'alloy',
              model: quality === 'hd' || quality === 'premium' ? 'tts-1-hd' : (model || 'tts-1'),
              speed: speed,
              format: format
            });
          }
      }

      if (!result.success) {
        throw new Error('Échec de génération audio');
      }

      // Si c'est Spotify ou FreeSound, retourner les résultats de recherche
      if (provider === 'spotify' || provider === 'freesound' || provider === 'shazam') {
        return NextResponse.json(result);
      }

      // Retourner l'audio en base64 avec métadonnées complètes
      const base64Audio = result.audioBuffer.toString('base64');
      
      return NextResponse.json({
        success: true,
        audio: base64Audio,
        metadata: {
          provider: result.provider,
          voice: result.voice,
          voiceInfo: result.voiceInfo,
          model: result.model,
          format: result.format,
          size: result.size,
          duration: result.duration,
          speed: result.speed,
          pitch: result.pitch,
          settings: result.settings,
          mimeType: 'audio/mpeg',
          generatedAt: new Date().toISOString()
        }
      });

    } catch (error: any) {
      console.error("❌ Erreur génération audio:", error);
      return NextResponse.json(
        {
          success: false,
          error: `Échec génération avec ${provider}: ${error.message}`,
          provider
        },
        { status: 500 }
      );
    }

  } catch (error: any) {
    console.error('❌ Erreur serveur audio:', error);
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}

// ENDPOINT GET POUR DÉCOUVERTE DES CAPACITÉS
export async function GET() {
  return NextResponse.json({
    title: "🎙️ API GÉNÉRATION AUDIO PROFESSIONNELLE - TTS pour Créateurs & Influenceurs",
    version: "2.0.0",
    providers: {
      openai: {
        models: AVAILABLE_MODELS.openai,
        voices: AVAILABLE_VOICES.openai,
        features: ['speed_control', 'hd_quality', 'fast_generation'],
        pricing: 'Bas coût, rapide'
      },
      elevenlabs: {
        models: AVAILABLE_MODELS.elevenlabs,
        voices: AVAILABLE_VOICES.elevenlabs,
        features: ['voice_cloning', 'emotion_control', 'multilingual', 'premium_quality'],
        pricing: 'Premium, haute qualité'
      }
    },
    parameters: {
      required: ['text'],
      optional: {
        provider: "openai | elevenlabs | auto (défaut: openai)",
        voice: "ID de la voix (voir voices ci-dessus)",
        model: "Modèle à utiliser (voir models ci-dessus)",
        speed: "Vitesse 0.25 - 4.0 (défaut: 1.0) - OpenAI uniquement",
        quality: "standard | hd | premium (défaut: standard)",
        format: "mp3 | wav | ogg | aac (défaut: mp3)",
        stability: "0.0 - 1.0 (ElevenLabs uniquement)",
        similarity_boost: "0.0 - 1.0 (ElevenLabs uniquement)",
        style: "0.0 - 1.0 (ElevenLabs uniquement)",
        use_speaker_boost: "boolean (ElevenLabs uniquement)"
      }
    },
    examples: {
      basic_openai: {
        text: "Bonjour, je suis un créateur de contenu.",
        provider: "openai",
        voice: "nova"
      },
      advanced_openai: {
        text: "Voici mon dernier podcast !",
        provider: "openai",
        voice: "onyx",
        model: "tts-1-hd",
        speed: 1.1,
        quality: "hd"
      },
      professional_elevenlabs: {
        text: "Welcome to my channel, today we're talking about AI.",
        provider: "elevenlabs",
        voice: "pNInz6obpgDQGcFmaJgB",
        model: "eleven_turbo_v2",
        stability: 0.6,
        similarity_boost: 0.8,
        style: 0.3,
        use_speaker_boost: true
      },
      auto_selection: {
        text: "Le système choisira automatiquement le meilleur provider.",
        provider: "auto",
        quality: "hd"
      }
    },
    usage_notes: [
      "✅ OpenAI: Rapide, économique, idéal pour narration et podcasts",
      "✅ ElevenLabs: Ultra réaliste, parfait pour voix professionnelles et clonage",
      "✅ Mode 'auto': Sélection intelligente selon vos paramètres",
      "⚡ HD Quality: Utilisez quality='hd' ou quality='premium'",
      "🎚️ Contrôle avancé: ElevenLabs offre stability, similarity_boost, style",
      "🌍 Multilingue: Les deux providers supportent plusieurs langues"
    ]
  });
}
