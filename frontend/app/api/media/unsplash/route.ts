/**
 * API Route - Unsplash Photos
 * Utilise les 3 clés Unsplash configurées
 */

import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const query = searchParams.get('query') || 'nature';
    const perPage = searchParams.get('perPage') || '10';
    const page = searchParams.get('page') || '1';

    const response = await fetch(
      `https://api.unsplash.com/search/photos?query=${encodeURIComponent(query)}&per_page=${perPage}&page=${page}`,
      {
        headers: {
          'Authorization': `Client-ID ${process.env.UNSPLASH_ACCESS_KEY}`
        }
      }
    );

    if (!response.ok) {
      throw new Error(`Unsplash API error: ${response.statusText}`);
    }

    const data = await response.json();

    return NextResponse.json({
      success: true,
      total: data.total,
      totalPages: data.total_pages,
      photos: data.results.map((photo: any) => ({
        id: photo.id,
        url: photo.urls.regular,
        thumb: photo.urls.thumb,
        full: photo.urls.full,
        alt: photo.alt_description,
        author: photo.user.name,
        authorUrl: photo.user.links.html,
        downloadUrl: photo.links.download
      }))
    });

  } catch (error: any) {
    console.error('Unsplash API Error:', error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}

// POST - Télécharger une photo (tracking obligatoire)
export async function POST(request: NextRequest) {
  try {
    const { photoId } = await request.json();

    if (!photoId) {
      return NextResponse.json(
        { error: 'Photo ID requis' },
        { status: 400 }
      );
    }

    // Trigger download tracking
    const response = await fetch(
      `https://api.unsplash.com/photos/${photoId}/download`,
      {
        headers: {
          'Authorization': `Client-ID ${process.env.UNSPLASH_ACCESS_KEY}`
        }
      }
    );

    if (!response.ok) {
      throw new Error(`Unsplash API error: ${response.statusText}`);
    }

    const data = await response.json();

    return NextResponse.json({
      success: true,
      url: data.url
    });

  } catch (error: any) {
    console.error('Unsplash Download Error:', error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}
