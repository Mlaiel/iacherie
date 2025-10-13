/**
 * TEST DIRECT OPENAI API
 */

import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    console.log("🧪 TESTING OPENAI API DIRECTLY");
    
    const body = await request.json();
    const { prompt = "Test image of a cute dog" } = body;
    
    const openaiKey = process.env.OPENAI_API_KEY;
    
    console.log("🔑 OpenAI Key exists:", !!openaiKey);
    console.log("🔑 OpenAI Key length:", openaiKey?.length || 0);
    console.log("🔑 OpenAI Key preview:", openaiKey?.substring(0, 15) + "...");
    
    if (!openaiKey) {
      return NextResponse.json({ 
        error: "OpenAI API key not found",
        envChecked: process.env.NODE_ENV
      }, { status: 400 });
    }
    
    console.log("🚀 Making OpenAI API call...");
    
    const openaiResponse = await fetch('https://api.openai.com/v1/images/generations', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${openaiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: "dall-e-2",
        prompt: prompt,
        n: 1,
        size: "1024x1024"
      })
    });
    
    console.log("📡 OpenAI Response status:", openaiResponse.status);
    
    if (openaiResponse.ok) {
      const data = await openaiResponse.json();
      console.log("✅ RÉELLE IMAGE GÉNÉRÉE AVEC OPENAI DALL-E 3!");
      
      return NextResponse.json({
        success: true,
        imageUrl: data.data[0].url,
        prompt: prompt,
        provider: "OpenAI DALL-E 3",
        generatedAt: new Date().toISOString(),
        REAL: true,
        NO_FALLBACK: true
      });
    } else {
      const errorText = await openaiResponse.text();
      console.log("❌ OpenAI API Error:", errorText);
      
      return NextResponse.json({ 
        error: "OpenAI API failed",
        status: openaiResponse.status,
        details: errorText
      }, { status: openaiResponse.status });
    }

  } catch (error) {
    console.error("❌ Test OpenAI error:", error);
    return NextResponse.json({ 
      error: "Test failed",
      details: error instanceof Error ? error.message : "Unknown error"
    }, { status: 500 });
  }
}