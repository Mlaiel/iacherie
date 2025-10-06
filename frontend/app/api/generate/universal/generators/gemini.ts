/**
 * Générateur Google Gemini Pro
 */

import { GenerationResponse } from '@/lib/api-orchestrator';

export async function generateWithGemini(
  prompt: string,
  options: Record<string, any> = {}
): Promise<GenerationResponse> {
  try {
    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=${process.env.GOOGLE_GEMINI_API_KEY}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }]
        })
      }
    );

    if (!response.ok) {
      throw new Error(`Gemini API error: ${response.statusText}`);
    }

    const data = await response.json();
    const content = data.candidates[0].content.parts[0].text;

    return {
      success: true,
      content,
      provider: 'gemini-pro',
      cost: 0.0005,
      metadata: {
        quality: 'standard',
        duration: 0,
        model: 'gemini-pro'
      }
    };
  } catch (error: any) {
    throw new Error(`Gemini error: ${error.message}`);
  }
}
