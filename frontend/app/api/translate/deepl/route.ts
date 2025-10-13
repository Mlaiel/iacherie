/**
 * API Route - DeepL Translation
 */

import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const { text, targetLang, sourceLang } = await request.json();

    if (!text || !targetLang) {
      return NextResponse.json(
        { error: 'Text et langue cible requis' },
        { status: 400 }
      );
    }

    const params = new URLSearchParams({
      auth_key: process.env.DEEPL_API_KEY!,
      text,
      target_lang: targetLang.toUpperCase()
    });

    if (sourceLang) {
      params.append('source_lang', sourceLang.toUpperCase());
    }

    const response = await fetch('https://api-free.deepl.com/v2/translate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: params
    });

    if (!response.ok) {
      throw new Error(`DeepL API error: ${response.statusText}`);
    }

    const data = await response.json();

    return NextResponse.json({
      success: true,
      text: data.translations[0].text,
      detectedSourceLang: data.translations[0].detected_source_language
    });

  } catch (error: any) {
    console.error('DeepL Error:', error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}
