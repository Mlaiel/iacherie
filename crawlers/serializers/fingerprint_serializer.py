"""Fingerprint Serializer Module
=============================

Specialized serialization for AI fingerprinting data and similarity vectors.
Optimized for content fingerprinting, matching, and protection systems.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.
"""import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import json
import base64
import hashlib
import numpy as np
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)

class FingerprintType(Enum):
    """Types of content fingerprints."""    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    PERCEPTUAL = "perceptual"
    CRYPTOGRAPHIC = "cryptographic"
    COMPOSITE = "composite"

class FingerprintAlgorithm(Enum):
    """Fingerprinting algorithms."""    CHROMAPRINT = "chromaprint"
    PHASH = "phash"
    DHASH = "dhash"
    WHASH = "whash"
    IMAGEHASH = "imagehash"
    CLIP = "clip"
    BERT = "bert"
    SPECTRAL = "spectral"
    MFCC = "mfcc"
    DEEP_LEARNING = "deep_learning"
    SHA256 = "sha256"
    MD5 = "md5"

class SimilarityMetric(Enum):
    """Similarity measurement metrics."""    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    MANHATTAN = "manhattan"
    HAMMING = "hamming"
    JACCARD = "jaccard"
    PEARSON = "pearson"
    CUSTOM = "custom"

@dataclass
class FingerprintVector:
    """Fingerprint vector data."""    vector_id: str
    vector_data: Union[List[float], np.ndarray]
    vector_dimension: int
    vector_type: str = "dense"
    normalization: str = "l2"
    quantization: Optional[str] = None
    compression_ratio: float = 1.0

@dataclass
class SimilarityMatch:
    """Similarity match result."""    match_id: str
    target_fingerprint_id: str
    reference_fingerprint_id: str
    similarity_score: float
    similarity_metric: SimilarityMetric
    confidence_score: float
    match_details: Dict[str, Any] = field(default_factory=dict)
    detected_at: datetime = field(default_factory=datetime.now)

@dataclass
class FingerprintMetrics:
    """Fingerprint performance metrics."""    generation_time: float = 0.0
    vector_size_bytes: int = 0
    compression_ratio: float = 1.0
    extraction_confidence: float = 1.0
    quality_score: float = 0.0
    robustness_score: float = 0.0
    uniqueness_score: float = 0.0

class FingerprintData(BaseModel):
    """    Comprehensive fingerprint data model.
    
    Represents AI-generated fingerprints for content protection
    and similarity detection in the IA-Influencer-Agent platform.
    """    
    # Basic identification
    fingerprint_id: str = Field(..., description="Unique fingerprint identifier")
    content_id: str = Field(..., description="Associated content identifier")
    fingerprint_type: FingerprintType = Field(..., description="Type of fingerprint")
    algorithm: FingerprintAlgorithm = Field(..., description="Fingerprinting algorithm")
    
    # Fingerprint data
    fingerprint_hash: str = Field(..., description="Primary fingerprint hash")
    fingerprint_vectors: List[FingerprintVector] = Field(default_factory=list)
    raw_features: Optional[Dict[str, Any]] = Field(default=None)
    processed_features: Optional[Dict[str, Any]] = Field(default=None)
    
    # Content properties
    content_duration: Optional[float] = Field(default=None)
    content_size: int = Field(default=0)
    content_format: str = Field(default="unknown")
    content_quality: Optional[str] = Field(default=None)
    
    # Generation parameters
    algorithm_version: str = Field(default="1.0")
    algorithm_parameters: Dict[str, Any] = Field(default_factory=dict)
    sampling_rate: Optional[int] = Field(default=None)
    window_size: Optional[int] = Field(default=None)
    hop_length: Optional[int] = Field(default=None)
    
    # Quality metrics
    metrics: Optional[FingerprintMetrics] = Field(default=None)
    validation_passed: bool = Field(default=False)
    validation_errors: List[str] = Field(default_factory=list)
    
    # Similarity configuration
    similarity_threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    matching_enabled: bool = Field(default=True)
    protected: bool = Field(default=True)
    
    # Timestamps
    generated_at: datetime = Field(default_factory=datetime.now)
    last_matched: Optional[datetime] = Field(default=None)
    expires_at: Optional[datetime] = Field(default=None)
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    custom_data: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('fingerprint_type', pre=True)
    def validate_fingerprint_type(cls, v):
        if isinstance(v, str):
            return FingerprintType(v.lower())
        return v
    
    @validator('algorithm', pre=True)
    def validate_algorithm(cls, v):
        if isinstance(v, str):
            return FingerprintAlgorithm(v.lower())
        return v
    
    @validator('similarity_threshold')
    def validate_similarity_threshold(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError("Similarity threshold must be between 0.0 and 1.0")
        return v

class FingerprintSerializer:
    """    Advanced fingerprint serialization system.
    
    Handles efficient serialization and deserialization of AI fingerprints,
    similarity vectors, and matching results with optimization for storage and retrieval.
    """    
    def __init__(self):
        """Initialize fingerprint serializer."""        self.vector_compression_threshold = 1000  # Compress vectors larger than 1000 elements
        self.max_vector_dimension = 10000  # Maximum vector dimension
        
        logger.info("Fingerprint serializer initialized")
    
    def serialize_fingerprint(
        self,
        fingerprint: FingerprintData,
        compress_vectors: bool = True,
        include_raw_features: bool = False
    ) -> Dict[str, Any]:
        """        Serialize fingerprint data to dictionary format.
        
        Args:
            fingerprint: Fingerprint data to serialize
            compress_vectors: Whether to compress large vectors
            include_raw_features: Whether to include raw feature data
            
        Returns:
            Serialized fingerprint dictionary
        """        try:
            # Convert to dictionary
            data = fingerprint.dict()
            
            # Handle datetime conversions
            data['generated_at'] = fingerprint.generated_at.isoformat()
            if fingerprint.last_matched:
                data['last_matched'] = fingerprint.last_matched.isoformat()
            if fingerprint.expires_at:
                data['expires_at'] = fingerprint.expires_at.isoformat()
            
            # Serialize fingerprint vectors
            if fingerprint.fingerprint_vectors:
                data['fingerprint_vectors'] = [
                    self._serialize_fingerprint_vector(vector, compress_vectors)
                    for vector in fingerprint.fingerprint_vectors
                ]
            
            # Handle raw features
            if not include_raw_features:
                data.pop('raw_features', None)
            elif fingerprint.raw_features:
                data['raw_features'] = self._serialize_features(fingerprint.raw_features)
            
            # Serialize processed features
            if fingerprint.processed_features:
                data['processed_features'] = self._serialize_features(fingerprint.processed_features)
            
            # Serialize metrics
            if fingerprint.metrics:
                data['metrics'] = self._serialize_fingerprint_metrics(fingerprint.metrics)
            
            # Convert enums
            data['fingerprint_type'] = fingerprint.fingerprint_type.value
            data['algorithm'] = fingerprint.algorithm.value
            
            # Add serialization metadata
            data['_serialization'] = {
                'version': '2.0.0',
                'serialized_at': datetime.now().isoformat(),
                'vectors_compressed': compress_vectors,
                'includes_raw_features': include_raw_features,
                'fingerprint_type': fingerprint.fingerprint_type.value
            }
            
            logger.debug(f"Serialized fingerprint {fingerprint.fingerprint_id}")
            return data
            
        except Exception as e:
            logger.error(f"Fingerprint serialization failed: {e}")
            raise
    
    def deserialize_fingerprint(
        self,
        data: Dict[str, Any]
    ) -> FingerprintData:
        """        Deserialize fingerprint data from dictionary format.
        
        Args:
            data: Serialized fingerprint dictionary
            
        Returns:
            Deserialized FingerprintData object
        """        try:
            # Handle datetime conversions
            if isinstance(data.get('generated_at'), str):
                data['generated_at'] = datetime.fromisoformat(data['generated_at'])
            
            if isinstance(data.get('last_matched'), str):
                data['last_matched'] = datetime.fromisoformat(data['last_matched'])
            
            if isinstance(data.get('expires_at'), str):
                data['expires_at'] = datetime.fromisoformat(data['expires_at'])
            
            # Deserialize fingerprint vectors
            if 'fingerprint_vectors' in data and data['fingerprint_vectors']:
                data['fingerprint_vectors'] = [
                    self._deserialize_fingerprint_vector(vector_data)
                    for vector_data in data['fingerprint_vectors']
                ]
            
            # Deserialize features
            if 'raw_features' in data and data['raw_features']:
                data['raw_features'] = self._deserialize_features(data['raw_features'])
            
            if 'processed_features' in data and data['processed_features']:
                data['processed_features'] = self._deserialize_features(data['processed_features'])
            
            # Deserialize metrics
            if 'metrics' in data and data['metrics']:
                data['metrics'] = self._deserialize_fingerprint_metrics(data['metrics'])
            
            # Remove serialization metadata
            data.pop('_serialization', None)
            
            # Create FingerprintData object
            fingerprint = FingerprintData(**data)
            
            logger.debug(f"Deserialized fingerprint {fingerprint.fingerprint_id}")
            return fingerprint
            
        except Exception as e:
            logger.error(f"Fingerprint deserialization failed: {e}")
            raise
    
    def serialize_similarity_match(
        self,
        match: SimilarityMatch
    ) -> Dict[str, Any]:
        """Serialize similarity match result."""        try:
            data = {
                'match_id': match.match_id,
                'target_fingerprint_id': match.target_fingerprint_id,
                'reference_fingerprint_id': match.reference_fingerprint_id,
                'similarity_score': match.similarity_score,
                'similarity_metric': match.similarity_metric.value,
                'confidence_score': match.confidence_score,
                'match_details': match.match_details,
                'detected_at': match.detected_at.isoformat()
            }
            
            return data
            
        except Exception as e:
            logger.error(f"Similarity match serialization failed: {e}")
            raise
    
    def deserialize_similarity_match(
        self,
        data: Dict[str, Any]
    ) -> SimilarityMatch:
        """Deserialize similarity match result."""        try:
            if isinstance(data.get('detected_at'), str):
                data['detected_at'] = datetime.fromisoformat(data['detected_at'])
            
            if isinstance(data.get('similarity_metric'), str):
                data['similarity_metric'] = SimilarityMetric(data['similarity_metric'])
            
            return SimilarityMatch(**data)
            
        except Exception as e:
            logger.error(f"Similarity match deserialization failed: {e}")
            raise
    
    def serialize_fingerprint_batch(
        self,
        fingerprints: List[FingerprintData],
        compact_mode: bool = True
    ) -> List[Dict[str, Any]]:
        """Serialize multiple fingerprints efficiently."""        try:
            serialized_list = []
            
            for fingerprint in fingerprints:
                serialized = self.serialize_fingerprint(
                    fingerprint,
                    compress_vectors=compact_mode,
                    include_raw_features=not compact_mode
                )
                serialized_list.append(serialized)
            
            logger.info(f"Serialized {len(fingerprints)} fingerprints")
            return serialized_list
            
        except Exception as e:
            logger.error(f"Fingerprint batch serialization failed: {e}")
            raise
    
    def deserialize_fingerprint_batch(
        self,
        data_list: List[Dict[str, Any]]
    ) -> List[FingerprintData]:
        """Deserialize multiple fingerprints efficiently."""        try:
            fingerprints = []
            
            for data in data_list:
                fingerprint = self.deserialize_fingerprint(data)
                fingerprints.append(fingerprint)
            
            logger.info(f"Deserialized {len(data_list)} fingerprints")
            return fingerprints
            
        except Exception as e:
            logger.error(f"Fingerprint batch deserialization failed: {e}")
            raise
    
    def _serialize_fingerprint_vector(
        self,
        vector: FingerprintVector,
        compress: bool = True
    ) -> Dict[str, Any]:
        """Serialize fingerprint vector."""        try:
            data = {
                'vector_id': vector.vector_id,
                'vector_dimension': vector.vector_dimension,
                'vector_type': vector.vector_type,
                'normalization': vector.normalization,
                'quantization': vector.quantization,
                'compression_ratio': vector.compression_ratio
            }
            
            # Handle vector data serialization
            if isinstance(vector.vector_data, np.ndarray):
                vector_data = vector.vector_data.tolist()
            else:
                vector_data = list(vector.vector_data)
            
            # Compress large vectors
            if compress and len(vector_data) > self.vector_compression_threshold:
                data['vector_data'] = self._compress_vector(vector_data)
                data['_compressed'] = True
            else:
                data['vector_data'] = vector_data
                data['_compressed'] = False
            
            return data
            
        except Exception as e:
            logger.error(f"Vector serialization failed: {e}")
            raise
    
    def _deserialize_fingerprint_vector(
        self,
        data: Dict[str, Any]
    ) -> FingerprintVector:
        """Deserialize fingerprint vector."""        try:
            # Handle compressed vectors
            if data.get('_compressed', False):
                vector_data = self._decompress_vector(data['vector_data'])
            else:
                vector_data = data['vector_data']
            
            # Remove compression metadata
            data.pop('_compressed', None)
            data['vector_data'] = vector_data
            
            return FingerprintVector(**data)
            
        except Exception as e:
            logger.error(f"Vector deserialization failed: {e}")
            raise
    
    def _compress_vector(self, vector_data: List[float]) -> str:
        """Compress vector data using base64 encoding."""        try:
            import gzip
            
            # Convert to bytes
            vector_array = np.array(vector_data, dtype=np.float32)
            vector_bytes = vector_array.tobytes()
            
            # Compress
            compressed = gzip.compress(vector_bytes)
            
            # Encode to base64
            encoded = base64.b64encode(compressed).decode('utf-8')
            
            return f"gzip_float32:{encoded}"
            
        except Exception as e:
            logger.error(f"Vector compression failed: {e}")
            return str(vector_data)  # Return as string if compression fails
    
    def _decompress_vector(self, compressed_data: str) -> List[float]:
        """Decompress vector data from base64 encoding."""        try:
            import gzip
            
            if compressed_data.startswith('gzip_float32:'):
                # Remove prefix
                encoded = compressed_data[13:]
                
                # Decode from base64
                compressed = base64.b64decode(encoded)
                
                # Decompress
                vector_bytes = gzip.decompress(compressed)
                
                # Convert back to array
                vector_array = np.frombuffer(vector_bytes, dtype=np.float32)
                
                return vector_array.tolist()
            else:
                # Not compressed or unknown format
                return eval(compressed_data) if isinstance(compressed_data, str) else compressed_data
                
        except Exception as e:
            logger.error(f"Vector decompression failed: {e}")
            return []
    
    def _serialize_features(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize feature data with numpy array handling."""        try:
            serialized = {}
            
            for key, value in features.items():
                if isinstance(value, np.ndarray):
                    # Convert numpy arrays to lists
                    serialized[key] = {
                        '_type': 'numpy_array',
                        '_dtype': str(value.dtype),
                        '_shape': value.shape,
                        'data': value.tolist()
                    }
                elif isinstance(value, dict):
                    # Recursively serialize nested dictionaries
                    serialized[key] = self._serialize_features(value)
                else:
                    serialized[key] = value
            
            return serialized
            
        except Exception as e:
            logger.error(f"Features serialization failed: {e}")
            return features
    
    def _deserialize_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Deserialize feature data with numpy array reconstruction."""        try:
            deserialized = {}
            
            for key, value in data.items():
                if isinstance(value, dict) and value.get('_type') == 'numpy_array':
                    # Reconstruct numpy array
                    array_data = np.array(value['data'], dtype=value['_dtype'])
                    deserialized[key] = array_data.reshape(value['_shape'])
                elif isinstance(value, dict):
                    # Recursively deserialize nested dictionaries
                    deserialized[key] = self._deserialize_features(value)
                else:
                    deserialized[key] = value
            
            return deserialized
            
        except Exception as e:
            logger.error(f"Features deserialization failed: {e}")
            return data
    
    def _serialize_fingerprint_metrics(self, metrics: FingerprintMetrics) -> Dict[str, Any]:
        """Serialize fingerprint metrics."""        return {
            'generation_time': metrics.generation_time,
            'vector_size_bytes': metrics.vector_size_bytes,
            'compression_ratio': metrics.compression_ratio,
            'extraction_confidence': metrics.extraction_confidence,
            'quality_score': metrics.quality_score,
            'robustness_score': metrics.robustness_score,
            'uniqueness_score': metrics.uniqueness_score
        }
    
    def _deserialize_fingerprint_metrics(self, data: Dict[str, Any]) -> FingerprintMetrics:
        """Deserialize fingerprint metrics."""        return FingerprintMetrics(**data)
    
    def calculate_fingerprint_signature(self, fingerprint: FingerprintData) -> str:
        """Calculate unique signature for fingerprint verification."""        try:
            # Create signature from key fingerprint properties
            signature_data = {
                'fingerprint_id': fingerprint.fingerprint_id,
                'content_id': fingerprint.content_id,
                'fingerprint_hash': fingerprint.fingerprint_hash,
                'algorithm': fingerprint.algorithm.value,
                'generated_at': fingerprint.generated_at.isoformat()
            }
            
            # Add vector signatures if available
            if fingerprint.fingerprint_vectors:
                vector_signatures = []
                for vector in fingerprint.fingerprint_vectors:
                    if isinstance(vector.vector_data, (list, np.ndarray)):
                        # Create hash of vector data
                        vector_array = np.array(vector.vector_data)
                        vector_hash = hashlib.sha256(vector_array.tobytes()).hexdigest()
                        vector_signatures.append(vector_hash)
                signature_data['vector_signatures'] = vector_signatures
            
            # Create final signature
            signature_json = json.dumps(signature_data, sort_keys=True)
            signature = hashlib.sha256(signature_json.encode()).hexdigest()
            
            return signature
            
        except Exception as e:
            logger.error(f"Fingerprint signature calculation failed: {e}")
            return ""
    
    def validate_fingerprint_integrity(
        self,
        fingerprint: FingerprintData,
        expected_signature: Optional[str] = None
    ) -> bool:
        """Validate fingerprint data integrity."""        try:
            # Calculate current signature
            current_signature = self.calculate_fingerprint_signature(fingerprint)
            
            # Compare with expected signature if provided
            if expected_signature:
                return current_signature == expected_signature
            
            # Basic validation checks
            if not fingerprint.fingerprint_id or not fingerprint.content_id:
                return False
            
            if not fingerprint.fingerprint_hash:
                return False
            
            # Validate vectors if present
            for vector in fingerprint.fingerprint_vectors:
                if not vector.vector_id or not vector.vector_data:
                    return False
                
                if vector.vector_dimension != len(vector.vector_data):
                    return False
                
                if vector.vector_dimension > self.max_vector_dimension:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Fingerprint integrity validation failed: {e}")
            return False


# Export main classes
__all__ = [
    'FingerprintSerializer',
    'FingerprintData',
    'FingerprintVector',
    'SimilarityMatch',
    'FingerprintMetrics',
    'FingerprintType',
    'FingerprintAlgorithm',
    'SimilarityMetric'
]
