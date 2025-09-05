"""Enterprise Analytics System
===========================

Advanced enterprise analytics platform with real-time business intelligence,
KPI tracking, predictive analytics, custom reporting, and comprehensive
data visualization for enterprise-grade insights and decision making.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA-Influencer Project. All rights reserved.

LEGAL WARNING: This software and all associated intellectual property
belong exclusively to Fahed Mlaiel. Any unauthorized copying, redistribution,
reverse engineering, or commercial use without explicit written permission
will result in immediate legal action under international copyright laws.
"""

import asyncio
import logging
import json
import uuid
import hashlib
import time
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Union, Set, Tuple, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import aiofiles
import aioredis
import aiokafka
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, State, callback
import elasticsearch
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import prophet
import statsmodels.api as sm
from scipy import stats
import joblib

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """
Analytics metric types"""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    RATE = "rate"
    PERCENTAGE = "percentage"
    RATIO = "ratio"
    CURRENCY = "currency"
    DURATION = "duration"


class DataSource(Enum):
    """Data source types"""

    DATABASE = "database"
    API = "api"
    FILE = "file"
    STREAM = "stream"
    EXTERNAL_API = "external_api"
    WEBHOOK = "webhook"
    LOG_FILES = "log_files"
    METRICS_API = "metrics_api"


class VisualizationType(Enum):
    """Chart and visualization types"""

    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    SCATTER_PLOT = "scatter_plot"
    HEATMAP = "heatmap"
    HISTOGRAM = "histogram"
    BOX_PLOT = "box_plot"
    GAUGE = "gauge"
    KPI_CARD = "kpi_card"
    TABLE = "table"
    FUNNEL = "funnel"
    TREEMAP = "treemap"
    SANKEY = "sankey"


class ReportFormat(Enum):
    """Report output formats"""

    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"
    HTML = "html"
    POWERPOINT = "powerpoint"


class AggregationMethod(Enum):
    """Data aggregation methods"""

    SUM = "sum"
    AVERAGE = "average"
    COUNT = "count"
    MIN = "min"
    MAX = "max"
    MEDIAN = "median"
    PERCENTILE = "percentile"
    STANDARD_DEVIATION = "std"
    VARIANCE = "variance"


@dataclass
class KPIDefinition:
    """Key Performance Indicator definition"""
    kpi_id: str
    name: str
    description: str
    metric_type: MetricType
    calculation_formula: str
    data_sources: List[str]
    target_value: Optional[float] = None
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None
    unit: str = ""
    category: str = "general"
    tags: List[str] = field(default_factory=list)
    is_active: bool = True
    refresh_interval_minutes: int = 15
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class MetricDataPoint:
    """Single metric data point"""
    metric_id: str
    value: Union[float, int]
    timestamp: datetime
    dimensions: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert to dictionary"""
        return {
            'metric_id': self.metric_id,
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
            'dimensions': self.dimensions,
            'metadata': self.metadata,
            'tags': self.tags
        }


@dataclass
class DashboardWidget:
    """
Dashboard widget configuration"""
    widget_id: str
    title: str
    widget_type: VisualizationType
    kpi_ids: List[str]
    configuration: Dict[str, Any] = field(default_factory=dict)
    position: Dict[str, int] = field(default_factory=dict)  # x, y, width, height
    refresh_interval: int = 30  # seconds
    filters: Dict[str, Any] = field(default_factory=dict)
    is_visible: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Dashboard:
    """
Analytics dashboard configuration"""
    dashboard_id: str
    name: str
    description: str
    widgets: List[DashboardWidget]
    layout: Dict[str, Any] = field(default_factory=dict)
    access_permissions: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    is_public: bool = False
    auto_refresh: bool = True
    refresh_interval: int = 60  # seconds
    created_by: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ReportTemplate:
    """Report template configuration"""
    template_id: str
    name: str
    description: str
    report_type: str
    format: ReportFormat
    sections: List[Dict[str, Any]]
    parameters: Dict[str, Any] = field(default_factory=dict)
    schedule: Optional[Dict[str, Any]] = None
    recipients: List[str] = field(default_factory=list)
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class DataCollector:
    """
Advanced data collection and ingestion system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._data_sources: Dict[str, Dict[str, Any]] = {}
        self._collectors: Dict[str, Callable] = {}
        self._redis: Optional[aioredis.Redis] = None
        self._elasticsearch: Optional[elasticsearch.AsyncElasticsearch] = None
        
    async def initialize(self):
        """
Initialize data collector"""
        try:
            # Initialize Redis for caching
            if 'redis_url' in self.config:
                self._redis = aioredis.from_url(self.config['redis_url'])
                await self._redis.ping()
            
            # Initialize Elasticsearch for search and analytics
            if 'elasticsearch_url' in self.config:
                self._elasticsearch = elasticsearch.AsyncElasticsearch([self.config['elasticsearch_url']])
                await self._elasticsearch.ping()
            
            logger.info("Data collector initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize data collector: {e}")
            raise
    
    async def register_data_source(
        self,
        source_id: str,
        source_type: DataSource,
        connection_config: Dict[str, Any],
        collection_config: Dict[str, Any]
    ) -> bool:
        """Register a new data source"""
        try:
            self._data_sources[source_id] = {
                'source_type': source_type,
                'connection_config': connection_config,
                'collection_config': collection_config,
                'last_collection': None,
                'status': 'active'
            }
            
            # Set up collector based on source type
            if source_type == DataSource.DATABASE:
                await self._setup_database_collector(source_id, connection_config, collection_config)
            elif source_type == DataSource.API:
                await self._setup_api_collector(source_id, connection_config, collection_config)
            elif source_type == DataSource.STREAM:
                await self._setup_stream_collector(source_id, connection_config, collection_config)
            
            logger.info(f"Registered data source: {source_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register data source {source_id}: {e}")
            return False
    
    async def _setup_database_collector(self, source_id: str, connection_config: Dict[str, Any], collection_config: Dict[str, Any]):
        """Setup database data collector"""
        try:
            engine = create_async_engine(connection_config['connection_string'])
            
            async def collect_database_data():
                try:
                    # Setup async session
                    async_session = sessionmaker(engine, class_=AsyncSession)
                    async with async_session() as session:
                        query = collection_config['query']
                        result = await session.execute(text(query))
                        data = result.fetchall()
                        
                        # Collect metrics
                        metrics = {
                            "timestamp": datetime.utcnow(),
                            "metric_name": "collect_database_data",
                            "value": len(data) if data else 0,
                            "tags": self._get_metric_tags()
                        }
                        
                        # Store metrics
                        await self._store_metric(metrics)
                        
                        # Send to monitoring system
                        if hasattr(self, 'metrics_client'):
                            await self.metrics_client.send(metrics)
                        
                        logger.info(f"Metric collect_database_data collected")
                        return metrics
                        
                except Exception as e:
                    logger.error(f"Database collection failed: {e}")
                    return None
            
            # Schedule regular collection
            self._collectors[source_id] = collect_database_data
            
        except Exception as e:
            logger.error(f"Failed to setup database collector: {e}")
            raise
    
    async def _setup_api_collector(self, source_id: str, connection_config: Dict[str, Any], collection_config: Dict[str, Any]):
        """Setup API data collector"""
        try:
            async def collect_api_data():
                async with aiohttp.ClientSession() as session:
                    headers = connection_config.get('headers', {})
                    
                    async with session.get(
                        connection_config['url'],
                        headers=headers,
                        params=connection_config.get('params', {})
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            # Extract metrics from API response
                            metrics = []
                            for item in collection_config.get('data_path', [data]):
                                metric = MetricDataPoint(
                                    metric_id=collection_config.get('metric_id', source_id),
                                    value=item[collection_config['value_field']],
                                    timestamp=datetime.now(timezone.utc),
                                    dimensions=collection_config.get('dimensions', {}),
                                    metadata={'source': source_id, 'api_response': item}
                                )
                                metrics.append(metric)
                            
                            return metrics
                        else:
                            raise Exception(f"API request failed: {response.status}")
            
            self._collectors[source_id] = collect_api_data
            
        except Exception as e:
            logger.error(f"Failed to setup API collector: {e}")
            raise
    
    async def collect_metrics(self, source_id: Optional[str] = None) -> List[MetricDataPoint]:
        """Collect metrics from data sources"""
        try:
            all_metrics = []
            
            sources_to_collect = [source_id] if source_id else list(self._collectors.keys())
            
            for sid in sources_to_collect:
                if sid in self._collectors:
                    try:
                        metrics = await self._collectors[sid]()
                        all_metrics.extend(metrics)
                        
                        # Update last collection time
                        self._data_sources[sid]['last_collection'] = datetime.now(timezone.utc)
                        
                    except Exception as e:
                        logger.error(f"Failed to collect from source {sid}: {e}")
                        self._data_sources[sid]['status'] = 'error'
            
            return all_metrics
            
        except Exception as e:
            logger.error(f"Metrics collection failed: {e}")
            return []
    
    async def store_metrics(self, metrics: List[MetricDataPoint]) -> bool:
        """Store metrics in data stores"""
        try:
            # Store in Redis for real-time access
            if self._redis:
                for metric in metrics:
                    key = f"metric:{metric.metric_id}:{int(metric.timestamp.timestamp())}"
                    await self._redis.setex(key, 3600, json.dumps(metric.to_dict()))
            
            # Store in Elasticsearch for analytics
            if self._elasticsearch:
                bulk_data = []
                for metric in metrics:
                    bulk_data.extend([
                        {"index": {"_index": "analytics-metrics"}},
                        metric.to_dict()
                    ])
                
                if bulk_data:
                    await self._elasticsearch.bulk(body=bulk_data)
            
            logger.info(f"Stored {len(metrics)} metrics")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store metrics: {e}")
            return False


class KPITracker:
    """Advanced KPI tracking and calculation system"""
    
    def __init__(self, data_collector: DataCollector):
        self.data_collector = data_collector
        self._kpi_definitions: Dict[str, KPIDefinition] = {}
        self._kpi_values: Dict[str, List[float]] = {}
        self._kpi_alerts: Dict[str, List[Dict[str, Any]]] = {}
        
    async def register_kpi(self, kpi_definition: KPIDefinition) -> bool:
        """
Register a new KPI"""
        try:
            self._kpi_definitions[kpi_definition.kpi_id] = kpi_definition
            self._kpi_values[kpi_definition.kpi_id] = []
            self._kpi_alerts[kpi_definition.kpi_id] = []
            
            logger.info(f"Registered KPI: {kpi_definition.kpi_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register KPI: {e}")
            return False
    
    async def calculate_kpi(self, kpi_id: str, time_range: Optional[Tuple[datetime, datetime]] = None) -> Optional[float]:
        """Calculate KPI value"""
        try:
            if kpi_id not in self._kpi_definitions:
                raise ValueError(f"KPI not found: {kpi_id}")
            
            kpi_def = self._kpi_definitions[kpi_id]
            
            # Collect data from specified sources
            metrics = []
            for source_id in kpi_def.data_sources:
                source_metrics = await self.data_collector.collect_metrics(source_id)
                metrics.extend(source_metrics)
            
            # Filter by time range if specified
            if time_range:
                start_time, end_time = time_range
                metrics = [m for m in metrics if start_time <= m.timestamp <= end_time]
            
            if not metrics:
                return None
            
            # Calculate KPI value based on formula
            values = [m.value for m in metrics]
            calculated_value = await self._apply_calculation_formula(kpi_def.calculation_formula, values)
            
            # Store calculated value
            self._kpi_values[kpi_id].append(calculated_value)
            
            # Check for alerts
            await self._check_kpi_alerts(kpi_id, calculated_value)
            
            return calculated_value
            
        except Exception as e:
            logger.error(f"KPI calculation failed for {kpi_id}: {e}")
            return None
    
    async def _apply_calculation_formula(self, formula: str, values: List[float]) -> float:
        """Apply calculation formula to values"""
        try:
            if formula == "sum":
                return sum(values)
            elif formula == "average" or formula == "mean":
                return np.mean(values)
            elif formula == "count":
                return len(values)
            elif formula == "min":
                return min(values)
            elif formula == "max":
                return max(values)
            elif formula == "median":
                return np.median(values)
            elif formula == "std":
                return np.std(values)
            elif formula.startswith("percentile_"):
                percentile = int(formula.split("_")[1])
                return np.percentile(values, percentile)
            else:
                # Custom formula - evaluate safely
                # In production, use a more secure formula evaluator
                return eval(formula.replace("values", str(values)))
                
        except Exception as e:
            logger.error(f"Formula calculation failed: {e}")
            return 0.0
    
    async def _check_kpi_alerts(self, kpi_id: str, value: float):
        """Check KPI value against thresholds and generate alerts"""
        try:
            kpi_def = self._kpi_definitions[kpi_id]
            
            alert_level = None
            if kpi_def.threshold_critical and value >= kpi_def.threshold_critical:
                alert_level = "critical"
            elif kpi_def.threshold_warning and value >= kpi_def.threshold_warning:
                alert_level = "warning"
            
            if alert_level:
                alert = {
                    'kpi_id': kpi_id,
                    'level': alert_level,
                    'value': value,
                    'threshold': kpi_def.threshold_critical if alert_level == "critical" else kpi_def.threshold_warning,
                    'timestamp': datetime.now(timezone.utc),
                    'message': f"KPI {kpi_def.name} has {alert_level} value: {value}"
                }
                
                self._kpi_alerts[kpi_id].append(alert)
                logger.warning(f"KPI alert generated: {alert['message']}")
                
        except Exception as e:
            logger.error(f"KPI alert check failed: {e}")
    
    async def get_kpi_history(self, kpi_id: str, time_range: Tuple[datetime, datetime]) -> List[Dict[str, Any]]:
        """Get KPI historical data"""
        try:
            # In real implementation, this would query the data store
            # For now, return recent calculated values
            if kpi_id in self._kpi_values:
                values = self._kpi_values[kpi_id]
                return [
                    {
                        'timestamp': datetime.now(timezone.utc) - timedelta(minutes=i*15),
                        'value': value
                    }
                    for i, value in enumerate(reversed(values[-100:]))  # Last 100 values
                ]
            return []
            
        except Exception as e:
            logger.error(f"Failed to get KPI history: {e}")
            return []
    
    async def get_kpi_alerts(self, kpi_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get KPI alerts"""
        try:
            if kpi_id:
                return self._kpi_alerts.get(kpi_id, [])
            else:
                all_alerts = []
                for alerts in self._kpi_alerts.values():
                    all_alerts.extend(alerts)
                return sorted(all_alerts, key=lambda x: x['timestamp'], reverse=True)
                
        except Exception as e:
            logger.error(f"Failed to get KPI alerts: {e}")
            return []


class BusinessIntelligence:
    """Advanced business intelligence and predictive analytics"""
    
    def __init__(self, data_collector: DataCollector):
        self.data_collector = data_collector
        self._models: Dict[str, Any] = {}
        self._predictions: Dict[str, Any] = {}
        
    async def create_predictive_model(
        self,
        model_id: str,
        model_type: str,
        features: List[str],
        target: str,
        training_data: pd.DataFrame
    ) -> bool:
        """
Create predictive analytics model"""
        try:
            # Prepare data
            X = training_data[features]
            y = training_data[target]
            
            # Handle missing values
            X = X.fillna(X.mean())
            y = y.fillna(y.mean())
            
            # Scale features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Create model based on type
            if model_type == "linear_regression":
                model = LinearRegression()
            elif model_type == "random_forest":
                model = RandomForestRegressor(n_estimators=100, random_state=42)
            elif model_type == "time_series":
                # Use Prophet for time series forecasting
                model = prophet.Prophet()
            else:
                raise ValueError(f"Unsupported model type: {model_type}")
            
            # Train model
            if model_type == "time_series":
                # Prophet expects specific column names
                ts_data = training_data[['timestamp', target]].rename(columns={'timestamp': 'ds', target: 'y'})
                model.fit(ts_data)
            else:
                model.fit(X_scaled, y)
            
            # Store model and scaler
            self._models[model_id] = {
                'model': model,
                'scaler': scaler if model_type != "time_series" else None,
                'model_type': model_type,
                'features': features,
                'target': target,
                'trained_at': datetime.now(timezone.utc)
            }
            
            logger.info(f"Created predictive model: {model_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create predictive model: {e}")
            return False
    
    async def generate_prediction(
        self,
        model_id: str,
        input_data: Union[pd.DataFrame, Dict[str, Any]],
        forecast_periods: int = 30
    ) -> Optional[Dict[str, Any]]:
        """Generate prediction using trained model"""
        try:
            if model_id not in self._models:
                raise ValueError(f"Model not found: {model_id}")
            
            model_info = self._models[model_id]
            model = model_info['model']
            model_type = model_info['model_type']
            
            if model_type == "time_series":
                # Time series forecasting
                future = model.make_future_dataframe(periods=forecast_periods)
                forecast = model.predict(future)
                
                prediction_result = {
                    'model_id': model_id,
                    'type': 'time_series_forecast',
                    'forecast': forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].to_dict('records'),
                    'generated_at': datetime.now(timezone.utc).isoformat()
                }
            else:
                # Regular ML prediction
                if isinstance(input_data, dict):
                    input_df = pd.DataFrame([input_data])
                else:
                    input_df = input_data
                
                # Prepare features
                X = input_df[model_info['features']]
                X = X.fillna(X.mean())
                
                # Scale features
                if model_info['scaler']:
                    X_scaled = model_info['scaler'].transform(X)
                else:
                    X_scaled = X
                
                # Make prediction
                predictions = model.predict(X_scaled)
                
                prediction_result = {
                    'model_id': model_id,
                    'type': 'ml_prediction',
                    'predictions': predictions.tolist(),
                    'input_features': X.to_dict('records'),
                    'generated_at': datetime.now(timezone.utc).isoformat()
                }
            
            # Store prediction
            self._predictions[f"{model_id}_{datetime.now().timestamp()}"] = prediction_result
            
            return prediction_result
            
        except Exception as e:
            logger.error(f"Prediction generation failed: {e}")
            return None
    
    async def detect_anomalies(self, data: pd.DataFrame, method: str = "isolation_forest") -> Dict[str, Any]:
        """Detect anomalies in data"""
        try:
            if method == "isolation_forest":
                detector = IsolationForest(contamination=0.1, random_state=42)
                anomaly_scores = detector.fit_predict(data.select_dtypes(include=[np.number]))
                
            elif method == "statistical":
                # Use statistical methods (Z-score)
                z_scores = np.abs(stats.zscore(data.select_dtypes(include=[np.number])))
                anomaly_scores = (z_scores > 3).any(axis=1).astype(int) * -1 + 1
                
            else:
                raise ValueError(f"Unsupported anomaly detection method: {method}")
            
            # Find anomalies
            anomaly_indices = np.where(anomaly_scores == -1)[0]
            anomalies = data.iloc[anomaly_indices]
            
            result = {
                'method': method,
                'total_records': len(data),
                'anomalies_detected': len(anomalies),
                'anomaly_percentage': (len(anomalies) / len(data)) * 100,
                'anomaly_indices': anomaly_indices.tolist(),
                'anomalies': anomalies.to_dict('records'),
                'detected_at': datetime.now(timezone.utc).isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            return []
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
            return {}
    
    async def perform_cohort_analysis(self, data: pd.DataFrame, user_col: str, date_col: str, value_col: str) -> Dict[str, Any]:
        """Perform cohort analysis"""
        try:
            # Create cohort analysis
            data[date_col] = pd.to_datetime(data[date_col])
            data['cohort_month'] = data[date_col].dt.to_period('M')
            data['period_number'] = (data[date_col].dt.to_period('M') - data.groupby(user_col)[date_col].transform('min').dt.to_period('M')).apply(attrgetter('n'))
            
            # Create cohort table
            cohort_data = data.groupby(['cohort_month', 'period_number'])[user_col].nunique().reset_index()
            cohort_table = cohort_data.pivot(index='cohort_month', columns='period_number', values=user_col)
            
            # Calculate retention rates
            cohort_sizes = cohort_table.iloc[:, 0]
            retention_table = cohort_table.divide(cohort_sizes, axis=0)
            
            result = {
                'cohort_table': cohort_table.to_dict(),
                'retention_table': retention_table.to_dict(),
                'analysis_date': datetime.now(timezone.utc).isoformat(),
                'total_cohorts': len(cohort_table),
                'average_retention': {
                    'month_1': retention_table.iloc[:, 1].mean() if len(retention_table.columns) > 1 else 0,
                    'month_3': retention_table.iloc[:, 3].mean() if len(retention_table.columns) > 3 else 0,
                    'month_6': retention_table.iloc[:, 6].mean() if len(retention_table.columns) > 6 else 0
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Cohort analysis failed: {e}")
            return {}


class VisualizationEngine:
    """Advanced data visualization and charting engine"""
    
    def __init__(self):
        self._chart_templates = {
            VisualizationType.LINE_CHART: self._create_line_chart,
            VisualizationType.BAR_CHART: self._create_bar_chart,
            VisualizationType.PIE_CHART: self._create_pie_chart,
            VisualizationType.SCATTER_PLOT: self._create_scatter_plot,
            VisualizationType.HEATMAP: self._create_heatmap,
            VisualizationType.GAUGE: self._create_gauge,
            VisualizationType.KPI_CARD: self._create_kpi_card
        }
    
    async def create_visualization(
        self,
        chart_type: VisualizationType,
        data: pd.DataFrame,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
Create visualization from data"""
        try:
            if chart_type not in self._chart_templates:
                raise ValueError(f"Unsupported chart type: {chart_type}")
            
            chart_func = self._chart_templates[chart_type]
            chart = await chart_func(data, config)
            
            return {
                'chart_type': chart_type.value,
                'chart_data': chart.to_dict() if hasattr(chart, 'to_dict') else chart,
                'config': config,
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Visualization creation failed: {e}")
            return {}
    
    async def _create_line_chart(self, data: pd.DataFrame, config: Dict[str, Any]) -> go.Figure:
        """Create line chart"""
        fig = go.Figure()
        
        x_col = config.get('x_column', data.columns[0])
        y_col = config.get('y_column', data.columns[1])
        
        fig.add_trace(go.Scatter(
            x=data[x_col],
            y=data[y_col],
            mode='lines+markers',
            name=config.get('series_name', y_col),
            line=dict(color=config.get('color', '#1f77b4'))
        ))
        
        fig.update_layout(
            title=config.get('title', 'Line Chart'),
            xaxis_title=config.get('x_title', x_col),
            yaxis_title=config.get('y_title', y_col),
            template='plotly_white'
        )
        
        return fig
    
    async def _create_bar_chart(self, data: pd.DataFrame, config: Dict[str, Any]) -> go.Figure:
        """
Create bar chart"""
        fig = go.Figure()
        
        x_col = config.get('x_column', data.columns[0])
        y_col = config.get('y_column', data.columns[1])
        
        fig.add_trace(go.Bar(
            x=data[x_col],
            y=data[y_col],
            name=config.get('series_name', y_col),
            marker_color=config.get('color', '#1f77b4')
        ))
        
        fig.update_layout(
            title=config.get('title', 'Bar Chart'),
            xaxis_title=config.get('x_title', x_col),
            yaxis_title=config.get('y_title', y_col),
            template='plotly_white'
        )
        
        return fig
    
    async def _create_pie_chart(self, data: pd.DataFrame, config: Dict[str, Any]) -> go.Figure:
        """
Create pie chart"""
        fig = go.Figure()
        
        labels_col = config.get('labels_column', data.columns[0])
        values_col = config.get('values_column', data.columns[1])
        
        fig.add_trace(go.Pie(
            labels=data[labels_col],
            values=data[values_col],
            name=config.get('series_name', 'Distribution')
        ))
        
        fig.update_layout(
            title=config.get('title', 'Pie Chart'),
            template='plotly_white'
        )
        
        return fig
    
    async def _create_scatter_plot(self, data: pd.DataFrame, config: Dict[str, Any]) -> go.Figure:
        """
Create scatter plot"""
        fig = go.Figure()
        
        x_col = config.get('x_column', data.columns[0])
        y_col = config.get('y_column', data.columns[1])
        
        fig.add_trace(go.Scatter(
            x=data[x_col],
            y=data[y_col],
            mode='markers',
            name=config.get('series_name', 'Data Points'),
            marker=dict(
                color=config.get('color', '#1f77b4'),
                size=config.get('marker_size', 8)
            )
        ))
        
        fig.update_layout(
            title=config.get('title', 'Scatter Plot'),
            xaxis_title=config.get('x_title', x_col),
            yaxis_title=config.get('y_title', y_col),
            template='plotly_white'
        )
        
        return fig
    
    async def _create_heatmap(self, data: pd.DataFrame, config: Dict[str, Any]) -> go.Figure:
        """
Create heatmap"""
        fig = go.Figure()
        
        # Assume data is already in matrix form or pivot as needed
        fig.add_trace(go.Heatmap(
            z=data.values,
            x=data.columns,
            y=data.index,
            colorscale=config.get('colorscale', 'Viridis'),
            name='Heatmap'
        ))
        
        fig.update_layout(
            title=config.get('title', 'Heatmap'),
            template='plotly_white'
        )
        
        return fig
    
    async def _create_gauge(self, data: pd.DataFrame, config: Dict[str, Any]) -> go.Figure:
        """
Create gauge chart"""
        fig = go.Figure()
        
        value = config.get('value', data.iloc[0, 0] if not data.empty else 0)
        max_value = config.get('max_value', 100)
        
        fig.add_trace(go.Indicator(
            mode="gauge+number+delta",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': config.get('title', 'Gauge')},
            delta={'reference': config.get('reference_value', 0)},
            gauge={
                'axis': {'range': [None, max_value]},
                'bar': {'color': config.get('color', '#1f77b4')},
                'steps': [
                    {'range': [0, max_value * 0.5], 'color': "lightgray"},
                    {'range': [max_value * 0.5, max_value * 0.8], 'color': "gray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': max_value * 0.9
                }
            }
        ))
        
        return fig
    
    async def _create_kpi_card(self, data: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create KPI card"""
        value = config.get('value', data.iloc[0, 0] if not data.empty else 0)
        
        kpi_card = {
            'type': 'kpi_card',
            'title': config.get('title', 'KPI'),
            'value': value,
            'unit': config.get('unit', ''),
            'change': config.get('change', 0),
            'change_type': config.get('change_type', 'neutral'),  # positive, negative, neutral
            'target': config.get('target'),
            'format': config.get('format', 'number'),
            'color': config.get('color', '#1f77b4')
        }
        
        return kpi_card


class ReportGenerator:
    """
Advanced report generation system"""
    
    def __init__(self, visualization_engine: VisualizationEngine):
        self.visualization_engine = visualization_engine
        self._report_templates: Dict[str, ReportTemplate] = {}
        
    async def create_report_template(self, template: ReportTemplate) -> bool:
        """
Create report template"""
        try:
            self._report_templates[template.template_id] = template
            logger.info(f"Created report template: {template.template_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to create report template: {e}")
            return False
    
    async def generate_report(
        self,
        template_id: str,
        data_sources: Dict[str, pd.DataFrame],
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate report from template"""
        try:
            if template_id not in self._report_templates:
                raise ValueError(f"Report template not found: {template_id}")
            
            template = self._report_templates[template_id]
            parameters = parameters or {}
            
            # Generate report sections
            report_sections = []
            
            for section_config in template.sections:
                section = await self._generate_report_section(section_config, data_sources, parameters)
                report_sections.append(section)
            
            # Compile report
            report = {
                'template_id': template_id,
                'title': template.name,
                'description': template.description,
                'format': template.format.value,
                'sections': report_sections,
                'parameters': parameters,
                'generated_at': datetime.now(timezone.utc).isoformat(),
                'metadata': {
                    'total_sections': len(report_sections),
                    'data_sources': list(data_sources.keys())
                }
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return {}
    
    async def _generate_report_section(
        self,
        section_config: Dict[str, Any],
        data_sources: Dict[str, pd.DataFrame],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate individual report section"""
        try:
            section_type = section_config.get('type', 'text')
            
            if section_type == 'visualization':
                # Create visualization
                data_source_name = section_config['data_source']
                if data_source_name not in data_sources:
                    raise ValueError(f"Data source not found: {data_source_name}")
                
                data = data_sources[data_source_name]
                chart_type = VisualizationType(section_config['chart_type'])
                chart_config = section_config.get('chart_config', {})
                
                visualization = await self.visualization_engine.create_visualization(
                    chart_type, data, chart_config
                )
                
                section = {
                    'type': 'visualization',
                    'title': section_config.get('title', ''),
                    'visualization': visualization
                }
                
            elif section_type == 'table':
                # Create data table
                data_source_name = section_config['data_source']
                if data_source_name not in data_sources:
                    raise ValueError(f"Data source not found: {data_source_name}")
                
                data = data_sources[data_source_name]
                
                # Apply filters if specified
                filters = section_config.get('filters', {})
                for column, filter_value in filters.items():
                    if column in data.columns:
                        data = data[data[column] == filter_value]
                
                section = {
                    'type': 'table',
                    'title': section_config.get('title', ''),
                    'data': data.to_dict('records'),
                    'columns': data.columns.tolist()
                }
                
            elif section_type == 'text':
                # Create text section
                section = {
                    'type': 'text',
                    'title': section_config.get('title', ''),
                    'content': section_config.get('content', '')
                }
                
            elif section_type == 'summary':
                # Create summary statistics
                data_source_name = section_config['data_source']
                if data_source_name not in data_sources:
                    raise ValueError(f"Data source not found: {data_source_name}")
                
                data = data_sources[data_source_name]
                summary = data.describe().to_dict()
                
                section = {
                    'type': 'summary',
                    'title': section_config.get('title', 'Summary Statistics'),
                    'summary': summary
                }
                
            else:
                section = {
                    'type': 'unknown',
                    'title': section_config.get('title', ''),
                    'error': f"Unknown section type: {section_type}"
                }
            
            return section
            
        except Exception as e:
            logger.error(f"Report section generation failed: {e}")
            return {
                'type': 'error',
                'title': section_config.get('title', ''),
                'error': str(e)
            }


class EnterpriseAnalytics:
    """Main enterprise analytics orchestrator"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.data_collector = DataCollector(self.config)
        self.kpi_tracker = KPITracker(self.data_collector)
        self.business_intelligence = BusinessIntelligence(self.data_collector)
        self.visualization_engine = VisualizationEngine()
        self.report_generator = ReportGenerator(self.visualization_engine)
        self._dashboards: Dict[str, Dashboard] = {}
        
    async def initialize(self):
        """
Initialize analytics system"""
        try:
            await self.data_collector.initialize()
            logger.info("Enterprise analytics system initialized")
        except Exception as e:
            logger.error(f"Failed to initialize analytics system: {e}")
            raise
    
    async def create_dashboard(
        self,
        organization_id: str,
        dashboard_config: Dict[str, Any]
    ) -> str:
        """Create analytics dashboard"""
        try:
            dashboard_id = f"dashboard_{uuid.uuid4().hex[:12]}"
            
            # Create widgets
            widgets = []
            for widget_config in dashboard_config.get('widgets', []):
                widget = DashboardWidget(
                    widget_id=f"widget_{uuid.uuid4().hex[:8]}",
                    title=widget_config['title'],
                    widget_type=VisualizationType(widget_config['type']),
                    kpi_ids=widget_config.get('kpi_ids', []),
                    configuration=widget_config.get('configuration', {}),
                    position=widget_config.get('position', {}),
                    refresh_interval=widget_config.get('refresh_interval', 30)
                )
                widgets.append(widget)
            
            # Create dashboard
            dashboard = Dashboard(
                dashboard_id=dashboard_id,
                name=dashboard_config['name'],
                description=dashboard_config.get('description', ''),
                widgets=widgets,
                layout=dashboard_config.get('layout', {}),
                access_permissions=dashboard_config.get('access_permissions', []),
                is_public=dashboard_config.get('is_public', False),
                created_by=organization_id
            )
            
            self._dashboards[dashboard_id] = dashboard
            
            logger.info(f"Created dashboard: {dashboard_id}")
            return dashboard_id
            
        except Exception as e:
            logger.error(f"Failed to create dashboard: {e}")
            raise
    
    async def get_dashboard_data(self, dashboard_id: str) -> Dict[str, Any]:
        """Get dashboard data"""
        try:
            if dashboard_id not in self._dashboards:
                raise ValueError(f"Dashboard not found: {dashboard_id}")
            
            dashboard = self._dashboards[dashboard_id]
            dashboard_data = {
                'dashboard_id': dashboard_id,
                'name': dashboard.name,
                'description': dashboard.description,
                'widgets': [],
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
            
            # Get data for each widget
            for widget in dashboard.widgets:
                widget_data = await self._get_widget_data(widget)
                dashboard_data['widgets'].append(widget_data)
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Failed to get dashboard data: {e}")
            return {}
    
    async def _get_widget_data(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Get data for individual widget"""
        try:
            widget_data = {
                'widget_id': widget.widget_id,
                'title': widget.title,
                'type': widget.widget_type.value,
                'data': None,
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
            
            # Get KPI data
            if widget.kpi_ids:
                kpi_data = []
                for kpi_id in widget.kpi_ids:
                    value = await self.kpi_tracker.calculate_kpi(kpi_id)
                    if value is not None:
                        kpi_data.append({
                            'kpi_id': kpi_id,
                            'value': value,
                            'timestamp': datetime.now(timezone.utc).isoformat()
                        })
                
                widget_data['data'] = kpi_data
            
            return widget_data
            
        except Exception as e:
            logger.error(f"Failed to get widget data: {e}")
            return {
                'widget_id': widget.widget_id,
                'title': widget.title,
                'type': widget.widget_type.value,
                'error': str(e),
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
    
    async def run_analytics_pipeline(self, organization_id: str) -> Dict[str, Any]:
        """Run complete analytics pipeline"""
        try:
            pipeline_id = f"pipeline_{uuid.uuid4().hex[:12]}"
            
            # Collect metrics
            metrics = await self.data_collector.collect_metrics()
            await self.data_collector.store_metrics(metrics)
            
            # Calculate all KPIs
            kpi_results = {}
            for kpi_id in self.kpi_tracker._kpi_definitions.keys():
                value = await self.kpi_tracker.calculate_kpi(kpi_id)
                if value is not None:
                    kpi_results[kpi_id] = value
            
            # Run anomaly detection
            if metrics:
                metrics_df = pd.DataFrame([m.to_dict() for m in metrics])
                anomalies = await self.business_intelligence.detect_anomalies(
                    metrics_df.select_dtypes(include=[np.number])
                )
            else:
                anomalies = {}
            
            pipeline_result = {
                'pipeline_id': pipeline_id,
                'organization_id': organization_id,
                'metrics_collected': len(metrics),
                'kpi_results': kpi_results,
                'anomalies': anomalies,
                'executed_at': datetime.now(timezone.utc).isoformat(),
                'status': 'completed'
            }
            
            return pipeline_result
            
        except Exception as e:
            logger.error(f"Analytics pipeline failed: {e}")
            return {
                'pipeline_id': f"pipeline_{uuid.uuid4().hex[:12]}",
                'organization_id': organization_id,
                'status': 'failed',
                'error': str(e),
                'executed_at': datetime.now(timezone.utc).isoformat()
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for analytics system"""
        try:
            return {
                'status': 'healthy',
                'components': {
                    'data_collector': 'active',
                    'kpi_tracker': 'active',
                    'business_intelligence': 'active',
                    'visualization_engine': 'active',
                    'report_generator': 'active'
                },
                'registered_kpis': len(self.kpi_tracker._kpi_definitions),
                'active_dashboards': len(self._dashboards),
                'predictive_models': len(self.business_intelligence._models),
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'score': 1.0
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'score': 0.0
            }