"""⚡ Recommendation Engine Performance Profiler
============================================

Advanced profiling system for recommendation algorithms in the Creator Economy platform.
Provides real-time monitoring of collaborative filtering, content-based recommendations, and ML matching optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ INTELLECTUAL PROPERTY WARNING:
=====================================
This code is proprietary to Fahed Mlaiel <mlaiel@live.de>
- Commercial use FORBIDDEN without written authorization
- Reverse engineering STRICTLY PROHIBITED
- Distribution FORBIDDEN without explicit license
- Violation = Automatic legal prosecution

🏢 ENTERPRISE USAGE:
- Enterprise license available on request
- Technical support included with license
- Maintenance and updates assured
- Technical team training provided
"""

import asyncio
import logging
import time
import threading
from typing import Dict, List, Optional, Any, Callable, Union, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import statistics
from collections import defaultdict, deque
import numpy as np

from prometheus_client import Counter, Gauge, Histogram, Summary

logger = logging.getLogger(__name__)


class RecommendationAlgorithm(Enum):
    """Recommendation algorithm types"""
    
    COLLABORATIVE_FILTERING = "collaborative_filtering"
    CONTENT_BASED = "content_based"
    HYBRID = "hybrid"
    MATRIX_FACTORIZATION = "matrix_factorization"
    DEEP_LEARNING = "deep_learning"
    ASSOCIATION_RULES = "association_rules"
    CLUSTERING_BASED = "clustering_based"
    GRAPH_BASED = "graph_based"
    REINFORCEMENT_LEARNING = "reinforcement_learning"
    CONTEXTUAL_BANDITS = "contextual_bandits"


class RecommendationType(Enum):
    """Types of recommendations"""
    
    CREATOR_MATCHING = "creator_matching"
    CONTENT_RECOMMENDATION = "content_recommendation"
    COLLABORATION_SUGGESTION = "collaboration_suggestion"
    AUDIENCE_TARGETING = "audience_targeting"
    TREND_PREDICTION = "trend_prediction"
    MONETIZATION_OPPORTUNITY = "monetization_opportunity"
    SKILL_DEVELOPMENT = "skill_development"
    PLATFORM_SUGGESTION = "platform_suggestion"


class QualityMetric(Enum):
    """Recommendation quality metrics"""
    
    PRECISION = "precision"
    RECALL = "recall"
    F1_SCORE = "f1_score"
    NDCG = "ndcg"
    MAP = "map"
    MRR = "mrr"
    DIVERSITY = "diversity"
    NOVELTY = "novelty"
    COVERAGE = "coverage"
    SERENDIPITY = "serendipity"


@dataclass
class UserProfile:
    """User profile for recommendations"""
    
    user_id: str
    content_preferences: Dict[str, float]
    interaction_history: List[str]
    demographic_info: Dict[str, Any]
    behavioral_patterns: Dict[str, float]
    engagement_metrics: Dict[str, float]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class RecommendationRequest:
    """Recommendation request parameters"""
    
    user_profile: UserProfile
    recommendation_type: RecommendationType
    algorithm: RecommendationAlgorithm
    num_recommendations: int
    context: Dict[str, Any]
    filters: Dict[str, Any]
    diversity_factor: float = 0.5
    novelty_factor: float = 0.3
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class RecommendationResult:
    """Recommendation algorithm result"""
    
    recommendations: List[Dict[str, Any]]
    confidence_scores: List[float]
    relevance_scores: List[float]
    diversity_score: float
    novelty_score: float
    explanation: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class RecommendationMetrics:
    """Recommendation engine performance metrics"""
    
    algorithm: RecommendationAlgorithm
    recommendation_type: RecommendationType
    request: RecommendationRequest
    result: RecommendationResult
    processing_time: float  # seconds
    data_loading_time: float  # seconds
    model_inference_time: float  # seconds
    postprocessing_time: float  # seconds
    memory_usage: int  # MB
    cpu_usage: float  # percentage
    cache_hit: bool = False
    model_size: Optional[int] = None  # MB
    num_candidates: int = 0
    filtering_time: float = 0.0
    ranking_time: float = 0.0
    quality_metrics: Dict[QualityMetric, float] = field(default_factory=dict)
    business_metrics: Dict[str, float] = field(default_factory=dict)
    a_b_test_group: Optional[str] = None
    error_count: int = 0
    warnings: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class RecommendationBottleneck:
    """Recommendation system bottleneck detection"""
    
    bottleneck_type: str
    severity: str  # low, medium, high, critical
    description: str
    affected_algorithm: RecommendationAlgorithm
    recommendation_type: RecommendationType
    performance_impact: float  # percentage
    optimization_suggestions: List[str]
    algorithm_recommendations: List[str]
    infrastructure_recommendations: List[str]
    timestamp: datetime = field(default_factory=datetime.now)


class RecommendationEngineProfiler:
    """
    Advanced Recommendation Engine Performance Profiler
    
    Provides comprehensive profiling for recommendation systems with focus on:
    - Algorithm performance monitoring
    - Quality metrics tracking
    - Real-time recommendation profiling
    - A/B testing support
    - Business impact measurement
    """
    
    def __init__(
        self,
        enable_quality_monitoring: bool = True,
        enable_ab_testing: bool = True,
        sampling_interval: float = 1.0,
        max_history_size: int = 50000,
        quality_threshold: float = 0.7
    ):
        """
        Initialize Recommendation Engine Profiler
        
        Args:
            enable_quality_monitoring: Enable recommendation quality tracking
            enable_ab_testing: Enable A/B testing support
            sampling_interval: Metrics collection interval in seconds
            max_history_size: Maximum number of metrics to keep
            quality_threshold: Minimum quality threshold for alerts
        """
        self.enable_quality_monitoring = enable_quality_monitoring
        self.enable_ab_testing = enable_ab_testing
        self.sampling_interval = sampling_interval
        self.max_history_size = max_history_size
        self.quality_threshold = quality_threshold
        
        # Metrics storage
        self.recommendation_metrics: deque = deque(maxlen=max_history_size)
        self.bottlenecks: deque = deque(maxlen=max_history_size)
        
        # Active profiling sessions
        self.active_sessions: Dict[str, Dict] = {}
        self.session_lock = threading.Lock()
        
        # Algorithm performance tracking
        self.algorithm_performance: Dict[RecommendationAlgorithm, List[float]] = defaultdict(list)
        self.quality_trends: Dict[RecommendationAlgorithm, Dict[QualityMetric, List[float]]] = defaultdict(lambda: defaultdict(list))
        
        # A/B testing results
        self.ab_test_results: Dict[str, List[RecommendationMetrics]] = defaultdict(list)
        
        # Cache for user profiles and models
        self.user_profile_cache: Dict[str, UserProfile] = {}
        self.model_cache: Dict[str, Any] = {}
        
        # Prometheus metrics
        self._setup_prometheus_metrics()
        
        # Background monitoring
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        
        logger.info("RecommendationEngineProfiler initialized")
    
    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics for monitoring"""
        
        self.processing_time_histogram = Histogram(
            'recommendation_processing_time_seconds',
            'Recommendation processing time',
            ['algorithm', 'recommendation_type']
        )
        
        self.quality_gauge = Gauge(
            'recommendation_quality_score',
            'Recommendation quality metrics',
            ['algorithm', 'metric_type']
        )
        
        self.throughput_gauge = Gauge(
            'recommendation_throughput_requests_per_second',
            'Recommendation throughput',
            ['algorithm']
        )
        
        self.cache_hit_rate_gauge = Gauge(
            'recommendation_cache_hit_rate',
            'Recommendation cache hit rate',
            ['cache_type']
        )
        
        self.diversity_gauge = Gauge(
            'recommendation_diversity_score',
            'Recommendation diversity score',
            ['algorithm']
        )
        
        self.business_impact_gauge = Gauge(
            'recommendation_business_impact',
            'Recommendation business impact metrics',
            ['metric_type', 'algorithm']
        )
        
        self.bottleneck_counter = Counter(
            'recommendation_bottlenecks_total',
            'Total recommendation bottlenecks',
            ['bottleneck_type', 'severity']
        )
        
        self.error_counter = Counter(
            'recommendation_errors_total',
            'Total recommendation errors',
            ['algorithm', 'recommendation_type']
        )
    
    def start_monitoring(self):
        """Start background monitoring thread"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        logger.info("Recommendation engine background monitoring started")
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5.0)
        logger.info("Recommendation engine background monitoring stopped")
    
    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.monitoring_active:
            try:
                # Analyze for bottlenecks
                self._detect_bottlenecks()
                
                # Update quality trend analysis
                self._update_quality_trends()
                
                # Process A/B test results
                if self.enable_ab_testing:
                    self._analyze_ab_tests()
                
                time.sleep(self.sampling_interval)
                
            except Exception as e:
                logger.error("Error in recommendation monitoring loop: %s", e)
                time.sleep(1.0)
    
    def start_recommendation_profiling(
        self,
        algorithm: RecommendationAlgorithm,
        recommendation_type: RecommendationType,
        user_profile: UserProfile,
        num_recommendations: int = 10,
        context: Optional[Dict[str, Any]] = None,
        filters: Optional[Dict[str, Any]] = None,
        ab_test_group: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> str:
        """
        Start profiling a recommendation request
        
        Args:
            algorithm: Recommendation algorithm to use
            recommendation_type: Type of recommendation
            user_profile: User profile for recommendations
            num_recommendations: Number of recommendations to generate
            context: Additional context information
            filters: Filtering criteria
            ab_test_group: A/B test group identifier
            session_id: Optional session identifier
        
        Returns:
            session_id: Unique identifier for this profiling session
        """
        if session_id is None:
            session_id = f"{algorithm.value}_{recommendation_type.value}_{int(time.time() * 1000)}"
        
        request = RecommendationRequest(
            user_profile=user_profile,
            recommendation_type=recommendation_type,
            algorithm=algorithm,
            num_recommendations=num_recommendations,
            context=context or {},
            filters=filters or {}
        )
        
        session_data = {
            'algorithm': algorithm,
            'recommendation_type': recommendation_type,
            'request': request,
            'ab_test_group': ab_test_group,
            'start_time': time.time(),
            'data_loading_start': None,
            'model_inference_start': None,
            'postprocessing_start': None,
            'error_count': 0,
            'warnings': [],
            'cache_hits': {
                'user_profile': False,
                'model': False,
                'results': False
            }
        }
        
        with self.session_lock:
            self.active_sessions[session_id] = session_data
        
        logger.debug("Started recommendation profiling session: %s", session_id)
        return session_id
    
    def mark_data_loading_start(self, session_id: str):
        """Mark the start of data loading phase"""
        with self.session_lock:
            if session_id in self.active_sessions:
                self.active_sessions[session_id]['data_loading_start'] = time.time()
    
    def mark_model_inference_start(self, session_id: str):
        """Mark the start of model inference phase"""
        with self.session_lock:
            if session_id in self.active_sessions:
                self.active_sessions[session_id]['model_inference_start'] = time.time()
    
    def mark_postprocessing_start(self, session_id: str):
        """Mark the start of postprocessing phase"""
        with self.session_lock:
            if session_id in self.active_sessions:
                self.active_sessions[session_id]['postprocessing_start'] = time.time()
    
    def record_cache_hit(self, session_id: str, cache_type: str):
        """Record a cache hit"""
        with self.session_lock:
            if session_id in self.active_sessions:
                self.active_sessions[session_id]['cache_hits'][cache_type] = True
    
    def add_warning(self, session_id: str, warning: str):
        """Add a warning to the session"""
        with self.session_lock:
            if session_id in self.active_sessions:
                self.active_sessions[session_id]['warnings'].append(warning)
    
    def increment_error_count(self, session_id: str):
        """Increment error count for the session"""
        with self.session_lock:
            if session_id in self.active_sessions:
                self.active_sessions[session_id]['error_count'] += 1
    
    def end_recommendation_profiling(
        self,
        session_id: str,
        result: RecommendationResult,
        quality_metrics: Optional[Dict[QualityMetric, float]] = None,
        business_metrics: Optional[Dict[str, float]] = None,
        num_candidates: int = 0,
        model_size: Optional[int] = None
    ) -> RecommendationMetrics:
        """
        End profiling session and return metrics
        
        Args:
            session_id: Session identifier
            result: Recommendation result
            quality_metrics: Quality assessment metrics
            business_metrics: Business impact metrics
            num_candidates: Number of candidates considered
            model_size: Model size in MB
        
        Returns:
            RecommendationMetrics: Complete recommendation metrics
        """
        with self.session_lock:
            if session_id not in self.active_sessions:
                raise ValueError(f"Session {session_id} not found")
            
            session_data = self.active_sessions.pop(session_id)
        
        end_time = time.time()
        total_time = end_time - session_data['start_time']
        
        # Calculate phase timings
        data_loading_time = 0.0
        model_inference_time = 0.0
        postprocessing_time = 0.0
        
        if session_data['data_loading_start']:
            if session_data['model_inference_start']:
                data_loading_time = session_data['model_inference_start'] - session_data['data_loading_start']
            else:
                data_loading_time = end_time - session_data['data_loading_start']
        
        if session_data['model_inference_start']:
            if session_data['postprocessing_start']:
                model_inference_time = session_data['postprocessing_start'] - session_data['model_inference_start']
            else:
                model_inference_time = end_time - session_data['model_inference_start']
        
        if session_data['postprocessing_start']:
            postprocessing_time = end_time - session_data['postprocessing_start']
        
        # Determine cache hit status
        cache_hit = any(session_data['cache_hits'].values())
        
        # Create metrics object
        metrics = RecommendationMetrics(
            algorithm=session_data['algorithm'],
            recommendation_type=session_data['recommendation_type'],
            request=session_data['request'],
            result=result,
            processing_time=total_time,
            data_loading_time=data_loading_time,
            model_inference_time=model_inference_time,
            postprocessing_time=postprocessing_time,
            memory_usage=0,  # TODO: Implement memory monitoring
            cpu_usage=0.0,   # TODO: Implement CPU monitoring
            cache_hit=cache_hit,
            model_size=model_size,
            num_candidates=num_candidates,
            quality_metrics=quality_metrics or {},
            business_metrics=business_metrics or {},
            a_b_test_group=session_data['ab_test_group'],
            error_count=session_data['error_count'],
            warnings=session_data['warnings']
        )
        
        # Store metrics
        self.recommendation_metrics.append(metrics)
        
        # Track algorithm performance
        self.algorithm_performance[session_data['algorithm']].append(total_time)
        
        # Track quality trends
        if self.enable_quality_monitoring and quality_metrics:
            for metric_type, score in quality_metrics.items():
                self.quality_trends[session_data['algorithm']][metric_type].append(score)
        
        # Store A/B test results
        if self.enable_ab_testing and session_data['ab_test_group']:
            self.ab_test_results[session_data['ab_test_group']].append(metrics)
        
        # Update Prometheus metrics
        self.processing_time_histogram.labels(
            algorithm=metrics.algorithm.value,
            recommendation_type=metrics.recommendation_type.value
        ).observe(metrics.processing_time)
        
        if quality_metrics:
            for metric_type, score in quality_metrics.items():
                self.quality_gauge.labels(
                    algorithm=metrics.algorithm.value,
                    metric_type=metric_type.value
                ).set(score)
        
        self.diversity_gauge.labels(
            algorithm=metrics.algorithm.value
        ).set(result.diversity_score)
        
        if business_metrics:
            for metric_name, value in business_metrics.items():
                self.business_impact_gauge.labels(
                    metric_type=metric_name,
                    algorithm=metrics.algorithm.value
                ).set(value)
        
        if metrics.error_count > 0:
            self.error_counter.labels(
                algorithm=metrics.algorithm.value,
                recommendation_type=metrics.recommendation_type.value
            ).inc(metrics.error_count)
        
        logger.info("Recommendation profiling completed for %s: %.3fs, %d recommendations",
                   session_id, metrics.processing_time, len(result.recommendations))
        
        return metrics
    
    def _detect_bottlenecks(self):
        """Detect performance bottlenecks in recommendation system"""
        if len(self.recommendation_metrics) < 5:
            return
        
        recent_metrics = list(self.recommendation_metrics)[-20:]  # Last 20 requests
        
        # Analyze processing times by algorithm
        algorithm_times = defaultdict(list)
        for metric in recent_metrics:
            algorithm_times[metric.algorithm].append(metric.processing_time)
        
        for algorithm, times in algorithm_times.items():
            if len(times) < 3:
                continue
            
            avg_time = statistics.mean(times)
            
            # Check for slow processing
            if avg_time > 2.0:  # 2 seconds threshold
                bottleneck = RecommendationBottleneck(
                    bottleneck_type="slow_processing",
                    severity="high" if avg_time > 5.0 else "medium",
                    description=f"Average {algorithm.value} processing time is {avg_time:.2f}s",
                    affected_algorithm=algorithm,
                    recommendation_type=RecommendationType.CONTENT_RECOMMENDATION,  # Generic
                    performance_impact=min(100, (avg_time / 0.5) * 20),
                    optimization_suggestions=[
                        "Implement result caching",
                        "Pre-compute user embeddings",
                        "Use approximate algorithms for large datasets",
                        "Implement incremental learning"
                    ],
                    algorithm_recommendations=[
                        "Switch to lighter algorithms for real-time requests",
                        "Use matrix factorization for faster collaborative filtering",
                        "Implement hierarchical clustering",
                        "Use sampling for large candidate sets"
                    ],
                    infrastructure_recommendations=[
                        "Add more computing nodes",
                        "Use faster storage for embeddings",
                        "Implement distributed computing",
                        "Use GPU acceleration for deep learning models"
                    ]
                )
                self._record_bottleneck(bottleneck)
        
        # Check quality degradation
        if self.enable_quality_monitoring:
            for algorithm, quality_data in self.quality_trends.items():
                for metric_type, scores in quality_data.items():
                    if len(scores) >= 10:
                        recent_scores = scores[-5:]
                        historical_scores = scores[-10:-5]
                        
                        if (historical_scores and 
                            statistics.mean(recent_scores) < statistics.mean(historical_scores) * 0.9):
                            
                            bottleneck = RecommendationBottleneck(
                                bottleneck_type="quality_degradation",
                                severity="high",
                                description=f"{algorithm.value} {metric_type.value} degraded by 10%+",
                                affected_algorithm=algorithm,
                                recommendation_type=RecommendationType.CONTENT_RECOMMENDATION,
                                performance_impact=50,
                                optimization_suggestions=[
                                    "Retrain recommendation models",
                                    "Update user profiles",
                                    "Refresh item features",
                                    "Check for data drift"
                                ],
                                algorithm_recommendations=[
                                    "Implement online learning",
                                    "Use ensemble methods",
                                    "Add regularization to prevent overfitting",
                                    "Implement model versioning"
                                ],
                                infrastructure_recommendations=[
                                    "Set up model monitoring",
                                    "Implement automated retraining",
                                    "Use feature stores",
                                    "Implement data quality checks"
                                ]
                            )
                            self._record_bottleneck(bottleneck)
        
        # Check cache efficiency
        cache_hits = [m for m in recent_metrics if m.cache_hit]
        cache_hit_rate = len(cache_hits) / len(recent_metrics) if recent_metrics else 0
        
        if cache_hit_rate < 0.3:  # Less than 30% cache hit rate
            bottleneck = RecommendationBottleneck(
                bottleneck_type="low_cache_efficiency",
                severity="medium",
                description=f"Cache hit rate is only {cache_hit_rate:.1%}",
                affected_algorithm=RecommendationAlgorithm.COLLABORATIVE_FILTERING,  # Generic
                recommendation_type=RecommendationType.CONTENT_RECOMMENDATION,
                performance_impact=(1 - cache_hit_rate) * 30,
                optimization_suggestions=[
                    "Increase cache size",
                    "Improve cache key strategy",
                    "Implement cache warming",
                    "Use distributed caching"
                ],
                algorithm_recommendations=[
                    "Cache user embeddings",
                    "Cache similarity matrices",
                    "Pre-compute popular recommendations",
                    "Use incremental updates"
                ],
                infrastructure_recommendations=[
                    "Use Redis cluster",
                    "Implement cache partitioning",
                    "Use SSD for cache storage",
                    "Monitor cache memory usage"
                ]
            )
            self._record_bottleneck(bottleneck)
    
    def _update_quality_trends(self):
        """Update quality trend analysis"""
        if not self.enable_quality_monitoring:
            return
        
        # Keep only recent quality measurements
        for algorithm in self.quality_trends:
            for metric_type in self.quality_trends[algorithm]:
                if len(self.quality_trends[algorithm][metric_type]) > 100:
                    self.quality_trends[algorithm][metric_type] = \
                        self.quality_trends[algorithm][metric_type][-100:]
    
    def _analyze_ab_tests(self):
        """Analyze A/B test results"""
        if not self.enable_ab_testing:
            return
        
        for test_group, metrics_list in self.ab_test_results.items():
            if len(metrics_list) >= 30:  # Minimum sample size
                # Analyze performance differences
                processing_times = [m.processing_time for m in metrics_list]
                quality_scores = []
                
                for metric in metrics_list:
                    if metric.quality_metrics:
                        avg_quality = statistics.mean(metric.quality_metrics.values())
                        quality_scores.append(avg_quality)
                
                logger.info("A/B Test Group %s: Avg processing time: %.3fs, Avg quality: %.3f",
                           test_group, 
                           statistics.mean(processing_times),
                           statistics.mean(quality_scores) if quality_scores else 0)
    
    def _record_bottleneck(self, bottleneck: RecommendationBottleneck):
        """Record a detected bottleneck"""
        self.bottlenecks.append(bottleneck)
        
        # Update Prometheus counter
        self.bottleneck_counter.labels(
            bottleneck_type=bottleneck.bottleneck_type,
            severity=bottleneck.severity
        ).inc()
        
        logger.warning("Recommendation bottleneck detected: %s (%s severity)",
                      bottleneck.description, bottleneck.severity)
    
    def calculate_quality_metrics(
        self,
        recommendations: List[Dict[str, Any]],
        ground_truth: List[str],
        user_interactions: Optional[List[str]] = None
    ) -> Dict[QualityMetric, float]:
        """
        Calculate recommendation quality metrics
        
        Args:
            recommendations: List of recommended items
            ground_truth: List of relevant items
            user_interactions: Optional user interaction history
        
        Returns:
            Dictionary of quality metrics
        """
        if not recommendations or not ground_truth:
            return {}
        
        # Extract recommendation IDs
        rec_ids = [rec.get('id', '') for rec in recommendations]
        
        # Calculate precision
        relevant_recommended = len(set(rec_ids) & set(ground_truth))
        precision = relevant_recommended / len(rec_ids) if rec_ids else 0
        
        # Calculate recall
        recall = relevant_recommended / len(ground_truth) if ground_truth else 0
        
        # Calculate F1 score
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        # Calculate NDCG (simplified)
        ndcg = self._calculate_ndcg(rec_ids, ground_truth)
        
        # Calculate diversity
        diversity = self._calculate_diversity(recommendations)
        
        # Calculate novelty
        novelty = self._calculate_novelty(recommendations, user_interactions or [])
        
        return {
            QualityMetric.PRECISION: precision,
            QualityMetric.RECALL: recall,
            QualityMetric.F1_SCORE: f1_score,
            QualityMetric.NDCG: ndcg,
            QualityMetric.DIVERSITY: diversity,
            QualityMetric.NOVELTY: novelty
        }
    
    def _calculate_ndcg(self, recommendations: List[str], ground_truth: List[str]) -> float:
        """Calculate Normalized Discounted Cumulative Gain"""
        if not recommendations or not ground_truth:
            return 0.0
        
        # Calculate DCG
        dcg = 0.0
        for i, rec_id in enumerate(recommendations):
            if rec_id in ground_truth:
                dcg += 1.0 / np.log2(i + 2)  # +2 because log2(1) = 0
        
        # Calculate IDCG (assuming all ground truth items are relevant)
        idcg = sum(1.0 / np.log2(i + 2) for i in range(min(len(recommendations), len(ground_truth))))
        
        return dcg / idcg if idcg > 0 else 0.0
    
    def _calculate_diversity(self, recommendations: List[Dict[str, Any]]) -> float:
        """Calculate diversity score of recommendations"""
        if len(recommendations) < 2:
            return 0.0
        
        # Extract categories or features for diversity calculation
        categories = []
        for rec in recommendations:
            category = rec.get('category', rec.get('type', 'unknown'))
            categories.append(category)
        
        # Calculate category diversity
        unique_categories = len(set(categories))
        max_possible_categories = len(categories)
        
        return unique_categories / max_possible_categories if max_possible_categories > 0 else 0.0
    
    def _calculate_novelty(self, recommendations: List[Dict[str, Any]], user_interactions: List[str]) -> float:
        """Calculate novelty score (how new the recommendations are to the user)"""
        if not recommendations:
            return 0.0
        
        rec_ids = [rec.get('id', '') for rec in recommendations]
        novel_items = len(set(rec_ids) - set(user_interactions))
        
        return novel_items / len(rec_ids) if rec_ids else 0.0
    
    def get_algorithm_comparison(
        self,
        algorithms: List[RecommendationAlgorithm],
        time_window: timedelta = timedelta(hours=24)
    ) -> Dict[str, Any]:
        """
        Compare performance of different algorithms
        
        Args:
            algorithms: List of algorithms to compare
            time_window: Time window for comparison
        
        Returns:
            Comparison results
        """
        cutoff_time = datetime.now() - time_window
        
        comparison = {}
        
        for algorithm in algorithms:
            # Filter metrics for this algorithm
            algorithm_metrics = [
                m for m in self.recommendation_metrics
                if m.algorithm == algorithm and m.timestamp >= cutoff_time
            ]
            
            if not algorithm_metrics:
                comparison[algorithm.value] = {'error': 'No data available'}
                continue
            
            # Calculate performance statistics
            processing_times = [m.processing_time for m in algorithm_metrics]
            quality_scores = []
            
            for metric in algorithm_metrics:
                if metric.quality_metrics:
                    avg_quality = statistics.mean(metric.quality_metrics.values())
                    quality_scores.append(avg_quality)
            
            comparison[algorithm.value] = {
                'total_requests': len(algorithm_metrics),
                'avg_processing_time': statistics.mean(processing_times),
                'p95_processing_time': statistics.quantiles(processing_times, n=20)[18] if len(processing_times) >= 20 else max(processing_times),
                'avg_quality_score': statistics.mean(quality_scores) if quality_scores else None,
                'error_rate': sum(m.error_count for m in algorithm_metrics) / len(algorithm_metrics),
                'cache_hit_rate': len([m for m in algorithm_metrics if m.cache_hit]) / len(algorithm_metrics)
            }
        
        return comparison
    
    def get_optimization_recommendations(
        self,
        algorithm: Optional[RecommendationAlgorithm] = None,
        time_window: timedelta = timedelta(hours=1)
    ) -> List[Dict[str, Any]]:
        """
        Get optimization recommendations for recommendation engine
        
        Args:
            algorithm: Specific algorithm to analyze
            time_window: Time window for analysis
        
        Returns:
            List of optimization recommendations
        """
        cutoff_time = datetime.now() - time_window
        
        # Filter recent metrics
        recent_metrics = [
            m for m in self.recommendation_metrics
            if (m.timestamp >= cutoff_time and
                (algorithm is None or m.algorithm == algorithm))
        ]
        
        if not recent_metrics:
            return []
        
        recommendations = []
        
        # Analyze processing time patterns
        processing_times = [m.processing_time for m in recent_metrics]
        avg_processing_time = statistics.mean(processing_times)
        
        if avg_processing_time > 1.0:  # More than 1 second
            recommendations.append({
                'type': 'performance_optimization',
                'priority': 'high',
                'description': f'Average processing time is {avg_processing_time:.2f}s',
                'suggestions': [
                    'Implement caching for user profiles and embeddings',
                    'Use approximate algorithms for real-time recommendations',
                    'Pre-compute recommendations for popular items',
                    'Implement asynchronous processing for non-critical requests'
                ],
                'expected_improvement': 'Up to 70% processing time reduction'
            })
        
        # Analyze quality metrics
        quality_issues = []
        for metric in recent_metrics:
            if metric.quality_metrics:
                for quality_type, score in metric.quality_metrics.items():
                    if score < self.quality_threshold:
                        quality_issues.append((quality_type, score))
        
        if quality_issues:
            avg_poor_quality = statistics.mean([score for _, score in quality_issues])
            recommendations.append({
                'type': 'quality_improvement',
                'priority': 'high',
                'description': f'Quality metrics below threshold: {avg_poor_quality:.2f}',
                'suggestions': [
                    'Retrain models with recent interaction data',
                    'Implement ensemble methods',
                    'Add more diverse features to models',
                    'Implement active learning for user feedback'
                ],
                'expected_improvement': f'{((self.quality_threshold - avg_poor_quality) * 100):.0f}% quality improvement'
            })
        
        # Analyze cache efficiency
        cache_hits = len([m for m in recent_metrics if m.cache_hit])
        cache_hit_rate = cache_hits / len(recent_metrics)
        
        if cache_hit_rate < 0.4:
            recommendations.append({
                'type': 'cache_optimization',
                'priority': 'medium',
                'description': f'Cache hit rate is {cache_hit_rate:.1%}',
                'suggestions': [
                    'Increase cache TTL for stable recommendations',
                    'Implement intelligent cache warming',
                    'Use distributed caching for better performance',
                    'Cache intermediate computation results'
                ],
                'expected_improvement': f'{((0.7 - cache_hit_rate) * 100):.0f}% cache efficiency improvement'
            })
        
        # Analyze diversity
        diversity_scores = [m.result.diversity_score for m in recent_metrics]
        avg_diversity = statistics.mean(diversity_scores)
        
        if avg_diversity < 0.5:
            recommendations.append({
                'type': 'diversity_improvement',
                'priority': 'medium',
                'description': f'Low recommendation diversity: {avg_diversity:.2f}',
                'suggestions': [
                    'Implement diversity-aware ranking',
                    'Use multi-objective optimization',
                    'Add category-based constraints',
                    'Implement topic diversification'
                ],
                'expected_improvement': 'Improved user engagement and satisfaction'
            })
        
        return recommendations
    
    def get_performance_summary(
        self,
        algorithm: Optional[RecommendationAlgorithm] = None,
        time_window: timedelta = timedelta(hours=1)
    ) -> Dict[str, Any]:
        """
        Get performance summary for recommendation engine
        
        Args:
            algorithm: Specific algorithm to analyze
            time_window: Time window for analysis
        
        Returns:
            Performance summary dictionary
        """
        cutoff_time = datetime.now() - time_window
        
        # Filter recent metrics
        recent_metrics = [
            m for m in self.recommendation_metrics
            if (m.timestamp >= cutoff_time and
                (algorithm is None or m.algorithm == algorithm))
        ]
        
        if not recent_metrics:
            return {'error': 'No metrics available'}
        
        # Calculate statistics
        processing_times = [m.processing_time for m in recent_metrics]
        quality_scores = []
        diversity_scores = [m.result.diversity_score for m in recent_metrics]
        
        for metric in recent_metrics:
            if metric.quality_metrics:
                avg_quality = statistics.mean(metric.quality_metrics.values())
                quality_scores.append(avg_quality)
        
        summary = {
            'time_window': str(time_window),
            'total_requests': len(recent_metrics),
            'algorithms_used': len(set(m.algorithm for m in recent_metrics)),
            'recommendation_types': len(set(m.recommendation_type for m in recent_metrics)),
            'performance_metrics': {
                'avg_processing_time': statistics.mean(processing_times),
                'p95_processing_time': statistics.quantiles(processing_times, n=20)[18] if len(processing_times) >= 20 else max(processing_times),
                'total_errors': sum(m.error_count for m in recent_metrics),
                'cache_hit_rate': (len([m for m in recent_metrics if m.cache_hit]) / len(recent_metrics)) * 100,
                'avg_diversity_score': statistics.mean(diversity_scores)
            }
        }
        
        if quality_scores:
            summary['performance_metrics'].update({
                'avg_quality_score': statistics.mean(quality_scores),
                'min_quality_score': min(quality_scores)
            })
        
        # A/B testing summary
        if self.enable_ab_testing:
            ab_groups = set(m.a_b_test_group for m in recent_metrics if m.a_b_test_group)
            summary['ab_testing'] = {
                'active_groups': len(ab_groups),
                'group_names': list(ab_groups)
            }
        
        # Recent bottlenecks
        recent_bottlenecks = [b for b in self.bottlenecks if b.timestamp >= cutoff_time]
        summary['bottlenecks'] = {
            'total_count': len(recent_bottlenecks),
            'by_severity': {
                severity: len([b for b in recent_bottlenecks if b.severity == severity])
                for severity in ['low', 'medium', 'high', 'critical']
            }
        }
        
        return summary


# Context manager for easy profiling
class RecommendationProfiler:
    """Context manager for recommendation engine profiling"""
    
    def __init__(
        self,
        profiler: RecommendationEngineProfiler,
        algorithm: RecommendationAlgorithm,
        recommendation_type: RecommendationType,
        user_profile: UserProfile,
        num_recommendations: int = 10,
        ab_test_group: Optional[str] = None
    ):
        self.profiler = profiler
        self.algorithm = algorithm
        self.recommendation_type = recommendation_type
        self.user_profile = user_profile
        self.num_recommendations = num_recommendations
        self.ab_test_group = ab_test_group
        self.session_id: Optional[str] = None
    
    def __enter__(self):
        self.session_id = self.profiler.start_recommendation_profiling(
            algorithm=self.algorithm,
            recommendation_type=self.recommendation_type,
            user_profile=self.user_profile,
            num_recommendations=self.num_recommendations,
            ab_test_group=self.ab_test_group
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        return None  # Session must be ended explicitly
    
    def mark_data_loading_start(self):
        if self.session_id:
            self.profiler.mark_data_loading_start(self.session_id)
    
    def mark_model_inference_start(self):
        if self.session_id:
            self.profiler.mark_model_inference_start(self.session_id)
    
    def mark_postprocessing_start(self):
        if self.session_id:
            self.profiler.mark_postprocessing_start(self.session_id)
    
    def record_cache_hit(self, cache_type: str):
        if self.session_id:
            self.profiler.record_cache_hit(self.session_id, cache_type)
    
    def end_profiling(self, result: RecommendationResult, **kwargs) -> RecommendationMetrics:
        if self.session_id:
            return self.profiler.end_recommendation_profiling(self.session_id, result, **kwargs)
        raise ValueError("Session not started")


# Factory function for creating profiler instances
def create_recommendation_engine_profiler(
    enable_quality_monitoring: bool = True,
    enable_ab_testing: bool = True,
    start_monitoring: bool = True
) -> RecommendationEngineProfiler:
    """
    Factory function to create and configure Recommendation Engine Profiler
    
    Args:
        enable_quality_monitoring: Enable quality metrics tracking
        enable_ab_testing: Enable A/B testing support
        start_monitoring: Start background monitoring immediately
    
    Returns:
        Configured RecommendationEngineProfiler instance
    """
    profiler = RecommendationEngineProfiler(
        enable_quality_monitoring=enable_quality_monitoring,
        enable_ab_testing=enable_ab_testing
    )
    
    if start_monitoring:
        profiler.start_monitoring()
    
    return profiler


if __name__ == "__main__":
    # Example usage
    
    # Create profiler
    profiler = create_recommendation_engine_profiler()
    
    # Create sample user profile
    user_profile = UserProfile(
        user_id="creator_123",
        content_preferences={"tech": 0.8, "gaming": 0.6, "music": 0.4},
        interaction_history=["item_1", "item_2", "item_3"],
        demographic_info={"age": 25, "location": "US"},
        behavioral_patterns={"engagement_rate": 0.7, "sharing_rate": 0.3},
        engagement_metrics={"avg_session_time": 300, "daily_active": True}
    )
    
    # Example: Profile collaborative filtering recommendation
    with RecommendationProfiler(
        profiler=profiler,
        algorithm=RecommendationAlgorithm.COLLABORATIVE_FILTERING,
        recommendation_type=RecommendationType.CREATOR_MATCHING,
        user_profile=user_profile,
        num_recommendations=10,
        ab_test_group="test_group_a"
    ) as session:
        
        # Simulate recommendation process
        session.mark_data_loading_start()
        time.sleep(0.1)  # Simulate data loading
        
        session.mark_model_inference_start()
        time.sleep(0.3)  # Simulate model inference
        
        session.mark_postprocessing_start()
        time.sleep(0.05)  # Simulate postprocessing
        
        # Create mock result
        result = RecommendationResult(
            recommendations=[
                {"id": "creator_456", "score": 0.9, "category": "tech"},
                {"id": "creator_789", "score": 0.8, "category": "gaming"}
            ],
            confidence_scores=[0.9, 0.8],
            relevance_scores=[0.85, 0.75],
            diversity_score=0.7,
            novelty_score=0.6
        )
        
        # Calculate quality metrics
        quality_metrics = profiler.calculate_quality_metrics(
            recommendations=result.recommendations,
            ground_truth=["creator_456", "creator_999"],
            user_interactions=user_profile.interaction_history
        )
        
        # End profiling
        metrics = session.end_profiling(
            result=result,
            quality_metrics=quality_metrics,
            business_metrics={"click_through_rate": 0.12, "conversion_rate": 0.03},
            num_candidates=1000
        )
    
    # Get performance summary
    summary = profiler.get_performance_summary()
    print("Performance Summary:", json.dumps(summary, indent=2, default=str))
    
    # Get optimization recommendations
    recommendations = profiler.get_optimization_recommendations()
    print("Optimization Recommendations:", json.dumps(recommendations, indent=2))
    
    # Stop monitoring
    profiler.stop_monitoring()