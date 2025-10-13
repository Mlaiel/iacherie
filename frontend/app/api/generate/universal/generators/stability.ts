/**
 * 🎨 STABILITY AI - Générateur d'Images IA
 * Alternative premium à DALL-E 3
 */

interface GeneratorResult {
  success: boolean;
  content: string;
  provider: string;
  cost: number;
  error?: string;
  metadata?: any;
}

const STABILITY_API_KEY = process.env.STABILITY_API_KEY;

export const generateWithStability = async (prompt: string, options?: any): Promise<GeneratorResult> => {
  if (!STABILITY_API_KEY) {
    throw new Error('Stability AI API key not configured');
  }

  const startTime = Date.now();

  try {
    // Stability AI - Stable Diffusion XL
    const response = await fetch('https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${STABILITY_API_KEY}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({
        text_prompts: [
          {
            text: prompt,
            weight: 1
          }
        ],
        cfg_scale: options?.cfg_scale || 7,
        height: options?.height || 1024,
        width: options?.width || 1024,
        samples: options?.samples || 1,
        steps: options?.steps || 30,
        style_preset: options?.style || 'photographic'
      })
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Stability AI error: ${error}`);
    }

    const data = await response.json();
    const duration = Date.now() - startTime;

    // Première image générée
    const image = data.artifacts?.[0];
    if (!image) {
      throw new Error('No image generated');
    }

    return {
      success: true,
      content: `data:image/png;base64,${image.base64}`,
      provider: 'stability',
      cost: 0.002, // ~$0.002 par image
      metadata: {
        quality: 'premium',
        duration: duration,
        model: 'Stable Diffusion XL',
        resolution: `${options?.width || 1024}x${options?.height || 1024}`,
        steps: options?.steps || 30,
        cfg_scale: options?.cfg_scale || 7,
        seed: image.seed
      }
    };

  } catch (error) {
    return {
      success: false,
      content: '',
      provider: 'stability',
      cost: 0,
      error: error instanceof Error ? error.message : 'Unknown error',
      metadata: {
        quality: 'failed',
        duration: Date.now() - startTime,
        model: 'Stable Diffusion XL'
      }
    };
  }
};
