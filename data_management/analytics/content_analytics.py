"""
Content Analytics Collector - Advanced Content Intelligence
==========================================================

Comprehensive content performance analytics and optimization system.
Provides deep insights into content effectiveness, protection performance,
and monetization optimization across all content types.

Features:
- Content performance tracking and optimization
- Protection effectiveness analysis
- Fingerprint accuracy measurement
- Content discovery and recommendation analytics
- Revenue attribution and optimization

Author: Fahed Mlaiel
Email: mlaiel@live.de
Copyright: Proprietary - All rights reserved
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import numpy as np
from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sklearn.metrics.pairwise import cosine_similarity

from ...core.database import get_database_session
from ...models.content import Content, ContentView, ContentInteraction, ContentMetrics
from ...models.protection import ProtectionEvent, Fingerprint, ContentMatch
from ...models.monetization import Revenue, ContentRevenue
from ...models.users import User


class ContentCategory(Enum):
    """Content analytics categories."""
    PERFORMANCE = "performance"
    PROTECTION = "protection"
    DISCOVERY = "discovery"
    MONETIZATION = "monetization"
    QUALITY = "quality"
    ENGAGEMENT = "engagement"


class ContentType(Enum):
    """Supported content types."""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"


@dataclass
class ContentMetric:
    """Structured content metric data."""
    content_id: str
    metric_name: str
    value: float
    category: ContentCategory
    timestamp: datetime
    content_type: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContentPerformanceProfile:
    """Comprehensive content performance profile."""
    content_id: str
    title: str
    content_type: str
    performance_score: float
    protection_effectiveness: float
    revenue_potential: float
    engagement_metrics: Dict[str, float]
    optimization_recommendations: List[str]
    last_updated: datetime


class ContentAnalyticsCollector:
    """
    Advanced content analytics and optimization system.
    
    Provides comprehensive insights into content performance,
    protection effectiveness, and revenue optimization.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._content_cache = {}
        self._performance_thresholds = {
            'high_performance': 80.0,
            'medium_performance': 50.0,
            'low_performance': 20.0
        }
        
    async def collect_content_analytics(
        self,
        content_id: Optional[str] = None,
        content_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[ContentMetric]:
        """
        Collect comprehensive content analytics metrics.
        
        Args:
            content_id: Specific content to analyze
            content_type: Filter by content type
            start_date: Analysis start date
            end_date: Analysis end date
            
        Returns:
            List of content metrics
        """
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
            
        try:
            metrics = []
            
            # Collect performance metrics
            performance_metrics = await self._collect_performance_metrics(
                content_id, content_type, start_date, end_date
            )
            metrics.extend(performance_metrics)
            
            # Collect protection metrics
            protection_metrics = await self._collect_protection_metrics(
                content_id, content_type, start_date, end_date
            )
            metrics.extend(protection_metrics)
            
            # Collect discovery metrics
            discovery_metrics = await self._collect_discovery_metrics(
                content_id, content_type, start_date, end_date
            )
            metrics.extend(discovery_metrics)
            
            # Collect monetization metrics
            monetization_metrics = await self._collect_monetization_metrics(
                content_id, content_type, start_date, end_date
            )
            metrics.extend(monetization_metrics)
            
            # Collect quality metrics
            quality_metrics = await self._collect_quality_metrics(
                content_id, content_type, start_date, end_date
            )
            metrics.extend(quality_metrics)
            
            self.logger.info(f"Collected {len(metrics)} content analytics metrics")
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting content analytics: {e}")
            raise
            
    async def _collect_performance_metrics(
        self,
        content_id: Optional[str],
        content_type: Optional[str],
        start_date: datetime,
        end_date: datetime
    ) -> List[ContentMetric]:
        """Collect content performance metrics."""
        
        async with get_database_session() as session:
            # Base query for content performance
            base_query = select(
                Content.id,
                Content.title,
                Content.content_type,
                func.count(ContentView.id).label('view_count'),
                func.avg(ContentView.duration).label('avg_duration'),
                func.count(ContentInteraction.id).label('interaction_count'),
                func.sum(
                    case(
                        (ContentInteraction.interaction_type == 'like', 1),
                        else_=0
                    )
                ).label('like_count'),
                func.sum(
                    case(
                        (ContentInteraction.interaction_type == 'share', 1),
                        else_=0
                    )
                ).label('share_count')
            ).outerjoin(ContentView).outerjoin(ContentInteraction).where(
                Content.created_at >= start_date
            ).group_by(Content.id, Content.title, Content.content_type)
            
            if content_id:
                base_query = base_query.where(Content.id == content_id)
            if content_type:
                base_query = base_query.where(Content.content_type == content_type)
                
            result = await session.execute(base_query)
            content_data = result.fetchall()
            
            metrics = []
            
            for row in content_data:
                cid = row.id
                views = row.view_count or 0
                interactions = row.interaction_count or 0
                likes = row.like_count or 0
                shares = row.share_count or 0
                avg_duration = row.avg_duration or 0
                
                # Calculate performance score
                performance_score = self._calculate_performance_score(
                    views, interactions, likes, shares, avg_duration
                )
                
                # Engagement rate
                engagement_rate = (interactions / max(views, 1)) * 100
                
                # Viral coefficient
                viral_coefficient = shares / max(views, 1)
                
                metrics.extend([
                    ContentMetric(
                        content_id=cid,
                        metric_name="view_count",
                        value=views,
                        category=ContentCategory.PERFORMANCE,
                        timestamp=datetime.now(),
                        content_type=row.content_type,
                        metadata={
                            "title": row.title,
                            "avg_duration": avg_duration
                        }
                    ),
                    ContentMetric(
                        content_id=cid,
                        metric_name="performance_score",
                        value=performance_score,
                        category=ContentCategory.PERFORMANCE,
                        timestamp=datetime.now(),
                        content_type=row.content_type
                    ),
                    ContentMetric(
                        content_id=cid,
                        metric_name="engagement_rate",
                        value=engagement_rate,
                        category=ContentCategory.ENGAGEMENT,
                        timestamp=datetime.now(),
                        content_type=row.content_type,
                        metadata={
                            "interactions": interactions,
                            "views": views
                        }
                    ),
                    ContentMetric(
                        content_id=cid,
                        metric_name="viral_coefficient",
                        value=viral_coefficient,
                        category=ContentCategory.PERFORMANCE,
                        timestamp=datetime.now(),
                        content_type=row.content_type
                    )
                ])
                
            return metrics
            
    def _calculate_performance_score(
        self,
        views: int,
        interactions: int,
        likes: int,
        shares: int,
        avg_duration: float
    ) -> float:
        """Calculate weighted content performance score."""
        
        # Normalize metrics to 0-100 scale
        view_score = min(views / 1000, 1.0) * 100  # Max 1000 views = 100
        interaction_score = min(interactions / 100, 1.0) * 100  # Max 100 interactions = 100
        like_score = min(likes / 50, 1.0) * 100  # Max 50 likes = 100
        share_score = min(shares / 20, 1.0) * 100  # Max 20 shares = 100
        duration_score = min(avg_duration / 300, 1.0) * 100  # Max 5 min = 100
        
        # Weighted average
        weights = {
            'views': 0.3,
            'interactions': 0.2,
            'likes': 0.2,
            'shares': 0.2,
            'duration': 0.1
        }
        
        performance_score = (
            view_score * weights['views'] +
            interaction_score * weights['interactions'] +
            like_score * weights['likes'] +
            share_score * weights['shares'] +
            duration_score * weights['duration']
        )
        
        return min(performance_score, 100.0)
        
    async def _collect_protection_metrics(
        self,
        content_id: Optional[str],
        content_type: Optional[str],
        start_date: datetime,
        end_date: datetime
    ) -> List[ContentMetric]:
        """Collect content protection effectiveness metrics."""
        
        async with get_database_session() as session:
            # Protection events query
            protection_query = select(
                Content.id,
                Content.content_type,
                func.count(ProtectionEvent.id).label('protection_events'),
                func.count(
                    case(
                        (ProtectionEvent.status == 'resolved', 1),
                        else_=None
                    )
                ).label('resolved_events'),
                func.avg(ProtectionEvent.confidence_score).label('avg_confidence'),
                func.count(Fingerprint.id).label('fingerprint_count')
            ).outerjoin(ProtectionEvent).outerjoin(Fingerprint).where(
                Content.created_at >= start_date
            ).group_by(Content.id, Content.content_type)
            
            if content_id:
                protection_query = protection_query.where(Content.id == content_id)
            if content_type:
                protection_query = protection_query.where(Content.content_type == content_type)
                
            result = await session.execute(protection_query)
            protection_data = result.fetchall()
            
            metrics = []
            
            for row in protection_data:
                cid = row.id
                total_events = row.protection_events or 0
                resolved_events = row.resolved_events or 0
                avg_confidence = row.avg_confidence or 0
                fingerprint_count = row.fingerprint_count or 0
                
                # Protection effectiveness
                protection_effectiveness = (
                    (resolved_events / max(total_events, 1)) * 100
                    if total_events > 0 else 100
                )
                
                # Fingerprint coverage
                fingerprint_coverage = min(fingerprint_count * 20, 100)  # 5 fingerprints = 100%
                
                metrics.extend([
                    ContentMetric(
                        content_id=cid,
                        metric_name="protection_events_total",
                        value=total_events,
                        category=ContentCategory.PROTECTION,
                        timestamp=datetime.now(),
                        content_type=row.content_type
                    ),
                    ContentMetric(
                        content_id=cid,
                        metric_name="protection_effectiveness",
                        value=protection_effectiveness,
                        category=ContentCategory.PROTECTION,
                        timestamp=datetime.now(),
                        content_type=row.content_type,
                        metadata={
                            "resolved_events": resolved_events,
                            "total_events": total_events
                        }
                    ),
                    ContentMetric(
                        content_id=cid,
                        metric_name="fingerprint_confidence",
                        value=avg_confidence,
                        category=ContentCategory.PROTECTION,
                        timestamp=datetime.now(),
                        content_type=row.content_type
                    ),
                    ContentMetric(
                        content_id=cid,
                        metric_name="fingerprint_coverage",
                        value=fingerprint_coverage,
                        category=ContentCategory.PROTECTION,
                        timestamp=datetime.now(),
                        content_type=row.content_type,
                        metadata={
                            "fingerprint_count": fingerprint_count
                        }
                    )
                ])
                
            return metrics
            
    async def _collect_discovery_metrics(
        self,
        content_id: Optional[str],
        content_type: Optional[str],
        start_date: datetime,
        end_date: datetime
    ) -> List[ContentMetric]:
        """Collect content discovery and recommendation metrics."""
        
        async with get_database_session() as session:
            # Discovery metrics query
            discovery_query = select(
                Content.id,
                Content.title,
                Content.content_type,
                Content.tags,
                func.count(ContentView.id).label('organic_views'),
                func.count(
                    case(
                        (ContentView.source == 'search', 1),
                        else_=None
                    )
                ).label('search_views'),
                func.count(
                    case(
                        (ContentView.source == 'recommendation', 1),
                        else_=None
                    )
                ).label('recommendation_views')
            ).outerjoin(ContentView).where(
                and_(
                    Content.created_at >= start_date,
                    ContentView.created_at >= start_date,
                    ContentView.created_at <= end_date
                )
            ).group_by(Content.id, Content.title, Content.content_type, Content.tags)
            
            if content_id:
                discovery_query = discovery_query.where(Content.id == content_id)
            if content_type:
                discovery_query = discovery_query.where(Content.content_type == content_type)
                
            result = await session.execute(discovery_query)
            discovery_data = result.fetchall()
            
            metrics = []
            
            for row in discovery_data:
                cid = row.id
                organic_views = row.organic_views or 0
                search_views = row.search_views or 0
                recommendation_views = row.recommendation_views or 0
                total_views = organic_views + search_views + recommendation_views
                
                # Discovery score
                discovery_score = self._calculate_discovery_score(
                    organic_views, search_views, recommendation_views
                )
                
                # Search optimization score
                search_optimization = (search_views / max(total_views, 1)) * 100
                
                # Recommendation effectiveness
                recommendation_effectiveness = (recommendation_views / max(total_views, 1)) * 100
                
                # Tag effectiveness
                tag_count = len(row.tags.split(',')) if row.tags else 0
                tag_effectiveness = min(tag_count * 10, 100)  # 10 tags = 100%
                
                metrics.extend([
                    ContentMetric(
                        content_id=cid,
                        metric_name="discovery_score",
                        value=discovery_score,
                        category=ContentCategory.DISCOVERY,
                        timestamp=datetime.now(),
                        content_type=row.content_type,
                        metadata={
                            "total_views": total_views,
                            "title": row.title
                        }
                    ),
                    ContentMetric(
                        content_id=cid,
                        metric_name="search_optimization_score",
                        value=search_optimization,
                        category=ContentCategory.DISCOVERY,
                        timestamp=datetime.now(),
                        content_type=row.content_type
                    ),
                    ContentMetric(
                        content_id=cid,
                        metric_name="recommendation_effectiveness",
                        value=recommendation_effectiveness,
                        category=ContentCategory.DISCOVERY,
                        timestamp=datetime.now(),
                        content_type=row.content_type
                    ),
                    ContentMetric(
                        content_id=cid,
                        metric_name="tag_effectiveness",
                        value=tag_effectiveness,
                        category=ContentCategory.DISCOVERY,
                        timestamp=datetime.now(),
                        content_type=row.content_type,
                        metadata={
                            "tag_count": tag_count,
                            "tags": row.tags
                        }
                    )
                ])
                
            return metrics
            
    def _calculate_discovery_score(
        self,
        organic_views: int,
        search_views: int,
        recommendation_views: int
    ) -> float:
        """Calculate content discovery effectiveness score."""
        
        total_views = organic_views + search_views + recommendation_views
        
        if total_views == 0:
            return 0.0
            
        # Weight different discovery channels
        organic_weight = 0.4
        search_weight = 0.4
        recommendation_weight = 0.2
        
        # Normalize to percentage of total possible
        max_views = 1000  # Assumed maximum for normalization
        
        organic_score = min(organic_views / max_views, 1.0) * 100
        search_score = min(search_views / max_views, 1.0) * 100
        recommendation_score = min(recommendation_views / max_views, 1.0) * 100
        
        discovery_score = (
            organic_score * organic_weight +
            search_score * search_weight +
            recommendation_score * recommendation_weight
        )
        
        return min(discovery_score, 100.0)
        
    async def _collect_monetization_metrics(
        self,
        content_id: Optional[str],
        content_type: Optional[str],
        start_date: datetime,
        end_date: datetime
    ) -> List[ContentMetric]:
        """Collect content monetization performance metrics."""
        
        async with get_database_session() as session:
            # Monetization query
            monetization_query = select(
                Content.id,
                Content.content_type,
                func.sum(ContentRevenue.amount).label('total_revenue'),
                func.count(ContentRevenue.id).label('revenue_events'),
                func.avg(ContentRevenue.amount).label('avg_revenue_per_event'),
                func.count(ContentView.id).label('total_views')
            ).outerjoin(ContentRevenue).outerjoin(ContentView).where(
                and_(
                    Content.created_at >= start_date,
                    or_(
                        ContentRevenue.created_at.is_(None),
                        ContentRevenue.created_at >= start_date
                    )
                )
            ).group_by(Content.id, Content.content_type)
            
            if content_id:
                monetization_query = monetization_query.where(Content.id == content_id)
            if content_type:
                monetization_query = monetization_query.where(Content.content_type == content_type)
                
            result = await session.execute(monetization_query)
            monetization_data = result.fetchall()
            
            metrics = []
            
            for row in monetization_data:
                cid = row.id
                total_revenue = row.total_revenue or 0
                revenue_events = row.revenue_events or 0
                avg_revenue = row.avg_revenue_per_event or 0
                total_views = row.total_views or 0
                
                # Revenue per view (RPV)
                revenue_per_view = total_revenue / max(total_views, 1)
                
                # Monetization efficiency
                monetization_efficiency = min(revenue_per_view * 1000, 100)  # Normalize
                
                # Revenue potential score
                revenue_potential = self._calculate_revenue_potential(
                    total_revenue, total_views, revenue_events
                )
                
                metrics.extend([
                    ContentMetric(
                        content_id=cid,
                        metric_name="total_revenue",
                        value=total_revenue,
                        category=ContentCategory.MONETIZATION,
                        timestamp=datetime.now(),
                        content_type=row.content_type,
                        metadata={
                            "currency": "EUR",
                            "revenue_events": revenue_events
                        }
                    ),
                    ContentMetric(
                        content_id=cid,
                        metric_name="revenue_per_view",
                        value=revenue_per_view,
                        category=ContentCategory.MONETIZATION,
                        timestamp=datetime.now(),
                        content_type=row.content_type
                    ),
                    ContentMetric(
                        content_id=cid,
                        metric_name="monetization_efficiency",
                        value=monetization_efficiency,
                        category=ContentCategory.MONETIZATION,
                        timestamp=datetime.now(),
                        content_type=row.content_type
                    ),
                    ContentMetric(
                        content_id=cid,
                        metric_name="revenue_potential_score",
                        value=revenue_potential,
                        category=ContentCategory.MONETIZATION,
                        timestamp=datetime.now(),
                        content_type=row.content_type
                    )
                ])
                
            return metrics
            
    def _calculate_revenue_potential(
        self,
        total_revenue: float,
        total_views: int,
        revenue_events: int
    ) -> float:
        """Calculate content revenue potential score."""
        
        if total_views == 0:
            return 0.0
            
        # Factors for revenue potential
        rpv = total_revenue / total_views  # Revenue per view
        conversion_rate = revenue_events / total_views  # Revenue event conversion
        
        # Normalize and weight
        rpv_score = min(rpv * 10000, 100)  # Normalize RPV
        conversion_score = min(conversion_rate * 1000, 100)  # Normalize conversion
        
        # Weighted potential score
        potential_score = (rpv_score * 0.6) + (conversion_score * 0.4)
        
        return min(potential_score, 100.0)
        
    async def _collect_quality_metrics(
        self,
        content_id: Optional[str],
        content_type: Optional[str],
        start_date: datetime,
        end_date: datetime
    ) -> List[ContentMetric]:
        """Collect content quality and technical metrics."""
        
        async with get_database_session() as session:
            # Quality metrics query
            quality_query = select(
                Content.id,
                Content.content_type,
                Content.file_size,
                Content.duration,
                Content.quality_score,
                Content.metadata,
                func.avg(ContentView.completion_rate).label('avg_completion_rate'),
                func.count(
                    case(
                        (ContentInteraction.interaction_type == 'report', 1),
                        else_=None
                    )
                ).label('report_count')
            ).outerjoin(ContentView).outerjoin(ContentInteraction).where(
                Content.created_at >= start_date
            ).group_by(
                Content.id, Content.content_type, Content.file_size,
                Content.duration, Content.quality_score, Content.metadata
            )
            
            if content_id:
                quality_query = quality_query.where(Content.id == content_id)
            if content_type:
                quality_query = quality_query.where(Content.content_type == content_type)
                
            result = await session.execute(quality_query)
            quality_data = result.fetchall()
            
            metrics = []
            
            for row in quality_data:
                cid = row.id
                file_size = row.file_size or 0
                duration = row.duration or 0
                quality_score = row.quality_score or 0
                completion_rate = row.avg_completion_rate or 0
                report_count = row.report_count or 0
                
                # Technical quality score
                technical_quality = self._calculate_technical_quality(
                    file_size, duration, row.content_type
                )
                
                # Content safety score
                safety_score = max(100 - (report_count * 10), 0)
                
                # Overall quality score
                overall_quality = (
                    quality_score * 0.4 +
                    technical_quality * 0.3 +
                    completion_rate * 100 * 0.2 +
                    safety_score * 0.1
                )
                
                metrics.extend([
                    ContentMetric(
                        content_id=cid,
                        metric_name="technical_quality_score",
                        value=technical_quality,
                        category=ContentCategory.QUALITY,
                        timestamp=datetime.now(),
                        content_type=row.content_type,
                        metadata={
                            "file_size": file_size,
                            "duration": duration
                        }
                    ),
                    ContentMetric(
                        content_id=cid,
                        metric_name="content_safety_score",
                        value=safety_score,
                        category=ContentCategory.QUALITY,
                        timestamp=datetime.now(),
                        content_type=row.content_type,
                        metadata={
                            "report_count": report_count
                        }
                    ),
                    ContentMetric(
                        content_id=cid,
                        metric_name="overall_quality_score",
                        value=overall_quality,
                        category=ContentCategory.QUALITY,
                        timestamp=datetime.now(),
                        content_type=row.content_type
                    ),
                    ContentMetric(
                        content_id=cid,
                        metric_name="completion_rate",
                        value=completion_rate * 100,
                        category=ContentCategory.QUALITY,
                        timestamp=datetime.now(),
                        content_type=row.content_type
                    )
                ])
                
            return metrics
            
    def _calculate_technical_quality(
        self,
        file_size: int,
        duration: float,
        content_type: str
    ) -> float:
        """Calculate technical quality score based on file characteristics."""
        
        quality_score = 50.0  # Base score
        
        # File size quality (bitrate estimation)
        if content_type == 'audio':
            # Good audio: 128-320 kbps
            if duration > 0:
                bitrate = (file_size * 8) / (duration * 1000)  # kbps
                if 128 <= bitrate <= 320:
                    quality_score += 30
                elif bitrate > 320:
                    quality_score += 20
                elif bitrate < 128:
                    quality_score -= 20
                    
        elif content_type == 'video':
            # Good video: 1-5 Mbps
            if duration > 0:
                bitrate = (file_size * 8) / (duration * 1000000)  # Mbps
                if 1 <= bitrate <= 5:
                    quality_score += 30
                elif bitrate > 5:
                    quality_score += 20
                elif bitrate < 1:
                    quality_score -= 20
                    
        elif content_type == 'image':
            # Good image: 100KB - 5MB
            if 100000 <= file_size <= 5000000:
                quality_score += 30
            elif file_size > 5000000:
                quality_score += 10
            elif file_size < 100000:
                quality_score -= 10
                
        # Duration quality
        if content_type in ['audio', 'video']:
            if 30 <= duration <= 600:  # 30 sec - 10 min optimal
                quality_score += 20
            elif duration > 600:
                quality_score += 10
            elif duration < 30:
                quality_score -= 10
                
        return max(min(quality_score, 100.0), 0.0)
        
    async def generate_content_performance_profiles(
        self,
        content_ids: Optional[List[str]] = None
    ) -> List[ContentPerformanceProfile]:
        """Generate comprehensive content performance profiles."""



        
        try:
            # Collect all content metrics
            content_metrics = await self.collect_content_analytics()
            
            # Group metrics by content
            content_metric_groups = defaultdict(list)
            for metric in content_metrics:
                content_metric_groups[metric.content_id].append(metric)
                
            profiles = []
            
            for cid, metrics in content_metric_groups.items():
                if content_ids and cid not in content_ids:
                    continue
                    
                # Extract content information
                content_info = await self._get_content_info(cid)
                if not content_info:
                    continue
                    
                # Calculate profile components
                performance_score = self._extract_metric_value(metrics, "performance_score")
                protection_effectiveness = self._extract_metric_value(
                    metrics, "protection_effectiveness"
                )
                revenue_potential = self._extract_metric_value(
                    metrics, "revenue_potential_score"
                )
                
                # Engagement metrics
                engagement_metrics = {
                    "engagement_rate": self._extract_metric_value(metrics, "engagement_rate"),
                    "completion_rate": self._extract_metric_value(metrics, "completion_rate"),
                    "viral_coefficient": self._extract_metric_value(metrics, "viral_coefficient")
                }
                
                # Generate optimization recommendations
                recommendations = self._generate_optimization_recommendations(metrics)
                
                profile = ContentPerformanceProfile(
                    content_id=cid,
                    title=content_info.get('title', 'Unknown'),
                    content_type=content_info.get('content_type', 'unknown'),
                    performance_score=performance_score,
                    protection_effectiveness=protection_effectiveness,
                    revenue_potential=revenue_potential,
                    engagement_metrics=engagement_metrics,
                    optimization_recommendations=recommendations,
                    last_updated=datetime.now()
                )
                
                profiles.append(profile)
                
            self.logger.info(f"Generated {len(profiles)} content performance profiles")
            return profiles
            
        except Exception as e:
            self.logger.error(f"Error generating content profiles: {e}")
            raise
            
    async def _get_content_info(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get basic content information."""
        
        async with get_database_session() as session:
            query = select(Content.title, Content.content_type).where(
                Content.id == content_id
            )
            result = await session.execute(query)
            row = result.first()
            
            if row:
                return {
                    'title': row.title,
                    'content_type': row.content_type
                }
            return None
            
    def _extract_metric_value(self, metrics: List[ContentMetric], metric_name: str) -> float:
        """Extract specific metric value from metrics list."""
        
        for metric in metrics:
            if metric.metric_name == metric_name:
                return metric.value
        return 0.0
        
    def _generate_optimization_recommendations(
        self,
        metrics: List[ContentMetric]
    ) -> List[str]:
        """Generate optimization recommendations based on metrics."""
        
        recommendations = []
        
        # Performance optimization
        performance_score = self._extract_metric_value(metrics, "performance_score")
        if performance_score < self._performance_thresholds['medium_performance']:
            recommendations.append("Improve content quality and engagement tactics")
            
        # SEO optimization
        search_optimization = self._extract_metric_value(metrics, "search_optimization_score")
        if search_optimization < 30:
            recommendations.append("Optimize tags and metadata for better discoverability")
            
        # Protection optimization
        protection_effectiveness = self._extract_metric_value(metrics, "protection_effectiveness")
        if protection_effectiveness < 80:
            recommendations.append("Enhance content protection with additional fingerprints")
            
        # Monetization optimization
        revenue_potential = self._extract_metric_value(metrics, "revenue_potential_score")
        if revenue_potential < 40:
            recommendations.append("Explore additional monetization strategies")
            
        # Engagement optimization
        engagement_rate = self._extract_metric_value(metrics, "engagement_rate")
        if engagement_rate < 5:
            recommendations.append("Improve content engagement with interactive elements")
            
        return recommendations
