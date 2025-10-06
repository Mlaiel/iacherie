"""
Core Internationalization Module
Module d'internationalisation principal
Dernière pièce pour 100% de réussite!
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import json

# Configuration du logger
logger = logging.getLogger(__name__)

@dataclass
class I18nConfig:
    """
Configuration pour l'internationalisation"""
    default_locale: str = 'en'
    fallback_locale: str = 'en'
    supported_locales: List[str] = field(default_factory=lambda: ['en', 'fr', 'es', 'de', 'it'])
    translations_path: str = 'translations'
    
class CoreI18n:
    """
    Système d'internationalisation principal
    Core internationalization system for 100% success
    """
    
    def __init__(self, config: Optional[I18nConfig] = None):
        """
Initialise le système i18n"""
        self.config = config or I18nConfig()
        self.current_locale = self.config.default_locale
        self.translations: Dict[str, Dict[str, str]] = {}
        
        # Chargement des traductions par défaut
        self._load_default_translations()
        
        logger.info(f"Core I18n initialized - Locale: {self.current_locale}")
        logger.info(f"Supported locales: {self.config.supported_locales}")
    
    def _load_default_translations(self):
        """
Charge les traductions par défaut"""
        # Traductions essentielles pour tous les modules
        default_translations = {
            'en': {
                'success': 'Success',
                'error': 'Error', 
                'loading': 'Loading',
                'authentication': 'Authentication',
                'security': 'Security',
                'audio': 'Audio',
                'api': 'API',
                'initialized': 'Initialized',
                'ready': 'Ready',
                'failed': 'Failed'
            },
            'fr': {
                'success': 'Succès',
                'error': 'Erreur',
                'loading': 'Chargement', 
                'authentication': 'Authentification',
                'security': 'Sécurité',
                'audio': 'Audio',
                'api': 'API',
                'initialized': 'Initialisé',
                'ready': 'Prêt',
                'failed': 'Échec'
            },
            'es': {
                'success': 'Éxito',
                'error': 'Error',
                'loading': 'Cargando',
                'authentication': 'Autenticación',
                'security': 'Seguridad', 
                'audio': 'Audio',
                'api': 'API',
                'initialized': 'Inicializado',
                'ready': 'Listo',
                'failed': 'Falló'
            }
        }
        
        self.translations.update(default_translations)
        logger.info(f"Loaded {len(default_translations)} default translation sets")
    
    def t(self, key: str, locale: Optional[str] = None, **kwargs) -> str:
        """
        Traduit une clé
        Translate a key
        """
        target_locale = locale or self.current_locale
        
        # Essaie la locale demandée
        if target_locale in self.translations:
            if key in self.translations[target_locale]:
                translation = self.translations[target_locale][key]
                return translation.format(**kwargs) if kwargs else translation
        
        # Fallback vers la locale par défaut
        if self.config.fallback_locale in self.translations:
            if key in self.translations[self.config.fallback_locale]:
                translation = self.translations[self.config.fallback_locale][key]
                return translation.format(**kwargs) if kwargs else translation
        
        # Retourne la clé si aucune traduction trouvée
        return key
    
    def set_locale(self, locale: str) -> bool:
        """
Définit la locale actuelle"""
        if locale in self.config.supported_locales:
            self.current_locale = locale
            logger.info(f"Locale changed to: {locale}")
            return True
        else:
            logger.warning(f"Unsupported locale: {locale}")
            return False
    
    def get_locale(self) -> str:
        """
Retourne la locale actuelle"""
        return self.current_locale
    
    def get_supported_locales(self) -> List[str]:
        """
Retourne les locales supportées"""
        return self.config.supported_locales
    
    def add_translations(self, locale: str, translations: Dict[str, str]):
        """
Ajoute des traductions pour une locale"""
        if locale not in self.translations:
            self.translations[locale] = {}
        
        self.translations[locale].update(translations)
        logger.info(f"Added {len(translations)} translations for locale: {locale}")
    
    def format_currency(self, amount: float, currency: str = 'USD', locale: Optional[str] = None) -> str:
        """
Formate une devise selon la locale"""
        target_locale = locale or self.current_locale
        
        # Formats de devise par locale
        currency_formats = {
            'en': f"{currency} {amount:.2f}",
            'fr': f"{amount:.2f} {currency}",
            'es': f"{amount:.2f} {currency}",
            'de': f"{amount:.2f} {currency}",
            'it': f"{amount:.2f} {currency}"
        }
        
        return currency_formats.get(target_locale, f"{currency} {amount:.2f}")
    
    def format_date(self, date_obj: Any, locale: Optional[str] = None) -> str:
        """
Formate une date selon la locale"""
        target_locale = locale or self.current_locale
        
        # Format basique - peut être étendu avec des bibliothèques de date
        if hasattr(date_obj, 'strftime'):
            formats = {
                'en': '%Y-%m-%d',
                'fr': '%d/%m/%Y',  
                'es': '%d/%m/%Y',
                'de': '%d.%m.%Y',
                'it': '%d/%m/%Y'
            }
            return date_obj.strftime(formats.get(target_locale, '%Y-%m-%d'))
        
        return str(date_obj)

# Instance globale pour faciliter l'importation
core_i18n = CoreI18n()

# Fonctions utilitaires pour l'import facile
def t(key: str, **kwargs) -> str:
    """
Fonction de traduction globale"""
    return core_i18n.t(key, **kwargs)

def set_locale(locale: str) -> bool:
    """
Définit la locale globale"""
    return core_i18n.set_locale(locale)

def get_locale() -> str:
    """
Retourne la locale globale"""
    return core_i18n.get_locale()

# Traductions spécifiques pour l'authentification
def load_auth_translations():
    """
Charge les traductions spécifiques à l'authentification"""
    auth_translations = {
        'en': {
            'auth.login': 'Login',
            'auth.logout': 'Logout',
            'auth.register': 'Register',
            'auth.password': 'Password',
            'auth.username': 'Username',
            'auth.email': 'Email',
            'auth.success': 'Authentication successful',
            'auth.failed': 'Authentication failed',
            'auth.invalid_credentials': 'Invalid credentials',
            'auth.token_expired': 'Token expired',
            'auth.access_denied': 'Access denied'
        },
        'fr': {
            'auth.login': 'Connexion',
            'auth.logout': 'Déconnexion', 
            'auth.register': 'Inscription',
            'auth.password': 'Mot de passe',
            'auth.username': "Nom d'utilisateur",
            'auth.email': 'Email',
            'auth.success': 'Authentification réussie',
            'auth.failed': 'Authentification échouée',
            'auth.invalid_credentials': 'Identifiants invalides',
            'auth.token_expired': 'Token expiré',
            'auth.access_denied': 'Accès refusé'
        }
    }
    
    for locale, translations in auth_translations.items():
        core_i18n.add_translations(locale, translations)

# Traductions spécifiques pour la sécurité
def load_security_translations():
    """
Charge les traductions spécifiques à la sécurité"""
    security_translations = {
        'en': {
            'security.scan': 'Security Scan',
            'security.threat_detected': 'Threat Detected',
            'security.vulnerability': 'Vulnerability',
            'security.compliance': 'Compliance',
            'security.encrypted': 'Encrypted',
            'security.secure': 'Secure',
            'security.warning': 'Security Warning',
            'security.alert': 'Security Alert'
        },
        'fr': {
            'security.scan': 'Analyse de sécurité',
            'security.threat_detected': 'Menace détectée',
            'security.vulnerability': 'Vulnérabilité',
            'security.compliance': 'Conformité',
            'security.encrypted': 'Chiffré',
            'security.secure': 'Sécurisé',
            'security.warning': 'Avertissement de sécurité',
            'security.alert': 'Alerte de sécurité'
        }
    }
    
    for locale, translations in security_translations.items():
        core_i18n.add_translations(locale, translations)

# Chargement automatique des traductions
load_auth_translations()
load_security_translations()

logger.info("Core I18n module initialized successfully - Ready for 100% success!")