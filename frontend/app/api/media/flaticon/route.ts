/**
 * API Route - Flaticon Icons
 * Utilise la clé Flaticon configurée
 */

import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const query = searchParams.get('query') || 'business';
    const limit = searchParams.get('limit') || '20';
    const styleId = searchParams.get('style') || ''; // linear, fill, etc.

    let url = `https://api.flaticon.com/v3/search/icons/priority?q=${encodeURIComponent(query)}&limit=${limit}`;
    if (styleId) url += `&styleId=${styleId}`;

    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${process.env.FLATICON_API_KEY}`,
        'Accept': 'application/json'
      }
    });

    if (!response.ok) {
      throw new Error(`Flaticon API error: ${response.statusText}`);
    }

    const data = await response.json();

    return NextResponse.json({
      success: true,
      total: data.metadata.total,
      icons: data.data.map((icon: any) => ({
        id: icon.id,
        description: icon.description,
        tags: icon.tags,
        images: {
          png_512: icon.images['512'],
          png_256: icon.images['256'],
          png_128: icon.images['128'],
          svg: icon.images.svg
        },
        colors: icon.colors,
        packId: icon.pack_id,
        packName: icon.pack_name
      }))
    });

  } catch (error: any) {
    console.error('Flaticon API Error:', error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}

// POST - Télécharger une icône
export async function POST(request: NextRequest) {
  try {
    const { iconId, format = 'png' } = await request.json();

    if (!iconId) {
      return NextResponse.json(
        { error: 'Icon ID requis' },
        { status: 400 }
      );
    }

    const response = await fetch(
      `https://api.flaticon.com/v3/item/icon/download/${iconId}/${format}`,
      {
        headers: {
          'Authorization': `Bearer ${process.env.FLATICON_API_KEY}`
        }
      }
    );

    if (!response.ok) {
      throw new Error(`Flaticon download error: ${response.statusText}`);
    }

    const data = await response.json();

    return NextResponse.json({
      success: true,
      downloadUrl: data.download.url
    });

  } catch (error: any) {
    console.error('Flaticon Download Error:', error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}
