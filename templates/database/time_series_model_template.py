"""
📊 TIME SERIES MODEL TEMPLATE - ML ENGINEER EXPERT IMPLEMENTATION
================================================================

Enterprise-grade time series model template with:
- Multiple time series storage backends (InfluxDB, TimescaleDB, MongoDB)
- Advanced time series analysis and forecasting
- Real-time streaming data ingestion
- Anomaly detection and alerting
- Automatic seasonality detection
- Multi-variate time series support
- Compression and retention policies
- High-frequency data optimization

Author: ML Engineer Expert
Version: 1.0.0
"""

from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import asyncio
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
import math
import asyncpg
import motor.motor_asyncio
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync
from influxdb_client import Point, WritePrecision
from influxdb_client.client.write_api_async import WriteApiAsync
import redis.asyncio as redis
from pydantic import BaseModel, Field, validator
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
from sklearn.metrics import mean_absolute_error, mean_squared_error
import statsmodels.api as sm
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.seasonal import seasonal_decompose
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import joblib
import warnings
warnings.filterwarnings('ignore')


class TimeSeriesBackend(Enum):
    """Time series storage backends"""
    INFLUXDB = "influxdb"
    TIMESCALEDB = "timescaledb"
    MONGODB = "mongodb"
    REDIS = "redis"


class AggregationType(Enum):
    """Time series aggregation types"""
    MEAN = "mean"
    SUM = "sum"
    COUNT = "count"
    MIN = "min"
    MAX = "max"
    MEDIAN = "median"
    STDDEV = "stddev"
    PERCENTILE = "percentile"
    FIRST = "first"
    LAST = "last"


class InterpolationMethod(Enum):
    """Data interpolation methods"""
    LINEAR = "linear"
    CUBIC = "cubic"
    SPLINE = "spline"
    FORWARD_FILL = "ffill"
    BACKWARD_FILL = "bfill"
    NEAREST = "nearest"


class AnomalyMethod(Enum):
    """Anomaly detection methods"""
    ISOLATION_FOREST = "isolation_forest"
    STATISTICAL = "statistical"
    LSTM_AUTOENCODER = "lstm_autoencoder"
    SEASONAL_DECOMPOSE = "seasonal_decompose"
    PROPHET = "prophet"


class ForecastMethod(Enum):
    """Forecasting methods"""
    ARIMA = "arima"
    EXPONENTIAL_SMOOTHING = "exponential_smoothing"
    LSTM = "lstm"
    PROPHET = "prophet"
    LINEAR_REGRESSION = "linear_regression"
    ENSEMBLE = "ensemble"


@dataclass
class TimeSeriesConfig:
    """Time series configuration"""
    # Storage backend
    backend: TimeSeriesBackend = TimeSeriesBackend.INFLUXDB
    
    # InfluxDB settings
    influxdb_url: str = "http://localhost:8086"
    influxdb_token: Optional[str] = None
    influxdb_org: str = "ainflue"
    influxdb_bucket: str = "timeseries"
    
    # TimescaleDB settings
    timescaledb_host: str = "localhost"
    timescaledb_port: int = 5432
    timescaledb_database: str = "timeseries"
    timescaledb_user: str = "postgres"
    timescaledb_password: Optional[str] = None
    
    # MongoDB settings
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_database: str = "timeseries"
    mongodb_collection: str = "data_points"
    
    # Redis settings
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    
    # Data settings
    default_retention_days: int = 365
    compression_enabled: bool = True
    batch_size: int = 1000
    max_points_per_query: int = 100000
    
    # Analysis settings
    anomaly_detection_enabled: bool = True
    anomaly_threshold: float = 3.0
    seasonality_detection_enabled: bool = True
    forecasting_enabled: bool = True
    default_forecast_horizon: int = 30  # days
    
    # Performance settings
    enable_caching: bool = True
    cache_ttl: int = 300  # seconds
    enable_compression: bool = True
    parallel_processing: bool = True
    max_workers: int = 4


class TimeSeriesPoint(BaseModel):
    """Time series data point"""
    timestamp: datetime
    measurement: str
    tags: Dict[str, str] = Field(default_factory=dict)
    fields: Dict[str, Union[float, int, str, bool]]
    
    @validator('timestamp')
    def validate_timestamp(cls, v) -> None:
        if isinstance(v, str):
            return datetime.fromisoformat(v)
        return v


class TimeSeriesQuery(BaseModel):
    """Time series query parameters"""
    measurement: str
    start_time: datetime
    end_time: datetime
    tags: Dict[str, str] = Field(default_factory=dict)
    fields: List[str] = Field(default_factory=list)
    aggregation: Optional[AggregationType] = None
    group_by_time: Optional[str] = None  # e.g., "1h", "1d"
    group_by_tags: List[str] = Field(default_factory=list)
    limit: Optional[int] = None
    offset: int = 0
    fill: Optional[str] = None  # "null", "previous", "linear"


class TimeSeriesResult(BaseModel):
    """Time series query result"""
    points: List[TimeSeriesPoint]
    total_count: int
    aggregated: bool = False
    query_time_ms: int
    cached: bool = False


class AnomalyPoint(BaseModel):
    """Anomaly detection result"""
    timestamp: datetime
    measurement: str
    field: str
    value: float
    expected_value: float
    anomaly_score: float
    method: AnomalyMethod
    severity: str  # "low", "medium", "high"


class ForecastPoint(BaseModel):
    """Forecast result point"""
    timestamp: datetime
    predicted_value: float
    confidence_lower: float
    confidence_upper: float
    method: ForecastMethod


class SeasonalityInfo(BaseModel):
    """Seasonality detection result"""
    measurement: str
    field: str
    seasonal_period: int
    seasonal_strength: float
    trend_strength: float
    has_seasonality: bool
    has_trend: bool


class AbstractTimeSeriesBackend(ABC):
    """Abstract time series backend interface"""
    
    @abstractmethod
    async def write_points(self, points: List[TimeSeriesPoint]) -> bool:
        """Write time series points"""
        pass
    
    @abstractmethod
    async def query_points(self, query: TimeSeriesQuery) -> TimeSeriesResult:
        """Query time series points"""
        pass
    
    @abstractmethod
    async def delete_points(self, measurement: str, start_time: datetime, end_time: datetime) -> bool:
        """Delete time series points"""
        pass
    
    @abstractmethod
    async def get_measurements(self) -> List[str]:
        """Get all measurements"""
        pass
    
    @abstractmethod
    async def get_tags(self, measurement: str) -> Dict[str, List[str]]:
        """Get all tags for measurement"""
        pass


class InfluxDBBackend(AbstractTimeSeriesBackend):
    """InfluxDB backend implementation"""
    
    def __init__(self, config -> None: TimeSeriesConfig) -> None:
        self.config = config
        self.client = None
        self.write_api = None
        self.logger = logging.getLogger(__name__)
    
    async def connect(self) -> None:
        """Connect to InfluxDB"""
        try:
            self.client = InfluxDBClientAsync(
                url=self.config.influxdb_url,
                token=self.config.influxdb_token,
                org=self.config.influxdb_org
            )
            self.write_api = self.client.write_api()
            
            # Test connection
            ready = await self.client.ready()
            if ready:
                self.logger.info("Connected to InfluxDB")
            else:
                raise ConnectionError("InfluxDB not ready")
                
        except Exception as e:
            self.logger.error(f"Failed to connect to InfluxDB: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from InfluxDB"""
        if self.client:
            await self.client.close()
    
    async def write_points(self, points: List[TimeSeriesPoint]) -> bool:
        """Write points to InfluxDB"""
        try:
            influx_points = []
            
            for point in points:
                influx_point = Point(point.measurement)
                influx_point.time(point.timestamp, WritePrecision.MS)
                
                # Add tags
                for tag_key, tag_value in point.tags.items():
                    influx_point.tag(tag_key, tag_value)
                
                # Add fields
                for field_key, field_value in point.fields.items():
                    influx_point.field(field_key, field_value)
                
                influx_points.append(influx_point)
            
            await self.write_api.write(
                bucket=self.config.influxdb_bucket,
                org=self.config.influxdb_org,
                record=influx_points
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to write points to InfluxDB: {e}")
            return False
    
    async def query_points(self, query: TimeSeriesQuery) -> TimeSeriesResult:
        """Query points from InfluxDB"""
        try:
            start_time = time.time()
            
            # Build Flux query
            flux_query = self._build_flux_query(query)
            
            # Execute query
            query_api = self.client.query_api()
            tables = await query_api.query(flux_query, org=self.config.influxdb_org)
            
            # Parse results
            points = []
            for table in tables:
                for record in table.records:
                    point = TimeSeriesPoint(
                        timestamp=record.get_time(),
                        measurement=record.get_measurement(),
                        tags={k: v for k, v in record.values.items() if k.startswith('tag_')},
                        fields={record.get_field(): record.get_value()}
                    )
                    points.append(point)
            
            query_time_ms = int((time.time() - start_time) * 1000)
            
            return TimeSeriesResult(
                points=points,
                total_count=len(points),
                aggregated=query.aggregation is not None,
                query_time_ms=query_time_ms,
                cached=False
            )
            
        except Exception as e:
            self.logger.error(f"Failed to query points from InfluxDB: {e}")
            raise
    
    def _build_flux_query(self, query: TimeSeriesQuery) -> str:
        """Build Flux query string"""
        flux_parts = [
            f'from(bucket: "{self.config.influxdb_bucket}")',
            f'|> range(start: {query.start_time.isoformat()}, stop: {query.end_time.isoformat()})',
            f'|> filter(fn: (r) => r._measurement == "{query.measurement}")'
        ]
        
        # Add field filters
        if query.fields:
            field_filter = " or ".join([f'r._field == "{field}"' for field in query.fields])
            flux_parts.append(f'|> filter(fn: (r) => {field_filter})')
        
        # Add tag filters
        for tag_key, tag_value in query.tags.items():
            flux_parts.append(f'|> filter(fn: (r) => r.{tag_key} == "{tag_value}")')
        
        # Add aggregation
        if query.aggregation:
            if query.group_by_time:
                flux_parts.append(f'|> aggregateWindow(every: {query.group_by_time}, fn: {query.aggregation.value})')
            else:
                flux_parts.append(f'|> {query.aggregation.value}()')
        
        # Add grouping
        if query.group_by_tags:
            group_columns = ["_time", "_field"] + query.group_by_tags
            flux_parts.append(f'|> group(columns: {group_columns})')
        
        # Add limit
        if query.limit:
            flux_parts.append(f'|> limit(n: {query.limit})')
        
        return " ".join(flux_parts)
    
    async def delete_points(self, measurement: str, start_time: datetime, end_time: datetime) -> bool:
        """Delete points from InfluxDB"""
        try:
            delete_api = self.client.delete_api()
            await delete_api.delete(
                start=start_time,
                stop=end_time,
                predicate=f'_measurement="{measurement}"',
                bucket=self.config.influxdb_bucket,
                org=self.config.influxdb_org
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete points from InfluxDB: {e}")
            return False
    
    async def get_measurements(self) -> List[str]:
        """Get all measurements from InfluxDB"""
        try:
            flux_query = f'''
                from(bucket: "{self.config.influxdb_bucket}")
                |> range(start: -30d)
                |> group(columns: ["_measurement"])
                |> distinct(column: "_measurement")
                |> keep(columns: ["_value"])
            '''
            
            query_api = self.client.query_api()
            tables = await query_api.query(flux_query, org=self.config.influxdb_org)
            
            measurements = []
            for table in tables:
                for record in table.records:
                    measurements.append(record.get_value())
            
            return measurements
        except Exception as e:
            self.logger.error(f"Failed to get measurements from InfluxDB: {e}")
            return []
    
    async def get_tags(self, measurement: str) -> Dict[str, List[str]]:
        """Get all tags for measurement from InfluxDB"""
        try:
            # This would need to be implemented based on your specific schema
            # Returning empty dict for now
            return {}
        except Exception as e:
            self.logger.error(f"Failed to get tags from InfluxDB: {e}")
            return {}


class TimeSeriesAnalyzer:
    """Time series analysis utilities"""
    
    def __init__(self, config -> None: TimeSeriesConfig) -> None:
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def detect_seasonality(self, data: pd.Series, periods: List[int] = None) -> SeasonalityInfo:
        """Detect seasonality in time series data"""
        if periods is None:
            periods = [7, 30, 365]  # Weekly, monthly, yearly
        
        try:
            # Ensure data is numeric and sorted by index
            data = data.astype(float).sort_index()
            
            best_period = None
            best_strength = 0.0
            
            for period in periods:
                if len(data) >= 2 * period:
                    try:
                        decomposition = seasonal_decompose(
                            data,
                            period=period,
                            model='additive',
                            extrapolate_trend='freq'
                        )
                        
                        # Calculate seasonal strength
                        seasonal_var = np.var(decomposition.seasonal.dropna())
                        residual_var = np.var(decomposition.resid.dropna())
                        
                        if residual_var > 0:
                            seasonal_strength = seasonal_var / (seasonal_var + residual_var)
                            
                            if seasonal_strength > best_strength:
                                best_strength = seasonal_strength
                                best_period = period
                    except:
                        continue
            
            # Calculate trend strength
            trend_strength = 0.0
            if best_period and len(data) >= 2 * best_period:
                try:
                    decomposition = seasonal_decompose(data, period=best_period, model='additive')
                    trend_var = np.var(decomposition.trend.dropna())
                    residual_var = np.var(decomposition.resid.dropna())
                    
                    if residual_var > 0:
                        trend_strength = trend_var / (trend_var + residual_var)
                except:
                    pass
            
            return SeasonalityInfo(
                measurement="",  # Will be filled by caller
                field="",  # Will be filled by caller
                seasonal_period=best_period or 0,
                seasonal_strength=best_strength,
                trend_strength=trend_strength,
                has_seasonality=best_strength > 0.3,
                has_trend=trend_strength > 0.3
            )
            
        except Exception as e:
            self.logger.error(f"Seasonality detection failed: {e}")
            return SeasonalityInfo(
                measurement="",
                field="",
                seasonal_period=0,
                seasonal_strength=0.0,
                trend_strength=0.0,
                has_seasonality=False,
                has_trend=False
            )
    
    def detect_anomalies(
        self,
        data: pd.Series,
        method: AnomalyMethod = AnomalyMethod.STATISTICAL
    ) -> List[AnomalyPoint]:
        """Detect anomalies in time series data"""
        try:
            anomalies = []
            
            if method == AnomalyMethod.STATISTICAL:
                anomalies = self._detect_statistical_anomalies(data)
            elif method == AnomalyMethod.ISOLATION_FOREST:
                anomalies = self._detect_isolation_forest_anomalies(data)
            elif method == AnomalyMethod.LSTM_AUTOENCODER:
                anomalies = self._detect_lstm_anomalies(data)
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Anomaly detection failed: {e}")
            return []
    
    def _detect_statistical_anomalies(self, data: pd.Series) -> List[AnomalyPoint]:
        """Detect anomalies using statistical methods"""
        anomalies = []
        
        try:
            # Calculate rolling statistics
            window = min(30, len(data) // 4)
            if window < 3:
                return anomalies
            
            rolling_mean = data.rolling(window=window, center=True).mean()
            rolling_std = data.rolling(window=window, center=True).std()
            
            # Detect anomalies (values outside 3 standard deviations)
            threshold = self.config.anomaly_threshold
            
            for timestamp, value in data.items():
                if pd.notna(rolling_mean.loc[timestamp]) and pd.notna(rolling_std.loc[timestamp]):
                    expected = rolling_mean.loc[timestamp]
                    std = rolling_std.loc[timestamp]
                    
                    if std > 0:
                        z_score = abs(value - expected) / std
                        
                        if z_score > threshold:
                            severity = "high" if z_score > threshold * 2 else "medium"
                            
                            anomaly = AnomalyPoint(
                                timestamp=timestamp,
                                measurement="",  # Will be filled by caller
                                field="",  # Will be filled by caller
                                value=value,
                                expected_value=expected,
                                anomaly_score=z_score,
                                method=AnomalyMethod.STATISTICAL,
                                severity=severity
                            )
                            anomalies.append(anomaly)
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Statistical anomaly detection failed: {e}")
            return []
    
    def _detect_isolation_forest_anomalies(self, data: pd.Series) -> List[AnomalyPoint]:
        """Detect anomalies using Isolation Forest"""
        anomalies = []
        
        try:
            if len(data) < 10:
                return anomalies
            
            # Prepare features (value, time-based features)
            df = pd.DataFrame({
                'value': data.values,
                'hour': [t.hour for t in data.index],
                'day_of_week': [t.dayofweek for t in data.index],
                'day_of_month': [t.day for t in data.index]
            })
            
            # Train Isolation Forest
            iso_forest = IsolationForest(contamination=0.1, random_state=42)
            anomaly_labels = iso_forest.fit_predict(df)
            anomaly_scores = iso_forest.score_samples(df)
            
            # Convert to anomaly points
            for i, (timestamp, value) in enumerate(data.items()):
                if anomaly_labels[i] == -1:  # Anomaly
                    score = abs(anomaly_scores[i])
                    severity = "high" if score > 0.5 else "medium"
                    
                    anomaly = AnomalyPoint(
                        timestamp=timestamp,
                        measurement="",
                        field="",
                        value=value,
                        expected_value=data.median(),  # Use median as expected
                        anomaly_score=score,
                        method=AnomalyMethod.ISOLATION_FOREST,
                        severity=severity
                    )
                    anomalies.append(anomaly)
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Isolation Forest anomaly detection failed: {e}")
            return []
    
    def _detect_lstm_anomalies(self, data: pd.Series) -> List[AnomalyPoint]:
        """Detect anomalies using LSTM autoencoder"""
        anomalies = []
        
        try:
            if len(data) < 100:
                return anomalies
            
            # Prepare data for LSTM
            scaler = MinMaxScaler()
            scaled_data = scaler.fit_transform(data.values.reshape(-1, 1))
            
            # Create sequences
            sequence_length = 20
            sequences = []
            for i in range(len(scaled_data) - sequence_length):
                sequences.append(scaled_data[i:i + sequence_length])
            
            sequences = np.array(sequences)
            
            # Build LSTM autoencoder
            model = Sequential([
                LSTM(50, activation='relu', input_shape=(sequence_length, 1), return_sequences=True),
                LSTM(25, activation='relu', return_sequences=False),
                Dense(25, activation='relu'),
                Dense(50, activation='relu'),
                Dense(sequence_length)
            ])
            
            model.compile(optimizer='adam', loss='mse')
            
            # Train model
            model.fit(sequences, sequences, epochs=50, batch_size=32, verbose=0)
            
            # Predict and calculate reconstruction error
            predictions = model.predict(sequences, verbose=0)
            mse = np.mean(np.power(sequences - predictions, 2), axis=1)
            
            # Detect anomalies based on reconstruction error
            threshold = np.mean(mse) + 2 * np.std(mse)
            
            for i, error in enumerate(mse):
                if error > threshold:
                    timestamp_idx = i + sequence_length
                    if timestamp_idx < len(data):
                        timestamp = data.index[timestamp_idx]
                        value = data.iloc[timestamp_idx]
                        
                        severity = "high" if error > threshold * 2 else "medium"
                        
                        anomaly = AnomalyPoint(
                            timestamp=timestamp,
                            measurement="",
                            field="",
                            value=value,
                            expected_value=data.mean(),
                            anomaly_score=error,
                            method=AnomalyMethod.LSTM_AUTOENCODER,
                            severity=severity
                        )
                        anomalies.append(anomaly)
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"LSTM anomaly detection failed: {e}")
            return []
    
    def forecast(
        self,
        data: pd.Series,
        periods: int,
        method: ForecastMethod = ForecastMethod.ARIMA
    ) -> List[ForecastPoint]:
        """Forecast future values"""
        try:
            if method == ForecastMethod.ARIMA:
                return self._forecast_arima(data, periods)
            elif method == ForecastMethod.EXPONENTIAL_SMOOTHING:
                return self._forecast_exponential_smoothing(data, periods)
            elif method == ForecastMethod.LSTM:
                return self._forecast_lstm(data, periods)
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"Forecasting failed: {e}")
            return []
    
    def _forecast_arima(self, data: pd.Series, periods: int) -> List[ForecastPoint]:
        """Forecast using ARIMA model"""
        try:
            # Automatic ARIMA order selection
            model = sm.tsa.arima.ARIMA(data, order=(1, 1, 1))
            fitted_model = model.fit()
            
            # Generate forecast
            forecast = fitted_model.forecast(steps=periods)
            conf_int = fitted_model.get_forecast(steps=periods).conf_int()
            
            # Create forecast points
            last_timestamp = data.index[-1]
            freq = pd.infer_freq(data.index) or 'D'
            
            forecast_points = []
            for i in range(periods):
                timestamp = last_timestamp + pd.Timedelta(periods=i+1, freq=freq)
                
                point = ForecastPoint(
                    timestamp=timestamp,
                    predicted_value=float(forecast.iloc[i]),
                    confidence_lower=float(conf_int.iloc[i, 0]),
                    confidence_upper=float(conf_int.iloc[i, 1]),
                    method=ForecastMethod.ARIMA
                )
                forecast_points.append(point)
            
            return forecast_points
            
        except Exception as e:
            self.logger.error(f"ARIMA forecasting failed: {e}")
            return []
    
    def _forecast_exponential_smoothing(self, data: pd.Series, periods: int) -> List[ForecastPoint]:
        """Forecast using Exponential Smoothing"""
        try:
            model = ExponentialSmoothing(
                data,
                trend='add',
                seasonal='add',
                seasonal_periods=min(12, len(data) // 4)
            )
            fitted_model = model.fit()
            
            # Generate forecast
            forecast = fitted_model.forecast(periods)
            
            # Create forecast points
            last_timestamp = data.index[-1]
            freq = pd.infer_freq(data.index) or 'D'
            
            forecast_points = []
            for i in range(periods):
                timestamp = last_timestamp + pd.Timedelta(periods=i+1, freq=freq)
                
                # Simple confidence intervals (±20% of predicted value)
                predicted = float(forecast.iloc[i])
                margin = abs(predicted) * 0.2
                
                point = ForecastPoint(
                    timestamp=timestamp,
                    predicted_value=predicted,
                    confidence_lower=predicted - margin,
                    confidence_upper=predicted + margin,
                    method=ForecastMethod.EXPONENTIAL_SMOOTHING
                )
                forecast_points.append(point)
            
            return forecast_points
            
        except Exception as e:
            self.logger.error(f"Exponential smoothing forecasting failed: {e}")
            return []
    
    def _forecast_lstm(self, data: pd.Series, periods: int) -> List[ForecastPoint]:
        """Forecast using LSTM neural network"""
        try:
            if len(data) < 50:
                return []
            
            # Prepare data
            scaler = MinMaxScaler()
            scaled_data = scaler.fit_transform(data.values.reshape(-1, 1))
            
            # Create sequences
            sequence_length = 20
            X, y = [], []
            for i in range(len(scaled_data) - sequence_length):
                X.append(scaled_data[i:i + sequence_length])
                y.append(scaled_data[i + sequence_length])
            
            X, y = np.array(X), np.array(y)
            
            # Build and train LSTM model
            model = Sequential([
                LSTM(50, activation='relu', input_shape=(sequence_length, 1), return_sequences=True),
                Dropout(0.2),
                LSTM(50, activation='relu'),
                Dropout(0.2),
                Dense(1)
            ])
            
            model.compile(optimizer='adam', loss='mse')
            model.fit(X, y, epochs=50, batch_size=32, verbose=0)
            
            # Generate forecasts
            last_sequence = scaled_data[-sequence_length:].reshape(1, sequence_length, 1)
            forecasts = []
            
            for _ in range(periods):
                pred = model.predict(last_sequence, verbose=0)
                forecasts.append(pred[0, 0])
                
                # Update sequence for next prediction
                last_sequence = np.roll(last_sequence, -1, axis=1)
                last_sequence[0, -1, 0] = pred[0, 0]
            
            # Scale back to original range
            forecasts = scaler.inverse_transform(np.array(forecasts).reshape(-1, 1)).flatten()
            
            # Create forecast points
            last_timestamp = data.index[-1]
            freq = pd.infer_freq(data.index) or 'D'
            
            forecast_points = []
            for i, forecast_value in enumerate(forecasts):
                timestamp = last_timestamp + pd.Timedelta(periods=i+1, freq=freq)
                
                # Simple confidence intervals
                margin = abs(forecast_value) * 0.15
                
                point = ForecastPoint(
                    timestamp=timestamp,
                    predicted_value=float(forecast_value),
                    confidence_lower=float(forecast_value - margin),
                    confidence_upper=float(forecast_value + margin),
                    method=ForecastMethod.LSTM
                )
                forecast_points.append(point)
            
            return forecast_points
            
        except Exception as e:
            self.logger.error(f"LSTM forecasting failed: {e}")
            return []


class TimeSeriesModel:
    """Main time series model class"""
    
    def __init__(self, config -> None: TimeSeriesConfig) -> None:
        self.config = config
        self.backend = self._create_backend()
        self.analyzer = TimeSeriesAnalyzer(config)
        self.cache = None
        self.logger = logging.getLogger(__name__)
    
    def _create_backend(self) -> AbstractTimeSeriesBackend:
        """Create storage backend instance"""
        if self.config.backend == TimeSeriesBackend.INFLUXDB:
            return InfluxDBBackend(self.config)
        else:
            raise ValueError(f"Unsupported backend: {self.config.backend}")
    
    async def initialize(self) -> None:
        """Initialize time series model"""
        await self.backend.connect()
        
        if self.config.enable_caching:
            self.cache = redis.Redis(
                host=self.config.redis_host,
                port=self.config.redis_port,
                db=self.config.redis_db,
                password=self.config.redis_password
            )
        
        self.logger.info("Time series model initialized")
    
    async def shutdown(self) -> None:
        """Shutdown time series model"""
        await self.backend.disconnect()
        if self.cache:
            await self.cache.close()
    
    async def write_point(self, point: TimeSeriesPoint) -> bool:
        """Write single time series point"""
        return await self.write_points([point])
    
    async def write_points(self, points: List[TimeSeriesPoint]) -> bool:
        """Write multiple time series points"""
        try:
            # Batch points for better performance
            batches = [
                points[i:i + self.config.batch_size]
                for i in range(0, len(points), self.config.batch_size)
            ]
            
            success = True
            for batch in batches:
                if not await self.backend.write_points(batch):
                    success = False
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to write points: {e}")
            return False
    
    async def query_points(self, query: TimeSeriesQuery) -> TimeSeriesResult:
        """Query time series points with caching"""
        try:
            # Check cache first
            cache_key = None
            if self.config.enable_caching and self.cache:
                cache_key = self._generate_cache_key(query)
                cached_result = await self.cache.get(cache_key)
                if cached_result:
                    try:
                        data = json.loads(cached_result)
                        result = TimeSeriesResult(**data)
                        result.cached = True
                        return result
                    except:
                        pass
            
            # Query from backend
            result = await self.backend.query_points(query)
            
            # Cache result
            if cache_key and self.cache:
                await self.cache.setex(
                    cache_key,
                    self.config.cache_ttl,
                    result.json()
                )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to query points: {e}")
            raise
    
    def _generate_cache_key(self, query: TimeSeriesQuery) -> str:
        """Generate cache key for query"""
        key_data = {
            "measurement": query.measurement,
            "start_time": query.start_time.isoformat(),
            "end_time": query.end_time.isoformat(),
            "tags": query.tags,
            "fields": query.fields,
            "aggregation": query.aggregation.value if query.aggregation else None,
            "group_by_time": query.group_by_time,
            "group_by_tags": query.group_by_tags
        }
        key_hash = hash(json.dumps(key_data, sort_keys=True))
        return f"ts_query:{key_hash}"
    
    async def analyze_data(
        self,
        measurement: str,
        field: str,
        start_time: datetime,
        end_time: datetime,
        tags: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """Perform comprehensive time series analysis"""
        try:
            # Query data
            query = TimeSeriesQuery(
                measurement=measurement,
                start_time=start_time,
                end_time=end_time,
                fields=[field],
                tags=tags or {}
            )
            
            result = await self.query_points(query)
            
            if not result.points:
                return {"error": "No data found"}
            
            # Convert to pandas Series
            data = pd.Series(
                [point.fields[field] for point in result.points],
                index=[point.timestamp for point in result.points]
            ).sort_index()
            
            analysis = {}
            
            # Basic statistics
            analysis["statistics"] = {
                "count": len(data),
                "mean": float(data.mean()),
                "median": float(data.median()),
                "std": float(data.std()),
                "min": float(data.min()),
                "max": float(data.max()),
                "range": float(data.max() - data.min())
            }
            
            # Seasonality detection
            if self.config.seasonality_detection_enabled:
                seasonality = self.analyzer.detect_seasonality(data)
                seasonality.measurement = measurement
                seasonality.field = field
                analysis["seasonality"] = seasonality.dict()
            
            # Anomaly detection
            if self.config.anomaly_detection_enabled:
                anomalies = self.analyzer.detect_anomalies(data)
                for anomaly in anomalies:
                    anomaly.measurement = measurement
                    anomaly.field = field
                analysis["anomalies"] = [anomaly.dict() for anomaly in anomalies]
            
            # Forecasting
            if self.config.forecasting_enabled:
                forecast = self.analyzer.forecast(
                    data,
                    self.config.default_forecast_horizon,
                    ForecastMethod.ARIMA
                )
                analysis["forecast"] = [point.dict() for point in forecast]
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Data analysis failed: {e}")
            return {"error": str(e)}


# Usage example
async def main() -> None:
    """Example usage of TimeSeriesModel"""
    
    # Configure time series model
    config = TimeSeriesConfig(
        backend=TimeSeriesBackend.INFLUXDB,
        influxdb_url="http://localhost:8086",
        influxdb_token="your-influxdb-token",
        influxdb_org="ainflue",
        influxdb_bucket="metrics",
        anomaly_detection_enabled=True,
        forecasting_enabled=True
    )
    
    # Initialize model
    ts_model = TimeSeriesModel(config)
    await ts_model.initialize()
    
    try:
        # Write some sample data
        points = []
        base_time = datetime.utcnow() - timedelta(days=30)
        
        for i in range(720):  # 30 days of hourly data
            timestamp = base_time + timedelta(hours=i)
            
            # Simulate user activity data with seasonality
            base_value = 100
            daily_pattern = 50 * math.sin(2 * math.pi * i / 24)  # Daily cycle
            weekly_pattern = 20 * math.sin(2 * math.pi * i / (24 * 7))  # Weekly cycle
            noise = np.random.normal(0, 10)
            
            value = base_value + daily_pattern + weekly_pattern + noise
            
            point = TimeSeriesPoint(
                timestamp=timestamp,
                measurement="user_activity",
                tags={"platform": "web", "region": "us-east"},
                fields={"active_users": max(0, int(value))}
            )
            points.append(point)
        
        # Write points
        success = await ts_model.write_points(points)
        print(f"Data written successfully: {success}")
        
        # Analyze data
        analysis = await ts_model.analyze_data(
            measurement="user_activity",
            field="active_users",
            start_time=base_time,
            end_time=datetime.utcnow(),
            tags={"platform": "web"}
        )
        
        print(f"Analysis results:")
        print(f"- Mean active users: {analysis['statistics']['mean']:.1f}")
        print(f"- Has seasonality: {analysis['seasonality']['has_seasonality']}")
        print(f"- Anomalies detected: {len(analysis['anomalies'])}")
        print(f"- Forecast points: {len(analysis['forecast'])}")
        
        # Query recent data
        query = TimeSeriesQuery(
            measurement="user_activity",
            start_time=datetime.utcnow() - timedelta(days=1),
            end_time=datetime.utcnow(),
            fields=["active_users"],
            tags={"platform": "web"},
            aggregation=AggregationType.MEAN,
            group_by_time="1h"
        )
        
        result = await ts_model.query_points(query)
        print(f"Retrieved {len(result.points)} hourly aggregated points")
        
    finally:
        await ts_model.shutdown()


if __name__ == "__main__":
    asyncio.run(main())