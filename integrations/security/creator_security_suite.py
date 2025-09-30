# 🔒 Creator Security Suite: Personalized Protection & Security Scoring
"""
Creator Security Suite - IA Chérie Integrations
============================================
Enterprise security suite providing personalized protection, security scoring,
creator-specific security features, and comprehensive threat protection for IA Chérie
creator platform with advanced ML-powered security intelligence.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: IA Chérie Integrations
Version: 1.0 Production
"""

import asyncio
import hashlib
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
import numpy as np
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import pandas as pd
from cryptography.fernet import Fernet
import bcrypt
import jwt
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import redis
from celery import Celery
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import twilio
from twilio.rest import Client
import boto3

# Configuration
Base = declarative_base()
logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """Niveaux de sécurité"""
    BASIC = "basic"
    ENHANCED = "enhanced"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class ThreatType(Enum):
    """Types de menaces"""
    ACCOUNT_TAKEOVER = "account_takeover"
    CONTENT_THEFT = "content_theft"
    IDENTITY_SPOOFING = "identity_spoofing"
    HARASSMENT = "harassment"
    SPAM = "spam"
    PHISHING = "phishing"
    MALWARE = "malware"
    DDOS = "ddos"

class AlertLevel(Enum):
    """Niveaux d'alerte"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class CreatorProfile:
    """Profil créateur sécurisé"""
    creator_id: str
    username: str
    email: str
    security_level: SecurityLevel
    verification_status: str
    security_score: float
    threat_profile: Dict[str, Any]
    protection_settings: Dict[str, Any]
    contact_preferences: Dict[str, Any]
    created_at: datetime
    last_updated: datetime

@dataclass
class SecurityScore:
    """Score de sécurité créateur"""
    creator_id: str
    overall_score: float
    category_scores: Dict[str, float]
    risk_factors: List[str]
    recommendations: List[str]
    last_calculated: datetime
    trend: str  # improving, declining, stable

@dataclass
class ThreatAlert:
    """Alerte de menace"""
    alert_id: str
    creator_id: str
    threat_type: ThreatType
    alert_level: AlertLevel
    description: str
    evidence: Dict[str, Any]
    recommended_actions: List[str]
    status: str  # active, resolved, dismissed
    created_at: datetime
    resolved_at: Optional[datetime]

@dataclass
class SecurityAction:
    """Action de sécurité"""
    action_id: str
    creator_id: str
    action_type: str
    description: str
    automatic: bool
    status: str
    result: Dict[str, Any]
    executed_at: datetime

class CreatorProfileModel(Base):
    """Modèle database profil créateur"""
    __tablename__ = 'creator_profiles'
    
    id = Column(Integer, primary_key=True)
    creator_id = Column(String(255), nullable=False, unique=True, index=True)
    username = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    security_level = Column(String(50), nullable=False)
    verification_status = Column(String(50), default='pending')
    security_score = Column(Float, default=50.0)
    threat_profile = Column(JSON)
    protection_settings = Column(JSON)
    contact_preferences = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)

class SecurityScoreModel(Base):
    """Modèle database scores sécurité"""
    __tablename__ = 'security_scores'
    
    id = Column(Integer, primary_key=True)
    creator_id = Column(String(255), nullable=False, index=True)
    overall_score = Column(Float, nullable=False)
    category_scores = Column(JSON)
    risk_factors = Column(JSON)
    recommendations = Column(JSON)
    last_calculated = Column(DateTime, default=datetime.utcnow)
    trend = Column(String(20), default='stable')

class ThreatAlertModel(Base):
    """Modèle database alertes menaces"""
    __tablename__ = 'threat_alerts'
    
    id = Column(Integer, primary_key=True)
    alert_id = Column(String(255), nullable=False, unique=True)
    creator_id = Column(String(255), nullable=False, index=True)
    threat_type = Column(String(50), nullable=False)
    alert_level = Column(String(20), nullable=False)
    description = Column(Text, nullable=False)
    evidence = Column(JSON)
    recommended_actions = Column(JSON)
    status = Column(String(20), default='active')
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)

class SecurityActionModel(Base):
    """Modèle database actions sécurité"""
    __tablename__ = 'security_actions'
    
    id = Column(Integer, primary_key=True)
    action_id = Column(String(255), nullable=False, unique=True)
    creator_id = Column(String(255), nullable=False, index=True)
    action_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    automatic = Column(Boolean, default=False)
    status = Column(String(20), default='pending')
    result = Column(JSON)
    executed_at = Column(DateTime, default=datetime.utcnow)

class CreatorSecuritySuite:
    """
    Suite sécurité personnalisée pour créateurs
    
    Fonctionnalités:
    - Profils sécurité personnalisés
    - Score sécurité ML-powered
    - Détection menaces comportementales
    - Protection automatisée adaptative
    - Alertes intelligentes multi-canal
    - Actions sécurité proactives
    - Vérification identité avancée
    - Monitoring réputation temps réel
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_engine = create_engine(config.get('database_url', 'sqlite:///creator_security.db'))
        Base.metadata.create_all(self.db_engine)
        self.Session = sessionmaker(bind=self.db_engine)
        
        # ML Models initialization
        self._init_ml_models()
        
        # Services initialization
        self._init_services()
        
        # Security modules
        self._init_security_modules()
        
        # Métriques
        self.metrics = {
            'total_creators': 0,
            'threats_detected': 0,
            'actions_executed': 0,
            'average_security_score': 0.0,
            'active_alerts': 0
        }
        
        logger.info("CreatorSecuritySuite initialisé avec succès")
    
    def _init_ml_models(self):
        """Initialisation modèles ML"""
        try:
            # Modèle classification menaces
            self.threat_classifier = RandomForestClassifier(
                n_estimators=100,
                random_state=42,
                class_weight='balanced'
            )
            
            # Modèle détection anomalies comportementales
            self.behavior_detector = IsolationForest(
                contamination=0.1,
                random_state=42
            )
            
            # Scaler pour normalisation
            self.scaler = StandardScaler()
            
            # Entraînement avec données simulées
            self._train_initial_models()
            
            logger.info("Modèles ML initialisés et entraînés")
            
        except Exception as e:
            logger.error(f"Erreur initialisation ML models: {e}")
    
    def _init_services(self):
        """Initialisation services externes"""
        try:
            # Redis pour cache
            self.redis_client = redis.Redis(
                host=self.config.get('redis_host', 'localhost'),
                port=self.config.get('redis_port', 6379),
                decode_responses=True
            )
            
            # Celery pour tasks async
            self.celery_app = Celery(
                'creator_security',
                broker=self.config.get('celery_broker', 'redis://localhost:6379/0')
            )
            
            # Services communication
            self.twilio_client = None
            if self.config.get('twilio_enabled'):
                self.twilio_client = Client(
                    self.config.get('twilio_account_sid'),
                    self.config.get('twilio_auth_token')
                )
            
            # AWS services
            self.ses_client = None
            if self.config.get('aws_enabled'):
                self.ses_client = boto3.client('ses')
            
            logger.info("Services externes initialisés")
            
        except Exception as e:
            logger.error(f"Erreur initialisation services: {e}")
    
    def _init_security_modules(self):
        """Initialisation modules sécurité"""
        try:
            # Encryption
            self.cipher_suite = Fernet(
                self.config.get('encryption_key', Fernet.generate_key())
            )
            
            # JWT pour tokens
            self.jwt_secret = self.config.get('jwt_secret', 'secure_secret_key')
            
            # Rate limiting
            self.rate_limits = {
                'login_attempts': 5,
                'api_requests': 1000,
                'content_uploads': 100
            }
            
            logger.info("Modules sécurité initialisés")
            
        except Exception as e:
            logger.error(f"Erreur initialisation sécurité: {e}")
    
    def _train_initial_models(self):
        """Entraînement initial des modèles avec données simulées"""
        try:
            # Génération données d'entraînement simulées
            np.random.seed(42)
            
            # Features comportementales
            n_samples = 1000
            features = np.random.rand(n_samples, 15)  # 15 features comportementales
            
            # Labels menaces (simulés)
            threat_labels = np.random.choice([0, 1], size=n_samples, p=[0.8, 0.2])
            
            # Entraînement classificateur menaces
            X_train, X_test, y_train, y_test = train_test_split(
                features, threat_labels, test_size=0.2, random_state=42
            )
            
            # Normalisation
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Entraînement
            self.threat_classifier.fit(X_train_scaled, y_train)
            
            # Entraînement détecteur anomalies
            normal_data = features[threat_labels == 0]
            self.behavior_detector.fit(self.scaler.transform(normal_data))
            
            # Évaluation basique
            train_accuracy = self.threat_classifier.score(X_train_scaled, y_train)
            test_accuracy = self.threat_classifier.score(X_test_scaled, y_test)
            
            logger.info(f"Modèles entraînés - Train: {train_accuracy:.3f}, Test: {test_accuracy:.3f}")
            
        except Exception as e:
            logger.error(f"Erreur entraînement modèles: {e}")
    
    async def create_creator_profile(self, creator_data: Dict[str, Any]) -> CreatorProfile:
        """
        Création profil créateur sécurisé
        
        Args:
            creator_data: Données créateur
            
        Returns:
            CreatorProfile: Profil créé
        """
        try:
            creator_id = creator_data.get('creator_id') or f"creator_{uuid.uuid4().hex[:12]}"
            
            # Validation sécurisée des données
            validated_data = await self._validate_creator_data(creator_data)
            
            # Détermination niveau sécurité basé sur profil
            security_level = await self._determine_security_level(validated_data)
            
            # Calcul score sécurité initial
            initial_score = await self._calculate_initial_security_score(validated_data)
            
            # Création profil menaces personnalisé
            threat_profile = await self._create_threat_profile(validated_data)
            
            # Configuration protection par défaut
            protection_settings = self._get_default_protection_settings(security_level)
            
            # Préférences contact par défaut
            contact_preferences = {
                'email_alerts': True,
                'sms_alerts': False,
                'push_notifications': True,
                'alert_frequency': 'immediate',
                'digest_enabled': True
            }
            
            # Création profil
            profile = CreatorProfile(
                creator_id=creator_id,
                username=validated_data['username'],
                email=validated_data['email'],
                security_level=security_level,
                verification_status='pending',
                security_score=initial_score,
                threat_profile=threat_profile,
                protection_settings=protection_settings,
                contact_preferences=contact_preferences,
                created_at=datetime.utcnow(),
                last_updated=datetime.utcnow()
            )
            
            # Sauvegarde database
            await self._save_creator_profile(profile)
            
            # Initiation processus vérification
            await self._initiate_verification_process(profile)
            
            # Mise à jour métriques
            self.metrics['total_creators'] += 1
            
            logger.info(f"Profil créateur créé: {creator_id}")
            
            return profile
            
        except Exception as e:
            logger.error(f"Erreur création profil: {e}")
            raise
    
    async def calculate_security_score(self, creator_id: str, 
                                     behavioral_data: Dict[str, Any] = None) -> SecurityScore:
        """
        Calcul score sécurité ML-powered
        
        Args:
            creator_id: ID créateur
            behavioral_data: Données comportementales récentes
            
        Returns:
            SecurityScore: Score calculé
        """
        try:
            # Récupération profil créateur
            profile = await self._get_creator_profile(creator_id)
            if not profile:
                raise ValueError(f"Profil non trouvé: {creator_id}")
            
            # Collecte données comportementales
            if behavioral_data is None:
                behavioral_data = await self._collect_behavioral_data(creator_id)
            
            # Calcul scores par catégorie
            category_scores = {}
            
            # 1. Account Security (25%)
            category_scores['account_security'] = await self._calculate_account_security_score(
                creator_id, behavioral_data
            )
            
            # 2. Content Protection (25%)
            category_scores['content_protection'] = await self._calculate_content_protection_score(
                creator_id, behavioral_data
            )
            
            # 3. Privacy & Identity (20%)
            category_scores['privacy_identity'] = await self._calculate_privacy_score(
                creator_id, behavioral_data
            )
            
            # 4. Threat Awareness (15%)
            category_scores['threat_awareness'] = await self._calculate_threat_awareness_score(
                creator_id, behavioral_data
            )
            
            # 5. Platform Compliance (15%)
            category_scores['platform_compliance'] = await self._calculate_compliance_score(
                creator_id, behavioral_data
            )
            
            # Calcul score global pondéré
            weights = {
                'account_security': 0.25,
                'content_protection': 0.25,
                'privacy_identity': 0.20,
                'threat_awareness': 0.15,
                'platform_compliance': 0.15
            }
            
            overall_score = sum(
                category_scores[category] * weights[category]
                for category in category_scores
            )
            
            # Identification facteurs de risque
            risk_factors = await self._identify_risk_factors(creator_id, category_scores)
            
            # Génération recommandations
            recommendations = await self._generate_security_recommendations(
                creator_id, category_scores, risk_factors
            )
            
            # Détermination tendance
            trend = await self._calculate_score_trend(creator_id, overall_score)
            
            # Création objet score
            security_score = SecurityScore(
                creator_id=creator_id,
                overall_score=overall_score,
                category_scores=category_scores,
                risk_factors=risk_factors,
                recommendations=recommendations,
                last_calculated=datetime.utcnow(),
                trend=trend
            )
            
            # Sauvegarde
            await self._save_security_score(security_score)
            
            # Mise à jour profil
            await self._update_profile_security_score(creator_id, overall_score)
            
            logger.info(f"Score sécurité calculé: {creator_id} - {overall_score:.1f}")
            
            return security_score
            
        except Exception as e:
            logger.error(f"Erreur calcul score sécurité: {e}")
            raise
    
    async def detect_threats(self, creator_id: str, 
                           activity_data: Dict[str, Any]) -> List[ThreatAlert]:
        """
        Détection menaces comportementales ML-powered
        
        Args:
            creator_id: ID créateur
            activity_data: Données d'activité récente
            
        Returns:
            List[ThreatAlert]: Alertes générées
        """
        try:
            alerts = []
            
            # Extraction features pour ML
            features = await self._extract_threat_features(creator_id, activity_data)
            if not features:
                return alerts
            
            # Normalisation features
            features_scaled = self.scaler.transform([features])
            
            # Prédiction menaces avec classificateur
            threat_probability = self.threat_classifier.predict_proba(features_scaled)[0][1]
            threat_prediction = self.threat_classifier.predict(features_scaled)[0]
            
            # Détection anomalies comportementales
            anomaly_score = self.behavior_detector.decision_function(features_scaled)[0]
            is_anomaly = self.behavior_detector.predict(features_scaled)[0] == -1
            
            # Analyse spécifique par type de menace
            specific_threats = await self._analyze_specific_threats(creator_id, activity_data)
            
            # Génération alertes basées sur ML predictions
            if threat_prediction == 1 or threat_probability > 0.7:
                alert = await self._create_threat_alert(
                    creator_id,
                    ThreatType.ACCOUNT_TAKEOVER,
                    AlertLevel.WARNING if threat_probability < 0.85 else AlertLevel.CRITICAL,
                    f"Activité suspecte détectée (probabilité: {threat_probability:.2f})",
                    {
                        'ml_prediction': threat_prediction,
                        'threat_probability': threat_probability,
                        'features_analyzed': len(features),
                        'detection_method': 'ml_classifier'
                    }
                )
                alerts.append(alert)
            
            # Alertes anomalies comportementales
            if is_anomaly and anomaly_score < -0.5:
                alert = await self._create_threat_alert(
                    creator_id,
                    ThreatType.IDENTITY_SPOOFING,
                    AlertLevel.WARNING,
                    f"Comportement anormal détecté (score: {anomaly_score:.2f})",
                    {
                        'anomaly_score': anomaly_score,
                        'is_anomaly': is_anomaly,
                        'detection_method': 'isolation_forest'
                    }
                )
                alerts.append(alert)
            
            # Ajout alertes spécifiques
            alerts.extend(specific_threats)
            
            # Filtrage doublons et priorisation
            alerts = await self._prioritize_alerts(alerts)
            
            # Sauvegarde et notifications
            for alert in alerts:
                await self._save_threat_alert(alert)
                await self._send_threat_notification(alert)
            
            # Mise à jour métriques
            self.metrics['threats_detected'] += len(alerts)
            self.metrics['active_alerts'] += len([a for a in alerts if a.status == 'active'])
            
            logger.info(f"Menaces détectées: {creator_id} - {len(alerts)} alertes")
            
            return alerts
            
        except Exception as e:
            logger.error(f"Erreur détection menaces: {e}")
            return []
    
    async def execute_security_action(self, creator_id: str, action_type: str,
                                    parameters: Dict[str, Any] = None,
                                    automatic: bool = False) -> SecurityAction:
        """
        Exécution action sécurité
        
        Args:
            creator_id: ID créateur
            action_type: Type d'action
            parameters: Paramètres action
            automatic: Action automatique ou manuelle
            
        Returns:
            SecurityAction: Action exécutée
        """
        try:
            action_id = f"action_{uuid.uuid4().hex[:12]}"
            parameters = parameters or {}
            
            # Validation permissions
            if not await self._validate_action_permissions(creator_id, action_type):
                raise PermissionError(f"Action non autorisée: {action_type}")
            
            # Exécution selon type
            result = {}
            description = ""
            
            if action_type == "lock_account":
                result = await self._lock_account(creator_id, parameters)
                description = "Verrouillage compte pour sécurité"
            
            elif action_type == "enable_2fa":
                result = await self._enable_2fa(creator_id, parameters)
                description = "Activation authentification à deux facteurs"
            
            elif action_type == "reset_password":
                result = await self._force_password_reset(creator_id, parameters)
                description = "Réinitialisation mot de passe forcée"
            
            elif action_type == "revoke_sessions":
                result = await self._revoke_all_sessions(creator_id, parameters)
                description = "Révocation toutes sessions actives"
            
            elif action_type == "enable_content_protection":
                result = await self._enable_content_protection(creator_id, parameters)
                description = "Activation protection contenu avancée"
            
            elif action_type == "quarantine_content":
                result = await self._quarantine_content(creator_id, parameters)
                description = "Mise en quarantaine contenu suspect"
            
            elif action_type == "notify_security_team":
                result = await self._notify_security_team(creator_id, parameters)
                description = "Notification équipe sécurité"
            
            elif action_type == "update_threat_profile":
                result = await self._update_threat_profile(creator_id, parameters)
                description = "Mise à jour profil menaces"
            
            else:
                raise ValueError(f"Type d'action non supporté: {action_type}")
            
            # Création objet action
            action = SecurityAction(
                action_id=action_id,
                creator_id=creator_id,
                action_type=action_type,
                description=description,
                automatic=automatic,
                status="completed" if result.get('success') else "failed",
                result=result,
                executed_at=datetime.utcnow()
            )
            
            # Sauvegarde
            await self._save_security_action(action)
            
            # Logging et audit
            await self._log_security_action(action)
            
            # Mise à jour métriques
            self.metrics['actions_executed'] += 1
            
            logger.info(f"Action sécurité exécutée: {action_id} - {action_type}")
            
            return action
            
        except Exception as e:
            logger.error(f"Erreur exécution action: {e}")
            raise
    
    async def get_creator_security_dashboard(self, creator_id: str) -> Dict[str, Any]:
        """
        Dashboard sécurité personnalisé créateur
        
        Args:
            creator_id: ID créateur
            
        Returns:
            Dict[str, Any]: Données dashboard
        """
        try:
            # Récupération profil
            profile = await self._get_creator_profile(creator_id)
            if not profile:
                raise ValueError(f"Profil non trouvé: {creator_id}")
            
            # Score sécurité actuel
            current_score = await self._get_latest_security_score(creator_id)
            
            # Alertes actives
            active_alerts = await self._get_active_alerts(creator_id)
            
            # Actions récentes
            recent_actions = await self._get_recent_actions(creator_id, limit=10)
            
            # Statistiques menaces
            threat_stats = await self._get_threat_statistics(creator_id)
            
            # Recommandations prioritaires
            priority_recommendations = await self._get_priority_recommendations(creator_id)
            
            # Historique scores (7 derniers jours)
            score_history = await self._get_score_history(creator_id, days=7)
            
            # Status vérification
            verification_status = await self._get_verification_status(creator_id)
            
            # Compilation dashboard
            dashboard = {
                'creator_id': creator_id,
                'profile': {
                    'username': profile.username,
                    'security_level': profile.security_level.value,
                    'verification_status': profile.verification_status,
                    'last_updated': profile.last_updated.isoformat()
                },
                'security_score': {
                    'current': current_score.overall_score if current_score else 0.0,
                    'trend': current_score.trend if current_score else 'unknown',
                    'category_breakdown': current_score.category_scores if current_score else {},
                    'last_calculated': current_score.last_calculated.isoformat() if current_score else None
                },
                'alerts': {
                    'active_count': len(active_alerts),
                    'critical_count': len([a for a in active_alerts if a.alert_level == AlertLevel.CRITICAL]),
                    'recent_alerts': [
                        {
                            'alert_id': alert.alert_id,
                            'threat_type': alert.threat_type.value,
                            'level': alert.alert_level.value,
                            'description': alert.description,
                            'created_at': alert.created_at.isoformat()
                        } for alert in active_alerts[:5]  # 5 plus récentes
                    ]
                },
                'recent_actions': [
                    {
                        'action_id': action.action_id,
                        'type': action.action_type,
                        'description': action.description,
                        'status': action.status,
                        'automatic': action.automatic,
                        'executed_at': action.executed_at.isoformat()
                    } for action in recent_actions
                ],
                'threat_statistics': threat_stats,
                'recommendations': priority_recommendations[:5],  # Top 5
                'score_history': score_history,
                'verification': verification_status,
                'protection_settings': profile.protection_settings,
                'last_updated': datetime.utcnow().isoformat()
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Erreur dashboard sécurité: {e}")
            return {}
    
    # Méthodes de calcul score sécurité par catégorie
    async def _calculate_account_security_score(self, creator_id: str, 
                                              behavioral_data: Dict[str, Any]) -> float:
        """Calcul score sécurité compte"""
        try:
            score = 0.0
            factors = []
            
            # 2FA activé (+30 points)
            if behavioral_data.get('has_2fa', False):
                score += 30
                factors.append('2fa_enabled')
            
            # Mot de passe fort (+20 points)
            password_strength = behavioral_data.get('password_strength', 0)
            score += min(password_strength * 20, 20)
            if password_strength > 0.8:
                factors.append('strong_password')
            
            # Dernière connexion récente (-10 si > 30 jours)
            last_login = behavioral_data.get('last_login_days', 0)
            if last_login > 30:
                score -= 10
                factors.append('inactive_account')
            elif last_login <= 7:
                score += 10
                factors.append('active_account')
            
            # Sessions multiples simultanées (-5 par session supplémentaire)
            active_sessions = behavioral_data.get('active_sessions', 1)
            if active_sessions > 3:
                score -= (active_sessions - 3) * 5
                factors.append('multiple_sessions')
            
            # Connexions depuis nouveaux appareils (-5 points)
            new_devices = behavioral_data.get('new_devices_30d', 0)
            score -= new_devices * 5
            if new_devices > 2:
                factors.append('frequent_new_devices')
            
            # Tentatives connexion échouées (-10 points)
            failed_logins = behavioral_data.get('failed_logins_7d', 0)
            score -= failed_logins * 2
            if failed_logins > 5:
                factors.append('frequent_failed_logins')
            
            return max(0, min(100, score))
            
        except Exception as e:
            logger.error(f"Erreur calcul score compte: {e}")
            return 50.0
    
    async def _calculate_content_protection_score(self, creator_id: str,
                                                behavioral_data: Dict[str, Any]) -> float:
        """Calcul score protection contenu"""
        try:
            score = 0.0
            
            # Watermarking activé (+25 points)
            if behavioral_data.get('watermarking_enabled', False):
                score += 25
            
            # DRM activé (+25 points)
            if behavioral_data.get('drm_enabled', False):
                score += 25
            
            # Backup régulier (+20 points)
            backup_frequency = behavioral_data.get('backup_frequency_days', 30)
            if backup_frequency <= 7:
                score += 20
            elif backup_frequency <= 14:
                score += 15
            elif backup_frequency <= 30:
                score += 10
            
            # Licences définies (+15 points)
            if behavioral_data.get('has_defined_licenses', False):
                score += 15
            
            # Monitoring violations (+15 points)
            if behavioral_data.get('violation_monitoring', False):
                score += 15
            
            # Violations détectées récemment (-10 points par violation)
            recent_violations = behavioral_data.get('violations_30d', 0)
            score -= recent_violations * 10
            
            return max(0, min(100, score))
            
        except Exception as e:
            logger.error(f"Erreur calcul score protection: {e}")
            return 50.0
    
    async def _calculate_privacy_score(self, creator_id: str,
                                     behavioral_data: Dict[str, Any]) -> float:
        """Calcul score confidentialité"""
        try:
            score = 0.0
            
            # Profil public vs privé
            profile_privacy = behavioral_data.get('profile_privacy', 'public')
            if profile_privacy == 'private':
                score += 20
            elif profile_privacy == 'restricted':
                score += 15
            
            # Informations personnelles exposées (-5 par info)
            exposed_info = behavioral_data.get('exposed_personal_info', [])
            score -= len(exposed_info) * 5
            
            # Géolocalisation activée (-10 points)
            if behavioral_data.get('geolocation_enabled', False):
                score -= 10
            
            # Partage données tiers (-15 points)
            if behavioral_data.get('third_party_sharing', False):
                score -= 15
            
            # Vérification identité (+30 points)
            if behavioral_data.get('identity_verified', False):
                score += 30
            
            # Paramètres confidentialité configurés (+25 points)
            privacy_configured = behavioral_data.get('privacy_settings_configured', False)
            if privacy_configured:
                score += 25
            
            return max(0, min(100, score))
            
        except Exception as e:
            logger.error(f"Erreur calcul score confidentialité: {e}")
            return 50.0
    
    # Méthodes utilitaires
    async def _create_threat_alert(self, creator_id: str, threat_type: ThreatType,
                                 alert_level: AlertLevel, description: str,
                                 evidence: Dict[str, Any]) -> ThreatAlert:
        """Création alerte menace"""
        alert_id = f"alert_{uuid.uuid4().hex[:12]}"
        
        # Génération recommandations basées sur type menace
        recommendations = self._get_threat_recommendations(threat_type, alert_level)
        
        return ThreatAlert(
            alert_id=alert_id,
            creator_id=creator_id,
            threat_type=threat_type,
            alert_level=alert_level,
            description=description,
            evidence=evidence,
            recommended_actions=recommendations,
            status='active',
            created_at=datetime.utcnow(),
            resolved_at=None
        )
    
    def _get_threat_recommendations(self, threat_type: ThreatType, 
                                  alert_level: AlertLevel) -> List[str]:
        """Recommandations par type de menace"""
        base_recommendations = {
            ThreatType.ACCOUNT_TAKEOVER: [
                "Changez immédiatement votre mot de passe",
                "Activez l'authentification à deux facteurs",
                "Révoquez toutes les sessions actives",
                "Vérifiez l'activité récente du compte"
            ],
            ThreatType.CONTENT_THEFT: [
                "Activez le watermarking sur vos contenus",
                "Déposez une réclamation DMCA",
                "Renforcez les paramètres de protection",
                "Surveillez les violations de droits d'auteur"
            ],
            ThreatType.IDENTITY_SPOOFING: [
                "Vérifiez votre identité officielle",
                "Signalez les comptes usurpateurs",
                "Renforcez votre branding authentique",
                "Activez les notifications d'usurpation"
            ],
            ThreatType.HARASSMENT: [
                "Bloquez les utilisateurs malveillants",
                "Signalez le harcèlement aux plateformes",
                "Activez les filtres de contenu",
                "Documentez les preuves de harcèlement"
            ]
        }
        
        recommendations = base_recommendations.get(threat_type, [
            "Contactez l'équipe de sécurité",
            "Surveillez votre compte attentivement",
            "Activez toutes les protections disponibles"
        ])
        
        if alert_level == AlertLevel.CRITICAL:
            recommendations.insert(0, "🚨 ACTION IMMÉDIATE REQUISE")
        
        return recommendations
    
    async def get_security_metrics(self) -> Dict[str, Any]:
        """Récupération métriques sécurité globales"""
        try:
            session = self.Session()
            
            # Statistiques générales
            total_creators = session.query(CreatorProfileModel).count()
            total_alerts = session.query(ThreatAlertModel).count()
            active_alerts = session.query(ThreatAlertModel)\
                                 .filter(ThreatAlertModel.status == 'active').count()
            
            # Distribution niveaux sécurité
            security_levels = {}
            for level in SecurityLevel:
                count = session.query(CreatorProfileModel)\
                             .filter(CreatorProfileModel.security_level == level.value)\
                             .count()
                security_levels[level.value] = count
            
            # Score sécurité moyen
            avg_score = session.query(
                sqlalchemy.func.avg(CreatorProfileModel.security_score)
            ).scalar() or 0.0
            
            # Alertes par type (7 derniers jours)
            recent_alerts = session.query(ThreatAlertModel)\
                                 .filter(ThreatAlertModel.created_at >= datetime.utcnow() - timedelta(days=7))\
                                 .all()
            
            alert_types = {}
            for alert in recent_alerts:
                alert_types[alert.threat_type] = alert_types.get(alert.threat_type, 0) + 1
            
            session.close()
            
            return {
                'total_creators': total_creators,
                'total_alerts': total_alerts,
                'active_alerts': active_alerts,
                'security_level_distribution': security_levels,
                'average_security_score': round(avg_score, 1),
                'recent_threat_types': alert_types,
                'actions_executed_total': self.metrics.get('actions_executed', 0),
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur métriques sécurité: {e}")
            return {}
    
    # Méthodes de sauvegarde
    async def _save_creator_profile(self, profile: CreatorProfile):
        """Sauvegarde profil créateur"""
        try:
            session = self.Session()
            
            profile_record = CreatorProfileModel(
                creator_id=profile.creator_id,
                username=profile.username,
                email=profile.email,
                security_level=profile.security_level.value,
                verification_status=profile.verification_status,
                security_score=profile.security_score,
                threat_profile=profile.threat_profile,
                protection_settings=profile.protection_settings,
                contact_preferences=profile.contact_preferences
            )
            
            session.add(profile_record)
            session.commit()
            session.close()
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde profil: {e}")

# Instance globale
_security_suite_instance = None

def get_creator_security_suite(config: Dict[str, Any] = None) -> CreatorSecuritySuite:
    """Factory pour instance suite sécurité"""
    global _security_suite_instance
    
    if _security_suite_instance is None:
        if config is None:
            config = {
                'database_url': 'sqlite:///creator_security.db',
                'redis_host': 'localhost',
                'redis_port': 6379,
                'twilio_enabled': False,
                'aws_enabled': False,
                'encryption_key': Fernet.generate_key(),
                'jwt_secret': 'secure_secret_key'
            }
        
        _security_suite_instance = CreatorSecuritySuite(config)
    
    return _security_suite_instance

if __name__ == "__main__":
    # Test basique
    async def test_security_suite():
        suite = get_creator_security_suite()
        
        # Test création profil
        creator_data = {
            'username': 'test_creator',
            'email': 'test@example.com',
            'follower_count': 1000,
            'content_types': ['video', 'image']
        }
        
        profile = await suite.create_creator_profile(creator_data)
        print(f"Profil créé: {profile.creator_id}")
        print(f"Score initial: {profile.security_score}")
        
        # Test calcul score
        behavioral_data = {
            'has_2fa': False,
            'password_strength': 0.6,
            'last_login_days': 2,
            'failed_logins_7d': 1
        }
        
        score = await suite.calculate_security_score(profile.creator_id, behavioral_data)
        print(f"Score calculé: {score.overall_score:.1f}")
        print(f"Recommandations: {score.recommendations[:3]}")
    
    # Exécution test
    asyncio.run(test_security_suite())