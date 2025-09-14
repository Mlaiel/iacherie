"""Content Format SEO Optimizer - Système d'Optimisation SEO Multi-Format Ultra-Avancé
======================================================================================

Système d'optimisation SEO multi-format ultra-avancé fournissant des stratégies SEO 
spécialisées pour différents formats de contenu, optimisation de recherche vocale, 
coordination de contenu multi-format et optimisation intelligente basée sur l'IA.

Fonctionnalités:
- Optimisation SEO spécialisée par format (vidéo, audio, image, texte, interactif)
- Moteur d'optimisation de recherche vocale avec NLP avancé
- Coordination multi-format intelligente avec IA
- Analyse de performance cross-format en temps réel
- Génération automatique de métadonnées optimisées
- Système de recommandations personnalisées par format
- Optimisation pour featured snippets et réponses vocales
- Analyse de tendances de contenu multimédia
- Intégration API multi-plateformes (YouTube, Spotify, Instagram, etc.)
- Système de monitoring et alertes automatisées

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Enterprise License - Usage Restreint
"""

import asyncio
import logging
import json
import re
import time
import hashlib
import mimetypes
from typing import Dict, List, Optional, Union, Any, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path

# Imports with error handling
try:
    import aiohttp
except ImportError:
    aiohttp = None
    
try:
    import numpy as np
except ImportError:
    np = None

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.cluster import KMeans
except ImportError:
    TfidfVectorizer = None
    cosine_similarity = None
    KMeans = None

try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
except (ImportError, OSError):
    spacy = None
    nlp = None

try:
    import cv2
except ImportError:
    cv2 = None

try:
    import librosa
except ImportError:
    librosa = None

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    import tensorflow as tf
except ImportError:
    tf = None

try:
    from transformers import pipeline, AutoTokenizer, AutoModel
except ImportError:
    pipeline = None
    AutoTokenizer = None
    AutoModel = None

try:
    import nltk
    from nltk.sentiment import SentimentIntensityAnalyzer
    # Download required NLTK data
    nltk.download('vader_lexicon', quiet=True)
    nltk.download('punkt', quiet=True) 
    nltk.download('stopwords', quiet=True)
except ImportError:
    nltk = None
    SentimentIntensityAnalyzer = None

try:
    import yake
except ImportError:
    yake = None

try:
    from textstat import flesch_reading_ease, automated_readability_index
except ImportError:
    flesch_reading_ease = None
    automated_readability_index = None

try:
    import speech_recognition as sr
except ImportError:
    sr = None

try:
    from moviepy.editor import VideoFileClip
except ImportError:
    VideoFileClip = None

try:
    import pytesseract
except ImportError:
    pytesseract = None

try:
    from fuzzywuzzy import fuzz
except ImportError:
    fuzz = None

try:
    import asyncpg
except ImportError:
    asyncpg = None

try:
    import redis
except ImportError:
    redis = None

try:
    from elasticsearch import AsyncElasticsearch
except ImportError:
    AsyncElasticsearch = None

logger = logging.getLogger(__name__)

# Configuration NLTK et spaCy avec gestion d'erreurs
if nltk and SentimentIntensityAnalyzer:
    try:
        nltk.download('vader_lexicon', quiet=True)
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
    except Exception as e:
        logger.warning(f"Problème de configuration NLTK: {e}")

if spacy and nlp is None:
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        logger.warning("Modèle spaCy 'en_core_web_sm' non trouvé")
        nlp = None
    except Exception as e:
        logger.warning(f"Problème de configuration spaCy: {e}")
        nlp = None

class ContentFormat(Enum):
    """Types de formats de contenu ultra-avancés"""
    VIDEO = "video"
    AUDIO = "audio"
    PODCAST = "podcast"
    IMAGE = "image"
    INFOGRAPHIC = "infographic"
    TEXT = "text"
    BLOG_POST = "blog_post"
    INTERACTIVE = "interactive"
    LIVE_STREAM = "live_stream"
    WEBINAR = "webinar"
    EBOOK = "ebook"
    CAROUSEL = "carousel"
    STORY = "story"
    REEL = "reel"
    SHORT_FORM = "short_form"
    LONG_FORM = "long_form"
    DOCUMENTARY = "documentary"
    TUTORIAL = "tutorial"
    REVIEW = "review"
    COMPARISON = "comparison"
    NEWS = "news"
    ENTERTAINMENT = "entertainment"

class VoiceSearchType(Enum):
    """Types de recherches vocales"""
    QUESTION = "question"
    COMMAND = "command"
    LOCAL = "local"
    CONVERSATIONAL = "conversational"
    INFORMATIONAL = "informational"
    TRANSACTIONAL = "transactional"
    NAVIGATIONAL = "navigational"
    COMMERCIAL = "commercial"

class OptimizationLevel(Enum):
    """Niveaux d'optimisation"""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    ENTERPRISE = "enterprise"

class ContentQuality(Enum):
    """Qualité de contenu"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    PREMIUM = "premium"
    VIRAL_POTENTIAL = "viral_potential"

class PlatformType(Enum):
    """Types de plateformes"""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    SPOTIFY = "spotify"
    APPLE_PODCASTS = "apple_podcasts"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    TWITCH = "twitch"

@dataclass
class ContentMetrics:
    """Métriques de contenu"""
    readability_score: float = 0.0
    sentiment_score: float = 0.0
    keyword_density: float = 0.0
    engagement_prediction: float = 0.0
    seo_score: float = 0.0
    voice_search_readiness: float = 0.0
    accessibility_score: float = 0.0
    mobile_optimization: float = 0.0
    load_time_score: float = 0.0
    visual_appeal_score: float = 0.0

@dataclass
class FormatOptimization:
    """Résultat d'optimisation de format ultra-avancé"""
    format_type: ContentFormat
    optimization_score: float
    quality_level: ContentQuality
    recommendations: List[str]
    seo_enhancements: Dict[str, Any]
    technical_specs: Dict[str, Any]
    platform_adaptations: Dict[PlatformType, Dict[str, Any]]
    performance_predictions: Dict[str, float]
    content_metrics: ContentMetrics
    ai_insights: Dict[str, Any]
    optimization_roadmap: List[Dict[str, Any]]
    competitive_analysis: Dict[str, Any]
    trending_elements: List[str]
    accessibility_features: Dict[str, Any]
    monetization_potential: Dict[str, Any]

@dataclass
class VoiceSearchOptimization:
    """Optimisation de recherche vocale"""
    query_type: VoiceSearchType
    optimization_score: float
    featured_snippet_potential: float
    conversational_keywords: List[str]
    question_answer_pairs: List[Dict[str, str]]
    local_seo_factors: Dict[str, Any]
    voice_device_compatibility: Dict[str, float]
    natural_language_score: float
    semantic_relevance: float

@dataclass
class MultiFormatStrategy:
    """Stratégie multi-format"""
    primary_format: ContentFormat
    supporting_formats: List[ContentFormat]
    cross_format_synergy_score: float
    content_repurposing_plan: Dict[str, Any]
    distribution_timeline: Dict[str, datetime]
    platform_optimization_map: Dict[PlatformType, ContentFormat]
    roi_projections: Dict[str, float]
    resource_allocation: Dict[str, float]

class ContentFormatAnalyzer:
    """Analyseur de format de contenu ultra-avancé"""
    
    def __init__(self) -> None:
        self.supported_formats = {
            'video': ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm'],
            'audio': ['.mp3', '.wav', '.aac', '.flac', '.ogg', '.m4a'],
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'],
            'text': ['.txt', '.md', '.html', '.rtf', '.doc', '.docx']
        }
        self.ml_models = {}
        self._initialize_ml_models()
    
    def _initialize_ml_models(self) -> None:
        """Initialise les modèles ML avec gestion d'erreurs"""
        try:
            if pipeline:
                self.ml_models['sentiment'] = pipeline("sentiment-analysis")
                self.ml_models['text_generation'] = pipeline("text-generation", 
                                                           model="gpt2")
                self.ml_models['summarization'] = pipeline("summarization")
                self.ml_models['question_answering'] = pipeline("question-answering")
                logger.info("Modèles ML initialisés avec succès")
            else:
                logger.warning("Transformers non disponible - modèles ML désactivés")
        except Exception as e:
            logger.error(f"Erreur initialisation ML: {e}")
            self.ml_models = {}
    
    async def analyze_content_format(self, file_path: str) -> ContentFormat:
        """Analyse le format de contenu"""
        try:
            file_extension = Path(file_path).suffix.lower()
            
            for format_type, extensions in self.supported_formats.items():
                if file_extension in extensions:
                    return ContentFormat(format_type.upper())
            
            # Analyse par contenu si extension inconnue
            return await self._analyze_by_content(file_path)
        except Exception as e:
            logger.error(f"Erreur analyse format: {e}")
            return ContentFormat.TEXT
    
    async def _analyze_by_content(self, file_path: str) -> ContentFormat:
        """Analyse par contenu"""
        try:
            mime_type, _ = mimetypes.guess_type(file_path)
            
            if mime_type:
                if mime_type.startswith('video/'):
                    return ContentFormat.VIDEO
                elif mime_type.startswith('audio/'):
                    return ContentFormat.AUDIO
                elif mime_type.startswith('image/'):
                    return ContentFormat.IMAGE
                elif mime_type.startswith('text/'):
                    return ContentFormat.TEXT
            
            return ContentFormat.TEXT
        except Exception as e:
            logger.error(f"Erreur analyse contenu: {e}")
            return ContentFormat.TEXT

class ContentFormatSEOOptimizer:
    """Optimiseur SEO de format de contenu ultra-avancé avec IA"""
    
    def __init__(self, config -> None: Dict[str, Any] = None) -> None:
        self.config = config or {}
        self.analyzer = ContentFormatAnalyzer()
        self.db_pool = None
        self.redis_client = None
        self.elasticsearch_client = None
        
        # Initialisation sécurisée des analyseurs
        if SentimentIntensityAnalyzer:
            try:
                self.sentiment_analyzer = SentimentIntensityAnalyzer()
            except Exception as e:
                logger.warning(f"Erreur init sentiment analyzer: {e}")
                self.sentiment_analyzer = None
        else:
            self.sentiment_analyzer = None
            
        if yake:
            try:
                self.keyword_extractor = yake.KeywordExtractor(
                    lan="en", n=3, dedupLim=0.7, top=20
                )
            except Exception as e:
                logger.warning(f"Erreur init keyword extractor: {e}")
                self.keyword_extractor = None
        else:
            self.keyword_extractor = None
            
        self.optimization_cache = {}
        self.performance_history = {}
        
        # Configuration des APIs externes
        self.api_keys = {
            'youtube': self.config.get('youtube_api_key'),
            'instagram': self.config.get('instagram_api_key'),
            'spotify': self.config.get('spotify_api_key'),
            'google_vision': self.config.get('google_vision_api_key'),
            'aws_transcribe': self.config.get('aws_transcribe_key')
        }
        
        # Modèles prédictifs
        self.prediction_models = {}
        self._initialize_prediction_models()
    
    def _initialize_prediction_models(self) -> None:
        """Initialise les modèles prédictifs avec gestion d'erreurs"""
        try:
            if tf:
                # Modèle de prédiction d'engagement
                self.prediction_models['engagement'] = self._create_engagement_model()
                
                # Modèle de score SEO
                self.prediction_models['seo_score'] = self._create_seo_model()
            else:
                logger.warning("TensorFlow non disponible - modèles prédictifs désactivés")
                
            if KMeans:
                # Modèle de tendances
                self.prediction_models['trends'] = self._create_trends_model()
            else:
                logger.warning("scikit-learn non disponible - modèle de tendances désactivé")
            
            logger.info("Modèles prédictifs initialisés")
        except Exception as e:
            logger.error(f"Erreur initialisation modèles: {e}")
    
    def _create_engagement_model(self) -> None:
        """Crée le modèle de prédiction d'engagement avec gestion d'erreurs"""
        if not tf:
            return None
        try:
            model = tf.keras.Sequential([
                tf.keras.layers.Dense(64, activation='relu'),
                tf.keras.layers.Dropout(0.3),
                tf.keras.layers.Dense(32, activation='relu'),
                tf.keras.layers.Dense(1, activation='sigmoid')
            ])
            model.compile(optimizer='adam', loss='binary_crossentropy', 
                         metrics=['accuracy'])
            return model
        except Exception as e:
            logger.error(f"Erreur création modèle engagement: {e}")
            return None
    
    def _create_seo_model(self) -> None:
        """Crée le modèle de score SEO avec gestion d'erreurs"""
        if not tf:
            return None
        try:
            model = tf.keras.Sequential([
                tf.keras.layers.Dense(128, activation='relu'),
                tf.keras.layers.BatchNormalization(),
                tf.keras.layers.Dropout(0.4),
                tf.keras.layers.Dense(64, activation='relu'),
                tf.keras.layers.Dense(32, activation='relu'),
                tf.keras.layers.Dense(1, activation='sigmoid')
            ])
            model.compile(optimizer='adam', loss='mse', metrics=['mae'])
            return model
        except Exception as e:
            logger.error(f"Erreur création modèle SEO: {e}")
            return None
    
    def _create_trends_model(self) -> None:
        """Crée le modèle d'analyse de tendances avec gestion d'erreurs"""
        if not KMeans:
            return None
        try:
            return KMeans(n_clusters=5, random_state=42)
        except Exception as e:
            logger.error(f"Erreur création modèle tendances: {e}")
            return None
    
    async def optimize_content_format(
        self,
        content: Union[str, bytes, Path],
        format_type: ContentFormat = None,
        target_keywords: List[str] = None,
        target_platforms: List[PlatformType] = None,
        optimization_level: OptimizationLevel = OptimizationLevel.ADVANCED
    ) -> FormatOptimization:
        """Optimise le contenu pour un format spécifique avec IA ultra-avancée"""
        try:
            start_time = time.time()
            
            # Détection automatique du format si non spécifié
            if format_type is None:
                format_type = await self._detect_format(content)
            
            # Analyse du contenu
            content_analysis = await self._analyze_content_comprehensive(
                content, format_type
            )
            
            # Extraction des métriques
            content_metrics = await self._extract_content_metrics(
                content, format_type
            )
            
            # Génération des recommandations IA
            recommendations = await self._generate_ai_recommendations(
                content_analysis, format_type, optimization_level
            )
            
            # Optimisations techniques
            technical_specs = await self._generate_technical_specs(
                content, format_type
            )
            
            # Adaptations par plateforme
            platform_adaptations = await self._generate_platform_adaptations(
                content, format_type, target_platforms or []
            )
            
            # Prédictions de performance
            performance_predictions = await self._predict_performance(
                content_analysis, format_type, target_platforms
            )
            
            # Insights IA
            ai_insights = await self._generate_ai_insights(
                content_analysis, format_type
            )
            
            # Roadmap d'optimisation
            optimization_roadmap = await self._create_optimization_roadmap(
                content_analysis, format_type, optimization_level
            )
            
            # Analyse compétitive
            competitive_analysis = await self._perform_competitive_analysis(
                content, format_type, target_keywords
            )
            
            # Éléments tendance
            trending_elements = await self._identify_trending_elements(
                content, format_type
            )
            
            # Features d'accessibilité
            accessibility_features = await self._generate_accessibility_features(
                content, format_type
            )
            
            # Potentiel de monétisation
            monetization_potential = await self._assess_monetization_potential(
                content_analysis, format_type
            )
            
            # Calcul du score d'optimisation
            optimization_score = await self._calculate_optimization_score(
                content_metrics, recommendations, technical_specs
            )
            
            # Détermination du niveau de qualité
            quality_level = await self._determine_quality_level(
                optimization_score, content_metrics
            )
            
            # Enhancements SEO
            seo_enhancements = await self._create_seo_enhancements(
                content_analysis, format_type, target_keywords
            )
            
            processing_time = time.time() - start_time
            
            # Cache des résultats
            await self._cache_optimization_results(
                content, format_type, optimization_score
            )
            
            logger.info(f"Optimisation {format_type.value} terminée en {processing_time:.2f}s")
            
            return FormatOptimization(
                format_type=format_type,
                optimization_score=optimization_score,
                quality_level=quality_level,
                recommendations=recommendations,
                seo_enhancements=seo_enhancements,
                technical_specs=technical_specs,
                platform_adaptations=platform_adaptations,
                performance_predictions=performance_predictions,
                content_metrics=content_metrics,
                ai_insights=ai_insights,
                optimization_roadmap=optimization_roadmap,
                competitive_analysis=competitive_analysis,
                trending_elements=trending_elements,
                accessibility_features=accessibility_features,
                monetization_potential=monetization_potential
            )
            
        except Exception as e:
            logger.error(f"Erreur optimisation format: {e}")
            raise
    
    async def _detect_format(self, content: Union[str, bytes, Path]) -> ContentFormat:
        """Détection intelligente du format"""
        try:
            if isinstance(content, Path):
                return await self.analyzer.analyze_content_format(str(content))
            elif isinstance(content, str):
                if self._is_url(content):
                    return await self._detect_format_from_url(content)
                else:
                    return await self._detect_format_from_text(content)
            else:
                return await self._detect_format_from_bytes(content)
        except Exception as e:
            logger.error(f"Erreur détection format: {e}")
            return ContentFormat.TEXT
    
    def _is_url(self, content: str) -> bool:
        """Vérifie si le contenu est une URL"""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(content) is not None
    
    async def _detect_format_from_url(self, url: str) -> ContentFormat:
        """Détecte le format depuis une URL"""
        try:
            if 'youtube.com' in url or 'youtu.be' in url:
                return ContentFormat.VIDEO
            elif 'spotify.com' in url or 'soundcloud.com' in url:
                return ContentFormat.AUDIO
            elif 'instagram.com' in url and '/p/' in url:
                return ContentFormat.IMAGE
            elif 'tiktok.com' in url:
                return ContentFormat.SHORT_FORM
            else:
                return ContentFormat.TEXT
        except Exception as e:
            logger.error(f"Erreur détection URL: {e}")
            return ContentFormat.TEXT
    
    async def _detect_format_from_text(self, text: str) -> ContentFormat:
        """Détecte le format depuis le texte"""
        try:
            text_lower = text.lower()
            
            # Indicateurs de format
            if any(word in text_lower for word in ['video', 'youtube', 'vimeo']):
                return ContentFormat.VIDEO
            elif any(word in text_lower for word in ['audio', 'podcast', 'music']):
                return ContentFormat.AUDIO
            elif any(word in text_lower for word in ['image', 'photo', 'picture']):
                return ContentFormat.IMAGE
            elif len(text) > 1000:
                return ContentFormat.LONG_FORM
            elif len(text) < 280:
                return ContentFormat.SHORT_FORM
            else:
                return ContentFormat.TEXT
        except Exception as e:
            logger.error(f"Erreur détection texte: {e}")
            return ContentFormat.TEXT
    
    async def _detect_format_from_bytes(self, data: bytes) -> ContentFormat:
        """Détecte le format depuis les bytes"""
        try:
            # Signatures de fichiers
            if data.startswith(b'\xff\xd8\xff'):  # JPEG
                return ContentFormat.IMAGE
            elif data.startswith(b'\x89PNG'):  # PNG
                return ContentFormat.IMAGE
            elif data.startswith(b'RIFF') and b'WAVE' in data[:12]:  # WAV
                return ContentFormat.AUDIO
            elif data.startswith(b'\x00\x00\x00\x18ftypmp4'):  # MP4
                return ContentFormat.VIDEO
            else:
                return ContentFormat.TEXT
        except Exception as e:
            logger.error(f"Erreur détection bytes: {e}")
            return ContentFormat.TEXT

    async def _analyze_content_comprehensive(
        self, 
        content: Union[str, bytes, Path], 
        format_type: ContentFormat
    ) -> Dict[str, Any]:
        """Analyse comprehensive du contenu"""
        try:
            analysis = {
                'basic_stats': await self._get_basic_stats(content, format_type),
                'linguistic_analysis': await self._analyze_linguistics(content),
                'semantic_analysis': await self._analyze_semantics(content),
                'technical_analysis': await self._analyze_technical(content, format_type),
                'sentiment_analysis': await self._analyze_sentiment(content),
                'keyword_analysis': await self._analyze_keywords(content),
                'readability_analysis': await self._analyze_readability(content),
                'structure_analysis': await self._analyze_structure(content, format_type)
            }
            
            return analysis
        except Exception as e:
            logger.error(f"Erreur analyse comprehensive: {e}")
            return {}
    
    async def _get_basic_stats(
        self, 
        content: Union[str, bytes, Path], 
        format_type: ContentFormat
    ) -> Dict[str, Any]:
        """Statistiques de base du contenu"""
        try:
            if format_type in [ContentFormat.VIDEO, ContentFormat.AUDIO]:
                return await self._get_media_stats(content, format_type)
            elif format_type == ContentFormat.IMAGE:
                return await self._get_image_stats(content)
            else:
                return await self._get_text_stats(content)
        except Exception as e:
            logger.error(f"Erreur stats de base: {e}")
            return {}
    
    async def _get_media_stats(
        self, 
        content: Union[str, Path], 
        format_type: ContentFormat
    ) -> Dict[str, Any]:
        """Stats pour contenu média"""
        try:
            if isinstance(content, str) and self._is_url(content):
                return {'source': 'url', 'url': content}
            
            file_path = Path(content) if not isinstance(content, Path) else content
            
            if format_type == ContentFormat.VIDEO:
                clip = VideoFileClip(str(file_path))
                return {
                    'duration': clip.duration,
                    'fps': clip.fps,
                    'size': clip.size,
                    'format': file_path.suffix,
                    'file_size': file_path.stat().st_size
                }
            elif format_type == ContentFormat.AUDIO:
                y, sr = librosa.load(str(file_path))
                return {
                    'duration': len(y) / sr,
                    'sample_rate': sr,
                    'channels': 1,
                    'format': file_path.suffix,
                    'file_size': file_path.stat().st_size
                }
        except Exception as e:
            logger.error(f"Erreur stats média: {e}")
            return {}
    
    async def _get_image_stats(self, content: Union[str, Path]) -> Dict[str, Any]:
        """Stats pour image"""
        try:
            if isinstance(content, str) and self._is_url(content):
                return {'source': 'url', 'url': content}
            
            file_path = Path(content) if not isinstance(content, Path) else content
            
            with Image.open(file_path) as img:
                return {
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'mode': img.mode,
                    'file_size': file_path.stat().st_size,
                    'aspect_ratio': img.width / img.height
                }
        except Exception as e:
            logger.error(f"Erreur stats image: {e}")
            return {}
    
    async def _get_text_stats(self, content: str) -> Dict[str, Any]:
        """Stats pour texte"""
        try:
            words = content.split()
            sentences = re.split(r'[.!?]+', content)
            paragraphs = content.split('\n\n')
            
            return {
                'character_count': len(content),
                'word_count': len(words),
                'sentence_count': len([s for s in sentences if s.strip()]),
                'paragraph_count': len([p for p in paragraphs if p.strip()]),
                'avg_words_per_sentence': len(words) / max(len(sentences), 1),
                'avg_characters_per_word': len(content) / max(len(words), 1)
            }
        except Exception as e:
            logger.error(f"Erreur stats texte: {e}")
            return {}
    
    async def _analyze_linguistics(self, content: str) -> Dict[str, Any]:
        """Analyse linguistique avancée avec gestion d'erreurs"""
        try:
            if not nlp:
                logger.warning("spaCy non disponible - analyse linguistique limitée")
                return {'entities': [], 'pos_tags': [], 'noun_phrases': [], 'language_detected': 'en'}
            
            doc = nlp(content[:1000000])  # Limite pour performance
            
            # Extraction d'entités
            entities = [(ent.text, ent.label_) for ent in doc.ents]
            
            # Analyse POS
            pos_tags = [(token.text, token.pos_) for token in doc]
            
            # Extraction de phrases clés
            noun_phrases = [chunk.text for chunk in doc.noun_chunks]
            
            return {
                'entities': entities,
                'pos_tags': pos_tags[:50],  # Limite pour lisibilité
                'noun_phrases': noun_phrases[:20],
                'language_detected': doc.lang_ if hasattr(doc, 'lang_') else 'en'
            }
        except Exception as e:
            logger.error(f"Erreur analyse linguistique: {e}")
            return {'entities': [], 'pos_tags': [], 'noun_phrases': [], 'language_detected': 'en'}
    
    async def _analyze_semantics(self, content: str) -> Dict[str, Any]:
        """Analyse sémantique avec gestion d'erreurs"""
        try:
            # Extraction de mots-clés avec YAKE si disponible
            keywords = []
            if yake:
                keyword_extractor = yake.KeywordExtractor(lan="en", n=3, dedupLim=0.7, top=20)
                keywords = keyword_extractor.extract_keywords(content)
            else:
                logger.warning("YAKE non disponible - extraction de mots-clés basique")
                # Extraction basique par fréquence
                words = re.findall(r'\b\w+\b', content.lower())
                word_freq = {}
                for word in words:
                    if len(word) > 3:  # Mots de plus de 3 caractères
                        word_freq[word] = word_freq.get(word, 0) + 1
                # Top 20 mots les plus fréquents
                keywords = [(word, freq) for word, freq in sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20]]
            
            # Analyse de similarité sémantique
            sentences = re.split(r'[.!?]+', content)
            avg_similarity = 0.0
            
            if TfidfVectorizer and cosine_similarity and len(sentences) > 1:
                try:
                    vectorizer = TfidfVectorizer(stop_words='english')
                    tfidf_matrix = vectorizer.fit_transform(sentences)
                    similarity_matrix = cosine_similarity(tfidf_matrix)
                    if np:
                        avg_similarity = np.mean(similarity_matrix)
                    else:
                        avg_similarity = 0.5  # Valeur par défaut
                except Exception as e:
                    logger.warning(f"Erreur calcul similarité: {e}")
                    avg_similarity = 0.5
            else:
                if not TfidfVectorizer:
                    logger.warning("scikit-learn non disponible - analyse sémantique limitée")
                avg_similarity = 0.5
            
            return {
                'keywords': [(kw[1], kw[0]) for kw in keywords] if keywords else [],
                'semantic_coherence': avg_similarity,
                'topic_diversity': len(set([kw[1] for kw in keywords])) if keywords else 0,
                'content_density': len(keywords) / max(len(content.split()), 1) if keywords else 0
            }
        except Exception as e:
            logger.error(f"Erreur analyse sémantique: {e}")
            return {'keywords': [], 'semantic_coherence': 0.5, 'topic_diversity': 0, 'content_density': 0}
    
    async def _analyze_technical(
        self, 
        content: Union[str, bytes, Path], 
        format_type: ContentFormat
    ) -> Dict[str, Any]:
        """Analyse technique du contenu"""
        try:
            technical_analysis = {
                'format_compliance': await self._check_format_compliance(content, format_type),
                'optimization_opportunities': await self._identify_optimization_opportunities(content, format_type),
                'technical_seo_factors': await self._analyze_technical_seo(content, format_type),
                'performance_metrics': await self._analyze_performance_metrics(content, format_type)
            }
            
            return technical_analysis
        except Exception as e:
            logger.error(f"Erreur analyse technique: {e}")
            return {}
    
    async def _check_format_compliance(
        self, 
        content: Union[str, bytes, Path], 
        format_type: ContentFormat
    ) -> Dict[str, Any]:
        """Vérifie la conformité du format"""
        compliance_score = 0.8  # Score par défaut
        issues = []
        recommendations = []
        
        try:
            if format_type == ContentFormat.VIDEO:
                # Vérifications spécifiques vidéo
                if isinstance(content, Path):
                    file_size = content.stat().st_size
                    if file_size > 100 * 1024 * 1024:  # 100MB
                        issues.append("Taille de fichier élevée")
                        recommendations.append("Compresser la vidéo")
                        compliance_score -= 0.1
            
            elif format_type == ContentFormat.IMAGE:
                # Vérifications spécifiques image
                if isinstance(content, Path):
                    with Image.open(content) as img:
                        if max(img.size) > 2048:
                            issues.append("Résolution très élevée")
                            recommendations.append("Optimiser la résolution")
                            compliance_score -= 0.1
            
            elif format_type in [ContentFormat.TEXT, ContentFormat.BLOG_POST]:
                # Vérifications spécifiques texte
                word_count = len(content.split()) if isinstance(content, str) else 0
                if word_count < 300:
                    issues.append("Contenu trop court")
                    recommendations.append("Étendre le contenu")
                    compliance_score -= 0.2
                elif word_count > 2000:
                    issues.append("Contenu très long")
                    recommendations.append("Diviser en sections")
                    compliance_score -= 0.1
            
        except Exception as e:
            logger.error(f"Erreur vérification conformité: {e}")
        
        return {
            'compliance_score': max(0.0, compliance_score),
            'issues': issues,
            'recommendations': recommendations
        }
    
    async def _identify_optimization_opportunities(
        self, 
        content: Union[str, bytes, Path], 
        format_type: ContentFormat
    ) -> List[Dict[str, Any]]:
        """Identifie les opportunités d'optimisation"""
        opportunities = []
        
        try:
            if format_type == ContentFormat.VIDEO:
                opportunities.extend([
                    {
                        'type': 'technical',
                        'description': 'Ajouter des sous-titres automatiques',
                        'impact': 'high',
                        'effort': 'medium'
                    },
                    {
                        'type': 'seo',
                        'description': 'Optimiser la miniature',
                        'impact': 'high',
                        'effort': 'low'
                    },
                    {
                        'type': 'engagement',
                        'description': 'Ajouter des timestamps',
                        'impact': 'medium',
                        'effort': 'low'
                    }
                ])
            
            elif format_type == ContentFormat.IMAGE:
                opportunities.extend([
                    {
                        'type': 'technical',
                        'description': 'Optimiser le format (WebP)',
                        'impact': 'medium',
                        'effort': 'low'
                    },
                    {
                        'type': 'accessibility',
                        'description': 'Ajouter du texte alt descriptif',
                        'impact': 'high',
                        'effort': 'low'
                    }
                ])
            
            elif format_type in [ContentFormat.TEXT, ContentFormat.BLOG_POST]:
                opportunities.extend([
                    {
                        'type': 'seo',
                        'description': 'Optimiser les titres H1-H6',
                        'impact': 'high',
                        'effort': 'medium'
                    },
                    {
                        'type': 'readability',
                        'description': 'Améliorer la lisibilité',
                        'impact': 'medium',
                        'effort': 'medium'
                    },
                    {
                        'type': 'engagement',
                        'description': 'Ajouter des CTA',
                        'impact': 'high',
                        'effort': 'low'
                    }
                ])
            
        except Exception as e:
            logger.error(f"Erreur identification opportunités: {e}")
        
        return opportunities
    
    async def _analyze_technical_seo(
        self, 
        content: Union[str, bytes, Path], 
        format_type: ContentFormat
    ) -> Dict[str, Any]:
        """Analyse SEO technique"""
        try:
            seo_factors = {
                'meta_optimization': await self._analyze_meta_optimization(content),
                'structure_optimization': await self._analyze_structure_optimization(content, format_type),
                'loading_optimization': await self._analyze_loading_optimization(content, format_type),
                'mobile_optimization': await self._analyze_mobile_optimization(content, format_type),
                'accessibility_optimization': await self._analyze_accessibility_optimization(content, format_type)
            }
            
            return seo_factors
        except Exception as e:
            logger.error(f"Erreur analyse SEO technique: {e}")
            return {}
    
    async def _analyze_performance_metrics(
        self, 
        content: Union[str, bytes, Path], 
        format_type: ContentFormat
    ) -> Dict[str, Any]:
        """Analyse des métriques de performance"""
        try:
            metrics = {
                'load_time_estimation': await self._estimate_load_time(content, format_type),
                'bandwidth_usage': await self._estimate_bandwidth(content, format_type),
                'compression_potential': await self._assess_compression_potential(content, format_type),
                'caching_optimization': await self._assess_caching_optimization(content, format_type)
            }
            
            return metrics
        except Exception as e:
            logger.error(f"Erreur analyse performance: {e}")
            return {}
    
    async def _analyze_sentiment(self, content: str) -> Dict[str, Any]:
        """Analyse de sentiment avec gestion d'erreurs"""
        try:
            sentiment_result = {
                'vader_compound': 0.0,
                'vader_positive': 0.0,
                'vader_negative': 0.0,
                'vader_neutral': 1.0,
                'ml_sentiment': None,
                'overall_sentiment': 'neutral'
            }
            
            # Analyse avec VADER si disponible
            if SentimentIntensityAnalyzer:
                try:
                    sentiment_analyzer = SentimentIntensityAnalyzer()
                    vader_scores = sentiment_analyzer.polarity_scores(content)
                    sentiment_result.update({
                        'vader_compound': vader_scores['compound'],
                        'vader_positive': vader_scores['pos'],
                        'vader_negative': vader_scores['neg'],
                        'vader_neutral': vader_scores['neu'],
                        'overall_sentiment': self._categorize_sentiment(vader_scores['compound'])
                    })
                except Exception as e:
                    logger.warning(f"Erreur VADER sentiment: {e}")
            else:
                logger.warning("NLTK/VADER non disponible - analyse de sentiment basique")
            
            # Analyse avec ML model si disponible
            if 'sentiment' in self.ml_models and self.ml_models['sentiment']:
                try:
                    ml_result = self.ml_models['sentiment'](content[:512])
                    sentiment_result['ml_sentiment'] = ml_result[0] if ml_result else None
                except Exception as e:
                    logger.warning(f"Erreur ML sentiment: {e}")
            
            return sentiment_result
            
        except Exception as e:
            logger.error(f"Erreur analyse sentiment: {e}")
            return {
                'vader_compound': 0.0,
                'vader_positive': 0.0,
                'vader_negative': 0.0,
                'vader_neutral': 1.0,
                'ml_sentiment': None,
                'overall_sentiment': 'neutral'
            }
    
    def _categorize_sentiment(self, compound_score: float) -> str:
        """Catégorise le sentiment"""
        if compound_score >= 0.05:
            return 'positive'
        elif compound_score <= -0.05:
            return 'negative'
        else:
            return 'neutral'
    
    async def _analyze_keywords(self, content: str) -> Dict[str, Any]:
        """Analyse des mots-clés"""
        try:
            # Extraction avec YAKE
            keywords = self.keyword_extractor.extract_keywords(content)
            
            # Analyse de densité
            words = content.lower().split()
            word_freq = {}
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            total_words = len(words)
            keyword_density = {}
            for keyword, score in keywords:
                count = word_freq.get(keyword.lower(), 0)
                density = (count / total_words) * 100 if total_words > 0 else 0
                keyword_density[keyword] = density
            
            return {
                'extracted_keywords': [(kw[1], kw[0]) for kw in keywords[:20]],
                'keyword_density': keyword_density,
                'top_frequent_words': sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10],
                'unique_word_ratio': len(set(words)) / max(len(words), 1)
            }
        except Exception as e:
            logger.error(f"Erreur analyse mots-clés: {e}")
            return {}
    
    async def _analyze_readability(self, content: str) -> Dict[str, Any]:
        """Analyse de lisibilité avec gestion d'erreurs"""
        try:
            if not isinstance(content, str) or len(content.strip()) == 0:
                return {
                    'flesch_reading_ease': 50.0,
                    'automated_readability_index': 10.0,
                    'avg_sentence_length': 15.0,
                    'avg_word_length': 5.0,
                    'readability_level': 'standard'
                }
            
            readability_result = {}
            
            # Scores de lisibilité si textstat disponible
            if flesch_reading_ease and automated_readability_index:
                try:
                    flesch_score = flesch_reading_ease(content)
                    ari_score = automated_readability_index(content)
                    readability_result.update({
                        'flesch_reading_ease': flesch_score,
                        'automated_readability_index': ari_score,
                        'readability_level': self._categorize_readability(flesch_score)
                    })
                except Exception as e:
                    logger.warning(f"Erreur calcul textstat: {e}")
                    readability_result.update({
                        'flesch_reading_ease': 50.0,
                        'automated_readability_index': 10.0,
                        'readability_level': 'standard'
                    })
            else:
                logger.warning("textstat non disponible - analyse de lisibilité basique")
                readability_result.update({
                    'flesch_reading_ease': 50.0,
                    'automated_readability_index': 10.0,
                    'readability_level': 'standard'
                })
            
            # Analyse de structure (toujours disponible)
            sentences = re.split(r'[.!?]+', content)
            sentences = [s for s in sentences if s.strip()]
            avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
            
            words = content.split()
            avg_word_length = sum(len(w) for w in words) / max(len(words), 1)
            
            readability_result.update({
                'avg_sentence_length': avg_sentence_length,
                'avg_word_length': avg_word_length
            })
            
            return readability_result
            
        except Exception as e:
            logger.error(f"Erreur analyse lisibilité: {e}")
            return {
                'flesch_reading_ease': 50.0,
                'automated_readability_index': 10.0,
                'avg_sentence_length': 15.0,
                'avg_word_length': 5.0,
                'readability_level': 'standard'
            }
    
    def _categorize_readability(self, flesch_score: float) -> str:
        """Catégorise le niveau de lisibilité"""
        if flesch_score >= 90:
            return 'very_easy'
        elif flesch_score >= 80:
            return 'easy'
        elif flesch_score >= 70:
            return 'fairly_easy'
        elif flesch_score >= 60:
            return 'standard'
        elif flesch_score >= 50:
            return 'fairly_difficult'
        elif flesch_score >= 30:
            return 'difficult'
        else:
            return 'very_difficult'
    
    async def _analyze_structure(
        self, 
        content: Union[str, bytes, Path], 
        format_type: ContentFormat
    ) -> Dict[str, Any]:
        """Analyse de structure du contenu"""
        try:
            if format_type in [ContentFormat.TEXT, ContentFormat.BLOG_POST]:
                return await self._analyze_text_structure(content)
            elif format_type == ContentFormat.VIDEO:
                return await self._analyze_video_structure(content)
            elif format_type == ContentFormat.AUDIO:
                return await self._analyze_audio_structure(content)
            elif format_type == ContentFormat.IMAGE:
                return await self._analyze_image_structure(content)
            else:
                return {}
        except Exception as e:
            logger.error(f"Erreur analyse structure: {e}")
            return {}
    
    async def _analyze_text_structure(self, content: str) -> Dict[str, Any]:
        """Analyse structure du texte"""
        try:
            # Détection des titres
            headings = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
            
            # Détection des listes
            lists = re.findall(r'^\s*[-*+]\s+(.+)$', content, re.MULTILINE)
            
            # Détection des liens
            links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
            
            # Paragraphes
            paragraphs = [p for p in content.split('\n\n') if p.strip()]
            
            return {
                'has_headings': len(headings) > 0,
                'heading_count': len(headings),
                'headings': headings[:10],
                'has_lists': len(lists) > 0,
                'list_items': len(lists),
                'has_links': len(links) > 0,
                'link_count': len(links),
                'paragraph_count': len(paragraphs),
                'avg_paragraph_length': sum(len(p.split()) for p in paragraphs) / max(len(paragraphs), 1)
            }
        except Exception as e:
            logger.error(f"Erreur analyse structure texte: {e}")
            return {}

    async def _analyze_video_structure(self, content: Union[str, Path]) -> Dict[str, Any]:
        """Analyse structure vidéo"""
        try:
            if isinstance(content, str) and self._is_url(content):
                return {'source': 'url', 'analysis': 'limited'}
            
            # Analyse basique pour demo
            return {
                'has_intro': True,
                'has_chapters': False,
                'has_outro': True,
                'transitions_count': 0,
                'scene_changes': 0
            }
        except Exception as e:
            logger.error(f"Erreur analyse structure vidéo: {e}")
            return {}
    
    async def _analyze_audio_structure(self, content: Union[str, Path]) -> Dict[str, Any]:
        """Analyse structure audio"""
        try:
            if isinstance(content, str) and self._is_url(content):
                return {'source': 'url', 'analysis': 'limited'}
            
            return {
                'has_intro_music': True,
                'speech_segments': 1,
                'music_segments': 0,
                'silence_ratio': 0.1
            }
        except Exception as e:
            logger.error(f"Erreur analyse structure audio: {e}")
            return {}
    
    async def _analyze_image_structure(self, content: Union[str, Path]) -> Dict[str, Any]:
        """Analyse structure image"""
        try:
            if isinstance(content, str) and self._is_url(content):
                return {'source': 'url', 'analysis': 'limited'}
            
            return {
                'has_text_overlay': False,
                'composition_type': 'standard',
                'color_palette_size': 5,
                'contrast_ratio': 0.7
            }
        except Exception as e:
            logger.error(f"Erreur analyse structure image: {e}")
            return {}

class VoiceSearchOptimizationEngine:
    """Moteur d'optimisation de recherche vocale ultra-avancé avec IA"""
    
    def __init__(self, config -> None: Dict[str, Any] = None) -> None:
        self.config = config or {}
        self.nlp_pipeline = None
        self.question_classifier = None
        self.intent_recognizer = None
        self.local_seo_optimizer = None
        self._initialize_voice_components()
    
    def _initialize_voice_components(self) -> None:
        """Initialise les composants de recherche vocale"""
        try:
            # Pipeline NLP pour questions
            self.nlp_pipeline = pipeline("question-answering")
            
            # Classificateur d'intention
            self.intent_recognizer = pipeline("text-classification")
            
            logger.info("Composants de recherche vocale initialisés")
        except Exception as e:
            logger.error(f"Erreur initialisation composants vocaux: {e}")
    
    async def optimize_for_voice_search(
        self,
        content: str,
        target_queries: List[str] = None,
        location_context: Dict[str, Any] = None,
        optimization_level: OptimizationLevel = OptimizationLevel.ADVANCED
    ) -> VoiceSearchOptimization:
        """Optimise le contenu pour la recherche vocale avec IA ultra-avancée"""
        try:
            # Analyse du type de requête
            query_type = await self._classify_query_type(content, target_queries)
            
            # Extraction de mots-clés conversationnels
            conversational_keywords = await self._extract_conversational_keywords_advanced(content)
            
            # Identification des paires question-réponse
            question_answer_pairs = await self._identify_question_answers_ai(content)
            
            # Optimisation locale
            local_seo_factors = await self._optimize_for_local_voice_advanced(
                content, location_context
            )
            
            # Optimisation pour featured snippets
            snippet_optimization = await self._optimize_for_snippets_advanced(content)
            
            # Compatibilité avec assistants vocaux
            voice_device_compatibility = await self._assess_voice_device_compatibility(content)
            
            # Score de langage naturel
            natural_language_score = await self._calculate_natural_language_score(content)
            
            # Pertinence sémantique
            semantic_relevance = await self._calculate_semantic_relevance(
                content, target_queries
            )
            
            # Score d'optimisation global
            optimization_score = await self._calculate_voice_optimization_score(
                conversational_keywords, question_answer_pairs, local_seo_factors,
                natural_language_score, semantic_relevance
            )
            
            # Potentiel featured snippet
            featured_snippet_potential = await self._calculate_featured_snippet_potential(
                content, snippet_optimization
            )
            
            return VoiceSearchOptimization(
                query_type=query_type,
                optimization_score=optimization_score,
                featured_snippet_potential=featured_snippet_potential,
                conversational_keywords=conversational_keywords,
                question_answer_pairs=question_answer_pairs,
                local_seo_factors=local_seo_factors,
                voice_device_compatibility=voice_device_compatibility,
                natural_language_score=natural_language_score,
                semantic_relevance=semantic_relevance
            )
            
        except Exception as e:
            logger.error(f"Erreur optimisation recherche vocale: {e}")
            raise
    
    async def _classify_query_type(
        self, 
        content: str, 
        target_queries: List[str] = None
    ) -> VoiceSearchType:
        """Classifie le type de requête vocale"""
        try:
            content_lower = content.lower()
            
            # Mots-clés indicateurs
            question_indicators = ['what', 'how', 'why', 'when', 'where', 'which', 'who']
            command_indicators = ['play', 'show', 'open', 'start', 'stop', 'call']
            local_indicators = ['near', 'nearby', 'location', 'address', 'directions']
            commercial_indicators = ['buy', 'price', 'cost', 'purchase', 'order']
            
            # Analyse des indicateurs
            if any(indicator in content_lower for indicator in question_indicators):
                if any(indicator in content_lower for indicator in local_indicators):
                    return VoiceSearchType.LOCAL
                else:
                    return VoiceSearchType.QUESTION
            elif any(indicator in content_lower for indicator in command_indicators):
                return VoiceSearchType.COMMAND
            elif any(indicator in content_lower for indicator in commercial_indicators):
                return VoiceSearchType.COMMERCIAL
            elif any(indicator in content_lower for indicator in local_indicators):
                return VoiceSearchType.LOCAL
            else:
                return VoiceSearchType.CONVERSATIONAL
                
        except Exception as e:
            logger.error(f"Erreur classification requête: {e}")
            return VoiceSearchType.CONVERSATIONAL
    
    async def _extract_conversational_keywords_advanced(self, content: str) -> List[str]:
        """Extraction avancée de mots-clés conversationnels"""
        try:
            keywords = []
            
            # Mots-clés conversationnels de base
            base_conversational = [
                "how to", "what is", "where can", "best way", "how do i",
                "what are", "where is", "when should", "why does", "which is",
                "tell me about", "show me", "find me", "help me", "can you",
                "i want to", "i need to", "looking for", "searching for"
            ]
            
            # Recherche dans le contenu
            content_lower = content.lower()
            for phrase in base_conversational:
                if phrase in content_lower:
                    keywords.append(phrase)
            
            # Extraction avec NLP si disponible
            if nlp and self.nlp_pipeline:
                try:
                    doc = nlp(content[:1000])  # Limite pour performance
                    for sent in doc.sents:
                        sent_text = sent.text.lower().strip()
                        if sent_text.endswith('?'):
                            keywords.append(sent_text)
                except Exception as e:
                    logger.warning(f"Erreur NLP conversationnel: {e}")
            
            # Génération de variations
            variations = []
            for keyword in keywords:
                variations.extend(self._generate_keyword_variations(keyword))
            
            return list(set(keywords + variations))[:50]  # Limite pour performance
            
        except Exception as e:
            logger.error(f"Erreur extraction mots-clés conversationnels: {e}")
            return []
    
    def _generate_keyword_variations(self, keyword: str) -> List[str]:
        """Génère des variations de mots-clés"""
        variations = []
        
        try:
            # Variations avec synonymes
            synonyms_map = {
                'how to': ['how can i', 'how do i', 'what is the way to'],
                'what is': ['what are', 'define', 'explain'],
                'where can': ['where to', 'where is', 'location of'],
                'best way': ['optimal way', 'better way', 'easiest way']
            }
            
            if keyword in synonyms_map:
                variations.extend(synonyms_map[keyword])
            
            # Variations avec préfixes/suffixes
            prefixes = ['', 'the ', 'a ', 'an ']
            suffixes = ['', ' for beginners', ' step by step', ' guide']
            
            for prefix in prefixes:
                for suffix in suffixes:
                    if prefix + keyword + suffix != keyword:
                        variations.append(prefix + keyword + suffix)
        
        except Exception as e:
            logger.error(f"Erreur génération variations: {e}")
        
        return variations[:10]  # Limite les variations
    
    async def _identify_question_answers_ai(self, content: str) -> List[Dict[str, str]]:
        """Identification IA des paires question-réponse"""
        try:
            qa_pairs = []
            
            # Recherche de questions explicites
            questions = re.findall(r'([^.!?]*\?)', content)
            
            for question in questions:
                question = question.strip()
                if len(question) > 10:  # Filtre les questions trop courtes
                    # Recherche de la réponse suivante
                    question_index = content.find(question)
                    if question_index != -1:
                        # Texte après la question
                        after_question = content[question_index + len(question):question_index + len(question) + 500]
                        
                        # Première phrase comme réponse potentielle
                        answer_match = re.match(r'([^.!?]*[.!?])', after_question.strip())
                        if answer_match:
                            answer = answer_match.group(1).strip()
                            if len(answer) > 10:
                                qa_pairs.append({
                                    'question': question,
                                    'answer': answer,
                                    'confidence': 0.7
                                })
            
            # Génération de Q&A avec ML si disponible
            if self.nlp_pipeline:
                try:
                    # Questions génériques pour extraction d'informations
                    generic_questions = [
                        "What is this about?",
                        "How does this work?",
                        "What are the benefits?",
                        "What is the main point?"
                    ]
                    
                    for question in generic_questions:
                        try:
                            result = self.nlp_pipeline(question=question, context=content[:1000])
                            if result['score'] > 0.5:  # Seuil de confiance
                                qa_pairs.append({
                                    'question': question,
                                    'answer': result['answer'],
                                    'confidence': result['score']
                                })
                        except Exception as e:
                            logger.warning(f"Erreur ML Q&A: {e}")
                
                except Exception as e:
                    logger.warning(f"Erreur pipeline Q&A: {e}")
            
            # Tri par confiance
            qa_pairs.sort(key=lambda x: x['confidence'], reverse=True)
            
            return qa_pairs[:20]  # Limite pour performance
            
        except Exception as e:
            logger.error(f"Erreur identification Q&A: {e}")
            return []
    
    async def _optimize_for_local_voice_advanced(
        self, 
        content: str, 
        location_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Optimisation avancée pour recherche vocale locale"""
        try:
            local_factors = {
                'location_keywords': [],
                'business_info': {},
                'local_intent_score': 0.0,
                'geographic_relevance': 0.0,
                'local_competition_analysis': {},
                'near_me_optimization': {},
                'local_schema_suggestions': []
            }
            
            content_lower = content.lower()
            
            # Mots-clés de localisation
            location_keywords = [
                'near me', 'nearby', 'close to', 'in my area', 'local',
                'around here', 'directions to', 'address', 'location',
                'open now', 'hours', 'phone number', 'contact'
            ]
            
            found_keywords = [kw for kw in location_keywords if kw in content_lower]
            local_factors['location_keywords'] = found_keywords
            
            # Score d'intention locale
            local_factors['local_intent_score'] = len(found_keywords) / len(location_keywords)
            
            # Informations business si contexte fourni
            if location_context:
                local_factors['business_info'] = {
                    'name': location_context.get('business_name', ''),
                    'address': location_context.get('address', ''),
                    'phone': location_context.get('phone', ''),
                    'hours': location_context.get('hours', {}),
                    'category': location_context.get('category', '')
                }
                
                # Augmente le score si informations business disponibles
                local_factors['geographic_relevance'] = 0.8
            
            # Suggestions de schéma local
            if local_factors['local_intent_score'] > 0.3:
                local_factors['local_schema_suggestions'] = [
                    'LocalBusiness',
                    'Organization',
                    'PostalAddress',
                    'ContactPoint',
                    'OpeningHoursSpecification'
                ]
            
            # Optimisation "near me"
            local_factors['near_me_optimization'] = {
                'keywords_to_add': [
                    f"{location_context.get('category', 'business')} near me",
                    f"best {location_context.get('category', 'service')} nearby",
                    f"local {location_context.get('category', 'business')}"
                ] if location_context else [],
                'content_suggestions': [
                    "Include location-specific information",
                    "Add operating hours",
                    "Include contact information",
                    "Add service area details"
                ]
            }
            
            return local_factors
            
        except Exception as e:
            logger.error(f"Erreur optimisation locale: {e}")
            return {}
    
    async def _optimize_for_snippets_advanced(self, content: str) -> Dict[str, Any]:
        """Optimisation avancée pour featured snippets"""
        try:
            snippet_optimization = {
                'snippet_opportunities': [],
                'structured_answers': [],
                'list_optimizations': [],
                'table_opportunities': [],
                'paragraph_snippets': [],
                'definition_opportunities': []
            }
            
            # Recherche d'opportunités de listes
            list_patterns = [
                r'steps? to',
                r'ways? to',
                r'methods? to',
                r'tips? for',
                r'benefits? of',
                r'reasons? why'
            ]
            
            for pattern in list_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    snippet_optimization['snippet_opportunities'].append({
                        'type': 'list',
                        'pattern': pattern,
                        'matches': len(matches),
                        'optimization': 'Create numbered or bulleted list'
                    })
            
            # Recherche de définitions
            definition_patterns = [
                r'(\w+) is (?:a|an|the) ([^.]+)',
                r'(\w+) refers to ([^.]+)',
                r'(\w+) means ([^.]+)'
            ]
            
            for pattern in definition_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    snippet_optimization['definition_opportunities'].append({
                        'term': match[0],
                        'definition': match[1],
                        'optimization': 'Structure as clear definition'
                    })
            
            # Réponses structurées
            sentences = re.split(r'[.!?]+', content)
            for sentence in sentences:
                sentence = sentence.strip()
                if 30 <= len(sentence) <= 160:  # Longueur optimale pour snippets
                    snippet_optimization['structured_answers'].append({
                        'text': sentence,
                        'length': len(sentence),
                        'snippet_potential': 'high' if 40 <= len(sentence) <= 120 else 'medium'
                    })
            
            # Optimisations de paragraphe
            paragraphs = content.split('\n\n')
            for i, paragraph in enumerate(paragraphs):
                if 50 <= len(paragraph) <= 300:
                    snippet_optimization['paragraph_snippets'].append({
                        'paragraph_index': i,
                        'text': paragraph[:100] + '...',
                        'length': len(paragraph),
                        'optimization_potential': 'high'
                    })
            
            return snippet_optimization
            
        except Exception as e:
            logger.error(f"Erreur optimisation snippets: {e}")
            return {}
    
    async def _assess_voice_device_compatibility(self, content: str) -> Dict[str, float]:
        """Évalue la compatibilité avec les assistants vocaux"""
        try:
            compatibility = {
                'alexa': 0.0,
                'google_assistant': 0.0,
                'siri': 0.0,
                'cortana': 0.0
            }
            
            content_lower = content.lower()
            
            # Facteurs de compatibilité
            factors = {
                'natural_language': len(re.findall(r'\b(how|what|where|when|why|who)\b', content_lower)) / max(len(content.split()), 1),
                'question_format': content.count('?') / max(len(content.split('.')), 1),
                'conversational_tone': len(re.findall(r'\b(you|your|we|us|i)\b', content_lower)) / max(len(content.split()), 1),
                'clear_answers': len(re.findall(r'\b(yes|no|because|therefore|however)\b', content_lower)) / max(len(content.split()), 1)
            }
            
            # Score de base pour chaque assistant
            base_score = sum(factors.values()) / len(factors)
            
            # Ajustements spécifiques par assistant
            compatibility['alexa'] = min(base_score + 0.1, 1.0)  # Alexa aime les réponses directes
            compatibility['google_assistant'] = min(base_score + 0.2, 1.0)  # Google est fort en NLP
            compatibility['siri'] = min(base_score, 1.0)  # Siri standard
            compatibility['cortana'] = min(base_score - 0.1, 1.0)  # Cortana moins utilisé
            
            return compatibility
            
        except Exception as e:
            logger.error(f"Erreur évaluation compatibilité: {e}")
            return {'alexa': 0.5, 'google_assistant': 0.5, 'siri': 0.5, 'cortana': 0.5}
    
    async def _calculate_natural_language_score(self, content: str) -> float:
        """Calcule le score de langage naturel"""
        try:
            score = 0.0
            content_lower = content.lower()
            
            # Facteurs de langage naturel
            factors = {
                'contractions': len(re.findall(r"[a-z]+'[a-z]+", content_lower)) / max(len(content.split()), 1),
                'conversational_words': len(re.findall(r'\b(well|so|actually|basically|really)\b', content_lower)) / max(len(content.split()), 1),
                'personal_pronouns': len(re.findall(r'\b(i|you|we|they|he|she)\b', content_lower)) / max(len(content.split()), 1),
                'question_words': len(re.findall(r'\b(what|how|where|when|why|who|which)\b', content_lower)) / max(len(content.split()), 1),
                'discourse_markers': len(re.findall(r'\b(however|therefore|moreover|furthermore|meanwhile)\b', content_lower)) / max(len(content.split()), 1)
            }
            
            # Moyenne pondérée
            weights = [0.2, 0.25, 0.2, 0.2, 0.15]
            score = sum(factor * weight for factor, weight in zip(factors.values(), weights))
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Erreur calcul score langage naturel: {e}")
            return 0.5
    
    async def _calculate_semantic_relevance(
        self, 
        content: str, 
        target_queries: List[str] = None
    ) -> float:
        """Calcule la pertinence sémantique"""
        try:
            if not target_queries:
                return 0.7  # Score par défaut
            
            # Vectorisation TF-IDF
            vectorizer = TfidfVectorizer(stop_words='english')
            
            # Corpus avec contenu + requêtes
            corpus = [content] + target_queries
            tfidf_matrix = vectorizer.fit_transform(corpus)
            
            # Similarité entre contenu et requêtes
            content_vector = tfidf_matrix[0]
            query_vectors = tfidf_matrix[1:]
            
            similarities = []
            for query_vector in query_vectors:
                similarity = cosine_similarity(content_vector, query_vector)[0][0]
                similarities.append(similarity)
            
            # Moyenne des similarités
            avg_similarity = sum(similarities) / len(similarities) if similarities else 0.0
            
            return min(avg_similarity, 1.0)
            
        except Exception as e:
            logger.error(f"Erreur calcul pertinence sémantique: {e}")
            return 0.5
    
    async def _calculate_voice_optimization_score(
        self,
        conversational_keywords: List[str],
        question_answer_pairs: List[Dict[str, str]],
        local_seo_factors: Dict[str, Any],
        natural_language_score: float,
        semantic_relevance: float
    ) -> float:
        """Calcule le score global d'optimisation vocale"""
        try:
            # Facteurs avec pondération
            factors = {
                'conversational_keywords': min(len(conversational_keywords) / 10, 1.0),  # 20%
                'qa_pairs': min(len(question_answer_pairs) / 5, 1.0),  # 25%
                'local_optimization': local_seo_factors.get('local_intent_score', 0.0),  # 15%
                'natural_language': natural_language_score,  # 25%
                'semantic_relevance': semantic_relevance  # 15%
            }
            
            weights = [0.2, 0.25, 0.15, 0.25, 0.15]
            
            # Score pondéré
            score = sum(factor * weight for factor, weight in zip(factors.values(), weights))
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Erreur calcul score optimisation vocale: {e}")
            return 0.5
    
    async def _calculate_featured_snippet_potential(
        self,
        content: str,
        snippet_optimization: Dict[str, Any]
    ) -> float:
        """Calcule le potentiel de featured snippet"""
        try:
            score = 0.0
            
            # Facteurs de snippet
            factors = {
                'snippet_opportunities': len(snippet_optimization.get('snippet_opportunities', [])) / 5,
                'structured_answers': len(snippet_optimization.get('structured_answers', [])) / 10,
                'definition_opportunities': len(snippet_optimization.get('definition_opportunities', [])) / 3,
                'list_optimizations': len(snippet_optimization.get('list_optimizations', [])) / 3
            }
            
            # Score moyen
            score = sum(factors.values()) / len(factors)
            
            # Bonus pour contenu bien structuré
            if content.count('\n') > 5:  # Paragraphes multiples
                score += 0.1
            if re.search(r'^\d+\.', content, re.MULTILINE):  # Listes numérotées
                score += 0.15
            if content.count('?') > 0:  # Questions
                score += 0.1
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Erreur calcul potentiel snippet: {e}")
            return 0.3

class MultiFormatContentSEOOptimizer:
    """Optimiseur SEO de contenu multi-format ultra-avancé avec coordination IA"""
    
    def __init__(self, config -> None: Dict[str, Any] = None) -> None:
        self.config = config or {}
        self.format_optimizer = ContentFormatSEOOptimizer(config)
        self.voice_optimizer = VoiceSearchOptimizationEngine(config)
        self.content_coordinator = ContentCoordinator()
        self.performance_predictor = PerformancePredictor()
        self.platform_adapters = self._initialize_platform_adapters()
        self.optimization_history = {}
        self.ml_models = {}
        self._initialize_multi_format_models()
    
    def _initialize_platform_adapters(self) -> Dict[PlatformType, Any]:
        """Initialise les adaptateurs de plateforme"""
        return {
            PlatformType.YOUTUBE: YouTubeAdapter(self.config),
            PlatformType.INSTAGRAM: InstagramAdapter(self.config),
            PlatformType.TIKTOK: TikTokAdapter(self.config),
            PlatformType.LINKEDIN: LinkedInAdapter(self.config),
            PlatformType.TWITTER: TwitterAdapter(self.config),
            PlatformType.FACEBOOK: FacebookAdapter(self.config),
            PlatformType.SPOTIFY: SpotifyAdapter(self.config)
        }
    
    def _initialize_multi_format_models(self) -> None:
        """Initialise les modèles ML multi-format"""
        try:
            # Modèle de synergie cross-format
            self.ml_models['cross_format_synergy'] = self._create_synergy_model()
            
            # Modèle de prédiction de performance
            self.ml_models['performance_predictor'] = self._create_performance_model()
            
            # Modèle d'allocation de ressources
            self.ml_models['resource_allocation'] = self._create_allocation_model()
            
            logger.info("Modèles multi-format initialisés")
        except Exception as e:
            logger.error(f"Erreur initialisation modèles multi-format: {e}")
    
    def _create_synergy_model(self) -> None:
        """Crée le modèle de synergie cross-format"""
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        return model
    
    def _create_performance_model(self) -> None:
        """Crée le modèle de prédiction de performance"""
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(256, activation='relu'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dropout(0.4),
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(3, activation='softmax')  # Low, Medium, High
        ])
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        return model
    
    def _create_allocation_model(self) -> None:
        """Crée le modèle d'allocation de ressources"""
        return KMeans(n_clusters=3, random_state=42)  # 3 niveaux de ressources
    
    async def optimize_multi_format_content(
        self,
        content_pieces: Dict[ContentFormat, Union[str, bytes, Path]],
        target_keywords: List[str] = None,
        target_platforms: List[PlatformType] = None,
        budget_constraints: Dict[str, float] = None,
        optimization_level: OptimizationLevel = OptimizationLevel.ENTERPRISE
    ) -> Dict[str, Any]:
        """Optimise le contenu multi-format avec coordination IA ultra-avancée"""
        try:
            start_time = time.time()
            
            # Optimisation individuelle des formats
            format_optimizations = await self._optimize_individual_formats(
                content_pieces, target_keywords, target_platforms, optimization_level
            )
            
            # Stratégie cross-format
            cross_format_strategy = await self._create_cross_format_strategy_advanced(
                content_pieces, format_optimizations, target_platforms
            )
            
            # Coordination intelligente
            coordination_plan = await self._create_coordination_plan(
                format_optimizations, cross_format_strategy
            )
            
            # Prédictions de performance
            performance_predictions = await self._predict_multi_format_performance(
                format_optimizations, cross_format_strategy
            )
            
            # Allocation de ressources optimale
            resource_allocation = await self._optimize_resource_allocation(
                format_optimizations, budget_constraints
            )
            
            # Timeline de distribution
            distribution_timeline = await self._create_distribution_timeline(
                format_optimizations, target_platforms
            )
            
            # Analyse de synergie
            synergy_analysis = await self._analyze_format_synergy(
                content_pieces, format_optimizations
            )
            
            # ROI projections
            roi_projections = await self._calculate_roi_projections(
                format_optimizations, performance_predictions, resource_allocation
            )
            
            # Plan de repurposing
            repurposing_plan = await self._create_repurposing_plan(
                content_pieces, format_optimizations
            )
            
            # Monitoring et alertes
            monitoring_setup = await self._setup_monitoring_alerts(
                format_optimizations, performance_predictions
            )
            
            # Score SEO unifié
            unified_seo_score = await self._calculate_unified_score_advanced(
                format_optimizations, synergy_analysis
            )
            
            # Recommandations d'amélioration
            improvement_recommendations = await self._generate_improvement_recommendations(
                format_optimizations, synergy_analysis, performance_predictions
            )
            
            processing_time = time.time() - start_time
            
            # Sauvegarde dans l'historique
            await self._save_optimization_history(
                content_pieces, format_optimizations, unified_seo_score
            )
            
            logger.info(f"Optimisation multi-format terminée en {processing_time:.2f}s")
            
            return {
                "format_optimizations": format_optimizations,
                "cross_format_strategy": cross_format_strategy,
                "coordination_plan": coordination_plan,
                "performance_predictions": performance_predictions,
                "resource_allocation": resource_allocation,
                "distribution_timeline": distribution_timeline,
                "synergy_analysis": synergy_analysis,
                "roi_projections": roi_projections,
                "repurposing_plan": repurposing_plan,
                "monitoring_setup": monitoring_setup,
                "unified_seo_score": unified_seo_score,
                "improvement_recommendations": improvement_recommendations,
                "processing_time": processing_time,
                "optimization_metadata": {
                    "timestamp": datetime.now(),
                    "optimization_level": optimization_level.value,
                    "formats_count": len(content_pieces),
                    "platforms_count": len(target_platforms) if target_platforms else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur optimisation multi-format: {e}")
            raise
    
    async def _optimize_individual_formats(
        self,
        content_pieces: Dict[ContentFormat, Union[str, bytes, Path]],
        target_keywords: List[str],
        target_platforms: List[PlatformType],
        optimization_level: OptimizationLevel
    ) -> Dict[str, FormatOptimization]:
        """Optimise chaque format individuellement"""
        try:
            format_optimizations = {}
            
            # Optimisation parallèle pour performance
            tasks = []
            for format_type, content in content_pieces.items():
                task = self.format_optimizer.optimize_content_format(
                    content, format_type, target_keywords, target_platforms, optimization_level
                )
                tasks.append((format_type, task))
            
            # Exécution parallèle
            results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
            
            # Compilation des résultats
            for (format_type, _), result in zip(tasks, results):
                if isinstance(result, Exception):
                    logger.error(f"Erreur optimisation {format_type}: {result}")
                    continue
                
                format_optimizations[format_type.value] = result
            
            return format_optimizations
            
        except Exception as e:
            logger.error(f"Erreur optimisation formats individuels: {e}")
            return {}
    
    async def _create_cross_format_strategy_advanced(
        self,
        content_pieces: Dict[ContentFormat, Union[str, bytes, Path]],
        format_optimizations: Dict[str, FormatOptimization],
        target_platforms: List[PlatformType] = None
    ) -> MultiFormatStrategy:
        """Crée une stratégie cross-format avancée"""
        try:
            # Analyse des formats disponibles
            available_formats = list(content_pieces.keys())
            
            # Détermination du format primaire (meilleur score)
            primary_format = await self._determine_primary_format(format_optimizations)
            
            # Formats de support
            supporting_formats = [f for f in available_formats if f != primary_format]
            
            # Calcul de synergie
            synergy_score = await self._calculate_cross_format_synergy(
                content_pieces, format_optimizations
            )
            
            # Plan de repurposing
            repurposing_plan = await self._create_content_repurposing_plan(
                content_pieces, format_optimizations
            )
            
            # Timeline de distribution
            distribution_timeline = await self._create_optimized_timeline(
                format_optimizations, target_platforms
            )
            
            # Mapping plateforme-format
            platform_optimization_map = await self._create_platform_format_map(
                format_optimizations, target_platforms
            )
            
            # Projections ROI
            roi_projections = await self._calculate_format_roi_projections(
                format_optimizations, synergy_score
            )
            
            # Allocation de ressources
            resource_allocation = await self._calculate_optimal_resource_allocation(
                format_optimizations, synergy_score
            )
            
            return MultiFormatStrategy(
                primary_format=primary_format,
                supporting_formats=supporting_formats,
                cross_format_synergy_score=synergy_score,
                content_repurposing_plan=repurposing_plan,
                distribution_timeline=distribution_timeline,
                platform_optimization_map=platform_optimization_map,
                roi_projections=roi_projections,
                resource_allocation=resource_allocation
            )
            
        except Exception as e:
            logger.error(f"Erreur création stratégie cross-format: {e}")
            # Retour de stratégie par défaut
            return MultiFormatStrategy(
                primary_format=list(content_pieces.keys())[0] if content_pieces else ContentFormat.TEXT,
                supporting_formats=[],
                cross_format_synergy_score=0.5,
                content_repurposing_plan={},
                distribution_timeline={},
                platform_optimization_map={},
                roi_projections={},
                resource_allocation={}
            )
    
    async def _determine_primary_format(
        self, 
        format_optimizations: Dict[str, FormatOptimization]
    ) -> ContentFormat:
        """Détermine le format primaire basé sur les scores"""
        try:
            if not format_optimizations:
                return ContentFormat.TEXT
            
            # Trouve le format avec le meilleur score
            best_format = max(
                format_optimizations.items(),
                key=lambda x: x[1].optimization_score
            )
            
            return ContentFormat(best_format[0].upper())
            
        except Exception as e:
            logger.error(f"Erreur détermination format primaire: {e}")
            return ContentFormat.TEXT
    
    async def _calculate_cross_format_synergy(
        self,
        content_pieces: Dict[ContentFormat, Union[str, bytes, Path]],
        format_optimizations: Dict[str, FormatOptimization]
    ) -> float:
        """Calcule la synergie cross-format"""
        try:
            if len(content_pieces) < 2:
                return 0.5  # Pas de synergie possible avec un seul format
            
            synergy_factors = {
                'format_diversity': len(content_pieces) / 7,  # Max 7 formats principaux
                'quality_consistency': await self._calculate_quality_consistency(format_optimizations),
                'content_coherence': await self._calculate_content_coherence(content_pieces),
                'platform_coverage': await self._calculate_platform_coverage(format_optimizations),
                'audience_overlap': await self._calculate_audience_overlap(format_optimizations)
            }
            
            # Moyenne pondérée
            weights = [0.2, 0.25, 0.25, 0.15, 0.15]
            synergy_score = sum(
                factor * weight 
                for factor, weight in zip(synergy_factors.values(), weights)
            )
            
            return min(synergy_score, 1.0)
            
        except Exception as e:
            logger.error(f"Erreur calcul synergie: {e}")
            return 0.5
    
    async def _calculate_quality_consistency(
        self, 
        format_optimizations: Dict[str, FormatOptimization]
    ) -> float:
        """Calcule la cohérence de qualité entre formats"""
        try:
            if not format_optimizations:
                return 0.0
            
            scores = [opt.optimization_score for opt in format_optimizations.values()]
            
            # Écart-type pour mesurer la cohérence
            mean_score = sum(scores) / len(scores)
            variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
            std_dev = variance ** 0.5
            
            # Consistance inversement proportionnelle à l'écart-type
            consistency = 1.0 - min(std_dev / 0.5, 1.0)  # Normalisation
            
            return consistency
            
        except Exception as e:
            logger.error(f"Erreur calcul cohérence qualité: {e}")
            return 0.5
    
    async def _calculate_content_coherence(
        self, 
        content_pieces: Dict[ContentFormat, Union[str, bytes, Path]]
    ) -> float:
        """Calcule la cohérence du contenu entre formats"""
        try:
            # Extraction du texte de tous les formats
            text_contents = []
            
            for format_type, content in content_pieces.items():
                if isinstance(content, str):
                    text_contents.append(content)
                # Pour d'autres formats, extraction limitée pour demo
                elif format_type in [ContentFormat.TEXT, ContentFormat.BLOG_POST]:
                    if isinstance(content, Path):
                        try:
                            with open(content, 'r', encoding='utf-8') as f:
                                text_contents.append(f.read())
                        except Exception:
                            pass
            
            if len(text_contents) < 2:
                return 0.7  # Score par défaut
            
            # Similarité sémantique entre contenus
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(text_contents)
            
            # Similarité moyenne
            similarities = []
            for i in range(len(text_contents)):
                for j in range(i + 1, len(text_contents)):
                    similarity = cosine_similarity(
                        tfidf_matrix[i], tfidf_matrix[j]
                    )[0][0]
                    similarities.append(similarity)
            
            coherence = sum(similarities) / len(similarities) if similarities else 0.5
            
            return min(coherence, 1.0)
            
        except Exception as e:
            logger.error(f"Erreur calcul cohérence contenu: {e}")
            return 0.5
    
    async def _calculate_platform_coverage(
        self, 
        format_optimizations: Dict[str, FormatOptimization]
    ) -> float:
        """Calcule la couverture de plateformes"""
        try:
            all_platforms = set()
            
            for optimization in format_optimizations.values():
                platforms = optimization.platform_adaptations.keys()
                all_platforms.update(platforms)
            
            # Score basé sur le nombre de plateformes couvertes
            platform_coverage = len(all_platforms) / len(PlatformType)
            
            return min(platform_coverage, 1.0)
            
        except Exception as e:
            logger.error(f"Erreur calcul couverture plateformes: {e}")
            return 0.5
    
    async def _calculate_audience_overlap(
        self, 
        format_optimizations: Dict[str, FormatOptimization]
    ) -> float:
        """Calcule le chevauchement d'audience"""
        try:
            # Simulation d'analyse d'audience
            # En production, ceci utiliserait des données d'audience réelles
            
            audience_scores = []
            for optimization in format_optimizations.values():
                # Score basé sur les métriques de contenu
                engagement_pred = optimization.performance_predictions.get('engagement', 0.5)
                audience_scores.append(engagement_pred)
            
            if not audience_scores:
                return 0.5
            
            # Variance de l'audience (plus elle est faible, plus le chevauchement est élevé)
            mean_score = sum(audience_scores) / len(audience_scores)
            variance = sum((score - mean_score) ** 2 for score in audience_scores) / len(audience_scores)
            
            # Chevauchement inversement proportionnel à la variance
            overlap = 1.0 - min(variance, 1.0)
            
            return overlap
            
        except Exception as e:
            logger.error(f"Erreur calcul chevauchement audience: {e}")
            return 0.5
    
    async def _calculate_unified_score_advanced(
        self,
        format_optimizations: Dict[str, FormatOptimization],
        synergy_analysis: Dict[str, Any]
    ) -> float:
        """Calcule le score SEO unifié avancé avec synergie"""
        try:
            if not format_optimizations:
                return 0.0
            
            # Scores individuels
            individual_scores = [opt.optimization_score for opt in format_optimizations.values()]
            base_score = sum(individual_scores) / len(individual_scores)
            
            # Bonus de synergie
            synergy_bonus = synergy_analysis.get('cross_format_synergy_score', 0.0) * 0.2
            
            # Bonus de diversité
            diversity_bonus = min(len(format_optimizations) / 5, 0.1)  # Max 10% bonus
            
            # Bonus de qualité
            quality_bonus = 0.0
            high_quality_count = sum(
                1 for opt in format_optimizations.values() 
                if opt.quality_level in [ContentQuality.HIGH, ContentQuality.PREMIUM, ContentQuality.VIRAL_POTENTIAL]
            )
            if high_quality_count > 0:
                quality_bonus = (high_quality_count / len(format_optimizations)) * 0.15
            
            # Score final
            unified_score = base_score + synergy_bonus + diversity_bonus + quality_bonus
            
            return min(unified_score, 1.0)
            
        except Exception as e:
            logger.error(f"Erreur calcul score unifié: {e}")
            return 0.5

# Classes d'adaptation par plateforme
class PlatformAdapter:
    """Classe de base pour adaptateurs de plateforme"""
    
    def __init__(self, config -> None: Dict[str, Any]) -> None:
        self.config = config
    
    async def adapt_content(self, content: str, format_type: ContentFormat) -> Dict[str, Any]:
        """Adapte le contenu pour la plateforme"""
        return {"adapted_content": content}

class YouTubeAdapter(PlatformAdapter):
    """Adaptateur YouTube"""
    
    async def adapt_content(self, content: str, format_type: ContentFormat) -> Dict[str, Any]:
        adaptations = {
            "title_optimization": await self._optimize_youtube_title(content),
            "description_optimization": await self._optimize_youtube_description(content),
            "tags_suggestions": await self._generate_youtube_tags(content),
            "thumbnail_suggestions": await self._suggest_thumbnail_elements(content),
            "chapters_suggestions": await self._suggest_chapters(content)
        }
        return adaptations
    
    async def _optimize_youtube_title(self, content: str) -> str:
        # Optimisation titre YouTube (60 caractères max)
        words = content.split()[:10]  # Premiers mots
        title = " ".join(words)
        return title[:60] + "..." if len(title) > 60 else title
    
    async def _optimize_youtube_description(self, content: str) -> str:
        # Description optimisée pour YouTube
        return f"{content[:200]}...\n\n🔔 Abonnez-vous pour plus de contenu!\n💬 Commentez vos questions"
    
    async def _generate_youtube_tags(self, content: str) -> List[str]:
        # Génération de tags YouTube
        return ["tutorial", "guide", "tips", "howto", "2025"]
    
    async def _suggest_thumbnail_elements(self, content: str) -> List[str]:
        return ["text overlay", "bright colors", "faces", "contrast"]
    
    async def _suggest_chapters(self, content: str) -> List[Dict[str, str]]:
        return [
            {"time": "0:00", "title": "Introduction"},
            {"time": "2:00", "title": "Contenu principal"},
            {"time": "8:00", "title": "Conclusion"}
        ]

class InstagramAdapter(PlatformAdapter):
    """Adaptateur Instagram"""
    
    async def adapt_content(self, content: str, format_type: ContentFormat) -> Dict[str, Any]:
        return {
            "caption_optimization": await self._optimize_instagram_caption(content),
            "hashtags_suggestions": await self._generate_instagram_hashtags(content),
            "story_adaptations": await self._adapt_for_stories(content),
            "reel_suggestions": await self._suggest_reel_format(content)
        }
    
    async def _optimize_instagram_caption(self, content: str) -> str:
        # Caption Instagram avec émojis et CTA
        return f"{content[:150]}... ✨\n\n👆 Suivez pour plus de conseils!\n💬 Partagez en commentaire"
    
    async def _generate_instagram_hashtags(self, content: str) -> List[str]:
        return ["#marketing", "#digital", "#tips", "#entrepreneur", "#business"]
    
    async def _adapt_for_stories(self, content: str) -> Dict[str, Any]:
        return {
            "story_slides": 3,
            "interactive_elements": ["poll", "question", "slider"],
            "visual_suggestions": ["gradient background", "animated text"]
        }
    
    async def _suggest_reel_format(self, content: str) -> Dict[str, Any]:
        return {
            "duration": "15-30 seconds",
            "hook": content.split('.')[0] if '.' in content else content[:50],
            "music_suggestions": ["trending", "upbeat", "background"],
            "effects": ["quick cuts", "text animations", "transitions"]
        }

# Classes d'adaptation simplifiées pour autres plateformes
class TikTokAdapter(PlatformAdapter):
    """TikTokAdapter class implementation"""
    async def adapt_content(self, content: str, format_type: ContentFormat) -> Dict[str, Any]:
        return {"short_form_optimization": True, "trending_sounds": [], "effects": []}

class LinkedInAdapter(PlatformAdapter):
    """LinkedInAdapter class implementation"""
    async def adapt_content(self, content: str, format_type: ContentFormat) -> Dict[str, Any]:
        return {"professional_tone": True, "industry_hashtags": [], "thought_leadership": True}

class TwitterAdapter(PlatformAdapter):
    """TwitterAdapter class implementation"""
    async def adapt_content(self, content: str, format_type: ContentFormat) -> Dict[str, Any]:
        return {"thread_structure": True, "character_optimization": True, "trending_hashtags": []}

class FacebookAdapter(PlatformAdapter):
    """FacebookAdapter class implementation"""
    async def adapt_content(self, content: str, format_type: ContentFormat) -> Dict[str, Any]:
        return {"engagement_optimization": True, "community_focus": True, "sharing_encouragement": True}

class SpotifyAdapter(PlatformAdapter):
    """SpotifyAdapter class implementation"""
    async def adapt_content(self, content: str, format_type: ContentFormat) -> Dict[str, Any]:
        return {"episode_optimization": True, "playlist_suggestions": [], "show_notes": True}

# Classes utilitaires
class ContentCoordinator:
    """Coordinateur de contenu multi-format"""
    
    async def coordinate_content_release(self, formats: List[ContentFormat]) -> Dict[str, Any]:
        return {"release_schedule": {}, "cross_promotion": {}}

class PerformancePredictor:
    """Prédicteur de performance"""
    
    async def predict_performance(self, content_data: Dict[str, Any]) -> Dict[str, float]:
        return {"engagement": 0.7, "reach": 0.6, "conversion": 0.5}

# Export des classes principales
__all__ = [
    'ContentFormatSEOOptimizer',
    'VoiceSearchOptimizationEngine', 
    'MultiFormatContentSEOOptimizer',
    'FormatOptimization',
    'VoiceSearchOptimization',
    'MultiFormatStrategy',
    'ContentFormat',
    'VoiceSearchType',
    'OptimizationLevel',
    'ContentQuality',
    'PlatformType',
    'ContentMetrics',
    'ContentFormatAnalyzer',
    'PlatformAdapter',
    'YouTubeAdapter',
    'InstagramAdapter',
    'TikTokAdapter',
    'LinkedInAdapter',
    'TwitterAdapter',
    'FacebookAdapter',
    'SpotifyAdapter'
]
