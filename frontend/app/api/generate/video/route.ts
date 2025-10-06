import { NextRequest, NextResponse } from 'next/server';

// Types
interface VideoGenerationRequest {
  prompt: string;
  provider: 'auto' | 'runwayml' | 'pexels' | 'vimeo' | 'loom' | 'youtube';
  duration: number;
  quality: 'draft' | 'standard' | 'hd' | 'ultra';
  type: 'generation' | 'stock' | 'hosting' | 'recording';
}

// === RUNWAYML GEN-3 ===
async function generateWithRunwayML(prompt: string, duration: number, quality: string) {
  const apiKey = process.env.RUNWAYML_API_KEY;
  const creditsRemaining = parseInt(process.env.RUNWAYML_CREDITS_REMAINING || '680');

  if (!apiKey) {
    throw new Error('RunwayML API key not configured');
  }

  // Estimation du coût (40 crédits/seconde)
  const estimatedCredits = duration * 40;
  if (estimatedCredits > creditsRemaining) {
    throw new Error(`Crédits insuffisants. Requis: ${estimatedCredits}, Disponibles: ${creditsRemaining}`);
  }

  console.log('🚀 GÉNÉRATION RUNWAYML GEN-3');
  console.log(`   Prompt: ${prompt}`);
  console.log(`   Durée: ${duration}s`);
  console.log(`   Crédits estimés: ${estimatedCredits}/${creditsRemaining}`);

  // Note: RunwayML nécessite une vraie implémentation avec leur SDK
  // Pour l'instant, on retourne un mock
  const cost = duration * 1.0; // ~$1/seconde

  return {
    success: true,
    provider: 'runwayml-gen3',
    videoUrl: 'https://example.com/generated-video.mp4', // Mock
    cost,
    duration,
    quality,
    creditsUsed: estimatedCredits,
    creditsRemaining: creditsRemaining - estimatedCredits
  };
}

// === PEXELS STOCK VIDEO ===
async function searchPexelsVideos(query: string, quality: string) {
  const apiKey = process.env.PEXELS_API_KEY;

  if (!apiKey) {
    throw new Error('Pexels API key not configured');
  }

  console.log('🎬 RECHERCHE PEXELS STOCK VIDEO');
  console.log(`   Query: ${query}`);
  console.log(`   Quality: ${quality}`);

  const response = await fetch(
    `https://api.pexels.com/videos/search?query=${encodeURIComponent(query)}&per_page=15&orientation=landscape`,
    {
      headers: {
        'Authorization': apiKey
      }
    }
  );

  if (!response.ok) {
    throw new Error(`Pexels API error: ${response.status}`);
  }

  const data = await response.json();

  if (!data.videos || data.videos.length === 0) {
    throw new Error('Aucune vidéo trouvée pour cette recherche');
  }

  // Sélectionner la meilleure qualité disponible
  const video = data.videos[0];
  let videoFile = video.video_files[0];

  // Chercher la qualité demandée
  if (quality === 'hd' || quality === 'ultra') {
    const hdFile = video.video_files.find((f: any) => f.quality === 'hd');
    if (hdFile) videoFile = hdFile;
  }

  return {
    success: true,
    provider: 'pexels',
    videoUrl: videoFile.link,
    thumbnail: video.image,
    cost: 0, // Gratuit
    duration: video.duration,
    quality: videoFile.quality,
    width: videoFile.width,
    height: videoFile.height,
    photographer: video.user.name,
    photographerUrl: video.user.url
  };
}

// === VIMEO HOSTING ===
async function uploadToVimeo(videoUrl: string) {
  const clientId = process.env.VIMEO_CLIENT_ID;
  const clientSecret = process.env.VIMEO_CLIENT_SECRET;

  if (!clientId || !clientSecret) {
    throw new Error('Vimeo credentials not configured');
  }

  console.log('📹 UPLOAD VIMEO PRO');
  console.log(`   Video URL: ${videoUrl}`);

  // Note: Vimeo nécessite OAuth + upload complexe
  // Pour l'instant, mock
  const cost = 0.02; // $0.02/GB estimé

  return {
    success: true,
    provider: 'vimeo',
    vimeoUrl: 'https://vimeo.com/123456789', // Mock
    embedCode: '<iframe src="https://player.vimeo.com/video/123456789"></iframe>',
    cost,
    privacy: 'public'
  };
}

// === LOOM RECORDING ===
async function createLoomRecording() {
  const apiKey = process.env.LOOM_API_KEY;

  if (!apiKey) {
    throw new Error('Loom API key not configured');
  }

  console.log('🎥 CRÉATION LOOM RECORDING');

  // Note: Loom nécessite SDK côté client pour le recording
  // L'API backend sert à créer le lien de partage
  const cost = 0.01; // $0.01/minute

  return {
    success: true,
    provider: 'loom',
    recordingUrl: 'https://www.loom.com/share/abcd1234', // Mock
    cost,
    features: ['Screen + Webcam', 'Transcription auto', 'CTA intégrés']
  };
}

// === YOUTUBE API ===
async function searchYouTubeVideos(query: string) {
  const apiKey = process.env.YOUTUBE_API_KEY;

  if (!apiKey) {
    throw new Error('YouTube API key not configured');
  }

  console.log('▶️ RECHERCHE YOUTUBE');
  console.log(`   Query: ${query}`);

  const response = await fetch(
    `https://www.googleapis.com/youtube/v3/search?part=snippet&q=${encodeURIComponent(query)}&type=video&maxResults=10&key=${apiKey}`
  );

  if (!response.ok) {
    throw new Error(`YouTube API error: ${response.status}`);
  }

  const data = await response.json();

  if (!data.items || data.items.length === 0) {
    throw new Error('Aucune vidéo trouvée');
  }

  const video = data.items[0];

  return {
    success: true,
    provider: 'youtube',
    videoId: video.id.videoId,
    videoUrl: `https://www.youtube.com/watch?v=${video.id.videoId}`,
    embedUrl: `https://www.youtube.com/embed/${video.id.videoId}`,
    title: video.snippet.title,
    description: video.snippet.description,
    thumbnail: video.snippet.thumbnails.high.url,
    cost: 0 // Gratuit
  };
}

// === MAESTRO AUTO SELECTION ===
function selectOptimalVideoProvider(request: VideoGenerationRequest) {
  const { type, quality, duration, prompt } = request;

  // Si stock footage demandé ou prompt simple
  if (type === 'stock' || (!prompt.includes('generate') && !prompt.includes('create'))) {
    return {
      provider: 'pexels',
      reasoning: 'Pexels stock video offre du contenu HD gratuit instantané, idéal pour ce besoin.',
      cost: 0,
      savings: duration * 1.0, // vs RunwayML
      savingsPercent: 100
    };
  }

  // Si hébergement demandé
  if (type === 'hosting') {
    return {
      provider: 'vimeo',
      reasoning: 'Vimeo Pro offre un hébergement professionnel avec analytics à faible coût.',
      cost: 0.02,
      savings: duration * 0.98,
      savingsPercent: 98
    };
  }

  // Si recording/tutoriel
  if (type === 'recording' || prompt.includes('tutorial') || prompt.includes('demo')) {
    return {
      provider: 'loom',
      reasoning: 'Loom est optimal pour les recordings screen + webcam avec transcription.',
      cost: duration * 0.01 / 60, // $0.01/min
      savings: duration * 0.99,
      savingsPercent: 99
    };
  }

  // Si génération IA nécessaire et budget OK
  if (quality === 'ultra' || prompt.includes('cinematic') || prompt.includes('ai generate')) {
    const creditsAvailable = parseInt(process.env.RUNWAYML_CREDITS_REMAINING || '680');
    const creditsNeeded = duration * 40;

    if (creditsNeeded <= creditsAvailable) {
      return {
        provider: 'runwayml',
        reasoning: 'RunwayML Gen-3 offre la meilleure qualité IA pour les vidéos cinématiques uniques.',
        cost: duration * 1.0,
        savings: 0,
        savingsPercent: 0
      };
    }
  }

  // Par défaut: Pexels stock
  return {
    provider: 'pexels',
    reasoning: 'Pexels stock video est le choix par défaut: gratuit, HD, et immédiat.',
    cost: 0,
    savings: duration * 1.0,
    savingsPercent: 100
  };
}

export async function POST(request: NextRequest) {
  try {
    const body: VideoGenerationRequest = await request.json();
    const { prompt, provider, duration, quality, type } = body;

    console.log('🎬 GÉNÉRATION VIDÉO');
    console.log(`   Prompt: ${prompt}`);
    console.log(`   Provider: ${provider}`);
    console.log(`   Durée: ${duration}s`);
    console.log(`   Qualité: ${quality}`);

    let result: any;
    let finalProvider = provider;
    let maestroSelection = null;

    // Auto selection
    if (provider === 'auto') {
      maestroSelection = selectOptimalVideoProvider(body);
      finalProvider = maestroSelection.provider as any;
      console.log('🎼 MAESTRO SÉLECTION:', maestroSelection.provider);
      console.log('💡 Raisonnement:', maestroSelection.reasoning);
    }

    // Génération selon provider
    switch (finalProvider) {
      case 'runwayml':
        result = await generateWithRunwayML(prompt, duration, quality);
        break;

      case 'pexels':
        result = await searchPexelsVideos(prompt, quality);
        break;

      case 'vimeo':
        result = await uploadToVimeo(''); // Nécessite URL vidéo source
        break;

      case 'loom':
        result = await createLoomRecording();
        break;

      case 'youtube':
        result = await searchYouTubeVideos(prompt);
        break;

      default:
        throw new Error(`Provider non supporté: ${finalProvider}`);
    }

    // Ajouter les infos Maestro si auto
    if (maestroSelection) {
      result.maestro = true;
      result.reasoning = maestroSelection.reasoning;
      result.savings = maestroSelection.savings;
      result.savingsPercent = maestroSelection.savingsPercent;
    }

    return NextResponse.json(result);

  } catch (error: any) {
    console.error('❌ Erreur génération vidéo:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: error.message || 'Erreur lors de la génération vidéo' 
      },
      { status: 500 }
    );
  }
}
