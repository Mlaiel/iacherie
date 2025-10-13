/**
 * TEST DIRECT OPENAI TEXT API
 */

import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    console.log("🧪 TESTING OPENAI TEXT API DIRECTLY");
    
    const body = await request.json();
    const { prompt = "Écris un court poème sur un chien mignon" } = body;
    
    const openaiKey = process.env.OPENAI_API_KEY;
    
    console.log("🔑 OpenAI Key exists:", !!openaiKey);
    console.log("🔑 OpenAI Key starts with sk-:", openaiKey?.startsWith('sk-'));
    
    if (!openaiKey || !openaiKey.startsWith('sk-')) {
      return NextResponse.json({ 
        error: "OpenAI API key not found or invalid format",
        keyExists: !!openaiKey,
        startsWithSk: openaiKey?.startsWith('sk-')
      }, { status: 400 });
    }
    
    console.log("🚀 Making OpenAI TEXT API call...");
    
    const openaiResponse = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${openaiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: "gpt-3.5-turbo",
        messages: [
          { role: "system", content: "Tu es un poète créatif. Écris des poèmes courts et mignons." },
          { role: "user", content: prompt }
        ],
        max_tokens: 150,
        temperature: 0.8
      })
    });
    
    console.log("📡 OpenAI TEXT Response status:", openaiResponse.status);
    
    if (openaiResponse.ok) {
      const data = await openaiResponse.json();
      console.log("✅ RÉEL TEXTE GÉNÉRÉ AVEC OPENAI GPT-4!");
      
      return NextResponse.json({
        success: true,
        text: data.choices[0].message.content,
        prompt: prompt,
        provider: "OpenAI GPT-4o-mini",
        generatedAt: new Date().toISOString(),
        REAL: true,
        NO_FALLBACK: true
      });
    } else {
      const errorText = await openaiResponse.text();
      console.log("❌ OpenAI TEXT API Error:", errorText);
      
      return NextResponse.json({ 
        error: "OpenAI TEXT API failed",
        status: openaiResponse.status,
        details: errorText
      }, { status: openaiResponse.status });
    }

  } catch (error) {
    console.error("❌ Test OpenAI TEXT error:", error);
    return NextResponse.json({ 
      error: "Test failed",
      details: error instanceof Error ? error.message : "Unknown error"
    }, { status: 500 });
  }
}