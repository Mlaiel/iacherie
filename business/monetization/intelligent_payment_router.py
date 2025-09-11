"""
Intelligent Payment Router Module
=================================

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue - AI-Powered Content Protection and Monetization Platform
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides intelligent payment routing and optimization.
"""

from typing import Dict, Any, List, Optional, Union
import logging
from datetime import datetime, timedelta
from decimal import Decimal
import json
from pydantic import BaseModel, Field
from enum import Enum

logger = logging.getLogger(__name__)

# ============ PYDANTIC MODELS ============

class PaymentProvider(str, Enum):
    """Payment provider options"""
    STRIPE = "stripe"
    PAYPAL = "paypal" 
    CRYPTO = "crypto"
    BANK_TRANSFER = "bank_transfer"
    WISE = "wise"

class RoutingStrategy(str, Enum):
    """Payment routing strategies"""
    LOWEST_COST = "lowest_cost"
    FASTEST = "fastest"
    MOST_RELIABLE = "most_reliable"
    BALANCED = "balanced"
    REGIONAL = "regional"

class PaymentRequest(BaseModel):
    """Payment request definition"""
    model_config = {"protected_namespaces": ()}
    
    request_id: str = Field(..., description="Payment request ID")
    amount: Decimal = Field(..., description="Payment amount")
    currency: str = Field(default="USD", description="Currency code")
    sender_id: str = Field(..., description="Sender ID")
    recipient_id: str = Field(..., description="Recipient ID")
    payment_type: str = Field(..., description="Type of payment")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class IntelligentPaymentRouter:
    """AI-powered payment routing system"""
    
    def __init__(self):
        self.routing_strategies = {
            RoutingStrategy.LOWEST_COST: self._route_lowest_cost,
            RoutingStrategy.FASTEST: self._route_fastest,
            RoutingStrategy.MOST_RELIABLE: self._route_most_reliable,
            RoutingStrategy.BALANCED: self._route_balanced,
            RoutingStrategy.REGIONAL: self._route_regional
        }
        logger.info("IntelligentPaymentRouter initialized")
    
    def route_payment(self, request: PaymentRequest, strategy: RoutingStrategy = RoutingStrategy.BALANCED) -> Dict[str, Any]:
        """Route payment using intelligent selection"""
        try:
            routing_func = self.routing_strategies.get(strategy, self._route_balanced)
            routing_result = routing_func(request)
            
            return {
                'request_id': request.request_id,
                'recommended_provider': routing_result['provider'],
                'estimated_cost': routing_result['cost'],
                'estimated_time': routing_result['time'],
                'reliability_score': routing_result['reliability'],
                'routing_reason': routing_result['reason'],
                'alternative_providers': routing_result.get('alternatives', []),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error routing payment: {e}")
            return {'error': str(e)}
    
    def _route_lowest_cost(self, request: PaymentRequest) -> Dict[str, Any]:
        """Route based on lowest cost"""
        # Mock cost calculation
        provider_costs = {
            PaymentProvider.CRYPTO: float(request.amount) * 0.005,  # 0.5%
            PaymentProvider.BANK_TRANSFER: float(request.amount) * 0.01,  # 1%
            PaymentProvider.PAYPAL: float(request.amount) * 0.029,  # 2.9%
            PaymentProvider.STRIPE: float(request.amount) * 0.029,  # 2.9%
            PaymentProvider.WISE: float(request.amount) * 0.015,  # 1.5%
        }
        
        best_provider = min(provider_costs.keys(), key=lambda p: provider_costs[p])
        
        return {
            'provider': best_provider,
            'cost': provider_costs[best_provider],
            'time': 24,  # hours
            'reliability': 0.95,
            'reason': 'Lowest transaction cost'
        }
    
    def _route_fastest(self, request: PaymentRequest) -> Dict[str, Any]:
        """Route based on fastest processing"""
        # Mock processing times (in hours)
        provider_times = {
            PaymentProvider.STRIPE: 0.1,  # 6 minutes
            PaymentProvider.PAYPAL: 0.5,  # 30 minutes
            PaymentProvider.CRYPTO: 1.0,  # 1 hour
            PaymentProvider.WISE: 2.0,  # 2 hours
            PaymentProvider.BANK_TRANSFER: 24.0,  # 24 hours
        }
        
        fastest_provider = min(provider_times.keys(), key=lambda p: provider_times[p])
        
        return {
            'provider': fastest_provider,
            'cost': float(request.amount) * 0.029,  # Stripe fee
            'time': provider_times[fastest_provider],
            'reliability': 0.99,
            'reason': 'Fastest processing time'
        }
    
    def _route_most_reliable(self, request: PaymentRequest) -> Dict[str, Any]:
        """Route based on highest reliability"""
        # Mock reliability scores
        provider_reliability = {
            PaymentProvider.STRIPE: 0.999,
            PaymentProvider.PAYPAL: 0.995,
            PaymentProvider.BANK_TRANSFER: 0.998,
            PaymentProvider.WISE: 0.992,
            PaymentProvider.CRYPTO: 0.985,
        }
        
        most_reliable = max(provider_reliability.keys(), key=lambda p: provider_reliability[p])
        
        return {
            'provider': most_reliable,
            'cost': float(request.amount) * 0.029,
            'time': 0.1,  # Stripe is fast too
            'reliability': provider_reliability[most_reliable],
            'reason': 'Highest reliability score'
        }
    
    def _route_balanced(self, request: PaymentRequest) -> Dict[str, Any]:
        """Route using balanced scoring algorithm"""
        # Weighted scoring: cost (30%), time (30%), reliability (40%)
        providers_scores = {}
        
        for provider in PaymentProvider:
            cost_score = self._calculate_cost_score(request, provider)
            time_score = self._calculate_time_score(provider)
            reliability_score = self._calculate_reliability_score(provider)
            
            total_score = (cost_score * 0.3 + time_score * 0.3 + reliability_score * 0.4)
            providers_scores[provider] = total_score
        
        best_provider = max(providers_scores.keys(), key=lambda p: providers_scores[p])
        
        return {
            'provider': best_provider,
            'cost': self._get_provider_cost(request, best_provider),
            'time': self._get_provider_time(best_provider),
            'reliability': self._get_provider_reliability(best_provider),
            'reason': 'Optimal balance of cost, speed, and reliability'
        }
    
    def _route_regional(self, request: PaymentRequest) -> Dict[str, Any]:
        """Route based on regional optimization"""
        # Mock regional preferences
        region = request.metadata.get('region', 'US')
        
        regional_preferences = {
            'US': PaymentProvider.STRIPE,
            'EU': PaymentProvider.WISE,
            'GLOBAL': PaymentProvider.PAYPAL,
            'CRYPTO': PaymentProvider.CRYPTO
        }
        
        preferred_provider = regional_preferences.get(region, PaymentProvider.STRIPE)
        
        return {
            'provider': preferred_provider,
            'cost': self._get_provider_cost(request, preferred_provider),
            'time': self._get_provider_time(preferred_provider),
            'reliability': self._get_provider_reliability(preferred_provider),
            'reason': f'Optimized for {region} region'
        }
    
    def _calculate_cost_score(self, request: PaymentRequest, provider: PaymentProvider) -> float:
        """Calculate cost score (higher is better)"""
        cost = self._get_provider_cost(request, provider)
        max_cost = float(request.amount) * 0.05  # 5% as max reasonable fee
        return 1.0 - (cost / max_cost)
    
    def _calculate_time_score(self, provider: PaymentProvider) -> float:
        """Calculate time score (higher is better)"""
        time = self._get_provider_time(provider)
        max_time = 48.0  # 48 hours as max reasonable time
        return 1.0 - (time / max_time)
    
    def _calculate_reliability_score(self, provider: PaymentProvider) -> float:
        """Calculate reliability score"""
        return self._get_provider_reliability(provider)
    
    def _get_provider_cost(self, request: PaymentRequest, provider: PaymentProvider) -> float:
        """Get cost for specific provider"""
        cost_rates = {
            PaymentProvider.CRYPTO: 0.005,
            PaymentProvider.BANK_TRANSFER: 0.01,
            PaymentProvider.WISE: 0.015,
            PaymentProvider.PAYPAL: 0.029,
            PaymentProvider.STRIPE: 0.029,
        }
        return float(request.amount) * cost_rates[provider]
    
    def _get_provider_time(self, provider: PaymentProvider) -> float:
        """Get processing time for specific provider (in hours)"""
        times = {
            PaymentProvider.STRIPE: 0.1,
            PaymentProvider.PAYPAL: 0.5,
            PaymentProvider.CRYPTO: 1.0,
            PaymentProvider.WISE: 2.0,
            PaymentProvider.BANK_TRANSFER: 24.0,
        }
        return times[provider]
    
    def _get_provider_reliability(self, provider: PaymentProvider) -> float:
        """Get reliability score for specific provider"""
        reliability = {
            PaymentProvider.STRIPE: 0.999,
            PaymentProvider.PAYPAL: 0.995,
            PaymentProvider.BANK_TRANSFER: 0.998,
            PaymentProvider.WISE: 0.992,
            PaymentProvider.CRYPTO: 0.985,
        }
        return reliability[provider]

# Global instance
intelligent_payment_router = IntelligentPaymentRouter()

# Export main components
__all__ = [
    'IntelligentPaymentRouter',
    'PaymentRequest',
    'RoutingStrategy', 
    'PaymentProvider',
    'intelligent_payment_router'
]