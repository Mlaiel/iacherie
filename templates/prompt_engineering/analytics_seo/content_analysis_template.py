"""
Content Analysis Template for AI-Powered Content Optimization

Enterprise-grade content analysis prompt engineering template optimized for the Creator Economy.
Provides comprehensive content evaluation, optimization recommendations, and performance insights
across multiple metrics and platforms.

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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalysisType(Enum):
    SEO_ANALYSIS = "seo_analysis"
    READABILITY = "readability"
    ENGAGEMENT = "engagement"
    CONVERSION = "conversion"
    COMPETITIVE = "competitive"
    PERFORMANCE = "performance"
    CONTENT_QUALITY = "content_quality"
    MONETIZATION = "monetization"

class ContentFormat(Enum):
    BLOG_POST = "blog_post"
    VIDEO_SCRIPT = "video_script"
    SOCIAL_MEDIA = "social_media"
    EMAIL = "email"
    LANDING_PAGE = "landing_page"
    PODCAST_SCRIPT = "podcast_script"

@dataclass
class ContentAnalysisPrompt:
    content_text: str
    content_format: ContentFormat
    analysis_types: List[AnalysisType] = field(default_factory=list)
    target_keywords: List[str] = field(default_factory=list)
    target_audience: str = ""
    business_goals: List[str] = field(default_factory=list)
    competitor_content: str = ""
    platform: str = ""
    current_performance_metrics: Dict[str, Any] = field(default_factory=dict)
    optimization_priorities: List[str] = field(default_factory=list)

class ContentAnalysisTemplate:
    def __init__(self):
        self.template_version = "1.0.0"
        self.creator_economy_features = True
        
    def generate_prompt(self, config: ContentAnalysisPrompt) -> Dict[str, Any]:
        try:
            prompt_components = {
                "system_prompt": self._build_system_prompt(config),
                "content_analysis": self._build_content_analysis(config),
                "seo_evaluation": self._build_seo_evaluation(config),
                "engagement_analysis": self._build_engagement_analysis(config),
                "optimization_recommendations": self._build_optimization_recommendations(config)
            }
            
            final_prompt = self._combine_prompt_components(prompt_components)
            metadata = self._generate_metadata(config)
            
            logger.info(f"Generated content analysis prompt for {config.content_format.value}")
            
            return {
                "prompt": final_prompt,
                "metadata": metadata,
                "config": config,
                "analysis_scope": self._calculate_analysis_scope(config)
            }
            
        except Exception as e:
            logger.error(f"Error generating content analysis prompt: {str(e)}")
            raise
    
    def _build_system_prompt(self, config: ContentAnalysisPrompt) -> str:
        analysis_types = [at.value for at in config.analysis_types] if config.analysis_types else ["comprehensive"]
        
        return f"""You are an expert content analyst and optimization specialist for the Creator Economy with expertise in:

- Comprehensive content evaluation and optimization
- SEO analysis and search performance optimization
- Engagement psychology and audience retention
- Conversion optimization and monetization strategies
- Competitive content analysis and differentiation
- Creator Economy best practices and trends

Analysis Focus: {', '.join(analysis_types)}
Content Format: {config.content_format.value}
Platform: {config.platform or 'Multi-platform'}
Target Audience: {config.target_audience or 'General audience'}

Provide actionable insights for Creator Economy success."""

    def _build_content_analysis(self, config: ContentAnalysisPrompt) -> str:
        keywords_info = f"Target Keywords: {', '.join(config.target_keywords)}" if config.target_keywords else ""
        goals_info = f"Business Goals: {', '.join(config.business_goals)}" if config.business_goals else ""
        
        return f"""
COMPREHENSIVE CONTENT ANALYSIS:

Content to Analyze:
"{config.content_text}"

{keywords_info}
{goals_info}

Analysis Framework:
1. Content Quality Assessment
   - Clarity and coherence
   - Value delivery and usefulness
   - Originality and uniqueness
   - Depth and comprehensiveness
   - Accuracy and credibility

2. Structure and Organization
   - Logical flow and progression
   - Header hierarchy and organization
   - Paragraph length and readability
   - Bullet points and formatting
   - Call-to-action placement

3. Voice and Tone Evaluation
   - Consistency with brand voice
   - Appropriateness for target audience
   - Emotional engagement level
   - Professional vs. conversational balance
   - Authenticity and personality

4. Technical Writing Assessment
   - Grammar and spelling accuracy
   - Sentence structure variety
   - Vocabulary appropriateness
   - Transition quality
   - Conclusion effectiveness"""

    def _build_seo_evaluation(self, config: ContentAnalysisPrompt) -> str:
        keywords = config.target_keywords or ["No keywords specified"]
        
        return f"""
SEO CONTENT EVALUATION:

Keyword Analysis:
Target Keywords: {', '.join(keywords)}

1. Keyword Integration Assessment
   - Primary keyword placement and frequency
   - Secondary keyword distribution
   - Natural keyword integration
   - Keyword stuffing evaluation
   - Semantic keyword usage

2. On-Page SEO Elements
   - Title optimization potential
   - Meta description opportunities
   - Header tag structure (H1-H6)
   - Internal linking opportunities
   - External linking strategy

3. Content Length and Depth
   - Word count appropriateness
   - Topic coverage comprehensiveness
   - Competitive content comparison
   - Search intent fulfillment
   - Featured snippet potential

4. Technical SEO Factors
   - URL optimization potential
   - Image alt text opportunities
   - Schema markup possibilities
   - Mobile optimization considerations
   - Page speed impact factors

5. Search Intent Matching
   - Informational intent satisfaction
   - Transactional element integration
   - Commercial investigation support
   - User journey alignment
   - Conversion path optimization"""

    def _build_engagement_analysis(self, config: ContentAnalysisPrompt) -> str:
        performance_metrics = config.current_performance_metrics
        
        return f"""
ENGAGEMENT AND RETENTION ANALYSIS:

Current Performance:
{performance_metrics if performance_metrics else "No metrics provided"}

1. Hook and Opening Assessment
   - First sentence effectiveness
   - Curiosity gap creation
   - Value proposition clarity
   - Attention-grabbing elements
   - Scroll-stopping potential

2. Content Flow and Pacing
   - Reading rhythm and flow
   - Information density balance
   - Break points and breathing room
   - Transition smoothness
   - Momentum maintenance

3. Interactive Elements
   - Question integration
   - Discussion prompts
   - Call-to-action effectiveness
   - Social sharing triggers
   - Comment encouragement

4. Emotional Engagement
   - Emotional trigger identification
   - Relatability factors
   - Story-telling elements
   - Personal connection opportunities
   - Empathy and understanding

5. Visual and Formatting
   - Scanability and readability
   - White space utilization
   - Bold and italic emphasis
   - List and bullet usage
   - Visual hierarchy clarity

6. Platform-Specific Optimization
   - Platform algorithm alignment
   - Format-specific best practices
   - Community engagement factors
   - Sharing and virality potential
   - Platform feature utilization"""

    def _build_optimization_recommendations(self, config: ContentAnalysisPrompt) -> str:
        priorities = config.optimization_priorities or ["Overall improvement"]
        competitor_info = f"Competitor Content Analysis: {config.competitor_content}" if config.competitor_content else ""
        
        return f"""
OPTIMIZATION RECOMMENDATIONS:

Priority Areas: {', '.join(priorities)}
{competitor_info}

1. Immediate Quick Wins (High Impact, Low Effort)
   - Grammar and spelling corrections
   - Header optimization for keywords
   - Call-to-action enhancement
   - Meta description optimization
   - Internal linking additions

2. Content Enhancement Opportunities
   - Additional value-add sections
   - Supporting examples and case studies
   - Updated statistics and data
   - Expert quotes and social proof
   - Multimedia integration suggestions

3. SEO Optimization Strategy
   - Keyword density optimization
   - Related keyword integration
   - Content cluster development
   - Featured snippet targeting
   - Technical SEO improvements

4. Engagement Improvement Tactics
   - Hook strengthening recommendations
   - Interactive element additions
   - Story-telling enhancement
   - Personal connection opportunities
   - Community engagement triggers

5. Conversion Optimization
   - CTA placement and copy optimization
   - Lead magnet integration
   - Trust signal additions
   - Social proof incorporation
   - Funnel alignment improvements

6. Creator Economy Monetization
   - Monetization opportunity identification
   - Audience building potential
   - Brand partnership alignment
   - Product placement opportunities
   - Community monetization strategies

7. Competitive Differentiation
   - Unique angle development
   - Value proposition strengthening
   - Content gap filling
   - Positioning optimization
   - Authority building recommendations

8. Performance Tracking Setup
   - KPI identification and tracking
   - A/B testing opportunities
   - Content performance metrics
   - Engagement optimization tracking
   - ROI measurement strategy"""

    def _combine_prompt_components(self, components: Dict[str, str]) -> str:
        return f"""{components['system_prompt']}

{components['content_analysis']}

{components['seo_evaluation']}

{components['engagement_analysis']}

{components['optimization_recommendations']}

Provide comprehensive analysis with specific, actionable recommendations for Creator Economy optimization and success."""

    def _generate_metadata(self, config: ContentAnalysisPrompt) -> Dict[str, Any]:
        return {
            "template_version": self.template_version,
            "content_format": config.content_format.value,
            "content_length": len(config.content_text),
            "analysis_types_count": len(config.analysis_types),
            "target_keywords_count": len(config.target_keywords),
            "business_goals_count": len(config.business_goals),
            "has_competitor_content": bool(config.competitor_content),
            "has_performance_metrics": bool(config.current_performance_metrics),
            "platform": config.platform,
            "creation_timestamp": datetime.now().isoformat(),
            "creator_economy_optimized": True
        }

    def _calculate_analysis_scope(self, config: ContentAnalysisPrompt) -> str:
        scope_factors = 0
        scope_factors += len(config.analysis_types)
        scope_factors += len(config.target_keywords)
        scope_factors += len(config.business_goals)
        if config.competitor_content: scope_factors += 1
        if config.current_performance_metrics: scope_factors += 1
        
        if scope_factors >= 10: return "Comprehensive"
        elif scope_factors >= 6: return "Extensive"
        elif scope_factors >= 3: return "Standard"
        else: return "Basic"

# Example usage
if __name__ == "__main__":
    config = ContentAnalysisPrompt(
        content_text="Your content here for analysis...",
        content_format=ContentFormat.BLOG_POST,
        analysis_types=[AnalysisType.SEO_ANALYSIS, AnalysisType.ENGAGEMENT, AnalysisType.MONETIZATION],
        target_keywords=["creator economy", "content monetization"],
        target_audience="content creators and digital entrepreneurs",
        business_goals=["increase organic traffic", "improve engagement", "generate leads"],
        platform="website blog",
        optimization_priorities=["SEO optimization", "engagement improvement"]
    )
    
    template = ContentAnalysisTemplate()
    result = template.generate_prompt(config)
    
    print("=== CONTENT ANALYSIS TEMPLATE EXAMPLE ===")
    print(f"Analysis Scope: {result['analysis_scope']}")
    print("\n" + "="*50)
    print(result['prompt'])