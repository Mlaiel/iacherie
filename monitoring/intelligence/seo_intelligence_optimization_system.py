"""SEO Intelligence Optimization System
====================================

Enterprise-grade SEO Intelligence system providing comprehensive
search optimization, intelligent keyword analytics, and advanced SEO
performance monitoring for the Ainflue Creator Economy. Implements
sophisticated search algorithms, content optimization, and real-time SEO analytics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
ALL RIGHTS RESERVED

🚨 INTELLECTUAL PROPERTY PROTECTION:
- Proprietary code of Fahed Mlaiel
- Commercial use FORBIDDEN without written authorization
- Reverse engineering STRICTLY PROHIBITED
- Distribution FORBIDDEN without explicit license
- Violation = Automatic legal prosecution

🏢 ENTERPRISE USAGE:
- Enterprise license available on request
- Technical support included with license
- Maintenance and updates provided
- Team technical training included
"""

import asyncio
import logging
import json
import time
import uuid
import re
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, deque, Counter
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

# Optional imports for enhanced functionality
try:
    import requests
    from bs4 import BeautifulSoup
    WEB_SCRAPING_AVAILABLE = True
except ImportError:
    WEB_SCRAPING_AVAILABLE = False

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    from nltk.stem import PorterStemmer
    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False

logger = logging.getLogger(__name__)

class ContentType(Enum):
    """Types of content for SEO optimization"""
    BLOG_POST = "blog_post"
    VIDEO = "video"
    PODCAST = "podcast"
    IMAGE = "image"
    SOCIAL_POST = "social_post"
    LANDING_PAGE = "landing_page"
    PRODUCT_PAGE = "product_page"
    PORTFOLIO = "portfolio"
    COURSE = "course"
    EBOOK = "ebook"

class SEOMetricType(Enum):
    """Types of SEO metrics to track"""
    KEYWORD_RANKING = "keyword_ranking"
    ORGANIC_TRAFFIC = "organic_traffic"
    CLICK_THROUGH_RATE = "click_through_rate"
    BOUNCE_RATE = "bounce_rate"
    PAGE_LOAD_SPEED = "page_load_speed"
    BACKLINK_COUNT = "backlink_count"
    DOMAIN_AUTHORITY = "domain_authority"
    PAGE_AUTHORITY = "page_authority"
    SOCIAL_SIGNALS = "social_signals"
    CONTENT_QUALITY_SCORE = "content_quality_score"

class SearchEngine(Enum):
    """Supported search engines"""
    GOOGLE = "google"
    BING = "bing"
    YAHOO = "yahoo"
    DUCKDUCKGO = "duckduckgo"
    YANDEX = "yandex"
    BAIDU = "baidu"

class KeywordDifficulty(Enum):
    """Keyword difficulty levels"""
    VERY_EASY = "very_easy"
    EASY = "easy"
    MODERATE = "moderate"
    HARD = "hard"
    VERY_HARD = "very_hard"

@dataclass
class Keyword:
    """Keyword data structure"""
    keyword: str
    search_volume: int
    difficulty: KeywordDifficulty
    cpc: float = 0.0
    competition: float = 0.0
    trending_score: float = 0.0
    seasonality: Dict[str, float] = field(default_factory=dict)
    related_keywords: List[str] = field(default_factory=list)
    intent: str = "informational"  # informational, commercial, transactional, navigational
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SEOMetric:
    """SEO metric data structure"""
    metric_type: SEOMetricType
    value: float
    timestamp: datetime
    content_id: str
    keyword: Optional[str] = None
    search_engine: SearchEngine = SearchEngine.GOOGLE
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ContentAnalysis:
    """Content SEO analysis result"""
    content_id: str
    content_type: ContentType
    title: str
    description: str
    keywords: List[str]
    readability_score: float
    content_quality_score: float
    seo_score: float
    suggestions: List[str]
    issues: List[str]
    opportunities: List[str]
    word_count: int
    meta_analysis: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class SEORecommendation:
    """SEO optimization recommendation"""
    recommendation_id: str
    content_id: str
    priority: str  # high, medium, low
    category: str
    title: str
    description: str
    implementation_effort: str  # easy, medium, hard
    expected_impact: str  # low, medium, high
    keywords_targeted: List[str] = field(default_factory=list)
    estimated_completion_time: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class CompetitorAnalysis:
    """Competitor SEO analysis"""
    competitor_domain: str
    domain_authority: float
    organic_keywords: int
    organic_traffic: int
    backlinks: int
    top_keywords: List[Dict[str, Any]]
    content_gaps: List[str]
    competitive_advantages: List[str]
    analysis_date: datetime = field(default_factory=datetime.now)

@dataclass
class SEOAuditResult:
    """Comprehensive SEO audit result"""
    audit_id: str
    content_id: str
    overall_score: float
    technical_seo_score: float
    content_seo_score: float
    user_experience_score: float
    issues_found: List[Dict[str, Any]]
    recommendations: List[SEORecommendation]
    audit_date: datetime = field(default_factory=datetime.now)

class SEOIntelligenceOptimizationSystem:
    """Enterprise SEO Intelligence Optimization System
    
    Provides comprehensive SEO optimization, keyword intelligence,
    content analysis, and search performance monitoring for Creator Economy.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize SEO Intelligence Optimization System
        
        Args:
            config: Configuration dictionary for SEO settings
        """
        self.config = config or {}
        self.keywords_database = {}
        self.content_analyses = {}
        self.seo_metrics = defaultdict(list)
        self.recommendations = defaultdict(list)
        self.competitor_data = {}
        self.audit_results = {}
        self.ranking_history = defaultdict(list)
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Initialize NLP components if available
        if NLP_AVAILABLE:
            try:
                nltk.download('punkt', quiet=True)
                nltk.download('stopwords', quiet=True)
                self.stemmer = PorterStemmer()
                self.stop_words = set(stopwords.words('english'))
            except:
                logger.warning("NLTK initialization failed, using fallback methods")
                self.stemmer = None
                self.stop_words = set()
        else:
            self.stemmer = None
            self.stop_words = set()
        
        # SEO scoring weights
        self.scoring_weights = {
            "title_optimization": 0.15,
            "meta_description": 0.10,
            "keyword_density": 0.12,
            "content_length": 0.08,
            "readability": 0.10,
            "internal_links": 0.08,
            "external_links": 0.07,
            "image_optimization": 0.10,
            "page_speed": 0.12,
            "mobile_friendliness": 0.08
        }
        
        # Content optimization templates
        self.content_templates = {
            ContentType.BLOG_POST: {
                "ideal_length": (1500, 3000),
                "keyword_density": (1.0, 3.0),
                "headings_count": (3, 8),
                "internal_links": (2, 5),
                "external_links": (1, 3)
            },
            ContentType.VIDEO: {
                "title_length": (50, 60),
                "description_length": (125, 300),
                "tags_count": (8, 12),
                "keyword_density": (2.0, 4.0)
            },
            ContentType.SOCIAL_POST: {
                "character_limit": 280,
                "hashtags_count": (3, 8),
                "keyword_density": (3.0, 6.0)
            }
        }
        
        logger.info("SEO Intelligence Optimization System initialized successfully")
    
    async def add_keyword(self, keyword: Keyword) -> bool:
        """Add keyword to the database with intelligence data
        
        Args:
            keyword: Keyword object with search data
            
        Returns:
            Success status of keyword addition
        """
        try:
            # Normalize keyword
            normalized_keyword = keyword.keyword.lower().strip()
            
            # Store keyword
            self.keywords_database[normalized_keyword] = keyword
            
            # Generate related keywords if not provided
            if not keyword.related_keywords:
                keyword.related_keywords = await self._generate_related_keywords(normalized_keyword)
            
            logger.info(f"Keyword '{normalized_keyword}' added to database")
            return True
            
        except Exception as e:
            logger.error(f"Error adding keyword: {str(e)}")
            return False
    
    async def analyze_content(self, content_id: str, content: Dict[str, Any]) -> Optional[ContentAnalysis]:
        """Analyze content for SEO optimization opportunities
        
        Args:
            content_id: Unique content identifier
            content: Content data including title, description, body, etc.
            
        Returns:
            Content analysis result
        """
        try:
            # Extract content elements
            title = content.get("title", "")
            description = content.get("description", "")
            body = content.get("body", "")
            content_type = ContentType(content.get("type", "blog_post"))
            
            # Analyze keywords
            keywords = await self._extract_keywords(title + " " + description + " " + body)
            
            # Calculate scores
            readability_score = await self._calculate_readability_score(body)
            content_quality_score = await self._calculate_content_quality_score(content, content_type)
            seo_score = await self._calculate_seo_score(content, keywords, content_type)
            
            # Generate suggestions and identify issues
            suggestions = await self._generate_seo_suggestions(content, keywords, content_type)
            issues = await self._identify_seo_issues(content, content_type)
            opportunities = await self._identify_seo_opportunities(content, keywords)
            
            # Create analysis result
            analysis = ContentAnalysis(
                content_id=content_id,
                content_type=content_type,
                title=title,
                description=description,
                keywords=keywords,
                readability_score=readability_score,
                content_quality_score=content_quality_score,
                seo_score=seo_score,
                suggestions=suggestions,
                issues=issues,
                opportunities=opportunities,
                word_count=len(body.split()) if body else 0,
                meta_analysis=await self._perform_meta_analysis(content)
            )
            
            # Store analysis
            self.content_analyses[content_id] = analysis
            
            # Generate recommendations
            await self._generate_content_recommendations(content_id, analysis)
            
            logger.info(f"Content analysis completed for {content_id} with SEO score: {seo_score:.2f}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing content: {str(e)}")
            return None
    
    async def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text content"""
        if not text:
            return []
        
        # Clean and normalize text
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        
        if NLP_AVAILABLE and self.stemmer:
            try:
                # Use NLTK for advanced keyword extraction
                tokens = word_tokenize(text)
                keywords = [
                    self.stemmer.stem(token) 
                    for token in tokens 
                    if token not in self.stop_words and len(token) > 2
                ]
            except:
                # Fallback to simple extraction
                keywords = self._simple_keyword_extraction(text)
        else:
            keywords = self._simple_keyword_extraction(text)
        
        # Count frequency and return most common
        keyword_counts = Counter(keywords)
        return [keyword for keyword, count in keyword_counts.most_common(20)]
    
    def _simple_keyword_extraction(self, text: str) -> List[str]:
        """Simple keyword extraction fallback"""
        # Basic stop words
        basic_stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
        }
        
        words = text.split()
        keywords = [
            word for word in words 
            if word not in basic_stop_words and len(word) > 2
        ]
        
        return keywords
    
    async def _calculate_readability_score(self, text: str) -> float:
        """Calculate readability score using Flesch Reading Ease approximation"""
        if not text:
            return 0.0
        
        # Count sentences (approximate)
        sentences = len(re.split(r'[.!?]+', text))
        
        # Count words
        words = len(text.split())
        
        # Count syllables (approximate)
        syllables = sum(max(1, len(re.findall(r'[aeiouAEIOU]', word))) for word in text.split())
        
        if sentences == 0 or words == 0:
            return 0.0
        
        # Flesch Reading Ease approximation
        avg_sentence_length = words / sentences
        avg_syllables_per_word = syllables / words
        
        score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        
        # Normalize to 0-100 scale
        return max(0.0, min(100.0, score))
    
    async def _calculate_content_quality_score(self, content: Dict[str, Any], content_type: ContentType) -> float:
        """Calculate content quality score based on various factors"""
        score = 0.0
        max_score = 100.0
        
        title = content.get("title", "")
        description = content.get("description", "")
        body = content.get("body", "")
        
        # Title quality (20 points)
        if title:
            title_length = len(title)
            if 30 <= title_length <= 60:
                score += 20
            elif 20 <= title_length <= 80:
                score += 15
            else:
                score += 5
        
        # Description quality (15 points)
        if description:
            desc_length = len(description)
            if 120 <= desc_length <= 160:
                score += 15
            elif 100 <= desc_length <= 200:
                score += 10
            else:
                score += 5
        
        # Content length (25 points)
        if body:
            word_count = len(body.split())
            template = self.content_templates.get(content_type, {})
            ideal_range = template.get("ideal_length", (1000, 2000))
            
            if ideal_range[0] <= word_count <= ideal_range[1]:
                score += 25
            elif word_count >= ideal_range[0] * 0.7:
                score += 15
            else:
                score += 5
        
        # Content structure (20 points)
        if body:
            # Check for headings
            heading_count = len(re.findall(r'#{1,6}\s', body))  # Markdown headings
            heading_count += len(re.findall(r'<h[1-6]>', body))  # HTML headings
            
            if heading_count >= 3:
                score += 10
            elif heading_count >= 1:
                score += 5
            
            # Check for lists
            list_count = len(re.findall(r'^\s*[-*+]\s', body, re.MULTILINE))
            list_count += len(re.findall(r'^\s*\d+\.\s', body, re.MULTILINE))
            
            if list_count >= 1:
                score += 10
            else:
                score += 5
        
        # Media content (10 points)
        images = content.get("images", [])
        videos = content.get("videos", [])
        
        if images or videos:
            score += 10
        
        # External references (10 points)
        if body:
            external_links = len(re.findall(r'https?://[^\s]+', body))
            if external_links >= 1:
                score += 10
            else:
                score += 5
        
        return min(max_score, score)
    
    async def _calculate_seo_score(
        self, 
        content: Dict[str, Any], 
        keywords: List[str], 
        content_type: ContentType
    ) -> float:
        """Calculate overall SEO score for content"""
        score = 0.0
        
        title = content.get("title", "")
        description = content.get("description", "")
        body = content.get("body", "")
        
        # Title optimization (15%)
        title_score = await self._score_title_optimization(title, keywords)
        score += title_score * self.scoring_weights["title_optimization"]
        
        # Meta description (10%)
        meta_score = await self._score_meta_description(description, keywords)
        score += meta_score * self.scoring_weights["meta_description"]
        
        # Keyword density (12%)
        keyword_score = await self._score_keyword_density(body, keywords)
        score += keyword_score * self.scoring_weights["keyword_density"]
        
        # Content length (8%)
        length_score = await self._score_content_length(body, content_type)
        score += length_score * self.scoring_weights["content_length"]
        
        # Readability (10%)
        readability_score = await self._calculate_readability_score(body)
        normalized_readability = readability_score / 100.0
        score += normalized_readability * self.scoring_weights["readability"]
        
        # Internal links (8%)
        internal_links_score = await self._score_internal_links(body)
        score += internal_links_score * self.scoring_weights["internal_links"]
        
        # External links (7%)
        external_links_score = await self._score_external_links(body)
        score += external_links_score * self.scoring_weights["external_links"]
        
        # Image optimization (10%)
        image_score = await self._score_image_optimization(content)
        score += image_score * self.scoring_weights["image_optimization"]
        
        # Remaining weights are for technical factors (page speed, mobile)
        # For now, give baseline scores
        score += 0.5 * self.scoring_weights["page_speed"]  # Baseline
        score += 0.8 * self.scoring_weights["mobile_friendliness"]  # Baseline
        
        return min(1.0, score) * 100  # Convert to percentage
    
    async def _score_title_optimization(self, title: str, keywords: List[str]) -> float:
        """Score title optimization (0-1 scale)"""
        if not title:
            return 0.0
        
        score = 0.0
        
        # Length check (30-60 characters ideal)
        title_length = len(title)
        if 30 <= title_length <= 60:
            score += 0.4
        elif 20 <= title_length <= 80:
            score += 0.2
        
        # Keyword presence
        title_lower = title.lower()
        keyword_found = False
        for keyword in keywords[:3]:  # Check top 3 keywords
            if keyword.lower() in title_lower:
                score += 0.3
                keyword_found = True
                break
        
        # Front-loading keyword bonus
        if keyword_found and keywords:
            first_keyword = keywords[0].lower()
            if title_lower.startswith(first_keyword):
                score += 0.2
            elif title_lower.find(first_keyword) < len(title) * 0.3:
                score += 0.1
        
        # Uniqueness and readability
        if not re.search(r'\b(click here|read more|learn more)\b', title_lower):
            score += 0.1
        
        return min(1.0, score)
    
    async def _score_meta_description(self, description: str, keywords: List[str]) -> float:
        """Score meta description optimization (0-1 scale)"""
        if not description:
            return 0.0
        
        score = 0.0
        
        # Length check (120-160 characters ideal)
        desc_length = len(description)
        if 120 <= desc_length <= 160:
            score += 0.5
        elif 100 <= desc_length <= 200:
            score += 0.3
        
        # Keyword presence
        description_lower = description.lower()
        for keyword in keywords[:2]:  # Check top 2 keywords
            if keyword.lower() in description_lower:
                score += 0.25
        
        return min(1.0, score)
    
    async def _score_keyword_density(self, body: str, keywords: List[str]) -> float:
        """Score keyword density (0-1 scale)"""
        if not body or not keywords:
            return 0.0
        
        body_lower = body.lower()
        word_count = len(body.split())
        
        if word_count == 0:
            return 0.0
        
        # Check density of top keyword
        main_keyword = keywords[0].lower()
        keyword_count = body_lower.count(main_keyword)
        density = (keyword_count / word_count) * 100
        
        # Ideal density is 1-3%
        if 1.0 <= density <= 3.0:
            return 1.0
        elif 0.5 <= density <= 5.0:
            return 0.7
        elif density > 0:
            return 0.3
        else:
            return 0.0
    
    async def _score_content_length(self, body: str, content_type: ContentType) -> float:
        """Score content length appropriateness (0-1 scale)"""
        if not body:
            return 0.0
        
        word_count = len(body.split())
        template = self.content_templates.get(content_type, {})
        ideal_range = template.get("ideal_length", (1000, 2000))
        
        if ideal_range[0] <= word_count <= ideal_range[1]:
            return 1.0
        elif word_count >= ideal_range[0] * 0.7:
            return 0.7
        elif word_count >= ideal_range[0] * 0.5:
            return 0.4
        else:
            return 0.2
    
    async def _score_internal_links(self, body: str) -> float:
        """Score internal links (0-1 scale)"""
        if not body:
            return 0.0
        
        # Count internal links (simplified - look for relative URLs)
        internal_links = len(re.findall(r'href=["\']\/[^"\']*["\']', body))
        internal_links += len(re.findall(r']\([^http][^)]*\)', body))  # Markdown relative links
        
        if internal_links >= 3:
            return 1.0
        elif internal_links >= 1:
            return 0.7
        else:
            return 0.3
    
    async def _score_external_links(self, body: str) -> float:
        """Score external links (0-1 scale)"""
        if not body:
            return 0.0
        
        # Count external links
        external_links = len(re.findall(r'https?://[^\s\)]+', body))
        
        if 1 <= external_links <= 3:
            return 1.0
        elif external_links > 0:
            return 0.7
        else:
            return 0.4
    
    async def _score_image_optimization(self, content: Dict[str, Any]) -> float:
        """Score image optimization (0-1 scale)"""
        images = content.get("images", [])
        
        if not images:
            return 0.5  # Neutral score for no images
        
        score = 0.0
        
        for image in images:
            # Check for alt text
            if image.get("alt_text"):
                score += 0.3
            
            # Check for descriptive filename
            filename = image.get("filename", "")
            if filename and not re.match(r'^(img|image|photo)\d*\.(jpg|png|gif)$', filename.lower()):
                score += 0.2
            
            # Check for appropriate file size (assume < 1MB is good)
            file_size = image.get("file_size", 0)
            if 0 < file_size < 1024 * 1024:  # Less than 1MB
                score += 0.2
        
        return min(1.0, score / len(images))
    
    async def _generate_seo_suggestions(
        self, 
        content: Dict[str, Any], 
        keywords: List[str], 
        content_type: ContentType
    ) -> List[str]:
        """Generate SEO improvement suggestions"""
        suggestions = []
        
        title = content.get("title", "")
        description = content.get("description", "")
        body = content.get("body", "")
        
        # Title suggestions
        if not title:
            suggestions.append("Add a compelling title with your target keyword")
        elif len(title) < 30:
            suggestions.append("Expand your title to 30-60 characters for better SEO")
        elif len(title) > 60:
            suggestions.append("Shorten your title to under 60 characters")
        
        # Meta description suggestions
        if not description:
            suggestions.append("Add a meta description to improve click-through rates")
        elif len(description) < 120:
            suggestions.append("Expand your meta description to 120-160 characters")
        
        # Keyword suggestions
        if keywords and title:
            main_keyword = keywords[0]
            if main_keyword.lower() not in title.lower():
                suggestions.append(f"Include your main keyword '{main_keyword}' in the title")
        
        # Content length suggestions
        if body:
            word_count = len(body.split())
            template = self.content_templates.get(content_type, {})
            ideal_range = template.get("ideal_length", (1000, 2000))
            
            if word_count < ideal_range[0]:
                suggestions.append(f"Expand content to at least {ideal_range[0]} words for better SEO")
        
        # Structure suggestions
        if body:
            heading_count = len(re.findall(r'#{1,6}\s|<h[1-6]>', body))
            if heading_count < 2:
                suggestions.append("Add more headings (H2, H3) to improve content structure")
            
            internal_links = len(re.findall(r'href=["\']\/|]\([^http]', body))
            if internal_links < 2:
                suggestions.append("Add internal links to other relevant content")
        
        # Image suggestions
        images = content.get("images", [])
        if not images and content_type in [ContentType.BLOG_POST, ContentType.LANDING_PAGE]:
            suggestions.append("Add relevant images to improve user engagement")
        elif images:
            for i, image in enumerate(images):
                if not image.get("alt_text"):
                    suggestions.append(f"Add alt text to image {i+1} for better accessibility and SEO")
        
        return suggestions[:10]  # Limit to top 10 suggestions
    
    async def _identify_seo_issues(self, content: Dict[str, Any], content_type: ContentType) -> List[str]:
        """Identify SEO issues in content"""
        issues = []
        
        title = content.get("title", "")
        description = content.get("description", "")
        body = content.get("body", "")
        
        # Critical issues
        if not title:
            issues.append("CRITICAL: Missing title tag")
        
        if not description:
            issues.append("HIGH: Missing meta description")
        
        if not body or len(body.split()) < 100:
            issues.append("HIGH: Content too short for effective SEO")
        
        # Medium issues
        if title and len(title) > 60:
            issues.append("MEDIUM: Title tag too long (>60 characters)")
        
        if description and len(description) > 160:
            issues.append("MEDIUM: Meta description too long (>160 characters)")
        
        # Technical issues
        if body:
            # Check for duplicate content (simplified)
            sentences = re.split(r'[.!?]+', body)
            unique_sentences = set(sentences)
            if len(sentences) > 10 and len(unique_sentences) / len(sentences) < 0.8:
                issues.append("MEDIUM: Potential duplicate content detected")
            
            # Check for keyword stuffing
            if body:
                word_count = len(body.split())
                # Simple keyword stuffing detection
                words = body.lower().split()
                word_freq = Counter(words)
                for word, count in word_freq.most_common(5):
                    if len(word) > 4 and count / word_count > 0.05:  # >5% frequency
                        issues.append(f"MEDIUM: Potential keyword stuffing detected for '{word}'")
        
        return issues[:5]  # Limit to top 5 issues
    
    async def _identify_seo_opportunities(self, content: Dict[str, Any], keywords: List[str]) -> List[str]:
        """Identify SEO optimization opportunities"""
        opportunities = []
        
        body = content.get("body", "")
        
        # Keyword opportunities
        if keywords:
            related_keywords = []
            for keyword in keywords[:3]:
                if keyword in self.keywords_database:
                    related_keywords.extend(self.keywords_database[keyword].related_keywords)
            
            if related_keywords:
                opportunities.append(f"Target related keywords: {', '.join(related_keywords[:5])}")
        
        # Content expansion opportunities
        if body:
            word_count = len(body.split())
            if word_count < 1500:
                opportunities.append("Expand content with more detailed information and examples")
        
        # Engagement opportunities
        if body:
            question_count = len(re.findall(r'\?', body))
            if question_count < 2:
                opportunities.append("Add more questions to increase user engagement")
        
        # Link building opportunities
        external_links = len(re.findall(r'https?://', body))
        if external_links < 2:
            opportunities.append("Add authoritative external links to boost credibility")
        
        # Schema markup opportunities
        opportunities.append("Consider adding structured data (schema markup) for rich snippets")
        
        return opportunities[:5]  # Limit to top 5 opportunities
    
    async def _perform_meta_analysis(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Perform meta analysis of content"""
        body = content.get("body", "")
        
        meta_analysis = {
            "readability_level": "intermediate",
            "content_freshness": "current",
            "topic_coverage": "comprehensive",
            "user_intent_match": "high"
        }
        
        if body:
            # Simple readability assessment
            avg_sentence_length = len(body.split()) / max(1, len(re.split(r'[.!?]+', body)))
            if avg_sentence_length > 25:
                meta_analysis["readability_level"] = "advanced"
            elif avg_sentence_length < 15:
                meta_analysis["readability_level"] = "basic"
            
            # Content depth assessment
            if len(body.split()) > 2000:
                meta_analysis["topic_coverage"] = "comprehensive"
            elif len(body.split()) > 1000:
                meta_analysis["topic_coverage"] = "moderate"
            else:
                meta_analysis["topic_coverage"] = "basic"
        
        return meta_analysis
    
    async def _generate_related_keywords(self, keyword: str) -> List[str]:
        """Generate related keywords for a given keyword"""
        # Simple related keyword generation
        # In production, this would use external APIs or ML models
        
        base_variations = [
            f"{keyword} tips",
            f"{keyword} guide",
            f"best {keyword}",
            f"{keyword} tutorial",
            f"how to {keyword}",
            f"{keyword} examples",
            f"{keyword} tools",
            f"{keyword} strategies"
        ]
        
        return base_variations[:5]
    
    async def _generate_content_recommendations(self, content_id: str, analysis: ContentAnalysis):
        """Generate specific recommendations based on content analysis"""
        recommendations = []
        
        # High priority recommendations
        if analysis.seo_score < 60:
            recommendations.append(SEORecommendation(
                recommendation_id=str(uuid.uuid4()),
                content_id=content_id,
                priority="high",
                category="seo_score",
                title="Improve Overall SEO Score",
                description="Your content SEO score is below 60. Focus on title optimization, keyword usage, and content structure.",
                implementation_effort="medium",
                expected_impact="high",
                keywords_targeted=analysis.keywords[:3],
                estimated_completion_time="2-4 hours"
            ))
        
        # Content quality recommendations
        if analysis.content_quality_score < 70:
            recommendations.append(SEORecommendation(
                recommendation_id=str(uuid.uuid4()),
                content_id=content_id,
                priority="medium",
                category="content_quality",
                title="Enhance Content Quality",
                description="Improve content structure, add more headings, and include relevant media.",
                implementation_effort="medium",
                expected_impact="medium",
                estimated_completion_time="1-2 hours"
            ))
        
        # Readability recommendations
        if analysis.readability_score < 60:
            recommendations.append(SEORecommendation(
                recommendation_id=str(uuid.uuid4()),
                content_id=content_id,
                priority="medium",
                category="readability",
                title="Improve Content Readability",
                description="Simplify sentence structure and use shorter paragraphs for better readability.",
                implementation_effort="easy",
                expected_impact="medium",
                estimated_completion_time="30-60 minutes"
            ))
        
        # Store recommendations
        self.recommendations[content_id].extend(recommendations)
    
    async def track_keyword_ranking(
        self, 
        keyword: str, 
        content_id: str, 
        ranking_position: int,
        search_engine: SearchEngine = SearchEngine.GOOGLE
    ) -> bool:
        """Track keyword ranking for content
        
        Args:
            keyword: Target keyword
            content_id: Content identifier
            ranking_position: Current ranking position
            search_engine: Search engine where ranking was checked
            
        Returns:
            Success status of tracking
        """
        try:
            ranking_data = {
                "keyword": keyword,
                "content_id": content_id,
                "position": ranking_position,
                "search_engine": search_engine.value,
                "timestamp": datetime.now(),
                "page": (ranking_position - 1) // 10 + 1  # Calculate page number
            }
            
            ranking_key = f"{content_id}_{keyword}_{search_engine.value}"
            self.ranking_history[ranking_key].append(ranking_data)
            
            # Keep only last 100 records per keyword
            self.ranking_history[ranking_key] = self.ranking_history[ranking_key][-100:]
            
            logger.info(f"Keyword ranking tracked: {keyword} at position {ranking_position}")
            return True
            
        except Exception as e:
            logger.error(f"Error tracking keyword ranking: {str(e)}")
            return False
    
    async def get_ranking_history(
        self, 
        content_id: str, 
        keyword: str,
        search_engine: SearchEngine = SearchEngine.GOOGLE,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get ranking history for a keyword
        
        Args:
            content_id: Content identifier
            keyword: Target keyword
            search_engine: Search engine
            days: Number of days to retrieve
            
        Returns:
            Ranking history data
        """
        try:
            ranking_key = f"{content_id}_{keyword}_{search_engine.value}"
            cutoff_date = datetime.now() - timedelta(days=days)
            
            history = self.ranking_history.get(ranking_key, [])
            filtered_history = [
                record for record in history
                if record["timestamp"] >= cutoff_date
            ]
            
            return filtered_history
            
        except Exception as e:
            logger.error(f"Error getting ranking history: {str(e)}")
            return []
    
    async def perform_seo_audit(self, content_id: str) -> Optional[SEOAuditResult]:
        """Perform comprehensive SEO audit for content
        
        Args:
            content_id: Content identifier
            
        Returns:
            SEO audit result
        """
        try:
            if content_id not in self.content_analyses:
                logger.error(f"Content analysis not found for {content_id}")
                return None
            
            analysis = self.content_analyses[content_id]
            
            # Calculate component scores
            technical_seo_score = min(100, analysis.seo_score * 1.1)  # Slightly higher weight
            content_seo_score = analysis.content_quality_score
            user_experience_score = analysis.readability_score
            
            # Overall score
            overall_score = (technical_seo_score + content_seo_score + user_experience_score) / 3
            
            # Compile issues
            issues_found = []
            for issue in analysis.issues:
                severity = "HIGH" if "CRITICAL" in issue else "MEDIUM" if "HIGH" in issue else "LOW"
                issues_found.append({
                    "severity": severity,
                    "description": issue,
                    "category": "technical" if "tag" in issue.lower() else "content"
                })
            
            # Get recommendations
            recommendations = self.recommendations.get(content_id, [])
            
            audit_result = SEOAuditResult(
                audit_id=str(uuid.uuid4()),
                content_id=content_id,
                overall_score=overall_score,
                technical_seo_score=technical_seo_score,
                content_seo_score=content_seo_score,
                user_experience_score=user_experience_score,
                issues_found=issues_found,
                recommendations=recommendations
            )
            
            # Store audit result
            self.audit_results[content_id] = audit_result
            
            logger.info(f"SEO audit completed for {content_id} with overall score: {overall_score:.2f}")
            return audit_result
            
        except Exception as e:
            logger.error(f"Error performing SEO audit: {str(e)}")
            return None
    
    async def analyze_competitor(self, competitor_domain: str) -> Optional[CompetitorAnalysis]:
        """Analyze competitor's SEO performance
        
        Args:
            competitor_domain: Competitor's domain to analyze
            
        Returns:
            Competitor analysis result
        """
        try:
            # Mock competitor analysis (in production, use SEO APIs)
            analysis = CompetitorAnalysis(
                competitor_domain=competitor_domain,
                domain_authority=np.random.rand() * 100 if NUMPY_AVAILABLE else 50.0,
                organic_keywords=int((np.random.rand() if NUMPY_AVAILABLE else 0.5) * 10000),
                organic_traffic=int((np.random.rand() if NUMPY_AVAILABLE else 0.5) * 100000),
                backlinks=int((np.random.rand() if NUMPY_AVAILABLE else 0.5) * 50000),
                top_keywords=[
                    {"keyword": f"sample_keyword_{i}", "position": i+1, "volume": 1000}
                    for i in range(10)
                ],
                content_gaps=["Missing blog content", "No video content", "Limited social presence"],
                competitive_advantages=["Strong domain authority", "Good content structure"]
            )
            
            self.competitor_data[competitor_domain] = analysis
            
            logger.info(f"Competitor analysis completed for {competitor_domain}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing competitor: {str(e)}")
            return None
    
    async def get_seo_dashboard(self, content_ids: List[str]) -> Dict[str, Any]:
        """Get SEO dashboard data for multiple content pieces
        
        Args:
            content_ids: List of content identifiers
            
        Returns:
            Dashboard data
        """
        try:
            dashboard_data = {
                "overview": {
                    "total_content": len(content_ids),
                    "analyzed_content": 0,
                    "average_seo_score": 0.0,
                    "total_keywords": 0,
                    "total_issues": 0
                },
                "content_performance": [],
                "keyword_rankings": {},
                "top_opportunities": [],
                "recent_audits": []
            }
            
            total_seo_score = 0.0
            analyzed_count = 0
            all_keywords = set()
            total_issues = 0
            
            for content_id in content_ids:
                analysis = self.content_analyses.get(content_id)
                if analysis:
                    analyzed_count += 1
                    total_seo_score += analysis.seo_score
                    all_keywords.update(analysis.keywords)
                    total_issues += len(analysis.issues)
                    
                    dashboard_data["content_performance"].append({
                        "content_id": content_id,
                        "title": analysis.title,
                        "seo_score": analysis.seo_score,
                        "content_quality_score": analysis.content_quality_score,
                        "readability_score": analysis.readability_score,
                        "issues_count": len(analysis.issues),
                        "opportunities_count": len(analysis.opportunities)
                    })
            
            # Update overview
            dashboard_data["overview"]["analyzed_content"] = analyzed_count
            dashboard_data["overview"]["average_seo_score"] = (
                total_seo_score / analyzed_count if analyzed_count > 0 else 0.0
            )
            dashboard_data["overview"]["total_keywords"] = len(all_keywords)
            dashboard_data["overview"]["total_issues"] = total_issues
            
            # Sort content by SEO score
            dashboard_data["content_performance"].sort(
                key=lambda x: x["seo_score"], reverse=True
            )
            
            # Get recent audits
            recent_audits = sorted(
                self.audit_results.values(),
                key=lambda x: x.audit_date,
                reverse=True
            )[:5]
            
            dashboard_data["recent_audits"] = [
                {
                    "audit_id": audit.audit_id,
                    "content_id": audit.content_id,
                    "overall_score": audit.overall_score,
                    "audit_date": audit.audit_date.isoformat()
                }
                for audit in recent_audits
            ]
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error generating SEO dashboard: {str(e)}")
            return {"error": str(e)}
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get system health and performance metrics
        
        Returns:
            System health information
        """
        try:
            return {
                "total_keywords": len(self.keywords_database),
                "analyzed_content": len(self.content_analyses),
                "tracked_rankings": len(self.ranking_history),
                "total_recommendations": sum(len(recs) for recs in self.recommendations.values()),
                "completed_audits": len(self.audit_results),
                "competitor_profiles": len(self.competitor_data),
                "nlp_available": NLP_AVAILABLE,
                "web_scraping_available": WEB_SCRAPING_AVAILABLE,
                "system_status": "operational",
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting system health: {str(e)}")
            return {"status": "error", "message": str(e)}

# Export main class and types
__all__ = [
    'SEOIntelligenceOptimizationSystem',
    'ContentType',
    'SEOMetricType',
    'SearchEngine',
    'KeywordDifficulty',
    'Keyword',
    'SEOMetric',
    'ContentAnalysis',
    'SEORecommendation',
    'CompetitorAnalysis',
    'SEOAuditResult'
]