import { NextRequest, NextResponse } from 'next/server';

// Configuration APIs - ORCHESTRATEUR INTELLIGENT MULTILINGUE
const DISCORD_BOT_TOKEN = process.env.DISCORD_BOT_TOKEN;
const MIDJOURNEY_CHANNEL_ID = '1297611734037291049';
const MIDJOURNEY_BOT_ID = '936929561302675456';
const LEONARDO_API_KEY = process.env.LEONARDO_API_KEY;
const REPLICATE_API_TOKEN = process.env.REPLICATE_API_TOKEN;

// APIs DE TRADUCTION MULTI-PROVIDER
const DEEPL_API_KEY = process.env.DEEPL_API_KEY;
const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
const GOOGLE_GEMINI_API_KEY = process.env.GOOGLE_GEMINI_API_KEY;
const COHERE_API_KEY = process.env.COHERE_API_KEY;

// ORCHESTRATEUR INTELLIGENT - DÉTECTION AUTOMATIQUE DE LANGUE
async function detectLanguageAndImprovePrompt(originalPrompt: string) {
  console.log("🔍 ORCHESTRATEUR INTELLIGENT - Analyse multilingue...");
  console.log("📝 Prompt original:", originalPrompt);

  try {
    // 1. DÉTECTION DE LANGUE + AMÉLIORATION AVEC OPENAI GPT-4
    if (OPENAI_API_KEY) {
      console.log("🧠 Analyse intelligente avec OpenAI GPT-4...");
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
            content: `Tu es un expert en prompts d'IA pour génération d'images. Ton rôle:
1. Détecter la langue du prompt (parmi 644+ langues/dialectes supportées)
2. Améliorer le prompt pour être TRÈS précis et détaillé
3. Traduire vers l'anglais optimisé pour Leonardo AI/Midjourney/Replicate
4. Ajouter des détails techniques pour une meilleure qualité

Réponds UNIQUEMENT avec un JSON:
{
  "detectedLanguage": "langue détectée",
  "originalMeaning": "sens exact du prompt original",
  "improvedPrompt": "prompt amélioré très détaillé en anglais",
  "technicalTags": "tags techniques pour IA"
}`
          }, {
            role: "user", 
            content: originalPrompt
          }],
          temperature: 0.3
        })
      });

      if (response.ok) {
        const data = await response.json();
        const analysis = JSON.parse(data.choices[0].message.content);
        console.log("✅ Analyse OpenAI réussie:", analysis);
        return analysis;
      }
    }

    // 2. FALLBACK - TRADUCTION DEEPL + AMÉLIORATION BASIQUE
    if (DEEPL_API_KEY) {
      console.log("🔄 Fallback - Traduction DeepL...");
      const response = await fetch('https://api-free.deepl.com/v2/translate', {
        method: 'POST',
        headers: {
          'Authorization': `DeepL-Auth-Key ${DEEPL_API_KEY}`,
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `text=${encodeURIComponent(originalPrompt)}&target_lang=EN&source_lang=auto`
      });

      if (response.ok) {
        const data = await response.json();
        const translatedText = data.translations[0].text;
        console.log("✅ Traduction DeepL:", translatedText);
        
        return {
          detectedLanguage: data.translations[0].detected_source_language,
          originalMeaning: originalPrompt,
          improvedPrompt: `${translatedText}, highly detailed, professional quality, 8K resolution`,
          technicalTags: "detailed, high-quality, professional"
        };
      }
    }

    // 3. FALLBACK FINAL - AMÉLIORATION BASIQUE
    console.log("🔄 Fallback final - Amélioration basique...");
    return {
      detectedLanguage: "unknown",
      originalMeaning: originalPrompt,
      improvedPrompt: `${originalPrompt}, highly detailed, professional quality, 8K resolution`,
      technicalTags: "detailed, high-quality"
    };

  } catch (error) {
    console.error("❌ Erreur orchestrateur:", error);
    return {
      detectedLanguage: "unknown",
      originalMeaning: originalPrompt,
      improvedPrompt: originalPrompt,
      technicalTags: ""
    };
  }
}

// SYSTÈME DE TRADUCTION ET AMÉLIORATION MULTILINGUE
async function enhancePromptMultilingual(originalPrompt: string, style: string) {
  try {
    console.log("🌍 AMÉLIORATION MULTILINGUE - 644+ LANGUES SUPPORTÉES");
    console.log("📝 Prompt original:", originalPrompt);
    
    // 1. Détecter si c'est déjà en anglais optimisé
    const englishKeywords = ['detailed', 'professional', 'realistic', 'photorealistic', '8K', 'masterpiece'];
    const isAlreadyOptimized = englishKeywords.some(keyword => 
      originalPrompt.toLowerCase().includes(keyword.toLowerCase())
    );
    
    if (isAlreadyOptimized) {
      console.log("✅ Prompt déjà optimisé en anglais");
      return originalPrompt;
    }
    
    // 2. Traduire vers l'anglais avec DeepL si nécessaire
    let englishPrompt = originalPrompt;
    
    if (DEEPL_API_KEY) {
      try {
        const translateResponse = await fetch('https://api-free.deepl.com/v2/translate', {
          method: 'POST',
          headers: {
            'Authorization': `DeepL-Auth-Key ${DEEPL_API_KEY}`,
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: new URLSearchParams({
            text: originalPrompt,
            target_lang: 'EN',
            preserve_formatting: '1'
          })
        });
        
        if (translateResponse.ok) {
          const translateData = await translateResponse.json();
          if (translateData.translations && translateData.translations[0]) {
            englishPrompt = translateData.translations[0].text;
            console.log("🔄 Traduit en anglais:", englishPrompt);
          }
        }
      } catch (error) {
        console.log("⚠️ Traduction échouée, utilisation du prompt original");
      }
    }
    
    // 3. Améliorer le prompt selon le style demandé
    let enhancedPrompt = englishPrompt;
    
    if (style === 'realistic') {
      enhancedPrompt = `${englishPrompt}, highly detailed, photorealistic, professional photography, 8K resolution, sharp focus, perfect lighting, masterpiece quality`;
    } else if (style === 'artistic') {
      enhancedPrompt = `${englishPrompt}, artistic masterpiece, creative composition, vibrant colors, digital art, beautiful aesthetic, award-winning artwork`;
    } else if (style === 'cartoon') {
      enhancedPrompt = `${englishPrompt}, cartoon style, animated character design, colorful illustration, fun and playful, cartoon artwork`;
    } else {
      enhancedPrompt = `${englishPrompt}, high quality, detailed, professional artwork, beautiful composition`;
    }
    
    console.log("✨ Prompt amélioré final:", enhancedPrompt);
    return enhancedPrompt;
    
  } catch (error) {
    console.error("❌ Erreur amélioration prompt:", error);
    return originalPrompt; // Fallback vers l'original
  }
}

// Provider 1: Midjourney via Discord
async function generateWithMidjourneyDiscord(prompt: string, style: string) {
  if (!DISCORD_BOT_TOKEN) {
    return { success: false, error: "Discord bot token not configured" };
  }

  try {
    console.log("🎨 PRIORITÉ 1: MIDJOURNEY AI GENERATION...");
    
    let enhancedPrompt = prompt;
    if (style === 'realistic') {
      enhancedPrompt = `${prompt} --style raw --quality 2 --ar 1:1 --v 6`;
    } else if (style === 'artistic') {
      enhancedPrompt = `${prompt} --style artistic --quality 2 --ar 1:1 --v 6`;
    } else {
      enhancedPrompt = `${prompt} --quality 2 --ar 1:1 --v 6`;
    }
    
    console.log("✨ Prompt Midjourney:", enhancedPrompt);

    const imagineResponse = await fetch(`https://discord.com/api/v10/channels/${MIDJOURNEY_CHANNEL_ID}/messages`, {
      method: 'POST',
      headers: {
        'Authorization': `Bot ${DISCORD_BOT_TOKEN}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        content: `/imagine prompt:${enhancedPrompt}`
      })
    });

    if (!imagineResponse.ok) {
      return { success: false, error: `Midjourney error: ${imagineResponse.status}` };
    }

    const messageData = await imagineResponse.json();
    console.log("📤 Midjourney - Message envoyé:", messageData.id);

    // Polling réduit
    let attempts = 0;
    const maxAttempts = 3;

    while (attempts < maxAttempts) {
      await new Promise(resolve => setTimeout(resolve, 10000));
      attempts++;

      const messagesResponse = await fetch(`https://discord.com/api/v10/channels/${MIDJOURNEY_CHANNEL_ID}/messages?limit=10`, {
        headers: { 'Authorization': `Bot ${DISCORD_BOT_TOKEN}` }
      });

      if (messagesResponse.ok) {
        const messages = await messagesResponse.json();
        for (const message of messages) {
          if (message.author.id === MIDJOURNEY_BOT_ID &&
              message.attachments &&
              message.attachments.length > 0 &&
              message.content.includes(prompt.substring(0, 15))) {
            return {
              success: true,
              imageUrl: message.attachments[0].url,
              provider: "Midjourney AI"
            };
          }
        }
      }
    }

    return { success: false, error: "Midjourney timeout" };
  } catch (error) {
    return { success: false, error: String(error) };
  }
}

// Provider 2: Leonardo AI - PRÉCISION AMÉLIORÉE PAR ORCHESTRATION
async function generateWithLeonardo(enhancedPrompt: string, style: string, analysisData: any) {
  if (!LEONARDO_API_KEY) {
    return { success: false, error: "Leonardo API key not configured" };
  }

  try {
    console.log("🎭 LEONARDO AI - Génération avec précision orchestrée...");
    console.log("📝 Prompt orchestré:", enhancedPrompt);
    console.log("🔍 Analyse intelligente:", analysisData);
    
    let modelId = "6bef9f1b-29cb-40c7-b9df-32b51c1f67d3";
    
    // Construction du prompt ultra-précis basé sur l'analyse intelligente
    let precisePrompt = `${enhancedPrompt}`;
    
    // Ajouter les tags techniques de l'analyse
    if (analysisData.technicalTags) {
      precisePrompt += `, ${analysisData.technicalTags}`;
    }
    
    if (style === 'realistic') {
      precisePrompt = `${precisePrompt}, ultra realistic, photorealistic, high detail, 8K resolution, professional photography`;
    } else if (style === 'artistic') {
      precisePrompt = `${precisePrompt}, artistic masterpiece, vibrant colors, creative composition`;
    }

    const response = await fetch('https://cloud.leonardo.ai/api/rest/v1/generations', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${LEONARDO_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        prompt: precisePrompt,
        modelId: modelId,
        width: 1024,
        height: 1024,
        num_images: 1,
        guidance_scale: 10, // Plus de guidance pour plus de précision
        num_inference_steps: 30,
        promptMagic: true,
        photoReal: style === 'realistic',
        alchemy: true
      })
    });

    if (response.ok) {
      const data = await response.json();
      const generationId = data.sdGenerationJob?.generationId;
      
      if (generationId) {
        // Polling pour récupérer l'image
        let attempts = 0;
        while (attempts < 20) {
          await new Promise(resolve => setTimeout(resolve, 3000));
          attempts++;
          
          const resultResponse = await fetch(`https://cloud.leonardo.ai/api/rest/v1/generations/${generationId}`, {
            headers: { 'Authorization': `Bearer ${LEONARDO_API_KEY}` }
          });
          
          if (resultResponse.ok) {
            const resultData = await resultResponse.json();
            if (resultData.generations_by_pk?.generated_images?.length > 0) {
              return {
                success: true,
                imageUrl: resultData.generations_by_pk.generated_images[0].url,
                provider: "Leonardo AI"
              };
            }
          }
        }
      }
    }

    return { success: false, error: "Leonardo generation failed" };
  } catch (error) {
    return { success: false, error: String(error) };
  }
}

// Provider 3: Replicate
async function generateWithReplicate(prompt: string, style: string) {
  if (!REPLICATE_API_TOKEN) {
    return { success: false, error: "Replicate API token not configured" };
  }

  try {
    console.log("🤖 PRIORITÉ 3: REPLICATE AI MODELS...");
    
    let enhancedPrompt = prompt;
    if (style === 'realistic') {
      enhancedPrompt = `${prompt}, photorealistic, highly detailed, 8K`;
    } else if (style === 'artistic') {
      enhancedPrompt = `${prompt}, digital art, artistic style`;
    }

    const response = await fetch('https://api.replicate.com/v1/predictions', {
      method: 'POST',
      headers: {
        'Authorization': `Token ${REPLICATE_API_TOKEN}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        version: "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
        input: {
          prompt: enhancedPrompt,
          width: 1024,
          height: 1024,
          num_outputs: 1
        }
      })
    });

    if (response.ok) {
      const prediction = await response.json();
      const predictionId = prediction.id;
      
      // Polling pour le résultat
      let attempts = 0;
      while (attempts < 30) {
        await new Promise(resolve => setTimeout(resolve, 3000));
        attempts++;
        
        const resultResponse = await fetch(`https://api.replicate.com/v1/predictions/${predictionId}`, {
          headers: { 'Authorization': `Token ${REPLICATE_API_TOKEN}` }
        });
        
        if (resultResponse.ok) {
          const result = await resultResponse.json();
          if (result.status === 'succeeded' && result.output && result.output.length > 0) {
            return {
              success: true,
              imageUrl: result.output[0],
              provider: "Replicate AI"
            };
          } else if (result.status === 'failed') {
            break;
          }
        }
      }
    }

    return { success: false, error: "Replicate generation failed" };
  } catch (error) {
    return { success: false, error: String(error) };
  }
}

export async function POST(request: NextRequest) {
  try {
    console.log("🌍 SYSTÈME MULTILINGUE IA - 644+ LANGUES - ORCHESTRATION INTELLIGENTE ✅");

    const body = await request.json();
    const { prompt, style = "realistic" } = body;

    if (!prompt) {
      return NextResponse.json({
        success: false,
        error: "Prompt requis"
      }, { status: 400 });
    }

    console.log("📝 Prompt original:", prompt);
    console.log("🎨 Style:", style);
    console.log("🔑 APIs configurées - Leonardo:", !!LEONARDO_API_KEY, "Replicate:", !!REPLICATE_API_TOKEN, "OpenAI:", !!OPENAI_API_KEY, "DeepL:", !!DEEPL_API_KEY);

    // ÉTAPE 1: ORCHESTRATION INTELLIGENTE - Analyse et amélioration du prompt
    console.log("� ORCHESTRATEUR INTELLIGENT - Analyse multilingue...");
    const analysisData = await detectLanguageAndImprovePrompt(prompt);
    
    console.log("✅ Analyse terminée:", {
      langue: analysisData.detectedLanguage,
      prompt_amélioré: analysisData.improvedPrompt
    });

    // ÉTAPE 2: GÉNÉRATION AVEC PRÉCISION AMÉLIORÉE

    // 1. Midjourney avec prompt orchestré
    const mjResult = await generateWithMidjourneyDiscord(analysisData.improvedPrompt, style);
    if (mjResult.success && mjResult.imageUrl) {
      return NextResponse.json({
        success: true,
        provider: "Midjourney AI Generation - Orchestrated",
        quality: "premium_ai_orchestrated",
        imageUrl: mjResult.imageUrl,
        prompt: analysisData.improvedPrompt,
        originalPrompt: prompt,
        promptAnalysis: analysisData,
        style: style,
        realGeneration: true
      });
    }

    // 2. Leonardo AI avec orchestration intelligente
    const leonardoResult = await generateWithLeonardo(analysisData.improvedPrompt, style, analysisData);
    if (leonardoResult.success && leonardoResult.imageUrl) {
      return NextResponse.json({
        success: true,
        provider: "Leonardo AI Generation - Orchestrated",
        quality: "premium_ai_orchestrated",
        imageUrl: leonardoResult.imageUrl,
        prompt: analysisData.improvedPrompt,
        originalPrompt: prompt,
        promptAnalysis: analysisData,
        style: style,
        realGeneration: true
      });
    }

    // 3. Replicate AI avec orchestration
    const replicateResult = await generateWithReplicate(analysisData.improvedPrompt, style);
    if (replicateResult.success && replicateResult.imageUrl) {
      return NextResponse.json({
        success: true,
        provider: "Replicate AI Models - Orchestrated",
        quality: "premium_ai_orchestrated",
        imageUrl: replicateResult.imageUrl,
        prompt: analysisData.improvedPrompt,
        originalPrompt: prompt,
        promptAnalysis: analysisData,
        style: style,
        realGeneration: true
      });
    }

    // Échec total - AUCUN FALLBACK DALLE
    return NextResponse.json({
      success: false,
      error: "Services de génération IA temporairement indisponibles - Orchestration intelligente activée",
      promptAnalysis: analysisData,
      message: `Prompt analysé en ${analysisData.detectedLanguage}, amélioré mais génération échouée`,
      providers_tried: ["Midjourney AI", "Leonardo AI", "Replicate AI"],
      leonardo_configured: !!LEONARDO_API_KEY,
      replicate_configured: !!REPLICATE_API_TOKEN
    }, { status: 503 });

  } catch (error) {
    console.error('❌ Erreur générale:', error);
    return NextResponse.json({
      success: false,
      error: "Erreur interne du serveur"
    }, { status: 500 });
  }
}
