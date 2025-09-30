import { NextResponse } from 'next/server';

// GET /api/audio/process - Audio Processing Status
export async function GET(request: Request) {
  try {
    const backendResponse = await fetch('http://localhost:8000/api/audio/process', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    const backendData = await backendResponse.json();
    return NextResponse.json(backendData);
    
  } catch (error) {
    console.error('Audio backend connection failed:', error);
    
    return NextResponse.json({
      success: false,
      error: "Audio processing backend unavailable",
      timestamp: new Date().toISOString(),
      source: "frontend-audio-error"
    });
  }
}

// POST /api/audio/process - Start Audio Processing
export async function POST(request: Request) {
  try {
    const body = await request.json();
    
    const backendResponse = await fetch('http://localhost:8000/api/audio/process', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body)
    });
    
    const backendData = await backendResponse.json();
    return NextResponse.json(backendData);
    
  } catch (error) {
    console.error('Audio processing POST failed:', error);
    
    return NextResponse.json({
      success: false,
      error: "Audio processing failed",
      timestamp: new Date().toISOString(),
      source: "frontend-audio-error"
    });
  }
}