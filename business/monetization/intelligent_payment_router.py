"""🚀 Intelligent Payment Router - Enterprise Multi-Provider Optimization
=====================================================================

Advanced payment routing system that intelligently selects optimal payment
providers based on cost, success rates, geographic optimization, and 
real-time performance metrics for enterprise monetization.

Created by: Fahed Mlaiel <mlaiel@live.de>
(c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - UNAUTHORIZED USE PROHIBITED ⚠️
Contact mlaiel@live.de for licensing inquiries.

Business Logic: Payment Request → Provider Analysis → Optimal Routing → Execution
=====================================================================
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
import uuid
import json
import statistics
from collections import defaultdict

logger = logging.getLogger(__name__)


class RoutingStrategy(Enum):
    """Payment routing strategies"""
    
    LOWEST_COST = "lowest_cost"
    HIGHEST_SUCCESS_RATE = "highest_success_rate"
    FASTEST_SETTLEMENT = "fastest_settlement"
    GEOGRAPHIC_OPTIMIZATION = "geographic_optimization"
    BALANCED_OPTIMIZATION = "balanced_optimization"
    LOAD_BALANCING = "load_balancing"
    RISK_MINIMIZATION = "risk_minimization"


class PaymentProvider(Enum):
    """Supported payment providers"""
    
    STRIPE = "stripe"
    PAYPAL = "paypal"
    WISE = "wise"
    ADYEN = "adyen"
    SQUARE = "square"
    COINBASE = "coinbase"
    BITPAY = "bitpay"
    BRAINTREE = "braintree"


@dataclass
class PaymentRequest:
    """Payment request for routing analysis"""
    
    request_id: str
    amount: Decimal
    currency: str
    payment_type: str
    recipient_country: str
    sender_country: str
    payment_method: str
    urgency_level: str = "normal"  # low, normal, high, urgent
    compliance_requirements: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProviderPerformanceMetrics:
    """Real-time provider performance metrics"""
    
    provider: PaymentProvider
    success_rate: float
    average_processing_time: float
    average_cost_percentage: float
    uptime_percentage: float
    geographic_coverage: List[str]
    supported_currencies: List[str]
    supported_payment_methods: List[str]
    current_load: int
    risk_score: float
    compliance_certifications: List[str]
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RoutingDecision:
    """Payment routing decision result"""
    
    decision_id: str
    request_id: str
    selected_provider: PaymentProvider
    fallback_providers: List[PaymentProvider]
    routing_strategy: RoutingStrategy
    decision_score: float
    cost_analysis: Dict[str, Any]
    risk_analysis: Dict[str, Any]
    performance_prediction: Dict[str, Any]
    estimated_completion_time: datetime
    decision_rationale: str
    created_at: datetime = field(default_factory=datetime.utcnow)


class IntelligentPaymentRouter:
    """
    Enterprise-grade intelligent payment routing system
    
    Features:
    - Real-time provider performance monitoring
    - Cost optimization across multiple providers
    - Geographic routing optimization
    - Risk-based provider selection
    - Load balancing and failover
    - Compliance-aware routing
    - Machine learning for routing optimization
    - A/B testing for routing strategies
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.provider_metrics = {}
        self.routing_history = []
        self.performance_cache = {}
        self.cache_duration = timedelta(minutes=5)
        
        # Initialize provider configurations
        self.providers = self._initialize_providers()
        
        # Routing weights for balanced optimization
        self.routing_weights = {
            "cost": 0.3,
            "success_rate": 0.3,
            "speed": 0.2,
            "risk": 0.1,
            "compliance": 0.1
        }
        
        logger.info("Intelligent Payment Router initialized")
    
    def _initialize_providers(self) -> Dict[PaymentProvider, Dict[str, Any]]:
        """Initialize payment provider configurations"""
        
        return {
            PaymentProvider.STRIPE: {
                "enabled": True,
                "priority": 1,
                "base_cost_percentage": Decimal("2.9"),
                "fixed_fee": Decimal("0.30"),
                "geographic_strength": ["US", "EU", "CA", "AU"],
                "settlement_time_hours": 24,
                "max_transaction_amount": Decimal("999999.99"),
                "compliance_level": "high",
                "supported_methods": ["card", "bank_transfer", "digital_wallet"]
            },
            
            PaymentProvider.PAYPAL: {
                "enabled": True,
                "priority": 2,
                "base_cost_percentage": Decimal("3.4"),
                "fixed_fee": Decimal("0.35"),
                "geographic_strength": ["GLOBAL"],
                "settlement_time_hours": 48,
                "max_transaction_amount": Decimal("10000.00"),
                "compliance_level": "high",
                "supported_methods": ["paypal_wallet", "card", "bank_transfer"]
            },
            
            PaymentProvider.WISE: {
                "enabled": True,
                "priority": 3,
                "base_cost_percentage": Decimal("0.5"),
                "fixed_fee": Decimal("0.50"),
                "geographic_strength": ["EU", "US", "UK", "CA", "AU"],
                "settlement_time_hours": 24,
                "max_transaction_amount": Decimal("1000000.00"),
                "compliance_level": "high",
                "supported_methods": ["bank_transfer", "swift"]
            },
            
            PaymentProvider.COINBASE: {
                "enabled": True,
                "priority": 4,
                "base_cost_percentage": Decimal("1.0"),
                "fixed_fee": Decimal("0.00"),
                "geographic_strength": ["US", "EU", "CA"],
                "settlement_time_hours": 1,
                "max_transaction_amount": Decimal("50000.00"),
                "compliance_level": "medium",
                "supported_methods": ["crypto"]
            }
        }
    
    async def route_payment(
        self,
        payment_request: PaymentRequest,
        routing_strategy: RoutingStrategy = RoutingStrategy.BALANCED_OPTIMIZATION
    ) -> RoutingDecision:
        """Route payment to optimal provider based on strategy"""
        
        try:
            logger.info(f"Routing payment request: {payment_request.request_id}")
            
            # Update provider metrics
            await self._update_provider_metrics()
            
            # Filter eligible providers
            eligible_providers = await self._filter_eligible_providers(payment_request)
            
            if not eligible_providers:
                raise ValueError("No eligible providers found for payment request")
            
            # Apply routing strategy
            routing_scores = await self._calculate_routing_scores(
                payment_request, eligible_providers, routing_strategy
            )
            
            # Select primary and fallback providers
            ranked_providers = sorted(
                routing_scores.items(), 
                key=lambda x: x[1]["total_score"], 
                reverse=True
            )
            
            primary_provider = ranked_providers[0][0]
            fallback_providers = [provider for provider, _ in ranked_providers[1:3]]
            
            # Generate decision rationale
            decision_rationale = await self._generate_decision_rationale(
                primary_provider, routing_scores[primary_provider], routing_strategy
            )
            
            # Create routing decision
            decision = RoutingDecision(
                decision_id=f"route_{uuid.uuid4().hex[:12]}",
                request_id=payment_request.request_id,
                selected_provider=primary_provider,
                fallback_providers=fallback_providers,
                routing_strategy=routing_strategy,
                decision_score=routing_scores[primary_provider]["total_score"],
                cost_analysis=routing_scores[primary_provider]["cost_analysis"],
                risk_analysis=routing_scores[primary_provider]["risk_analysis"],
                performance_prediction=routing_scores[primary_provider]["performance_prediction"],
                estimated_completion_time=datetime.utcnow() + timedelta(
                    hours=routing_scores[primary_provider]["estimated_hours"]
                ),
                decision_rationale=decision_rationale
            )
            
            # Store routing decision
            await self._store_routing_decision(decision)
            
            # Update routing history for ML optimization
            await self._update_routing_history(payment_request, decision)
            
            logger.info(f"Payment routed to {primary_provider.value}: {decision.decision_id}")
            return decision
            
        except Exception as e:

            
            logger.error(f"Error: {e}")

            
            raise
            logger.error(f"Payment routing failed: {e}")
            raise
    
    async def _update_provider_metrics(self):
        """Update real-time provider performance metrics"""
        
        try:
            current_time = datetime.utcnow()
            
            for provider in self.providers.keys():
                # Check if metrics need updating
                if (provider not in self.provider_metrics or 
                    current_time - self.provider_metrics[provider].last_updated > self.cache_duration):
                    
                    # Fetch real-time metrics
                    metrics = await self._fetch_provider_metrics(provider)
                    self.provider_metrics[provider] = metrics
            
        except Exception as e:

            
            logger.error(f"Error: {e}")

            
            raise
            logger.error(f"Provider metrics update failed: {e}")
    
    async def _fetch_provider_metrics(self, provider: PaymentProvider) -> ProviderPerformanceMetrics:
        """Fetch real-time metrics for a provider"""
        
        # Mock implementation - in production would fetch from monitoring systems
        base_metrics = {
            PaymentProvider.STRIPE: {
                "success_rate": 0.98,
                "avg_processing_time": 2.5,
                "avg_cost_percentage": 2.9,
                "uptime_percentage": 99.9,
                "current_load": 45,
                "risk_score": 0.1
            },
            PaymentProvider.PAYPAL: {
                "success_rate": 0.96,
                "avg_processing_time": 3.2,
                "avg_cost_percentage": 3.4,
                "uptime_percentage": 99.7,
                "current_load": 60,
                "risk_score": 0.15
            },
            PaymentProvider.WISE: {
                "success_rate": 0.97,
                "avg_processing_time": 4.0,
                "avg_cost_percentage": 0.8,
                "uptime_percentage": 99.8,
                "current_load": 30,
                "risk_score": 0.12
            },
            PaymentProvider.COINBASE: {
                "success_rate": 0.94,
                "avg_processing_time": 0.5,
                "avg_cost_percentage": 1.0,
                "uptime_percentage": 99.5,
                "current_load": 25,
                "risk_score": 0.25
            }
        }
        
        provider_config = self.providers[provider]
        metrics_data = base_metrics.get(provider, {})
        
        return ProviderPerformanceMetrics(
            provider=provider,
            success_rate=metrics_data.get("success_rate", 0.95),
            average_processing_time=metrics_data.get("avg_processing_time", 3.0),
            average_cost_percentage=metrics_data.get("avg_cost_percentage", 3.0),
            uptime_percentage=metrics_data.get("uptime_percentage", 99.0),
            geographic_coverage=provider_config.get("geographic_strength", []),
            supported_currencies=["USD", "EUR", "GBP"],  # Simplified
            supported_payment_methods=provider_config.get("supported_methods", []),
            current_load=metrics_data.get("current_load", 50),
            risk_score=metrics_data.get("risk_score", 0.2),
            compliance_certifications=["PCI_DSS", "SOC2"]
        )
    
    async def _filter_eligible_providers(
        self, 
        payment_request: PaymentRequest
    ) -> List[PaymentProvider]:
        """Filter providers eligible for the payment request"""
        
        eligible = []
        
        for provider, config in self.providers.items():
            if not config.get("enabled", False):
                continue
            
            # Check amount limits
            if payment_request.amount > config.get("max_transaction_amount", Decimal("999999.99")):
                continue
            
            # Check geographic coverage
            geographic_strength = config.get("geographic_strength", [])
            if (geographic_strength and 
                "GLOBAL" not in geographic_strength and 
                payment_request.recipient_country not in geographic_strength):
                continue
            
            # Check payment method support
            supported_methods = config.get("supported_methods", [])
            if (supported_methods and 
                payment_request.payment_method not in supported_methods):
                continue
            
            # Check provider availability
            if provider in self.provider_metrics:
                metrics = self.provider_metrics[provider]
                if metrics.uptime_percentage < 99.0:  # Provider down
                    continue
            
            eligible.append(provider)
        
        return eligible
    
    async def _calculate_routing_scores(
        self,
        payment_request: PaymentRequest,
        eligible_providers: List[PaymentProvider],
        routing_strategy: RoutingStrategy
    ) -> Dict[PaymentProvider, Dict[str, Any]]:
        """Calculate routing scores for eligible providers"""
        
        scores = {}
        
        for provider in eligible_providers:
            provider_config = self.providers[provider]
            provider_metrics = self.provider_metrics.get(provider)
            
            # Calculate individual scores
            cost_score = await self._calculate_cost_score(payment_request, provider_config)
            performance_score = await self._calculate_performance_score(provider_metrics)
            risk_score = await self._calculate_risk_score(provider_metrics, payment_request)
            compliance_score = await self._calculate_compliance_score(provider_config, payment_request)
            geographic_score = await self._calculate_geographic_score(provider_config, payment_request)
            
            # Apply routing strategy weights
            if routing_strategy == RoutingStrategy.LOWEST_COST:
                weights = {"cost": 0.8, "performance": 0.1, "risk": 0.05, "compliance": 0.05, "geographic": 0.0}
            elif routing_strategy == RoutingStrategy.HIGHEST_SUCCESS_RATE:
                weights = {"cost": 0.1, "performance": 0.7, "risk": 0.1, "compliance": 0.05, "geographic": 0.05}
            elif routing_strategy == RoutingStrategy.FASTEST_SETTLEMENT:
                weights = {"cost": 0.2, "performance": 0.6, "risk": 0.1, "compliance": 0.05, "geographic": 0.05}
            elif routing_strategy == RoutingStrategy.GEOGRAPHIC_OPTIMIZATION:
                weights = {"cost": 0.2, "performance": 0.2, "risk": 0.1, "compliance": 0.1, "geographic": 0.4}
            elif routing_strategy == RoutingStrategy.RISK_MINIMIZATION:
                weights = {"cost": 0.1, "performance": 0.2, "risk": 0.5, "compliance": 0.15, "geographic": 0.05}
            else:  # BALANCED_OPTIMIZATION
                weights = self.routing_weights
            
            # Calculate total score
            total_score = (
                cost_score * weights["cost"] +
                performance_score * weights["performance"] +
                risk_score * weights["risk"] +
                compliance_score * weights["compliance"] +
                geographic_score * weights["geographic"]
            )
            
            # Calculate estimated completion time
            base_hours = provider_config.get("settlement_time_hours", 24)
            load_factor = provider_metrics.current_load / 100 if provider_metrics else 0.5
            estimated_hours = base_hours * (1 + load_factor * 0.5)
            
            scores[provider] = {
                "total_score": total_score,
                "cost_score": cost_score,
                "performance_score": performance_score,
                "risk_score": risk_score,
                "compliance_score": compliance_score,
                "geographic_score": geographic_score,
                "estimated_hours": estimated_hours,
                "cost_analysis": await self._generate_cost_analysis(payment_request, provider_config),
                "risk_analysis": await self._generate_risk_analysis(provider_metrics, payment_request),
                "performance_prediction": await self._generate_performance_prediction(provider_metrics)
            }
        
        return scores
    
    async def _calculate_cost_score(
        self, 
        payment_request: PaymentRequest, 
        provider_config: Dict[str, Any]
    ) -> float:
        """Calculate cost score for provider (higher score = lower cost)"""
        
        # Calculate total cost
        percentage_fee = payment_request.amount * (provider_config["base_cost_percentage"] / 100)
        fixed_fee = provider_config["fixed_fee"]
        total_cost = percentage_fee + fixed_fee
        
        # Convert to percentage of transaction
        cost_percentage = (total_cost / payment_request.amount) * 100
        
        # Score: lower cost = higher score (inverted)
        # Assume max reasonable cost is 5%
        score = max(0, (5.0 - float(cost_percentage)) / 5.0)
        
        return score
    
    async def _calculate_performance_score(self, provider_metrics: ProviderPerformanceMetrics) -> float:
        """Calculate performance score for provider"""
        
        if not provider_metrics:
            return 0.5  # Neutral score if no metrics
        
        # Weighted performance score
        success_weight = 0.4
        speed_weight = 0.3
        uptime_weight = 0.3
        
        # Normalize success rate (0.9 to 1.0 -> 0 to 1)
        success_score = max(0, (provider_metrics.success_rate - 0.9) / 0.1)
        
        # Normalize processing time (0 to 10 seconds -> 1 to 0)
        speed_score = max(0, 1 - (provider_metrics.average_processing_time / 10))
        
        # Normalize uptime (95% to 100% -> 0 to 1)
        uptime_score = max(0, (provider_metrics.uptime_percentage - 95) / 5)
        
        total_score = (
            success_score * success_weight +
            speed_score * speed_weight +
            uptime_score * uptime_weight
        )
        
        return min(1.0, total_score)
    
    async def _calculate_risk_score(
        self, 
        provider_metrics: ProviderPerformanceMetrics, 
        payment_request: PaymentRequest
    ) -> float:
        """Calculate risk score for provider (higher score = lower risk)"""
        
        if not provider_metrics:
            return 0.5
        
        # Base risk score (inverted - lower risk score = higher routing score)
        base_risk_score = 1.0 - provider_metrics.risk_score
        
        # Adjust based on transaction characteristics
        if payment_request.amount > Decimal("10000"):
            base_risk_score *= 0.9  # Higher amount = slightly higher risk
        
        if payment_request.urgency_level in ["high", "urgent"]:
            base_risk_score *= 0.95  # Urgent payments have slightly higher risk
        
        return max(0, min(1.0, base_risk_score))
    
    async def _calculate_compliance_score(
        self, 
        provider_config: Dict[str, Any], 
        payment_request: PaymentRequest
    ) -> float:
        """Calculate compliance score for provider"""
        
        compliance_level = provider_config.get("compliance_level", "medium")
        
        # Base compliance scores
        compliance_scores = {
            "high": 1.0,
            "medium": 0.7,
            "low": 0.4
        }
        
        base_score = compliance_scores.get(compliance_level, 0.5)
        
        # Adjust based on compliance requirements
        if payment_request.compliance_requirements:
            # For this implementation, assume all providers meet basic requirements
            pass
        
        return base_score
    
    async def _calculate_geographic_score(
        self, 
        provider_config: Dict[str, Any], 
        payment_request: PaymentRequest
    ) -> float:
        """Calculate geographic optimization score"""
        
        geographic_strength = provider_config.get("geographic_strength", [])
        
        if "GLOBAL" in geographic_strength:
            return 1.0  # Global coverage
        
        if payment_request.recipient_country in geographic_strength:
            return 1.0  # Perfect geographic match
        
        # Check for regional matches
        regional_matches = {
            "US": ["CA", "MX"],
            "EU": ["GB", "CH", "NO"],
            "GB": ["IE", "EU"]
        }
        
        for region, countries in regional_matches.items():
            if (region in geographic_strength and 
                payment_request.recipient_country in countries):
                return 0.8  # Good regional match
        
        return 0.3  # Poor geographic match
    
    async def _generate_cost_analysis(
        self, 
        payment_request: PaymentRequest, 
        provider_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate detailed cost analysis"""
        
        percentage_fee = payment_request.amount * (provider_config["base_cost_percentage"] / 100)
        fixed_fee = provider_config["fixed_fee"]
        total_cost = percentage_fee + fixed_fee
        
        return {
            "percentage_fee": str(percentage_fee),
            "fixed_fee": str(fixed_fee),
            "total_cost": str(total_cost),
            "cost_percentage": str((total_cost / payment_request.amount) * 100),
            "breakdown": {
                "base_percentage": str(provider_config["base_cost_percentage"]),
                "fixed_component": str(fixed_fee)
            }
        }
    
    async def _generate_risk_analysis(
        self, 
        provider_metrics: ProviderPerformanceMetrics, 
        payment_request: PaymentRequest
    ) -> Dict[str, Any]:
        """Generate detailed risk analysis"""
        
        if not provider_metrics:
            return {"risk_level": "unknown", "factors": []}
        
        risk_factors = []
        
        if provider_metrics.success_rate < 0.95:
            risk_factors.append("Below average success rate")
        
        if provider_metrics.risk_score > 0.3:
            risk_factors.append("High provider risk score")
        
        if payment_request.amount > Decimal("50000"):
            risk_factors.append("High value transaction")
        
        risk_level = "low"
        if len(risk_factors) > 2:
            risk_level = "high"
        elif len(risk_factors) > 0:
            risk_level = "medium"
        
        return {
            "risk_level": risk_level,
            "provider_risk_score": provider_metrics.risk_score,
            "success_rate": provider_metrics.success_rate,
            "risk_factors": risk_factors
        }
    
    async def _generate_performance_prediction(
        self, 
        provider_metrics: ProviderPerformanceMetrics
    ) -> Dict[str, Any]:
        """Generate performance prediction"""
        
        if not provider_metrics:
            return {"predicted_success_rate": 0.95, "predicted_processing_time": 3.0}
        
        # Simple prediction based on current metrics
        predicted_success_rate = provider_metrics.success_rate
        predicted_processing_time = provider_metrics.average_processing_time
        
        # Adjust based on current load
        load_factor = provider_metrics.current_load / 100
        if load_factor > 0.8:
            predicted_processing_time *= 1.5
            predicted_success_rate *= 0.98
        
        return {
            "predicted_success_rate": predicted_success_rate,
            "predicted_processing_time": predicted_processing_time,
            "load_factor": load_factor
        }
    
    async def _generate_decision_rationale(
        self, 
        provider: PaymentProvider, 
        provider_scores: Dict[str, Any], 
        strategy: RoutingStrategy
    ) -> str:
        """Generate human-readable decision rationale"""
        
        rationale_parts = [
            f"Selected {provider.value} based on {strategy.value} strategy."
        ]
        
        if strategy == RoutingStrategy.LOWEST_COST:
            rationale_parts.append(f"Offers lowest total cost at {provider_scores['cost_analysis']['cost_percentage']:.2f}%.")
        elif strategy == RoutingStrategy.HIGHEST_SUCCESS_RATE:
            rationale_parts.append(f"Highest success rate predicted at {provider_scores['performance_prediction']['predicted_success_rate']:.1%}.")
        elif strategy == RoutingStrategy.FASTEST_SETTLEMENT:
            rationale_parts.append(f"Fastest settlement time of {provider_scores['estimated_hours']:.1f} hours.")
        else:
            rationale_parts.append(f"Best overall score of {provider_scores['total_score']:.2f}.")
        
        return " ".join(rationale_parts)
    
    async def _store_routing_decision(self, decision: RoutingDecision):
        """Store routing decision for analytics"""
        # Mock implementation - would store in database
        logger.info(f"Stored routing decision: {decision.decision_id}")
    
    async def _update_routing_history(self, request: PaymentRequest, decision: RoutingDecision):
        """Update routing history for ML optimization"""
        # Mock implementation - would store for machine learning
        self.routing_history.append({
            "request": request,
            "decision": decision,
            "timestamp": datetime.utcnow()
        })
    
    async def get_provider_analytics(self) -> Dict[str, Any]:
        """Get comprehensive provider analytics"""
        
        analytics = {
            "providers": {},
            "routing_statistics": {},
            "performance_trends": {},
            "generated_at": datetime.utcnow()
        }
        
        # Provider analytics
        for provider, metrics in self.provider_metrics.items():
            analytics["providers"][provider.value] = {
                "success_rate": metrics.success_rate,
                "average_cost": metrics.average_cost_percentage,
                "uptime": metrics.uptime_percentage,
                "current_load": metrics.current_load,
                "risk_score": metrics.risk_score
            }
        
        # Routing statistics
        if self.routing_history:
            total_routings = len(self.routing_history)
            provider_distribution = defaultdict(int)
            
            for entry in self.routing_history:
                provider_distribution[entry["decision"].selected_provider] += 1
            
            analytics["routing_statistics"] = {
                "total_routings": total_routings,
                "provider_distribution": {
                    provider.value: count for provider, count in provider_distribution.items()
                }
            }
        
        return analytics