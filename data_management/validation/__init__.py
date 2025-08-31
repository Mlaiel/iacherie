""" Validation System - IA Influencer Agent Platform Enterprise
============================================================
Module: backend/data_management/validation/__init__.py
Author: Fahed Mlaiel (mlaiel@live.de)
============================================================

  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL 
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

 MODULE VALIDATION DONNÉES COMPLÈTE
Système de validation enterprise multi-format et multi-créateur
- Validation contenu audio/vidéo/image/texte
- Règles business par type de créateur
- Sécurité et conformité intégrée
- Métriques et monitoring avancés
- IA fingerprinting et qualité avancée
- Workflow orchestration complète
"""
from typing import Dict, List, Optional, Any, Union, Tuple
import logging
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import magic
import hashlib

# Modules de base existants
from .content_validator import ContentValidator, AsyncContentValidator
from .format_validator import FormatValidator, AsyncFormatValidator  
from .business_validator import BusinessValidator, AsyncBusinessValidator
from .security_validator import SecurityValidator, AsyncSecurityValidator

# Nouveaux modules IA avancés
from .fingerprint_validator import (
    FingerprintValidator,
    AsyncFingerprintValidator,
    FingerprintResult,
    SimilarityLevel,
    AudioFingerprintGenerator,
    VideoFingerprintGenerator,
    ImageFingerprintGenerator,
    TextFingerprintGenerator
)

from .quality_assessor import (
    QualityAssessor,
    AsyncQualityAssessor,
    QualityAssessmentResult,
    QualityScore,
    QualityDimension,
    QualityLevel,
    AudioQualityAnalyzer,
    VideoQualityAnalyzer
)

from .metadata_extractor import (
    MetadataExtractor,
    AsyncMetadataExtractor,
    ContentMetadata,
    TechnicalMetadata,
    MediaDimensions,
    CreativeMetadata,
    BusinessMetadata,
    GeolocationData,
    ImageMetadataExtractor,
    AudioMetadataExtractor,
    VideoMetadataExtractor,
    TextMetadataExtractor
)

from .compliance_checker import (
    ComplianceChecker,
    AsyncComplianceChecker,
    ComplianceResult,
    ComplianceIssue,
    ComplianceLevel,
    ComplianceCategory,
    JurisdictionType,
    PrivacyComplianceChecker,
    CopyrightComplianceChecker,
    PlatformPolicyChecker
)

from .workflow_validator import (
    WorkflowValidator,
    WorkflowOrchestrator,
    WorkflowResult,
    WorkflowConfiguration,
    WorkflowStepResult,
    WorkflowStep,
    WorkflowStatus,
    CreatorType
)

class ValidationLevel(Enum):
    """Niveaux de validation"""    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"
    ENTERPRISE = "enterprise"

@dataclass
class ValidationResult:
    """Résultat de validation"""    is_valid: bool
    score: float  # 0.0 - 1.0
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]
    
class ValidationConfig:
    """Configuration du système de validation"""    
    # Tailles maximales par type de créateur (en MB)
    MAX_FILE_SIZES = {
        'musician': {
            'audio': 500,  # 500MB pour audio haute qualité
            'video': 2000,  # 2GB pour clips musicaux
            'image': 50,   # 50MB pour artwork
            'document': 10  # 10MB pour paroles/partitions
        },
        'influencer': {
            'video': 1000,  # 1GB pour contenus sociaux
            'image': 25,   # 25MB pour photos/stories
            'audio': 100,  # 100MB pour podcasts courts
            'document': 5   # 5MB pour scripts
        },
        'photographer': {
            'image': 200,  # 200MB pour photos haute résolution
            'video': 500,  # 500MB pour timelapses
            'document': 20, # 20MB pour descriptions/contrats
            'audio': 50    # 50MB pour commentaires audio
        },
        'blogger': {
            'document': 50, # 50MB pour articles longs
            'image': 30,   # 30MB pour illustrations
            'video': 300,  # 300MB pour vidéos explicatives
            'audio': 100   # 100MB pour podcasts
        },
        'comedian': {
            'video': 800,  # 800MB pour spectacles
            'audio': 300,  # 300MB pour sketches audio
            'image': 20,   # 20MB pour affiches/memes
            'document': 15  # 15MB pour scripts
        }
    }
    
    # Formats supportés par type de créateur
    SUPPORTED_FORMATS = {
        'musician': {
            'audio': ['mp3', 'wav', 'flac', 'ogg', 'm4a', 'aiff'],
            'video': ['mp4', 'mov', 'avi', 'mkv'],
            'image': ['jpg', 'jpeg', 'png', 'tiff', 'webp'],
            'document': ['txt', 'md', 'pdf', 'docx']
        },
        'influencer': {
            'video': ['mp4', 'mov', 'webm', 'avi'],
            'image': ['jpg', 'jpeg', 'png', 'gif', 'webp'],
            'audio': ['mp3', 'wav', 'ogg', 'm4a'],
            'document': ['txt', 'md', 'pdf']
        },
        'photographer': {
            'image': ['jpg', 'jpeg', 'png', 'tiff', 'raw', 'dng', 'webp'],
            'video': ['mp4', 'mov', 'avi'],
            'document': ['txt', 'md', 'pdf', 'docx'],
            'audio': ['mp3', 'wav']
        },
        'blogger': {
            'document': ['txt', 'md', 'html', 'pdf', 'docx', 'rtf'],
            'image': ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'],
            'video': ['mp4', 'webm', 'mov'],
            'audio': ['mp3', 'wav', 'ogg']
        },
        'comedian': {
            'video': ['mp4', 'mov', 'avi', 'webm'],
            'audio': ['mp3', 'wav', 'ogg', 'm4a'],
            'image': ['jpg', 'jpeg', 'png', 'gif', 'webp'],
            'document': ['txt', 'md', 'pdf']
        }
    }
    
    # Règles de qualité minimales
    QUALITY_REQUIREMENTS = {
        'audio': {
            'min_sample_rate': 22050,
            'min_bitrate': 128,
            'max_duration': 3600  # 1 heure
        },
        'video': {
            'min_resolution': [640, 480],
            'min_fps': 15,
            'max_duration': 7200  # 2 heures
        },
        'image': {
            'min_resolution': [300, 300],
            'max_resolution': [8192, 8192],
            'min_quality': 50
        },
        'document': {
            'min_words': 10,
            'max_words': 100000,
            'encoding': 'utf-8'
        }
    }

class ValidationManager:
    """Gestionnaire principal du système de validation"""    
    def __init__(self, config: Optional[ValidationConfig] = None):
        self.config = config or ValidationConfig()
        self.logger = logging.getLogger(__name__)
        
        # Initialisation des validateurs
        self.content_validator = ContentValidator()
        self.format_validator = FormatValidator()
        self.business_validator = BusinessValidator(self.config)
        self.security_validator = SecurityValidator()
        
        # Cache des résultats de validation
        self._validation_cache: Dict[str, ValidationResult] = {}
    
    def validate_file(
        self,
        file_path: str,
        creator_type: str,
        content_type: str,
        level: ValidationLevel = ValidationLevel.STANDARD
    ) -> ValidationResult:
        """Valide un fichier selon le type de créateur et niveau requis"""        
        # Vérification du cache
        cache_key = self._generate_cache_key(file_path, creator_type, content_type, level)
        if cache_key in self._validation_cache:
            return self._validation_cache[cache_key]
        
        errors = []
        warnings = []
        metadata = {}
        
        try:
            # 1. Validation de format
            format_result = self.format_validator.validate_format(file_path, content_type)
            if not format_result.is_valid:
                errors.extend(format_result.errors)
            warnings.extend(format_result.warnings)
            metadata.update(format_result.metadata)
            
            # 2. Validation de contenu
            if format_result.is_valid:
                content_result = self.content_validator.validate_content(file_path, content_type)
                if not content_result.is_valid:
                    errors.extend(content_result.errors)
                warnings.extend(content_result.warnings)
                metadata.update(content_result.metadata)
            
            # 3. Validation métier
            if level in [ValidationLevel.STANDARD, ValidationLevel.STRICT, ValidationLevel.ENTERPRISE]:
                business_result = self.business_validator.validate_business_rules(
                    file_path, creator_type, content_type
                )
                if not business_result.is_valid:
                    errors.extend(business_result.errors)
                warnings.extend(business_result.warnings)
                metadata.update(business_result.metadata)
            
            # 4. Validation sécurité
            if level in [ValidationLevel.STRICT, ValidationLevel.ENTERPRISE]:
                security_result = self.security_validator.validate_security(file_path)
                if not security_result.is_valid:
                    errors.extend(security_result.errors)
                warnings.extend(security_result.warnings)
                metadata.update(security_result.metadata)
            
            # Calcul du score global
            score = self._calculate_validation_score(errors, warnings, level)
            
            result = ValidationResult(
                is_valid=len(errors) == 0,
                score=score,
                errors=errors,
                warnings=warnings,
                metadata=metadata
            )
            
            # Mise en cache
            self._validation_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erreur validation {file_path}: {e}")
            return ValidationResult(
                is_valid=False,
                score=0.0,
                errors=[f"Erreur système: {str(e)}"],
                warnings=[],
                metadata={}
            )
    
    def validate_batch(
        self,
        file_paths: List[str],
        creator_type: str,
        content_types: List[str],
        level: ValidationLevel = ValidationLevel.STANDARD
    ) -> Dict[str, ValidationResult]:
        """Valide un lot de fichiers"""        results = {}
        
        for i, file_path in enumerate(file_paths):
            content_type = content_types[i] if i < len(content_types) else 'unknown'
            results[file_path] = self.validate_file(file_path, creator_type, content_type, level)
        
        return results
    
    def get_validation_summary(self, results: Dict[str, ValidationResult]) -> Dict[str, Any]:
        """Génère un résumé des validations"""        total_files = len(results)
        valid_files = sum(1 for r in results.values() if r.is_valid)
        total_errors = sum(len(r.errors) for r in results.values())
        total_warnings = sum(len(r.warnings) for r in results.values())
        avg_score = sum(r.score for r in results.values()) / total_files if total_files > 0 else 0.0
        
        return {
            "total_files": total_files,
            "valid_files": valid_files,
            "invalid_files": total_files - valid_files,
            "success_rate": valid_files / total_files if total_files > 0 else 0.0,
            "total_errors": total_errors,
            "total_warnings": total_warnings,
            "average_score": avg_score,
            "validation_level": level.value if 'level' in locals() else "standard"
        }
    
    def _generate_cache_key(self, file_path: str, creator_type: str, content_type: str, level: ValidationLevel) -> str:
        """Génère une clé de cache pour les résultats de validation"""        # Inclure le hash du fichier pour détecter les modifications
        try:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.md5(f.read(1024)).hexdigest()  # Hash des premiers 1KB
        except:
            file_hash = "unknown"
        
        return f"{file_path}:{creator_type}:{content_type}:{level.value}:{file_hash}"
    
    def _calculate_validation_score(self, errors: List[str], warnings: List[str], level: ValidationLevel) -> float:
        """Calcule le score de validation basé sur les erreurs et avertissements"""        if errors:
            return 0.0  # Score 0 si des erreurs critiques
        
        # Score basé sur les avertissements et niveau de validation
        warning_penalty = len(warnings) * 0.1
        level_bonus = {
            ValidationLevel.BASIC: 0.0,
            ValidationLevel.STANDARD: 0.1,
            ValidationLevel.STRICT: 0.15,
            ValidationLevel.ENTERPRISE: 0.2
        }.get(level, 0.0)
        
        score = 1.0 - warning_penalty + level_bonus
        return max(0.0, min(1.0, score))  # Clamp entre 0 et 1

# Instances globales pour usage facile
validation_manager = ValidationManager()

# Export des classes principales
__all__ = [
    # Modules de base
    'ValidationManager',
    'ValidationConfig', 
    'ValidationResult',
    'ValidationLevel',
    'ContentValidator',
    'AsyncContentValidator',
    'FormatValidator',
    'AsyncFormatValidator',
    'BusinessValidator',
    'AsyncBusinessValidator',
    'SecurityValidator',
    'AsyncSecurityValidator',
    'validation_manager',
    
    # Fingerprinting IA
    'FingerprintValidator',
    'AsyncFingerprintValidator',
    'FingerprintResult',
    'SimilarityLevel',
    'AudioFingerprintGenerator',
    'VideoFingerprintGenerator',
    'ImageFingerprintGenerator',
    'TextFingerprintGenerator',
    
    # Évaluation qualité
    'QualityAssessor',
    'AsyncQualityAssessor',
    'QualityAssessmentResult',
    'QualityScore',
    'QualityDimension',
    'QualityLevel',
    'AudioQualityAnalyzer',
    'VideoQualityAnalyzer',
    
    # Extraction métadonnées
    'MetadataExtractor',
    'AsyncMetadataExtractor',
    'ContentMetadata',
    'TechnicalMetadata',
    'MediaDimensions',
    'CreativeMetadata',
    'BusinessMetadata',
    'GeolocationData',
    'ImageMetadataExtractor',
    'AudioMetadataExtractor',
    'VideoMetadataExtractor',
    'TextMetadataExtractor',
    
    # Vérification conformité
    'ComplianceChecker',
    'AsyncComplianceChecker',
    'ComplianceResult',
    'ComplianceIssue',
    'ComplianceLevel',
    'ComplianceCategory',
    'JurisdictionType',
    'PrivacyComplianceChecker',
    'CopyrightComplianceChecker',
    'PlatformPolicyChecker',
    
    # Workflow orchestration
    'WorkflowValidator',
    'WorkflowOrchestrator',
    'WorkflowResult',
    'WorkflowConfiguration',
    'WorkflowStepResult',
    'WorkflowStep',
    'WorkflowStatus',
    'CreatorType'
]

# Version du module
__version__ = "1.0.0"

# Configuration par défaut
DEFAULT_VALIDATION_CONFIG = {
    'quality_thresholds': {
        'minimum_score': 0.7,
        'technical_quality': 0.8,
        'professional_standard': 0.9
    },
    'compliance_jurisdictions': ['EU', 'US'],
    'target_platforms': ['youtube', 'instagram', 'tiktok'],
    'fingerprint_enabled': True,
    'parallel_execution': True,
    'timeout_seconds': 300
}
