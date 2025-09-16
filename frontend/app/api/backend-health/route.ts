import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // Appel côté serveur Next.js vers le backend
    const response = await fetch('http://localhost:8000/health');
    
    if (response.ok) {
      const data = await response.json();
      return NextResponse.json({ status: 'online', data });
    } else {
      return NextResponse.json({ status: 'offline', error: 'Backend not responding' });
    }
  } catch (error) {
    return NextResponse.json({ status: 'offline', error: 'Connection failed' });
  }
}