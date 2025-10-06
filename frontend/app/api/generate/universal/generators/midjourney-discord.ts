/**
 * Générateur Midjourney Discord Bot
 * Utilise le Discord Bot configuré pour Midjourney
 */

import { GenerationResponse } from '@/lib/api-orchestrator';

export async function generateWithMidjourneyDiscord(
  prompt: string,
  options: Record<string, any> = {}
): Promise<GenerationResponse> {
  try {
    // Appel au backend Python qui gère le Discord Bot
    const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/midjourney/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        prompt,
        wait: options.wait !== false
      })
    });

    if (!response.ok) {
      throw new Error(`Midjourney Discord error: ${response.statusText}`);
    }

    const data = await response.json();

    return {
      success: data.success,
      content: data.image_url || data.url,
      provider: 'midjourney-discord',
      cost: 0.08,
      metadata: {
        quality: 'ultra',
        duration: data.duration || 0,
        model: 'midjourney-v6'
      }
    };
  } catch (error: any) {
    throw new Error(`Midjourney Discord error: ${error.message}`);
  }
}
