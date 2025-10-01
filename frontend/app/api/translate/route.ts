import { NextRequest, NextResponse } from 'next/server';

// Configuration DeepL
const DEEPL_API_KEY = process.env.DEEPL_API_KEY;
const DEEPL_BASE_URL = 'https://api-free.deepl.com/v2';

// Langues supportées par DeepL
const SUPPORTED_LANGUAGES = {
  'auto': 'Auto-detect',
  'ar': 'Arabic',
  'bg': 'Bulgarian',
  'cs': 'Czech',
  'da': 'Danish',
  'de': 'German',
  'el': 'Greek',
  'en': 'English',
  'es': 'Spanish',
  'et': 'Estonian',
  'fi': 'Finnish',
  'fr': 'French',
  'hu': 'Hungarian',
  'id': 'Indonesian',
  'it': 'Italian',
  'ja': 'Japanese',
  'ko': 'Korean',
  'lt': 'Lithuanian',
  'lv': 'Latvian',
  'nb': 'Norwegian',
  'nl': 'Dutch',
  'pl': 'Polish',
  'pt': 'Portuguese',
  'ro': 'Romanian',
  'ru': 'Russian',
  'sk': 'Slovak',
  'sl': 'Slovenian',
  'sv': 'Swedish',
  'tr': 'Turkish',
  'uk': 'Ukrainian',
  'zh': 'Chinese'
};

export async function POST(request: NextRequest) {
  try {
    console.log("🌐 DEEPL TRADUCTION PREMIUM - QUALITÉ PROFESSIONNELLE");
    
    if (!DEEPL_API_KEY) {
      return NextResponse.json({
        success: false,
        error: "DeepL API key not configured"
      }, { status: 500 });
    }

    const body = await request.json();
    const { text, targetLang, sourceLang = 'auto' } = body;

    if (!text || !targetLang) {
      return NextResponse.json({
        success: false,
        error: "Text et targetLang requis"
      }, { status: 400 });
    }

    console.log("📝 Texte à traduire:", text.substring(0, 100) + "...");
    console.log("🎯 Langue cible:", targetLang);
    console.log("🔍 Langue source:", sourceLang);

    // Traduction avec DeepL
    const response = await fetch(`${DEEPL_BASE_URL}/translate`, {
      method: 'POST',
      headers: {
        'Authorization': `DeepL-Auth-Key ${DEEPL_API_KEY}`,
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        text: text,
        target_lang: targetLang.toUpperCase(),
        source_lang: sourceLang === 'auto' ? '' : sourceLang.toUpperCase(),
        preserve_formatting: '1',
        formality: 'default'
      })
    });

    console.log("🔍 DeepL Response Status:", response.status);

    if (!response.ok) {
      const errorText = await response.text();
      console.error("❌ DeepL API Error:", response.status, errorText);
      return NextResponse.json({
        success: false,
        error: `DeepL API error: ${response.status}`
      }, { status: response.status });
    }

    const data = await response.json();
    
    if (data.translations && data.translations.length > 0) {
      const translation = data.translations[0];
      
      console.log("✅ SUCCÈS - DeepL Premium Translation");
      return NextResponse.json({
        success: true,
        provider: "DeepL Premium",
        quality: "professional",
        originalText: text,
        translatedText: translation.text,
        detectedSourceLang: translation.detected_source_language || sourceLang,
        targetLang: targetLang,
        wordCount: text.split(' ').length,
        realTranslation: true
      });
    }

    return NextResponse.json({
      success: false,
      error: "Aucune traduction reçue de DeepL"
    }, { status: 500 });

  } catch (error) {
    console.error('❌ Erreur DeepL:', error);
    return NextResponse.json({
      success: false,
      error: "Erreur interne du serveur"
    }, { status: 500 });
  }
}

// GET pour récupérer les langues supportées
export async function GET(request: NextRequest) {
  try {
    console.log("📋 Récupération des langues supportées DeepL");
    
    if (!DEEPL_API_KEY) {
      return NextResponse.json({
        success: false,
        error: "DeepL API key not configured"
      }, { status: 500 });
    }

    // Récupérer les langues depuis l'API DeepL
    const response = await fetch(`${DEEPL_BASE_URL}/languages?type=target`, {
      headers: {
        'Authorization': `DeepL-Auth-Key ${DEEPL_API_KEY}`,
      }
    });

    if (response.ok) {
      const languages = await response.json();
      console.log("✅ Langues récupérées depuis DeepL API");
      
      return NextResponse.json({
        success: true,
        provider: "DeepL API",
        languages: languages,
        supported: SUPPORTED_LANGUAGES
      });
    }

    // Fallback avec langues statiques
    return NextResponse.json({
      success: true,
      provider: "DeepL Static",
      supported: SUPPORTED_LANGUAGES
    });

  } catch (error) {
    console.error('❌ Erreur récupération langues:', error);
    return NextResponse.json({
      success: true,
      provider: "DeepL Static",
      supported: SUPPORTED_LANGUAGES
    });
  }
}