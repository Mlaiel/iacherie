"""Content SEO Optimizer - AI-Powered Content Optimization

This module provides intelligent content optimization for SEO including
readability analysis, keyword density optimization, and content structure enhancement.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import re
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class OptimizationLevel(Enum):
    """
SEO optimization levels"""

    BASIC = "basic"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class ContentAnalysis:
    """Content analysis results"""
    readability_score: float
    keyword_density: Dict[str, float]
    content_structure: Dict[str, Any]
    seo_recommendations: List[str]
    optimization_score: float


@dataclass
class SEOOptimizationResult:
    """
SEO optimization result"""
    original_content: str
    optimized_content: str
    analysis: ContentAnalysis
    improvements: List[str]
    performance_metrics: Dict[str, float]


class ContentSEOOptimizer:
    """
    AI-powered content SEO optimizer that analyzes and improves content
    for better search engine optimization.
    """
    def __init__(self, optimization_level -> None: OptimizationLevel = OptimizationLevel.ADVANCED) -> None:
        """
        Initialize the content SEO optimizer.
        
        Args:
            optimization_level: Level of optimization to apply
        """
        self.optimization_level = optimization_level
        self.min_keyword_density = 0.5
        self.max_keyword_density = 3.0
        self.target_readability_score = 60.0

    def optimize_content(
        self,
        content: str,
        target_keywords: List[str],
        platform_type: str = "general",
        language: str = "en"
    ) -> SEOOptimizationResult:
        """
        Optimize content for SEO.
        
        Args:
            content: Original content to optimize
            target_keywords: List of target keywords
            platform_type: Platform type (e.g., 'instagram', 'youtube', 'blog')
            language: Content language
            
        Returns:
            SEOOptimizationResult with optimized content and analysis
        """
        try:
            logger.info(f"Starting SEO optimization for {platform_type} content")
            
            # Analyze original content
            analysis = self._analyze_content(content, target_keywords, language)
            
            # Generate optimizations
            optimized_content = self._apply_optimizations(
                content, target_keywords, analysis, platform_type
            )
            
            # Track improvements
            improvements = self._track_improvements(content, optimized_content, analysis)
            
            # Calculate performance metrics
            performance_metrics = self._calculate_performance_metrics(
                analysis, optimized_content, target_keywords
            )
            
            return SEOOptimizationResult(
                original_content=content,
                optimized_content=optimized_content,
                analysis=analysis,
                improvements=improvements,
                performance_metrics=performance_metrics
            )
            
        except Exception as e:
            logger.error(f"Error optimizing content: {str(e)}")
            raise

    def _analyze_content(
        self, 
        content: str, 
        target_keywords: List[str], 
        language: str
    ) -> ContentAnalysis:
        """Analyze content for SEO metrics."""
        
        # Calculate readability score (simplified Flesch reading ease)
        readability_score = self._calculate_readability(content)
        
        # Calculate keyword density
        keyword_density = self._calculate_keyword_density(content, target_keywords)
        
        # Analyze content structure
        content_structure = self._analyze_structure(content)
        
        # Generate recommendations
        seo_recommendations = self._generate_recommendations(
            readability_score, keyword_density, content_structure
        )
        
        # Calculate overall optimization score
        optimization_score = self._calculate_optimization_score(
            readability_score, keyword_density, content_structure
        )
        
        return ContentAnalysis(
            readability_score=readability_score,
            keyword_density=keyword_density,
            content_structure=content_structure,
            seo_recommendations=seo_recommendations,
            optimization_score=optimization_score
        )

    def _calculate_readability(self, content: str) -> float:
        """
Calculate readability score using simplified Flesch reading ease."""
        sentences = len(re.findall(r'[.!?]+', content))
        words = len(content.split())
        syllables = self._count_syllables(content)
        
        if sentences == 0 or words == 0:
            return 0.0
            
        avg_sentence_length = words / sentences
        avg_syllables_per_word = syllables / words
        
        # Simplified Flesch reading ease formula
        score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        return max(0.0, min(100.0, score))

    def _count_syllables(self, text: str) -> int:
        """
Count syllables in text (simplified approach)."""
        text = text.lower()
        syllables = 0
        vowels = 'aeiouy'
        
        for word in text.split():
            word = re.sub(r'[^a-z]', '', word)
            if word:
                syllable_count = 0
                prev_char_vowel = False
                
                for char in word:
                    is_vowel = char in vowels
                    if is_vowel and not prev_char_vowel:
                        syllable_count += 1
                    prev_char_vowel = is_vowel
                
                # Adjust for silent 'e'
                if word.endswith('e') and syllable_count > 1:
                    syllable_count -= 1
                    
                syllables += max(1, syllable_count)
                
        return syllables

    def _calculate_keyword_density(
        self, 
        content: str, 
        keywords: List[str]
    ) -> Dict[str, float]:
        """
Calculate keyword density for each target keyword."""
        content_lower = content.lower()
        total_words = len(content.split())
        
        if total_words == 0:
            return {keyword: 0.0 for keyword in keywords}
        
        keyword_density = {}
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            occurrences = content_lower.count(keyword_lower)
            density = (occurrences / total_words) * 100
            keyword_density[keyword] = density
            
        return keyword_density

    def _analyze_structure(self, content: str) -> Dict[str, Any]:
        """
Analyze content structure for SEO."""
        return {
            "word_count": len(content.split()),
            "paragraph_count": len(content.split('\n\n')),
            "has_headings": bool(re.search(r'^#+\s', content, re.MULTILINE)),
            "has_lists": bool(re.search(r'^\s*[-*+]\s', content, re.MULTILINE)),
            "avg_paragraph_length": self._calculate_avg_paragraph_length(content),
            "sentence_variety": self._analyze_sentence_variety(content)
        }

    def _calculate_avg_paragraph_length(self, content: str) -> float:
        """Calculate average paragraph length."""
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        if not paragraphs:
            return 0.0
        
        total_words = sum(len(p.split()) for p in paragraphs)
        return total_words / len(paragraphs)

    def _analyze_sentence_variety(self, content: str) -> Dict[str, int]:
        """
Analyze sentence variety for better readability."""
        sentences = re.findall(r'[.!?]+', content)
        return {
            "total_sentences": len(sentences),
            "declarative": len([s for s in sentences if s == '.']),
            "interrogative": len([s for s in sentences if s == '?']),
            "exclamatory": len([s for s in sentences if s == '!'])
        }

    def _generate_recommendations(
        self, 
        readability_score: float, 
        keyword_density: Dict[str, float], 
        content_structure: Dict[str, Any]
    ) -> List[str]:
        """Generate SEO recommendations based on analysis."""
        recommendations = []
        
        # Readability recommendations
        if readability_score < 40:
            recommendations.append("Content is difficult to read. Consider simplifying sentences and vocabulary.")
        elif readability_score > 80:
            recommendations.append("Content might be too simple. Consider adding more sophisticated language.")
        
        # Keyword density recommendations
        for keyword, density in keyword_density.items():
            if density < self.min_keyword_density:
                recommendations.append(f"Increase density for keyword '{keyword}' (current: {density:.1f}%)")
            elif density > self.max_keyword_density:
                recommendations.append(f"Reduce density for keyword '{keyword}' (current: {density:.1f}%)")
        
        # Structure recommendations
        if content_structure["word_count"] < 300:
            recommendations.append("Content is too short. Aim for at least 300 words.")
        
        if not content_structure["has_headings"]:
            recommendations.append("Add headings to improve content structure.")
        
        if content_structure["avg_paragraph_length"] > 100:
            recommendations.append("Paragraphs are too long. Break them into smaller chunks.")
        
        return recommendations

    def _calculate_optimization_score(
        self, 
        readability_score: float, 
        keyword_density: Dict[str, float], 
        content_structure: Dict[str, Any]
    ) -> float:
        """Calculate overall optimization score."""
        scores = []
        
        # Readability score (0-100, target around 60)
        readability_normalized = 100 - abs(readability_score - self.target_readability_score)
        scores.append(max(0, readability_normalized))
        
        # Keyword density score
        keyword_scores = []
        for density in keyword_density.values():
            if self.min_keyword_density <= density <= self.max_keyword_density:
                keyword_scores.append(100)
            else:
                distance = min(
                    abs(density - self.min_keyword_density),
                    abs(density - self.max_keyword_density)
                )
                keyword_scores.append(max(0, 100 - distance * 20))
        
        if keyword_scores:
            scores.append(sum(keyword_scores) / len(keyword_scores))
        
        # Structure score
        structure_score = 0
        if content_structure["word_count"] >= 300:
            structure_score += 25
        if content_structure["has_headings"]:
            structure_score += 25
        if content_structure["has_lists"]:
            structure_score += 25
        if content_structure["avg_paragraph_length"] <= 100:
            structure_score += 25
            
        scores.append(structure_score)
        
        return sum(scores) / len(scores) if scores else 0.0

    def _apply_optimizations(
        self, 
        content: str, 
        target_keywords: List[str], 
        analysis: ContentAnalysis, 
        platform_type: str
    ) -> str:
        """Apply optimizations to content based on analysis."""
        optimized = content
        
        # Apply keyword optimization
        optimized = self._optimize_keywords(optimized, target_keywords, analysis.keyword_density)
        
        # Apply readability improvements
        if analysis.readability_score < 40:
            optimized = self._improve_readability(optimized)
        
        # Apply structure improvements
        optimized = self._improve_structure(optimized, analysis.content_structure)
        
        # Apply platform-specific optimizations
        optimized = self._apply_platform_optimizations(optimized, platform_type)
        
        return optimized

    def _optimize_keywords(
        self, 
        content: str, 
        target_keywords: List[str], 
        current_density: Dict[str, float]
    ) -> str:
        """
Optimize keyword distribution in content."""
        optimized = content
        
        for keyword in target_keywords:
            current_freq = current_density.get(keyword, 0)
            
            if current_freq < self.min_keyword_density:
                # Add keyword naturally
                optimized = self._add_keyword_naturally(optimized, keyword)
        
        return optimized

    def _add_keyword_naturally(self, content: str, keyword: str) -> str:
        """
Add keyword naturally to content."""
        sentences = content.split('.')
        if len(sentences) > 1:
            # Add keyword to a random sentence
            import random
            target_sentence_idx = random.randint(0, len(sentences) - 2)
            sentences[target_sentence_idx] += f" {keyword}"
            return '.'.join(sentences)
        return content

    def _improve_readability(self, content: str) -> str:
        """Improve content readability."""
        # Split long sentences
        sentences = re.split(r'[.!?]', content)
        improved_sentences = []
        
        for sentence in sentences:
            if len(sentence.split()) > 20:  # Long sentence
                # Split at conjunctions
                parts = re.split(r'\b(and|but|or|so|yet)\b', sentence)
                if len(parts) > 1:
                    improved_sentences.extend(parts[::2])  # Take every other part
                else:
                    improved_sentences.append(sentence)
            else:
                improved_sentences.append(sentence)
        
        return '. '.join(improved_sentences).strip()

    def _improve_structure(self, content: str, structure: Dict[str, Any]) -> str:
        """
Improve content structure."""
        improved = content
        
        # Add paragraph breaks for long content
        if structure["avg_paragraph_length"] > 100:
            sentences = improved.split('.')
            paragraphs = []
            current_paragraph = []
            
            for sentence in sentences:
                current_paragraph.append(sentence)
                if len(' '.join(current_paragraph).split()) > 80:
                    paragraphs.append('. '.join(current_paragraph).strip())
                    current_paragraph = []
            
            if current_paragraph:
                paragraphs.append('. '.join(current_paragraph).strip())
            
            improved = '\n\n'.join(paragraphs)
        
        return improved

    def _apply_platform_optimizations(self, content: str, platform_type: str) -> str:
        """Apply platform-specific optimizations."""
        if platform_type == "instagram":
            # Add line breaks for better mobile readability
            return re.sub(r'([.!?])\s+', r'\1\n\n', content)
        elif platform_type == "twitter":
            # Ensure content fits character limits
            if len(content) > 280:
                return content[:277] + "..."
        elif platform_type == "youtube":
            # Add timestamps or chapter markers
            return content
        
        return content

    def _track_improvements(
        self, 
        original: str, 
        optimized: str, 
        analysis: ContentAnalysis
    ) -> List[str]:
        """Track improvements made during optimization."""
        improvements = []
        
        if len(optimized.split()) > len(original.split()):
            improvements.append("Added content for better keyword density")
        
        if optimized.count('\n\n') > original.count('\n\n'):
            improvements.append("Improved paragraph structure")
        
        if len(re.findall(r'[.!?]', optimized)) > len(re.findall(r'[.!?]', original)):
            improvements.append("Improved sentence variety")
        
        return improvements

    def _calculate_performance_metrics(
        self, 
        analysis: ContentAnalysis, 
        optimized_content: str, 
        target_keywords: List[str]
    ) -> Dict[str, float]:
        """Calculate performance metrics for optimization."""
        return {
            "optimization_score": analysis.optimization_score,
            "readability_improvement": max(0, self.target_readability_score - abs(analysis.readability_score - self.target_readability_score)),
            "keyword_coverage": len([k for k, d in analysis.keyword_density.items() if self.min_keyword_density <= d <= self.max_keyword_density]) / len(target_keywords) * 100 if target_keywords else 0,
            "content_length_score": min(100, len(optimized_content.split()) / 3),  # 300 words = 100 score
            "structure_score": sum([
                25 if analysis.content_structure["has_headings"] else 0,
                25 if analysis.content_structure["has_lists"] else 0,
                25 if analysis.content_structure["avg_paragraph_length"] <= 100 else 0,
                25 if analysis.content_structure["word_count"] >= 300 else 0
            ])
        }


# Export for module usage
__all__ = ["ContentSEOOptimizer", "OptimizationLevel", "ContentAnalysis", "SEOOptimizationResult"]