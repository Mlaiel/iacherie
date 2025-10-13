/**
 * Générateur Replicate Flux
 */

import { GenerationResponse } from '@/lib/api-orchestrator';
import Replicate from 'replicate';

const replicate = new Replicate({
  auth: process.env.REPLICATE_API_TOKEN!
});

export async function generateWithReplicate(
  prompt: string,
  options: Record<string, any> = {}
): Promise<GenerationResponse> {
  try {
    const output = await replicate.run(
      'black-forest-labs/flux-schnell',
      {
        input: {
          prompt,
          num_outputs: 1,
          aspect_ratio: options.aspectRatio || '1:1',
          output_format: 'webp'
        }
      }
    ) as string[];

    return {
      success: true,
      content: output[0],
      provider: 'replicate-flux',
      cost: 0.008,
      metadata: {
        quality: 'draft',
        duration: 0,
        model: 'flux-schnell'
      }
    };
  } catch (error: any) {
    throw new Error(`Replicate error: ${error.message}`);
  }
}
