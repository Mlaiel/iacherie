"""♻️ Deduplication Engine - IA Influencer Agent Platform Enterprise
================================================================
Module: backend/data_management/storage/deduplication_engine.py
Author: Fahed Mlaiel (mlaiel@live.de)
================================================================

Intelligent deduplication engine for content optimization
with advanced fingerprinting and similarity detection.

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

AVERTISSEMENT LÉGAL:
Ce code est la propriété exclusive de Fahed Mlaiel. Toute utilisation,
reproduction, modification ou distribution non autorisée est strictement
interdite et fera l'objet de poursuites judiciaires.

ÉQUIPE PROJET - SPÉCIALITÉS:
- Lead Dev IA: Fahed Mlaiel
- Backend Senior: Fahed Mlaiel  
- ML Engineer: Fahed Mlaiel
- DBA: Fahed Mlaiel
- Sécurité: Fahed Mlaiel
- Microservices: Fahed Mlaiel
- Audio Engineer: Fahed Mlaiel
- DevOps: Fahed Mlaiel
- IA Prompt Engineer: Fahed Mlaiel
"""
from typing import Dict, List, Optional, Any, Union, Tuple, Set
import logging
import asyncio
import hashlib
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import struct
from collections import defaultdict

# Audio/Video similarity
import numpy as np
from scipy.spatial.distance import cosine
import imagehash
from PIL import Image
import io

# Text similarity
from difflib import SequenceMatcher
import re

logger = logging.getLogger(__name__)

class DuplicateType(Enum):
    """Types of duplicate detection"""    EXACT = "exact"                    # Bit-for-bit identical
    NEAR_DUPLICATE = "near_duplicate"  # Very similar content
    VARIANT = "variant"                # Same content, different format
    REFERENCE = "reference"            # Reference to existing content

class ContentFingerprint(Enum):
    """Content fingerprinting methods"""    SHA256 = "sha256"              # Cryptographic hash
    MD5 = "md5"                    # Fast hash
    PERCEPTUAL = "perceptual"      # Content-aware hash
    FUZZY = "fuzzy"                # Fuzzy matching
    SEMANTIC = "semantic"          # Semantic similarity

@dataclass
class DuplicationResult:
    """Result of deduplication analysis"""    is_duplicate: bool
    duplicate_type: Optional[DuplicateType] = None
    original_content_id: Optional[str] = None
    similarity_score: float = 0.0
    fingerprints: Dict[str, str] = field(default_factory=dict)
    space_saved_bytes: int = 0
    processing_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ContentFingerprints:
    """Content fingerprints for deduplication"""    content_id: str
    sha256_hash: str
    md5_hash: str
    perceptual_hash: Optional[str] = None
    fuzzy_hash: Optional[str] = None
    semantic_features: Optional[List[float]] = None
    content_type: str = ""
    file_size: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    reference_count: int = 1

@dataclass
class DeduplicationConfig:
    """Configuration for deduplication engine"""    enable_exact_matching: bool = True
    enable_near_duplicate_detection: bool = True
    enable_variant_detection: bool = True
    similarity_threshold: float = 0.95
    perceptual_threshold: float = 0.90
    semantic_threshold: float = 0.85
    max_processing_time: int = 30  # seconds
    chunk_size: int = 8192
    enable_audio_fingerprinting: bool = True
    enable_image_fingerprinting: bool = True
    enable_text_similarity: bool = True

class AudioFingerprinter:
    """Audio content fingerprinting for similarity detection"""    
    @staticmethod
    def extract_audio_features(audio_data: bytes) -> Optional[List[float]]:
        """Extract audio features for similarity comparison"""        try:
            # Simplified audio feature extraction
            # In production, use librosa or similar for proper audio analysis
            
            # Convert audio data to numpy array (simplified)
            audio_array = np.frombuffer(audio_data[:1024], dtype=np.int16)
            
            if len(audio_array) == 0:
                return None
            
            # Extract basic features
            features = [
                float(np.mean(audio_array)),      # Average amplitude
                float(np.std(audio_array)),       # Standard deviation
                float(np.max(audio_array)),       # Peak amplitude
                float(np.min(audio_array)),       # Minimum amplitude
                float(len(audio_array)),          # Length
            ]
            
            # Add frequency domain features (simplified)
            fft = np.fft.fft(audio_array)
            fft_magnitude = np.abs(fft)
            
            features.extend([
                float(np.mean(fft_magnitude)),
                float(np.std(fft_magnitude)),
                float(np.argmax(fft_magnitude))   # Dominant frequency bin
            ])
            
            return features
            
        except Exception as e:
            logger.warning(f"Audio feature extraction failed: {str(e)}")
            return None
    
    @staticmethod
    def calculate_audio_similarity(features1: List[float], features2: List[float]) -> float:
        """Calculate similarity between audio feature vectors"""        try:
            if len(features1) != len(features2):
                return 0.0
            
            # Use cosine similarity
            return 1.0 - cosine(features1, features2)
            
        except Exception as e:
            logger.warning(f"Audio similarity calculation failed: {str(e)}")
            return 0.0

class ImageFingerprinter:
    """Image content fingerprinting for similarity detection"""    
    @staticmethod
    def extract_perceptual_hash(image_data: bytes) -> Optional[str]:
        """Extract perceptual hash for image similarity"""        try:
            image = Image.open(io.BytesIO(image_data))
            
            # Generate multiple hash types for better accuracy
            dhash = imagehash.dhash(image)
            phash = imagehash.phash(image)
            ahash = imagehash.average_hash(image)
            
            # Combine hashes
            combined_hash = f"{dhash}_{phash}_{ahash}"
            return combined_hash
            
        except Exception as e:
            logger.warning(f"Image perceptual hash extraction failed: {str(e)}")
            return None
    
    @staticmethod
    def calculate_image_similarity(hash1: str, hash2: str) -> float:
        """Calculate similarity between image perceptual hashes"""        try:
            hashes1 = hash1.split('_')
            hashes2 = hash2.split('_')
            
            if len(hashes1) != 3 or len(hashes2) != 3:
                return 0.0
            
            similarities = []
            for h1, h2 in zip(hashes1, hashes2):
                # Calculate Hamming distance
                hash_obj1 = imagehash.hex_to_hash(h1)
                hash_obj2 = imagehash.hex_to_hash(h2)
                distance = hash_obj1 - hash_obj2
                
                # Convert distance to similarity (0-1)
                max_distance = len(h1) * 4  # 4 bits per hex char
                similarity = 1.0 - (distance / max_distance)
                similarities.append(similarity)
            
            # Return average similarity
            return sum(similarities) / len(similarities)
            
        except Exception as e:
            logger.warning(f"Image similarity calculation failed: {str(e)}")
            return 0.0

class TextSimilarityAnalyzer:
    """Text content similarity analysis"""    
    @staticmethod
    def calculate_text_similarity(text1: str, text2: str) -> float:
        """Calculate similarity between text content"""        try:
            # Normalize texts
            normalized1 = TextSimilarityAnalyzer._normalize_text(text1)
            normalized2 = TextSimilarityAnalyzer._normalize_text(text2)
            
            # Calculate sequence similarity
            seq_similarity = SequenceMatcher(None, normalized1, normalized2).ratio()
            
            # Calculate word-level similarity
            words1 = set(normalized1.split())
            words2 = set(normalized2.split())
            
            if not words1 and not words2:
                return 1.0
            if not words1 or not words2:
                return 0.0
            
            word_similarity = len(words1.intersection(words2)) / len(words1.union(words2))
            
            # Combine similarities
            final_similarity = (seq_similarity * 0.6) + (word_similarity * 0.4)
            return final_similarity
            
        except Exception as e:
            logger.warning(f"Text similarity calculation failed: {str(e)}")
            return 0.0
    
    @staticmethod
    def _normalize_text(text: str) -> str:
        """Normalize text for comparison"""        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove punctuation (keep only alphanumeric and spaces)
        text = re.sub(r'[^a-z0-9\s]', '', text)
        
        return text

class DeduplicationEngine:
    """    Enterprise deduplication engine for content optimization.
    
    Business Logic:
    - Detects exact duplicates to save storage space
    - Identifies near-duplicates for version management
    - Finds content variants across formats
    - Maintains reference counting for shared content
    - Provides space savings analytics
    """    
    def __init__(self, config: Optional[DeduplicationConfig] = None):
        """Initialize deduplication engine"""        self.config = config or DeduplicationConfig()
        
        # Content fingerprint storage
        self.fingerprints: Dict[str, ContentFingerprints] = {}
        
        # Hash-based indexes for fast lookup
        self.sha256_index: Dict[str, str] = {}  # hash -> content_id
        self.md5_index: Dict[str, str] = {}
        self.perceptual_index: Dict[str, str] = {}
        
        # Content type analyzers
        self.audio_fingerprinter = AudioFingerprinter()
        self.image_fingerprinter = ImageFingerprinter()
        self.text_analyzer = TextSimilarityAnalyzer()
        
        # Performance metrics
        self.metrics = {
            'total_analyses': 0,
            'exact_duplicates_found': 0,
            'near_duplicates_found': 0,
            'variants_found': 0,
            'total_space_saved_mb': 0.0,
            'average_processing_time': 0.0,
            'fingerprint_cache_size': 0
        }
        
        logger.info("DeduplicationEngine initialized successfully")
    
    async def analyze_content(
        self,
        content_data: bytes,
        content_id: str,
        content_type: str = "application/octet-stream",
        metadata: Optional[Dict[str, Any]] = None
    ) -> DuplicationResult:
        """        Analyze content for deduplication opportunities.
        
        Business Flow:
        1. Generate content fingerprints
        2. Check for exact duplicates
        3. Analyze near-duplicates if enabled
        4. Detect content variants
        5. Update indexes and metrics
        """        start_time = time.time()
        
        try:
            # Generate fingerprints for the content
            fingerprints = await self._generate_fingerprints(
                content_data, content_id, content_type
            )
            
            # Check for exact duplicates first
            exact_duplicate = await self._check_exact_duplicate(fingerprints)
            if exact_duplicate:
                processing_time = time.time() - start_time
                self._update_metrics('exact', len(content_data), processing_time)
                
                return DuplicationResult(
                    is_duplicate=True,
                    duplicate_type=DuplicateType.EXACT,
                    original_content_id=exact_duplicate,
                    similarity_score=1.0,
                    fingerprints=self._fingerprints_to_dict(fingerprints),
                    space_saved_bytes=len(content_data),
                    processing_time=processing_time,
                    metadata={'duplicate_detection_method': 'exact_hash'}
                )
            
            # Check for near-duplicates if enabled
            near_duplicate = None
            if self.config.enable_near_duplicate_detection:
                near_duplicate = await self._check_near_duplicate(fingerprints, content_type)
            
            if near_duplicate:
                processing_time = time.time() - start_time
                self._update_metrics('near_duplicate', len(content_data), processing_time)
                
                return DuplicationResult(
                    is_duplicate=True,
                    duplicate_type=DuplicateType.NEAR_DUPLICATE,
                    original_content_id=near_duplicate['content_id'],
                    similarity_score=near_duplicate['similarity'],
                    fingerprints=self._fingerprints_to_dict(fingerprints),
                    space_saved_bytes=int(len(content_data) * near_duplicate['similarity']),
                    processing_time=processing_time,
                    metadata={'duplicate_detection_method': 'similarity_analysis'}
                )
            
            # Check for variants if enabled
            variant = None
            if self.config.enable_variant_detection:
                variant = await self._check_content_variant(fingerprints, content_type)
            
            if variant:
                processing_time = time.time() - start_time
                self._update_metrics('variant', len(content_data), processing_time)
                
                return DuplicationResult(
                    is_duplicate=True,
                    duplicate_type=DuplicateType.VARIANT,
                    original_content_id=variant['content_id'],
                    similarity_score=variant['similarity'],
                    fingerprints=self._fingerprints_to_dict(fingerprints),
                    space_saved_bytes=int(len(content_data) * 0.5),  # Partial savings for variants
                    processing_time=processing_time,
                    metadata={'duplicate_detection_method': 'variant_analysis'}
                )
            
            # No duplicates found - store fingerprints for future comparisons
            await self._store_fingerprints(fingerprints)
            
            processing_time = time.time() - start_time
            self._update_metrics('unique', len(content_data), processing_time)
            
            return DuplicationResult(
                is_duplicate=False,
                fingerprints=self._fingerprints_to_dict(fingerprints),
                processing_time=processing_time,
                metadata={'duplicate_detection_method': 'comprehensive_analysis'}
            )
            
        except Exception as e:
            logger.error(f"Deduplication analysis failed for {content_id}: {str(e)}")
            return DuplicationResult(
                is_duplicate=False,
                processing_time=time.time() - start_time,
                metadata={'error': str(e)}
            )
    
    async def analyze_batch(
        self,
        content_items: List[Dict[str, Any]],
        max_concurrent: int = 5
    ) -> List[DuplicationResult]:
        """Analyze multiple content items for deduplication"""        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def analyze_single(item):
            async with semaphore:
                return await self.analyze_content(
                    item['data'],
                    item['content_id'],
                    item.get('content_type', 'application/octet-stream'),
                    item.get('metadata')
                )
        
        tasks = [analyze_single(item) for item in content_items]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [
            result if isinstance(result, DuplicationResult)
            else DuplicationResult(
                is_duplicate=False,
                metadata={'error': str(result)}
            )
            for result in results
        ]
    
    async def get_duplicate_groups(self) -> Dict[str, List[str]]:
        """Get groups of duplicate content"""        duplicate_groups = defaultdict(list)
        
        # Group by exact hash
        hash_groups = defaultdict(list)
        for content_id, fingerprint in self.fingerprints.items():
            hash_groups[fingerprint.sha256_hash].append(content_id)
        
        # Find groups with multiple items
        for hash_value, content_ids in hash_groups.items():
            if len(content_ids) > 1:
                # Use first content as the group key
                group_key = content_ids[0]
                duplicate_groups[group_key] = content_ids[1:]
        
        return dict(duplicate_groups)
    
    async def optimize_storage(self) -> Dict[str, Any]:
        """Optimize storage by consolidating duplicates"""        optimization_results = {
            'duplicate_groups_processed': 0,
            'total_space_saved_mb': 0.0,
            'files_deduplicated': 0,
            'optimization_time': 0.0
        }
        
        start_time = time.time()
        
        try:
            duplicate_groups = await self.get_duplicate_groups()
            
            for original_id, duplicate_ids in duplicate_groups.items():
                # Update reference counts
                original_fingerprint = self.fingerprints[original_id]
                original_fingerprint.reference_count += len(duplicate_ids)
                
                # Calculate space savings
                total_size = sum(
                    self.fingerprints[dup_id].file_size 
                    for dup_id in duplicate_ids
                )
                
                optimization_results['total_space_saved_mb'] += total_size / (1024 * 1024)
                optimization_results['files_deduplicated'] += len(duplicate_ids)
                
                # Remove duplicate fingerprints
                for dup_id in duplicate_ids:
                    if dup_id in self.fingerprints:
                        del self.fingerprints[dup_id]
                
                optimization_results['duplicate_groups_processed'] += 1
            
            # Update indexes
            await self._rebuild_indexes()
            
            optimization_results['optimization_time'] = time.time() - start_time
            
            logger.info(
                f"Storage optimization completed: "
                f"{optimization_results['files_deduplicated']} files deduplicated, "
                f"{optimization_results['total_space_saved_mb']:.2f} MB saved"
            )
            
            return optimization_results
            
        except Exception as e:
            logger.error(f"Storage optimization failed: {str(e)}")
            return {
                **optimization_results,
                'error': str(e),
                'optimization_time': time.time() - start_time
            }
    
    # Private methods for fingerprint generation and analysis
    
    async def _generate_fingerprints(
        self,
        content_data: bytes,
        content_id: str,
        content_type: str
    ) -> ContentFingerprints:
        """Generate comprehensive fingerprints for content"""        
        # Basic cryptographic hashes
        sha256_hash = hashlib.sha256(content_data).hexdigest()
        md5_hash = hashlib.md5(content_data).hexdigest()
        
        # Initialize fingerprints object
        fingerprints = ContentFingerprints(
            content_id=content_id,
            sha256_hash=sha256_hash,
            md5_hash=md5_hash,
            content_type=content_type,
            file_size=len(content_data)
        )
        
        # Content-specific fingerprinting
        if content_type.startswith('image/') and self.config.enable_image_fingerprinting:
            fingerprints.perceptual_hash = self.image_fingerprinter.extract_perceptual_hash(content_data)
        
        elif content_type.startswith('audio/') and self.config.enable_audio_fingerprinting:
            audio_features = self.audio_fingerprinter.extract_audio_features(content_data)
            if audio_features:
                fingerprints.semantic_features = audio_features
        
        elif content_type.startswith('text/') and self.config.enable_text_similarity:
            try:
                text_content = content_data.decode('utf-8', errors='ignore')
                # Store normalized text hash as fuzzy hash
                normalized_text = self.text_analyzer._normalize_text(text_content)
                fingerprints.fuzzy_hash = hashlib.sha256(normalized_text.encode()).hexdigest()
            except Exception as e:
                logger.warning(f"Text fingerprinting failed: {str(e)}")
        
        return fingerprints
    
    async def _check_exact_duplicate(self, fingerprints: ContentFingerprints) -> Optional[str]:
        """Check for exact duplicate using cryptographic hashes"""        if not self.config.enable_exact_matching:
            return None
        
        # Check SHA256 first (most reliable)
        existing_content_id = self.sha256_index.get(fingerprints.sha256_hash)
        if existing_content_id:
            return existing_content_id
        
        # Fallback to MD5 if SHA256 not found
        existing_content_id = self.md5_index.get(fingerprints.md5_hash)
        if existing_content_id:
            return existing_content_id
        
        return None
    
    async def _check_near_duplicate(
        self,
        fingerprints: ContentFingerprints,
        content_type: str
    ) -> Optional[Dict[str, Any]]:
        """Check for near-duplicates using perceptual/semantic analysis"""        
        best_match = None
        best_similarity = 0.0
        
        for existing_id, existing_fp in self.fingerprints.items():
            if existing_fp.content_type != content_type:
                continue
            
            similarity = 0.0
            
            # Image similarity using perceptual hashes
            if (content_type.startswith('image/') and 
                fingerprints.perceptual_hash and existing_fp.perceptual_hash):
                
                similarity = self.image_fingerprinter.calculate_image_similarity(
                    fingerprints.perceptual_hash,
                    existing_fp.perceptual_hash
                )
            
            # Audio similarity using feature vectors
            elif (content_type.startswith('audio/') and 
                  fingerprints.semantic_features and existing_fp.semantic_features):
                
                similarity = self.audio_fingerprinter.calculate_audio_similarity(
                    fingerprints.semantic_features,
                    existing_fp.semantic_features
                )
            
            # Text similarity using fuzzy matching
            elif (content_type.startswith('text/') and 
                  fingerprints.fuzzy_hash and existing_fp.fuzzy_hash):
                
                # Use hash comparison as a fast similarity check
                if fingerprints.fuzzy_hash == existing_fp.fuzzy_hash:
                    similarity = 1.0
                else:
                    # Could implement more sophisticated text similarity here
                    similarity = 0.0
            
            # Update best match if similarity exceeds threshold
            if similarity >= self.config.similarity_threshold and similarity > best_similarity:
                best_similarity = similarity
                best_match = {
                    'content_id': existing_id,
                    'similarity': similarity
                }
        
        return best_match
    
    async def _check_content_variant(
        self,
        fingerprints: ContentFingerprints,
        content_type: str
    ) -> Optional[Dict[str, Any]]:
        """Check for content variants (same content, different format)"""        
        # Check for variants by comparing base content characteristics
        # This is a simplified implementation - could be enhanced with more sophisticated analysis
        
        for existing_id, existing_fp in self.fingerprints.items():
            # Skip same content type
            if existing_fp.content_type == content_type:
                continue
            
            # Check if file sizes are similar (within 20%)
            size_ratio = min(fingerprints.file_size, existing_fp.file_size) / max(fingerprints.file_size, existing_fp.file_size)
            
            if size_ratio >= 0.8:  # Files are similar in size
                # Additional checks could be added here for format conversion detection
                return {
                    'content_id': existing_id,
                    'similarity': size_ratio
                }
        
        return None
    
    async def _store_fingerprints(self, fingerprints: ContentFingerprints) -> None:
        """Store fingerprints and update indexes"""        # Store fingerprints
        self.fingerprints[fingerprints.content_id] = fingerprints
        
        # Update indexes
        self.sha256_index[fingerprints.sha256_hash] = fingerprints.content_id
        self.md5_index[fingerprints.md5_hash] = fingerprints.content_id
        
        if fingerprints.perceptual_hash:
            self.perceptual_index[fingerprints.perceptual_hash] = fingerprints.content_id
        
        # Update cache size metric
        self.metrics['fingerprint_cache_size'] = len(self.fingerprints)
    
    async def _rebuild_indexes(self) -> None:
        """Rebuild all indexes after optimization"""        self.sha256_index.clear()
        self.md5_index.clear()
        self.perceptual_index.clear()
        
        for content_id, fingerprints in self.fingerprints.items():
            self.sha256_index[fingerprints.sha256_hash] = content_id
            self.md5_index[fingerprints.md5_hash] = content_id
            
            if fingerprints.perceptual_hash:
                self.perceptual_index[fingerprints.perceptual_hash] = content_id
    
    def _fingerprints_to_dict(self, fingerprints: ContentFingerprints) -> Dict[str, str]:
        """Convert fingerprints object to dictionary"""        return {
            'sha256': fingerprints.sha256_hash,
            'md5': fingerprints.md5_hash,
            'perceptual': fingerprints.perceptual_hash or '',
            'fuzzy': fingerprints.fuzzy_hash or '',
            'content_type': fingerprints.content_type
        }
    
    def _update_metrics(
        self,
        result_type: str,
        data_size: int,
        processing_time: float
    ) -> None:
        """Update deduplication metrics"""        self.metrics['total_analyses'] += 1
        
        if result_type == 'exact':
            self.metrics['exact_duplicates_found'] += 1
            self.metrics['total_space_saved_mb'] += data_size / (1024 * 1024)
        elif result_type == 'near_duplicate':
            self.metrics['near_duplicates_found'] += 1
            self.metrics['total_space_saved_mb'] += (data_size * 0.8) / (1024 * 1024)
        elif result_type == 'variant':
            self.metrics['variants_found'] += 1
            self.metrics['total_space_saved_mb'] += (data_size * 0.3) / (1024 * 1024)
        
        # Update average processing time
        count = self.metrics['total_analyses']
        old_avg = self.metrics['average_processing_time']
        self.metrics['average_processing_time'] = (
            (old_avg * (count - 1) + processing_time) / count
        )
    
    def get_deduplication_statistics(self) -> Dict[str, Any]:
        """Get comprehensive deduplication statistics"""        total_duplicates = (
            self.metrics['exact_duplicates_found'] +
            self.metrics['near_duplicates_found'] +
            self.metrics['variants_found']
        )
        
        duplication_rate = 0.0
        if self.metrics['total_analyses'] > 0:
            duplication_rate = total_duplicates / self.metrics['total_analyses']
        
        return {
            'total_analyses': self.metrics['total_analyses'],
            'exact_duplicates_found': self.metrics['exact_duplicates_found'],
            'near_duplicates_found': self.metrics['near_duplicates_found'],
            'variants_found': self.metrics['variants_found'],
            'total_duplicates': total_duplicates,
            'duplication_rate_percent': round(duplication_rate * 100, 2),
            'total_space_saved_mb': round(self.metrics['total_space_saved_mb'], 2),
            'average_processing_time_ms': round(self.metrics['average_processing_time'] * 1000, 2),
            'fingerprint_cache_size': self.metrics['fingerprint_cache_size'],
            'index_sizes': {
                'sha256_index': len(self.sha256_index),
                'md5_index': len(self.md5_index),
                'perceptual_index': len(self.perceptual_index)
            }
        }
    
    async def check_duplicate(self, content_hash: str) -> Optional[Dict[str, Any]]:
        """Quick check if content with given hash already exists"""        existing_content_id = self.sha256_index.get(content_hash)
        if existing_content_id and existing_content_id in self.fingerprints:
            fingerprints = self.fingerprints[existing_content_id]
            return {
                'content_id': existing_content_id,
                'fingerprints': self._fingerprints_to_dict(fingerprints),
                'reference_count': fingerprints.reference_count,
                'created_at': fingerprints.created_at.isoformat()
            }
        return None

# Export main classes
__all__ = [
    'DeduplicationEngine',
    'DuplicateType',
    'ContentFingerprint',
    'DuplicationResult',
    'DeduplicationConfig',
    'AudioFingerprinter',
    'ImageFingerprinter',
    'TextSimilarityAnalyzer'
]
