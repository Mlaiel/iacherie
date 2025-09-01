"""IA Influencer Agent - License Template Manager
===========================================

Gestionnaire de modèles de licences pour différents types de contenu et cas d'usage.
Fournit des templates personnalisables pour tous les formats supportés.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: 2024-2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LEGAL STRICT ⚠️
Ce code et tous les concepts associés sont la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation écrite explicite est strictement interdite.
Les contrevenants s'exposent à des poursuites judiciaires.

Contact autorisé: mlaiel@live.de
"""
from typing import Dict, Any, List, Optional
import json
import logging
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class LicenseType(Enum):
    """Types de licences disponibles."""
    CREATIVE_COMMONS = "creative_commons"
    COMMERCIAL = "commercial"
    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    ROYALTY_FREE = "royalty_free"
    SUBSCRIPTION = "subscription"
    PAY_PER_USE = "pay_per_use"
    COLLABORATION = "collaboration"
    EDUCATIONAL = "educational"
    EDITORIAL = "editorial"


class ContentFormat(Enum):
    """Formats de contenu supportés."""
    MUSIC = "music"
    VIDEO = "video"
    PHOTO = "photo"
    BLOG_ARTICLE = "blog_article"
    PODCAST = "podcast"
    LIVESTREAM = "livestream"
    STORY = "story"
    REEL = "reel"
    COURSE = "course"
    TUTORIAL = "tutorial"


class UsageScope(Enum):
    """Portées d'utilisation."""
    PERSONAL = "personal"
    COMMERCIAL = "commercial"
    BROADCAST = "broadcast"
    DIGITAL = "digital"
    PRINT = "print"
    SOCIAL_MEDIA = "social_media"
    ADVERTISING = "advertising"
    MERCHANDISING = "merchandising"


class LicenseTemplateManager:
    """
    Gestionnaire de modèles de licences avancé pour l'IA Influencer Agent.
    
    Fournit des templates personnalisables et optimisés pour tous les types
    de contenu et cas d'usage business.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialise le gestionnaire de templates.
        
        Args:
            config: Configuration du gestionnaire
        """
        self.config = config or {}
        self.templates = {}
        self.custom_templates = {}
        self.is_initialized = False
        
        logger.info("LicenseTemplateManager initialized")
    
    async def initialize(self):
        """Initialise les templates par défaut."""
        try:
            await self._load_default_templates()
            await self._load_custom_templates()
            self.is_initialized = True
            logger.info("License templates successfully loaded")
        except Exception as e:
            logger.error(f"Failed to initialize templates: {str(e)}")
            raise
    
    async def _load_default_templates(self):
        """Charge les templates par défaut."""
        self.templates = {
            # Templates pour contenu musical
            "music_commercial": {
                "name": "Commercial Music License",
                "content_format": ContentFormat.MUSIC.value,
                "license_type": LicenseType.COMMERCIAL.value,
                "terms": {
                    "usage_scope": [UsageScope.COMMERCIAL.value, UsageScope.BROADCAST.value],
                    "duration": "perpetual",
                    "territory": "worldwide",
                    "exclusivity": False,
                    "royalty_rate": 0.15,
                    "minimum_fee": 100.0,
                    "attribution_required": True,
                    "modifications_allowed": False,
                    "resale_allowed": False,
                    "sync_rights": True,
                    "master_rights": False
                },
                "restrictions": {
                    "adult_content": False,
                    "political_use": False,
                    "competing_brands": True,
                    "max_duration": None,
                    "quality_requirements": "minimum 320kbps"
                },
                "pricing": {
                    "base_price": 100.0,
                    "territory_multiplier": {"worldwide": 1.5, "regional": 1.0, "local": 0.7},
                    "duration_multiplier": {"1_year": 1.0, "2_years": 1.8, "perpetual": 3.0},
                    "usage_multiplier": {"commercial": 2.0, "broadcast": 3.0, "social_media": 1.0}
                }
            },
            
            "music_creative_commons": {
                "name": "Creative Commons Music License",
                "content_format": ContentFormat.MUSIC.value,
                "license_type": LicenseType.CREATIVE_COMMONS.value,
                "terms": {
                    "usage_scope": [UsageScope.PERSONAL.value, UsageScope.EDUCATIONAL.value],
                    "duration": "perpetual",
                    "territory": "worldwide",
                    "exclusivity": False,
                    "royalty_rate": 0.0,
                    "minimum_fee": 0.0,
                    "attribution_required": True,
                    "modifications_allowed": True,
                    "resale_allowed": False,
                    "sync_rights": True,
                    "master_rights": False
                },
                "restrictions": {
                    "adult_content": False,
                    "political_use": True,
                    "competing_brands": False,
                    "max_duration": None,
                    "quality_requirements": "any"
                },
                "pricing": {
                    "base_price": 0.0,
                    "territory_multiplier": {"worldwide": 1.0},
                    "duration_multiplier": {"perpetual": 1.0},
                    "usage_multiplier": {"personal": 1.0, "educational": 1.0}
                }
            },
            
            # Templates pour contenu vidéo
            "video_exclusive": {
                "name": "Exclusive Video License",
                "content_format": ContentFormat.VIDEO.value,
                "license_type": LicenseType.EXCLUSIVE.value,
                "terms": {
                    "usage_scope": [UsageScope.COMMERCIAL.value, UsageScope.BROADCAST.value, 
                                  UsageScope.DIGITAL.value],
                    "duration": "2_years",
                    "territory": "regional",
                    "exclusivity": True,
                    "royalty_rate": 0.25,
                    "minimum_fee": 500.0,
                    "attribution_required": True,
                    "modifications_allowed": True,
                    "resale_allowed": False,
                    "distribution_rights": True,
                    "derivative_works": True
                },
                "restrictions": {
                    "adult_content": False,
                    "political_use": False,
                    "competing_brands": True,
                    "max_duration": "unlimited",
                    "quality_requirements": "minimum 1080p"
                },
                "pricing": {
                    "base_price": 500.0,
                    "exclusivity_multiplier": 3.0,
                    "territory_multiplier": {"worldwide": 2.0, "regional": 1.0},
                    "duration_multiplier": {"1_year": 1.0, "2_years": 1.8},
                    "usage_multiplier": {"commercial": 2.0, "broadcast": 3.0}
                }
            },
            
            # Templates pour contenu photo
            "photo_subscription": {
                "name": "Photo Subscription License",
                "content_format": ContentFormat.PHOTO.value,
                "license_type": LicenseType.SUBSCRIPTION.value,
                "terms": {
                    "usage_scope": [UsageScope.COMMERCIAL.value, UsageScope.DIGITAL.value,
                                  UsageScope.SOCIAL_MEDIA.value],
                    "duration": "1_year",
                    "territory": "worldwide",
                    "exclusivity": False,
                    "royalty_rate": 0.0,
                    "subscription_fee": 99.0,
                    "download_limit": 100,
                    "attribution_required": False,
                    "modifications_allowed": True,
                    "resale_allowed": False,
                    "print_rights": True,
                    "web_rights": True
                },
                "restrictions": {
                    "adult_content": False,
                    "political_use": True,
                    "competing_brands": False,
                    "max_resolution": "unlimited",
                    "quality_requirements": "minimum 300dpi for print"
                },
                "pricing": {
                    "monthly_fee": 29.0,
                    "yearly_fee": 99.0,
                    "download_price": 0.0,
                    "extended_license_fee": 50.0
                }
            },
            
            # Templates pour contenu blog
            "blog_collaboration": {
                "name": "Blog Collaboration License",
                "content_format": ContentFormat.BLOG_ARTICLE.value,
                "license_type": LicenseType.COLLABORATION.value,
                "terms": {
                    "usage_scope": [UsageScope.DIGITAL.value, UsageScope.SOCIAL_MEDIA.value],
                    "duration": "6_months",
                    "territory": "worldwide",
                    "exclusivity": False,
                    "revenue_share": 0.30,
                    "attribution_required": True,
                    "modifications_allowed": True,
                    "translation_allowed": True,
                    "syndication_allowed": True,
                    "archive_rights": True
                },
                "restrictions": {
                    "adult_content": False,
                    "political_use": True,
                    "competing_brands": True,
                    "word_count_minimum": 500,
                    "quality_requirements": "professional editorial standards"
                },
                "revenue_model": {
                    "creator_share": 0.70,
                    "platform_share": 0.30,
                    "minimum_payout": 25.0,
                    "payment_frequency": "monthly"
                }
            }
        }
    
    async def _load_custom_templates(self):
        """Charge les templates personnalisés."""
        # Ici on pourrait charger depuis une base de données
        self.custom_templates = {}
    
    async def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère un template de licence.
        
        Args:
            template_id: ID du template
            
        Returns:
            Dict contenant le template ou None
        """
        if not self.is_initialized:
            await self.initialize()
        
        template = self.templates.get(template_id) or self.custom_templates.get(template_id)
        if template:
            logger.info(f"Template {template_id} retrieved successfully")
        else:
            logger.warning(f"Template {template_id} not found")
        
        return template
    
    async def create_custom_template(self, template_id: str, template_data: Dict[str, Any]) -> bool:
        """
        Crée un template personnalisé.
        
        Args:
            template_id: ID du nouveau template
            template_data: Données du template
            
        Returns:
            bool: True si création réussie
        """
        try:
            # Validation du template
            if not await self._validate_template(template_data):
                return False
            
            self.custom_templates[template_id] = {
                **template_data,
                "created_at": datetime.utcnow().isoformat(),
                "custom": True
            }
            
            logger.info(f"Custom template {template_id} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create custom template {template_id}: {str(e)}")
            return False
    
    async def _validate_template(self, template_data: Dict[str, Any]) -> bool:
        """
        Valide la structure d'un template.
        
        Args:
            template_data: Données du template à valider
            
        Returns:
            bool: True si valide
        """
        required_fields = ["name", "content_format", "license_type", "terms"]
        
        for field in required_fields:
            if field not in template_data:
                logger.error(f"Missing required field: {field}")
                return False
        
        # Validation des termes
        terms = template_data.get("terms", {})
        required_terms = ["usage_scope", "duration", "territory"]
        
        for term in required_terms:
            if term not in terms:
                logger.error(f"Missing required term: {term}")
                return False
        
        return True
    
    async def get_templates_for_content(self, content_format: str, 
                                      usage_type: str = None) -> List[Dict[str, Any]]:
        """
        Récupère les templates appropriés pour un type de contenu.
        
        Args:
            content_format: Format du contenu
            usage_type: Type d'usage (optionnel)
            
        Returns:
            Liste des templates appropriés
        """
        if not self.is_initialized:
            await self.initialize()
        
        matching_templates = []
        
        all_templates = {**self.templates, **self.custom_templates}
        
        for template_id, template in all_templates.items():
            if template.get("content_format") == content_format:
                if not usage_type or usage_type in template.get("terms", {}).get("usage_scope", []):
                    matching_templates.append({
                        "id": template_id,
                        **template
                    })
        
        logger.info(f"Found {len(matching_templates)} templates for {content_format}")
        return matching_templates
    
    async def calculate_pricing(self, template_id: str, 
                              customizations: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Calcule le prix basé sur un template et des personnalisations.
        
        Args:
            template_id: ID du template
            customizations: Personnalisations du prix
            
        Returns:
            Dict contenant les détails du pricing
        """
        template = await self.get_template(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        pricing_config = template.get("pricing", {})
        base_price = pricing_config.get("base_price", 0.0)
        
        # Application des multiplicateurs
        territory = customizations.get("territory", "local") if customizations else "local"
        duration = customizations.get("duration", "1_year") if customizations else "1_year"
        usage = customizations.get("usage_type", "personal") if customizations else "personal"
        
        territory_multiplier = pricing_config.get("territory_multiplier", {}).get(territory, 1.0)
        duration_multiplier = pricing_config.get("duration_multiplier", {}).get(duration, 1.0)
        usage_multiplier = pricing_config.get("usage_multiplier", {}).get(usage, 1.0)
        
        # Calcul du prix final
        final_price = base_price * territory_multiplier * duration_multiplier * usage_multiplier
        
        # Ajout des frais spéciaux
        if template.get("license_type") == LicenseType.EXCLUSIVE.value:
            exclusivity_multiplier = pricing_config.get("exclusivity_multiplier", 1.0)
            final_price *= exclusivity_multiplier
        
        return {
            "base_price": base_price,
            "territory_multiplier": territory_multiplier,
            "duration_multiplier": duration_multiplier,
            "usage_multiplier": usage_multiplier,
            "final_price": round(final_price, 2),
            "currency": "USD",
            "calculation_date": datetime.utcnow().isoformat()
        }
    
    async def generate_license_from_template(self, template_id: str,
                                           content_id: str,
                                           creator_id: str,
                                           licensee_id: str,
                                           customizations: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Génère une licence complète basée sur un template.
        
        Args:
            template_id: ID du template
            content_id: ID du contenu
            creator_id: ID du créateur
            licensee_id: ID du licencié
            customizations: Personnalisations
            
        Returns:
            Dict contenant la licence générée
        """
        template = await self.get_template(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        # Calcul du pricing
        pricing = await self.calculate_pricing(template_id, customizations)
        
        # Fusion des termes avec les personnalisations
        terms = template["terms"].copy()
        if customizations:
            terms.update(customizations.get("terms", {}))
        
        # Génération de la licence
        license_data = {
            "license_id": f"LIC-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{content_id[:8]}",
            "template_id": template_id,
            "template_name": template["name"],
            "content_id": content_id,
            "creator_id": creator_id,
            "licensee_id": licensee_id,
            "license_type": template["license_type"],
            "content_format": template["content_format"],
            "terms": terms,
            "restrictions": template.get("restrictions", {}),
            "pricing": pricing,
            "status": "draft",
            "created_at": datetime.utcnow().isoformat(),
            "valid_from": datetime.utcnow().isoformat(),
            "expires_at": self._calculate_expiry_date(terms.get("duration", "1_year")).isoformat()
        }
        
        logger.info(f"License generated from template {template_id} for content {content_id}")
        return license_data
    
    def _calculate_expiry_date(self, duration: str) -> datetime:
        """
        Calcule la date d'expiration basée sur la durée.
        
        Args:
            duration: Durée de la licence
            
        Returns:
            datetime: Date d'expiration
        """
        now = datetime.utcnow()
        
        duration_mapping = {
            "1_month": timedelta(days=30),
            "3_months": timedelta(days=90),
            "6_months": timedelta(days=180),
            "1_year": timedelta(days=365),
            "2_years": timedelta(days=730),
            "3_years": timedelta(days=1095),
            "5_years": timedelta(days=1825),
            "perpetual": timedelta(days=36500)  # 100 ans
        }
        
        delta = duration_mapping.get(duration, timedelta(days=365))
        return now + delta
    
    async def get_recommended_templates(self, content_id: str,
                                      creator_preferences: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Recommande des templates basés sur le contenu et les préférences.
        
        Args:
            content_id: ID du contenu
            creator_preferences: Préférences du créateur
            
        Returns:
            Liste des templates recommandés
        """
        # Ici on intégrerait l'IA pour analyser le contenu et recommander
        # Pour l'instant, retournons quelques templates populaires
        
        recommended = []
        
        # Logique de recommandation basique
        if creator_preferences:
            preferred_type = creator_preferences.get("license_type")
            content_format = creator_preferences.get("content_format")
            
            if preferred_type and content_format:
                templates = await self.get_templates_for_content(content_format)
                for template in templates:
                    if template.get("license_type") == preferred_type:
                        recommended.append(template)
        
        # Si pas de recommandations spécifiques, retourner les plus populaires
        if not recommended:
            popular_templates = ["music_commercial", "video_exclusive", "photo_subscription"]
            for template_id in popular_templates:
                template = await self.get_template(template_id)
                if template:
                    recommended.append({"id": template_id, **template})
        
        logger.info(f"Recommended {len(recommended)} templates for content {content_id}")
        return recommended
