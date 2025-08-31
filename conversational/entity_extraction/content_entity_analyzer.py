"""Content Entity Analyzer - Advanced Content Analysis

Specialized content entity analysis for multi-format creative content with
intelligent metadata extraction, content type detection, and creative industry
specific entity recognition for musicians, influencers, and content creators.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written 
permission is strictly prohibited and will be prosecuted to the full extent of the law.
Contact: mlaiel@live.de
"""
import asyncio
import mimetypes
from typing import Dict, List, Set, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging
import json
import hashlib

import numpy as np
from PIL import Image, ExifTags
import cv2
import librosa
import mutagen
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC
import spacy
from transformers import pipeline

from ...core.base_service import BaseService
from ...core.cache import cache_manager
from ...core.monitoring import MetricsCollector
from ...models.content import ContentType, ContentMetadata, CreativeContent
from ...utils.file_processors import FileProcessor
from ...utils.media_analyzers import MediaAnalyzer
from .entity_extractor import ExtractedEntity, EntityCategory


class ContentFormat(Enum):
    """Supported content formats"""    # Audio formats
    AUDIO_MP3 = "audio/mp3"
    AUDIO_WAV = "audio/wav"
    AUDIO_FLAC = "audio/flac"
    AUDIO_AAC = "audio/aac"
    AUDIO_OGG = "audio/ogg"
    
    # Video formats
    VIDEO_MP4 = "video/mp4"
    VIDEO_AVI = "video/avi"
    VIDEO_MOV = "video/mov"
    VIDEO_MKV = "video/mkv"
    VIDEO_WEBM = "video/webm"
    
    # Image formats
    IMAGE_JPEG = "image/jpeg"
    IMAGE_PNG = "image/png"
    IMAGE_GIF = "image/gif"
    IMAGE_WEBP = "image/webp"
    IMAGE_TIFF = "image/tiff"
    
    # Text formats
    TEXT_PLAIN = "text/plain"
    TEXT_MARKDOWN = "text/markdown"
    TEXT_HTML = "text/html"
    TEXT_JSON = "application/json"


class CreativeRole(Enum):
    """Creative roles in content"""    ARTIST = "artist"
    PRODUCER = "producer"
    SONGWRITER = "songwriter"
    PERFORMER = "performer"
    MIXER = "mixer"
    MASTERING_ENGINEER = "mastering_engineer"
    PHOTOGRAPHER = "photographer"
    VIDEOGRAPHER = "videographer"
    DIRECTOR = "director"
    EDITOR = "editor"
    COMPOSER = "composer"
    LYRICIST = "lyricist"


@dataclass
class ContentEntity:
    """Content-specific entity with creative context"""    entity: ExtractedEntity
    content_role: Optional[CreativeRole]
    content_context: str
    technical_metadata: Dict[str, Any] = field(default_factory=dict)
    creative_metadata: Dict[str, Any] = field(default_factory=dict)
    quality_score: float = 0.0
    relevance_score: float = 0.0


@dataclass
class ContentAnalysisResult:
    """Result of content entity analysis"""    content_type: ContentType
    content_format: ContentFormat
    entities: List[ContentEntity]
    metadata: ContentMetadata
    technical_analysis: Dict[str, Any]
    creative_analysis: Dict[str, Any]
    quality_metrics: Dict[str, float]
    processing_time: float
    confidence_score: float


class ContentEntityAnalyzer(BaseService):
    """    Advanced Content Entity Analyzer for creative industry content.
    
    Features:
    - Multi-format content analysis (audio, video, image, text)
    - Creative industry metadata extraction
    - Technical and artistic entity recognition
    - Quality assessment and scoring
    - Content type and format detection
    - Role-based entity classification
    - Cross-platform content correlation
    - Metadata standardization and enrichment
    """    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.metrics = MetricsCollector("content_entity_analyzer")
        self.file_processor = FileProcessor()
        self.media_analyzer = MediaAnalyzer()
        
        # Content analyzers
        self.audio_analyzer = None
        self.video_analyzer = None
        self.image_analyzer = None
        self.text_analyzer = None
        
        # ML models for content analysis
        self.content_classifier = None
        self.quality_assessor = None
        
        # Content vocabularies
        self.creative_vocabularies = {}
        
        # Analysis cache
        self.analysis_cache = {}
        
        # Statistics
        self.analysis_stats = {
            'total_analyses': 0,
            'successful_analyses': 0,
            'content_type_distribution': {},
            'avg_processing_time': 0.0,
            'format_distribution': {}
        }
        
    async def initialize(self):
        """Initialize content analysis resources"""        try:
            self.logger.info("Initializing ContentEntityAnalyzer...")
            
            # Load content classification models
            await self._load_content_models()
            
            # Initialize format-specific analyzers
            await self._initialize_format_analyzers()
            
            # Load creative vocabularies
            await self._load_creative_vocabularies()
            
            # Initialize quality assessment models
            await self._initialize_quality_models()
            
            self.logger.info("ContentEntityAnalyzer initialization completed")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ContentEntityAnalyzer: {str(e)}")
            raise
    
    async def _load_content_models(self):
        """Load comprehensive machine learning models for advanced content analysis"""        try:
            # Primary content classification model with creative industry fine-tuning
            self.content_classifier = pipeline(
                "text-classification",
                model="microsoft/DialoGPT-medium",
                return_all_scores=True,
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Advanced quality assessment model for creative content
            self.quality_assessor = pipeline(
                "text-classification",
                model="facebook/bart-large-mnli",
                return_all_scores=True
            )
            
            # Genre classification model for music content
            self.genre_classifier = pipeline(
                "audio-classification",
                model="facebook/wav2vec2-base-960h",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Content moderation and safety model
            self.content_moderator = pipeline(
                "text-classification",
                model="unitary/toxic-bert",
                return_all_scores=True
            )
            
            # Creative style analyzer
            self.style_analyzer = pipeline(
                "feature-extraction",
                model="sentence-transformers/all-MiniLM-L6-v2"
            )
            
            # Technical quality assessment for audio/video
            self.technical_quality_assessor = self._initialize_technical_quality_model()
            
            # Content sentiment and mood analyzer
            self.mood_analyzer = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                return_all_scores=True
            )
            
            # SEO and discoverability optimizer
            self.seo_optimizer = self._initialize_seo_optimization_model()
            
            # Collaborative filtering for content recommendation
            self.content_recommender = self._initialize_content_recommendation_model()
            
            # Load spaCy model for advanced NLP processing
            try:
                self.nlp = spacy.load("en_core_web_lg")
            except OSError:
                try:
                    self.nlp = spacy.load("en_core_web_md")
                except OSError:
                    self.nlp = spacy.load("en_core_web_sm")
                    self.logger.warning("Using basic spaCy model as fallback")
            
            self.logger.info("Successfully loaded all content analysis models")
            
        except Exception as e:
            self.logger.error(f"Failed to load content models: {str(e)}")
            # Load fallback models
            await self._load_fallback_content_models()
    
    def _initialize_technical_quality_model(self):
        """Initialize technical quality assessment model for media content"""        import torch.nn as nn
        
        class TechnicalQualityAssessor(nn.Module):
            def __init__(self, input_dim=100, hidden_dims=[256, 128, 64]):
                super(TechnicalQualityAssessor, self).__init__()
                
                layers = []
                prev_dim = input_dim
                
                for hidden_dim in hidden_dims:
                    layers.extend([
                        nn.Linear(prev_dim, hidden_dim),
                        nn.ReLU(),
                        nn.BatchNorm1d(hidden_dim),
                        nn.Dropout(0.25)
                    ])
                    prev_dim = hidden_dim
                
                # Output layers for different quality metrics
                self.audio_quality = nn.Linear(prev_dim, 1)
                self.video_quality = nn.Linear(prev_dim, 1)
                self.image_quality = nn.Linear(prev_dim, 1)
                
                self.shared_layers = nn.Sequential(*layers)
                
            def forward(self, x, content_type):
                features = self.shared_layers(x)
                
                if content_type == 'audio':
                    return torch.sigmoid(self.audio_quality(features))
                elif content_type == 'video':
                    return torch.sigmoid(self.video_quality(features))
                elif content_type == 'image':
                    return torch.sigmoid(self.image_quality(features))
                else:
                    # Return average quality score for unknown types
                    return (torch.sigmoid(self.audio_quality(features)) + 
                           torch.sigmoid(self.video_quality(features)) + 
                           torch.sigmoid(self.image_quality(features))) / 3
        
        model = TechnicalQualityAssessor()
        
        # Load pre-trained weights if available
        quality_model_path = self.config.get('technical_quality_model_path')
        if quality_model_path:
            try:
                model.load_state_dict(torch.load(quality_model_path))
                self.logger.info("Loaded pre-trained technical quality model")
            except Exception as e:
                self.logger.warning(f"Could not load quality model weights: {e}")
        
        return model
    
    def _initialize_seo_optimization_model(self):
        """Initialize SEO optimization model for content discoverability"""        import torch.nn as nn
        
        class SEOOptimizer(nn.Module):
            def __init__(self, vocab_size=50000, embedding_dim=300, hidden_dim=512):
                super(SEOOptimizer, self).__init__()
                self.embedding = nn.Embedding(vocab_size, embedding_dim)
                self.lstm = nn.LSTM(embedding_dim, hidden_dim, batch_first=True, bidirectional=True)
                self.dropout = nn.Dropout(0.3)
                
                # Multiple output heads for different SEO aspects
                self.keyword_relevance = nn.Linear(hidden_dim * 2, 1)
                self.title_optimization = nn.Linear(hidden_dim * 2, 1)
                self.description_quality = nn.Linear(hidden_dim * 2, 1)
                self.hashtag_effectiveness = nn.Linear(hidden_dim * 2, 1)
                
            def forward(self, input_ids):
                embeddings = self.embedding(input_ids)
                lstm_out, _ = self.lstm(embeddings)
                lstm_out = self.dropout(lstm_out)
                
                # Global max pooling
                pooled = torch.max(lstm_out, dim=1)[0]
                
                return {
                    'keyword_relevance': torch.sigmoid(self.keyword_relevance(pooled)),
                    'title_optimization': torch.sigmoid(self.title_optimization(pooled)),
                    'description_quality': torch.sigmoid(self.description_quality(pooled)),
                    'hashtag_effectiveness': torch.sigmoid(self.hashtag_effectiveness(pooled))
                }
        
        model = SEOOptimizer()
        
        # Load pre-trained weights if available
        seo_model_path = self.config.get('seo_optimization_model_path')
        if seo_model_path:
            try:
                model.load_state_dict(torch.load(seo_model_path))
                self.logger.info("Loaded pre-trained SEO optimization model")
            except Exception as e:
                self.logger.warning(f"Could not load SEO model weights: {e}")
        
        return model
    
    def _initialize_content_recommendation_model(self):
        """Initialize content recommendation model for similar content discovery"""        import torch.nn as nn
        from sklearn.decomposition import NMF
        from sklearn.feature_extraction.text import TfidfVectorizer
        
        class ContentRecommender:
            def __init__(self, n_components=50, max_features=10000):
                self.nmf = NMF(n_components=n_components, random_state=42)
                self.tfidf = TfidfVectorizer(
                    max_features=max_features,
                    stop_words='english',
                    ngram_range=(1, 3)
                )
                self.is_fitted = False
                self.content_embeddings = {}
                
            def fit(self, content_corpus):
                """Fit the recommendation model on content corpus"""                try:
                    tfidf_matrix = self.tfidf.fit_transform(content_corpus)
                    self.nmf.fit(tfidf_matrix)
                    self.is_fitted = True
                    return True
                except Exception as e:
                    logging.error(f"Failed to fit content recommender: {e}")
                    return False
            
            def get_recommendations(self, content_text, n_recommendations=5):
                """Get content recommendations based on similarity"""                if not self.is_fitted:
                    return []
                
                try:
                    content_tfidf = self.tfidf.transform([content_text])
                    content_topics = self.nmf.transform(content_tfidf)
                    
                    # Compute similarity with existing content
                    similarities = []
                    for content_id, embedding in self.content_embeddings.items():
                        similarity = cosine_similarity(content_topics, embedding)[0][0]
                        similarities.append((content_id, similarity))
                    
                    # Sort by similarity and return top recommendations
                    similarities.sort(key=lambda x: x[1], reverse=True)
                    return similarities[:n_recommendations]
                    
                except Exception as e:
                    logging.error(f"Failed to get recommendations: {e}")
                    return []
            
            def add_content(self, content_id, content_text):
                """Add new content to the recommendation system"""                if not self.is_fitted:
                    return False
                
                try:
                    content_tfidf = self.tfidf.transform([content_text])
                    content_topics = self.nmf.transform(content_tfidf)
                    self.content_embeddings[content_id] = content_topics
                    return True
                except Exception as e:
                    logging.error(f"Failed to add content: {e}")
                    return False
        
        return ContentRecommender()
    
    async def _load_fallback_content_models(self):
        """Load simplified fallback models if advanced models fail"""        try:
            # Basic content classifier
            self.content_classifier = pipeline(
                "text-classification",
                model="distilbert-base-uncased-finetuned-sst-2-english"
            )
            
            # Basic sentiment analyzer
            self.mood_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
            
            # Basic spaCy model
            self.nlp = spacy.load("en_core_web_sm")
            
            self.logger.info("Loaded fallback content models")
            
        except Exception as e:
            self.logger.error(f"Failed to load fallback content models: {e}")
            
            self.logger.info("Loaded content analysis models")
            
        except Exception as e:
            self.logger.warning(f"Failed to load some content models: {str(e)}")
    
    async def _initialize_format_analyzers(self):
        """Initialize format-specific analyzers"""        try:
            # Audio analyzer initialization
            self.audio_analyzer = {
                'supported_formats': ['.mp3', '.wav', '.flac', '.aac', '.ogg'],
                'features': ['tempo', 'key', 'loudness', 'spectral_features']
            }
            
            # Video analyzer initialization
            self.video_analyzer = {
                'supported_formats': ['.mp4', '.avi', '.mov', '.mkv', '.webm'],
                'features': ['resolution', 'frame_rate', 'duration', 'codec']
            }
            
            # Image analyzer initialization
            self.image_analyzer = {
                'supported_formats': ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.tiff'],
                'features': ['resolution', 'color_space', 'compression', 'metadata']
            }
            
            # Text analyzer initialization (spaCy)
            try:
                self.text_analyzer = spacy.load("en_core_web_sm")
            except OSError:
                self.logger.warning("spaCy model not available for text analysis")
                self.text_analyzer = None
            
            self.logger.info("Initialized format-specific analyzers")
            
        except Exception as e:
            self.logger.warning(f"Failed to initialize some analyzers: {str(e)}")
    
    async def _load_creative_vocabularies(self):
        """Load creative industry vocabularies"""        self.creative_vocabularies = {
            'audio_terms': {
                'instruments': {
                    'guitar', 'piano', 'drums', 'bass', 'violin', 'trumpet', 'saxophone',
                    'synthesizer', 'keyboard', 'flute', 'clarinet', 'cello', 'harp'
                },
                'techniques': {
                    'reverb', 'delay', 'compression', 'eq', 'distortion', 'chorus',
                    'flanger', 'phaser', 'overdrive', 'sustain', 'vibrato', 'tremolo'
                },
                'genres': {
                    'rock', 'pop', 'jazz', 'classical', 'electronic', 'hip-hop',
                    'country', 'blues', 'reggae', 'folk', 'metal', 'punk'
                }
            },
            'video_terms': {
                'techniques': {
                    'close-up', 'wide shot', 'pan', 'tilt', 'zoom', 'dolly',
                    'handheld', 'steadicam', 'time-lapse', 'slow motion'
                },
                'equipment': {
                    'camera', 'lens', 'tripod', 'gimbal', 'drone', 'lighting',
                    'microphone', 'boom', 'reflector', 'diffuser'
                }
            },
            'image_terms': {
                'techniques': {
                    'portrait', 'landscape', 'macro', 'wide angle', 'telephoto',
                    'bokeh', 'depth of field', 'exposure', 'composition'
                },
                'styles': {
                    'documentary', 'fashion', 'street', 'nature', 'architectural',
                    'abstract', 'candid', 'staged', 'black and white'
                }
            },
            'business_terms': {
                'licensing': {
                    'copyright', 'royalty', 'sync license', 'mechanical license',
                    'performance rights', 'publishing', 'distribution'
                },
                'platforms': {
                    'spotify', 'apple music', 'youtube', 'instagram', 'tiktok',
                    'soundcloud', 'bandcamp', 'facebook', 'twitter'
                }
            }
        }
    
    async def _initialize_quality_models(self):
        """Initialize quality assessment models"""        try:
            # Audio quality metrics
            self.quality_metrics = {
                'audio': {
                    'technical': ['sample_rate', 'bit_depth', 'dynamic_range', 'thd'],
                    'perceptual': ['loudness', 'clarity', 'balance', 'spatial_quality']
                },
                'video': {
                    'technical': ['resolution', 'bitrate', 'frame_rate', 'compression'],
                    'perceptual': ['sharpness', 'color_accuracy', 'motion_blur', 'artifacts']
                },
                'image': {
                    'technical': ['resolution', 'bit_depth', 'compression_ratio'],
                    'perceptual': ['sharpness', 'noise_level', 'color_balance', 'exposure']
                },
                'text': {
                    'technical': ['encoding', 'structure', 'metadata_completeness'],
                    'perceptual': ['readability', 'coherence', 'relevance', 'sentiment']
                }
            }
            
            self.logger.info("Initialized quality assessment models")
            
        except Exception as e:
            self.logger.warning(f"Failed to initialize quality models: {str(e)}")
    
    @cache_manager.cached(ttl=3600)
    async def analyze_content(
        self,
        content_path: str,
        content_data: Optional[bytes] = None,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> ContentAnalysisResult:
        """        Analyze content for entity extraction and metadata enrichment.
        
        Args:
            content_path: Path to content file
            content_data: Raw content data (if not reading from file)
            additional_metadata: Additional metadata context
            
        Returns:
            ContentAnalysisResult with extracted entities and analysis
        """        start_time = datetime.now()
        
        try:
            self.logger.debug(f"Analyzing content: {content_path}")
            self.metrics.increment('analysis_requests')
            
            # Detect content type and format
            content_type, content_format = await self._detect_content_type_and_format(
                content_path, content_data
            )
            
            # Load content metadata
            metadata = await self._extract_content_metadata(content_path, content_data, content_type)
            
            # Perform format-specific analysis
            if content_type == ContentType.AUDIO:
                analysis_result = await self._analyze_audio_content(content_path, content_data, metadata)
            elif content_type == ContentType.VIDEO:
                analysis_result = await self._analyze_video_content(content_path, content_data, metadata)
            elif content_type == ContentType.IMAGE:
                analysis_result = await self._analyze_image_content(content_path, content_data, metadata)
            elif content_type == ContentType.TEXT:
                analysis_result = await self._analyze_text_content(content_path, content_data, metadata)
            else:
                analysis_result = await self._analyze_generic_content(content_path, content_data, metadata)
            
            # Enhance with additional metadata
            if additional_metadata:
                analysis_result.metadata.update(additional_metadata)
            
            # Calculate overall quality and confidence scores
            quality_score = self._calculate_overall_quality_score(analysis_result)
            confidence_score = self._calculate_analysis_confidence(analysis_result)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Create final result
            result = ContentAnalysisResult(
                content_type=content_type,
                content_format=content_format,
                entities=analysis_result.get('entities', []),
                metadata=metadata,
                technical_analysis=analysis_result.get('technical_analysis', {}),
                creative_analysis=analysis_result.get('creative_analysis', {}),
                quality_metrics=analysis_result.get('quality_metrics', {}),
                processing_time=processing_time,
                confidence_score=confidence_score
            )
            
            # Update statistics
            self._update_analysis_stats(result)
            
            self.logger.info(f"Content analysis completed: {content_path} ({content_type.value}) in {processing_time:.3f}s")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Content analysis failed: {str(e)}")
            self.metrics.increment('analysis_errors')
            raise
    
    async def _detect_content_type_and_format(
        self,
        content_path: str,
        content_data: Optional[bytes]
    ) -> Tuple[ContentType, ContentFormat]:
        """Detect content type and format"""        # Get MIME type
        mime_type, _ = mimetypes.guess_type(content_path)
        
        if not mime_type and content_data:
            # Try to detect from content data
            mime_type = self._detect_mime_from_data(content_data)
        
        # Map MIME type to our enums
        content_type = self._map_mime_to_content_type(mime_type)
        content_format = self._map_mime_to_content_format(mime_type)
        
        return content_type, content_format
    
    def _detect_mime_from_data(self, data: bytes) -> Optional[str]:
        """Detect MIME type from binary data"""        # Simple magic number detection
        if data.startswith(b'\xff\xfb') or data.startswith(b'ID3'):
            return 'audio/mp3'
        elif data.startswith(b'RIFF') and b'WAVE' in data[:12]:
            return 'audio/wav'
        elif data.startswith(b'\xff\xd8\xff'):
            return 'image/jpeg'
        elif data.startswith(b'\x89PNG'):
            return 'image/png'
        elif data.startswith(b'GIF8'):
            return 'image/gif'
        elif data.startswith(b'\x00\x00\x00\x18ftypmp4') or data.startswith(b'\x00\x00\x00 ftyp'):
            return 'video/mp4'
        
        return None
    
    def _map_mime_to_content_type(self, mime_type: Optional[str]) -> ContentType:
        """Map MIME type to ContentType enum"""        if not mime_type:
            return ContentType.UNKNOWN
            
        if mime_type.startswith('audio/'):
            return ContentType.AUDIO
        elif mime_type.startswith('video/'):
            return ContentType.VIDEO
        elif mime_type.startswith('image/'):
            return ContentType.IMAGE
        elif mime_type.startswith('text/'):
            return ContentType.TEXT
        else:
            return ContentType.UNKNOWN
    
    def _map_mime_to_content_format(self, mime_type: Optional[str]) -> ContentFormat:
        """Map MIME type to ContentFormat enum"""        if not mime_type:
            return ContentFormat.TEXT_PLAIN  # Default
            
        format_mapping = {
            'audio/mp3': ContentFormat.AUDIO_MP3,
            'audio/mpeg': ContentFormat.AUDIO_MP3,
            'audio/wav': ContentFormat.AUDIO_WAV,
            'audio/flac': ContentFormat.AUDIO_FLAC,
            'audio/aac': ContentFormat.AUDIO_AAC,
            'audio/ogg': ContentFormat.AUDIO_OGG,
            'video/mp4': ContentFormat.VIDEO_MP4,
            'video/avi': ContentFormat.VIDEO_AVI,
            'video/quicktime': ContentFormat.VIDEO_MOV,
            'video/x-msvideo': ContentFormat.VIDEO_AVI,
            'image/jpeg': ContentFormat.IMAGE_JPEG,
            'image/png': ContentFormat.IMAGE_PNG,
            'image/gif': ContentFormat.IMAGE_GIF,
            'image/webp': ContentFormat.IMAGE_WEBP,
            'text/plain': ContentFormat.TEXT_PLAIN,
            'text/markdown': ContentFormat.TEXT_MARKDOWN,
            'text/html': ContentFormat.TEXT_HTML,
            'application/json': ContentFormat.TEXT_JSON
        }
        
        return format_mapping.get(mime_type, ContentFormat.TEXT_PLAIN)
    
    async def _extract_content_metadata(
        self,
        content_path: str,
        content_data: Optional[bytes],
        content_type: ContentType
    ) -> ContentMetadata:
        """Extract basic content metadata"""        metadata = ContentMetadata()
        
        try:
            if content_type == ContentType.AUDIO:
                metadata = await self._extract_audio_metadata(content_path, content_data)
            elif content_type == ContentType.VIDEO:
                metadata = await self._extract_video_metadata(content_path, content_data)
            elif content_type == ContentType.IMAGE:
                metadata = await self._extract_image_metadata(content_path, content_data)
            elif content_type == ContentType.TEXT:
                metadata = await self._extract_text_metadata(content_path, content_data)
                
        except Exception as e:
            self.logger.warning(f"Failed to extract metadata: {str(e)}")
        
        return metadata
    
    async def _extract_audio_metadata(self, content_path: str, content_data: Optional[bytes]) -> ContentMetadata:
        """Extract audio file metadata"""        metadata = ContentMetadata()
        
        try:
            # Use mutagen to extract audio metadata
            audio_file = mutagen.File(content_path)
            
            if audio_file:
                # Basic metadata
                metadata.title = str(audio_file.get('TIT2', [''])[0]) if 'TIT2' in audio_file else None
                metadata.artist = str(audio_file.get('TPE1', [''])[0]) if 'TPE1' in audio_file else None
                metadata.album = str(audio_file.get('TALB', [''])[0]) if 'TALB' in audio_file else None
                metadata.year = str(audio_file.get('TDRC', [''])[0]) if 'TDRC' in audio_file else None
                metadata.genre = str(audio_file.get('TCON', [''])[0]) if 'TCON' in audio_file else None
                
                # Technical metadata
                if hasattr(audio_file, 'info'):
                    info = audio_file.info
                    metadata.duration = getattr(info, 'length', 0)
                    metadata.bitrate = getattr(info, 'bitrate', 0)
                    metadata.sample_rate = getattr(info, 'sample_rate', 0)
                    metadata.channels = getattr(info, 'channels', 0)
                
                # Additional audio-specific metadata
                metadata.custom_metadata.update({
                    'codec': str(type(audio_file).__name__),
                    'file_size': audio_file.info.length if hasattr(audio_file, 'info') else 0
                })
                
        except Exception as e:
            self.logger.warning(f"Failed to extract audio metadata: {str(e)}")
        
        return metadata
    
    async def _extract_video_metadata(self, content_path: str, content_data: Optional[bytes]) -> ContentMetadata:
        """Extract video file metadata"""        metadata = ContentMetadata()
        
        try:
            # Use OpenCV to extract video metadata
            cap = cv2.VideoCapture(content_path)
            
            if cap.isOpened():
                # Basic video properties
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                
                metadata.duration = frame_count / fps if fps > 0 else 0
                metadata.width = width
                metadata.height = height
                metadata.frame_rate = fps
                
                metadata.custom_metadata.update({
                    'frame_count': frame_count,
                    'resolution': f"{width}x{height}",
                    'aspect_ratio': width / height if height > 0 else 0
                })
                
            cap.release()
            
        except Exception as e:
            self.logger.warning(f"Failed to extract video metadata: {str(e)}")
        
        return metadata
    
    async def _extract_image_metadata(self, content_path: str, content_data: Optional[bytes]) -> ContentMetadata:
        """Extract image file metadata"""        metadata = ContentMetadata()
        
        try:
            # Use PIL to extract image metadata
            with Image.open(content_path) as img:
                metadata.width = img.width
                metadata.height = img.height
                metadata.format = img.format
                
                # EXIF data
                if hasattr(img, '_getexif') and img._getexif():
                    exif = img._getexif()
                    
                    for tag_id, value in exif.items():
                        tag = ExifTags.TAGS.get(tag_id, tag_id)
                        metadata.custom_metadata[f"exif_{tag}"] = str(value)
                
                metadata.custom_metadata.update({
                    'mode': img.mode,
                    'resolution': f"{img.width}x{img.height}",
                    'aspect_ratio': img.width / img.height if img.height > 0 else 0
                })
                
        except Exception as e:
            self.logger.warning(f"Failed to extract image metadata: {str(e)}")
        
        return metadata
    
    async def _extract_text_metadata(self, content_path: str, content_data: Optional[bytes]) -> ContentMetadata:
        """Extract text file metadata"""        metadata = ContentMetadata()
        
        try:
            # Read text content
            if content_data:
                text_content = content_data.decode('utf-8', errors='ignore')
            else:
                with open(content_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text_content = f.read()
            
            # Basic text statistics
            word_count = len(text_content.split())
            char_count = len(text_content)
            line_count = text_content.count('\n') + 1
            
            metadata.custom_metadata.update({
                'word_count': word_count,
                'character_count': char_count,
                'line_count': line_count,
                'encoding': 'utf-8'
            })
            
            # Language detection (simplified)
            if self.text_analyzer:
                doc = self.text_analyzer(text_content[:1000])  # First 1000 chars
                metadata.language = doc.lang_
            
        except Exception as e:
            self.logger.warning(f"Failed to extract text metadata: {str(e)}")
        
        return metadata
    
    async def _analyze_audio_content(
        self,
        content_path: str,
        content_data: Optional[bytes],
        metadata: ContentMetadata
    ) -> Dict[str, Any]:
        """Analyze audio content for entities and features"""        result = {
            'entities': [],
            'technical_analysis': {},
            'creative_analysis': {},
            'quality_metrics': {}
        }
        
        try:
            # Extract audio features using librosa
            if content_path:
                y, sr = librosa.load(content_path)
                
                # Technical analysis
                tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
                chroma = librosa.feature.chroma_stft(y=y, sr=sr)
                mfcc = librosa.feature.mfcc(y=y, sr=sr)
                spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)
                
                result['technical_analysis'] = {
                    'tempo': float(tempo),
                    'duration': len(y) / sr,
                    'sample_rate': sr,
                    'spectral_centroid_mean': float(np.mean(spectral_centroids)),
                    'mfcc_mean': [float(np.mean(mfcc[i])) for i in range(min(13, len(mfcc)))]
                }
                
                # Creative analysis
                result['creative_analysis'] = {
                    'estimated_key': self._estimate_key_from_chroma(chroma),
                    'energy_level': self._calculate_energy_level(y),
                    'rhythm_complexity': self._analyze_rhythm_complexity(beats),
                    'tonal_characteristics': self._analyze_tonal_characteristics(chroma)
                }
                
                # Extract entities from audio metadata
                entities = await self._extract_audio_entities(metadata, result['technical_analysis'])
                result['entities'] = entities
                
                # Quality metrics
                result['quality_metrics'] = self._calculate_audio_quality_metrics(y, sr, metadata)
            
        except Exception as e:
            self.logger.warning(f"Audio analysis failed: {str(e)}")
        
        return result
    
    async def _analyze_video_content(
        self,
        content_path: str,
        content_data: Optional[bytes],
        metadata: ContentMetadata
    ) -> Dict[str, Any]:
        """Analyze video content for entities and features"""        result = {
            'entities': [],
            'technical_analysis': {},
            'creative_analysis': {},
            'quality_metrics': {}
        }
        
        try:
            # Video technical analysis
            cap = cv2.VideoCapture(content_path)
            
            if cap.isOpened():
                # Sample frames for analysis
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                sample_frames = min(10, frame_count)
                frame_indices = np.linspace(0, frame_count - 1, sample_frames, dtype=int)
                
                brightness_values = []
                contrast_values = []
                
                for frame_idx in frame_indices:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                    ret, frame = cap.read()
                    
                    if ret:
                        # Calculate frame statistics
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        brightness_values.append(np.mean(gray))
                        contrast_values.append(np.std(gray))
                
                result['technical_analysis'] = {
                    'avg_brightness': float(np.mean(brightness_values)) if brightness_values else 0,
                    'avg_contrast': float(np.mean(contrast_values)) if contrast_values else 0,
                    'frame_stability': self._calculate_frame_stability(brightness_values),
                    'resolution_quality': self._assess_resolution_quality(metadata.width, metadata.height)
                }
                
                # Creative analysis
                result['creative_analysis'] = {
                    'visual_complexity': self._analyze_visual_complexity(contrast_values),
                    'color_palette': 'varied',  # Simplified
                    'composition_style': self._analyze_composition_style(metadata)
                }
                
            cap.release()
            
            # Extract entities from video metadata
            entities = await self._extract_video_entities(metadata, result['technical_analysis'])
            result['entities'] = entities
            
            # Quality metrics
            result['quality_metrics'] = self._calculate_video_quality_metrics(metadata, result['technical_analysis'])
            
        except Exception as e:
            self.logger.warning(f"Video analysis failed: {str(e)}")
        
        return result
    
    async def _analyze_image_content(
        self,
        content_path: str,
        content_data: Optional[bytes],
        metadata: ContentMetadata
    ) -> Dict[str, Any]:
        """Analyze image content for entities and features"""        result = {
            'entities': [],
            'technical_analysis': {},
            'creative_analysis': {},
            'quality_metrics': {}
        }
        
        try:
            # Image technical analysis
            with Image.open(content_path) as img:
                # Convert to numpy array for analysis
                img_array = np.array(img)
                
                # Technical metrics
                result['technical_analysis'] = {
                    'resolution': f"{img.width}x{img.height}",
                    'aspect_ratio': img.width / img.height if img.height > 0 else 0,
                    'color_mode': img.mode,
                    'bit_depth': self._calculate_bit_depth(img),
                    'file_size': metadata.custom_metadata.get('file_size', 0)
                }
                
                # Creative analysis
                if len(img_array.shape) == 3:  # Color image
                    result['creative_analysis'] = {
                        'dominant_colors': self._extract_dominant_colors(img_array),
                        'brightness_level': float(np.mean(img_array)),
                        'contrast_level': float(np.std(img_array)),
                        'color_distribution': self._analyze_color_distribution(img_array)
                    }
                else:  # Grayscale
                    result['creative_analysis'] = {
                        'brightness_level': float(np.mean(img_array)),
                        'contrast_level': float(np.std(img_array)),
                        'is_grayscale': True
                    }
            
            # Extract entities from image metadata
            entities = await self._extract_image_entities(metadata, result['technical_analysis'])
            result['entities'] = entities
            
            # Quality metrics
            result['quality_metrics'] = self._calculate_image_quality_metrics(metadata, result['technical_analysis'])
            
        except Exception as e:
            self.logger.warning(f"Image analysis failed: {str(e)}")
        
        return result
    
    async def _analyze_text_content(
        self,
        content_path: str,
        content_data: Optional[bytes],
        metadata: ContentMetadata
    ) -> Dict[str, Any]:
        """Analyze text content for entities and features"""        result = {
            'entities': [],
            'technical_analysis': {},
            'creative_analysis': {},
            'quality_metrics': {}
        }
        
        try:
            # Read text content
            if content_data:
                text_content = content_data.decode('utf-8', errors='ignore')
            else:
                with open(content_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text_content = f.read()
            
            # Technical analysis
            result['technical_analysis'] = {
                'word_count': len(text_content.split()),
                'character_count': len(text_content),
                'line_count': text_content.count('\n') + 1,
                'paragraph_count': len([p for p in text_content.split('\n\n') if p.strip()]),
                'encoding': 'utf-8'
            }
            
            # Creative analysis using NLP
            if self.text_analyzer:
                doc = self.text_analyzer(text_content[:10000])  # First 10k chars
                
                result['creative_analysis'] = {
                    'language': doc.lang_,
                    'readability_score': self._calculate_readability_score(text_content),
                    'sentiment_analysis': self._analyze_sentiment(text_content),
                    'topic_keywords': self._extract_topic_keywords(doc),
                    'writing_style': self._analyze_writing_style(doc)
                }
            
            # Extract entities from text content
            entities = await self._extract_text_entities(text_content, metadata)
            result['entities'] = entities
            
            # Quality metrics
            result['quality_metrics'] = self._calculate_text_quality_metrics(text_content, result['technical_analysis'])
            
        except Exception as e:
            self.logger.warning(f"Text analysis failed: {str(e)}")
        
        return result
    
    async def _analyze_generic_content(
        self,
        content_path: str,
        content_data: Optional[bytes],
        metadata: ContentMetadata
    ) -> Dict[str, Any]:
        """Analyze generic content"""        return {
            'entities': [],
            'technical_analysis': {'format': 'unknown'},
            'creative_analysis': {},
            'quality_metrics': {}
        }
    
    # Helper methods for audio analysis
    def _estimate_key_from_chroma(self, chroma: np.ndarray) -> str:
        """Estimate musical key from chroma features"""        try:
            # Simplified key estimation
            chroma_mean = np.mean(chroma, axis=1)
            key_idx = np.argmax(chroma_mean)
            keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            return keys[key_idx]
        except:
            return 'Unknown'
    
    def _calculate_energy_level(self, y: np.ndarray) -> str:
        """Calculate energy level of audio"""        rms = np.sqrt(np.mean(y**2))
        if rms > 0.1:
            return 'High'
        elif rms > 0.05:
            return 'Medium'
        else:
            return 'Low'
    
    def _analyze_rhythm_complexity(self, beats: np.ndarray) -> str:
        """Analyze rhythm complexity"""        if len(beats) < 2:
            return 'Simple'
        
        # Calculate beat interval variations
        intervals = np.diff(beats)
        variation = np.std(intervals) / np.mean(intervals) if np.mean(intervals) > 0 else 0
        
        if variation > 0.2:
            return 'Complex'
        elif variation > 0.1:
            return 'Moderate'
        else:
            return 'Simple'
    
    def _analyze_tonal_characteristics(self, chroma: np.ndarray) -> Dict[str, float]:
        """Analyze tonal characteristics"""        return {
            'harmonic_complexity': float(np.std(np.mean(chroma, axis=1))),
            'tonal_stability': float(1 - np.std(chroma) / np.mean(chroma)) if np.mean(chroma) > 0 else 0
        }
    
    # Helper methods for video analysis
    def _calculate_frame_stability(self, brightness_values: List[float]) -> float:
        """Calculate frame stability score"""        if len(brightness_values) < 2:
            return 1.0
        
        variations = np.std(brightness_values)
        return max(0, 1 - (variations / 100))  # Normalize
    
    def _assess_resolution_quality(self, width: int, height: int) -> str:
        """Assess resolution quality"""        total_pixels = width * height
        
        if total_pixels >= 3840 * 2160:  # 4K
            return 'Ultra High'
        elif total_pixels >= 1920 * 1080:  # 1080p
            return 'High'
        elif total_pixels >= 1280 * 720:  # 720p
            return 'Medium'
        else:
            return 'Low'
    
    def _analyze_visual_complexity(self, contrast_values: List[float]) -> str:
        """Analyze visual complexity"""        if not contrast_values:
            return 'Low'
        
        avg_contrast = np.mean(contrast_values)
        
        if avg_contrast > 50:
            return 'High'
        elif avg_contrast > 25:
            return 'Medium'
        else:
            return 'Low'
    
    def _analyze_composition_style(self, metadata: ContentMetadata) -> str:
        """Analyze composition style from metadata"""        aspect_ratio = metadata.width / metadata.height if metadata.height > 0 else 1
        
        if abs(aspect_ratio - 16/9) < 0.1:
            return 'Cinematic'
        elif abs(aspect_ratio - 1) < 0.1:
            return 'Square'
        elif aspect_ratio > 2:
            return 'Panoramic'
        else:
            return 'Standard'
    
    # Helper methods for image analysis
    def _calculate_bit_depth(self, img: Image.Image) -> int:
        """Calculate bit depth of image"""        mode_bits = {
            '1': 1,      # 1-bit pixels, black and white
            'L': 8,      # 8-bit pixels, grayscale
            'P': 8,      # 8-bit pixels, mapped to any other mode using a color palette
            'RGB': 24,   # 3x8-bit pixels, true color
            'RGBA': 32,  # 4x8-bit pixels, true color with transparency mask
            'CMYK': 32,  # 4x8-bit pixels, color separation
            'YCbCr': 24, # 3x8-bit pixels, color video format
            'LAB': 24,   # 3x8-bit pixels, the L*a*b* color space
            'HSV': 24,   # 3x8-bit pixels, Hue, Saturation, Value color space
        }
        return mode_bits.get(img.mode, 8)
    
    def _extract_dominant_colors(self, img_array: np.ndarray) -> List[str]:
        """Extract dominant colors from image"""        try:
            # Reshape image for clustering
            pixels = img_array.reshape(-1, 3)
            
            # Use KMeans to find dominant colors
            from sklearn.cluster import KMeans
            kmeans = KMeans(n_clusters=5, random_state=42)
            kmeans.fit(pixels[::100])  # Sample pixels for efficiency
            
            # Convert to hex colors
            colors = []
            for color in kmeans.cluster_centers_:
                hex_color = '#{:02x}{:02x}{:02x}'.format(int(color[0]), int(color[1]), int(color[2]))
                colors.append(hex_color)
            
            return colors[:3]  # Return top 3 colors
            
        except:
            return ['#000000']  # Default
    
    def _analyze_color_distribution(self, img_array: np.ndarray) -> Dict[str, float]:
        """Analyze color distribution in image"""        try:
            # Calculate color statistics
            red_mean = float(np.mean(img_array[:, :, 0]))
            green_mean = float(np.mean(img_array[:, :, 1]))
            blue_mean = float(np.mean(img_array[:, :, 2]))
            
            return {
                'red_dominance': red_mean / 255,
                'green_dominance': green_mean / 255,
                'blue_dominance': blue_mean / 255,
                'color_variance': float(np.var(img_array) / (255**2))
            }
        except:
            return {}
    
    # Helper methods for text analysis
    def _calculate_readability_score(self, text: str) -> float:
        """Calculate readability score (simplified Flesch score)"""        try:
            sentences = text.count('.') + text.count('!') + text.count('?')
            words = len(text.split())
            syllables = sum([self._count_syllables(word) for word in text.split()])
            
            if sentences == 0 or words == 0:
                return 0.0
            
            flesch_score = 206.835 - (1.015 * (words / sentences)) - (84.6 * (syllables / words))
            return max(0, min(100, flesch_score)) / 100  # Normalize to 0-1
            
        except:
            return 0.5  # Default
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified)"""        word = word.lower()
        vowels = 'aeiouy'
        syllable_count = 0
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel
        
        # Handle silent 'e'
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1
        
        return max(1, syllable_count)
    
    def _analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of text"""        try:
            if self.content_classifier:
                # Use classifier for sentiment analysis
                results = self.content_classifier(text[:1000])  # First 1000 chars
                
                # Convert to sentiment scores
                sentiment_scores = {
                    'positive': 0.0,
                    'negative': 0.0,
                    'neutral': 0.0
                }
                
                for result in results:
                    label = result['label'].lower()
                    if 'pos' in label:
                        sentiment_scores['positive'] = result['score']
                    elif 'neg' in label:
                        sentiment_scores['negative'] = result['score']
                    else:
                        sentiment_scores['neutral'] = result['score']
                
                return sentiment_scores
            else:
                return {'neutral': 1.0}
                
        except:
            return {'neutral': 1.0}
    
    def _extract_topic_keywords(self, doc) -> List[str]:
        """Extract topic keywords from spaCy doc"""        try:
            # Extract important tokens
            keywords = []
            for token in doc:
                if (token.pos_ in ['NOUN', 'PROPN', 'ADJ'] and 
                    not token.is_stop and 
                    not token.is_punct and 
                    len(token.text) > 2):
                    keywords.append(token.lemma_.lower())
            
            # Return most frequent keywords
            from collections import Counter
            counter = Counter(keywords)
            return [word for word, count in counter.most_common(10)]
            
        except:
            return []
    
    def _analyze_writing_style(self, doc) -> Dict[str, Any]:
        """Analyze writing style from spaCy doc"""        try:
            # Calculate style metrics
            total_tokens = len(doc)
            avg_sentence_length = total_tokens / len(list(doc.sents)) if list(doc.sents) else 0
            
            # POS distribution
            pos_counts = {}
            for token in doc:
                pos_counts[token.pos_] = pos_counts.get(token.pos_, 0) + 1
            
            return {
                'avg_sentence_length': avg_sentence_length,
                'complexity': 'high' if avg_sentence_length > 20 else 'medium' if avg_sentence_length > 10 else 'low',
                'pos_distribution': pos_counts
            }
            
        except:
            return {}
    
    # Entity extraction methods
    async def _extract_audio_entities(
        self,
        metadata: ContentMetadata,
        technical_analysis: Dict[str, Any]
    ) -> List[ContentEntity]:
        """Extract entities from audio content"""        entities = []
        
        # Artist entity
        if metadata.artist:
            entity = ContentEntity(
                entity=ExtractedEntity(
                    text=metadata.artist,
                    entity_type=EntityCategory.PERSON,
                    confidence=0.9,
                    start_pos=0,
                    end_pos=len(metadata.artist),
                    context="audio_metadata"
                ),
                content_role=CreativeRole.ARTIST,
                content_context="audio_file",
                technical_metadata=technical_analysis,
                quality_score=0.8,
                relevance_score=0.9
            )
            entities.append(entity)
        
        # Genre entity
        if metadata.genre:
            entity = ContentEntity(
                entity=ExtractedEntity(
                    text=metadata.genre,
                    entity_type=EntityCategory.GENRE,
                    confidence=0.8,
                    start_pos=0,
                    end_pos=len(metadata.genre),
                    context="audio_metadata"
                ),
                content_role=None,
                content_context="audio_file",
                technical_metadata=technical_analysis,
                quality_score=0.7,
                relevance_score=0.8
            )
            entities.append(entity)
        
        return entities
    
    async def _extract_video_entities(
        self,
        metadata: ContentMetadata,
        technical_analysis: Dict[str, Any]
    ) -> List[ContentEntity]:
        """Extract entities from video content"""        entities = []
        
        # Resolution entity
        if metadata.width and metadata.height:
            resolution_text = f"{metadata.width}x{metadata.height}"
            entity = ContentEntity(
                entity=ExtractedEntity(
                    text=resolution_text,
                    entity_type=EntityCategory.TECHNOLOGY,
                    confidence=0.9,
                    start_pos=0,
                    end_pos=len(resolution_text),
                    context="video_metadata"
                ),
                content_role=None,
                content_context="video_file",
                technical_metadata=technical_analysis,
                quality_score=0.8,
                relevance_score=0.7
            )
            entities.append(entity)
        
        return entities
    
    async def _extract_image_entities(
        self,
        metadata: ContentMetadata,
        technical_analysis: Dict[str, Any]
    ) -> List[ContentEntity]:
        """Extract entities from image content"""        entities = []
        
        # Format entity
        if metadata.format:
            entity = ContentEntity(
                entity=ExtractedEntity(
                    text=metadata.format,
                    entity_type=EntityCategory.TECHNOLOGY,
                    confidence=0.9,
                    start_pos=0,
                    end_pos=len(metadata.format),
                    context="image_metadata"
                ),
                content_role=None,
                content_context="image_file",
                technical_metadata=technical_analysis,
                quality_score=0.8,
                relevance_score=0.6
            )
            entities.append(entity)
        
        return entities
    
    async def _extract_text_entities(
        self,
        text_content: str,
        metadata: ContentMetadata
    ) -> List[ContentEntity]:
        """Extract entities from text content"""        entities = []
        
        if self.text_analyzer:
            doc = self.text_analyzer(text_content[:5000])  # First 5k chars
            
            for ent in doc.ents:
                if ent.label_ in ['PERSON', 'ORG', 'WORK_OF_ART']:
                    entity_category = EntityCategory.PERSON if ent.label_ == 'PERSON' else \
                                    EntityCategory.ORGANIZATION if ent.label_ == 'ORG' else \
                                    EntityCategory.CREATIVE_WORK
                    
                    entity = ContentEntity(
                        entity=ExtractedEntity(
                            text=ent.text,
                            entity_type=entity_category,
                            confidence=0.7,
                            start_pos=ent.start_char,
                            end_pos=ent.end_char,
                            context="text_content"
                        ),
                        content_role=None,
                        content_context="text_file",
                        technical_metadata={},
                        quality_score=0.6,
                        relevance_score=0.7
                    )
                    entities.append(entity)
        
        return entities
    
    # Quality calculation methods
    def _calculate_audio_quality_metrics(
        self,
        y: np.ndarray,
        sr: int,
        metadata: ContentMetadata
    ) -> Dict[str, float]:
        """Calculate audio quality metrics"""        metrics = {}
        
        try:
            # Dynamic range
            dynamic_range = 20 * np.log10(np.max(np.abs(y)) / (np.mean(np.abs(y)) + 1e-10))
            metrics['dynamic_range'] = float(dynamic_range)
            
            # Signal-to-noise ratio (simplified)
            signal_power = np.mean(y**2)
            noise_power = np.var(y - np.mean(y))
            snr = 10 * np.log10(signal_power / (noise_power + 1e-10))
            metrics['snr'] = float(snr)
            
            # Frequency response quality
            fft = np.abs(np.fft.fft(y))
            frequency_balance = np.std(fft[:len(fft)//2])
            metrics['frequency_balance'] = float(frequency_balance)
            
        except Exception as e:
            self.logger.warning(f"Audio quality calculation failed: {str(e)}")
        
        return metrics
    
    def _calculate_video_quality_metrics(
        self,
        metadata: ContentMetadata,
        technical_analysis: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate video quality metrics"""        metrics = {}
        
        # Resolution quality score
        total_pixels = metadata.width * metadata.height if metadata.width and metadata.height else 0
        metrics['resolution_score'] = min(1.0, total_pixels / (1920 * 1080))  # Normalized to 1080p
        
        # Frame rate quality
        frame_rate = metadata.frame_rate or 0
        metrics['frame_rate_score'] = min(1.0, frame_rate / 60)  # Normalized to 60fps
        
        # Brightness stability
        metrics['brightness_stability'] = technical_analysis.get('frame_stability', 0.5)
        
        return metrics
    
    def _calculate_image_quality_metrics(
        self,
        metadata: ContentMetadata,
        technical_analysis: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate image quality metrics"""        metrics = {}
        
        # Resolution quality
        total_pixels = metadata.width * metadata.height if metadata.width and metadata.height else 0
        metrics['resolution_score'] = min(1.0, total_pixels / (1920 * 1080))
        
        # Bit depth quality
        bit_depth = technical_analysis.get('bit_depth', 8)
        metrics['bit_depth_score'] = min(1.0, bit_depth / 24)  # Normalized to 24-bit
        
        return metrics
    
    def _calculate_text_quality_metrics(
        self,
        text_content: str,
        technical_analysis: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate text quality metrics"""        metrics = {}
        
        # Length quality (optimal range)
        word_count = technical_analysis.get('word_count', 0)
        metrics['length_score'] = min(1.0, word_count / 1000) if word_count < 1000 else max(0.5, 1000 / word_count)
        
        # Structure quality
        paragraph_count = technical_analysis.get('paragraph_count', 0)
        metrics['structure_score'] = min(1.0, paragraph_count / 10) if paragraph_count > 0 else 0.1
        
        return metrics
    
    def _calculate_overall_quality_score(self, analysis_result: Dict[str, Any]) -> float:
        """Calculate overall quality score"""        quality_metrics = analysis_result.get('quality_metrics', {})
        
        if not quality_metrics:
            return 0.5  # Default
        
        # Average all quality metrics
        scores = [score for score in quality_metrics.values() if isinstance(score, (int, float))]
        return np.mean(scores) if scores else 0.5
    
    def _calculate_analysis_confidence(self, analysis_result: Dict[str, Any]) -> float:
        """Calculate overall analysis confidence"""        factors = []
        
        # Technical analysis completeness
        tech_analysis = analysis_result.get('technical_analysis', {})
        factors.append(min(1.0, len(tech_analysis) / 5))  # Expect ~5 metrics
        
        # Creative analysis completeness
        creative_analysis = analysis_result.get('creative_analysis', {})
        factors.append(min(1.0, len(creative_analysis) / 3))  # Expect ~3 metrics
        
        # Entity extraction success
        entities = analysis_result.get('entities', [])
        factors.append(min(1.0, len(entities) / 3))  # Expect ~3 entities
        
        return np.mean(factors) if factors else 0.5
    
    def _update_analysis_stats(self, result: ContentAnalysisResult):
        """Update analysis statistics"""        self.analysis_stats['total_analyses'] += 1
        self.analysis_stats['successful_analyses'] += 1
        
        # Update content type distribution
        content_type = result.content_type.value
        self.analysis_stats['content_type_distribution'][content_type] = \
            self.analysis_stats['content_type_distribution'].get(content_type, 0) + 1
        
        # Update format distribution
        content_format = result.content_format.value
        self.analysis_stats['format_distribution'][content_format] = \
            self.analysis_stats['format_distribution'].get(content_format, 0) + 1
        
        # Update average processing time
        current_avg = self.analysis_stats['avg_processing_time']
        total_analyses = self.analysis_stats['total_analyses']
        new_avg = ((current_avg * (total_analyses - 1)) + result.processing_time) / total_analyses
        self.analysis_stats['avg_processing_time'] = new_avg
    
    async def get_analysis_statistics(self) -> Dict[str, Any]:
        """Get content analysis statistics"""        return {
            **self.analysis_stats,
            'supported_formats': {
                'audio': [fmt.value for fmt in ContentFormat if fmt.value.startswith('audio/')],
                'video': [fmt.value for fmt in ContentFormat if fmt.value.startswith('video/')],
                'image': [fmt.value for fmt in ContentFormat if fmt.value.startswith('image/')],
                'text': [fmt.value for fmt in ContentFormat if fmt.value.startswith('text/')]
            },
            'cache_size': len(self.analysis_cache),
            'available_roles': [role.value for role in CreativeRole]
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for content entity analyzer"""        return {
            'status': 'healthy',
            'text_analyzer_available': self.text_analyzer is not None,
            'content_classifier_available': self.content_classifier is not None,
            'supported_formats': len([fmt for fmt in ContentFormat]),
            'total_analyses': self.analysis_stats['total_analyses'],
            'success_rate': (
                self.analysis_stats['successful_analyses'] / 
                max(self.analysis_stats['total_analyses'], 1)
            ) * 100,
            'avg_processing_time': self.analysis_stats['avg_processing_time']
        }
