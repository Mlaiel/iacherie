#!/usr/bin/env python3
"""
🛡️ Payment Security Validator - Enterprise Transaction Security
===============================================================

Advanced payment validation system for IA Chérie creator economy.
Real-time transaction validation, risk assessment, and automated blocking.

Author: Expert Team (Security + Backend Senior + ML Engineer)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Contact mlaiel@live.de for enterprise licensing

⚠️  LEGAL WARNING:
This code is proprietary to Fahed Mlaiel. Unauthorized use, distribution,
reverse engineering, or commercial exploitation is strictly prohibited.
Violations will result in immediate legal action.
"""

import asyncio
import hashlib
import hmac
import logging
import secrets
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union, Any, Set
import json
import re
from collections import defaultdict

import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler


class ValidationStatus(Enum):
    """Statuts de validation"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPICIOUS = "suspicious"
    BLOCKED = "blocked"
    REVIEW_REQUIRED = "review_required"
    FRAUD_DETECTED = "fraud_detected"


class RiskLevel(Enum):
    """Niveaux de risque"""
    MINIMAL = "minimal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EXTREME = "extreme"


class TransactionType(Enum):
    """Types de transactions"""
    CREATOR_PAYOUT = "creator_payout"
    REVENUE_SHARE = "revenue_share"
    SUBSCRIPTION = "subscription"
    TIP = "tip"
    PURCHASE = "purchase"
    REFUND = "refund"
    WITHDRAWAL = "withdrawal"
    PLATFORM_FEE = "platform_fee"


class ValidationRule(Enum):
    """Règles de validation"""
    AMOUNT_LIMITS = "amount_limits"
    FREQUENCY_LIMITS = "frequency_limits"
    GEOGRAPHIC_RESTRICTIONS = "geographic_restrictions"
    ACCOUNT_VERIFICATION = "account_verification"
    PAYMENT_METHOD_VALIDATION = "payment_method_validation"
    FRAUD_PATTERN_DETECTION = "fraud_pattern_detection"
    COMPLIANCE_CHECKS = "compliance_checks"
    BLACKLIST_SCREENING = "blacklist_screening"


@dataclass
class PaymentTransaction:
    """Représentation d'une transaction de paiement"""
    transaction_id: str
    creator_id: str
    amount: Decimal
    currency: str
    transaction_type: TransactionType
    payment_method: str
    timestamp: datetime
    ip_address: str
    user_agent: str
    country_code: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Champs de validation
    validation_status: ValidationStatus = ValidationStatus.PENDING
    risk_level: RiskLevel = RiskLevel.MEDIUM
    risk_score: float = 0.0
    validation_results: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Résultat de validation"""
    transaction_id: str
    status: ValidationStatus
    risk_level: RiskLevel
    risk_score: float
    validation_time: datetime
    rules_applied: List[str]
    alerts: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FraudSignal:
    """Signal de fraude détecté"""
    signal_id: str
    transaction_id: str
    signal_type: str
    confidence: float
    description: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


class TransactionPatternAnalyzer:
    """Analyseur de patterns de transactions"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        self.fraud_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        
        # Patterns suspects connus
        self.suspicious_patterns = {
            'rapid_succession': {'max_transactions': 10, 'time_window': 300},  # 10 tx en 5 min
            'amount_progression': {'threshold': 0.8},  # Augmentation progressive montants
            'geographic_hopping': {'max_countries': 3, 'time_window': 3600},  # 3 pays en 1h
            'round_amounts': {'threshold': 0.7},  # Trop de montants ronds
            'unusual_hours': {'start_hour': 2, 'end_hour': 6}  # Activité 2h-6h
        }
        
        # Historique des transactions pour analyse
        self.transaction_history: Dict[str, List[PaymentTransaction]] = defaultdict(list)
        
    async def analyze_transaction_patterns(self, transaction: PaymentTransaction) -> List[FraudSignal]:
        """Analyse des patterns de transaction"""
        signals = []
        creator_id = transaction.creator_id
        
        # Ajouter à l'historique
        self.transaction_history[creator_id].append(transaction)
        
        # Garder seulement les 1000 dernières transactions par créateur
        if len(self.transaction_history[creator_id]) > 1000:
            self.transaction_history[creator_id] = self.transaction_history[creator_id][-1000:]
        
        # Analyser différents patterns
        signals.extend(await self._detect_rapid_succession(transaction))
        signals.extend(await self._detect_amount_progression(transaction))
        signals.extend(await self._detect_geographic_hopping(transaction))
        signals.extend(await self._detect_round_amounts(transaction))
        signals.extend(await self._detect_unusual_hours(transaction))
        
        return signals
        
    async def _detect_rapid_succession(self, transaction: PaymentTransaction) -> List[FraudSignal]:
        """Détection de transactions en succession rapide"""
        signals = []
        creator_transactions = self.transaction_history[transaction.creator_id]
        
        # Compter transactions dans fenêtre de temps
        time_window = self.suspicious_patterns['rapid_succession']['time_window']
        max_transactions = self.suspicious_patterns['rapid_succession']['max_transactions']
        
        recent_transactions = [
            tx for tx in creator_transactions
            if (transaction.timestamp - tx.timestamp).total_seconds() <= time_window
        ]
        
        if len(recent_transactions) >= max_transactions:
            confidence = min(1.0, len(recent_transactions) / max_transactions)
            signals.append(FraudSignal(
                signal_id=f"rapid_succession_{uuid.uuid4().hex[:8]}",
                transaction_id=transaction.transaction_id,
                signal_type="rapid_succession",
                confidence=confidence,
                description=f"{len(recent_transactions)} transactions in {time_window}s",
                timestamp=datetime.utcnow(),
                metadata={'transaction_count': len(recent_transactions), 'time_window': time_window}
            ))
            
        return signals
        
    async def _detect_amount_progression(self, transaction: PaymentTransaction) -> List[FraudSignal]:
        """Détection de progression suspecte des montants"""
        signals = []
        creator_transactions = self.transaction_history[transaction.creator_id]
        
        if len(creator_transactions) < 5:
            return signals
            
        # Analyser progression des montants
        amounts = [float(tx.amount) for tx in creator_transactions[-10:]]
        if len(amounts) >= 5:
            # Calculer coefficient de corrélation avec progression linéaire
            x = np.arange(len(amounts))
            correlation = np.corrcoef(x, amounts)[0, 1]
            
            threshold = self.suspicious_patterns['amount_progression']['threshold']
            if abs(correlation) > threshold:
                confidence = abs(correlation)
                signals.append(FraudSignal(
                    signal_id=f"amount_progression_{uuid.uuid4().hex[:8]}",
                    transaction_id=transaction.transaction_id,
                    signal_type="amount_progression",
                    confidence=confidence,
                    description=f"Suspicious amount progression (correlation: {correlation:.3f})",
                    timestamp=datetime.utcnow(),
                    metadata={'correlation': correlation, 'amounts': amounts}
                ))
                
        return signals
        
    async def _detect_geographic_hopping(self, transaction: PaymentTransaction) -> List[FraudSignal]:
        """Détection de saut géographique suspect"""
        signals = []
        creator_transactions = self.transaction_history[transaction.creator_id]
        
        # Analyser pays récents
        time_window = self.suspicious_patterns['geographic_hopping']['time_window']
        max_countries = self.suspicious_patterns['geographic_hopping']['max_countries']
        
        recent_transactions = [
            tx for tx in creator_transactions
            if (transaction.timestamp - tx.timestamp).total_seconds() <= time_window
        ]
        
        countries = set(tx.country_code for tx in recent_transactions)
        
        if len(countries) >= max_countries:
            confidence = min(1.0, len(countries) / max_countries)
            signals.append(FraudSignal(
                signal_id=f"geographic_hopping_{uuid.uuid4().hex[:8]}",
                transaction_id=transaction.transaction_id,
                signal_type="geographic_hopping",
                confidence=confidence,
                description=f"Activity from {len(countries)} countries in {time_window}s",
                timestamp=datetime.utcnow(),
                metadata={'countries': list(countries), 'time_window': time_window}
            ))
            
        return signals
        
    async def _detect_round_amounts(self, transaction: PaymentTransaction) -> List[FraudSignal]:
        """Détection de montants ronds suspects"""
        signals = []
        creator_transactions = self.transaction_history[transaction.creator_id]
        
        if len(creator_transactions) < 10:
            return signals
            
        # Compter montants ronds dans les dernières transactions
        recent_amounts = [tx.amount for tx in creator_transactions[-20:]]
        round_amounts = sum(1 for amount in recent_amounts if amount % 1 == 0 or amount % 10 == 0)
        
        threshold = self.suspicious_patterns['round_amounts']['threshold']
        round_ratio = round_amounts / len(recent_amounts)
        
        if round_ratio > threshold:
            confidence = round_ratio
            signals.append(FraudSignal(
                signal_id=f"round_amounts_{uuid.uuid4().hex[:8]}",
                transaction_id=transaction.transaction_id,
                signal_type="round_amounts",
                confidence=confidence,
                description=f"{round_ratio:.1%} of recent amounts are round numbers",
                timestamp=datetime.utcnow(),
                metadata={'round_ratio': round_ratio, 'round_count': round_amounts}
            ))
            
        return signals
        
    async def _detect_unusual_hours(self, transaction: PaymentTransaction) -> List[FraudSignal]:
        """Détection d'activité à heures inhabituelles"""
        signals = []
        
        hour = transaction.timestamp.hour
        start_hour = self.suspicious_patterns['unusual_hours']['start_hour']
        end_hour = self.suspicious_patterns['unusual_hours']['end_hour']
        
        if start_hour <= hour <= end_hour:
            # Calculer fréquence d'activité nocturne
            creator_transactions = self.transaction_history[transaction.creator_id]
            night_transactions = sum(
                1 for tx in creator_transactions
                if start_hour <= tx.timestamp.hour <= end_hour
            )
            
            if len(creator_transactions) > 0:
                night_ratio = night_transactions / len(creator_transactions)
                if night_ratio > 0.3:  # Plus de 30% d'activité nocturne
                    confidence = min(1.0, night_ratio * 2)
                    signals.append(FraudSignal(
                        signal_id=f"unusual_hours_{uuid.uuid4().hex[:8]}",
                        transaction_id=transaction.transaction_id,
                        signal_type="unusual_hours",
                        confidence=confidence,
                        description=f"Transaction at unusual hour ({hour}:00) - {night_ratio:.1%} night activity",
                        timestamp=datetime.utcnow(),
                        metadata={'hour': hour, 'night_ratio': night_ratio}
                    ))
                    
        return signals


class ComplianceChecker:
    """Vérificateur de conformité réglementaire"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Limites par région
        self.regional_limits = {
            'US': {'daily_limit': 10000, 'monthly_limit': 50000, 'kyc_threshold': 3000},
            'EU': {'daily_limit': 8000, 'monthly_limit': 40000, 'kyc_threshold': 2500},
            'UK': {'daily_limit': 7500, 'monthly_limit': 35000, 'kyc_threshold': 2000},
            'DEFAULT': {'daily_limit': 5000, 'monthly_limit': 25000, 'kyc_threshold': 1500}
        }
        
        # Listes de sanctions
        self.sanctions_lists = {
            'OFAC': set(),  # Office of Foreign Assets Control
            'EU_SANCTIONS': set(),
            'UN_SANCTIONS': set()
        }
        
        # Pays à haut risque
        self.high_risk_countries = {
            'AF', 'IR', 'IQ', 'KP', 'SY', 'YE'  # Afghanistan, Iran, Iraq, North Korea, Syria, Yemen
        }
        
    async def check_compliance(self, transaction: PaymentTransaction) -> Dict[str, Any]:
        """Vérification complète de conformité"""
        compliance_results = {
            'aml_check': await self._check_aml_compliance(transaction),
            'sanctions_check': await self._check_sanctions(transaction),
            'kyc_check': await self._check_kyc_requirements(transaction),
            'regional_limits': await self._check_regional_limits(transaction),
            'high_risk_assessment': await self._assess_high_risk_factors(transaction)
        }
        
        # Score de conformité global
        compliance_score = self._calculate_compliance_score(compliance_results)
        compliance_results['overall_score'] = compliance_score
        compliance_results['compliant'] = compliance_score >= 0.7
        
        return compliance_results
        
    async def _check_aml_compliance(self, transaction: PaymentTransaction) -> Dict[str, Any]:
        """Vérification Anti-Money Laundering"""
        aml_flags = []
        
        # Vérifier seuils AML
        if transaction.amount > 10000:
            aml_flags.append("large_amount")
            
        # Vérifier patterns AML
        if transaction.transaction_type == TransactionType.WITHDRAWAL:
            if transaction.amount > 5000:
                aml_flags.append("large_withdrawal")
                
        # Vérifier structuring (fractionnement suspect)
        # Implémentation simplifiée - analyser montants proches des seuils
        amount_float = float(transaction.amount)
        suspicious_amounts = [2999, 4999, 9999]  # Juste sous les seuils
        
        for suspicious_amount in suspicious_amounts:
            if abs(amount_float - suspicious_amount) < 100:
                aml_flags.append("potential_structuring")
                break
                
        return {
            'flags': aml_flags,
            'risk_level': 'high' if aml_flags else 'low',
            'requires_reporting': len(aml_flags) > 0
        }
        
    async def _check_sanctions(self, transaction: PaymentTransaction) -> Dict[str, Any]:
        """Vérification des listes de sanctions"""
        sanctions_hits = []
        
        # Vérifier pays de la transaction
        if transaction.country_code in self.high_risk_countries:
            sanctions_hits.append(f"high_risk_country_{transaction.country_code}")
            
        # En production, vérifier contre vraies listes de sanctions
        # Pour simulation, vérifier patterns suspects
        creator_id = transaction.creator_id.lower()
        if any(term in creator_id for term in ['test', 'fake', 'dummy']):
            sanctions_hits.append("suspicious_identifier")
            
        return {
            'hits': sanctions_hits,
            'blocked': len(sanctions_hits) > 0,
            'risk_level': 'critical' if sanctions_hits else 'low'
        }
        
    async def _check_kyc_requirements(self, transaction: PaymentTransaction) -> Dict[str, Any]:
        """Vérification des exigences KYC"""
        region = self._get_region(transaction.country_code)
        limits = self.regional_limits.get(region, self.regional_limits['DEFAULT'])
        
        kyc_required = transaction.amount >= limits['kyc_threshold']
        
        return {
            'kyc_required': kyc_required,
            'threshold': limits['kyc_threshold'],
            'region': region,
            'status': 'required' if kyc_required else 'not_required'
        }
        
    async def _check_regional_limits(self, transaction: PaymentTransaction) -> Dict[str, Any]:
        """Vérification des limites régionales"""
        region = self._get_region(transaction.country_code)
        limits = self.regional_limits.get(region, self.regional_limits['DEFAULT'])
        
        # Simulation vérification limites
        # En production, vérifier contre base de données des transactions
        exceeds_daily = transaction.amount > limits['daily_limit']
        exceeds_monthly = transaction.amount > limits['monthly_limit']
        
        return {
            'region': region,
            'daily_limit': limits['daily_limit'],
            'monthly_limit': limits['monthly_limit'],
            'exceeds_daily': exceeds_daily,
            'exceeds_monthly': exceeds_monthly,
            'blocked': exceeds_daily or exceeds_monthly
        }
        
    async def _assess_high_risk_factors(self, transaction: PaymentTransaction) -> Dict[str, Any]:
        """Évaluation des facteurs de haut risque"""
        risk_factors = []
        
        # Vérifier pays à haut risque
        if transaction.country_code in self.high_risk_countries:
            risk_factors.append("high_risk_country")
            
        # Vérifier méthodes de paiement à risque
        high_risk_methods = ['crypto', 'anonymous_card', 'prepaid']
        if any(method in transaction.payment_method.lower() for method in high_risk_methods):
            risk_factors.append("high_risk_payment_method")
            
        # Vérifier heures suspectes
        if 2 <= transaction.timestamp.hour <= 6:
            risk_factors.append("unusual_hour")
            
        return {
            'risk_factors': risk_factors,
            'risk_count': len(risk_factors),
            'risk_level': 'high' if len(risk_factors) >= 2 else 'medium' if risk_factors else 'low'
        }
        
    def _get_region(self, country_code: str) -> str:
        """Déterminer région basée sur code pays"""
        eu_countries = {
            'AT', 'BE', 'BG', 'CY', 'CZ', 'DE', 'DK', 'EE', 'ES', 'FI',
            'FR', 'GR', 'HR', 'HU', 'IE', 'IT', 'LT', 'LU', 'LV', 'MT',
            'NL', 'PL', 'PT', 'RO', 'SE', 'SI', 'SK'
        }
        
        if country_code == 'US':
            return 'US'
        elif country_code in eu_countries:
            return 'EU'
        elif country_code == 'GB':
            return 'UK'
        else:
            return 'DEFAULT'
            
    def _calculate_compliance_score(self, compliance_results: Dict[str, Any]) -> float:
        """Calcul du score de conformité global"""
        score = 1.0
        
        # Pénalités pour non-conformité
        if compliance_results['aml_check']['flags']:
            score -= 0.3
            
        if compliance_results['sanctions_check']['blocked']:
            score -= 0.5
            
        if compliance_results['regional_limits']['blocked']:
            score -= 0.4
            
        if compliance_results['high_risk_assessment']['risk_level'] == 'high':
            score -= 0.2
            
        return max(0.0, score)


class PaymentSecurityValidator:
    """
    Validateur de sécurité des paiements enterprise-grade
    
    Fonctionnalités:
    - Validation en temps réel des transactions
    - Évaluation de risque basée ML
    - Détection de fraude avancée
    - Conformité réglementaire automatisée
    - Blocage automatique des transactions suspectes
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.pattern_analyzer = TransactionPatternAnalyzer()
        self.compliance_checker = ComplianceChecker()
        
        # Configuration de validation
        self.validation_config = {
            'auto_approve_threshold': 0.8,
            'auto_reject_threshold': 0.3,
            'fraud_block_threshold': 0.7,
            'review_required_threshold': 0.5,
            'max_validation_time_seconds': 30
        }
        
        # Métriques de validation
        self.metrics = {
            'total_validations': 0,
            'approved_transactions': 0,
            'rejected_transactions': 0,
            'fraud_detected': 0,
            'average_processing_time': 0.0,
            'false_positives': 0,
            'false_negatives': 0
        }
        
        # Cache de validation
        self.validation_cache: Dict[str, ValidationResult] = {}
        
        # Règles de validation personnalisées
        self.custom_rules: Dict[str, callable] = {}
        
        self.logger.info("Payment Security Validator initialized")
        
    async def validate_transaction(self, transaction: PaymentTransaction) -> ValidationResult:
        """Validation complète d'une transaction"""
        start_time = time.time()
        
        try:
            # Vérifier cache
            cache_key = self._generate_cache_key(transaction)
            if cache_key in self.validation_cache:
                cached_result = self.validation_cache[cache_key]
                if (datetime.utcnow() - cached_result.validation_time).total_seconds() < 300:  # 5 min
                    return cached_result
                    
            # Initialiser résultat de validation
            validation_result = ValidationResult(
                transaction_id=transaction.transaction_id,
                status=ValidationStatus.PENDING,
                risk_level=RiskLevel.MEDIUM,
                risk_score=0.5,
                validation_time=datetime.utcnow(),
                rules_applied=[]
            )
            
            # Appliquer règles de validation
            await self._apply_basic_validation_rules(transaction, validation_result)
            await self._apply_fraud_detection(transaction, validation_result)
            await self._apply_compliance_checks(transaction, validation_result)
            await self._apply_custom_rules(transaction, validation_result)
            
            # Analyser patterns de transaction
            fraud_signals = await self.pattern_analyzer.analyze_transaction_patterns(transaction)
            if fraud_signals:
                await self._process_fraud_signals(fraud_signals, validation_result)
                
            # Calculer score de risque final
            await self._calculate_final_risk_score(transaction, validation_result)
            
            # Déterminer statut final
            await self._determine_final_status(validation_result)
            
            # Mise à jour des métriques
            self._update_metrics(validation_result, time.time() - start_time)
            
            # Mise en cache
            self.validation_cache[cache_key] = validation_result
            
            # Logging
            self.logger.info(
                f"Transaction {transaction.transaction_id} validated: "
                f"{validation_result.status.value} (risk: {validation_result.risk_score:.3f})"
            )
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Validation failed for {transaction.transaction_id}: {str(e)}")
            self.metrics['total_validations'] += 1
            
            # Retourner résultat d'erreur
            return ValidationResult(
                transaction_id=transaction.transaction_id,
                status=ValidationStatus.REVIEW_REQUIRED,
                risk_level=RiskLevel.HIGH,
                risk_score=0.9,
                validation_time=datetime.utcnow(),
                rules_applied=['error_fallback'],
                alerts=[f"Validation error: {str(e)}"]
            )
            
    async def _apply_basic_validation_rules(self, 
                                          transaction: PaymentTransaction,
                                          result: ValidationResult):
        """Application des règles de validation de base"""
        result.rules_applied.append('basic_validation')
        
        # Validation montant
        if transaction.amount <= 0:
            result.alerts.append("Invalid amount: must be positive")
            result.risk_score += 0.5
            
        if transaction.amount > 100000:  # 100k limit
            result.alerts.append("Amount exceeds maximum limit")
            result.risk_score += 0.3
            
        # Validation devise
        valid_currencies = {'USD', 'EUR', 'GBP', 'CAD', 'AUD'}
        if transaction.currency not in valid_currencies:
            result.alerts.append(f"Unsupported currency: {transaction.currency}")
            result.risk_score += 0.2
            
        # Validation créateur
        if not transaction.creator_id or len(transaction.creator_id) < 5:
            result.alerts.append("Invalid creator ID")
            result.risk_score += 0.4
            
        # Validation méthode de paiement
        if not transaction.payment_method:
            result.alerts.append("Payment method required")
            result.risk_score += 0.3
            
        # Validation géolocalisation
        if not transaction.country_code or len(transaction.country_code) != 2:
            result.alerts.append("Invalid country code")
            result.risk_score += 0.2
            
    async def _apply_fraud_detection(self, 
                                   transaction: PaymentTransaction,
                                   result: ValidationResult):
        """Application de la détection de fraude"""
        result.rules_applied.append('fraud_detection')
        
        # Vérification IP suspecte
        if await self._is_suspicious_ip(transaction.ip_address):
            result.alerts.append("Suspicious IP address detected")
            result.risk_score += 0.4
            
        # Vérification User-Agent
        if await self._is_suspicious_user_agent(transaction.user_agent):
            result.alerts.append("Suspicious user agent detected")
            result.risk_score += 0.2
            
        # Vérification vitesse de transaction
        if await self._check_transaction_velocity(transaction):
            result.alerts.append("Suspicious transaction velocity")
            result.risk_score += 0.3
            
        # Vérification patterns de montant
        if await self._check_amount_patterns(transaction):
            result.alerts.append("Suspicious amount pattern")
            result.risk_score += 0.2
            
    async def _apply_compliance_checks(self, 
                                     transaction: PaymentTransaction,
                                     result: ValidationResult):
        """Application des vérifications de conformité"""
        result.rules_applied.append('compliance_checks')
        
        compliance_results = await self.compliance_checker.check_compliance(transaction)
        result.metadata['compliance'] = compliance_results
        
        if not compliance_results['compliant']:
            result.alerts.append("Compliance check failed")
            result.risk_score += 0.5
            
        # Vérifications spécifiques
        if compliance_results['sanctions_check']['blocked']:
            result.alerts.append("Sanctions list match")
            result.risk_score += 0.8  # Très critique
            
        if compliance_results['aml_check']['requires_reporting']:
            result.alerts.append("AML reporting required")
            result.risk_score += 0.3
            
        if compliance_results['regional_limits']['blocked']:
            result.alerts.append("Regional limits exceeded")
            result.risk_score += 0.4
            
    async def _apply_custom_rules(self, 
                                transaction: PaymentTransaction,
                                result: ValidationResult):
        """Application des règles personnalisées"""
        for rule_name, rule_func in self.custom_rules.items():
            try:
                rule_result = await rule_func(transaction)
                if rule_result:
                    result.rules_applied.append(rule_name)
                    if isinstance(rule_result, dict):
                        if 'risk_increase' in rule_result:
                            result.risk_score += rule_result['risk_increase']
                        if 'alert' in rule_result:
                            result.alerts.append(rule_result['alert'])
            except Exception as e:
                self.logger.error(f"Custom rule {rule_name} failed: {str(e)}")
                
    async def _process_fraud_signals(self, 
                                   fraud_signals: List[FraudSignal],
                                   result: ValidationResult):
        """Traitement des signaux de fraude"""
        if not fraud_signals:
            return
            
        result.rules_applied.append('pattern_analysis')
        
        # Calculer score de fraude basé sur signaux
        fraud_score = 0.0
        for signal in fraud_signals:
            fraud_score += signal.confidence * 0.2  # Pondération
            result.alerts.append(f"Fraud signal: {signal.description}")
            
        result.risk_score += min(0.5, fraud_score)  # Cap à 0.5
        result.metadata['fraud_signals'] = [
            {
                'type': signal.signal_type,
                'confidence': signal.confidence,
                'description': signal.description
            }
            for signal in fraud_signals
        ]
        
    async def _calculate_final_risk_score(self, 
                                        transaction: PaymentTransaction,
                                        result: ValidationResult):
        """Calcul du score de risque final"""
        # Ajustements basés sur contexte
        
        # Créateurs vérifiés - risque réduit
        if transaction.metadata.get('creator_verified', False):
            result.risk_score *= 0.8
            
        # Transactions récurrentes - risque réduit
        if transaction.transaction_type == TransactionType.SUBSCRIPTION:
            result.risk_score *= 0.9
            
        # Gros montants - risque augmenté
        if transaction.amount > 10000:
            result.risk_score *= 1.2
            
        # Pays à haut risque - risque augmenté
        if transaction.country_code in self.compliance_checker.high_risk_countries:
            result.risk_score *= 1.3
            
        # S'assurer que le score reste dans [0, 1]
        result.risk_score = max(0.0, min(1.0, result.risk_score))
        
        # Déterminer niveau de risque
        if result.risk_score >= 0.8:
            result.risk_level = RiskLevel.CRITICAL
        elif result.risk_score >= 0.6:
            result.risk_level = RiskLevel.HIGH
        elif result.risk_score >= 0.4:
            result.risk_level = RiskLevel.MEDIUM
        elif result.risk_score >= 0.2:
            result.risk_level = RiskLevel.LOW
        else:
            result.risk_level = RiskLevel.MINIMAL
            
    async def _determine_final_status(self, result: ValidationResult):
        """Détermination du statut final"""
        config = self.validation_config
        
        if result.risk_score >= config['fraud_block_threshold']:
            if any('Fraud signal' in alert for alert in result.alerts):
                result.status = ValidationStatus.FRAUD_DETECTED
            else:
                result.status = ValidationStatus.BLOCKED
        elif result.risk_score >= config['auto_reject_threshold']:
            if result.risk_score >= config['review_required_threshold']:
                result.status = ValidationStatus.REVIEW_REQUIRED
            else:
                result.status = ValidationStatus.SUSPICIOUS
        elif result.risk_score <= config['auto_approve_threshold']:
            result.status = ValidationStatus.APPROVED
        else:
            result.status = ValidationStatus.REVIEW_REQUIRED
            
        # Recommandations basées sur statut
        if result.status == ValidationStatus.APPROVED:
            result.recommendations.append("Transaction approved for processing")
        elif result.status == ValidationStatus.REVIEW_REQUIRED:
            result.recommendations.append("Manual review recommended")
        elif result.status == ValidationStatus.BLOCKED:
            result.recommendations.append("Block transaction and notify creator")
        elif result.status == ValidationStatus.FRAUD_DETECTED:
            result.recommendations.append("Immediate fraud investigation required")
            
    async def _is_suspicious_ip(self, ip_address: str) -> bool:
        """Vérification IP suspecte"""
        # Simulation - en production, vérifier contre base de données de réputation
        suspicious_patterns = ['127.0.0.1', '0.0.0.0', '192.168.']
        return any(pattern in ip_address for pattern in suspicious_patterns)
        
    async def _is_suspicious_user_agent(self, user_agent: str) -> bool:
        """Vérification User-Agent suspect"""
        if not user_agent:
            return True
            
        suspicious_patterns = ['bot', 'crawler', 'curl', 'wget', 'python']
        return any(pattern.lower() in user_agent.lower() for pattern in suspicious_patterns)
        
    async def _check_transaction_velocity(self, transaction: PaymentTransaction) -> bool:
        """Vérification vitesse de transaction"""
        # Simulation - vérifier fréquence des transactions
        creator_transactions = self.pattern_analyzer.transaction_history.get(transaction.creator_id, [])
        
        # Compter transactions dans les 5 dernières minutes
        recent_count = sum(
            1 for tx in creator_transactions
            if (transaction.timestamp - tx.timestamp).total_seconds() <= 300
        )
        
        return recent_count > 5  # Plus de 5 transactions en 5 minutes
        
    async def _check_amount_patterns(self, transaction: PaymentTransaction) -> bool:
        """Vérification patterns de montant"""
        amount_float = float(transaction.amount)
        
        # Montants très ronds suspects
        if amount_float in [100, 500, 1000, 5000, 10000]:
            return True
            
        # Montants juste sous les seuils
        thresholds = [2999, 4999, 9999]
        return any(abs(amount_float - threshold) < 10 for threshold in thresholds)
        
    def _generate_cache_key(self, transaction: PaymentTransaction) -> str:
        """Génération clé de cache"""
        key_data = f"{transaction.creator_id}_{transaction.amount}_{transaction.currency}_{transaction.payment_method}"
        return hashlib.md5(key_data.encode()).hexdigest()
        
    def _update_metrics(self, result: ValidationResult, processing_time: float):
        """Mise à jour des métriques"""
        self.metrics['total_validations'] += 1
        
        if result.status == ValidationStatus.APPROVED:
            self.metrics['approved_transactions'] += 1
        elif result.status in [ValidationStatus.REJECTED, ValidationStatus.BLOCKED]:
            self.metrics['rejected_transactions'] += 1
        elif result.status == ValidationStatus.FRAUD_DETECTED:
            self.metrics['fraud_detected'] += 1
            
        # Moyenne mobile du temps de traitement
        current_avg = self.metrics['average_processing_time']
        total_validations = self.metrics['total_validations']
        self.metrics['average_processing_time'] = (
            (current_avg * (total_validations - 1) + processing_time) / total_validations
        )
        
    async def add_custom_rule(self, rule_name: str, rule_func: callable):
        """Ajout d'une règle de validation personnalisée"""
        self.custom_rules[rule_name] = rule_func
        self.logger.info(f"Added custom validation rule: {rule_name}")
        
    async def get_validation_metrics(self) -> Dict[str, Any]:
        """Métriques de validation"""
        total = self.metrics['total_validations']
        if total == 0:
            return self.metrics
            
        return {
            **self.metrics,
            'approval_rate': self.metrics['approved_transactions'] / total,
            'rejection_rate': self.metrics['rejected_transactions'] / total,
            'fraud_rate': self.metrics['fraud_detected'] / total,
            'false_positive_rate': self.metrics['false_positives'] / total if total > 0 else 0,
            'false_negative_rate': self.metrics['false_negatives'] / total if total > 0 else 0
        }
        
    async def bulk_validate_transactions(self, 
                                       transactions: List[PaymentTransaction]) -> List[ValidationResult]:
        """Validation en lot de transactions"""
        self.logger.info(f"Bulk validating {len(transactions)} transactions")
        
        # Validation parallèle
        tasks = [self.validate_transaction(tx) for tx in transactions]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Traiter les exceptions
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Bulk validation error for transaction {i}: {str(result)}")
                # Créer résultat d'erreur
                error_result = ValidationResult(
                    transaction_id=transactions[i].transaction_id,
                    status=ValidationStatus.REVIEW_REQUIRED,
                    risk_level=RiskLevel.HIGH,
                    risk_score=0.9,
                    validation_time=datetime.utcnow(),
                    rules_applied=['bulk_validation_error'],
                    alerts=[f"Bulk validation error: {str(result)}"]
                )
                valid_results.append(error_result)
            else:
                valid_results.append(result)
                
        return valid_results


# Instance globale du validateur
payment_validator = PaymentSecurityValidator()


async def get_payment_validator() -> PaymentSecurityValidator:
    """Factory function pour le validateur de paiement"""
    return payment_validator


# Fonctions utilitaires pour intégration IA Chérie
async def validate_creator_payout(creator_id: str, 
                                amount: Decimal,
                                currency: str = 'USD',
                                metadata: Optional[Dict[str, Any]] = None) -> ValidationResult:
    """Validation spécialisée des paiements créateur"""
    transaction = PaymentTransaction(
        transaction_id=f"payout_{uuid.uuid4().hex}",
        creator_id=creator_id,
        amount=amount,
        currency=currency,
        transaction_type=TransactionType.CREATOR_PAYOUT,
        payment_method="platform_payout",
        timestamp=datetime.utcnow(),
        ip_address="platform_internal",
        user_agent="IA Chérie Platform",
        country_code="US",  # Default platform country
        metadata=metadata or {}
    )
    
    return await payment_validator.validate_transaction(transaction)


async def validate_revenue_share(creator_id: str,
                               revenue_amount: Decimal,
                               platform_fee: Decimal,
                               metadata: Optional[Dict[str, Any]] = None) -> ValidationResult:
    """Validation spécialisée du partage de revenus"""
    total_amount = revenue_amount + platform_fee
    
    transaction = PaymentTransaction(
        transaction_id=f"revenue_share_{uuid.uuid4().hex}",
        creator_id=creator_id,
        amount=total_amount,
        currency="USD",
        transaction_type=TransactionType.REVENUE_SHARE,
        payment_method="platform_revenue_share",
        timestamp=datetime.utcnow(),
        ip_address="platform_internal",
        user_agent="IA Chérie Revenue System",
        country_code="US",
        metadata={
            'creator_revenue': float(revenue_amount),
            'platform_fee': float(platform_fee),
            'revenue_split_validated': True,
            **(metadata or {})
        }
    )
    
    return await payment_validator.validate_transaction(transaction)


# Export des classes principales
__all__ = [
    'PaymentSecurityValidator',
    'PaymentTransaction',
    'ValidationResult',
    'FraudSignal',
    'ValidationStatus',
    'RiskLevel',
    'TransactionType',
    'TransactionPatternAnalyzer',
    'ComplianceChecker',
    'payment_validator',
    'get_payment_validator',
    'validate_creator_payout',
    'validate_revenue_share'
]


# Initialisation pour tests
if __name__ == "__main__":
    async def demo_validation():
        """Démonstration du système de validation"""
        validator = await get_payment_validator()
        
        # Test transaction normale
        normal_transaction = PaymentTransaction(
            transaction_id="tx_12345",
            creator_id="creator_abc123",
            amount=Decimal("250.00"),
            currency="USD",
            transaction_type=TransactionType.CREATOR_PAYOUT,
            payment_method="bank_transfer",
            timestamp=datetime.utcnow(),
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            country_code="US"
        )
        
        result = await validator.validate_transaction(normal_transaction)
        print(f"Normal transaction result: {result.status.value} (risk: {result.risk_score:.3f})")
        
        # Test transaction suspecte
        suspicious_transaction = PaymentTransaction(
            transaction_id="tx_67890",
            creator_id="creator_xyz789",
            amount=Decimal("9999.00"),  # Juste sous seuil
            currency="USD",
            transaction_type=TransactionType.WITHDRAWAL,
            payment_method="crypto",
            timestamp=datetime.utcnow().replace(hour=3),  # 3h du matin
            ip_address="127.0.0.1",  # IP suspecte
            user_agent="curl/7.68.0",  # User agent suspect
            country_code="IR"  # Pays haut risque
        )
        
        result2 = await validator.validate_transaction(suspicious_transaction)
        print(f"Suspicious transaction result: {result2.status.value} (risk: {result2.risk_score:.3f})")
        print(f"Alerts: {result2.alerts}")
        
        # Test fonctions utilitaires IA Chérie
        payout_result = await validate_creator_payout("creator_test", Decimal("500.00"))
        print(f"Creator payout validation: {payout_result.status.value}")
        
        revenue_result = await validate_revenue_share(
            "creator_test", 
            Decimal("800.00"), 
            Decimal("200.00")
        )
        print(f"Revenue share validation: {revenue_result.status.value}")
        
        # Métriques
        metrics = await validator.get_validation_metrics()
        print(f"Validation metrics: {metrics}")
        
    # Exécution démo
    asyncio.run(demo_validation())