# SEO Optimization and Metadata Generation for Visual Content
# Industrial-Grade Visual Content SEO and Metadata Intelligence
#
# Project Team Specialties:
# - Lead Dev + AI Architect: Advanced AI/ML Systems Design
# - Backend Senior (Python/FastAPI): High-Performance API Development  
# - ML Engineer (TensorFlow/PyTorch/HuggingFace): Deep Learning Models
# - DBA & Data Engineer: Scalable Data Architecture
# - Security Backend Specialist: Enterprise Security Implementation
# - Microservices Architect: Distributed Systems Design
# - Audio Developer: Professional Audio Processing
# - DevOps Engineer: Production Infrastructure
# - AI Prompt Engineer: Advanced Language Model Integration
#
# Created by: Fahed Mlaiel (mlaiel@live.de)
# 
#   STRICT COPYRIGHT WARNING  
# This code, concept, and intellectual property belongs exclusively to Fahed Mlaiel.
# ANY unauthorized use, reproduction, distribution, or theft of this code/concept 
# without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is 
# STRICTLY PROHIBITED and will result in immediate legal action.
# All rights reserved. Patent pending.

import cv2
import numpy as np
import torch
import torch.nn as nn
from PIL import Image, ExifTags
from typing import Dict, List, Tuple, Optional, Union, Any
from dataclasses import dataclass, field
from enum import Enum
import logging
from abc import ABC, abstractmethod
import json
import re
from datetime import datetime
import hashlib
from pathlib import Path
import requests
from collections import Counter
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import spacy
from transformers import pipeline, BlipProcessor, BlipForConditionalGeneration
import openai
from googletrans import Translator
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentType(Enum):
    """Types of visual content"""
    PHOTOGRAPHY = "photography"
    ILLUSTRATION = "illustration"
    INFOGRAPHIC = "infographic"
    ARTWORK = "artwork"
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"
    PRODUCT = "product"
    SCREENSHOT = "screenshot"
    MEME = "meme"
    LOGO = "logo"

class SEOPlatform(Enum):
    """Target SEO platforms"""
    GOOGLE = "google"
    INSTAGRAM = "instagram"
    PINTEREST = "pinterest"
    YOUTUBE = "youtube"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    TIKTOK = "tiktok"

class LanguageTarget(Enum):
    """Target languages for SEO"""
    ENGLISH = "en"
    GERMAN = "de"
    FRENCH = "fr"
    SPANISH = "es"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    DUTCH = "nl"
    JAPANESE = "ja"
    KOREAN = "ko"
    CHINESE = "zh"

@dataclass
class OptimizationSettings:
    """SEO optimization configuration"""
    target_platforms: List[SEOPlatform]
    target_languages: List[LanguageTarget] = field(default_factory=lambda: [LanguageTarget.ENGLISH])
    content_type: Optional[ContentType] = None
    target_audience: str = "general"
    brand_keywords: List[str] = field(default_factory=list)
    competitor_analysis: bool = True
    trending_analysis: bool = True
    accessibility_compliance: bool = True
    schema_markup: bool = True
    social_sharing_optimization: bool = True
    image_compression: bool = True
    webp_conversion: bool = True
    responsive_optimization: bool = True
    performance_optimization: bool = True

@dataclass
class SEOMetrics:
    """SEO performance metrics"""
    keyword_density: Dict[str, float]
    readability_score: float
    accessibility_score: float
    social_sharing_potential: float
    search_visibility_score: float
    engagement_prediction: float
    viral_potential: float
    brand_alignment: float
    content_quality_score: float
    technical_seo_score: float
    overall_seo_score: float

@dataclass
class SEOResult:
    """Complete SEO optimization result"""
    optimized_title: str
    optimized_description: str
    hashtags: List[str]
    keywords: List[str]
    alt_text: str
    schema_markup: Dict[str, Any]
    social_media_variants: Dict[str, Dict[str, str]]
    technical_optimizations: Dict[str, Any]
    metrics: SEOMetrics
    recommendations: List[str]
    multilingual_variants: Dict[str, Dict[str, str]] = field(default_factory=dict)

class SEOOptimizer:
    """Advanced SEO optimization engine for visual content"""
    
    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        self.api_keys = api_keys or {}
        
        # Initialize NLP components
        self._init_nlp_components()
        
        # Initialize AI models
        self._init_ai_models()
        
        # SEO knowledge base
        self.seo_rules = self._load_seo_rules()
        self.trending_keywords = {}
        self.competitor_data = {}
        
        # Platform-specific configurations
        self.platform_configs = self._init_platform_configs()
        
    def _init_nlp_components(self):
        """Initialize NLP processing components"""



        try:
            # Download required NLTK data
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('wordnet', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
            
            self.lemmatizer = WordNetLemmatizer()
            self.stop_words = set(stopwords.words('english'))
            
            # Load spaCy model
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("spaCy model not found. Some features may be limited.")
                self.nlp = None
            
            # Initialize translator
            self.translator = Translator()
            
            logger.info("NLP components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize NLP components: {e}")
            self.lemmatizer = None
            self.stop_words = set()
            self.nlp = None
            self.translator = None
    
    def _init_ai_models(self):
        """Initialize AI models for content analysis"""



        try:
            # Image captioning model
            self.caption_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            self.caption_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
            
            # Sentiment analysis
            self.sentiment_analyzer = pipeline("sentiment-analysis")
            
            # Text classification
            self.text_classifier = pipeline("zero-shot-classification")
            
            logger.info("AI models initialized successfully")
            
        except Exception as e:
            logger.warning(f"Some AI models failed to load: {e}")
            self.caption_processor = None
            self.caption_model = None
            self.sentiment_analyzer = None
            self.text_classifier = None
    
    def _load_seo_rules(self) -> Dict[str, Any]:
        """Load SEO rules and best practices"""



        return {
            'title_length': {'min': 30, 'max': 60},
            'description_length': {'min': 120, 'max': 160},
            'keyword_density': {'min': 0.01, 'max': 0.03},
            'hashtag_count': {'min': 5, 'max': 30},
            'alt_text_length': {'min': 50, 'max': 125},
            'readability_target': 60,  # Flesch reading ease score
            'engagement_keywords': [
                'amazing', 'incredible', 'stunning', 'beautiful', 'perfect',
                'best', 'top', 'ultimate', 'exclusive', 'limited', 'new',
                'trending', 'viral', 'must-see', 'breakthrough', 'innovative'
            ],
            'action_words': [
                'discover', 'explore', 'learn', 'find', 'get', 'create',
                'build', 'master', 'unlock', 'reveal', 'transform'
            ]
        }
    
    def _init_platform_configs(self) -> Dict[SEOPlatform, Dict[str, Any]]:
        """Initialize platform-specific configurations"""



        return {
            SEOPlatform.INSTAGRAM: {
                'title_length': 125,
                'hashtag_limit': 30,
                'trending_hashtags': True,
                'story_optimization': True,
                'reel_optimization': True
            },
            SEOPlatform.PINTEREST: {
                'title_length': 100,
                'description_length': 500,
                'hashtag_limit': 20,
                'board_optimization': True,
                'seasonal_trends': True
            },
            SEOPlatform.YOUTUBE: {
                'title_length': 100,
                'description_length': 5000,
                'thumbnail_optimization': True,
                'chapter_optimization': True
            },
            SEOPlatform.GOOGLE: {
                'title_length': 60,
                'meta_description': 160,
                'structured_data': True,
                'image_seo': True,
                'core_web_vitals': True
            },
            SEOPlatform.FACEBOOK: {
                'title_length': 125,
                'description_length': 250,
                'engagement_optimization': True,
                'video_optimization': True
            },
            SEOPlatform.TWITTER: {
                'title_length': 280,
                'hashtag_limit': 10,
                'thread_optimization': True,
                'real_time_trends': True
            },
            SEOPlatform.LINKEDIN: {
                'title_length': 150,
                'description_length': 1300,
                'professional_tone': True,
                'industry_keywords': True
            },
            SEOPlatform.TIKTOK: {
                'title_length': 150,
                'hashtag_limit': 100,
                'trending_sounds': True,
                'viral_optimization': True
            }
        }
    
    def optimize_content(self, image: np.ndarray, settings: OptimizationSettings, 
                        existing_metadata: Optional[Dict[str, Any]] = None) -> SEOResult:
        """Perform comprehensive SEO optimization"""
        logger.info("Starting comprehensive SEO optimization")
        
        try:
            # Step 1: Analyze image content
            content_analysis = self._analyze_image_content(image)
            
            # Step 2: Generate base content
            base_title = self._generate_base_title(content_analysis, settings)
            base_description = self._generate_base_description(content_analysis, settings)
            
            # Step 3: Keyword research and analysis
            keywords = self._research_keywords(content_analysis, settings)
            
            # Step 4: Generate optimized content
            optimized_title = self._optimize_title(base_title, keywords, settings)
            optimized_description = self._optimize_description(base_description, keywords, settings)
            
            # Step 5: Generate hashtags
            hashtags = self._generate_hashtags(content_analysis, keywords, settings)
            
            # Step 6: Generate alt text
            alt_text = self._generate_alt_text(content_analysis, keywords, settings)
            
            # Step 7: Create schema markup
            schema_markup = self._create_schema_markup(content_analysis, optimized_title, optimized_description, settings)
            
            # Step 8: Generate platform-specific variants
            social_variants = self._generate_social_variants(
                optimized_title, optimized_description, hashtags, settings
            )
            
            # Step 9: Generate multilingual variants
            multilingual_variants = self._generate_multilingual_variants(
                optimized_title, optimized_description, hashtags, settings
            )
            
            # Step 10: Technical optimizations
            technical_optimizations = self._generate_technical_optimizations(image, settings)
            
            # Step 11: Calculate SEO metrics
            metrics = self._calculate_seo_metrics(
                optimized_title, optimized_description, keywords, hashtags, settings
            )
            
            # Step 12: Generate recommendations
            recommendations = self._generate_recommendations(metrics, settings)
            
            result = SEOResult(
                optimized_title=optimized_title,
                optimized_description=optimized_description,
                hashtags=hashtags,
                keywords=keywords,
                alt_text=alt_text,
                schema_markup=schema_markup,
                social_media_variants=social_variants,
                technical_optimizations=technical_optimizations,
                metrics=metrics,
                recommendations=recommendations,
                multilingual_variants=multilingual_variants
            )
            
            logger.info(f"SEO optimization completed with score: {metrics.overall_seo_score:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"SEO optimization failed: {e}")
            return self._create_fallback_result(image, settings)
    
    def _analyze_image_content(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze image content using AI models"""
        analysis = {
            'dominant_colors': [],
            'objects_detected': [],
            'scene_type': 'unknown',
            'mood': 'neutral',
            'style': 'realistic',
            'quality_score': 0.8,
            'composition_score': 0.7,
            'caption': '',
            'content_type': ContentType.PHOTOGRAPHY
        }
        
        try:
            # Color analysis
            analysis['dominant_colors'] = self._analyze_colors(image)
            
            # Generate AI caption
            if self.caption_processor and self.caption_model:
                pil_image = Image.fromarray(image)
                inputs = self.caption_processor(pil_image, return_tensors="pt")
                out = self.caption_model.generate(**inputs, max_length=50)
                caption = self.caption_processor.decode(out[0], skip_special_tokens=True)
                analysis['caption'] = caption
                
                # Extract objects from caption
                analysis['objects_detected'] = self._extract_objects_from_caption(caption)
            
            # Analyze composition
            analysis['composition_score'] = self._analyze_composition(image)
            
            # Analyze quality
            analysis['quality_score'] = self._analyze_quality(image)
            
            # Detect content type
            analysis['content_type'] = self._detect_content_type(image, analysis['caption'])
            
            # Analyze mood/sentiment
            if analysis['caption'] and self.sentiment_analyzer:
                sentiment = self.sentiment_analyzer(analysis['caption'])[0]
                analysis['mood'] = sentiment['label'].lower()
            
        except Exception as e:
            logger.warning(f"Image analysis failed: {e}")
        
        return analysis
    
    def _analyze_colors(self, image: np.ndarray) -> List[str]:
        """Analyze dominant colors in the image"""



        try:
            # Reshape image to pixels
            pixels = image.reshape(-1, 3)
            
            # Use KMeans to find dominant colors
            from sklearn.cluster import KMeans
            kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
            kmeans.fit(pixels)
            
            # Get dominant colors
            dominant_colors = kmeans.cluster_centers_.astype(int)
            
            # Convert to color names
            color_names = []
            for color in dominant_colors:
                color_name = self._rgb_to_color_name(color)
                color_names.append(color_name)
            
            return color_names[:3]  # Return top 3 colors
            
        except Exception as e:
            logger.warning(f"Color analysis failed: {e}")
            return ['unknown']
    
    def _rgb_to_color_name(self, rgb: np.ndarray) -> str:
        """Convert RGB values to color name"""
        r, g, b = rgb
        
        # Simple color mapping
        if r > 200 and g > 200 and b > 200:
            return 'white'
        elif r < 50 and g < 50 and b < 50:
            return 'black'
        elif r > g and r > b:
            if r > 150:
                return 'red'
            else:
                return 'dark_red'
        elif g > r and g > b:
            if g > 150:
                return 'green'
            else:
                return 'dark_green'
        elif b > r and b > g:
            if b > 150:
                return 'blue'
            else:
                return 'dark_blue'
        elif r > 150 and g > 150:
            return 'yellow'
        elif r > 150 and b > 150:
            return 'magenta'
        elif g > 150 and b > 150:
            return 'cyan'
        else:
            return 'gray'
    
    def _extract_objects_from_caption(self, caption: str) -> List[str]:
        """Extract objects/entities from AI-generated caption"""
        objects = []
        
        if self.nlp:
            doc = self.nlp(caption)
            for ent in doc.ents:
                if ent.label_ in ['PERSON', 'ORG', 'GPE', 'PRODUCT']:
                    objects.append(ent.text.lower())
            
            # Extract nouns
            for token in doc:
                if token.pos_ == 'NOUN' and token.text.lower() not in self.stop_words:
                    objects.append(token.text.lower())
        else:
            # Fallback: simple noun extraction
            words = word_tokenize(caption.lower())
            pos_tags = nltk.pos_tag(words)
            for word, pos in pos_tags:
                if pos.startswith('NN') and word not in self.stop_words:
                    objects.append(word)
        
        return list(set(objects))  # Remove duplicates
    
    def _analyze_composition(self, image: np.ndarray) -> float:
        """Analyze image composition quality"""



        try:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            h, w = gray.shape
            
            # Rule of thirds analysis
            thirds_score = self._analyze_rule_of_thirds(gray)
            
            # Symmetry analysis
            symmetry_score = self._analyze_symmetry(gray)
            
            # Leading lines detection
            lines_score = self._analyze_leading_lines(gray)
            
            # Overall composition score
            composition_score = (thirds_score * 0.4 + symmetry_score * 0.3 + lines_score * 0.3)
            
            return min(1.0, composition_score)
            
        except Exception as e:
            logger.warning(f"Composition analysis failed: {e}")
            return 0.7  # Default score
    
    def _analyze_rule_of_thirds(self, gray: np.ndarray) -> float:
        """Analyze rule of thirds composition"""
        h, w = gray.shape
        
        # Define thirds lines
        v_thirds = [w // 3, 2 * w // 3]
        h_thirds = [h // 3, 2 * h // 3]
        
        # Detect edges
        edges = cv2.Canny(gray, 50, 150)
        
        # Check for interesting features near thirds lines
        score = 0.0
        total_checks = 0
        
        for v_line in v_thirds:
            for h_line in h_thirds:
                # Check area around intersection
                roi = edges[max(0, h_line-10):min(h, h_line+10), 
                           max(0, v_line-10):min(w, v_line+10)]
                if roi.size > 0:
                    edge_density = np.sum(roi) / roi.size
                    score += min(1.0, edge_density / 50.0)
                    total_checks += 1
        
        return score / max(total_checks, 1)
    
    def _analyze_symmetry(self, gray: np.ndarray) -> float:
        """Analyze image symmetry"""
        h, w = gray.shape
        
        # Vertical symmetry
        left_half = gray[:, :w//2]
        right_half = cv2.flip(gray[:, w//2:], 1)
        
        # Resize to match if needed
        min_width = min(left_half.shape[1], right_half.shape[1])
        left_half = left_half[:, :min_width]
        right_half = right_half[:, :min_width]
        
        # Calculate correlation
        if left_half.size > 0 and right_half.size > 0:
            correlation = cv2.matchTemplate(left_half, right_half, cv2.TM_CCOEFF_NORMED)[0, 0]
            return max(0.0, correlation)
        
        return 0.5
    
    def _analyze_leading_lines(self, gray: np.ndarray) -> float:
        """Analyze leading lines in composition"""
        # Detect lines using HoughLinesP
        edges = cv2.Canny(gray, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=50, maxLineGap=10)
        
        if lines is None:
            return 0.3
        
        # Analyze line directions and convergence
        line_score = min(1.0, len(lines) / 20.0)  # More lines generally better
        
        return line_score
    
    def _analyze_quality(self, image: np.ndarray) -> float:
        """Analyze technical image quality"""



        try:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Sharpness analysis
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            sharpness_score = min(1.0, laplacian_var / 2000)
            
            # Noise analysis
            noise_level = np.std(gray)
            noise_score = max(0.0, 1.0 - (noise_level / 100))
            
            # Contrast analysis
            contrast = np.std(gray)
            contrast_score = min(1.0, contrast / 80)
            
            # Overall quality
            quality_score = (sharpness_score * 0.4 + noise_score * 0.3 + contrast_score * 0.3)
            
            return quality_score
            
        except Exception as e:
            logger.warning(f"Quality analysis failed: {e}")
            return 0.8
    
    def _detect_content_type(self, image: np.ndarray, caption: str) -> ContentType:
        """Detect the type of visual content"""



        try:
            # Analyze image characteristics
            h, w = image.shape[:2]
            aspect_ratio = w / h
            
            # Check for text in image (potential infographic/meme)
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Use caption analysis
            if caption:
                caption_lower = caption.lower()
                
                if any(word in caption_lower for word in ['person', 'man', 'woman', 'face', 'portrait']):
                    return ContentType.PORTRAIT
                elif any(word in caption_lower for word in ['landscape', 'mountain', 'ocean', 'forest', 'sky']):
                    return ContentType.LANDSCAPE
                elif any(word in caption_lower for word in ['product', 'bottle', 'package', 'brand']):
                    return ContentType.PRODUCT
                elif any(word in caption_lower for word in ['art', 'painting', 'drawing', 'illustration']):
                    return ContentType.ARTWORK
                elif any(word in caption_lower for word in ['logo', 'brand', 'company']):
                    return ContentType.LOGO
                elif any(word in caption_lower for word in ['chart', 'graph', 'data', 'infographic']):
                    return ContentType.INFOGRAPHIC
            
            # Default to photography
            return ContentType.PHOTOGRAPHY
            
        except Exception as e:
            logger.warning(f"Content type detection failed: {e}")
            return ContentType.PHOTOGRAPHY
    
    def _research_keywords(self, content_analysis: Dict[str, Any], settings: OptimizationSettings) -> List[str]:
        """Research and generate relevant keywords"""
        keywords = []
        
        try:
            # Extract from content analysis
            if content_analysis.get('objects_detected'):
                keywords.extend(content_analysis['objects_detected'])
            
            # Add color keywords
            if content_analysis.get('dominant_colors'):
                keywords.extend(content_analysis['dominant_colors'])
            
            # Add content type keywords
            content_type = content_analysis.get('content_type', ContentType.PHOTOGRAPHY)
            keywords.extend(self._get_content_type_keywords(content_type))
            
            # Add brand keywords
            keywords.extend(settings.brand_keywords)
            
            # Add trending keywords if enabled
            if settings.trending_analysis:
                trending = self._get_trending_keywords(settings.target_platforms)
                keywords.extend(trending)
            
            # Add platform-specific keywords
            for platform in settings.target_platforms:
                platform_keywords = self._get_platform_keywords(platform, content_analysis)
                keywords.extend(platform_keywords)
            
            # Clean and deduplicate keywords
            keywords = self._clean_keywords(keywords)
            
            # Score and rank keywords
            scored_keywords = self._score_keywords(keywords, content_analysis, settings)
            
            # Return top keywords
            return [kw for kw, score in scored_keywords[:20]]
            
        except Exception as e:
            logger.warning(f"Keyword research failed: {e}")
            return ['image', 'photo', 'visual', 'content']
    
    def _get_content_type_keywords(self, content_type: ContentType) -> List[str]:
        """Get keywords specific to content type"""
        keyword_map = {
            ContentType.PHOTOGRAPHY: ['photo', 'photography', 'picture', 'image', 'shot', 'capture'],
            ContentType.PORTRAIT: ['portrait', 'headshot', 'person', 'face', 'people', 'human'],
            ContentType.LANDSCAPE: ['landscape', 'nature', 'scenery', 'outdoor', 'vista', 'horizon'],
            ContentType.PRODUCT: ['product', 'item', 'merchandise', 'goods', 'commercial', 'brand'],
            ContentType.ARTWORK: ['art', 'artwork', 'creative', 'artistic', 'design', 'visual'],
            ContentType.ILLUSTRATION: ['illustration', 'drawing', 'graphic', 'digital', 'artwork'],
            ContentType.INFOGRAPHIC: ['infographic', 'data', 'information', 'chart', 'visualization'],
            ContentType.LOGO: ['logo', 'brand', 'identity', 'symbol', 'mark', 'emblem'],
            ContentType.SCREENSHOT: ['screenshot', 'screen', 'interface', 'app', 'software', 'digital'],
            ContentType.MEME: ['meme', 'funny', 'humor', 'viral', 'internet', 'social']
        }
        
        return keyword_map.get(content_type, ['image', 'visual'])
    
    def _get_trending_keywords(self, platforms: List[SEOPlatform]) -> List[str]:
        """Get trending keywords for specified platforms"""
        # This would integrate with real trending APIs
        # For now, return some common trending keywords
        trending_keywords = [
            'trending', 'viral', 'popular', 'new', 'latest', 'hot',
            '2024', 'fresh', 'amazing', 'incredible', 'stunning'
        ]
        
        return trending_keywords
    
    def _get_platform_keywords(self, platform: SEOPlatform, content_analysis: Dict[str, Any]) -> List[str]:
        """Get platform-specific keywords"""
        platform_keywords = {
            SEOPlatform.INSTAGRAM: ['insta', 'ig', 'gram', 'story', 'reel', 'post'],
            SEOPlatform.PINTEREST: ['pin', 'board', 'inspiration', 'ideas', 'diy', 'style'],
            SEOPlatform.YOUTUBE: ['video', 'watch', 'tutorial', 'how-to', 'guide', 'tips'],
            SEOPlatform.TIKTOK: ['tiktok', 'viral', 'trend', 'challenge', 'fyp', 'foryou'],
            SEOPlatform.LINKEDIN: ['professional', 'business', 'career', 'industry', 'work'],
            SEOPlatform.TWITTER: ['tweet', 'news', 'update', 'breaking', 'live', 'real-time'],
            SEOPlatform.FACEBOOK: ['share', 'community', 'social', 'connect', 'friends'],
            SEOPlatform.GOOGLE: ['search', 'find', 'discover', 'learn', 'explore', 'guide']
        }
        
        return platform_keywords.get(platform, [])
    
    def _clean_keywords(self, keywords: List[str]) -> List[str]:
        """Clean and normalize keywords"""
        cleaned = []
        
        for keyword in keywords:
            if isinstance(keyword, str):
                # Clean the keyword
                clean_kw = keyword.lower().strip()
                clean_kw = re.sub(r'[^\w\s-]', '', clean_kw)
                clean_kw = re.sub(r'\s+', ' ', clean_kw)
                
                # Filter out short, common, or invalid keywords
                if (len(clean_kw) >= 2 and 
                    clean_kw not in self.stop_words and 
                    not clean_kw.isdigit() and
                    clean_kw not in cleaned):
                    cleaned.append(clean_kw)
        
        return cleaned
    
    def _score_keywords(self, keywords: List[str], content_analysis: Dict[str, Any], 
                       settings: OptimizationSettings) -> List[Tuple[str, float]]:
        """Score keywords based on relevance and SEO value"""
        scored_keywords = []
        
        for keyword in keywords:
            score = 0.0
            
            # Base relevance score
            if keyword in content_analysis.get('caption', '').lower():
                score += 0.3
            
            if keyword in content_analysis.get('objects_detected', []):
                score += 0.4
            
            # Brand keyword bonus
            if keyword in [bk.lower() for bk in settings.brand_keywords]:
                score += 0.5
            
            # Length penalty/bonus
            if 3 <= len(keyword) <= 15:
                score += 0.2
            elif len(keyword) > 20:
                score -= 0.2
            
            # Engagement keyword bonus
            if keyword in self.seo_rules['engagement_keywords']:
                score += 0.3
            
            # Action word bonus
            if keyword in self.seo_rules['action_words']:
                score += 0.2
            
            scored_keywords.append((keyword, score))
        
        # Sort by score
        scored_keywords.sort(key=lambda x: x[1], reverse=True)
        
        return scored_keywords
    
    def _generate_base_title(self, content_analysis: Dict[str, Any], settings: OptimizationSettings) -> str:
        """Generate base title from content analysis"""



        try:
            caption = content_analysis.get('caption', '')
            objects = content_analysis.get('objects_detected', [])
            content_type = content_analysis.get('content_type', ContentType.PHOTOGRAPHY)
            
            if caption:
                # Use AI caption as base
                title = caption.title()
                
                # Enhance with engagement words
                if len(title) < 40:
                    enhancer = self._get_title_enhancer(content_type)
                    title = f"{enhancer} {title}"
            
            elif objects:
                # Create title from detected objects
                main_object = objects[0] if objects else "image"
                enhancer = self._get_title_enhancer(content_type)
                title = f"{enhancer} {main_object.title()}"
            
            else:
                # Fallback title
                title = f"Amazing {content_type.value.title()}"
            
            # Ensure proper length
            if len(title) > 60:
                title = title[:57] + "..."
            elif len(title) < 30:
                title += " - High Quality Visual Content"
            
            return title
            
        except Exception as e:
            logger.warning(f"Title generation failed: {e}")
            return "Stunning Visual Content"
    
    def _get_title_enhancer(self, content_type: ContentType) -> str:
        """Get appropriate title enhancer based on content type"""
        enhancers = {
            ContentType.PHOTOGRAPHY: "Stunning",
            ContentType.PORTRAIT: "Beautiful",
            ContentType.LANDSCAPE: "Breathtaking",
            ContentType.PRODUCT: "Premium",
            ContentType.ARTWORK: "Amazing",
            ContentType.ILLUSTRATION: "Creative",
            ContentType.INFOGRAPHIC: "Informative",
            ContentType.LOGO: "Professional",
            ContentType.SCREENSHOT: "Detailed",
            ContentType.MEME: "Hilarious"
        }
        
        return enhancers.get(content_type, "Incredible")
    
    def _generate_base_description(self, content_analysis: Dict[str, Any], settings: OptimizationSettings) -> str:
        """Generate base description from content analysis"""



        try:
            caption = content_analysis.get('caption', '')
            objects = content_analysis.get('objects_detected', [])
            colors = content_analysis.get('dominant_colors', [])
            content_type = content_analysis.get('content_type', ContentType.PHOTOGRAPHY)
            
            description_parts = []
            
            # Start with caption if available
            if caption:
                description_parts.append(caption)
            
            # Add object details
            if objects:
                if len(objects) > 1:
                    obj_text = f"Featuring {', '.join(objects[:3])}"
                    description_parts.append(obj_text)
            
            # Add color information
            if colors:
                color_text = f"Beautiful {' and '.join(colors[:2])} tones"
                description_parts.append(color_text)
            
            # Add content type context
            type_context = self._get_content_type_context(content_type)
            description_parts.append(type_context)
            
            # Add call to action
            cta = self._get_call_to_action(settings.target_platforms)
            description_parts.append(cta)
            
            # Combine parts
            description = '. '.join(description_parts)
            
            # Ensure proper length
            if len(description) < 120:
                description += ". Perfect for social media sharing and professional use."
            elif len(description) > 160:
                description = description[:157] + "..."
            
            return description
            
        except Exception as e:
            logger.warning(f"Description generation failed: {e}")
            return "High-quality visual content perfect for professional and personal use."
    
    def _get_content_type_context(self, content_type: ContentType) -> str:
        """Get context text for content type"""
        contexts = {
            ContentType.PHOTOGRAPHY: "Professional photography with exceptional detail",
            ContentType.PORTRAIT: "Captivating portrait photography",
            ContentType.LANDSCAPE: "Scenic landscape capturing natural beauty",
            ContentType.PRODUCT: "High-quality product photography",
            ContentType.ARTWORK: "Original artistic creation",
            ContentType.ILLUSTRATION: "Creative digital illustration",
            ContentType.INFOGRAPHIC: "Informative visual design",
            ContentType.LOGO: "Professional brand identity",
            ContentType.SCREENSHOT: "Clear interface demonstration",
            ContentType.MEME: "Entertaining visual content"
        }
        
        return contexts.get(content_type, "High-quality visual content")
    
    def _get_call_to_action(self, platforms: List[SEOPlatform]) -> str:
        """Get appropriate call to action"""
        if SEOPlatform.INSTAGRAM in platforms:
            return "Like and share for more amazing content"
        elif SEOPlatform.PINTEREST in platforms:
            return "Save this pin for inspiration"
        elif SEOPlatform.YOUTUBE in platforms:
            return "Subscribe for more quality content"
        else:
            return "Share and discover more"
    
    def _optimize_title(self, base_title: str, keywords: List[str], settings: OptimizationSettings) -> str:
        """Optimize title with keywords and SEO best practices"""



        try:
            # Start with base title
            optimized = base_title
            
            # Add primary keyword if not present
            primary_keyword = keywords[0] if keywords else ""
            if primary_keyword and primary_keyword.lower() not in optimized.lower():
                # Try to integrate naturally
                if len(optimized) + len(primary_keyword) + 3 <= 60:
                    optimized = f"{optimized} - {primary_keyword.title()}"
            
            # Add year for freshness
            current_year = datetime.now().year
            if str(current_year) not in optimized and len(optimized) < 55:
                optimized = f"{optimized} {current_year}"
            
            # Ensure proper length
            if len(optimized) > 60:
                # Truncate while preserving meaning
                optimized = optimized[:57] + "..."
            
            return optimized
            
        except Exception as e:
            logger.warning(f"Title optimization failed: {e}")
            return base_title
    
    def _optimize_description(self, base_description: str, keywords: List[str], settings: OptimizationSettings) -> str:
        """Optimize description with keywords and SEO best practices"""



        try:
            optimized = base_description
            
            # Add keywords naturally
            for keyword in keywords[:3]:  # Use top 3 keywords
                if keyword.lower() not in optimized.lower():
                    if len(optimized) + len(keyword) + 10 < 160:
                        # Add keyword naturally
                        optimized += f" #{keyword.replace(' ', '')}"
            
            # Ensure proper length
            if len(optimized) > 160:
                optimized = optimized[:157] + "..."
            elif len(optimized) < 120:
                optimized += " Discover more amazing visual content and high-quality images."
            
            return optimized
            
        except Exception as e:
            logger.warning(f"Description optimization failed: {e}")
            return base_description

class MetadataGenerator:
    """Advanced metadata generation for visual content"""
    
    def __init__(self):
        self.metadata_templates = self._load_metadata_templates()
    
    def _load_metadata_templates(self) -> Dict[str, Any]:
        """Load metadata templates for different platforms"""



        return {
            'dublin_core': {
                'title': '',
                'creator': '',
                'subject': [],
                'description': '',
                'date': '',
                'type': 'Image',
                'format': '',
                'identifier': '',
                'language': 'en',
                'rights': ''
            },
            'exif': {
                'ImageDescription': '',
                'Artist': '',
                'Copyright': '',
                'Software': 'IA Influencer Agent',
                'DateTime': '',
                'Keywords': []
            },
            'iptc': {
                'Caption': '',
                'Keywords': [],
                'Category': '',
                'Credit': '',
                'Source': '',
                'Copyright': ''
            }
        }
    
    def generate_comprehensive_metadata(self, seo_result: SEOResult, 
                                      author_info: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Generate comprehensive metadata package"""
        metadata = {}
        
        # Dublin Core metadata
        metadata['dublin_core'] = self._generate_dublin_core(seo_result, author_info)
        
        # EXIF metadata
        metadata['exif'] = self._generate_exif_metadata(seo_result, author_info)
        
        # IPTC metadata
        metadata['iptc'] = self._generate_iptc_metadata(seo_result, author_info)
        
        # Schema.org metadata
        metadata['schema_org'] = seo_result.schema_markup
        
        # Open Graph metadata
        metadata['open_graph'] = self._generate_open_graph(seo_result)
        
        # Twitter Card metadata
        metadata['twitter_card'] = self._generate_twitter_card(seo_result)
        
        return metadata
    
    def _generate_dublin_core(self, seo_result: SEOResult, author_info: Optional[Dict[str, str]]) -> Dict[str, Any]:
        """Generate Dublin Core metadata"""
        dc = self.metadata_templates['dublin_core'].copy()
        
        dc['title'] = seo_result.optimized_title
        dc['description'] = seo_result.optimized_description
        dc['subject'] = seo_result.keywords
        dc['date'] = datetime.now().isoformat()
        
        if author_info:
            dc['creator'] = author_info.get('name', '')
            dc['rights'] = author_info.get('copyright', '')
        
        return dc
    
    def _generate_exif_metadata(self, seo_result: SEOResult, author_info: Optional[Dict[str, str]]) -> Dict[str, Any]:
        """Generate EXIF metadata"""
        exif = self.metadata_templates['exif'].copy()
        
        exif['ImageDescription'] = seo_result.optimized_description
        exif['Keywords'] = seo_result.hashtags
        exif['DateTime'] = datetime.now().strftime('%Y:%m:%d %H:%M:%S')
        
        if author_info:
            exif['Artist'] = author_info.get('name', '')
            exif['Copyright'] = author_info.get('copyright', '')
        
        return exif
    
    def _generate_iptc_metadata(self, seo_result: SEOResult, author_info: Optional[Dict[str, str]]) -> Dict[str, Any]:
        """Generate IPTC metadata"""
        iptc = self.metadata_templates['iptc'].copy()
        
        iptc['Caption'] = seo_result.optimized_description
        iptc['Keywords'] = seo_result.keywords
        
        if author_info:
            iptc['Credit'] = author_info.get('name', '')
            iptc['Copyright'] = author_info.get('copyright', '')
        
        return iptc
    
    def _generate_open_graph(self, seo_result: SEOResult) -> Dict[str, str]:
        """Generate Open Graph metadata"""



        return {
            'og:title': seo_result.optimized_title,
            'og:description': seo_result.optimized_description,
            'og:type': 'article',
            'og:image:alt': seo_result.alt_text
        }
    
    def _generate_twitter_card(self, seo_result: SEOResult) -> Dict[str, str]:
        """Generate Twitter Card metadata"""



        return {
            'twitter:card': 'summary_large_image',
            'twitter:title': seo_result.optimized_title,
            'twitter:description': seo_result.optimized_description,
            'twitter:image:alt': seo_result.alt_text
        }

class TagGenerator:
    """Advanced tag generation system"""
    
    def __init__(self):
        self.tag_categories = self._init_tag_categories()
    
    def _init_tag_categories(self) -> Dict[str, List[str]]:
        """Initialize tag categories"""



        return {
            'emotions': ['happy', 'sad', 'excited', 'calm', 'energetic', 'peaceful', 'dramatic'],
            'styles': ['minimalist', 'vintage', 'modern', 'classic', 'artistic', 'professional', 'casual'],
            'colors': ['colorful', 'monochrome', 'bright', 'dark', 'pastel', 'vibrant', 'muted'],
            'composition': ['portrait', 'landscape', 'closeup', 'wide', 'macro', 'aerial', 'candid'],
            'quality': ['hd', 'highresolution', 'professional', 'studio', 'crisp', 'sharp', 'detailed'],
            'time': ['morning', 'evening', 'sunset', 'sunrise', 'night', 'golden_hour', 'blue_hour'],
            'season': ['spring', 'summer', 'autumn', 'winter', 'seasonal'],
            'trending': ['viral', 'trending', 'popular', 'featured', 'curated', 'editor_choice']
        }
    
    def generate_hashtags(self, content_analysis: Dict[str, Any], keywords: List[str], 
                         settings: OptimizationSettings) -> List[str]:
        """Generate optimized hashtags"""
        hashtags = set()
        
        # Add keyword-based hashtags
        for keyword in keywords[:10]:
            hashtag = self._create_hashtag(keyword)
            if hashtag:
                hashtags.add(hashtag)
        
        # Add content-specific hashtags
        content_hashtags = self._get_content_specific_hashtags(content_analysis)
        hashtags.update(content_hashtags)
        
        # Add platform-specific hashtags
        for platform in settings.target_platforms:
            platform_hashtags = self._get_platform_hashtags(platform)
            hashtags.update(platform_hashtags)
        
        # Add category-based hashtags
        category_hashtags = self._get_category_hashtags(content_analysis)
        hashtags.update(category_hashtags)
        
        # Filter and rank hashtags
        ranked_hashtags = self._rank_hashtags(list(hashtags), settings)
        
        # Return appropriate number based on platform limits
        max_hashtags = self._get_max_hashtags(settings.target_platforms)
        
        return ranked_hashtags[:max_hashtags]
    
    def _create_hashtag(self, text: str) -> Optional[str]:
        """Create hashtag from text"""
        if not text:
            return None
        
        # Clean text
        clean_text = re.sub(r'[^\w\s]', '', text)
        clean_text = re.sub(r'\s+', '', clean_text)
        
        if len(clean_text) >= 2:
            return f"#{clean_text.lower()}"
        
        return None
    
    def _get_content_specific_hashtags(self, content_analysis: Dict[str, Any]) -> List[str]:
        """Get hashtags specific to content"""
        hashtags = []
        
        # Content type hashtags
        content_type = content_analysis.get('content_type', ContentType.PHOTOGRAPHY)
        hashtags.append(f"#{content_type.value}")
        
        # Object hashtags
        objects = content_analysis.get('objects_detected', [])
        for obj in objects[:5]:
            hashtag = self._create_hashtag(obj)
            if hashtag:
                hashtags.append(hashtag)
        
        # Color hashtags
        colors = content_analysis.get('dominant_colors', [])
        for color in colors[:3]:
            hashtags.append(f"#{color}")
        
        # Quality hashtags
        quality_score = content_analysis.get('quality_score', 0.8)
        if quality_score > 0.9:
            hashtags.extend(['#hd', '#highquality', '#professional'])
        elif quality_score > 0.7:
            hashtags.extend(['#quality', '#crisp'])
        
        return hashtags
    
    def _get_platform_hashtags(self, platform: SEOPlatform) -> List[str]:
        """Get platform-specific hashtags"""
        platform_hashtags = {
            SEOPlatform.INSTAGRAM: ['#instagram', '#insta', '#ig', '#instagood', '#photooftheday'],
            SEOPlatform.PINTEREST: ['#pinterest', '#pin', '#inspiration', '#ideas'],
            SEOPlatform.YOUTUBE: ['#youtube', '#video', '#content'],
            SEOPlatform.TIKTOK: ['#tiktok', '#viral', '#fyp', '#foryou'],
            SEOPlatform.TWITTER: ['#twitter', '#tweet'],
            SEOPlatform.FACEBOOK: ['#facebook', '#social'],
            SEOPlatform.LINKEDIN: ['#linkedin', '#professional', '#business'],
            SEOPlatform.GOOGLE: ['#search', '#discover']
        }
        
        return platform_hashtags.get(platform, [])
    
    def _get_category_hashtags(self, content_analysis: Dict[str, Any]) -> List[str]:
        """Get hashtags from predefined categories"""
        hashtags = []
        
        # Add emotional hashtags based on mood
        mood = content_analysis.get('mood', 'neutral')
        if mood in self.tag_categories['emotions']:
            hashtags.append(f"#{mood}")
        
        # Add style hashtags
        hashtags.extend([f"#{tag}" for tag in self.tag_categories['styles'][:2]])
        
        # Add time-based hashtags
        current_hour = datetime.now().hour
        if 5 <= current_hour <= 11:
            hashtags.append('#morning')
        elif 17 <= current_hour <= 20:
            hashtags.append('#evening')
        elif 20 <= current_hour <= 22:
            hashtags.append('#sunset')
        
        return hashtags
    
    def _rank_hashtags(self, hashtags: List[str], settings: OptimizationSettings) -> List[str]:
        """Rank hashtags by relevance and popularity"""
        # Simple ranking based on length and common patterns
        scored_hashtags = []
        
        for hashtag in hashtags:
            score = 0.0
            
            # Length scoring
            if 5 <= len(hashtag) <= 15:
                score += 1.0
            elif len(hashtag) > 20:
                score -= 0.5
            
            # Brand keyword bonus
            for brand_keyword in settings.brand_keywords:
                if brand_keyword.lower() in hashtag.lower():
                    score += 2.0
            
            # Popular hashtag patterns
            if any(pattern in hashtag for pattern in ['photo', 'pic', 'image', 'visual']):
                score += 0.5
            
            scored_hashtags.append((hashtag, score))
        
        # Sort by score
        scored_hashtags.sort(key=lambda x: x[1], reverse=True)
        
        return [hashtag for hashtag, score in scored_hashtags]
    
    def _get_max_hashtags(self, platforms: List[SEOPlatform]) -> int:
        """Get maximum number of hashtags based on platforms"""
        max_limits = {
            SEOPlatform.INSTAGRAM: 30,
            SEOPlatform.PINTEREST: 20,
            SEOPlatform.YOUTUBE: 15,
            SEOPlatform.TIKTOK: 100,
            SEOPlatform.TWITTER: 10,
            SEOPlatform.FACEBOOK: 15,
            SEOPlatform.LINKEDIN: 10,
            SEOPlatform.GOOGLE: 10
        }
        
        if platforms:
            return min([max_limits.get(platform, 15) for platform in platforms])
        
        return 15

class DescriptionGenerator:
    """Advanced description generation system"""
    
    def __init__(self):
        self.description_templates = self._load_description_templates()
    
    def _load_description_templates(self) -> Dict[str, List[str]]:
        """Load description templates for different content types"""



        return {
            ContentType.PHOTOGRAPHY: [
                "Stunning {subject} captured with professional photography techniques.",
                "High-quality {subject} photography showcasing {details}.",
                "Professional {subject} image perfect for {use_cases}."
            ],
            ContentType.PORTRAIT: [
                "Beautiful portrait photography featuring {subject}.",
                "Captivating {subject} portrait with {style} aesthetics.",
                "Professional headshot of {subject} with {lighting} lighting."
            ],
            ContentType.LANDSCAPE: [
                "Breathtaking {location} landscape photography.",
                "Scenic {subject} capturing the beauty of {location}.",
                "Stunning natural scenery from {location} at {time}."
            ],
            ContentType.PRODUCT: [
                "Premium {product} photography for commercial use.",
                "High-quality {product} image showcasing {features}.",
                "Professional product photography of {product} with {style} styling."
            ]
        }
    
    def generate_platform_specific_descriptions(self, base_description: str, 
                                              settings: OptimizationSettings) -> Dict[str, str]:
        """Generate platform-specific descriptions"""
        descriptions = {}
        
        for platform in settings.target_platforms:
            platform_desc = self._adapt_description_for_platform(base_description, platform)
            descriptions[platform.value] = platform_desc
        
        return descriptions
    
    def _adapt_description_for_platform(self, base_description: str, platform: SEOPlatform) -> str:
        """Adapt description for specific platform"""
        if platform == SEOPlatform.INSTAGRAM:
            # Instagram prefers shorter, more engaging descriptions
            return self._create_instagram_description(base_description)
        elif platform == SEOPlatform.PINTEREST:
            # Pinterest likes descriptive, searchable text
            return self._create_pinterest_description(base_description)
        elif platform == SEOPlatform.YOUTUBE:
            # YouTube allows longer descriptions with more detail
            return self._create_youtube_description(base_description)
        elif platform == SEOPlatform.LINKEDIN:
            # LinkedIn prefers professional tone
            return self._create_linkedin_description(base_description)
        else:
            return base_description
    
    def _create_instagram_description(self, base_description: str) -> str:
        """Create Instagram-optimized description"""
        # Keep it short and engaging
        if len(base_description) > 125:
            short_desc = base_description[:120] + "..."
        else:
            short_desc = base_description
        
        # Add Instagram-specific elements
        return f"{short_desc}  #instagood #photooftheday"
    
    def _create_pinterest_description(self, base_description: str) -> str:
        """Create Pinterest-optimized description"""
        # Pinterest allows longer descriptions
        extended_desc = base_description
        
        if len(extended_desc) < 200:
            extended_desc += " Perfect for inspiration, decoration, and creative projects. Save this pin for later!"
        
        return extended_desc
    
    def _create_youtube_description(self, base_description: str) -> str:
        """Create YouTube-optimized description"""
        # YouTube allows very long descriptions
        extended_desc = f"{base_description}\n\n"
        extended_desc += " Subscribe for more amazing content!\n"
        extended_desc += " Like if you enjoyed this content\n"
        extended_desc += " Comment your thoughts below\n\n"
        extended_desc += "#YouTube #Content #Subscribe"
        
        return extended_desc
    
    def _create_linkedin_description(self, base_description: str) -> str:
        """Create LinkedIn-optimized description"""
        # Professional tone for LinkedIn
        professional_desc = base_description.replace("amazing", "exceptional")
        professional_desc = professional_desc.replace("stunning", "remarkable")
        
        return f"{professional_desc} #Professional #Business #LinkedIn"

# Additional utility functions for SEO optimization
def calculate_keyword_density(text: str, keyword: str) -> float:
    """Calculate keyword density in text"""
    if not text or not keyword:
        return 0.0
    
    text_lower = text.lower()
    keyword_lower = keyword.lower()
    
    word_count = len(text_lower.split())
    keyword_count = text_lower.count(keyword_lower)
    
    if word_count == 0:
        return 0.0
    
    return keyword_count / word_count

def calculate_readability_score(text: str) -> float:
    """Calculate Flesch reading ease score"""
    if not text:
        return 0.0
    
    try:
        sentences = text.count('.') + text.count('!') + text.count('?')
        words = len(text.split())
        syllables = sum([count_syllables(word) for word in text.split()])
        
        if sentences == 0 or words == 0:
            return 0.0
        
        # Flesch Reading Ease formula
        score = 206.835 - (1.015 * (words / sentences)) - (84.6 * (syllables / words))
        
        return max(0.0, min(100.0, score))
        
    except Exception:
        return 50.0  # Default moderate score

def count_syllables(word: str) -> int:
    """Count syllables in a word"""
    word = word.lower()
    vowels = "aeiouy"
    syllable_count = 0
    prev_was_vowel = False
    
    for char in word:
        if char in vowels:
            if not prev_was_vowel:
                syllable_count += 1
            prev_was_vowel = True
        else:
            prev_was_vowel = False
    
    # Handle silent 'e'
    if word.endswith('e') and syllable_count > 1:
        syllable_count -= 1
    
    return max(1, syllable_count)  # Every word has at least 1 syllable
