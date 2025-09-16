import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const response = await fetch('http://localhost:8000/docs');
    
    if (response.ok) {
      const html = await response.text();
      return new NextResponse(html, {
        headers: {
          'Content-Type': 'text/html',
        },
      });
    } else {
      return new NextResponse('API Documentation not available', { status: 500 });
    }
  } catch (error) {
    return new NextResponse('Backend connection failed', { status: 500 });
  }
}