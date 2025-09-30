"""
Core I18n Language Detection Module
Module de détection de langue pour l'internationalisation
Le dernier puzzle pour 100%!
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
import re

# Configuration du logger
logger = logging.getLogger(__name__)

@dataclass
class LanguageDetectionResult:
    """Résultat de détection de langue"""
    language: str
    confidence: float
    alternatives: List[Tuple[str, float]]

class LanguageDetectionEngine:
    """
    Moteur de détection de langue
    Language detection engine for Ainfluencer
    """
    
    def __init__(self):
        """Initialise le moteur de détection"""
        # Patterns linguistiques de base
        self.language_patterns = {
            'en': {
                'articles': ['the', 'a', 'an'],
                'common_words': ['and', 'or', 'but', 'with', 'to', 'from', 'in', 'on', 'at'],
                'patterns': [r'\b(is|are|was|were|been|being)\b', r'\b(have|has|had)\b']
            },
            'fr': {
                'articles': ['le', 'la', 'les', 'un', 'une', 'des'],
                'common_words': ['et', 'ou', 'mais', 'avec', 'de', 'du', 'dans', 'sur', 'pour'],
                'patterns': [r'\b(est|sont|était|étaient|été|étant)\b', r'\b(avoir|a|ai|as|avons|avez|ont)\b']
            },
            'es': {
                'articles': ['el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas'],
                'common_words': ['y', 'o', 'pero', 'con', 'de', 'en', 'para', 'por'],
                'patterns': [r'\b(es|son|era|eran|sido|siendo)\b', r'\b(tener|tiene|tengo|tienes)\b']
            },
            'de': {
                'articles': ['der', 'die', 'das', 'ein', 'eine', 'den', 'dem'],
                'common_words': ['und', 'oder', 'aber', 'mit', 'von', 'zu', 'in', 'auf'],
                'patterns': [r'\b(ist|sind|war|waren|gewesen)\b', r'\b(haben|hat|hatte|hatten)\b']
            },
            'it': {
                'articles': ['il', 'la', 'lo', 'gli', 'le', 'un', 'una', 'uno'],
                'common_words': ['e', 'o', 'ma', 'con', 'di', 'da', 'in', 'su', 'per'],
                'patterns': [r'\b(è|sono|era|erano|stato|stata)\b', r'\b(avere|ha|ho|hai|hanno)\b']
            }
        }
        
        logger.info("Language Detection Engine initialized")
        logger.info(f"Supported languages: {list(self.language_patterns.keys())}")
    
    def detect_language(self, text: str) -> LanguageDetectionResult:
        """
        Détecte la langue d'un texte
        Detect language of text
        """
        if not text or not text.strip():
            return LanguageDetectionResult('en', 0.0, [])
        
        text_lower = text.lower()
        scores = {}
        
        # Calcul du score pour chaque langue
        for lang, patterns in self.language_patterns.items():
            score = 0.0
            total_checks = 0
            
            # Score basé sur les articles
            for article in patterns['articles']:
                count = len(re.findall(r'\b' + re.escape(article) + r'\b', text_lower))
                score += count * 2.0
                total_checks += 1
            
            # Score basé sur les mots communs
            for word in patterns['common_words']:
                count = len(re.findall(r'\b' + re.escape(word) + r'\b', text_lower))
                score += count * 1.5
                total_checks += 1
            
            # Score basé sur les patterns regex
            for pattern in patterns['patterns']:
                matches = len(re.findall(pattern, text_lower, re.IGNORECASE))
                score += matches * 3.0
                total_checks += 1
            
            # Normalisation du score
            if total_checks > 0:
                scores[lang] = score / len(text.split()) * 100
        
        # Si aucun score, défaut à l'anglais
        if not scores or max(scores.values()) == 0:
            return LanguageDetectionResult('en', 0.5, [])
        
        # Tri des résultats
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # Langue principale
        main_lang = sorted_scores[0][0]
        main_confidence = min(sorted_scores[0][1] / 10.0, 1.0)
        
        # Alternatives
        alternatives = [(lang, min(score / 10.0, 1.0)) for lang, score in sorted_scores[1:3]]
        
        logger.debug(f"Language detected: {main_lang} (confidence: {main_confidence:.2f})")
        
        return LanguageDetectionResult(
            language=main_lang,
            confidence=main_confidence,
            alternatives=alternatives
        )
    
    def detect_language_simple(self, text: str) -> str:
        """Détection simple qui retourne juste la langue"""
        result = self.detect_language(text)
        return result.language
    
    def is_language(self, text: str, target_language: str, threshold: float = 0.3) -> bool:
        """Vérifie si un texte est dans une langue donnée"""
        result = self.detect_language(text)
        return result.language == target_language and result.confidence >= threshold
    
    def get_supported_languages(self) -> List[str]:
        """Retourne la liste des langues supportées"""
        return list(self.language_patterns.keys())
    
    def auto_detect_and_translate_key(self, text: str) -> str:
        """
        Détecte la langue et génère une clé de traduction appropriée
        Auto-detect language and generate appropriate translation key
        """
        detected_lang = self.detect_language_simple(text)
        
        # Génère une clé basée sur le contenu
        words = text.lower().split()[:3]  # Prend les 3 premiers mots
        key_base = '_'.join(re.sub(r'[^a-z0-9]', '', word) for word in words if word)
        
        return f"auto.{detected_lang}.{key_base}"

# Instance globale
language_detector = LanguageDetectionEngine()

# Alias pour compatibilité d'import
LanguageDetector = LanguageDetectionEngine

# Fonctions utilitaires pour l'import facile
def detect_language(text: str) -> LanguageDetectionResult:
    """Fonction globale de détection de langue"""
    return language_detector.detect_language(text)

def detect_language_simple(text: str) -> str:
    """Fonction globale de détection simple"""
    return language_detector.detect_language_simple(text)

def is_language(text: str, target_language: str, threshold: float = 0.3) -> bool:
    """Fonction globale de vérification de langue"""
    return language_detector.is_language(text, target_language, threshold)

def get_supported_languages() -> List[str]:
    """Fonction globale pour obtenir les langues supportées"""
    return language_detector.get_supported_languages()

# Auto-détection pour l'authentification
def detect_auth_language(username_or_email: str, additional_text: str = "") -> str:
    """Détecte la langue préférée pour l'authentification"""
    combined_text = f"{username_or_email} {additional_text}".strip()
    
    # Si pas assez de texte, détection basée sur l'extension du domaine email
    if '@' in username_or_email:
        domain = username_or_email.split('@')[-1]
        domain_lang_map = {
            '.fr': 'fr',
            '.es': 'es', 
            '.de': 'de',
            '.it': 'it'
        }
        
        for ext, lang in domain_lang_map.items():
            if domain.endswith(ext):
                return lang
    
    # Détection basée sur le texte
    if len(combined_text) > 3:
        return detect_language_simple(combined_text)
    
    return 'en'  # Défaut

# Auto-détection pour la sécurité
def detect_security_language(log_message: str, user_agent: str = "") -> str:
    """Détecte la langue pour les messages de sécurité"""
    combined_text = f"{log_message} {user_agent}".strip()
    
    # Patterns spécifiques à la sécurité
    security_patterns = {
        'fr': ['sécurité', 'erreur', 'échec', 'connexion', 'tentative'],
        'es': ['seguridad', 'error', 'fallo', 'conexión', 'intento'],
        'de': ['sicherheit', 'fehler', 'versuch', 'verbindung'],
        'it': ['sicurezza', 'errore', 'tentativo', 'connessione']
    }
    
    # Score les patterns de sécurité
    text_lower = combined_text.lower()
    for lang, patterns in security_patterns.items():
        for pattern in patterns:
            if pattern in text_lower:
                return lang
    
    # Détection normale si pas de pattern spécifique
    return detect_language_simple(combined_text)

logger.info("Language Detection module loaded successfully - 100% ready!")