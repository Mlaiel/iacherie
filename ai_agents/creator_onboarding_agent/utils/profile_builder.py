"""Profile Builder - Intelligent Creator Profile Construction

Advanced AI-powered system for building comprehensive creator profiles
with multi-format analysis, preference detection, and optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import uuid

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import spacy

try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
try:
    from core.exceptions import ProfileBuildingError, ValidationError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    ProfileBuildingError, ValidationError = globals().get('ProfileBuildingError, ValidationError', Exception)
from ...ml.profile_models import ProfileAnalyzer, InterestExtractor
from ...utils.text_processor import TextProcessor
from ...utils.social_media_analyzer import SocialMediaAnalyzer
from ...security.data_validator import DataValidator

logger = logging.getLogger(__name__)

class ProfileCompleteness(Enum):
    """
Profile completeness levels"""

    BASIC = "basic"          # 0-30%
    INTERMEDIATE = "intermediate"  # 31-60%
    ADVANCED = "advanced"    # 61-85%
    COMPLETE = "complete"    # 86-100%

class ContentGenre(Enum):
    """Supported content genres"""

    MUSIC_ELECTRONIC = "music_electronic"
    MUSIC_ACOUSTIC = "music_acoustic"
    MUSIC_HIP_HOP = "music_hip_hop"
    MUSIC_POP = "music_pop"
    MUSIC_ROCK = "music_rock"
    MUSIC_CLASSICAL = "music_classical"
    VIDEO_ENTERTAINMENT = "video_entertainment"
    VIDEO_EDUCATIONAL = "video_educational"
    VIDEO_LIFESTYLE = "video_lifestyle"
    PHOTO_PORTRAIT = "photo_portrait"
    PHOTO_LANDSCAPE = "photo_landscape"
    PHOTO_COMMERCIAL = "photo_commercial"
    TEXT_BLOG = "text_blog"
    TEXT_FICTION = "text_fiction"
    TEXT_JOURNALISM = "text_journalism"
    COMEDY_STANDUP = "comedy_standup"
    COMEDY_SKETCH = "comedy_sketch"
    PODCAST_NEWS = "podcast_news"
    PODCAST_INTERVIEW = "podcast_interview"
    PODCAST_NARRATIVE = "podcast_narrative"

@dataclass
class ProfileData:
    """Comprehensive creator profile data structure"""
    user_id: str
    creator_type: str
    
    # Basic Information
    display_name: str = ""
    bio: str = ""
    location: str = ""
    languages: List[str] = field(default_factory=list)
    timezone: str = ""
    
    # Content Preferences
    primary_genres: List[ContentGenre] = field(default_factory=list)
    content_formats: List[str] = field(default_factory=list)
    target_audience: Dict[str, Any] = field(default_factory=dict)
    posting_schedule: Dict[str, Any] = field(default_factory=dict)
    
    # Professional Information
    experience_level: str = ""  # beginner, intermediate, professional, expert
    career_goals: List[str] = field(default_factory=list)
    collaboration_interests: List[str] = field(default_factory=list)
    brand_guidelines: Dict[str, Any] = field(default_factory=dict)
    
    # Platform Presence
    social_media_handles: Dict[str, str] = field(default_factory=dict)
    website_url: str = ""
    portfolio_links: List[str] = field(default_factory=list)
    
    # AI-Generated Insights
    personality_traits: Dict[str, float] = field(default_factory=dict)
    content_themes: List[str] = field(default_factory=list)
    engagement_patterns: Dict[str, Any] = field(default_factory=dict)
    optimization_suggestions: List[str] = field(default_factory=list)
    
    # Metadata
    completeness_score: float = 0.0
    completeness_level: ProfileCompleteness = ProfileCompleteness.BASIC
    last_updated: datetime = field(default_factory=datetime.utcnow)
    verification_status: Dict[str, bool] = field(default_factory=dict)

class ProfileBuilder:
    """
    Advanced profile building system with AI-powered analysis and optimization.
    
    Core Capabilities:
    - Multi-source data integration and analysis
    - AI-powered personality and preference extraction
    - Intelligent content categorization and tagging
    - Social media presence analysis and optimization
    - Brand consistency validation and recommendations
    - Profile completeness scoring and improvement suggestions
    - Privacy-aware data handling and security
    """
    
    def __init__(self):
        self.profile_analyzer = ProfileAnalyzer()
        self.interest_extractor = InterestExtractor()
        self.text_processor = TextProcessor()
        self.social_analyzer = SocialMediaAnalyzer()
        self.data_validator = DataValidator()
        
        # Initialize NLP models
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy model not found, using basic text processing")
            self.nlp = None
        
        # TF-IDF for content analysis
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        logger.info("ProfileBuilder initialized successfully")
    
    async def initialize_profile(self, user_id: str, creator_type: str, 
                               initial_data: Dict[str, Any] = None) -> ProfileData:
        """
        Initialize new creator profile with intelligent defaults and analysis.
        """
        try:
            # Create base profile
            profile = ProfileData(
                user_id=user_id,
                creator_type=creator_type
            )
            
            # Process initial data if provided
            if initial_data:
                await self._process_initial_data(profile, initial_data)
            
            # Apply creator type defaults
            await self._apply_creator_defaults(profile)
            
            # Perform initial analysis
            await self._analyze_initial_profile(profile)
            
            # Calculate completeness
            await self._update_completeness_score(profile)
            
            logger.info(f"Initialized profile for user {user_id}, type: {creator_type}")
            return profile
            
        except Exception as e:
            logger.error(f"Error initializing profile: {str(e)}")
            raise ProfileBuildingError(f"Failed to initialize profile: {str(e)}")
    
    async def enrich_profile(self, profile: ProfileData, 
                           enrichment_data: Dict[str, Any]) -> ProfileData:
        """
        Enrich existing profile with additional data and AI analysis.
        """
        try:
            # Validate enrichment data
            validated_data = await self.data_validator.validate_profile_data(
                enrichment_data
            )
            
            # Update profile fields
            await self._update_profile_fields(profile, validated_data)
            
            # Perform content analysis if content provided
            if 'content_samples' in validated_data:
                await self._analyze_content_samples(profile, validated_data['content_samples'])
            
            # Analyze social media presence if provided
            if 'social_media_data' in validated_data:
                await self._analyze_social_presence(profile, validated_data['social_media_data'])
            
            # Extract personality insights
            await self._extract_personality_insights(profile)
            
            # Generate optimization suggestions
            await self._generate_optimization_suggestions(profile)
            
            # Update completeness
            await self._update_completeness_score(profile)
            
            profile.last_updated = datetime.utcnow()
            
            logger.info(f"Enriched profile for user {profile.user_id}")
            return profile
            
        except Exception as e:
            logger.error(f"Error enriching profile: {str(e)}")
            raise ProfileBuildingError(f"Failed to enrich profile: {str(e)}")
    
    async def analyze_brand_consistency(self, profile: ProfileData) -> Dict[str, Any]:
        """
        Analyze brand consistency across profile elements.
        """
        try:
            consistency_analysis = {
                'overall_score': 0.0,
                'visual_consistency': 0.0,
                'tone_consistency': 0.0,
                'messaging_consistency': 0.0,
                'issues': [],
                'recommendations': []
            }
            
            # Analyze visual consistency
            if profile.brand_guidelines:
                visual_score = await self._analyze_visual_consistency(profile)
                consistency_analysis['visual_consistency'] = visual_score
            
            # Analyze tone consistency
            if profile.content_themes:
                tone_score = await self._analyze_tone_consistency(profile)
                consistency_analysis['tone_consistency'] = tone_score
            
            # Analyze messaging consistency
            messaging_score = await self._analyze_messaging_consistency(profile)
            consistency_analysis['messaging_consistency'] = messaging_score
            
            # Calculate overall score
            scores = [
                consistency_analysis['visual_consistency'],
                consistency_analysis['tone_consistency'],
                consistency_analysis['messaging_consistency']
            ]
            consistency_analysis['overall_score'] = sum(s for s in scores if s > 0) / len([s for s in scores if s > 0])
            
            # Generate recommendations
            if consistency_analysis['overall_score'] < 0.7:
                consistency_analysis['recommendations'].extend([
                    "Develop consistent brand guidelines",
                    "Standardize visual elements across platforms",
                    "Create consistent messaging framework"
                ])
            
            return consistency_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing brand consistency: {str(e)}")
            return {'overall_score': 0.0, 'issues': ['Analysis failed']}
    
    async def suggest_improvements(self, profile: ProfileData) -> List[Dict[str, Any]]:
        """
        Generate intelligent profile improvement suggestions.
        """
        try:
            suggestions = []
            
            # Completeness-based suggestions
            if profile.completeness_score < 0.3:
                suggestions.append({
                    'category': 'basic_info',
                    'priority': 'high',
                    'title': 'Complete Basic Information',
                    'description': 'Add essential profile details like bio, location, and contact info',
                    'estimated_impact': 'High visibility improvement'
                })
            
            # Content-based suggestions
            if not profile.content_themes:
                suggestions.append({
                    'category': 'content_strategy',
                    'priority': 'high', 
                    'title': 'Define Content Themes',
                    'description': 'Identify and focus on specific content themes for better audience targeting',
                    'estimated_impact': 'Improved content consistency'
                })
            
            # Social media suggestions
            if len(profile.social_media_handles) < 3:
                suggestions.append({
                    'category': 'platform_presence',
                    'priority': 'medium',
                    'title': 'Expand Platform Presence',
                    'description': 'Connect additional social media platforms to increase reach',
                    'estimated_impact': 'Broader audience reach'
                })
            
            # Professional development suggestions
            if profile.experience_level == "beginner":
                suggestions.append({
                    'category': 'professional_growth',
                    'priority': 'medium',
                    'title': 'Enhance Professional Skills',
                    'description': 'Consider skill development courses or certification programs',
                    'estimated_impact': 'Career advancement opportunities'
                })
            
            # Collaboration suggestions
            if not profile.collaboration_interests:
                suggestions.append({
                    'category': 'networking',
                    'priority': 'low',
                    'title': 'Define Collaboration Interests',
                    'description': 'Specify types of collaborations you\'re interested in',
                    'estimated_impact': 'Better collaboration matching'
                })
            
            # AI-generated personalized suggestions
            ai_suggestions = await self._generate_ai_suggestions(profile)
            suggestions.extend(ai_suggestions)
            
            # Sort by priority
            priority_order = {'high': 3, 'medium': 2, 'low': 1}
            suggestions.sort(key=lambda x: priority_order.get(x['priority'], 0), reverse=True)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generating suggestions: {str(e)}")
            return []
    
    async def validate_profile(self, profile: ProfileData) -> Dict[str, Any]:
        """
        Comprehensive profile validation with detailed feedback.
        """
        try:
            validation_results = {
                'is_valid': True,
                'score': 0.0,
                'issues': [],
                'warnings': [],
                'recommendations': []
            }
            
            # Required field validation
            required_fields = ['display_name', 'bio', 'creator_type']
            missing_fields = [field for field in required_fields 
                            if not getattr(profile, field, '').strip()]
            
            if missing_fields:
                validation_results['is_valid'] = False
                validation_results['issues'].append(
                    f"Missing required fields: {', '.join(missing_fields)}"
                )
            
            # Content validation
            if profile.bio and len(profile.bio) < 50:
                validation_results['warnings'].append(
                    "Bio is too short - consider expanding to 50+ characters"
                )
            
            # Social media validation
            if len(profile.social_media_handles) == 0:
                validation_results['warnings'].append(
                    "No social media handles provided - this may limit discoverability"
                )
            
            # Genre validation
            if not profile.primary_genres:
                validation_results['warnings'].append(
                    "No content genres specified - this may affect content recommendations"
                )
            
            # Calculate validation score
            total_checks = len(required_fields) + 4  # Additional checks
            issues_count = len(validation_results['issues'])
            warnings_count = len(validation_results['warnings'])
            
            validation_results['score'] = max(0.0, 
                (total_checks - issues_count - (warnings_count * 0.5)) / total_checks
            )
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating profile: {str(e)}")
            return {
                'is_valid': False,
                'score': 0.0,
                'issues': ['Validation failed due to system error']
            }
    
    async def _process_initial_data(self, profile: ProfileData, 
                                  initial_data: Dict[str, Any]) -> None:
        """Process and integrate initial profile data."""
        # Map common fields
        field_mapping = {
            'name': 'display_name',
            'description': 'bio',
            'about': 'bio',
            'location': 'location',
            'website': 'website_url',
            'languages': 'languages'
        }
        
        for key, value in initial_data.items():
            if key in field_mapping:
                setattr(profile, field_mapping[key], value)
            elif hasattr(profile, key):
                setattr(profile, key, value)
        
        # Process nested data
        if 'social_media' in initial_data:
            profile.social_media_handles.update(initial_data['social_media'])
        
        if 'brand' in initial_data:
            profile.brand_guidelines.update(initial_data['brand'])
    
    async def _apply_creator_defaults(self, profile: ProfileData) -> None:
        """
Apply creator type-specific defaults and configurations."""
        creator_configs = {
            'musician': {
                'content_formats': ['audio', 'video', 'image'],
                'primary_genres': [ContentGenre.MUSIC_POP],
                'collaboration_interests': ['other_musicians', 'producers', 'labels']
            },
            'influencer': {
                'content_formats': ['video', 'image', 'text'],
                'collaboration_interests': ['brands', 'other_influencers', 'agencies']
            },
            'photographer': {
                'content_formats': ['image', 'video'],
                'primary_genres': [ContentGenre.PHOTO_PORTRAIT],
                'collaboration_interests': ['models', 'brands', 'agencies']
            },
            'video_creator': {
                'content_formats': ['video', 'image'],
                'collaboration_interests': ['brands', 'other_creators', 'sponsors']
            }
        }
        
        config = creator_configs.get(profile.creator_type, {})
        
        for key, default_value in config.items():
            if not getattr(profile, key):
                setattr(profile, key, default_value)
    
    async def _analyze_initial_profile(self, profile: ProfileData) -> None:
        """
Perform initial AI analysis of profile data."""
        if profile.bio:
            # Extract interests and themes from bio
            interests = await self.interest_extractor.extract_interests(profile.bio)
            profile.content_themes.extend(interests)
            
            # Analyze personality traits from bio text
            if self.nlp:
                personality = await self._analyze_personality_from_text(profile.bio)
                profile.personality_traits.update(personality)
    
    async def _analyze_content_samples(self, profile: ProfileData, 
                                     content_samples: List[Dict[str, Any]]) -> None:
        """
Analyze provided content samples for profile enrichment."""
        for sample in content_samples:
            content_type = sample.get('type', 'unknown')
            
            if content_type == 'text':
                # Extract themes and topics
                themes = await self._extract_content_themes(sample.get('content', ''))
                profile.content_themes.extend(themes)
            
            elif content_type == 'audio':
                # Analyze audio characteristics
                audio_analysis = await self._analyze_audio_sample(sample)
                if 'genre' in audio_analysis:
                    try:
                        genre = ContentGenre(f"music_{audio_analysis['genre'].lower()}")
                        if genre not in profile.primary_genres:
                            profile.primary_genres.append(genre)
                    except ValueError:
                        pass
            
            elif content_type == 'image':
                # Analyze image content and style
                image_analysis = await self._analyze_image_sample(sample)
                profile.content_themes.extend(image_analysis.get('themes', []))
    
    async def _analyze_social_presence(self, profile: ProfileData, 
                                     social_data: Dict[str, Any]) -> None:
        """Analyze social media presence and engagement patterns."""
        try:
            # Aggregate engagement metrics
            total_followers = 0
            total_engagement = 0
            
            for platform, data in social_data.items():
                if isinstance(data, dict):
                    followers = data.get('followers', 0)
                    engagement_rate = data.get('engagement_rate', 0)
                    
                    total_followers += followers
                    total_engagement += engagement_rate
                    
                    # Store platform-specific data
                    profile.social_media_handles[platform] = data.get('handle', '')
            
            # Calculate average engagement
            platform_count = len(social_data)
            if platform_count > 0:
                avg_engagement = total_engagement / platform_count
                profile.engagement_patterns['average_engagement_rate'] = avg_engagement
                profile.engagement_patterns['total_followers'] = total_followers
                profile.engagement_patterns['platform_count'] = platform_count
            
        except Exception as e:
            logger.error(f"Error analyzing social presence: {str(e)}")
    
    async def _extract_personality_insights(self, profile: ProfileData) -> None:
        """Extract personality insights from all available profile data."""
        text_sources = []
        
        # Collect text from various sources
        if profile.bio:
            text_sources.append(profile.bio)
        
        if profile.content_themes:
            text_sources.append(' '.join(profile.content_themes))
        
        # Combine and analyze
        combined_text = ' '.join(text_sources)
        if combined_text.strip():
            personality_analysis = await self._analyze_personality_from_text(combined_text)
            profile.personality_traits.update(personality_analysis)
    
    async def _generate_optimization_suggestions(self, profile: ProfileData) -> None:
        """
Generate AI-powered profile optimization suggestions."""
        suggestions = []
        
        # Content optimization
        if profile.completeness_score < 0.8:
            suggestions.append("Complete remaining profile sections for better visibility")
        
        # Engagement optimization
        if profile.engagement_patterns.get('average_engagement_rate', 0) < 0.05:
            suggestions.append("Focus on creating more engaging content to improve interaction rates")
        
        # Brand consistency
        if not profile.brand_guidelines:
            suggestions.append("Develop brand guidelines to maintain consistent visual identity")
        
        # Platform diversification
        if len(profile.social_media_handles) < 3:
            suggestions.append("Expand to additional platforms to increase reach and audience diversity")
        
        profile.optimization_suggestions = suggestions
    
    async def _update_completeness_score(self, profile: ProfileData) -> None:
        """Calculate and update profile completeness score."""
        completeness_factors = {
            'display_name': 5,
            'bio': 10,
            'location': 3,
            'languages': 3,
            'primary_genres': 8,
            'content_formats': 5,
            'target_audience': 7,
            'social_media_handles': 10,
            'website_url': 5,
            'portfolio_links': 7,
            'experience_level': 5,
            'career_goals': 6,
            'collaboration_interests': 8,
            'brand_guidelines': 12,
            'personality_traits': 6,
            'content_themes': 10
        }
        
        total_possible = sum(completeness_factors.values())
        achieved_score = 0
        
        for field, weight in completeness_factors.items():
            value = getattr(profile, field, None)
            
            if value:
                if isinstance(value, str) and value.strip():
                    achieved_score += weight
                elif isinstance(value, (list, dict)) and value:
                    achieved_score += weight
                elif isinstance(value, (int, float)) and value > 0:
                    achieved_score += weight
        
        profile.completeness_score = achieved_score / total_possible
        
        # Determine completeness level
        if profile.completeness_score < 0.3:
            profile.completeness_level = ProfileCompleteness.BASIC
        elif profile.completeness_score < 0.6:
            profile.completeness_level = ProfileCompleteness.INTERMEDIATE
        elif profile.completeness_score < 0.85:
            profile.completeness_level = ProfileCompleteness.ADVANCED
        else:
            profile.completeness_level = ProfileCompleteness.COMPLETE
    
    async def _analyze_personality_from_text(self, text: str) -> Dict[str, float]:
        """
Analyze personality traits from text using NLP."""
        try:
            # Simple keyword-based personality analysis
            personality_keywords = {
                'creativity': ['creative', 'artistic', 'innovative', 'original', 'unique'],
                'professionalism': ['professional', 'dedicated', 'committed', 'quality', 'excellence'],
                'collaboration': ['collaborate', 'team', 'together', 'community', 'partnership'],
                'passion': ['passionate', 'love', 'enthusiastic', 'excited', 'driven'],
                'authenticity': ['authentic', 'genuine', 'honest', 'real', 'transparent']
            }
            
            text_lower = text.lower()
            scores = {}
            
            for trait, keywords in personality_keywords.items():
                score = sum(1 for keyword in keywords if keyword in text_lower)
                # Normalize score (0-1)
                scores[trait] = min(score / len(keywords), 1.0)
            
            return scores
            
        except Exception as e:
            logger.error(f"Error analyzing personality: {str(e)}")
            return {}
    
    async def _extract_content_themes(self, content: str) -> List[str]:
        """Extract content themes and topics from text."""
        try:
            if not content.strip():
                return []
            
            # Use TF-IDF to extract important terms
            if hasattr(self, '_fitted_tfidf'):
                feature_names = self.tfidf_vectorizer.get_feature_names_out()
                tfidf_scores = self.tfidf_vectorizer.transform([content]).toarray()[0]
                
                # Get top themes
                top_indices = np.argsort(tfidf_scores)[-10:]  # Top 10
                themes = [feature_names[i] for i in top_indices if tfidf_scores[i] > 0]
                return themes
            else:
                # Simple keyword extraction
                keywords = ['music', 'art', 'technology', 'lifestyle', 'travel', 'food', 
                          'fashion', 'fitness', 'business', 'education', 'entertainment']
                
                content_lower = content.lower()
                found_themes = [kw for kw in keywords if kw in content_lower]
                return found_themes
                
        except Exception as e:
            logger.error(f"Error extracting themes: {str(e)}")
            return []
    
    async def _analyze_visual_consistency(self, profile: ProfileData) -> float:
        """Analyze visual brand consistency across profile elements."""
        # Placeholder implementation
        return 0.8 if profile.brand_guidelines else 0.3
    
    async def _analyze_tone_consistency(self, profile: ProfileData) -> float:
        """
Analyze tone consistency across content."""
        # Placeholder implementation
        return 0.7 if profile.content_themes else 0.4
    
    async def _analyze_messaging_consistency(self, profile: ProfileData) -> float:
        """
Analyze messaging consistency across platforms.""" 
        # Placeholder implementation
        return 0.6 if profile.bio and len(profile.social_media_handles) > 0 else 0.2
    
    async def _generate_ai_suggestions(self, profile: ProfileData) -> List[Dict[str, Any]]:
        """
Generate AI-powered personalized suggestions."""
        ai_suggestions = []
        
        # Content strategy suggestions based on creator type
        if profile.creator_type == 'musician' and not any('music' in theme for theme in profile.content_themes):
            ai_suggestions.append({
                'category': 'content_strategy',
                'priority': 'high',
                'title': 'Define Musical Style',
                'description': 'Clearly define your musical style and genre to attract the right audience',
                'estimated_impact': 'Better audience targeting'
            })
        
        # Engagement optimization
        engagement_rate = profile.engagement_patterns.get('average_engagement_rate', 0)
        if engagement_rate < 0.03:  # Less than 3%
            ai_suggestions.append({
                'category': 'engagement',
                'priority': 'medium',
                'title': 'Improve Engagement Strategy',
                'description': 'Focus on interactive content and community building to increase engagement',
                'estimated_impact': 'Higher audience interaction'
            })
        
        return ai_suggestions
    
    async def _analyze_audio_sample(self, sample: Dict[str, Any]) -> Dict[str, Any]:
        """
Analyze audio sample for genre and characteristics."""
        # Placeholder implementation - would use actual audio analysis
        return {'genre': 'pop', 'tempo': 'medium', 'energy': 'high'}
    
    async def _analyze_image_sample(self, sample: Dict[str, Any]) -> Dict[str, Any]:
        """
Analyze image sample for content and style."""
        # Placeholder implementation - would use actual image analysis
        return {'themes': ['portrait', 'professional'], 'style': 'modern'}
