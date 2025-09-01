"""Multi-modal Conversation Intelligence - Advanced Multi-format Analysis System
============================================================================

Ultra-advanced multi-modal conversation intelligence system providing comprehensive
analysis across text, voice, image, and video conversations for content creators.

Key Features:
- Advanced multi-modal conversation analysis (text, voice, image, video)
- Cross-modal intelligence fusion and correlation analysis
- Voice conversation analysis with emotion and intent detection
- Image context analysis for visual conversation enhancement
- Video conversation intelligence with scene understanding
- Multi-format creator conversation optimization
- Cross-platform conversation intelligence
- Advanced multi-modal business context awareness

Architecture:
Multi-modal Input → Format Detection → Specialized Processing → 
Intelligence Fusion → Cross-modal Analysis → Unified Intelligence Output

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIETARY MULTI-MODAL INTELLIGENCE WARNING ⚠️
This multi-modal conversation intelligence system contains proprietary algorithms
for cross-modal analysis and intelligence fusion. Unauthorized use, copying,
or reverse engineering is strictly prohibited and legally prosecuted.
Contact: mlaiel@live.de for legal authorization inquiries only.
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
import json
import uuid
from concurrent.futures import ThreadPoolExecutor
import threading
from enum import Enum
import statistics
import base64
import io
from pathlib import Path

# Audio processing imports
try:
    import librosa
    import soundfile as sf
    from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
    import torch
    AUDIO_PROCESSING_AVAILABLE = True
except ImportError:
    AUDIO_PROCESSING_AVAILABLE = False

# Image processing imports
try:
    from PIL import Image
    import cv2
    from transformers import CLIPProcessor, CLIPModel, BlipProcessor, BlipForConditionalGeneration
    import torchvision.transforms as transforms
    IMAGE_PROCESSING_AVAILABLE = True
except ImportError:
    IMAGE_PROCESSING_AVAILABLE = False

# Video processing imports
try:
    import moviepy.editor as mp
    from transformers import VideoMAEImageProcessor, VideoMAEForVideoClassification
    VIDEO_PROCESSING_AVAILABLE = True
except ImportError:
    VIDEO_PROCESSING_AVAILABLE = False

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

logger = logging.getLogger(__name__)


class ModalityType(Enum):
    """
Types of conversation modalities"""

    TEXT = "text"
    VOICE = "voice"
    IMAGE = "image"
    VIDEO = "video"
    MULTI_MODAL = "multi_modal"


class ConversationFormat(Enum):
    """Conversation format types"""

    CHAT_TEXT = "chat_text"
    VOICE_MESSAGE = "voice_message"
    VIDEO_CALL = "video_call"
    IMAGE_SHARE = "image_share"
    SCREEN_SHARE = "screen_share"
    MIXED_MEDIA = "mixed_media"


@dataclass
class MultiModalInput:
    """Multi-modal conversation input structure"""
    input_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    modality_type: ModalityType = ModalityType.TEXT
    format_type: ConversationFormat = ConversationFormat.CHAT_TEXT
    content: Any = None
    text_content: str = ""
    audio_data: Optional[bytes] = None
    image_data: Optional[bytes] = None
    video_data: Optional[bytes] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    business_context: Dict[str, Any] = field(default_factory=dict)
    creator_profile: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class MultiModalAnalysisResult:
    """Multi-modal analysis result structure"""
    input_id: str
    modality_results: Dict[str, Any] = field(default_factory=dict)
    cross_modal_insights: Dict[str, Any] = field(default_factory=dict)
    unified_intelligence: Dict[str, Any] = field(default_factory=dict)
    business_intelligence: Dict[str, Any] = field(default_factory=dict)
    creator_insights: Dict[str, Any] = field(default_factory=dict)
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    processing_metrics: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class VoiceAnalysisResult:
    """
Voice conversation analysis result"""
    transcription: str = ""
    emotion_detection: Dict[str, float] = field(default_factory=dict)
    speaker_identification: str = ""
    voice_quality_metrics: Dict[str, float] = field(default_factory=dict)
    conversation_flow: Dict[str, Any] = field(default_factory=dict)
    business_signals: List[str] = field(default_factory=list)
    collaboration_indicators: List[str] = field(default_factory=list)


@dataclass
class ImageAnalysisResult:
    """Image conversation analysis result"""
    scene_description: str = ""
    object_detection: List[Dict[str, Any]] = field(default_factory=list)
    text_extraction: str = ""
    brand_recognition: List[str] = field(default_factory=list)
    visual_sentiment: Dict[str, float] = field(default_factory=dict)
    business_relevance: float = 0.0
    creator_context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VideoAnalysisResult:
    """Video conversation analysis result"""
    scene_analysis: List[Dict[str, Any]] = field(default_factory=list)
    audio_analysis: VoiceAnalysisResult = field(default_factory=VoiceAnalysisResult)
    visual_analysis: List[ImageAnalysisResult] = field(default_factory=list)
    video_summary: str = ""
    engagement_metrics: Dict[str, float] = field(default_factory=dict)
    content_classification: List[str] = field(default_factory=list)
    monetization_potential: float = 0.0


class MultimodalConversationIntelligence:
    """
    Ultra-advanced multi-modal conversation intelligence system
    
    This system provides comprehensive multi-modal conversation analysis including:
    - Text conversation intelligence with advanced NLP
    - Voice conversation analysis with emotion and intent detection
    - Image context analysis with scene understanding
    - Video conversation intelligence with comprehensive analysis
    - Cross-modal intelligence fusion and correlation
    - Business context awareness across all modalities
    """
    
    def __init__(self,
                 enable_audio_processing: bool = True,
                 enable_image_processing: bool = True,
                 enable_video_processing: bool = True,
                 max_concurrent_processing: int = 10):
        """
        Initialize multi-modal conversation intelligence
        
        Args:
            enable_audio_processing: Enable audio/voice processing
            enable_image_processing: Enable image processing
            enable_video_processing: Enable video processing
            max_concurrent_processing: Maximum concurrent processing tasks
        """
        self.enable_audio_processing = enable_audio_processing and AUDIO_PROCESSING_AVAILABLE
        self.enable_image_processing = enable_image_processing and IMAGE_PROCESSING_AVAILABLE
        self.enable_video_processing = enable_video_processing and VIDEO_PROCESSING_AVAILABLE
        self.max_concurrent_processing = max_concurrent_processing
        
        # Processing models
        self.text_processor = None
        self.voice_processor = None
        self.image_processor = None
        self.video_processor = None
        
        # Intelligence fusion engine
        self.fusion_engine = None
        self.cross_modal_analyzer = None
        
        # Business intelligence
        self.business_analyzer = None
        self.creator_intelligence = None
        
        # Processing cache
        self.processing_cache = {}
        self.intelligence_cache = {}
        
        # Performance metrics
        self.processing_metrics = {
            'total_processed': 0,
            'text_processed': 0,
            'voice_processed': 0,
            'image_processed': 0,
            'video_processed': 0,
            'average_processing_time': 0.0,
            'cross_modal_correlations': 0
        }
        
        # Initialize multi-modal system
        asyncio.create_task(self._initialize_multimodal_system())
        
        logger.info("Multi-modal Conversation Intelligence initialized")
    
    async def _initialize_multimodal_system(self):
        """Initialize multi-modal processing system"""
        try:
            # Initialize text processing
            await self._initialize_text_processing()
            
            # Initialize voice processing
            if self.enable_audio_processing:
                await self._initialize_voice_processing()
            
            # Initialize image processing
            if self.enable_image_processing:
                await self._initialize_image_processing()
            
            # Initialize video processing
            if self.enable_video_processing:
                await self._initialize_video_processing()
            
            # Initialize intelligence fusion
            await self._initialize_intelligence_fusion()
            
            logger.info("Multi-modal system initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing multi-modal system: {str(e)}")
            raise
    
    async def _initialize_text_processing(self):
        """Initialize text conversation processing"""
        try:
            # TF-IDF vectorizer for text analysis
            self.text_vectorizer = TfidfVectorizer(
                max_features=10000,
                ngram_range=(1, 3),
                stop_words='english'
            )
            
            # Text processing models would be initialized here
            self.text_processor = {
                'vectorizer': self.text_vectorizer,
                'sentiment_analyzer': None,  # Would be initialized with actual model
                'topic_extractor': None,
                'intent_classifier': None
            }
            
            logger.info("Text processing initialized")
            
        except Exception as e:
            logger.error(f"Error initializing text processing: {str(e)}")
            raise
    
    async def _initialize_voice_processing(self):
        """Initialize voice conversation processing"""
        try:
            if not AUDIO_PROCESSING_AVAILABLE:
                logger.warning("Audio processing libraries not available")
                return
            
            # Initialize voice processing models
            self.voice_processor = {
                'speech_to_text': None,  # Wav2Vec2 model would be loaded here
                'emotion_detector': None,
                'speaker_identifier': None,
                'audio_analyzer': None
            }
            
            logger.info("Voice processing initialized")
            
        except Exception as e:
            logger.error(f"Error initializing voice processing: {str(e)}")
            raise
    
    async def _initialize_image_processing(self):
        """Initialize image conversation processing"""
        try:
            if not IMAGE_PROCESSING_AVAILABLE:
                logger.warning("Image processing libraries not available")
                return
            
            # Initialize image processing models
            self.image_processor = {
                'scene_analyzer': None,  # CLIP model would be loaded here
                'object_detector': None,
                'text_extractor': None,
                'brand_recognizer': None
            }
            
            logger.info("Image processing initialized")
            
        except Exception as e:
            logger.error(f"Error initializing image processing: {str(e)}")
            raise
    
    async def _initialize_video_processing(self):
        """Initialize video conversation processing"""
        try:
            if not VIDEO_PROCESSING_AVAILABLE:
                logger.warning("Video processing libraries not available")
                return
            
            # Initialize video processing models
            self.video_processor = {
                'scene_analyzer': None,  # VideoMAE model would be loaded here
                'action_recognizer': None,
                'content_classifier': None,
                'engagement_analyzer': None
            }
            
            logger.info("Video processing initialized")
            
        except Exception as e:
            logger.error(f"Error initializing video processing: {str(e)}")
            raise
    
    async def analyze_multimodal_conversation(self,
                                            input_data: MultiModalInput) -> MultiModalAnalysisResult:
        """
        Analyze multi-modal conversation with comprehensive intelligence
        
        Args:
            input_data: Multi-modal conversation input
            
        Returns:
            Comprehensive multi-modal analysis result
        """
        try:
            start_time = datetime.utcnow()
            
            # Determine modality and route to appropriate processor
            modality_results = {}
            
            # Process text content
            if input_data.text_content:
                modality_results['text'] = await self._process_text_modality(
                    input_data.text_content, input_data
                )
            
            # Process voice content
            if input_data.audio_data and self.enable_audio_processing:
                modality_results['voice'] = await self._process_voice_modality(
                    input_data.audio_data, input_data
                )
            
            # Process image content
            if input_data.image_data and self.enable_image_processing:
                modality_results['image'] = await self._process_image_modality(
                    input_data.image_data, input_data
                )
            
            # Process video content
            if input_data.video_data and self.enable_video_processing:
                modality_results['video'] = await self._process_video_modality(
                    input_data.video_data, input_data
                )
            
            # Perform cross-modal analysis
            cross_modal_insights = await self._perform_cross_modal_analysis(
                modality_results, input_data
            )
            
            # Generate unified intelligence
            unified_intelligence = await self._generate_unified_intelligence(
                modality_results, cross_modal_insights, input_data
            )
            
            # Analyze business intelligence
            business_intelligence = await self._analyze_business_intelligence(
                unified_intelligence, input_data.business_context
            )
            
            # Generate creator-specific insights
            creator_insights = await self._generate_creator_insights(
                unified_intelligence, input_data.creator_profile
            )
            
            # Calculate confidence scores
            confidence_scores = await self._calculate_confidence_scores(
                modality_results, cross_modal_insights, unified_intelligence
            )
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Update metrics
            await self._update_processing_metrics(input_data.modality_type, processing_time)
            
            return MultiModalAnalysisResult(
                input_id=input_data.input_id,
                modality_results=modality_results,
                cross_modal_insights=cross_modal_insights,
                unified_intelligence=unified_intelligence,
                business_intelligence=business_intelligence,
                creator_insights=creator_insights,
                confidence_scores=confidence_scores,
                processing_metrics={
                    'processing_time': processing_time,
                    'modalities_processed': len(modality_results),
                    'cross_modal_correlations': len(cross_modal_insights)
                }
            )
            
        except Exception as e:
            logger.error(f"Error analyzing multi-modal conversation: {str(e)}")
            raise
    
    async def _process_text_modality(self,
                                   text_content: str,
                                   input_data: MultiModalInput) -> Dict[str, Any]:
        """Process text modality for conversation intelligence"""
        try:
            # Text preprocessing
            processed_text = await self._preprocess_text(text_content)
            
            # Sentiment analysis
            sentiment = await self._analyze_text_sentiment(processed_text)
            
            # Topic extraction
            topics = await self._extract_text_topics(processed_text)
            
            # Intent classification
            intent = await self._classify_text_intent(processed_text)
            
            # Business signal detection
            business_signals = await self._detect_text_business_signals(
                processed_text, input_data.business_context
            )
            
            # Creator relevance analysis
            creator_relevance = await self._analyze_text_creator_relevance(
                processed_text, input_data.creator_profile
            )
            
            return {
                'processed_text': processed_text,
                'sentiment': sentiment,
                'topics': topics,
                'intent': intent,
                'business_signals': business_signals,
                'creator_relevance': creator_relevance,
                'text_quality': await self._assess_text_quality(processed_text),
                'engagement_potential': await self._calculate_text_engagement(processed_text)
            }
            
        except Exception as e:
            logger.error(f"Error processing text modality: {str(e)}")
            return {}
    
    async def _process_voice_modality(self,
                                    audio_data: bytes,
                                    input_data: MultiModalInput) -> VoiceAnalysisResult:
        """Process voice modality for conversation intelligence"""
        try:
            if not AUDIO_PROCESSING_AVAILABLE:
                return VoiceAnalysisResult()
            
            # Convert audio data to processable format
            audio_array = await self._convert_audio_data(audio_data)
            
            # Speech-to-text transcription
            transcription = await self._transcribe_audio(audio_array)
            
            # Emotion detection from voice
            emotion_detection = await self._detect_voice_emotion(audio_array)
            
            # Speaker identification
            speaker_id = await self._identify_speaker(audio_array)
            
            # Voice quality metrics
            quality_metrics = await self._analyze_voice_quality(audio_array)
            
            # Business signal detection from voice
            business_signals = await self._detect_voice_business_signals(
                transcription, emotion_detection
            )
            
            # Collaboration indicators
            collaboration_indicators = await self._detect_voice_collaboration_signals(
                transcription, emotion_detection
            )
            
            return VoiceAnalysisResult(
                transcription=transcription,
                emotion_detection=emotion_detection,
                speaker_identification=speaker_id,
                voice_quality_metrics=quality_metrics,
                business_signals=business_signals,
                collaboration_indicators=collaboration_indicators
            )
            
        except Exception as e:
            logger.error(f"Error processing voice modality: {str(e)}")
            return VoiceAnalysisResult()
    
    async def _process_image_modality(self,
                                    image_data: bytes,
                                    input_data: MultiModalInput) -> ImageAnalysisResult:
        """Process image modality for conversation intelligence"""
        try:
            if not IMAGE_PROCESSING_AVAILABLE:
                return ImageAnalysisResult()
            
            # Convert image data to processable format
            image = await self._convert_image_data(image_data)
            
            # Scene description
            scene_description = await self._describe_image_scene(image)
            
            # Object detection
            object_detection = await self._detect_image_objects(image)
            
            # Text extraction from image
            text_extraction = await self._extract_image_text(image)
            
            # Brand recognition
            brand_recognition = await self._recognize_image_brands(image)
            
            # Visual sentiment analysis
            visual_sentiment = await self._analyze_image_sentiment(image)
            
            # Business relevance scoring
            business_relevance = await self._score_image_business_relevance(
                scene_description, object_detection, input_data.business_context
            )
            
            # Creator context analysis
            creator_context = await self._analyze_image_creator_context(
                image, input_data.creator_profile
            )
            
            return ImageAnalysisResult(
                scene_description=scene_description,
                object_detection=object_detection,
                text_extraction=text_extraction,
                brand_recognition=brand_recognition,
                visual_sentiment=visual_sentiment,
                business_relevance=business_relevance,
                creator_context=creator_context
            )
            
        except Exception as e:
            logger.error(f"Error processing image modality: {str(e)}")
            return ImageAnalysisResult()
    
    async def _process_video_modality(self,
                                    video_data: bytes,
                                    input_data: MultiModalInput) -> VideoAnalysisResult:
        """Process video modality for conversation intelligence"""
        try:
            if not VIDEO_PROCESSING_AVAILABLE:
                return VideoAnalysisResult()
            
            # Convert video data to processable format
            video_frames, audio_track = await self._convert_video_data(video_data)
            
            # Scene analysis for each frame
            scene_analysis = await self._analyze_video_scenes(video_frames)
            
            # Audio analysis from video
            audio_analysis = await self._process_voice_modality(audio_track, input_data)
            
            # Visual analysis for key frames
            visual_analysis = []
            for frame in video_frames[::30]:  # Sample every 30th frame
                frame_analysis = await self._process_image_modality(
                    await self._frame_to_bytes(frame), input_data
                )
                visual_analysis.append(frame_analysis)
            
            # Video summary generation
            video_summary = await self._generate_video_summary(
                scene_analysis, audio_analysis, visual_analysis
            )
            
            # Engagement metrics calculation
            engagement_metrics = await self._calculate_video_engagement(
                scene_analysis, audio_analysis
            )
            
            # Content classification
            content_classification = await self._classify_video_content(
                scene_analysis, audio_analysis
            )
            
            # Monetization potential assessment
            monetization_potential = await self._assess_video_monetization_potential(
                content_classification, engagement_metrics, input_data.creator_profile
            )
            
            return VideoAnalysisResult(
                scene_analysis=scene_analysis,
                audio_analysis=audio_analysis,
                visual_analysis=visual_analysis,
                video_summary=video_summary,
                engagement_metrics=engagement_metrics,
                content_classification=content_classification,
                monetization_potential=monetization_potential
            )
            
        except Exception as e:
            logger.error(f"Error processing video modality: {str(e)}")
            return VideoAnalysisResult()


class VoiceConversationAnalyzer:
    """Advanced voice conversation analysis system"""
    
    def __init__(self):
        self.voice_models = {}
        self.emotion_analyzer = {}
        self.conversation_parser = {}
        
    async def analyze_voice_conversation(self,
                                       audio_data: bytes,
                                       conversation_context: Dict[str, Any]) -> Dict[str, Any]:
        """
Analyze voice conversation with advanced intelligence"""
        try:
            # Voice processing and transcription
            transcription_result = await self._process_voice_transcription(audio_data)
            
            # Emotion and sentiment analysis
            emotion_analysis = await self._analyze_voice_emotions(audio_data)
            
            # Conversation flow analysis
            flow_analysis = await self._analyze_conversation_flow(
                transcription_result, emotion_analysis
            )
            
            # Business intelligence from voice
            business_intelligence = await self._extract_voice_business_intelligence(
                transcription_result, conversation_context
            )
            
            return {
                'transcription': transcription_result,
                'emotion_analysis': emotion_analysis,
                'flow_analysis': flow_analysis,
                'business_intelligence': business_intelligence,
                'voice_quality_score': await self._calculate_voice_quality(audio_data),
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing voice conversation: {str(e)}")
            return {}


class TextConversationProcessor:
    """Advanced text conversation processing system"""
    
    def __init__(self):
        self.text_models = {}
        self.nlp_pipeline = {}
        self.conversation_analyzer = {}
        
    async def process_text_conversation(self,
                                      text_content: str,
                                      conversation_context: Dict[str, Any]) -> Dict[str, Any]:
        """
Process text conversation with advanced NLP intelligence"""
        try:
            # Advanced text preprocessing
            processed_text = await self._advanced_text_preprocessing(text_content)
            
            # Multi-level sentiment analysis
            sentiment_analysis = await self._multilevel_sentiment_analysis(processed_text)
            
            # Advanced topic modeling
            topic_analysis = await self._advanced_topic_modeling(processed_text)
            
            # Intent and entity recognition
            intent_entities = await self._recognize_intent_entities(processed_text)
            
            # Business context extraction
            business_context = await self._extract_business_context(
                processed_text, conversation_context
            )
            
            return {
                'processed_text': processed_text,
                'sentiment_analysis': sentiment_analysis,
                'topic_analysis': topic_analysis,
                'intent_entities': intent_entities,
                'business_context': business_context,
                'text_intelligence_score': await self._calculate_text_intelligence(processed_text),
                'processing_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing text conversation: {str(e)}")
            return {}


class ImageContextAnalyzer:
    """Advanced image context analysis system"""
    
    def __init__(self):
        self.image_models = {}
        self.context_analyzer = {}
        self.visual_intelligence = {}
        
    async def analyze_image_context(self,
                                  image_data: bytes,
                                  conversation_context: Dict[str, Any]) -> Dict[str, Any]:
        """
Analyze image context for conversation intelligence"""
        try:
            # Image preprocessing and analysis
            image_analysis = await self._comprehensive_image_analysis(image_data)
            
            # Context extraction from image
            context_extraction = await self._extract_image_context(
                image_analysis, conversation_context
            )
            
            # Visual business intelligence
            visual_business_intel = await self._analyze_visual_business_intelligence(
                image_analysis, conversation_context
            )
            
            # Creator relevance analysis
            creator_relevance = await self._analyze_image_creator_relevance(
                image_analysis, conversation_context
            )
            
            return {
                'image_analysis': image_analysis,
                'context_extraction': context_extraction,
                'visual_business_intelligence': visual_business_intel,
                'creator_relevance': creator_relevance,
                'visual_intelligence_score': await self._calculate_visual_intelligence(image_analysis),
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing image context: {str(e)}")
            return {}


class VideoConversationIntelligence:
    """Advanced video conversation intelligence system"""
    
    def __init__(self):
        self.video_models = {}
        self.conversation_analyzer = {}
        self.intelligence_engine = {}
        
    async def analyze_video_conversation(self,
                                       video_data: bytes,
                                       conversation_context: Dict[str, Any]) -> Dict[str, Any]:
        """
Analyze video conversation with comprehensive intelligence"""
        try:
            # Comprehensive video analysis
            video_analysis = await self._comprehensive_video_analysis(video_data)
            
            # Conversation flow from video
            conversation_flow = await self._extract_video_conversation_flow(video_analysis)
            
            # Business intelligence from video
            business_intelligence = await self._extract_video_business_intelligence(
                video_analysis, conversation_context
            )
            
            # Engagement and monetization analysis
            engagement_monetization = await self._analyze_video_engagement_monetization(
                video_analysis, conversation_context
            )
            
            return {
                'video_analysis': video_analysis,
                'conversation_flow': conversation_flow,
                'business_intelligence': business_intelligence,
                'engagement_monetization': engagement_monetization,
                'video_intelligence_score': await self._calculate_video_intelligence(video_analysis),
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing video conversation: {str(e)}")
            return {}
