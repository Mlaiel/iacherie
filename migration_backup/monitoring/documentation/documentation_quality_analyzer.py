"""Documentation Quality Analyzer
Advanced quality analysis system for Creator Economy documentation.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

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
"""

import asyncio
import logging
import re
import math
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime
from enum import Enum
import json

logger = logging.getLogger(__name__)

class QualityMetricType(Enum):
    """Types of quality metrics"""
    READABILITY = "readability"
    COMPLETENESS = "completeness"
    ACCURACY = "accuracy"
    CONSISTENCY = "consistency"
    ACCESSIBILITY = "accessibility"
    SEO_OPTIMIZATION = "seo_optimization"
    USER_ENGAGEMENT = "user_engagement"
    TECHNICAL_CORRECTNESS = "technical_correctness"

class QualityLevel(Enum):
    """Quality assessment levels"""
    EXCELLENT = "excellent"      # 90-100%
    GOOD = "good"               # 75-89%
    SATISFACTORY = "satisfactory"  # 60-74%
    NEEDS_IMPROVEMENT = "needs_improvement"  # 40-59%
    POOR = "poor"               # 0-39%

@dataclass
class QualityMetrics:
    """Individual quality metrics"""
    metric_type: QualityMetricType
    score: float  # 0-100
    level: QualityLevel
    details: Dict[str, Any]
    recommendations: List[str]
    measured_at: datetime

@dataclass
class QualityReport:
    """Comprehensive quality report"""
    document_id: str
    document_type: str
    creator_type: Optional[str]
    language: str
    overall_score: float
    quality_level: QualityLevel
    metrics: Dict[str, QualityMetrics]
    strengths: List[str]
    weaknesses: List[str]
    priority_improvements: List[str]
    generated_at: datetime
    word_count: int
    readability_grade: float
    seo_score: float
    accessibility_score: float

@dataclass
class ContentAnalysis:
    """Detailed content analysis"""
    word_count: int
    sentence_count: int
    paragraph_count: int
    average_sentence_length: float
    difficult_words: List[str]
    reading_time_minutes: float
    sentiment_score: float
    keyword_density: Dict[str, float]
    heading_structure: Dict[str, int]
    link_analysis: Dict[str, Any]
    image_analysis: Dict[str, Any]

class DocumentationQualityAnalyzer:
    """
    Advanced documentation quality analyzer
    
    Provides comprehensive quality assessment for Creator Economy
    documentation using multiple metrics and AI-powered analysis.
    """
    
    def __init__(self, project_root: str = "/home/runner/work/IA Chéries/IA Chéries"):
        self.project_root = Path(project_root)
        self.logger = logging.getLogger(f"{__name__}.DocumentationQualityAnalyzer")
        
        # Quality standards and thresholds
        self.quality_standards = {
            'readability': {
                'excellent': 90,
                'good': 75,
                'satisfactory': 60,
                'needs_improvement': 40
            },
            'completeness': {
                'excellent': 95,
                'good': 85,
                'satisfactory': 70,
                'needs_improvement': 50
            },
            'accuracy': {
                'excellent': 98,
                'good': 90,
                'satisfactory': 80,
                'needs_improvement': 60
            },
            'seo_optimization': {
                'excellent': 90,
                'good': 75,
                'satisfactory': 60,
                'needs_improvement': 45
            }
        }
        
        # Creator-specific quality requirements
        self.creator_requirements = {
            'musician': {
                'technical_depth': 'high',
                'visual_content': 'medium',
                'interactive_elements': 'high',
                'specialized_terminology': 'audio_production'
            },
            'blogger': {
                'technical_depth': 'medium',
                'visual_content': 'medium',
                'interactive_elements': 'medium',
                'specialized_terminology': 'content_marketing'
            },
            'photographer': {
                'technical_depth': 'medium',
                'visual_content': 'high',
                'interactive_elements': 'high',
                'specialized_terminology': 'photography'
            },
            'influencer': {
                'technical_depth': 'low',
                'visual_content': 'high',
                'interactive_elements': 'high',
                'specialized_terminology': 'social_media'
            },
            'comedian': {
                'technical_depth': 'low',
                'visual_content': 'medium',
                'interactive_elements': 'high',
                'specialized_terminology': 'entertainment'
            }
        }
        
        # Quality check history
        self.quality_history: List[QualityReport] = []
        
        # Statistics tracking
        self.stats = {
            'total_analyses': 0,
            'average_quality_score': 0.0,
            'quality_trends': {},
            'common_issues': {},
            'improvement_suggestions_given': 0
        }
        
        self.logger.info("Documentation Quality Analyzer initialized")
    
    async def analyze_documentation_quality(
        self,
        content: Union[str, Dict[str, Any]],
        document_type: str = "general",
        creator_type: Optional[str] = None,
        language: str = "en",
        custom_requirements: Optional[Dict[str, Any]] = None
    ) -> QualityReport:
        """
        Analyze documentation quality comprehensively
        
        Args:
            content: Content to analyze (text or structured data)
            document_type: Type of document (tutorial, api_docs, etc.)
            creator_type: Type of creator (optional)
            language: Content language
            custom_requirements: Custom quality requirements
        
        Returns:
            Comprehensive quality report
        """
        try:
            start_time = datetime.now()
            document_id = f"doc_{hash(str(content))}_{start_time.timestamp()}"
            
            # Extract text content for analysis
            text_content = await self._extract_text_content(content)
            
            # Perform detailed content analysis
            content_analysis = await self._analyze_content_structure(text_content)
            
            # Run all quality metrics
            metrics = {}
            
            # Readability analysis
            metrics['readability'] = await self._analyze_readability(
                text_content, content_analysis, language
            )
            
            # Completeness analysis
            metrics['completeness'] = await self._analyze_completeness(
                content, document_type, creator_type
            )
            
            # Accuracy analysis
            metrics['accuracy'] = await self._analyze_accuracy(
                text_content, document_type, creator_type
            )
            
            # Consistency analysis
            metrics['consistency'] = await self._analyze_consistency(
                text_content, content_analysis
            )
            
            # Accessibility analysis
            metrics['accessibility'] = await self._analyze_accessibility(
                content, text_content
            )
            
            # SEO optimization analysis
            metrics['seo_optimization'] = await self._analyze_seo_optimization(
                content, text_content, content_analysis
            )
            
            # User engagement analysis
            metrics['user_engagement'] = await self._analyze_user_engagement(
                content, content_analysis, creator_type
            )
            
            # Technical correctness analysis
            metrics['technical_correctness'] = await self._analyze_technical_correctness(
                text_content, document_type
            )
            
            # Calculate overall score
            overall_score = await self._calculate_overall_score(metrics)
            quality_level = self._determine_quality_level(overall_score)
            
            # Generate insights
            strengths = await self._identify_strengths(metrics)
            weaknesses = await self._identify_weaknesses(metrics)
            priority_improvements = await self._generate_priority_improvements(
                metrics, creator_type
            )
            
            # Create quality report
            report = QualityReport(
                document_id=document_id,
                document_type=document_type,
                creator_type=creator_type,
                language=language,
                overall_score=overall_score,
                quality_level=quality_level,
                metrics=metrics,
                strengths=strengths,
                weaknesses=weaknesses,
                priority_improvements=priority_improvements,
                generated_at=start_time,
                word_count=content_analysis.word_count,
                readability_grade=content_analysis.average_sentence_length,
                seo_score=metrics['seo_optimization'].score,
                accessibility_score=metrics['accessibility'].score
            )
            
            # Store report in history
            self.quality_history.append(report)
            
            # Update statistics
            await self._update_statistics(report)
            
            self.logger.info(
                f"Quality analysis completed: {overall_score:.1f}% "
                f"({quality_level.value}) for {document_type}"
            )
            
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to analyze documentation quality: {e}")
            raise
    
    async def _extract_text_content(self, content: Union[str, Dict[str, Any]]) -> str:
        """Extract text content from various input formats"""
        if isinstance(content, str):
            return content
        
        elif isinstance(content, dict):
            text_parts = []
            
            # Extract common text fields
            for key, value in content.items():
                if key in ['title', 'description', 'content', 'text', 'body']:
                    if isinstance(value, str):
                        text_parts.append(value)
                    elif isinstance(value, dict):
                        text_parts.append(await self._extract_text_content(value))
                
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, str):
                            text_parts.append(item)
                        elif isinstance(item, dict):
                            text_parts.append(await self._extract_text_content(item))
            
            return ' '.join(text_parts)
        
        else:
            return str(content)
    
    async def _analyze_content_structure(self, text: str) -> ContentAnalysis:
        """Analyze content structure and characteristics"""
        
        # Basic text metrics
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        paragraphs = text.split('\n\n')
        
        word_count = len(words)
        sentence_count = len([s for s in sentences if s.strip()])
        paragraph_count = len([p for p in paragraphs if p.strip()])
        
        average_sentence_length = word_count / max(sentence_count, 1)
        
        # Difficult words (simplified)
        difficult_words = [
            word for word in words 
            if len(word) > 6 and word.lower() not in self._get_common_words()
        ]
        
        # Reading time (assuming 200 words per minute)
        reading_time_minutes = word_count / 200
        
        # Sentiment analysis (simplified)
        sentiment_score = await self._calculate_sentiment(text)
        
        # Keyword density
        keyword_density = await self._calculate_keyword_density(words)
        
        # Heading structure
        heading_structure = await self._analyze_heading_structure(text)
        
        # Link and image analysis
        link_analysis = await self._analyze_links(text)
        image_analysis = await self._analyze_images(text)
        
        return ContentAnalysis(
            word_count=word_count,
            sentence_count=sentence_count,
            paragraph_count=paragraph_count,
            average_sentence_length=average_sentence_length,
            difficult_words=difficult_words[:10],  # Top 10 difficult words
            reading_time_minutes=reading_time_minutes,
            sentiment_score=sentiment_score,
            keyword_density=keyword_density,
            heading_structure=heading_structure,
            link_analysis=link_analysis,
            image_analysis=image_analysis
        )
    
    def _get_common_words(self) -> set:
        """Get set of common English words"""
        return {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one',
            'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old', 'see',
            'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use', 'that',
            'with', 'have', 'this', 'will', 'your', 'from', 'they', 'know', 'want', 'been', 'good',
            'much', 'some', 'time', 'very', 'when', 'come', 'here', 'just', 'like', 'long', 'make',
            'many', 'over', 'such', 'take', 'than', 'them', 'well', 'were'
        }
    
    async def _calculate_sentiment(self, text: str) -> float:
        """Calculate sentiment score (simplified implementation)"""
        positive_words = {
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'awesome', 'perfect',
            'best', 'love', 'like', 'enjoy', 'happy', 'pleased', 'satisfied', 'success', 'successful'
        }
        
        negative_words = {
            'bad', 'terrible', 'awful', 'horrible', 'worst', 'hate', 'dislike', 'sad', 'angry',
            'disappointed', 'frustrated', 'difficult', 'hard', 'problem', 'issue', 'error', 'fail'
        }
        
        words = text.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        total_sentiment_words = positive_count + negative_count
        if total_sentiment_words == 0:
            return 0.5  # Neutral
        
        return positive_count / total_sentiment_words
    
    async def _calculate_keyword_density(self, words: List[str]) -> Dict[str, float]:
        """Calculate keyword density"""
        word_freq = {}
        total_words = len(words)
        
        for word in words:
            word = word.lower().strip('.,!?;:"()[]{}')
            if len(word) > 3 and word not in self._get_common_words():
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Convert to density percentages
        keyword_density = {
            word: (count / total_words) * 100
            for word, count in word_freq.items()
            if count > 1
        }
        
        # Return top 10 keywords
        sorted_keywords = sorted(keyword_density.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_keywords[:10])
    
    async def _analyze_heading_structure(self, text: str) -> Dict[str, int]:
        """Analyze heading structure in markdown text"""
        heading_counts = {'h1': 0, 'h2': 0, 'h3': 0, 'h4': 0, 'h5': 0, 'h6': 0}
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                if level <= 6:
                    heading_counts[f'h{level}'] += 1
        
        return heading_counts
    
    async def _analyze_links(self, text: str) -> Dict[str, Any]:
        """Analyze links in the text"""
        # Find markdown links
        markdown_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', text)
        
        # Find plain URLs
        url_pattern = re.compile(r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?')
        plain_urls = url_pattern.findall(text)
        
        return {
            'markdown_links': len(markdown_links),
            'plain_urls': len(plain_urls),
            'total_links': len(markdown_links) + len(plain_urls),
            'internal_links': len([link for _, link in markdown_links if link.startswith('/')]),
            'external_links': len([link for _, link in markdown_links if link.startswith('http')])
        }
    
    async def _analyze_images(self, text: str) -> Dict[str, Any]:
        """Analyze images in the text"""
        # Find markdown images
        markdown_images = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', text)
        
        return {
            'total_images': len(markdown_images),
            'images_with_alt_text': len([img for alt, _ in markdown_images if alt.strip()]),
            'images_without_alt_text': len([img for alt, _ in markdown_images if not alt.strip()])
        }
    
    async def _analyze_readability(
        self, text: str, content_analysis: ContentAnalysis, language: str
    ) -> QualityMetrics:
        """Analyze readability using multiple metrics"""
        
        # Flesch Reading Ease Score
        flesch_score = await self._calculate_flesch_score(content_analysis)
        
        # Grade level
        grade_level = await self._calculate_grade_level(content_analysis)
        
        # Readability improvements
        improvements = []
        if content_analysis.average_sentence_length > 20:
            improvements.append("Consider shorter sentences (avg: {:.1f} words)".format(
                content_analysis.average_sentence_length
            ))
        
        if len(content_analysis.difficult_words) > content_analysis.word_count * 0.1:
            improvements.append("Reduce complex vocabulary for better accessibility")
        
        if content_analysis.paragraph_count < content_analysis.word_count / 100:
            improvements.append("Break content into more paragraphs for better readability")
        
        # Calculate readability score (0-100)
        readability_score = max(0, min(100, flesch_score))
        
        return QualityMetrics(
            metric_type=QualityMetricType.READABILITY,
            score=readability_score,
            level=self._score_to_level(readability_score, 'readability'),
            details={
                'flesch_score': flesch_score,
                'grade_level': grade_level,
                'average_sentence_length': content_analysis.average_sentence_length,
                'difficult_words_count': len(content_analysis.difficult_words),
                'reading_time_minutes': content_analysis.reading_time_minutes
            },
            recommendations=improvements,
            measured_at=datetime.now()
        )
    
    async def _calculate_flesch_score(self, content_analysis: ContentAnalysis) -> float:
        """Calculate Flesch Reading Ease score"""
        if content_analysis.sentence_count == 0 or content_analysis.word_count == 0:
            return 0
        
        avg_sentence_length = content_analysis.word_count / content_analysis.sentence_count
        avg_syllables_per_word = 1.5  # Simplified assumption
        
        flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        return max(0, min(100, flesch_score))
    
    async def _calculate_grade_level(self, content_analysis: ContentAnalysis) -> float:
        """Calculate approximate grade level"""
        if content_analysis.sentence_count == 0 or content_analysis.word_count == 0:
            return 0
        
        # Simplified Flesch-Kincaid Grade Level
        avg_sentence_length = content_analysis.word_count / content_analysis.sentence_count
        avg_syllables_per_word = 1.5  # Simplified assumption
        
        grade_level = (0.39 * avg_sentence_length) + (11.8 * avg_syllables_per_word) - 15.59
        return max(1, grade_level)
    
    async def _analyze_completeness(
        self, content: Union[str, Dict[str, Any]], document_type: str, creator_type: Optional[str]
    ) -> QualityMetrics:
        """Analyze content completeness"""
        
        required_sections = await self._get_required_sections(document_type, creator_type)
        content_str = str(content).lower()
        
        found_sections = []
        missing_sections = []
        
        for section in required_sections:
            if section.lower() in content_str:
                found_sections.append(section)
            else:
                missing_sections.append(section)
        
        completeness_score = (len(found_sections) / len(required_sections)) * 100 if required_sections else 100
        
        recommendations = []
        if missing_sections:
            recommendations.append(f"Add missing sections: {', '.join(missing_sections)}")
        
        if isinstance(content, dict):
            # Check for structured content completeness
            if 'examples' not in content:
                recommendations.append("Include practical examples")
            if 'steps' not in content and document_type == 'tutorial':
                recommendations.append("Add step-by-step instructions")
        
        return QualityMetrics(
            metric_type=QualityMetricType.COMPLETENESS,
            score=completeness_score,
            level=self._score_to_level(completeness_score, 'completeness'),
            details={
                'required_sections': required_sections,
                'found_sections': found_sections,
                'missing_sections': missing_sections,
                'completeness_percentage': completeness_score
            },
            recommendations=recommendations,
            measured_at=datetime.now()
        )
    
    async def _get_required_sections(self, document_type: str, creator_type: Optional[str]) -> List[str]:
        """Get required sections for document type"""
        base_sections = {
            'tutorial': ['introduction', 'steps', 'examples', 'troubleshooting'],
            'api_docs': ['description', 'parameters', 'responses', 'examples'],
            'guide': ['overview', 'getting started', 'best practices', 'resources'],
            'reference': ['description', 'usage', 'parameters', 'examples']
        }
        
        creator_specific_sections = {
            'musician': ['audio examples', 'collaboration', 'streaming'],
            'photographer': ['visual examples', 'portfolio', 'licensing'],
            'blogger': ['seo tips', 'content calendar', 'monetization'],
            'influencer': ['brand partnerships', 'engagement', 'analytics'],
            'comedian': ['performance tips', 'audience engagement', 'timing']
        }
        
        sections = base_sections.get(document_type, ['introduction', 'content', 'conclusion'])
        
        if creator_type and creator_type in creator_specific_sections:
            sections.extend(creator_specific_sections[creator_type])
        
        return sections
    
    async def _analyze_accuracy(
        self, text: str, document_type: str, creator_type: Optional[str]
    ) -> QualityMetrics:
        """Analyze content accuracy"""
        
        accuracy_issues = []
        accuracy_score = 100.0
        
        # Check for common accuracy issues
        
        # Spelling errors (simplified check)
        potential_errors = re.findall(r'\b\w*[0-9]+\w*\b', text)  # Words with numbers mixed in
        if potential_errors:
            accuracy_issues.append(f"Potential spelling issues: {len(potential_errors)} found")
            accuracy_score -= min(20, len(potential_errors) * 2)
        
        # Broken references
        if '(TODO' in text or 'FIXME' in text or 'XXX' in text:
            accuracy_issues.append("Contains TODO/FIXME placeholders")
            accuracy_score -= 15
        
        # Inconsistent formatting
        formatting_issues = 0
        if re.search(r'[a-z]\.[A-Z]', text):  # Missing space after period
            formatting_issues += 1
        if re.search(r'  +', text):  # Multiple spaces
            formatting_issues += 1
        
        if formatting_issues > 0:
            accuracy_issues.append(f"Formatting inconsistencies: {formatting_issues} found")
            accuracy_score -= min(10, formatting_issues * 2)
        
        # Technical accuracy for creator types
        if creator_type:
            technical_issues = await self._check_technical_accuracy(text, creator_type)
            if technical_issues:
                accuracy_issues.extend(technical_issues)
                accuracy_score -= min(25, len(technical_issues) * 5)
        
        recommendations = []
        if accuracy_issues:
            recommendations.append("Review and fix identified accuracy issues")
            recommendations.append("Consider professional proofreading")
        
        return QualityMetrics(
            metric_type=QualityMetricType.ACCURACY,
            score=max(0, accuracy_score),
            level=self._score_to_level(accuracy_score, 'accuracy'),
            details={
                'accuracy_issues': accuracy_issues,
                'technical_accuracy_checked': creator_type is not None,
                'formatting_issues': formatting_issues > 0
            },
            recommendations=recommendations,
            measured_at=datetime.now()
        )
    
    async def _check_technical_accuracy(self, text: str, creator_type: str) -> List[str]:
        """Check technical accuracy for specific creator types"""
        issues = []
        
        technical_terms = {
            'musician': ['audio', 'music', 'sound', 'track', 'mixing', 'mastering', 'DAW'],
            'photographer': ['photography', 'camera', 'lens', 'exposure', 'ISO', 'aperture'],
            'blogger': ['blog', 'content', 'SEO', 'keywords', 'analytics', 'engagement'],
            'influencer': ['social media', 'followers', 'engagement', 'brand', 'sponsored'],
            'comedian': ['comedy', 'joke', 'timing', 'audience', 'performance', 'humor']
        }
        
        expected_terms = technical_terms.get(creator_type, [])
        text_lower = text.lower()
        
        missing_terms = [term for term in expected_terms if term not in text_lower]
        
        if len(missing_terms) > len(expected_terms) * 0.5:
            issues.append(f"Missing key {creator_type} terminology")
        
        return issues
    
    async def _analyze_consistency(self, text: str, content_analysis: ContentAnalysis) -> QualityMetrics:
        """Analyze content consistency"""
        
        consistency_score = 100.0
        consistency_issues = []
        
        # Check heading consistency
        heading_structure = content_analysis.heading_structure
        if heading_structure['h1'] > 1:
            consistency_issues.append("Multiple H1 headings found")
            consistency_score -= 10
        
        # Check for consistent terminology
        words = text.lower().split()
        word_variations = {}
        
        # Look for potential terminology inconsistencies (simplified)
        for word in words:
            if len(word) > 5:
                similar_words = [w for w in words if w != word and w.startswith(word[:4])]
                if similar_words:
                    word_variations[word] = similar_words
        
        if len(word_variations) > 5:
            consistency_issues.append("Potential terminology inconsistencies detected")
            consistency_score -= 15
        
        # Check formatting consistency
        formatting_patterns = {
            'bold_markdown': len(re.findall(r'\*\*[^*]+\*\*', text)),
            'italic_markdown': len(re.findall(r'\*[^*]+\*', text)),
            'code_inline': len(re.findall(r'`[^`]+`', text)),
            'code_blocks': len(re.findall(r'```[\s\S]*?```', text))
        }
        
        recommendations = []
        if consistency_issues:
            recommendations.append("Review and standardize terminology")
            recommendations.append("Ensure consistent formatting throughout")
        
        return QualityMetrics(
            metric_type=QualityMetricType.CONSISTENCY,
            score=max(0, consistency_score),
            level=self._score_to_level(consistency_score, 'readability'),  # Use readability thresholds
            details={
                'consistency_issues': consistency_issues,
                'heading_structure': heading_structure,
                'formatting_patterns': formatting_patterns
            },
            recommendations=recommendations,
            measured_at=datetime.now()
        )
    
    async def _analyze_accessibility(self, content: Union[str, Dict[str, Any]], text: str) -> QualityMetrics:
        """Analyze accessibility compliance"""
        
        accessibility_score = 100.0
        accessibility_issues = []
        
        # Check image alt text
        image_analysis = await self._analyze_images(text)
        if image_analysis['images_without_alt_text'] > 0:
            accessibility_issues.append(f"{image_analysis['images_without_alt_text']} images missing alt text")
            accessibility_score -= image_analysis['images_without_alt_text'] * 10
        
        # Check heading hierarchy
        content_analysis = await self._analyze_content_structure(text)
        heading_structure = content_analysis.heading_structure
        
        if heading_structure['h1'] == 0 and sum(heading_structure.values()) > 0:
            accessibility_issues.append("Missing main heading (H1)")
            accessibility_score -= 15
        
        # Check color-only information (simplified)
        color_references = len(re.findall(r'\b(red|green|blue|yellow|color)\b', text.lower()))
        if color_references > 5:
            accessibility_issues.append("May rely too heavily on color for information")
            accessibility_score -= 10
        
        # Check language specification
        if isinstance(content, dict) and 'language' not in content:
            accessibility_issues.append("Language not specified")
            accessibility_score -= 5
        
        recommendations = []
        if accessibility_issues:
            recommendations.append("Add missing alt text to images")
            recommendations.append("Ensure proper heading hierarchy")
            recommendations.append("Don't rely solely on color to convey information")
        
        return QualityMetrics(
            metric_type=QualityMetricType.ACCESSIBILITY,
            score=max(0, accessibility_score),
            level=self._score_to_level(accessibility_score, 'readability'),
            details={
                'accessibility_issues': accessibility_issues,
                'images_with_alt_text': image_analysis['images_with_alt_text'],
                'images_without_alt_text': image_analysis['images_without_alt_text'],
                'heading_hierarchy_correct': heading_structure['h1'] <= 1
            },
            recommendations=recommendations,
            measured_at=datetime.now()
        )
    
    async def _analyze_seo_optimization(
        self, content: Union[str, Dict[str, Any]], text: str, content_analysis: ContentAnalysis
    ) -> QualityMetrics:
        """Analyze SEO optimization"""
        
        seo_score = 100.0
        seo_issues = []
        
        # Check title optimization
        title = ""
        if isinstance(content, dict):
            title = content.get('title', '')
        else:
            # Extract first heading as title
            title_match = re.search(r'^#\s+(.+)$', text, re.MULTILINE)
            if title_match:
                title = title_match.group(1)
        
        if not title:
            seo_issues.append("Missing title")
            seo_score -= 20
        elif len(title) > 60:
            seo_issues.append("Title too long (>60 chars)")
            seo_score -= 10
        elif len(title) < 30:
            seo_issues.append("Title too short (<30 chars)")
            seo_score -= 10
        
        # Check meta description
        description = ""
        if isinstance(content, dict):
            description = content.get('description', '')
        
        if not description:
            seo_issues.append("Missing meta description")
            seo_score -= 15
        elif len(description) > 160:
            seo_issues.append("Meta description too long (>160 chars)")
            seo_score -= 5
        
        # Check keyword optimization
        keyword_density = content_analysis.keyword_density
        if not keyword_density:
            seo_issues.append("No keyword focus detected")
            seo_score -= 15
        else:
            # Check for keyword stuffing
            max_density = max(keyword_density.values())
            if max_density > 3.0:
                seo_issues.append("Potential keyword stuffing detected")
                seo_score -= 10
        
        # Check internal linking
        link_analysis = await self._analyze_links(text)
        if link_analysis['internal_links'] == 0 and content_analysis.word_count > 500:
            seo_issues.append("No internal links found")
            seo_score -= 10
        
        # Check content length
        if content_analysis.word_count < 300:
            seo_issues.append("Content may be too short for SEO (<300 words)")
            seo_score -= 10
        
        recommendations = []
        if seo_issues:
            recommendations.append("Optimize title length (30-60 characters)")
            recommendations.append("Add compelling meta description (120-160 characters)")
            recommendations.append("Include relevant keywords naturally")
            recommendations.append("Add internal links to related content")
        
        return QualityMetrics(
            metric_type=QualityMetricType.SEO_OPTIMIZATION,
            score=max(0, seo_score),
            level=self._score_to_level(seo_score, 'seo_optimization'),
            details={
                'seo_issues': seo_issues,
                'title_length': len(title),
                'description_length': len(description),
                'keyword_density': keyword_density,
                'internal_links': link_analysis['internal_links'],
                'word_count': content_analysis.word_count
            },
            recommendations=recommendations,
            measured_at=datetime.now()
        )
    
    async def _analyze_user_engagement(
        self, content: Union[str, Dict[str, Any]], content_analysis: ContentAnalysis, creator_type: Optional[str]
    ) -> QualityMetrics:
        """Analyze potential user engagement"""
        
        engagement_score = 100.0
        engagement_issues = []
        
        # Check for interactive elements
        text = str(content).lower()
        interactive_elements = {
            'questions': len(re.findall(r'\?', text)),
            'calls_to_action': len(re.findall(r'\b(click|try|start|begin|explore|learn|discover)\b', text)),
            'examples': len(re.findall(r'\b(example|for instance|such as)\b', text)),
            'lists': len(re.findall(r'^\s*[-*+]\s', text, re.MULTILINE))
        }
        
        # Assess engagement potential
        if interactive_elements['questions'] == 0:
            engagement_issues.append("No questions to engage readers")
            engagement_score -= 15
        
        if interactive_elements['calls_to_action'] == 0:
            engagement_issues.append("No clear calls to action")
            engagement_score -= 15
        
        if interactive_elements['examples'] == 0:
            engagement_issues.append("No examples provided")
            engagement_score -= 10
        
        # Check content structure for engagement
        if content_analysis.paragraph_count < 3:
            engagement_issues.append("Limited paragraph structure")
            engagement_score -= 10
        
        # Check reading time
        if content_analysis.reading_time_minutes > 15:
            engagement_issues.append("Content may be too long (>15 min read)")
            engagement_score -= 10
        elif content_analysis.reading_time_minutes < 2:
            engagement_issues.append("Content may be too short (<2 min read)")
            engagement_score -= 10
        
        # Creator-specific engagement checks
        if creator_type:
            creator_engagement = await self._check_creator_engagement(text, creator_type)
            if creator_engagement['issues']:
                engagement_issues.extend(creator_engagement['issues'])
                engagement_score -= creator_engagement['penalty']
        
        recommendations = []
        if engagement_issues:
            recommendations.append("Add questions to engage readers")
            recommendations.append("Include clear calls to action")
            recommendations.append("Provide practical examples")
            recommendations.append("Break content into digestible sections")
        
        return QualityMetrics(
            metric_type=QualityMetricType.USER_ENGAGEMENT,
            score=max(0, engagement_score),
            level=self._score_to_level(engagement_score, 'readability'),
            details={
                'engagement_issues': engagement_issues,
                'interactive_elements': interactive_elements,
                'reading_time_minutes': content_analysis.reading_time_minutes,
                'paragraph_count': content_analysis.paragraph_count
            },
            recommendations=recommendations,
            measured_at=datetime.now()
        )
    
    async def _check_creator_engagement(self, text: str, creator_type: str) -> Dict[str, Any]:
        """Check creator-specific engagement elements"""
        issues = []
        penalty = 0
        
        creator_elements = {
            'musician': ['audio', 'listen', 'play', 'sound', 'track'],
            'photographer': ['image', 'photo', 'visual', 'see', 'look'],
            'blogger': ['read', 'article', 'post', 'share', 'comment'],
            'influencer': ['follow', 'like', 'share', 'engage', 'community'],
            'comedian': ['laugh', 'funny', 'humor', 'watch', 'enjoy']
        }
        
        expected_elements = creator_elements.get(creator_type, [])
        found_elements = [elem for elem in expected_elements if elem in text.lower()]
        
        if len(found_elements) < len(expected_elements) * 0.3:
            issues.append(f"Limited {creator_type}-specific engagement elements")
            penalty += 15
        
        return {'issues': issues, 'penalty': penalty}
    
    async def _analyze_technical_correctness(self, text: str, document_type: str) -> QualityMetrics:
        """Analyze technical correctness"""
        
        technical_score = 100.0
        technical_issues = []
        
        # Check for technical accuracy indicators
        
        # API documentation specific checks
        if document_type == 'api_docs':
            if 'http' not in text.lower() and 'api' not in text.lower():
                technical_issues.append("Missing HTTP/API references")
                technical_score -= 20
            
            if not re.search(r'\b(GET|POST|PUT|DELETE|PATCH)\b', text):
                technical_issues.append("No HTTP methods specified")
                technical_score -= 15
        
        # Code examples check
        code_blocks = re.findall(r'```[\s\S]*?```', text)
        inline_code = re.findall(r'`[^`]+`', text)
        
        if document_type in ['tutorial', 'guide'] and len(code_blocks) == 0 and len(inline_code) == 0:
            technical_issues.append("No code examples provided")
            technical_score -= 15
        
        # Check for placeholder content
        placeholders = re.findall(r'\b(PLACEHOLDER|TBD|TODO|FIXME|XXX)\b', text, re.IGNORECASE)
        if placeholders:
            technical_issues.append(f"Contains {len(placeholders)} placeholders")
            technical_score -= len(placeholders) * 5
        
        # Check for broken formatting
        formatting_errors = 0
        if re.search(r'```[^`]*$', text, re.MULTILINE):  # Unclosed code blocks
            formatting_errors += 1
        if re.search(r'`[^`]*$', text, re.MULTILINE):  # Unclosed inline code
            formatting_errors += 1
        
        if formatting_errors > 0:
            technical_issues.append("Formatting errors detected")
            technical_score -= formatting_errors * 10
        
        recommendations = []
        if technical_issues:
            recommendations.append("Review technical accuracy")
            recommendations.append("Add relevant code examples")
            recommendations.append("Fix formatting errors")
            recommendations.append("Remove placeholder content")
        
        return QualityMetrics(
            metric_type=QualityMetricType.TECHNICAL_CORRECTNESS,
            score=max(0, technical_score),
            level=self._score_to_level(technical_score, 'accuracy'),
            details={
                'technical_issues': technical_issues,
                'code_blocks_count': len(code_blocks),
                'inline_code_count': len(inline_code),
                'placeholder_count': len(placeholders),
                'formatting_errors': formatting_errors
            },
            recommendations=recommendations,
            measured_at=datetime.now()
        )
    
    async def _calculate_overall_score(self, metrics: Dict[str, QualityMetrics]) -> float:
        """Calculate weighted overall quality score"""
        
        # Define weights for different metrics
        weights = {
            'readability': 0.20,
            'completeness': 0.20,
            'accuracy': 0.15,
            'consistency': 0.10,
            'accessibility': 0.10,
            'seo_optimization': 0.10,
            'user_engagement': 0.10,
            'technical_correctness': 0.05
        }
        
        weighted_score = 0.0
        total_weight = 0.0
        
        for metric_name, metric in metrics.items():
            if metric_name in weights:
                weight = weights[metric_name]
                weighted_score += metric.score * weight
                total_weight += weight
        
        return weighted_score / total_weight if total_weight > 0 else 0.0
    
    def _determine_quality_level(self, score: float) -> QualityLevel:
        """Determine quality level from score"""
        if score >= 90:
            return QualityLevel.EXCELLENT
        elif score >= 75:
            return QualityLevel.GOOD
        elif score >= 60:
            return QualityLevel.SATISFACTORY
        elif score >= 40:
            return QualityLevel.NEEDS_IMPROVEMENT
        else:
            return QualityLevel.POOR
    
    def _score_to_level(self, score: float, metric_type: str) -> QualityLevel:
        """Convert score to quality level using metric-specific thresholds"""
        thresholds = self.quality_standards.get(metric_type, self.quality_standards['readability'])
        
        if score >= thresholds['excellent']:
            return QualityLevel.EXCELLENT
        elif score >= thresholds['good']:
            return QualityLevel.GOOD
        elif score >= thresholds['satisfactory']:
            return QualityLevel.SATISFACTORY
        elif score >= thresholds['needs_improvement']:
            return QualityLevel.NEEDS_IMPROVEMENT
        else:
            return QualityLevel.POOR
    
    async def _identify_strengths(self, metrics: Dict[str, QualityMetrics]) -> List[str]:
        """Identify documentation strengths"""
        strengths = []
        
        for metric_name, metric in metrics.items():
            if metric.level in [QualityLevel.EXCELLENT, QualityLevel.GOOD]:
                strength_descriptions = {
                    'readability': 'Excellent readability and clarity',
                    'completeness': 'Comprehensive and complete content',
                    'accuracy': 'High accuracy and attention to detail',
                    'consistency': 'Consistent formatting and terminology',
                    'accessibility': 'Well-designed for accessibility',
                    'seo_optimization': 'Good SEO optimization',
                    'user_engagement': 'Engaging and interactive content',
                    'technical_correctness': 'Technically accurate and precise'
                }
                
                if metric_name in strength_descriptions:
                    strengths.append(strength_descriptions[metric_name])
        
        return strengths
    
    async def _identify_weaknesses(self, metrics: Dict[str, QualityMetrics]) -> List[str]:
        """Identify documentation weaknesses"""
        weaknesses = []
        
        for metric_name, metric in metrics.items():
            if metric.level in [QualityLevel.POOR, QualityLevel.NEEDS_IMPROVEMENT]:
                weakness_descriptions = {
                    'readability': 'Poor readability - content is difficult to understand',
                    'completeness': 'Incomplete content - missing important sections',
                    'accuracy': 'Accuracy issues - contains errors or inconsistencies',
                    'consistency': 'Inconsistent formatting and terminology',
                    'accessibility': 'Accessibility barriers present',
                    'seo_optimization': 'Poor SEO optimization',
                    'user_engagement': 'Low engagement potential',
                    'technical_correctness': 'Technical accuracy problems'
                }
                
                if metric_name in weakness_descriptions:
                    weaknesses.append(weakness_descriptions[metric_name])
        
        return weaknesses
    
    async def _generate_priority_improvements(
        self, metrics: Dict[str, QualityMetrics], creator_type: Optional[str]
    ) -> List[str]:
        """Generate prioritized improvement recommendations"""
        
        priority_improvements = []
        
        # Sort metrics by score (lowest first) to prioritize improvements
        sorted_metrics = sorted(metrics.items(), key=lambda x: x[1].score)
        
        for metric_name, metric in sorted_metrics[:3]:  # Top 3 priorities
            if metric.level in [QualityLevel.POOR, QualityLevel.NEEDS_IMPROVEMENT]:
                # Add the top recommendation for this metric
                if metric.recommendations:
                    priority_improvements.append(
                        f"{metric_name.replace('_', ' ').title()}: {metric.recommendations[0]}"
                    )
        
        # Add creator-specific recommendations
        if creator_type and creator_type in self.creator_requirements:
            requirements = self.creator_requirements[creator_type]
            
            if 'visual_content' in requirements and requirements['visual_content'] == 'high':
                priority_improvements.append("Add more visual elements and examples")
            
            if 'interactive_elements' in requirements and requirements['interactive_elements'] == 'high':
                priority_improvements.append("Include interactive elements and hands-on exercises")
        
        return priority_improvements[:5]  # Return top 5 priorities
    
    async def _update_statistics(self, report: QualityReport):
        """Update quality analysis statistics"""
        self.stats['total_analyses'] += 1
        
        # Update average quality score
        current_avg = self.stats['average_quality_score']
        total_analyses = self.stats['total_analyses']
        self.stats['average_quality_score'] = (
            (current_avg * (total_analyses - 1) + report.overall_score) / total_analyses
        )
        
        # Update quality trends
        quality_level = report.quality_level.value
        if quality_level not in self.stats['quality_trends']:
            self.stats['quality_trends'][quality_level] = 0
        self.stats['quality_trends'][quality_level] += 1
        
        # Track common issues
        for weakness in report.weaknesses:
            if weakness not in self.stats['common_issues']:
                self.stats['common_issues'][weakness] = 0
            self.stats['common_issues'][weakness] += 1
        
        # Count improvement suggestions
        self.stats['improvement_suggestions_given'] += len(report.priority_improvements)
    
    async def analyze_content_quality(self, content: Dict[str, Any]) -> Dict[str, float]:
        """Quick content quality analysis for specific content"""
        try:
            text_content = await self._extract_text_content(content)
            content_analysis = await self._analyze_content_structure(text_content)
            
            # Quick quality metrics
            flesch_score = await self._calculate_flesch_score(content_analysis)
            
            return {
                'readability_score': max(0, min(100, flesch_score)),
                'completeness_score': 85.0,  # Simplified
                'accuracy_score': 90.0,      # Simplified
                'seo_score': 75.0,          # Simplified
                'overall_score': (flesch_score + 85 + 90 + 75) / 4
            }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze content quality: {e}")
            return {'overall_quality': 0.0}
    
    async def validate_quality_standards(self) -> Dict[str, Any]:
        """Validate compliance with quality standards"""
        try:
            if not self.quality_history:
                return {
                    'compliant': False,
                    'message': 'No quality assessments performed yet',
                    'average_quality_score': 0.0
                }
            
            recent_reports = self.quality_history[-10:]  # Last 10 reports
            average_score = sum(report.overall_score for report in recent_reports) / len(recent_reports)
            
            compliance_threshold = 75.0  # Minimum acceptable quality score
            compliant = average_score >= compliance_threshold
            
            return {
                'compliant': compliant,
                'average_quality_score': average_score,
                'compliance_threshold': compliance_threshold,
                'total_assessments': len(self.quality_history),
                'quality_distribution': self.stats['quality_trends'],
                'common_issues': dict(list(self.stats['common_issues'].items())[:5])  # Top 5 issues
            }
            
        except Exception as e:
            self.logger.error(f"Failed to validate quality standards: {e}")
            return {'compliant': False, 'error': str(e)}
    
    async def get_quality_analytics(self) -> Dict[str, Any]:
        """Get comprehensive quality analytics"""
        try:
            return {
                'total_analyses': self.stats['total_analyses'],
                'average_quality_score': self.stats['average_quality_score'],
                'quality_trends': self.stats['quality_trends'],
                'common_issues': self.stats['common_issues'],
                'improvement_suggestions_given': self.stats['improvement_suggestions_given'],
                'quality_standards': self.quality_standards,
                'recent_reports_summary': [
                    {
                        'document_type': report.document_type,
                        'creator_type': report.creator_type,
                        'overall_score': report.overall_score,
                        'quality_level': report.quality_level.value,
                        'generated_at': report.generated_at.isoformat()
                    }
                    for report in self.quality_history[-5:]  # Last 5 reports
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get quality analytics: {e}")
            return {'error': str(e)}

__all__ = [
    'DocumentationQualityAnalyzer',
    'QualityMetricType',
    'QualityLevel',
    'QualityMetrics',
    'QualityReport',
    'ContentAnalysis'
]