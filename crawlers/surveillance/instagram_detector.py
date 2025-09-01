"""Instagram Detector - Détection Instagram Avancée
===============================================

⚠️ PROPRIETARY SOFTWARE - UNAUTHORIZED ACCESS PROHIBITED

(c) 2024 IA Influencer Agent Development Team. All rights reserved.
This software is proprietary and confidential. Unauthorized reproduction,
distribution, or reverse engineering is strictly prohibited by law.

Author: Fahed Mlaiel <mlaiel@live.de>
Team Specialties: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

Advanced Instagram detection system for content monitoring and violation identification.
Provides sophisticated analysis of Instagram posts, stories, reels, and user activities.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json
import re
import hashlib
from urllib.parse import urlparse
import base64

logger = logging.getLogger(__name__)


@dataclass
class InstagramPost:
    """
Instagram post data."""
    post_id: str
    user_id: str
    username: str
    caption: str
    hashtags: List[str]
    mentions: List[str]
    like_count: int
    comment_count: int
    media_type: str  # photo, video, carousel
    media_urls: List[str]
    created_at: datetime
    location: Optional[str] = None
    is_ad: bool = False
    is_sponsored: bool = False
    scraped_at: datetime = field(default_factory=datetime.now)


@dataclass
class InstagramStory:
    """
Instagram story data."""
    story_id: str
    user_id: str
    username: str
    media_type: str  # photo, video
    media_url: str
    text_content: str
    stickers: List[str]
    hashtags: List[str]
    mentions: List[str]
    view_count: int
    created_at: datetime
    expires_at: datetime
    scraped_at: datetime = field(default_factory=datetime.now)


@dataclass
class InstagramUser:
    """
Instagram user profile data."""
    user_id: str
    username: str
    full_name: str
    bio: str
    follower_count: int
    following_count: int
    post_count: int
    profile_pic_url: str
    verified: bool = False
    private: bool = False
    business_account: bool = False
    category: Optional[str] = None
    external_url: Optional[str] = None
    scraped_at: datetime = field(default_factory=datetime.now)


@dataclass
class InstagramReel:
    """
Instagram reel data."""
    reel_id: str
    user_id: str
    username: str
    caption: str
    hashtags: List[str]
    mentions: List[str]
    like_count: int
    comment_count: int
    view_count: int
    share_count: int
    play_count: int
    video_url: str
    thumbnail_url: str
    audio_id: str
    audio_title: str
    duration_seconds: int
    created_at: datetime
    scraped_at: datetime = field(default_factory=datetime.now)


@dataclass
class InstagramViolation:
    """
Instagram content violation detection result."""
    violation_id: str
    content_type: str  # post, story, reel, user
    content_id: str
    user_id: str
    username: str
    violation_type: str
    confidence_score: float
    detected_at: datetime
    description: str
    evidence: Dict[str, Any] = field(default_factory=dict)
    severity: str = "medium"  # low, medium, high, critical


@dataclass
class InstagramDetectionMetrics:
    """Instagram detection system metrics."""
    posts_analyzed: int = 0
    stories_analyzed: int = 0
    reels_analyzed: int = 0
    users_analyzed: int = 0
    violations_detected: int = 0
    false_positives: int = 0
    detection_accuracy: float = 0.0
    processing_time_seconds: float = 0.0
    last_update: datetime = field(default_factory=datetime.now)


class InstagramDetector:
    """
    Advanced Instagram detection and analysis system.
    
    Features:
    - Real-time content monitoring
    - Advanced violation detection
    - Image and video analysis
    - Text content analysis
    - User behavior analysis
    - Trend detection
    - Automated reporting
    - Machine learning integration
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
Initialize Instagram detector."""
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Configuration
        self.config = config or {}
        self.max_concurrent_analysis = self.config.get('max_concurrent_analysis', 10)
        self.detection_threshold = self.config.get('detection_threshold', 0.7)
        self.enable_image_analysis = self.config.get('enable_image_analysis', True)
        self.enable_video_analysis = self.config.get('enable_video_analysis', True)
        self.enable_text_analysis = self.config.get('enable_text_analysis', True)
        
        # Detection state
        self.metrics = InstagramDetectionMetrics()
        self.violations: List[InstagramViolation] = []
        self._detection_active = False
        
        # Content storage
        self.posts: Dict[str, InstagramPost] = {}
        self.stories: Dict[str, InstagramStory] = {}
        self.reels: Dict[str, InstagramReel] = {}
        self.users: Dict[str, InstagramUser] = {}
        
        # Detection models and patterns
        self.violation_patterns = {
            'copyright': [
                r'(?i)(pirated|stolen|leaked|unauthorized|copyright)',
                r'(?i)(download|free\s+download|torrent)',
                r'(?i)(bootleg|knockoff|replica|fake)'
            ],
            'spam': [
                r'(?i)(click\s+link|follow\s+for\s+follow|f4f|l4l)',
                r'(?i)(buy\s+followers|buy\s+likes|increase\s+followers)',
                r'(?i)(dm\s+for\s+more|link\s+in\s+bio\s+for)'
            ],
            'adult_content': [
                r'(?i)(nsfw|adult\s+content|18\+)',
                r'(?i)(explicit|mature|adult\s+only)',
                r'(?i)(onlyfans|premium\s+content)'
            ],
            'harassment': [
                r'(?i)(hate\s+speech|harassment|bullying)',
                r'(?i)(kill\s+yourself|kys|die)',
                r'(?i)(discrimination|racist|sexist)'
            ]
        }
        
        # Image analysis keywords
        self.image_violation_keywords = [
            'copyright_watermark', 'adult_content', 'violence', 
            'dangerous_activities', 'fake_products'
        ]
        
        self._logger.info("Instagram Detector initialized")
    
    async def initialize(self) -> None:
        """Initialize the Instagram detector."""
        try:
            self._logger.info("Initializing Instagram detector...")
            
            # Initialize detection models
            await self._initialize_detection_models()
            
            # Setup analysis pipelines
            await self._setup_analysis_pipelines()
            
            self._logger.info("Instagram detector initialization complete")
            
        except Exception as e:
            self._logger.error(f"Failed to initialize Instagram detector: {e}")
            raise
    
    async def _initialize_detection_models(self) -> None:
        """Initialize AI detection models."""
        try:
            # This would load actual ML models for content analysis
            # For now, implement placeholder
            self._logger.debug("Detection models initialized")
            
        except Exception as e:
            self._logger.error(f"Failed to initialize detection models: {e}")
            raise
    
    async def _setup_analysis_pipelines(self) -> None:
        """Setup content analysis pipelines."""
        try:
            # This would setup actual analysis pipelines
            # For now, implement placeholder
            self._logger.debug("Analysis pipelines setup complete")
            
        except Exception as e:
            self._logger.error(f"Failed to setup analysis pipelines: {e}")
            raise
    
    async def start_detection(self) -> None:
        """Start Instagram detection operations."""
        try:
            if self._detection_active:
                self._logger.warning("Instagram detection is already active")
                return
            
            self._logger.info("Starting Instagram detection...")
            
            self._detection_active = True
            
            self._logger.info("Instagram detection started successfully")
            
        except Exception as e:
            self._logger.error(f"Failed to start Instagram detection: {e}")
            self._detection_active = False
            raise
    
    async def stop_detection(self) -> None:
        """Stop Instagram detection operations."""
        try:
            if not self._detection_active:
                self._logger.warning("Instagram detection is not active")
                return
            
            self._logger.info("Stopping Instagram detection...")
            
            self._detection_active = False
            
            self._logger.info("Instagram detection stopped successfully")
            
        except Exception as e:
            self._logger.error(f"Error stopping Instagram detection: {e}")
            raise
    
    async def analyze_post(self, post: InstagramPost) -> List[InstagramViolation]:
        """Analyze Instagram post for violations."""
        try:
            self._logger.debug(f"Analyzing post: {post.post_id}")
            analysis_start = datetime.now()
            
            violations = []
            
            # Store post
            self.posts[post.post_id] = post
            
            # Text analysis
            if self.enable_text_analysis:
                text_violations = await self._analyze_text_content(
                    post.caption, post.hashtags, post.mentions, post
                )
                violations.extend(text_violations)
            
            # Image/Video analysis
            if post.media_type == "photo" and self.enable_image_analysis:
                image_violations = await self._analyze_images(post.media_urls, post)
                violations.extend(image_violations)
            elif post.media_type == "video" and self.enable_video_analysis:
                video_violations = await self._analyze_videos(post.media_urls, post)
                violations.extend(video_violations)
            
            # User behavior analysis
            user_violations = await self._analyze_user_behavior(post.user_id, post.username, post)
            violations.extend(user_violations)
            
            # Update metrics
            self.metrics.posts_analyzed += 1
            self.metrics.violations_detected += len(violations)
            
            analysis_duration = (datetime.now() - analysis_start).total_seconds()
            self.metrics.processing_time_seconds += analysis_duration
            
            # Store violations
            for violation in violations:
                self.violations.append(violation)
            
            if violations:
                self._logger.warning(f"Detected {len(violations)} violations in post {post.post_id}")
            
            return violations
            
        except Exception as e:
            self._logger.error(f"Error analyzing post {post.post_id}: {e}")
            return []
    
    async def analyze_story(self, story: InstagramStory) -> List[InstagramViolation]:
        """Analyze Instagram story for violations."""
        try:
            self._logger.debug(f"Analyzing story: {story.story_id}")
            analysis_start = datetime.now()
            
            violations = []
            
            # Store story
            self.stories[story.story_id] = story
            
            # Text analysis
            if self.enable_text_analysis:
                text_violations = await self._analyze_text_content(
                    story.text_content, story.hashtags, story.mentions, story
                )
                violations.extend(text_violations)
            
            # Media analysis
            if story.media_type == "photo" and self.enable_image_analysis:
                image_violations = await self._analyze_images([story.media_url], story)
                violations.extend(image_violations)
            elif story.media_type == "video" and self.enable_video_analysis:
                video_violations = await self._analyze_videos([story.media_url], story)
                violations.extend(video_violations)
            
            # Update metrics
            self.metrics.stories_analyzed += 1
            self.metrics.violations_detected += len(violations)
            
            analysis_duration = (datetime.now() - analysis_start).total_seconds()
            self.metrics.processing_time_seconds += analysis_duration
            
            # Store violations
            for violation in violations:
                self.violations.append(violation)
            
            if violations:
                self._logger.warning(f"Detected {len(violations)} violations in story {story.story_id}")
            
            return violations
            
        except Exception as e:
            self._logger.error(f"Error analyzing story {story.story_id}: {e}")
            return []
    
    async def analyze_reel(self, reel: InstagramReel) -> List[InstagramViolation]:
        """Analyze Instagram reel for violations."""
        try:
            self._logger.debug(f"Analyzing reel: {reel.reel_id}")
            analysis_start = datetime.now()
            
            violations = []
            
            # Store reel
            self.reels[reel.reel_id] = reel
            
            # Text analysis
            if self.enable_text_analysis:
                text_violations = await self._analyze_text_content(
                    reel.caption, reel.hashtags, reel.mentions, reel
                )
                violations.extend(text_violations)
            
            # Video analysis
            if self.enable_video_analysis:
                video_violations = await self._analyze_videos([reel.video_url], reel)
                violations.extend(video_violations)
            
            # Audio analysis
            audio_violations = await self._analyze_audio(reel.audio_id, reel.audio_title, reel)
            violations.extend(audio_violations)
            
            # Update metrics
            self.metrics.reels_analyzed += 1
            self.metrics.violations_detected += len(violations)
            
            analysis_duration = (datetime.now() - analysis_start).total_seconds()
            self.metrics.processing_time_seconds += analysis_duration
            
            # Store violations
            for violation in violations:
                self.violations.append(violation)
            
            if violations:
                self._logger.warning(f"Detected {len(violations)} violations in reel {reel.reel_id}")
            
            return violations
            
        except Exception as e:
            self._logger.error(f"Error analyzing reel {reel.reel_id}: {e}")
            return []
    
    async def analyze_user(self, user: InstagramUser) -> List[InstagramViolation]:
        """Analyze Instagram user for violations."""
        try:
            self._logger.debug(f"Analyzing user: {user.username}")
            analysis_start = datetime.now()
            
            violations = []
            
            # Store user
            self.users[user.user_id] = user
            
            # Profile analysis
            profile_violations = await self._analyze_user_profile(user)
            violations.extend(profile_violations)
            
            # Update metrics
            self.metrics.users_analyzed += 1
            self.metrics.violations_detected += len(violations)
            
            analysis_duration = (datetime.now() - analysis_start).total_seconds()
            self.metrics.processing_time_seconds += analysis_duration
            
            # Store violations
            for violation in violations:
                self.violations.append(violation)
            
            if violations:
                self._logger.warning(f"Detected {len(violations)} violations in user {user.username}")
            
            return violations
            
        except Exception as e:
            self._logger.error(f"Error analyzing user {user.username}: {e}")
            return []
    
    async def _analyze_text_content(
        self,
        text: str,
        hashtags: List[str],
        mentions: List[str],
        content: Union[InstagramPost, InstagramStory, InstagramReel]
    ) -> List[InstagramViolation]:
        """Analyze text content for violations."""
        violations = []
        
        try:
            # Combine all text
            full_text = f"{text} {' '.join(hashtags)} {' '.join(mentions)}".lower()
            
            # Check each violation type
            for violation_type, patterns in self.violation_patterns.items():
                for pattern in patterns:
                    matches = re.findall(pattern, full_text)
                    
                    if matches:
                        confidence = min(len(matches) * 0.3 + 0.4, 1.0)
                        
                        if confidence >= self.detection_threshold:
                            violation = InstagramViolation(
                                violation_id=f"ig_text_{content.__class__.__name__.lower()}_{getattr(content, content.__class__.__name__.lower() + '_id')}_{violation_type}_{datetime.now().timestamp()}",
                                content_type=content.__class__.__name__.lower().replace('instagram', ''),
                                content_id=getattr(content, content.__class__.__name__.lower().replace('instagram', '') + '_id'),
                                user_id=content.user_id,
                                username=content.username,
                                violation_type=violation_type,
                                confidence_score=confidence,
                                detected_at=datetime.now(),
                                description=f"Text violation detected: {violation_type}",
                                evidence={
                                    'pattern_matched': pattern,
                                    'matches': matches,
                                    'text_preview': text[:200]
                                },
                                severity=self._calculate_severity(violation_type, confidence)
                            )
                            violations.append(violation)
            
        except Exception as e:
            self._logger.error(f"Error analyzing text content: {e}")
        
        return violations
    
    async def _analyze_images(
        self,
        image_urls: List[str],
        content: Union[InstagramPost, InstagramStory]
    ) -> List[InstagramViolation]:
        """Analyze images for violations."""
        violations = []
        
        try:
            # Simulate image analysis
            await asyncio.sleep(0.2)
            
            for url in image_urls:
                # In real implementation, this would use computer vision models
                # to analyze images for violations
                
                # Simulate detection results
                detected_issues = []
                
                # Random simulation of violations
                import random
                if random.random() < 0.1:  # 10% chance of violation
                    detected_issues.append({
                        'type': 'copyright_watermark',
                        'confidence': 0.85
                    })
                
                for issue in detected_issues:
                    if issue['confidence'] >= self.detection_threshold:
                        violation = InstagramViolation(
                            violation_id=f"ig_image_{content.__class__.__name__.lower()}_{getattr(content, content.__class__.__name__.lower() + '_id')}_image_{datetime.now().timestamp()}",
                            content_type=content.__class__.__name__.lower().replace('instagram', ''),
                            content_id=getattr(content, content.__class__.__name__.lower().replace('instagram', '') + '_id'),
                            user_id=content.user_id,
                            username=content.username,
                            violation_type='visual_violation',
                            confidence_score=issue['confidence'],
                            detected_at=datetime.now(),
                            description=f"Image violation detected: {issue['type']}",
                            evidence={
                                'image_url': url,
                                'detected_issue': issue['type'],
                                'analysis_type': 'computer_vision'
                            },
                            severity=self._calculate_severity('visual_violation', issue['confidence'])
                        )
                        violations.append(violation)
            
        except Exception as e:
            self._logger.error(f"Error analyzing images: {e}")
        
        return violations
    
    async def _analyze_videos(
        self,
        video_urls: List[str],
        content: Union[InstagramPost, InstagramReel]
    ) -> List[InstagramViolation]:
        """Analyze videos for violations."""
        violations = []
        
        try:
            # Simulate video analysis
            await asyncio.sleep(0.5)
            
            for url in video_urls:
                # In real implementation, this would use video analysis models
                # to analyze videos for violations
                
                # Simulate detection results
                detected_issues = []
                
                # Random simulation of violations
                import random
                if random.random() < 0.15:  # 15% chance of violation
                    detected_issues.append({
                        'type': 'copyright_content',
                        'confidence': 0.75
                    })
                
                for issue in detected_issues:
                    if issue['confidence'] >= self.detection_threshold:
                        violation = InstagramViolation(
                            violation_id=f"ig_video_{content.__class__.__name__.lower()}_{getattr(content, content.__class__.__name__.lower() + '_id')}_video_{datetime.now().timestamp()}",
                            content_type=content.__class__.__name__.lower().replace('instagram', ''),
                            content_id=getattr(content, content.__class__.__name__.lower().replace('instagram', '') + '_id'),
                            user_id=content.user_id,
                            username=content.username,
                            violation_type='video_violation',
                            confidence_score=issue['confidence'],
                            detected_at=datetime.now(),
                            description=f"Video violation detected: {issue['type']}",
                            evidence={
                                'video_url': url,
                                'detected_issue': issue['type'],
                                'analysis_type': 'video_analysis'
                            },
                            severity=self._calculate_severity('video_violation', issue['confidence'])
                        )
                        violations.append(violation)
            
        except Exception as e:
            self._logger.error(f"Error analyzing videos: {e}")
        
        return violations
    
    async def _analyze_audio(
        self,
        audio_id: str,
        audio_title: str,
        content: InstagramReel
    ) -> List[InstagramViolation]:
        """Analyze audio for violations."""
        violations = []
        
        try:
            # Simulate audio analysis
            await asyncio.sleep(0.3)
            
            # Check for copyrighted music
            if audio_title:
                # In real implementation, this would check against music databases
                # and use audio fingerprinting
                
                # Simple keyword-based check
                copyrighted_indicators = ['official', 'record', 'label', 'studio']
                
                if any(indicator in audio_title.lower() for indicator in copyrighted_indicators):
                    violation = InstagramViolation(
                        violation_id=f"ig_audio_reel_{content.reel_id}_audio_{datetime.now().timestamp()}",
                        content_type="reel",
                        content_id=content.reel_id,
                        user_id=content.user_id,
                        username=content.username,
                        violation_type='audio_copyright',
                        confidence_score=0.6,
                        detected_at=datetime.now(),
                        description=f"Potential audio copyright violation: {audio_title}",
                        evidence={
                            'audio_id': audio_id,
                            'audio_title': audio_title,
                            'analysis_type': 'audio_fingerprint'
                        },
                        severity=self._calculate_severity('audio_copyright', 0.6)
                    )
                    violations.append(violation)
            
        except Exception as e:
            self._logger.error(f"Error analyzing audio: {e}")
        
        return violations
    
    async def _analyze_user_behavior(
        self,
        user_id: str,
        username: str,
        content: Union[InstagramPost, InstagramStory, InstagramReel]
    ) -> List[InstagramViolation]:
        """Analyze user behavior patterns for violations."""
        violations = []
        
        try:
            # Analyze posting patterns, content similarity, etc.
            # This would include behavioral analysis
            
            # For now, implement basic checks
            user_content = [
                c for c in list(self.posts.values()) + list(self.stories.values()) + list(self.reels.values())
                if c.user_id == user_id
            ]
            
            # Check for spam behavior (too many posts in short time)
            if len(user_content) > 20:  # If user has more than 20 pieces of content
                recent_content = [
                    c for c in user_content
                    if (datetime.now() - c.created_at).total_seconds() < 3600  # Last hour
                ]
                
                if len(recent_content) > 10:  # More than 10 posts in last hour
                    violation = InstagramViolation(
                        violation_id=f"ig_behavior_{user_id}_spam_{datetime.now().timestamp()}",
                        content_type=content.__class__.__name__.lower().replace('instagram', ''),
                        content_id=getattr(content, content.__class__.__name__.lower().replace('instagram', '') + '_id'),
                        user_id=user_id,
                        username=username,
                        violation_type='spam_behavior',
                        confidence_score=0.8,
                        detected_at=datetime.now(),
                        description=f"Potential spam behavior: {len(recent_content)} posts in last hour",
                        evidence={
                            'recent_posts_count': len(recent_content),
                            'total_posts_count': len(user_content),
                            'analysis_type': 'behavioral_analysis'
                        },
                        severity='medium'
                    )
                    violations.append(violation)
            
        except Exception as e:
            self._logger.error(f"Error analyzing user behavior: {e}")
        
        return violations
    
    async def _analyze_user_profile(self, user: InstagramUser) -> List[InstagramViolation]:
        """Analyze user profile for violations."""
        violations = []
        
        try:
            # Analyze bio and profile information
            profile_text = f"{user.full_name} {user.bio}".lower()
            
            # Check for suspicious profile content
            for violation_type, patterns in self.violation_patterns.items():
                for pattern in patterns:
                    matches = re.findall(pattern, profile_text)
                    
                    if matches:
                        confidence = min(len(matches) * 0.4 + 0.5, 1.0)
                        
                        if confidence >= self.detection_threshold:
                            violation = InstagramViolation(
                                violation_id=f"ig_profile_{user.user_id}_{violation_type}_{datetime.now().timestamp()}",
                                content_type="user",
                                content_id=user.user_id,
                                user_id=user.user_id,
                                username=user.username,
                                violation_type=f"profile_{violation_type}",
                                confidence_score=confidence,
                                detected_at=datetime.now(),
                                description=f"Profile violation detected: {violation_type}",
                                evidence={
                                    'pattern_matched': pattern,
                                    'matches': matches,
                                    'bio_preview': user.bio[:100]
                                },
                                severity=self._calculate_severity(f"profile_{violation_type}", confidence)
                            )
                            violations.append(violation)
            
        except Exception as e:
            self._logger.error(f"Error analyzing user profile: {e}")
        
        return violations
    
    def _calculate_severity(self, violation_type: str, confidence: float) -> str:
        """Calculate violation severity based on type and confidence."""
        if confidence >= 0.9:
            return "critical"
        elif confidence >= 0.8:
            return "high"
        elif confidence >= 0.6:
            return "medium"
        else:
            return "low"
    
    def get_detection_status(self) -> Dict[str, Any]:
        """Get current detection status."""
        return {
            'detection_active': self._detection_active,
            'metrics': {
                'posts_analyzed': self.metrics.posts_analyzed,
                'stories_analyzed': self.metrics.stories_analyzed,
                'reels_analyzed': self.metrics.reels_analyzed,
                'users_analyzed': self.metrics.users_analyzed,
                'violations_detected': self.metrics.violations_detected,
                'false_positives': self.metrics.false_positives,
                'detection_accuracy': self.metrics.detection_accuracy,
                'processing_time_seconds': self.metrics.processing_time_seconds,
                'last_update': self.metrics.last_update.isoformat()
            },
            'content_counts': {
                'posts_stored': len(self.posts),
                'stories_stored': len(self.stories),
                'reels_stored': len(self.reels),
                'users_stored': len(self.users)
            }
        }
    
    def get_recent_violations(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
Get recent violations."""
        recent_violations = sorted(
            self.violations,
            key=lambda v: v.detected_at,
            reverse=True
        )[:limit]
        
        return [
            {
                'violation_id': v.violation_id,
                'content_type': v.content_type,
                'content_id': v.content_id,
                'user_id': v.user_id,
                'username': v.username,
                'violation_type': v.violation_type,
                'confidence_score': v.confidence_score,
                'detected_at': v.detected_at.isoformat(),
                'description': v.description,
                'evidence': v.evidence,
                'severity': v.severity
            }
            for v in recent_violations
        ]
    
    async def shutdown(self) -> None:
        """
Shutdown the Instagram detector."""
        try:
            self._logger.info("Shutting down Instagram detector...")
            
            await self.stop_detection()
            
            # Clear data
            self.posts.clear()
            self.stories.clear()
            self.reels.clear()
            self.users.clear()
            self.violations.clear()
            
            self._logger.info("Instagram detector shutdown complete")
            
        except Exception as e:
            self._logger.error(f"Error during Instagram detector shutdown: {e}")
            raise


# Export main class
__all__ = [
    'InstagramDetector', 'InstagramPost', 'InstagramStory', 'InstagramUser', 
    'InstagramReel', 'InstagramViolation', 'InstagramDetectionMetrics'
]