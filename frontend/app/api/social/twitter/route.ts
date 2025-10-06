/**
 * API Route - Twitter/X Post
 * Utilise les 9 clés Twitter configurées
 */

import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const { text, media, schedule } = await request.json();

    if (!text) {
      return NextResponse.json(
        { error: 'Le texte est requis' },
        { status: 400 }
      );
    }

    // Twitter API v2
    const response = await fetch('https://api.twitter.com/2/tweets', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.TWITTER_BEARER_TOKEN}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        text: text.slice(0, 280) // Limite Twitter
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(`Twitter API error: ${error.detail || response.statusText}`);
    }

    const data = await response.json();

    return NextResponse.json({
      success: true,
      platform: 'twitter',
      tweetId: data.data.id,
      url: `https://twitter.com/user/status/${data.data.id}`,
      text: data.data.text
    });

  } catch (error: any) {
    console.error('Twitter API Error:', error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}

// GET - Récupérer les tweets récents
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const userId = searchParams.get('userId') || 'me';

    const response = await fetch(
      `https://api.twitter.com/2/users/${userId}/tweets?max_results=10`,
      {
        headers: {
          'Authorization': `Bearer ${process.env.TWITTER_BEARER_TOKEN}`
        }
      }
    );

    if (!response.ok) {
      throw new Error(`Twitter API error: ${response.statusText}`);
    }

    const data = await response.json();

    return NextResponse.json({
      success: true,
      tweets: data.data || []
    });

  } catch (error: any) {
    console.error('Twitter GET Error:', error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}
