"""Content Gap Identifier - AI-Powered Content Opportunity Discovery

This module identifies content gaps by analyzing competitor content strategies,
user search intent, and market opportunities using advanced NLP and ML techniques.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import uuid
from collections import defaultdict, Counter
import statistics
import numpy as np
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import LatentDirichletAllocation

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Types of content"""
    BLOG_POST = "blog_post"
    VIDEO = "video"
    PODCAST = "podcast"
    INFOGRAPHIC = "infographic"
    CASE_STUDY = "case_study"
    TUTORIAL = "tutorial"
    REVIEW = "review"
    COMPARISON = "comparison"
    GUIDE = "guide"
    NEWS = "news"
    INTERVIEW = "interview"
    WEBINAR = "webinar"
    EBOOK = "ebook"
    WHITEPAPER = "whitepaper"
    SOCIAL_POST = "social_post"


class ContentFormat(Enum):
    """Content formats"""
    SHORT_FORM = "short_form"      # < 800 words
    MEDIUM_FORM = "medium_form"    # 800-2000 words
    LONG_FORM = "long_form"        # > 2000 words
    VISUAL = "visual"              # Image/video focused
    INTERACTIVE = "interactive"     # Interactive elements
    LIVE = "live"                  # Live streaming
    SERIES = "series"              # Multi-part content


class SearchIntent(Enum):
    """User search intent types"""
    INFORMATIONAL = "informational"
    NAVIGATIONAL = "navigational"
    TRANSACTIONAL = "transactional"
    COMMERCIAL = "commercial"


class GapSeverity(Enum):
    """Content gap severity levels"""
    CRITICAL = "critical"      # High traffic, no coverage
    HIGH = "high"             # Medium-high traffic, minimal coverage
    MEDIUM = "medium"         # Medium traffic, some coverage
    LOW = "low"              # Low traffic, adequate coverage


@dataclass
class ContentPiece:
    """Represents a piece of content"""
    content_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    url: str = ""
    content_type: ContentType = ContentType.BLOG_POST
    content_format: ContentFormat = ContentFormat.MEDIUM_FORM
    word_count: int = 0
    publish_date: datetime = field(default_factory=datetime.now)
    author: str = ""
    domain: str = ""
    keywords: List[str] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)
    search_intent: SearchIntent = SearchIntent.INFORMATIONAL
    engagement_metrics: Dict[str, float] = field(default_factory=dict)
    seo_metrics: Dict[str, float] = field(default_factory=dict)
    quality_score: float = 0.0
    freshness_score: float = 0.0
    comprehensiveness_score: float = 0.0


@dataclass
class ContentGap:
    """Represents a content gap opportunity"""
    gap_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    topic: str = ""
    keywords: List[str] = field(default_factory=list)
    search_intent: SearchIntent = SearchIntent.INFORMATIONAL
    gap_severity: GapSeverity = GapSeverity.MEDIUM
    content_types_missing: List[ContentType] = field(default_factory=list)
    formats_missing: List[ContentFormat] = field(default_factory=list)
    estimated_traffic: float = 0.0
    competition_level: float = 0.0
    difficulty_score: float = 0.0
    opportunity_score: float = 0.0
    target_audience: Dict[str, Any] = field(default_factory=dict)
    content_angles: List[str] = field(default_factory=list)
    competitor_content: List[str] = field(default_factory=list)
    recommended_length: int = 0
    recommended_format: ContentFormat = ContentFormat.MEDIUM_FORM
    seasonal_factors: Dict[str, float] = field(default_factory=dict)
    trending_score: float = 0.0
    implementation_priority: int = 1
    estimated_effort: str = "medium"
    roi_estimate: float = 0.0
    discovered_date: datetime = field(default_factory=datetime.now)


@dataclass
class CompetitorContentAnalysis:
    """Competitor content analysis results"""
    competitor_domain: str
    total_content_pieces: int = 0
    content_types: Dict[str, int] = field(default_factory=dict)
    content_formats: Dict[str, int] = field(default_factory=dict)
    top_topics: List[str] = field(default_factory=list)
    average_word_count: float = 0.0
    content_frequency: float = 0.0  # pieces per month
    quality_score: float = 0.0
    content_gaps_vs_us: List[str] = field(default_factory=list)
    content_strengths: List[str] = field(default_factory=list)
    content_weaknesses: List[str] = field(default_factory=list)


class ContentGapIdentifier:
    """Advanced content gap identification using AI and competitive analysis"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Content Gap Identifier
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.content_database: Dict[str, ContentPiece] = {}
        self.content_gaps: Dict[str, ContentGap] = {}
        self.competitor_analysis: Dict[str, CompetitorContentAnalysis] = {}
        self.topic_clusters: Dict[str, List[str]] = {}
        
        # AI Models setup
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2
        )
        self.clusterer = DBSCAN(eps=0.3, min_samples=2)
        self.topic_model = LatentDirichletAllocation(
            n_components=20,
            random_state=42,
            max_iter=100
        )
        
        # Configuration parameters
        self.min_opportunity_score = self.config.get('min_opportunity_score', 0.6)
        self.max_competition_level = self.config.get('max_competition_level', 0.8)
        self.trending_weight = self.config.get('trending_weight', 0.2)
        self.freshness_weight = self.config.get('freshness_weight', 0.3)
        self.comprehensiveness_weight = self.config.get('comprehensiveness_weight', 0.4)
    
    async def identify_content_gaps(
        self,
        our_domain: str,
        competitors: List[str],
        target_keywords: Optional[List[str]] = None,
        target_audience: Optional[Dict[str, Any]] = None
    ) -> List[ContentGap]:
        """Comprehensive content gap identification
        
        Args:
            our_domain: Our domain to analyze
            competitors: List of competitor domains
            target_keywords: Keywords to focus on
            target_audience: Target audience information
            
        Returns:
            List of identified content gaps
        """
        try:
            logger.info(f"Starting content gap analysis for {our_domain}")
            
            # Analyze our content
            our_content = await self._analyze_domain_content(our_domain)
            
            # Analyze competitor content
            competitor_content = {}
            for competitor in competitors:
                competitor_content[competitor] = await self._analyze_domain_content(competitor)
            
            # Perform competitive content analysis
            competitive_analysis = await self._perform_competitive_analysis(
                our_content, competitor_content
            )
            
            # Identify topic gaps
            topic_gaps = await self._identify_topic_gaps(our_content, competitor_content)
            
            # Identify format gaps
            format_gaps = await self._identify_format_gaps(our_content, competitor_content)
            
            # Identify intent gaps
            intent_gaps = await self._identify_intent_gaps(our_content, competitor_content)
            
            # Analyze keyword gaps
            keyword_gaps = await self._analyze_keyword_gaps(
                our_content, competitor_content, target_keywords
            )
            
            # Identify trending content opportunities
            trending_gaps = await self._identify_trending_opportunities(target_keywords)
            
            # Analyze seasonal content gaps
            seasonal_gaps = await self._analyze_seasonal_gaps(our_content)
            
            # Combine all gaps
            all_gaps = topic_gaps + format_gaps + intent_gaps + keyword_gaps + trending_gaps + seasonal_gaps
            
            # Score and prioritize gaps
            prioritized_gaps = await self._prioritize_content_gaps(all_gaps, target_audience)
            
            # Store results
            for gap in prioritized_gaps:
                self.content_gaps[gap.gap_id] = gap
            
            logger.info(f"Identified {len(prioritized_gaps)} content gaps")
            return prioritized_gaps
            
        except Exception as e:
            logger.error(f"Error in content gap analysis: {str(e)}")
            return []
    
    async def _analyze_domain_content(self, domain: str) -> List[ContentPiece]:
        """Analyze content for a specific domain"""
        try:
            content_pieces = []
            
            # Simulate content discovery
            # In production, this would crawl and analyze actual content
            num_pieces = np.random.randint(50, 300)
            
            content_types = list(ContentType)
            content_formats = list(ContentFormat)
            search_intents = list(SearchIntent)
            
            for i in range(num_pieces):
                content = ContentPiece(
                    title=f"Sample Content {i} - {domain}",
                    url=f"https://{domain}/content/{i}",
                    content_type=np.random.choice(content_types),
                    content_format=np.random.choice(content_formats),
                    word_count=np.random.randint(300, 3000),
                    domain=domain,
                    author=f"Author {i % 10}",
                    search_intent=np.random.choice(search_intents),
                    quality_score=np.random.uniform(0.3, 0.95),
                    freshness_score=np.random.uniform(0.1, 1.0),
                    comprehensiveness_score=np.random.uniform(0.2, 0.9)
                )
                
                # Generate topics and keywords
                content.topics = await self._extract_topics(content.title)
                content.keywords = await self._extract_keywords(content.title, content.topics)
                
                # Set engagement metrics
                content.engagement_metrics = {
                    "page_views": np.random.randint(100, 10000),
                    "time_on_page": np.random.uniform(60, 600),
                    "bounce_rate": np.random.uniform(0.2, 0.8),
                    "social_shares": np.random.randint(0, 500),
                    "comments": np.random.randint(0, 100)
                }
                
                # Set SEO metrics
                content.seo_metrics = {
                    "organic_traffic": np.random.randint(10, 5000),
                    "keyword_rankings": np.random.randint(1, 100),
                    "backlinks": np.random.randint(0, 200),
                    "domain_authority": np.random.uniform(20, 90)
                }
                
                content_pieces.append(content)
                self.content_database[content.content_id] = content
            
            return content_pieces
            
        except Exception as e:
            logger.error(f"Error analyzing domain content: {str(e)}")
            return []
    
    async def _perform_competitive_analysis(
        self,
        our_content: List[ContentPiece],
        competitor_content: Dict[str, List[ContentPiece]]
    ) -> Dict[str, CompetitorContentAnalysis]:
        """Perform detailed competitive content analysis"""
        try:
            analysis_results = {}
            
            # Analyze our content characteristics
            our_topics = self._extract_all_topics(our_content)
            our_content_types = Counter([c.content_type.value for c in our_content])
            our_formats = Counter([c.content_format.value for c in our_content])
            
            for competitor_domain, content_list in competitor_content.items():
                analysis = CompetitorContentAnalysis(
                    competitor_domain=competitor_domain,
                    total_content_pieces=len(content_list)
                )
                
                # Analyze content types and formats
                analysis.content_types = dict(Counter([c.content_type.value for c in content_list]))
                analysis.content_formats = dict(Counter([c.content_format.value for c in content_list]))
                
                # Extract top topics
                competitor_topics = self._extract_all_topics(content_list)
                analysis.top_topics = list(competitor_topics.most_common(20))
                
                # Calculate metrics
                word_counts = [c.word_count for c in content_list if c.word_count > 0]
                analysis.average_word_count = statistics.mean(word_counts) if word_counts else 0
                
                # Estimate content frequency (pieces per month)
                if content_list:
                    date_range = max(c.publish_date for c in content_list) - min(c.publish_date for c in content_list)
                    months = max(date_range.days / 30, 1)
                    analysis.content_frequency = len(content_list) / months
                
                # Calculate quality score
                quality_scores = [c.quality_score for c in content_list]
                analysis.quality_score = statistics.mean(quality_scores) if quality_scores else 0
                
                # Identify gaps vs our content
                competitor_topic_set = set(topic for topic, _ in competitor_topics.most_common(50))
                our_topic_set = set(topic for topic, _ in our_topics.most_common(50))
                
                analysis.content_gaps_vs_us = list(competitor_topic_set - our_topic_set)
                
                # Identify strengths and weaknesses
                analysis.content_strengths = await self._identify_competitor_strengths(content_list)
                analysis.content_weaknesses = await self._identify_competitor_weaknesses(content_list)
                
                analysis_results[competitor_domain] = analysis
                self.competitor_analysis[competitor_domain] = analysis
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error in competitive analysis: {str(e)}")
            return {}
    
    async def _identify_topic_gaps(
        self,
        our_content: List[ContentPiece],
        competitor_content: Dict[str, List[ContentPiece]]
    ) -> List[ContentGap]:
        """Identify topic-based content gaps"""
        try:
            gaps = []
            
            # Extract all topics from our content and competitors
            our_topics = set(self._extract_all_topics(our_content).keys())
            
            # Combine all competitor topics
            all_competitor_topics = Counter()
            for content_list in competitor_content.values():
                competitor_topics = self._extract_all_topics(content_list)
                all_competitor_topics.update(competitor_topics)
            
            # Find topics covered by competitors but not by us
            missing_topics = set(all_competitor_topics.keys()) - our_topics
            
            for topic in missing_topics:
                if all_competitor_topics[topic] >= 3:  # Topic covered by multiple pieces
                    # Estimate traffic and competition
                    estimated_traffic = await self._estimate_topic_traffic(topic)
                    competition_level = await self._calculate_topic_competition(topic, competitor_content)
                    
                    # Calculate opportunity score
                    opportunity_score = await self._calculate_opportunity_score(
                        estimated_traffic, competition_level, all_competitor_topics[topic]
                    )
                    
                    if opportunity_score >= self.min_opportunity_score:
                        gap = ContentGap(
                            topic=topic,
                            keywords=await self._generate_topic_keywords(topic),
                            search_intent=await self._determine_topic_intent(topic),
                            estimated_traffic=estimated_traffic,
                            competition_level=competition_level,
                            opportunity_score=opportunity_score,
                            gap_severity=await self._classify_gap_severity(opportunity_score),
                            content_angles=await self._generate_content_angles(topic),
                            recommended_length=await self._recommend_content_length(topic),
                            recommended_format=await self._recommend_content_format(topic)
                        )
                        gaps.append(gap)
            
            return gaps
            
        except Exception as e:
            logger.error(f"Error identifying topic gaps: {str(e)}")
            return []
    
    async def _identify_format_gaps(
        self,
        our_content: List[ContentPiece],
        competitor_content: Dict[str, List[ContentPiece]]
    ) -> List[ContentGap]:
        """Identify content format gaps"""
        try:
            gaps = []
            
            # Analyze our format distribution
            our_formats = Counter([c.content_format.value for c in our_content])
            our_types = Counter([c.content_type.value for c in our_content])
            
            # Analyze competitor format usage
            competitor_formats = Counter()
            competitor_types = Counter()
            
            for content_list in competitor_content.values():
                for content in content_list:
                    competitor_formats[content.content_format.value] += 1
                    competitor_types[content.content_type.value] += 1
            
            # Identify underutilized formats
            all_formats = set(list(ContentFormat))
            all_types = set(list(ContentType))
            
            for format_enum in all_formats:
                format_value = format_enum.value
                our_count = our_formats.get(format_value, 0)
                competitor_count = competitor_formats.get(format_value, 0)
                
                # Check if competitors are using this format significantly more
                if competitor_count > our_count * 2 and competitor_count >= 10:
                    # This is a format gap
                    estimated_traffic = competitor_count * 50  # Rough estimate
                    competition_level = 0.6  # Format gaps usually have medium competition
                    
                    opportunity_score = await self._calculate_opportunity_score(
                        estimated_traffic, competition_level, competitor_count - our_count
                    )
                    
                    gap = ContentGap(
                        topic=f"{format_value}_content_opportunity",
                        keywords=[f"{format_value} content"],
                        formats_missing=[format_enum],
                        estimated_traffic=estimated_traffic,
                        competition_level=competition_level,
                        opportunity_score=opportunity_score,
                        gap_severity=await self._classify_gap_severity(opportunity_score),
                        recommended_format=format_enum,
                        content_angles=await self._generate_format_angles(format_enum)
                    )
                    gaps.append(gap)
            
            # Check content types
            for type_enum in all_types:
                type_value = type_enum.value
                our_count = our_types.get(type_value, 0)
                competitor_count = competitor_types.get(type_value, 0)
                
                if competitor_count > our_count * 2 and competitor_count >= 8:
                    estimated_traffic = competitor_count * 75
                    competition_level = 0.5
                    
                    opportunity_score = await self._calculate_opportunity_score(
                        estimated_traffic, competition_level, competitor_count - our_count
                    )
                    
                    gap = ContentGap(
                        topic=f"{type_value}_content_opportunity",
                        keywords=[f"{type_value} content"],
                        content_types_missing=[type_enum],
                        estimated_traffic=estimated_traffic,
                        competition_level=competition_level,
                        opportunity_score=opportunity_score,
                        gap_severity=await self._classify_gap_severity(opportunity_score),
                        content_angles=await self._generate_type_angles(type_enum)
                    )
                    gaps.append(gap)
            
            return gaps
            
        except Exception as e:
            logger.error(f"Error identifying format gaps: {str(e)}")
            return []
    
    async def _identify_intent_gaps(
        self,
        our_content: List[ContentPiece],
        competitor_content: Dict[str, List[ContentPiece]]
    ) -> List[ContentGap]:
        """Identify search intent gaps"""
        try:
            gaps = []
            
            # Analyze intent distribution
            our_intents = Counter([c.search_intent.value for c in our_content])
            competitor_intents = Counter()
            
            for content_list in competitor_content.values():
                for content in content_list:
                    competitor_intents[content.search_intent.value] += 1
            
            # Check each intent type
            for intent_enum in SearchIntent:
                intent_value = intent_enum.value
                our_count = our_intents.get(intent_value, 0)
                competitor_count = competitor_intents.get(intent_value, 0)
                
                # Calculate coverage ratio
                our_ratio = our_count / len(our_content) if our_content else 0
                competitor_ratio = competitor_count / sum(competitor_intents.values()) if competitor_intents else 0
                
                # Identify significant gaps
                if competitor_ratio > our_ratio * 1.5 and competitor_count >= 15:
                    estimated_traffic = competitor_count * 60
                    competition_level = 0.55
                    
                    opportunity_score = await self._calculate_opportunity_score(
                        estimated_traffic, competition_level, competitor_count - our_count
                    )
                    
                    gap = ContentGap(
                        topic=f"{intent_value}_intent_content",
                        keywords=await self._generate_intent_keywords(intent_enum),
                        search_intent=intent_enum,
                        estimated_traffic=estimated_traffic,
                        competition_level=competition_level,
                        opportunity_score=opportunity_score,
                        gap_severity=await self._classify_gap_severity(opportunity_score),
                        content_angles=await self._generate_intent_angles(intent_enum)
                    )
                    gaps.append(gap)
            
            return gaps
            
        except Exception as e:
            logger.error(f"Error identifying intent gaps: {str(e)}")
            return []
    
    async def _analyze_keyword_gaps(
        self,
        our_content: List[ContentPiece],
        competitor_content: Dict[str, List[ContentPiece]],
        target_keywords: Optional[List[str]] = None
    ) -> List[ContentGap]:
        """Analyze keyword-specific content gaps"""
        try:
            gaps = []
            
            if not target_keywords:
                return gaps
            
            # Extract keywords from our content
            our_keywords = set()
            for content in our_content:
                our_keywords.update(content.keywords)
            
            # Extract keywords from competitor content
            competitor_keywords = Counter()
            for content_list in competitor_content.values():
                for content in content_list:
                    competitor_keywords.update(content.keywords)
            
            # Check each target keyword
            for keyword in target_keywords:
                our_coverage = keyword.lower() in {k.lower() for k in our_keywords}
                competitor_coverage = competitor_keywords.get(keyword.lower(), 0)
                
                if not our_coverage and competitor_coverage >= 2:
                    # This is a keyword gap
                    estimated_traffic = await self._estimate_keyword_traffic(keyword)
                    competition_level = min(competitor_coverage / 10, 1.0)
                    
                    opportunity_score = await self._calculate_opportunity_score(
                        estimated_traffic, competition_level, competitor_coverage
                    )
                    
                    gap = ContentGap(
                        topic=f"Content for '{keyword}'",
                        keywords=[keyword],
                        search_intent=await self._determine_keyword_intent(keyword),
                        estimated_traffic=estimated_traffic,
                        competition_level=competition_level,
                        opportunity_score=opportunity_score,
                        gap_severity=await self._classify_gap_severity(opportunity_score),
                        content_angles=await self._generate_keyword_angles(keyword),
                        recommended_length=await self._recommend_keyword_content_length(keyword)
                    )
                    gaps.append(gap)
            
            return gaps
            
        except Exception as e:
            logger.error(f"Error analyzing keyword gaps: {str(e)}")
            return []
    
    async def _identify_trending_opportunities(self, target_keywords: Optional[List[str]]) -> List[ContentGap]:
        """Identify trending content opportunities"""
        try:
            gaps = []
            
            # Get trending topics (simulated)
            trending_topics = await self._get_trending_topics()
            
            for topic in trending_topics:
                # Check if we should focus on this trending topic
                if target_keywords and not any(keyword in topic for keyword in target_keywords):
                    continue
                
                # Calculate trending metrics
                trending_score = await self._calculate_trending_score(topic)
                estimated_traffic = await self._estimate_trending_traffic(topic)
                competition_level = 0.3  # Trending topics usually have lower initial competition
                
                opportunity_score = await self._calculate_opportunity_score(
                    estimated_traffic, competition_level, 0
                ) + (trending_score * self.trending_weight)
                
                gap = ContentGap(
                    topic=topic,
                    keywords=await self._generate_trending_keywords(topic),
                    search_intent=SearchIntent.INFORMATIONAL,
                    estimated_traffic=estimated_traffic,
                    competition_level=competition_level,
                    opportunity_score=min(opportunity_score, 1.0),
                    trending_score=trending_score,
                    gap_severity=await self._classify_gap_severity(opportunity_score),
                    content_angles=await self._generate_trending_angles(topic),
                    estimated_effort="low",  # Quick to capitalize on trends
                    implementation_priority=1  # High priority due to time sensitivity
                )
                gaps.append(gap)
            
            return gaps
            
        except Exception as e:
            logger.error(f"Error identifying trending opportunities: {str(e)}")
            return []
    
    async def _analyze_seasonal_gaps(self, our_content: List[ContentPiece]) -> List[ContentGap]:
        """Analyze seasonal content opportunities"""
        try:
            gaps = []
            
            # Define seasonal topics
            seasonal_topics = {
                "spring": ["spring_cleaning", "gardening", "fitness", "renewal"],
                "summer": ["vacation", "outdoor_activities", "festivals", "travel"],
                "fall": ["back_to_school", "holiday_prep", "harvesting", "cozy_content"],
                "winter": ["holiday", "new_year", "indoor_activities", "winter_sports"]
            }
            
            current_month = datetime.now().month
            current_season = self._get_season(current_month)
            next_season = self._get_next_season(current_season)
            
            # Check coverage for upcoming season
            seasonal_keywords = seasonal_topics.get(next_season, [])
            
            for seasonal_keyword in seasonal_keywords:
                # Check if we have content covering this seasonal topic
                our_coverage = any(
                    seasonal_keyword in " ".join(content.keywords).lower()
                    for content in our_content
                )
                
                if not our_coverage:
                    estimated_traffic = await self._estimate_seasonal_traffic(seasonal_keyword, next_season)
                    seasonal_factor = await self._calculate_seasonal_factor(seasonal_keyword, next_season)
                    
                    opportunity_score = (estimated_traffic / 5000) * seasonal_factor
                    
                    gap = ContentGap(
                        topic=f"Seasonal: {seasonal_keyword} for {next_season}",
                        keywords=[seasonal_keyword, next_season],
                        search_intent=SearchIntent.INFORMATIONAL,
                        estimated_traffic=estimated_traffic,
                        competition_level=0.4,
                        opportunity_score=min(opportunity_score, 1.0),
                        seasonal_factors={next_season: seasonal_factor},
                        gap_severity=await self._classify_gap_severity(opportunity_score),
                        content_angles=await self._generate_seasonal_angles(seasonal_keyword, next_season),
                        estimated_effort="medium"
                    )
                    gaps.append(gap)
            
            return gaps
            
        except Exception as e:
            logger.error(f"Error analyzing seasonal gaps: {str(e)}")
            return []
    
    async def _prioritize_content_gaps(
        self,
        gaps: List[ContentGap],
        target_audience: Optional[Dict[str, Any]] = None
    ) -> List[ContentGap]:
        """Prioritize content gaps based on multiple factors"""
        try:
            for gap in gaps:
                # Calculate final opportunity score with weights
                final_score = gap.opportunity_score
                
                # Apply trending boost
                if gap.trending_score > 0:
                    final_score += gap.trending_score * self.trending_weight
                
                # Apply seasonal boost
                if gap.seasonal_factors:
                    seasonal_boost = max(gap.seasonal_factors.values()) * 0.15
                    final_score += seasonal_boost
                
                # Audience alignment
                if target_audience:
                    alignment_score = await self._calculate_audience_alignment(gap, target_audience)
                    final_score *= alignment_score
                
                gap.opportunity_score = min(final_score, 1.0)
                
                # Set implementation priority
                if gap.opportunity_score >= 0.8 or gap.trending_score > 0.8:
                    gap.implementation_priority = 1
                elif gap.opportunity_score >= 0.6:
                    gap.implementation_priority = 2
                else:
                    gap.implementation_priority = 3
                
                # Estimate effort and ROI
                gap.estimated_effort = await self._estimate_content_effort(gap)
                gap.roi_estimate = await self._estimate_content_roi(gap)
            
            # Sort by priority and opportunity score
            return sorted(gaps, key=lambda x: (x.implementation_priority, -x.opportunity_score))
            
        except Exception as e:
            logger.error(f"Error prioritizing gaps: {str(e)}")
            return gaps
    
    # Helper methods
    async def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from text"""
        # Simplified topic extraction
        words = re.findall(r'\b\w+\b', text.lower())
        return [word for word in words if len(word) > 3][:5]
    
    async def _extract_keywords(self, title: str, topics: List[str]) -> List[str]:
        """Extract keywords from title and topics"""
        keywords = topics.copy()
        title_words = re.findall(r'\b\w+\b', title.lower())
        keywords.extend([word for word in title_words if len(word) > 2])
        return list(set(keywords))[:10]
    
    def _extract_all_topics(self, content_list: List[ContentPiece]) -> Counter:
        """Extract all topics from content list"""
        all_topics = Counter()
        for content in content_list:
            all_topics.update(content.topics)
        return all_topics
    
    async def _estimate_topic_traffic(self, topic: str) -> float:
        """Estimate traffic potential for topic"""
        # Simplified traffic estimation
        base_traffic = len(topic) * 100
        return base_traffic + np.random.uniform(200, 2000)
    
    async def _calculate_topic_competition(
        self,
        topic: str,
        competitor_content: Dict[str, List[ContentPiece]]
    ) -> float:
        """Calculate competition level for topic"""
        competitor_count = 0
        for content_list in competitor_content.values():
            if any(topic in content.topics for content in content_list):
                competitor_count += 1
        
        return min(competitor_count / len(competitor_content), 1.0) if competitor_content else 0
    
    async def _calculate_opportunity_score(
        self,
        traffic: float,
        competition: float,
        coverage_gap: float
    ) -> float:
        """Calculate overall opportunity score"""
        # Normalize traffic (assuming max 5000)
        traffic_score = min(traffic / 5000, 1.0)
        
        # Competition score (lower is better)
        competition_score = 1.0 - competition
        
        # Coverage gap score
        gap_score = min(coverage_gap / 20, 1.0)
        
        # Weighted average
        opportunity_score = (
            traffic_score * 0.4 +
            competition_score * 0.3 +
            gap_score * 0.3
        )
        
        return min(opportunity_score, 1.0)
    
    async def _classify_gap_severity(self, opportunity_score: float) -> GapSeverity:
        """Classify gap severity based on opportunity score"""
        if opportunity_score >= 0.8:
            return GapSeverity.CRITICAL
        elif opportunity_score >= 0.6:
            return GapSeverity.HIGH
        elif opportunity_score >= 0.4:
            return GapSeverity.MEDIUM
        else:
            return GapSeverity.LOW
    
    async def _generate_content_angles(self, topic: str) -> List[str]:
        """Generate content angles for topic"""
        angles = [
            f"Complete guide to {topic}",
            f"Best practices for {topic}",
            f"Common mistakes in {topic}",
            f"Advanced {topic} strategies",
            f"{topic} for beginners"
        ]
        return angles
    
    async def _recommend_content_length(self, topic: str) -> int:
        """Recommend content length for topic"""
        # Simplified recommendation based on topic complexity
        if len(topic.split()) > 2:
            return np.random.randint(1500, 3000)
        else:
            return np.random.randint(800, 1500)
    
    async def _recommend_content_format(self, topic: str) -> ContentFormat:
        """Recommend content format for topic"""
        formats = [ContentFormat.MEDIUM_FORM, ContentFormat.LONG_FORM, ContentFormat.VISUAL]
        return np.random.choice(formats)
    
    def _get_season(self, month: int) -> str:
        """Get season based on month"""
        if month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        elif month in [9, 10, 11]:
            return "fall"
        else:
            return "winter"
    
    def _get_next_season(self, current_season: str) -> str:
        """Get next season"""
        seasons = ["spring", "summer", "fall", "winter"]
        current_index = seasons.index(current_season)
        return seasons[(current_index + 1) % 4]
    
    # Placeholder methods for external integrations
    async def _identify_competitor_strengths(self, content_list: List[ContentPiece]) -> List[str]:
        return ["comprehensive_coverage", "high_quality_content", "regular_publishing"]
    
    async def _identify_competitor_weaknesses(self, content_list: List[ContentPiece]) -> List[str]:
        return ["outdated_content", "poor_visual_design", "limited_engagement"]
    
    async def _generate_topic_keywords(self, topic: str) -> List[str]:
        return [topic, f"{topic} tips", f"{topic} guide", f"best {topic}"]
    
    async def _determine_topic_intent(self, topic: str) -> SearchIntent:
        return SearchIntent.INFORMATIONAL
    
    async def _generate_format_angles(self, format_enum: ContentFormat) -> List[str]:
        return [f"Create engaging {format_enum.value}", f"Best {format_enum.value} examples"]
    
    async def _generate_type_angles(self, type_enum: ContentType) -> List[str]:
        return [f"How to create {type_enum.value}", f"Best {type_enum.value} strategies"]
    
    async def _generate_intent_keywords(self, intent_enum: SearchIntent) -> List[str]:
        intent_keywords = {
            SearchIntent.INFORMATIONAL: ["how to", "what is", "guide", "tutorial"],
            SearchIntent.NAVIGATIONAL: ["login", "contact", "about", "official"],
            SearchIntent.TRANSACTIONAL: ["buy", "purchase", "order", "subscribe"],
            SearchIntent.COMMERCIAL: ["best", "review", "compare", "vs"]
        }
        return intent_keywords.get(intent_enum, ["general"])
    
    async def _generate_intent_angles(self, intent_enum: SearchIntent) -> List[str]:
        return [f"Content optimized for {intent_enum.value} intent"]
    
    async def _estimate_keyword_traffic(self, keyword: str) -> float:
        return np.random.uniform(500, 3000)
    
    async def _determine_keyword_intent(self, keyword: str) -> SearchIntent:
        if any(word in keyword.lower() for word in ["how", "what", "why", "guide"]):
            return SearchIntent.INFORMATIONAL
        elif any(word in keyword.lower() for word in ["buy", "purchase", "order"]):
            return SearchIntent.TRANSACTIONAL
        elif any(word in keyword.lower() for word in ["best", "review", "compare"]):
            return SearchIntent.COMMERCIAL
        else:
            return SearchIntent.INFORMATIONAL
    
    async def _generate_keyword_angles(self, keyword: str) -> List[str]:
        return [f"Complete guide to {keyword}", f"Best practices for {keyword}"]
    
    async def _recommend_keyword_content_length(self, keyword: str) -> int:
        return np.random.randint(1000, 2500)
    
    async def _get_trending_topics(self) -> List[str]:
        return ["ai automation", "sustainable technology", "remote work tools", "digital wellness"]
    
    async def _calculate_trending_score(self, topic: str) -> float:
        return np.random.uniform(0.6, 1.0)
    
    async def _estimate_trending_traffic(self, topic: str) -> float:
        return np.random.uniform(1500, 5000)
    
    async def _generate_trending_keywords(self, topic: str) -> List[str]:
        return [topic, f"{topic} 2025", f"latest {topic}", f"{topic} trends"]
    
    async def _generate_trending_angles(self, topic: str) -> List[str]:
        return [f"Latest trends in {topic}", f"Future of {topic}", f"{topic} predictions 2025"]
    
    async def _estimate_seasonal_traffic(self, keyword: str, season: str) -> float:
        return np.random.uniform(800, 2500)
    
    async def _calculate_seasonal_factor(self, keyword: str, season: str) -> float:
        return np.random.uniform(0.7, 1.0)
    
    async def _generate_seasonal_angles(self, keyword: str, season: str) -> List[str]:
        return [f"{keyword} for {season}", f"Best {keyword} this {season}"]
    
    async def _calculate_audience_alignment(
        self,
        gap: ContentGap,
        target_audience: Dict[str, Any]
    ) -> float:
        return np.random.uniform(0.8, 1.0)
    
    async def _estimate_content_effort(self, gap: ContentGap) -> str:
        if gap.recommended_length > 2000:
            return "high"
        elif gap.recommended_length > 1000:
            return "medium"
        else:
            return "low"
    
    async def _estimate_content_roi(self, gap: ContentGap) -> float:
        potential_revenue = gap.estimated_traffic * 0.02 * 25  # 2% conversion at $25 value
        estimated_cost = 500  # Content creation cost
        
        if estimated_cost > 0:
            return (potential_revenue - estimated_cost) / estimated_cost
        return 0.0
    
    def get_content_gap_summary(self) -> Dict[str, Any]:
        """Get summary of identified content gaps"""
        try:
            if not self.content_gaps:
                return {}
            
            total_gaps = len(self.content_gaps)
            severity_distribution = Counter([g.gap_severity.value for g in self.content_gaps.values()])
            total_estimated_traffic = sum(g.estimated_traffic for g in self.content_gaps.values())
            
            return {
                "total_content_gaps": total_gaps,
                "severity_distribution": dict(severity_distribution),
                "total_estimated_traffic": total_estimated_traffic,
                "average_opportunity_score": statistics.mean([g.opportunity_score for g in self.content_gaps.values()]),
                "priority_distribution": Counter([g.implementation_priority for g in self.content_gaps.values()]),
                "estimated_total_roi": sum(g.roi_estimate for g in self.content_gaps.values())
            }
            
        except Exception as e:
            logger.error(f"Error generating content gap summary: {str(e)}")
            return {}


# Example usage
async def main():
    """Example usage of Content Gap Identifier"""
    try:
        # Initialize identifier
        config = {
            'min_opportunity_score': 0.5,
            'max_competition_level': 0.8,
            'trending_weight': 0.2,
            'freshness_weight': 0.3
        }
        
        identifier = ContentGapIdentifier(config)
        
        # Example data
        our_domain = "oursite.com"
        competitors = ["competitor1.com", "competitor2.com", "competitor3.com"]
        target_keywords = ["content marketing", "seo optimization", "digital strategy"]
        target_audience = {
            "age_range": "25-45",
            "interests": ["marketing", "technology", "business"],
            "content_preferences": ["guides", "tutorials", "case_studies"]
        }
        
        print(f"🔍 Identifying content gaps for {our_domain}...")
        
        # Identify content gaps
        gaps = await identifier.identify_content_gaps(
            our_domain=our_domain,
            competitors=competitors,
            target_keywords=target_keywords,
            target_audience=target_audience
        )
        
        # Print results
        print(f"\n📊 Found {len(gaps)} content opportunities:")
        for i, gap in enumerate(gaps[:10]):  # Show top 10
            print(f"\n{i+1}. {gap.topic}")
            print(f"   Severity: {gap.gap_severity.value}")
            print(f"   Opportunity Score: {gap.opportunity_score:.2f}")
            print(f"   Estimated Traffic: {gap.estimated_traffic:.0f}")
            print(f"   Competition: {gap.competition_level:.2f}")
            print(f"   Priority: {gap.implementation_priority}")
            print(f"   Recommended Length: {gap.recommended_length} words")
            print(f"   ROI Estimate: {gap.roi_estimate:.1f}x")
            if gap.content_angles:
                print(f"   Content Angles: {', '.join(gap.content_angles[:2])}")
        
        # Get summary
        summary = identifier.get_content_gap_summary()
        print(f"\n📈 Summary:")
        print(f"   Total Gaps: {summary['total_content_gaps']}")
        print(f"   Critical: {summary['severity_distribution'].get('critical', 0)}")
        print(f"   High: {summary['severity_distribution'].get('high', 0)}")
        print(f"   Total Traffic Potential: {summary['total_estimated_traffic']:.0f}")
        print(f"   Average Opportunity Score: {summary['average_opportunity_score']:.2f}")
        print(f"   Estimated Total ROI: {summary['estimated_total_roi']:.1f}x")
        
        print("\n✅ Content Gap Analysis completed!")
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())