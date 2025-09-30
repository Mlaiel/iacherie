import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    
    // Proxy vers le backend Python pour génération de vidéo
    const response = await fetch('http://localhost:8000/generate/video', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body)
    });
    
    if (response.ok) {
      const data = await response.json();
      return NextResponse.json(data);
    } else {
      const error = await response.text();
      return NextResponse.json({ error }, { status: response.status });
    }
  } catch (error) {
    console.error('Video Generation API Error:', error);
    return NextResponse.json({ 
      error: 'Failed to generate video',
      message: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}