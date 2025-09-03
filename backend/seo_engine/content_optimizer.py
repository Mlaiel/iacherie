"""Content Optimizer - AI-Powered SEO Content Optimization Engine

Advanced content optimization system for maximizing SEO performance with
AI-driven recommendations, real-time analysis, and multi-platform optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Types of content for optimization"""
    BLOG_POST = "blog_post"
    PRODUCT_PAGE = "product_page"
    LANDING_PAGE = "landing_page"
    VIDEO_DESCRIPTION = "video_description"
    SOCIAL_MEDIA = "social_media"
    EMAIL = "email"
    META_CONTENT = "meta_content"


class OptimizationLevel(Enum):
    """Levels of optimization intensity"""
    BASIC = "basic"
    ADVANCED = "advanced"
    AGGRESSIVE = "aggressive"
    CONSERVATIVE = "conservative"


@dataclass
class ContentMetrics:
    """Content performance metrics"""
    readability_score: float
    keyword_density: Dict[str, float]
    content_length: int
    heading_structure: Dict[str, int]
    internal_links: int
    external_links: int
    image_count: int
    alt_text_coverage: float
    meta_description_length: int
    title_tag_length: int
    schema_markup_present: bool
    loading_speed_score: float


@dataclass
class OptimizationRecommendation:
    """Single optimization recommendation"""
    type: str
    priority: str  # high, medium, low
    description: str
    current_value: Any
    recommended_value: Any
    impact_score: float
    effort_required: str  # easy, medium, hard
    implementation_steps: List[str]


@dataclass
class OptimizedContent:
    """Optimized content result"""
    original_content: str
    optimized_content: str
    title_suggestions: List[str]
    meta_description_suggestions: List[str]
    heading_structure: Dict[str, str]
    keyword_placement: Dict[str, List[int]]
    recommendations: List[OptimizationRecommendation]
    optimization_score: float
    performance_prediction: Dict[str, float]


class ContentOptimizer:
    """AI-powered SEO content optimization engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.target_language = self.config.get('language', 'en')
        self.optimization_level = OptimizationLevel(
            self.config.get('optimization_level', 'advanced')
        )
        
        # Optimization thresholds
        self.thresholds = {
            'keyword_density': {'min': 0.5, 'max': 3.0, 'optimal': 1.5},
            'content_length': {'min': 300, 'optimal': 1500, 'max': 3000},
            'readability_score': {'min': 60, 'optimal': 80},
            'title_length': {'min': 30, 'max': 60},
            'meta_description_length': {'min': 120, 'max': 155}
        }
        
        # SEO scoring weights
        self.scoring_weights = {
            'keyword_optimization': 0.25,
            'content_quality': 0.20,
            'technical_seo': 0.20,
            'user_experience': 0.15,
            'structure': 0.10,
            'meta_optimization': 0.10
        }
        
        logger.info("ContentOptimizer initialized with AI-powered optimization")
    
    async def optimize_content(
        self,
        content: str,
        target_keywords: List[str],
        content_type: ContentType = ContentType.BLOG_POST,
        existing_meta: Optional[Dict[str, str]] = None
    ) -> OptimizedContent:
        """Perform comprehensive content optimization"""
        try:
            logger.info(f"Starting content optimization for {content_type.value}")
            
            # Analyze current content
            current_metrics = await self._analyze_content_metrics(content, target_keywords)
            
            # Generate optimization recommendations
            recommendations = await self._generate_recommendations(
                content, target_keywords, current_metrics, content_type
            )
            
            # Apply optimizations
            optimized_content = await self._apply_optimizations(
                content, target_keywords, recommendations
            )
            
            # Generate title suggestions
            title_suggestions = await self._generate_title_suggestions(
                content, target_keywords, content_type
            )
            
            # Generate meta description suggestions
            meta_descriptions = await self._generate_meta_descriptions(
                content, target_keywords
            )
            
            # Optimize heading structure
            heading_structure = await self._optimize_heading_structure(
                content, target_keywords
            )
            
            # Analyze keyword placement
            keyword_placement = await self._analyze_keyword_placement(
                optimized_content, target_keywords
            )
            
            # Calculate optimization score
            optimization_score = await self._calculate_optimization_score(
                optimized_content, target_keywords, content_type
            )
            
            # Predict performance
            performance_prediction = await self._predict_performance(
                optimized_content, target_keywords, optimization_score
            )
            
            result = OptimizedContent(
                original_content=content,
                optimized_content=optimized_content,
                title_suggestions=title_suggestions,
                meta_description_suggestions=meta_descriptions,
                heading_structure=heading_structure,
                keyword_placement=keyword_placement,
                recommendations=recommendations,
                optimization_score=optimization_score,
                performance_prediction=performance_prediction
            )
            
            logger.info(f"Content optimization completed with score: {optimization_score:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Content optimization failed: {e}")
            raise
    
    async def _analyze_content_metrics(
        self,
        content: str,
        target_keywords: List[str]
    ) -> ContentMetrics:
        """Analyze current content metrics"""
        # Calculate readability score
        readability_score = await self._calculate_readability_score(content)
        
        # Calculate keyword density
        keyword_density = await self._calculate_keyword_density(content, target_keywords)
        
        # Analyze content structure
        content_length = len(content.split())
        heading_structure = await self._analyze_heading_structure(content)
        
        # Count links
        internal_links = len(re.findall(r'<a[^>]*href=["\'][^"\']*["\'][^>]*>', content))
        external_links = len(re.findall(r'<a[^>]*href=["\']https?://[^"\']*["\'][^>]*>', content))
        
        # Count images and alt text
        image_count = len(re.findall(r'<img[^>]*>', content))
        alt_texts = re.findall(r'alt=["\']([^"\']*)["\']', content)
        alt_text_coverage = len(alt_texts) / max(image_count, 1)
        
        # Check meta content (would come from existing_meta in real implementation)
        meta_description_length = 0  # Placeholder
        title_tag_length = 0  # Placeholder
        
        # Check for schema markup
        schema_markup_present = 'schema.org' in content or 'application/ld+json' in content
        
        # Simulate loading speed score
        loading_speed_score = 85.0  # Placeholder
        
        return ContentMetrics(
            readability_score=readability_score,
            keyword_density=keyword_density,
            content_length=content_length,
            heading_structure=heading_structure,
            internal_links=internal_links,
            external_links=external_links,
            image_count=image_count,
            alt_text_coverage=alt_text_coverage,
            meta_description_length=meta_description_length,
            title_tag_length=title_tag_length,
            schema_markup_present=schema_markup_present,
            loading_speed_score=loading_speed_score
        )
    
    async def _calculate_readability_score(self, content: str) -> float:
        """Calculate content readability score using Flesch Reading Ease"""
        # Simplified readability calculation
        sentences = len(re.split(r'[.!?]+', content))
        words = len(content.split())
        syllables = sum(self._count_syllables(word) for word in content.split())
        
        if sentences == 0 or words == 0:
            return 0.0
        
        # Flesch Reading Ease formula
        score = 206.835 - (1.015 * (words / sentences)) - (84.6 * (syllables / words))
        return max(0, min(100, score))
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word"""
        word = word.lower().strip()
        if not word:
            return 0
        
        vowels = 'aeiouy'
        syllable_count = 0
        prev_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllable_count += 1
            prev_was_vowel = is_vowel
        
        # Adjust for silent 'e'
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1
        
        return max(1, syllable_count)
    
    async def _calculate_keyword_density(
        self,
        content: str,
        target_keywords: List[str]
    ) -> Dict[str, float]:
        """Calculate keyword density for target keywords"""
        content_lower = content.lower()
        total_words = len(content.split())
        
        density = {}
        for keyword in target_keywords:
            keyword_lower = keyword.lower()
            count = content_lower.count(keyword_lower)
            density[keyword] = (count / max(total_words, 1)) * 100
        
        return density
    
    async def _analyze_heading_structure(self, content: str) -> Dict[str, int]:
        """Analyze heading structure"""
        headings = {
            'h1': len(re.findall(r'<h1[^>]*>', content, re.IGNORECASE)),
            'h2': len(re.findall(r'<h2[^>]*>', content, re.IGNORECASE)),
            'h3': len(re.findall(r'<h3[^>]*>', content, re.IGNORECASE)),
            'h4': len(re.findall(r'<h4[^>]*>', content, re.IGNORECASE)),
            'h5': len(re.findall(r'<h5[^>]*>', content, re.IGNORECASE)),
            'h6': len(re.findall(r'<h6[^>]*>', content, re.IGNORECASE))
        }
        return headings
    
    async def _generate_recommendations(
        self,
        content: str,
        target_keywords: List[str],
        metrics: ContentMetrics,
        content_type: ContentType
    ) -> List[OptimizationRecommendation]:
        """Generate optimization recommendations"""
        recommendations = []
        
        # Keyword density recommendations
        for keyword, density in metrics.keyword_density.items():
            if density < self.thresholds['keyword_density']['min']:
                recommendations.append(OptimizationRecommendation(
                    type="keyword_optimization",
                    priority="high",
                    description=f"Increase density for keyword '{keyword}'",
                    current_value=f"{density:.2f}%",
                    recommended_value=f"{self.thresholds['keyword_density']['optimal']:.2f}%",
                    impact_score=0.8,
                    effort_required="easy",
                    implementation_steps=[
                        f"Add '{keyword}' naturally in content body",
                        f"Include '{keyword}' in subheadings",
                        f"Use '{keyword}' in image alt text"
                    ]
                ))
            elif density > self.thresholds['keyword_density']['max']:
                recommendations.append(OptimizationRecommendation(
                    type="keyword_optimization",
                    priority="medium",
                    description=f"Reduce keyword stuffing for '{keyword}'",
                    current_value=f"{density:.2f}%",
                    recommended_value=f"{self.thresholds['keyword_density']['optimal']:.2f}%",
                    impact_score=0.6,
                    effort_required="medium",
                    implementation_steps=[
                        f"Replace some instances of '{keyword}' with synonyms",
                        "Use varied anchor text for internal links",
                        "Focus on semantic keywords"
                    ]
                ))
        
        # Content length recommendations
        if metrics.content_length < self.thresholds['content_length']['min']:
            recommendations.append(OptimizationRecommendation(
                type="content_length",
                priority="high",
                description="Increase content length for better SEO",
                current_value=f"{metrics.content_length} words",
                recommended_value=f"{self.thresholds['content_length']['optimal']} words",
                impact_score=0.7,
                effort_required="hard",
                implementation_steps=[
                    "Add more detailed explanations",
                    "Include examples and case studies",
                    "Add FAQ section",
                    "Include related subtopics"
                ]
            ))
        
        # Readability recommendations
        if metrics.readability_score < self.thresholds['readability_score']['min']:
            recommendations.append(OptimizationRecommendation(
                type="readability",
                priority="medium",
                description="Improve content readability",
                current_value=f"{metrics.readability_score:.1f}",
                recommended_value=f"{self.thresholds['readability_score']['optimal']:.1f}",
                impact_score=0.5,
                effort_required="medium",
                implementation_steps=[
                    "Use shorter sentences",
                    "Break up long paragraphs",
                    "Use simpler vocabulary",
                    "Add bullet points and lists"
                ]
            ))
        
        # Heading structure recommendations
        if metrics.heading_structure['h1'] == 0:
            recommendations.append(OptimizationRecommendation(
                type="structure",
                priority="high",
                description="Add H1 heading with primary keyword",
                current_value="0 H1 tags",
                recommended_value="1 H1 tag",
                impact_score=0.9,
                effort_required="easy",
                implementation_steps=[
                    "Add single H1 tag at the top",
                    "Include primary keyword in H1",
                    "Keep H1 under 60 characters"
                ]
            ))
        
        if metrics.heading_structure['h2'] < 2 and metrics.content_length > 500:
            recommendations.append(OptimizationRecommendation(
                type="structure",
                priority="medium",
                description="Add more H2 subheadings for better structure",
                current_value=f"{metrics.heading_structure['h2']} H2 tags",
                recommended_value="3-5 H2 tags",
                impact_score=0.6,
                effort_required="easy",
                implementation_steps=[
                    "Break content into logical sections",
                    "Add H2 tags for main topics",
                    "Include keywords in some H2 tags"
                ]
            ))
        
        # Internal linking recommendations
        if metrics.internal_links < 3 and metrics.content_length > 800:
            recommendations.append(OptimizationRecommendation(
                type="internal_linking",
                priority="medium",
                description="Add more internal links",
                current_value=f"{metrics.internal_links} internal links",
                recommended_value="3-5 internal links",
                impact_score=0.5,
                effort_required="easy",
                implementation_steps=[
                    "Link to related content on your site",
                    "Use descriptive anchor text",
                    "Link to important pages like homepage"
                ]
            ))
        
        # Image optimization recommendations
        if metrics.image_count > 0 and metrics.alt_text_coverage < 0.8:
            recommendations.append(OptimizationRecommendation(
                type="image_optimization",
                priority="medium",
                description="Add alt text to images",
                current_value=f"{metrics.alt_text_coverage*100:.1f}% coverage",
                recommended_value="100% coverage",
                impact_score=0.4,
                effort_required="easy",
                implementation_steps=[
                    "Add descriptive alt text to all images",
                    "Include keywords in alt text when relevant",
                    "Keep alt text under 125 characters"
                ]
            ))
        
        return recommendations
    
    async def _apply_optimizations(
        self,
        content: str,
        target_keywords: List[str],
        recommendations: List[OptimizationRecommendation]
    ) -> str:
        """Apply optimization recommendations to content"""
        optimized_content = content
        
        # Apply keyword optimizations
        for rec in recommendations:
            if rec.type == "keyword_optimization" and "Increase density" in rec.description:
                keyword = rec.description.split("'")[1]
                # Simple keyword insertion (in real implementation, use NLP for natural placement)
                optimized_content = await self._insert_keyword_naturally(
                    optimized_content, keyword
                )
        
        # Apply structure optimizations
        for rec in recommendations:
            if rec.type == "structure" and "Add H1" in rec.description:
                if target_keywords:
                    h1_tag = f"<h1>{target_keywords[0].title()}: Complete Guide</h1>\n"
                    optimized_content = h1_tag + optimized_content
        
        return optimized_content
    
    async def _insert_keyword_naturally(self, content: str, keyword: str) -> str:
        """Insert keyword naturally into content"""
        sentences = re.split(r'(?<=[.!?])\s+', content)
        
        # Find sentences where we can naturally insert the keyword
        for i, sentence in enumerate(sentences):
            if len(sentence.split()) > 10 and keyword.lower() not in sentence.lower():
                # Simple insertion at the beginning of a sentence
                sentences[i] = f"{keyword} {sentence.lower()}"
                break
        
        return ' '.join(sentences)
    
    async def _generate_title_suggestions(
        self,
        content: str,
        target_keywords: List[str],
        content_type: ContentType
    ) -> List[str]:
        """Generate SEO-optimized title suggestions"""
        if not target_keywords:
            return ["Optimized Title"]
        
        primary_keyword = target_keywords[0]
        suggestions = []
        
        # Template-based titles
        templates = [
            f"Ultimate Guide to {primary_keyword.title()}",
            f"How to Master {primary_keyword.title()} in 2025",
            f"{primary_keyword.title()}: Everything You Need to Know",
            f"Best {primary_keyword.title()} Tips and Strategies",
            f"Complete {primary_keyword.title()} Tutorial for Beginners",
            f"{primary_keyword.title()} Explained: Step-by-Step Guide",
            f"Why {primary_keyword.title()} is Essential for Success",
            f"Top 10 {primary_keyword.title()} Secrets Revealed"
        ]
        
        # Filter by content type
        if content_type == ContentType.PRODUCT_PAGE:
            suggestions.extend([
                f"Buy {primary_keyword.title()} - Best Prices & Reviews",
                f"{primary_keyword.title()} for Sale - Premium Quality",
                f"Professional {primary_keyword.title()} Solutions"
            ])
        elif content_type == ContentType.BLOG_POST:
            suggestions.extend(templates[:5])
        else:
            suggestions.extend(templates[:3])
        
        # Ensure titles are within optimal length
        return [title for title in suggestions if 30 <= len(title) <= 60][:8]
    
    async def _generate_meta_descriptions(
        self,
        content: str,
        target_keywords: List[str]
    ) -> List[str]:
        """Generate SEO-optimized meta descriptions"""
        if not target_keywords:
            return ["SEO-optimized content for better search rankings."]
        
        primary_keyword = target_keywords[0]
        
        # Extract first few sentences for context
        sentences = re.split(r'[.!?]+', content)
        first_sentence = sentences[0] if sentences else ""
        
        descriptions = [
            f"Learn everything about {primary_keyword} with our comprehensive guide. "
            f"Get expert tips, strategies, and actionable insights for better results.",
            
            f"Discover the best {primary_keyword} techniques and strategies. "
            f"Step-by-step tutorials and expert advice for optimal performance.",
            
            f"Master {primary_keyword} with our detailed guide. "
            f"Proven methods, practical tips, and expert insights to boost your success.",
            
            f"Complete {primary_keyword} resource with practical examples. "
            f"Learn from experts and implement proven strategies today.",
            
            f"Everything you need to know about {primary_keyword}. "
            f"Expert guidance, best practices, and actionable tips for success."
        ]
        
        # Ensure descriptions are within optimal length
        return [desc for desc in descriptions if 120 <= len(desc) <= 155]
    
    async def _optimize_heading_structure(
        self,
        content: str,
        target_keywords: List[str]
    ) -> Dict[str, str]:
        """Optimize heading structure with keywords"""
        headings = {}
        
        if target_keywords:
            primary_keyword = target_keywords[0]
            
            headings['h1'] = f"{primary_keyword.title()}: Complete Guide"
            headings['h2_1'] = f"Understanding {primary_keyword.title()}"
            headings['h2_2'] = f"Best Practices for {primary_keyword.title()}"
            headings['h2_3'] = f"Advanced {primary_keyword.title()} Strategies"
            headings['h2_4'] = f"Common {primary_keyword.title()} Mistakes to Avoid"
            
            if len(target_keywords) > 1:
                secondary_keyword = target_keywords[1]
                headings['h2_5'] = f"{secondary_keyword.title()} Integration"
        
        return headings
    
    async def _analyze_keyword_placement(
        self,
        content: str,
        target_keywords: List[str]
    ) -> Dict[str, List[int]]:
        """Analyze keyword placement positions in content"""
        placement = {}
        content_lower = content.lower()
        
        for keyword in target_keywords:
            keyword_lower = keyword.lower()
            positions = []
            
            start = 0
            while True:
                pos = content_lower.find(keyword_lower, start)
                if pos == -1:
                    break
                positions.append(pos)
                start = pos + 1
            
            placement[keyword] = positions
        
        return placement
    
    async def _calculate_optimization_score(
        self,
        content: str,
        target_keywords: List[str],
        content_type: ContentType
    ) -> float:
        """Calculate overall optimization score"""
        scores = {}
        
        # Keyword optimization score
        keyword_density = await self._calculate_keyword_density(content, target_keywords)
        keyword_score = 0
        for keyword, density in keyword_density.items():
            if self.thresholds['keyword_density']['min'] <= density <= self.thresholds['keyword_density']['max']:
                keyword_score += 1
        keyword_score = (keyword_score / max(len(target_keywords), 1)) * 100
        scores['keyword_optimization'] = keyword_score
        
        # Content quality score
        readability = await self._calculate_readability_score(content)
        content_length = len(content.split())
        
        length_score = 100 if content_length >= self.thresholds['content_length']['optimal'] else \
                      (content_length / self.thresholds['content_length']['optimal']) * 100
        
        quality_score = (readability + length_score) / 2
        scores['content_quality'] = min(100, quality_score)
        
        # Technical SEO score (simplified)
        technical_score = 75  # Placeholder for technical aspects
        scores['technical_seo'] = technical_score
        
        # User experience score
        ux_score = min(100, readability + 20)  # Simplified UX score
        scores['user_experience'] = ux_score
        
        # Structure score
        headings = await self._analyze_heading_structure(content)
        structure_score = min(100, (headings['h1'] * 40 + headings['h2'] * 10) * 10)
        scores['structure'] = structure_score
        
        # Meta optimization score (placeholder)
        scores['meta_optimization'] = 80
        
        # Calculate weighted average
        total_score = sum(
            scores[component] * weight
            for component, weight in self.scoring_weights.items()
        )
        
        return round(total_score, 2)
    
    async def _predict_performance(
        self,
        content: str,
        target_keywords: List[str],
        optimization_score: float
    ) -> Dict[str, float]:
        """Predict content performance based on optimization"""
        # Simplified performance prediction
        base_performance = optimization_score / 100
        
        predictions = {
            'search_ranking_improvement': round(base_performance * 30, 1),
            'organic_traffic_increase': round(base_performance * 25, 1),
            'engagement_rate_boost': round(base_performance * 15, 1),
            'click_through_rate_improvement': round(base_performance * 20, 1),
            'conversion_rate_increase': round(base_performance * 10, 1)
        }
        
        return predictions


# Export main class
__all__ = ['ContentOptimizer', 'OptimizedContent', 'OptimizationRecommendation', 'ContentType', 'OptimizationLevel']