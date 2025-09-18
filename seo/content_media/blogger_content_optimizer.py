"""Blogger Content Optimizer
Advanced SEO optimization specialized for bloggers and content creators.

Features:
- Blog post SEO optimization
- Content readability analysis
- Keyword optimization engine
- Featured snippet optimization
- Content structure enhancement
- Social media integration SEO
- Blog monetization SEO
- Content series/campaign optimization

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie

Author: Fahed Mlaiel (mlaiel@live.de)
Expertise: Lead Dev IA + Content Strategy Expert + SEO Specialist + Blogger Growth Expert
"""

import asyncio
import logging
import re
import hashlib
from typing import Dict, List, Optional, Tuple, Any, Union, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
from pathlib import Path
import statistics

try:
    from transformers import pipeline
    import requests
    from bs4 import BeautifulSoup
    import nltk
    from nltk.sentiment import SentimentIntensityAnalyzer
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize, sent_tokenize
    from textstat import flesch_reading_ease, flesch_kincaid_grade
    import yake
    from wordcloud import WordCloud
    import matplotlib.pyplot as plt
    from collections import Counter
    import spacy
except ImportError as e:
    logging.warning(f"Optional blogger content dependencies not available: {e}")

logger = logging.getLogger(__name__)


class BlogContentType(Enum):
    """Types of blog content for specialized optimization."""
    TUTORIAL = "tutorial"
    REVIEW = "review"
    LISTICLE = "listicle"
    OPINION = "opinion"
    NEWS = "news"
    INTERVIEW = "interview"
    CASE_STUDY = "case_study"
    HOW_TO = "how_to"
    COMPARISON = "comparison"
    ROUNDUP = "roundup"
    PERSONAL_STORY = "personal_story"
    RESOURCE_LIST = "resource_list"
    GUEST_POST = "guest_post"
    VIDEO_TRANSCRIPT = "video_transcript"
    PODCAST_NOTES = "podcast_notes"


class BlogNiche(Enum):
    """Blog niches for targeted SEO optimization."""
    TECHNOLOGY = "technology"
    LIFESTYLE = "lifestyle"
    BUSINESS = "business"
    HEALTH = "health"
    FITNESS = "fitness"
    TRAVEL = "travel"
    FOOD = "food"
    FASHION = "fashion"
    BEAUTY = "beauty"
    FINANCE = "finance"
    EDUCATION = "education"
    PARENTING = "parenting"
    DIY = "diy"
    PHOTOGRAPHY = "photography"
    MARKETING = "marketing"
    PRODUCTIVITY = "productivity"
    PERSONAL_DEVELOPMENT = "personal_development"
    ENTERTAINMENT = "entertainment"
    GAMING = "gaming"
    SPORTS = "sports"


class ContentReadabilityLevel(Enum):
    """Content readability levels."""
    VERY_EASY = "very_easy"  # 90-100
    EASY = "easy"  # 80-89
    FAIRLY_EASY = "fairly_easy"  # 70-79
    STANDARD = "standard"  # 60-69
    FAIRLY_DIFFICULT = "fairly_difficult"  # 50-59
    DIFFICULT = "difficult"  # 30-49
    VERY_DIFFICULT = "very_difficult"  # 0-29


class SEODifficulty(Enum):
    """SEO keyword difficulty levels."""
    VERY_LOW = "very_low"  # 0-20
    LOW = "low"  # 21-40
    MEDIUM = "medium"  # 41-60
    HIGH = "high"  # 61-80
    VERY_HIGH = "very_high"  # 81-100


@dataclass
class BlogPost:
    """Comprehensive blog post data structure."""
    title: str
    content: str
    url: Optional[str] = None
    meta_description: Optional[str] = None
    author: Optional[str] = None
    publish_date: Optional[datetime] = None
    category: Optional[BlogNiche] = None
    content_type: Optional[BlogContentType] = None
    target_keywords: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    featured_image: Optional[str] = None
    word_count: Optional[int] = None
    reading_time: Optional[int] = None
    internal_links: List[str] = field(default_factory=list)
    external_links: List[str] = field(default_factory=list)
    images: List[str] = field(default_factory=list)
    social_shares: Dict[str, int] = field(default_factory=dict)
    comments_count: Optional[int] = None
    engagement_rate: Optional[float] = None


@dataclass
class KeywordAnalysis:
    """Keyword analysis results."""
    keyword: str
    search_volume: Optional[int] = None
    difficulty: Optional[SEODifficulty] = None
    cpc: Optional[float] = None
    competition: Optional[float] = None
    related_keywords: List[str] = field(default_factory=list)
    long_tail_variations: List[str] = field(default_factory=list)
    user_intent: Optional[str] = None
    seasonal_trends: Dict[str, float] = field(default_factory=dict)
    serp_features: List[str] = field(default_factory=list)


@dataclass
class ContentStructure:
    """Content structure analysis."""
    headings: Dict[str, List[str]] = field(default_factory=dict)  # h1, h2, h3, etc.
    paragraphs_count: int = 0
    sentences_count: int = 0
    avg_paragraph_length: float = 0.0
    avg_sentence_length: float = 0.0
    bullet_points: int = 0
    numbered_lists: int = 0
    tables: int = 0
    code_blocks: int = 0
    quotes: int = 0
    has_table_of_contents: bool = False
    has_conclusion: bool = False
    has_call_to_action: bool = False


@dataclass
class ReadabilityAnalysis:
    """Content readability analysis results."""
    flesch_reading_ease: float
    flesch_kincaid_grade: float
    readability_level: ContentReadabilityLevel
    avg_words_per_sentence: float
    avg_syllables_per_word: float
    complex_words_percentage: float
    passive_voice_percentage: float
    sentence_variety_score: float
    transition_words_count: int
    readability_suggestions: List[str] = field(default_factory=list)


@dataclass
class SEOAnalysis:
    """Comprehensive SEO analysis results."""
    title_seo_score: float
    meta_description_score: float
    content_seo_score: float
    keyword_density: Dict[str, float] = field(default_factory=dict)
    keyword_distribution: Dict[str, List[int]] = field(default_factory=dict)
    heading_optimization: Dict[str, float] = field(default_factory=dict)
    internal_linking_score: float = 0.0
    external_linking_score: float = 0.0
    image_seo_score: float = 0.0
    featured_snippet_potential: float = 0.0
    overall_seo_score: float = 0.0
    seo_recommendations: List[str] = field(default_factory=list)


@dataclass
class BlogOptimizationResult:
    """Complete blog optimization results."""
    original_post: BlogPost
    keyword_analysis: Dict[str, KeywordAnalysis]
    content_structure: ContentStructure
    readability_analysis: ReadabilityAnalysis
    seo_analysis: SEOAnalysis
    optimized_title: str
    optimized_meta_description: str
    optimized_content: str
    suggested_tags: List[str]
    content_calendar_suggestions: List[str]
    monetization_opportunities: List[str]
    social_media_strategy: Dict[str, List[str]]
    competitor_insights: Dict[str, Any]
    performance_predictions: Dict[str, float]
    timestamp: datetime = field(default_factory=datetime.now)


class BloggerContentOptimizer:
    """Advanced content optimizer specialized for bloggers and content creators.
    
    Provides comprehensive SEO optimization, readability analysis, and content 
    strategy recommendations for maximum blog performance.
    """
    
    def __init__(self, 
                 enable_ai_enhancement: bool = True,
                 api_keys: Dict[str, str] = None):
        """Initialize Blogger Content Optimizer.
        
        Args:
            enable_ai_enhancement: Enable AI-powered content enhancements
            api_keys: Dictionary containing API keys for various services
        """
        self.enable_ai_enhancement = enable_ai_enhancement
        self.api_keys = api_keys or {}
        
        # Initialize AI models if available
        self.text_classifier = None
        self.sentiment_analyzer = None
        self.summarizer = None
        self.question_answerer = None
        
        if enable_ai_enhancement:
            try:
                self.text_classifier = pipeline("zero-shot-classification")
                self.sentiment_analyzer = pipeline("sentiment-analysis")
                self.summarizer = pipeline("summarization", max_length=130, min_length=30)
                self.question_answerer = pipeline("question-answering")
            except Exception as e:
                logger.warning(f"AI models not available: {e}")
        
        # Initialize NLTK components
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('vader_lexicon', quiet=True)
            self.sentiment_analyzer_nltk = SentimentIntensityAnalyzer()
            self.stop_words = set(stopwords.words('english'))
        except Exception as e:
            logger.warning(f"NLTK components not available: {e}")
            self.sentiment_analyzer_nltk = None
            self.stop_words = set()
        
        # SEO and content optimization parameters
        self.seo_keywords = {
            "high_value": ["ultimate guide", "complete tutorial", "step by step", "how to", "best practices"],
            "engagement": ["amazing", "incredible", "proven", "secret", "exclusive", "free"],
            "urgency": ["now", "today", "immediately", "quickly", "instant", "fast"],
            "authority": ["expert", "professional", "advanced", "master", "comprehensive"],
            "numbers": ["top 10", "5 ways", "7 tips", "3 methods", "100%", "2025"]
        }
        
        self.content_patterns = {
            "listicle_triggers": ["ways to", "tips for", "methods to", "strategies for", "reasons why"],
            "tutorial_triggers": ["how to", "step by step", "guide to", "tutorial", "learn"],
            "comparison_triggers": ["vs", "versus", "compared to", "better than", "difference between"],
            "review_triggers": ["review", "honest opinion", "pros and cons", "rating", "experience"]
        }
        
        logger.info("Blogger Content Optimizer initialized successfully")
    
    async def optimize_blog_post(self, 
                               blog_post: BlogPost,
                               target_keywords: List[str] = None,
                               competitor_urls: List[str] = None) -> BlogOptimizationResult:
        """Optimize a complete blog post for SEO and engagement.
        
        Args:
            blog_post: Blog post to optimize
            target_keywords: Primary keywords to target
            competitor_urls: Competitor URLs for analysis
            
        Returns:
            BlogOptimizationResult with comprehensive optimization data
        """
        try:
            # Update target keywords if provided
            if target_keywords:
                blog_post.target_keywords = target_keywords
            
            # Analyze keywords
            keyword_analysis = await self._analyze_keywords(blog_post.target_keywords)
            
            # Analyze content structure
            content_structure = self._analyze_content_structure(blog_post.content)
            
            # Analyze readability
            readability_analysis = self._analyze_readability(blog_post.content)
            
            # Perform SEO analysis
            seo_analysis = await self._analyze_seo(blog_post)
            
            # Generate optimized content
            optimized_title = await self._optimize_title(blog_post, keyword_analysis)
            optimized_meta_description = await self._optimize_meta_description(blog_post, keyword_analysis)
            optimized_content = await self._optimize_content(blog_post, keyword_analysis, seo_analysis)
            
            # Generate suggestions and strategies
            suggested_tags = await self._generate_content_tags(blog_post, keyword_analysis)
            content_calendar = await self._generate_content_calendar_suggestions(blog_post)
            monetization_opportunities = self._identify_monetization_opportunities(blog_post)
            social_media_strategy = await self._create_social_media_strategy(blog_post)
            
            # Analyze competitors if URLs provided
            competitor_insights = {}
            if competitor_urls:
                competitor_insights = await self._analyze_competitors(competitor_urls, blog_post.target_keywords)
            
            # Predict performance
            performance_predictions = self._predict_content_performance(
                blog_post, seo_analysis, readability_analysis
            )
            
            return BlogOptimizationResult(
                original_post=blog_post,
                keyword_analysis=keyword_analysis,
                content_structure=content_structure,
                readability_analysis=readability_analysis,
                seo_analysis=seo_analysis,
                optimized_title=optimized_title,
                optimized_meta_description=optimized_meta_description,
                optimized_content=optimized_content,
                suggested_tags=suggested_tags,
                content_calendar_suggestions=content_calendar,
                monetization_opportunities=monetization_opportunities,
                social_media_strategy=social_media_strategy,
                competitor_insights=competitor_insights,
                performance_predictions=performance_predictions
            )
            
        except Exception as e:
            logger.error(f"Error optimizing blog post: {e}")
            raise
    
    async def analyze_content_gap(self, 
                                niche: BlogNiche,
                                competitor_urls: List[str],
                                target_keywords: List[str]) -> Dict[str, Any]:
        """Analyze content gaps in a specific niche.
        
        Args:
            niche: Blog niche to analyze
            competitor_urls: List of competitor URLs
            target_keywords: Keywords to analyze gaps for
            
        Returns:
            Dictionary with content gap analysis
        """
        try:
            gap_analysis = {
                "missing_topics": [],
                "underperforming_content": [],
                "content_opportunities": [],
                "keyword_gaps": [],
                "format_gaps": [],
                "competitor_strengths": {},
                "recommended_content": []
            }
            
            # Analyze competitor content
            competitor_content = {}
            for url in competitor_urls:
                try:
                    content_data = await self._scrape_competitor_content(url)
                    competitor_content[url] = content_data
                except Exception as e:
                    logger.warning(f"Failed to analyze competitor {url}: {e}")
            
            # Identify content gaps
            if competitor_content:
                gap_analysis = await self._identify_content_gaps(
                    competitor_content, target_keywords, niche
                )
            
            return gap_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing content gap: {e}")
            return {}
    
    async def generate_content_series(self, 
                                    main_topic: str,
                                    target_audience: str,
                                    series_length: int = 5) -> Dict[str, Any]:
        """Generate a complete content series strategy.
        
        Args:
            main_topic: Main topic for the series
            target_audience: Target audience description
            series_length: Number of posts in the series
            
        Returns:
            Dictionary with complete content series plan
        """
        try:
            series_plan = {
                "series_title": f"The Complete {main_topic} Guide Series",
                "series_description": "",
                "posts": [],
                "content_calendar": {},
                "cross_linking_strategy": {},
                "social_promotion_plan": {},
                "lead_magnets": [],
                "monetization_strategy": {}
            }
            
            # Generate series description
            series_plan["series_description"] = await self._generate_series_description(
                main_topic, target_audience
            )
            
            # Generate individual posts
            for i in range(series_length):
                post_plan = await self._generate_series_post_plan(
                    main_topic, target_audience, i + 1, series_length
                )
                series_plan["posts"].append(post_plan)
            
            # Create content calendar
            series_plan["content_calendar"] = self._create_series_calendar(series_plan["posts"])
            
            # Plan cross-linking strategy
            series_plan["cross_linking_strategy"] = self._plan_series_cross_linking(series_plan["posts"])
            
            # Create social promotion plan
            series_plan["social_promotion_plan"] = await self._create_series_social_plan(series_plan)
            
            # Generate lead magnets
            series_plan["lead_magnets"] = self._generate_series_lead_magnets(main_topic)
            
            # Create monetization strategy
            series_plan["monetization_strategy"] = self._create_series_monetization_strategy(
                main_topic, target_audience
            )
            
            return series_plan
            
        except Exception as e:
            logger.error(f"Error generating content series: {e}")
            return {}
    
    # Private helper methods
    
    async def _analyze_keywords(self, keywords: List[str]) -> Dict[str, KeywordAnalysis]:
        """Analyze keywords for SEO potential."""
        keyword_analysis = {}
        
        for keyword in keywords:
            try:
                # Extract keyword using YAKE
                kw_extractor = yake.KeywordExtractor(
                    lan="en",
                    n=3,
                    dedupLim=0.7,
                    top=20
                )
                
                # Simulate keyword analysis (would use real API in production)
                analysis = KeywordAnalysis(
                    keyword=keyword,
                    search_volume=self._estimate_search_volume(keyword),
                    difficulty=self._estimate_keyword_difficulty(keyword),
                    cpc=self._estimate_cpc(keyword),
                    competition=self._estimate_competition(keyword),
                    related_keywords=self._find_related_keywords(keyword),
                    long_tail_variations=self._generate_long_tail_variations(keyword),
                    user_intent=self._determine_user_intent(keyword),
                    seasonal_trends=self._analyze_seasonal_trends(keyword),
                    serp_features=self._identify_serp_features(keyword)
                )
                
                keyword_analysis[keyword] = analysis
                
            except Exception as e:
                logger.warning(f"Error analyzing keyword {keyword}: {e}")
                keyword_analysis[keyword] = KeywordAnalysis(keyword=keyword)
        
        return keyword_analysis
    
    def _analyze_content_structure(self, content: str) -> ContentStructure:
        """Analyze content structure and formatting."""
        try:
            # Parse HTML content
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract headings
            headings = {}
            for i in range(1, 7):
                heading_tags = soup.find_all(f'h{i}')
                if heading_tags:
                    headings[f'h{i}'] = [tag.get_text().strip() for tag in heading_tags]
            
            # Count structural elements
            paragraphs = soup.find_all('p')
            bullet_points = len(soup.find_all('ul')) + len(soup.find_all('ol'))
            tables = len(soup.find_all('table'))
            code_blocks = len(soup.find_all('code')) + len(soup.find_all('pre'))
            quotes = len(soup.find_all('blockquote'))
            
            # Analyze text content
            text_content = soup.get_text()
            sentences = sent_tokenize(text_content)
            words = word_tokenize(text_content)
            
            # Calculate averages
            avg_paragraph_length = len(words) / max(len(paragraphs), 1)
            avg_sentence_length = len(words) / max(len(sentences), 1)
            
            # Check for specific elements
            has_toc = bool(soup.find_all(string=re.compile(r'table of contents|contents', re.I)))
            has_conclusion = bool(soup.find_all(string=re.compile(r'conclusion|summary|final thoughts', re.I)))
            has_cta = bool(soup.find_all(string=re.compile(r'subscribe|download|buy now|learn more', re.I)))
            
            return ContentStructure(
                headings=headings,
                paragraphs_count=len(paragraphs),
                sentences_count=len(sentences),
                avg_paragraph_length=avg_paragraph_length,
                avg_sentence_length=avg_sentence_length,
                bullet_points=bullet_points,
                numbered_lists=len(soup.find_all('ol')),
                tables=tables,
                code_blocks=code_blocks,
                quotes=quotes,
                has_table_of_contents=has_toc,
                has_conclusion=has_conclusion,
                has_call_to_action=has_cta
            )
            
        except Exception as e:
            logger.error(f"Error analyzing content structure: {e}")
            return ContentStructure()
    
    def _analyze_readability(self, content: str) -> ReadabilityAnalysis:
        """Analyze content readability."""
        try:
            # Extract text content
            soup = BeautifulSoup(content, 'html.parser')
            text_content = soup.get_text()
            
            # Calculate readability scores
            flesch_ease = flesch_reading_ease(text_content)
            flesch_grade = flesch_kincaid_grade(text_content)
            
            # Determine readability level
            if flesch_ease >= 90:
                readability_level = ContentReadabilityLevel.VERY_EASY
            elif flesch_ease >= 80:
                readability_level = ContentReadabilityLevel.EASY
            elif flesch_ease >= 70:
                readability_level = ContentReadabilityLevel.FAIRLY_EASY
            elif flesch_ease >= 60:
                readability_level = ContentReadabilityLevel.STANDARD
            elif flesch_ease >= 50:
                readability_level = ContentReadabilityLevel.FAIRLY_DIFFICULT
            elif flesch_ease >= 30:
                readability_level = ContentReadabilityLevel.DIFFICULT
            else:
                readability_level = ContentReadabilityLevel.VERY_DIFFICULT
            
            # Analyze text characteristics
            sentences = sent_tokenize(text_content)
            words = word_tokenize(text_content)
            
            avg_words_per_sentence = len(words) / max(len(sentences), 1)
            
            # Count syllables (simplified)
            syllable_count = sum(self._count_syllables(word) for word in words)
            avg_syllables_per_word = syllable_count / max(len(words), 1)
            
            # Calculate complex words percentage
            complex_words = [word for word in words if self._count_syllables(word) >= 3]
            complex_words_percentage = (len(complex_words) / max(len(words), 1)) * 100
            
            # Estimate passive voice percentage (simplified)
            passive_voice_percentage = self._estimate_passive_voice_percentage(text_content)
            
            # Calculate sentence variety score
            sentence_lengths = [len(word_tokenize(sentence)) for sentence in sentences]
            sentence_variety_score = statistics.stdev(sentence_lengths) if len(sentence_lengths) > 1 else 0
            
            # Count transition words
            transition_words = {
                'however', 'therefore', 'furthermore', 'moreover', 'meanwhile', 
                'consequently', 'nevertheless', 'additionally', 'similarly', 'finally'
            }
            transition_words_count = sum(1 for word in words if word.lower() in transition_words)
            
            # Generate readability suggestions
            suggestions = self._generate_readability_suggestions(
                flesch_ease, avg_words_per_sentence, complex_words_percentage
            )
            
            return ReadabilityAnalysis(
                flesch_reading_ease=flesch_ease,
                flesch_kincaid_grade=flesch_grade,
                readability_level=readability_level,
                avg_words_per_sentence=avg_words_per_sentence,
                avg_syllables_per_word=avg_syllables_per_word,
                complex_words_percentage=complex_words_percentage,
                passive_voice_percentage=passive_voice_percentage,
                sentence_variety_score=sentence_variety_score,
                transition_words_count=transition_words_count,
                readability_suggestions=suggestions
            )
            
        except Exception as e:
            logger.error(f"Error analyzing readability: {e}")
            return ReadabilityAnalysis(
                flesch_reading_ease=50.0,
                flesch_kincaid_grade=10.0,
                readability_level=ContentReadabilityLevel.STANDARD,
                avg_words_per_sentence=15.0,
                avg_syllables_per_word=1.5,
                complex_words_percentage=20.0,
                passive_voice_percentage=10.0,
                sentence_variety_score=5.0,
                transition_words_count=5
            )
    
    async def _analyze_seo(self, blog_post: BlogPost) -> SEOAnalysis:
        """Perform comprehensive SEO analysis."""
        try:
            # Analyze title SEO
            title_score = self._analyze_title_seo(blog_post.title, blog_post.target_keywords)
            
            # Analyze meta description SEO
            meta_score = self._analyze_meta_description_seo(
                blog_post.meta_description, blog_post.target_keywords
            )
            
            # Analyze content SEO
            content_score = self._analyze_content_seo(blog_post.content, blog_post.target_keywords)
            
            # Calculate keyword density
            keyword_density = self._calculate_keyword_density(blog_post.content, blog_post.target_keywords)
            
            # Analyze keyword distribution
            keyword_distribution = self._analyze_keyword_distribution(
                blog_post.content, blog_post.target_keywords
            )
            
            # Analyze heading optimization
            heading_optimization = self._analyze_heading_optimization(
                blog_post.content, blog_post.target_keywords
            )
            
            # Analyze internal linking
            internal_linking_score = self._analyze_internal_linking(blog_post.internal_links, blog_post.content)
            
            # Analyze external linking
            external_linking_score = self._analyze_external_linking(blog_post.external_links, blog_post.content)
            
            # Analyze image SEO
            image_seo_score = self._analyze_image_seo(blog_post.images, blog_post.content)
            
            # Assess featured snippet potential
            featured_snippet_potential = self._assess_featured_snippet_potential(
                blog_post.content, blog_post.target_keywords
            )
            
            # Calculate overall SEO score
            overall_score = (
                title_score * 0.20 +
                meta_score * 0.15 +
                content_score * 0.25 +
                internal_linking_score * 0.15 +
                external_linking_score * 0.10 +
                image_seo_score * 0.10 +
                featured_snippet_potential * 0.05
            )
            
            # Generate SEO recommendations
            recommendations = self._generate_seo_recommendations(
                title_score, meta_score, content_score, keyword_density
            )
            
            return SEOAnalysis(
                title_seo_score=title_score,
                meta_description_score=meta_score,
                content_seo_score=content_score,
                keyword_density=keyword_density,
                keyword_distribution=keyword_distribution,
                heading_optimization=heading_optimization,
                internal_linking_score=internal_linking_score,
                external_linking_score=external_linking_score,
                image_seo_score=image_seo_score,
                featured_snippet_potential=featured_snippet_potential,
                overall_seo_score=overall_score,
                seo_recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error performing SEO analysis: {e}")
            return SEOAnalysis(
                title_seo_score=50.0,
                meta_description_score=50.0,
                content_seo_score=50.0,
                overall_seo_score=50.0
            )
    
    # Additional helper methods (simplified for brevity)
    
    def _estimate_search_volume(self, keyword: str) -> int:
        """Estimate search volume for keyword."""
        # Simplified estimation based on keyword length and common patterns
        base_volume = 1000
        if len(keyword.split()) == 1:
            return base_volume * 2
        elif len(keyword.split()) <= 3:
            return base_volume
        else:
            return base_volume // 2
    
    def _estimate_keyword_difficulty(self, keyword: str) -> SEODifficulty:
        """Estimate keyword difficulty."""
        # Simplified heuristic
        word_count = len(keyword.split())
        if word_count == 1:
            return SEODifficulty.VERY_HIGH
        elif word_count <= 3:
            return SEODifficulty.HIGH
        elif word_count <= 5:
            return SEODifficulty.MEDIUM
        else:
            return SEODifficulty.LOW
    
    def _estimate_cpc(self, keyword: str) -> float:
        """Estimate cost per click for keyword."""
        # Simplified estimation
        commercial_keywords = ['buy', 'price', 'cost', 'review', 'best']
        if any(word in keyword.lower() for word in commercial_keywords):
            return 2.50
        return 1.25
    
    def _estimate_competition(self, keyword: str) -> float:
        """Estimate keyword competition (0-1)."""
        # Simplified competition score
        return min(1.0, len(keyword.split()) / 5.0)
    
    def _find_related_keywords(self, keyword: str) -> List[str]:
        """Find related keywords."""
        base_variations = [
            f"how to {keyword}",
            f"best {keyword}",
            f"{keyword} guide",
            f"{keyword} tips",
            f"{keyword} tutorial"
        ]
        return base_variations[:5]
    
    def _generate_long_tail_variations(self, keyword: str) -> List[str]:
        """Generate long-tail keyword variations."""
        variations = [
            f"{keyword} for beginners",
            f"{keyword} step by step",
            f"{keyword} complete guide",
            f"how to {keyword} easily",
            f"{keyword} best practices"
        ]
        return variations[:5]
    
    def _determine_user_intent(self, keyword: str) -> str:
        """Determine user search intent."""
        if any(word in keyword.lower() for word in ['how', 'tutorial', 'guide', 'learn']):
            return "informational"
        elif any(word in keyword.lower() for word in ['buy', 'price', 'cost', 'purchase']):
            return "commercial"
        elif any(word in keyword.lower() for word in ['review', 'vs', 'compare', 'best']):
            return "commercial_investigation"
        else:
            return "navigational"
    
    def _analyze_seasonal_trends(self, keyword: str) -> Dict[str, float]:
        """Analyze seasonal trends for keyword."""
        # Simplified seasonal analysis
        seasonal_keywords = {
            'holiday': {'Dec': 2.0, 'Nov': 1.5, 'Jan': 0.5},
            'fitness': {'Jan': 2.0, 'Feb': 1.8, 'Mar': 1.5},
            'travel': {'Jun': 2.0, 'Jul': 2.0, 'Aug': 1.8},
            'back to school': {'Aug': 2.0, 'Sep': 1.8}
        }
        
        for pattern, trends in seasonal_keywords.items():
            if pattern in keyword.lower():
                return trends
        
        return {'Jan': 1.0, 'Feb': 1.0, 'Mar': 1.0, 'Apr': 1.0, 
                'May': 1.0, 'Jun': 1.0, 'Jul': 1.0, 'Aug': 1.0,
                'Sep': 1.0, 'Oct': 1.0, 'Nov': 1.0, 'Dec': 1.0}
    
    def _identify_serp_features(self, keyword: str) -> List[str]:
        """Identify potential SERP features for keyword."""
        features = []
        
        if any(word in keyword.lower() for word in ['how', 'what', 'why', 'when']):
            features.append("featured_snippet")
        
        if any(word in keyword.lower() for word in ['near me', 'location']):
            features.append("local_pack")
        
        if any(word in keyword.lower() for word in ['image', 'photo', 'picture']):
            features.append("image_pack")
        
        if any(word in keyword.lower() for word in ['video', 'tutorial']):
            features.append("video_results")
        
        return features
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified)."""
        word = word.lower()
        vowels = "aeiouy"
        syllable_count = 0
        previous_char_was_vowel = False
        
        for char in word:
            if char in vowels:
                if not previous_char_was_vowel:
                    syllable_count += 1
                previous_char_was_vowel = True
            else:
                previous_char_was_vowel = False
        
        if word.endswith('e'):
            syllable_count -= 1
        
        return max(1, syllable_count)
    
    def _estimate_passive_voice_percentage(self, text: str) -> float:
        """Estimate percentage of passive voice usage."""
        # Simplified passive voice detection
        passive_indicators = ['was', 'were', 'been', 'being', 'is', 'are', 'am']
        past_participle_endings = ['ed', 'en', 'ne', 'wn', 'ught', 'ung']
        
        sentences = sent_tokenize(text)
        passive_count = 0
        
        for sentence in sentences:
            words = word_tokenize(sentence.lower())
            has_passive_indicator = any(word in passive_indicators for word in words)
            has_past_participle = any(word.endswith(ending) for word in words for ending in past_participle_endings)
            
            if has_passive_indicator and has_past_participle:
                passive_count += 1
        
        return (passive_count / max(len(sentences), 1)) * 100
    
    def _generate_readability_suggestions(self, 
                                        flesch_ease: float,
                                        avg_words_per_sentence: float,
                                        complex_words_percentage: float) -> List[str]:
        """Generate readability improvement suggestions."""
        suggestions = []
        
        if flesch_ease < 60:
            suggestions.append("Consider simplifying sentence structure for better readability")
        
        if avg_words_per_sentence > 20:
            suggestions.append("Break down long sentences to improve readability")
        
        if complex_words_percentage > 15:
            suggestions.append("Replace complex words with simpler alternatives where possible")
        
        suggestions.extend([
            "Use more transition words to improve flow",
            "Add bullet points and subheadings to break up text",
            "Include relevant examples and analogies"
        ])
        
        return suggestions[:5]
    
    # Additional core optimization methods would continue here...
    # Due to length constraints, implementing key structure and main functionality
    
    async def _optimize_title(self, blog_post: BlogPost, keyword_analysis: Dict[str, KeywordAnalysis]) -> str:
        """Optimize blog post title for SEO."""
        try:
            title = blog_post.title
            primary_keyword = blog_post.target_keywords[0] if blog_post.target_keywords else ""
            
            # Add primary keyword if not present
            if primary_keyword and primary_keyword.lower() not in title.lower():
                title = f"{primary_keyword}: {title}"
            
            # Add power words for engagement
            power_words = ["Ultimate", "Complete", "Essential", "Proven", "Expert"]
            if not any(word in title for word in power_words):
                title = f"Complete {title}"
            
            # Optimize length (50-60 characters ideal)
            if len(title) > 60:
                title = title[:57] + "..."
            
            return title
            
        except Exception as e:
            logger.error(f"Error optimizing title: {e}")
            return blog_post.title
    
    async def _optimize_meta_description(self, blog_post: BlogPost, keyword_analysis: Dict[str, KeywordAnalysis]) -> str:
        """Optimize meta description for SEO."""
        try:
            if not blog_post.meta_description:
                # Generate from content
                soup = BeautifulSoup(blog_post.content, 'html.parser')
                text_content = soup.get_text()
                first_paragraph = text_content.split('.')[0]
                meta_description = first_paragraph[:150] + "..."
            else:
                meta_description = blog_post.meta_description
            
            # Ensure primary keyword is included
            primary_keyword = blog_post.target_keywords[0] if blog_post.target_keywords else ""
            if primary_keyword and primary_keyword.lower() not in meta_description.lower():
                meta_description = f"{primary_keyword} - {meta_description}"
            
            # Optimize length (150-160 characters)
            if len(meta_description) > 160:
                meta_description = meta_description[:157] + "..."
            
            return meta_description
            
        except Exception as e:
            logger.error(f"Error optimizing meta description: {e}")
            return blog_post.meta_description or "Read this comprehensive guide..."
    
    async def _optimize_content(self, 
                              blog_post: BlogPost, 
                              keyword_analysis: Dict[str, KeywordAnalysis],
                              seo_analysis: SEOAnalysis) -> str:
        """Optimize blog content for SEO."""
        try:
            content = blog_post.content
            
            # Add missing headings if needed
            if not re.search(r'<h[1-6]', content):
                content = f"<h2>Introduction</h2>{content}"
            
            # Optimize keyword density
            for keyword in blog_post.target_keywords:
                current_density = seo_analysis.keyword_density.get(keyword, 0)
                if current_density < 1.0:  # Less than 1% density
                    # Add keyword naturally in a new paragraph
                    content += f"\n<p>This guide covers everything you need to know about {keyword}.</p>"
            
            # Add call-to-action if missing
            if "subscribe" not in content.lower() and "download" not in content.lower():
                content += "\n<p><strong>Want more content like this? Subscribe to our newsletter for weekly updates!</strong></p>"
            
            return content
            
        except Exception as e:
            logger.error(f"Error optimizing content: {e}")
            return blog_post.content
    
    # Placeholder methods for remaining functionality
    async def _generate_content_tags(self, blog_post: BlogPost, keyword_analysis: Dict[str, KeywordAnalysis]) -> List[str]:
        """Generate relevant content tags."""
        tags = []
        
        # Add keywords as tags
        tags.extend(blog_post.target_keywords)
        
        # Add category-based tags
        if blog_post.category:
            tags.append(blog_post.category.value)
        
        # Add content type tags
        if blog_post.content_type:
            tags.append(blog_post.content_type.value)
        
        # Add trending tags
        tags.extend(["2025", "guide", "tips", "tutorial"])
        
        return list(set(tags))[:10]
    
    def _analyze_title_seo(self, title: str, keywords: List[str]) -> float:
        """Analyze title SEO score."""
        score = 50.0  # Base score
        
        if keywords:
            primary_keyword = keywords[0]
            if primary_keyword.lower() in title.lower():
                score += 30.0
        
        if 50 <= len(title) <= 60:
            score += 20.0
        
        return min(100.0, score)
    
    def _analyze_meta_description_seo(self, meta_description: str, keywords: List[str]) -> float:
        """Analyze meta description SEO score."""
        if not meta_description:
            return 0.0
        
        score = 50.0
        
        if keywords and keywords[0].lower() in meta_description.lower():
            score += 30.0
        
        if 150 <= len(meta_description) <= 160:
            score += 20.0
        
        return min(100.0, score)
    
    def _analyze_content_seo(self, content: str, keywords: List[str]) -> float:
        """Analyze content SEO score."""
        score = 50.0
        
        # Check keyword presence
        for keyword in keywords:
            if keyword.lower() in content.lower():
                score += 10.0
        
        # Check content length
        word_count = len(content.split())
        if word_count >= 1000:
            score += 20.0
        elif word_count >= 500:
            score += 10.0
        
        return min(100.0, score)
    
    def _calculate_keyword_density(self, content: str, keywords: List[str]) -> Dict[str, float]:
        """Calculate keyword density."""
        density = {}
        total_words = len(content.split())
        
        for keyword in keywords:
            keyword_count = content.lower().count(keyword.lower())
            density[keyword] = (keyword_count / total_words) * 100 if total_words > 0 else 0
        
        return density