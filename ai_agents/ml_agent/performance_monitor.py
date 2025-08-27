"""
ML Performance Monitor - Advanced ML Performance Monitoring & Analytics System

Industrial-grade ML performance monitoring providing comprehensive performance tracking,
drift detection, model quality analysis, and predictive maintenance for ML systems
in the IA-Influencer-Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL WARNING:
This monitoring system and methodologies are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission
from Fahed Mlaiel (mlaiel@live.de) is STRICTLY PROHIBITED and will result in legal action.

ALL RIGHTS RESERVED - FAHED MLAIEL ©2025

🎯 BUSINESS LOGIC INTEGRATION:
Performance Monitoring → Drift Detection → Quality Analysis → Alert Generation
→ Predictive Maintenance → Auto-scaling → Model Retraining Triggers

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""

import asyncio
import logging
import time
import uuid
import json
import hashlib
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from pathlib import Path
import traceback
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support, roc_auc_score,
    mean_squared_error, r2_score, silhouette_score
)
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px

# Drift detection libraries
try:
    from evidently import ColumnMapping
    from evidently.report import Report
    from evidently.metric_preset import DataDriftPreset, DataQualityPreset
    EVIDENTLY_AVAILABLE = True
except ImportError:
    EVIDENTLY_AVAILABLE = False

# Time series analysis
try:
    from statsmodels.tsa.seasonal import seasonal_decompose
    from statsmodels.tsa.arima.model import ARIMA
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False

# Platform core
from ...core.config import settings
from ...core.database import get_db_session
from ...core.exceptions import MonitoringError, ValidationError, AnalysisError
from ...security.encryption import ContentEncryption
from ...utils.performance_monitor import PerformanceMonitor
from ...utils.cache import CacheManager
from ...utils.alerting import AlertManager

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class DriftType(Enum):
    """Data drift types"""
    DATA_DRIFT = "data_drift"
    CONCEPT_DRIFT = "concept_drift"
    PREDICTION_DRIFT = "prediction_drift"
    TARGET_DRIFT = "target_drift"

class PerformanceMetric(Enum):
    """Performance metrics to track"""
    ACCURACY = "accuracy"
    PRECISION = "precision"
    RECALL = "recall"
    F1_SCORE = "f1_score"
    ROC_AUC = "roc_auc"
    MSE = "mse"
    RMSE = "rmse"
    R2_SCORE = "r2_score"
    LATENCY = "latency"
    THROUGHPUT = "throughput"

@dataclass
class PerformanceThresholds:
    """Performance monitoring thresholds"""
    accuracy_threshold: float = 0.8
    drift_threshold: float = 0.1
    latency_threshold: float = 100.0  # milliseconds
    error_rate_threshold: float = 0.05
    throughput_threshold: float = 100.0  # requests per second
    data_quality_threshold: float = 0.95
    prediction_stability_threshold: float = 0.1

@dataclass
class MonitoringAlert:
    """Monitoring alert data"""
    alert_id: str
    model_id: str
    alert_type: str
    severity: AlertSeverity
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolved: bool = False
    resolution_time: Optional[datetime] = None

@dataclass
class DriftReport:
    """Data drift analysis report"""
    report_id: str
    model_id: str
    drift_type: DriftType
    drift_detected: bool
    drift_score: float
    affected_features: List[str]
    reference_period: Tuple[datetime, datetime]
    analysis_period: Tuple[datetime, datetime]
    statistical_tests: Dict[str, Any] = field(default_factory=dict)
    visualization_paths: Dict[str, str] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class ModelQualityReport:
    """Model quality analysis report"""
    report_id: str
    model_id: str
    model_version: str
    performance_metrics: Dict[str, float]
    quality_score: float
    data_quality_metrics: Dict[str, float]
    prediction_stability: float
    feature_importance: Dict[str, float] = field(default_factory=dict)
    anomalies_detected: int = 0
    quality_trends: Dict[str, List[float]] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

class MLPerformanceMonitor:
    """
    Ultra-advanced ML performance monitoring system providing comprehensive
    performance tracking, drift detection, quality analysis, and alerting
    """
    
    def __init__(self):
        self.monitoring_configs = {}
        self.performance_data = {}
        self.alerts = {}
        self.drift_reports = {}
        self.quality_reports = {}
        self.performance_monitor = PerformanceMonitor()
        self.cache_manager = CacheManager()
        self.alert_manager = AlertManager()
        self._initialize_monitoring()
    
    def _initialize_monitoring(self):
        """Initialize performance monitoring system"""
        try:
            # Setup default thresholds
            self.default_thresholds = PerformanceThresholds()
            
            # Initialize data collectors
            self._setup_data_collectors()
            
            # Start background monitoring tasks
            asyncio.create_task(self._run_continuous_monitoring())
            
            logger.info("ML Performance Monitor initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ML Performance Monitor: {str(e)}")
            raise MonitoringError(f"Monitor initialization failed: {str(e)}")
    
    def _setup_data_collectors(self):
        """Setup data collection mechanisms"""
        # Initialize metrics collectors
        self.metrics_collectors = {
            'prediction_metrics': self._collect_prediction_metrics,
            'system_metrics': self._collect_system_metrics,
            'data_quality_metrics': self._collect_data_quality_metrics,
            'drift_metrics': self._collect_drift_metrics
        }
    
    async def register_model_monitoring(
        self, 
        model_id: str, 
        monitoring_config: Dict[str, Any]
    ) -> str:
        """Register a model for continuous monitoring"""
        try:
            config_id = str(uuid.uuid4())
            
            # Validate configuration
            await self._validate_monitoring_config(monitoring_config)
            
            # Store configuration
            self.monitoring_configs[model_id] = {
                'config_id': config_id,
                'model_id': model_id,
                'thresholds': monitoring_config.get('thresholds', self.default_thresholds),
                'monitoring_frequency': monitoring_config.get('frequency', 300),  # 5 minutes
                'drift_detection_enabled': monitoring_config.get('drift_detection', True),
                'quality_analysis_enabled': monitoring_config.get('quality_analysis', True),
                'alerting_enabled': monitoring_config.get('alerting', True),
                'reference_data': monitoring_config.get('reference_data'),
                'enabled': True,
                'created_at': datetime.now(timezone.utc)
            }
            
            # Initialize performance data storage
            self.performance_data[model_id] = {
                'metrics_history': [],
                'prediction_history': [],
                'system_metrics': [],
                'drift_history': [],
                'quality_history': []
            }
            
            logger.info(f"Model monitoring registered: {model_id}")
            return config_id
            
        except Exception as e:
            logger.error(f"Failed to register model monitoring: {str(e)}")
            raise MonitoringError(f"Registration failed: {str(e)}")
    
    async def _validate_monitoring_config(self, config: Dict[str, Any]):
        """Validate monitoring configuration"""
        required_fields = ['model_id']
        for field in required_fields:
            if field not in config:
                raise ValidationError(f"Missing required field: {field}")
        
        # Validate thresholds if provided
        if 'thresholds' in config:
            thresholds = config['thresholds']
            if isinstance(thresholds, dict):
                for key, value in thresholds.items():
                    if not isinstance(value, (int, float)):
                        raise ValidationError(f"Invalid threshold value for {key}")
    
    async def _run_continuous_monitoring(self):
        """Run continuous monitoring loop"""
        while True:
            try:
                for model_id, config in self.monitoring_configs.items():
                    if not config.get('enabled', True):
                        continue
                    
                    # Collect metrics
                    await self._collect_model_metrics(model_id)
                    
                    # Perform drift detection
                    if config.get('drift_detection_enabled', True):
                        await self._detect_drift(model_id)
                    
                    # Analyze model quality
                    if config.get('quality_analysis_enabled', True):
                        await self._analyze_model_quality(model_id)
                    
                    # Check for alerts
                    if config.get('alerting_enabled', True):
                        await self._check_alerts(model_id)
                
                # Sleep between monitoring cycles
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in continuous monitoring: {str(e)}")
                await asyncio.sleep(60)
    
    async def _collect_model_metrics(self, model_id: str):
        """Collect comprehensive metrics for a model"""
        try:
            timestamp = datetime.now(timezone.utc)
            metrics = {}
            
            # Collect different types of metrics
            for collector_name, collector_func in self.metrics_collectors.items():
                try:
                    metric_data = await collector_func(model_id)
                    metrics[collector_name] = metric_data
                except Exception as e:
                    logger.warning(f"Failed to collect {collector_name} for {model_id}: {str(e)}")
            
            # Store metrics
            if model_id not in self.performance_data:
                self.performance_data[model_id] = {'metrics_history': []}
            
            self.performance_data[model_id]['metrics_history'].append({
                'timestamp': timestamp,
                'metrics': metrics
            })
            
            # Keep only recent data (last 30 days)
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=30)
            self.performance_data[model_id]['metrics_history'] = [
                m for m in self.performance_data[model_id]['metrics_history']
                if m['timestamp'] > cutoff_date
            ]
            
        except Exception as e:
            logger.error(f"Error collecting metrics for {model_id}: {str(e)}")
    
    async def _collect_prediction_metrics(self, model_id: str) -> Dict[str, Any]:
        """Collect prediction-related metrics"""
        # This would integrate with the model's prediction endpoint
        # For now, returning simulated metrics
        return {
            'prediction_count': np.random.randint(50, 500),
            'average_latency': np.random.uniform(10, 100),
            'error_rate': np.random.uniform(0, 0.1),
            'prediction_confidence': np.random.uniform(0.7, 0.95)
        }
    
    async def _collect_system_metrics(self, model_id: str) -> Dict[str, Any]:
        """Collect system-level metrics"""
        import psutil
        
        return {
            'cpu_usage': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'network_io': psutil.net_io_counters()._asdict()
        }
    
    async def _collect_data_quality_metrics(self, model_id: str) -> Dict[str, Any]:
        """Collect data quality metrics"""
        # This would analyze incoming data quality
        return {
            'completeness': np.random.uniform(0.9, 1.0),
            'consistency': np.random.uniform(0.8, 1.0),
            'validity': np.random.uniform(0.85, 1.0),
            'uniqueness': np.random.uniform(0.95, 1.0)
        }
    
    async def _collect_drift_metrics(self, model_id: str) -> Dict[str, Any]:
        """Collect drift-related metrics"""
        # This would calculate statistical measures for drift detection
        return {
            'feature_drift_scores': {f'feature_{i}': np.random.uniform(0, 0.2) for i in range(5)},
            'prediction_drift_score': np.random.uniform(0, 0.1),
            'target_drift_score': np.random.uniform(0, 0.15)
        }
    
    async def _detect_drift(self, model_id: str):
        """Detect data drift for a model"""
        try:
            config = self.monitoring_configs.get(model_id)
            if not config:
                return
            
            # Get recent data
            recent_data = await self._get_recent_data(model_id, hours=24)
            reference_data = config.get('reference_data')
            
            if not recent_data or not reference_data:
                return
            
            # Perform drift detection
            drift_results = await self._perform_drift_analysis(
                reference_data, recent_data, model_id
            )
            
            # Create drift report
            if drift_results['drift_detected']:
                await self._create_drift_report(model_id, drift_results)
                
                # Generate alert if drift is significant
                if drift_results['drift_score'] > config.get('thresholds', {}).get('drift_threshold', 0.1):
                    await self._generate_drift_alert(model_id, drift_results)
            
        except Exception as e:
            logger.error(f"Error detecting drift for {model_id}: {str(e)}")
    
    async def _get_recent_data(self, model_id: str, hours: int = 24) -> Optional[pd.DataFrame]:
        """Get recent data for drift analysis"""
        # This would retrieve recent prediction data from the database
        # For now, returning simulated data
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        # Simulate recent data
        n_samples = np.random.randint(100, 1000)
        n_features = 10
        
        data = np.random.randn(n_samples, n_features)
        feature_names = [f'feature_{i}' for i in range(n_features)]
        
        return pd.DataFrame(data, columns=feature_names)
    
    async def _perform_drift_analysis(
        self, 
        reference_data: pd.DataFrame, 
        current_data: pd.DataFrame,
        model_id: str
    ) -> Dict[str, Any]:
        """Perform comprehensive drift analysis"""
        
        drift_results = {
            'drift_detected': False,
            'drift_score': 0.0,
            'affected_features': [],
            'statistical_tests': {},
            'drift_type': None
        }
        
        try:
            # Kolmogorov-Smirnov test for each feature
            ks_results = {}
            for feature in reference_data.columns:
                if feature in current_data.columns:
                    ks_stat, p_value = stats.ks_2samp(
                        reference_data[feature], 
                        current_data[feature]
                    )
                    ks_results[feature] = {
                        'ks_statistic': ks_stat,
                        'p_value': p_value,
                        'drift_detected': p_value < 0.05
                    }
                    
                    if p_value < 0.05:
                        drift_results['affected_features'].append(feature)
            
            drift_results['statistical_tests']['kolmogorov_smirnov'] = ks_results
            
            # Calculate overall drift score
            drift_scores = [result['ks_statistic'] for result in ks_results.values()]
            drift_results['drift_score'] = np.mean(drift_scores) if drift_scores else 0.0
            
            # Determine if drift is detected
            drift_results['drift_detected'] = len(drift_results['affected_features']) > 0
            
            if drift_results['drift_detected']:
                drift_results['drift_type'] = DriftType.DATA_DRIFT
            
            # Use Evidently if available for more advanced drift detection
            if EVIDENTLY_AVAILABLE:
                evidently_results = await self._run_evidently_analysis(
                    reference_data, current_data
                )
                drift_results['evidently_report'] = evidently_results
            
        except Exception as e:
            logger.error(f"Error in drift analysis: {str(e)}")
        
        return drift_results
    
    async def _run_evidently_analysis(
        self, 
        reference_data: pd.DataFrame, 
        current_data: pd.DataFrame
    ) -> Dict[str, Any]:
        """Run Evidently drift analysis"""
        try:
            # Create Evidently report
            report = Report(metrics=[
                DataDriftPreset(),
                DataQualityPreset()
            ])
            
            report.run(reference_data=reference_data, current_data=current_data)
            
            # Extract key metrics
            report_json = json.loads(report.json())
            
            return {
                'data_drift': report_json.get('metrics', {}).get('DataDriftTable', {}),
                'data_quality': report_json.get('metrics', {}).get('DataQualityTable', {})
            }
            
        except Exception as e:
            logger.error(f"Error running Evidently analysis: {str(e)}")
            return {}
    
    async def _create_drift_report(self, model_id: str, drift_results: Dict[str, Any]):
        """Create comprehensive drift report"""
        try:
            report_id = str(uuid.uuid4())
            
            # Generate visualizations
            visualization_paths = await self._generate_drift_visualizations(
                model_id, drift_results, report_id
            )
            
            # Generate recommendations
            recommendations = await self._generate_drift_recommendations(drift_results)
            
            # Create report
            drift_report = DriftReport(
                report_id=report_id,
                model_id=model_id,
                drift_type=drift_results.get('drift_type', DriftType.DATA_DRIFT),
                drift_detected=drift_results['drift_detected'],
                drift_score=drift_results['drift_score'],
                affected_features=drift_results['affected_features'],
                reference_period=(datetime.now(timezone.utc) - timedelta(days=30), datetime.now(timezone.utc) - timedelta(days=7)),
                analysis_period=(datetime.now(timezone.utc) - timedelta(days=7), datetime.now(timezone.utc)),
                statistical_tests=drift_results['statistical_tests'],
                visualization_paths=visualization_paths,
                recommendations=recommendations
            )
            
            # Store report
            self.drift_reports[report_id] = drift_report
            
            logger.info(f"Drift report created: {report_id} for model {model_id}")
            
        except Exception as e:
            logger.error(f"Error creating drift report: {str(e)}")
    
    async def _generate_drift_visualizations(
        self, 
        model_id: str, 
        drift_results: Dict[str, Any],
        report_id: str
    ) -> Dict[str, str]:
        """Generate drift visualization charts"""
        visualization_paths = {}
        
        try:
            # Create output directory
            viz_dir = Path(f"/tmp/drift_reports/{report_id}")
            viz_dir.mkdir(parents=True, exist_ok=True)
            
            # Feature drift score chart
            if drift_results.get('statistical_tests', {}).get('kolmogorov_smirnov'):
                ks_results = drift_results['statistical_tests']['kolmogorov_smirnov']
                
                features = list(ks_results.keys())
                ks_stats = [ks_results[f]['ks_statistic'] for f in features]
                
                fig = go.Figure(data=[
                    go.Bar(x=features, y=ks_stats, name='KS Statistic')
                ])
                fig.update_layout(
                    title='Feature Drift Scores (Kolmogorov-Smirnov)',
                    xaxis_title='Features',
                    yaxis_title='KS Statistic'
                )
                
                drift_chart_path = viz_dir / "feature_drift_scores.html"
                fig.write_html(str(drift_chart_path))
                visualization_paths['feature_drift_scores'] = str(drift_chart_path)
            
        except Exception as e:
            logger.error(f"Error generating drift visualizations: {str(e)}")
        
        return visualization_paths
    
    async def _generate_drift_recommendations(self, drift_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on drift analysis"""
        recommendations = []
        
        if drift_results['drift_detected']:
            recommendations.append("Data drift detected - consider retraining the model")
            
            if len(drift_results['affected_features']) > 3:
                recommendations.append("Multiple features affected - investigate data pipeline")
            
            if drift_results['drift_score'] > 0.2:
                recommendations.append("High drift score - urgent model update recommended")
            
            recommendations.append("Monitor model performance closely")
            recommendations.append("Consider implementing automated retraining")
        
        return recommendations
    
    async def _generate_drift_alert(self, model_id: str, drift_results: Dict[str, Any]):
        """Generate drift detection alert"""
        alert_id = str(uuid.uuid4())
        
        severity = AlertSeverity.WARNING
        if drift_results['drift_score'] > 0.2:
            severity = AlertSeverity.ERROR
        if drift_results['drift_score'] > 0.3:
            severity = AlertSeverity.CRITICAL
        
        alert = MonitoringAlert(
            alert_id=alert_id,
            model_id=model_id,
            alert_type="DATA_DRIFT",
            severity=severity,
            message=f"Data drift detected for model {model_id}",
            details={
                'drift_score': drift_results['drift_score'],
                'affected_features': drift_results['affected_features'],
                'recommendation': 'Consider retraining the model'
            }
        )
        
        self.alerts[alert_id] = alert
        
        # Send alert through alert manager
        await self.alert_manager.send_alert(alert)
        
        logger.warning(f"Drift alert generated: {alert_id} for model {model_id}")
    
    async def _analyze_model_quality(self, model_id: str):
        """Analyze model quality metrics"""
        try:
            # Get recent performance metrics
            recent_metrics = await self._get_recent_performance_metrics(model_id)
            
            if not recent_metrics:
                return
            
            # Calculate quality metrics
            quality_analysis = await self._calculate_quality_metrics(model_id, recent_metrics)
            
            # Create quality report
            await self._create_quality_report(model_id, quality_analysis)
            
            # Check for quality alerts
            await self._check_quality_alerts(model_id, quality_analysis)
            
        except Exception as e:
            logger.error(f"Error analyzing model quality for {model_id}: {str(e)}")
    
    async def _get_recent_performance_metrics(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get recent performance metrics for quality analysis"""
        if model_id not in self.performance_data:
            return None
        
        metrics_history = self.performance_data[model_id].get('metrics_history', [])
        
        if not metrics_history:
            return None
        
        # Get metrics from last 24 hours
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
        recent_metrics = [
            m for m in metrics_history
            if m['timestamp'] > cutoff_time
        ]
        
        return recent_metrics
    
    async def _calculate_quality_metrics(
        self, 
        model_id: str, 
        recent_metrics: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate comprehensive quality metrics"""
        
        quality_metrics = {
            'performance_metrics': {},
            'stability_metrics': {},
            'data_quality_metrics': {},
            'system_metrics': {}
        }
        
        try:
            # Extract metrics from recent data
            prediction_metrics = []
            system_metrics = []
            data_quality_metrics = []
            
            for metric_entry in recent_metrics:
                metrics = metric_entry.get('metrics', {})
                
                if 'prediction_metrics' in metrics:
                    prediction_metrics.append(metrics['prediction_metrics'])
                
                if 'system_metrics' in metrics:
                    system_metrics.append(metrics['system_metrics'])
                
                if 'data_quality_metrics' in metrics:
                    data_quality_metrics.append(metrics['data_quality_metrics'])
            
            # Calculate performance metrics
            if prediction_metrics:
                quality_metrics['performance_metrics'] = {
                    'avg_latency': np.mean([m.get('average_latency', 0) for m in prediction_metrics]),
                    'avg_error_rate': np.mean([m.get('error_rate', 0) for m in prediction_metrics]),
                    'avg_confidence': np.mean([m.get('prediction_confidence', 0) for m in prediction_metrics]),
                    'total_predictions': sum([m.get('prediction_count', 0) for m in prediction_metrics])
                }
            
            # Calculate stability metrics
            if prediction_metrics:
                latencies = [m.get('average_latency', 0) for m in prediction_metrics]
                error_rates = [m.get('error_rate', 0) for m in prediction_metrics]
                
                quality_metrics['stability_metrics'] = {
                    'latency_std': np.std(latencies),
                    'error_rate_std': np.std(error_rates),
                    'latency_trend': self._calculate_trend(latencies),
                    'error_rate_trend': self._calculate_trend(error_rates)
                }
            
            # Calculate data quality metrics
            if data_quality_metrics:
                quality_metrics['data_quality_metrics'] = {
                    'avg_completeness': np.mean([m.get('completeness', 0) for m in data_quality_metrics]),
                    'avg_consistency': np.mean([m.get('consistency', 0) for m in data_quality_metrics]),
                    'avg_validity': np.mean([m.get('validity', 0) for m in data_quality_metrics])
                }
            
            # Calculate system metrics
            if system_metrics:
                quality_metrics['system_metrics'] = {
                    'avg_cpu_usage': np.mean([m.get('cpu_usage', 0) for m in system_metrics]),
                    'avg_memory_usage': np.mean([m.get('memory_usage', 0) for m in system_metrics]),
                    'avg_disk_usage': np.mean([m.get('disk_usage', 0) for m in system_metrics])
                }
            
            # Calculate overall quality score
            quality_score = await self._calculate_overall_quality_score(quality_metrics)
            quality_metrics['overall_quality_score'] = quality_score
            
        except Exception as e:
            logger.error(f"Error calculating quality metrics: {str(e)}")
        
        return quality_metrics
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction for a series of values"""
        if len(values) < 2:
            return "stable"
        
        # Simple linear trend calculation
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        if slope > 0.01:
            return "increasing"
        elif slope < -0.01:
            return "decreasing"
        else:
            return "stable"
    
    async def _calculate_overall_quality_score(self, quality_metrics: Dict[str, Any]) -> float:
        """Calculate overall quality score from component metrics"""
        score_components = []
        
        # Performance score
        perf_metrics = quality_metrics.get('performance_metrics', {})
        if perf_metrics:
            latency_score = max(0, 1 - perf_metrics.get('avg_latency', 0) / 1000)  # Normalize by 1000ms
            error_score = max(0, 1 - perf_metrics.get('avg_error_rate', 0) * 10)  # Scale error rate
            confidence_score = perf_metrics.get('avg_confidence', 0)
            
            performance_score = np.mean([latency_score, error_score, confidence_score])
            score_components.append(performance_score)
        
        # Data quality score
        dq_metrics = quality_metrics.get('data_quality_metrics', {})
        if dq_metrics:
            data_quality_score = np.mean([
                dq_metrics.get('avg_completeness', 0),
                dq_metrics.get('avg_consistency', 0),
                dq_metrics.get('avg_validity', 0)
            ])
            score_components.append(data_quality_score)
        
        # System health score
        sys_metrics = quality_metrics.get('system_metrics', {})
        if sys_metrics:
            cpu_score = max(0, 1 - sys_metrics.get('avg_cpu_usage', 0) / 100)
            memory_score = max(0, 1 - sys_metrics.get('avg_memory_usage', 0) / 100)
            system_score = np.mean([cpu_score, memory_score])
            score_components.append(system_score)
        
        # Calculate weighted average
        if score_components:
            return np.mean(score_components)
        else:
            return 0.5  # Default neutral score
    
    async def _create_quality_report(self, model_id: str, quality_analysis: Dict[str, Any]):
        """Create model quality report"""
        try:
            report_id = str(uuid.uuid4())
            
            # Get model version (would come from model registry)
            model_version = "1.0.0"  # Placeholder
            
            # Create quality report
            quality_report = ModelQualityReport(
                report_id=report_id,
                model_id=model_id,
                model_version=model_version,
                performance_metrics=quality_analysis.get('performance_metrics', {}),
                quality_score=quality_analysis.get('overall_quality_score', 0.0),
                data_quality_metrics=quality_analysis.get('data_quality_metrics', {}),
                prediction_stability=quality_analysis.get('stability_metrics', {}).get('latency_std', 0.0)
            )
            
            # Store report
            self.quality_reports[report_id] = quality_report
            
            logger.info(f"Quality report created: {report_id} for model {model_id}")
            
        except Exception as e:
            logger.error(f"Error creating quality report: {str(e)}")
    
    async def _check_quality_alerts(self, model_id: str, quality_analysis: Dict[str, Any]):
        """Check for quality-based alerts"""
        try:
            config = self.monitoring_configs.get(model_id, {})
            thresholds = config.get('thresholds', self.default_thresholds)
            
            # Check performance thresholds
            perf_metrics = quality_analysis.get('performance_metrics', {})
            
            # Latency alert
            avg_latency = perf_metrics.get('avg_latency', 0)
            if avg_latency > thresholds.latency_threshold:
                await self._generate_performance_alert(
                    model_id, 'HIGH_LATENCY', 
                    f"Average latency {avg_latency:.2f}ms exceeds threshold {thresholds.latency_threshold}ms"
                )
            
            # Error rate alert
            error_rate = perf_metrics.get('avg_error_rate', 0)
            if error_rate > thresholds.error_rate_threshold:
                await self._generate_performance_alert(
                    model_id, 'HIGH_ERROR_RATE',
                    f"Error rate {error_rate:.3f} exceeds threshold {thresholds.error_rate_threshold}"
                )
            
            # Overall quality alert
            overall_score = quality_analysis.get('overall_quality_score', 1.0)
            if overall_score < 0.7:  # Quality threshold
                severity = AlertSeverity.WARNING if overall_score > 0.5 else AlertSeverity.ERROR
                await self._generate_quality_alert(
                    model_id, severity,
                    f"Model quality score {overall_score:.3f} is below acceptable threshold"
                )
            
        except Exception as e:
            logger.error(f"Error checking quality alerts: {str(e)}")
    
    async def _generate_performance_alert(self, model_id: str, alert_type: str, message: str):
        """Generate performance-related alert"""
        alert_id = str(uuid.uuid4())
        
        alert = MonitoringAlert(
            alert_id=alert_id,
            model_id=model_id,
            alert_type=alert_type,
            severity=AlertSeverity.WARNING,
            message=message
        )
        
        self.alerts[alert_id] = alert
        await self.alert_manager.send_alert(alert)
        
        logger.warning(f"Performance alert generated: {alert_id} - {message}")
    
    async def _generate_quality_alert(self, model_id: str, severity: AlertSeverity, message: str):
        """Generate quality-related alert"""
        alert_id = str(uuid.uuid4())
        
        alert = MonitoringAlert(
            alert_id=alert_id,
            model_id=model_id,
            alert_type="MODEL_QUALITY",
            severity=severity,
            message=message
        )
        
        self.alerts[alert_id] = alert
        await self.alert_manager.send_alert(alert)
        
        logger.warning(f"Quality alert generated: {alert_id} - {message}")
    
    async def _check_alerts(self, model_id: str):
        """Check for any alerts that need to be generated"""
        # This method orchestrates all alert checking
        # Individual alert checks are handled in other methods
        pass
    
    async def get_model_performance_summary(self, model_id: str) -> Dict[str, Any]:
        """Get comprehensive performance summary for a model"""
        try:
            if model_id not in self.performance_data:
                raise ValueError(f"No performance data found for model: {model_id}")
            
            performance_data = self.performance_data[model_id]
            
            # Get latest metrics
            latest_metrics = None
            if performance_data.get('metrics_history'):
                latest_metrics = performance_data['metrics_history'][-1]
            
            # Get recent quality report
            recent_quality_reports = [
                report for report in self.quality_reports.values()
                if report.model_id == model_id
            ]
            latest_quality_report = None
            if recent_quality_reports:
                latest_quality_report = max(recent_quality_reports, key=lambda r: r.timestamp)
            
            # Get recent drift reports
            recent_drift_reports = [
                report for report in self.drift_reports.values()
                if report.model_id == model_id
            ]
            latest_drift_report = None
            if recent_drift_reports:
                latest_drift_report = max(recent_drift_reports, key=lambda r: r.timestamp)
            
            # Get active alerts
            active_alerts = [
                alert for alert in self.alerts.values()
                if alert.model_id == model_id and not alert.resolved
            ]
            
            summary = {
                'model_id': model_id,
                'monitoring_enabled': model_id in self.monitoring_configs,
                'latest_metrics': latest_metrics,
                'quality_report': asdict(latest_quality_report) if latest_quality_report else None,
                'drift_report': asdict(latest_drift_report) if latest_drift_report else None,
                'active_alerts': [asdict(alert) for alert in active_alerts],
                'performance_trends': await self._calculate_performance_trends(model_id),
                'health_status': await self._get_overall_health_status(model_id)
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting performance summary for {model_id}: {str(e)}")
            raise MonitoringError(f"Failed to get performance summary: {str(e)}")
    
    async def _calculate_performance_trends(self, model_id: str) -> Dict[str, Any]:
        """Calculate performance trends for a model"""
        if model_id not in self.performance_data:
            return {}
        
        metrics_history = self.performance_data[model_id].get('metrics_history', [])
        
        if len(metrics_history) < 2:
            return {}
        
        # Extract time series data
        timestamps = [m['timestamp'] for m in metrics_history]
        
        trends = {}
        
        # Calculate trends for key metrics
        if metrics_history:
            latencies = []
            error_rates = []
            
            for entry in metrics_history:
                pred_metrics = entry.get('metrics', {}).get('prediction_metrics', {})
                latencies.append(pred_metrics.get('average_latency', 0))
                error_rates.append(pred_metrics.get('error_rate', 0))
            
            trends = {
                'latency_trend': self._calculate_trend(latencies),
                'error_rate_trend': self._calculate_trend(error_rates),
                'data_points': len(metrics_history),
                'time_range_hours': (timestamps[-1] - timestamps[0]).total_seconds() / 3600 if len(timestamps) > 1 else 0
            }
        
        return trends
    
    async def _get_overall_health_status(self, model_id: str) -> str:
        """Get overall health status for a model"""
        # Check for critical alerts
        critical_alerts = [
            alert for alert in self.alerts.values()
            if alert.model_id == model_id and alert.severity == AlertSeverity.CRITICAL and not alert.resolved
        ]
        
        if critical_alerts:
            return "critical"
        
        # Check for error alerts
        error_alerts = [
            alert for alert in self.alerts.values()
            if alert.model_id == model_id and alert.severity == AlertSeverity.ERROR and not alert.resolved
        ]
        
        if error_alerts:
            return "degraded"
        
        # Check for warning alerts
        warning_alerts = [
            alert for alert in self.alerts.values()
            if alert.model_id == model_id and alert.severity == AlertSeverity.WARNING and not alert.resolved
        ]
        
        if warning_alerts:
            return "warning"
        
        return "healthy"
    
    async def resolve_alert(self, alert_id: str, resolution_notes: str = "") -> bool:
        """Resolve a monitoring alert"""
        try:
            if alert_id not in self.alerts:
                raise ValueError(f"Alert not found: {alert_id}")
            
            alert = self.alerts[alert_id]
            alert.resolved = True
            alert.resolution_time = datetime.now(timezone.utc)
            
            if resolution_notes:
                alert.details['resolution_notes'] = resolution_notes
            
            logger.info(f"Alert resolved: {alert_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error resolving alert: {str(e)}")
            return False
    
    async def get_drift_report(self, report_id: str) -> Dict[str, Any]:
        """Get detailed drift report"""
        if report_id not in self.drift_reports:
            raise ValueError(f"Drift report not found: {report_id}")
        
        return asdict(self.drift_reports[report_id])
    
    async def get_quality_report(self, report_id: str) -> Dict[str, Any]:
        """Get detailed quality report"""
        if report_id not in self.quality_reports:
            raise ValueError(f"Quality report not found: {report_id}")
        
        return asdict(self.quality_reports[report_id])
    
    async def disable_model_monitoring(self, model_id: str) -> bool:
        """Disable monitoring for a model"""
        try:
            if model_id in self.monitoring_configs:
                self.monitoring_configs[model_id]['enabled'] = False
                logger.info(f"Monitoring disabled for model: {model_id}")
                return True
            else:
                logger.warning(f"No monitoring configuration found for model: {model_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error disabling monitoring: {str(e)}")
            return False
    
    async def export_performance_report(
        self, 
        model_id: str, 
        format: str = 'json',
        time_range_hours: int = 24
    ) -> str:
        """Export comprehensive performance report"""
        try:
            # Get performance summary
            summary = await self.get_model_performance_summary(model_id)
            
            # Get historical data
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=time_range_hours)
            
            historical_data = []
            if model_id in self.performance_data:
                historical_data = [
                    entry for entry in self.performance_data[model_id].get('metrics_history', [])
                    if entry['timestamp'] > cutoff_time
                ]
            
            report_data = {
                'model_id': model_id,
                'report_generated': datetime.now(timezone.utc).isoformat(),
                'time_range_hours': time_range_hours,
                'summary': summary,
                'historical_data': historical_data,
                'drift_reports': [
                    asdict(report) for report in self.drift_reports.values()
                    if report.model_id == model_id and report.timestamp > cutoff_time
                ],
                'quality_reports': [
                    asdict(report) for report in self.quality_reports.values()
                    if report.model_id == model_id and report.timestamp > cutoff_time
                ]
            }
            
            # Export based on format
            if format == 'json':
                output_path = f"/tmp/performance_report_{model_id}_{int(time.time())}.json"
                with open(output_path, 'w') as f:
                    json.dump(report_data, f, indent=2, default=str)
            
            elif format == 'html':
                output_path = f"/tmp/performance_report_{model_id}_{int(time.time())}.html"
                await self._generate_html_performance_report(report_data, output_path)
            
            else:
                raise ValueError(f"Unsupported export format: {format}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error exporting performance report: {str(e)}")
            raise MonitoringError(f"Report export failed: {str(e)}")
    
    async def _generate_html_performance_report(self, report_data: Dict[str, Any], output_path: str):
        """Generate HTML performance report"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>ML Performance Report - {report_data['model_id']}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #dee2e6; border-radius: 5px; }}
                .metric {{ display: inline-block; margin: 10px; padding: 15px; background-color: #e9ecef; border-radius: 5px; }}
                .alert {{ padding: 10px; margin: 5px 0; border-radius: 5px; }}
                .alert-warning {{ background-color: #fff3cd; border: 1px solid #ffeaa7; }}
                .alert-error {{ background-color: #f8d7da; border: 1px solid #f5c6cb; }}
                .alert-critical {{ background-color: #721c24; color: white; border: 1px solid #491217; }}
                table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>ML Performance Report</h1>
                <h2>Model ID: {report_data['model_id']}</h2>
                <p><strong>Generated:</strong> {report_data['report_generated']}</p>
                <p><strong>Time Range:</strong> {report_data['time_range_hours']} hours</p>
            </div>
            
            <div class="section">
                <h3>Health Status</h3>
                <div class="metric">
                    <h4>Overall Health</h4>
                    <p>{report_data['summary'].get('health_status', 'Unknown')}</p>
                </div>
            </div>
        """
        
        # Add alerts section
        if report_data['summary'].get('active_alerts'):
            html_content += "<div class='section'><h3>Active Alerts</h3>"
            for alert in report_data['summary']['active_alerts']:
                alert_class = f"alert-{alert['severity']}"
                html_content += f"""
                <div class="alert {alert_class}">
                    <strong>{alert['alert_type']}</strong>: {alert['message']}
                    <small>({alert['timestamp']})</small>
                </div>
                """
            html_content += "</div>"
        
        html_content += "</body></html>"
        
        with open(output_path, 'w') as f:
            f.write(html_content)

# Global performance monitor instance
ml_performance_monitor = MLPerformanceMonitor()

# Export all components
__all__ = [
    'MLPerformanceMonitor',
    'PerformanceThresholds',
    'MonitoringAlert',
    'DriftReport',
    'ModelQualityReport',
    'AlertSeverity',
    'DriftType',
    'PerformanceMetric',
    'ml_performance_monitor'
]
