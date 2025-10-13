"""
🛡️ SYSTÈME DE MODÉRATION MULTILINGUE - GUARDIAN
Support de 644+ langues et dialectes
Détection automatique de contenu inapproprié dans toutes les langues
"""

import re
import httpx
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime
from language_support import detect_language, translate_text, TranslationProvider


# ============================================================================
# LISTES DE MOTS INAPPROPRIÉS PAR LANGUE (644+ langues supportées)
# ============================================================================

# Mots inappropriés - Anglais (EN)
PROFANITY_EN = {
    "fuck", "shit", "ass", "bitch", "bastard", "damn", "hell", "crap",
    "dick", "cock", "pussy", "slut", "whore", "fag", "nigger", "cunt",
    "asshole", "motherfucker", "bullshit", "piss", "rape", "kill yourself"
}

# Mots inappropriés - Français (FR)
PROFANITY_FR = {
    "merde", "putain", "connard", "salaud", "enculé", "con", "pute",
    "bordel", "chier", "bite", "couille", "nique", "bâtard", "salope",
    "pd", "tapette", "fils de pute", "va te faire foutre", "trou du cul"
}

# Mots inappropriés - Allemand (DE)
PROFANITY_DE = {
    "scheiße", "scheisse", "arsch", "hurensohn", "fick", "fotze", "sau",
    "schwanz", "wichser", "idiot", "arschloch", "verdammt", "drecksau",
    "miststück", "schwuchtel", "schlampe", "bastard"
}

# Mots inappropriés - Arabe (AR)
PROFANITY_AR = {
    "كس", "خرا", "عرص", "زبي", "منيوك", "شرموط", "قحبة", "ولد الحرام",
    "يا ابن الكلب", "كلب", "حمار", "غبي", "احمق", "معفن", "قذر"
}

# Mots inappropriés - Espagnol (ES)
PROFANITY_ES = {
    "mierda", "coño", "puta", "cabrón", "pendejo", "joder", "chingar",
    "verga", "puto", "hijo de puta", "maricón", "cojones", "culo",
    "gilipollas", "tonto", "idiota", "perra", "zorra"
}

# Mots inappropriés - Italien (IT)
PROFANITY_IT = {
    "cazzo", "merda", "puttana", "stronzo", "fottere", "coglione",
    "fica", "bastardo", "figlio di puttana", "vaffanculo", "porco",
    "idiota", "stupido", "troia", "schifo"
}

# Mots inappropriés - Portugais (PT)
PROFANITY_PT = {
    "merda", "porra", "caralho", "foda", "puta", "filho da puta",
    "cu", "cacete", "buceta", "viado", "bicha", "idiota", "burro",
    "vadia", "desgraçado", "bosta"
}

# Mots inappropriés - Russe (RU)
PROFANITY_RU = {
    "блядь", "сука", "хуй", "пизда", "ебать", "говно", "мудак",
    "дерьмо", "жопа", "ублюдок", "идиот", "дурак", "педик",
    "шлюха", "засранец", "гандон", "чмо"
}

# Mots inappropriés - Chinois (ZH)
PROFANITY_ZH = {
    "操", "他妈的", "傻逼", "混蛋", "妈的", "靠", "艹", "狗娘养的",
    "婊子", "贱人", "王八蛋", "去死", "白痴", "蠢货", "废物"
}

# Mots inappropriés - Japonais (JA)
PROFANITY_JA = {
    "くそ", "ばか", "アホ", "死ね", "殺す", "ちくしょう", "くたばれ",
    "馬鹿野郎", "糞", "畜生", "うるさい", "最低", "クズ", "ゴミ"
}

# Mots inappropriés - Coréen (KO)
PROFANITY_KO = {
    "씨발", "개새끼", "병신", "지랄", "엿먹어", "꺼져", "죽어",
    "미친놈", "쓰레기", "바보", "멍청이", "비겁한", "더러운"
}

# Mots inappropriés - Hindi (HI)
PROFANITY_HI = {
    "बकवास", "गधा", "कमीना", "हरामी", "साला", "बदमाश", "कुत्ता",
    "मूर्ख", "बेवकूफ", "चूतिया", "भोसड़ी", "रंडी", "मादरचोद"
}

# Mots inappropriés - Turc (TR)
PROFANITY_TR = {
    "siktir", "amk", "orospu", "piç", "göt", "bok", "kahpe",
    "salak", "aptal", "gerizekalı", "dangalak", "mal", "puşt"
}

# Mots inappropriés - Polonais (PL)
PROFANITY_PL = {
    "kurwa", "chuj", "dupa", "pierdolić", "gówno", "skurwysyn",
    "suka", "dupek", "idiota", "debil", "kretyn", "śmieć"
}

# Mots inappropriés - Néerlandais (NL)
PROFANITY_NL = {
    "kut", "klootzak", "lul", "hoer", "eikel", "kanker", "tering",
    "tyfus", "shit", "verdomme", "idioot", "sukkel", "rotzak"
}

# Mots inappropriés - Suédois (SV)
PROFANITY_SV = {
    "fan", "skit", "jävel", "hora", "kuk", "fitta", "helvete",
    "idiot", "dumbom", "tönt", "svin", "jävla"
}

# Mots inappropriés - Vietnamien (VI)
PROFANITY_VI = {
    "địt", "đụ", "lồn", "cặc", "đéo", "đĩ", "con chó",
    "ngu", "khốn", "đồ ngốc", "mẹ mày", "con lợn", "đồ khốn"
}

# Mots inappropriés - Thaï (TH)
PROFANITY_TH = {
    "เหี้ย", "ควย", "หี", "เย็ด", "สัส", "ไอ้สัตว์", "ชาติหมา",
    "โง่", "ปัญญาอ่อน", "ไอ้เวร", "เลว", "ขี้", "สารเลว"
}

# Mots inappropriés - Grec (EL)
PROFANITY_EL = {
    "γαμώ", "μαλάκας", "πούστης", "πουτάνα", "σκατά", "χέστηκα",
    "βλάκας", "κωλόπαιδο", "ηλίθιος", "κερατάς", "αρχίδι"
}

# Mots inappropriés - Hébreu (IW)
PROFANITY_HW = {
    "זין", "כוס", "חרא", "לעזאזל", "בן זונה", "מניאק", "שרמוטה",
    "טיפש", "אידיוט", "מפגר", "דפוק", "זבל", "מטומטם"
}


# Dictionnaire global combinant toutes les langues
PROFANITY_BY_LANGUAGE = {
    "EN": PROFANITY_EN,
    "FR": PROFANITY_FR,
    "DE": PROFANITY_DE,
    "AR": PROFANITY_AR,
    "ES": PROFANITY_ES,
    "IT": PROFANITY_IT,
    "PT": PROFANITY_PT,
    "RU": PROFANITY_RU,
    "ZH": PROFANITY_ZH,
    "JA": PROFANITY_JA,
    "KO": PROFANITY_KO,
    "HI": PROFANITY_HI,
    "TR": PROFANITY_TR,
    "PL": PROFANITY_PL,
    "NL": PROFANITY_NL,
    "SV": PROFANITY_SV,
    "VI": PROFANITY_VI,
    "TH": PROFANITY_TH,
    "EL": PROFANITY_EL,
    "IW": PROFANITY_HW,
}


# ============================================================================
# PATTERNS DE DÉTECTION UNIVERSELS
# ============================================================================

# Patterns pour détecter les insultes, menaces, discours de haine
HATE_SPEECH_PATTERNS = [
    r'\b(kill|murder|die|death)\s+(yourself|themselves|all)\b',
    r'\b(hate|fucking hate|despise)\s+(all|every)\s+\w+',
    r'\b(terrorist|terrorism|bomb|attack)\b',
    r'\b(suicide|hang yourself|jump off)\b',
    r'\b(genocide|holocaust|ethnic cleansing)\b',
]

# Patterns pour détecter le spam
SPAM_PATTERNS = [
    r'(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+){3,}',  # 3+ URLs
    r'(\b\w+\b)(\s+\1){4,}',  # Même mot répété 5+ fois
    r'[A-Z]{10,}',  # 10+ majuscules consécutives
    r'(.)\1{10,}',  # 10+ caractères identiques consécutifs
]

# Patterns pour détecter les informations personnelles (PII)
PII_PATTERNS = [
    r'\b\d{3}-\d{2}-\d{4}\b',  # SSN américain
    r'\b\d{16}\b',  # Numéro de carte de crédit
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
    r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # Numéro de téléphone
]


# ============================================================================
# CLASSE PRINCIPALE DE MODÉRATION
# ============================================================================

class MultilingualModerationService:
    """
    Service de modération multilingue avec support de 644+ langues
    """
    
    def __init__(self):
        self.profanity_cache: Dict[str, Set[str]] = {}
        self.blocked_words_count: Dict[str, int] = {}
        
    async def moderate_text(
        self,
        text: str,
        user_language: Optional[str] = None,
        strict_mode: bool = False
    ) -> Dict:
        """
        Modère un texte dans n'importe quelle langue (644+ langues supportées)
        
        Args:
            text: Texte à modérer
            user_language: Langue de l'utilisateur (optionnel, sera détectée automatiquement)
            strict_mode: Mode strict (bloque plus de contenu)
            
        Returns:
            Dict contenant:
            - is_appropriate: bool - Le texte est-il approprié?
            - detected_language: str - Langue détectée
            - violations: List[str] - Liste des violations détectées
            - filtered_text: str - Texte filtré (mots inappropriés masqués)
            - confidence: float - Confiance de la détection (0-1)
        """
        if not text or not text.strip():
            return {
                "is_appropriate": True,
                "detected_language": "unknown",
                "violations": [],
                "filtered_text": text,
                "confidence": 1.0
            }
        
        # Détecter la langue
        detected_lang = user_language or await detect_language(text)
        
        violations = []
        filtered_text = text
        
        # 1. Vérifier les mots inappropriés dans la langue détectée
        profanity_check = await self._check_profanity(text, detected_lang)
        if profanity_check["found"]:
            violations.extend(profanity_check["violations"])
            filtered_text = profanity_check["filtered_text"]
        
        # 2. Si la langue n'est pas dans notre liste principale, traduire vers EN et vérifier
        if detected_lang.upper() not in PROFANITY_BY_LANGUAGE:
            translation_result = await translate_text(text, "EN", detected_lang)
            if translation_result["provider"] != TranslationProvider.NONE:
                en_check = await self._check_profanity(
                    translation_result["translatedText"],
                    "EN"
                )
                if en_check["found"]:
                    violations.extend([f"EN-translation: {v}" for v in en_check["violations"]])
        
        # 3. Vérifier les patterns universels
        pattern_violations = self._check_patterns(text, strict_mode)
        violations.extend(pattern_violations)
        
        # 4. Calculer la confiance
        confidence = self._calculate_confidence(text, detected_lang, violations)
        
        is_appropriate = len(violations) == 0
        
        return {
            "is_appropriate": is_appropriate,
            "detected_language": detected_lang,
            "violations": violations,
            "filtered_text": filtered_text if not is_appropriate else text,
            "confidence": confidence,
            "moderation_timestamp": datetime.utcnow().isoformat()
        }
    
    async def _check_profanity(
        self,
        text: str,
        language: str
    ) -> Dict:
        """
        Vérifie si le texte contient des mots inappropriés dans une langue donnée
        """
        language_upper = language.upper()
        profanity_list = PROFANITY_BY_LANGUAGE.get(language_upper, set())
        
        text_lower = text.lower()
        found_words = []
        filtered_text = text
        
        for word in profanity_list:
            # Recherche avec boundaries pour éviter les faux positifs
            pattern = r'\b' + re.escape(word) + r'\b'
            if re.search(pattern, text_lower, re.IGNORECASE):
                found_words.append(word)
                # Masquer le mot (remplacer par des astérisques)
                replacement = '*' * len(word)
                filtered_text = re.sub(pattern, replacement, filtered_text, flags=re.IGNORECASE)
                
                # Compter pour les stats
                self.blocked_words_count[word] = self.blocked_words_count.get(word, 0) + 1
        
        return {
            "found": len(found_words) > 0,
            "violations": [f"profanity-{language_upper}: {w}" for w in found_words],
            "filtered_text": filtered_text
        }
    
    def _check_patterns(self, text: str, strict_mode: bool) -> List[str]:
        """
        Vérifie les patterns universels (spam, hate speech, PII)
        """
        violations = []
        
        # Vérifier hate speech
        for pattern in HATE_SPEECH_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                violations.append(f"hate-speech: pattern matched")
        
        # Vérifier spam
        for pattern in SPAM_PATTERNS:
            if re.search(pattern, text):
                violations.append(f"spam: pattern matched")
        
        # Vérifier PII (information personnelle)
        if strict_mode:
            for pattern in PII_PATTERNS:
                if re.search(pattern, text):
                    violations.append(f"pii: personal information detected")
        
        return violations
    
    def _calculate_confidence(
        self,
        text: str,
        language: str,
        violations: List[str]
    ) -> float:
        """
        Calcule la confiance de la détection
        """
        # Confiance de base
        confidence = 0.8
        
        # Augmenter si la langue est dans nos listes principales
        if language.upper() in PROFANITY_BY_LANGUAGE:
            confidence += 0.1
        
        # Augmenter si plusieurs violations détectées
        if len(violations) > 2:
            confidence += 0.1
        
        # Diminuer si le texte est très court
        if len(text) < 10:
            confidence -= 0.2
        
        return min(1.0, max(0.0, confidence))
    
    async def moderate_file_content(
        self,
        file_content: bytes,
        filename: str,
        content_type: str
    ) -> Dict:
        """
        Modère le contenu d'un fichier (texte, image, vidéo)
        """
        violations = []
        
        # Vérifier l'extension
        extension = filename.lower().split('.')[-1]
        
        # Extensions interdites
        forbidden_extensions = {
            'exe', 'bat', 'cmd', 'sh', 'ps1', 'dll', 'sys',
            'scr', 'vbs', 'jar', 'app', 'msi', 'deb', 'rpm'
        }
        
        if extension in forbidden_extensions:
            violations.append(f"forbidden-extension: {extension}")
        
        # Vérifier la taille (max 100MB)
        max_size = 100 * 1024 * 1024  # 100MB
        if len(file_content) > max_size:
            violations.append(f"file-too-large: {len(file_content)} bytes")
        
        # Si c'est un fichier texte, modérer le contenu
        text_extensions = {'txt', 'md', 'json', 'xml', 'csv', 'log'}
        if extension in text_extensions:
            try:
                text_content = file_content.decode('utf-8')
                text_moderation = await self.moderate_text(text_content)
                if not text_moderation["is_appropriate"]:
                    violations.extend(text_moderation["violations"])
            except UnicodeDecodeError:
                violations.append("invalid-encoding")
        
        return {
            "is_appropriate": len(violations) == 0,
            "violations": violations,
            "file_info": {
                "filename": filename,
                "extension": extension,
                "size": len(file_content),
                "content_type": content_type
            }
        }
    
    def get_statistics(self) -> Dict:
        """
        Retourne les statistiques de modération
        """
        return {
            "total_languages_supported": 644,
            "active_profanity_lists": len(PROFANITY_BY_LANGUAGE),
            "total_blocked_words": sum(self.blocked_words_count.values()),
            "most_blocked_words": sorted(
                self.blocked_words_count.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }


# Instance globale
moderation_service = MultilingualModerationService()


# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

async def moderate_text_simple(text: str, language: Optional[str] = None) -> bool:
    """
    Fonction simple pour vérifier si un texte est approprié
    
    Args:
        text: Texte à vérifier
        language: Langue (optionnel)
        
    Returns:
        True si approprié, False sinon
    """
    result = await moderation_service.moderate_text(text, language)
    return result["is_appropriate"]


async def filter_text(text: str, language: Optional[str] = None) -> str:
    """
    Filtre un texte en masquant les mots inappropriés
    
    Args:
        text: Texte à filtrer
        language: Langue (optionnel)
        
    Returns:
        Texte filtré
    """
    result = await moderation_service.moderate_text(text, language)
    return result["filtered_text"]


def add_custom_profanity_words(language: str, words: Set[str]):
    """
    Ajoute des mots personnalisés à la liste de modération d'une langue
    
    Args:
        language: Code de la langue (ex: "EN", "FR")
        words: Ensemble de mots à ajouter
    """
    language_upper = language.upper()
    if language_upper not in PROFANITY_BY_LANGUAGE:
        PROFANITY_BY_LANGUAGE[language_upper] = set()
    
    PROFANITY_BY_LANGUAGE[language_upper].update(words)


def get_supported_moderation_languages() -> List[str]:
    """
    Retourne la liste des langues avec listes de modération actives
    
    Returns:
        Liste des codes de langues
    """
    return list(PROFANITY_BY_LANGUAGE.keys())
