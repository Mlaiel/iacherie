"""📊 Vector Database Analytics Engine
===================================

Advanced analytics and insights for vector database performance and content patterns.
Provides detailed metrics, trend analysis, and optimization recommendations.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL IMPORTANT ⚠️
=====================================
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation 
écrite explicite est strictement interdite et constitue une violation 
des droits d'auteur passible de poursuites judiciaires.

Contact: mlaiel@live.de
"""import asyncio
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import time
import json
from collections import defaultdict, deque
from pathlib import Path
import pickle
from datetime import datetime, timedelta

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False

try:
    from sklearn.cluster import DBSCAN, KMeans
    from sklearn.decomposition import PCA
    from sklearn.manifold import TSNE
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics tracked"""    PERFORMANCE = "performance"
    USAGE = "usage"
    QUALITY = "quality"
    DISTRIBUTION = "distribution"
    SIMILARITY = "similarity"
    ERROR = "error"


class AnalyticsLevel(Enum):
    """Analytics detail levels"""    BASIC = "basic"
    DETAILED = "detailed"
    COMPREHENSIVE = "comprehensive"
    EXPERT = "expert"


@dataclass
class PerformanceMetric:
    """Individual performance measurement"""    metric_name: str
    value: float
    unit: str
    timestamp: float
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalyticsReport:
    """Complete analytics report"""    report_id: str
    generated_at: float
    period_start: float
    period_end: float
    level: AnalyticsLevel
    metrics: Dict[str, Any]
    insights: List[str]
    recommendations: List[str]
    charts: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContentPattern:
    """Detected content pattern"""    pattern_id: str
    pattern_type: str
    confidence: float
    frequency: int
    sample_vectors: List[str]
    characteristics: Dict[str, Any]
    detected_at: float


class MetricsCollector:
    """Collect and aggregate performance metrics"""    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.MetricsCollector")
        
        # Metrics storage
        self.metrics_buffer = deque(maxlen=config.get('buffer_size', 10000))
        self.aggregated_metrics = defaultdict(list)
        self.metric_summaries = {}
        
        # Configuration
        self.aggregation_interval = config.get('aggregation_interval_seconds', 60)
        self.retention_days = config.get('retention_days', 30)
        self.auto_aggregate = config.get('auto_aggregate', True)
        
        # Background task
        self.aggregation_task = None
        
        # Metric definitions
        self.metric_definitions = {
            'search_latency_ms': {'type': 'performance', 'aggregations': ['mean', 'p95', 'p99', 'max']},
            'index_size_mb': {'type': 'usage', 'aggregations': ['mean', 'max']},
            'similarity_scores': {'type': 'quality', 'aggregations': ['mean', 'std', 'min', 'max']},
            'error_rate': {'type': 'error', 'aggregations': ['mean', 'sum']},
            'vectors_processed': {'type': 'usage', 'aggregations': ['sum', 'rate']},
            'cache_hit_rate': {'type': 'performance', 'aggregations': ['mean']},
            'duplicate_rate': {'type': 'quality', 'aggregations': ['mean', 'sum']}
        }
    
    async def start_collection(self):
        """Start background metrics aggregation"""        if self.auto_aggregate and not self.aggregation_task:
            self.aggregation_task = asyncio.create_task(self._aggregation_loop())
            self.logger.info("Metrics collection started")
    
    async def stop_collection(self):
        """Stop background metrics aggregation"""        if self.aggregation_task:
            self.aggregation_task.cancel()
            try:
                await self.aggregation_task
            except asyncio.CancelledError:
                pass
            self.aggregation_task = None
            self.logger.info("Metrics collection stopped")
    
    async def record_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = "",
        tags: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record a new metric value"""        try:
            metric = PerformanceMetric(
                metric_name=metric_name,
                value=value,
                unit=unit,
                timestamp=time.time(),
                tags=tags or {},
                metadata=metadata or {}
            )
            
            self.metrics_buffer.append(metric)
            
        except Exception as e:
            self.logger.error(f"Failed to record metric {metric_name}: {e}")
    
    async def record_search_performance(self, latency_ms: float, result_count: int, cache_hit: bool):
        """Record search operation performance"""        await self.record_metric('search_latency_ms', latency_ms, 'ms')
        await self.record_metric('search_results', result_count, 'count')
        await self.record_metric('cache_hit_rate', 1.0 if cache_hit else 0.0, 'ratio')
    
    async def record_index_stats(self, total_vectors: int, index_size_mb: float, dimension: int):
        """Record index statistics"""        await self.record_metric('vectors_total', total_vectors, 'count')
        await self.record_metric('index_size_mb', index_size_mb, 'MB')
        await self.record_metric('vector_dimension', dimension, 'count')
    
    async def record_similarity_distribution(self, similarity_scores: List[float]):
        """Record similarity score distribution"""        if not similarity_scores:
            return
        
        scores_array = np.array(similarity_scores)
        
        await self.record_metric('similarity_mean', float(np.mean(scores_array)), 'score')
        await self.record_metric('similarity_std', float(np.std(scores_array)), 'score')
        await self.record_metric('similarity_min', float(np.min(scores_array)), 'score')
        await self.record_metric('similarity_max', float(np.max(scores_array)), 'score')
    
    async def get_metric_summary(self, metric_name: str, hours: int = 24) -> Dict[str, Any]:
        """Get aggregated metric summary for time period"""        try:
            end_time = time.time()
            start_time = end_time - (hours * 3600)
            
            # Filter metrics by time and name
            relevant_metrics = [
                m for m in self.metrics_buffer
                if m.metric_name == metric_name and start_time <= m.timestamp <= end_time
            ]
            
            if not relevant_metrics:
                return {'error': f'No data for metric {metric_name}'}
            
            values = [m.value for m in relevant_metrics]
            
            # Calculate aggregations
            summary = {
                'metric_name': metric_name,
                'period_hours': hours,
                'sample_count': len(values),
                'mean': float(np.mean(values)),
                'std': float(np.std(values)),
                'min': float(np.min(values)),
                'max': float(np.max(values)),
                'p50': float(np.percentile(values, 50)),
                'p95': float(np.percentile(values, 95)),
                'p99': float(np.percentile(values, 99))
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to get metric summary for {metric_name}: {e}")
            return {'error': str(e)}
    
    async def _aggregation_loop(self):
        """Background loop for metrics aggregation"""        while True:
            try:
                await self._aggregate_metrics()
                await asyncio.sleep(self.aggregation_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Metrics aggregation error: {e}")
                await asyncio.sleep(self.aggregation_interval)
    
    async def _aggregate_metrics(self):
        """Aggregate collected metrics"""        try:
            current_time = time.time()
            cutoff_time = current_time - self.aggregation_interval
            
            # Group metrics by name and time window
            metrics_to_aggregate = defaultdict(list)
            
            for metric in list(self.metrics_buffer):
                if metric.timestamp >= cutoff_time:
                    metrics_to_aggregate[metric.metric_name].append(metric)
            
            # Aggregate each metric type
            for metric_name, metrics in metrics_to_aggregate.items():
                if metric_name in self.metric_definitions:
                    aggregations = self.metric_definitions[metric_name]['aggregations']
                    values = [m.value for m in metrics]
                    
                    if values:
                        aggregated = {}
                        for agg_type in aggregations:
                            if agg_type == 'mean':
                                aggregated[agg_type] = float(np.mean(values))
                            elif agg_type == 'sum':
                                aggregated[agg_type] = float(np.sum(values))
                            elif agg_type == 'max':
                                aggregated[agg_type] = float(np.max(values))
                            elif agg_type == 'min':
                                aggregated[agg_type] = float(np.min(values))
                            elif agg_type == 'std':
                                aggregated[agg_type] = float(np.std(values))
                            elif agg_type == 'p95':
                                aggregated[agg_type] = float(np.percentile(values, 95))
                            elif agg_type == 'p99':
                                aggregated[agg_type] = float(np.percentile(values, 99))
                            elif agg_type == 'rate':
                                aggregated[agg_type] = len(values) / self.aggregation_interval
                        
                        self.aggregated_metrics[metric_name].append({
                            'timestamp': current_time,
                            'values': aggregated,
                            'sample_count': len(values)
                        })
            
            # Clean old aggregated data
            retention_seconds = self.retention_days * 24 * 3600
            cutoff_time = current_time - retention_seconds
            
            for metric_name in self.aggregated_metrics:
                self.aggregated_metrics[metric_name] = [
                    agg for agg in self.aggregated_metrics[metric_name]
                    if agg['timestamp'] >= cutoff_time
                ]
                
        except Exception as e:
            self.logger.error(f"Metrics aggregation failed: {e}")


class PatternDetector:
    """Detect patterns in vector content and usage"""    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.PatternDetector")
        
        # Pattern storage
        self.detected_patterns = {}
        self.pattern_history = []
        
        # Configuration
        self.min_pattern_frequency = config.get('min_pattern_frequency', 5)
        self.similarity_threshold = config.get('pattern_similarity_threshold', 0.85)
        self.enable_clustering = config.get('enable_clustering', True) and SKLEARN_AVAILABLE
        
        # Clustering parameters
        self.cluster_eps = config.get('cluster_eps', 0.3)
        self.cluster_min_samples = config.get('cluster_min_samples', 5)
    
    async def analyze_content_patterns(self, embeddings: List[np.ndarray], metadata_list: List[Dict[str, Any]]) -> List[ContentPattern]:
        """Analyze patterns in content embeddings"""        try:
            if not embeddings or not self.enable_clustering:
                return []
            
            # Stack embeddings
            embedding_matrix = np.vstack(embeddings)
            
            # Detect clusters using DBSCAN
            clustering = DBSCAN(eps=self.cluster_eps, min_samples=self.cluster_min_samples)
            cluster_labels = clustering.fit_predict(embedding_matrix)
            
            patterns = []
            
            # Analyze each cluster
            unique_labels = set(cluster_labels)
            for label in unique_labels:
                if label == -1:  # Noise points
                    continue
                
                cluster_indices = np.where(cluster_labels == label)[0]
                cluster_size = len(cluster_indices)
                
                if cluster_size >= self.min_pattern_frequency:
                    # Calculate cluster characteristics
                    cluster_embeddings = embedding_matrix[cluster_indices]
                    cluster_metadata = [metadata_list[i] for i in cluster_indices]
                    
                    # Analyze metadata patterns
                    content_types = [m.get('content_type', 'unknown') for m in cluster_metadata]
                    creators = [m.get('creator', 'unknown') for m in cluster_metadata]
                    
                    most_common_type = max(set(content_types), key=content_types.count)
                    most_common_creator = max(set(creators), key=creators.count)
                    
                    # Calculate pattern confidence
                    type_consistency = content_types.count(most_common_type) / len(content_types)
                    creator_consistency = creators.count(most_common_creator) / len(creators)
                    
                    confidence = (type_consistency + creator_consistency) / 2
                    
                    pattern = ContentPattern(
                        pattern_id=f"cluster_{label}_{int(time.time())}",
                        pattern_type="content_similarity",
                        confidence=confidence,
                        frequency=cluster_size,
                        sample_vectors=[f"vector_{i}" for i in cluster_indices[:5]],
                        characteristics={
                            'dominant_content_type': most_common_type,
                            'dominant_creator': most_common_creator,
                            'type_consistency': type_consistency,
                            'creator_consistency': creator_consistency,
                            'cluster_center': np.mean(cluster_embeddings, axis=0).tolist(),
                            'cluster_std': np.std(cluster_embeddings, axis=0).tolist()
                        },
                        detected_at=time.time()
                    )
                    
                    patterns.append(pattern)
                    self.detected_patterns[pattern.pattern_id] = pattern
            
            self.pattern_history.extend(patterns)
            self.logger.info(f"Detected {len(patterns)} content patterns")
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Pattern analysis failed: {e}")
            return []
    
    async def detect_duplicate_patterns(self, similarity_matrix: np.ndarray, threshold: float = 0.95) -> List[ContentPattern]:
        """Detect potential duplicate content patterns"""        try:
            patterns = []
            
            # Find high similarity pairs
            high_similarity_pairs = np.where(similarity_matrix > threshold)
            
            if len(high_similarity_pairs[0]) > 0:
                # Group into potential duplicate clusters
                duplicate_groups = defaultdict(set)
                
                for i, j in zip(high_similarity_pairs[0], high_similarity_pairs[1]):
                    if i != j:  # Don't include self-similarity
                        duplicate_groups[i].add(j)
                        duplicate_groups[j].add(i)
                
                # Create patterns for significant duplicate groups
                for group_id, similar_indices in duplicate_groups.items():
                    if len(similar_indices) >= self.min_pattern_frequency:
                        pattern = ContentPattern(
                            pattern_id=f"duplicates_{group_id}_{int(time.time())}",
                            pattern_type="potential_duplicates",
                            confidence=float(np.mean(similarity_matrix[group_id, list(similar_indices)])),
                            frequency=len(similar_indices),
                            sample_vectors=[f"vector_{group_id}"] + [f"vector_{i}" for i in list(similar_indices)[:4]],
                            characteristics={
                                'similarity_threshold': threshold,
                                'average_similarity': float(np.mean(similarity_matrix[group_id, list(similar_indices)])),
                                'max_similarity': float(np.max(similarity_matrix[group_id, list(similar_indices)]))
                            },
                            detected_at=time.time()
                        )
                        
                        patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Duplicate pattern detection failed: {e}")
            return []
    
    def get_pattern_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get summary of detected patterns"""        try:
            end_time = time.time()
            start_time = end_time - (hours * 3600)
            
            recent_patterns = [
                p for p in self.pattern_history
                if start_time <= p.detected_at <= end_time
            ]
            
            # Group by pattern type
            patterns_by_type = defaultdict(list)
            for pattern in recent_patterns:
                patterns_by_type[pattern.pattern_type].append(pattern)
            
            summary = {
                'period_hours': hours,
                'total_patterns': len(recent_patterns),
                'patterns_by_type': {
                    pattern_type: len(patterns)
                    for pattern_type, patterns in patterns_by_type.items()
                },
                'average_confidence': float(np.mean([p.confidence for p in recent_patterns])) if recent_patterns else 0,
                'most_frequent_pattern': max(recent_patterns, key=lambda p: p.frequency) if recent_patterns else None
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to get pattern summary: {e}")
            return {'error': str(e)}


class AnalyticsEngine:
    """Main analytics engine coordinating all analytics components"""    
    def __init__(self, vector_store, config: Dict[str, Any]):
        self.vector_store = vector_store
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.AnalyticsEngine")
        
        # Components
        self.metrics_collector = MetricsCollector(config.get('metrics', {}))
        self.pattern_detector = PatternDetector(config.get('patterns', {}))
        
        # Report storage
        self.reports = {}
        self.report_history = []
        
        # Configuration
        self.auto_reporting = config.get('auto_reporting', True)
        self.report_interval_hours = config.get('report_interval_hours', 24)
        self.enable_visualizations = config.get('enable_visualizations', True) and PLOTTING_AVAILABLE
        
        # Background task
        self.reporting_task = None
    
    async def start_analytics(self):
        """Start analytics collection and reporting"""        await self.metrics_collector.start_collection()
        
        if self.auto_reporting:
            self.reporting_task = asyncio.create_task(self._reporting_loop())
        
        self.logger.info("Analytics engine started")
    
    async def stop_analytics(self):
        """Stop analytics collection and reporting"""        await self.metrics_collector.stop_collection()
        
        if self.reporting_task:
            self.reporting_task.cancel()
            try:
                await self.reporting_task
            except asyncio.CancelledError:
                pass
            self.reporting_task = None
        
        self.logger.info("Analytics engine stopped")
    
    async def generate_analytics_report(self, level: AnalyticsLevel = AnalyticsLevel.DETAILED, hours: int = 24) -> AnalyticsReport:
        """Generate comprehensive analytics report"""        try:
            report_id = f"report_{int(time.time())}"
            end_time = time.time()
            start_time = end_time - (hours * 3600)
            
            # Collect metrics
            metrics = {}
            
            # Performance metrics
            search_latency = await self.metrics_collector.get_metric_summary('search_latency_ms', hours)
            cache_hit_rate = await self.metrics_collector.get_metric_summary('cache_hit_rate', hours)
            
            metrics['performance'] = {
                'search_latency': search_latency,
                'cache_hit_rate': cache_hit_rate
            }
            
            # Usage metrics
            vectors_total = await self.metrics_collector.get_metric_summary('vectors_total', hours)
            index_size = await self.metrics_collector.get_metric_summary('index_size_mb', hours)
            
            metrics['usage'] = {
                'vectors_total': vectors_total,
                'index_size': index_size
            }
            
            # Quality metrics
            similarity_scores = await self.metrics_collector.get_metric_summary('similarity_mean', hours)
            
            metrics['quality'] = {
                'similarity_distribution': similarity_scores
            }
            
            # Pattern analysis
            pattern_summary = self.pattern_detector.get_pattern_summary(hours)
            metrics['patterns'] = pattern_summary
            
            # Generate insights and recommendations
            insights = await self._generate_insights(metrics)
            recommendations = await self._generate_recommendations(metrics)
            
            # Create charts if enabled
            charts = {}
            if self.enable_visualizations and level in [AnalyticsLevel.DETAILED, AnalyticsLevel.COMPREHENSIVE]:
                charts = await self._generate_charts(metrics)
            
            report = AnalyticsReport(
                report_id=report_id,
                generated_at=end_time,
                period_start=start_time,
                period_end=end_time,
                level=level,
                metrics=metrics,
                insights=insights,
                recommendations=recommendations,
                charts=charts
            )
            
            self.reports[report_id] = report
            self.report_history.append(report)
            
            self.logger.info(f"Generated analytics report {report_id}")
            
            return report
            
        except Exception as e:
            self.logger.error(f"Analytics report generation failed: {e}")
            raise
    
    async def _generate_insights(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate insights from collected metrics"""        insights = []
        
        try:
            # Performance insights
            perf_metrics = metrics.get('performance', {})
            search_latency = perf_metrics.get('search_latency', {})
            
            if 'mean' in search_latency:
                avg_latency = search_latency['mean']
                if avg_latency > 1000:  # >1 second
                    insights.append(f"Search latency is high (avg: {avg_latency:.1f}ms). Consider index optimization.")
                elif avg_latency < 100:  # <100ms
                    insights.append(f"Excellent search performance (avg: {avg_latency:.1f}ms).")
            
            # Cache insights
            cache_hit_rate = perf_metrics.get('cache_hit_rate', {})
            if 'mean' in cache_hit_rate:
                hit_rate = cache_hit_rate['mean']
                if hit_rate < 0.5:
                    insights.append(f"Low cache hit rate ({hit_rate:.1%}). Consider increasing cache size.")
                elif hit_rate > 0.8:
                    insights.append(f"Excellent cache performance ({hit_rate:.1%}).")
            
            # Usage insights
            usage_metrics = metrics.get('usage', {})
            vectors_total = usage_metrics.get('vectors_total', {})
            
            if 'mean' in vectors_total:
                total_vectors = int(vectors_total['mean'])
                if total_vectors > 1000000:  # >1M vectors
                    insights.append(f"Large vector database ({total_vectors:,} vectors). Monitor memory usage.")
                elif total_vectors < 1000:  # <1K vectors
                    insights.append(f"Small vector database ({total_vectors:,} vectors). Good for testing.")
            
            # Pattern insights
            pattern_metrics = metrics.get('patterns', {})
            patterns_by_type = pattern_metrics.get('patterns_by_type', {})
            
            if 'potential_duplicates' in patterns_by_type:
                duplicate_count = patterns_by_type['potential_duplicates']
                if duplicate_count > 0:
                    insights.append(f"Found {duplicate_count} potential duplicate patterns. Consider deduplication.")
            
            if 'content_similarity' in patterns_by_type:
                similarity_count = patterns_by_type['content_similarity']
                if similarity_count > 10:
                    insights.append(f"High content clustering ({similarity_count} patterns). Good for recommendation systems.")
            
        except Exception as e:
            self.logger.error(f"Insight generation failed: {e}")
            insights.append("Insight generation encountered errors.")
        
        return insights
    
    async def _generate_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate optimization recommendations"""        recommendations = []
        
        try:
            # Performance recommendations
            perf_metrics = metrics.get('performance', {})
            search_latency = perf_metrics.get('search_latency', {})
            
            if 'p95' in search_latency and search_latency['p95'] > 2000:
                recommendations.append("Consider using IndexIVFPQ for better search performance on large datasets.")
            
            if 'std' in search_latency and search_latency['std'] > search_latency.get('mean', 0):
                recommendations.append("High latency variance detected. Check for concurrent operations affecting performance.")
            
            # Index recommendations
            usage_metrics = metrics.get('usage', {})
            index_size = usage_metrics.get('index_size', {})
            
            if 'mean' in index_size and index_size['mean'] > 1000:  # >1GB
                recommendations.append("Large index size. Consider using product quantization (IndexIVFPQ) to reduce memory usage.")
            
            # Cache recommendations
            cache_hit_rate = perf_metrics.get('cache_hit_rate', {})
            if 'mean' in cache_hit_rate and cache_hit_rate['mean'] < 0.6:
                recommendations.append("Low cache hit rate. Increase cache size or improve query patterns.")
            
            # Pattern-based recommendations
            pattern_metrics = metrics.get('patterns', {})
            if pattern_metrics.get('total_patterns', 0) > 50:
                recommendations.append("Many content patterns detected. Consider implementing automatic content categorization.")
            
        except Exception as e:
            self.logger.error(f"Recommendation generation failed: {e}")
            recommendations.append("Recommendation generation encountered errors.")
        
        return recommendations
    
    async def _generate_charts(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate visualization charts"""        charts = {}
        
        if not self.enable_visualizations:
            return charts
        
        try:
            # Performance trend chart
            # This would generate actual matplotlib charts
            charts['performance_trend'] = {
                'type': 'line_chart',
                'title': 'Search Performance Trend',
                'description': 'Performance metrics over time',
                'data_available': True
            }
            
            # Usage distribution chart
            charts['usage_distribution'] = {
                'type': 'bar_chart',
                'title': 'Vector Usage Distribution',
                'description': 'Distribution of vector operations',
                'data_available': True
            }
            
            # Similarity heatmap
            charts['similarity_heatmap'] = {
                'type': 'heatmap',
                'title': 'Content Similarity Patterns',
                'description': 'Similarity patterns across content types',
                'data_available': True
            }
            
        except Exception as e:
            self.logger.error(f"Chart generation failed: {e}")
        
        return charts
    
    async def _reporting_loop(self):
        """Background loop for automatic report generation"""        while True:
            try:
                await self.generate_analytics_report(AnalyticsLevel.BASIC, self.report_interval_hours)
                await asyncio.sleep(self.report_interval_hours * 3600)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Automatic reporting error: {e}")
                await asyncio.sleep(3600)  # Retry in 1 hour
    
    def get_latest_report(self) -> Optional[AnalyticsReport]:
        """Get the most recent analytics report"""        if self.report_history:
            return self.report_history[-1]
        return None
    
    def export_report(self, report_id: str, format: str = 'json') -> Optional[str]:
        """Export report in specified format"""        try:
            if report_id not in self.reports:
                return None
            
            report = self.reports[report_id]
            
            if format == 'json':
                return json.dumps({
                    'report_id': report.report_id,
                    'generated_at': report.generated_at,
                    'period_start': report.period_start,
                    'period_end': report.period_end,
                    'level': report.level.value,
                    'metrics': report.metrics,
                    'insights': report.insights,
                    'recommendations': report.recommendations
                }, indent=2, default=str)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Report export failed: {e}")
            return None
