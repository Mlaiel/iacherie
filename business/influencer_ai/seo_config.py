"""🔧 Configuration pour les APIs SEO Ultra-Avancées
================================================
Configuration centralisée pour toutes les intégrations API SEO
Author: Fahed Mlaiel (mlaiel@live.de)
Type: SEO_API_CONFIG
================================================
"""

import os
from typing import Dict, Optional
from dataclasses import dataclass, field

@dataclass
class UltraAdvancedSEOConfig:
    """
Configuration pour les APIs SEO ultra-avancées"""
    
    # Google Ads / Keyword Planner API
    google_ads_api_key: str = ""
    google_ads_developer_token: str = ""
    google_ads_customer_id: str = ""
    google_ads_client_id: str = ""
    google_ads_client_secret: str = ""
    google_ads_refresh_token: str = ""
    
    # SEMrush API
    semrush_api_key: str = ""
    
    # Ahrefs API
    ahrefs_api_key: str = ""
    
    # Configuration générale
    use_real_apis: bool = False
    fallback_to_simulation: bool = True
    
    # Rate limiting
    api_rate_limits: Dict[str, int] = field(default_factory=lambda: {
        'google_ads': 1000,
        'semrush': 120,
        'ahrefs': 500,
        'google_trends': 100
    })
    
    # Timeouts
    api_timeouts: Dict[str, int] = field(default_factory=lambda: {
        'google_ads': 30,
        'semrush': 20,
        'ahrefs': 25,
        'google_trends': 15
    })
    
    def __post_init__(self):
        """Charger les clés API depuis les variables d'environnement"""
        # Google Ads API
        self.google_ads_api_key = self.google_ads_api_key or os.getenv('GOOGLE_ADS_API_KEY', '')
        self.google_ads_developer_token = self.google_ads_developer_token or os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN', '')
        self.google_ads_customer_id = self.google_ads_customer_id or os.getenv('GOOGLE_ADS_CUSTOMER_ID', '')
        self.google_ads_client_id = self.google_ads_client_id or os.getenv('GOOGLE_ADS_CLIENT_ID', '')
        self.google_ads_client_secret = self.google_ads_client_secret or os.getenv('GOOGLE_ADS_CLIENT_SECRET', '')
        self.google_ads_refresh_token = self.google_ads_refresh_token or os.getenv('GOOGLE_ADS_REFRESH_TOKEN', '')
        
        # SEMrush API
        self.semrush_api_key = self.semrush_api_key or os.getenv('SEMRUSH_API_KEY', '')
        
        # Ahrefs API
        self.ahrefs_api_key = self.ahrefs_api_key or os.getenv('AHREFS_API_KEY', '')
        
        # Déterminer si les APIs réelles peuvent être utilisées
        self.use_real_apis = bool(
            self.google_ads_api_key or 
            self.semrush_api_key or 
            self.ahrefs_api_key
        )
    
    def get_api_keys_dict(self) -> Dict[str, str]:
        """
Obtenir les clés API dans un format dict"""
        return {
            'google_ads_api_key': self.google_ads_api_key,
            'google_ads_developer_token': self.google_ads_developer_token,
            'google_ads_customer_id': self.google_ads_customer_id,
            'google_ads_client_id': self.google_ads_client_id,
            'google_ads_client_secret': self.google_ads_client_secret,
            'google_ads_refresh_token': self.google_ads_refresh_token,
            'semrush_api_key': self.semrush_api_key,
            'ahrefs_api_key': self.ahrefs_api_key
        }
    
    def is_api_configured(self, api_name: str) -> bool:
        """
Vérifier si une API spécifique est configurée"""
        api_keys = {
            'google_ads': self.google_ads_api_key,
            'semrush': self.semrush_api_key,
            'ahrefs': self.ahrefs_api_key
        }
        return bool(api_keys.get(api_name, ''))
    
    def get_configured_apis(self) -> List[str]:
        """
Obtenir la liste des APIs configurées"""
        configured = []
        if self.google_ads_api_key:
            configured.append('google_ads')
        if self.semrush_api_key:
            configured.append('semrush')
        if self.ahrefs_api_key:
            configured.append('ahrefs')
        return configured

def load_seo_config() -> UltraAdvancedSEOConfig:
    """
Charger la configuration SEO"""
    return UltraAdvancedSEOConfig()

def validate_api_config(config: UltraAdvancedSEOConfig) -> Dict[str, bool]:
    """
Valider la configuration des APIs"""
    validation_results = {
        'google_ads': bool(config.google_ads_api_key and config.google_ads_developer_token),
        'semrush': bool(config.semrush_api_key),
        'ahrefs': bool(config.ahrefs_api_key),
        'any_configured': config.use_real_apis
    }
    return validation_results

# Configuration globale par défaut
DEFAULT_SEO_CONFIG = UltraAdvancedSEOConfig()