"""Advanced Content Detection Engine
Professional content identification and analysis system for IA Influencer Protection

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""

import hashlib
import imagehash
import librosa
import numpy as np
from PIL import Image
from typing import Dict, List, Optional, Tuple, Any
import cv2
import tensorflow as tf
from datetime import datetime, timezone
import logging
from dataclasses import dataclass, asdict
import json

logger = logging.getLogger(__name__)


@dataclass
class ContentFingerprint:
    """
Content fingerprint for identification"""
    content_id: str
    content_type: str  # 'image', 'audio', 'video', 'text'
    hash_signatures: Dict[str, str]
    feature_vectors: Dict[str, List[float]]
    metadata: Dict[str, Any]
    created_at: datetime
    confidence_score: float


class ContentHashGenerator:
    """
Advanced hashing system for content identification"""
    
    def __init__(self):
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
            'image': ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'],
            'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'],
            'video': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv'],
            'text': ['.txt', '.md', '.doc', '.docx', '.pdf']
        }
    
    def generate_image_hash(self, image_path: str) -> Dict[str, str]:
        """
Generate multiple hash signatures for images"""
        try:
            image = Image.open(image_path)
            
            hashes = {
                'md5': self._calculate_file_hash(image_path, 'md5'),
                'sha256': self._calculate_file_hash(image_path, 'sha256'),
                'perceptual': str(imagehash.phash(image)),
                'difference': str(imagehash.dhash(image)),
                'average': str(imagehash.average_hash(image)),
                'wavelet': str(imagehash.whash(image))
            }
            
            logger.info(f"Generated {len(hashes)} hash signatures for image")
            return hashes
            
        except Exception as e:
            logger.error(f"Error generating image hash: {str(e)}")
            raise
    
    def generate_audio_hash(self, audio_path: str) -> Dict[str, str]:
        """Generate audio fingerprint using spectral analysis"""
        try:
            # Load audio file
            y, sr = librosa.load(audio_path, duration=30)  # First 30 seconds
            
            # Extract features
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            chroma = librosa.feature.chroma(y=y, sr=sr)
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
            
            # Create feature hash
            features = np.concatenate([
                np.mean(mfcc, axis=1),
                np.mean(chroma, axis=1),
                np.mean(spectral_centroid, axis=1)
            ])
            
            feature_hash = hashlib.sha256(features.tobytes()).hexdigest()
            
            hashes = {
                'md5': self._calculate_file_hash(audio_path, 'md5'),
                'sha256': self._calculate_file_hash(audio_path, 'sha256'),
                'spectral': feature_hash,
                'mfcc_signature': hashlib.md5(np.mean(mfcc, axis=1).tobytes()).hexdigest()
            }
            
            logger.info(f"Generated audio fingerprint with {len(hashes)} signatures")
            return hashes
            
        except Exception as e:
            logger.error(f"Error generating audio hash: {str(e)}")
            raise
    
    def generate_video_hash(self, video_path: str) -> Dict[str, str]:
        """Generate video fingerprint using frame analysis"""
        try:
            cap = cv2.VideoCapture(video_path)
            frame_hashes = []
            
            # Sample frames every second for first 30 seconds
            frame_count = 0
            max_frames = 30
            
            while cap.isOpened() and frame_count < max_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Convert to PIL Image for hashing
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_frame = Image.fromarray(frame_rgb)
                frame_hash = str(imagehash.phash(pil_frame))
                frame_hashes.append(frame_hash)
                
                # Skip to next second
                fps = cap.get(cv2.CAP_PROP_FPS)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count * fps)
                frame_count += 1
            
            cap.release()
            
            # Create composite hash
            composite_hash = hashlib.sha256(''.join(frame_hashes).encode()).hexdigest()
            
            hashes = {
                'md5': self._calculate_file_hash(video_path, 'md5'),
                'sha256': self._calculate_file_hash(video_path, 'sha256'),
                'frame_composite': composite_hash,
                'frame_sequence': hashlib.md5(''.join(frame_hashes[:10]).encode()).hexdigest()
            }
            
            logger.info(f"Generated video fingerprint with {len(frame_hashes)} frames analyzed")
            return hashes
            
        except Exception as e:
            logger.error(f"Error generating video hash: {str(e)}")
            raise
    
    def generate_text_hash(self, text_content: str) -> Dict[str, str]:
        """Generate text content fingerprint"""
        try:
            # Normalize text
            normalized = text_content.lower().strip()
            words = normalized.split()
            
            # Generate various hashes
            hashes = {
                'md5': hashlib.md5(text_content.encode()).hexdigest(),
                'sha256': hashlib.sha256(text_content.encode()).hexdigest(),
                'normalized': hashlib.sha256(normalized.encode()).hexdigest(),
                'semantic': self._generate_semantic_hash(words)
            }
            
            return hashes
            
        except Exception as e:
            logger.error(f"Error generating text hash: {str(e)}")
            raise
    
    def _calculate_file_hash(self, file_path: str, algorithm: str) -> str:
        """Calculate file hash using specified algorithm"""
        hash_func = getattr(hashlib, algorithm)()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        
        return hash_func.hexdigest()
    
    def _generate_semantic_hash(self, words: List[str]) -> str:
        """Generate semantic hash for text similarity"""
        # Simple word frequency-based hash
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and create signature
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        signature = ''.join([f"{word}:{freq}" for word, freq in sorted_words[:20]])
        
        return hashlib.md5(signature.encode()).hexdigest()


class ContentDetectionEngine:
    """Main content detection and analysis engine"""
    
    def __init__(self):
        self.hash_generator = ContentHashGenerator()
        self.similarity_threshold = 0.95
        self.fingerprint_cache = {}
    
    def analyze_content(self, content_path: str, content_type: str = None) -> ContentFingerprint:
        """
Comprehensive content analysis and fingerprinting"""
        try:
            if not content_type:
                content_type = self._detect_content_type(content_path)
            
            content_id = hashlib.sha256(f"{content_path}:{datetime.now().isoformat()}".encode()).hexdigest()[:16]
            
            # Generate appropriate hashes
            if content_type == 'image':
                hash_signatures = self.hash_generator.generate_image_hash(content_path)
                feature_vectors = self._extract_image_features(content_path)
            elif content_type == 'audio':
                hash_signatures = self.hash_generator.generate_audio_hash(content_path)
                feature_vectors = self._extract_audio_features(content_path)
            elif content_type == 'video':
                hash_signatures = self.hash_generator.generate_video_hash(content_path)
                feature_vectors = self._extract_video_features(content_path)
            else:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            # Extract metadata
            metadata = self._extract_metadata(content_path, content_type)
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(hash_signatures, feature_vectors)
            
            fingerprint = ContentFingerprint(
                content_id=content_id,
                content_type=content_type,
                hash_signatures=hash_signatures,
                feature_vectors=feature_vectors,
                metadata=metadata,
                created_at=datetime.now(timezone.utc),
                confidence_score=confidence_score
            )
            
            # Cache fingerprint
            self.fingerprint_cache[content_id] = fingerprint
            
            logger.info(f"Generated fingerprint for {content_type} content: {content_id}")
            return fingerprint
            
        except Exception as e:
            logger.error(f"Error analyzing content: {str(e)}")
            raise
    
    def detect_similarity(self, fingerprint1: ContentFingerprint, fingerprint2: ContentFingerprint) -> float:
        """Calculate similarity between two content fingerprints"""
        try:
            if fingerprint1.content_type != fingerprint2.content_type:
                return 0.0
            
            # Hash similarity
            hash_similarity = self._compare_hashes(
                fingerprint1.hash_signatures, 
                fingerprint2.hash_signatures
            )
            
            # Feature similarity
            feature_similarity = self._compare_features(
                fingerprint1.feature_vectors,
                fingerprint2.feature_vectors
            )
            
            # Combined similarity score
            combined_score = (hash_similarity * 0.6) + (feature_similarity * 0.4)
            
            logger.debug(f"Similarity: hash={hash_similarity:.3f}, features={feature_similarity:.3f}, combined={combined_score:.3f}")
            
            return combined_score
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0
    
    def search_duplicates(self, target_fingerprint: ContentFingerprint, fingerprint_database: List[ContentFingerprint]) -> List[Tuple[ContentFingerprint, float]]:
        """Search for potential duplicates in fingerprint database"""
        matches = []
        
        for fp in fingerprint_database:
            if fp.content_type == target_fingerprint.content_type:
                similarity = self.detect_similarity(target_fingerprint, fp)
                if similarity >= self.similarity_threshold:
                    matches.append((fp, similarity))
        
        # Sort by similarity score (descending)
        matches.sort(key=lambda x: x[1], reverse=True)
        
        logger.info(f"Found {len(matches)} potential duplicates")
        return matches
    
    def _detect_content_type(self, file_path: str) -> str:
        """Auto-detect content type from file extension"""
        ext = file_path.lower().split('.')[-1]
        
        for content_type, extensions in self.hash_generator.supported_formats.items():
            if f'.{ext}' in extensions:
                return content_type
        
        raise ValueError(f"Unsupported file extension: .{ext}")
    
    def _extract_image_features(self, image_path: str) -> Dict[str, List[float]]:
        """Extract advanced image features"""
        try:
            image = cv2.imread(image_path)
            
            # Color histograms
            hist_b = cv2.calcHist([image], [0], None, [256], [0, 256]).flatten()
            hist_g = cv2.calcHist([image], [1], None, [256], [0, 256]).flatten()
            hist_r = cv2.calcHist([image], [2], None, [256], [0, 256]).flatten()
            
            # Texture features (LBP-like)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            texture_features = self._calculate_texture_features(gray)
            
            return {
                'color_hist_b': hist_b.tolist()[:64],  # Reduced size
                'color_hist_g': hist_g.tolist()[:64],
                'color_hist_r': hist_r.tolist()[:64],
                'texture': texture_features.tolist()
            }
            
        except Exception as e:
            logger.error(f"Error extracting image features: {str(e)}")
            return {}
    
    def _extract_audio_features(self, audio_path: str) -> Dict[str, List[float]]:
        """Extract advanced audio features"""
        try:
            y, sr = librosa.load(audio_path, duration=30)
            
            # Spectral features
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            chroma = librosa.feature.chroma(y=y, sr=sr)
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
            zero_crossing_rate = librosa.feature.zero_crossing_rate(y)
            
            return {
                'mfcc': np.mean(mfcc, axis=1).tolist(),
                'chroma': np.mean(chroma, axis=1).tolist(),
                'spectral_centroid': np.mean(spectral_centroid).tolist() if spectral_centroid.size > 0 else [0.0],
                'spectral_bandwidth': np.mean(spectral_bandwidth).tolist() if spectral_bandwidth.size > 0 else [0.0],
                'spectral_rolloff': np.mean(spectral_rolloff).tolist() if spectral_rolloff.size > 0 else [0.0],
                'zero_crossing_rate': np.mean(zero_crossing_rate).tolist() if zero_crossing_rate.size > 0 else [0.0]
            }
            
        except Exception as e:
            logger.error(f"Error extracting audio features: {str(e)}")
            return {}
    
    def _extract_video_features(self, video_path: str) -> Dict[str, List[float]]:
        """Extract video-specific features"""
        try:
            cap = cv2.VideoCapture(video_path)
            
            # Video metadata
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            
            # Sample frame features
            frame_features = []
            sample_frames = min(10, frame_count)
            
            for i in range(sample_frames):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i * (frame_count // sample_frames))
                ret, frame = cap.read()
                if ret:
                    # Extract color histogram
                    hist = cv2.calcHist([frame], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
                    frame_features.extend(hist.flatten()[:64].tolist())  # Reduced size
            
            cap.release()
            
            return {
                'fps': [fps],
                'duration': [duration],
                'frame_features': frame_features[:512]  # Limit size
            }
            
        except Exception as e:
            logger.error(f"Error extracting video features: {str(e)}")
            return {}
    
    def _extract_metadata(self, file_path: str, content_type: str) -> Dict[str, Any]:
        """Extract file metadata"""
        import os
        from pathlib import Path
        
        path_obj = Path(file_path)
        stat = os.stat(file_path)
        
        metadata = {
            'filename': path_obj.name,
            'file_size': stat.st_size,
            'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'content_type': content_type,
            'file_extension': path_obj.suffix
        }
        
        return metadata
    
    def _calculate_confidence_score(self, hash_signatures: Dict[str, str], feature_vectors: Dict[str, List[float]]) -> float:
        """
Calculate confidence score for fingerprint quality"""
        score = 0.0
        
        # Hash quality (more hashes = higher confidence)
        hash_score = min(len(hash_signatures) / 4, 1.0) * 0.4
        
        # Feature quality (more features = higher confidence)
        feature_count = sum(len(features) for features in feature_vectors.values())
        feature_score = min(feature_count / 100, 1.0) * 0.6
        
        score = hash_score + feature_score
        
        return min(score, 1.0)
    
    def _compare_hashes(self, hashes1: Dict[str, str], hashes2: Dict[str, str]) -> float:
        """
Compare hash signatures for similarity"""
        common_keys = set(hashes1.keys()) & set(hashes2.keys())
        if not common_keys:
            return 0.0
        
        matches = sum(1 for key in common_keys if hashes1[key] == hashes2[key])
        return matches / len(common_keys)
    
    def _compare_features(self, features1: Dict[str, List[float]], features2: Dict[str, List[float]]) -> float:
        """
Compare feature vectors for similarity"""
        common_keys = set(features1.keys()) & set(features2.keys())
        if not common_keys:
            return 0.0
        
        similarities = []
        for key in common_keys:
            vec1 = np.array(features1[key])
            vec2 = np.array(features2[key])
            
            if len(vec1) == len(vec2) and len(vec1) > 0:
                # Cosine similarity
                dot_product = np.dot(vec1, vec2)
                norm1 = np.linalg.norm(vec1)
                norm2 = np.linalg.norm(vec2)
                
                if norm1 > 0 and norm2 > 0:
                    similarity = dot_product / (norm1 * norm2)
                    similarities.append(max(0, similarity))  # Ensure non-negative
        
        return np.mean(similarities) if similarities else 0.0
    
    def _calculate_texture_features(self, gray_image: np.ndarray) -> np.ndarray:
        """
Calculate basic texture features"""
        # Simple gradient-based texture features
        grad_x = cv2.Sobel(gray_image, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray_image, cv2.CV_64F, 0, 1, ksize=3)
        
        magnitude = np.sqrt(grad_x**2 + grad_y**2)
        
        # Calculate texture statistics
        features = np.array([
            np.mean(magnitude),
            np.std(magnitude),
            np.percentile(magnitude, 25),
            np.percentile(magnitude, 75)
        ])
        
        return features


class ContentDetectionManager:
    """
High-level manager for content detection operations"""
    
    def __init__(self):
        self.detection_engine = ContentDetectionEngine()
        self.fingerprint_database = []
    
    def register_content(self, content_path: str, owner_id: str, content_metadata: Dict[str, Any] = None) -> str:
        """
Register new content for protection"""
        try:
            fingerprint = self.detection_engine.analyze_content(content_path)
            
            # Add owner information
            fingerprint.metadata.update({
                'owner_id': owner_id,
                'registration_date': datetime.now(timezone.utc).isoformat(),
                'content_metadata': content_metadata or {}
            })
            
            # Add to database
            self.fingerprint_database.append(fingerprint)
            
            logger.info(f"Content registered successfully: {fingerprint.content_id}")
            return fingerprint.content_id
            
        except Exception as e:
            logger.error(f"Error registering content: {str(e)}")
            raise
    
    def detect_infringement(self, suspicious_content_path: str) -> List[Dict[str, Any]]:
        """Detect potential copyright infringement"""
        try:
            # Analyze suspicious content
            suspicious_fingerprint = self.detection_engine.analyze_content(suspicious_content_path)
            
            # Search for matches
            matches = self.detection_engine.search_duplicates(
                suspicious_fingerprint, 
                self.fingerprint_database
            )
            
            # Format results
            infringement_results = []
            for original_fp, similarity_score in matches:
                result = {
                    'original_content_id': original_fp.content_id,
                    'owner_id': original_fp.metadata.get('owner_id'),
                    'similarity_score': similarity_score,
                    'content_type': original_fp.content_type,
                    'detection_timestamp': datetime.now(timezone.utc).isoformat(),
                    'confidence_level': 'HIGH' if similarity_score > 0.98 else 'MEDIUM' if similarity_score > 0.95 else 'LOW'
                }
                infringement_results.append(result)
            
            logger.info(f"Detected {len(infringement_results)} potential infringements")
            return infringement_results
            
        except Exception as e:
            logger.error(f"Error detecting infringement: {str(e)}")
            raise
    
    def export_fingerprint_database(self) -> str:
        """Export fingerprint database to JSON"""
        try:
            export_data = []
            for fp in self.fingerprint_database:
                export_data.append(asdict(fp))
            
            return json.dumps(export_data, indent=2, default=str)
            
        except Exception as e:
            logger.error(f"Error exporting database: {str(e)}")
            raise
    
    def import_fingerprint_database(self, json_data: str) -> int:
        """Import fingerprint database from JSON"""
        try:
            import_data = json.loads(json_data)
            imported_count = 0
            
            for fp_data in import_data:
                # Convert back to ContentFingerprint object
                fp_data['created_at'] = datetime.fromisoformat(fp_data['created_at'].replace('Z', '+00:00'))
                fingerprint = ContentFingerprint(**fp_data)
                
                self.fingerprint_database.append(fingerprint)
                imported_count += 1
            
            logger.info(f"Imported {imported_count} fingerprints")
            return imported_count
            
        except Exception as e:
            logger.error(f"Error importing database: {str(e)}")
            raise


# Export main classes
__all__ = [
    'ContentFingerprint',
    'ContentHashGenerator', 
    'ContentDetectionEngine',
    'ContentDetectionManager'
]
