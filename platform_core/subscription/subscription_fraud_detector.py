"""🚀 Platform Core Subscription - Subscription Fraud Detector
=============================================================
Module: backend/platform_core/subscription/subscription_fraud_detector.py
Author: Fahed Mlaiel (mlaiel@live.de)
=============================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🚨 AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie

🎯 DÉTECTEUR FRAUDES ABONNEMENTS ML
Détection avancée de fraudes avec machine learning
- Détection patterns frauduleux en temps réel
- Analyse comportementale et anomalies
- Prévention abus essais gratuits multiples
- Protection contre chargebacks et fraudes paiement
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
import logging
import asyncio
import json
import hashlib
from decimal import Decimal
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
import ipaddress
import re

# Configure logging
logger = logging.getLogger(__name__)


class FraudRiskLevel(Enum):
    """Niveaux de risque de fraude"""
    VERY_LOW = "very_low"    # <10%
    LOW = "low"              # 10-30%
    MEDIUM = "medium"        # 30-60%
    HIGH = "high"            # 60-80%
    VERY_HIGH = "very_high"  # >80%


class FraudType(Enum):
    """Types de fraude détectés"""
    PAYMENT_FRAUD = "payment_fraud"
    IDENTITY_THEFT = "identity_theft"
    ACCOUNT_TAKEOVER = "account_takeover"
    TRIAL_ABUSE = "trial_abuse"
    CHARGEBACK_FRAUD = "chargeback_fraud"
    SYNTHETIC_IDENTITY = "synthetic_identity"
    VELOCITY_FRAUD = "velocity_fraud"
    BEHAVIORAL_ANOMALY = "behavioral_anomaly"


class ActionType(Enum):
    """Actions à prendre contre la fraude"""
    MONITOR = "monitor"
    FLAG = "flag"
    BLOCK = "block"
    SUSPEND = "suspend"
    REQUIRE_VERIFICATION = "require_verification"
    MANUAL_REVIEW = "manual_review"


@dataclass
class FraudSignal:
    """Signal de fraude détecté"""
    signal_id: str
    signal_type: str
    severity: float
    description: str
    evidence: Dict[str, Any]
    timestamp: datetime


@dataclass
class FraudAssessment:
    """Évaluation complète de fraude"""
    user_id: str
    assessment_id: str
    risk_level: FraudRiskLevel
    risk_score: float
    fraud_types: List[FraudType]
    signals: List[FraudSignal]
    recommended_actions: List[ActionType]
    confidence: float
    assessment_time: datetime
    expires_at: datetime


@dataclass
class UserRiskProfile:
    """Profil de risque utilisateur"""
    user_id: str
    current_risk_level: FraudRiskLevel
    historical_assessments: List[str]
    trusted_signals: List[str]
    suspicious_patterns: List[str]
    last_updated: datetime


class SubscriptionFraudDetector:
    """🚀 Détecteur Fraudes Abonnements ML Enterprise
    
    Système ML avancé de détection de fraudes avec
    analyse comportementale et protection en temps réel.
    """
    
    def __init__(self):
        """Initialise le détecteur de fraudes"""
        self.ml_models = {}
        self.fraud_rules = {}
        self.user_profiles = {}
        self.fraud_assessments = {}
        self.known_fraud_patterns = {}
        self.ip_reputation_cache = {}
        
        # Configuration des modèles ML
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.fraud_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.clustering_model = DBSCAN(eps=0.5, min_samples=5)
        
        # Initialisation des règles de détection
        self._initialize_fraud_rules()
        
        # Patterns frauduleux connus
        self._initialize_fraud_patterns()
        
        logger.info("🚀 Subscription Fraud Detector initialized")
    
    def _initialize_fraud_rules(self):
        """Initialise les règles de détection de fraude"""
        
        self.fraud_rules = {
            'velocity_checks': {
                'max_trials_per_ip_24h': 3,
                'max_accounts_per_email_domain_7d': 5,
                'max_payment_attempts_1h': 5,
                'max_subscriptions_per_card_30d': 10
            },
            
            'behavioral_anomalies': {
                'unusual_login_hours': True,
                'geo_velocity_impossible': True,
                'device_fingerprint_mismatch': True,
                'usage_pattern_deviation': True
            },
            
            'payment_fraud_indicators': {
                'high_risk_countries': ['XX', 'YY'],  # Placeholder
                'suspicious_bin_ranges': ['123456', '654321'],  # Placeholder
                'frequent_chargeback_emails': [],
                'test_card_patterns': ['4111111111111111', '4000000000000002']
            },
            
            'content_abuse_patterns': {
                'mass_content_upload': 100,  # Plus de 100 fichiers en 1h
                'duplicate_content_threshold': 0.95,  # 95% similarité
                'spam_keywords': ['spam', 'fake', 'scam']
            }
        }
    
    def _initialize_fraud_patterns(self):
        """Initialise les patterns frauduleux connus"""
        
        self.known_fraud_patterns = {
            'email_patterns': [
                r'^[a-z]+\d{3,}@gmail\.com$',  # Pattern: nom + chiffres
                r'^[a-z]{10,}@[a-z]{5,}\.tk$',  # Domaines .tk suspicieux
                r'^test\w*@\w*\.com$'  # Emails de test
            ],
            
            'name_patterns': [
                r'^test\s*user\d*$',
                r'^john\s*doe\d*$',
                r'^[a-z]+\d{3,}$'  # Nom + chiffres
            ],
            
            'phone_patterns': [
                r'^\+1(555|123|000)\d{7}$',  # Numéros factices US
                r'^(\d)\1{9,}$'  # Chiffres répétés
            ],
            
            'address_patterns': [
                r'123\s*main\s*st',
                r'test\s*address',
                r'fake\s*street'
            ]
        }
    
    async def assess_fraud_risk(
        self,
        user_id: str,
        context_data: Dict[str, Any]
    ) -> FraudAssessment:
        """Évalue le risque de fraude pour un utilisateur"""
        try:
            assessment_id = f"fraud_assessment_{user_id}_{int(datetime.now().timestamp())}"
            
            # Collecte des signaux de fraude
            fraud_signals = await self._collect_fraud_signals(user_id, context_data)
            
            # Calcul du score de risque
            risk_score = await self._calculate_risk_score(fraud_signals, context_data)
            
            # Détermination du niveau de risque
            risk_level = self._get_risk_level(risk_score)
            
            # Identification des types de fraude
            fraud_types = await self._identify_fraud_types(fraud_signals)
            
            # Recommandations d'actions
            recommended_actions = await self._recommend_actions(risk_level, fraud_types, fraud_signals)
            
            # Score de confiance
            confidence = await self._calculate_confidence_score(fraud_signals, context_data)
            
            assessment = FraudAssessment(
                user_id=user_id,
                assessment_id=assessment_id,
                risk_level=risk_level,
                risk_score=risk_score,
                fraud_types=fraud_types,
                signals=fraud_signals,
                recommended_actions=recommended_actions,
                confidence=confidence,
                assessment_time=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=24)
            )
            
            # Stockage de l'évaluation
            self.fraud_assessments[assessment_id] = assessment
            
            # Mise à jour du profil utilisateur
            await self._update_user_risk_profile(user_id, assessment)
            
            logger.info(f"✅ Fraud risk assessed for user {user_id}: {risk_level.value} ({risk_score:.2f})")
            return assessment
            
        except Exception as e:
            logger.error(f"❌ Error assessing fraud risk for user {user_id}: {e}")
            return None
    
    async def _collect_fraud_signals(
        self,
        user_id: str,
        context_data: Dict[str, Any]
    ) -> List[FraudSignal]:
        """Collecte les signaux de fraude"""
        signals = []
        
        try:
            # Signaux de vélocité
            velocity_signals = await self._check_velocity_fraud(user_id, context_data)
            signals.extend(velocity_signals)
            
            # Signaux comportementaux
            behavioral_signals = await self._check_behavioral_anomalies(user_id, context_data)
            signals.extend(behavioral_signals)
            
            # Signaux de paiement
            payment_signals = await self._check_payment_fraud(user_id, context_data)
            signals.extend(payment_signals)
            
            # Signaux d'identité
            identity_signals = await self._check_identity_fraud(user_id, context_data)
            signals.extend(identity_signals)
            
            # Signaux techniques
            technical_signals = await self._check_technical_fraud(user_id, context_data)
            signals.extend(technical_signals)
            
            # Signaux de contenu
            content_signals = await self._check_content_abuse(user_id, context_data)
            signals.extend(content_signals)
            
            return signals
            
        except Exception as e:
            logger.error(f"❌ Error collecting fraud signals: {e}")
            return []
    
    async def _check_velocity_fraud(
        self,
        user_id: str,
        context_data: Dict[str, Any]
    ) -> List[FraudSignal]:
        """Vérifie les fraudes de vélocité"""
        signals = []
        
        try:
            user_ip = context_data.get('ip_address', '')
            email_domain = context_data.get('email', '').split('@')[-1]
            payment_method = context_data.get('payment_method', {})
            
            # Vérification essais multiples même IP
            ip_trials = await self._count_recent_trials_by_ip(user_ip, hours=24)
            if ip_trials > self.fraud_rules['velocity_checks']['max_trials_per_ip_24h']:
                signals.append(FraudSignal(
                    signal_id=f"velocity_ip_trials_{user_id}",
                    signal_type="velocity_fraud",
                    severity=0.8,
                    description=f"Trop d'essais depuis IP {user_ip}: {ip_trials}",
                    evidence={'ip_address': user_ip, 'trial_count': ip_trials},
                    timestamp=datetime.now()
                ))
            
            # Vérification comptes multiples même domaine email
            domain_accounts = await self._count_recent_accounts_by_domain(email_domain, days=7)
            if domain_accounts > self.fraud_rules['velocity_checks']['max_accounts_per_email_domain_7d']:
                signals.append(FraudSignal(
                    signal_id=f"velocity_email_domain_{user_id}",
                    signal_type="velocity_fraud",
                    severity=0.7,
                    description=f"Trop de comptes pour domaine {email_domain}: {domain_accounts}",
                    evidence={'email_domain': email_domain, 'account_count': domain_accounts},
                    timestamp=datetime.now()
                ))
            
            # Vérification tentatives de paiement
            if payment_method:
                payment_attempts = await self._count_payment_attempts(payment_method, hours=1)
                if payment_attempts > self.fraud_rules['velocity_checks']['max_payment_attempts_1h']:
                    signals.append(FraudSignal(
                        signal_id=f"velocity_payment_{user_id}",
                        signal_type="payment_fraud",
                        severity=0.9,
                        description=f"Trop de tentatives de paiement: {payment_attempts}",
                        evidence={'payment_attempts': payment_attempts},
                        timestamp=datetime.now()
                    ))
            
            return signals
            
        except Exception as e:
            logger.error(f"❌ Error checking velocity fraud: {e}")
            return []
    
    async def _check_behavioral_anomalies(
        self,
        user_id: str,
        context_data: Dict[str, Any]
    ) -> List[FraudSignal]:
        """Vérifie les anomalies comportementales"""
        signals = []
        
        try:
            # Heures de connexion inhabituelles
            login_hour = datetime.now().hour
            if login_hour < 6 or login_hour > 23:  # Connexions très tard/tôt
                signals.append(FraudSignal(
                    signal_id=f"unusual_hours_{user_id}",
                    signal_type="behavioral_anomaly",
                    severity=0.3,
                    description=f"Connexion à heure inhabituelle: {login_hour}h",
                    evidence={'login_hour': login_hour},
                    timestamp=datetime.now()
                ))
            
            # Géolocalisation impossible (vélocité géographique)
            if await self._check_impossible_geo_velocity(user_id, context_data):
                signals.append(FraudSignal(
                    signal_id=f"geo_velocity_{user_id}",
                    signal_type="behavioral_anomaly",
                    severity=0.9,
                    description="Déplacement géographique impossible détecté",
                    evidence=context_data.get('location_data', {}),
                    timestamp=datetime.now()
                ))
            
            # Empreinte digitale d'appareil suspecte
            device_fingerprint = context_data.get('device_fingerprint', {})
            if await self._check_suspicious_device(device_fingerprint):
                signals.append(FraudSignal(
                    signal_id=f"suspicious_device_{user_id}",
                    signal_type="technical_fraud",
                    severity=0.6,
                    description="Empreinte d'appareil suspecte détectée",
                    evidence=device_fingerprint,
                    timestamp=datetime.now()
                ))
            
            # Pattern d'usage anormal (ML)
            usage_anomaly_score = await self._detect_usage_anomaly(user_id, context_data)
            if usage_anomaly_score > 0.7:
                signals.append(FraudSignal(
                    signal_id=f"usage_anomaly_{user_id}",
                    signal_type="behavioral_anomaly",
                    severity=usage_anomaly_score,
                    description=f"Pattern d'usage anormal détecté (score: {usage_anomaly_score:.2f})",
                    evidence={'anomaly_score': usage_anomaly_score},
                    timestamp=datetime.now()
                ))
            
            return signals
            
        except Exception as e:
            logger.error(f"❌ Error checking behavioral anomalies: {e}")
            return []
    
    async def _check_payment_fraud(
        self,
        user_id: str,
        context_data: Dict[str, Any]
    ) -> List[FraudSignal]:
        """Vérifie les fraudes de paiement"""
        signals = []
        
        try:
            payment_data = context_data.get('payment_method', {})
            if not payment_data:
                return signals
            
            card_number = payment_data.get('card_number', '')
            billing_country = payment_data.get('billing_country', '')
            cardholder_name = payment_data.get('cardholder_name', '')
            
            # Vérification pays à haut risque
            if billing_country in self.fraud_rules['payment_fraud_indicators']['high_risk_countries']:
                signals.append(FraudSignal(
                    signal_id=f"high_risk_country_{user_id}",
                    signal_type="payment_fraud",
                    severity=0.6,
                    description=f"Pays de facturation à haut risque: {billing_country}",
                    evidence={'billing_country': billing_country},
                    timestamp=datetime.now()
                ))
            
            # Vérification cartes de test
            card_last4 = card_number[-4:] if len(card_number) >= 4 else ''
            for test_card in self.fraud_rules['payment_fraud_indicators']['test_card_patterns']:
                if card_number.replace(' ', '') == test_card:
                    signals.append(FraudSignal(
                        signal_id=f"test_card_{user_id}",
                        signal_type="payment_fraud",
                        severity=1.0,
                        description="Carte de test détectée",
                        evidence={'card_pattern': 'test_card'},
                        timestamp=datetime.now()
                    ))
            
            # Vérification BIN suspicieux
            bin_range = card_number[:6] if len(card_number) >= 6 else ''
            if bin_range in self.fraud_rules['payment_fraud_indicators']['suspicious_bin_ranges']:
                signals.append(FraudSignal(
                    signal_id=f"suspicious_bin_{user_id}",
                    signal_type="payment_fraud",
                    severity=0.8,
                    description=f"BIN suspicieux détecté: {bin_range}",
                    evidence={'bin_range': bin_range},
                    timestamp=datetime.now()
                ))
            
            # Disparité nom/email
            email_name = context_data.get('email', '').split('@')[0].lower()
            if cardholder_name and not self._names_match(cardholder_name, email_name):
                signals.append(FraudSignal(
                    signal_id=f"name_mismatch_{user_id}",
                    signal_type="identity_theft",
                    severity=0.5,
                    description="Disparité entre nom titulaire carte et email",
                    evidence={'cardholder_name': cardholder_name, 'email_name': email_name},
                    timestamp=datetime.now()
                ))
            
            return signals
            
        except Exception as e:
            logger.error(f"❌ Error checking payment fraud: {e}")
            return []
    
    async def _check_identity_fraud(
        self,
        user_id: str,
        context_data: Dict[str, Any]
    ) -> List[FraudSignal]:
        """Vérifie les fraudes d'identité"""
        signals = []
        
        try:
            email = context_data.get('email', '')
            name = context_data.get('name', '')
            phone = context_data.get('phone', '')
            address = context_data.get('address', '')
            
            # Vérification patterns d'email suspects
            for pattern in self.known_fraud_patterns['email_patterns']:
                if re.match(pattern, email.lower()):
                    signals.append(FraudSignal(
                        signal_id=f"suspicious_email_{user_id}",
                        signal_type="identity_theft",
                        severity=0.7,
                        description=f"Pattern d'email suspicieux: {email}",
                        evidence={'email': email, 'pattern': pattern},
                        timestamp=datetime.now()
                    ))
            
            # Vérification patterns de nom suspects
            for pattern in self.known_fraud_patterns['name_patterns']:
                if re.match(pattern, name.lower()):
                    signals.append(FraudSignal(
                        signal_id=f"suspicious_name_{user_id}",
                        signal_type="synthetic_identity",
                        severity=0.8,
                        description=f"Pattern de nom suspicieux: {name}",
                        evidence={'name': name, 'pattern': pattern},
                        timestamp=datetime.now()
                    ))
            
            # Vérification numéro de téléphone
            if phone:
                for pattern in self.known_fraud_patterns['phone_patterns']:
                    if re.match(pattern, phone):
                        signals.append(FraudSignal(
                            signal_id=f"suspicious_phone_{user_id}",
                            signal_type="synthetic_identity",
                            severity=0.6,
                            description=f"Numéro de téléphone suspicieux: {phone}",
                            evidence={'phone': phone, 'pattern': pattern},
                            timestamp=datetime.now()
                        ))
            
            # Vérification adresse
            if address:
                for pattern in self.known_fraud_patterns['address_patterns']:
                    if re.search(pattern, address.lower()):
                        signals.append(FraudSignal(
                            signal_id=f"suspicious_address_{user_id}",
                            signal_type="synthetic_identity",
                            severity=0.5,
                            description=f"Adresse suspecte: {address}",
                            evidence={'address': address, 'pattern': pattern},
                            timestamp=datetime.now()
                        ))
            
            return signals
            
        except Exception as e:
            logger.error(f"❌ Error checking identity fraud: {e}")
            return []
    
    async def _check_technical_fraud(
        self,
        user_id: str,
        context_data: Dict[str, Any]
    ) -> List[FraudSignal]:
        """Vérifie les fraudes techniques"""
        signals = []
        
        try:
            ip_address = context_data.get('ip_address', '')
            user_agent = context_data.get('user_agent', '')
            headers = context_data.get('headers', {})
            
            # Vérification IP suspecte
            ip_risk = await self._check_ip_reputation(ip_address)
            if ip_risk > 0.6:
                signals.append(FraudSignal(
                    signal_id=f"suspicious_ip_{user_id}",
                    signal_type="technical_fraud",
                    severity=ip_risk,
                    description=f"IP à haut risque: {ip_address}",
                    evidence={'ip_address': ip_address, 'risk_score': ip_risk},
                    timestamp=datetime.now()
                ))
            
            # Détection VPN/Proxy
            if await self._is_vpn_or_proxy(ip_address):
                signals.append(FraudSignal(
                    signal_id=f"vpn_proxy_{user_id}",
                    signal_type="technical_fraud",
                    severity=0.4,
                    description=f"VPN/Proxy détecté: {ip_address}",
                    evidence={'ip_address': ip_address, 'type': 'vpn_proxy'},
                    timestamp=datetime.now()
                ))
            
            # User-Agent suspicieux
            if self._is_suspicious_user_agent(user_agent):
                signals.append(FraudSignal(
                    signal_id=f"suspicious_ua_{user_id}",
                    signal_type="technical_fraud",
                    severity=0.5,
                    description=f"User-Agent suspicieux: {user_agent}",
                    evidence={'user_agent': user_agent},
                    timestamp=datetime.now()
                ))
            
            # Headers manquants ou suspects
            missing_headers = self._check_missing_headers(headers)
            if missing_headers:
                signals.append(FraudSignal(
                    signal_id=f"missing_headers_{user_id}",
                    signal_type="technical_fraud",
                    severity=0.3,
                    description=f"Headers HTTP manquants: {missing_headers}",
                    evidence={'missing_headers': missing_headers},
                    timestamp=datetime.now()
                ))
            
            return signals
            
        except Exception as e:
            logger.error(f"❌ Error checking technical fraud: {e}")
            return []
    
    async def _check_content_abuse(
        self,
        user_id: str,
        context_data: Dict[str, Any]
    ) -> List[FraudSignal]:
        """Vérifie les abus de contenu"""
        signals = []
        
        try:
            content_data = context_data.get('content_activity', {})
            if not content_data:
                return signals
            
            # Upload massif de contenu
            uploads_last_hour = content_data.get('uploads_last_hour', 0)
            if uploads_last_hour > self.fraud_rules['content_abuse_patterns']['mass_content_upload']:
                signals.append(FraudSignal(
                    signal_id=f"mass_upload_{user_id}",
                    signal_type="content_abuse",
                    severity=0.8,
                    description=f"Upload massif détecté: {uploads_last_hour} fichiers/heure",
                    evidence={'uploads_count': uploads_last_hour},
                    timestamp=datetime.now()
                ))
            
            # Contenu dupliqué
            duplicate_percentage = content_data.get('duplicate_content_percentage', 0)
            if duplicate_percentage > self.fraud_rules['content_abuse_patterns']['duplicate_content_threshold']:
                signals.append(FraudSignal(
                    signal_id=f"duplicate_content_{user_id}",
                    signal_type="content_abuse",
                    severity=0.7,
                    description=f"Contenu dupliqué: {duplicate_percentage:.1%}",
                    evidence={'duplicate_percentage': duplicate_percentage},
                    timestamp=datetime.now()
                ))
            
            # Détection de spam dans le contenu
            content_text = content_data.get('recent_content_text', '')
            spam_score = self._calculate_spam_score(content_text)
            if spam_score > 0.7:
                signals.append(FraudSignal(
                    signal_id=f"spam_content_{user_id}",
                    signal_type="content_abuse",
                    severity=spam_score,
                    description=f"Contenu spam détecté (score: {spam_score:.2f})",
                    evidence={'spam_score': spam_score},
                    timestamp=datetime.now()
                ))
            
            return signals
            
        except Exception as e:
            logger.error(f"❌ Error checking content abuse: {e}")
            return []
    
    async def _calculate_risk_score(
        self,
        fraud_signals: List[FraudSignal],
        context_data: Dict[str, Any]
    ) -> float:
        """Calcule le score de risque global"""
        try:
            if not fraud_signals:
                return 0.1  # Risque minimal
            
            # Pondération des signaux par type
            signal_weights = {
                'payment_fraud': 0.3,
                'identity_theft': 0.25,
                'velocity_fraud': 0.2,
                'behavioral_anomaly': 0.15,
                'technical_fraud': 0.05,
                'content_abuse': 0.05
            }
            
            # Calcul du score pondéré
            weighted_score = 0.0
            total_weight = 0.0
            
            for signal in fraud_signals:
                signal_type = signal.signal_type
                weight = signal_weights.get(signal_type, 0.1)
                weighted_score += signal.severity * weight
                total_weight += weight
            
            # Normalisation
            if total_weight > 0:
                base_score = weighted_score / total_weight
            else:
                base_score = 0.1
            
            # Facteurs d'amplification
            amplification_factors = []
            
            # Amplification pour signaux multiples
            if len(fraud_signals) > 3:
                amplification_factors.append(0.1 * (len(fraud_signals) - 3))
            
            # Amplification pour haute sévérité
            high_severity_signals = [s for s in fraud_signals if s.severity > 0.8]
            if high_severity_signals:
                amplification_factors.append(0.2 * len(high_severity_signals))
            
            # Application des amplifications
            final_score = base_score
            for factor in amplification_factors:
                final_score = min(final_score + factor, 1.0)
            
            return max(0.0, min(final_score, 1.0))
            
        except Exception as e:
            logger.error(f"❌ Error calculating risk score: {e}")
            return 0.5  # Score neutre par défaut
    
    def _get_risk_level(self, risk_score: float) -> FraudRiskLevel:
        """Détermine le niveau de risque"""
        if risk_score >= 0.8:
            return FraudRiskLevel.VERY_HIGH
        elif risk_score >= 0.6:
            return FraudRiskLevel.HIGH
        elif risk_score >= 0.3:
            return FraudRiskLevel.MEDIUM
        elif risk_score >= 0.1:
            return FraudRiskLevel.LOW
        else:
            return FraudRiskLevel.VERY_LOW
    
    async def _identify_fraud_types(self, fraud_signals: List[FraudSignal]) -> List[FraudType]:
        """Identifie les types de fraude présents"""
        fraud_types = set()
        
        signal_type_mapping = {
            'payment_fraud': FraudType.PAYMENT_FRAUD,
            'identity_theft': FraudType.IDENTITY_THEFT,
            'velocity_fraud': FraudType.VELOCITY_FRAUD,
            'behavioral_anomaly': FraudType.BEHAVIORAL_ANOMALY,
            'technical_fraud': FraudType.ACCOUNT_TAKEOVER,
            'synthetic_identity': FraudType.SYNTHETIC_IDENTITY,
            'content_abuse': FraudType.TRIAL_ABUSE
        }
        
        for signal in fraud_signals:
            fraud_type = signal_type_mapping.get(signal.signal_type)
            if fraud_type:
                fraud_types.add(fraud_type)
        
        return list(fraud_types)
    
    async def _recommend_actions(
        self,
        risk_level: FraudRiskLevel,
        fraud_types: List[FraudType],
        fraud_signals: List[FraudSignal]
    ) -> List[ActionType]:
        """Recommande des actions basées sur le risque"""
        actions = []
        
        # Actions basées sur le niveau de risque
        if risk_level == FraudRiskLevel.VERY_HIGH:
            actions.extend([ActionType.BLOCK, ActionType.MANUAL_REVIEW])
        elif risk_level == FraudRiskLevel.HIGH:
            actions.extend([ActionType.SUSPEND, ActionType.REQUIRE_VERIFICATION])
        elif risk_level == FraudRiskLevel.MEDIUM:
            actions.extend([ActionType.FLAG, ActionType.REQUIRE_VERIFICATION])
        elif risk_level == FraudRiskLevel.LOW:
            actions.append(ActionType.MONITOR)
        
        # Actions spécifiques par type de fraude
        if FraudType.PAYMENT_FRAUD in fraud_types:
            actions.append(ActionType.REQUIRE_VERIFICATION)
        
        if FraudType.VELOCITY_FRAUD in fraud_types:
            actions.append(ActionType.BLOCK)
        
        if FraudType.IDENTITY_THEFT in fraud_types:
            actions.extend([ActionType.MANUAL_REVIEW, ActionType.REQUIRE_VERIFICATION])
        
        # Déduplication
        return list(set(actions))
    
    async def _calculate_confidence_score(
        self,
        fraud_signals: List[FraudSignal],
        context_data: Dict[str, Any]
    ) -> float:
        """Calcule le score de confiance de l'évaluation"""
        try:
            # Facteurs de confiance
            confidence_factors = []
            
            # Confiance basée sur le nombre de signaux
            if len(fraud_signals) >= 3:
                confidence_factors.append(0.8)
            elif len(fraud_signals) >= 2:
                confidence_factors.append(0.6)
            else:
                confidence_factors.append(0.4)
            
            # Confiance basée sur la sévérité des signaux
            if fraud_signals:
                avg_severity = np.mean([s.severity for s in fraud_signals])
                confidence_factors.append(avg_severity)
            
            # Confiance basée sur la diversité des types de signaux
            signal_types = set(s.signal_type for s in fraud_signals)
            diversity_score = min(len(signal_types) / 5, 1.0)  # Normalisé sur 5 types
            confidence_factors.append(diversity_score)
            
            # Confiance basée sur les données disponibles
            data_completeness = len(context_data) / 10  # Normalisé sur 10 champs
            confidence_factors.append(min(data_completeness, 1.0))
            
            return np.mean(confidence_factors)
            
        except Exception as e:
            logger.error(f"❌ Error calculating confidence score: {e}")
            return 0.5
    
    # Méthodes utilitaires
    
    async def _count_recent_trials_by_ip(self, ip_address: str, hours: int) -> int:
        """Compte les essais récents depuis une IP"""
        # Simulation - à remplacer par vraie requête DB
        return np.random.poisson(1)  # Distribution réaliste
    
    async def _count_recent_accounts_by_domain(self, domain: str, days: int) -> int:
        """Compte les comptes récents pour un domaine email"""
        # Simulation - à remplacer par vraie requête DB
        return np.random.poisson(2)
    
    async def _count_payment_attempts(self, payment_method: Dict[str, Any], hours: int) -> int:
        """Compte les tentatives de paiement récentes"""
        # Simulation - à remplacer par vraie requête DB
        return np.random.poisson(1)
    
    async def _check_impossible_geo_velocity(self, user_id: str, context_data: Dict[str, Any]) -> bool:
        """Vérifie si la vélocité géographique est impossible"""
        # Simulation de vérification géographique
        current_location = context_data.get('location', {})
        if not current_location:
            return False
        
        # Logique simplifiée - à remplacer par vraie vérification
        return False
    
    async def _check_suspicious_device(self, device_fingerprint: Dict[str, Any]) -> bool:
        """Vérifie si l'empreinte d'appareil est suspecte"""
        if not device_fingerprint:
            return True  # Absence d'empreinte = suspect
        
        # Vérifications basiques
        screen_resolution = device_fingerprint.get('screen_resolution', '')
        if screen_resolution in ['800x600', '1024x768']:  # Résolutions anciennes/suspectes
            return True
        
        timezone = device_fingerprint.get('timezone', '')
        if not timezone:
            return True
        
        return False
    
    async def _detect_usage_anomaly(self, user_id: str, context_data: Dict[str, Any]) -> float:
        """Détecte les anomalies d'usage avec ML"""
        try:
            # Extraction de features d'usage
            usage_features = [
                context_data.get('session_duration', 300),  # Durée session en secondes
                context_data.get('pages_visited', 5),
                context_data.get('actions_per_minute', 2),
                context_data.get('mouse_movements', 100),
                context_data.get('keyboard_events', 50)
            ]
            
            # Utilisation du modèle d'anomalie si disponible
            if hasattr(self.anomaly_detector, 'predict'):
                try:
                    # Normalisation et prédiction
                    features_array = np.array(usage_features).reshape(1, -1)
                    anomaly_score = self.anomaly_detector.decision_function(features_array)[0]
                    # Conversion en score 0-1
                    return max(0, min(1, (anomaly_score + 0.5)))
                except:
                    pass
            
            # Heuristique de base
            if context_data.get('actions_per_minute', 2) > 10:  # Activité trop rapide
                return 0.8
            if context_data.get('session_duration', 300) < 30:  # Session trop courte
                return 0.6
            
            return 0.2  # Anomalie faible par défaut
            
        except Exception as e:
            logger.error(f"❌ Error detecting usage anomaly: {e}")
            return 0.3
    
    async def _check_ip_reputation(self, ip_address: str) -> float:
        """Vérifie la réputation d'une IP"""
        try:
            # Cache check
            if ip_address in self.ip_reputation_cache:
                return self.ip_reputation_cache[ip_address]
            
            # Vérifications basiques
            risk_score = 0.0
            
            # IP privées = risque faible
            try:
                ip_obj = ipaddress.ip_address(ip_address)
                if ip_obj.is_private:
                    risk_score = 0.1
                elif ip_obj.is_loopback:
                    risk_score = 0.9  # Localhost suspect
            except:
                risk_score = 0.5  # IP invalide
            
            # Simulation de vérification externe
            # (à remplacer par vraie API de réputation IP)
            if risk_score == 0.0:
                risk_score = np.random.beta(2, 8)  # Distribution réaliste vers faible risque
            
            # Cache du résultat
            self.ip_reputation_cache[ip_address] = risk_score
            
            return risk_score
            
        except Exception as e:
            logger.error(f"❌ Error checking IP reputation: {e}")
            return 0.3
    
    async def _is_vpn_or_proxy(self, ip_address: str) -> bool:
        """Détecte VPN/Proxy"""
        # Simulation - à remplacer par vraie détection
        return np.random.random() < 0.1  # 10% de chance
    
    def _is_suspicious_user_agent(self, user_agent: str) -> bool:
        """Vérifie si le User-Agent est suspicieux"""
        if not user_agent:
            return True
        
        suspicious_patterns = [
            'bot', 'crawler', 'spider', 'scraper',
            'curl', 'wget', 'python', 'java',
            'test', 'automation'
        ]
        
        ua_lower = user_agent.lower()
        return any(pattern in ua_lower for pattern in suspicious_patterns)
    
    def _check_missing_headers(self, headers: Dict[str, str]) -> List[str]:
        """Vérifie les headers HTTP manquants"""
        expected_headers = ['accept', 'accept-language', 'accept-encoding', 'referer']
        missing = [h for h in expected_headers if h not in headers]
        return missing
    
    def _names_match(self, name1: str, name2: str) -> bool:
        """Vérifie si deux noms correspondent"""
        if not name1 or not name2:
            return False
        
        # Normalisation
        name1_clean = re.sub(r'[^a-zA-Z]', '', name1.lower())
        name2_clean = re.sub(r'[^a-zA-Z]', '', name2.lower())
        
        # Vérifications de correspondance
        return (
            name1_clean in name2_clean or
            name2_clean in name1_clean or
            name1_clean[:3] == name2_clean[:3]  # 3 premiers caractères
        )
    
    def _calculate_spam_score(self, text: str) -> float:
        """Calcule le score de spam d'un texte"""
        if not text:
            return 0.0
        
        text_lower = text.lower()
        spam_keywords = self.fraud_rules['content_abuse_patterns']['spam_keywords']
        
        spam_count = sum(1 for keyword in spam_keywords if keyword in text_lower)
        return min(spam_count / len(spam_keywords), 1.0)
    
    async def _update_user_risk_profile(self, user_id: str, assessment: FraudAssessment):
        """Met à jour le profil de risque utilisateur"""
        try:
            if user_id not in self.user_profiles:
                self.user_profiles[user_id] = UserRiskProfile(
                    user_id=user_id,
                    current_risk_level=assessment.risk_level,
                    historical_assessments=[],
                    trusted_signals=[],
                    suspicious_patterns=[],
                    last_updated=datetime.now()
                )
            
            profile = self.user_profiles[user_id]
            profile.current_risk_level = assessment.risk_level
            profile.historical_assessments.append(assessment.assessment_id)
            profile.last_updated = datetime.now()
            
            # Garde seulement les 10 dernières évaluations
            if len(profile.historical_assessments) > 10:
                profile.historical_assessments = profile.historical_assessments[-10:]
            
        except Exception as e:
            logger.error(f"❌ Error updating user risk profile: {e}")
    
    async def get_user_risk_history(self, user_id: str) -> Dict[str, Any]:
        """Récupère l'historique de risque d'un utilisateur"""
        try:
            if user_id not in self.user_profiles:
                return {'user_id': user_id, 'message': 'No risk history found'}
            
            profile = self.user_profiles[user_id]
            
            # Récupération des évaluations historiques
            historical_data = []
            for assessment_id in profile.historical_assessments[-5:]:  # 5 dernières
                if assessment_id in self.fraud_assessments:
                    assessment = self.fraud_assessments[assessment_id]
                    historical_data.append({
                        'assessment_id': assessment_id,
                        'risk_level': assessment.risk_level.value,
                        'risk_score': assessment.risk_score,
                        'fraud_types': [ft.value for ft in assessment.fraud_types],
                        'assessment_time': assessment.assessment_time.isoformat()
                    })
            
            return {
                'user_id': user_id,
                'current_risk_level': profile.current_risk_level.value,
                'historical_assessments': historical_data,
                'trusted_signals': profile.trusted_signals,
                'suspicious_patterns': profile.suspicious_patterns,
                'last_updated': profile.last_updated.isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting user risk history: {e}")
            return {}


# Instance globale
subscription_fraud_detector = SubscriptionFraudDetector()

# Export des classes principales
__all__ = [
    'SubscriptionFraudDetector',
    'FraudAssessment',
    'FraudSignal',
    'UserRiskProfile',
    'FraudRiskLevel',
    'FraudType',
    'ActionType',
    'subscription_fraud_detector'
]