import { NextResponse } from 'next/server';

export async function POST(
  request: Request,
  { params }: { params: { id: string } }
) {
  try {
    const agentId = params.id;
    const response = await fetch(`http://localhost:8000/agents/${agentId}/stop`, {
      method: 'POST'
    });
    
    if (response.ok) {
      const data = await response.json();
      return NextResponse.json(data);
    } else {
      return NextResponse.json({ error: 'Failed to stop agent' }, { status: 500 });
    }
  } catch (error) {
    return NextResponse.json({ error: 'Connection failed' }, { status: 500 });
  }
}