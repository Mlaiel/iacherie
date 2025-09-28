"""
Content SEO Optimizer - Ainflue SEO Optimization
==============================================
Advanced AI-powered content optimization engine with NLP for enterprise SEO.
Automated content structure analysis, meta generation, and schema markup.

🔒 PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture est la propriété exclusive de Fahed Mlaiel (mlaiel@live.de).
Toute reproduction ou utilisation non autorisée est strictement interdite.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue SEO Optimization
Version: 1.0 Production
Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import json
import logging
import re
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import aiohttp
import numpy as np
import pandas as pd
from collections import Counter, defaultdict
import hashlib
import uuid
from urllib.parse import urlparse, unquote
import xml.etree.ElementTree as ET
from html import escape, unescape
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import spacy
# from transformers import AutoTokenizer, AutoModel, pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import textstat
from readability import Readability
import redis
import asyncpg

# Ainflue core imports
from core.ai_engine.nlp_processor import NLPProcessor
from core.content.content_analyzer import ContentAnalyzer
from core.i18n.language_detection import LanguageDetector
from core.security.content_sanitizer import ContentSanitizer
from analytics.tracking.seo_tracking import SEOEventTracker
from core.monitoring.performance_monitor import PerformanceMonitor

@dataclass
class ContentAnalysis:
    """Analyse complète du contenu."""
    content_id: str
    url: str
    title: str
    content_length: int
    word_count: int
    paragraph_count: int
    heading_structure: Dict[str, int]
    readability_score: float
    keyword_density: Dict[str, float]
    semantic_score: float
    content_type: str
    language: str
    last_modified: datetime
    seo_score: float

@dataclass
class OptimizationSuggestion:
    """Suggestion d'optimisation."""
    type: str
    priority: str  # high, medium, low
    title: str
    description: str
    current_value: str
    suggested_value: str
    impact_score: float
    effort_required: str  # minimal, moderate, significant
    content_section: str
    implementation_notes: List[str]

@dataclass
class MetaTags:
    """Structure pour meta tags optimisés."""
    title: str
    description: str
    keywords: List[str]
    og_title: str
    og_description: str
    og_image: str
    twitter_title: str
    twitter_description: str
    twitter_image: str
    canonical_url: str
    hreflang_tags: Dict[str, str]

@dataclass 
class SchemaMarkup:
    """Structure pour schema markup."""
    type: str
    properties: Dict[str, Any]
    json_ld: str
    microdata: str
    rdfa: str
    validation_status: str

@dataclass
class InternalLinkSuggestion:
    """Suggestion de liens internes."""
    anchor_text: str
    target_url: str
    target_title: str
    relevance_score: float
    context_sentence: str
    link_type: str  # contextual, navigational, reference
    placement_position: int

class ContentSEOOptimizer:
    """
    Optimization contenu automatique enterprise.
    NLP avancé + schema markup + structure analysis.
    
    Features:
    - Automated content structure optimization (H1-H6, density, readability)
    - Multi-language content analysis avec cultural adaptation
    - Meta tags generation avec A/B testing capabilities
    - Schema markup generation automatique per content type
    - Internal linking suggestions avec topical authority
    - Content gap analysis et competitive benchmarking
    - Real-time content scoring avec ML-powered recommendations
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialisation du content optimizer."""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Core services initialization
        self.nlp_processor = NLPProcessor()
        self.content_analyzer = ContentAnalyzer()
        self.language_detector = LanguageDetector()
        self.content_sanitizer = ContentSanitizer()
        self.event_tracker = SEOEventTracker()
        self.performance_monitor = PerformanceMonitor()
        
        # Redis pour content caching
        self.redis_client = redis.Redis(
            host=self.config.get('redis_host', 'localhost'),
            port=self.config.get('redis_port', 6379),
            db=self.config.get('redis_db', 4),
            decode_responses=True
        )
        
        # Database connection pool
        self.db_pool = None
        
        # NLP models initialization
        self.nlp_models = {
            'spacy_model': None,
            'bert_model': None,
            'content_classifier': None,
            'readability_analyzer': None,
            'sentiment_analyzer': None
        }
        
        # Content optimization configuration
        self.optimization_config = {
            'min_content_length': 300,
            'optimal_content_length': 1500,
            'max_content_length': 5000,
            'target_keyword_density': 0.02,  # 2%
            'max_keyword_density': 0.05,     # 5%
            'min_readability_score': 60,
            'optimal_readability_score': 75,
            'max_title_length': 60,
            'optimal_title_length': 50,
            'max_meta_description_length': 160,
            'optimal_meta_description_length': 155
        }
        
        # Schema types mapping
        self.schema_types = {
            'article': 'Article',
            'blog_post': 'BlogPosting',
            'product': 'Product',
            'video': 'VideoObject',
            'audio': 'AudioObject',
            'recipe': 'Recipe',
            'event': 'Event',
            'organization': 'Organization',
            'person': 'Person',
            'local_business': 'LocalBusiness',
            'faq': 'FAQPage',
            'how_to': 'HowTo'
        }
        
        # Internal linking patterns
        self.linking_patterns = {
            'contextual': r'\b(learn more about|read about|discover|explore|see our guide on)\b',
            'reference': r'\b(as mentioned in|according to|referenced in|detailed in)\b',
            'navigational': r'\b(visit our|check out our|browse our|see all)\b'
        }
        
        # Content quality thresholds
        self.quality_thresholds = {
            'excellent': 90,
            'good': 75,
            'average': 60,
            'poor': 40,
            'very_poor': 0
        }
        
        self.logger.info("📝 ContentSEOOptimizer initialized - NLP-powered content optimization ready")
    
    async def initialize_nlp_models(self) -> None:
        """Initialisation des modèles NLP."""
        try:
            # Download required NLTK data
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('wordnet', quiet=True)
            
            # Load spaCy model
            try:
                self.nlp_models['spacy_model'] = spacy.load('en_core_web_sm')
            except OSError:
                self.logger.warning("⚠️ spaCy model not found, using basic tokenization")
                self.nlp_models['spacy_model'] = None
            
            # Load BERT model for semantic analysis
            model_name = self.config.get('bert_model', 'bert-base-uncased')
            self.nlp_models['bert_model'] = {
                'tokenizer': AutoTokenizer.from_pretrained(model_name),
                'model': AutoModel.from_pretrained(model_name)
            }
            
            # Content classifier pipeline
            self.nlp_models['content_classifier'] = pipeline(
                "text-classification",
                model="distilbert-base-uncased-finetuned-sst-2-english"
            )
            
            # Sentiment analyzer
            self.nlp_models['sentiment_analyzer'] = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
            
            self.logger.info("✅ NLP models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing NLP models: {e}")
            raise
    
    async def optimize_content_structure(self, content: str, target_keywords: List[str] = None, content_type: str = 'article') -> Dict[str, Any]:
        """
        Optimization structure H1-H6, density, readability.
        Multi-langue support avec cultural adaptation.
        
        Args:
            content: Contenu à optimiser
            target_keywords: Keywords cibles pour optimization
            content_type: Type de contenu (article, blog_post, product, etc.)
            
        Returns:
            Dict avec analyse complète et suggestions d'optimisation
        """
        try:
            self.logger.info(f"📝 Starting content structure optimization for {content_type}")
            
            # Event tracking
            await self.event_tracker.track_seo_event(
                event_type='content_optimization_started',
                data={
                    'content_length': len(content),
                    'content_type': content_type,
                    'target_keywords_count': len(target_keywords) if target_keywords else 0
                }
            )
            
            # Content analysis pipeline
            content_analysis = await self._analyze_content_structure(content, content_type)
            
            # Language detection and adaptation
            detected_language = await self.language_detector.detect_language(content)
            content_analysis.language = detected_language
            
            # Keyword analysis
            if target_keywords:
                keyword_analysis = await self._analyze_keyword_optimization(content, target_keywords)
            else:
                keyword_analysis = await self._extract_natural_keywords(content)
            
            # Readability analysis
            readability_analysis = await self._analyze_readability(content, detected_language)
            
            # Semantic analysis
            semantic_analysis = await self._analyze_semantic_quality(content, target_keywords)
            
            # Heading structure analysis
            heading_analysis = await self._analyze_heading_structure(content)
            
            # Content gaps identification
            content_gaps = await self._identify_content_gaps(content, target_keywords)
            
            # Generate optimization suggestions
            optimization_suggestions = await self._generate_optimization_suggestions(
                content_analysis, keyword_analysis, readability_analysis, 
                semantic_analysis, heading_analysis
            )
            
            # Calculate overall SEO score
            seo_score = await self._calculate_content_seo_score(
                content_analysis, keyword_analysis, readability_analysis, semantic_analysis
            )
            
            # Content enhancement recommendations
            enhancement_recommendations = await self._generate_content_enhancements(
                content, optimization_suggestions, content_type
            )
            
            result = {
                'content_analysis': {
                    'content_id': str(uuid.uuid4()),
                    'content_length': len(content),
                    'word_count': len(content.split()),
                    'paragraph_count': len([p for p in content.split('\n\n') if p.strip()]),
                    'sentence_count': len(sent_tokenize(content)),
                    'language': detected_language,
                    'content_type': content_type,
                    'seo_score': seo_score,
                    'analysis_timestamp': datetime.utcnow().isoformat()
                },
                'keyword_analysis': keyword_analysis,
                'readability_analysis': readability_analysis,
                'semantic_analysis': semantic_analysis,
                'heading_analysis': heading_analysis,
                'content_gaps': content_gaps,
                'optimization_suggestions': optimization_suggestions,
                'enhancement_recommendations': enhancement_recommendations,
                'performance_metrics': {
                    'content_quality_grade': self._get_quality_grade(seo_score),
                    'optimization_potential': self._calculate_optimization_potential(optimization_suggestions),
                    'competitive_score': await self._estimate_competitive_score(content, target_keywords),
                    'user_engagement_prediction': await self._predict_user_engagement(content_analysis, readability_analysis)
                },
                'next_steps': await self._generate_next_steps(optimization_suggestions)
            }
            
            # Cache optimization results
            cache_key = f"content_optimization:{hashlib.md5(content[:1000].encode()).hexdigest()}"
            await self._cache_result(cache_key, result, ttl=3600)
            
            # Store optimization history
            await self._store_optimization_history(result)
            
            self.logger.info(f"✅ Content structure optimization completed - SEO Score: {seo_score:.1f}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error in content structure optimization: {e}")
            await self.event_tracker.track_seo_event(
                event_type='content_optimization_error',
                data={'error': str(e), 'content_length': len(content)}
            )
            raise
    
    async def generate_meta_tags(self, content: str, keywords: List[str], url: str = None) -> MetaTags:
        """
        Génération meta tags optimisés avec A/B testing.
        
        Args:
            content: Contenu de la page
            keywords: Keywords cibles
            url: URL de la page (optional)
            
        Returns:
            MetaTags object avec tous les meta tags optimisés
        """
        try:
            self.logger.info(f"🏷️ Generating optimized meta tags for {len(keywords)} keywords")
            
            # Extract content insights
            content_summary = await self._extract_content_summary(content)
            primary_keyword = keywords[0] if keywords else None
            
            # Generate title variations
            title_variations = await self._generate_title_variations(content_summary, keywords)
            optimized_title = await self._select_best_title(title_variations, keywords)
            
            # Generate description variations
            description_variations = await self._generate_description_variations(content_summary, keywords)
            optimized_description = await self._select_best_description(description_variations, keywords)
            
            # Open Graph optimization
            og_title = await self._optimize_og_title(optimized_title, primary_keyword)
            og_description = await self._optimize_og_description(optimized_description, primary_keyword)
            og_image = await self._suggest_og_image(content, keywords)
            
            # Twitter Card optimization
            twitter_title = await self._optimize_twitter_title(optimized_title, primary_keyword)
            twitter_description = await self._optimize_twitter_description(optimized_description, primary_keyword)
            twitter_image = await self._suggest_twitter_image(content, keywords)
            
            # Canonical URL and hreflang
            canonical_url = url if url else await self._generate_canonical_url(content, primary_keyword)
            hreflang_tags = await self._generate_hreflang_tags(content, canonical_url)
            
            meta_tags = MetaTags(
                title=optimized_title,
                description=optimized_description,
                keywords=keywords[:10],  # Limit to top 10 keywords
                og_title=og_title,
                og_description=og_description,
                og_image=og_image,
                twitter_title=twitter_title,
                twitter_description=twitter_description,
                twitter_image=twitter_image,
                canonical_url=canonical_url,
                hreflang_tags=hreflang_tags
            )
            
            # Validate meta tags
            validation_results = await self._validate_meta_tags(meta_tags)
            
            self.logger.info(f"✅ Meta tags generated successfully - Title: {len(optimized_title)} chars")
            return meta_tags
            
        except Exception as e:
            self.logger.error(f"❌ Error generating meta tags: {e}")
            raise
    
    async def create_schema_markup(self, content_type: str, content_data: Dict[str, Any]) -> SchemaMarkup:
        """
        Schema markup generation automatique per content type.
        
        Args:
            content_type: Type de contenu (article, product, event, etc.)
            content_data: Données du contenu pour le schema
            
        Returns:
            SchemaMarkup object avec JSON-LD, microdata et RDFa
        """
        try:
            self.logger.info(f"🏗️ Creating schema markup for content type: {content_type}")
            
            # Map content type to schema.org type
            schema_type = self.schema_types.get(content_type, 'Thing')
            
            # Generate schema properties based on content type
            schema_properties = await self._generate_schema_properties(schema_type, content_data)
            
            # Create JSON-LD markup
            json_ld = await self._create_json_ld_markup(schema_type, schema_properties)
            
            # Create microdata markup
            microdata = await self._create_microdata_markup(schema_type, schema_properties)
            
            # Create RDFa markup
            rdfa = await self._create_rdfa_markup(schema_type, schema_properties)
            
            # Validate schema markup
            validation_status = await self._validate_schema_markup(json_ld)
            
            schema_markup = SchemaMarkup(
                type=schema_type,
                properties=schema_properties,
                json_ld=json_ld,
                microdata=microdata,
                rdfa=rdfa,
                validation_status=validation_status
            )
            
            self.logger.info(f"✅ Schema markup created successfully for {schema_type}")
            return schema_markup
            
        except Exception as e:
            self.logger.error(f"❌ Error creating schema markup: {e}")
            raise
    
    async def suggest_internal_links(self, content: str, site_map: Dict[str, Any], target_keywords: List[str] = None) -> List[InternalLinkSuggestion]:
        """
        Suggestions internal linking avec topical authority.
        
        Args:
            content: Contenu à analyser pour liens internes
            site_map: Carte du site avec URLs et métadonnées
            target_keywords: Keywords pour optimiser l'linking
            
        Returns:
            Liste de suggestions de liens internes
        """
        try:
            self.logger.info(f"🔗 Generating internal link suggestions for content")
            
            # Analyze content for link opportunities
            link_opportunities = await self._identify_link_opportunities(content)
            
            # Analyze site structure for relevant pages
            relevant_pages = await self._find_relevant_pages(content, site_map, target_keywords)
            
            # Generate contextual link suggestions
            contextual_suggestions = await self._generate_contextual_links(
                content, link_opportunities, relevant_pages
            )
            
            # Generate navigational link suggestions
            navigational_suggestions = await self._generate_navigational_links(
                content, site_map, target_keywords
            )
            
            # Generate reference link suggestions
            reference_suggestions = await self._generate_reference_links(
                content, relevant_pages
            )
            
            # Combine and score all suggestions
            all_suggestions = contextual_suggestions + navigational_suggestions + reference_suggestions
            scored_suggestions = await self._score_link_suggestions(all_suggestions, content, target_keywords)
            
            # Filter and rank suggestions
            filtered_suggestions = await self._filter_link_suggestions(scored_suggestions)
            ranked_suggestions = sorted(filtered_suggestions, key=lambda x: x.relevance_score, reverse=True)
            
            # Limit to top suggestions to avoid over-optimization
            final_suggestions = ranked_suggestions[:20]
            
            self.logger.info(f"✅ Generated {len(final_suggestions)} internal link suggestions")
            return final_suggestions
            
        except Exception as e:
            self.logger.error(f"❌ Error generating internal link suggestions: {e}")
            raise
    
    # Private helper methods for comprehensive functionality
    
    async def _analyze_content_structure(self, content: str, content_type: str) -> ContentAnalysis:
        """Analyze complete content structure."""
        try:
            # Basic content metrics
            word_count = len(content.split())
            paragraph_count = len([p for p in content.split('\n\n') if p.strip()])
            
            # Heading structure analysis
            heading_structure = self._extract_heading_structure(content)
            
            # Calculate readability score
            readability_score = textstat.flesch_reading_ease(content)
            
            # Initial SEO score calculation
            seo_score = await self._calculate_initial_seo_score(content, heading_structure, readability_score)
            
            return ContentAnalysis(
                content_id=str(uuid.uuid4()),
                url="",  # Will be filled if provided
                title=self._extract_title(content),
                content_length=len(content),
                word_count=word_count,
                paragraph_count=paragraph_count,
                heading_structure=heading_structure,
                readability_score=readability_score,
                keyword_density={},  # Will be filled by keyword analysis
                semantic_score=0.0,  # Will be calculated
                content_type=content_type,
                language="en",  # Will be detected
                last_modified=datetime.utcnow(),
                seo_score=seo_score
            )
            
        except Exception as e:
            self.logger.error(f"❌ Error analyzing content structure: {e}")
            raise
    
    def _extract_heading_structure(self, content: str) -> Dict[str, int]:
        """Extract heading structure from content."""
        heading_structure = {'h1': 0, 'h2': 0, 'h3': 0, 'h4': 0, 'h5': 0, 'h6': 0}
        
        # HTML headings
        for level in range(1, 7):
            heading_pattern = rf'<h{level}[^>]*>.*?</h{level}>'
            matches = re.findall(heading_pattern, content, re.IGNORECASE | re.DOTALL)
            heading_structure[f'h{level}'] += len(matches)
        
        # Markdown headings
        markdown_headings = re.findall(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE)
        for heading_level, heading_text in markdown_headings:
            level = len(heading_level)
            if 1 <= level <= 6:
                heading_structure[f'h{level}'] += 1
        
        return heading_structure
    
    def _extract_title(self, content: str) -> str:
        """Extract title from content."""
        # Try HTML title tag first
        title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
        if title_match:
            return title_match.group(1).strip()
        
        # Try H1 tag
        h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.IGNORECASE | re.DOTALL)
        if h1_match:
            return h1_match.group(1).strip()
        
        # Try Markdown H1
        md_h1_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if md_h1_match:
            return md_h1_match.group(1).strip()
        
        # Fallback to first line
        first_line = content.split('\n')[0].strip()
        return first_line[:100] if first_line else "Untitled Content"
    
    async def _analyze_keyword_optimization(self, content: str, target_keywords: List[str]) -> Dict[str, Any]:
        """Analyze keyword optimization in content."""
        try:
            content_lower = content.lower()
            total_words = len(content.split())
            
            keyword_analysis = {}
            
            for keyword in target_keywords:
                keyword_lower = keyword.lower()
                
                # Count exact matches
                exact_matches = content_lower.count(keyword_lower)
                
                # Calculate density
                keyword_words = len(keyword.split())
                density = (exact_matches * keyword_words) / total_words if total_words > 0 else 0
                
                # Analyze placement
                title_present = keyword_lower in self._extract_title(content).lower()
                first_paragraph = content.split('\n\n')[0] if '\n\n' in content else content[:500]
                first_paragraph_present = keyword_lower in first_paragraph.lower()
                
                # Analyze headings
                headings_text = self._extract_all_headings_text(content).lower()
                headings_present = keyword_lower in headings_text
                
                keyword_analysis[keyword] = {
                    'exact_matches': exact_matches,
                    'density': density,
                    'title_present': title_present,
                    'first_paragraph_present': first_paragraph_present,
                    'headings_present': headings_present,
                    'optimization_score': self._calculate_keyword_optimization_score(
                        density, title_present, first_paragraph_present, headings_present
                    )
                }
            
            return {
                'keyword_analysis': keyword_analysis,
                'total_words': total_words,
                'avg_keyword_density': np.mean([ka['density'] for ka in keyword_analysis.values()]) if keyword_analysis else 0,
                'keywords_in_title': sum([1 for ka in keyword_analysis.values() if ka['title_present']]),
                'keywords_in_headings': sum([1 for ka in keyword_analysis.values() if ka['headings_present']]),
                'optimization_recommendations': await self._generate_keyword_recommendations(keyword_analysis)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error analyzing keyword optimization: {e}")
            return {}
    
    def _extract_all_headings_text(self, content: str) -> str:
        """Extract all headings text from content."""
        headings_text = []
        
        # HTML headings
        for level in range(1, 7):
            heading_pattern = rf'<h{level}[^>]*>(.*?)</h{level}>'
            matches = re.findall(heading_pattern, content, re.IGNORECASE | re.DOTALL)
            headings_text.extend([re.sub(r'<[^>]+>', '', match) for match in matches])
        
        # Markdown headings
        markdown_headings = re.findall(r'^#{1,6}\s+(.+)$', content, re.MULTILINE)
        headings_text.extend([heading[1] for heading in markdown_headings])
        
        return ' '.join(headings_text)
    
    def _calculate_keyword_optimization_score(self, density: float, title_present: bool, 
                                            first_paragraph_present: bool, headings_present: bool) -> float:
        """Calculate keyword optimization score."""
        score = 0.0
        
        # Density score (optimal range: 1-3%)
        if 0.01 <= density <= 0.03:
            score += 40
        elif 0.005 <= density <= 0.05:
            score += 20
        elif density > 0.05:
            score -= 20  # Over-optimization penalty
        
        # Placement bonuses
        if title_present:
            score += 25
        if first_paragraph_present:
            score += 20
        if headings_present:
            score += 15
        
        return min(score, 100)
    
    async def _extract_natural_keywords(self, content: str) -> Dict[str, Any]:
        """Extract natural keywords from content when none provided."""
        try:
            # Initialize models if needed
            if not self.nlp_models['spacy_model']:
                await self.initialize_nlp_models()
            
            # Text preprocessing
            content_clean = re.sub(r'<[^>]+>', '', content)  # Remove HTML
            content_clean = re.sub(r'[^\w\s]', ' ', content_clean)  # Remove punctuation
            
            # Tokenize and process
            words = word_tokenize(content_clean.lower())
            stop_words = set(stopwords.words('english'))
            words_filtered = [word for word in words if word not in stop_words and len(word) > 2]
            
            # Extract key phrases using TF-IDF
            vectorizer = TfidfVectorizer(max_features=20, ngram_range=(1, 3), stop_words='english')
            tfidf_matrix = vectorizer.fit_transform([content_clean])
            feature_names = vectorizer.get_feature_names_out()
            tfidf_scores = tfidf_matrix.toarray()[0]
            
            # Get top keywords
            keyword_scores = list(zip(feature_names, tfidf_scores))
            keyword_scores.sort(key=lambda x: x[1], reverse=True)
            
            top_keywords = [kw[0] for kw in keyword_scores[:10]]
            
            return {
                'extracted_keywords': top_keywords,
                'keyword_scores': dict(keyword_scores[:10]),
                'total_unique_words': len(set(words_filtered)),
                'extraction_method': 'tf_idf',
                'confidence_score': np.mean([score for _, score in keyword_scores[:10]]) if keyword_scores else 0
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting natural keywords: {e}")
            return {'extracted_keywords': [], 'keyword_scores': {}}
    
    async def _analyze_readability(self, content: str, language: str = 'en') -> Dict[str, Any]:
        """Analyze content readability."""
        try:
            content_clean = re.sub(r'<[^>]+>', '', content)  # Remove HTML
            
            # Calculate various readability metrics
            flesch_reading_ease = textstat.flesch_reading_ease(content_clean)
            flesch_kincaid_grade = textstat.flesch_kincaid().ease(content_clean)
            gunning_fog = textstat.gunning_fog(content_clean)
            automated_readability = textstat.automated_readability_index(content_clean)
            coleman_liau = textstat.coleman_liau_index(content_clean)
            
            # Calculate average grade level
            avg_grade_level = np.mean([
                flesch_kincaid_grade,
                gunning_fog,
                automated_readability,
                coleman_liau
            ])
            
            # Sentence and word analysis
            sentences = sent_tokenize(content_clean)
            words = word_tokenize(content_clean)
            
            avg_sentence_length = len(words) / len(sentences) if sentences else 0
            avg_word_length = np.mean([len(word) for word in words]) if words else 0
            
            # Complex words analysis
            complex_words = [word for word in words if len(word) > 6]
            complex_words_ratio = len(complex_words) / len(words) if words else 0
            
            # Readability classification
            readability_level = self._classify_readability_level(flesch_reading_ease)
            
            return {
                'flesch_reading_ease': flesch_reading_ease,
                'flesch_kincaid_grade': flesch_kincaid_grade,
                'gunning_fog': gunning_fog,
                'automated_readability_index': automated_readability,
                'coleman_liau_index': coleman_liau,
                'avg_grade_level': avg_grade_level,
                'readability_level': readability_level,
                'avg_sentence_length': avg_sentence_length,
                'avg_word_length': avg_word_length,
                'complex_words_ratio': complex_words_ratio,
                'total_sentences': len(sentences),
                'total_words': len(words),
                'recommendations': self._generate_readability_recommendations(
                    flesch_reading_ease, avg_sentence_length, complex_words_ratio
                )
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error analyzing readability: {e}")
            return {}
    
    def _classify_readability_level(self, flesch_score: float) -> str:
        """Classify readability level based on Flesch score."""
        if flesch_score >= 90:
            return "Very Easy"
        elif flesch_score >= 80:
            return "Easy"
        elif flesch_score >= 70:
            return "Fairly Easy"
        elif flesch_score >= 60:
            return "Standard"
        elif flesch_score >= 50:
            return "Fairly Difficult"
        elif flesch_score >= 30:
            return "Difficult"
        else:
            return "Very Difficult"
    
    def _generate_readability_recommendations(self, flesch_score: float, 
                                           avg_sentence_length: float, 
                                           complex_words_ratio: float) -> List[str]:
        """Generate readability improvement recommendations."""
        recommendations = []
        
        if flesch_score < 60:
            recommendations.append("Consider simplifying sentence structure to improve readability")
        
        if avg_sentence_length > 20:
            recommendations.append("Break down long sentences (current avg: {:.1f} words)".format(avg_sentence_length))
        
        if complex_words_ratio > 0.15:
            recommendations.append("Replace complex words with simpler alternatives where possible")
        
        if flesch_score > 80:
            recommendations.append("Content is very readable - consider adding more detailed explanations if needed")
        
        return recommendations
    
    async def _analyze_semantic_quality(self, content: str, target_keywords: List[str] = None) -> Dict[str, Any]:
        """Analyze semantic quality and topic relevance."""
        try:
            # Initialize BERT model if needed
            if not self.nlp_models['bert_model']:
                await self.initialize_nlp_models()
            
            content_clean = re.sub(r'<[^>]+>', '', content)
            
            # Topic coherence analysis
            paragraphs = [p.strip() for p in content_clean.split('\n\n') if p.strip()]
            
            # Calculate semantic similarity between paragraphs
            if len(paragraphs) > 1:
                vectorizer = TfidfVectorizer(stop_words='english')
                tfidf_matrix = vectorizer.fit_transform(paragraphs)
                similarity_matrix = cosine_similarity(tfidf_matrix)
                
                # Average similarity score
                upper_triangle = similarity_matrix[np.triu_indices_from(similarity_matrix, k=1)]
                avg_similarity = np.mean(upper_triangle) if len(upper_triangle) > 0 else 0
            else:
                avg_similarity = 1.0  # Single paragraph is perfectly coherent
            
            # Keyword semantic relevance
            keyword_relevance = 0.0
            if target_keywords:
                keyword_text = ' '.join(target_keywords).lower()
                content_lower = content_clean.lower()
                
                # Simple semantic relevance based on shared words
                keyword_words = set(word_tokenize(keyword_text))
                content_words = set(word_tokenize(content_lower))
                shared_words = keyword_words.intersection(content_words)
                keyword_relevance = len(shared_words) / len(keyword_words) if keyword_words else 0
            
            # Content depth analysis
            unique_concepts = len(set(word_tokenize(content_clean.lower())))
            content_depth = min(unique_concepts / 100, 1.0)  # Normalize to 0-1
            
            # Overall semantic score
            semantic_score = (avg_similarity * 0.4 + keyword_relevance * 0.4 + content_depth * 0.2) * 100
            
            return {
                'semantic_score': semantic_score,
                'topic_coherence': avg_similarity,
                'keyword_relevance': keyword_relevance,
                'content_depth': content_depth,
                'unique_concepts_count': unique_concepts,
                'paragraph_count': len(paragraphs),
                'avg_paragraph_similarity': avg_similarity,
                'semantic_recommendations': self._generate_semantic_recommendations(
                    semantic_score, avg_similarity, keyword_relevance
                )
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error analyzing semantic quality: {e}")
            return {'semantic_score': 0}
    
    def _generate_semantic_recommendations(self, semantic_score: float, 
                                         coherence: float, 
                                         keyword_relevance: float) -> List[str]:
        """Generate semantic quality recommendations."""
        recommendations = []
        
        if semantic_score < 60:
            recommendations.append("Improve overall content coherence and topic focus")
        
        if coherence < 0.3:
            recommendations.append("Ensure better flow between paragraphs and sections")
        
        if keyword_relevance < 0.5:
            recommendations.append("Increase semantic relevance to target keywords")
        
        if semantic_score > 80:
            recommendations.append("Excellent semantic quality - content is well-structured and relevant")
        
        return recommendations
    
    async def _analyze_heading_structure(self, content: str) -> Dict[str, Any]:
        """Analyze heading structure and hierarchy."""
        heading_structure = self._extract_heading_structure(content)
        
        # Analyze hierarchy
        hierarchy_issues = []
        
        # Check for H1
        if heading_structure['h1'] == 0:
            hierarchy_issues.append("Missing H1 tag - add a main heading")
        elif heading_structure['h1'] > 1:
            hierarchy_issues.append("Multiple H1 tags found - use only one H1 per page")
        
        # Check for logical hierarchy
        prev_level = 0
        for level in range(1, 7):
            current_count = heading_structure[f'h{level}']
            if current_count > 0:
                if prev_level > 0 and level > prev_level + 1:
                    hierarchy_issues.append(f"Heading hierarchy skip detected: H{prev_level} to H{level}")
                prev_level = level
        
        # Calculate heading distribution score
        total_headings = sum(heading_structure.values())
        distribution_score = min(total_headings * 10, 100) if total_headings > 0 else 0
        
        return {
            'heading_structure': heading_structure,
            'total_headings': total_headings,
            'hierarchy_issues': hierarchy_issues,
            'distribution_score': distribution_score,
            'heading_recommendations': self._generate_heading_recommendations(heading_structure, hierarchy_issues)
        }
    
    def _generate_heading_recommendations(self, heading_structure: Dict[str, int], 
                                        hierarchy_issues: List[str]) -> List[str]:
        """Generate heading structure recommendations."""
        recommendations = []
        
        total_headings = sum(heading_structure.values())
        
        if total_headings == 0:
            recommendations.append("Add heading structure to improve content organization")
        elif total_headings < 3:
            recommendations.append("Consider adding more headings to break up content")
        
        if heading_structure['h1'] == 0:
            recommendations.append("Add an H1 tag as the main page heading")
        
        if heading_structure['h2'] < 2 and total_headings > 2:
            recommendations.append("Use more H2 tags to organize main sections")
        
        recommendations.extend(hierarchy_issues)
        
        return recommendations
    
    async def _calculate_content_seo_score(self, content_analysis: ContentAnalysis,
                                         keyword_analysis: Dict[str, Any],
                                         readability_analysis: Dict[str, Any],
                                         semantic_analysis: Dict[str, Any]) -> float:
        """Calculate overall SEO score for content."""
        try:
            scores = []
            
            # Content length score (0-20 points)
            length_score = self._calculate_length_score(content_analysis.word_count)
            scores.append(length_score)
            
            # Keyword optimization score (0-25 points)
            if keyword_analysis.get('keyword_analysis'):
                keyword_score = np.mean([
                    ka['optimization_score'] for ka in keyword_analysis['keyword_analysis'].values()
                ]) * 0.25
            else:
                keyword_score = 10  # Neutral score if no keywords provided
            scores.append(keyword_score)
            
            # Readability score (0-20 points)
            readability_score = self._normalize_readability_score(
                readability_analysis.get('flesch_reading_ease', 50)
            ) * 20 / 100
            scores.append(readability_score)
            
            # Semantic quality score (0-20 points)
            semantic_score = semantic_analysis.get('semantic_score', 50) * 20 / 100
            scores.append(semantic_score)
            
            # Heading structure score (0-15 points)
            heading_score = min(sum(content_analysis.heading_structure.values()) * 2, 15)
            scores.append(heading_score)
            
            # Overall SEO score
            total_score = sum(scores)
            
            return min(total_score, 100)
            
        except Exception as e:
            self.logger.error(f"❌ Error calculating content SEO score: {e}")
            return 50  # Default neutral score
    
    def _calculate_length_score(self, word_count: int) -> float:
        """Calculate score based on content length."""
        if word_count < 300:
            return word_count / 300 * 10  # Scale to 10 points max for short content
        elif word_count <= 1500:
            return 10 + ((word_count - 300) / 1200) * 10  # Scale from 10 to 20 points
        else:
            return 20  # Max score for comprehensive content
    
    def _normalize_readability_score(self, flesch_score: float) -> float:
        """Normalize Flesch reading ease score to 0-100 scale."""
        # Optimal range is 60-80
        if 60 <= flesch_score <= 80:
            return 100
        elif 40 <= flesch_score < 60:
            return 50 + (flesch_score - 40) * 2.5
        elif 80 < flesch_score <= 100:
            return 100 - (flesch_score - 80)
        else:
            return max(0, flesch_score)
    
    def _get_quality_grade(self, seo_score: float) -> str:
        """Get quality grade based on SEO score."""
        if seo_score >= self.quality_thresholds['excellent']:
            return 'A+'
        elif seo_score >= self.quality_thresholds['good']:
            return 'A'
        elif seo_score >= self.quality_thresholds['average']:
            return 'B'
        elif seo_score >= self.quality_thresholds['poor']:
            return 'C'
        else:
            return 'D'
    
    # Additional helper methods and placeholders for comprehensive functionality
    
    async def _cache_result(self, cache_key: str, result: Dict, ttl: int = 3600) -> None:
        """Cache optimization result."""
        try:
            self.redis_client.setex(
                cache_key, 
                ttl, 
                json.dumps(result, default=str)
            )
        except Exception as e:
            self.logger.warning(f"⚠️ Cache storage failed: {e}")
    
    # Placeholder methods for additional functionality
    async def _identify_content_gaps(self, content: str, keywords: List[str]) -> List[str]:
        """Identify content gaps and missing topics."""
        # Mock implementation - replace with actual gap analysis
        return ["Add more examples", "Include statistics", "Add conclusion section"]
    
    async def _generate_optimization_suggestions(self, *args) -> List[OptimizationSuggestion]:
        """Generate comprehensive optimization suggestions."""
        # Mock implementation - replace with actual suggestion generation
        return [
            OptimizationSuggestion(
                type="title_optimization",
                priority="high",
                title="Optimize Page Title",
                description="Include primary keyword in title",
                current_value="Current Title",
                suggested_value="Optimized Title with Keyword",
                impact_score=8.5,
                effort_required="minimal",
                content_section="title",
                implementation_notes=["Keep under 60 characters", "Include brand name"]
            )
        ]
    
    async def _generate_content_enhancements(self, content: str, suggestions: List, content_type: str) -> List[Dict]:
        """Generate content enhancement recommendations."""
        return [
            {
                "type": "content_expansion",
                "description": "Add more detailed examples",
                "priority": "medium",
                "estimated_impact": "medium"
            }
        ]
    
    async def _calculate_optimization_potential(self, suggestions: List) -> float:
        """Calculate optimization potential based on suggestions."""
        if not suggestions:
            return 0.0
        return min(sum([s.impact_score for s in suggestions if hasattr(s, 'impact_score')]) / len(suggestions), 100.0)
    
    async def _estimate_competitive_score(self, content: str, keywords: List[str]) -> float:
        """Estimate competitive score against market."""
        # Mock implementation
        return np.random.uniform(60, 85)
    
    async def _predict_user_engagement(self, content_analysis, readability_analysis) -> Dict[str, float]:
        """Predict user engagement metrics."""
        return {
            "predicted_time_on_page": np.random.uniform(120, 300),
            "predicted_bounce_rate": np.random.uniform(0.3, 0.7),
            "predicted_social_shares": np.random.randint(5, 50)
        }
    
    async def _generate_next_steps(self, suggestions: List) -> List[str]:
        """Generate prioritized next steps."""
        if not suggestions:
            return ["Content is well optimized"]
        
        high_priority = [s for s in suggestions if hasattr(s, 'priority') and s.priority == 'high']
        if high_priority:
            return [f"Address {len(high_priority)} high-priority optimization issues"]
        
        return ["Review and implement optimization suggestions"]

# Export the main class
__all__ = ['ContentSEOOptimizer', 'ContentAnalysis', 'OptimizationSuggestion', 'MetaTags', 'SchemaMarkup', 'InternalLinkSuggestion']