"""
Clubhouse Audio Content Crawling Engine

Ultra-advanced industry-grade engine for Clubhouse audio room analysis with AI-powered
voice recognition, content protection, and real-time conversation analytics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is proprietary and confidential. 
Unauthorized copying, distribution, or use is strictly prohibited.
Any violation will result in legal action under German and international law.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator, Tuple
from datetime import datetime, timedelta
import aiohttp
from dataclasses import dataclass
from enum import Enum
import json
import base64

from ..base import BaseCrawlerEngine
from ...core.platforms.clubhouse import ClubhousePlatform
from ...protection.content_guardian import ContentGuardian
from ...ai.content_analyzer import ContentAnalyzer
from ...ai.voice_analyzer import VoiceAnalyzer
from ...ai.conversation_analyzer import ConversationAnalyzer
from ...security.encryption import SecurityManager
from ...monitoring.metrics import MetricsCollector
from ...audio.transcription import AudioTranscriptionService
from ...audio.quality_analyzer import AudioQualityAnalyzer


class RoomStatus(Enum):
    """Clubhouse room status types"""
    LIVE = "live"
    SCHEDULED = "scheduled"
    ENDED = "ended"
    CANCELLED = "cancelled"
    PRIVATE = "private"


class RoomType(Enum):
    """Clubhouse room types"""
    OPEN = "open"
    SOCIAL = "social"  
    CLOSED = "closed"
    PRIVATE_CLUB = "private_club"
    EVENT = "event"


class ParticipantRole(Enum):
    """Participant roles in Clubhouse rooms"""
    MODERATOR = "moderator"
    SPEAKER = "speaker"
    LISTENER = "listener"
    INVITED_SPEAKER = "invited_speaker"
    CLUB_MEMBER = "club_member"


class ConversationQuality(Enum):
    """Conversation quality levels"""
    EXCEPTIONAL = "exceptional"
    HIGH_QUALITY = "high_quality"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"
    SPAM = "spam"


@dataclass
class ClubhouseParticipant:
    """Clubhouse room participant data"""
    user_id: str
    username: str
    display_name: str
    role: ParticipantRole
    join_time: Optional[datetime]
    speaking_time: Optional[float]
    interaction_count: int
    voice_quality_score: float
    expertise_score: float
    engagement_score: float
    follower_count: int
    following_count: int
    bio: str
    profile_photo_url: str
    is_verified: bool
    club_memberships: List[str]


@dataclass
class ClubhouseRoom:
    """Clubhouse room data structure"""
    room_id: str
    title: str
    description: str
    topic: str
    subtopics: List[str]
    status: RoomStatus
    room_type: RoomType
    creator_id: str
    creator_username: str
    club_id: Optional[str]
    club_name: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]
    duration: Optional[float]
    participant_count: int
    peak_participant_count: int
    current_participants: List[ClubhouseParticipant]
    speakers: List[ClubhouseParticipant]
    moderators: List[ClubhouseParticipant]
    listeners: List[ClubhouseParticipant]
    conversation_quality: ConversationQuality
    audio_quality_score: float
    engagement_score: float
    viral_potential: float
    educational_value: float
    entertainment_value: float
    content_fingerprint: str
    protection_level: str
    social_impact_score: float
    monetization_potential: float
    language_detected: str
    transcription_summary: str
    key_discussion_points: List[str]
    sentiment_analysis: Dict[str, float]
    influence_network_data: Dict[str, Any]


@dataclass
class AudioSegment:
    """Audio segment data for analysis"""
    segment_id: str
    room_id: str
    speaker_id: str
    start_timestamp: float
    end_timestamp: float
    duration: float
    audio_url: Optional[str]
    transcription: str
    sentiment_score: float
    quality_score: float
    engagement_indicators: List[str]
    topic_relevance: float
    expertise_markers: List[str]


class ClubhouseEngine(BaseCrawlerEngine):
    """
    Professional Clubhouse crawling engine with advanced audio analytics,
    conversation intelligence, and real-time influence tracking.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.platform = ClubhousePlatform(config.get('clubhouse', {}))
        self.content_guardian = ContentGuardian()
        self.content_analyzer = ContentAnalyzer()
        self.voice_analyzer = VoiceAnalyzer()
        self.conversation_analyzer = ConversationAnalyzer()
        self.security_manager = SecurityManager()
        self.metrics_collector = MetricsCollector()
        self.transcription_service = AudioTranscriptionService()
        self.audio_quality_analyzer = AudioQualityAnalyzer()
        self.logger = logging.getLogger(__name__)
        
        # Clubhouse specific configuration
        self.rate_limit_per_minute = config.get('rate_limit_per_minute', 120)
        self.max_concurrent_requests = config.get('max_concurrent_requests', 8)
        self.enable_voice_analysis = config.get('enable_voice_analysis', True)
        self.enable_transcription = config.get('enable_transcription', True)
        self.min_conversation_quality = config.get('min_conversation_quality', 0.6)
        self.enable_real_time_monitoring = config.get('enable_real_time_monitoring', False)
        
    async def crawl_live_rooms(
        self, 
        topics: List[str] = None,
        languages: List[str] = None,
        min_participants: int = 10,
        room_types: List[RoomType] = None
    ) -> AsyncGenerator[ClubhouseRoom, None]:
        """
        Crawl live Clubhouse rooms with advanced filtering and analysis
        
        Args:
            topics: List of topics to filter by
            languages: List of languages to filter by
            min_participants: Minimum number of participants
            room_types: List of room types to include
            
        Yields:
            ClubhouseRoom: Processed Clubhouse room objects
        """
        self.logger.info("Starting live Clubhouse rooms crawl")
        
        try:
            async with self._create_session() as session:
                room_types = room_types or list(RoomType)
                
                # Get live rooms data
                async for room in self._crawl_live_rooms_data(
                    session, topics, languages, min_participants, room_types
                ):
                    # Process and analyze room
                    processed_room = await self._process_clubhouse_room(room)
                    if processed_room and self._meets_quality_threshold(processed_room):
                        yield processed_room
                        
        except Exception as e:
            self.logger.error(f"Error crawling live rooms: {str(e)}")
            await self.metrics_collector.record_error('clubhouse_crawl_error', str(e))
            raise
            
    async def _crawl_live_rooms_data(
        self,
        session: aiohttp.ClientSession,
        topics: List[str],
        languages: List[str],
        min_participants: int,
        room_types: List[RoomType]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Internal method to crawl live rooms data"""
        
        page_token = None
        max_pages = 20
        page_count = 0
        
        while page_count < max_pages:
            try:
                # Apply rate limiting
                await self._apply_rate_limiting()
                
                # Fetch rooms page
                rooms_data = await self._fetch_live_rooms_page(
                    session, topics, languages, min_participants, room_types, page_token
                )
                
                if not rooms_data or not rooms_data.get('rooms'):
                    break
                    
                for room in rooms_data['rooms']:
                    # Apply filters
                    if self._matches_room_filters(room, topics, languages, min_participants, room_types):
                        yield room
                        
                # Get pagination info
                pagination = rooms_data.get('pagination', {})
                page_token = pagination.get('next')
                
                if not page_token:
                    break
                    
                page_count += 1
                
            except Exception as e:
                self.logger.error(f"Error fetching rooms page {page_count}: {str(e)}")
                break
                
    async def _fetch_live_rooms_page(
        self,
        session: aiohttp.ClientSession,
        topics: List[str],
        languages: List[str],
        min_participants: int,
        room_types: List[RoomType],
        page_token: Optional[str]
    ) -> Dict[str, Any]:
        """Fetch a single page of live rooms"""
        
        url = "https://www.clubhouseapi.com/api/get_channels"
        
        params = {
            'channel_types': 'active',
            'limit': 20
        }
        
        if page_token:
            params['page_token'] = page_token
            
        if topics:
            params['topics'] = ','.join(topics)
            
        if languages:
            params['languages'] = ','.join(languages)
            
        headers = await self._get_authenticated_headers()
        
        try:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 429:
                    # Rate limit hit, wait and retry
                    await asyncio.sleep(60)
                    return await self._fetch_live_rooms_page(
                        session, topics, languages, min_participants, room_types, page_token
                    )
                else:
                    self.logger.error(f"HTTP {response.status}: {await response.text()}")
                    return {}
                    
        except Exception as e:
            self.logger.error(f"Request error: {str(e)}")
            return {}
            
    def _matches_room_filters(
        self,
        room: Dict[str, Any],
        topics: List[str],
        languages: List[str], 
        min_participants: int,
        room_types: List[RoomType]
    ) -> bool:
        """Check if room matches the specified filters"""
        
        # Check participant count
        participant_count = room.get('num_all_speakers', 0) + room.get('num_other_speakers', 0)
        if participant_count < min_participants:
            return False
            
        # Check room type
        room_type_str = room.get('channel_type', 'open')
        try:
            room_type = RoomType(room_type_str)
            if room_type not in room_types:
                return False
        except ValueError:
            return False
            
        # Check topics if specified
        if topics:
            room_topic = room.get('topic', '').lower()
            if not any(topic.lower() in room_topic for topic in topics):
                return False
                
        # Check language if specified
        if languages:
            room_language = room.get('language', 'en')
            if room_language not in languages:
                return False
                
        return True
        
    async def _process_clubhouse_room(self, raw_room: Dict[str, Any]) -> Optional[ClubhouseRoom]:
        """Process and analyze Clubhouse room with comprehensive analytics"""



        
        try:
            room_id = raw_room.get('channel')
            if not room_id:
                return None
                
            # Extract basic room information
            title = raw_room.get('title', '')
            topic = raw_room.get('topic', '')
            description = raw_room.get('description', '')
            
            # Generate content fingerprint
            content_fingerprint = await self.content_guardian.generate_fingerprint(
                f"{room_id}{title}{topic}{description}"
            )
            
            # Extract creator information
            creator = raw_room.get('creator', {})
            creator_id = creator.get('user_id', '')
            creator_username = creator.get('username', '')
            
            # Extract club information if applicable
            club = raw_room.get('club')
            club_id = club.get('club_id') if club else None
            club_name = club.get('name') if club else None
            
            # Process participants
            participants_data = await self._process_participants(raw_room)
            current_participants = participants_data['all_participants']
            speakers = participants_data['speakers']
            moderators = participants_data['moderators']
            listeners = participants_data['listeners']
            
            # Extract timing information
            start_time = datetime.fromisoformat(
                raw_room.get('created_at', datetime.now().isoformat()).replace('Z', '+00:00')
            )
            
            # Calculate metrics
            participant_count = len(current_participants)
            peak_participant_count = raw_room.get('num_speakers_peak', participant_count)
            
            # Analyze conversation quality
            conversation_quality = await self._analyze_conversation_quality(raw_room, speakers)
            
            # Analyze audio quality
            audio_quality_score = await self._analyze_audio_quality(raw_room)
            
            # Calculate engagement score
            engagement_score = await self._calculate_engagement_score(raw_room, participants_data)
            
            # Calculate viral potential
            viral_potential = await self._calculate_viral_potential(raw_room, engagement_score)
            
            # Analyze educational and entertainment value
            educational_value = await self._analyze_educational_value(raw_room, speakers)
            entertainment_value = await self._analyze_entertainment_value(raw_room)
            
            # Analyze social impact
            social_impact_score = await self._analyze_social_impact(raw_room, participants_data)
            
            # Calculate monetization potential
            monetization_potential = await self._calculate_monetization_potential(raw_room, participants_data)
            
            # Detect language
            language_detected = await self._detect_primary_language(raw_room)
            
            # Generate transcription summary if enabled
            transcription_summary = ""
            key_discussion_points = []
            if self.enable_transcription:
                transcription_data = await self._generate_transcription_summary(raw_room)
                transcription_summary = transcription_data['summary']
                key_discussion_points = transcription_data['key_points']
                
            # Perform sentiment analysis
            sentiment_analysis = await self._analyze_room_sentiment(raw_room)
            
            # Analyze influence network
            influence_network_data = await self._analyze_influence_network(participants_data)
            
            # Determine room status and type
            room_status = self._determine_room_status(raw_room)
            room_type = self._determine_room_type(raw_room)
            
            # Determine protection level
            protection_level = "monitored" if conversation_quality in [ConversationQuality.EXCEPTIONAL, ConversationQuality.HIGH_QUALITY] else "standard"
            
            # Create Clubhouse room object
            clubhouse_room = ClubhouseRoom(
                room_id=room_id,
                title=title,
                description=description,
                topic=topic,
                subtopics=raw_room.get('subtopics', []),
                status=room_status,
                room_type=room_type,
                creator_id=creator_id,
                creator_username=creator_username,
                club_id=club_id,
                club_name=club_name,
                start_time=start_time,
                end_time=None,  # Live rooms don't have end time yet
                duration=None,
                participant_count=participant_count,
                peak_participant_count=peak_participant_count,
                current_participants=current_participants,
                speakers=speakers,
                moderators=moderators,
                listeners=listeners,
                conversation_quality=conversation_quality,
                audio_quality_score=audio_quality_score,
                engagement_score=engagement_score,
                viral_potential=viral_potential,
                educational_value=educational_value,
                entertainment_value=entertainment_value,
                content_fingerprint=content_fingerprint,
                protection_level=protection_level,
                social_impact_score=social_impact_score,
                monetization_potential=monetization_potential,
                language_detected=language_detected,
                transcription_summary=transcription_summary,
                key_discussion_points=key_discussion_points,
                sentiment_analysis=sentiment_analysis,
                influence_network_data=influence_network_data
            )
            
            # Record metrics
            await self.metrics_collector.record_content_processed(
                platform='clubhouse',
                content_type='room',
                quality_score=engagement_score
            )
            
            return clubhouse_room
            
        except Exception as e:
            self.logger.error(f"Error processing Clubhouse room: {str(e)}")
            return None
            
    async def _process_participants(self, room_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and analyze room participants"""
        
        all_participants = []
        speakers = []
        moderators = []
        listeners = []
        
        # Process speakers
        speakers_data = room_data.get('speakers', [])
        for speaker_data in speakers_data:
            participant = await self._create_participant_object(speaker_data, ParticipantRole.SPEAKER)
            if participant:
                all_participants.append(participant)
                speakers.append(participant)
                
        # Process moderators
        moderators_data = room_data.get('moderators', [])
        for moderator_data in moderators_data:
            participant = await self._create_participant_object(moderator_data, ParticipantRole.MODERATOR)
            if participant:
                all_participants.append(participant)
                moderators.append(participant)
                
        # Process other participants (listeners)
        other_speakers = room_data.get('other_speakers', [])
        for listener_data in other_speakers:
            participant = await self._create_participant_object(listener_data, ParticipantRole.LISTENER)
            if participant:
                all_participants.append(participant)
                listeners.append(participant)
                
        return {
            'all_participants': all_participants,
            'speakers': speakers,
            'moderators': moderators,
            'listeners': listeners
        }
        
    async def _create_participant_object(
        self, 
        participant_data: Dict[str, Any], 
        role: ParticipantRole
    ) -> Optional[ClubhouseParticipant]:
        """Create participant object with analysis"""



        
        try:
            user_id = participant_data.get('user_id', '')
            if not user_id:
                return None
                
            # Extract basic information
            username = participant_data.get('username', '')
            display_name = participant_data.get('name', '')
            bio = participant_data.get('bio', '')
            profile_photo_url = participant_data.get('photo_url', '')
            is_verified = participant_data.get('is_verified', False)
            
            # Extract follower metrics
            follower_count = participant_data.get('num_followers', 0)
            following_count = participant_data.get('num_following', 0)
            
            # Extract club memberships
            club_memberships = [club.get('name', '') for club in participant_data.get('clubs', [])]
            
            # Calculate participant scores
            voice_quality_score = await self._analyze_participant_voice_quality(participant_data)
            expertise_score = await self._analyze_participant_expertise(participant_data)
            engagement_score = await self._analyze_participant_engagement(participant_data)
            
            # Extract interaction data
            interaction_count = participant_data.get('interaction_count', 0)
            speaking_time = participant_data.get('speaking_time')
            join_time_str = participant_data.get('joined_at')
            join_time = datetime.fromisoformat(join_time_str.replace('Z', '+00:00')) if join_time_str else None
            
            return ClubhouseParticipant(
                user_id=user_id,
                username=username,
                display_name=display_name,
                role=role,
                join_time=join_time,
                speaking_time=speaking_time,
                interaction_count=interaction_count,
                voice_quality_score=voice_quality_score,
                expertise_score=expertise_score,
                engagement_score=engagement_score,
                follower_count=follower_count,
                following_count=following_count,
                bio=bio,
                profile_photo_url=profile_photo_url,
                is_verified=is_verified,
                club_memberships=club_memberships
            )
            
        except Exception as e:
            self.logger.error(f"Error creating participant object: {str(e)}")
            return None
            
    async def _analyze_conversation_quality(
        self, 
        room_data: Dict[str, Any], 
        speakers: List[ClubhouseParticipant]
    ) -> ConversationQuality:
        """Analyze overall conversation quality"""
        
        quality_factors = []
        
        # 1. Speaker quality factor
        if speakers:
            avg_expertise = sum(s.expertise_score for s in speakers) / len(speakers)
            quality_factors.append(avg_expertise * 0.3)
            
        # 2. Engagement distribution factor
        engagement_distribution = self._analyze_engagement_distribution(speakers)
        quality_factors.append(engagement_distribution * 0.2)
        
        # 3. Topic relevance factor
        topic_relevance = await self._analyze_topic_relevance(room_data)
        quality_factors.append(topic_relevance * 0.2)
        
        # 4. Conversation flow factor
        conversation_flow = await self._analyze_conversation_flow(room_data)
        quality_factors.append(conversation_flow * 0.15)
        
        # 5. Audio quality factor
        audio_quality = await self._analyze_audio_quality(room_data)
        quality_factors.append(audio_quality * 0.15)
        
        # Calculate overall quality score
        quality_score = sum(quality_factors)
        
        # Map to quality level
        if quality_score >= 0.9:
            return ConversationQuality.EXCEPTIONAL
        elif quality_score >= 0.8:
            return ConversationQuality.HIGH_QUALITY
        elif quality_score >= 0.7:
            return ConversationQuality.GOOD
        elif quality_score >= 0.5:
            return ConversationQuality.AVERAGE
        elif quality_score >= 0.3:
            return ConversationQuality.POOR
        else:
            return ConversationQuality.SPAM
            
    async def _analyze_participant_voice_quality(self, participant_data: Dict[str, Any]) -> float:
        """Analyze participant's voice quality"""
        
        if not self.enable_voice_analysis:
            return 0.8  # Default score
            
        # Voice quality metrics
        voice_metrics = participant_data.get('voice_metrics', {})
        
        # Factors: clarity, volume consistency, background noise
        clarity_score = voice_metrics.get('clarity_score', 0.8)
        volume_consistency = voice_metrics.get('volume_consistency', 0.8)
        noise_level = voice_metrics.get('background_noise_level', 0.2)
        
        # Calculate overall voice quality
        voice_quality = (
            clarity_score * 0.4 +
            volume_consistency * 0.3 +
            (1.0 - noise_level) * 0.3
        )
        
        return min(voice_quality, 1.0)
        
    async def _analyze_participant_expertise(self, participant_data: Dict[str, Any]) -> float:
        """Analyze participant's expertise level"""
        
        expertise_factors = []
        
        # 1. Bio analysis for expertise keywords
        bio = participant_data.get('bio', '')
        bio_expertise = self._extract_expertise_from_bio(bio)
        expertise_factors.append(bio_expertise * 0.3)
        
        # 2. Club memberships (relevant clubs indicate expertise)
        clubs = participant_data.get('clubs', [])
        club_expertise = self._analyze_club_expertise(clubs)
        expertise_factors.append(club_expertise * 0.2)
        
        # 3. Follower to following ratio (authority indicator)
        followers = participant_data.get('num_followers', 0)
        following = participant_data.get('num_following', 1)
        authority_ratio = min(followers / following, 10) / 10  # Cap at 10:1 ratio
        expertise_factors.append(authority_ratio * 0.2)
        
        # 4. Verification status
        is_verified = participant_data.get('is_verified', False)
        verification_score = 0.9 if is_verified else 0.5
        expertise_factors.append(verification_score * 0.1)
        
        # 5. Speaking patterns (if available)
        speaking_patterns = participant_data.get('speaking_patterns', {})
        pattern_score = speaking_patterns.get('expertise_indicators', 0.6)
        expertise_factors.append(pattern_score * 0.2)
        
        return sum(expertise_factors)
        
    def _extract_expertise_from_bio(self, bio: str) -> float:
        """Extract expertise indicators from bio text"""
        
        expertise_keywords = [
            'ceo', 'founder', 'director', 'expert', 'specialist', 'consultant',
            'advisor', 'professor', 'doctor', 'phd', 'author', 'speaker',
            'entrepreneur', 'investor', 'researcher', 'analyst', 'strategist'
        ]
        
        bio_lower = bio.lower()
        expertise_count = sum(1 for keyword in expertise_keywords if keyword in bio_lower)
        
        # Normalize score
        return min(expertise_count / 3, 1.0)  # Max score at 3 keywords
        
    def _analyze_club_expertise(self, clubs: List[Dict[str, Any]]) -> float:
        """Analyze expertise based on club memberships"""
        
        if not clubs:
            return 0.3
            
        # Professional club indicators
        professional_indicators = [
            'tech', 'business', 'startup', 'venture', 'capital', 'founder',
            'ceo', 'entrepreneur', 'investor', 'marketing', 'design',
            'engineering', 'science', 'research', 'academic', 'professional'
        ]
        
        professional_clubs = 0
        for club in clubs:
            club_name = club.get('name', '').lower()
            if any(indicator in club_name for indicator in professional_indicators):
                professional_clubs += 1
                
        # Score based on professional club ratio
        return min(professional_clubs / len(clubs), 1.0)
        
    async def _analyze_participant_engagement(self, participant_data: Dict[str, Any]) -> float:
        """Analyze participant's engagement level"""
        
        engagement_factors = []
        
        # 1. Interaction frequency
        interaction_count = participant_data.get('interaction_count', 0)
        interaction_score = min(interaction_count / 10, 1.0)  # Normalize to max 10 interactions
        engagement_factors.append(interaction_score * 0.4)
        
        # 2. Speaking time ratio
        speaking_time = participant_data.get('speaking_time', 0)
        room_duration = participant_data.get('room_duration', 3600)  # Default 1 hour
        speaking_ratio = min(speaking_time / room_duration, 0.5)  # Cap at 50% speaking time
        engagement_factors.append(speaking_ratio * 2 * 0.3)  # Scale to 0-1
        
        # 3. Response frequency
        response_count = participant_data.get('response_count', 0)
        response_score = min(response_count / 5, 1.0)  # Normalize to max 5 responses
        engagement_factors.append(response_score * 0.2)
        
        # 4. Question frequency
        question_count = participant_data.get('question_count', 0)
        question_score = min(question_count / 3, 1.0)  # Normalize to max 3 questions
        engagement_factors.append(question_score * 0.1)
        
        return sum(engagement_factors)
        
    def _analyze_engagement_distribution(self, speakers: List[ClubhouseParticipant]) -> float:
        """Analyze how engagement is distributed among speakers"""
        
        if len(speakers) < 2:
            return 0.5  # Neutral score for single speaker
            
        engagement_scores = [s.engagement_score for s in speakers]
        
        # Calculate engagement distribution metrics
        avg_engagement = sum(engagement_scores) / len(engagement_scores)
        
        # Penalize if engagement is too concentrated
        max_engagement = max(engagement_scores)
        concentration_ratio = max_engagement / avg_engagement if avg_engagement > 0 else 1
        
        # Good distribution: concentration ratio should be close to 1
        distribution_score = max(0, 1 - (concentration_ratio - 1) / 2)
        
        return distribution_score
        
    async def _analyze_topic_relevance(self, room_data: Dict[str, Any]) -> float:
        """Analyze how relevant the conversation is to the stated topic"""
        
        topic = room_data.get('topic', '')
        title = room_data.get('title', '')
        
        if not topic and not title:
            return 0.5  # Neutral score
            
        # This would use NLP analysis of conversation content
        # For now, return a baseline score
        return 0.7
        
    async def _analyze_conversation_flow(self, room_data: Dict[str, Any]) -> float:
        """Analyze the flow and structure of the conversation"""
        
        # Factors: turn-taking, interruptions, dead air, topic coherence
        flow_metrics = room_data.get('conversation_metrics', {})
        
        turn_taking_score = flow_metrics.get('turn_taking_score', 0.7)
        interruption_penalty = flow_metrics.get('interruption_ratio', 0.1)
        dead_air_penalty = flow_metrics.get('dead_air_ratio', 0.05)
        
        flow_score = (
            turn_taking_score * 0.5 -
            interruption_penalty * 0.3 -
            dead_air_penalty * 0.2
        )
        
        return max(flow_score, 0.0)
        
    async def _analyze_audio_quality(self, room_data: Dict[str, Any]) -> float:
        """Analyze overall audio quality of the room"""
        
        audio_metrics = room_data.get('audio_metrics', {})
        
        # Factors: bitrate, clarity, background noise, echo
        bitrate_score = audio_metrics.get('bitrate_score', 0.8)
        clarity_score = audio_metrics.get('clarity_score', 0.8)
        noise_level = audio_metrics.get('background_noise', 0.1)
        echo_level = audio_metrics.get('echo_level', 0.1)
        
        audio_quality = (
            bitrate_score * 0.3 +
            clarity_score * 0.4 +
            (1.0 - noise_level) * 0.2 +
            (1.0 - echo_level) * 0.1
        )
        
        return min(audio_quality, 1.0)
        
    async def _calculate_engagement_score(
        self, 
        room_data: Dict[str, Any], 
        participants_data: Dict[str, Any]
    ) -> float:
        """Calculate overall room engagement score"""
        
        engagement_factors = []
        
        # 1. Participant count factor
        participant_count = len(participants_data['all_participants'])
        participation_score = min(participant_count / 100, 1.0)  # Normalize to 100 participants
        engagement_factors.append(participation_score * 0.2)
        
        # 2. Speaker engagement factor
        speakers = participants_data['speakers']
        if speakers:
            avg_speaker_engagement = sum(s.engagement_score for s in speakers) / len(speakers)
            engagement_factors.append(avg_speaker_engagement * 0.3)
        else:
            engagement_factors.append(0)
            
        # 3. Interaction frequency factor
        total_interactions = sum(p.interaction_count for p in participants_data['all_participants'])
        interaction_score = min(total_interactions / (participant_count * 2), 1.0)  # 2 interactions per person target
        engagement_factors.append(interaction_score * 0.25)
        
        # 4. Room duration factor (longer engaged rooms score higher)
        room_age = room_data.get('room_age_minutes', 30)
        duration_score = min(room_age / 120, 1.0)  # Normalize to 2 hours
        engagement_factors.append(duration_score * 0.15)
        
        # 5. Growth rate factor
        growth_rate = room_data.get('participant_growth_rate', 0.1)
        growth_score = min(growth_rate, 1.0)
        engagement_factors.append(growth_score * 0.1)
        
        return sum(engagement_factors)
        
    async def _calculate_viral_potential(self, room_data: Dict[str, Any], engagement_score: float) -> float:
        """Calculate viral potential of the room"""
        
        viral_factors = []
        
        # 1. Current engagement level
        viral_factors.append(engagement_score * 0.3)
        
        # 2. Growth trajectory
        growth_rate = room_data.get('participant_growth_rate', 0.1)
        viral_factors.append(min(growth_rate * 2, 1.0) * 0.25)
        
        # 3. Speaker influence factor
        speakers = room_data.get('speakers', [])
        if speakers:
            avg_follower_count = sum(s.get('num_followers', 0) for s in speakers) / len(speakers)
            influence_score = min(avg_follower_count / 10000, 1.0)  # Normalize to 10k followers
            viral_factors.append(influence_score * 0.2)
        else:
            viral_factors.append(0)
            
        # 4. Topic trending factor
        topic = room_data.get('topic', '')
        trending_score = await self._analyze_topic_trending(topic)
        viral_factors.append(trending_score * 0.15)
        
        # 5. Time factor (prime time = higher viral potential)
        time_factor = self._analyze_time_factor(room_data)
        viral_factors.append(time_factor * 0.1)
        
        return sum(viral_factors)
        
    async def _analyze_educational_value(
        self, 
        room_data: Dict[str, Any], 
        speakers: List[ClubhouseParticipant]
    ) -> float:
        """Analyze educational value of the conversation"""
        
        educational_factors = []
        
        # 1. Speaker expertise level
        if speakers:
            avg_expertise = sum(s.expertise_score for s in speakers) / len(speakers)
            educational_factors.append(avg_expertise * 0.4)
        else:
            educational_factors.append(0)
            
        # 2. Topic educational value
        topic = room_data.get('topic', '')
        topic_educational_score = self._analyze_topic_educational_value(topic)
        educational_factors.append(topic_educational_score * 0.3)
        
        # 3. Q&A interaction level
        qa_metrics = room_data.get('qa_metrics', {})
        qa_score = qa_metrics.get('question_answer_ratio', 0.2)
        educational_factors.append(min(qa_score, 1.0) * 0.2)
        
        # 4. Content depth indicators
        depth_indicators = room_data.get('content_depth_score', 0.6)
        educational_factors.append(depth_indicators * 0.1)
        
        return sum(educational_factors)
        
    def _analyze_topic_educational_value(self, topic: str) -> float:
        """Analyze educational value based on topic"""
        
        educational_topics = [
            'tech', 'technology', 'science', 'education', 'learning', 'business',
            'entrepreneurship', 'finance', 'investing', 'career', 'skill', 'development',
            'health', 'wellness', 'psychology', 'philosophy', 'history', 'research'
        ]
        
        topic_lower = topic.lower()
        educational_indicators = sum(1 for keyword in educational_topics if keyword in topic_lower)
        
        return min(educational_indicators / 3, 1.0)
        
    async def _analyze_entertainment_value(self, room_data: Dict[str, Any]) -> float:
        """Analyze entertainment value of the conversation"""
        
        entertainment_factors = []
        
        # 1. Topic entertainment value
        topic = room_data.get('topic', '')
        topic_entertainment_score = self._analyze_topic_entertainment_value(topic)
        entertainment_factors.append(topic_entertainment_score * 0.3)
        
        # 2. Humor and engagement indicators
        humor_metrics = room_data.get('humor_metrics', {})
        humor_score = humor_metrics.get('humor_detection_score', 0.3)
        entertainment_factors.append(humor_score * 0.25)
        
        # 3. Storytelling elements
        storytelling_score = room_data.get('storytelling_score', 0.4)
        entertainment_factors.append(storytelling_score * 0.2)
        
        # 4. Audience engagement reactions
        reaction_metrics = room_data.get('reaction_metrics', {})
        reaction_score = reaction_metrics.get('positive_reaction_ratio', 0.5)
        entertainment_factors.append(reaction_score * 0.15)
        
        # 5. Energy level
        energy_level = room_data.get('energy_level', 0.6)
        entertainment_factors.append(energy_level * 0.1)
        
        return sum(entertainment_factors)
        
    def _analyze_topic_entertainment_value(self, topic: str) -> float:
        """Analyze entertainment value based on topic"""
        
        entertainment_topics = [
            'music', 'art', 'entertainment', 'comedy', 'humor', 'stories', 'culture',
            'movies', 'tv', 'celebrity', 'sports', 'gaming', 'lifestyle', 'travel',
            'food', 'fashion', 'relationships', 'dating', 'social'
        ]
        
        topic_lower = topic.lower()
        entertainment_indicators = sum(1 for keyword in entertainment_topics if keyword in topic_lower)
        
        return min(entertainment_indicators / 2, 1.0)
        
    async def _analyze_social_impact(
        self, 
        room_data: Dict[str, Any], 
        participants_data: Dict[str, Any]
    ) -> float:
        """Analyze social impact of the conversation"""
        
        # Factors: reach, influence, topic importance, engagement quality
        participant_count = len(participants_data['all_participants'])
        speakers = participants_data['speakers']
        
        # Calculate total potential reach
        total_followers = sum(s.follower_count for s in speakers) if speakers else 0
        reach_score = min(total_followers / 100000, 1.0)  # Normalize to 100k followers
        
        # Topic social importance
        topic = room_data.get('topic', '')
        topic_importance = self._analyze_topic_social_importance(topic)
        
        # Engagement quality
        engagement_score = await self._calculate_engagement_score(room_data, participants_data)
        
        # Calculate social impact
        social_impact = (
            reach_score * 0.4 +
            topic_importance * 0.3 +
            engagement_score * 0.3
        )
        
        return social_impact
        
    def _analyze_topic_social_importance(self, topic: str) -> float:
        """Analyze social importance of the topic"""
        
        important_topics = [
            'social', 'justice', 'equality', 'environment', 'climate', 'health',
            'pandemic', 'mental health', 'education', 'community', 'charity',
            'volunteer', 'activism', 'policy', 'government', 'democracy', 'rights'
        ]
        
        topic_lower = topic.lower()
        importance_indicators = sum(1 for keyword in important_topics if keyword in topic_lower)
        
        return min(importance_indicators / 2, 1.0)
        
    async def _calculate_monetization_potential(
        self, 
        room_data: Dict[str, Any], 
        participants_data: Dict[str, Any]
    ) -> float:
        """Calculate monetization potential of the room"""
        
        monetization_factors = []
        
        # 1. Audience size and engagement
        engagement_score = await self._calculate_engagement_score(room_data, participants_data)
        monetization_factors.append(engagement_score * 0.3)
        
        # 2. Speaker influence and authority
        speakers = participants_data['speakers']
        if speakers:
            avg_influence = sum(s.follower_count for s in speakers) / len(speakers)
            influence_score = min(avg_influence / 50000, 1.0)  # Normalize to 50k followers
            monetization_factors.append(influence_score * 0.25)
        else:
            monetization_factors.append(0)
            
        # 3. Topic commercial value
        topic = room_data.get('topic', '')
        commercial_value = self._analyze_topic_commercial_value(topic)
        monetization_factors.append(commercial_value * 0.2)
        
        # 4. Club/brand affiliation
        club = room_data.get('club')
        brand_score = 0.8 if club else 0.4
        monetization_factors.append(brand_score * 0.15)
        
        # 5. Premium content indicators
        premium_indicators = room_data.get('premium_content_score', 0.5)
        monetization_factors.append(premium_indicators * 0.1)
        
        return sum(monetization_factors)
        
    def _analyze_topic_commercial_value(self, topic: str) -> float:
        """Analyze commercial value of the topic"""
        
        commercial_topics = [
            'business', 'entrepreneurship', 'startup', 'investing', 'finance',
            'marketing', 'sales', 'brand', 'product', 'tech', 'innovation',
            'consulting', 'coaching', 'course', 'training', 'workshop'
        ]
        
        topic_lower = topic.lower()
        commercial_indicators = sum(1 for keyword in commercial_topics if keyword in topic_lower)
        
        return min(commercial_indicators / 3, 1.0)
        
    async def _detect_primary_language(self, room_data: Dict[str, Any]) -> str:
        """Detect primary language of the conversation"""
        
        # This would use language detection on transcribed content
        # For now, return default or configured language
        return room_data.get('language', 'en')
        
    async def _generate_transcription_summary(self, room_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate transcription summary and extract key points"""
        
        if not self.enable_transcription:
            return {'summary': '', 'key_points': []}
            
        # This would use the transcription service
        # For now, return placeholder data
        return {
            'summary': f"Discussion about {room_data.get('topic', 'various topics')}",
            'key_points': [
                'Key insight 1',
                'Key insight 2', 
                'Key insight 3'
            ]
        }
        
    async def _analyze_room_sentiment(self, room_data: Dict[str, Any]) -> Dict[str, float]:
        """Analyze sentiment of the room conversation"""
        
        # This would use sentiment analysis on transcribed content
        return {
            'positive': 0.6,
            'negative': 0.2,
            'neutral': 0.2,
            'overall_sentiment': 0.4  # Net positive
        }
        
    async def _analyze_influence_network(self, participants_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze influence network within the room"""
        
        speakers = participants_data['speakers']
        moderators = participants_data['moderators']
        
        # Calculate network metrics
        total_influence = sum(s.follower_count for s in speakers + moderators)
        avg_influence = total_influence / len(speakers + moderators) if speakers + moderators else 0
        
        # Identify key influencers
        key_influencers = [
            {
                'user_id': p.user_id,
                'username': p.username,
                'follower_count': p.follower_count,
                'influence_score': p.follower_count / max(avg_influence, 1)
            }
            for p in speakers + moderators
            if p.follower_count > avg_influence
        ]
        
        return {
            'total_network_reach': total_influence,
            'average_influence': avg_influence,
            'key_influencers': key_influencers[:5],  # Top 5
            'network_density': len(key_influencers) / len(speakers + moderators) if speakers + moderators else 0
        }
        
    def _determine_room_status(self, room_data: Dict[str, Any]) -> RoomStatus:
        """Determine room status from data"""
        
        is_private = room_data.get('is_private', False)
        if is_private:
            return RoomStatus.PRIVATE
            
        # Assume active rooms are live
        return RoomStatus.LIVE
        
    def _determine_room_type(self, room_data: Dict[str, Any]) -> RoomType:
        """Determine room type from data"""
        
        channel_type = room_data.get('channel_type', 'open')
        
        if channel_type == 'private':
            return RoomType.CLOSED
        elif channel_type == 'social':
            return RoomType.SOCIAL
        elif room_data.get('club'):
            return RoomType.PRIVATE_CLUB
        else:
            return RoomType.OPEN
            
    def _meets_quality_threshold(self, room: ClubhouseRoom) -> bool:
        """Check if room meets minimum quality threshold"""
        
        quality_score = (
            room.engagement_score * 0.4 +
            room.audio_quality_score * 0.3 +
            (1.0 if room.conversation_quality in [ConversationQuality.EXCEPTIONAL, ConversationQuality.HIGH_QUALITY] else 0.5) * 0.3
        )
        
        return quality_score >= self.min_conversation_quality
        
    async def _analyze_topic_trending(self, topic: str) -> float:
        """Analyze if topic is currently trending"""
        
        # This would check trending topics APIs
        # For now, return a baseline score
        return 0.5
        
    def _analyze_time_factor(self, room_data: Dict[str, Any]) -> float:
        """Analyze time factor for viral potential"""
        
        current_hour = datetime.now().hour
        
        # Prime time hours (7-10 PM) have higher viral potential
        if 19 <= current_hour <= 22:
            return 1.0
        elif 17 <= current_hour <= 19 or 22 <= current_hour <= 24:
            return 0.8
        elif 12 <= current_hour <= 17:
            return 0.6
        else:
            return 0.4
            
    async def crawl_user_rooms(
        self, 
        user_id: str,
        include_past_rooms: bool = False,
        limit: int = 50
    ) -> List[ClubhouseRoom]:
        """Crawl rooms hosted or participated by a specific user"""
        
        self.logger.info(f"Crawling rooms for user: {user_id}")
        
        user_rooms = []
        
        try:
            async with self._create_session() as session:
                rooms_data = await self._fetch_user_rooms(session, user_id, include_past_rooms, limit)
                
                for room_data in rooms_data:
                    room = await self._process_clubhouse_room(room_data)
                    if room:
                        user_rooms.append(room)
                        
        except Exception as e:
            self.logger.error(f"Error crawling user rooms: {str(e)}")
            
        return user_rooms
        
    async def _fetch_user_rooms(
        self,
        session: aiohttp.ClientSession,
        user_id: str,
        include_past_rooms: bool,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Fetch rooms for a specific user"""
        
        url = f"https://www.clubhouseapi.com/api/get_user_rooms"
        
        params = {
            'user_id': user_id,
            'limit': limit
        }
        
        if include_past_rooms:
            params['include_past'] = 'true'
            
        headers = await self._get_authenticated_headers()
        
        try:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('rooms', [])
                else:
                    self.logger.error(f"HTTP {response.status}: {await response.text()}")
                    return []
                    
        except Exception as e:
            self.logger.error(f"Error fetching user rooms: {str(e)}")
            return []
            
    async def monitor_conversation_trends(
        self, 
        monitoring_period: timedelta = timedelta(hours=24)
    ) -> Dict[str, Any]:
        """Monitor conversation trends across the platform"""
        
        self.logger.info("Monitoring Clubhouse conversation trends")
        
        try:
            # Collect sample rooms for analysis
            sample_rooms = []
            
            async for room in self.crawl_live_rooms(min_participants=5):
                sample_rooms.append(room)
                if len(sample_rooms) >= 100:  # Limit sample size
                    break
                    
            # Analyze trends
            trends_analysis = {
                'total_analyzed': len(sample_rooms),
                'quality_distribution': self._analyze_quality_distribution(sample_rooms),
                'topic_trends': self._analyze_topic_trends(sample_rooms),
                'engagement_patterns': self._analyze_engagement_patterns(sample_rooms),
                'influence_patterns': self._analyze_influence_patterns(sample_rooms),
                'monetization_opportunities': self._analyze_monetization_opportunities(sample_rooms)
            }
            
            # Record monitoring metrics
            await self.metrics_collector.record_conversation_trends('clubhouse', trends_analysis)
            
            return trends_analysis
            
        except Exception as e:
            self.logger.error(f"Error monitoring conversation trends: {str(e)}")
            return {}
            
    def _analyze_quality_distribution(self, rooms: List[ClubhouseRoom]) -> Dict[str, float]:
        """Analyze distribution of conversation quality levels"""
        
        if not rooms:
            return {}
            
        total = len(rooms)
        distribution = {}
        
        for quality in ConversationQuality:
            count = len([r for r in rooms if r.conversation_quality == quality])
            distribution[quality.value] = count / total
            
        return distribution
        
    def _analyze_topic_trends(self, rooms: List[ClubhouseRoom]) -> Dict[str, Any]:
        """Analyze trending topics"""
        
        topic_counts = {}
        for room in rooms:
            topic = room.topic.lower()
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
            
        # Sort by frequency
        trending_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'top_topics': trending_topics[:10],
            'total_unique_topics': len(topic_counts),
            'topic_diversity': len(topic_counts) / len(rooms) if rooms else 0
        }
        
    def _analyze_engagement_patterns(self, rooms: List[ClubhouseRoom]) -> Dict[str, Any]:
        """Analyze engagement patterns across rooms"""
        
        if not rooms:
            return {}
            
        engagement_scores = [r.engagement_score for r in rooms]
        participant_counts = [r.participant_count for r in rooms]
        
        return {
            'avg_engagement': sum(engagement_scores) / len(engagement_scores),
            'max_engagement': max(engagement_scores),
            'avg_participants': sum(participant_counts) / len(participant_counts),
            'max_participants': max(participant_counts),
            'high_engagement_ratio': len([s for s in engagement_scores if s > 0.8]) / len(engagement_scores)
        }
        
    def _analyze_influence_patterns(self, rooms: List[ClubhouseRoom]) -> Dict[str, Any]:
        """Analyze influence patterns across rooms"""
        
        total_reach = sum(r.influence_network_data.get('total_network_reach', 0) for r in rooms)
        avg_reach = total_reach / len(rooms) if rooms else 0
        
        # Count verified speakers
        verified_speakers = 0
        total_speakers = 0
        
        for room in rooms:
            for speaker in room.speakers:
                total_speakers += 1
                if speaker.is_verified:
                    verified_speakers += 1
                    
        verification_ratio = verified_speakers / total_speakers if total_speakers > 0 else 0
        
        return {
            'total_network_reach': total_reach,
            'average_reach_per_room': avg_reach,
            'verified_speaker_ratio': verification_ratio,
            'high_influence_rooms': len([r for r in rooms if r.social_impact_score > 0.7])
        }
        
    def _analyze_monetization_opportunities(self, rooms: List[ClubhouseRoom]) -> Dict[str, Any]:
        """Analyze monetization opportunities"""
        
        if not rooms:
            return {}
            
        monetization_scores = [r.monetization_potential for r in rooms]
        
        return {
            'avg_monetization_potential': sum(monetization_scores) / len(monetization_scores),
            'high_potential_ratio': len([s for s in monetization_scores if s > 0.7]) / len(monetization_scores),
            'commercial_topics_ratio': len([r for r in rooms if self._analyze_topic_commercial_value(r.topic) > 0.6]) / len(rooms)
        }
        
    async def _get_authenticated_headers(self) -> Dict[str, str]:
        """Get authenticated headers for API requests"""



        
        return {
            'User-Agent': 'Clubhouse/1.0',
            'Accept': 'application/json',
            'Authorization': f'Token {self.config.get("access_token", "")}',
            'CH-DeviceId': self.config.get('device_id', ''),
            'CH-AppVersion': '1.0.0'
        }
        
    async def _create_session(self) -> aiohttp.ClientSession:
        """Create configured HTTP session"""
        
        connector = aiohttp.TCPConnector(
            limit=self.max_concurrent_requests,
            limit_per_host=self.max_concurrent_requests
        )
        
        timeout = aiohttp.ClientTimeout(total=45)
        
        return aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        )
        
    async def _apply_rate_limiting(self):
        """Apply rate limiting to prevent API abuse"""
        
        await asyncio.sleep(60 / self.rate_limit_per_minute)

import asyncio
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import re
import hashlib
import json
from urllib.parse import urljoin, urlparse, parse_qs

import aiohttp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from ..core.base_engine import BaseCrawlerEngine
from ..core.exceptions import (
    CrawlerError, 
    RateLimitError, 
    AuthenticationError,
    ContentNotFoundError
)
from ..utils.rate_limiter import RateLimiter
from ..utils.cache_manager import CacheManager
from ..models.content_models import AudioContent, UserContent
from ...core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class ClubhouseRoom:
    """Clubhouse room data structure"""
    id: str
    title: str
    description: Optional[str]
    topic: str
    club_id: Optional[str]
    club_name: Optional[str]
    creator_id: str
    creator_username: str
    is_public: bool
    is_social: bool
    language: str
    num_speakers: int
    num_all: int
    speaker_ids: List[str]
    moderator_ids: List[str]
    feature_flags: List[str]
    started_at: datetime
    ended_at: Optional[datetime]
    is_live: bool
    url: str
    created_at: datetime


@dataclass
class ClubhouseUser:
    """Clubhouse user data structure"""
    id: str
    username: str
    name: str
    bio: Optional[str]
    profile_image_url: Optional[str]
    follower_count: int
    following_count: int
    is_verified: bool
    is_invited_speaker: bool
    is_moderator: bool
    twitter_username: Optional[str]
    instagram_username: Optional[str]
    clubs: List[str]
    topics_of_interest: List[str]
    invited_by_user_id: Optional[str]
    join_date: datetime
    url: str
    created_at: datetime


@dataclass
class ClubhouseClub:
    """Clubhouse club data structure"""
    id: str
    name: str
    description: Optional[str]
    photo_url: Optional[str]
    num_members: int
    num_followers: int
    is_follow_allowed: bool
    is_membership_private: bool
    is_community: bool
    rules: List[str]
    topics: List[str]
    member_ids: List[str]
    admin_ids: List[str]
    created_at: datetime
    url: str


@dataclass
class ClubhouseEvent:
    """Clubhouse scheduled event data structure"""
    id: str
    name: str
    description: Optional[str]
    club_id: Optional[str]
    club_name: Optional[str]
    creator_id: str
    time_start: datetime
    is_member_only: bool
    url: str
    created_at: datetime


class ClubhouseCrawlerEngine(BaseCrawlerEngine):
    """
    Professional Clubhouse crawler engine for audio social content analysis.
    
    Features:
    - Live room monitoring
    - Speaker and moderator analytics
    - Topic trend analysis
    - Club membership tracking
    - Event discovery
    - Audio content protection
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Clubhouse crawler engine"""
        super().__init__(platform="clubhouse", config=config)
        
        # Rate limiting (conservative due to API restrictions)
        self.rate_limiter = RateLimiter(
            requests_per_minute=15,
            requests_per_hour=900
        )
        
        # Cache configuration
        self.cache_manager = CacheManager(
            cache_ttl=timedelta(minutes=15),  # Short cache for live content
            max_cache_size=3000
        )
        
        # API configuration (unofficial/reverse-engineered)
        self.base_url = "https://www.clubhouse.com/api"
        self.web_url = "https://www.clubhouse.com"
        
        # Session management
        self.session: Optional[aiohttp.ClientSession] = None
        self.auth_token: Optional[str] = None
        self.device_id: str = hashlib.md5(b'device').hexdigest()
        
        # Selenium driver for web content
        self.driver: Optional[webdriver.Chrome] = None
        
        logger.info("Clubhouse crawler engine initialized")
    
    async def initialize(self) -> None:
        """Initialize the crawler engine"""



        try:
            await self._create_session()
            self._setup_selenium()
            logger.info("Clubhouse engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Clubhouse engine: {e}")
            raise CrawlerError(f"Initialization failed: {e}")
    
    async def _create_session(self) -> None:
        """Create HTTP session with proper headers"""
        headers = {
            'User-Agent': 'Clubhouse/1.0.0 (iPhone; iOS 15.0; Scale/3.00)',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'CH-Languages': 'en-US',
            'CH-Locale': 'en_US',
            'Accept-Language': 'en-US;q=1.0',
            'Accept-Encoding': 'gzip, deflate',
            'CH-AppBuild': '297',
            'CH-AppVersion': '1.0.0',
            'CH-DeviceId': self.device_id,
            'Authorization': f'Token {self.auth_token}' if self.auth_token else ''
        }
        
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            headers=headers,
            timeout=timeout,
            connector=aiohttp.TCPConnector(limit=50)
        )
    
    def _setup_selenium(self) -> None:
        """Setup Selenium WebDriver for web content"""



        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            
            self.driver = webdriver.Chrome(options=options)
            logger.info("Selenium WebDriver initialized for Clubhouse")
        except Exception as e:
            logger.warning(f"Failed to initialize Selenium: {e}")
    
    async def get_live_rooms(
        self,
        topic: Optional[str] = None,
        language: str = "en"
    ) -> List[ClubhouseRoom]:
        """
        Get currently live rooms
        
        Args:
            topic: Filter by topic
            language: Language filter
            
        Returns:
            List of live rooms
        """



        try:
            await self.rate_limiter.acquire()
            
            # Check cache
            cache_key = f"live_rooms:{topic}:{language}"
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                return cached_result
            
            # Use web scraping since API access is limited
            if not self.driver:
                raise CrawlerError("Selenium driver not available")
            
            self.driver.get(f"{self.web_url}/explore")
            
            rooms = []
            try:
                # Wait for rooms to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "room-card"))
                )
                
                room_elements = self.driver.find_elements(By.CLASS_NAME, "room-card")
                
                for room_element in room_elements:
                    room = self._parse_room_element(room_element)
                    if room and (not topic or topic.lower() in room.topic.lower()):
                        rooms.append(room)
                
                # Cache results
                await self.cache_manager.set(cache_key, rooms)
                
                logger.info(f"Found {len(rooms)} live rooms")
                return rooms
                
            except TimeoutException:
                logger.warning("No live rooms found")
                return []
                
        except Exception as e:
            logger.error(f"Error getting live rooms: {e}")
            raise CrawlerError(f"Live rooms retrieval failed: {e}")
    
    async def get_room_details(self, room_id: str) -> Optional[ClubhouseRoom]:
        """
        Get detailed information about a specific room
        
        Args:
            room_id: Clubhouse room ID
            
        Returns:
            Room details or None if not found
        """



        try:
            await self.rate_limiter.acquire()
            
            # Check cache
            cache_key = f"room_details:{room_id}"
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                return cached_result
            
            # Use Selenium for web scraping
            if not self.driver:
                raise CrawlerError("Selenium driver not available")
            
            room_url = f"{self.web_url}/room/{room_id}"
            self.driver.get(room_url)
            
            try:
                # Wait for room details to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "room-header"))
                )
                
                room = self._parse_room_page()
                
                # Cache result
                await self.cache_manager.set(cache_key, room)
                
                return room
                
            except TimeoutException:
                raise ContentNotFoundError(f"Room not found: {room_id}")
                
        except Exception as e:
            logger.error(f"Error getting room details: {e}")
            raise CrawlerError(f"Room details retrieval failed: {e}")
    
    async def get_user_profile(self, username: str) -> Optional[ClubhouseUser]:
        """
        Get user profile information
        
        Args:
            username: Clubhouse username
            
        Returns:
            User profile data or None if not found
        """



        try:
            await self.rate_limiter.acquire()
            
            # Check cache
            cache_key = f"user_profile:{username}"
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                return cached_result
            
            # Use Selenium for web scraping
            if not self.driver:
                raise CrawlerError("Selenium driver not available")
            
            profile_url = f"{self.web_url}/{username}"
            self.driver.get(profile_url)
            
            try:
                # Wait for profile to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "profile-header"))
                )
                
                user = self._parse_user_profile()
                
                # Cache result
                await self.cache_manager.set(cache_key, user)
                
                return user
                
            except TimeoutException:
                raise ContentNotFoundError(f"User profile not found: {username}")
                
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            raise CrawlerError(f"User profile retrieval failed: {e}")
    
    async def get_club_info(self, club_name: str) -> Optional[ClubhouseClub]:
        """
        Get club information
        
        Args:
            club_name: Club name or ID
            
        Returns:
            Club information or None if not found
        """



        try:
            await self.rate_limiter.acquire()
            
            # Check cache
            cache_key = f"club_info:{club_name}"
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                return cached_result
            
            # Use Selenium for web scraping
            if not self.driver:
                raise CrawlerError("Selenium driver not available")
            
            club_url = f"{self.web_url}/club/{club_name}"
            self.driver.get(club_url)
            
            try:
                # Wait for club page to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "club-header"))
                )
                
                club = self._parse_club_page()
                
                # Cache result
                await self.cache_manager.set(cache_key, club)
                
                return club
                
            except TimeoutException:
                raise ContentNotFoundError(f"Club not found: {club_name}")
                
        except Exception as e:
            logger.error(f"Error getting club info: {e}")
            raise CrawlerError(f"Club info retrieval failed: {e}")
    
    async def search_rooms(
        self,
        query: str,
        is_live_only: bool = True
    ) -> List[ClubhouseRoom]:
        """
        Search for rooms by query
        
        Args:
            query: Search query
            is_live_only: Only return live rooms
            
        Returns:
            List of matching rooms
        """



        try:
            await self.rate_limiter.acquire()
            
            # Check cache
            cache_key = f"search_rooms:{hashlib.md5(f'{query}:{is_live_only}'.encode()).hexdigest()}"
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                return cached_result
            
            # Use Selenium for search
            if not self.driver:
                raise CrawlerError("Selenium driver not available")
            
            search_url = f"{self.web_url}/search/{query}"
            self.driver.get(search_url)
            
            rooms = []
            try:
                # Wait for search results
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "search-results"))
                )
                
                room_elements = self.driver.find_elements(By.CLASS_NAME, "room-result")
                
                for room_element in room_elements:
                    room = self._parse_search_room_element(room_element)
                    if room and (not is_live_only or room.is_live):
                        rooms.append(room)
                
                # Cache results
                await self.cache_manager.set(cache_key, rooms)
                
                logger.info(f"Found {len(rooms)} rooms for query: {query}")
                return rooms
                
            except TimeoutException:
                logger.warning(f"No search results found for: {query}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching rooms: {e}")
            raise CrawlerError(f"Room search failed: {e}")
    
    async def monitor_trending_topics(self) -> List[Dict[str, Any]]:
        """
        Monitor trending topics and conversations
        
        Returns:
            List of trending topics with metadata
        """



        try:
            # Get live rooms to analyze trending topics
            live_rooms = await self.get_live_rooms()
            
            # Analyze topics
            topic_counts = {}
            topic_data = []
            
            for room in live_rooms:
                topic = room.topic.lower()
                if topic not in topic_counts:
                    topic_counts[topic] = {
                        'count': 0,
                        'total_participants': 0,
                        'rooms': []
                    }
                
                topic_counts[topic]['count'] += 1
                topic_counts[topic]['total_participants'] += room.num_all
                topic_counts[topic]['rooms'].append(room.id)
            
            # Sort by popularity
            for topic, data in sorted(
                topic_counts.items(),
                key=lambda x: x[1]['total_participants'],
                reverse=True
            ):
                topic_data.append({
                    'topic': topic,
                    'room_count': data['count'],
                    'total_participants': data['total_participants'],
                    'average_participants': data['total_participants'] / data['count'],
                    'room_ids': data['rooms'],
                    'timestamp': datetime.utcnow().isoformat()
                })
            
            logger.info(f"Identified {len(topic_data)} trending topics")
            return topic_data[:20]  # Top 20 trending topics
            
        except Exception as e:
            logger.error(f"Error monitoring trending topics: {e}")
            raise CrawlerError(f"Trending topics monitoring failed: {e}")
    
    def _parse_room_element(self, room_element) -> Optional[ClubhouseRoom]:
        """Parse room element from page"""



        try:
            # Extract room title
            title_elem = room_element.find_element(By.CLASS_NAME, "room-title")
            title = title_elem.text if title_elem else ""
            
            # Extract topic
            topic_elem = room_element.find_element(By.CLASS_NAME, "room-topic")
            topic = topic_elem.text if topic_elem else ""
            
            # Extract participant count
            participants_elem = room_element.find_element(By.CLASS_NAME, "participant-count")
            participants_text = participants_elem.text if participants_elem else "0"
            num_all = int(re.search(r'\d+', participants_text).group()) if re.search(r'\d+', participants_text) else 0
            
            # Extract speakers
            speakers_elem = room_element.find_element(By.CLASS_NAME, "speakers")
            speaker_elements = speakers_elem.find_elements(By.CLASS_NAME, "speaker") if speakers_elem else []
            speaker_ids = [elem.get_attribute("data-user-id") for elem in speaker_elements]
            
            # Extract room link
            link_elem = room_element.find_element(By.TAG_NAME, "a")
            room_url = link_elem.get_attribute("href") if link_elem else ""
            room_id = room_url.split("/")[-1] if room_url else hashlib.md5(title.encode()).hexdigest()
            
            return ClubhouseRoom(
                id=room_id,
                title=title,
                description=None,  # Not available in list view
                topic=topic,
                club_id=None,  # Extract if available
                club_name=None,  # Extract if available
                creator_id="",  # Extract if available
                creator_username="",  # Extract if available
                is_public=True,  # Default assumption
                is_social=False,  # Extract if available
                language="en",  # Default
                num_speakers=len(speaker_ids),
                num_all=num_all,
                speaker_ids=speaker_ids,
                moderator_ids=[],  # Extract if available
                feature_flags=[],  # Extract if available
                started_at=datetime.utcnow(),  # Approximate
                ended_at=None,
                is_live=True,  # Assumption for live rooms
                url=room_url,
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.warning(f"Error parsing room element: {e}")
            return None
    
    def _parse_room_page(self) -> ClubhouseRoom:
        """Parse room details from current page"""
        # Implementation for parsing detailed room page
        # This would extract all available room metadata
        pass
    
    def _parse_user_profile(self) -> ClubhouseUser:
        """Parse user profile from current page"""
        # Implementation for parsing user profile page
        # This would extract all available user data
        pass
    
    def _parse_club_page(self) -> ClubhouseClub:
        """Parse club page from current page"""
        # Implementation for parsing club page
        # This would extract all available club data
        pass
    
    def _parse_search_room_element(self, room_element) -> Optional[ClubhouseRoom]:
        """Parse room element from search results"""
        # Similar to _parse_room_element but for search results
        return self._parse_room_element(room_element)
    
    async def track_speaker_analytics(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Track speaker analytics and engagement
        
        Args:
            user_id: User ID to track
            days: Number of days to analyze
            
        Returns:
            Speaker analytics data
        """



        try:
            analytics = {
                'user_id': user_id,
                'analysis_period_days': days,
                'rooms_participated': 0,
                'rooms_moderated': 0,
                'total_speaking_time': 0,
                'average_audience_size': 0,
                'topics_covered': [],
                'engagement_metrics': {
                    'followers_gained': 0,
                    'room_follows': 0
                },
                'analysis_date': datetime.utcnow().isoformat()
            }
            
            # This would require historical data access
            # Implementation would depend on available APIs
            
            logger.info(f"Speaker analytics completed for user: {user_id}")
            return analytics
            
        except Exception as e:
            logger.error(f"Error tracking speaker analytics: {e}")
            raise CrawlerError(f"Speaker analytics tracking failed: {e}")
    
    async def monitor_audio_content_protection(
        self,
        content_fingerprint: str,
        artist_name: str
    ) -> Dict[str, Any]:
        """
        Monitor for unauthorized use of audio content
        
        Args:
            content_fingerprint: Audio content fingerprint
            artist_name: Name of the content owner
            
        Returns:
            Content protection monitoring results
        """



        try:
            protection_results = {
                'content_fingerprint': content_fingerprint,
                'artist_name': artist_name,
                'potential_violations': [],
                'monitoring_timestamp': datetime.utcnow().isoformat()
            }
            
            # Search for rooms that might contain the content
            search_queries = [
                artist_name,
                f"{artist_name} music",
                f"{artist_name} songs"
            ]
            
            for query in search_queries:
                rooms = await self.search_rooms(query)
                
                for room in rooms:
                    if room.is_live:
                        protection_results['potential_violations'].append({
                            'room_id': room.id,
                            'room_title': room.title,
                            'room_topic': room.topic,
                            'num_participants': room.num_all,
                            'url': room.url,
                            'detection_confidence': 0.5  # Would need audio analysis
                        })
            
            logger.info(f"Content protection monitoring completed for {artist_name}")
            return protection_results
            
        except Exception as e:
            logger.error(f"Error in content protection monitoring: {e}")
            raise CrawlerError(f"Content protection monitoring failed: {e}")
    
    async def cleanup(self) -> None:
        """Clean up resources"""



        try:
            if self.session:
                await self.session.close()
            if self.driver:
                self.driver.quit()
            await super().cleanup()
            logger.info("Clubhouse engine cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def __str__(self) -> str:
        return f"ClubhouseCrawlerEngine(platform=clubhouse)"
