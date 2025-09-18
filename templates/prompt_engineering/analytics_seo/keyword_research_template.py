"""
Keyword Research Template for AI-Powered Content Generation

Enterprise-grade keyword research prompt engineering template optimized for the Creator Economy.
Provides advanced prompt structures for comprehensive keyword research across
multiple industries, search intents, and competition levels with built-in optimization for discovery and monetization.

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

class KeywordType(Enum):
    """Keyword research types"""
    SEED_KEYWORDS = "seed_keywords"
    LONG_TAIL = "long_tail"
    QUESTION_BASED = "question_based"
    COMPETITOR = "competitor"
    BRANDED = "branded"
    LOCAL = "local"
    SEASONAL = "seasonal"
    TRENDING = "trending"
    PRODUCT = "product"
    INFORMATIONAL = "informational"
    TRANSACTIONAL = "transactional"
    NAVIGATIONAL = "navigational"

class SearchVolume(Enum):
    """Search volume ranges"""
    LOW = "low"          # 0-1000
    MEDIUM = "medium"    # 1000-10000
    HIGH = "high"        # 10000-100000
    VERY_HIGH = "very_high"  # 100000+

class KeywordDifficulty(Enum):
    """Keyword difficulty levels"""
    EASY = "easy"        # 0-30
    MEDIUM = "medium"    # 30-50
    HARD = "hard"        # 50-70
    VERY_HARD = "very_hard"  # 70+

class ContentFormat(Enum):
    """Content format for keyword targeting"""
    BLOG_POST = "blog_post"
    VIDEO = "video"
    PODCAST = "podcast"
    SOCIAL_MEDIA = "social_media"
    LANDING_PAGE = "landing_page"
    PRODUCT_PAGE = "product_page"
    CATEGORY_PAGE = "category_page"
    FAQ = "faq"
    GUIDE = "guide"
    TOOL = "tool"

@dataclass
class KeywordResearchPrompt:
    """Keyword research prompt configuration"""
    primary_topic: str
    industry: str
    business_type: str = ""
    target_audience: str = ""
    content_goals: List[str] = field(default_factory=list)
    keyword_types: List[KeywordType] = field(default_factory=list)
    target_volume: SearchVolume = SearchVolume.MEDIUM
    max_difficulty: KeywordDifficulty = KeywordDifficulty.MEDIUM
    content_formats: List[ContentFormat] = field(default_factory=list)
    geographic_focus: str = ""
    language: str = "English"
    competitor_domains: List[str] = field(default_factory=list)
    existing_keywords: List[str] = field(default_factory=list)
    brand_keywords: List[str] = field(default_factory=list)
    seasonal_considerations: str = ""
    user_personas: List[str] = field(default_factory=list)
    buyer_journey_stage: str = ""
    monetization_goals: List[str] = field(default_factory=list)
    content_gaps: List[str] = field(default_factory=list)
    trending_topics: List[str] = field(default_factory=list)
    voice_search_focus: bool = False
    mobile_search_priority: bool = True
    local_search_intent: bool = False
    feature_snippet_targets: List[str] = field(default_factory=list)

class KeywordResearchTemplate:
    """
    Advanced keyword research template for AI content generation
    
    Optimized for Creator Economy with comprehensive keyword discovery, competitive analysis,
    and strategic content planning. Supports all major search engines and content formats.
    """
    
    def __init__(self):
        self.template_version = "1.0.0"
        self.creator_economy_features = True
        self.competitive_analysis = True
        self.trend_analysis = True
        
        # Search volume and difficulty matrices
        self.volume_ranges = {
            SearchVolume.LOW: {"min": 0, "max": 1000, "description": "Niche, low competition"},
            SearchVolume.MEDIUM: {"min": 1000, "max": 10000, "description": "Moderate traffic potential"},
            SearchVolume.HIGH: {"min": 10000, "max": 100000, "description": "High traffic potential"},
            SearchVolume.VERY_HIGH: {"min": 100000, "max": float('inf'), "description": "Massive traffic potential"}
        }
        
        self.difficulty_ranges = {
            KeywordDifficulty.EASY: {"score": "0-30", "description": "Quick wins, low authority needed"},
            KeywordDifficulty.MEDIUM: {"score": "30-50", "description": "Moderate effort, good content needed"},
            KeywordDifficulty.HARD: {"score": "50-70", "description": "High effort, strong authority needed"},
            KeywordDifficulty.VERY_HARD: {"score": "70+", "description": "Very difficult, top-tier content needed"}
        }
        
        # Content format keyword strategies
        self.format_strategies = {
            ContentFormat.BLOG_POST: {
                "keyword_focus": "Informational, how-to, comparison keywords",
                "content_length": "1500-3000 words",
                "keyword_density": "1-2%",
                "structure": "H1 with primary keyword, H2s with secondary keywords"
            },
            ContentFormat.VIDEO: {
                "keyword_focus": "Tutorial, demonstration, entertainment keywords",
                "content_length": "5-15 minutes",
                "keyword_density": "Natural integration in title and description",
                "structure": "Title, description, tags, transcript optimization"
            },
            ContentFormat.SOCIAL_MEDIA: {
                "keyword_focus": "Trending, hashtag-based, viral keywords",
                "content_length": "50-280 characters",
                "keyword_density": "Hashtag integration",
                "structure": "Hashtags, captions, bio optimization"
            }
        }
        
        # Industry-specific keyword modifiers
        self.industry_modifiers = {
            "technology": ["software", "app", "digital", "online", "AI", "automation"],
            "health": ["wellness", "fitness", "nutrition", "medical", "healthy", "treatment"],
            "finance": ["money", "investment", "savings", "budget", "financial", "wealth"],
            "education": ["learning", "course", "training", "skill", "knowledge", "study"],
            "ecommerce": ["buy", "shop", "product", "review", "deal", "discount"],
            "entertainment": ["fun", "game", "movie", "music", "show", "celebrity"]
        }
        
    def generate_prompt(self, config: KeywordResearchPrompt) -> Dict[str, Any]:
        """
        Generate comprehensive keyword research prompt
        
        Args:
            config: Keyword research configuration
            
        Returns:
            Dictionary containing optimized prompt and metadata
        """
        try:
            # Build comprehensive prompt
            prompt_components = {
                "system_prompt": self._build_system_prompt(config),
                "user_prompt": self._build_user_prompt(config),
                "keyword_discovery": self._build_keyword_discovery(config),
                "competitive_analysis": self._build_competitive_analysis(config),
                "search_intent_analysis": self._build_search_intent_analysis(config),
                "opportunity_identification": self._build_opportunity_identification(config),
                "content_strategy": self._build_content_strategy(config),
                "keyword_prioritization": self._build_keyword_prioritization(config),
                "trend_analysis": self._build_trend_analysis(config),
                "measurement_strategy": self._build_measurement_strategy(config)
            }
            
            # Combine into final prompt
            final_prompt = self._combine_prompt_components(prompt_components)
            
            # Generate metadata
            metadata = self._generate_metadata(config)
            
            logger.info(f"Generated keyword research prompt for {config.primary_topic} in {config.industry}")
            
            return {
                "prompt": final_prompt,
                "metadata": metadata,
                "config": config,
                "research_scope": self._calculate_research_scope(config),
                "opportunity_score": self._calculate_opportunity_score(config),
                "competition_level": self._assess_competition_level(config),
                "keyword_categories": self._generate_keyword_categories(config)
            }
            
        except Exception as e:
            logger.error(f"Error generating keyword research prompt: {str(e)}")
            raise
    
    def _build_system_prompt(self, config: KeywordResearchPrompt) -> str:
        """Build system prompt for keyword research"""
        volume_desc = self.volume_ranges[config.target_volume]["description"]
        difficulty_desc = self.difficulty_ranges[config.max_difficulty]["description"]
        
        return f"""You are an expert SEO keyword researcher and content strategist with deep expertise in Creator Economy optimization and search market analysis.

Your expertise includes:
- Advanced keyword research methodologies and tools
- Search intent analysis and user behavior patterns
- Competitive keyword analysis and gap identification
- Creator Economy keyword opportunities and monetization
- Trend analysis and seasonal keyword planning
- Technical SEO and search algorithm understanding

Research Focus: {config.primary_topic}
Industry: {config.industry}
Target Volume: {config.target_volume.value} ({volume_desc})
Max Difficulty: {config.max_difficulty.value} ({difficulty_desc})
Geographic Focus: {config.geographic_focus or 'Global'}
Target Audience: {config.target_audience or 'General audience'}

Focus on:
- Comprehensive keyword discovery across all search intents
- Competitive analysis and opportunity identification
- Creator Economy monetization keyword opportunities
- Long-tail and question-based keyword research
- Trend analysis and seasonal keyword planning
- Content gap analysis and strategic recommendations"""

    def _build_user_prompt(self, config: KeywordResearchPrompt) -> str:
        """Build user prompt with research specifications"""
        keyword_types = [kt.value for kt in config.keyword_types] if config.keyword_types else ["All types"]
        content_formats = [cf.value for cf in config.content_formats] if config.content_formats else ["All formats"]
        content_goals = config.content_goals or ["Traffic growth", "Audience engagement"]
        monetization_goals = config.monetization_goals or ["General business growth"]
        
        competitors_info = f"\nCompetitor Domains: {', '.join(config.competitor_domains)}" if config.competitor_domains else ""
        existing_keywords_info = f"\nExisting Keywords: {', '.join(config.existing_keywords)}" if config.existing_keywords else ""
        brand_keywords_info = f"\nBrand Keywords: {', '.join(config.brand_keywords)}" if config.brand_keywords else ""
        personas_info = f"\nUser Personas: {', '.join(config.user_personas)}" if config.user_personas else ""
        seasonal_info = f"\nSeasonal Considerations: {config.seasonal_considerations}" if config.seasonal_considerations else ""
        trending_info = f"\nTrending Topics: {', '.join(config.trending_topics)}" if config.trending_topics else ""
        
        return f"""Primary Topic: {config.primary_topic}
Industry: {config.industry}
Business Type: {config.business_type or 'Creator economy business'}
Target Audience: {config.target_audience or 'General audience'}

Research Parameters:
- Keyword Types: {', '.join(keyword_types)}
- Target Volume: {config.target_volume.value} ({self.volume_ranges[config.target_volume]['min']}-{self.volume_ranges[config.target_volume]['max']} searches/month)
- Max Difficulty: {config.max_difficulty.value} ({self.difficulty_ranges[config.max_difficulty]['score']})
- Content Formats: {', '.join(content_formats)}
- Geographic Focus: {config.geographic_focus or 'Global'}
- Language: {config.language}{competitors_info}{existing_keywords_info}{brand_keywords_info}{personas_info}{seasonal_info}{trending_info}

Content Goals: {', '.join(content_goals)}
Monetization Goals: {', '.join(monetization_goals)}
Buyer Journey Stage: {config.buyer_journey_stage or 'All stages'}

Special Requirements:
- Voice Search Focus: {config.voice_search_focus}
- Mobile Search Priority: {config.mobile_search_priority}
- Local Search Intent: {config.local_search_intent}
- Featured Snippet Targets: {', '.join(config.feature_snippet_targets) if config.feature_snippet_targets else 'Identify opportunities'}

Creator Economy Optimization:
- Identify keywords for content monetization opportunities
- Find gaps in competitor keyword strategies
- Discover trending topics for viral content potential
- Analyze keywords for different content formats and platforms
- Prioritize keywords for Creator Economy business models
- Include seasonal and trending keyword opportunities"""

    def _build_keyword_discovery(self, config: KeywordResearchPrompt) -> str:
        """Build keyword discovery methodology"""
        industry_modifiers = self.industry_modifiers.get(config.industry.lower(), ["industry-specific", "professional", "expert"])
        
        return f"""
KEYWORD DISCOVERY METHODOLOGY:

Seed Keyword Expansion:
- Start with primary topic: "{config.primary_topic}"
- Use industry modifiers: {', '.join(industry_modifiers)}
- Include synonym variations and related terms
- Explore different word orders and phrase structures
- Consider abbreviations and alternative spellings

Long-tail Keyword Research:
- 3-5 word phrases with lower competition
- Specific problem-solving keywords
- How-to and tutorial-based queries
- Comparison and versus keywords
- Location-based variations (if applicable)

Question-based Keywords:
- Who, what, when, where, why, how questions
- People Also Ask (PAA) expansion
- Answer-the-public style questions
- FAQ and common user queries
- Voice search conversational phrases

Competitor Keyword Mining:
- Analyze top-ranking competitor content
- Identify gaps in competitor keyword coverage
- Find keywords competitors rank for but you don't
- Discover successful keyword clusters
- Analyze competitor content gaps and opportunities

Trending and Seasonal Keywords:
- Google Trends analysis for topic variations
- Seasonal search pattern identification
- Emerging trend keywords and topics
- News and current event-related terms
- Social media trending hashtags and topics

Content Format Keywords:
- Video-specific keywords (tutorial, how-to, demo)
- Blog post informational keywords
- Social media hashtag research
- Podcast episode and audio content keywords
- Tool and resource-based keywords

Local and Geographic Keywords:
- City, state, and region-specific terms
- "Near me" and location-based modifiers
- Local business and service keywords
- Regional slang and terminology
- Geographic landmark and area references"""

    def _build_competitive_analysis(self, config: KeywordResearchPrompt) -> str:
        """Build competitive analysis strategy"""
        competitors = config.competitor_domains or ["Top-ranking websites in your industry"]
        
        return f"""
COMPETITIVE KEYWORD ANALYSIS:

Target Competitors: {', '.join(competitors)}

Competitor Content Analysis:
- Identify top-performing competitor pages
- Analyze competitor keyword targeting strategies
- Review competitor content depth and quality
- Identify competitor content gaps and weaknesses
- Study competitor internal linking and keyword clustering

Keyword Gap Analysis:
- Find keywords competitors rank for that you don't
- Identify underutilized keywords with good potential
- Discover competitor keyword cannibalization issues
- Find keywords with declining competitor performance
- Identify seasonal opportunities competitors miss

SERP Analysis:
- Analyze top 10 results for target keywords
- Identify SERP features (featured snippets, PAA, etc.)
- Study competitor title tag and meta description strategies
- Analyze competitor content length and structure
- Identify opportunities for better content creation

Competitor Weakness Identification:
- Find competitors with thin or outdated content
- Identify technical SEO issues on competitor sites
- Discover competitor keywords with declining rankings
- Find gaps in competitor content freshness
- Identify opportunities for content differentiation

Market Share Analysis:
- Estimate competitor organic traffic share
- Identify industry keyword leaders
- Find emerging competitors and rising rankings
- Analyze seasonal competitor performance
- Identify market consolidation opportunities

Competitive Advantage Opportunities:
- Create more comprehensive content than competitors
- Target competitor keyword gaps with high potential
- Develop unique angles on popular topics
- Build stronger topical authority than competitors
- Leverage better user experience and site performance"""

    def _build_search_intent_analysis(self, config: KeywordResearchPrompt) -> str:
        """Build search intent analysis"""
        return f"""
SEARCH INTENT ANALYSIS:

Informational Intent Keywords:
- How-to and tutorial keywords
- Definition and explanation searches
- Research and learning-focused queries
- Problem identification keywords
- Educational content opportunities

Navigational Intent Keywords:
- Brand name and company searches
- Specific website or page searches
- Product name and model searches
- Service provider location searches
- Direct navigation queries

Transactional Intent Keywords:
- Buy, purchase, and order keywords
- Product and service comparison searches
- Review and recommendation queries
- Price and deal-focused searches
- Action-oriented commercial queries

Commercial Investigation:
- "Best" and "top" product/service searches
- Comparison and versus keywords
- Review and rating-focused queries
- Feature and benefit research
- Vendor and provider evaluation searches

Local Intent Keywords:
- "Near me" and location-based searches
- Local business and service queries
- Geographic area-specific searches
- Local event and activity keywords
- Regional product and service searches

Voice Search Intent:
- Conversational question-based queries
- Natural language search phrases
- Local and immediate need searches
- Quick answer and fact-based queries
- Mobile and on-the-go search behavior

Intent-based Content Strategy:
- Match content type to search intent
- Create appropriate calls-to-action for each intent
- Develop content funnels based on user journey
- Optimize conversion paths for different intents
- Build topical authority across all intent types"""

    def _build_opportunity_identification(self, config: KeywordResearchPrompt) -> str:
        """Build opportunity identification strategy"""
        return f"""
KEYWORD OPPORTUNITY IDENTIFICATION:

Low-Hanging Fruit Keywords:
- High volume, low competition keywords
- Keywords with declining competitor rankings
- Trending topics with low competition
- Long-tail variations of competitive terms
- Question-based keywords with content gaps

Content Gap Opportunities:
- Topics competitors cover poorly or briefly
- Outdated competitor content opportunities
- Missing subtopics in competitor coverage
- Underserved user questions and problems
- Format gaps (video, audio, interactive content)

Seasonal and Trending Opportunities:
- Emerging trend keywords before they become competitive
- Seasonal keywords with good search volume
- News and current event-related opportunities
- Holiday and event-based keyword opportunities
- Industry-specific seasonal patterns

Featured Snippet Opportunities:
- Questions currently answered poorly in snippets
- List and table format keyword opportunities
- How-to keywords suitable for step-by-step snippets
- Definition keywords for paragraph snippets
- Comparison keywords for table snippets

Local SEO Opportunities:
- Underserved local keyword combinations
- Location + service/product keyword gaps
- Local business directory optimization keywords
- Geographic modifier opportunities
- Local event and activity keywords

Voice Search Opportunities:
- Conversational long-tail keywords
- Question-based queries for voice search
- Local and immediate need voice searches
- FAQ-style keyword opportunities
- Natural language query optimization

Creator Economy Specific Opportunities:
- Content creation and tools keywords
- Monetization and business-related searches
- Platform-specific optimization keywords
- Creator education and training searches
- Industry trend and news keywords

Monetization Keyword Opportunities:
- High commercial intent keywords
- Product and service comparison terms
- Tool and software evaluation keywords
- Investment and ROI-focused searches
- Business growth and strategy keywords"""

    def _build_content_strategy(self, config: KeywordResearchPrompt) -> str:
        """Build content strategy based on keywords"""
        content_formats = [cf.value for cf in config.content_formats] if config.content_formats else ["blog_post", "video", "social_media"]
        
        return f"""
KEYWORD-DRIVEN CONTENT STRATEGY:

Content Format Mapping:
Target Formats: {', '.join(content_formats)}

Blog Post Keywords:
- Informational and educational searches
- Long-form how-to and guide keywords
- Comparison and review keywords
- In-depth topic exploration searches
- Problem-solving and solution keywords

Video Content Keywords:
- Tutorial and demonstration searches
- Entertainment and lifestyle keywords
- Product review and unboxing terms
- Behind-the-scenes and process keywords
- Visual learning and explanation searches

Social Media Keywords:
- Trending hashtags and viral topics
- Quick tip and advice keywords
- Inspirational and motivational searches
- Community and discussion-focused terms
- Real-time and current event keywords

Podcast Keywords:
- Interview and conversation topics
- Deep-dive analysis keywords
- Expert opinion and commentary searches
- Story-telling and narrative keywords
- Industry news and trend discussions

Content Cluster Strategy:
- Create pillar pages for broad topic keywords
- Develop cluster content for long-tail variations
- Build topic authority through comprehensive coverage
- Link related content for SEO benefit
- Create series and ongoing content themes

Content Calendar Integration:
- Map seasonal keywords to content calendar
- Align trending topics with publishing schedule
- Balance evergreen and timely content
- Plan content series around keyword clusters
- Schedule competitor gap-filling content

Cross-Platform Content Strategy:
- Repurpose content across multiple formats
- Optimize keyword targeting for each platform
- Create platform-specific keyword variations
- Build audience across multiple channels
- Leverage platform-specific search features

Monetization Content Integration:
- Include commercial keywords in content mix
- Create conversion-optimized landing pages
- Develop product and service showcase content
- Build trust through educational content first
- Create clear conversion funnels from organic traffic"""

    def _build_keyword_prioritization(self, config: KeywordResearchPrompt) -> str:
        """Build keyword prioritization framework"""
        return f"""
KEYWORD PRIORITIZATION FRAMEWORK:

Priority Scoring Matrix:
Factor 1: Search Volume (Weight: 30%)
- {config.target_volume.value} volume range preferred
- Higher volume = higher priority
- Consider traffic potential vs. competition

Factor 2: Keyword Difficulty (Weight: 25%)
- Maximum difficulty: {config.max_difficulty.value}
- Lower difficulty = higher priority
- Consider current domain authority and resources

Factor 3: Commercial Intent (Weight: 20%)
- Transactional keywords = highest priority
- Commercial investigation = high priority
- Informational = medium priority for authority building

Factor 4: Relevance to Business (Weight: 15%)
- Direct product/service keywords = highest priority
- Industry authority keywords = high priority
- General topic keywords = medium priority

Factor 5: Competition Analysis (Weight: 10%)
- Weak competitor content = higher priority
- Content gaps = higher priority
- Saturated markets = lower priority

Quick Win Keywords (Implement First):
- Low competition, medium volume keywords
- Long-tail variations of main topics
- Question-based keywords with content gaps
- Seasonal opportunities with immediate potential
- Local keywords (if applicable)

Medium-term Targets:
- Medium competition, high volume keywords
- Competitive analysis gap keywords
- Content cluster supporting keywords
- Brand awareness and authority keywords
- Cross-format content opportunities

Long-term Aspirational Keywords:
- High competition, high volume keywords
- Industry-defining topic keywords
- Competitor stronghold keywords
- Market leadership positioning keywords
- High commercial value keywords

Implementation Timeline:
Month 1-3: Quick win keywords and content gaps
Month 4-6: Medium competition targets and clusters
Month 7-12: Long-term aspirational keywords
Ongoing: Seasonal and trending opportunities
Quarterly: Competitive analysis and strategy adjustment

Budget and Resource Allocation:
- Prioritize keywords based on available resources
- Consider content creation time and complexity
- Factor in promotion and link building requirements
- Allocate budget for keyword research tools
- Plan for ongoing optimization and monitoring"""

    def _build_trend_analysis(self, config: KeywordResearchPrompt) -> str:
        """Build trend analysis strategy"""
        trending_topics = config.trending_topics or ["Identify emerging trends in the industry"]
        
        return f"""
TREND ANALYSIS AND FORECASTING:

Current Trending Topics: {', '.join(trending_topics)}

Google Trends Analysis:
- Analyze search volume trends for target keywords
- Identify seasonal patterns and cyclical behavior
- Compare trending topics and related searches
- Monitor geographic trends and regional interests
- Track competitor keyword trend performance

Emerging Keyword Opportunities:
- Identify keywords with growing search volume
- Monitor new industry terminology and jargon
- Track technology and innovation-related searches
- Follow social media trending hashtags
- Analyze news and media coverage for keyword opportunities

Seasonal Keyword Planning:
{config.seasonal_considerations or 'Analyze seasonal patterns for target industry'}
- Map keyword search volume to calendar periods
- Identify peak and off-peak search seasons
- Plan content publication timing for maximum impact
- Prepare evergreen content for consistent performance
- Create seasonal content variations and updates

Industry Trend Monitoring:
- Track industry news and development keywords
- Monitor competitor content and keyword strategies
- Follow thought leader and influencer discussions
- Analyze conference and event keyword opportunities
- Track regulatory and policy change impacts

Technology and Innovation Trends:
- Monitor emerging technology keyword adoption
- Track new platform and tool-related searches
- Analyze AI and automation keyword trends
- Follow social media platform algorithm changes
- Monitor creator economy platform developments

Content Freshness Strategy:
- Update content based on keyword trend changes
- Refresh outdated content with new trending terms
- Create new content around emerging opportunities
- Optimize existing content for trend-related keywords
- Monitor and respond to real-time trend opportunities

Predictive Keyword Research:
- Analyze historical data for pattern prediction
- Use competitor analysis for trend forecasting
- Monitor early adopter and innovator content
- Track investment and funding news for keyword insights
- Analyze patent filings and research publications

Risk Assessment:
- Identify fad vs. lasting trend keywords
- Assess potential algorithm change impacts
- Monitor competitor response to trends
- Evaluate resource investment vs. trend longevity
- Plan contingency strategies for trend shifts"""

    def _build_measurement_strategy(self, config: KeywordResearchPrompt) -> str:
        """Build measurement and tracking strategy"""
        return f"""
KEYWORD RESEARCH MEASUREMENT STRATEGY:

Key Performance Indicators (KPIs):
- Keyword ranking positions and movement
- Organic traffic growth from target keywords
- Click-through rates from search results
- Conversion rates from organic keyword traffic
- Market share vs. competitors for target keywords

Tracking Setup:
- Google Search Console keyword monitoring
- SEO tool rank tracking (SEMrush, Ahrefs, etc.)
- Google Analytics organic traffic analysis
- Conversion tracking for commercial keywords
- Competitor monitoring and alerts

Research Quality Metrics:
- Keyword opportunity identification accuracy
- Ranking achievement rate for target keywords
- Traffic prediction vs. actual performance
- Conversion rate accuracy for commercial keywords
- Content gap identification success rate

Competitive Monitoring:
- Competitor keyword ranking changes
- New competitor content and keyword targeting
- Market share shifts and opportunities
- Competitor content gap analysis updates
- Industry trend adoption by competitors

Content Performance Analysis:
- Content ranking performance for target keywords
- User engagement metrics for keyword-targeted content
- Social sharing and backlink generation
- Content freshness and update requirements
- Cross-format content performance comparison

ROI Measurement:
- Cost per keyword research hour
- Revenue attribution to keyword-driven content
- Organic traffic value calculation
- Conversion value from target keywords
- Long-term brand authority building metrics

Continuous Improvement:
- Monthly keyword ranking reviews
- Quarterly research strategy assessment
- Annual competitive landscape analysis
- Ongoing trend monitoring and adjustment
- Regular tool and methodology evaluation

Reporting and Communication:
- Executive summary of keyword opportunities
- Detailed keyword research findings and recommendations
- Competitive analysis insights and strategic implications
- Trend analysis and future opportunity forecasting
- Implementation roadmap and resource requirements"""

    def _combine_prompt_components(self, components: Dict[str, str]) -> str:
        """Combine all prompt components into final prompt"""
        return f"""{components['system_prompt']}

{components['user_prompt']}

{components['keyword_discovery']}

{components['competitive_analysis']}

{components['search_intent_analysis']}

{components['opportunity_identification']}

{components['content_strategy']}

{components['keyword_prioritization']}

{components['trend_analysis']}

{components['measurement_strategy']}

Now conduct comprehensive keyword research following all these methodologies. Provide detailed keyword lists, competitive analysis, opportunity identification, and strategic recommendations for optimal search visibility and Creator Economy success."""

    def _generate_metadata(self, config: KeywordResearchPrompt) -> Dict[str, Any]:
        """Generate metadata for the keyword research"""
        return {
            "template_version": self.template_version,
            "primary_topic": config.primary_topic,
            "industry": config.industry,
            "target_volume": config.target_volume.value,
            "max_difficulty": config.max_difficulty.value,
            "keyword_types_count": len(config.keyword_types),
            "content_formats_count": len(config.content_formats),
            "competitor_count": len(config.competitor_domains),
            "existing_keywords_count": len(config.existing_keywords),
            "brand_keywords_count": len(config.brand_keywords),
            "content_goals_count": len(config.content_goals),
            "monetization_goals_count": len(config.monetization_goals),
            "voice_search_enabled": config.voice_search_focus,
            "mobile_priority": config.mobile_search_priority,
            "local_focus": config.local_search_intent,
            "geographic_focus": config.geographic_focus,
            "language": config.language,
            "creation_timestamp": datetime.now().isoformat(),
            "creator_economy_optimized": True
        }

    def _calculate_research_scope(self, config: KeywordResearchPrompt) -> str:
        """Calculate research scope based on configuration"""
        scope_factors = 0
        
        if config.keyword_types:
            scope_factors += len(config.keyword_types)
        if config.content_formats:
            scope_factors += len(config.content_formats)
        if config.competitor_domains:
            scope_factors += len(config.competitor_domains)
        if config.content_goals:
            scope_factors += len(config.content_goals)
            
        if scope_factors >= 15:
            return "Comprehensive"
        elif scope_factors >= 10:
            return "Extensive"
        elif scope_factors >= 5:
            return "Moderate"
        else:
            return "Basic"

    def _calculate_opportunity_score(self, config: KeywordResearchPrompt) -> float:
        """Calculate opportunity score based on configuration"""
        score = 0.3  # Base score
        
        # Volume and difficulty balance
        if config.target_volume == SearchVolume.HIGH and config.max_difficulty == KeywordDifficulty.MEDIUM:
            score += 0.2
        elif config.target_volume == SearchVolume.MEDIUM and config.max_difficulty == KeywordDifficulty.EASY:
            score += 0.2
        
        # Competitive analysis
        if config.competitor_domains:
            score += 0.1
            
        # Content format diversity
        if len(config.content_formats) >= 3:
            score += 0.1
            
        # Creator economy features
        if config.monetization_goals:
            score += 0.1
            
        # Trend and voice search
        if config.voice_search_focus:
            score += 0.05
        if config.trending_topics:
            score += 0.05
            
        return min(score, 1.0)

    def _assess_competition_level(self, config: KeywordResearchPrompt) -> str:
        """Assess overall competition level"""
        if config.max_difficulty == KeywordDifficulty.EASY:
            return "Low Competition Environment"
        elif config.max_difficulty == KeywordDifficulty.MEDIUM:
            return "Moderate Competition Environment"
        elif config.max_difficulty == KeywordDifficulty.HARD:
            return "High Competition Environment"
        else:
            return "Very High Competition Environment"

    def _generate_keyword_categories(self, config: KeywordResearchPrompt) -> List[str]:
        """Generate keyword categories for research"""
        categories = []
        
        # Always include these basic categories
        categories.extend([
            "Primary Topic Keywords",
            "Long-tail Variations",
            "Question-based Keywords",
            "Commercial Intent Keywords"
        ])
        
        # Add based on configuration
        if config.competitor_domains:
            categories.append("Competitor Gap Keywords")
            
        if config.local_search_intent:
            categories.append("Local SEO Keywords")
            
        if config.voice_search_focus:
            categories.append("Voice Search Keywords")
            
        if config.trending_topics:
            categories.append("Trending Keywords")
            
        if config.seasonal_considerations:
            categories.append("Seasonal Keywords")
            
        if config.brand_keywords:
            categories.append("Brand Keywords")
            
        return categories

# Example usage and testing
if __name__ == "__main__":
    # Example configuration
    config = KeywordResearchPrompt(
        primary_topic="content creator marketing strategies",
        industry="Digital Marketing",
        business_type="Creator economy education and tools",
        target_audience="Content creators, influencers, and digital entrepreneurs",
        content_goals=["Increase organic traffic", "Build topical authority", "Generate leads"],
        keyword_types=[KeywordType.LONG_TAIL, KeywordType.QUESTION_BASED, KeywordType.COMPETITOR],
        target_volume=SearchVolume.MEDIUM,
        max_difficulty=KeywordDifficulty.MEDIUM,
        content_formats=[ContentFormat.BLOG_POST, ContentFormat.VIDEO, ContentFormat.PODCAST],
        geographic_focus="United States",
        competitor_domains=["creatoreconomy.com", "socialmediacreators.com", "influencermarketing.com"],
        existing_keywords=["creator marketing", "influencer strategy", "content monetization"],
        brand_keywords=["Creator Academy", "Marketing Masters"],
        seasonal_considerations="Higher interest in Q1 for New Year business planning",
        user_personas=["Beginning creators", "Established influencers", "Creator economy entrepreneurs"],
        buyer_journey_stage="Awareness and consideration",
        monetization_goals=["Course sales", "Consulting leads", "Tool subscriptions"],
        trending_topics=["AI content creation", "TikTok marketing", "Creator economy trends"],
        voice_search_focus=True,
        mobile_search_priority=True,
        local_search_intent=False,
        feature_snippet_targets=["What is creator marketing", "How to monetize content", "Best creator tools"]
    )
    
    # Generate prompt
    template = KeywordResearchTemplate()
    result = template.generate_prompt(config)
    
    print("=== KEYWORD RESEARCH TEMPLATE EXAMPLE ===")
    print(f"Research Scope: {result['research_scope']}")
    print(f"Opportunity Score: {result['opportunity_score']:.2f}")
    print(f"Competition Level: {result['competition_level']}")
    print(f"Keyword Categories: {', '.join(result['keyword_categories'])}")
    print("\n" + "="*50)
    print(result['prompt'])