"""
Meta Description Template for AI-Powered Content Generation

Enterprise-grade meta description prompt engineering template optimized for the Creator Economy.
Provides advanced prompt structures for generating high-quality meta descriptions across
multiple content types and platforms with built-in optimization for CTR and search visibility.

Author: AI Expert Team Lead by Fahed Mlaiel
Contact: contact@fahedmlaiel.fr | https://fahedmlaiel.fr
Copyright (c) 2024 Fahed Mlaiel. All rights reserved.
License: Proprietary - Contact for licensing terms
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, field
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentType(Enum):
    BLOG_POST = "blog_post"
    LANDING_PAGE = "landing_page"
    PRODUCT_PAGE = "product_page"
    SERVICE_PAGE = "service_page"
    ABOUT_PAGE = "about_page"
    CONTACT_PAGE = "contact_page"
    FAQ_PAGE = "faq_page"
    CATEGORY_PAGE = "category_page"
    NEWS_ARTICLE = "news_article"
    TUTORIAL = "tutorial"
    GUIDE = "guide"
    REVIEW = "review"
    COMPARISON = "comparison"
    CASE_STUDY = "case_study"
    VIDEO_PAGE = "video_page"
    PODCAST_PAGE = "podcast_page"

class SearchIntent(Enum):
    INFORMATIONAL = "informational"
    TRANSACTIONAL = "transactional"
    NAVIGATIONAL = "navigational"
    COMMERCIAL = "commercial"

@dataclass
class MetaDescriptionPrompt:
    content_type: ContentType
    page_title: str
    primary_keyword: str
    secondary_keywords: List[str] = field(default_factory=list)
    search_intent: SearchIntent = SearchIntent.INFORMATIONAL
    target_audience: str = ""
    unique_value_proposition: str = ""
    call_to_action: str = ""
    brand_name: str = ""
    page_content_summary: str = ""
    competitive_advantage: str = ""
    emotional_trigger: str = ""
    urgency_factor: str = ""
    social_proof: str = ""
    character_limit: int = 160
    include_brand: bool = True
    include_cta: bool = True
    locale: str = "en-US"

class MetaDescriptionTemplate:
    def __init__(self):
        self.template_version = "1.0.0"
        self.creator_economy_features = True
        
    def generate_prompt(self, config: MetaDescriptionPrompt) -> Dict[str, Any]:
        try:
            prompt_components = {
                "system_prompt": self._build_system_prompt(config),
                "user_prompt": self._build_user_prompt(config),
                "optimization_guidelines": self._build_optimization_guidelines(config),
                "ctr_optimization": self._build_ctr_optimization(config),
                "testing_variations": self._build_testing_variations(config)
            }
            
            final_prompt = self._combine_prompt_components(prompt_components)
            metadata = self._generate_metadata(config)
            
            logger.info(f"Generated meta description prompt for {config.content_type.value}")
            
            return {
                "prompt": final_prompt,
                "metadata": metadata,
                "config": config,
                "optimization_score": self._calculate_optimization_score(config),
                "ctr_potential": self._estimate_ctr_potential(config)
            }
            
        except Exception as e:
            logger.error(f"Error generating meta description prompt: {str(e)}")
            raise
    
    def _build_system_prompt(self, config: MetaDescriptionPrompt) -> str:
        return f"""You are an expert SEO copywriter specializing in high-converting meta descriptions for the Creator Economy.

Your expertise includes:
- SERP optimization and click-through rate maximization
- Psychology-driven copywriting for search results
- Creator Economy content optimization
- A/B testing and conversion optimization
- Search intent matching and user experience

Creating: Meta description for {config.content_type.value}
Primary Keyword: "{config.primary_keyword}"
Search Intent: {config.search_intent.value}
Character Limit: {config.character_limit}
Target Audience: {config.target_audience or 'General audience'}

Focus on:
- Maximum click-through rate from search results
- Perfect keyword integration and search intent matching
- Compelling value proposition and emotional triggers
- Creator Economy monetization optimization
- SERP competition differentiation"""

    def _build_user_prompt(self, config: MetaDescriptionPrompt) -> str:
        secondary_keywords = f"\nSecondary Keywords: {', '.join(config.secondary_keywords)}" if config.secondary_keywords else ""
        brand_info = f"\nBrand: {config.brand_name}" if config.brand_name else ""
        value_prop = f"\nValue Proposition: {config.unique_value_proposition}" if config.unique_value_proposition else ""
        content_summary = f"\nContent Summary: {config.page_content_summary}" if config.page_content_summary else ""
        competitive_advantage = f"\nCompetitive Advantage: {config.competitive_advantage}" if config.competitive_advantage else ""
        
        return f"""Page Title: {config.page_title}
Primary Keyword: "{config.primary_keyword}"{secondary_keywords}
Search Intent: {config.search_intent.value}
Character Limit: {config.character_limit} characters maximum{brand_info}{value_prop}{content_summary}{competitive_advantage}

Requirements:
- Include primary keyword naturally
- Create compelling, click-worthy copy
- Match {config.search_intent.value} search intent
- Include call-to-action: {config.call_to_action or 'Encourage clicks'}
- Target {config.target_audience or 'general audience'}
- Stay within {config.character_limit} character limit
- Include brand name: {config.include_brand}

Creator Economy Optimization:
- Maximize organic click-through rates
- Build authority and trust in search results
- Drive qualified traffic for monetization
- Differentiate from competitor results"""

    def _build_optimization_guidelines(self, config: MetaDescriptionPrompt) -> str:
        return f"""
META DESCRIPTION OPTIMIZATION GUIDELINES:

Character Count Management:
- Target: {config.character_limit} characters maximum
- Optimal range: 150-160 characters for desktop
- Mobile consideration: 120-130 characters for mobile snippets
- Include spaces and punctuation in count
- Avoid truncation with strategic length management

Keyword Integration:
- Include primary keyword: "{config.primary_keyword}"
- Place primary keyword early in description
- Use secondary keywords naturally if space allows
- Avoid keyword stuffing and maintain readability
- Use synonyms and variations for semantic relevance

Value Proposition:
- Lead with unique benefit or solution
- Highlight what makes this page different
- Include specific outcomes or results
- Mention exclusive content or insights
- Address user pain points or needs

Call-to-Action Integration:
- Include action words: learn, discover, get, find, see
- Create urgency where appropriate
- Use benefit-driven language
- Include specific next steps
- Balance CTA with information

Brand Integration:
- Include brand name strategically
- Position brand for trust and authority
- Use brand as quality indicator
- Balance brand mention with content description
- Leverage brand recognition where strong"""

    def _build_ctr_optimization(self, config: MetaDescriptionPrompt) -> str:
        emotional_trigger = f"Emotional trigger: {config.emotional_trigger}" if config.emotional_trigger else ""
        urgency_factor = f"Urgency factor: {config.urgency_factor}" if config.urgency_factor else ""
        social_proof = f"Social proof: {config.social_proof}" if config.social_proof else ""
        
        return f"""
CLICK-THROUGH RATE OPTIMIZATION:

Psychological Triggers:
{emotional_trigger or "- Use curiosity, urgency, or benefit-driven language"}
{urgency_factor or "- Create time-sensitive or limited availability appeal"}
{social_proof or "- Include trust indicators and social validation"}
- Use power words: ultimate, essential, proven, exclusive
- Include numbers and specific benefits
- Address user emotions and desires

SERP Differentiation:
- Stand out from competitor meta descriptions
- Use unique angles and positioning
- Include specific details and benefits
- Avoid generic or vague language
- Highlight exclusive content or insights

Search Intent Matching:
- Informational: Promise valuable information and insights
- Transactional: Include clear product benefits and CTA
- Commercial: Highlight comparisons and decision factors
- Navigational: Confirm page relevance and brand

Mobile Optimization:
- Front-load important information
- Use shorter sentences and clear language
- Ensure readability on small screens
- Include tap-worthy action words
- Consider voice search implications

Competitive Analysis:
- Analyze top-ranking meta descriptions for keyword
- Identify gaps and opportunities
- Use better value propositions
- Include unique selling points
- Leverage competitive advantages"""

    def _build_testing_variations(self, config: MetaDescriptionPrompt) -> str:
        return f"""
A/B TESTING VARIATIONS:

Create Multiple Versions:
1. Benefit-focused version emphasizing outcomes
2. Feature-focused version highlighting specific content
3. Urgency-driven version with time-sensitive language
4. Question-based version engaging curiosity
5. Social proof version with credibility indicators

Testing Elements:
- Different keyword placements
- Various call-to-action approaches
- Emotional vs. rational appeals
- Brand positioning variations
- Length optimization tests

Performance Metrics:
- Click-through rate from search results
- Time on page from organic traffic
- Bounce rate from meta description traffic
- Conversion rate from organic visitors
- Search impression share and visibility

Optimization Strategy:
- Test one element at a time
- Run tests for statistical significance
- Monitor seasonal and trend impacts
- Analyze competitor meta description changes
- Optimize based on search console data"""

    def _combine_prompt_components(self, components: Dict[str, str]) -> str:
        return f"""{components['system_prompt']}

{components['user_prompt']}

{components['optimization_guidelines']}

{components['ctr_optimization']}

{components['testing_variations']}

Now create optimized meta descriptions following all guidelines. Provide the main version plus 3-5 testing variations for A/B testing."""

    def _generate_metadata(self, config: MetaDescriptionPrompt) -> Dict[str, Any]:
        return {
            "template_version": self.template_version,
            "content_type": config.content_type.value,
            "primary_keyword": config.primary_keyword,
            "search_intent": config.search_intent.value,
            "character_limit": config.character_limit,
            "include_brand": config.include_brand,
            "include_cta": config.include_cta,
            "secondary_keywords_count": len(config.secondary_keywords),
            "creation_timestamp": datetime.now().isoformat(),
            "creator_economy_optimized": True
        }

    def _calculate_optimization_score(self, config: MetaDescriptionPrompt) -> float:
        score = 0.5
        if config.unique_value_proposition: score += 0.15
        if config.call_to_action: score += 0.1
        if config.secondary_keywords: score += 0.1
        if config.emotional_trigger: score += 0.1
        if config.social_proof: score += 0.05
        return min(score, 1.0)

    def _estimate_ctr_potential(self, config: MetaDescriptionPrompt) -> str:
        score = self._calculate_optimization_score(config)
        if score >= 0.8: return "High"
        elif score >= 0.6: return "Medium-High"
        elif score >= 0.4: return "Medium"
        else: return "Low-Medium"

# Example usage
if __name__ == "__main__":
    config = MetaDescriptionPrompt(
        content_type=ContentType.BLOG_POST,
        page_title="Ultimate Guide to Creator Economy SEO Strategies",
        primary_keyword="creator economy SEO",
        secondary_keywords=["content creator marketing", "influencer SEO"],
        search_intent=SearchIntent.INFORMATIONAL,
        target_audience="content creators and digital entrepreneurs",
        unique_value_proposition="Proven strategies that increased creator traffic by 300%",
        call_to_action="Learn the exact tactics",
        brand_name="Creator SEO Academy",
        page_content_summary="Comprehensive guide covering keyword research, content optimization, and monetization",
        competitive_advantage="Only guide written by creators who scaled to 7-figures",
        emotional_trigger="Transform your content into a traffic magnet",
        social_proof="Used by 10,000+ successful creators"
    )
    
    template = MetaDescriptionTemplate()
    result = template.generate_prompt(config)
    
    print("=== META DESCRIPTION TEMPLATE EXAMPLE ===")
    print(f"Optimization Score: {result['optimization_score']:.2f}")
    print(f"CTR Potential: {result['ctr_potential']}")
    print("\n" + "="*50)
    print(result['prompt'])