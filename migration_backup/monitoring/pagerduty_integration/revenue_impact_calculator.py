"""
Revenue Impact Calculator for IA Chéries Platform
Real-time financial impact assessment for Creator Economy incidents

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL:
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

import logging
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from decimal import Decimal, ROUND_HALF_UP
import statistics
import math

logger = logging.getLogger(__name__)


class RevenueStreamType(Enum):
    """Types of revenue streams in Creator Economy"""
    CONTENT_MONETIZATION = "content_monetization"
    SUBSCRIPTION_REVENUE = "subscription_revenue"
    BRAND_PARTNERSHIPS = "brand_partnerships"
    COMMISSION_SALES = "commission_sales"
    PREMIUM_FEATURES = "premium_features"
    ADVERTISING_REVENUE = "advertising_revenue"
    LICENSING_DEALS = "licensing_deals"
    MERCHANDISE_SALES = "merchandise_sales"
    LIVE_STREAMING = "live_streaming"
    EDUCATIONAL_CONTENT = "educational_content"


class ImpactSeverity(Enum):
    """Revenue impact severity levels"""
    CATASTROPHIC = "catastrophic"  # >$50K/hour
    CRITICAL = "critical"          # $10K-$50K/hour
    HIGH = "high"                  # $1K-$10K/hour
    MEDIUM = "medium"              # $100-$1K/hour
    LOW = "low"                    # <$100/hour


@dataclass
class RevenueStream:
    """Individual revenue stream configuration"""
    stream_id: str
    stream_type: RevenueStreamType
    base_hourly_rate: Decimal
    peak_multiplier: float
    off_peak_multiplier: float
    seasonal_adjustment: float
    dependency_services: List[str]
    creator_tier_multipliers: Dict[str, float]
    geographical_multipliers: Dict[str, float]
    
    def calculate_current_rate(self, 
                             timestamp: datetime,
                             creator_tier: str = "standard",
                             geo_region: str = "global") -> Decimal:
        """Calculate current hourly rate with all multipliers"""
        base_rate = self.base_hourly_rate
        
        # Apply time-based multipliers
        hour = timestamp.hour
        is_peak = 9 <= hour <= 17  # Business hours
        time_multiplier = self.peak_multiplier if is_peak else self.off_peak_multiplier
        
        # Apply tier multiplier
        tier_multiplier = self.creator_tier_multipliers.get(creator_tier, 1.0)
        
        # Apply geographical multiplier
        geo_multiplier = self.geographical_multipliers.get(geo_region, 1.0)
        
        # Calculate final rate
        final_rate = base_rate * Decimal(str(time_multiplier)) * \
                    Decimal(str(tier_multiplier)) * \
                    Decimal(str(geo_multiplier)) * \
                    Decimal(str(self.seasonal_adjustment))
        
        return final_rate.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


@dataclass
class CreatorMetrics:
    """Creator-specific metrics for impact calculation"""
    creator_id: str
    tier: str  # premium, pro, standard, basic
    monthly_revenue: Decimal
    daily_active_sessions: int
    average_session_value: Decimal
    content_upload_frequency: int
    collaboration_count: int
    audience_size: int
    engagement_rate: float
    geo_region: str
    primary_revenue_streams: List[str]


@dataclass
class ServiceDependency:
    """Service dependency configuration for impact calculation"""
    service_name: str
    dependent_streams: List[str]
    impact_percentage: float  # 0.0 to 1.0
    recovery_time_minutes: int
    cascading_services: List[str]
    business_criticality: float  # 0.0 to 1.0


@dataclass
class IncidentImpactResult:
    """Comprehensive incident impact assessment"""
    incident_id: str
    total_hourly_impact: Decimal
    total_daily_impact: Decimal
    projected_weekly_impact: Decimal
    affected_creators_count: int
    affected_revenue_streams: List[str]
    impact_severity: ImpactSeverity
    impact_breakdown: Dict[str, Decimal]
    recovery_cost_estimate: Decimal
    lost_opportunity_cost: Decimal
    brand_reputation_impact: float
    creator_churn_risk: float
    calculation_timestamp: datetime
    confidence_level: float
    mitigation_recommendations: List[str]


class RevenueImpactCalculator:
    """
    Advanced revenue impact calculator for Creator Economy incidents
    Provides real-time financial impact assessment and predictions
    """
    
    def __init__(self):
        """Initialize the revenue impact calculator"""
        self.revenue_streams = self._initialize_revenue_streams()
        self.service_dependencies = self._initialize_service_dependencies()
        self.creator_tiers = self._initialize_creator_tiers()
        self.historical_data = {}
        self.cached_metrics = {}
        
        logger.info("Revenue Impact Calculator initialized")
    
    def _initialize_revenue_streams(self) -> Dict[str, RevenueStream]:
        """Initialize default revenue stream configurations"""
        streams = {}
        
        # Content Monetization Stream
        streams["content_monetization"] = RevenueStream(
            stream_id="content_monetization",
            stream_type=RevenueStreamType.CONTENT_MONETIZATION,
            base_hourly_rate=Decimal("1250.00"),  # $1.25K/hour average
            peak_multiplier=1.5,
            off_peak_multiplier=0.7,
            seasonal_adjustment=1.0,
            dependency_services=["content-upload", "ai-processing", "storage"],
            creator_tier_multipliers={
                "premium": 3.0,
                "pro": 2.0,
                "standard": 1.0,
                "basic": 0.3
            },
            geographical_multipliers={
                "north_america": 1.2,
                "europe": 1.1,
                "asia_pacific": 0.9,
                "global": 1.0
            }
        )
        
        # Brand Partnerships Stream
        streams["brand_partnerships"] = RevenueStream(
            stream_id="brand_partnerships",
            stream_type=RevenueStreamType.BRAND_PARTNERSHIPS,
            base_hourly_rate=Decimal("2500.00"),  # $2.5K/hour average
            peak_multiplier=2.0,
            off_peak_multiplier=0.5,
            seasonal_adjustment=1.0,
            dependency_services=["collaboration", "matching", "communication"],
            creator_tier_multipliers={
                "premium": 5.0,
                "pro": 2.5,
                "standard": 1.0,
                "basic": 0.1
            },
            geographical_multipliers={
                "north_america": 1.3,
                "europe": 1.2,
                "asia_pacific": 0.8,
                "global": 1.0
            }
        )
        
        # Subscription Revenue Stream
        streams["subscription_revenue"] = RevenueStream(
            stream_id="subscription_revenue",
            stream_type=RevenueStreamType.SUBSCRIPTION_REVENUE,
            base_hourly_rate=Decimal("800.00"),  # $800/hour average
            peak_multiplier=1.2,
            off_peak_multiplier=0.9,
            seasonal_adjustment=1.0,
            dependency_services=["payment", "authentication", "user-management"],
            creator_tier_multipliers={
                "premium": 4.0,
                "pro": 2.0,
                "standard": 1.0,
                "basic": 0.2
            },
            geographical_multipliers={
                "north_america": 1.4,
                "europe": 1.2,
                "asia_pacific": 0.7,
                "global": 1.0
            }
        )
        
        # Commission Sales Stream
        streams["commission_sales"] = RevenueStream(
            stream_id="commission_sales",
            stream_type=RevenueStreamType.COMMISSION_SALES,
            base_hourly_rate=Decimal("600.00"),  # $600/hour average
            peak_multiplier=1.8,
            off_peak_multiplier=0.6,
            seasonal_adjustment=1.0,
            dependency_services=["e-commerce", "payment", "analytics"],
            creator_tier_multipliers={
                "premium": 3.0,
                "pro": 1.8,
                "standard": 1.0,
                "basic": 0.4
            },
            geographical_multipliers={
                "north_america": 1.3,
                "europe": 1.1,
                "asia_pacific": 0.8,
                "global": 1.0
            }
        )
        
        # Premium Features Stream
        streams["premium_features"] = RevenueStream(
            stream_id="premium_features",
            stream_type=RevenueStreamType.PREMIUM_FEATURES,
            base_hourly_rate=Decimal("300.00"),  # $300/hour average
            peak_multiplier=1.3,
            off_peak_multiplier=0.8,
            seasonal_adjustment=1.0,
            dependency_services=["ai-processing", "premium-api", "analytics"],
            creator_tier_multipliers={
                "premium": 2.0,
                "pro": 1.5,
                "standard": 1.0,
                "basic": 0.5
            },
            geographical_multipliers={
                "north_america": 1.2,
                "europe": 1.1,
                "asia_pacific": 0.9,
                "global": 1.0
            }
        )
        
        return streams
    
    def _initialize_service_dependencies(self) -> Dict[str, ServiceDependency]:
        """Initialize service dependency configurations"""
        dependencies = {}
        
        dependencies["payment"] = ServiceDependency(
            service_name="payment",
            dependent_streams=["subscription_revenue", "commission_sales", "brand_partnerships"],
            impact_percentage=0.95,  # 95% impact when payment is down
            recovery_time_minutes=15,
            cascading_services=["billing", "user-accounts"],
            business_criticality=0.98
        )
        
        dependencies["content-upload"] = ServiceDependency(
            service_name="content-upload",
            dependent_streams=["content_monetization", "brand_partnerships"],
            impact_percentage=0.80,
            recovery_time_minutes=30,
            cascading_services=["ai-processing", "storage"],
            business_criticality=0.85
        )
        
        dependencies["ai-processing"] = ServiceDependency(
            service_name="ai-processing",
            dependent_streams=["content_monetization", "premium_features"],
            impact_percentage=0.70,
            recovery_time_minutes=45,
            cascading_services=["ml-pipeline", "gpu-cluster"],
            business_criticality=0.75
        )
        
        dependencies["collaboration"] = ServiceDependency(
            service_name="collaboration",
            dependent_streams=["brand_partnerships"],
            impact_percentage=0.90,
            recovery_time_minutes=20,
            cascading_services=["matching", "communication"],
            business_criticality=0.80
        )
        
        dependencies["authentication"] = ServiceDependency(
            service_name="authentication",
            dependent_streams=["subscription_revenue", "content_monetization", "premium_features"],
            impact_percentage=0.85,
            recovery_time_minutes=10,
            cascading_services=["user-management", "session-management"],
            business_criticality=0.95
        )
        
        return dependencies
    
    def _initialize_creator_tiers(self) -> Dict[str, Dict[str, Any]]:
        """Initialize creator tier configurations"""
        return {
            "premium": {
                "min_monthly_revenue": Decimal("50000.00"),
                "audience_threshold": 1000000,
                "revenue_multiplier": 3.0,
                "impact_weight": 0.4  # 40% of total platform impact
            },
            "pro": {
                "min_monthly_revenue": Decimal("10000.00"),
                "audience_threshold": 100000,
                "revenue_multiplier": 2.0,
                "impact_weight": 0.35  # 35% of total platform impact
            },
            "standard": {
                "min_monthly_revenue": Decimal("1000.00"),
                "audience_threshold": 10000,
                "revenue_multiplier": 1.0,
                "impact_weight": 0.20  # 20% of total platform impact
            },
            "basic": {
                "min_monthly_revenue": Decimal("0.00"),
                "audience_threshold": 0,
                "revenue_multiplier": 0.3,
                "impact_weight": 0.05  # 5% of total platform impact
            }
        }
    
    def calculate_incident_impact(self,
                                incident_id: str,
                                affected_services: List[str],
                                affected_creators: List[CreatorMetrics],
                                incident_start_time: datetime,
                                estimated_duration_hours: float = 1.0) -> IncidentImpactResult:
        """
        Calculate comprehensive revenue impact for an incident
        
        Args:
            incident_id: Unique incident identifier
            affected_services: List of affected service names
            affected_creators: List of affected creator metrics
            incident_start_time: When the incident started
            estimated_duration_hours: Estimated incident duration
            
        Returns:
            IncidentImpactResult with detailed impact analysis
        """
        try:
            logger.info(f"Calculating impact for incident {incident_id}")
            
            # Calculate hourly impact by revenue stream
            impact_breakdown = {}
            affected_streams = set()
            
            for service in affected_services:
                if service in self.service_dependencies:
                    dependency = self.service_dependencies[service]
                    
                    for stream_id in dependency.dependent_streams:
                        if stream_id in self.revenue_streams:
                            stream = self.revenue_streams[stream_id]
                            affected_streams.add(stream_id)
                            
                            # Calculate impact for this stream
                            stream_impact = self._calculate_stream_impact(
                                stream, dependency, affected_creators, incident_start_time
                            )
                            
                            if stream_id in impact_breakdown:
                                impact_breakdown[stream_id] += stream_impact
                            else:
                                impact_breakdown[stream_id] = stream_impact
            
            # Calculate total impacts
            total_hourly_impact = sum(impact_breakdown.values())
            total_daily_impact = total_hourly_impact * Decimal("24")
            projected_weekly_impact = total_daily_impact * Decimal("7")
            
            # Calculate recovery and opportunity costs
            recovery_cost = self._calculate_recovery_cost(affected_services, estimated_duration_hours)
            opportunity_cost = self._calculate_opportunity_cost(total_hourly_impact, estimated_duration_hours)
            
            # Assess brand and churn risks
            brand_impact = self._assess_brand_reputation_impact(affected_creators, total_hourly_impact)
            churn_risk = self._assess_creator_churn_risk(affected_creators, estimated_duration_hours)
            
            # Determine impact severity
            impact_severity = self._determine_impact_severity(total_hourly_impact)
            
            # Generate mitigation recommendations
            recommendations = self._generate_mitigation_recommendations(
                affected_services, impact_severity, estimated_duration_hours
            )
            
            # Calculate confidence level
            confidence = self._calculate_confidence_level(affected_creators, affected_services)
            
            result = IncidentImpactResult(
                incident_id=incident_id,
                total_hourly_impact=total_hourly_impact,
                total_daily_impact=total_daily_impact,
                projected_weekly_impact=projected_weekly_impact,
                affected_creators_count=len(affected_creators),
                affected_revenue_streams=list(affected_streams),
                impact_severity=impact_severity,
                impact_breakdown=impact_breakdown,
                recovery_cost_estimate=recovery_cost,
                lost_opportunity_cost=opportunity_cost,
                brand_reputation_impact=brand_impact,
                creator_churn_risk=churn_risk,
                calculation_timestamp=datetime.utcnow(),
                confidence_level=confidence,
                mitigation_recommendations=recommendations
            )
            
            logger.info(f"Impact calculation complete: ${total_hourly_impact}/hour ({impact_severity.value})")
            return result
            
        except Exception as e:
            logger.error(f"Failed to calculate impact for incident {incident_id}: {e}")
            raise
    
    def _calculate_stream_impact(self,
                               stream: RevenueStream,
                               dependency: ServiceDependency,
                               affected_creators: List[CreatorMetrics],
                               timestamp: datetime) -> Decimal:
        """Calculate impact for a specific revenue stream"""
        total_impact = Decimal("0.00")
        
        for creator in affected_creators:
            # Check if creator uses this revenue stream
            if stream.stream_id in creator.primary_revenue_streams:
                # Get current rate for this creator
                current_rate = stream.calculate_current_rate(
                    timestamp, creator.tier, creator.geo_region
                )
                
                # Apply dependency impact percentage
                stream_impact = current_rate * Decimal(str(dependency.impact_percentage))
                
                # Apply creator-specific adjustments
                creator_adjustment = self._get_creator_adjustment(creator, stream.stream_id)
                final_impact = stream_impact * creator_adjustment
                
                total_impact += final_impact
        
        return total_impact
    
    def _get_creator_adjustment(self, creator: CreatorMetrics, stream_id: str) -> Decimal:
        """Get creator-specific adjustment factor"""
        base_adjustment = Decimal("1.0")
        
        # Adjust based on creator activity level
        if creator.daily_active_sessions > 100:
            base_adjustment *= Decimal("1.2")
        elif creator.daily_active_sessions > 50:
            base_adjustment *= Decimal("1.1")
        elif creator.daily_active_sessions < 5:
            base_adjustment *= Decimal("0.3")
        
        # Adjust based on engagement rate
        if creator.engagement_rate > 0.15:  # 15%+
            base_adjustment *= Decimal("1.15")
        elif creator.engagement_rate > 0.10:  # 10%+
            base_adjustment *= Decimal("1.05")
        elif creator.engagement_rate < 0.02:  # <2%
            base_adjustment *= Decimal("0.5")
        
        # Adjust based on audience size
        if creator.audience_size > 1000000:
            base_adjustment *= Decimal("1.3")
        elif creator.audience_size > 100000:
            base_adjustment *= Decimal("1.1")
        elif creator.audience_size < 1000:
            base_adjustment *= Decimal("0.4")
        
        return base_adjustment
    
    def _calculate_recovery_cost(self, affected_services: List[str], duration_hours: float) -> Decimal:
        """Calculate estimated recovery cost"""
        base_recovery_cost = Decimal("5000.00")  # Base $5K for incident response
        
        # Additional costs per service
        service_costs = {
            "payment": Decimal("20000.00"),
            "authentication": Decimal("15000.00"),
            "content-upload": Decimal("10000.00"),
            "ai-processing": Decimal("12000.00"),
            "collaboration": Decimal("8000.00")
        }
        
        total_cost = base_recovery_cost
        
        for service in affected_services:
            if service in service_costs:
                total_cost += service_costs[service]
        
        # Duration multiplier
        duration_multiplier = Decimal(str(min(duration_hours, 24.0)))  # Cap at 24 hours
        total_cost *= duration_multiplier
        
        return total_cost
    
    def _calculate_opportunity_cost(self, hourly_impact: Decimal, duration_hours: float) -> Decimal:
        """Calculate lost opportunity cost"""
        # Opportunity cost is 150% of direct revenue impact
        opportunity_multiplier = Decimal("1.5")
        duration = Decimal(str(duration_hours))
        
        return hourly_impact * duration * opportunity_multiplier
    
    def _assess_brand_reputation_impact(self, affected_creators: List[CreatorMetrics], 
                                      hourly_impact: Decimal) -> float:
        """Assess brand reputation impact (0.0 to 1.0)"""
        impact_score = 0.0
        
        # Impact based on affected premium creators
        premium_creators = [c for c in affected_creators if c.tier == "premium"]
        if premium_creators:
            impact_score += min(len(premium_creators) * 0.1, 0.4)
        
        # Impact based on financial magnitude
        if hourly_impact > Decimal("10000.00"):
            impact_score += 0.3
        elif hourly_impact > Decimal("5000.00"):
            impact_score += 0.2
        elif hourly_impact > Decimal("1000.00"):
            impact_score += 0.1
        
        # Impact based on total affected creators
        if len(affected_creators) > 1000:
            impact_score += 0.3
        elif len(affected_creators) > 100:
            impact_score += 0.2
        elif len(affected_creators) > 10:
            impact_score += 0.1
        
        return min(impact_score, 1.0)
    
    def _assess_creator_churn_risk(self, affected_creators: List[CreatorMetrics], 
                                 duration_hours: float) -> float:
        """Assess creator churn risk (0.0 to 1.0)"""
        churn_risk = 0.0
        
        # Base risk increases with duration
        if duration_hours > 24:
            churn_risk += 0.4
        elif duration_hours > 8:
            churn_risk += 0.3
        elif duration_hours > 2:
            churn_risk += 0.2
        elif duration_hours > 0.5:
            churn_risk += 0.1
        
        # Higher risk for premium creators
        premium_creators = [c for c in affected_creators if c.tier in ["premium", "pro"]]
        if premium_creators:
            churn_risk += min(len(premium_creators) * 0.05, 0.3)
        
        # Risk based on revenue dependency
        high_revenue_creators = [c for c in affected_creators 
                               if c.monthly_revenue > Decimal("10000.00")]
        if high_revenue_creators:
            churn_risk += min(len(high_revenue_creators) * 0.02, 0.3)
        
        return min(churn_risk, 1.0)
    
    def _determine_impact_severity(self, hourly_impact: Decimal) -> ImpactSeverity:
        """Determine impact severity based on hourly revenue loss"""
        if hourly_impact >= Decimal("50000.00"):
            return ImpactSeverity.CATASTROPHIC
        elif hourly_impact >= Decimal("10000.00"):
            return ImpactSeverity.CRITICAL
        elif hourly_impact >= Decimal("1000.00"):
            return ImpactSeverity.HIGH
        elif hourly_impact >= Decimal("100.00"):
            return ImpactSeverity.MEDIUM
        else:
            return ImpactSeverity.LOW
    
    def _generate_mitigation_recommendations(self,
                                           affected_services: List[str],
                                           severity: ImpactSeverity,
                                           duration_hours: float) -> List[str]:
        """Generate mitigation recommendations"""
        recommendations = []
        
        # Service-specific recommendations
        service_recommendations = {
            "payment": [
                "Switch to backup payment processor",
                "Enable manual payment reconciliation",
                "Communicate with affected creators about payment delays"
            ],
            "authentication": [
                "Activate emergency authentication bypass",
                "Enable backup authentication service",
                "Implement temporary API key access"
            ],
            "content-upload": [
                "Enable alternative upload endpoints",
                "Increase storage redundancy",
                "Communicate upload alternatives to creators"
            ],
            "ai-processing": [
                "Switch to backup AI infrastructure",
                "Enable manual content approval",
                "Scale up GPU resources"
            ],
            "collaboration": [
                "Enable offline collaboration tools",
                "Notify brand partners of delays",
                "Implement manual matching process"
            ]
        }
        
        for service in affected_services:
            if service in service_recommendations:
                recommendations.extend(service_recommendations[service])
        
        # Severity-based recommendations
        if severity in [ImpactSeverity.CATASTROPHIC, ImpactSeverity.CRITICAL]:
            recommendations.extend([
                "Activate incident command center",
                "Notify C-level executives immediately",
                "Prepare public communication",
                "Consider legal/regulatory notifications"
            ])
        
        if severity in [ImpactSeverity.CRITICAL, ImpactSeverity.HIGH]:
            recommendations.extend([
                "Implement temporary creator compensation",
                "Activate PR crisis management",
                "Scale incident response team"
            ])
        
        # Duration-based recommendations
        if duration_hours > 4:
            recommendations.append("Prepare creator retention offers")
        
        if duration_hours > 8:
            recommendations.append("Activate business continuity plan")
        
        return list(set(recommendations))  # Remove duplicates
    
    def _calculate_confidence_level(self, affected_creators: List[CreatorMetrics],
                                  affected_services: List[str]) -> float:
        """Calculate confidence level of impact assessment"""
        confidence = 0.5  # Base confidence
        
        # Higher confidence with more data points
        if len(affected_creators) > 100:
            confidence += 0.2
        elif len(affected_creators) > 50:
            confidence += 0.15
        elif len(affected_creators) > 10:
            confidence += 0.1
        
        # Higher confidence for well-known services
        known_services = ["payment", "authentication", "content-upload", "ai-processing"]
        known_affected = [s for s in affected_services if s in known_services]
        confidence += min(len(known_affected) * 0.1, 0.3)
        
        return min(confidence, 0.95)  # Cap at 95%
    
    def update_revenue_stream(self, stream_id: str, stream_config: RevenueStream) -> bool:
        """Update revenue stream configuration"""
        try:
            self.revenue_streams[stream_id] = stream_config
            logger.info(f"Updated revenue stream: {stream_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update revenue stream {stream_id}: {e}")
            return False
    
    def get_historical_impact_trends(self, days: int = 30) -> Dict[str, Any]:
        """Get historical impact trends for analysis"""
        # TODO: Implement historical data analysis
        return {
            "average_daily_impact": "0.00",
            "peak_impact_day": None,
            "most_affected_services": [],
            "creator_tier_impact_distribution": {},
            "revenue_stream_reliability": {}
        }
    
    def export_impact_report(self, result: IncidentImpactResult) -> Dict[str, Any]:
        """Export detailed impact report"""
        return {
            "incident_summary": {
                "incident_id": result.incident_id,
                "total_hourly_impact": str(result.total_hourly_impact),
                "impact_severity": result.impact_severity.value,
                "affected_creators": result.affected_creators_count,
                "calculation_time": result.calculation_timestamp.isoformat()
            },
            "financial_impact": {
                "hourly_loss": str(result.total_hourly_impact),
                "daily_projection": str(result.total_daily_impact),
                "weekly_projection": str(result.projected_weekly_impact),
                "recovery_cost": str(result.recovery_cost_estimate),
                "opportunity_cost": str(result.lost_opportunity_cost)
            },
            "revenue_breakdown": {
                stream: str(amount) for stream, amount in result.impact_breakdown.items()
            },
            "risk_assessment": {
                "brand_reputation_impact": result.brand_reputation_impact,
                "creator_churn_risk": result.creator_churn_risk,
                "confidence_level": result.confidence_level
            },
            "recommendations": result.mitigation_recommendations,
            "affected_streams": result.affected_revenue_streams
        }


# Factory function
def create_revenue_impact_calculator() -> RevenueImpactCalculator:
    """Create new revenue impact calculator instance"""
    return RevenueImpactCalculator()


# Export all classes and functions
__all__ = [
    'RevenueImpactCalculator',
    'RevenueStreamType',
    'ImpactSeverity',
    'RevenueStream',
    'CreatorMetrics',
    'ServiceDependency',
    'IncidentImpactResult',
    'create_revenue_impact_calculator'
]