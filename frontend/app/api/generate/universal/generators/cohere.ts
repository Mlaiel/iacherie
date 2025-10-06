/**
 * Générateur Cohere Command
 */

import { GenerationResponse } from '@/lib/api-orchestrator';

export async function generateWithCohere(
  prompt: string,
  options: Record<string, any> = {}
): Promise<GenerationResponse> {
  try {
    const response = await fetch('https://api.cohere.ai/v1/generate', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.COHERE_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: 'command',
        prompt,
        max_tokens: options.maxTokens || 500,
        temperature: options.temperature || 0.7
      })
    });

    if (!response.ok) {
      throw new Error(`Cohere API error: ${response.statusText}`);
    }

    const data = await response.json();
    const content = data.generations[0].text;

    return {
      success: true,
      content,
      provider: 'cohere-command',
      cost: 0.001,
      metadata: {
        quality: 'standard',
        duration: 0,
        model: 'command'
      }
    };
  } catch (error: any) {
    throw new Error(`Cohere error: ${error.message}`);
  }
}
