/**
 * 🎬 RUNWAYML GEN-3 API ROUTE
 * Génération vidéo IA premium avec gestion des crédits
 */

import { NextRequest, NextResponse } from 'next/server';
import { generateWithRunwayML } from '../../generate/universal/generators/runwayml';

const RUNWAYML_CREDITS_REMAINING = parseInt(process.env.RUNWAYML_CREDITS_REMAINING || '680');

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { prompt, duration = 3, resolution = '1280x720', fps = 24 } = body;

    if (!prompt) {
      return NextResponse.json(
        { error: 'Prompt is required' },
        { status: 400 }
      );
    }

    // Vérification des crédits
    const estimatedCost = duration * 40; // 40 crédits/seconde
    if (RUNWAYML_CREDITS_REMAINING < estimatedCost) {
      return NextResponse.json(
        {
          error: 'Insufficient RunwayML credits',
          credits_remaining: RUNWAYML_CREDITS_REMAINING,
          credits_required: estimatedCost,
          warning: 'Utilisez des alternatives gratuites comme Pika Labs'
        },
        { status: 402 } // Payment Required
      );
    }

    // Génération vidéo
    const result = await generateWithRunwayML(prompt, {
      duration,
      resolution,
      fps
    });

    if (!result.success) {
      return NextResponse.json(
        { error: result.error || 'Generation failed' },
        { status: 500 }
      );
    }

    return NextResponse.json({
      success: true,
      video_url: result.content,
      provider: 'runwayml',
      credits_used: result.metadata?.credits_used,
      credits_remaining: result.metadata?.credits_remaining,
      metadata: result.metadata,
      warning: result.metadata?.warning
    });

  } catch (error) {
    console.error('RunwayML route error:', error);
    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : 'Unknown error',
        credits_remaining: RUNWAYML_CREDITS_REMAINING
      },
      { status: 500 }
    );
  }
}

// GET - Status des crédits
export async function GET() {
  return NextResponse.json({
    provider: 'RunwayML Gen-3',
    status: RUNWAYML_CREDITS_REMAINING >= 40 ? 'active' : 'insufficient_credits',
    credits_remaining: RUNWAYML_CREDITS_REMAINING,
    cost_per_second: 40,
    max_video_duration: Math.floor(RUNWAYML_CREDITS_REMAINING / 40),
    warning: RUNWAYML_CREDITS_REMAINING < 120 ? '⚠️ Crédits faibles! Utiliser avec parcimonie.' : undefined
  });
}
