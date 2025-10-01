"""🛡️ Zero Trust Architecture - Continuous Verification Security
==============================================================

Architecture Zero Trust enterprise avec continuous verification,
micro-segmentation et least privilege enforcement.

Expert Team Implementation:
🤖 Lead Dev IA: Intelligent trust scoring + ML-based access decisions + adaptive policies
🏗️ Backend Senior: Scalable zero trust infrastructure + policy enforcement + performance
🧠 ML Engineer: Behavioral trust models + anomaly-based access control + risk prediction
🗄️ DBA: Identity database + audit trails + session management + trust analytics
🔒 Sécurité: Zero trust principles + continuous verification + security policies
🔗 Microservices: Service-to-service authentication + micro-segmentation + mesh security
🎵 Audio Engineer: Audio content access control + creator identity verification
⚙️ DevOps: Zero trust deployment + policy automation + continuous monitoring
🎨 IA Prompt Engineer: AI safety in zero trust + intelligent access recommendations

Author: Fahed Mlaiel (mlaiel@live.de)
Project: IA Chéries Integrations
Version: 1.0 Production
Date: Septembre 2024

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
"""

import asyncio
import logging
import json
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import ipaddress
import geoip2.database
from collections import defaultdict
import numpy as np
from sklearn.ensemble import IsolationForest


class TrustLevel(Enum):
    """Niveaux de confiance"""
    UNTRUSTED = "untrusted"
    LOW_TRUST = "low_trust"
    MEDIUM_TRUST = "medium_trust"
    HIGH_TRUST = "high_trust"
    VERIFIED_TRUST = "verified_trust"


class AccessDecision(Enum):
    """Décisions d'accès"""
    DENY = "deny"
    ALLOW = "allow"
    CONDITIONAL_ALLOW = "conditional_allow"
    STEP_UP_AUTH = "step_up_auth"
    REVIEW_REQUIRED = "review_required"


class VerificationType(Enum):
    """Types de vérification"""
    IDENTITY = "identity"
    DEVICE = "device"
    LOCATION = "location"
    BEHAVIOR = "behavior"
    CONTEXT = "context"
    BIOMETRIC = "biometric"


class NetworkSegment(Enum):
    """Segments réseau"""
    PUBLIC_DMZ = "public_dmz"
    CREATOR_ZONE = "creator_zone"
    ADMIN_ZONE = "admin_zone"
    API_GATEWAY = "api_gateway"
    DATABASE_TIER = "database_tier"
    ANALYTICS_ZONE = "analytics_zone"
    CONTENT_STORAGE = "content_storage"
    QUARANTINE = "quarantine"


@dataclass
class Identity:
    """Identité utilisateur/service"""
    identity_id: str
    identity_type: str  # user, service, device
    principal_name: str
    domain: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    roles: List[str] = field(default_factory=list)
    groups: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_verified: Optional[datetime] = None
    verification_level: int = 0  # 0-5 scale


@dataclass
class Device:
    """Appareil de l'utilisateur"""
    device_id: str
    device_type: str  # mobile, desktop, tablet, iot
    os_type: str
    os_version: str
    browser_type: Optional[str] = None
    browser_version: Optional[str] = None
    device_fingerprint: str = ""
    is_managed: bool = False
    is_compliant: bool = False
    trust_score: float = 0.0
    last_seen: datetime = field(default_factory=datetime.utcnow)
    security_posture: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AccessContext:
    """Contexte d'accès"""
    context_id: str
    identity: Identity
    device: Device
    source_ip: str
    location: Dict[str, Any]
    requested_resource: str
    requested_action: str
    timestamp: datetime
    session_context: Dict[str, Any] = field(default_factory=dict)
    risk_indicators: List[str] = field(default_factory=list)
    previous_access_pattern: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TrustScore:
    """Score de confiance"""
    overall_trust: float
    identity_trust: float
    device_trust: float
    location_trust: float
    behavior_trust: float
    context_trust: float
    verification_trust: float
    trust_factors: Dict[str, float]
    confidence_level: float
    calculated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AccessPolicy:
    """Politique d'accès"""
    policy_id: str
    name: str
    description: str
    resource_pattern: str
    conditions: List[Dict[str, Any]]
    required_trust_level: TrustLevel
    required_verifications: List[VerificationType]
    allowed_actions: List[str]
    network_restrictions: List[str] = field(default_factory=list)
    time_restrictions: Dict[str, Any] = field(default_factory=dict)
    priority: int = 100
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ZeroTrustDecision:
    """Décision Zero Trust"""
    decision_id: str
    access_context: AccessContext
    trust_score: TrustScore
    access_decision: AccessDecision
    allowed_actions: List[str]
    conditions: List[str]
    network_segment: NetworkSegment
    session_duration: int  # minutes
    monitoring_level: str
    justification: str
    policy_applied: str
    decision_timestamp: datetime = field(default_factory=datetime.utcnow)


class ContinuousIdentityVerifier:
    """
    🔐 Vérificateur d'identité continu
    =================================
    """
    
    def __init__(self):
        self.verification_cache = {}
        self.behavioral_models = {}
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        
    async def verify_identity_continuous(
        self,
        identity: Identity,
        access_context: AccessContext
    ) -> Dict[str, Any]:
        """Vérification continue de l'identité"""
        try:
            verification_result = {
                'identity_verified': False,
                'verification_level': 0,
                'trust_score': 0.0,
                'verification_methods': [],
                'risk_indicators': [],
                'next_verification_required': datetime.utcnow() + timedelta(hours=1)
            }
            
            # Vérification identité de base
            base_verification = await self._verify_base_identity(identity)
            verification_result.update(base_verification)
            
            # Vérification comportementale
            behavioral_verification = await self._verify_behavioral_patterns(
                identity, access_context
            )
            verification_result['behavior_score'] = behavioral_verification.get('trust_score', 0.0)
            
            # Vérification biométrique (si disponible)
            if access_context.device.security_posture.get('biometric_available', False):
                biometric_verification = await self._verify_biometric_identity(
                    identity, access_context
                )
                verification_result['biometric_score'] = biometric_verification.get('trust_score', 0.0)
                verification_result['verification_methods'].append('biometric')
            
            # Vérification multi-facteurs
            mfa_verification = await self._verify_multi_factor_auth(identity, access_context)
            verification_result['mfa_score'] = mfa_verification.get('trust_score', 0.0)
            
            # Score global de vérification identité
            identity_trust_score = self._calculate_identity_trust_score(
                base_verification,
                behavioral_verification,
                verification_result.get('biometric_score', 0.0),
                mfa_verification
            )
            
            verification_result['trust_score'] = identity_trust_score
            verification_result['identity_verified'] = identity_trust_score > 0.7
            
            # Mise à jour cache
            self.verification_cache[identity.identity_id] = verification_result
            
            return verification_result
            
        except Exception as e:
            logging.error(f"❌ Erreur vérification identité: {str(e)}")
            return {
                'identity_verified': False,
                'verification_level': 0,
                'trust_score': 0.0,
                'error': str(e)
            }
    
    async def _verify_base_identity(self, identity: Identity) -> Dict[str, Any]:
        """Vérification identité de base"""
        # Simulation vérification de base
        # En production: vérification contre annuaire, certificats, etc.
        
        verification_score = 0.5  # Base trust
        verification_methods = ['password']
        
        # Bonus pour identités vérifiées récemment
        if identity.last_verified and (datetime.utcnow() - identity.last_verified).seconds < 3600:
            verification_score += 0.2
            verification_methods.append('recent_verification')
        
        # Bonus pour niveau de vérification élevé
        verification_score += identity.verification_level * 0.1
        
        return {
            'base_trust_score': min(verification_score, 1.0),
            'verification_methods': verification_methods,
            'verification_level': identity.verification_level
        }
    
    async def _verify_behavioral_patterns(
        self,
        identity: Identity,
        access_context: AccessContext
    ) -> Dict[str, Any]:
        """Vérification patterns comportementaux"""
        try:
            # Features comportementales
            behavior_features = self._extract_behavioral_features(access_context)
            
            # Comparaison avec baseline comportemental
            user_baseline = self.behavioral_models.get(identity.identity_id, {})
            
            if user_baseline:
                # Calcul anomalie comportementale
                anomaly_score = self._calculate_behavioral_anomaly(
                    behavior_features, user_baseline
                )
                
                # Score confiance comportementale
                behavior_trust = max(1.0 - anomaly_score, 0.0)
            else:
                # Première connexion - confiance modérée
                behavior_trust = 0.6
                # Création baseline
                self.behavioral_models[identity.identity_id] = {
                    'baseline_features': behavior_features,
                    'access_patterns': [access_context.timestamp.hour],
                    'location_patterns': [access_context.location.get('country', 'unknown')]
                }
            
            return {
                'trust_score': behavior_trust,
                'anomaly_detected': behavior_trust < 0.5,
                'behavioral_features': behavior_features
            }
            
        except Exception as e:
            logging.error(f"❌ Erreur vérification comportementale: {str(e)}")
            return {'trust_score': 0.5, 'error': str(e)}
    
    def _extract_behavioral_features(self, access_context: AccessContext) -> List[float]:
        """Extraction features comportementales"""
        features = []
        
        # Feature temporelle (heure de la journée)
        features.append(access_context.timestamp.hour / 24.0)
        
        # Feature jour de la semaine
        features.append(access_context.timestamp.weekday() / 7.0)
        
        # Feature géographique (simulation)
        location = access_context.location
        country_code = location.get('country_code', 'US')
        # Conversion simple pays en numérique
        features.append(hash(country_code) % 100 / 100.0)
        
        # Feature device type
        device_type_mapping = {'mobile': 0.2, 'desktop': 0.5, 'tablet': 0.3, 'iot': 0.1}
        features.append(device_type_mapping.get(access_context.device.device_type, 0.5))
        
        # Feature resource demandée
        resource_hash = hash(access_context.requested_resource) % 100
        features.append(resource_hash / 100.0)
        
        return features
    
    def _calculate_behavioral_anomaly(
        self,
        current_features: List[float],
        baseline: Dict[str, Any]
    ) -> float:
        """Calcul anomalie comportementale"""
        try:
            baseline_features = baseline.get('baseline_features', [])
            
            if not baseline_features or len(baseline_features) != len(current_features):
                return 0.5  # Anomalie modérée si pas de baseline
            
            # Calcul distance euclidienne
            diff_squared = [(c - b) ** 2 for c, b in zip(current_features, baseline_features)]
            euclidean_distance = (sum(diff_squared)) ** 0.5
            
            # Normalisation (distance max possible avec features [0,1])
            max_distance = len(current_features) ** 0.5
            normalized_anomaly = euclidean_distance / max_distance
            
            return min(normalized_anomaly, 1.0)
            
        except Exception as e:
            logging.error(f"❌ Erreur calcul anomalie: {str(e)}")
            return 0.5
    
    async def _verify_biometric_identity(
        self,
        identity: Identity,
        access_context: AccessContext
    ) -> Dict[str, Any]:
        """Vérification identité biométrique"""
        # Simulation vérification biométrique
        # En production: intégration SDK biométrique
        
        biometric_score = 0.9  # Simulation haute confiance biométrique
        
        return {
            'trust_score': biometric_score,
            'biometric_type': 'fingerprint',
            'verification_successful': True
        }
    
    async def _verify_multi_factor_auth(
        self,
        identity: Identity,
        access_context: AccessContext
    ) -> Dict[str, Any]:
        """Vérification authentification multi-facteurs"""
        # Simulation MFA
        mfa_present = access_context.session_context.get('mfa_verified', False)
        
        if mfa_present:
            return {
                'trust_score': 0.95,
                'mfa_methods': ['totp', 'sms'],
                'mfa_verified': True
            }
        else:
            return {
                'trust_score': 0.3,
                'mfa_methods': [],
                'mfa_verified': False,
                'mfa_required': True
            }
    
    def _calculate_identity_trust_score(
        self,
        base_verification: Dict[str, Any],
        behavioral_verification: Dict[str, Any],
        biometric_score: float,
        mfa_verification: Dict[str, Any]
    ) -> float:
        """Calcul score confiance identité global"""
        # Pondération des différentes vérifications
        weights = {
            'base': 0.3,
            'behavioral': 0.25,
            'biometric': 0.25,
            'mfa': 0.2
        }
        
        scores = {
            'base': base_verification.get('base_trust_score', 0.0),
            'behavioral': behavioral_verification.get('trust_score', 0.0),
            'biometric': biometric_score,
            'mfa': mfa_verification.get('trust_score', 0.0)
        }
        
        # Score pondéré
        weighted_score = sum(scores[key] * weights[key] for key in weights.keys())
        
        return min(weighted_score, 1.0)


class MicroSegmentationEngine:
    """
    🔗 Moteur de micro-segmentation
    ==============================
    """
    
    def __init__(self):
        self.network_policies = {}
        self.segment_mappings = {}
        self._initialize_network_segments()
    
    def _initialize_network_segments(self):
        """Initialisation segments réseau"""
        self.segment_mappings = {
            # Segments par type d'utilisateur
            'creator': NetworkSegment.CREATOR_ZONE,
            'admin': NetworkSegment.ADMIN_ZONE,
            'api_client': NetworkSegment.API_GATEWAY,
            'public': NetworkSegment.PUBLIC_DMZ,
            'analytics': NetworkSegment.ANALYTICS_ZONE,
            
            # Segments par ressource
            'database': NetworkSegment.DATABASE_TIER,
            'content': NetworkSegment.CONTENT_STORAGE,
            'quarantine': NetworkSegment.QUARANTINE
        }
    
    async def determine_network_segment(
        self,
        access_context: AccessContext,
        trust_score: TrustScore
    ) -> NetworkSegment:
        """Détermination segment réseau approprié"""
        try:
            identity = access_context.identity
            device = access_context.device
            requested_resource = access_context.requested_resource
            
            # Segment basé sur confiance
            if trust_score.overall_trust < 0.3:
                return NetworkSegment.QUARANTINE
            
            # Segment basé sur rôle utilisateur
            if 'admin' in identity.roles:
                if trust_score.overall_trust > 0.8:
                    return NetworkSegment.ADMIN_ZONE
                else:
                    return NetworkSegment.PUBLIC_DMZ  # Admin avec faible confiance
            
            if 'creator' in identity.roles or 'content_creator' in identity.groups:
                return NetworkSegment.CREATOR_ZONE
            
            # Segment basé sur ressource demandée
            if '/api/' in requested_resource:
                return NetworkSegment.API_GATEWAY
            
            if '/analytics/' in requested_resource:
                if trust_score.overall_trust > 0.7:
                    return NetworkSegment.ANALYTICS_ZONE
                else:
                    return NetworkSegment.PUBLIC_DMZ
            
            if '/content/' in requested_resource:
                return NetworkSegment.CONTENT_STORAGE
            
            # Segment par défaut
            return NetworkSegment.PUBLIC_DMZ
            
        except Exception as e:
            logging.error(f"❌ Erreur détermination segment: {str(e)}")
            return NetworkSegment.QUARANTINE
    
    async def enforce_network_policies(
        self,
        source_segment: NetworkSegment,
        target_segment: NetworkSegment,
        access_context: AccessContext
    ) -> Dict[str, Any]:
        """Application politiques réseau"""
        try:
            policy_key = f"{source_segment.value}_{target_segment.value}"
            
            # Matrice de contrôle inter-segments
            segment_matrix = {
                # Depuis PUBLIC_DMZ
                f"{NetworkSegment.PUBLIC_DMZ.value}_{NetworkSegment.CREATOR_ZONE.value}": {
                    'allowed': True,
                    'conditions': ['authenticated', 'rate_limited'],
                    'monitoring': 'standard'
                },
                f"{NetworkSegment.PUBLIC_DMZ.value}_{NetworkSegment.ADMIN_ZONE.value}": {
                    'allowed': False,
                    'conditions': [],
                    'monitoring': 'high'
                },
                f"{NetworkSegment.PUBLIC_DMZ.value}_{NetworkSegment.DATABASE_TIER.value}": {
                    'allowed': False,
                    'conditions': [],
                    'monitoring': 'critical'
                },
                
                # Depuis CREATOR_ZONE
                f"{NetworkSegment.CREATOR_ZONE.value}_{NetworkSegment.CONTENT_STORAGE.value}": {
                    'allowed': True,
                    'conditions': ['authenticated', 'content_owner'],
                    'monitoring': 'standard'
                },
                f"{NetworkSegment.CREATOR_ZONE.value}_{NetworkSegment.DATABASE_TIER.value}": {
                    'allowed': True,
                    'conditions': ['authenticated', 'least_privilege'],
                    'monitoring': 'high'
                },
                
                # Depuis ADMIN_ZONE
                f"{NetworkSegment.ADMIN_ZONE.value}_{NetworkSegment.DATABASE_TIER.value}": {
                    'allowed': True,
                    'conditions': ['mfa_verified', 'admin_privileges'],
                    'monitoring': 'critical'
                },
                
                # Quarantine restrictions
                f"{NetworkSegment.QUARANTINE.value}_{NetworkSegment.PUBLIC_DMZ.value}": {
                    'allowed': True,
                    'conditions': ['security_review_passed'],
                    'monitoring': 'critical'
                }
            }
            
            policy = segment_matrix.get(policy_key, {
                'allowed': False,
                'conditions': ['explicit_approval_required'],
                'monitoring': 'critical'
            })
            
            # Vérification conditions
            conditions_met = await self._verify_policy_conditions(
                policy.get('conditions', []), access_context
            )
            
            return {
                'policy_decision': 'allow' if policy['allowed'] and conditions_met else 'deny',
                'policy_conditions': policy.get('conditions', []),
                'conditions_met': conditions_met,
                'monitoring_level': policy.get('monitoring', 'standard'),
                'enforcement_actions': self._generate_enforcement_actions(policy, conditions_met)
            }
            
        except Exception as e:
            logging.error(f"❌ Erreur application politique: {str(e)}")
            return {
                'policy_decision': 'deny',
                'error': str(e),
                'monitoring_level': 'critical'
            }
    
    async def _verify_policy_conditions(
        self,
        conditions: List[str],
        access_context: AccessContext
    ) -> bool:
        """Vérification conditions politique"""
        try:
            for condition in conditions:
                if condition == 'authenticated':
                    # Vérification authentification
                    if not access_context.session_context.get('authenticated', False):
                        return False
                
                elif condition == 'mfa_verified':
                    # Vérification MFA
                    if not access_context.session_context.get('mfa_verified', False):
                        return False
                
                elif condition == 'rate_limited':
                    # Vérification rate limiting (simulation)
                    # En production: intégration avec rate limiter
                    pass
                
                elif condition == 'content_owner':
                    # Vérification propriété contenu
                    # Simulation - vérification réelle nécessaire
                    if 'creator' not in access_context.identity.roles:
                        return False
                
                elif condition == 'admin_privileges':
                    # Vérification privilèges admin
                    if 'admin' not in access_context.identity.roles:
                        return False
                
                elif condition == 'least_privilege':
                    # Principe moindre privilège
                    # Vérification que l'accès est minimal nécessaire
                    pass
                
                elif condition == 'security_review_passed':
                    # Vérification review sécurité
                    # Pour sortie de quarantaine
                    return False  # Par défaut refuse jusqu'à review manuelle
            
            return True
            
        except Exception as e:
            logging.error(f"❌ Erreur vérification conditions: {str(e)}")
            return False
    
    def _generate_enforcement_actions(
        self,
        policy: Dict[str, Any],
        conditions_met: bool
    ) -> List[str]:
        """Génération actions d'application"""
        actions = []
        
        if not conditions_met:
            actions.extend([
                'log_access_violation',
                'increment_risk_score',
                'notify_security_team'
            ])
            
            if policy.get('monitoring') == 'critical':
                actions.append('immediate_security_review')
        
        if policy.get('monitoring') in ['high', 'critical']:
            actions.extend([
                'enhanced_logging',
                'real_time_monitoring'
            ])
        
        return actions


class ZeroTrustArchitecture:
    """
    🛡️ Architecture Zero Trust Enterprise
    ====================================
    
    Architecture complète avec continuous verification,
    micro-segmentation et least privilege enforcement.
    """
    
    def __init__(self):
        """Initialisation architecture Zero Trust"""
        self.logger = logging.getLogger(__name__)
        
        # Composants Zero Trust
        self.identity_verifier = ContinuousIdentityVerifier()
        self.segmentation_engine = MicroSegmentationEngine()
        
        # Politiques et cache
        self.access_policies = {}
        self.trust_cache = {}
        self.decision_history = defaultdict(list)
        
        # Configuration
        self.zt_config = {
            'default_trust_level': TrustLevel.UNTRUSTED,
            'trust_decay_hours': 4,
            'min_verification_interval': 300,  # 5 minutes
            'max_session_duration': 8,  # hours
            'anomaly_threshold': 0.7
        }
        
        # Initialisation politiques par défaut
        self._initialize_default_policies()
        
        self.logger.info("🛡️ Zero Trust Architecture initialisé")
    
    def _initialize_default_policies(self):
        """Initialisation politiques par défaut"""
        # Politique créateurs
        self.access_policies['creator_content_access'] = AccessPolicy(
            policy_id='creator_content_access',
            name='Creator Content Access',
            description='Access policy for creators to their content',
            resource_pattern='/api/creator/content/*',
            conditions=[
                {'type': 'identity_verified', 'required': True},
                {'type': 'device_trusted', 'required': True},
                {'type': 'creator_ownership', 'required': True}
            ],
            required_trust_level=TrustLevel.MEDIUM_TRUST,
            required_verifications=[VerificationType.IDENTITY, VerificationType.DEVICE],
            allowed_actions=['read', 'write', 'delete'],
            priority=200
        )
        
        # Politique admin
        self.access_policies['admin_system_access'] = AccessPolicy(
            policy_id='admin_system_access',
            name='Admin System Access',
            description='Administrative access to system resources',
            resource_pattern='/admin/*',
            conditions=[
                {'type': 'identity_verified', 'required': True},
                {'type': 'mfa_verified', 'required': True},
                {'type': 'admin_role', 'required': True},
                {'type': 'secure_location', 'required': True}
            ],
            required_trust_level=TrustLevel.HIGH_TRUST,
            required_verifications=[
                VerificationType.IDENTITY,
                VerificationType.DEVICE,
                VerificationType.LOCATION,
                VerificationType.BIOMETRIC
            ],
            allowed_actions=['read', 'write', 'admin'],
            time_restrictions={'business_hours_only': True},
            priority=100
        )
        
        # Politique publique
        self.access_policies['public_api_access'] = AccessPolicy(
            policy_id='public_api_access',
            name='Public API Access',
            description='Access to public API endpoints',
            resource_pattern='/api/public/*',
            conditions=[
                {'type': 'rate_limited', 'required': True}
            ],
            required_trust_level=TrustLevel.LOW_TRUST,
            required_verifications=[],
            allowed_actions=['read'],
            priority=300
        )
    
    async def evaluate_zero_trust_access(
        self,
        access_context: AccessContext
    ) -> ZeroTrustDecision:
        """
        🎯 Évaluation accès Zero Trust
        
        Args:
            access_context: Contexte d'accès complet
            
        Returns:
            ZeroTrustDecision: Décision d'accès Zero Trust
        """
        decision_id = str(uuid.uuid4())
        
        try:
            self.logger.info(
                f"🔍 Évaluation Zero Trust: {access_context.identity.principal_name} "
                f"-> {access_context.requested_resource}"
            )
            
            # 1. Vérification continue identité
            identity_verification = await self.identity_verifier.verify_identity_continuous(
                access_context.identity, access_context
            )
            
            # 2. Évaluation confiance device
            device_trust = await self._evaluate_device_trust(access_context.device)
            
            # 3. Évaluation confiance location
            location_trust = await self._evaluate_location_trust(access_context)
            
            # 4. Évaluation confiance context
            context_trust = await self._evaluate_context_trust(access_context)
            
            # 5. Calcul score confiance global
            trust_score = self._calculate_comprehensive_trust_score(
                identity_verification, device_trust, location_trust, context_trust
            )
            
            # 6. Sélection politique applicable
            applicable_policy = await self._select_applicable_policy(access_context)
            
            # 7. Évaluation conformité politique
            policy_compliance = await self._evaluate_policy_compliance(
                access_context, trust_score, applicable_policy
            )
            
            # 8. Détermination segment réseau
            network_segment = await self.segmentation_engine.determine_network_segment(
                access_context, trust_score
            )
            
            # 9. Décision d'accès finale
            access_decision, conditions = self._make_access_decision(
                trust_score, policy_compliance, access_context
            )
            
            # 10. Détermination actions surveillance
            monitoring_level = self._determine_monitoring_level(
                trust_score, access_decision, access_context
            )
            
            # 11. Calcul durée session
            session_duration = self._calculate_session_duration(
                trust_score, access_decision, applicable_policy
            )
            
            decision = ZeroTrustDecision(
                decision_id=decision_id,
                access_context=access_context,
                trust_score=trust_score,
                access_decision=access_decision,
                allowed_actions=self._determine_allowed_actions(
                    access_decision, applicable_policy, access_context
                ),
                conditions=conditions,
                network_segment=network_segment,
                session_duration=session_duration,
                monitoring_level=monitoring_level,
                justification=self._generate_decision_justification(
                    trust_score, policy_compliance, access_decision
                ),
                policy_applied=applicable_policy.policy_id if applicable_policy else 'default'
            )
            
            # Cache et historique
            self.trust_cache[access_context.identity.identity_id] = trust_score
            self.decision_history[access_context.identity.identity_id].append(decision)
            
            self.logger.info(
                f"✅ Décision Zero Trust: {access_decision.value} "
                f"(Trust: {trust_score.overall_trust:.2f}, Segment: {network_segment.value})"
            )
            
            return decision
            
        except Exception as e:
            self.logger.error(f"❌ Erreur évaluation Zero Trust: {str(e)}")
            
            # Décision par défaut sécurisée
            return ZeroTrustDecision(
                decision_id=decision_id,
                access_context=access_context,
                trust_score=TrustScore(
                    overall_trust=0.0,
                    identity_trust=0.0,
                    device_trust=0.0,
                    location_trust=0.0,
                    behavior_trust=0.0,
                    context_trust=0.0,
                    verification_trust=0.0,
                    trust_factors={},
                    confidence_level=0.0
                ),
                access_decision=AccessDecision.DENY,
                allowed_actions=[],
                conditions=[f"Error in evaluation: {str(e)}"],
                network_segment=NetworkSegment.QUARANTINE,
                session_duration=0,
                monitoring_level='critical',
                justification=f"Access denied due to evaluation error: {str(e)}",
                policy_applied='error_policy'
            )
    
    async def _evaluate_device_trust(self, device: Device) -> Dict[str, Any]:
        """Évaluation confiance device"""
        try:
            trust_factors = {}
            device_trust_score = 0.5  # Base trust
            
            # Device géré par organisation
            if device.is_managed:
                trust_factors['managed_device'] = 0.3
                device_trust_score += 0.3
            
            # Device conforme aux politiques
            if device.is_compliant:
                trust_factors['compliant_device'] = 0.2
                device_trust_score += 0.2
            
            # Device vu récemment
            time_since_last_seen = (datetime.utcnow() - device.last_seen).total_seconds()
            if time_since_last_seen < 3600:  # Moins d'1 heure
                trust_factors['recently_seen'] = 0.1
                device_trust_score += 0.1
            
            # Posture sécurité device
            security_posture = device.security_posture
            if security_posture.get('antivirus_active', False):
                trust_factors['antivirus_protection'] = 0.1
                device_trust_score += 0.1
            
            if security_posture.get('firewall_enabled', False):
                trust_factors['firewall_protection'] = 0.1
                device_trust_score += 0.1
            
            # OS récent
            if security_posture.get('os_up_to_date', False):
                trust_factors['updated_os'] = 0.1
                device_trust_score += 0.1
            
            # Fingerprint device cohérent
            if device.device_fingerprint and len(device.device_fingerprint) > 10:
                trust_factors['consistent_fingerprint'] = 0.1
                device_trust_score += 0.1
            
            return {
                'trust_score': min(device_trust_score, 1.0),
                'trust_factors': trust_factors,
                'risk_indicators': self._identify_device_risks(device)
            }
            
        except Exception as e:
            logging.error(f"❌ Erreur évaluation device: {str(e)}")
            return {'trust_score': 0.0, 'error': str(e)}
    
    def _identify_device_risks(self, device: Device) -> List[str]:
        """Identification risques device"""
        risks = []
        
        if not device.is_managed:
            risks.append("Unmanaged device")
        
        if not device.is_compliant:
            risks.append("Non-compliant device")
        
        security_posture = device.security_posture
        if not security_posture.get('antivirus_active', True):
            risks.append("No antivirus protection")
        
        if not security_posture.get('firewall_enabled', True):
            risks.append("Firewall disabled")
        
        if not security_posture.get('os_up_to_date', True):
            risks.append("Outdated operating system")
        
        # Device type risks
        if device.device_type == 'iot':
            risks.append("IoT device - inherent security risks")
        
        return risks
    
    async def _evaluate_location_trust(self, access_context: AccessContext) -> Dict[str, Any]:
        """Évaluation confiance location"""
        try:
            location = access_context.location
            location_trust_score = 0.5  # Base trust
            trust_factors = {}
            
            # Location connue/habituelle
            user_locations = self._get_user_historical_locations(
                access_context.identity.identity_id
            )
            current_country = location.get('country_code', 'unknown')
            
            if current_country in user_locations:
                trust_factors['known_location'] = 0.3
                location_trust_score += 0.3
            
            # Location considérée sûre
            safe_countries = ['US', 'CA', 'GB', 'DE', 'FR', 'AU', 'JP']
            if current_country in safe_countries:
                trust_factors['safe_jurisdiction'] = 0.2
                location_trust_score += 0.2
            
            # IP reputation
            ip_reputation = await self._check_ip_reputation(access_context.source_ip)
            if ip_reputation > 0.8:
                trust_factors['good_ip_reputation'] = 0.2
                location_trust_score += 0.2
            elif ip_reputation < 0.3:
                trust_factors['bad_ip_reputation'] = -0.3
                location_trust_score -= 0.3
            
            # VPN/Proxy detection (simulation)
            if self._is_vpn_or_proxy(access_context.source_ip):
                trust_factors['vpn_proxy_detected'] = -0.2
                location_trust_score -= 0.2
            
            return {
                'trust_score': max(min(location_trust_score, 1.0), 0.0),
                'trust_factors': trust_factors,
                'location_risk_indicators': self._identify_location_risks(location)
            }
            
        except Exception as e:
            logging.error(f"❌ Erreur évaluation location: {str(e)}")
            return {'trust_score': 0.3, 'error': str(e)}
    
    def _get_user_historical_locations(self, identity_id: str) -> List[str]:
        """Récupération locations historiques utilisateur"""
        # Simulation - en production: base de données historique
        return ['US', 'CA', 'FR']
    
    async def _check_ip_reputation(self, ip_address: str) -> float:
        """Vérification réputation IP"""
        # Simulation - en production: API threat intelligence
        try:
            ip = ipaddress.ip_address(ip_address)
            if ip.is_private:
                return 0.8  # IP privée = généralement sûre
            elif ip.is_loopback:
                return 1.0  # Localhost
            else:
                return 0.7  # IP publique - réputation moyenne
        except:
            return 0.3  # IP invalide
    
    def _is_vpn_or_proxy(self, ip_address: str) -> bool:
        """Détection VPN/Proxy"""
        # Simulation - en production: service de détection VPN
        return False
    
    def _identify_location_risks(self, location: Dict[str, Any]) -> List[str]:
        """Identification risques location"""
        risks = []
        
        # Pays à haut risque
        high_risk_countries = ['CN', 'RU', 'IR', 'KP']
        country_code = location.get('country_code', 'unknown')
        
        if country_code in high_risk_countries:
            risks.append(f"Access from high-risk country: {country_code}")
        
        if country_code == 'unknown':
            risks.append("Unable to determine location")
        
        return risks
    
    async def _evaluate_context_trust(self, access_context: AccessContext) -> Dict[str, Any]:
        """Évaluation confiance contextuelle"""
        try:
            context_trust_score = 0.5
            trust_factors = {}
            
            # Heure d'accès
            current_hour = access_context.timestamp.hour
            if 9 <= current_hour <= 17:  # Heures ouvrables
                trust_factors['business_hours'] = 0.2
                context_trust_score += 0.2
            elif current_hour < 6 or current_hour > 22:  # Heures inhabituelles
                trust_factors['unusual_hours'] = -0.2
                context_trust_score -= 0.2
            
            # Type de ressource demandée
            resource = access_context.requested_resource
            if '/admin/' in resource:
                trust_factors['admin_resource_access'] = -0.1
                context_trust_score -= 0.1
            elif '/api/public/' in resource:
                trust_factors['public_resource_access'] = 0.1
                context_trust_score += 0.1
            
            # Session context
            session_context = access_context.session_context
            if session_context.get('authentication_method') == 'sso':
                trust_factors['sso_authentication'] = 0.1
                context_trust_score += 0.1
            
            # Patterns d'accès précédents
            previous_pattern = access_context.previous_access_pattern
            if previous_pattern.get('consistent_pattern', False):
                trust_factors['consistent_behavior'] = 0.2
                context_trust_score += 0.2
            
            return {
                'trust_score': max(min(context_trust_score, 1.0), 0.0),
                'trust_factors': trust_factors
            }
            
        except Exception as e:
            logging.error(f"❌ Erreur évaluation context: {str(e)}")
            return {'trust_score': 0.5, 'error': str(e)}
    
    def _calculate_comprehensive_trust_score(
        self,
        identity_verification: Dict[str, Any],
        device_trust: Dict[str, Any],
        location_trust: Dict[str, Any],
        context_trust: Dict[str, Any]
    ) -> TrustScore:
        """Calcul score confiance global"""
        try:
            # Pondération des différents facteurs
            weights = {
                'identity': 0.35,
                'device': 0.25,
                'location': 0.20,
                'context': 0.20
            }
            
            # Scores individuels
            identity_trust = identity_verification.get('trust_score', 0.0)
            device_trust_score = device_trust.get('trust_score', 0.0)
            location_trust_score = location_trust.get('trust_score', 0.0)
            context_trust_score = context_trust.get('trust_score', 0.0)
            
            # Score global pondéré
            overall_trust = (
                identity_trust * weights['identity'] +
                device_trust_score * weights['device'] +
                location_trust_score * weights['location'] +
                context_trust_score * weights['context']
            )
            
            # Facteurs de confiance consolidés
            trust_factors = {}
            trust_factors.update(identity_verification.get('trust_factors', {}))
            trust_factors.update(device_trust.get('trust_factors', {}))
            trust_factors.update(location_trust.get('trust_factors', {}))
            trust_factors.update(context_trust.get('trust_factors', {}))
            
            # Calcul niveau confiance
            confidence_level = min(
                identity_verification.get('confidence', 0.5),
                0.9  # Confiance maximale
            )
            
            return TrustScore(
                overall_trust=overall_trust,
                identity_trust=identity_trust,
                device_trust=device_trust_score,
                location_trust=location_trust_score,
                behavior_trust=identity_verification.get('behavior_score', 0.0),
                context_trust=context_trust_score,
                verification_trust=identity_verification.get('verification_level', 0) / 5.0,
                trust_factors=trust_factors,
                confidence_level=confidence_level
            )
            
        except Exception as e:
            logging.error(f"❌ Erreur calcul trust score: {str(e)}")
            return TrustScore(
                overall_trust=0.0,
                identity_trust=0.0,
                device_trust=0.0,
                location_trust=0.0,
                behavior_trust=0.0,
                context_trust=0.0,
                verification_trust=0.0,
                trust_factors={},
                confidence_level=0.0
            )
    
    async def _select_applicable_policy(
        self,
        access_context: AccessContext
    ) -> Optional[AccessPolicy]:
        """Sélection politique applicable"""
        try:
            matching_policies = []
            
            for policy in self.access_policies.values():
                if not policy.enabled:
                    continue
                
                # Vérification pattern ressource
                if self._matches_resource_pattern(
                    access_context.requested_resource, 
                    policy.resource_pattern
                ):
                    matching_policies.append(policy)
            
            # Tri par priorité (plus faible = plus prioritaire)
            matching_policies.sort(key=lambda p: p.priority)
            
            return matching_policies[0] if matching_policies else None
            
        except Exception as e:
            logging.error(f"❌ Erreur sélection politique: {str(e)}")
            return None
    
    def _matches_resource_pattern(self, resource: str, pattern: str) -> bool:
        """Vérification correspondance pattern ressource"""
        # Conversion pattern simple avec wildcards
        import re
        regex_pattern = pattern.replace('*', '.*').replace('?', '.')
        return bool(re.match(regex_pattern, resource))
    
    async def _evaluate_policy_compliance(
        self,
        access_context: AccessContext,
        trust_score: TrustScore,
        policy: Optional[AccessPolicy]
    ) -> Dict[str, Any]:
        """Évaluation conformité politique"""
        if not policy:
            return {
                'compliant': False,
                'reason': 'No applicable policy found',
                'missing_requirements': []
            }
        
        try:
            compliance_result = {
                'compliant': True,
                'policy_id': policy.policy_id,
                'missing_requirements': [],
                'conditions_met': []
            }
            
            # Vérification niveau confiance requis
            required_trust_level = self._trust_level_to_score(policy.required_trust_level)
            if trust_score.overall_trust < required_trust_level:
                compliance_result['compliant'] = False
                compliance_result['missing_requirements'].append(
                    f"Insufficient trust level: {trust_score.overall_trust:.2f} < {required_trust_level}"
                )
            
            # Vérification vérifications requises
            for verification_type in policy.required_verifications:
                if not self._is_verification_satisfied(verification_type, access_context, trust_score):
                    compliance_result['compliant'] = False
                    compliance_result['missing_requirements'].append(
                        f"Missing verification: {verification_type.value}"
                    )
            
            # Vérification conditions spécifiques
            for condition in policy.conditions:
                condition_met = await self._evaluate_policy_condition(condition, access_context)
                if condition['required'] and not condition_met:
                    compliance_result['compliant'] = False
                    compliance_result['missing_requirements'].append(
                        f"Condition not met: {condition['type']}"
                    )
                elif condition_met:
                    compliance_result['conditions_met'].append(condition['type'])
            
            # Vérification restrictions temporelles
            if policy.time_restrictions:
                time_compliance = self._check_time_restrictions(
                    policy.time_restrictions, access_context.timestamp
                )
                if not time_compliance:
                    compliance_result['compliant'] = False
                    compliance_result['missing_requirements'].append("Outside allowed time window")
            
            return compliance_result
            
        except Exception as e:
            logging.error(f"❌ Erreur évaluation conformité: {str(e)}")
            return {
                'compliant': False,
                'reason': f"Evaluation error: {str(e)}",
                'missing_requirements': [str(e)]
            }
    
    def _trust_level_to_score(self, trust_level: TrustLevel) -> float:
        """Conversion niveau confiance en score"""
        mapping = {
            TrustLevel.UNTRUSTED: 0.0,
            TrustLevel.LOW_TRUST: 0.3,
            TrustLevel.MEDIUM_TRUST: 0.6,
            TrustLevel.HIGH_TRUST: 0.8,
            TrustLevel.VERIFIED_TRUST: 0.95
        }
        return mapping.get(trust_level, 0.0)
    
    def _is_verification_satisfied(
        self,
        verification_type: VerificationType,
        access_context: AccessContext,
        trust_score: TrustScore
    ) -> bool:
        """Vérification si type de vérification satisfait"""
        if verification_type == VerificationType.IDENTITY:
            return trust_score.identity_trust > 0.7
        elif verification_type == VerificationType.DEVICE:
            return trust_score.device_trust > 0.6
        elif verification_type == VerificationType.LOCATION:
            return trust_score.location_trust > 0.5
        elif verification_type == VerificationType.BEHAVIOR:
            return trust_score.behavior_trust > 0.6
        elif verification_type == VerificationType.BIOMETRIC:
            return access_context.session_context.get('biometric_verified', False)
        else:
            return False
    
    async def _evaluate_policy_condition(
        self,
        condition: Dict[str, Any],
        access_context: AccessContext
    ) -> bool:
        """Évaluation condition politique"""
        condition_type = condition.get('type')
        
        if condition_type == 'identity_verified':
            return access_context.session_context.get('authenticated', False)
        
        elif condition_type == 'device_trusted':
            return access_context.device.is_managed and access_context.device.is_compliant
        
        elif condition_type == 'mfa_verified':
            return access_context.session_context.get('mfa_verified', False)
        
        elif condition_type == 'admin_role':
            return 'admin' in access_context.identity.roles
        
        elif condition_type == 'creator_ownership':
            # Simulation - vérification propriété contenu
            return 'creator' in access_context.identity.roles
        
        elif condition_type == 'secure_location':
            # Définition location sécurisée
            return access_context.location.get('country_code') in ['US', 'CA', 'GB', 'DE', 'FR']
        
        elif condition_type == 'rate_limited':
            # Simulation rate limiting
            return True  # Assume rate limit OK
        
        else:
            return False
    
    def _check_time_restrictions(
        self,
        time_restrictions: Dict[str, Any],
        timestamp: datetime
    ) -> bool:
        """Vérification restrictions temporelles"""
        if time_restrictions.get('business_hours_only', False):
            hour = timestamp.hour
            weekday = timestamp.weekday()
            
            # Lundi-Vendredi, 9h-17h
            if weekday < 5 and 9 <= hour <= 17:
                return True
            else:
                return False
        
        return True
    
    def _make_access_decision(
        self,
        trust_score: TrustScore,
        policy_compliance: Dict[str, Any],
        access_context: AccessContext
    ) -> tuple[AccessDecision, List[str]]:
        """Décision d'accès finale"""
        conditions = []
        
        # Si politique non respectée
        if not policy_compliance.get('compliant', False):
            missing_reqs = policy_compliance.get('missing_requirements', [])
            
            # Vérifier si step-up auth peut résoudre
            if any('verification' in req.lower() or 'mfa' in req.lower() for req in missing_reqs):
                conditions.extend([
                    "Additional authentication required",
                    "Complete MFA verification"
                ])
                return AccessDecision.STEP_UP_AUTH, conditions
            
            # Sinon, refus
            conditions.extend(missing_reqs)
            return AccessDecision.DENY, conditions
        
        # Décision basée sur confiance
        if trust_score.overall_trust >= 0.8:
            return AccessDecision.ALLOW, ["High trust level - full access granted"]
        
        elif trust_score.overall_trust >= 0.6:
            conditions.extend([
                "Medium trust level - conditional access",
                "Enhanced monitoring active",
                "Limited session duration"
            ])
            return AccessDecision.CONDITIONAL_ALLOW, conditions
        
        elif trust_score.overall_trust >= 0.4:
            conditions.extend([
                "Low trust level - additional verification required",
                "Step-up authentication needed"
            ])
            return AccessDecision.STEP_UP_AUTH, conditions
        
        else:
            conditions.extend([
                "Very low trust level - access denied",
                "Manual review required"
            ])
            return AccessDecision.DENY, conditions
    
    def _determine_monitoring_level(
        self,
        trust_score: TrustScore,
        access_decision: AccessDecision,
        access_context: AccessContext
    ) -> str:
        """Détermination niveau surveillance"""
        if access_decision == AccessDecision.DENY:
            return 'critical'
        
        if trust_score.overall_trust < 0.5:
            return 'high'
        
        if '/admin/' in access_context.requested_resource:
            return 'high'
        
        if access_decision == AccessDecision.CONDITIONAL_ALLOW:
            return 'medium'
        
        return 'standard'
    
    def _calculate_session_duration(
        self,
        trust_score: TrustScore,
        access_decision: AccessDecision,
        policy: Optional[AccessPolicy]
    ) -> int:
        """Calcul durée session"""
        base_duration = self.zt_config['max_session_duration']  # hours
        
        if access_decision == AccessDecision.DENY:
            return 0
        
        # Ajustement basé sur confiance
        trust_multiplier = trust_score.overall_trust
        adjusted_duration = int(base_duration * trust_multiplier)
        
        # Minimum 1 heure, maximum configuré
        return max(min(adjusted_duration, base_duration), 1)
    
    def _determine_allowed_actions(
        self,
        access_decision: AccessDecision,
        policy: Optional[AccessPolicy],
        access_context: AccessContext
    ) -> List[str]:
        """Détermination actions autorisées"""
        if access_decision == AccessDecision.DENY:
            return []
        
        if not policy:
            return ['read']  # Action minimale par défaut
        
        allowed_actions = policy.allowed_actions.copy()
        
        # Restrictions basées sur décision
        if access_decision == AccessDecision.CONDITIONAL_ALLOW:
            # Limitation actions sensibles
            if 'admin' in allowed_actions:
                allowed_actions.remove('admin')
            if 'delete' in allowed_actions:
                allowed_actions.remove('delete')
        
        return allowed_actions
    
    def _generate_decision_justification(
        self,
        trust_score: TrustScore,
        policy_compliance: Dict[str, Any],
        access_decision: AccessDecision
    ) -> str:
        """Génération justification décision"""
        justification_parts = []
        
        justification_parts.append(
            f"Trust Score: {trust_score.overall_trust:.2f} "
            f"(Identity: {trust_score.identity_trust:.2f}, "
            f"Device: {trust_score.device_trust:.2f}, "
            f"Location: {trust_score.location_trust:.2f})"
        )
        
        if policy_compliance.get('compliant', False):
            justification_parts.append("Policy compliance: PASSED")
        else:
            missing_reqs = policy_compliance.get('missing_requirements', [])
            justification_parts.append(f"Policy compliance: FAILED - {', '.join(missing_reqs[:2])}")
        
        justification_parts.append(f"Decision: {access_decision.value}")
        
        return " | ".join(justification_parts)


# Export classes principales
__all__ = [
    'ZeroTrustArchitecture',
    'ZeroTrustDecision',
    'TrustScore',
    'AccessContext',
    'Identity',
    'Device',
    'AccessPolicy',
    'TrustLevel',
    'AccessDecision',
    'VerificationType',
    'NetworkSegment',
    'ContinuousIdentityVerifier',
    'MicroSegmentationEngine'
]