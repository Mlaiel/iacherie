/**
 * Générateur OpenAI (GPT-4o, GPT-4o-mini, GPT-3.5)
 */

import { GenerationResponse } from '@/lib/api-orchestrator';
import OpenAI from 'openai';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY!
});

const MODEL_MAP: Record<string, string> = {
  'openai-gpt4o': 'gpt-4o',
  'openai-gpt4o-mini': 'gpt-4o-mini',
  'openai-gpt4-turbo': 'gpt-4-turbo',
  'openai-o1': 'o1-preview',
  'openai-o1-mini': 'o1-mini',
  'openai-gpt35': 'gpt-3.5-turbo'
};

export async function generateWithOpenAI(
  apiKey: string,
  prompt: string,
  options: Record<string, any> = {}
): Promise<GenerationResponse> {
  const model = MODEL_MAP[apiKey] || 'gpt-4o-mini';
  
  try {
    const response = await openai.chat.completions.create({
      model,
      messages: [{ role: 'user', content: prompt }],
      max_tokens: options.maxTokens || 1000,
      temperature: options.temperature || 0.7
    });

    const content = response.choices[0].message.content;
    const tokens = response.usage?.total_tokens || 0;

    return {
      success: true,
      content,
      provider: apiKey,
      cost: calculateOpenAICost(model, tokens),
      metadata: {
        quality: 'standard',
        duration: 0,
        tokens,
        model
      }
    };
  } catch (error: any) {
    throw new Error(`OpenAI error: ${error.message}`);
  }
}

function calculateOpenAICost(model: string, tokens: number): number {
  const costs: Record<string, number> = {
    'gpt-4o': 0.005 / 1000,
    'gpt-4o-mini': 0.00015 / 1000,
    'gpt-4-turbo': 0.01 / 1000,
    'o1-preview': 0.015 / 1000,
    'o1-mini': 0.003 / 1000,
    'gpt-3.5-turbo': 0.0005 / 1000
  };
  return (costs[model] || 0.001) * tokens;
}
