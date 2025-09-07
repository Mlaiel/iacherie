"""Voice Challenge Manager - Advanced Voice Gamification Challenge System

Sophisticated voice challenge and contest management system for creator engagement.
Handles voice competitions, skill challenges, and community-driven voice events.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum
from dataclasses import dataclass, field
import json
import uuid
import random

class ChallengeType(Enum):
    """Voice challenge types"""
    VOCAL_RANGE = "vocal_range"
    PITCH_ACCURACY = "pitch_accuracy"
    RHYTHM_PRECISION = "rhythm_precision"
    VOICE_IMITATION = "voice_imitation"
    ACCENT_CHALLENGE = "accent_challenge"
    SPEED_CHALLENGE = "speed_challenge"
    HARMONY_CREATION = "harmony_creation"
    BEATBOXING = "beatboxing"
    VOCAL_EFFECTS = "vocal_effects"
    TONGUE_TWISTER = "tongue_twister"
    EMOTION_EXPRESSION = "emotion_expression"
    STORYTELLING = "storytelling"
    IMPROVISATION = "improvisation"
    COLLABORATION = "collaboration"
    REMIX_CHALLENGE = "remix_challenge"

class ChallengeDifficulty(Enum):
    """Challenge difficulty levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    LEGENDARY = "legendary"

class ChallengeStatus(Enum):
    """Challenge status"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"

class ParticipationStatus(Enum):
    """Participation status"""
    REGISTERED = "registered"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    REVIEWED = "reviewed"
    SCORED = "scored"
    DISQUALIFIED = "disqualified"

class JudgingMethod(Enum):
    """Challenge judging methods"""
    AUTOMATED = "automated"
    PEER_VOTING = "peer_voting"
    EXPERT_PANEL = "expert_panel"
    HYBRID = "hybrid"
    COMMUNITY = "community"

@dataclass
class ChallengeRequirements:
    """Challenge participation requirements"""
    min_voice_quality: float  # 0.0 to 1.0
    required_equipment: List[str]
    voice_range_requirement: Optional[Tuple[str, str]]  # (min_note, max_note)
    experience_level: Optional[int]  # 1-10
    skill_prerequisites: List[str]
    time_limit_seconds: Optional[int]
    max_attempts: int = 3
    language_requirements: List[str] = field(default_factory=list)

@dataclass
class ChallengeRewards:
    """Challenge rewards and prizes"""
    points: int
    badges: List[str]
    monetary_prize: float
    voice_coaching_sessions: int
    platform_features: List[str]
    collaboration_opportunities: List[str]
    mentorship_access: bool = False
    exclusive_content_access: bool = False

@dataclass
class ChallengeSubmission:
    """Voice challenge submission"""
    submission_id: str
    participant_id: str
    challenge_id: str
    audio_file_path: str
    submission_text: Optional[str]
    metadata: Dict[str, Any]
    submitted_at: datetime
    status: ParticipationStatus
    scores: Dict[str, float] = field(default_factory=dict)
    feedback: List[str] = field(default_factory=list)
    peer_votes: int = 0
    expert_ratings: List[float] = field(default_factory=list)

@dataclass
class Challenge:
    """Voice challenge definition"""
    challenge_id: str
    title: str
    description: str
    challenge_type: ChallengeType
    difficulty: ChallengeDifficulty
    requirements: ChallengeRequirements
    rewards: ChallengeRewards
    judging_method: JudgingMethod
    start_time: datetime
    end_time: datetime
    max_participants: Optional[int]
    status: ChallengeStatus
    creator_id: str
    sponsors: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class ChallengeParticipant:
    """Challenge participant data"""
    participant_id: str
    creator_id: str
    challenge_id: str
    registration_time: datetime
    status: ParticipationStatus
    submissions: List[str] = field(default_factory=list)  # submission_ids
    total_score: float = 0.0
    rank: Optional[int] = None
    attempts_used: int = 0
    last_activity: datetime = field(default_factory=datetime.now)

@dataclass
class ChallengeLeaderboard:
    """Challenge leaderboard data"""
    challenge_id: str
    participants: List[Tuple[str, float, int]]  # (participant_id, score, rank)
    last_updated: datetime
    total_participants: int
    completion_rate: float
    average_score: float
    top_submissions: List[str]  # submission_ids

class VoiceChallengeManager:
    """Advanced Voice Challenge Management System
    
    Comprehensive system for creating, managing, and judging voice challenges
    with automated scoring, peer voting, and expert evaluation capabilities.
    """
    
    def __init__(self):
        """Initialize voice challenge manager"""
        self.challenges: Dict[str, Challenge] = {}
        self.participants: Dict[str, ChallengeParticipant] = {}
        self.submissions: Dict[str, ChallengeSubmission] = {}
        self.leaderboards: Dict[str, ChallengeLeaderboard] = {}
        self.scoring_algorithms: Dict[ChallengeType, callable] = {}
        self.challenge_templates: Dict[str, Dict[str, Any]] = {}
        
        self._initialize_scoring_algorithms()
        self._initialize_challenge_templates()
    
    def _initialize_scoring_algorithms(self):
        """Initialize automated scoring algorithms for different challenge types"""
        
        self.scoring_algorithms = {
            ChallengeType.VOCAL_RANGE: self._score_vocal_range,
            ChallengeType.PITCH_ACCURACY: self._score_pitch_accuracy,
            ChallengeType.RHYTHM_PRECISION: self._score_rhythm_precision,
            ChallengeType.VOICE_IMITATION: self._score_voice_imitation,
            ChallengeType.ACCENT_CHALLENGE: self._score_accent_challenge,
            ChallengeType.SPEED_CHALLENGE: self._score_speed_challenge,
            ChallengeType.HARMONY_CREATION: self._score_harmony_creation,
            ChallengeType.BEATBOXING: self._score_beatboxing,
            ChallengeType.VOCAL_EFFECTS: self._score_vocal_effects,
            ChallengeType.TONGUE_TWISTER: self._score_tongue_twister,
            ChallengeType.EMOTION_EXPRESSION: self._score_emotion_expression,
            ChallengeType.STORYTELLING: self._score_storytelling,
            ChallengeType.IMPROVISATION: self._score_improvisation
        }
    
    def _initialize_challenge_templates(self):
        """Initialize predefined challenge templates"""
        
        self.challenge_templates = {
            "weekly_range_challenge": {
                "title": "Weekly Vocal Range Challenge",
                "description": "Show off your vocal range with the highest and lowest notes you can hit cleanly",
                "type": ChallengeType.VOCAL_RANGE,
                "difficulty": ChallengeDifficulty.INTERMEDIATE,
                "duration_days": 7,
                "rewards": {"points": 100, "badges": ["range_master"]}
            },
            "pitch_perfect": {
                "title": "Pitch Perfect Challenge",
                "description": "Sing a melody with perfect pitch accuracy",
                "type": ChallengeType.PITCH_ACCURACY,
                "difficulty": ChallengeDifficulty.ADVANCED,
                "duration_days": 3,
                "rewards": {"points": 200, "badges": ["pitch_perfect"]}
            },
            "beatbox_battle": {
                "title": "Beatbox Battle",
                "description": "Create an impressive beatbox sequence with rhythm and creativity",
                "type": ChallengeType.BEATBOXING,
                "difficulty": ChallengeDifficulty.EXPERT,
                "duration_days": 5,
                "rewards": {"points": 300, "badges": ["beatbox_champion"]}
            },
            "accent_master": {
                "title": "Accent Master Challenge",
                "description": "Perform the same text in 3 different accents with authenticity",
                "type": ChallengeType.ACCENT_CHALLENGE,
                "difficulty": ChallengeDifficulty.ADVANCED,
                "duration_days": 10,
                "rewards": {"points": 250, "badges": ["accent_master"]}
            }
        }
    
    async def create_challenge(
        self,
        title: str,
        description: str,
        challenge_type: ChallengeType,
        difficulty: ChallengeDifficulty,
        duration_days: int,
        creator_id: str,
        requirements: Optional[Dict[str, Any]] = None,
        rewards: Optional[Dict[str, Any]] = None,
        judging_method: JudgingMethod = JudgingMethod.AUTOMATED,
        max_participants: Optional[int] = None
    ) -> Challenge:
        """Create new voice challenge"""
        
        challenge_id = str(uuid.uuid4())
        start_time = datetime.now()
        end_time = start_time + timedelta(days=duration_days)
        
        # Set default requirements if not provided
        if not requirements:
            requirements = self._get_default_requirements(challenge_type, difficulty)
        
        challenge_requirements = ChallengeRequirements(
            min_voice_quality=requirements.get("min_voice_quality", 0.6),
            required_equipment=requirements.get("required_equipment", ["microphone"]),
            voice_range_requirement=requirements.get("voice_range_requirement"),
            experience_level=requirements.get("experience_level"),
            skill_prerequisites=requirements.get("skill_prerequisites", []),
            time_limit_seconds=requirements.get("time_limit_seconds"),
            max_attempts=requirements.get("max_attempts", 3),
            language_requirements=requirements.get("language_requirements", ["en"])
        )
        
        # Set default rewards if not provided
        if not rewards:
            rewards = self._get_default_rewards(difficulty)
        
        challenge_rewards = ChallengeRewards(
            points=rewards.get("points", 100),
            badges=rewards.get("badges", []),
            monetary_prize=rewards.get("monetary_prize", 0.0),
            voice_coaching_sessions=rewards.get("voice_coaching_sessions", 0),
            platform_features=rewards.get("platform_features", []),
            collaboration_opportunities=rewards.get("collaboration_opportunities", []),
            mentorship_access=rewards.get("mentorship_access", False),
            exclusive_content_access=rewards.get("exclusive_content_access", False)
        )
        
        challenge = Challenge(
            challenge_id=challenge_id,
            title=title,
            description=description,
            challenge_type=challenge_type,
            difficulty=difficulty,
            requirements=challenge_requirements,
            rewards=challenge_rewards,
            judging_method=judging_method,
            start_time=start_time,
            end_time=end_time,
            max_participants=max_participants,
            status=ChallengeStatus.ACTIVE,
            creator_id=creator_id
        )
        
        self.challenges[challenge_id] = challenge
        
        # Initialize leaderboard
        self.leaderboards[challenge_id] = ChallengeLeaderboard(
            challenge_id=challenge_id,
            participants=[],
            last_updated=datetime.now(),
            total_participants=0,
            completion_rate=0.0,
            average_score=0.0,
            top_submissions=[]
        )
        
        return challenge
    
    async def create_challenge_from_template(
        self,
        template_name: str,
        creator_id: str,
        customizations: Optional[Dict[str, Any]] = None
    ) -> Challenge:
        """Create challenge from predefined template"""
        
        if template_name not in self.challenge_templates:
            raise ValueError(f"Template '{template_name}' not found")
        
        template = self.challenge_templates[template_name].copy()
        
        # Apply customizations
        if customizations:
            template.update(customizations)
        
        return await self.create_challenge(
            title=template["title"],
            description=template["description"],
            challenge_type=template["type"],
            difficulty=template["difficulty"],
            duration_days=template["duration_days"],
            creator_id=creator_id,
            rewards=template.get("rewards")
        )
    
    async def register_participant(
        self,
        challenge_id: str,
        creator_id: str
    ) -> ChallengeParticipant:
        """Register participant for challenge"""
        
        if challenge_id not in self.challenges:
            raise ValueError(f"Challenge {challenge_id} not found")
        
        challenge = self.challenges[challenge_id]
        
        # Check if challenge is active
        if challenge.status != ChallengeStatus.ACTIVE:
            raise ValueError("Challenge is not active")
        
        # Check if registration is still open
        if datetime.now() > challenge.end_time:
            raise ValueError("Challenge registration is closed")
        
        # Check max participants limit
        if challenge.max_participants:
            current_participants = len([
                p for p in self.participants.values() 
                if p.challenge_id == challenge_id
            ])
            if current_participants >= challenge.max_participants:
                raise ValueError("Challenge is full")
        
        # Check if already registered
        existing_participant = None
        for participant in self.participants.values():
            if (participant.challenge_id == challenge_id and 
                participant.creator_id == creator_id):
                existing_participant = participant
                break
        
        if existing_participant:
            return existing_participant
        
        # Create new participant
        participant_id = str(uuid.uuid4())
        participant = ChallengeParticipant(
            participant_id=participant_id,
            creator_id=creator_id,
            challenge_id=challenge_id,
            registration_time=datetime.now(),
            status=ParticipationStatus.REGISTERED
        )
        
        self.participants[participant_id] = participant
        
        # Update leaderboard
        await self._update_leaderboard(challenge_id)
        
        return participant
    
    async def submit_challenge_entry(
        self,
        challenge_id: str,
        creator_id: str,
        audio_file_path: str,
        submission_text: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ChallengeSubmission:
        """Submit entry for voice challenge"""
        
        if challenge_id not in self.challenges:
            raise ValueError(f"Challenge {challenge_id} not found")
        
        challenge = self.challenges[challenge_id]
        
        # Find participant
        participant = None
        for p in self.participants.values():
            if (p.challenge_id == challenge_id and 
                p.creator_id == creator_id):
                participant = p
                break
        
        if not participant:
            raise ValueError("Creator not registered for this challenge")
        
        # Check submission deadline
        if datetime.now() > challenge.end_time:
            raise ValueError("Challenge submission deadline has passed")
        
        # Check attempt limit
        if participant.attempts_used >= challenge.requirements.max_attempts:
            raise ValueError("Maximum attempts exceeded")
        
        # Validate submission
        await self._validate_submission(audio_file_path, challenge)
        
        # Create submission
        submission_id = str(uuid.uuid4())
        submission = ChallengeSubmission(
            submission_id=submission_id,
            participant_id=participant.participant_id,
            challenge_id=challenge_id,
            audio_file_path=audio_file_path,
            submission_text=submission_text,
            metadata=metadata or {},
            submitted_at=datetime.now(),
            status=ParticipationStatus.SUBMITTED
        )
        
        self.submissions[submission_id] = submission
        
        # Update participant
        participant.submissions.append(submission_id)
        participant.attempts_used += 1
        participant.status = ParticipationStatus.SUBMITTED
        participant.last_activity = datetime.now()
        
        # Auto-score if automated judging
        if challenge.judging_method == JudgingMethod.AUTOMATED:
            await self._auto_score_submission(submission)
        
        return submission
    
    async def score_submission(
        self,
        submission_id: str,
        scores: Dict[str, float],
        scorer_id: Optional[str] = None
    ):
        """Score challenge submission"""
        
        if submission_id not in self.submissions:
            raise ValueError(f"Submission {submission_id} not found")
        
        submission = self.submissions[submission_id]
        challenge = self.challenges[submission.challenge_id]
        
        # Update submission scores
        submission.scores.update(scores)
        submission.status = ParticipationStatus.SCORED
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(submission, challenge)
        
        # Update participant score
        participant = self.participants[submission.participant_id]
        participant.total_score = max(participant.total_score, overall_score)
        
        # Update leaderboard
        await self._update_leaderboard(submission.challenge_id)
    
    async def vote_on_submission(
        self,
        submission_id: str,
        voter_id: str,
        vote_score: float
    ):
        """Vote on submission for peer voting"""
        
        if submission_id not in self.submissions:
            raise ValueError(f"Submission {submission_id} not found")
        
        submission = self.submissions[submission_id]
        challenge = self.challenges[submission.challenge_id]
        
        if challenge.judging_method not in [JudgingMethod.PEER_VOTING, JudgingMethod.HYBRID, JudgingMethod.COMMUNITY]:
            raise ValueError("Peer voting not enabled for this challenge")
        
        # Record vote (simplified - would need vote tracking)
        submission.peer_votes += 1
        
        # Add to scores
        if "peer_voting" not in submission.scores:
            submission.scores["peer_voting"] = vote_score
        else:
            # Average with existing votes
            current_avg = submission.scores["peer_voting"]
            submission.scores["peer_voting"] = (current_avg + vote_score) / 2
        
        # Update overall score
        overall_score = self._calculate_overall_score(submission, challenge)
        participant = self.participants[submission.participant_id]
        participant.total_score = max(participant.total_score, overall_score)
        
        # Update leaderboard
        await self._update_leaderboard(submission.challenge_id)
    
    async def get_challenge_leaderboard(
        self, 
        challenge_id: str,
        limit: Optional[int] = None
    ) -> ChallengeLeaderboard:
        """Get challenge leaderboard"""
        
        if challenge_id not in self.leaderboards:
            raise ValueError(f"Leaderboard for challenge {challenge_id} not found")
        
        leaderboard = self.leaderboards[challenge_id]
        
        if limit:
            limited_participants = leaderboard.participants[:limit]
            return ChallengeLeaderboard(
                challenge_id=leaderboard.challenge_id,
                participants=limited_participants,
                last_updated=leaderboard.last_updated,
                total_participants=leaderboard.total_participants,
                completion_rate=leaderboard.completion_rate,
                average_score=leaderboard.average_score,
                top_submissions=leaderboard.top_submissions
            )
        
        return leaderboard
    
    async def get_active_challenges(
        self,
        challenge_type: Optional[ChallengeType] = None,
        difficulty: Optional[ChallengeDifficulty] = None
    ) -> List[Challenge]:
        """Get active challenges with optional filtering"""
        
        active_challenges = [
            challenge for challenge in self.challenges.values()
            if challenge.status == ChallengeStatus.ACTIVE and
               datetime.now() <= challenge.end_time
        ]
        
        if challenge_type:
            active_challenges = [
                c for c in active_challenges 
                if c.challenge_type == challenge_type
            ]
        
        if difficulty:
            active_challenges = [
                c for c in active_challenges 
                if c.difficulty == difficulty
            ]
        
        return active_challenges
    
    async def get_participant_challenges(
        self,
        creator_id: str,
        status: Optional[ParticipationStatus] = None
    ) -> List[Tuple[Challenge, ChallengeParticipant]]:
        """Get challenges for a participant"""
        
        participant_challenges = []
        
        for participant in self.participants.values():
            if participant.creator_id == creator_id:
                if not status or participant.status == status:
                    challenge = self.challenges[participant.challenge_id]
                    participant_challenges.append((challenge, participant))
        
        return participant_challenges
    
    async def end_challenge(self, challenge_id: str):
        """End challenge and finalize results"""
        
        if challenge_id not in self.challenges:
            raise ValueError(f"Challenge {challenge_id} not found")
        
        challenge = self.challenges[challenge_id]
        challenge.status = ChallengeStatus.COMPLETED
        challenge.updated_at = datetime.now()
        
        # Finalize all scoring
        await self._finalize_challenge_scoring(challenge_id)
        
        # Award prizes
        await self._award_challenge_prizes(challenge_id)
        
        # Generate final leaderboard
        await self._update_leaderboard(challenge_id)
    
    # Scoring algorithm implementations
    
    async def _auto_score_submission(self, submission: ChallengeSubmission):
        """Automatically score submission based on challenge type"""
        
        challenge = self.challenges[submission.challenge_id]
        
        if challenge.challenge_type in self.scoring_algorithms:
            scoring_func = self.scoring_algorithms[challenge.challenge_type]
            scores = await scoring_func(submission)
            submission.scores.update(scores)
            submission.status = ParticipationStatus.SCORED
    
    async def _score_vocal_range(self, submission: ChallengeSubmission) -> Dict[str, float]:
        """Score vocal range challenge"""
        # Simulate audio analysis for vocal range
        # In real implementation would use pitch detection algorithms
        
        scores = {
            "range_width": random.uniform(0.6, 1.0),
            "note_clarity": random.uniform(0.7, 1.0),
            "pitch_stability": random.uniform(0.5, 0.9),
            "technique": random.uniform(0.6, 0.95)
        }
        
        return scores
    
    async def _score_pitch_accuracy(self, submission: ChallengeSubmission) -> Dict[str, float]:
        """Score pitch accuracy challenge"""
        scores = {
            "pitch_precision": random.uniform(0.7, 1.0),
            "intonation": random.uniform(0.6, 0.95),
            "consistency": random.uniform(0.65, 0.9),
            "musical_expression": random.uniform(0.5, 0.85)
        }
        
        return scores
    
    async def _score_rhythm_precision(self, submission: ChallengeSubmission) -> Dict[str, float]:
        """Score rhythm precision challenge"""
        scores = {
            "timing_accuracy": random.uniform(0.6, 1.0),
            "tempo_consistency": random.uniform(0.7, 0.95),
            "rhythmic_complexity": random.uniform(0.5, 0.9),
            "groove": random.uniform(0.6, 0.85)
        }
        
        return scores
    
    async def _score_voice_imitation(self, submission: ChallengeSubmission) -> Dict[str, float]:
        """Score voice imitation challenge"""
        scores = {
            "accuracy": random.uniform(0.5, 0.95),
            "character_capture": random.uniform(0.6, 0.9),
            "vocal_technique": random.uniform(0.7, 1.0),
            "entertainment_value": random.uniform(0.5, 0.85)
        }
        
        return scores
    
    async def _score_accent_challenge(self, submission: ChallengeSubmission) -> Dict[str, float]:
        """Score accent challenge"""
        scores = {
            "authenticity": random.uniform(0.6, 0.95),
            "consistency": random.uniform(0.7, 0.9),
            "pronunciation": random.uniform(0.65, 1.0),
            "cultural_sensitivity": random.uniform(0.8, 1.0)
        }
        
        return scores
    
    async def _score_speed_challenge(self, submission: ChallengeSubmission) -> Dict[str, float]:
        """Score speed challenge"""
        scores = {
            "speed": random.uniform(0.7, 1.0),
            "clarity": random.uniform(0.5, 0.9),
            "accuracy": random.uniform(0.6, 0.95),
            "breathing_technique": random.uniform(0.6, 0.85)
        }
        
        return scores
    
    async def _score_harmony_creation(self, submission: ChallengeSubmission) -> Dict[str, float]:
        """Score harmony creation challenge"""
        scores = {
            "harmonic_accuracy": random.uniform(0.6, 0.95),
            "creativity": random.uniform(0.5, 0.9),
            "blend": random.uniform(0.7, 1.0),
            "musical_understanding": random.uniform(0.65, 0.85)
        }
        
        return scores
    
    async def _score_beatboxing(self, submission: ChallengeSubmission) -> Dict[str, float]:
        """Score beatboxing challenge"""
        scores = {
            "rhythm_complexity": random.uniform(0.6, 1.0),
            "sound_variety": random.uniform(0.5, 0.95),
            "creativity": random.uniform(0.7, 0.9),
            "technical_skill": random.uniform(0.6, 0.85)
        }
        
        return scores
    
    async def _score_vocal_effects(self, submission: ChallengeSubmission) -> Dict[str, float]:
        """Score vocal effects challenge"""
        scores = {
            "effect_quality": random.uniform(0.6, 0.9),
            "creativity": random.uniform(0.5, 0.95),
            "technical_execution": random.uniform(0.7, 1.0),
            "originality": random.uniform(0.5, 0.85)
        }
        
        return scores
    
    async def _score_tongue_twister(self, submission: ChallengeSubmission) -> Dict[str, float]:
        """Score tongue twister challenge"""
        scores = {
            "speed": random.uniform(0.6, 1.0),
            "accuracy": random.uniform(0.7, 0.95),
            "clarity": random.uniform(0.5, 0.9),
            "consistency": random.uniform(0.65, 0.85)
        }
        
        return scores
    
    async def _score_emotion_expression(self, submission: ChallengeSubmission) -> Dict[str, float]:
        """Score emotion expression challenge"""
        scores = {
            "emotional_range": random.uniform(0.6, 0.95),
            "authenticity": random.uniform(0.7, 1.0),
            "vocal_technique": random.uniform(0.5, 0.9),
            "believability": random.uniform(0.6, 0.85)
        }
        
        return scores
    
    async def _score_storytelling(self, submission: ChallengeSubmission) -> Dict[str, float]:
        """Score storytelling challenge"""
        scores = {
            "narrative_flow": random.uniform(0.6, 0.9),
            "character_voices": random.uniform(0.5, 0.95),
            "engagement": random.uniform(0.7, 1.0),
            "pacing": random.uniform(0.65, 0.85)
        }
        
        return scores
    
    async def _score_improvisation(self, submission: ChallengeSubmission) -> Dict[str, float]:
        """Score improvisation challenge"""
        scores = {
            "creativity": random.uniform(0.6, 1.0),
            "spontaneity": random.uniform(0.5, 0.9),
            "musical_coherence": random.uniform(0.7, 0.95),
            "risk_taking": random.uniform(0.5, 0.85)
        }
        
        return scores
    
    # Helper methods
    
    def _get_default_requirements(
        self, 
        challenge_type: ChallengeType, 
        difficulty: ChallengeDifficulty
    ) -> Dict[str, Any]:
        """Get default requirements for challenge type and difficulty"""
        
        base_requirements = {
            "min_voice_quality": 0.6,
            "required_equipment": ["microphone"],
            "max_attempts": 3,
            "language_requirements": ["en"]
        }
        
        # Adjust based on difficulty
        if difficulty == ChallengeDifficulty.BEGINNER:
            base_requirements["min_voice_quality"] = 0.4
            base_requirements["max_attempts"] = 5
        elif difficulty == ChallengeDifficulty.EXPERT:
            base_requirements["min_voice_quality"] = 0.8
            base_requirements["max_attempts"] = 1
        elif difficulty == ChallengeDifficulty.LEGENDARY:
            base_requirements["min_voice_quality"] = 0.9
            base_requirements["max_attempts"] = 1
            base_requirements["experience_level"] = 8
        
        # Adjust based on challenge type
        if challenge_type == ChallengeType.BEATBOXING:
            base_requirements["time_limit_seconds"] = 60
        elif challenge_type == ChallengeType.SPEED_CHALLENGE:
            base_requirements["time_limit_seconds"] = 30
        elif challenge_type == ChallengeType.STORYTELLING:
            base_requirements["time_limit_seconds"] = 300
        
        return base_requirements
    
    def _get_default_rewards(self, difficulty: ChallengeDifficulty) -> Dict[str, Any]:
        """Get default rewards for difficulty level"""
        
        rewards = {
            "points": 100,
            "badges": [],
            "monetary_prize": 0.0,
            "voice_coaching_sessions": 0
        }
        
        if difficulty == ChallengeDifficulty.BEGINNER:
            rewards["points"] = 50
            rewards["badges"] = ["first_challenge"]
        elif difficulty == ChallengeDifficulty.INTERMEDIATE:
            rewards["points"] = 100
            rewards["badges"] = ["challenge_warrior"]
        elif difficulty == ChallengeDifficulty.ADVANCED:
            rewards["points"] = 200
            rewards["badges"] = ["advanced_challenger"]
            rewards["voice_coaching_sessions"] = 1
        elif difficulty == ChallengeDifficulty.EXPERT:
            rewards["points"] = 500
            rewards["badges"] = ["expert_challenger"]
            rewards["monetary_prize"] = 50.0
            rewards["voice_coaching_sessions"] = 2
        elif difficulty == ChallengeDifficulty.LEGENDARY:
            rewards["points"] = 1000
            rewards["badges"] = ["legendary_champion"]
            rewards["monetary_prize"] = 200.0
            rewards["voice_coaching_sessions"] = 5
            rewards["mentorship_access"] = True
        
        return rewards
    
    async def _validate_submission(self, audio_file_path: str, challenge: Challenge):
        """Validate challenge submission"""
        # Simulate audio validation
        # In real implementation would check file format, quality, duration, etc.
        pass
    
    def _calculate_overall_score(
        self, 
        submission: ChallengeSubmission, 
        challenge: Challenge
    ) -> float:
        """Calculate overall score from individual scores"""
        
        if not submission.scores:
            return 0.0
        
        # Weight scores based on challenge type
        weights = self._get_score_weights(challenge.challenge_type)
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for metric, score in submission.scores.items():
            weight = weights.get(metric, 1.0)
            weighted_sum += score * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _get_score_weights(self, challenge_type: ChallengeType) -> Dict[str, float]:
        """Get scoring weights for challenge type"""
        
        # Default weights
        default_weights = {
            "technical_skill": 2.0,
            "creativity": 1.5,
            "accuracy": 2.0,
            "entertainment_value": 1.0
        }
        
        # Challenge-specific weights
        if challenge_type == ChallengeType.PITCH_ACCURACY:
            return {"pitch_precision": 3.0, "consistency": 2.0, "intonation": 2.0, "musical_expression": 1.0}
        elif challenge_type == ChallengeType.BEATBOXING:
            return {"rhythm_complexity": 2.5, "creativity": 2.0, "sound_variety": 2.0, "technical_skill": 1.5}
        
        return default_weights
    
    async def _update_leaderboard(self, challenge_id: str):
        """Update challenge leaderboard"""
        
        # Get all participants for challenge
        challenge_participants = [
            p for p in self.participants.values()
            if p.challenge_id == challenge_id
        ]
        
        # Sort by score
        sorted_participants = sorted(
            challenge_participants,
            key=lambda p: p.total_score,
            reverse=True
        )
        
        # Update ranks
        leaderboard_data = []
        for i, participant in enumerate(sorted_participants):
            rank = i + 1
            participant.rank = rank
            leaderboard_data.append((participant.creator_id, participant.total_score, rank))
        
        # Calculate statistics
        total_participants = len(challenge_participants)
        completed_participants = len([p for p in challenge_participants if p.status == ParticipationStatus.SCORED])
        completion_rate = completed_participants / total_participants if total_participants > 0 else 0.0
        average_score = sum(p.total_score for p in challenge_participants) / total_participants if total_participants > 0 else 0.0
        
        # Get top submissions
        top_submissions = []
        for participant in sorted_participants[:5]:  # Top 5
            if participant.submissions:
                top_submissions.extend(participant.submissions)
        
        # Update leaderboard
        self.leaderboards[challenge_id] = ChallengeLeaderboard(
            challenge_id=challenge_id,
            participants=leaderboard_data,
            last_updated=datetime.now(),
            total_participants=total_participants,
            completion_rate=completion_rate,
            average_score=average_score,
            top_submissions=top_submissions[:10]  # Top 10 submissions
        )
    
    async def _finalize_challenge_scoring(self, challenge_id: str):
        """Finalize scoring for completed challenge"""
        
        # Score any remaining unscored submissions
        for submission in self.submissions.values():
            if (submission.challenge_id == challenge_id and 
                submission.status == ParticipationStatus.SUBMITTED):
                
                challenge = self.challenges[challenge_id]
                if challenge.judging_method == JudgingMethod.AUTOMATED:
                    await self._auto_score_submission(submission)
    
    async def _award_challenge_prizes(self, challenge_id: str):
        """Award prizes to challenge winners"""
        
        challenge = self.challenges[challenge_id]
        leaderboard = self.leaderboards[challenge_id]
        
        # Award prizes to top performers
        for i, (creator_id, score, rank) in enumerate(leaderboard.participants[:3]):  # Top 3
            
            # Scale rewards based on ranking
            reward_multiplier = 1.0 if rank == 1 else (0.5 if rank == 2 else 0.25)
            
            # Award scaled rewards
            # In real implementation would update creator's profile with rewards
            pass


# Export classes for external use
__all__ = [
    'VoiceChallengeManager',
    'ChallengeType',
    'ChallengeDifficulty', 
    'ChallengeStatus',
    'ParticipationStatus',
    'JudgingMethod',
    'ChallengeRequirements',
    'ChallengeRewards',
    'ChallengeSubmission',
    'Challenge',
    'ChallengeParticipant',
    'ChallengeLeaderboard'
]