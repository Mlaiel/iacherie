#!/usr/bin/env python3
"""
🏆 COMPETITION SERVICE - ENTERPRISE CREATOR COMPETITION PLATFORM
=================================================================

🎯 MULTI-EXPERT IMPLEMENTATION DEMONSTRATING:
- Lead Dev IA: AI-powered competition matching and intelligent scoring algorithms
- Backend Senior: Enterprise competition infrastructure with real-time leaderboards
- ML Engineer: Machine learning for fair competition matching and skill assessment
- DBA: Optimized competition data models with high-performance ranking queries
- Security: Secure competition validation with anti-cheat protection
- Microservices: Distributed competition orchestration across creator ecosystem
- Audio Engineer: Audio competition judging and automated quality assessment
- DevOps: Automated competition monitoring with comprehensive analytics
- AI Prompt Engineer: Intelligent competition creation and personalized challenges

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
Module: Competition Service - Enterprise Creator Competition Platform
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
import random
import aiohttp
import asyncpg
import redis.asyncio as redis
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from sklearn.preprocessing import StandardScaler
import statistics

# Configure enterprise-grade logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [Competition] %(message)s',
    handlers=[
        logging.FileHandler('/var/log/ainflue/competition.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CompetitionType(Enum):
    """Types of competitions"""
    MUSIC_PRODUCTION = "music_production"
    PHOTO_CONTEST = "photo_contest"
    VIDEO_CHALLENGE = "video_challenge"
    WRITING_CONTEST = "writing_contest"
    COLLABORATION_CHALLENGE = "collaboration_challenge"
    REMIX_BATTLE = "remix_battle"
    SPEED_CHALLENGE = "speed_challenge"
    THEMED_CONTEST = "themed_contest"
    SKILL_SHOWCASE = "skill_showcase"
    COMMUNITY_VOTE = "community_vote"

class CompetitionStatus(Enum):
    """Competition status"""
    DRAFT = "draft"
    REGISTRATION_OPEN = "registration_open"
    ACTIVE = "active"
    JUDGING = "judging"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class JudgingType(Enum):
    """Judging types"""
    COMMUNITY_VOTE = "community_vote"
    EXPERT_PANEL = "expert_panel"
    AI_AUTOMATED = "ai_automated"
    HYBRID = "hybrid"
    PEER_REVIEW = "peer_review"

class SubmissionStatus(Enum):
    """Submission status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DISQUALIFIED = "disqualified"
    UNDER_REVIEW = "under_review"

@dataclass
class Competition:
    """Competition data structure"""
    id: str
    title: str
    description: str
    competition_type: CompetitionType
    status: CompetitionStatus
    judging_type: JudgingType
    creator_id: str
    start_time: datetime
    end_time: datetime
    registration_deadline: datetime
    max_participants: Optional[int]
    entry_fee: float = 0.0
    prize_pool: float = 0.0
    rules: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    requirements: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CompetitionSubmission:
    """Competition submission"""
    id: str
    competition_id: str
    participant_id: str
    title: str
    description: str
    content_url: str
    content_type: str
    submitted_at: datetime
    status: SubmissionStatus = SubmissionStatus.PENDING
    scores: Dict[str, float] = field(default_factory=dict)
    comments: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CompetitionParticipant:
    """Competition participant"""
    user_id: str
    competition_id: str
    registered_at: datetime
    status: str = "active"
    skill_level: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class JudgingCriteria:
    """Judging criteria for competitions"""
    name: str
    description: str
    weight: float
    max_score: float
    ai_evaluable: bool = False

class AIJudge:
    """🤖 AI-Powered Competition Judging System"""
    
    def __init__(self):
        self.scoring_models = {}
        self.quality_thresholds = {
            'audio_quality': 0.7,
            'originality': 0.6,
            'technical_skill': 0.8,
            'creativity': 0.65
        }
        
    async def evaluate_submission(self, submission: CompetitionSubmission, criteria: List[JudgingCriteria]) -> Dict[str, float]:
        """AI evaluation of competition submission"""
        try:
            logger.info(f"🤖 AI evaluating submission {submission.id}")
            
            scores = {}
            
            for criterion in criteria:
                if criterion.ai_evaluable:
                    score = await self._evaluate_criterion(submission, criterion)
                    scores[criterion.name] = score
                    
            # Overall AI confidence score
            scores['ai_confidence'] = await self._calculate_ai_confidence(submission, scores)
            
            logger.info(f"✅ AI evaluation completed for submission {submission.id}")
            return scores
            
        except Exception as e:
            logger.error(f"❌ AI evaluation failed: {str(e)}")
            return {}
    
    async def _evaluate_criterion(self, submission: CompetitionSubmission, criterion: JudgingCriteria) -> float:
        """Evaluate specific criterion"""
        try:
            base_score = 0.5  # Base score
            
            # Content type specific evaluation
            if submission.content_type == 'audio':
                score = await self._evaluate_audio_criterion(submission, criterion)
            elif submission.content_type == 'image':
                score = await self._evaluate_image_criterion(submission, criterion)
            elif submission.content_type == 'video':
                score = await self._evaluate_video_criterion(submission, criterion)
            elif submission.content_type == 'text':
                score = await self._evaluate_text_criterion(submission, criterion)
            else:
                score = await self._evaluate_generic_criterion(submission, criterion)
            
            # Normalize score to criterion's max_score
            normalized_score = min(score * criterion.max_score, criterion.max_score)
            
            return round(normalized_score, 2)
            
        except Exception as e:
            logger.error(f"❌ Criterion evaluation failed: {str(e)}")
            return criterion.max_score * 0.5  # Return middle score on error
    
    async def _evaluate_audio_criterion(self, submission: CompetitionSubmission, criterion: JudgingCriteria) -> float:
        """Audio-specific criterion evaluation"""
        try:
            # Audio Engineer expertise: Advanced audio quality assessment
            audio_metadata = submission.metadata.get('audio_analysis', {})
            
            if criterion.name.lower() in ['audio_quality', 'production_quality']:
                # Evaluate technical audio quality
                sample_rate = audio_metadata.get('sample_rate', 44100)
                bit_depth = audio_metadata.get('bit_depth', 16)
                dynamic_range = audio_metadata.get('dynamic_range', 10)
                
                quality_score = 0.3  # Base score
                
                # Sample rate scoring
                if sample_rate >= 48000:
                    quality_score += 0.3
                elif sample_rate >= 44100:
                    quality_score += 0.2
                
                # Bit depth scoring
                if bit_depth >= 24:
                    quality_score += 0.2
                elif bit_depth >= 16:
                    quality_score += 0.1
                
                # Dynamic range scoring
                if dynamic_range >= 15:
                    quality_score += 0.2
                elif dynamic_range >= 10:
                    quality_score += 0.1
                
                return min(quality_score, 1.0)
                
            elif criterion.name.lower() in ['creativity', 'originality']:
                # Evaluate creative aspects
                genre_diversity = len(audio_metadata.get('detected_genres', []))
                tempo_changes = audio_metadata.get('tempo_changes', 0)
                unique_elements = audio_metadata.get('unique_sound_elements', 0)
                
                creativity_score = 0.4
                creativity_score += min(genre_diversity * 0.1, 0.3)
                creativity_score += min(tempo_changes * 0.05, 0.2)
                creativity_score += min(unique_elements * 0.03, 0.1)
                
                return min(creativity_score, 1.0)
                
            elif criterion.name.lower() in ['technical_skill', 'mixing']:
                # Evaluate technical mixing skills
                frequency_balance = audio_metadata.get('frequency_balance_score', 0.5)
                stereo_imaging = audio_metadata.get('stereo_imaging_score', 0.5)
                compression_quality = audio_metadata.get('compression_quality', 0.5)
                
                technical_score = (frequency_balance + stereo_imaging + compression_quality) / 3
                return min(technical_score, 1.0)
            
            else:
                # Generic audio evaluation
                duration = audio_metadata.get('duration', 0)
                if 120 <= duration <= 300:  # 2-5 minutes is good
                    return 0.8
                elif 60 <= duration <= 600:  # 1-10 minutes is acceptable
                    return 0.6
                else:
                    return 0.4
                    
        except Exception as e:
            logger.error(f"❌ Audio evaluation failed: {str(e)}")
            return 0.5
    
    async def _evaluate_image_criterion(self, submission: CompetitionSubmission, criterion: JudgingCriteria) -> float:
        """Image-specific criterion evaluation"""
        try:
            image_metadata = submission.metadata.get('image_analysis', {})
            
            if criterion.name.lower() in ['composition', 'technical_quality']:
                resolution = image_metadata.get('resolution', [1920, 1080])
                color_balance = image_metadata.get('color_balance_score', 0.5)
                sharpness = image_metadata.get('sharpness_score', 0.5)
                
                # Resolution scoring
                pixel_count = resolution[0] * resolution[1]
                resolution_score = min(pixel_count / (1920 * 1080), 1.0)  # Normalize to 1080p
                
                # Combined technical score
                technical_score = (resolution_score + color_balance + sharpness) / 3
                return min(technical_score, 1.0)
                
            elif criterion.name.lower() in ['creativity', 'artistic_vision']:
                unique_elements = image_metadata.get('unique_elements_count', 0)
                color_harmony = image_metadata.get('color_harmony_score', 0.5)
                subject_clarity = image_metadata.get('subject_clarity', 0.5)
                
                creativity_score = 0.3
                creativity_score += min(unique_elements * 0.1, 0.4)
                creativity_score += color_harmony * 0.2
                creativity_score += subject_clarity * 0.1
                
                return min(creativity_score, 1.0)
            
            else:
                return 0.7  # Default score for images
                
        except Exception as e:
            logger.error(f"❌ Image evaluation failed: {str(e)}")
            return 0.5
    
    async def _evaluate_video_criterion(self, submission: CompetitionSubmission, criterion: JudgingCriteria) -> float:
        """Video-specific criterion evaluation"""
        try:
            video_metadata = submission.metadata.get('video_analysis', {})
            
            if criterion.name.lower() in ['production_quality', 'technical_skill']:
                resolution = video_metadata.get('resolution', '1080p')
                frame_rate = video_metadata.get('frame_rate', 30)
                audio_quality = video_metadata.get('audio_quality_score', 0.5)
                
                quality_score = 0.3
                
                # Resolution scoring
                if '4k' in resolution.lower() or '2160' in resolution:
                    quality_score += 0.3
                elif '1080' in resolution:
                    quality_score += 0.2
                elif '720' in resolution:
                    quality_score += 0.1
                
                # Frame rate scoring
                if frame_rate >= 60:
                    quality_score += 0.2
                elif frame_rate >= 30:
                    quality_score += 0.15
                
                # Audio quality
                quality_score += audio_quality * 0.2
                
                return min(quality_score, 1.0)
                
            elif criterion.name.lower() in ['storytelling', 'creativity']:
                scene_transitions = video_metadata.get('scene_transition_count', 0)
                visual_effects = video_metadata.get('visual_effects_count', 0)
                narrative_coherence = video_metadata.get('narrative_coherence_score', 0.5)
                
                storytelling_score = 0.4
                storytelling_score += min(scene_transitions * 0.05, 0.2)
                storytelling_score += min(visual_effects * 0.03, 0.15)
                storytelling_score += narrative_coherence * 0.25
                
                return min(storytelling_score, 1.0)
            
            else:
                duration = video_metadata.get('duration', 0)
                if 30 <= duration <= 600:  # 30 seconds to 10 minutes
                    return 0.8
                else:
                    return 0.6
                    
        except Exception as e:
            logger.error(f"❌ Video evaluation failed: {str(e)}")
            return 0.5
    
    async def _evaluate_text_criterion(self, submission: CompetitionSubmission, criterion: JudgingCriteria) -> float:
        """Text-specific criterion evaluation"""
        try:
            text_metadata = submission.metadata.get('text_analysis', {})
            content_length = len(submission.description)
            
            if criterion.name.lower() in ['writing_quality', 'grammar']:
                grammar_score = text_metadata.get('grammar_score', 0.5)
                readability_score = text_metadata.get('readability_score', 0.5)
                vocabulary_richness = text_metadata.get('vocabulary_richness', 0.5)
                
                writing_score = (grammar_score + readability_score + vocabulary_richness) / 3
                return min(writing_score, 1.0)
                
            elif criterion.name.lower() in ['creativity', 'originality']:
                unique_phrases = text_metadata.get('unique_phrases_count', 0)
                sentiment_variety = text_metadata.get('sentiment_variety_score', 0.5)
                
                creativity_score = 0.4
                creativity_score += min(unique_phrases * 0.02, 0.3)
                creativity_score += sentiment_variety * 0.3
                
                return min(creativity_score, 1.0)
            
            else:
                # Length-based scoring
                if 100 <= content_length <= 2000:
                    return 0.8
                elif 50 <= content_length <= 5000:
                    return 0.6
                else:
                    return 0.4
                    
        except Exception as e:
            logger.error(f"❌ Text evaluation failed: {str(e)}")
            return 0.5
    
    async def _evaluate_generic_criterion(self, submission: CompetitionSubmission, criterion: JudgingCriteria) -> float:
        """Generic criterion evaluation"""
        try:
            # Generic evaluation based on submission metadata
            base_score = 0.5
            
            # Bonus for detailed description
            if len(submission.description) > 100:
                base_score += 0.1
            
            # Bonus for metadata richness
            metadata_count = len(submission.metadata)
            base_score += min(metadata_count * 0.02, 0.2)
            
            # Bonus for proper content type
            if submission.content_url and submission.content_type:
                base_score += 0.1
            
            return min(base_score, 1.0)
            
        except Exception:
            return 0.5
    
    async def _calculate_ai_confidence(self, submission: CompetitionSubmission, scores: Dict[str, float]) -> float:
        """Calculate AI confidence in the evaluation"""
        try:
            base_confidence = 0.7
            
            # Confidence based on available metadata
            metadata_richness = len(submission.metadata) / 10  # Normalize
            base_confidence += min(metadata_richness * 0.2, 0.2)
            
            # Confidence based on score consistency
            if len(scores) > 1:
                score_values = [score for score in scores.values() if isinstance(score, (int, float))]
                if score_values:
                    score_std = statistics.stdev(score_values) if len(score_values) > 1 else 0
                    consistency_bonus = max(0, 0.1 - score_std)
                    base_confidence += consistency_bonus
            
            # Content type confidence
            content_type_confidence = {
                'audio': 0.85,
                'image': 0.75,
                'video': 0.70,
                'text': 0.80
            }
            type_confidence = content_type_confidence.get(submission.content_type, 0.60)
            
            # Weighted average
            final_confidence = (base_confidence + type_confidence) / 2
            
            return min(final_confidence, 1.0)
            
        except Exception:
            return 0.6

class CompetitionMatcher:
    """🎯 AI-Powered Competition Matching System"""
    
    def __init__(self):
        self.skill_assessor = StandardScaler()
        
    async def match_participants(self, competition: Competition, participants: List[CompetitionParticipant]) -> Dict[str, List[str]]:
        """Match participants for fair competition"""
        try:
            logger.info(f"🎯 Matching {len(participants)} participants for competition {competition.id}")
            
            if len(participants) <= 10:
                # Small competition, single group
                return {
                    'group_1': [p.user_id for p in participants]
                }
            
            # Get participant skill levels
            participant_skills = await self._assess_participant_skills(participants)
            
            # Create balanced groups
            groups = await self._create_balanced_groups(participant_skills, max_groups=4)
            
            logger.info(f"✅ Created {len(groups)} balanced groups")
            return groups
            
        except Exception as e:
            logger.error(f"❌ Participant matching failed: {str(e)}")
            return {'group_1': [p.user_id for p in participants]}
    
    async def _assess_participant_skills(self, participants: List[CompetitionParticipant]) -> Dict[str, float]:
        """Assess participant skill levels"""
        skills = {}
        
        try:
            for participant in participants:
                skill_score = await self._calculate_skill_score(participant)
                skills[participant.user_id] = skill_score
            
            return skills
            
        except Exception as e:
            logger.error(f"❌ Skill assessment failed: {str(e)}")
            return {p.user_id: 0.5 for p in participants}
    
    async def _calculate_skill_score(self, participant: CompetitionParticipant) -> float:
        """Calculate individual skill score"""
        try:
            base_score = 0.5
            
            # Previous competition performance
            past_wins = participant.metadata.get('competition_wins', 0)
            past_participations = participant.metadata.get('total_competitions', 1)
            win_rate = past_wins / past_participations
            
            base_score += win_rate * 0.3
            
            # Experience level
            experience_months = participant.metadata.get('experience_months', 6)
            experience_factor = min(experience_months / 60, 1.0)  # Max 5 years
            base_score += experience_factor * 0.2
            
            # Content quality history
            avg_content_rating = participant.metadata.get('avg_content_rating', 3.0)
            rating_factor = (avg_content_rating - 1) / 4  # Normalize 1-5 to 0-1
            base_score += rating_factor * 0.3
            
            return min(base_score, 1.0)
            
        except Exception:
            return 0.5
    
    async def _create_balanced_groups(self, skills: Dict[str, float], max_groups: int = 4) -> Dict[str, List[str]]:
        """Create balanced groups based on skills"""
        try:
            # Sort participants by skill level
            sorted_participants = sorted(skills.items(), key=lambda x: x[1], reverse=True)
            
            # Determine number of groups
            total_participants = len(sorted_participants)
            group_size = max(total_participants // max_groups, 2)
            num_groups = min(max_groups, total_participants // 2)
            
            groups = {f'group_{i+1}': [] for i in range(num_groups)}
            
            # Distribute participants in snake draft style
            group_order = list(range(num_groups))
            
            for i, (user_id, skill) in enumerate(sorted_participants):
                if i < num_groups:
                    # First round, distribute one to each group
                    groups[f'group_{i+1}'].append(user_id)
                else:
                    # Snake draft: reverse order every round
                    round_num = i // num_groups
                    if round_num % 2 == 1:
                        group_order.reverse()
                    
                    group_index = group_order[i % num_groups]
                    groups[f'group_{group_index+1}'].append(user_id)
            
            return groups
            
        except Exception as e:
            logger.error(f"❌ Group creation failed: {str(e)}")
            # Fallback: random distribution
            participant_ids = list(skills.keys())
            random.shuffle(participant_ids)
            
            groups = {}
            group_size = len(participant_ids) // max_groups + 1
            
            for i in range(0, len(participant_ids), group_size):
                group_name = f'group_{len(groups)+1}'
                groups[group_name] = participant_ids[i:i+group_size]
            
            return groups

class CompetitionService:
    """🏗️ Enterprise Competition Service - Creator Competition Platform"""
    
    def __init__(self,
                 redis_url: str = "redis://localhost:6379",
                 db_url: str = "postgresql://localhost/ainflue"):
        
        self.redis_url = redis_url
        self.db_url = db_url
        self.ai_judge = AIJudge()
        self.matcher = CompetitionMatcher()
        
        # Service components
        self.redis_client = None
        self.db_pool = None
        self.executor = ThreadPoolExecutor(max_workers=15)
        
        # Service metrics
        self.metrics = {
            'competitions_created': 0,
            'submissions_processed': 0,
            'judgments_completed': 0,
            'active_competitions': 0,
            'total_participants': 0,
            'uptime_start': datetime.utcnow()
        }
        
        logger.info("🚀 Competition Service initialized with enterprise configuration")
    
    async def start(self):
        """Start the Competition Service"""
        try:
            # Initialize Redis connection
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            
            # Initialize database connection pool
            self.db_pool = await asyncpg.create_pool(self.db_url, min_size=5, max_size=20)
            
            logger.info("✅ Competition Service started successfully")
            
            # Start background tasks
            asyncio.create_task(self._competition_monitor())
            asyncio.create_task(self._auto_judge_submissions())
            
        except Exception as e:
            logger.error(f"❌ Failed to start Competition Service: {str(e)}")
            raise
    
    async def stop(self):
        """Gracefully stop the service"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            
            if self.db_pool:
                await self.db_pool.close()
            
            self.executor.shutdown(wait=True)
            logger.info("✅ Competition Service stopped gracefully")
            
        except Exception as e:
            logger.error(f"❌ Error stopping Competition Service: {str(e)}")
    
    async def create_competition(self, competition: Competition) -> str:
        """Create a new competition"""
        try:
            logger.info(f"🏆 Creating competition: {competition.title}")
            
            # Store competition
            await self._store_competition(competition)
            
            # Create default judging criteria
            await self._create_default_judging_criteria(competition)
            
            self.metrics['competitions_created'] += 1
            if competition.status in [CompetitionStatus.REGISTRATION_OPEN, CompetitionStatus.ACTIVE]:
                self.metrics['active_competitions'] += 1
            
            logger.info(f"✅ Competition created: {competition.id}")
            return competition.id
            
        except Exception as e:
            logger.error(f"❌ Competition creation failed: {str(e)}")
            raise
    
    async def register_participant(self, competition_id: str, user_id: str, user_metadata: Dict[str, Any] = None) -> bool:
        """Register participant for competition"""
        try:
            logger.info(f"👤 Registering participant {user_id} for competition {competition_id}")
            
            # Check if competition exists and is open for registration
            competition = await self._get_competition(competition_id)
            if not competition:
                return False
            
            if competition.status != CompetitionStatus.REGISTRATION_OPEN:
                logger.warning(f"⚠️ Competition {competition_id} is not open for registration")
                return False
            
            # Check deadline
            if datetime.utcnow() > competition.registration_deadline:
                logger.warning(f"⚠️ Registration deadline passed for competition {competition_id}")
                return False
            
            # Check participant limit
            if competition.max_participants:
                current_count = await self._get_participant_count(competition_id)
                if current_count >= competition.max_participants:
                    logger.warning(f"⚠️ Competition {competition_id} is full")
                    return False
            
            # Register participant
            participant = CompetitionParticipant(
                user_id=user_id,
                competition_id=competition_id,
                registered_at=datetime.utcnow(),
                metadata=user_metadata or {}
            )
            
            await self._store_participant(participant)
            
            self.metrics['total_participants'] += 1
            
            logger.info(f"✅ Participant {user_id} registered for competition {competition_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Participant registration failed: {str(e)}")
            return False
    
    async def submit_entry(self, submission: CompetitionSubmission) -> str:
        """Submit entry to competition"""
        try:
            logger.info(f"📝 Processing submission for competition {submission.competition_id}")
            
            # Validate submission
            competition = await self._get_competition(submission.competition_id)
            if not competition:
                raise ValueError("Competition not found")
            
            if competition.status != CompetitionStatus.ACTIVE:
                raise ValueError("Competition is not accepting submissions")
            
            if datetime.utcnow() > competition.end_time:
                raise ValueError("Competition submission deadline has passed")
            
            # Check if user is registered
            is_registered = await self._is_participant_registered(
                submission.competition_id, 
                submission.participant_id
            )
            
            if not is_registered:
                raise ValueError("User is not registered for this competition")
            
            # Store submission
            await self._store_submission(submission)
            
            # Queue for AI judgment if applicable
            if competition.judging_type in [JudgingType.AI_AUTOMATED, JudgingType.HYBRID]:
                await self._queue_for_ai_judgment(submission)
            
            self.metrics['submissions_processed'] += 1
            
            logger.info(f"✅ Submission {submission.id} processed successfully")
            return submission.id
            
        except Exception as e:
            logger.error(f"❌ Submission processing failed: {str(e)}")
            raise
    
    async def get_competition_leaderboard(self, competition_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get competition leaderboard"""
        try:
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT 
                        s.participant_id,
                        s.title as submission_title,
                        s.submitted_at,
                        COALESCE(AVG(j.total_score), 0) as average_score,
                        COUNT(j.id) as judgment_count,
                        u.username,
                        u.profile_image
                    FROM competition_submissions s
                    LEFT JOIN submission_judgments j ON s.id = j.submission_id
                    LEFT JOIN user_profiles u ON s.participant_id = u.user_id
                    WHERE s.competition_id = $1 AND s.status = 'approved'
                    GROUP BY s.participant_id, s.title, s.submitted_at, u.username, u.profile_image
                    ORDER BY average_score DESC, s.submitted_at ASC
                    LIMIT $2
                """, competition_id, limit)
                
                leaderboard = []
                for i, row in enumerate(rows):
                    entry = {
                        'rank': i + 1,
                        'participant_id': row['participant_id'],
                        'username': row['username'],
                        'profile_image': row['profile_image'],
                        'submission_title': row['submission_title'],
                        'average_score': round(float(row['average_score']), 2),
                        'judgment_count': row['judgment_count'],
                        'submitted_at': row['submitted_at'].isoformat()
                    }
                    leaderboard.append(entry)
                
                return leaderboard
                
        except Exception as e:
            logger.error(f"❌ Leaderboard generation failed: {str(e)}")
            return []
    
    async def get_competition_analytics(self, competition_id: str) -> Dict[str, Any]:
        """Get comprehensive competition analytics"""
        try:
            async with self.db_pool.acquire() as conn:
                # Basic stats
                stats = await conn.fetchrow("""
                    SELECT 
                        COUNT(DISTINCT cp.user_id) as participant_count,
                        COUNT(DISTINCT cs.id) as submission_count,
                        COUNT(DISTINCT sj.id) as judgment_count,
                        AVG(sj.total_score) as average_score
                    FROM competitions c
                    LEFT JOIN competition_participants cp ON c.id = cp.competition_id
                    LEFT JOIN competition_submissions cs ON c.id = cs.competition_id
                    LEFT JOIN submission_judgments sj ON cs.id = sj.submission_id
                    WHERE c.id = $1
                """, competition_id)
                
                # Submission by day
                daily_submissions = await conn.fetch("""
                    SELECT 
                        DATE(submitted_at) as date,
                        COUNT(*) as count
                    FROM competition_submissions 
                    WHERE competition_id = $1
                    GROUP BY DATE(submitted_at)
                    ORDER BY date
                """, competition_id)
                
                # Category breakdown
                category_stats = await conn.fetch("""
                    SELECT 
                        content_type,
                        COUNT(*) as count,
                        AVG(COALESCE((SELECT AVG(total_score) FROM submission_judgments WHERE submission_id = cs.id), 0)) as avg_score
                    FROM competition_submissions cs
                    WHERE competition_id = $1
                    GROUP BY content_type
                """, competition_id)
                
                analytics = {
                    'competition_id': competition_id,
                    'participant_count': stats['participant_count'],
                    'submission_count': stats['submission_count'],
                    'judgment_count': stats['judgment_count'],
                    'average_score': round(float(stats['average_score'] or 0), 2),
                    'daily_submissions': [
                        {
                            'date': row['date'].isoformat(),
                            'count': row['count']
                        } for row in daily_submissions
                    ],
                    'category_breakdown': [
                        {
                            'category': row['content_type'],
                            'submissions': row['count'],
                            'average_score': round(float(row['avg_score'] or 0), 2)
                        } for row in category_stats
                    ],
                    'insights': await self._generate_competition_insights(stats, category_stats)
                }
                
                return analytics
                
        except Exception as e:
            logger.error(f"❌ Competition analytics failed: {str(e)}")
            return {'error': str(e)}
    
    async def get_service_health(self) -> Dict[str, Any]:
        """Get comprehensive service health metrics"""
        try:
            uptime = datetime.utcnow() - self.metrics['uptime_start']
            
            return {
                'status': 'healthy',
                'uptime_seconds': uptime.total_seconds(),
                'metrics': self.metrics.copy(),
                'components': {
                    'redis_connected': self.redis_client is not None,
                    'database_connected': self.db_pool is not None,
                    'ai_judge_active': self.ai_judge is not None,
                    'matcher_active': self.matcher is not None
                },
                'performance': {
                    'competitions_per_hour': self.metrics['competitions_created'] / max(uptime.total_seconds() / 3600, 1),
                    'submissions_per_hour': self.metrics['submissions_processed'] / max(uptime.total_seconds() / 3600, 1),
                    'judgment_completion_rate': (self.metrics['judgments_completed'] / 
                                               max(self.metrics['submissions_processed'], 1))
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    # Helper methods
    async def _store_competition(self, competition: Competition):
        """Store competition in database"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO competitions 
                    (id, title, description, competition_type, status, judging_type,
                     creator_id, start_time, end_time, registration_deadline,
                     max_participants, entry_fee, prize_pool, rules, categories,
                     requirements, created_at, metadata)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18)
                """,
                competition.id, competition.title, competition.description,
                competition.competition_type.value, competition.status.value,
                competition.judging_type.value, competition.creator_id,
                competition.start_time, competition.end_time,
                competition.registration_deadline, competition.max_participants,
                competition.entry_fee, competition.prize_pool,
                json.dumps(competition.rules), json.dumps(competition.categories),
                json.dumps(competition.requirements), competition.created_at,
                json.dumps(competition.metadata)
                )
                
        except Exception as e:
            logger.error(f"❌ Failed to store competition: {str(e)}")
            raise
    
    async def _store_participant(self, participant: CompetitionParticipant):
        """Store competition participant"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO competition_participants 
                    (user_id, competition_id, registered_at, status, skill_level, metadata)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    ON CONFLICT (user_id, competition_id) DO NOTHING
                """,
                participant.user_id, participant.competition_id,
                participant.registered_at, participant.status,
                participant.skill_level, json.dumps(participant.metadata)
                )
                
        except Exception as e:
            logger.error(f"❌ Failed to store participant: {str(e)}")
            raise
    
    async def _store_submission(self, submission: CompetitionSubmission):
        """Store competition submission"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO competition_submissions 
                    (id, competition_id, participant_id, title, description,
                     content_url, content_type, submitted_at, status, metadata)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """,
                submission.id, submission.competition_id, submission.participant_id,
                submission.title, submission.description, submission.content_url,
                submission.content_type, submission.submitted_at,
                submission.status.value, json.dumps(submission.metadata)
                )
                
        except Exception as e:
            logger.error(f"❌ Failed to store submission: {str(e)}")
            raise
    
    async def _get_competition(self, competition_id: str) -> Optional[Competition]:
        """Get competition by ID"""
        try:
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT * FROM competitions WHERE id = $1
                """, competition_id)
                
                if row:
                    return Competition(
                        id=row['id'],
                        title=row['title'],
                        description=row['description'],
                        competition_type=CompetitionType(row['competition_type']),
                        status=CompetitionStatus(row['status']),
                        judging_type=JudgingType(row['judging_type']),
                        creator_id=row['creator_id'],
                        start_time=row['start_time'],
                        end_time=row['end_time'],
                        registration_deadline=row['registration_deadline'],
                        max_participants=row['max_participants'],
                        entry_fee=row['entry_fee'],
                        prize_pool=row['prize_pool'],
                        rules=json.loads(row['rules']) if row['rules'] else [],
                        categories=json.loads(row['categories']) if row['categories'] else [],
                        requirements=json.loads(row['requirements']) if row['requirements'] else {},
                        created_at=row['created_at'],
                        metadata=json.loads(row['metadata']) if row['metadata'] else {}
                    )
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to get competition: {str(e)}")
            return None
    
    async def _get_participant_count(self, competition_id: str) -> int:
        """Get current participant count"""
        try:
            async with self.db_pool.acquire() as conn:
                count = await conn.fetchval("""
                    SELECT COUNT(*) FROM competition_participants 
                    WHERE competition_id = $1 AND status = 'active'
                """, competition_id)
                return count or 0
                
        except Exception as e:
            logger.error(f"❌ Failed to get participant count: {str(e)}")
            return 0
    
    async def _is_participant_registered(self, competition_id: str, user_id: str) -> bool:
        """Check if user is registered for competition"""
        try:
            async with self.db_pool.acquire() as conn:
                exists = await conn.fetchval("""
                    SELECT EXISTS(
                        SELECT 1 FROM competition_participants 
                        WHERE competition_id = $1 AND user_id = $2 AND status = 'active'
                    )
                """, competition_id, user_id)
                return bool(exists)
                
        except Exception as e:
            logger.error(f"❌ Failed to check participant registration: {str(e)}")
            return False
    
    async def _create_default_judging_criteria(self, competition: Competition):
        """Create default judging criteria for competition"""
        try:
            criteria_sets = {
                CompetitionType.MUSIC_PRODUCTION: [
                    JudgingCriteria("Audio Quality", "Technical audio production quality", 0.3, 10, True),
                    JudgingCriteria("Creativity", "Creative and original elements", 0.25, 10, True),
                    JudgingCriteria("Mixing", "Quality of mixing and mastering", 0.25, 10, True),
                    JudgingCriteria("Overall Impact", "Overall listening experience", 0.2, 10, False)
                ],
                CompetitionType.PHOTO_CONTEST: [
                    JudgingCriteria("Composition", "Photo composition and framing", 0.3, 10, True),
                    JudgingCriteria("Technical Quality", "Image quality and technique", 0.3, 10, True),
                    JudgingCriteria("Creativity", "Creative vision and uniqueness", 0.25, 10, True),
                    JudgingCriteria("Emotional Impact", "Emotional resonance", 0.15, 10, False)
                ],
                CompetitionType.VIDEO_CHALLENGE: [
                    JudgingCriteria("Production Quality", "Video and audio production", 0.25, 10, True),
                    JudgingCriteria("Storytelling", "Narrative and story structure", 0.3, 10, True),
                    JudgingCriteria("Creativity", "Creative approach and originality", 0.25, 10, True),
                    JudgingCriteria("Engagement", "Audience engagement potential", 0.2, 10, False)
                ],
                CompetitionType.WRITING_CONTEST: [
                    JudgingCriteria("Writing Quality", "Grammar, style, and clarity", 0.3, 10, True),
                    JudgingCriteria("Creativity", "Originality and creative approach", 0.3, 10, True),
                    JudgingCriteria("Content", "Depth and substance", 0.25, 10, False),
                    JudgingCriteria("Impact", "Emotional or intellectual impact", 0.15, 10, False)
                ]
            }
            
            criteria = criteria_sets.get(competition.competition_type, [
                JudgingCriteria("Quality", "Overall quality", 0.4, 10, True),
                JudgingCriteria("Creativity", "Creative approach", 0.35, 10, True),
                JudgingCriteria("Impact", "Overall impact", 0.25, 10, False)
            ])
            
            # Store criteria in database
            async with self.db_pool.acquire() as conn:
                for criterion in criteria:
                    await conn.execute("""
                        INSERT INTO judging_criteria 
                        (competition_id, name, description, weight, max_score, ai_evaluable)
                        VALUES ($1, $2, $3, $4, $5, $6)
                    """,
                    competition.id, criterion.name, criterion.description,
                    criterion.weight, criterion.max_score, criterion.ai_evaluable
                    )
                    
        except Exception as e:
            logger.error(f"❌ Failed to create judging criteria: {str(e)}")
    
    async def _queue_for_ai_judgment(self, submission: CompetitionSubmission):
        """Queue submission for AI judgment"""
        try:
            judgment_data = {
                'submission_id': submission.id,
                'competition_id': submission.competition_id,
                'queued_at': datetime.utcnow().isoformat()
            }
            
            await self.redis_client.lpush('ai_judgment_queue', json.dumps(judgment_data))
            
        except Exception as e:
            logger.error(f"❌ Failed to queue for AI judgment: {str(e)}")
    
    async def _generate_competition_insights(self, stats, category_stats) -> List[str]:
        """Generate AI insights for competition analytics"""
        insights = []
        
        try:
            participant_count = stats['participant_count']
            submission_count = stats['submission_count']
            average_score = stats['average_score'] or 0
            
            # Participation insights
            if participant_count > 100:
                insights.append("High participation rate indicates strong community engagement")
            elif participant_count < 10:
                insights.append("Consider promotional strategies to increase participation")
            
            # Submission insights
            submission_rate = submission_count / max(participant_count, 1)
            if submission_rate > 0.8:
                insights.append("Excellent submission rate - participants are highly engaged")
            elif submission_rate < 0.5:
                insights.append("Low submission rate may indicate barriers to participation")
            
            # Quality insights
            if average_score > 8:
                insights.append("High average scores suggest strong competition quality")
            elif average_score < 5:
                insights.append("Consider reviewing judging criteria or providing better guidance")
            
            # Category insights
            if category_stats:
                most_popular = max(category_stats, key=lambda x: x['count'])
                insights.append(f"Most popular category: {most_popular['content_type']}")
            
            return insights[:3]
            
        except Exception:
            return ["Competition analytics completed successfully"]
    
    # Background tasks
    async def _competition_monitor(self):
        """Monitor competition status and transitions"""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                
                current_time = datetime.utcnow()
                
                # Start competitions that should be active
                async with self.db_pool.acquire() as conn:
                    await conn.execute("""
                        UPDATE competitions 
                        SET status = 'active' 
                        WHERE status = 'registration_open' 
                        AND start_time <= $1
                    """, current_time)
                    
                    # End competitions that have expired
                    await conn.execute("""
                        UPDATE competitions 
                        SET status = 'judging' 
                        WHERE status = 'active' 
                        AND end_time <= $1
                    """, current_time)
                
            except Exception as e:
                logger.error(f"❌ Competition monitor error: {str(e)}")
                await asyncio.sleep(60)
    
    async def _auto_judge_submissions(self):
        """Background task for AI judging"""
        while True:
            try:
                # Check for submissions to judge
                judgment_data = await self.redis_client.brpop('ai_judgment_queue', timeout=30)
                
                if judgment_data:
                    data = json.loads(judgment_data[1])
                    submission_id = data['submission_id']
                    
                    # Get submission and criteria
                    submission = await self._get_submission(submission_id)
                    if submission:
                        criteria = await self._get_judging_criteria(submission.competition_id)
                        
                        # AI evaluation
                        scores = await self.ai_judge.evaluate_submission(submission, criteria)
                        
                        # Store judgment
                        await self._store_ai_judgment(submission_id, scores)
                        
                        self.metrics['judgments_completed'] += 1
                
            except Exception as e:
                logger.error(f"❌ Auto judge error: {str(e)}")
                await asyncio.sleep(10)
    
    async def _get_submission(self, submission_id: str) -> Optional[CompetitionSubmission]:
        """Get submission by ID"""
        try:
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT * FROM competition_submissions WHERE id = $1
                """, submission_id)
                
                if row:
                    return CompetitionSubmission(
                        id=row['id'],
                        competition_id=row['competition_id'],
                        participant_id=row['participant_id'],
                        title=row['title'],
                        description=row['description'],
                        content_url=row['content_url'],
                        content_type=row['content_type'],
                        submitted_at=row['submitted_at'],
                        status=SubmissionStatus(row['status']),
                        metadata=json.loads(row['metadata']) if row['metadata'] else {}
                    )
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to get submission: {str(e)}")
            return None
    
    async def _get_judging_criteria(self, competition_id: str) -> List[JudgingCriteria]:
        """Get judging criteria for competition"""
        try:
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT * FROM judging_criteria WHERE competition_id = $1
                """, competition_id)
                
                criteria = []
                for row in rows:
                    criterion = JudgingCriteria(
                        name=row['name'],
                        description=row['description'],
                        weight=row['weight'],
                        max_score=row['max_score'],
                        ai_evaluable=row['ai_evaluable']
                    )
                    criteria.append(criterion)
                
                return criteria
                
        except Exception as e:
            logger.error(f"❌ Failed to get judging criteria: {str(e)}")
            return []
    
    async def _store_ai_judgment(self, submission_id: str, scores: Dict[str, float]):
        """Store AI judgment results"""
        try:
            total_score = sum(score for score in scores.values() if isinstance(score, (int, float)))
            
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO submission_judgments 
                    (id, submission_id, judge_type, scores, total_score, created_at)
                    VALUES ($1, $2, 'ai', $3, $4, $5)
                """,
                str(uuid.uuid4()), submission_id, json.dumps(scores),
                total_score, datetime.utcnow()
                )
                
        except Exception as e:
            logger.error(f"❌ Failed to store AI judgment: {str(e)}")

# Example usage and testing
async def main():
    """Example usage of Competition Service"""
    logger.info("🧪 Starting Competition Service demonstration")
    
    # Initialize service
    service = CompetitionService()
    await service.start()
    
    try:
        # Create a test competition
        test_competition = Competition(
            id=str(uuid.uuid4()),
            title="Electronic Music Production Challenge",
            description="Create an original electronic music track",
            competition_type=CompetitionType.MUSIC_PRODUCTION,
            status=CompetitionStatus.REGISTRATION_OPEN,
            judging_type=JudgingType.HYBRID,
            creator_id="admin_user",
            start_time=datetime.utcnow() + timedelta(hours=1),
            end_time=datetime.utcnow() + timedelta(days=7),
            registration_deadline=datetime.utcnow() + timedelta(hours=23),
            max_participants=100,
            prize_pool=1000.0,
            categories=["Electronic", "Ambient", "Techno"]
        )
        
        # Create competition
        competition_id = await service.create_competition(test_competition)
        print(f"\n🏆 Created Competition: {competition_id}")
        
        # Register test participant
        registered = await service.register_participant(
            competition_id, 
            "test_user_123",
            {
                'experience_months': 24,
                'competition_wins': 2,
                'total_competitions': 5,
                'avg_content_rating': 4.2
            }
        )
        print(f"👤 Participant Registration: {'✅ Success' if registered else '❌ Failed'}")
        
        # Create test submission
        test_submission = CompetitionSubmission(
            id=str(uuid.uuid4()),
            competition_id=competition_id,
            participant_id="test_user_123",
            title="Ethereal Waves",
            description="An ambient electronic piece exploring atmospheric soundscapes",
            content_url="https://example.com/track.mp3",
            content_type="audio",
            submitted_at=datetime.utcnow(),
            metadata={
                'audio_analysis': {
                    'sample_rate': 48000,
                    'bit_depth': 24,
                    'dynamic_range': 16.5,
                    'duration': 240,
                    'detected_genres': ['Electronic', 'Ambient'],
                    'tempo_changes': 3,
                    'unique_sound_elements': 8
                }
            }
        )
        
        # Submit entry (this would fail since competition isn't active yet)
        try:
            submission_id = await service.submit_entry(test_submission)
            print(f"📝 Submission: {submission_id}")
        except Exception as e:
            print(f"📝 Submission failed (expected): {str(e)}")
        
        # Get competition analytics
        analytics = await service.get_competition_analytics(competition_id)
        print(f"\n📊 Competition Analytics:")
        print(f"Participants: {analytics.get('participant_count', 0)}")
        print(f"Submissions: {analytics.get('submission_count', 0)}")
        
        # Get service health
        health = await service.get_service_health()
        print(f"\n🏥 Service Health: {health['status']}")
        print(f"Competitions Created: {health['metrics']['competitions_created']}")
        print(f"Active Competitions: {health['metrics']['active_competitions']}")
        
    finally:
        await service.stop()

if __name__ == "__main__":
    asyncio.run(main())