"""Cross Platform Events Module

Advanced cross-platform analytics and unification for multi-format content creators.
Provides comprehensive platform synchronization, unified analytics, and optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel - All rights reserved
⚠️  WARNING: This code and concept are proprietary to Fahed Mlaiel.
    Any unauthorized use, copying, or distribution without explicit written 
    permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.

Team Expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
                Microservices + Audio + DevOps + IA Prompt Engineer
"""import asyncio
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx
from scipy import stats
import aiohttp
import hashlib

from ...core.events.base_event import BaseEvent, BaseEventHandler
from ...core.cache import CacheManager
from ...core.database import DatabaseManager
from ...core.logging import get_logger
from ...ml.models.platform_predictor import PlatformPerformancePredictor
from ...ai.unification.content_unifier import ContentUnificationEngine
from ...utils.metrics import MetricsCalculator
from ...config import settings

logger = get_logger(__name__)


class SupportedPlatform(Enum):
    """Supported platforms for cross-platform analytics"""    SPOTIFY = "spotify"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"
    TWITCH = "twitch"
    DISCORD = "discord"
    PATREON = "patreon"
    ONLYFANS = "onlyfans"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    REDDIT = "reddit"
    CLUBHOUSE = "clubhouse"
    MEDIUM = "medium"
    SUBSTACK = "substack"
    GITHUB = "github"


class PlatformCategory(Enum):
    """Categories of platforms"""    SOCIAL_MEDIA = "social_media"
    MUSIC_STREAMING = "music_streaming"
    VIDEO_STREAMING = "video_streaming"
    CONTENT_PUBLISHING = "content_publishing"
    CREATOR_ECONOMY = "creator_economy"
    PROFESSIONAL = "professional"
    GAMING = "gaming"
    COMMUNITY = "community"
    MONETIZATION = "monetization"


class SyncAction(Enum):
    """Types of synchronization actions"""    CONTENT_PUBLISH = "content_publish"
    METADATA_UPDATE = "metadata_update"
    CROSS_PROMOTE = "cross_promote"
    AUDIENCE_SYNC = "audience_sync"
    ANALYTICS_SYNC = "analytics_sync"
    ENGAGEMENT_SYNC = "engagement_sync"
    REVENUE_SYNC = "revenue_sync"
    PROFILE_SYNC = "profile_sync"


class UnificationStrategy(Enum):
    """Strategies for platform unification"""    CONTENT_FIRST = "content_first"
    AUDIENCE_FIRST = "audience_first"
    ENGAGEMENT_FIRST = "engagement_first"
    REVENUE_FIRST = "revenue_first"
    GROWTH_FIRST = "growth_first"
    BALANCED = "balanced"


@dataclass
class CrossPlatformEvent(BaseEvent):
    """Represents a cross-platform analytics event"""    creator_id: str
    platforms: List[SupportedPlatform]
    sync_action: SyncAction
    primary_platform: SupportedPlatform
    secondary_platforms: List[SupportedPlatform]
    content_metadata: Dict[str, Any]
    platform_metrics: Dict[str, Dict[str, Any]]
    unification_data: Dict[str, Any]
    sync_timestamp: datetime
    correlation_analysis: Optional[Dict[str, Any]] = None
    cross_promotion_data: Optional[Dict[str, Any]] = None
    audience_overlap: Optional[Dict[str, float]] = None
    performance_comparison: Optional[Dict[str, Any]] = None
    optimization_recommendations: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert cross-platform event to dictionary"""        return {
            **asdict(self),
            'platforms': [p.value for p in self.platforms],
            'sync_action': self.sync_action.value,
            'primary_platform': self.primary_platform.value,
            'secondary_platforms': [p.value for p in self.secondary_platforms],
            'sync_timestamp': self.sync_timestamp.isoformat()
        }


@dataclass
class PlatformProfile:
    """Profile of a creator's presence on a platform"""    platform: SupportedPlatform
    creator_id: str
    platform_user_id: str
    follower_count: int
    content_count: int
    engagement_rate: float
    growth_rate: float
    revenue: float
    content_types: List[str]
    posting_frequency: float
    optimal_posting_times: List[str]
    audience_demographics: Dict[str, Any]
    performance_metrics: Dict[str, float]
    api_credentials: Optional[Dict[str, str]] = None
    last_sync: Optional[datetime] = None
    is_active: bool = True


@dataclass
class UnificationResult:
    """Result of platform unification process"""    creator_id: str
    unified_metrics: Dict[str, Any]
    platform_correlations: Dict[str, float]
    content_performance_unified: Dict[str, Any]
    audience_unified: Dict[str, Any]
    revenue_unified: Dict[str, float]
    optimization_opportunities: List[str]
    sync_recommendations: List[str]
    unified_strategy: UnificationStrategy
    confidence_score: float
    created_at: datetime


class CrossPlatformEventHandler(BaseEventHandler):
    """Handles cross-platform events with advanced unification"""    
    def __init__(self):
        super().__init__()
        self.cache_manager = CacheManager()
        self.db_manager = DatabaseManager()
        self.platform_tracker = CrossPlatformTracker()
        self.unification_engine = PlatformUnificationEngine()
        self.analyzer = CrossPlatformAnalyzer()
        self.sync_engine = PlatformSyncEngine()
        
    async def handle(self, event: CrossPlatformEvent) -> Dict[str, Any]:
        """Process cross-platform event with comprehensive analysis"""        try:
            # Validate event data
            await self._validate_event(event)
            
            # Store cross-platform data
            await self._store_cross_platform_data(event)
            
            # Track platform metrics
            platform_tracking = await self.platform_tracker.track_platforms(event)
            
            # Unify platform data
            unification_result = await self.unification_engine.unify_platforms(event)
            
            # Analyze cross-platform correlations
            correlation_analysis = await self.analyzer.analyze_correlations(event)
            
            # Synchronize platforms
            sync_results = await self.sync_engine.sync_platforms(event)
            
            # Calculate platform efficiency
            efficiency_metrics = await self._calculate_platform_efficiency(event)
            
            # Generate optimization recommendations
            optimizations = await self._generate_platform_optimizations(event)
            
            # Update unified dashboard
            await self._update_unified_dashboard(event, unification_result)
            
            return {
                'status': 'success',
                'event_id': event.event_id,
                'platform_tracking': platform_tracking,
                'unification_result': unification_result,
                'correlation_analysis': correlation_analysis,
                'sync_results': sync_results,
                'efficiency_metrics': efficiency_metrics,
                'optimizations': optimizations,
                'processing_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing cross-platform event: {str(e)}")
            await self._handle_error(event, e)
            raise
    
    async def _validate_event(self, event: CrossPlatformEvent) -> None:
        """Validate cross-platform event data"""        required_fields = ['creator_id', 'platforms', 'sync_action', 'primary_platform']
        for field in required_fields:
            if not getattr(event, field):
                raise ValueError(f"Missing required field: {field}")
        
        # Validate platforms
        for platform in event.platforms:
            if platform not in SupportedPlatform:
                raise ValueError(f"Invalid platform: {platform}")
        
        if event.primary_platform not in event.platforms:
            raise ValueError("Primary platform must be in platforms list")
    
    async def _store_cross_platform_data(self, event: CrossPlatformEvent) -> None:
        """Store cross-platform data in database"""        async with self.db_manager.get_session() as session:
            await session.execute(
                """                INSERT INTO cross_platform_events 
                (event_id, creator_id, platforms, sync_action, primary_platform,
                 secondary_platforms, content_metadata, platform_metrics,
                 unification_data, sync_timestamp, correlation_analysis,
                 cross_promotion_data, audience_overlap, performance_comparison,
                 optimization_recommendations)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    event.event_id, event.creator_id,
                    json.dumps([p.value for p in event.platforms]),
                    event.sync_action.value, event.primary_platform.value,
                    json.dumps([p.value for p in event.secondary_platforms]),
                    json.dumps(event.content_metadata),
                    json.dumps(event.platform_metrics),
                    json.dumps(event.unification_data), event.sync_timestamp,
                    json.dumps(event.correlation_analysis),
                    json.dumps(event.cross_promotion_data),
                    json.dumps(event.audience_overlap),
                    json.dumps(event.performance_comparison),
                    json.dumps(event.optimization_recommendations)
                )
            )
    
    async def _calculate_platform_efficiency(self, event: CrossPlatformEvent) -> Dict[str, Any]:
        """Calculate efficiency metrics across platforms"""        platform_metrics = event.platform_metrics
        
        efficiency_scores = {}
        for platform_name, metrics in platform_metrics.items():
            # Calculate ROI-based efficiency
            content_count = metrics.get('content_count', 1)
            engagement = metrics.get('total_engagement', 0)
            reach = metrics.get('total_reach', 1)
            time_spent = metrics.get('time_spent_hours', 1)
            
            # Efficiency calculations
            engagement_per_content = engagement / content_count
            reach_per_content = reach / content_count
            efficiency_per_hour = engagement / time_spent
            
            efficiency_scores[platform_name] = {
                'engagement_efficiency': engagement_per_content,
                'reach_efficiency': reach_per_content,
                'time_efficiency': efficiency_per_hour,
                'overall_efficiency': (engagement_per_content + reach_per_content + efficiency_per_hour) / 3
            }
        
        # Rank platforms by efficiency
        platform_ranking = sorted(
            efficiency_scores.items(),
            key=lambda x: x[1]['overall_efficiency'],
            reverse=True
        )
        
        return {
            'platform_efficiency_scores': efficiency_scores,
            'platform_ranking': platform_ranking,
            'most_efficient_platform': platform_ranking[0][0] if platform_ranking else None,
            'efficiency_improvement_opportunities': await self._identify_efficiency_improvements(event)
        }


class CrossPlatformTracker:
    """Tracks performance and metrics across multiple platforms"""    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.cache_manager = CacheManager()
        self.metrics_calculator = MetricsCalculator()
        
    async def track_platforms(self, event: CrossPlatformEvent) -> Dict[str, Any]:
        """Track comprehensive platform metrics"""        # Get platform profiles
        platform_profiles = await self._get_platform_profiles(event.creator_id)
        
        # Calculate unified metrics
        unified_metrics = await self._calculate_unified_metrics(event, platform_profiles)
        
        # Track growth trends across platforms
        growth_trends = await self._track_growth_trends(event.creator_id)
        
        # Calculate platform diversification
        diversification_metrics = await self._calculate_diversification_metrics(event)
        
        # Track content performance across platforms
        content_performance = await self._track_content_performance(event)
        
        # Calculate audience overlap
        audience_overlap = await self._calculate_audience_overlap(event.creator_id)
        
        return {
            'platform_profiles': platform_profiles,
            'unified_metrics': unified_metrics,
            'growth_trends': growth_trends,
            'diversification_metrics': diversification_metrics,
            'content_performance': content_performance,
            'audience_overlap': audience_overlap,
            'platform_health_scores': await self._calculate_platform_health_scores(event)
        }
    
    async def _get_platform_profiles(self, creator_id: str) -> Dict[str, PlatformProfile]:
        """Get creator's profiles across all platforms"""        async with self.db_manager.get_session() as session:
            result = await session.execute(
                """                SELECT platform, platform_user_id, follower_count, content_count,
                       engagement_rate, growth_rate, revenue, content_types,
                       posting_frequency, optimal_posting_times, audience_demographics,
                       performance_metrics, last_sync, is_active
                FROM platform_profiles 
                WHERE creator_id = %s AND is_active = true
                """,
                (creator_id,)
            )
            
            profiles = {}
            for row in result.fetchall():
                platform = SupportedPlatform(row[0])
                profiles[platform.value] = PlatformProfile(
                    platform=platform,
                    creator_id=creator_id,
                    platform_user_id=row[1],
                    follower_count=row[2],
                    content_count=row[3],
                    engagement_rate=row[4],
                    growth_rate=row[5],
                    revenue=row[6],
                    content_types=json.loads(row[7]) if row[7] else [],
                    posting_frequency=row[8],
                    optimal_posting_times=json.loads(row[9]) if row[9] else [],
                    audience_demographics=json.loads(row[10]) if row[10] else {},
                    performance_metrics=json.loads(row[11]) if row[11] else {},
                    last_sync=row[12],
                    is_active=row[13]
                )
            
            return profiles
    
    async def _calculate_unified_metrics(self, event: CrossPlatformEvent, 
                                       profiles: Dict[str, PlatformProfile]) -> Dict[str, Any]:
        """Calculate unified metrics across all platforms"""        total_followers = sum(profile.follower_count for profile in profiles.values())
        total_content = sum(profile.content_count for profile in profiles.values())
        total_revenue = sum(profile.revenue for profile in profiles.values())
        
        # Weighted engagement rate (by follower count)
        weighted_engagement = 0
        total_weight = 0
        for profile in profiles.values():
            weight = profile.follower_count
            weighted_engagement += profile.engagement_rate * weight
            total_weight += weight
        
        avg_engagement_rate = weighted_engagement / total_weight if total_weight > 0 else 0
        
        # Platform diversity index (Shannon diversity)
        platform_diversity = self._calculate_shannon_diversity(profiles)
        
        return {
            'total_followers': total_followers,
            'total_content_pieces': total_content,
            'total_revenue': total_revenue,
            'average_engagement_rate': avg_engagement_rate,
            'platform_count': len(profiles),
            'platform_diversity_index': platform_diversity,
            'revenue_per_follower': total_revenue / max(total_followers, 1),
            'content_per_platform': total_content / max(len(profiles), 1),
            'cross_platform_efficiency': await self._calculate_cross_platform_efficiency(profiles)
        }
    
    def _calculate_shannon_diversity(self, profiles: Dict[str, PlatformProfile]) -> float:
        """Calculate Shannon diversity index for platform distribution"""        total_followers = sum(profile.follower_count for profile in profiles.values())
        
        if total_followers == 0:
            return 0
        
        diversity = 0
        for profile in profiles.values():
            if profile.follower_count > 0:
                proportion = profile.follower_count / total_followers
                diversity -= proportion * np.log(proportion)
        
        return diversity


class PlatformUnificationEngine:
    """Unifies data and metrics across multiple platforms"""    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.content_unifier = ContentUnificationEngine()
        self.scaler = StandardScaler()
        
    async def unify_platforms(self, event: CrossPlatformEvent) -> UnificationResult:
        """Unify data across all platforms for comprehensive analysis"""        # Collect platform data
        platform_data = await self._collect_platform_data(event)
        
        # Unify content metrics
        unified_content = await self._unify_content_metrics(platform_data)
        
        # Unify audience metrics
        unified_audience = await self._unify_audience_metrics(platform_data)
        
        # Unify revenue metrics
        unified_revenue = await self._unify_revenue_metrics(platform_data)
        
        # Calculate platform correlations
        correlations = await self._calculate_platform_correlations(platform_data)
        
        # Determine optimal unification strategy
        optimal_strategy = await self._determine_optimal_strategy(event, platform_data)
        
        # Generate optimization opportunities
        optimizations = await self._identify_unification_optimizations(platform_data)
        
        # Calculate confidence score
        confidence = await self._calculate_unification_confidence(platform_data, correlations)
        
        return UnificationResult(
            creator_id=event.creator_id,
            unified_metrics={
                'content': unified_content,
                'audience': unified_audience,
                'revenue': unified_revenue
            },
            platform_correlations=correlations,
            content_performance_unified=unified_content,
            audience_unified=unified_audience,
            revenue_unified=unified_revenue,
            optimization_opportunities=optimizations,
            sync_recommendations=await self._generate_sync_recommendations(platform_data),
            unified_strategy=optimal_strategy,
            confidence_score=confidence,
            created_at=datetime.utcnow()
        )
    
    async def _collect_platform_data(self, event: CrossPlatformEvent) -> Dict[str, Dict[str, Any]]:
        """Collect comprehensive data from all platforms"""        platform_data = {}
        
        for platform in event.platforms:
            # Get cached data first
            cache_key = f"platform_data_{event.creator_id}_{platform.value}"
            cached_data = await self.cache_manager.get(cache_key)
            
            if cached_data:
                platform_data[platform.value] = cached_data
            else:
                # Fetch fresh data from platform APIs
                fresh_data = await self._fetch_platform_data(event.creator_id, platform)
                platform_data[platform.value] = fresh_data
                
                # Cache for 1 hour
                await self.cache_manager.set(cache_key, fresh_data, expires_in=3600)
        
        return platform_data
    
    async def _fetch_platform_data(self, creator_id: str, platform: SupportedPlatform) -> Dict[str, Any]:
        """Fetch data from specific platform API"""        # This would integrate with actual platform APIs
        # For now, return mock data structure
        
        async with self.db_manager.get_session() as session:
            result = await session.execute(
                """                SELECT performance_metrics, audience_metrics, content_metrics, revenue_metrics
                FROM platform_analytics 
                WHERE creator_id = %s AND platform = %s
                ORDER BY timestamp DESC
                LIMIT 1
                """,
                (creator_id, platform.value)
            )
            
            row = result.fetchone()
            if row:
                return {
                    'performance': json.loads(row[0]) if row[0] else {},
                    'audience': json.loads(row[1]) if row[1] else {},
                    'content': json.loads(row[2]) if row[2] else {},
                    'revenue': json.loads(row[3]) if row[3] else {}
                }
            else:
                return {
                    'performance': {},
                    'audience': {},
                    'content': {},
                    'revenue': {}
                }
    
    async def _unify_content_metrics(self, platform_data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Unify content metrics across platforms"""        total_content = 0
        total_views = 0
        total_engagement = 0
        content_types = set()
        
        for platform, data in platform_data.items():
            content_metrics = data.get('content', {})
            total_content += content_metrics.get('total_posts', 0)
            total_views += content_metrics.get('total_views', 0)
            total_engagement += content_metrics.get('total_engagement', 0)
            
            platform_content_types = content_metrics.get('content_types', [])
            content_types.update(platform_content_types)
        
        unified_engagement_rate = total_engagement / max(total_views, 1)
        
        return {
            'total_content_pieces': total_content,
            'total_views': total_views,
            'total_engagement': total_engagement,
            'unified_engagement_rate': unified_engagement_rate,
            'content_diversity': len(content_types),
            'content_types': list(content_types),
            'average_content_per_platform': total_content / max(len(platform_data), 1)
        }


class CrossPlatformAnalyzer:
    """Analyzes correlations and patterns across platforms"""    
    def __init__(self):
        self.db_manager = DatabaseManager()
        
    async def analyze_correlations(self, event: CrossPlatformEvent) -> Dict[str, Any]:
        """Analyze correlations between platform performances"""        # Get historical platform data
        historical_data = await self._get_historical_platform_data(event.creator_id)
        
        # Calculate correlation matrices
        correlation_matrices = await self._calculate_correlation_matrices(historical_data)
        
        # Identify strongest correlations
        strong_correlations = await self._identify_strong_correlations(correlation_matrices)
        
        # Analyze cross-platform influence
        influence_analysis = await self._analyze_cross_platform_influence(historical_data)
        
        # Calculate lag correlations
        lag_correlations = await self._calculate_lag_correlations(historical_data)
        
        # Identify leading and lagging platforms
        platform_relationships = await self._identify_platform_relationships(historical_data)
        
        return {
            'correlation_matrices': correlation_matrices,
            'strong_correlations': strong_correlations,
            'influence_analysis': influence_analysis,
            'lag_correlations': lag_correlations,
            'platform_relationships': platform_relationships,
            'cross_platform_insights': await self._generate_correlation_insights(correlation_matrices)
        }
    
    async def _get_historical_platform_data(self, creator_id: str) -> pd.DataFrame:
        """Get historical data for correlation analysis"""        async with self.db_manager.get_session() as session:
            result = await session.execute(
                """                SELECT platform, timestamp, performance_metrics, audience_metrics
                FROM platform_analytics 
                WHERE creator_id = %s 
                AND timestamp >= %s
                ORDER BY timestamp ASC
                """,
                (creator_id, datetime.utcnow() - timedelta(days=90))
            )
            
            data = []
            for row in result.fetchall():
                platform = row[0]
                timestamp = row[1]
                performance = json.loads(row[2]) if row[2] else {}
                audience = json.loads(row[3]) if row[3] else {}
                
                record = {
                    'platform': platform,
                    'timestamp': timestamp,
                    **{f"perf_{k}": v for k, v in performance.items()},
                    **{f"aud_{k}": v for k, v in audience.items()}
                }
                data.append(record)
            
            return pd.DataFrame(data)


class PlatformSyncEngine:
    """Synchronizes content and data across platforms"""    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.api_clients = {}  # Platform API clients
        
    async def sync_platforms(self, event: CrossPlatformEvent) -> Dict[str, Any]:
        """Synchronize data and content across platforms"""        sync_results = {}
        
        for platform in event.secondary_platforms:
            try:
                # Perform specific sync action
                if event.sync_action == SyncAction.CONTENT_PUBLISH:
                    result = await self._sync_content_publish(event, platform)
                elif event.sync_action == SyncAction.METADATA_UPDATE:
                    result = await self._sync_metadata_update(event, platform)
                elif event.sync_action == SyncAction.CROSS_PROMOTE:
                    result = await self._sync_cross_promotion(event, platform)
                elif event.sync_action == SyncAction.ANALYTICS_SYNC:
                    result = await self._sync_analytics(event, platform)
                else:
                    result = {'status': 'unsupported_action'}
                
                sync_results[platform.value] = result
                
            except Exception as e:
                logger.error(f"Error syncing {platform.value}: {str(e)}")
                sync_results[platform.value] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        # Update sync history
        await self._update_sync_history(event, sync_results)
        
        return {
            'sync_results': sync_results,
            'sync_summary': await self._generate_sync_summary(sync_results),
            'next_sync_recommendations': await self._generate_next_sync_recommendations(event)
        }
    
    async def _sync_content_publish(self, event: CrossPlatformEvent, 
                                  target_platform: SupportedPlatform) -> Dict[str, Any]:
        """Sync content publishing to target platform"""        content_metadata = event.content_metadata
        
        # Adapt content for target platform
        adapted_content = await self._adapt_content_for_platform(content_metadata, target_platform)
        
        # Schedule or publish content
        publish_result = await self._publish_to_platform(adapted_content, target_platform)
        
        return {
            'status': 'success' if publish_result['success'] else 'failed',
            'adapted_content': adapted_content,
            'publish_result': publish_result,
            'platform_specific_id': publish_result.get('content_id'),
            'sync_timestamp': datetime.utcnow().isoformat()
        }
    
    async def _adapt_content_for_platform(self, content: Dict[str, Any], 
                                        platform: SupportedPlatform) -> Dict[str, Any]:
        """Adapt content for specific platform requirements"""        adapted = content.copy()
        
        # Platform-specific adaptations
        if platform == SupportedPlatform.TWITTER:
            # Truncate for Twitter character limit
            if len(adapted.get('description', '')) > 280:
                adapted['description'] = adapted['description'][:277] + '...'
        
        elif platform == SupportedPlatform.INSTAGRAM:
            # Optimize for Instagram format
            adapted['hashtags'] = self._optimize_instagram_hashtags(adapted.get('hashtags', []))
        
        elif platform == SupportedPlatform.TIKTOK:
            # Optimize for TikTok trends
            adapted['hashtags'] = self._optimize_tiktok_hashtags(adapted.get('hashtags', []))
        
        elif platform == SupportedPlatform.LINKEDIN:
            # Professional formatting for LinkedIn
            adapted['description'] = self._format_for_linkedin(adapted.get('description', ''))
        
        return adapted
