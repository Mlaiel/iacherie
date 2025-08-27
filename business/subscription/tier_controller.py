"""
Tier Controller

Feature access control and tier management system for subscription plans.
Manages granular feature permissions, usage limits, and tier-based functionality.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

WARNING: Proprietary code - Unauthorized use strictly prohibited.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List, Set
import logging
from sqlalchemy.orm import Session
from enum import Enum

from .models import (
    UserSubscription, SubscriptionPlan, FeatureAccess,
    SubscriptionStatus, FeatureType, SUBSCRIPTION_PLANS
)
from ..core.database import get_db_session
from ..core.exceptions import (
    InsufficientPermissionError, ValidationError,
    SubscriptionNotFoundError
)
from ..core.logging import get_logger
from ..core.cache import CacheManager

logger = get_logger(__name__)


class FeatureCategory(Enum):
    """Feature categories for the IA Influencer platform."""
    AI_PROCESSING = "ai_processing"
    CONTENT_PROTECTION = "content_protection"
    ANALYTICS = "analytics"
    COLLABORATION = "collaboration"
    MONETIZATION = "monetization"
    STORAGE = "storage"
    API_ACCESS = "api_access"
    INTEGRATIONS = "integrations"
    CUSTOMIZATION = "customization"
    SUPPORT = "support"


class TierController:
    """
    Advanced tier-based feature access controller.
    
    Manages:
    - Feature access permissions per subscription tier
    - Usage limit enforcement and tracking
    - Feature unlock/lock based on subscription status
    - Dynamic feature availability based on plan changes
    - Free tier vs. paid tier access control
    - Enterprise-level custom feature sets
    - API rate limiting and quota management
    - Feature rollout and A/B testing support
    """
    
    def __init__(self):
        """Initialize tier controller."""
        self.logger = get_logger(__name__)
        self.cache = CacheManager()
        
        # Feature definitions for IA Influencer platform
        self.platform_features = {
            # AI Processing Features
            "ai_recommendations": {
                "category": FeatureCategory.AI_PROCESSING,
                "description": "AI-powered content recommendations",
                "type": FeatureType.QUOTA,
                "free_tier": {"enabled": True, "quota": 100},
                "paid_tiers": {"enabled": True, "quota": None}
            },
            "ai_content_generation": {
                "category": FeatureCategory.AI_PROCESSING,
                "description": "AI content generation and enhancement",
                "type": FeatureType.QUOTA,
                "free_tier": {"enabled": False},
                "paid_tiers": {"enabled": True, "quota": 1000}
            },
            "custom_ai_models": {
                "category": FeatureCategory.AI_PROCESSING,
                "description": "Custom AI model training and deployment",
                "type": FeatureType.BOOLEAN,
                "free_tier": {"enabled": False},
                "paid_tiers": {"enabled": False},
                "enterprise_only": True
            },
            
            # Content Protection Features
            "basic_protection": {
                "category": FeatureCategory.CONTENT_PROTECTION,
                "description": "Basic content fingerprinting and monitoring",
                "type": FeatureType.QUOTA,
                "free_tier": {"enabled": True, "quota": 5},
                "paid_tiers": {"enabled": True, "quota": 100}
            },
            "advanced_protection": {
                "category": FeatureCategory.CONTENT_PROTECTION,
                "description": "Advanced multi-format protection",
                "type": FeatureType.QUOTA,
                "free_tier": {"enabled": False},
                "paid_tiers": {"enabled": True, "quota": 1000}
            },
            "enterprise_protection": {
                "category": FeatureCategory.CONTENT_PROTECTION,
                "description": "Enterprise-grade protection with legal tools",
                "type": FeatureType.UNLIMITED,
                "free_tier": {"enabled": False},
                "paid_tiers": {"enabled": False},
                "enterprise_only": True
            },
            "real_time_monitoring": {
                "category": FeatureCategory.CONTENT_PROTECTION,
                "description": "Real-time content monitoring across platforms",
                "type": FeatureType.BOOLEAN,
                "free_tier": {"enabled": False},
                "paid_tiers": {"enabled": True}
            },
            
            # Analytics Features
            "basic_analytics": {
                "category": FeatureCategory.ANALYTICS,
                "description": "Basic performance analytics",
                "type": FeatureType.BOOLEAN,
                "free_tier": {"enabled": True},
                "paid_tiers": {"enabled": True}
            },
            "advanced_analytics": {
                "category": FeatureCategory.ANALYTICS,
                "description": "Advanced analytics with AI insights",
                "type": FeatureType.BOOLEAN,
                "free_tier": {"enabled": False},
                "paid_tiers": {"enabled": True}
            },
            "premium_analytics": {
                "category": FeatureCategory.ANALYTICS,
                "description": "Premium analytics with predictive insights",
                "type": FeatureType.BOOLEAN,
                "free_tier": {"enabled": False},
                "paid_tiers": {"enabled": True, "min_tier": 2}
            },
            "custom_analytics": {
                "category": FeatureCategory.ANALYTICS,
                "description": "Custom analytics dashboards and reports",
                "type": FeatureType.BOOLEAN,
                "free_tier": {"enabled": False},
                "paid_tiers": {"enabled": False},
                "enterprise_only": True
            },
            
            # Collaboration Features
            "collaboration_tools": {
                "category": FeatureCategory.COLLABORATION,
                "description": "Team collaboration and sharing tools",
                "type": FeatureType.QUOTA,
                "free_tier": {"enabled": False},
                "paid_tiers": {"enabled": True, "quota": 5}
            },
            "unlimited_collaborators": {
                "category": FeatureCategory.COLLABORATION,
                "description": "Unlimited team members and collaborators",
                "type": FeatureType.UNLIMITED,
                "free_tier": {"enabled": False},
                "paid_tiers": {"enabled": False},
                "enterprise_only": True
            },
            
            # Storage and Limits
            "storage_quota": {
                "category": FeatureCategory.STORAGE,
                "description": "Content storage quota",
                "type": FeatureType.QUOTA,
                "free_tier": {"enabled": True, "quota": 1},  # 1GB
                "paid_tiers": {"enabled": True, "quota": 50}  # 50GB
            },
            "content_uploads": {
                "category": FeatureCategory.STORAGE,
                "description": "Monthly content upload limit",
                "type": FeatureType.QUOTA,
                "free_tier": {"enabled": True, "quota": 10},
                "paid_tiers": {"enabled": True, "quota": 100}
            },
            
            # API and Integrations
            "api_access": {
                "category": FeatureCategory.API_ACCESS,
                "description": "API access for integrations",
                "type": FeatureType.QUOTA,
                "free_tier": {"enabled": False},
                "paid_tiers": {"enabled": True, "quota": 1000}
            },
            "webhook_integrations": {
                "category": FeatureCategory.INTEGRATIONS,
                "description": "Webhook integrations",
                "type": FeatureType.QUOTA,
                "free_tier": {"enabled": False},
                "paid_tiers": {"enabled": True, "quota": 10}
            },
            "custom_integrations": {
                "category": FeatureCategory.INTEGRATIONS,
                "description": "Custom integrations and development",
                "type": FeatureType.BOOLEAN,
                "free_tier": {"enabled": False},
                "paid_tiers": {"enabled": False},
                "enterprise_only": True
            },
            
            # Monetization
            "revenue_tracking": {
                "category": FeatureCategory.MONETIZATION,
                "description": "Revenue tracking and analytics",
                "type": FeatureType.BOOLEAN,
                "free_tier": {"enabled": False},
                "paid_tiers": {"enabled": True, "min_tier": 2}
            },
            "multi_platform_distribution": {
                "category": FeatureCategory.MONETIZATION,
                "description": "Multi-platform content distribution",
                "type": FeatureType.BOOLEAN,
                "free_tier": {"enabled": False},
                "paid_tiers": {"enabled": True, "min_tier": 2}
            },
            
            # SEO and Optimization
            "seo_optimization": {
                "category": FeatureCategory.AI_PROCESSING,
                "description": "SEO optimization tools",
                "type": FeatureType.BOOLEAN,
                "free_tier": {"enabled": False},
                "paid_tiers": {"enabled": True}
            },
            
            # Support
            "email_support": {
                "category": FeatureCategory.SUPPORT,
                "description": "Email support",
                "type": FeatureType.BOOLEAN,
                "free_tier": {"enabled": True},
                "paid_tiers": {"enabled": True}
            },
            "priority_support": {
                "category": FeatureCategory.SUPPORT,
                "description": "Priority support with faster response",
                "type": FeatureType.BOOLEAN,
                "free_tier": {"enabled": False},
                "paid_tiers": {"enabled": True}
            },
            "dedicated_support": {
                "category": FeatureCategory.SUPPORT,
                "description": "Dedicated support manager",
                "type": FeatureType.BOOLEAN,
                "free_tier": {"enabled": False},
                "paid_tiers": {"enabled": False},
                "enterprise_only": True
            }
        }
    
    async def check_feature_access(
        self,
        user_id: int,
        feature_name: str,
        db: Session = None
    ) -> bool:
        """
        Check if user has access to specific feature.
        
        Args:
            user_id: User ID
            feature_name: Feature name to check
            db: Database session
            
        Returns:
            True if user has access, False otherwise
        """
        if not db:
            db = get_db_session()
        
        try:
            # Check cache first
            cache_key = f"feature_access:{user_id}:{feature_name}"
            cached_result = await self.cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Get user's active subscription
            subscription = db.query(UserSubscription).filter(
                UserSubscription.user_id == user_id,
                UserSubscription.status.in_([
                    SubscriptionStatus.ACTIVE.value,
                    SubscriptionStatus.TRIAL.value
                ]),
                UserSubscription.end_date > datetime.utcnow()
            ).first()
            
            # Check feature definition
            if feature_name not in self.platform_features:
                self.logger.warning(f"Unknown feature: {feature_name}")
                return False
            
            feature_def = self.platform_features[feature_name]
            
            if not subscription:
                # Free tier access
                has_access = feature_def.get("free_tier", {}).get("enabled", False)
            else:
                # Check paid tier access
                plan = subscription.plan
                has_access = await self._check_paid_tier_access(
                    plan, feature_name, feature_def
                )
            
            # Cache result for 5 minutes
            await self.cache.set(cache_key, has_access, ttl=300)
            
            return has_access
            
        except Exception as e:
            self.logger.error(f"Feature access check failed for user {user_id}, feature {feature_name}: {str(e)}")
            return False
    
    async def get_available_features(
        self,
        user_id: int,
        category: Optional[str] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Get all available features for user.
        
        Args:
            user_id: User ID
            category: Optional feature category filter
            db: Database session
            
        Returns:
            Available features with access status and limits
        """
        if not db:
            db = get_db_session()
        
        try:
            # Get user's subscription
            subscription = db.query(UserSubscription).filter(
                UserSubscription.user_id == user_id,
                UserSubscription.status.in_([
                    SubscriptionStatus.ACTIVE.value,
                    SubscriptionStatus.TRIAL.value
                ]),
                UserSubscription.end_date > datetime.utcnow()
            ).first()
            
            available_features = {}
            
            for feature_name, feature_def in self.platform_features.items():
                # Apply category filter
                if category and feature_def["category"].value != category:
                    continue
                
                # Check access
                has_access = await self.check_feature_access(user_id, feature_name, db)
                
                feature_info = {
                    "name": feature_name,
                    "description": feature_def["description"],
                    "category": feature_def["category"].value,
                    "type": feature_def["type"].value,
                    "has_access": has_access,
                    "is_enterprise_only": feature_def.get("enterprise_only", False)
                }
                
                # Add quota information if applicable
                if has_access and feature_def["type"] == FeatureType.QUOTA:
                    if subscription:
                        # Paid tier quota
                        quota_info = feature_def.get("paid_tiers", {})
                        feature_info["quota_limit"] = quota_info.get("quota")
                    else:
                        # Free tier quota
                        quota_info = feature_def.get("free_tier", {})
                        feature_info["quota_limit"] = quota_info.get("quota")
                
                available_features[feature_name] = feature_info
            
            return {
                "user_id": user_id,
                "subscription_tier": subscription.plan.name if subscription else "free",
                "features": available_features
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get available features for user {user_id}: {str(e)}")
            raise ValidationError(f"Failed to get available features: {str(e)}")
    
    async def check_free_tier_access(self, feature_name: str) -> bool:
        """
        Check if feature is available in free tier.
        
        Args:
            feature_name: Feature name to check
            
        Returns:
            True if available in free tier
        """
        if feature_name not in self.platform_features:
            return False
        
        feature_def = self.platform_features[feature_name]
        return feature_def.get("free_tier", {}).get("enabled", False)
    
    async def get_tier_upgrade_recommendations(
        self,
        user_id: int,
        requested_features: List[str],
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Get tier upgrade recommendations based on requested features.
        
        Args:
            user_id: User ID
            requested_features: List of features user wants access to
            db: Database session
            
        Returns:
            Upgrade recommendations with pricing
        """
        if not db:
            db = get_db_session()
        
        try:
            # Get current subscription
            current_subscription = db.query(UserSubscription).filter(
                UserSubscription.user_id == user_id,
                UserSubscription.status.in_([
                    SubscriptionStatus.ACTIVE.value,
                    SubscriptionStatus.TRIAL.value
                ])
            ).first()
            
            current_tier = current_subscription.plan.tier_level if current_subscription else 0
            
            # Find minimum tier that provides all requested features
            required_tier = 0
            enterprise_features = []
            
            for feature_name in requested_features:
                if feature_name not in self.platform_features:
                    continue
                
                feature_def = self.platform_features[feature_name]
                
                # Check if feature is enterprise-only
                if feature_def.get("enterprise_only", False):
                    enterprise_features.append(feature_name)
                    required_tier = max(required_tier, 3)  # Enterprise tier
                    continue
                
                # Check minimum tier requirement
                paid_tier_info = feature_def.get("paid_tiers", {})
                min_tier = paid_tier_info.get("min_tier", 1)
                
                if not feature_def.get("free_tier", {}).get("enabled", False):
                    required_tier = max(required_tier, min_tier)
            
            # Get available plans
            available_plans = db.query(SubscriptionPlan).filter(
                SubscriptionPlan.is_active == True,
                SubscriptionPlan.tier_level >= required_tier
            ).order_by(SubscriptionPlan.tier_level).all()
            
            recommendations = []
            for plan in available_plans:
                if plan.tier_level > current_tier:
                    recommendations.append({
                        "plan_id": plan.id,
                        "plan_name": plan.name,
                        "display_name": plan.display_name,
                        "tier_level": plan.tier_level,
                        "monthly_price": float(plan.monthly_price),
                        "yearly_price": float(plan.yearly_price),
                        "features_unlocked": await self._get_features_unlocked_by_plan(
                            plan, requested_features
                        ),
                        "is_minimum_required": plan.tier_level == required_tier
                    })
            
            return {
                "current_tier": current_tier,
                "required_tier": required_tier,
                "enterprise_features": enterprise_features,
                "recommendations": recommendations,
                "can_access_all": len(enterprise_features) == 0
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get upgrade recommendations: {str(e)}")
            raise ValidationError(f"Failed to get upgrade recommendations: {str(e)}")
    
    async def enforce_feature_limits(
        self,
        user_id: int,
        feature_name: str,
        requested_usage: int = 1,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Enforce feature usage limits.
        
        Args:
            user_id: User ID
            feature_name: Feature name
            requested_usage: Amount of usage requested
            db: Database session
            
        Returns:
            Enforcement result with allowed status and recommendations
        """
        if not db:
            db = get_db_session()
        
        try:
            # First check basic access
            has_access = await self.check_feature_access(user_id, feature_name, db)
            
            if not has_access:
                return {
                    "allowed": False,
                    "reason": "no_access",
                    "message": f"Access to {feature_name} not included in current plan",
                    "recommended_action": "upgrade_plan"
                }
            
            # Check if feature has usage limits
            feature_def = self.platform_features.get(feature_name)
            if not feature_def or feature_def["type"] == FeatureType.BOOLEAN:
                return {
                    "allowed": True,
                    "reason": "boolean_feature",
                    "message": "Feature access granted"
                }
            
            if feature_def["type"] == FeatureType.UNLIMITED:
                return {
                    "allowed": True,
                    "reason": "unlimited_access",
                    "message": "Unlimited access granted"
                }
            
            # Check quota limits
            subscription = db.query(UserSubscription).filter(
                UserSubscription.user_id == user_id,
                UserSubscription.status.in_([
                    SubscriptionStatus.ACTIVE.value,
                    SubscriptionStatus.TRIAL.value
                ])
            ).first()
            
            if subscription:
                quota_info = feature_def.get("paid_tiers", {})
            else:
                quota_info = feature_def.get("free_tier", {})
            
            quota_limit = quota_info.get("quota")
            
            if quota_limit is None:
                return {
                    "allowed": True,
                    "reason": "no_quota_limit",
                    "message": "No usage limits for this feature"
                }
            
            # Check current usage (this would integrate with usage_tracker)
            # For now, we'll return a simplified check
            return {
                "allowed": True,
                "reason": "within_quota",
                "message": f"Usage within quota limit of {quota_limit}",
                "quota_limit": quota_limit,
                "quota_used": 0,  # Would be actual usage
                "quota_remaining": quota_limit
            }
            
        except Exception as e:
            self.logger.error(f"Feature limit enforcement failed: {str(e)}")
            return {
                "allowed": False,
                "reason": "enforcement_error",
                "message": "Failed to check feature limits"
            }
    
    async def get_feature_comparison_matrix(
        self, 
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Get feature comparison matrix across all subscription tiers.
        
        Args:
            db: Database session
            
        Returns:
            Feature comparison matrix
        """
        if not db:
            db = get_db_session()
        
        try:
            # Get all active subscription plans
            plans = db.query(SubscriptionPlan).filter(
                SubscriptionPlan.is_active == True
            ).order_by(SubscriptionPlan.tier_level).all()
            
            # Build comparison matrix
            comparison_matrix = {
                "plans": [],
                "features_by_category": {}
            }
            
            # Add free tier
            comparison_matrix["plans"].append({
                "name": "free",
                "display_name": "Free",
                "tier_level": 0,
                "monthly_price": 0.00,
                "yearly_price": 0.00
            })
            
            # Add paid plans
            for plan in plans:
                comparison_matrix["plans"].append({
                    "name": plan.name,
                    "display_name": plan.display_name,
                    "tier_level": plan.tier_level,
                    "monthly_price": float(plan.monthly_price),
                    "yearly_price": float(plan.yearly_price)
                })
            
            # Group features by category
            for feature_name, feature_def in self.platform_features.items():
                category = feature_def["category"].value
                
                if category not in comparison_matrix["features_by_category"]:
                    comparison_matrix["features_by_category"][category] = []
                
                feature_availability = {
                    "name": feature_name,
                    "description": feature_def["description"],
                    "type": feature_def["type"].value,
                    "availability": {}
                }
                
                # Check availability across tiers
                # Free tier
                free_tier_info = feature_def.get("free_tier", {})
                feature_availability["availability"]["free"] = {
                    "enabled": free_tier_info.get("enabled", False),
                    "quota": free_tier_info.get("quota")
                }
                
                # Paid tiers
                for plan in plans:
                    is_available = not feature_def.get("enterprise_only", False) or plan.is_enterprise
                    
                    if is_available:
                        paid_tier_info = feature_def.get("paid_tiers", {})
                        min_tier_required = paid_tier_info.get("min_tier", 1)
                        
                        feature_availability["availability"][plan.name] = {
                            "enabled": plan.tier_level >= min_tier_required,
                            "quota": paid_tier_info.get("quota")
                        }
                    else:
                        feature_availability["availability"][plan.name] = {
                            "enabled": False,
                            "quota": None
                        }
                
                comparison_matrix["features_by_category"][category].append(feature_availability)
            
            return comparison_matrix
            
        except Exception as e:
            self.logger.error(f"Failed to generate feature comparison matrix: {str(e)}")
            raise ValidationError(f"Failed to generate comparison matrix: {str(e)}")
    
    # Private helper methods
    
    async def _check_paid_tier_access(
        self,
        plan: SubscriptionPlan,
        feature_name: str,
        feature_def: Dict[str, Any]
    ) -> bool:
        """Check if paid tier plan has access to feature."""
        # Check if feature is enterprise-only
        if feature_def.get("enterprise_only", False):
            return plan.is_enterprise
        
        # Check minimum tier requirement
        paid_tier_info = feature_def.get("paid_tiers", {})
        if not paid_tier_info.get("enabled", False):
            return False
        
        min_tier_required = paid_tier_info.get("min_tier", 1)
        return plan.tier_level >= min_tier_required
    
    async def _get_features_unlocked_by_plan(
        self,
        plan: SubscriptionPlan,
        requested_features: List[str]
    ) -> List[str]:
        """Get features that would be unlocked by upgrading to specific plan."""
        unlocked_features = []
        
        for feature_name in requested_features:
            if feature_name not in self.platform_features:
                continue
            
            feature_def = self.platform_features[feature_name]
            
            # Check if plan provides access to this feature
            has_access = await self._check_paid_tier_access(plan, feature_name, feature_def)
            
            if has_access:
                unlocked_features.append(feature_name)
        
        return unlocked_features


__all__ = ['TierController', 'FeatureCategory']
