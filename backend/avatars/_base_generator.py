"""Base Content Generator

Classe de base pour les générateurs de contenu avatar.
Remplace temporairement la dépendance ai_engine manquante.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ContentGenerationContext:
    """Contexte de génération de contenu"""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    platform: str = "web"
    quality_level: str = "standard"
    custom_parameters: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.custom_parameters is None:
            self.custom_parameters = {}


class BaseContentGenerator:
    """Classe de base pour tous les générateurs de contenu"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.generator_type = "base"
        self.version = "1.0.0"
        self.initialized = False
    
    async def initialize(self) -> bool:
        """Initialisation du générateur"""
        self.initialized = True
        return True
    
    async def generate(self, context: ContentGenerationContext) -> Dict[str, Any]:
        """Méthode de génération principale (à surcharger)"""
        if not self.initialized:
            await self.initialize()
        
        return {
            'success': True,
            'generated_at': datetime.now().isoformat(),
            'generator_type': self.generator_type,
            'context': context.__dict__
        }
    
    def _supports_content_type(self, content_type: str) -> bool:
        """Vérifier si ce générateur supporte le type de contenu"""
        return True
    
    def get_supported_formats(self) -> list:
        """Formats supportés par ce générateur"""
        return ['json', 'dict']