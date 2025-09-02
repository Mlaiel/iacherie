"""Advanced Content Analysis Engine for IA Influencer Agent Protection System
Handles multi-format content analysis, fingerprinting, and copyright protection

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: Proprietary - All rights reserved
WARNING: Unauthorized use, copying, or distribution prohibited
"""

import hashlib
import numpy as np
import cv2
import librosa
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass
from datetime import datetime
import imagehash
from PIL import Image
import speech_recognition as sr
from transformers import pipeline
import logging

logger = logging.getLogger(__name__)

@dataclass
class ContentFingerprint:
    """
Advanced fingerprint structure for multi-format content"""
    content_id: str
    content_type: str
    hash_sha256: str
    perceptual_hash: Optional[str] = None
    audio_fingerprint: Optional[Dict] = None
    visual_features: Optional[Dict] = None
    text_features: Optional[Dict] = None
    metadata: Optional[Dict] = None
    timestamp: datetime = None
    confidence_score: float = 0.0
    
    def __post_init__(self):
        try:
                    # Request validation
                    if not data:
                        raise ValueError("Invalid request")
            
                    # Process request
                    result = await self._handle___post_init___request(data)
            
                    # Return response
                    return {"status": "success", "data": result}
            
                except Exception as e:
                    logger.error(f"API handler __post_init__ failed: {e}")
                    return {"status": "error", "message": str(e)}
            self.timestamp = datetime.utcnow()


class AdvancedContentAnalyzer:
    """
    Ultra-advanced content analyzer for multi-format protection
    Handles audio, video, image, and text content analysis
    """
    
    def __init__(self):
        self.audio_sr = 22050
        self.video_fps = 30
        self.image_size = (224, 224)
        self.text_model = pipeline("feature-extraction", model="bert-base-uncased")
        self.speech_recognizer = sr.Recognizer()
        
    def analyze_content(self, content_data: bytes, content_type: str, metadata: Dict = None) -> ContentFingerprint:
        """
        Master content analysis method
        
        Args:
            content_data: Raw content bytes
            content_type: MIME type of content
            metadata: Additional metadata
            
        Returns:
            ContentFingerprint: Complete fingerprint analysis
        """
        try:
            content_id = self._generate_content_id(content_data)
            base_hash = hashlib.sha256(content_data).hexdigest()
            
            fingerprint = ContentFingerprint(
                content_id=content_id,
                content_type=content_type,
                hash_sha256=base_hash,
                metadata=metadata or {}
            )
            
            # Route to specific analyzer based on content type
            if content_type.startswith('audio/'):
                self._analyze_audio_content(content_data, fingerprint)
            elif content_type.startswith('video/'):
                self._analyze_video_content(content_data, fingerprint)
            elif content_type.startswith('image/'):
                self._analyze_image_content(content_data, fingerprint)
            elif content_type.startswith('text/'):
                self._analyze_text_content(content_data, fingerprint)
            else:
                logger.warning(f"Unknown content type: {content_type}")
                
            return fingerprint
            
        except Exception as e:
            logger.error(f"Content analysis failed: {str(e)}")
            raise
            
    def _generate_content_id(self, content_data: bytes) -> str:
        """Generate unique content identifier"""
        return f"CONTENT_{hashlib.md5(content_data).hexdigest()[:16].upper()}"
        
    def _analyze_audio_content(self, audio_data: bytes, fingerprint: ContentFingerprint):
        """Advanced audio content analysis with ML fingerprinting"""
        try:
            # Load audio data
            y, sr = librosa.load(io.BytesIO(audio_data), sr=self.audio_sr)
            
            # Extract comprehensive audio features
            features = self._extract_audio_features(y, sr)
            
            # Generate perceptual hash
            fingerprint.perceptual_hash = self._generate_audio_hash(features)
            fingerprint.audio_fingerprint = features
            fingerprint.confidence_score = self._calculate_audio_confidence(features)
            
        except Exception as e:
            logger.error(f"Audio analysis failed: {str(e)}")
            fingerprint.confidence_score = 0.0
            
    def _extract_audio_features(self, y: np.ndarray, sr: int) -> Dict:
        """Extract comprehensive audio features for fingerprinting"""
        features = {}
        
        # Spectral features
        features['mfcc'] = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13).tolist()
        features['chroma'] = librosa.feature.chroma(y=y, sr=sr).tolist()
        features['spectral_centroid'] = librosa.feature.spectral_centroid(y=y, sr=sr).tolist()
        features['spectral_rolloff'] = librosa.feature.spectral_rolloff(y=y, sr=sr).tolist()
        features['zero_crossing_rate'] = librosa.feature.zero_crossing_rate(y).tolist()
        
        # Temporal features
        features['tempo'] = float(librosa.beat.tempo(y=y, sr=sr)[0])
        features['duration'] = float(len(y) / sr)
        
        # Advanced features
        features['spectral_contrast'] = librosa.feature.spectral_contrast(y=y, sr=sr).tolist()
        features['tonnetz'] = librosa.feature.tonnetz(y=librosa.effects.harmonic(y), sr=sr).tolist()
        
        # Statistical measures
        features['rms_energy'] = librosa.feature.rms(y=y).tolist()
        features['spectral_bandwidth'] = librosa.feature.spectral_bandwidth(y=y, sr=sr).tolist()
        
        return features
        
    def _generate_audio_hash(self, features: Dict) -> str:
        """
Generate perceptual hash from audio features"""
        # Create feature vector
        feature_vector = []
        for key, value in features.items():
            if isinstance(value, list):
                feature_vector.extend([np.mean(value), np.std(value)])
            else:
                feature_vector.append(value)
                
        # Normalize and hash
        feature_array = np.array(feature_vector)
        normalized = (feature_array - np.mean(feature_array)) / (np.std(feature_array) + 1e-8)
        return hashlib.sha256(normalized.tobytes()).hexdigest()
        
    def _calculate_audio_confidence(self, features: Dict) -> float:
        """
Calculate confidence score for audio fingerprint"""
        confidence = 0.8  # Base confidence
        
        # Adjust based on feature quality
        if features.get('duration', 0) > 10:  # Longer audio = higher confidence
            confidence += 0.1
        if features.get('tempo', 0) > 0:  # Valid tempo detected
            confidence += 0.05
        if len(features.get('mfcc', [])) > 0:  # MFCC features available
            confidence += 0.05
            
        return min(confidence, 1.0)
        
    def _analyze_video_content(self, video_data: bytes, fingerprint: ContentFingerprint):
        """
Advanced video content analysis"""
        try:
            # Extract video frames and audio
            frames, audio_track = self._extract_video_components(video_data)
            
            # Analyze visual components
            visual_features = self._extract_video_features(frames)
            fingerprint.visual_features = visual_features
            
            # Analyze audio track if present
            if audio_track is not None:
                self._analyze_audio_content(audio_track, fingerprint)
                
            # Generate combined hash
            fingerprint.perceptual_hash = self._generate_video_hash(visual_features)
            fingerprint.confidence_score = self._calculate_video_confidence(visual_features)
            
        except Exception as e:
            logger.error(f"Video analysis failed: {str(e)}")
            fingerprint.confidence_score = 0.0
            
    def _extract_video_components(self, video_data: bytes) -> Tuple[List[np.ndarray], Optional[bytes]]:
        """Extract frames and audio from video"""
        # Implementation would use OpenCV or similar
        # Placeholder for video processing logic
        frames = []
        audio_track = None
        return frames, audio_track
        
    def _extract_video_features(self, frames: List[np.ndarray]) -> Dict:
        """
Extract visual features from video frames"""
        features = {
            'frame_count': len(frames),
            'average_brightness': [],
            'color_histogram': [],
            'edge_density': [],
            'motion_vectors': []
        }
        
        for frame in frames:
            # Brightness analysis
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            features['average_brightness'].append(float(np.mean(gray)))
            
            # Color histogram
            hist = cv2.calcHist([frame], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
            features['color_histogram'].append(hist.flatten().tolist())
            
            # Edge detection
            edges = cv2.Canny(gray, 50, 150)
            features['edge_density'].append(float(np.sum(edges) / edges.size))
            
        return features
        
    def _generate_video_hash(self, visual_features: Dict) -> str:
        """
Generate perceptual hash for video content"""
        # Combine visual features into hash
        feature_string = str(visual_features)
        return hashlib.sha256(feature_string.encode()).hexdigest()
        
    def _calculate_video_confidence(self, visual_features: Dict) -> float:
        """
Calculate confidence score for video fingerprint"""
        confidence = 0.7
        
        frame_count = visual_features.get('frame_count', 0)
        if frame_count > 30:  # At least 1 second at 30fps
            confidence += 0.1
        if frame_count > 300:  # At least 10 seconds
            confidence += 0.1
            
        return min(confidence, 1.0)
        
    def _analyze_image_content(self, image_data: bytes, fingerprint: ContentFingerprint):
        """
Advanced image content analysis"""
        try:
            # Load image
            image = Image.open(io.BytesIO(image_data))
            
            # Generate perceptual hashes
            ahash = str(imagehash.average_hash(image))
            phash = str(imagehash.phash(image))
            dhash = str(imagehash.dhash(image))
            whash = str(imagehash.whash(image))
            
            # Extract visual features
            visual_features = self._extract_image_features(image)
            
            fingerprint.perceptual_hash = f"{ahash}:{phash}:{dhash}:{whash}"
            fingerprint.visual_features = visual_features
            fingerprint.confidence_score = self._calculate_image_confidence(visual_features)
            
        except Exception as e:
            logger.error(f"Image analysis failed: {str(e)}")
            fingerprint.confidence_score = 0.0
            
    def _extract_image_features(self, image: Image.Image) -> Dict:
        """Extract comprehensive image features"""
        # Convert to numpy array
        img_array = np.array(image.resize(self.image_size))
        
        features = {
            'dimensions': image.size,
            'mode': image.mode,
            'format': image.format,
            'color_histogram': {},
            'texture_features': {},
            'statistical_features': {}
        }
        
        # Color histogram analysis
        if len(img_array.shape) == 3:  # Color image
            for i, color in enumerate(['red', 'green', 'blue']):
                hist, _ = np.histogram(img_array[:, :, i], bins=32, range=(0, 256))
                features['color_histogram'][color] = hist.tolist()
        else:  # Grayscale
            hist, _ = np.histogram(img_array, bins=32, range=(0, 256))
            features['color_histogram']['gray'] = hist.tolist()
            
        # Statistical features
        features['statistical_features'] = {
            'mean': float(np.mean(img_array)),
            'std': float(np.std(img_array)),
            'min': float(np.min(img_array)),
            'max': float(np.max(img_array))
        }
        
        return features
        
    def _calculate_image_confidence(self, visual_features: Dict) -> float:
        """
Calculate confidence score for image fingerprint"""
        confidence = 0.85
        
        # Adjust based on image quality indicators
        dimensions = visual_features.get('dimensions', (0, 0))
        if dimensions[0] * dimensions[1] > 100000:  # High resolution
            confidence += 0.1
            
        return min(confidence, 1.0)
        
    def _analyze_text_content(self, text_data: bytes, fingerprint: ContentFingerprint):
        """
Advanced text content analysis"""
        try:
            text = text_data.decode('utf-8')
            
            # Extract text features
            text_features = self._extract_text_features(text)
            
            # Generate text hash
            fingerprint.perceptual_hash = self._generate_text_hash(text)
            fingerprint.text_features = text_features
            fingerprint.confidence_score = self._calculate_text_confidence(text_features)
            
        except Exception as e:
            logger.error(f"Text analysis failed: {str(e)}")
            fingerprint.confidence_score = 0.0
            
    def _extract_text_features(self, text: str) -> Dict:
        """Extract comprehensive text features"""
        features = {
            'length': len(text),
            'word_count': len(text.split()),
            'line_count': len(text.split('\n')),
            'character_frequency': {},
            'linguistic_features': {}
        }
        
        # Character frequency analysis
        for char in text.lower():
            if char.isalnum():
                features['character_frequency'][char] = features['character_frequency'].get(char, 0) + 1
                
        # Linguistic features using NLP
        try:
            # Use transformer model for feature extraction
            embeddings = self.text_model(text[:512])  # Limit input size
            features['linguistic_features']['embeddings_mean'] = np.mean(embeddings[0], axis=0).tolist()
        except Exception as e:
            logger.warning(f"NLP feature extraction failed: {str(e)}")
            
        return features
        
    def _generate_text_hash(self, text: str) -> str:
        """Generate perceptual hash for text content"""
        # Normalize text for hashing
        normalized = ''.join(c.lower() for c in text if c.isalnum() or c.isspace())
        return hashlib.sha256(normalized.encode()).hexdigest()
        
    def _calculate_text_confidence(self, text_features: Dict) -> float:
        """
Calculate confidence score for text fingerprint"""
        confidence = 0.8
        
        word_count = text_features.get('word_count', 0)
        if word_count > 100:  # Substantial text content
            confidence += 0.1
        if word_count > 1000:  # Large text content
            confidence += 0.05
            
        return min(confidence, 1.0)


class ContentMatchingEngine:
    """
Advanced content matching and similarity detection engine"""
    
    def __init__(self):
        self.similarity_threshold = 0.85
        self.audio_threshold = 0.90
        self.visual_threshold = 0.88
        self.text_threshold = 0.92
        
    def find_matches(self, target_fingerprint: ContentFingerprint, 
                    candidate_fingerprints: List[ContentFingerprint]) -> List[Dict]:
        """
        Find matching content using advanced similarity algorithms
        
        Args:
            target_fingerprint: Fingerprint to match against
            candidate_fingerprints: List of candidate fingerprints
            
        Returns:
            List of match results with similarity scores
        """
        matches = []
        
        for candidate in candidate_fingerprints:
            similarity_score = self._calculate_similarity(target_fingerprint, candidate)
            
            if similarity_score >= self.similarity_threshold:
                match_result = {
                    'candidate_id': candidate.content_id,
                    'similarity_score': similarity_score,
                    'match_type': self._determine_match_type(similarity_score),
                    'confidence': min(target_fingerprint.confidence_score, 
                                    candidate.confidence_score),
                    'analysis_details': self._generate_match_analysis(
                        target_fingerprint, candidate, similarity_score)
                }
                matches.append(match_result)
                
        # Sort by similarity score (descending)
        matches.sort(key=lambda x: x['similarity_score'], reverse=True)
        return matches
        
    def _calculate_similarity(self, fp1: ContentFingerprint, fp2: ContentFingerprint) -> float:
        """
Calculate comprehensive similarity score between fingerprints"""
        if fp1.content_type != fp2.content_type:
            return 0.0
            
        # Content type specific similarity calculation
        if fp1.content_type.startswith('audio/'):
            return self._calculate_audio_similarity(fp1, fp2)
        elif fp1.content_type.startswith('video/'):
            return self._calculate_video_similarity(fp1, fp2)
        elif fp1.content_type.startswith('image/'):
            return self._calculate_image_similarity(fp1, fp2)
        elif fp1.content_type.startswith('text/'):
            return self._calculate_text_similarity(fp1, fp2)
        else:
            # Fallback to hash comparison
            return 1.0 if fp1.hash_sha256 == fp2.hash_sha256 else 0.0
            
    def _calculate_audio_similarity(self, fp1: ContentFingerprint, fp2: ContentFingerprint) -> float:
        """
Calculate audio content similarity"""
        if not (fp1.audio_fingerprint and fp2.audio_fingerprint):
            return 0.0
            
        similarities = []
        
        # MFCC similarity
        mfcc1 = np.array(fp1.audio_fingerprint.get('mfcc', []))
        mfcc2 = np.array(fp2.audio_fingerprint.get('mfcc', []))
        if mfcc1.size > 0 and mfcc2.size > 0:
            mfcc_sim = self._cosine_similarity(mfcc1.flatten(), mfcc2.flatten())
            similarities.append(mfcc_sim * 0.4)  # 40% weight
            
        # Chroma similarity
        chroma1 = np.array(fp1.audio_fingerprint.get('chroma', []))
        chroma2 = np.array(fp2.audio_fingerprint.get('chroma', []))
        if chroma1.size > 0 and chroma2.size > 0:
            chroma_sim = self._cosine_similarity(chroma1.flatten(), chroma2.flatten())
            similarities.append(chroma_sim * 0.3)  # 30% weight
            
        # Tempo similarity
        tempo1 = fp1.audio_fingerprint.get('tempo', 0)
        tempo2 = fp2.audio_fingerprint.get('tempo', 0)
        if tempo1 > 0 and tempo2 > 0:
            tempo_diff = abs(tempo1 - tempo2) / max(tempo1, tempo2)
            tempo_sim = max(0, 1 - tempo_diff)
            similarities.append(tempo_sim * 0.2)  # 20% weight
            
        # Duration similarity
        dur1 = fp1.audio_fingerprint.get('duration', 0)
        dur2 = fp2.audio_fingerprint.get('duration', 0)
        if dur1 > 0 and dur2 > 0:
            dur_diff = abs(dur1 - dur2) / max(dur1, dur2)
            dur_sim = max(0, 1 - dur_diff)
            similarities.append(dur_sim * 0.1)  # 10% weight
            
        return sum(similarities) if similarities else 0.0
        
    def _calculate_image_similarity(self, fp1: ContentFingerprint, fp2: ContentFingerprint) -> float:
        """
Calculate image content similarity"""
        if not (fp1.perceptual_hash and fp2.perceptual_hash):
            return 0.0
            
        # Parse perceptual hashes
        hashes1 = fp1.perceptual_hash.split(':')
        hashes2 = fp2.perceptual_hash.split(':')
        
        if len(hashes1) != 4 or len(hashes2) != 4:
            return 0.0
            
        similarities = []
        for h1, h2 in zip(hashes1, hashes2):
            # Calculate Hamming distance for each hash type
            hamming_dist = sum(c1 != c2 for c1, c2 in zip(h1, h2))
            similarity = max(0, 1 - hamming_dist / len(h1))
            similarities.append(similarity)
            
        # Average similarity across all hash types
        return sum(similarities) / len(similarities)
        
    def _calculate_text_similarity(self, fp1: ContentFingerprint, fp2: ContentFingerprint) -> float:
        """
Calculate text content similarity"""
        if not (fp1.text_features and fp2.text_features):
            return 0.0
            
        similarities = []
        
        # Character frequency similarity
        freq1 = fp1.text_features.get('character_frequency', {})
        freq2 = fp2.text_features.get('character_frequency', {})
        if freq1 and freq2:
            freq_sim = self._calculate_frequency_similarity(freq1, freq2)
            similarities.append(freq_sim * 0.3)
            
        # Linguistic features similarity
        ling1 = fp1.text_features.get('linguistic_features', {})
        ling2 = fp2.text_features.get('linguistic_features', {})
        if ling1.get('embeddings_mean') and ling2.get('embeddings_mean'):
            emb1 = np.array(ling1['embeddings_mean'])
            emb2 = np.array(ling2['embeddings_mean'])
            emb_sim = self._cosine_similarity(emb1, emb2)
            similarities.append(emb_sim * 0.7)
            
        return sum(similarities) if similarities else 0.0
        
    def _calculate_video_similarity(self, fp1: ContentFingerprint, fp2: ContentFingerprint) -> float:
        """
Calculate video content similarity"""
        similarities = []
        
        # Visual similarity
        if fp1.visual_features and fp2.visual_features:
            visual_sim = self._calculate_visual_features_similarity(
                fp1.visual_features, fp2.visual_features)
            similarities.append(visual_sim * 0.6)
            
        # Audio similarity (if available)
        if fp1.audio_fingerprint and fp2.audio_fingerprint:
            audio_sim = self._calculate_audio_similarity(fp1, fp2)
            similarities.append(audio_sim * 0.4)
            
        return sum(similarities) if similarities else 0.0
        
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
Calculate cosine similarity between two vectors"""
        if vec1.size == 0 or vec2.size == 0:
            return 0.0
            
        # Ensure vectors have same length
        min_len = min(len(vec1), len(vec2))
        vec1 = vec1[:min_len]
        vec2 = vec2[:min_len]
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        return dot_product / (norm1 * norm2)
        
    def _calculate_frequency_similarity(self, freq1: Dict, freq2: Dict) -> float:
        """
Calculate similarity between character frequency distributions"""
        all_chars = set(freq1.keys()) | set(freq2.keys())
        
        if not all_chars:
            return 0.0
            
        vec1 = np.array([freq1.get(char, 0) for char in all_chars])
        vec2 = np.array([freq2.get(char, 0) for char in all_chars])
        
        return self._cosine_similarity(vec1, vec2)
        
    def _calculate_visual_features_similarity(self, features1: Dict, features2: Dict) -> float:
        """
Calculate similarity between visual features"""
        similarities = []
        
        # Frame count similarity
        fc1 = features1.get('frame_count', 0)
        fc2 = features2.get('frame_count', 0)
        if fc1 > 0 and fc2 > 0:
            fc_diff = abs(fc1 - fc2) / max(fc1, fc2)
            fc_sim = max(0, 1 - fc_diff)
            similarities.append(fc_sim * 0.2)
            
        # Average brightness similarity
        bright1 = features1.get('average_brightness', [])
        bright2 = features2.get('average_brightness', [])
        if bright1 and bright2:
            b1_mean = np.mean(bright1)
            b2_mean = np.mean(bright2)
            bright_diff = abs(b1_mean - b2_mean) / 255.0  # Normalize by max brightness
            bright_sim = max(0, 1 - bright_diff)
            similarities.append(bright_sim * 0.3)
            
        # Color histogram similarity
        hist1 = features1.get('color_histogram', [])
        hist2 = features2.get('color_histogram', [])
        if hist1 and hist2 and len(hist1) == len(hist2):
            hist_sim = self._calculate_histogram_similarity(hist1, hist2)
            similarities.append(hist_sim * 0.5)
            
        return sum(similarities) if similarities else 0.0
        
    def _calculate_histogram_similarity(self, hist1: List, hist2: List) -> float:
        """
Calculate similarity between color histograms"""
        h1 = np.array(hist1)
        h2 = np.array(hist2)
        
        # Normalize histograms
        h1_norm = h1 / (np.sum(h1) + 1e-8)
        h2_norm = h2 / (np.sum(h2) + 1e-8)
        
        # Calculate histogram intersection
        intersection = np.minimum(h1_norm, h2_norm)
        return np.sum(intersection)
        
    def _determine_match_type(self, similarity_score: float) -> str:
        """
Determine the type of match based on similarity score"""
        if similarity_score >= 0.95:
            return "EXACT_MATCH"
        elif similarity_score >= 0.90:
            return "NEAR_DUPLICATE"
        elif similarity_score >= 0.85:
            return "SIMILAR_CONTENT"
        else:
            return "POTENTIAL_MATCH"
            
    def _generate_match_analysis(self, fp1: ContentFingerprint, fp2: ContentFingerprint, 
                                similarity_score: float) -> Dict:
        """Generate detailed analysis of the match"""
        analysis = {
            'similarity_score': similarity_score,
            'content_type': fp1.content_type,
            'hash_match': fp1.hash_sha256 == fp2.hash_sha256,
            'perceptual_match': fp1.perceptual_hash == fp2.perceptual_hash if fp1.perceptual_hash else False,
            'confidence_difference': abs(fp1.confidence_score - fp2.confidence_score),
            'analysis_timestamp': datetime.utcnow().isoformat()
        }
        
        # Add content-specific analysis
        if fp1.content_type.startswith('audio/'):
            analysis['audio_analysis'] = self._analyze_audio_match(fp1, fp2)
        elif fp1.content_type.startswith('image/'):
            analysis['image_analysis'] = self._analyze_image_match(fp1, fp2)
        elif fp1.content_type.startswith('text/'):
            analysis['text_analysis'] = self._analyze_text_match(fp1, fp2)
            
        return analysis
        
    def _analyze_audio_match(self, fp1: ContentFingerprint, fp2: ContentFingerprint) -> Dict:
        """
Detailed audio match analysis"""
        if not (fp1.audio_fingerprint and fp2.audio_fingerprint):
            return {}
            
        analysis = {}
        
        # Duration comparison
        dur1 = fp1.audio_fingerprint.get('duration', 0)
        dur2 = fp2.audio_fingerprint.get('duration', 0)
        analysis['duration_difference'] = abs(dur1 - dur2)
        
        # Tempo comparison
        tempo1 = fp1.audio_fingerprint.get('tempo', 0)
        tempo2 = fp2.audio_fingerprint.get('tempo', 0)
        analysis['tempo_difference'] = abs(tempo1 - tempo2)
        
        return analysis
        
    def _analyze_image_match(self, fp1: ContentFingerprint, fp2: ContentFingerprint) -> Dict:
        """
Detailed image match analysis"""
        if not (fp1.visual_features and fp2.visual_features):
            return {}
            
        analysis = {}
        
        # Dimension comparison
        dim1 = fp1.visual_features.get('dimensions', (0, 0))
        dim2 = fp2.visual_features.get('dimensions', (0, 0))
        analysis['dimension_match'] = dim1 == dim2
        analysis['resolution_difference'] = abs(dim1[0] * dim1[1] - dim2[0] * dim2[1])
        
        return analysis
        
    def _analyze_text_match(self, fp1: ContentFingerprint, fp2: ContentFingerprint) -> Dict:
        """
Detailed text match analysis"""
        if not (fp1.text_features and fp2.text_features):
            return {}
            
        analysis = {}
        
        # Length comparison
        len1 = fp1.text_features.get('length', 0)
        len2 = fp2.text_features.get('length', 0)
        analysis['length_difference'] = abs(len1 - len2)
        
        # Word count comparison
        wc1 = fp1.text_features.get('word_count', 0)
        wc2 = fp2.text_features.get('word_count', 0)
        analysis['word_count_difference'] = abs(wc1 - wc2)
        
        return analysis


# Import necessary modules
import io
