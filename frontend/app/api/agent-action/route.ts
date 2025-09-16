import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { agentId, action } = body;
    
    const response = await fetch(`http://localhost:8000/agents/${agentId}/${action}`, {
      method: 'POST'
    });
    
    if (response.ok) {
      const data = await response.json();
      return NextResponse.json(data);
    } else {
      const error = await response.text();
      return NextResponse.json({ error: 'Failed to execute action', details: error }, { status: 500 });
    }
  } catch (error) {
    return NextResponse.json({ error: 'Connection failed', details: String(error) }, { status: 500 });
  }
}