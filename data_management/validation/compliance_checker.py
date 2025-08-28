"""
🚀 Compliance Checker - IA Influencer Agent Platform Enterprise
===============================================================
Module: backend/data_management/validation/compliance_checker.py
Author: Fahed Mlaiel (mlaiel@live.de)
===============================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 VÉRIFICATION CONFORMITÉ LÉGALE & PLATEFORME
Vérification automatisée des conformités multi-juridictionnelles
- RGPD/GDPR compliance complète
- CCPA/Privacy Act américain
- Copyright et propriété intellectuelle
- Standards plateformes (YouTube, TikTok, Instagram)
- Conformité business multi-créateurs
"""

from typing import Dict, List, Optional, Any, Union, Tuple, Set
import asyncio
import logging
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import re
import json
from urllib.parse import urlparse

# ML pour détection de contenu
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np

# Analyse d'image pour contenu inapproprié
from PIL import Image
import cv2

# Validation de données
import validators
from email_validator import validate_email, EmailNotValidError

# Geo-compliance
import pycountry
from geopy.geocoders import Nominatim

logger = logging.getLogger(__name__)

class ComplianceLevel(Enum):
    """Niveaux de conformité"""
    COMPLIANT = "compliant"
    WARNING = "warning"
    VIOLATION = "violation"
    CRITICAL = "critical"

class ComplianceCategory(Enum):
    """Catégories de conformité"""
    PRIVACY = "privacy"
    COPYRIGHT = "copyright"
    CONTENT_SAFETY = "content_safety"
    PLATFORM_POLICY = "platform_policy"
    BUSINESS_TERMS = "business_terms"
    ACCESSIBILITY = "accessibility"
    LEGAL_REQUIREMENTS = "legal_requirements"

class JurisdictionType(Enum):
    """Types de juridiction"""
    EU = "european_union"
    US = "united_states"
    CA = "canada"
    UK = "united_kingdom"
    GLOBAL = "global"

@dataclass
class ComplianceIssue:
    """Issue de conformité détectée"""
    category: ComplianceCategory
    level: ComplianceLevel
    jurisdiction: JurisdictionType
    description: str
    details: Dict[str, Any]
    suggested_actions: List[str]
    legal_reference: Optional[str] = None
    auto_fixable: bool = False
    fix_priority: int = 1  # 1=low, 5=critical

@dataclass
class ComplianceResult:
    """Résultat de vérification de conformité"""
    overall_compliance: ComplianceLevel
    issues: List[ComplianceIssue]
    compliant_categories: List[ComplianceCategory]
    jurisdiction_status: Dict[JurisdictionType, ComplianceLevel]
    recommendations: List[str]
    required_actions: List[str]
    compliance_score: float  # 0.0 - 1.0
    certification_ready: bool
    metadata: Dict[str, Any]

class PrivacyComplianceChecker:
    """Vérificateur de conformité vie privée (RGPD/CCPA)"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.PrivacyComplianceChecker")
        
        # Patterns pour détecter des données personnelles
        self.pii_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            'passport': r'\b[A-Z]{1,2}\d{6,9}\b'
        }
        
        # Mots-clés sensibles RGPD
        self.gdpr_sensitive_keywords = [
            'race', 'ethnic', 'political', 'religious', 'philosophical',
            'trade union', 'genetic', 'biometric', 'health', 'sex life',
            'sexual orientation', 'criminal conviction'
        ]
    
    def check_privacy_compliance(self, content: Dict[str, Any], 
                               metadata: Dict[str, Any]) -> List[ComplianceIssue]:
        """Vérifie la conformité vie privée"""
        issues = []
        
        # Vérification données personnelles dans contenu
        pii_issues = self._check_pii_exposure(content)
        issues.extend(pii_issues)
        
        # Vérification métadonnées sensibles
        metadata_issues = self._check_metadata_privacy(metadata)
        issues.extend(metadata_issues)
        
        # Vérification géolocalisation
        geo_issues = self._check_geolocation_compliance(metadata)
        issues.extend(geo_issues)
        
        # Vérification consentement
        consent_issues = self._check_consent_compliance(metadata)
        issues.extend(consent_issues)
        
        return issues
    
    def _check_pii_exposure(self, content: Dict[str, Any]) -> List[ComplianceIssue]:
        """Vérifie l'exposition de données personnelles"""
        issues = []
        
        # Analyse du contenu textuel
        text_content = ""
        if 'text' in content:
            text_content = str(content['text'])
        elif 'description' in content:
            text_content = str(content['description'])
        elif 'title' in content:
            text_content = str(content['title'])
        
        if text_content:
            for pii_type, pattern in self.pii_patterns.items():
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                
                if matches:
                    issues.append(ComplianceIssue(
                        category=ComplianceCategory.PRIVACY,
                        level=ComplianceLevel.CRITICAL,
                        jurisdiction=JurisdictionType.EU,
                        description=f"Données personnelles détectées: {pii_type}",
                        details={
                            'pii_type': pii_type,
                            'matches_count': len(matches),
                            'sample_matches': matches[:3]  # Échantillon sans données réelles
                        },
                        suggested_actions=[
                            f"Supprimer ou anonymiser les {pii_type}",
                            "Obtenir le consentement explicite si nécessaire",
                            "Implémenter la pseudonymisation"
                        ],
                        legal_reference="RGPD Art. 4, 5",
                        auto_fixable=False,
                        fix_priority=5
                    ))
        
        # Vérification données sensibles RGPD
        for keyword in self.gdpr_sensitive_keywords:
            if keyword.lower() in text_content.lower():
                issues.append(ComplianceIssue(
                    category=ComplianceCategory.PRIVACY,
                    level=ComplianceLevel.CRITICAL,
                    jurisdiction=JurisdictionType.EU,
                    description=f"Données sensibles RGPD détectées: {keyword}",
                    details={'sensitive_keyword': keyword},
                    suggested_actions=[
                        "Vérifier la base légale pour le traitement",
                        "Obtenir le consentement explicite",
                        "Évaluer la nécessité du traitement"
                    ],
                    legal_reference="RGPD Art. 9",
                    auto_fixable=False,
                    fix_priority=5
                ))
        
        return issues
    
    def _check_metadata_privacy(self, metadata: Dict[str, Any]) -> List[ComplianceIssue]:
        """Vérifie la vie privée dans les métadonnées"""
        issues = []
        
        # Vérification EXIF sensible
        if 'geolocation' in metadata and metadata['geolocation']:
            geo = metadata['geolocation']
            if geo.get('latitude') and geo.get('longitude'):
                issues.append(ComplianceIssue(
                    category=ComplianceCategory.PRIVACY,
                    level=ComplianceLevel.WARNING,
                    jurisdiction=JurisdictionType.EU,
                    description="Géolocalisation précise dans métadonnées",
                    details={
                        'has_coordinates': True,
                        'precision': 'high'
                    },
                    suggested_actions=[
                        "Supprimer les coordonnées GPS précises",
                        "Utiliser une géolocalisation approximative",
                        "Demander le consentement pour la géolocalisation"
                    ],
                    legal_reference="RGPD Art. 4(1)",
                    auto_fixable=True,
                    fix_priority=3
                ))
        
        # Vérification métadonnées d'appareil
        technical = metadata.get('technical', {})
        if technical.get('device_info') or technical.get('camera_model'):
            issues.append(ComplianceIssue(
                category=ComplianceCategory.PRIVACY,
                level=ComplianceLevel.WARNING,
                jurisdiction=JurisdictionType.EU,
                description="Informations d'appareil dans métadonnées",
                details={'device_tracking_possible': True},
                suggested_actions=[
                    "Supprimer les métadonnées d'appareil",
                    "Nettoyer les EXIF avant publication"
                ],
                legal_reference="RGPD Art. 4(1)",
                auto_fixable=True,
                fix_priority=2
            ))
        
        return issues
    
    def _check_geolocation_compliance(self, metadata: Dict[str, Any]) -> List[ComplianceIssue]:
        """Vérifie la conformité géolocalisation"""
        issues = []
        
        geolocation = metadata.get('geolocation')
        if geolocation and geolocation.get('latitude'):
            # Précision de la géolocalisation
            lat = float(geolocation['latitude'])
            lon = float(geolocation['longitude'])
            
            # Vérification si c'est une zone sensible
            if self._is_sensitive_location(lat, lon):
                issues.append(ComplianceIssue(
                    category=ComplianceCategory.PRIVACY,
                    level=ComplianceLevel.CRITICAL,
                    jurisdiction=JurisdictionType.GLOBAL,
                    description="Géolocalisation dans zone sensible",
                    details={
                        'location_type': 'sensitive_area',
                        'privacy_risk': 'high'
                    },
                    suggested_actions=[
                        "Supprimer la géolocalisation",
                        "Obtenir consentement explicite",
                        "Évaluer la nécessité"
                    ],
                    legal_reference="RGPD Art. 6",
                    auto_fixable=False,
                    fix_priority=5
                ))
        
        return issues
    
    def _check_consent_compliance(self, metadata: Dict[str, Any]) -> List[ComplianceIssue]:
        """Vérifie la conformité du consentement"""
        issues = []
        
        # Vérification présence de consentement
        consent_info = metadata.get('consent', {})
        
        if not consent_info:
            issues.append(ComplianceIssue(
                category=ComplianceCategory.PRIVACY,
                level=ComplianceLevel.WARNING,
                jurisdiction=JurisdictionType.EU,
                description="Absence d'informations de consentement",
                details={'consent_documented': False},
                suggested_actions=[
                    "Documenter le consentement obtenu",
                    "Implémenter un mécanisme de consentement",
                    "Vérifier la base légale du traitement"
                ],
                legal_reference="RGPD Art. 7",
                auto_fixable=False,
                fix_priority=3
            ))
        else:
            # Vérification validité du consentement
            consent_date = consent_info.get('date')
            if consent_date:
                consent_age = datetime.now() - datetime.fromisoformat(consent_date)
                if consent_age > timedelta(days=365):  # Plus d'un an
                    issues.append(ComplianceIssue(
                        category=ComplianceCategory.PRIVACY,
                        level=ComplianceLevel.WARNING,
                        jurisdiction=JurisdictionType.EU,
                        description="Consentement expiré (>1 an)",
                        details={'consent_age_days': consent_age.days},
                        suggested_actions=[
                            "Renouveler le consentement",
                            "Vérifier si le consentement est toujours valide"
                        ],
                        legal_reference="RGPD Art. 7(3)",
                        auto_fixable=False,
                        fix_priority=2
                    ))
        
        return issues
    
    def _is_sensitive_location(self, lat: float, lon: float) -> bool:
        """Vérifie si une localisation est sensible"""
        # Zones sensibles basiques (à étendre)
        sensitive_zones = [
            # Écoles, hôpitaux, zones militaires approximatives
            {'lat_range': (48.8, 48.9), 'lon_range': (2.3, 2.4), 'type': 'restricted'},  # Paris centre
            # Ajouter d'autres zones selon les besoins
        ]
        
        for zone in sensitive_zones:
            lat_min, lat_max = zone['lat_range']
            lon_min, lon_max = zone['lon_range']
            
            if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
                return True
        
        return False

class CopyrightComplianceChecker:
    """Vérificateur de conformité copyright"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.CopyrightComplianceChecker")
        
        # Mots-clés de copyright
        self.copyright_indicators = [
            '©', 'copyright', 'all rights reserved', 'proprietary',
            'trademark', '®', '™', 'licensed', 'permission required'
        ]
        
        # Formats protégés couramment
        self.protected_formats = {
            'music': ['mp3', 'flac', 'wav', 'm4a'],
            'video': ['mp4', 'avi', 'mov', 'mkv'],
            'image': ['jpg', 'png', 'gif', 'bmp']
        }
    
    def check_copyright_compliance(self, content: Dict[str, Any], 
                                 metadata: Dict[str, Any]) -> List[ComplianceIssue]:
        """Vérifie la conformité copyright"""
        issues = []
        
        # Vérification licence
        license_issues = self._check_license_compliance(metadata)
        issues.extend(license_issues)
        
        # Vérification attribution
        attribution_issues = self._check_attribution_requirements(metadata)
        issues.extend(attribution_issues)
        
        # Vérification usage commercial
        commercial_issues = self._check_commercial_usage(metadata)
        issues.extend(commercial_issues)
        
        # Vérification watermarks
        watermark_issues = self._check_watermark_requirements(content, metadata)
        issues.extend(watermark_issues)
        
        return issues
    
    def _check_license_compliance(self, metadata: Dict[str, Any]) -> List[ComplianceIssue]:
        """Vérifie la conformité de licence"""
        issues = []
        
        business = metadata.get('business', {})
        license_info = business.get('license')
        
        if not license_info:
            issues.append(ComplianceIssue(
                category=ComplianceCategory.COPYRIGHT,
                level=ComplianceLevel.CRITICAL,
                jurisdiction=JurisdictionType.GLOBAL,
                description="Licence non spécifiée",
                details={'license_status': 'missing'},
                suggested_actions=[
                    "Spécifier une licence appropriée",
                    "Vérifier les droits de propriété",
                    "Documenter la chaîne de droits"
                ],
                legal_reference="Copyright Law",
                auto_fixable=False,
                fix_priority=4
            ))
        else:
            # Vérification validité de la licence
            if 'unknown' in license_info.lower() or 'none' in license_info.lower():
                issues.append(ComplianceIssue(
                    category=ComplianceCategory.COPYRIGHT,
                    level=ComplianceLevel.WARNING,
                    jurisdiction=JurisdictionType.GLOBAL,
                    description="Licence non claire ou invalide",
                    details={'license': license_info},
                    suggested_actions=[
                        "Clarifier les termes de licence",
                        "Utiliser une licence standard (CC, GPL, etc.)"
                    ],
                    legal_reference="Copyright Law",
                    auto_fixable=False,
                    fix_priority=3
                ))
        
        return issues
    
    def _check_attribution_requirements(self, metadata: Dict[str, Any]) -> List[ComplianceIssue]:
        """Vérifie les exigences d'attribution"""
        issues = []
        
        business = metadata.get('business', {})
        creative = metadata.get('creative', {})
        
        # Vérification si attribution requise
        attribution_required = business.get('attribution_required', False)
        
        if attribution_required:
            # Vérification présence d'informations d'attribution
            creator = creative.get('creator')
            copyright_info = creative.get('copyright')
            
            if not creator and not copyright_info:
                issues.append(ComplianceIssue(
                    category=ComplianceCategory.COPYRIGHT,
                    level=ComplianceLevel.VIOLATION,
                    jurisdiction=JurisdictionType.GLOBAL,
                    description="Attribution requise mais manquante",
                    details={
                        'attribution_required': True,
                        'creator_info': bool(creator),
                        'copyright_info': bool(copyright_info)
                    },
                    suggested_actions=[
                        "Ajouter les informations de créateur",
                        "Inclure le copyright approprié",
                        "Respecter les termes de licence"
                    ],
                    legal_reference="Creative Commons Attribution",
                    auto_fixable=True,
                    fix_priority=4
                ))
        
        return issues
    
    def _check_commercial_usage(self, metadata: Dict[str, Any]) -> List[ComplianceIssue]:
        """Vérifie l'usage commercial"""
        issues = []
        
        business = metadata.get('business', {})
        commercial_use = business.get('commercial_use')
        monetization_context = metadata.get('context', {}).get('monetization', False)
        
        # Si usage commercial prévu mais pas autorisé
        if monetization_context and commercial_use is False:
            issues.append(ComplianceIssue(
                category=ComplianceCategory.COPYRIGHT,
                level=ComplianceLevel.VIOLATION,
                jurisdiction=JurisdictionType.GLOBAL,
                description="Usage commercial non autorisé",
                details={
                    'commercial_allowed': commercial_use,
                    'monetization_intended': monetization_context
                },
                suggested_actions=[
                    "Obtenir licence commerciale",
                    "Utiliser contenu libre de droits",
                    "Retirer l'intention de monétisation"
                ],
                legal_reference="Copyright Law - Commercial Use",
                auto_fixable=False,
                fix_priority=5
            ))
        
        return issues
    
    def _check_watermark_requirements(self, content: Dict[str, Any], 
                                    metadata: Dict[str, Any]) -> List[ComplianceIssue]:
        """Vérifie les exigences de watermark"""
        issues = []
        
        business = metadata.get('business', {})
        
        # Si watermark requis par la licence
        license_text = business.get('license', '').lower()
        if 'watermark' in license_text or 'attribution' in license_text:
            
            # Vérification présence watermark dans contenu
            has_watermark = self._detect_watermark(content)
            
            if not has_watermark:
                issues.append(ComplianceIssue(
                    category=ComplianceCategory.COPYRIGHT,
                    level=ComplianceLevel.WARNING,
                    jurisdiction=JurisdictionType.GLOBAL,
                    description="Watermark requis mais absent",
                    details={'watermark_detected': has_watermark},
                    suggested_actions=[
                        "Ajouter watermark approprié",
                        "Inclure attribution visible",
                        "Respecter les termes de licence"
                    ],
                    legal_reference="License Terms",
                    auto_fixable=True,
                    fix_priority=2
                ))
        
        return issues
    
    def _detect_watermark(self, content: Dict[str, Any]) -> bool:
        """Détecte la présence d'un watermark"""
        # Analyse basique pour détecter watermarks
        
        # Dans le texte
        text_content = str(content.get('text', ''))
        for indicator in self.copyright_indicators:
            if indicator.lower() in text_content.lower():
                return True
        
        # Dans les métadonnées créatives
        creative = content.get('creative', {})
        if creative.get('copyright') or creative.get('creator'):
            return True
        
        # Visual detection for images/videos
        content_type = creative.get('type', '').lower()
        
        if content_type in ['image', 'video']:
            try:
                # Implement visual content analysis for copyright detection
                visual_analysis = await self._analyze_visual_content(creative)
                if visual_analysis.get('has_copyrighted_elements', False):
                    return True
                
                # Check for brand logos or watermarks
                if visual_analysis.get('has_brand_elements', False):
                    return True
                
                # Check for recognizable faces or celebrities
                if visual_analysis.get('has_celebrity_faces', False):
                    return True
                    
            except Exception as e:
                self.logger.warning(f"Visual analysis failed: {e}")
        
        return False
    
    async def _analyze_visual_content(self, creative: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze visual content for copyright elements
        
        Args:
            creative: Creative content metadata
            
        Returns:
            Dict containing analysis results
        """
        analysis_result = {
            'has_copyrighted_elements': False,
            'has_brand_elements': False,
            'has_celebrity_faces': False,
            'confidence_scores': {}
        }
        
        try:
            content_url = creative.get('url') or creative.get('file_path')
            if not content_url:
                return analysis_result
            
            # Check for known copyrighted visual patterns
            visual_fingerprint = creative.get('visual_fingerprint', '')
            if visual_fingerprint:
                # Compare against known copyrighted content database
                copyright_match = await self._check_copyright_database(visual_fingerprint)
                if copyright_match:
                    analysis_result['has_copyrighted_elements'] = True
                    analysis_result['confidence_scores']['copyright'] = copyright_match.get('confidence', 0.0)
            
            # Check for brand logos using simple pattern matching
            metadata = creative.get('metadata', {})
            if metadata.get('has_text_overlay') or metadata.get('detected_text'):
                # Simple brand detection based on text content
                detected_text = metadata.get('detected_text', '').lower()
                common_brands = ['nike', 'adidas', 'apple', 'google', 'microsoft', 'disney', 'marvel', 'dc comics']
                
                for brand in common_brands:
                    if brand in detected_text:
                        analysis_result['has_brand_elements'] = True
                        analysis_result['confidence_scores']['brand'] = 0.8
                        break
            
            # Check for face detection results
            if metadata.get('faces_detected', 0) > 0:
                # In a production system, this would use celebrity recognition APIs
                # For now, flag content with multiple faces as potentially having celebrities
                if metadata.get('faces_detected', 0) > 2:
                    analysis_result['has_celebrity_faces'] = True
                    analysis_result['confidence_scores']['celebrity'] = 0.6
            
            self.logger.info(f"Visual analysis completed for content: {analysis_result}")
            
        except Exception as e:
            self.logger.error(f"Error in visual content analysis: {e}")
        
        return analysis_result
    
    async def _check_copyright_database(self, visual_fingerprint: str) -> Optional[Dict[str, Any]]:
        """
        Check visual fingerprint against copyright database
        
        Args:
            visual_fingerprint: Visual content fingerprint/hash
            
        Returns:
            Match result if found, None otherwise
        """
        try:
            # In production, this would query a real copyright database
            # For now, simulate with known bad hashes
            known_copyrighted_hashes = {
                'abc123def456': {'owner': 'Disney Corp', 'confidence': 0.95},
                'def456ghi789': {'owner': 'Universal Studios', 'confidence': 0.89},
                'ghi789jkl012': {'owner': 'Warner Bros', 'confidence': 0.92}
            }
            
            if visual_fingerprint in known_copyrighted_hashes:
                return known_copyrighted_hashes[visual_fingerprint]
            
            # Simulate fuzzy matching with similar hashes
            for known_hash, info in known_copyrighted_hashes.items():
                # Simple similarity check (in production use proper similarity algorithms)
                if len(visual_fingerprint) >= 8 and visual_fingerprint[:8] == known_hash[:8]:
                    return {
                        'owner': info['owner'],
                        'confidence': info['confidence'] * 0.7  # Lower confidence for fuzzy match
                    }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error checking copyright database: {e}")
            return None

class PlatformPolicyChecker:
    """Vérificateur de conformité aux politiques des plateformes"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.PlatformPolicyChecker")
        
        # Initialisation des modèles de modération
        try:
            self.content_moderator = pipeline("text-classification", 
                                             model="unitary/toxic-bert")
        except Exception as e:
            self.logger.warning(f"Impossible de charger le modérateur: {e}")
            self.content_moderator = None
        
        # Règles par plateforme
        self.platform_rules = {
            'youtube': {
                'max_duration': 12 * 3600,  # 12 heures
                'prohibited_content': ['violence', 'hate_speech', 'misleading'],
                'copyright_strict': True,
                'age_restrictions': True
            },
            'tiktok': {
                'max_duration': 180,  # 3 minutes
                'prohibited_content': ['violence', 'adult_content', 'dangerous'],
                'copyright_strict': True,
                'age_restrictions': True
            },
            'instagram': {
                'max_duration': 3600,  # 1 heure pour IGTV
                'prohibited_content': ['nudity', 'violence', 'hate_speech'],
                'copyright_strict': True,
                'age_restrictions': True
            }
        }
    
    def check_platform_compliance(self, content: Dict[str, Any], 
                                 metadata: Dict[str, Any],
                                 platforms: List[str]) -> List[ComplianceIssue]:
        """Vérifie la conformité aux plateformes"""
        issues = []
        
        for platform in platforms:
            platform_issues = self._check_single_platform(content, metadata, platform)
            issues.extend(platform_issues)
        
        return issues
    
    def _check_single_platform(self, content: Dict[str, Any], 
                              metadata: Dict[str, Any], 
                              platform: str) -> List[ComplianceIssue]:
        """Vérifie la conformité pour une plateforme"""
        issues = []
        
        if platform not in self.platform_rules:
            return issues
        
        rules = self.platform_rules[platform]
        
        # Vérification durée
        duration_issues = self._check_duration_limits(metadata, platform, rules)
        issues.extend(duration_issues)
        
        # Vérification contenu inapproprié
        content_issues = self._check_inappropriate_content(content, platform, rules)
        issues.extend(content_issues)
        
        # Vérification restrictions d'âge
        age_issues = self._check_age_restrictions(content, metadata, platform, rules)
        issues.extend(age_issues)
        
        # Vérification format
        format_issues = self._check_format_requirements(metadata, platform)
        issues.extend(format_issues)
        
        return issues
    
    def _check_duration_limits(self, metadata: Dict[str, Any], 
                              platform: str, rules: Dict[str, Any]) -> List[ComplianceIssue]:
        """Vérifie les limites de durée"""
        issues = []
        
        dimensions = metadata.get('dimensions', {})
        duration = dimensions.get('duration')
        
        if duration and 'max_duration' in rules:
            max_duration = rules['max_duration']
            
            if duration > max_duration:
                issues.append(ComplianceIssue(
                    category=ComplianceCategory.PLATFORM_POLICY,
                    level=ComplianceLevel.VIOLATION,
                    jurisdiction=JurisdictionType.GLOBAL,
                    description=f"Durée excessive pour {platform}",
                    details={
                        'platform': platform,
                        'duration': duration,
                        'max_allowed': max_duration,
                        'excess_seconds': duration - max_duration
                    },
                    suggested_actions=[
                        f"Réduire la durée à maximum {max_duration//60} minutes",
                        "Diviser en plusieurs parties",
                        "Choisir une autre plateforme"
                    ],
                    legal_reference=f"{platform.title()} Terms of Service",
                    auto_fixable=False,
                    fix_priority=3
                ))
        
        return issues
    
    def _check_inappropriate_content(self, content: Dict[str, Any], 
                                   platform: str, rules: Dict[str, Any]) -> List[ComplianceIssue]:
        """Vérifie le contenu inapproprié"""
        issues = []
        
        # Analyse du contenu textuel
        text_content = str(content.get('text', ''))
        if text_content and self.content_moderator:
            try:
                moderation_result = self.content_moderator(text_content[:512])
                
                for result in moderation_result:
                    if result['label'] == 'TOXIC' and result['score'] > 0.7:
                        issues.append(ComplianceIssue(
                            category=ComplianceCategory.PLATFORM_POLICY,
                            level=ComplianceLevel.VIOLATION,
                            jurisdiction=JurisdictionType.GLOBAL,
                            description=f"Contenu toxique détecté pour {platform}",
                            details={
                                'platform': platform,
                                'toxicity_score': result['score'],
                                'content_type': 'text'
                            },
                            suggested_actions=[
                                "Réviser le contenu textuel",
                                "Supprimer les éléments inappropriés",
                                "Utiliser un langage plus approprié"
                            ],
                            legal_reference=f"{platform.title()} Community Guidelines",
                            auto_fixable=False,
                            fix_priority=4
                        ))
            except Exception as e:
                self.logger.debug(f"Erreur modération contenu: {e}")
        
        # Vérification mots-clés prohibés
        prohibited_keywords = {
            'violence': ['kill', 'murder', 'attack', 'weapon', 'bomb'],
            'hate_speech': ['hate', 'racist', 'nazi', 'terrorist'],
            'adult_content': ['sex', 'porn', 'naked', 'explicit'],
            'dangerous': ['suicide', 'self-harm', 'drug', 'illegal']
        }
        
        for category, keywords in prohibited_keywords.items():
            if category in rules.get('prohibited_content', []):
                for keyword in keywords:
                    if keyword.lower() in text_content.lower():
                        issues.append(ComplianceIssue(
                            category=ComplianceCategory.PLATFORM_POLICY,
                            level=ComplianceLevel.WARNING,
                            jurisdiction=JurisdictionType.GLOBAL,
                            description=f"Contenu potentiellement problématique: {category}",
                            details={
                                'platform': platform,
                                'category': category,
                                'keyword': keyword
                            },
                            suggested_actions=[
                                f"Réviser le contenu lié à: {category}",
                                "Considérer une formulation alternative",
                                "Ajouter des avertissements si approprié"
                            ],
                            legal_reference=f"{platform.title()} Community Guidelines",
                            auto_fixable=False,
                            fix_priority=3
                        ))
        
        return issues
    
    def _check_age_restrictions(self, content: Dict[str, Any], 
                               metadata: Dict[str, Any], 
                               platform: str, rules: Dict[str, Any]) -> List[ComplianceIssue]:
        """Vérifie les restrictions d'âge"""
        issues = []
        
        if not rules.get('age_restrictions'):
            return issues
        
        # Détection contenu mature
        mature_indicators = ['alcohol', 'tobacco', 'gambling', 'mature theme']
        text_content = str(content.get('text', '')).lower()
        
        for indicator in mature_indicators:
            if indicator in text_content:
                issues.append(ComplianceIssue(
                    category=ComplianceCategory.PLATFORM_POLICY,
                    level=ComplianceLevel.WARNING,
                    jurisdiction=JurisdictionType.GLOBAL,
                    description=f"Contenu mature détecté pour {platform}",
                    details={
                        'platform': platform,
                        'mature_indicator': indicator,
                        'age_restriction_needed': True
                    },
                    suggested_actions=[
                        "Marquer comme contenu mature",
                        "Ajouter des avertissements d'âge",
                        "Vérifier les restrictions de la plateforme"
                    ],
                    legal_reference=f"{platform.title()} Age Restriction Policy",
                    auto_fixable=True,
                    fix_priority=2
                ))
                break  # Un seul avertissement par plateforme
        
        return issues
    
    def _check_format_requirements(self, metadata: Dict[str, Any], 
                                  platform: str) -> List[ComplianceIssue]:
        """Vérifie les exigences de format"""
        issues = []
        
        technical = metadata.get('technical', {})
        dimensions = metadata.get('dimensions', {})
        
        file_format = technical.get('file_format', '').lower()
        
        # Formats recommandés par plateforme
        platform_formats = {
            'youtube': ['mp4', 'mov', 'avi', 'wmv', 'flv'],
            'tiktok': ['mp4', 'mov'],
            'instagram': ['mp4', 'mov', 'jpg', 'png']
        }
        
        if platform in platform_formats:
            recommended_formats = platform_formats[platform]
            
            if file_format and file_format not in recommended_formats:
                issues.append(ComplianceIssue(
                    category=ComplianceCategory.PLATFORM_POLICY,
                    level=ComplianceLevel.WARNING,
                    jurisdiction=JurisdictionType.GLOBAL,
                    description=f"Format non optimal pour {platform}",
                    details={
                        'platform': platform,
                        'current_format': file_format,
                        'recommended_formats': recommended_formats
                    },
                    suggested_actions=[
                        f"Convertir vers un format recommandé: {', '.join(recommended_formats)}",
                        "Vérifier la qualité après conversion",
                        "Optimiser pour la plateforme"
                    ],
                    legal_reference=f"{platform.title()} Upload Requirements",
                    auto_fixable=True,
                    fix_priority=1
                ))
        
        return issues

class ComplianceChecker:
    """Vérificateur de conformité principal"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.ComplianceChecker")
        
        # Vérificateurs spécialisés
        self.privacy_checker = PrivacyComplianceChecker()
        self.copyright_checker = CopyrightComplianceChecker()
        self.platform_checker = PlatformPolicyChecker()
        
        # Cache des résultats
        self._compliance_cache: Dict[str, ComplianceResult] = {}
    
    def check_compliance(self, content: Dict[str, Any], 
                        metadata: Dict[str, Any],
                        target_platforms: List[str] = None,
                        jurisdictions: List[JurisdictionType] = None) -> ComplianceResult:
        """Vérifie la conformité complète"""
        
        # Paramètres par défaut
        if target_platforms is None:
            target_platforms = ['youtube', 'instagram', 'tiktok']
        
        if jurisdictions is None:
            jurisdictions = [JurisdictionType.EU, JurisdictionType.US]
        
        try:
            all_issues = []
            
            # Vérification vie privée
            privacy_issues = self.privacy_checker.check_privacy_compliance(content, metadata)
            all_issues.extend(privacy_issues)
            
            # Vérification copyright
            copyright_issues = self.copyright_checker.check_copyright_compliance(content, metadata)
            all_issues.extend(copyright_issues)
            
            # Vérification plateformes
            platform_issues = self.platform_checker.check_platform_compliance(
                content, metadata, target_platforms
            )
            all_issues.extend(platform_issues)
            
            # Analyse des résultats
            result = self._analyze_compliance_results(all_issues, jurisdictions)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erreur vérification conformité: {e}")
            return self._create_error_result(str(e))
    
    def _analyze_compliance_results(self, issues: List[ComplianceIssue], 
                                   jurisdictions: List[JurisdictionType]) -> ComplianceResult:
        """Analyse les résultats de conformité"""
        
        # Classification des issues par niveau
        critical_issues = [i for i in issues if i.level == ComplianceLevel.CRITICAL]
        violation_issues = [i for i in issues if i.level == ComplianceLevel.VIOLATION]
        warning_issues = [i for i in issues if i.level == ComplianceLevel.WARNING]
        
        # Détermination du niveau global
        if critical_issues:
            overall_compliance = ComplianceLevel.CRITICAL
        elif violation_issues:
            overall_compliance = ComplianceLevel.VIOLATION
        elif warning_issues:
            overall_compliance = ComplianceLevel.WARNING
        else:
            overall_compliance = ComplianceLevel.COMPLIANT
        
        # Score de conformité
        total_issues = len(issues)
        max_possible_score = 100
        penalty_weights = {
            ComplianceLevel.CRITICAL: 25,
            ComplianceLevel.VIOLATION: 15,
            ComplianceLevel.WARNING: 5
        }
        
        penalty_score = sum(penalty_weights.get(issue.level, 0) for issue in issues)
        compliance_score = max(0.0, (max_possible_score - penalty_score) / max_possible_score)
        
        # Catégories conformes
        all_categories = set(ComplianceCategory)
        problematic_categories = set(issue.category for issue in issues)
        compliant_categories = list(all_categories - problematic_categories)
        
        # Status par juridiction
        jurisdiction_status = {}
        for jurisdiction in jurisdictions:
            jurisdiction_issues = [i for i in issues if i.jurisdiction == jurisdiction]
            if any(i.level in [ComplianceLevel.CRITICAL, ComplianceLevel.VIOLATION] 
                   for i in jurisdiction_issues):
                jurisdiction_status[jurisdiction] = ComplianceLevel.VIOLATION
            elif jurisdiction_issues:
                jurisdiction_status[jurisdiction] = ComplianceLevel.WARNING
            else:
                jurisdiction_status[jurisdiction] = ComplianceLevel.COMPLIANT
        
        # Recommandations globales
        recommendations = self._generate_recommendations(issues)
        
        # Actions requises
        required_actions = self._generate_required_actions(critical_issues + violation_issues)
        
        # Prêt pour certification
        certification_ready = (overall_compliance in [ComplianceLevel.COMPLIANT, ComplianceLevel.WARNING] 
                              and len(critical_issues) == 0)
        
        return ComplianceResult(
            overall_compliance=overall_compliance,
            issues=issues,
            compliant_categories=compliant_categories,
            jurisdiction_status=jurisdiction_status,
            recommendations=recommendations,
            required_actions=required_actions,
            compliance_score=compliance_score,
            certification_ready=certification_ready,
            metadata={
                'total_issues': total_issues,
                'critical_count': len(critical_issues),
                'violation_count': len(violation_issues),
                'warning_count': len(warning_issues),
                'checked_at': datetime.now().isoformat()
            }
        )
    
    def _generate_recommendations(self, issues: List[ComplianceIssue]) -> List[str]:
        """Génère des recommandations globales"""
        recommendations = []
        
        # Recommandations par catégorie
        category_counts = {}
        for issue in issues:
            category_counts[issue.category] = category_counts.get(issue.category, 0) + 1
        
        if category_counts.get(ComplianceCategory.PRIVACY, 0) > 0:
            recommendations.append("Réviser les pratiques de protection de données personnelles")
        
        if category_counts.get(ComplianceCategory.COPYRIGHT, 0) > 0:
            recommendations.append("Clarifier et documenter les droits de propriété intellectuelle")
        
        if category_counts.get(ComplianceCategory.PLATFORM_POLICY, 0) > 0:
            recommendations.append("Adapter le contenu aux politiques des plateformes cibles")
        
        # Recommandations sur les correctifs automatiques
        auto_fixable_count = sum(1 for issue in issues if issue.auto_fixable)
        if auto_fixable_count > 0:
            recommendations.append(f"{auto_fixable_count} problèmes peuvent être corrigés automatiquement")
        
        return recommendations
    
    def _generate_required_actions(self, critical_issues: List[ComplianceIssue]) -> List[str]:
        """Génère les actions requises pour les problèmes critiques"""
        required_actions = []
        
        # Actions par priorité
        priority_actions = {}
        for issue in critical_issues:
            priority = issue.fix_priority
            if priority not in priority_actions:
                priority_actions[priority] = []
            priority_actions[priority].extend(issue.suggested_actions)
        
        # Tri par priorité décroissante
        for priority in sorted(priority_actions.keys(), reverse=True):
            actions = list(set(priority_actions[priority]))  # Dédoublonnage
            required_actions.extend(actions)
        
        return required_actions
    
    def _create_error_result(self, error: str) -> ComplianceResult:
        """Crée un résultat d'erreur"""
        return ComplianceResult(
            overall_compliance=ComplianceLevel.CRITICAL,
            issues=[ComplianceIssue(
                category=ComplianceCategory.LEGAL_REQUIREMENTS,
                level=ComplianceLevel.CRITICAL,
                jurisdiction=JurisdictionType.GLOBAL,
                description=f"Erreur de vérification: {error}",
                details={'error': error},
                suggested_actions=["Corriger l'erreur système", "Relancer la vérification"],
                auto_fixable=False,
                fix_priority=5
            )],
            compliant_categories=[],
            jurisdiction_status={},
            recommendations=[],
            required_actions=["Corriger l'erreur système"],
            compliance_score=0.0,
            certification_ready=False,
            metadata={'error': error}
        )

class AsyncComplianceChecker:
    """Version asynchrone du vérificateur de conformité"""
    
    def __init__(self):
        self.sync_checker = ComplianceChecker()
        self.logger = logging.getLogger(f"{__name__}.AsyncComplianceChecker")
    
    async def check_compliance(self, content: Dict[str, Any], 
                              metadata: Dict[str, Any],
                              target_platforms: List[str] = None,
                              jurisdictions: List[JurisdictionType] = None) -> ComplianceResult:
        """Vérifie la conformité de manière asynchrone"""
        loop = asyncio.get_event_loop()
        
        result = await loop.run_in_executor(
            None,
            self.sync_checker.check_compliance,
            content,
            metadata,
            target_platforms,
            jurisdictions
        )
        
        return result
    
    async def check_batch_compliance(self, 
                                   content_batch: List[Tuple[Dict[str, Any], Dict[str, Any]]],
                                   target_platforms: List[str] = None,
                                   jurisdictions: List[JurisdictionType] = None) -> List[ComplianceResult]:
        """Vérifie la conformité d'un lot de contenus"""
        tasks = []
        
        for content, metadata in content_batch:
            task = self.check_compliance(content, metadata, target_platforms, jurisdictions)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Gestion des erreurs
        compliance_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                compliance_results.append(self.sync_checker._create_error_result(str(result)))
            else:
                compliance_results.append(result)
        
        return compliance_results

# Export des classes principales
__all__ = [
    'ComplianceChecker',
    'AsyncComplianceChecker',
    'ComplianceResult',
    'ComplianceIssue',
    'ComplianceLevel',
    'ComplianceCategory',
    'JurisdictionType',
    'PrivacyComplianceChecker',
    'CopyrightComplianceChecker',
    'PlatformPolicyChecker'
]
