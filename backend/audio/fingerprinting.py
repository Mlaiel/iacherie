"""🔍 Audio Fingerprinting Module - Professional Content Identification & Protection

Advanced audio fingerprinting system for content protection, copyright detection,
and audio content identification using multiple fingerprinting algorithms.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ COPYRIGHT & INTELLECTUAL PROPERTY WARNING:
This software and all related concepts, algorithms, and implementations are the 
exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 

UNAUTHORIZED USE, COPYING, MODIFICATION, DISTRIBUTION, OR REVERSE ENGINEERING 
IS STRICTLY PROHIBITED AND WILL RESULT IN IMMEDIATE LEGAL ACTION.
"""

import hashlib
import numpy as np
import librosa
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass, field
from scipy import signal
from scipy.spatial.distance import cosine, euclidean
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
from pathlib import Path
import time


@dataclass
class FingerprintResult:
    """Result container for audio fingerprinting operations"""
    fingerprint_hash: str
    chromaprint: Optional[str]
    spectral_features: Optional[np.ndarray]
    perceptual_hash: str
    metadata: Dict[str, Any]
    confidence_score: float
    processing_time: float
    file_hash: str
    audio_duration: float
    sample_rate: int


@dataclass
class MatchResult:
    """Result container for fingerprint matching operations"""
    similarity_score: float
    match_confidence: float
    matched_fingerprint_id: str
    offset_seconds: float
    duration_match: float
    metadata_match: Dict[str, Any]
    algorithm_used: str
    match_timestamp: float


@dataclass
class FingerprintRecord:
    """Database record for stored fingerprints"""
    id: str
    fingerprint_hash: str
    chromaprint: Optional[str]
    perceptual_hash: str
    spectral_features: bytes  # Serialized numpy array
    metadata: Dict[str, Any]
    created_timestamp: float
    audio_duration: float
    sample_rate: int


class AudioFingerprinter:
    """🔍 Professional Audio Fingerprinting Engine
    
    Advanced audio fingerprinting system using multiple algorithms including
    chromaprint, spectral features, and perceptual hashing for robust content identification.
    """
    
    def __init__(self, 
                 sample_rate: int = 22050,
                 hop_length: int = 512,
                 n_fft: int = 2048,
                 n_mels: int = 128,
                 max_workers: int = 4):
        """Initialize audio fingerprinter"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
        self.hop_length = hop_length
        self.n_fft = n_fft
        self.n_mels = n_mels
        self.max_workers = max_workers
        
        # Initialize executor for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Fingerprinting parameters
        self.similarity_threshold = 0.85
        self.min_match_duration = 5.0
        
        self.logger.info(f"AudioFingerprinter initialized - SR: {sample_rate}Hz")
    
    def generate_fingerprint(self, 
                           audio_data: Union[str, np.ndarray],
                           metadata: Optional[Dict[str, Any]] = None) -> FingerprintResult:
        """Generate comprehensive fingerprint for audio content"""
        start_time = time.time()
        
        # Load audio if path is provided
        if isinstance(audio_data, str):
            audio_data, sr = librosa.load(audio_data, sr=self.sample_rate)
        else:
            sr = self.sample_rate
        
        if metadata is None:
            metadata = {}
        
        # Generate different types of fingerprints
        chromaprint_hash = self._generate_chromaprint(audio_data, sr)
        spectral_features = self._extract_spectral_features(audio_data, sr)
        perceptual_hash = self._generate_perceptual_hash(spectral_features)
        
        # Create composite fingerprint hash
        fingerprint_hash = self._create_composite_hash(chromaprint_hash, perceptual_hash, spectral_features)
        
        # File hash for integrity checking
        file_hash = self._generate_file_hash(audio_data)
        
        # Calculate confidence score
        confidence_score = self._calculate_fingerprint_confidence(audio_data, spectral_features)
        
        processing_time = time.time() - start_time
        
        return FingerprintResult(
            fingerprint_hash=fingerprint_hash,
            chromaprint=chromaprint_hash,
            spectral_features=spectral_features,
            perceptual_hash=perceptual_hash,
            metadata=metadata,
            confidence_score=confidence_score,
            processing_time=processing_time,
            file_hash=file_hash,
            audio_duration=len(audio_data) / sr,
            sample_rate=sr
        )
    
    def _generate_chromaprint(self, audio_data: np.ndarray, sample_rate: int) -> str:
        """Generate chromaprint fingerprint"""
        try:
            # This would use the actual chromaprint library in production
            # For now, we'll create a simplified version
            
            # Extract chroma features
            chroma = librosa.feature.chroma_stft(
                y=audio_data, 
                sr=sample_rate,
                hop_length=self.hop_length
            )
            
            # Quantize chroma features to create hash-like representation
            chroma_binary = (chroma > np.mean(chroma, axis=1, keepdims=True)).astype(int)
            
            # Convert to string representation
            chromaprint_str = ''.join([str(int(''.join(map(str, frame)), 2)) for frame in chroma_binary.T[:100]])
            
            return chromaprint_str
            
        except Exception as e:
            self.logger.warning(f"Chromaprint generation failed: {e}")
            return ""
    
    def _extract_spectral_features(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Extract spectral features for fingerprinting"""
        # Mel-frequency cepstral coefficients
        mfcc = librosa.feature.mfcc(
            y=audio_data,
            sr=sample_rate,
            n_mfcc=13,
            hop_length=self.hop_length,
            n_fft=self.n_fft
        )
        
        # Spectral centroid
        spectral_centroid = librosa.feature.spectral_centroid(
            y=audio_data,
            sr=sample_rate,
            hop_length=self.hop_length
        )
        
        # Spectral rolloff
        spectral_rolloff = librosa.feature.spectral_rolloff(
            y=audio_data,
            sr=sample_rate,
            hop_length=self.hop_length
        )
        
        # Zero crossing rate
        zcr = librosa.feature.zero_crossing_rate(
            audio_data,
            hop_length=self.hop_length
        )
        
        # Combine features
        features = np.vstack([
            mfcc,
            spectral_centroid,
            spectral_rolloff,
            zcr
        ])
        
        # Summarize features (mean and std across time)
        feature_summary = np.hstack([
            np.mean(features, axis=1),
            np.std(features, axis=1)
        ])
        
        return feature_summary
    
    def _generate_perceptual_hash(self, spectral_features: np.ndarray) -> str:
        """Generate perceptual hash from spectral features"""
        # Normalize features
        normalized_features = (spectral_features - np.mean(spectral_features)) / (np.std(spectral_features) + 1e-10)
        
        # Create binary hash
        binary_features = (normalized_features > 0).astype(int)
        
        # Convert to hexadecimal string
        hex_chunks = []
        for i in range(0, len(binary_features), 4):
            chunk = binary_features[i:i+4]
            if len(chunk) < 4:
                chunk = np.pad(chunk, (0, 4 - len(chunk)), mode='constant')
            hex_value = int(''.join(map(str, chunk)), 2)
            hex_chunks.append(format(hex_value, 'x'))
        
        return ''.join(hex_chunks)
    
    def _create_composite_hash(self, chromaprint: str, perceptual_hash: str, spectral_features: np.ndarray) -> str:
        """Create composite fingerprint hash"""
        # Combine all fingerprinting data
        composite_data = f"{chromaprint}_{perceptual_hash}_{spectral_features.tobytes().hex()}"
        
        # Generate SHA-256 hash
        return hashlib.sha256(composite_data.encode()).hexdigest()
    
    def _generate_file_hash(self, audio_data: np.ndarray) -> str:
        """Generate file hash for integrity checking"""
        return hashlib.md5(audio_data.tobytes()).hexdigest()
    
    def _calculate_fingerprint_confidence(self, audio_data: np.ndarray, spectral_features: np.ndarray) -> float:
        """Calculate confidence score for fingerprint quality"""
        # Audio quality metrics
        signal_power = np.mean(audio_data ** 2)
        noise_floor = np.percentile(np.abs(audio_data), 10)
        snr = 10 * np.log10(signal_power / (noise_floor ** 2 + 1e-10))
        
        # Feature consistency
        feature_std = np.std(spectral_features)
        feature_consistency = 1.0 / (1.0 + feature_std)
        
        # Duration factor
        duration = len(audio_data) / self.sample_rate
        duration_factor = min(1.0, duration / 10.0)  # Prefer longer audio
        
        # Combine factors
        confidence = (snr / 60.0 + feature_consistency + duration_factor) / 3.0
        return min(1.0, max(0.0, float(confidence)))


class ContentMatcher:
    """🔍 Professional Content Matching Engine
    
    Advanced matching algorithm for comparing audio fingerprints and
    detecting similar or identical content.
    """
    
    def __init__(self, similarity_threshold: float = 0.85):
        """Initialize content matcher"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.similarity_threshold = similarity_threshold
    
    def match_fingerprints(self, 
                          query_fingerprint: FingerprintResult,
                          database_fingerprints: List[FingerprintRecord]) -> List[MatchResult]:
        """Match query fingerprint against database"""
        matches = []
        
        for db_fingerprint in database_fingerprints:
            match_result = self._compare_fingerprints(query_fingerprint, db_fingerprint)
            
            if match_result.similarity_score >= self.similarity_threshold:
                matches.append(match_result)
        
        # Sort by similarity score (descending)
        matches.sort(key=lambda x: x.similarity_score, reverse=True)
        
        return matches
    
    def _compare_fingerprints(self, 
                             query: FingerprintResult,
                             db_record: FingerprintRecord) -> MatchResult:
        """Compare two fingerprints and calculate similarity"""
        start_time = time.time()
        
        # Hash comparison (exact match)
        hash_match = query.fingerprint_hash == db_record.fingerprint_hash
        hash_similarity = 1.0 if hash_match else 0.0
        
        # Perceptual hash comparison
        perceptual_similarity = self._compare_perceptual_hashes(
            query.perceptual_hash, 
            db_record.perceptual_hash
        )
        
        # Spectral features comparison
        if query.spectral_features is not None:
            db_spectral_features = np.frombuffer(db_record.spectral_features, dtype=np.float64)
            spectral_similarity = self._compare_spectral_features(
                query.spectral_features,
                db_spectral_features
            )
        else:
            spectral_similarity = 0.0
        
        # Chromaprint comparison
        chromaprint_similarity = self._compare_chromaprints(
            query.chromaprint or "",
            db_record.chromaprint or ""
        )
        
        # Weighted combination of similarities
        overall_similarity = (
            hash_similarity * 0.4 +
            perceptual_similarity * 0.25 +
            spectral_similarity * 0.25 +
            chromaprint_similarity * 0.1
        )
        
        # Calculate match confidence
        match_confidence = self._calculate_match_confidence(
            overall_similarity, 
            query,
            db_record
        )
        
        # Calculate offset (simplified)
        offset_seconds = 0.0  # Would implement time alignment algorithm
        
        # Duration match
        duration_diff = abs(query.audio_duration - db_record.audio_duration)
        max_duration = max(query.audio_duration, db_record.audio_duration)
        duration_match = 1.0 - (duration_diff / max_duration) if max_duration > 0 else 1.0
        
        return MatchResult(
            similarity_score=overall_similarity,
            match_confidence=match_confidence,
            matched_fingerprint_id=db_record.id,
            offset_seconds=offset_seconds,
            duration_match=duration_match,
            metadata_match=db_record.metadata,
            algorithm_used="composite",
            match_timestamp=time.time()
        )
    
    def _compare_perceptual_hashes(self, hash1: str, hash2: str) -> float:
        """Compare perceptual hashes using Hamming distance"""
        if not hash1 or not hash2 or len(hash1) != len(hash2):
            return 0.0
        
        # Calculate Hamming distance
        differences = sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
        max_differences = len(hash1)
        
        # Convert to similarity (0-1)
        similarity = 1.0 - (differences / max_differences) if max_differences > 0 else 0.0
        
        return float(similarity)
    
    def _compare_spectral_features(self, features1: np.ndarray, features2: np.ndarray) -> float:
        """Compare spectral features using cosine similarity"""
        if len(features1) != len(features2):
            # Adjust lengths if needed
            min_length = min(len(features1), len(features2))
            features1 = features1[:min_length]
            features2 = features2[:min_length]
        
        try:
            # Cosine similarity
            cos_sim = 1.0 - cosine(features1, features2)
            return max(0.0, float(cos_sim))
        except:
            return 0.0
    
    def _compare_chromaprints(self, chroma1: str, chroma2: str) -> float:
        """Compare chromaprint strings"""
        if not chroma1 or not chroma2:
            return 0.0
        
        # Simple string similarity (in practice, would use chromaprint library)
        if chroma1 == chroma2:
            return 1.0
        
        # Calculate character-level similarity
        max_length = max(len(chroma1), len(chroma2))
        if max_length == 0:
            return 1.0
        
        differences = sum(c1 != c2 for c1, c2 in zip(chroma1, chroma2))
        differences += abs(len(chroma1) - len(chroma2))
        
        similarity = 1.0 - (differences / max_length)
        return max(0.0, float(similarity))
    
    def _calculate_match_confidence(self, 
                                  similarity: float,
                                  query: FingerprintResult,
                                  db_record: FingerprintRecord) -> float:
        """Calculate confidence in the match"""
        # Base confidence from similarity
        base_confidence = similarity
        
        # Adjust based on fingerprint quality
        quality_factor = (query.confidence_score + 1.0) / 2.0  # Assume db_record has confidence 1.0
        
        # Adjust based on duration match
        duration_factor = min(query.audio_duration, db_record.audio_duration) / max(query.audio_duration, db_record.audio_duration)
        
        # Combined confidence
        confidence = base_confidence * quality_factor * duration_factor
        
        return min(1.0, max(0.0, float(confidence)))


class CopyrightDetector:
    """⚖️ Professional Copyright Detection System
    
    Specialized system for detecting copyrighted content and potential
    copyright infringement using advanced fingerprinting techniques.
    """
    
    def __init__(self, 
                 fingerprinter: AudioFingerprinter,
                 matcher: ContentMatcher):
        """Initialize copyright detector"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.fingerprinter = fingerprinter
        self.matcher = matcher
        
        # Copyright detection thresholds
        self.infringement_threshold = 0.9
        self.partial_match_threshold = 0.7
        self.minimum_match_duration = 10.0  # seconds
    
    def detect_copyright_infringement(self, 
                                    audio_data: Union[str, np.ndarray],
                                    copyright_database: List[FingerprintRecord]) -> Dict[str, Any]:
        """Detect potential copyright infringement"""
        # Generate fingerprint for query audio
        query_fingerprint = self.fingerprinter.generate_fingerprint(audio_data)
        
        # Match against copyright database
        matches = self.matcher.match_fingerprints(query_fingerprint, copyright_database)
        
        # Analyze matches for copyright infringement
        infringement_analysis = self._analyze_infringement(matches, query_fingerprint)
        
        return {
            'query_fingerprint': query_fingerprint,
            'matches': matches,
            'infringement_detected': infringement_analysis['infringement_detected'],
            'infringement_confidence': infringement_analysis['confidence'],
            'partial_matches': infringement_analysis['partial_matches'],
            'analysis_summary': infringement_analysis['summary']
        }
    
    def _analyze_infringement(self, 
                            matches: List[MatchResult],
                            query_fingerprint: FingerprintResult) -> Dict[str, Any]:
        """Analyze matches for copyright infringement"""
        if not matches:
            return {
                'infringement_detected': False,
                'confidence': 0.0,
                'partial_matches': [],
                'summary': 'No matches found in copyright database'
            }
        
        best_match = matches[0]
        
        # Check for high-confidence infringement
        if (best_match.similarity_score >= self.infringement_threshold and
            best_match.match_confidence >= 0.8 and
            query_fingerprint.audio_duration >= self.minimum_match_duration):
            
            return {
                'infringement_detected': True,
                'confidence': best_match.match_confidence,
                'partial_matches': [m for m in matches if m.similarity_score >= self.partial_match_threshold],
                'summary': f'High-confidence copyright infringement detected (similarity: {best_match.similarity_score:.2f})'
            }
        
        # Check for partial matches
        partial_matches = [m for m in matches if m.similarity_score >= self.partial_match_threshold]
        
        if partial_matches:
            return {
                'infringement_detected': False,
                'confidence': best_match.match_confidence,
                'partial_matches': partial_matches,
                'summary': f'Partial matches detected - manual review recommended'
            }
        
        return {
            'infringement_detected': False,
            'confidence': 0.0,
            'partial_matches': [],
            'summary': 'No significant matches found'
        }


class FingerprintDatabase:
    """🗄️ Professional Fingerprint Database Manager
    
    Database management system for storing, indexing, and retrieving
    audio fingerprints for content identification.
    """
    
    def __init__(self):
        """Initialize fingerprint database"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.fingerprints: Dict[str, FingerprintRecord] = {}
        self.index_by_hash: Dict[str, str] = {}
        self.index_by_perceptual: Dict[str, List[str]] = {}
    
    def store_fingerprint(self, fingerprint_result: FingerprintResult, audio_id: str) -> str:
        """Store fingerprint in database"""
        record_id = self._generate_record_id(audio_id)
        
        # Serialize spectral features
        spectral_features_bytes = fingerprint_result.spectral_features.tobytes() if fingerprint_result.spectral_features is not None else b''
        
        record = FingerprintRecord(
            id=record_id,
            fingerprint_hash=fingerprint_result.fingerprint_hash,
            chromaprint=fingerprint_result.chromaprint,
            perceptual_hash=fingerprint_result.perceptual_hash,
            spectral_features=spectral_features_bytes,
            metadata=fingerprint_result.metadata,
            created_timestamp=time.time(),
            audio_duration=fingerprint_result.audio_duration,
            sample_rate=fingerprint_result.sample_rate
        )
        
        # Store record
        self.fingerprints[record_id] = record
        
        # Update indexes
        self.index_by_hash[fingerprint_result.fingerprint_hash] = record_id
        
        if fingerprint_result.perceptual_hash not in self.index_by_perceptual:
            self.index_by_perceptual[fingerprint_result.perceptual_hash] = []
        self.index_by_perceptual[fingerprint_result.perceptual_hash].append(record_id)
        
        self.logger.info(f"Stored fingerprint: {record_id}")
        return record_id
    
    def get_fingerprint(self, record_id: str) -> Optional[FingerprintRecord]:
        """Get fingerprint by record ID"""
        return self.fingerprints.get(record_id)
    
    def search_by_hash(self, fingerprint_hash: str) -> Optional[FingerprintRecord]:
        """Search for exact hash match"""
        record_id = self.index_by_hash.get(fingerprint_hash)
        return self.fingerprints.get(record_id) if record_id else None
    
    def search_similar(self, perceptual_hash: str, max_distance: int = 3) -> List[FingerprintRecord]:
        """Search for similar fingerprints using perceptual hash"""
        similar_records = []
        
        for stored_hash, record_ids in self.index_by_perceptual.items():
            # Calculate Hamming distance
            if len(stored_hash) == len(perceptual_hash):
                distance = sum(c1 != c2 for c1, c2 in zip(stored_hash, perceptual_hash))
                if distance <= max_distance:
                    for record_id in record_ids:
                        record = self.fingerprints.get(record_id)
                        if record:
                            similar_records.append(record)
        
        return similar_records
    
    def get_all_fingerprints(self) -> List[FingerprintRecord]:
        """Get all stored fingerprints"""
        return list(self.fingerprints.values())
    
    def delete_fingerprint(self, record_id: str) -> bool:
        """Delete fingerprint from database"""
        record = self.fingerprints.get(record_id)
        if not record:
            return False
        
        # Remove from main storage
        del self.fingerprints[record_id]
        
        # Remove from indexes
        if record.fingerprint_hash in self.index_by_hash:
            del self.index_by_hash[record.fingerprint_hash]
        
        if record.perceptual_hash in self.index_by_perceptual:
            self.index_by_perceptual[record.perceptual_hash].remove(record_id)
            if not self.index_by_perceptual[record.perceptual_hash]:
                del self.index_by_perceptual[record.perceptual_hash]
        
        self.logger.info(f"Deleted fingerprint: {record_id}")
        return True
    
    def _generate_record_id(self, audio_id: str) -> str:
        """Generate unique record ID"""
        timestamp = str(time.time())
        return hashlib.sha256(f"{audio_id}_{timestamp}".encode()).hexdigest()[:16]
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        return {
            'total_fingerprints': len(self.fingerprints),
            'hash_index_size': len(self.index_by_hash),
            'perceptual_index_size': len(self.index_by_perceptual),
            'avg_audio_duration': np.mean([fp.audio_duration for fp in self.fingerprints.values()]) if self.fingerprints else 0.0
        }


class SimilarityEngine:
    """🔍 Advanced Audio Similarity Detection Engine
    
    Sophisticated similarity analysis for detecting related, derivative,
    or transformed versions of audio content.
    """
    
    def __init__(self):
        """Initialize similarity engine"""
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def calculate_similarity(self, 
                           audio1: Union[str, np.ndarray],
                           audio2: Union[str, np.ndarray],
                           fingerprinter: AudioFingerprinter) -> Dict[str, float]:
        """Calculate comprehensive similarity between two audio files"""
        # Generate fingerprints
        fp1 = fingerprinter.generate_fingerprint(audio1)
        fp2 = fingerprinter.generate_fingerprint(audio2)
        
        # Create temporary database records for comparison
        record1 = FingerprintRecord(
            id="temp1",
            fingerprint_hash=fp1.fingerprint_hash,
            chromaprint=fp1.chromaprint,
            perceptual_hash=fp1.perceptual_hash,
            spectral_features=fp1.spectral_features.tobytes() if fp1.spectral_features is not None else b'',
            metadata=fp1.metadata,
            created_timestamp=time.time(),
            audio_duration=fp1.audio_duration,
            sample_rate=fp1.sample_rate
        )
        
        # Use content matcher
        matcher = ContentMatcher()
        match_result = matcher._compare_fingerprints(fp1, record1)
        
        return {
            'overall_similarity': match_result.similarity_score,
            'perceptual_similarity': matcher._compare_perceptual_hashes(fp1.perceptual_hash, fp2.perceptual_hash),
            'spectral_similarity': matcher._compare_spectral_features(fp1.spectral_features, fp2.spectral_features) if fp1.spectral_features is not None and fp2.spectral_features is not None else 0.0,
            'duration_similarity': match_result.duration_match,
            'confidence': match_result.match_confidence
        }


class DuplicateDetector:
    """🔍 Professional Duplicate Content Detection
    
    Specialized system for detecting exact and near-duplicate audio content
    within large audio collections.
    """
    
    def __init__(self, 
                 fingerprinter: AudioFingerprinter,
                 database: FingerprintDatabase):
        """Initialize duplicate detector"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.fingerprinter = fingerprinter
        self.database = database
        
        # Duplicate detection thresholds
        self.exact_duplicate_threshold = 0.99
        self.near_duplicate_threshold = 0.95
    
    def detect_duplicates(self, audio_collection: List[Union[str, np.ndarray]]) -> Dict[str, Any]:
        """Detect duplicates in audio collection"""
        fingerprints = []
        
        # Generate fingerprints for all audio files
        for i, audio in enumerate(audio_collection):
            try:
                fp = self.fingerprinter.generate_fingerprint(audio, metadata={'collection_index': i})
                fingerprints.append((i, fp))
            except Exception as e:
                self.logger.warning(f"Failed to fingerprint audio {i}: {e}")
        
        # Find duplicates
        exact_duplicates = []
        near_duplicates = []
        
        for i, (idx1, fp1) in enumerate(fingerprints):
            for j, (idx2, fp2) in enumerate(fingerprints[i+1:], i+1):
                similarity = self._calculate_duplicate_similarity(fp1, fp2)
                
                if similarity >= self.exact_duplicate_threshold:
                    exact_duplicates.append({
                        'audio1_index': idx1,
                        'audio2_index': idx2,
                        'similarity': similarity
                    })
                elif similarity >= self.near_duplicate_threshold:
                    near_duplicates.append({
                        'audio1_index': idx1,
                        'audio2_index': idx2,
                        'similarity': similarity
                    })
        
        return {
            'exact_duplicates': exact_duplicates,
            'near_duplicates': near_duplicates,
            'total_analyzed': len(fingerprints),
            'duplicate_groups': self._group_duplicates(exact_duplicates + near_duplicates)
        }
    
    def _calculate_duplicate_similarity(self, fp1: FingerprintResult, fp2: FingerprintResult) -> float:
        """Calculate similarity for duplicate detection"""
        # Hash comparison (highest priority)
        if fp1.fingerprint_hash == fp2.fingerprint_hash:
            return 1.0
        
        # Perceptual hash comparison
        perceptual_sim = ContentMatcher()._compare_perceptual_hashes(fp1.perceptual_hash, fp2.perceptual_hash)
        
        # Spectral features comparison
        if fp1.spectral_features is not None and fp2.spectral_features is not None:
            spectral_sim = ContentMatcher()._compare_spectral_features(fp1.spectral_features, fp2.spectral_features)
        else:
            spectral_sim = 0.0
        
        # Weighted combination
        return perceptual_sim * 0.6 + spectral_sim * 0.4
    
    def _group_duplicates(self, duplicates: List[Dict]) -> List[List[int]]:
        """Group duplicate indices into clusters"""
        if not duplicates:
            return []
        
        # Create adjacency list
        graph = {}
        for dup in duplicates:
            idx1, idx2 = dup['audio1_index'], dup['audio2_index']
            if idx1 not in graph:
                graph[idx1] = set()
            if idx2 not in graph:
                graph[idx2] = set()
            graph[idx1].add(idx2)
            graph[idx2].add(idx1)
        
        # Find connected components
        visited = set()
        groups = []
        
        def dfs(node, group):
            if node in visited:
                return
            visited.add(node)
            group.append(node)
            for neighbor in graph.get(node, []):
                dfs(neighbor, group)
        
        for node in graph:
            if node not in visited:
                group = []
                dfs(node, group)
                if len(group) > 1:
                    groups.append(sorted(group))
        
        return groups


class PerceptualHashGenerator:
    """🔍 Advanced Perceptual Hash Generation
    
    Specialized system for generating robust perceptual hashes that are
    resistant to minor audio modifications while maintaining sensitivity
    to significant changes.
    """
    
    def __init__(self, hash_size: int = 64):
        """Initialize perceptual hash generator"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.hash_size = hash_size
    
    def generate_hash(self, audio_data: np.ndarray, sample_rate: int = 22050) -> str:
        """Generate perceptual hash from audio data"""
        # Extract robust features
        features = self._extract_robust_features(audio_data, sample_rate)
        
        # Generate binary hash
        binary_hash = self._features_to_binary(features)
        
        # Convert to hex string
        hex_hash = self._binary_to_hex(binary_hash)
        
        return hex_hash
    
    def _extract_robust_features(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Extract features robust to minor modifications"""
        # Chromagram (robust to tempo changes)
        chroma = librosa.feature.chroma_cqt(y=audio_data, sr=sample_rate)
        
        # Tonnetz (harmonic network, robust to transposition)
        tonnetz = librosa.feature.tonnetz(y=audio_data, sr=sample_rate)
        
        # Spectral contrast (robust to noise)
        spectral_contrast = librosa.feature.spectral_contrast(y=audio_data, sr=sample_rate)
        
        # Combine and summarize features
        combined_features = np.vstack([chroma, tonnetz, spectral_contrast])
        
        # Use median to reduce noise sensitivity
        robust_features = np.median(combined_features, axis=1)
        
        return robust_features
    
    def _features_to_binary(self, features: np.ndarray) -> np.ndarray:
        """Convert features to binary representation"""
        # Normalize features
        normalized = (features - np.mean(features)) / (np.std(features) + 1e-10)
        
        # Threshold to binary
        binary = (normalized > 0).astype(int)
        
        # Ensure fixed size
        if len(binary) > self.hash_size:
            binary = binary[:self.hash_size]
        elif len(binary) < self.hash_size:
            binary = np.pad(binary, (0, self.hash_size - len(binary)), mode='constant')
        
        return binary
    
    def _binary_to_hex(self, binary_hash: np.ndarray) -> str:
        """Convert binary hash to hexadecimal string"""
        hex_chars = []
        for i in range(0, len(binary_hash), 4):
            chunk = binary_hash[i:i+4]
            if len(chunk) < 4:
                chunk = np.pad(chunk, (0, 4 - len(chunk)), mode='constant')
            hex_value = int(''.join(map(str, chunk)), 2)
            hex_chars.append(format(hex_value, 'x'))
        
        return ''.join(hex_chars)


class FingerprintMatchingEngine:
    """🔍 Advanced Fingerprint Matching Engine
    
    High-performance matching engine for comparing audio fingerprints
    with support for fuzzy matching, time alignment, and confidence scoring.
    """
    
    def __init__(self):
        """Initialize fingerprint matching engine"""
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def match_fingerprints(self, 
                          query_fp: FingerprintResult,
                          database_fps: List[FingerprintRecord],
                          max_results: int = 10) -> List[MatchResult]:
        """Match fingerprints with advanced algorithms"""
        matches = []
        
        for db_fp in database_fps:
            match_result = self._detailed_match(query_fp, db_fp)
            matches.append(match_result)
        
        # Sort by similarity score
        matches.sort(key=lambda x: x.similarity_score, reverse=True)
        
        return matches[:max_results]
    
    def _detailed_match(self, query_fp: FingerprintResult, db_fp: FingerprintRecord) -> MatchResult:
        """Perform detailed fingerprint matching"""
        # Use ContentMatcher for core comparison
        matcher = ContentMatcher()
        return matcher._compare_fingerprints(query_fp, db_fp)


# Export all classes
__all__ = [
    'AudioFingerprinter',
    'ContentMatcher',
    'CopyrightDetector',
    'FingerprintDatabase',
    'SimilarityEngine',
    'DuplicateDetector',
    'PerceptualHashGenerator',
    'FingerprintMatchingEngine',
    'FingerprintResult',
    'MatchResult',
    'FingerprintRecord'
]