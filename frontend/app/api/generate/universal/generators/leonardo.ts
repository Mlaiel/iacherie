/**
 * Générateur Leonardo AI
 */

import { GenerationResponse } from '@/lib/api-orchestrator';

export async function generateWithLeonardo(
  prompt: string,
  options: Record<string, any> = {}
): Promise<GenerationResponse> {
  try {
    const response = await fetch('https://cloud.leonardo.ai/api/rest/v1/generations', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.LEONARDO_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        prompt,
        num_images: 1,
        width: options.width || 1024,
        height: options.height || 1024,
        modelId: options.modelId || 'b24e16ff-06e3-43eb-8d33-4416c2d75876'
      })
    });

    if (!response.ok) {
      throw new Error(`Leonardo API error: ${response.statusText}`);
    }

    const data = await response.json();
    const generationId = data.sdGenerationJob.generationId;

    // Poll pour le résultat
    await new Promise(resolve => setTimeout(resolve, 5000));

    const resultResponse = await fetch(
      `https://cloud.leonardo.ai/api/rest/v1/generations/${generationId}`,
      {
        headers: {
          'Authorization': `Bearer ${process.env.LEONARDO_API_KEY}`
        }
      }
    );

    const resultData = await resultResponse.json();
    const imageUrl = resultData.generations_by_pk.generated_images[0].url;

    return {
      success: true,
      content: imageUrl,
      provider: 'leonardo',
      cost: 0.015,
      metadata: {
        quality: 'standard',
        duration: 5000,
        model: 'leonardo-diffusion-xl'
      }
    };
  } catch (error: any) {
    throw new Error(`Leonardo error: ${error.message}`);
  }
}
