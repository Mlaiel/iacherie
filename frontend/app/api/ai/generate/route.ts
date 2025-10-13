/**
 * 🤖 AI GENERATION API - REAL AI SERVICES ONLY
 * NO SIMULATION - DIRECT CONNECTION TO REAL BACKEND
 * Author: Fahed Mlaiel
 */

import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    const { prompt, type, options } = await request.json();
    
    console.log('🔥 REAL AI CONNECTION - NO SIMULATION - 53 Real Agents');
    
    if (!prompt) {
      return NextResponse.json(
        { success: false, error: 'Prompt is required' },
        { status: 400 }
      );
    }

    // DIRECT CONNECTION TO REAL BACKEND - NO SIMULATION
    const backendResponse = await fetch(`${BACKEND_URL}/api/ai/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt,
        type: type || 'content-generation',
        options: options || {}
      })
    });

    if (!backendResponse.ok) {
      const errorText = await backendResponse.text();
      throw new Error(`Backend error ${backendResponse.status}: ${errorText}`);
    }

    const realResult = await backendResponse.json();
    
    console.log('✅ Real AI result received from 53+ agents backend');
    
    // Format de réponse adapté au frontend
    const formattedData = {
      generated_content: realResult.result || realResult.data,
      content_type: realResult.type || type,
      processing_time: realResult.metadata?.time || 'N/A',
      agent_used: realResult.metadata?.agent || 'N/A',
      id: realResult.metadata?.id || 'N/A',
      // URLs et données spécifiques selon le type
      ...(realResult.image_url && { 
        image_url: realResult.image_url,
        image_data: realResult.image_url,
        dimensions: `${realResult.image_data?.width}x${realResult.image_data?.height}` || '1024x1024',
        download_url: realResult.image_url 
      }),
      ...(realResult.audio_url && { 
        audio_url: realResult.audio_url,
        duration: realResult.audio_data?.duration || 'N/A',
        format: realResult.audio_data?.format || 'wav',
        download_url: realResult.audio_url 
      }),
      ...(realResult.video_url && { 
        video_url: realResult.video_url,
        thumbnail_url: realResult.video_url.replace('.mp4', '_thumb.jpg'),
        resolution: realResult.video_data?.resolution || '1280x720',
        duration: realResult.video_data?.duration || 'N/A',
        download_url: realResult.video_url 
      })
    };
    
    return NextResponse.json({
      success: true,
      data: formattedData,
      source: '53+ Real AI Agents Backend',
      status: '✅ REAL AI GENERATED',
      timestamp: new Date().toISOString(),
      no_simulation: true
    });

  } catch (error) {
    console.error('❌ Real AI connection failed:', error);
    
    return NextResponse.json(
      { 
        success: false, 
        error: `Real AI backend connection failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
        message: 'NO SIMULATION PROVIDED - Only real AI services supported',
        timestamp: new Date().toISOString()
      },
      { status: 503 }
    );
  }
}

export async function GET() {
  try {
    console.log('🔗 Fetching real AI services from backend...');
    
    const response = await fetch(`${BACKEND_URL}/ai-agents`);
    
    if (response.ok) {
      const realServices = await response.json();
      return NextResponse.json({
        success: true,
        data: realServices,
        source: 'Real AI Services Backend'
      });
    }
  } catch (error) {
    console.error('Real AI services unavailable:', error);
  }

  return NextResponse.json(
    { 
      success: false, 
      error: 'Real AI services temporarily unavailable - NO SIMULATION'
    },
    { status: 503 }
  );
}
