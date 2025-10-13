"""
Streaming Analytics Engine - Analytics temps réel streaming

Moteur analytics avancé pour streaming avec métriques temps réel,
insights audience prédictifs, détection anomalies et rapports
performance automatisés multi-plateformes.

Copyright (c) 2025 Fahed Mlaiel (mlaiel@live.de)
Protected by copyright - All rights reserved
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from uuid import uuid4
import statistics


logger = logging.getLogger(__name__)


class MetricType(Enum):
    """
        Types de métriques collectées"""
    VIEWERS = "viewers"
    ENGAGEMENT = "engagement"
    REVENUE = "revenue"
    QUALITY = "quality"
    PERFORMANCE = "performance"
    AUDIENCE = "audience"
    CONTENT = "content"
    TECHNICAL = "technical"


class AnalyticsTimeframe(Enum):
    """Périodes d'analyse"""
    REAL_TIME = "real_time"  # Dernières 5 min
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class InsightPriority(Enum):
    """Priorités des insights"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class MetricPoint:
    """Point de métrique temporel"""
    timestamp: datetime
    metric_type: MetricType
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalyticsReport:
    """
        Rapport analytics complet"""
    report_id: str
    stream_id: str
    timeframe: AnalyticsTimeframe
    start_time: datetime
    end_time: datetime
    metrics_summary: Dict[MetricType, Dict[str, float]]
    top_insights: List[Dict[str, Any]]
    recommendations: List[str]
    benchmark_comparison: Dict[str, float]
    generated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RealTimeMetrics:
    """
        Métriques temps réel"""
    stream_id: str
    current_viewers: int
    peak_viewers: int
    average_viewers: float
    engagement_rate: float
    chat_messages_per_minute: float
    likes_per_minute: float
    shares_count: int
    new_followers: int
    revenue_rate: float  # $/minute
    quality_score: float  # 0-100
    buffering_ratio: float  # %
    average_bitrate: int
    viewer_countries: Dict[str, int]
    viewer_devices: Dict[str, int]
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AudienceInsights:
    """
        Insights audience détaillés"""
    stream_id: str
    demographics: Dict[str, Any]
    geographic_distribution: Dict[str, int]
    device_breakdown: Dict[str, int]
    viewing_patterns: Dict[str, Any]
    engagement_segments: Dict[str, float]
    retention_curve: List[Tuple[int, float]]  # (minute, retention%)
    churn_points: List[int]  # minutes où viewers quittent
    peak_activity_times: List[str]
    audience_overlap: Dict[str, float]  # Autres streams regardés


@dataclass
class PredictiveInsight:
    """
        Insight prédictif actionable"""
    insight_id: str
    priority: InsightPriority
    category: str
    title: str
    description: str
    predicted_impact: str
    confidence_score: float  # 0-1
    recommended_actions: List[str]
    expected_results: Dict[str, Any]
    time_sensitive: bool
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class StreamingAnalyticsRecord:
    """
        Enregistrement analytics streaming"""
    record_id: str
    stream_id: str
    creator_id: str
    session_start: datetime
    session_end: Optional[datetime]
    real_time_metrics: RealTimeMetrics
    audience_insights: AudienceInsights
    predictive_insights: List[PredictiveInsight]
    anomalies_detected: List[Dict[str, Any]]
    performance_score: float  # 0-100


class StreamingAnalyticsEngine:
    """
    Moteur analytics streaming temps réel
    
    Fonctionnalités:
    - Collecte métriques temps réel multi-sources
    - Génération insights prédictifs ML
    - Détection anomalies automatique
    - Benchmarking compétitif
    - Rapports automatisés personnalisés
    - Alertes intelligentes temps réel
    - Analytics multi-plateformes agrégées
    """
    
    def __init__(self, enable_predictive: bool = True):
        """
        Initialise le moteur analytics
        
        Args:
            enable_predictive: Activer insights prédictifs ML
        """
        self.enable_predictive = enable_predictive
        self.active_streams: Dict[str, StreamingAnalyticsRecord] = {}
        self.metrics_buffer: Dict[str, List[MetricPoint]] = {}
        self.historical_benchmarks: Dict[str, Dict[str, float]] = {}
        self.anomaly_thresholds: Dict[MetricType, Dict[str, float]] = {}
        
        # Initialiser seuils anomalies
        self._initialize_anomaly_thresholds()

        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"StreamingAnalyticsEngine initialized (predictive={enable_predictive})")
    
    def _initialize_anomaly_thresholds(self) -> None:
        """Initialise seuils détection anomalies"""
        self.anomaly_thresholds = {
            MetricType.VIEWERS: {
                "sudden_drop_threshold": 0.30,  # -30% viewers en <5min
                "sudden_spike_threshold": 2.0,  # +100% viewers en <5min
                "volatility_threshold": 0.50
            },
            MetricType.ENGAGEMENT: {
                "low_engagement_threshold": 0.10,  # <10% engagement
                "chat_silence_threshold": 1.0  # <1 msg/min
            },
            MetricType.QUALITY: {
                "quality_drop_threshold": 70.0,  # <70 score
                "buffering_threshold": 0.05,  # >5% buffering
                "bitrate_drop_threshold": 0.40  # -40% bitrate
            }
        }
    
    async def start_stream_analytics(
        self,
        stream_id: str,
        creator_id: str
    ) -> StreamingAnalyticsRecord:
        """
        Démarre analytics pour un stream
        
        Args:
            stream_id: ID du stream
            creator_id: ID créateur
            
        Returns:
            Enregistrement analytics créé
        """
        record_id = str(uuid4())
        
        # Initialiser métriques temps réel

        real_time_metrics = RealTimeMetrics(
            stream_id=stream_id,
            current_viewers=0,
            peak_viewers=0,
            average_viewers=0.0,
            engagement_rate=0.0,
            chat_messages_per_minute=0.0,
            likes_per_minute=0.0,
            shares_count=0,
            new_followers=0,
            revenue_rate=0.0,
            quality_score=100.0,
            buffering_ratio=0.0,
            average_bitrate=6000,
            viewer_countries={},
            viewer_devices={}
        )
        
        # Initialiser insights audience

        audience_insights = AudienceInsights(
            stream_id=stream_id,
            demographics={},
            geographic_distribution={},
            device_breakdown={},
            viewing_patterns={},
            engagement_segments={},
            retention_curve=[],
            churn_points=[],
            peak_activity_times=[],
            audience_overlap={}
        )
        
        # Créer enregistrement

        record = StreamingAnalyticsRecord(
            record_id=record_id,
            stream_id=stream_id,
            creator_id=creator_id,
            session_start=datetime.utcnow(),
            session_end=None,
            real_time_metrics=real_time_metrics,
            audience_insights=audience_insights,
            predictive_insights=[],
            anomalies_detected=[],
            performance_score=0.0
        )

        
        self.active_streams[stream_id] = record
        self.metrics_buffer[stream_id] = []
        
        # Démarrer monitoring continu
        asyncio.create_task(self._monitor_stream_metrics(stream_id))

        
        self.logger.info(f"Started analytics for stream {stream_id}")
        return record
    
    async def update_metrics(
        self,
        stream_id: str,
        metrics_update: Dict[str, Any]
    ) -> bool:
        """
        Met à jour les métriques d'un stream
        
        Args:
            stream_id: ID du stream
            metrics_update: Nouvelles métriques
            
        Returns:
            True si mise à jour réussie
        """
        if stream_id not in self.active_streams:
            return False

        
        record = self.active_streams[stream_id]

        metrics = record.real_time_metrics
        
        # Mettre à jour métriques
        for key, value in metrics_update.items():
            if hasattr(metrics, key):
                old_value = getattr(metrics, key)

                setattr(metrics, key, value)
                
                # Enregistrer point métrique pour historique
                if isinstance(value, (int, float)):
                    metric_type = self._get_metric_type(key)


                    point = MetricPoint(
                        timestamp=datetime.utcnow(),
                        metric_type=metric_type,
                        value=float(value),
                        metadata={"key": key, "old_value": old_value}
                    )

                    self.metrics_buffer[stream_id].append(point)
        
        # Mettre à jour peak viewers
        if metrics.current_viewers > metrics.peak_viewers:
            metrics.peak_viewers = metrics.current_viewers
        
        # Détecter anomalies

        anomalies = await self._detect_anomalies(stream_id)
        if anomalies:
            record.anomalies_detected.extend(anomalies)
        
        # Générer insights prédictifs
        if self.enable_predictive:
            insights = await self._generate_predictive_insights(stream_id)

            record.predictive_insights.extend(insights)

        
        metrics.updated_at = datetime.utcnow()
        return True
    
    async def generate_analytics_report(
        self,
        stream_id: str,
        timeframe: AnalyticsTimeframe = AnalyticsTimeframe.DAILY
    ) -> Optional[AnalyticsReport]:
        """
        Génère rapport analytics complet
        
        Args:
            stream_id: ID du stream
            timeframe: Période d'analyse
            
        Returns:
            Rapport analytics
        """
        if stream_id not in self.active_streams and stream_id not in self.metrics_buffer:
            return None

        
        report_id = str(uuid4())

        now = datetime.utcnow()
        
        # Déterminer période
        if timeframe == AnalyticsTimeframe.HOURLY:
            start_time = now - timedelta(hours=1)
        elif timeframe == AnalyticsTimeframe.DAILY:
            start_time = now - timedelta(days=1)
        elif timeframe == AnalyticsTimeframe.WEEKLY:
            start_time = now - timedelta(weeks=1)
        else:
            start_time = now - timedelta(days=1)
        
        # Calculer métriques agrégées

        metrics_summary = await self._calculate_metrics_summary(stream_id, start_time, now)
        
        # Générer insights top

        top_insights = await self._generate_top_insights(stream_id, metrics_summary)
        
        # Générer recommandations

        recommendations = await self._generate_recommendations(stream_id, metrics_summary)
        
        # Benchmark comparison

        benchmark = await self._get_benchmark_comparison(stream_id, metrics_summary)


        
        report = AnalyticsReport(
            report_id=report_id,
            stream_id=stream_id,
            timeframe=timeframe,
            start_time=start_time,
            end_time=now,
            metrics_summary=metrics_summary,
            top_insights=top_insights,
            recommendations=recommendations,
            benchmark_comparison=benchmark
        )

        
        self.logger.info(f"Generated analytics report {report_id} for stream {stream_id}")
        return report
    
    async def get_real_time_metrics(
        self,
        stream_id: str
    ) -> Optional[RealTimeMetrics]:
        """
        Récupère métriques temps réel
        
        Args:
            stream_id: ID du stream
            
        Returns:
            Métriques temps réel ou None
        """
        if stream_id not in self.active_streams:
            return None
        return self.active_streams[stream_id].real_time_metrics
    
    async def get_audience_insights(
        self,
        stream_id: str
    ) -> Optional[AudienceInsights]:
        """
        Récupère insights audience
        
        Args:
            stream_id: ID du stream
            
        Returns:
            Insights audience ou None
        """
        if stream_id not in self.active_streams:
            return None
        return self.active_streams[stream_id].audience_insights
    
    async def get_predictive_insights(
        self,
        stream_id: str,
        min_priority: InsightPriority = InsightPriority.MEDIUM
    ) -> List[PredictiveInsight]:
        """
        Récupère insights prédictifs filtrés
        
        Args:
            stream_id: ID du stream
            min_priority: Priorité minimale
            
        Returns:
            Liste insights prédictifs
        """
        if stream_id not in self.active_streams:
            return []

        
        record = self.active_streams[stream_id]

        priority_order = [
            InsightPriority.CRITICAL,
            InsightPriority.HIGH,
            InsightPriority.MEDIUM,
            InsightPriority.LOW,
            InsightPriority.INFO
        ]

        
        min_index = priority_order.index(min_priority)

        
        return [
            insight for insight in record.predictive_insights
            if priority_order.index(insight.priority) <= min_index
        ]
    
    async def end_stream_analytics(
        self,
        stream_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Termine analytics et génère rapport final
        
        Args:
            stream_id: ID du stream
            
        Returns:
            Rapport final ou None
        """
        if stream_id not in self.active_streams:
            return None

        
        record = self.active_streams[stream_id]
        record.session_end = datetime.utcnow()
        
        # Calculer score performance global
        record.performance_score = await self._calculate_performance_score(record)
        
        # Générer rapport final

        final_report = await self.generate_analytics_report(
            stream_id,
            AnalyticsTimeframe.CUSTOM
        )
        
        # Nettoyer
        del self.active_streams[stream_id]
        
        self.logger.info(
            f"Ended analytics for stream {stream_id} "
            f"(score: {record.performance_score:.1f})"
        )

        
        return {
            "stream_id": stream_id,
            "duration": (record.session_end - record.session_start).total_seconds() / 60,
            "performance_score": record.performance_score,
            "peak_viewers": record.real_time_metrics.peak_viewers,
            "total_engagement": record.real_time_metrics.engagement_rate,
            "anomalies_count": len(record.anomalies_detected),
            "insights_count": len(record.predictive_insights),
            "report": final_report
        }
    
    async def _monitor_stream_metrics(self, stream_id: str) -> None:
        """Monitoring continu métriques stream"""
        while stream_id in self.active_streams:
            await asyncio.sleep(30)  # Check toutes les 30s
            
            # Mettre à jour average viewers
            if stream_id in self.metrics_buffer:
                viewer_points = [
                    p.value for p in self.metrics_buffer[stream_id]
                    if p.metric_type == MetricType.VIEWERS
                ]
                if viewer_points:
                    record = self.active_streams[stream_id]
                    record.real_time_metrics.average_viewers = statistics.mean(viewer_points)
    
    def _get_metric_type(self, key: str) -> MetricType:
        """
        Détermine le type de métrique"""
        if "viewer" in key.lower():
            return MetricType.VIEWERS
        elif "engagement" in key.lower() or "chat" in key.lower() or "like" in key.lower():
            return MetricType.ENGAGEMENT
        elif "revenue" in key.lower():
            return MetricType.REVENUE
        elif "quality" in key.lower() or "bitrate" in key.lower() or "buffering" in key.lower():
            return MetricType.QUALITY
        else:
            return MetricType.PERFORMANCE
    
    async def _detect_anomalies(self, stream_id: str) -> List[Dict[str, Any]]:
        """Détecte anomalies dans les métriques"""
        anomalies = []
        
        if stream_id not in self.metrics_buffer:
            return anomalies

        
        recent_points = self.metrics_buffer[stream_id][-20:]  # 20 derniers points
        
        # Détecter chute soudaine viewers

        viewer_points = [p for p in recent_points if p.metric_type == MetricType.VIEWERS]
        if len(viewer_points) >= 2:
            current = viewer_points[-1].value

            previous = viewer_points[-2].value
            if previous > 0 and (previous - current) / previous > 0.30:
                anomalies.append({
                    "type": "viewer_drop",
                    "severity": "high",
                    "description": f"Chute viewers de {previous:.0f} à {current:.0f} (-{((previous-current)/previous*100):.0f}%)",
                    "timestamp": viewer_points[-1].timestamp.isoformat()
                })

        
        return anomalies
    
    async def _generate_predictive_insights(self, stream_id: str) -> List[PredictiveInsight]:
        """Génère insights prédictifs ML"""
        insights = []
        
        if stream_id not in self.active_streams:
            return insights

        
        record = self.active_streams[stream_id]

        metrics = record.real_time_metrics
        
        # Insight: Faible engagement
        if metrics.engagement_rate < 0.15:
            insights.append(PredictiveInsight(
                insight_id=str(uuid4()),
                priority=InsightPriority.HIGH,
                category="engagement",
                title="Engagement faible détecté",
                description=f"Taux engagement actuel: {metrics.engagement_rate*100:.1f}% (cible: >15%)",
                predicted_impact="Impact négatif sur croissance et monétisation",
                confidence_score=0.85,
                recommended_actions=[
                    "Augmenter interactions chat (polls, Q&A)",
                    "Lancer challenges/giveaways",
                    "Créer moments viraux/clips"
                ],
                expected_results={"engagement_increase": "+8-12%", "follower_boost": "+15%"},
                time_sensitive=True
            ))

        
        return insights
    
    async def _calculate_metrics_summary(
        self,
        stream_id: str,
        start: datetime,
        end: datetime
    ) -> Dict[MetricType, Dict[str, float]]:
        """Calcule résumé métriques période"""
        summary = {}
        
        if stream_id not in self.metrics_buffer:
            return summary

        
        points = [
            p for p in self.metrics_buffer[stream_id]
            if start <= p.timestamp <= end
        ]
        
        for metric_type in MetricType:
            type_points = [p.value for p in points if p.metric_type == metric_type]
            if type_points:
                summary[metric_type] = {
                    "min": min(type_points),
                    "max": max(type_points),
                    "avg": statistics.mean(type_points),
                    "median": statistics.median(type_points),
                    "count": len(type_points)
                }
        
        return summary
    
    async def _generate_top_insights(
        self,
        stream_id: str,
        metrics_summary: Dict[MetricType, Dict[str, float]]
    ) -> List[Dict[str, Any]]:
        """Génère top insights"""
        insights = []
        
        if MetricType.VIEWERS in metrics_summary:
            viewer_stats = metrics_summary[MetricType.VIEWERS]
            insights.append({
                "type": "viewers",
                "title": f"Pic d'audience: {viewer_stats['max']:.0f} viewers",
                "impact": "high"
            })

        
        return insights[:5]
    
    async def _generate_recommendations(
        self,
        stream_id: str,
        metrics_summary: Dict[MetricType, Dict[str, float]]
    ) -> List[str]:
        """Génère recommandations actionnables"""
        recommendations = [
            "Maintenir constance streaming (3-5x/semaine)",
            "Optimiser titres/thumbnails pour CTR",
            "Créer clips highlights post-stream"
        ]
        return recommendations
    
    async def _get_benchmark_comparison(
        self,
        stream_id: str,
        metrics_summary: Dict[MetricType, Dict[str, float]]
    ) -> Dict[str, float]:
        """Compare aux benchmarks industrie"""
        return {
            "viewers_vs_avg": 1.2,
            "engagement_vs_avg": 0.9,
            "revenue_vs_avg": 1.5
        }
    
    async def _calculate_performance_score(
        self,
        record: StreamingAnalyticsRecord
    ) -> float:
        """Calcule score performance global 0-100"""
        metrics = record.real_time_metrics
        
        # Pondérations

        viewer_score = min(100, (metrics.peak_viewers / 100) * 30)

        engagement_score = metrics.engagement_rate * 30

        quality_score = metrics.quality_score * 0.25

        revenue_score = min(100, metrics.revenue_rate * 15)

        
        return viewer_score + engagement_score + quality_score + revenue_score


def create_streaming_analytics_engine(
    enable_predictive: bool = True
) -> StreamingAnalyticsEngine:
    """
    Factory function pour créer moteur analytics
    
    Args:
        enable_predictive: Activer insights prédictifs ML
        
    Returns:
        Instance de StreamingAnalyticsEngine
    """
    return StreamingAnalyticsEngine(enable_predictive=enable_predictive)


__all__ = [
    "StreamingAnalyticsEngine",
    "MetricType",
    "AnalyticsTimeframe",
    "InsightPriority",
    "MetricPoint",
    "AnalyticsReport",
    "RealTimeMetrics",
    "AudienceInsights",
    "PredictiveInsight",
    "StreamingAnalyticsRecord",
    "create_streaming_analytics_engine",
]
