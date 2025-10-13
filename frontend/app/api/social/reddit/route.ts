/**
 * API Route - Reddit Post
 * Utilise les 2 clés Reddit configurées
 */

import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const { title, text, url, subreddit } = await request.json();

    if (!title || !subreddit) {
      return NextResponse.json(
        { error: 'Le titre et le subreddit sont requis' },
        { status: 400 }
      );
    }

    // Obtenir un token d'accès
    const authResponse = await fetch('https://www.reddit.com/api/v1/access_token', {
      method: 'POST',
      headers: {
        'Authorization': `Basic ${Buffer.from(
          `${process.env.REDDIT_CLIENT_ID}:${process.env.REDDIT_CLIENT_SECRET}`
        ).toString('base64')}`,
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: 'grant_type=client_credentials'
    });

    if (!authResponse.ok) {
      throw new Error(`Reddit auth error: ${authResponse.statusText}`);
    }

    const authData = await authResponse.json();
    const accessToken = authData.access_token;

    // Poster sur Reddit
    const kind = url ? 'link' : 'self';
    const postData: any = {
      sr: subreddit,
      title,
      kind
    };

    if (kind === 'self') {
      postData.text = text || '';
    } else {
      postData.url = url;
    }

    const response = await fetch('https://oauth.reddit.com/api/submit', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'IACherie/1.0'
      },
      body: new URLSearchParams(postData)
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(`Reddit API error: ${error.message || response.statusText}`);
    }

    const data = await response.json();

    return NextResponse.json({
      success: true,
      platform: 'reddit',
      postId: data.json.data.id,
      url: data.json.data.url,
      permalink: `https://reddit.com${data.json.data.permalink}`
    });

  } catch (error: any) {
    console.error('Reddit API Error:', error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}

// GET - Récupérer les posts d'un subreddit
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const subreddit = searchParams.get('subreddit') || 'popular';

    const response = await fetch(
      `https://www.reddit.com/r/${subreddit}/hot.json?limit=10`,
      {
        headers: {
          'User-Agent': 'IACherie/1.0'
        }
      }
    );

    if (!response.ok) {
      throw new Error(`Reddit API error: ${response.statusText}`);
    }

    const data = await response.json();

    return NextResponse.json({
      success: true,
      posts: data.data.children.map((child: any) => child.data)
    });

  } catch (error: any) {
    console.error('Reddit GET Error:', error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}
