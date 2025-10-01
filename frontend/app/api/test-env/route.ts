import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  return NextResponse.json({
    legnext_key_exists: !!process.env.LEGNEXT_MIDJOURNEY_KEY,
    legnext_key_length: process.env.LEGNEXT_MIDJOURNEY_KEY?.length || 0,
    goapi_key_exists: !!process.env.GOAPI_MIDJOURNEY_KEY,
    goapi_key_length: process.env.GOAPI_MIDJOURNEY_KEY?.length || 0,
    openai_key_exists: !!process.env.OPENAI_API_KEY,
    openai_key_length: process.env.OPENAI_API_KEY?.length || 0,
    legnext_key_starts: process.env.LEGNEXT_MIDJOURNEY_KEY?.substring(0, 10) || 'missing',
    openai_key_starts: process.env.OPENAI_API_KEY?.substring(0, 10) || 'missing'
  });
}
