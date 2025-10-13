/**
 * Générateur ElevenLabs TTS
 */

import { GenerationResponse } from '@/lib/api-orchestrator';

export async function generateWithElevenLabs(
  text: string,
  options: Record<string, any> = {}
): Promise<GenerationResponse> {
  const voiceId = options.voiceId || '21m00Tcm4TlvDq8ikWAM';
  
  try {
    const response = await fetch(
      `https://api.elevenlabs.io/v1/text-to-speech/${voiceId}`,
      {
        method: 'POST',
        headers: {
          'xi-api-key': process.env.ELEVENLABS_API_KEY!,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          text,
          model_id: options.modelId || 'eleven_monolingual_v1',
          voice_settings: {
            stability: options.stability || 0.5,
            similarity_boost: options.similarityBoost || 0.5
          }
        })
      }
    );

    if (!response.ok) {
      throw new Error(`ElevenLabs API error: ${response.statusText}`);
    }

    const audioBlob = await response.blob();
    const audioUrl = URL.createObjectURL(audioBlob);

    return {
      success: true,
      content: audioUrl,
      provider: 'elevenlabs',
      cost: 0.18,
      metadata: {
        quality: 'premium',
        duration: 0,
        model: 'eleven_monolingual_v1'
      }
    };
  } catch (error: any) {
    throw new Error(`ElevenLabs error: ${error.message}`);
  }
}
