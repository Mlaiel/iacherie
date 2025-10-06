/**
 * API Route - TinyURL
 */

import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const { url, alias } = await request.json();

    if (!url) {
      return NextResponse.json(
        { error: 'URL requise' },
        { status: 400 }
      );
    }

    const params: any = {
      url,
      domain: 'tinyurl.com'
    };

    if (alias) {
      params.alias = alias;
    }

    const response = await fetch('https://api.tinyurl.com/create', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.TINYURL_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(params)
    });

    if (!response.ok) {
      throw new Error(`TinyURL API error: ${response.statusText}`);
    }

    const data = await response.json();

    return NextResponse.json({
      success: true,
      shortUrl: data.data.tiny_url,
      alias: data.data.alias
    });

  } catch (error: any) {
    console.error('TinyURL Error:', error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}
