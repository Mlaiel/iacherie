"""Internationalization (i18n) Manager for Ainflue Platform
Supports 195+ languages with automatic translation and localization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path
import re
from enum import Enum

logger = logging.getLogger(__name__)


class LanguageRegion(Enum):
    """
Language regions for proper localization"""

    AFRICA = "africa"
    ASIA = "asia"
    EUROPE = "europe"
    NORTH_AMERICA = "north_america"
    SOUTH_AMERICA = "south_america"
    OCEANIA = "oceania"


class LanguageScript(Enum):
    """Writing system scripts"""

    LATIN = "latin"
    CYRILLIC = "cyrillic"
    ARABIC = "arabic"
    CHINESE = "chinese"
    JAPANESE = "japanese"
    KOREAN = "korean"
    DEVANAGARI = "devanagari"
    THAI = "thai"
    HEBREW = "hebrew"
    TIFINAGH = "tifinagh"  # Amazigh/Berber script


@dataclass
class LanguageInfo:
    """Complete language information"""
    code: str  # ISO 639-1/639-3 code
    name: str  # English name
    native_name: str  # Native name
    region: LanguageRegion
    script: LanguageScript
    rtl: bool = False  # Right-to-left
    plural_rules: Dict[str, str] = None
    date_format: str = "%Y-%m-%d"
    time_format: str = "%H:%M:%S"
    currency_format: str = "{amount} {currency}"
    number_format: Dict[str, str] = None
    fallback_language: str = "en"
    translation_quality: float = 1.0  # 0.0-1.0
    auto_translate: bool = True
    enabled: bool = True


class InternationalizationManager:
    """Advanced internationalization manager supporting 195+ languages"""
    
    def __init__(self):
        self.languages: Dict[str, LanguageInfo] = {}
        self.translations: Dict[str, Dict[str, str]] = {}
        self.cached_translations: Dict[str, Dict[str, str]] = {}
        self.translation_providers = []
        self.default_language = "en"
        self.fallback_chain = ["en", "es", "fr", "de", "zh"]
        
        # Initialize all supported languages
        self._initialize_languages()
        
    def _initialize_languages(self):
        """Initialize comprehensive language support (195+ languages)"""
        
        # Major languages (Tier 1 - Human translated)
        major_languages = [
            # European languages
            LanguageInfo("en", "English", "English", LanguageRegion.EUROPE, LanguageScript.LATIN),
            LanguageInfo("es", "Spanish", "Español", LanguageRegion.EUROPE, LanguageScript.LATIN),
            LanguageInfo("fr", "French", "Français", LanguageRegion.EUROPE, LanguageScript.LATIN),
            LanguageInfo("de", "German", "Deutsch", LanguageRegion.EUROPE, LanguageScript.LATIN),
            LanguageInfo("it", "Italian", "Italiano", LanguageRegion.EUROPE, LanguageScript.LATIN),
            LanguageInfo("pt", "Portuguese", "Português", LanguageRegion.EUROPE, LanguageScript.LATIN),
            LanguageInfo("ru", "Russian", "Русский", LanguageRegion.EUROPE, LanguageScript.CYRILLIC),
            LanguageInfo("pl", "Polish", "Polski", LanguageRegion.EUROPE, LanguageScript.LATIN),
            LanguageInfo("nl", "Dutch", "Nederlands", LanguageRegion.EUROPE, LanguageScript.LATIN),
            LanguageInfo("sv", "Swedish", "Svenska", LanguageRegion.EUROPE, LanguageScript.LATIN),
            LanguageInfo("da", "Danish", "Dansk", LanguageRegion.EUROPE, LanguageScript.LATIN),
            LanguageInfo("no", "Norwegian", "Norsk", LanguageRegion.EUROPE, LanguageScript.LATIN),
            LanguageInfo("fi", "Finnish", "Suomi", LanguageRegion.EUROPE, LanguageScript.LATIN),
            LanguageInfo("el", "Greek", "Ελληνικά", LanguageRegion.EUROPE, LanguageScript.LATIN),
            LanguageInfo("cs", "Czech", "Čeština", LanguageRegion.EUROPE, LanguageScript.LATIN),
            LanguageInfo("hu", "Hungarian", "Magyar", LanguageRegion.EUROPE, LanguageScript.LATIN),
            LanguageInfo("ro", "Romanian", "Română", LanguageRegion.EUROPE, LanguageScript.LATIN),
            LanguageInfo("bg", "Bulgarian", "Български", LanguageRegion.EUROPE, LanguageScript.CYRILLIC),
            LanguageInfo("hr", "Croatian", "Hrvatski", LanguageRegion.EUROPE, LanguageScript.LATIN),
            LanguageInfo("sk", "Slovak", "Slovenčina", LanguageRegion.EUROPE, LanguageScript.LATIN),
            LanguageInfo("sl", "Slovenian", "Slovenščina", LanguageRegion.EUROPE, LanguageScript.LATIN),
            LanguageInfo("et", "Estonian", "Eesti", LanguageRegion.EUROPE, LanguageScript.LATIN),
            LanguageInfo("lv", "Latvian", "Latviešu", LanguageRegion.EUROPE, LanguageScript.LATIN),
            LanguageInfo("lt", "Lithuanian", "Lietuvių", LanguageRegion.EUROPE, LanguageScript.LATIN),
            LanguageInfo("uk", "Ukrainian", "Українська", LanguageRegion.EUROPE, LanguageScript.CYRILLIC),
            LanguageInfo("be", "Belarusian", "Беларуская", LanguageRegion.EUROPE, LanguageScript.CYRILLIC),
            
            # Asian languages
            LanguageInfo("zh", "Chinese", "中文", LanguageRegion.ASIA, LanguageScript.CHINESE),
            LanguageInfo("ja", "Japanese", "日本語", LanguageRegion.ASIA, LanguageScript.JAPANESE),
            LanguageInfo("ko", "Korean", "한국어", LanguageRegion.ASIA, LanguageScript.KOREAN),
            LanguageInfo("hi", "Hindi", "हिन्दी", LanguageRegion.ASIA, LanguageScript.DEVANAGARI),
            LanguageInfo("ar", "Arabic", "العربية", LanguageRegion.ASIA, LanguageScript.ARABIC, rtl=True),
            LanguageInfo("fa", "Persian", "فارسی", LanguageRegion.ASIA, LanguageScript.ARABIC, rtl=True),
            LanguageInfo("ur", "Urdu", "اردو", LanguageRegion.ASIA, LanguageScript.ARABIC, rtl=True),
            LanguageInfo("he", "Hebrew", "עברית", LanguageRegion.ASIA, LanguageScript.HEBREW, rtl=True),
            LanguageInfo("th", "Thai", "ไทย", LanguageRegion.ASIA, LanguageScript.THAI),
            LanguageInfo("vi", "Vietnamese", "Tiếng Việt", LanguageRegion.ASIA, LanguageScript.LATIN),
            LanguageInfo("id", "Indonesian", "Bahasa Indonesia", LanguageRegion.ASIA, LanguageScript.LATIN),
            LanguageInfo("ms", "Malay", "Bahasa Melayu", LanguageRegion.ASIA, LanguageScript.LATIN),
            LanguageInfo("tl", "Filipino", "Filipino", LanguageRegion.ASIA, LanguageScript.LATIN),
            LanguageInfo("bn", "Bengali", "বাংলা", LanguageRegion.ASIA, LanguageScript.DEVANAGARI),
            LanguageInfo("te", "Telugu", "తెలుగు", LanguageRegion.ASIA, LanguageScript.DEVANAGARI),
            LanguageInfo("ta", "Tamil", "தமிழ்", LanguageRegion.ASIA, LanguageScript.DEVANAGARI),
            LanguageInfo("ml", "Malayalam", "മലയാളം", LanguageRegion.ASIA, LanguageScript.DEVANAGARI),
            LanguageInfo("kn", "Kannada", "ಕನ್ನಡ", LanguageRegion.ASIA, LanguageScript.DEVANAGARI),
            LanguageInfo("gu", "Gujarati", "ગુજરાતી", LanguageRegion.ASIA, LanguageScript.DEVANAGARI),
            LanguageInfo("pa", "Punjabi", "ਪੰਜਾਬੀ", LanguageRegion.ASIA, LanguageScript.DEVANAGARI),
            LanguageInfo("mr", "Marathi", "मराठी", LanguageRegion.ASIA, LanguageScript.DEVANAGARI),
            
            # African languages  
            LanguageInfo("sw", "Swahili", "Kiswahili", LanguageRegion.AFRICA, LanguageScript.LATIN),
            LanguageInfo("af", "Afrikaans", "Afrikaans", LanguageRegion.AFRICA, LanguageScript.LATIN),
            LanguageInfo("zu", "Zulu", "isiZulu", LanguageRegion.AFRICA, LanguageScript.LATIN),
            LanguageInfo("xh", "Xhosa", "isiXhosa", LanguageRegion.AFRICA, LanguageScript.LATIN),
            LanguageInfo("am", "Amharic", "አማርኛ", LanguageRegion.AFRICA, LanguageScript.LATIN),
            LanguageInfo("ha", "Hausa", "Hausa", LanguageRegion.AFRICA, LanguageScript.LATIN),
            LanguageInfo("yo", "Yoruba", "Yorùbá", LanguageRegion.AFRICA, LanguageScript.LATIN),
            LanguageInfo("ig", "Igbo", "Igbo", LanguageRegion.AFRICA, LanguageScript.LATIN),
            
            # American languages
            LanguageInfo("pt-BR", "Portuguese (Brazil)", "Português (Brasil)", LanguageRegion.SOUTH_AMERICA, LanguageScript.LATIN),
            LanguageInfo("es-MX", "Spanish (Mexico)", "Español (México)", LanguageRegion.NORTH_AMERICA, LanguageScript.LATIN),
            LanguageInfo("es-AR", "Spanish (Argentina)", "Español (Argentina)", LanguageRegion.SOUTH_AMERICA, LanguageScript.LATIN),
            LanguageInfo("fr-CA", "French (Canada)", "Français (Canada)", LanguageRegion.NORTH_AMERICA, LanguageScript.LATIN),
        ]
        
        # Add all major languages
        for lang in major_languages:
            self.languages[lang.code] = lang
            
        # Add extended language support (auto-translated)
        self._add_extended_languages()
        
        logger.info(f"Initialized {len(self.languages)} languages")
        
        # Initialize extended language support for 644+ languages
        try:
            from .extended_language_support import ExtendedLanguageSupport
            self.extended_support = ExtendedLanguageSupport(self)
            logger.info(f"Extended language support initialized: {self.extended_support.get_language_count()} total languages")
        except ImportError as e:
            logger.warning(f"Extended language support not available: {e}")
            self.extended_support = None
    
    def _add_extended_languages(self):
        """Add extended language support for comprehensive coverage"""
        
        # Additional European languages
        extended_european = [
            ("is", "Icelandic", "Íslenska"),
            ("mt", "Maltese", "Malti"),
            ("ga", "Irish", "Gaeilge"),
            ("cy", "Welsh", "Cymraeg"),
            ("eu", "Basque", "Euskera"),
            ("ca", "Catalan", "Català"),
            ("gl", "Galician", "Galego"),
            ("br", "Breton", "Brezhoneg"),
            ("co", "Corsican", "Corsu"),
            ("sc", "Sardinian", "Sardu"),
            ("rm", "Romansh", "Rumantsch"),
            ("fy", "Frisian", "Frysk"),
            ("lb", "Luxembourgish", "Lëtzebuergesch"),
            ("mk", "Macedonian", "Македонски"),
            ("sq", "Albanian", "Shqip"),
            ("sr", "Serbian", "Српски"),
            ("bs", "Bosnian", "Bosanski"),
            ("me", "Montenegrin", "Crnogorski"),
        ]
        
        # Additional Asian languages
        extended_asian = [
            ("tr", "Turkish", "Türkçe"),
            ("az", "Azerbaijani", "Azərbaycan"),
            ("kk", "Kazakh", "Қазақша"),
            ("ky", "Kyrgyz", "Кыргызча"),
            ("uz", "Uzbek", "O'zbek"),
            ("tk", "Turkmen", "Türkmen"),
            ("tg", "Tajik", "Тоҷикӣ"),
            ("mn", "Mongolian", "Монгол"),
            ("ne", "Nepali", "नेपाली"),
            ("si", "Sinhala", "සිංහල"),
            ("my", "Myanmar", "မြန်မာ"),
            ("km", "Khmer", "ខ្មែរ"),
            ("lo", "Lao", "ລາວ"),
            ("ka", "Georgian", "ქართული"),
            ("hy", "Armenian", "Հայերեն"),
            ("ku", "Kurdish", "Kurdî"),
            ("ps", "Pashto", "پښتو"),
            ("sd", "Sindhi", "سنڌي"),
            ("dv", "Dhivehi", "ދިވެހި"),
        ]
        
        # Additional African languages
        extended_african = [
            ("ar-MA", "Arabic (Morocco)", "العربية (المغرب)"),
            ("ar-EG", "Arabic (Egypt)", "العربية (مصر)"),
            ("ar-SA", "Arabic (Saudi Arabia)", "العربية (السعودية)"),
            ("fr-SN", "French (Senegal)", "Français (Sénégal)"),
            ("pt-AO", "Portuguese (Angola)", "Português (Angola)"),
            ("pt-MZ", "Portuguese (Mozambique)", "Português (Moçambique)"),
            ("rw", "Kinyarwanda", "Ikinyarwanda"),
            ("lg", "Luganda", "Luganda"),
            ("om", "Oromo", "Afaan Oromoo"),
            ("ti", "Tigrinya", "ትግርኛ"),
            ("so", "Somali", "Soomaali"),
            ("mg", "Malagasy", "Malagasy"),
            ("ny", "Chichewa", "Chichewa"),
            ("sn", "Shona", "ChiShona"),
            ("st", "Sesotho", "Sesotho"),
            ("tn", "Setswana", "Setswana"),
            ("ve", "Venda", "Tshivenḓa"),
            ("ts", "Tsonga", "Xitsonga"),
            ("ss", "Swati", "siSwati"),
            ("nr", "Ndebele", "isiNdebele"),
        ]
        
        # Additional American languages
        extended_american = [
            ("qu", "Quechua", "Runa Simi"),
            ("gn", "Guarani", "Avañe'ẽ"),
            ("ay", "Aymara", "Aymar aru"),
            ("ht", "Haitian Creole", "Kreyòl Ayisyen"),
            ("nv", "Navajo", "Diné bizaad"),
            ("chr", "Cherokee", "ᏣᎳᎩ"),
            ("iu", "Inuktitut", "ᐃᓄᒃᑎᑐᑦ"),
            ("kl", "Greenlandic", "Kalaallisut"),
        ]
        
        # Pacific languages
        pacific_languages = [
            ("mi", "Maori", "Te Reo Māori"),
            ("sm", "Samoan", "Gagana Samoa"),
            ("to", "Tongan", "Lea Fakatonga"),
            ("fj", "Fijian", "Na Vosa Vakaviti"),
            ("haw", "Hawaiian", "ʻŌlelo Hawaiʻi"),
            ("ty", "Tahitian", "Reo Tahiti"),
            ("gil", "Gilbertese", "Taetae ni Kiribati"),
            ("mh", "Marshallese", "Kajin M̧ajeļ"),
            ("na", "Nauruan", "Dorerin Naoero"),
            ("pon", "Pohnpeian", "Lokaiahn Pohnpei"),
            ("chk", "Chuukese", "Finefenubwach"),
            ("kos", "Kosraean", "Kosrae"),
            ("yap", "Yapese", "Waqab"),
            ("pau", "Palauan", "a tekoi er a Belau"),
            ("tvl", "Tuvaluan", "Te Ggana Tuuvalu"),
            ("niu", "Niuean", "Ko e Vagahau Niuē"),
            ("tkl", "Tokelauan", "Gagana Tokelau"),
        ]
        
        # CRITICAL: Add Amazigh/Berber languages (missing from original)
        amazigh_berber_languages = [
            # Primary Amazigh/Berber Languages
            ("tzm", "Central Atlas Tamazight", "ⵜⴰⵎⴰⵣⵉⵖⵜ"),
            ("rif", "Tarifit (Rif Berber)", "ⵜⴰⵔⵉⴼⵉⵜ"),
            ("shi", "Tashelhit (Souss Berber)", "ⵜⴰⵛⵍⵃⵉⵜ"),
            ("kab", "Kabyle", "ⵜⴰⵇⴱⴰⵢⵍⵉⵜ"),
            ("shy", "Chaouia (Shawiya)", "ⵜⴰⵛⴰⵡⵉⵜ"),
            ("mzb", "Tumzabt (Mozabite)", "ⵜⵓⵎⵣⴰⴱⵜ"),
            ("thv", "Tahaggart Tamahaq", "ⵜⴰⵀⴰⴳⴳⴰⵔⵜ"),
            ("ttq", "Tawallammat Tamajaq", "ⵜⴰⵡⴰⵍⵍⴰⵎⵎⴰⵜ"),
            ("taq", "Tamasheq", "ⵜⴰⵎⴰⵛⴻⵖ"),
            ("zen", "Zenaga", "ⵜⵓⵣⵏⴰⴳⴰ"),
            
            # Regional Amazigh Dialects - Morocco
            ("tzm-MA-cent", "Central Morocco Tamazight", "ⵜⴰⵎⴰⵣⵉⵖⵜ ⵏ ⵡⴰⵟⵍⴰⵙ"),
            ("rif-MA-north", "Northern Morocco Tarifit", "ⵜⴰⵔⵉⴼⵉⵜ ⵏ ⵓⴳⴰⴼⴰⵢ"),
            ("shi-MA-south", "Southern Morocco Tashelhit", "ⵜⴰⵛⵍⵃⵉⵜ ⵏ ⵓⵏⵣⵓⵍ"),
            
            # Regional Amazigh Dialects - Algeria  
            ("kab-DZ-tizi", "Tizi Ouzou Kabyle", "ⵜⴰⵇⴱⴰⵢⵍⵉⵜ ⵏ ⵜⵉⵣⵉ ⵡⴻⵣⵣⵓ"),
            ("shy-DZ-aures", "Aurès Chaouia", "ⵜⴰⵛⴰⵡⵉⵜ ⵏ ⵡⴰⵡⵔⴰⵙ"),
            ("mzb-DZ-ghardaia", "Ghardaïa Mozabite", "ⵜⵓⵎⵣⴰⴱⵜ ⵏ ⵖⴰⵔⴷⴰⵢⴰ"),
            
            # Regional Amazigh Dialects - Tuareg (Multi-country)
            ("thv-DZ-hoggar", "Hoggar Tuareg (Algeria)", "ⵜⴰⵀⴰⴳⴳⴰⵔⵜ ⵏ ⵍⵣⴰⵢⴻⵔ"),
            ("ttq-NE-niger", "Niger Tuareg", "ⵜⴰⵎⴰⵊⴰⵖ ⵏ ⵏⵉⵊⴻⵔ"),
            ("taq-ML-mali", "Mali Tuareg", "ⵜⴰⵎⴰⵛⴻⵖ ⵏ ⵎⴰⵍⵉ"),
            ("thv-LY-fezzan", "Fezzan Tuareg (Libya)", "ⵜⴰⵀⴰⴳⴳⴰⵔⵜ ⵏ ⴼⴻⵣⵣⴰⵏ"),
            
            # Additional Berber Languages
            ("siz", "Siwi (Siwa Oasis)", "ⵙⵉⵡⵉ"),
            ("jbn", "Nafusi (Jebel Nafusa)", "ⵏⴰⴼⵓⵙⵉ"),
            ("gha", "Ghadamès Berber", "ⵖⴰⴷⴰⵎⴻⵙ"),
            ("auj", "Awjila Berber", "ⴰⵡⵊⵉⵍⴰ"),
            ("soc", "Sokna Berber", "ⵙⵓⴽⵏⴰ"),
            
            # Canary Islands (Historical)
            ("guanche", "Guanche (Canary Islands)", "Guanche"),
        ]
        
        # North African Arabic Dialects (Critical for completeness)
        north_african_dialects = [
            # Tunisian Regional Dialects
            ("ar-TN-tunis", "Tunisian Arabic (Tunis)", "تونسي (تونس)"),
            ("ar-TN-sfax", "Tunisian Arabic (Sfax)", "تونسي (صفاقس)"),
            ("ar-TN-sousse", "Tunisian Arabic (Sousse)", "تونسي (سوسة)"),
            ("ar-TN-gafsa", "Tunisian Arabic (Gafsa)", "تونسي (قفصة)"),
            ("ar-TN-kairouan", "Tunisian Arabic (Kairouan)", "تونسي (القيروان)"),
            ("ar-TN-bizerte", "Tunisian Arabic (Bizerte)", "تونسي (بنزرت)"),
            ("ar-TN-gabes", "Tunisian Arabic (Gabès)", "تونسي (قابس)"),
            ("ar-TN-tozeur", "Tunisian Arabic (Tozeur)", "تونسي (توزر)"),
            ("ar-TN-mahdia", "Tunisian Arabic (Mahdia)", "تونسي (المهدية)"),
            ("ar-TN-monastir", "Tunisian Arabic (Monastir)", "تونسي (المنستير)"),
            ("ar-TN-nabeul", "Tunisian Arabic (Nabeul)", "تونسي (نابل)"),
            ("ar-TN-kef", "Tunisian Arabic (Le Kef)", "تونسي (الكاف)"),
            ("ar-TN-kasserine", "Tunisian Arabic (Kasserine)", "تونسي (القصرين)"),
            ("ar-TN-medenine", "Tunisian Arabic (Médenine)", "تونسي (مدنين)"),
            
            # Algerian Regional Dialects
            ("ar-DZ-algiers", "Algerian Arabic (Algiers)", "دزيري (الجزائر)"),
            ("ar-DZ-oran", "Algerian Arabic (Oran)", "دزيري (وهران)"),
            ("ar-DZ-constantine", "Algerian Arabic (Constantine)", "دزيري (قسنطينة)"),
            ("ar-DZ-annaba", "Algerian Arabic (Annaba)", "دزيري (عنابة)"),
            ("ar-DZ-setif", "Algerian Arabic (Sétif)", "دزيري (سطيف)"),
            ("ar-DZ-tlemcen", "Algerian Arabic (Tlemcen)", "دزيري (تلمسان)"),
            ("ar-DZ-batna", "Algerian Arabic (Batna)", "دزيري (باتنة)"),
            ("ar-DZ-biskra", "Algerian Arabic (Biskra)", "دزيري (بسكرة)"),
            ("ar-DZ-ouargla", "Algerian Arabic (Ouargla)", "دزيري (ورقلة)"),
            ("ar-DZ-ghardaia", "Algerian Arabic (Ghardaïa)", "دزيري (غرداية)"),
            ("ar-DZ-adrar", "Algerian Arabic (Adrar)", "دزيري (أدرار)"),
            ("ar-DZ-tamanrasset", "Algerian Arabic (Tamanrasset)", "دزيري (تمنراست)"),
            ("ar-DZ-bechar", "Algerian Arabic (Béchar)", "دزيري (بشار)"),
            ("ar-DZ-tindouf", "Algerian Arabic (Tindouf)", "دزيري (تندوف)"),
            ("ar-DZ-illizi", "Algerian Arabic (Illizi)", "دزيري (إليزي)"),
            
            # Moroccan Regional Dialects
            ("ar-MA-casablanca", "Moroccan Arabic (Casablanca)", "دارجة (الدار البيضاء)"),
            ("ar-MA-rabat", "Moroccan Arabic (Rabat)", "دارجة (الرباط)"),
            ("ar-MA-fes", "Moroccan Arabic (Fès)", "دارجة (فاس)"),
            ("ar-MA-marrakech", "Moroccan Arabic (Marrakech)", "دارجة (مراكش)"),
            ("ar-MA-agadir", "Moroccan Arabic (Agadir)", "دارجة (أكادير)"),
            ("ar-MA-tangier", "Moroccan Arabic (Tangier)", "دارجة (طنجة)"),
            ("ar-MA-oujda", "Moroccan Arabic (Oujda)", "دارجة (وجدة)"),
            ("ar-MA-tetouan", "Moroccan Arabic (Tétouan)", "دارجة (تطوان)"),
            ("ar-MA-meknes", "Moroccan Arabic (Meknès)", "دارجة (مكناس)"),
            ("ar-MA-kenitra", "Moroccan Arabic (Kénitra)", "دارجة (القنيطرة)"),
            ("ar-MA-sale", "Moroccan Arabic (Salé)", "دارجة (سلا)"),
            ("ar-MA-mohammedia", "Moroccan Arabic (Mohammedia)", "دارجة (المحمدية)"),
            ("ar-MA-safi", "Moroccan Arabic (Safi)", "دارجة (آسفي)"),
            ("ar-MA-essaouira", "Moroccan Arabic (Essaouira)", "دارجة (الصويرة)"),
            ("ar-MA-ouarzazate", "Moroccan Arabic (Ouarzazate)", "دارجة (ورزازات)"),
            ("ar-MA-errachidia", "Moroccan Arabic (Errachidia)", "دارجة (الراشيدية)"),
            ("ar-MA-al-hoceima", "Moroccan Arabic (Al Hoceïma)", "دارجة (الحسيمة)"),
            ("ar-MA-chefchaouen", "Moroccan Arabic (Chefchaouen)", "دارجة (شفشاون)"),
            ("ar-MA-laayoune", "Moroccan Arabic (Laâyoune)", "دارجة (العيون)"),
            ("ar-MA-dakhla", "Moroccan Arabic (Dakhla)", "دارجة (الداخلة)"),
            
            # Libyan Regional Dialects
            ("ar-LY-tripoli", "Libyan Arabic (Tripoli)", "ليبي (طرابلس)"),
            ("ar-LY-benghazi", "Libyan Arabic (Benghazi)", "ليبي (بنغازي)"),
            ("ar-LY-misrata", "Libyan Arabic (Misrata)", "ليبي (مصراتة)"),
            ("ar-LY-sirte", "Libyan Arabic (Sirte)", "ليبي (سرت)"),
            ("ar-LY-sebha", "Libyan Arabic (Sebha)", "ليبي (سبها)"),
            ("ar-LY-murzuq", "Libyan Arabic (Murzuq)", "ليبي (مرزق)"),
            ("ar-LY-tobruk", "Libyan Arabic (Tobruk)", "ليبي (طبرق)"),
            ("ar-LY-derna", "Libyan Arabic (Derna)", "ليبي (درنة)"),
            ("ar-LY-bayda", "Libyan Arabic (Al Bayda)", "ليبي (البيضاء)"),
            ("ar-LY-zawiya", "Libyan Arabic (Zawiya)", "ليبي (الزاوية)"),
            ("ar-LY-nalut", "Libyan Arabic (Nalut)", "ليبي (نالوت)"),
            
            # Egyptian Regional Dialects
            ("ar-EG-cairo", "Egyptian Arabic (Cairo)", "مصري (القاهرة)"),
            ("ar-EG-alexandria", "Egyptian Arabic (Alexandria)", "مصري (الإسكندرية)"),
            ("ar-EG-giza", "Egyptian Arabic (Giza)", "مصري (الجيزة)"),
            ("ar-EG-luxor", "Egyptian Arabic (Luxor)", "مصري (الأقصر)"),
            ("ar-EG-aswan", "Egyptian Arabic (Aswan)", "مصري (أسوان)"),
            ("ar-EG-asyut", "Egyptian Arabic (Asyut)", "مصري (أسيوط)"),
            ("ar-EG-minya", "Egyptian Arabic (Minya)", "مصري (المنيا)"),
            ("ar-EG-fayoum", "Egyptian Arabic (Fayoum)", "مصري (الفيوم)"),
            ("ar-EG-suez", "Egyptian Arabic (Suez)", "مصري (السويس)"),
            ("ar-EG-ismailia", "Egyptian Arabic (Ismaïlia)", "مصري (الإسماعيلية)"),
            ("ar-EG-port-said", "Egyptian Arabic (Port Said)", "مصري (بورسعيد)"),
            ("ar-EG-damietta", "Egyptian Arabic (Damietta)", "مصري (دمياط)"),
            ("ar-EG-mansoura", "Egyptian Arabic (Mansoura)", "مصري (المنصورة)"),
            ("ar-EG-tanta", "Egyptian Arabic (Tanta)", "مصري (طنطا)"),
            ("ar-EG-zagazig", "Egyptian Arabic (Zagazig)", "مصري (الزقازيق)"),
            
            # Sudanese Regional Dialects
            ("ar-SD-khartoum", "Sudanese Arabic (Khartoum)", "سوداني (الخرطوم)"),
            ("ar-SD-omdurman", "Sudanese Arabic (Omdurman)", "سوداني (أم درمان)"),
            ("ar-SD-port-sudan", "Sudanese Arabic (Port Sudan)", "سوداني (بورتسودان)"),
            ("ar-SD-kassala", "Sudanese Arabic (Kassala)", "سوداني (كسلا)"),
            ("ar-SD-gedaref", "Sudanese Arabic (Gedaref)", "سوداني (القضارف)"),
            ("ar-SD-nyala", "Sudanese Arabic (Nyala)", "سوداني (نيالا)"),
            ("ar-SD-el-fasher", "Sudanese Arabic (El Fasher)", "سوداني (الفاشر)"),
            ("ar-SD-el-obeid", "Sudanese Arabic (El Obeid)", "سوداني (الأبيض)"),
            ("ar-SD-wad-madani", "Sudanese Arabic (Wad Madani)", "سوداني (ود مدني)"),
            ("ar-SD-atbara", "Sudanese Arabic (Atbara)", "سوداني (عطبرة)"),
            ("ar-SD-dongola", "Sudanese Arabic (Dongola)", "سوداني (دنقلا)"),
            ("ar-SD-kosti", "Sudanese Arabic (Kosti)", "سوداني (كوستي)"),
            ("ar-SD-sennar", "Sudanese Arabic (Sennar)", "سوداني (سنار)"),
            
            # Mauritanian Regional Dialects
            ("ar-MR-nouakchott", "Mauritanian Arabic (Nouakchott)", "موريتاني (نواكشوط)"),
            ("ar-MR-nouadhibou", "Mauritanian Arabic (Nouadhibou)", "موريتاني (نواذيبو)"),
            ("ar-MR-atar", "Mauritanian Arabic (Atar)", "موريتاني (أطار)"),
            ("ar-MR-rosso", "Mauritanian Arabic (Rosso)", "موريتاني (روصو)"),
            ("ar-MR-kaedi", "Mauritanian Arabic (Kaédi)", "موريتاني (كيهيدي)"),
            ("ar-MR-kiffa", "Mauritanian Arabic (Kiffa)", "موريتاني (كيفة)"),
            ("ar-MR-aioun", "Mauritanian Arabic (Aïoun)", "موريتاني (عيون العتروس)"),
            ("ar-MR-nema", "Mauritanian Arabic (Néma)", "موريتاني (النعمة)"),
            ("ar-MR-tidjikja", "Mauritanian Arabic (Tidjikja)", "موريتاني (تيجيكجة)"),
            ("ar-MR-boutilimit", "Mauritanian Arabic (Boutilimit)", "موريتاني (بوتلميت)"),
            ("ar-MR-selibaby", "Mauritanian Arabic (Sélibaby)", "موريتاني (سيلبابي)"),
            ("ar-MR-maghama", "Mauritanian Arabic (Maghama)", "موريتاني (مقامة)"),
            
            # Hassanya Arabic (Mauritanian Bedouin)
            ("mey", "Hassaniyya Arabic", "حسانية"),
        ]
        
        # Add all extended languages with auto-translation enabled
        all_extended = (extended_european + extended_asian + extended_african + 
                       extended_american + pacific_languages + amazigh_berber_languages + 
                       north_african_dialects)
        
        for code, name, native_name in all_extended:
            # Determine region and script based on language
            region = self._determine_region(code)
            script = self._determine_script(code)
            rtl = self._is_rtl_language(code)
            
            lang_info = LanguageInfo(
                code=code,
                name=name,
                native_name=native_name,
                region=region,
                script=script,
                rtl=rtl,
                translation_quality=0.8,  # Auto-translated quality
                auto_translate=True,
                fallback_language=self._determine_fallback(code)
            )
            
            self.languages[code] = lang_info
    
    def _determine_region(self, code: str) -> LanguageRegion:
        """Determine language region based on language code"""
        european = ["is", "mt", "ga", "cy", "eu", "ca", "gl", "br", "co", "sc", "rm", "fy", "lb", "mk", "sq", "sr", "bs", "me"]
        asian = ["tr", "az", "kk", "ky", "uz", "tk", "tg", "mn", "ne", "si", "my", "km", "lo", "ka", "hy", "ku", "ps", "sd", "dv"]
        african = ["ar-MA", "ar-EG", "ar-SA", "fr-SN", "pt-AO", "pt-MZ", "rw", "lg", "om", "ti", "so", "mg", "ny", "sn", "st", "tn", "ve", "ts", "ss", "nr"]
        american = ["qu", "gn", "ay", "ht", "nv", "chr", "iu", "kl"]
        pacific = ["mi", "sm", "to", "fj", "haw", "ty", "gil", "mh", "na", "pon", "chk", "kos", "yap", "pau", "tvl", "niu", "tkl"]
        
        if code in european:
            return LanguageRegion.EUROPE
        elif code in asian:
            return LanguageRegion.ASIA
        elif code in african:
            return LanguageRegion.AFRICA
        elif code in american:
            return LanguageRegion.NORTH_AMERICA
        elif code in pacific:
            return LanguageRegion.OCEANIA
        else:
            return LanguageRegion.EUROPE  # Default
    
    def _determine_script(self, code: str) -> LanguageScript:
        """Determine writing script based on language code"""
        cyrillic = ["mk", "sr", "kk", "ky", "tg", "mn"]
        arabic = ["ar-MA", "ar-EG", "ar-SA", "ku", "ps", "sd", "dv"] + \
                [f"ar-{country}-{city}" for country in ["TN", "DZ", "MA", "LY", "SD", "MR"] 
                 for city in ["tunis", "sfax", "algiers", "oran", "casablanca", "fes", "tripoli", "benghazi", "khartoum", "nouakchott"]]
        devanagari = ["ne"]
        thai = ["km", "lo"]
        tifinagh = ["tzm", "rif", "shi", "kab", "shy", "mzb", "thv", "ttq", "taq", "zen"] + \
                  [f"{base}-{country}-{region}" for base in ["tzm", "rif", "shi", "kab", "shy", "mzb", "thv", "ttq", "taq"] 
                   for country in ["MA", "DZ", "NE", "ML", "LY"] for region in ["cent", "north", "south", "tizi", "aures", "ghardaia", "hoggar", "niger", "mali", "fezzan"]]
        
        if code in cyrillic:
            return LanguageScript.CYRILLIC
        elif code in arabic:
            return LanguageScript.ARABIC
        elif code in devanagari:
            return LanguageScript.DEVANAGARI
        elif code in thai:
            return LanguageScript.THAI
        elif code in tifinagh:
            return LanguageScript.TIFINAGH
        else:
            return LanguageScript.LATIN
    
    def _is_rtl_language(self, code: str) -> bool:
        """Check if language is right-to-left"""
        rtl_languages = ["ar-MA", "ar-EG", "ar-SA", "ku", "ps", "sd", "dv"]
        return code in rtl_languages
    
    def _determine_fallback(self, code: str) -> str:
        """Determine fallback language based on region"""
        if code.startswith("ar"):
            return "ar"
        elif code.startswith("es"):
            return "es"
        elif code.startswith("pt"):
            return "pt"
        elif code.startswith("fr"):
            return "fr"
        else:
            return "en"
    
    async def get_translation(
        self, 
        key: str, 
        language: str, 
        default: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Get translation for a key in specified language"""
        try:
            # Check if language is supported
            if language not in self.languages:
                language = self.default_language
            
            # Check cache first
            cache_key = f"{language}:{key}"
            if cache_key in self.cached_translations:
                translation = self.cached_translations[cache_key]
            else:
                # Load translation from storage
                translation = await self._load_translation(key, language)
                self.cached_translations[cache_key] = translation
            
            # If translation not found, use fallback chain
            if not translation:
                translation = await self._get_fallback_translation(key, language)
            
            # Apply context variables if provided
            if translation and context:
                translation = self._apply_context(translation, context)
            
            return translation or default or key
            
        except Exception as e:
            logger.error(f"Error getting translation for {key} in {language}: {str(e)}")
            return default or key
    
    async def _load_translation(self, key: str, language: str) -> Optional[str]:
        """Load translation from storage or translation service"""
        try:
            # Try to load from local translation files
            translation_file = Path(f"translations/{language}.json")
            if translation_file.exists():
                with open(translation_file, 'r', encoding='utf-8') as f:
                    translations = json.load(f)
                    return translations.get(key)
            
            # If not found and auto-translate is enabled, use translation service
            lang_info = self.languages.get(language)
            if lang_info and lang_info.auto_translate:
                return await self._auto_translate(key, language)
            
            return None
            
        except Exception as e:
            logger.error(f"Error loading translation: {str(e)}")
            return None
    
    async def _auto_translate(self, text: str, target_language: str) -> Optional[str]:
        """Auto-translate text using AI translation services"""
        try:
            # This would integrate with translation services like:
            # - Google Translate API
            # - DeepL API
            # - Azure Translator
            # - AWS Translate
            
            # For now, return a placeholder implementation
            # In production, this would call actual translation APIs
            
            if target_language == "es":
                # Mock Spanish translation
                return f"[ES] {text}"
            elif target_language == "fr":
                # Mock French translation  
                return f"[FR] {text}"
            elif target_language == "de":
                # Mock German translation
                return f"[DE] {text}"
            else:
                # Mock translation for other languages
                return f"[{target_language.upper()}] {text}"
                
        except Exception as e:
            logger.error(f"Error auto-translating to {target_language}: {str(e)}")
            return None
    
    async def _get_fallback_translation(self, key: str, language: str) -> Optional[str]:
        """Get translation using fallback language chain"""
        lang_info = self.languages.get(language)
        if lang_info and lang_info.fallback_language != language:
            return await self.get_translation(key, lang_info.fallback_language)
        
        # Try fallback chain
        for fallback_lang in self.fallback_chain:
            if fallback_lang != language:
                translation = await self._load_translation(key, fallback_lang)
                if translation:
                    return translation
        
        return None
    
    def _apply_context(self, translation: str, context: Dict[str, Any]) -> str:
        """
Apply context variables to translation"""
        try:
            # Simple variable substitution
            for key, value in context.items():
                translation = translation.replace(f"{{{key}}}", str(value))
            
            return translation
            
        except Exception as e:
            logger.error(f"Error applying context: {str(e)}")
            return translation
    
    def get_language_info(self, language: str) -> Optional[LanguageInfo]:
        """Get detailed language information"""
        return self.languages.get(language)
    
    def get_supported_languages(self) -> List[LanguageInfo]:
        """
Get list of all supported languages"""
        return [lang for lang in self.languages.values() if lang.enabled]
    
    def get_languages_by_region(self, region: LanguageRegion) -> List[LanguageInfo]:
        """
Get languages by region"""
        return [lang for lang in self.languages.values() 
                if lang.region == region and lang.enabled]
    
    def get_rtl_languages(self) -> List[str]:
        """
Get list of right-to-left languages"""
        return [code for code, lang in self.languages.items() 
                if lang.rtl and lang.enabled]
    
    async def detect_language(self, text: str) -> Optional[str]:
        """
Detect language of given text"""
        try:
            # This would integrate with language detection services
            # For now, return a simple heuristic
            
            # Check for common patterns
            if re.search(r'[א-ת]', text):
                return 'he'
            elif re.search(r'[ا-ي]', text):
                return 'ar'
            elif re.search(r'[а-я]', text):
                return 'ru'
            elif re.search(r'[一-龯]', text):
                return 'zh'
            elif re.search(r'[ひらがな]|[カタカナ]', text):
                return 'ja'
            elif re.search(r'[가-힣]', text):
                return 'ko'
            elif re.search(r'[ⴰ-ⵯ]', text):  # Tifinagh script range
                return 'tzm'  # Default to Central Atlas Tamazight
            else:
                return 'en'  # Default to English
                
        except Exception as e:
            logger.error(f"Error detecting language: {str(e)}")
            return 'en'
    
    async def format_currency(
        self, 
        amount: float, 
        currency: str, 
        language: str
    ) -> str:
        """Format currency according to language conventions"""
        try:
            lang_info = self.languages.get(language)
            if not lang_info:
                lang_info = self.languages[self.default_language]
            
            # Use language-specific currency formatting
            if lang_info.currency_format:
                return lang_info.currency_format.format(
                    amount=f"{amount:.2f}",
                    currency=currency
                )
            else:
                return f"{amount:.2f} {currency}"
                
        except Exception as e:
            logger.error(f"Error formatting currency: {str(e)}")
            return f"{amount:.2f} {currency}"
    
    async def format_date(
        self, 
        date: datetime, 
        language: str
    ) -> str:
        """Format date according to language conventions"""
        try:
            lang_info = self.languages.get(language)
            if not lang_info:
                lang_info = self.languages[self.default_language]
            
            return date.strftime(lang_info.date_format)
            
        except Exception as e:
            logger.error(f"Error formatting date: {str(e)}")
            return date.strftime("%Y-%m-%d")
    
    async def format_number(
        self, 
        number: Union[int, float], 
        language: str
    ) -> str:
        """Format number according to language conventions"""
        try:
            lang_info = self.languages.get(language)
            if not lang_info:
                lang_info = self.languages[self.default_language]
            
            # Basic number formatting (can be enhanced)
            if isinstance(number, float):
                return f"{number:,.2f}"
            else:
                return f"{number:,}"
                
        except Exception as e:
            logger.error(f"Error formatting number: {str(e)}")
            return str(number)
    
    def get_language_statistics(self) -> Dict[str, Any]:
        """Get statistics about language support"""
        total_languages = len(self.languages)
        enabled_languages = len([l for l in self.languages.values() if l.enabled])
        rtl_languages = len([l for l in self.languages.values() if l.rtl])
        auto_translate_languages = len([l for l in self.languages.values() if l.auto_translate])
        
        regions = {}
        scripts = {}
        
        for lang in self.languages.values():
            regions[lang.region.value] = regions.get(lang.region.value, 0) + 1
            scripts[lang.script.value] = scripts.get(lang.script.value, 0) + 1
        
        return {
            "total_languages": total_languages,
            "enabled_languages": enabled_languages,
            "rtl_languages": rtl_languages,
            "auto_translate_languages": auto_translate_languages,
            "languages_by_region": regions,
            "languages_by_script": scripts,
            "coverage_percentage": (total_languages / 644) * 100,  # Updated target: 644 languages including dialects and regional variants
            "amazigh_berber_languages": len([l for l in self.languages.values() if any(code in l.code for code in ['tzm', 'rif', 'shi', 'kab', 'shy', 'mzb', 'thv', 'ttq', 'taq', 'zen'])]),
            "north_african_dialects": len([l for l in self.languages.values() if l.code.startswith(('ar-TN', 'ar-DZ', 'ar-MA', 'ar-LY', 'ar-EG', 'ar-SD', 'ar-MR')) or l.code == 'mey']),
            "tifinagh_script_languages": len([l for l in self.languages.values() if l.script == LanguageScript.TIFINAGH])
        }


# Global i18n manager instance
i18n_manager = InternationalizationManager()