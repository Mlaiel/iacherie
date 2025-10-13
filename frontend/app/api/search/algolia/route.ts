/**
 * API Route - Algolia Search
 * Utilise les 2 clés Algolia configurées
 */

import { NextRequest, NextResponse } from 'next/server';

const ALGOLIA_APP_ID = process.env.ALGOLIA_APPLICATION_ID!;
const ALGOLIA_API_KEY = process.env.ALGOLIA_API_KEY!;

// POST - Indexer des données
export async function POST(request: NextRequest) {
  try {
    const { indexName, objects } = await request.json();

    if (!indexName || !objects) {
      return NextResponse.json(
        { error: 'Index name et objects requis' },
        { status: 400 }
      );
    }

    const response = await fetch(
      `https://${ALGOLIA_APP_ID}-dsn.algolia.net/1/indexes/${indexName}/batch`,
      {
        method: 'POST',
        headers: {
          'X-Algolia-Application-Id': ALGOLIA_APP_ID,
          'X-Algolia-API-Key': ALGOLIA_API_KEY,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          requests: objects.map((obj: any) => ({
            action: 'addObject',
            body: obj
          }))
        })
      }
    );

    if (!response.ok) {
      throw new Error(`Algolia API error: ${response.statusText}`);
    }

    const data = await response.json();

    return NextResponse.json({
      success: true,
      objectIDs: data.objectIDs,
      taskID: data.taskID
    });

  } catch (error: any) {
    console.error('Algolia Index Error:', error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}

// GET - Rechercher
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const indexName = searchParams.get('index') || 'default';
    const query = searchParams.get('query') || '';
    const hitsPerPage = searchParams.get('hitsPerPage') || '20';

    const response = await fetch(
      `https://${ALGOLIA_APP_ID}-dsn.algolia.net/1/indexes/${indexName}/query`,
      {
        method: 'POST',
        headers: {
          'X-Algolia-Application-Id': ALGOLIA_APP_ID,
          'X-Algolia-API-Key': ALGOLIA_API_KEY,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          query,
          hitsPerPage: parseInt(hitsPerPage)
        })
      }
    );

    if (!response.ok) {
      throw new Error(`Algolia API error: ${response.statusText}`);
    }

    const data = await response.json();

    return NextResponse.json({
      success: true,
      hits: data.hits,
      nbHits: data.nbHits,
      processingTimeMS: data.processingTimeMS
    });

  } catch (error: any) {
    console.error('Algolia Search Error:', error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}
