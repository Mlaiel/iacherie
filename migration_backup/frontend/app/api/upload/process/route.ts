import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const formData = await request.formData();
    
    // Proxy vers le backend Python avec FormData
    const response = await fetch('http://localhost:8000/upload/process', {
      method: 'POST',
      body: formData // FormData se forward automatiquement
    });
    
    if (response.ok) {
      const data = await response.json();
      return NextResponse.json(data);
    } else {
      const error = await response.text();
      return NextResponse.json({ error }, { status: response.status });
    }
  } catch (error) {
    console.error('Upload API Error:', error);
    return NextResponse.json({ 
      error: 'Failed to upload file',
      message: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}