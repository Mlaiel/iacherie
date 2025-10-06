/**
 * Générateur Claude Sonnet 4.5
 */

import { GenerationResponse } from '@/lib/api-orchestrator';
import Anthropic from '@anthropic-ai/sdk';

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY!
});

export async function generateWithClaude(
  prompt: string,
  options: Record<string, any> = {}
): Promise<GenerationResponse> {
  try {
    const response = await anthropic.messages.create({
      model: 'claude-sonnet-4-20241022',
      max_tokens: options.maxTokens || 1024,
      messages: [{ role: 'user', content: prompt }]
    });

    const content = response.content[0].type === 'text' 
      ? response.content[0].text 
      : '';

    return {
      success: true,
      content,
      provider: 'claude-sonnet-45',
      cost: 0.003,
      metadata: {
        quality: 'ultra',
        duration: 0,
        tokens: response.usage.input_tokens + response.usage.output_tokens,
        model: 'claude-sonnet-4.5'
      }
    };
  } catch (error: any) {
    throw new Error(`Claude error: ${error.message}`);
  }
}
