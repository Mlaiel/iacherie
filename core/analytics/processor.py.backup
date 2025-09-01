"""Analytics Processor - Advanced Analytics Processing Engine

High-performance analytics processing system with real-time data processing,
advanced algorithms, and comprehensive data transformation capabilities.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de).
ANY unauthorized use, reproduction, or distribution is STRICTLY PROHIBITED.
Legal action will be taken against violators under German and international law.
Contact mlaiel@live.de for licensing inquiries.

Team Specialists:
- Lead IA Developer: Fahed Mlaiel (mlaiel@live.de)
- Backend Senior Engineer: Advanced microservices architecture
- ML Engineer: Deep learning & analytics algorithms
- Database Administrator: High-performance data optimization
- Security Expert: Enterprise-grade protection systems
- Microservices Architect: Scalable distributed systems
- Audio Processing Specialist: Advanced audio AI algorithms
- DevOps Engineer: Production-ready infrastructure
- IA Prompt Engineer: Optimized AI model interactions
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional, Union, Callable, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import json
import math
import statistics
import numpy as np
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import threading
import queue

from .exceptions import ProcessingError, DataValidationError, ConfigurationError
from .collector import MetricPoint, MetricType, MetricScope

logger = logging.getLogger(__name__)


class ProcessingMode(Enum):
    """Processing modes for analytics data"""
    REALTIME = "realtime"
    BATCH = "batch"
    STREAM = "stream"
    HYBRID = "hybrid"


class ProcessingPriority(Enum):
    """Processing priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class DataQuality(Enum):
    """Data quality levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    INVALID = "invalid"


@dataclass
class ProcessingTask:
    """Processing task data structure"""
    task_id: str
    task_type: str
    data: Any
    priority: ProcessingPriority
    mode: ProcessingMode
    created_at: datetime
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary"""
        return {
            'task_id': self.task_id,
            'task_type': self.task_type,
            'priority': self.priority.value,
            'mode': self.mode.value,
            'created_at': self.created_at.isoformat(),
            'parameters': self.parameters,
            'metadata': self.metadata
        }


@dataclass
class ProcessingResult:
    """Processing result data structure"""
    task_id: str
    result_type: str
    data: Any
    processing_time: float
    quality_score: float
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            'task_id': self.task_id,
            'result_type': self.result_type,
            'processing_time': self.processing_time,
            'quality_score': self.quality_score,
            'confidence': self.confidence,
            'metadata': self.metadata
        }


class AnalyticsProcessor:
    """
    Advanced analytics processing engine.
    
    Provides high-performance data processing with real-time and batch capabilities,
    advanced algorithms, and comprehensive data transformation.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Processing infrastructure
        self.processing_queue = queue.PriorityQueue()
        self.completed_tasks = {}
        self.active_processors = {}
        
        # Thread pools
        self.thread_pool = ThreadPoolExecutor(
            max_workers=self.config.get('max_threads', 4)
        )
        self.process_pool = ProcessPoolExecutor(
            max_workers=self.config.get('max_processes', 2)
        )
        
        # Configuration
        self.enable_realtime = self.config.get('enable_realtime', True)
        self.batch_size = self.config.get('batch_size', 1000)
        self.processing_timeout = self.config.get('processing_timeout', 300)
        self.quality_threshold = self.config.get('quality_threshold', 0.8)
        
        # Performance tracking
        self.processing_stats = {
            'total_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0,
            'average_processing_time': 0.0,
            'queue_size': 0,
            'last_processed': None
        }
        
        # Registered processors
        self.processors = {}
        self._register_default_processors()
    
    async def initialize(self) -> None:
        """Initialize analytics processor"""
        try:
            self.logger.info("Initializing AnalyticsProcessor...")
            
            # Start processing workers
            if self.enable_realtime:
                asyncio.create_task(self._realtime_processing_worker())
                asyncio.create_task(self._batch_processing_worker())
                asyncio.create_task(self._monitoring_worker())
            
            self.logger.info("AnalyticsProcessor initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize AnalyticsProcessor: {str(e)}")
            raise ProcessingError(f"Initialization failed: {str(e)}")
    
    async def shutdown(self) -> None:
        """Shutdown analytics processor"""
        try:
            self.logger.info("Shutting down AnalyticsProcessor...")
            
            # Complete pending tasks
            await self._complete_pending_tasks()
            
            # Shutdown thread pools
            self.thread_pool.shutdown(wait=True)
            self.process_pool.shutdown(wait=True)
            
            self.logger.info("AnalyticsProcessor shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error shutting down AnalyticsProcessor: {str(e)}")
            raise ProcessingError(f"Shutdown failed: {str(e)}")
    
    async def submit_task(
        self,
        task_type: str,
        data: Any,
        priority: ProcessingPriority = ProcessingPriority.MEDIUM,
        mode: ProcessingMode = ProcessingMode.REALTIME,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """Submit processing task"""
        try:
            # Generate task ID
            task_id = f"task_{datetime.now().timestamp()}_{hash(str(data)) % 10000:04d}"
            
            # Create processing task
            task = ProcessingTask(
                task_id=task_id,
                task_type=task_type,
                data=data,
                priority=priority,
                mode=mode,
                created_at=datetime.now(),
                parameters=parameters or {},
                metadata={
                    'submitted_by': 'analytics_processor',
                    'submission_time': datetime.now().isoformat()
                }
            )
            
            # Add to queue with priority
            priority_value = (4 - priority.value, datetime.now().timestamp())
            self.processing_queue.put((priority_value, task))
            
            # Update statistics
            self.processing_stats['total_tasks'] += 1
            self.processing_stats['queue_size'] = self.processing_queue.qsize()
            
            self.logger.debug(f"Submitted task {task_id}: {task_type}")
            return task_id
            
        except Exception as e:
            self.logger.error(f"Error submitting task: {str(e)}")
            raise ProcessingError(f"Task submission failed: {str(e)}")
    
    async def get_result(
        self,
        task_id: str,
        timeout: Optional[float] = None
    ) -> Optional[ProcessingResult]:
        """Get processing result"""
        try:
            timeout = timeout or self.processing_timeout
            start_time = datetime.now()
            
            while (datetime.now() - start_time).total_seconds() < timeout:
                if task_id in self.completed_tasks:
                    return self.completed_tasks[task_id]
                
                await asyncio.sleep(0.1)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting result: {str(e)}")
            raise ProcessingError(f"Result retrieval failed: {str(e)}")
    
    async def process_realtime(
        self,
        processor_type: str,
        data: Any,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ProcessingResult:
        """Process data in real-time"""
        try:
            if processor_type not in self.processors:
                raise ValueError(f"Unknown processor type: {processor_type}")
            
            processor = self.processors[processor_type]
            start_time = datetime.now()
            
            # Process data
            result_data = await processor(data, parameters or {})
            
            # Calculate processing metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            quality_score = await self._calculate_quality_score(result_data)
            confidence = await self._calculate_confidence_score(result_data, quality_score)
            
            # Create result
            result = ProcessingResult(
                task_id=f"realtime_{datetime.now().timestamp()}",
                result_type=processor_type,
                data=result_data,
                processing_time=processing_time,
                quality_score=quality_score,
                confidence=confidence,
                metadata={
                    'processing_mode': 'realtime',
                    'processor_type': processor_type,
                    'processed_at': datetime.now().isoformat()
                }
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in realtime processing: {str(e)}")
            raise ProcessingError(f"Realtime processing failed: {str(e)}")
    
    async def process_batch(
        self,
        processor_type: str,
        data_batch: List[Any],
        parameters: Optional[Dict[str, Any]] = None
    ) -> List[ProcessingResult]:
        """Process batch of data"""
        try:
            if processor_type not in self.processors:
                raise ValueError(f"Unknown processor type: {processor_type}")
            
            processor = self.processors[processor_type]
            results = []
            
            # Process batch in chunks
            chunk_size = self.batch_size
            for i in range(0, len(data_batch), chunk_size):
                chunk = data_batch[i:i + chunk_size]
                
                # Process chunk
                chunk_results = await self._process_chunk(
                    processor, chunk, processor_type, parameters or {}
                )
                results.extend(chunk_results)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in batch processing: {str(e)}")
            raise ProcessingError(f"Batch processing failed: {str(e)}")
    
    def register_processor(
        self,
        processor_type: str,
        processor_func: Callable
    ) -> None:
        """Register custom processor"""
        try:
            self.processors[processor_type] = processor_func
            self.logger.info(f"Registered processor: {processor_type}")
            
        except Exception as e:
            self.logger.error(f"Error registering processor: {str(e)}")
            raise ProcessingError(f"Processor registration failed: {str(e)}")
    
    async def get_processing_metrics(self) -> Dict[str, Any]:
        """Get processing performance metrics"""
        try:
            return {
                'timestamp': datetime.now().isoformat(),
                'queue_size': self.processing_queue.qsize(),
                'active_processors': len(self.active_processors),
                'total_tasks': self.processing_stats['total_tasks'],
                'completed_tasks': self.processing_stats['completed_tasks'],
                'failed_tasks': self.processing_stats['failed_tasks'],
                'success_rate': (
                    self.processing_stats['completed_tasks'] / 
                    max(1, self.processing_stats['total_tasks'])
                ),
                'average_processing_time': self.processing_stats['average_processing_time'],
                'throughput_per_minute': await self._calculate_throughput(),
                'registered_processors': list(self.processors.keys())
            }
            
        except Exception as e:
            self.logger.error(f"Error getting processing metrics: {str(e)}")
            raise ProcessingError(f"Metrics retrieval failed: {str(e)}")
    
    # Private Methods
    
    def _register_default_processors(self) -> None:
        """Register default data processors"""
        self.processors.update({
            'statistical_analysis': self._statistical_processor,
            'trend_analysis': self._trend_processor,
            'anomaly_detection': self._anomaly_processor,
            'correlation_analysis': self._correlation_processor,
            'clustering': self._clustering_processor,
            'forecasting': self._forecasting_processor,
            'classification': self._classification_processor,
            'feature_extraction': self._feature_extraction_processor,
            'data_quality': self._data_quality_processor,
            'aggregation': self._aggregation_processor
        })
    
    async def _statistical_processor(
        self,
        data: List[float],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Statistical analysis processor"""
        try:
            if not data:
                return {'error': 'No data provided'}
            
            # Basic statistics
            stats = {
                'count': len(data),
                'mean': statistics.mean(data),
                'median': statistics.median(data),
                'std_dev': statistics.stdev(data) if len(data) > 1 else 0,
                'min': min(data),
                'max': max(data),
                'sum': sum(data)
            }
            
            # Percentiles
            if len(data) >= 4:
                stats.update({
                    'q1': np.percentile(data, 25),
                    'q3': np.percentile(data, 75),
                    'iqr': np.percentile(data, 75) - np.percentile(data, 25)
                })
            
            # Advanced statistics
            if parameters.get('advanced', False) and len(data) > 2:
                stats.update({
                    'skewness': self._calculate_skewness(data),
                    'kurtosis': self._calculate_kurtosis(data),
                    'variance': statistics.variance(data)
                })
            
            return stats
            
        except Exception as e:
            return {'error': f'Statistical processing failed: {str(e)}'}
    
    async def _trend_processor(
        self,
        data: List[Dict[str, Any]],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Trend analysis processor"""
        try:
            if not data:
                return {'error': 'No data provided'}
            
            # Extract time series data
            time_field = parameters.get('time_field', 'timestamp')
            value_field = parameters.get('value_field', 'value')
            
            time_series = []
            for item in data:
                if time_field in item and value_field in item:
                    time_series.append((item[time_field], item[value_field]))
            
            if not time_series:
                return {'error': 'No valid time series data'}
            
            # Sort by time
            time_series.sort(key=lambda x: x[0])
            values = [x[1] for x in time_series]
            
            # Calculate trend
            trend_direction = self._calculate_trend_direction(values)
            trend_strength = self._calculate_trend_strength(values)
            
            # Detect seasonality
            seasonality = self._detect_seasonality(values) if len(values) >= 12 else None
            
            return {
                'trend_direction': trend_direction,
                'trend_strength': trend_strength,
                'seasonality': seasonality,
                'data_points': len(values),
                'trend_analysis': {
                    'linear_regression': self._linear_regression(values),
                    'moving_average': self._moving_average(values, window=5),
                    'growth_rate': self._calculate_growth_rate(values)
                }
            }
            
        except Exception as e:
            return {'error': f'Trend processing failed: {str(e)}'}
    
    async def _anomaly_processor(
        self,
        data: List[float],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Anomaly detection processor"""
        try:
            if not data or len(data) < 3:
                return {'error': 'Insufficient data for anomaly detection'}
            
            # Calculate statistics
            mean = statistics.mean(data)
            std_dev = statistics.stdev(data)
            
            # Z-score method
            threshold = parameters.get('threshold', 2.0)
            anomalies_zscore = []
            
            for i, value in enumerate(data):
                z_score = abs(value - mean) / std_dev if std_dev > 0 else 0
                if z_score > threshold:
                    anomalies_zscore.append({
                        'index': i,
                        'value': value,
                        'z_score': z_score,
                        'type': 'statistical'
                    })
            
            # IQR method
            if len(data) >= 4:
                q1 = np.percentile(data, 25)
                q3 = np.percentile(data, 75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                
                anomalies_iqr = []
                for i, value in enumerate(data):
                    if value < lower_bound or value > upper_bound:
                        anomalies_iqr.append({
                            'index': i,
                            'value': value,
                            'bounds': [lower_bound, upper_bound],
                            'type': 'iqr'
                        })
            else:
                anomalies_iqr = []
            
            return {
                'total_points': len(data),
                'anomalies_zscore': anomalies_zscore,
                'anomalies_iqr': anomalies_iqr,
                'anomaly_rate': (len(anomalies_zscore) + len(anomalies_iqr)) / (2 * len(data)),
                'statistics': {
                    'mean': mean,
                    'std_dev': std_dev,
                    'threshold': threshold
                }
            }
            
        except Exception as e:
            return {'error': f'Anomaly detection failed: {str(e)}'}
    
    async def _correlation_processor(
        self,
        data: Dict[str, List[float]],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Correlation analysis processor"""
        try:
            if not data or len(data) < 2:
                return {'error': 'Need at least 2 variables for correlation'}
            
            # Validate data lengths
            lengths = [len(values) for values in data.values()]
            if len(set(lengths)) > 1:
                return {'error': 'All variables must have same length'}
            
            variables = list(data.keys())
            correlations = {}
            
            # Calculate pairwise correlations
            for i, var1 in enumerate(variables):
                for j, var2 in enumerate(variables[i+1:], i+1):
                    correlation = np.corrcoef(data[var1], data[var2])[0, 1]
                    correlations[f"{var1}_vs_{var2}"] = {
                        'correlation': correlation,
                        'strength': self._classify_correlation_strength(abs(correlation)),
                        'direction': 'positive' if correlation > 0 else 'negative'
                    }
            
            # Find strongest correlations
            strongest = max(correlations.items(), key=lambda x: abs(x[1]['correlation']))
            
            return {
                'correlations': correlations,
                'strongest_correlation': {
                    'variables': strongest[0],
                    'value': strongest[1]['correlation'],
                    'strength': strongest[1]['strength']
                },
                'variables_analyzed': variables,
                'data_points': lengths[0]
            }
            
        except Exception as e:
            return {'error': f'Correlation analysis failed: {str(e)}'}
    
    async def _clustering_processor(
        self,
        data: List[List[float]],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Clustering analysis processor"""
        try:
            if not data or len(data) < 2:
                return {'error': 'Insufficient data for clustering'}
            
            # Simple K-means clustering implementation
            k = parameters.get('k', 3)
            max_iterations = parameters.get('max_iterations', 100)
            
            # Initialize centroids randomly
            data_array = np.array(data)
            centroids = data_array[np.random.choice(len(data), k, replace=False)]
            
            for iteration in range(max_iterations):
                # Assign points to clusters
                distances = np.sqrt(((data_array - centroids[:, np.newaxis])**2).sum(axis=2))
                labels = np.argmin(distances, axis=0)
                
                # Update centroids
                new_centroids = np.array([data_array[labels == i].mean(axis=0) for i in range(k)])
                
                # Check convergence
                if np.allclose(centroids, new_centroids):
                    break
                
                centroids = new_centroids
            
            # Calculate cluster quality
            inertia = sum(
                np.sum((data_array[labels == i] - centroids[i])**2) 
                for i in range(k)
            )
            
            # Create cluster assignments
            clusters = {}
            for i in range(k):
                cluster_points = data_array[labels == i].tolist()
                clusters[f"cluster_{i}"] = {
                    'points': cluster_points,
                    'centroid': centroids[i].tolist(),
                    'size': len(cluster_points)
                }
            
            return {
                'clusters': clusters,
                'k': k,
                'iterations': iteration + 1,
                'inertia': inertia,
                'cluster_sizes': [len(data_array[labels == i]) for i in range(k)]
            }
            
        except Exception as e:
            return {'error': f'Clustering failed: {str(e)}'}
    
    async def _forecasting_processor(
        self,
        data: List[float],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Time series forecasting processor"""
        try:
            if not data or len(data) < 3:
                return {'error': 'Insufficient data for forecasting'}
            
            forecast_periods = parameters.get('periods', 5)
            method = parameters.get('method', 'simple')
            
            if method == 'simple':
                # Simple moving average forecast
                window = min(len(data), parameters.get('window', 3))
                recent_avg = sum(data[-window:]) / window
                forecast = [recent_avg] * forecast_periods
                
            elif method == 'linear':
                # Linear trend forecast
                x = list(range(len(data)))
                slope, intercept = self._linear_regression_params(x, data)
                forecast = [
                    slope * (len(data) + i) + intercept 
                    for i in range(1, forecast_periods + 1)
                ]
                
            elif method == 'exponential':
                # Exponential smoothing
                alpha = parameters.get('alpha', 0.3)
                smoothed = [data[0]]
                
                for value in data[1:]:
                    smoothed.append(alpha * value + (1 - alpha) * smoothed[-1])
                
                forecast = [smoothed[-1]] * forecast_periods
                
            else:
                return {'error': f'Unknown forecasting method: {method}'}
            
            # Calculate confidence intervals (simplified)
            recent_errors = [abs(data[i] - data[i-1]) for i in range(1, len(data))]
            avg_error = sum(recent_errors) / len(recent_errors) if recent_errors else 0
            
            confidence_intervals = [
                {
                    'forecast': f,
                    'lower_bound': f - 1.96 * avg_error,
                    'upper_bound': f + 1.96 * avg_error
                }
                for f in forecast
            ]
            
            return {
                'forecast': forecast,
                'confidence_intervals': confidence_intervals,
                'method': method,
                'periods': forecast_periods,
                'historical_data_points': len(data),
                'forecast_accuracy_estimate': 1.0 - (avg_error / max(data)) if max(data) > 0 else 0
            }
            
        except Exception as e:
            return {'error': f'Forecasting failed: {str(e)}'}
    
    async def _classification_processor(
        self,
        data: Dict[str, Any],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Data classification processor"""
        try:
            classification_type = parameters.get('type', 'value_based')
            
            if classification_type == 'value_based':
                values = data.get('values', [])
                if not values:
                    return {'error': 'No values to classify'}
                
                # Classify based on value ranges
                thresholds = parameters.get('thresholds', [33, 66])
                labels = parameters.get('labels', ['low', 'medium', 'high'])
                
                classifications = []
                for value in values:
                    if value <= thresholds[0]:
                        category = labels[0]
                    elif value <= thresholds[1]:
                        category = labels[1]
                    else:
                        category = labels[2]
                    
                    classifications.append({
                        'value': value,
                        'category': category
                    })
                
                # Summary statistics
                category_counts = {}
                for label in labels:
                    category_counts[label] = sum(1 for c in classifications if c['category'] == label)
                
                return {
                    'classifications': classifications,
                    'category_counts': category_counts,
                    'total_items': len(values),
                    'thresholds': thresholds,
                    'labels': labels
                }
            
            else:
                return {'error': f'Unknown classification type: {classification_type}'}
                
        except Exception as e:
            return {'error': f'Classification failed: {str(e)}'}
    
    async def _feature_extraction_processor(
        self,
        data: Dict[str, Any],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Feature extraction processor"""
        try:
            extraction_type = parameters.get('type', 'statistical')
            
            if extraction_type == 'statistical':
                values = data.get('values', [])
                if not values:
                    return {'error': 'No values for feature extraction'}
                
                features = {
                    'basic_stats': await self._statistical_processor(values, {}),
                    'distribution_features': {
                        'range': max(values) - min(values),
                        'coefficient_of_variation': statistics.stdev(values) / statistics.mean(values) if statistics.mean(values) != 0 else 0,
                        'outlier_count': len([v for v in values if abs(v - statistics.mean(values)) > 2 * statistics.stdev(values)])
                    }
                }
                
                if len(values) > 5:
                    features['pattern_features'] = {
                        'trend_direction': self._calculate_trend_direction(values),
                        'volatility': statistics.stdev(values),
                        'stability_score': 1.0 - (statistics.stdev(values) / max(values)) if max(values) > 0 else 0
                    }
                
                return features
            
            else:
                return {'error': f'Unknown extraction type: {extraction_type}'}
                
        except Exception as e:
            return {'error': f'Feature extraction failed: {str(e)}'}
    
    async def _data_quality_processor(
        self,
        data: Any,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Data quality assessment processor"""
        try:
            quality_metrics = {
                'completeness': 0.0,
                'accuracy': 0.0,
                'consistency': 0.0,
                'validity': 0.0,
                'overall_quality': DataQuality.POOR
            }
            
            if isinstance(data, list):
                # Completeness: ratio of non-null values
                non_null_count = sum(1 for item in data if item is not None)
                quality_metrics['completeness'] = non_null_count / len(data) if data else 0
                
                # Validity: ratio of values within expected ranges
                if all(isinstance(item, (int, float)) for item in data if item is not None):
                    min_expected = parameters.get('min_value', float('-inf'))
                    max_expected = parameters.get('max_value', float('inf'))
                    
                    valid_count = sum(
                        1 for item in data 
                        if item is not None and min_expected <= item <= max_expected
                    )
                    quality_metrics['validity'] = valid_count / non_null_count if non_null_count > 0 else 0
                else:
                    quality_metrics['validity'] = 1.0  # Assume valid for non-numeric data
                
                # Consistency: coefficient of variation for numeric data
                if all(isinstance(item, (int, float)) for item in data if item is not None):
                    numeric_data = [item for item in data if item is not None]
                    if numeric_data and len(numeric_data) > 1:
                        cv = statistics.stdev(numeric_data) / abs(statistics.mean(numeric_data)) if statistics.mean(numeric_data) != 0 else 0
                        quality_metrics['consistency'] = max(0, 1.0 - cv)
                    else:
                        quality_metrics['consistency'] = 1.0
                else:
                    quality_metrics['consistency'] = 1.0
            
            elif isinstance(data, dict):
                # For dictionary data, assess based on key-value completeness
                total_keys = len(data)
                non_null_values = sum(1 for value in data.values() if value is not None)
                quality_metrics['completeness'] = non_null_values / total_keys if total_keys > 0 else 0
                quality_metrics['validity'] = 1.0  # Assume valid structure
                quality_metrics['consistency'] = 1.0  # Assume consistent
            
            # Accuracy (simplified - based on other metrics)
            quality_metrics['accuracy'] = (
                quality_metrics['completeness'] * 0.4 +
                quality_metrics['validity'] * 0.4 +
                quality_metrics['consistency'] * 0.2
            )
            
            # Overall quality assessment
            avg_quality = (
                quality_metrics['completeness'] +
                quality_metrics['accuracy'] +
                quality_metrics['consistency'] +
                quality_metrics['validity']
            ) / 4
            
            if avg_quality >= 0.9:
                quality_metrics['overall_quality'] = DataQuality.EXCELLENT
            elif avg_quality >= 0.7:
                quality_metrics['overall_quality'] = DataQuality.GOOD
            elif avg_quality >= 0.5:
                quality_metrics['overall_quality'] = DataQuality.FAIR
            elif avg_quality >= 0.3:
                quality_metrics['overall_quality'] = DataQuality.POOR
            else:
                quality_metrics['overall_quality'] = DataQuality.INVALID
            
            return {
                'quality_metrics': quality_metrics,
                'quality_score': avg_quality,
                'recommendations': self._generate_quality_recommendations(quality_metrics)
            }
            
        except Exception as e:
            return {'error': f'Data quality assessment failed: {str(e)}'}
    
    async def _aggregation_processor(
        self,
        data: List[Dict[str, Any]],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Data aggregation processor"""
        try:
            if not data:
                return {'error': 'No data to aggregate'}
            
            group_by = parameters.get('group_by')
            aggregation_functions = parameters.get('functions', ['count', 'sum', 'avg'])
            value_field = parameters.get('value_field', 'value')
            
            if group_by:
                # Group aggregation
                groups = defaultdict(list)
                for item in data:
                    if group_by in item:
                        groups[item[group_by]].append(item)
                
                aggregated = {}
                for group_key, group_data in groups.items():
                    group_values = [item.get(value_field, 0) for item in group_data if value_field in item]
                    
                    group_agg = {}
                    if 'count' in aggregation_functions:
                        group_agg['count'] = len(group_data)
                    if 'sum' in aggregation_functions and group_values:
                        group_agg['sum'] = sum(group_values)
                    if 'avg' in aggregation_functions and group_values:
                        group_agg['avg'] = sum(group_values) / len(group_values)
                    if 'min' in aggregation_functions and group_values:
                        group_agg['min'] = min(group_values)
                    if 'max' in aggregation_functions and group_values:
                        group_agg['max'] = max(group_values)
                    
                    aggregated[str(group_key)] = group_agg
                
                return {
                    'aggregated_data': aggregated,
                    'group_by': group_by,
                    'total_groups': len(groups),
                    'total_records': len(data)
                }
            
            else:
                # Overall aggregation
                values = [item.get(value_field, 0) for item in data if value_field in item]
                
                aggregated = {}
                if 'count' in aggregation_functions:
                    aggregated['count'] = len(data)
                if 'sum' in aggregation_functions and values:
                    aggregated['sum'] = sum(values)
                if 'avg' in aggregation_functions and values:
                    aggregated['avg'] = sum(values) / len(values)
                if 'min' in aggregation_functions and values:
                    aggregated['min'] = min(values)
                if 'max' in aggregation_functions and values:
                    aggregated['max'] = max(values)
                
                return {
                    'aggregated_data': aggregated,
                    'total_records': len(data),
                    'value_field': value_field
                }
                
        except Exception as e:
            return {'error': f'Aggregation failed: {str(e)}'}
    
    # Utility Methods
    
    def _calculate_skewness(self, data: List[float]) -> float:
        """Calculate skewness of data"""
        if len(data) < 3:
            return 0.0
        
        mean = statistics.mean(data)
        std_dev = statistics.stdev(data)
        
        if std_dev == 0:
            return 0.0
        
        skewness = sum((x - mean) ** 3 for x in data) / (len(data) * std_dev ** 3)
        return skewness
    
    def _calculate_kurtosis(self, data: List[float]) -> float:
        """Calculate kurtosis of data"""
        if len(data) < 4:
            return 0.0
        
        mean = statistics.mean(data)
        std_dev = statistics.stdev(data)
        
        if std_dev == 0:
            return 0.0
        
        kurtosis = sum((x - mean) ** 4 for x in data) / (len(data) * std_dev ** 4) - 3
        return kurtosis
    
    def _calculate_trend_direction(self, values: List[float]) -> str:
        """Calculate trend direction"""
        if len(values) < 2:
            return 'unknown'
        
        # Simple linear regression slope
        x = list(range(len(values)))
        slope, _ = self._linear_regression_params(x, values)
        
        if slope > 0.01:
            return 'increasing'
        elif slope < -0.01:
            return 'decreasing'
        else:
            return 'stable'
    
    def _calculate_trend_strength(self, values: List[float]) -> float:
        """Calculate trend strength (0-1)"""
        if len(values) < 3:
            return 0.0
        
        # Calculate R-squared for linear trend
        x = list(range(len(values)))
        slope, intercept = self._linear_regression_params(x, values)
        
        predicted = [slope * i + intercept for i in x]
        
        ss_res = sum((values[i] - predicted[i]) ** 2 for i in range(len(values)))
        ss_tot = sum((values[i] - statistics.mean(values)) ** 2 for i in range(len(values)))
        
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        return max(0, min(1, r_squared))
    
    def _detect_seasonality(self, values: List[float]) -> Optional[Dict[str, Any]]:
        """Simple seasonality detection"""
        if len(values) < 12:
            return None
        
        # Check for monthly seasonality (12-period cycle)
        seasonal_strength = 0.0
        
        # Calculate autocorrelation at lag 12
        if len(values) >= 24:
            lag_12_corr = self._autocorrelation(values, 12)
            if abs(lag_12_corr) > 0.3:
                seasonal_strength = abs(lag_12_corr)
        
        return {
            'detected': seasonal_strength > 0.3,
            'strength': seasonal_strength,
            'period': 12
        }
    
    def _linear_regression_params(
        self,
        x: List[float],
        y: List[float]
    ) -> Tuple[float, float]:
        """Calculate linear regression parameters"""
        n = len(x)
        if n == 0:
            return 0.0, 0.0
        
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(xi ** 2 for xi in x)
        
        denominator = n * sum_x2 - sum_x ** 2
        if denominator == 0:
            return 0.0, statistics.mean(y) if y else 0.0
        
        slope = (n * sum_xy - sum_x * sum_y) / denominator
        intercept = (sum_y - slope * sum_x) / n
        
        return slope, intercept
    
    def _linear_regression(self, values: List[float]) -> Dict[str, float]:
        """Perform linear regression on values"""
        x = list(range(len(values)))
        slope, intercept = self._linear_regression_params(x, values)
        
        return {
            'slope': slope,
            'intercept': intercept,
            'trend_strength': self._calculate_trend_strength(values)
        }
    
    def _moving_average(self, values: List[float], window: int) -> List[float]:
        """Calculate moving average"""
        if len(values) < window:
            return values[:]
        
        ma = []
        for i in range(len(values) - window + 1):
            avg = sum(values[i:i + window]) / window
            ma.append(avg)
        
        return ma
    
    def _calculate_growth_rate(self, values: List[float]) -> float:
        """Calculate overall growth rate"""
        if len(values) < 2 or values[0] == 0:
            return 0.0
        
        return (values[-1] - values[0]) / values[0]
    
    def _classify_correlation_strength(self, correlation: float) -> str:
        """Classify correlation strength"""
        abs_corr = abs(correlation)
        
        if abs_corr >= 0.8:
            return 'very_strong'
        elif abs_corr >= 0.6:
            return 'strong'
        elif abs_corr >= 0.4:
            return 'moderate'
        elif abs_corr >= 0.2:
            return 'weak'
        else:
            return 'very_weak'
    
    def _autocorrelation(self, values: List[float], lag: int) -> float:
        """Calculate autocorrelation at given lag"""
        if len(values) <= lag:
            return 0.0
        
        n = len(values) - lag
        mean_val = statistics.mean(values)
        
        numerator = sum(
            (values[i] - mean_val) * (values[i + lag] - mean_val)
            for i in range(n)
        )
        
        denominator = sum((values[i] - mean_val) ** 2 for i in range(len(values)))
        
        return numerator / denominator if denominator > 0 else 0.0
    
    def _generate_quality_recommendations(
        self,
        quality_metrics: Dict[str, Any]
    ) -> List[str]:
        """Generate data quality improvement recommendations"""
        recommendations = []
        
        if quality_metrics['completeness'] < 0.8:
            recommendations.append("Improve data completeness by reducing missing values")
        
        if quality_metrics['validity'] < 0.8:
            recommendations.append("Validate data values against expected ranges")
        
        if quality_metrics['consistency'] < 0.8:
            recommendations.append("Improve data consistency by standardizing formats")
        
        if quality_metrics['accuracy'] < 0.8:
            recommendations.append("Implement data validation and cleansing processes")
        
        if not recommendations:
            recommendations.append("Data quality is good - maintain current standards")
        
        return recommendations
    
    async def _process_chunk(
        self,
        processor: Callable,
        chunk: List[Any],
        processor_type: str,
        parameters: Dict[str, Any]
    ) -> List[ProcessingResult]:
        """Process data chunk"""
        results = []
        
        for i, item in enumerate(chunk):
            try:
                start_time = datetime.now()
                
                result_data = await processor(item, parameters)
                
                processing_time = (datetime.now() - start_time).total_seconds()
                quality_score = await self._calculate_quality_score(result_data)
                confidence = await self._calculate_confidence_score(result_data, quality_score)
                
                result = ProcessingResult(
                    task_id=f"batch_{processor_type}_{i}",
                    result_type=processor_type,
                    data=result_data,
                    processing_time=processing_time,
                    quality_score=quality_score,
                    confidence=confidence,
                    metadata={
                        'processing_mode': 'batch',
                        'chunk_index': i,
                        'processor_type': processor_type
                    }
                )
                
                results.append(result)
                
            except Exception as e:
                self.logger.error(f"Error processing chunk item {i}: {str(e)}")
                # Continue processing other items
        
        return results
    
    async def _calculate_quality_score(self, result_data: Any) -> float:
        """Calculate quality score for result data"""
        try:
            if isinstance(result_data, dict):
                if 'error' in result_data:
                    return 0.0
                
                # Score based on data completeness and structure
                score = 0.0
                
                # Basic structure score
                if result_data:
                    score += 0.5
                
                # Completeness score
                non_null_values = sum(1 for v in result_data.values() if v is not None)
                total_values = len(result_data)
                if total_values > 0:
                    score += 0.5 * (non_null_values / total_values)
                
                return min(1.0, score)
            
            elif isinstance(result_data, (list, tuple)):
                return 0.8 if result_data else 0.2
            
            else:
                return 0.6 if result_data is not None else 0.0
                
        except Exception:
            return 0.0
    
    async def _calculate_confidence_score(
        self,
        result_data: Any,
        quality_score: float
    ) -> float:
        """Calculate confidence score for result"""
        try:
            # Base confidence on quality score
            confidence = quality_score
            
            # Adjust based on data characteristics
            if isinstance(result_data, dict):
                if 'error' in result_data:
                    confidence = 0.0
                elif 'confidence' in result_data:
                    # Use provided confidence if available
                    confidence = min(1.0, result_data['confidence'])
            
            return confidence
            
        except Exception:
            return 0.0
    
    async def _calculate_throughput(self) -> float:
        """Calculate processing throughput per minute"""
        try:
            # Simple throughput calculation based on recent completions
            if self.processing_stats['last_processed']:
                time_diff = (datetime.now() - self.processing_stats['last_processed']).total_seconds()
                if time_diff > 0:
                    return (self.processing_stats['completed_tasks'] / time_diff) * 60
            
            return 0.0
            
        except Exception:
            return 0.0
    
    async def _realtime_processing_worker(self) -> None:
        """Real-time processing worker"""
        while True:
            try:
                if not self.processing_queue.empty():
                    priority, task = self.processing_queue.get_nowait()
                    
                    if task.mode == ProcessingMode.REALTIME:
                        # Process immediately
                        await self._execute_task(task)
                    else:
                        # Put back for batch processing
                        self.processing_queue.put((priority, task))
                
                await asyncio.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Error in realtime processing worker: {str(e)}")
                await asyncio.sleep(1)
    
    async def _batch_processing_worker(self) -> None:
        """Batch processing worker"""
        while True:
            try:
                # Collect batch tasks
                batch_tasks = []
                
                while len(batch_tasks) < self.batch_size and not self.processing_queue.empty():
                    try:
                        priority, task = self.processing_queue.get_nowait()
                        if task.mode in [ProcessingMode.BATCH, ProcessingMode.HYBRID]:
                            batch_tasks.append(task)
                    except queue.Empty:
                        break
                
                # Process batch
                if batch_tasks:
                    await self._execute_batch(batch_tasks)
                
                await asyncio.sleep(5)  # Batch processing interval
                
            except Exception as e:
                self.logger.error(f"Error in batch processing worker: {str(e)}")
                await asyncio.sleep(5)
    
    async def _monitoring_worker(self) -> None:
        """Performance monitoring worker"""
        while True:
            try:
                # Update processing statistics
                self.processing_stats['queue_size'] = self.processing_queue.qsize()
                
                # Log performance metrics
                if self.processing_stats['total_tasks'] > 0:
                    success_rate = (
                        self.processing_stats['completed_tasks'] / 
                        self.processing_stats['total_tasks']
                    )
                    
                    if success_rate < 0.8:
                        self.logger.warning(f"Low processing success rate: {success_rate:.2f}")
                
                await asyncio.sleep(60)  # Monitor every minute
                
            except Exception as e:
                self.logger.error(f"Error in monitoring worker: {str(e)}")
                await asyncio.sleep(60)
    
    async def _execute_task(self, task: ProcessingTask) -> None:
        """Execute single processing task"""
        try:
            start_time = datetime.now()
            
            if task.task_type in self.processors:
                processor = self.processors[task.task_type]
                result_data = await processor(task.data, task.parameters)
                
                processing_time = (datetime.now() - start_time).total_seconds()
                quality_score = await self._calculate_quality_score(result_data)
                confidence = await self._calculate_confidence_score(result_data, quality_score)
                
                result = ProcessingResult(
                    task_id=task.task_id,
                    result_type=task.task_type,
                    data=result_data,
                    processing_time=processing_time,
                    quality_score=quality_score,
                    confidence=confidence,
                    metadata=task.metadata
                )
                
                self.completed_tasks[task.task_id] = result
                self.processing_stats['completed_tasks'] += 1
                
            else:
                # Unknown processor type
                error_result = ProcessingResult(
                    task_id=task.task_id,
                    result_type='error',
                    data={'error': f'Unknown processor type: {task.task_type}'},
                    processing_time=0.0,
                    quality_score=0.0,
                    confidence=0.0,
                    metadata=task.metadata
                )
                
                self.completed_tasks[task.task_id] = error_result
                self.processing_stats['failed_tasks'] += 1
            
            # Update average processing time
            total_completed = self.processing_stats['completed_tasks']
            if total_completed > 0:
                current_avg = self.processing_stats['average_processing_time']
                processing_time = (datetime.now() - start_time).total_seconds()
                
                new_avg = ((current_avg * (total_completed - 1)) + processing_time) / total_completed
                self.processing_stats['average_processing_time'] = new_avg
            
            self.processing_stats['last_processed'] = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Error executing task {task.task_id}: {str(e)}")
            self.processing_stats['failed_tasks'] += 1
    
    async def _execute_batch(self, tasks: List[ProcessingTask]) -> None:
        """Execute batch of processing tasks"""
        try:
            # Group tasks by type
            task_groups = defaultdict(list)
            for task in tasks:
                task_groups[task.task_type].append(task)
            
            # Process each group
            for task_type, group_tasks in task_groups.items():
                if task_type in self.processors:
                    processor = self.processors[task_type]
                    
                    # Process group
                    for task in group_tasks:
                        await self._execute_task(task)
                else:
                    # Handle unknown processor types
                    for task in group_tasks:
                        self.processing_stats['failed_tasks'] += 1
            
        except Exception as e:
            self.logger.error(f"Error executing batch: {str(e)}")
            self.processing_stats['failed_tasks'] += len(tasks)
    
    async def _complete_pending_tasks(self) -> None:
        """Complete all pending tasks before shutdown"""
        try:
            pending_count = self.processing_queue.qsize()
            if pending_count > 0:
                self.logger.info(f"Completing {pending_count} pending tasks...")
                
                # Process remaining tasks
                while not self.processing_queue.empty():
                    try:
                        priority, task = self.processing_queue.get_nowait()
                        await self._execute_task(task)
                    except queue.Empty:
                        break
                
                self.logger.info("All pending tasks completed")
            
        except Exception as e:
            self.logger.error(f"Error completing pending tasks: {str(e)}")
