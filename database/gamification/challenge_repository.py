"""
Challenge Repository - Enterprise Challenge Data Management

This module provides comprehensive data access layer for challenge management
with advanced repository patterns, real-time tracking, and analytics integration.

Features:
- High-performance challenge data access with optimized queries
- Real-time challenge progress tracking and updates
- Advanced challenge analytics and performance monitoring
- Challenge leaderboard management and caching
- Cross-platform challenge data synchronization
- Professional audit trails and data integrity
- Integration with scoring and validation systems
- Challenge lifecycle management and automation

Business Logic Integration:
- Challenge creation → Database persistence → Real-time tracking
- Challenge participation → Progress updates → Analytics collection
- Challenge completion → Result processing → Reward distribution
- Challenge performance → Business intelligence → Optimization insights

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  STRICT COPYRIGHT WARNING ⚠️
This code, concept, and intellectual property belong exclusively to Fahed Mlaiel.
Any unauthorized use, copying, distribution, or theft of this code or concept
without explicit written permission from Fahed Mlaiel is strictly prohibited
and will result in immediate legal action.

Contact: mlaiel@live.de for authorized usage inquiries.
"""

from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
import asyncio
import json
import logging

logger = logging.getLogger(__name__)


class ChallengeDataStatus(Enum):
    """Challenge data status"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


@dataclass
class ChallengeData:
    """Comprehensive challenge data model"""
    challenge_id: str
    title: str
    description: str
    challenge_type: str
    status: ChallengeDataStatus
    
    # Timing
    start_date: datetime
    end_date: datetime
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Participation
    max_participants: Optional[int] = None
    current_participants: int = 0
    entry_fee: float = 0.0
    
    # Requirements and rewards
    requirements: Dict[str, Any] = field(default_factory=dict)
    rewards: Dict[str, Any] = field(default_factory=dict)
    
    # Configuration
    difficulty: str = "intermediate"
    category: str = ""
    tags: List[str] = field(default_factory=list)
    
    # Performance metrics
    completion_rate: float = 0.0
    average_score: float = 0.0
    total_submissions: int = 0
    
    # Business metrics
    business_value: float = 0.0
    revenue_impact: float = 0.0
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChallengeParticipantData:
    """Challenge participant data"""
    user_id: str
    challenge_id: str
    username: str
    joined_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Progress
    current_score: float = 0.0
    current_rank: int = 0
    progress_percentage: float = 0.0
    submissions_count: int = 0
    
    # Status
    is_active: bool = True
    completion_status: str = "in_progress"  # in_progress, completed, withdrawn
    
    # Performance
    best_score: float = 0.0
    last_submission: Optional[datetime] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChallengeQuery:
    """Challenge query parameters"""
    challenge_ids: Optional[List[str]] = None
    statuses: Optional[List[ChallengeDataStatus]] = None
    challenge_types: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    
    # Participation filters
    min_participants: Optional[int] = None
    max_participants: Optional[int] = None
    has_space_available: bool = False
    
    # User-specific filters
    user_id: Optional[str] = None
    user_participating: bool = False
    user_completed: bool = False
    
    # Timing filters
    active_now: bool = False
    starting_after: Optional[datetime] = None
    ending_before: Optional[datetime] = None
    
    # Performance filters
    min_completion_rate: Optional[float] = None
    min_average_score: Optional[float] = None
    
    # Sorting and pagination
    sort_by: str = "created_at"
    sort_desc: bool = True
    limit: int = 50
    offset: int = 0
    
    # Includes
    include_participants: bool = False
    include_analytics: bool = False


class ChallengeRepository:
    """
    Enterprise-grade challenge repository with advanced data management
    
    Provides comprehensive challenge data access with high-performance
    querying, real-time tracking, analytics, and business intelligence.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize challenge repository"""
        self.config = config or {}
        
        # Core storage
        self._challenges: Dict[str, ChallengeData] = {}
        self._participants: Dict[str, Dict[str, ChallengeParticipantData]] = {}
        
        # Performance indices
        self._status_index: Dict[ChallengeDataStatus, Set[str]] = {
            status: set() for status in ChallengeDataStatus
        }
        self._type_index: Dict[str, Set[str]] = {}
        self._category_index: Dict[str, Set[str]] = {}
        self._tag_index: Dict[str, Set[str]] = {}
        self._user_index: Dict[str, Set[str]] = {}
        
        # Caching
        self._query_cache: Dict[str, Tuple[datetime, Any]] = {}
        self._leaderboard_cache: Dict[str, Tuple[datetime, List[Dict[str, Any]]]] = {}
        
        # Analytics
        self._challenge_analytics: Dict[str, Dict[str, Any]] = {}
        
        # Configuration
        self.cache_enabled = self.config.get('cache_enabled', True)
        self.cache_ttl_seconds = self.config.get('cache_ttl_seconds', 300)
        
        logger.info("Challenge Repository initialized successfully")
    
    async def create_challenge(self, challenge_data: ChallengeData) -> bool:
        """Create a new challenge"""
        try:
            challenge_id = challenge_data.challenge_id
            
            if challenge_id in self._challenges:
                logger.warning(f"Challenge {challenge_id} already exists")
                return False
            
            # Store challenge
            self._challenges[challenge_id] = challenge_data
            self._participants[challenge_id] = {}
            
            # Update indices
            await self._update_indices(challenge_data)
            
            # Initialize analytics
            await self._initialize_analytics(challenge_id)
            
            logger.info(f"Challenge {challenge_id} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating challenge: {e}")
            return False
    
    async def get_challenge(
        self,
        challenge_id: str,
        include_participants: bool = False,
        include_analytics: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Get challenge by ID"""
        try:
            if challenge_id not in self._challenges:
                return None
            
            challenge = self._challenges[challenge_id]
            
            result = {
                'challenge_id': challenge_id,
                'title': challenge.title,
                'description': challenge.description,
                'challenge_type': challenge.challenge_type,
                'status': challenge.status.value,
                'start_date': challenge.start_date.isoformat(),
                'end_date': challenge.end_date.isoformat(),
                'created_at': challenge.created_at.isoformat(),
                'updated_at': challenge.updated_at.isoformat(),
                'max_participants': challenge.max_participants,
                'current_participants': challenge.current_participants,
                'entry_fee': challenge.entry_fee,
                'requirements': challenge.requirements,
                'rewards': challenge.rewards,
                'difficulty': challenge.difficulty,
                'category': challenge.category,
                'tags': challenge.tags,
                'completion_rate': challenge.completion_rate,
                'average_score': challenge.average_score,
                'total_submissions': challenge.total_submissions,
                'business_value': challenge.business_value,
                'revenue_impact': challenge.revenue_impact,
                'metadata': challenge.metadata
            }
            
            if include_participants:
                participants = await self._get_challenge_participants(challenge_id)
                result['participants'] = participants
            
            if include_analytics:
                analytics = await self._get_challenge_analytics(challenge_id)
                result['analytics'] = analytics
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting challenge {challenge_id}: {e}")
            return None
    
    async def query_challenges(self, query: ChallengeQuery) -> Dict[str, Any]:
        """Query challenges with advanced filtering"""
        try:
            # Check cache
            if self.cache_enabled:
                cache_key = self._generate_cache_key(query)
                cached_result = await self._get_cached_result(cache_key)
                if cached_result:
                    return cached_result
            
            # Apply filters
            candidate_ids = set(self._challenges.keys())
            candidate_ids = await self._apply_filters(query, candidate_ids)
            
            # Build results
            results = []
            for challenge_id in candidate_ids:
                challenge_data = await self.get_challenge(
                    challenge_id,
                    include_participants=query.include_participants,
                    include_analytics=query.include_analytics
                )
                if challenge_data:
                    results.append(challenge_data)
            
            # Sort results
            results = await self._sort_results(results, query.sort_by, query.sort_desc)
            
            # Apply pagination
            total_count = len(results)
            results = results[query.offset:query.offset + query.limit]
            
            result = {
                'challenges': results,
                'total_count': total_count,
                'offset': query.offset,
                'limit': query.limit
            }
            
            # Cache result
            if self.cache_enabled:
                await self._cache_result(cache_key, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error querying challenges: {e}")
            return {'challenges': [], 'total_count': 0, 'offset': 0, 'limit': 0}
    
    async def add_participant(
        self,
        challenge_id: str,
        user_id: str,
        username: str
    ) -> bool:
        """Add participant to challenge"""
        try:
            if challenge_id not in self._challenges:
                return False
            
            challenge = self._challenges[challenge_id]
            
            # Check participant limits
            if challenge.max_participants and challenge.current_participants >= challenge.max_participants:
                return False
            
            # Check if user already participating
            if user_id in self._participants[challenge_id]:
                return False
            
            # Add participant
            participant = ChallengeParticipantData(
                user_id=user_id,
                challenge_id=challenge_id,
                username=username
            )
            
            self._participants[challenge_id][user_id] = participant
            challenge.current_participants += 1
            
            # Update user index
            if user_id not in self._user_index:
                self._user_index[user_id] = set()
            self._user_index[user_id].add(challenge_id)
            
            # Clear caches
            await self._clear_challenge_cache(challenge_id)
            
            logger.info(f"User {user_id} added to challenge {challenge_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding participant: {e}")
            return False
    
    async def update_participant_progress(
        self,
        challenge_id: str,
        user_id: str,
        progress_data: Dict[str, Any]
    ) -> bool:
        """Update participant progress"""
        try:
            if (challenge_id not in self._participants or 
                user_id not in self._participants[challenge_id]):
                return False
            
            participant = self._participants[challenge_id][user_id]
            
            # Update progress fields
            if 'current_score' in progress_data:
                participant.current_score = progress_data['current_score']
                participant.best_score = max(participant.best_score, participant.current_score)
            
            if 'progress_percentage' in progress_data:
                participant.progress_percentage = progress_data['progress_percentage']
            
            if 'completion_status' in progress_data:
                participant.completion_status = progress_data['completion_status']
            
            participant.submissions_count += 1
            participant.last_submission = datetime.now(timezone.utc)
            
            # Update challenge statistics
            await self._update_challenge_statistics(challenge_id)
            
            # Update analytics
            await self._update_analytics(challenge_id, 'participant_progress', {
                'user_id': user_id,
                'score': participant.current_score,
                'progress': participant.progress_percentage
            })
            
            # Clear caches
            await self._clear_challenge_cache(challenge_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating participant progress: {e}")
            return False
    
    async def get_challenge_leaderboard(
        self,
        challenge_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get challenge leaderboard"""
        try:
            # Check cache
            if self.cache_enabled:
                cache_key = f"leaderboard_{challenge_id}_{limit}"
                if cache_key in self._leaderboard_cache:
                    cached_time, cached_result = self._leaderboard_cache[cache_key]
                    if (datetime.now(timezone.utc) - cached_time).total_seconds() < 60:  # 1 minute cache
                        return cached_result
            
            if challenge_id not in self._participants:
                return []
            
            participants = list(self._participants[challenge_id].values())
            
            # Sort by score
            participants.sort(
                key=lambda p: (p.current_score, -p.submissions_count, p.joined_at),
                reverse=True
            )
            
            # Build leaderboard
            leaderboard = []
            for i, participant in enumerate(participants[:limit]):
                leaderboard.append({
                    'rank': i + 1,
                    'user_id': participant.user_id,
                    'username': participant.username,
                    'current_score': participant.current_score,
                    'best_score': participant.best_score,
                    'progress_percentage': participant.progress_percentage,
                    'submissions_count': participant.submissions_count,
                    'completion_status': participant.completion_status,
                    'joined_at': participant.joined_at.isoformat(),
                    'last_submission': participant.last_submission.isoformat() if participant.last_submission else None
                })
                
                # Update participant rank
                participant.current_rank = i + 1
            
            # Cache result
            if self.cache_enabled:
                self._leaderboard_cache[cache_key] = (datetime.now(timezone.utc), leaderboard)
            
            return leaderboard
            
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return []
    
    # Helper methods
    
    async def _update_indices(self, challenge_data: ChallengeData) -> None:
        """Update search indices"""
        try:
            challenge_id = challenge_data.challenge_id
            
            # Status index
            self._status_index[challenge_data.status].add(challenge_id)
            
            # Type index
            if challenge_data.challenge_type not in self._type_index:
                self._type_index[challenge_data.challenge_type] = set()
            self._type_index[challenge_data.challenge_type].add(challenge_id)
            
            # Category index
            if challenge_data.category:
                if challenge_data.category not in self._category_index:
                    self._category_index[challenge_data.category] = set()
                self._category_index[challenge_data.category].add(challenge_id)
            
            # Tag index
            for tag in challenge_data.tags:
                if tag not in self._tag_index:
                    self._tag_index[tag] = set()
                self._tag_index[tag].add(challenge_id)
            
        except Exception as e:
            logger.error(f"Error updating indices: {e}")
    
    async def _apply_filters(
        self,
        query: ChallengeQuery,
        candidate_ids: Set[str]
    ) -> Set[str]:
        """Apply query filters"""
        try:
            # Challenge ID filter
            if query.challenge_ids:
                candidate_ids &= set(query.challenge_ids)
            
            # Status filter
            if query.statuses:
                status_matches = set()
                for status in query.statuses:
                    status_matches.update(self._status_index[status])
                candidate_ids &= status_matches
            
            # Type filter
            if query.challenge_types:
                type_matches = set()
                for challenge_type in query.challenge_types:
                    if challenge_type in self._type_index:
                        type_matches.update(self._type_index[challenge_type])
                candidate_ids &= type_matches
            
            # Category filter
            if query.categories:
                category_matches = set()
                for category in query.categories:
                    if category in self._category_index:
                        category_matches.update(self._category_index[category])
                candidate_ids &= category_matches
            
            # Tag filter
            if query.tags:
                tag_matches = set()
                for tag in query.tags:
                    if tag in self._tag_index:
                        tag_matches.update(self._tag_index[tag])
                candidate_ids &= tag_matches
            
            # Active now filter
            if query.active_now:
                now = datetime.now(timezone.utc)
                active_matches = {
                    cid for cid in candidate_ids
                    if (self._challenges[cid].start_date <= now <= self._challenges[cid].end_date and
                        self._challenges[cid].status == ChallengeDataStatus.ACTIVE)
                }
                candidate_ids &= active_matches
            
            # User-specific filters
            if query.user_id:
                user_challenges = self._user_index.get(query.user_id, set())
                
                if query.user_participating:
                    candidate_ids &= user_challenges
                elif query.user_completed:
                    completed_challenges = {
                        cid for cid in user_challenges
                        if (cid in self._participants and
                            query.user_id in self._participants[cid] and
                            self._participants[cid][query.user_id].completion_status == "completed")
                    }
                    candidate_ids &= completed_challenges
            
            # Participation filters
            if query.has_space_available:
                space_available = {
                    cid for cid in candidate_ids
                    if (self._challenges[cid].max_participants is None or
                        self._challenges[cid].current_participants < self._challenges[cid].max_participants)
                }
                candidate_ids &= space_available
            
            return candidate_ids
            
        except Exception as e:
            logger.error(f"Error applying filters: {e}")
            return candidate_ids
    
    async def _sort_results(
        self,
        results: List[Dict[str, Any]],
        sort_by: str,
        sort_desc: bool
    ) -> List[Dict[str, Any]]:
        """Sort query results"""
        try:
            if sort_by == "title":
                results.sort(key=lambda x: x['title'], reverse=sort_desc)
            elif sort_by == "start_date":
                results.sort(key=lambda x: x['start_date'], reverse=sort_desc)
            elif sort_by == "end_date":
                results.sort(key=lambda x: x['end_date'], reverse=sort_desc)
            elif sort_by == "current_participants":
                results.sort(key=lambda x: x['current_participants'], reverse=sort_desc)
            elif sort_by == "completion_rate":
                results.sort(key=lambda x: x['completion_rate'], reverse=sort_desc)
            elif sort_by == "average_score":
                results.sort(key=lambda x: x['average_score'], reverse=sort_desc)
            else:  # default to created_at
                results.sort(key=lambda x: x['created_at'], reverse=sort_desc)
            
            return results
            
        except Exception as e:
            logger.error(f"Error sorting results: {e}")
            return results
    
    async def _update_challenge_statistics(self, challenge_id: str) -> None:
        """Update challenge statistics"""
        try:
            if challenge_id not in self._challenges:
                return
            
            challenge = self._challenges[challenge_id]
            participants = self._participants[challenge_id]
            
            if not participants:
                return
            
            # Calculate statistics
            scores = [p.current_score for p in participants.values() if p.current_score > 0]
            if scores:
                challenge.average_score = sum(scores) / len(scores)
            
            challenge.total_submissions = sum(p.submissions_count for p in participants.values())
            
            completed_count = sum(
                1 for p in participants.values()
                if p.completion_status == "completed"
            )
            
            if len(participants) > 0:
                challenge.completion_rate = (completed_count / len(participants)) * 100
            
            challenge.updated_at = datetime.now(timezone.utc)
            
        except Exception as e:
            logger.error(f"Error updating challenge statistics: {e}")
    
    async def _get_challenge_participants(self, challenge_id: str) -> List[Dict[str, Any]]:
        """Get challenge participants"""
        try:
            if challenge_id not in self._participants:
                return []
            
            participants = []
            for participant in self._participants[challenge_id].values():
                participants.append({
                    'user_id': participant.user_id,
                    'username': participant.username,
                    'current_score': participant.current_score,
                    'current_rank': participant.current_rank,
                    'progress_percentage': participant.progress_percentage,
                    'submissions_count': participant.submissions_count,
                    'completion_status': participant.completion_status,
                    'joined_at': participant.joined_at.isoformat(),
                    'last_submission': participant.last_submission.isoformat() if participant.last_submission else None
                })
            
            return participants
            
        except Exception as e:
            logger.error(f"Error getting challenge participants: {e}")
            return []
    
    # Analytics methods
    
    async def _initialize_analytics(self, challenge_id: str) -> None:
        """Initialize analytics for challenge"""
        try:
            self._challenge_analytics[challenge_id] = {
                'created_at': datetime.now(timezone.utc).isoformat(),
                'participation_events': [],
                'progress_events': [],
                'daily_stats': {}
            }
            
        except Exception as e:
            logger.error(f"Error initializing analytics: {e}")
    
    async def _update_analytics(
        self,
        challenge_id: str,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> None:
        """Update challenge analytics"""
        try:
            if challenge_id not in self._challenge_analytics:
                await self._initialize_analytics(challenge_id)
            
            analytics = self._challenge_analytics[challenge_id]
            
            event = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'type': event_type,
                'data': event_data
            }
            
            if event_type == 'participant_added':
                analytics['participation_events'].append(event)
            elif event_type == 'participant_progress':
                analytics['progress_events'].append(event)
            
            # Update daily stats
            today = datetime.now(timezone.utc).date().isoformat()
            if today not in analytics['daily_stats']:
                analytics['daily_stats'][today] = {
                    'new_participants': 0,
                    'progress_updates': 0,
                    'unique_users': set()
                }
            
            daily_stats = analytics['daily_stats'][today]
            if event_type == 'participant_added':
                daily_stats['new_participants'] += 1
            elif event_type == 'participant_progress':
                daily_stats['progress_updates'] += 1
            
            if 'user_id' in event_data:
                daily_stats['unique_users'].add(event_data['user_id'])
            
        except Exception as e:
            logger.error(f"Error updating analytics: {e}")
    
    async def _get_challenge_analytics(self, challenge_id: str) -> Dict[str, Any]:
        """Get challenge analytics"""
        try:
            if challenge_id not in self._challenge_analytics:
                return {}
            
            analytics = self._challenge_analytics[challenge_id]
            
            return {
                'total_participation_events': len(analytics['participation_events']),
                'total_progress_events': len(analytics['progress_events']),
                'daily_stats': analytics['daily_stats'],
                'recent_events': (analytics['participation_events'] + analytics['progress_events'])[-20:]
            }
            
        except Exception as e:
            logger.error(f"Error getting challenge analytics: {e}")
            return {}
    
    # Cache management
    
    def _generate_cache_key(self, query: ChallengeQuery) -> str:
        """Generate cache key for query"""
        key_parts = [
            f"ids:{','.join(query.challenge_ids) if query.challenge_ids else 'all'}",
            f"status:{','.join([s.value for s in query.statuses]) if query.statuses else 'all'}",
            f"types:{','.join(query.challenge_types) if query.challenge_types else 'all'}",
            f"user:{query.user_id or 'none'}",
            f"active:{query.active_now}",
            f"sort:{query.sort_by}:{query.sort_desc}",
            f"page:{query.offset}:{query.limit}"
        ]
        return "challenge_query_" + "_".join(key_parts)
    
    async def _get_cached_result(self, cache_key: str) -> Optional[Any]:
        """Get cached result"""
        try:
            if cache_key not in self._query_cache:
                return None
            
            cached_time, cached_result = self._query_cache[cache_key]
            
            if (datetime.now(timezone.utc) - cached_time).total_seconds() > self.cache_ttl_seconds:
                del self._query_cache[cache_key]
                return None
            
            return cached_result
            
        except Exception as e:
            logger.error(f"Error getting cached result: {e}")
            return None
    
    async def _cache_result(self, cache_key: str, result: Any) -> None:
        """Cache result"""
        try:
            self._query_cache[cache_key] = (datetime.now(timezone.utc), result)
            
            # Limit cache size
            if len(self._query_cache) > 1000:
                oldest_key = min(self._query_cache.keys(), key=lambda k: self._query_cache[k][0])
                del self._query_cache[oldest_key]
            
        except Exception as e:
            logger.error(f"Error caching result: {e}")
    
    async def _clear_challenge_cache(self, challenge_id: str) -> None:
        """Clear cache for specific challenge"""
        try:
            keys_to_remove = []
            for cache_key in self._query_cache:
                if challenge_id in cache_key or "all" in cache_key:
                    keys_to_remove.append(cache_key)
            
            for key in keys_to_remove:
                del self._query_cache[key]
            
            # Clear leaderboard cache
            leaderboard_keys = [k for k in self._leaderboard_cache if k.startswith(f"leaderboard_{challenge_id}")]
            for key in leaderboard_keys:
                del self._leaderboard_cache[key]
                
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")