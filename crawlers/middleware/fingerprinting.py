"""
Fingerprinting Middleware Module
===============================

Enterprise-grade fingerprinting middleware for crawler pipeline.
Implements multi-format content fingerprinting, similarity detection, and protection.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

Business Logic Pipeline:
Multi-format Creators → IA Protection → SEO Optimization → Collaboration Matching → Distribution

Key Features:
- Audio fingerprinting: Chromaprint, spectral analysis, MFCC
- Video fingerprinting: Perceptual hashing, motion vectors, frame analysis
- Image fingerprinting: pHash, dHash, CLIP embeddings, visual similarity
- Text fingerprinting: Semantic embeddings, structural analysis, plagiarism detection
- Real-time similarity detection with FAISS vector search
- Multi-platform content monitoring and protection
"""

import asyncio
import json
import time
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Union, Any, Tuple
from enum import Enum
import numpy as np
import cv2
import librosa
from PIL import Image
import imagehash
import chromaprint
import faiss
from transformers import CLIPProcessor, CLIPModel, AutoTokenizer, AutoModel
import torch
import tempfile
from pathlib import Path

from pydantic import BaseModel, Field
import logging

from ...config.settings import get_settings
from ...utils.cache import CacheManager
from ...ai.models.protection_models import UniversalFingerprintEngine

settings = get_settings()
logger = logging.getLogger(__name__)


class FingerprintType(str, Enum):
    """Supported fingerprint types"""
    AUDIO_CHROMAPRINT = "audio_chromaprint"
    AUDIO_SPECTRAL = "audio_spectral"
    AUDIO_MFCC = "audio_mfcc"
    AUDIO_TEMPO = "audio_tempo"
    VIDEO_PERCEPTUAL = "video_perceptual"
    VIDEO_MOTION = "video_motion"
    VIDEO_HISTOGRAM = "video_histogram"
    VIDEO_OPTICAL_FLOW = "video_optical_flow"
    IMAGE_PHASH = "image_phash"
    IMAGE_DHASH = "image_dhash"
    IMAGE_WHASH = "image_whash"
    IMAGE_CLIP = "image_clip"
    TEXT_SEMANTIC = "text_semantic"
    TEXT_STRUCTURAL = "text_structural"
    TEXT_BERT = "text_bert"
    TEXT_NGRAM = "text_ngram"


class ContentProtectionLevel(str, Enum):
    """Content protection levels"""
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class FingerprintRequest(BaseModel):
    """Fingerprint generation request model"""
    content_id: str = Field(description="Unique content identifier")
    content_type: str = Field(description="Type of content")
    content_data: Union[str, bytes, Dict[str, Any]] = Field(description="Content data")
    fingerprint_types: List[FingerprintType] = Field(description="Requested fingerprint types")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Content metadata")
    quality_level: ContentProtectionLevel = Field(default=ContentProtectionLevel.STANDARD, 
                                                 description="Fingerprint quality level")
    enable_similarity_search: bool = Field(default=True, description="Enable similarity search")
    similarity_threshold: float = Field(default=0.85, description="Similarity threshold")


class FingerprintResult(BaseModel):
    """Fingerprint generation result model"""
    content_id: str = Field(description="Content identifier")
    fingerprints: Dict[str, str] = Field(description="Generated fingerprints")
    similarity_vectors: Dict[str, List[float]] = Field(default_factory=dict, description="Similarity vectors")
    confidence_scores: Dict[str, float] = Field(default_factory=dict, description="Confidence scores")
    similar_content: List[Dict[str, Any]] = Field(default_factory=list, description="Similar content found")
    protection_metadata: Dict[str, Any] = Field(default_factory=dict, description="Protection metadata")
    processing_time: float = Field(description="Processing duration")
    error: Optional[str] = Field(None, description="Error message if failed")


class AudioFingerprinter:
    """Advanced audio fingerprinting engine"""
    
    def __init__(self):
        self.supported_formats = ['.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac']
        self.cache = CacheManager()
        
    async def generate_chromaprint(self, audio_data: bytes) -> Tuple[str, List[float]]:
        """Generate Chromaprint fingerprint"""



        try:
            import tempfile
            from pathlib import Path
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name
            
            try:
                # Load audio with librosa
                audio_array, sample_rate = librosa.load(temp_path, sr=None)
                
                # Convert to int16 format for chromaprint
                audio_int16 = (audio_array * 32767).astype(np.int16)
                
                # Generate chromaprint fingerprint
                fingerprint = chromaprint.encode(audio_int16, sample_rate)
                
                # Generate similarity vector (chroma features)
                chroma = librosa.feature.chroma(y=audio_array, sr=sample_rate)
                similarity_vector = np.mean(chroma, axis=1).tolist()
                
                return fingerprint, similarity_vector
                
            finally:
                Path(temp_path).unlink(missing_ok=True)
                
        except Exception as e:
            logger.error(f"Chromaprint generation error: {e}")
            raise
    
    async def generate_spectral_fingerprint(self, audio_data: bytes) -> Tuple[str, List[float]]:
        """Generate spectral fingerprint"""



        try:
            import tempfile
            from pathlib import Path
            
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name
            
            try:
                # Load audio
                audio_array, sample_rate = librosa.load(temp_path, sr=None)
                
                # Extract spectral features
                mfcc = librosa.feature.mfcc(y=audio_array, sr=sample_rate, n_mfcc=13)
                spectral_centroid = librosa.feature.spectral_centroid(y=audio_array, sr=sample_rate)
                spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio_array, sr=sample_rate)
                spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_array, sr=sample_rate)
                
                # Combine features into fingerprint vector
                features = np.concatenate([
                    np.mean(mfcc, axis=1),
                    np.mean(spectral_centroid, axis=1),
                    np.mean(spectral_bandwidth, axis=1),
                    np.mean(spectral_rolloff, axis=1)
                ])
                
                # Create hash from features
                feature_string = ','.join(f'{f:.6f}' for f in features)
                fingerprint = hashlib.sha256(feature_string.encode()).hexdigest()
                
                return fingerprint, features.tolist()
                
            finally:
                Path(temp_path).unlink(missing_ok=True)
                
        except Exception as e:
            logger.error(f"Spectral fingerprint generation error: {e}")
            raise
    
    async def generate_fingerprints(self, audio_data: bytes, 
                                  types: List[FingerprintType]) -> Dict[str, Tuple[str, List[float]]]:
        """Generate multiple audio fingerprints"""
        results = {}
        
        if FingerprintType.AUDIO_CHROMAPRINT in types:
            try:
                fingerprint, vector = await self.generate_chromaprint(audio_data)
                results[FingerprintType.AUDIO_CHROMAPRINT.value] = (fingerprint, vector)
            except Exception as e:
                logger.error(f"Chromaprint generation failed: {e}")
        
        if FingerprintType.AUDIO_SPECTRAL in types:
            try:
                fingerprint, vector = await self.generate_spectral_fingerprint(audio_data)
                results[FingerprintType.AUDIO_SPECTRAL.value] = (fingerprint, vector)
            except Exception as e:
                logger.error(f"Spectral fingerprint generation failed: {e}")
        
        return results


class VideoFingerprinter:
    """Advanced video fingerprinting engine"""
    
    def __init__(self):
        self.supported_formats = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        
    async def generate_perceptual_fingerprint(self, video_data: bytes) -> Tuple[str, List[float]]:
        """Generate perceptual hash fingerprint"""



        try:
            import tempfile
            from pathlib import Path
            
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
                temp_file.write(video_data)
                temp_path = temp_file.name
            
            try:
                # Load video
                cap = cv2.VideoCapture(temp_path)
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                
                # Sample frames (every second)
                frame_skip = max(1, int(fps))
                frames = []
                fingerprints = []
                
                for i in range(0, frame_count, frame_skip):
                    cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                    ret, frame = cap.read()
                    if ret:
                        frames.append(frame)
                        
                        # Generate perceptual hash for frame
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        resized = cv2.resize(gray, (8, 8))
                        avg = resized.mean()
                        binary = (resized > avg).flatten()
                        frame_hash = ''.join(['1' if x else '0' for x in binary])
                        fingerprints.append(frame_hash)
                    
                    if len(frames) >= 30:  # Limit to 30 frames
                        break
                
                cap.release()
                
                # Combine frame hashes
                combined_hash = ''.join(fingerprints)
                fingerprint = hashlib.sha256(combined_hash.encode()).hexdigest()
                
                # Generate similarity vector from frame statistics
                if frames:
                    frame_stats = []
                    for frame in frames:
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        mean_brightness = np.mean(gray)
                        std_brightness = np.std(gray)
                        frame_stats.extend([mean_brightness, std_brightness])
                    
                    # Normalize and truncate to fixed size
                    similarity_vector = frame_stats[:100]  # Max 100 features
                    while len(similarity_vector) < 100:
                        similarity_vector.append(0.0)
                else:
                    similarity_vector = [0.0] * 100
                
                return fingerprint, similarity_vector
                
            finally:
                Path(temp_path).unlink(missing_ok=True)
                
        except Exception as e:
            logger.error(f"Video perceptual fingerprint generation error: {e}")
            raise
    
    async def generate_motion_fingerprint(self, video_data: bytes) -> Tuple[str, List[float]]:
        """Generate motion-based fingerprint"""



        try:
            import tempfile
            from pathlib import Path
            
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
                temp_file.write(video_data)
                temp_path = temp_file.name
            
            try:
                # Load video
                cap = cv2.VideoCapture(temp_path)
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                
                # Analyze motion between frames
                prev_frame = None
                motion_vectors = []
                
                frame_skip = max(1, int(fps // 2))  # Every 0.5 seconds
                
                for i in range(0, frame_count, frame_skip):
                    cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                    ret, frame = cap.read()
                    if ret:
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        
                        if prev_frame is not None:
                            # Calculate optical flow
                            flow = cv2.calcOpticalFlowPyrLK(prev_frame, gray, None, None)
                            
                            if flow[0] is not None:
                                # Calculate motion statistics
                                motion_magnitude = np.mean(np.sqrt(flow[0][:, :, 0]**2 + flow[0][:, :, 1]**2))
                                motion_angle = np.mean(np.arctan2(flow[0][:, :, 1], flow[0][:, :, 0]))
                                motion_vectors.extend([motion_magnitude, motion_angle])
                        
                        prev_frame = gray.copy()
                    
                    if len(motion_vectors) >= 60:  # Limit features
                        break
                
                cap.release()
                
                # Create fingerprint from motion data
                if motion_vectors:
                    motion_string = ','.join(f'{v:.6f}' for v in motion_vectors)
                    fingerprint = hashlib.sha256(motion_string.encode()).hexdigest()
                    
                    # Normalize similarity vector
                    similarity_vector = motion_vectors[:100]  # Max 100 features
                    while len(similarity_vector) < 100:
                        similarity_vector.append(0.0)
                else:
                    fingerprint = hashlib.sha256(b'no_motion_detected').hexdigest()
                    similarity_vector = [0.0] * 100
                
                return fingerprint, similarity_vector
                
            finally:
                Path(temp_path).unlink(missing_ok=True)
                
        except Exception as e:
            logger.error(f"Video motion fingerprint generation error: {e}")
            raise
    
    async def generate_fingerprints(self, video_data: bytes, 
                                  types: List[FingerprintType]) -> Dict[str, Tuple[str, List[float]]]:
        """Generate multiple video fingerprints"""
        results = {}
        
        if FingerprintType.VIDEO_PERCEPTUAL in types:
            try:
                fingerprint, vector = await self.generate_perceptual_fingerprint(video_data)
                results[FingerprintType.VIDEO_PERCEPTUAL.value] = (fingerprint, vector)
            except Exception as e:
                logger.error(f"Video perceptual fingerprint generation failed: {e}")
        
        if FingerprintType.VIDEO_MOTION in types:
            try:
                fingerprint, vector = await self.generate_motion_fingerprint(video_data)
                results[FingerprintType.VIDEO_MOTION.value] = (fingerprint, vector)
            except Exception as e:
                logger.error(f"Video motion fingerprint generation failed: {e}")
        
        return results


class ImageFingerprinter:
    """Advanced image fingerprinting engine"""
    
    def __init__(self):
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        
    async def generate_perceptual_hash(self, image_data: bytes) -> Tuple[str, List[float]]:
        """Generate perceptual hash fingerprint"""



        try:
            from io import BytesIO
            
            # Load image
            image = Image.open(BytesIO(image_data))
            
            # Generate perceptual hash
            phash = str(imagehash.phash(image))
            
            # Convert to similarity vector
            # Each hex character represents 4 bits
            binary_str = bin(int(phash, 16))[2:].zfill(64)  # 64-bit hash
            similarity_vector = [float(bit) for bit in binary_str]
            
            return phash, similarity_vector
            
        except Exception as e:
            logger.error(f"Image perceptual hash generation error: {e}")
            raise
    
    async def generate_difference_hash(self, image_data: bytes) -> Tuple[str, List[float]]:
        """Generate difference hash fingerprint"""



        try:
            from io import BytesIO
            
            # Load image
            image = Image.open(BytesIO(image_data))
            
            # Generate difference hash
            dhash = str(imagehash.dhash(image))
            
            # Convert to similarity vector
            binary_str = bin(int(dhash, 16))[2:].zfill(64)  # 64-bit hash
            similarity_vector = [float(bit) for bit in binary_str]
            
            return dhash, similarity_vector
            
        except Exception as e:
            logger.error(f"Image difference hash generation error: {e}")
            raise
    
    async def generate_advanced_features(self, image_data: bytes) -> Tuple[str, List[float]]:
        """Generate advanced feature-based fingerprint"""



        try:
            from io import BytesIO
            import cv2
            
            # Load image
            image = Image.open(BytesIO(image_data))
            img_array = np.array(image)
            
            # Convert to grayscale if needed
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # Extract features
            features = []
            
            # Color moments
            if len(img_array.shape) == 3:
                for channel in range(img_array.shape[2]):
                    channel_data = img_array[:, :, channel]
                    features.extend([
                        np.mean(channel_data),
                        np.std(channel_data),
                        np.var(channel_data)
                    ])
            else:
                features.extend([
                    np.mean(gray),
                    np.std(gray),
                    np.var(gray)
                ])
            
            # Texture features (Local Binary Pattern)
            from skimage import feature
            lbp = feature.local_binary_pattern(gray, 8, 1, method='uniform')
            lbp_hist, _ = np.histogram(lbp.ravel(), bins=10)
            features.extend(lbp_hist.tolist())
            
            # Edge features
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            features.append(edge_density)
            
            # Create fingerprint hash
            feature_string = ','.join(f'{f:.6f}' for f in features)
            fingerprint = hashlib.sha256(feature_string.encode()).hexdigest()
            
            return fingerprint, features
            
        except Exception as e:
            logger.error(f"Image advanced features generation error: {e}")
            raise
    
    async def generate_fingerprints(self, image_data: bytes, 
                                  types: List[FingerprintType]) -> Dict[str, Tuple[str, List[float]]]:
        """Generate multiple image fingerprints"""
        results = {}
        
        if FingerprintType.IMAGE_PHASH in types:
            try:
                fingerprint, vector = await self.generate_perceptual_hash(image_data)
                results[FingerprintType.IMAGE_PHASH.value] = (fingerprint, vector)
            except Exception as e:
                logger.error(f"Image perceptual hash generation failed: {e}")
        
        if FingerprintType.IMAGE_DHASH in types:
            try:
                fingerprint, vector = await self.generate_difference_hash(image_data)
                results[FingerprintType.IMAGE_DHASH.value] = (fingerprint, vector)
            except Exception as e:
                logger.error(f"Image difference hash generation failed: {e}")
        
        return results


class TextFingerprinter:
    """Advanced text fingerprinting engine"""
    
    def __init__(self):
        try:
            from transformers import pipeline
            self.embedder = pipeline("feature-extraction", model="bert-base-uncased")
        except:
            self.embedder = None
            logger.warning("BERT model not available for text fingerprinting")
        
    async def generate_semantic_fingerprint(self, text_data: str) -> Tuple[str, List[float]]:
        """Generate semantic fingerprint using NLP"""



        try:
            # Simple word frequency-based approach if BERT not available
            if not self.embedder:
                words = text_data.lower().split()
                word_freq = {}
                for word in words:
                    word_freq[word] = word_freq.get(word, 0) + 1
                
                # Get top words and create vector
                sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
                top_words = [word for word, freq in sorted_words[:100]]
                fingerprint_string = ''.join(sorted(top_words))
                fingerprint = hashlib.sha256(fingerprint_string.encode()).hexdigest()
                
                # Create simple similarity vector
                similarity_vector = [float(hash(word) % 1000) / 1000 for word in top_words[:50]]
                while len(similarity_vector) < 50:
                    similarity_vector.append(0.0)
                
                return fingerprint, similarity_vector
            
            # Use BERT embeddings
            # Truncate text for efficiency
            truncated_text = text_data[:512] if len(text_data) > 512 else text_data
            
            # Get embeddings
            embeddings = self.embedder(truncated_text)
            
            # Average embeddings across tokens
            if isinstance(embeddings, list) and len(embeddings) > 0:
                if isinstance(embeddings[0], list) and len(embeddings[0]) > 0:
                    # Handle nested structure
                    embedding_array = np.array(embeddings[0])
                    if embedding_array.ndim > 1:
                        similarity_vector = np.mean(embedding_array, axis=0).tolist()
                    else:
                        similarity_vector = embedding_array.tolist()
                else:
                    similarity_vector = embeddings[0] if embeddings[0] else [0.0] * 768
            else:
                similarity_vector = [0.0] * 768
            
            # Truncate to manageable size
            similarity_vector = similarity_vector[:100]
            while len(similarity_vector) < 100:
                similarity_vector.append(0.0)
            
            # Create fingerprint hash
            vector_string = ','.join(f'{v:.6f}' for v in similarity_vector)
            fingerprint = hashlib.sha256(vector_string.encode()).hexdigest()
            
            return fingerprint, similarity_vector
            
        except Exception as e:
            logger.error(f"Text semantic fingerprint generation error: {e}")
            raise
    
    async def generate_structural_fingerprint(self, text_data: str) -> Tuple[str, List[float]]:
        """Generate structural fingerprint based on text structure"""



        try:
            # Analyze text structure
            features = []
            
            # Basic statistics
            char_count = len(text_data)
            word_count = len(text_data.split())
            line_count = text_data.count('\n') + 1
            
            features.extend([char_count, word_count, line_count])
            
            # Character frequency
            char_freq = {}
            for char in text_data.lower():
                if char.isalpha():
                    char_freq[char] = char_freq.get(char, 0) + 1
            
            # Top 26 character frequencies (normalized)
            total_chars = sum(char_freq.values())
            if total_chars > 0:
                for i in range(26):
                    char = chr(ord('a') + i)
                    freq = char_freq.get(char, 0) / total_chars
                    features.append(freq)
            else:
                features.extend([0.0] * 26)
            
            # Punctuation analysis
            punctuation_chars = '.,!?;:'
            for punct in punctuation_chars:
                count = text_data.count(punct)
                features.append(count / char_count if char_count > 0 else 0.0)
            
            # Sentence structure
            sentences = text_data.count('.') + text_data.count('!') + text_data.count('?')
            avg_sentence_length = word_count / sentences if sentences > 0 else 0
            features.append(avg_sentence_length)
            
            # Create fingerprint
            feature_string = ','.join(f'{f:.6f}' for f in features)
            fingerprint = hashlib.sha256(feature_string.encode()).hexdigest()
            
            return fingerprint, features
            
        except Exception as e:
            logger.error(f"Text structural fingerprint generation error: {e}")
            raise
    
    async def generate_fingerprints(self, text_data: str, 
                                  types: List[FingerprintType]) -> Dict[str, Tuple[str, List[float]]]:
        """Generate multiple text fingerprints"""
        results = {}
        
        if FingerprintType.TEXT_SEMANTIC in types:
            try:
                fingerprint, vector = await self.generate_semantic_fingerprint(text_data)
                results[FingerprintType.TEXT_SEMANTIC.value] = (fingerprint, vector)
            except Exception as e:
                logger.error(f"Text semantic fingerprint generation failed: {e}")
        
        if FingerprintType.TEXT_STRUCTURAL in types:
            try:
                fingerprint, vector = await self.generate_structural_fingerprint(text_data)
                results[FingerprintType.TEXT_STRUCTURAL.value] = (fingerprint, vector)
            except Exception as e:
                logger.error(f"Text structural fingerprint generation failed: {e}")
        
        return results


class FingerprintingMiddleware:
    """Main fingerprinting middleware orchestrator"""
    
    def __init__(self):
        self.cache = CacheManager()
        self.fingerprint_engine = UniversalFingerprintEngine()
        
        # Initialize fingerprinters
        self.audio_fingerprinter = AudioFingerprinter()
        self.video_fingerprinter = VideoFingerprinter()
        self.image_fingerprinter = ImageFingerprinter()
        self.text_fingerprinter = TextFingerprinter()
        
        # Quality level configurations
        self.quality_configs = {
            "basic": {
                "audio": [FingerprintType.AUDIO_CHROMAPRINT],
                "video": [FingerprintType.VIDEO_PERCEPTUAL],
                "image": [FingerprintType.IMAGE_PHASH],
                "text": [FingerprintType.TEXT_STRUCTURAL]
            },
            "standard": {
                "audio": [FingerprintType.AUDIO_CHROMAPRINT, FingerprintType.AUDIO_SPECTRAL],
                "video": [FingerprintType.VIDEO_PERCEPTUAL, FingerprintType.VIDEO_MOTION],
                "image": [FingerprintType.IMAGE_PHASH, FingerprintType.IMAGE_DHASH],
                "text": [FingerprintType.TEXT_SEMANTIC, FingerprintType.TEXT_STRUCTURAL]
            },
            "premium": {
                "audio": [FingerprintType.AUDIO_CHROMAPRINT, FingerprintType.AUDIO_SPECTRAL],
                "video": [FingerprintType.VIDEO_PERCEPTUAL, FingerprintType.VIDEO_MOTION],
                "image": [FingerprintType.IMAGE_PHASH, FingerprintType.IMAGE_DHASH],
                "text": [FingerprintType.TEXT_SEMANTIC, FingerprintType.TEXT_STRUCTURAL]
            }
        }
    
    async def generate_fingerprints(self, request: FingerprintRequest) -> FingerprintResult:
        """Main fingerprint generation method"""
        start_time = time.time()
        
        try:
            # Determine fingerprint types to generate
            if request.fingerprint_types:
                fingerprint_types = request.fingerprint_types
            else:
                # Use quality level configuration
                quality_config = self.quality_configs.get(request.quality_level, 
                                                        self.quality_configs["standard"])
                fingerprint_types = quality_config.get(request.content_type, [])
            
            # Generate fingerprints based on content type
            all_fingerprints = {}
            all_vectors = {}
            all_confidence_scores = {}
            
            if request.content_type == "audio" and isinstance(request.content_data, bytes):
                results = await self.audio_fingerprinter.generate_fingerprints(
                    request.content_data, fingerprint_types
                )
                for fp_type, (fingerprint, vector) in results.items():
                    all_fingerprints[fp_type] = fingerprint
                    all_vectors[fp_type] = vector
                    all_confidence_scores[fp_type] = self.calculate_confidence_score(vector)
            
            elif request.content_type == "video" and isinstance(request.content_data, bytes):
                results = await self.video_fingerprinter.generate_fingerprints(
                    request.content_data, fingerprint_types
                )
                for fp_type, (fingerprint, vector) in results.items():
                    all_fingerprints[fp_type] = fingerprint
                    all_vectors[fp_type] = vector
                    all_confidence_scores[fp_type] = self.calculate_confidence_score(vector)
            
            elif request.content_type == "image" and isinstance(request.content_data, bytes):
                results = await self.image_fingerprinter.generate_fingerprints(
                    request.content_data, fingerprint_types
                )
                for fp_type, (fingerprint, vector) in results.items():
                    all_fingerprints[fp_type] = fingerprint
                    all_vectors[fp_type] = vector
                    all_confidence_scores[fp_type] = self.calculate_confidence_score(vector)
            
            elif request.content_type == "text" and isinstance(request.content_data, str):
                results = await self.text_fingerprinter.generate_fingerprints(
                    request.content_data, fingerprint_types
                )
                for fp_type, (fingerprint, vector) in results.items():
                    all_fingerprints[fp_type] = fingerprint
                    all_vectors[fp_type] = vector
                    all_confidence_scores[fp_type] = self.calculate_confidence_score(vector)
            
            # Enhanced metadata
            enhanced_metadata = await self.enhance_fingerprint_metadata(
                request, all_fingerprints, all_confidence_scores
            )
            
            # Cache fingerprints for future similarity searches
            await self.cache_fingerprints(request.content_id, all_fingerprints, all_vectors)
            
            processing_time = time.time() - start_time
            
            return FingerprintResult(
                content_id=request.content_id,
                fingerprints=all_fingerprints,
                similarity_vectors=all_vectors,
                confidence_scores=all_confidence_scores,
                metadata=enhanced_metadata,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Fingerprint generation failed for {request.content_id}: {e}")
            
            return FingerprintResult(
                content_id=request.content_id,
                fingerprints={},
                similarity_vectors={},
                confidence_scores={},
                metadata=request.metadata,
                processing_time=time.time() - start_time,
                error=str(e)
            )
    
    def calculate_confidence_score(self, similarity_vector: List[float]) -> float:
        """Calculate confidence score for fingerprint"""
        if not similarity_vector:
            return 0.0
        
        # Calculate vector properties that indicate good fingerprint quality
        vector_array = np.array(similarity_vector)
        
        # Non-zero variance indicates good feature diversity
        variance = np.var(vector_array)
        
        # Non-zero mean indicates presence of features
        mean_value = np.abs(np.mean(vector_array))
        
        # Normalize confidence score (0-1)
        confidence = min(1.0, (variance * 10 + mean_value) / 2)
        
        return float(confidence)
    
    async def enhance_fingerprint_metadata(self, request: FingerprintRequest,
                                         fingerprints: Dict[str, str],
                                         confidence_scores: Dict[str, float]) -> Dict[str, Any]:
        """Enhance metadata with fingerprinting information"""
        enhanced = request.metadata.copy()
        
        enhanced.update({
            "fingerprint_generation_timestamp": datetime.utcnow().isoformat(),
            "fingerprint_types_generated": list(fingerprints.keys()),
            "fingerprint_count": len(fingerprints),
            "average_confidence_score": np.mean(list(confidence_scores.values())) if confidence_scores else 0.0,
            "content_type": request.content_type,
            "quality_level": request.quality_level
        })
        
        return enhanced
    
    async def cache_fingerprints(self, content_id: str, fingerprints: Dict[str, str],
                               vectors: Dict[str, List[float]]):
        """Cache fingerprints for similarity searches"""
        cache_data = {
            "content_id": content_id,
            "fingerprints": fingerprints,
            "vectors": vectors,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        cache_key = f"fingerprints:{content_id}"
        await self.cache.set(cache_key, json.dumps(cache_data), expire=86400 * 30)  # 30 days
    
    async def find_similar_content(self, fingerprints: Dict[str, str],
                                 similarity_vectors: Dict[str, List[float]],
                                 threshold: float = 0.8) -> List[Dict[str, Any]]:
        """Find similar content based on fingerprints"""
        similar_content = []
        
        try:
            # This would typically use a vector database like FAISS or Pinecone
            # For now, implement a simple similarity search
            
            # Get all cached fingerprints
            cache_pattern = "fingerprints:*"
            cached_keys = await self.cache.keys(cache_pattern)
            
            for cache_key in cached_keys:
                cached_data = await self.cache.get(cache_key)
                if cached_data:
                    cached_fingerprints = json.loads(cached_data)
                    
                    # Calculate similarity
                    similarity_score = await self.calculate_similarity(
                        similarity_vectors, cached_fingerprints.get("vectors", {})
                    )
                    
                    if similarity_score >= threshold:
                        similar_content.append({
                            "content_id": cached_fingerprints["content_id"],
                            "similarity_score": similarity_score,
                            "fingerprints": cached_fingerprints["fingerprints"]
                        })
            
            # Sort by similarity score
            similar_content.sort(key=lambda x: x["similarity_score"], reverse=True)
            
        except Exception as e:
            logger.error(f"Similar content search error: {e}")
        
        return similar_content
    
    async def calculate_similarity(self, vectors1: Dict[str, List[float]], 
                                 vectors2: Dict[str, List[float]]) -> float:
        """Calculate similarity between two sets of vectors"""
        if not vectors1 or not vectors2:
            return 0.0
        
        similarities = []
        
        # Calculate cosine similarity for each matching vector type
        for vector_type, vector1 in vectors1.items():
            if vector_type in vectors2:
                vector2 = vectors2[vector_type]
                
                # Ensure same length
                min_len = min(len(vector1), len(vector2))
                v1 = np.array(vector1[:min_len])
                v2 = np.array(vector2[:min_len])
                
                # Calculate cosine similarity
                if np.linalg.norm(v1) > 0 and np.linalg.norm(v2) > 0:
                    similarity = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
                    similarities.append(float(similarity))
        
        # Return average similarity
        return np.mean(similarities) if similarities else 0.0


# Factory function for dependency injection
def get_fingerprinting_middleware() -> FingerprintingMiddleware:
    """Get fingerprinting middleware instance"""



    return FingerprintingMiddleware()


# Utility functions
async def generate_content_fingerprint(content_data: Union[str, bytes], content_type: str,
                                     content_id: str = None, 
                                     quality_level: str = "standard") -> FingerprintResult:
    """Convenience function for content fingerprinting"""
    if content_id is None:
        content_id = hashlib.md5(str(content_data).encode()).hexdigest()
    
    middleware = get_fingerprinting_middleware()
    request = FingerprintRequest(
        content_id=content_id,
        content_type=content_type,
        content_data=content_data,
        fingerprint_types=[],  # Use quality level default
        quality_level=quality_level
    )
    
    return await middleware.generate_fingerprints(request)


async def find_duplicate_content(fingerprints: Dict[str, str],
                               similarity_vectors: Dict[str, List[float]],
                               threshold: float = 0.9) -> List[Dict[str, Any]]:
    """Convenience function for duplicate content detection"""
    middleware = get_fingerprinting_middleware()
    return await middleware.find_similar_content(fingerprints, similarity_vectors, threshold)
