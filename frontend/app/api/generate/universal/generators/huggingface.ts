/**
 * Générateur HuggingFace
 * Utilise les 3 clés HuggingFace configurées
 */

import { GenerationResponse } from '@/lib/api-orchestrator';

export async function generateWithHuggingFace(
  prompt: string,
  options: Record<string, any> = {}
): Promise<GenerationResponse> {
  const model = options.model || 'gpt2';
  const apiKey = process.env.HUGGINGFACE_API_KEY || process.env.HUGGINGFACE_READ_TOKEN;
  
  try {
    const response = await fetch(
      `https://api-inference.huggingface.co/models/${model}`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          inputs: prompt,
          parameters: {
            max_new_tokens: options.maxTokens || 250,
            temperature: options.temperature || 0.7,
            top_p: options.topP || 0.95
          }
        })
      }
    );

    if (!response.ok) {
      throw new Error(`HuggingFace API error: ${response.statusText}`);
    }

    const data = await response.json();
    const content = Array.isArray(data) ? data[0]?.generated_text : data.generated_text;

    return {
      success: true,
      content: content || '',
      provider: 'huggingface',
      cost: 0,
      metadata: {
        quality: 'standard',
        duration: 0,
        model
      }
    };
  } catch (error: any) {
    throw new Error(`HuggingFace error: ${error.message}`);
  }
}
