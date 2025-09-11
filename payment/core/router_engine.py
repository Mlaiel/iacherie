"""💳 Payment Router Engine
=========================

Intelligent payment routing engine that optimizes payment processing
by selecting the best provider based on amount, currency, location,
cost optimization, and performance metrics.

Features:
- Intelligent routing based on amount, currency, location
- Cost optimization across providers
- Performance-based routing decisions  
- Real-time provider selection algorithms
- Failover and load balancing
- Machine learning optimization

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import statistics
from collections import defaultdict

logger = logging.getLogger(__name__)


class RoutingStrategy(Enum):
    """Routing strategies"""
    COST_OPTIMIZATION = "cost_optimization"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    LOAD_BALANCING = "load_balancing"
    RELIABILITY_FIRST = "reliability_first"
    GEOGRAPHIC_OPTIMIZATION = "geographic_optimization"
    HYBRID = "hybrid"


class RouteDecisionFactor(Enum):
    """Factors considered in routing decisions"""
    TRANSACTION_FEE = "transaction_fee"
    SUCCESS_RATE = "success_rate"
    RESPONSE_TIME = "response_time"
    PROVIDER_LOAD = "provider_load"
    GEOGRAPHIC_PROXIMITY = "geographic_proximity"
    CURRENCY_SUPPORT = "currency_support"
    AMOUNT_LIMITS = "amount_limits"
    HISTORICAL_PERFORMANCE = "historical_performance"


@dataclass
class RoutingCriteria:
    """Criteria for payment routing decisions"""
    amount: Decimal
    currency: str
    source_country: str
    destination_country: Optional[str] = None
    payment_method: Optional[str] = None
    user_id: Optional[str] = None
    merchant_id: Optional[str] = None
    urgency_level: int = 1  # 1-5, 5 being most urgent
    preferred_providers: List[str] = field(default_factory=list)
    excluded_providers: List[str] = field(default_factory=list)
    routing_strategy: RoutingStrategy = RoutingStrategy.HYBRID


@dataclass
class ProviderMetrics:
    """Performance metrics for a payment provider"""
    provider_name: str
    success_rate: float
    average_response_time: float  # in seconds
    current_load: int  # number of active transactions
    availability: float  # uptime percentage
    cost_per_transaction: Decimal
    geographic_coverage: List[str]
    currency_exchange_rates: Dict[str, Decimal]
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class RoutingDecision:
    """Result of routing decision"""
    selected_provider: str
    backup_providers: List[str]
    routing_score: float
    decision_factors: Dict[RouteDecisionFactor, float]
    estimated_cost: Decimal
    estimated_time: float
    confidence_level: float
    reasoning: str
    fallback_strategy: Optional[str] = None


@dataclass
class RoutingRule:
    """Custom routing rule"""
    rule_id: str
    name: str
    conditions: Dict[str, Any]
    preferred_provider: str
    priority: int
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)


class PaymentRouterEngine:
    """
    Intelligent payment routing engine that optimizes provider selection
    based on multiple factors including cost, performance, and reliability.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize payment router engine"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Provider metrics tracking
        self.provider_metrics: Dict[str, ProviderMetrics] = {}
        
        # Routing rules
        self.routing_rules: List[RoutingRule] = []
        
        # Performance history
        self.performance_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        # Load balancing
        self.provider_loads: Dict[str, int] = defaultdict(int)
        
        # Geographic mapping
        self.geographic_mapping = self._initialize_geographic_mapping()
        
        # ML model for optimization (simplified)
        self.ml_weights: Dict[RouteDecisionFactor, float] = {
            RouteDecisionFactor.TRANSACTION_FEE: 0.25,
            RouteDecisionFactor.SUCCESS_RATE: 0.30,
            RouteDecisionFactor.RESPONSE_TIME: 0.20,
            RouteDecisionFactor.PROVIDER_LOAD: 0.10,
            RouteDecisionFactor.GEOGRAPHIC_PROXIMITY: 0.15
        }
    
    async def route_payment(self, criteria: RoutingCriteria, 
                          available_providers: List[str]) -> RoutingDecision:
        """
        Make intelligent routing decision based on criteria
        """
        try:
            self.logger.info(f"Routing payment: {criteria.amount} {criteria.currency}")
            
            # Filter providers based on criteria
            suitable_providers = await self._filter_suitable_providers(
                available_providers, criteria
            )
            
            if not suitable_providers:
                raise ValueError("No suitable providers found for routing criteria")
            
            # Apply custom routing rules first
            rule_provider = await self._check_routing_rules(criteria)
            if rule_provider and rule_provider in suitable_providers:
                return await self._create_rule_based_decision(rule_provider, criteria)
            
            # Calculate routing scores for each provider
            provider_scores = {}
            for provider in suitable_providers:
                score = await self._calculate_routing_score(provider, criteria)
                provider_scores[provider] = score
            
            # Select best provider based on strategy
            decision = await self._make_routing_decision(
                provider_scores, criteria
            )
            
            self.logger.info(f"Selected provider: {decision.selected_provider} "
                           f"(score: {decision.routing_score:.3f})")
            
            return decision
            
        except Exception as e:
            self.logger.error(f"Payment routing failed: {e}")
            raise
    
    async def _filter_suitable_providers(self, providers: List[str], 
                                       criteria: RoutingCriteria) -> List[str]:
        """Filter providers based on basic criteria"""
        suitable = []
        
        for provider in providers:
            # Skip excluded providers
            if provider in criteria.excluded_providers:
                continue
            
            # Check if provider metrics exist
            if provider not in self.provider_metrics:
                continue
                
            metrics = self.provider_metrics[provider]
            
            # Check currency support
            if criteria.currency not in metrics.currency_exchange_rates and \
               'ALL' not in metrics.currency_exchange_rates:
                continue
            
            # Check geographic coverage
            if criteria.source_country not in metrics.geographic_coverage and \
               'ALL' not in metrics.geographic_coverage:
                continue
            
            # Check availability
            if metrics.availability < 0.95:  # 95% minimum uptime
                continue
            
            suitable.append(provider)
        
        return suitable
    
    async def _calculate_routing_score(self, provider: str, 
                                     criteria: RoutingCriteria) -> Dict[str, float]:
        """Calculate comprehensive routing score for provider"""
        metrics = self.provider_metrics[provider]
        scores = {}
        
        # Cost score (lower cost = higher score)
        cost = await self._calculate_transaction_cost(provider, criteria)
        cost_score = max(0, 1 - (float(cost) / 100))  # Normalize to 0-1
        scores[RouteDecisionFactor.TRANSACTION_FEE] = cost_score
        
        # Success rate score
        scores[RouteDecisionFactor.SUCCESS_RATE] = metrics.success_rate
        
        # Response time score (faster = higher score)
        time_score = max(0, 1 - (metrics.average_response_time / 10))  # Normalize to 0-1
        scores[RouteDecisionFactor.RESPONSE_TIME] = time_score
        
        # Load balancing score (lower load = higher score)
        max_load = max(self.provider_loads.values()) if self.provider_loads else 100
        load_score = 1 - (self.provider_loads[provider] / max(max_load, 1))
        scores[RouteDecisionFactor.PROVIDER_LOAD] = load_score
        
        # Geographic proximity score
        geo_score = await self._calculate_geographic_score(provider, criteria)
        scores[RouteDecisionFactor.GEOGRAPHIC_PROXIMITY] = geo_score
        
        # Historical performance score
        history_score = await self._calculate_historical_score(provider)
        scores[RouteDecisionFactor.HISTORICAL_PERFORMANCE] = history_score
        
        return scores
    
    async def _calculate_transaction_cost(self, provider: str, 
                                        criteria: RoutingCriteria) -> Decimal:
        """Calculate total transaction cost for provider"""
        metrics = self.provider_metrics[provider]
        base_cost = metrics.cost_per_transaction
        
        # Add percentage-based fees
        percentage_fee = criteria.amount * Decimal("0.029")  # Example 2.9%
        
        # Add currency conversion costs if needed
        conversion_cost = Decimal("0")
        if criteria.currency in metrics.currency_exchange_rates:
            conversion_cost = criteria.amount * Decimal("0.01")  # 1% conversion fee
        
        return base_cost + percentage_fee + conversion_cost
    
    async def _calculate_geographic_score(self, provider: str, 
                                        criteria: RoutingCriteria) -> float:
        """Calculate geographic proximity score"""
        # Simplified geographic scoring
        # In practice, this would use actual geographic distance calculations
        if criteria.source_country in self.geographic_mapping.get(provider, []):
            return 1.0
        elif self._is_same_region(criteria.source_country, provider):
            return 0.7
        else:
            return 0.3
    
    async def _calculate_historical_score(self, provider: str) -> float:
        """Calculate score based on historical performance"""
        if provider not in self.performance_history:
            return 0.5  # Neutral score for new providers
        
        recent_history = self.performance_history[provider][-100:]  # Last 100 transactions
        
        if not recent_history:
            return 0.5
        
        # Calculate average success rate from recent history
        success_rates = [h.get('success', 0) for h in recent_history]
        return statistics.mean(success_rates) if success_rates else 0.5
    
    async def _make_routing_decision(self, provider_scores: Dict[str, Dict[str, float]], 
                                   criteria: RoutingCriteria) -> RoutingDecision:
        """Make final routing decision based on strategy and scores"""
        
        # Calculate weighted scores based on strategy
        weighted_scores = {}
        for provider, scores in provider_scores.items():
            total_score = 0
            for factor, score in scores.items():
                weight = self.ml_weights.get(factor, 0.1)
                total_score += score * weight
            weighted_scores[provider] = total_score
        
        # Sort providers by score
        sorted_providers = sorted(weighted_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Select primary and backup providers
        primary_provider = sorted_providers[0][0]
        backup_providers = [p[0] for p in sorted_providers[1:3]]  # Top 2 backups
        
        # Get detailed scores for selected provider
        selected_scores = provider_scores[primary_provider]
        
        # Calculate confidence level
        confidence = await self._calculate_confidence_level(
            primary_provider, sorted_providers
        )
        
        # Estimate cost and time
        estimated_cost = await self._calculate_transaction_cost(primary_provider, criteria)
        estimated_time = self.provider_metrics[primary_provider].average_response_time
        
        # Generate reasoning
        reasoning = await self._generate_reasoning(primary_provider, selected_scores)
        
        return RoutingDecision(
            selected_provider=primary_provider,
            backup_providers=backup_providers,
            routing_score=weighted_scores[primary_provider],
            decision_factors=selected_scores,
            estimated_cost=estimated_cost,
            estimated_time=estimated_time,
            confidence_level=confidence,
            reasoning=reasoning,
            fallback_strategy="round_robin"
        )
    
    async def _calculate_confidence_level(self, selected_provider: str, 
                                        sorted_providers: List[Tuple[str, float]]) -> float:
        """Calculate confidence level for routing decision"""
        if len(sorted_providers) < 2:
            return 1.0
        
        best_score = sorted_providers[0][1]
        second_best_score = sorted_providers[1][1]
        
        # Higher difference = higher confidence
        score_difference = best_score - second_best_score
        return min(1.0, 0.5 + score_difference)
    
    async def _generate_reasoning(self, provider: str, 
                                scores: Dict[RouteDecisionFactor, float]) -> str:
        """Generate human-readable reasoning for decision"""
        reasons = []
        
        # Find strongest factors
        sorted_factors = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        for factor, score in sorted_factors[:2]:  # Top 2 factors
            if score > 0.8:
                if factor == RouteDecisionFactor.SUCCESS_RATE:
                    reasons.append(f"high success rate ({score:.1%})")
                elif factor == RouteDecisionFactor.TRANSACTION_FEE:
                    reasons.append("competitive pricing")
                elif factor == RouteDecisionFactor.RESPONSE_TIME:
                    reasons.append("fast processing")
        
        if not reasons:
            reasons.append("balanced performance across factors")
        
        return f"Selected {provider} due to " + " and ".join(reasons)
    
    async def _check_routing_rules(self, criteria: RoutingCriteria) -> Optional[str]:
        """Check if any custom routing rules apply"""
        for rule in sorted(self.routing_rules, key=lambda x: x.priority):
            if not rule.enabled:
                continue
                
            if await self._rule_matches_criteria(rule, criteria):
                self.logger.info(f"Applied routing rule: {rule.name}")
                return rule.preferred_provider
        
        return None
    
    async def _rule_matches_criteria(self, rule: RoutingRule, 
                                   criteria: RoutingCriteria) -> bool:
        """Check if routing rule matches criteria"""
        conditions = rule.conditions
        
        # Check amount range
        if 'min_amount' in conditions and criteria.amount < Decimal(str(conditions['min_amount'])):
            return False
        if 'max_amount' in conditions and criteria.amount > Decimal(str(conditions['max_amount'])):
            return False
        
        # Check currency
        if 'currencies' in conditions and criteria.currency not in conditions['currencies']:
            return False
        
        # Check country
        if 'countries' in conditions and criteria.source_country not in conditions['countries']:
            return False
        
        return True
    
    async def _create_rule_based_decision(self, provider: str, 
                                        criteria: RoutingCriteria) -> RoutingDecision:
        """Create routing decision based on rule match"""
        estimated_cost = await self._calculate_transaction_cost(provider, criteria)
        
        return RoutingDecision(
            selected_provider=provider,
            backup_providers=[],
            routing_score=1.0,
            decision_factors={RouteDecisionFactor.TRANSACTION_FEE: 1.0},
            estimated_cost=estimated_cost,
            estimated_time=2.0,  # Default estimate
            confidence_level=1.0,
            reasoning=f"Selected {provider} based on routing rule",
            fallback_strategy="cost_optimization"
        )
    
    async def update_provider_metrics(self, provider: str, metrics: ProviderMetrics):
        """Update provider performance metrics"""
        self.provider_metrics[provider] = metrics
        self.logger.debug(f"Updated metrics for provider: {provider}")
    
    async def record_transaction_result(self, provider: str, success: bool, 
                                      response_time: float, cost: Decimal):
        """Record transaction result for learning"""
        result = {
            'success': 1 if success else 0,
            'response_time': response_time,
            'cost': float(cost),
            'timestamp': datetime.now().isoformat()
        }
        
        self.performance_history[provider].append(result)
        
        # Keep only recent history (last 1000 transactions)
        if len(self.performance_history[provider]) > 1000:
            self.performance_history[provider] = self.performance_history[provider][-1000:]
    
    async def add_routing_rule(self, rule: RoutingRule):
        """Add custom routing rule"""
        self.routing_rules.append(rule)
        self.routing_rules.sort(key=lambda x: x.priority)
        self.logger.info(f"Added routing rule: {rule.name}")
    
    async def optimize_ml_weights(self):
        """Optimize ML weights based on historical performance"""
        # Simplified ML optimization
        # In practice, this would use more sophisticated algorithms
        
        total_transactions = sum(len(history) for history in self.performance_history.values())
        if total_transactions < 100:
            return  # Need more data
        
        # Analyze which factors correlate with success
        factor_success_correlation = {}
        
        # This is a simplified example - real implementation would be more sophisticated
        for factor in RouteDecisionFactor:
            # Calculate correlation between factor score and success rate
            correlation = 0.5  # Placeholder
            factor_success_correlation[factor] = correlation
        
        # Update weights based on correlations
        total_correlation = sum(factor_success_correlation.values())
        for factor, correlation in factor_success_correlation.items():
            self.ml_weights[factor] = correlation / total_correlation
        
        self.logger.info("Updated ML weights based on historical performance")
    
    def _initialize_geographic_mapping(self) -> Dict[str, List[str]]:
        """Initialize geographic mapping for providers"""
        return {
            'stripe': ['US', 'CA', 'UK', 'DE', 'FR', 'AU'],
            'paypal': ['US', 'CA', 'UK', 'DE', 'FR', 'AU', 'JP'],
            'wise': ['UK', 'US', 'EU', 'CA', 'AU', 'SG'],
            'crypto': ['ALL']  # Cryptocurrency works globally
        }
    
    def _is_same_region(self, country: str, provider: str) -> bool:
        """Check if country is in same region as provider's primary coverage"""
        # Simplified region mapping
        europe = ['UK', 'DE', 'FR', 'IT', 'ES', 'NL']
        north_america = ['US', 'CA', 'MX']
        asia_pacific = ['JP', 'AU', 'SG', 'HK']
        
        provider_regions = self.geographic_mapping.get(provider, [])
        
        if country in europe and any(p in europe for p in provider_regions):
            return True
        if country in north_america and any(p in north_america for p in provider_regions):
            return True
        if country in asia_pacific and any(p in asia_pacific for p in provider_regions):
            return True
        
        return False


# Export main classes
__all__ = [
    "PaymentRouterEngine",
    "RoutingCriteria",
    "RoutingDecision",
    "ProviderMetrics",
    "RoutingRule",
    "RoutingStrategy",
    "RouteDecisionFactor"
]