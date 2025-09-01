"""Fingerprint Utilities Module
============================

Professional content fingerprinting utilities for web crawlers.
Implements advanced fingerprinting algorithms for content protection and similarity detection.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

Project Team Specialties:
- Lead Dev IA: Advanced AI integration and machine learning
- Backend Senior: Scalable architecture and microservices  
- ML Engineer: Content analysis and recommendation systems
- DBA: High-performance database optimization
- Security Expert: Enterprise-grade security and encryption
- Microservices Architect: Distributed systems design
- Audio Engineer: Advanced audio processing and analysis
- DevOps Engineer: CI/CD and infrastructure automation
- IA Prompt Engineer: Intelligent prompt optimization
"""

import hashlib
import hmac
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from datetime import datetime
import json
import base64
import asyncio
from urllib.parse import urlparse, urljoin
import re

# Image processing
try:
    from PIL import Image, ImageFilter, ImageEnhance
    import cv2
    import numpy as np
    VISION_AVAILABLE = True
except ImportError:
    VISION_AVAILABLE = False

# Audio processing
try:
    import librosa
    import soundfile as sf
    from scipy.signal import spectrogram
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

# Text processing
import nltk
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
import spacy

logger = logging.getLogger(__name__)

@dataclass
class ContentFingerprint:
    """
Structure for content fingerprints."""
    content_id: str
    content_type: str  # text, image, audio, video, html
    primary_hash: str
    secondary_hashes: Dict[str, str]
    feature_vector: Optional[List[float]]
    metadata: Dict[str, Any]
    extraction_method: str
    quality_score: float
    timestamp: datetime
    
    def __post_init__(self):
        if self.secondary_hashes is None:
            self.secondary_hashes = {}
        if self.metadata is None:
            self.metadata = {}

@dataclass
class SimilarityResult:
    """
Structure for similarity comparison results."""
    content_id_1: str
    content_id_2: str
    similarity_score: float
    similarity_type: str
    confidence: float
    matched_features: List[str]
    metadata: Dict[str, Any]
    
    def __post_init__(self):
        if self.matched_features is None:
            self.matched_features = []
        if self.metadata is None:
            self.metadata = {}

class ContentFingerprintGenerator:
    """
    Advanced content fingerprinting generator.
    
    Supports multiple content types with various fingerprinting strategies:
    - Text: Semantic embeddings, n-grams, linguistic features
    - Images: Perceptual hashing, feature descriptors, color histograms
    - Audio: Spectral fingerprints, MFCC features, chromagrams
    - HTML: DOM structure, content patterns, meta information
    """
    
    def __init__(self):
        """
Initialize fingerprint generator."""
        self.text_model = None
        self.spacy_nlp = None
        self.tfidf_vectorizer = None
        
        # Initialize models
        self._init_text_models()
        
    def _init_text_models(self) -> None:
        """
Initialize text processing models."""
        try:
            # Initialize sentence transformer
            self.text_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Initialize spacy
            try:
                self.spacy_nlp = spacy.load('en_core_web_sm')
            except IOError:
                logger.warning("Spacy model not found, some features will be limited")
                self.spacy_nlp = None
            
            # Initialize TF-IDF
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 3)
            )
            
            logger.info("Text models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize text models: {e}")
    
    async def generate_fingerprint(
        self,
        content: Union[str, bytes, np.ndarray],
        content_type: str,
        content_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ContentFingerprint:
        """
        Generate comprehensive fingerprint for content.
        
        Args:
            content: Content data (text, bytes, or array)
            content_type: Type of content (text, image, audio, video, html)
            content_id: Unique identifier for content
            metadata: Additional metadata
            
        Returns:
            ContentFingerprint object
        """
        metadata = metadata or {}
        
        try:
            if content_type == 'text':
                return await self._fingerprint_text(content, content_id, metadata)
            elif content_type == 'html':
                return await self._fingerprint_html(content, content_id, metadata)
            elif content_type == 'image':
                return await self._fingerprint_image(content, content_id, metadata)
            elif content_type == 'audio':
                return await self._fingerprint_audio(content, content_id, metadata)
            elif content_type == 'video':
                return await self._fingerprint_video(content, content_id, metadata)
            else:
                return await self._fingerprint_generic(content, content_id, metadata)
                
        except Exception as e:
            logger.error(f"Fingerprinting failed for {content_id}: {e}")
            # Return basic fingerprint on error
            return ContentFingerprint(
                content_id=content_id,
                content_type=content_type,
                primary_hash=self._basic_hash(str(content)),
                secondary_hashes={},
                feature_vector=None,
                metadata=metadata,
                extraction_method='fallback',
                quality_score=0.1,
                timestamp=datetime.now()
            )
    
    async def _fingerprint_text(
        self,
        text: str,
        content_id: str,
        metadata: Dict[str, Any]
    ) -> ContentFingerprint:
        """Generate fingerprint for text content."""
        # Primary hash (content-based)
        normalized_text = self._normalize_text(text)
        primary_hash = self._semantic_hash(normalized_text)
        
        # Secondary hashes
        secondary_hashes = {
            'md5': hashlib.md5(text.encode()).hexdigest(),
            'sha256': hashlib.sha256(text.encode()).hexdigest(),
            'fuzzy': self._fuzzy_hash(normalized_text),
            'ngram': self._ngram_hash(normalized_text),
            'linguistic': self._linguistic_hash(text)
        }
        
        # Feature vector (semantic embedding)
        feature_vector = None
        extraction_method = 'basic'
        quality_score = 0.5
        
        if self.text_model:
            try:
                embedding = self.text_model.encode(normalized_text)
                feature_vector = embedding.tolist()
                extraction_method = 'semantic_embedding'
                quality_score = 0.9
            except Exception as e:
                logger.warning(f"Semantic embedding failed: {e}")
        
        # Linguistic features
        if self.spacy_nlp:
            try:
                doc = self.spacy_nlp(text[:1000000])  # Limit for performance
                metadata.update({
                    'entity_count': len(doc.ents),
                    'sentence_count': len(list(doc.sents)),
                    'token_count': len(doc),
                    'pos_distribution': self._get_pos_distribution(doc)
                })
                quality_score = min(quality_score + 0.1, 1.0)
            except Exception as e:
                logger.warning(f"Linguistic analysis failed: {e}")
        
        return ContentFingerprint(
            content_id=content_id,
            content_type='text',
            primary_hash=primary_hash,
            secondary_hashes=secondary_hashes,
            feature_vector=feature_vector,
            metadata=metadata,
            extraction_method=extraction_method,
            quality_score=quality_score,
            timestamp=datetime.now()
        )
    
    async def _fingerprint_html(
        self,
        html: str,
        content_id: str,
        metadata: Dict[str, Any]
    ) -> ContentFingerprint:
        """Generate fingerprint for HTML content."""
        from bs4 import BeautifulSoup
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract text content
            text_content = soup.get_text(strip=True)
            
            # Primary hash (structure + content)
            structure_hash = self._html_structure_hash(soup)
            content_hash = self._semantic_hash(text_content)
            primary_hash = hashlib.sha256(
                f"{structure_hash}:{content_hash}".encode()
            ).hexdigest()
            
            # Secondary hashes
            secondary_hashes = {
                'raw_html': hashlib.sha256(html.encode()).hexdigest(),
                'structure': structure_hash,
                'content': content_hash,
                'metadata': self._html_metadata_hash(soup),
                'links': self._html_links_hash(soup)
            }
            
            # HTML-specific metadata
            metadata.update({
                'title': soup.title.string if soup.title else None,
                'meta_tags': len(soup.find_all('meta')),
                'links_count': len(soup.find_all('a')),
                'images_count': len(soup.find_all('img')),
                'scripts_count': len(soup.find_all('script')),
                'text_length': len(text_content)
            })
            
            # Feature vector from text content
            feature_vector = None
            if self.text_model and text_content:
                try:
                    embedding = self.text_model.encode(text_content[:10000])
                    feature_vector = embedding.tolist()
                except Exception as e:
                    logger.warning(f"HTML text embedding failed: {e}")
            
            return ContentFingerprint(
                content_id=content_id,
                content_type='html',
                primary_hash=primary_hash,
                secondary_hashes=secondary_hashes,
                feature_vector=feature_vector,
                metadata=metadata,
                extraction_method='html_structure_content',
                quality_score=0.8,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"HTML fingerprinting failed: {e}")
            return await self._fingerprint_generic(html, content_id, metadata)
    
    async def _fingerprint_image(
        self,
        image_data: Union[bytes, np.ndarray, str],
        content_id: str,
        metadata: Dict[str, Any]
    ) -> ContentFingerprint:
        """Generate fingerprint for image content."""
        if not VISION_AVAILABLE:
            logger.warning("Vision libraries not available, using basic fingerprint")
            return await self._fingerprint_generic(image_data, content_id, metadata)
        
        try:
            # Convert to PIL Image
            if isinstance(image_data, str):
                # Assume it's a file path
                image = Image.open(image_data)
            elif isinstance(image_data, bytes):
                # Assume it's image bytes
                from io import BytesIO
                image = Image.open(BytesIO(image_data))
            elif isinstance(image_data, np.ndarray):
                image = Image.fromarray(image_data)
            else:
                raise ValueError(f"Unsupported image data type: {type(image_data)}")
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Primary hash (perceptual hash)
            primary_hash = self._perceptual_hash(image)
            
            # Secondary hashes
            secondary_hashes = {
                'dhash': self._difference_hash(image),
                'ahash': self._average_hash(image),
                'whash': self._wavelet_hash(image),
                'color_hist': self._color_histogram_hash(image),
                'texture': self._texture_hash(image)
            }
            
            # Feature vector (color and texture features)
            feature_vector = self._extract_image_features(image)
            
            # Image metadata
            metadata.update({
                'width': image.width,
                'height': image.height,
                'mode': image.mode,
                'format': getattr(image, 'format', 'unknown'),
                'size_bytes': len(image_data) if isinstance(image_data, bytes) else 0
            })
            
            return ContentFingerprint(
                content_id=content_id,
                content_type='image',
                primary_hash=primary_hash,
                secondary_hashes=secondary_hashes,
                feature_vector=feature_vector,
                metadata=metadata,
                extraction_method='perceptual_features',
                quality_score=0.9,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Image fingerprinting failed: {e}")
            return await self._fingerprint_generic(image_data, content_id, metadata)
    
    async def _fingerprint_audio(
        self,
        audio_data: Union[bytes, np.ndarray, str],
        content_id: str,
        metadata: Dict[str, Any]
    ) -> ContentFingerprint:
        """Generate fingerprint for audio content."""
        if not AUDIO_AVAILABLE:
            logger.warning("Audio libraries not available, using basic fingerprint")
            return await self._fingerprint_generic(audio_data, content_id, metadata)
        
        try:
            # Load audio
            if isinstance(audio_data, str):
                # File path
                y, sr = librosa.load(audio_data)
            elif isinstance(audio_data, bytes):
                # Audio bytes - save temporarily and load
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.wav') as tmp:
                    tmp.write(audio_data)
                    tmp.flush()
                    y, sr = librosa.load(tmp.name)
            elif isinstance(audio_data, np.ndarray):
                y = audio_data
                sr = metadata.get('sample_rate', 22050)
            else:
                raise ValueError(f"Unsupported audio data type: {type(audio_data)}")
            
            # Primary hash (spectral centroid + tempo)
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            primary_features = f"{spectral_centroid.mean():.4f}:{tempo:.2f}"
            primary_hash = hashlib.sha256(primary_features.encode()).hexdigest()
            
            # Secondary hashes
            secondary_hashes = {
                'mfcc': self._mfcc_hash(y, sr),
                'chroma': self._chroma_hash(y, sr),
                'spectral': self._spectral_hash(y, sr),
                'rhythm': self._rhythm_hash(y, sr),
                'raw_data': hashlib.sha256(y.tobytes()).hexdigest()
            }
            
            # Feature vector (comprehensive audio features)
            feature_vector = self._extract_audio_features(y, sr)
            
            # Audio metadata
            metadata.update({
                'duration': len(y) / sr,
                'sample_rate': sr,
                'channels': 1 if y.ndim == 1 else y.shape[0],
                'samples': len(y),
                'tempo': float(tempo),
                'spectral_centroid_mean': float(spectral_centroid.mean())
            })
            
            return ContentFingerprint(
                content_id=content_id,
                content_type='audio',
                primary_hash=primary_hash,
                secondary_hashes=secondary_hashes,
                feature_vector=feature_vector,
                metadata=metadata,
                extraction_method='spectral_features',
                quality_score=0.9,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Audio fingerprinting failed: {e}")
            return await self._fingerprint_generic(audio_data, content_id, metadata)
    
    async def _fingerprint_video(
        self,
        video_data: Union[bytes, str],
        content_id: str,
        metadata: Dict[str, Any]
    ) -> ContentFingerprint:
        """Generate fingerprint for video content."""
        if not VISION_AVAILABLE:
            logger.warning("Vision libraries not available, using basic fingerprint")
            return await self._fingerprint_generic(video_data, content_id, metadata)
        
        try:
            # For video, we'll extract key frames and audio
            if isinstance(video_data, str):
                # File path
                cap = cv2.VideoCapture(video_data)
            else:
                # For bytes, would need to save temporarily
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.mp4') as tmp:
                    tmp.write(video_data)
                    tmp.flush()
                    cap = cv2.VideoCapture(tmp.name)
            
            # Extract key frames
            frames = []
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            # Sample frames at regular intervals
            sample_interval = max(1, frame_count // 10)  # Sample 10 frames max
            
            for i in range(0, frame_count, sample_interval):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                if ret:
                    frames.append(frame)
            
            cap.release()
            
            # Generate fingerprints for sampled frames
            frame_hashes = []
            for i, frame in enumerate(frames):
                frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                frame_hash = self._perceptual_hash(frame_pil)
                frame_hashes.append(frame_hash)
            
            # Primary hash (combination of frame hashes)
            combined_frames = ':'.join(frame_hashes[:5])  # Use first 5 frames
            primary_hash = hashlib.sha256(combined_frames.encode()).hexdigest()
            
            # Secondary hashes
            secondary_hashes = {
                'frame_sequence': hashlib.sha256(':'.join(frame_hashes).encode()).hexdigest(),
                'first_frame': frame_hashes[0] if frame_hashes else '',
                'last_frame': frame_hashes[-1] if frame_hashes else '',
                'frame_variance': self._calculate_frame_variance(frames)
            }
            
            # Feature vector (visual features from frames)
            feature_vector = self._extract_video_features(frames)
            
            # Video metadata
            metadata.update({
                'frame_count': frame_count,
                'fps': fps,
                'duration': frame_count / fps if fps > 0 else 0,
                'sampled_frames': len(frames),
                'width': frames[0].shape[1] if frames else 0,
                'height': frames[0].shape[0] if frames else 0
            })
            
            return ContentFingerprint(
                content_id=content_id,
                content_type='video',
                primary_hash=primary_hash,
                secondary_hashes=secondary_hashes,
                feature_vector=feature_vector,
                metadata=metadata,
                extraction_method='frame_sampling',
                quality_score=0.8,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Video fingerprinting failed: {e}")
            return await self._fingerprint_generic(video_data, content_id, metadata)
    
    async def _fingerprint_generic(
        self,
        content: Any,
        content_id: str,
        metadata: Dict[str, Any]
    ) -> ContentFingerprint:
        """Generate basic fingerprint for unknown content types."""
        content_str = str(content)
        
        primary_hash = hashlib.sha256(content_str.encode()).hexdigest()
        
        secondary_hashes = {
            'md5': hashlib.md5(content_str.encode()).hexdigest(),
            'sha1': hashlib.sha1(content_str.encode()).hexdigest(),
            'length': str(len(content_str))
        }
        
        return ContentFingerprint(
            content_id=content_id,
            content_type='generic',
            primary_hash=primary_hash,
            secondary_hashes=secondary_hashes,
            feature_vector=None,
            metadata=metadata,
            extraction_method='basic_hash',
            quality_score=0.3,
            timestamp=datetime.now()
        )
    
    # Helper methods for hashing
    def _basic_hash(self, content: str) -> str:
        """
Generate basic SHA-256 hash."""
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _normalize_text(self, text: str) -> str:
        """
Normalize text for consistent hashing."""
        # Remove extra whitespace, lowercase, basic cleanup
        normalized = re.sub(r'\s+', ' ', text.lower().strip())
        # Remove punctuation for fuzzy matching
        normalized = re.sub(r'[^\w\s]', '', normalized)
        return normalized
    
    def _semantic_hash(self, text: str) -> str:
        """
Generate semantic hash based on meaning."""
        # Use TF-IDF or other semantic features
        words = text.split()
        # Create a hash based on significant words
        significant_words = sorted([w for w in words if len(w) > 3])[:50]
        semantic_content = ' '.join(significant_words)
        return hashlib.sha256(semantic_content.encode()).hexdigest()
    
    def _fuzzy_hash(self, text: str) -> str:
        """
Generate fuzzy hash for approximate matching."""
        # Simplified fuzzy hash - in production use ssdeep or similar
        words = text.split()
        # Group similar length words
        short_words = [w for w in words if len(w) <= 4]
        long_words = [w for w in words if len(w) > 4]
        
        fuzzy_content = f"{len(short_words)}:{len(long_words)}:{len(text)}"
        return hashlib.md5(fuzzy_content.encode()).hexdigest()
    
    def _ngram_hash(self, text: str, n: int = 3) -> str:
        """Generate n-gram based hash."""
        # Create character n-grams
        ngrams = [text[i:i+n] for i in range(len(text)-n+1)]
        # Use most common n-grams
        from collections import Counter
        common_ngrams = Counter(ngrams).most_common(20)
        ngram_content = ''.join([ng[0] for ng in common_ngrams])
        return hashlib.md5(ngram_content.encode()).hexdigest()
    
    def _linguistic_hash(self, text: str) -> str:
        """
Generate hash based on linguistic features."""
        # Basic linguistic features
        words = text.split()
        avg_word_length = sum(len(w) for w in words) / len(words) if words else 0
        sentence_count = text.count('.') + text.count('!') + text.count('?')
        
        features = f"{avg_word_length:.2f}:{sentence_count}:{len(words)}"
        return hashlib.md5(features.encode()).hexdigest()
    
    def _get_pos_distribution(self, doc) -> Dict[str, int]:
        """Get part-of-speech distribution."""
        pos_counts = {}
        for token in doc:
            pos = token.pos_
            pos_counts[pos] = pos_counts.get(pos, 0) + 1
        return pos_counts
    
    def _html_structure_hash(self, soup) -> str:
        """
Generate hash based on HTML structure."""
        # Extract tag structure
        tags = [tag.name for tag in soup.find_all()]
        structure = ':'.join(tags[:50])  # Limit for performance
        return hashlib.md5(structure.encode()).hexdigest()
    
    def _html_metadata_hash(self, soup) -> str:
        """
Generate hash based on HTML metadata."""
        meta_tags = soup.find_all('meta')
        meta_content = []
        for meta in meta_tags:
            name = meta.get('name', '')
            content = meta.get('content', '')
            if name and content:
                meta_content.append(f"{name}:{content}")
        
        meta_string = '|'.join(sorted(meta_content))
        return hashlib.md5(meta_string.encode()).hexdigest()
    
    def _html_links_hash(self, soup) -> str:
        """Generate hash based on HTML links."""
        links = [a.get('href', '') for a in soup.find_all('a', href=True)]
        # Normalize links (remove parameters, etc.)
        normalized_links = []
        for link in links[:20]:  # Limit for performance
            parsed = urlparse(link)
            normalized = f"{parsed.netloc}{parsed.path}"
            normalized_links.append(normalized)
        
        links_string = '|'.join(sorted(set(normalized_links)))
        return hashlib.md5(links_string.encode()).hexdigest()
    
    # Image processing methods
    def _perceptual_hash(self, image: Image.Image, hash_size: int = 8) -> str:
        """Generate perceptual hash for image."""
        # Resize and convert to grayscale
        image = image.resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
        image = image.convert('L')
        
        # Calculate horizontal gradient
        pixels = list(image.getdata())
        
        # Calculate differences
        hash_bits = []
        for row in range(hash_size):
            for col in range(hash_size):
                pixel = pixels[row * (hash_size + 1) + col]
                pixel_right = pixels[row * (hash_size + 1) + col + 1]
                hash_bits.append('1' if pixel < pixel_right else '0')
        
        # Convert to hex
        hash_string = ''.join(hash_bits)
        hash_int = int(hash_string, 2)
        return f"{hash_int:016x}"
    
    def _difference_hash(self, image: Image.Image, hash_size: int = 8) -> str:
        """Generate difference hash for image."""
        image = image.resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
        image = image.convert('L')
        
        pixels = list(image.getdata())
        hash_bits = []
        
        for row in range(hash_size):
            for col in range(hash_size):
                pixel = pixels[row * (hash_size + 1) + col]
                pixel_right = pixels[row * (hash_size + 1) + col + 1]
                hash_bits.append(pixel < pixel_right)
        
        # Convert to hex
        hash_int = sum(2**i for i, bit in enumerate(hash_bits) if bit)
        return f"{hash_int:016x}"
    
    def _average_hash(self, image: Image.Image, hash_size: int = 8) -> str:
        """Generate average hash for image."""
        image = image.resize((hash_size, hash_size), Image.Resampling.LANCZOS)
        image = image.convert('L')
        
        pixels = list(image.getdata())
        avg = sum(pixels) / len(pixels)
        
        hash_bits = [pixel > avg for pixel in pixels]
        hash_int = sum(2**i for i, bit in enumerate(hash_bits) if bit)
        return f"{hash_int:016x}"
    
    def _wavelet_hash(self, image: Image.Image, hash_size: int = 8) -> str:
        """Generate wavelet hash for image."""
        try:
            import pywt
            
            image = image.resize((hash_size * 2, hash_size * 2), Image.Resampling.LANCZOS)
            image = image.convert('L')
            
            # Convert to numpy array
            pixels = np.array(image)
            
            # Apply wavelet transform
            coeffs = pywt.dwt2(pixels, 'haar')
            cA, (cH, cV, cD) = coeffs
            
            # Use low-frequency component
            cA = cA[:hash_size, :hash_size]
            
            # Calculate hash
            avg = cA.mean()
            hash_bits = cA > avg
            
            hash_int = 0
            for i, row in enumerate(hash_bits):
                for j, bit in enumerate(row):
                    if bit:
                        hash_int += 2**(i * hash_size + j)
            
            return f"{hash_int:016x}"
            
        except ImportError:
            # Fallback to average hash
            return self._average_hash(image, hash_size)
    
    def _color_histogram_hash(self, image: Image.Image) -> str:
        """Generate hash based on color histogram."""
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Calculate histogram
        hist_r = image.histogram()[0:256]
        hist_g = image.histogram()[256:512]
        hist_b = image.histogram()[512:768]
        
        # Normalize and quantize
        total_pixels = image.width * image.height
        hist_features = []
        
        for hist in [hist_r, hist_g, hist_b]:
            # Divide into bins
            bin_size = 256 // 8  # 8 bins per channel
            bins = []
            for i in range(0, 256, bin_size):
                bin_sum = sum(hist[i:i+bin_size])
                bins.append(bin_sum / total_pixels)
            hist_features.extend(bins)
        
        # Convert to string
        feature_string = ':'.join([f"{f:.3f}" for f in hist_features])
        return hashlib.md5(feature_string.encode()).hexdigest()
    
    def _texture_hash(self, image: Image.Image) -> str:
        """Generate hash based on texture features."""
        # Convert to grayscale
        gray = image.convert('L')
        gray = gray.resize((64, 64), Image.Resampling.LANCZOS)
        
        # Apply edge detection
        edges = gray.filter(ImageFilter.FIND_EDGES)
        
        # Calculate texture measures
        pixels = np.array(edges)
        
        # Local binary pattern approximation
        rows, cols = pixels.shape
        lbp_features = []
        
        for i in range(1, rows-1):
            for j in range(1, cols-1):
                center = pixels[i, j]
                pattern = 0
                
                # Check 8 neighbors
                neighbors = [
                    pixels[i-1, j-1], pixels[i-1, j], pixels[i-1, j+1],
                    pixels[i, j+1], pixels[i+1, j+1], pixels[i+1, j],
                    pixels[i+1, j-1], pixels[i, j-1]
                ]
                
                for k, neighbor in enumerate(neighbors):
                    if neighbor >= center:
                        pattern += 2**k
                
                lbp_features.append(pattern)
        
        # Create histogram of patterns
        hist, _ = np.histogram(lbp_features, bins=32)
        hist_normalized = hist / hist.sum()
        
        feature_string = ':'.join([f"{f:.3f}" for f in hist_normalized])
        return hashlib.md5(feature_string.encode()).hexdigest()
    
    def _extract_image_features(self, image: Image.Image) -> List[float]:
        """Extract comprehensive image features."""
        features = []
        
        # Color features
        if image.mode == 'RGB':
            # Average color
            r, g, b = image.resize((1, 1)).getpixel((0, 0))
            features.extend([r/255.0, g/255.0, b/255.0])
            
            # Color variance
            pixels = np.array(image)
            features.extend([
                np.var(pixels[:, :, 0]) / 255.0,
                np.var(pixels[:, :, 1]) / 255.0,
                np.var(pixels[:, :, 2]) / 255.0
            ])
        
        # Brightness and contrast
        gray = image.convert('L')
        gray_array = np.array(gray)
        features.append(np.mean(gray_array) / 255.0)  # Brightness
        features.append(np.std(gray_array) / 255.0)   # Contrast
        
        # Edge density
        edges = gray.filter(ImageFilter.FIND_EDGES)
        edge_array = np.array(edges)
        edge_density = np.count_nonzero(edge_array) / edge_array.size
        features.append(edge_density)
        
        # Aspect ratio
        features.append(image.width / image.height)
        
        return features
    
    # Audio processing methods
    def _mfcc_hash(self, y: np.ndarray, sr: int) -> str:
        """
Generate hash based on MFCC features."""
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        mfcc_mean = np.mean(mfcc, axis=1)
        feature_string = ':'.join([f"{f:.4f}" for f in mfcc_mean])
        return hashlib.md5(feature_string.encode()).hexdigest()
    
    def _chroma_hash(self, y: np.ndarray, sr: int) -> str:
        """Generate hash based on chroma features."""
        chroma = librosa.feature.chroma(y=y, sr=sr)
        chroma_mean = np.mean(chroma, axis=1)
        feature_string = ':'.join([f"{f:.4f}" for f in chroma_mean])
        return hashlib.md5(feature_string.encode()).hexdigest()
    
    def _spectral_hash(self, y: np.ndarray, sr: int) -> str:
        """Generate hash based on spectral features."""
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
        
        features = [
            np.mean(spectral_centroids),
            np.mean(spectral_rolloff),
            np.mean(spectral_bandwidth)
        ]
        
        feature_string = ':'.join([f"{f:.4f}" for f in features])
        return hashlib.md5(feature_string.encode()).hexdigest()
    
    def _rhythm_hash(self, y: np.ndarray, sr: int) -> str:
        """Generate hash based on rhythm features."""
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        
        # Beat intervals
        if len(beats) > 1:
            beat_intervals = np.diff(beats) / sr
            rhythm_features = [
                float(tempo),
                np.mean(beat_intervals),
                np.std(beat_intervals)
            ]
        else:
            rhythm_features = [float(tempo), 0.0, 0.0]
        
        feature_string = ':'.join([f"{f:.4f}" for f in rhythm_features])
        return hashlib.md5(feature_string.encode()).hexdigest()
    
    def _extract_audio_features(self, y: np.ndarray, sr: int) -> List[float]:
        """Extract comprehensive audio features."""
        features = []
        
        # Temporal features
        features.append(len(y) / sr)  # Duration
        features.append(np.mean(np.abs(y)))  # RMS energy
        features.append(np.std(y))  # Standard deviation
        
        # Spectral features
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)
        features.append(np.mean(spectral_centroids))
        features.append(np.std(spectral_centroids))
        
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
        features.append(np.mean(spectral_rolloff))
        
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
        features.append(np.mean(spectral_bandwidth))
        
        # MFCC features (first 5 coefficients)
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=5)
        features.extend(np.mean(mfcc, axis=1).tolist())
        
        # Chroma features
        chroma = librosa.feature.chroma(y=y, sr=sr)
        features.extend(np.mean(chroma, axis=1).tolist())
        
        # Tempo
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        features.append(float(tempo))
        
        return features
    
    # Video processing methods
    def _calculate_frame_variance(self, frames: List[np.ndarray]) -> str:
        """
Calculate variance between frames."""
        if len(frames) < 2:
            return "0"
        
        variances = []
        for i in range(len(frames) - 1):
            frame1_gray = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
            frame2_gray = cv2.cvtColor(frames[i + 1], cv2.COLOR_BGR2GRAY)
            
            # Calculate MSE between frames
            mse = np.mean((frame1_gray - frame2_gray) ** 2)
            variances.append(mse)
        
        avg_variance = np.mean(variances)
        return hashlib.md5(f"{avg_variance:.4f}".encode()).hexdigest()
    
    def _extract_video_features(self, frames: List[np.ndarray]) -> List[float]:
        """Extract video features from frames."""
        if not frames:
            return []
        
        features = []
        
        # Average brightness across frames
        brightness_values = []
        for frame in frames:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            brightness_values.append(np.mean(gray))
        
        features.append(np.mean(brightness_values) / 255.0)
        features.append(np.std(brightness_values) / 255.0)
        
        # Motion between frames
        if len(frames) > 1:
            motion_values = []
            for i in range(len(frames) - 1):
                gray1 = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
                gray2 = cv2.cvtColor(frames[i + 1], cv2.COLOR_BGR2GRAY)
                diff = cv2.absdiff(gray1, gray2)
                motion_values.append(np.mean(diff))
            
            features.append(np.mean(motion_values) / 255.0)
            features.append(np.std(motion_values) / 255.0)
        else:
            features.extend([0.0, 0.0])
        
        # Color features from first frame
        if frames:
            first_frame = frames[0]
            # Average color
            mean_color = np.mean(first_frame, axis=(0, 1))
            features.extend((mean_color / 255.0).tolist())
            
            # Color variance
            color_var = np.var(first_frame, axis=(0, 1))
            features.extend((color_var / 255.0).tolist())
        
        return features

class SimilarityAnalyzer:
    """
    Advanced similarity analysis for content fingerprints.
    
    Supports multiple similarity metrics and algorithms for different content types.
    """
    
    def __init__(self):
        """
Initialize similarity analyzer."""
        pass
    
    async def calculate_similarity(
        self,
        fingerprint1: ContentFingerprint,
        fingerprint2: ContentFingerprint,
        similarity_type: str = "auto"
    ) -> SimilarityResult:
        """
        Calculate similarity between two content fingerprints.
        
        Args:
            fingerprint1: First content fingerprint
            fingerprint2: Second content fingerprint
            similarity_type: Type of similarity calculation
            
        Returns:
            SimilarityResult object
        """
        if fingerprint1.content_type != fingerprint2.content_type:
            # Different content types - very low similarity
            return SimilarityResult(
                content_id_1=fingerprint1.content_id,
                content_id_2=fingerprint2.content_id,
                similarity_score=0.0,
                similarity_type="type_mismatch",
                confidence=1.0,
                matched_features=[],
                metadata={"reason": "Different content types"}
            )
        
        content_type = fingerprint1.content_type
        
        if similarity_type == "auto":
            similarity_type = self._get_best_similarity_method(content_type)
        
        try:
            if content_type == "text":
                return await self._calculate_text_similarity(
                    fingerprint1, fingerprint2, similarity_type
                )
            elif content_type == "image":
                return await self._calculate_image_similarity(
                    fingerprint1, fingerprint2, similarity_type
                )
            elif content_type == "audio":
                return await self._calculate_audio_similarity(
                    fingerprint1, fingerprint2, similarity_type
                )
            elif content_type == "video":
                return await self._calculate_video_similarity(
                    fingerprint1, fingerprint2, similarity_type
                )
            else:
                return await self._calculate_generic_similarity(
                    fingerprint1, fingerprint2, similarity_type
                )
                
        except Exception as e:
            logger.error(f"Similarity calculation failed: {e}")
            return SimilarityResult(
                content_id_1=fingerprint1.content_id,
                content_id_2=fingerprint2.content_id,
                similarity_score=0.0,
                similarity_type="error",
                confidence=0.0,
                matched_features=[],
                metadata={"error": str(e)}
            )
    
    def _get_best_similarity_method(self, content_type: str) -> str:
        """Get best similarity method for content type."""
        method_map = {
            "text": "semantic",
            "image": "perceptual",
            "audio": "spectral",
            "video": "frame_based",
            "html": "semantic",
            "generic": "hash"
        }
        return method_map.get(content_type, "hash")
    
    async def _calculate_text_similarity(
        self,
        fp1: ContentFingerprint,
        fp2: ContentFingerprint,
        method: str
    ) -> SimilarityResult:
        """Calculate text similarity."""
        matched_features = []
        similarity_score = 0.0
        confidence = 0.5
        
        if method == "semantic" and fp1.feature_vector and fp2.feature_vector:
            # Cosine similarity of embeddings
            vec1 = np.array(fp1.feature_vector)
            vec2 = np.array(fp2.feature_vector)
            
            cosine_sim = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
            similarity_score = max(0.0, cosine_sim)
            confidence = 0.9
            matched_features.append("semantic_embedding")
            
        elif method == "hash":
            # Hash-based similarity
            if fp1.primary_hash == fp2.primary_hash:
                similarity_score = 1.0
                confidence = 1.0
                matched_features.append("primary_hash")
            else:
                # Check secondary hashes
                hash_matches = 0
                total_hashes = 0
                
                for hash_type in fp1.secondary_hashes:
                    if hash_type in fp2.secondary_hashes:
                        total_hashes += 1
                        if fp1.secondary_hashes[hash_type] == fp2.secondary_hashes[hash_type]:
                            hash_matches += 1
                            matched_features.append(f"hash_{hash_type}")
                
                if total_hashes > 0:
                    similarity_score = hash_matches / total_hashes
                    confidence = 0.7
        
        return SimilarityResult(
            content_id_1=fp1.content_id,
            content_id_2=fp2.content_id,
            similarity_score=similarity_score,
            similarity_type=method,
            confidence=confidence,
            matched_features=matched_features,
            metadata={
                "method": method,
                "has_embeddings": bool(fp1.feature_vector and fp2.feature_vector)
            }
        )
    
    async def _calculate_image_similarity(
        self,
        fp1: ContentFingerprint,
        fp2: ContentFingerprint,
        method: str
    ) -> SimilarityResult:
        """Calculate image similarity."""
        matched_features = []
        similarity_score = 0.0
        confidence = 0.5
        
        if method == "perceptual":
            # Compare perceptual hashes
            hash1 = fp1.primary_hash
            hash2 = fp2.primary_hash
            
            if hash1 and hash2:
                # Calculate Hamming distance
                hamming_distance = self._hamming_distance(hash1, hash2)
                max_distance = len(hash1) * 4  # Each hex char represents 4 bits
                
                similarity_score = 1.0 - (hamming_distance / max_distance)
                confidence = 0.8
                matched_features.append("perceptual_hash")
        
        elif method == "feature_vector" and fp1.feature_vector and fp2.feature_vector:
            # Compare feature vectors
            vec1 = np.array(fp1.feature_vector)
            vec2 = np.array(fp2.feature_vector)
            
            # Euclidean distance normalized
            distance = np.linalg.norm(vec1 - vec2)
            max_distance = np.sqrt(len(vec1))  # Maximum possible distance
            
            similarity_score = max(0.0, 1.0 - (distance / max_distance))
            confidence = 0.7
            matched_features.append("feature_vector")
        
        # Check secondary hashes as fallback
        if similarity_score < 0.5:
            hash_similarities = []
            for hash_type in ['dhash', 'ahash', 'color_hist']:
                if (hash_type in fp1.secondary_hashes and 
                    hash_type in fp2.secondary_hashes):
                    
                    hash1 = fp1.secondary_hashes[hash_type]
                    hash2 = fp2.secondary_hashes[hash_type]
                    
                    if hash1 == hash2:
                        hash_similarities.append(1.0)
                        matched_features.append(f"hash_{hash_type}")
                    else:
                        hamming_dist = self._hamming_distance(hash1, hash2)
                        max_dist = len(hash1) * 4
                        hash_sim = 1.0 - (hamming_dist / max_dist)
                        hash_similarities.append(hash_sim)
                        
                        if hash_sim > 0.8:
                            matched_features.append(f"hash_{hash_type}")
            
            if hash_similarities:
                similarity_score = max(similarity_score, np.mean(hash_similarities))
                confidence = min(confidence + 0.1, 1.0)
        
        return SimilarityResult(
            content_id_1=fp1.content_id,
            content_id_2=fp2.content_id,
            similarity_score=similarity_score,
            similarity_type=method,
            confidence=confidence,
            matched_features=matched_features,
            metadata={
                "method": method,
                "has_features": bool(fp1.feature_vector and fp2.feature_vector)
            }
        )
    
    async def _calculate_audio_similarity(
        self,
        fp1: ContentFingerprint,
        fp2: ContentFingerprint,
        method: str
    ) -> SimilarityResult:
        """Calculate audio similarity."""
        matched_features = []
        similarity_score = 0.0
        confidence = 0.5
        
        if method == "spectral" and fp1.feature_vector and fp2.feature_vector:
            # Compare audio feature vectors
            vec1 = np.array(fp1.feature_vector)
            vec2 = np.array(fp2.feature_vector)
            
            # Cosine similarity for audio features
            cosine_sim = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
            similarity_score = max(0.0, cosine_sim)
            confidence = 0.9
            matched_features.append("spectral_features")
        
        # Check audio-specific hashes
        audio_hashes = ['mfcc', 'chroma', 'spectral', 'rhythm']
        hash_similarities = []
        
        for hash_type in audio_hashes:
            if (hash_type in fp1.secondary_hashes and 
                hash_type in fp2.secondary_hashes):
                
                if fp1.secondary_hashes[hash_type] == fp2.secondary_hashes[hash_type]:
                    hash_similarities.append(1.0)
                    matched_features.append(f"hash_{hash_type}")
                else:
                    # Could implement more sophisticated hash comparison here
                    hash_similarities.append(0.0)
        
        if hash_similarities:
            hash_similarity = np.mean(hash_similarities)
            similarity_score = max(similarity_score, hash_similarity)
            if hash_similarity > 0.5:
                confidence = min(confidence + 0.2, 1.0)
        
        return SimilarityResult(
            content_id_1=fp1.content_id,
            content_id_2=fp2.content_id,
            similarity_score=similarity_score,
            similarity_type=method,
            confidence=confidence,
            matched_features=matched_features,
            metadata={
                "method": method,
                "audio_duration_1": fp1.metadata.get("duration", 0),
                "audio_duration_2": fp2.metadata.get("duration", 0)
            }
        )
    
    async def _calculate_video_similarity(
        self,
        fp1: ContentFingerprint,
        fp2: ContentFingerprint,
        method: str
    ) -> SimilarityResult:
        """Calculate video similarity."""
        matched_features = []
        similarity_score = 0.0
        confidence = 0.5
        
        if method == "frame_based":
            # Compare frame sequences
            if ('frame_sequence' in fp1.secondary_hashes and 
                'frame_sequence' in fp2.secondary_hashes):
                
                if fp1.secondary_hashes['frame_sequence'] == fp2.secondary_hashes['frame_sequence']:
                    similarity_score = 1.0
                    confidence = 0.9
                    matched_features.append("frame_sequence")
            
            # Compare first and last frames
            frame_matches = 0
            frame_total = 0
            
            for frame_type in ['first_frame', 'last_frame']:
                if (frame_type in fp1.secondary_hashes and 
                    frame_type in fp2.secondary_hashes):
                    frame_total += 1
                    
                    hash1 = fp1.secondary_hashes[frame_type]
                    hash2 = fp2.secondary_hashes[frame_type]
                    
                    if hash1 == hash2:
                        frame_matches += 1
                        matched_features.append(frame_type)
                    else:
                        # Calculate perceptual similarity
                        hamming_dist = self._hamming_distance(hash1, hash2)
                        max_dist = len(hash1) * 4
                        frame_sim = 1.0 - (hamming_dist / max_dist)
                        
                        if frame_sim > 0.8:
                            frame_matches += 0.5
                            matched_features.append(f"{frame_type}_similar")
            
            if frame_total > 0:
                frame_similarity = frame_matches / frame_total
                similarity_score = max(similarity_score, frame_similarity)
        
        # Compare visual features if available
        if fp1.feature_vector and fp2.feature_vector:
            vec1 = np.array(fp1.feature_vector)
            vec2 = np.array(fp2.feature_vector)
            
            cosine_sim = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
            feature_similarity = max(0.0, cosine_sim)
            
            similarity_score = max(similarity_score, feature_similarity)
            if feature_similarity > 0.5:
                matched_features.append("visual_features")
                confidence = min(confidence + 0.2, 1.0)
        
        return SimilarityResult(
            content_id_1=fp1.content_id,
            content_id_2=fp2.content_id,
            similarity_score=similarity_score,
            similarity_type=method,
            confidence=confidence,
            matched_features=matched_features,
            metadata={
                "method": method,
                "video_duration_1": fp1.metadata.get("duration", 0),
                "video_duration_2": fp2.metadata.get("duration", 0),
                "frame_count_1": fp1.metadata.get("frame_count", 0),
                "frame_count_2": fp2.metadata.get("frame_count", 0)
            }
        )
    
    async def _calculate_generic_similarity(
        self,
        fp1: ContentFingerprint,
        fp2: ContentFingerprint,
        method: str
    ) -> SimilarityResult:
        """Calculate generic similarity."""
        matched_features = []
        similarity_score = 0.0
        confidence = 0.3
        
        # Compare primary hashes
        if fp1.primary_hash == fp2.primary_hash:
            similarity_score = 1.0
            confidence = 1.0
            matched_features.append("primary_hash")
        else:
            # Compare secondary hashes
            hash_matches = 0
            total_hashes = 0
            
            for hash_type in fp1.secondary_hashes:
                if hash_type in fp2.secondary_hashes:
                    total_hashes += 1
                    if fp1.secondary_hashes[hash_type] == fp2.secondary_hashes[hash_type]:
                        hash_matches += 1
                        matched_features.append(f"hash_{hash_type}")
            
            if total_hashes > 0:
                similarity_score = hash_matches / total_hashes
                confidence = 0.5
        
        return SimilarityResult(
            content_id_1=fp1.content_id,
            content_id_2=fp2.content_id,
            similarity_score=similarity_score,
            similarity_type=method,
            confidence=confidence,
            matched_features=matched_features,
            metadata={"method": method}
        )
    
    def _hamming_distance(self, hash1: str, hash2: str) -> int:
        """Calculate Hamming distance between two hex hashes."""
        if len(hash1) != len(hash2):
            return max(len(hash1), len(hash2)) * 4  # Maximum distance
        
        distance = 0
        for i in range(len(hash1)):
            # Convert hex chars to integers and XOR
            val1 = int(hash1[i], 16)
            val2 = int(hash2[i], 16)
            xor_result = val1 ^ val2
            
            # Count bits set in XOR result
            distance += bin(xor_result).count('1')
        
        return distance

# Factory functions
def create_fingerprint_generator() -> ContentFingerprintGenerator:
    """
Create a new fingerprint generator."""
    return ContentFingerprintGenerator()

def create_similarity_analyzer() -> SimilarityAnalyzer:
    """
Create a new similarity analyzer."""
    return SimilarityAnalyzer()

async def generate_content_fingerprint(
    content: Union[str, bytes, np.ndarray],
    content_type: str,
    content_id: str,
    metadata: Optional[Dict[str, Any]] = None
) -> ContentFingerprint:
    """
Quick function to generate content fingerprint."""
    generator = create_fingerprint_generator()
    return await generator.generate_fingerprint(content, content_type, content_id, metadata)

async def calculate_content_similarity(
    fingerprint1: ContentFingerprint,
    fingerprint2: ContentFingerprint,
    similarity_type: str = "auto"
) -> SimilarityResult:
    """Quick function to calculate content similarity."""
    analyzer = create_similarity_analyzer()
    return await analyzer.calculate_similarity(fingerprint1, fingerprint2, similarity_type)

# Export main components
__all__ = [
    'ContentFingerprint',
    'SimilarityResult',
    'ContentFingerprintGenerator',
    'SimilarityAnalyzer',
    'create_fingerprint_generator',
    'create_similarity_analyzer',
    'generate_content_fingerprint',
    'calculate_content_similarity',
]
