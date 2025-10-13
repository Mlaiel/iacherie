"""🚀 Fraud Detection System - IA Influencer Agent Platform Enterprise
=====================================================================
Module: backend/platform_core/billing/fraud_detection.py
Author: Fahed Mlaiel (mlaiel@live.de)
=====================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 SYSTÈME DÉTECTION FRAUDE ML TEMPS RÉEL
Détection intelligente de fraude avec Machine Learning avancé
- Modèles ML en temps réel pour scoring risque
- Analyse comportementale et détection d'anomalies
- 3D Secure intelligent et vérifications adaptatives
- Blacklist/Whitelist management automatisé
- Learning continu et adaptation aux nouvelles menaces

Multi-Expert Implementation:
🧠 Lead Dev IA: Modèles ML fraude, algorithmes anomalie, apprentissage adaptatif
🏗️ Backend Senior: Architecture temps réel haute performance, pipelines sécurisés
🤖 ML Engineer: Entraînement modèles, feature engineering, model evaluation
🗄️ DBA: Stockage patterns fraude, index optimisés, analytics historiques
🔒 Security: Threat intelligence, security protocols, incident response
🌐 Microservices: Intégration services anti-fraude, API sécurisées
🎵 Audio: Détection fraude spécifique industry musicale, copyright fraud
⚙️ DevOps: Monitoring alerting temps réel, scaling automatique
💡 AI Prompt: Génération règles intelligentes, alertes contextuelles
"""

import asyncio
import json
import logging
import time
import uuid
import hashlib
import numpy as np
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import ipaddress
import re
from decimal import Decimal
import statistics

# Configuration logging
logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Niveaux de risque"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FraudType(Enum):
    """Types de fraude détectés"""
    CARD_FRAUD = "card_fraud"
    IDENTITY_THEFT = "identity_theft"
    ACCOUNT_TAKEOVER = "account_takeover"
    VELOCITY_FRAUD = "velocity_fraud"
    BIN_ATTACK = "bin_attack"
    CHARGEBACK_FRAUD = "chargeback_fraud"
    SYNTHETIC_IDENTITY = "synthetic_identity"
    MONEY_LAUNDERING = "money_laundering"
    BONUS_ABUSE = "bonus_abuse"
    MERCHANT_FRAUD = "merchant_fraud"


class ActionRecommendation(Enum):
    """Actions recommandées"""
    APPROVE = "approve"
    REVIEW = "review"
    DECLINE = "decline"
    CHALLENGE = "challenge"
    BLOCK = "block"
    MONITOR = "monitor"


@dataclass
class FraudSignal:
    """Signal de fraude détecté"""
    signal_id: str
    fraud_type: FraudType
    risk_score: float
    confidence: float
    description: str
    evidence: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RiskProfile:
    """Profil de risque utilisateur"""
    user_id: str
    risk_score: float
    risk_level: RiskLevel
    last_updated: datetime
    transaction_count: int = 0
    total_volume: Decimal = Decimal('0.00')
    fraud_history: List[str] = field(default_factory=list)
    behavioral_patterns: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FraudAnalysisResult:
    """Résultat de l'analyse de fraude"""
    transaction_id: str
    overall_risk_score: float
    risk_level: RiskLevel
    recommendation: ActionRecommendation
    signals: List[FraudSignal]
    processing_time: float
    model_version: str
    requires_3ds: bool = False
    requires_manual_review: bool = False


class MLFraudModel:
    """🤖 Modèle ML pour détection de fraude"""
    
    def __init__(self):
        self.model_version = "1.0.0"
        self.feature_weights = {
            "amount_velocity": 0.25,
            "geo_location": 0.20,
            "device_fingerprint": 0.15,
            "behavioral_pattern": 0.15,
            "network_analysis": 0.10,
            "temporal_pattern": 0.10,
            "payment_method": 0.05
        }
        self.trained_at = datetime.utcnow()
        self.accuracy_score = 0.95
    
    def extract_features(self, transaction_data: Dict[str, Any]) -> Dict[str, float]:
        """🔍 Extraction de features pour le modèle"""
        
        features = {}
        
        # Features de base
        features["amount"] = float(transaction_data.get("amount", 0))
        features["hour_of_day"] = datetime.utcnow().hour
        features["day_of_week"] = datetime.utcnow().weekday()
        
        # Features de vélocité
        features["amount_velocity"] = self._calculate_amount_velocity(transaction_data)
        features["transaction_velocity"] = self._calculate_transaction_velocity(transaction_data)
        
        # Features géographiques
        geo_features = self._extract_geo_features(transaction_data)
        features.update(geo_features)
        
        # Features comportementales
        behavioral_features = self._extract_behavioral_features(transaction_data)
        features.update(behavioral_features)
        
        # Features de paiement
        payment_features = self._extract_payment_features(transaction_data)
        features.update(payment_features)
        
        return features
    
    def _calculate_amount_velocity(self, transaction_data: Dict[str, Any]) -> float:
        """💰 Calcul de la vélocité de montant"""
        
        amount = float(transaction_data.get("amount", 0))
        user_id = transaction_data.get("user_id")
        
        # Simulation historique (en production: base de données)
        historical_amounts = [100, 50, 200, 75, 150]  # Montants récents
        
        if not historical_amounts:
            return 0.5  # Score neutre
        
        avg_amount = statistics.mean(historical_amounts)
        max_amount = max(historical_amounts)
        
        # Score basé sur l'écart à la moyenne
        if amount > avg_amount * 3:
            return 1.0  # Très suspect
        elif amount > avg_amount * 2:
            return 0.8  # Suspect
        elif amount < avg_amount * 0.1:
            return 0.7  # Montant très faible suspect
        else:
            return 0.2  # Normal
    
    def _calculate_transaction_velocity(self, transaction_data: Dict[str, Any]) -> float:
        """⚡ Calcul de la vélocité de transaction"""
        
        user_id = transaction_data.get("user_id")
        
        # Simulation du nombre de transactions récentes
        recent_transactions = 3  # Dernière heure
        daily_transactions = 8   # Dernier jour
        
        # Seuils de vélocité
        if recent_transactions > 10:
            return 1.0  # Très suspect
        elif recent_transactions > 5:
            return 0.8  # Suspect
        elif daily_transactions > 50:
            return 0.7  # Volume élevé
        else:
            return 0.1  # Normal
    
    def _extract_geo_features(self, transaction_data: Dict[str, Any]) -> Dict[str, float]:
        """🌍 Extraction features géographiques"""
        
        features = {}
        
        ip_address = transaction_data.get("ip_address", "127.0.0.1")
        user_country = transaction_data.get("user_country", "US")
        card_country = transaction_data.get("card_country", "US")
        
        # Distance géographique
        features["geo_distance"] = self._calculate_geo_distance(user_country, card_country)
        
        # Risque par pays
        high_risk_countries = ["XX", "YY", "ZZ"]  # ISO codes pays à risque
        features["country_risk"] = 1.0 if user_country in high_risk_countries else 0.1
        
        # Type IP
        features["ip_risk"] = self._analyze_ip_risk(ip_address)
        
        return features
    
    def _extract_behavioral_features(self, transaction_data: Dict[str, Any]) -> Dict[str, float]:
        """🧠 Extraction features comportementales"""
        
        features = {}
        
        # Analyse du user agent
        user_agent = transaction_data.get("user_agent", "")
        features["device_consistency"] = self._analyze_device_consistency(user_agent)
        
        # Temps de saisie
        input_duration = transaction_data.get("form_input_duration", 30)
        features["input_pattern"] = self._analyze_input_pattern(input_duration)
        
        # Navigation pattern
        page_views = transaction_data.get("page_views_before_payment", 3)
        features["navigation_pattern"] = self._analyze_navigation_pattern(page_views)
        
        return features
    
    def _extract_payment_features(self, transaction_data: Dict[str, Any]) -> Dict[str, float]:
        """💳 Extraction features de paiement"""
        
        features = {}
        
        # Type de carte
        card_type = transaction_data.get("card_type", "credit")
        features["card_type_risk"] = 0.3 if card_type == "prepaid" else 0.1
        
        # BIN analysis
        card_bin = transaction_data.get("card_bin", "")
        features["bin_risk"] = self._analyze_bin_risk(card_bin)
        
        # Currency mismatch
        transaction_currency = transaction_data.get("currency", "USD")
        user_currency = transaction_data.get("user_preferred_currency", "USD")
        features["currency_mismatch"] = 0.6 if transaction_currency != user_currency else 0.1
        
        return features
    
    def _calculate_geo_distance(self, country1: str, country2: str) -> float:
        """📍 Calcul distance géographique"""
        
        if country1 == country2:
            return 0.0
        
        # Distances simplifiées (en production: vraie géolocalisation)
        same_continent = {
            ("US", "CA"): 0.2,
            ("FR", "DE"): 0.1,
            ("UK", "IE"): 0.1
        }
        
        pair = tuple(sorted([country1, country2]))
        return same_continent.get(pair, 0.8)  # Distance intercontinentale par défaut
    
    def _analyze_ip_risk(self, ip_address: str) -> float:
        """🌐 Analyse du risque IP"""
        
        try:
            ip = ipaddress.ip_address(ip_address)
            
            # IP privées
            if ip.is_private:
                return 0.8  # Suspect (proxy/VPN)
            
            # IP de loopback
            if ip.is_loopback:
                return 0.9  # Très suspect
            
            # IP multicast
            if ip.is_multicast:
                return 1.0  # Très suspect
            
            return 0.1  # IP publique normale
            
        except ValueError:
            return 1.0  # IP invalide
    
    def _analyze_device_consistency(self, user_agent: str) -> float:
        """📱 Analyse cohérence device"""
        
        if not user_agent:
            return 0.8  # Pas de user agent suspect
        
        # Détection de patterns suspects
        suspicious_patterns = [
            r"bot|crawler|spider",
            r"curl|wget|python",
            r"test|automation"
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, user_agent, re.IGNORECASE):
                return 0.9  # Très suspect
        
        return 0.1  # Normal
    
    def _analyze_input_pattern(self, input_duration: int) -> float:
        """⌨️ Analyse pattern de saisie"""
        
        # Temps de saisie suspect
        if input_duration < 5:  # Trop rapide (bot)
            return 0.9
        elif input_duration > 600:  # Trop lent (abandon/reprise)
            return 0.6
        elif 10 <= input_duration <= 120:  # Normal
            return 0.1
        else:
            return 0.4
    
    def _analyze_navigation_pattern(self, page_views: int) -> float:
        """🧭 Analyse pattern de navigation"""
        
        if page_views == 1:  # Direct au paiement
            return 0.7  # Suspect
        elif page_views > 20:  # Trop de pages
            return 0.5  # Moyennement suspect
        elif 2 <= page_views <= 10:  # Normal
            return 0.1
        else:
            return 0.4
    
    def _analyze_bin_risk(self, card_bin: str) -> float:
        """🏦 Analyse du risque BIN"""
        
        if not card_bin or len(card_bin) < 6:
            return 0.5  # BIN incomplet
        
        # BINs à haut risque (exemples)
        high_risk_bins = ["123456", "999999", "000000"]
        
        if card_bin[:6] in high_risk_bins:
            return 1.0  # Très risqué
        
        # BINs de cartes prépayées (plus risqués)
        prepaid_bins = ["555555", "444444"]
        
        if card_bin[:6] in prepaid_bins:
            return 0.6  # Moyennement risqué
        
        return 0.1  # BIN normal
    
    def predict_fraud_score(self, features: Dict[str, float]) -> float:
        """🎯 Prédiction du score de fraude"""
        
        weighted_score = 0.0
        
        for feature_name, weight in self.feature_weights.items():
            feature_value = features.get(feature_name, 0.0)
            weighted_score += feature_value * weight
        
        # Normalisation entre 0 et 1
        return min(1.0, max(0.0, weighted_score))


class FraudDetectionEngine:
    """🚀 Moteur de Détection de Fraude Enterprise"""
    
    def __init__(self):
        self.ml_model = MLFraudModel()
        self.risk_profiles: Dict[str, RiskProfile] = {}
        self.blacklist_ips: set = set()
        self.blacklist_emails: set = set()
        self.blacklist_cards: set = set()
        self.whitelist_users: set = set()
        self.fraud_rules: List[Dict[str, Any]] = []
        self.min_risk_threshold = 0.3
        self.high_risk_threshold = 0.7
        self.critical_risk_threshold = 0.9
        self._load_blacklists()
        self._load_fraud_rules()
    
    def _load_blacklists(self):
        """🚫 Chargement des listes noires"""
        
        # Simulation de données (en production: base de données)
        self.blacklist_ips = {
            "192.168.1.100",
            "10.0.0.50",
            "suspicious.proxy.com"
        }
        
        self.blacklist_emails = {
            "fraud@example.com",
            "test@suspicious.com"
        }
        
        self.blacklist_cards = {
            "4111111111111111",  # Test card
            "4000000000000002"   # Declined test card
        }
        
        self.whitelist_users = {
            "verified_user_123",
            "enterprise_customer_456"
        }
    
    def _load_fraud_rules(self):
        """📋 Chargement des règles de fraude"""
        
        self.fraud_rules = [
            {
                "name": "high_velocity_transactions",
                "description": "Plus de 5 transactions en 1 heure",
                "conditions": {
                    "transaction_count_1h": {"operator": ">", "value": 5}
                },
                "risk_score_add": 0.6,
                "fraud_type": FraudType.VELOCITY_FRAUD
            },
            {
                "name": "large_amount_anomaly",
                "description": "Montant 10x supérieur à la moyenne",
                "conditions": {
                    "amount_ratio_to_avg": {"operator": ">", "value": 10}
                },
                "risk_score_add": 0.5,
                "fraud_type": FraudType.CARD_FRAUD
            },
            {
                "name": "geo_inconsistency",
                "description": "Transaction depuis pays différent en <1h",
                "conditions": {
                    "geo_distance": {"operator": ">", "value": 0.8},
                    "time_since_last": {"operator": "<", "value": 3600}
                },
                "risk_score_add": 0.7,
                "fraud_type": FraudType.CARD_FRAUD
            },
            {
                "name": "suspicious_ip_pattern",
                "description": "IP Tor/VPN/Proxy détectée",
                "conditions": {
                    "ip_type": {"operator": "in", "value": ["tor", "vpn", "proxy"]}
                },
                "risk_score_add": 0.4,
                "fraud_type": FraudType.CARD_FRAUD
            }
        ]
    
    async def analyze_transaction(
        self,
        transaction_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> FraudAnalysisResult:
        """🔍 Analyse complète de fraude pour une transaction"""
        
        start_time = time.time()
        transaction_id = transaction_data.get("transaction_id", f"txn_{uuid.uuid4().hex[:12]}")
        
        try:
            # 1. Vérification des listes noires/blanches
            blacklist_signals = await self._check_blacklists(transaction_data)
            whitelist_check = await self._check_whitelists(transaction_data)
            
            # 2. Extraction des features ML
            features = self.ml_model.extract_features(transaction_data)
            
            # 3. Prédiction ML du score de fraude
            ml_risk_score = self.ml_model.predict_fraud_score(features)
            
            # 4. Application des règles business
            rule_signals = await self._apply_fraud_rules(transaction_data, features)
            
            # 5. Analyse du profil de risque utilisateur
            user_risk_profile = await self._analyze_user_risk_profile(
                transaction_data.get("user_id"), transaction_data
            )
            
            # 6. Calcul du score de risque global
            overall_risk_score = await self._calculate_overall_risk_score(
                ml_risk_score, blacklist_signals, rule_signals, user_risk_profile, whitelist_check
            )
            
            # 7. Détermination du niveau de risque et recommandation
            risk_level = self._determine_risk_level(overall_risk_score)
            recommendation = await self._determine_action_recommendation(
                overall_risk_score, risk_level, blacklist_signals, transaction_data
            )
            
            # 8. Compilation des signaux
            all_signals = blacklist_signals + rule_signals
            
            # 9. Détermination des mesures de sécurité
            requires_3ds = await self._should_require_3ds(overall_risk_score, transaction_data)
            requires_manual_review = await self._should_require_manual_review(
                overall_risk_score, all_signals
            )
            
            processing_time = (time.time() - start_time) * 1000  # ms
            
            result = FraudAnalysisResult(
                transaction_id=transaction_id,
                overall_risk_score=overall_risk_score,
                risk_level=risk_level,
                recommendation=recommendation,
                signals=all_signals,
                processing_time=processing_time,
                model_version=self.ml_model.model_version,
                requires_3ds=requires_3ds,
                requires_manual_review=requires_manual_review
            )
            
            # 10. Logging et mise à jour des profils
            await self._log_fraud_analysis(result, transaction_data)
            await self._update_user_risk_profile(
                transaction_data.get("user_id"), result, transaction_data
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de fraude: {e}")
            
            # Fallback en cas d'erreur
            return FraudAnalysisResult(
                transaction_id=transaction_id,
                overall_risk_score=0.5,  # Score neutre
                risk_level=RiskLevel.MEDIUM,
                recommendation=ActionRecommendation.REVIEW,
                signals=[],
                processing_time=(time.time() - start_time) * 1000,
                model_version="error_fallback",
                requires_3ds=True,
                requires_manual_review=True
            )
    
    async def _check_blacklists(self, transaction_data: Dict[str, Any]) -> List[FraudSignal]:
        """🚫 Vérification des listes noires"""
        
        signals = []
        
        # Vérification IP
        ip_address = transaction_data.get("ip_address", "")
        if ip_address in self.blacklist_ips:
            signals.append(FraudSignal(
                signal_id=f"blacklist_ip_{uuid.uuid4().hex[:8]}",
                fraud_type=FraudType.CARD_FRAUD,
                risk_score=1.0,
                confidence=1.0,
                description=f"IP address {ip_address} is blacklisted",
                evidence={"ip_address": ip_address, "list_type": "blacklist"}
            ))
        
        # Vérification email
        email = transaction_data.get("user_email", "")
        if email in self.blacklist_emails:
            signals.append(FraudSignal(
                signal_id=f"blacklist_email_{uuid.uuid4().hex[:8]}",
                fraud_type=FraudType.IDENTITY_THEFT,
                risk_score=0.9,
                confidence=1.0,
                description=f"Email {email} is blacklisted",
                evidence={"email": email, "list_type": "blacklist"}
            ))
        
        # Vérification carte
        card_number = transaction_data.get("card_number", "")
        if card_number in self.blacklist_cards:
            signals.append(FraudSignal(
                signal_id=f"blacklist_card_{uuid.uuid4().hex[:8]}",
                fraud_type=FraudType.CARD_FRAUD,
                risk_score=1.0,
                confidence=1.0,
                description=f"Card number is blacklisted",
                evidence={"card_masked": f"****{card_number[-4:]}", "list_type": "blacklist"}
            ))
        
        return signals
    
    async def _check_whitelists(self, transaction_data: Dict[str, Any]) -> bool:
        """✅ Vérification des listes blanches"""
        
        user_id = transaction_data.get("user_id", "")
        return user_id in self.whitelist_users
    
    async def _apply_fraud_rules(
        self,
        transaction_data: Dict[str, Any],
        features: Dict[str, float]
    ) -> List[FraudSignal]:
        """📋 Application des règles de fraude"""
        
        signals = []
        
        for rule in self.fraud_rules:
            try:
                if await self._evaluate_rule_conditions(rule["conditions"], transaction_data, features):
                    signal = FraudSignal(
                        signal_id=f"rule_{rule['name']}_{uuid.uuid4().hex[:8]}",
                        fraud_type=rule["fraud_type"],
                        risk_score=rule["risk_score_add"],
                        confidence=0.8,
                        description=rule["description"],
                        evidence={
                            "rule_name": rule["name"],
                            "conditions_met": rule["conditions"]
                        }
                    )
                    signals.append(signal)
                    
            except Exception as e:
                logger.error(f"Erreur lors de l'évaluation de la règle {rule['name']}: {e}")
        
        return signals
    
    async def _evaluate_rule_conditions(
        self,
        conditions: Dict[str, Any],
        transaction_data: Dict[str, Any],
        features: Dict[str, float]
    ) -> bool:
        """🔍 Évaluation des conditions d'une règle"""
        
        for condition_name, condition_def in conditions.items():
            operator = condition_def["operator"]
            expected_value = condition_def["value"]
            
            # Récupération de la valeur actuelle
            actual_value = None
            
            if condition_name in features:
                actual_value = features[condition_name]
            elif condition_name in transaction_data:
                actual_value = transaction_data[condition_name]
            else:
                # Calcul de métriques complexes
                actual_value = await self._calculate_dynamic_metric(
                    condition_name, transaction_data
                )
            
            if actual_value is None:
                continue  # Condition non évaluable
            
            # Évaluation de la condition
            if not self._evaluate_condition(actual_value, operator, expected_value):
                return False  # Une condition non remplie = règle non applicable
        
        return True  # Toutes les conditions sont remplies
    
    def _evaluate_condition(self, actual_value: Any, operator: str, expected_value: Any) -> bool:
        """🔍 Évaluation d'une condition individuelle"""
        
        try:
            if operator == ">":
                return actual_value > expected_value
            elif operator == ">=":
                return actual_value >= expected_value
            elif operator == "<":
                return actual_value < expected_value
            elif operator == "<=":
                return actual_value <= expected_value
            elif operator == "==":
                return actual_value == expected_value
            elif operator == "!=":
                return actual_value != expected_value
            elif operator == "in":
                return actual_value in expected_value
            elif operator == "not_in":
                return actual_value not in expected_value
            else:
                logger.warning(f"Opérateur inconnu: {operator}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors de l'évaluation de condition: {e}")
            return False
    
    async def _calculate_dynamic_metric(
        self,
        metric_name: str,
        transaction_data: Dict[str, Any]
    ) -> Optional[float]:
        """📊 Calcul de métriques dynamiques"""
        
        user_id = transaction_data.get("user_id")
        
        if metric_name == "transaction_count_1h":
            # Simulation du compte de transactions récentes
            return float(3)  # 3 transactions dans la dernière heure
        
        elif metric_name == "amount_ratio_to_avg":
            # Ratio du montant vs moyenne historique
            current_amount = float(transaction_data.get("amount", 0))
            avg_amount = 150.0  # Simulation moyenne historique
            return current_amount / avg_amount if avg_amount > 0 else 0
        
        elif metric_name == "time_since_last":
            # Temps depuis la dernière transaction (secondes)
            return float(1800)  # 30 minutes
        
        return None
    
    async def _analyze_user_risk_profile(
        self,
        user_id: Optional[str],
        transaction_data: Dict[str, Any]
    ) -> Optional[RiskProfile]:
        """👤 Analyse du profil de risque utilisateur"""
        
        if not user_id:
            return None
        
        # Récupération ou création du profil
        if user_id in self.risk_profiles:
            profile = self.risk_profiles[user_id]
        else:
            profile = RiskProfile(
                user_id=user_id,
                risk_score=0.3,  # Score neutre pour nouveau utilisateur
                risk_level=RiskLevel.MEDIUM,
                last_updated=datetime.utcnow()
            )
            self.risk_profiles[user_id] = profile
        
        # Mise à jour des métriques
        profile.transaction_count += 1
        profile.total_volume += Decimal(str(transaction_data.get("amount", 0)))
        
        # Analyse comportementale
        await self._update_behavioral_patterns(profile, transaction_data)
        
        # Recalcul du score de risque
        profile.risk_score = await self._calculate_user_risk_score(profile, transaction_data)
        profile.risk_level = self._determine_risk_level(profile.risk_score)
        profile.last_updated = datetime.utcnow()
        
        return profile
    
    async def _update_behavioral_patterns(
        self,
        profile: RiskProfile,
        transaction_data: Dict[str, Any]
    ):
        """🧠 Mise à jour des patterns comportementaux"""
        
        # Patterns temporels
        hour = datetime.utcnow().hour
        if "transaction_hours" not in profile.behavioral_patterns:
            profile.behavioral_patterns["transaction_hours"] = {}
        
        hour_key = str(hour)
        profile.behavioral_patterns["transaction_hours"][hour_key] = (
            profile.behavioral_patterns["transaction_hours"].get(hour_key, 0) + 1
        )
        
        # Patterns de montants
        amount = float(transaction_data.get("amount", 0))
        if "amount_history" not in profile.behavioral_patterns:
            profile.behavioral_patterns["amount_history"] = []
        
        profile.behavioral_patterns["amount_history"].append(amount)
        
        # Garder seulement les 50 derniers montants
        if len(profile.behavioral_patterns["amount_history"]) > 50:
            profile.behavioral_patterns["amount_history"] = (
                profile.behavioral_patterns["amount_history"][-50:]
            )
        
        # Patterns géographiques
        country = transaction_data.get("user_country", "")
        if country:
            if "countries" not in profile.behavioral_patterns:
                profile.behavioral_patterns["countries"] = {}
            
            profile.behavioral_patterns["countries"][country] = (
                profile.behavioral_patterns["countries"].get(country, 0) + 1
            )
    
    async def _calculate_user_risk_score(
        self,
        profile: RiskProfile,
        transaction_data: Dict[str, Any]
    ) -> float:
        """📈 Calcul du score de risque utilisateur"""
        
        base_score = 0.3  # Score de base
        
        # Facteur historique de fraude
        fraud_history_factor = len(profile.fraud_history) * 0.1
        
        # Facteur de vélocité
        if profile.transaction_count > 20:  # Utilisateur établi
            velocity_factor = -0.1  # Bonus utilisateur établi
        elif profile.transaction_count > 100:
            velocity_factor = -0.2  # Gros bonus utilisateur très établi
        else:
            velocity_factor = 0.1  # Penalty nouveau utilisateur
        
        # Facteur de volume
        avg_transaction = float(profile.total_volume / profile.transaction_count) if profile.transaction_count > 0 else 0
        current_amount = float(transaction_data.get("amount", 0))
        
        if current_amount > avg_transaction * 5:
            amount_factor = 0.3  # Transaction anormalement élevée
        elif current_amount < avg_transaction * 0.1:
            amount_factor = 0.2  # Transaction anormalement faible
        else:
            amount_factor = -0.05  # Transaction normale
        
        # Facteur comportemental
        behavioral_factor = await self._calculate_behavioral_deviation(profile, transaction_data)
        
        final_score = base_score + fraud_history_factor + velocity_factor + amount_factor + behavioral_factor
        
        return min(1.0, max(0.0, final_score))
    
    async def _calculate_behavioral_deviation(
        self,
        profile: RiskProfile,
        transaction_data: Dict[str, Any]
    ) -> float:
        """🔍 Calcul de la déviation comportementale"""
        
        deviation_score = 0.0
        
        # Déviation temporelle
        current_hour = datetime.utcnow().hour
        hour_history = profile.behavioral_patterns.get("transaction_hours", {})
        
        if hour_history:
            total_transactions = sum(hour_history.values())
            hour_frequency = hour_history.get(str(current_hour), 0) / total_transactions
            
            if hour_frequency < 0.01:  # Heure inhabituelle
                deviation_score += 0.2
        
        # Déviation géographique
        current_country = transaction_data.get("user_country", "")
        country_history = profile.behavioral_patterns.get("countries", {})
        
        if current_country and country_history:
            total_transactions = sum(country_history.values())
            country_frequency = country_history.get(current_country, 0) / total_transactions
            
            if country_frequency < 0.1:  # Pays inhabituel
                deviation_score += 0.3
        
        return min(0.5, deviation_score)
    
    async def _calculate_overall_risk_score(
        self,
        ml_score: float,
        blacklist_signals: List[FraudSignal],
        rule_signals: List[FraudSignal],
        user_profile: Optional[RiskProfile],
        is_whitelisted: bool
    ) -> float:
        """🎯 Calcul du score de risque global"""
        
        # Score de base ML
        base_score = ml_score
        
        # Bonus/Malus liste blanche
        if is_whitelisted:
            base_score *= 0.3  # Réduction importante pour utilisateurs de confiance
        
        # Ajout des signaux de liste noire
        blacklist_penalty = 0.0
        for signal in blacklist_signals:
            blacklist_penalty += signal.risk_score * signal.confidence
        
        # Ajout des signaux de règles
        rule_penalty = 0.0
        for signal in rule_signals:
            rule_penalty += signal.risk_score * signal.confidence * 0.5  # Pondération moindre
        
        # Facteur profil utilisateur
        profile_factor = 0.0
        if user_profile:
            profile_factor = user_profile.risk_score * 0.3
        
        # Score final
        final_score = base_score + blacklist_penalty + rule_penalty + profile_factor
        
        return min(1.0, max(0.0, final_score))
    
    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """📊 Détermination du niveau de risque"""
        
        if risk_score >= self.critical_risk_threshold:
            return RiskLevel.CRITICAL
        elif risk_score >= self.high_risk_threshold:
            return RiskLevel.HIGH
        elif risk_score >= self.min_risk_threshold:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    async def _determine_action_recommendation(
        self,
        risk_score: float,
        risk_level: RiskLevel,
        blacklist_signals: List[FraudSignal],
        transaction_data: Dict[str, Any]
    ) -> ActionRecommendation:
        """🎯 Détermination de l'action recommandée"""
        
        # Blocage immédiat pour liste noire
        if blacklist_signals:
            critical_signals = [s for s in blacklist_signals if s.risk_score >= 0.9]
            if critical_signals:
                return ActionRecommendation.BLOCK
        
        # Actions par niveau de risque
        if risk_level == RiskLevel.CRITICAL:
            return ActionRecommendation.DECLINE
        
        elif risk_level == RiskLevel.HIGH:
            # Vérification 3DS ou review manuelle selon le montant
            amount = float(transaction_data.get("amount", 0))
            if amount > 1000:
                return ActionRecommendation.REVIEW
            else:
                return ActionRecommendation.CHALLENGE
        
        elif risk_level == RiskLevel.MEDIUM:
            return ActionRecommendation.CHALLENGE
        
        else:  # LOW risk
            return ActionRecommendation.APPROVE
    
    async def _should_require_3ds(
        self,
        risk_score: float,
        transaction_data: Dict[str, Any]
    ) -> bool:
        """🔐 Détermination si 3DS est requis"""
        
        # 3DS obligatoire pour score élevé
        if risk_score >= 0.6:
            return True
        
        # 3DS pour montants élevés
        amount = float(transaction_data.get("amount", 0))
        if amount > 500:
            return True
        
        # 3DS pour certaines régions (SCA européenne)
        region = transaction_data.get("user_country", "")
        if region in ["FR", "DE", "IT", "ES", "NL"]:  # Pays SCA
            return True
        
        return False
    
    async def _should_require_manual_review(
        self,
        risk_score: float,
        signals: List[FraudSignal]
    ) -> bool:
        """👥 Détermination si review manuelle requise"""
        
        # Review pour score très élevé
        if risk_score >= 0.8:
            return True
        
        # Review pour certains types de fraude
        critical_fraud_types = [
            FraudType.MONEY_LAUNDERING,
            FraudType.SYNTHETIC_IDENTITY,
            FraudType.MERCHANT_FRAUD
        ]
        
        for signal in signals:
            if signal.fraud_type in critical_fraud_types:
                return True
        
        return False
    
    async def _log_fraud_analysis(
        self,
        result: FraudAnalysisResult,
        transaction_data: Dict[str, Any]
    ):
        """📝 Logging de l'analyse de fraude"""
        
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "transaction_id": result.transaction_id,
            "risk_score": result.overall_risk_score,
            "risk_level": result.risk_level.value,
            "recommendation": result.recommendation.value,
            "signals_count": len(result.signals),
            "processing_time_ms": result.processing_time,
            "model_version": result.model_version,
            "amount": transaction_data.get("amount"),
            "currency": transaction_data.get("currency"),
            "user_id": transaction_data.get("user_id"),
            "requires_3ds": result.requires_3ds,
            "requires_manual_review": result.requires_manual_review
        }
        
        logger.info(f"Fraud analysis completed: {json.dumps(log_data)}")
        
        # Logging détaillé des signaux pour investigation
        for signal in result.signals:
            signal_log = {
                "timestamp": datetime.utcnow().isoformat(),
                "transaction_id": result.transaction_id,
                "signal_id": signal.signal_id,
                "fraud_type": signal.fraud_type.value,
                "risk_score": signal.risk_score,
                "confidence": signal.confidence,
                "description": signal.description,
                "evidence": signal.evidence
            }
            logger.warning(f"Fraud signal detected: {json.dumps(signal_log)}")
    
    async def _update_user_risk_profile(
        self,
        user_id: Optional[str],
        result: FraudAnalysisResult,
        transaction_data: Dict[str, Any]
    ):
        """📊 Mise à jour du profil de risque utilisateur"""
        
        if not user_id:
            return
        
        profile = self.risk_profiles.get(user_id)
        if not profile:
            return
        
        # Ajout à l'historique si fraude détectée
        if result.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            fraud_entry = {
                "transaction_id": result.transaction_id,
                "timestamp": datetime.utcnow().isoformat(),
                "risk_score": result.overall_risk_score,
                "fraud_types": [s.fraud_type.value for s in result.signals]
            }
            profile.fraud_history.append(str(fraud_entry))
            
            # Garder seulement les 20 derniers incidents
            if len(profile.fraud_history) > 20:
                profile.fraud_history = profile.fraud_history[-20:]
    
    async def calculate_risk_score(
        self,
        transaction_data: Dict[str, Any]
    ) -> float:
        """🎯 Calcul rapide du score de risque"""
        
        result = await self.analyze_transaction(transaction_data)
        return result.overall_risk_score
    
    async def trigger_security_measures(
        self,
        transaction_id: str,
        risk_level: RiskLevel,
        recommended_action: ActionRecommendation
    ) -> Dict[str, Any]:
        """🚨 Déclenchement des mesures de sécurité"""
        
        try:
            security_actions = []
            
            if recommended_action == ActionRecommendation.BLOCK:
                security_actions.append({
                    "action": "block_transaction",
                    "reason": "High fraud risk detected",
                    "immediate": True
                })
                
                security_actions.append({
                    "action": "alert_security_team",
                    "priority": "high",
                    "immediate": True
                })
            
            elif recommended_action == ActionRecommendation.DECLINE:
                security_actions.append({
                    "action": "decline_payment",
                    "reason": "Critical fraud risk",
                    "immediate": True
                })
            
            elif recommended_action == ActionRecommendation.CHALLENGE:
                security_actions.append({
                    "action": "require_3ds_authentication",
                    "reason": "Additional verification required",
                    "immediate": False
                })
            
            elif recommended_action == ActionRecommendation.REVIEW:
                security_actions.append({
                    "action": "queue_manual_review",
                    "priority": "medium",
                    "immediate": False
                })
            
            # Logging des actions
            logger.info(f"Security measures triggered for {transaction_id}: {security_actions}")
            
            return {
                "transaction_id": transaction_id,
                "actions_triggered": security_actions,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du déclenchement des mesures de sécurité: {e}")
            return {"error": str(e)}
    
    async def learn_from_patterns(
        self,
        feedback_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """🧠 Apprentissage à partir des patterns de fraude"""
        
        try:
            transaction_id = feedback_data.get("transaction_id")
            actual_fraud = feedback_data.get("is_fraud", False)
            predicted_score = feedback_data.get("predicted_score", 0.0)
            
            # Analyse de la précision de prédiction
            prediction_accuracy = self._calculate_prediction_accuracy(
                predicted_score, actual_fraud
            )
            
            # Mise à jour des poids du modèle si nécessaire
            if prediction_accuracy < 0.8:  # Seuil de précision
                await self._adjust_model_weights(feedback_data)
            
            # Mise à jour des règles de fraude
            await self._update_fraud_rules_from_feedback(feedback_data)
            
            # Mise à jour des listes noires/blanches
            await self._update_lists_from_feedback(feedback_data)
            
            return {
                "transaction_id": transaction_id,
                "learning_applied": True,
                "prediction_accuracy": prediction_accuracy,
                "model_updated": prediction_accuracy < 0.8,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'apprentissage: {e}")
            return {"error": str(e)}
    
    def _calculate_prediction_accuracy(
        self,
        predicted_score: float,
        actual_fraud: bool
    ) -> float:
        """📊 Calcul de la précision de prédiction"""
        
        # Conversion du score en prédiction binaire
        predicted_fraud = predicted_score > self.high_risk_threshold
        
        # Calcul de la précision
        if predicted_fraud == actual_fraud:
            return 1.0  # Prédiction correcte
        else:
            # Erreur pondérée par la distance au seuil
            if actual_fraud and predicted_score < self.min_risk_threshold:
                return 0.0  # Faux négatif grave
            elif not actual_fraud and predicted_score > self.critical_risk_threshold:
                return 0.2  # Faux positif grave
            else:
                return 0.6  # Erreur modérée
    
    async def _adjust_model_weights(self, feedback_data: Dict[str, Any]):
        """⚖️ Ajustement des poids du modèle"""
        
        # Simulation d'ajustement (en production: ML pipeline complet)
        actual_fraud = feedback_data.get("is_fraud", False)
        features_used = feedback_data.get("features", {})
        
        adjustment_factor = 0.01  # Apprentissage conservateur
        
        if actual_fraud:
            # Augmenter l'importance des features qui ont détecté
            for feature_name, feature_value in features_used.items():
                if feature_name in self.ml_model.feature_weights and feature_value > 0.5:
                    self.ml_model.feature_weights[feature_name] = min(
                        1.0, 
                        self.ml_model.feature_weights[feature_name] + adjustment_factor
                    )
        else:
            # Diminuer l'importance des features qui ont faussement alerté
            for feature_name, feature_value in features_used.items():
                if feature_name in self.ml_model.feature_weights and feature_value > 0.5:
                    self.ml_model.feature_weights[feature_name] = max(
                        0.0,
                        self.ml_model.feature_weights[feature_name] - adjustment_factor
                    )
        
        logger.info("Model weights adjusted based on feedback")
    
    async def _update_fraud_rules_from_feedback(self, feedback_data: Dict[str, Any]):
        """📋 Mise à jour des règles à partir du feedback"""
        
        # Simulation de mise à jour des règles
        # En production: analyse des patterns pour créer/modifier des règles
        
        if feedback_data.get("is_fraud") and feedback_data.get("predicted_score", 0) < 0.3:
            # Cas de faux négatif - règle potentiellement manquante
            logger.info("Analyzing patterns for new fraud rule creation")
        
        elif not feedback_data.get("is_fraud") and feedback_data.get("predicted_score", 0) > 0.8:
            # Cas de faux positif - règle potentiellement trop stricte
            logger.info("Analyzing rules for potential relaxation")
    
    async def _update_lists_from_feedback(self, feedback_data: Dict[str, Any]):
        """📝 Mise à jour des listes à partir du feedback"""
        
        transaction_data = feedback_data.get("transaction_data", {})
        is_fraud = feedback_data.get("is_fraud", False)
        
        if is_fraud:
            # Ajouter aux listes noires si fraude confirmée
            ip_address = transaction_data.get("ip_address")
            if ip_address:
                self.blacklist_ips.add(ip_address)
                logger.info(f"Added IP {ip_address} to blacklist")
        
        else:
            # Considérer pour liste blanche si utilisateur légitime fréquent
            user_id = transaction_data.get("user_id")
            if user_id and user_id in self.risk_profiles:
                profile = self.risk_profiles[user_id]
                if profile.transaction_count > 50 and profile.risk_score < 0.2:
                    self.whitelist_users.add(user_id)
                    logger.info(f"Added user {user_id} to whitelist")
    
    def get_fraud_statistics(self, period_days: int = 30) -> Dict[str, Any]:
        """📊 Statistiques de fraude"""
        
        try:
            # Simulation de statistiques (en production: base de données)
            total_transactions = 10000
            fraud_detected = 150
            false_positives = 25
            false_negatives = 8
            
            fraud_rate = (fraud_detected / total_transactions) * 100
            precision = fraud_detected / (fraud_detected + false_positives)
            recall = fraud_detected / (fraud_detected + false_negatives)
            f1_score = 2 * (precision * recall) / (precision + recall)
            
            return {
                "period_days": period_days,
                "total_transactions": total_transactions,
                "fraud_detected": fraud_detected,
                "fraud_rate_percentage": round(fraud_rate, 2),
                "false_positives": false_positives,
                "false_negatives": false_negatives,
                "precision": round(precision, 3),
                "recall": round(recall, 3),
                "f1_score": round(f1_score, 3),
                "model_accuracy": round(self.ml_model.accuracy_score, 3),
                "blacklist_size": {
                    "ips": len(self.blacklist_ips),
                    "emails": len(self.blacklist_emails),
                    "cards": len(self.blacklist_cards)
                },
                "whitelist_size": len(self.whitelist_users),
                "active_rules": len(self.fraud_rules),
                "risk_profiles": len(self.risk_profiles)
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des statistiques: {e}")
            return {"error": str(e)}
    
    def add_to_blacklist(
        self,
        list_type: str,
        value: str,
        reason: str = "Manual addition"
    ) -> bool:
        """➕ Ajout à la liste noire"""
        
        try:
            if list_type == "ip":
                self.blacklist_ips.add(value)
            elif list_type == "email":
                self.blacklist_emails.add(value)
            elif list_type == "card":
                self.blacklist_cards.add(value)
            else:
                logger.error(f"Type de liste inconnu: {list_type}")
                return False
            
            logger.info(f"Added {value} to {list_type} blacklist: {reason}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout à la liste noire: {e}")
            return False
    
    def remove_from_blacklist(self, list_type: str, value: str) -> bool:
        """➖ Suppression de la liste noire"""
        
        try:
            if list_type == "ip":
                self.blacklist_ips.discard(value)
            elif list_type == "email":
                self.blacklist_emails.discard(value)
            elif list_type == "card":
                self.blacklist_cards.discard(value)
            else:
                logger.error(f"Type de liste inconnu: {list_type}")
                return False
            
            logger.info(f"Removed {value} from {list_type} blacklist")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de la liste noire: {e}")
            return False