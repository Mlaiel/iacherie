/**
 * Générateur TextRazor NLP
 */

import { GenerationResponse } from '@/lib/api-orchestrator';

export async function generateWithTextRazor(
  text: string,
  options: Record<string, any> = {}
): Promise<GenerationResponse> {
  try {
    const extractors = options.extractors || ['entities', 'topics', 'words'];
    
    const response = await fetch('https://api.textrazor.com/', {
      method: 'POST',
      headers: {
        'X-TextRazor-Key': process.env.TEXTRAZOR_API_KEY!,
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: new URLSearchParams({
        text,
        extractors: extractors.join(',')
      })
    });

    if (!response.ok) {
      throw new Error(`TextRazor API error: ${response.statusText}`);
    }

    const data = await response.json();

    return {
      success: true,
      content: data.response,
      provider: 'textrazor',
      cost: 0.0001,
      metadata: {
        quality: 'standard',
        duration: 0,
        model: 'textrazor-nlp'
      }
    };
  } catch (error: any) {
    throw new Error(`TextRazor error: ${error.message}`);
  }
}
