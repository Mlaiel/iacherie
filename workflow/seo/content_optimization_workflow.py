"""Content Optimization Workflow - AI-powered content enhancement for maximum SEO impact.

This module provides comprehensive content optimization capabilities including readability analysis,
keyword optimization, structure enhancement, and platform-specific content adaptation for
improved search visibility and user engagement.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Ainflue Platform. All rights reserved.
Licensed under proprietary license - reproduction forbidden without written authorization.
"""

import asyncio
import re
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import json
import math
from collections import Counter


class ContentQuality(Enum):
    """Content quality assessment levels."""
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    BELOW_AVERAGE = "below_average"
    POOR = "poor"


class ReadabilityLevel(Enum):
    """Content readability levels."""
    VERY_EASY = "very_easy"
    EASY = "easy"
    FAIRLY_EASY = "fairly_easy"
    STANDARD = "standard"
    FAIRLY_DIFFICULT = "fairly_difficult"
    DIFFICULT = "difficult"
    VERY_DIFFICULT = "very_difficult"


class ContentStructure(Enum):
    """Content structure types."""
    ARTICLE = "article"
    LISTICLE = "listicle"
    TUTORIAL = "tutorial"
    REVIEW = "review"
    COMPARISON = "comparison"
    INTERVIEW = "interview"
    NEWS = "news"


@dataclass
class ReadabilityMetrics:
    """Comprehensive readability analysis metrics."""
    flesch_score: float
    flesch_kincaid_grade: float
    readability_level: ReadabilityLevel
    avg_sentence_length: float
    avg_syllables_per_word: float
    complex_words_percentage: float
    passive_voice_percentage: float
    suggestions: List[str] = field(default_factory=list)


@dataclass
class KeywordOptimization:
    """Keyword optimization analysis and recommendations."""
    target_keyword: str
    current_density: float
    recommended_density: float
    keyword_frequency: int
    keyword_variations: List[str]
    placement_analysis: Dict[str, bool]  # title, meta, headers, etc.
    semantic_keywords: List[str]
    lsi_keywords: List[str]
    optimization_score: float
    recommendations: List[str] = field(default_factory=list)


@dataclass
class ContentStructureAnalysis:
    """Content structure and organization analysis."""
    structure_type: ContentStructure
    heading_hierarchy: List[Dict[str, Any]]
    paragraph_count: int
    avg_paragraph_length: float
    internal_links: int
    external_links: int
    image_count: int
    video_count: int
    word_count: int
    structure_score: float
    improvements: List[str] = field(default_factory=list)


@dataclass
class ContentScore:
    """Overall content quality and optimization scores."""
    overall_score: float
    seo_score: float
    readability_score: float
    structure_score: float
    engagement_score: float
    uniqueness_score: float
    quality_level: ContentQuality
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)


@dataclass
class OptimizationMetrics:
    """Comprehensive content optimization metrics and analysis."""
    content_score: ContentScore
    readability_metrics: ReadabilityMetrics
    keyword_optimization: KeywordOptimization
    structure_analysis: ContentStructureAnalysis
    platform_adaptations: Dict[str, Dict[str, Any]]
    optimization_recommendations: List[Dict[str, Any]]
    optimized_content: str
    metadata_suggestions: Dict[str, str]


class ContentOptimizationWorkflow:
    """Advanced content optimization workflow with AI-powered analysis."""
    
    def __init__(self):
        """Initialize the content optimization workflow."""
        self.optimization_engines = {
            "readability": self._analyze_readability,
            "keyword_optimization": self._optimize_keywords,
            "structure": self._analyze_structure,
            "engagement": self._enhance_engagement,
            "uniqueness": self._check_uniqueness
        }
        
        self.platform_optimizers = {
            "google": self._optimize_for_google,
            "youtube": self._optimize_for_youtube,
            "instagram": self._optimize_for_instagram,
            "tiktok": self._optimize_for_tiktok,
            "linkedin": self._optimize_for_linkedin
        }
    
    async def execute(self, content_data: Dict[str, Any], config: Any) -> Dict[str, Any]:
        """Execute comprehensive content optimization workflow.
        
        Args:
            content_data: Content information for optimization
            config: Workflow configuration
            
        Returns:
            Comprehensive content optimization results
        """
        try:
            # Extract content parameters
            content_text = content_data.get("content", "")
            title = content_data.get("title", "")
            target_keywords = content_data.get("target_keywords", [])
            target_platforms = content_data.get("target_platforms", ["google"])
            content_type = content_data.get("content_type", "article")
            target_audience = content_data.get("target_audience", "general")
            
            if not content_text:
                raise ValueError("Content text is required for optimization")
            
            # Step 1: Analyze current content
            readability_metrics = await self._analyze_readability(content_text)
            structure_analysis = await self._analyze_structure(content_text, title)
            
            # Step 2: Keyword optimization
            primary_keyword = target_keywords[0] if target_keywords else ""
            keyword_optimization = await self._optimize_keywords(
                content_text, primary_keyword, target_keywords
            )
            
            # Step 3: Content scoring
            content_score = await self._calculate_content_score(
                content_text, readability_metrics, keyword_optimization, structure_analysis
            )
            
            # Step 4: Generate optimized content
            optimized_content = await self._generate_optimized_content(
                content_text, keyword_optimization, structure_analysis, target_audience
            )
            
            # Step 5: Platform-specific adaptations
            platform_adaptations = await self._create_platform_adaptations(
                optimized_content, target_platforms, target_keywords
            )
            
            # Step 6: Generate metadata suggestions
            metadata_suggestions = await self._generate_metadata_suggestions(
                optimized_content, target_keywords, content_type
            )
            
            # Step 7: Create optimization recommendations
            recommendations = await self._generate_optimization_recommendations(
                content_score, readability_metrics, keyword_optimization, structure_analysis
            )
            
            # Create comprehensive optimization metrics
            optimization_metrics = OptimizationMetrics(
                content_score=content_score,
                readability_metrics=readability_metrics,
                keyword_optimization=keyword_optimization,
                structure_analysis=structure_analysis,
                platform_adaptations=platform_adaptations,
                optimization_recommendations=recommendations,
                optimized_content=optimized_content,
                metadata_suggestions=metadata_suggestions
            )
            
            return {
                "status": "completed",
                "score": content_score.overall_score,
                "optimization_metrics": optimization_metrics,
                "recommendations": recommendations,
                "optimized_content": optimized_content,
                "metadata_suggestions": metadata_suggestions,
                "metrics": {
                    "original_word_count": len(content_text.split()),
                    "optimized_word_count": len(optimized_content.split()),
                    "readability_improvement": self._calculate_readability_improvement(readability_metrics),
                    "seo_score": content_score.seo_score,
                    "optimization_opportunities": len(recommendations)
                }
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "score": 0.0,
                "recommendations": [],
                "metrics": {}
            }
    
    async def _analyze_readability(self, content: str) -> ReadabilityMetrics:
        """Analyze content readability using multiple metrics."""
        sentences = self._split_sentences(content)
        words = content.split()
        
        if not sentences or not words:
            return ReadabilityMetrics(
                flesch_score=0.0,
                flesch_kincaid_grade=0.0,
                readability_level=ReadabilityLevel.VERY_DIFFICULT,
                avg_sentence_length=0.0,
                avg_syllables_per_word=0.0,
                complex_words_percentage=0.0,
                passive_voice_percentage=0.0
            )
        
        # Calculate basic metrics
        total_sentences = len(sentences)
        total_words = len(words)
        total_syllables = sum([self._count_syllables(word) for word in words])
        
        avg_sentence_length = total_words / total_sentences
        avg_syllables_per_word = total_syllables / total_words
        
        # Flesch Reading Ease Score
        flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        flesch_score = max(0, min(100, flesch_score))  # Clamp to 0-100
        
        # Flesch-Kincaid Grade Level
        flesch_kincaid_grade = (0.39 * avg_sentence_length) + (11.8 * avg_syllables_per_word) - 15.59
        flesch_kincaid_grade = max(0, flesch_kincaid_grade)
        
        # Determine readability level
        readability_level = self._determine_readability_level(flesch_score)
        
        # Complex words percentage (3+ syllables)
        complex_words = [word for word in words if self._count_syllables(word) >= 3]
        complex_words_percentage = (len(complex_words) / total_words) * 100
        
        # Passive voice percentage (simplified detection)
        passive_voice_percentage = self._calculate_passive_voice_percentage(content)
        
        # Generate suggestions
        suggestions = self._generate_readability_suggestions(
            flesch_score, avg_sentence_length, complex_words_percentage, passive_voice_percentage
        )
        
        return ReadabilityMetrics(
            flesch_score=round(flesch_score, 1),
            flesch_kincaid_grade=round(flesch_kincaid_grade, 1),
            readability_level=readability_level,
            avg_sentence_length=round(avg_sentence_length, 1),
            avg_syllables_per_word=round(avg_syllables_per_word, 2),
            complex_words_percentage=round(complex_words_percentage, 1),
            passive_voice_percentage=round(passive_voice_percentage, 1),
            suggestions=suggestions
        )
    
    async def _optimize_keywords(
        self, 
        content: str, 
        primary_keyword: str, 
        target_keywords: List[str]
    ) -> KeywordOptimization:
        """Optimize keyword usage and placement in content."""
        if not primary_keyword:
            primary_keyword = target_keywords[0] if target_keywords else ""
        
        if not primary_keyword:
            return KeywordOptimization(
                target_keyword="",
                current_density=0.0,
                recommended_density=0.0,
                keyword_frequency=0,
                keyword_variations=[],
                placement_analysis={},
                semantic_keywords=[],
                lsi_keywords=[],
                optimization_score=0.0
            )
        
        content_lower = content.lower()
        words = content.split()
        total_words = len(words)
        
        # Calculate current keyword density
        keyword_frequency = content_lower.count(primary_keyword.lower())
        current_density = (keyword_frequency / total_words) * 100 if total_words > 0 else 0
        
        # Recommended density (1-3% for primary keyword)
        recommended_density = 2.0
        
        # Generate keyword variations
        keyword_variations = self._generate_keyword_variations(primary_keyword)
        
        # Analyze keyword placement
        placement_analysis = {
            "in_first_paragraph": primary_keyword.lower() in content_lower[:200],
            "in_last_paragraph": primary_keyword.lower() in content_lower[-200:],
            "in_headings": self._check_keyword_in_headings(content, primary_keyword),
            "proper_distribution": self._check_keyword_distribution(content, primary_keyword)
        }
        
        # Generate semantic and LSI keywords
        semantic_keywords = self._generate_semantic_keywords(primary_keyword)
        lsi_keywords = self._generate_lsi_keywords(primary_keyword, content)
        
        # Calculate optimization score
        optimization_score = self._calculate_keyword_optimization_score(
            current_density, recommended_density, placement_analysis, keyword_variations
        )
        
        # Generate recommendations
        recommendations = self._generate_keyword_recommendations(
            current_density, recommended_density, placement_analysis, optimization_score
        )
        
        return KeywordOptimization(
            target_keyword=primary_keyword,
            current_density=round(current_density, 2),
            recommended_density=recommended_density,
            keyword_frequency=keyword_frequency,
            keyword_variations=keyword_variations,
            placement_analysis=placement_analysis,
            semantic_keywords=semantic_keywords,
            lsi_keywords=lsi_keywords,
            optimization_score=round(optimization_score, 1),
            recommendations=recommendations
        )
    
    async def _analyze_structure(self, content: str, title: str = "") -> ContentStructureAnalysis:
        """Analyze content structure and organization."""
        
        # Detect structure type
        structure_type = self._detect_structure_type(content)
        
        # Analyze heading hierarchy
        heading_hierarchy = self._analyze_heading_hierarchy(content)
        
        # Count elements
        paragraphs = content.split('\n\n')
        paragraph_count = len([p for p in paragraphs if p.strip()])
        
        # Average paragraph length
        paragraph_lengths = [len(p.split()) for p in paragraphs if p.strip()]
        avg_paragraph_length = sum(paragraph_lengths) / len(paragraph_lengths) if paragraph_lengths else 0
        
        # Count links and media
        internal_links = len(re.findall(r'\[.*?\]\((?!http)', content))  # Simplified internal link detection
        external_links = len(re.findall(r'\[.*?\]\(http', content))  # Simplified external link detection
        image_count = len(re.findall(r'!\[.*?\]', content))  # Markdown image syntax
        video_count = content.lower().count('video') + content.lower().count('youtube')  # Simplified
        
        # Word count
        word_count = len(content.split())
        
        # Calculate structure score
        structure_score = self._calculate_structure_score(
            heading_hierarchy, paragraph_count, avg_paragraph_length, 
            internal_links, external_links, word_count
        )
        
        # Generate improvements
        improvements = self._generate_structure_improvements(
            structure_type, heading_hierarchy, paragraph_count, 
            avg_paragraph_length, internal_links, word_count
        )
        
        return ContentStructureAnalysis(
            structure_type=structure_type,
            heading_hierarchy=heading_hierarchy,
            paragraph_count=paragraph_count,
            avg_paragraph_length=round(avg_paragraph_length, 1),
            internal_links=internal_links,
            external_links=external_links,
            image_count=image_count,
            video_count=video_count,
            word_count=word_count,
            structure_score=round(structure_score, 1),
            improvements=improvements
        )
    
    async def _calculate_content_score(
        self,
        content: str,
        readability: ReadabilityMetrics,
        keyword_opt: KeywordOptimization,
        structure: ContentStructureAnalysis
    ) -> ContentScore:
        """Calculate comprehensive content quality scores."""
        
        # Readability score (0-100)
        readability_score = min(readability.flesch_score, 100)
        
        # SEO score based on keyword optimization
        seo_score = keyword_opt.optimization_score
        
        # Structure score
        structure_score = structure.structure_score
        
        # Engagement score (based on structure and readability)
        engagement_score = (readability_score + structure_score) / 2
        
        # Uniqueness score (simplified - would use actual plagiarism detection)
        uniqueness_score = 85.0  # Assume good uniqueness
        
        # Overall score (weighted average)
        overall_score = (
            seo_score * 0.3 +
            readability_score * 0.25 +
            structure_score * 0.25 +
            engagement_score * 0.1 +
            uniqueness_score * 0.1
        )
        
        # Determine quality level
        quality_level = self._determine_quality_level(overall_score)
        
        # Identify strengths and weaknesses
        strengths, weaknesses = self._identify_strengths_weaknesses(
            readability, keyword_opt, structure, overall_score
        )
        
        return ContentScore(
            overall_score=round(overall_score, 1),
            seo_score=round(seo_score, 1),
            readability_score=round(readability_score, 1),
            structure_score=round(structure_score, 1),
            engagement_score=round(engagement_score, 1),
            uniqueness_score=round(uniqueness_score, 1),
            quality_level=quality_level,
            strengths=strengths,
            weaknesses=weaknesses
        )
    
    async def _generate_optimized_content(
        self,
        original_content: str,
        keyword_opt: KeywordOptimization,
        structure: ContentStructureAnalysis,
        target_audience: str
    ) -> str:
        """Generate optimized version of the content."""
        optimized_content = original_content
        
        # Optimize keyword density if needed
        if keyword_opt.current_density < keyword_opt.recommended_density:
            optimized_content = self._enhance_keyword_usage(
                optimized_content, keyword_opt.target_keyword, keyword_opt.semantic_keywords
            )
        
        # Improve readability if needed
        optimized_content = self._improve_readability(optimized_content, target_audience)
        
        # Enhance structure if needed
        optimized_content = self._improve_structure(optimized_content, structure)
        
        return optimized_content
    
    async def _create_platform_adaptations(
        self,
        content: str,
        target_platforms: List[str],
        target_keywords: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """Create platform-specific content adaptations."""
        adaptations = {}
        
        for platform in target_platforms:
            if platform in self.platform_optimizers:
                adaptation = await self.platform_optimizers[platform](content, target_keywords)
                adaptations[platform] = adaptation
        
        return adaptations
    
    async def _generate_metadata_suggestions(
        self,
        content: str,
        target_keywords: List[str],
        content_type: str
    ) -> Dict[str, str]:
        """Generate optimized metadata suggestions."""
        primary_keyword = target_keywords[0] if target_keywords else ""
        
        # Generate title suggestions
        title_suggestions = self._generate_title_suggestions(content, primary_keyword, content_type)
        
        # Generate meta description
        meta_description = self._generate_meta_description(content, primary_keyword)
        
        # Generate tags
        tags = self._generate_content_tags(content, target_keywords)
        
        return {
            "title_suggestions": title_suggestions,
            "meta_description": meta_description,
            "tags": tags,
            "canonical_url": "",  # Would be generated based on content
            "schema_markup": self._generate_schema_markup(content, content_type)
        }
    
    async def _generate_optimization_recommendations(
        self,
        content_score: ContentScore,
        readability: ReadabilityMetrics,
        keyword_opt: KeywordOptimization,
        structure: ContentStructureAnalysis
    ) -> List[Dict[str, Any]]:
        """Generate actionable optimization recommendations."""
        recommendations = []
        
        # Keyword optimization recommendations
        if keyword_opt.optimization_score < 70:
            recommendations.extend([
                {
                    "type": "keyword_optimization",
                    "priority": "high",
                    "action": f"Improve keyword density for '{keyword_opt.target_keyword}' (current: {keyword_opt.current_density}%, recommended: {keyword_opt.recommended_density}%)",
                    "impact_score": 85,
                    "effort": "medium"
                }
            ])
        
        # Readability recommendations
        if readability.flesch_score < 60:
            recommendations.append({
                "type": "readability",
                "priority": "high",
                "action": "Improve readability by shortening sentences and using simpler words",
                "impact_score": 75,
                "effort": "medium"
            })
        
        # Structure recommendations
        if structure.structure_score < 70:
            recommendations.append({
                "type": "structure",
                "priority": "medium",
                "action": "Improve content structure with better headings and paragraph organization",
                "impact_score": 70,
                "effort": "medium"
            })
        
        # Add specific recommendations from keyword optimization
        for rec in keyword_opt.recommendations:
            recommendations.append({
                "type": "keyword_specific",
                "priority": "medium",
                "action": rec,
                "impact_score": 65,
                "effort": "low"
            })
        
        return recommendations
    
    # Helper methods
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified algorithm)."""
        word = word.lower()
        vowels = "aeiouy"
        syllable_count = 0
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel
        
        # Handle silent 'e'
        if word.endswith('e'):
            syllable_count -= 1
        
        # Every word has at least one syllable
        return max(1, syllable_count)
    
    def _determine_readability_level(self, flesch_score: float) -> ReadabilityLevel:
        """Determine readability level from Flesch score."""
        if flesch_score >= 90:
            return ReadabilityLevel.VERY_EASY
        elif flesch_score >= 80:
            return ReadabilityLevel.EASY
        elif flesch_score >= 70:
            return ReadabilityLevel.FAIRLY_EASY
        elif flesch_score >= 60:
            return ReadabilityLevel.STANDARD
        elif flesch_score >= 50:
            return ReadabilityLevel.FAIRLY_DIFFICULT
        elif flesch_score >= 30:
            return ReadabilityLevel.DIFFICULT
        else:
            return ReadabilityLevel.VERY_DIFFICULT
    
    def _calculate_passive_voice_percentage(self, content: str) -> float:
        """Calculate percentage of passive voice usage (simplified)."""
        # Simplified passive voice detection
        passive_indicators = ["was", "were", "been", "being", "is", "are", "am"]
        words = content.lower().split()
        passive_count = sum(1 for word in words if word in passive_indicators)
        return (passive_count / len(words)) * 100 if words else 0
    
    def _generate_readability_suggestions(
        self,
        flesch_score: float,
        avg_sentence_length: float,
        complex_words_percentage: float,
        passive_voice_percentage: float
    ) -> List[str]:
        """Generate readability improvement suggestions."""
        suggestions = []
        
        if flesch_score < 60:
            suggestions.append("Consider simplifying language and using shorter sentences")
        
        if avg_sentence_length > 20:
            suggestions.append("Break down long sentences into shorter ones")
        
        if complex_words_percentage > 20:
            suggestions.append("Replace complex words with simpler alternatives where possible")
        
        if passive_voice_percentage > 20:
            suggestions.append("Use more active voice to improve clarity and engagement")
        
        return suggestions
    
    def _generate_keyword_variations(self, keyword: str) -> List[str]:
        """Generate keyword variations."""
        variations = [keyword]
        
        # Add plural/singular variations
        if keyword.endswith('s'):
            variations.append(keyword[:-1])
        else:
            variations.append(keyword + 's')
        
        # Add related forms (simplified)
        words = keyword.split()
        if len(words) > 1:
            variations.extend(words)  # Individual words
            variations.append(' '.join(reversed(words)))  # Reversed order
        
        return list(set(variations))
    
    def _check_keyword_in_headings(self, content: str, keyword: str) -> bool:
        """Check if keyword appears in headings."""
        headings = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
        return any(keyword.lower() in heading.lower() for heading in headings)
    
    def _check_keyword_distribution(self, content: str, keyword: str) -> bool:
        """Check if keyword is properly distributed throughout content."""
        sentences = self._split_sentences(content)
        if len(sentences) < 3:
            return True
        
        # Check if keyword appears in first third, middle third, and last third
        third_size = len(sentences) // 3
        first_third = ' '.join(sentences[:third_size])
        middle_third = ' '.join(sentences[third_size:2*third_size])
        last_third = ' '.join(sentences[2*third_size:])
        
        first_has_keyword = keyword.lower() in first_third.lower()
        middle_has_keyword = keyword.lower() in middle_third.lower()
        last_has_keyword = keyword.lower() in last_third.lower()
        
        return sum([first_has_keyword, middle_has_keyword, last_has_keyword]) >= 2
    
    def _generate_semantic_keywords(self, keyword: str) -> List[str]:
        """Generate semantic keywords (simplified)."""
        # In real implementation, would use actual semantic analysis
        semantic_map = {
            "content marketing": ["digital marketing", "brand awareness", "audience engagement"],
            "video editing": ["video production", "post-production", "video effects"],
            "social media": ["digital presence", "online marketing", "social networking"]
        }
        
        return semantic_map.get(keyword.lower(), [])
    
    def _generate_lsi_keywords(self, keyword: str, content: str) -> List[str]:
        """Generate LSI (Latent Semantic Indexing) keywords."""
        # Simplified LSI keyword generation
        words = content.lower().split()
        word_freq = Counter(words)
        
        # Return most common words that aren't stop words
        stop_words = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'])
        lsi_keywords = [word for word, freq in word_freq.most_common(10) 
                       if word not in stop_words and len(word) > 3]
        
        return lsi_keywords[:5]
    
    def _calculate_keyword_optimization_score(
        self,
        current_density: float,
        recommended_density: float,
        placement_analysis: Dict[str, bool],
        variations: List[str]
    ) -> float:
        """Calculate keyword optimization score."""
        # Density score (0-40 points)
        density_diff = abs(current_density - recommended_density)
        density_score = max(0, 40 - (density_diff * 10))
        
        # Placement score (0-40 points)
        placement_score = sum(placement_analysis.values()) * 10
        
        # Variation score (0-20 points)
        variation_score = min(len(variations) * 4, 20)
        
        return density_score + placement_score + variation_score
    
    def _generate_keyword_recommendations(
        self,
        current_density: float,
        recommended_density: float,
        placement_analysis: Dict[str, bool],
        optimization_score: float
    ) -> List[str]:
        """Generate keyword optimization recommendations."""
        recommendations = []
        
        if current_density < recommended_density:
            recommendations.append(f"Increase keyword density from {current_density}% to {recommended_density}%")
        elif current_density > recommended_density * 1.5:
            recommendations.append(f"Reduce keyword density from {current_density}% to avoid over-optimization")
        
        if not placement_analysis.get("in_first_paragraph", False):
            recommendations.append("Include target keyword in the first paragraph")
        
        if not placement_analysis.get("in_headings", False):
            recommendations.append("Include target keyword in at least one heading")
        
        if not placement_analysis.get("proper_distribution", False):
            recommendations.append("Distribute keyword more evenly throughout the content")
        
        return recommendations
    
    def _detect_structure_type(self, content: str) -> ContentStructure:
        """Detect content structure type."""
        content_lower = content.lower()
        
        if "how to" in content_lower or "step" in content_lower:
            return ContentStructure.TUTORIAL
        elif content_lower.count('\n') > 10 and any(marker in content_lower for marker in ['1.', '2.', '3.', '-', '*']):
            return ContentStructure.LISTICLE
        elif "review" in content_lower or "rating" in content_lower:
            return ContentStructure.REVIEW
        elif "vs" in content_lower or "comparison" in content_lower:
            return ContentStructure.COMPARISON
        else:
            return ContentStructure.ARTICLE
    
    def _analyze_heading_hierarchy(self, content: str) -> List[Dict[str, Any]]:
        """Analyze heading hierarchy and structure."""
        headings = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                text = line.lstrip('#').strip()
                headings.append({
                    "level": level,
                    "text": text,
                    "word_count": len(text.split())
                })
        
        return headings
    
    def _calculate_structure_score(
        self,
        headings: List[Dict[str, Any]],
        paragraph_count: int,
        avg_paragraph_length: float,
        internal_links: int,
        external_links: int,
        word_count: int
    ) -> float:
        """Calculate content structure score."""
        score = 0
        
        # Heading score (0-30 points)
        if headings:
            score += 20
            if len(headings) >= 3:
                score += 10
        
        # Paragraph score (0-25 points)
        if 50 <= avg_paragraph_length <= 150:
            score += 25
        elif avg_paragraph_length < 200:
            score += 15
        
        # Link score (0-25 points)
        total_links = internal_links + external_links
        if total_links > 0:
            score += min(total_links * 5, 25)
        
        # Word count score (0-20 points)
        if 300 <= word_count <= 2000:
            score += 20
        elif word_count > 200:
            score += 10
        
        return min(score, 100)
    
    def _generate_structure_improvements(
        self,
        structure_type: ContentStructure,
        headings: List[Dict[str, Any]],
        paragraph_count: int,
        avg_paragraph_length: float,
        internal_links: int,
        word_count: int
    ) -> List[str]:
        """Generate structure improvement suggestions."""
        improvements = []
        
        if not headings:
            improvements.append("Add headings to improve content structure and readability")
        elif len(headings) < 3 and word_count > 500:
            improvements.append("Add more headings to break up long content sections")
        
        if avg_paragraph_length > 200:
            improvements.append("Break up long paragraphs into shorter ones for better readability")
        
        if internal_links == 0 and word_count > 500:
            improvements.append("Add internal links to improve site navigation and SEO")
        
        if word_count < 300:
            improvements.append("Consider expanding content length for better SEO performance")
        
        return improvements
    
    def _determine_quality_level(self, overall_score: float) -> ContentQuality:
        """Determine content quality level from overall score."""
        if overall_score >= 90:
            return ContentQuality.EXCELLENT
        elif overall_score >= 80:
            return ContentQuality.GOOD
        elif overall_score >= 70:
            return ContentQuality.AVERAGE
        elif overall_score >= 60:
            return ContentQuality.BELOW_AVERAGE
        else:
            return ContentQuality.POOR
    
    def _identify_strengths_weaknesses(
        self,
        readability: ReadabilityMetrics,
        keyword_opt: KeywordOptimization,
        structure: ContentStructureAnalysis,
        overall_score: float
    ) -> Tuple[List[str], List[str]]:
        """Identify content strengths and weaknesses."""
        strengths = []
        weaknesses = []
        
        # Readability strengths/weaknesses
        if readability.flesch_score >= 70:
            strengths.append("Good readability score")
        else:
            weaknesses.append("Poor readability - content may be difficult to read")
        
        # Keyword optimization strengths/weaknesses
        if keyword_opt.optimization_score >= 70:
            strengths.append("Good keyword optimization")
        else:
            weaknesses.append("Keyword optimization needs improvement")
        
        # Structure strengths/weaknesses
        if structure.structure_score >= 70:
            strengths.append("Well-structured content")
        else:
            weaknesses.append("Content structure needs improvement")
        
        # Word count
        if 500 <= structure.word_count <= 2000:
            strengths.append("Appropriate content length")
        elif structure.word_count < 300:
            weaknesses.append("Content may be too short for good SEO performance")
        elif structure.word_count > 3000:
            weaknesses.append("Content may be too long for optimal engagement")
        
        return strengths, weaknesses
    
    def _enhance_keyword_usage(self, content: str, keyword: str, semantic_keywords: List[str]) -> str:
        """Enhance keyword usage in content."""
        # Simple keyword enhancement (in real implementation, would be more sophisticated)
        enhanced_content = content
        
        # Add keyword to first paragraph if not present
        paragraphs = content.split('\n\n')
        if paragraphs and keyword.lower() not in paragraphs[0].lower():
            paragraphs[0] = f"{keyword} is an important topic. {paragraphs[0]}"
            enhanced_content = '\n\n'.join(paragraphs)
        
        return enhanced_content
    
    def _improve_readability(self, content: str, target_audience: str) -> str:
        """Improve content readability."""
        # Simple readability improvements
        improved_content = content
        
        # Break up long sentences (simplified)
        sentences = self._split_sentences(content)
        improved_sentences = []
        
        for sentence in sentences:
            if len(sentence.split()) > 25:  # Long sentence
                # Try to split at conjunctions
                for conjunction in [', and ', ', but ', ', or ', ', so ']:
                    if conjunction in sentence:
                        parts = sentence.split(conjunction, 1)
                        improved_sentences.extend(parts)
                        break
                else:
                    improved_sentences.append(sentence)
            else:
                improved_sentences.append(sentence)
        
        improved_content = '. '.join(improved_sentences)
        return improved_content
    
    def _improve_structure(self, content: str, structure: ContentStructureAnalysis) -> str:
        """Improve content structure."""
        # Simple structure improvements
        if structure.paragraph_count < 3 and structure.word_count > 300:
            # Add paragraph breaks
            sentences = self._split_sentences(content)
            if len(sentences) > 6:
                # Break into paragraphs every 2-3 sentences
                paragraphs = []
                current_paragraph = []
                
                for i, sentence in enumerate(sentences):
                    current_paragraph.append(sentence)
                    if (i + 1) % 3 == 0 or i == len(sentences) - 1:
                        paragraphs.append('. '.join(current_paragraph) + '.')
                        current_paragraph = []
                
                return '\n\n'.join(paragraphs)
        
        return content
    
    def _calculate_readability_improvement(self, readability: ReadabilityMetrics) -> float:
        """Calculate readability improvement percentage."""
        # Simplified calculation
        if readability.flesch_score >= 70:
            return 0  # Already good
        else:
            potential_improvement = (70 - readability.flesch_score) / 70 * 100
            return min(potential_improvement, 50)  # Cap at 50% improvement
    
    # Platform-specific optimization methods
    
    async def _optimize_for_google(self, content: str, keywords: List[str]) -> Dict[str, Any]:
        """Optimize content for Google search."""
        return {
            "platform": "google",
            "recommendations": [
                "Include target keyword in title and meta description",
                "Use header tags (H1, H2, H3) with keywords",
                "Optimize for featured snippets with Q&A format",
                "Include internal and external links"
            ],
            "title_format": "Primary Keyword | Secondary Keyword | Brand",
            "meta_description_length": "150-160 characters",
            "optimal_length": "1500-2500 words"
        }
    
    async def _optimize_for_youtube(self, content: str, keywords: List[str]) -> Dict[str, Any]:
        """Optimize content for YouTube."""
        return {
            "platform": "youtube",
            "recommendations": [
                "Include keywords in video title and description",
                "Use keywords as tags",
                "Create engaging thumbnails with text",
                "Add timestamps for longer videos"
            ],
            "title_format": "Keyword | How to | Benefit",
            "description_structure": "Hook + Keywords + Call to Action",
            "optimal_length": "10-15 minutes for most topics"
        }
    
    async def _optimize_for_instagram(self, content: str, keywords: List[str]) -> Dict[str, Any]:
        """Optimize content for Instagram."""
        return {
            "platform": "instagram",
            "recommendations": [
                "Use keywords as hashtags",
                "Include keywords in captions",
                "Optimize for visual storytelling",
                "Use location tags when relevant"
            ],
            "hashtag_strategy": "Mix of popular and niche hashtags",
            "caption_length": "125-150 characters for optimal engagement",
            "posting_frequency": "1-2 times per day"
        }
    
    async def _optimize_for_tiktok(self, content: str, keywords: List[str]) -> Dict[str, Any]:
        """Optimize content for TikTok."""
        return {
            "platform": "tiktok",
            "recommendations": [
                "Use trending sounds and hashtags",
                "Create engaging hooks in first 3 seconds",
                "Include keywords in captions",
                "Participate in trending challenges"
            ],
            "optimal_length": "15-30 seconds",
            "hashtag_limit": "3-5 hashtags maximum",
            "posting_time": "Peak hours: 6-10pm"
        }
    
    async def _optimize_for_linkedin(self, content: str, keywords: List[str]) -> Dict[str, Any]:
        """Optimize content for LinkedIn."""
        return {
            "platform": "linkedin",
            "recommendations": [
                "Use professional tone and industry keywords",
                "Include relevant hashtags (3-5)",
                "Tag relevant connections and companies",
                "Share valuable insights and experiences"
            ],
            "content_type": "Professional insights and industry expertise",
            "optimal_length": "1300-1700 characters",
            "posting_frequency": "1 post per day maximum"
        }
    
    def _generate_title_suggestions(self, content: str, keyword: str, content_type: str) -> List[str]:
        """Generate optimized title suggestions."""
        suggestions = []
        
        if keyword:
            suggestions.extend([
                f"The Ultimate Guide to {keyword}",
                f"How to Master {keyword} in 2025",
                f"{keyword}: Everything You Need to Know",
                f"Best {keyword} Strategies That Actually Work",
                f"The Complete {keyword} Tutorial for Beginners"
            ])
        
        return suggestions[:3]
    
    def _generate_meta_description(self, content: str, keyword: str) -> str:
        """Generate optimized meta description."""
        first_sentence = self._split_sentences(content)[0] if content else ""
        
        if keyword and first_sentence:
            return f"Learn about {keyword}. {first_sentence[:100]}... Discover expert tips and strategies."
        elif first_sentence:
            return first_sentence[:150] + "..."
        else:
            return "Discover valuable insights and expert strategies in this comprehensive guide."
    
    def _generate_content_tags(self, content: str, keywords: List[str]) -> List[str]:
        """Generate content tags."""
        tags = keywords.copy()
        
        # Add common words from content
        words = content.lower().split()
        word_freq = Counter(words)
        common_words = [word for word, freq in word_freq.most_common(10) 
                       if len(word) > 4 and word not in ['about', 'which', 'where', 'there']]
        
        tags.extend(common_words[:5])
        return list(set(tags))[:10]
    
    def _generate_schema_markup(self, content: str, content_type: str) -> str:
        """Generate basic schema markup."""
        if content_type == "article":
            return '{"@type": "Article", "@context": "https://schema.org"}'
        elif content_type == "tutorial":
            return '{"@type": "HowTo", "@context": "https://schema.org"}'
        elif content_type == "review":
            return '{"@type": "Review", "@context": "https://schema.org"}'
        else:
            return '{"@type": "WebPage", "@context": "https://schema.org"}'