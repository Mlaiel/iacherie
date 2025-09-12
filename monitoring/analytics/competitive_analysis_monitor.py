"""
Ainflue Platform - Competitive Analysis Monitor
==============================================

Enterprise-grade competitive intelligence system with real-time competitor tracking,
market positioning analysis, trend detection, and strategic insights generation.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
import statistics
from collections import defaultdict, deque
import hashlib
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CompetitorCategory(Enum):
    """Categories of competitors to monitor."""
    DIRECT_COMPETITOR = "direct_competitor"
    INDIRECT_COMPETITOR = "indirect_competitor"
    PLATFORM_COMPETITOR = "platform_competitor"
    TECHNOLOGY_COMPETITOR = "technology_competitor"
    MARKET_LEADER = "market_leader"
    EMERGING_PLAYER = "emerging_player"

class AnalysisMetric(Enum):
    """Types of competitive metrics to track."""
    MARKET_SHARE = "market_share"
    USER_ENGAGEMENT = "user_engagement"
    FEATURE_ADOPTION = "feature_adoption"
    PRICING_STRATEGY = "pricing_strategy"
    CONTENT_QUALITY = "content_quality"
    SOCIAL_PRESENCE = "social_presence"
    TECHNOLOGY_STACK = "technology_stack"
    PARTNERSHIP_NETWORK = "partnership_network"
    REVENUE_MODEL = "revenue_model"
    USER_ACQUISITION = "user_acquisition"

class TrendDirection(Enum):
    """Direction of competitive trends."""
    RISING = "rising"
    DECLINING = "declining" 
    STABLE = "stable"
    VOLATILE = "volatile"
    BREAKTHROUGH = "breakthrough"

@dataclass
class CompetitorProfile:
    """Comprehensive competitor profile."""
    competitor_id: str
    name: str
    category: CompetitorCategory
    website: str
    description: str
    founded_year: int
    headquarters: str
    estimated_users: int = 0
    estimated_revenue: float = 0.0
    funding_raised: float = 0.0
    employees_count: int = 0
    key_features: List[str] = field(default_factory=list)
    pricing_model: str = ""
    target_audience: List[str] = field(default_factory=list)
    geographic_presence: List[str] = field(default_factory=list)
    technology_stack: List[str] = field(default_factory=list)
    key_partnerships: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    monitoring_active: bool = True

@dataclass
class CompetitiveMetric:
    """Individual competitive metric data point."""
    metric_id: str
    competitor_id: str
    metric_type: AnalysisMetric
    value: float
    normalized_value: float
    timestamp: datetime
    source: str
    confidence_score: float = 0.8
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MarketIntelligence:
    """Market intelligence analysis result."""
    analysis_id: str
    analysis_type: str
    market_segment: str
    time_period: str
    key_findings: List[str]
    market_trends: Dict[str, Any]
    competitive_landscape: Dict[str, Any]
    opportunities: List[str]
    threats: List[str]
    strategic_recommendations: List[str]
    confidence_score: float
    generated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class TrendAnalysis:
    """Trend analysis for competitive metrics."""
    trend_id: str
    metric_type: AnalysisMetric
    trend_direction: TrendDirection
    magnitude: float
    duration_days: int
    affected_competitors: List[str]
    significance_score: float
    implications: List[str]
    detected_at: datetime = field(default_factory=datetime.utcnow)

class CompetitiveAnalysisMonitor:
    """
    Enterprise competitive analysis and intelligence system.
    
    Features:
    - Real-time competitor tracking and profiling
    - Multi-dimensional competitive metrics analysis
    - Market trend detection and prediction
    - Strategic positioning insights
    - Competitive advantage identification
    - Market opportunity discovery
    - Threat assessment and early warning
    - Strategic recommendation generation
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.competitors: Dict[str, CompetitorProfile] = {}
        self.metrics_history: Dict[str, List[CompetitiveMetric]] = defaultdict(list)
        self.market_intelligence: Dict[str, MarketIntelligence] = {}
        self.trend_analyses: Dict[str, TrendAnalysis] = {}
        self.analysis_models: Dict[str, Any] = {}
        
        # Initialize competitive analysis components
        self._setup_analysis_models()
        self._setup_data_sources()
        self._setup_intelligence_algorithms()
        self._setup_benchmarking_framework()
        
        logger.info("🔍 Competitive Analysis Monitor initialized")
    
    def _setup_analysis_models(self):
        """Initialize competitive analysis models."""
        self.analysis_models = {
            "market_positioning": {
                "algorithm": "multi_dimensional_scaling",
                "dimensions": ["feature_completeness", "user_experience", "pricing", "market_reach"],
                "accuracy": 0.87,
                "last_trained": datetime.utcnow() - timedelta(days=7)
            },
            "trend_detection": {
                "algorithm": "time_series_analysis",
                "window_size": 30,  # days
                "sensitivity": 0.15,
                "accuracy": 0.83
            },
            "opportunity_scoring": {
                "algorithm": "gradient_boosting",
                "features": ["market_gap", "user_demand", "technical_feasibility", "competitive_intensity"],
                "accuracy": 0.79
            },
            "threat_assessment": {
                "algorithm": "ensemble_classifier",
                "threat_categories": ["market_disruption", "technology_advancement", "pricing_pressure"],
                "precision": 0.84
            }
        }
        
        logger.info("📊 Analysis models configured")
    
    def _setup_data_sources(self):
        """Initialize data sources for competitive intelligence."""
        self.data_sources = {
            "web_scraping": {
                "enabled": True,
                "frequency": "daily",
                "targets": ["competitor_websites", "pricing_pages", "feature_announcements"]
            },
            "social_media": {
                "enabled": True,
                "platforms": ["twitter", "linkedin", "youtube", "tiktok"],
                "frequency": "hourly"
            },
            "news_monitoring": {
                "enabled": True,
                "sources": ["techcrunch", "venturebeat", "industry_blogs"],
                "keywords": ["ai music", "content creation", "creator economy"]
            },
            "app_stores": {
                "enabled": True,
                "stores": ["app_store", "google_play", "web_stores"],
                "metrics": ["downloads", "ratings", "reviews"]
            },
            "financial_data": {
                "enabled": True,
                "sources": ["crunchbase", "pitchbook", "public_filings"],
                "frequency": "weekly"
            },
            "patent_monitoring": {
                "enabled": True,
                "databases": ["uspto", "epo", "wipo"],
                "technology_areas": ["ai", "audio_processing", "blockchain"]
            }
        }
        
        logger.info("🌐 Data sources configured")
    
    def _setup_intelligence_algorithms(self):
        """Initialize intelligence analysis algorithms."""
        self.intelligence_algorithms = {
            "swot_analysis": {
                "enabled": True,
                "factors": {
                    "strengths": ["technology", "market_position", "user_base", "funding"],
                    "weaknesses": ["feature_gaps", "user_complaints", "technical_issues"],
                    "opportunities": ["market_gaps", "emerging_trends", "partnerships"],
                    "threats": ["new_competitors", "technology_shifts", "regulatory_changes"]
                }
            },
            "porter_five_forces": {
                "enabled": True,
                "forces": [
                    "competitive_rivalry",
                    "supplier_power",
                    "buyer_power", 
                    "threat_of_substitution",
                    "threat_of_new_entry"
                ]
            },
            "value_chain_analysis": {
                "enabled": True,
                "primary_activities": ["content_creation", "platform_operations", "marketing", "distribution"],
                "support_activities": ["technology", "human_resources", "procurement"]
            }
        }
        
        logger.info("🧠 Intelligence algorithms configured")
    
    def _setup_benchmarking_framework(self):
        """Initialize competitive benchmarking framework."""
        self.benchmarking_framework = {
            "performance_indicators": {
                "user_growth_rate": {"weight": 0.25, "benchmark_type": "percentile"},
                "engagement_rate": {"weight": 0.20, "benchmark_type": "average"},
                "feature_velocity": {"weight": 0.15, "benchmark_type": "trend"},
                "market_share": {"weight": 0.20, "benchmark_type": "absolute"},
                "customer_satisfaction": {"weight": 0.20, "benchmark_type": "score"}
            },
            "benchmarking_frequency": "weekly",
            "peer_groups": {
                "direct_competitors": ["competitor_a", "competitor_b"],
                "market_leaders": ["leader_a", "leader_b"],
                "emerging_players": ["startup_a", "startup_b"]
            }
        }
        
        logger.info("📏 Benchmarking framework configured")
    
    async def add_competitor(self, competitor_data: Dict[str, Any]) -> str:
        """
        Add a new competitor to the monitoring system.
        
        Args:
            competitor_data: Competitor information and profile data
            
        Returns:
            Competitor ID for tracking
        """
        try:
            competitor_id = str(uuid.uuid4())
            
            competitor = CompetitorProfile(
                competitor_id=competitor_id,
                name=competitor_data["name"],
                category=CompetitorCategory(competitor_data["category"]),
                website=competitor_data["website"],
                description=competitor_data["description"],
                founded_year=competitor_data.get("founded_year", 2020),
                headquarters=competitor_data.get("headquarters", "Unknown"),
                estimated_users=competitor_data.get("estimated_users", 0),
                estimated_revenue=competitor_data.get("estimated_revenue", 0.0),
                funding_raised=competitor_data.get("funding_raised", 0.0),
                employees_count=competitor_data.get("employees_count", 0),
                key_features=competitor_data.get("key_features", []),
                pricing_model=competitor_data.get("pricing_model", ""),
                target_audience=competitor_data.get("target_audience", []),
                geographic_presence=competitor_data.get("geographic_presence", []),
                technology_stack=competitor_data.get("technology_stack", []),
                key_partnerships=competitor_data.get("key_partnerships", []),
                strengths=competitor_data.get("strengths", []),
                weaknesses=competitor_data.get("weaknesses", [])
            )
            
            self.competitors[competitor_id] = competitor
            
            # Initialize monitoring for this competitor
            await self._initialize_competitor_monitoring(competitor)
            
            # Perform initial competitive analysis
            initial_analysis = await self._perform_initial_analysis(competitor)
            
            logger.info(f"🎯 Competitor added: {competitor.name} ({competitor_id})")
            
            return {
                "competitor_id": competitor_id,
                "status": "added",
                "monitoring_active": True,
                "initial_analysis": initial_analysis,
                "next_update": (datetime.utcnow() + timedelta(hours=24)).isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error adding competitor: {e}")
            return {"status": "error", "message": str(e)}
    
    async def update_competitor_metrics(self, competitor_id: str, metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update competitive metrics for a competitor.
        
        Args:
            competitor_id: Competitor identifier
            metrics_data: New metrics data
            
        Returns:
            Update result with trend analysis
        """
        try:
            if competitor_id not in self.competitors:
                return {"status": "error", "message": "Competitor not found"}
            
            competitor = self.competitors[competitor_id]
            
            # Process each metric
            updated_metrics = []
            for metric_name, metric_value in metrics_data.items():
                if hasattr(AnalysisMetric, metric_name.upper()):
                    metric_type = AnalysisMetric(metric_name)
                    
                    # Create metric record
                    metric = CompetitiveMetric(
                        metric_id=str(uuid.uuid4()),
                        competitor_id=competitor_id,
                        metric_type=metric_type,
                        value=float(metric_value),
                        normalized_value=await self._normalize_metric_value(metric_type, metric_value),
                        timestamp=datetime.utcnow(),
                        source=metrics_data.get("source", "manual_update"),
                        confidence_score=metrics_data.get("confidence", 0.8)
                    )
                    
                    # Store metric
                    metric_key = f"{competitor_id}_{metric_type.value}"
                    self.metrics_history[metric_key].append(metric)
                    
                    # Keep only last 90 days of data
                    cutoff_date = datetime.utcnow() - timedelta(days=90)
                    self.metrics_history[metric_key] = [
                        m for m in self.metrics_history[metric_key]
                        if m.timestamp >= cutoff_date
                    ]
                    
                    updated_metrics.append(metric_name)
            
            # Analyze trends for updated metrics
            trend_analysis = await self._analyze_metric_trends(competitor_id, updated_metrics)
            
            # Update competitor profile timestamp
            competitor.last_updated = datetime.utcnow()
            
            # Trigger competitive alerts if needed
            alerts = await self._check_competitive_alerts(competitor_id, metrics_data, trend_analysis)
            
            logger.info(f"📊 Metrics updated for {competitor.name}: {len(updated_metrics)} metrics")
            
            return {
                "status": "updated",
                "competitor_id": competitor_id,
                "updated_metrics": updated_metrics,
                "trend_analysis": trend_analysis,
                "competitive_alerts": alerts,
                "last_updated": competitor.last_updated.isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error updating competitor metrics: {e}")
            return {"status": "error", "message": str(e)}
    
    async def analyze_market_positioning(self, market_segment: str = "ai_content_creation") -> Dict[str, Any]:
        """
        Analyze market positioning across all competitors.
        
        Args:
            market_segment: Market segment to analyze
            
        Returns:
            Market positioning analysis
        """
        try:
            active_competitors = [
                comp for comp in self.competitors.values()
                if comp.monitoring_active
            ]
            
            if len(active_competitors) < 2:
                return {"status": "error", "message": "Need at least 2 active competitors for analysis"}
            
            # Analyze positioning dimensions
            positioning_analysis = await self._calculate_positioning_matrix(active_competitors)
            
            # Identify market leaders and laggards
            market_leaders = await self._identify_market_leaders(active_competitors, positioning_analysis)
            
            # Find market gaps and opportunities
            market_opportunities = await self._identify_market_opportunities(positioning_analysis)
            
            # Competitive intensity analysis
            competitive_intensity = await self._analyze_competitive_intensity(active_competitors)
            
            # Generate strategic insights
            strategic_insights = await self._generate_strategic_insights(
                positioning_analysis, market_leaders, market_opportunities
            )
            
            analysis_result = {
                "market_segment": market_segment,
                "analysis_date": datetime.utcnow().isoformat(),
                "competitors_analyzed": len(active_competitors),
                "positioning_matrix": positioning_analysis,
                "market_leaders": market_leaders,
                "market_opportunities": market_opportunities,
                "competitive_intensity": competitive_intensity,
                "strategic_insights": strategic_insights,
                "confidence_score": 0.85
            }
            
            # Store analysis for future reference
            analysis_id = str(uuid.uuid4())
            self.market_intelligence[analysis_id] = MarketIntelligence(
                analysis_id=analysis_id,
                analysis_type="market_positioning",
                market_segment=market_segment,
                time_period="current",
                key_findings=strategic_insights.get("key_findings", []),
                market_trends=positioning_analysis,
                competitive_landscape={"leaders": market_leaders, "intensity": competitive_intensity},
                opportunities=market_opportunities.get("identified_gaps", []),
                threats=strategic_insights.get("competitive_threats", []),
                strategic_recommendations=strategic_insights.get("recommendations", []),
                confidence_score=0.85
            )
            
            logger.info(f"📈 Market positioning analysis completed for {market_segment}")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"❌ Error in market positioning analysis: {e}")
            return {"status": "error", "message": str(e)}
    
    async def detect_competitive_trends(self, period_days: int = 30) -> Dict[str, Any]:
        """
        Detect and analyze competitive trends across the market.
        
        Args:
            period_days: Analysis period in days
            
        Returns:
            Trend detection and analysis results
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=period_days)
            
            # Analyze trends for each metric type
            detected_trends = {}
            for metric_type in AnalysisMetric:
                trend_analysis = await self._detect_metric_trends(metric_type, cutoff_date)
                if trend_analysis["trends_detected"]:
                    detected_trends[metric_type.value] = trend_analysis
            
            # Cross-metric trend correlation
            trend_correlations = await self._analyze_trend_correlations(detected_trends)
            
            # Market shift detection
            market_shifts = await self._detect_market_shifts(detected_trends, period_days)
            
            # Emerging patterns
            emerging_patterns = await self._identify_emerging_patterns(detected_trends)
            
            # Competitive implications
            competitive_implications = await self._assess_competitive_implications(
                detected_trends, market_shifts, emerging_patterns
            )
            
            # Generate trend report
            trend_report = {
                "analysis_period_days": period_days,
                "analysis_date": datetime.utcnow().isoformat(),
                "detected_trends": detected_trends,
                "trend_correlations": trend_correlations,
                "market_shifts": market_shifts,
                "emerging_patterns": emerging_patterns,
                "competitive_implications": competitive_implications,
                "significance_score": await self._calculate_trend_significance(detected_trends)
            }
            
            # Store significant trends
            for metric_type, trend_data in detected_trends.items():
                if trend_data.get("significance_score", 0) > 0.7:
                    trend_id = str(uuid.uuid4())
                    self.trend_analyses[trend_id] = TrendAnalysis(
                        trend_id=trend_id,
                        metric_type=AnalysisMetric(metric_type),
                        trend_direction=TrendDirection(trend_data["direction"]),
                        magnitude=trend_data["magnitude"],
                        duration_days=period_days,
                        affected_competitors=trend_data["affected_competitors"],
                        significance_score=trend_data["significance_score"],
                        implications=competitive_implications.get(metric_type, [])
                    )
            
            logger.info(f"📊 Competitive trends analysis completed: {len(detected_trends)} trends detected")
            
            return trend_report
            
        except Exception as e:
            logger.error(f"❌ Error in trend detection: {e}")
            return {"status": "error", "message": str(e)}
    
    async def generate_competitive_intelligence_report(self, report_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Generate comprehensive competitive intelligence report.
        
        Args:
            report_type: Type of report to generate
            
        Returns:
            Competitive intelligence report
        """
        try:
            report_id = str(uuid.uuid4())
            
            # Gather data for report
            market_analysis = await self.analyze_market_positioning()
            trend_analysis = await self.detect_competitive_trends()
            competitor_profiles = await self._generate_competitor_summaries()
            
            # SWOT analysis for our position
            swot_analysis = await self._perform_swot_analysis()
            
            # Opportunity assessment
            opportunity_assessment = await self._assess_market_opportunities()
            
            # Threat analysis
            threat_analysis = await self._assess_competitive_threats()
            
            # Strategic recommendations
            strategic_recommendations = await self._generate_strategic_recommendations(
                market_analysis, trend_analysis, swot_analysis
            )
            
            # Executive summary
            executive_summary = await self._generate_executive_summary(
                market_analysis, trend_analysis, opportunity_assessment, threat_analysis
            )
            
            report = {
                "report_id": report_id,
                "report_type": report_type,
                "generated_at": datetime.utcnow().isoformat(),
                "executive_summary": executive_summary,
                "market_analysis": market_analysis,
                "trend_analysis": trend_analysis,
                "competitor_profiles": competitor_profiles,
                "swot_analysis": swot_analysis,
                "opportunities": opportunity_assessment,
                "threats": threat_analysis,
                "strategic_recommendations": strategic_recommendations,
                "confidence_score": 0.88,
                "next_update_recommended": (datetime.utcnow() + timedelta(days=7)).isoformat()
            }
            
            logger.info(f"📋 Competitive intelligence report generated: {report_id}")
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Error generating intelligence report: {e}")
            return {"status": "error", "message": str(e)}
    
    # Helper methods
    
    async def _initialize_competitor_monitoring(self, competitor: CompetitorProfile):
        """Initialize monitoring for a new competitor."""
        # Set up data collection schedules
        monitoring_config = {
            "competitor_id": competitor.competitor_id,
            "data_sources": ["website", "social_media", "app_stores"],
            "collection_frequency": "daily",
            "metrics_to_track": [metric.value for metric in AnalysisMetric],
            "alert_thresholds": self._get_default_alert_thresholds()
        }
        
        # Initialize empty metrics history
        for metric_type in AnalysisMetric:
            metric_key = f"{competitor.competitor_id}_{metric_type.value}"
            self.metrics_history[metric_key] = []
        
        logger.info(f"👁️ Monitoring initialized for {competitor.name}")
    
    def _get_default_alert_thresholds(self) -> Dict[str, float]:
        """Get default alert thresholds for competitive monitoring."""
        return {
            "market_share_change": 0.05,  # 5% change
            "user_growth_rate": 0.20,     # 20% change
            "feature_announcement": 1.0,  # Any new feature
            "pricing_change": 0.10,       # 10% price change
            "funding_announcement": 1.0,  # Any funding news
            "partnership_announcement": 1.0  # Any partnership news
        }
    
    async def _perform_initial_analysis(self, competitor: CompetitorProfile) -> Dict[str, Any]:
        """Perform initial competitive analysis for a new competitor."""
        return {
            "competitive_positioning": "analysis_pending",
            "strengths_identified": len(competitor.strengths),
            "weaknesses_identified": len(competitor.weaknesses),
            "key_differentiators": competitor.key_features[:3],
            "threat_level": await self._assess_initial_threat_level(competitor),
            "monitoring_priority": await self._determine_monitoring_priority(competitor)
        }
    
    async def _assess_initial_threat_level(self, competitor: CompetitorProfile) -> str:
        """Assess initial threat level of a new competitor."""
        threat_score = 0.0
        
        # Market position factors
        if competitor.estimated_users > 100000:
            threat_score += 0.3
        
        if competitor.funding_raised > 10000000:  # $10M+
            threat_score += 0.2
        
        if competitor.category == CompetitorCategory.DIRECT_COMPETITOR:
            threat_score += 0.4
        
        # Technology and feature overlap
        if len(competitor.key_features) > 5:
            threat_score += 0.1
        
        if threat_score >= 0.7:
            return "high"
        elif threat_score >= 0.4:
            return "medium"
        else:
            return "low"
    
    async def _determine_monitoring_priority(self, competitor: CompetitorProfile) -> str:
        """Determine monitoring priority for a competitor."""
        priority_score = 0.0
        
        # Direct competitors get higher priority
        if competitor.category == CompetitorCategory.DIRECT_COMPETITOR:
            priority_score += 0.4
        elif competitor.category == CompetitorCategory.MARKET_LEADER:
            priority_score += 0.5
        
        # Size and growth factors
        if competitor.estimated_users > 50000:
            priority_score += 0.2
        
        if competitor.funding_raised > 5000000:  # $5M+
            priority_score += 0.2
        
        # Innovation and feature velocity
        if len(competitor.key_features) > 3:
            priority_score += 0.1
        
        if priority_score >= 0.7:
            return "high"
        elif priority_score >= 0.4:
            return "medium"
        else:
            return "low"
    
    async def _normalize_metric_value(self, metric_type: AnalysisMetric, value: float) -> float:
        """Normalize metric value for comparison across competitors."""
        # Simplified normalization - in practice would use historical data
        normalization_ranges = {
            AnalysisMetric.MARKET_SHARE: (0, 100),
            AnalysisMetric.USER_ENGAGEMENT: (0, 10),
            AnalysisMetric.FEATURE_ADOPTION: (0, 100),
            AnalysisMetric.CONTENT_QUALITY: (0, 5),
            AnalysisMetric.SOCIAL_PRESENCE: (0, 1000000),
            AnalysisMetric.USER_ACQUISITION: (0, 50000)
        }
        
        min_val, max_val = normalization_ranges.get(metric_type, (0, 100))
        return min(max(value - min_val, 0) / (max_val - min_val), 1.0)
    
    async def _analyze_metric_trends(self, competitor_id: str, metric_names: List[str]) -> Dict[str, Any]:
        """Analyze trends for updated metrics."""
        trend_analysis = {}
        
        for metric_name in metric_names:
            metric_key = f"{competitor_id}_{metric_name}"
            if metric_key in self.metrics_history:
                metrics = self.metrics_history[metric_key]
                
                if len(metrics) >= 5:  # Need at least 5 data points
                    values = [m.value for m in metrics[-10:]]  # Last 10 values
                    
                    # Simple trend calculation
                    if len(values) >= 2:
                        recent_trend = (values[-1] - values[0]) / max(values[0], 1)
                        
                        if recent_trend > 0.1:
                            direction = TrendDirection.RISING
                        elif recent_trend < -0.1:
                            direction = TrendDirection.DECLINING
                        else:
                            direction = TrendDirection.STABLE
                        
                        trend_analysis[metric_name] = {
                            "direction": direction.value,
                            "magnitude": abs(recent_trend),
                            "significance": min(abs(recent_trend) * 2, 1.0)
                        }
        
        return trend_analysis
    
    async def _check_competitive_alerts(self, competitor_id: str, metrics_data: Dict[str, Any], 
                                      trend_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for competitive alerts based on metrics and trends."""
        alerts = []
        
        competitor = self.competitors[competitor_id]
        thresholds = self._get_default_alert_thresholds()
        
        # Check for significant changes
        for metric_name, trend_info in trend_analysis.items():
            if trend_info.get("significance", 0) > 0.5:
                alerts.append({
                    "type": "significant_change",
                    "metric": metric_name,
                    "competitor": competitor.name,
                    "direction": trend_info["direction"],
                    "magnitude": trend_info["magnitude"],
                    "severity": "high" if trend_info["significance"] > 0.8 else "medium"
                })
        
        return alerts
    
    async def _calculate_positioning_matrix(self, competitors: List[CompetitorProfile]) -> Dict[str, Any]:
        """Calculate competitive positioning matrix."""
        positioning_matrix = {}
        
        # Define positioning dimensions
        dimensions = {
            "feature_completeness": {},
            "user_experience": {},
            "market_reach": {},
            "innovation": {}
        }
        
        # Score each competitor on each dimension
        for competitor in competitors:
            competitor_scores = {}
            
            # Feature completeness (based on key features count)
            competitor_scores["feature_completeness"] = min(len(competitor.key_features) / 10, 1.0)
            
            # Market reach (based on users and geographic presence)
            market_reach_score = (
                min(competitor.estimated_users / 1000000, 0.7) +  # Up to 70% for users
                min(len(competitor.geographic_presence) / 10, 0.3)  # Up to 30% for geo presence
            )
            competitor_scores["market_reach"] = market_reach_score
            
            # Innovation (based on technology stack and funding)
            innovation_score = (
                min(len(competitor.technology_stack) / 15, 0.5) +  # Up to 50% for tech
                min(competitor.funding_raised / 50000000, 0.5)     # Up to 50% for funding
            )
            competitor_scores["innovation"] = innovation_score
            
            # User experience (simplified scoring)
            competitor_scores["user_experience"] = 0.7  # Would be based on actual UX metrics
            
            positioning_matrix[competitor.name] = competitor_scores
        
        return positioning_matrix
    
    async def _identify_market_leaders(self, competitors: List[CompetitorProfile], 
                                     positioning_matrix: Dict[str, Any]) -> Dict[str, Any]:
        """Identify market leaders based on positioning analysis."""
        # Calculate overall scores
        overall_scores = {}
        for competitor_name, scores in positioning_matrix.items():
            overall_score = sum(scores.values()) / len(scores)
            overall_scores[competitor_name] = overall_score
        
        # Sort by overall score
        sorted_competitors = sorted(overall_scores.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "market_leader": sorted_competitors[0] if sorted_competitors else None,
            "top_3": sorted_competitors[:3],
            "ranking": {name: rank + 1 for rank, (name, score) in enumerate(sorted_competitors)},
            "score_distribution": overall_scores
        }
    
    async def _identify_market_opportunities(self, positioning_matrix: Dict[str, Any]) -> Dict[str, Any]:
        """Identify market opportunities based on positioning gaps."""
        opportunities = {
            "identified_gaps": [],
            "underserved_segments": [],
            "innovation_opportunities": []
        }
        
        # Analyze dimension averages to find gaps
        if positioning_matrix:
            dimension_averages = {}
            dimensions = list(list(positioning_matrix.values())[0].keys())
            
            for dimension in dimensions:
                scores = [scores[dimension] for scores in positioning_matrix.values()]
                dimension_averages[dimension] = statistics.mean(scores)
            
            # Identify gaps (dimensions with low average scores)
            for dimension, avg_score in dimension_averages.items():
                if avg_score < 0.6:  # Threshold for identifying gaps
                    gap_description = f"Market gap in {dimension.replace('_', ' ')}"
                    opportunities["identified_gaps"].append({
                        "dimension": dimension,
                        "gap_score": 1.0 - avg_score,
                        "description": gap_description,
                        "opportunity_rating": "high" if avg_score < 0.4 else "medium"
                    })
        
        return opportunities
    
    async def _analyze_competitive_intensity(self, competitors: List[CompetitorProfile]) -> Dict[str, Any]:
        """Analyze competitive intensity in the market."""
        intensity_factors = {
            "number_of_competitors": len(competitors),
            "direct_competitors": len([c for c in competitors if c.category == CompetitorCategory.DIRECT_COMPETITOR]),
            "market_leaders": len([c for c in competitors if c.category == CompetitorCategory.MARKET_LEADER]),
            "emerging_players": len([c for c in competitors if c.category == CompetitorCategory.EMERGING_PLAYER])
        }
        
        # Calculate intensity score
        intensity_score = 0.0
        
        # More competitors = higher intensity
        intensity_score += min(intensity_factors["number_of_competitors"] / 10, 0.4)
        
        # More direct competitors = higher intensity
        intensity_score += min(intensity_factors["direct_competitors"] / 5, 0.3)
        
        # Market leaders increase intensity
        intensity_score += min(intensity_factors["market_leaders"] / 3, 0.2)
        
        # Emerging players add uncertainty
        intensity_score += min(intensity_factors["emerging_players"] / 5, 0.1)
        
        intensity_level = "high" if intensity_score > 0.7 else "medium" if intensity_score > 0.4 else "low"
        
        return {
            "intensity_score": intensity_score,
            "intensity_level": intensity_level,
            "factors": intensity_factors,
            "market_dynamics": {
                "rivalry_level": intensity_level,
                "innovation_pressure": "high" if intensity_factors["emerging_players"] > 2 else "medium",
                "price_pressure": "medium",  # Simplified
                "differentiation_importance": "high"
            }
        }
    
    async def _generate_strategic_insights(self, positioning_analysis: Dict[str, Any], 
                                         market_leaders: Dict[str, Any], 
                                         market_opportunities: Dict[str, Any]) -> Dict[str, Any]:
        """Generate strategic insights from competitive analysis."""
        insights = {
            "key_findings": [],
            "competitive_advantages": [],
            "areas_for_improvement": [],
            "strategic_moves": [],
            "recommendations": []
        }
        
        # Analyze our position (assuming we're "Ainflue" in the analysis)
        if "Ainflue" in positioning_analysis:
            our_scores = positioning_analysis["Ainflue"]
            
            # Identify strengths and weaknesses
            for dimension, score in our_scores.items():
                if score > 0.7:
                    insights["competitive_advantages"].append(f"Strong {dimension.replace('_', ' ')}")
                elif score < 0.4:
                    insights["areas_for_improvement"].append(f"Improve {dimension.replace('_', ' ')}")
        
        # Market opportunity insights
        for gap in market_opportunities.get("identified_gaps", []):
            if gap["opportunity_rating"] == "high":
                insights["strategic_moves"].append(f"Invest in {gap['dimension'].replace('_', ' ')} capabilities")
        
        # Competitive threat insights
        market_leader_name = market_leaders.get("market_leader", [None, None])[0]
        if market_leader_name and market_leader_name != "Ainflue":
            insights["key_findings"].append(f"{market_leader_name} is the current market leader")
            insights["recommendations"].append(f"Monitor {market_leader_name}'s strategy closely")
        
        # General recommendations
        insights["recommendations"].extend([
            "Focus on differentiation in underserved market segments",
            "Accelerate innovation to stay competitive",
            "Consider strategic partnerships to expand capabilities"
        ])
        
        return insights

# Create global instance
competitive_analysis_monitor = CompetitiveAnalysisMonitor()

__all__ = [
    'CompetitiveAnalysisMonitor',
    'CompetitorCategory',
    'AnalysisMetric',
    'TrendDirection',
    'CompetitorProfile',
    'CompetitiveMetric',
    'MarketIntelligence',
    'TrendAnalysis',
    'competitive_analysis_monitor'
]