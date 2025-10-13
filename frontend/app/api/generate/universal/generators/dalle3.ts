/**
 * Générateur DALL-E 3
 */

import { GenerationResponse } from '@/lib/api-orchestrator';
import OpenAI from 'openai';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY!
});

export async function generateWithDALLE3(
  prompt: string,
  options: Record<string, any> = {}
): Promise<GenerationResponse> {
  try {
    const response = await openai.images.generate({
      model: 'dall-e-3',
      prompt,
      n: 1,
      size: options.size || '1024x1024',
      quality: options.quality || 'standard'
    });

    const imageUrl = response.data[0].url!;

    return {
      success: true,
      content: imageUrl,
      provider: 'dalle3',
      cost: options.quality === 'hd' ? 0.08 : 0.04,
      metadata: {
        quality: options.quality === 'hd' ? 'premium' : 'standard',
        duration: 0,
        model: 'dall-e-3'
      }
    };
  } catch (error: any) {
    throw new Error(`DALL-E 3 error: ${error.message}`);
  }
}
