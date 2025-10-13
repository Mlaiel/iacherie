/**
 * API Route - Freepik Assets
 * Utilise la clé Freepik configurée
 */

import { NextRequest, NextResponse } from 'next/server';

// Force dynamic rendering for this route
export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = request.nextUrl;
    const query = searchParams.get('query') || 'business';
    const type = searchParams.get('type') || 'photo'; // photo, vector, psd
    const limit = searchParams.get('limit') || '20';

    const response = await fetch(
      `https://api.freepik.com/v1/resources?term=${encodeURIComponent(query)}&filters[content_type]=${type}&limit=${limit}`,
      {
        headers: {
          'X-Freepik-API-Key': process.env.FREEPIK_API_KEY!,
          'Accept': 'application/json'
        }
      }
    );

    if (!response.ok) {
      throw new Error(`Freepik API error: ${response.statusText}`);
    }

    const data = await response.json();

    return NextResponse.json({
      success: true,
      total: data.meta.total,
      assets: data.data.map((item: any) => ({
        id: item.id,
        title: item.title,
        thumbnail: item.thumbnail.url,
        preview: item.preview?.url,
        downloadUrl: item.download?.url,
        type: item.content_type,
        author: item.author.name,
        tags: item.tags
      }))
    });

  } catch (error: any) {
    console.error('Freepik API Error:', error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}
