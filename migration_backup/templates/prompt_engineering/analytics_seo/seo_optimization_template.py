"""
SEO Optimization Template for AI-Powered Content Generation

Enterprise-grade SEO optimization prompt engineering template optimized for the Creator Economy.
Provides advanced prompt structures for generating SEO-optimized content across
multiple platforms and content types with built-in optimization for discovery and monetization.

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

class ContentType(Enum):
    """Content types for SEO optimization"""
    BLOG_POST = "blog_post"
    LANDING_PAGE = "landing_page"
    PRODUCT_PAGE = "product_page"
    CATEGORY_PAGE = "category_page"
    ABOUT_PAGE = "about_page"
    SERVICE_PAGE = "service_page"
    FAQ_PAGE = "faq_page"
    NEWS_ARTICLE = "news_article"
    TUTORIAL = "tutorial"
    REVIEW = "review"
    COMPARISON = "comparison"
    LISTICLE = "listicle"
    GUIDE = "guide"
    CASE_STUDY = "case_study"
    VIDEO_PAGE = "video_page"
    PODCAST_PAGE = "podcast_page"

class SearchIntent(Enum):
    """Search intent types"""
    INFORMATIONAL = "informational"
    NAVIGATIONAL = "navigational"
    TRANSACTIONAL = "transactional"
    COMMERCIAL = "commercial"
    LOCAL = "local"
    EDUCATIONAL = "educational"

class CompetitionLevel(Enum):
    """Keyword competition levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

@dataclass
class SEOOptimizationPrompt:
    """SEO optimization prompt configuration"""
    content_type: ContentType
    primary_keyword: str
    secondary_keywords: List[str] = field(default_factory=list)
    search_intent: SearchIntent = SearchIntent.INFORMATIONAL
    target_audience: str = ""
    competition_level: CompetitionLevel = CompetitionLevel.MEDIUM
    target_length: int = 1500
    business_type: str = ""
    location: str = ""
    industry: str = ""
    brand_name: str = ""
    unique_selling_proposition: str = ""
    conversion_goals: List[str] = field(default_factory=list)
    competitor_analysis: List[str] = field(default_factory=list)
    seasonal_factors: str = ""
    technical_requirements: List[str] = field(default_factory=list)
    content_clusters: List[str] = field(default_factory=list)
    internal_linking_strategy: str = ""
    external_authority_sources: List[str] = field(default_factory=list)
    featured_snippet_target: bool = False
    local_seo_focus: bool = False
    mobile_optimization: bool = True
    voice_search_optimization: bool = False
    schema_markup_requirements: List[str] = field(default_factory=list)

class SEOOptimizationTemplate:
    """
    Advanced SEO optimization template for AI content generation
    
    Optimized for Creator Economy with comprehensive SEO strategies, technical optimization,
    and conversion-focused content creation. Supports all major search engines and platforms.
    """
    
    def __init__(self):
        self.template_version = "1.0.0"
        self.creator_economy_features = True
        self.technical_seo_optimization = True
        self.conversion_optimization = True
        
        # SEO best practices by content type
        self.content_type_specs = {
            ContentType.BLOG_POST: {
                "optimal_length": "1500-3000 words",
                "title_length": "50-60 characters",
                "meta_description": "150-160 characters",
                "h1_count": 1,
                "h2_count": "3-6",
                "keyword_density": "1-2%",
                "internal_links": "3-5",
                "external_links": "2-3"
            },
            ContentType.LANDING_PAGE: {
                "optimal_length": "800-1500 words",
                "title_length": "50-60 characters", 
                "meta_description": "150-160 characters",
                "h1_count": 1,
                "h2_count": "2-4",
                "keyword_density": "2-3%",
                "internal_links": "2-4",
                "external_links": "1-2"
            },
            ContentType.PRODUCT_PAGE: {
                "optimal_length": "500-1000 words",
                "title_length": "50-60 characters",
                "meta_description": "150-160 characters", 
                "h1_count": 1,
                "h2_count": "2-5",
                "keyword_density": "2-4%",
                "internal_links": "2-3",
                "external_links": "0-1"
            }
        }
        
        # Search intent optimization strategies
        self.intent_strategies = {
            SearchIntent.INFORMATIONAL: {
                "content_focus": "Comprehensive, educational content",
                "call_to_action": "Subscribe, download, learn more",
                "structure": "Problem > Solution > Detailed explanation",
                "keywords": "How to, what is, why, guide, tutorial"
            },
            SearchIntent.TRANSACTIONAL: {
                "content_focus": "Product benefits, reviews, comparisons",
                "call_to_action": "Buy now, get quote, start trial",
                "structure": "Problem > Product solution > Benefits > CTA",
                "keywords": "Buy, purchase, price, deal, discount"
            },
            SearchIntent.COMMERCIAL: {
                "content_focus": "Product research, comparisons, reviews",
                "call_to_action": "Compare, review, get info",
                "structure": "Options > Comparisons > Recommendations",
                "keywords": "Best, vs, review, comparison, alternative"
            }
        }
        
        # Technical SEO requirements
        self.technical_requirements = {
            "core_web_vitals": ["LCP < 2.5s", "FID < 100ms", "CLS < 0.1"],
            "mobile_optimization": ["Responsive design", "Touch-friendly", "Fast loading"],
            "schema_markup": ["Article", "Product", "Organization", "Person", "FAQ"],
            "accessibility": ["Alt text", "Heading structure", "Color contrast", "Keyboard navigation"]
        }
        
    def generate_prompt(self, config: SEOOptimizationPrompt) -> Dict[str, Any]:
        """
        Generate comprehensive SEO optimization prompt
        
        Args:
            config: SEO optimization configuration
            
        Returns:
            Dictionary containing optimized prompt and metadata
        """
        try:
            # Get content type specifications
            content_specs = self.content_type_specs.get(config.content_type, {})
            
            # Get intent strategy
            intent_strategy = self.intent_strategies.get(config.search_intent, {})
            
            # Build comprehensive prompt
            prompt_components = {
                "system_prompt": self._build_system_prompt(config),
                "user_prompt": self._build_user_prompt(config, content_specs, intent_strategy),
                "keyword_optimization": self._build_keyword_optimization(config),
                "content_structure": self._build_content_structure(config, content_specs),
                "technical_seo": self._build_technical_seo(config),
                "on_page_optimization": self._build_on_page_optimization(config),
                "user_experience": self._build_user_experience(config),
                "conversion_optimization": self._build_conversion_optimization(config),
                "competitive_analysis": self._build_competitive_analysis(config),
                "measurement_tracking": self._build_measurement_tracking(config)
            }
            
            # Combine into final prompt
            final_prompt = self._combine_prompt_components(prompt_components)
            
            # Generate metadata
            metadata = self._generate_metadata(config)
            
            logger.info(f"Generated SEO optimization prompt for {config.content_type.value}")
            
            return {
                "prompt": final_prompt,
                "metadata": metadata,
                "config": config,
                "optimization_score": self._calculate_seo_score(config),
                "competition_analysis": self._analyze_competition(config),
                "ranking_potential": self._estimate_ranking_potential(config),
                "technical_checklist": self._generate_technical_checklist(config)
            }
            
        except Exception as e:
            logger.error(f"Error generating SEO optimization prompt: {str(e)}")
            raise
    
    def _build_system_prompt(self, config: SEOOptimizationPrompt) -> str:
        """Build system prompt for SEO optimization"""
        return f"""You are an expert SEO specialist and content strategist with deep expertise in Creator Economy optimization and search engine algorithms.

Your expertise includes:
- Advanced SEO strategy and technical optimization
- Google Algorithm updates and ranking factors (E-A-T, Core Web Vitals, etc.)
- Content optimization for search intent and user experience
- Creator Economy SEO and monetization strategies
- Competitive analysis and keyword research
- Conversion rate optimization and user journey mapping

Optimizing: {config.content_type.value.replace('_', ' ').title()}
Primary Keyword: "{config.primary_keyword}"
Search Intent: {config.search_intent.value}
Competition Level: {config.competition_level.value}
Target Audience: {config.target_audience or 'General audience'}
Business Type: {config.business_type or 'Creator business'}

Focus on:
- Comprehensive SEO optimization for top search rankings
- User-first content that satisfies search intent
- Technical SEO excellence and Core Web Vitals
- Creator Economy monetization through organic traffic
- Conversion optimization and user engagement
- Future-proof SEO strategies and algorithm resilience"""

    def _build_user_prompt(self, config: SEOOptimizationPrompt, content_specs: Dict, intent_strategy: Dict) -> str:
        """Build user prompt with SEO specifications"""
        secondary_keywords = f"\nSecondary Keywords: {', '.join(config.secondary_keywords)}" if config.secondary_keywords else ""
        location_info = f"\nLocation: {config.location}" if config.location else ""
        industry_info = f"\nIndustry: {config.industry}" if config.industry else ""
        brand_info = f"\nBrand: {config.brand_name}" if config.brand_name else ""
        usp_info = f"\nUSP: {config.unique_selling_proposition}" if config.unique_selling_proposition else ""
        competitors_info = f"\nCompetitors: {', '.join(config.competitor_analysis)}" if config.competitor_analysis else ""
        seasonal_info = f"\nSeasonal Factors: {config.seasonal_factors}" if config.seasonal_factors else ""
        
        return f"""Primary Keyword: "{config.primary_keyword}"{secondary_keywords}
Content Type: {config.content_type.value.replace('_', ' ').title()}
Target Length: {config.target_length} words
Search Intent: {config.search_intent.value}
Competition Level: {config.competition_level.value}{location_info}{industry_info}{brand_info}{usp_info}{competitors_info}{seasonal_info}

Content Specifications:
- Optimal Length: {content_specs.get('optimal_length', 'Based on competition analysis')}
- Title Length: {content_specs.get('title_length', '50-60 characters')}
- Meta Description: {content_specs.get('meta_description', '150-160 characters')}
- Header Structure: {content_specs.get('h1_count', 1)} H1, {content_specs.get('h2_count', '3-6')} H2s
- Keyword Density: {content_specs.get('keyword_density', '1-2%')}

Search Intent Strategy:
- Content Focus: {intent_strategy.get('content_focus', 'Comprehensive value delivery')}
- Structure: {intent_strategy.get('structure', 'Problem > Solution > Action')}
- CTA Strategy: {intent_strategy.get('call_to_action', 'Engagement and conversion')}

SEO Requirements:
- Rank for primary keyword "{config.primary_keyword}"
- Target featured snippet: {config.featured_snippet_target}
- Local SEO focus: {config.local_seo_focus}
- Voice search optimization: {config.voice_search_optimization}
- Mobile-first optimization: {config.mobile_optimization}

Creator Economy Optimization:
- Build organic traffic for long-term monetization
- Create content that converts visitors to customers/subscribers
- Establish topical authority and thought leadership
- Generate social shares and backlink opportunities
- Optimize for Creator Economy business models and revenue streams"""

    def _build_keyword_optimization(self, config: SEOOptimizationPrompt) -> str:
        """Build keyword optimization strategy"""
        secondary_keywords = config.secondary_keywords or ["Related keywords to be researched"]
        
        return f"""
KEYWORD OPTIMIZATION STRATEGY:

Primary Keyword: "{config.primary_keyword}"
- Target keyword density: 1-2% (natural integration)
- Include in title, H1, first paragraph, and conclusion
- Use in meta description and URL slug
- Include in image alt text where relevant
- Maintain natural, readable flow

Secondary Keywords: {', '.join(secondary_keywords)}
- Integrate naturally throughout content
- Use in subheadings (H2, H3) where appropriate
- Include in supporting paragraphs and examples
- Create semantic keyword variations
- Address related search queries and topics

Long-tail Keyword Strategy:
- Target question-based long-tail variations
- Include conversational phrases for voice search
- Address specific user problems and pain points
- Create content clusters around related topics
- Use location-based keywords if applicable

Semantic SEO:
- Include related terms and synonyms naturally
- Address topic comprehensively with supporting concepts
- Use LSI (Latent Semantic Indexing) keywords
- Create topical authority through comprehensive coverage
- Include industry terminology and jargon appropriately

Keyword Distribution:
- Front-load important keywords in titles and headings
- Distribute keywords evenly throughout content
- Use keywords in anchor text for internal links
- Include keywords in image file names and captions
- Optimize for featured snippet keyword patterns"""

    def _build_content_structure(self, config: SEOOptimizationPrompt, content_specs: Dict) -> str:
        """Build SEO-optimized content structure"""
        return f"""
SEO CONTENT STRUCTURE:

Title Tag Optimization:
- Length: {content_specs.get('title_length', '50-60 characters')}
- Include primary keyword at the beginning
- Create compelling, click-worthy titles
- Include emotional triggers or numbers where appropriate
- Ensure uniqueness across the website

Header Structure (H1-H6):
- H1: One per page, include primary keyword
- H2: {content_specs.get('h2_count', '3-6')} headers, include secondary keywords
- H3-H6: Support content hierarchy and readability
- Use descriptive, keyword-rich headers
- Maintain logical content flow and structure

Meta Description:
- Length: {content_specs.get('meta_description', '150-160 characters')}
- Include primary keyword naturally
- Create compelling copy that encourages clicks
- Include a clear value proposition
- Use action words and urgency where appropriate

Content Organization:
- Introduction: Hook + keyword + preview of content
- Body: Logical sections with keyword-rich subheadings
- Conclusion: Summary + call-to-action + keyword reinforcement
- Use bullet points and numbered lists for readability
- Include FAQ section if targeting featured snippets

Internal Linking:
- {content_specs.get('internal_links', '3-5')} relevant internal links
- Use descriptive, keyword-rich anchor text
- Link to related content and category pages
- Create topic clusters and content silos
- Include links to conversion pages where appropriate

External Linking:
- {content_specs.get('external_links', '2-3')} authoritative external links
- Link to credible, high-authority sources
- Use relevant anchor text for outbound links
- Include nofollow attributes where appropriate
- Support content credibility and E-A-T signals"""

    def _build_technical_seo(self, config: SEOOptimizationPrompt) -> str:
        """Build technical SEO requirements"""
        schema_markup = config.schema_markup_requirements or ["Article", "Organization"]
        technical_reqs = config.technical_requirements or ["Core Web Vitals optimization"]
        
        return f"""
TECHNICAL SEO REQUIREMENTS:

Core Web Vitals Optimization:
- Largest Contentful Paint (LCP): < 2.5 seconds
- First Input Delay (FID): < 100 milliseconds
- Cumulative Layout Shift (CLS): < 0.1
- Optimize images and implement lazy loading
- Minimize JavaScript and CSS blocking

Mobile Optimization:
- Responsive design for all screen sizes
- Touch-friendly navigation and buttons
- Fast mobile loading speeds
- Readable fonts and appropriate sizing
- Mobile-first indexing optimization

Schema Markup Implementation:
{chr(10).join([f"- {schema}" for schema in schema_markup])}
- Implement structured data for rich snippets
- Use JSON-LD format for schema markup
- Test with Google's Rich Results Test
- Include breadcrumb schema for navigation

URL Optimization:
- Include primary keyword in URL slug
- Use hyphens to separate words
- Keep URLs short and descriptive
- Implement proper URL structure and hierarchy
- Use canonical tags to prevent duplicate content

Technical Requirements:
{chr(10).join([f"- {req}" for req in technical_reqs])}
- Implement SSL certificate (HTTPS)
- Create and submit XML sitemap
- Optimize robots.txt file
- Use proper heading hierarchy
- Implement breadcrumb navigation

Page Speed Optimization:
- Compress and optimize images
- Minimize HTTP requests
- Use browser caching and CDN
- Optimize CSS and JavaScript delivery
- Monitor and improve loading speeds regularly"""

    def _build_on_page_optimization(self, config: SEOOptimizationPrompt) -> str:
        """Build on-page SEO optimization"""
        return f"""
ON-PAGE SEO OPTIMIZATION:

Content Quality Factors:
- Create comprehensive, in-depth content
- Ensure factual accuracy and credibility
- Include original research and insights
- Use current, up-to-date information
- Provide unique value and perspective

E-A-T Optimization (Expertise, Authoritativeness, Trustworthiness):
- Demonstrate subject matter expertise
- Include author bio and credentials
- Link to authoritative sources and studies
- Include contact information and about page
- Display social proof and testimonials

Image Optimization:
- Use descriptive, keyword-rich file names
- Include alt text for all images
- Optimize image sizes and formats (WebP when possible)
- Implement image lazy loading
- Include captions where appropriate

Content Freshness:
- Keep content updated with current information
- Add publication and last updated dates
- Include recent examples and case studies
- Monitor and refresh outdated content
- Implement content maintenance schedule

User Engagement Signals:
- Create compelling, engaging content
- Use clear, scannable formatting
- Include interactive elements where appropriate
- Encourage comments and social sharing
- Optimize for time on page and low bounce rate

Local SEO Optimization (if applicable):
- Include location-based keywords naturally
- Add business address and contact information
- Include local landmarks and references
- Optimize for "near me" searches
- Create location-specific content where relevant"""

    def _build_user_experience(self, config: SEOOptimizationPrompt) -> str:
        """Build user experience optimization"""
        return f"""
USER EXPERIENCE OPTIMIZATION:

Content Readability:
- Use short paragraphs (2-3 sentences max)
- Include bullet points and numbered lists
- Use subheadings to break up content
- Maintain 8th-grade reading level
- Include white space for visual breathing room

Navigation and Structure:
- Implement clear, logical navigation
- Include breadcrumb navigation
- Use descriptive menu labels
- Create intuitive user journey paths
- Include search functionality

Accessibility Optimization:
- Use proper heading hierarchy (H1-H6)
- Include alt text for all images
- Ensure sufficient color contrast
- Make content keyboard navigable
- Use descriptive link text

Visual Design:
- Use clean, professional design
- Include relevant, high-quality images
- Implement consistent branding
- Optimize for visual hierarchy
- Create mobile-friendly layouts

Loading Speed:
- Optimize for fast loading times
- Compress images and files
- Minimize redirects and broken links
- Use efficient hosting and CDN
- Monitor Core Web Vitals regularly

Conversion Optimization:
- Include clear calls-to-action
- Use contrasting colors for CTA buttons
- Place CTAs strategically throughout content
- Remove friction from conversion process
- A/B test different CTA variations"""

    def _build_conversion_optimization(self, config: SEOOptimizationPrompt) -> str:
        """Build conversion optimization strategy"""
        conversion_goals = config.conversion_goals or ["Email signups", "Content engagement"]
        
        return f"""
CONVERSION OPTIMIZATION STRATEGY:

Conversion Goals: {', '.join(conversion_goals)}

Call-to-Action Strategy:
- Include multiple CTAs throughout content
- Use action-oriented, compelling language
- Create urgency and scarcity where appropriate
- A/B test different CTA placements and copy
- Ensure CTAs are mobile-friendly

Lead Magnets:
- Offer valuable content upgrades
- Create downloadable resources related to content
- Include email capture forms strategically
- Provide exclusive content for subscribers
- Use exit-intent popups appropriately

Trust Signals:
- Include customer testimonials and reviews
- Display security badges and certifications
- Show social proof and user counts
- Include contact information and support
- Use professional design and branding

Content Funnel:
- Create awareness-stage content for discovery
- Include consideration-stage comparisons and guides
- Develop decision-stage content with clear CTAs
- Nurture leads through email sequences
- Track user journey and optimize touchpoints

Monetization Integration:
- Include relevant product/service mentions
- Create content that demonstrates value
- Use affiliate links where appropriate and disclosed
- Build audience for future monetization
- Establish authority for premium offerings

Analytics and Testing:
- Set up conversion tracking in Google Analytics
- Monitor user behavior with heatmaps
- A/B test headlines, CTAs, and content structure
- Track keyword rankings and organic traffic
- Measure ROI from organic search efforts"""

    def _build_competitive_analysis(self, config: SEOOptimizationPrompt) -> str:
        """Build competitive analysis strategy"""
        competitors = config.competitor_analysis or ["Top ranking competitors for target keywords"]
        
        return f"""
COMPETITIVE ANALYSIS STRATEGY:

Target Competitors: {', '.join(competitors)}

Content Gap Analysis:
- Identify topics competitors are ranking for
- Find content gaps and opportunities
- Analyze competitor content depth and quality
- Discover untapped keyword opportunities
- Create better, more comprehensive content

SERP Analysis:
- Study top 10 results for target keywords
- Analyze competitor title tags and meta descriptions
- Review competitor content structure and length
- Identify common ranking factors
- Find opportunities for differentiation

Backlink Analysis:
- Research competitor backlink profiles
- Identify high-authority linking opportunities
- Find broken link building opportunities
- Analyze competitor content that attracts links
- Develop link-worthy content strategies

Technical SEO Comparison:
- Analyze competitor site speed and performance
- Review competitor schema markup usage
- Compare mobile optimization and UX
- Study competitor internal linking strategies
- Identify technical advantages and opportunities

Content Strategy Insights:
- Analyze competitor content publishing frequency
- Study competitor social media integration
- Review competitor conversion strategies
- Identify competitor weaknesses to exploit
- Develop unique value propositions

Differentiation Strategy:
- Create more comprehensive, higher-quality content
- Include unique insights and original research
- Develop better user experience and design
- Provide more value and actionable advice
- Build stronger E-A-T signals than competitors"""

    def _build_measurement_tracking(self, config: SEOOptimizationPrompt) -> str:
        """Build measurement and tracking strategy"""
        return f"""
MEASUREMENT AND TRACKING STRATEGY:

Key Performance Indicators (KPIs):
- Organic traffic growth and quality
- Keyword ranking positions and visibility
- Click-through rates from search results
- Time on page and engagement metrics
- Conversion rates from organic traffic

Google Analytics Setup:
- Track organic traffic and user behavior
- Set up conversion goals and funnels
- Monitor page performance and user journey
- Track mobile vs desktop performance
- Measure content engagement and retention

Google Search Console Monitoring:
- Track keyword rankings and impressions
- Monitor click-through rates and positions
- Identify crawl errors and technical issues
- Track search queries and content performance
- Optimize for featured snippets and rich results

SEO Tools Integration:
- Use SEMrush/Ahrefs for keyword tracking
- Monitor backlinks and domain authority
- Track competitor performance and rankings
- Analyze SERP features and opportunities
- Set up alerts for ranking changes

Content Performance Metrics:
- Track social shares and engagement
- Monitor time on page and scroll depth
- Measure return visitors and brand searches
- Analyze content that generates backlinks
- Track email signups and lead generation

ROI Measurement:
- Calculate cost per acquisition from organic traffic
- Measure lifetime value of organic visitors
- Track revenue attribution to SEO efforts
- Compare organic performance to paid channels
- Demonstrate SEO ROI and business impact

Continuous Optimization:
- Regular content audits and updates
- Monthly keyword ranking reviews
- Quarterly competitor analysis
- Technical SEO health checks
- Content gap analysis and planning"""

    def _combine_prompt_components(self, components: Dict[str, str]) -> str:
        """Combine all prompt components into final prompt"""
        return f"""{components['system_prompt']}

{components['user_prompt']}

{components['keyword_optimization']}

{components['content_structure']}

{components['technical_seo']}

{components['on_page_optimization']}

{components['user_experience']}

{components['conversion_optimization']}

{components['competitive_analysis']}

{components['measurement_tracking']}

Now create comprehensive SEO-optimized content following all these guidelines. Include all technical requirements, optimization strategies, and conversion elements while maintaining natural readability and user value."""

    def _generate_metadata(self, config: SEOOptimizationPrompt) -> Dict[str, Any]:
        """Generate metadata for the SEO optimization"""
        return {
            "template_version": self.template_version,
            "content_type": config.content_type.value,
            "primary_keyword": config.primary_keyword,
            "secondary_keywords_count": len(config.secondary_keywords),
            "search_intent": config.search_intent.value,
            "competition_level": config.competition_level.value,
            "target_length": config.target_length,
            "local_seo_enabled": config.local_seo_focus,
            "voice_search_optimized": config.voice_search_optimization,
            "featured_snippet_target": config.featured_snippet_target,
            "mobile_optimized": config.mobile_optimization,
            "schema_markup_count": len(config.schema_markup_requirements),
            "conversion_goals_count": len(config.conversion_goals),
            "competitor_count": len(config.competitor_analysis),
            "creation_timestamp": datetime.now().isoformat(),
            "creator_economy_optimized": True
        }

    def _calculate_seo_score(self, config: SEOOptimizationPrompt) -> float:
        """Calculate SEO optimization score"""
        score = 0.4  # Base score
        
        # Add points for optimization elements
        if config.secondary_keywords:
            score += 0.1
        if config.target_audience:
            score += 0.05
        if config.conversion_goals:
            score += 0.1
        if config.competitor_analysis:
            score += 0.1
        if config.schema_markup_requirements:
            score += 0.1
        if config.featured_snippet_target:
            score += 0.05
        if config.voice_search_optimization:
            score += 0.05
        if config.internal_linking_strategy:
            score += 0.05
        
        return min(score, 1.0)

    def _analyze_competition(self, config: SEOOptimizationPrompt) -> Dict[str, Any]:
        """Analyze competition level and strategy"""
        return {
            "level": config.competition_level.value,
            "strategy": self._get_competition_strategy(config.competition_level),
            "keyword_difficulty": self._estimate_keyword_difficulty(config.competition_level),
            "content_requirements": self._get_content_requirements(config.competition_level),
            "ranking_timeline": self._estimate_ranking_timeline(config.competition_level)
        }

    def _estimate_ranking_potential(self, config: SEOOptimizationPrompt) -> str:
        """Estimate ranking potential based on configuration"""
        score = self._calculate_seo_score(config)
        
        # Adjust for competition level
        if config.competition_level == CompetitionLevel.LOW:
            score += 0.1
        elif config.competition_level == CompetitionLevel.HIGH:
            score -= 0.1
        elif config.competition_level == CompetitionLevel.VERY_HIGH:
            score -= 0.2
            
        if score >= 0.8:
            return "Excellent"
        elif score >= 0.6:
            return "Good"
        elif score >= 0.4:
            return "Fair"
        else:
            return "Challenging"

    def _generate_technical_checklist(self, config: SEOOptimizationPrompt) -> List[str]:
        """Generate technical SEO checklist"""
        checklist = [
            "Optimize title tag with primary keyword",
            "Write compelling meta description",
            "Use proper header hierarchy (H1-H6)",
            "Include alt text for all images",
            "Implement schema markup",
            "Optimize URL slug with keyword",
            "Ensure mobile responsiveness",
            "Optimize Core Web Vitals",
            "Add internal and external links",
            "Include keyword-rich content"
        ]
        
        if config.local_seo_focus:
            checklist.extend([
                "Include location-based keywords",
                "Add business address and contact info",
                "Optimize for local search terms"
            ])
            
        if config.voice_search_optimization:
            checklist.extend([
                "Include conversational long-tail keywords",
                "Answer common questions",
                "Optimize for featured snippets"
            ])
            
        return checklist

    def _get_competition_strategy(self, level: CompetitionLevel) -> str:
        """Get strategy based on competition level"""
        strategies = {
            CompetitionLevel.LOW: "Target primary keyword directly with comprehensive content",
            CompetitionLevel.MEDIUM: "Create exceptional content with strong E-A-T signals",
            CompetitionLevel.HIGH: "Focus on long-tail variations and content clusters",
            CompetitionLevel.VERY_HIGH: "Build authority through topic clusters and expert content"
        }
        return strategies[level]

    def _estimate_keyword_difficulty(self, level: CompetitionLevel) -> str:
        """Estimate keyword difficulty score"""
        difficulties = {
            CompetitionLevel.LOW: "10-30 (Easy)",
            CompetitionLevel.MEDIUM: "30-50 (Medium)",
            CompetitionLevel.HIGH: "50-70 (Hard)",
            CompetitionLevel.VERY_HIGH: "70+ (Very Hard)"
        }
        return difficulties[level]

    def _get_content_requirements(self, level: CompetitionLevel) -> str:
        """Get content requirements based on competition"""
        requirements = {
            CompetitionLevel.LOW: "1000-1500 words, basic optimization",
            CompetitionLevel.MEDIUM: "1500-2500 words, comprehensive coverage",
            CompetitionLevel.HIGH: "2500-4000 words, expert-level content",
            CompetitionLevel.VERY_HIGH: "3000+ words, industry-leading quality"
        }
        return requirements[level]

    def _estimate_ranking_timeline(self, level: CompetitionLevel) -> str:
        """Estimate ranking timeline based on competition"""
        timelines = {
            CompetitionLevel.LOW: "1-3 months",
            CompetitionLevel.MEDIUM: "3-6 months", 
            CompetitionLevel.HIGH: "6-12 months",
            CompetitionLevel.VERY_HIGH: "12+ months"
        }
        return timelines[level]

# Example usage and testing
if __name__ == "__main__":
    # Example configuration
    config = SEOOptimizationPrompt(
        content_type=ContentType.BLOG_POST,
        primary_keyword="content creator SEO strategy",
        secondary_keywords=["creator economy SEO", "influencer SEO tips", "social media SEO"],
        search_intent=SearchIntent.EDUCATIONAL,
        target_audience="content creators and digital entrepreneurs",
        competition_level=CompetitionLevel.MEDIUM,
        target_length=2500,
        business_type="Creator economy education",
        industry="Digital marketing and content creation",
        brand_name="Creator SEO Academy",
        unique_selling_proposition="SEO strategies specifically for content creators",
        conversion_goals=["email signups", "course enrollments", "consultation bookings"],
        competitor_analysis=["Neil Patel blog", "HubSpot Academy", "Creator Economy Report"],
        seasonal_factors="Higher interest during January (New Year content planning)",
        technical_requirements=["Core Web Vitals optimization", "Mobile-first design"],
        content_clusters=["SEO fundamentals", "Creator tools", "Monetization strategies"],
        internal_linking_strategy="Topic cluster model with pillar pages",
        external_authority_sources=["Google Webmaster Guidelines", "Search Engine Journal"],
        featured_snippet_target=True,
        local_seo_focus=False,
        mobile_optimization=True,
        voice_search_optimization=True,
        schema_markup_requirements=["Article", "Person", "Organization", "FAQ"]
    )
    
    # Generate prompt
    template = SEOOptimizationTemplate()
    result = template.generate_prompt(config)
    
    print("=== SEO OPTIMIZATION TEMPLATE EXAMPLE ===")
    print(f"SEO Score: {result['optimization_score']:.2f}")
    print(f"Ranking Potential: {result['ranking_potential']}")
    print(f"Competition Analysis: {result['competition_analysis']}")
    print(f"Technical Checklist Items: {len(result['technical_checklist'])}")
    print("\n" + "="*50)
    print(result['prompt'])