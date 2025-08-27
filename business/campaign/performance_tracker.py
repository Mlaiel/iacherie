"""
Performance Tracker - Campaign Performance Monitoring and Analytics
==================================================================

Advanced performance tracking system with real-time monitoring, predictive analytics,
and comprehensive reporting for campaign effectiveness measurement.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is protected by copyright law. Unauthorized use, reproduction,
or distribution without explicit written permission from Fahed Mlaiel is strictly
prohibited and may result in legal action.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass
import asyncio
import numpy as np
from collections import defaultdict

from backend.core.logging import get_logger
from backend.ai.ml.performance_predictor import PerformancePredictor
from backend.ai.ml.anomaly_detection import AnomalyDetector
from backend.ai.analytics.trend_analyzer import TrendAnalyzer
from backend.business.analytics.kpi_calculator import KPICalculator
from backend.business.analytics.benchmark_analyzer import BenchmarkAnalyzer
from backend.integrations.analytics_platforms import AnalyticsPlatformManager
from backend.utils.data_aggregator import DataAggregator


class MetricType(str, Enum):
    """Performance metric types"""
    REACH = "reach"
    IMPRESSIONS = "impressions"
    ENGAGEMENT = "engagement"
    CLICKS = "clicks"
    CONVERSIONS = "conversions"
    REVENUE = "revenue"
    COST_PER_CLICK = "cost_per_click"
    COST_PER_ACQUISITION = "cost_per_acquisition"
    RETURN_ON_INVESTMENT = "return_on_investment"
    BRAND_AWARENESS = "brand_awareness"
    SENTIMENT_SCORE = "sentiment_score"


class TrackingFrequency(str, Enum):
    """Performance tracking frequencies"""
    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class AlertLevel(str, Enum):
    """Performance alert levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class PerformanceMetric:
    """Individual performance metric data"""
    metric_type: MetricType
    value: float
    previous_value: Optional[float]
    change_percentage: float
    timestamp: datetime
    confidence_score: float
    source_platform: str
    metadata: Dict[str, Any]


@dataclass
class PerformanceAlert:
    """Performance alert information"""
    alert_id: str
    campaign_id: str
    metric_type: MetricType
    alert_level: AlertLevel
    message: str
    current_value: float
    threshold_value: float
    triggered_at: datetime
    resolved: bool = False
    resolution_action: Optional[str] = None


@dataclass
class PerformanceBenchmark:
    """Performance benchmark data"""
    campaign_type: str
    industry: str
    benchmarks: Dict[MetricType, Dict[str, float]]
    sample_size: int
    confidence_interval: float
    last_updated: datetime


@dataclass
class PerformanceInsight:
    """AI-generated performance insight"""
    insight_id: str
    campaign_id: str
    insight_type: str
    title: str
    description: str
    impact_level: str
    confidence_score: float
    recommended_actions: List[str]
    generated_at: datetime


class PerformanceTracker:
    """
    Advanced Campaign Performance Monitoring and Analytics System
    
    Provides comprehensive performance tracking including real-time monitoring,
    predictive analytics, benchmark comparison, anomaly detection,
    and actionable insights for campaign optimization.
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.performance_predictor = PerformancePredictor()
        self.anomaly_detector = AnomalyDetector()
        self.trend_analyzer = TrendAnalyzer()
        self.kpi_calculator = KPICalculator()
        self.benchmark_analyzer = BenchmarkAnalyzer()
        self.analytics_platform_manager = AnalyticsPlatformManager()
        self.data_aggregator = DataAggregator()
        
        self._tracking_configs: Dict[str, Dict] = {}
        self._performance_data: Dict[str, List] = {}
        self._active_alerts: Dict[str, List[PerformanceAlert]] = {}
        self._benchmark_cache: Dict[str, PerformanceBenchmark] = {}
        self._insights_cache: Dict[str, List[PerformanceInsight]] = {}
        
        # Start background monitoring processes
        asyncio.create_task(self._performance_monitoring_loop())
        asyncio.create_task(self._alert_processing_loop())
        asyncio.create_task(self._insight_generation_loop())
    
    async def setup_campaign_tracking(
        self,
        campaign_id: str,
        tracking_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Setup comprehensive performance tracking for a campaign
        
        Args:
            campaign_id: Campaign unique identifier
            tracking_config: Tracking configuration settings
            
        Returns:
            Tracking setup result
        """
        try:
            tracking_id = f"track_{campaign_id}_{int(datetime.utcnow().timestamp())}"
            
            # Parse tracking configuration
            config = {
                "tracking_id": tracking_id,
                "campaign_id": campaign_id,
                "metrics_to_track": [MetricType(m) for m in tracking_config.get("metrics", [])],
                "tracking_frequency": TrackingFrequency(tracking_config.get("frequency", "daily")),
                "platforms": tracking_config.get("platforms", []),
                "alert_thresholds": tracking_config.get("alert_thresholds", {}),
                "benchmark_comparison": tracking_config.get("benchmark_comparison", True),
                "predictive_analytics": tracking_config.get("predictive_analytics", True),
                "anomaly_detection": tracking_config.get("anomaly_detection", True),
                "real_time_monitoring": tracking_config.get("real_time_monitoring", False),
                "custom_kpis": tracking_config.get("custom_kpis", []),
                "created_at": datetime.utcnow()
            }
            
            # Setup data collection from analytics platforms
            data_collection_setup = await self._setup_data_collection(
                campaign_id, config["platforms"], config["metrics_to_track"]
            )
            
            # Initialize performance prediction models
            prediction_models = {}
            if config["predictive_analytics"]:
                prediction_models = await self.performance_predictor.setup_campaign_models(
                    campaign_id, config["metrics_to_track"]
                )
            
            # Setup anomaly detection
            anomaly_models = {}
            if config["anomaly_detection"]:
                anomaly_models = await self.anomaly_detector.setup_campaign_monitoring(
                    campaign_id, config["metrics_to_track"]
                )
            
            # Configure alert system
            alert_config = await self._setup_alert_system(
                campaign_id, config["alert_thresholds"], config["metrics_to_track"]
            )
            
            # Initialize benchmark comparison
            benchmark_config = {}
            if config["benchmark_comparison"]:
                benchmark_config = await self._setup_benchmark_comparison(
                    campaign_id, tracking_config.get("industry"), tracking_config.get("campaign_type")
                )
            
            # Store tracking configuration
            self._tracking_configs[campaign_id] = {
                **config,
                "data_collection_setup": data_collection_setup,
                "prediction_models": prediction_models,
                "anomaly_models": anomaly_models,
                "alert_config": alert_config,
                "benchmark_config": benchmark_config,
                "status": "active"
            }
            
            # Initialize performance data storage
            self._performance_data[campaign_id] = []
            self._active_alerts[campaign_id] = []
            
            # Start real-time monitoring if enabled
            if config["real_time_monitoring"]:
                asyncio.create_task(self._start_real_time_monitoring(campaign_id))
            
            self.logger.info(f"Campaign tracking setup completed: {tracking_id}")
            
            return {
                "tracking_id": tracking_id,
                "campaign_id": campaign_id,
                "status": "active",
                "metrics_tracked": len(config["metrics_to_track"]),
                "platforms_connected": len(data_collection_setup),
                "predictive_models_active": len(prediction_models),
                "anomaly_detection_active": len(anomaly_models),
                "real_time_monitoring": config["real_time_monitoring"],
                "benchmark_comparison": config["benchmark_comparison"]
            }
            
        except Exception as e:
            self.logger.error(f"Campaign tracking setup failed: {str(e)}")
            raise
    
    async def collect_performance_data(
        self,
        campaign_id: str,
        force_collection: bool = False
    ) -> Dict[str, Any]:
        """
        Collect current performance data for campaign
        
        Args:
            campaign_id: Campaign unique identifier
            force_collection: Force immediate data collection
            
        Returns:
            Collected performance data
        """
        try:
            if campaign_id not in self._tracking_configs:
                raise ValueError(f"Campaign tracking not configured: {campaign_id}")
            
            config = self._tracking_configs[campaign_id]
            collection_timestamp = datetime.utcnow()
            
            # Collect data from configured platforms
            platform_data = {}
            for platform in config["platforms"]:
                platform_metrics = await self.analytics_platform_manager.collect_metrics(
                    platform, campaign_id, config["metrics_to_track"]
                )
                platform_data[platform] = platform_metrics
            
            # Aggregate and normalize data
            aggregated_data = await self.data_aggregator.aggregate_platform_data(
                platform_data, config["metrics_to_track"]
            )
            
            # Calculate custom KPIs
            custom_kpis = {}
            if config["custom_kpis"]:
                custom_kpis = await self.kpi_calculator.calculate_custom_kpis(
                    aggregated_data, config["custom_kpis"]
                )
            
            # Create performance metrics
            performance_metrics = []
            for metric_type in config["metrics_to_track"]:
                if metric_type.value in aggregated_data:
                    current_value = aggregated_data[metric_type.value]["value"]
                    previous_value = await self._get_previous_metric_value(
                        campaign_id, metric_type
                    )
                    
                    change_percentage = 0.0
                    if previous_value and previous_value > 0:
                        change_percentage = ((current_value - previous_value) / previous_value) * 100
                    
                    metric = PerformanceMetric(
                        metric_type=metric_type,
                        value=current_value,
                        previous_value=previous_value,
                        change_percentage=change_percentage,
                        timestamp=collection_timestamp,
                        confidence_score=aggregated_data[metric_type.value].get("confidence", 1.0),
                        source_platform="aggregated",
                        metadata=aggregated_data[metric_type.value].get("metadata", {})
                    )
                    performance_metrics.append(metric)
            
            # Store performance data
            performance_record = {
                "timestamp": collection_timestamp,
                "metrics": performance_metrics,
                "platform_data": platform_data,
                "custom_kpis": custom_kpis,
                "collection_method": "forced" if force_collection else "scheduled"
            }
            
            self._performance_data[campaign_id].append(performance_record)
            
            # Trigger analysis processes
            asyncio.create_task(self._analyze_performance_data(campaign_id, performance_record))
            
            self.logger.info(f"Performance data collected for campaign: {campaign_id}")
            
            return {
                "campaign_id": campaign_id,
                "collection_timestamp": collection_timestamp.isoformat(),
                "metrics_collected": len(performance_metrics),
                "platforms_data": list(platform_data.keys()),
                "custom_kpis": len(custom_kpis),
                "performance_summary": {
                    metric.metric_type.value: {
                        "value": metric.value,
                        "change": metric.change_percentage
                    }
                    for metric in performance_metrics
                }
            }
            
        except Exception as e:
            self.logger.error(f"Performance data collection failed: {str(e)}")
            raise
    
    async def analyze_campaign_performance(
        self,
        campaign_id: str,
        analysis_period: Optional[Tuple[datetime, datetime]] = None,
        include_predictions: bool = True
    ) -> Dict[str, Any]:
        """
        Perform comprehensive campaign performance analysis
        
        Args:
            campaign_id: Campaign unique identifier
            analysis_period: Optional analysis period (start, end)
            include_predictions: Whether to include predictive analysis
            
        Returns:
            Comprehensive performance analysis
        """
        try:
            if campaign_id not in self._tracking_configs:
                raise ValueError(f"Campaign tracking not configured: {campaign_id}")
            
            config = self._tracking_configs[campaign_id]
            
            # Determine analysis period
            if analysis_period:
                start_date, end_date = analysis_period
            else:
                end_date = datetime.utcnow()
                start_date = config["created_at"]
            
            # Get performance data for period
            period_data = await self._get_performance_data_for_period(
                campaign_id, start_date, end_date
            )
            
            if not period_data:
                return {"error": "No performance data available for analysis period"}
            
            # Calculate performance trends
            trend_analysis = await self.trend_analyzer.analyze_performance_trends(
                period_data, config["metrics_to_track"]
            )
            
            # Calculate key performance indicators
            kpi_analysis = await self.kpi_calculator.calculate_campaign_kpis(
                period_data, config["custom_kpis"]
            )
            
            # Benchmark comparison
            benchmark_analysis = {}
            if config["benchmark_comparison"] and campaign_id in self._benchmark_cache:
                benchmark_analysis = await self.benchmark_analyzer.compare_performance(
                    period_data, self._benchmark_cache[campaign_id]
                )
            
            # Anomaly detection
            anomalies = []
            if config["anomaly_detection"]:
                anomalies = await self.anomaly_detector.detect_performance_anomalies(
                    campaign_id, period_data
                )
            
            # Performance insights
            insights = await self._generate_performance_insights(
                campaign_id, period_data, trend_analysis, benchmark_analysis
            )
            
            analysis_result = {
                "campaign_id": campaign_id,
                "analysis_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "duration_days": (end_date - start_date).days
                },
                "performance_summary": await self._summarize_performance(period_data),
                "trend_analysis": trend_analysis,
                "kpi_analysis": kpi_analysis,
                "benchmark_comparison": benchmark_analysis,
                "anomalies_detected": len(anomalies),
                "anomalies": [anomaly.__dict__ for anomaly in anomalies],
                "insights": [insight.__dict__ for insight in insights],
                "recommendations": await self._generate_performance_recommendations(
                    period_data, trend_analysis, insights
                )
            }
            
            # Add predictive analysis
            if include_predictions and config["predictive_analytics"]:
                predictions = await self.performance_predictor.predict_future_performance(
                    campaign_id, period_data, forecast_days=30
                )
                analysis_result["predictions"] = predictions
            
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Campaign performance analysis failed: {str(e)}")
            raise
    
    async def track_real_time_performance(
        self,
        campaign_id: str,
        metrics: Optional[List[MetricType]] = None
    ) -> Dict[str, Any]:
        """
        Get real-time performance data for campaign
        
        Args:
            campaign_id: Campaign unique identifier
            metrics: Specific metrics to track (optional)
            
        Returns:
            Real-time performance data
        """
        try:
            if campaign_id not in self._tracking_configs:
                raise ValueError(f"Campaign tracking not configured: {campaign_id}")
            
            config = self._tracking_configs[campaign_id]
            
            if not config.get("real_time_monitoring", False):
                raise ValueError(f"Real-time monitoring not enabled for campaign: {campaign_id}")
            
            # Determine metrics to track
            target_metrics = metrics or config["metrics_to_track"]
            
            # Collect real-time data
            real_time_data = {}
            for platform in config["platforms"]:
                platform_real_time = await self.analytics_platform_manager.get_real_time_metrics(
                    platform, campaign_id, target_metrics
                )
                real_time_data[platform] = platform_real_time
            
            # Aggregate real-time data
            aggregated_real_time = await self.data_aggregator.aggregate_real_time_data(
                real_time_data, target_metrics
            )
            
            # Calculate real-time KPIs
            real_time_kpis = await self.kpi_calculator.calculate_real_time_kpis(
                aggregated_real_time, config.get("custom_kpis", [])
            )
            
            # Detect real-time anomalies
            real_time_anomalies = []
            if config["anomaly_detection"]:
                real_time_anomalies = await self.anomaly_detector.detect_real_time_anomalies(
                    campaign_id, aggregated_real_time
                )
            
            # Check for alert triggers
            alert_triggers = await self._check_real_time_alerts(
                campaign_id, aggregated_real_time
            )
            
            return {
                "campaign_id": campaign_id,
                "timestamp": datetime.utcnow().isoformat(),
                "real_time_metrics": aggregated_real_time,
                "real_time_kpis": real_time_kpis,
                "anomalies": real_time_anomalies,
                "alert_triggers": alert_triggers,
                "data_sources": list(real_time_data.keys()),
                "monitoring_status": "active"
            }
            
        except Exception as e:
            self.logger.error(f"Real-time performance tracking failed: {str(e)}")
            raise
    
    async def generate_performance_report(
        self,
        campaign_id: str,
        report_type: str = "comprehensive",
        format_type: str = "json",
        include_visualizations: bool = False
    ) -> Dict[str, Any]:
        """
        Generate comprehensive performance report
        
        Args:
            campaign_id: Campaign unique identifier
            report_type: Type of report (summary, comprehensive, executive)
            format_type: Report format (json, pdf, excel)
            include_visualizations: Whether to include visualizations
            
        Returns:
            Generated performance report
        """
        try:
            if campaign_id not in self._tracking_configs:
                raise ValueError(f"Campaign tracking not configured: {campaign_id}")
            
            config = self._tracking_configs[campaign_id]
            
            # Get comprehensive analysis
            analysis = await self.analyze_campaign_performance(
                campaign_id, include_predictions=True
            )
            
            # Build report based on type
            if report_type == "summary":
                report = await self._generate_summary_report(campaign_id, analysis)
            elif report_type == "executive":
                report = await self._generate_executive_report(campaign_id, analysis)
            else:  # comprehensive
                report = await self._generate_comprehensive_report(campaign_id, analysis)
            
            # Add report metadata
            report["metadata"] = {
                "report_id": f"report_{campaign_id}_{int(datetime.utcnow().timestamp())}",
                "campaign_id": campaign_id,
                "report_type": report_type,
                "format_type": format_type,
                "generated_at": datetime.utcnow().isoformat(),
                "tracking_period": f"{config['created_at'].isoformat()} to {datetime.utcnow().isoformat()}"
            }
            
            # Add visualizations if requested
            if include_visualizations:
                report["visualizations"] = await self._generate_report_visualizations(
                    campaign_id, analysis
                )
            
            return report
            
        except Exception as e:
            self.logger.error(f"Performance report generation failed: {str(e)}")
            raise
    
    async def manage_performance_alerts(
        self,
        campaign_id: str,
        action: str,
        alert_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Manage performance alerts for campaign
        
        Args:
            campaign_id: Campaign unique identifier
            action: Alert management action
            alert_config: Alert configuration data
            
        Returns:
            Alert management result
        """
        try:
            if campaign_id not in self._tracking_configs:
                raise ValueError(f"Campaign tracking not configured: {campaign_id}")
            
            if action == "list":
                active_alerts = self._active_alerts.get(campaign_id, [])
                return {
                    "campaign_id": campaign_id,
                    "active_alerts": len(active_alerts),
                    "alerts": [alert.__dict__ for alert in active_alerts]
                }
            
            elif action == "create":
                if not alert_config:
                    raise ValueError("Alert configuration required")
                
                # Create new alert threshold
                await self._create_performance_alert(campaign_id, alert_config)
                
                return {
                    "campaign_id": campaign_id,
                    "action": "created",
                    "alert_config": alert_config
                }
            
            elif action == "update":
                await self._update_performance_alerts(campaign_id, alert_config)
                
                return {
                    "campaign_id": campaign_id,
                    "action": "updated",
                    "alert_config": alert_config
                }
            
            elif action == "resolve":
                alert_id = alert_config.get("alert_id")
                resolution_action = alert_config.get("resolution_action")
                
                await self._resolve_performance_alert(campaign_id, alert_id, resolution_action)
                
                return {
                    "campaign_id": campaign_id,
                    "action": "resolved",
                    "alert_id": alert_id
                }
            
            else:
                raise ValueError(f"Unknown action: {action}")
                
        except Exception as e:
            self.logger.error(f"Performance alert management failed: {str(e)}")
            raise
    
    # Private helper methods
    
    async def _performance_monitoring_loop(self) -> None:
        """Background performance monitoring loop"""
        while True:
            try:
                for campaign_id, config in self._tracking_configs.items():
                    if config["status"] == "active":
                        await self._check_scheduled_collection(campaign_id, config)
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Performance monitoring loop error: {str(e)}")
                await asyncio.sleep(600)
    
    async def _alert_processing_loop(self) -> None:
        """Background alert processing loop"""
        while True:
            try:
                await self._process_pending_alerts()
                await asyncio.sleep(60)  # Process every minute
                
            except Exception as e:
                self.logger.error(f"Alert processing loop error: {str(e)}")
                await asyncio.sleep(120)
    
    async def _insight_generation_loop(self) -> None:
        """Background insight generation loop"""
        while True:
            try:
                await self._generate_scheduled_insights()
                await asyncio.sleep(3600)  # Generate every hour
                
            except Exception as e:
                self.logger.error(f"Insight generation loop error: {str(e)}")
                await asyncio.sleep(1800)
    
    async def _setup_data_collection(
        self,
        campaign_id: str,
        platforms: List[str],
        metrics: List[MetricType]
    ) -> Dict[str, Any]:
        """Setup data collection from analytics platforms"""
        collection_setup = {}
        
        for platform in platforms:
            setup_result = await self.analytics_platform_manager.setup_data_collection(
                platform, campaign_id, metrics
            )
            collection_setup[platform] = setup_result
        
        return collection_setup
    
    async def _get_previous_metric_value(
        self,
        campaign_id: str,
        metric_type: MetricType
    ) -> Optional[float]:
        """Get previous value for a metric"""
        if campaign_id not in self._performance_data:
            return None
        
        data_points = self._performance_data[campaign_id]
        if not data_points:
            return None
        
        # Find most recent data point with this metric
        for data_point in reversed(data_points[:-1]):  # Exclude current
            for metric in data_point["metrics"]:
                if metric.metric_type == metric_type:
                    return metric.value
        
        return None
