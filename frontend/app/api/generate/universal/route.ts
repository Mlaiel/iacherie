/**
 * 🎯 ROUTE GÉNÉRATION UNIVERSELLE
 * Route unique qui orchestre TOUTES les 72 APIs intelligemment
 */

import { NextRequest, NextResponse } from 'next/server';
import { IntelligentAPIOrchestrator } from '@/lib/api-orchestrator';

// Import des générateurs
import { generateWithOpenAI } from './generators/openai';
import { generateWithClaude } from './generators/claude';
import { generateWithGemini } from './generators/gemini';
import { generateWithCohere } from './generators/cohere';
import { generateWithHuggingFace } from './generators/huggingface';
import { generateWithTextRazor } from './generators/textrazor';
import { generateWithMidjourneyDiscord } from './generators/midjourney-discord';
import { generateWithDALLE3 } from './generators/dalle3';
import { generateWithLeonardo } from './generators/leonardo';
import { generateWithReplicate } from './generators/replicate';
import { generateWithElevenLabs } from './generators/elevenlabs';
import { generateWithOpenAIAudio } from './generators/openai-audio';

const orchestrator = new IntelligentAPIOrchestrator();

export async function POST(request: NextRequest) {
  const startTime = Date.now();

  try {
    const body = await request.json();
    
    const generationRequest = {
      contentType: body.contentType || 'text',
      useCase: body.useCase || 'chat',
      quality: body.quality || 'standard',
      budget: body.budget,
      prompt: body.prompt,
      options: body.options || {}
    };

    console.log('🎯 Nouvelle requête:', generationRequest);

    // Sélection intelligente de l'API
    const primaryAPI = body.provider || orchestrator.selectBestAPI(generationRequest);
    
    const fallbackAPIs = orchestrator.getFallbackAPIs(primaryAPI);

    console.log('🤖 API sélectionnée:', primaryAPI);

    // Vérification disponibilité
    if (!orchestrator.isAPIAvailable(primaryAPI)) {
      const availableFallback = fallbackAPIs.find(api => orchestrator.isAPIAvailable(api));
      
      if (!availableFallback) {
        return NextResponse.json({
          success: false,
          error: 'Aucune API disponible'
        }, { status: 503 });
      }
    }

    // Estimation du coût
    const estimatedCost = orchestrator.estimateCost(primaryAPI, generationRequest);
    console.log('💰 Coût estimé:', estimatedCost);

    // Génération
    let response = null;
    const attempts = [primaryAPI, ...fallbackAPIs.slice(0, 2)];

    for (const apiKey of attempts) {
      if (!orchestrator.isAPIAvailable(apiKey)) continue;

      try {
        console.log(`🔄 Tentative: ${apiKey}`);
        response = await executeGeneration(apiKey, generationRequest.prompt, generationRequest.options);
        
        if (response.success) {
          console.log(`✅ Succès: ${apiKey}`);
          break;
        }
      } catch (error: any) {
        console.error(`❌ Erreur ${apiKey}:`, error.message);
        continue;
      }
    }

    if (!response || !response.success) {
      return NextResponse.json({
        success: false,
        error: 'Échec génération'
      }, { status: 500 });
    }

    const duration = Date.now() - startTime;
    response.metadata.duration = duration;

    return NextResponse.json({
      success: true,
      ...response,
      orchestration: {
        selectedAPI: primaryAPI,
        fallbacksAvailable: fallbackAPIs.length,
        estimatedCost,
        actualCost: response.cost,
        duration
      }
    });

  } catch (error: any) {
    console.error('❌ Erreur orchestrateur:', error);
    return NextResponse.json({
      success: false,
      error: error.message
    }, { status: 500 });
  }
}

// Fonction d'exécution
async function executeGeneration(apiKey: string, prompt: string, options: any) {
  const generatorMap: Record<string, Function> = {
    'openai-gpt4o': (p: string, o: any) => generateWithOpenAI('openai-gpt4o', p, o),
    'openai-gpt4o-mini': (p: string, o: any) => generateWithOpenAI('openai-gpt4o-mini', p, o),
    'openai-gpt4-turbo': (p: string, o: any) => generateWithOpenAI('openai-gpt4-turbo', p, o),
    'openai-o1': (p: string, o: any) => generateWithOpenAI('openai-o1', p, o),
    'openai-o1-mini': (p: string, o: any) => generateWithOpenAI('openai-o1-mini', p, o),
    'openai-gpt35': (p: string, o: any) => generateWithOpenAI('openai-gpt35', p, o),
    'claude-sonnet-45': generateWithClaude,
    'gemini-pro': generateWithGemini,
    'cohere-command': generateWithCohere,
    'huggingface': generateWithHuggingFace,
    'textrazor': generateWithTextRazor,
    'midjourney-discord': generateWithMidjourneyDiscord,
    'dalle3': generateWithDALLE3,
    'leonardo': generateWithLeonardo,
    'replicate-flux': generateWithReplicate,
    'elevenlabs': generateWithElevenLabs,
    'openai-tts': (p: string, o: any) => generateWithOpenAIAudio(p, { ...o, mode: 'tts' }),
    'openai-whisper': (p: string, o: any) => generateWithOpenAIAudio(p, { ...o, mode: 'whisper' })
  };

  const generator = generatorMap[apiKey];
  if (!generator) {
    throw new Error(`Générateur non trouvé: ${apiKey}`);
  }

  return await generator(prompt, options);
}

// GET - Stats
export async function GET() {
  const stats = orchestrator.getUsageStats();
  
  return NextResponse.json({
    success: true,
    stats,
    totalAPIs: stats.total,
    availableAPIs: stats.available
  });
}
