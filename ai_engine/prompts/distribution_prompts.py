"""Professional Multi-Platform Distribution Prompts System
Professional prompts for content distribution across multiple platforms

Created by: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️ COPYRIGHT WARNING ⚠️
This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de)
Any unauthorized use, copying, or distribution without explicit written permission is strictly prohibited.
Violators will be prosecuted under German and International copyright law.
"""from typing import Dict, List, Optional, Tuple, Any, Union
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import logging
from pydantic import BaseModel, Field
import uuid

logger = logging.getLogger(__name__)

class DistributionPlatform(Enum):
    """Supported distribution platforms"""    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    YOUTUBE = "youtube"
    YOUTUBE_MUSIC = "youtube_music"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    TWITCH = "twitch"
    DISCORD = "discord"
    REDDIT = "reddit"
    PINTEREST = "pinterest"

class DistributionStrategy(Enum):
    """Distribution strategies"""    SIMULTANEOUS = "simultaneous"
    SEQUENTIAL = "sequential"
    PLATFORM_EXCLUSIVE = "platform_exclusive"
    TIERED_RELEASE = "tiered_release"
    VIRAL_CASCADE = "viral_cascade"

class ContentAdaptation(Enum):
    """Content adaptation types"""    FORMAT_OPTIMIZATION = "format_optimization"
    PLATFORM_SPECIFIC = "platform_specific"
    AUDIENCE_TAILORED = "audience_tailored"
    REGIONAL_LOCALIZATION = "regional_localization"

@dataclass
class DistributionContext:
    """Context for distribution prompt generation"""    content_type: str
    target_platforms: List[DistributionPlatform]
    distribution_strategy: DistributionStrategy
    content_adaptations: List[ContentAdaptation]
    timeline: Dict[str, str]
    budget: Dict[str, float]
    target_audience: Dict[str, Any]

class MultiPlatformDistributionPrompts:
    """Professional Multi-Platform Distribution Prompts System"""    
    def __init__(self):
        """Initialize the distribution prompts system"""        self.distribution_templates = {}
        self.platform_specifications = {}
        self.optimization_strategies = {}
        self._load_distribution_templates()
    
    def _load_distribution_templates(self) -> None:
        """Load distribution templates and platform specifications"""        
        # Distribution Templates
        self.distribution_templates = {
            "music_distribution": {
                DistributionStrategy.SIMULTANEOUS: {
                    "id": "music_simultaneous_distribution",
                    "template": """                    Create comprehensive simultaneous music distribution strategy:
                    
                    Release Overview:
                    - Track/Album: {release_title}
                    - Artist: {artist_name}
                    - Genre: {genre}
                    - Release date: {release_date}
                    - Distribution scope: {distribution_scope}
                    - Target markets: {target_markets}
                    
                    Platform Distribution Strategy:
                    
                    Streaming Platforms:
                    1. Spotify:
                       - Pre-save campaign: {spotify_presave}
                       - Playlist submission: {spotify_playlists}
                       - Canvas video: {spotify_canvas}
                       - Artist pick: {spotify_artist_pick}
                       - Release radar optimization: {spotify_release_radar}
                    
                    2. Apple Music:
                       - Spatial audio version: {apple_spatial_audio}
                       - Apple Music playlist pitching: {apple_playlists}
                       - Connect posts: {apple_connect_posts}
                       - Artist spotlight: {apple_spotlight}
                    
                    3. YouTube Music:
                       - Official video upload: {youtube_official_video}
                       - YouTube Shorts clips: {youtube_shorts}
                       - Lyric video: {youtube_lyric_video}
                       - Artist channel optimization: {youtube_channel_opt}
                    
                    4. SoundCloud:
                       - Pro account features: {soundcloud_pro}
                       - Repost network activation: {soundcloud_reposts}
                       - Community engagement: {soundcloud_community}
                    
                    Social Media Distribution:
                    
                    1. Instagram:
                       - Feed post with audio: {instagram_feed}
                       - Stories with music sticker: {instagram_stories}
                       - Reels with track: {instagram_reels}
                       - IGTV behind-the-scenes: {instagram_igtv}
                    
                    2. TikTok:
                       - Original sound creation: {tiktok_original_sound}
                       - Hashtag challenge: {tiktok_challenge}
                       - Creator partnerships: {tiktok_creators}
                       - Trend integration: {tiktok_trends}
                    
                    3. Twitter:
                       - Audio tweet feature: {twitter_audio}
                       - Twitter Spaces live session: {twitter_spaces}
                       - Engagement threads: {twitter_threads}
                    
                    Content Adaptation by Platform:
                    
                    Audio Formats:
                    - Streaming quality: {streaming_format} (WAV, 24-bit, 48kHz)
                    - Compressed versions: {compressed_formats} (MP3, AAC)
                    - Lossless versions: {lossless_formats} (FLAC, ALAC)
                    - Platform-specific: {platform_specific_formats}
                    
                    Visual Content:
                    - Cover art variations: {cover_art_variations}
                    - Platform-specific sizes: {cover_sizes}
                    - Animated covers: {animated_covers}
                    - Video content: {video_content}
                    
                    Timing and Coordination:
                    - Global release time: {global_release_time} UTC
                    - Platform sync verification: {sync_verification}
                    - Backup release schedule: {backup_schedule}
                    - Time zone considerations: {timezone_strategy}
                    
                    Marketing Coordination:
                    - Cross-platform messaging: {cross_platform_messaging}
                    - Unified hashtag strategy: {hashtag_strategy}
                    - Press release timing: {press_release_timing}
                    - Influencer coordination: {influencer_coordination}
                    
                    Performance Tracking:
                    - Real-time monitoring: {realtime_monitoring}
                    - Platform-specific metrics: {platform_metrics}
                    - Cross-platform analytics: {cross_platform_analytics}
                    - Performance benchmarks: {performance_benchmarks}
                    
                    Legal and Rights Management:
                    - Distribution rights: {distribution_rights}
                    - Territory restrictions: {territory_restrictions}
                    - Revenue sharing: {revenue_sharing}
                    - Copyright protection: {copyright_protection}
                    
                    Crisis Management:
                    - Platform failure contingency: {platform_failure_plan}
                    - Content issues protocol: {content_issues_protocol}
                    - Communication crisis plan: {crisis_communication}
                    
                    Success Metrics:
                    - First 24-hour targets: {first_24h_targets}
                    - Weekly performance goals: {weekly_goals}
                    - Cross-platform synergy: {synergy_metrics}
                    - Long-term growth indicators: {growth_indicators}
                    
                    Output Requirements:
                    1. Complete distribution timeline
                    2. Platform-specific optimization guides
                    3. Content adaptation specifications
                    4. Performance tracking dashboard
                    5. Crisis management protocols
                    6. Success measurement framework
                    """,
                    "variables": ["release_title", "artist_name", "genre", "release_date", "distribution_scope", "target_markets", "spotify_presave", "spotify_playlists", "spotify_canvas", "spotify_artist_pick", "spotify_release_radar", "apple_spatial_audio", "apple_playlists", "apple_connect_posts", "apple_spotlight", "youtube_official_video", "youtube_shorts", "youtube_lyric_video", "youtube_channel_opt", "soundcloud_pro", "soundcloud_reposts", "soundcloud_community", "instagram_feed", "instagram_stories", "instagram_reels", "instagram_igtv", "tiktok_original_sound", "tiktok_challenge", "tiktok_creators", "tiktok_trends", "twitter_audio", "twitter_spaces", "twitter_threads", "streaming_format", "compressed_formats", "lossless_formats", "platform_specific_formats", "cover_art_variations", "cover_sizes", "animated_covers", "video_content", "global_release_time", "sync_verification", "backup_schedule", "timezone_strategy", "cross_platform_messaging", "hashtag_strategy", "press_release_timing", "influencer_coordination", "realtime_monitoring", "platform_metrics", "cross_platform_analytics", "performance_benchmarks", "distribution_rights", "territory_restrictions", "revenue_sharing", "copyright_protection", "platform_failure_plan", "content_issues_protocol", "crisis_communication", "first_24h_targets", "weekly_goals", "synergy_metrics", "growth_indicators"],
                    "quality_score": 96
                },
                
                DistributionStrategy.TIERED_RELEASE: {
                    "id": "music_tiered_distribution",
                    "template": """                    Create strategic tiered music distribution system:
                    
                    Tiered Release Strategy:
                    - Release title: {release_title}
                    - Artist: {artist_name}
                    - Total distribution timeline: {total_timeline}
                    - Tier strategy rationale: {tier_rationale}
                    
                    Tier 1 - Premium/Exclusive Release:
                    
                    Exclusive Platforms (Week 1):
                    - Primary platform: {tier1_primary_platform}
                    - Exclusive period: {tier1_exclusive_period}
                    - Premium features: {tier1_premium_features}
                    - VIP access: {tier1_vip_access}
                    
                    Tier 1 Marketing:
                    - Exclusive announcement: {tier1_announcement}
                    - Limited access strategy: {tier1_limited_access}
                    - FOMO (Fear of Missing Out) tactics: {tier1_fomo}
                    - Premium subscriber benefits: {tier1_subscriber_benefits}
                    
                    Tier 2 - Major Streaming Platforms:
                    
                    Major Platform Release (Week 2-3):
                    - Platforms: {tier2_platforms}
                    - Release timing: {tier2_timing}
                    - Platform-specific features: {tier2_features}
                    - Cross-platform coordination: {tier2_coordination}
                    
                    Tier 2 Marketing:
                    - Broader announcement: {tier2_announcement}
                    - Playlist pitching campaign: {tier2_playlist_campaign}
                    - Algorithm optimization: {tier2_algorithm_opt}
                    - Influencer partnerships: {tier2_influencers}
                    
                    Tier 3 - Social Media & Video Platforms:
                    
                    Social Platform Release (Week 3-4):
                    - Platforms: {tier3_platforms}
                    - Content adaptations: {tier3_adaptations}
                    - Viral optimization: {tier3_viral_opt}
                    - Community engagement: {tier3_community}
                    
                    Tier 3 Marketing:
                    - Viral campaign launch: {tier3_viral_campaign}
                    - User-generated content: {tier3_ugc}
                    - Challenge/trend creation: {tier3_challenges}
                    - Mass engagement tactics: {tier3_mass_engagement}
                    
                    Tier 4 - Free & Open Platforms:
                    
                    Open Platform Release (Week 4+):
                    - Platforms: {tier4_platforms}
                    - Free access strategy: {tier4_free_strategy}
                    - Monetization alternatives: {tier4_monetization}
                    - Long-tail distribution: {tier4_longtail}
                    
                    Content Progression Strategy:
                    - Exclusive content: {exclusive_content}
                    - Progressive reveals: {progressive_reveals}
                    - Behind-the-scenes releases: {bts_releases}
                    - Remix/alternative versions: {remix_versions}
                    
                    Audience Journey Mapping:
                    1. Early Adopters (Tier 1):
                       - Profile: {early_adopter_profile}
                       - Engagement strategy: {early_adopter_engagement}
                       - Conversion goals: {early_adopter_conversion}
                    
                    2. Core Audience (Tier 2):
                       - Profile: {core_audience_profile}
                       - Engagement strategy: {core_audience_engagement}
                       - Growth objectives: {core_audience_growth}
                    
                    3. Mass Market (Tier 3-4):
                       - Profile: {mass_market_profile}
                       - Viral strategies: {mass_market_viral}
                       - Reach maximization: {mass_market_reach}
                    
                    Performance Analytics by Tier:
                    - Tier 1 metrics: {tier1_metrics}
                    - Tier 2 metrics: {tier2_metrics}
                    - Tier 3 metrics: {tier3_metrics}
                    - Tier 4 metrics: {tier4_metrics}
                    - Cross-tier analysis: {cross_tier_analysis}
                    
                    Revenue Optimization:
                    - Tier-based pricing: {tier_pricing}
                    - Revenue per tier: {tier_revenue}
                    - Lifetime value optimization: {ltv_optimization}
                    - Upselling opportunities: {upselling_opportunities}
                    
                    Feedback Integration:
                    - Tier 1 feedback collection: {tier1_feedback}
                    - Content optimization: {content_optimization}
                    - Strategy refinement: {strategy_refinement}
                    - Tier 2+ improvements: {tier_improvements}
                    
                    Output Requirements:
                    1. Detailed tier-by-tier release plan
                    2. Content progression strategy
                    3. Audience journey mapping
                    4. Performance analytics framework
                    5. Revenue optimization plan
                    6. Feedback integration system
                    """,
                    "variables": ["release_title", "artist_name", "total_timeline", "tier_rationale", "tier1_primary_platform", "tier1_exclusive_period", "tier1_premium_features", "tier1_vip_access", "tier1_announcement", "tier1_limited_access", "tier1_fomo", "tier1_subscriber_benefits", "tier2_platforms", "tier2_timing", "tier2_features", "tier2_coordination", "tier2_announcement", "tier2_playlist_campaign", "tier2_algorithm_opt", "tier2_influencers", "tier3_platforms", "tier3_adaptations", "tier3_viral_opt", "tier3_community", "tier3_viral_campaign", "tier3_ugc", "tier3_challenges", "tier3_mass_engagement", "tier4_platforms", "tier4_free_strategy", "tier4_monetization", "tier4_longtail", "exclusive_content", "progressive_reveals", "bts_releases", "remix_versions", "early_adopter_profile", "early_adopter_engagement", "early_adopter_conversion", "core_audience_profile", "core_audience_engagement", "core_audience_growth", "mass_market_profile", "mass_market_viral", "mass_market_reach", "tier1_metrics", "tier2_metrics", "tier3_metrics", "tier4_metrics", "cross_tier_analysis", "tier_pricing", "tier_revenue", "ltv_optimization", "upselling_opportunities", "tier1_feedback", "content_optimization", "strategy_refinement", "tier_improvements"],
                    "quality_score": 95
                }
            },
            
            "video_distribution": {
                DistributionStrategy.VIRAL_CASCADE: {
                    "id": "video_viral_cascade_distribution",
                    "template": """                    Create viral cascade video distribution strategy:
                    
                    Video Content Overview:
                    - Video title: {video_title}
                    - Creator: {creator_name}
                    - Duration: {video_duration}
                    - Genre/Category: {video_category}
                    - Target demographic: {target_demographic}
                    
                    Viral Cascade Strategy:
                    
                    Phase 1 - Seed Platform (Hour 0):
                    - Primary platform: {seed_platform}
                    - Initial audience: {seed_audience}
                    - Engagement triggers: {seed_triggers}
                    - Viral elements: {viral_elements}
                    
                    Phase 1 Optimization:
                    - Hook within first 3 seconds: {first_3_seconds_hook}
                    - Emotional response targeting: {emotional_triggers}
                    - Shareable moments: {shareable_moments}
                    - Call-to-action placement: {cta_placement}
                    
                    Phase 2 - Rapid Expansion (Hours 1-6):
                    - Secondary platforms: {phase2_platforms}
                    - Cross-posting timing: {phase2_timing}
                    - Platform adaptations: {phase2_adaptations}
                    - Amplification tactics: {phase2_amplification}
                    
                    Platform-Specific Viral Optimization:
                    
                    TikTok Viral Strategy:
                    - Trending audio integration: {tiktok_trending_audio}
                    - Hashtag combinations: {tiktok_hashtags}
                    - For You Page optimization: {tiktok_fyp_opt}
                    - Creator collaboration: {tiktok_creators}
                    - Challenge creation: {tiktok_challenge}
                    
                    Instagram Viral Strategy:
                    - Reels algorithm optimization: {instagram_reels_opt}
                    - Story engagement boost: {instagram_story_boost}
                    - IGTV discoverability: {instagram_igtv_disc}
                    - Feed post engagement: {instagram_feed_eng}
                    
                    YouTube Viral Strategy:
                    - Thumbnail optimization: {youtube_thumbnail}
                    - Title A/B testing: {youtube_title_testing}
                    - Description optimization: {youtube_description}
                    - Tags and categories: {youtube_tags}
                    - Community engagement: {youtube_community}
                    
                    Twitter Viral Strategy:
                    - Thread creation: {twitter_threads}
                    - Retweet amplification: {twitter_retweets}
                    - Trending topic integration: {twitter_trends}
                    - Influencer mentions: {twitter_influencers}
                    
                    Phase 3 - Sustained Momentum (Hours 6-24):
                    - Momentum maintenance: {momentum_maintenance}
                    - Content variations: {content_variations}
                    - Community response: {community_response}
                    - Media outreach: {media_outreach}
                    
                    Phase 4 - Long-tail Distribution (Days 1-7):
                    - Platform saturation: {platform_saturation}
                    - Niche community targeting: {niche_targeting}
                    - International expansion: {international_expansion}
                    - Evergreen optimization: {evergreen_optimization}
                    
                    Viral Amplification Tactics:
                    
                    1. Influencer Network Activation:
                       - Micro-influencer outreach: {micro_influencer_outreach}
                       - Nano-influencer engagement: {nano_influencer_engagement}
                       - Celebrity endorsements: {celebrity_endorsements}
                       - Creator collaborations: {creator_collaborations}
                    
                    2. Community Engagement:
                       - Reddit strategy: {reddit_strategy}
                       - Discord community: {discord_community}
                       - Facebook groups: {facebook_groups}
                       - Specialized forums: {specialized_forums}
                    
                    3. Paid Amplification:
                       - Strategic ad spend: ${strategic_ad_spend}
                       - Boosted posts timing: {boosted_posts_timing}
                       - Influencer partnerships: ${influencer_budget}
                       - Cross-platform promotion: ${cross_platform_budget}
                    
                    Content Adaptation by Platform:
                    - Format variations: {format_variations}
                    - Aspect ratio optimization: {aspect_ratios}
                    - Duration adjustments: {duration_adjustments}
                    - Platform-specific elements: {platform_elements}
                    
                    Real-time Monitoring and Optimization:
                    - Viral tracking metrics: {viral_metrics}
                    - Real-time performance: {realtime_performance}
                    - Optimization triggers: {optimization_triggers}
                    - Response protocols: {response_protocols}
                    
                    Crisis Management:
                    - Negative feedback handling: {negative_feedback_protocol}
                    - Content moderation: {content_moderation}
                    - Platform violations: {platform_violations_protocol}
                    - Reputation management: {reputation_management}
                    
                    Success Metrics:
                    - Viral coefficient target: {viral_coefficient}
                    - Cross-platform reach: {cross_platform_reach}
                    - Engagement velocity: {engagement_velocity}
                    - Share-to-view ratio: {share_view_ratio}
                    - Conversion metrics: {conversion_metrics}
                    
                    Post-Viral Strategy:
                    - Audience retention: {audience_retention}
                    - Follow-up content: {followup_content}
                    - Monetization opportunities: {monetization_opportunities}
                    - Long-term growth: {longterm_growth}
                    
                    Output Requirements:
                    1. Hour-by-hour distribution timeline
                    2. Platform-specific optimization guides
                    3. Viral amplification toolkit
                    4. Real-time monitoring dashboard
                    5. Crisis management protocols
                    6. Success measurement framework
                    """,
                    "variables": ["video_title", "creator_name", "video_duration", "video_category", "target_demographic", "seed_platform", "seed_audience", "seed_triggers", "viral_elements", "first_3_seconds_hook", "emotional_triggers", "shareable_moments", "cta_placement", "phase2_platforms", "phase2_timing", "phase2_adaptations", "phase2_amplification", "tiktok_trending_audio", "tiktok_hashtags", "tiktok_fyp_opt", "tiktok_creators", "tiktok_challenge", "instagram_reels_opt", "instagram_story_boost", "instagram_igtv_disc", "instagram_feed_eng", "youtube_thumbnail", "youtube_title_testing", "youtube_description", "youtube_tags", "youtube_community", "twitter_threads", "twitter_retweets", "twitter_trends", "twitter_influencers", "momentum_maintenance", "content_variations", "community_response", "media_outreach", "platform_saturation", "niche_targeting", "international_expansion", "evergreen_optimization", "micro_influencer_outreach", "nano_influencer_engagement", "celebrity_endorsements", "creator_collaborations", "reddit_strategy", "discord_community", "facebook_groups", "specialized_forums", "strategic_ad_spend", "boosted_posts_timing", "influencer_budget", "cross_platform_budget", "format_variations", "aspect_ratios", "duration_adjustments", "platform_elements", "viral_metrics", "realtime_performance", "optimization_triggers", "response_protocols", "negative_feedback_protocol", "content_moderation", "platform_violations_protocol", "reputation_management", "viral_coefficient", "cross_platform_reach", "engagement_velocity", "share_view_ratio", "conversion_metrics", "audience_retention", "followup_content", "monetization_opportunities", "longterm_growth"],
                    "quality_score": 97
                }
            }
        }
        
        # Platform Specifications
        self.platform_specifications = {
            DistributionPlatform.INSTAGRAM: {
                "content_formats": {
                    "feed_post": {"aspect_ratio": "1:1", "max_resolution": "1080x1080", "formats": ["JPG", "PNG"]},
                    "story": {"aspect_ratio": "9:16", "max_resolution": "1080x1920", "formats": ["JPG", "PNG", "MP4"]},
                    "reel": {"aspect_ratio": "9:16", "max_duration": "90s", "formats": ["MP4"]},
                    "igtv": {"aspect_ratio": "16:9 or 9:16", "max_duration": "60min", "formats": ["MP4"]}
                },
                "optimal_times": ["6-9 AM", "12-2 PM", "5-7 PM"],
                "hashtag_limit": 30,
                "caption_limit": 2200
            },
            
            DistributionPlatform.TIKTOK: {
                "content_formats": {
                    "video": {"aspect_ratio": "9:16", "max_duration": "10min", "formats": ["MP4", "MOV"]}
                },
                "optimal_times": ["6-10 AM", "7-9 PM"],
                "hashtag_limit": None,
                "caption_limit": 2200
            },
            
            DistributionPlatform.YOUTUBE: {
                "content_formats": {
                    "video": {"aspect_ratio": "16:9", "max_duration": "12h", "formats": ["MP4", "MOV", "AVI"]},
                    "shorts": {"aspect_ratio": "9:16", "max_duration": "60s", "formats": ["MP4", "MOV"]}
                },
                "optimal_times": ["2-4 PM", "8-11 PM"],
                "title_limit": 100,
                "description_limit": 5000
            },
            
            DistributionPlatform.SPOTIFY: {
                "content_formats": {
                    "audio": {"formats": ["WAV", "FLAC"], "sample_rate": "44.1kHz", "bit_depth": "16-bit"},
                    "canvas": {"aspect_ratio": "1:1", "duration": "3-8s", "formats": ["MP4"]}
                },
                "metadata_requirements": ["ISRC", "UPC", "publisher_info"],
                "playlist_categories": ["mood", "genre", "activity", "decade"]
            }
        }
    
    def generate_distribution_prompt(self, context: DistributionContext, custom_params: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate distribution prompt based on context"""        try:
            # Get distribution template
            content_templates = self.distribution_templates.get(f"{context.content_type}_distribution", {})
            strategy_template = content_templates.get(context.distribution_strategy)
            
            if not strategy_template:
                logger.warning(f"No distribution template found for {context.content_type} - {context.distribution_strategy}")
                return self._generate_fallback_distribution_prompt(context)
            
            # Customize prompt based on target platforms
            customized_prompt = self._customize_for_platforms(strategy_template, context.target_platforms)
            
            # Apply content adaptations
            if context.content_adaptations:
                customized_prompt = self._apply_content_adaptations(customized_prompt, context.content_adaptations)
            
            # Apply timeline constraints
            if context.timeline:
                customized_prompt = self._apply_timeline_constraints(customized_prompt, context.timeline)
            
            # Apply budget constraints
            if context.budget:
                customized_prompt = self._apply_budget_constraints(customized_prompt, context.budget)
            
            # Apply target audience specifications
            if context.target_audience:
                customized_prompt = self._apply_audience_targeting(customized_prompt, context.target_audience)
            
            # Apply custom parameters
            if custom_params:
                customized_prompt = self._apply_custom_distribution_params(customized_prompt, custom_params)
            
            # Add platform specifications
            customized_prompt = self._add_platform_specifications(customized_prompt, context.target_platforms)
            
            # Add metadata
            customized_prompt["generation_timestamp"] = datetime.utcnow().isoformat()
            customized_prompt["distribution_id"] = str(uuid.uuid4())
            customized_prompt["context_type"] = "multi_platform_distribution"
            
            return customized_prompt
            
        except Exception as e:
            logger.error(f"Error generating distribution prompt: {str(e)}")
            return self._generate_fallback_distribution_prompt(context)
    
    def _customize_for_platforms(self, template: Dict, platforms: List[DistributionPlatform]) -> Dict:
        """Customize template for specific platforms"""        customized = template.copy()
        
        platform_section = "\n\nTarget Platforms Configuration:\n"
        for platform in platforms:
            platform_section += f"- {platform.value.replace('_', ' ').title()}: Optimized\n"
        
        template_text = customized.get("template", "")
        customized["template"] = template_text + platform_section
        customized["target_platforms"] = [p.value for p in platforms]
        
        return customized
    
    def _apply_content_adaptations(self, prompt: Dict, adaptations: List[ContentAdaptation]) -> Dict:
        """Apply content adaptation requirements"""        modified_prompt = prompt.copy()
        
        adaptations_section = "\n\nContent Adaptation Requirements:\n"
        for adaptation in adaptations:
            if adaptation == ContentAdaptation.FORMAT_OPTIMIZATION:
                adaptations_section += "- Format optimization for each platform's technical requirements\n"
            elif adaptation == ContentAdaptation.PLATFORM_SPECIFIC:
                adaptations_section += "- Platform-specific content variations and features\n"
            elif adaptation == ContentAdaptation.AUDIENCE_TAILORED:
                adaptations_section += "- Audience-tailored messaging and presentation\n"
            elif adaptation == ContentAdaptation.REGIONAL_LOCALIZATION:
                adaptations_section += "- Regional localization and cultural adaptation\n"
        
        template = modified_prompt.get("template", "")
        modified_prompt["template"] = template + adaptations_section
        modified_prompt["content_adaptations"] = [a.value for a in adaptations]
        
        return modified_prompt
    
    def _apply_timeline_constraints(self, prompt: Dict, timeline: Dict) -> Dict:
        """Apply timeline constraints to distribution"""        modified_prompt = prompt.copy()
        
        timeline_section = "\n\nDistribution Timeline:\n"
        for timeline_key, timeline_value in timeline.items():
            timeline_section += f"- {timeline_key.replace('_', ' ').title()}: {timeline_value}\n"
        
        template = modified_prompt.get("template", "")
        modified_prompt["template"] = template + timeline_section
        modified_prompt["timeline_applied"] = timeline
        
        return modified_prompt
    
    def _apply_budget_constraints(self, prompt: Dict, budget: Dict) -> Dict:
        """Apply budget constraints to distribution"""        modified_prompt = prompt.copy()
        
        budget_section = "\n\nDistribution Budget:\n"
        for budget_key, budget_value in budget.items():
            budget_section += f"- {budget_key.replace('_', ' ').title()}: ${budget_value}\n"
        
        template = modified_prompt.get("template", "")
        modified_prompt["template"] = template + budget_section
        modified_prompt["budget_applied"] = budget
        
        return modified_prompt
    
    def _apply_audience_targeting(self, prompt: Dict, audience: Dict) -> Dict:
        """Apply audience targeting to distribution"""        modified_prompt = prompt.copy()
        
        audience_section = "\n\nTarget Audience Profile:\n"
        for audience_key, audience_value in audience.items():
            audience_section += f"- {audience_key.replace('_', ' ').title()}: {audience_value}\n"
        
        template = modified_prompt.get("template", "")
        modified_prompt["template"] = template + audience_section
        modified_prompt["audience_targeting_applied"] = audience
        
        return modified_prompt
    
    def _apply_custom_distribution_params(self, prompt: Dict, custom_params: Dict) -> Dict:
        """Apply custom distribution parameters"""        modified_prompt = prompt.copy()
        
        # Replace custom parameters in template
        template = modified_prompt.get("template", "")
        for param_key, param_value in custom_params.items():
            template = template.replace(f"{{{param_key}}}", str(param_value))
        
        modified_prompt["template"] = template
        modified_prompt["custom_distribution_parameters"] = custom_params
        
        return modified_prompt
    
    def _add_platform_specifications(self, prompt: Dict, platforms: List[DistributionPlatform]) -> Dict:
        """Add platform-specific technical specifications"""        modified_prompt = prompt.copy()
        
        specs_section = "\n\nPlatform Technical Specifications:\n"
        for platform in platforms:
            if platform in self.platform_specifications:
                specs = self.platform_specifications[platform]
                specs_section += f"\n{platform.value.replace('_', ' ').title()}:\n"
                
                if "content_formats" in specs:
                    specs_section += "  Content Formats:\n"
                    for format_name, format_specs in specs["content_formats"].items():
                        specs_section += f"    - {format_name}: {format_specs}\n"
                
                if "optimal_times" in specs:
                    specs_section += f"  Optimal Posting Times: {', '.join(specs['optimal_times'])}\n"
                
                if "hashtag_limit" in specs:
                    specs_section += f"  Hashtag Limit: {specs['hashtag_limit']}\n"
        
        template = modified_prompt.get("template", "")
        modified_prompt["template"] = template + specs_section
        modified_prompt["platform_specifications"] = {p.value: self.platform_specifications.get(p, {}) for p in platforms}
        
        return modified_prompt
    
    def _generate_fallback_distribution_prompt(self, context: DistributionContext) -> Dict[str, Any]:
        """Generate fallback distribution prompt"""        return {
            "id": "fallback_distribution",
            "template": f"""            Create {context.distribution_strategy.value} distribution strategy for {context.content_type}:
            
            Distribution Requirements:
            - Content type: {context.content_type}
            - Distribution strategy: {context.distribution_strategy.value}
            - Target platforms: {[p.value for p in context.target_platforms]}
            - Content adaptations: {[a.value for a in context.content_adaptations]}
            
            Please provide:
            1. Multi-platform distribution plan
            2. Content adaptation strategy
            3. Timeline and coordination
            4. Performance tracking system
            5. Platform-specific optimizations
            """,
            "variables": [],
            "quality_score": 70,
            "is_fallback": True
        }

# Multi-platform distribution registry
DISTRIBUTION_REGISTRY = {
    "music_simultaneous": MultiPlatformDistributionPrompts(),
    "music_tiered": MultiPlatformDistributionPrompts(),
    "video_viral": MultiPlatformDistributionPrompts(),
    "general_distribution": MultiPlatformDistributionPrompts()
}

def get_distribution_prompts() -> MultiPlatformDistributionPrompts:
    """Get the main distribution prompts instance"""    return MultiPlatformDistributionPrompts()

def create_distribution_context(
    content_type: str,
    target_platforms: List[str],
    distribution_strategy: str,
    content_adaptations: List[str],
    timeline: Optional[Dict] = None,
    budget: Optional[Dict] = None,
    target_audience: Optional[Dict] = None
) -> DistributionContext:
    """Create distribution context"""    return DistributionContext(
        content_type=content_type,
        target_platforms=[DistributionPlatform(p) for p in target_platforms],
        distribution_strategy=DistributionStrategy(distribution_strategy),
        content_adaptations=[ContentAdaptation(a) for a in content_adaptations],
        timeline=timeline or {},
        budget=budget or {},
        target_audience=target_audience or {}
    )
