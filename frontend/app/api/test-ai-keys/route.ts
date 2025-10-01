import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  return NextResponse.json({
    leonardo_configured: !!process.env.LEONARDO_API_KEY,
    leonardo_key_length: process.env.LEONARDO_API_KEY?.length || 0,
    leonardo_key_starts: process.env.LEONARDO_API_KEY?.substring(0, 15) || 'missing',
    
    replicate_configured: !!process.env.REPLICATE_API_TOKEN,
    replicate_key_length: process.env.REPLICATE_API_TOKEN?.length || 0,
    replicate_key_starts: process.env.REPLICATE_API_TOKEN?.substring(0, 15) || 'missing',
    
    discord_configured: !!process.env.DISCORD_BOT_TOKEN,
    midjourney_configured: !!process.env.GOAPI_MIDJOURNEY_KEY,
    
    status: "Pure AI Generation System Ready ✅"
  });
}