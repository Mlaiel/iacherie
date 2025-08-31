"""Multi-Format Content Processing Module for IA Influencer Agent Platform

Advanced processing capabilities for multiple content formats including audio,
video, images, and text content for creators, influencers, and multimedia platforms.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - Unauthorized use prohibited ⚠️
This software is proprietary and confidential. Contact: mlaiel@live.de
"""
import asyncio
import logging
import io
import base64
from typing import Dict, List, Optional, Any, Union, Tuple, BinaryIO
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod
from enum import Enum
import numpy as np
from PIL import Image
import cv2
import librosa
import soundfile as sf
import speech_recognition as sr
from moviepy import VideoFileClip
import pytesseract
from transformers import pipeline, BlipProcessor, BlipForConditionalGeneration
import torch
import whisper
import json

logger = logging.getLogger(__name__)

class ContentFormat(Enum):
    """Supported content formats"""    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    MIXED_MEDIA = "mixed_media"

class ProcessingPipeline(Enum):
    """Processing pipeline types"""    TRANSCRIPTION = "transcription"
    DESCRIPTION = "description"
    EXTRACTION = "extraction"
    CLASSIFICATION = "classification"
    ENHANCEMENT = "enhancement"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"

@dataclass
class MediaMetadata:
    """Media file metadata"""    format: ContentFormat
    file_size: int
    duration: Optional[float] = None  # for audio/video
    dimensions: Optional[Tuple[int, int]] = None  # for images/video
    sample_rate: Optional[int] = None  # for audio
    fps: Optional[float] = None  # for video
    encoding: Optional[str] = None
    quality_score: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ProcessingResult:
    """Multi-format content processing result"""    content_id: str
    original_format: ContentFormat
    processed_content: Dict[str, Any] = field(default_factory=dict)
    extracted_text: Optional[str] = None
    transcription: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    entities: List[Dict[str, Any]] = field(default_factory=list)
    sentiment: Dict[str, float] = field(default_factory=dict)
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    metadata: MediaMetadata = None
    processing_time: float = 0.0
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    platform_optimized: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

class ContentProcessor(ABC):
    """Abstract base class for content processors"""    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.name = self.__class__.__name__
        
    @abstractmethod
    async def process(self, content: Any, metadata: Dict[str, Any] = None) -> ProcessingResult:
        """Process content and return result"""        pass
    
    @abstractmethod
    def supports_format(self, format: ContentFormat) -> bool:
        """Check if processor supports the given format"""        pass

class MultiFormatProcessor:
    """    Advanced multi-format content processor
    
    Capabilities:
    - Audio transcription and analysis
    - Video content extraction and description
    - Image description and OCR
    - Document text extraction
    - Cross-format content linking
    - Platform-specific optimization
    - Real-time processing pipeline
    """    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._get_default_config()
        self.processors: Dict[ContentFormat, ContentProcessor] = {}
        self.models = {}
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize all processors and models"""        try:
            logger.info("Initializing multi-format processor...")
            
            # Initialize text processor
            self.processors[ContentFormat.TEXT] = TextProcessor(self.config)
            
            # Initialize image processor
            self.processors[ContentFormat.IMAGE] = ImageProcessor(self.config)
            await self.processors[ContentFormat.IMAGE].initialize()
            
            # Initialize audio processor
            self.processors[ContentFormat.AUDIO] = AudioProcessor(self.config)
            await self.processors[ContentFormat.AUDIO].initialize()
            
            # Initialize video processor
            self.processors[ContentFormat.VIDEO] = VideoProcessor(self.config)
            await self.processors[ContentFormat.VIDEO].initialize()
            
            # Initialize document processor
            self.processors[ContentFormat.DOCUMENT] = DocumentProcessor(self.config)
            
            self.is_initialized = True
            logger.info("Multi-format processor initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing multi-format processor: {e}")
            raise
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""        return {
            'max_file_size': 100 * 1024 * 1024,  # 100MB
            'supported_image_formats': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'],
            'supported_audio_formats': ['.mp3', '.wav', '.ogg', '.m4a', '.flac'],
            'supported_video_formats': ['.mp4', '.avi', '.mov', '.mkv', '.webm'],
            'supported_document_formats': ['.pdf', '.docx', '.txt', '.rtf'],
            'enable_gpu': torch.cuda.is_available(),
            'whisper_model': 'base',
            'image_description_model': 'Salesforce/blip-image-captioning-base',
            'enable_ocr': True,
            'enable_face_detection': True,
            'enable_object_detection': True,
            'platform_optimization': True,
            'quality_threshold': 0.7
        }
    
    async def process_content(
        self,
        content: Any,
        format: ContentFormat,
        metadata: Dict[str, Any] = None,
        pipeline: List[ProcessingPipeline] = None
    ) -> ProcessingResult:
        """Process content based on format and pipeline"""        try:
            if not self.is_initialized:
                await self.initialize()
            
            if format not in self.processors:
                raise ValueError(f"Unsupported content format: {format}")
            
            # Generate content ID
            content_id = f"content_{format.value}_{int(datetime.utcnow().timestamp())}"
            
            # Process with appropriate processor
            processor = self.processors[format]
            result = await processor.process(content, metadata)
            result.content_id = content_id
            
            # Apply additional processing pipelines
            if pipeline:
                result = await self._apply_processing_pipelines(result, pipeline)
            
            # Platform-specific optimization
            if self.config.get('platform_optimization', False):
                result.platform_optimized = await self._optimize_for_platforms(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing content: {e}")
            return ProcessingResult(
                content_id=f"error_{int(datetime.utcnow().timestamp())}",
                original_format=format
            )
    
    async def process_mixed_media(
        self,
        content_items: List[Tuple[Any, ContentFormat]],
        metadata: Dict[str, Any] = None
    ) -> ProcessingResult:
        """Process multiple content items as mixed media"""        try:
            mixed_result = ProcessingResult(
                content_id=f"mixed_{int(datetime.utcnow().timestamp())}",
                original_format=ContentFormat.MIXED_MEDIA
            )
            
            individual_results = []
            for content, format in content_items:
                result = await self.process_content(content, format, metadata)
                individual_results.append(result)
            
            # Combine results
            mixed_result = await self._combine_processing_results(individual_results, mixed_result)
            
            return mixed_result
            
        except Exception as e:
            logger.error(f"Error processing mixed media: {e}")
            return ProcessingResult(
                content_id=f"mixed_error_{int(datetime.utcnow().timestamp())}",
                original_format=ContentFormat.MIXED_MEDIA
            )

class TextProcessor(ContentProcessor):
    """Advanced text content processor"""    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.nlp_pipeline = None
        
    async def initialize(self):
        """Initialize NLP pipeline"""        try:
            from ..core import AdvancedNLPEngine
            self.nlp_engine = AdvancedNLPEngine(self.config)
            await self.nlp_engine.initialize()
        except Exception as e:
            logger.error(f"Error initializing text processor: {e}")
    
    def supports_format(self, format: ContentFormat) -> bool:
        return format == ContentFormat.TEXT
    
    async def process(self, content: str, metadata: Dict[str, Any] = None) -> ProcessingResult:
        """Process text content"""        try:
            start_time = datetime.utcnow()
            
            result = ProcessingResult(
                content_id="",
                original_format=ContentFormat.TEXT,
                processed_content={'text': content},
                extracted_text=content
            )
            
            # Basic text analysis
            if self.nlp_engine:
                # Sentiment analysis
                sentiment_result = await self.nlp_engine.analyze_sentiment(content)
                result.sentiment = sentiment_result.get('scores', {})
                
                # Entity extraction
                entities_result = await self.nlp_engine.extract_entities(content)
                result.entities = entities_result.get('entities', [])
                
                # Tag generation
                tags_result = await self.nlp_engine.generate_tags(content)
                result.tags = tags_result.get('tags', [])
            
            # Calculate quality metrics
            result.quality_metrics = self._calculate_text_quality(content)
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            result.processing_time = processing_time
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing text: {e}")
            return ProcessingResult(content_id="", original_format=ContentFormat.TEXT)
    
    def _calculate_text_quality(self, text: str) -> Dict[str, float]:
        """Calculate text quality metrics"""        try:
            import textstat
            
            metrics = {
                'readability_score': textstat.flesch_reading_ease(text) / 100.0,
                'complexity_score': 1.0 - (textstat.flesch_kincaid_grade(text) / 20.0),
                'length_score': min(len(text.split()) / 300.0, 1.0),
                'coherence_score': self._calculate_coherence(text)
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating text quality: {e}")
            return {'overall_quality': 0.5}
    
    def _calculate_coherence(self, text: str) -> float:
        """Calculate text coherence score"""        sentences = text.split('.')
        if len(sentences) < 2:
            return 1.0
        
        # Simple coherence based on sentence length variation
        lengths = [len(sentence.split()) for sentence in sentences if sentence.strip()]
        if not lengths:
            return 0.5
        
        avg_length = sum(lengths) / len(lengths)
        variance = sum((length - avg_length) ** 2 for length in lengths) / len(lengths)
        coherence = 1.0 / (1.0 + variance / 100.0)
        
        return min(coherence, 1.0)

class ImageProcessor(ContentProcessor):
    """Advanced image content processor"""    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.image_captioning_model = None
        self.image_captioning_processor = None
        
    async def initialize(self):
        """Initialize image processing models"""        try:
            # Initialize image captioning model
            model_name = self.config.get('image_description_model', 'Salesforce/blip-image-captioning-base')
            self.image_captioning_processor = BlipProcessor.from_pretrained(model_name)
            self.image_captioning_model = BlipForConditionalGeneration.from_pretrained(model_name)
            
            logger.info("Image processor initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing image processor: {e}")
    
    def supports_format(self, format: ContentFormat) -> bool:
        return format == ContentFormat.IMAGE
    
    async def process(self, content: Union[str, bytes, Image.Image], metadata: Dict[str, Any] = None) -> ProcessingResult:
        """Process image content"""        try:
            start_time = datetime.utcnow()
            
            # Convert content to PIL Image
            if isinstance(content, str):
                # Base64 encoded image
                image_data = base64.b64decode(content)
                image = Image.open(io.BytesIO(image_data))
            elif isinstance(content, bytes):
                image = Image.open(io.BytesIO(content))
            elif isinstance(content, Image.Image):
                image = content
            else:
                raise ValueError("Unsupported image format")
            
            result = ProcessingResult(
                content_id="",
                original_format=ContentFormat.IMAGE
            )
            
            # Extract image metadata
            result.metadata = self._extract_image_metadata(image)
            
            # Generate image description
            if self.image_captioning_model:
                description = await self._generate_image_description(image)
                result.description = description
                result.processed_content['description'] = description
            
            # OCR text extraction
            if self.config.get('enable_ocr', True):
                extracted_text = await self._extract_text_from_image(image)
                if extracted_text:
                    result.extracted_text = extracted_text
                    result.processed_content['ocr_text'] = extracted_text
            
            # Object detection
            if self.config.get('enable_object_detection', True):
                objects = await self._detect_objects(image)
                result.processed_content['objects'] = objects
                result.tags.extend([obj['label'] for obj in objects])
            
            # Face detection
            if self.config.get('enable_face_detection', True):
                faces = await self._detect_faces(image)
                result.processed_content['faces'] = faces
                if faces:
                    result.tags.append('faces')
            
            # Calculate image quality metrics
            result.quality_metrics = self._calculate_image_quality(image)
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            result.processing_time = processing_time
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return ProcessingResult(content_id="", original_format=ContentFormat.IMAGE)
    
    def _extract_image_metadata(self, image: Image.Image) -> MediaMetadata:
        """Extract image metadata"""        try:
            return MediaMetadata(
                format=ContentFormat.IMAGE,
                file_size=len(image.tobytes()),
                dimensions=image.size,
                encoding=image.format or 'Unknown',
                quality_score=self._calculate_image_quality_score(image)
            )
        except Exception as e:
            logger.error(f"Error extracting image metadata: {e}")
            return MediaMetadata(format=ContentFormat.IMAGE, file_size=0)
    
    async def _generate_image_description(self, image: Image.Image) -> str:
        """Generate image description using AI model"""        try:
            inputs = self.image_captioning_processor(image, return_tensors="pt")
            out = self.image_captioning_model.generate(**inputs, max_length=50)
            description = self.image_captioning_processor.decode(out[0], skip_special_tokens=True)
            return description
        except Exception as e:
            logger.error(f"Error generating image description: {e}")
            return "Unable to generate description"
    
    async def _extract_text_from_image(self, image: Image.Image) -> str:
        """Extract text from image using OCR"""        try:
            # Convert PIL image to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Use Tesseract OCR
            text = pytesseract.image_to_string(cv_image)
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            return ""
    
    async def _detect_objects(self, image: Image.Image) -> List[Dict[str, Any]]:
        """Detect objects in image"""        try:
            # Simple object detection using OpenCV (placeholder)
            # In production, use more advanced models like YOLO or COCO
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Placeholder implementation
            objects = []
            
            # Detect edges as a simple object indicator
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for i, contour in enumerate(contours[:10]):  # Limit to 10 objects
                area = cv2.contourArea(contour)
                if area > 1000:  # Filter small objects
                    x, y, w, h = cv2.boundingRect(contour)
                    objects.append({
                        'label': f'object_{i}',
                        'confidence': 0.5,
                        'bbox': [x, y, w, h],
                        'area': area
                    })
            
            return objects
        except Exception as e:
            logger.error(f"Error detecting objects: {e}")
            return []
    
    async def _detect_faces(self, image: Image.Image) -> List[Dict[str, Any]]:
        """Detect faces in image"""        try:
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Load face cascade classifier
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            face_data = []
            for (x, y, w, h) in faces:
                face_data.append({
                    'bbox': [int(x), int(y), int(w), int(h)],
                    'confidence': 0.8  # Placeholder confidence
                })
            
            return face_data
        except Exception as e:
            logger.error(f"Error detecting faces: {e}")
            return []
    
    def _calculate_image_quality(self, image: Image.Image) -> Dict[str, float]:
        """Calculate image quality metrics"""        try:
            # Convert to grayscale for analysis
            gray = image.convert('L')
            img_array = np.array(gray)
            
            # Calculate sharpness (Laplacian variance)
            laplacian = cv2.Laplacian(img_array, cv2.CV_64F)
            sharpness = laplacian.var() / 1000.0  # Normalize
            
            # Calculate brightness
            brightness = np.mean(img_array) / 255.0
            
            # Calculate contrast
            contrast = np.std(img_array) / 255.0
            
            # Resolution score
            total_pixels = image.size[0] * image.size[1]
            resolution_score = min(total_pixels / (1920 * 1080), 1.0)  # Normalize to 1080p
            
            return {
                'sharpness': min(sharpness, 1.0),
                'brightness': brightness,
                'contrast': contrast,
                'resolution': resolution_score,
                'overall_quality': (sharpness + contrast + resolution_score) / 3.0
            }
        except Exception as e:
            logger.error(f"Error calculating image quality: {e}")
            return {'overall_quality': 0.5}
    
    def _calculate_image_quality_score(self, image: Image.Image) -> float:
        """Calculate overall image quality score"""        quality_metrics = self._calculate_image_quality(image)
        return quality_metrics.get('overall_quality', 0.5)

class AudioProcessor(ContentProcessor):
    """Advanced audio content processor"""    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.whisper_model = None
        self.speech_recognizer = None
        
    async def initialize(self):
        """Initialize audio processing models"""        try:
            # Initialize Whisper model for transcription
            model_name = self.config.get('whisper_model', 'base')
            self.whisper_model = whisper.load_model(model_name)
            
            # Initialize speech recognizer
            self.speech_recognizer = sr.Recognizer()
            
            logger.info("Audio processor initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing audio processor: {e}")
    
    def supports_format(self, format: ContentFormat) -> bool:
        return format == ContentFormat.AUDIO
    
    async def process(self, content: Union[str, bytes], metadata: Dict[str, Any] = None) -> ProcessingResult:
        """Process audio content"""        try:
            start_time = datetime.utcnow()
            
            # Load audio data
            if isinstance(content, str):
                # File path
                audio_data, sample_rate = librosa.load(content, sr=None)
            elif isinstance(content, bytes):
                # Raw audio bytes
                audio_data, sample_rate = sf.read(io.BytesIO(content))
            else:
                raise ValueError("Unsupported audio format")
            
            result = ProcessingResult(
                content_id="",
                original_format=ContentFormat.AUDIO
            )
            
            # Extract audio metadata
            result.metadata = self._extract_audio_metadata(audio_data, sample_rate)
            
            # Transcribe audio
            if self.whisper_model:
                transcription = await self._transcribe_audio(content)
                result.transcription = transcription
                result.extracted_text = transcription
                result.processed_content['transcription'] = transcription
            
            # Audio analysis
            audio_features = await self._analyze_audio_features(audio_data, sample_rate)
            result.processed_content['audio_features'] = audio_features
            
            # Generate audio description
            description = await self._generate_audio_description(audio_features)
            result.description = description
            
            # Extract tags based on audio content
            if transcription:
                # Use NLP to extract tags from transcription
                from ..core import AdvancedNLPEngine
                nlp_engine = AdvancedNLPEngine()
                await nlp_engine.initialize()
                tags_result = await nlp_engine.generate_tags(transcription)
                result.tags = tags_result.get('tags', [])
            
            # Calculate audio quality metrics
            result.quality_metrics = self._calculate_audio_quality(audio_data, sample_rate)
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            result.processing_time = processing_time
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            return ProcessingResult(content_id="", original_format=ContentFormat.AUDIO)
    
    def _extract_audio_metadata(self, audio_data: np.ndarray, sample_rate: int) -> MediaMetadata:
        """Extract audio metadata"""        try:
            duration = len(audio_data) / sample_rate
            file_size = audio_data.nbytes
            
            return MediaMetadata(
                format=ContentFormat.AUDIO,
                file_size=file_size,
                duration=duration,
                sample_rate=sample_rate,
                quality_score=self._calculate_audio_quality_score(audio_data, sample_rate)
            )
        except Exception as e:
            logger.error(f"Error extracting audio metadata: {e}")
            return MediaMetadata(format=ContentFormat.AUDIO, file_size=0)
    
    async def _transcribe_audio(self, content: Union[str, bytes]) -> str:
        """Transcribe audio using Whisper"""        try:
            if isinstance(content, str):
                # File path
                result = self.whisper_model.transcribe(content)
                return result['text']
            else:
                # For bytes, save temporarily and transcribe
                with open('/tmp/temp_audio.wav', 'wb') as f:
                    f.write(content)
                result = self.whisper_model.transcribe('/tmp/temp_audio.wav')
                return result['text']
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return "Transcription failed"
    
    async def _analyze_audio_features(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """Analyze audio features"""        try:
            features = {}
            
            # Tempo
            tempo, _ = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
            features['tempo'] = float(tempo)
            
            # Spectral centroid (brightness)
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)[0]
            features['brightness'] = float(np.mean(spectral_centroids))
            
            # RMS energy (loudness)
            rms = librosa.feature.rms(y=audio_data)[0]
            features['loudness'] = float(np.mean(rms))
            
            # Zero crossing rate (roughness)
            zcr = librosa.feature.zero_crossing_rate(audio_data)[0]
            features['roughness'] = float(np.mean(zcr))
            
            # MFCC features
            mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
            features['mfcc_mean'] = [float(x) for x in np.mean(mfccs, axis=1)]
            
            # Duration
            features['duration'] = len(audio_data) / sample_rate
            
            return features
        except Exception as e:
            logger.error(f"Error analyzing audio features: {e}")
            return {}
    
    async def _generate_audio_description(self, audio_features: Dict[str, Any]) -> str:
        """Generate audio description based on features"""        try:
            tempo = audio_features.get('tempo', 0)
            brightness = audio_features.get('brightness', 0)
            loudness = audio_features.get('loudness', 0)
            
            description_parts = []
            
            # Tempo description
            if tempo < 90:
                description_parts.append("slow-paced")
            elif tempo < 120:
                description_parts.append("moderate-paced")
            elif tempo < 140:
                description_parts.append("upbeat")
            else:
                description_parts.append("fast-paced")
            
            # Brightness description
            if brightness > 2000:
                description_parts.append("bright")
            else:
                description_parts.append("warm")
            
            # Loudness description
            if loudness > 0.1:
                description_parts.append("energetic")
            else:
                description_parts.append("gentle")
            
            description = f"This audio content is {', '.join(description_parts)}."
            return description
            
        except Exception as e:
            logger.error(f"Error generating audio description: {e}")
            return "Audio content"
    
    def _calculate_audio_quality(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """Calculate audio quality metrics"""        try:
            # Signal-to-noise ratio estimation
            signal_power = np.mean(audio_data ** 2)
            noise_power = np.var(audio_data - np.mean(audio_data))
            snr = 10 * np.log10(signal_power / max(noise_power, 1e-10))
            snr_normalized = min(max(snr / 40.0, 0), 1)  # Normalize to 0-1
            
            # Dynamic range
            dynamic_range = np.max(np.abs(audio_data)) - np.min(np.abs(audio_data[audio_data != 0]))
            dynamic_range_normalized = min(dynamic_range, 1.0)
            
            # Frequency response (simplified)
            fft = np.fft.fft(audio_data)
            freq_response = np.abs(fft[:len(fft)//2])
            freq_balance = 1.0 - np.std(freq_response) / np.mean(freq_response)
            freq_balance = max(0, min(freq_balance, 1))
            
            return {
                'signal_to_noise_ratio': snr_normalized,
                'dynamic_range': dynamic_range_normalized,
                'frequency_balance': freq_balance,
                'overall_quality': (snr_normalized + dynamic_range_normalized + freq_balance) / 3.0
            }
        except Exception as e:
            logger.error(f"Error calculating audio quality: {e}")
            return {'overall_quality': 0.5}
    
    def _calculate_audio_quality_score(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """Calculate overall audio quality score"""        quality_metrics = self._calculate_audio_quality(audio_data, sample_rate)
        return quality_metrics.get('overall_quality', 0.5)

class VideoProcessor(ContentProcessor):
    """Advanced video content processor"""    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        
    async def initialize(self):
        """Initialize video processing capabilities"""        try:
            logger.info("Video processor initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing video processor: {e}")
    
    def supports_format(self, format: ContentFormat) -> bool:
        return format == ContentFormat.VIDEO
    
    async def process(self, content: str, metadata: Dict[str, Any] = None) -> ProcessingResult:
        """Process video content"""        try:
            start_time = datetime.utcnow()
            
            # Load video
            video = VideoFileClip(content)
            
            result = ProcessingResult(
                content_id="",
                original_format=ContentFormat.VIDEO
            )
            
            # Extract video metadata
            result.metadata = self._extract_video_metadata(video)
            
            # Extract audio for transcription
            if video.audio:
                audio_path = "/tmp/temp_video_audio.wav"
                video.audio.write_audiofile(audio_path, verbose=False, logger=None)
                
                # Process audio component
                audio_processor = AudioProcessor(self.config)
                await audio_processor.initialize()
                audio_result = await audio_processor.process(audio_path)
                
                result.transcription = audio_result.transcription
                result.extracted_text = audio_result.extracted_text
                result.processed_content['audio_analysis'] = audio_result.processed_content
            
            # Extract key frames for image analysis
            key_frames = await self._extract_key_frames(video)
            if key_frames:
                # Process first key frame as representative image
                image_processor = ImageProcessor(self.config)
                await image_processor.initialize()
                image_result = await image_processor.process(key_frames[0])
                
                result.description = image_result.description
                result.processed_content['visual_analysis'] = image_result.processed_content
                result.tags.extend(image_result.tags)
            
            # Video-specific analysis
            video_features = await self._analyze_video_features(video)
            result.processed_content['video_features'] = video_features
            
            # Calculate video quality metrics
            result.quality_metrics = self._calculate_video_quality(video)
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            result.processing_time = processing_time
            
            # Close video file
            video.close()
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing video: {e}")
            return ProcessingResult(content_id="", original_format=ContentFormat.VIDEO)
    
    def _extract_video_metadata(self, video: VideoFileClip) -> MediaMetadata:
        """Extract video metadata"""        try:
            return MediaMetadata(
                format=ContentFormat.VIDEO,
                file_size=0,  # Would need to calculate from file
                duration=video.duration,
                dimensions=(int(video.w), int(video.h)),
                fps=video.fps,
                quality_score=self._calculate_video_quality_score(video)
            )
        except Exception as e:
            logger.error(f"Error extracting video metadata: {e}")
            return MediaMetadata(format=ContentFormat.VIDEO, file_size=0)
    
    async def _extract_key_frames(self, video: VideoFileClip, num_frames: int = 5) -> List[Image.Image]:
        """Extract key frames from video"""        try:
            key_frames = []
            duration = video.duration
            
            for i in range(num_frames):
                timestamp = (duration / num_frames) * i
                frame = video.get_frame(timestamp)
                pil_image = Image.fromarray(frame.astype('uint8'), 'RGB')
                key_frames.append(pil_image)
            
            return key_frames
        except Exception as e:
            logger.error(f"Error extracting key frames: {e}")
            return []
    
    async def _analyze_video_features(self, video: VideoFileClip) -> Dict[str, Any]:
        """Analyze video features"""        try:
            features = {
                'duration': video.duration,
                'fps': video.fps,
                'resolution': (video.w, video.h),
                'aspect_ratio': video.w / video.h if video.h > 0 else 1.0,
                'has_audio': video.audio is not None
            }
            
            # Calculate average brightness across frames
            try:
                # Sample a few frames for analysis
                sample_times = [video.duration * i / 10 for i in range(0, 10)]
                brightness_values = []
                
                for time in sample_times:
                    if time < video.duration:
                        frame = video.get_frame(time)
                        brightness = np.mean(frame)
                        brightness_values.append(brightness)
                
                if brightness_values:
                    features['average_brightness'] = np.mean(brightness_values)
                    features['brightness_variance'] = np.var(brightness_values)
            except:
                features['average_brightness'] = 128  # Default middle brightness
                features['brightness_variance'] = 0
            
            return features
        except Exception as e:
            logger.error(f"Error analyzing video features: {e}")
            return {}
    
    def _calculate_video_quality(self, video: VideoFileClip) -> Dict[str, float]:
        """Calculate video quality metrics"""        try:
            # Resolution score
            total_pixels = video.w * video.h
            resolution_score = min(total_pixels / (1920 * 1080), 1.0)  # Normalize to 1080p
            
            # Frame rate score
            fps_score = min(video.fps / 30.0, 1.0)  # Normalize to 30 fps
            
            # Duration score (longer videos might be better content)
            duration_score = min(video.duration / 300.0, 1.0)  # Normalize to 5 minutes
            
            # Audio presence bonus
            audio_bonus = 0.1 if video.audio else 0.0
            
            overall_quality = (resolution_score + fps_score + duration_score) / 3.0 + audio_bonus
            
            return {
                'resolution': resolution_score,
                'frame_rate': fps_score,
                'duration': duration_score,
                'has_audio': 1.0 if video.audio else 0.0,
                'overall_quality': min(overall_quality, 1.0)
            }
        except Exception as e:
            logger.error(f"Error calculating video quality: {e}")
            return {'overall_quality': 0.5}
    
    def _calculate_video_quality_score(self, video: VideoFileClip) -> float:
        """Calculate overall video quality score"""        quality_metrics = self._calculate_video_quality(video)
        return quality_metrics.get('overall_quality', 0.5)

class DocumentProcessor(ContentProcessor):
    """Advanced document content processor"""    
    def supports_format(self, format: ContentFormat) -> bool:
        return format == ContentFormat.DOCUMENT
    
    async def process(self, content: str, metadata: Dict[str, Any] = None) -> ProcessingResult:
        """Process document content"""        try:
            start_time = datetime.utcnow()
            
            result = ProcessingResult(
                content_id="",
                original_format=ContentFormat.DOCUMENT
            )
            
            # Extract text based on document type
            extracted_text = await self._extract_document_text(content, metadata)
            result.extracted_text = extracted_text
            result.processed_content['extracted_text'] = extracted_text
            
            # Process extracted text using text processor
            if extracted_text:
                text_processor = TextProcessor(self.config)
                await text_processor.initialize()
                text_result = await text_processor.process(extracted_text)
                
                result.sentiment = text_result.sentiment
                result.entities = text_result.entities
                result.tags = text_result.tags
                result.quality_metrics = text_result.quality_metrics
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            result.processing_time = processing_time
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            return ProcessingResult(content_id="", original_format=ContentFormat.DOCUMENT)
    
    async def _extract_document_text(self, file_path: str, metadata: Dict[str, Any] = None) -> str:
        """Extract text from document based on file type"""        try:
            file_extension = file_path.lower().split('.')[-1]
            
            if file_extension == 'pdf':
                return await self._extract_pdf_text(file_path)
            elif file_extension == 'docx':
                return await self._extract_docx_text(file_path)
            elif file_extension == 'txt':
                return await self._extract_txt_text(file_path)
            else:
                raise ValueError(f"Unsupported document format: {file_extension}")
                
        except Exception as e:
            logger.error(f"Error extracting document text: {e}")
            return ""
    
    async def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF"""        try:
            import PyPDF2
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            return ""
    
    async def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from DOCX"""        try:
            import docx
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting DOCX text: {e}")
            return ""
    
    async def _extract_txt_text(self, file_path: str) -> str:
        """Extract text from TXT"""        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error extracting TXT text: {e}")
            return ""
