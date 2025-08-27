"""
AI Processing Pipeline
=====================

Enterprise-grade processing pipeline for multi-format content analysis
with advanced AI fingerprinting and protection capabilities.

Features:
- Multi-stage content processing
- Parallel execution and optimization
- Quality assurance and validation
- Enterprise monitoring and logging

Author: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Callable
import json

import numpy as np
import librosa
import cv2
from PIL import Image
import torch
import tensorflow as tf
from transformers import pipeline as hf_pipeline
from sentence_transformers import SentenceTransformer
import imagehash
import essentia.standard as es
from prometheus_client import Counter, Histogram, Gauge

from .core import ProcessingTask, ProcessingStatus, AIModelType

# Metrics
pipeline_executions_total = Counter('pipeline_executions_total', 'Total pipeline executions')
pipeline_execution_time = Histogram('pipeline_execution_time_seconds', 'Pipeline execution time')
pipeline_stage_time = Histogram('pipeline_stage_time_seconds', 'Pipeline stage execution time', ['stage'])
pipeline_active_executions = Gauge('pipeline_active_executions', 'Active pipeline executions')

logger = logging.getLogger(__name__)


class PipelineStage(Enum):
    """Pipeline processing stages."""
    PREPROCESSING = "preprocessing"
    FEATURE_EXTRACTION = "feature_extraction"
    FINGERPRINT_GENERATION = "fingerprint_generation"
    VECTOR_EMBEDDING = "vector_embedding"
    SIMILARITY_ANALYSIS = "similarity_analysis"
    POSTPROCESSING = "postprocessing"
    VALIDATION = "validation"


class ContentFormat(Enum):
    """Supported content formats."""
    AUDIO_MP3 = "audio/mp3"
    AUDIO_WAV = "audio/wav"
    AUDIO_FLAC = "audio/flac"
    VIDEO_MP4 = "video/mp4"
    VIDEO_AVI = "video/avi"
    VIDEO_MOV = "video/mov"
    IMAGE_JPEG = "image/jpeg"
    IMAGE_PNG = "image/png"
    IMAGE_WEBP = "image/webp"
    TEXT_PLAIN = "text/plain"
    TEXT_MARKDOWN = "text/markdown"
    TEXT_HTML = "text/html"


@dataclass
class PipelineConfig:
    """Pipeline configuration parameters."""
    enable_parallel_processing: bool = True
    max_parallel_stages: int = 4
    enable_gpu_acceleration: bool = True
    quality_threshold: float = 0.85
    similarity_threshold: float = 0.9
    timeout_seconds: int = 300
    enable_caching: bool = True
    enable_validation: bool = True


@dataclass
class StageResult:
    """Result from a pipeline stage."""
    stage: PipelineStage
    success: bool
    data: Any
    metadata: Dict[str, Any]
    execution_time: float
    error: Optional[str] = None


@dataclass
class PipelineResult:
    """Complete pipeline execution result."""
    task_id: str
    success: bool
    fingerprint: Optional[str]
    vector_embedding: Optional[np.ndarray]
    similarity_scores: Optional[Dict[str, float]]
    metadata: Dict[str, Any]
    stage_results: List[StageResult]
    total_execution_time: float
    error: Optional[str] = None


class ProcessingPipeline:
    """
    Enterprise AI Processing Pipeline
    
    Orchestrates multi-stage content processing with AI fingerprinting,
    vector embeddings, and similarity analysis for content protection.
    """
    
    def __init__(self, config: PipelineConfig):
        """Initialize processing pipeline."""
        self.config = config
        self.stage_processors = {}
        self.active_executions: Dict[str, asyncio.Task] = {}
        
        # Initialize AI models
        self._initialize_models()
        
        # Initialize stage processors
        self._initialize_stage_processors()
    
    def _initialize_models(self):
        """Initialize AI models for different content types."""
        try:
            # Text embedding model
            self.text_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Audio processing components
            self.audio_components = {
                'windowing': es.Windowing(type='hann'),
                'spectrum': es.Spectrum(),
                'mfcc': es.MFCC(),
                'spectral_centroid': es.SpectralCentroid(),
                'spectral_rolloff': es.SpectralRollOff()
            }
            
            # Image processing components (lazy loaded)
            self.clip_model = None
            self.clip_processor = None
            
            logger.info("AI models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI models: {e}")
            raise
    
    def _initialize_stage_processors(self):
        """Initialize stage-specific processors."""
        self.stage_processors = {
            PipelineStage.PREPROCESSING: self._preprocess_content,
            PipelineStage.FEATURE_EXTRACTION: self._extract_features,
            PipelineStage.FINGERPRINT_GENERATION: self._generate_fingerprint,
            PipelineStage.VECTOR_EMBEDDING: self._generate_vector_embedding,
            PipelineStage.SIMILARITY_ANALYSIS: self._analyze_similarity,
            PipelineStage.POSTPROCESSING: self._postprocess_results,
            PipelineStage.VALIDATION: self._validate_results
        }
    
    async def execute_pipeline(self, task: ProcessingTask) -> PipelineResult:
        """
        Execute complete processing pipeline for task.
        
        Args:
            task: Processing task to execute
            
        Returns:
            PipelineResult: Complete execution result
        """
        execution_id = str(uuid.uuid4())
        start_time = time.time()
        stage_results = []
        
        try:
            pipeline_executions_total.inc()
            pipeline_active_executions.inc()
            
            logger.info(f"Starting pipeline execution {execution_id} for task {task.task_id}")
            
            # Stage 1: Preprocessing
            stage_result = await self._execute_stage(
                PipelineStage.PREPROCESSING,
                task,
                {}
            )
            stage_results.append(stage_result)
            
            if not stage_result.success:
                raise RuntimeError(f"Preprocessing failed: {stage_result.error}")
            
            preprocessed_data = stage_result.data
            
            # Stage 2: Feature Extraction
            stage_result = await self._execute_stage(
                PipelineStage.FEATURE_EXTRACTION,
                task,
                preprocessed_data
            )
            stage_results.append(stage_result)
            
            if not stage_result.success:
                raise RuntimeError(f"Feature extraction failed: {stage_result.error}")
            
            features = stage_result.data
            
            # Parallel execution of fingerprinting and vector embedding
            if self.config.enable_parallel_processing:
                fingerprint_task, embedding_task = await asyncio.gather(
                    self._execute_stage(PipelineStage.FINGERPRINT_GENERATION, task, features),
                    self._execute_stage(PipelineStage.VECTOR_EMBEDDING, task, features),
                    return_exceptions=True
                )
                
                if isinstance(fingerprint_task, Exception):
                    fingerprint_result = StageResult(
                        PipelineStage.FINGERPRINT_GENERATION,
                        False,
                        None,
                        {},
                        0.0,
                        str(fingerprint_task)
                    )
                else:
                    fingerprint_result = fingerprint_task
                
                if isinstance(embedding_task, Exception):
                    embedding_result = StageResult(
                        PipelineStage.VECTOR_EMBEDDING,
                        False,
                        None,
                        {},
                        0.0,
                        str(embedding_task)
                    )
                else:
                    embedding_result = embedding_task
                
                stage_results.extend([fingerprint_result, embedding_result])
            else:
                # Sequential execution
                fingerprint_result = await self._execute_stage(
                    PipelineStage.FINGERPRINT_GENERATION,
                    task,
                    features
                )
                stage_results.append(fingerprint_result)
                
                embedding_result = await self._execute_stage(
                    PipelineStage.VECTOR_EMBEDDING,
                    task,
                    features
                )
                stage_results.append(embedding_result)
            
            # Check critical stages success
            if not fingerprint_result.success and not embedding_result.success:
                raise RuntimeError("Both fingerprinting and embedding failed")
            
            # Stage 5: Similarity Analysis (if enabled)
            similarity_result = None
            if task.input_data.get('enable_similarity_analysis', True):
                similarity_data = {
                    'fingerprint': fingerprint_result.data if fingerprint_result.success else None,
                    'embedding': embedding_result.data if embedding_result.success else None
                }
                
                similarity_result = await self._execute_stage(
                    PipelineStage.SIMILARITY_ANALYSIS,
                    task,
                    similarity_data
                )
                stage_results.append(similarity_result)
            
            # Stage 6: Postprocessing
            postprocess_data = {
                'fingerprint': fingerprint_result.data if fingerprint_result.success else None,
                'embedding': embedding_result.data if embedding_result.success else None,
                'similarity': similarity_result.data if similarity_result and similarity_result.success else None
            }
            
            postprocess_result = await self._execute_stage(
                PipelineStage.POSTPROCESSING,
                task,
                postprocess_data
            )
            stage_results.append(postprocess_result)
            
            # Stage 7: Validation (if enabled)
            if self.config.enable_validation:
                validation_result = await self._execute_stage(
                    PipelineStage.VALIDATION,
                    task,
                    postprocess_result.data
                )
                stage_results.append(validation_result)
                
                if not validation_result.success:
                    logger.warning(f"Validation failed for task {task.task_id}: {validation_result.error}")
            
            # Create final result
            total_time = time.time() - start_time
            
            result = PipelineResult(
                task_id=task.task_id,
                success=True,
                fingerprint=fingerprint_result.data if fingerprint_result.success else None,
                vector_embedding=embedding_result.data if embedding_result.success else None,
                similarity_scores=similarity_result.data if similarity_result and similarity_result.success else None,
                metadata=self._compile_metadata(stage_results),
                stage_results=stage_results,
                total_execution_time=total_time
            )
            
            pipeline_execution_time.observe(total_time)
            logger.info(f"Pipeline execution {execution_id} completed successfully in {total_time:.2f}s")
            
            return result
            
        except Exception as e:
            total_time = time.time() - start_time
            error_msg = f"Pipeline execution failed: {str(e)}"
            logger.error(f"Pipeline execution {execution_id} failed: {error_msg}")
            
            return PipelineResult(
                task_id=task.task_id,
                success=False,
                fingerprint=None,
                vector_embedding=None,
                similarity_scores=None,
                metadata=self._compile_metadata(stage_results),
                stage_results=stage_results,
                total_execution_time=total_time,
                error=error_msg
            )
            
        finally:
            pipeline_active_executions.dec()
            if execution_id in self.active_executions:
                del self.active_executions[execution_id]
    
    async def _execute_stage(
        self, 
        stage: PipelineStage, 
        task: ProcessingTask, 
        input_data: Any
    ) -> StageResult:
        """Execute a single pipeline stage."""
        start_time = time.time()
        
        try:
            processor = self.stage_processors.get(stage)
            if not processor:
                raise ValueError(f"No processor found for stage {stage}")
            
            result_data = await processor(task, input_data)
            execution_time = time.time() - start_time
            
            pipeline_stage_time.labels(stage=stage.value).observe(execution_time)
            
            return StageResult(
                stage=stage,
                success=True,
                data=result_data,
                metadata={'execution_time': execution_time},
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Stage {stage.value} failed: {str(e)}"
            logger.error(error_msg)
            
            return StageResult(
                stage=stage,
                success=False,
                data=None,
                metadata={'execution_time': execution_time},
                execution_time=execution_time,
                error=error_msg
            )
    
    async def _preprocess_content(self, task: ProcessingTask, input_data: Any) -> Dict[str, Any]:
        """Preprocess content based on type."""
        content_data = task.input_data.get('content_data')
        content_type = task.content_type
        
        if content_type == 'audio':
            return await self._preprocess_audio(content_data, task.input_data)
        elif content_type == 'video':
            return await self._preprocess_video(content_data, task.input_data)
        elif content_type == 'image':
            return await self._preprocess_image(content_data, task.input_data)
        elif content_type == 'text':
            return await self._preprocess_text(content_data, task.input_data)
        else:
            raise ValueError(f"Unsupported content type: {content_type}")
    
    async def _preprocess_audio(self, content_data: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess audio content."""
        try:
            # Load audio using librosa
            if isinstance(content_data, str):  # File path
                audio, sr = librosa.load(content_data, sr=params.get('sample_rate', 22050))
            elif isinstance(content_data, bytes):  # Raw audio bytes
                # Handle raw audio data
                audio = np.frombuffer(content_data, dtype=np.float32)
                sr = params.get('sample_rate', 22050)
            else:
                audio = np.array(content_data)
                sr = params.get('sample_rate', 22050)
            
            # Normalize audio
            audio = librosa.util.normalize(audio)
            
            # Trim silence
            audio, _ = librosa.effects.trim(audio, top_db=20)
            
            # Resample if needed
            target_sr = params.get('target_sample_rate', 22050)
            if sr != target_sr:
                audio = librosa.resample(audio, orig_sr=sr, target_sr=target_sr)
                sr = target_sr
            
            return {
                'audio_data': audio,
                'sample_rate': sr,
                'duration': len(audio) / sr,
                'format': 'preprocessed_audio'
            }
            
        except Exception as e:
            raise RuntimeError(f"Audio preprocessing failed: {e}")
    
    async def _preprocess_video(self, content_data: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess video content."""
        try:
            import cv2
            
            if isinstance(content_data, str):  # File path
                cap = cv2.VideoCapture(content_data)
            else:
                # Handle video bytes or array
                raise NotImplementedError("Direct video bytes processing not yet implemented")
            
            frames = []
            frame_rate = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Extract key frames
            extract_interval = params.get('frame_extract_interval', max(1, int(frame_rate)))
            
            frame_count = 0
            while cap.isOpened() and len(frames) < params.get('max_frames', 100):
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % extract_interval == 0:
                    # Resize frame
                    target_size = params.get('frame_size', (224, 224))
                    frame = cv2.resize(frame, target_size)
                    frames.append(frame)
                
                frame_count += 1
            
            cap.release()
            
            return {
                'frames': np.array(frames),
                'frame_rate': frame_rate,
                'total_frames': total_frames,
                'extracted_frames': len(frames),
                'format': 'preprocessed_video'
            }
            
        except Exception as e:
            raise RuntimeError(f"Video preprocessing failed: {e}")
    
    async def _preprocess_image(self, content_data: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess image content."""
        try:
            from PIL import Image
            
            if isinstance(content_data, str):  # File path
                image = Image.open(content_data)
            elif isinstance(content_data, bytes):  # Image bytes
                from io import BytesIO
                image = Image.open(BytesIO(content_data))
            else:
                image = content_data
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if needed
            target_size = params.get('image_size', (224, 224))
            if image.size != target_size:
                image = image.resize(target_size, Image.Resampling.LANCZOS)
            
            # Convert to array
            image_array = np.array(image)
            
            return {
                'image_data': image_array,
                'original_size': image.size,
                'format': 'preprocessed_image',
                'channels': image_array.shape[2] if len(image_array.shape) > 2 else 1
            }
            
        except Exception as e:
            raise RuntimeError(f"Image preprocessing failed: {e}")
    
    async def _preprocess_text(self, content_data: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess text content."""
        try:
            if isinstance(content_data, bytes):
                text = content_data.decode('utf-8')
            else:
                text = str(content_data)
            
            # Clean text
            import re
            
            # Remove extra whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Remove special characters if requested
            if params.get('remove_special_chars', False):
                text = re.sub(r'[^\w\s]', '', text)
            
            # Truncate if too long
            max_length = params.get('max_length', 10000)
            if len(text) > max_length:
                text = text[:max_length]
            
            return {
                'text_data': text,
                'character_count': len(text),
                'word_count': len(text.split()),
                'format': 'preprocessed_text'
            }
            
        except Exception as e:
            raise RuntimeError(f"Text preprocessing failed: {e}")
    
    async def _extract_features(self, task: ProcessingTask, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features from preprocessed content."""
        content_type = task.content_type
        
        if content_type == 'audio':
            return await self._extract_audio_features(input_data)
        elif content_type == 'video':
            return await self._extract_video_features(input_data)
        elif content_type == 'image':
            return await self._extract_image_features(input_data)
        elif content_type == 'text':
            return await self._extract_text_features(input_data)
        else:
            raise ValueError(f"Unsupported content type: {content_type}")
    
    async def _extract_audio_features(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract audio features using Essentia and librosa."""
        try:
            audio_data = input_data['audio_data']
            sr = input_data['sample_rate']
            
            # Extract various audio features
            features = {}
            
            # MFCC features
            mfcc = librosa.feature.mfcc(y=audio_data, sr=sr, n_mfcc=13)
            features['mfcc'] = np.mean(mfcc, axis=1)
            
            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sr)
            features['spectral_centroid'] = np.mean(spectral_centroids)
            
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sr)
            features['spectral_rolloff'] = np.mean(spectral_rolloff)
            
            # Zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(audio_data)
            features['zero_crossing_rate'] = np.mean(zcr)
            
            # Chroma features
            chroma = librosa.feature.chroma_stft(y=audio_data, sr=sr)
            features['chroma'] = np.mean(chroma, axis=1)
            
            # Tempo
            tempo, _ = librosa.beat.beat_track(y=audio_data, sr=sr)
            features['tempo'] = tempo
            
            return {
                'features': features,
                'feature_vector': np.concatenate([
                    features['mfcc'],
                    [features['spectral_centroid']],
                    [features['spectral_rolloff']],
                    [features['zero_crossing_rate']],
                    features['chroma'],
                    [features['tempo']]
                ]),
                'feature_names': ['mfcc', 'spectral_centroid', 'spectral_rolloff', 'zcr', 'chroma', 'tempo']
            }
            
        except Exception as e:
            raise RuntimeError(f"Audio feature extraction failed: {e}")
    
    async def _extract_video_features(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract video features using OpenCV."""
        try:
            frames = input_data['frames']
            
            features = []
            for frame in frames:
                # Convert to grayscale for some features
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Extract ORB features
                orb = cv2.ORB_create()
                keypoints, descriptors = orb.detectAndCompute(gray_frame, None)
                
                # Calculate frame statistics
                frame_features = {
                    'mean_intensity': np.mean(gray_frame),
                    'std_intensity': np.std(gray_frame),
                    'num_keypoints': len(keypoints) if keypoints else 0,
                    'descriptor_mean': np.mean(descriptors) if descriptors is not None else 0
                }
                
                features.append(frame_features)
            
            # Aggregate features across frames
            aggregated_features = {
                'mean_intensity': np.mean([f['mean_intensity'] for f in features]),
                'std_intensity': np.mean([f['std_intensity'] for f in features]),
                'avg_keypoints': np.mean([f['num_keypoints'] for f in features]),
                'descriptor_variance': np.var([f['descriptor_mean'] for f in features])
            }
            
            return {
                'frame_features': features,
                'aggregated_features': aggregated_features,
                'feature_vector': np.array(list(aggregated_features.values())),
                'num_frames': len(frames)
            }
            
        except Exception as e:
            raise RuntimeError(f"Video feature extraction failed: {e}")
    
    async def _extract_image_features(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract image features using various techniques."""
        try:
            image_data = input_data['image_data']
            
            # Color histogram
            hist_r = cv2.calcHist([image_data], [0], None, [256], [0, 256])
            hist_g = cv2.calcHist([image_data], [1], None, [256], [0, 256])
            hist_b = cv2.calcHist([image_data], [2], None, [256], [0, 256])
            
            # Statistical features
            features = {
                'mean_rgb': np.mean(image_data, axis=(0, 1)),
                'std_rgb': np.std(image_data, axis=(0, 1)),
                'hist_correlation': cv2.compareHist(hist_r, hist_g, cv2.HISTCMP_CORREL)
            }
            
            # Texture features using Local Binary Pattern (simplified)
            gray_image = cv2.cvtColor(image_data, cv2.COLOR_RGB2GRAY)
            texture_variance = np.var(gray_image)
            features['texture_variance'] = texture_variance
            
            # Edge features
            edges = cv2.Canny(gray_image, 100, 200)
            features['edge_density'] = np.sum(edges > 0) / edges.size
            
            # Combine into feature vector
            feature_vector = np.concatenate([
                features['mean_rgb'],
                features['std_rgb'],
                [features['hist_correlation']],
                [features['texture_variance']],
                [features['edge_density']]
            ])
            
            return {
                'features': features,
                'feature_vector': feature_vector,
                'histograms': {
                    'red': hist_r.flatten(),
                    'green': hist_g.flatten(),
                    'blue': hist_b.flatten()
                }
            }
            
        except Exception as e:
            raise RuntimeError(f"Image feature extraction failed: {e}")
    
    async def _extract_text_features(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract text features using NLP techniques."""
        try:
            text_data = input_data['text_data']
            
            # Basic text statistics
            words = text_data.split()
            sentences = text_data.split('.')
            
            features = {
                'character_count': len(text_data),
                'word_count': len(words),
                'sentence_count': len(sentences),
                'avg_word_length': np.mean([len(word) for word in words]) if words else 0,
                'avg_sentence_length': np.mean([len(sent.split()) for sent in sentences]) if sentences else 0
            }
            
            # Character n-gram features (simplified)
            char_bigrams = [text_data[i:i+2] for i in range(len(text_data)-1)]
            unique_bigrams = len(set(char_bigrams))
            features['unique_bigrams'] = unique_bigrams
            
            # Word frequency features
            word_freq = {}
            for word in words:
                word_lower = word.lower()
                word_freq[word_lower] = word_freq.get(word_lower, 0) + 1
            
            features['unique_words'] = len(word_freq)
            features['vocabulary_richness'] = len(word_freq) / len(words) if words else 0
            
            # Feature vector
            feature_vector = np.array([
                features['character_count'],
                features['word_count'],
                features['sentence_count'],
                features['avg_word_length'],
                features['avg_sentence_length'],
                features['unique_bigrams'],
                features['unique_words'],
                features['vocabulary_richness']
            ])
            
            return {
                'features': features,
                'feature_vector': feature_vector,
                'word_frequencies': word_freq
            }
            
        except Exception as e:
            raise RuntimeError(f"Text feature extraction failed: {e}")
    
    async def _generate_fingerprint(self, task: ProcessingTask, input_data: Dict[str, Any]) -> str:
        """Generate content fingerprint."""
        content_type = task.content_type
        
        if content_type == 'audio':
            return await self._generate_audio_fingerprint(input_data)
        elif content_type == 'video':
            return await self._generate_video_fingerprint(input_data)
        elif content_type == 'image':
            return await self._generate_image_fingerprint(input_data)
        elif content_type == 'text':
            return await self._generate_text_fingerprint(input_data)
        else:
            raise ValueError(f"Unsupported content type: {content_type}")
    
    async def _generate_audio_fingerprint(self, input_data: Dict[str, Any]) -> str:
        """Generate audio fingerprint using perceptual hashing."""
        try:
            feature_vector = input_data['feature_vector']
            
            # Quantize features to create binary hash
            hash_bits = []
            for i in range(0, len(feature_vector), 2):
                if i + 1 < len(feature_vector):
                    bit = 1 if feature_vector[i] > feature_vector[i + 1] else 0
                    hash_bits.append(str(bit))
            
            # Ensure minimum hash length
            while len(hash_bits) < 32:
                hash_bits.append('0')
            
            fingerprint = ''.join(hash_bits[:64])  # 64-bit hash
            return fingerprint
            
        except Exception as e:
            raise RuntimeError(f"Audio fingerprint generation failed: {e}")
    
    async def _generate_video_fingerprint(self, input_data: Dict[str, Any]) -> str:
        """Generate video fingerprint using frame analysis."""
        try:
            feature_vector = input_data['feature_vector']
            
            # Create hash from aggregated features
            hash_input = ''.join(f"{x:.3f}" for x in feature_vector)
            import hashlib
            fingerprint = hashlib.md5(hash_input.encode()).hexdigest()[:32]
            
            return fingerprint
            
        except Exception as e:
            raise RuntimeError(f"Video fingerprint generation failed: {e}")
    
    async def _generate_image_fingerprint(self, input_data: Dict[str, Any]) -> str:
        """Generate image fingerprint using perceptual hashing."""
        try:
            # Use PIL Image from input_data if available
            if 'image_data' in input_data:
                image_array = input_data['image_data']
                image = Image.fromarray(image_array.astype('uint8'))
                
                # Generate perceptual hash
                phash = imagehash.phash(image)
                return str(phash)
            else:
                # Fallback to feature vector hash
                feature_vector = input_data['feature_vector']
                hash_input = ''.join(f"{x:.3f}" for x in feature_vector)
                import hashlib
                return hashlib.md5(hash_input.encode()).hexdigest()[:32]
            
        except Exception as e:
            raise RuntimeError(f"Image fingerprint generation failed: {e}")
    
    async def _generate_text_fingerprint(self, input_data: Dict[str, Any]) -> str:
        """Generate text fingerprint using content hashing."""
        try:
            feature_vector = input_data['feature_vector']
            
            # Create stable hash from features
            hash_input = ''.join(f"{x:.6f}" for x in feature_vector)
            import hashlib
            fingerprint = hashlib.sha256(hash_input.encode()).hexdigest()[:32]
            
            return fingerprint
            
        except Exception as e:
            raise RuntimeError(f"Text fingerprint generation failed: {e}")
    
    async def _generate_vector_embedding(self, task: ProcessingTask, input_data: Dict[str, Any]) -> np.ndarray:
        """Generate vector embedding for similarity search."""
        try:
            if task.content_type == 'text':
                # Use sentence transformer for text
                text_data = input_data.get('text_data', '')
                embedding = self.text_model.encode([text_data])[0]
                return embedding
            else:
                # Use feature vector as embedding for other types
                feature_vector = input_data['feature_vector']
                
                # Normalize to unit vector
                norm = np.linalg.norm(feature_vector)
                if norm > 0:
                    embedding = feature_vector / norm
                else:
                    embedding = feature_vector
                
                # Ensure consistent dimensionality
                target_dim = 384  # Standard embedding dimension
                if len(embedding) < target_dim:
                    # Pad with zeros
                    padded = np.zeros(target_dim)
                    padded[:len(embedding)] = embedding
                    embedding = padded
                elif len(embedding) > target_dim:
                    # Truncate
                    embedding = embedding[:target_dim]
                
                return embedding
            
        except Exception as e:
            raise RuntimeError(f"Vector embedding generation failed: {e}")
    
    async def _analyze_similarity(self, task: ProcessingTask, input_data: Dict[str, Any]) -> Dict[str, float]:
        """Analyze similarity with existing content."""
        try:
            # This would integrate with vector database for similarity search
            # For now, return placeholder similarity scores
            
            similarity_scores = {
                'max_similarity': 0.0,
                'avg_similarity': 0.0,
                'matches_found': 0
            }
            
            # Placeholder implementation
            # In production, this would query FAISS or similar vector database
            
            return similarity_scores
            
        except Exception as e:
            raise RuntimeError(f"Similarity analysis failed: {e}")
    
    async def _postprocess_results(self, task: ProcessingTask, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Postprocess and format final results."""
        try:
            processed_results = {
                'fingerprint': input_data.get('fingerprint'),
                'vector_embedding': input_data.get('embedding'),
                'similarity_analysis': input_data.get('similarity'),
                'processing_metadata': {
                    'task_id': task.task_id,
                    'content_type': task.content_type,
                    'model_type': task.model_type.value,
                    'processed_at': datetime.utcnow().isoformat(),
                    'quality_score': self._calculate_quality_score(input_data)
                }
            }
            
            return processed_results
            
        except Exception as e:
            raise RuntimeError(f"Postprocessing failed: {e}")
    
    def _calculate_quality_score(self, input_data: Dict[str, Any]) -> float:
        """Calculate quality score for processed content."""
        try:
            # Basic quality scoring based on available data
            quality_factors = []
            
            # Check if fingerprint was generated
            if input_data.get('fingerprint'):
                quality_factors.append(0.4)
            
            # Check if embedding was generated
            if input_data.get('embedding') is not None:
                quality_factors.append(0.4)
            
            # Check similarity analysis
            if input_data.get('similarity'):
                quality_factors.append(0.2)
            
            return sum(quality_factors)
            
        except Exception:
            return 0.5  # Default quality score
    
    async def _validate_results(self, task: ProcessingTask, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate processing results."""
        try:
            validation_results = {
                'fingerprint_valid': bool(input_data.get('fingerprint')),
                'embedding_valid': input_data.get('vector_embedding') is not None,
                'quality_threshold_met': input_data.get('processing_metadata', {}).get('quality_score', 0) >= self.config.quality_threshold,
                'validation_passed': True
            }
            
            # Overall validation
            validation_results['validation_passed'] = all([
                validation_results['fingerprint_valid'] or validation_results['embedding_valid'],
                validation_results['quality_threshold_met']
            ])
            
            return validation_results
            
        except Exception as e:
            raise RuntimeError(f"Validation failed: {e}")
    
    def _compile_metadata(self, stage_results: List[StageResult]) -> Dict[str, Any]:
        """Compile metadata from all stage results."""
        metadata = {
            'stages_executed': len(stage_results),
            'successful_stages': sum(1 for result in stage_results if result.success),
            'total_stage_time': sum(result.execution_time for result in stage_results),
            'stage_details': {}
        }
        
        for result in stage_results:
            metadata['stage_details'][result.stage.value] = {
                'success': result.success,
                'execution_time': result.execution_time,
                'error': result.error
            }
        
        return metadata
    
    async def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline status."""
        return {
            'active_executions': len(self.active_executions),
            'config': {
                'parallel_processing': self.config.enable_parallel_processing,
                'max_parallel_stages': self.config.max_parallel_stages,
                'gpu_acceleration': self.config.enable_gpu_acceleration,
                'quality_threshold': self.config.quality_threshold,
                'timeout_seconds': self.config.timeout_seconds
            },
            'available_stages': list(self.stage_processors.keys())
        }


# Factory function
def create_pipeline(config: Optional[PipelineConfig] = None) -> ProcessingPipeline:
    """Create processing pipeline with configuration."""
    if config is None:
        config = PipelineConfig()
    return ProcessingPipeline(config)
