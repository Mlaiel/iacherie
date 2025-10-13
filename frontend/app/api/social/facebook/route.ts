/**
 * API Route - Facebook Post
 * Utilise les 3 clés Facebook configurées
 */

import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const { message, link, imageUrl, pageId } = await request.json();

    if (!message && !link && !imageUrl) {
      return NextResponse.json(
        { error: 'Le contenu est requis (message, lien ou image)' },
        { status: 400 }
      );
    }

    // Facebook Graph API
    const postData: any = {
      access_token: process.env.FACEBOOK_ACCESS_TOKEN
    };

    if (message) postData.message = message;
    if (link) postData.link = link;
    if (imageUrl) postData.url = imageUrl;

    const response = await fetch(
      `https://graph.facebook.com/v18.0/${pageId || 'me'}/feed`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(postData)
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(`Facebook API error: ${error.error?.message || response.statusText}`);
    }

    const data = await response.json();

    return NextResponse.json({
      success: true,
      platform: 'facebook',
      postId: data.id,
      url: `https://facebook.com/${data.id}`
    });

  } catch (error: any) {
    console.error('Facebook API Error:', error);
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
    const pageId = searchParams.get('pageId') || 'me';

    const response = await fetch(
      `https://graph.facebook.com/v18.0/${pageId}/posts?fields=id,message,created_time,permalink_url&access_token=${process.env.FACEBOOK_ACCESS_TOKEN}`
    );

    if (!response.ok) {
      throw new Error(`Facebook API error: ${response.statusText}`);
    }

    const data = await response.json();

    return NextResponse.json({
      success: true,
      posts: data.data || []
    });

  } catch (error: any) {
    console.error('Facebook GET Error:', error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}
