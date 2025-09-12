"""
Ainflue Platform - Partnership Performance Analyzer
===================================================

Advanced partnership performance analysis system for measuring collaboration
success, ROI tracking, and performance optimization with ML-powered insights
for the Ainflue platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import statistics
from collections import defaultdict, deque
import json
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.cluster import KMeans

logger = logging.getLogger(__name__)

class PerformanceMetric(Enum):
    """Partnership performance metrics."""
    ENGAGEMENT_GROWTH = "engagement_growth"
    AUDIENCE_EXPANSION = "audience_expansion"
    CONTENT_QUALITY = "content_quality"
    REVENUE_GENERATION = "revenue_generation"
    BRAND_AWARENESS = "brand_awareness"
    CREATIVE_INNOVATION = "creative_innovation"
    PRODUCTION_EFFICIENCY = "production_efficiency"
    CROSS_PROMOTION_SUCCESS = "cross_promotion_success"
    COLLABORATION_SATISFACTION = "collaboration_satisfaction"
    LONG_TERM_RELATIONSHIP = "long_term_relationship"
    MARKET_PENETRATION = "market_penetration"
    VIRAL_POTENTIAL = "viral_potential"

class PerformancePhase(Enum):
    """Partnership performance phases."""
    PLANNING = "planning"
    LAUNCH = "launch"
    ACTIVE_COLLABORATION = "active_collaboration"
    PROMOTION = "promotion"
    EVALUATION = "evaluation"
    FOLLOW_UP = "follow_up"

class PerformanceCategory(Enum):
    """Performance categories."""
    EXCEPTIONAL = "exceptional"      # 90-100%
    EXCELLENT = "excellent"          # 80-89%
    GOOD = "good"                   # 70-79%
    AVERAGE = "average"             # 60-69%
    BELOW_AVERAGE = "below_average"  # 40-59%
    POOR = "poor"                   # 0-39%

@dataclass
class PerformanceSnapshot:
    """Performance snapshot at a specific time."""
    partnership_id: str
    timestamp: datetime
    phase: PerformancePhase
    metrics: Dict[PerformanceMetric, float]
    kpis: Dict[str, float]
    external_factors: Dict[str, Any]
    context: Dict[str, Any]
    notes: str = ""

@dataclass
class PerformanceInsight:
    """Performance insight and recommendation."""
    insight_type: str
    title: str
    description: str
    impact_level: str  # high, medium, low
    actionable_recommendations: List[str]
    confidence_score: float
    supporting_data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class PartnershipAnalysis:
    """Comprehensive partnership analysis."""
    partnership_id: str
    creator_a_id: str
    creator_b_id: str
    analysis_period: Tuple[datetime, datetime]
    overall_performance_score: float
    category: PerformanceCategory
    phase_performances: Dict[PerformancePhase, float]
    metric_scores: Dict[PerformanceMetric, float]
    roi_analysis: Dict[str, float]
    success_factors: List[str]
    improvement_areas: List[str]
    insights: List[PerformanceInsight]
    future_potential: float
    risk_assessment: Dict[str, float]
    recommendations: List[str]
    benchmark_comparison: Dict[str, float]
    timestamp: datetime = field(default_factory=datetime.now)

class PartnershipPerformanceAnalyzer:
    """
    Advanced partnership performance analyzer for collaboration monitoring.
    
    Features:
    - Real-time performance tracking
    - Multi-phase analysis
    - ROI calculation and optimization
    - Predictive performance modeling
    - Benchmark comparison
    - Success factor identification
    - Risk assessment
    - Actionable insights generation
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.performance_snapshots: Dict[str, List[PerformanceSnapshot]] = defaultdict(list)
        self.partnership_analyses: Dict[str, PartnershipAnalysis] = {}
        self.performance_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.benchmarks: Dict[str, float] = {}
        self.ml_models: Dict[str, Any] = {}
        self.success_patterns: Dict[str, Any] = {}
        
        # Initialize ML models
        self._initialize_ml_models()
        
        # Initialize benchmarks
        self._initialize_benchmarks()
        
        # Performance tracking
        self.tracking_metrics = {
            'total_partnerships_analyzed': 0,
            'average_analysis_time': 0.0,
            'prediction_accuracy': 0.0,
            'insights_generated': 0,
            'successful_partnerships': 0,
            'failed_partnerships': 0
        }
        
        logger.info("PartnershipPerformanceAnalyzer initialized")

    def _initialize_ml_models(self):
        """Initialize ML models for performance prediction."""
        try:
            self.ml_models = {
                'performance_predictor': RandomForestRegressor(n_estimators=100, random_state=42),
                'success_classifier': RandomForestRegressor(n_estimators=100, random_state=42),
                'roi_predictor': RandomForestRegressor(n_estimators=100, random_state=42),
                'risk_assessor': RandomForestRegressor(n_estimators=100, random_state=42)
            }
            logger.info("ML models initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing ML models: {e}")

    def _initialize_benchmarks(self):
        """Initialize industry benchmarks."""
        self.benchmarks = {
            'engagement_growth': 0.15,
            'audience_expansion': 0.10,
            'content_quality': 0.75,
            'revenue_generation': 0.20,
            'brand_awareness': 0.12,
            'creative_innovation': 0.60,
            'production_efficiency': 0.70,
            'cross_promotion_success': 0.25,
            'collaboration_satisfaction': 0.80,
            'long_term_relationship': 0.35,
            'market_penetration': 0.08,
            'viral_potential': 0.05
        }

    async def record_performance_snapshot(
        self,
        partnership_id: str,
        phase: PerformancePhase,
        metrics_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> PerformanceSnapshot:
        """Record a performance snapshot."""
        try:
            # Extract and normalize metrics
            metrics = self._extract_performance_metrics(metrics_data)
            
            # Calculate KPIs
            kpis = self._calculate_kpis(metrics_data, metrics)
            
            # Extract external factors
            external_factors = self._extract_external_factors(metrics_data, context)
            
            snapshot = PerformanceSnapshot(
                partnership_id=partnership_id,
                timestamp=datetime.now(),
                phase=phase,
                metrics=metrics,
                kpis=kpis,
                external_factors=external_factors,
                context=context or {},
                notes=context.get('notes', '') if context else ''
            )
            
            # Store snapshot
            self.performance_snapshots[partnership_id].append(snapshot)
            
            # Update performance history
            self.performance_history[partnership_id].append({
                'timestamp': snapshot.timestamp,
                'phase': phase,
                'overall_score': np.mean(list(metrics.values())),
                'kpis': kpis
            })
            
            logger.info(f"Recorded performance snapshot for partnership {partnership_id} in {phase.value} phase")
            return snapshot
            
        except Exception as e:
            logger.error(f"Error recording performance snapshot: {e}")
            raise

    def _extract_performance_metrics(self, data: Dict[str, Any]) -> Dict[PerformanceMetric, float]:
        """Extract performance metrics from data."""
        metrics = {}
        
        try:
            # Engagement growth
            metrics[PerformanceMetric.ENGAGEMENT_GROWTH] = self._calculate_engagement_growth(data)
            
            # Audience expansion
            metrics[PerformanceMetric.AUDIENCE_EXPANSION] = self._calculate_audience_expansion(data)
            
            # Content quality
            metrics[PerformanceMetric.CONTENT_QUALITY] = self._calculate_content_quality(data)
            
            # Revenue generation
            metrics[PerformanceMetric.REVENUE_GENERATION] = self._calculate_revenue_generation(data)
            
            # Brand awareness
            metrics[PerformanceMetric.BRAND_AWARENESS] = self._calculate_brand_awareness(data)
            
            # Creative innovation
            metrics[PerformanceMetric.CREATIVE_INNOVATION] = self._calculate_creative_innovation(data)
            
            # Production efficiency
            metrics[PerformanceMetric.PRODUCTION_EFFICIENCY] = self._calculate_production_efficiency(data)
            
            # Cross-promotion success
            metrics[PerformanceMetric.CROSS_PROMOTION_SUCCESS] = self._calculate_cross_promotion_success(data)
            
            # Collaboration satisfaction
            metrics[PerformanceMetric.COLLABORATION_SATISFACTION] = self._calculate_collaboration_satisfaction(data)
            
            # Long-term relationship potential
            metrics[PerformanceMetric.LONG_TERM_RELATIONSHIP] = self._calculate_long_term_potential(data)
            
            # Market penetration
            metrics[PerformanceMetric.MARKET_PENETRATION] = self._calculate_market_penetration(data)
            
            # Viral potential
            metrics[PerformanceMetric.VIRAL_POTENTIAL] = self._calculate_viral_potential(data)
            
        except Exception as e:
            logger.error(f"Error extracting performance metrics: {e}")
            # Set default values
            for metric in PerformanceMetric:
                if metric not in metrics:
                    metrics[metric] = 0.0
        
        return metrics

    def _calculate_engagement_growth(self, data: Dict[str, Any]) -> float:
        """Calculate engagement growth metric."""
        try:
            current_engagement = data.get('current_engagement', {})
            baseline_engagement = data.get('baseline_engagement', {})
            
            current_total = sum([
                current_engagement.get('likes', 0),
                current_engagement.get('comments', 0),
                current_engagement.get('shares', 0),
                current_engagement.get('saves', 0)
            ])
            
            baseline_total = sum([
                baseline_engagement.get('likes', 0),
                baseline_engagement.get('comments', 0),
                baseline_engagement.get('shares', 0),
                baseline_engagement.get('saves', 0)
            ])
            
            if baseline_total == 0:
                return 0.0
            
            growth_rate = (current_total - baseline_total) / baseline_total
            return max(0.0, min(1.0, growth_rate))
            
        except Exception as e:
            logger.error(f"Error calculating engagement growth: {e}")
            return 0.0

    def _calculate_audience_expansion(self, data: Dict[str, Any]) -> float:
        """Calculate audience expansion metric."""
        try:
            audience_data = data.get('audience_metrics', {})
            
            new_followers = audience_data.get('new_followers', 0)
            cross_pollination = audience_data.get('cross_pollination_rate', 0.0)
            reach_expansion = audience_data.get('reach_expansion', 0.0)
            
            # Normalize and combine metrics
            normalized_followers = min(new_followers / 1000, 1.0)  # Normalize to 1000 followers
            
            expansion_score = (
                0.4 * normalized_followers +
                0.3 * cross_pollination +
                0.3 * reach_expansion
            )
            
            return max(0.0, min(1.0, expansion_score))
            
        except Exception as e:
            logger.error(f"Error calculating audience expansion: {e}")
            return 0.0

    def _calculate_content_quality(self, data: Dict[str, Any]) -> float:
        """Calculate content quality metric."""
        try:
            quality_data = data.get('content_quality', {})
            
            production_quality = quality_data.get('production_quality', 0.5)
            creativity_score = quality_data.get('creativity_score', 0.5)
            technical_execution = quality_data.get('technical_execution', 0.5)
            audience_feedback = quality_data.get('audience_feedback', 0.5)
            
            quality_score = (
                0.3 * production_quality +
                0.25 * creativity_score +
                0.25 * technical_execution +
                0.2 * audience_feedback
            )
            
            return max(0.0, min(1.0, quality_score))
            
        except Exception as e:
            logger.error(f"Error calculating content quality: {e}")
            return 0.5

    def _calculate_revenue_generation(self, data: Dict[str, Any]) -> float:
        """Calculate revenue generation metric."""
        try:
            revenue_data = data.get('revenue_metrics', {})
            
            direct_revenue = revenue_data.get('direct_revenue', 0.0)
            indirect_revenue = revenue_data.get('indirect_revenue', 0.0)
            projected_revenue = revenue_data.get('projected_revenue', 0.0)
            
            total_revenue = direct_revenue + indirect_revenue
            roi = revenue_data.get('roi', 0.0)
            
            # Normalize revenue based on partnership investment
            investment = revenue_data.get('investment', 1.0)
            normalized_revenue = total_revenue / investment if investment > 0 else 0.0
            
            revenue_score = min(normalized_revenue / 2.0, 1.0)  # Cap at 200% ROI = 1.0 score
            
            return max(0.0, min(1.0, revenue_score))
            
        except Exception as e:
            logger.error(f"Error calculating revenue generation: {e}")
            return 0.0

    def _calculate_brand_awareness(self, data: Dict[str, Any]) -> float:
        """Calculate brand awareness metric."""
        try:
            brand_data = data.get('brand_metrics', {})
            
            mention_increase = brand_data.get('mention_increase', 0.0)
            sentiment_improvement = brand_data.get('sentiment_improvement', 0.0)
            share_of_voice = brand_data.get('share_of_voice', 0.0)
            brand_recall = brand_data.get('brand_recall', 0.0)
            
            awareness_score = (
                0.3 * mention_increase +
                0.25 * sentiment_improvement +
                0.25 * share_of_voice +
                0.2 * brand_recall
            )
            
            return max(0.0, min(1.0, awareness_score))
            
        except Exception as e:
            logger.error(f"Error calculating brand awareness: {e}")
            return 0.0

    def _calculate_creative_innovation(self, data: Dict[str, Any]) -> float:
        """Calculate creative innovation metric."""
        try:
            innovation_data = data.get('innovation_metrics', {})
            
            novelty_score = innovation_data.get('novelty_score', 0.5)
            creative_risk_taking = innovation_data.get('creative_risk_taking', 0.5)
            format_innovation = innovation_data.get('format_innovation', 0.5)
            artistic_growth = innovation_data.get('artistic_growth', 0.5)
            
            innovation_score = (
                0.3 * novelty_score +
                0.25 * creative_risk_taking +
                0.25 * format_innovation +
                0.2 * artistic_growth
            )
            
            return max(0.0, min(1.0, innovation_score))
            
        except Exception as e:
            logger.error(f"Error calculating creative innovation: {e}")
            return 0.5

    def _calculate_production_efficiency(self, data: Dict[str, Any]) -> float:
        """Calculate production efficiency metric."""
        try:
            efficiency_data = data.get('production_metrics', {})
            
            time_efficiency = efficiency_data.get('time_efficiency', 0.5)
            resource_utilization = efficiency_data.get('resource_utilization', 0.5)
            workflow_optimization = efficiency_data.get('workflow_optimization', 0.5)
            deadline_adherence = efficiency_data.get('deadline_adherence', 0.5)
            
            efficiency_score = (
                0.3 * time_efficiency +
                0.25 * resource_utilization +
                0.25 * workflow_optimization +
                0.2 * deadline_adherence
            )
            
            return max(0.0, min(1.0, efficiency_score))
            
        except Exception as e:
            logger.error(f"Error calculating production efficiency: {e}")
            return 0.5

    def _calculate_cross_promotion_success(self, data: Dict[str, Any]) -> float:
        """Calculate cross-promotion success metric."""
        try:
            promo_data = data.get('cross_promotion', {})
            
            audience_transfer = promo_data.get('audience_transfer_rate', 0.0)
            engagement_lift = promo_data.get('engagement_lift', 0.0)
            reach_amplification = promo_data.get('reach_amplification', 0.0)
            conversion_rate = promo_data.get('conversion_rate', 0.0)
            
            promo_score = (
                0.3 * audience_transfer +
                0.25 * engagement_lift +
                0.25 * reach_amplification +
                0.2 * conversion_rate
            )
            
            return max(0.0, min(1.0, promo_score))
            
        except Exception as e:
            logger.error(f"Error calculating cross-promotion success: {e}")
            return 0.0

    def _calculate_collaboration_satisfaction(self, data: Dict[str, Any]) -> float:
        """Calculate collaboration satisfaction metric."""
        try:
            satisfaction_data = data.get('satisfaction_metrics', {})
            
            creator_a_satisfaction = satisfaction_data.get('creator_a_satisfaction', 0.5)
            creator_b_satisfaction = satisfaction_data.get('creator_b_satisfaction', 0.5)
            process_satisfaction = satisfaction_data.get('process_satisfaction', 0.5)
            outcome_satisfaction = satisfaction_data.get('outcome_satisfaction', 0.5)
            
            satisfaction_score = (
                0.3 * creator_a_satisfaction +
                0.3 * creator_b_satisfaction +
                0.2 * process_satisfaction +
                0.2 * outcome_satisfaction
            )
            
            return max(0.0, min(1.0, satisfaction_score))
            
        except Exception as e:
            logger.error(f"Error calculating collaboration satisfaction: {e}")
            return 0.5

    def _calculate_long_term_potential(self, data: Dict[str, Any]) -> float:
        """Calculate long-term relationship potential."""
        try:
            relationship_data = data.get('relationship_metrics', {})
            
            trust_level = relationship_data.get('trust_level', 0.5)
            communication_quality = relationship_data.get('communication_quality', 0.5)
            shared_vision_alignment = relationship_data.get('shared_vision_alignment', 0.5)
            future_opportunities = relationship_data.get('future_opportunities', 0.5)
            
            potential_score = (
                0.3 * trust_level +
                0.25 * communication_quality +
                0.25 * shared_vision_alignment +
                0.2 * future_opportunities
            )
            
            return max(0.0, min(1.0, potential_score))
            
        except Exception as e:
            logger.error(f"Error calculating long-term potential: {e}")
            return 0.5

    def _calculate_market_penetration(self, data: Dict[str, Any]) -> float:
        """Calculate market penetration metric."""
        try:
            market_data = data.get('market_metrics', {})
            
            new_market_segments = market_data.get('new_market_segments', 0.0)
            demographic_expansion = market_data.get('demographic_expansion', 0.0)
            geographic_reach = market_data.get('geographic_reach', 0.0)
            niche_penetration = market_data.get('niche_penetration', 0.0)
            
            penetration_score = (
                0.3 * new_market_segments +
                0.25 * demographic_expansion +
                0.25 * geographic_reach +
                0.2 * niche_penetration
            )
            
            return max(0.0, min(1.0, penetration_score))
            
        except Exception as e:
            logger.error(f"Error calculating market penetration: {e}")
            return 0.0

    def _calculate_viral_potential(self, data: Dict[str, Any]) -> float:
        """Calculate viral potential metric."""
        try:
            viral_data = data.get('viral_metrics', {})
            
            share_velocity = viral_data.get('share_velocity', 0.0)
            organic_amplification = viral_data.get('organic_amplification', 0.0)
            trend_alignment = viral_data.get('trend_alignment', 0.0)
            memetic_potential = viral_data.get('memetic_potential', 0.0)
            
            viral_score = (
                0.3 * share_velocity +
                0.25 * organic_amplification +
                0.25 * trend_alignment +
                0.2 * memetic_potential
            )
            
            return max(0.0, min(1.0, viral_score))
            
        except Exception as e:
            logger.error(f"Error calculating viral potential: {e}")
            return 0.0

    def _calculate_kpis(
        self,
        raw_data: Dict[str, Any],
        metrics: Dict[PerformanceMetric, float]
    ) -> Dict[str, float]:
        """Calculate key performance indicators."""
        kpis = {}
        
        try:
            # Engagement KPIs
            kpis['engagement_rate'] = raw_data.get('engagement_rate', 0.0)
            kpis['engagement_growth_rate'] = metrics.get(PerformanceMetric.ENGAGEMENT_GROWTH, 0.0)
            
            # Audience KPIs
            kpis['follower_growth_rate'] = raw_data.get('follower_growth_rate', 0.0)
            kpis['audience_retention_rate'] = raw_data.get('audience_retention_rate', 0.0)
            
            # Content KPIs
            kpis['content_completion_rate'] = raw_data.get('content_completion_rate', 0.0)
            kpis['content_share_rate'] = raw_data.get('content_share_rate', 0.0)
            
            # Financial KPIs
            kpis['roi'] = raw_data.get('roi', 0.0)
            kpis['cost_per_engagement'] = raw_data.get('cost_per_engagement', 0.0)
            kpis['revenue_per_view'] = raw_data.get('revenue_per_view', 0.0)
            
            # Brand KPIs
            kpis['brand_sentiment_score'] = raw_data.get('brand_sentiment_score', 0.0)
            kpis['brand_mention_growth'] = raw_data.get('brand_mention_growth', 0.0)
            
            # Collaboration KPIs
            kpis['collaboration_efficiency'] = metrics.get(PerformanceMetric.PRODUCTION_EFFICIENCY, 0.0)
            kpis['creative_synergy_score'] = metrics.get(PerformanceMetric.CREATIVE_INNOVATION, 0.0)
            
        except Exception as e:
            logger.error(f"Error calculating KPIs: {e}")
        
        return kpis

    def _extract_external_factors(
        self,
        data: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract external factors affecting performance."""
        factors = {}
        
        try:
            # Market conditions
            factors['market_conditions'] = data.get('market_conditions', {})
            
            # Seasonal factors
            factors['seasonal_impact'] = data.get('seasonal_impact', 0.0)
            
            # Platform algorithm changes
            factors['algorithm_changes'] = data.get('algorithm_changes', {})
            
            # Competitive landscape
            factors['competitive_pressure'] = data.get('competitive_pressure', 0.0)
            
            # Economic factors
            factors['economic_indicators'] = data.get('economic_indicators', {})
            
            # Platform-specific factors
            factors['platform_performance'] = data.get('platform_performance', {})
            
            # Context factors
            if context:
                factors.update(context.get('external_factors', {}))
                
        except Exception as e:
            logger.error(f"Error extracting external factors: {e}")
        
        return factors

    async def analyze_partnership_performance(
        self,
        partnership_id: str,
        analysis_period: Optional[Tuple[datetime, datetime]] = None
    ) -> PartnershipAnalysis:
        """Perform comprehensive partnership performance analysis."""
        try:
            # Get performance snapshots for the period
            snapshots = self.performance_snapshots.get(partnership_id, [])
            
            if not snapshots:
                raise ValueError(f"No performance data found for partnership {partnership_id}")
            
            # Filter by analysis period if provided
            if analysis_period:
                start_date, end_date = analysis_period
                snapshots = [s for s in snapshots if start_date <= s.timestamp <= end_date]
            else:
                # Default to last 30 days
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)
                snapshots = [s for s in snapshots if start_date <= s.timestamp <= end_date]
                analysis_period = (start_date, end_date)
            
            if not snapshots:
                raise ValueError(f"No performance data found for partnership {partnership_id} in specified period")
            
            # Extract creator IDs from first snapshot
            first_snapshot = snapshots[0]
            creator_a_id = first_snapshot.context.get('creator_a_id', 'unknown')
            creator_b_id = first_snapshot.context.get('creator_b_id', 'unknown')
            
            # Calculate overall performance score
            overall_score = self._calculate_overall_performance_score(snapshots)
            
            # Determine performance category
            category = self._determine_performance_category(overall_score)
            
            # Analyze phase performances
            phase_performances = self._analyze_phase_performances(snapshots)
            
            # Calculate metric scores
            metric_scores = self._calculate_average_metric_scores(snapshots)
            
            # Perform ROI analysis
            roi_analysis = self._perform_roi_analysis(snapshots)
            
            # Identify success factors and improvement areas
            success_factors = self._identify_success_factors(snapshots, metric_scores)
            improvement_areas = self._identify_improvement_areas(snapshots, metric_scores)
            
            # Generate insights
            insights = await self._generate_performance_insights(snapshots, metric_scores)
            
            # Calculate future potential
            future_potential = self._calculate_future_potential(snapshots, metric_scores)
            
            # Perform risk assessment
            risk_assessment = self._perform_risk_assessment(snapshots)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(metric_scores, insights, risk_assessment)
            
            # Benchmark comparison
            benchmark_comparison = self._perform_benchmark_comparison(metric_scores)
            
            analysis = PartnershipAnalysis(
                partnership_id=partnership_id,
                creator_a_id=creator_a_id,
                creator_b_id=creator_b_id,
                analysis_period=analysis_period,
                overall_performance_score=overall_score,
                category=category,
                phase_performances=phase_performances,
                metric_scores=metric_scores,
                roi_analysis=roi_analysis,
                success_factors=success_factors,
                improvement_areas=improvement_areas,
                insights=insights,
                future_potential=future_potential,
                risk_assessment=risk_assessment,
                recommendations=recommendations,
                benchmark_comparison=benchmark_comparison
            )
            
            # Store analysis
            self.partnership_analyses[partnership_id] = analysis
            
            # Update tracking metrics
            self.tracking_metrics['total_partnerships_analyzed'] += 1
            
            logger.info(f"Completed partnership analysis for {partnership_id} - Score: {overall_score:.3f}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing partnership performance: {e}")
            raise

    def _calculate_overall_performance_score(self, snapshots: List[PerformanceSnapshot]) -> float:
        """Calculate overall performance score from snapshots."""
        try:
            if not snapshots:
                return 0.0
            
            # Weight snapshots by recency
            weighted_scores = []
            total_weight = 0.0
            
            for i, snapshot in enumerate(snapshots):
                # More recent snapshots get higher weight
                weight = 1.0 + (i / len(snapshots)) * 0.5
                
                # Calculate snapshot score
                metric_scores = list(snapshot.metrics.values())
                snapshot_score = np.mean(metric_scores) if metric_scores else 0.0
                
                weighted_scores.append(snapshot_score * weight)
                total_weight += weight
            
            overall_score = sum(weighted_scores) / total_weight if total_weight > 0 else 0.0
            return max(0.0, min(1.0, overall_score))
            
        except Exception as e:
            logger.error(f"Error calculating overall performance score: {e}")
            return 0.0

    def _determine_performance_category(self, score: float) -> PerformanceCategory:
        """Determine performance category based on score."""
        if score >= 0.90:
            return PerformanceCategory.EXCEPTIONAL
        elif score >= 0.80:
            return PerformanceCategory.EXCELLENT
        elif score >= 0.70:
            return PerformanceCategory.GOOD
        elif score >= 0.60:
            return PerformanceCategory.AVERAGE
        elif score >= 0.40:
            return PerformanceCategory.BELOW_AVERAGE
        else:
            return PerformanceCategory.POOR

    def _analyze_phase_performances(self, snapshots: List[PerformanceSnapshot]) -> Dict[PerformancePhase, float]:
        """Analyze performance by collaboration phase."""
        phase_performances = {}
        phase_snapshots = defaultdict(list)
        
        # Group snapshots by phase
        for snapshot in snapshots:
            phase_snapshots[snapshot.phase].append(snapshot)
        
        # Calculate average performance for each phase
        for phase, phase_snaps in phase_snapshots.items():
            phase_scores = []
            for snapshot in phase_snaps:
                metric_scores = list(snapshot.metrics.values())
                if metric_scores:
                    phase_scores.append(np.mean(metric_scores))
            
            phase_performances[phase] = np.mean(phase_scores) if phase_scores else 0.0
        
        return phase_performances

    def _calculate_average_metric_scores(self, snapshots: List[PerformanceSnapshot]) -> Dict[PerformanceMetric, float]:
        """Calculate average scores for each metric."""
        metric_scores = {}
        metric_values = defaultdict(list)
        
        # Collect all metric values
        for snapshot in snapshots:
            for metric, value in snapshot.metrics.items():
                metric_values[metric].append(value)
        
        # Calculate averages
        for metric, values in metric_values.items():
            metric_scores[metric] = np.mean(values) if values else 0.0
        
        return metric_scores

    def _perform_roi_analysis(self, snapshots: List[PerformanceSnapshot]) -> Dict[str, float]:
        """Perform ROI analysis from snapshots."""
        roi_analysis = {}
        
        try:
            # Extract financial data from snapshots
            revenue_values = []
            investment_values = []
            
            for snapshot in snapshots:
                revenue_metric = snapshot.metrics.get(PerformanceMetric.REVENUE_GENERATION, 0.0)
                revenue_values.append(revenue_metric)
                
                # Extract investment from KPIs if available
                investment = snapshot.kpis.get('investment', 1.0)
                investment_values.append(investment)
            
            # Calculate ROI metrics
            total_revenue = sum(revenue_values)
            total_investment = sum(investment_values)
            
            roi_analysis['total_revenue_score'] = total_revenue
            roi_analysis['total_investment_score'] = total_investment
            roi_analysis['roi_ratio'] = total_revenue / total_investment if total_investment > 0 else 0.0
            roi_analysis['revenue_trend'] = self._calculate_trend(revenue_values)
            roi_analysis['payback_period_estimate'] = self._estimate_payback_period(revenue_values, investment_values)
            roi_analysis['profit_margin'] = (total_revenue - total_investment) / total_revenue if total_revenue > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error performing ROI analysis: {e}")
            roi_analysis = {
                'total_revenue_score': 0.0,
                'total_investment_score': 0.0,
                'roi_ratio': 0.0,
                'revenue_trend': 0.0,
                'payback_period_estimate': 0.0,
                'profit_margin': 0.0
            }
        
        return roi_analysis

    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend direction (-1 to 1)."""
        if len(values) < 2:
            return 0.0
        
        # Simple linear trend
        x = list(range(len(values)))
        slope = np.polyfit(x, values, 1)[0] if len(values) > 1 else 0.0
        
        # Normalize slope to -1 to 1 range
        return max(-1.0, min(1.0, slope * 10))

    def _estimate_payback_period(self, revenue_values: List[float], investment_values: List[float]) -> float:
        """Estimate payback period in days."""
        if not revenue_values or not investment_values:
            return 0.0
        
        total_investment = sum(investment_values)
        if total_investment <= 0:
            return 0.0
        
        cumulative_revenue = 0.0
        for i, revenue in enumerate(revenue_values):
            cumulative_revenue += revenue
            if cumulative_revenue >= total_investment:
                return i + 1  # Days to payback
        
        return len(revenue_values)  # Full period if not reached

    def _identify_success_factors(
        self,
        snapshots: List[PerformanceSnapshot],
        metric_scores: Dict[PerformanceMetric, float]
    ) -> List[str]:
        """Identify key success factors."""
        success_factors = []
        
        # High-performing metrics
        top_metrics = sorted(metric_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        
        factor_descriptions = {
            PerformanceMetric.ENGAGEMENT_GROWTH: "Strong audience engagement and community building",
            PerformanceMetric.AUDIENCE_EXPANSION: "Effective cross-audience growth and reach expansion",
            PerformanceMetric.CONTENT_QUALITY: "High-quality content production and creative excellence",
            PerformanceMetric.REVENUE_GENERATION: "Successful monetization and revenue optimization",
            PerformanceMetric.BRAND_AWARENESS: "Increased brand visibility and market presence",
            PerformanceMetric.CREATIVE_INNOVATION: "Innovative creative approaches and artistic growth",
            PerformanceMetric.PRODUCTION_EFFICIENCY: "Streamlined production processes and resource optimization",
            PerformanceMetric.CROSS_PROMOTION_SUCCESS: "Effective cross-platform promotion and amplification",
            PerformanceMetric.COLLABORATION_SATISFACTION: "Positive collaboration experience and partnership satisfaction",
            PerformanceMetric.LONG_TERM_RELATIONSHIP: "Strong foundation for ongoing partnership",
            PerformanceMetric.MARKET_PENETRATION: "Successful entry into new market segments",
            PerformanceMetric.VIRAL_POTENTIAL: "Content with high shareability and viral characteristics"
        }
        
        for metric, score in top_metrics:
            if score >= 0.70:
                success_factors.append(factor_descriptions.get(metric, f"Strong {metric.value} performance"))
        
        return success_factors

    def _identify_improvement_areas(
        self,
        snapshots: List[PerformanceSnapshot],
        metric_scores: Dict[PerformanceMetric, float]
    ) -> List[str]:
        """Identify areas needing improvement."""
        improvement_areas = []
        
        # Low-performing metrics
        bottom_metrics = sorted(metric_scores.items(), key=lambda x: x[1])[:3]
        
        improvement_descriptions = {
            PerformanceMetric.ENGAGEMENT_GROWTH: "Enhance audience engagement strategies and community interaction",
            PerformanceMetric.AUDIENCE_EXPANSION: "Improve cross-audience acquisition and retention methods",
            PerformanceMetric.CONTENT_QUALITY: "Elevate content production standards and creative execution",
            PerformanceMetric.REVENUE_GENERATION: "Optimize monetization strategies and revenue streams",
            PerformanceMetric.BRAND_AWARENESS: "Strengthen brand building and market visibility efforts",
            PerformanceMetric.CREATIVE_INNOVATION: "Explore more innovative creative approaches and formats",
            PerformanceMetric.PRODUCTION_EFFICIENCY: "Streamline production workflows and resource utilization",
            PerformanceMetric.CROSS_PROMOTION_SUCCESS: "Enhance cross-platform promotion effectiveness",
            PerformanceMetric.COLLABORATION_SATISFACTION: "Improve collaboration processes and communication",
            PerformanceMetric.LONG_TERM_RELATIONSHIP: "Strengthen partnership foundation and future planning",
            PerformanceMetric.MARKET_PENETRATION: "Develop better market entry and expansion strategies",
            PerformanceMetric.VIRAL_POTENTIAL: "Create more shareable and viral-ready content"
        }
        
        for metric, score in bottom_metrics:
            if score <= 0.60:
                improvement_areas.append(improvement_descriptions.get(metric, f"Improve {metric.value} performance"))
        
        return improvement_areas

    async def _generate_performance_insights(
        self,
        snapshots: List[PerformanceSnapshot],
        metric_scores: Dict[PerformanceMetric, float]
    ) -> List[PerformanceInsight]:
        """Generate actionable performance insights."""
        insights = []
        
        try:
            # Trend analysis insights
            for metric, score in metric_scores.items():
                metric_values = [s.metrics.get(metric, 0.0) for s in snapshots]
                trend = self._calculate_trend(metric_values)
                
                if abs(trend) > 0.3:  # Significant trend
                    insight_type = "trend_analysis"
                    direction = "positive" if trend > 0 else "negative"
                    
                    insight = PerformanceInsight(
                        insight_type=insight_type,
                        title=f"{metric.value.replace('_', ' ').title()} {direction.title()} Trend",
                        description=f"Strong {'upward' if trend > 0 else 'downward'} trend detected in {metric.value}",
                        impact_level="high" if abs(trend) > 0.6 else "medium",
                        actionable_recommendations=self._get_trend_recommendations(metric, trend),
                        confidence_score=min(abs(trend), 1.0),
                        supporting_data={'trend_value': trend, 'data_points': len(metric_values)}
                    )
                    insights.append(insight)
            
            # Performance gap insights
            for metric, score in metric_scores.items():
                benchmark = self.benchmarks.get(metric.value, 0.5)
                gap = score - benchmark
                
                if abs(gap) > 0.2:  # Significant gap
                    insight_type = "performance_gap"
                    gap_type = "opportunity" if gap > 0 else "underperformance"
                    
                    insight = PerformanceInsight(
                        insight_type=insight_type,
                        title=f"{metric.value.replace('_', ' ').title()} {'Exceeds' if gap > 0 else 'Below'} Benchmark",
                        description=f"Performance {'above' if gap > 0 else 'below'} industry benchmark by {abs(gap):.1%}",
                        impact_level="high" if abs(gap) > 0.4 else "medium",
                        actionable_recommendations=self._get_gap_recommendations(metric, gap),
                        confidence_score=0.8,
                        supporting_data={'gap_value': gap, 'current_score': score, 'benchmark': benchmark}
                    )
                    insights.append(insight)
            
            # Phase performance insights
            phase_performances = self._analyze_phase_performances(snapshots)
            best_phase = max(phase_performances, key=phase_performances.get) if phase_performances else None
            worst_phase = min(phase_performances, key=phase_performances.get) if phase_performances else None
            
            if best_phase and worst_phase and phase_performances[best_phase] - phase_performances[worst_phase] > 0.2:
                insight = PerformanceInsight(
                    insight_type="phase_analysis",
                    title="Phase Performance Variation",
                    description=f"Significant performance difference between {best_phase.value} and {worst_phase.value} phases",
                    impact_level="medium",
                    actionable_recommendations=[
                        f"Analyze success factors from {best_phase.value} phase",
                        f"Apply learnings to improve {worst_phase.value} phase performance",
                        "Establish phase-specific optimization strategies"
                    ],
                    confidence_score=0.7,
                    supporting_data={'best_phase': best_phase.value, 'worst_phase': worst_phase.value}
                )
                insights.append(insight)
            
            # Update insights counter
            self.tracking_metrics['insights_generated'] += len(insights)
            
        except Exception as e:
            logger.error(f"Error generating performance insights: {e}")
        
        return insights[:10]  # Limit to top 10 insights

    def _get_trend_recommendations(self, metric: PerformanceMetric, trend: float) -> List[str]:
        """Get recommendations based on metric trend."""
        recommendations = []
        
        if trend > 0:  # Positive trend
            recommendations.append(f"Maintain and amplify current strategies driving {metric.value} growth")
            recommendations.append("Identify replicable success patterns for other metrics")
            recommendations.append("Consider increasing investment in this area")
        else:  # Negative trend
            recommendations.append(f"Investigate root causes of declining {metric.value}")
            recommendations.append("Implement corrective measures immediately")
            recommendations.append("Monitor closely and adjust strategies")
        
        return recommendations

    def _get_gap_recommendations(self, metric: PerformanceMetric, gap: float) -> List[str]:
        """Get recommendations based on performance gap."""
        recommendations = []
        
        if gap > 0:  # Above benchmark
            recommendations.append("Leverage this strength for competitive advantage")
            recommendations.append("Share best practices with other performance areas")
            recommendations.append("Consider setting higher targets for continued growth")
        else:  # Below benchmark
            recommendations.append("Prioritize improvement in this area")
            recommendations.append("Study industry best practices and successful competitors")
            recommendations.append("Allocate additional resources to close the gap")
        
        return recommendations

    def _calculate_future_potential(
        self,
        snapshots: List[PerformanceSnapshot],
        metric_scores: Dict[PerformanceMetric, float]
    ) -> float:
        """Calculate future collaboration potential."""
        try:
            # Weight different factors for future potential
            factors = {
                'current_performance': np.mean(list(metric_scores.values())),
                'collaboration_satisfaction': metric_scores.get(PerformanceMetric.COLLABORATION_SATISFACTION, 0.5),
                'long_term_relationship': metric_scores.get(PerformanceMetric.LONG_TERM_RELATIONSHIP, 0.5),
                'creative_innovation': metric_scores.get(PerformanceMetric.CREATIVE_INNOVATION, 0.5),
                'revenue_potential': metric_scores.get(PerformanceMetric.REVENUE_GENERATION, 0.5)
            }
            
            # Calculate growth trends
            growth_trends = []
            for metric in [PerformanceMetric.ENGAGEMENT_GROWTH, PerformanceMetric.AUDIENCE_EXPANSION]:
                metric_values = [s.metrics.get(metric, 0.0) for s in snapshots]
                trend = self._calculate_trend(metric_values)
                growth_trends.append(max(0.0, trend))
            
            average_growth_trend = np.mean(growth_trends) if growth_trends else 0.0
            
            # Weighted combination
            future_potential = (
                0.3 * factors['current_performance'] +
                0.2 * factors['collaboration_satisfaction'] +
                0.2 * factors['long_term_relationship'] +
                0.15 * factors['creative_innovation'] +
                0.1 * factors['revenue_potential'] +
                0.05 * average_growth_trend
            )
            
            return max(0.0, min(1.0, future_potential))
            
        except Exception as e:
            logger.error(f"Error calculating future potential: {e}")
            return 0.5

    def _perform_risk_assessment(self, snapshots: List[PerformanceSnapshot]) -> Dict[str, float]:
        """Perform partnership risk assessment."""
        risk_assessment = {}
        
        try:
            # Calculate various risk factors
            
            # Performance volatility risk
            overall_scores = []
            for snapshot in snapshots:
                metric_scores = list(snapshot.metrics.values())
                overall_scores.append(np.mean(metric_scores) if metric_scores else 0.0)
            
            volatility = np.std(overall_scores) if len(overall_scores) > 1 else 0.0
            risk_assessment['performance_volatility'] = min(volatility * 2, 1.0)
            
            # Declining trend risk
            trend = self._calculate_trend(overall_scores)
            risk_assessment['declining_trend'] = max(0.0, -trend)
            
            # Low satisfaction risk
            satisfaction_scores = [
                s.metrics.get(PerformanceMetric.COLLABORATION_SATISFACTION, 0.5)
                for s in snapshots
            ]
            avg_satisfaction = np.mean(satisfaction_scores) if satisfaction_scores else 0.5
            risk_assessment['low_satisfaction'] = max(0.0, 1.0 - avg_satisfaction)
            
            # Revenue risk
            revenue_scores = [
                s.metrics.get(PerformanceMetric.REVENUE_GENERATION, 0.0)
                for s in snapshots
            ]
            avg_revenue = np.mean(revenue_scores) if revenue_scores else 0.0
            risk_assessment['revenue_underperformance'] = max(0.0, 0.5 - avg_revenue)
            
            # Market risk (external factors)
            market_risks = []
            for snapshot in snapshots:
                market_conditions = snapshot.external_factors.get('market_conditions', {})
                competitive_pressure = snapshot.external_factors.get('competitive_pressure', 0.0)
                market_risks.append(competitive_pressure)
            
            avg_market_risk = np.mean(market_risks) if market_risks else 0.3
            risk_assessment['market_conditions'] = avg_market_risk
            
            # Overall risk score
            risk_scores = list(risk_assessment.values())
            risk_assessment['overall_risk'] = np.mean(risk_scores) if risk_scores else 0.3
            
        except Exception as e:
            logger.error(f"Error performing risk assessment: {e}")
            risk_assessment = {
                'performance_volatility': 0.3,
                'declining_trend': 0.3,
                'low_satisfaction': 0.3,
                'revenue_underperformance': 0.3,
                'market_conditions': 0.3,
                'overall_risk': 0.3
            }
        
        return risk_assessment

    def _generate_recommendations(
        self,
        metric_scores: Dict[PerformanceMetric, float],
        insights: List[PerformanceInsight],
        risk_assessment: Dict[str, float]
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        try:
            # Performance-based recommendations
            low_metrics = [metric for metric, score in metric_scores.items() if score < 0.6]
            high_metrics = [metric for metric, score in metric_scores.items() if score > 0.8]
            
            if low_metrics:
                recommendations.append(f"Priority focus on improving: {', '.join([m.value for m in low_metrics[:2]])}")
            
            if high_metrics:
                recommendations.append(f"Leverage strengths in: {', '.join([m.value for m in high_metrics[:2]])}")
            
            # Risk-based recommendations
            high_risks = [risk for risk, level in risk_assessment.items() if level > 0.6]
            if high_risks:
                recommendations.append(f"Address high-risk areas: {', '.join(high_risks[:2])}")
            
            # Insight-based recommendations
            high_impact_insights = [i for i in insights if i.impact_level == "high"]
            for insight in high_impact_insights[:2]:
                recommendations.extend(insight.actionable_recommendations[:1])
            
            # General recommendations
            overall_score = np.mean(list(metric_scores.values()))
            if overall_score >= 0.8:
                recommendations.append("Maintain current momentum and explore expansion opportunities")
            elif overall_score >= 0.6:
                recommendations.append("Focus on consistency and addressing specific weaknesses")
            else:
                recommendations.append("Comprehensive performance review and strategy adjustment needed")
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
        
        return recommendations[:8]  # Limit to top 8 recommendations

    def _perform_benchmark_comparison(self, metric_scores: Dict[PerformanceMetric, float]) -> Dict[str, float]:
        """Compare performance against benchmarks."""
        comparison = {}
        
        for metric, score in metric_scores.items():
            benchmark = self.benchmarks.get(metric.value, 0.5)
            comparison[f"{metric.value}_vs_benchmark"] = score - benchmark
            comparison[f"{metric.value}_relative_performance"] = (score / benchmark) if benchmark > 0 else 1.0
        
        # Overall benchmark comparison
        benchmark_gaps = [comparison[key] for key in comparison.keys() if key.endswith('_vs_benchmark')]
        comparison['overall_vs_benchmark'] = np.mean(benchmark_gaps) if benchmark_gaps else 0.0
        
        return comparison

    async def get_performance_trends(
        self,
        partnership_id: str,
        metric: Optional[PerformanceMetric] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get performance trends for a partnership."""
        try:
            snapshots = self.performance_snapshots.get(partnership_id, [])
            
            # Filter by time period
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_snapshots = [s for s in snapshots if s.timestamp >= cutoff_date]
            
            if not recent_snapshots:
                return {'error': 'No recent performance data available'}
            
            trends = {}
            
            if metric:
                # Single metric trend
                values = [s.metrics.get(metric, 0.0) for s in recent_snapshots]
                timestamps = [s.timestamp for s in recent_snapshots]
                
                trends[metric.value] = {
                    'values': values,
                    'timestamps': [t.isoformat() for t in timestamps],
                    'trend_direction': self._calculate_trend(values),
                    'average': np.mean(values),
                    'volatility': np.std(values),
                    'latest_value': values[-1] if values else 0.0
                }
            else:
                # All metrics trends
                for perf_metric in PerformanceMetric:
                    values = [s.metrics.get(perf_metric, 0.0) for s in recent_snapshots]
                    
                    trends[perf_metric.value] = {
                        'trend_direction': self._calculate_trend(values),
                        'average': np.mean(values),
                        'latest_value': values[-1] if values else 0.0
                    }
            
            return trends
            
        except Exception as e:
            logger.error(f"Error getting performance trends: {e}")
            return {'error': str(e)}

    async def get_analyzer_metrics(self) -> Dict[str, Any]:
        """Get analyzer performance metrics."""
        try:
            return {
                'total_partnerships_analyzed': self.tracking_metrics['total_partnerships_analyzed'],
                'average_analysis_time': self.tracking_metrics['average_analysis_time'],
                'prediction_accuracy': self.tracking_metrics['prediction_accuracy'],
                'insights_generated': self.tracking_metrics['insights_generated'],
                'successful_partnerships': self.tracking_metrics['successful_partnerships'],
                'failed_partnerships': self.tracking_metrics['failed_partnerships'],
                'success_rate': (
                    self.tracking_metrics['successful_partnerships'] /
                    (self.tracking_metrics['successful_partnerships'] + self.tracking_metrics['failed_partnerships'])
                    if (self.tracking_metrics['successful_partnerships'] + self.tracking_metrics['failed_partnerships']) > 0
                    else 0.0
                ),
                'total_snapshots_recorded': sum(len(snapshots) for snapshots in self.performance_snapshots.values()),
                'active_partnerships': len(self.performance_snapshots),
                'benchmarks': self.benchmarks
            }
            
        except Exception as e:
            logger.error(f"Error getting analyzer metrics: {e}")
            return {'error': str(e)}

# Example usage and testing
if __name__ == "__main__":
    async def test_partnership_analyzer():
        """Test partnership performance analyzer."""
        analyzer = PartnershipPerformanceAnalyzer()
        
        # Sample performance data
        sample_data = {
            'current_engagement': {'likes': 1500, 'comments': 300, 'shares': 200, 'saves': 100},
            'baseline_engagement': {'likes': 1000, 'comments': 200, 'shares': 150, 'saves': 75},
            'audience_metrics': {
                'new_followers': 500,
                'cross_pollination_rate': 0.25,
                'reach_expansion': 0.30
            },
            'content_quality': {
                'production_quality': 0.85,
                'creativity_score': 0.90,
                'technical_execution': 0.80,
                'audience_feedback': 0.88
            },
            'revenue_metrics': {
                'direct_revenue': 5000,
                'indirect_revenue': 2000,
                'investment': 3000,
                'roi': 2.33
            }
        }
        
        try:
            # Record performance snapshot
            snapshot = await analyzer.record_performance_snapshot(
                partnership_id="partnership_001",
                phase=PerformancePhase.ACTIVE_COLLABORATION,
                metrics_data=sample_data,
                context={'creator_a_id': 'creator_001', 'creator_b_id': 'creator_002'}
            )
            
            print(f"Recorded snapshot with {len(snapshot.metrics)} metrics")
            
            # Perform analysis
            analysis = await analyzer.analyze_partnership_performance("partnership_001")
            
            print(f"Partnership Analysis:")
            print(f"  Overall Score: {analysis.overall_performance_score:.3f}")
            print(f"  Category: {analysis.category.value}")
            print(f"  Future Potential: {analysis.future_potential:.3f}")
            print(f"  Success Factors: {len(analysis.success_factors)}")
            print(f"  Insights Generated: {len(analysis.insights)}")
            
            # Get trends
            trends = await analyzer.get_performance_trends("partnership_001")
            print(f"Trends available for {len(trends)} metrics")
            
            # Get analyzer metrics
            metrics = await analyzer.get_analyzer_metrics()
            print(f"Analyzer Metrics: {metrics}")
            
        except Exception as e:
            print(f"Error in test: {e}")
    
    # Run test
    asyncio.run(test_partnership_analyzer())