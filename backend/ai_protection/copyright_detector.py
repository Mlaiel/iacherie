"""Copyright Detector

AI-powered copyright violation detection system for multimedia content.
Detects unauthorized usage and copyright infringement across platforms.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
import hashlib
import json
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import uuid
import numpy as np

try:
    import librosa
    import cv2
    from PIL import Image
    from sentence_transformers import SentenceTransformer
    import torch
    DETECTION_AVAILABLE = True
except ImportError:
    DETECTION_AVAILABLE = False

# Import existing detection functionality
from ...core.fingerprinting import ContentFingerprint
from ...protection.monitoring import ViolationDetector

logger = logging.getLogger(__name__)


class ViolationType(Enum):
    """Types of copyright violations"""
    EXACT_MATCH = "exact_match"
    PARTIAL_MATCH = "partial_match"
    DERIVATIVE_WORK = "derivative_work"
    UNAUTHORIZED_USE = "unauthorized_use"
    PLAGIARISM = "plagiarism"
    FAIR_USE_VIOLATION = "fair_use_violation"


class DetectionAlgorithm(Enum):
    """Detection algorithms"""
    FINGERPRINT_MATCHING = "fingerprint_matching"
    PERCEPTUAL_HASHING = "perceptual_hashing"
    AUDIO_FINGERPRINTING = "audio_fingerprinting"
    VIDEO_ANALYSIS = "video_analysis"
    TEXT_SIMILARITY = "text_similarity"
    IMAGE_SIMILARITY = "image_similarity"


@dataclass
class CopyrightMatch:
    """Copyright violation match result"""
    match_id: str
    violation_type: ViolationType
    confidence: float
    similarity_score: float
    original_content_id: str
    detected_content_id: str
    detection_algorithm: DetectionAlgorithm
    match_metadata: Dict[str, Any]
    timestamp: datetime
    platform_info: Optional[Dict[str, Any]] = None


@dataclass
class DetectionResult:
    """Copyright detection result"""
    content_id: str
    violations_detected: bool
    total_matches: int
    matches: List[CopyrightMatch]
    processing_time: float
    detection_summary: Dict[str, Any]
    error: Optional[str] = None


class CopyrightDetector:
    """AI-powered copyright violation detection system"""
    
    def __init__(self, 
                 similarity_threshold -> None: float = 0.8,
                 enable_deep_learning -> None: bool = True) -> None:
        """
        Initialize copyright detector
        
        Args:
            similarity_threshold: Minimum similarity for violation detection
            enable_deep_learning: Enable deep learning models
        """
        self.similarity_threshold = similarity_threshold
        self.enable_deep_learning = enable_deep_learning
        
        # Initialize AI models if available
        self.text_model = None
        self.image_model = None
        
        if DETECTION_AVAILABLE and enable_deep_learning:
            try:
                self.text_model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Text similarity model loaded")
            except Exception as e:
                logger.warning(f"Failed to load text model: {e}")
                
        # Import existing violation detector
        self.violation_detector = ViolationDetector()
        
        # Content database for comparison
        self._content_database = {}
        self._fingerprint_database = {}
        
    async def register_original_content(self,
                                      content_id: str,
                                      content_data: Union[bytes, str],
                                      content_type: str,
                                      owner_id: str,
                                      metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Register original content for copyright protection
        
        Args:
            content_id: Unique content identifier
            content_data: Content data (bytes for media, string for text)
            content_type: Type of content (audio, video, image, text)
            owner_id: Content owner identifier
            metadata: Additional metadata
            
        Returns:
            Registration result
        """
        try:
            # Generate content fingerprint based on type
            fingerprint = await self._generate_content_fingerprint(
                content_data, content_type
            )
            
            # Store in content database
            content_record = {
                'content_id': content_id,
                'owner_id': owner_id,
                'content_type': content_type,
                'fingerprint': fingerprint,
                'registration_timestamp': datetime.now().isoformat(),
                'metadata': metadata or {}
            }
            
            self._content_database[content_id] = content_record
            self._fingerprint_database[fingerprint['hash']] = content_id
            
            return {
                'success': True,
                'content_id': content_id,
                'fingerprint_hash': fingerprint['hash'],
                'registration_timestamp': content_record['registration_timestamp']
            }
            
        except Exception as e:
            logger.error(f"Content registration failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def detect_violations(self,
                              suspected_content: Union[bytes, str],
                              content_type: str,
                              platform_info: Optional[Dict[str, Any]] = None) -> DetectionResult:
        """
        Detect copyright violations in suspected content
        
        Args:
            suspected_content: Content to analyze
            content_type: Type of content
            platform_info: Platform where content was found
            
        Returns:
            Detection result with violation matches
        """
        try:
            start_time = asyncio.get_event_loop().time()
            
            detection_id = str(uuid.uuid4())
            
            # Generate fingerprint for suspected content
            suspected_fingerprint = await self._generate_content_fingerprint(
                suspected_content, content_type
            )
            
            matches = []
            
            # Compare with registered content
            for original_content_id, original_record in self._content_database.items():
                if original_record['content_type'] == content_type:
                    # Calculate similarity
                    similarity = await self._calculate_similarity(
                        suspected_fingerprint,
                        original_record['fingerprint'],
                        content_type
                    )
                    
                    if similarity['score'] >= self.similarity_threshold:
                        # Determine violation type
                        violation_type = self._determine_violation_type(similarity)
                        
                        match = CopyrightMatch(
                            match_id=str(uuid.uuid4()),
                            violation_type=violation_type,
                            confidence=similarity['confidence'],
                            similarity_score=similarity['score'],
                            original_content_id=original_content_id,
                            detected_content_id=detection_id,
                            detection_algorithm=similarity['algorithm'],
                            match_metadata=similarity['metadata'],
                            timestamp=datetime.now(),
                            platform_info=platform_info
                        )
                        
                        matches.append(match)
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            # Generate detection summary
            summary = self._generate_detection_summary(matches)
            
            return DetectionResult(
                content_id=detection_id,
                violations_detected=len(matches) > 0,
                total_matches=len(matches),
                matches=matches,
                processing_time=processing_time,
                detection_summary=summary
            )
            
        except Exception as e:
            logger.error(f"Violation detection failed: {e}")
            return DetectionResult(
                content_id="",
                violations_detected=False,
                total_matches=0,
                matches=[],
                processing_time=0,
                detection_summary={},
                error=str(e)
            )
    
    async def batch_detect_violations(self,
                                    content_batch: List[Dict[str, Any]]) -> List[DetectionResult]:
        """
        Perform batch violation detection
        
        Args:
            content_batch: List of content items to analyze
            
        Returns:
            List of detection results
        """
        results = []
        
        # Process in parallel for efficiency
        tasks = []
        for content_item in content_batch:
            task = self.detect_violations(
                content_item['content'],
                content_item['content_type'],
                content_item.get('platform_info')
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                results[i] = DetectionResult(
                    content_id=f"batch_{i}",
                    violations_detected=False,
                    total_matches=0,
                    matches=[],
                    processing_time=0,
                    detection_summary={},
                    error=str(result)
                )
        
        return results
    
    async def analyze_platform_violations(self,
                                        platform_name: str,
                                        content_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze violations across a specific platform
        
        Args:
            platform_name: Name of the platform
            content_list: List of content found on platform
            
        Returns:
            Platform violation analysis
        """
        try:
            platform_results = await self.batch_detect_violations(content_list)
            
            # Aggregate results
            total_violations = sum(1 for r in platform_results if r.violations_detected)
            total_matches = sum(r.total_matches for r in platform_results)
            
            # Group by violation type
            violation_types = {}
            for result in platform_results:
                for match in result.matches:
                    violation_type = match.violation_type.value
                    if violation_type not in violation_types:
                        violation_types[violation_type] = 0
                    violation_types[violation_type] += 1
            
            # Calculate risk score
            risk_score = min((total_violations / len(content_list)) * 100, 100) if content_list else 0
            
            return {
                'platform': platform_name,
                'total_content_analyzed': len(content_list),
                'violations_detected': total_violations,
                'total_matches': total_matches,
                'violation_rate': (total_violations / len(content_list)) * 100 if content_list else 0,
                'risk_score': risk_score,
                'violation_types': violation_types,
                'detailed_results': platform_results,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Platform analysis failed: {e}")
            return {
                'platform': platform_name,
                'error': str(e),
                'analysis_timestamp': datetime.now().isoformat()
            }
    
    async def generate_takedown_notice(self,
                                     violation_match: CopyrightMatch,
                                     contact_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate DMCA takedown notice for violation
        
        Args:
            violation_match: Detected violation match
            contact_info: Contact information for notice
            
        Returns:
            Generated takedown notice
        """
        try:
            # Get original content info
            original_content = self._content_database.get(violation_match.original_content_id)
            
            if not original_content:
                raise ValueError("Original content not found")
            
            notice_id = str(uuid.uuid4())
            
            notice = {
                'notice_id': notice_id,
                'notice_type': 'DMCA_TAKEDOWN',
                'violation_details': {
                    'match_id': violation_match.match_id,
                    'violation_type': violation_match.violation_type.value,
                    'confidence': violation_match.confidence,
                    'similarity_score': violation_match.similarity_score,
                    'platform_info': violation_match.platform_info
                },
                'original_content': {
                    'content_id': original_content['content_id'],
                    'owner_id': original_content['owner_id'],
                    'content_type': original_content['content_type'],
                    'registration_date': original_content['registration_timestamp']
                },
                'copyright_holder': contact_info,
                'generated_timestamp': datetime.now().isoformat(),
                'legal_text': self._generate_dmca_text(violation_match, original_content, contact_info)
            }
            
            return {
                'success': True,
                'notice_id': notice_id,
                'notice': notice,
                'estimated_response_time': '7-14 days'
            }
            
        except Exception as e:
            logger.error(f"Takedown notice generation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _generate_content_fingerprint(self,
                                          content_data: Union[bytes, str],
                                          content_type: str) -> Dict[str, Any]:
        """Generate content fingerprint based on type"""
        try:
            if content_type == 'audio':
                return await self._generate_audio_fingerprint(content_data)
            elif content_type == 'video':
                return await self._generate_video_fingerprint(content_data)
            elif content_type == 'image':
                return await self._generate_image_fingerprint(content_data)
            elif content_type == 'text':
                return await self._generate_text_fingerprint(content_data)
            else:
                # Generic hash for other types
                content_bytes = content_data if isinstance(content_data, bytes) else content_data.encode()
                hash_value = hashlib.sha256(content_bytes).hexdigest()
                return {
                    'hash': hash_value,
                    'type': 'generic',
                    'features': []
                }
                
        except Exception as e:
            logger.error(f"Fingerprint generation failed: {e}")
            raise
    
    async def _generate_audio_fingerprint(self, audio_data: bytes) -> Dict[str, Any]:
        """Generate audio fingerprint using spectral features"""
        if not DETECTION_AVAILABLE:
            # Fallback to simple hash
            hash_value = hashlib.sha256(audio_data).hexdigest()
            return {'hash': hash_value, 'type': 'audio_hash', 'features': []}
        
        try:
            # Load audio using librosa
            import io
            import tempfile
            
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                tmp_file.write(audio_data)
                tmp_file.flush()
                
                # Extract features
                y, sr = librosa.load(tmp_file.name, sr=22050)
                
                # Spectral features
                mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
                chroma = librosa.feature.chroma(y=y, sr=sr)
                spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
                
                # Combine features
                features = np.concatenate([
                    np.mean(mfcc, axis=1),
                    np.mean(chroma, axis=1),
                    np.mean(spectral_centroid)
                ])
                
                # Generate hash from features
                features_str = ','.join(f'{f:.6f}' for f in features)
                hash_value = hashlib.sha256(features_str.encode()).hexdigest()
                
                return {
                    'hash': hash_value,
                    'type': 'audio_fingerprint',
                    'features': features.tolist(),
                    'duration': len(y) / sr
                }
                
        except Exception as e:
            logger.warning(f"Audio fingerprint generation failed, using fallback: {e}")
            hash_value = hashlib.sha256(audio_data).hexdigest()
            return {'hash': hash_value, 'type': 'audio_hash', 'features': []}
    
    async def _generate_image_fingerprint(self, image_data: bytes) -> Dict[str, Any]:
        """Generate image fingerprint using perceptual hashing"""
        if not DETECTION_AVAILABLE:
            hash_value = hashlib.sha256(image_data).hexdigest()
            return {'hash': hash_value, 'type': 'image_hash', 'features': []}
        
        try:
            import io
            
            # Load image
            image = Image.open(io.BytesIO(image_data))
            image = image.convert('RGB')
            
            # Resize for consistent fingerprinting
            image = image.resize((64, 64))
            
            # Convert to grayscale and calculate hash
            gray = image.convert('L')
            pixels = list(gray.getdata())
            
            # Generate perceptual hash
            avg = sum(pixels) / len(pixels)
            hash_bits = ''.join('1' if pixel > avg else '0' for pixel in pixels)
            hash_value = hashlib.sha256(hash_bits.encode()).hexdigest()
            
            return {
                'hash': hash_value,
                'type': 'image_fingerprint',
                'features': pixels[:100],  # First 100 pixels as features
                'size': image.size
            }
            
        except Exception as e:
            logger.warning(f"Image fingerprint generation failed, using fallback: {e}")
            hash_value = hashlib.sha256(image_data).hexdigest()
            return {'hash': hash_value, 'type': 'image_hash', 'features': []}
    
    async def _generate_text_fingerprint(self, text_data: str) -> Dict[str, Any]:
        """Generate text fingerprint using semantic embeddings"""
        try:
            # Clean text
            clean_text = ' '.join(text_data.split())
            
            if self.text_model:
                # Generate semantic embedding
                embedding = self.text_model.encode(clean_text)
                
                # Generate hash from embedding
                embedding_str = ','.join(f'{f:.6f}' for f in embedding)
                hash_value = hashlib.sha256(embedding_str.encode()).hexdigest()
                
                return {
                    'hash': hash_value,
                    'type': 'text_embedding',
                    'features': embedding.tolist(),
                    'length': len(clean_text)
                }
            else:
                # Fallback to n-gram based fingerprint
                words = clean_text.lower().split()
                ngrams = [' '.join(words[i:i+3]) for i in range(len(words)-2)]
                
                # Hash n-grams
                ngrams_str = '|'.join(sorted(ngrams))
                hash_value = hashlib.sha256(ngrams_str.encode()).hexdigest()
                
                return {
                    'hash': hash_value,
                    'type': 'text_ngrams',
                    'features': ngrams[:50],  # First 50 n-grams
                    'length': len(clean_text)
                }
                
        except Exception as e:
            logger.warning(f"Text fingerprint generation failed, using fallback: {e}")
            hash_value = hashlib.sha256(text_data.encode()).hexdigest()
            return {'hash': hash_value, 'type': 'text_hash', 'features': []}
    
    async def _calculate_similarity(self,
                                  fingerprint1: Dict[str, Any],
                                  fingerprint2: Dict[str, Any],
                                  content_type: str) -> Dict[str, Any]:
        """Calculate similarity between two fingerprints"""
        try:
            if fingerprint1['type'] != fingerprint2['type']:
                return {
                    'score': 0.0,
                    'confidence': 0.0,
                    'algorithm': DetectionAlgorithm.FINGERPRINT_MATCHING,
                    'metadata': {'error': 'Fingerprint type mismatch'}
                }
            
            # Hash-based exact matching
            if fingerprint1['hash'] == fingerprint2['hash']:
                return {
                    'score': 1.0,
                    'confidence': 1.0,
                    'algorithm': DetectionAlgorithm.FINGERPRINT_MATCHING,
                    'metadata': {'match_type': 'exact_hash'}
                }
            
            # Feature-based similarity for advanced fingerprints
            if fingerprint1.get('features') and fingerprint2.get('features'):
                features1 = np.array(fingerprint1['features'])
                features2 = np.array(fingerprint2['features'])
                
                if len(features1) == len(features2):
                    # Calculate cosine similarity
                    dot_product = np.dot(features1, features2)
                    norm1 = np.linalg.norm(features1)
                    norm2 = np.linalg.norm(features2)
                    
                    if norm1 > 0 and norm2 > 0:
                        similarity = dot_product / (norm1 * norm2)
                        confidence = min(abs(similarity), 1.0)
                        
                        algorithm_map = {
                            'audio': DetectionAlgorithm.AUDIO_FINGERPRINTING,
                            'image': DetectionAlgorithm.IMAGE_SIMILARITY,
                            'text': DetectionAlgorithm.TEXT_SIMILARITY
                        }
                        
                        return {
                            'score': max(similarity, 0.0),
                            'confidence': confidence,
                            'algorithm': algorithm_map.get(content_type, DetectionAlgorithm.FINGERPRINT_MATCHING),
                            'metadata': {
                                'match_type': 'feature_similarity',
                                'feature_correlation': similarity
                            }
                        }
            
            # No similarity detected
            return {
                'score': 0.0,
                'confidence': 0.0,
                'algorithm': DetectionAlgorithm.FINGERPRINT_MATCHING,
                'metadata': {'match_type': 'no_match'}
            }
            
        except Exception as e:
            logger.error(f"Similarity calculation failed: {e}")
            return {
                'score': 0.0,
                'confidence': 0.0,
                'algorithm': DetectionAlgorithm.FINGERPRINT_MATCHING,
                'metadata': {'error': str(e)}
            }
    
    def _determine_violation_type(self, similarity: Dict[str, Any]) -> ViolationType:
        """Determine violation type based on similarity"""
        score = similarity['score']
        match_type = similarity['metadata'].get('match_type', '')
        
        if score >= 0.95 or match_type == 'exact_hash':
            return ViolationType.EXACT_MATCH
        elif score >= 0.8:
            return ViolationType.PARTIAL_MATCH
        elif score >= 0.6:
            return ViolationType.DERIVATIVE_WORK
        else:
            return ViolationType.UNAUTHORIZED_USE
    
    def _generate_detection_summary(self, matches: List[CopyrightMatch]) -> Dict[str, Any]:
        """Generate summary of detection results"""
        if not matches:
            return {
                'violation_detected': False,
                'highest_confidence': 0.0,
                'primary_violation_type': None
            }
        
        # Calculate statistics
        confidences = [match.confidence for match in matches]
        violation_types = [match.violation_type.value for match in matches]
        
        return {
            'violation_detected': True,
            'highest_confidence': max(confidences),
            'average_confidence': sum(confidences) / len(confidences),
            'primary_violation_type': max(set(violation_types), key=violation_types.count),
            'violation_type_distribution': {vt: violation_types.count(vt) for vt in set(violation_types)}
        }
    
    def _generate_dmca_text(self,
                          violation_match: CopyrightMatch,
                          original_content: Dict[str, Any],
                          contact_info: Dict[str, Any]) -> str:
        """Generate DMCA takedown notice text"""
        return f"""
DMCA TAKEDOWN NOTICE

To: Platform Copyright Agent

I, {contact_info.get('name', 'Copyright Holder')}, am the owner of copyrighted material that is being used without authorization.

IDENTIFICATION OF COPYRIGHTED WORK:
- Content ID: {original_content['content_id']}
- Content Type: {original_content['content_type']}
- Registration Date: {original_content['registration_timestamp']}

IDENTIFICATION OF INFRINGING MATERIAL:
- Violation Type: {violation_match.violation_type.value}
- Similarity Score: {violation_match.similarity_score:.2%}
- Detection Confidence: {violation_match.confidence:.2%}
- Platform: {violation_match.platform_info.get('name', 'Unknown') if violation_match.platform_info else 'Unknown'}

I have a good faith belief that the use of the copyrighted material described above is not authorized by the copyright owner, its agent, or the law.

I swear, under penalty of perjury, that the information in this notification is accurate and that I am the copyright owner or am authorized to act on behalf of the owner.

Contact Information:
Name: {contact_info.get('name', '')}
Email: {contact_info.get('email', '')}
Phone: {contact_info.get('phone', '')}

Date: {datetime.now().strftime('%Y-%m-%d')}
Signature: [Electronic Signature]
        """.strip()
    
    async def _generate_video_fingerprint(self, video_data: bytes) -> Dict[str, Any]:
        """Generate video fingerprint (placeholder - requires video processing)"""
        # For now, use simple hash - in production, extract keyframes and analyze
        hash_value = hashlib.sha256(video_data).hexdigest()
        return {
            'hash': hash_value,
            'type': 'video_hash',
            'features': []
        }