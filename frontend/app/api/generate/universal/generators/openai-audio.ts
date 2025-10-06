/**
 * Générateur OpenAI TTS/Whisper
 */

import { GenerationResponse } from '@/lib/api-orchestrator';
import OpenAI from 'openai';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY!
});

export async function generateWithOpenAIAudio(
  input: string,
  options: Record<string, any> = {}
): Promise<GenerationResponse> {
  const mode = options.mode || 'tts'; // tts or whisper
  
  try {
    if (mode === 'tts') {
      // Text-to-Speech
      const response = await openai.audio.speech.create({
        model: 'tts-1',
        voice: options.voice || 'alloy',
        input
      });

      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);

      return {
        success: true,
        content: audioUrl,
        provider: 'openai-tts',
        cost: 0.015,
        metadata: {
          quality: 'standard',
          duration: 0,
          model: 'tts-1'
        }
      };
    } else {
      // Whisper transcription (nécessite File)
      return {
        success: false,
        content: '',
        provider: 'openai-whisper',
        cost: 0,
        metadata: {
          quality: 'standard',
          duration: 0,
          model: 'whisper-1'
        }
      };
    }
  } catch (error: any) {
    throw new Error(`OpenAI Audio error: ${error.message}`);
  }
}
