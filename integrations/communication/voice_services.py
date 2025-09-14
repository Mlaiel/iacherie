"""Voice Services Integration
==========================

Enterprise-grade voice services integration for audio content creation,
podcast monetization, and voice-based creator interactions.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import aiohttp
import base64
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urlencode
import uuid

# Configure logger
logger = logging.getLogger(__name__)

class VoiceSession:
    """Voice session management"""
    
    def __init__(self, session_id -> None: str, creator_id -> None: str, session_type -> None: str) -> None:
        self.session_id = session_id
        self.creator_id = creator_id
        self.session_type = session_type  # 'podcast', 'voice_chat', 'audio_call', 'voice_note'
        self.title = ""
        self.description = ""
        self.start_time = datetime.utcnow()
        self.end_time = None
        self.duration = 0
        self.participants = []
        self.recording_url = ""
        self.transcript = ""
        self.quality_score = 0.0

class VoiceParticipant:
    """Voice session participant"""
    
    def __init__(self, participant_id -> None: str, user_id -> None: str, display_name -> None: str) -> None:
        self.participant_id = participant_id
        self.user_id = user_id
        self.display_name = display_name
        self.joined_at = datetime.utcnow()
        self.left_at = None
        self.speaking_time = 0
        self.is_muted = False
        self.audio_quality = 0.0
        self.role = "participant"  # 'host', 'co-host', 'participant', 'guest'

class PodcastEpisode:
    """Podcast episode management"""
    
    def __init__(self, episode_id -> None: str, podcast_id -> None: str, title -> None: str) -> None:
        self.episode_id = episode_id
        self.podcast_id = podcast_id
        self.title = title
        self.description = ""
        self.audio_url = ""
        self.duration = 0
        self.file_size = 0
        self.published_at = datetime.utcnow()
        self.listens = 0
        self.downloads = 0
        self.revenue = 0.0
        self.sponsors = []

class VoiceAnalytics:
    """Voice analytics and insights"""
    
    def __init__(self, session_id -> None: str) -> None:
        self.session_id = session_id
        self.total_speaking_time = 0
        self.silence_percentage = 0.0
        self.interruption_count = 0
        self.speaker_balance = {}
        self.emotion_analysis = {}
        self.topic_analysis = {}
        self.engagement_score = 0.0

class VoiceServicesError(Exception):
    """Custom exception for voice services errors"""
    pass

class VoiceServices:
    """
    Comprehensive voice services integration for Ainflue platform.
    
    Features:
    - Podcast creation and distribution
    - Voice chat and audio calls
    - Voice note creation and sharing
    - Audio transcription and analysis
    - Voice AI enhancement
    - Monetization through audio ads
    - Cross-platform audio distribution
    - Voice analytics and insights
    """
    
    def __init__(self, services_config -> None: Dict[str, Dict[str, Any]]) -> None:
        self.services_config = services_config
        self.session = None
        self.active_sessions = {}
        self.rate_limits = {
            'requests_per_minute': 120,
            'requests_made': 0,
            'minute_start': datetime.utcnow().minute
        }
        
    async def __aenter__(self) -> None:
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    def _check_rate_limit(self) -> None:
        """Check and enforce rate limiting"""
        current_minute = datetime.utcnow().minute
        
        if current_minute != self.rate_limits['minute_start']:
            self.rate_limits['requests_made'] = 0
            self.rate_limits['minute_start'] = current_minute
            
        if self.rate_limits['requests_made'] >= self.rate_limits['requests_per_minute']:
            raise VoiceServicesError("Rate limit exceeded")
            
        self.rate_limits['requests_made'] += 1

    async def _make_service_request(self, service: str, method: str, endpoint: str, 
                                  data: Dict = None, params: Dict = None) -> Dict[str, Any]:
        """
        Make authenticated request to specific service API.
        
        Args:
            service: Service name (twilio, agora, spotify, anchor)
            method: HTTP method
            endpoint: API endpoint
            data: Request body data
            params: URL parameters
            
        Returns:
            API response data
        """
        self._check_rate_limit()
        
        service_config = self.services_config.get(service)
        if not service_config:
            raise VoiceServicesError(f"Service {service} not configured")
        
        base_url = service_config['base_url']
        headers = await self._get_service_headers(service)
        
        url = f"{base_url}{endpoint}"
        
        try:
            async with self.session.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                params=params
            ) as response:
                
                if response.status == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    await asyncio.sleep(retry_after)
                    return await self._make_service_request(service, method, endpoint, data, params)
                
                response_data = await response.json()
                
                if response.status >= 400:
                    raise VoiceServicesError(
                        f"{service} API request failed: {response.status} - {response_data}"
                    )
                    
                return response_data
                
        except aiohttp.ClientError as e:
            logger.error(f"Request error for {service}: {e}")
            raise VoiceServicesError(f"Request error: {e}")

    async def _get_service_headers(self, service: str) -> Dict[str, str]:
        """Get authentication headers for service"""
        service_config = self.services_config.get(service)
        
        if service == 'twilio':
            # Twilio Voice API
            auth = base64.b64encode(f"{service_config['account_sid']}:{service_config['auth_token']}".encode()).decode()
            return {
                'Authorization': f'Basic {auth}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        elif service == 'agora':
            # Agora Voice SDK
            return {
                'Authorization': f'Basic {service_config["app_certificate"]}',
                'Content-Type': 'application/json'
            }
        elif service == 'spotify':
            # Spotify Podcasts API
            token = await self._get_spotify_token()
            return {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
        elif service == 'anchor':
            # Anchor.fm API
            return {
                'Authorization': f'Bearer {service_config["api_token"]}',
                'Content-Type': 'application/json'
            }
        else:
            return {
                'Authorization': f'Bearer {service_config.get("api_token", "")}',
                'Content-Type': 'application/json'
            }

    # Voice Session Management
    async def create_voice_session(self, session_data: Dict[str, Any]) -> VoiceSession:
        """
        Create a new voice session.
        
        Args:
            session_data: Voice session configuration
            
        Returns:
            Created VoiceSession object
        """
        required_fields = ['creator_id', 'session_type', 'title']
        for field in required_fields:
            if field not in session_data:
                raise VoiceServicesError(f"Missing required field: {field}")
        
        session = VoiceSession(
            session_id=str(uuid.uuid4()),
            creator_id=session_data['creator_id'],
            session_type=session_data['session_type']
        )
        
        session.title = session_data['title']
        session.description = session_data.get('description', '')
        
        # Initialize session based on type
        if session.session_type == 'podcast':
            await self._initialize_podcast_session(session, session_data)
        elif session.session_type == 'voice_chat':
            await self._initialize_voice_chat_session(session, session_data)
        elif session.session_type == 'audio_call':
            await self._initialize_audio_call_session(session, session_data)
        elif session.session_type == 'voice_note':
            await self._initialize_voice_note_session(session, session_data)
        
        # Store active session
        self.active_sessions[session.session_id] = session
        
        logger.info(f"Created voice session: {session.session_id} ({session.session_type})")
        return session

    async def join_voice_session(self, session_id: str, participant_data: Dict[str, Any]) -> VoiceParticipant:
        """
        Join a participant to a voice session.
        
        Args:
            session_id: Voice session ID
            participant_data: Participant information
            
        Returns:
            VoiceParticipant object
        """
        session = await self.get_voice_session(session_id)
        
        participant = VoiceParticipant(
            participant_id=str(uuid.uuid4()),
            user_id=participant_data['user_id'],
            display_name=participant_data['display_name']
        )
        
        participant.role = participant_data.get('role', 'participant')
        
        # Add participant to session
        session.participants.append(participant)
        
        # Service-specific join logic
        await self._join_service_session(session, participant)
        
        logger.info(f"Participant {participant.user_id} joined voice session {session_id}")
        return participant

    async def get_voice_session(self, session_id: str) -> VoiceSession:
        """
        Get voice session details and current status.
        
        Args:
            session_id: Voice session ID
            
        Returns:
            VoiceSession object
        """
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
        else:
            session = await self._fetch_session_from_storage(session_id)
        
        # Update real-time information
        await self._update_session_status(session)
        
        return session

    # Podcast Management
    async def create_podcast_episode(self, episode_data: Dict[str, Any]) -> PodcastEpisode:
        """
        Create and publish a podcast episode.
        
        Args:
            episode_data: Episode configuration and content
            
        Returns:
            Created PodcastEpisode object
        """
        required_fields = ['podcast_id', 'title', 'audio_file']
        for field in required_fields:
            if field not in episode_data:
                raise VoiceServicesError(f"Missing required field: {field}")
        
        episode = PodcastEpisode(
            episode_id=str(uuid.uuid4()),
            podcast_id=episode_data['podcast_id'],
            title=episode_data['title']
        )
        
        episode.description = episode_data.get('description', '')
        
        # Upload and process audio file
        audio_result = await self._upload_and_process_audio(episode_data['audio_file'], episode_data)
        episode.audio_url = audio_result['audio_url']
        episode.duration = audio_result['duration']
        episode.file_size = audio_result['file_size']
        
        # Generate transcript if requested
        if episode_data.get('generate_transcript', True):
            transcript = await self._generate_transcript(episode.audio_url)
            episode.transcript = transcript
        
        # Enhance audio quality
        if episode_data.get('enhance_audio', True):
            enhanced_audio = await self._enhance_audio_quality(episode.audio_url)
            episode.audio_url = enhanced_audio['enhanced_url']
            episode.quality_score = enhanced_audio['quality_score']
        
        # Distribute to podcast platforms
        distribution_results = await self._distribute_podcast_episode(episode, episode_data.get('distribution_platforms', []))
        episode.distribution_results = distribution_results
        
        # Setup monetization
        if episode_data.get('enable_monetization', True):
            await self._setup_episode_monetization(episode, episode_data.get('monetization_config', {}))
        
        logger.info(f"Created podcast episode: {episode.episode_id}")
        return episode

    async def get_podcast_analytics(self, podcast_id: str, period: str = 'monthly') -> Dict[str, Any]:
        """
        Get comprehensive podcast analytics.
        
        Args:
            podcast_id: Podcast ID
            period: Analytics period
            
        Returns:
            Podcast analytics data
        """
        # Fetch episodes for the podcast
        episodes = await self._fetch_podcast_episodes(podcast_id)
        
        # Calculate basic metrics
        total_episodes = len(episodes)
        total_listens = sum(episode.listens for episode in episodes)
        total_downloads = sum(episode.downloads for episode in episodes)
        total_revenue = sum(episode.revenue for episode in episodes)
        
        # Get listener demographics
        demographics = await self._get_podcast_demographics(podcast_id)
        
        # Analyze episode performance
        episode_performance = await self._analyze_episode_performance(episodes)
        
        analytics = {
            'podcast_id': podcast_id,
            'period': period,
            'overview_metrics': {
                'total_episodes': total_episodes,
                'total_listens': total_listens,
                'total_downloads': total_downloads,
                'total_revenue': total_revenue,
                'average_listens_per_episode': total_listens / total_episodes if total_episodes > 0 else 0,
                'completion_rate': await self._calculate_completion_rate(episodes),
                'subscriber_growth': await self._calculate_subscriber_growth(podcast_id, period)
            },
            'audience_analytics': {
                'demographics': demographics,
                'listening_patterns': await self._analyze_listening_patterns(podcast_id),
                'engagement_metrics': await self._calculate_engagement_metrics(episodes),
                'retention_analysis': await self._analyze_audience_retention(podcast_id)
            },
            'content_performance': {
                'top_episodes': sorted(episodes, key=lambda x: x.listens, reverse=True)[:10],
                'content_themes': await self._analyze_content_themes(episodes),
                'optimal_episode_length': await self._analyze_optimal_length(episodes),
                'publishing_patterns': await self._analyze_publishing_patterns(episodes)
            },
            'monetization_metrics': {
                'revenue_breakdown': await self._analyze_revenue_breakdown(episodes),
                'sponsor_performance': await self._analyze_sponsor_performance(episodes),
                'premium_subscriptions': await self._get_premium_subscription_metrics(podcast_id),
                'merchandise_sales': await self._get_merchandise_metrics(podcast_id)
            },
            'growth_opportunities': {
                'content_recommendations': await self._generate_content_recommendations(analytics),
                'audience_expansion': await self._recommend_audience_expansion(analytics),
                'monetization_optimization': await self._suggest_monetization_optimization(analytics),
                'cross_platform_opportunities': await self._identify_cross_platform_opportunities(analytics)
            }
        }
        
        return analytics

    # Voice Enhancement and Processing
    async def enhance_voice_quality(self, audio_url: str, enhancement_options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Enhance voice quality using AI processing.
        
        Args:
            audio_url: URL of audio file to enhance
            enhancement_options: Enhancement configuration
            
        Returns:
            Enhancement result with enhanced audio URL
        """
        options = enhancement_options or {}
        
        # Apply noise reduction
        noise_reduced = await self._apply_noise_reduction(audio_url, options.get('noise_reduction', 0.8))
        
        # Normalize audio levels
        normalized = await self._normalize_audio_levels(noise_reduced['audio_url'])
        
        # Enhance voice clarity
        clarity_enhanced = await self._enhance_voice_clarity(normalized['audio_url'])
        
        # Apply EQ optimization
        eq_optimized = await self._apply_eq_optimization(clarity_enhanced['audio_url'])
        
        # Generate quality metrics
        quality_metrics = await self._analyze_audio_quality(eq_optimized['audio_url'])
        
        enhancement_result = {
            'original_audio_url': audio_url,
            'enhanced_audio_url': eq_optimized['audio_url'],
            'quality_improvement': quality_metrics['quality_score'] - quality_metrics['original_quality_score'],
            'processing_steps': [
                {'step': 'noise_reduction', 'improvement': noise_reduced['improvement']},
                {'step': 'normalization', 'improvement': normalized['improvement']},
                {'step': 'clarity_enhancement', 'improvement': clarity_enhanced['improvement']},
                {'step': 'eq_optimization', 'improvement': eq_optimized['improvement']}
            ],
            'final_quality_score': quality_metrics['quality_score'],
            'enhancement_metadata': {
                'processing_time': quality_metrics['processing_time'],
                'file_size_change': quality_metrics['file_size_change'],
                'format': quality_metrics['format']
            }
        }
        
        return enhancement_result

    async def generate_voice_transcript(self, audio_url: str, transcript_options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate transcript from voice audio.
        
        Args:
            audio_url: URL of audio file
            transcript_options: Transcription configuration
            
        Returns:
            Transcript data with timestamps and metadata
        """
        options = transcript_options or {}
        
        # Use multiple transcription services for accuracy
        transcription_services = options.get('services', ['whisper', 'google', 'azure'])
        
        transcripts = []
        for service in transcription_services:
            try:
                transcript = await self._transcribe_with_service(audio_url, service, options)
                transcripts.append(transcript)
            except Exception as e:
                logger.warning(f"Transcription failed with {service}: {e}")
        
        # Combine and improve transcripts
        combined_transcript = await self._combine_transcripts(transcripts)
        
        # Add speaker identification
        if options.get('speaker_identification', True):
            speaker_data = await self._identify_speakers(audio_url, combined_transcript)
            combined_transcript['speakers'] = speaker_data
        
        # Extract key insights
        insights = await self._extract_transcript_insights(combined_transcript['text'])
        
        transcript_result = {
            'transcript': combined_transcript['text'],
            'timestamped_segments': combined_transcript['segments'],
            'speakers': combined_transcript.get('speakers', []),
            'confidence_score': combined_transcript['confidence'],
            'language': combined_transcript['language'],
            'insights': {
                'key_topics': insights['topics'],
                'sentiment_analysis': insights['sentiment'],
                'action_items': insights['action_items'],
                'questions_asked': insights['questions'],
                'important_moments': insights['highlights']
            },
            'metadata': {
                'audio_duration': combined_transcript['duration'],
                'transcription_time': combined_transcript['processing_time'],
                'word_count': len(combined_transcript['text'].split()),
                'services_used': transcription_services
            }
        }
        
        return transcript_result

    # Voice Analytics and Insights
    async def analyze_voice_session(self, session_id: str) -> VoiceAnalytics:
        """
        Analyze voice session for insights and metrics.
        
        Args:
            session_id: Voice session ID
            
        Returns:
            VoiceAnalytics object
        """
        session = await self.get_voice_session(session_id)
        
        analytics = VoiceAnalytics(session_id)
        
        # Calculate speaking time metrics
        analytics.total_speaking_time = sum(p.speaking_time for p in session.participants)
        analytics.speaker_balance = {
            p.user_id: (p.speaking_time / analytics.total_speaking_time * 100) if analytics.total_speaking_time > 0 else 0
            for p in session.participants
        }
        
        # Analyze audio quality
        if session.recording_url:
            audio_analysis = await self._analyze_session_audio(session.recording_url)
            analytics.silence_percentage = audio_analysis['silence_percentage']
            analytics.interruption_count = audio_analysis['interruption_count']
            analytics.emotion_analysis = audio_analysis['emotion_analysis']
        
        # Extract topics from transcript
        if session.transcript:
            topic_analysis = await self._analyze_session_topics(session.transcript)
            analytics.topic_analysis = topic_analysis
        
        # Calculate engagement score
        analytics.engagement_score = await self._calculate_session_engagement_score(session, analytics)
        
        return analytics

    # Monetization Features
    async def setup_voice_monetization(self, content_id: str, content_type: str, monetization_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Setup monetization for voice content.
        
        Args:
            content_id: Content ID (episode, session, etc.)
            content_type: Type of content ('podcast', 'voice_note', etc.)
            monetization_config: Monetization configuration
            
        Returns:
            Monetization setup result
        """
        monetization_setup = {
            'content_id': content_id,
            'content_type': content_type,
            'enabled_features': [],
            'revenue_streams': []
        }
        
        # Setup advertising
        if monetization_config.get('enable_ads', False):
            ads_config = await self._setup_voice_advertising(content_id, monetization_config.get('ads_config', {}))
            monetization_setup['enabled_features'].append('advertising')
            monetization_setup['revenue_streams'].append({
                'type': 'advertising',
                'estimated_revenue': ads_config['estimated_revenue'],
                'configuration': ads_config
            })
        
        # Setup premium subscriptions
        if monetization_config.get('enable_premium', False):
            premium_config = await self._setup_premium_subscriptions(content_id, monetization_config.get('premium_config', {}))
            monetization_setup['enabled_features'].append('premium_subscriptions')
            monetization_setup['revenue_streams'].append({
                'type': 'premium_subscriptions',
                'estimated_revenue': premium_config['estimated_revenue'],
                'configuration': premium_config
            })
        
        # Setup sponsorships
        if monetization_config.get('enable_sponsorships', False):
            sponsorship_config = await self._setup_sponsorships(content_id, monetization_config.get('sponsorship_config', {}))
            monetization_setup['enabled_features'].append('sponsorships')
            monetization_setup['revenue_streams'].append({
                'type': 'sponsorships',
                'estimated_revenue': sponsorship_config['estimated_revenue'],
                'configuration': sponsorship_config
            })
        
        # Setup merchandise integration
        if monetization_config.get('enable_merchandise', False):
            merch_config = await self._setup_merchandise_integration(content_id, monetization_config.get('merchandise_config', {}))
            monetization_setup['enabled_features'].append('merchandise')
            monetization_setup['revenue_streams'].append({
                'type': 'merchandise',
                'estimated_revenue': merch_config['estimated_revenue'],
                'configuration': merch_config
            })
        
        return monetization_setup

    # Helper Methods for Enhanced Functionality
    async def _get_spotify_token(self) -> str:
        """Get Spotify API token"""
        # This would implement Spotify OAuth token generation
        return self.services_config['spotify']['api_token']

    async def _initialize_podcast_session(self, session: VoiceSession, session_data: Dict[str, Any]) -> None:
        """Initialize podcast recording session"""
        # Setup high-quality recording
        session.recording_config = {
            'quality': 'high',
            'format': 'wav',
            'sample_rate': 48000,
            'bit_depth': 24,
            'channels': 'stereo'
        }
        
        # Setup automatic transcription
        session.auto_transcribe = session_data.get('auto_transcribe', True)
        
        # Setup chapter markers
        session.chapter_markers = session_data.get('enable_chapters', True)

    async def _upload_and_process_audio(self, audio_file: str, processing_options: Dict[str, Any]) -> Dict[str, Any]:
        """Upload and process audio file"""
        # This would implement audio upload and processing
        return {
            'audio_url': f"https://cdn.ainflue.com/audio/{uuid.uuid4()}.mp3",
            'duration': 1800,  # 30 minutes
            'file_size': 25600000,  # 25.6 MB
            'format': 'mp3',
            'quality_score': 8.5
        }

    async def _generate_transcript(self, audio_url: str) -> str:
        """Generate transcript from audio"""
        # This would implement transcription service integration
        return "This is a sample transcript generated from the audio content..."

    async def _enhance_audio_quality(self, audio_url: str) -> Dict[str, Any]:
        """Enhance audio quality using AI"""
        return {
            'enhanced_url': f"https://cdn.ainflue.com/audio/enhanced_{uuid.uuid4()}.mp3",
            'quality_score': 9.2,
            'improvements': ['noise_reduction', 'normalization', 'clarity_enhancement']
        }

    async def _distribute_podcast_episode(self, episode: PodcastEpisode, platforms: List[str]) -> Dict[str, Any]:
        """Distribute episode to podcast platforms"""
        distribution_results = {}
        
        for platform in platforms:
            try:
                result = await self._distribute_to_platform(episode, platform)
                distribution_results[platform] = {
                    'success': True,
                    'episode_url': result['episode_url'],
                    'platform_id': result['platform_id']
                }
            except Exception as e:
                distribution_results[platform] = {
                    'success': False,
                    'error': str(e)
                }
        
        return distribution_results

    # Additional helper methods for comprehensive functionality...

# Example usage and testing
async def main() -> None:
    """Example usage of Voice Services integration"""
    
    # Initialize the service
    services_config = {
        'twilio': {
            'base_url': 'https://api.twilio.com/2010-04-01',
            'account_sid': 'your_account_sid',
            'auth_token': 'your_auth_token'
        },
        'spotify': {
            'base_url': 'https://api.spotify.com/v1',
            'api_token': 'your_spotify_token'
        },
        'anchor': {
            'base_url': 'https://anchor.fm/api',
            'api_token': 'your_anchor_token'
        }
    }
    
    voice_service = VoiceServices(services_config)
    
    async with voice_service:
        try:
            # Create a podcast recording session
            session_data = {
                'creator_id': 'creator_123',
                'session_type': 'podcast',
                'title': 'Creator Insights Episode 5',
                'description': 'Discussion about AI in content creation',
                'auto_transcribe': True,
                'enable_chapters': True
            }
            
            session = await voice_service.create_voice_session(session_data)
            print(f"Created voice session: {session.title}")
            
            # Create a podcast episode
            episode_data = {
                'podcast_id': 'podcast_123',
                'title': 'AI and the Future of Content Creation',
                'description': 'Deep dive into how AI is transforming creator economy',
                'audio_file': 'path/to/audio/file.wav',
                'generate_transcript': True,
                'enhance_audio': True,
                'distribution_platforms': ['spotify', 'apple_podcasts', 'google_podcasts'],
                'enable_monetization': True
            }
            
            # episode = await voice_service.create_podcast_episode(episode_data)
            # print(f"Created podcast episode: {episode.title}")
            
            # Enhance voice quality
            enhancement_result = await voice_service.enhance_voice_quality(
                'https://example.com/audio.mp3',
                {'noise_reduction': 0.9, 'enhance_clarity': True}
            )
            print(f"Audio quality improved by {enhancement_result['quality_improvement']:.1f} points")
            
            logger.info("Voice Services integration example completed successfully")
            
        except VoiceServicesError as e:
            logger.error(f"Voice Services error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run example
    asyncio.run(main())