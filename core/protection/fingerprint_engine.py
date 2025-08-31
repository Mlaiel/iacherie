"""AI Fingerprinting Engine for Multi-Format Content Protection

This module provides advanced fingerprinting capabilities for content protection:
- Audio fingerprinting using Chromaprint and spectral analysis
- Video fingerprinting with frame-based hashing and object detection
- Image fingerprinting using perceptual hashing and CLIP embeddings
- Text fingerprinting with BERT-based semantic analysis
- Vector similarity matching using FAISS

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""import hashlib
import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass
from enum import Enum
import logging
from pathlib import Path
import asyncio
import aiofiles
from concurrent.futures import ThreadPoolExecutor

# Audio processing
import librosa
import chromaprint
from essentia.standard import MonoLoader, Windowing, Spectrum, SpectralPeaks

# Video processing  
import cv2
from PIL import Image
import imagehash

# Text processing
import torch
from transformers import AutoTokenizer, AutoModel, CLIPProcessor, CLIPModel
import sentence_transformers

# Vector operations
import faiss
from sklearn.preprocessing import normalize

# Internal imports
from ...utils.logging import get_logger
from ...database.models.content import ContentFingerprint, ContentType
from ...config.settings import get_settings

logger = get_logger(__name__)
settings = get_settings()


class FingerprintType(Enum):
    """Supported fingerprint types for content protection"""    AUDIO_CHROMAPRINT = "audio_chromaprint"
    AUDIO_SPECTRAL = "audio_spectral"
    VIDEO_PERCEPTUAL = "video_perceptual"
    VIDEO_OBJECT = "video_object"
    IMAGE_PERCEPTUAL = "image_perceptual"
    IMAGE_CLIP = "image_clip"
    TEXT_SEMANTIC = "text_semantic"
    TEXT_SYNTACTIC = "text_syntactic"


@dataclass
class FingerprintResult:
    """Result container for fingerprinting operations"""    fingerprint_type: FingerprintType
    hash_value: str
    vector_embedding: Optional[np.ndarray] = None
    metadata: Optional[Dict[str, Any]] = None
    confidence: float = 1.0
    processing_time: float = 0.0


class AudioFingerprinter:
    """Advanced audio fingerprinting with multiple algorithms"""    
    def __init__(self):
        self.sample_rate = 22050
        self.duration_limit = 300  # 5 minutes max
        
    async def generate_chromaprint(self, audio_path: Path) -> FingerprintResult:
        """Generate Chromaprint fingerprint for audio content"""        try:
            # Load audio with librosa
            y, sr = librosa.load(str(audio_path), sr=self.sample_rate, duration=self.duration_limit)
            
            # Convert to format expected by chromaprint
            audio_data = (y * 32767).astype(np.int16)
            
            # Generate chromaprint
            raw_fingerprint = chromaprint.encode(audio_data, sr)
            
            # Create hash from raw fingerprint
            hash_value = hashlib.sha256(str(raw_fingerprint).encode()).hexdigest()
            
            # Extract numerical features for vector embedding
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
            
            # Combine features into vector
            features = np.concatenate([
                np.mean(chroma, axis=1),
                np.mean(mfcc, axis=1),
                np.mean(spectral_centroid, axis=1)
            ])
            
            metadata = {
                'duration': len(y) / sr,
                'sample_rate': sr,
                'chromaprint_raw': raw_fingerprint,
                'feature_dimensions': len(features)
            }
            
            return FingerprintResult(
                fingerprint_type=FingerprintType.AUDIO_CHROMAPRINT,
                hash_value=hash_value,
                vector_embedding=features,
                metadata=metadata,
                confidence=0.95
            )
            
        except Exception as e:
            logger.error(f"Error generating chromaprint: {e}")
            raise
    
    async def generate_spectral_fingerprint(self, audio_path: Path) -> FingerprintResult:
        """Generate spectral-based fingerprint using Essentia"""        try:
            # Load audio with Essentia
            loader = MonoLoader(filename=str(audio_path), sampleRate=self.sample_rate)
            audio = loader()
            
            # Windowing and spectrum analysis
            windowing = Windowing(type='hann')
            spectrum = Spectrum()
            spectral_peaks = SpectralPeaks()
            
            # Process audio in frames
            frame_size = 2048
            hop_size = 1024
            spectral_features = []
            
            for i in range(0, len(audio) - frame_size, hop_size):
                frame = audio[i:i + frame_size]
                windowed_frame = windowing(frame)
                spectrum_frame = spectrum(windowed_frame)
                peaks_freq, peaks_mag = spectral_peaks(spectrum_frame)
                
                # Extract top spectral peaks
                if len(peaks_freq) > 0:
                    top_peaks = sorted(zip(peaks_freq, peaks_mag), 
                                     key=lambda x: x[1], reverse=True)[:10]
                    spectral_features.extend([freq for freq, _ in top_peaks])
            
            # Create fingerprint from spectral features
            spectral_array = np.array(spectral_features[:100])  # Limit to 100 features
            
            # Normalize and create hash
            normalized_features = normalize([spectral_array])[0]
            hash_value = hashlib.sha256(normalized_features.tobytes()).hexdigest()
            
            metadata = {
                'duration': len(audio) / self.sample_rate,
                'frame_size': frame_size,
                'hop_size': hop_size,
                'features_count': len(spectral_features)
            }
            
            return FingerprintResult(
                fingerprint_type=FingerprintType.AUDIO_SPECTRAL,
                hash_value=hash_value,
                vector_embedding=normalized_features,
                metadata=metadata,
                confidence=0.90
            )
            
        except Exception as e:
            logger.error(f"Error generating spectral fingerprint: {e}")
            raise


class VideoFingerprinter:
    """Advanced video fingerprinting with frame analysis"""    
    def __init__(self):
        self.frame_sample_rate = 1.0  # Extract 1 frame per second
        self.max_frames = 300  # Limit to 5 minutes worth of frames
        
    async def generate_perceptual_fingerprint(self, video_path: Path) -> FingerprintResult:
        """Generate perceptual hash fingerprint for video content"""        try:
            cap = cv2.VideoCapture(str(video_path))
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps > 0 else 0
            
            # Calculate frame sampling interval
            frame_interval = max(1, int(fps / self.frame_sample_rate))
            
            frame_hashes = []
            frame_count = 0
            
            while cap.isOpened() and frame_count < self.max_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Sample frames at specified interval
                if cap.get(cv2.CAP_PROP_POS_FRAMES) % frame_interval == 0:
                    # Convert to PIL Image for hashing
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pil_image = Image.fromarray(frame_rgb)
                    
                    # Generate perceptual hash
                    phash = imagehash.phash(pil_image, hash_size=8)
                    dhash = imagehash.dhash(pil_image, hash_size=8)
                    
                    # Combine hashes
                    combined_hash = str(phash) + str(dhash)
                    frame_hashes.append(combined_hash)
                    frame_count += 1
            
            cap.release()
            
            # Create overall video fingerprint
            video_fingerprint = ''.join(frame_hashes)
            hash_value = hashlib.sha256(video_fingerprint.encode()).hexdigest()
            
            # Create vector embedding from hash patterns
            hash_pattern = np.array([int(c, 16) for c in hash_value[:64]])
            vector_embedding = normalize([hash_pattern])[0]
            
            metadata = {
                'duration': duration,
                'fps': fps,
                'total_frames': total_frames,
                'sampled_frames': len(frame_hashes),
                'frame_interval': frame_interval
            }
            
            return FingerprintResult(
                fingerprint_type=FingerprintType.VIDEO_PERCEPTUAL,
                hash_value=hash_value,
                vector_embedding=vector_embedding,
                metadata=metadata,
                confidence=0.85
            )
            
        except Exception as e:
            logger.error(f"Error generating video perceptual fingerprint: {e}")
            raise
    
    async def generate_object_fingerprint(self, video_path: Path) -> FingerprintResult:
        """Generate object-based fingerprint using YOLO detection"""        try:
            # Note: This would require YOLO model integration
            # For now, implementing a simplified object detection approach
            
            cap = cv2.VideoCapture(str(video_path))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            # Use OpenCV's built-in object detection as placeholder
            # In production, integrate YOLOv8 or similar
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            object_features = []
            frame_count = 0
            
            while cap.isOpened() and frame_count < 100:  # Sample fewer frames for object detection
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % 30 == 0:  # Sample every 30 frames
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    
                    # Detect faces as example objects
                    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                    
                    # Extract features from detections
                    for (x, y, w, h) in faces:
                        # Simple geometric features
                        aspect_ratio = w / h
                        area = w * h
                        center_x = x + w // 2
                        center_y = y + h // 2
                        
                        object_features.extend([aspect_ratio, area / 10000, center_x / frame.shape[1], center_y / frame.shape[0]])
                
                frame_count += 1
            
            cap.release()
            
            # Create fingerprint from object features
            if object_features:
                features_array = np.array(object_features[:64])  # Limit features
                hash_value = hashlib.sha256(features_array.tobytes()).hexdigest()
                vector_embedding = normalize([features_array])[0]
            else:
                # Fallback if no objects detected
                hash_value = hashlib.sha256(b'no_objects_detected').hexdigest()
                vector_embedding = np.zeros(64)
            
            metadata = {
                'objects_detected': len(object_features) // 4,
                'detection_method': 'opencv_cascade',
                'frames_processed': frame_count
            }
            
            return FingerprintResult(
                fingerprint_type=FingerprintType.VIDEO_OBJECT,
                hash_value=hash_value,
                vector_embedding=vector_embedding,
                metadata=metadata,
                confidence=0.75
            )
            
        except Exception as e:
            logger.error(f"Error generating video object fingerprint: {e}")
            raise


class ImageFingerprinter:
    """Advanced image fingerprinting with perceptual and semantic methods"""    
    def __init__(self):
        # Initialize CLIP model for semantic embeddings
        self.clip_model = None
        self.clip_processor = None
        self._load_clip_model()
    
    def _load_clip_model(self):
        """Load CLIP model for semantic image analysis"""        try:
            self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        except Exception as e:
            logger.warning(f"Could not load CLIP model: {e}")
    
    async def generate_perceptual_fingerprint(self, image_path: Path) -> FingerprintResult:
        """Generate perceptual hash fingerprint for image content"""        try:
            # Load image
            image = Image.open(image_path)
            
            # Generate multiple perceptual hashes
            phash = imagehash.phash(image, hash_size=8)
            dhash = imagehash.dhash(image, hash_size=8)
            whash = imagehash.whash(image, hash_size=8)
            ahash = imagehash.average_hash(image, hash_size=8)
            
            # Combine hashes
            combined_hash = str(phash) + str(dhash) + str(whash) + str(ahash)
            hash_value = hashlib.sha256(combined_hash.encode()).hexdigest()
            
            # Create vector embedding from hash patterns
            hash_values = [int(str(h), 16) for h in [phash, dhash, whash, ahash]]
            vector_embedding = normalize([np.array(hash_values)])[0]
            
            metadata = {
                'image_size': image.size,
                'image_mode': image.mode,
                'phash': str(phash),
                'dhash': str(dhash),
                'whash': str(whash),
                'ahash': str(ahash)
            }
            
            return FingerprintResult(
                fingerprint_type=FingerprintType.IMAGE_PERCEPTUAL,
                hash_value=hash_value,
                vector_embedding=vector_embedding,
                metadata=metadata,
                confidence=0.90
            )
            
        except Exception as e:
            logger.error(f"Error generating image perceptual fingerprint: {e}")
            raise
    
    async def generate_clip_fingerprint(self, image_path: Path) -> FingerprintResult:
        """Generate CLIP-based semantic fingerprint for image content"""        try:
            if not self.clip_model:
                raise ValueError("CLIP model not available")
            
            # Load and process image
            image = Image.open(image_path).convert('RGB')
            
            # Process with CLIP
            inputs = self.clip_processor(images=image, return_tensors="pt")
            
            with torch.no_grad():
                image_features = self.clip_model.get_image_features(**inputs)
                embedding = image_features.squeeze().numpy()
            
            # Normalize embedding
            normalized_embedding = normalize([embedding])[0]
            
            # Create hash from embedding
            hash_value = hashlib.sha256(normalized_embedding.tobytes()).hexdigest()
            
            metadata = {
                'embedding_dimension': len(normalized_embedding),
                'model_name': 'clip-vit-base-patch32',
                'image_size': image.size
            }
            
            return FingerprintResult(
                fingerprint_type=FingerprintType.IMAGE_CLIP,
                hash_value=hash_value,
                vector_embedding=normalized_embedding,
                metadata=metadata,
                confidence=0.95
            )
            
        except Exception as e:
            logger.error(f"Error generating CLIP fingerprint: {e}")
            raise


class TextFingerprinter:
    """Advanced text fingerprinting with semantic and syntactic analysis"""    
    def __init__(self):
        # Initialize BERT model for semantic embeddings
        self.bert_model = None
        self.bert_tokenizer = None
        self._load_bert_model()
    
    def _load_bert_model(self):
        """Load BERT model for semantic text analysis"""        try:
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
            self.sentence_model = sentence_transformers.SentenceTransformer(model_name)
        except Exception as e:
            logger.warning(f"Could not load sentence transformer model: {e}")
    
    async def generate_semantic_fingerprint(self, text_content: str) -> FingerprintResult:
        """Generate semantic fingerprint for text content"""        try:
            if not self.sentence_model:
                raise ValueError("Sentence transformer model not available")
            
            # Clean and preprocess text
            cleaned_text = text_content.strip()[:5000]  # Limit to 5000 characters
            
            # Generate semantic embedding
            embedding = self.sentence_model.encode(cleaned_text, normalize_embeddings=True)
            
            # Create hash from embedding
            hash_value = hashlib.sha256(embedding.tobytes()).hexdigest()
            
            # Additional text features
            word_count = len(cleaned_text.split())
            char_count = len(cleaned_text)
            sentence_count = len([s for s in cleaned_text.split('.') if s.strip()])
            
            metadata = {
                'word_count': word_count,
                'char_count': char_count,
                'sentence_count': sentence_count,
                'embedding_dimension': len(embedding),
                'model_name': 'all-MiniLM-L6-v2',
                'text_preview': cleaned_text[:100] + '...' if len(cleaned_text) > 100 else cleaned_text
            }
            
            return FingerprintResult(
                fingerprint_type=FingerprintType.TEXT_SEMANTIC,
                hash_value=hash_value,
                vector_embedding=embedding,
                metadata=metadata,
                confidence=0.88
            )
            
        except Exception as e:
            logger.error(f"Error generating semantic fingerprint: {e}")
            raise
    
    async def generate_syntactic_fingerprint(self, text_content: str) -> FingerprintResult:
        """Generate syntactic fingerprint based on text structure"""        try:
            import re
            import string
            from collections import Counter
            
            # Clean text
            cleaned_text = text_content.strip()
            
            # Extract syntactic features
            features = []
            
            # Character distribution
            char_dist = Counter(cleaned_text.lower())
            for char in string.ascii_lowercase:
                features.append(char_dist.get(char, 0) / len(cleaned_text) if cleaned_text else 0)
            
            # Word length distribution
            words = cleaned_text.split()
            word_lengths = [len(word) for word in words]
            avg_word_length = np.mean(word_lengths) if word_lengths else 0
            features.append(avg_word_length)
            
            # Punctuation frequency
            punct_count = sum(1 for char in cleaned_text if char in string.punctuation)
            features.append(punct_count / len(cleaned_text) if cleaned_text else 0)
            
            # Sentence structure patterns
            sentences = re.split(r'[.!?]+', cleaned_text)
            avg_sentence_length = np.mean([len(s.split()) for s in sentences if s.strip()]) if sentences else 0
            features.append(avg_sentence_length)
            
            # Convert to numpy array and normalize
            features_array = np.array(features)
            normalized_features = normalize([features_array])[0]
            
            # Create hash
            hash_value = hashlib.sha256(normalized_features.tobytes()).hexdigest()
            
            metadata = {
                'feature_count': len(features),
                'avg_word_length': float(avg_word_length),
                'punctuation_ratio': float(punct_count / len(cleaned_text) if cleaned_text else 0),
                'avg_sentence_length': float(avg_sentence_length),
                'text_length': len(cleaned_text)
            }
            
            return FingerprintResult(
                fingerprint_type=FingerprintType.TEXT_SYNTACTIC,
                hash_value=hash_value,
                vector_embedding=normalized_features,
                metadata=metadata,
                confidence=0.80
            )
            
        except Exception as e:
            logger.error(f"Error generating syntactic fingerprint: {e}")
            raise


class FingerprintEngine:
    """Main fingerprinting engine coordinating all content types"""    
    def __init__(self):
        self.audio_fingerprinter = AudioFingerprinter()
        self.video_fingerprinter = VideoFingerprinter()
        self.image_fingerprinter = ImageFingerprinter()
        self.text_fingerprinter = TextFingerprinter()
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # FAISS index for vector similarity search
        self.vector_indexes = {}
        self._initialize_vector_indexes()
    
    def _initialize_vector_indexes(self):
        """Initialize FAISS indexes for different content types"""        try:
            # Initialize indexes for different embedding dimensions
            dimensions = {
                'audio': 26,  # 12 chroma + 13 mfcc + 1 spectral_centroid
                'video': 64,  # Hash-based features
                'image': 512,  # CLIP embeddings
                'text': 384   # Sentence transformer embeddings
            }
            
            for content_type, dim in dimensions.items():
                index = faiss.IndexFlatIP(dim)  # Inner product for normalized vectors
                self.vector_indexes[content_type] = index
                
        except Exception as e:
            logger.error(f"Error initializing FAISS indexes: {e}")
    
    async def generate_fingerprint(self, 
                                 content_path: Path, 
                                 content_type: ContentType,
                                 text_content: Optional[str] = None) -> List[FingerprintResult]:
        """Generate comprehensive fingerprints for content"""        try:
            results = []
            
            if content_type == ContentType.AUDIO:
                # Generate multiple audio fingerprints
                chromaprint_result = await self.audio_fingerprinter.generate_chromaprint(content_path)
                spectral_result = await self.audio_fingerprinter.generate_spectral_fingerprint(content_path)
                results.extend([chromaprint_result, spectral_result])
                
            elif content_type == ContentType.VIDEO:
                # Generate multiple video fingerprints
                perceptual_result = await self.video_fingerprinter.generate_perceptual_fingerprint(content_path)
                object_result = await self.video_fingerprinter.generate_object_fingerprint(content_path)
                results.extend([perceptual_result, object_result])
                
            elif content_type == ContentType.IMAGE:
                # Generate multiple image fingerprints
                perceptual_result = await self.image_fingerprinter.generate_perceptual_fingerprint(content_path)
                try:
                    clip_result = await self.image_fingerprinter.generate_clip_fingerprint(content_path)
                    results.append(clip_result)
                except Exception:
                    logger.warning("CLIP fingerprinting failed, using perceptual only")
                results.append(perceptual_result)
                
            elif content_type == ContentType.TEXT and text_content:
                # Generate multiple text fingerprints
                semantic_result = await self.text_fingerprinter.generate_semantic_fingerprint(text_content)
                syntactic_result = await self.text_fingerprinter.generate_syntactic_fingerprint(text_content)
                results.extend([semantic_result, syntactic_result])
            
            logger.info(f"Generated {len(results)} fingerprints for {content_type} content")
            return results
            
        except Exception as e:
            logger.error(f"Error generating fingerprints: {e}")
            raise
    
    async def find_similar_content(self, 
                                 fingerprint_result: FingerprintResult,
                                 threshold: float = 0.8) -> List[Tuple[str, float]]:
        """Find similar content using vector similarity search"""        try:
            if fingerprint_result.vector_embedding is None:
                return []
            
            # Determine content type from fingerprint type
            content_type_mapping = {
                FingerprintType.AUDIO_CHROMAPRINT: 'audio',
                FingerprintType.AUDIO_SPECTRAL: 'audio',
                FingerprintType.VIDEO_PERCEPTUAL: 'video',
                FingerprintType.VIDEO_OBJECT: 'video',
                FingerprintType.IMAGE_PERCEPTUAL: 'image',
                FingerprintType.IMAGE_CLIP: 'image',
                FingerprintType.TEXT_SEMANTIC: 'text',
                FingerprintType.TEXT_SYNTACTIC: 'text'
            }
            
            content_type = content_type_mapping.get(fingerprint_result.fingerprint_type)
            if not content_type or content_type not in self.vector_indexes:
                return []
            
            index = self.vector_indexes[content_type]
            
            if index.ntotal == 0:
                return []  # No indexed vectors yet
            
            # Search for similar vectors
            query_vector = fingerprint_result.vector_embedding.reshape(1, -1)
            scores, indices = index.search(query_vector, k=10)
            
            # Filter by threshold
            similar_content = []
            for score, idx in zip(scores[0], indices[0]):
                if score >= threshold and idx >= 0:
                    similar_content.append((f"content_{idx}", float(score)))
            
            return similar_content
            
        except Exception as e:
            logger.error(f"Error finding similar content: {e}")
            return []
    
    async def add_to_index(self, fingerprint_result: FingerprintResult, content_id: str):
        """Add fingerprint to vector index for future similarity searches"""        try:
            if fingerprint_result.vector_embedding is None:
                return
            
            # Determine content type
            content_type_mapping = {
                FingerprintType.AUDIO_CHROMAPRINT: 'audio',
                FingerprintType.AUDIO_SPECTRAL: 'audio',
                FingerprintType.VIDEO_PERCEPTUAL: 'video',
                FingerprintType.VIDEO_OBJECT: 'video',
                FingerprintType.IMAGE_PERCEPTUAL: 'image',
                FingerprintType.IMAGE_CLIP: 'image',
                FingerprintType.TEXT_SEMANTIC: 'text',
                FingerprintType.TEXT_SYNTACTIC: 'text'
            }
            
            content_type = content_type_mapping.get(fingerprint_result.fingerprint_type)
            if not content_type or content_type not in self.vector_indexes:
                return
            
            index = self.vector_indexes[content_type]
            vector = fingerprint_result.vector_embedding.reshape(1, -1)
            
            # Add to index
            index.add(vector)
            
            logger.debug(f"Added fingerprint to {content_type} index: {content_id}")
            
        except Exception as e:
            logger.error(f"Error adding fingerprint to index: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get fingerprinting engine statistics"""        return {
            'vector_indexes': {
                content_type: {'count': index.ntotal, 'dimension': index.d}
                for content_type, index in self.vector_indexes.items()
            },
            'supported_types': list(FingerprintType),
            'version': '2.0.0'
        }
