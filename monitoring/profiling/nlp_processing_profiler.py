"""⚡ NLP Processing Performance Profiler
======================================

Advanced profiling system for NLP and SEO processing in the Creator Economy platform.
Provides real-time monitoring of text analysis, sentiment analysis, keyword extraction, and SEO optimization.

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
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import statistics
from collections import defaultdict, deque
import gc
import re

from prometheus_client import Counter, Gauge, Histogram, Summary

logger = logging.getLogger(__name__)


class NLPOperation(Enum):
    """NLP processing operations"""
    
    TOKENIZATION = "tokenization"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    KEYWORD_EXTRACTION = "keyword_extraction"
    NAMED_ENTITY_RECOGNITION = "named_entity_recognition"
    LANGUAGE_DETECTION = "language_detection"
    TEXT_CLASSIFICATION = "text_classification"
    TOPIC_MODELING = "topic_modeling"
    TEXT_SUMMARIZATION = "text_summarization"
    SEMANTIC_SIMILARITY = "semantic_similarity"
    CONTENT_SCORING = "content_scoring"
    SEO_ANALYSIS = "seo_analysis"
    READABILITY_ANALYSIS = "readability_analysis"
    TRANSLATION = "translation"
    SPELL_CHECK = "spell_check"
    GRAMMAR_CHECK = "grammar_check"


class TextComplexity(Enum):
    """Text complexity levels"""
    
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    HIGHLY_COMPLEX = "highly_complex"


class AnalysisQuality(Enum):
    """Analysis quality levels"""
    
    FAST = "fast"
    BALANCED = "balanced"
    ACCURATE = "accurate"
    COMPREHENSIVE = "comprehensive"


@dataclass
class TextMetadata:
    """Text content metadata"""
    
    text_length: int  # characters
    word_count: int
    sentence_count: int
    paragraph_count: int
    language: Optional[str] = None
    encoding: str = "utf-8"
    complexity: Optional[TextComplexity] = None
    readability_score: Optional[float] = None
    keyword_density: Optional[Dict[str, float]] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class SEOMetrics:
    """SEO analysis metrics"""
    
    title_optimization_score: float  # 0-100
    meta_description_score: float  # 0-100
    header_structure_score: float  # 0-100
    keyword_optimization_score: float  # 0-100
    content_quality_score: float  # 0-100
    internal_links_score: float  # 0-100
    readability_score: float  # 0-100
    overall_seo_score: float  # 0-100
    target_keywords: List[str] = field(default_factory=list)
    suggested_keywords: List[str] = field(default_factory=list)
    content_length_recommendation: Optional[str] = None
    optimization_suggestions: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class NLPProcessingMetrics:
    """NLP processing performance metrics"""
    
    operation: NLPOperation
    text_metadata: TextMetadata
    processing_time: float  # seconds
    accuracy_score: Optional[float] = None  # 0-100
    confidence_score: Optional[float] = None  # 0-100
    memory_usage: int = 0  # MB
    cpu_usage: float = 0.0  # percentage
    model_name: Optional[str] = None
    model_version: Optional[str] = None
    analysis_quality: AnalysisQuality = AnalysisQuality.BALANCED
    preprocessing_time: float = 0.0
    inference_time: float = 0.0
    postprocessing_time: float = 0.0
    tokens_processed: int = 0
    throughput: float = 0.0  # tokens/second
    cache_hit: bool = False
    error_count: int = 0
    warnings: List[str] = field(default_factory=list)
    seo_metrics: Optional[SEOMetrics] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        # Calculate throughput
        if self.processing_time > 0 and self.tokens_processed > 0:
            self.throughput = self.tokens_processed / self.processing_time


@dataclass
class NLPBottleneck:
    """NLP processing bottleneck detection"""
    
    bottleneck_type: str
    severity: str  # low, medium, high, critical
    description: str
    affected_operation: NLPOperation
    performance_impact: float  # percentage
    optimization_suggestions: List[str]
    model_recommendations: List[str]
    timestamp: datetime = field(default_factory=datetime.now)


class NLPProcessingProfiler:
    """
    Advanced NLP Processing Performance Profiler
    
    Provides comprehensive profiling for NLP operations with focus on:
    - Text analysis performance monitoring
    - SEO optimization tracking
    - Model inference profiling
    - Language processing efficiency
    - Content quality assessment
    """
    
    def __init__(
        self,
        enable_model_monitoring: bool = True,
        enable_cache_monitoring: bool = True,
        sampling_interval: float = 0.1,
        max_history_size: int = 10000,
        cache_ttl: int = 3600  # Cache TTL in seconds
    ):
        """
        Initialize NLP Processing Profiler
        
        Args:
            enable_model_monitoring: Enable ML model performance monitoring
            enable_cache_monitoring: Enable cache hit/miss tracking
            sampling_interval: Metrics collection interval in seconds
            max_history_size: Maximum number of metrics to keep
            cache_ttl: Cache time-to-live in seconds
        """
        self.enable_model_monitoring = enable_model_monitoring
        self.enable_cache_monitoring = enable_cache_monitoring
        self.sampling_interval = sampling_interval
        self.max_history_size = max_history_size
        self.cache_ttl = cache_ttl
        
        # Metrics storage
        self.processing_metrics: deque = deque(maxlen=max_history_size)
        self.bottlenecks: deque = deque(maxlen=max_history_size)
        
        # Active processing sessions
        self.active_sessions: Dict[str, Dict] = {}
        self.session_lock = threading.Lock()
        
        # Model performance tracking
        self.model_performance: Dict[str, List[float]] = defaultdict(list)
        
        # Cache for processed results
        self.result_cache: Dict[str, Any] = {}
        self.cache_timestamps: Dict[str, datetime] = {}
        
        # Available NLP libraries
        self.available_libraries = self._check_nlp_libraries()
        
        # Prometheus metrics
        self._setup_prometheus_metrics()
        
        # Background monitoring
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        
        logger.info("NLPProcessingProfiler initialized with libraries: %s",
                   ', '.join(self.available_libraries.keys()))
    
    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics for monitoring"""
        
        self.processing_time_histogram = Histogram(
            'nlp_processing_time_seconds',
            'NLP processing time',
            ['operation', 'quality', 'model']
        )
        
        self.throughput_gauge = Gauge(
            'nlp_throughput_tokens_per_second',
            'NLP processing throughput in tokens per second',
            ['operation']
        )
        
        self.accuracy_gauge = Gauge(
            'nlp_accuracy_score',
            'NLP processing accuracy score',
            ['operation', 'model']
        )
        
        self.cache_hit_rate_gauge = Gauge(
            'nlp_cache_hit_rate',
            'NLP cache hit rate percentage',
            ['operation']
        )
        
        self.seo_score_gauge = Gauge(
            'nlp_seo_score',
            'SEO optimization score',
            ['metric_type']
        )
        
        self.bottleneck_counter = Counter(
            'nlp_bottlenecks_total',
            'Total NLP processing bottlenecks',
            ['bottleneck_type', 'severity']
        )
        
        self.error_counter = Counter(
            'nlp_errors_total',
            'Total NLP processing errors',
            ['operation']
        )
    
    def _check_nlp_libraries(self) -> Dict[str, bool]:
        """Check availability of NLP libraries"""
        libraries = {}
        
        # Check spaCy
        try:
            import spacy
            libraries['spacy'] = True
        except ImportError:
            libraries['spacy'] = False
        
        # Check NLTK
        try:
            import nltk
            libraries['nltk'] = True
        except ImportError:
            libraries['nltk'] = False
        
        # Check transformers
        try:
            # import transformers
            libraries['transformers'] = True
        except ImportError:
            libraries['transformers'] = False
        
        # Check textblob
        try:
            import textblob
            libraries['textblob'] = True
        except ImportError:
            libraries['textblob'] = False
        
        # Check langdetect
        try:
            import langdetect
            libraries['langdetect'] = True
        except ImportError:
            libraries['langdetect'] = False
        
        return libraries
    
    def _extract_text_metadata(self, text: str) -> TextMetadata:
        """Extract metadata from text content"""
        try:
            # Basic text statistics
            text_length = len(text)
            words = text.split()
            word_count = len(words)
            sentences = re.split(r'[.!?]+', text)
            sentence_count = len([s for s in sentences if s.strip()])
            paragraphs = text.split('\n\n')
            paragraph_count = len([p for p in paragraphs if p.strip()])
            
            # Determine text complexity
            complexity = self._assess_text_complexity(text, word_count, sentence_count)
            
            # Calculate basic readability score
            readability_score = self._calculate_readability_score(text, word_count, sentence_count)
            
            # Detect language if possible
            language = self._detect_language(text)
            
            # Extract keyword density
            keyword_density = self._calculate_keyword_density(text, words)
            
            return TextMetadata(
                text_length=text_length,
                word_count=word_count,
                sentence_count=sentence_count,
                paragraph_count=paragraph_count,
                language=language,
                complexity=complexity,
                readability_score=readability_score,
                keyword_density=keyword_density
            )
            
        except Exception as e:
            logger.error("Error extracting text metadata: %s", e)
            return TextMetadata(
                text_length=len(text),
                word_count=len(text.split()),
                sentence_count=1,
                paragraph_count=1
            )
    
    def _assess_text_complexity(self, text: str, word_count: int, sentence_count: int) -> TextComplexity:
        """Assess text complexity level"""
        if sentence_count == 0:
            return TextComplexity.SIMPLE
        
        avg_words_per_sentence = word_count / sentence_count
        
        # Count complex words (3+ syllables)
        complex_word_count = 0
        for word in text.split():
            syllables = self._count_syllables(word)
            if syllables >= 3:
                complex_word_count += 1
        
        complex_word_ratio = complex_word_count / word_count if word_count > 0 else 0
        
        # Determine complexity
        if avg_words_per_sentence < 15 and complex_word_ratio < 0.1:
            return TextComplexity.SIMPLE
        elif avg_words_per_sentence < 20 and complex_word_ratio < 0.15:
            return TextComplexity.MODERATE
        elif avg_words_per_sentence < 25 and complex_word_ratio < 0.25:
            return TextComplexity.COMPLEX
        else:
            return TextComplexity.HIGHLY_COMPLEX
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified)"""
        word = word.lower()
        vowels = 'aeiouy'
        syllable_count = 0
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel
        
        # Handle silent 'e'
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1
        
        return max(1, syllable_count)
    
    def _calculate_readability_score(self, text: str, word_count: int, sentence_count: int) -> float:
        """Calculate Flesch Reading Ease score"""
        if sentence_count == 0 or word_count == 0:
            return 0.0
        
        # Count syllables
        total_syllables = sum(self._count_syllables(word) for word in text.split())
        
        # Flesch Reading Ease formula
        score = 206.835 - (1.015 * (word_count / sentence_count)) - (84.6 * (total_syllables / word_count))
        return max(0, min(100, score))
    
    def _detect_language(self, text: str) -> Optional[str]:
        """Detect text language"""
        if not self.available_libraries.get('langdetect', False):
            return None
        
        try:
            from langdetect import detect
            return detect(text)
        except:
            return None
    
    def _calculate_keyword_density(self, text: str, words: List[str]) -> Dict[str, float]:
        """Calculate keyword density"""
        if not words:
            return {}
        
        # Count word frequencies
        word_freq = defaultdict(int)
        total_words = len(words)
        
        for word in words:
            # Clean and normalize word
            cleaned_word = re.sub(r'[^\w]', '', word.lower())
            if len(cleaned_word) > 2:  # Ignore short words
                word_freq[cleaned_word] += 1
        
        # Calculate density for top words
        keyword_density = {}
        for word, count in sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20]:
            keyword_density[word] = (count / total_words) * 100
        
        return keyword_density
    
    def _generate_cache_key(self, operation: NLPOperation, text: str, **kwargs) -> str:
        """Generate cache key for operation"""
        import hashlib
        
        # Create a hash of the operation, text, and parameters
        content = f"{operation.value}_{text}_{str(sorted(kwargs.items()))}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _check_cache(self, cache_key: str) -> Optional[Any]:
        """Check if result is in cache"""
        if not self.enable_cache_monitoring:
            return None
        
        if cache_key in self.result_cache:
            timestamp = self.cache_timestamps.get(cache_key)
            if timestamp and (datetime.now() - timestamp).seconds < self.cache_ttl:
                return self.result_cache[cache_key]
            else:
                # Remove expired cache entry
                self.result_cache.pop(cache_key, None)
                self.cache_timestamps.pop(cache_key, None)
        
        return None
    
    def _store_cache(self, cache_key: str, result: Any):
        """Store result in cache"""
        if self.enable_cache_monitoring:
            self.result_cache[cache_key] = result
            self.cache_timestamps[cache_key] = datetime.now()
            
            # Clean old cache entries if needed
            if len(self.result_cache) > 1000:
                self._clean_cache()
    
    def _clean_cache(self):
        """Clean expired cache entries"""
        current_time = datetime.now()
        expired_keys = [
            key for key, timestamp in self.cache_timestamps.items()
            if (current_time - timestamp).seconds >= self.cache_ttl
        ]
        
        for key in expired_keys:
            self.result_cache.pop(key, None)
            self.cache_timestamps.pop(key, None)
    
    def start_monitoring(self):
        """Start background monitoring thread"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        logger.info("NLP processing background monitoring started")
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5.0)
        logger.info("NLP processing background monitoring stopped")
    
    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.monitoring_active:
            try:
                # Clean cache periodically
                self._clean_cache()
                
                # Analyze for bottlenecks
                self._detect_bottlenecks()
                
                # Update cache hit rate metrics
                self._update_cache_metrics()
                
                time.sleep(self.sampling_interval)
                
            except Exception as e:
                logger.error("Error in NLP monitoring loop: %s", e)
                time.sleep(1.0)
    
    def start_nlp_profiling(
        self,
        operation: NLPOperation,
        text: str,
        analysis_quality: AnalysisQuality = AnalysisQuality.BALANCED,
        model_name: Optional[str] = None,
        session_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Start profiling an NLP processing operation
        
        Args:
            operation: Type of NLP operation
            text: Text content to process
            analysis_quality: Quality level for analysis
            model_name: Name of the model being used
            session_id: Optional session identifier
            **kwargs: Additional parameters for the operation
        
        Returns:
            session_id: Unique identifier for this profiling session
        """
        if session_id is None:
            session_id = f"{operation.value}_{int(time.time() * 1000)}"
        
        # Extract text metadata
        text_metadata = self._extract_text_metadata(text)
        
        # Check cache
        cache_key = self._generate_cache_key(operation, text, **kwargs)
        cached_result = self._check_cache(cache_key)
        
        session_data = {
            'operation': operation,
            'text': text,
            'text_metadata': text_metadata,
            'analysis_quality': analysis_quality,
            'model_name': model_name,
            'cache_key': cache_key,
            'cached_result': cached_result,
            'start_time': time.time(),
            'preprocessing_start': None,
            'inference_start': None,
            'postprocessing_start': None,
            'error_count': 0,
            'warnings': [],
            'kwargs': kwargs
        }
        
        with self.session_lock:
            self.active_sessions[session_id] = session_data
        
        logger.debug("Started NLP profiling session: %s", session_id)
        return session_id
    
    def mark_preprocessing_start(self, session_id: str):
        """Mark the start of preprocessing phase"""
        with self.session_lock:
            if session_id in self.active_sessions:
                self.active_sessions[session_id]['preprocessing_start'] = time.time()
    
    def mark_inference_start(self, session_id: str):
        """Mark the start of inference phase"""
        with self.session_lock:
            if session_id in self.active_sessions:
                self.active_sessions[session_id]['inference_start'] = time.time()
    
    def mark_postprocessing_start(self, session_id: str):
        """Mark the start of postprocessing phase"""
        with self.session_lock:
            if session_id in self.active_sessions:
                self.active_sessions[session_id]['postprocessing_start'] = time.time()
    
    def add_warning(self, session_id: str, warning: str):
        """Add a warning to the processing session"""
        with self.session_lock:
            if session_id in self.active_sessions:
                self.active_sessions[session_id]['warnings'].append(warning)
    
    def increment_error_count(self, session_id: str):
        """Increment error count for the session"""
        with self.session_lock:
            if session_id in self.active_sessions:
                self.active_sessions[session_id]['error_count'] += 1
    
    def end_nlp_profiling(
        self,
        session_id: str,
        result: Optional[Any] = None,
        accuracy_score: Optional[float] = None,
        confidence_score: Optional[float] = None,
        tokens_processed: Optional[int] = None,
        seo_metrics: Optional[SEOMetrics] = None
    ) -> NLPProcessingMetrics:
        """
        End profiling session and return metrics
        
        Args:
            session_id: Session identifier
            result: Processing result to cache
            accuracy_score: Accuracy assessment (0-100)
            confidence_score: Confidence in result (0-100)
            tokens_processed: Number of tokens processed
            seo_metrics: SEO analysis metrics if applicable
        
        Returns:
            NLPProcessingMetrics: Complete processing metrics
        """
        with self.session_lock:
            if session_id not in self.active_sessions:
                raise ValueError(f"Session {session_id} not found")
            
            session_data = self.active_sessions.pop(session_id)
        
        end_time = time.time()
        total_time = end_time - session_data['start_time']
        
        # Calculate phase timings
        preprocessing_time = 0.0
        inference_time = 0.0
        postprocessing_time = 0.0
        
        if session_data['preprocessing_start']:
            if session_data['inference_start']:
                preprocessing_time = session_data['inference_start'] - session_data['preprocessing_start']
            else:
                preprocessing_time = end_time - session_data['preprocessing_start']
        
        if session_data['inference_start']:
            if session_data['postprocessing_start']:
                inference_time = session_data['postprocessing_start'] - session_data['inference_start']
            else:
                inference_time = end_time - session_data['inference_start']
        
        if session_data['postprocessing_start']:
            postprocessing_time = end_time - session_data['postprocessing_start']
        
        # Determine if result was from cache
        cache_hit = session_data['cached_result'] is not None
        
        # Store result in cache if not from cache
        if not cache_hit and result is not None:
            self._store_cache(session_data['cache_key'], result)
        
        # Estimate tokens processed if not provided
        if tokens_processed is None:
            tokens_processed = session_data['text_metadata'].word_count
        
        # Create metrics object
        metrics = NLPProcessingMetrics(
            operation=session_data['operation'],
            text_metadata=session_data['text_metadata'],
            processing_time=total_time,
            accuracy_score=accuracy_score,
            confidence_score=confidence_score,
            model_name=session_data['model_name'],
            analysis_quality=session_data['analysis_quality'],
            preprocessing_time=preprocessing_time,
            inference_time=inference_time,
            postprocessing_time=postprocessing_time,
            tokens_processed=tokens_processed,
            cache_hit=cache_hit,
            error_count=session_data['error_count'],
            warnings=session_data['warnings'],
            seo_metrics=seo_metrics
        )
        
        # Store metrics
        self.processing_metrics.append(metrics)
        
        # Track model performance
        if self.enable_model_monitoring and session_data['model_name']:
            self.model_performance[session_data['model_name']].append(total_time)
            # Keep only recent measurements
            if len(self.model_performance[session_data['model_name']]) > 100:
                self.model_performance[session_data['model_name']] = \
                    self.model_performance[session_data['model_name']][-100:]
        
        # Update Prometheus metrics
        self.processing_time_histogram.labels(
            operation=metrics.operation.value,
            quality=metrics.analysis_quality.value,
            model=metrics.model_name or 'unknown'
        ).observe(metrics.processing_time)
        
        self.throughput_gauge.labels(
            operation=metrics.operation.value
        ).set(metrics.throughput)
        
        if metrics.accuracy_score is not None:
            self.accuracy_gauge.labels(
                operation=metrics.operation.value,
                model=metrics.model_name or 'unknown'
            ).set(metrics.accuracy_score)
        
        if metrics.error_count > 0:
            self.error_counter.labels(
                operation=metrics.operation.value
            ).inc(metrics.error_count)
        
        # Update SEO metrics if available
        if seo_metrics:
            self.seo_score_gauge.labels(metric_type='overall').set(seo_metrics.overall_seo_score)
            self.seo_score_gauge.labels(metric_type='title').set(seo_metrics.title_optimization_score)
            self.seo_score_gauge.labels(metric_type='content_quality').set(seo_metrics.content_quality_score)
            self.seo_score_gauge.labels(metric_type='keyword').set(seo_metrics.keyword_optimization_score)
        
        logger.info("NLP profiling completed for %s: %.3fs, %.1f tokens/sec, cache_hit: %s",
                   metrics.operation.value, metrics.processing_time, metrics.throughput, cache_hit)
        
        return metrics
    
    def _update_cache_metrics(self):
        """Update cache hit rate metrics"""
        if not self.processing_metrics:
            return
        
        # Calculate cache hit rates per operation
        operation_stats = defaultdict(lambda: {'hits': 0, 'total': 0})
        
        recent_metrics = list(self.processing_metrics)[-100:]  # Last 100 operations
        
        for metric in recent_metrics:
            operation_stats[metric.operation]['total'] += 1
            if metric.cache_hit:
                operation_stats[metric.operation]['hits'] += 1
        
        # Update Prometheus metrics
        for operation, stats in operation_stats.items():
            hit_rate = (stats['hits'] / stats['total']) * 100 if stats['total'] > 0 else 0
            self.cache_hit_rate_gauge.labels(operation=operation.value).set(hit_rate)
    
    def _detect_bottlenecks(self):
        """Detect performance bottlenecks in NLP processing"""
        if len(self.processing_metrics) < 3:
            return
        
        recent_metrics = list(self.processing_metrics)[-20:]  # Last 20 operations
        
        # Analyze processing times by operation
        operation_times = defaultdict(list)
        for metric in recent_metrics:
            operation_times[metric.operation].append(metric.processing_time)
        
        for operation, times in operation_times.items():
            if len(times) < 2:
                continue
            
            avg_time = statistics.mean(times)
            
            # Check for slow processing
            if avg_time > 5.0:  # 5 seconds threshold
                bottleneck = NLPBottleneck(
                    bottleneck_type="slow_processing",
                    severity="high" if avg_time > 10.0 else "medium",
                    description=f"Average {operation.value} time is {avg_time:.2f}s",
                    affected_operation=operation,
                    performance_impact=min(100, (avg_time / 1.0) * 10),
                    optimization_suggestions=[
                        "Use faster models for real-time processing",
                        "Implement text chunking for large documents",
                        "Enable result caching",
                        "Use GPU acceleration if available"
                    ],
                    model_recommendations=[
                        "Switch to lightweight models for speed",
                        "Use distilled models",
                        "Implement model quantization",
                        "Consider edge-optimized models"
                    ]
                )
                self._record_bottleneck(bottleneck)
        
        # Check cache efficiency
        cache_hit_metrics = [m for m in recent_metrics if m.cache_hit]
        cache_hit_rate = len(cache_hit_metrics) / len(recent_metrics) if recent_metrics else 0
        
        if cache_hit_rate < 0.3:  # Less than 30% cache hit rate
            bottleneck = NLPBottleneck(
                bottleneck_type="low_cache_efficiency",
                severity="medium",
                description=f"Cache hit rate is only {cache_hit_rate:.1%}",
                affected_operation=NLPOperation.TEXT_CLASSIFICATION,  # Generic
                performance_impact=(1 - cache_hit_rate) * 50,
                optimization_suggestions=[
                    "Increase cache TTL",
                    "Improve cache key generation",
                    "Pre-populate cache with common queries",
                    "Implement intelligent cache warming"
                ],
                model_recommendations=[
                    "Use consistent model versions",
                    "Implement result normalization",
                    "Cache intermediate processing steps"
                ]
            )
            self._record_bottleneck(bottleneck)
        
        # Check model accuracy consistency
        if self.enable_model_monitoring:
            for model_name, performance_history in self.model_performance.items():
                if len(performance_history) >= 10:
                    recent_performance = performance_history[-10:]
                    
                    # Check for performance degradation
                    first_half = recent_performance[:5]
                    second_half = recent_performance[5:]
                    
                    if statistics.mean(second_half) > statistics.mean(first_half) * 1.5:
                        bottleneck = NLPBottleneck(
                            bottleneck_type="model_performance_degradation",
                            severity="high",
                            description=f"Model {model_name} performance degraded by 50%",
                            affected_operation=NLPOperation.TEXT_CLASSIFICATION,
                            performance_impact=50,
                            optimization_suggestions=[
                                "Restart model service",
                                "Check model health",
                                "Monitor resource usage",
                                "Implement model fallback"
                            ],
                            model_recommendations=[
                                "Update model to latest version",
                                "Retrain model with recent data",
                                "Check for model corruption",
                                "Implement A/B testing"
                            ]
                        )
                        self._record_bottleneck(bottleneck)
    
    def _record_bottleneck(self, bottleneck: NLPBottleneck):
        """Record a detected bottleneck"""
        self.bottlenecks.append(bottleneck)
        
        # Update Prometheus counter
        self.bottleneck_counter.labels(
            bottleneck_type=bottleneck.bottleneck_type,
            severity=bottleneck.severity
        ).inc()
        
        logger.warning("NLP processing bottleneck detected: %s (%s severity)",
                      bottleneck.description, bottleneck.severity)
    
    def analyze_seo(
        self,
        title: str,
        content: str,
        meta_description: Optional[str] = None,
        target_keywords: Optional[List[str]] = None,
        url: Optional[str] = None
    ) -> SEOMetrics:
        """
        Perform comprehensive SEO analysis
        
        Args:
            title: Page/content title
            content: Main content text
            meta_description: Meta description
            target_keywords: Target keywords for optimization
            url: URL for additional analysis
        
        Returns:
            SEOMetrics: Comprehensive SEO analysis results
        """
        target_keywords = target_keywords or []
        
        # Analyze title optimization
        title_score = self._analyze_title_seo(title, target_keywords)
        
        # Analyze meta description
        meta_score = self._analyze_meta_description(meta_description, target_keywords)
        
        # Analyze content structure
        header_score = self._analyze_header_structure(content)
        
        # Analyze keyword optimization
        keyword_score = self._analyze_keyword_optimization(content, target_keywords)
        
        # Analyze content quality
        content_score = self._analyze_content_quality(content)
        
        # Analyze internal links (simplified)
        links_score = self._analyze_internal_links(content)
        
        # Calculate readability
        text_metadata = self._extract_text_metadata(content)
        readability_score = text_metadata.readability_score or 0
        
        # Generate keyword suggestions
        suggested_keywords = self._generate_keyword_suggestions(content)
        
        # Calculate overall score
        scores = [title_score, meta_score, header_score, keyword_score, 
                 content_score, links_score, readability_score]
        overall_score = statistics.mean(scores)
        
        # Generate optimization suggestions
        optimization_suggestions = self._generate_seo_suggestions(
            title_score, meta_score, header_score, keyword_score,
            content_score, links_score, readability_score
        )
        
        # Content length recommendation
        content_length_rec = self._get_content_length_recommendation(len(content))
        
        return SEOMetrics(
            title_optimization_score=title_score,
            meta_description_score=meta_score,
            header_structure_score=header_score,
            keyword_optimization_score=keyword_score,
            content_quality_score=content_score,
            internal_links_score=links_score,
            readability_score=readability_score,
            overall_seo_score=overall_score,
            target_keywords=target_keywords,
            suggested_keywords=suggested_keywords,
            content_length_recommendation=content_length_rec,
            optimization_suggestions=optimization_suggestions
        )
    
    def _analyze_title_seo(self, title: str, target_keywords: List[str]) -> float:
        """Analyze title SEO optimization"""
        if not title:
            return 0.0
        
        score = 0.0
        
        # Length check (50-60 characters is optimal)
        title_length = len(title)
        if 50 <= title_length <= 60:
            score += 30
        elif 30 <= title_length <= 70:
            score += 20
        else:
            score += 10
        
        # Keyword presence
        title_lower = title.lower()
        keywords_found = sum(1 for kw in target_keywords if kw.lower() in title_lower)
        if target_keywords:
            score += (keywords_found / len(target_keywords)) * 40
        else:
            score += 20  # No keywords to check
        
        # Keyword position (earlier is better)
        if target_keywords:
            for keyword in target_keywords:
                pos = title_lower.find(keyword.lower())
                if pos == 0:
                    score += 15
                elif pos > 0 and pos < len(title) // 2:
                    score += 10
                elif pos > 0:
                    score += 5
        
        # Readability and engagement
        if any(char in title for char in '?!'):
            score += 5
        if title.count('|') == 1 or title.count('-') == 1:
            score += 5
        
        return min(100, score)
    
    def _analyze_meta_description(self, meta_description: Optional[str], target_keywords: List[str]) -> float:
        """Analyze meta description SEO optimization"""
        if not meta_description:
            return 0.0
        
        score = 0.0
        
        # Length check (150-160 characters is optimal)
        desc_length = len(meta_description)
        if 150 <= desc_length <= 160:
            score += 40
        elif 120 <= desc_length <= 170:
            score += 30
        else:
            score += 15
        
        # Keyword presence
        desc_lower = meta_description.lower()
        keywords_found = sum(1 for kw in target_keywords if kw.lower() in desc_lower)
        if target_keywords:
            score += (keywords_found / len(target_keywords)) * 40
        else:
            score += 20
        
        # Call-to-action presence
        cta_words = ['click', 'learn', 'discover', 'find', 'get', 'read', 'see', 'watch']
        if any(word in desc_lower for word in cta_words):
            score += 20
        
        return min(100, score)
    
    def _analyze_header_structure(self, content: str) -> float:
        """Analyze header structure (H1, H2, etc.)"""
        score = 0.0
        
        # Look for header patterns
        h1_count = len(re.findall(r'#\s+', content))  # Markdown H1
        h2_count = len(re.findall(r'##\s+', content))  # Markdown H2
        h3_count = len(re.findall(r'###\s+', content))  # Markdown H3
        
        # Also check HTML headers
        h1_count += len(re.findall(r'<h1[^>]*>', content, re.IGNORECASE))
        h2_count += len(re.findall(r'<h2[^>]*>', content, re.IGNORECASE))
        h3_count += len(re.findall(r'<h3[^>]*>', content, re.IGNORECASE))
        
        # H1 presence and uniqueness
        if h1_count == 1:
            score += 30
        elif h1_count > 1:
            score += 10  # Multiple H1s are not ideal
        
        # H2 structure
        if h2_count >= 1:
            score += 25
            if h2_count >= 3:
                score += 15
        
        # H3 structure
        if h3_count >= 1:
            score += 20
        
        # Logical hierarchy
        if h1_count >= 1 and h2_count >= 1:
            score += 10
        
        return min(100, score)
    
    def _analyze_keyword_optimization(self, content: str, target_keywords: List[str]) -> float:
        """Analyze keyword optimization in content"""
        if not target_keywords:
            return 50.0  # Neutral score if no keywords specified
        
        content_lower = content.lower()
        words = content_lower.split()
        total_words = len(words)
        
        if total_words == 0:
            return 0.0
        
        score = 0.0
        
        for keyword in target_keywords:
            keyword_lower = keyword.lower()
            
            # Keyword presence
            if keyword_lower in content_lower:
                score += 20
                
                # Keyword density (1-3% is optimal)
                keyword_count = content_lower.count(keyword_lower)
                density = (keyword_count / total_words) * 100
                
                if 1 <= density <= 3:
                    score += 15
                elif 0.5 <= density <= 5:
                    score += 10
                else:
                    score += 5
                
                # Keyword distribution
                first_100_words = ' '.join(words[:100])
                last_100_words = ' '.join(words[-100:])
                
                if keyword_lower in first_100_words:
                    score += 10
                if keyword_lower in last_100_words:
                    score += 5
        
        # Average score across keywords
        return min(100, score / len(target_keywords))
    
    def _analyze_content_quality(self, content: str) -> float:
        """Analyze content quality metrics"""
        score = 0.0
        
        # Content length
        word_count = len(content.split())
        if word_count >= 1000:
            score += 30
        elif word_count >= 500:
            score += 20
        elif word_count >= 300:
            score += 15
        else:
            score += 5
        
        # Readability
        readability = self._calculate_readability_score(content, word_count, len(re.split(r'[.!?]+', content)))
        if readability >= 70:
            score += 25
        elif readability >= 50:
            score += 20
        elif readability >= 30:
            score += 15
        else:
            score += 10
        
        # Content structure
        paragraphs = len(content.split('\n\n'))
        if paragraphs >= 3:
            score += 15
        
        # Unique content indicators
        sentences = re.split(r'[.!?]+', content)
        unique_sentences = len(set(s.strip() for s in sentences if s.strip()))
        if unique_sentences / len(sentences) > 0.9:
            score += 15
        
        # Media indicators (simplified)
        if 'image' in content.lower() or 'video' in content.lower() or 'img' in content:
            score += 15
        
        return min(100, score)
    
    def _analyze_internal_links(self, content: str) -> float:
        """Analyze internal links (simplified)"""
        score = 0.0
        
        # Look for link patterns
        link_count = len(re.findall(r'\[([^\]]+)\]\([^)]+\)', content))  # Markdown links
        link_count += len(re.findall(r'<a[^>]+href[^>]*>', content, re.IGNORECASE))  # HTML links
        
        word_count = len(content.split())
        
        if word_count > 0:
            link_ratio = link_count / (word_count / 100)  # Links per 100 words
            
            if 1 <= link_ratio <= 3:
                score += 50
            elif 0.5 <= link_ratio <= 5:
                score += 30
            elif link_ratio > 0:
                score += 20
            else:
                score += 10
        
        # Anchor text diversity (simplified)
        if link_count > 0:
            score += 30
        
        # Internal vs external (simplified assumption)
        score += 20
        
        return min(100, score)
    
    def _generate_keyword_suggestions(self, content: str) -> List[str]:
        """Generate keyword suggestions based on content"""
        words = re.findall(r'\b\w{3,}\b', content.lower())
        
        # Count word frequencies
        word_freq = defaultdict(int)
        for word in words:
            if len(word) > 3 and word.isalpha():
                word_freq[word] += 1
        
        # Get top words as suggestions
        suggestions = [word for word, count in sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]]
        
        return suggestions
    
    def _generate_seo_suggestions(self, title_score: float, meta_score: float, header_score: float,
                                keyword_score: float, content_score: float, links_score: float,
                                readability_score: float) -> List[str]:
        """Generate SEO optimization suggestions"""
        suggestions = []
        
        if title_score < 70:
            suggestions.append("Optimize title length (50-60 characters) and include target keywords")
        
        if meta_score < 70:
            suggestions.append("Improve meta description with target keywords and call-to-action")
        
        if header_score < 70:
            suggestions.append("Add proper header structure (H1, H2, H3) for better content organization")
        
        if keyword_score < 70:
            suggestions.append("Improve keyword density and distribution throughout content")
        
        if content_score < 70:
            suggestions.append("Increase content length and improve readability")
        
        if links_score < 70:
            suggestions.append("Add relevant internal links with descriptive anchor text")
        
        if readability_score < 50:
            suggestions.append("Improve content readability with shorter sentences and simpler words")
        
        return suggestions
    
    def _get_content_length_recommendation(self, content_length: int) -> str:
        """Get content length recommendation"""
        if content_length < 1000:
            return "Consider expanding content to at least 1000 characters for better SEO"
        elif content_length < 2000:
            return "Good content length, consider adding more value-driven information"
        else:
            return "Excellent content length for SEO"
    
    def get_optimization_recommendations(
        self,
        operation: Optional[NLPOperation] = None,
        time_window: timedelta = timedelta(hours=1)
    ) -> List[Dict[str, Any]]:
        """
        Get NLP processing optimization recommendations
        
        Args:
            operation: Specific operation to analyze
            time_window: Time window for analysis
        
        Returns:
            List of optimization recommendations
        """
        cutoff_time = datetime.now() - time_window
        
        # Filter recent metrics
        recent_metrics = [
            m for m in self.processing_metrics
            if (m.timestamp >= cutoff_time and
                (operation is None or m.operation == operation))
        ]
        
        if not recent_metrics:
            return []
        
        recommendations = []
        
        # Analyze cache efficiency
        cache_hits = len([m for m in recent_metrics if m.cache_hit])
        cache_hit_rate = cache_hits / len(recent_metrics)
        
        if cache_hit_rate < 0.5:
            recommendations.append({
                'type': 'cache_optimization',
                'priority': 'high',
                'description': f'Cache hit rate is {cache_hit_rate:.1%}, which is below optimal',
                'suggestions': [
                    'Increase cache TTL for stable operations',
                    'Implement cache warming strategies',
                    'Optimize cache key generation',
                    'Pre-process common text patterns'
                ],
                'expected_improvement': f'{((0.7 - cache_hit_rate) * 100):.0f}% performance improvement'
            })
        
        # Analyze processing time patterns
        operation_times = defaultdict(list)
        for metric in recent_metrics:
            operation_times[metric.operation].append(metric.processing_time)
        
        for op, times in operation_times.items():
            if len(times) >= 5:
                avg_time = statistics.mean(times)
                if avg_time > 2.0:  # Operations taking more than 2 seconds
                    recommendations.append({
                        'type': 'performance_optimization',
                        'priority': 'medium',
                        'description': f'{op.value} operations averaging {avg_time:.2f}s',
                        'suggestions': [
                            'Use lighter models for real-time processing',
                            'Implement text chunking for large documents',
                            'Enable parallel processing',
                            'Consider GPU acceleration'
                        ],
                        'expected_improvement': 'Up to 60% processing time reduction'
                    })
        
        # Analyze model performance
        if self.enable_model_monitoring:
            for model_name, performance_history in self.model_performance.items():
                if len(performance_history) >= 10:
                    recent_avg = statistics.mean(performance_history[-5:])
                    overall_avg = statistics.mean(performance_history)
                    
                    if recent_avg > overall_avg * 1.3:  # 30% performance degradation
                        recommendations.append({
                            'type': 'model_optimization',
                            'priority': 'high',
                            'description': f'Model {model_name} performance degraded by {((recent_avg/overall_avg - 1) * 100):.0f}%',
                            'suggestions': [
                                'Check model health and restart if needed',
                                'Monitor resource usage and scaling',
                                'Consider model version updates',
                                'Implement model fallback mechanisms'
                            ],
                            'expected_improvement': 'Restore original performance levels'
                        })
        
        return recommendations
    
    def get_performance_summary(
        self,
        operation: Optional[NLPOperation] = None,
        time_window: timedelta = timedelta(hours=1)
    ) -> Dict[str, Any]:
        """
        Get performance summary for NLP processing
        
        Args:
            operation: Specific operation to analyze
            time_window: Time window for analysis
        
        Returns:
            Performance summary dictionary
        """
        cutoff_time = datetime.now() - time_window
        
        # Filter recent metrics
        recent_metrics = [
            m for m in self.processing_metrics
            if (m.timestamp >= cutoff_time and
                (operation is None or m.operation == operation))
        ]
        
        if not recent_metrics:
            return {'error': 'No metrics available'}
        
        # Calculate statistics
        processing_times = [m.processing_time for m in recent_metrics]
        throughputs = [m.throughput for m in recent_metrics if m.throughput > 0]
        accuracy_scores = [m.accuracy_score for m in recent_metrics if m.accuracy_score is not None]
        cache_hits = [m for m in recent_metrics if m.cache_hit]
        
        summary = {
            'time_window': str(time_window),
            'total_operations': len(recent_metrics),
            'operations_analyzed': len(set(m.operation for m in recent_metrics)),
            'performance_metrics': {
                'avg_processing_time': statistics.mean(processing_times),
                'p95_processing_time': statistics.quantiles(processing_times, n=20)[18] if len(processing_times) >= 20 else max(processing_times),
                'total_errors': sum(m.error_count for m in recent_metrics),
                'cache_hit_rate': (len(cache_hits) / len(recent_metrics)) * 100
            }
        }
        
        if throughputs:
            summary['performance_metrics'].update({
                'avg_throughput': statistics.mean(throughputs),
                'max_throughput': max(throughputs)
            })
        
        if accuracy_scores:
            summary['performance_metrics'].update({
                'avg_accuracy': statistics.mean(accuracy_scores),
                'min_accuracy': min(accuracy_scores)
            })
        
        # Model performance summary
        if self.enable_model_monitoring:
            model_stats = {}
            for model_name, performance_history in self.model_performance.items():
                if performance_history:
                    model_stats[model_name] = {
                        'avg_processing_time': statistics.mean(performance_history),
                        'operations_count': len(performance_history)
                    }
            summary['model_performance'] = model_stats
        
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
class NLPProfiler:
    """Context manager for NLP processing profiling"""
    
    def __init__(
        self,
        profiler: NLPProcessingProfiler,
        operation: NLPOperation,
        text: str,
        analysis_quality: AnalysisQuality = AnalysisQuality.BALANCED,
        model_name: Optional[str] = None,
        **kwargs
    ):
        self.profiler = profiler
        self.operation = operation
        self.text = text
        self.analysis_quality = analysis_quality
        self.model_name = model_name
        self.kwargs = kwargs
        self.session_id: Optional[str] = None
    
    def __enter__(self):
        self.session_id = self.profiler.start_nlp_profiling(
            operation=self.operation,
            text=self.text,
            analysis_quality=self.analysis_quality,
            model_name=self.model_name,
            **self.kwargs
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session_id:
            return self.profiler.end_nlp_profiling(self.session_id)
        return None
    
    def mark_preprocessing_start(self):
        if self.session_id:
            self.profiler.mark_preprocessing_start(self.session_id)
    
    def mark_inference_start(self):
        if self.session_id:
            self.profiler.mark_inference_start(self.session_id)
    
    def mark_postprocessing_start(self):
        if self.session_id:
            self.profiler.mark_postprocessing_start(self.session_id)


# Factory function for creating profiler instances
def create_nlp_processing_profiler(
    enable_model_monitoring: bool = True,
    enable_cache_monitoring: bool = True,
    start_monitoring: bool = True
) -> NLPProcessingProfiler:
    """
    Factory function to create and configure NLP Processing Profiler
    
    Args:
        enable_model_monitoring: Enable ML model monitoring
        enable_cache_monitoring: Enable cache monitoring
        start_monitoring: Start background monitoring immediately
    
    Returns:
        Configured NLPProcessingProfiler instance
    """
    profiler = NLPProcessingProfiler(
        enable_model_monitoring=enable_model_monitoring,
        enable_cache_monitoring=enable_cache_monitoring
    )
    
    if start_monitoring:
        profiler.start_monitoring()
    
    return profiler


if __name__ == "__main__":
    # Example usage
    
    # Create profiler
    profiler = create_nlp_processing_profiler()
    
    # Example text
    sample_text = """
    Artificial Intelligence is revolutionizing the creator economy by providing powerful tools 
    for content generation, optimization, and distribution. This technology enables creators 
    to produce high-quality content more efficiently while reaching broader audiences through 
    intelligent SEO optimization and personalized recommendations.
    """
    
    # Example: Profile sentiment analysis
    with NLPProfiler(
        profiler=profiler,
        operation=NLPOperation.SENTIMENT_ANALYSIS,
        text=sample_text,
        analysis_quality=AnalysisQuality.ACCURATE,
        model_name="sentiment-bert-v1"
    ) as session:
        
        # Simulate processing phases
        session.mark_preprocessing_start()
        time.sleep(0.1)
        
        session.mark_inference_start()
        time.sleep(0.3)
        
        session.mark_postprocessing_start()
        time.sleep(0.05)
    
    # Example: SEO analysis
    seo_metrics = profiler.analyze_seo(
        title="AI in Creator Economy: Revolutionary Tools for Content Creation",
        content=sample_text,
        meta_description="Discover how AI is transforming the creator economy with powerful content tools",
        target_keywords=["AI", "creator economy", "content creation", "artificial intelligence"]
    )
    
    print("SEO Analysis Results:")
    print(f"Overall SEO Score: {seo_metrics.overall_seo_score:.1f}")
    print(f"Title Score: {seo_metrics.title_optimization_score:.1f}")
    print(f"Content Quality Score: {seo_metrics.content_quality_score:.1f}")
    print("Optimization Suggestions:", seo_metrics.optimization_suggestions)
    
    # Get performance summary
    summary = profiler.get_performance_summary()
    print("Performance Summary:", json.dumps(summary, indent=2))
    
    # Stop monitoring
    profiler.stop_monitoring()