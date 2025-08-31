"""Multi-Modal Embedding Generation Engine
======================================

Advanced embedding generation for multiple content types including audio, video,
image, and text content. Optimized for content fingerprinting and similarity search.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

ATTENTION: Ce code est protégé par les droits d'auteur.
Toute reproduction, distribution ou modification non autorisée est strictement interdite.
"""
import asyncio
import logging
import numpy as np
import torch
import cv2
from typing import Dict, List, Optional, Tuple, Any, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
import io
import base64
from pathlib import Path
import hashlib
import pickle
from concurrent.futures import ThreadPoolExecutor

# Text embedding imports
from sentence_transformers import SentenceTransformer
import transformers
from transformers import AutoModel, AutoTokenizer

# Audio processing imports
import librosa
import torchaudio
import essentia.standard as es
from audiocraft.models import MusicGen

# Image processing imports
from PIL import Image
import torchvision.transforms as transforms
from torchvision.models import resnet50, ResNet50_Weights
import clip

# Video processing imports
import decord
from decord import VideoReader
import torch.nn.functional as F

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingResult:
    """Result of embedding generation."""    content_id: str
    content_type: str
    embedding: np.ndarray
    features: Dict[str, Any]
    metadata: Dict[str, Any]
    processing_time: float
    model_info: Dict[str, str]


@dataclass
class AudioFeatures:
    """Comprehensive audio feature extraction results."""    mfcc: np.ndarray
    chroma: np.ndarray
    spectral_centroid: np.ndarray
    spectral_bandwidth: np.ndarray
    spectral_rolloff: np.ndarray
    zero_crossing_rate: np.ndarray
    tempo: float
    onset_frames: np.ndarray
    harmonic: np.ndarray
    percussive: np.ndarray
    tonnetz: np.ndarray
    spectral_contrast: np.ndarray


@dataclass 
class VideoFeatures:
    """Comprehensive video feature extraction results."""    frame_features: List[np.ndarray]
    optical_flow: np.ndarray
    scene_changes: List[int]
    motion_vectors: np.ndarray
    color_histograms: List[np.ndarray]
    edge_histograms: List[np.ndarray]
    temporal_features: np.ndarray


@dataclass
class ImageFeatures:
    """Comprehensive image feature extraction results."""    visual_features: np.ndarray
    color_histogram: np.ndarray
    edge_histogram: np.ndarray
    texture_features: np.ndarray
    object_detections: List[Dict[str, Any]]
    perceptual_hash: str
    avg_hash: str
    diff_hash: str


class BaseEmbeddingGenerator(ABC):
    """Base class for embedding generators."""    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    @abstractmethod
    async def generate_embedding(self, content: Any, metadata: Dict[str, Any]) -> EmbeddingResult:
        """Generate embedding for content."""        pass
    
    @abstractmethod
    def extract_features(self, content: Any) -> Dict[str, Any]:
        """Extract content-specific features."""        pass
    
    def normalize_embedding(self, embedding: np.ndarray) -> np.ndarray:
        """Normalize embedding vector."""        norm = np.linalg.norm(embedding)
        if norm > 0:
            return embedding / norm
        return embedding


class TextEmbeddingGenerator(BaseEmbeddingGenerator):
    """    Advanced text embedding generator with multiple model support.
    
    Features:
    - Sentence transformers for semantic embeddings
    - BERT/RoBERTa for contextual embeddings
    - Multi-language support
    - Text preprocessing and cleaning
    """    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model_name = config.get('text_model', 'all-MiniLM-L6-v2')
        self.max_length = config.get('max_length', 512)
        
        # Load sentence transformer model
        self.sentence_model = SentenceTransformer(self.model_name)
        self.sentence_model.to(self.device)
        
        # Load BERT model for additional features
        self.bert_model_name = config.get('bert_model', 'bert-base-uncased')
        self.bert_tokenizer = AutoTokenizer.from_pretrained(self.bert_model_name)
        self.bert_model = AutoModel.from_pretrained(self.bert_model_name)
        self.bert_model.to(self.device)
        self.bert_model.eval()
        
        logger.info(f"Text embedding generator initialized with model: {self.model_name}")
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text for embedding generation."""        try:
            # Basic cleaning
            text = text.strip()
            text = ' '.join(text.split())  # Normalize whitespace
            
            # Truncate if too long
            if len(text) > self.max_length * 4:  # Rough character limit
                text = text[:self.max_length * 4]
            
            return text
            
        except Exception as e:
            logger.error(f"Text preprocessing failed: {str(e)}")
            return text
    
    def extract_features(self, text: str) -> Dict[str, Any]:
        """Extract comprehensive text features."""        try:
            features = {}
            
            # Basic text statistics
            features['length'] = len(text)
            features['word_count'] = len(text.split())
            features['sentence_count'] = len([s for s in text.split('.') if s.strip()])
            features['avg_word_length'] = np.mean([len(word) for word in text.split()])
            
            # Language detection (simplified)
            features['language'] = 'en'  # Placeholder - could use langdetect
            
            # Text hash for fingerprinting
            features['text_hash'] = hashlib.sha256(text.encode()).hexdigest()
            
            # Character n-grams
            features['char_trigrams'] = len(set([text[i:i+3] for i in range(len(text)-2)]))
            
            return features
            
        except Exception as e:
            logger.error(f"Text feature extraction failed: {str(e)}")
            return {}
    
    async def generate_embedding(self, text: str, metadata: Dict[str, Any]) -> EmbeddingResult:
        """Generate comprehensive text embedding."""        start_time = datetime.now()
        
        try:
            # Preprocess text
            processed_text = self.preprocess_text(text)
            
            # Generate sentence embedding
            loop = asyncio.get_event_loop()
            sentence_embedding = await loop.run_in_executor(
                self.executor, self.sentence_model.encode, processed_text
            )
            
            # Generate BERT embedding
            bert_embedding = await self._generate_bert_embedding(processed_text)
            
            # Combine embeddings
            combined_embedding = np.concatenate([sentence_embedding, bert_embedding])
            
            # Normalize
            final_embedding = self.normalize_embedding(combined_embedding)
            
            # Extract features
            features = self.extract_features(processed_text)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return EmbeddingResult(
                content_id=metadata.get('content_id', ''),
                content_type='text',
                embedding=final_embedding,
                features=features,
                metadata=metadata,
                processing_time=processing_time,
                model_info={
                    'sentence_model': self.model_name,
                    'bert_model': self.bert_model_name,
                    'dimension': len(final_embedding)
                }
            )
            
        except Exception as e:
            logger.error(f"Text embedding generation failed: {str(e)}")
            raise
    
    async def _generate_bert_embedding(self, text: str) -> np.ndarray:
        """Generate BERT contextual embedding."""        try:
            # Tokenize
            inputs = self.bert_tokenizer(
                text, 
                return_tensors='pt', 
                truncation=True, 
                padding=True, 
                max_length=self.max_length
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate embedding
            with torch.no_grad():
                outputs = self.bert_model(**inputs)
                # Use CLS token embedding
                embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy().flatten()
            
            return embedding
            
        except Exception as e:
            logger.error(f"BERT embedding generation failed: {str(e)}")
            return np.zeros(768)  # Default BERT dimension


class AudioEmbeddingGenerator(BaseEmbeddingGenerator):
    """    Advanced audio embedding generator with comprehensive feature extraction.
    
    Features:
    - Spectral analysis (MFCC, chroma, spectral features)
    - Rhythm and tempo analysis
    - Harmonic/percussive separation
    - Music-specific features
    - Audio fingerprinting
    """    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.sample_rate = config.get('sample_rate', 22050)
        self.duration = config.get('max_duration', 30.0)  # Max 30 seconds
        self.n_mfcc = config.get('n_mfcc', 13)
        self.n_chroma = config.get('n_chroma', 12)
        
        # Initialize Essentia algorithms
        self.windowing = es.Windowing(type='hann')
        self.spectrum = es.Spectrum()
        self.mfcc = es.MFCC()
        self.spectral_peaks = es.SpectralPeaks()
        
        logger.info(f"Audio embedding generator initialized with sample rate: {self.sample_rate}")
    
    def preprocess_audio(self, audio_data: np.ndarray, sr: int) -> Tuple[np.ndarray, int]:
        """Preprocess audio for feature extraction."""        try:
            # Resample if needed
            if sr != self.sample_rate:
                audio_data = librosa.resample(audio_data, orig_sr=sr, target_sr=self.sample_rate)
            
            # Convert to mono if stereo
            if len(audio_data.shape) > 1:
                audio_data = librosa.to_mono(audio_data)
            
            # Trim silence
            audio_data, _ = librosa.effects.trim(audio_data, top_db=20)
            
            # Limit duration
            max_samples = int(self.duration * self.sample_rate)
            if len(audio_data) > max_samples:
                audio_data = audio_data[:max_samples]
            
            # Normalize
            audio_data = librosa.util.normalize(audio_data)
            
            return audio_data, self.sample_rate
            
        except Exception as e:
            logger.error(f"Audio preprocessing failed: {str(e)}")
            return audio_data, sr
    
    def extract_features(self, audio_data: np.ndarray, sr: int = None) -> AudioFeatures:
        """Extract comprehensive audio features."""        try:
            if sr is None:
                sr = self.sample_rate
            
            # Preprocess
            audio, sr = self.preprocess_audio(audio_data, sr)
            
            # MFCC features
            mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=self.n_mfcc)
            
            # Chroma features
            chroma = librosa.feature.chroma_stft(y=audio, sr=sr, n_chroma=self.n_chroma)
            
            # Spectral features
            spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=sr)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr)
            spectral_contrast = librosa.feature.spectral_contrast(y=audio, sr=sr)
            
            # Zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(audio)
            
            # Tempo and beat tracking
            tempo, _ = librosa.beat.beat_track(y=audio, sr=sr)
            
            # Onset detection
            onset_frames = librosa.onset.onset_detect(y=audio, sr=sr)
            
            # Harmonic-percussive separation
            harmonic, percussive = librosa.effects.hpss(audio)
            
            # Tonnetz (harmonic network) features
            tonnetz = librosa.feature.tonnetz(y=harmonic, sr=sr)
            
            return AudioFeatures(
                mfcc=mfcc,
                chroma=chroma,
                spectral_centroid=spectral_centroid,
                spectral_bandwidth=spectral_bandwidth,
                spectral_rolloff=spectral_rolloff,
                zero_crossing_rate=zcr,
                tempo=tempo,
                onset_frames=onset_frames,
                harmonic=harmonic,
                percussive=percussive,
                tonnetz=tonnetz,
                spectral_contrast=spectral_contrast
            )
            
        except Exception as e:
            logger.error(f"Audio feature extraction failed: {str(e)}")
            # Return empty features
            return AudioFeatures(
                mfcc=np.zeros((self.n_mfcc, 1)),
                chroma=np.zeros((self.n_chroma, 1)),
                spectral_centroid=np.zeros((1, 1)),
                spectral_bandwidth=np.zeros((1, 1)),
                spectral_rolloff=np.zeros((1, 1)),
                zero_crossing_rate=np.zeros((1, 1)),
                tempo=0.0,
                onset_frames=np.array([]),
                harmonic=np.zeros(1),
                percussive=np.zeros(1),
                tonnetz=np.zeros((6, 1)),
                spectral_contrast=np.zeros((7, 1))
            )
    
    def features_to_embedding(self, features: AudioFeatures) -> np.ndarray:
        """Convert audio features to a fixed-size embedding vector."""        try:
            embedding_parts = []
            
            # Statistical summaries of time-varying features
            # MFCC statistics
            mfcc_stats = np.concatenate([
                np.mean(features.mfcc, axis=1),
                np.std(features.mfcc, axis=1),
                np.max(features.mfcc, axis=1),
                np.min(features.mfcc, axis=1)
            ])
            embedding_parts.append(mfcc_stats)
            
            # Chroma statistics
            chroma_stats = np.concatenate([
                np.mean(features.chroma, axis=1),
                np.std(features.chroma, axis=1)
            ])
            embedding_parts.append(chroma_stats)
            
            # Spectral feature statistics
            spectral_stats = np.array([
                np.mean(features.spectral_centroid),
                np.std(features.spectral_centroid),
                np.mean(features.spectral_bandwidth),
                np.std(features.spectral_bandwidth),
                np.mean(features.spectral_rolloff),
                np.std(features.spectral_rolloff),
                np.mean(features.zero_crossing_rate),
                np.std(features.zero_crossing_rate)
            ])
            embedding_parts.append(spectral_stats)
            
            # Spectral contrast statistics
            contrast_stats = np.concatenate([
                np.mean(features.spectral_contrast, axis=1),
                np.std(features.spectral_contrast, axis=1)
            ])
            embedding_parts.append(contrast_stats)
            
            # Tonnetz statistics
            tonnetz_stats = np.concatenate([
                np.mean(features.tonnetz, axis=1),
                np.std(features.tonnetz, axis=1)
            ])
            embedding_parts.append(tonnetz_stats)
            
            # Rhythm features
            rhythm_features = np.array([
                features.tempo,
                len(features.onset_frames),  # Number of onsets
                np.std(features.harmonic) if len(features.harmonic) > 0 else 0,
                np.std(features.percussive) if len(features.percussive) > 0 else 0
            ])
            embedding_parts.append(rhythm_features)
            
            # Combine all parts
            embedding = np.concatenate(embedding_parts)
            
            return embedding.astype(np.float32)
            
        except Exception as e:
            logger.error(f"Feature to embedding conversion failed: {str(e)}")
            return np.zeros(200, dtype=np.float32)  # Default size
    
    async def generate_embedding(self, audio_data: np.ndarray, metadata: Dict[str, Any]) -> EmbeddingResult:
        """Generate comprehensive audio embedding."""        start_time = datetime.now()
        
        try:
            sr = metadata.get('sample_rate', self.sample_rate)
            
            # Extract features
            loop = asyncio.get_event_loop()
            features = await loop.run_in_executor(
                self.executor, self.extract_features, audio_data, sr
            )
            
            # Convert to embedding
            embedding = await loop.run_in_executor(
                self.executor, self.features_to_embedding, features
            )
            
            # Normalize
            final_embedding = self.normalize_embedding(embedding)
            
            # Create feature summary for metadata
            feature_summary = {
                'mfcc_shape': features.mfcc.shape,
                'chroma_shape': features.chroma.shape,
                'tempo': float(features.tempo),
                'onset_count': len(features.onset_frames),
                'duration': len(audio_data) / sr,
                'sample_rate': sr
            }
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return EmbeddingResult(
                content_id=metadata.get('content_id', ''),
                content_type='audio',
                embedding=final_embedding,
                features=feature_summary,
                metadata=metadata,
                processing_time=processing_time,
                model_info={
                    'sample_rate': self.sample_rate,
                    'n_mfcc': self.n_mfcc,
                    'n_chroma': self.n_chroma,
                    'dimension': len(final_embedding)
                }
            )
            
        except Exception as e:
            logger.error(f"Audio embedding generation failed: {str(e)}")
            raise


class ImageEmbeddingGenerator(BaseEmbeddingGenerator):
    """    Advanced image embedding generator with comprehensive visual analysis.
    
    Features:
    - Deep CNN features (ResNet, CLIP)
    - Color histograms and analysis
    - Edge and texture analysis
    - Object detection
    - Perceptual hashing
    """    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.image_size = config.get('image_size', 224)
        
        # Load ResNet model
        self.resnet = resnet50(weights=ResNet50_Weights.IMAGENET1K_V1)
        self.resnet.eval()
        self.resnet.to(self.device)
        
        # Load CLIP model
        self.clip_model, self.clip_preprocess = clip.load("ViT-B/32", device=self.device)
        
        # Image preprocessing
        self.transform = transforms.Compose([
            transforms.Resize((self.image_size, self.image_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        logger.info(f"Image embedding generator initialized with size: {self.image_size}")
    
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocess image for feature extraction."""        try:
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize while maintaining aspect ratio
            image.thumbnail((self.image_size * 2, self.image_size * 2), Image.Resampling.LANCZOS)
            
            return image
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {str(e)}")
            return image
    
    def extract_color_features(self, image: Image.Image) -> Dict[str, np.ndarray]:
        """Extract color-based features."""        try:
            # Convert to numpy array
            img_array = np.array(image)
            
            # Color histograms
            hist_r = np.histogram(img_array[:, :, 0], bins=64, range=(0, 256))[0]
            hist_g = np.histogram(img_array[:, :, 1], bins=64, range=(0, 256))[0]
            hist_b = np.histogram(img_array[:, :, 2], bins=64, range=(0, 256))[0]
            
            color_histogram = np.concatenate([hist_r, hist_g, hist_b])
            
            # Dominant colors (simplified)
            pixels = img_array.reshape(-1, 3)
            dominant_colors = np.mean(pixels, axis=0)
            
            return {
                'color_histogram': color_histogram.astype(np.float32),
                'dominant_colors': dominant_colors.astype(np.float32)
            }
            
        except Exception as e:
            logger.error(f"Color feature extraction failed: {str(e)}")
            return {
                'color_histogram': np.zeros(192, dtype=np.float32),
                'dominant_colors': np.zeros(3, dtype=np.float32)
            }
    
    def extract_texture_features(self, image: Image.Image) -> np.ndarray:
        """Extract texture features using edge detection."""        try:
            # Convert to grayscale
            gray = np.array(image.convert('L'))
            
            # Edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Edge histogram
            edge_hist = np.histogram(edges, bins=32, range=(0, 255))[0]
            
            # Texture analysis (simplified using edge statistics)
            edge_density = np.sum(edges > 0) / edges.size
            edge_mean = np.mean(edges)
            edge_std = np.std(edges)
            
            texture_features = np.array([edge_density, edge_mean, edge_std])
            
            return np.concatenate([edge_hist, texture_features]).astype(np.float32)
            
        except Exception as e:
            logger.error(f"Texture feature extraction failed: {str(e)}")
            return np.zeros(35, dtype=np.float32)
    
    def extract_perceptual_hashes(self, image: Image.Image) -> Dict[str, str]:
        """Extract perceptual hashes for image fingerprinting."""        try:
            import imagehash
            
            # Different hash types
            avg_hash = str(imagehash.average_hash(image))
            diff_hash = str(imagehash.dhash(image))
            perceptual_hash = str(imagehash.phash(image))
            
            return {
                'avg_hash': avg_hash,
                'diff_hash': diff_hash,
                'perceptual_hash': perceptual_hash
            }
            
        except Exception as e:
            logger.error(f"Perceptual hash extraction failed: {str(e)}")
            return {
                'avg_hash': '',
                'diff_hash': '',
                'perceptual_hash': ''
            }
    
    def extract_features(self, image: Image.Image) -> ImageFeatures:
        """Extract comprehensive image features."""        try:
            # Preprocess image
            processed_image = self.preprocess_image(image)
            
            # Extract different feature types
            color_features = self.extract_color_features(processed_image)
            texture_features = self.extract_texture_features(processed_image)
            hashes = self.extract_perceptual_hashes(processed_image)
            
            # Visual features using ResNet
            img_tensor = self.transform(processed_image).unsqueeze(0).to(self.device)
            with torch.no_grad():
                visual_features = self.resnet(img_tensor).cpu().numpy().flatten()
            
            # Placeholder for object detection
            object_detections = []  # Would use YOLO or similar
            
            return ImageFeatures(
                visual_features=visual_features,
                color_histogram=color_features['color_histogram'],
                edge_histogram=texture_features[:32],  # Edge histogram part
                texture_features=texture_features[32:],  # Texture stats part
                object_detections=object_detections,
                perceptual_hash=hashes['perceptual_hash'],
                avg_hash=hashes['avg_hash'],
                diff_hash=hashes['diff_hash']
            )
            
        except Exception as e:
            logger.error(f"Image feature extraction failed: {str(e)}")
            # Return empty features
            return ImageFeatures(
                visual_features=np.zeros(1000, dtype=np.float32),
                color_histogram=np.zeros(192, dtype=np.float32),
                edge_histogram=np.zeros(32, dtype=np.float32),
                texture_features=np.zeros(3, dtype=np.float32),
                object_detections=[],
                perceptual_hash='',
                avg_hash='',
                diff_hash=''
            )
    
    async def generate_embedding(self, image: Image.Image, metadata: Dict[str, Any]) -> EmbeddingResult:
        """Generate comprehensive image embedding."""        start_time = datetime.now()
        
        try:
            # Extract features
            loop = asyncio.get_event_loop()
            features = await loop.run_in_executor(
                self.executor, self.extract_features, image
            )
            
            # Generate CLIP embedding
            clip_image = self.clip_preprocess(image).unsqueeze(0).to(self.device)
            with torch.no_grad():
                clip_features = self.clip_model.encode_image(clip_image).cpu().numpy().flatten()
            
            # Combine features
            combined_features = np.concatenate([
                features.visual_features,
                clip_features,
                features.color_histogram,
                features.texture_features
            ])
            
            # Normalize
            final_embedding = self.normalize_embedding(combined_features)
            
            # Create feature summary
            feature_summary = {
                'image_size': image.size,
                'mode': image.mode,
                'perceptual_hash': features.perceptual_hash,
                'avg_hash': features.avg_hash,
                'diff_hash': features.diff_hash,
                'object_count': len(features.object_detections)
            }
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return EmbeddingResult(
                content_id=metadata.get('content_id', ''),
                content_type='image',
                embedding=final_embedding,
                features=feature_summary,
                metadata=metadata,
                processing_time=processing_time,
                model_info={
                    'resnet_model': 'resnet50',
                    'clip_model': 'ViT-B/32',
                    'image_size': self.image_size,
                    'dimension': len(final_embedding)
                }
            )
            
        except Exception as e:
            logger.error(f"Image embedding generation failed: {str(e)}")
            raise


class VideoEmbeddingGenerator(BaseEmbeddingGenerator):
    """    Advanced video embedding generator with temporal and spatial analysis.
    
    Features:
    - Frame-level visual analysis
    - Temporal motion analysis
    - Scene change detection
    - Audio track processing
    - Video fingerprinting
    """    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.max_frames = config.get('max_frames', 100)
        self.frame_step = config.get('frame_step', 10)
        self.image_generator = ImageEmbeddingGenerator(config)
        self.audio_generator = AudioEmbeddingGenerator(config)
        
        logger.info(f"Video embedding generator initialized with max frames: {self.max_frames}")
    
    def extract_frames(self, video_path: str) -> List[np.ndarray]:
        """Extract frames from video."""        try:
            vr = VideoReader(video_path, ctx=decord.cpu(0))
            total_frames = len(vr)
            
            # Sample frames
            frame_indices = np.linspace(0, total_frames - 1, 
                                      min(self.max_frames, total_frames), 
                                      dtype=int)
            
            frames = vr.get_batch(frame_indices).asnumpy()
            
            return [frame for frame in frames]
            
        except Exception as e:
            logger.error(f"Frame extraction failed: {str(e)}")
            return []
    
    def detect_scene_changes(self, frames: List[np.ndarray]) -> List[int]:
        """Detect scene changes in video frames."""        try:
            scene_changes = []
            
            if len(frames) < 2:
                return scene_changes
            
            prev_frame = cv2.cvtColor(frames[0], cv2.COLOR_RGB2GRAY)
            
            for i, frame in enumerate(frames[1:], 1):
                curr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
                
                # Calculate frame difference
                diff = cv2.absdiff(prev_frame, curr_frame)
                diff_score = np.mean(diff)
                
                # Threshold for scene change
                if diff_score > 50:  # Adjustable threshold
                    scene_changes.append(i)
                
                prev_frame = curr_frame
            
            return scene_changes
            
        except Exception as e:
            logger.error(f"Scene change detection failed: {str(e)}")
            return []
    
    def extract_motion_vectors(self, frames: List[np.ndarray]) -> np.ndarray:
        """Extract motion vectors between frames."""        try:
            if len(frames) < 2:
                return np.zeros((0, 2))
            
            motion_vectors = []
            
            for i in range(len(frames) - 1):
                frame1 = cv2.cvtColor(frames[i], cv2.COLOR_RGB2GRAY)
                frame2 = cv2.cvtColor(frames[i + 1], cv2.COLOR_RGB2GRAY)
                
                # Calculate optical flow
                flow = cv2.calcOpticalFlowPyrLK(
                    frame1, frame2,
                    np.array([[100, 100]], dtype=np.float32),  # Points to track
                    None
                )[0]
                
                if flow is not None and len(flow) > 0:
                    motion_vectors.append(flow[0])
            
            return np.array(motion_vectors) if motion_vectors else np.zeros((0, 2))
            
        except Exception as e:
            logger.error(f"Motion vector extraction failed: {str(e)}")
            return np.zeros((0, 2))
    
    def extract_features(self, video_path: str) -> VideoFeatures:
        """Extract comprehensive video features."""        try:
            # Extract frames
            frames = self.extract_frames(video_path)
            
            if not frames:
                # Return empty features
                return VideoFeatures(
                    frame_features=[],
                    optical_flow=np.zeros((0, 2)),
                    scene_changes=[],
                    motion_vectors=np.zeros((0, 2)),
                    color_histograms=[],
                    edge_histograms=[],
                    temporal_features=np.zeros(10)
                )
            
            # Extract frame-level features
            frame_features = []
            color_histograms = []
            edge_histograms = []
            
            for frame in frames:
                # Convert to PIL Image for image generator
                pil_frame = Image.fromarray(frame)
                
                # Extract image features (simplified)
                img_features = self.image_generator.extract_color_features(pil_frame)
                texture_features = self.image_generator.extract_texture_features(pil_frame)
                
                frame_features.append(img_features['color_histogram'])
                color_histograms.append(img_features['color_histogram'])
                edge_histograms.append(texture_features[:32])
            
            # Detect scene changes
            scene_changes = self.detect_scene_changes(frames)
            
            # Extract motion vectors
            motion_vectors = self.extract_motion_vectors(frames)
            
            # Temporal features (summary statistics)
            temporal_features = np.array([
                len(frames),  # Number of frames
                len(scene_changes),  # Number of scene changes
                np.mean([np.std(feat) for feat in frame_features]) if frame_features else 0,  # Visual stability
                np.mean(np.linalg.norm(motion_vectors, axis=1)) if len(motion_vectors) > 0 else 0,  # Average motion
                0, 0, 0, 0, 0, 0  # Placeholder for additional temporal features
            ])
            
            return VideoFeatures(
                frame_features=frame_features,
                optical_flow=np.zeros((0, 2)),  # Simplified
                scene_changes=scene_changes,
                motion_vectors=motion_vectors,
                color_histograms=color_histograms,
                edge_histograms=edge_histograms,
                temporal_features=temporal_features
            )
            
        except Exception as e:
            logger.error(f"Video feature extraction failed: {str(e)}")
            # Return empty features
            return VideoFeatures(
                frame_features=[],
                optical_flow=np.zeros((0, 2)),
                scene_changes=[],
                motion_vectors=np.zeros((0, 2)),
                color_histograms=[],
                edge_histograms=[],
                temporal_features=np.zeros(10)
            )
    
    async def generate_embedding(self, video_path: str, metadata: Dict[str, Any]) -> EmbeddingResult:
        """Generate comprehensive video embedding."""        start_time = datetime.now()
        
        try:
            # Extract features
            loop = asyncio.get_event_loop()
            features = await loop.run_in_executor(
                self.executor, self.extract_features, video_path
            )
            
            # Aggregate frame features
            if features.frame_features:
                aggregated_visual = np.mean(features.frame_features, axis=0)
            else:
                aggregated_visual = np.zeros(192)  # Default color histogram size
            
            # Combine features
            combined_features = np.concatenate([
                aggregated_visual,
                features.temporal_features,
                np.mean(features.motion_vectors, axis=0) if len(features.motion_vectors) > 0 else np.zeros(2)
            ])
            
            # Normalize
            final_embedding = self.normalize_embedding(combined_features)
            
            # Create feature summary
            feature_summary = {
                'frame_count': len(features.frame_features),
                'scene_changes': len(features.scene_changes),
                'motion_intensity': float(np.mean(np.linalg.norm(features.motion_vectors, axis=1))) if len(features.motion_vectors) > 0 else 0.0,
                'duration_estimate': len(features.frame_features) / 30.0  # Assume 30 FPS
            }
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return EmbeddingResult(
                content_id=metadata.get('content_id', ''),
                content_type='video',
                embedding=final_embedding,
                features=feature_summary,
                metadata=metadata,
                processing_time=processing_time,
                model_info={
                    'max_frames': self.max_frames,
                    'frame_step': self.frame_step,
                    'dimension': len(final_embedding)
                }
            )
            
        except Exception as e:
            logger.error(f"Video embedding generation failed: {str(e)}")
            raise


class MultiModalEmbeddingEngine:
    """    Unified engine for multi-modal embedding generation.
    
    Coordinates different embedding generators and provides a unified interface
    for processing various content types.
    """    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Initialize generators
        self.text_generator = TextEmbeddingGenerator(config.get('text', {}))
        self.audio_generator = AudioEmbeddingGenerator(config.get('audio', {}))
        self.image_generator = ImageEmbeddingGenerator(config.get('image', {}))
        self.video_generator = VideoEmbeddingGenerator(config.get('video', {}))
        
        logger.info("Multi-modal embedding engine initialized")
    
    async def generate_embedding(self, content: Any, content_type: str, 
                               metadata: Dict[str, Any]) -> EmbeddingResult:
        """Generate embedding for any content type."""        try:
            if content_type == 'text':
                return await self.text_generator.generate_embedding(content, metadata)
            elif content_type == 'audio':
                return await self.audio_generator.generate_embedding(content, metadata)
            elif content_type == 'image':
                return await self.image_generator.generate_embedding(content, metadata)
            elif content_type == 'video':
                return await self.video_generator.generate_embedding(content, metadata)
            else:
                raise ValueError(f"Unsupported content type: {content_type}")
                
        except Exception as e:
            logger.error(f"Embedding generation failed for {content_type}: {str(e)}")
            raise
    
    def get_supported_types(self) -> List[str]:
        """Get list of supported content types."""        return ['text', 'audio', 'image', 'video']
    
    def get_embedding_dimensions(self) -> Dict[str, int]:
        """Get embedding dimensions for each content type."""        return {
            'text': self.text_generator.sentence_model.get_sentence_embedding_dimension() + 768,  # Sentence + BERT
            'audio': 200,  # Estimated based on feature extraction
            'image': 1000 + 512 + 192 + 3,  # ResNet + CLIP + color + texture
            'video': 192 + 10 + 2  # Aggregated visual + temporal + motion
        }


# Export classes
__all__ = [
    'MultiModalEmbeddingEngine',
    'TextEmbeddingGenerator',
    'AudioEmbeddingGenerator', 
    'ImageEmbeddingGenerator',
    'VideoEmbeddingGenerator',
    'EmbeddingResult',
    'AudioFeatures',
    'VideoFeatures',
    'ImageFeatures'
]
