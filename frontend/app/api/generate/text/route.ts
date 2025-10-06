import { NextRequest, NextResponse } from 'next/server';
import { orchestrate } from '@/lib/api-orchestrator';
import { detectLanguage, translateText, ALL_LANGUAGES } from '@/lib/language-manager';

// Configuration APIs RÉELLES - AUCUN FALLBACK
const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
const GOOGLE_GEMINI_API_KEY = process.env.GOOGLE_GEMINI_API_KEY;
const COHERE_API_KEY = process.env.COHERE_API_KEY;
const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY;
const DEEPL_API_KEY = process.env.DEEPL_API_KEY;

console.log("🔑 VÉRIFICATION CLÉS API RÉELLES:");
console.log("OpenAI:", OPENAI_API_KEY ? `✅ ${OPENAI_API_KEY.substring(0, 20)}...` : "❌ Manquante");
console.log("Gemini:", GOOGLE_GEMINI_API_KEY ? `✅ ${GOOGLE_GEMINI_API_KEY.substring(0, 20)}...` : "❌ Manquante");
console.log("Cohere:", COHERE_API_KEY ? `✅ ${COHERE_API_KEY.substring(0, 20)}...` : "❌ Manquante");
console.log("Claude:", ANTHROPIC_API_KEY ? `✅ ${ANTHROPIC_API_KEY.substring(0, 20)}...` : "❌ Manquante");

// MODÈLES DISPONIBLES
const OPENAI_AVAILABLE_MODELS = [
  "gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo", 
  "gpt-4", "o1-mini", "o1", "chatgpt-4o-latest", "gpt-4.1"
];

const CLAUDE_AVAILABLE_MODELS = [
  "claude-sonnet-4.5-20241022", "claude-3-5-sonnet-20241022",
  "claude-3-opus-20240229", "claude-3-sonnet-20240229"
];

// GÉNÉRATION OPENAI RÉELLE
async function generateWithOpenAI(prompt: string, model: string = "gpt-4o-mini") {
  if (!OPENAI_API_KEY) {
    throw new Error('❌ OpenAI API key RÉELLE non configurée');
  }

  console.log("🧠 GÉNÉRATION OPENAI RÉELLE - Modèle:", model);
  
  try {
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${OPENAI_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: model,
        messages: [{ role: "user", content: prompt }],
        max_tokens: 1000,
        temperature: 0.7
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`OpenAI error: ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    return {
      success: true,
      text: data.choices[0].message.content,
      provider: 'openai',
      model: model,
      usage: data.usage
    };
  } catch (error) {
    console.error("❌ Erreur OpenAI:", error);
    throw error;
  }
}

// GÉNÉRATION CLAUDE RÉELLE
async function generateWithClaude(prompt: string, model: string = "claude-sonnet-4-20250514") {
  if (!ANTHROPIC_API_KEY) {
    throw new Error('❌ Anthropic API key RÉELLE non configurée');
  }

  console.log("🤖 GÉNÉRATION CLAUDE RÉELLE - Modèle:", model);
  
  try {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'x-api-key': ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: model,
        max_tokens: 1000,
        messages: [{ role: "user", content: prompt }]
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Claude error: ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    return {
      success: true,
      text: data.content[0].text,
      provider: 'claude',
      model: model,
      usage: data.usage
    };
  } catch (error) {
    console.error("❌ Erreur Claude:", error);
    throw error;
  }
}

// GÉNÉRATION GEMINI RÉELLE
async function generateWithGemini(prompt: string) {
  if (!GOOGLE_GEMINI_API_KEY) {
    throw new Error('❌ Google Gemini API key RÉELLE non configurée');
  }

  console.log("💎 GÉNÉRATION GEMINI RÉELLE");
  
  try {
    const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${GOOGLE_GEMINI_API_KEY}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{ parts: [{ text: prompt }] }],
        generationConfig: {
          temperature: 0.7,
          topK: 40,
          topP: 0.95,
          maxOutputTokens: 1000,
        }
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Gemini error: ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    return {
      success: true,
      text: data.candidates[0].content.parts[0].text,
      provider: 'gemini',
      model: 'gemini-1.5-flash'
    };
  } catch (error) {
    console.error("❌ Erreur Gemini:", error);
    throw error;
  }
}

// GÉNÉRATION COHERE RÉELLE
async function generateWithCohere(prompt: string) {
  if (!COHERE_API_KEY) {
    throw new Error('❌ Cohere API key RÉELLE non configurée');
  }

  console.log("🔥 GÉNÉRATION COHERE RÉELLE");
  
  try {
    const response = await fetch('https://api.cohere.com/v2/chat', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${COHERE_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'command-a-03-2025',
        messages: [{ role: 'user', content: prompt }],
        max_tokens: 1000,
        temperature: 0.7
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Cohere error: ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    return {
      success: true,
      text: data.message.content[0].text,
      provider: 'cohere',
      model: 'command-a-03-2025'
    };
  } catch (error) {
    console.error("❌ Erreur Cohere:", error);
    throw error;
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { 
      prompt, 
      type = 'article',
      length = 'medium', 
      tone = 'professional',
      language = 'en',
      provider = 'auto',
      model = 'auto'
    } = body;

    if (!prompt) {
      return NextResponse.json(
        { success: false, error: 'Prompt requis' },
        { status: 400 }
      );
    }

    console.log(`� Génération de texte - Type: ${type}, Provider: ${provider}, Model: ${model}`);

    // ========================================
    // SÉLECTION INTELLIGENTE DU PROVIDER
    // ========================================
    let selectedProvider = provider;
    let selectedModel = model;

    // ========================================
    // 🎼 ORCHESTRATION INTELLIGENTE
    // ========================================
    if (provider === 'auto') {
      console.log('🎼 MAESTRO: Sélection intelligente du meilleur provider...');
      
      // Mapper le type au useCase de l'orchestrateur
      const useCaseMap: Record<string, string> = {
        'chat': 'chat',
        'article': 'article',
        'marketing': 'marketing',
        'technical': 'technical',
        'creative': 'creative'
      };

      // Mapper la longueur à la qualité
      const qualityMap: Record<string, 'draft' | 'standard' | 'premium' | 'ultra'> = {
        'short': 'draft',
        'medium': 'standard',
        'long': 'premium'
      };

      const orchestrationResult = orchestrate({
        contentType: 'text',
        quality: qualityMap[length] || 'standard',
        useCase: useCaseMap[type] || 'article',
        budget: 0.5 // Budget par défaut
      });

      console.log(`✅ MAESTRO: ${orchestrationResult.provider} sélectionné (${orchestrationResult.reasoning})`);
      console.log(`💰 Économie estimée: $${orchestrationResult.estimatedSavings?.toFixed(3) || 0}`);

      // Mapper le provider de l'orchestrateur aux providers de l'API
      const providerMap: Record<string, string> = {
        'gemini-2.5-flash': 'gemini',
        'gpt-4o-mini': 'openai',
        'gpt-4o': 'openai',
        'claude-sonnet-4': 'claude',
        'cohere-command-a': 'cohere'
      };

      selectedProvider = providerMap[orchestrationResult.provider] || 'openai';
      
      // Ajuster le modèle selon le provider orchestré
      if (orchestrationResult.provider === 'gpt-4o-mini') {
        selectedModel = 'gpt-4o-mini';
      } else if (orchestrationResult.provider === 'gpt-4o') {
        selectedModel = 'gpt-4o';
      } else if (orchestrationResult.provider === 'gemini-2.5-flash') {
        selectedModel = 'gemini-2.5-flash';
      }
    } else {
      console.log(`🎯 Provider manuel: ${selectedProvider}`);
    }

    // Si model auto avec OpenAI spécifique
    if (selectedProvider === 'openai' && selectedModel === 'auto') {
      if (type === 'marketing') {
        selectedModel = 'gpt-4o';
      } else if (type === 'chat' || length === 'short') {
        selectedModel = 'gpt-3.5-turbo';
      } else {
        selectedModel = 'gpt-4o-mini';
      }
    }

    // ========================================
    // GÉNÉRATION SELON LE PROVIDER
    // ========================================
    let result;

    try {
      switch (selectedProvider) {
        case 'openai':
          result = await generateWithOpenAI(prompt, selectedModel);
          break;
        case 'claude':
          result = await generateWithClaude(prompt);
          break;
        case 'gemini':
          // ✅ Réactivé avec gemini-2.5-flash
          result = await generateWithGemini(prompt);
          break;
        case 'cohere':
          // ✅ Réactivé avec command-a-03-2025
          result = await generateWithCohere(prompt);
          break;
        default:
          // Fallback à GPT-4o-mini si provider inconnu
          result = await generateWithOpenAI(prompt, 'gpt-4o-mini');
      }

      return NextResponse.json({
        success: true,
        ...result,
        autoSelected: provider === 'auto',
        requestedProvider: provider,
        requestedModel: model
      });

    } catch (error) {
      console.error(`❌ Erreur génération texte avec ${selectedProvider}:`, error);
      
      // Pas de fallback - retourner l'erreur
      return NextResponse.json(
        { 
          success: false, 
          error: `Échec génération avec ${selectedProvider}: ${error}`,
          provider: selectedProvider
        },
        { status: 500 }
      );
    }

  } catch (error) {
    console.error("❌ Erreur générale:", error);
    return NextResponse.json(
      { success: false, error: `Erreur: ${error}` },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json({
    message: "API de génération de texte - APIS RÉELLES SEULEMENT",
    status: "AUCUN FALLBACK - AUCUNE SIMULATION",
    endpoints: { POST: "/api/generate/text" },
    parameters: {
      prompt: "string (required)",
      provider: "string (optional) - 'auto', 'openai', 'claude', 'gemini', 'cohere'",
      model: "string (optional)"
    },
    realAPIStatus: {
      openai: {
        configured: !!OPENAI_API_KEY,
        models: OPENAI_AVAILABLE_MODELS
      },
      claude: {
        configured: !!ANTHROPIC_API_KEY,
        models: CLAUDE_AVAILABLE_MODELS
      },
      gemini: {
        configured: !!GOOGLE_GEMINI_API_KEY,
        models: ["gemini-1.5-flash-latest", "gemini-pro"]
      },
      cohere: {
        configured: !!COHERE_API_KEY,
        models: ["command"]
      }
    },
    warning: "AUCUNE SIMULATION - APIs réelles uniquement"
  });
}
