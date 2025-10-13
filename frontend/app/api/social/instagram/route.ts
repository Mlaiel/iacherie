/**
 * API Route - Instagram Post
 * Utilise les 4 clés Instagram configurées
 */

import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const { imageUrl, caption, userId } = await request.json();

    if (!imageUrl) {
      return NextResponse.json(
        { error: 'L\'image est requise' },
        { status: 400 }
      );
    }

    // Instagram Graph API - Créer un conteneur de média
    const containerResponse = await fetch(
      `https://graph.facebook.com/v18.0/${userId || 'me'}/media`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          image_url: imageUrl,
          caption: caption || '',
          access_token: process.env.INSTAGRAM_ACCESS_TOKEN
        })
      }
    );

    if (!containerResponse.ok) {
      const error = await containerResponse.json();
      throw new Error(`Instagram API error: ${error.error?.message || containerResponse.statusText}`);
    }

    const containerData = await containerResponse.json();
    const creationId = containerData.id;

    // Publier le conteneur
    const publishResponse = await fetch(
      `https://graph.facebook.com/v18.0/${userId || 'me'}/media_publish`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          creation_id: creationId,
          access_token: process.env.INSTAGRAM_ACCESS_TOKEN
        })
      }
    );

    if (!publishResponse.ok) {
      const error = await publishResponse.json();
      throw new Error(`Instagram publish error: ${error.error?.message || publishResponse.statusText}`);
    }

    const publishData = await publishResponse.json();

    return NextResponse.json({
      success: true,
      platform: 'instagram',
      postId: publishData.id,
      url: `https://instagram.com/p/${publishData.id}`
    });

  } catch (error: any) {
    console.error('Instagram API Error:', error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}

// GET - Récupérer les posts récents
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const userId = searchParams.get('userId') || 'me';

    const response = await fetch(
      `https://graph.facebook.com/v18.0/${userId}/media?fields=id,caption,media_type,media_url,thumbnail_url,permalink,timestamp&access_token=${process.env.INSTAGRAM_ACCESS_TOKEN}`
    );

    if (!response.ok) {
      throw new Error(`Instagram API error: ${response.statusText}`);
    }

    const data = await response.json();

    return NextResponse.json({
      success: true,
      posts: data.data || []
    });

  } catch (error: any) {
    console.error('Instagram GET Error:', error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}
