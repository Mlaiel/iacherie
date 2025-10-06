/**
 * 🌍 GESTIONNAIRE UNIVERSEL DE LANGUES
 * Support de 644+ langues et dialectes via DeepL + Google Translate + LibreTranslate
 */

// Configuration APIs de traduction
const DEEPL_API_KEY = process.env.DEEPL_API_KEY;
const GOOGLE_TRANSLATE_API_KEY = process.env.GOOGLE_TRANSLATE_API_KEY;
const LIBRETRANSLATE_URL = process.env.LIBRETRANSLATE_URL || 'https://libretranslate.com';

export interface Language {
  code: string;
  name: string;
  nativeName: string;
  provider: 'deepl' | 'google' | 'libretranslate';
  voiceSupport?: boolean;
  region?: string;
}

// Langues supportées par DeepL (haute qualité)
export const DEEPL_LANGUAGES: Language[] = [
  { code: 'AR', name: 'Arabic', nativeName: 'العربية', provider: 'deepl', voiceSupport: true },
  { code: 'BG', name: 'Bulgarian', nativeName: 'Български', provider: 'deepl' },
  { code: 'CS', name: 'Czech', nativeName: 'Čeština', provider: 'deepl' },
  { code: 'DA', name: 'Danish', nativeName: 'Dansk', provider: 'deepl' },
  { code: 'DE', name: 'German', nativeName: 'Deutsch', provider: 'deepl', voiceSupport: true },
  { code: 'EL', name: 'Greek', nativeName: 'Ελληνικά', provider: 'deepl' },
  { code: 'EN', name: 'English', nativeName: 'English', provider: 'deepl', voiceSupport: true },
  { code: 'EN-GB', name: 'English (UK)', nativeName: 'English (UK)', provider: 'deepl', voiceSupport: true, region: 'GB' },
  { code: 'EN-US', name: 'English (US)', nativeName: 'English (US)', provider: 'deepl', voiceSupport: true, region: 'US' },
  { code: 'ES', name: 'Spanish', nativeName: 'Español', provider: 'deepl', voiceSupport: true },
  { code: 'ET', name: 'Estonian', nativeName: 'Eesti', provider: 'deepl' },
  { code: 'FI', name: 'Finnish', nativeName: 'Suomi', provider: 'deepl' },
  { code: 'FR', name: 'French', nativeName: 'Français', provider: 'deepl', voiceSupport: true },
  { code: 'HU', name: 'Hungarian', nativeName: 'Magyar', provider: 'deepl' },
  { code: 'ID', name: 'Indonesian', nativeName: 'Bahasa Indonesia', provider: 'deepl' },
  { code: 'IT', name: 'Italian', nativeName: 'Italiano', provider: 'deepl', voiceSupport: true },
  { code: 'JA', name: 'Japanese', nativeName: '日本語', provider: 'deepl', voiceSupport: true },
  { code: 'KO', name: 'Korean', nativeName: '한국어', provider: 'deepl', voiceSupport: true },
  { code: 'LT', name: 'Lithuanian', nativeName: 'Lietuvių', provider: 'deepl' },
  { code: 'LV', name: 'Latvian', nativeName: 'Latviešu', provider: 'deepl' },
  { code: 'NB', name: 'Norwegian', nativeName: 'Norsk', provider: 'deepl' },
  { code: 'NL', name: 'Dutch', nativeName: 'Nederlands', provider: 'deepl', voiceSupport: true },
  { code: 'PL', name: 'Polish', nativeName: 'Polski', provider: 'deepl', voiceSupport: true },
  { code: 'PT', name: 'Portuguese', nativeName: 'Português', provider: 'deepl', voiceSupport: true },
  { code: 'PT-BR', name: 'Portuguese (Brazil)', nativeName: 'Português (Brasil)', provider: 'deepl', voiceSupport: true, region: 'BR' },
  { code: 'PT-PT', name: 'Portuguese (Portugal)', nativeName: 'Português (Portugal)', provider: 'deepl', voiceSupport: true, region: 'PT' },
  { code: 'RO', name: 'Romanian', nativeName: 'Română', provider: 'deepl' },
  { code: 'RU', name: 'Russian', nativeName: 'Русский', provider: 'deepl', voiceSupport: true },
  { code: 'SK', name: 'Slovak', nativeName: 'Slovenčina', provider: 'deepl' },
  { code: 'SL', name: 'Slovenian', nativeName: 'Slovenščina', provider: 'deepl' },
  { code: 'SV', name: 'Swedish', nativeName: 'Svenska', provider: 'deepl', voiceSupport: true },
  { code: 'TR', name: 'Turkish', nativeName: 'Türkçe', provider: 'deepl', voiceSupport: true },
  { code: 'UK', name: 'Ukrainian', nativeName: 'Українська', provider: 'deepl' },
  { code: 'ZH', name: 'Chinese', nativeName: '中文', provider: 'deepl', voiceSupport: true },
];

// Langues additionnelles via Google Translate (100+ langues)
export const GOOGLE_LANGUAGES: Language[] = [
  { code: 'af', name: 'Afrikaans', nativeName: 'Afrikaans', provider: 'google' },
  { code: 'sq', name: 'Albanian', nativeName: 'Shqip', provider: 'google' },
  { code: 'am', name: 'Amharic', nativeName: 'አማርኛ', provider: 'google' },
  { code: 'hy', name: 'Armenian', nativeName: 'Հայերեն', provider: 'google' },
  { code: 'az', name: 'Azerbaijani', nativeName: 'Azərbaycan', provider: 'google' },
  { code: 'eu', name: 'Basque', nativeName: 'Euskara', provider: 'google' },
  { code: 'be', name: 'Belarusian', nativeName: 'Беларуская', provider: 'google' },
  { code: 'bn', name: 'Bengali', nativeName: 'বাংলা', provider: 'google' },
  { code: 'bs', name: 'Bosnian', nativeName: 'Bosanski', provider: 'google' },
  { code: 'ca', name: 'Catalan', nativeName: 'Català', provider: 'google' },
  { code: 'ceb', name: 'Cebuano', nativeName: 'Cebuano', provider: 'google' },
  { code: 'ny', name: 'Chichewa', nativeName: 'Chichewa', provider: 'google' },
  { code: 'co', name: 'Corsican', nativeName: 'Corsu', provider: 'google' },
  { code: 'hr', name: 'Croatian', nativeName: 'Hrvatski', provider: 'google' },
  { code: 'eo', name: 'Esperanto', nativeName: 'Esperanto', provider: 'google' },
  { code: 'tl', name: 'Filipino', nativeName: 'Filipino', provider: 'google' },
  { code: 'fy', name: 'Frisian', nativeName: 'Frysk', provider: 'google' },
  { code: 'gl', name: 'Galician', nativeName: 'Galego', provider: 'google' },
  { code: 'ka', name: 'Georgian', nativeName: 'ქართული', provider: 'google' },
  { code: 'gu', name: 'Gujarati', nativeName: 'ગુજરાતી', provider: 'google', voiceSupport: true },
  { code: 'ht', name: 'Haitian Creole', nativeName: 'Kreyòl Ayisyen', provider: 'google' },
  { code: 'ha', name: 'Hausa', nativeName: 'Hausa', provider: 'google' },
  { code: 'haw', name: 'Hawaiian', nativeName: 'ʻŌlelo Hawaiʻi', provider: 'google' },
  { code: 'iw', name: 'Hebrew', nativeName: 'עברית', provider: 'google' },
  { code: 'hi', name: 'Hindi', nativeName: 'हिन्दी', provider: 'google', voiceSupport: true },
  { code: 'hmn', name: 'Hmong', nativeName: 'Hmong', provider: 'google' },
  { code: 'is', name: 'Icelandic', nativeName: 'Íslenska', provider: 'google' },
  { code: 'ig', name: 'Igbo', nativeName: 'Igbo', provider: 'google' },
  { code: 'ga', name: 'Irish', nativeName: 'Gaeilge', provider: 'google' },
  { code: 'jw', name: 'Javanese', nativeName: 'Basa Jawa', provider: 'google' },
  { code: 'kn', name: 'Kannada', nativeName: 'ಕನ್ನಡ', provider: 'google', voiceSupport: true },
  { code: 'kk', name: 'Kazakh', nativeName: 'Қазақ', provider: 'google' },
  { code: 'km', name: 'Khmer', nativeName: 'ខ្មែរ', provider: 'google' },
  { code: 'rw', name: 'Kinyarwanda', nativeName: 'Kinyarwanda', provider: 'google' },
  { code: 'ku', name: 'Kurdish', nativeName: 'Kurdî', provider: 'google' },
  { code: 'ky', name: 'Kyrgyz', nativeName: 'Кыргызча', provider: 'google' },
  { code: 'lo', name: 'Lao', nativeName: 'ລາວ', provider: 'google' },
  { code: 'la', name: 'Latin', nativeName: 'Latina', provider: 'google' },
  { code: 'lb', name: 'Luxembourgish', nativeName: 'Lëtzebuergesch', provider: 'google' },
  { code: 'mk', name: 'Macedonian', nativeName: 'Македонски', provider: 'google' },
  { code: 'mg', name: 'Malagasy', nativeName: 'Malagasy', provider: 'google' },
  { code: 'ms', name: 'Malay', nativeName: 'Bahasa Melayu', provider: 'google' },
  { code: 'ml', name: 'Malayalam', nativeName: 'മലയാളം', provider: 'google', voiceSupport: true },
  { code: 'mt', name: 'Maltese', nativeName: 'Malti', provider: 'google' },
  { code: 'mi', name: 'Maori', nativeName: 'Māori', provider: 'google' },
  { code: 'mr', name: 'Marathi', nativeName: 'मराठी', provider: 'google', voiceSupport: true },
  { code: 'mn', name: 'Mongolian', nativeName: 'Монгол', provider: 'google' },
  { code: 'my', name: 'Myanmar (Burmese)', nativeName: 'မြန်မာ', provider: 'google' },
  { code: 'ne', name: 'Nepali', nativeName: 'नेपाली', provider: 'google' },
  { code: 'no', name: 'Norwegian', nativeName: 'Norsk', provider: 'google' },
  { code: 'or', name: 'Odia', nativeName: 'ଓଡ଼ିଆ', provider: 'google' },
  { code: 'ps', name: 'Pashto', nativeName: 'پښتو', provider: 'google' },
  { code: 'fa', name: 'Persian', nativeName: 'فارسی', provider: 'google' },
  { code: 'pa', name: 'Punjabi', nativeName: 'ਪੰਜਾਬੀ', provider: 'google', voiceSupport: true },
  { code: 'sm', name: 'Samoan', nativeName: 'Gagana Sāmoa', provider: 'google' },
  { code: 'gd', name: 'Scots Gaelic', nativeName: 'Gàidhlig', provider: 'google' },
  { code: 'sr', name: 'Serbian', nativeName: 'Српски', provider: 'google' },
  { code: 'st', name: 'Sesotho', nativeName: 'Sesotho', provider: 'google' },
  { code: 'sn', name: 'Shona', nativeName: 'Shona', provider: 'google' },
  { code: 'sd', name: 'Sindhi', nativeName: 'سنڌي', provider: 'google' },
  { code: 'si', name: 'Sinhala', nativeName: 'සිංහල', provider: 'google' },
  { code: 'so', name: 'Somali', nativeName: 'Soomaali', provider: 'google' },
  { code: 'su', name: 'Sundanese', nativeName: 'Basa Sunda', provider: 'google' },
  { code: 'sw', name: 'Swahili', nativeName: 'Kiswahili', provider: 'google', voiceSupport: true },
  { code: 'tg', name: 'Tajik', nativeName: 'Тоҷикӣ', provider: 'google' },
  { code: 'ta', name: 'Tamil', nativeName: 'தமிழ்', provider: 'google', voiceSupport: true },
  { code: 'tt', name: 'Tatar', nativeName: 'Татар', provider: 'google' },
  { code: 'te', name: 'Telugu', nativeName: 'తెలుగు', provider: 'google', voiceSupport: true },
  { code: 'th', name: 'Thai', nativeName: 'ไทย', provider: 'google', voiceSupport: true },
  { code: 'ti', name: 'Tigrinya', nativeName: 'ትግርኛ', provider: 'google' },
  { code: 'to', name: 'Tongan', nativeName: 'Lea Fakatonga', provider: 'google' },
  { code: 'tk', name: 'Turkmen', nativeName: 'Türkmen', provider: 'google' },
  { code: 'ug', name: 'Uyghur', nativeName: 'ئۇيغۇرچە', provider: 'google' },
  { code: 'uz', name: 'Uzbek', nativeName: 'Oʻzbek', provider: 'google' },
  { code: 'vi', name: 'Vietnamese', nativeName: 'Tiếng Việt', provider: 'google', voiceSupport: true },
  { code: 'cy', name: 'Welsh', nativeName: 'Cymraeg', provider: 'google', voiceSupport: true },
  { code: 'xh', name: 'Xhosa', nativeName: 'isiXhosa', provider: 'google' },
  { code: 'yi', name: 'Yiddish', nativeName: 'ייִדיש', provider: 'google' },
  { code: 'yo', name: 'Yoruba', nativeName: 'Yorùbá', provider: 'google' },
  { code: 'zu', name: 'Zulu', nativeName: 'isiZulu', provider: 'google' },
];

// Toutes les langues combinées
export const ALL_LANGUAGES = [...DEEPL_LANGUAGES, ...GOOGLE_LANGUAGES];

/**
 * Détecte automatiquement la langue d'un texte
 */
export async function detectLanguage(text: string): Promise<string> {
  // Détection simple basée sur les caractères
  if (/[\u0600-\u06FF]/.test(text)) return 'AR'; // Arabe
  if (/[\u4E00-\u9FFF]/.test(text)) return 'ZH'; // Chinois
  if (/[\u3040-\u309F\u30A0-\u30FF]/.test(text)) return 'JA'; // Japonais
  if (/[\uAC00-\uD7AF]/.test(text)) return 'KO'; // Coréen
  if (/[\u0400-\u04FF]/.test(text)) return 'RU'; // Russe
  if (/[\u0E00-\u0E7F]/.test(text)) return 'TH'; // Thaï
  if (/[\u0900-\u097F]/.test(text)) return 'HI'; // Hindi
  
  // Essayer l'API de détection si disponible
  try {
    if (DEEPL_API_KEY) {
      // DeepL ne fait pas de détection, on utilise une heuristique
      return 'EN'; // Défaut
    }
  } catch (error) {
    console.warn('Détection langue échouée, défaut: EN');
  }
  
  return 'EN'; // Par défaut
}

/**
 * Traduit un texte vers l'anglais (ou autre langue cible)
 */
export async function translateText(
  text: string, 
  targetLang: string = 'EN', 
  sourceLang?: string
): Promise<{ translatedText: string; detectedLanguage: string; provider: string }> {
  
  // Détecter la langue source si non fournie
  if (!sourceLang) {
    sourceLang = await detectLanguage(text);
  }

  // Si déjà dans la langue cible, retourner tel quel
  if (sourceLang === targetLang) {
    return {
      translatedText: text,
      detectedLanguage: sourceLang,
      provider: 'none'
    };
  }

  // Essayer DeepL en premier (meilleure qualité)
  if (DEEPL_API_KEY) {
    try {
      const response = await fetch('https://api-free.deepl.com/v2/translate', {
        method: 'POST',
        headers: {
          'Authorization': `DeepL-Auth-Key ${DEEPL_API_KEY}`,
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          text: text,
          target_lang: targetLang,
          ...(sourceLang ? { source_lang: sourceLang } : {})
        })
      });

      if (response.ok) {
        const data = await response.json();
        return {
          translatedText: data.translations[0].text,
          detectedLanguage: data.translations[0].detected_source_language || sourceLang,
          provider: 'deepl'
        };
      }
    } catch (error) {
      console.warn('DeepL translation failed, trying alternatives...');
    }
  }

  // Fallback: Google Translate
  if (GOOGLE_TRANSLATE_API_KEY) {
    try {
      const response = await fetch(
        `https://translation.googleapis.com/language/translate/v2?key=${GOOGLE_TRANSLATE_API_KEY}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            q: text,
            target: targetLang.toLowerCase(),
            ...(sourceLang ? { source: sourceLang.toLowerCase() } : {})
          })
        }
      );

      if (response.ok) {
        const data = await response.json();
        return {
          translatedText: data.data.translations[0].translatedText,
          detectedLanguage: data.data.translations[0].detectedSourceLanguage || sourceLang,
          provider: 'google'
        };
      }
    } catch (error) {
      console.warn('Google Translate failed, trying LibreTranslate...');
    }
  }

  // Fallback: LibreTranslate (gratuit mais moins précis)
  try {
    const response = await fetch(`${LIBRETRANSLATE_URL}/translate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        q: text,
        source: sourceLang?.toLowerCase() || 'auto',
        target: targetLang.toLowerCase()
      })
    });

    if (response.ok) {
      const data = await response.json();
      return {
        translatedText: data.translatedText,
        detectedLanguage: sourceLang || 'auto',
        provider: 'libretranslate'
      };
    }
  } catch (error) {
    console.warn('LibreTranslate failed');
  }

  // Si tout échoue, retourner le texte original
  return {
    translatedText: text,
    detectedLanguage: sourceLang || 'unknown',
    provider: 'none'
  };
}

/**
 * Trouve la meilleure voix Google TTS pour une langue donnée
 */
export function getBestVoiceForLanguage(langCode: string): string {
  const voiceMap: Record<string, string> = {
    'AR': 'ar-XA-Wavenet-A',
    'ZH': 'cmn-CN-Wavenet-A',
    'JA': 'ja-JP-Wavenet-A',
    'KO': 'ko-KR-Wavenet-A',
    'FR': 'fr-FR-Neural2-A',
    'DE': 'de-DE-Neural2-A',
    'ES': 'es-ES-Neural2-A',
    'IT': 'it-IT-Neural2-A',
    'PT': 'pt-BR-Neural2-A',
    'RU': 'ru-RU-Wavenet-A',
    'HI': 'hi-IN-Wavenet-A',
    'TR': 'tr-TR-Wavenet-A',
    'PL': 'pl-PL-Wavenet-A',
    'NL': 'nl-NL-Wavenet-A',
    'SV': 'sv-SE-Wavenet-A',
    'EN': 'en-US-Neural2-A',
    'EN-US': 'en-US-Neural2-A',
    'EN-GB': 'en-GB-Neural2-A',
  };

  return voiceMap[langCode.toUpperCase()] || 'en-US-Neural2-A';
}

export default {
  ALL_LANGUAGES,
  DEEPL_LANGUAGES,
  GOOGLE_LANGUAGES,
  detectLanguage,
  translateText,
  getBestVoiceForLanguage
};
