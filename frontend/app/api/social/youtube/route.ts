/**
 * API Route - YouTube Integration
 * Utilise les 3 clés YouTube configurées
 */

import { NextRequest, NextResponse } from 'next/server';

// POST - Upload video
export async function POST(request: NextRequest) {
  try {
    const { videoUrl, title, description, tags, categoryId = '22' } = await request.json();

    if (!videoUrl || !title) {
      return NextResponse.json(
        { error: 'Video URL et titre requis' },
        { status: 400 }
      );
    }

    // YouTube Data API v3 - Upload
    const metadata = {
      snippet: {
        title,
        description: description || '',
        tags: tags || [],
        categoryId
      },
      status: {
        privacyStatus: 'public'
      }
    };

    // Note: Upload vidéo nécessite OAuth2 pour authentification utilisateur
    // Cette implémentation est simplifiée

    return NextResponse.json({
      success: true,
      message: 'Upload YouTube nécessite OAuth2 flow complet',
      metadata,
      nextSteps: [
        'Implémenter OAuth2 consent flow',
        'Obtenir access token utilisateur',
        'Uploader via resumable upload protocol'
      ]
    });

  } catch (error: any) {
    console.error('YouTube Upload Error:', error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}

// GET - Récupérer des vidéos
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const query = searchParams.get('query') || 'AI technology';
    const maxResults = searchParams.get('maxResults') || '10';

    const response = await fetch(
      `https://www.googleapis.com/youtube/v3/search?part=snippet&q=${encodeURIComponent(query)}&maxResults=${maxResults}&type=video&key=${process.env.YOUTUBE_API_KEY}`
    );

    if (!response.ok) {
      throw new Error(`YouTube API error: ${response.statusText}`);
    }

    const data = await response.json();

    return NextResponse.json({
      success: true,
      total: data.pageInfo.totalResults,
      videos: data.items.map((item: any) => ({
        id: item.id.videoId,
        title: item.snippet.title,
        description: item.snippet.description,
        thumbnail: item.snippet.thumbnails.high.url,
        channelTitle: item.snippet.channelTitle,
        publishedAt: item.snippet.publishedAt,
        url: `https://www.youtube.com/watch?v=${item.id.videoId}`
      }))
    });

  } catch (error: any) {
    console.error('YouTube Search Error:', error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}
