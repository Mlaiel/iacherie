"""Revenue Validator - Advanced Revenue Authentication System

Comprehensive revenue validation system for detecting financial fraud, revenue manipulation,
and payment anomalies in the IA-Influencer ecosystem.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum

import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import redis.asyncio as aioredis

try:
    from core.exceptions import RevenueValidationError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    RevenueValidationError = globals().get('RevenueValidationError', Exception)
from ...utils.financial_analyzer import FinancialAnalyzer
from ...data.models.revenue import RevenueTransaction, PaymentMethod
from ...integrations.payment_processors import PaymentProcessorManager

logger = logging.getLogger(__name__)

class RevenueAnomalyType(Enum):
    """Types of revenue anomalies"""
    AMOUNT_MANIPULATION = "amount_manipulation"
    FREQUENCY_ABUSE = "frequency_abuse"
    SOURCE_SPOOFING = "source_spoofing"
    CURRENCY_ARBITRAGE = "currency_arbitrage"
    REFUND_FRAUD = "refund_fraud"
    CHARGEBACK_PATTERN = "chargeback_pattern"
    DUPLICATE_TRANSACTIONS = "duplicate_transactions"
    VELOCITY_FRAUD = "velocity_fraud"
    GEOGRAPHIC_INCONSISTENCY = "geographic_inconsistency"
    PAYMENT_METHOD_ABUSE = "payment_method_abuse"

@dataclass
class RevenueMetrics:
    """Revenue analysis metrics"""
    total_amount: Decimal
    transaction_count: int
    average_amount: Decimal
    median_amount: Decimal
    amount_variance: float
    frequency_per_hour: float
    unique_sources: int
    unique_currencies: int
    refund_rate: float
    chargeback_rate: float
    geographic_spread: int
    payment_methods_used: int

@dataclass
class RevenueValidationResult:
    """Revenue validation result"""
    anomaly_detected: bool
    anomaly_types: List[RevenueAnomalyType]
    confidence: float
    risk_score: float
    irregularities: List[str]
    evidence: Dict[str, Any]
    recommended_actions: List[str]
    validation_timestamp: datetime

class RevenueValidator:
    """
    Advanced Revenue Validation Engine
    
    Validates revenue authenticity through:
    - Statistical anomaly detection
    - Payment pattern analysis
    - Cross-platform verification
    - Historical baseline comparison
    - Real-time fraud detection
    """
    
    def __init__(self, redis_client: Optional[aioredis.Redis] = None):
        self.redis_client = redis_client
        self.financial_analyzer = FinancialAnalyzer()
        self.payment_processor_manager = PaymentProcessorManager()
        
        # ML models for anomaly detection
        self.amount_anomaly_detector = IsolationForest(
            contamination=0.1, 
            random_state=42
        )
        self.frequency_anomaly_detector = IsolationForest(
            contamination=0.05,
            random_state=42
        )
        self.scaler = StandardScaler()
        
        # Revenue validation thresholds
        self.validation_thresholds = {
            'max_amount_increase': 10.0,  # 10x increase
            'max_frequency_increase': 5.0,  # 5x increase
            'max_refund_rate': 0.15,  # 15%
            'max_chargeback_rate': 0.05,  # 5%
            'max_currency_switches': 3,  # per day
            'min_geographic_consistency': 0.7,
            'max_duplicate_threshold': 0.95
        }
        
        # Fraud indicators weights
        self.anomaly_weights = {
            RevenueAnomalyType.AMOUNT_MANIPULATION: 0.25,
            RevenueAnomalyType.FREQUENCY_ABUSE: 0.20,
            RevenueAnomalyType.SOURCE_SPOOFING: 0.15,
            RevenueAnomalyType.CURRENCY_ARBITRAGE: 0.10,
            RevenueAnomalyType.REFUND_FRAUD: 0.10,
            RevenueAnomalyType.CHARGEBACK_PATTERN: 0.08,
            RevenueAnomalyType.DUPLICATE_TRANSACTIONS: 0.07,
            RevenueAnomalyType.VELOCITY_FRAUD: 0.05
        }
        
        logger.info("Revenue Validator initialized successfully")

    async def validate_revenue(
        self,
        user_id: str,
        transaction_data: Dict[str, Any],
        platform: str
    ) -> Dict[str, Any]:
        """
        Comprehensive revenue validation
        
        Args:
            user_id: User identifier
            transaction_data: Transaction data to validate
            platform: Platform where transaction occurred
            
        Returns:
            Revenue validation results
        """
        try:
            # Extract revenue metrics
            current_metrics = await self._extract_revenue_metrics(transaction_data)
            
            # Get historical baselines
            historical_baselines = await self._get_historical_baselines(user_id, platform)
            
            # Detect revenue anomalies
            anomalies = await self._detect_revenue_anomalies(
                current_metrics, historical_baselines, transaction_data, user_id
            )
            
            # Validate against external sources
            external_validation = await self._validate_external_sources(
                transaction_data, platform
            )
            
            # Calculate risk score
            risk_score = await self._calculate_revenue_risk_score(
                anomalies, current_metrics, historical_baselines
            )
            
            # Generate validation result
            result = RevenueValidationResult(
                anomaly_detected=len(anomalies) > 0,
                anomaly_types=list(anomalies.keys()),
                confidence=await self._calculate_validation_confidence(anomalies),
                risk_score=risk_score,
                irregularities=self._extract_irregularities(anomalies),
                evidence=await self._compile_validation_evidence(
                    anomalies, current_metrics, external_validation
                ),
                recommended_actions=await self._generate_revenue_recommendations(
                    anomalies, risk_score
                ),
                validation_timestamp=datetime.now()
            )
            
            # Update revenue history
            await self._update_revenue_history(user_id, current_metrics, platform)
            
            # Cache validation result
            await self._cache_validation_result(user_id, result)
            
            response = {
                'anomaly_detected': result.anomaly_detected,
                'confidence': result.confidence,
                'risk_score': result.risk_score,
                'irregularities': result.irregularities,
                'anomaly_types': [anomaly.value for anomaly in result.anomaly_types],
                'evidence': result.evidence,
                'recommended_actions': result.recommended_actions,
                'validation_timestamp': result.validation_timestamp.isoformat()
            }
            
            logger.info(
                f"Revenue validation completed for user {user_id}: "
                f"anomaly_detected={result.anomaly_detected}, "
                f"risk_score={result.risk_score:.3f}"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Revenue validation failed for user {user_id}: {str(e)}")
            raise RevenueValidationError(f"Revenue validation failed: {str(e)}")

    async def _extract_revenue_metrics(self, transaction_data: Dict[str, Any]) -> RevenueMetrics:
        """Extract comprehensive revenue metrics from transaction data"""
        transactions = transaction_data.get('transactions', [])
        
        if not transactions:
            return RevenueMetrics(
                total_amount=Decimal('0'),
                transaction_count=0,
                average_amount=Decimal('0'),
                median_amount=Decimal('0'),
                amount_variance=0.0,
                frequency_per_hour=0.0,
                unique_sources=0,
                unique_currencies=0,
                refund_rate=0.0,
                chargeback_rate=0.0,
                geographic_spread=0,
                payment_methods_used=0
            )
            
        # Amount metrics
        amounts = [Decimal(str(t.get('amount', 0))) for t in transactions]
        total_amount = sum(amounts)
        average_amount = total_amount / len(amounts) if amounts else Decimal('0')
        median_amount = Decimal(str(np.median([float(a) for a in amounts]))) if amounts else Decimal('0')
        amount_variance = float(np.var([float(a) for a in amounts])) if amounts else 0.0
        
        # Frequency metrics
        timestamps = [t.get('timestamp', 0) for t in transactions]
        if len(timestamps) >= 2:
            time_span_hours = (max(timestamps) - min(timestamps)) / 3600
            frequency_per_hour = len(transactions) / max(time_span_hours, 1)
        else:
            frequency_per_hour = 0.0
            
        # Source diversity metrics
        sources = set(t.get('source', '') for t in transactions)
        currencies = set(t.get('currency', 'USD') for t in transactions)
        payment_methods = set(t.get('payment_method', '') for t in transactions)
        
        # Refund and chargeback metrics
        refunds = [t for t in transactions if t.get('type') == 'refund']
        chargebacks = [t for t in transactions if t.get('type') == 'chargeback']
        
        refund_rate = len(refunds) / len(transactions) if transactions else 0.0
        chargeback_rate = len(chargebacks) / len(transactions) if transactions else 0.0
        
        # Geographic metrics
        countries = set(t.get('country', '') for t in transactions if t.get('country'))
        
        return RevenueMetrics(
            total_amount=total_amount,
            transaction_count=len(transactions),
            average_amount=average_amount,
            median_amount=median_amount,
            amount_variance=amount_variance,
            frequency_per_hour=frequency_per_hour,
            unique_sources=len(sources),
            unique_currencies=len(currencies),
            refund_rate=refund_rate,
            chargeback_rate=chargeback_rate,
            geographic_spread=len(countries),
            payment_methods_used=len(payment_methods)
        )

    async def _get_historical_baselines(
        self, 
        user_id: str, 
        platform: str
    ) -> Dict[str, Any]:
        """Get user's historical revenue baselines"""
        try:
            cache_key = f"revenue_baseline:{user_id}:{platform}"
            cached_baseline = await self.redis_client.get(cache_key)
            
            if cached_baseline:
                import json
                return json.loads(cached_baseline)
                
            # Default baselines for new users
            baseline = {
                'avg_daily_revenue': 0.0,
                'avg_transaction_amount': 0.0,
                'avg_transactions_per_day': 0.0,
                'typical_sources': [],
                'typical_currencies': ['USD'],
                'typical_refund_rate': 0.02,
                'typical_chargeback_rate': 0.01,
                'typical_countries': []
            }
            
            # Cache baseline
            import json
            await self.redis_client.setex(cache_key, 7200, json.dumps(baseline))  # 2 hours
            
            return baseline
            
        except Exception as e:
            logger.error(f"Failed to get revenue baselines for user {user_id}: {str(e)}")
            return {}

    async def _detect_revenue_anomalies(
        self,
        current_metrics: RevenueMetrics,
        historical_baselines: Dict[str, Any],
        transaction_data: Dict[str, Any],
        user_id: str
    ) -> Dict[RevenueAnomalyType, Dict[str, Any]]:
        """Detect various types of revenue anomalies"""
        anomalies = {}
        
        # Amount manipulation detection
        amount_anomaly = await self._detect_amount_manipulation(
            current_metrics, historical_baselines
        )
        if amount_anomaly:
            anomalies[RevenueAnomalyType.AMOUNT_MANIPULATION] = amount_anomaly
            
        # Frequency abuse detection
        frequency_anomaly = await self._detect_frequency_abuse(
            current_metrics, historical_baselines
        )
        if frequency_anomaly:
            anomalies[RevenueAnomalyType.FREQUENCY_ABUSE] = frequency_anomaly
            
        # Source spoofing detection
        source_anomaly = await self._detect_source_spoofing(
            current_metrics, historical_baselines, transaction_data
        )
        if source_anomaly:
            anomalies[RevenueAnomalyType.SOURCE_SPOOFING] = source_anomaly
            
        # Currency arbitrage detection
        currency_anomaly = await self._detect_currency_arbitrage(
            current_metrics, transaction_data
        )
        if currency_anomaly:
            anomalies[RevenueAnomalyType.CURRENCY_ARBITRAGE] = currency_anomaly
            
        # Refund fraud detection
        refund_anomaly = await self._detect_refund_fraud(
            current_metrics, historical_baselines
        )
        if refund_anomaly:
            anomalies[RevenueAnomalyType.REFUND_FRAUD] = refund_anomaly
            
        # Duplicate transaction detection
        duplicate_anomaly = await self._detect_duplicate_transactions(transaction_data)
        if duplicate_anomaly:
            anomalies[RevenueAnomalyType.DUPLICATE_TRANSACTIONS] = duplicate_anomaly
            
        # Velocity fraud detection
        velocity_anomaly = await self._detect_velocity_fraud(
            current_metrics, transaction_data
        )
        if velocity_anomaly:
            anomalies[RevenueAnomalyType.VELOCITY_FRAUD] = velocity_anomaly
            
        return anomalies

    async def _detect_amount_manipulation(
        self,
        current_metrics: RevenueMetrics,
        historical_baselines: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Detect amount manipulation anomalies"""
        try:
            baseline_avg = historical_baselines.get('avg_transaction_amount', 0)
            current_avg = float(current_metrics.average_amount)
            
            # Check for dramatic amount increases
            if baseline_avg > 0:
                increase_factor = current_avg / baseline_avg
                if increase_factor > self.validation_thresholds['max_amount_increase']:
                    return {
                        'type': 'dramatic_amount_increase',
                        'increase_factor': increase_factor,
                        'baseline_amount': baseline_avg,
                        'current_amount': current_avg,
                        'confidence': min(1.0, (increase_factor - 1) * 0.1)
                    }
                    
            # Check for unusual amount variance
            if current_metrics.amount_variance > 1000000:  # Very high variance
                return {
                    'type': 'unusual_amount_variance',
                    'variance': current_metrics.amount_variance,
                    'confidence': 0.7
                }
                
            return None
            
        except Exception as e:
            logger.error(f"Amount manipulation detection failed: {str(e)}")
            return None

    async def _detect_frequency_abuse(
        self,
        current_metrics: RevenueMetrics,
        historical_baselines: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Detect frequency abuse anomalies"""
        try:
            baseline_frequency = historical_baselines.get('avg_transactions_per_day', 0) / 24
            current_frequency = current_metrics.frequency_per_hour
            
            if baseline_frequency > 0:
                frequency_factor = current_frequency / baseline_frequency
                if frequency_factor > self.validation_thresholds['max_frequency_increase']:
                    return {
                        'type': 'excessive_transaction_frequency',
                        'frequency_factor': frequency_factor,
                        'baseline_frequency': baseline_frequency,
                        'current_frequency': current_frequency,
                        'confidence': min(1.0, (frequency_factor - 1) * 0.2)
                    }
                    
            # Check for burst transactions
            if current_metrics.frequency_per_hour > 50:  # More than 50 transactions per hour
                return {
                    'type': 'burst_transaction_pattern',
                    'frequency_per_hour': current_metrics.frequency_per_hour,
                    'confidence': 0.8
                }
                
            return None
            
        except Exception as e:
            logger.error(f"Frequency abuse detection failed: {str(e)}")
            return None

    async def _detect_source_spoofing(
        self,
        current_metrics: RevenueMetrics,
        historical_baselines: Dict[str, Any],
        transaction_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Detect source spoofing anomalies"""
        try:
            typical_sources = set(historical_baselines.get('typical_sources', []))
            transactions = transaction_data.get('transactions', [])
            current_sources = set(t.get('source', '') for t in transactions)
            
            # Check for completely new sources
            if typical_sources and not typical_sources.intersection(current_sources):
                return {
                    'type': 'all_new_sources',
                    'typical_sources': list(typical_sources)[:5],  # Limit for privacy
                    'current_sources': list(current_sources)[:5],
                    'confidence': 0.7
                }
                
            # Check for suspicious source diversity
            if current_metrics.unique_sources > 10 and current_metrics.transaction_count < 20:
                return {
                    'type': 'excessive_source_diversity',
                    'unique_sources': current_metrics.unique_sources,
                    'transaction_count': current_metrics.transaction_count,
                    'confidence': 0.6
                }
                
            return None
            
        except Exception as e:
            logger.error(f"Source spoofing detection failed: {str(e)}")
            return None

    async def _detect_currency_arbitrage(
        self,
        current_metrics: RevenueMetrics,
        transaction_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Detect currency arbitrage anomalies"""
        try:
            if current_metrics.unique_currencies > self.validation_thresholds['max_currency_switches']:
                transactions = transaction_data.get('transactions', [])
                
                # Analyze currency switching patterns
                currency_switches = 0
                prev_currency = None
                
                for transaction in sorted(transactions, key=lambda x: x.get('timestamp', 0)):
                    current_currency = transaction.get('currency', 'USD')
                    if prev_currency and prev_currency != current_currency:
                        currency_switches += 1
                    prev_currency = current_currency
                    
                if currency_switches > 5:  # Frequent currency switching
                    return {
                        'type': 'frequent_currency_switching',
                        'currency_switches': currency_switches,
                        'unique_currencies': current_metrics.unique_currencies,
                        'confidence': min(1.0, currency_switches * 0.1)
                    }
                    
            return None
            
        except Exception as e:
            logger.error(f"Currency arbitrage detection failed: {str(e)}")
            return None

    async def _detect_refund_fraud(
        self,
        current_metrics: RevenueMetrics,
        historical_baselines: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Detect refund fraud patterns"""
        try:
            typical_refund_rate = historical_baselines.get('typical_refund_rate', 0.02)
            current_refund_rate = current_metrics.refund_rate
            
            if current_refund_rate > self.validation_thresholds['max_refund_rate']:
                return {
                    'type': 'excessive_refund_rate',
                    'current_refund_rate': current_refund_rate,
                    'typical_refund_rate': typical_refund_rate,
                    'threshold': self.validation_thresholds['max_refund_rate'],
                    'confidence': min(1.0, current_refund_rate * 2)
                }
                
            # Check for chargeback patterns
            if current_metrics.chargeback_rate > self.validation_thresholds['max_chargeback_rate']:
                return {
                    'type': 'excessive_chargeback_rate',
                    'chargeback_rate': current_metrics.chargeback_rate,
                    'confidence': min(1.0, current_metrics.chargeback_rate * 5)
                }
                
            return None
            
        except Exception as e:
            logger.error(f"Refund fraud detection failed: {str(e)}")
            return None

    async def _detect_duplicate_transactions(
        self, 
        transaction_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Detect duplicate transaction patterns"""
        try:
            transactions = transaction_data.get('transactions', [])
            
            if len(transactions) < 2:
                return None
                
            # Create transaction signatures
            signatures = []
            for transaction in transactions:
                signature = f"{transaction.get('amount', 0)}_{transaction.get('currency', 'USD')}_{transaction.get('payment_method', '')}"
                signatures.append(signature)
                
            # Count duplicates
            from collections import Counter
            signature_counts = Counter(signatures)
            
            duplicates = {sig: count for sig, count in signature_counts.items() if count > 1}
            
            if duplicates:
                total_duplicates = sum(count - 1 for count in duplicates.values())
                duplicate_ratio = total_duplicates / len(transactions)
                
                if duplicate_ratio > 0.3:  # More than 30% duplicates
                    return {
                        'type': 'high_duplicate_ratio',
                        'duplicate_ratio': duplicate_ratio,
                        'duplicate_signatures': list(duplicates.keys())[:5],
                        'confidence': min(1.0, duplicate_ratio * 2)
                    }
                    
            return None
            
        except Exception as e:
            logger.error(f"Duplicate transaction detection failed: {str(e)}")
            return None

    async def _detect_velocity_fraud(
        self,
        current_metrics: RevenueMetrics,
        transaction_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Detect velocity fraud patterns"""
        try:
            transactions = transaction_data.get('transactions', [])
            
            if len(transactions) < 5:
                return None
                
            # Analyze transaction timing
            timestamps = sorted([t.get('timestamp', 0) for t in transactions])
            intervals = [timestamps[i] - timestamps[i-1] for i in range(1, len(timestamps))]
            
            # Check for suspiciously regular intervals
            if len(set(intervals)) <= 2 and len(intervals) >= 5:
                return {
                    'type': 'uniform_transaction_timing',
                    'unique_intervals': len(set(intervals)),
                    'total_transactions': len(transactions),
                    'confidence': 0.8
                }
                
            # Check for micro-transactions velocity
            small_amounts = [t for t in transactions if float(t.get('amount', 0)) < 1.0]
            if len(small_amounts) > len(transactions) * 0.8:  # 80% micro-transactions
                return {
                    'type': 'micro_transaction_velocity',
                    'micro_transaction_ratio': len(small_amounts) / len(transactions),
                    'confidence': 0.7
                }
                
            return None
            
        except Exception as e:
            logger.error(f"Velocity fraud detection failed: {str(e)}")
            return None

    async def _validate_external_sources(
        self, 
        transaction_data: Dict[str, Any], 
        platform: str
    ) -> Dict[str, Any]:
        """Validate revenue against external sources"""
        try:
            validation_result = {
                'platform_api_verified': False,
                'payment_processor_verified': False,
                'discrepancies': [],
                'confidence': 0.0
            }
            
            # Validate against platform APIs (YouTube, Instagram, etc.)
            platform_validation = await self._validate_platform_api(transaction_data, platform)
            validation_result.update(platform_validation)
            
            # Validate against payment processors
            processor_validation = await self._validate_payment_processors(transaction_data)
            validation_result['payment_processor_verified'] = processor_validation.get('verified', False)
            
            # Calculate overall validation confidence
            verification_count = sum([
                validation_result['platform_api_verified'],
                validation_result['payment_processor_verified']
            ])
            validation_result['confidence'] = verification_count / 2.0
            
            return validation_result
            
        except Exception as e:
            logger.error(f"External validation failed: {str(e)}")
            return {'platform_api_verified': False, 'payment_processor_verified': False, 'confidence': 0.0}

    async def _validate_platform_api(
        self, 
        transaction_data: Dict[str, Any], 
        platform: str
    ) -> Dict[str, Any]:
        """Validate revenue against platform APIs"""
        try:
            # This would integrate with actual platform APIs
            # For now, return simulated validation
            return {
                'platform_api_verified': True,
                'platform_discrepancy': 0.0,
                'platform_confidence': 0.8
            }
            
        except Exception as e:
            logger.error(f"Platform API validation failed: {str(e)}")
            return {'platform_api_verified': False, 'platform_confidence': 0.0}

    async def _validate_payment_processors(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate against payment processor records"""
        try:
            # This would integrate with payment processors (Stripe, PayPal, etc.)
            # For now, return simulated validation
            return {
                'verified': True,
                'processor_confidence': 0.9
            }
            
        except Exception as e:
            logger.error(f"Payment processor validation failed: {str(e)}")
            return {'verified': False, 'processor_confidence': 0.0}

    async def _calculate_revenue_risk_score(
        self,
        anomalies: Dict[RevenueAnomalyType, Dict[str, Any]],
        current_metrics: RevenueMetrics,
        historical_baselines: Dict[str, Any]
    ) -> float:
        """Calculate comprehensive revenue risk score"""
        if not anomalies:
            return 0.0
            
        risk_score = 0.0
        
        for anomaly_type, anomaly_data in anomalies.items():
            anomaly_confidence = anomaly_data.get('confidence', 0.0)
            anomaly_weight = self.anomaly_weights.get(anomaly_type, 0.1)
            
            risk_score += anomaly_confidence * anomaly_weight
            
        # Apply severity multiplier for critical anomalies
        critical_anomalies = [
            RevenueAnomalyType.AMOUNT_MANIPULATION,
            RevenueAnomalyType.SOURCE_SPOOFING,
            RevenueAnomalyType.REFUND_FRAUD
        ]
        
        for anomaly_type in critical_anomalies:
            if anomaly_type in anomalies:
                risk_score *= 1.5
                
        return min(1.0, risk_score)

    async def _calculate_validation_confidence(
        self, 
        anomalies: Dict[RevenueAnomalyType, Dict[str, Any]]
    ) -> float:
        """Calculate validation confidence score"""
        if not anomalies:
            return 1.0
            
        # Average confidence of detected anomalies
        confidences = [anomaly.get('confidence', 0.0) for anomaly in anomalies.values()]
        return np.mean(confidences) if confidences else 0.0

    def _extract_irregularities(
        self, 
        anomalies: Dict[RevenueAnomalyType, Dict[str, Any]]
    ) -> List[str]:
        """Extract irregularity descriptions from anomalies"""
        irregularities = []
        
        for anomaly_type, anomaly_data in anomalies.items():
            anomaly_description = anomaly_data.get('type', anomaly_type.value)
            irregularities.append(f"{anomaly_type.value}: {anomaly_description}")
            
        return irregularities

    async def _compile_validation_evidence(
        self,
        anomalies: Dict[RevenueAnomalyType, Dict[str, Any]],
        current_metrics: RevenueMetrics,
        external_validation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compile comprehensive validation evidence"""
        evidence = {
            'current_metrics': {
                'total_amount': float(current_metrics.total_amount),
                'transaction_count': current_metrics.transaction_count,
                'average_amount': float(current_metrics.average_amount),
                'frequency_per_hour': current_metrics.frequency_per_hour,
                'refund_rate': current_metrics.refund_rate,
                'unique_sources': current_metrics.unique_sources
            },
            'anomaly_details': {
                anomaly_type.value: anomaly_data 
                for anomaly_type, anomaly_data in anomalies.items()
            },
            'external_validation': external_validation,
            'risk_indicators': self._extract_risk_indicators(anomalies, current_metrics)
        }
        
        return evidence

    def _extract_risk_indicators(
        self,
        anomalies: Dict[RevenueAnomalyType, Dict[str, Any]],
        current_metrics: RevenueMetrics
    ) -> List[str]:
        """Extract key risk indicators"""
        indicators = []
        
        # High-impact indicators
        if RevenueAnomalyType.AMOUNT_MANIPULATION in anomalies:
            indicators.append("Suspicious amount manipulation detected")
            
        if RevenueAnomalyType.FREQUENCY_ABUSE in anomalies:
            indicators.append("Abnormal transaction frequency")
            
        if RevenueAnomalyType.SOURCE_SPOOFING in anomalies:
            indicators.append("Potential source spoofing")
            
        # Volume-based indicators
        if current_metrics.refund_rate > 0.1:
            indicators.append("Elevated refund rate")
            
        if current_metrics.unique_sources > 15:
            indicators.append("Excessive source diversity")
            
        return indicators[:5]  # Limit to top 5

    async def _generate_revenue_recommendations(
        self,
        anomalies: Dict[RevenueAnomalyType, Dict[str, Any]],
        risk_score: float
    ) -> List[str]:
        """Generate recommended actions based on validation results"""
        recommendations = []
        
        if risk_score >= 0.8:
            recommendations.extend([
                "Immediately suspend revenue payouts",
                "Initiate manual investigation",
                "Verify all recent transactions",
                "Contact payment processors for verification"
            ])
        elif risk_score >= 0.6:
            recommendations.extend([
                "Hold revenue payouts for review",
                "Require additional documentation",
                "Increase monitoring frequency",
                "Verify high-value transactions"
            ])
        elif risk_score >= 0.3:
            recommendations.extend([
                "Apply enhanced monitoring",
                "Flag for periodic review",
                "Request revenue source documentation"
            ])
            
        # Specific recommendations based on anomaly types
        if RevenueAnomalyType.REFUND_FRAUD in anomalies:
            recommendations.append("Review refund patterns and policies")
            
        if RevenueAnomalyType.DUPLICATE_TRANSACTIONS in anomalies:
            recommendations.append("Implement duplicate transaction detection")
            
        if RevenueAnomalyType.CURRENCY_ARBITRAGE in anomalies:
            recommendations.append("Review currency exchange patterns")
            
        return list(set(recommendations))  # Remove duplicates

    async def _update_revenue_history(
        self, 
        user_id: str, 
        metrics: RevenueMetrics, 
        platform: str
    ):
        """Update user's revenue history for baseline calculations"""
        try:
            history_key = f"revenue_history:{user_id}:{platform}"
            
            revenue_record = {
                'timestamp': datetime.now().isoformat(),
                'total_amount': float(metrics.total_amount),
                'transaction_count': metrics.transaction_count,
                'average_amount': float(metrics.average_amount),
                'frequency_per_hour': metrics.frequency_per_hour,
                'refund_rate': metrics.refund_rate,
                'unique_sources': metrics.unique_sources
            }
            
            # Add to history (keep last 50 records)
            import json
            await self.redis_client.lpush(history_key, json.dumps(revenue_record))
            await self.redis_client.ltrim(history_key, 0, 49)
            await self.redis_client.expire(history_key, 86400 * 90)  # 90 days
            
        except Exception as e:
            logger.error(f"Failed to update revenue history for user {user_id}: {str(e)}")

    async def _cache_validation_result(self, user_id: str, result: RevenueValidationResult):
        """Cache validation result for quick access"""
        try:
            cache_key = f"revenue_validation:{user_id}"
            
            cached_result = {
                'anomaly_detected': result.anomaly_detected,
                'risk_score': result.risk_score,
                'anomaly_types': [a.value for a in result.anomaly_types],
                'validation_timestamp': result.validation_timestamp.isoformat()
            }
            
            import json
            await self.redis_client.setex(cache_key, 3600, json.dumps(cached_result))  # 1 hour
            
        except Exception as e:
            logger.error(f"Failed to cache validation result for user {user_id}: {str(e)}")

    async def get_revenue_analytics(
        self, 
        user_id: str, 
        platform: str, 
        days: int = 30
    ) -> Dict[str, Any]:
        """Get comprehensive revenue analytics for a user"""
        try:
            history_key = f"revenue_history:{user_id}:{platform}"
            history_records = await self.redis_client.lrange(history_key, 0, -1)
            
            if not history_records:
                return {
                    'analytics': 'Insufficient historical data',
                    'total_records': 0
                }
                
            # Parse records
            import json
            parsed_records = []
            for record in history_records:
                try:
                    parsed_records.append(json.loads(record))
                except:
                    continue
                    
            # Filter by date range
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_records = [
                record for record in parsed_records
                if datetime.fromisoformat(record['timestamp']) > cutoff_date
            ]
            
            if not recent_records:
                return {
                    'analytics': 'No recent revenue data',
                    'total_records': len(parsed_records)
                }
                
            # Calculate analytics
            total_amounts = [r['total_amount'] for r in recent_records]
            transaction_counts = [r['transaction_count'] for r in recent_records]
            
            analytics = {
                'total_revenue': sum(total_amounts),
                'average_daily_revenue': np.mean(total_amounts),
                'revenue_trend': self._calculate_trend([
                    datetime.fromisoformat(r['timestamp']) for r in recent_records
                ], total_amounts),
                'total_transactions': sum(transaction_counts),
                'average_transactions_per_day': np.mean(transaction_counts),
                'average_refund_rate': np.mean([r.get('refund_rate', 0) for r in recent_records]),
                'revenue_volatility': np.std(total_amounts),
                'data_points': len(recent_records),
                'time_range_days': days
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get revenue analytics for user {user_id}: {str(e)}")
            return {'error': str(e)}

    def _calculate_trend(self, timestamps: List[datetime], values: List[float]) -> float:
        """Calculate trend direction for revenue over time"""
        if len(timestamps) < 2 or len(values) < 2:
            return 0.0
            
        # Convert to numeric for correlation
        numeric_times = [(t - timestamps[0]).total_seconds() for t in timestamps]
        
        # Calculate correlation coefficient
        correlation_matrix = np.corrcoef(numeric_times, values)
        correlation = correlation_matrix[0, 1]
        
        return correlation if not np.isnan(correlation) else 0.0
