"""Quality Metrics - Advanced content quality measurement and scoring

Professional quality assessment system that evaluates content across
multiple dimensions and provides comprehensive quality scores.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

STRICT COPYRIGHT NOTICE:
This code belongs exclusively to Fahed Mlaiel. Unauthorized use prohibited.
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import re
import math
from dataclasses import dataclass
from collections import Counter
import statistics


@dataclass
class QualityScore:
    """Data class for quality scores"""    overall_score: float
    readability_score: float
    engagement_score: float
    seo_score: float
    originality_score: float
    technical_score: float
    brand_alignment_score: float
    dimension_scores: Dict[str, float]
    improvement_suggestions: List[str]
    quality_grade: str


class QualityMetrics:
    """    Advanced quality metrics system that provides:
    
    - Multi-dimensional quality assessment
    - Readability analysis (Flesch, Gunning Fog, etc.)
    - SEO quality scoring
    - Content originality detection
    - Brand voice alignment measurement
    - Technical quality evaluation
    - Engagement potential prediction
    - Competitive benchmarking
    """    
    def __init__(self):
        """Initialize quality metrics system"""        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Quality dimensions and weights
        self.quality_dimensions = {
            'readability': {
                'weight': 0.20,
                'metrics': ['flesch_score', 'sentence_length', 'word_complexity']
            },
            'engagement': {
                'weight': 0.18,
                'metrics': ['hook_strength', 'emotional_appeal', 'call_to_action']
            },
            'seo': {
                'weight': 0.15,
                'metrics': ['keyword_optimization', 'structure', 'meta_quality']
            },
            'originality': {
                'weight': 0.15,
                'metrics': ['uniqueness', 'creativity', 'freshness']
            },
            'technical': {
                'weight': 0.12,
                'metrics': ['grammar', 'spelling', 'formatting']
            },
            'brand_alignment': {
                'weight': 0.10,
                'metrics': ['tone_consistency', 'voice_match', 'value_alignment']
            },
            'completeness': {
                'weight': 0.10,
                'metrics': ['information_depth', 'coverage', 'actionability']
            }
        }
        
        # Grade boundaries
        self.grade_boundaries = {
            'A+': 0.95,
            'A': 0.90,
            'A-': 0.85,
            'B+': 0.80,
            'B': 0.75,
            'B-': 0.70,
            'C+': 0.65,
            'C': 0.60,
            'C-': 0.55,
            'D': 0.50,
            'F': 0.0
        }
        
        # Common readability formulas
        self.readability_formulas = {
            'flesch_reading_ease': self._flesch_reading_ease,
            'flesch_kincaid_grade': self._flesch_kincaid_grade,
            'gunning_fog': self._gunning_fog_index,
            'smog': self._smog_index,
            'coleman_liau': self._coleman_liau_index
        }
        
        # Engagement indicators
        self.engagement_patterns = {
            'questions': r'\?',
            'exclamations': r'!',
            'action_words': r'\b(discover|learn|get|find|start|create|build|achieve|transform|improve)\b',
            'emotional_words': r'\b(amazing|incredible|awesome|fantastic|exciting|inspiring|powerful)\b',
            'urgency_words': r'\b(now|today|urgent|limited|exclusive|immediate|instant)\b',
            'power_words': r'\b(secret|proven|guaranteed|ultimate|essential|breakthrough)\b'
        }
        
        # SEO quality factors
        self.seo_factors = {
            'title_length': (30, 60),  # Optimal character range
            'description_length': (120, 160),
            'heading_structure': True,
            'keyword_density': (0.01, 0.03),  # 1-3%
            'internal_links': True,
            'image_alt_text': True
        }
        
        # Brand voice patterns (customizable)
        self.brand_voice_patterns = {
            'professional': {
                'tone_words': ['professional', 'expert', 'industry', 'strategic', 'solution'],
                'avoid_words': ['awesome', 'cool', 'super', 'crazy', 'insane'],
                'sentence_style': 'formal'
            },
            'casual': {
                'tone_words': ['easy', 'simple', 'fun', 'cool', 'awesome'],
                'avoid_words': ['paradigm', 'synergy', 'leverage', 'utilize'],
                'sentence_style': 'conversational'
            },
            'authoritative': {
                'tone_words': ['proven', 'research', 'data', 'study', 'analysis'],
                'avoid_words': ['maybe', 'possibly', 'might', 'could'],
                'sentence_style': 'declarative'
            }
        }
    
    async def analyze_content_quality(
        self,
        content: str,
        content_type: str,
        target_audience: Optional[str] = None,
        brand_voice: Optional[str] = None,
        seo_keywords: Optional[List[str]] = None
    ) -> QualityScore:
        """        Comprehensive content quality analysis.
        
        Args:
            content: Content to analyze
            content_type: Type of content (blog, social, email, etc.)
            target_audience: Target audience for content
            brand_voice: Brand voice style (professional, casual, etc.)
            seo_keywords: Target SEO keywords
            
        Returns:
            Comprehensive quality score with detailed breakdown
        """        try:
            # Initialize scores dictionary
            dimension_scores = {}
            improvement_suggestions = []
            
            # Analyze each quality dimension
            dimension_scores['readability'] = await self._analyze_readability(content, target_audience)
            dimension_scores['engagement'] = await self._analyze_engagement_potential(content, content_type)
            dimension_scores['seo'] = await self._analyze_seo_quality(content, seo_keywords)
            dimension_scores['originality'] = await self._analyze_originality(content)
            dimension_scores['technical'] = await self._analyze_technical_quality(content)
            dimension_scores['brand_alignment'] = await self._analyze_brand_alignment(content, brand_voice)
            dimension_scores['completeness'] = await self._analyze_completeness(content, content_type)
            
            # Calculate weighted overall score
            overall_score = sum(
                dimension_scores[dimension] * self.quality_dimensions[dimension]['weight']
                for dimension in dimension_scores
            )
            
            # Get improvement suggestions
            improvement_suggestions = await self._generate_improvement_suggestions(
                dimension_scores, content, content_type
            )
            
            # Determine quality grade
            quality_grade = self._get_quality_grade(overall_score)
            
            # Create quality score object
            quality_score = QualityScore(
                overall_score=overall_score,
                readability_score=dimension_scores['readability'],
                engagement_score=dimension_scores['engagement'],
                seo_score=dimension_scores['seo'],
                originality_score=dimension_scores['originality'],
                technical_score=dimension_scores['technical'],
                brand_alignment_score=dimension_scores['brand_alignment'],
                dimension_scores=dimension_scores,
                improvement_suggestions=improvement_suggestions,
                quality_grade=quality_grade
            )
            
            self.logger.info(f"Content quality analyzed: {quality_grade} ({overall_score:.2f})")
            
            return quality_score
            
        except Exception as e:
            self.logger.error(f"Quality analysis failed: {str(e)}")
            return QualityScore(
                overall_score=0.5,
                readability_score=0.5,
                engagement_score=0.5,
                seo_score=0.5,
                originality_score=0.5,
                technical_score=0.5,
                brand_alignment_score=0.5,
                dimension_scores={},
                improvement_suggestions=["Unable to analyze content quality"],
                quality_grade="C"
            )
    
    async def _analyze_readability(self, content: str, target_audience: Optional[str]) -> float:
        """Analyze content readability"""        try:
            # Calculate multiple readability scores
            flesch_score = self._flesch_reading_ease(content)
            flesch_grade = self._flesch_kincaid_grade(content)
            fog_index = self._gunning_fog_index(content)
            
            # Normalize scores to 0-1 range
            flesch_normalized = max(0, min(1, flesch_score / 100))
            grade_normalized = max(0, min(1, (20 - flesch_grade) / 15))  # Invert grade scale
            fog_normalized = max(0, min(1, (20 - fog_index) / 15))
            
            # Calculate sentence and word statistics
            sentences = self._split_sentences(content)
            words = content.split()
            
            avg_sentence_length = len(words) / len(sentences) if sentences else 0
            avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
            
            # Score sentence length (ideal: 15-20 words)
            sentence_score = 1.0 if 15 <= avg_sentence_length <= 20 else max(0, 1 - abs(avg_sentence_length - 17.5) / 20)
            
            # Score word complexity (ideal: 4-6 characters)
            word_score = 1.0 if 4 <= avg_word_length <= 6 else max(0, 1 - abs(avg_word_length - 5) / 5)
            
            # Adjust for target audience
            audience_adjustment = 1.0
            if target_audience:
                if target_audience.lower() in ['children', 'young', 'beginner']:
                    # Prefer simpler content
                    audience_adjustment = flesch_normalized
                elif target_audience.lower() in ['expert', 'professional', 'academic']:
                    # Allow more complex content
                    audience_adjustment = min(1.0, grade_normalized + 0.2)
            
            # Combine scores
            readability_score = (
                flesch_normalized * 0.3 +
                grade_normalized * 0.3 +
                fog_normalized * 0.2 +
                sentence_score * 0.1 +
                word_score * 0.1
            ) * audience_adjustment
            
            return min(1.0, max(0.0, readability_score))
            
        except Exception as e:
            self.logger.warning(f"Readability analysis failed: {str(e)}")
            return 0.5
    
    async def _analyze_engagement_potential(self, content: str, content_type: str) -> float:
        """Analyze content engagement potential"""        try:
            engagement_score = 0.0
            content_lower = content.lower()
            
            # Analyze engagement patterns
            for pattern_name, pattern in self.engagement_patterns.items():
                matches = len(re.findall(pattern, content_lower))
                word_count = len(content.split())
                
                # Calculate pattern density
                density = matches / word_count if word_count > 0 else 0
                
                # Score based on pattern type
                if pattern_name == 'questions':
                    engagement_score += min(0.15, density * 10)  # Up to 15% for questions
                elif pattern_name == 'exclamations':
                    engagement_score += min(0.10, density * 8)   # Up to 10% for exclamations
                elif pattern_name in ['action_words', 'emotional_words']:
                    engagement_score += min(0.15, density * 20)  # Up to 15% for action/emotional words
                elif pattern_name in ['urgency_words', 'power_words']:
                    engagement_score += min(0.10, density * 15)  # Up to 10% for urgency/power words
            
            # Analyze hook strength (first 50 words)
            first_words = ' '.join(content.split()[:50]).lower()
            hook_indicators = ['did you know', 'imagine', 'what if', 'here\'s why', 'secret', 'discover']
            
            hook_score = 0.0
            for indicator in hook_indicators:
                if indicator in first_words:
                    hook_score += 0.05
            
            engagement_score += min(0.2, hook_score)
            
            # Check for call-to-action
            cta_patterns = [
                r'\b(click|subscribe|follow|share|comment|like|buy|get|download|sign up)\b',
                r'\b(learn more|find out|discover|explore|try now|start today)\b'
            ]
            
            cta_score = 0.0
            for pattern in cta_patterns:
                if re.search(pattern, content_lower):
                    cta_score += 0.05
            
            engagement_score += min(0.15, cta_score)
            
            # Content type adjustments
            if content_type == 'social':
                # Social content should be more engaging
                engagement_score *= 1.2
            elif content_type == 'blog':
                # Blog content can be less immediately engaging
                engagement_score *= 0.9
            
            return min(1.0, max(0.0, engagement_score))
            
        except Exception as e:
            self.logger.warning(f"Engagement analysis failed: {str(e)}")
            return 0.5
    
    async def _analyze_seo_quality(self, content: str, keywords: Optional[List[str]]) -> float:
        """Analyze SEO quality"""        try:
            seo_score = 0.0
            
            # Check content structure
            has_headings = bool(re.search(r'^#+\s+', content, re.MULTILINE))
            if has_headings:
                seo_score += 0.2
            
            # Check content length
            word_count = len(content.split())
            if 300 <= word_count <= 2000:  # Optimal length for most content
                seo_score += 0.2
            elif word_count >= 1000:  # Long-form content bonus
                seo_score += 0.25
            
            # Keyword analysis
            if keywords:
                keyword_score = 0.0
                content_lower = content.lower()
                
                for keyword in keywords:
                    keyword_lower = keyword.lower()
                    keyword_count = content_lower.count(keyword_lower)
                    keyword_density = keyword_count / word_count if word_count > 0 else 0
                    
                    # Optimal keyword density: 1-3%
                    if 0.01 <= keyword_density <= 0.03:
                        keyword_score += 0.1
                    elif keyword_density > 0:
                        keyword_score += 0.05  # Some keyword usage
                
                seo_score += min(0.3, keyword_score)
            else:
                seo_score += 0.15  # Neutral score when no keywords provided
            
            # Check for internal/external links
            links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
            if links:
                seo_score += 0.1
            
            # Check for lists and formatting
            has_lists = bool(re.search(r'^[\*\-\+]\s+', content, re.MULTILINE))
            if has_lists:
                seo_score += 0.1
            
            # Check for images/media references
            has_media = bool(re.search(r'!\[([^\]]*)\]\(([^)]+)\)', content))
            if has_media:
                seo_score += 0.1
            
            return min(1.0, max(0.0, seo_score))
            
        except Exception as e:
            self.logger.warning(f"SEO analysis failed: {str(e)}")
            return 0.5
    
    async def _analyze_originality(self, content: str) -> float:
        """Analyze content originality and uniqueness"""        try:
            originality_score = 0.5  # Base score
            
            # Check for unique insights (simplified)
            insight_indicators = [
                'in my experience', 'i discovered', 'what i learned', 'here\'s what',
                'my approach', 'i found that', 'personally', 'from my perspective'
            ]
            
            content_lower = content.lower()
            personal_insight_count = sum(1 for indicator in insight_indicators if indicator in content_lower)
            
            if personal_insight_count > 0:
                originality_score += min(0.2, personal_insight_count * 0.05)
            
            # Check for specific examples and data
            has_numbers = bool(re.search(r'\b\d+%|\$\d+|\d+x\b', content))
            has_examples = bool(re.search(r'\b(for example|such as|like|including)\b', content_lower))
            
            if has_numbers:
                originality_score += 0.1
            if has_examples:
                originality_score += 0.1
            
            # Check for quotes or citations
            has_quotes = bool(re.search(r'["""].*?["""]', content))
            if has_quotes:
                originality_score += 0.1
            
            # Vocabulary diversity
            words = re.findall(r'\b\w+\b', content_lower)
            unique_words = set(words)
            vocabulary_diversity = len(unique_words) / len(words) if words else 0
            
            # High vocabulary diversity indicates originality
            if vocabulary_diversity > 0.7:
                originality_score += 0.1
            elif vocabulary_diversity > 0.5:
                originality_score += 0.05
            
            return min(1.0, max(0.0, originality_score))
            
        except Exception as e:
            self.logger.warning(f"Originality analysis failed: {str(e)}")
            return 0.5
    
    async def _analyze_technical_quality(self, content: str) -> float:
        """Analyze technical quality (grammar, spelling, formatting)"""        try:
            technical_score = 0.8  # Start with high base score
            
            # Check for common grammar issues
            grammar_issues = 0
            
            # Double spaces
            if '  ' in content:
                grammar_issues += content.count('  ')
            
            # Missing spaces after punctuation
            missing_spaces = len(re.findall(r'[.!?][A-Z]', content))
            grammar_issues += missing_spaces
            
            # Check capitalization
            sentences = self._split_sentences(content)
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence and not sentence[0].isupper():
                    grammar_issues += 1
            
            # Check for proper paragraph structure
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            if len(paragraphs) < 2 and len(content.split()) > 100:
                grammar_issues += 1  # Long content should have paragraphs
            
            # Deduct score for grammar issues
            grammar_penalty = min(0.3, grammar_issues * 0.02)
            technical_score -= grammar_penalty
            
            # Check formatting consistency
            formatting_score = 0.0
            
            # Consistent heading format
            headings = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
            if headings:
                formatting_score += 0.1
            
            # Consistent list formatting
            list_items = re.findall(r'^[\*\-\+]\s+', content, re.MULTILINE)
            if list_items:
                formatting_score += 0.05
            
            technical_score += formatting_score
            
            return min(1.0, max(0.0, technical_score))
            
        except Exception as e:
            self.logger.warning(f"Technical analysis failed: {str(e)}")
            return 0.7
    
    async def _analyze_brand_alignment(self, content: str, brand_voice: Optional[str]) -> float:
        """Analyze brand voice alignment"""        try:
            if not brand_voice or brand_voice not in self.brand_voice_patterns:
                return 0.7  # Neutral score when no brand voice specified
            
            brand_pattern = self.brand_voice_patterns[brand_voice]
            content_lower = content.lower()
            
            alignment_score = 0.5  # Base score
            
            # Check for brand tone words
            tone_words_found = sum(1 for word in brand_pattern['tone_words'] if word in content_lower)
            if tone_words_found > 0:
                alignment_score += min(0.2, tone_words_found * 0.05)
            
            # Check for words to avoid
            avoid_words_found = sum(1 for word in brand_pattern['avoid_words'] if word in content_lower)
            if avoid_words_found > 0:
                alignment_score -= min(0.2, avoid_words_found * 0.05)
            
            # Check sentence style
            sentences = self._split_sentences(content)
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
            
            if brand_pattern['sentence_style'] == 'formal' and avg_sentence_length > 15:
                alignment_score += 0.1
            elif brand_pattern['sentence_style'] == 'conversational' and 10 <= avg_sentence_length <= 15:
                alignment_score += 0.1
            
            # Check for brand voice consistency
            if brand_voice == 'professional':
                # Professional content should avoid excessive exclamations
                exclamation_count = content.count('!')
                if exclamation_count / len(sentences) < 0.1:  # Less than 10% of sentences
                    alignment_score += 0.1
            elif brand_voice == 'casual':
                # Casual content can have contractions
                contractions = re.findall(r"\b\w+'\w+\b", content)
                if contractions:
                    alignment_score += 0.1
            
            return min(1.0, max(0.0, alignment_score))
            
        except Exception as e:
            self.logger.warning(f"Brand alignment analysis failed: {str(e)}")
            return 0.7
    
    async def _analyze_completeness(self, content: str, content_type: str) -> float:
        """Analyze content completeness and informativeness"""        try:
            completeness_score = 0.0
            
            # Check information depth based on content type
            word_count = len(content.split())
            
            # Minimum word counts by content type
            min_words = {
                'blog': 300,
                'social': 50,
                'email': 100,
                'article': 500,
                'tutorial': 800
            }
            
            min_required = min_words.get(content_type, 200)
            
            if word_count >= min_required:
                completeness_score += 0.3
            elif word_count >= min_required * 0.7:
                completeness_score += 0.2
            else:
                completeness_score += 0.1
            
            # Check for actionable information
            action_indicators = [
                'step', 'how to', 'follow these', 'instructions', 'guide',
                'tip', 'strategy', 'method', 'approach', 'technique'
            ]
            
            content_lower = content.lower()
            actionable_count = sum(1 for indicator in action_indicators if indicator in content_lower)
            
            if actionable_count > 0:
                completeness_score += min(0.2, actionable_count * 0.05)
            
            # Check for supporting elements
            has_examples = bool(re.search(r'\b(example|such as|for instance)\b', content_lower))
            has_lists = bool(re.search(r'^[\*\-\+]\s+', content, re.MULTILINE))
            has_headings = bool(re.search(r'^#+\s+', content, re.MULTILINE))
            
            if has_examples:
                completeness_score += 0.1
            if has_lists:
                completeness_score += 0.1
            if has_headings:
                completeness_score += 0.1
            
            # Check for conclusion or summary
            conclusion_indicators = ['conclusion', 'summary', 'in summary', 'to conclude', 'final thoughts']
            has_conclusion = any(indicator in content_lower for indicator in conclusion_indicators)
            
            if has_conclusion:
                completeness_score += 0.1
            
            # Check coverage (topics addressed)
            topics_covered = len(re.findall(r'^#+\s+', content, re.MULTILINE))
            if topics_covered >= 3:
                completeness_score += 0.1
            
            return min(1.0, max(0.0, completeness_score))
            
        except Exception as e:
            self.logger.warning(f"Completeness analysis failed: {str(e)}")
            return 0.6
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _flesch_reading_ease(self, text: str) -> float:
        """Calculate Flesch Reading Ease score"""        sentences = self._split_sentences(text)
        words = text.split()
        syllables = sum(self._count_syllables(word) for word in words)
        
        if len(sentences) == 0 or len(words) == 0:
            return 0
        
        score = 206.835 - (1.015 * len(words) / len(sentences)) - (84.6 * syllables / len(words))
        return max(0, min(100, score))
    
    def _flesch_kincaid_grade(self, text: str) -> float:
        """Calculate Flesch-Kincaid Grade Level"""        sentences = self._split_sentences(text)
        words = text.split()
        syllables = sum(self._count_syllables(word) for word in words)
        
        if len(sentences) == 0 or len(words) == 0:
            return 0
        
        grade = (0.39 * len(words) / len(sentences)) + (11.8 * syllables / len(words)) - 15.59
        return max(0, grade)
    
    def _gunning_fog_index(self, text: str) -> float:
        """Calculate Gunning Fog Index"""        sentences = self._split_sentences(text)
        words = text.split()
        complex_words = sum(1 for word in words if self._count_syllables(word) >= 3)
        
        if len(sentences) == 0 or len(words) == 0:
            return 0
        
        fog = 0.4 * ((len(words) / len(sentences)) + (100 * complex_words / len(words)))
        return max(0, fog)
    
    def _smog_index(self, text: str) -> float:
        """Calculate SMOG Index"""        sentences = self._split_sentences(text)
        if len(sentences) < 30:
            return self._gunning_fog_index(text)  # Fallback for short text
        
        words = text.split()
        complex_words = sum(1 for word in words if self._count_syllables(word) >= 3)
        
        smog = 1.0430 * math.sqrt(complex_words * 30 / len(sentences)) + 3.1291
        return max(0, smog)
    
    def _coleman_liau_index(self, text: str) -> float:
        """Calculate Coleman-Liau Index"""        sentences = self._split_sentences(text)
        words = text.split()
        letters = sum(len(re.sub(r'[^a-zA-Z]', '', word)) for word in words)
        
        if len(words) == 0:
            return 0
        
        l = letters / len(words) * 100  # Average letters per 100 words
        s = len(sentences) / len(words) * 100  # Average sentences per 100 words
        
        cli = 0.0588 * l - 0.296 * s - 15.8
        return max(0, cli)
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified)"""        word = word.lower().strip()
        if not word:
            return 0
        
        # Remove non-alphabetic characters
        word = re.sub(r'[^a-z]', '', word)
        
        # Count vowel groups
        vowels = 'aeiouy'
        syllable_count = 0
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel
        
        # Handle silent e
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1
        
        # Every word has at least one syllable
        return max(1, syllable_count)
    
    def _get_quality_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""        for grade, threshold in self.grade_boundaries.items():
            if score >= threshold:
                return grade
        return 'F'
    
    async def _generate_improvement_suggestions(
        self,
        dimension_scores: Dict[str, float],
        content: str,
        content_type: str
    ) -> List[str]:
        """Generate specific improvement suggestions"""        suggestions = []
        
        # Readability improvements
        if dimension_scores.get('readability', 0) < 0.7:
            sentences = self._split_sentences(content)
            avg_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
            
            if avg_length > 20:
                suggestions.append("Break down long sentences for better readability")
            
            words = content.split()
            avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
            
            if avg_word_length > 6:
                suggestions.append("Use simpler words to improve accessibility")
        
        # Engagement improvements
        if dimension_scores.get('engagement', 0) < 0.6:
            if '?' not in content:
                suggestions.append("Add questions to increase engagement")
            
            if not re.search(r'\b(click|subscribe|follow|share)\b', content.lower()):
                suggestions.append("Include a clear call-to-action")
        
        # SEO improvements
        if dimension_scores.get('seo', 0) < 0.6:
            if not re.search(r'^#+\s+', content, re.MULTILINE):
                suggestions.append("Add headings to improve content structure")
            
            word_count = len(content.split())
            if word_count < 300:
                suggestions.append("Expand content length for better SEO performance")
        
        # Technical improvements
        if dimension_scores.get('technical', 0) < 0.8:
            if '  ' in content:
                suggestions.append("Remove double spaces and fix formatting")
            
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            if len(paragraphs) < 2 and len(content.split()) > 100:
                suggestions.append("Break content into paragraphs for better readability")
        
        # Originality improvements
        if dimension_scores.get('originality', 0) < 0.6:
            suggestions.append("Add personal insights or unique perspectives")
            suggestions.append("Include specific examples or data to support points")
        
        return suggestions[:5]  # Return top 5 suggestions


class ContentQualityAnalyzer:
    """Advanced content quality analysis system"""    
    def __init__(self):
        self.analyzer_config = {
            'grammar_weight': 0.3,
            'readability_weight': 0.25,
            'engagement_weight': 0.25,
            'seo_weight': 0.2
        }
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def analyze_structure(self, content: str) -> Dict[str, Any]:
        """Analyze content structure and organization"""        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        words = content.split()
        
        structure_metrics = {
            'paragraph_count': len(paragraphs),
            'sentence_count': len(sentences),
            'word_count': len(words),
            'avg_paragraph_length': len(words) / len(paragraphs) if paragraphs else 0,
            'avg_sentence_length': len(words) / len(sentences) if sentences else 0,
            'has_headings': any(line.startswith('#') for line in content.split('\n')),
            'has_lists': any(line.strip().startswith(('-', '*', '1.')) for line in content.split('\n'))
        }
        
        # Structure quality score
        score = 0.5  # Base score
        
        # Paragraph structure
        if 3 <= structure_metrics['paragraph_count'] <= 8:
            score += 0.2
        
        # Sentence length
        if 15 <= structure_metrics['avg_sentence_length'] <= 25:
            score += 0.15
        
        # Content organization
        if structure_metrics['has_headings']:
            score += 0.1
        if structure_metrics['has_lists']:
            score += 0.05
        
        structure_metrics['quality_score'] = min(1.0, score)
        return structure_metrics
    
    def analyze_comprehensiveness(self, content: str, topic: str = "") -> Dict[str, Any]:
        """Analyze content comprehensiveness and depth"""        words = content.split()
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        
        comprehensiveness_metrics = {
            'content_depth': len(words) / 100,  # Simplified metric
            'topic_coverage': 0.7,  # Mock implementation
            'detail_level': len([s for s in sentences if len(s.split()) > 20]) / len(sentences) if sentences else 0,
            'examples_count': content.lower().count('example') + content.lower().count('for instance'),
            'citations_count': content.count('[') + content.count('('),
            'actionable_insights': content.lower().count('how to') + content.lower().count('step')
        }
        
        # Comprehensiveness score
        score = 0.3  # Base score
        score += min(0.3, comprehensiveness_metrics['content_depth'] * 0.1)
        score += min(0.2, comprehensiveness_metrics['examples_count'] * 0.05)
        score += min(0.1, comprehensiveness_metrics['actionable_insights'] * 0.02)
        score += min(0.1, comprehensiveness_metrics['citations_count'] * 0.01)
        
        comprehensiveness_metrics['quality_score'] = min(1.0, score)
        return comprehensiveness_metrics
