"""SEO Enhancement Engine - Advanced Search Engine Optimization
==========================================================

Professional SEO enhancement engine for content creators providing:
- Content SEO Analysis & Optimization
- Keyword Research & Density Optimization
- Meta Tags Generation & Optimization
- Schema Markup Generation
- Content Structure Analysis
- Readability & User Experience Optimization
- Technical SEO Recommendations
- Social Media Optimization (SMO)
- Local SEO Enhancement
- Performance & Core Web Vitals Optimization

Created by: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use strictly prohibited
"""import re
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
import logging
from dataclasses import dataclass
from collections import Counter, defaultdict
import requests
from urllib.parse import urlparse, urljoin
import json
from textstat import flesch_reading_ease, flesch_kincaid_grade
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class SEOAnalysis:
    """SEO analysis result"""    seo_score: float
    keyword_density: Dict[str, float]
    meta_analysis: Dict[str, Any]
    content_structure: Dict[str, Any]
    recommendations: List[str]
    technical_issues: List[str]

@dataclass
class KeywordAnalysis:
    """Keyword analysis result"""    keyword: str
    density: float
    frequency: int
    relevance_score: float
    competition_level: str
    search_volume: Optional[int] = None

@dataclass
class ContentOptimization:
    """Content optimization recommendations"""    optimized_title: str
    optimized_description: str
    optimized_content: str
    meta_tags: Dict[str, str]
    schema_markup: Dict[str, Any]
    improvements: List[str]

class SEOEnhancementEngine:
    """    Industrial-grade SEO enhancement engine for content creators
    """    
    def __init__(self, language: str = 'en'):
        self.language = language
        
        # Initialize SEO components
        self._initialize_seo_components()
        
        # Initialize keyword databases
        self._initialize_keyword_databases()
        
        # Initialize optimization rules
        self._initialize_optimization_rules()
        
        logger.info("SEOEnhancementEngine initialized successfully")
    
    def _initialize_seo_components(self) -> None:
        """Initialize SEO analysis components"""        try:
            # SEO scoring weights
            self.seo_weights = {
                'title_optimization': 0.20,
                'meta_description': 0.15,
                'heading_structure': 0.15,
                'keyword_density': 0.15,
                'content_quality': 0.10,
                'readability': 0.10,
                'internal_linking': 0.05,
                'image_optimization': 0.05,
                'technical_seo': 0.05
            }
            
            # Content length recommendations
            self.content_length_targets = {
                'blog_post': {'min': 1000, 'optimal': 2000, 'max': 4000},
                'product_description': {'min': 150, 'optimal': 300, 'max': 500},
                'social_media': {'min': 50, 'optimal': 120, 'max': 280},
                'meta_description': {'min': 120, 'optimal': 155, 'max': 160}
            }
            
            # Keyword density targets
            self.keyword_density_targets = {
                'primary_keyword': {'min': 0.5, 'optimal': 2.0, 'max': 3.0},
                'secondary_keyword': {'min': 0.2, 'optimal': 1.0, 'max': 2.0},
                'long_tail_keyword': {'min': 0.1, 'optimal': 0.5, 'max': 1.0}
            }
            
        except Exception as e:
            logger.error(f"Failed to initialize SEO components: {e}")
            raise
    
    def _initialize_keyword_databases(self) -> None:
        """Initialize keyword research databases"""        try:
            # Stop words for different languages
            try:
                nltk.download('stopwords', quiet=True)
                self.stop_words = set(stopwords.words('english'))
            except:
                self.stop_words = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'])
            
            # Common SEO keywords and phrases
            self.seo_keywords = {
                'music': ['music', 'song', 'album', 'artist', 'band', 'concert', 'audio', 'sound', 'melody', 'rhythm'],
                'video': ['video', 'film', 'movie', 'clip', 'visual', 'cinematic', 'production', 'streaming'],
                'content': ['content', 'creator', 'influencer', 'social media', 'digital', 'online', 'platform'],
                'business': ['business', 'marketing', 'brand', 'strategy', 'growth', 'revenue', 'monetization']
            }
            
            # High-value keyword patterns
            self.high_value_patterns = [
                r'\b\w+\s+(tutorial|guide|how\s+to|tips|best\s+practices)\b',
                r'\b(free|premium|professional|advanced)\s+\w+\b',
                r'\b\w+\s+(2024|2025|latest|new|updated)\b',
                r'\b(top|best|ultimate|complete)\s+\w+\b'
            ]
            
        except Exception as e:
            logger.error(f"Failed to initialize keyword databases: {e}")
            raise
    
    def _initialize_optimization_rules(self) -> None:
        """Initialize SEO optimization rules"""        try:
            # Title optimization rules
            self.title_rules = {
                'min_length': 30,
                'max_length': 60,
                'include_primary_keyword': True,
                'avoid_keyword_stuffing': True,
                'use_power_words': True,
                'include_numbers': True
            }
            
            # Meta description rules
            self.meta_description_rules = {
                'min_length': 120,
                'max_length': 155,
                'include_call_to_action': True,
                'include_primary_keyword': True,
                'unique_for_each_page': True
            }
            
            # Content structure rules
            self.content_structure_rules = {
                'use_h1_tag': True,
                'hierarchical_headings': True,
                'short_paragraphs': True,
                'bullet_points': True,
                'internal_links': True,
                'external_authority_links': True
            }
            
        except Exception as e:
            logger.error(f"Failed to initialize optimization rules: {e}")
            raise
    
    def enhance(self, content_data: Union[str, Dict[str, Any]], 
                config: Dict[str, Any]) -> Dict[str, Any]:
        """        Comprehensive SEO enhancement pipeline
        
        Args:
            content_data: Content text or structured content data
            config: SEO enhancement configuration
            
        Returns:
            SEO enhancement results and recommendations
        """        try:
            # Extract content information
            content_info = self._extract_content_info(content_data)
            
            # Perform SEO analysis
            seo_analysis = self._analyze_seo(content_info, config)
            
            # Keyword research and analysis
            keyword_analysis = self._perform_keyword_analysis(content_info, config)
            
            # Content optimization
            content_optimization = self._optimize_content(content_info, keyword_analysis, config)
            
            # Technical SEO analysis
            technical_seo = self._analyze_technical_seo(content_info, config)
            
            # Generate schema markup
            schema_markup = self._generate_schema_markup(content_info, config)
            
            # Performance analysis
            performance_analysis = self._analyze_performance_seo(content_info, config)
            
            # Generate comprehensive recommendations
            recommendations = self._generate_seo_recommendations(
                seo_analysis, keyword_analysis, content_optimization, technical_seo, config
            )
            
            return {
                'seo_analysis': seo_analysis,
                'keyword_analysis': keyword_analysis,
                'content_optimization': content_optimization,
                'technical_seo': technical_seo,
                'schema_markup': schema_markup,
                'performance_analysis': performance_analysis,
                'recommendations': recommendations,
                'enhancement_config': config
            }
            
        except Exception as e:
            logger.error(f"SEO enhancement failed: {e}")
            raise
    
    def _extract_content_info(self, content_data: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Extract content information for SEO analysis"""        try:
            if isinstance(content_data, str):
                # Simple text content
                content_info = {
                    'title': '',
                    'content': content_data,
                    'meta_description': '',
                    'headings': [],
                    'images': [],
                    'links': [],
                    'content_type': 'text'
                }
                
                # Try to extract title from content
                sentences = sent_tokenize(content_data)
                if sentences:
                    # Use first sentence as potential title
                    first_sentence = sentences[0]
                    if len(first_sentence) < 100:
                        content_info['title'] = first_sentence
                
            else:
                # Structured content data
                content_info = {
                    'title': content_data.get('title', ''),
                    'content': content_data.get('content', ''),
                    'meta_description': content_data.get('meta_description', ''),
                    'headings': content_data.get('headings', []),
                    'images': content_data.get('images', []),
                    'links': content_data.get('links', []),
                    'content_type': content_data.get('content_type', 'text'),
                    'url': content_data.get('url', ''),
                    'author': content_data.get('author', ''),
                    'category': content_data.get('category', ''),
                    'tags': content_data.get('tags', [])
                }
            
            # Extract additional content metrics
            content_info['word_count'] = len(content_info['content'].split())
            content_info['sentence_count'] = len(sent_tokenize(content_info['content']))
            content_info['paragraph_count'] = len(content_info['content'].split('\n\n'))
            
            return content_info
            
        except Exception as e:
            logger.error(f"Content info extraction failed: {e}")
            return {}
    
    def _analyze_seo(self, content_info: Dict[str, Any], config: Dict[str, Any]) -> SEOAnalysis:
        """Perform comprehensive SEO analysis"""        try:
            # Title analysis
            title_score = self._analyze_title_seo(content_info['title'])
            
            # Meta description analysis
            meta_score = self._analyze_meta_description_seo(content_info['meta_description'])
            
            # Content structure analysis
            structure_score = self._analyze_content_structure_seo(content_info)
            
            # Keyword density analysis
            keyword_density = self._analyze_keyword_density(content_info['content'], config)
            
            # Content quality analysis
            quality_score = self._analyze_content_quality_seo(content_info)
            
            # Readability analysis
            readability_score = self._analyze_readability_seo(content_info['content'])
            
            # Calculate overall SEO score
            seo_score = (
                title_score * self.seo_weights['title_optimization'] +
                meta_score * self.seo_weights['meta_description'] +
                structure_score * self.seo_weights['heading_structure'] +
                quality_score * self.seo_weights['content_quality'] +
                readability_score * self.seo_weights['readability']
            )
            
            # Generate recommendations
            recommendations = self._generate_seo_analysis_recommendations(
                title_score, meta_score, structure_score, quality_score, readability_score
            )
            
            # Identify technical issues
            technical_issues = self._identify_technical_issues(content_info)
            
            # Meta analysis
            meta_analysis = {
                'title_score': title_score,
                'meta_description_score': meta_score,
                'content_structure_score': structure_score,
                'content_quality_score': quality_score,
                'readability_score': readability_score
            }
            
            # Content structure analysis
            content_structure = {
                'heading_hierarchy': self._analyze_heading_hierarchy(content_info.get('headings', [])),
                'paragraph_structure': self._analyze_paragraph_structure(content_info['content']),
                'link_structure': self._analyze_link_structure(content_info.get('links', []))
            }
            
            return SEOAnalysis(
                seo_score=seo_score,
                keyword_density=keyword_density,
                meta_analysis=meta_analysis,
                content_structure=content_structure,
                recommendations=recommendations,
                technical_issues=technical_issues
            )
            
        except Exception as e:
            logger.error(f"SEO analysis failed: {e}")
            return SEOAnalysis(0.0, {}, {}, {}, [], [])
    
    def _analyze_title_seo(self, title: str) -> float:
        """Analyze title SEO optimization"""        try:
            if not title:
                return 0.0
            
            score = 0.0
            
            # Length check
            title_length = len(title)
            if self.title_rules['min_length'] <= title_length <= self.title_rules['max_length']:
                score += 0.3
            elif title_length < self.title_rules['min_length']:
                score += 0.1
            
            # Check for power words
            power_words = ['ultimate', 'complete', 'essential', 'professional', 'advanced', 'best', 'top', 'guide']
            if any(word in title.lower() for word in power_words):
                score += 0.2
            
            # Check for numbers
            if re.search(r'\d+', title):
                score += 0.1
            
            # Check for emotional appeal
            emotional_words = ['amazing', 'incredible', 'stunning', 'breakthrough', 'revolutionary']
            if any(word in title.lower() for word in emotional_words):
                score += 0.1
            
            # Check for keyword stuffing
            words = title.lower().split()
            word_counts = Counter(words)
            max_word_count = max(word_counts.values()) if word_counts else 0
            if max_word_count <= 2:
                score += 0.2
            
            # Check capitalization
            if title.istitle() or title.isupper():
                score += 0.1
            
            return min(1.0, score)
            
        except Exception as e:
            logger.error(f"Title SEO analysis failed: {e}")
            return 0.0
    
    def _analyze_meta_description_seo(self, meta_description: str) -> float:
        """Analyze meta description SEO optimization"""        try:
            if not meta_description:
                return 0.0
            
            score = 0.0
            
            # Length check
            desc_length = len(meta_description)
            if self.meta_description_rules['min_length'] <= desc_length <= self.meta_description_rules['max_length']:
                score += 0.4
            elif desc_length < self.meta_description_rules['min_length']:
                score += 0.2
            
            # Check for call-to-action
            cta_phrases = ['learn more', 'discover', 'find out', 'get started', 'download', 'try now', 'click here']
            if any(phrase in meta_description.lower() for phrase in cta_phrases):
                score += 0.3
            
            # Check for unique selling proposition
            usp_words = ['unique', 'exclusive', 'premium', 'professional', 'expert', 'guaranteed']
            if any(word in meta_description.lower() for word in usp_words):
                score += 0.2
            
            # Check for proper sentence structure
            if meta_description.endswith('.') or meta_description.endswith('!'):
                score += 0.1
            
            return min(1.0, score)
            
        except Exception as e:
            logger.error(f"Meta description SEO analysis failed: {e}")
            return 0.0
    
    def _analyze_content_structure_seo(self, content_info: Dict[str, Any]) -> float:
        """Analyze content structure for SEO"""        try:
            score = 0.0
            
            # Check heading structure
            headings = content_info.get('headings', [])
            if headings:
                score += 0.3
                
                # Check for H1 tag
                h1_count = sum(1 for h in headings if h.get('level') == 1)
                if h1_count == 1:
                    score += 0.2
                elif h1_count == 0:
                    score += 0.0
                else:
                    score += 0.1  # Multiple H1s are not ideal
            
            # Check paragraph length
            content = content_info['content']
            paragraphs = content.split('\n\n')
            avg_paragraph_length = np.mean([len(p.split()) for p in paragraphs if p.strip()])
            
            if 50 <= avg_paragraph_length <= 150:
                score += 0.2
            elif avg_paragraph_length < 50:
                score += 0.1
            
            # Check for bullet points or numbered lists
            if re.search(r'(\n\s*[\-\*\+]\s+|\n\s*\d+\.\s+)', content):
                score += 0.1
            
            # Check for internal links
            links = content_info.get('links', [])
            internal_links = [link for link in links if not self._is_external_link(link)]
            if internal_links:
                score += 0.1
            
            # Check for images with alt text
            images = content_info.get('images', [])
            images_with_alt = [img for img in images if img.get('alt_text')]
            if images and len(images_with_alt) / len(images) > 0.8:
                score += 0.1
            
            return min(1.0, score)
            
        except Exception as e:
            logger.error(f"Content structure SEO analysis failed: {e}")
            return 0.0
    
    def _analyze_keyword_density(self, content: str, config: Dict[str, Any]) -> Dict[str, float]:
        """Analyze keyword density"""        try:
            # Tokenize content
            words = word_tokenize(content.lower())
            words = [word for word in words if word.isalpha() and word not in self.stop_words]
            
            total_words = len(words)
            if total_words == 0:
                return {}
            
            # Count word frequencies
            word_counts = Counter(words)
            
            # Calculate density for each word
            keyword_density = {}
            for word, count in word_counts.most_common(20):  # Top 20 words
                density = (count / total_words) * 100
                keyword_density[word] = density
            
            # Extract n-grams
            bigrams = [' '.join(words[i:i+2]) for i in range(len(words)-1)]
            trigrams = [' '.join(words[i:i+3]) for i in range(len(words)-2)]
            
            # Analyze bigram density
            bigram_counts = Counter(bigrams)
            for bigram, count in bigram_counts.most_common(10):
                density = (count / (total_words - 1)) * 100
                keyword_density[bigram] = density
            
            # Analyze trigram density
            trigram_counts = Counter(trigrams)
            for trigram, count in trigram_counts.most_common(5):
                density = (count / (total_words - 2)) * 100
                keyword_density[trigram] = density
            
            return keyword_density
            
        except Exception as e:
            logger.error(f"Keyword density analysis failed: {e}")
            return {}
    
    def _analyze_content_quality_seo(self, content_info: Dict[str, Any]) -> float:
        """Analyze content quality for SEO"""        try:
            score = 0.0
            content = content_info['content']
            
            # Word count check
            word_count = content_info['word_count']
            if word_count >= 1000:
                score += 0.4
            elif word_count >= 500:
                score += 0.3
            elif word_count >= 300:
                score += 0.2
            else:
                score += 0.1
            
            # Content uniqueness (simplified check)
            unique_words = len(set(word_tokenize(content.lower())))
            total_words = len(word_tokenize(content))
            uniqueness_ratio = unique_words / total_words if total_words > 0 else 0
            
            if uniqueness_ratio > 0.6:
                score += 0.2
            elif uniqueness_ratio > 0.4:
                score += 0.1
            
            # Content depth (check for detailed explanations)
            sentences = sent_tokenize(content)
            avg_sentence_length = np.mean([len(word_tokenize(sent)) for sent in sentences])
            
            if 15 <= avg_sentence_length <= 25:
                score += 0.2
            elif 10 <= avg_sentence_length <= 30:
                score += 0.1
            
            # Check for multimedia content
            if content_info.get('images'):
                score += 0.1
            
            # Check for external references
            if 'http' in content or 'www.' in content:
                score += 0.1
            
            return min(1.0, score)
            
        except Exception as e:
            logger.error(f"Content quality SEO analysis failed: {e}")
            return 0.0
    
    def _analyze_readability_seo(self, content: str) -> float:
        """Analyze content readability for SEO"""        try:
            if not content:
                return 0.0
            
            score = 0.0
            
            # Flesch Reading Ease
            try:
                reading_ease = flesch_reading_ease(content)
                if reading_ease >= 60:  # Easy to read
                    score += 0.4
                elif reading_ease >= 30:  # Fairly difficult
                    score += 0.3
                else:  # Difficult
                    score += 0.1
            except:
                score += 0.2  # Default score if calculation fails
            
            # Flesch-Kincaid Grade Level
            try:
                grade_level = flesch_kincaid_grade(content)
                if grade_level <= 8:  # 8th grade or below
                    score += 0.3
                elif grade_level <= 12:  # High school level
                    score += 0.2
                else:  # College level
                    score += 0.1
            except:
                score += 0.15  # Default score if calculation fails
            
            # Sentence length analysis
            sentences = sent_tokenize(content)
            if sentences:
                avg_sentence_length = np.mean([len(word_tokenize(sent)) for sent in sentences])
                if avg_sentence_length <= 20:
                    score += 0.2
                elif avg_sentence_length <= 30:
                    score += 0.1
            
            # Transition words
            transition_words = ['however', 'therefore', 'moreover', 'furthermore', 'additionally', 'consequently']
            transition_count = sum(1 for word in transition_words if word in content.lower())
            if transition_count > 0:
                score += 0.1
            
            return min(1.0, score)
            
        except Exception as e:
            logger.error(f"Readability SEO analysis failed: {e}")
            return 0.0
    
    def _perform_keyword_analysis(self, content_info: Dict[str, Any], config: Dict[str, Any]) -> List[KeywordAnalysis]:
        """Perform comprehensive keyword analysis"""        try:
            keyword_analyses = []
            content = content_info['content']
            
            # Extract potential keywords
            keywords = self._extract_keywords(content, config)
            
            for keyword in keywords:
                # Calculate keyword metrics
                density = self._calculate_keyword_density(keyword, content)
                frequency = self._calculate_keyword_frequency(keyword, content)
                relevance = self._calculate_keyword_relevance(keyword, content_info, config)
                competition = self._estimate_keyword_competition(keyword)
                
                keyword_analysis = KeywordAnalysis(
                    keyword=keyword,
                    density=density,
                    frequency=frequency,
                    relevance_score=relevance,
                    competition_level=competition
                )
                
                keyword_analyses.append(keyword_analysis)
            
            # Sort by relevance score
            keyword_analyses.sort(key=lambda x: x.relevance_score, reverse=True)
            
            return keyword_analyses[:20]  # Top 20 keywords
            
        except Exception as e:
            logger.error(f"Keyword analysis failed: {e}")
            return []
    
    def _extract_keywords(self, content: str, config: Dict[str, Any]) -> List[str]:
        """Extract potential keywords from content"""        try:
            keywords = []
            
            # Single words
            words = word_tokenize(content.lower())
            words = [word for word in words if word.isalpha() and len(word) > 3 and word not in self.stop_words]
            
            # Get most frequent words
            word_counts = Counter(words)
            frequent_words = [word for word, count in word_counts.most_common(50) if count > 1]
            keywords.extend(frequent_words)
            
            # Bigrams
            bigrams = [' '.join(words[i:i+2]) for i in range(len(words)-1)]
            bigram_counts = Counter(bigrams)
            frequent_bigrams = [bigram for bigram, count in bigram_counts.most_common(20) if count > 1]
            keywords.extend(frequent_bigrams)
            
            # Trigrams
            trigrams = [' '.join(words[i:i+3]) for i in range(len(words)-2)]
            trigram_counts = Counter(trigrams)
            frequent_trigrams = [trigram for trigram, count in trigram_counts.most_common(10) if count > 1]
            keywords.extend(frequent_trigrams)
            
            # Extract high-value patterns
            for pattern in self.high_value_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                keywords.extend([match.lower() for match in matches])
            
            # Remove duplicates
            keywords = list(set(keywords))
            
            return keywords
            
        except Exception as e:
            logger.error(f"Keyword extraction failed: {e}")
            return []
    
    def _calculate_keyword_density(self, keyword: str, content: str) -> float:
        """Calculate keyword density"""        try:
            content_lower = content.lower()
            keyword_lower = keyword.lower()
            
            # Count occurrences
            keyword_count = content_lower.count(keyword_lower)
            
            # Count total words
            total_words = len(word_tokenize(content))
            
            if total_words == 0:
                return 0.0
            
            # Calculate density as percentage
            density = (keyword_count / total_words) * 100
            
            return density
            
        except Exception as e:
            logger.error(f"Keyword density calculation failed: {e}")
            return 0.0
    
    def _calculate_keyword_frequency(self, keyword: str, content: str) -> int:
        """Calculate keyword frequency"""        try:
            content_lower = content.lower()
            keyword_lower = keyword.lower()
            
            return content_lower.count(keyword_lower)
            
        except Exception as e:
            logger.error(f"Keyword frequency calculation failed: {e}")
            return 0
    
    def _calculate_keyword_relevance(self, keyword: str, content_info: Dict[str, Any], config: Dict[str, Any]) -> float:
        """Calculate keyword relevance score"""        try:
            relevance_score = 0.0
            
            # Check if keyword appears in title
            title = content_info.get('title', '').lower()
            if keyword.lower() in title:
                relevance_score += 0.3
            
            # Check if keyword appears in headings
            headings = content_info.get('headings', [])
            for heading in headings:
                if keyword.lower() in heading.get('text', '').lower():
                    relevance_score += 0.2
                    break
            
            # Check keyword density (optimal range)
            density = self._calculate_keyword_density(keyword, content_info['content'])
            if 0.5 <= density <= 3.0:
                relevance_score += 0.3
            elif density > 0:
                relevance_score += 0.1
            
            # Check if keyword is category-relevant
            content_type = content_info.get('content_type', '')
            category = content_info.get('category', '')
            
            for category_name, category_keywords in self.seo_keywords.items():
                if keyword in category_keywords:
                    if category_name in content_type.lower() or category_name in category.lower():
                        relevance_score += 0.2
                    else:
                        relevance_score += 0.1
            
            return min(1.0, relevance_score)
            
        except Exception as e:
            logger.error(f"Keyword relevance calculation failed: {e}")
            return 0.0
    
    def _estimate_keyword_competition(self, keyword: str) -> str:
        """Estimate keyword competition level"""        try:
            # Simple heuristics for competition estimation
            keyword_length = len(keyword.split())
            
            # Long-tail keywords typically have lower competition
            if keyword_length >= 3:
                return 'low'
            elif keyword_length == 2:
                return 'medium'
            else:
                # Single words typically have higher competition
                if keyword in self.stop_words:
                    return 'very_high'
                
                # Check if it's a common SEO keyword
                for category_keywords in self.seo_keywords.values():
                    if keyword in category_keywords:
                        return 'high'
                
                return 'medium'
                
        except Exception as e:
            logger.error(f"Keyword competition estimation failed: {e}")
            return 'unknown'
    
    def _optimize_content(self, content_info: Dict[str, Any], 
                         keyword_analysis: List[KeywordAnalysis], 
                         config: Dict[str, Any]) -> ContentOptimization:
        """Optimize content for SEO"""        try:
            # Get primary keywords
            primary_keywords = [kw.keyword for kw in keyword_analysis[:3] if kw.relevance_score > 0.5]
            
            # Optimize title
            optimized_title = self._optimize_title(content_info['title'], primary_keywords)
            
            # Optimize meta description
            optimized_description = self._optimize_meta_description(
                content_info.get('meta_description', ''), 
                content_info['content'], 
                primary_keywords
            )
            
            # Optimize content
            optimized_content = self._optimize_content_text(content_info['content'], keyword_analysis)
            
            # Generate meta tags
            meta_tags = self._generate_meta_tags(content_info, primary_keywords)
            
            # Generate schema markup
            schema_markup = self._generate_schema_markup(content_info, config)
            
            # Generate improvement suggestions
            improvements = self._generate_content_improvements(content_info, keyword_analysis)
            
            return ContentOptimization(
                optimized_title=optimized_title,
                optimized_description=optimized_description,
                optimized_content=optimized_content,
                meta_tags=meta_tags,
                schema_markup=schema_markup,
                improvements=improvements
            )
            
        except Exception as e:
            logger.error(f"Content optimization failed: {e}")
            return ContentOptimization('', '', '', {}, {}, [])
    
    def _optimize_title(self, original_title: str, primary_keywords: List[str]) -> str:
        """Optimize title for SEO"""        try:
            if not original_title and not primary_keywords:
                return ''
            
            # Start with original title or create from keywords
            if original_title:
                optimized_title = original_title
            else:
                # Create title from primary keyword
                if primary_keywords:
                    optimized_title = f"Complete Guide to {primary_keywords[0].title()}"
                else:
                    return ''
            
            # Ensure primary keyword is included
            if primary_keywords and primary_keywords[0].lower() not in optimized_title.lower():
                optimized_title = f"{primary_keywords[0].title()}: {optimized_title}"
            
            # Add power words if missing
            power_words = ['Ultimate', 'Complete', 'Essential', 'Professional', 'Advanced']
            if not any(word.lower() in optimized_title.lower() for word in power_words):
                if len(optimized_title) < 50:
                    optimized_title = f"Ultimate {optimized_title}"
            
            # Ensure proper length
            if len(optimized_title) > 60:
                optimized_title = optimized_title[:57] + '...'
            elif len(optimized_title) < 30:
                if primary_keywords and len(primary_keywords) > 1:
                    optimized_title += f" and {primary_keywords[1].title()}"
            
            return optimized_title
            
        except Exception as e:
            logger.error(f"Title optimization failed: {e}")
            return original_title
    
    def _optimize_meta_description(self, original_description: str, content: str, primary_keywords: List[str]) -> str:
        """Optimize meta description for SEO"""        try:
            if not original_description:
                # Generate from content
                sentences = sent_tokenize(content)
                if sentences:
                    original_description = sentences[0]
                else:
                    original_description = ''
            
            # Start with original or generated description
            optimized_description = original_description
            
            # Ensure primary keyword is included
            if primary_keywords and primary_keywords[0].lower() not in optimized_description.lower():
                optimized_description = f"Learn about {primary_keywords[0]} - {optimized_description}"
            
            # Add call-to-action if missing
            cta_phrases = ['learn more', 'discover', 'find out', 'get started']
            if not any(phrase in optimized_description.lower() for phrase in cta_phrases):
                if len(optimized_description) < 130:
                    optimized_description += " Discover more today!"
            
            # Ensure proper length
            if len(optimized_description) > 155:
                optimized_description = optimized_description[:152] + '...'
            elif len(optimized_description) < 120:
                if primary_keywords and len(primary_keywords) > 1:
                    addition = f" Explore {primary_keywords[1]} and more."
                    if len(optimized_description + addition) <= 155:
                        optimized_description += addition
            
            return optimized_description
            
        except Exception as e:
            logger.error(f"Meta description optimization failed: {e}")
            return original_description
    
    def _optimize_content_text(self, content: str, keyword_analysis: List[KeywordAnalysis]) -> str:
        """Optimize content text for SEO"""        try:
            optimized_content = content
            
            # Get primary keywords with low density
            underused_keywords = [
                kw for kw in keyword_analysis[:5] 
                if kw.relevance_score > 0.4 and kw.density < 1.0
            ]
            
            # Add keywords naturally to content
            for keyword_obj in underused_keywords:
                keyword = keyword_obj.keyword
                current_density = keyword_obj.density
                target_density = 1.5  # Target 1.5% density
                
                # Calculate how many more occurrences needed
                total_words = len(word_tokenize(content))
                current_count = int((current_density / 100) * total_words)
                target_count = int((target_density / 100) * total_words)
                
                if target_count > current_count:
                    needed_count = target_count - current_count
                    
                    # Add keyword naturally in different variations
                    variations = [
                        f"When working with {keyword},",
                        f"The importance of {keyword} cannot be overstated.",
                        f"Understanding {keyword} is crucial for success.",
                        f"Professional {keyword} techniques",
                        f"Advanced {keyword} strategies"
                    ]
                    
                    # Add variations to content (simplified approach)
                    for i in range(min(needed_count, len(variations))):
                        if variations[i] not in optimized_content:
                            # Insert at appropriate places (end of paragraphs)
                            paragraphs = optimized_content.split('\n\n')
                            if len(paragraphs) > i:
                                paragraphs[i] += f" {variations[i]}"
                                optimized_content = '\n\n'.join(paragraphs)
            
            return optimized_content
            
        except Exception as e:
            logger.error(f"Content text optimization failed: {e}")
            return content
    
    def _generate_meta_tags(self, content_info: Dict[str, Any], primary_keywords: List[str]) -> Dict[str, str]:
        """Generate SEO meta tags"""        try:
            meta_tags = {}
            
            # Basic meta tags
            meta_tags['title'] = content_info.get('title', '')
            meta_tags['description'] = content_info.get('meta_description', '')
            
            # Keywords meta tag (though less important now)
            if primary_keywords:
                meta_tags['keywords'] = ', '.join(primary_keywords[:10])
            
            # Author tag
            if content_info.get('author'):
                meta_tags['author'] = content_info['author']
            
            # Content type
            meta_tags['content-type'] = 'text/html; charset=utf-8'
            
            # Robots tag
            meta_tags['robots'] = 'index, follow'
            
            # Viewport for mobile
            meta_tags['viewport'] = 'width=device-width, initial-scale=1.0'
            
            # Open Graph tags for social media
            meta_tags['og:title'] = content_info.get('title', '')
            meta_tags['og:description'] = content_info.get('meta_description', '')
            meta_tags['og:type'] = 'article'
            meta_tags['og:url'] = content_info.get('url', '')
            
            # Twitter Card tags
            meta_tags['twitter:card'] = 'summary_large_image'
            meta_tags['twitter:title'] = content_info.get('title', '')
            meta_tags['twitter:description'] = content_info.get('meta_description', '')
            
            return meta_tags
            
        except Exception as e:
            logger.error(f"Meta tags generation failed: {e}")
            return {}
    
    def _generate_schema_markup(self, content_info: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Schema.org markup"""        try:
            schema = {
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": content_info.get('title', ''),
                "description": content_info.get('meta_description', ''),
                "author": {
                    "@type": "Person",
                    "name": content_info.get('author', 'Unknown')
                },
                "publisher": {
                    "@type": "Organization",
                    "name": "IA Influencer Agent",
                    "logo": {
                        "@type": "ImageObject",
                        "url": "https://example.com/logo.png"
                    }
                },
                "datePublished": "2025-01-01",
                "dateModified": "2025-01-01",
                "mainEntityOfPage": {
                    "@type": "WebPage",
                    "@id": content_info.get('url', '')
                }
            }
            
            # Add specific schema based on content type
            content_type = content_info.get('content_type', '').lower()
            
            if 'music' in content_type:
                schema["@type"] = "MusicRecording"
                schema["name"] = content_info.get('title', '')
                
            elif 'video' in content_type:
                schema["@type"] = "VideoObject"
                schema["name"] = content_info.get('title', '')
                schema["description"] = content_info.get('meta_description', '')
                
            elif 'image' in content_type:
                schema["@type"] = "ImageObject"
                schema["name"] = content_info.get('title', '')
                schema["description"] = content_info.get('meta_description', '')
            
            return schema
            
        except Exception as e:
            logger.error(f"Schema markup generation failed: {e}")
            return {}
    
    def _analyze_technical_seo(self, content_info: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze technical SEO aspects"""        try:
            technical_analysis = {
                'url_optimization': {},
                'mobile_optimization': {},
                'page_speed': {},
                'crawlability': {},
                'indexability': {}
            }
            
            # URL optimization
            url = content_info.get('url', '')
            if url:
                technical_analysis['url_optimization'] = self._analyze_url_seo(url)
            
            # Mobile optimization (basic checks)
            technical_analysis['mobile_optimization'] = {
                'viewport_meta_tag': True,  # Assumed present
                'mobile_friendly_design': True,  # Would need actual testing
                'responsive_images': True  # Would need actual testing
            }
            
            # Page speed (would need actual testing)
            technical_analysis['page_speed'] = {
                'core_web_vitals': 'unknown',
                'loading_time': 'unknown',
                'optimization_suggestions': []
            }
            
            # Crawlability
            technical_analysis['crawlability'] = {
                'robots_txt': 'unknown',
                'sitemap': 'unknown',
                'internal_linking': len(content_info.get('links', [])) > 0
            }
            
            # Indexability
            technical_analysis['indexability'] = {
                'meta_robots': 'index, follow',
                'canonical_url': url,
                'duplicate_content': False  # Would need actual checking
            }
            
            return technical_analysis
            
        except Exception as e:
            logger.error(f"Technical SEO analysis failed: {e}")
            return {}
    
    def _analyze_url_seo(self, url: str) -> Dict[str, Any]:
        """Analyze URL for SEO optimization"""        try:
            parsed_url = urlparse(url)
            path = parsed_url.path
            
            analysis = {
                'length': len(url),
                'readable': True,
                'hyphens_used': '-' in path,
                'underscores_used': '_' in path,
                'parameters': bool(parsed_url.query),
                'https': parsed_url.scheme == 'https',
                'subdomain': parsed_url.netloc.count('.') > 1
            }
            
            # Check for SEO-friendly characteristics
            analysis['seo_friendly'] = (
                analysis['length'] < 100 and
                analysis['readable'] and
                analysis['hyphens_used'] and
                not analysis['underscores_used'] and
                analysis['https']
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"URL SEO analysis failed: {e}")
            return {}
    
    def _analyze_performance_seo(self, content_info: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance-related SEO factors"""        try:
            performance_analysis = {
                'content_optimization': {},
                'image_optimization': {},
                'loading_optimization': {},
                'user_experience': {}
            }
            
            # Content optimization
            content = content_info['content']
            performance_analysis['content_optimization'] = {
                'content_length': len(content),
                'content_depth': content_info['word_count'],
                'content_freshness': 'recent',  # Would need timestamp analysis
                'content_uniqueness': 'high'  # Would need plagiarism checking
            }
            
            # Image optimization
            images = content_info.get('images', [])
            performance_analysis['image_optimization'] = {
                'total_images': len(images),
                'alt_text_coverage': sum(1 for img in images if img.get('alt_text')) / len(images) if images else 0,
                'optimized_formats': 'unknown',  # Would need actual analysis
                'lazy_loading': 'unknown'  # Would need actual analysis
            }
            
            # Loading optimization
            performance_analysis['loading_optimization'] = {
                'minification': 'unknown',
                'compression': 'unknown',
                'caching': 'unknown',
                'cdn_usage': 'unknown'
            }
            
            # User experience
            performance_analysis['user_experience'] = {
                'readability_score': self._analyze_readability_seo(content),
                'mobile_friendly': True,  # Assumed
                'navigation_clarity': True,  # Would need actual analysis
                'call_to_action': 'present' if any(cta in content.lower() for cta in ['click', 'learn more', 'get started']) else 'missing'
            }
            
            return performance_analysis
            
        except Exception as e:
            logger.error(f"Performance SEO analysis failed: {e}")
            return {}
    
    def _generate_seo_analysis_recommendations(self, title_score: float, meta_score: float, 
                                             structure_score: float, quality_score: float, 
                                             readability_score: float) -> List[str]:
        """Generate SEO analysis recommendations"""        recommendations = []
        
        if title_score < 0.7:
            recommendations.append("Optimize title: Include primary keyword and power words")
        
        if meta_score < 0.7:
            recommendations.append("Improve meta description: Add call-to-action and ensure optimal length")
        
        if structure_score < 0.7:
            recommendations.append("Enhance content structure: Use proper headings and improve internal linking")
        
        if quality_score < 0.7:
            recommendations.append("Increase content quality: Add more detailed information and unique insights")
        
        if readability_score < 0.7:
            recommendations.append("Improve readability: Use shorter sentences and simpler language")
        
        return recommendations
    
    def _identify_technical_issues(self, content_info: Dict[str, Any]) -> List[str]:
        """Identify technical SEO issues"""        issues = []
        
        # Missing meta description
        if not content_info.get('meta_description'):
            issues.append("Missing meta description")
        
        # Missing title
        if not content_info.get('title'):
            issues.append("Missing title tag")
        
        # No headings
        if not content_info.get('headings'):
            issues.append("No heading tags found")
        
        # No images with alt text
        images = content_info.get('images', [])
        if images and not any(img.get('alt_text') for img in images):
            issues.append("Images missing alt text")
        
        # Short content
        if content_info['word_count'] < 300:
            issues.append("Content too short for optimal SEO")
        
        return issues
    
    def _analyze_heading_hierarchy(self, headings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze heading hierarchy"""        try:
            hierarchy_analysis = {
                'has_h1': False,
                'h1_count': 0,
                'proper_hierarchy': True,
                'heading_distribution': {}
            }
            
            if not headings:
                return hierarchy_analysis
            
            # Count headings by level
            level_counts = Counter(h.get('level', 1) for h in headings)
            hierarchy_analysis['heading_distribution'] = dict(level_counts)
            
            # Check for H1
            hierarchy_analysis['h1_count'] = level_counts.get(1, 0)
            hierarchy_analysis['has_h1'] = hierarchy_analysis['h1_count'] > 0
            
            # Check proper hierarchy (simplified)
            levels = [h.get('level', 1) for h in headings]
            if levels:
                for i in range(1, len(levels)):
                    if levels[i] > levels[i-1] + 1:
                        hierarchy_analysis['proper_hierarchy'] = False
                        break
            
            return hierarchy_analysis
            
        except Exception as e:
            logger.error(f"Heading hierarchy analysis failed: {e}")
            return {}
    
    def _analyze_paragraph_structure(self, content: str) -> Dict[str, Any]:
        """Analyze paragraph structure"""        try:
            paragraphs = content.split('\n\n')
            paragraphs = [p.strip() for p in paragraphs if p.strip()]
            
            if not paragraphs:
                return {}
            
            paragraph_lengths = [len(p.split()) for p in paragraphs]
            
            return {
                'paragraph_count': len(paragraphs),
                'avg_paragraph_length': np.mean(paragraph_lengths),
                'max_paragraph_length': max(paragraph_lengths),
                'min_paragraph_length': min(paragraph_lengths),
                'optimal_length': all(50 <= length <= 150 for length in paragraph_lengths)
            }
            
        except Exception as e:
            logger.error(f"Paragraph structure analysis failed: {e}")
            return {}
    
    def _analyze_link_structure(self, links: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze link structure"""        try:
            internal_links = [link for link in links if not self._is_external_link(link)]
            external_links = [link for link in links if self._is_external_link(link)]
            
            return {
                'total_links': len(links),
                'internal_links': len(internal_links),
                'external_links': len(external_links),
                'internal_external_ratio': len(internal_links) / len(external_links) if external_links else float('inf'),
                'has_internal_links': len(internal_links) > 0,
                'has_external_links': len(external_links) > 0
            }
            
        except Exception as e:
            logger.error(f"Link structure analysis failed: {e}")
            return {}
    
    def _is_external_link(self, link: Union[str, Dict[str, Any]]) -> bool:
        """Check if link is external"""        try:
            if isinstance(link, dict):
                url = link.get('url', '')
            else:
                url = str(link)
            
            return url.startswith('http://') or url.startswith('https://')
            
        except Exception as e:
            logger.error(f"External link check failed: {e}")
            return False
    
    def _generate_content_improvements(self, content_info: Dict[str, Any], 
                                     keyword_analysis: List[KeywordAnalysis]) -> List[str]:
        """Generate content improvement suggestions"""        improvements = []
        
        # Content length improvements
        word_count = content_info['word_count']
        if word_count < 500:
            improvements.append("Expand content to at least 500 words for better SEO performance")
        elif word_count < 1000:
            improvements.append("Consider expanding content to 1000+ words for comprehensive coverage")
        
        # Keyword improvements
        high_relevance_keywords = [kw for kw in keyword_analysis if kw.relevance_score > 0.7]
        if len(high_relevance_keywords) < 3:
            improvements.append("Identify and incorporate more relevant keywords")
        
        # Structure improvements
        if not content_info.get('headings'):
            improvements.append("Add heading tags (H1, H2, H3) to improve content structure")
        
        # Media improvements
        if not content_info.get('images'):
            improvements.append("Add relevant images to enhance user engagement")
        
        # Link improvements
        links = content_info.get('links', [])
        internal_links = [link for link in links if not self._is_external_link(link)]
        if len(internal_links) < 2:
            improvements.append("Add more internal links to improve site navigation and SEO")
        
        return improvements
    
    def _generate_seo_recommendations(self, seo_analysis: SEOAnalysis, 
                                    keyword_analysis: List[KeywordAnalysis],
                                    content_optimization: ContentOptimization,
                                    technical_seo: Dict[str, Any],
                                    config: Dict[str, Any]) -> List[str]:
        """Generate comprehensive SEO recommendations"""        recommendations = []
        
        # Add specific recommendations based on analysis results
        recommendations.extend(seo_analysis.recommendations)
        recommendations.extend(content_optimization.improvements)
        
        # Add keyword-based recommendations
        if keyword_analysis:
            top_keyword = keyword_analysis[0]
            if top_keyword.density < 1.0:
                recommendations.append(f"Increase density of primary keyword '{top_keyword.keyword}' to 1-2%")
        
        # Add technical recommendations
        if technical_seo.get('url_optimization', {}).get('seo_friendly') is False:
            recommendations.append("Optimize URL structure for better SEO")
        
        # Overall SEO score recommendations
        if seo_analysis.seo_score < 0.6:
            recommendations.append("Overall SEO score is below optimal - focus on title and content optimization")
        elif seo_analysis.seo_score < 0.8:
            recommendations.append("Good SEO foundation - fine-tune meta descriptions and keyword usage")
        
        return list(set(recommendations))  # Remove duplicates
