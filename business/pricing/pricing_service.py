"""🚀 Pricing Service - Industrial-Grade Pricing Management API
==========================================================

High-level pricing service orchestrating all pricing operations.
Provides RESTful API endpoints, business logic coordination, and integration
with ML models, payment systems, and analytics platforms.

Project Team Specialists:
- Lead Dev IA: Advanced AI architecture and ML optimization algorithms
- Backend Senior: Enterprise-grade API development and microservices
- ML Engineer: Machine learning models for pricing prediction and optimization
- DBA: High-performance database design and query optimization
- Security Expert: Enterprise security protocols and data protection
- Microservices Architect: Scalable distributed systems design
- Audio Engineer: Audio-specific pricing models and royalty calculations
- DevOps: CI/CD pipelines and production deployment automation
- IA Prompt Engineer: AI prompt optimization and natural language processing

Created by: Fahed Mlaiel <mlaiel@live.de>
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - UNAUTHORIZED USE PROHIBITED ⚠️

This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized copying, modification, distribution, or use of this code or its
underlying concepts without explicit written permission from Fahed Mlaiel is
strictly prohibited and will result in immediate legal action under German and
international copyright laws.

For licensing inquiries and authorization requests:
Email: mlaiel@live.de
All usage must be pre-approved in writing.

Business Logic Flow:
API Request → Authentication → Input Validation → Pricing Calculation → 
ML Optimization → Market Analysis → Result Caching → Response Generation
==========================================================
"""import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from pydantic import BaseModel, Field, validator

# Internal imports
from ...core.database import DatabaseManager
from ...core.security import SecurityManager
from ...core.cache import CacheManager
from ...utils.validators import ContentValidator
from ...utils.metrics import MetricsCollector
from ...utils.exceptions import BusinessLogicError, ValidationError
from .pricing_engine import PricingEngine, PricingModel, PricingMetrics, PricingStrategy, ContentType, Currency, PricingTier
from .tier_manager import TierManager, TierConfiguration
from .models import (
    PricingCalculation,
    UserSubscription,
    TierUpgrade,
    UsageRecord,
    PricingAuditLog,
    MarketIntelligence
)

logger = logging.getLogger(__name__)


class PricingRequest(BaseModel):
    """Request model for pricing calculations"""    content_id: str = Field(..., description="Content identifier")
    content_type: ContentType = Field(..., description="Type of content")
    platform: str = Field(..., description="Target platform")
    base_price: Decimal = Field(..., gt=0, description="Base price")
    currency: Currency = Field(default=Currency.EUR, description="Currency")
    pricing_strategy: PricingStrategy = Field(..., description="Pricing strategy")
    tier_level: PricingTier = Field(..., description="Creator tier")
    geographic_market: str = Field(..., description="Target market")
    target_audience: Dict[str, Any] = Field(default_factory=dict, description="Audience data")
    content_metadata: Dict[str, Any] = Field(default_factory=dict, description="Content metadata")
    
    @validator('geographic_market')
    def validate_market(cls, v):
        allowed = ['EU', 'US', 'UK', 'CA', 'AU', 'JP', 'GLOBAL']
        if v not in allowed:
            raise ValueError(f'Market must be one of {allowed}')
        return v


class PricingResponse(BaseModel):
    """Response model for pricing calculations"""    content_id: str
    calculation_id: str
    base_price: Decimal
    optimized_price: Decimal
    currency: Currency
    confidence_score: float
    predicted_conversion_rate: float
    estimated_roi: Decimal
    pricing_factors: Dict[str, Any]
    recommendations: List[str]
    expires_at: datetime


class TierRecommendationRequest(BaseModel):
    """Request model for tier recommendations"""    usage_pattern: Dict[str, Any] = Field(..., description="Historical usage data")
    content_types: List[ContentType] = Field(..., description="Content types produced")
    target_revenue: Optional[Decimal] = Field(None, description="Revenue goal")
    current_challenges: List[str] = Field(default_factory=list, description="Current limitations")


class TierRecommendationResponse(BaseModel):
    """Response model for tier recommendations"""    recommended_tier: str
    current_tier: str
    upgrade_benefits: List[str]
    cost_analysis: Dict[str, Any]
    roi_projection: Dict[str, Any]
    implementation_timeline: str


class BulkPricingRequest(BaseModel):
    """Request model for bulk pricing calculations"""    pricing_requests: List[PricingRequest] = Field(..., max_items=100)
    priority: str = Field(default="normal", description="Processing priority")
    callback_url: Optional[str] = Field(None, description="Callback URL for results")


class PricingService:
    """    Industrial-grade pricing service for content creators
    
    Features:
    - Real-time pricing optimization
    - AI-powered recommendations
    - Multi-platform support
    - Tier management
    - Usage analytics
    - Market intelligence integration
    """    
    def __init__(
        self,
        db_manager: DatabaseManager,
        security_manager: SecurityManager,
        cache_manager: CacheManager,
        pricing_engine: PricingEngine,
        tier_manager: TierManager,
        metrics_collector: MetricsCollector
    ):
        self.db_manager = db_manager
        self.security_manager = security_manager
        self.cache_manager = cache_manager
        self.pricing_engine = pricing_engine
        self.tier_manager = tier_manager
        self.metrics_collector = metrics_collector
        self.content_validator = ContentValidator()
        
    async def calculate_pricing(
        self,
        creator_id: str,
        request: PricingRequest
    ) -> PricingResponse:
        """        Calculate optimal pricing for content
        
        Args:
            creator_id: Creator identifier
            request: Pricing request parameters
            
        Returns:
            PricingResponse with optimization results
        """        try:
            # Validate creator permissions
            await self._validate_creator_access(creator_id, request.content_id)
            
            # Validate content and pricing parameters
            await self._validate_pricing_request(request)
            
            # Create pricing model
            pricing_model = PricingModel(
                content_id=request.content_id,
                creator_id=creator_id,
                content_type=request.content_type,
                platform=request.platform,
                base_price=request.base_price,
                currency=request.currency,
                pricing_strategy=request.pricing_strategy,
                tier_level=request.tier_level,
                geographic_market=request.geographic_market,
                target_audience=request.target_audience,
                content_metadata=request.content_metadata
            )
            
            # Calculate optimal pricing
            async with self.pricing_engine.pricing_session(creator_id) as session:
                pricing_metrics = await self.pricing_engine.calculate_optimal_pricing(
                    pricing_model,
                    session
                )
            
            # Store calculation in database
            calculation_id = await self._store_pricing_calculation(
                creator_id,
                pricing_model,
                pricing_metrics
            )
            
            # Generate recommendations
            recommendations = await self._generate_pricing_recommendations(
                pricing_model,
                pricing_metrics
            )
            
            # Track metrics
            await self.metrics_collector.track_pricing_request(
                creator_id,
                request.content_type.value,
                request.platform,
                pricing_metrics.confidence_score
            )
            
            # Build response
            response = PricingResponse(
                content_id=request.content_id,
                calculation_id=str(calculation_id),
                base_price=pricing_metrics.base_price,
                optimized_price=pricing_metrics.optimized_price,
                currency=request.currency,
                confidence_score=pricing_metrics.confidence_score,
                predicted_conversion_rate=pricing_metrics.predicted_conversion_rate,
                estimated_roi=pricing_metrics.roi_estimate,
                pricing_factors=self._extract_pricing_factors(pricing_metrics),
                recommendations=recommendations,
                expires_at=datetime.utcnow() + timedelta(hours=24)
            )
            
            logger.info(f"Pricing calculated for {creator_id}/{request.content_id}")
            return response
            
        except ValidationError as e:
            logger.warning(f"Pricing validation error: {e}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            logger.error(f"Pricing calculation error: {e}")
            await self.metrics_collector.track_error('pricing_calculation', str(e))
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                              detail="Internal server error during pricing calculation")
    
    async def recommend_tier(
        self,
        creator_id: str,
        request: TierRecommendationRequest
    ) -> TierRecommendationResponse:
        """        Recommend optimal tier for creator
        
        Args:
            creator_id: Creator identifier
            request: Tier recommendation parameters
            
        Returns:
            TierRecommendationResponse with recommendation
        """        try:
            # Get current tier
            current_tier_config = await self._get_current_tier(creator_id)
            
            # Get tier recommendation
            recommended_tier_config = await self.tier_manager.recommend_tier(
                creator_id,
                request.usage_pattern,
                request.content_types,
                request.target_revenue
            )
            
            # Calculate upgrade benefits and costs
            if recommended_tier_config.tier_name != current_tier_config.tier_name:
                cost_analysis = await self.tier_manager.calculate_tier_upgrade_savings(
                    creator_id,
                    recommended_tier_config.tier_name,
                    'monthly'
                )
            else:
                cost_analysis = {'message': 'Already on optimal tier'}
            
            # Generate ROI projection
            roi_projection = await self._calculate_tier_roi_projection(
                creator_id,
                current_tier_config,
                recommended_tier_config,
                request.target_revenue
            )
            
            # Generate upgrade benefits
            upgrade_benefits = self._generate_upgrade_benefits(
                current_tier_config,
                recommended_tier_config
            )
            
            # Store recommendation
            await self._store_tier_recommendation(
                creator_id,
                current_tier_config.tier_name,
                recommended_tier_config.tier_name,
                request.usage_pattern,
                cost_analysis
            )
            
            response = TierRecommendationResponse(
                recommended_tier=recommended_tier_config.tier_name.value,
                current_tier=current_tier_config.tier_name.value,
                upgrade_benefits=upgrade_benefits,
                cost_analysis=cost_analysis,
                roi_projection=roi_projection,
                implementation_timeline="Immediate upon upgrade confirmation"
            )
            
            logger.info(f"Tier recommended for {creator_id}: {recommended_tier_config.tier_name.value}")
            return response
            
        except Exception as e:
            logger.error(f"Tier recommendation error: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                              detail="Error generating tier recommendation")
    
    async def bulk_calculate_pricing(
        self,
        creator_id: str,
        request: BulkPricingRequest
    ) -> Dict[str, Any]:
        """        Calculate pricing for multiple items in bulk
        
        Args:
            creator_id: Creator identifier
            request: Bulk pricing request
            
        Returns:
            Bulk pricing results
        """        try:
            # Validate bulk request size
            if len(request.pricing_requests) > 100:
                raise ValidationError("Maximum 100 items per bulk request")
            
            # Convert to pricing models
            pricing_models = []
            for pricing_req in request.pricing_requests:
                await self._validate_creator_access(creator_id, pricing_req.content_id)
                
                pricing_model = PricingModel(
                    content_id=pricing_req.content_id,
                    creator_id=creator_id,
                    content_type=pricing_req.content_type,
                    platform=pricing_req.platform,
                    base_price=pricing_req.base_price,
                    currency=pricing_req.currency,
                    pricing_strategy=pricing_req.pricing_strategy,
                    tier_level=pricing_req.tier_level,
                    geographic_market=pricing_req.geographic_market,
                    target_audience=pricing_req.target_audience,
                    content_metadata=pricing_req.content_metadata
                )
                pricing_models.append(pricing_model)
            
            # Process bulk pricing
            results = await self.pricing_engine.bulk_price_optimization(pricing_models)
            
            # Store results
            stored_results = {}
            for content_id, metrics in results.items():
                calculation_id = await self._store_bulk_pricing_result(
                    creator_id,
                    content_id,
                    metrics
                )
                stored_results[content_id] = {
                    'calculation_id': str(calculation_id),
                    'optimized_price': float(metrics.optimized_price),
                    'confidence_score': metrics.confidence_score,
                    'estimated_roi': float(metrics.roi_estimate)
                }
            
            # Track bulk operation
            await self.metrics_collector.track_bulk_pricing_request(
                creator_id,
                len(request.pricing_requests),
                len(stored_results)
            )
            
            return {
                'total_processed': len(stored_results),
                'total_requested': len(request.pricing_requests),
                'results': stored_results,
                'processing_time': 'varies',
                'status': 'completed'
            }
            
        except Exception as e:
            logger.error(f"Bulk pricing error: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                              detail="Error processing bulk pricing request")
    
    async def get_pricing_history(
        self,
        creator_id: str,
        content_id: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get pricing calculation history"""        
        try:
            async with self.db_manager.get_session() as session:
                query = session.query(PricingCalculation).filter(
                    PricingCalculation.creator_id == creator_id
                )
                
                if content_id:
                    query = query.filter(PricingCalculation.content_id == content_id)
                
                # Date filter
                start_date = datetime.utcnow() - timedelta(days=days)
                query = query.filter(PricingCalculation.calculation_timestamp >= start_date)
                
                # Order by timestamp
                query = query.order_by(PricingCalculation.calculation_timestamp.desc())
                
                calculations = query.limit(100).all()
                
                history = []
                for calc in calculations:
                    history.append({
                        'calculation_id': str(calc.id),
                        'content_id': str(calc.content_id),
                        'content_type': calc.content_type,
                        'platform': calc.platform,
                        'base_price': float(calc.base_price),
                        'optimized_price': float(calc.optimized_price),
                        'confidence_score': float(calc.confidence_score),
                        'estimated_roi': float(calc.estimated_roi) if calc.estimated_roi else None,
                        'is_applied': calc.is_applied,
                        'timestamp': calc.calculation_timestamp.isoformat()
                    })
                
                return {
                    'total_calculations': len(history),
                    'date_range': f"{start_date.date()} to {datetime.utcnow().date()}",
                    'history': history
                }
                
        except Exception as e:
            logger.error(f"Error retrieving pricing history: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                              detail="Error retrieving pricing history")
    
    async def get_usage_analytics(
        self,
        creator_id: str,
        metric: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get usage analytics for tier management"""        
        try:
            async with self.db_manager.get_session() as session:
                # Get current subscription
                subscription = session.query(UserSubscription).filter(
                    and_(
                        UserSubscription.user_id == creator_id,
                        UserSubscription.status == 'active'
                    )
                ).first()
                
                if not subscription:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                      detail="No active subscription found")
                
                # Get usage records for current billing period
                usage_query = session.query(UsageRecord).filter(
                    and_(
                        UsageRecord.user_id == creator_id,
                        UsageRecord.billing_period_start >= subscription.current_period_start,
                        UsageRecord.billing_period_end <= subscription.current_period_end
                    )
                )
                
                if metric:
                    usage_query = usage_query.filter(UsageRecord.metric_name == metric)
                
                usage_records = usage_query.all()
                
                # Aggregate usage by metric
                usage_summary = {}
                for record in usage_records:
                    metric_name = record.metric_name
                    if metric_name not in usage_summary:
                        usage_summary[metric_name] = {
                            'total_usage': 0,
                            'record_count': 0,
                            'last_updated': None
                        }
                    
                    usage_summary[metric_name]['total_usage'] += float(record.metric_value)
                    usage_summary[metric_name]['record_count'] += 1
                    
                    if (usage_summary[metric_name]['last_updated'] is None or 
                        record.usage_date > usage_summary[metric_name]['last_updated']):
                        usage_summary[metric_name]['last_updated'] = record.usage_date.isoformat()
                
                return {
                    'subscription_id': str(subscription.id),
                    'tier': subscription.tier.tier_name,
                    'billing_period': {
                        'start': subscription.current_period_start.isoformat(),
                        'end': subscription.current_period_end.isoformat()
                    },
                    'usage_summary': usage_summary,
                    'total_metrics_tracked': len(usage_summary)
                }
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error retrieving usage analytics: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                              detail="Error retrieving usage analytics")
    
    # Private helper methods
    async def _validate_creator_access(self, creator_id: str, content_id: str):
        """Validate creator has access to content"""        # This would typically check content ownership
        # Mock implementation for now
        pass
    
    async def _validate_pricing_request(self, request: PricingRequest):
        """Validate pricing request parameters"""        
        # Validate content exists and is accessible
        if not await self.content_validator.validate_content_exists(request.content_id):
            raise ValidationError(f"Content {request.content_id} not found")
        
        # Validate platform
        supported_platforms = ['spotify', 'youtube', 'instagram', 'tiktok', 'onlyfans', 'patreon']
        if request.platform.lower() not in supported_platforms:
            raise ValidationError(f"Unsupported platform: {request.platform}")
        
        # Validate price range
        if request.base_price <= 0 or request.base_price > Decimal('10000'):
            raise ValidationError("Base price must be between 0.01 and 10000")
    
    async def _store_pricing_calculation(
        self,
        creator_id: str,
        pricing_model: PricingModel,
        metrics: PricingMetrics
    ) -> uuid.UUID:
        """Store pricing calculation in database"""        
        try:
            async with self.db_manager.get_session() as session:
                calculation = PricingCalculation(
                    content_id=pricing_model.content_id,
                    creator_id=creator_id,
                    strategy_id=None,  # Would link to strategy record
                    content_type=pricing_model.content_type.value,
                    platform=pricing_model.platform,
                    base_price=pricing_model.base_price,
                    optimized_price=metrics.optimized_price,
                    currency=pricing_model.currency.value,
                    geographic_market=pricing_model.geographic_market,
                    pricing_factors={
                        'market_demand_score': metrics.market_demand_score,
                        'competition_density': metrics.competition_density,
                        'engagement_multiplier': metrics.engagement_multiplier,
                        'geographic_adjustment': metrics.geographic_adjustment
                    },
                    market_analysis={
                        'seasonal_factor': metrics.seasonal_factor,
                        'trend_momentum': metrics.trend_momentum,
                        'price_elasticity': metrics.price_elasticity
                    },
                    confidence_score=Decimal(str(metrics.confidence_score)),
                    predicted_conversion_rate=Decimal(str(metrics.predicted_conversion_rate)),
                    estimated_roi=metrics.roi_estimate,
                    expires_at=datetime.utcnow() + timedelta(hours=24)
                )
                
                session.add(calculation)
                await session.commit()
                
                # Log audit trail
                await self._log_pricing_audit(
                    'pricing_calculation',
                    str(calculation.id),
                    creator_id,
                    'calculated',
                    {'pricing_model': pricing_model.dict(), 'metrics': metrics.__dict__}
                )
                
                return calculation.id
                
        except Exception as e:
            logger.error(f"Error storing pricing calculation: {e}")
            raise
    
    async def _generate_pricing_recommendations(
        self,
        pricing_model: PricingModel,
        metrics: PricingMetrics
    ) -> List[str]:
        """Generate pricing recommendations based on metrics"""        
        recommendations = []
        
        # Confidence-based recommendations
        if metrics.confidence_score < 0.7:
            recommendations.append("Consider gathering more market data for better pricing accuracy")
        
        # Price optimization recommendations
        price_increase_pct = ((metrics.optimized_price - pricing_model.base_price) / pricing_model.base_price) * 100
        
        if price_increase_pct > 20:
            recommendations.append(f"Significant price increase recommended (+{price_increase_pct:.1f}%)")
        elif price_increase_pct < -10:
            recommendations.append(f"Price reduction recommended ({price_increase_pct:.1f}%)")
        else:
            recommendations.append("Current pricing is well-optimized")
        
        # Market-based recommendations
        if metrics.market_demand_score > 0.8:
            recommendations.append("High market demand detected - consider premium pricing")
        elif metrics.competition_density > 0.7:
            recommendations.append("High competition - focus on differentiation or value pricing")
        
        # Engagement recommendations
        if metrics.engagement_multiplier < 1.0:
            recommendations.append("Low audience engagement - consider improving content quality")
        
        return recommendations
    
    async def _get_current_tier(self, creator_id: str) -> TierConfiguration:
        """Get creator's current tier configuration"""        
        # Mock implementation - replace with actual database query
        current_tier = await self.tier_manager._get_creator_tier(creator_id)
        return self.tier_manager.tier_configs[current_tier]
    
    async def _calculate_tier_roi_projection(
        self,
        creator_id: str,
        current_tier: TierConfiguration,
        recommended_tier: TierConfiguration,
        target_revenue: Optional[Decimal]
    ) -> Dict[str, Any]:
        """Calculate ROI projection for tier upgrade"""        
        if recommended_tier.tier_name == current_tier.tier_name:
            return {'message': 'No tier change recommended'}
        
        # Calculate monthly cost difference
        cost_difference = recommended_tier.base_monthly_price - current_tier.base_monthly_price
        
        # Estimate revenue impact (simplified)
        feature_count_diff = len(recommended_tier.features) - len(current_tier.features)
        estimated_revenue_increase = feature_count_diff * Decimal('100')  # €100 per additional feature
        
        # ROI calculation
        if cost_difference > 0:
            roi_months = int(cost_difference / max(estimated_revenue_increase, Decimal('1')))
        else:
            roi_months = 0
        
        return {
            'monthly_cost_increase': float(cost_difference),
            'estimated_monthly_revenue_increase': float(estimated_revenue_increase),
            'payback_period_months': roi_months,
            'annual_roi_percentage': float((estimated_revenue_increase * 12) / max(cost_difference * 12, Decimal('1')) * 100)
        }
    
    def _generate_upgrade_benefits(
        self,
        current_tier: TierConfiguration,
        recommended_tier: TierConfiguration
    ) -> List[str]:
        """Generate list of upgrade benefits"""        
        benefits = []
        
        # New features
        new_features = recommended_tier.features - current_tier.features
        for feature in new_features:
            benefits.append(f"Access to {feature.value.replace('_', ' ').title()}")
        
        # Limit increases
        if recommended_tier.limits.monthly_uploads > current_tier.limits.monthly_uploads:
            increase = recommended_tier.limits.monthly_uploads - current_tier.limits.monthly_uploads
            benefits.append(f"+{increase} additional monthly uploads")
        
        if recommended_tier.limits.storage_gb > current_tier.limits.storage_gb:
            increase = recommended_tier.limits.storage_gb - current_tier.limits.storage_gb
            benefits.append(f"+{increase}GB additional storage")
        
        # Support improvements
        if recommended_tier.limits.priority_support and not current_tier.limits.priority_support:
            benefits.append("Priority customer support")
        
        return benefits
    
    async def _store_tier_recommendation(
        self,
        creator_id: str,
        current_tier: PricingTier,
        recommended_tier: PricingTier,
        usage_pattern: Dict[str, Any],
        cost_analysis: Dict[str, Any]
    ):
        """Store tier recommendation in database"""        
        try:
            async with self.db_manager.get_session() as session:
                recommendation = TierUpgrade(
                    user_id=creator_id,
                    current_tier_id=None,  # Would link to tier record
                    target_tier_id=None,   # Would link to tier record
                    recommendation_reason=f"Upgrade to {recommended_tier.value} based on usage analysis",
                    usage_analysis=usage_pattern,
                    financial_impact=cost_analysis,
                    confidence_score=Decimal('0.85')  # Mock confidence
                )
                
                session.add(recommendation)
                await session.commit()
                
        except Exception as e:
            logger.error(f"Error storing tier recommendation: {e}")
            
    async def _store_bulk_pricing_result(
        self,
        creator_id: str,
        content_id: str,
        metrics: PricingMetrics
    ) -> uuid.UUID:
        """Store bulk pricing result"""        
        # Simplified version of _store_pricing_calculation for bulk operations
        return uuid.uuid4()  # Mock implementation
    
    async def _log_pricing_audit(
        self,
        entity_type: str,
        entity_id: str,
        user_id: str,
        action: str,
        data: Dict[str, Any]
    ):
        """Log pricing audit trail"""        
        try:
            async with self.db_manager.get_session() as session:
                audit_log = PricingAuditLog(
                    entity_type=entity_type,
                    entity_id=entity_id,
                    user_id=user_id,
                    action=action,
                    new_values=data,
                    automated=True
                )
                
                session.add(audit_log)
                await session.commit()
                
        except Exception as e:
            logger.warning(f"Audit logging failed: {e}")
    
    def _extract_pricing_factors(self, metrics: PricingMetrics) -> Dict[str, Any]:
        """Extract pricing factors for response"""        
        return {
            'market_demand_score': metrics.market_demand_score,
            'competition_density': metrics.competition_density,
            'audience_willingness_to_pay': metrics.audience_willingness_to_pay,
            'engagement_multiplier': metrics.engagement_multiplier,
            'geographic_adjustment': metrics.geographic_adjustment,
            'platform_commission_rate': metrics.platform_commission_rate,
            'seasonal_factor': metrics.seasonal_factor,
            'trend_momentum': metrics.trend_momentum,
            'confidence_score': metrics.confidence_score
        }
