/**
 * 🎬 RUNWAYML GEN-3 - Générateur Vidéo IA Premium
 * 
 * ⚠️ ATTENTION: CRÉDITS LIMITÉS!
 * - Crédits restants: 680
 * - Coût Veo-3: 40 crédits/seconde
 * - Capacité totale: ~17 secondes de vidéo
 */

interface GeneratorResult {
  success: boolean;
  content: string;
  provider: string;
  cost: number;
  error?: string;
  metadata?: any;
}

const RUNWAYML_API_KEY = process.env.RUNWAYML_API_KEY;
const RUNWAYML_CREDITS_REMAINING = parseInt(process.env.RUNWAYML_CREDITS_REMAINING || '680');

export const generateWithRunwayML = async (prompt: string, options?: any): Promise<GeneratorResult> => {
  if (!RUNWAYML_API_KEY) {
    throw new Error('RunwayML API key not configured');
  }

  // ⚠️ Vérification des crédits avant génération
  if (RUNWAYML_CREDITS_REMAINING < 40) {
    throw new Error('Crédits RunwayML insuffisants (< 40 crédits restants)');
  }

  const startTime = Date.now();

  try {
    // RunwayML Gen-3 API
    const response = await fetch('https://api.runwayml.com/v1/generate', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${RUNWAYML_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: options?.model || 'gen3',
        prompt: prompt,
        duration: options?.duration || 3, // 3 secondes par défaut
        resolution: options?.resolution || '1280x720',
        fps: options?.fps || 24
      })
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`RunwayML API error: ${error}`);
    }

    const data = await response.json();
    const duration = Date.now() - startTime;

    // Calcul du coût en crédits (40 crédits/seconde)
    const videoDuration = options?.duration || 3;
    const creditsUsed = videoDuration * 40;

    return {
      success: true,
      content: data.video_url || data.url,
      provider: 'runwayml',
      cost: creditsUsed, // Coût en crédits
      metadata: {
        quality: 'premium',
        duration: duration,
        model: 'Gen-3',
        video_duration: videoDuration,
        credits_used: creditsUsed,
        credits_remaining: RUNWAYML_CREDITS_REMAINING - creditsUsed,
        resolution: options?.resolution || '1280x720',
        fps: options?.fps || 24,
        warning: creditsUsed >= 40 ? '⚠️ Génération coûteuse en crédits!' : undefined
      }
    };

  } catch (error) {
    return {
      success: false,
      content: '',
      provider: 'runwayml',
      cost: 0,
      error: error instanceof Error ? error.message : 'Unknown error',
      metadata: {
        quality: 'failed',
        duration: Date.now() - startTime,
        model: 'Gen-3',
        credits_remaining: RUNWAYML_CREDITS_REMAINING
      }
    };
  }
};
