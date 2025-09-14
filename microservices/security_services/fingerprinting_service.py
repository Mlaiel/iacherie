"""
🔍 Content Fingerprinting Microservice
Advanced content fingerprinting and identification service for copyright protection

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Any, Optional, Union, Tuple, Set
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime, timedelta
import asyncio
import uuid
import hashlib
import logging
from abc import ABC, abstractmethod
import numpy as np
import json
import base64

logger = logging.getLogger(__name__)


class ContentType(str, Enum):
    """Content types for fingerprinting"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"


class FingerprintType(str, Enum):
    """Types of fingerprinting algorithms"""
    PERCEPTUAL_HASH = "perceptual_hash"
    CHROMAPRINT = "chromaprint"
    WAVELET_HASH = "wavelet_hash"
    DCT_HASH = "dct_hash"
    SIFT_FEATURES = "sift_features"
    ORB_FEATURES = "orb_features"
    SEMANTIC_HASH = "semantic_hash"
    PHONETIC_HASH = "phonetic_hash"
    FUZZY_HASH = "fuzzy_hash"
    ROBUST_HASH = "robust_hash"


class MatchType(str, Enum):
    """Types of content matches"""
    EXACT = "exact"
    NEAR_DUPLICATE = "near_duplicate"
    PARTIAL = "partial"
    TRANSFORMED = "transformed"
    DERIVATIVE = "derivative"
    REMIX = "remix"
    COVER = "cover"
    SAMPLE = "sample"


class FingerprintStatus(str, Enum):
    """Fingerprinting operation status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


class ContentFingerprint(BaseModel):
    """Content fingerprint data model"""
    fingerprint_id: str = Field(..., description="Unique fingerprint identifier")
    content_id: str = Field(..., description="Associated content identifier")
    creator_id: str = Field(..., description="Content creator identifier")
    content_type: ContentType = Field(..., description="Type of content")
    fingerprint_type: FingerprintType = Field(..., description="Fingerprinting algorithm used")
    fingerprint_data: str = Field(..., description="Base64 encoded fingerprint data")
    fingerprint_hash: str = Field(..., description="Hash of fingerprint for quick lookup")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Content metadata")
    features: Dict[str, Any] = Field(default_factory=dict, description="Extracted features")
    confidence_score: float = Field(..., ge=0, le=1, description="Fingerprint quality score")
    segment_info: Optional[Dict[str, Any]] = Field(None, description="Segment information")
    duration_seconds: Optional[float] = Field(None, description="Content duration")
    file_size_bytes: Optional[int] = Field(None, description="Original file size")
    checksum: str = Field(..., description="Content checksum")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(None, description="Fingerprint expiry")
    tags: List[str] = Field(default_factory=list, description="Content tags")


class FingerprintMatch(BaseModel):
    """Fingerprint match result"""
    match_id: str = Field(..., description="Unique match identifier")
    query_fingerprint_id: str = Field(..., description="Query fingerprint ID")
    reference_fingerprint_id: str = Field(..., description="Matched reference fingerprint ID")
    match_type: MatchType = Field(..., description="Type of match")
    similarity_score: float = Field(..., ge=0, le=1, description="Similarity score")
    confidence_score: float = Field(..., ge=0, le=1, description="Match confidence")
    overlap_percentage: float = Field(default=0.0, ge=0, le=100, description="Content overlap percentage")
    time_offset: Optional[float] = Field(None, description="Time offset in seconds")
    spatial_offset: Optional[Dict[str, int]] = Field(None, description="Spatial offset for images")
    transformation_info: Dict[str, Any] = Field(default_factory=dict, description="Applied transformations")
    segment_matches: List[Dict[str, Any]] = Field(default_factory=list, description="Segment-level matches")
    false_positive_probability: float = Field(default=0.0, ge=0, le=1, description="False positive probability")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class FingerprintRequest(BaseModel):
    """Content fingerprinting request"""
    request_id: str = Field(..., description="Unique request identifier")
    content_id: str = Field(..., description="Content identifier")
    creator_id: str = Field(..., description="Creator identifier")
    content_type: ContentType = Field(..., description="Content type")
    fingerprint_types: List[FingerprintType] = Field(..., min_items=1, description="Fingerprinting algorithms")
    content_url: Optional[str] = Field(None, description="Content URL")
    content_data: Optional[bytes] = Field(None, description="Content binary data")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Content metadata")
    priority: int = Field(default=5, ge=1, le=10, description="Processing priority")
    segment_analysis: bool = Field(default=False, description="Enable segment-level analysis")
    quality_threshold: float = Field(default=0.8, ge=0, le=1, description="Minimum quality threshold")


class MatchRequest(BaseModel):
    """Content matching request"""
    request_id: str = Field(..., description="Unique request identifier")
    query_content_id: str = Field(..., description="Query content identifier")
    content_type: ContentType = Field(..., description="Content type")
    match_types: List[MatchType] = Field(default_factory=list, description="Types of matches to find")
    similarity_threshold: float = Field(default=0.8, ge=0, le=1, description="Minimum similarity threshold")
    max_matches: int = Field(default=100, ge=1, le=1000, description="Maximum number of matches")
    include_metadata: bool = Field(default=True, description="Include match metadata")
    filter_criteria: Dict[str, Any] = Field(default_factory=dict, description="Match filtering criteria")


class FingerprintingEngine(ABC):
    """Abstract base class for fingerprinting engines"""
    
    @abstractmethod
    async def generate_fingerprint(
        self, 
        content_data: bytes, 
        content_type: ContentType,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate fingerprint for content"""
        pass
    
    @abstractmethod
    async def compare_fingerprints(
        self, 
        fp1: Dict[str, Any], 
        fp2: Dict[str, Any]
    ) -> float:
        """Compare two fingerprints and return similarity score"""
        pass
    
    @abstractmethod
    def get_supported_types(self) -> List[ContentType]:
        """Get supported content types"""
        pass


class AudioFingerprintingEngine(FingerprintingEngine):
    """Audio content fingerprinting engine"""
    
    def get_supported_types(self) -> List[ContentType]:
        return [ContentType.AUDIO, ContentType.VIDEO]
    
    async def generate_fingerprint(
        self, 
        content_data: bytes, 
        content_type: ContentType,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate audio fingerprint"""
        
        # Simulate audio analysis
        await asyncio.sleep(0.2)
        
        # Extract audio features (simulated)
        duration = metadata.get("duration_seconds", 180.0)
        sample_rate = metadata.get("sample_rate", 44100)
        
        # Chromaprint-style fingerprint
        chroma_features = np.random.rand(12, int(duration * 2)).flatten()  # 2 frames per second
        
        # Spectral features
        spectral_features = {
            "spectral_centroid": np.random.rand(int(duration * 10)).tolist(),  # 10 frames per second
            "mfcc": np.random.rand(13, int(duration * 10)).tolist(),
            "spectral_rolloff": np.random.rand(int(duration * 10)).tolist(),
            "zero_crossing_rate": np.random.rand(int(duration * 10)).tolist()
        }
        
        # Tempo and rhythm features
        tempo_features = {
            "tempo_bpm": np.random.uniform(60, 200),
            "beat_positions": np.random.rand(int(duration / 0.5)).tolist(),  # Beat every 0.5s average
            "rhythm_pattern": np.random.randint(0, 16, 32).tolist()
        }
        
        # Create robust hash
        fingerprint_vector = np.concatenate([
            chroma_features[:1000],  # Limit size
            np.array(spectral_features["mfcc"]).flatten()[:500]
        ])
        
        # Quantize to create robust hash
        quantized = (fingerprint_vector * 255).astype(np.uint8)
        fingerprint_data = base64.b64encode(quantized.tobytes()).decode()
        
        return {
            "fingerprint_data": fingerprint_data,
            "features": {
                "chroma": chroma_features[:100].tolist(),  # Reduce for storage
                "spectral": spectral_features,
                "temporal": tempo_features
            },
            "metadata": {
                "duration": duration,
                "sample_rate": sample_rate,
                "algorithm": "chromaprint_spectral",
                "version": "1.0"
            },
            "confidence": np.random.uniform(0.85, 0.98)
        }
    
    async def compare_fingerprints(
        self, 
        fp1: Dict[str, Any], 
        fp2: Dict[str, Any]
    ) -> float:
        """Compare audio fingerprints"""
        
        try:
            # Decode fingerprint data
            data1 = np.frombuffer(base64.b64decode(fp1["fingerprint_data"]), dtype=np.uint8)
            data2 = np.frombuffer(base64.b64decode(fp2["fingerprint_data"]), dtype=np.uint8)
            
            # Ensure same length for comparison
            min_len = min(len(data1), len(data2))
            data1 = data1[:min_len]
            data2 = data2[:min_len]
            
            # Calculate similarity using normalized correlation
            correlation = np.corrcoef(data1.astype(float), data2.astype(float))[0, 1]
            correlation = 0 if np.isnan(correlation) else correlation
            
            # Also compare tempo features
            tempo1 = fp1.get("features", {}).get("temporal", {}).get("tempo_bpm", 0)
            tempo2 = fp2.get("features", {}).get("temporal", {}).get("tempo_bpm", 0)
            
            tempo_similarity = 1 - abs(tempo1 - tempo2) / max(tempo1, tempo2, 1)
            
            # Combine similarities
            final_similarity = (correlation * 0.8 + tempo_similarity * 0.2)
            return max(0, min(1, final_similarity))
            
        except Exception as e:
            logger.error(f"Audio fingerprint comparison failed: {str(e)}")
            return 0.0


class ImageFingerprintingEngine(FingerprintingEngine):
    """Image content fingerprinting engine"""
    
    def get_supported_types(self) -> List[ContentType]:
        return [ContentType.IMAGE, ContentType.VIDEO]
    
    async def generate_fingerprint(
        self, 
        content_data: bytes, 
        content_type: ContentType,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate image fingerprint"""
        
        # Simulate image analysis
        await asyncio.sleep(0.1)
        
        width = metadata.get("width", 1920)
        height = metadata.get("height", 1080)
        
        # Perceptual hash (pHash-style)
        # Simulate DCT-based perceptual hash
        phash = np.random.randint(0, 2, 64)  # 64-bit hash
        phash_data = ''.join(map(str, phash))
        
        # Color histogram
        color_hist = {
            "red_hist": np.random.rand(256).tolist(),
            "green_hist": np.random.rand(256).tolist(),
            "blue_hist": np.random.rand(256).tolist(),
            "dominant_colors": [
                [np.random.randint(0, 255) for _ in range(3)] for _ in range(5)
            ]
        }
        
        # Texture features
        texture_features = {
            "lbp_histogram": np.random.rand(256).tolist(),
            "glcm_features": {
                "contrast": np.random.uniform(0, 1),
                "dissimilarity": np.random.uniform(0, 1),
                "homogeneity": np.random.uniform(0, 1),
                "energy": np.random.uniform(0, 1)
            }
        }
        
        # Edge features
        edge_features = {
            "edge_density": np.random.uniform(0, 1),
            "edge_direction_hist": np.random.rand(36).tolist(),  # 36 directions
            "corner_count": np.random.randint(10, 1000)
        }
        
        # Combine features into fingerprint
        feature_vector = np.concatenate([
            phash.astype(float),
            np.array(color_hist["red_hist"])[:32],  # Reduce dimensionality
            np.array(texture_features["lbp_histogram"])[:32],
            np.array(edge_features["edge_direction_hist"])
        ])
        
        fingerprint_data = base64.b64encode(feature_vector.astype(np.float32).tobytes()).decode()
        
        return {
            "fingerprint_data": fingerprint_data,
            "features": {
                "perceptual_hash": phash_data,
                "color": color_hist,
                "texture": texture_features,
                "edges": edge_features
            },
            "metadata": {
                "width": width,
                "height": height,
                "algorithm": "perceptual_hash_combined",
                "version": "1.0"
            },
            "confidence": np.random.uniform(0.88, 0.97)
        }
    
    async def compare_fingerprints(
        self, 
        fp1: Dict[str, Any], 
        fp2: Dict[str, Any]
    ) -> float:
        """Compare image fingerprints"""
        
        try:
            # Compare perceptual hashes
            phash1 = fp1.get("features", {}).get("perceptual_hash", "")
            phash2 = fp2.get("features", {}).get("perceptual_hash", "")
            
            if phash1 and phash2 and len(phash1) == len(phash2):
                # Hamming distance for perceptual hash
                hamming_dist = sum(c1 != c2 for c1, c2 in zip(phash1, phash2))
                phash_similarity = 1 - (hamming_dist / len(phash1))
            else:
                phash_similarity = 0
            
            # Compare color histograms
            color1 = np.array(fp1.get("features", {}).get("color", {}).get("red_hist", []))
            color2 = np.array(fp2.get("features", {}).get("color", {}).get("red_hist", []))
            
            if len(color1) > 0 and len(color2) > 0:
                color_similarity = 1 - np.sum(np.abs(color1 - color2)) / (np.sum(color1) + np.sum(color2) + 1e-8)
                color_similarity = max(0, color_similarity)
            else:
                color_similarity = 0
            
            # Compare feature vectors
            data1 = np.frombuffer(base64.b64decode(fp1["fingerprint_data"]), dtype=np.float32)
            data2 = np.frombuffer(base64.b64decode(fp2["fingerprint_data"]), dtype=np.float32)
            
            min_len = min(len(data1), len(data2))
            if min_len > 0:
                cosine_sim = np.dot(data1[:min_len], data2[:min_len]) / (
                    np.linalg.norm(data1[:min_len]) * np.linalg.norm(data2[:min_len]) + 1e-8
                )
                cosine_sim = max(0, cosine_sim)
            else:
                cosine_sim = 0
            
            # Combine similarities
            final_similarity = (phash_similarity * 0.4 + color_similarity * 0.3 + cosine_sim * 0.3)
            return max(0, min(1, final_similarity))
            
        except Exception as e:
            logger.error(f"Image fingerprint comparison failed: {str(e)}")
            return 0.0


class TextFingerprintingEngine(FingerprintingEngine):
    """Text content fingerprinting engine"""
    
    def get_supported_types(self) -> List[ContentType]:
        return [ContentType.TEXT, ContentType.DOCUMENT]
    
    async def generate_fingerprint(
        self, 
        content_data: bytes, 
        content_type: ContentType,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate text fingerprint"""
        
        # Simulate text analysis
        await asyncio.sleep(0.05)
        
        try:
            text = content_data.decode('utf-8')
        except:
            text = str(content_data)
        
        # N-gram features
        words = text.lower().split()
        
        # Character-level features
        char_freq = {}
        for char in text.lower():
            if char.isalnum():
                char_freq[char] = char_freq.get(char, 0) + 1
        
        # Word-level features
        word_freq = {}
        for word in words:
            if len(word) > 2:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Bigram features
        bigrams = [words[i] + "_" + words[i+1] for i in range(len(words)-1)]
        bigram_freq = {}
        for bigram in bigrams:
            bigram_freq[bigram] = bigram_freq.get(bigram, 0) + 1
        
        # Structural features
        structural_features = {
            "word_count": len(words),
            "char_count": len(text),
            "sentence_count": text.count('.') + text.count('!') + text.count('?'),
            "paragraph_count": text.count('\n\n') + 1,
            "avg_word_length": np.mean([len(word) for word in words]) if words else 0,
            "avg_sentence_length": len(words) / max(text.count('.') + text.count('!') + text.count('?'), 1)
        }
        
        # Semantic hash (simplified)
        # Use top frequent words as semantic signature
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:50]
        semantic_signature = [word for word, freq in top_words]
        
        # Create fuzzy hash using rolling hash
        rolling_hash = []
        window_size = 10
        for i in range(0, len(words) - window_size + 1, window_size):
            window_text = ' '.join(words[i:i+window_size])
            window_hash = hashlib.md5(window_text.encode()).hexdigest()[:8]
            rolling_hash.append(window_hash)
        
        # Feature vector for similarity comparison
        feature_vector = np.array([
            len(words),
            len(text),
            structural_features["avg_word_length"],
            structural_features["avg_sentence_length"],
            len(set(words)),  # Unique words
            len(char_freq),   # Unique characters
        ] + [char_freq.get(chr(ord('a') + i), 0) for i in range(26)])  # Letter frequencies
        
        fingerprint_data = base64.b64encode(feature_vector.astype(np.float32).tobytes()).decode()
        
        return {
            "fingerprint_data": fingerprint_data,
            "features": {
                "structural": structural_features,
                "semantic_signature": semantic_signature,
                "rolling_hash": rolling_hash,
                "top_bigrams": sorted(bigram_freq.items(), key=lambda x: x[1], reverse=True)[:20]
            },
            "metadata": {
                "language": "en",  # Simplified
                "algorithm": "ngram_semantic_fuzzy",
                "version": "1.0"
            },
            "confidence": np.random.uniform(0.82, 0.95)
        }
    
    async def compare_fingerprints(
        self, 
        fp1: Dict[str, Any], 
        fp2: Dict[str, Any]
    ) -> float:
        """Compare text fingerprints"""
        
        try:
            # Compare structural features
            struct1 = fp1.get("features", {}).get("structural", {})
            struct2 = fp2.get("features", {}).get("structural", {})
            
            structural_similarity = 0
            if struct1 and struct2:
                # Normalize and compare key metrics
                word_ratio = min(struct1.get("word_count", 1), struct2.get("word_count", 1)) / max(struct1.get("word_count", 1), struct2.get("word_count", 1))
                avg_word_len_diff = abs(struct1.get("avg_word_length", 0) - struct2.get("avg_word_length", 0))
                avg_word_len_sim = 1 - min(avg_word_len_diff / 10, 1)  # Normalize by 10
                
                structural_similarity = (word_ratio + avg_word_len_sim) / 2
            
            # Compare semantic signatures
            sig1 = set(fp1.get("features", {}).get("semantic_signature", []))
            sig2 = set(fp2.get("features", {}).get("semantic_signature", []))
            
            if sig1 and sig2:
                semantic_similarity = len(sig1.intersection(sig2)) / len(sig1.union(sig2))
            else:
                semantic_similarity = 0
            
            # Compare rolling hashes (fuzzy matching)
            hash1 = fp1.get("features", {}).get("rolling_hash", [])
            hash2 = fp2.get("features", {}).get("rolling_hash", [])
            
            if hash1 and hash2:
                common_hashes = len(set(hash1).intersection(set(hash2)))
                total_hashes = len(set(hash1).union(set(hash2)))
                fuzzy_similarity = common_hashes / total_hashes if total_hashes > 0 else 0
            else:
                fuzzy_similarity = 0
            
            # Compare feature vectors
            data1 = np.frombuffer(base64.b64decode(fp1["fingerprint_data"]), dtype=np.float32)
            data2 = np.frombuffer(base64.b64decode(fp2["fingerprint_data"]), dtype=np.float32)
            
            if len(data1) > 0 and len(data2) > 0:
                cosine_sim = np.dot(data1, data2) / (np.linalg.norm(data1) * np.linalg.norm(data2) + 1e-8)
                cosine_sim = max(0, cosine_sim)
            else:
                cosine_sim = 0
            
            # Combine similarities
            final_similarity = (
                structural_similarity * 0.2 + 
                semantic_similarity * 0.4 + 
                fuzzy_similarity * 0.2 + 
                cosine_sim * 0.2
            )
            
            return max(0, min(1, final_similarity))
            
        except Exception as e:
            logger.error(f"Text fingerprint comparison failed: {str(e)}")
            return 0.0


class ContentFingerprintingService:
    """Main content fingerprinting service"""
    
    def __init__(self) -> None:
        self.fingerprinting_engines = {
            ContentType.AUDIO: AudioFingerprintingEngine(),
            ContentType.VIDEO: AudioFingerprintingEngine(),  # Can process audio track
            ContentType.IMAGE: ImageFingerprintingEngine(),
            ContentType.TEXT: TextFingerprintingEngine(),
            ContentType.DOCUMENT: TextFingerprintingEngine()
        }
        
        self.fingerprint_database: Dict[str, ContentFingerprint] = {}
        self.content_index: Dict[str, List[str]] = {}  # content_type -> [fingerprint_ids]
        self.hash_index: Dict[str, str] = {}  # fingerprint_hash -> fingerprint_id
        
        # Initialize content type indices
        for content_type in ContentType:
            self.content_index[content_type] = []
    
    async def generate_fingerprint(self, request: FingerprintRequest) -> Optional[str]:
        """Generate fingerprint for content"""
        
        try:
            # Get content data
            if request.content_data:
                content_data = request.content_data
            elif request.content_url:
                # In production, would fetch from URL
                content_data = b"simulated_content_data"
            else:
                logger.error("No content data or URL provided")
                return None
            
            # Get appropriate engine
            engine = self.fingerprinting_engines.get(request.content_type)
            if not engine:
                logger.error(f"No fingerprinting engine for content type {request.content_type}")
                return None
            
            fingerprint_results = []
            
            # Generate fingerprints for each requested type
            for fp_type in request.fingerprint_types:
                try:
                    result = await engine.generate_fingerprint(
                        content_data, request.content_type, request.metadata
                    )
                    
                    if result["confidence"] >= request.quality_threshold:
                        fingerprint_results.append((fp_type, result))
                    else:
                        logger.warning(f"Fingerprint quality below threshold for {fp_type}")
                        
                except Exception as e:
                    logger.error(f"Fingerprinting failed for {fp_type}: {str(e)}")
            
            if not fingerprint_results:
                return None
            
            # Create primary fingerprint (use first successful result)
            fp_type, fp_result = fingerprint_results[0]
            fingerprint_id = str(uuid.uuid4())
            
            # Create fingerprint hash for indexing
            fingerprint_hash = hashlib.sha256(fp_result["fingerprint_data"].encode()).hexdigest()
            
            # Calculate content checksum
            content_checksum = hashlib.sha256(content_data).hexdigest()
            
            # Create fingerprint object
            fingerprint = ContentFingerprint(
                fingerprint_id=fingerprint_id,
                content_id=request.content_id,
                creator_id=request.creator_id,
                content_type=request.content_type,
                fingerprint_type=fp_type,
                fingerprint_data=fp_result["fingerprint_data"],
                fingerprint_hash=fingerprint_hash,
                metadata=fp_result.get("metadata", {}),
                features=fp_result.get("features", {}),
                confidence_score=fp_result["confidence"],
                duration_seconds=request.metadata.get("duration_seconds"),
                file_size_bytes=len(content_data),
                checksum=content_checksum
            )
            
            # Store in database and indices
            self.fingerprint_database[fingerprint_id] = fingerprint
            self.content_index[request.content_type].append(fingerprint_id)
            self.hash_index[fingerprint_hash] = fingerprint_id
            
            logger.info(f"Generated fingerprint {fingerprint_id} for content {request.content_id}")
            return fingerprint_id
            
        except Exception as e:
            logger.error(f"Fingerprint generation failed: {str(e)}")
            return None
    
    async def find_matches(self, request: MatchRequest) -> List[FingerprintMatch]:
        """Find content matches"""
        
        try:
            # Get query fingerprint
            query_fingerprint = None
            for fp_id, fp in self.fingerprint_database.items():
                if fp.content_id == request.query_content_id:
                    query_fingerprint = fp
                    break
            
            if not query_fingerprint:
                logger.error(f"Query fingerprint not found for content {request.query_content_id}")
                return []
            
            # Get engine for comparison
            engine = self.fingerprinting_engines.get(request.content_type)
            if not engine:
                logger.error(f"No engine for content type {request.content_type}")
                return []
            
            matches = []
            
            # Search through fingerprints of same content type
            candidate_fp_ids = self.content_index.get(request.content_type, [])
            
            for fp_id in candidate_fp_ids:
                if fp_id == query_fingerprint.fingerprint_id:
                    continue  # Skip self
                
                candidate_fp = self.fingerprint_database[fp_id]
                
                # Apply filters
                if not self._passes_filter_criteria(candidate_fp, request.filter_criteria):
                    continue
                
                try:
                    # Compare fingerprints
                    similarity = await engine.compare_fingerprints(
                        {
                            "fingerprint_data": query_fingerprint.fingerprint_data,
                            "features": query_fingerprint.features
                        },
                        {
                            "fingerprint_data": candidate_fp.fingerprint_data,
                            "features": candidate_fp.features
                        }
                    )
                    
                    if similarity >= request.similarity_threshold:
                        # Determine match type
                        match_type = self._determine_match_type(similarity, query_fingerprint, candidate_fp)
                        
                        # Calculate additional metrics
                        overlap_percentage = similarity * 100
                        confidence = min(query_fingerprint.confidence_score, candidate_fp.confidence_score)
                        
                        match = FingerprintMatch(
                            match_id=str(uuid.uuid4()),
                            query_fingerprint_id=query_fingerprint.fingerprint_id,
                            reference_fingerprint_id=candidate_fp.fingerprint_id,
                            match_type=match_type,
                            similarity_score=similarity,
                            confidence_score=confidence,
                            overlap_percentage=overlap_percentage,
                            transformation_info=self._analyze_transformations(query_fingerprint, candidate_fp),
                            false_positive_probability=self._estimate_false_positive_rate(similarity, match_type)
                        )
                        
                        matches.append(match)
                        
                except Exception as e:
                    logger.error(f"Error comparing fingerprints {query_fingerprint.fingerprint_id} and {fp_id}: {str(e)}")
            
            # Sort by similarity and limit results
            matches.sort(key=lambda x: x.similarity_score, reverse=True)
            matches = matches[:request.max_matches]
            
            logger.info(f"Found {len(matches)} matches for content {request.query_content_id}")
            return matches
            
        except Exception as e:
            logger.error(f"Content matching failed: {str(e)}")
            return []
    
    async def batch_fingerprint(self, requests: List[FingerprintRequest]) -> List[Optional[str]]:
        """Process multiple fingerprinting requests"""
        
        tasks = [self.generate_fingerprint(request) for request in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Batch fingerprinting error: {str(result)}")
                processed_results.append(None)
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def get_fingerprint(self, fingerprint_id: str) -> Optional[ContentFingerprint]:
        """Get fingerprint by ID"""
        return self.fingerprint_database.get(fingerprint_id)
    
    async def delete_fingerprint(self, fingerprint_id: str) -> bool:
        """Delete a fingerprint"""
        
        if fingerprint_id not in self.fingerprint_database:
            return False
        
        fingerprint = self.fingerprint_database[fingerprint_id]
        
        # Remove from database
        del self.fingerprint_database[fingerprint_id]
        
        # Remove from indices
        if fingerprint_id in self.content_index[fingerprint.content_type]:
            self.content_index[fingerprint.content_type].remove(fingerprint_id)
        
        if fingerprint.fingerprint_hash in self.hash_index:
            del self.hash_index[fingerprint.fingerprint_hash]
        
        logger.info(f"Deleted fingerprint {fingerprint_id}")
        return True
    
    def _passes_filter_criteria(self, fingerprint: ContentFingerprint, criteria: Dict[str, Any]) -> bool:
        """Check if fingerprint passes filter criteria"""
        
        if not criteria:
            return True
        
        # Creator filter
        if "creator_id" in criteria and fingerprint.creator_id != criteria["creator_id"]:
            return False
        
        # Confidence threshold
        if "min_confidence" in criteria and fingerprint.confidence_score < criteria["min_confidence"]:
            return False
        
        # Date range filter
        if "created_after" in criteria:
            after_date = datetime.fromisoformat(criteria["created_after"])
            if fingerprint.created_at < after_date:
                return False
        
        if "created_before" in criteria:
            before_date = datetime.fromisoformat(criteria["created_before"])
            if fingerprint.created_at > before_date:
                return False
        
        # Tag filter
        if "tags" in criteria:
            required_tags = set(criteria["tags"])
            fingerprint_tags = set(fingerprint.tags)
            if not required_tags.issubset(fingerprint_tags):
                return False
        
        return True
    
    def _determine_match_type(
        self, 
        similarity: float, 
        query_fp: ContentFingerprint, 
        candidate_fp: ContentFingerprint
    ) -> MatchType:
        """Determine the type of match based on similarity and metadata"""
        
        if similarity >= 0.98:
            return MatchType.EXACT
        elif similarity >= 0.9:
            return MatchType.NEAR_DUPLICATE
        elif similarity >= 0.8:
            # Check for transformations
            if query_fp.content_type == ContentType.AUDIO:
                return MatchType.COVER if similarity >= 0.85 else MatchType.REMIX
            elif query_fp.content_type == ContentType.IMAGE:
                return MatchType.TRANSFORMED
            else:
                return MatchType.DERIVATIVE
        elif similarity >= 0.6:
            return MatchType.PARTIAL
        else:
            return MatchType.SAMPLE
    
    def _analyze_transformations(
        self, 
        query_fp: ContentFingerprint, 
        candidate_fp: ContentFingerprint
    ) -> Dict[str, Any]:
        """Analyze potential transformations between content"""
        
        transformations = {}
        
        if query_fp.content_type == ContentType.AUDIO:
            # Check tempo differences
            query_tempo = query_fp.features.get("temporal", {}).get("tempo_bpm", 0)
            candidate_tempo = candidate_fp.features.get("temporal", {}).get("tempo_bpm", 0)
            
            if query_tempo > 0 and candidate_tempo > 0:
                tempo_ratio = candidate_tempo / query_tempo
                if abs(tempo_ratio - 1.0) > 0.1:
                    transformations["tempo_change"] = {
                        "ratio": tempo_ratio,
                        "type": "speed_up" if tempo_ratio > 1.1 else "slow_down" if tempo_ratio < 0.9 else "minor"
                    }
        
        elif query_fp.content_type == ContentType.IMAGE:
            # Check dimension differences
            query_width = query_fp.metadata.get("width", 0)
            query_height = query_fp.metadata.get("height", 0)
            candidate_width = candidate_fp.metadata.get("width", 0)
            candidate_height = candidate_fp.metadata.get("height", 0)
            
            if all([query_width, query_height, candidate_width, candidate_height]):
                width_ratio = candidate_width / query_width
                height_ratio = candidate_height / query_height
                
                if abs(width_ratio - height_ratio) < 0.1:  # Uniform scaling
                    if abs(width_ratio - 1.0) > 0.1:
                        transformations["scaling"] = {
                            "ratio": width_ratio,
                            "type": "uniform"
                        }
                else:
                    transformations["aspect_ratio_change"] = {
                        "width_ratio": width_ratio,
                        "height_ratio": height_ratio
                    }
        
        return transformations
    
    def _estimate_false_positive_rate(self, similarity: float, match_type: MatchType) -> float:
        """Estimate false positive probability"""
        
        # Base false positive rates by match type (heuristic)
        base_rates = {
            MatchType.EXACT: 0.001,
            MatchType.NEAR_DUPLICATE: 0.005,
            MatchType.PARTIAL: 0.02,
            MatchType.TRANSFORMED: 0.01,
            MatchType.DERIVATIVE: 0.03,
            MatchType.REMIX: 0.05,
            MatchType.COVER: 0.08,
            MatchType.SAMPLE: 0.15
        }
        
        base_rate = base_rates.get(match_type, 0.1)
        
        # Adjust based on similarity score
        # Higher similarity = lower false positive rate
        similarity_factor = (1 - similarity) * 2  # 0 to 2 multiplier
        
        return min(0.5, base_rate * similarity_factor)
    
    def get_service_health(self) -> Dict[str, Any]:
        """Get service health and statistics"""
        
        total_fingerprints = len(self.fingerprint_database)
        
        # Count by content type
        type_counts = {}
        confidence_scores = []
        
        for fp in self.fingerprint_database.values():
            type_counts[fp.content_type] = type_counts.get(fp.content_type, 0) + 1
            confidence_scores.append(fp.confidence_score)
        
        avg_confidence = np.mean(confidence_scores) if confidence_scores else 0
        
        return {
            "service_status": "healthy",
            "total_fingerprints": total_fingerprints,
            "fingerprints_by_type": type_counts,
            "average_confidence": avg_confidence,
            "supported_content_types": [ct.value for ct in ContentType],
            "supported_fingerprint_types": [ft.value for ft in FingerprintType],
            "database_size_mb": total_fingerprints * 0.1,  # Estimated
        }


# Export classes for external use
__all__ = [
    'ContentType',
    'FingerprintType',
    'MatchType',
    'FingerprintStatus',
    'ContentFingerprint',
    'FingerprintMatch',
    'FingerprintRequest',
    'MatchRequest',
    'FingerprintingEngine',
    'AudioFingerprintingEngine',
    'ImageFingerprintingEngine',
    'TextFingerprintingEngine',
    'ContentFingerprintingService'
]