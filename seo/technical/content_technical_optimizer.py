"""Content Technical Optimizer
Advanced content structure and semantic optimization for IA Chérie creator economy platform.

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

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie

Author: Fahed Mlaiel (mlaiel@live.de)
Technical SEO Expert: Advanced Technical Optimization
Content Architecture Specialist: Semantic Structure Optimization
Performance Engineer: Content Loading & Rendering Optimization
ML Engineer: AI-powered Content Analysis & Enhancement
"""

import asyncio
import re
import json
import hashlib
import requests
from urllib.parse import urlparse, urljoin
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup, NavigableString
import xml.etree.ElementTree as ET
from collections import defaultdict, Counter
import nltk
from textstat import flesch_reading_ease, flesch_kincaid_grade
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class ContentType(Enum):
    """Content types for optimization."""
    ARTICLE = "article"
    BLOG_POST = "blog_post"
    TUTORIAL = "tutorial"
    REVIEW = "review"
    GUIDE = "guide"
    NEWS = "news"
    CREATIVE_CONTENT = "creative_content"
    TECHNICAL_DOCS = "technical_docs"


class SemanticEntity(Enum):
    """Semantic entity types."""
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    PRODUCT = "product"
    EVENT = "event"
    CONCEPT = "concept"
    TECHNOLOGY = "technology"


@dataclass
class ContentStructureIssue:
    """Content structure issue."""
    issue_type: str
    severity: str  # critical, high, medium, low
    description: str
    location: str  # where in content
    recommendation: str
    technical_impact: str
    seo_impact: str


@dataclass
class SemanticAnalysisResult:
    """Semantic analysis results."""
    entities: List[Dict[str, Any]] = field(default_factory=list)
    topics: List[Dict[str, Any]] = field(default_factory=list)
    sentiment_score: float = 0.0
    readability_score: float = 0.0
    complexity_score: float = 0.0
    semantic_coherence: float = 0.0
    keyword_density: Dict[str, float] = field(default_factory=dict)
    content_gaps: List[str] = field(default_factory=list)


@dataclass
class ContentOptimizationResult:
    """Content optimization results."""
    content_id: str
    original_content: str
    optimized_content: str
    content_type: ContentType
    structure_issues: List[ContentStructureIssue]
    semantic_analysis: SemanticAnalysisResult
    performance_metrics: Dict[str, Any]
    optimization_score: float
    recommendations: List[str]
    schema_markup: Dict[str, Any]
    technical_improvements: List[str]


class HTMLStructureAnalyzer:
    """Analyze and optimize HTML structure for technical SEO."""
    
    def __init__(self):
        self.logger = self._setup_logging()
        
        # HTML structure rules
        self.structure_rules = {
            'heading_hierarchy': {
                'required': True,
                'max_levels': 6,
                'skip_levels': False
            },
            'semantic_elements': {
                'article': {'required': True, 'max_count': 1},
                'main': {'required': True, 'max_count': 1},
                'header': {'required': True, 'max_count': 1},
                'footer': {'required': False, 'max_count': 1},
                'nav': {'required': False, 'max_count': 3},
                'aside': {'required': False, 'max_count': 2}
            },
            'content_sections': {
                'min_paragraphs': 3,
                'max_paragraph_length': 150,
                'list_formatting': True
            }
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger(f'{__name__}.HTMLStructureAnalyzer')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    async def analyze_html_structure(self, html_content: str) -> Dict[str, Any]:
        """Comprehensive HTML structure analysis."""
        self.logger.info("Analyzing HTML structure for technical optimization")
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        analysis = {
            'heading_structure': await self._analyze_heading_structure(soup),
            'semantic_elements': await self._analyze_semantic_elements(soup),
            'content_organization': await self._analyze_content_organization(soup),
            'accessibility_features': await self._analyze_accessibility_features(soup),
            'performance_structure': await self._analyze_performance_structure(soup),
            'issues': [],
            'recommendations': []
        }
        
        # Identify structural issues
        issues = await self._identify_structure_issues(analysis, soup)
        analysis['issues'] = issues
        
        # Generate recommendations
        recommendations = await self._generate_structure_recommendations(analysis)
        analysis['recommendations'] = recommendations
        
        return analysis
    
    async def _analyze_heading_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze heading hierarchy and structure."""
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        heading_analysis = {
            'total_headings': len(headings),
            'heading_distribution': defaultdict(int),
            'hierarchy_issues': [],
            'missing_h1': False,
            'multiple_h1': False,
            'skipped_levels': [],
            'empty_headings': []
        }
        
        if not headings:
            heading_analysis['missing_h1'] = True
            return heading_analysis
        
        # Analyze heading distribution and hierarchy
        heading_levels = []
        for heading in headings:
            level = int(heading.name[1])
            heading_levels.append(level)
            heading_analysis['heading_distribution'][level] += 1
            
            # Check for empty headings
            if not heading.get_text().strip():
                heading_analysis['empty_headings'].append(heading.name)
        
        # Check H1 requirements
        h1_count = heading_analysis['heading_distribution'][1]
        if h1_count == 0:
            heading_analysis['missing_h1'] = True
        elif h1_count > 1:
            heading_analysis['multiple_h1'] = True
        
        # Check for skipped levels
        for i in range(1, len(heading_levels)):
            current_level = heading_levels[i]
            previous_level = heading_levels[i-1]
            if current_level > previous_level + 1:
                heading_analysis['skipped_levels'].append({
                    'from': previous_level,
                    'to': current_level,
                    'position': i
                })
        
        return heading_analysis
    
    async def _analyze_semantic_elements(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze semantic HTML5 elements usage."""
        semantic_elements = ['article', 'main', 'header', 'footer', 'nav', 'aside', 'section']
        
        element_analysis = {
            'elements_found': {},
            'elements_missing': [],
            'elements_overused': [],
            'semantic_score': 0
        }
        
        for element in semantic_elements:
            found_elements = soup.find_all(element)
            count = len(found_elements)
            element_analysis['elements_found'][element] = count
            
            # Check against rules
            rule = self.structure_rules['semantic_elements'].get(element, {})
            if rule.get('required', False) and count == 0:
                element_analysis['elements_missing'].append(element)
            elif count > rule.get('max_count', 10):
                element_analysis['elements_overused'].append(element)
        
        # Calculate semantic score
        required_elements = ['article', 'main', 'header']
        found_required = sum(1 for elem in required_elements if element_analysis['elements_found'].get(elem, 0) > 0)
        element_analysis['semantic_score'] = (found_required / len(required_elements)) * 100
        
        return element_analysis
    
    async def _analyze_content_organization(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze content organization and structure."""
        organization = {
            'paragraph_count': 0,
            'average_paragraph_length': 0,
            'list_usage': {},
            'table_usage': {},
            'content_sections': 0,
            'reading_flow_score': 0
        }
        
        # Analyze paragraphs
        paragraphs = soup.find_all('p')
        organization['paragraph_count'] = len(paragraphs)
        
        if paragraphs:
            paragraph_lengths = [len(p.get_text().strip()) for p in paragraphs if p.get_text().strip()]
            organization['average_paragraph_length'] = sum(paragraph_lengths) / len(paragraph_lengths) if paragraph_lengths else 0
        
        # Analyze lists
        ul_lists = soup.find_all('ul')
        ol_lists = soup.find_all('ol')
        organization['list_usage'] = {
            'unordered_lists': len(ul_lists),
            'ordered_lists': len(ol_lists),
            'total_list_items': len(soup.find_all('li'))
        }
        
        # Analyze tables
        tables = soup.find_all('table')
        organization['table_usage'] = {
            'table_count': len(tables),
            'tables_with_headers': len([t for t in tables if t.find('th')]),
            'tables_with_captions': len([t for t in tables if t.find('caption')])
        }
        
        # Analyze content sections
        sections = soup.find_all('section')
        organization['content_sections'] = len(sections)
        
        return organization
    
    async def _analyze_accessibility_features(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze accessibility features in content structure."""
        accessibility = {
            'images_with_alt': 0,
            'images_without_alt': 0,
            'links_with_titles': 0,
            'links_without_context': 0,
            'form_labels': 0,
            'landmark_elements': 0,
            'accessibility_score': 0
        }
        
        # Analyze images
        images = soup.find_all('img')
        for img in images:
            if img.get('alt') is not None:
                accessibility['images_with_alt'] += 1
            else:
                accessibility['images_without_alt'] += 1
        
        # Analyze links
        links = soup.find_all('a')
        for link in links:
            if link.get('title') or link.get('aria-label'):
                accessibility['links_with_titles'] += 1
            elif not link.get_text().strip():
                accessibility['links_without_context'] += 1
        
        # Analyze form elements
        labels = soup.find_all('label')
        accessibility['form_labels'] = len(labels)
        
        # Count landmark elements
        landmark_elements = ['main', 'nav', 'header', 'footer', 'aside', 'section']
        accessibility['landmark_elements'] = sum(len(soup.find_all(elem)) for elem in landmark_elements)
        
        # Calculate accessibility score
        total_images = accessibility['images_with_alt'] + accessibility['images_without_alt']
        alt_score = (accessibility['images_with_alt'] / total_images * 100) if total_images > 0 else 100
        
        landmark_score = min(100, accessibility['landmark_elements'] * 20)
        
        accessibility['accessibility_score'] = (alt_score + landmark_score) / 2
        
        return accessibility
    
    async def _analyze_performance_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze HTML structure for performance impact."""
        performance = {
            'dom_depth': 0,
            'dom_size': 0,
            'inline_styles': 0,
            'inline_scripts': 0,
            'external_resources': {
                'stylesheets': 0,
                'scripts': 0,
                'images': 0
            },
            'performance_score': 0
        }
        
        # Calculate DOM depth and size
        performance['dom_size'] = len(soup.find_all())
        performance['dom_depth'] = await self._calculate_dom_depth(soup)
        
        # Count inline styles and scripts
        performance['inline_styles'] = len(soup.find_all(attrs={'style': True}))
        performance['inline_scripts'] = len(soup.find_all('script', src=False))
        
        # Count external resources
        performance['external_resources']['stylesheets'] = len(soup.find_all('link', rel='stylesheet'))
        performance['external_resources']['scripts'] = len(soup.find_all('script', src=True))
        performance['external_resources']['images'] = len(soup.find_all('img', src=True))
        
        # Calculate performance score
        score = 100
        if performance['dom_depth'] > 12:
            score -= 20
        if performance['dom_size'] > 1500:
            score -= 15
        if performance['inline_styles'] > 5:
            score -= 10
        if performance['inline_scripts'] > 2:
            score -= 15
        
        performance['performance_score'] = max(0, score)
        
        return performance
    
    async def _calculate_dom_depth(self, element, current_depth=0):
        """Calculate maximum DOM depth."""
        max_depth = current_depth
        for child in element.children:
            if hasattr(child, 'children'):
                child_depth = await self._calculate_dom_depth(child, current_depth + 1)
                max_depth = max(max_depth, child_depth)
        return max_depth
    
    async def _identify_structure_issues(self, analysis: Dict[str, Any], soup: BeautifulSoup) -> List[ContentStructureIssue]:
        """Identify structural issues in HTML."""
        issues = []
        
        # Heading structure issues
        heading_analysis = analysis['heading_structure']
        if heading_analysis['missing_h1']:
            issues.append(ContentStructureIssue(
                issue_type='missing_h1',
                severity='critical',
                description='Page is missing H1 heading',
                location='document_head',
                recommendation='Add a single, descriptive H1 heading',
                technical_impact='Poor document structure and accessibility',
                seo_impact='Reduced search engine understanding of page topic'
            ))
        
        if heading_analysis['multiple_h1']:
            issues.append(ContentStructureIssue(
                issue_type='multiple_h1',
                severity='medium',
                description='Page has multiple H1 headings',
                location='document_body',
                recommendation='Use only one H1 per page',
                technical_impact='Confused document hierarchy',
                seo_impact='Diluted topic focus for search engines'
            ))
        
        if heading_analysis['skipped_levels']:
            issues.append(ContentStructureIssue(
                issue_type='skipped_heading_levels',
                severity='medium',
                description=f'Heading hierarchy skips levels: {heading_analysis["skipped_levels"]}',
                location='document_body',
                recommendation='Use sequential heading levels (h1→h2→h3)',
                technical_impact='Poor accessibility and screen reader navigation',
                seo_impact='Reduced content structure understanding'
            ))
        
        # Semantic elements issues
        semantic_analysis = analysis['semantic_elements']
        for missing_element in semantic_analysis['elements_missing']:
            issues.append(ContentStructureIssue(
                issue_type='missing_semantic_element',
                severity='high' if missing_element in ['main', 'article'] else 'medium',
                description=f'Missing semantic element: {missing_element}',
                location='document_structure',
                recommendation=f'Add <{missing_element}> element for better semantic structure',
                technical_impact='Reduced accessibility and document semantics',
                seo_impact='Missed semantic signals for search engines'
            ))
        
        # Performance issues
        performance_analysis = analysis['performance_structure']
        if performance_analysis['dom_depth'] > 12:
            issues.append(ContentStructureIssue(
                issue_type='excessive_dom_depth',
                severity='medium',
                description=f'DOM depth is {performance_analysis["dom_depth"]} (recommended: <12)',
                location='document_structure',
                recommendation='Simplify HTML structure and reduce nesting',
                technical_impact='Slower rendering and increased memory usage',
                seo_impact='Potential negative impact on Core Web Vitals'
            ))
        
        return issues
    
    async def _generate_structure_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate structural optimization recommendations."""
        recommendations = []
        
        # Heading recommendations
        heading_analysis = analysis['heading_structure']
        if heading_analysis['total_headings'] < 3:
            recommendations.append('Add more headings to improve content structure and readability')
        
        # Semantic recommendations
        semantic_analysis = analysis['semantic_elements']
        if semantic_analysis['semantic_score'] < 70:
            recommendations.append('Improve semantic HTML usage with elements like <article>, <main>, <header>')
        
        # Accessibility recommendations
        accessibility_analysis = analysis['accessibility_features']
        if accessibility_analysis['accessibility_score'] < 80:
            recommendations.append('Improve accessibility with alt text, proper labels, and semantic markup')
        
        # Performance recommendations
        performance_analysis = analysis['performance_structure']
        if performance_analysis['performance_score'] < 80:
            recommendations.append('Optimize HTML structure for better performance (reduce DOM complexity)')
        
        return recommendations


class SemanticContentAnalyzer:
    """Analyze content semantics and optimize for entity recognition."""
    
    def __init__(self):
        self.logger = self._setup_logging()
        
        # Initialize NLP models
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            self.logger.warning("spaCy model not available. Some features will be limited.")
            self.nlp = None
        
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger(f'{__name__}.SemanticContentAnalyzer')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    async def analyze_semantic_content(self, content: str, content_type: ContentType) -> SemanticAnalysisResult:
        """Comprehensive semantic content analysis."""
        self.logger.info(f"Analyzing semantic content for {content_type.value}")
        
        # Clean content for analysis
        clean_content = await self._clean_content_for_analysis(content)
        
        analysis = SemanticAnalysisResult()
        
        # Entity extraction
        if self.nlp:
            analysis.entities = await self._extract_entities(clean_content)
        
        # Topic analysis
        analysis.topics = await self._analyze_topics(clean_content)
        
        # Readability analysis
        analysis.readability_score = await self._calculate_readability(clean_content)
        
        # Complexity analysis
        analysis.complexity_score = await self._calculate_complexity(clean_content)
        
        # Semantic coherence
        analysis.semantic_coherence = await self._calculate_semantic_coherence(clean_content)
        
        # Keyword density
        analysis.keyword_density = await self._calculate_keyword_density(clean_content)
        
        # Content gaps identification
        analysis.content_gaps = await self._identify_content_gaps(clean_content, content_type)
        
        return analysis
    
    async def _clean_content_for_analysis(self, content: str) -> str:
        """Clean HTML content for text analysis."""
        if '<' in content and '>' in content:
            soup = BeautifulSoup(content, 'html.parser')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            clean_content = soup.get_text()
        else:
            clean_content = content
        
        # Clean whitespace
        clean_content = re.sub(r'\s+', ' ', clean_content).strip()
        return clean_content
    
    async def _extract_entities(self, content: str) -> List[Dict[str, Any]]:
        """Extract named entities from content."""
        if not self.nlp:
            return []
        
        doc = self.nlp(content[:1000000])  # Limit content length for processing
        
        entities = []
        for ent in doc.ents:
            entity_type = ent.label_
            confidence = 1.0  # spaCy doesn't provide confidence scores directly
            
            # Map spaCy labels to our semantic entity types
            mapped_type = await self._map_entity_type(entity_type)
            
            entities.append({
                'text': ent.text,
                'type': mapped_type,
                'start': ent.start_char,
                'end': ent.end_char,
                'confidence': confidence,
                'context': content[max(0, ent.start_char-50):ent.end_char+50]
            })
        
        # Remove duplicates and sort by confidence
        unique_entities = {}
        for entity in entities:
            key = (entity['text'].lower(), entity['type'])
            if key not in unique_entities or entity['confidence'] > unique_entities[key]['confidence']:
                unique_entities[key] = entity
        
        return list(unique_entities.values())
    
    async def _map_entity_type(self, spacy_label: str) -> str:
        """Map spaCy entity labels to our semantic types."""
        mapping = {
            'PERSON': SemanticEntity.PERSON.value,
            'ORG': SemanticEntity.ORGANIZATION.value,
            'GPE': SemanticEntity.LOCATION.value,
            'LOC': SemanticEntity.LOCATION.value,
            'PRODUCT': SemanticEntity.PRODUCT.value,
            'EVENT': SemanticEntity.EVENT.value,
            'TECH': SemanticEntity.TECHNOLOGY.value,
            'MONEY': SemanticEntity.CONCEPT.value,
            'DATE': SemanticEntity.CONCEPT.value,
            'TIME': SemanticEntity.CONCEPT.value
        }
        return mapping.get(spacy_label, SemanticEntity.CONCEPT.value)
    
    async def _analyze_topics(self, content: str) -> List[Dict[str, Any]]:
        """Analyze content topics using TF-IDF."""
        try:
            # Simple topic extraction using TF-IDF
            sentences = content.split('.')
            if len(sentences) < 2:
                return []
            
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(sentences)
            feature_names = self.tfidf_vectorizer.get_feature_names_out()
            
            # Get top terms
            tfidf_scores = tfidf_matrix.sum(axis=0).A1
            top_indices = tfidf_scores.argsort()[-20:][::-1]
            
            topics = []
            for idx in top_indices:
                if tfidf_scores[idx] > 0.1:  # Threshold for relevance
                    topics.append({
                        'term': feature_names[idx],
                        'score': float(tfidf_scores[idx]),
                        'type': 'keyword'
                    })
            
            return topics[:10]  # Return top 10 topics
            
        except Exception as e:
            self.logger.error(f"Error in topic analysis: {e}")
            return []
    
    async def _calculate_readability(self, content: str) -> float:
        """Calculate content readability score."""
        try:
            # Use Flesch Reading Ease score
            flesch_score = flesch_reading_ease(content)
            return max(0, min(100, flesch_score))
        except:
            return 50.0  # Default score if calculation fails
    
    async def _calculate_complexity(self, content: str) -> float:
        """Calculate content complexity score."""
        try:
            # Use Flesch-Kincaid Grade Level
            grade_level = flesch_kincaid_grade(content)
            # Convert to 0-100 scale (12th grade = 100)
            complexity_score = min(100, (grade_level / 12) * 100)
            return max(0, complexity_score)
        except:
            return 50.0  # Default score if calculation fails
    
    async def _calculate_semantic_coherence(self, content: str) -> float:
        """Calculate semantic coherence of content."""
        try:
            sentences = [s.strip() for s in content.split('.') if len(s.strip()) > 10]
            if len(sentences) < 2:
                return 50.0
            
            # Calculate sentence similarity using TF-IDF
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(sentences)
            similarity_matrix = cosine_similarity(tfidf_matrix)
            
            # Calculate average similarity (excluding diagonal)
            n = similarity_matrix.shape[0]
            total_similarity = 0
            count = 0
            
            for i in range(n):
                for j in range(i + 1, n):
                    total_similarity += similarity_matrix[i][j]
                    count += 1
            
            if count > 0:
                avg_similarity = total_similarity / count
                coherence_score = avg_similarity * 100
                return max(0, min(100, coherence_score))
            
            return 50.0
            
        except Exception as e:
            self.logger.error(f"Error calculating semantic coherence: {e}")
            return 50.0
    
    async def _calculate_keyword_density(self, content: str) -> Dict[str, float]:
        """Calculate keyword density for important terms."""
        words = re.findall(r'\b\w+\b', content.lower())
        total_words = len(words)
        
        if total_words == 0:
            return {}
        
        # Count word frequencies
        word_counts = Counter(words)
        
        # Filter out common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'}
        
        # Calculate density for significant words
        keyword_density = {}
        for word, count in word_counts.most_common(20):
            if word not in stop_words and len(word) > 2:
                density = (count / total_words) * 100
                keyword_density[word] = round(density, 2)
        
        return keyword_density
    
    async def _identify_content_gaps(self, content: str, content_type: ContentType) -> List[str]:
        """Identify potential content gaps based on content type."""
        gaps = []
        
        content_lower = content.lower()
        
        # Common gaps based on content type
        if content_type == ContentType.TUTORIAL:
            if 'step' not in content_lower and 'steps' not in content_lower:
                gaps.append('Missing step-by-step structure')
            if 'example' not in content_lower:
                gaps.append('Missing practical examples')
            if 'tip' not in content_lower and 'tips' not in content_lower:
                gaps.append('Missing helpful tips or best practices')
        
        elif content_type == ContentType.REVIEW:
            if 'pros' not in content_lower and 'advantages' not in content_lower:
                gaps.append('Missing pros/advantages section')
            if 'cons' not in content_lower and 'disadvantages' not in content_lower:
                gaps.append('Missing cons/disadvantages section')
            if 'rating' not in content_lower and 'score' not in content_lower:
                gaps.append('Missing rating or scoring system')
        
        elif content_type == ContentType.GUIDE:
            if 'introduction' not in content_lower and 'overview' not in content_lower:
                gaps.append('Missing introduction or overview section')
            if 'conclusion' not in content_lower and 'summary' not in content_lower:
                gaps.append('Missing conclusion or summary section')
            if len(content.split()) < 1000:
                gaps.append('Content may be too short for comprehensive guide')
        
        # General content gaps
        if 'image' not in content_lower and '<img' not in content:
            gaps.append('Missing visual elements (images, diagrams)')
        
        if len(re.findall(r'\?', content)) < 2:
            gaps.append('Missing FAQ or questions section')
        
        return gaps


class ContentTechnicalOptimizer:
    """Main content technical optimizer for IA Chérie creator economy."""
    
    def __init__(self):
        self.logger = self._setup_logging()
        
        # Initialize analyzers
        self.html_analyzer = HTMLStructureAnalyzer()
        self.semantic_analyzer = SemanticContentAnalyzer()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging."""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    async def optimize_content_technical(self, content_data: Dict[str, Any]) -> ContentOptimizationResult:
        """Comprehensive technical content optimization."""
        content_id = content_data.get('content_id', 'unknown')
        self.logger.info(f"Starting technical optimization for content {content_id}")
        
        start_time = datetime.now(timezone.utc)
        
        content = content_data.get('content', '')
        content_type = ContentType(content_data.get('content_type', 'article'))
        
        try:
            # 1. HTML Structure Analysis
            self.logger.info("Analyzing HTML structure...")
            html_analysis = await self.html_analyzer.analyze_html_structure(content)
            
            # 2. Semantic Content Analysis
            self.logger.info("Performing semantic analysis...")
            semantic_analysis = await self.semantic_analyzer.analyze_semantic_content(content, content_type)
            
            # 3. Content Structure Optimization
            optimized_content = await self._optimize_content_structure(content, html_analysis, semantic_analysis)
            
            # 4. Generate Schema Markup
            schema_markup = await self._generate_content_schema(content_data, semantic_analysis)
            
            # 5. Performance Optimization
            performance_metrics = await self._analyze_content_performance(content, optimized_content)
            
            # 6. Calculate Optimization Score
            optimization_score = await self._calculate_optimization_score(
                html_analysis, semantic_analysis, performance_metrics
            )
            
            # 7. Generate Recommendations
            recommendations = await self._generate_comprehensive_recommendations(
                html_analysis, semantic_analysis, content_type
            )
            
            # 8. Technical Improvements
            technical_improvements = await self._generate_technical_improvements(
                html_analysis, performance_metrics
            )
            
            # 9. Compile Structure Issues
            structure_issues = html_analysis.get('issues', [])
            
            # Create optimization result
            result = ContentOptimizationResult(
                content_id=content_id,
                original_content=content,
                optimized_content=optimized_content,
                content_type=content_type,
                structure_issues=structure_issues,
                semantic_analysis=semantic_analysis,
                performance_metrics=performance_metrics,
                optimization_score=optimization_score,
                recommendations=recommendations,
                schema_markup=schema_markup,
                technical_improvements=technical_improvements
            )
            
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            self.logger.info(f"Content optimization completed in {duration:.2f}s. Score: {optimization_score:.1f}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error during content optimization: {e}")
            raise
    
    async def _optimize_content_structure(self, content: str, html_analysis: Dict[str, Any], 
                                        semantic_analysis: SemanticAnalysisResult) -> str:
        """Optimize content structure based on analysis results."""
        if not content.strip():
            return content
        
        # Parse content
        soup = BeautifulSoup(content, 'html.parser')
        
        # Fix heading structure
        soup = await self._fix_heading_structure(soup, html_analysis)
        
        # Improve semantic elements
        soup = await self._improve_semantic_elements(soup, html_analysis)
        
        # Optimize paragraphs
        soup = await self._optimize_paragraphs(soup)
        
        # Add semantic markup
        soup = await self._add_semantic_markup(soup, semantic_analysis)
        
        # Improve accessibility
        soup = await self._improve_accessibility(soup)
        
        return str(soup)
    
    async def _fix_heading_structure(self, soup: BeautifulSoup, html_analysis: Dict[str, Any]) -> BeautifulSoup:
        """Fix heading hierarchy issues."""
        heading_analysis = html_analysis.get('heading_structure', {})
        
        # Add H1 if missing
        if heading_analysis.get('missing_h1', False):
            title_element = soup.find('title')
            if title_element:
                h1 = soup.new_tag('h1')
                h1.string = title_element.get_text()
                
                # Insert H1 at the beginning of main content
                main_content = soup.find('main') or soup.find('article') or soup.find('body')
                if main_content:
                    main_content.insert(0, h1)
        
        # Fix multiple H1s
        if heading_analysis.get('multiple_h1', False):
            h1_elements = soup.find_all('h1')
            for i, h1 in enumerate(h1_elements[1:], 1):  # Keep first H1, convert others
                h1.name = 'h2'
        
        return soup
    
    async def _improve_semantic_elements(self, soup: BeautifulSoup, html_analysis: Dict[str, Any]) -> BeautifulSoup:
        """Improve semantic HTML5 elements."""
        semantic_analysis = html_analysis.get('semantic_elements', {})
        
        # Add main element if missing
        if 'main' in semantic_analysis.get('elements_missing', []):
            main = soup.new_tag('main')
            
            # Move content into main
            body = soup.find('body')
            if body:
                # Find content elements (skip header, nav, footer)
                content_elements = []
                for element in body.children:
                    if hasattr(element, 'name') and element.name not in ['header', 'nav', 'footer', 'script', 'style']:
                        content_elements.append(element)
                
                # Move elements to main
                for element in content_elements:
                    main.append(element.extract())
                
                body.append(main)
        
        # Add article element if missing
        if 'article' in semantic_analysis.get('elements_missing', []):
            article = soup.new_tag('article')
            main = soup.find('main')
            
            if main:
                # Move main content into article
                content_elements = list(main.children)
                for element in content_elements:
                    if hasattr(element, 'name'):
                        article.append(element.extract())
                
                main.append(article)
        
        return soup
    
    async def _optimize_paragraphs(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Optimize paragraph structure and length."""
        paragraphs = soup.find_all('p')
        
        for p in paragraphs:
            text = p.get_text().strip()
            
            # Split overly long paragraphs
            if len(text) > 300:
                sentences = text.split('. ')
                if len(sentences) > 2:
                    # Split into multiple paragraphs
                    mid_point = len(sentences) // 2
                    first_part = '. '.join(sentences[:mid_point]) + '.'
                    second_part = '. '.join(sentences[mid_point:])
                    
                    # Update current paragraph
                    p.clear()
                    p.string = first_part
                    
                    # Create new paragraph
                    new_p = soup.new_tag('p')
                    new_p.string = second_part
                    p.insert_after(new_p)
        
        return soup
    
    async def _add_semantic_markup(self, soup: BeautifulSoup, semantic_analysis: SemanticAnalysisResult) -> BeautifulSoup:
        """Add semantic markup based on entity analysis."""
        # Add entity markup for high-confidence entities
        for entity in semantic_analysis.entities:
            if entity['confidence'] > 0.8:
                # Find and mark up entity occurrences
                entity_text = entity['text']
                entity_type = entity['type']
                
                # Create appropriate markup based on entity type
                if entity_type == 'person':
                    markup_tag = 'span'
                    markup_attrs = {'itemscope': '', 'itemtype': 'http://schema.org/Person'}
                elif entity_type == 'organization':
                    markup_tag = 'span'
                    markup_attrs = {'itemscope': '', 'itemtype': 'http://schema.org/Organization'}
                else:
                    continue  # Skip other entity types for now
                
                # Find and wrap entity text
                text_elements = soup.find_all(text=re.compile(re.escape(entity_text), re.I))
                for text_element in text_elements[:3]:  # Limit to first 3 occurrences
                    if isinstance(text_element, NavigableString):
                        parent = text_element.parent
                        if parent and parent.name not in ['script', 'style', 'title']:
                            # Replace text with marked up version
                            new_text = str(text_element).replace(entity_text, f'<{markup_tag} {" ".join([f"{k}=\"{v}\"" for k, v in markup_attrs.items()])}>{entity_text}</{markup_tag}>')
                            text_element.replace_with(BeautifulSoup(new_text, 'html.parser'))
        
        return soup
    
    async def _improve_accessibility(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Improve content accessibility."""
        # Add alt text to images without it
        images = soup.find_all('img')
        for img in images:
            if not img.get('alt'):
                # Generate basic alt text from src or surrounding context
                src = img.get('src', '')
                if src:
                    # Extract filename and create basic alt text
                    filename = src.split('/')[-1].split('.')[0]
                    alt_text = filename.replace('-', ' ').replace('_', ' ').title()
                    img['alt'] = alt_text
                else:
                    img['alt'] = 'Image'
        
        # Add labels to form elements
        inputs = soup.find_all(['input', 'textarea', 'select'])
        for input_elem in inputs:
            if not input_elem.get('aria-label') and not input_elem.get('id'):
                input_type = input_elem.get('type', 'text')
                input_elem['aria-label'] = f'{input_type.title()} field'
        
        return soup
    
    async def _generate_content_schema(self, content_data: Dict[str, Any], 
                                     semantic_analysis: SemanticAnalysisResult) -> Dict[str, Any]:
        """Generate appropriate schema markup for content."""
        content_type = content_data.get('content_type', 'article')
        
        # Base schema structure
        if content_type == 'article':
            schema_type = 'Article'
        elif content_type == 'blog_post':
            schema_type = 'BlogPosting'
        elif content_type == 'tutorial':
            schema_type = 'HowTo'
        elif content_type == 'review':
            schema_type = 'Review'
        else:
            schema_type = 'CreativeWork'
        
        schema = {
            "@context": "https://schema.org",
            "@type": schema_type,
            "headline": content_data.get('title', ''),
            "description": content_data.get('description', ''),
            "author": {
                "@type": "Person",
                "name": content_data.get('author', 'IA Chérie Creator')
            },
            "publisher": {
                "@type": "Organization",
                "name": "IA Chérie",
                "url": "https://iacherie.com"
            },
            "datePublished": content_data.get('published_date', datetime.now(timezone.utc).isoformat()),
            "dateModified": datetime.now(timezone.utc).isoformat()
        }
        
        # Add entities as mentions
        if semantic_analysis.entities:
            mentions = []
            for entity in semantic_analysis.entities[:5]:  # Top 5 entities
                if entity['type'] in ['person', 'organization']:
                    mentions.append({
                        "@type": "Thing",
                        "name": entity['text']
                    })
            
            if mentions:
                schema["mentions"] = mentions
        
        # Add keywords from topic analysis
        if semantic_analysis.topics:
            keywords = [topic['term'] for topic in semantic_analysis.topics[:10]]
            schema["keywords"] = ", ".join(keywords)
        
        return schema
    
    async def _analyze_content_performance(self, original_content: str, optimized_content: str) -> Dict[str, Any]:
        """Analyze content performance metrics."""
        metrics = {
            'original_size': len(original_content),
            'optimized_size': len(optimized_content),
            'size_difference': len(optimized_content) - len(original_content),
            'compression_ratio': 0,
            'dom_complexity_original': 0,
            'dom_complexity_optimized': 0,
            'load_time_estimate': 0
        }
        
        # Calculate compression ratio
        if metrics['original_size'] > 0:
            metrics['compression_ratio'] = (metrics['size_difference'] / metrics['original_size']) * 100
        
        # Estimate DOM complexity
        metrics['dom_complexity_original'] = original_content.count('<') 
        metrics['dom_complexity_optimized'] = optimized_content.count('<')
        
        # Estimate load time (simplified calculation)
        # Assume 1KB takes ~10ms to parse and render
        estimated_load_time = (metrics['optimized_size'] / 1024) * 10
        metrics['load_time_estimate'] = estimated_load_time
        
        return metrics
    
    async def _calculate_optimization_score(self, html_analysis: Dict[str, Any], 
                                          semantic_analysis: SemanticAnalysisResult,
                                          performance_metrics: Dict[str, Any]) -> float:
        """Calculate overall content optimization score."""
        score = 0
        
        # HTML structure score (40%)
        heading_score = 100 if not html_analysis.get('heading_structure', {}).get('missing_h1') else 50
        semantic_score = html_analysis.get('semantic_elements', {}).get('semantic_score', 50)
        accessibility_score = html_analysis.get('accessibility_features', {}).get('accessibility_score', 50)
        performance_score = html_analysis.get('performance_structure', {}).get('performance_score', 50)
        
        html_score = (heading_score + semantic_score + accessibility_score + performance_score) / 4
        score += html_score * 0.4
        
        # Semantic content score (40%)
        readability_score = semantic_analysis.readability_score
        coherence_score = semantic_analysis.semantic_coherence
        entity_score = min(100, len(semantic_analysis.entities) * 10)  # 10 points per entity, max 100
        topic_score = min(100, len(semantic_analysis.topics) * 5)  # 5 points per topic, max 100
        
        semantic_score = (readability_score + coherence_score + entity_score + topic_score) / 4
        score += semantic_score * 0.4
        
        # Performance score (20%)
        perf_score = 100
        if performance_metrics['size_difference'] > 1000:  # If content increased significantly
            perf_score -= 20
        
        score += perf_score * 0.2
        
        return min(100, max(0, score))
    
    async def _generate_comprehensive_recommendations(self, html_analysis: Dict[str, Any],
                                                    semantic_analysis: SemanticAnalysisResult,
                                                    content_type: ContentType) -> List[str]:
        """Generate comprehensive optimization recommendations."""
        recommendations = []
        
        # HTML structure recommendations
        recommendations.extend(html_analysis.get('recommendations', []))
        
        # Semantic content recommendations
        if semantic_analysis.readability_score < 60:
            recommendations.append('Improve content readability by using shorter sentences and simpler words')
        
        if semantic_analysis.semantic_coherence < 50:
            recommendations.append('Improve content coherence by better connecting ideas between sentences')
        
        if len(semantic_analysis.entities) < 3:
            recommendations.append('Add more specific entities (people, places, organizations) to improve semantic richness')
        
        if len(semantic_analysis.topics) < 5:
            recommendations.append('Expand topic coverage to provide more comprehensive information')
        
        # Content gaps recommendations
        for gap in semantic_analysis.content_gaps:
            recommendations.append(f'Content improvement: {gap}')
        
        # Content type specific recommendations
        if content_type == ContentType.TUTORIAL:
            recommendations.extend([
                'Use numbered steps for better tutorial structure',
                'Add visual aids and examples for each step',
                'Include troubleshooting section for common issues'
            ])
        elif content_type == ContentType.REVIEW:
            recommendations.extend([
                'Include rating system with clear criteria',
                'Add comparison with similar products/services',
                'Provide specific use cases and recommendations'
            ])
        
        return recommendations[:15]  # Limit to top 15 recommendations
    
    async def _generate_technical_improvements(self, html_analysis: Dict[str, Any],
                                             performance_metrics: Dict[str, Any]) -> List[str]:
        """Generate technical improvement suggestions."""
        improvements = []
        
        # Performance improvements
        if performance_metrics['optimized_size'] > 100000:  # 100KB
            improvements.append('Consider breaking content into multiple pages for better performance')
        
        if performance_metrics['dom_complexity_optimized'] > 1000:
            improvements.append('Reduce DOM complexity by simplifying HTML structure')
        
        # HTML structure improvements
        performance_analysis = html_analysis.get('performance_structure', {})
        if performance_analysis.get('inline_styles', 0) > 5:
            improvements.append('Move inline styles to external CSS files')
        
        if performance_analysis.get('inline_scripts', 0) > 2:
            improvements.append('Move inline scripts to external JavaScript files')
        
        # Accessibility improvements
        accessibility_analysis = html_analysis.get('accessibility_features', {})
        if accessibility_analysis.get('images_without_alt', 0) > 0:
            improvements.append('Add alt text to all images for better accessibility')
        
        if accessibility_analysis.get('landmark_elements', 0) < 3:
            improvements.append('Add more semantic landmark elements (main, nav, header, footer)')
        
        return improvements


# Usage Example
async def main():
    """Example usage of Content Technical Optimizer."""
    
    # Initialize content optimizer
    content_optimizer = ContentTechnicalOptimizer()
    
    try:
        # Example content data
        content_data = {
            'content_id': 'article_123',
            'content_type': 'tutorial',
            'title': 'Complete Guide to Content Optimization',
            'description': 'Learn how to optimize your content for better search visibility and user engagement.',
            'author': 'Content Expert',
            'published_date': datetime.now(timezone.utc).isoformat(),
            'content': '''
            <div>
                <h2>Introduction to Content Optimization</h2>
                <p>Content optimization is a crucial aspect of digital marketing that involves improving your content to make it more discoverable, engaging, and valuable to your target audience. This comprehensive guide will walk you through the essential steps and techniques for optimizing your content effectively.</p>
                
                <h2>Why Content Optimization Matters</h2>
                <p>In today's competitive digital landscape, simply creating content is not enough. You need to ensure that your content is optimized for search engines, user experience, and conversion goals. Proper content optimization can significantly improve your search rankings, increase organic traffic, and enhance user engagement.</p>
                
                <h3>Key Benefits</h3>
                <p>Content optimization offers numerous benefits including improved search visibility, better user experience, increased engagement rates, and higher conversion potential. By following best practices, you can create content that not only ranks well but also provides real value to your audience.</p>
                
                <h2>Optimization Techniques</h2>
                <p>There are several proven techniques for optimizing content. These include keyword research and integration, improving content structure, enhancing readability, adding visual elements, and ensuring mobile compatibility. Each of these techniques plays a crucial role in the overall optimization process.</p>
            </div>
            '''
        }
        
        print(f"\n=== Content Technical Optimization ===")
        
        # Run content optimization
        result = await content_optimizer.optimize_content_technical(content_data)
        
        print(f"Content ID: {result.content_id}")
        print(f"Content Type: {result.content_type.value}")
        print(f"Optimization Score: {result.optimization_score:.1f}/100")
        print(f"Structure Issues: {len(result.structure_issues)}")
        print(f"Entities Found: {len(result.semantic_analysis.entities)}")
        print(f"Topics Identified: {len(result.semantic_analysis.topics)}")
        print(f"Readability Score: {result.semantic_analysis.readability_score:.1f}")
        
        # Show recommendations
        if result.recommendations:
            print("\n=== Content Optimization Recommendations ===")
            for i, rec in enumerate(result.recommendations[:5], 1):
                print(f"{i}. {rec}")
        
        # Show technical improvements
        if result.technical_improvements:
            print("\n=== Technical Improvements ===")
            for i, improvement in enumerate(result.technical_improvements[:3], 1):
                print(f"{i}. {improvement}")
        
        # Show semantic analysis highlights
        print(f"\n=== Semantic Analysis Highlights ===")
        print(f"Semantic Coherence: {result.semantic_analysis.semantic_coherence:.1f}%")
        print(f"Content Complexity: {result.semantic_analysis.complexity_score:.1f}%")
        
        if result.semantic_analysis.keyword_density:
            top_keywords = list(result.semantic_analysis.keyword_density.items())[:5]
            print("Top Keywords:", ", ".join([f"{k} ({v}%)" for k, v in top_keywords]))
        
        if result.semantic_analysis.content_gaps:
            print("Content Gaps:", ", ".join(result.semantic_analysis.content_gaps[:3]))
        
    except Exception as e:
        print(f"Error during content optimization: {e}")


if __name__ == "__main__":
    asyncio.run(main())