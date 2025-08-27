"""
SEO Quality Analyzer - Enterprise SEO Optimization System

Advanced SEO analysis and optimization system for content quality assessment
with comprehensive SEO metrics, keyword analysis, and search optimization.

Business Logic:
Content analysis → SEO scoring → Keyword optimization → Meta tags validation →
Search readiness → SEO recommendations → Performance tracking

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
"""

import re
import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from urllib.parse import urlparse
import math

try:
    from textstat import flesch_reading_ease, flesch_kincaid_grade
    TEXTSTAT_AVAILABLE = True
except ImportError:
    TEXTSTAT_AVAILABLE = False

logger = logging.getLogger(__name__)


class SEOMetricType(Enum):
    """Types of SEO metrics"""
    CONTENT_QUALITY = "content_quality"
    KEYWORD_OPTIMIZATION = "keyword_optimization"
    TECHNICAL_SEO = "technical_seo"
    META_TAGS = "meta_tags"
    READABILITY = "readability"
    STRUCTURE = "structure"
    SOCIAL_MEDIA = "social_media"


class SEOLevel(Enum):
    """SEO optimization levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"


@dataclass
class SEOIssue:
    """Individual SEO issue"""
    category: SEOMetricType
    severity: str  # critical, error, warning, info
    message: str
    field: Optional[str] = None
    current_value: Optional[Any] = None
    recommended_value: Optional[Any] = None
    suggestions: List[str] = field(default_factory=list)
    impact_score: float = 0.0  # 0-10 scale
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'category': self.category.value,
            'severity': self.severity,
            'message': self.message,
            'field': self.field,
            'current_value': self.current_value,
            'recommended_value': self.recommended_value,
            'suggestions': self.suggestions,
            'impact_score': self.impact_score
        }


@dataclass
class KeywordAnalysis:
    """Keyword analysis results"""
    primary_keywords: List[str]
    secondary_keywords: List[str]
    keyword_density: Dict[str, float]
    keyword_placement: Dict[str, List[str]]  # keyword -> locations
    long_tail_keywords: List[str]
    keyword_score: float  # 0-100
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'primary_keywords': self.primary_keywords,
            'secondary_keywords': self.secondary_keywords,
            'keyword_density': self.keyword_density,
            'keyword_placement': self.keyword_placement,
            'long_tail_keywords': self.long_tail_keywords,
            'keyword_score': self.keyword_score
        }


@dataclass
class ReadabilityMetrics:
    """Content readability analysis"""
    flesch_score: Optional[float] = None
    flesch_grade: Optional[float] = None
    avg_sentence_length: float = 0.0
    avg_word_length: float = 0.0
    complex_words_ratio: float = 0.0
    readability_level: str = "unknown"
    readability_score: float = 0.0  # 0-100
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'flesch_score': self.flesch_score,
            'flesch_grade': self.flesch_grade,
            'avg_sentence_length': self.avg_sentence_length,
            'avg_word_length': self.avg_word_length,
            'complex_words_ratio': self.complex_words_ratio,
            'readability_level': self.readability_level,
            'readability_score': self.readability_score
        }


@dataclass
class SEOAnalysisResult:
    """Comprehensive SEO analysis result"""
    content_id: str
    overall_seo_score: float  # 0-100
    seo_level: SEOLevel
    
    # Component scores
    content_score: float = 0.0
    keyword_score: float = 0.0
    technical_score: float = 0.0
    meta_score: float = 0.0
    readability_score: float = 0.0
    structure_score: float = 0.0
    social_score: float = 0.0
    
    # Analysis results
    keyword_analysis: Optional[KeywordAnalysis] = None
    readability_metrics: Optional[ReadabilityMetrics] = None
    
    # Issues and recommendations
    issues: List[SEOIssue] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    # Metadata
    analysis_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    processing_time_ms: float = 0.0
    
    def add_issue(self, issue: SEOIssue):
        """Add an SEO issue"""
        self.issues.append(issue)
    
    def get_issues_by_category(self, category: SEOMetricType) -> List[SEOIssue]:
        """Get issues by category"""
        return [issue for issue in self.issues if issue.category == category]
    
    def get_critical_issues(self) -> List[SEOIssue]:
        """Get critical issues"""
        return [issue for issue in self.issues if issue.severity == 'critical']
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'content_id': self.content_id,
            'overall_seo_score': self.overall_seo_score,
            'seo_level': self.seo_level.value,
            'component_scores': {
                'content': self.content_score,
                'keyword': self.keyword_score,
                'technical': self.technical_score,
                'meta': self.meta_score,
                'readability': self.readability_score,
                'structure': self.structure_score,
                'social': self.social_score
            },
            'keyword_analysis': self.keyword_analysis.to_dict() if self.keyword_analysis else None,
            'readability_metrics': self.readability_metrics.to_dict() if self.readability_metrics else None,
            'issues': [issue.to_dict() for issue in self.issues],
            'recommendations': self.recommendations,
            'analysis_timestamp': self.analysis_timestamp.isoformat(),
            'processing_time_ms': self.processing_time_ms
        }


class KeywordAnalyzer:
    """Advanced keyword analysis and optimization"""
    
    def __init__(self):
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these',
            'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him',
            'her', 'us', 'them', 'my', 'your', 'his', 'hers', 'its', 'our', 'their'
        }
    
    def analyze_keywords(self, content: str, title: str = "", 
                        description: str = "") -> KeywordAnalysis:
        """Analyze keywords in content"""
        # Extract words and clean
        all_text = f"{title} {description} {content}".lower()
        words = self._extract_words(all_text)
        
        # Calculate word frequency
        word_freq = self._calculate_word_frequency(words)
        
        # Identify primary keywords (most frequent, significant words)
        primary_keywords = self._identify_primary_keywords(word_freq, words)
        
        # Identify secondary keywords
        secondary_keywords = self._identify_secondary_keywords(word_freq, primary_keywords)
        
        # Calculate keyword density
        total_words = len(words)
        keyword_density = {
            word: (count / total_words) * 100
            for word, count in word_freq.items()
            if word in primary_keywords + secondary_keywords
        }
        
        # Analyze keyword placement
        keyword_placement = self._analyze_keyword_placement(
            primary_keywords + secondary_keywords, title, description, content
        )
        
        # Identify long-tail keywords
        long_tail_keywords = self._identify_long_tail_keywords(content)
        
        # Calculate keyword score
        keyword_score = self._calculate_keyword_score(
            primary_keywords, secondary_keywords, keyword_density, keyword_placement
        )
        
        return KeywordAnalysis(
            primary_keywords=primary_keywords,
            secondary_keywords=secondary_keywords,
            keyword_density=keyword_density,
            keyword_placement=keyword_placement,
            long_tail_keywords=long_tail_keywords,
            keyword_score=keyword_score
        )
    
    def _extract_words(self, text: str) -> List[str]:
        """Extract and clean words from text"""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Extract words (letters and numbers)
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        
        # Filter out stop words and short words
        return [word for word in words if word not in self.stop_words and len(word) > 2]
    
    def _calculate_word_frequency(self, words: List[str]) -> Dict[str, int]:
        """Calculate word frequency"""
        freq = {}
        for word in words:
            freq[word] = freq.get(word, 0) + 1
        return freq
    
    def _identify_primary_keywords(self, word_freq: Dict[str, int], 
                                  words: List[str]) -> List[str]:
        """Identify primary keywords"""
        # Sort by frequency and take top candidates
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        # Select top 3-5 words with good frequency
        primary = []
        for word, count in sorted_words[:10]:
            if count >= 3 and len(word) > 3:  # Minimum frequency and length
                primary.append(word)
                if len(primary) >= 5:
                    break
        
        return primary[:5]
    
    def _identify_secondary_keywords(self, word_freq: Dict[str, int],
                                   primary_keywords: List[str]) -> List[str]:
        """Identify secondary keywords"""
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        secondary = []
        for word, count in sorted_words:
            if (word not in primary_keywords and 
                count >= 2 and 
                len(word) > 3):
                secondary.append(word)
                if len(secondary) >= 10:
                    break
        
        return secondary
    
    def _analyze_keyword_placement(self, keywords: List[str], title: str,
                                  description: str, content: str) -> Dict[str, List[str]]:
        """Analyze where keywords appear"""
        placement = {keyword: [] for keyword in keywords}
        
        for keyword in keywords:
            # Check title
            if keyword.lower() in title.lower():
                placement[keyword].append('title')
            
            # Check description
            if keyword.lower() in description.lower():
                placement[keyword].append('description')
            
            # Check beginning of content
            content_words = content.lower().split()[:50]  # First 50 words
            if keyword.lower() in ' '.join(content_words):
                placement[keyword].append('content_start')
            
            # Check end of content
            content_words = content.lower().split()[-50:]  # Last 50 words
            if keyword.lower() in ' '.join(content_words):
                placement[keyword].append('content_end')
            
            # Check throughout content
            if keyword.lower() in content.lower():
                placement[keyword].append('content_body')
        
        return placement
    
    def _identify_long_tail_keywords(self, content: str) -> List[str]:
        """Identify long-tail keyword phrases"""
        # Extract 3-4 word phrases
        words = content.lower().split()
        long_tail = []
        
        for i in range(len(words) - 2):
            phrase_3 = ' '.join(words[i:i+3])
            phrase_4 = ' '.join(words[i:i+4]) if i < len(words) - 3 else ''
            
            # Simple scoring for meaningful phrases
            if (self._is_meaningful_phrase(phrase_3) and 
                content.lower().count(phrase_3) >= 2):
                long_tail.append(phrase_3)
            
            if (phrase_4 and 
                self._is_meaningful_phrase(phrase_4) and 
                content.lower().count(phrase_4) >= 2):
                long_tail.append(phrase_4)
        
        # Remove duplicates and return top candidates
        return list(set(long_tail))[:10]
    
    def _is_meaningful_phrase(self, phrase: str) -> bool:
        """Check if phrase is meaningful (not just stop words)"""
        words = phrase.split()
        meaningful_words = [w for w in words if w not in self.stop_words]
        return len(meaningful_words) >= 2
    
    def _calculate_keyword_score(self, primary: List[str], secondary: List[str],
                               density: Dict[str, float], 
                               placement: Dict[str, List[str]]) -> float:
        """Calculate overall keyword score"""
        score = 0.0
        
        # Primary keyword score
        primary_score = len(primary) * 10  # Up to 50 points
        score += min(primary_score, 50)
        
        # Secondary keyword score
        secondary_score = len(secondary) * 2  # Up to 20 points
        score += min(secondary_score, 20)
        
        # Density score (optimal 1-3%)
        density_score = 0
        for keyword in primary + secondary:
            keyword_density = density.get(keyword, 0)
            if 1 <= keyword_density <= 3:
                density_score += 5
            elif 0.5 <= keyword_density < 1 or 3 < keyword_density <= 5:
                density_score += 3
        score += min(density_score, 15)
        
        # Placement score
        placement_score = 0
        for keyword in primary:
            keyword_placements = placement.get(keyword, [])
            if 'title' in keyword_placements:
                placement_score += 5
            if 'description' in keyword_placements:
                placement_score += 3
            if 'content_start' in keyword_placements:
                placement_score += 2
        score += min(placement_score, 15)
        
        return min(score, 100.0)


class ReadabilityAnalyzer:
    """Content readability analysis"""
    
    def analyze_readability(self, content: str) -> ReadabilityMetrics:
        """Analyze content readability"""
        metrics = ReadabilityMetrics()
        
        # Basic text statistics
        sentences = self._count_sentences(content)
        words = len(content.split())
        characters = len(content.replace(' ', ''))
        
        if sentences > 0 and words > 0:
            metrics.avg_sentence_length = words / sentences
            metrics.avg_word_length = characters / words
        
        # Complex words analysis
        complex_words = self._count_complex_words(content)
        if words > 0:
            metrics.complex_words_ratio = complex_words / words
        
        # Use textstat if available
        if TEXTSTAT_AVAILABLE:
            try:
                metrics.flesch_score = flesch_reading_ease(content)
                metrics.flesch_grade = flesch_kincaid_grade(content)
            except Exception as e:
                logger.warning(f"Textstat analysis failed: {e}")
        
        # Determine readability level
        metrics.readability_level = self._assess_readability_level(metrics)
        
        # Calculate readability score
        metrics.readability_score = self._calculate_readability_score(metrics)
        
        return metrics
    
    def _count_sentences(self, text: str) -> int:
        """Count sentences in text"""
        sentence_endings = re.findall(r'[.!?]+', text)
        return len(sentence_endings)
    
    def _count_complex_words(self, text: str) -> int:
        """Count complex words (3+ syllables)"""
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        complex_count = 0
        
        for word in words:
            syllables = self._count_syllables(word)
            if syllables >= 3:
                complex_count += 1
        
        return complex_count
    
    def _count_syllables(self, word: str) -> int:
        """Estimate syllable count in a word"""
        vowels = 'aeiouy'
        syllable_count = 0
        previous_was_vowel = False
        
        for char in word.lower():
            if char in vowels:
                if not previous_was_vowel:
                    syllable_count += 1
                previous_was_vowel = True
            else:
                previous_was_vowel = False
        
        # Adjust for silent 'e'
        if word.lower().endswith('e'):
            syllable_count -= 1
        
        # Ensure at least 1 syllable
        return max(1, syllable_count)
    
    def _assess_readability_level(self, metrics: ReadabilityMetrics) -> str:
        """Assess readability level based on metrics"""
        if metrics.flesch_score is not None:
            if metrics.flesch_score >= 90:
                return "very_easy"
            elif metrics.flesch_score >= 80:
                return "easy"
            elif metrics.flesch_score >= 70:
                return "fairly_easy"
            elif metrics.flesch_score >= 60:
                return "standard"
            elif metrics.flesch_score >= 50:
                return "fairly_difficult"
            elif metrics.flesch_score >= 30:
                return "difficult"
            else:
                return "very_difficult"
        
        # Fallback assessment
        if metrics.avg_sentence_length < 15 and metrics.complex_words_ratio < 0.1:
            return "easy"
        elif metrics.avg_sentence_length < 20 and metrics.complex_words_ratio < 0.15:
            return "standard"
        else:
            return "difficult"
    
    def _calculate_readability_score(self, metrics: ReadabilityMetrics) -> float:
        """Calculate readability score (0-100)"""
        score = 100.0
        
        # Sentence length penalty
        if metrics.avg_sentence_length > 20:
            score -= (metrics.avg_sentence_length - 20) * 2
        
        # Complex words penalty
        if metrics.complex_words_ratio > 0.15:
            score -= (metrics.complex_words_ratio - 0.15) * 100
        
        # Use Flesch score if available
        if metrics.flesch_score is not None:
            return max(0, metrics.flesch_score)
        
        return max(0, score)


class SEOQualityAnalyzer:
    """Enterprise SEO quality analysis system"""
    
    def __init__(self):
        self.keyword_analyzer = KeywordAnalyzer()
        self.readability_analyzer = ReadabilityAnalyzer()
    
    def analyze_seo_quality(self, content_data: Dict[str, Any]) -> SEOAnalysisResult:
        """Perform comprehensive SEO analysis"""
        start_time = datetime.now(timezone.utc)
        
        # Extract content elements
        content = content_data.get('content', '')
        title = content_data.get('title', '')
        description = content_data.get('description', '')
        meta_tags = content_data.get('meta_tags', {})
        url = content_data.get('url', '')
        content_id = content_data.get('id', 'unknown')
        
        # Initialize result
        result = SEOAnalysisResult(content_id=content_id, overall_seo_score=0.0, seo_level=SEOLevel.POOR)
        
        try:
            # Keyword analysis
            result.keyword_analysis = self.keyword_analyzer.analyze_keywords(content, title, description)
            result.keyword_score = result.keyword_analysis.keyword_score
            
            # Readability analysis
            result.readability_metrics = self.readability_analyzer.analyze_readability(content)
            result.readability_score = result.readability_metrics.readability_score
            
            # Content quality analysis
            result.content_score = self._analyze_content_quality(content, title, description, result)
            
            # Technical SEO analysis
            result.technical_score = self._analyze_technical_seo(url, meta_tags, result)
            
            # Meta tags analysis
            result.meta_score = self._analyze_meta_tags(title, description, meta_tags, result)
            
            # Structure analysis
            result.structure_score = self._analyze_content_structure(content, result)
            
            # Social media optimization
            result.social_score = self._analyze_social_optimization(content_data, result)
            
            # Calculate overall score
            result.overall_seo_score = self._calculate_overall_seo_score(result)
            
            # Determine SEO level
            result.seo_level = self._assess_seo_level(result.overall_seo_score)
            
            # Generate recommendations
            result.recommendations = self._generate_seo_recommendations(result)
            
        except Exception as e:
            logger.error(f"SEO analysis error: {e}")
            result.add_issue(SEOIssue(
                category=SEOMetricType.TECHNICAL_SEO,
                severity='critical',
                message=f"SEO analysis failed: {str(e)}",
                impact_score=10.0
            ))
        
        # Finalize result
        end_time = datetime.now(timezone.utc)
        result.processing_time_ms = (end_time - start_time).total_seconds() * 1000
        
        return result
    
    def _analyze_content_quality(self, content: str, title: str, description: str,
                               result: SEOAnalysisResult) -> float:
        """Analyze content quality for SEO"""
        score = 100.0
        
        # Content length analysis
        word_count = len(content.split())
        if word_count < 300:
            result.add_issue(SEOIssue(
                category=SEOMetricType.CONTENT_QUALITY,
                severity='warning',
                message=f"Content too short: {word_count} words (recommended: 300+ words)",
                field='content',
                current_value=word_count,
                recommended_value=300,
                suggestions=['Expand content with more detailed information'],
                impact_score=7.0
            ))
            score -= 20
        elif word_count > 3000:
            result.add_issue(SEOIssue(
                category=SEOMetricType.CONTENT_QUALITY,
                severity='info',
                message=f"Very long content: {word_count} words (consider breaking into sections)",
                field='content',
                current_value=word_count,
                suggestions=['Consider breaking long content into sections or multiple pages'],
                impact_score=2.0
            ))
        
        # Content uniqueness (basic check)
        if self._has_duplicate_content(content):
            result.add_issue(SEOIssue(
                category=SEOMetricType.CONTENT_QUALITY,
                severity='error',
                message="Potential duplicate content detected",
                field='content',
                suggestions=['Ensure content is unique and original'],
                impact_score=8.0
            ))
            score -= 30
        
        # Content freshness indicators
        if not self._has_current_information(content):
            result.add_issue(SEOIssue(
                category=SEOMetricType.CONTENT_QUALITY,
                severity='warning',
                message="Content may lack current/timely information",
                field='content',
                suggestions=['Include current dates, recent examples, or timely information'],
                impact_score=4.0
            ))
            score -= 10
        
        return max(0, score)
    
    def _analyze_technical_seo(self, url: str, meta_tags: Dict[str, Any],
                              result: SEOAnalysisResult) -> float:
        """Analyze technical SEO factors"""
        score = 100.0
        
        # URL analysis
        if url:
            parsed_url = urlparse(url)
            
            # URL length
            if len(url) > 100:
                result.add_issue(SEOIssue(
                    category=SEOMetricType.TECHNICAL_SEO,
                    severity='warning',
                    message=f"URL too long: {len(url)} characters (recommended: <100)",
                    field='url',
                    current_value=len(url),
                    recommended_value=100,
                    suggestions=['Shorten URL for better SEO'],
                    impact_score=5.0
                ))
                score -= 15
            
            # URL structure
            if not self._has_seo_friendly_url(parsed_url.path):
                result.add_issue(SEOIssue(
                    category=SEOMetricType.TECHNICAL_SEO,
                    severity='warning',
                    message="URL not SEO-friendly (use hyphens, lowercase, descriptive)",
                    field='url',
                    current_value=parsed_url.path,
                    suggestions=['Use lowercase letters, hyphens, and descriptive words in URL'],
                    impact_score=6.0
                ))
                score -= 20
        
        # HTTPS check (if URL provided)
        if url and not url.startswith('https://'):
            result.add_issue(SEOIssue(
                category=SEOMetricType.TECHNICAL_SEO,
                severity='error',
                message="URL should use HTTPS for security and SEO",
                field='url',
                suggestions=['Implement HTTPS for better security and SEO ranking'],
                impact_score=8.0
            ))
            score -= 25
        
        return max(0, score)
    
    def _analyze_meta_tags(self, title: str, description: str, meta_tags: Dict[str, Any],
                          result: SEOAnalysisResult) -> float:
        """Analyze meta tags for SEO"""
        score = 100.0
        
        # Title analysis
        if not title:
            result.add_issue(SEOIssue(
                category=SEOMetricType.META_TAGS,
                severity='critical',
                message="Missing title tag",
                field='title',
                suggestions=['Add a descriptive title tag'],
                impact_score=10.0
            ))
            score -= 40
        else:
            # Title length
            if len(title) < 30:
                result.add_issue(SEOIssue(
                    category=SEOMetricType.META_TAGS,
                    severity='warning',
                    message=f"Title too short: {len(title)} characters (recommended: 30-60)",
                    field='title',
                    current_value=len(title),
                    recommended_value='30-60 characters',
                    suggestions=['Expand title with more descriptive keywords'],
                    impact_score=6.0
                ))
                score -= 15
            elif len(title) > 60:
                result.add_issue(SEOIssue(
                    category=SEOMetricType.META_TAGS,
                    severity='warning',
                    message=f"Title too long: {len(title)} characters (recommended: 30-60)",
                    field='title',
                    current_value=len(title),
                    recommended_value='30-60 characters',
                    suggestions=['Shorten title to prevent truncation in search results'],
                    impact_score=7.0
                ))
                score -= 20
        
        # Description analysis
        if not description:
            result.add_issue(SEOIssue(
                category=SEOMetricType.META_TAGS,
                severity='error',
                message="Missing meta description",
                field='description',
                suggestions=['Add a compelling meta description'],
                impact_score=8.0
            ))
            score -= 30
        else:
            # Description length
            if len(description) < 120:
                result.add_issue(SEOIssue(
                    category=SEOMetricType.META_TAGS,
                    severity='warning',
                    message=f"Description too short: {len(description)} characters (recommended: 120-160)",
                    field='description',
                    current_value=len(description),
                    recommended_value='120-160 characters',
                    suggestions=['Expand description with more compelling details'],
                    impact_score=5.0
                ))
                score -= 10
            elif len(description) > 160:
                result.add_issue(SEOIssue(
                    category=SEOMetricType.META_TAGS,
                    severity='warning',
                    message=f"Description too long: {len(description)} characters (recommended: 120-160)",
                    field='description',
                    current_value=len(description),
                    recommended_value='120-160 characters',
                    suggestions=['Shorten description to prevent truncation'],
                    impact_score=6.0
                ))
                score -= 15
        
        return max(0, score)
    
    def _analyze_content_structure(self, content: str, result: SEOAnalysisResult) -> float:
        """Analyze content structure for SEO"""
        score = 100.0
        
        # Heading structure analysis
        headings = self._extract_headings(content)
        
        if not headings.get('h1'):
            result.add_issue(SEOIssue(
                category=SEOMetricType.STRUCTURE,
                severity='error',
                message="Missing H1 heading",
                field='content_structure',
                suggestions=['Add one H1 heading for the main topic'],
                impact_score=8.0
            ))
            score -= 25
        elif len(headings.get('h1', [])) > 1:
            result.add_issue(SEOIssue(
                category=SEOMetricType.STRUCTURE,
                severity='warning',
                message=f"Multiple H1 headings found: {len(headings['h1'])}",
                field='content_structure',
                suggestions=['Use only one H1 heading per page'],
                impact_score=5.0
            ))
            score -= 15
        
        # Subheading structure
        if not headings.get('h2') and len(content.split()) > 300:
            result.add_issue(SEOIssue(
                category=SEOMetricType.STRUCTURE,
                severity='warning',
                message="No H2 subheadings found in long content",
                field='content_structure',
                suggestions=['Add H2 subheadings to improve content structure'],
                impact_score=6.0
            ))
            score -= 20
        
        # Paragraph structure
        paragraphs = content.split('\n\n')
        long_paragraphs = [p for p in paragraphs if len(p.split()) > 100]
        if len(long_paragraphs) > len(paragraphs) * 0.5:
            result.add_issue(SEOIssue(
                category=SEOMetricType.STRUCTURE,
                severity='warning',
                message="Many paragraphs are too long (>100 words)",
                field='content_structure',
                suggestions=['Break long paragraphs into shorter, more readable sections'],
                impact_score=4.0
            ))
            score -= 10
        
        return max(0, score)
    
    def _analyze_social_optimization(self, content_data: Dict[str, Any],
                                   result: SEOAnalysisResult) -> float:
        """Analyze social media optimization"""
        score = 100.0
        
        meta_tags = content_data.get('meta_tags', {})
        
        # Open Graph tags
        if not meta_tags.get('og:title'):
            result.add_issue(SEOIssue(
                category=SEOMetricType.SOCIAL_MEDIA,
                severity='warning',
                message="Missing Open Graph title",
                field='og:title',
                suggestions=['Add Open Graph title for better social sharing'],
                impact_score=4.0
            ))
            score -= 15
        
        if not meta_tags.get('og:description'):
            result.add_issue(SEOIssue(
                category=SEOMetricType.SOCIAL_MEDIA,
                severity='warning',
                message="Missing Open Graph description",
                field='og:description',
                suggestions=['Add Open Graph description for social sharing'],
                impact_score=4.0
            ))
            score -= 15
        
        if not meta_tags.get('og:image'):
            result.add_issue(SEOIssue(
                category=SEOMetricType.SOCIAL_MEDIA,
                severity='info',
                message="Missing Open Graph image",
                field='og:image',
                suggestions=['Add attractive image for social media previews'],
                impact_score=3.0
            ))
            score -= 10
        
        # Twitter Card tags
        if not meta_tags.get('twitter:card'):
            result.add_issue(SEOIssue(
                category=SEOMetricType.SOCIAL_MEDIA,
                severity='info',
                message="Missing Twitter Card tags",
                field='twitter:card',
                suggestions=['Add Twitter Card tags for better Twitter sharing'],
                impact_score=2.0
            ))
            score -= 10
        
        return max(0, score)
    
    def _has_duplicate_content(self, content: str) -> bool:
        """Basic check for potential duplicate content"""
        # Simple heuristic: check for repeated sentences
        sentences = content.split('.')
        unique_sentences = set(sentence.strip().lower() for sentence in sentences if sentence.strip())
        
        # If less than 80% of sentences are unique, flag as potential duplicate
        if len(sentences) > 5 and len(unique_sentences) / len(sentences) < 0.8:
            return True
        
        return False
    
    def _has_current_information(self, content: str) -> bool:
        """Check if content has current/timely information"""
        current_year = datetime.now().year
        
        # Look for current year or recent years
        year_pattern = r'\b(20\d{2})\b'
        years = re.findall(year_pattern, content)
        
        if years:
            recent_years = [int(year) for year in years if int(year) >= current_year - 2]
            return len(recent_years) > 0
        
        # Look for time-sensitive words
        current_words = ['today', 'currently', 'now', 'recent', 'latest', 'new']
        return any(word in content.lower() for word in current_words)
    
    def _has_seo_friendly_url(self, path: str) -> bool:
        """Check if URL path is SEO-friendly"""
        if not path or path == '/':
            return True
        
        # Check for SEO-friendly patterns
        seo_pattern = r'^/[a-z0-9\-/]+$'
        return bool(re.match(seo_pattern, path))
    
    def _extract_headings(self, content: str) -> Dict[str, List[str]]:
        """Extract headings from content"""
        headings = {'h1': [], 'h2': [], 'h3': [], 'h4': [], 'h5': [], 'h6': []}
        
        # HTML headings
        for level in range(1, 7):
            pattern = rf'<h{level}[^>]*>(.*?)</h{level}>'
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            headings[f'h{level}'].extend(matches)
        
        # Markdown headings
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                if 1 <= level <= 6:
                    heading_text = line.lstrip('#').strip()
                    headings[f'h{level}'].append(heading_text)
        
        return headings
    
    def _calculate_overall_seo_score(self, result: SEOAnalysisResult) -> float:
        """Calculate overall SEO score"""
        weights = {
            'content': 0.25,
            'keyword': 0.20,
            'meta': 0.20,
            'technical': 0.15,
            'readability': 0.10,
            'structure': 0.05,
            'social': 0.05
        }
        
        weighted_score = (
            result.content_score * weights['content'] +
            result.keyword_score * weights['keyword'] +
            result.meta_score * weights['meta'] +
            result.technical_score * weights['technical'] +
            result.readability_score * weights['readability'] +
            result.structure_score * weights['structure'] +
            result.social_score * weights['social']
        )
        
        return min(100.0, max(0.0, weighted_score))
    
    def _assess_seo_level(self, score: float) -> SEOLevel:
        """Assess SEO level based on score"""
        if score >= 90:
            return SEOLevel.EXCELLENT
        elif score >= 75:
            return SEOLevel.GOOD
        elif score >= 60:
            return SEOLevel.FAIR
        elif score >= 40:
            return SEOLevel.POOR
        else:
            return SEOLevel.CRITICAL
    
    def _generate_seo_recommendations(self, result: SEOAnalysisResult) -> List[str]:
        """Generate SEO improvement recommendations"""
        recommendations = []
        
        # Score-based recommendations
        if result.overall_seo_score < 40:
            recommendations.append("SEO score is critical - comprehensive optimization needed")
        elif result.overall_seo_score < 60:
            recommendations.append("SEO needs significant improvement - focus on key issues")
        elif result.overall_seo_score < 75:
            recommendations.append("Good SEO foundation - optimize remaining issues")
        else:
            recommendations.append("Excellent SEO optimization - maintain current standards")
        
        # Component-specific recommendations
        if result.keyword_score < 60:
            recommendations.append("Improve keyword optimization and density")
        
        if result.meta_score < 70:
            recommendations.append("Optimize title tags and meta descriptions")
        
        if result.readability_score < 60:
            recommendations.append("Improve content readability and structure")
        
        if result.technical_score < 70:
            recommendations.append("Address technical SEO issues")
        
        # Critical issue recommendations
        critical_issues = result.get_critical_issues()
        if critical_issues:
            recommendations.append("Address all critical SEO issues immediately")
        
        return recommendations
