"""SEO API Template for IA Chéries Platform

⚠️  AVERTISSEMENT LÉGAL:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Author: Fahed Mlaiel (mlaiel@live.de)
Created: 2025-01-18
Version: 1.0.0
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator, HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import uuid
import asyncio
import logging
import json
import re
from dataclasses import dataclass
import requests
from urllib.parse import urlparse, urljoin
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

# Database Models
Base = declarative_base()

class SEOPriority(str, Enum):
    """SEO optimization priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ContentType(str, Enum):
    """Content types for SEO optimization"""
    ARTICLE = "article"
    VIDEO = "video"
    PODCAST = "podcast"
    IMAGE = "image"
    COURSE = "course"
    TUTORIAL = "tutorial"
    REVIEW = "review"
    NEWS = "news"

class SEOIssueType(str, Enum):
    """Types of SEO issues"""
    MISSING_TITLE = "missing_title"
    MISSING_DESCRIPTION = "missing_description"
    DUPLICATE_CONTENT = "duplicate_content"
    BROKEN_LINKS = "broken_links"
    SLOW_LOADING = "slow_loading"
    MISSING_ALT_TEXT = "missing_alt_text"
    POOR_KEYWORD_DENSITY = "poor_keyword_density"
    MISSING_SCHEMA = "missing_schema"
    LOW_QUALITY_CONTENT = "low_quality_content"

class SEOMetadata(Base):
    """SEO metadata for content"""
    __tablename__ = "seo_metadata"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    content_id = Column(String, ForeignKey("content.id"), nullable=False)
    creator_id = Column(String, ForeignKey("creators.id"), nullable=False)
    
    # Basic SEO fields
    title = Column(String(70))  # Recommended title length
    meta_description = Column(String(160))  # Recommended description length
    slug = Column(String(100))
    canonical_url = Column(String(500))
    
    # Keywords
    primary_keyword = Column(String(100))
    secondary_keywords = Column(JSON)  # List of keywords
    focus_keywords = Column(JSON)  # List of focus keywords
    
    # Open Graph metadata
    og_title = Column(String(95))
    og_description = Column(String(200))
    og_image = Column(String(500))
    og_type = Column(String(50), default="article")
    
    # Twitter Card metadata
    twitter_title = Column(String(70))
    twitter_description = Column(String(200))
    twitter_image = Column(String(500))
    twitter_card = Column(String(50), default="summary_large_image")
    
    # Schema.org structured data
    schema_markup = Column(JSON)
    
    # Content optimization
    word_count = Column(Integer)
    reading_time_minutes = Column(Integer)
    content_type = Column(String(50))
    language = Column(String(5), default="en")
    
    # SEO scores
    seo_score = Column(Float, default=0.0)
    keyword_density = Column(Float, default=0.0)
    readability_score = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SEOAudit(Base):
    """SEO audit results"""
    __tablename__ = "seo_audits"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    content_id = Column(String, ForeignKey("content.id"))
    creator_id = Column(String, ForeignKey("creators.id"))
    url = Column(String(500))
    
    # Audit results
    overall_score = Column(Float, default=0.0)
    performance_score = Column(Float, default=0.0)
    accessibility_score = Column(Float, default=0.0)
    seo_score = Column(Float, default=0.0)
    best_practices_score = Column(Float, default=0.0)
    
    # Issues found
    issues = Column(JSON)  # List of SEO issues
    recommendations = Column(JSON)  # List of recommendations
    
    # Technical details
    page_load_time = Column(Float)
    page_size_kb = Column(Integer)
    mobile_friendly = Column(Boolean)
    https_enabled = Column(Boolean)
    
    # Audit metadata
    audit_date = Column(DateTime, default=datetime.utcnow)
    audit_type = Column(String(50), default="automatic")  # automatic, manual
    
    created_at = Column(DateTime, default=datetime.utcnow)

class KeywordRanking(Base):
    """Keyword ranking tracking"""
    __tablename__ = "keyword_rankings"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    content_id = Column(String, ForeignKey("content.id"))
    creator_id = Column(String, ForeignKey("creators.id"), nullable=False)
    
    # Keyword details
    keyword = Column(String(200), nullable=False)
    search_volume = Column(Integer)
    competition = Column(String(20))  # low, medium, high
    
    # Ranking data
    current_position = Column(Integer)
    previous_position = Column(Integer)
    position_change = Column(Integer)
    
    # Search engine specific
    search_engine = Column(String(50), default="google")
    country = Column(String(2), default="US")
    device = Column(String(20), default="desktop")  # desktop, mobile
    
    # Performance metrics
    clicks = Column(Integer, default=0)
    impressions = Column(Integer, default=0)
    ctr = Column(Float, default=0.0)  # Click-through rate
    
    date_tracked = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

class SitemapEntry(Base):
    """Sitemap entries for SEO"""
    __tablename__ = "sitemap_entries"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    creator_id = Column(String, ForeignKey("creators.id"), nullable=False)
    content_id = Column(String, ForeignKey("content.id"))
    
    # URL details
    url = Column(String(500), nullable=False)
    priority = Column(Float, default=0.5)  # 0.0 to 1.0
    change_frequency = Column(String(20), default="weekly")  # never, yearly, monthly, weekly, daily, hourly, always
    
    # Metadata
    last_modified = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Pydantic Models
class SEOMetadataCreate(BaseModel):
    """Create SEO metadata request"""
    title: str = Field(..., min_length=10, max_length=70)
    meta_description: str = Field(..., min_length=50, max_length=160)
    primary_keyword: str = Field(..., min_length=2, max_length=100)
    secondary_keywords: List[str] = Field(default=[])
    slug: Optional[str] = None
    canonical_url: Optional[HttpUrl] = None
    og_title: Optional[str] = Field(None, max_length=95)
    og_description: Optional[str] = Field(None, max_length=200)
    og_image: Optional[HttpUrl] = None
    twitter_title: Optional[str] = Field(None, max_length=70)
    twitter_description: Optional[str] = Field(None, max_length=200)
    twitter_image: Optional[HttpUrl] = None
    content_type: ContentType = ContentType.ARTICLE
    language: str = Field(default="en", pattern="^[a-z]{2}$")
    
    @validator('slug')
    def validate_slug(cls, v):
        if v and not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('Slug must contain only lowercase letters, numbers, and hyphens')
        return v

class SEOMetadataResponse(BaseModel):
    """SEO metadata response"""
    id: str
    content_id: str
    creator_id: str
    title: str
    meta_description: str
    slug: Optional[str]
    canonical_url: Optional[str]
    primary_keyword: str
    secondary_keywords: List[str]
    og_title: Optional[str]
    og_description: Optional[str]
    og_image: Optional[str]
    twitter_title: Optional[str]
    twitter_description: Optional[str]
    twitter_image: Optional[str]
    schema_markup: Optional[Dict[str, Any]]
    word_count: Optional[int]
    reading_time_minutes: Optional[int]
    content_type: str
    language: str
    seo_score: float
    keyword_density: float
    readability_score: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class SEOAuditResponse(BaseModel):
    """SEO audit response"""
    id: str
    content_id: Optional[str]
    creator_id: Optional[str]
    url: Optional[str]
    overall_score: float
    performance_score: float
    accessibility_score: float
    seo_score: float
    best_practices_score: float
    issues: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    page_load_time: Optional[float]
    page_size_kb: Optional[int]
    mobile_friendly: Optional[bool]
    https_enabled: Optional[bool]
    audit_date: datetime
    audit_type: str
    
    class Config:
        from_attributes = True

class KeywordAnalysis(BaseModel):
    """Keyword analysis response"""
    keyword: str
    search_volume: int
    competition: str
    difficulty: float
    related_keywords: List[str]
    search_intent: str
    seasonal_trends: Dict[str, float]
    cost_per_click: Optional[float]

class SEORecommendations(BaseModel):
    """SEO recommendations"""
    content_id: str
    recommendations: List[Dict[str, Any]]
    priority_issues: List[Dict[str, Any]]
    quick_wins: List[Dict[str, Any]]
    long_term_strategy: List[str]
    estimated_impact: Dict[str, float]

class CompetitorAnalysis(BaseModel):
    """Competitor SEO analysis"""
    competitor_url: str
    domain_authority: float
    keywords_ranking: List[Dict[str, Any]]
    backlinks_count: int
    content_gaps: List[str]
    opportunities: List[Dict[str, Any]]

class SEOService:
    """Service for handling SEO operations"""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        
        # SEO tools configuration
        self.google_api_key = "your_google_api_key"
        self.semrush_api_key = "your_semrush_api_key"
        self.ahrefs_api_key = "your_ahrefs_api_key"
        
        logger.info("SEO service initialized")
    
    async def create_seo_metadata(
        self,
        content_id: str,
        creator_id: str,
        metadata: SEOMetadataCreate
    ) -> SEOMetadataResponse:
        """Create SEO metadata for content"""
        
        # Generate slug if not provided
        slug = metadata.slug or self._generate_slug(metadata.title)
        
        # Generate schema markup
        schema_markup = self._generate_schema_markup(metadata, content_id)
        
        # Calculate initial scores
        seo_score = await self._calculate_seo_score(metadata)
        keyword_density = self._calculate_keyword_density(metadata.primary_keyword, "")  # Content would be passed
        readability_score = self._calculate_readability_score("")  # Content would be passed
        
        # Create SEO metadata
        seo_metadata = SEOMetadata(
            content_id=content_id,
            creator_id=creator_id,
            title=metadata.title,
            meta_description=metadata.meta_description,
            slug=slug,
            canonical_url=str(metadata.canonical_url) if metadata.canonical_url else None,
            primary_keyword=metadata.primary_keyword,
            secondary_keywords=metadata.secondary_keywords,
            og_title=metadata.og_title or metadata.title,
            og_description=metadata.og_description or metadata.meta_description,
            og_image=str(metadata.og_image) if metadata.og_image else None,
            twitter_title=metadata.twitter_title or metadata.title,
            twitter_description=metadata.twitter_description or metadata.meta_description,
            twitter_image=str(metadata.twitter_image) if metadata.twitter_image else None,
            schema_markup=schema_markup,
            content_type=metadata.content_type.value,
            language=metadata.language,
            seo_score=seo_score,
            keyword_density=keyword_density,
            readability_score=readability_score
        )
        
        self.db.add(seo_metadata)
        await self.db.commit()
        await self.db.refresh(seo_metadata)
        
        return SEOMetadataResponse(**seo_metadata.__dict__)
    
    async def audit_content_seo(
        self,
        content_id: str,
        creator_id: str,
        url: Optional[str] = None
    ) -> SEOAuditResponse:
        """Perform SEO audit on content"""
        
        # Run comprehensive SEO audit
        audit_results = await self._run_seo_audit(content_id, url)
        
        # Create audit record
        audit = SEOAudit(
            content_id=content_id,
            creator_id=creator_id,
            url=url,
            overall_score=audit_results["overall_score"],
            performance_score=audit_results["performance_score"],
            accessibility_score=audit_results["accessibility_score"],
            seo_score=audit_results["seo_score"],
            best_practices_score=audit_results["best_practices_score"],
            issues=audit_results["issues"],
            recommendations=audit_results["recommendations"],
            page_load_time=audit_results.get("page_load_time"),
            page_size_kb=audit_results.get("page_size_kb"),
            mobile_friendly=audit_results.get("mobile_friendly"),
            https_enabled=audit_results.get("https_enabled"),
            audit_type="automatic"
        )
        
        self.db.add(audit)
        await self.db.commit()
        await self.db.refresh(audit)
        
        return SEOAuditResponse(**audit.__dict__)
    
    async def analyze_keyword(
        self,
        keyword: str,
        country: str = "US",
        language: str = "en"
    ) -> KeywordAnalysis:
        """Analyze keyword for SEO potential"""
        
        # Get keyword data from various sources
        search_volume = await self._get_search_volume(keyword, country)
        competition = await self._get_keyword_competition(keyword)
        difficulty = await self._calculate_keyword_difficulty(keyword)
        related_keywords = await self._get_related_keywords(keyword)
        search_intent = await self._analyze_search_intent(keyword)
        seasonal_trends = await self._get_seasonal_trends(keyword)
        cost_per_click = await self._get_cost_per_click(keyword)
        
        return KeywordAnalysis(
            keyword=keyword,
            search_volume=search_volume,
            competition=competition,
            difficulty=difficulty,
            related_keywords=related_keywords,
            search_intent=search_intent,
            seasonal_trends=seasonal_trends,
            cost_per_click=cost_per_click
        )
    
    async def get_seo_recommendations(
        self,
        content_id: str,
        creator_id: str
    ) -> SEORecommendations:
        """Get SEO recommendations for content"""
        
        # Get content metadata and audit results
        metadata = await self._get_seo_metadata(content_id)
        latest_audit = await self._get_latest_audit(content_id)
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(metadata, latest_audit)
        priority_issues = await self._identify_priority_issues(latest_audit)
        quick_wins = await self._identify_quick_wins(metadata, latest_audit)
        long_term_strategy = await self._generate_long_term_strategy(creator_id)
        estimated_impact = await self._estimate_recommendation_impact(recommendations)
        
        return SEORecommendations(
            content_id=content_id,
            recommendations=recommendations,
            priority_issues=priority_issues,
            quick_wins=quick_wins,
            long_term_strategy=long_term_strategy,
            estimated_impact=estimated_impact
        )
    
    async def track_keyword_rankings(
        self,
        creator_id: str,
        keywords: List[str],
        content_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Track keyword rankings"""
        
        rankings = []
        
        for keyword in keywords:
            # Get current ranking position
            position = await self._get_keyword_position(keyword, content_id)
            
            # Get search volume and metrics
            search_volume = await self._get_search_volume(keyword)
            competition = await self._get_keyword_competition(keyword)
            
            # Get performance metrics from search console
            metrics = await self._get_search_console_metrics(keyword, content_id)
            
            # Create or update ranking record
            ranking = KeywordRanking(
                content_id=content_id,
                creator_id=creator_id,
                keyword=keyword,
                search_volume=search_volume,
                competition=competition,
                current_position=position,
                clicks=metrics.get("clicks", 0),
                impressions=metrics.get("impressions", 0),
                ctr=metrics.get("ctr", 0.0)
            )
            
            self.db.add(ranking)
            rankings.append({
                "keyword": keyword,
                "position": position,
                "search_volume": search_volume,
                "competition": competition,
                "clicks": metrics.get("clicks", 0),
                "impressions": metrics.get("impressions", 0),
                "ctr": metrics.get("ctr", 0.0)
            })
        
        await self.db.commit()
        return rankings
    
    async def generate_sitemap(
        self,
        creator_id: str,
        base_url: str
    ) -> str:
        """Generate XML sitemap for creator's content"""
        
        # Get all published content for creator
        content_urls = await self._get_creator_content_urls(creator_id, base_url)
        
        # Create XML sitemap
        urlset = ET.Element("urlset")
        urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
        
        for url_data in content_urls:
            url_elem = ET.SubElement(urlset, "url")
            
            loc = ET.SubElement(url_elem, "loc")
            loc.text = url_data["url"]
            
            lastmod = ET.SubElement(url_elem, "lastmod")
            lastmod.text = url_data["last_modified"].strftime("%Y-%m-%d")
            
            changefreq = ET.SubElement(url_elem, "changefreq")
            changefreq.text = url_data.get("change_frequency", "weekly")
            
            priority = ET.SubElement(url_elem, "priority")
            priority.text = str(url_data.get("priority", 0.5))
        
        # Convert to string
        sitemap_xml = ET.tostring(urlset, encoding="unicode")
        
        # Store sitemap entries in database
        for url_data in content_urls:
            sitemap_entry = SitemapEntry(
                creator_id=creator_id,
                content_id=url_data.get("content_id"),
                url=url_data["url"],
                priority=url_data.get("priority", 0.5),
                change_frequency=url_data.get("change_frequency", "weekly"),
                last_modified=url_data["last_modified"]
            )
            self.db.add(sitemap_entry)
        
        await self.db.commit()
        
        return sitemap_xml
    
    async def analyze_competitors(
        self,
        creator_id: str,
        competitor_urls: List[str]
    ) -> List[CompetitorAnalysis]:
        """Analyze competitor SEO strategies"""
        
        analyses = []
        
        for url in competitor_urls:
            # Get competitor metrics
            domain_authority = await self._get_domain_authority(url)
            keywords_ranking = await self._get_competitor_keywords(url)
            backlinks_count = await self._get_backlinks_count(url)
            
            # Identify content gaps and opportunities
            content_gaps = await self._identify_content_gaps(creator_id, url)
            opportunities = await self._identify_seo_opportunities(creator_id, url)
            
            analysis = CompetitorAnalysis(
                competitor_url=url,
                domain_authority=domain_authority,
                keywords_ranking=keywords_ranking,
                backlinks_count=backlinks_count,
                content_gaps=content_gaps,
                opportunities=opportunities
            )
            
            analyses.append(analysis)
        
        return analyses
    
    def _generate_slug(self, title: str) -> str:
        """Generate URL slug from title"""
        # Convert to lowercase and replace spaces with hyphens
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')
    
    def _generate_schema_markup(self, metadata: SEOMetadataCreate, content_id: str) -> Dict[str, Any]:
        """Generate Schema.org structured data"""
        
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": metadata.title,
            "description": metadata.meta_description,
            "author": {
                "@type": "Person",
                "name": "Creator Name"  # Would be fetched from creator data
            },
            "publisher": {
                "@type": "Organization",
                "name": "IA Chéries",
                "logo": {
                    "@type": "ImageObject",
                    "url": "https://ainflue.com/logo.png"
                }
            },
            "datePublished": datetime.utcnow().isoformat(),
            "dateModified": datetime.utcnow().isoformat(),
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": f"https://ainflue.com/content/{content_id}"
            }
        }
        
        if metadata.og_image:
            schema["image"] = {
                "@type": "ImageObject",
                "url": str(metadata.og_image)
            }
        
        return schema
    
    async def _calculate_seo_score(self, metadata: SEOMetadataCreate) -> float:
        """Calculate SEO score based on metadata"""
        score = 0.0
        
        # Title score (0-20 points)
        if 30 <= len(metadata.title) <= 60:
            score += 20
        elif 20 <= len(metadata.title) <= 70:
            score += 15
        else:
            score += 10
        
        # Meta description score (0-20 points)
        if 120 <= len(metadata.meta_description) <= 160:
            score += 20
        elif 100 <= len(metadata.meta_description) <= 180:
            score += 15
        else:
            score += 10
        
        # Primary keyword in title (0-15 points)
        if metadata.primary_keyword.lower() in metadata.title.lower():
            score += 15
        
        # Primary keyword in description (0-10 points)
        if metadata.primary_keyword.lower() in metadata.meta_description.lower():
            score += 10
        
        # Secondary keywords (0-10 points)
        if metadata.secondary_keywords:
            score += min(len(metadata.secondary_keywords) * 2, 10)
        
        # Social media metadata (0-15 points)
        if metadata.og_title and metadata.og_description:
            score += 10
        if metadata.twitter_title and metadata.twitter_description:
            score += 5
        
        # Content type specific bonuses (0-10 points)
        if metadata.content_type in [ContentType.ARTICLE, ContentType.TUTORIAL]:
            score += 10
        
        return min(score, 100.0)
    
    def _calculate_keyword_density(self, keyword: str, content: str) -> float:
        """Calculate keyword density in content"""
        if not content:
            return 0.0
        
        words = content.lower().split()
        keyword_count = content.lower().count(keyword.lower())
        
        if len(words) == 0:
            return 0.0
        
        density = (keyword_count / len(words)) * 100
        return round(density, 2)
    
    def _calculate_readability_score(self, content: str) -> float:
        """Calculate content readability score"""
        if not content:
            return 0.0
        
        # Simplified readability calculation
        sentences = content.count('.') + content.count('!') + content.count('?')
        words = len(content.split())
        
        if sentences == 0:
            return 0.0
        
        avg_sentence_length = words / sentences
        
        # Basic readability score (inverse of complexity)
        if avg_sentence_length <= 15:
            return 90.0
        elif avg_sentence_length <= 20:
            return 70.0
        elif avg_sentence_length <= 25:
            return 50.0
        else:
            return 30.0
    
    async def _run_seo_audit(self, content_id: str, url: Optional[str]) -> Dict[str, Any]:
        """Run comprehensive SEO audit"""
        
        # Mock audit results - would integrate with real SEO tools
        return {
            "overall_score": 78.5,
            "performance_score": 85.2,
            "accessibility_score": 72.1,
            "seo_score": 82.3,
            "best_practices_score": 91.7,
            "issues": [
                {
                    "type": "missing_alt_text",
                    "severity": "medium",
                    "description": "3 images are missing alt text",
                    "fix": "Add descriptive alt text to all images"
                },
                {
                    "type": "slow_loading",
                    "severity": "high", 
                    "description": "Page load time is 4.2 seconds",
                    "fix": "Optimize images and minify CSS/JS"
                }
            ],
            "recommendations": [
                {
                    "priority": "high",
                    "title": "Optimize page speed",
                    "description": "Reduce page load time to under 3 seconds",
                    "estimated_impact": "15% increase in rankings"
                },
                {
                    "priority": "medium",
                    "title": "Add alt text to images",
                    "description": "Improve accessibility and SEO",
                    "estimated_impact": "5% increase in rankings"
                }
            ],
            "page_load_time": 4.2,
            "page_size_kb": 2840,
            "mobile_friendly": True,
            "https_enabled": True
        }
    
    async def _get_search_volume(self, keyword: str, country: str = "US") -> int:
        """Get keyword search volume"""
        # Mock implementation - would use Google Keyword Planner API
        return 1450
    
    async def _get_keyword_competition(self, keyword: str) -> str:
        """Get keyword competition level"""
        # Mock implementation - would use SEO tools API
        return "medium"
    
    async def _calculate_keyword_difficulty(self, keyword: str) -> float:
        """Calculate keyword difficulty score"""
        # Mock implementation - would use tools like Ahrefs, SEMrush
        return 65.5
    
    async def _get_related_keywords(self, keyword: str) -> List[str]:
        """Get related keywords"""
        # Mock implementation - would use keyword research tools
        return [
            f"{keyword} tutorial",
            f"how to {keyword}",
            f"{keyword} guide",
            f"best {keyword}",
            f"{keyword} tips"
        ]
    
    async def _analyze_search_intent(self, keyword: str) -> str:
        """Analyze search intent for keyword"""
        # Mock implementation - would use NLP analysis
        intent_keywords = {
            "how": "informational",
            "what": "informational", 
            "buy": "transactional",
            "best": "commercial",
            "review": "commercial"
        }
        
        for intent_word, intent_type in intent_keywords.items():
            if intent_word in keyword.lower():
                return intent_type
        
        return "informational"
    
    async def _get_seasonal_trends(self, keyword: str) -> Dict[str, float]:
        """Get seasonal trends for keyword"""
        # Mock implementation - would use Google Trends API
        return {
            "january": 0.8,
            "february": 0.9,
            "march": 1.1,
            "april": 1.0,
            "may": 0.9,
            "june": 0.8,
            "july": 0.7,
            "august": 0.9,
            "september": 1.2,
            "october": 1.1,
            "november": 1.0,
            "december": 0.9
        }
    
    async def _get_cost_per_click(self, keyword: str) -> Optional[float]:
        """Get estimated cost per click for keyword"""
        # Mock implementation - would use Google Ads API
        return 2.45
    
    # Additional helper methods would be implemented here...
    async def _get_seo_metadata(self, content_id: str):
        """Get SEO metadata for content"""
        return None
    
    async def _get_latest_audit(self, content_id: str):
        """Get latest SEO audit for content"""
        return None
    
    async def _generate_recommendations(self, metadata, audit):
        """Generate SEO recommendations"""
        return []
    
    async def _identify_priority_issues(self, audit):
        """Identify priority SEO issues"""
        return []
    
    async def _identify_quick_wins(self, metadata, audit):
        """Identify quick SEO wins"""
        return []
    
    async def _generate_long_term_strategy(self, creator_id: str):
        """Generate long-term SEO strategy"""
        return []
    
    async def _estimate_recommendation_impact(self, recommendations):
        """Estimate impact of recommendations"""
        return {}
    
    async def _get_keyword_position(self, keyword: str, content_id: Optional[str]):
        """Get keyword ranking position"""
        return 15
    
    async def _get_search_console_metrics(self, keyword: str, content_id: Optional[str]):
        """Get search console metrics"""
        return {"clicks": 45, "impressions": 1250, "ctr": 3.6}
    
    async def _get_creator_content_urls(self, creator_id: str, base_url: str):
        """Get all content URLs for creator"""
        return []
    
    async def _get_domain_authority(self, url: str):
        """Get domain authority score"""
        return 65.5
    
    async def _get_competitor_keywords(self, url: str):
        """Get competitor's ranking keywords"""
        return []
    
    async def _get_backlinks_count(self, url: str):
        """Get backlinks count"""
        return 1250
    
    async def _identify_content_gaps(self, creator_id: str, competitor_url: str):
        """Identify content gaps vs competitor"""
        return []
    
    async def _identify_seo_opportunities(self, creator_id: str, competitor_url: str):
        """Identify SEO opportunities"""
        return []

# FastAPI Router
from fastapi import APIRouter

def create_seo_router(db_session_dependency) -> APIRouter:
    """Create SEO API router"""
    
    router = APIRouter(prefix="/seo", tags=["SEO"])
    security = HTTPBearer()
    
    @router.post("/metadata/{content_id}", response_model=SEOMetadataResponse)
    async def create_seo_metadata(
        content_id: str,
        metadata: SEOMetadataCreate,
        db: AsyncSession = Depends(db_session_dependency),
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
        """Create SEO metadata for content"""
        # Extract creator_id from JWT token
        creator_id = "creator_123"  # Mock - extract from JWT
        
        service = SEOService(db)
        return await service.create_seo_metadata(content_id, creator_id, metadata)
    
    @router.post("/audit/{content_id}", response_model=SEOAuditResponse)
    async def audit_content(
        content_id: str,
        url: Optional[str] = None,
        db: AsyncSession = Depends(db_session_dependency),
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
        """Perform SEO audit on content"""
        # Extract creator_id from JWT token
        creator_id = "creator_123"  # Mock - extract from JWT
        
        service = SEOService(db)
        return await service.audit_content_seo(content_id, creator_id, url)
    
    @router.get("/keywords/{keyword}/analyze", response_model=KeywordAnalysis)
    async def analyze_keyword(
        keyword: str,
        country: str = Query("US", pattern="^[A-Z]{2}$"),
        language: str = Query("en", pattern="^[a-z]{2}$"),
        db: AsyncSession = Depends(db_session_dependency),
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
        """Analyze keyword for SEO potential"""
        service = SEOService(db)
        return await service.analyze_keyword(keyword, country, language)
    
    @router.get("/recommendations/{content_id}", response_model=SEORecommendations)
    async def get_recommendations(
        content_id: str,
        db: AsyncSession = Depends(db_session_dependency),
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
        """Get SEO recommendations for content"""
        # Extract creator_id from JWT token
        creator_id = "creator_123"  # Mock - extract from JWT
        
        service = SEOService(db)
        return await service.get_seo_recommendations(content_id, creator_id)
    
    @router.post("/rankings/track")
    async def track_rankings(
        keywords: List[str],
        content_id: Optional[str] = None,
        db: AsyncSession = Depends(db_session_dependency),
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
        """Track keyword rankings"""
        # Extract creator_id from JWT token
        creator_id = "creator_123"  # Mock - extract from JWT
        
        service = SEOService(db)
        return await service.track_keyword_rankings(creator_id, keywords, content_id)
    
    @router.get("/sitemap/generate")
    async def generate_sitemap(
        base_url: HttpUrl,
        db: AsyncSession = Depends(db_session_dependency),
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
        """Generate XML sitemap"""
        # Extract creator_id from JWT token
        creator_id = "creator_123"  # Mock - extract from JWT
        
        service = SEOService(db)
        sitemap_xml = await service.generate_sitemap(creator_id, str(base_url))
        
        from fastapi import Response
        return Response(content=sitemap_xml, media_type="application/xml")
    
    @router.post("/competitors/analyze")
    async def analyze_competitors(
        competitor_urls: List[HttpUrl],
        db: AsyncSession = Depends(db_session_dependency),
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
        """Analyze competitor SEO strategies"""
        # Extract creator_id from JWT token
        creator_id = "creator_123"  # Mock - extract from JWT
        
        service = SEOService(db)
        return await service.analyze_competitors(creator_id, [str(url) for url in competitor_urls])
    
    return router

# Configuration template
SEO_CONFIG = {
    "keyword_research": {
        "google_api_key": "your_google_api_key",
        "semrush_api_key": "your_semrush_api_key",
        "ahrefs_api_key": "your_ahrefs_api_key"
    },
    "optimization": {
        "target_keyword_density": 1.5,  # percentage
        "min_content_length": 300,  # words
        "max_title_length": 60,
        "max_description_length": 160
    },
    "auditing": {
        "audit_frequency": "weekly",
        "performance_threshold": 70.0,
        "seo_score_threshold": 80.0
    },
    "tracking": {
        "search_engines": ["google", "bing"],
        "countries": ["US", "UK", "CA"],
        "devices": ["desktop", "mobile"]
    },
    "sitemap": {
        "max_urls": 50000,
        "default_priority": 0.5,
        "default_changefreq": "weekly"
    }
}

if __name__ == "__main__":
    # Example usage
    print("SEO API Template loaded successfully")
    print("Content Types:", [content_type.value for content_type in ContentType])
    print("SEO Issue Types:", [issue.value for issue in SEOIssueType])