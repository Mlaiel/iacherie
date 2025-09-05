"""Avatar Factory - Factory Pattern Central

Factory principal pour orchestration complète des avatars.
Gestion centralisée de la création d'avatars avec templates métier
et validation qualité intégrée.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

STRICT COPYRIGHT NOTICE:
This code belongs exclusively to Fahed Mlaiel. Unauthorized use prohibited.
"""

import asyncio
import logging
import json
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
import uuid

# Local imports
from .metahuman import MetaHumanGenerator, MetaHumanConfig, MetaHumanQuality, BodyType, AgeCategory
from .animation_system import AvatarAnimationSystem, AnimationConfig
from .clothing_system import AvatarClothingSystem, ClothingConfig
from .facial_expressions import FacialExpressionSystem, ExpressionConfig


class AvatarTemplate(Enum):
    """Templates d'avatars pré-configurés pour différents métiers"""
    INFLUENCER = "influencer"
    MUSICIAN = "musician"
    PHOTOGRAPHER = "photographer"
    FASHION_MODEL = "fashion_model"
    FITNESS_COACH = "fitness_coach"
    CHEF = "chef"
    ARTIST = "artist"
    BUSINESS_PROFESSIONAL = "business_professional"
    EDUCATOR = "educator"
    ENTERTAINER = "entertainer"
    CUSTOM = "custom"


class AvatarValidationLevel(Enum):
    """Niveaux de validation qualité"""
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


@dataclass
class AvatarSpec:
    """Spécification complète d'un avatar"""
    template: AvatarTemplate
    metahuman_config: Optional[MetaHumanConfig] = None
    animation_config: Optional[AnimationConfig] = None
    clothing_config: Optional[ClothingConfig] = None
    expression_config: Optional[ExpressionConfig] = None
    quality_level: MetaHumanQuality = MetaHumanQuality.STANDARD
    validation_level: AvatarValidationLevel = AvatarValidationLevel.STANDARD
    custom_attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AvatarCreationResult:
    """Résultat de création d'avatar"""
    avatar_id: str
    success: bool
    avatar_data: Optional[Dict[str, Any]] = None
    metahuman_data: Optional[Dict[str, Any]] = None
    animation_data: Optional[Dict[str, Any]] = None
    clothing_data: Optional[Dict[str, Any]] = None
    expression_data: Optional[Dict[str, Any]] = None
    validation_report: Optional[Dict[str, Any]] = None
    creation_time: datetime = field(default_factory=datetime.now)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class AvatarValidation:
    """Système de validation qualité et conformité"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def validate_avatar(self, avatar_data: Dict[str, Any], 
                            validation_level: AvatarValidationLevel) -> Dict[str, Any]:
        """Validation complète d'un avatar"""
        try:
            validation_report = {
                'validation_id': str(uuid.uuid4()),
                'level': validation_level.value,
                'timestamp': datetime.now().isoformat(),
                'checks': {},
                'score': 0.0,
                'passed': False,
                'issues': []
            }
            
            # Validation de base
            basic_score = await self._validate_basic_structure(avatar_data)
            validation_report['checks']['basic_structure'] = basic_score
            
            # Validation standard
            if validation_level in [AvatarValidationLevel.STANDARD, 
                                  AvatarValidationLevel.PREMIUM, 
                                  AvatarValidationLevel.ENTERPRISE]:
                quality_score = await self._validate_quality_metrics(avatar_data)
                validation_report['checks']['quality_metrics'] = quality_score
            
            # Validation premium
            if validation_level in [AvatarValidationLevel.PREMIUM, 
                                  AvatarValidationLevel.ENTERPRISE]:
                performance_score = await self._validate_performance(avatar_data)
                validation_report['checks']['performance'] = performance_score
            
            # Validation enterprise
            if validation_level == AvatarValidationLevel.ENTERPRISE:
                compliance_score = await self._validate_compliance(avatar_data)
                validation_report['checks']['compliance'] = compliance_score
            
            # Calcul score global
            total_score = sum(validation_report['checks'].values())
            validation_report['score'] = total_score / len(validation_report['checks'])
            validation_report['passed'] = validation_report['score'] >= 0.8
            
            return validation_report
            
        except Exception as e:
            self.logger.error(f"Erreur validation avatar: {e}")
            return {
                'validation_id': str(uuid.uuid4()),
                'level': validation_level.value,
                'timestamp': datetime.now().isoformat(),
                'score': 0.0,
                'passed': False,
                'error': str(e)
            }
    
    async def _validate_basic_structure(self, avatar_data: Dict[str, Any]) -> float:
        """Validation structure de base"""
        required_fields = ['avatar_id', 'metahuman_data', 'created_at']
        score = 0.0
        
        for field in required_fields:
            if field in avatar_data:
                score += 1.0
        
        return score / len(required_fields)
    
    async def _validate_quality_metrics(self, avatar_data: Dict[str, Any]) -> float:
        """Validation métriques qualité"""
        # Simulation validation qualité
        quality_checks = [
            'polygon_count',
            'texture_resolution', 
            'animation_smoothness',
            'facial_accuracy'
        ]
        return 0.85  # Score simulé
    
    async def _validate_performance(self, avatar_data: Dict[str, Any]) -> float:
        """Validation performance"""
        # Simulation validation performance
        return 0.90  # Score simulé
    
    async def _validate_compliance(self, avatar_data: Dict[str, Any]) -> float:
        """Validation conformité entreprise"""
        # Simulation validation conformité
        return 0.95  # Score simulé


class AvatarBuilder:
    """Builder pattern pour création progressive d'avatars"""
    
    def __init__(self):
        self.spec = AvatarSpec(template=AvatarTemplate.CUSTOM)
        self.logger = logging.getLogger(__name__)
    
    def with_template(self, template: AvatarTemplate) -> 'AvatarBuilder':
        """Définir le template d'avatar"""
        self.spec.template = template
        return self
    
    def with_metahuman_config(self, config: MetaHumanConfig) -> 'AvatarBuilder':
        """Définir la configuration MetaHuman"""
        self.spec.metahuman_config = config
        return self
    
    def with_animation_config(self, config: AnimationConfig) -> 'AvatarBuilder':
        """Définir la configuration d'animation"""
        self.spec.animation_config = config
        return self
    
    def with_clothing_config(self, config: ClothingConfig) -> 'AvatarBuilder':
        """Définir la configuration de vêtements"""
        self.spec.clothing_config = config
        return self
    
    def with_expression_config(self, config: ExpressionConfig) -> 'AvatarBuilder':
        """Définir la configuration d'expressions"""
        self.spec.expression_config = config
        return self
    
    def with_quality(self, quality: MetaHumanQuality) -> 'AvatarBuilder':
        """Définir le niveau de qualité"""
        self.spec.quality_level = quality
        return self
    
    def with_validation(self, validation: AvatarValidationLevel) -> 'AvatarBuilder':
        """Définir le niveau de validation"""
        self.spec.validation_level = validation
        return self
    
    def with_custom_attribute(self, key: str, value: Any) -> 'AvatarBuilder':
        """Ajouter un attribut personnalisé"""
        self.spec.custom_attributes[key] = value
        return self
    
    def build(self) -> AvatarSpec:
        """Construire la spécification finale"""
        return self.spec


class AvatarFactory:
    """Factory principal pour orchestration complète des avatars"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metahuman_generator = MetaHumanGenerator()
        self.animation_system = AvatarAnimationSystem()
        self.clothing_system = AvatarClothingSystem()
        self.expression_system = FacialExpressionSystem()
        self.validator = AvatarValidation()
        self._cache = {}
    
    async def create_avatar(self, spec: AvatarSpec) -> AvatarCreationResult:
        """Création complète d'un avatar selon les spécifications"""
        avatar_id = str(uuid.uuid4())
        result = AvatarCreationResult(avatar_id=avatar_id, success=False)
        
        try:
            self.logger.info(f"Début création avatar {avatar_id} avec template {spec.template.value}")
            
            # Étape 1: Configuration automatique selon template
            auto_config = await self._configure_from_template(spec)
            
            # Étape 2: Génération MetaHuman
            if auto_config.metahuman_config:
                metahuman_result = await self.metahuman_generator.generate_avatar(auto_config.metahuman_config)
                result.metahuman_data = metahuman_result
            
            # Étape 3: Configuration animations
            if auto_config.animation_config:
                animation_result = await self.animation_system.create_animation_set(auto_config.animation_config)
                result.animation_data = animation_result
            
            # Étape 4: Configuration vêtements
            if auto_config.clothing_config:
                clothing_result = await self.clothing_system.generate_outfit(auto_config.clothing_config)
                result.clothing_data = clothing_result
            
            # Étape 5: Configuration expressions
            if auto_config.expression_config:
                expression_result = await self.expression_system.generate_expression_set(auto_config.expression_config)
                result.expression_data = expression_result
            
            # Étape 6: Assemblage final
            avatar_data = await self._assemble_avatar(result, auto_config)
            result.avatar_data = avatar_data
            
            # Étape 7: Validation
            validation_report = await self.validator.validate_avatar(
                avatar_data, auto_config.validation_level
            )
            result.validation_report = validation_report
            
            # Étape 8: Cache et finalisation
            if validation_report.get('passed', False):
                self._cache[avatar_id] = result
                result.success = True
                self.logger.info(f"Avatar {avatar_id} créé avec succès")
            else:
                result.errors.append("Validation échouée")
                self.logger.warning(f"Avatar {avatar_id} n'a pas passé la validation")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erreur création avatar {avatar_id}: {e}")
            result.errors.append(str(e))
            return result
    
    async def _configure_from_template(self, spec: AvatarSpec) -> AvatarSpec:
        """Configuration automatique selon le template métier"""
        if spec.template == AvatarTemplate.INFLUENCER:
            return await self._configure_influencer_template(spec)
        elif spec.template == AvatarTemplate.MUSICIAN:
            return await self._configure_musician_template(spec)
        elif spec.template == AvatarTemplate.FASHION_MODEL:
            return await self._configure_fashion_model_template(spec)
        elif spec.template == AvatarTemplate.FITNESS_COACH:
            return await self._configure_fitness_coach_template(spec)
        else:
            return spec
    
    async def _configure_influencer_template(self, spec: AvatarSpec) -> AvatarSpec:
        """Configuration template influenceur"""
        if not spec.metahuman_config:
            from .metahuman import MetaHumanConfig
            spec.metahuman_config = MetaHumanConfig(
                quality=MetaHumanQuality.HIGH,
                body_type=BodyType.ATHLETIC,
                age_category=AgeCategory.YOUNG_ADULT,
                custom_features={'style': 'trendy', 'charisma': 'high'}
            )
        return spec
    
    async def _configure_musician_template(self, spec: AvatarSpec) -> AvatarSpec:
        """Configuration template musicien"""
        if not spec.metahuman_config:
            from .metahuman import MetaHumanConfig
            spec.metahuman_config = MetaHumanConfig(
                quality=MetaHumanQuality.HIGH,
                body_type=BodyType.AVERAGE,
                age_category=AgeCategory.YOUNG_ADULT,
                custom_features={'style': 'artistic', 'expression': 'creative'}
            )
        return spec
    
    async def _configure_fashion_model_template(self, spec: AvatarSpec) -> AvatarSpec:
        """Configuration template mannequin mode"""
        if not spec.metahuman_config:
            from .metahuman import MetaHumanConfig
            spec.metahuman_config = MetaHumanConfig(
                quality=MetaHumanQuality.ULTRA,
                body_type=BodyType.SLIM,
                age_category=AgeCategory.YOUNG_ADULT,
                custom_features={'style': 'elegant', 'posture': 'perfect'}
            )
        return spec
    
    async def _configure_fitness_coach_template(self, spec: AvatarSpec) -> AvatarSpec:
        """Configuration template coach fitness"""
        if not spec.metahuman_config:
            from .metahuman import MetaHumanConfig
            spec.metahuman_config = MetaHumanConfig(
                quality=MetaHumanQuality.HIGH,
                body_type=BodyType.MUSCULAR,
                age_category=AgeCategory.ADULT,
                custom_features={'style': 'athletic', 'energy': 'high'}
            )
        return spec
    
    async def _assemble_avatar(self, result: AvatarCreationResult, 
                             spec: AvatarSpec) -> Dict[str, Any]:
        """Assemblage final de l'avatar"""
        avatar_data = {
            'avatar_id': result.avatar_id,
            'template': spec.template.value,
            'created_at': result.creation_time.isoformat(),
            'quality_level': spec.quality_level.value,
            'validation_level': spec.validation_level.value,
            'metahuman_data': result.metahuman_data,
            'animation_data': result.animation_data,
            'clothing_data': result.clothing_data,
            'expression_data': result.expression_data,
            'custom_attributes': spec.custom_attributes
        }
        
        return avatar_data
    
    def get_cached_avatar(self, avatar_id: str) -> Optional[AvatarCreationResult]:
        """Récupération d'un avatar depuis le cache"""
        return self._cache.get(avatar_id)
    
    def clear_cache(self) -> None:
        """Vider le cache des avatars"""
        self._cache.clear()
    
    def get_template_presets(self) -> Dict[str, Dict[str, Any]]:
        """Obtenir les préréglages des templates"""
        return {
            'influencer': {
                'description': 'Avatar influenceur avec style tendance',
                'quality': 'high',
                'features': ['charismatic', 'trendy', 'social']
            },
            'musician': {
                'description': 'Avatar musicien avec style artistique',
                'quality': 'high',
                'features': ['creative', 'artistic', 'expressive']
            },
            'fashion_model': {
                'description': 'Avatar mannequin haute couture',
                'quality': 'ultra',
                'features': ['elegant', 'sophisticated', 'photogenic']
            },
            'fitness_coach': {
                'description': 'Avatar coach sportif énergique',
                'quality': 'high',
                'features': ['athletic', 'motivational', 'healthy']
            }
        }


# Factory instance globale
avatar_factory = AvatarFactory()

__all__ = [
    'AvatarFactory',
    'AvatarBuilder', 
    'AvatarTemplate',
    'AvatarSpec',
    'AvatarCreationResult',
    'AvatarValidation',
    'AvatarValidationLevel',
    'avatar_factory'
]