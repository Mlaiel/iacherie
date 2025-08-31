"""🎯 Quality Standards - Professional Quality Standards Framework

Comprehensive quality standards system defining quality profiles, rules,
and requirements for different audio content types and platforms.

Created by: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + Audio Developer + DevOps + DBA + Security + Microservices
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ AVERTISSEMENT STRICT ⚠️
Ce code et concept sont la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification, distribution ou reproduction sans 
autorisation écrite explicite de Fahed Mlaiel (mlaiel@live.de) est strictement 
interdite et passible de poursuites judiciaires selon la loi allemande et internationale.
"""
import logging
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Audio content types"""    MUSIC = "music"
    SPEECH = "speech"
    PODCAST = "podcast"
    AUDIOBOOK = "audiobook"
    SOUND_EFFECTS = "sound_effects"
    AMBIENT = "ambient"
    VOICEOVER = "voiceover"
    INTERVIEW = "interview"
    BROADCAST = "broadcast"
    LIVESTREAM = "livestream"
    GENERAL = "general"


class QualityLevel(Enum):
    """Quality requirement levels"""    BASIC = "basic"           # Minimum acceptable quality
    STANDARD = "standard"     # Standard professional quality
    HIGH = "high"             # High professional quality
    PREMIUM = "premium"       # Premium broadcast quality
    MASTERED = "mastered"     # Mastered release quality


class PlatformType(Enum):
    """Supported platform types"""    SPOTIFY = "spotify"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    SOUNDCLOUD = "soundcloud"
    APPLE_MUSIC = "apple_music"
    BANDCAMP = "bandcamp"
    PODCAST_PLATFORMS = "podcast_platforms"
    BROADCAST = "broadcast"
    STREAMING = "streaming"
    SOCIAL_MEDIA = "social_media"
    GENERAL = "general"


@dataclass
class QualityRule:
    """Individual quality rule definition"""    name: str
    description: str
    parameter: str
    operator: str  # ">=", "<=", "==", "!=", "in", "not_in"
    threshold: Union[float, int, str, List]
    weight: float = 1.0
    mandatory: bool = False
    category: str = "general"
    error_message: str = ""
    recommendation: str = ""


@dataclass
class QualityProfile:
    """Complete quality profile definition"""    name: str
    description: str
    content_type: ContentType
    quality_level: QualityLevel
    platform_type: PlatformType
    
    # Basic requirements
    requirements: Dict[str, Any] = field(default_factory=dict)
    
    # Platform-specific requirements
    platform_requirements: Dict[str, Any] = field(default_factory=dict)
    
    # Quality rules
    quality_rules: List[QualityRule] = field(default_factory=list)
    
    # Scoring weights
    scoring_weights: Dict[str, float] = field(default_factory=lambda: {
        "technical": 0.35,
        "perceptual": 0.30,
        "content": 0.20,
        "compliance": 0.15
    })
    
    # Thresholds
    pass_threshold: float = 0.7
    warning_threshold: float = 0.8
    
    # Metadata
    created_by: str = "system"
    version: str = "1.0"
    active: bool = True


class QualityStandards:
    """    🎯 Professional Quality Standards Manager
    
    Comprehensive quality standards system:
    - Pre-defined quality profiles for different content types
    - Platform-specific quality requirements
    - Customizable quality rules and thresholds
    - Industry standard compliance
    - Quality profile management
    """    
    def __init__(self):
        self.profiles: Dict[str, QualityProfile] = {}
        self.default_profile_name = "standard_music"
        
        # Initialize standard profiles
        self._initialize_standard_profiles()
        
        logger.info(f"QualityStandards initialized with {len(self.profiles)} profiles")
    
    def _initialize_standard_profiles(self):
        """Initialize industry-standard quality profiles"""        
        # Standard Music Profile
        self.profiles["standard_music"] = QualityProfile(
            name="standard_music",
            description="Standard professional music quality",
            content_type=ContentType.MUSIC,
            quality_level=QualityLevel.STANDARD,
            platform_type=PlatformType.GENERAL,
            requirements={
                "min_sample_rate": 44100,
                "min_bit_depth": 16,
                "min_duration": 10.0,
                "max_duration": 600.0,
                "max_silence_ratio": 0.1,
                "min_dynamic_range": 20.0
            },
            quality_rules=[
                QualityRule(
                    name="minimum_sample_rate",
                    description="Minimum sample rate for music",
                    parameter="sample_rate",
                    operator=">=",
                    threshold=44100,
                    mandatory=True,
                    category="technical",
                    error_message="Sample rate below minimum requirement",
                    recommendation="Use 44.1kHz or higher sample rate"
                ),
                QualityRule(
                    name="no_clipping",
                    description="Audio must not have significant clipping",
                    parameter="clipping_ratio",
                    operator="<=",
                    threshold=0.005,
                    weight=2.0,
                    mandatory=True,
                    category="technical",
                    error_message="Excessive audio clipping detected",
                    recommendation="Reduce input levels to prevent clipping"
                ),
                QualityRule(
                    name="minimum_snr",
                    description="Minimum signal-to-noise ratio",
                    parameter="snr",
                    operator=">=",
                    threshold=40.0,
                    weight=1.5,
                    category="technical",
                    recommendation="Apply noise reduction if SNR is low"
                ),
                QualityRule(
                    name="maximum_thd",
                    description="Maximum total harmonic distortion",
                    parameter="thd",
                    operator="<=",
                    threshold=5.0,
                    weight=1.2,
                    category="technical",
                    recommendation="Check for distortion sources"
                )
            ]
        )
        
        # Spotify Music Profile
        self.profiles["spotify_music"] = QualityProfile(
            name="spotify_music",
            description="Spotify optimized music quality",
            content_type=ContentType.MUSIC,
            quality_level=QualityLevel.HIGH,
            platform_type=PlatformType.SPOTIFY,
            requirements={
                "min_sample_rate": 44100,
                "preferred_sample_rate": 44100,
                "min_bit_depth": 16,
                "preferred_bit_depth": 24,
                "min_duration": 5.0,
                "max_duration": 1200.0,  # 20 minutes
                "max_silence_ratio": 0.05,
                "target_lufs": -14.0,
                "lufs_tolerance": 2.0,
                "min_dynamic_range": 8.0
            },
            platform_requirements={
                "max_file_size": 50 * 1024 * 1024,  # 50MB
                "required_formats": ["wav", "flac", "mp3"],
                "required_sample_rates": [44100, 48000, 96000],
                "max_channels": 2
            },
            quality_rules=[
                QualityRule(
                    name="spotify_loudness",
                    description="Spotify loudness standard (-14 LUFS)",
                    parameter="lufs",
                    operator="in_range",
                    threshold=[-16, -12],
                    weight=2.0,
                    category="perceptual",
                    recommendation="Normalize to -14 LUFS for Spotify"
                ),
                QualityRule(
                    name="spotify_peak",
                    description="Peak level below -1 dBTP",
                    parameter="peak_dbtp",
                    operator="<=",
                    threshold=-1.0,
                    weight=1.5,
                    mandatory=True,
                    category="technical",
                    recommendation="Apply true peak limiting"
                )
            ]
        )
        
        # YouTube Music Profile
        self.profiles["youtube_music"] = QualityProfile(
            name="youtube_music",
            description="YouTube optimized music quality",
            content_type=ContentType.MUSIC,
            quality_level=QualityLevel.STANDARD,
            platform_type=PlatformType.YOUTUBE,
            requirements={
                "min_sample_rate": 44100,
                "min_bit_depth": 16,
                "min_duration": 1.0,
                "max_duration": 3600.0,  # 1 hour
                "target_lufs": -13.0,
                "lufs_tolerance": 3.0
            },
            platform_requirements={
                "max_file_size": 128 * 1024 * 1024,  # 128MB
                "required_formats": ["wav", "mp3", "aac"],
                "required_sample_rates": [44100, 48000],
                "max_channels": 2
            }
        )
        
        # Podcast Profile
        self.profiles["podcast_standard"] = QualityProfile(
            name="podcast_standard",
            description="Standard podcast quality",
            content_type=ContentType.PODCAST,
            quality_level=QualityLevel.STANDARD,
            platform_type=PlatformType.PODCAST_PLATFORMS,
            requirements={
                "min_sample_rate": 44100,
                "preferred_sample_rate": 44100,
                "min_bit_depth": 16,
                "min_duration": 60.0,  # 1 minute
                "max_duration": 14400.0,  # 4 hours
                "max_silence_ratio": 0.15,
                "target_lufs": -16.0,
                "lufs_tolerance": 3.0
            },
            platform_requirements={
                "max_file_size": 500 * 1024 * 1024,  # 500MB
                "required_formats": ["mp3", "aac"],
                "required_sample_rates": [44100, 48000],
                "max_channels": 2,
                "required_mono": False
            }
        )
        
        # Speech Profile
        self.profiles["speech_standard"] = QualityProfile(
            name="speech_standard",
            description="Standard speech quality",
            content_type=ContentType.SPEECH,
            quality_level=QualityLevel.STANDARD,
            platform_type=PlatformType.GENERAL,
            requirements={
                "min_sample_rate": 22050,
                "preferred_sample_rate": 44100,
                "min_bit_depth": 16,
                "min_duration": 1.0,
                "max_duration": 3600.0,
                "max_silence_ratio": 0.3,
                "min_snr": 35.0
            },
            quality_rules=[
                QualityRule(
                    name="speech_clarity",
                    description="Speech must be clear and intelligible",
                    parameter="spectral_centroid",
                    operator="in_range",
                    threshold=[1000, 4000],  # Typical speech range
                    weight=2.0,
                    category="perceptual",
                    recommendation="Optimize frequency response for speech"
                ),
                QualityRule(
                    name="speech_consistency",
                    description="Consistent speech levels",
                    parameter="level_variation",
                    operator="<=",
                    threshold=6.0,  # Max 6dB variation
                    weight=1.5,
                    category="perceptual",
                    recommendation="Apply compression to even out levels"
                )
            ]
        )
        
        # TikTok Profile
        self.profiles["tiktok_audio"] = QualityProfile(
            name="tiktok_audio",
            description="TikTok optimized audio",
            content_type=ContentType.GENERAL,
            quality_level=QualityLevel.STANDARD,
            platform_type=PlatformType.TIKTOK,
            requirements={
                "min_sample_rate": 44100,
                "min_bit_depth": 16,
                "min_duration": 1.0,
                "max_duration": 180.0,  # 3 minutes
                "target_lufs": -12.0,
                "lufs_tolerance": 2.0
            },
            platform_requirements={
                "max_file_size": 50 * 1024 * 1024,  # 50MB
                "required_formats": ["mp3", "aac"],
                "required_sample_rates": [44100],
                "max_channels": 2
            }
        )
        
        # Broadcast Quality Profile
        self.profiles["broadcast_quality"] = QualityProfile(
            name="broadcast_quality",
            description="Professional broadcast quality",
            content_type=ContentType.BROADCAST,
            quality_level=QualityLevel.PREMIUM,
            platform_type=PlatformType.BROADCAST,
            requirements={
                "min_sample_rate": 48000,
                "min_bit_depth": 24,
                "min_duration": 1.0,
                "max_duration": 7200.0,  # 2 hours
                "max_silence_ratio": 0.05,
                "target_lufs": -23.0,
                "lufs_tolerance": 1.0,
                "min_dynamic_range": 30.0
            },
            quality_rules=[
                QualityRule(
                    name="broadcast_peak",
                    description="Peak level below -9 dBFS",
                    parameter="peak_dbfs",
                    operator="<=",
                    threshold=-9.0,
                    mandatory=True,
                    category="technical",
                    recommendation="Apply broadcast limiting"
                ),
                QualityRule(
                    name="broadcast_stereo",
                    description="Stereo compatibility required",
                    parameter="stereo_compatible",
                    operator="==",
                    threshold=True,
                    weight=1.5,
                    category="technical",
                    recommendation="Ensure mono compatibility"
                )
            ]
        )
        
        # High-Resolution Audio Profile
        self.profiles["hires_audio"] = QualityProfile(
            name="hires_audio",
            description="High-resolution audio quality",
            content_type=ContentType.MUSIC,
            quality_level=QualityLevel.PREMIUM,
            platform_type=PlatformType.GENERAL,
            requirements={
                "min_sample_rate": 96000,
                "min_bit_depth": 24,
                "min_duration": 10.0,
                "max_duration": 1200.0,
                "max_silence_ratio": 0.02,
                "min_dynamic_range": 40.0,
                "min_snr": 60.0
            },
            quality_rules=[
                QualityRule(
                    name="hires_sample_rate",
                    description="High-resolution sample rate",
                    parameter="sample_rate",
                    operator=">=",
                    threshold=96000,
                    mandatory=True,
                    category="technical"
                ),
                QualityRule(
                    name="hires_bit_depth",
                    description="High-resolution bit depth",
                    parameter="bit_depth",
                    operator=">=",
                    threshold=24,
                    mandatory=True,
                    category="technical"
                )
            ]
        )
    
    def get_profile(self, profile_name: str) -> Optional[QualityProfile]:
        """Get quality profile by name"""        return self.profiles.get(profile_name)
    
    def get_default_profile(self) -> QualityProfile:
        """Get default quality profile"""        return self.profiles[self.default_profile_name]
    
    def list_profiles(self) -> List[str]:
        """List all available profile names"""        return list(self.profiles.keys())
    
    def get_profiles_by_content_type(self, content_type: ContentType) -> List[QualityProfile]:
        """Get profiles filtered by content type"""        return [
            profile for profile in self.profiles.values()
            if profile.content_type == content_type
        ]
    
    def get_profiles_by_platform(self, platform_type: PlatformType) -> List[QualityProfile]:
        """Get profiles filtered by platform type"""        return [
            profile for profile in self.profiles.values()
            if profile.platform_type == platform_type or profile.platform_type == PlatformType.GENERAL
        ]
    
    def get_profiles_by_quality_level(self, quality_level: QualityLevel) -> List[QualityProfile]:
        """Get profiles filtered by quality level"""        return [
            profile for profile in self.profiles.values()
            if profile.quality_level == quality_level
        ]
    
    def add_profile(self, profile: QualityProfile) -> bool:
        """Add custom quality profile"""        if profile.name in self.profiles:
            logger.warning(f"Profile {profile.name} already exists, overwriting")
        
        self.profiles[profile.name] = profile
        logger.info(f"Added quality profile: {profile.name}")
        return True
    
    def remove_profile(self, profile_name: str) -> bool:
        """Remove quality profile"""        if profile_name in self.profiles:
            if profile_name == self.default_profile_name:
                logger.error("Cannot remove default profile")
                return False
            
            del self.profiles[profile_name]
            logger.info(f"Removed quality profile: {profile_name}")
            return True
        
        logger.warning(f"Profile not found: {profile_name}")
        return False
    
    def update_profile(self, profile_name: str, updates: Dict[str, Any]) -> bool:
        """Update quality profile parameters"""        if profile_name not in self.profiles:
            logger.error(f"Profile not found: {profile_name}")
            return False
        
        profile = self.profiles[profile_name]
        
        # Update requirements
        if "requirements" in updates:
            profile.requirements.update(updates["requirements"])
        
        # Update platform requirements
        if "platform_requirements" in updates:
            profile.platform_requirements.update(updates["platform_requirements"])
        
        # Update thresholds
        if "pass_threshold" in updates:
            profile.pass_threshold = updates["pass_threshold"]
        
        if "warning_threshold" in updates:
            profile.warning_threshold = updates["warning_threshold"]
        
        # Update scoring weights
        if "scoring_weights" in updates:
            profile.scoring_weights.update(updates["scoring_weights"])
        
        logger.info(f"Updated quality profile: {profile_name}")
        return True
    
    def validate_profile(self, profile: QualityProfile) -> List[str]:
        """Validate quality profile configuration"""        issues = []
        
        # Check required fields
        if not profile.name:
            issues.append("Profile name is required")
        
        if not profile.description:
            issues.append("Profile description is required")
        
        # Check thresholds
        if not (0.0 <= profile.pass_threshold <= 1.0):
            issues.append("Pass threshold must be between 0.0 and 1.0")
        
        if not (0.0 <= profile.warning_threshold <= 1.0):
            issues.append("Warning threshold must be between 0.0 and 1.0")
        
        if profile.pass_threshold > profile.warning_threshold:
            issues.append("Pass threshold cannot be higher than warning threshold")
        
        # Check scoring weights
        total_weight = sum(profile.scoring_weights.values())
        if abs(total_weight - 1.0) > 0.1:
            issues.append(f"Scoring weights should sum to 1.0, got {total_weight}")
        
        # Validate quality rules
        for rule in profile.quality_rules:
            if not rule.name:
                issues.append("Quality rule name is required")
            
            if rule.operator not in [">=", "<=", "==", "!=", "in", "not_in", "in_range"]:
                issues.append(f"Invalid operator in rule {rule.name}: {rule.operator}")
            
            if not (0.0 <= rule.weight <= 10.0):
                issues.append(f"Rule weight should be between 0.0 and 10.0: {rule.name}")
        
        return issues
    
    def create_custom_profile(
        self,
        name: str,
        description: str,
        content_type: ContentType,
        quality_level: QualityLevel,
        platform_type: PlatformType,
        requirements: Dict[str, Any],
        quality_rules: List[QualityRule] = None
    ) -> QualityProfile:
        """Create custom quality profile"""        
        profile = QualityProfile(
            name=name,
            description=description,
            content_type=content_type,
            quality_level=quality_level,
            platform_type=platform_type,
            requirements=requirements,
            quality_rules=quality_rules or [],
            created_by="custom"
        )
        
        # Validate profile
        issues = self.validate_profile(profile)
        if issues:
            logger.error(f"Profile validation failed: {issues}")
            raise ValueError(f"Invalid profile configuration: {', '.join(issues)}")
        
        return profile
    
    def get_recommended_profile(
        self,
        content_type: Optional[ContentType] = None,
        platform_type: Optional[PlatformType] = None,
        quality_level: Optional[QualityLevel] = None
    ) -> QualityProfile:
        """Get recommended profile based on criteria"""        
        # Filter profiles by criteria
        candidates = list(self.profiles.values())
        
        if content_type:
            candidates = [p for p in candidates if p.content_type == content_type]
        
        if platform_type:
            candidates = [
                p for p in candidates 
                if p.platform_type == platform_type or p.platform_type == PlatformType.GENERAL
            ]
        
        if quality_level:
            candidates = [p for p in candidates if p.quality_level == quality_level]
        
        # Return best match or default
        if candidates:
            # Prefer platform-specific profiles
            platform_specific = [p for p in candidates if p.platform_type != PlatformType.GENERAL]
            if platform_specific:
                return platform_specific[0]
            return candidates[0]
        
        return self.get_default_profile()
    
    def export_profiles(self, file_path: str, profile_names: List[str] = None):
        """Export quality profiles to JSON file"""        
        if profile_names is None:
            profiles_to_export = self.profiles
        else:
            profiles_to_export = {
                name: self.profiles[name] 
                for name in profile_names 
                if name in self.profiles
            }
        
        # Convert to serializable format
        export_data = {}
        for name, profile in profiles_to_export.items():
            export_data[name] = {
                "name": profile.name,
                "description": profile.description,
                "content_type": profile.content_type.value,
                "quality_level": profile.quality_level.value,
                "platform_type": profile.platform_type.value,
                "requirements": profile.requirements,
                "platform_requirements": profile.platform_requirements,
                "quality_rules": [
                    {
                        "name": rule.name,
                        "description": rule.description,
                        "parameter": rule.parameter,
                        "operator": rule.operator,
                        "threshold": rule.threshold,
                        "weight": rule.weight,
                        "mandatory": rule.mandatory,
                        "category": rule.category,
                        "error_message": rule.error_message,
                        "recommendation": rule.recommendation
                    }
                    for rule in profile.quality_rules
                ],
                "scoring_weights": profile.scoring_weights,
                "pass_threshold": profile.pass_threshold,
                "warning_threshold": profile.warning_threshold,
                "created_by": profile.created_by,
                "version": profile.version,
                "active": profile.active
            }
        
        with open(file_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Exported {len(export_data)} profiles to {file_path}")
    
    def import_profiles(self, file_path: str, overwrite: bool = False):
        """Import quality profiles from JSON file"""        
        try:
            with open(file_path, 'r') as f:
                import_data = json.load(f)
            
            imported_count = 0
            skipped_count = 0
            
            for name, profile_data in import_data.items():
                if name in self.profiles and not overwrite:
                    logger.warning(f"Profile {name} already exists, skipping")
                    skipped_count += 1
                    continue
                
                # Convert back to objects
                quality_rules = []
                for rule_data in profile_data.get("quality_rules", []):
                    rule = QualityRule(**rule_data)
                    quality_rules.append(rule)
                
                profile = QualityProfile(
                    name=profile_data["name"],
                    description=profile_data["description"],
                    content_type=ContentType(profile_data["content_type"]),
                    quality_level=QualityLevel(profile_data["quality_level"]),
                    platform_type=PlatformType(profile_data["platform_type"]),
                    requirements=profile_data["requirements"],
                    platform_requirements=profile_data.get("platform_requirements", {}),
                    quality_rules=quality_rules,
                    scoring_weights=profile_data.get("scoring_weights", {}),
                    pass_threshold=profile_data.get("pass_threshold", 0.7),
                    warning_threshold=profile_data.get("warning_threshold", 0.8),
                    created_by=profile_data.get("created_by", "imported"),
                    version=profile_data.get("version", "1.0"),
                    active=profile_data.get("active", True)
                )
                
                # Validate imported profile
                issues = self.validate_profile(profile)
                if issues:
                    logger.error(f"Imported profile {name} failed validation: {issues}")
                    continue
                
                self.profiles[name] = profile
                imported_count += 1
            
            logger.info(f"Imported {imported_count} profiles, skipped {skipped_count}")
            
        except Exception as e:
            logger.error(f"Failed to import profiles: {e}")
            raise
    
    def set_default_profile(self, profile_name: str) -> bool:
        """Set default quality profile"""        if profile_name not in self.profiles:
            logger.error(f"Profile not found: {profile_name}")
            return False
        
        self.default_profile_name = profile_name
        logger.info(f"Set default profile to: {profile_name}")
        return True
    
    def get_profile_summary(self) -> Dict[str, Any]:
        """Get summary of all profiles"""        summary = {
            "total_profiles": len(self.profiles),
            "default_profile": self.default_profile_name,
            "by_content_type": {},
            "by_platform": {},
            "by_quality_level": {}
        }
        
        for profile in self.profiles.values():
            # Count by content type
            content_type = profile.content_type.value
            if content_type not in summary["by_content_type"]:
                summary["by_content_type"][content_type] = 0
            summary["by_content_type"][content_type] += 1
            
            # Count by platform
            platform = profile.platform_type.value
            if platform not in summary["by_platform"]:
                summary["by_platform"][platform] = 0
            summary["by_platform"][platform] += 1
            
            # Count by quality level
            quality_level = profile.quality_level.value
            if quality_level not in summary["by_quality_level"]:
                summary["by_quality_level"][quality_level] = 0
            summary["by_quality_level"][quality_level] += 1
        
        return summary
