"""Payment Flow Analytics Module

Enterprise-grade payment flow analytics and transaction intelligence.
Advanced payment processing analytics, fraud detection, and revenue
optimization for payment systems and financial transactions.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel - All rights reserved
⚠️  WARNING: This code and concept are proprietary to Fahed Mlaiel.
    Any unauthorized use, copying, or distribution without explicit written 
    permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.

Team Expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
                Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class PaymentStatus(Enum):
    """Payment status types"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DECLINED = "declined"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
    DISPUTED = "disputed"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"


class PaymentMethod(Enum):
    """Payment method types"""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    DIGITAL_WALLET = "digital_wallet"
    CRYPTOCURRENCY = "cryptocurrency"
    PAYPAL = "paypal"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"
    STRIPE = "stripe"
    WIRE_TRANSFER = "wire_transfer"


class FraudRiskLevel(Enum):
    """Fraud risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    BLOCKED = "blocked"


class PaymentGateway(Enum):
    """Payment gateway providers"""
    STRIPE = "stripe"
    PAYPAL = "paypal"
    SQUARE = "square"
    BRAINTREE = "braintree"
    ADYEN = "adyen"
    WORLDPAY = "worldpay"
    AUTHORIZE_NET = "authorize_net"
    RAZORPAY = "razorpay"


class TransactionType(Enum):
    """Transaction types"""
    PAYMENT = "payment"
    REFUND = "refund"
    CHARGEBACK = "chargeback"
    FEE = "fee"
    ADJUSTMENT = "adjustment"
    PAYOUT = "payout"
    TRANSFER = "transfer"


@dataclass
class PaymentEvent:
    """Payment flow event"""
    event_id: str
    transaction_id: str
    user_id: str
    payment_method: PaymentMethod
    payment_gateway: PaymentGateway
    amount: float
    currency: str
    status: PaymentStatus
    transaction_type: TransactionType
    processing_time_ms: int
    gateway_fee: float
    net_amount: float
    country_code: str
    ip_address: str
    device_info: Dict[str, Any]
    risk_score: float
    fraud_flags: List[str]
    metadata: Dict[str, Any]
    timestamp: datetime
    completed_at: Optional[datetime] = None


@dataclass
class PaymentFlowMetrics:
    """Payment flow analytics metrics"""
    total_transactions: int
    successful_transactions: int
    failed_transactions: int
    success_rate: float
    failure_rate: float
    average_transaction_amount: float
    total_volume: float
    total_fees: float
    net_revenue: float
    average_processing_time_ms: float
    fraud_detection_rate: float
    chargeback_rate: float
    refund_rate: float
    conversion_rate: float
    abandonment_rate: float


@dataclass
class FraudAnalysis:
    """Fraud detection analysis"""
    transaction_id: str
    risk_level: FraudRiskLevel
    risk_score: float
    risk_factors: List[str]
    fraud_indicators: Dict[str, Any]
    recommended_action: str
    confidence_score: float
    analysis_timestamp: datetime
    prevention_rules_triggered: List[str]
    manual_review_required: bool


@dataclass
class PaymentFlowInsight:
    """Payment flow insight"""
    insight_id: str
    insight_type: str
    title: str
    description: str
    impact_level: str
    affected_transactions: int
    revenue_impact: float
    recommendations: List[str]
    priority: str
    generated_at: datetime


class PaymentAnalyticsEngine:
    """Core payment analytics processing engine"""
    
    def __init__(self):
        self.payment_data: Dict[str, PaymentEvent] = {}
        self.fraud_models: Dict[str, Any] = {}
        self.gateway_performance: Dict[str, Dict[str, Any]] = {}
        self.conversion_funnels: Dict[str, List[Dict[str, Any]]] = {}
        
    async def track_payment_event(self, event: PaymentEvent) -> Dict[str, Any]:
        """Track payment event and update analytics"""
        try:
            # Store payment event
            self.payment_data[event.transaction_id] = event
            
            # Update gateway performance metrics
            await self._update_gateway_performance(event)
            
            # Perform fraud analysis
            fraud_analysis = await self._perform_fraud_analysis(event)
            
            # Update conversion funnel
            await self._update_conversion_funnel(event)
            
            # Calculate real-time metrics
            real_time_metrics = await self._calculate_real_time_metrics(event)
            
            # Detect anomalies
            anomalies = await self._detect_payment_anomalies(event)
            
            return {
                "event_id": event.event_id,
                "transaction_id": event.transaction_id,
                "processed_at": datetime.utcnow().isoformat(),
                "fraud_analysis": asdict(fraud_analysis),
                "real_time_metrics": real_time_metrics,
                "anomalies": anomalies,
                "status": "processed"
            }
            
        except Exception as e:
            logger.error(f"Error tracking payment event: {str(e)}")
            raise
    
    async def calculate_payment_metrics(self, 
                                       period_start: datetime,
                                       period_end: datetime) -> PaymentFlowMetrics:
        """Calculate comprehensive payment flow metrics"""
        try:
            # Filter events by period
            period_events = [
                event for event in self.payment_data.values()
                if period_start <= event.timestamp <= period_end
            ]
            
            if not period_events:
                return PaymentFlowMetrics(
                    total_transactions=0, successful_transactions=0, failed_transactions=0,
                    success_rate=0.0, failure_rate=0.0, average_transaction_amount=0.0,
                    total_volume=0.0, total_fees=0.0, net_revenue=0.0,
                    average_processing_time_ms=0.0, fraud_detection_rate=0.0,
                    chargeback_rate=0.0, refund_rate=0.0, conversion_rate=0.0,
                    abandonment_rate=0.0
                )
            
            # Calculate basic metrics
            total_transactions = len(period_events)
            successful_transactions = len([e for e in period_events if e.status == PaymentStatus.COMPLETED])
            failed_transactions = total_transactions - successful_transactions
            
            # Calculate rates
            success_rate = successful_transactions / total_transactions if total_transactions > 0 else 0
            failure_rate = 1 - success_rate
            
            # Calculate amounts
            successful_events = [e for e in period_events if e.status == PaymentStatus.COMPLETED]
            total_volume = sum(e.amount for e in successful_events)
            total_fees = sum(e.gateway_fee for e in successful_events)
            net_revenue = sum(e.net_amount for e in successful_events)
            average_transaction_amount = total_volume / len(successful_events) if successful_events else 0
            
            # Calculate processing time
            processing_times = [e.processing_time_ms for e in period_events if e.processing_time_ms > 0]
            average_processing_time_ms = sum(processing_times) / len(processing_times) if processing_times else 0
            
            # Calculate fraud and risk metrics
            fraud_detected = len([e for e in period_events if e.risk_score > 0.7])
            fraud_detection_rate = fraud_detected / total_transactions if total_transactions > 0 else 0
            
            # Calculate chargeback and refund rates
            chargebacks = len([e for e in period_events if e.transaction_type == TransactionType.CHARGEBACK])
            refunds = len([e for e in period_events if e.status == PaymentStatus.REFUNDED])
            chargeback_rate = chargebacks / successful_transactions if successful_transactions > 0 else 0
            refund_rate = refunds / successful_transactions if successful_transactions > 0 else 0
            
            # Calculate conversion metrics (simplified)
            conversion_rate = await self._calculate_conversion_rate(period_start, period_end)
            abandonment_rate = 1 - conversion_rate
            
            return PaymentFlowMetrics(
                total_transactions=total_transactions,
                successful_transactions=successful_transactions,
                failed_transactions=failed_transactions,
                success_rate=success_rate,
                failure_rate=failure_rate,
                average_transaction_amount=average_transaction_amount,
                total_volume=total_volume,
                total_fees=total_fees,
                net_revenue=net_revenue,
                average_processing_time_ms=average_processing_time_ms,
                fraud_detection_rate=fraud_detection_rate,
                chargeback_rate=chargeback_rate,
                refund_rate=refund_rate,
                conversion_rate=conversion_rate,
                abandonment_rate=abandonment_rate
            )
            
        except Exception as e:
            logger.error(f"Error calculating payment metrics: {str(e)}")
            raise
    
    async def analyze_gateway_performance(self, gateway: PaymentGateway,
                                         period_start: datetime,
                                         period_end: datetime) -> Dict[str, Any]:
        """Analyze payment gateway performance"""
        try:
            # Filter events by gateway and period
            gateway_events = [
                event for event in self.payment_data.values()
                if (event.payment_gateway == gateway and 
                    period_start <= event.timestamp <= period_end)
            ]
            
            if not gateway_events:
                return {"error": f"No data found for gateway {gateway.value}"}
            
            # Calculate gateway-specific metrics
            total_transactions = len(gateway_events)
            successful_transactions = len([e for e in gateway_events if e.status == PaymentStatus.COMPLETED])
            success_rate = successful_transactions / total_transactions if total_transactions > 0 else 0
            
            # Calculate processing time statistics
            processing_times = [e.processing_time_ms for e in gateway_events if e.processing_time_ms > 0]
            avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
            
            # Calculate fee analysis
            total_fees = sum(e.gateway_fee for e in gateway_events if e.status == PaymentStatus.COMPLETED)
            avg_fee_rate = total_fees / sum(e.amount for e in gateway_events if e.status == PaymentStatus.COMPLETED) if successful_transactions > 0 else 0
            
            # Fraud analysis
            fraud_events = [e for e in gateway_events if e.risk_score > 0.7]
            fraud_rate = len(fraud_events) / total_transactions if total_transactions > 0 else 0
            
            # Performance comparison
            benchmarks = await self._get_gateway_benchmarks(gateway)
            
            return {
                "gateway": gateway.value,
                "period": f"{period_start.date()} to {period_end.date()}",
                "metrics": {
                    "total_transactions": total_transactions,
                    "success_rate": success_rate,
                    "average_processing_time_ms": avg_processing_time,
                    "total_fees": total_fees,
                    "average_fee_rate": avg_fee_rate,
                    "fraud_rate": fraud_rate
                },
                "benchmarks": benchmarks,
                "recommendations": await self._generate_gateway_recommendations(gateway, gateway_events),
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing gateway performance: {str(e)}")
            raise
    
    async def detect_payment_fraud(self, transaction_id: str) -> FraudAnalysis:
        """Detect fraud for specific transaction"""
        try:
            if transaction_id not in self.payment_data:
                raise ValueError(f"Transaction not found: {transaction_id}")
            
            event = self.payment_data[transaction_id]
            
            # Analyze fraud indicators
            fraud_indicators = await self._analyze_fraud_indicators(event)
            
            # Calculate risk score
            risk_score = await self._calculate_fraud_risk_score(fraud_indicators, event)
            
            # Determine risk level
            risk_level = await self._determine_fraud_risk_level(risk_score)
            
            # Identify risk factors
            risk_factors = await self._identify_fraud_risk_factors(fraud_indicators, event)
            
            # Determine recommended action
            recommended_action = await self._determine_fraud_action(risk_level, risk_factors)
            
            # Check prevention rules
            prevention_rules = await self._check_fraud_prevention_rules(event, fraud_indicators)
            
            return FraudAnalysis(
                transaction_id=transaction_id,
                risk_level=risk_level,
                risk_score=risk_score,
                risk_factors=risk_factors,
                fraud_indicators=fraud_indicators,
                recommended_action=recommended_action,
                confidence_score=0.88,  # Simplified confidence
                analysis_timestamp=datetime.utcnow(),
                prevention_rules_triggered=prevention_rules,
                manual_review_required=risk_level in [FraudRiskLevel.HIGH, FraudRiskLevel.CRITICAL]
            )
            
        except Exception as e:
            logger.error(f"Error detecting payment fraud: {str(e)}")
            raise
    
    async def generate_payment_insights(self, period_start: datetime,
                                       period_end: datetime) -> List[PaymentFlowInsight]:
        """Generate payment flow insights"""
        try:
            insights = []
            
            # Get period metrics
            metrics = await self.calculate_payment_metrics(period_start, period_end)
            
            # Success rate insight
            if metrics.success_rate < 0.85:
                insights.append(PaymentFlowInsight(
                    insight_id=str(uuid.uuid4()),
                    insight_type="performance",
                    title="Low Payment Success Rate",
                    description=f"Payment success rate of {metrics.success_rate:.1%} is below optimal threshold",
                    impact_level="high",
                    affected_transactions=metrics.failed_transactions,
                    revenue_impact=metrics.failed_transactions * metrics.average_transaction_amount,
                    recommendations=[
                        "Analyze failed payment reasons",
                        "Optimize payment gateway selection",
                        "Implement retry logic for declined payments"
                    ],
                    priority="high",
                    generated_at=datetime.utcnow()
                ))
            
            # High fees insight
            fee_rate = metrics.total_fees / metrics.total_volume if metrics.total_volume > 0 else 0
            if fee_rate > 0.03:  # 3% threshold
                insights.append(PaymentFlowInsight(
                    insight_id=str(uuid.uuid4()),
                    insight_type="cost_optimization",
                    title="High Payment Processing Fees",
                    description=f"Payment fees at {fee_rate:.1%} are above industry average",
                    impact_level="medium",
                    affected_transactions=metrics.successful_transactions,
                    revenue_impact=metrics.total_fees,
                    recommendations=[
                        "Negotiate better rates with current gateways",
                        "Consider alternative payment providers",
                        "Implement gateway routing optimization"
                    ],
                    priority="medium",
                    generated_at=datetime.utcnow()
                ))
            
            # Fraud detection insight
            if metrics.fraud_detection_rate > 0.05:  # 5% threshold
                insights.append(PaymentFlowInsight(
                    insight_id=str(uuid.uuid4()),
                    insight_type="security",
                    title="High Fraud Detection Rate",
                    description=f"Fraud detection rate of {metrics.fraud_detection_rate:.1%} indicates security concerns",
                    impact_level="high",
                    affected_transactions=int(metrics.total_transactions * metrics.fraud_detection_rate),
                    revenue_impact=0,  # Prevented losses
                    recommendations=[
                        "Review and enhance fraud detection rules",
                        "Implement additional verification steps",
                        "Analyze fraud patterns for prevention"
                    ],
                    priority="high",
                    generated_at=datetime.utcnow()
                ))
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating payment insights: {str(e)}")
            raise
    
    # Private helper methods
    
    async def _update_gateway_performance(self, event: PaymentEvent) -> None:
        """Update gateway performance tracking"""
        gateway = event.payment_gateway.value
        
        if gateway not in self.gateway_performance:
            self.gateway_performance[gateway] = {
                "total_transactions": 0,
                "successful_transactions": 0,
                "total_processing_time": 0,
                "total_fees": 0
            }
        
        perf = self.gateway_performance[gateway]
        perf["total_transactions"] += 1
        
        if event.status == PaymentStatus.COMPLETED:
            perf["successful_transactions"] += 1
            perf["total_fees"] += event.gateway_fee
        
        perf["total_processing_time"] += event.processing_time_ms
    
    async def _perform_fraud_analysis(self, event: PaymentEvent) -> FraudAnalysis:
        """Perform fraud analysis on payment event"""
        return await self.detect_payment_fraud(event.transaction_id)
    
    async def _update_conversion_funnel(self, event: PaymentEvent) -> None:
        """Update conversion funnel tracking"""
        user_id = event.user_id
        
        if user_id not in self.conversion_funnels:
            self.conversion_funnels[user_id] = []
        
        self.conversion_funnels[user_id].append({
            "step": "payment_attempt",
            "timestamp": event.timestamp,
            "status": event.status.value,
            "amount": event.amount
        })
    
    async def _calculate_real_time_metrics(self, event: PaymentEvent) -> Dict[str, Any]:
        """Calculate real-time metrics for event"""
        # Get recent events (last hour)
        recent_events = [
            e for e in self.payment_data.values()
            if (datetime.utcnow() - e.timestamp).total_seconds() <= 3600
        ]
        
        if not recent_events:
            return {"transactions_per_hour": 0, "success_rate": 0.0}
        
        successful = len([e for e in recent_events if e.status == PaymentStatus.COMPLETED])
        success_rate = successful / len(recent_events)
        
        return {
            "transactions_per_hour": len(recent_events),
            "success_rate": success_rate,
            "average_amount": sum(e.amount for e in recent_events) / len(recent_events)
        }
    
    async def _detect_payment_anomalies(self, event: PaymentEvent) -> List[str]:
        """Detect payment anomalies"""
        anomalies = []
        
        # High amount anomaly
        if event.amount > 10000:  # $10,000 threshold
            anomalies.append("High transaction amount detected")
        
        # Unusual country
        if event.country_code not in ["US", "CA", "GB", "DE", "FR"]:
            anomalies.append("Transaction from unusual country")
        
        # High processing time
        if event.processing_time_ms > 5000:  # 5 seconds
            anomalies.append("Unusually high processing time")
        
        return anomalies
    
    async def _calculate_conversion_rate(self, start: datetime, end: datetime) -> float:
        """Calculate conversion rate for period"""
        # Simplified conversion rate calculation
        return 0.78  # 78% conversion rate
    
    async def _get_gateway_benchmarks(self, gateway: PaymentGateway) -> Dict[str, Any]:
        """Get industry benchmarks for gateway"""
        # Simplified benchmarks - in production would use real industry data
        benchmarks = {
            PaymentGateway.STRIPE: {"success_rate": 0.92, "avg_processing_time": 800, "fee_rate": 0.029},
            PaymentGateway.PAYPAL: {"success_rate": 0.89, "avg_processing_time": 1200, "fee_rate": 0.034},
            PaymentGateway.SQUARE: {"success_rate": 0.91, "avg_processing_time": 900, "fee_rate": 0.027}
        }
        
        return benchmarks.get(gateway, {"success_rate": 0.90, "avg_processing_time": 1000, "fee_rate": 0.030})
    
    async def _generate_gateway_recommendations(self, gateway: PaymentGateway,
                                              events: List[PaymentEvent]) -> List[str]:
        """Generate recommendations for gateway optimization"""
        recommendations = []
        
        success_rate = len([e for e in events if e.status == PaymentStatus.COMPLETED]) / len(events) if events else 0
        
        if success_rate < 0.90:
            recommendations.append("Improve payment success rate through better error handling")
        
        avg_processing_time = sum(e.processing_time_ms for e in events) / len(events) if events else 0
        if avg_processing_time > 2000:
            recommendations.append("Optimize payment processing time")
        
        return recommendations
    
    async def _analyze_fraud_indicators(self, event: PaymentEvent) -> Dict[str, Any]:
        """Analyze fraud indicators for transaction"""
        indicators = {
            "velocity_check": await self._check_velocity_fraud(event),
            "geolocation_risk": await self._check_geolocation_risk(event),
            "device_fingerprint": await self._check_device_fingerprint(event),
            "payment_pattern": await self._check_payment_pattern(event),
            "amount_analysis": await self._check_amount_anomaly(event)
        }
        
        return indicators
    
    async def _calculate_fraud_risk_score(self, indicators: Dict[str, Any], 
                                         event: PaymentEvent) -> float:
        """Calculate fraud risk score"""
        base_score = 0.1  # 10% base risk
        
        # Add risk based on indicators
        if indicators["velocity_check"]["high_velocity"]:
            base_score += 0.3
        
        if indicators["geolocation_risk"]["suspicious_location"]:
            base_score += 0.2
        
        if indicators["amount_analysis"]["unusual_amount"]:
            base_score += 0.15
        
        # Cap at 95%
        return min(base_score, 0.95)
    
    async def _determine_fraud_risk_level(self, risk_score: float) -> FraudRiskLevel:
        """Determine fraud risk level from score"""
        if risk_score >= 0.8:
            return FraudRiskLevel.CRITICAL
        elif risk_score >= 0.6:
            return FraudRiskLevel.HIGH
        elif risk_score >= 0.4:
            return FraudRiskLevel.MEDIUM
        else:
            return FraudRiskLevel.LOW
    
    async def _identify_fraud_risk_factors(self, indicators: Dict[str, Any],
                                          event: PaymentEvent) -> List[str]:
        """Identify specific fraud risk factors"""
        factors = []
        
        if indicators["velocity_check"]["high_velocity"]:
            factors.append("High transaction velocity detected")
        
        if indicators["geolocation_risk"]["suspicious_location"]:
            factors.append("Transaction from suspicious location")
        
        if indicators["amount_analysis"]["unusual_amount"]:
            factors.append("Unusual transaction amount")
        
        return factors
    
    async def _determine_fraud_action(self, risk_level: FraudRiskLevel, 
                                     risk_factors: List[str]) -> str:
        """Determine recommended action for fraud detection"""
        if risk_level == FraudRiskLevel.CRITICAL:
            return "Block transaction immediately"
        elif risk_level == FraudRiskLevel.HIGH:
            return "Require additional verification"
        elif risk_level == FraudRiskLevel.MEDIUM:
            return "Flag for manual review"
        else:
            return "Allow with monitoring"
    
    async def _check_fraud_prevention_rules(self, event: PaymentEvent,
                                           indicators: Dict[str, Any]) -> List[str]:
        """Check which fraud prevention rules were triggered"""
        triggered_rules = []
        
        if event.amount > 5000:
            triggered_rules.append("High amount rule")
        
        if indicators["velocity_check"]["high_velocity"]:
            triggered_rules.append("Velocity rule")
        
        return triggered_rules
    
    # Simplified fraud check methods
    
    async def _check_velocity_fraud(self, event: PaymentEvent) -> Dict[str, Any]:
        """Check for velocity-based fraud"""
        # Simplified velocity check
        return {"high_velocity": False, "transactions_per_hour": 2}
    
    async def _check_geolocation_risk(self, event: PaymentEvent) -> Dict[str, Any]:
        """Check geolocation risk"""
        suspicious_countries = ["XX", "YY", "ZZ"]  # Example suspicious countries
        return {
            "suspicious_location": event.country_code in suspicious_countries,
            "risk_score": 0.2 if event.country_code in suspicious_countries else 0.1
        }
    
    async def _check_device_fingerprint(self, event: PaymentEvent) -> Dict[str, Any]:
        """Check device fingerprint"""
        return {"known_device": True, "device_risk_score": 0.1}
    
    async def _check_payment_pattern(self, event: PaymentEvent) -> Dict[str, Any]:
        """Check payment pattern anomalies"""
        return {"unusual_pattern": False, "pattern_score": 0.1}
    
    async def _check_amount_anomaly(self, event: PaymentEvent) -> Dict[str, Any]:
        """Check for amount anomalies"""
        return {
            "unusual_amount": event.amount > 1000,
            "amount_percentile": 0.85 if event.amount > 1000 else 0.5
        }


class PaymentAnalyticsEventHandler:
    """Main event handler for payment analytics"""
    
    def __init__(self):
        self.analytics_engine = PaymentAnalyticsEngine()
        
    async def handle_payment_event(self, event: PaymentEvent) -> Dict[str, Any]:
        """Handle payment analytics event"""
        return await self.analytics_engine.track_payment_event(event)
    
    async def handle_metrics_request(self, period_start: datetime,
                                    period_end: datetime) -> PaymentFlowMetrics:
        """Handle payment metrics request"""
        return await self.analytics_engine.calculate_payment_metrics(period_start, period_end)
    
    async def handle_gateway_analysis_request(self, gateway: PaymentGateway,
                                             period_start: datetime,
                                             period_end: datetime) -> Dict[str, Any]:
        """Handle gateway analysis request"""
        return await self.analytics_engine.analyze_gateway_performance(gateway, period_start, period_end)
    
    async def handle_fraud_detection_request(self, transaction_id: str) -> FraudAnalysis:
        """Handle fraud detection request"""
        return await self.analytics_engine.detect_payment_fraud(transaction_id)
    
    async def handle_insights_request(self, period_start: datetime,
                                     period_end: datetime) -> List[PaymentFlowInsight]:
        """Handle payment insights request"""
        return await self.analytics_engine.generate_payment_insights(period_start, period_end)


# Global analytics engine instance
global_payment_analytics = PaymentAnalyticsEngine()


# Helper functions for easy integration
async def track_payment_event(event: PaymentEvent) -> Dict[str, Any]:
    """Track payment event"""
    return await global_payment_analytics.track_payment_event(event)


async def get_payment_metrics(period_start: datetime, period_end: datetime) -> PaymentFlowMetrics:
    """Get payment flow metrics"""
    return await global_payment_analytics.calculate_payment_metrics(period_start, period_end)


async def analyze_gateway_performance(gateway: PaymentGateway,
                                     period_start: datetime,
                                     period_end: datetime) -> Dict[str, Any]:
    """Analyze payment gateway performance"""
    return await global_payment_analytics.analyze_gateway_performance(gateway, period_start, period_end)


async def detect_payment_fraud(transaction_id: str) -> FraudAnalysis:
    """Detect payment fraud"""
    return await global_payment_analytics.detect_payment_fraud(transaction_id)


async def get_payment_insights(period_start: datetime, period_end: datetime) -> List[PaymentFlowInsight]:
    """Get payment flow insights"""
    return await global_payment_analytics.generate_payment_insights(period_start, period_end)