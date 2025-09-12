"""MLOps Revenue Impact Analyzer - Advanced Revenue Attribution for ML Optimizations
Analyseur d'impact revenus des optimisations ML avec attribution précise.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

🎯 Business Logic Integration:
ML Optimization → Revenue Tracking → Attribution Analysis → Creator Segment Impact → Revenue Growth

🚀 Multi-Expert Implementation:
- ML Engineer: Model performance correlation with revenue metrics
- Backend Senior: High-performance revenue data processing
- DBA: Revenue data lineage and aggregation optimization
- Business Analyst: Revenue attribution models and KPI tracking
"""

import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
import statistics
from pathlib import Path
import aiofiles

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RevenueSource(Enum):
    """Sources de revenus pour attribution."""
    SUBSCRIPTION_REVENUE = "subscription_revenue"
    CONTENT_MONETIZATION = "content_monetization"
    PREMIUM_FEATURES = "premium_features"
    COLLABORATION_FEES = "collaboration_fees"
    ADVERTISEMENT_REVENUE = "advertisement_revenue"
    COMMISSION_REVENUE = "commission_revenue"
    LICENSING_REVENUE = "licensing_revenue"
    MERCHANDISE_REVENUE = "merchandise_revenue"

class OptimizationType(Enum):
    """Types d'optimisations ML trackées."""
    RECOMMENDATION_ENGINE = "recommendation_engine"
    CONTENT_DISCOVERY = "content_discovery"
    PERSONALIZATION = "personalization"
    SEARCH_OPTIMIZATION = "search_optimization"
    ENGAGEMENT_BOOST = "engagement_boost"
    CONVERSION_OPTIMIZATION = "conversion_optimization"
    RETENTION_IMPROVEMENT = "retention_improvement"
    PRICING_OPTIMIZATION = "pricing_optimization"

@dataclass
class RevenueMetric:
    """Métrique de revenus pour analyse."""
    metric_id: str
    creator_segment: str
    revenue_source: RevenueSource
    amount_usd: float
    period_start: datetime
    period_end: datetime
    optimization_type: Optional[OptimizationType] = None
    ml_model_id: Optional[str] = None
    attribution_confidence: float = 1.0

@dataclass
class OptimizationImpact:
    """Impact d'une optimisation ML sur les revenus."""
    optimization_id: str
    optimization_type: OptimizationType
    creator_segments_affected: List[str]
    start_date: datetime
    baseline_revenue: float
    current_revenue: float
    revenue_lift_usd: float
    revenue_lift_percentage: float
    attribution_confidence: float
    statistical_significance: float
    affected_users_count: int

@dataclass
class CreatorSegmentAnalysis:
    """Analyse de revenus par segment de créateur."""
    segment_name: str
    total_revenue_usd: float
    revenue_growth_percentage: float
    ml_attributed_revenue: float
    ml_attribution_percentage: float
    top_revenue_sources: List[Tuple[RevenueSource, float]]
    optimization_impacts: List[OptimizationImpact]
    average_revenue_per_user: float
    user_count: int

class RevenueImpactAnalyzer:
    """Analyseur enterprise d'impact revenus pour optimisations ML."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize revenue impact analyzer."""
        self.config = self._load_config(config_path)
        self.revenue_metrics: List[RevenueMetric] = []
        self.optimization_impacts: List[OptimizationImpact] = []
        
        # Creator segment revenue models
        self.segment_revenue_models = {
            "musicians": {
                "base_arpu": 15.0,
                "engagement_multiplier": 1.2,
                "subscription_rate": 0.25,
                "monetization_efficiency": 0.18
            },
            "photographers": {
                "base_arpu": 45.0,
                "engagement_multiplier": 1.1,
                "subscription_rate": 0.35,
                "monetization_efficiency": 0.28
            },
            "bloggers": {
                "base_arpu": 8.0,
                "engagement_multiplier": 1.0,
                "subscription_rate": 0.15,
                "monetization_efficiency": 0.12
            },
            "influencers": {
                "base_arpu": 25.0,
                "engagement_multiplier": 1.4,
                "subscription_rate": 0.30,
                "monetization_efficiency": 0.22
            },
            "comedians": {
                "base_arpu": 12.0,
                "engagement_multiplier": 1.1,
                "subscription_rate": 0.20,
                "monetization_efficiency": 0.15
            }
        }
        
        # Optimization impact baselines
        self.optimization_baselines = {
            OptimizationType.RECOMMENDATION_ENGINE: {"avg_lift": 0.15, "confidence": 0.85},
            OptimizationType.CONTENT_DISCOVERY: {"avg_lift": 0.12, "confidence": 0.80},
            OptimizationType.PERSONALIZATION: {"avg_lift": 0.20, "confidence": 0.90},
            OptimizationType.SEARCH_OPTIMIZATION: {"avg_lift": 0.08, "confidence": 0.75},
            OptimizationType.ENGAGEMENT_BOOST: {"avg_lift": 0.18, "confidence": 0.88},
            OptimizationType.CONVERSION_OPTIMIZATION: {"avg_lift": 0.25, "confidence": 0.92},
            OptimizationType.RETENTION_IMPROVEMENT: {"avg_lift": 0.30, "confidence": 0.95},
            OptimizationType.PRICING_OPTIMIZATION: {"avg_lift": 0.10, "confidence": 0.70}
        }
        
        logger.info("💰 RevenueImpactAnalyzer enterprise initialized with ML attribution")

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load revenue analyzer configuration."""
        default_config = {
            "analysis_settings": {
                "attribution_window_days": 30,
                "minimum_confidence_threshold": 0.70,
                "statistical_significance_threshold": 0.95,
                "baseline_comparison_period_days": 90
            },
            "revenue_tracking": {
                "real_time_tracking": True,
                "batch_processing_interval_hours": 4,
                "data_retention_days": 365
            },
            "ml_attribution": {
                "enable_advanced_attribution": True,
                "multi_touch_attribution": True,
                "decay_rate": 0.8,
                "control_group_percentage": 0.10
            }
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                return {**default_config, **config}
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")
        
        return default_config

    async def track_revenue_metric(self,
                                 creator_segment: str,
                                 revenue_source: RevenueSource,
                                 amount_usd: float,
                                 optimization_type: Optional[OptimizationType] = None,
                                 ml_model_id: Optional[str] = None,
                                 attribution_confidence: float = 1.0) -> str:
        """Tracker une métrique de revenus avec attribution ML."""
        try:
            metric_id = f"rev_{int(time.time())}_{creator_segment[:3]}"
            
            metric = RevenueMetric(
                metric_id=metric_id,
                creator_segment=creator_segment,
                revenue_source=revenue_source,
                amount_usd=amount_usd,
                period_start=datetime.now() - timedelta(hours=1),
                period_end=datetime.now(),
                optimization_type=optimization_type,
                ml_model_id=ml_model_id,
                attribution_confidence=attribution_confidence
            )
            
            self.revenue_metrics.append(metric)
            
            logger.info(f"💰 Tracked revenue: ${amount_usd:.2f} from {revenue_source.value} "
                       f"for {creator_segment} (confidence: {attribution_confidence:.2f})")
            
            return metric_id
            
        except Exception as e:
            logger.error(f"❌ Error tracking revenue metric: {e}")
            return ""

    async def analyze_optimization_impact(self,
                                        optimization_type: OptimizationType,
                                        creator_segments: List[str],
                                        analysis_period_days: int = 30) -> OptimizationImpact:
        """Analyser l'impact d'une optimisation ML sur les revenus."""
        try:
            optimization_id = f"opt_{int(time.time())}_{optimization_type.value[:4]}"
            
            # Calculate baseline and current revenue
            end_date = datetime.now()
            start_date = end_date - timedelta(days=analysis_period_days)
            baseline_start = start_date - timedelta(days=analysis_period_days)
            
            # Get baseline revenue (before optimization)
            baseline_revenue = await self._calculate_baseline_revenue(
                creator_segments, baseline_start, start_date, optimization_type
            )
            
            # Get current revenue (after optimization)
            current_revenue = await self._calculate_current_revenue(
                creator_segments, start_date, end_date, optimization_type
            )
            
            # Calculate impact
            revenue_lift_usd = current_revenue - baseline_revenue
            revenue_lift_percentage = (revenue_lift_usd / baseline_revenue * 100) if baseline_revenue > 0 else 0
            
            # Attribution confidence based on optimization type and data quality
            baseline_confidence = self.optimization_baselines.get(optimization_type, {}).get("confidence", 0.80)
            
            # Adjust confidence based on data quality and segment coverage
            data_quality_factor = min(1.0, len(creator_segments) / 3)  # Better confidence with more segments
            attribution_confidence = baseline_confidence * data_quality_factor
            
            # Statistical significance (simplified calculation)
            statistical_significance = await self._calculate_statistical_significance(
                baseline_revenue, current_revenue, analysis_period_days
            )
            
            # Estimate affected users
            affected_users = await self._estimate_affected_users(creator_segments, optimization_type)
            
            impact = OptimizationImpact(
                optimization_id=optimization_id,
                optimization_type=optimization_type,
                creator_segments_affected=creator_segments,
                start_date=start_date,
                baseline_revenue=baseline_revenue,
                current_revenue=current_revenue,
                revenue_lift_usd=revenue_lift_usd,
                revenue_lift_percentage=revenue_lift_percentage,
                attribution_confidence=attribution_confidence,
                statistical_significance=statistical_significance,
                affected_users_count=affected_users
            )
            
            self.optimization_impacts.append(impact)
            
            logger.info(f"📊 Optimization impact: {optimization_type.value} generated "
                       f"${revenue_lift_usd:,.2f} lift ({revenue_lift_percentage:+.1f}%) "
                       f"with {attribution_confidence:.1%} confidence")
            
            return impact
            
        except Exception as e:
            logger.error(f"❌ Error analyzing optimization impact: {e}")
            return OptimizationImpact(
                optimization_id="",
                optimization_type=optimization_type,
                creator_segments_affected=creator_segments,
                start_date=datetime.now(),
                baseline_revenue=0.0,
                current_revenue=0.0,
                revenue_lift_usd=0.0,
                revenue_lift_percentage=0.0,
                attribution_confidence=0.0,
                statistical_significance=0.0,
                affected_users_count=0
            )

    async def _calculate_baseline_revenue(self,
                                        creator_segments: List[str],
                                        start_date: datetime,
                                        end_date: datetime,
                                        optimization_type: OptimizationType) -> float:
        """Calculer les revenus de baseline avant optimisation."""
        
        baseline_revenue = 0.0
        
        for segment in creator_segments:
            # Get segment revenue model
            model = self.segment_revenue_models.get(segment, self.segment_revenue_models["bloggers"])
            
            # Estimate baseline users and ARPU
            estimated_users = await self._estimate_segment_users(segment)
            base_arpu = model["base_arpu"]
            
            # Calculate time period factor
            days = (end_date - start_date).days
            period_factor = days / 30  # Normalize to monthly
            
            # Calculate baseline revenue for segment
            segment_baseline = estimated_users * base_arpu * period_factor
            
            # Apply optimization type specific baseline adjustment
            optimization_factor = self.optimization_baselines.get(optimization_type, {}).get("avg_lift", 0.15)
            # Baseline assumes no optimization, so we reduce by expected lift
            segment_baseline = segment_baseline / (1 + optimization_factor)
            
            baseline_revenue += segment_baseline
        
        return baseline_revenue

    async def _calculate_current_revenue(self,
                                       creator_segments: List[str],
                                       start_date: datetime,
                                       end_date: datetime,
                                       optimization_type: OptimizationType) -> float:
        """Calculer les revenus actuels après optimisation."""
        
        current_revenue = 0.0
        
        # Get actual revenue metrics in the period
        period_metrics = [
            m for m in self.revenue_metrics
            if (m.period_start >= start_date and m.period_end <= end_date and
                m.creator_segment in creator_segments and
                (m.optimization_type == optimization_type or m.optimization_type is None))
        ]
        
        if period_metrics:
            # Use actual tracked revenue
            current_revenue = sum(m.amount_usd for m in period_metrics)
        else:
            # Estimate current revenue based on models
            for segment in creator_segments:
                model = self.segment_revenue_models.get(segment, self.segment_revenue_models["bloggers"])
                
                estimated_users = await self._estimate_segment_users(segment)
                base_arpu = model["base_arpu"]
                
                days = (end_date - start_date).days
                period_factor = days / 30
                
                # Apply optimization lift
                optimization_lift = self.optimization_baselines.get(optimization_type, {}).get("avg_lift", 0.15)
                enhanced_arpu = base_arpu * (1 + optimization_lift)
                
                segment_revenue = estimated_users * enhanced_arpu * period_factor
                current_revenue += segment_revenue
        
        return current_revenue

    async def _estimate_segment_users(self, segment: str) -> int:
        """Estimer le nombre d'utilisateurs pour un segment."""
        # Simulate user counts based on segment
        base_users = {
            "musicians": 5000,
            "photographers": 3000,
            "bloggers": 8000,
            "influencers": 4000,
            "comedians": 2000
        }
        
        # Add some variability
        base = base_users.get(segment, 1000)
        return int(base * (0.8 + np.random.random() * 0.4))  # ±20% variance

    async def _calculate_statistical_significance(self,
                                                baseline_revenue: float,
                                                current_revenue: float,
                                                period_days: int) -> float:
        """Calculer la signification statistique de l'impact."""
        
        # Simplified statistical significance calculation
        # In production, this would use proper statistical tests
        
        if baseline_revenue <= 0:
            return 0.0
        
        # Revenue lift magnitude
        lift_magnitude = abs(current_revenue - baseline_revenue) / baseline_revenue
        
        # Period stability factor
        period_factor = min(1.0, period_days / 30)  # More days = higher confidence
        
        # Sample size factor (simplified)
        sample_factor = min(1.0, baseline_revenue / 10000)  # Higher revenue = more samples
        
        significance = lift_magnitude * period_factor * sample_factor
        
        return min(0.99, max(0.50, significance))

    async def _estimate_affected_users(self,
                                     creator_segments: List[str],
                                     optimization_type: OptimizationType) -> int:
        """Estimer le nombre d'utilisateurs affectés par l'optimisation."""
        
        total_users = 0
        
        for segment in creator_segments:
            segment_users = await self._estimate_segment_users(segment)
            
            # Apply optimization reach factor
            reach_factors = {
                OptimizationType.RECOMMENDATION_ENGINE: 0.80,
                OptimizationType.CONTENT_DISCOVERY: 0.90,
                OptimizationType.PERSONALIZATION: 0.95,
                OptimizationType.SEARCH_OPTIMIZATION: 0.70,
                OptimizationType.ENGAGEMENT_BOOST: 0.85,
                OptimizationType.CONVERSION_OPTIMIZATION: 0.60,
                OptimizationType.RETENTION_IMPROVEMENT: 0.75,
                OptimizationType.PRICING_OPTIMIZATION: 0.50
            }
            
            reach_factor = reach_factors.get(optimization_type, 0.70)
            affected_users = int(segment_users * reach_factor)
            total_users += affected_users
        
        return total_users

    async def analyze_creator_segment_revenue(self, segment_name: str) -> CreatorSegmentAnalysis:
        """Analyser les revenus détaillés pour un segment de créateur."""
        try:
            # Get all revenue metrics for this segment
            segment_metrics = [m for m in self.revenue_metrics if m.creator_segment == segment_name]
            
            if not segment_metrics:
                # Create baseline analysis
                return await self._create_baseline_segment_analysis(segment_name)
            
            # Calculate total revenue
            total_revenue = sum(m.amount_usd for m in segment_metrics)
            
            # Calculate ML attributed revenue
            ml_metrics = [m for m in segment_metrics if m.optimization_type is not None]
            ml_attributed_revenue = sum(m.amount_usd * m.attribution_confidence for m in ml_metrics)
            ml_attribution_percentage = (ml_attributed_revenue / total_revenue * 100) if total_revenue > 0 else 0
            
            # Revenue by source
            revenue_by_source = {}
            for metric in segment_metrics:
                if metric.revenue_source not in revenue_by_source:
                    revenue_by_source[metric.revenue_source] = 0
                revenue_by_source[metric.revenue_source] += metric.amount_usd
            
            top_revenue_sources = sorted(
                revenue_by_source.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            # Get optimization impacts for this segment
            segment_impacts = [
                impact for impact in self.optimization_impacts
                if segment_name in impact.creator_segments_affected
            ]
            
            # Calculate growth (simplified - compare with baseline)
            baseline_model = self.segment_revenue_models.get(segment_name, self.segment_revenue_models["bloggers"])
            estimated_users = await self._estimate_segment_users(segment_name)
            baseline_monthly_revenue = estimated_users * baseline_model["base_arpu"]
            
            # Annualize current revenue (assuming metrics are recent)
            current_monthly_revenue = total_revenue  # Simplified assumption
            revenue_growth = ((current_monthly_revenue - baseline_monthly_revenue) / baseline_monthly_revenue * 100) if baseline_monthly_revenue > 0 else 0
            
            # Average revenue per user
            arpu = current_monthly_revenue / estimated_users if estimated_users > 0 else 0
            
            analysis = CreatorSegmentAnalysis(
                segment_name=segment_name,
                total_revenue_usd=total_revenue,
                revenue_growth_percentage=revenue_growth,
                ml_attributed_revenue=ml_attributed_revenue,
                ml_attribution_percentage=ml_attribution_percentage,
                top_revenue_sources=top_revenue_sources,
                optimization_impacts=segment_impacts,
                average_revenue_per_user=arpu,
                user_count=estimated_users
            )
            
            logger.info(f"📊 {segment_name} analysis: ${total_revenue:,.2f} total revenue, "
                       f"{ml_attribution_percentage:.1f}% ML attributed, {revenue_growth:+.1f}% growth")
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error analyzing segment {segment_name}: {e}")
            return await self._create_baseline_segment_analysis(segment_name)

    async def _create_baseline_segment_analysis(self, segment_name: str) -> CreatorSegmentAnalysis:
        """Créer une analyse baseline pour un segment sans données."""
        
        model = self.segment_revenue_models.get(segment_name, self.segment_revenue_models["bloggers"])
        estimated_users = await self._estimate_segment_users(segment_name)
        baseline_revenue = estimated_users * model["base_arpu"]
        
        return CreatorSegmentAnalysis(
            segment_name=segment_name,
            total_revenue_usd=baseline_revenue,
            revenue_growth_percentage=0.0,
            ml_attributed_revenue=0.0,
            ml_attribution_percentage=0.0,
            top_revenue_sources=[(RevenueSource.SUBSCRIPTION_REVENUE, baseline_revenue * 0.6)],
            optimization_impacts=[],
            average_revenue_per_user=model["base_arpu"],
            user_count=estimated_users
        )

    async def generate_comprehensive_revenue_report(self) -> Dict[str, Any]:
        """Générer un rapport complet d'impact revenus."""
        try:
            # Overall metrics
            total_revenue = sum(m.amount_usd for m in self.revenue_metrics)
            ml_attributed = sum(m.amount_usd * m.attribution_confidence 
                              for m in self.revenue_metrics if m.optimization_type)
            
            # Analysis by creator segment
            segment_analyses = {}
            for segment in ["musicians", "photographers", "bloggers", "influencers", "comedians"]:
                segment_analyses[segment] = asdict(await self.analyze_creator_segment_revenue(segment))
            
            # Optimization performance
            optimization_performance = {}
            for opt_type in OptimizationType:
                type_impacts = [i for i in self.optimization_impacts if i.optimization_type == opt_type]
                if type_impacts:
                    avg_lift = statistics.mean([i.revenue_lift_percentage for i in type_impacts])
                    total_impact = sum([i.revenue_lift_usd for i in type_impacts])
                    avg_confidence = statistics.mean([i.attribution_confidence for i in type_impacts])
                    
                    optimization_performance[opt_type.value] = {
                        "average_lift_percentage": avg_lift,
                        "total_impact_usd": total_impact,
                        "average_confidence": avg_confidence,
                        "implementations_count": len(type_impacts)
                    }
            
            # Revenue source distribution
            revenue_by_source = {}
            for metric in self.revenue_metrics:
                source = metric.revenue_source.value
                if source not in revenue_by_source:
                    revenue_by_source[source] = 0
                revenue_by_source[source] += metric.amount_usd
            
            # Top performing optimizations
            top_optimizations = sorted(
                self.optimization_impacts,
                key=lambda x: x.revenue_lift_usd,
                reverse=True
            )[:5]
            
            report = {
                "report_summary": {
                    "total_revenue_tracked_usd": round(total_revenue, 2),
                    "ml_attributed_revenue_usd": round(ml_attributed, 2),
                    "ml_attribution_percentage": round((ml_attributed / total_revenue * 100) if total_revenue > 0 else 0, 1),
                    "total_optimizations_analyzed": len(self.optimization_impacts),
                    "revenue_metrics_tracked": len(self.revenue_metrics)
                },
                "creator_segment_analysis": segment_analyses,
                "optimization_performance": optimization_performance,
                "revenue_source_distribution": revenue_by_source,
                "top_performing_optimizations": [
                    {
                        "optimization_type": opt.optimization_type.value,
                        "revenue_lift_usd": round(opt.revenue_lift_usd, 2),
                        "revenue_lift_percentage": round(opt.revenue_lift_percentage, 1),
                        "attribution_confidence": round(opt.attribution_confidence, 2),
                        "affected_segments": opt.creator_segments_affected
                    } for opt in top_optimizations
                ],
                "insights_and_recommendations": await self._generate_insights()
            }
            
            logger.info(f"📊 Revenue report generated: ${total_revenue:,.2f} total revenue, "
                       f"{len(self.optimization_impacts)} optimizations analyzed")
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Error generating revenue report: {e}")
            return {"error": str(e)}

    async def _generate_insights(self) -> List[str]:
        """Générer des insights et recommandations."""
        insights = []
        
        if not self.optimization_impacts:
            insights.append("No optimization impacts tracked yet. Begin implementing ML optimizations to measure revenue impact.")
            return insights
        
        # Best performing optimization type
        if self.optimization_impacts:
            best_opt = max(self.optimization_impacts, key=lambda x: x.revenue_lift_percentage)
            insights.append(f"Best performing optimization: {best_opt.optimization_type.value} "
                          f"with {best_opt.revenue_lift_percentage:.1f}% revenue lift")
        
        # Segment with highest ML attribution
        segment_ml_impact = {}
        for metric in self.revenue_metrics:
            if metric.optimization_type:
                segment = metric.creator_segment
                if segment not in segment_ml_impact:
                    segment_ml_impact[segment] = 0
                segment_ml_impact[segment] += metric.amount_usd * metric.attribution_confidence
        
        if segment_ml_impact:
            top_segment = max(segment_ml_impact.items(), key=lambda x: x[1])
            insights.append(f"Creator segment with highest ML revenue impact: {top_segment[0]} "
                          f"(${top_segment[1]:,.2f} attributed revenue)")
        
        # Revenue concentration analysis
        if len(self.revenue_metrics) > 10:
            top_80_percent = len(self.revenue_metrics) * 0.8
            insights.append(f"Revenue tracking maturity: {len(self.revenue_metrics)} metrics tracked, "
                          f"suggesting good data coverage for attribution analysis")
        
        return insights

    async def export_revenue_analysis(self, format_type: str = "json") -> str:
        """Exporter l'analyse de revenus complète."""
        try:
            report = await self.generate_comprehensive_revenue_report()
            
            # Add metadata
            export_data = {
                "export_metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "export_type": "ml_revenue_impact_analysis",
                    "analysis_period": "last_30_days",
                    "attribution_confidence_threshold": self.config["analysis_settings"]["minimum_confidence_threshold"]
                },
                "revenue_analysis": report
            }
            
            # Export to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"/tmp/revenue_impact_analysis_{timestamp}.{format_type}"
            
            async with aiofiles.open(filename, 'w') as f:
                await f.write(json.dumps(export_data, indent=2, default=str))
            
            logger.info(f"📊 Revenue analysis exported to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"❌ Error exporting revenue analysis: {e}")
            return ""

# Example usage and testing
async def main():
    """Example usage of revenue impact analyzer."""
    print("💰 MLOps Revenue Impact Analyzer - Enterprise Demo")
    print("="*60)
    
    # Create analyzer
    analyzer = RevenueImpactAnalyzer()
    
    # Track some revenue metrics
    print("\n📊 Tracking revenue metrics...")
    
    # Musicians revenue from AI-optimized recommendations
    await analyzer.track_revenue_metric(
        creator_segment="musicians",
        revenue_source=RevenueSource.SUBSCRIPTION_REVENUE,
        amount_usd=2500.0,
        optimization_type=OptimizationType.RECOMMENDATION_ENGINE,
        attribution_confidence=0.85
    )
    
    # Photographers premium features revenue
    await analyzer.track_revenue_metric(
        creator_segment="photographers", 
        revenue_source=RevenueSource.PREMIUM_FEATURES,
        amount_usd=1800.0,
        optimization_type=OptimizationType.PERSONALIZATION,
        attribution_confidence=0.90
    )
    
    # Influencers collaboration revenue
    await analyzer.track_revenue_metric(
        creator_segment="influencers",
        revenue_source=RevenueSource.COLLABORATION_FEES,
        amount_usd=3200.0,
        optimization_type=OptimizationType.ENGAGEMENT_BOOST,
        attribution_confidence=0.88
    )
    
    print(f"   Tracked {len(analyzer.revenue_metrics)} revenue metrics")
    
    # Analyze optimization impacts
    print(f"\n🎯 Analyzing optimization impacts...")
    
    # Recommendation engine impact
    rec_impact = await analyzer.analyze_optimization_impact(
        optimization_type=OptimizationType.RECOMMENDATION_ENGINE,
        creator_segments=["musicians", "influencers"],
        analysis_period_days=30
    )
    
    print(f"   Recommendation engine: {rec_impact.revenue_lift_percentage:+.1f}% lift, "
          f"${rec_impact.revenue_lift_usd:,.2f} impact")
    
    # Personalization impact  
    pers_impact = await analyzer.analyze_optimization_impact(
        optimization_type=OptimizationType.PERSONALIZATION,
        creator_segments=["photographers", "bloggers"],
        analysis_period_days=30
    )
    
    print(f"   Personalization: {pers_impact.revenue_lift_percentage:+.1f}% lift, "
          f"${pers_impact.revenue_lift_usd:,.2f} impact")
    
    # Creator segment analysis
    print(f"\n👥 Analyzing creator segments...")
    
    for segment in ["musicians", "photographers", "influencers"]:
        analysis = await analyzer.analyze_creator_segment_revenue(segment)
        print(f"   {segment}: ${analysis.total_revenue_usd:,.2f} revenue, "
              f"{analysis.ml_attribution_percentage:.1f}% ML attributed, "
              f"${analysis.average_revenue_per_user:.2f} ARPU")
    
    # Generate comprehensive report
    print(f"\n📊 Generating comprehensive revenue report...")
    report = await analyzer.generate_comprehensive_revenue_report()
    
    summary = report["report_summary"]
    print(f"   Total revenue tracked: ${summary['total_revenue_tracked_usd']:,.2f}")
    print(f"   ML attributed revenue: ${summary['ml_attributed_revenue_usd']:,.2f}")
    print(f"   ML attribution percentage: {summary['ml_attribution_percentage']:.1f}%")
    print(f"   Optimizations analyzed: {summary['total_optimizations_analyzed']}")
    
    # Show insights
    if report.get("insights_and_recommendations"):
        print(f"\n💡 Key insights:")
        for insight in report["insights_and_recommendations"]:
            print(f"   • {insight}")
    
    # Export analysis
    print(f"\n📊 Exporting revenue analysis...")
    export_file = await analyzer.export_revenue_analysis()
    print(f"   Analysis exported to: {export_file}")
    
    print(f"\n✅ Revenue impact analysis complete!")

if __name__ == "__main__":
    asyncio.run(main())