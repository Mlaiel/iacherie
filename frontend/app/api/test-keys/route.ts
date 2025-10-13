import { NextRequest, NextResponse } from 'next/server';

export async function GET() {
  try {
    console.log("🔍 Testing API Keys availability...");
    
    const keys = {
      openai: !!process.env.OPENAI_API_KEY,
      openai_length: process.env.OPENAI_API_KEY?.length || 0,
      openai_prefix: process.env.OPENAI_API_KEY?.substring(0, 10) || "none",
      
      huggingface: !!process.env.HUGGINGFACE_API_KEY,
      huggingface_length: process.env.HUGGINGFACE_API_KEY?.length || 0,
      huggingface_prefix: process.env.HUGGINGFACE_API_KEY?.substring(0, 10) || "none",
      
      stability: !!process.env.STABILITY_API_KEY,
      gemini: !!process.env.GOOGLE_GEMINI_API_KEY,
      gemini_length: process.env.GOOGLE_GEMINI_API_KEY?.length || 0,
      
      all_env_vars: Object.keys(process.env).filter(key => key.includes('API_KEY')).length
    };

    console.log("🔍 Available API Keys:", keys);

    return NextResponse.json({
      success: true,
      keys,
      message: "API Key status check"
    });

  } catch (error) {
    console.error("❌ Error checking API keys:", error);
    return NextResponse.json({ 
      error: "Failed to check API keys",
      details: error instanceof Error ? error.message : "Unknown error"
    }, { status: 500 });
  }
}