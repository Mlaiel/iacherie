import { NextRequest, NextResponse } from 'next/server';

// TEST DE L'ORCHESTRATEUR INTELLIGENT MULTILINGUE
export async function POST(request: NextRequest) {
  try {
    const { prompt, testLanguage } = await request.json();

    console.log("🔬 TEST ORCHESTRATEUR INTELLIGENT");
    console.log("📝 Prompt de test:", prompt);
    console.log("🌍 Langue de test:", testLanguage);

    // Configuration APIs
    const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
    const DEEPL_API_KEY = process.env.DEEPL_API_KEY;
    const GOOGLE_GEMINI_API_KEY = process.env.GOOGLE_GEMINI_API_KEY;
    const COHERE_API_KEY = process.env.COHERE_API_KEY;

    const testResults = {
      timestamp: new Date().toISOString(),
      originalPrompt: prompt,
      testLanguage: testLanguage,
      apiStatus: {
        openai: !!OPENAI_API_KEY,
        deepl: !!DEEPL_API_KEY,
        gemini: !!GOOGLE_GEMINI_API_KEY,
        cohere: !!COHERE_API_KEY
      },
      orchestrationResults: {
        openai: null as any,
        deepl: null as any,
        gemini: null as any
      }
    };

    // 1. TEST OPENAI GPT-4 - ORCHESTRATION INTELLIGENTE
    if (OPENAI_API_KEY) {
      try {
        console.log("🧠 Test OpenAI GPT-4 - Orchestration...");
        const response = await fetch('https://api.openai.com/v1/chat/completions', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${OPENAI_API_KEY}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            model: "gpt-4o-mini",
            messages: [{
              role: "system",
              content: `Tu es un expert en prompts d'IA pour génération d'images multilingue. Analyse ce prompt:
1. Détecte la langue exacte (parmi 644+ langues supportées)
2. Comprends le sens exact et le contexte culturel
3. Améliore le prompt pour Leonardo AI/Midjourney avec détails techniques
4. Traduis en anglais optimisé pour IA
5. Ajoute des tags techniques pour meilleure qualité

Réponds UNIQUEMENT avec un JSON valide:
{
  "detectedLanguage": "langue détectée avec code ISO",
  "originalMeaning": "sens exact du prompt original",
  "culturalContext": "contexte culturel si applicable",
  "improvedPrompt": "prompt amélioré très détaillé en anglais",
  "technicalTags": "tags techniques pour IA",
  "confidenceScore": "score de confiance 0-100"
}`
            }, {
              role: "user", 
              content: prompt
            }],
            temperature: 0.2
          })
        });

        if (response.ok) {
          const data = await response.json();
          const analysis = JSON.parse(data.choices[0].message.content);
          testResults.orchestrationResults.openai = {
            success: true,
            analysis: analysis,
            responseTime: Date.now()
          };
          console.log("✅ OpenAI orchestration success:", analysis);
        } else {
          testResults.orchestrationResults.openai = {
            success: false,
            error: `HTTP ${response.status}`
          };
        }
      } catch (error) {
        testResults.orchestrationResults.openai = {
          success: false,
          error: error.message
        };
      }
    }

    // 2. TEST DEEPL - TRADUCTION PREMIUM
    if (DEEPL_API_KEY) {
      try {
        console.log("🔄 Test DeepL - Traduction premium...");
        const response = await fetch('https://api-free.deepl.com/v2/translate', {
          method: 'POST',
          headers: {
            'Authorization': `DeepL-Auth-Key ${DEEPL_API_KEY}`,
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: `text=${encodeURIComponent(prompt)}&target_lang=EN&source_lang=auto`
        });

        if (response.ok) {
          const data = await response.json();
          testResults.orchestrationResults.deepl = {
            success: true,
            translation: data.translations[0].text,
            detectedLanguage: data.translations[0].detected_source_language,
            responseTime: Date.now()
          };
          console.log("✅ DeepL translation success");
        } else {
          testResults.orchestrationResults.deepl = {
            success: false,
            error: `HTTP ${response.status}`
          };
        }
      } catch (error) {
        testResults.orchestrationResults.deepl = {
          success: false,
          error: error.message
        };
      }
    }

    // 3. TEST GOOGLE GEMINI - ANALYSE ALTERNATIVE
    if (GOOGLE_GEMINI_API_KEY) {
      try {
        console.log("💎 Test Google Gemini - Analyse alternative...");
        const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=${GOOGLE_GEMINI_API_KEY}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            contents: [{
              parts: [{
                text: `Analyse ce prompt pour génération d'images IA: "${prompt}". Détecte la langue, améliore-le pour Leonardo AI/Midjourney en anglais avec détails techniques. Réponds uniquement en JSON: {"language": "...", "improved": "...", "tags": "..."}`
              }]
            }]
          })
        });

        if (response.ok) {
          const data = await response.json();
          const content = data.candidates[0].content.parts[0].text;
          testResults.orchestrationResults.gemini = {
            success: true,
            analysis: content,
            responseTime: Date.now()
          };
          console.log("✅ Gemini analysis success");
        } else {
          testResults.orchestrationResults.gemini = {
            success: false,
            error: `HTTP ${response.status}`
          };
        }
      } catch (error) {
        testResults.orchestrationResults.gemini = {
          success: false,
          error: error.message
        };
      }
    }

    return NextResponse.json({
      success: true,
      message: "Test d'orchestration intelligent terminé",
      results: testResults,
      summary: {
        apisConfigured: Object.values(testResults.apiStatus).filter(Boolean).length,
        orchestrationSuccess: Object.values(testResults.orchestrationResults).filter((r: any) => r && r.success).length,
        multilingual: true,
        supportedLanguages: "644+"
      }
    });

  } catch (error) {
    console.error("❌ Erreur test orchestration:", error);
    return NextResponse.json({
      success: false,
      error: "Erreur lors du test d'orchestration",
      details: error.message
    }, { status: 500 });
  }
}

export async function GET() {
  return NextResponse.json({
    message: "Endpoint de test pour l'orchestrateur intelligent multilingue",
    usage: "POST avec { prompt: 'votre prompt', testLanguage: 'langue optionnelle' }",
    capabilities: [
      "Détection automatique de langue (644+ langues)",
      "Orchestration intelligente OpenAI + DeepL + Gemini",
      "Amélioration de prompts pour Leonardo AI/Midjourney",
      "Traduction premium avec contexte culturel",
      "Tags techniques optimisés pour IA"
    ]
  });
}