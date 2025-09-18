"""
Photography Caption Template for AI-Powered Content Generation

Enterprise-grade photography caption prompt engineering template optimized for the Creator Economy.
Provides advanced prompt structures for generating high-quality photography captions across
multiple platforms, styles, and purposes with built-in optimization for engagement and monetization.

Author: AI Expert Team Lead by Fahed Mlaiel
Contact: contact@fahedmlaiel.fr | https://fahedmlaiel.fr
Copyright (c) 2024 Fahed Mlaiel. All rights reserved.
License: Proprietary - Contact for licensing terms
"""

from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass, field
import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PhotoStyle(Enum):
    """Photography style types"""
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"
    STREET = "street"
    FASHION = "fashion"
    LIFESTYLE = "lifestyle"
    TRAVEL = "travel"
    FOOD = "food"
    PRODUCT = "product"
    ARCHITECTURAL = "architectural"
    NATURE = "nature"
    DOCUMENTARY = "documentary"
    ARTISTIC = "artistic"
    COMMERCIAL = "commercial"
    EVENT = "event"
    MACRO = "macro"
    ABSTRACT = "abstract"

class CaptionTone(Enum):
    """Caption tone options"""
    INSPIRATIONAL = "inspirational"
    CONVERSATIONAL = "conversational"
    PROFESSIONAL = "professional"
    HUMOROUS = "humorous"
    POETIC = "poetic"
    EDUCATIONAL = "educational"
    STORYTELLING = "storytelling"
    MINIMALIST = "minimalist"
    EMOTIONAL = "emotional"
    PROMOTIONAL = "promotional"

class Platform(Enum):
    """Social media platforms"""
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    TIKTOK = "tiktok"
    THREADS = "threads"
    SNAPCHAT = "snapchat"
    TUMBLR = "tumblr"
    FLICKR = "flickr"

class CaptionLength(Enum):
    """Caption length options"""
    SHORT = "short"        # 1-50 characters
    MEDIUM = "medium"      # 50-150 characters
    LONG = "long"         # 150-500 characters
    EXTENDED = "extended"  # 500+ characters

@dataclass
class PhotographyCaptionPrompt:
    """Photography caption prompt configuration"""
    photo_style: PhotoStyle
    platform: Platform
    tone: CaptionTone
    length: CaptionLength
    photo_description: str
    caption_purpose: str = ""
    target_audience: str = ""
    brand_voice: str = ""
    hashtag_strategy: str = ""
    call_to_action: str = ""
    location: str = ""
    photographer_info: str = ""
    technical_details: str = ""
    story_context: str = ""
    emotional_message: str = ""
    seasonal_theme: str = ""
    trending_topics: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    mentions: List[str] = field(default_factory=list)
    monetization_focus: str = ""
    accessibility_description: str = ""

class PhotographyCaptionTemplate:
    """
    Advanced photography caption template for AI content generation
    
    Optimized for Creator Economy with platform-specific formatting, engagement optimization,
    and monetization strategies. Supports all major social media platforms.
    """
    
    def __init__(self):
        self.template_version = "1.0.0"
        self.creator_economy_features = True
        self.platform_optimization = True
        self.accessibility_support = True
        
        # Platform specifications and best practices
        self.platform_specs = {
            "instagram": {
                "max_length": 2200,
                "optimal_length": 150,
                "hashtag_limit": 30,
                "features": ["hashtags", "mentions", "location", "alt_text", "stories", "reels"],
                "engagement_features": ["like", "comment", "share", "save", "follow"]
            },
            "facebook": {
                "max_length": 8000,
                "optimal_length": 200,
                "hashtag_limit": 10,
                "features": ["hashtags", "mentions", "location", "tagging", "reactions"],
                "engagement_features": ["like", "comment", "share", "reaction", "follow"]
            },
            "twitter": {
                "max_length": 280,
                "optimal_length": 100,
                "hashtag_limit": 5,
                "features": ["hashtags", "mentions", "threads", "alt_text"],
                "engagement_features": ["like", "retweet", "reply", "quote_tweet", "follow"]
            },
            "linkedin": {
                "max_length": 3000,
                "optimal_length": 250,
                "hashtag_limit": 5,
                "features": ["hashtags", "mentions", "professional_focus"],
                "engagement_features": ["like", "comment", "share", "follow", "connect"]
            },
            "pinterest": {
                "max_length": 500,
                "optimal_length": 100,
                "hashtag_limit": 20,
                "features": ["hashtags", "rich_pins", "seo_focus"],
                "engagement_features": ["save", "comment", "follow", "try"]
            },
            "tiktok": {
                "max_length": 150,
                "optimal_length": 100,
                "hashtag_limit": 10,
                "features": ["hashtags", "mentions", "trending_sounds"],
                "engagement_features": ["like", "comment", "share", "follow", "duet"]
            }
        }
        
        # Style-specific caption approaches
        self.style_approaches = {
            PhotoStyle.PORTRAIT: "Focus on subject's story, emotions, and human connection",
            PhotoStyle.LANDSCAPE: "Emphasize natural beauty, location, and environmental awareness",
            PhotoStyle.STREET: "Capture authentic moments and urban life narratives",
            PhotoStyle.FASHION: "Highlight style, trends, and aesthetic inspiration",
            PhotoStyle.LIFESTYLE: "Share relatable moments and aspirational content",
            PhotoStyle.TRAVEL: "Inspire wanderlust and share cultural experiences",
            PhotoStyle.FOOD: "Make viewers crave the dish and share cooking/dining experiences",
            PhotoStyle.PRODUCT: "Highlight features, benefits, and usage scenarios",
            PhotoStyle.NATURE: "Connect with environmental themes and natural wonder",
            PhotoStyle.DOCUMENTARY: "Tell compelling stories and share important messages"
        }
        
    def generate_prompt(self, config: PhotographyCaptionPrompt) -> Dict[str, Any]:
        """
        Generate optimized photography caption prompt
        
        Args:
            config: Photography caption configuration
            
        Returns:
            Dictionary containing optimized prompt and metadata
        """
        try:
            # Get platform specifications
            platform_spec = self.platform_specs.get(config.platform.value, {})
            
            # Build comprehensive prompt
            prompt_components = {
                "system_prompt": self._build_system_prompt(config),
                "user_prompt": self._build_user_prompt(config, platform_spec),
                "caption_structure": self._build_caption_structure(config, platform_spec),
                "engagement_optimization": self._build_engagement_optimization(config),
                "platform_optimization": self._build_platform_optimization(config, platform_spec),
                "hashtag_strategy": self._build_hashtag_strategy(config, platform_spec),
                "accessibility_guidance": self._build_accessibility_guidance(config),
                "monetization_integration": self._build_monetization_integration(config)
            }
            
            # Combine into final prompt
            final_prompt = self._combine_prompt_components(prompt_components)
            
            # Generate metadata
            metadata = self._generate_metadata(config)
            
            logger.info(f"Generated photography caption prompt for {config.photo_style.value} on {config.platform.value}")
            
            return {
                "prompt": final_prompt,
                "metadata": metadata,
                "config": config,
                "optimization_score": self._calculate_optimization_score(config),
                "engagement_potential": self._estimate_engagement_potential(config),
                "viral_potential": self._estimate_viral_potential(config),
                "platform_compliance": self._check_platform_compliance(config)
            }
            
        except Exception as e:
            logger.error(f"Error generating photography caption prompt: {str(e)}")
            raise
    
    def _build_system_prompt(self, config: PhotographyCaptionPrompt) -> str:
        """Build system prompt for caption generation"""
        style_approach = self.style_approaches.get(config.photo_style, "Create engaging visual storytelling")
        
        return f"""You are an expert social media content creator and photography caption writer specializing in {config.photo_style.value} photography for the Creator Economy.

Your expertise includes:
- Professional social media copywriting and engagement optimization
- Photography storytelling and visual narrative techniques
- Platform-specific content optimization and algorithm understanding
- Creator Economy monetization and audience growth strategies
- Accessibility best practices and inclusive content creation
- Hashtag research and social media SEO optimization

Creating: {config.platform.value.title()} caption
Style: {config.photo_style.value} photography
Tone: {config.tone.value}
Length: {config.length.value}
Target Audience: {config.target_audience or 'Photography and lifestyle enthusiasts'}

Style Approach: {style_approach}

Focus on:
- Maximum engagement and algorithmic reach
- Authentic storytelling that connects with viewers
- Strategic monetization integration
- Platform-specific optimization and features
- Community building and audience development
- Creator brand building and recognition"""

    def _build_user_prompt(self, config: PhotographyCaptionPrompt, platform_spec: Dict) -> str:
        """Build user prompt with photo and caption specifications"""
        max_length = platform_spec.get('max_length', 'platform standard')
        optimal_length = platform_spec.get('optimal_length', 'optimal for engagement')
        
        location_info = f"\nLocation: {config.location}" if config.location else ""
        photographer_info = f"\nPhotographer: {config.photographer_info}" if config.photographer_info else ""
        technical_info = f"\nTechnical Details: {config.technical_details}" if config.technical_details else ""
        story_info = f"\nStory Context: {config.story_context}" if config.story_context else ""
        emotional_info = f"\nEmotional Message: {config.emotional_message}" if config.emotional_message else ""
        seasonal_info = f"\nSeasonal Theme: {config.seasonal_theme}" if config.seasonal_theme else ""
        brand_info = f"\nBrand Voice: {config.brand_voice}" if config.brand_voice else ""
        
        return f"""Photo Description: {config.photo_description}
Platform: {config.platform.value.title()}
Caption Purpose: {config.caption_purpose or 'Engagement and community building'}
Target Length: {config.length.value} (~{optimal_length} characters, max {max_length}){location_info}{photographer_info}{technical_info}{story_info}{emotional_info}{seasonal_info}{brand_info}

Caption Requirements:
- Write in {config.tone.value} tone that resonates with {config.target_audience or 'target audience'}
- Follow {config.photo_style.value} photography storytelling conventions
- Include strategic call-to-action: {config.call_to_action or 'Encourage engagement and following'}
- Optimize for {config.platform.value} algorithm and user behavior
- Include relevant hashtags and mentions strategically
- Ensure accessibility with descriptive language

Creator Economy Optimization:
- Build photographer/creator brand recognition and authority
- Include subtle monetization elements without being pushy
- Create shareable and quotable content moments
- Encourage community engagement and conversation
- Design for cross-platform content repurposing
- Build long-term audience loyalty and connection"""

    def _build_caption_structure(self, config: PhotographyCaptionPrompt, platform_spec: Dict) -> str:
        """Build caption structure based on length and platform"""
        if config.length == CaptionLength.SHORT:
            structure = """
CAPTION STRUCTURE (Short):
1. Hook/Opening line (compelling and attention-grabbing)
2. Core message or story (concise and impactful)
3. Call-to-action (direct and engaging)
4. Strategic hashtags (relevant and discoverable)"""
        
        elif config.length == CaptionLength.MEDIUM:
            structure = """
CAPTION STRUCTURE (Medium):
1. Hook/Opening question or statement
2. Story development or context setting
3. Personal insight or lesson learned
4. Audience connection and relatability
5. Call-to-action and engagement prompt
6. Hashtags and mentions"""
        
        elif config.length == CaptionLength.LONG:
            structure = """
CAPTION STRUCTURE (Long):
1. Compelling hook that stops the scroll
2. Story setup and context introduction
3. Detailed narrative or experience sharing
4. Personal reflection and insights
5. Broader message or life lesson
6. Community question or discussion starter
7. Clear call-to-action
8. Strategic hashtags and mentions"""
        
        else:  # EXTENDED
            structure = """
CAPTION STRUCTURE (Extended):
1. Attention-grabbing opening hook
2. Detailed story introduction and setting
3. Rich narrative with sensory details
4. Character development (if applicable)
5. Conflict or challenge presentation
6. Resolution and personal growth
7. Universal message and life lesson
8. Community engagement and discussion
9. Multiple calls-to-action
10. Comprehensive hashtag strategy"""
        
        return f"""{structure}

Platform-Specific Considerations:
- Character limit: {platform_spec.get('max_length', 'Standard')}
- Optimal length: ~{platform_spec.get('optimal_length', 'Platform recommended')} characters
- Hashtag limit: {platform_spec.get('hashtag_limit', 'Platform standard')} hashtags maximum
- Features to leverage: {', '.join(platform_spec.get('features', []))}
- Engagement actions: {', '.join(platform_spec.get('engagement_features', []))}"""

    def _build_engagement_optimization(self, config: PhotographyCaptionPrompt) -> str:
        """Build engagement optimization strategies"""
        trending_topics = f"Trending topics to incorporate: {', '.join(config.trending_topics)}" if config.trending_topics else ""
        keywords = f"Keywords to include: {', '.join(config.keywords)}" if config.keywords else ""
        mentions = f"Accounts to mention: {', '.join(config.mentions)}" if config.mentions else ""
        
        return f"""
ENGAGEMENT OPTIMIZATION:

Psychological Triggers:
- Use curiosity gaps and open-ended questions
- Include relatable experiences and emotions
- Create FOMO (fear of missing out) elements
- Use storytelling to build emotional connection
- Include surprise or unexpected elements

Social Media Psychology:
- Write captions that encourage comments and saves
- Ask specific questions that prompt responses
- Include controversial or discussion-worthy points (appropriately)
- Use interactive elements like polls or challenges
- Create shareable moments and quotable content

Platform Algorithm Optimization:
- Front-load important information in first 125 characters
- Use line breaks and emojis for visual appeal and readability
- Include keywords naturally for discoverability
- Encourage meaningful engagement (comments > likes)
- Design for completion rate (full caption reading)

Community Building:
{trending_topics}
{keywords}
{mentions}
- Foster genuine connections and conversations
- Show vulnerability and authenticity
- Celebrate community members and user-generated content
- Create ongoing series or themes for consistent engagement
- Respond to comments and build relationships actively"""

    def _build_platform_optimization(self, config: PhotographyCaptionPrompt, platform_spec: Dict) -> str:
        """Build platform-specific optimization"""
        platform = config.platform.value
        features = platform_spec.get('features', [])
        
        if platform == "instagram":
            optimization = """
INSTAGRAM OPTIMIZATION:
- Use line breaks for visual appeal and readability
- Include emojis strategically for personality and visual interest
- Front-load key information for preview text
- Use Instagram-specific features (Stories, Reels integration)
- Include location tags for local discovery
- Create caption that works for both feed and Stories sharing"""
            
        elif platform == "twitter":
            optimization = """
TWITTER OPTIMIZATION:
- Make every character count within 280 limit
- Use threading for longer stories
- Include trending hashtags strategically
- Create tweetable moments and quotable content
- Use alt text for accessibility
- Time posting for maximum engagement"""
            
        elif platform == "linkedin":
            optimization = """
LINKEDIN OPTIMIZATION:
- Maintain professional tone while being personable
- Include industry insights and thought leadership
- Use professional hashtags and connections
- Share lessons learned and business insights
- Tag relevant industry leaders appropriately
- Focus on value delivery and professional growth"""
            
        elif platform == "tiktok":
            optimization = """
TIKTOK OPTIMIZATION:
- Keep captions concise and punchy
- Include trending hashtags and challenges
- Use TikTok-specific language and culture
- Create captions that work with video content
- Include calls for video responses and duets
- Focus on viral potential and shareability"""
            
        else:
            optimization = f"""
{platform.upper()} OPTIMIZATION:
- Follow platform-specific best practices and culture
- Use appropriate hashtags and tagging features
- Optimize for platform's unique algorithm and user behavior
- Leverage platform-specific features: {', '.join(features)}
- Create content that fits platform consumption patterns"""
        
        return optimization

    def _build_hashtag_strategy(self, config: PhotographyCaptionPrompt, platform_spec: Dict) -> str:
        """Build hashtag strategy"""
        hashtag_limit = platform_spec.get('hashtag_limit', 10)
        strategy = config.hashtag_strategy or "Mix of popular, niche, and branded hashtags"
        
        return f"""
HASHTAG STRATEGY:

Strategy: {strategy}
Platform Limit: {hashtag_limit} hashtags maximum

Hashtag Mix:
- Popular hashtags (100K+ posts): 2-3 for reach
- Medium hashtags (10K-100K posts): 3-4 for engagement
- Niche hashtags (1K-10K posts): 2-3 for targeted audience
- Branded/personal hashtags: 1-2 for brand building

Photography-Specific Hashtags:
- Style-specific: #{config.photo_style.value}photography
- Technical hashtags related to camera/technique
- Location-based hashtags if applicable
- Community hashtags for photographer networks
- Trending photography hashtags

Engagement Hashtags:
- Platform-specific trending tags
- Seasonal and event-based hashtags
- Industry and niche community tags
- Call-to-action hashtags
- User-generated content campaign tags

Research and Optimization:
- Use platform analytics to identify top-performing hashtags
- Rotate hashtags to avoid algorithm penalties
- Create unique branded hashtags for campaigns
- Monitor competitor hashtag strategies
- Track hashtag performance and adjust strategy"""

    def _build_accessibility_guidance(self, config: PhotographyCaptionPrompt) -> str:
        """Build accessibility and inclusion guidance"""
        accessibility_desc = config.accessibility_description or "Detailed visual description to be included"
        
        return f"""
ACCESSIBILITY AND INCLUSION:

Visual Description:
{accessibility_desc}
- Describe key visual elements, colors, and composition
- Include information about people, objects, and setting
- Mention facial expressions, body language, and mood
- Describe text or graphics visible in the image
- Use inclusive language that welcomes all audiences

Platform Accessibility Features:
- Instagram: Include detailed alt text for screen readers
- Twitter: Use alt text feature for image descriptions
- Facebook: Include comprehensive image descriptions
- LinkedIn: Use professional inclusive language
- All platforms: Avoid ableist language and assumptions

Inclusive Content Creation:
- Use person-first language when describing people
- Avoid assumptions about audience abilities or circumstances
- Include diverse perspectives and experiences
- Use clear, simple language that's easy to understand
- Consider color contrast and readability for visual elements

Universal Design:
- Create content that's accessible to users with disabilities
- Use emoji thoughtfully (screen readers read them aloud)
- Include content warnings for sensitive material
- Provide context for cultural references or slang
- Design captions that work for all users regardless of ability"""

    def _build_monetization_integration(self, config: PhotographyCaptionPrompt) -> str:
        """Build monetization integration strategies"""
        monetization = config.monetization_focus or "Organic audience growth and engagement"
        
        return f"""
MONETIZATION INTEGRATION:

Focus: {monetization}

Organic Monetization:
- Build photographer brand recognition and authority
- Showcase technical skills and creative vision
- Include subtle portfolio promotion and booking information
- Create content that demonstrates expertise and value
- Build email list through valuable content offers

Product Integration:
- Naturally mention camera gear, editing software, or equipment
- Include affiliate links in bio or comments appropriately
- Showcase photography services and offerings
- Promote workshops, courses, or educational content
- Feature client work and testimonials organically

Platform Monetization:
- Optimize for platform creator funds and revenue sharing
- Create content eligible for brand partnerships
- Build audience for sponsored content opportunities
- Use platform shopping features where available
- Develop content for premium subscriptions or exclusive access

Long-term Value:
- Establish thought leadership in photography niche
- Build community that translates to business opportunities
- Create content that drives traffic to portfolio or website
- Develop relationships that lead to collaboration opportunities
- Build reputation that attracts high-value clients and partnerships

Ethical Considerations:
- Clearly disclose sponsored content and partnerships
- Maintain authenticity while including promotional elements
- Balance promotional content with value-driven posts
- Respect audience trust and platform guidelines
- Provide genuine value regardless of monetization strategy"""

    def _combine_prompt_components(self, components: Dict[str, str]) -> str:
        """Combine all prompt components into final prompt"""
        return f"""{components['system_prompt']}

{components['user_prompt']}

{components['caption_structure']}

{components['engagement_optimization']}

{components['platform_optimization']}

{components['hashtag_strategy']}

{components['accessibility_guidance']}

{components['monetization_integration']}

Now create the complete photography caption following all these guidelines. Include the main caption text, hashtag recommendations, and any additional platform-specific elements."""

    def _generate_metadata(self, config: PhotographyCaptionPrompt) -> Dict[str, Any]:
        """Generate metadata for the caption"""
        return {
            "template_version": self.template_version,
            "photo_style": config.photo_style.value,
            "platform": config.platform.value,
            "tone": config.tone.value,
            "length": config.length.value,
            "target_audience": config.target_audience,
            "has_location": bool(config.location),
            "has_technical_details": bool(config.technical_details),
            "has_story_context": bool(config.story_context),
            "trending_topics_count": len(config.trending_topics),
            "keywords_count": len(config.keywords),
            "mentions_count": len(config.mentions),
            "has_cta": bool(config.call_to_action),
            "monetization_enabled": bool(config.monetization_focus),
            "accessibility_optimized": bool(config.accessibility_description),
            "creation_timestamp": datetime.now().isoformat(),
            "creator_economy_optimized": True
        }

    def _calculate_optimization_score(self, config: PhotographyCaptionPrompt) -> float:
        """Calculate optimization score based on configuration"""
        score = 0.5  # Base score
        
        # Add points for configuration completeness
        if config.target_audience:
            score += 0.1
        if config.call_to_action:
            score += 0.1
        if config.hashtag_strategy:
            score += 0.1
        if config.keywords:
            score += 0.05
        if config.trending_topics:
            score += 0.05
        if config.story_context:
            score += 0.05
        if config.accessibility_description:
            score += 0.1
        if config.monetization_focus:
            score += 0.05
        
        return min(score, 1.0)

    def _estimate_engagement_potential(self, config: PhotographyCaptionPrompt) -> str:
        """Estimate engagement potential"""
        score = self._calculate_optimization_score(config)
        
        # Boost for engagement-friendly elements
        if config.trending_topics:
            score += 0.05
        if config.tone in [CaptionTone.CONVERSATIONAL, CaptionTone.HUMOROUS, CaptionTone.STORYTELLING]:
            score += 0.05
            
        if score >= 0.8:
            return "High"
        elif score >= 0.6:
            return "Medium-High"
        elif score >= 0.4:
            return "Medium"
        else:
            return "Low-Medium"

    def _estimate_viral_potential(self, config: PhotographyCaptionPrompt) -> str:
        """Estimate viral potential"""
        viral_score = 0.3  # Base viral potential
        
        # Boost for viral-friendly elements
        if config.trending_topics:
            viral_score += 0.2
        if config.tone in [CaptionTone.HUMOROUS, CaptionTone.INSPIRATIONAL]:
            viral_score += 0.2
        if config.platform in [Platform.TIKTOK, Platform.INSTAGRAM, Platform.TWITTER]:
            viral_score += 0.15
        if config.photo_style in [PhotoStyle.LIFESTYLE, PhotoStyle.TRAVEL, PhotoStyle.FASHION]:
            viral_score += 0.1
        if config.length in [CaptionLength.SHORT, CaptionLength.MEDIUM]:
            viral_score += 0.05
            
        if viral_score >= 0.7:
            return "High"
        elif viral_score >= 0.5:
            return "Medium-High"
        elif viral_score >= 0.3:
            return "Medium"
        else:
            return "Low"

    def _check_platform_compliance(self, config: PhotographyCaptionPrompt) -> Dict[str, Any]:
        """Check platform compliance and requirements"""
        platform_spec = self.platform_specs.get(config.platform.value, {})
        
        return {
            "platform": config.platform.value,
            "max_length": platform_spec.get('max_length', 'Unknown'),
            "hashtag_limit": platform_spec.get('hashtag_limit', 'Unknown'),
            "features_available": platform_spec.get('features', []),
            "engagement_types": platform_spec.get('engagement_features', []),
            "compliant": True,  # Assume compliant unless specific issues found
            "recommendations": f"Optimize for {platform_spec.get('optimal_length', 'platform standard')} character count"
        }

# Example usage and testing
if __name__ == "__main__":
    # Example configuration
    config = PhotographyCaptionPrompt(
        photo_style=PhotoStyle.TRAVEL,
        platform=Platform.INSTAGRAM,
        tone=CaptionTone.INSPIRATIONAL,
        length=CaptionLength.LONG,
        photo_description="Sunset over the Swiss Alps with a lone hiker silhouetted against the golden sky",
        caption_purpose="Inspire travel and showcase photography skills",
        target_audience="travel enthusiasts and adventure seekers",
        brand_voice="Inspirational and authentic with focus on sustainable travel",
        hashtag_strategy="Mix of travel, photography, and sustainable tourism hashtags",
        call_to_action="Share your favorite mountain sunset memory in the comments",
        location="Swiss Alps, Switzerland",
        photographer_info="Professional travel photographer with 10+ years experience",
        technical_details="Shot with Sony A7R IV, 24-70mm lens at f/8, ISO 100",
        story_context="Three-day solo hiking trip documenting sustainable mountain tourism",
        emotional_message="Finding peace and perspective in nature's grandeur",
        seasonal_theme="Summer hiking and golden hour photography",
        trending_topics=["sustainable travel", "solo hiking", "mountain photography"],
        keywords=["Swiss Alps", "sunset photography", "hiking", "travel inspiration"],
        monetization_focus="Build photography portfolio and attract travel photography clients",
        accessibility_description="Golden sunset illuminates snow-capped mountain peaks while a small human figure stands on rocky outcrop in silhouette"
    )
    
    # Generate prompt
    template = PhotographyCaptionTemplate()
    result = template.generate_prompt(config)
    
    print("=== PHOTOGRAPHY CAPTION TEMPLATE EXAMPLE ===")
    print(f"Optimization Score: {result['optimization_score']:.2f}")
    print(f"Engagement Potential: {result['engagement_potential']}")
    print(f"Viral Potential: {result['viral_potential']}")
    print(f"Platform Compliance: {result['platform_compliance']}")
    print("\n" + "="*50)
    print(result['prompt'])