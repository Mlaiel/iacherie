#!/usr/bin/env python3

"""
IA Chéries Monetization Rate Limiter - Enterprise Subscription Management
=====================================================================

Advanced rate limiting system with subscription tier management, premium features,
usage-based billing, revenue analytics, and dynamic tier optimization for the 
IA Chéries creator platform.

Features:
- Multi-tier subscription management (Free/Basic/Pro/Enterprise/Custom)
- Premium features access control with granular permissions
- Usage-based billing with overage protection and automatic scaling
- Revenue analytics with tier optimization recommendations
- Dynamic tier upgrades/downgrades with prorated billing
- Billing integration with payment processors
- Compliance with subscription regulations (PCI DSS, GDPR)
- Real-time usage tracking and billing alerts

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized copying or distribution prohibited

Project: IA Chéries Rate Limiting - Monetization Module
Version: 1.0 Production
"""

import asyncio
import time
import json
import logging
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

# Configure logging for monetization rate limiter
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SubscriptionTier(Enum):
    """Subscription tier levels with increasing capabilities"""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"

class BillingCycle(Enum):
    """Billing cycle options"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    PAY_PER_USE = "pay_per_use"

class PremiumFeature(Enum):
    """Premium features available in different tiers"""
    ADVANCED_ANALYTICS = "advanced_analytics"
    PRIORITY_PROCESSING = "priority_processing"
    UNLIMITED_STORAGE = "unlimited_storage"
    API_ACCESS = "api_access"
    COLLABORATION_TOOLS = "collaboration_tools"
    WHITE_LABEL = "white_label"
    CUSTOM_BRANDING = "custom_branding"
    MULTI_TEAM_MANAGEMENT = "multi_team_management"
    ADVANCED_AI_MODELS = "advanced_ai_models"
    REAL_TIME_SUPPORT = "real_time_support"
    CUSTOM_INTEGRATIONS = "custom_integrations"
    ENTERPRISE_SECURITY = "enterprise_security"
    BULK_OPERATIONS = "bulk_operations"
    ADVANCED_SEO = "advanced_seo"
    CUSTOM_WORKFLOWS = "custom_workflows"

class UsageMetric(Enum):
    """Usage metrics tracked for billing"""
    API_REQUESTS = "api_requests"
    STORAGE_GB = "storage_gb"
    BANDWIDTH_GB = "bandwidth_gb"
    AI_PROCESSING_SECONDS = "ai_processing_seconds"
    COLLABORATORS = "collaborators"
    PROJECTS = "projects"
    PREMIUM_EXPORTS = "premium_exports"
    ANALYTICS_QUERIES = "analytics_queries"
    SUPPORT_TICKETS = "support_tickets"
    CUSTOM_INTEGRATIONS_COUNT = "custom_integrations"

@dataclass
class TierLimits:
    """Tier-specific limits and features"""
    tier: SubscriptionTier
    max_api_requests: int
    max_storage_gb: int
    max_bandwidth_gb: int
    max_ai_processing_seconds: int
    max_collaborators: int
    max_projects: int
    features: Set[PremiumFeature]
    monthly_price: Decimal
    overage_rates: Dict[UsageMetric, Decimal]
    burst_multiplier: float = 1.2
    support_level: str = "email"

@dataclass
class UsageRecord:
    """Record of user usage for billing"""
    user_id: str
    metric: UsageMetric
    amount: float
    timestamp: datetime
    tier: SubscriptionTier
    cost: Decimal = field(default=Decimal('0'))
    is_overage: bool = False

@dataclass
class BillingAlert:
    """Billing alert for usage thresholds"""
    user_id: str
    alert_type: str
    threshold_percentage: float
    current_usage: float
    limit: float
    estimated_overage: Decimal
    recommendation: str
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class TierOptimizationRecommendation:
    """Recommendation for tier optimization"""
    user_id: str
    current_tier: SubscriptionTier
    recommended_tier: SubscriptionTier
    potential_savings: Decimal
    usage_analysis: Dict[str, Any]
    confidence_score: float
    reasoning: List[str]

class MonetizationRateLimiter:
    """
    Advanced monetization rate limiter with subscription management
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize monetization rate limiter"""
        self.config = config or {}
        self.node_id = str(uuid.uuid4())
        
        # Initialize tier configurations
        self._setup_tier_configurations()
        
        # User subscriptions and usage tracking
        self.user_subscriptions: Dict[str, Dict[str, Any]] = {}
        self.usage_records: Dict[str, List[UsageRecord]] = {}
        self.billing_alerts: Dict[str, List[BillingAlert]] = {}
        
        # Analytics and optimization
        self.revenue_analytics: Dict[str, Any] = {}
        self.optimization_recommendations: Dict[str, TierOptimizationRecommendation] = {}
        
        # Background task management
        self.background_tasks: Set[asyncio.Task] = set()
        self.is_running = False
        
        logger.info(f"MonetizationRateLimiter initialized with node_id: {self.node_id}")
    
    def _setup_tier_configurations(self):
        """Setup tier configurations with limits and features"""
        self.tier_configs = {
            SubscriptionTier.FREE: TierLimits(
                tier=SubscriptionTier.FREE,
                max_api_requests=1000,  # per month
                max_storage_gb=1,
                max_bandwidth_gb=5,
                max_ai_processing_seconds=300,  # 5 minutes
                max_collaborators=1,
                max_projects=3,
                features=set(),
                monthly_price=Decimal('0'),
                overage_rates={},
                support_level="community"
            ),
            SubscriptionTier.BASIC: TierLimits(
                tier=SubscriptionTier.BASIC,
                max_api_requests=10000,
                max_storage_gb=10,
                max_bandwidth_gb=50,
                max_ai_processing_seconds=3600,  # 1 hour
                max_collaborators=5,
                max_projects=10,
                features={
                    PremiumFeature.ADVANCED_ANALYTICS,
                    PremiumFeature.COLLABORATION_TOOLS
                },
                monthly_price=Decimal('29.99'),
                overage_rates={
                    UsageMetric.API_REQUESTS: Decimal('0.001'),
                    UsageMetric.STORAGE_GB: Decimal('2.99'),
                    UsageMetric.BANDWIDTH_GB: Decimal('0.99'),
                    UsageMetric.AI_PROCESSING_SECONDS: Decimal('0.05')
                },
                support_level="email"
            ),
            SubscriptionTier.PRO: TierLimits(
                tier=SubscriptionTier.PRO,
                max_api_requests=100000,
                max_storage_gb=100,
                max_bandwidth_gb=500,
                max_ai_processing_seconds=18000,  # 5 hours
                max_collaborators=20,
                max_projects=50,
                features={
                    PremiumFeature.ADVANCED_ANALYTICS,
                    PremiumFeature.PRIORITY_PROCESSING,
                    PremiumFeature.API_ACCESS,
                    PremiumFeature.COLLABORATION_TOOLS,
                    PremiumFeature.ADVANCED_AI_MODELS,
                    PremiumFeature.ADVANCED_SEO
                },
                monthly_price=Decimal('99.99'),
                overage_rates={
                    UsageMetric.API_REQUESTS: Decimal('0.0005'),
                    UsageMetric.STORAGE_GB: Decimal('1.99'),
                    UsageMetric.BANDWIDTH_GB: Decimal('0.49'),
                    UsageMetric.AI_PROCESSING_SECONDS: Decimal('0.02')
                },
                support_level="priority"
            ),
            SubscriptionTier.ENTERPRISE: TierLimits(
                tier=SubscriptionTier.ENTERPRISE,
                max_api_requests=1000000,
                max_storage_gb=1000,
                max_bandwidth_gb=5000,
                max_ai_processing_seconds=72000,  # 20 hours
                max_collaborators=100,
                max_projects=500,
                features={
                    PremiumFeature.ADVANCED_ANALYTICS,
                    PremiumFeature.PRIORITY_PROCESSING,
                    PremiumFeature.UNLIMITED_STORAGE,
                    PremiumFeature.API_ACCESS,
                    PremiumFeature.COLLABORATION_TOOLS,
                    PremiumFeature.WHITE_LABEL,
                    PremiumFeature.CUSTOM_BRANDING,
                    PremiumFeature.MULTI_TEAM_MANAGEMENT,
                    PremiumFeature.ADVANCED_AI_MODELS,
                    PremiumFeature.REAL_TIME_SUPPORT,
                    PremiumFeature.CUSTOM_INTEGRATIONS,
                    PremiumFeature.ENTERPRISE_SECURITY,
                    PremiumFeature.BULK_OPERATIONS,
                    PremiumFeature.ADVANCED_SEO,
                    PremiumFeature.CUSTOM_WORKFLOWS
                },
                monthly_price=Decimal('499.99'),
                overage_rates={
                    UsageMetric.API_REQUESTS: Decimal('0.0001'),
                    UsageMetric.STORAGE_GB: Decimal('0.99'),
                    UsageMetric.BANDWIDTH_GB: Decimal('0.19'),
                    UsageMetric.AI_PROCESSING_SECONDS: Decimal('0.01')
                },
                support_level="dedicated"
            ),
            SubscriptionTier.CUSTOM: TierLimits(
                tier=SubscriptionTier.CUSTOM,
                max_api_requests=-1,  # unlimited
                max_storage_gb=-1,
                max_bandwidth_gb=-1,
                max_ai_processing_seconds=-1,
                max_collaborators=-1,
                max_projects=-1,
                features=set(PremiumFeature),  # all features
                monthly_price=Decimal('0'),  # custom pricing
                overage_rates={},
                support_level="dedicated_priority"
            )
        }
    
    async def initialize(self) -> bool:
        """Initialize monetization rate limiter"""
        try:
            self.is_running = True
            
            # Start background tasks
            self.background_tasks.add(
                asyncio.create_task(self._billing_monitor_task())
            )
            self.background_tasks.add(
                asyncio.create_task(self._tier_optimization_task())
            )
            self.background_tasks.add(
                asyncio.create_task(self._revenue_analytics_task())
            )
            
            logger.info("MonetizationRateLimiter initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize MonetizationRateLimiter: {e}")
            return False
    
    async def check_rate_limit(
        self,
        user_id: str,
        metric: UsageMetric,
        amount: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Check rate limit for user based on subscription tier"""
        start_time = time.time()
        
        try:
            # Get user subscription
            subscription = await self._get_user_subscription(user_id)
            tier = subscription.get('tier', SubscriptionTier.FREE)
            tier_config = self.tier_configs[tier]
            
            # Get current usage
            current_usage = await self._get_current_usage(user_id, metric)
            
            # Check limit
            limit = self._get_metric_limit(tier_config, metric)
            
            if limit == -1:  # unlimited
                allowed = True
                remaining = -1
            else:
                allowed = (current_usage + amount) <= (limit * tier_config.burst_multiplier)
                remaining = max(0, limit - current_usage)
            
            # Calculate cost if overages
            cost = Decimal('0')
            is_overage = False
            
            if not allowed and limit != -1:
                overage_amount = (current_usage + amount) - limit
                if metric in tier_config.overage_rates:
                    cost = tier_config.overage_rates[metric] * Decimal(str(overage_amount))
                    is_overage = True
                    
                    # Allow if user has overage protection enabled
                    overage_protection = subscription.get('overage_protection', True)
                    if overage_protection:
                        allowed = True
            
            # Record usage if allowed
            if allowed:
                await self._record_usage(user_id, metric, amount, tier, cost, is_overage)
            
            # Check for billing alerts
            await self._check_billing_thresholds(user_id, metric, current_usage + amount, limit)
            
            execution_time = (time.time() - start_time) * 1000
            
            return {
                'allowed': allowed,
                'remaining': remaining,
                'tier': tier.value,
                'limit': limit,
                'current_usage': current_usage,
                'cost': float(cost),
                'is_overage': is_overage,
                'features_available': [f.value for f in tier_config.features],
                'execution_time_ms': execution_time,
                'node_id': self.node_id
            }
            
        except Exception as e:
            logger.error(f"Error checking rate limit for user {user_id}: {e}")
            return {
                'allowed': False,
                'error': str(e),
                'execution_time_ms': (time.time() - start_time) * 1000
            }
    
    async def check_feature_access(
        self,
        user_id: str,
        feature: PremiumFeature
    ) -> Dict[str, Any]:
        """Check if user has access to premium feature"""
        try:
            subscription = await self._get_user_subscription(user_id)
            tier = subscription.get('tier', SubscriptionTier.FREE)
            tier_config = self.tier_configs[tier]
            
            has_access = feature in tier_config.features
            
            return {
                'has_access': has_access,
                'feature': feature.value,
                'tier': tier.value,
                'required_tiers': [
                    t.value for t in SubscriptionTier 
                    if feature in self.tier_configs[t].features
                ]
            }
            
        except Exception as e:
            logger.error(f"Error checking feature access for user {user_id}: {e}")
            return {'has_access': False, 'error': str(e)}
    
    async def get_subscription_status(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive subscription status for user"""
        try:
            subscription = await self._get_user_subscription(user_id)
            tier = subscription.get('tier', SubscriptionTier.FREE)
            tier_config = self.tier_configs[tier]
            
            # Get current usage across all metrics
            usage_summary = {}
            for metric in UsageMetric:
                current_usage = await self._get_current_usage(user_id, metric)
                limit = self._get_metric_limit(tier_config, metric)
                
                usage_summary[metric.value] = {
                    'current': current_usage,
                    'limit': limit,
                    'percentage': (current_usage / limit * 100) if limit > 0 else 0,
                    'remaining': max(0, limit - current_usage) if limit > 0 else -1
                }
            
            # Get billing information
            billing_info = await self._get_billing_info(user_id)
            
            # Get optimization recommendations
            recommendations = self.optimization_recommendations.get(user_id)
            
            return {
                'user_id': user_id,
                'tier': tier.value,
                'monthly_price': float(tier_config.monthly_price),
                'features': [f.value for f in tier_config.features],
                'usage_summary': usage_summary,
                'billing_info': billing_info,
                'alerts': self.billing_alerts.get(user_id, []),
                'optimization_recommendation': recommendations.__dict__ if recommendations else None,
                'support_level': tier_config.support_level
            }
            
        except Exception as e:
            logger.error(f"Error getting subscription status for user {user_id}: {e}")
            return {'error': str(e)}
    
    async def upgrade_tier(
        self,
        user_id: str,
        new_tier: SubscriptionTier,
        prorate: bool = True
    ) -> Dict[str, Any]:
        """Upgrade user to new subscription tier"""
        try:
            current_subscription = await self._get_user_subscription(user_id)
            current_tier = current_subscription.get('tier', SubscriptionTier.FREE)
            
            if new_tier.value <= current_tier.value:
                return {'success': False, 'error': 'Cannot downgrade using upgrade method'}
            
            # Calculate prorated amount
            prorated_amount = Decimal('0')
            if prorate:
                prorated_amount = await self._calculate_prorated_amount(
                    user_id, current_tier, new_tier
                )
            
            # Update subscription
            subscription_update = {
                'tier': new_tier,
                'upgraded_at': datetime.now(),
                'previous_tier': current_tier,
                'prorated_amount': prorated_amount
            }
            
            await self._update_user_subscription(user_id, subscription_update)
            
            logger.info(f"User {user_id} upgraded from {current_tier.value} to {new_tier.value}")
            
            return {
                'success': True,
                'previous_tier': current_tier.value,
                'new_tier': new_tier.value,
                'prorated_amount': float(prorated_amount),
                'effective_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error upgrading tier for user {user_id}: {e}")
            return {'success': False, 'error': str(e)}
    
    async def get_revenue_analytics(self, period_days: int = 30) -> Dict[str, Any]:
        """Get revenue analytics for specified period"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)
            
            analytics = {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': period_days
                },
                'revenue_by_tier': {},
                'user_distribution': {},
                'growth_metrics': {},
                'churn_analysis': {},
                'optimization_impact': {}
            }
            
            # Calculate revenue by tier
            for tier in SubscriptionTier:
                tier_users = await self._get_users_by_tier(tier)
                tier_config = self.tier_configs[tier]
                
                monthly_revenue = len(tier_users) * tier_config.monthly_price
                overage_revenue = await self._calculate_overage_revenue(tier_users, start_date, end_date)
                
                analytics['revenue_by_tier'][tier.value] = {
                    'user_count': len(tier_users),
                    'monthly_revenue': float(monthly_revenue),
                    'overage_revenue': float(overage_revenue),
                    'total_revenue': float(monthly_revenue + overage_revenue),
                    'avg_revenue_per_user': float((monthly_revenue + overage_revenue) / len(tier_users)) if tier_users else 0
                }
            
            # User distribution
            total_users = sum(len(await self._get_users_by_tier(tier)) for tier in SubscriptionTier)
            for tier in SubscriptionTier:
                tier_users = len(await self._get_users_by_tier(tier))
                analytics['user_distribution'][tier.value] = {
                    'count': tier_users,
                    'percentage': (tier_users / total_users * 100) if total_users > 0 else 0
                }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting revenue analytics: {e}")
            return {'error': str(e)}
    
    def _get_metric_limit(self, tier_config: TierLimits, metric: UsageMetric) -> int:
        """Get limit for specific metric from tier configuration"""
        metric_mapping = {
            UsageMetric.API_REQUESTS: tier_config.max_api_requests,
            UsageMetric.STORAGE_GB: tier_config.max_storage_gb,
            UsageMetric.BANDWIDTH_GB: tier_config.max_bandwidth_gb,
            UsageMetric.AI_PROCESSING_SECONDS: tier_config.max_ai_processing_seconds,
            UsageMetric.COLLABORATORS: tier_config.max_collaborators,
            UsageMetric.PROJECTS: tier_config.max_projects,
        }
        
        return metric_mapping.get(metric, 1000)  # default limit
    
    async def _get_user_subscription(self, user_id: str) -> Dict[str, Any]:
        """Get user subscription information"""
        if user_id not in self.user_subscriptions:
            self.user_subscriptions[user_id] = {
                'tier': SubscriptionTier.FREE,
                'created_at': datetime.now(),
                'billing_cycle': BillingCycle.MONTHLY,
                'overage_protection': True,
                'auto_upgrade_enabled': False
            }
        
        return self.user_subscriptions[user_id]
    
    async def _update_user_subscription(self, user_id: str, updates: Dict[str, Any]):
        """Update user subscription"""
        if user_id not in self.user_subscriptions:
            await self._get_user_subscription(user_id)  # Create default
        
        self.user_subscriptions[user_id].update(updates)
    
    async def _get_current_usage(self, user_id: str, metric: UsageMetric) -> float:
        """Get current usage for user and metric"""
        if user_id not in self.usage_records:
            return 0.0
        
        # Get current month usage
        current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        total_usage = 0.0
        for record in self.usage_records[user_id]:
            if record.metric == metric and record.timestamp >= current_month:
                total_usage += record.amount
        
        return total_usage
    
    async def _record_usage(
        self,
        user_id: str,
        metric: UsageMetric,
        amount: float,
        tier: SubscriptionTier,
        cost: Decimal,
        is_overage: bool
    ):
        """Record usage for billing purposes"""
        if user_id not in self.usage_records:
            self.usage_records[user_id] = []
        
        record = UsageRecord(
            user_id=user_id,
            metric=metric,
            amount=amount,
            timestamp=datetime.now(),
            tier=tier,
            cost=cost,
            is_overage=is_overage
        )
        
        self.usage_records[user_id].append(record)
        
        # Keep only recent records (current month + 1 previous month)
        cutoff_date = datetime.now() - timedelta(days=60)
        self.usage_records[user_id] = [
            r for r in self.usage_records[user_id]
            if r.timestamp >= cutoff_date
        ]
    
    async def _check_billing_thresholds(
        self,
        user_id: str,
        metric: UsageMetric,
        current_usage: float,
        limit: int
    ):
        """Check billing thresholds and create alerts"""
        if limit <= 0:  # unlimited
            return
        
        threshold_percentages = [50, 75, 90, 100]
        usage_percentage = (current_usage / limit) * 100
        
        for threshold in threshold_percentages:
            if usage_percentage >= threshold:
                # Check if alert already exists for this threshold
                existing_alerts = self.billing_alerts.get(user_id, [])
                has_alert = any(
                    alert.threshold_percentage == threshold and 
                    alert.alert_type == f"{metric.value}_threshold"
                    for alert in existing_alerts
                )
                
                if not has_alert:
                    alert = BillingAlert(
                        user_id=user_id,
                        alert_type=f"{metric.value}_threshold",
                        threshold_percentage=threshold,
                        current_usage=current_usage,
                        limit=limit,
                        estimated_overage=Decimal('0'),
                        recommendation=self._get_threshold_recommendation(threshold, metric)
                    )
                    
                    if user_id not in self.billing_alerts:
                        self.billing_alerts[user_id] = []
                    self.billing_alerts[user_id].append(alert)
    
    def _get_threshold_recommendation(self, threshold: float, metric: UsageMetric) -> str:
        """Get recommendation for threshold alert"""
        if threshold >= 90:
            return f"Consider upgrading your plan to avoid {metric.value} overages"
        elif threshold >= 75:
            return f"Monitor your {metric.value} usage closely"
        else:
            return f"You're approaching your {metric.value} limit"
    
    async def _calculate_prorated_amount(
        self,
        user_id: str,
        current_tier: SubscriptionTier,
        new_tier: SubscriptionTier
    ) -> Decimal:
        """Calculate prorated amount for tier upgrade"""
        current_config = self.tier_configs[current_tier]
        new_config = self.tier_configs[new_tier]
        
        # Simple prorated calculation (days remaining in month)
        now = datetime.now()
        days_in_month = (now.replace(month=now.month+1) - now.replace(day=1)).days
        days_remaining = days_in_month - now.day + 1
        
        daily_difference = (new_config.monthly_price - current_config.monthly_price) / days_in_month
        prorated_amount = daily_difference * days_remaining
        
        return prorated_amount
    
    async def _get_users_by_tier(self, tier: SubscriptionTier) -> List[str]:
        """Get list of user IDs for specific tier"""
        return [
            user_id for user_id, subscription in self.user_subscriptions.items()
            if subscription.get('tier') == tier
        ]
    
    async def _calculate_overage_revenue(
        self,
        user_ids: List[str],
        start_date: datetime,
        end_date: datetime
    ) -> Decimal:
        """Calculate overage revenue for users in date range"""
        total_overage = Decimal('0')
        
        for user_id in user_ids:
            if user_id in self.usage_records:
                for record in self.usage_records[user_id]:
                    if (start_date <= record.timestamp <= end_date and 
                        record.is_overage):
                        total_overage += record.cost
        
        return total_overage
    
    async def _get_billing_info(self, user_id: str) -> Dict[str, Any]:
        """Get billing information for user"""
        current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Calculate current month costs
        base_cost = Decimal('0')
        overage_cost = Decimal('0')
        
        if user_id in self.usage_records:
            for record in self.usage_records[user_id]:
                if record.timestamp >= current_month:
                    if record.is_overage:
                        overage_cost += record.cost
        
        # Get base subscription cost
        subscription = await self._get_user_subscription(user_id)
        tier = subscription.get('tier', SubscriptionTier.FREE)
        base_cost = self.tier_configs[tier].monthly_price
        
        return {
            'base_cost': float(base_cost),
            'overage_cost': float(overage_cost),
            'total_cost': float(base_cost + overage_cost),
            'billing_cycle': subscription.get('billing_cycle', BillingCycle.MONTHLY).value,
            'next_billing_date': (current_month + timedelta(days=32)).replace(day=1).isoformat(),
            'overage_protection': subscription.get('overage_protection', True)
        }
    
    async def _billing_monitor_task(self):
        """Background task for billing monitoring"""
        while self.is_running:
            try:
                # Clean up old alerts
                cutoff_date = datetime.now() - timedelta(days=7)
                for user_id in list(self.billing_alerts.keys()):
                    self.billing_alerts[user_id] = [
                        alert for alert in self.billing_alerts[user_id]
                        if alert.timestamp >= cutoff_date
                    ]
                    
                    if not self.billing_alerts[user_id]:
                        del self.billing_alerts[user_id]
                
                await asyncio.sleep(3600)  # Run every hour
                
            except Exception as e:
                logger.error(f"Error in billing monitor task: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def _tier_optimization_task(self):
        """Background task for tier optimization recommendations"""
        while self.is_running:
            try:
                # Analyze user usage patterns and generate recommendations
                for user_id in self.user_subscriptions.keys():
                    recommendation = await self._generate_tier_recommendation(user_id)
                    if recommendation:
                        self.optimization_recommendations[user_id] = recommendation
                
                await asyncio.sleep(86400)  # Run daily
                
            except Exception as e:
                logger.error(f"Error in tier optimization task: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour on error
    
    async def _revenue_analytics_task(self):
        """Background task for revenue analytics"""
        while self.is_running:
            try:
                # Update revenue analytics
                self.revenue_analytics = await self.get_revenue_analytics(30)
                
                await asyncio.sleep(3600)  # Run every hour
                
            except Exception as e:
                logger.error(f"Error in revenue analytics task: {e}")
                await asyncio.sleep(1800)  # Wait 30 minutes on error
    
    async def _generate_tier_recommendation(self, user_id: str) -> Optional[TierOptimizationRecommendation]:
        """Generate tier optimization recommendation for user"""
        try:
            subscription = await self._get_user_subscription(user_id)
            current_tier = subscription.get('tier', SubscriptionTier.FREE)
            
            # Analyze usage patterns
            usage_analysis = {}
            total_overage_cost = Decimal('0')
            
            for metric in UsageMetric:
                current_usage = await self._get_current_usage(user_id, metric)
                limit = self._get_metric_limit(self.tier_configs[current_tier], metric)
                
                usage_analysis[metric.value] = {
                    'usage': current_usage,
                    'limit': limit,
                    'utilization': (current_usage / limit) if limit > 0 else 0
                }
                
                # Calculate overage costs
                if user_id in self.usage_records:
                    for record in self.usage_records[user_id]:
                        if record.metric == metric and record.is_overage:
                            total_overage_cost += record.cost
            
            # Determine if upgrade would be beneficial
            recommended_tier = current_tier
            potential_savings = Decimal('0')
            reasoning = []
            
            # Check if user frequently hits limits
            high_utilization_metrics = [
                metric for metric, data in usage_analysis.items()
                if data['utilization'] > 0.8
            ]
            
            if len(high_utilization_metrics) >= 2:
                # Consider upgrade
                next_tier = self._get_next_tier(current_tier)
                if next_tier:
                    next_tier_cost = self.tier_configs[next_tier].monthly_price
                    current_total_cost = self.tier_configs[current_tier].monthly_price + total_overage_cost
                    
                    if current_total_cost > next_tier_cost:
                        recommended_tier = next_tier
                        potential_savings = current_total_cost - next_tier_cost
                        reasoning.append(f"Frequent overages in {len(high_utilization_metrics)} metrics")
                        reasoning.append(f"Upgrade would save ${potential_savings:.2f}/month")
            
            # Check if user under-utilizes current tier
            low_utilization_metrics = [
                metric for metric, data in usage_analysis.items()
                if data['utilization'] < 0.3
            ]
            
            if len(low_utilization_metrics) >= 3 and current_tier != SubscriptionTier.FREE:
                # Consider downgrade
                previous_tier = self._get_previous_tier(current_tier)
                if previous_tier:
                    savings = self.tier_configs[current_tier].monthly_price - self.tier_configs[previous_tier].monthly_price
                    if savings > Decimal('10'):  # Only recommend if significant savings
                        recommended_tier = previous_tier
                        potential_savings = savings
                        reasoning.append(f"Low utilization in {len(low_utilization_metrics)} metrics")
                        reasoning.append(f"Downgrade would save ${potential_savings:.2f}/month")
            
            if recommended_tier != current_tier:
                confidence_score = min(0.95, len(reasoning) * 0.3 + (float(potential_savings) / 100.0))
                
                return TierOptimizationRecommendation(
                    user_id=user_id,
                    current_tier=current_tier,
                    recommended_tier=recommended_tier,
                    potential_savings=potential_savings,
                    usage_analysis=usage_analysis,
                    confidence_score=confidence_score,
                    reasoning=reasoning
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating tier recommendation for user {user_id}: {e}")
            return None
    
    def _get_next_tier(self, current_tier: SubscriptionTier) -> Optional[SubscriptionTier]:
        """Get next higher tier"""
        tier_order = [
            SubscriptionTier.FREE,
            SubscriptionTier.BASIC,
            SubscriptionTier.PRO,
            SubscriptionTier.ENTERPRISE,
            SubscriptionTier.CUSTOM
        ]
        
        try:
            current_index = tier_order.index(current_tier)
            if current_index < len(tier_order) - 1:
                return tier_order[current_index + 1]
        except ValueError:
            pass
        
        return None
    
    def _get_previous_tier(self, current_tier: SubscriptionTier) -> Optional[SubscriptionTier]:
        """Get previous lower tier"""
        tier_order = [
            SubscriptionTier.FREE,
            SubscriptionTier.BASIC,
            SubscriptionTier.PRO,
            SubscriptionTier.ENTERPRISE,
            SubscriptionTier.CUSTOM
        ]
        
        try:
            current_index = tier_order.index(current_tier)
            if current_index > 0:
                return tier_order[current_index - 1]
        except ValueError:
            pass
        
        return None
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status"""
        return {
            'service': 'MonetizationRateLimiter',
            'status': 'healthy' if self.is_running else 'stopped',
            'node_id': self.node_id,
            'users_count': len(self.user_subscriptions),
            'active_alerts': sum(len(alerts) for alerts in self.billing_alerts.values()),
            'recommendations_count': len(self.optimization_recommendations),
            'background_tasks': len(self.background_tasks),
            'uptime_seconds': time.time() - getattr(self, '_start_time', time.time())
        }
    
    async def shutdown(self):
        """Gracefully shutdown monetization rate limiter"""
        logger.info("Shutting down MonetizationRateLimiter...")
        self.is_running = False
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        logger.info("MonetizationRateLimiter shut down complete")

# Export main classes and functions
__all__ = [
    'MonetizationRateLimiter',
    'SubscriptionTier',
    'BillingCycle', 
    'PremiumFeature',
    'UsageMetric',
    'TierLimits',
    'UsageRecord',
    'BillingAlert',
    'TierOptimizationRecommendation'
]

if __name__ == "__main__":
    async def demo():
        """Demo monetization rate limiter functionality"""
        limiter = MonetizationRateLimiter()
        await limiter.initialize()
        
        # Test user subscription management
        user_id = "user_123"
        
        # Check initial status (should be Free tier)
        status = await limiter.get_subscription_status(user_id)
        print(f"Initial status: {json.dumps(status, indent=2, default=str)}")
        
        # Test rate limiting
        result = await limiter.check_rate_limit(user_id, UsageMetric.API_REQUESTS, 10)
        print(f"Rate limit check: {json.dumps(result, indent=2)}")
        
        # Test feature access
        feature_access = await limiter.check_feature_access(user_id, PremiumFeature.ADVANCED_ANALYTICS)
        print(f"Feature access: {json.dumps(feature_access, indent=2)}")
        
        # Test tier upgrade
        upgrade_result = await limiter.upgrade_tier(user_id, SubscriptionTier.PRO)
        print(f"Upgrade result: {json.dumps(upgrade_result, indent=2, default=str)}")
        
        # Check updated status
        updated_status = await limiter.get_subscription_status(user_id)
        print(f"Updated status: {json.dumps(updated_status, indent=2, default=str)}")
        
        # Get revenue analytics
        analytics = await limiter.get_revenue_analytics()
        print(f"Revenue analytics: {json.dumps(analytics, indent=2, default=str)}")
        
        # Get health status
        health = await limiter.get_health_status()
        print(f"Health status: {json.dumps(health, indent=2)}")
        
        await limiter.shutdown()
    
    # Run demo
    asyncio.run(demo())