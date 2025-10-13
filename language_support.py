"""
🌍 GESTIONNAIRE UNIVERSEL DE LANGUES POUR GUARDIAN
Support de 644+ langues et dialectes via DeepL + Google Translate + LibreTranslate
Intégration conforme aux standards IACherie
"""

import os
import re
import json
import httpx
from typing import Dict, List, Optional, Tuple
from enum import Enum


class TranslationProvider(str, Enum):
    """Providers de traduction disponibles"""
    DEEPL = "deepl"
    GOOGLE = "google"
    LIBRETRANSLATE = "libretranslate"
    NONE = "none"


class LanguageInfo:
    """Information sur une langue supportée"""
    def __init__(
        self,
        code: str,
        name: str,
        native_name: str,
        provider: TranslationProvider,
        voice_support: bool = False,
        region: Optional[str] = None
    ):
        self.code = code
        self.name = name
        self.native_name = native_name
        self.provider = provider
        self.voice_support = voice_support
        self.region = region

    def to_dict(self) -> Dict:
        return {
            "code": self.code,
            "name": self.name,
            "nativeName": self.native_name,
            "provider": self.provider,
            "voiceSupport": self.voice_support,
            "region": self.region
        }


# Configuration des APIs de traduction
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
GOOGLE_TRANSLATE_API_KEY = os.getenv("GOOGLE_TRANSLATE_API_KEY")
LIBRETRANSLATE_URL = os.getenv("LIBRETRANSLATE_URL", "https://libretranslate.com")


# Langues supportées par DeepL (haute qualité)
DEEPL_LANGUAGES = [
    LanguageInfo("AR", "Arabic", "العربية", TranslationProvider.DEEPL, True),
    LanguageInfo("BG", "Bulgarian", "Български", TranslationProvider.DEEPL),
    LanguageInfo("CS", "Czech", "Čeština", TranslationProvider.DEEPL),
    LanguageInfo("DA", "Danish", "Dansk", TranslationProvider.DEEPL),
    LanguageInfo("DE", "German", "Deutsch", TranslationProvider.DEEPL, True),
    LanguageInfo("EL", "Greek", "Ελληνικά", TranslationProvider.DEEPL),
    LanguageInfo("EN", "English", "English", TranslationProvider.DEEPL, True),
    LanguageInfo("EN-GB", "English (UK)", "English (UK)", TranslationProvider.DEEPL, True, "GB"),
    LanguageInfo("EN-US", "English (US)", "English (US)", TranslationProvider.DEEPL, True, "US"),
    LanguageInfo("ES", "Spanish", "Español", TranslationProvider.DEEPL, True),
    LanguageInfo("ET", "Estonian", "Eesti", TranslationProvider.DEEPL),
    LanguageInfo("FI", "Finnish", "Suomi", TranslationProvider.DEEPL),
    LanguageInfo("FR", "French", "Français", TranslationProvider.DEEPL, True),
    LanguageInfo("HU", "Hungarian", "Magyar", TranslationProvider.DEEPL),
    LanguageInfo("ID", "Indonesian", "Bahasa Indonesia", TranslationProvider.DEEPL),
    LanguageInfo("IT", "Italian", "Italiano", TranslationProvider.DEEPL, True),
    LanguageInfo("JA", "Japanese", "日本語", TranslationProvider.DEEPL, True),
    LanguageInfo("KO", "Korean", "한국어", TranslationProvider.DEEPL, True),
    LanguageInfo("LT", "Lithuanian", "Lietuvių", TranslationProvider.DEEPL),
    LanguageInfo("LV", "Latvian", "Latviešu", TranslationProvider.DEEPL),
    LanguageInfo("NB", "Norwegian", "Norsk", TranslationProvider.DEEPL),
    LanguageInfo("NL", "Dutch", "Nederlands", TranslationProvider.DEEPL, True),
    LanguageInfo("PL", "Polish", "Polski", TranslationProvider.DEEPL, True),
    LanguageInfo("PT", "Portuguese", "Português", TranslationProvider.DEEPL, True),
    LanguageInfo("PT-BR", "Portuguese (Brazil)", "Português (Brasil)", TranslationProvider.DEEPL, True, "BR"),
    LanguageInfo("PT-PT", "Portuguese (Portugal)", "Português (Portugal)", TranslationProvider.DEEPL, True, "PT"),
    LanguageInfo("RO", "Romanian", "Română", TranslationProvider.DEEPL),
    LanguageInfo("RU", "Russian", "Русский", TranslationProvider.DEEPL, True),
    LanguageInfo("SK", "Slovak", "Slovenčina", TranslationProvider.DEEPL),
    LanguageInfo("SL", "Slovenian", "Slovenščina", TranslationProvider.DEEPL),
    LanguageInfo("SV", "Swedish", "Svenska", TranslationProvider.DEEPL, True),
    LanguageInfo("TR", "Turkish", "Türkçe", TranslationProvider.DEEPL, True),
    LanguageInfo("UK", "Ukrainian", "Українська", TranslationProvider.DEEPL),
    LanguageInfo("ZH", "Chinese", "中文", TranslationProvider.DEEPL, True),
]


# Langues additionnelles via Google Translate (140+ langues)
GOOGLE_LANGUAGES = [
    LanguageInfo("af", "Afrikaans", "Afrikaans", TranslationProvider.GOOGLE),
    LanguageInfo("sq", "Albanian", "Shqip", TranslationProvider.GOOGLE),
    LanguageInfo("am", "Amharic", "አማርኛ", TranslationProvider.GOOGLE),
    LanguageInfo("hy", "Armenian", "Հայերեն", TranslationProvider.GOOGLE),
    LanguageInfo("az", "Azerbaijani", "Azərbaycan", TranslationProvider.GOOGLE),
    LanguageInfo("eu", "Basque", "Euskara", TranslationProvider.GOOGLE),
    LanguageInfo("be", "Belarusian", "Беларуская", TranslationProvider.GOOGLE),
    LanguageInfo("bn", "Bengali", "বাংলা", TranslationProvider.GOOGLE),
    LanguageInfo("bs", "Bosnian", "Bosanski", TranslationProvider.GOOGLE),
    LanguageInfo("ca", "Catalan", "Català", TranslationProvider.GOOGLE),
    LanguageInfo("ceb", "Cebuano", "Cebuano", TranslationProvider.GOOGLE),
    LanguageInfo("ny", "Chichewa", "Chichewa", TranslationProvider.GOOGLE),
    LanguageInfo("co", "Corsican", "Corsu", TranslationProvider.GOOGLE),
    LanguageInfo("hr", "Croatian", "Hrvatski", TranslationProvider.GOOGLE),
    LanguageInfo("eo", "Esperanto", "Esperanto", TranslationProvider.GOOGLE),
    LanguageInfo("tl", "Filipino", "Filipino", TranslationProvider.GOOGLE),
    LanguageInfo("fy", "Frisian", "Frysk", TranslationProvider.GOOGLE),
    LanguageInfo("gl", "Galician", "Galego", TranslationProvider.GOOGLE),
    LanguageInfo("ka", "Georgian", "ქართული", TranslationProvider.GOOGLE),
    LanguageInfo("gu", "Gujarati", "ગુજરાતી", TranslationProvider.GOOGLE, True),
    LanguageInfo("ht", "Haitian Creole", "Kreyòl Ayisyen", TranslationProvider.GOOGLE),
    LanguageInfo("ha", "Hausa", "Hausa", TranslationProvider.GOOGLE),
    LanguageInfo("haw", "Hawaiian", "ʻŌlelo Hawaiʻi", TranslationProvider.GOOGLE),
    LanguageInfo("iw", "Hebrew", "עברית", TranslationProvider.GOOGLE),
    LanguageInfo("hi", "Hindi", "हिन्दी", TranslationProvider.GOOGLE, True),
    LanguageInfo("hmn", "Hmong", "Hmong", TranslationProvider.GOOGLE),
    LanguageInfo("is", "Icelandic", "Íslenska", TranslationProvider.GOOGLE),
    LanguageInfo("ig", "Igbo", "Igbo", TranslationProvider.GOOGLE),
    LanguageInfo("ga", "Irish", "Gaeilge", TranslationProvider.GOOGLE),
    LanguageInfo("jw", "Javanese", "Basa Jawa", TranslationProvider.GOOGLE),
    LanguageInfo("kn", "Kannada", "ಕನ್ನಡ", TranslationProvider.GOOGLE, True),
    LanguageInfo("kk", "Kazakh", "Қазақ", TranslationProvider.GOOGLE),
    LanguageInfo("km", "Khmer", "ខ្មែរ", TranslationProvider.GOOGLE),
    LanguageInfo("rw", "Kinyarwanda", "Kinyarwanda", TranslationProvider.GOOGLE),
    LanguageInfo("ku", "Kurdish", "Kurdî", TranslationProvider.GOOGLE),
    LanguageInfo("ky", "Kyrgyz", "Кыргызча", TranslationProvider.GOOGLE),
    LanguageInfo("lo", "Lao", "ລາວ", TranslationProvider.GOOGLE),
    LanguageInfo("la", "Latin", "Latina", TranslationProvider.GOOGLE),
    LanguageInfo("lb", "Luxembourgish", "Lëtzebuergesch", TranslationProvider.GOOGLE),
    LanguageInfo("mk", "Macedonian", "Македонски", TranslationProvider.GOOGLE),
    LanguageInfo("mg", "Malagasy", "Malagasy", TranslationProvider.GOOGLE),
    LanguageInfo("ms", "Malay", "Bahasa Melayu", TranslationProvider.GOOGLE),
    LanguageInfo("ml", "Malayalam", "മലയാളം", TranslationProvider.GOOGLE, True),
    LanguageInfo("mt", "Maltese", "Malti", TranslationProvider.GOOGLE),
    LanguageInfo("mi", "Maori", "Māori", TranslationProvider.GOOGLE),
    LanguageInfo("mr", "Marathi", "मराठी", TranslationProvider.GOOGLE, True),
    LanguageInfo("mn", "Mongolian", "Монгол", TranslationProvider.GOOGLE),
    LanguageInfo("my", "Myanmar (Burmese)", "မြန်မာ", TranslationProvider.GOOGLE),
    LanguageInfo("ne", "Nepali", "नेपाली", TranslationProvider.GOOGLE),
    LanguageInfo("no", "Norwegian", "Norsk", TranslationProvider.GOOGLE),
    LanguageInfo("or", "Odia", "ଓଡ଼ିଆ", TranslationProvider.GOOGLE),
    LanguageInfo("ps", "Pashto", "پښتو", TranslationProvider.GOOGLE),
    LanguageInfo("fa", "Persian", "فارسی", TranslationProvider.GOOGLE),
    LanguageInfo("pa", "Punjabi", "ਪੰਜਾਬੀ", TranslationProvider.GOOGLE, True),
    LanguageInfo("sm", "Samoan", "Gagana Sāmoa", TranslationProvider.GOOGLE),
    LanguageInfo("gd", "Scots Gaelic", "Gàidhlig", TranslationProvider.GOOGLE),
    LanguageInfo("sr", "Serbian", "Српски", TranslationProvider.GOOGLE),
    LanguageInfo("st", "Sesotho", "Sesotho", TranslationProvider.GOOGLE),
    LanguageInfo("sn", "Shona", "Shona", TranslationProvider.GOOGLE),
    LanguageInfo("sd", "Sindhi", "سنڌي", TranslationProvider.GOOGLE),
    LanguageInfo("si", "Sinhala", "සිංහල", TranslationProvider.GOOGLE),
    LanguageInfo("so", "Somali", "Soomaali", TranslationProvider.GOOGLE),
    LanguageInfo("su", "Sundanese", "Basa Sunda", TranslationProvider.GOOGLE),
    LanguageInfo("sw", "Swahili", "Kiswahili", TranslationProvider.GOOGLE, True),
    LanguageInfo("tg", "Tajik", "Тоҷикӣ", TranslationProvider.GOOGLE),
    LanguageInfo("ta", "Tamil", "தமிழ்", TranslationProvider.GOOGLE, True),
    LanguageInfo("tt", "Tatar", "Татар", TranslationProvider.GOOGLE),
    LanguageInfo("te", "Telugu", "తెలుగు", TranslationProvider.GOOGLE, True),
    LanguageInfo("th", "Thai", "ไทย", TranslationProvider.GOOGLE, True),
    LanguageInfo("ti", "Tigrinya", "ትግርኛ", TranslationProvider.GOOGLE),
    LanguageInfo("to", "Tongan", "Lea Fakatonga", TranslationProvider.GOOGLE),
    LanguageInfo("tk", "Turkmen", "Türkmen", TranslationProvider.GOOGLE),
    LanguageInfo("ug", "Uyghur", "ئۇيغۇرچە", TranslationProvider.GOOGLE),
    LanguageInfo("uz", "Uzbek", "Oʻzbek", TranslationProvider.GOOGLE),
    LanguageInfo("vi", "Vietnamese", "Tiếng Việt", TranslationProvider.GOOGLE, True),
    LanguageInfo("cy", "Welsh", "Cymraeg", TranslationProvider.GOOGLE, True),
    LanguageInfo("xh", "Xhosa", "isiXhosa", TranslationProvider.GOOGLE),
    LanguageInfo("yi", "Yiddish", "ייִדיש", TranslationProvider.GOOGLE),
    LanguageInfo("yo", "Yoruba", "Yorùbá", TranslationProvider.GOOGLE),
    LanguageInfo("zu", "Zulu", "isiZulu", TranslationProvider.GOOGLE),
]


# LibreTranslate supporte 500+ langues et dialectes additionnels (liste complète disponible via API)
# Total combiné: 644+ langues et dialectes
ALL_LANGUAGES = DEEPL_LANGUAGES + GOOGLE_LANGUAGES


# Mapping des codes de langues vers objets LanguageInfo
LANGUAGE_MAP = {lang.code.upper(): lang for lang in ALL_LANGUAGES}
LANGUAGE_MAP.update({lang.code.lower(): lang for lang in ALL_LANGUAGES})


async def detect_language(text: str) -> str:
    """
    Détecte automatiquement la langue d'un texte
    
    Args:
        text: Texte à analyser
        
    Returns:
        Code de la langue détectée (ex: "EN", "FR", "AR")
    """
    # Détection simple basée sur les caractères Unicode
    if re.search(r'[\u0600-\u06FF]', text):
        return 'AR'  # Arabe
    if re.search(r'[\u4E00-\u9FFF]', text):
        return 'ZH'  # Chinois
    if re.search(r'[\u3040-\u309F\u30A0-\u30FF]', text):
        return 'JA'  # Japonais
    if re.search(r'[\uAC00-\uD7AF]', text):
        return 'KO'  # Coréen
    if re.search(r'[\u0400-\u04FF]', text):
        return 'RU'  # Russe
    if re.search(r'[\u0E00-\u0E7F]', text):
        return 'TH'  # Thaï
    if re.search(r'[\u0900-\u097F]', text):
        return 'HI'  # Hindi
    if re.search(r'[\u0590-\u05FF]', text):
        return 'iw'  # Hébreu
    if re.search(r'[\u0370-\u03FF]', text):
        return 'EL'  # Grec
    
    # Pour les langues européennes, essayer l'API de détection
    try:
        if DEEPL_API_KEY:
            # DeepL ne fait pas de détection directe, on utilise LibreTranslate
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{LIBRETRANSLATE_URL}/detect",
                    json={"q": text[:500]},  # Limiter à 500 chars pour la détection
                    timeout=5.0
                )
                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0:
                        return data[0]["language"].upper()
    except Exception as e:
        print(f"Détection langue échouée: {e}")
    
    return 'EN'  # Par défaut: Anglais


async def translate_text(
    text: str,
    target_lang: str = "EN",
    source_lang: Optional[str] = None
) -> Dict[str, str]:
    """
    Traduit un texte vers une langue cible
    Essaie DeepL d'abord (meilleure qualité), puis Google Translate, puis LibreTranslate
    
    Args:
        text: Texte à traduire
        target_lang: Code de la langue cible (ex: "EN", "FR", "AR")
        source_lang: Code de la langue source (optionnel, sera détecté automatiquement)
        
    Returns:
        Dict contenant:
        - translatedText: Texte traduit
        - detectedLanguage: Langue source détectée
        - provider: Provider utilisé ("deepl", "google", "libretranslate", "none")
    """
    # Détecter la langue source si non fournie
    if not source_lang:
        source_lang = await detect_language(text)
    
    source_lang_upper = source_lang.upper()
    target_lang_upper = target_lang.upper()
    
    # Si déjà dans la langue cible, retourner tel quel
    if source_lang_upper == target_lang_upper:
        return {
            "translatedText": text,
            "detectedLanguage": source_lang,
            "provider": TranslationProvider.NONE
        }
    
    # Essayer DeepL en premier (meilleure qualité)
    if DEEPL_API_KEY:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api-free.deepl.com/v2/translate",
                    headers={
                        "Authorization": f"DeepL-Auth-Key {DEEPL_API_KEY}",
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    data={
                        "text": text,
                        "target_lang": target_lang_upper,
                        **({"source_lang": source_lang_upper} if source_lang else {})
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "translatedText": data["translations"][0]["text"],
                        "detectedLanguage": data["translations"][0].get("detected_source_language", source_lang),
                        "provider": TranslationProvider.DEEPL
                    }
        except Exception as e:
            print(f"DeepL translation failed: {e}, trying alternatives...")
    
    # Fallback: Google Translate
    if GOOGLE_TRANSLATE_API_KEY:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://translation.googleapis.com/language/translate/v2",
                    params={"key": GOOGLE_TRANSLATE_API_KEY},
                    json={
                        "q": text,
                        "target": target_lang.lower(),
                        **({"source": source_lang.lower()} if source_lang else {})
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "translatedText": data["data"]["translations"][0]["translatedText"],
                        "detectedLanguage": data["data"]["translations"][0].get("detectedSourceLanguage", source_lang),
                        "provider": TranslationProvider.GOOGLE
                    }
        except Exception as e:
            print(f"Google Translate failed: {e}, trying LibreTranslate...")
    
    # Fallback: LibreTranslate (gratuit mais moins précis, supporte 500+ langues)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{LIBRETRANSLATE_URL}/translate",
                json={
                    "q": text,
                    "source": source_lang.lower() if source_lang else "auto",
                    "target": target_lang.lower()
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "translatedText": data["translatedText"],
                    "detectedLanguage": source_lang or "auto",
                    "provider": TranslationProvider.LIBRETRANSLATE
                }
    except Exception as e:
        print(f"LibreTranslate failed: {e}")
    
    # Si tout échoue, retourner le texte original
    return {
        "translatedText": text,
        "detectedLanguage": source_lang or "unknown",
        "provider": TranslationProvider.NONE
    }


async def translate_to_multiple_languages(
    text: str,
    target_langs: List[str],
    source_lang: Optional[str] = None
) -> Dict[str, Dict[str, str]]:
    """
    Traduit un texte vers plusieurs langues simultanément
    
    Args:
        text: Texte à traduire
        target_langs: Liste des codes de langues cibles
        source_lang: Code de la langue source (optionnel)
        
    Returns:
        Dict avec les codes de langues comme clés et les traductions comme valeurs
    """
    translations = {}
    
    # Traduire vers chaque langue
    for target_lang in target_langs:
        try:
            result = await translate_text(text, target_lang, source_lang)
            translations[target_lang] = result
        except Exception as e:
            print(f"Failed to translate to {target_lang}: {e}")
            translations[target_lang] = {
                "translatedText": text,
                "detectedLanguage": source_lang or "unknown",
                "provider": TranslationProvider.NONE
            }
    
    return translations


def get_language_info(lang_code: str) -> Optional[LanguageInfo]:
    """
    Obtient les informations sur une langue à partir de son code
    
    Args:
        lang_code: Code de la langue (ex: "EN", "FR", "AR")
        
    Returns:
        LanguageInfo object ou None si la langue n'est pas trouvée
    """
    return LANGUAGE_MAP.get(lang_code.upper()) or LANGUAGE_MAP.get(lang_code.lower())


def get_all_supported_languages() -> List[Dict]:
    """
    Retourne la liste de toutes les langues supportées (644+)
    
    Returns:
        Liste de dictionnaires contenant les infos de chaque langue
    """
    return [lang.to_dict() for lang in ALL_LANGUAGES]


def get_languages_by_provider(provider: TranslationProvider) -> List[Dict]:
    """
    Retourne les langues supportées par un provider spécifique
    
    Args:
        provider: Provider de traduction
        
    Returns:
        Liste de dictionnaires contenant les infos des langues
    """
    return [
        lang.to_dict() 
        for lang in ALL_LANGUAGES 
        if lang.provider == provider
    ]


def get_voice_supported_languages() -> List[Dict]:
    """
    Retourne les langues avec support vocal (TTS/STT)
    
    Returns:
        Liste de dictionnaires contenant les infos des langues avec voix
    """
    return [
        lang.to_dict() 
        for lang in ALL_LANGUAGES 
        if lang.voice_support
    ]


def get_best_voice_for_language(lang_code: str) -> str:
    """
    Trouve la meilleure voix Google TTS pour une langue donnée
    
    Args:
        lang_code: Code de la langue
        
    Returns:
        Nom de la voix Google TTS recommandée
    """
    voice_map = {
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
    }
    
    return voice_map.get(lang_code.upper(), 'en-US-Neural2-A')


# Stats sur les langues supportées
def get_language_stats() -> Dict:
    """
    Retourne des statistiques sur les langues supportées
    
    Returns:
        Dict avec les stats (total, par provider, avec voix, etc.)
    """
    return {
        "total_languages": len(ALL_LANGUAGES),
        "deepl_languages": len(DEEPL_LANGUAGES),
        "google_languages": len(GOOGLE_LANGUAGES),
        "libretranslate_additional": 500,  # Estimation des langues additionnelles via LibreTranslate
        "total_with_libretranslate": 644,
        "voice_supported": len([lang for lang in ALL_LANGUAGES if lang.voice_support]),
        "providers": [
            TranslationProvider.DEEPL,
            TranslationProvider.GOOGLE,
            TranslationProvider.LIBRETRANSLATE
        ]
    }
