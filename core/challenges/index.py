"""
Challenge Index Manager - Centralized Challenge Discovery and Management

This module provides centralized indexing and discovery capabilities for all
challenge-related operations across the Ainflue platform.

Features:
- Centralized challenge registry and discovery
- Real-time challenge status tracking
- Challenge category management and filtering
- Performance metrics and analytics integration
- Cross-reference with creator collaboration workflows
- Multi-tenant challenge organization
- Challenge template management
- Integration with monetization systems

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  STRICT COPYRIGHT WARNING ⚠️
This code, concept, and intellectual property belong exclusively to Fahed Mlaiel.
Any unauthorized use, copying, distribution, or theft of this code or concept
without explicit written permission from Fahed Mlaiel is strictly prohibited
and will result in immediate legal action.

Contact: mlaiel@live.de for authorized usage inquiries.
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timezone
import asyncio
import logging

logger = logging.getLogger(__name__)


class ChallengeCategory(Enum):
    """Professional challenge categorization"""
    CONTENT_CREATION = "content_creation"
    COLLABORATION = "collaboration"
    REVENUE_OPTIMIZATION = "revenue_optimization"
    AUDIENCE_GROWTH = "audience_growth"
    QUALITY_IMPROVEMENT = "quality_improvement"
    INNOVATION = "innovation"
    SEO_OPTIMIZATION = "seo_optimization"
    CROSS_PLATFORM = "cross_platform"
    PROTECTION_COMPLIANCE = "protection_compliance"
    MONETIZATION = "monetization"


class ChallengeIndexStatus(Enum):
    """Challenge index entry status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    FEATURED = "featured"
    PREMIUM = "premium"


@dataclass
class ChallengeIndexEntry:
    """Challenge index entry with comprehensive metadata"""
    challenge_id: str
    title: str
    category: ChallengeCategory
    status: ChallengeIndexStatus
    creator_id: str
    created_at: datetime
    updated_at: datetime
    participant_count: int
    completion_rate: float
    average_score: float
    revenue_impact: float
    tags: Set[str]
    prerequisites: List[str]
    rewards: Dict[str, Any]
    metadata: Dict[str, Any]


@dataclass
class ChallengeDiscoveryFilter:
    """Challenge discovery filtering configuration"""
    categories: Optional[List[ChallengeCategory]] = None
    status: Optional[List[ChallengeIndexStatus]] = None
    min_participants: Optional[int] = None
    max_participants: Optional[int] = None
    min_completion_rate: Optional[float] = None
    creator_level_required: Optional[int] = None
    tags: Optional[Set[str]] = None
    date_range: Optional[tuple] = None
    revenue_threshold: Optional[float] = None


class ChallengeIndexManager:
    """
    Enterprise-grade challenge index and discovery management system
    
    Provides centralized registry, discovery, and analytics for all platform challenges
    with advanced filtering, performance tracking, and business intelligence capabilities.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize challenge index manager with configuration"""
        self.config = config or {}
        
        # Core registries
        self._challenge_index: Dict[str, ChallengeIndexEntry] = {}
        self._category_index: Dict[ChallengeCategory, Set[str]] = {
            category: set() for category in ChallengeCategory
        }
        self._creator_index: Dict[str, Set[str]] = {}
        self._tag_index: Dict[str, Set[str]] = {}
        
        # Performance tracking
        self._performance_metrics: Dict[str, Dict[str, Any]] = {}
        self._trend_analysis: Dict[str, List[float]] = {}
        
        # Configuration
        self.max_entries = self.config.get('max_entries', 10000)
        self.cache_duration = self.config.get('cache_duration_minutes', 60)
        self.analytics_enabled = self.config.get('analytics_enabled', True)
        
        logger.info("Challenge Index Manager initialized successfully")
    
    async def register_challenge(
        self,
        challenge_id: str,
        challenge_data: Dict[str, Any]
    ) -> bool:
        """Register a new challenge in the index"""
        try:
            if challenge_id in self._challenge_index:
                logger.warning(f"Challenge {challenge_id} already registered")
                return False
            
            # Create index entry
            entry = ChallengeIndexEntry(
                challenge_id=challenge_id,
                title=challenge_data.get('title', ''),
                category=ChallengeCategory(challenge_data.get('category', 'content_creation')),
                status=ChallengeIndexStatus(challenge_data.get('status', 'active')),
                creator_id=challenge_data.get('creator_id', ''),
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                participant_count=0,
                completion_rate=0.0,
                average_score=0.0,
                revenue_impact=0.0,
                tags=set(challenge_data.get('tags', [])),
                prerequisites=challenge_data.get('prerequisites', []),
                rewards=challenge_data.get('rewards', {}),
                metadata=challenge_data.get('metadata', {})
            )
            
            # Register in indices
            self._challenge_index[challenge_id] = entry
            self._category_index[entry.category].add(challenge_id)
            
            # Creator index
            if entry.creator_id not in self._creator_index:
                self._creator_index[entry.creator_id] = set()
            self._creator_index[entry.creator_id].add(challenge_id)
            
            # Tag index
            for tag in entry.tags:
                if tag not in self._tag_index:
                    self._tag_index[tag] = set()
                self._tag_index[tag].add(challenge_id)
            
            logger.info(f"Challenge {challenge_id} registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error registering challenge {challenge_id}: {e}")
            return False
    
    async def discover_challenges(
        self,
        filters: Optional[ChallengeDiscoveryFilter] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[ChallengeIndexEntry]:
        """Discover challenges based on filters"""
        try:
            # Start with all challenges
            candidate_ids = set(self._challenge_index.keys())
            
            if filters:
                # Apply category filter
                if filters.categories:
                    category_matches = set()
                    for category in filters.categories:
                        category_matches.update(self._category_index[category])
                    candidate_ids &= category_matches
                
                # Apply status filter
                if filters.status:
                    status_matches = {
                        cid for cid, entry in self._challenge_index.items()
                        if entry.status in filters.status
                    }
                    candidate_ids &= status_matches
                
                # Apply participant count filter
                if filters.min_participants is not None:
                    participant_matches = {
                        cid for cid, entry in self._challenge_index.items()
                        if entry.participant_count >= filters.min_participants
                    }
                    candidate_ids &= participant_matches
                
                if filters.max_participants is not None:
                    participant_matches = {
                        cid for cid, entry in self._challenge_index.items()
                        if entry.participant_count <= filters.max_participants
                    }
                    candidate_ids &= participant_matches
                
                # Apply completion rate filter
                if filters.min_completion_rate is not None:
                    completion_matches = {
                        cid for cid, entry in self._challenge_index.items()
                        if entry.completion_rate >= filters.min_completion_rate
                    }
                    candidate_ids &= completion_matches
                
                # Apply tag filter
                if filters.tags:
                    tag_matches = set()
                    for tag in filters.tags:
                        if tag in self._tag_index:
                            tag_matches.update(self._tag_index[tag])
                    candidate_ids &= tag_matches
                
                # Apply revenue threshold filter
                if filters.revenue_threshold is not None:
                    revenue_matches = {
                        cid for cid, entry in self._challenge_index.items()
                        if entry.revenue_impact >= filters.revenue_threshold
                    }
                    candidate_ids &= revenue_matches
            
            # Convert to entries and sort
            results = [self._challenge_index[cid] for cid in candidate_ids]
            
            # Sort by relevance (participant count + completion rate + revenue impact)
            results.sort(
                key=lambda x: (x.participant_count * 0.3 + 
                              x.completion_rate * 0.3 + 
                              x.revenue_impact * 0.4),
                reverse=True
            )
            
            # Apply pagination
            return results[offset:offset + limit]
            
        except Exception as e:
            logger.error(f"Error discovering challenges: {e}")
            return []
    
    async def get_challenge_analytics(
        self,
        challenge_id: str
    ) -> Dict[str, Any]:
        """Get comprehensive analytics for a challenge"""
        try:
            if challenge_id not in self._challenge_index:
                return {}
            
            entry = self._challenge_index[challenge_id]
            
            analytics = {
                'basic_metrics': {
                    'participant_count': entry.participant_count,
                    'completion_rate': entry.completion_rate,
                    'average_score': entry.average_score,
                    'revenue_impact': entry.revenue_impact
                },
                'performance_trends': self._trend_analysis.get(challenge_id, []),
                'category_ranking': await self._get_category_ranking(challenge_id),
                'engagement_metrics': self._performance_metrics.get(challenge_id, {}),
                'recommendations': await self._generate_recommendations(challenge_id)
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting analytics for challenge {challenge_id}: {e}")
            return {}
    
    async def update_challenge_metrics(
        self,
        challenge_id: str,
        metrics: Dict[str, Any]
    ) -> bool:
        """Update challenge performance metrics"""
        try:
            if challenge_id not in self._challenge_index:
                return False
            
            entry = self._challenge_index[challenge_id]
            
            # Update metrics
            if 'participant_count' in metrics:
                entry.participant_count = metrics['participant_count']
            
            if 'completion_rate' in metrics:
                entry.completion_rate = metrics['completion_rate']
            
            if 'average_score' in metrics:
                entry.average_score = metrics['average_score']
            
            if 'revenue_impact' in metrics:
                entry.revenue_impact = metrics['revenue_impact']
            
            entry.updated_at = datetime.now(timezone.utc)
            
            # Update performance tracking
            if self.analytics_enabled:
                if challenge_id not in self._performance_metrics:
                    self._performance_metrics[challenge_id] = {}
                
                self._performance_metrics[challenge_id].update(metrics)
                
                # Update trends
                if challenge_id not in self._trend_analysis:
                    self._trend_analysis[challenge_id] = []
                
                trend_score = (
                    entry.participant_count * 0.3 +
                    entry.completion_rate * 0.3 +
                    entry.revenue_impact * 0.4
                )
                
                self._trend_analysis[challenge_id].append(trend_score)
                
                # Keep only last 30 data points
                if len(self._trend_analysis[challenge_id]) > 30:
                    self._trend_analysis[challenge_id] = self._trend_analysis[challenge_id][-30:]
            
            logger.info(f"Metrics updated for challenge {challenge_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating metrics for challenge {challenge_id}: {e}")
            return False
    
    async def get_trending_challenges(
        self,
        category: Optional[ChallengeCategory] = None,
        limit: int = 10
    ) -> List[ChallengeIndexEntry]:
        """Get trending challenges based on recent performance"""
        try:
            # Filter by category if specified
            if category:
                candidate_ids = self._category_index[category]
            else:
                candidate_ids = set(self._challenge_index.keys())
            
            # Calculate trend scores
            trending_challenges = []
            for challenge_id in candidate_ids:
                entry = self._challenge_index[challenge_id]
                
                # Calculate trend based on recent performance
                trend_data = self._trend_analysis.get(challenge_id, [])
                if len(trend_data) >= 2:
                    recent_trend = (trend_data[-1] - trend_data[-2]) / max(trend_data[-2], 0.1)
                else:
                    recent_trend = 0.0
                
                trending_challenges.append((entry, recent_trend))
            
            # Sort by trend score
            trending_challenges.sort(key=lambda x: x[1], reverse=True)
            
            # Return top entries
            return [entry for entry, _ in trending_challenges[:limit]]
            
        except Exception as e:
            logger.error(f"Error getting trending challenges: {e}")
            return []
    
    async def _get_category_ranking(self, challenge_id: str) -> int:
        """Get challenge ranking within its category"""
        try:
            entry = self._challenge_index[challenge_id]
            category_challenges = [
                self._challenge_index[cid] 
                for cid in self._category_index[entry.category]
            ]
            
            # Sort by performance score
            category_challenges.sort(
                key=lambda x: (x.participant_count * 0.3 + 
                              x.completion_rate * 0.3 + 
                              x.revenue_impact * 0.4),
                reverse=True
            )
            
            for i, challenge in enumerate(category_challenges):
                if challenge.challenge_id == challenge_id:
                    return i + 1
            
            return len(category_challenges)
            
        except Exception as e:
            logger.error(f"Error calculating category ranking: {e}")
            return 0
    
    async def _generate_recommendations(self, challenge_id: str) -> List[str]:
        """Generate improvement recommendations for a challenge"""
        try:
            entry = self._challenge_index[challenge_id]
            recommendations = []
            
            # Participant count recommendations
            if entry.participant_count < 10:
                recommendations.append("Increase challenge visibility through featured placement")
            
            # Completion rate recommendations
            if entry.completion_rate < 0.3:
                recommendations.append("Review challenge difficulty and adjust requirements")
            
            # Revenue impact recommendations
            if entry.revenue_impact < 100:
                recommendations.append("Enhance rewards to increase monetization potential")
            
            # Engagement recommendations
            if entry.average_score < 70:
                recommendations.append("Improve challenge content quality and engagement factors")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []
    
    def get_index_statistics(self) -> Dict[str, Any]:
        """Get comprehensive index statistics"""
        try:
            total_challenges = len(self._challenge_index)
            
            # Category distribution
            category_stats = {
                category.value: len(challenge_ids)
                for category, challenge_ids in self._category_index.items()
            }
            
            # Status distribution
            status_stats = {}
            for entry in self._challenge_index.values():
                status = entry.status.value
                status_stats[status] = status_stats.get(status, 0) + 1
            
            # Performance averages
            if total_challenges > 0:
                avg_participants = sum(
                    entry.participant_count for entry in self._challenge_index.values()
                ) / total_challenges
                
                avg_completion = sum(
                    entry.completion_rate for entry in self._challenge_index.values()
                ) / total_challenges
                
                avg_revenue = sum(
                    entry.revenue_impact for entry in self._challenge_index.values()
                ) / total_challenges
            else:
                avg_participants = avg_completion = avg_revenue = 0.0
            
            return {
                'total_challenges': total_challenges,
                'category_distribution': category_stats,
                'status_distribution': status_stats,
                'performance_averages': {
                    'participants': avg_participants,
                    'completion_rate': avg_completion,
                    'revenue_impact': avg_revenue
                },
                'total_creators': len(self._creator_index),
                'total_tags': len(self._tag_index)
            }
            
        except Exception as e:
            logger.error(f"Error calculating index statistics: {e}")
            return {}