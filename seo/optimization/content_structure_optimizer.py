"""
Content Structure Optimizer for Ainflue Platform
===============================================

Advanced content structure optimization for maximum SEO performance.
Analyzes and optimizes content hierarchy, readability, and structure.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import asyncpg
import json
from datetime import datetime
from collections import defaultdict

# NLP imports
import spacy
from textstat import flesch_reading_ease, automated_readability_index
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class ContentType(Enum):
    """Content types for structure optimization."""
    BLOG_POST = "blog_post"
    VIDEO_DESCRIPTION = "video_description"
    SOCIAL_MEDIA = "social_media"
    PODCAST_DESCRIPTION = "podcast_description"
    PRODUCT_DESCRIPTION = "product_description"
    LANDING_PAGE = "landing_page"
    EMAIL_NEWSLETTER = "email_newsletter"

@dataclass
class StructureAnalysis:
    """Structure analysis result."""
    content_id: str
    content_type: ContentType
    heading_structure: Dict[str, int]
    paragraph_count: int
    sentence_count: int
    word_count: int
    readability_score: float
    keyword_density: Dict[str, float]
    internal_links: int
    external_links: int
    images_count: int
    tables_count: int
    lists_count: int
    optimization_score: float
    recommendations: List[str]
    created_at: datetime

@dataclass
class OptimizationSuggestion:
    """Content optimization suggestion."""
    type: str
    priority: int  # 1-5, 1 being highest
    description: str
    implementation: str
    expected_impact: str

class ContentStructureOptimizer:
    """
    Advanced Content Structure Optimizer
    
    Features:
    - Hierarchical heading analysis
    - Content readability optimization
    - Keyword density analysis
    - Link structure optimization
    - Media element optimization
    - Mobile-first structure recommendations
    """
    
    def __init__(self, db_pool -> None: asyncpg.Pool) -> None:
        self.db_pool = db_pool
        self.nlp = None
        self._initialize_nlp()
        
    def _initialize_nlp(self) -> None:
        """Initialize spaCy NLP pipeline."""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy model not found. Some features will be limited.")
            self.nlp = None
    
    async def analyze_content_structure(
        self,
        content: str,
        content_id: str,
        content_type: ContentType,
        target_keywords: Optional[List[str]] = None
    ) -> StructureAnalysis:
        """
        Analyze content structure for SEO optimization.
        
        Args:
            content: HTML or plain text content
            content_id: Unique content identifier
            content_type: Type of content being analyzed
            target_keywords: Keywords to analyze density for
            
        Returns:
            StructureAnalysis object with detailed analysis
        """
        try:
            # Parse HTML content
            soup = BeautifulSoup(content, 'html.parser')
            text_content = soup.get_text()
            
            # Basic content metrics
            word_count = len(text_content.split())
            sentence_count = len(re.split(r'[.!?]+', text_content))
            paragraph_count = len(soup.find_all(['p', 'div'])) or text_content.count('\n\n') + 1
            
            # Heading structure analysis
            heading_structure = self._analyze_heading_structure(soup)
            
            # Readability analysis
            readability_score = self._calculate_readability(text_content)
            
            # Keyword density analysis
            keyword_density = {}
            if target_keywords:
                keyword_density = self._analyze_keyword_density(text_content, target_keywords)
            
            # Link analysis
            internal_links = len(soup.find_all('a', href=re.compile(r'^(?!http)')))
            external_links = len(soup.find_all('a', href=re.compile(r'^http')))
            
            # Media analysis
            images_count = len(soup.find_all('img'))
            tables_count = len(soup.find_all('table'))
            lists_count = len(soup.find_all(['ul', 'ol']))
            
            # Calculate optimization score
            optimization_score = self._calculate_optimization_score(
                heading_structure, word_count, readability_score,
                internal_links, external_links, images_count, content_type
            )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                heading_structure, word_count, readability_score,
                keyword_density, internal_links, external_links,
                images_count, content_type
            )
            
            analysis = StructureAnalysis(
                content_id=content_id,
                content_type=content_type,
                heading_structure=heading_structure,
                paragraph_count=paragraph_count,
                sentence_count=sentence_count,
                word_count=word_count,
                readability_score=readability_score,
                keyword_density=keyword_density,
                internal_links=internal_links,
                external_links=external_links,
                images_count=images_count,
                tables_count=tables_count,
                lists_count=lists_count,
                optimization_score=optimization_score,
                recommendations=recommendations,
                created_at=datetime.utcnow()
            )
            
            # Store analysis in database
            await self._store_analysis(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing content structure: {e}")
            raise
    
    def _analyze_heading_structure(self, soup: BeautifulSoup) -> Dict[str, int]:
        """Analyze heading structure and hierarchy."""
        headings = {}
        for i in range(1, 7):
            count = len(soup.find_all(f'h{i}'))
            if count > 0:
                headings[f'h{i}'] = count
        return headings
    
    def _calculate_readability(self, text: str) -> float:
        """Calculate readability score using multiple metrics."""
        try:
            flesch_score = flesch_reading_ease(text)
            ari_score = automated_readability_index(text)
            # Weighted average (Flesch is more commonly used)
            return (flesch_score * 0.7 + (100 - ari_score * 10) * 0.3)
        except:
            return 50.0  # Default neutral score
    
    def _analyze_keyword_density(self, text: str, keywords: List[str]) -> Dict[str, float]:
        """Analyze keyword density in content."""
        text_lower = text.lower()
        word_count = len(text.split())
        
        density = {}
        for keyword in keywords:
            keyword_lower = keyword.lower()
            count = text_lower.count(keyword_lower)
            density[keyword] = (count / word_count) * 100 if word_count > 0 else 0
            
        return density
    
    def _calculate_optimization_score(
        self,
        heading_structure: Dict[str, int],
        word_count: int,
        readability_score: float,
        internal_links: int,
        external_links: int,
        images_count: int,
        content_type: ContentType
    ) -> float:
        """Calculate overall optimization score (0-100)."""
        score = 0.0
        
        # Heading structure score (20 points max)
        if 'h1' in heading_structure and heading_structure['h1'] == 1:
            score += 10
        if any(f'h{i}' in heading_structure for i in range(2, 4)):
            score += 10
        
        # Word count score (20 points max)
        if content_type == ContentType.BLOG_POST:
            if 1000 <= word_count <= 2500:
                score += 20
            elif 500 <= word_count < 1000:
                score += 15
        elif content_type == ContentType.VIDEO_DESCRIPTION:
            if 100 <= word_count <= 500:
                score += 20
        
        # Readability score (20 points max)
        if 60 <= readability_score <= 80:
            score += 20
        elif 50 <= readability_score < 60 or 80 < readability_score <= 90:
            score += 15
        
        # Links score (20 points max)
        if internal_links >= 2:
            score += 10
        if external_links >= 1:
            score += 10
        
        # Media score (20 points max)
        if images_count > 0:
            score += 10
        if images_count >= word_count // 300:  # At least 1 image per 300 words
            score += 10
        
        return min(score, 100.0)
    
    def _generate_recommendations(
        self,
        heading_structure: Dict[str, int],
        word_count: int,
        readability_score: float,
        keyword_density: Dict[str, float],
        internal_links: int,
        external_links: int,
        images_count: int,
        content_type: ContentType
    ) -> List[str]:
        """Generate specific optimization recommendations."""
        recommendations = []
        
        # Heading recommendations
        if 'h1' not in heading_structure:
            recommendations.append("Add an H1 tag as the main heading")
        elif heading_structure.get('h1', 0) > 1:
            recommendations.append("Use only one H1 tag per page")
        
        if not any(f'h{i}' in heading_structure for i in range(2, 4)):
            recommendations.append("Add H2 and H3 subheadings to improve content structure")
        
        # Word count recommendations
        if content_type == ContentType.BLOG_POST:
            if word_count < 500:
                recommendations.append("Consider expanding content to at least 500 words for better SEO")
            elif word_count > 3000:
                recommendations.append("Consider breaking long content into multiple pages or sections")
        
        # Readability recommendations
        if readability_score < 50:
            recommendations.append("Simplify language and use shorter sentences to improve readability")
        elif readability_score > 90:
            recommendations.append("Add some complexity to avoid overly simple content")
        
        # Keyword density recommendations
        for keyword, density in keyword_density.items():
            if density > 3.0:
                recommendations.append(f"Reduce keyword density for '{keyword}' (currently {density:.1f}%)")
            elif density < 0.5:
                recommendations.append(f"Consider increasing keyword density for '{keyword}' (currently {density:.1f}%)")
        
        # Link recommendations
        if internal_links < 2:
            recommendations.append("Add more internal links to improve site structure")
        if external_links == 0:
            recommendations.append("Consider adding relevant external links to authoritative sources")
        
        # Media recommendations
        if images_count == 0:
            recommendations.append("Add relevant images to improve user engagement")
        elif word_count > 300 and images_count < word_count // 300:
            recommendations.append("Add more images (aim for at least 1 per 300 words)")
        
        return recommendations
    
    async def optimize_content_structure(
        self,
        content: str,
        content_id: str,
        content_type: ContentType,
        target_keywords: Optional[List[str]] = None
    ) -> Tuple[str, List[OptimizationSuggestion]]:
        """
        Optimize content structure and return improved version.
        
        Args:
            content: Original content
            content_id: Content identifier
            content_type: Type of content
            target_keywords: Keywords to optimize for
            
        Returns:
            Tuple of (optimized_content, suggestions)
        """
        try:
            # Analyze current structure
            analysis = await self.analyze_content_structure(
                content, content_id, content_type, target_keywords
            )
            
            # Generate optimization suggestions
            suggestions = await self._generate_optimization_suggestions(analysis)
            
            # Apply automatic optimizations
            optimized_content = await self._apply_automatic_optimizations(
                content, analysis, suggestions
            )
            
            return optimized_content, suggestions
            
        except Exception as e:
            logger.error(f"Error optimizing content structure: {e}")
            raise
    
    async def _generate_optimization_suggestions(
        self,
        analysis: StructureAnalysis
    ) -> List[OptimizationSuggestion]:
        """Generate detailed optimization suggestions."""
        suggestions = []
        
        # High priority suggestions
        if analysis.optimization_score < 60:
            suggestions.append(OptimizationSuggestion(
                type="critical",
                priority=1,
                description="Overall content structure needs significant improvement",
                implementation="Address heading structure, readability, and media elements",
                expected_impact="20-40% improvement in SEO performance"
            ))
        
        # Heading structure suggestions
        if 'h1' not in analysis.heading_structure:
            suggestions.append(OptimizationSuggestion(
                type="heading",
                priority=1,
                description="Missing H1 tag",
                implementation="Add a single H1 tag with primary keyword",
                expected_impact="10-15% improvement in search rankings"
            ))
        
        # Readability suggestions
        if analysis.readability_score < 50:
            suggestions.append(OptimizationSuggestion(
                type="readability",
                priority=2,
                description="Content readability is too low",
                implementation="Use shorter sentences and simpler vocabulary",
                expected_impact="5-10% improvement in user engagement"
            ))
        
        # Keyword density suggestions
        for keyword, density in analysis.keyword_density.items():
            if density > 3.0:
                suggestions.append(OptimizationSuggestion(
                    type="keyword",
                    priority=2,
                    description=f"Keyword '{keyword}' is over-optimized",
                    implementation="Reduce keyword usage and use synonyms",
                    expected_impact="Avoid keyword stuffing penalties"
                ))
        
        return suggestions
    
    async def _apply_automatic_optimizations(
        self,
        content: str,
        analysis: StructureAnalysis,
        suggestions: List[OptimizationSuggestion]
    ) -> str:
        """Apply automatic content optimizations."""
        soup = BeautifulSoup(content, 'html.parser')
        
        # Add missing alt tags to images
        for img in soup.find_all('img'):
            if not img.get('alt'):
                img['alt'] = "Relevant image description needed"
        
        # Optimize heading structure
        if 'h1' not in analysis.heading_structure:
            # If no H1, convert first heading to H1
            first_heading = soup.find(['h2', 'h3', 'h4', 'h5', 'h6'])
            if first_heading:
                first_heading.name = 'h1'
        
        # Add internal link opportunities (placeholder)
        # This would integrate with the internal linking engine
        
        return str(soup)
    
    async def _store_analysis(self, analysis -> None: StructureAnalysis) -> None:
        """Store structure analysis in database."""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO seo_content_structure_analysis 
                    (content_id, content_type, heading_structure, paragraph_count,
                     sentence_count, word_count, readability_score, keyword_density,
                     internal_links, external_links, images_count, tables_count,
                     lists_count, optimization_score, recommendations, created_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
                """, 
                    analysis.content_id,
                    analysis.content_type.value,
                    json.dumps(analysis.heading_structure),
                    analysis.paragraph_count,
                    analysis.sentence_count,
                    analysis.word_count,
                    analysis.readability_score,
                    json.dumps(analysis.keyword_density),
                    analysis.internal_links,
                    analysis.external_links,
                    analysis.images_count,
                    analysis.tables_count,
                    analysis.lists_count,
                    analysis.optimization_score,
                    json.dumps(analysis.recommendations),
                    analysis.created_at
                )
        except Exception as e:
            logger.error(f"Error storing structure analysis: {e}")
    
    async def get_content_optimization_history(
        self,
        content_id: str,
        limit: int = 10
    ) -> List[StructureAnalysis]:
        """Get optimization history for content."""
        try:
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT * FROM seo_content_structure_analysis 
                    WHERE content_id = $1 
                    ORDER BY created_at DESC 
                    LIMIT $2
                """, content_id, limit)
                
                analyses = []
                for row in rows:
                    analysis = StructureAnalysis(
                        content_id=row['content_id'],
                        content_type=ContentType(row['content_type']),
                        heading_structure=json.loads(row['heading_structure']),
                        paragraph_count=row['paragraph_count'],
                        sentence_count=row['sentence_count'],
                        word_count=row['word_count'],
                        readability_score=row['readability_score'],
                        keyword_density=json.loads(row['keyword_density']),
                        internal_links=row['internal_links'],
                        external_links=row['external_links'],
                        images_count=row['images_count'],
                        tables_count=row['tables_count'],
                        lists_count=row['lists_count'],
                        optimization_score=row['optimization_score'],
                        recommendations=json.loads(row['recommendations']),
                        created_at=row['created_at']
                    )
                    analyses.append(analysis)
                
                return analyses
                
        except Exception as e:
            logger.error(f"Error fetching optimization history: {e}")
            return []
    
    async def batch_optimize_content(
        self,
        content_items: List[Tuple[str, str, ContentType]],
        target_keywords: Optional[Dict[str, List[str]]] = None
    ) -> Dict[str, StructureAnalysis]:
        """
        Batch optimize multiple content items.
        
        Args:
            content_items: List of (content_id, content, content_type) tuples
            target_keywords: Dict mapping content_id to keywords
            
        Returns:
            Dict mapping content_id to analysis results
        """
        results = {}
        
        for content_id, content, content_type in content_items:
            keywords = target_keywords.get(content_id) if target_keywords else None
            
            try:
                analysis = await self.analyze_content_structure(
                    content, content_id, content_type, keywords
                )
                results[content_id] = analysis
            except Exception as e:
                logger.error(f"Error optimizing content {content_id}: {e}")
        
        return results
    
    async def get_optimization_metrics(self) -> Dict[str, Any]:
        """Get overall optimization metrics."""
        try:
            async with self.db_pool.acquire() as conn:
                result = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_analyses,
                        AVG(optimization_score) as avg_score,
                        COUNT(CASE WHEN optimization_score >= 80 THEN 1 END) as high_score_count,
                        COUNT(CASE WHEN optimization_score < 60 THEN 1 END) as low_score_count
                    FROM seo_content_structure_analysis
                    WHERE created_at >= NOW() - INTERVAL '30 days'
                """)
                
                return {
                    'total_analyses': result['total_analyses'],
                    'average_score': float(result['avg_score']) if result['avg_score'] else 0,
                    'high_score_count': result['high_score_count'],
                    'low_score_count': result['low_score_count'],
                    'optimization_rate': (result['high_score_count'] / result['total_analyses'] * 100) 
                                       if result['total_analyses'] > 0 else 0
                }
                
        except Exception as e:
            logger.error(f"Error fetching optimization metrics: {e}")
            return {}

# Export classes
__all__ = [
    'ContentStructureOptimizer',
    'StructureAnalysis', 
    'OptimizationSuggestion',
    'ContentType'
]