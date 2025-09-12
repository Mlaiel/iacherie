"""MLOps User Experience Monitor - Advanced UX Monitoring with Satisfaction Tracking
Monitor d'expérience utilisateur avec tracking de satisfaction pour créateurs.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

🎯 Business Logic Integration:
Creator Interaction → UX Monitoring → Satisfaction Analysis → Experience Optimization → Business KPIs

🚀 Multi-Expert Implementation:
- Backend Senior: High-performance UX data collection and real-time analytics
- ML Engineer: ML-powered satisfaction prediction and anomaly detection
- UX/UI Expert: Experience metrics and journey optimization
- DevOps: Performance monitoring and user session tracking
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
from collections import defaultdict, deque

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InteractionType(Enum):
    """Types d'interactions utilisateur."""
    PAGE_VIEW = "page_view"
    CONTENT_UPLOAD = "content_upload"
    CONTENT_DISCOVERY = "content_discovery"
    SEARCH_ACTION = "search_action"
    COLLABORATION_ACTION = "collaboration_action"
    PAYMENT_ACTION = "payment_action"
    SETTINGS_CHANGE = "settings_change"
    SOCIAL_INTERACTION = "social_interaction"
    AI_INTERACTION = "ai_interaction"

class SatisfactionLevel(Enum):
    """Niveaux de satisfaction utilisateur."""
    VERY_SATISFIED = "very_satisfied"
    SATISFIED = "satisfied"
    NEUTRAL = "neutral"
    DISSATISFIED = "dissatisfied"
    VERY_DISSATISFIED = "very_dissatisfied"

class UXMetricType(Enum):
    """Types de métriques UX."""
    RESPONSE_TIME = "response_time"
    ERROR_RATE = "error_rate"
    TASK_COMPLETION_RATE = "task_completion_rate"
    TIME_TO_COMPLETE = "time_to_complete"
    BOUNCE_RATE = "bounce_rate"
    SESSION_DURATION = "session_duration"
    CLICKS_TO_GOAL = "clicks_to_goal"
    SATISFACTION_SCORE = "satisfaction_score"

@dataclass
class UserInteraction:
    """Interaction utilisateur pour monitoring UX."""
    interaction_id: str
    user_id: str
    creator_type: str
    interaction_type: InteractionType
    timestamp: datetime
    page_url: str
    session_id: str
    response_time_ms: float
    success: bool
    error_message: Optional[str] = None
    additional_data: Dict[str, Any] = None

@dataclass
class UXMetric:
    """Métrique d'expérience utilisateur."""
    metric_id: str
    user_id: str
    creator_type: str
    metric_type: UXMetricType
    value: float
    timestamp: datetime
    session_id: str
    page_context: str
    satisfaction_impact: float  # -1.0 to 1.0

@dataclass
class SatisfactionFeedback:
    """Feedback de satisfaction utilisateur."""
    feedback_id: str
    user_id: str
    creator_type: str
    satisfaction_level: SatisfactionLevel
    satisfaction_score: float  # 1-10 scale
    feedback_text: Optional[str]
    timestamp: datetime
    interaction_context: str
    improvement_suggestions: List[str]

@dataclass
class UXInsight:
    """Insight d'expérience utilisateur."""
    insight_id: str
    insight_type: str
    creator_segments_affected: List[str]
    severity: str  # "low", "medium", "high", "critical"
    description: str
    metrics_involved: List[str]
    recommended_actions: List[str]
    confidence_score: float
    estimated_impact: str

class UserExperienceMonitor:
    """Monitor enterprise d'expérience utilisateur avec IA prédictive."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize user experience monitor."""
        self.config = self._load_config(config_path)
        self.interactions: List[UserInteraction] = []
        self.ux_metrics: List[UXMetric] = []
        self.satisfaction_feedback: List[SatisfactionFeedback] = []
        self.ux_insights: List[UXInsight] = []
        
        # Real-time monitoring data structures
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.real_time_metrics: deque = deque(maxlen=1000)
        
        # Creator segment UX baselines
        self.creator_ux_baselines = {
            "musicians": {
                "expected_response_time_ms": 100,
                "target_satisfaction_score": 8.5,
                "max_acceptable_error_rate": 0.02,
                "target_task_completion_rate": 0.95
            },
            "photographers": {
                "expected_response_time_ms": 150,
                "target_satisfaction_score": 8.2,
                "max_acceptable_error_rate": 0.03,
                "target_task_completion_rate": 0.92
            },
            "bloggers": {
                "expected_response_time_ms": 200,
                "target_satisfaction_score": 8.0,
                "max_acceptable_error_rate": 0.04,
                "target_task_completion_rate": 0.90
            },
            "influencers": {
                "expected_response_time_ms": 80,
                "target_satisfaction_score": 9.0,
                "max_acceptable_error_rate": 0.01,
                "target_task_completion_rate": 0.98
            },
            "comedians": {
                "expected_response_time_ms": 120,
                "target_satisfaction_score": 8.3,
                "max_acceptable_error_rate": 0.025,
                "target_task_completion_rate": 0.93
            }
        }
        
        # Satisfaction prediction model coefficients
        self.satisfaction_model_weights = {
            "response_time_weight": -0.3,
            "error_rate_weight": -0.5,
            "task_completion_weight": 0.4,
            "session_duration_weight": 0.2,
            "feature_usage_weight": 0.1
        }
        
        logger.info("👥 UserExperienceMonitor enterprise initialized with ML satisfaction prediction")

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load UX monitor configuration."""
        default_config = {
            "monitoring_settings": {
                "real_time_tracking": True,
                "satisfaction_prediction_enabled": True,
                "anomaly_detection_enabled": True,
                "session_tracking_enabled": True
            },
            "alert_thresholds": {
                "critical_response_time_ms": 5000,
                "high_error_rate": 0.10,
                "low_satisfaction_score": 5.0,
                "critical_satisfaction_drop": 2.0
            },
            "data_retention": {
                "interaction_retention_days": 90,
                "metrics_retention_days": 180,
                "feedback_retention_days": 365
            },
            "ml_settings": {
                "satisfaction_prediction_threshold": 0.80,
                "anomaly_detection_sensitivity": 0.85,
                "insight_generation_interval_minutes": 15
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

    async def track_user_interaction(self,
                                   user_id: str,
                                   creator_type: str,
                                   interaction_type: InteractionType,
                                   page_url: str,
                                   session_id: str,
                                   response_time_ms: float,
                                   success: bool,
                                   error_message: Optional[str] = None,
                                   additional_data: Optional[Dict[str, Any]] = None) -> str:
        """Tracker une interaction utilisateur."""
        try:
            interaction_id = f"int_{int(time.time())}_{user_id[:8]}"
            
            interaction = UserInteraction(
                interaction_id=interaction_id,
                user_id=user_id,
                creator_type=creator_type,
                interaction_type=interaction_type,
                timestamp=datetime.now(),
                page_url=page_url,
                session_id=session_id,
                response_time_ms=response_time_ms,
                success=success,
                error_message=error_message,
                additional_data=additional_data or {}
            )
            
            self.interactions.append(interaction)
            self.real_time_metrics.append({
                "type": "interaction",
                "data": interaction,
                "timestamp": time.time()
            })
            
            # Update active session
            await self._update_session_data(session_id, interaction)
            
            # Generate UX metrics from interaction
            await self._generate_ux_metrics_from_interaction(interaction)
            
            # Check for real-time alerts
            await self._check_real_time_alerts(interaction)
            
            logger.debug(f"📊 Tracked interaction: {interaction_type.value} for {creator_type} "
                        f"(response: {response_time_ms:.1f}ms, success: {success})")
            
            return interaction_id
            
        except Exception as e:
            logger.error(f"❌ Error tracking user interaction: {e}")
            return ""

    async def _update_session_data(self, session_id: str, interaction: UserInteraction) -> None:
        """Mettre à jour les données de session."""
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = {
                "start_time": interaction.timestamp,
                "user_id": interaction.user_id,
                "creator_type": interaction.creator_type,
                "interaction_count": 0,
                "total_response_time": 0.0,
                "error_count": 0,
                "pages_visited": set(),
                "last_activity": interaction.timestamp
            }
        
        session = self.active_sessions[session_id]
        session["interaction_count"] += 1
        session["total_response_time"] += interaction.response_time_ms
        session["last_activity"] = interaction.timestamp
        session["pages_visited"].add(interaction.page_url)
        
        if not interaction.success:
            session["error_count"] += 1

    async def _generate_ux_metrics_from_interaction(self, interaction: UserInteraction) -> None:
        """Générer des métriques UX à partir d'une interaction."""
        
        # Response time metric
        response_time_metric = UXMetric(
            metric_id=f"rt_{interaction.interaction_id}",
            user_id=interaction.user_id,
            creator_type=interaction.creator_type,
            metric_type=UXMetricType.RESPONSE_TIME,
            value=interaction.response_time_ms,
            timestamp=interaction.timestamp,
            session_id=interaction.session_id,
            page_context=interaction.page_url,
            satisfaction_impact=await self._calculate_satisfaction_impact(
                UXMetricType.RESPONSE_TIME, interaction.response_time_ms, interaction.creator_type
            )
        )
        
        self.ux_metrics.append(response_time_metric)
        
        # Error rate contribution
        if not interaction.success:
            error_metric = UXMetric(
                metric_id=f"err_{interaction.interaction_id}",
                user_id=interaction.user_id,
                creator_type=interaction.creator_type,
                metric_type=UXMetricType.ERROR_RATE,
                value=1.0,  # Error occurred
                timestamp=interaction.timestamp,
                session_id=interaction.session_id,
                page_context=interaction.page_url,
                satisfaction_impact=-0.8  # Errors significantly impact satisfaction
            )
            
            self.ux_metrics.append(error_metric)

    async def _calculate_satisfaction_impact(self,
                                           metric_type: UXMetricType,
                                           value: float,
                                           creator_type: str) -> float:
        """Calculer l'impact sur la satisfaction d'une métrique."""
        
        baseline = self.creator_ux_baselines.get(creator_type, self.creator_ux_baselines["bloggers"])
        
        if metric_type == UXMetricType.RESPONSE_TIME:
            expected = baseline["expected_response_time_ms"]
            # Negative impact increases exponentially with response time
            if value <= expected:
                return 0.1  # Slight positive impact for fast responses
            else:
                ratio = value / expected
                return max(-1.0, -0.3 * (ratio - 1) ** 1.5)
        
        elif metric_type == UXMetricType.ERROR_RATE:
            return -0.8  # Errors always have high negative impact
        
        elif metric_type == UXMetricType.TASK_COMPLETION_RATE:
            return 0.6 if value == 1.0 else -0.4
        
        else:
            return 0.0

    async def _check_real_time_alerts(self, interaction: UserInteraction) -> None:
        """Vérifier les alertes en temps réel."""
        alerts = []
        
        # Response time alert
        if interaction.response_time_ms > self.config["alert_thresholds"]["critical_response_time_ms"]:
            alerts.append(f"Critical response time: {interaction.response_time_ms:.1f}ms")
        
        # Error alert
        if not interaction.success:
            alerts.append(f"User error: {interaction.error_message or 'Unknown error'}")
        
        # Send alerts if any
        for alert in alerts:
            logger.warning(f"🚨 UX Alert: {alert} for {interaction.creator_type} user {interaction.user_id}")

    async def record_satisfaction_feedback(self,
                                         user_id: str,
                                         creator_type: str,
                                         satisfaction_level: SatisfactionLevel,
                                         satisfaction_score: float,
                                         feedback_text: Optional[str] = None,
                                         interaction_context: str = "",
                                         improvement_suggestions: Optional[List[str]] = None) -> str:
        """Enregistrer un feedback de satisfaction utilisateur."""
        try:
            feedback_id = f"fb_{int(time.time())}_{user_id[:8]}"
            
            feedback = SatisfactionFeedback(
                feedback_id=feedback_id,
                user_id=user_id,
                creator_type=creator_type,
                satisfaction_level=satisfaction_level,
                satisfaction_score=satisfaction_score,
                feedback_text=feedback_text,
                timestamp=datetime.now(),
                interaction_context=interaction_context,
                improvement_suggestions=improvement_suggestions or []
            )
            
            self.satisfaction_feedback.append(feedback)
            
            # Create satisfaction metric
            satisfaction_metric = UXMetric(
                metric_id=f"sat_{feedback_id}",
                user_id=user_id,
                creator_type=creator_type,
                metric_type=UXMetricType.SATISFACTION_SCORE,
                value=satisfaction_score,
                timestamp=feedback.timestamp,
                session_id="",  # Not tied to specific session
                page_context=interaction_context,
                satisfaction_impact=1.0  # Direct satisfaction measurement
            )
            
            self.ux_metrics.append(satisfaction_metric)
            
            # Check for low satisfaction alerts
            if satisfaction_score <= self.config["alert_thresholds"]["low_satisfaction_score"]:
                logger.warning(f"🚨 Low satisfaction alert: {satisfaction_score}/10 from {creator_type} user")
            
            logger.info(f"💬 Recorded satisfaction feedback: {satisfaction_score}/10 "
                       f"({satisfaction_level.value}) from {creator_type}")
            
            return feedback_id
            
        except Exception as e:
            logger.error(f"❌ Error recording satisfaction feedback: {e}")
            return ""

    async def predict_user_satisfaction(self, user_id: str, session_id: str) -> Dict[str, Any]:
        """Prédire la satisfaction utilisateur en temps réel."""
        try:
            # Get recent metrics for user/session
            recent_metrics = [
                m for m in self.ux_metrics
                if (m.user_id == user_id or m.session_id == session_id) and
                   m.timestamp > datetime.now() - timedelta(minutes=30)
            ]
            
            if not recent_metrics:
                return {"predicted_satisfaction": 7.0, "confidence": 0.5, "factors": []}
            
            # Calculate weighted satisfaction prediction
            total_impact = 0.0
            total_weight = 0.0
            contributing_factors = []
            
            # Group metrics by type
            metrics_by_type = defaultdict(list)
            for metric in recent_metrics:
                metrics_by_type[metric.metric_type].append(metric)
            
            # Calculate impacts for each metric type
            for metric_type, metrics in metrics_by_type.items():
                avg_value = statistics.mean([m.value for m in metrics])
                avg_impact = statistics.mean([m.satisfaction_impact for m in metrics])
                
                weight = self.satisfaction_model_weights.get(f"{metric_type.value}_weight", 0.1)
                
                contribution = avg_impact * weight
                total_impact += contribution
                total_weight += abs(weight)
                
                contributing_factors.append({
                    "factor": metric_type.value,
                    "average_value": avg_value,
                    "impact": avg_impact,
                    "contribution": contribution
                })
            
            # Base satisfaction score (neutral)
            base_satisfaction = 7.0
            
            # Apply impact (scale from -3 to +3)
            normalized_impact = (total_impact / total_weight) * 3 if total_weight > 0 else 0
            predicted_satisfaction = base_satisfaction + normalized_impact
            
            # Clamp to valid range
            predicted_satisfaction = max(1.0, min(10.0, predicted_satisfaction))
            
            # Calculate confidence based on data availability
            confidence = min(0.95, 0.5 + (len(recent_metrics) / 20))
            
            prediction = {
                "predicted_satisfaction": round(predicted_satisfaction, 1),
                "confidence": round(confidence, 2),
                "contributing_factors": contributing_factors,
                "data_points_used": len(recent_metrics),
                "prediction_timestamp": datetime.now().isoformat()
            }
            
            logger.debug(f"🔮 Predicted satisfaction for {user_id}: {predicted_satisfaction:.1f}/10 "
                        f"(confidence: {confidence:.2f})")
            
            return prediction
            
        except Exception as e:
            logger.error(f"❌ Error predicting user satisfaction: {e}")
            return {"predicted_satisfaction": 7.0, "confidence": 0.0, "factors": []}

    async def analyze_creator_segment_ux(self, creator_type: str) -> Dict[str, Any]:
        """Analyser l'UX pour un segment de créateurs."""
        try:
            # Get metrics for this creator type
            creator_metrics = [m for m in self.ux_metrics if m.creator_type == creator_type]
            creator_feedback = [f for f in self.satisfaction_feedback if f.creator_type == creator_type]
            
            if not creator_metrics:
                return {"error": f"No UX data available for {creator_type}"}
            
            # Calculate key UX metrics
            response_times = [m.value for m in creator_metrics if m.metric_type == UXMetricType.RESPONSE_TIME]
            error_metrics = [m for m in creator_metrics if m.metric_type == UXMetricType.ERROR_RATE]
            satisfaction_scores = [f.satisfaction_score for f in creator_feedback]
            
            baseline = self.creator_ux_baselines.get(creator_type, self.creator_ux_baselines["bloggers"])
            
            # Calculate performance vs baselines
            avg_response_time = statistics.mean(response_times) if response_times else 0
            error_rate = len(error_metrics) / len(creator_metrics) if creator_metrics else 0
            avg_satisfaction = statistics.mean(satisfaction_scores) if satisfaction_scores else 7.0
            
            # Performance assessment
            response_time_performance = "good" if avg_response_time <= baseline["expected_response_time_ms"] else "poor"
            error_rate_performance = "good" if error_rate <= baseline["max_acceptable_error_rate"] else "poor"
            satisfaction_performance = "good" if avg_satisfaction >= baseline["target_satisfaction_score"] else "poor"
            
            # Recent trend analysis (last 7 days vs previous 7 days)
            cutoff_date = datetime.now() - timedelta(days=7)
            recent_satisfaction = [f.satisfaction_score for f in creator_feedback if f.timestamp >= cutoff_date]
            older_satisfaction = [f.satisfaction_score for f in creator_feedback if f.timestamp < cutoff_date]
            
            satisfaction_trend = "stable"
            if recent_satisfaction and older_satisfaction:
                recent_avg = statistics.mean(recent_satisfaction)
                older_avg = statistics.mean(older_satisfaction)
                diff = recent_avg - older_avg
                
                if diff > 0.5:
                    satisfaction_trend = "improving"
                elif diff < -0.5:
                    satisfaction_trend = "declining"
            
            # Top pain points from feedback
            pain_points = []
            improvement_suggestions = []
            
            for feedback in creator_feedback:
                if feedback.satisfaction_score < 6.0 and feedback.feedback_text:
                    pain_points.append(feedback.feedback_text)
                
                improvement_suggestions.extend(feedback.improvement_suggestions)
            
            # Common improvement suggestions
            suggestion_counts = defaultdict(int)
            for suggestion in improvement_suggestions:
                suggestion_counts[suggestion] += 1
            
            top_suggestions = sorted(suggestion_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            analysis = {
                "creator_type": creator_type,
                "performance_summary": {
                    "average_response_time_ms": round(avg_response_time, 1),
                    "response_time_vs_baseline": response_time_performance,
                    "error_rate_percentage": round(error_rate * 100, 2),
                    "error_rate_vs_baseline": error_rate_performance,
                    "average_satisfaction_score": round(avg_satisfaction, 1),
                    "satisfaction_vs_baseline": satisfaction_performance,
                    "satisfaction_trend": satisfaction_trend
                },
                "baseline_comparison": {
                    "expected_response_time_ms": baseline["expected_response_time_ms"],
                    "target_satisfaction_score": baseline["target_satisfaction_score"],
                    "max_acceptable_error_rate": baseline["max_acceptable_error_rate"]
                },
                "data_summary": {
                    "total_interactions": len([i for i in self.interactions if i.creator_type == creator_type]),
                    "total_ux_metrics": len(creator_metrics),
                    "satisfaction_feedback_count": len(creator_feedback),
                    "analysis_period_days": 30
                },
                "top_improvement_suggestions": [{"suggestion": s[0], "frequency": s[1]} for s in top_suggestions],
                "recent_pain_points": pain_points[-5:] if pain_points else []
            }
            
            logger.info(f"📊 UX Analysis for {creator_type}: {avg_satisfaction:.1f}/10 satisfaction, "
                       f"{avg_response_time:.1f}ms avg response time, {error_rate:.2%} error rate")
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error analyzing creator segment UX: {e}")
            return {"error": str(e)}

    async def generate_ux_insights(self) -> List[UXInsight]:
        """Générer des insights UX automatisés."""
        try:
            insights = []
            insight_counter = 0
            
            # Analyze each creator segment
            for creator_type in ["musicians", "photographers", "bloggers", "influencers", "comedians"]:
                analysis = await self.analyze_creator_segment_ux(creator_type)
                
                if "error" in analysis:
                    continue
                
                perf = analysis.get("performance_summary", {})
                baseline = analysis.get("baseline_comparison", {})
                
                # High response time insight
                if perf.get("response_time_vs_baseline") == "poor":
                    insight_counter += 1
                    insights.append(UXInsight(
                        insight_id=f"insight_{insight_counter}",
                        insight_type="performance_degradation",
                        creator_segments_affected=[creator_type],
                        severity="high",
                        description=f"{creator_type} experiencing slow response times: "
                                  f"{perf.get('average_response_time_ms', 0):.1f}ms vs "
                                  f"{baseline.get('expected_response_time_ms', 0)}ms baseline",
                        metrics_involved=["response_time"],
                        recommended_actions=[
                            "Optimize server performance",
                            "Implement caching strategies",
                            "Review database query performance"
                        ],
                        confidence_score=0.85,
                        estimated_impact="medium"
                    ))
                
                # Low satisfaction insight
                if perf.get("satisfaction_vs_baseline") == "poor":
                    insight_counter += 1
                    insights.append(UXInsight(
                        insight_id=f"insight_{insight_counter}",
                        insight_type="satisfaction_decline",
                        creator_segments_affected=[creator_type],
                        severity="high" if perf.get("average_satisfaction_score", 7) < 5.0 else "medium",
                        description=f"{creator_type} satisfaction below target: "
                                  f"{perf.get('average_satisfaction_score', 0):.1f}/10 vs "
                                  f"{baseline.get('target_satisfaction_score', 8.0)}/10 target",
                        metrics_involved=["satisfaction_score"],
                        recommended_actions=[
                            "Review user feedback for specific pain points",
                            "Implement suggested improvements",
                            "Conduct user interviews",
                            "A/B test interface improvements"
                        ],
                        confidence_score=0.90,
                        estimated_impact="high"
                    ))
                
                # Declining satisfaction trend
                if perf.get("satisfaction_trend") == "declining":
                    insight_counter += 1
                    insights.append(UXInsight(
                        insight_id=f"insight_{insight_counter}",
                        insight_type="negative_trend",
                        creator_segments_affected=[creator_type],
                        severity="medium",
                        description=f"{creator_type} satisfaction showing declining trend over last 7 days",
                        metrics_involved=["satisfaction_score"],
                        recommended_actions=[
                            "Investigate recent changes or incidents",
                            "Monitor user feedback closely",
                            "Consider rolling back recent changes"
                        ],
                        confidence_score=0.75,
                        estimated_impact="medium"
                    ))
            
            # Cross-segment insights
            all_satisfaction = [f.satisfaction_score for f in self.satisfaction_feedback]
            if all_satisfaction:
                avg_overall_satisfaction = statistics.mean(all_satisfaction)
                
                if avg_overall_satisfaction < 6.0:
                    insight_counter += 1
                    insights.append(UXInsight(
                        insight_id=f"insight_{insight_counter}",
                        insight_type="platform_wide_issue",
                        creator_segments_affected=["all"],
                        severity="critical",
                        description=f"Platform-wide satisfaction critically low: {avg_overall_satisfaction:.1f}/10",
                        metrics_involved=["satisfaction_score"],
                        recommended_actions=[
                            "Emergency UX review required",
                            "Identify and fix critical issues immediately",
                            "Increase support capacity",
                            "Communicate with users about improvements"
                        ],
                        confidence_score=0.95,
                        estimated_impact="critical"
                    ))
            
            self.ux_insights.extend(insights)
            
            logger.info(f"🧠 Generated {len(insights)} UX insights")
            return insights
            
        except Exception as e:
            logger.error(f"❌ Error generating UX insights: {e}")
            return []

    async def export_ux_report(self, format_type: str = "json") -> str:
        """Exporter un rapport UX complet."""
        try:
            # Generate insights
            insights = await self.generate_ux_insights()
            
            # Analyze all creator segments
            segment_analyses = {}
            for creator_type in ["musicians", "photographers", "bloggers", "influencers", "comedians"]:
                analysis = await self.analyze_creator_segment_ux(creator_type)
                if "error" not in analysis:
                    segment_analyses[creator_type] = analysis
            
            # Overall statistics
            total_interactions = len(self.interactions)
            total_metrics = len(self.ux_metrics)
            total_feedback = len(self.satisfaction_feedback)
            
            avg_satisfaction = statistics.mean([f.satisfaction_score for f in self.satisfaction_feedback]) if self.satisfaction_feedback else 0
            
            report_data = {
                "report_metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "report_type": "user_experience_analysis",
                    "monitoring_period": "last_30_days",
                    "total_data_points": total_interactions + total_metrics + total_feedback
                },
                "executive_summary": {
                    "overall_satisfaction_score": round(avg_satisfaction, 1),
                    "total_user_interactions": total_interactions,
                    "total_ux_metrics": total_metrics,
                    "satisfaction_feedback_count": total_feedback,
                    "insights_generated": len(insights),
                    "critical_issues": len([i for i in insights if i.severity == "critical"])
                },
                "creator_segment_analysis": segment_analyses,
                "ux_insights": [
                    {
                        **asdict(insight),
                        "creator_segments_affected": insight.creator_segments_affected
                    } for insight in insights
                ],
                "satisfaction_distribution": self._calculate_satisfaction_distribution(),
                "performance_trends": await self._calculate_performance_trends()
            }
            
            # Export to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"/tmp/ux_analysis_report_{timestamp}.{format_type}"
            
            async with aiofiles.open(filename, 'w') as f:
                await f.write(json.dumps(report_data, indent=2, default=str))
            
            logger.info(f"📊 UX analysis report exported to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"❌ Error exporting UX report: {e}")
            return ""

    def _calculate_satisfaction_distribution(self) -> Dict[str, int]:
        """Calculer la distribution des niveaux de satisfaction."""
        distribution = {level.value: 0 for level in SatisfactionLevel}
        
        for feedback in self.satisfaction_feedback:
            distribution[feedback.satisfaction_level.value] += 1
        
        return distribution

    async def _calculate_performance_trends(self) -> Dict[str, Any]:
        """Calculer les tendances de performance."""
        try:
            now = datetime.now()
            week_ago = now - timedelta(days=7)
            two_weeks_ago = now - timedelta(days=14)
            
            # Recent week metrics
            recent_metrics = [m for m in self.ux_metrics if m.timestamp >= week_ago]
            previous_metrics = [m for m in self.ux_metrics if two_weeks_ago <= m.timestamp < week_ago]
            
            trends = {}
            
            for metric_type in UXMetricType:
                recent_values = [m.value for m in recent_metrics if m.metric_type == metric_type]
                previous_values = [m.value for m in previous_metrics if m.metric_type == metric_type]
                
                if recent_values and previous_values:
                    recent_avg = statistics.mean(recent_values)
                    previous_avg = statistics.mean(previous_values)
                    
                    change_pct = ((recent_avg - previous_avg) / previous_avg * 100) if previous_avg != 0 else 0
                    
                    trends[metric_type.value] = {
                        "recent_average": round(recent_avg, 2),
                        "previous_average": round(previous_avg, 2),
                        "change_percentage": round(change_pct, 1),
                        "trend": "improving" if change_pct > 5 else "declining" if change_pct < -5 else "stable"
                    }
            
            return trends
            
        except Exception as e:
            logger.error(f"Error calculating performance trends: {e}")
            return {}

# Example usage and testing
async def main():
    """Example usage of user experience monitor."""
    print("👥 MLOps User Experience Monitor - Enterprise Demo")
    print("="*60)
    
    # Create UX monitor
    ux_monitor = UserExperienceMonitor()
    
    # Simulate user interactions
    print("\n📊 Tracking user interactions...")
    
    # Musician interactions
    await ux_monitor.track_user_interaction(
        user_id="musician_001",
        creator_type="musicians",
        interaction_type=InteractionType.CONTENT_UPLOAD,
        page_url="/upload/audio",
        session_id="session_001",
        response_time_ms=120.5,
        success=True
    )
    
    await ux_monitor.track_user_interaction(
        user_id="musician_001",
        creator_type="musicians",
        interaction_type=InteractionType.AI_INTERACTION,
        page_url="/ai/enhancement",
        session_id="session_001",
        response_time_ms=250.0,
        success=False,
        error_message="AI processing timeout"
    )
    
    # Photographer interactions
    await ux_monitor.track_user_interaction(
        user_id="photographer_001",
        creator_type="photographers",
        interaction_type=InteractionType.CONTENT_DISCOVERY,
        page_url="/discover/photos",
        session_id="session_002",
        response_time_ms=95.3,
        success=True
    )
    
    print(f"   Tracked {len(ux_monitor.interactions)} user interactions")
    
    # Record satisfaction feedback
    print(f"\n💬 Recording satisfaction feedback...")
    
    await ux_monitor.record_satisfaction_feedback(
        user_id="musician_001",
        creator_type="musicians",
        satisfaction_level=SatisfactionLevel.DISSATISFIED,
        satisfaction_score=4.0,
        feedback_text="AI processing is too slow and unreliable",
        interaction_context="ai_enhancement",
        improvement_suggestions=["Improve AI response time", "Add better error handling"]
    )
    
    await ux_monitor.record_satisfaction_feedback(
        user_id="photographer_001",
        creator_type="photographers",
        satisfaction_level=SatisfactionLevel.SATISFIED,
        satisfaction_score=8.5,
        feedback_text="Love the new discovery features",
        interaction_context="content_discovery"
    )
    
    print(f"   Recorded {len(ux_monitor.satisfaction_feedback)} satisfaction feedback entries")
    
    # Predict satisfaction
    print(f"\n🔮 Predicting user satisfaction...")
    
    prediction = await ux_monitor.predict_user_satisfaction("musician_001", "session_001")
    print(f"   Musician satisfaction prediction: {prediction['predicted_satisfaction']}/10 "
          f"(confidence: {prediction['confidence']:.2f})")
    
    # Analyze creator segments
    print(f"\n📊 Analyzing creator segment UX...")
    
    for segment in ["musicians", "photographers"]:
        analysis = await ux_monitor.analyze_creator_segment_ux(segment)
        if "error" not in analysis:
            perf = analysis["performance_summary"]
            print(f"   {segment}: {perf['average_satisfaction_score']:.1f}/10 satisfaction, "
                  f"{perf['average_response_time_ms']:.1f}ms response time")
    
    # Generate UX insights
    print(f"\n🧠 Generating UX insights...")
    
    insights = await ux_monitor.generate_ux_insights()
    print(f"   Generated {len(insights)} insights:")
    
    for insight in insights[:3]:  # Show first 3
        print(f"   • {insight.severity.upper()}: {insight.description}")
        print(f"     Recommended: {insight.recommended_actions[0] if insight.recommended_actions else 'No actions'}")
    
    # Export UX report
    print(f"\n📊 Exporting UX analysis report...")
    report_file = await ux_monitor.export_ux_report()
    print(f"   Report exported to: {report_file}")
    
    print(f"\n✅ User experience monitoring demo complete!")

if __name__ == "__main__":
    asyncio.run(main())