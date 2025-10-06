import { NextRequest, NextResponse } from 'next/server';
import { orchestrate } from '@/lib/api-orchestrator';
import { detectLanguage, translateText } from '@/lib/language-manager';

// Configuration APIs REELLES
const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
const LEONARDO_API_KEY = process.env.LEONARDO_API_KEY;
const REPLICATE_API_TOKEN = process.env.REPLICATE_API_TOKEN;
const DEEPL_API_KEY = process.env.DEEPL_API_KEY;
const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY;

console.log("🎨 CONFIGURATION APIs IMAGE:");
console.log("OpenAI DALL-E 3:", OPENAI_API_KEY ? "✅" : "❌");
console.log("Leonardo AI:", LEONARDO_API_KEY ? "✅" : "❌");
console.log("Replicate:", REPLICATE_API_TOKEN ? "✅" : "❌");

interface ImageGenerationRequest {
  prompt: string;
  style?: string;
  quality?: 'draft' | 'standard' | 'premium' | 'ultra';
  size?: string;
  provider?: 'auto' | 'dalle3' | 'leonardo' | 'replicate';
  model_id?: string; // ID du modèle spécifique (ex: internal-diffusion-xl)
  model?: string; // Alias pour model_id
  prefer_internal?: boolean;
}

async function enhancePromptWithAI(originalPrompt: string, style: string, quality: string) {
  console.log("🧠 AMELIORATION INTELLIGENTE DU PROMPT");
  
  try {
    if (ANTHROPIC_API_KEY) {
      console.log("🤖 Amelioration avec Claude...");
      
      const response = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
          'x-api-key': ANTHROPIC_API_KEY,
          'anthropic-version': '2023-06-01',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: 'claude-sonnet-4.5-20241022',
          max_tokens: 500,
          messages: [{
            role: 'user',
            content: `Improve this image prompt for ${style} style, ${quality} quality. Translate to English if needed. Add technical details. Return only JSON: {detectedLanguage, improvedPrompt, technicalDetails}\n\nPrompt: "${originalPrompt}"`
          }]
        })
      });

      if (response.ok) {
        const data = await response.json();
        const result = JSON.parse(data.content[0].text);
        console.log("✅ Prompt ameliore:", result.improvedPrompt);
        return result.improvedPrompt;
      }
    }

    console.log("🔄 Amelioration basique...");
    let enhanced = originalPrompt;

    if (DEEPL_API_KEY && /[\u0600-\u06FF\u0750-\u077F\u4E00-\u9FFF\u3040-\u309F\u30A0-\u30FF]/.test(originalPrompt)) {
      try {
        const translateResponse = await fetch('https://api-free.deepl.com/v2/translate', {
          method: 'POST',
          headers: {
            'Authorization': `DeepL-Auth-Key ${DEEPL_API_KEY}`,
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: `text=${encodeURIComponent(originalPrompt)}&target_lang=EN`
        });

        if (translateResponse.ok) {
          const data = await translateResponse.json();
          enhanced = data.translations[0].text;
          console.log("🌍 Traduit:", enhanced);
        }
      } catch (error) {
        console.log("⚠️ Traduction echouee");
      }
    }

    const qualityEnhancements = {
      draft: '',
      standard: ', high quality, detailed',
      premium: ', highly detailed, professional quality, perfect composition, 8K resolution',
      ultra: ', masterpiece quality, ultra detailed, professional photography, perfect lighting, cinematic composition, 8K UHD, award-winning'
    };

    const styleEnhancements = {
      realistic: ', photorealistic, professional photography, sharp focus',
      artistic: ', digital art masterpiece, vibrant colors, artistic composition',
      cinematic: ', cinematic lighting, movie quality, dramatic atmosphere',
      minimalist: ', clean minimalist design, elegant simplicity',
      '3d': ', 3D render, octane render, unreal engine 5'
    };

    enhanced += (styleEnhancements[style] || '');
    enhanced += (qualityEnhancements[quality] || qualityEnhancements.standard);

    console.log("✨ Prompt final:", enhanced);
    return enhanced;

  } catch (error) {
    console.error("❌ Erreur amelioration:", error);
    return originalPrompt;
  }
}

async function generateWithDALLE3(prompt: string, quality: string, size: string = '1024x1024') {
  if (!OPENAI_API_KEY) {
    throw new Error('OpenAI API key non configuree');
  }

  console.log("🎨 DALL-E 3 GENERATION (PREMIUM)");

  try {
    const response = await fetch('https://api.openai.com/v1/images/generations', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${OPENAI_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'dall-e-3',
        prompt: prompt,
        n: 1,
        size: size,
        quality: quality === 'ultra' || quality === 'premium' ? 'hd' : 'standard',
        style: 'vivid'
      })
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`DALL-E 3 error: ${response.status} - ${error}`);
    }

    const data = await response.json();
    console.log("✅ DALL-E 3 - Image generee avec succes");
    
    return {
      success: true,
      imageUrl: data.data[0].url,
      revisedPrompt: data.data[0].revised_prompt,
      provider: 'dalle3',
      model: 'dall-e-3',
      quality: quality,
      cost: quality === 'ultra' || quality === 'premium' ? 0.08 : 0.04
    };

  } catch (error) {
    console.error("❌ Erreur DALL-E 3:", error);
    throw error;
  }
}

async function generateWithLeonardo(prompt: string, quality: string) {
  if (!LEONARDO_API_KEY) {
    throw new Error('Leonardo API key non configuree');
  }

  console.log("🎨 LEONARDO AI GENERATION (OPTIMAL)");

  try {
    const response = await fetch('https://cloud.leonardo.ai/api/rest/v1/generations', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${LEONARDO_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        prompt: prompt,
        modelId: 'b24e16ff-06e3-43eb-8d33-4416c2d75876',
        width: 1024,
        height: 1024,
        num_images: 1,
        guidance_scale: quality === 'draft' ? 5 : quality === 'standard' ? 7 : 10,
        num_inference_steps: quality === 'draft' ? 20 : quality === 'standard' ? 30 : 50
      })
    });

    if (!response.ok) {
      throw new Error(`Leonardo error: ${response.status}`);
    }

    const data = await response.json();
    const generationId = data.sdGenerationJob.generationId;

    console.log("⏳ Generation Leonardo en cours...");

    let imageUrl = null;
    let attempts = 0;
    const maxAttempts = 30;

    while (!imageUrl && attempts < maxAttempts) {
      await new Promise(resolve => setTimeout(resolve, 2000));

      const checkResponse = await fetch(`https://cloud.leonardo.ai/api/rest/v1/generations/${generationId}`, {
        headers: {
          'Authorization': `Bearer ${LEONARDO_API_KEY}`,
        }
      });

      if (checkResponse.ok) {
        const checkData = await checkResponse.json();
        
        if (checkData.generations_by_pk?.status === 'COMPLETE' && checkData.generations_by_pk.generated_images?.length > 0) {
          imageUrl = checkData.generations_by_pk.generated_images[0].url;
        }
      }

      attempts++;
    }

    if (!imageUrl) {
      throw new Error('Timeout: Leonardo generation took too long');
    }

    console.log("✅ Leonardo AI - Image generee avec succes");

    return {
      success: true,
      imageUrl: imageUrl,
      provider: 'leonardo',
      model: 'Leonardo Kino XL',
      quality: quality,
      cost: 0.015
    };

  } catch (error) {
    console.error("❌ Erreur Leonardo:", error);
    throw error;
  }
}

async function generateWithReplicate(prompt: string, quality: string) {
  if (!REPLICATE_API_TOKEN) {
    throw new Error('Replicate API token non configure');
  }

  console.log("🚀 REPLICATE GENERATION (ECONOMIQUE)");

  try {
    const response = await fetch('https://api.replicate.com/v1/predictions', {
      method: 'POST',
      headers: {
        'Authorization': `Token ${REPLICATE_API_TOKEN}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        version: 'black-forest-labs/flux-1.1-pro',
        input: {
          prompt: prompt,
          aspect_ratio: '1:1',
          output_format: 'png',
          output_quality: quality === 'draft' ? 70 : quality === 'standard' ? 85 : 95
        }
      })
    });

    if (!response.ok) {
      throw new Error(`Replicate error: ${response.status}`);
    }

    const prediction = await response.json();
    console.log("⏳ Generation Replicate en cours...");

    let result = prediction;
    let attempts = 0;
    const maxAttempts = 30;

    while (result.status !== 'succeeded' && result.status !== 'failed' && attempts < maxAttempts) {
      await new Promise(resolve => setTimeout(resolve, 1500));

      const checkResponse = await fetch(`https://api.replicate.com/v1/predictions/${result.id}`, {
        headers: {
          'Authorization': `Token ${REPLICATE_API_TOKEN}`,
        }
      });

      result = await checkResponse.json();
      attempts++;
    }

    if (result.status === 'failed') {
      throw new Error('Replicate generation failed');
    }

    if (!result.output) {
      throw new Error('No output from Replicate');
    }

    console.log("✅ Replicate - Image generee avec succes");

    return {
      success: true,
      imageUrl: result.output,
      provider: 'replicate',
      model: 'Flux 1.1 Pro',
      quality: quality,
      cost: 0.008
    };

  } catch (error) {
    console.error("❌ Erreur Replicate:", error);
    throw error;
  }
}

async function generateImageIntelligent(request: ImageGenerationRequest) {
  const { prompt, style = 'realistic', quality = 'standard', size = '1024x1024', provider = 'auto', model_id, model } = request;

  // Utiliser model_id ou model (compatibilité)
  const selectedModel = model_id || model;

  console.log("🎯 ORCHESTRATEUR INTELLIGENT");
  console.log("📝 Prompt:", prompt);
  console.log("🎨 Style:", style);
  console.log("💎 Qualite:", quality);
  console.log("🤖 Model:", selectedModel);

  // ========================================
  // 🆓 SI MODÈLE INTERNE SÉLECTIONNÉ
  // ========================================
  if (selectedModel && selectedModel.startsWith('internal-')) {
    console.log("🆓 MODÈLE INTERNE GRATUIT SÉLECTIONNÉ:", selectedModel);
    
    try {
      // Appeler le backend Python pour utiliser le modèle interne
      const backendResponse = await fetch('http://localhost:8000/api/generate/image', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: prompt,
          model: selectedModel,
          style: style,
          quality: quality,
          size: size,
          prefer_internal: true
        })
      });

      if (backendResponse.ok) {
        const data = await backendResponse.json();
        console.log("✅ Modèle interne - Génération réussie:", data);
        
        return {
          success: true,
          imageUrl: data.images?.[0]?.url || data.url || data.image_url,
          provider: 'internal',
          model: selectedModel,
          quality: quality,
          cost: 0,
          originalPrompt: prompt,
          enhancedPrompt: data.images?.[0]?.revised_prompt || prompt,
          internal: true,
          timestamp: new Date().toISOString()
        };
      } else {
        const errorData = await backendResponse.json();
        console.log("⚠️ Modèle interne échoué:", errorData);
        console.log("🔄 Fallback vers APIs externes...");
      }
    } catch (error) {
      console.error("❌ Erreur modèle interne:", error);
      console.log("🔄 Fallback vers APIs externes...");
    }
  }

  const enhancedPrompt = await enhancePromptWithAI(prompt, style, quality);

  let selectedProvider = provider;

  // ========================================
  // 🎼 ORCHESTRATION INTELLIGENTE
  // ========================================
  if (provider === 'auto') {
    console.log('🎼 MAESTRO: Sélection intelligente du meilleur provider image...');
    
    // Déterminer le useCase basé sur le style
    const useCaseMap: Record<string, string> = {
      'realistic': 'hero-image',
      'artistic': 'creative',
      'cartoon': 'thumbnail',
      'default': 'social-post'
    };

    const orchestrationResult = orchestrate({
      contentType: 'image',
      quality: quality as 'draft' | 'standard' | 'premium' | 'ultra',
      useCase: useCaseMap[style] || 'social-post',
      budget: quality === 'ultra' ? undefined : 0.05 // Budget flexible sauf ultra
    });

    console.log(`✅ MAESTRO IMAGE: ${orchestrationResult.provider} sélectionné`);
    console.log(`💰 ${orchestrationResult.reasoning}`);
    if (orchestrationResult.estimatedSavings) {
      console.log(`💵 Économie: $${orchestrationResult.estimatedSavings.toFixed(3)} vs ${orchestrationResult.alternativeProvider}`);
    }

    // Mapper les providers de l'orchestrateur aux providers de l'API
    const providerMap: Record<string, 'dalle3' | 'leonardo' | 'replicate'> = {
      'replicate-flux': 'replicate',
      'leonardo-xl': 'leonardo',
      'leonardo-phoenix': 'leonardo',
      'openai-dalle3': 'dalle3',
      'openai-dalle3-hd': 'dalle3',
      'pexels': 'dalle3', // Fallback à DALL-E si stock demandé
      'unsplash': 'dalle3'
    };

    selectedProvider = providerMap[orchestrationResult.provider] || 'leonardo';
  } else {
    console.log(`🎯 Provider manuel: ${selectedProvider}`);
  }

  const fallbackOrder = {
    dalle3: ['dalle3', 'leonardo', 'replicate'],
    leonardo: ['leonardo', 'replicate', 'dalle3'],
    replicate: ['replicate', 'leonardo', 'dalle3']
  };

  const tryOrder = fallbackOrder[selectedProvider] || ['dalle3', 'leonardo', 'replicate'];

  for (const providerName of tryOrder) {
    try {
      console.log(`\n🔄 Tentative: ${providerName}`);
      
      let result;
      if (providerName === 'dalle3') {
        result = await generateWithDALLE3(enhancedPrompt, quality, size);
      } else if (providerName === 'leonardo') {
        result = await generateWithLeonardo(enhancedPrompt, quality);
      } else {
        result = await generateWithReplicate(enhancedPrompt, quality);
      }

      return {
        ...result,
        originalPrompt: prompt,
        enhancedPrompt: enhancedPrompt,
        requestedProvider: selectedProvider,
        timestamp: new Date().toISOString()
      };

    } catch (error: any) {
      console.error(`❌ ${providerName} echoue:`, error.message);
      if (providerName === tryOrder[tryOrder.length - 1]) {
        throw new Error('Tous les providers ont echoue');
      }
      console.log("🔄 Essai du provider suivant...");
    }
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const result = await generateImageIntelligent(body);

    return NextResponse.json({
      success: true,
      ...result,
      realAPI: true,
      intelligentSelection: true
    });

  } catch (error: any) {
    console.error("❌ Erreur generation image:", error);
    
    return NextResponse.json({
      success: false,
      error: error.message || "Erreur lors de la generation",
      realAPI: true
    }, { status: 500 });
  }
}

export async function GET() {
  return NextResponse.json({
    message: "API de generation d'images - OPTIMISATION INTELLIGENTE COUTS/QUALITE",
    status: "OPERATIONAL",
    
    parameters: {
      prompt: "string (required)",
      style: "realistic | artistic | cinematic | minimalist | 3d",
      quality: "draft | standard | premium | ultra (default: standard)",
      size: "1024x1024 | 1024x1792 | 1792x1024 (DALL-E 3)",
      provider: "auto | dalle3 | leonardo | replicate (default: auto)"
    },

    strategie_optimisation: {
      ULTRA_PREMIUM: {
        provider: "DALL-E 3",
        cout: "$0.08/image",
        usage: "Projets professionnels, qualite maximale"
      },
      STANDARD_OPTIMAL: {
        provider: "Leonardo AI",
        cout: "$0.015/image",
        usage: "Production standard, rapport qualite/prix"
      },
      DRAFT_ECONOMIQUE: {
        provider: "Replicate",
        cout: "$0.008/image",
        usage: "Tests, prototypes, volume eleve"
      }
    },

    providers_disponibles: {
      dalle3: {
        configured: !!OPENAI_API_KEY,
        models: ["dall-e-3"],
        resolutions: ["1024x1024", "1024x1792", "1792x1024"],
        cost: "$0.04-0.08"
      },
      leonardo: {
        configured: !!LEONARDO_API_KEY,
        models: ["Leonardo Kino XL"],
        cost: "$0.01-0.02"
      },
      replicate: {
        configured: !!REPLICATE_API_TOKEN,
        models: ["Flux 1.1 Pro"],
        cost: "$0.005-0.01"
      }
    },

    amelioration_prompts: {
      enabled: true,
      ai_powered: !!ANTHROPIC_API_KEY,
      traduction: !!DEEPL_API_KEY
    },

    exemples: [
      { prompt: "un chat noir", quality: "draft", provider_selectionne: "Replicate", cout: "$0.008" },
      { prompt: "portrait professionnel", quality: "standard", provider_selectionne: "Leonardo", cout: "$0.015" },
      { prompt: "image marketing premium", quality: "ultra", provider_selectionne: "DALL-E 3", cout: "$0.08" }
    ]
  });
}
