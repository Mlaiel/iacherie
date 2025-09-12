#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ Session Security Validator - Validateur Sécurité Sessions Enterprise
========================================================================

Validateur enterprise de sécurité sessions avec détection avancée des menaces,
validation multi-facteurs et protection contre les attaques sophistiquées.

**Rôles Experts:**
- **Sécurité**: Validation sécurité, détection menaces, protection attaques
- **Lead Dev IA**: IA détection anomalies et patterns suspects
- **Backend Senior**: Architecture validation haute performance
- **DevOps**: Monitoring sécurité et alertes automatisées

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
import json
import hashlib
import hmac
import secrets
from typing import Dict, Any, Optional, List, Union, Set, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta, timezone
import yaml
import aioredis
from collections import defaultdict, deque
import ipaddress
import re
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import geoip2.database
import user_agents

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """Niveaux sécurité session"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ThreatType(Enum):
    """Types de menaces"""
    SESSION_HIJACKING = "session_hijacking"
    CSRF_ATTACK = "csrf_attack"
    XSS_ATTEMPT = "xss_attempt"
    BRUTE_FORCE = "brute_force"
    ANOMALOUS_BEHAVIOR = "anomalous_behavior"
    GEO_ANOMALY = "geo_anomaly"
    DEVICE_MISMATCH = "device_mismatch"
    CONCURRENT_ABUSE = "concurrent_abuse"
    TIME_ANOMALY = "time_anomaly"

class ValidationResult(Enum):
    """Résultats validation"""
    VALID = "valid"
    SUSPICIOUS = "suspicious"
    BLOCKED = "blocked"
    REQUIRES_MFA = "requires_mfa"
    RATE_LIMITED = "rate_limited"

@dataclass
class SecurityContext:
    """Contexte sécurité session"""
    session_id: str
    user_id: Optional[str]
    ip_address: str
    user_agent: str
    timestamp: datetime
    geolocation: Optional[Dict[str, Any]] = None
    device_fingerprint: Optional[str] = None
    csrf_token: Optional[str] = None
    mfa_verified: bool = False
    security_level: SecurityLevel = SecurityLevel.MEDIUM

@dataclass
class ThreatEvent:
    """Événement menace sécurité"""
    event_id: str
    threat_type: ThreatType
    session_id: str
    user_id: Optional[str]
    ip_address: str
    severity: float  # 0.0 - 1.0
    confidence: float  # 0.0 - 1.0
    timestamp: datetime
    details: Dict[str, Any] = field(default_factory=dict)
    actions_taken: List[str] = field(default_factory=list)

@dataclass
class SecurityMetrics:
    """Métriques sécurité"""
    total_validations: int = 0
    valid_sessions: int = 0
    suspicious_sessions: int = 0
    blocked_sessions: int = 0
    threats_detected: int = 0
    false_positives: int = 0
    average_validation_time: float = 0.0
    threat_distribution: Dict[str, int] = field(default_factory=lambda: defaultdict(int))

class SessionSecurityValidator:
    """
    🛡️ Validateur Sécurité Sessions Enterprise
    
    **Sécurité**: Validation multi-niveaux et protection attaques avancées
    **Lead Dev IA**: Détection IA anomalies et apprentissage patterns
    **Backend Senior**: Architecture validation haute performance
    **DevOps**: Monitoring automatisé et alertes temps réel
    """
    
    def __init__(self, redis_pool, config: Optional[Dict[str, Any]] = None):
        self.redis_pool = redis_pool
        self.config = config or self._get_default_config()
        
        # Stockage validations et menaces
        self.active_sessions: Dict[str, SecurityContext] = {}
        self.threat_events: Dict[str, ThreatEvent] = {}
        self.blocked_ips: Set[str] = set()
        self.trusted_ips: Set[str] = set()
        
        # Modèles IA détection anomalies
        self.anomaly_detector: Optional[IsolationForest] = None
        self.scaler: Optional[StandardScaler] = None
        self.behavioral_patterns: deque = deque(maxlen=10000)
        
        # Rate limiting
        self.rate_limiters: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Métriques
        self.metrics = SecurityMetrics()
        self.security_history: deque = deque(maxlen=5000)
        
        # Géolocalisation (optionnel)
        self.geoip_reader = None
        try:
            # En production, utiliser une vraie base GeoIP
            pass  # self.geoip_reader = geoip2.database.Reader('GeoLite2-City.mmdb')
        except:
            pass
        
        # CSRF tokens storage
        self.csrf_tokens: Dict[str, datetime] = {}
        
        # Validators personnalisés
        self.custom_validators: List[Callable] = []
        
        # Tâches background
        self.cleanup_task: Optional[asyncio.Task] = None
        self.ml_training_task: Optional[asyncio.Task] = None
        
        logger.info("🛡️ Session Security Validator initialisé")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """**Sécurité**: Configuration sécurité par défaut**"""
        return {
            'enable_anomaly_detection': True,
            'enable_geolocation_check': True,
            'enable_device_fingerprinting': True,
            'enable_rate_limiting': True,
            'max_login_attempts': 5,
            'lockout_duration': 300,  # 5 minutes
            'session_timeout': 3600,  # 1 heure
            'csrf_token_ttl': 300,  # 5 minutes
            'suspicious_threshold': 0.7,
            'blocking_threshold': 0.9,
            'rate_limit_window': 300,  # 5 minutes
            'rate_limit_max_requests': 100,
            'enable_ip_whitelist': True,
            'enable_ip_blacklist': True,
            'geo_anomaly_threshold': 1000,  # km
            'time_anomaly_threshold': 3600,  # secondes
            'concurrent_session_limit': 5,
            'ml_retraining_interval': 3600,  # 1 heure
            'cleanup_interval': 300,  # 5 minutes
            'threat_retention_days': 30
        }
    
    async def start_background_services(self):
        """**DevOps**: Démarrage services sécurité background"""
        
        # Initialisation modèle IA
        if self.config.get('enable_anomaly_detection'):
            await self._initialize_ml_models()
        
        # Tâche nettoyage
        if not self.cleanup_task or self.cleanup_task.done():
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        # Tâche entraînement ML
        if not self.ml_training_task or self.ml_training_task.done():
            self.ml_training_task = asyncio.create_task(self._ml_training_loop())
        
        logger.info("🚀 Services sécurité background démarrés")
    
    async def stop_background_services(self):
        """**DevOps**: Arrêt services background"""
        
        tasks = [self.cleanup_task, self.ml_training_task]
        
        for task in tasks:
            if task and not task.done():
                task.cancel()
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.info("🛑 Services sécurité background arrêtés")
    
    async def _initialize_ml_models(self):
        """**Lead Dev IA**: Initialisation modèles ML détection anomalies"""
        try:
            self.anomaly_detector = IsolationForest(
                contamination=0.1,  # 10% d'anomalies attendues
                random_state=42,
                n_estimators=100
            )
            self.scaler = StandardScaler()
            
            # Entraînement initial avec données simulées
            await self._train_initial_models()
            
            logger.info("✅ Modèles ML sécurité initialisés")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation ML sécurité: {e}")
    
    async def _train_initial_models(self):
        """**Lead Dev IA**: Entraînement initial modèles avec données simulées"""
        try:
            # Génération données d'entraînement normales
            n_samples = 2000
            normal_features = []
            
            for _ in range(n_samples):
                # Features: hour, day_week, session_duration, request_rate, geo_distance
                hour = np.random.normal(14, 4) % 24  # Centré sur 14h
                day_week = np.random.randint(0, 7)
                session_duration = np.random.exponential(1800)  # 30 min moyenne
                request_rate = np.random.gamma(2, 2)  # Requêtes par minute
                geo_distance = np.random.exponential(50)  # Distance en km
                device_consistency = np.random.uniform(0.8, 1.0)  # Score cohérence device
                
                normal_features.append([
                    hour, day_week, session_duration, 
                    request_rate, geo_distance, device_consistency
                ])
            
            # Ajout données anomaliques
            anomaly_features = []
            for _ in range(200):  # 10% anomalies
                hour = np.random.uniform(0, 24)
                day_week = np.random.randint(0, 7)
                session_duration = np.random.uniform(0, 100)  # Sessions très courtes
                request_rate = np.random.uniform(20, 100)  # Taux élevé
                geo_distance = np.random.uniform(5000, 20000)  # Distance importante
                device_consistency = np.random.uniform(0.0, 0.3)  # Cohérence faible
                
                anomaly_features.append([
                    hour, day_week, session_duration,
                    request_rate, geo_distance, device_consistency
                ])
            
            # Combinaison et entraînement
            all_features = normal_features + anomaly_features
            features_scaled = self.scaler.fit_transform(all_features)
            self.anomaly_detector.fit(features_scaled)
            
            logger.info("🎯 Modèles ML sécurité entraînés")
            
        except Exception as e:
            logger.error(f"❌ Erreur entraînement ML: {e}")
    
    async def validate_session_security(
        self,
        session_id: str,
        user_id: Optional[str],
        ip_address: str,
        user_agent: str,
        csrf_token: Optional[str] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Tuple[ValidationResult, Optional[ThreatEvent]]:
        """**Sécurité**: Validation sécurité session complète"""
        
        start_time = time.time()
        
        try:
            # Création contexte sécurité
            security_context = SecurityContext(
                session_id=session_id,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                timestamp=datetime.now(timezone.utc),
                csrf_token=csrf_token
            )
            
            # Enrichissement contexte
            await self._enrich_security_context(security_context, additional_context)
            
            # Validations multi-niveaux
            validation_results = []
            threat_events = []
            
            # 1. Validation IP
            ip_result, ip_threat = await self._validate_ip_address(security_context)
            validation_results.append(ip_result)
            if ip_threat:
                threat_events.append(ip_threat)
            
            # 2. Validation géolocalisation
            if self.config.get('enable_geolocation_check'):
                geo_result, geo_threat = await self._validate_geolocation(security_context)
                validation_results.append(geo_result)
                if geo_threat:
                    threat_events.append(geo_threat)
            
            # 3. Validation device fingerprint
            if self.config.get('enable_device_fingerprinting'):
                device_result, device_threat = await self._validate_device_fingerprint(security_context)
                validation_results.append(device_result)
                if device_threat:
                    threat_events.append(device_threat)
            
            # 4. Validation CSRF
            if csrf_token:
                csrf_result, csrf_threat = await self._validate_csrf_token(security_context)
                validation_results.append(csrf_result)
                if csrf_threat:
                    threat_events.append(csrf_threat)
            
            # 5. Rate limiting
            if self.config.get('enable_rate_limiting'):
                rate_result, rate_threat = await self._validate_rate_limit(security_context)
                validation_results.append(rate_result)
                if rate_threat:
                    threat_events.append(rate_threat)
            
            # 6. Détection anomalies IA
            if self.config.get('enable_anomaly_detection') and self.anomaly_detector:
                anomaly_result, anomaly_threat = await self._detect_anomalies(security_context)
                validation_results.append(anomaly_result)
                if anomaly_threat:
                    threat_events.append(anomaly_threat)
            
            # 7. Validateurs personnalisés
            for validator in self.custom_validators:
                try:
                    custom_result = await validator(security_context)
                    if custom_result:
                        validation_results.append(custom_result)
                except Exception as e:
                    logger.warning(f"⚠️ Erreur validateur personnalisé: {e}")
            
            # Calcul résultat final
            final_result, primary_threat = self._calculate_final_validation_result(
                validation_results, threat_events
            )
            
            # Stockage contexte
            self.active_sessions[session_id] = security_context
            
            # Mise à jour métriques
            await self._update_security_metrics(final_result, start_time)
            
            # Actions selon résultat
            await self._take_security_actions(final_result, primary_threat, security_context)
            
            logger.debug(f"🔍 Validation sécurité {session_id}: {final_result.value}")
            
            return final_result, primary_threat
            
        except Exception as e:
            logger.error(f"❌ Erreur validation sécurité {session_id}: {e}")
            return ValidationResult.BLOCKED, None
    
    async def _enrich_security_context(
        self, 
        context: SecurityContext, 
        additional: Optional[Dict[str, Any]]
    ):
        """**Lead Dev IA**: Enrichissement contexte sécurité**"""
        
        # Géolocalisation IP
        if self.geoip_reader:
            try:
                response = self.geoip_reader.city(context.ip_address)
                context.geolocation = {
                    'country': response.country.name,
                    'city': response.city.name,
                    'latitude': float(response.location.latitude),
                    'longitude': float(response.location.longitude)
                }
            except:
                pass
        
        # Device fingerprint
        context.device_fingerprint = self._generate_device_fingerprint(
            context.user_agent, context.ip_address
        )
        
        # Données additionnelles
        if additional:
            context.security_level = SecurityLevel(
                additional.get('security_level', SecurityLevel.MEDIUM.value)
            )
            context.mfa_verified = additional.get('mfa_verified', False)
    
    def _generate_device_fingerprint(self, user_agent: str, ip_address: str) -> str:
        """**Sécurité**: Génération empreinte device"""
        
        # Parsing user agent
        try:
            ua = user_agents.parse(user_agent)
            fingerprint_data = f"{ua.browser.family}:{ua.browser.version_string}:{ua.os.family}:{ua.device.family}"
        except:
            fingerprint_data = user_agent
        
        # Ajout subnet IP (pour tolérance changements IP mineurs)
        try:
            ip = ipaddress.ip_address(ip_address)
            if ip.version == 4:
                subnet = str(ipaddress.ip_network(f"{ip}/24", strict=False))
            else:
                subnet = str(ipaddress.ip_network(f"{ip}/64", strict=False))
            fingerprint_data += f":{subnet}"
        except:
            fingerprint_data += f":{ip_address}"
        
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()[:16]
    
    async def _validate_ip_address(self, context: SecurityContext) -> Tuple[ValidationResult, Optional[ThreatEvent]]:
        """**Sécurité**: Validation adresse IP"""
        
        # Vérification blacklist
        if context.ip_address in self.blocked_ips:
            threat = ThreatEvent(
                event_id=f"ip_blocked_{int(time.time())}",
                threat_type=ThreatType.BRUTE_FORCE,
                session_id=context.session_id,
                user_id=context.user_id,
                ip_address=context.ip_address,
                severity=1.0,
                confidence=1.0,
                timestamp=context.timestamp,
                details={'reason': 'IP in blacklist'}
            )
            return ValidationResult.BLOCKED, threat
        
        # Vérification whitelist
        if context.ip_address in self.trusted_ips:
            return ValidationResult.VALID, None
        
        # Vérification plages privées/publiques
        try:
            ip = ipaddress.ip_address(context.ip_address)
            if ip.is_private or ip.is_loopback:
                # IPs privées - validation moins stricte
                return ValidationResult.VALID, None
        except:
            pass
        
        return ValidationResult.VALID, None
    
    async def _validate_geolocation(self, context: SecurityContext) -> Tuple[ValidationResult, Optional[ThreatEvent]]:
        """**Lead Dev IA**: Validation géolocalisation intelligente"""
        
        if not context.geolocation or not context.user_id:
            return ValidationResult.VALID, None
        
        # Récupération localisation précédente utilisateur
        previous_location = await self._get_user_previous_location(context.user_id)
        
        if not previous_location:
            # Première connexion ou pas d'historique
            await self._store_user_location(context.user_id, context.geolocation)
            return ValidationResult.VALID, None
        
        # Calcul distance
        distance_km = self._calculate_geo_distance(
            previous_location, context.geolocation
        )
        
        threshold = self.config.get('geo_anomaly_threshold', 1000)
        
        if distance_km > threshold:
            threat = ThreatEvent(
                event_id=f"geo_anomaly_{int(time.time())}",
                threat_type=ThreatType.GEO_ANOMALY,
                session_id=context.session_id,
                user_id=context.user_id,
                ip_address=context.ip_address,
                severity=min(1.0, distance_km / 10000),  # Proportionnel distance
                confidence=0.8,
                timestamp=context.timestamp,
                details={
                    'distance_km': distance_km,
                    'previous_location': previous_location,
                    'current_location': context.geolocation
                }
            )
            
            # Mise à jour localisation si validée ultérieurement
            await self._store_user_location(context.user_id, context.geolocation)
            
            return ValidationResult.SUSPICIOUS, threat
        
        # Mise à jour localisation normale
        await self._store_user_location(context.user_id, context.geolocation)
        return ValidationResult.VALID, None
    
    def _calculate_geo_distance(self, loc1: Dict[str, Any], loc2: Dict[str, Any]) -> float:
        """**Lead Dev IA**: Calcul distance géographique"""
        
        try:
            lat1, lon1 = loc1['latitude'], loc1['longitude']
            lat2, lon2 = loc2['latitude'], loc2['longitude']
            
            # Formule haversine
            R = 6371  # Rayon Terre en km
            
            dlat = np.radians(lat2 - lat1)
            dlon = np.radians(lon2 - lon1)
            
            a = (np.sin(dlat/2)**2 + 
                 np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2)
            
            c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
            distance = R * c
            
            return distance
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur calcul distance géo: {e}")
            return 0.0
    
    async def _validate_device_fingerprint(self, context: SecurityContext) -> Tuple[ValidationResult, Optional[ThreatEvent]]:
        """**Sécurité**: Validation empreinte device"""
        
        if not context.device_fingerprint or not context.user_id:
            return ValidationResult.VALID, None
        
        # Récupération empreintes utilisateur connues
        known_fingerprints = await self._get_user_fingerprints(context.user_id)
        
        if not known_fingerprints:
            # Premier device
            await self._store_user_fingerprint(context.user_id, context.device_fingerprint)
            return ValidationResult.VALID, None
        
        # Vérification correspondance
        if context.device_fingerprint in known_fingerprints:
            return ValidationResult.VALID, None
        
        # Nouveau device - suspicious mais pas bloqué
        threat = ThreatEvent(
            event_id=f"device_new_{int(time.time())}",
            threat_type=ThreatType.DEVICE_MISMATCH,
            session_id=context.session_id,
            user_id=context.user_id,
            ip_address=context.ip_address,
            severity=0.6,
            confidence=0.7,
            timestamp=context.timestamp,
            details={
                'new_fingerprint': context.device_fingerprint,
                'known_fingerprints': list(known_fingerprints)[:5]  # Limité pour logs
            }
        )
        
        # Ajout nouveau fingerprint avec validation MFA recommandée
        await self._store_user_fingerprint(context.user_id, context.device_fingerprint)
        
        return ValidationResult.REQUIRES_MFA, threat
    
    async def _validate_csrf_token(self, context: SecurityContext) -> Tuple[ValidationResult, Optional[ThreatEvent]]:
        """**Sécurité**: Validation token CSRF"""
        
        if not context.csrf_token:
            return ValidationResult.VALID, None  # Token optionnel
        
        # Vérification existence et validité
        token_timestamp = self.csrf_tokens.get(context.csrf_token)
        
        if not token_timestamp:
            threat = ThreatEvent(
                event_id=f"csrf_invalid_{int(time.time())}",
                threat_type=ThreatType.CSRF_ATTACK,
                session_id=context.session_id,
                user_id=context.user_id,
                ip_address=context.ip_address,
                severity=0.8,
                confidence=0.9,
                timestamp=context.timestamp,
                details={'invalid_token': context.csrf_token[:10]}
            )
            return ValidationResult.SUSPICIOUS, threat
        
        # Vérification expiration
        ttl = self.config.get('csrf_token_ttl', 300)
        if (context.timestamp - token_timestamp).total_seconds() > ttl:
            # Token expiré
            del self.csrf_tokens[context.csrf_token]
            
            threat = ThreatEvent(
                event_id=f"csrf_expired_{int(time.time())}",
                threat_type=ThreatType.CSRF_ATTACK,
                session_id=context.session_id,
                user_id=context.user_id,
                ip_address=context.ip_address,
                severity=0.6,
                confidence=0.8,
                timestamp=context.timestamp,
                details={'expired_token': context.csrf_token[:10]}
            )
            return ValidationResult.SUSPICIOUS, threat
        
        # Token valide - suppression après usage
        del self.csrf_tokens[context.csrf_token]
        return ValidationResult.VALID, None
    
    async def _validate_rate_limit(self, context: SecurityContext) -> Tuple[ValidationResult, Optional[ThreatEvent]]:
        """**Sécurité**: Validation rate limiting"""
        
        current_time = context.timestamp
        window = self.config.get('rate_limit_window', 300)
        max_requests = self.config.get('rate_limit_max_requests', 100)
        
        # Clé rate limiting (par IP)
        rate_key = context.ip_address
        
        # Nettoyage anciennes entrées
        cutoff_time = current_time - timedelta(seconds=window)
        rate_history = self.rate_limiters[rate_key]
        
        while rate_history and rate_history[0] < cutoff_time:
            rate_history.popleft()
        
        # Vérification limite
        if len(rate_history) >= max_requests:
            threat = ThreatEvent(
                event_id=f"rate_limit_{int(time.time())}",
                threat_type=ThreatType.BRUTE_FORCE,
                session_id=context.session_id,
                user_id=context.user_id,
                ip_address=context.ip_address,
                severity=0.7,
                confidence=0.9,
                timestamp=context.timestamp,
                details={
                    'requests_count': len(rate_history),
                    'window_seconds': window,
                    'max_allowed': max_requests
                }
            )
            return ValidationResult.RATE_LIMITED, threat
        
        # Ajout requête actuelle
        rate_history.append(current_time)
        
        return ValidationResult.VALID, None
    
    async def _detect_anomalies(self, context: SecurityContext) -> Tuple[ValidationResult, Optional[ThreatEvent]]:
        """**Lead Dev IA**: Détection anomalies via IA"""
        
        if not self.anomaly_detector or not self.scaler:
            return ValidationResult.VALID, None
        
        try:
            # Extraction features pour ML
            features = await self._extract_ml_features(context)
            
            if not features:
                return ValidationResult.VALID, None
            
            # Prédiction anomalie
            features_scaled = self.scaler.transform([features])
            anomaly_score = self.anomaly_detector.decision_function(features_scaled)[0]
            is_anomaly = self.anomaly_detector.predict(features_scaled)[0] == -1
            
            # Conversion score en confiance
            confidence = min(1.0, abs(anomaly_score))
            
            if is_anomaly and confidence > self.config.get('suspicious_threshold', 0.7):
                threat = ThreatEvent(
                    event_id=f"anomaly_{int(time.time())}",
                    threat_type=ThreatType.ANOMALOUS_BEHAVIOR,
                    session_id=context.session_id,
                    user_id=context.user_id,
                    ip_address=context.ip_address,
                    severity=confidence,
                    confidence=confidence,
                    timestamp=context.timestamp,
                    details={
                        'anomaly_score': anomaly_score,
                        'features': features,
                        'ml_model': 'isolation_forest'
                    }
                )
                
                # Enregistrement pattern pour apprentissage
                self.behavioral_patterns.append({
                    'features': features,
                    'timestamp': context.timestamp.timestamp(),
                    'anomaly': True,
                    'confidence': confidence
                })
                
                result = ValidationResult.BLOCKED if confidence > self.config.get('blocking_threshold', 0.9) else ValidationResult.SUSPICIOUS
                return result, threat
            
            # Pattern normal - enregistrement pour apprentissage
            self.behavioral_patterns.append({
                'features': features,
                'timestamp': context.timestamp.timestamp(),
                'anomaly': False,
                'confidence': 1.0 - confidence
            })
            
            return ValidationResult.VALID, None
            
        except Exception as e:
            logger.error(f"❌ Erreur détection anomalies IA: {e}")
            return ValidationResult.VALID, None
    
    async def _extract_ml_features(self, context: SecurityContext) -> Optional[List[float]]:
        """**Lead Dev IA**: Extraction features ML**"""
        
        try:
            current_time = context.timestamp
            
            # Features temporelles
            hour = current_time.hour
            day_week = current_time.weekday()
            
            # Features session
            session_age = 0.0  # Calculé si session existante
            request_rate = len(self.rate_limiters.get(context.ip_address, []))
            
            # Features géo
            geo_distance = 0.0
            if context.geolocation and context.user_id:
                prev_location = await self._get_user_previous_location(context.user_id)
                if prev_location:
                    geo_distance = self._calculate_geo_distance(prev_location, context.geolocation)
            
            # Features device
            device_consistency = 1.0  # Score cohérence device
            if context.user_id:
                known_fingerprints = await self._get_user_fingerprints(context.user_id)
                if known_fingerprints and context.device_fingerprint not in known_fingerprints:
                    device_consistency = 0.3
            
            return [hour, day_week, session_age, request_rate, geo_distance, device_consistency]
            
        except Exception as e:
            logger.error(f"❌ Erreur extraction features ML: {e}")
            return None
    
    def _calculate_final_validation_result(
        self,
        results: List[ValidationResult],
        threats: List[ThreatEvent]
    ) -> Tuple[ValidationResult, Optional[ThreatEvent]]:
        """**Sécurité**: Calcul résultat final validation**"""
        
        # Priorité: BLOCKED > RATE_LIMITED > REQUIRES_MFA > SUSPICIOUS > VALID
        priority = {
            ValidationResult.BLOCKED: 5,
            ValidationResult.RATE_LIMITED: 4,
            ValidationResult.REQUIRES_MFA: 3,
            ValidationResult.SUSPICIOUS: 2,
            ValidationResult.VALID: 1
        }
        
        # Résultat avec priorité maximale
        final_result = max(results, key=lambda r: priority[r])
        
        # Menace principale (plus sévère)
        primary_threat = None
        if threats:
            primary_threat = max(threats, key=lambda t: t.severity)
        
        return final_result, primary_threat
    
    async def _take_security_actions(
        self,
        result: ValidationResult,
        threat: Optional[ThreatEvent],
        context: SecurityContext
    ):
        """**Sécurité**: Actions sécurité selon résultat**"""
        
        actions_taken = []
        
        if result == ValidationResult.BLOCKED:
            # Blocage IP temporaire
            self.blocked_ips.add(context.ip_address)
            actions_taken.append("ip_blocked")
            
            # Invalidation sessions utilisateur si applicable
            if context.user_id:
                actions_taken.append("user_sessions_invalidated")
        
        elif result == ValidationResult.RATE_LIMITED:
            # Logging détaillé pour rate limiting
            actions_taken.append("rate_limited")
        
        elif result == ValidationResult.REQUIRES_MFA:
            # Marquer pour MFA requis
            actions_taken.append("mfa_required")
        
        elif result == ValidationResult.SUSPICIOUS:
            # Monitoring renforcé
            actions_taken.append("enhanced_monitoring")
        
        # Enregistrement threat si présent
        if threat:
            threat.actions_taken = actions_taken
            self.threat_events[threat.event_id] = threat
            
            # Notification si sévérité élevée
            if threat.severity > 0.8:
                await self._send_security_alert(threat)
    
    async def _send_security_alert(self, threat: ThreatEvent):
        """**DevOps**: Envoi alerte sécurité"""
        
        alert_data = {
            'threat_type': threat.threat_type.value,
            'severity': threat.severity,
            'session_id': threat.session_id,
            'user_id': threat.user_id,
            'ip_address': threat.ip_address,
            'timestamp': threat.timestamp.isoformat(),
            'details': threat.details
        }
        
        # En production: intégration avec système alertes (Slack, email, etc.)
        logger.warning(f"🚨 ALERTE SÉCURITÉ: {threat.threat_type.value} - {alert_data}")
    
    async def generate_csrf_token(self, session_id: str) -> str:
        """**Sécurité**: Génération token CSRF sécurisé"""
        
        token = secrets.token_urlsafe(32)
        self.csrf_tokens[token] = datetime.now(timezone.utc)
        
        logger.debug(f"🔐 Token CSRF généré pour session {session_id}")
        return token
    
    def add_custom_validator(self, validator: Callable):
        """**Backend Senior**: Ajout validateur personnalisé"""
        self.custom_validators.append(validator)
        logger.info("🔧 Validateur personnalisé ajouté")
    
    def add_trusted_ip(self, ip_address: str):
        """**Sécurité**: Ajout IP de confiance"""
        self.trusted_ips.add(ip_address)
        logger.info(f"✅ IP ajoutée à whitelist: {ip_address}")
    
    def remove_trusted_ip(self, ip_address: str):
        """**Sécurité**: Suppression IP de confiance"""
        self.trusted_ips.discard(ip_address)
        logger.info(f"❌ IP supprimée de whitelist: {ip_address}")
    
    def block_ip(self, ip_address: str, duration_seconds: int = None):
        """**Sécurité**: Blocage IP manuel"""
        self.blocked_ips.add(ip_address)
        
        if duration_seconds:
            # Planifier déblocage automatique
            asyncio.create_task(self._auto_unblock_ip(ip_address, duration_seconds))
        
        logger.info(f"🚫 IP bloquée: {ip_address}")
    
    async def _auto_unblock_ip(self, ip_address: str, duration: int):
        """**DevOps**: Déblocage automatique IP"""
        await asyncio.sleep(duration)
        self.blocked_ips.discard(ip_address)
        logger.info(f"🔓 IP débloquée automatiquement: {ip_address}")
    
    async def _get_user_previous_location(self, user_id: str) -> Optional[Dict[str, Any]]:
        """**DBA**: Récupération localisation précédente utilisateur"""
        try:
            async with self.redis_pool.get_connection() as redis_conn:
                location_data = await redis_conn.get(f"user_location:{user_id}")
                if location_data:
                    return json.loads(location_data)
        except Exception as e:
            logger.error(f"❌ Erreur récupération localisation {user_id}: {e}")
        return None
    
    async def _store_user_location(self, user_id: str, location: Dict[str, Any]):
        """**DBA**: Stockage localisation utilisateur"""
        try:
            async with self.redis_pool.get_connection() as redis_conn:
                await redis_conn.setex(
                    f"user_location:{user_id}",
                    86400,  # 24h
                    json.dumps(location)
                )
        except Exception as e:
            logger.error(f"❌ Erreur stockage localisation {user_id}: {e}")
    
    async def _get_user_fingerprints(self, user_id: str) -> Set[str]:
        """**DBA**: Récupération empreintes utilisateur"""
        try:
            async with self.redis_pool.get_connection() as redis_conn:
                fingerprints = await redis_conn.smembers(f"user_fingerprints:{user_id}")
                return set(fingerprints) if fingerprints else set()
        except Exception as e:
            logger.error(f"❌ Erreur récupération fingerprints {user_id}: {e}")
            return set()
    
    async def _store_user_fingerprint(self, user_id: str, fingerprint: str):
        """**DBA**: Stockage empreinte utilisateur"""
        try:
            async with self.redis_pool.get_connection() as redis_conn:
                await redis_conn.sadd(f"user_fingerprints:{user_id}", fingerprint)
                await redis_conn.expire(f"user_fingerprints:{user_id}", 2592000)  # 30 jours
        except Exception as e:
            logger.error(f"❌ Erreur stockage fingerprint {user_id}: {e}")
    
    async def _update_security_metrics(self, result: ValidationResult, start_time: float):
        """**DevOps**: Mise à jour métriques sécurité"""
        
        self.metrics.total_validations += 1
        execution_time = (time.time() - start_time) * 1000  # ms
        
        # Mise à jour temps moyen
        self.metrics.average_validation_time = (
            self.metrics.average_validation_time * (self.metrics.total_validations - 1) +
            execution_time
        ) / self.metrics.total_validations
        
        # Compteurs par résultat
        if result == ValidationResult.VALID:
            self.metrics.valid_sessions += 1
        elif result == ValidationResult.SUSPICIOUS:
            self.metrics.suspicious_sessions += 1
        elif result == ValidationResult.BLOCKED:
            self.metrics.blocked_sessions += 1
    
    async def _cleanup_loop(self):
        """**DevOps**: Boucle nettoyage données anciennes"""
        while True:
            try:
                await self._cleanup_old_data()
                interval = self.config.get('cleanup_interval', 300)
                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"❌ Erreur nettoyage sécurité: {e}")
                await asyncio.sleep(60)
    
    async def _cleanup_old_data(self):
        """**DevOps**: Nettoyage données anciennes**"""
        current_time = datetime.now(timezone.utc)
        
        # Nettoyage CSRF tokens expirés
        ttl = self.config.get('csrf_token_ttl', 300)
        expired_tokens = [
            token for token, timestamp in self.csrf_tokens.items()
            if (current_time - timestamp).total_seconds() > ttl
        ]
        
        for token in expired_tokens:
            del self.csrf_tokens[token]
        
        # Nettoyage threats anciens
        retention_days = self.config.get('threat_retention_days', 30)
        cutoff_time = current_time - timedelta(days=retention_days)
        
        expired_threats = [
            event_id for event_id, threat in self.threat_events.items()
            if threat.timestamp < cutoff_time
        ]
        
        for event_id in expired_threats:
            del self.threat_events[event_id]
        
        if expired_tokens or expired_threats:
            logger.debug(f"🧹 Nettoyage sécurité: {len(expired_tokens)} tokens, {len(expired_threats)} threats")
    
    async def _ml_training_loop(self):
        """**Lead Dev IA**: Boucle re-entraînement ML**"""
        while True:
            try:
                await self._retrain_ml_models()
                interval = self.config.get('ml_retraining_interval', 3600)
                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"❌ Erreur re-entraînement ML: {e}")
                await asyncio.sleep(300)
    
    async def _retrain_ml_models(self):
        """**Lead Dev IA**: Re-entraînement modèles ML**"""
        
        if not self.anomaly_detector or len(self.behavioral_patterns) < 100:
            return
        
        try:
            # Préparation données récentes
            recent_patterns = list(self.behavioral_patterns)[-1000:]  # 1000 derniers
            
            features = [p['features'] for p in recent_patterns]
            
            # Re-entraînement
            features_scaled = self.scaler.fit_transform(features)
            self.anomaly_detector.fit(features_scaled)
            
            logger.info("🔄 Modèles ML sécurité re-entraînés")
            
        except Exception as e:
            logger.error(f"❌ Erreur re-entraînement ML: {e}")
    
    async def get_security_analytics(self) -> Dict[str, Any]:
        """**DevOps**: Analytics sécurité détaillées"""
        
        # Distribution threats
        threat_dist = defaultdict(int)
        threat_severities = []
        
        for threat in self.threat_events.values():
            threat_dist[threat.threat_type.value] += 1
            threat_severities.append(threat.severity)
        
        avg_severity = np.mean(threat_severities) if threat_severities else 0
        
        # Top IPs problématiques
        ip_threat_count = defaultdict(int)
        for threat in self.threat_events.values():
            ip_threat_count[threat.ip_address] += 1
        
        top_threat_ips = sorted(
            ip_threat_count.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            'global_metrics': {
                'total_validations': self.metrics.total_validations,
                'valid_sessions': self.metrics.valid_sessions,
                'suspicious_sessions': self.metrics.suspicious_sessions,
                'blocked_sessions': self.metrics.blocked_sessions,
                'validation_success_rate': self.metrics.valid_sessions / max(1, self.metrics.total_validations),
                'threats_detected': len(self.threat_events),
                'average_validation_time_ms': self.metrics.average_validation_time
            },
            'threat_analysis': {
                'by_type': dict(threat_dist),
                'average_severity': avg_severity,
                'high_severity_count': len([t for t in self.threat_events.values() if t.severity > 0.8]),
                'top_threat_ips': top_threat_ips
            },
            'security_state': {
                'blocked_ips_count': len(self.blocked_ips),
                'trusted_ips_count': len(self.trusted_ips),
                'active_sessions': len(self.active_sessions),
                'csrf_tokens_active': len(self.csrf_tokens)
            },
            'ml_status': {
                'anomaly_detection_enabled': self.anomaly_detector is not None,
                'behavioral_patterns_count': len(self.behavioral_patterns),
                'model_last_trained': 'recent'  # Timestamp réel en production
            },
            'recent_threats': [
                {
                    'type': threat.threat_type.value,
                    'severity': threat.severity,
                    'ip': threat.ip_address,
                    'timestamp': threat.timestamp.isoformat()
                }
                for threat in sorted(
                    self.threat_events.values(),
                    key=lambda t: t.timestamp,
                    reverse=True
                )[:20]
            ],
            'configuration': {
                'anomaly_detection': self.config.get('enable_anomaly_detection'),
                'geolocation_check': self.config.get('enable_geolocation_check'),
                'device_fingerprinting': self.config.get('enable_device_fingerprinting'),
                'rate_limiting': self.config.get('enable_rate_limiting'),
                'suspicious_threshold': self.config.get('suspicious_threshold'),
                'blocking_threshold': self.config.get('blocking_threshold')
            }
        }

# Factory function
async def create_session_security_validator(redis_pool, config: Optional[Dict[str, Any]] = None):
    """**Sécurité**: Factory création validateur sécurité sessions"""
    validator = SessionSecurityValidator(redis_pool, config)
    await validator.start_background_services()
    return validator

if __name__ == "__main__":
    async def demo():
        """Démonstration Session Security Validator"""
        
        # Configuration Redis simulée
        class MockRedisPool:
            def get_connection(self):
                from unittest.mock import AsyncMock
                mock = AsyncMock()
                mock.get.return_value = None
                mock.setex.return_value = True
                mock.sadd.return_value = 1
                mock.smembers.return_value = set()
                return mock
        
        # Création validator
        validator = await create_session_security_validator(MockRedisPool())
        
        # Test validation normale
        result, threat = await validator.validate_session_security(
            session_id="test_session_123",
            user_id="user456",
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        
        print(f"Validation normale: {result.value}")
        
        # Test avec IP suspecte
        result, threat = await validator.validate_session_security(
            session_id="suspicious_session",
            user_id="user789",
            ip_address="1.2.3.4",  # IP externe
            user_agent="curl/7.68.0"  # User agent automatisé
        )
        
        print(f"Validation suspecte: {result.value}")
        if threat:
            print(f"Menace détectée: {threat.threat_type.value}")
        
        # Analytics
        analytics = await validator.get_security_analytics()
        print(f"Analytics sécurité: {analytics}")
        
        # Nettoyage
        await validator.stop_background_services()
    
    asyncio.run(demo())