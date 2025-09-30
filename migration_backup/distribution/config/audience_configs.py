"""
Audience Configuration
=====================

Advanced audience configuration and segmentation settings for Ainflue Distribution Platform.
Provides intelligent audience targeting and personalization configurations.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import os
import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class AudienceType(Enum):
    """Audience type categories"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    NICHE = "niche"
    LOOKALIKE = "lookalike"
    CUSTOM = "custom"

class DemographicAge(Enum):
    """Age group categories"""
    GEN_Z = "13-24"
    MILLENNIAL = "25-40"
    GEN_X = "41-56"
    BOOMER = "57-75"
    SENIOR = "75+"

class InterestCategory(Enum):
    """Interest categories for targeting"""
    TECHNOLOGY = "technology"
    ENTERTAINMENT = "entertainment"
    BUSINESS = "business"
    LIFESTYLE = "lifestyle"
    EDUCATION = "education"
    HEALTH_FITNESS = "health_fitness"
    TRAVEL = "travel"
    FOOD = "food"
    FASHION = "fashion"
    SPORTS = "sports"
    GAMING = "gaming"
    MUSIC = "music"
    ART = "art"
    SCIENCE = "science"
    POLITICS = "politics"

@dataclass
class DemographicConfig:
    """Demographic targeting configuration"""
    age_groups: List[str] = field(default_factory=list)
    genders: List[str] = field(default_factory=list)
    locations: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)
    income_levels: List[str] = field(default_factory=list)
    education_levels: List[str] = field(default_factory=list)
    relationship_status: List[str] = field(default_factory=list)
    employment_status: List[str] = field(default_factory=list)

@dataclass
class PsychographicConfig:
    """Psychographic targeting configuration"""
    interests: List[str] = field(default_factory=list)
    behaviors: List[str] = field(default_factory=list)
    values: List[str] = field(default_factory=list)
    lifestyle: List[str] = field(default_factory=list)
    personality_traits: List[str] = field(default_factory=list)
    buying_patterns: List[str] = field(default_factory=list)
    media_consumption: List[str] = field(default_factory=list)
    social_media_usage: List[str] = field(default_factory=list)

@dataclass
class BehavioralConfig:
    """Behavioral targeting configuration"""
    website_visitors: bool = False
    engagement_history: List[str] = field(default_factory=list)
    purchase_history: List[str] = field(default_factory=list)
    content_interactions: List[str] = field(default_factory=list)
    platform_activity: Dict[str, List[str]] = field(default_factory=dict)
    device_usage: List[str] = field(default_factory=list)
    time_patterns: List[str] = field(default_factory=list)
    frequency_patterns: List[str] = field(default_factory=list)

@dataclass
class CustomAudienceConfig:
    """Custom audience configuration"""
    name: str
    description: str = ""
    source_type: str = "manual"  # manual, upload, api, lookalike
    source_data: Dict[str, Any] = field(default_factory=dict)
    size_estimate: int = 0
    creation_date: Optional[str] = None
    last_updated: Optional[str] = None
    is_active: bool = True

@dataclass
class AudienceSegment:
    """Audience segment definition"""
    segment_id: str
    name: str
    description: str
    type: str = "primary"
    demographic: DemographicConfig = field(default_factory=DemographicConfig)
    psychographic: PsychographicConfig = field(default_factory=PsychographicConfig)
    behavioral: BehavioralConfig = field(default_factory=BehavioralConfig)
    custom_attributes: Dict[str, Any] = field(default_factory=dict)
    platform_specific: Dict[str, Dict] = field(default_factory=dict)
    priority: int = 1
    is_active: bool = True

@dataclass
class PersonalizationRule:
    """Content personalization rule"""
    rule_id: str
    name: str
    condition: Dict[str, Any]
    action: Dict[str, Any]
    priority: int = 1
    is_active: bool = True

@dataclass
class AudienceConfig:
    """Main audience configuration"""
    # Core Settings
    enable_audience_intelligence: bool = True
    enable_real_time_segmentation: bool = True
    enable_lookalike_discovery: bool = True
    enable_behavioral_tracking: bool = True
    enable_cross_platform_unification: bool = True
    
    # Audience Segments
    segments: Dict[str, AudienceSegment] = field(default_factory=dict)
    custom_audiences: Dict[str, CustomAudienceConfig] = field(default_factory=dict)
    
    # Targeting Configuration
    min_audience_size: int = 1000
    max_audience_size: int = 10000000
    overlap_threshold: float = 0.3
    similarity_threshold: float = 0.7
    refresh_interval_hours: int = 24
    
    # Platform-Specific Settings
    platform_settings: Dict[str, Dict] = field(default_factory=dict)
    
    # Personalization
    personalization_rules: List[PersonalizationRule] = field(default_factory=list)
    enable_dynamic_content: bool = True
    enable_a_b_testing: bool = True
    
    # Privacy and Compliance
    gdpr_compliant: bool = True
    ccpa_compliant: bool = True
    data_retention_days: int = 365
    anonymize_data: bool = True
    
    # Analytics
    track_engagement: bool = True
    track_conversions: bool = True
    track_attribution: bool = True
    
    def __post_init__(self):
        """Initialize default configurations"""
        if not self.platform_settings:
            self.platform_settings = self._get_default_platform_settings()
        
        if not self.segments:
            self.segments = self._get_default_segments()
    
    def _get_default_platform_settings(self) -> Dict[str, Dict]:
        """Get default platform-specific settings"""
        return {
            "facebook": {
                "enable_detailed_targeting": True,
                "enable_lookalike_audiences": True,
                "enable_custom_audiences": True,
                "min_audience_size": 1000,
                "interests_limit": 25,
                "behaviors_limit": 10,
                "demographic_overlap_tolerance": 0.2
            },
            "instagram": {
                "enable_detailed_targeting": True,
                "enable_lookalike_audiences": True,
                "enable_custom_audiences": True,
                "min_audience_size": 1000,
                "interests_limit": 25,
                "hashtag_targeting": True,
                "story_targeting": True
            },
            "twitter": {
                "enable_tailored_audiences": True,
                "enable_lookalike_audiences": True,
                "keyword_targeting": True,
                "interest_targeting": True,
                "follower_targeting": True,
                "conversation_targeting": True
            },
            "linkedin": {
                "enable_matched_audiences": True,
                "enable_lookalike_audiences": True,
                "company_targeting": True,
                "job_title_targeting": True,
                "skill_targeting": True,
                "industry_targeting": True
            },
            "tiktok": {
                "enable_custom_audiences": True,
                "enable_lookalike_audiences": True,
                "interest_targeting": True,
                "behavior_targeting": True,
                "hashtag_targeting": True,
                "video_interaction_targeting": True
            },
            "youtube": {
                "enable_custom_audiences": True,
                "enable_similar_audiences": True,
                "demographic_targeting": True,
                "interest_targeting": True,
                "placement_targeting": True,
                "keyword_targeting": True
            }
        }
    
    def _get_default_segments(self) -> Dict[str, AudienceSegment]:
        """Get default audience segments"""
        segments = {}
        
        # Primary audience - Business professionals
        segments["business_professionals"] = AudienceSegment(
            segment_id="business_professionals",
            name="Business Professionals",
            description="Working professionals interested in business and career growth",
            type="primary",
            demographic=DemographicConfig(
                age_groups=["25-40", "41-56"],
                education_levels=["bachelor", "master", "professional"],
                employment_status=["employed", "self_employed"],
                income_levels=["middle", "upper_middle", "high"]
            ),
            psychographic=PsychographicConfig(
                interests=["business", "technology", "education", "career_development"],
                behaviors=["professional_networking", "online_learning", "business_reading"],
                values=["achievement", "success", "growth", "innovation"]
            ),
            behavioral=BehavioralConfig(
                platform_activity={
                    "linkedin": ["profile_views", "post_engagement", "article_reading"],
                    "twitter": ["business_hashtags", "thought_leader_following"]
                },
                time_patterns=["weekday_morning", "lunch_break", "evening"]
            ),
            priority=1
        )
        
        # Secondary audience - Entrepreneurs
        segments["entrepreneurs"] = AudienceSegment(
            segment_id="entrepreneurs",
            name="Entrepreneurs & Startup Founders",
            description="Business owners and startup founders",
            type="secondary",
            demographic=DemographicConfig(
                age_groups=["25-40", "41-56"],
                employment_status=["self_employed", "business_owner"],
                income_levels=["variable", "high"]
            ),
            psychographic=PsychographicConfig(
                interests=["entrepreneurship", "startup", "innovation", "business"],
                behaviors=["risk_taking", "networking", "continuous_learning"],
                values=["independence", "innovation", "growth", "impact"]
            ),
            behavioral=BehavioralConfig(
                platform_activity={
                    "twitter": ["startup_hashtags", "entrepreneur_following"],
                    "linkedin": ["startup_content", "business_networking"]
                }
            ),
            priority=2
        )
        
        # Niche audience - Tech enthusiasts
        segments["tech_enthusiasts"] = AudienceSegment(
            segment_id="tech_enthusiasts",
            name="Technology Enthusiasts",
            description="People passionate about technology and innovation",
            type="niche",
            demographic=DemographicConfig(
                age_groups=["13-24", "25-40"],
                education_levels=["bachelor", "master", "technical"],
                employment_status=["employed", "student"]
            ),
            psychographic=PsychographicConfig(
                interests=["technology", "programming", "gadgets", "gaming"],
                behaviors=["early_adopter", "tech_forums", "product_reviews"],
                values=["innovation", "efficiency", "knowledge", "progress"]
            ),
            behavioral=BehavioralConfig(
                platform_activity={
                    "twitter": ["tech_hashtags", "developer_following"],
                    "reddit": ["tech_subreddits", "programming_communities"],
                    "youtube": ["tech_reviews", "programming_tutorials"]
                }
            ),
            priority=3
        )
        
        return segments
    
    def add_segment(self, segment: AudienceSegment) -> bool:
        """
        Add a new audience segment
        
        Args:
            segment: Audience segment to add
            
        Returns:
            bool: Success status
        """
        try:
            if not segment.segment_id or not segment.name:
                logger.error("Segment ID and name are required")
                return False
            
            self.segments[segment.segment_id] = segment
            logger.info(f"Added audience segment: {segment.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding segment: {str(e)}")
            return False
    
    def remove_segment(self, segment_id: str) -> bool:
        """
        Remove an audience segment
        
        Args:
            segment_id: ID of segment to remove
            
        Returns:
            bool: Success status
        """
        try:
            if segment_id in self.segments:
                del self.segments[segment_id]
                logger.info(f"Removed audience segment: {segment_id}")
                return True
            else:
                logger.warning(f"Segment not found: {segment_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error removing segment: {str(e)}")
            return False
    
    def get_segment(self, segment_id: str) -> Optional[AudienceSegment]:
        """
        Get audience segment by ID
        
        Args:
            segment_id: Segment ID
            
        Returns:
            Optional[AudienceSegment]: Segment if found
        """
        return self.segments.get(segment_id)
    
    def get_active_segments(self) -> List[AudienceSegment]:
        """
        Get all active audience segments
        
        Returns:
            List[AudienceSegment]: Active segments
        """
        return [segment for segment in self.segments.values() if segment.is_active]
    
    def add_personalization_rule(self, rule: PersonalizationRule) -> bool:
        """
        Add a personalization rule
        
        Args:
            rule: Personalization rule
            
        Returns:
            bool: Success status
        """
        try:
            if not rule.rule_id or not rule.name:
                logger.error("Rule ID and name are required")
                return False
            
            self.personalization_rules.append(rule)
            logger.info(f"Added personalization rule: {rule.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding personalization rule: {str(e)}")
            return False
    
    def get_platform_config(self, platform: str) -> Dict[str, Any]:
        """
        Get platform-specific configuration
        
        Args:
            platform: Platform name
            
        Returns:
            Dict[str, Any]: Platform configuration
        """
        return self.platform_settings.get(platform, {})
    
    def update_platform_config(self, platform: str, config: Dict[str, Any]) -> bool:
        """
        Update platform-specific configuration
        
        Args:
            platform: Platform name
            config: Configuration updates
            
        Returns:
            bool: Success status
        """
        try:
            if platform not in self.platform_settings:
                self.platform_settings[platform] = {}
            
            self.platform_settings[platform].update(config)
            logger.info(f"Updated platform config for: {platform}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating platform config: {str(e)}")
            return False
    
    def validate_config(self) -> List[str]:
        """
        Validate configuration settings
        
        Returns:
            List[str]: List of validation errors (empty if valid)
        """
        errors = []
        
        # Validate basic settings
        if self.min_audience_size < 100:
            errors.append("Minimum audience size should be at least 100")
        
        if self.max_audience_size < self.min_audience_size:
            errors.append("Maximum audience size must be greater than minimum")
        
        if not 0 <= self.overlap_threshold <= 1:
            errors.append("Overlap threshold must be between 0 and 1")
        
        if not 0 <= self.similarity_threshold <= 1:
            errors.append("Similarity threshold must be between 0 and 1")
        
        if self.refresh_interval_hours < 1:
            errors.append("Refresh interval must be at least 1 hour")
        
        if self.data_retention_days < 1:
            errors.append("Data retention must be at least 1 day")
        
        # Validate segments
        for segment_id, segment in self.segments.items():
            if not segment.name:
                errors.append(f"Segment {segment_id} must have a name")
            
            if segment.priority < 1:
                errors.append(f"Segment {segment_id} priority must be at least 1")
        
        # Validate personalization rules
        for rule in self.personalization_rules:
            if not rule.name:
                errors.append(f"Personalization rule {rule.rule_id} must have a name")
            
            if not rule.condition:
                errors.append(f"Personalization rule {rule.rule_id} must have a condition")
            
            if not rule.action:
                errors.append(f"Personalization rule {rule.rule_id} must have an action")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary
        
        Returns:
            Dict[str, Any]: Configuration as dictionary
        """
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AudienceConfig':
        """
        Create configuration from dictionary
        
        Args:
            data: Configuration data
            
        Returns:
            AudienceConfig: Configuration instance
        """
        # Convert nested dictionaries back to dataclass instances
        if 'segments' in data:
            segments = {}
            for segment_id, segment_data in data['segments'].items():
                # Convert nested configs
                if 'demographic' in segment_data:
                    segment_data['demographic'] = DemographicConfig(**segment_data['demographic'])
                if 'psychographic' in segment_data:
                    segment_data['psychographic'] = PsychographicConfig(**segment_data['psychographic'])
                if 'behavioral' in segment_data:
                    segment_data['behavioral'] = BehavioralConfig(**segment_data['behavioral'])
                
                segments[segment_id] = AudienceSegment(**segment_data)
            data['segments'] = segments
        
        if 'custom_audiences' in data:
            custom_audiences = {}
            for audience_id, audience_data in data['custom_audiences'].items():
                custom_audiences[audience_id] = CustomAudienceConfig(**audience_data)
            data['custom_audiences'] = custom_audiences
        
        if 'personalization_rules' in data:
            rules = []
            for rule_data in data['personalization_rules']:
                rules.append(PersonalizationRule(**rule_data))
            data['personalization_rules'] = rules
        
        return cls(**data)
    
    def save_to_file(self, file_path: str) -> bool:
        """
        Save configuration to JSON file
        
        Args:
            file_path: Path to save file
            
        Returns:
            bool: Success status
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, default=str)
            
            logger.info(f"Saved audience configuration to: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
            return False
    
    @classmethod
    def load_from_file(cls, file_path: str) -> Optional['AudienceConfig']:
        """
        Load configuration from JSON file
        
        Args:
            file_path: Path to load file
            
        Returns:
            Optional[AudienceConfig]: Configuration instance if successful
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            config = cls.from_dict(data)
            logger.info(f"Loaded audience configuration from: {file_path}")
            return config
            
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            return None

# Global configuration instance
audience_config = AudienceConfig()

def get_audience_config() -> AudienceConfig:
    """Get global audience configuration"""
    return audience_config

def load_audience_config(config_file: str = None) -> AudienceConfig:
    """
    Load audience configuration from file or environment
    
    Args:
        config_file: Optional config file path
        
    Returns:
        AudienceConfig: Loaded configuration
    """
    global audience_config
    
    # Try to load from specified file
    if config_file and os.path.exists(config_file):
        loaded_config = AudienceConfig.load_from_file(config_file)
        if loaded_config:
            audience_config = loaded_config
            return audience_config
    
    # Try to load from environment-specified file
    env_config_file = os.getenv('AINFLUE_AUDIENCE_CONFIG')
    if env_config_file and os.path.exists(env_config_file):
        loaded_config = AudienceConfig.load_from_file(env_config_file)
        if loaded_config:
            audience_config = loaded_config
            return audience_config
    
    # Return default configuration
    logger.info("Using default audience configuration")
    return audience_config

# Example usage
if __name__ == "__main__":
    # Create custom configuration
    config = AudienceConfig()
    
    # Add custom segment
    custom_segment = AudienceSegment(
        segment_id="creators",
        name="Content Creators",
        description="Influencers and content creators",
        type="niche",
        demographic=DemographicConfig(
            age_groups=["18-34", "25-40"],
            employment_status=["self_employed", "freelancer"]
        ),
        psychographic=PsychographicConfig(
            interests=["content_creation", "social_media", "marketing"],
            behaviors=["content_publishing", "audience_engagement"]
        )
    )
    
    config.add_segment(custom_segment)
    
    # Validate configuration
    errors = config.validate_config()
    if errors:
        print(f"Configuration errors: {errors}")
    else:
        print("Configuration is valid")
    
    # Save to file
    config.save_to_file("audience_config.json")
    
    print(f"Configuration created with {len(config.segments)} segments")