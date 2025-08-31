"""Multilingual Support Metrics & Monitoring System

Enterprise-grade monitoring, analytics, and performance tracking for
multilingual communication systems in content creator environments.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE ⚠️
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
"""import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
import json
import statistics
from collections import defaultdict, Counter

# Monitoring and metrics
import prometheus_client
from prometheus_client import Counter as PrometheusCounter, Histogram, Gauge
import redis.asyncio as aioredis

# Internal imports
from .language_manager import SupportedLanguage
from .translation_engine import TranslationResult, TranslationProvider
from .content_creator_specialist import CreatorType, ContentCategory, PlatformType

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics tracked"""    TRANSLATION_COUNT = "translation_count"
    TRANSLATION_LATENCY = "translation_latency"
    TRANSLATION_QUALITY = "translation_quality"
    LANGUAGE_DETECTION_ACCURACY = "language_detection_accuracy"
    CULTURAL_ADAPTATION_SUCCESS = "cultural_adaptation_success"
    CREATOR_SATISFACTION = "creator_satisfaction"
    PLATFORM_PERFORMANCE = "platform_performance"
    ERROR_RATE = "error_rate"
    CACHE_HIT_RATE = "cache_hit_rate"
    API_USAGE = "api_usage"


class QualityThreshold(Enum):
    """Quality thresholds for different use cases"""    CRITICAL = 0.95  # Rights protection, legal content
    HIGH = 0.90      # Brand collaboration, monetization
    STANDARD = 0.85  # General communication
    BASIC = 0.75     # Informal content


@dataclass
class TranslationMetrics:
    """Comprehensive translation performance metrics"""    translation_id: str
    timestamp: datetime
    source_language: SupportedLanguage
    target_language: SupportedLanguage
    provider: TranslationProvider
    creator_type: Optional[CreatorType] = None
    content_category: Optional[ContentCategory] = None
    platform: Optional[PlatformType] = None
    
    # Performance metrics
    latency_ms: float = 0.0
    quality_score: float = 0.0
    confidence_score: float = 0.0
    character_count: int = 0
    word_count: int = 0
    
    # Quality indicators
    human_review_required: bool = False
    human_review_score: Optional[float] = None
    user_satisfaction_score: Optional[float] = None
    
    # Business metrics
    cost_usd: float = 0.0
    cache_hit: bool = False
    error_occurred: bool = False
    error_type: Optional[str] = None
    
    # Context metrics
    brand_voice_preserved: bool = True
    cultural_adaptation_applied: bool = False
    seo_optimization_applied: bool = False
    terminology_accuracy: float = 1.0


@dataclass
class LanguagePerformanceReport:
    """Performance report for specific language pairs"""    source_language: SupportedLanguage
    target_language: SupportedLanguage
    period_start: datetime
    period_end: datetime
    
    # Volume metrics
    total_translations: int = 0
    total_characters: int = 0
    total_words: int = 0
    
    # Performance metrics
    avg_latency_ms: float = 0.0
    avg_quality_score: float = 0.0
    avg_confidence_score: float = 0.0
    cache_hit_rate: float = 0.0
    error_rate: float = 0.0
    
    # Quality metrics
    human_review_rate: float = 0.0
    user_satisfaction_avg: float = 0.0
    terminology_accuracy_avg: float = 1.0
    
    # Business metrics
    total_cost_usd: float = 0.0
    cost_per_character: float = 0.0
    
    # Provider breakdown
    provider_performance: Dict[TranslationProvider, Dict[str, float]] = field(default_factory=dict)


@dataclass
class CreatorTypeReport:
    """Performance report for specific creator types"""    creator_type: CreatorType
    period_start: datetime
    period_end: datetime
    
    # Volume by content category
    category_volumes: Dict[ContentCategory, int] = field(default_factory=dict)
    
    # Platform distribution
    platform_distribution: Dict[PlatformType, int] = field(default_factory=dict)
    
    # Language preferences
    popular_languages: List[Tuple[SupportedLanguage, int]] = field(default_factory=list)
    
    # Quality metrics
    avg_satisfaction_score: float = 0.0
    specialized_terminology_accuracy: float = 1.0
    brand_voice_preservation_rate: float = 1.0
    
    # Business value
    total_cost_usd: float = 0.0
    avg_cost_per_translation: float = 0.0


class MultilingualMetricsCollector:
    """    Enterprise-grade metrics collection and analysis system for multilingual
    communication in content creator environments.
    """    
    def __init__(self, redis_client: aioredis.Redis):
        self.redis_client = redis_client
        
        # Prometheus metrics
        self._setup_prometheus_metrics()
        
        # In-memory metric buffers
        self.translation_metrics: List[TranslationMetrics] = []
        self.metric_buffer_size = 10000
        
        # Aggregated statistics
        self.language_pair_stats: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.creator_type_stats: Dict[CreatorType, Dict[str, Any]] = defaultdict(dict)
        self.platform_stats: Dict[PlatformType, Dict[str, Any]] = defaultdict(dict)
        
        # Real-time monitoring
        self.active_sessions: Dict[str, datetime] = {}
        self.error_alerts: List[Dict[str, Any]] = []
    
    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics for monitoring"""        
        self.translation_counter = PrometheusCounter(
            'multilingual_translations_total',
            'Total number of translations performed',
            ['source_lang', 'target_lang', 'provider', 'creator_type', 'content_category']
        )
        
        self.translation_latency = Histogram(
            'multilingual_translation_latency_seconds',
            'Translation latency in seconds',
            ['source_lang', 'target_lang', 'provider'],
            buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
        )
        
        self.translation_quality = Histogram(
            'multilingual_translation_quality_score',
            'Translation quality score distribution',
            ['source_lang', 'target_lang', 'provider'],
            buckets=[0.5, 0.6, 0.7, 0.8, 0.85, 0.9, 0.95, 1.0]
        )
        
        self.error_counter = PrometheusCounter(
            'multilingual_errors_total',
            'Total number of translation errors',
            ['error_type', 'provider', 'source_lang', 'target_lang']
        )
        
        self.cache_hit_rate = Gauge(
            'multilingual_cache_hit_rate',
            'Translation cache hit rate',
            ['language_pair']
        )
        
        self.active_sessions_gauge = Gauge(
            'multilingual_active_sessions',
            'Number of active multilingual sessions'
        )
        
        self.user_satisfaction = Histogram(
            'multilingual_user_satisfaction_score',
            'User satisfaction score distribution',
            ['creator_type', 'content_category'],
            buckets=[1.0, 2.0, 3.0, 4.0, 5.0]
        )
    
    async def record_translation_metrics(self, metrics: TranslationMetrics):
        """Record comprehensive translation metrics"""        
        # Update Prometheus metrics
        self.translation_counter.labels(
            source_lang=metrics.source_language.value,
            target_lang=metrics.target_language.value,
            provider=metrics.provider.value,
            creator_type=metrics.creator_type.value if metrics.creator_type else "unknown",
            content_category=metrics.content_category.value if metrics.content_category else "general"
        ).inc()
        
        self.translation_latency.labels(
            source_lang=metrics.source_language.value,
            target_lang=metrics.target_language.value,
            provider=metrics.provider.value
        ).observe(metrics.latency_ms / 1000.0)
        
        self.translation_quality.labels(
            source_lang=metrics.source_language.value,
            target_lang=metrics.target_language.value,
            provider=metrics.provider.value
        ).observe(metrics.quality_score)
        
        if metrics.error_occurred:
            self.error_counter.labels(
                error_type=metrics.error_type or "unknown",
                provider=metrics.provider.value,
                source_lang=metrics.source_language.value,
                target_lang=metrics.target_language.value
            ).inc()
        
        if metrics.user_satisfaction_score:
            self.user_satisfaction.labels(
                creator_type=metrics.creator_type.value if metrics.creator_type else "unknown",
                content_category=metrics.content_category.value if metrics.content_category else "general"
            ).observe(metrics.user_satisfaction_score)
        
        # Store in buffer
        self.translation_metrics.append(metrics)
        
        # Maintain buffer size
        if len(self.translation_metrics) > self.metric_buffer_size:
            self.translation_metrics = self.translation_metrics[-self.metric_buffer_size:]
        
        # Store in Redis for persistence
        await self._persist_metrics_to_redis(metrics)
        
        # Update real-time aggregations
        await self._update_real_time_stats(metrics)
    
    async def _persist_metrics_to_redis(self, metrics: TranslationMetrics):
        """Persist metrics to Redis for historical analysis"""        
        # Store individual metric
        metric_key = f"translation_metric:{metrics.translation_id}"
        metric_data = {
            "timestamp": metrics.timestamp.isoformat(),
            "source_language": metrics.source_language.value,
            "target_language": metrics.target_language.value,
            "provider": metrics.provider.value,
            "creator_type": metrics.creator_type.value if metrics.creator_type else None,
            "content_category": metrics.content_category.value if metrics.content_category else None,
            "platform": metrics.platform.value if metrics.platform else None,
            "latency_ms": metrics.latency_ms,
            "quality_score": metrics.quality_score,
            "confidence_score": metrics.confidence_score,
            "character_count": metrics.character_count,
            "word_count": metrics.word_count,
            "cost_usd": metrics.cost_usd,
            "cache_hit": metrics.cache_hit,
            "error_occurred": metrics.error_occurred,
            "error_type": metrics.error_type,
            "terminology_accuracy": metrics.terminology_accuracy
        }
        
        await self.redis_client.hset(metric_key, mapping=metric_data)
        await self.redis_client.expire(metric_key, 86400 * 30)  # Keep for 30 days
        
        # Add to time-series for aggregation
        date_key = metrics.timestamp.strftime("%Y-%m-%d")
        hour_key = metrics.timestamp.strftime("%Y-%m-%d-%H")
        
        # Daily aggregation
        daily_key = f"daily_metrics:{date_key}"
        await self.redis_client.lpush(daily_key, metrics.translation_id)
        await self.redis_client.expire(daily_key, 86400 * 30)
        
        # Hourly aggregation
        hourly_key = f"hourly_metrics:{hour_key}"
        await self.redis_client.lpush(hourly_key, metrics.translation_id)
        await self.redis_client.expire(hourly_key, 86400 * 7)
    
    async def _update_real_time_stats(self, metrics: TranslationMetrics):
        """Update real-time statistics"""        
        # Language pair statistics
        lang_pair = f"{metrics.source_language.value}_{metrics.target_language.value}"
        
        if lang_pair not in self.language_pair_stats:
            self.language_pair_stats[lang_pair] = {
                "count": 0,
                "total_latency": 0.0,
                "total_quality": 0.0,
                "cache_hits": 0,
                "errors": 0
            }
        
        stats = self.language_pair_stats[lang_pair]
        stats["count"] += 1
        stats["total_latency"] += metrics.latency_ms
        stats["total_quality"] += metrics.quality_score
        
        if metrics.cache_hit:
            stats["cache_hits"] += 1
        
        if metrics.error_occurred:
            stats["errors"] += 1
        
        # Update cache hit rate gauge
        cache_hit_rate = stats["cache_hits"] / stats["count"] if stats["count"] > 0 else 0
        self.cache_hit_rate.labels(language_pair=lang_pair).set(cache_hit_rate)
        
        # Creator type statistics
        if metrics.creator_type:
            if metrics.creator_type not in self.creator_type_stats:
                self.creator_type_stats[metrics.creator_type] = {
                    "count": 0,
                    "total_satisfaction": 0.0,
                    "satisfaction_count": 0,
                    "total_cost": 0.0
                }
            
            creator_stats = self.creator_type_stats[metrics.creator_type]
            creator_stats["count"] += 1
            creator_stats["total_cost"] += metrics.cost_usd
            
            if metrics.user_satisfaction_score:
                creator_stats["total_satisfaction"] += metrics.user_satisfaction_score
                creator_stats["satisfaction_count"] += 1
    
    async def generate_language_performance_report(
        self,
        source_language: SupportedLanguage,
        target_language: SupportedLanguage,
        period_days: int = 7
    ) -> LanguagePerformanceReport:
        """Generate comprehensive performance report for language pair"""        
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=period_days)
        
        # Filter metrics for the specified period and language pair
        filtered_metrics = [
            m for m in self.translation_metrics
            if (m.source_language == source_language and
                m.target_language == target_language and
                start_time <= m.timestamp <= end_time)
        ]
        
        if not filtered_metrics:
            return LanguagePerformanceReport(
                source_language=source_language,
                target_language=target_language,
                period_start=start_time,
                period_end=end_time
            )
        
        # Calculate aggregated metrics
        total_translations = len(filtered_metrics)
        total_characters = sum(m.character_count for m in filtered_metrics)
        total_words = sum(m.word_count for m in filtered_metrics)
        
        avg_latency = statistics.mean(m.latency_ms for m in filtered_metrics)
        avg_quality = statistics.mean(m.quality_score for m in filtered_metrics)
        avg_confidence = statistics.mean(m.confidence_score for m in filtered_metrics)
        
        cache_hits = sum(1 for m in filtered_metrics if m.cache_hit)
        cache_hit_rate = cache_hits / total_translations if total_translations > 0 else 0
        
        errors = sum(1 for m in filtered_metrics if m.error_occurred)
        error_rate = errors / total_translations if total_translations > 0 else 0
        
        human_reviews = sum(1 for m in filtered_metrics if m.human_review_required)
        human_review_rate = human_reviews / total_translations if total_translations > 0 else 0
        
        satisfaction_scores = [m.user_satisfaction_score for m in filtered_metrics if m.user_satisfaction_score]
        avg_satisfaction = statistics.mean(satisfaction_scores) if satisfaction_scores else 0
        
        terminology_accuracies = [m.terminology_accuracy for m in filtered_metrics]
        avg_terminology_accuracy = statistics.mean(terminology_accuracies)
        
        total_cost = sum(m.cost_usd for m in filtered_metrics)
        cost_per_character = total_cost / total_characters if total_characters > 0 else 0
        
        # Provider performance breakdown
        provider_performance = {}
        for provider in TranslationProvider:
            provider_metrics = [m for m in filtered_metrics if m.provider == provider]
            if provider_metrics:
                provider_performance[provider] = {
                    "count": len(provider_metrics),
                    "avg_latency": statistics.mean(m.latency_ms for m in provider_metrics),
                    "avg_quality": statistics.mean(m.quality_score for m in provider_metrics),
                    "error_rate": sum(1 for m in provider_metrics if m.error_occurred) / len(provider_metrics)
                }
        
        return LanguagePerformanceReport(
            source_language=source_language,
            target_language=target_language,
            period_start=start_time,
            period_end=end_time,
            total_translations=total_translations,
            total_characters=total_characters,
            total_words=total_words,
            avg_latency_ms=avg_latency,
            avg_quality_score=avg_quality,
            avg_confidence_score=avg_confidence,
            cache_hit_rate=cache_hit_rate,
            error_rate=error_rate,
            human_review_rate=human_review_rate,
            user_satisfaction_avg=avg_satisfaction,
            terminology_accuracy_avg=avg_terminology_accuracy,
            total_cost_usd=total_cost,
            cost_per_character=cost_per_character,
            provider_performance=provider_performance
        )
    
    async def generate_creator_type_report(
        self,
        creator_type: CreatorType,
        period_days: int = 30
    ) -> CreatorTypeReport:
        """Generate comprehensive report for specific creator type"""        
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=period_days)
        
        # Filter metrics for creator type and period
        filtered_metrics = [
            m for m in self.translation_metrics
            if (m.creator_type == creator_type and
                start_time <= m.timestamp <= end_time)
        ]
        
        if not filtered_metrics:
            return CreatorTypeReport(
                creator_type=creator_type,
                period_start=start_time,
                period_end=end_time
            )
        
        # Category volumes
        category_volumes = Counter(
            m.content_category for m in filtered_metrics if m.content_category
        )
        
        # Platform distribution
        platform_distribution = Counter(
            m.platform for m in filtered_metrics if m.platform
        )
        
        # Popular languages
        language_counter = Counter()
        for m in filtered_metrics:
            language_counter[m.target_language] += 1
        popular_languages = language_counter.most_common(10)
        
        # Quality metrics
        satisfaction_scores = [m.user_satisfaction_score for m in filtered_metrics if m.user_satisfaction_score]
        avg_satisfaction = statistics.mean(satisfaction_scores) if satisfaction_scores else 0
        
        terminology_accuracies = [m.terminology_accuracy for m in filtered_metrics]
        avg_terminology_accuracy = statistics.mean(terminology_accuracies)
        
        brand_voice_preserved = sum(1 for m in filtered_metrics if m.brand_voice_preserved)
        brand_voice_preservation_rate = brand_voice_preserved / len(filtered_metrics) if filtered_metrics else 1.0
        
        # Business metrics
        total_cost = sum(m.cost_usd for m in filtered_metrics)
        avg_cost_per_translation = total_cost / len(filtered_metrics) if filtered_metrics else 0
        
        return CreatorTypeReport(
            creator_type=creator_type,
            period_start=start_time,
            period_end=end_time,
            category_volumes=dict(category_volumes),
            platform_distribution=dict(platform_distribution),
            popular_languages=popular_languages,
            avg_satisfaction_score=avg_satisfaction,
            specialized_terminology_accuracy=avg_terminology_accuracy,
            brand_voice_preservation_rate=brand_voice_preservation_rate,
            total_cost_usd=total_cost,
            avg_cost_per_translation=avg_cost_per_translation
        )
    
    async def detect_quality_anomalies(self) -> List[Dict[str, Any]]:
        """Detect quality anomalies and potential issues"""        
        anomalies = []
        recent_metrics = [
            m for m in self.translation_metrics
            if m.timestamp >= datetime.now(timezone.utc) - timedelta(hours=24)
        ]
        
        if not recent_metrics:
            return anomalies
        
        # Check for quality degradation
        avg_quality = statistics.mean(m.quality_score for m in recent_metrics)
        if avg_quality < QualityThreshold.STANDARD.value:
            anomalies.append({
                "type": "quality_degradation",
                "severity": "high" if avg_quality < QualityThreshold.BASIC.value else "medium",
                "description": f"Average quality score dropped to {avg_quality:.3f}",
                "affected_translations": len(recent_metrics),
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        # Check for latency spikes
        avg_latency = statistics.mean(m.latency_ms for m in recent_metrics)
        if avg_latency > 5000:  # 5 seconds
            anomalies.append({
                "type": "latency_spike",
                "severity": "high" if avg_latency > 10000 else "medium",
                "description": f"Average latency increased to {avg_latency:.0f}ms",
                "affected_translations": len(recent_metrics),
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        # Check for error rate increase
        error_count = sum(1 for m in recent_metrics if m.error_occurred)
        error_rate = error_count / len(recent_metrics)
        if error_rate > 0.05:  # 5% error rate
            anomalies.append({
                "type": "error_rate_increase",
                "severity": "high" if error_rate > 0.10 else "medium",
                "description": f"Error rate increased to {error_rate:.1%}",
                "affected_translations": error_count,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        # Check for provider issues
        provider_errors = Counter(
            m.provider for m in recent_metrics if m.error_occurred
        )
        
        for provider, error_count in provider_errors.items():
            provider_metrics = [m for m in recent_metrics if m.provider == provider]
            provider_error_rate = error_count / len(provider_metrics)
            
            if provider_error_rate > 0.10:  # 10% error rate for specific provider
                anomalies.append({
                    "type": "provider_degradation",
                    "severity": "high",
                    "description": f"Provider {provider.value} has {provider_error_rate:.1%} error rate",
                    "provider": provider.value,
                    "affected_translations": error_count,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
        
        return anomalies
    
    async def get_real_time_dashboard_data(self) -> Dict[str, Any]:
        """Get real-time dashboard data for monitoring"""        
        now = datetime.now(timezone.utc)
        last_hour = now - timedelta(hours=1)
        last_24h = now - timedelta(hours=24)
        
        recent_metrics = [
            m for m in self.translation_metrics
            if m.timestamp >= last_hour
        ]
        
        daily_metrics = [
            m for m in self.translation_metrics
            if m.timestamp >= last_24h
        ]
        
        # Update active sessions gauge
        active_count = len([
            session_id for session_id, last_activity in self.active_sessions.items()
            if last_activity >= now - timedelta(minutes=15)
        ])
        self.active_sessions_gauge.set(active_count)
        
        dashboard_data = {
            "current_time": now.isoformat(),
            "active_sessions": active_count,
            "last_hour": {
                "translations": len(recent_metrics),
                "avg_quality": statistics.mean(m.quality_score for m in recent_metrics) if recent_metrics else 0,
                "avg_latency_ms": statistics.mean(m.latency_ms for m in recent_metrics) if recent_metrics else 0,
                "error_rate": sum(1 for m in recent_metrics if m.error_occurred) / len(recent_metrics) if recent_metrics else 0,
                "cache_hit_rate": sum(1 for m in recent_metrics if m.cache_hit) / len(recent_metrics) if recent_metrics else 0
            },
            "last_24h": {
                "translations": len(daily_metrics),
                "unique_languages": len(set(m.target_language for m in daily_metrics)),
                "unique_creators": len(set(m.creator_type for m in daily_metrics if m.creator_type)),
                "total_cost_usd": sum(m.cost_usd for m in daily_metrics),
                "avg_satisfaction": statistics.mean(
                    m.user_satisfaction_score for m in daily_metrics if m.user_satisfaction_score
                ) if any(m.user_satisfaction_score for m in daily_metrics) else 0
            },
            "top_language_pairs": [
                {
                    "pair": f"{lang_pair.replace('_', ' → ')}",
                    "count": stats["count"],
                    "avg_quality": stats["total_quality"] / stats["count"] if stats["count"] > 0 else 0
                }
                for lang_pair, stats in sorted(
                    self.language_pair_stats.items(),
                    key=lambda x: x[1]["count"],
                    reverse=True
                )[:10]
            ],
            "anomalies": await self.detect_quality_anomalies()
        }
        
        return dashboard_data
    
    def update_session_activity(self, session_id: str):
        """Update session activity timestamp"""        self.active_sessions[session_id] = datetime.now(timezone.utc)
    
    def end_session(self, session_id: str):
        """End a multilingual session"""        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
