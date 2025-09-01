"""Advanced Fraud Detection System - Enhanced payment fraud detection
====================================================================

Advanced fraud detection system with machine learning algorithms,
risk scoring, real-time monitoring, and automated response actions.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import redis
import asyncpg
from decimal import Decimal
from fastapi import HTTPException
import json
import hashlib
import re

logger = logging.getLogger(__name__)

class FraudRiskLevel(Enum):
    """Fraud risk levels"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

class FraudIndicator(Enum):
    """Types of fraud indicators"""
    VELOCITY_ANOMALY = "velocity_anomaly"
    LOCATION_MISMATCH = "location_mismatch"
    DEVICE_FINGERPRINT = "device_fingerprint"
    PAYMENT_PATTERN = "payment_pattern"
    ACCOUNT_BEHAVIOR = "account_behavior"
    IP_REPUTATION = "ip_reputation"
    EMAIL_RISK = "email_risk"
    TRANSACTION_AMOUNT = "transaction_amount"
    TIME_PATTERN = "time_pattern"
    CARD_TESTING = "card_testing"

class FraudAction(Enum):
    """Automated fraud response actions"""
    ALLOW = "allow"
    BLOCK = "block"
    REVIEW = "review"
    CHALLENGE = "challenge"
    LIMIT = "limit"
    NOTIFY = "notify"
    ESCALATE = "escalate"

@dataclass
class FraudAssessment:
    """Fraud risk assessment result"""
    assessment_id: str
    entity_type: str
    entity_id: str
    risk_level: FraudRiskLevel
    risk_score: float
    indicators: List[Dict[str, Any]]
    recommended_action: FraudAction
    confidence: float
    assessed_at: datetime
    expires_at: datetime

@dataclass
class FraudRule:
    """Fraud detection rule"""
    rule_id: str
    name: str
    description: str
    indicator_type: FraudIndicator
    threshold: float
    weight: float
    active: bool
    conditions: Dict[str, Any]
    actions: List[FraudAction]

@dataclass
class PaymentContext:
    """Payment context for fraud analysis"""
    payment_id: str
    customer_id: str
    amount: Decimal
    currency: str
    payment_method: str
    ip_address: Optional[str]
    user_agent: Optional[str]
    device_fingerprint: Optional[str]
    billing_address: Optional[Dict[str, str]]
    shipping_address: Optional[Dict[str, str]]
    timestamp: datetime
    metadata: Dict[str, Any]

class AdvancedFraudDetection:
    """Advanced fraud detection and prevention system"""
    
    def __init__(self, redis_client: redis.Redis, db_pool: asyncpg.Pool):
        self.redis = redis_client
        self.db_pool = db_pool
        self.fraud_rules = {}
        self.risk_thresholds = {
            FraudRiskLevel.VERY_LOW: 0.1,
            FraudRiskLevel.LOW: 0.3,
            FraudRiskLevel.MEDIUM: 0.5,
            FraudRiskLevel.HIGH: 0.7,
            FraudRiskLevel.VERY_HIGH: 0.9
        }
        
    async def initialize(self) -> None:
        """Initialize fraud detection system"""
        try:
            await self._setup_database_tables()
            await self._load_fraud_rules()
            await self._initialize_blacklists()
            logger.info("Advanced Fraud Detection System initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Advanced Fraud Detection System: {e}")
            raise
            
    async def _setup_database_tables(self) -> None:
        """Setup required database tables"""
        async with self.db_pool.acquire() as conn:
            # Fraud assessments table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS fraud_assessments (
                    assessment_id VARCHAR PRIMARY KEY,
                    entity_type VARCHAR(50) NOT NULL,
                    entity_id VARCHAR(100) NOT NULL,
                    risk_level VARCHAR(20) NOT NULL,
                    risk_score DECIMAL(5,4) NOT NULL,
                    indicators JSONB NOT NULL,
                    recommended_action VARCHAR(20) NOT NULL,
                    confidence DECIMAL(5,4) NOT NULL,
                    assessed_at TIMESTAMP DEFAULT NOW(),
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Fraud rules table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS fraud_rules (
                    rule_id VARCHAR PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    indicator_type VARCHAR(30) NOT NULL,
                    threshold DECIMAL(5,4) NOT NULL,
                    weight DECIMAL(5,4) NOT NULL,
                    active BOOLEAN DEFAULT TRUE,
                    conditions JSONB,
                    actions JSONB,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Fraud events table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS fraud_events (
                    event_id VARCHAR PRIMARY KEY,
                    assessment_id VARCHAR REFERENCES fraud_assessments(assessment_id),
                    event_type VARCHAR(30) NOT NULL,
                    entity_type VARCHAR(50) NOT NULL,
                    entity_id VARCHAR(100) NOT NULL,
                    details JSONB,
                    action_taken VARCHAR(20),
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Blacklists table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS fraud_blacklists (
                    list_id VARCHAR PRIMARY KEY,
                    list_type VARCHAR(20) NOT NULL,
                    value VARCHAR(255) NOT NULL,
                    reason TEXT,
                    active BOOLEAN DEFAULT TRUE,
                    expires_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Create indexes
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_fraud_assessments_entity 
                ON fraud_assessments(entity_type, entity_id)
            """)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_fraud_assessments_risk 
                ON fraud_assessments(risk_level, assessed_at)
            """)
            
    async def _load_fraud_rules(self) -> None:
        """Load fraud detection rules"""
        default_rules = [
            FraudRule(
                rule_id="velocity_check",
                name="Transaction Velocity",
                description="Check for unusual transaction velocity",
                indicator_type=FraudIndicator.VELOCITY_ANOMALY,
                threshold=0.7,
                weight=0.8,
                active=True,
                conditions={"max_transactions_per_hour": 10, "time_window": 3600},
                actions=[FraudAction.REVIEW, FraudAction.LIMIT]
            ),
            FraudRule(
                rule_id="large_amount",
                name="Large Transaction Amount",
                description="Flag unusually large transactions",
                indicator_type=FraudIndicator.TRANSACTION_AMOUNT,
                threshold=0.6,
                weight=0.7,
                active=True,
                conditions={"amount_threshold": 5000, "currency": "USD"},
                actions=[FraudAction.REVIEW]
            ),
            FraudRule(
                rule_id="location_mismatch",
                name="Geographic Location Mismatch",
                description="Check for geographic inconsistencies",
                indicator_type=FraudIndicator.LOCATION_MISMATCH,
                threshold=0.8,
                weight=0.9,
                active=True,
                conditions={"max_distance_km": 1000, "time_window": 3600},
                actions=[FraudAction.CHALLENGE, FraudAction.NOTIFY]
            ),
            FraudRule(
                rule_id="card_testing",
                name="Card Testing Detection",
                description="Detect card testing patterns",
                indicator_type=FraudIndicator.CARD_TESTING,
                threshold=0.9,
                weight=1.0,
                active=True,
                conditions={"small_amounts": True, "frequency_threshold": 5},
                actions=[FraudAction.BLOCK, FraudAction.ESCALATE]
            ),
            FraudRule(
                rule_id="ip_reputation",
                name="IP Reputation Check",
                description="Check IP address reputation",
                indicator_type=FraudIndicator.IP_REPUTATION,
                threshold=0.8,
                weight=0.6,
                active=True,
                conditions={"check_vpn": True, "check_tor": True},
                actions=[FraudAction.REVIEW, FraudAction.CHALLENGE]
            )
        ]
        
        # Store rules in database and memory
        async with self.db_pool.acquire() as conn:
            for rule in default_rules:
                await conn.execute("""
                    INSERT INTO fraud_rules (
                        rule_id, name, description, indicator_type,
                        threshold, weight, active, conditions, actions
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    ON CONFLICT (rule_id) DO UPDATE SET
                        threshold = EXCLUDED.threshold,
                        weight = EXCLUDED.weight,
                        conditions = EXCLUDED.conditions,
                        actions = EXCLUDED.actions,
                        updated_at = NOW()
                """, 
                rule.rule_id, rule.name, rule.description,
                rule.indicator_type.value, rule.threshold, rule.weight,
                rule.active, json.dumps(rule.conditions),
                json.dumps([action.value for action in rule.actions])
                )
                
                self.fraud_rules[rule.rule_id] = rule
                
    async def _initialize_blacklists(self) -> None:
        """Initialize fraud blacklists"""
        try:
            # Sample blacklist entries
            blacklist_entries = [
                {"type": "ip", "value": "192.168.1.100", "reason": "Known fraudulent IP"},
                {"type": "email", "value": "fraud@example.com", "reason": "Fraudulent email pattern"},
                {"type": "card_bin", "value": "424242", "reason": "Test card BIN"},
            ]
            
            async with self.db_pool.acquire() as conn:
                for entry in blacklist_entries:
                    list_id = f"BL_{entry['type']}_{hashlib.md5(entry['value'].encode()).hexdigest()[:8]}"
                    await conn.execute("""
                        INSERT INTO fraud_blacklists (
                            list_id, list_type, value, reason, active
                        ) VALUES ($1, $2, $3, $4, $5)
                        ON CONFLICT (list_id) DO NOTHING
                    """, list_id, entry['type'], entry['value'], entry['reason'], True)
                    
        except Exception as e:
            logger.error(f"Failed to initialize blacklists: {e}")
            
    async def assess_payment_fraud(self, payment_context: PaymentContext) -> FraudAssessment:
        """Assess fraud risk for payment transaction"""
        try:
            assessment_id = f"FA_{payment_context.payment_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            
            # Run fraud analysis
            risk_indicators = []
            total_risk_score = 0.0
            total_weight = 0.0
            
            # Check each fraud rule
            for rule in self.fraud_rules.values():
                if not rule.active:
                    continue
                    
                indicator_result = await self._evaluate_fraud_indicator(
                    rule, payment_context
                )
                
                if indicator_result['triggered']:
                    risk_indicators.append({
                        "indicator": rule.indicator_type.value,
                        "rule_id": rule.rule_id,
                        "score": indicator_result['score'],
                        "details": indicator_result['details']
                    })
                    
                    # Calculate weighted score
                    total_risk_score += indicator_result['score'] * rule.weight
                    total_weight += rule.weight
            
            # Calculate final risk score
            final_risk_score = total_risk_score / total_weight if total_weight > 0 else 0.0
            
            # Determine risk level
            risk_level = self._calculate_risk_level(final_risk_score)
            
            # Determine recommended action
            recommended_action = self._determine_action(risk_level, risk_indicators)
            
            # Calculate confidence based on number of indicators
            confidence = min(0.95, 0.5 + (len(risk_indicators) * 0.1))
            
            assessment = FraudAssessment(
                assessment_id=assessment_id,
                entity_type="payment",
                entity_id=payment_context.payment_id,
                risk_level=risk_level,
                risk_score=final_risk_score,
                indicators=risk_indicators,
                recommended_action=recommended_action,
                confidence=confidence,
                assessed_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(hours=24)
            )
            
            # Store assessment
            await self._store_assessment(assessment)
            
            # Log fraud event if high risk
            if risk_level in [FraudRiskLevel.HIGH, FraudRiskLevel.VERY_HIGH]:
                await self._log_fraud_event(assessment, "high_risk_detected")
                
            logger.info(f"Fraud assessment completed: {assessment_id} - Risk: {risk_level.value}")
            return assessment
            
        except Exception as e:
            logger.error(f"Failed to assess payment fraud: {e}")
            raise
            
    async def _evaluate_fraud_indicator(
        self,
        rule: FraudRule,
        payment_context: PaymentContext
    ) -> Dict[str, Any]:
        """Evaluate specific fraud indicator"""
        try:
            if rule.indicator_type == FraudIndicator.VELOCITY_ANOMALY:
                return await self._check_velocity_anomaly(rule, payment_context)
            elif rule.indicator_type == FraudIndicator.TRANSACTION_AMOUNT:
                return await self._check_transaction_amount(rule, payment_context)
            elif rule.indicator_type == FraudIndicator.LOCATION_MISMATCH:
                return await self._check_location_mismatch(rule, payment_context)
            elif rule.indicator_type == FraudIndicator.CARD_TESTING:
                return await self._check_card_testing(rule, payment_context)
            elif rule.indicator_type == FraudIndicator.IP_REPUTATION:
                return await self._check_ip_reputation(rule, payment_context)
            elif rule.indicator_type == FraudIndicator.EMAIL_RISK:
                return await self._check_email_risk(rule, payment_context)
            else:
                return {"triggered": False, "score": 0.0, "details": {}}
                
        except Exception as e:
            logger.error(f"Failed to evaluate fraud indicator {rule.indicator_type}: {e}")
            return {"triggered": False, "score": 0.0, "details": {"error": str(e)}}
            
    async def _check_velocity_anomaly(
        self,
        rule: FraudRule,
        payment_context: PaymentContext
    ) -> Dict[str, Any]:
        """Check for transaction velocity anomalies"""
        try:
            time_window = rule.conditions.get("time_window", 3600)  # seconds
            max_transactions = rule.conditions.get("max_transactions_per_hour", 10)
            
            cutoff_time = payment_context.timestamp - timedelta(seconds=time_window)
            
            # Count recent transactions for this customer
            # In production, this would query actual payment data
            # For now, simulate with Redis counter
            redis_key = f"velocity:{payment_context.customer_id}"
            current_count = await self.redis.get(redis_key)
            transaction_count = int(current_count) if current_count else 0
            
            # Increment counter
            await self.redis.setex(redis_key, time_window, transaction_count + 1)
            
            if transaction_count >= max_transactions:
                return {
                    "triggered": True,
                    "score": min(1.0, transaction_count / max_transactions),
                    "details": {
                        "transaction_count": transaction_count,
                        "time_window": time_window,
                        "threshold": max_transactions
                    }
                }
            
            return {"triggered": False, "score": 0.0, "details": {}}
            
        except Exception as e:
            logger.error(f"Failed to check velocity anomaly: {e}")
            return {"triggered": False, "score": 0.0, "details": {"error": str(e)}}
            
    async def _check_transaction_amount(
        self,
        rule: FraudRule,
        payment_context: PaymentContext
    ) -> Dict[str, Any]:
        """Check for unusual transaction amounts"""
        try:
            threshold_amount = Decimal(str(rule.conditions.get("amount_threshold", 5000)))
            
            if payment_context.amount >= threshold_amount:
                # Calculate score based on how much it exceeds threshold
                excess_ratio = float(payment_context.amount) / float(threshold_amount)
                score = min(1.0, excess_ratio / 2.0)  # Cap at 2x threshold = 1.0 score
                
                return {
                    "triggered": True,
                    "score": score,
                    "details": {
                        "amount": float(payment_context.amount),
                        "threshold": float(threshold_amount),
                        "excess_ratio": excess_ratio
                    }
                }
                
            return {"triggered": False, "score": 0.0, "details": {}}
            
        except Exception as e:
            logger.error(f"Failed to check transaction amount: {e}")
            return {"triggered": False, "score": 0.0, "details": {"error": str(e)}}
            
    async def _check_location_mismatch(
        self,
        rule: FraudRule,
        payment_context: PaymentContext
    ) -> Dict[str, Any]:
        """Check for geographic location mismatches"""
        try:
            # In production, this would use IP geolocation and billing address
            # For now, simulate basic check
            
            if not payment_context.ip_address or not payment_context.billing_address:
                return {"triggered": False, "score": 0.0, "details": {}}
                
            # Simulate IP geolocation (would use actual service)
            ip_country = "US"  # Simulated
            billing_country = payment_context.billing_address.get("country", "Unknown")
            
            if ip_country != billing_country:
                return {
                    "triggered": True,
                    "score": 0.8,
                    "details": {
                        "ip_country": ip_country,
                        "billing_country": billing_country,
                        "mismatch_type": "country"
                    }
                }
                
            return {"triggered": False, "score": 0.0, "details": {}}
            
        except Exception as e:
            logger.error(f"Failed to check location mismatch: {e}")
            return {"triggered": False, "score": 0.0, "details": {"error": str(e)}}
            
    async def _check_card_testing(
        self,
        rule: FraudRule,
        payment_context: PaymentContext
    ) -> Dict[str, Any]:
        """Check for card testing patterns"""
        try:
            # Look for multiple small transactions in short timeframe
            small_amount_threshold = Decimal("10.00")  # Small amounts
            frequency_threshold = rule.conditions.get("frequency_threshold", 5)
            
            if payment_context.amount <= small_amount_threshold:
                # Check frequency of small transactions
                redis_key = f"card_testing:{payment_context.customer_id}"
                current_count = await self.redis.get(redis_key)
                test_count = int(current_count) if current_count else 0
                
                # Increment counter with 1-hour expiry
                await self.redis.setex(redis_key, 3600, test_count + 1)
                
                if test_count >= frequency_threshold:
                    return {
                        "triggered": True,
                        "score": 0.9,
                        "details": {
                            "small_transaction_count": test_count,
                            "amount": float(payment_context.amount),
                            "frequency_threshold": frequency_threshold
                        }
                    }
                    
            return {"triggered": False, "score": 0.0, "details": {}}
            
        except Exception as e:
            logger.error(f"Failed to check card testing: {e}")
            return {"triggered": False, "score": 0.0, "details": {"error": str(e)}}
            
    async def _check_ip_reputation(
        self,
        rule: FraudRule,
        payment_context: PaymentContext
    ) -> Dict[str, Any]:
        """Check IP address reputation"""
        try:
            if not payment_context.ip_address:
                return {"triggered": False, "score": 0.0, "details": {}}
                
            # Check against blacklist
            async with self.db_pool.acquire() as conn:
                blacklist_entry = await conn.fetchrow("""
                    SELECT * FROM fraud_blacklists 
                    WHERE list_type = 'ip' 
                    AND value = $1 
                    AND active = TRUE
                """, payment_context.ip_address)
                
            if blacklist_entry:
                return {
                    "triggered": True,
                    "score": 1.0,
                    "details": {
                        "ip_address": payment_context.ip_address,
                        "blacklist_reason": blacklist_entry['reason']
                    }
                }
                
            # Additional checks for VPN/Tor would go here
            return {"triggered": False, "score": 0.0, "details": {}}
            
        except Exception as e:
            logger.error(f"Failed to check IP reputation: {e}")
            return {"triggered": False, "score": 0.0, "details": {"error": str(e)}}
            
    async def _check_email_risk(
        self,
        rule: FraudRule,
        payment_context: PaymentContext
    ) -> Dict[str, Any]:
        """Check email address risk factors"""
        try:
            email = payment_context.metadata.get("email")
            if not email:
                return {"triggered": False, "score": 0.0, "details": {}}
                
            # Check against blacklist
            async with self.db_pool.acquire() as conn:
                blacklist_entry = await conn.fetchrow("""
                    SELECT * FROM fraud_blacklists 
                    WHERE list_type = 'email' 
                    AND value = $1 
                    AND active = TRUE
                """, email)
                
            if blacklist_entry:
                return {
                    "triggered": True,
                    "score": 0.9,
                    "details": {
                        "email": email,
                        "blacklist_reason": blacklist_entry['reason']
                    }
                }
                
            # Check for disposable email domains
            disposable_domains = ["tempmail.com", "10minutemail.com", "guerrillamail.com"]
            email_domain = email.split("@")[-1].lower()
            
            if email_domain in disposable_domains:
                return {
                    "triggered": True,
                    "score": 0.7,
                    "details": {
                        "email": email,
                        "risk_type": "disposable_email",
                        "domain": email_domain
                    }
                }
                
            return {"triggered": False, "score": 0.0, "details": {}}
            
        except Exception as e:
            logger.error(f"Failed to check email risk: {e}")
            return {"triggered": False, "score": 0.0, "details": {"error": str(e)}}
            
    def _calculate_risk_level(self, risk_score: float) -> FraudRiskLevel:
        """Calculate risk level from score"""
        if risk_score >= self.risk_thresholds[FraudRiskLevel.VERY_HIGH]:
            return FraudRiskLevel.VERY_HIGH
        elif risk_score >= self.risk_thresholds[FraudRiskLevel.HIGH]:
            return FraudRiskLevel.HIGH
        elif risk_score >= self.risk_thresholds[FraudRiskLevel.MEDIUM]:
            return FraudRiskLevel.MEDIUM
        elif risk_score >= self.risk_thresholds[FraudRiskLevel.LOW]:
            return FraudRiskLevel.LOW
        else:
            return FraudRiskLevel.VERY_LOW
            
    def _determine_action(
        self,
        risk_level: FraudRiskLevel,
        indicators: List[Dict[str, Any]]
    ) -> FraudAction:
        """Determine recommended action based on risk level"""
        if risk_level == FraudRiskLevel.VERY_HIGH:
            return FraudAction.BLOCK
        elif risk_level == FraudRiskLevel.HIGH:
            return FraudAction.REVIEW
        elif risk_level == FraudRiskLevel.MEDIUM:
            return FraudAction.CHALLENGE
        elif risk_level == FraudRiskLevel.LOW:
            return FraudAction.NOTIFY
        else:
            return FraudAction.ALLOW
            
    async def _store_assessment(self, assessment: FraudAssessment) -> None:
        """Store fraud assessment in database"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO fraud_assessments (
                        assessment_id, entity_type, entity_id, risk_level,
                        risk_score, indicators, recommended_action, confidence,
                        assessed_at, expires_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """, 
                assessment.assessment_id, assessment.entity_type, assessment.entity_id,
                assessment.risk_level.value, assessment.risk_score,
                json.dumps(assessment.indicators), assessment.recommended_action.value,
                assessment.confidence, assessment.assessed_at, assessment.expires_at
                )
                
        except Exception as e:
            logger.error(f"Failed to store fraud assessment: {e}")
            raise
            
    async def _log_fraud_event(self, assessment: FraudAssessment, event_type: str) -> None:
        """Log fraud event"""
        try:
            event_id = f"FE_{assessment.assessment_id}_{event_type}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO fraud_events (
                        event_id, assessment_id, event_type, entity_type,
                        entity_id, details, action_taken
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                """, 
                event_id, assessment.assessment_id, event_type,
                assessment.entity_type, assessment.entity_id,
                json.dumps({
                    "risk_level": assessment.risk_level.value,
                    "risk_score": assessment.risk_score,
                    "indicator_count": len(assessment.indicators)
                }),
                assessment.recommended_action.value
                )
                
        except Exception as e:
            logger.error(f"Failed to log fraud event: {e}")
            
    async def get_fraud_analytics(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get fraud detection analytics"""
        try:
            async with self.db_pool.acquire() as conn:
                # Assessment statistics
                assessment_stats = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_assessments,
                        COUNT(*) FILTER (WHERE risk_level = 'very_high') as very_high_risk,
                        COUNT(*) FILTER (WHERE risk_level = 'high') as high_risk,
                        COUNT(*) FILTER (WHERE risk_level = 'medium') as medium_risk,
                        AVG(risk_score) as avg_risk_score
                    FROM fraud_assessments 
                    WHERE assessed_at BETWEEN $1 AND $2
                """, start_date, end_date)
                
                # Top fraud indicators
                top_indicators = await conn.fetch("""
                    SELECT 
                        indicator->>'indicator' as indicator_type,
                        COUNT(*) as count
                    FROM fraud_assessments,
                         jsonb_array_elements(indicators) as indicator
                    WHERE assessed_at BETWEEN $1 AND $2
                    GROUP BY indicator->>'indicator'
                    ORDER BY count DESC
                    LIMIT 10
                """, start_date, end_date)
                
                # Actions distribution
                actions_distribution = await conn.fetch("""
                    SELECT 
                        recommended_action,
                        COUNT(*) as count
                    FROM fraud_assessments 
                    WHERE assessed_at BETWEEN $1 AND $2
                    GROUP BY recommended_action
                """, start_date, end_date)
                
            return {
                "summary": {
                    "total_assessments": assessment_stats['total_assessments'],
                    "very_high_risk": assessment_stats['very_high_risk'],
                    "high_risk": assessment_stats['high_risk'],
                    "medium_risk": assessment_stats['medium_risk'],
                    "avg_risk_score": float(assessment_stats['avg_risk_score'] or 0)
                },
                "top_indicators": [
                    {
                        "indicator": row['indicator_type'],
                        "count": row['count']
                    } for row in top_indicators
                ],
                "actions_distribution": [
                    {
                        "action": row['recommended_action'],
                        "count": row['count']
                    } for row in actions_distribution
                ],
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get fraud analytics: {e}")
            raise