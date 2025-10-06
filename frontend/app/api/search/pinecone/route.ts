/**
 * API Route - Pinecone Vector Database
 * Utilise la clé Pinecone configurée
 */

import { NextRequest, NextResponse } from 'next/server';

const PINECONE_API_KEY = process.env.PINECONE_API_KEY!;
const PINECONE_ENVIRONMENT = process.env.PINECONE_ENVIRONMENT || 'us-west1-gcp';
const PINECONE_INDEX = process.env.PINECONE_INDEX || 'iacherie';

// POST - Upsert vectors
export async function POST(request: NextRequest) {
  try {
    const { vectors, namespace } = await request.json();

    if (!vectors || vectors.length === 0) {
      return NextResponse.json(
        { error: 'Vectors requis' },
        { status: 400 }
      );
    }

    const response = await fetch(
      `https://${PINECONE_INDEX}-${PINECONE_ENVIRONMENT}.pinecone.io/vectors/upsert`,
      {
        method: 'POST',
        headers: {
          'Api-Key': PINECONE_API_KEY,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          vectors,
          namespace: namespace || 'default'
        })
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(`Pinecone API error: ${error.message || response.statusText}`);
    }

    const data = await response.json();

    return NextResponse.json({
      success: true,
      upsertedCount: data.upsertedCount
    });

  } catch (error: any) {
    console.error('Pinecone Upsert Error:', error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}

// GET - Query vectors
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const vectorParam = searchParams.get('vector');
    const topK = searchParams.get('topK') || '10';
    const namespace = searchParams.get('namespace') || 'default';

    if (!vectorParam) {
      return NextResponse.json(
        { error: 'Vector requis' },
        { status: 400 }
      );
    }

    const vector = JSON.parse(vectorParam);

    const response = await fetch(
      `https://${PINECONE_INDEX}-${PINECONE_ENVIRONMENT}.pinecone.io/query`,
      {
        method: 'POST',
        headers: {
          'Api-Key': PINECONE_API_KEY,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          vector,
          topK: parseInt(topK),
          namespace,
          includeMetadata: true
        })
      }
    );

    if (!response.ok) {
      throw new Error(`Pinecone API error: ${response.statusText}`);
    }

    const data = await response.json();

    return NextResponse.json({
      success: true,
      matches: data.matches
    });

  } catch (error: any) {
    console.error('Pinecone Query Error:', error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}
