/**
 * API Route - LibreTranslate
 */

import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const { text, targetLang, sourceLang = 'auto' } = await request.json();

    if (!text || !targetLang) {
      return NextResponse.json(
        { error: 'Text et langue cible requis' },
        { status: 400 }
      );
    }

    const libretranslateUrl = process.env.LIBRETRANSLATE_URL || 'https://libretranslate.com';

    const response = await fetch(`${libretranslateUrl}/translate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        q: text,
        source: sourceLang,
        target: targetLang,
        format: 'text'
      })
    });

    if (!response.ok) {
      throw new Error(`LibreTranslate API error: ${response.statusText}`);
    }

    const data = await response.json();

    return NextResponse.json({
      success: true,
      text: data.translatedText
    });

  } catch (error: any) {
    console.error('LibreTranslate Error:', error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}
