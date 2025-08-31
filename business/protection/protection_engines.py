"""
Advanced Protection Engines
Core AI-powered protection engines for content rights management

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""

import asyncio
import numpy as np
import tensorflow as tf
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
import logging
import json
import pickle
import hashlib
from pathlib import Path
import cv2
import librosa
from PIL import Image
import imagehash
from concurrent.futures import ThreadPoolExecutor, as_completed
import aiohttp
import requests
from urllib.parse import urlparse
import re

logger = logging.getLogger(__name__)


@dataclass
class ProtectionRule:
    """Content protection rule definition"""
    rule_id: str
    rule_name: str
    content_types: List[str]
    similarity_threshold: float
    enforcement_actions: List[str]
    priority_level: int  # 1-5, 5 being highest
    active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ThreatIntelligence:
    """Threat intelligence data"""
    threat_id: str
    threat_type: str
    indicators: List[str]
    confidence_score: float
    source: str
    first_seen: datetime
    last_updated: datetime
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL


class ContentHashingEngine:
    """Advanced content hashing for protection"""
    
    def __init__(self):
        self.hash_algorithms = ['md5', 'sha256', 'perceptual', 'semantic']
        self.feature_extractors = {}
        self.initialize_extractors()
    
    def initialize_extractors(self):
        """Initialize feature extraction models"""



        try:
            # Initialize text embeddings model
            self.text_tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2', local_files_only=False)
            self.text_model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2', local_files_only=False)
            
            logger.info("Content hashing engine initialized successfully")
        except Exception as e:
            logger.warning(f"Could not initialize some extractors: {str(e)}")
            self.text_tokenizer = None
            self.text_model = None
    
    def generate_multi_hash(self, content: Any, content_type: str) -> Dict[str, str]:
        """Generate multiple hash signatures for content"""



        try:
            hashes = {}
            
            if content_type == 'image':
                hashes.update(self._hash_image(content))
            elif content_type == 'audio':
                hashes.update(self._hash_audio(content))
            elif content_type == 'video':
                hashes.update(self._hash_video(content))
            elif content_type == 'text':
                hashes.update(self._hash_text(content))
            
            logger.debug(f"Generated {len(hashes)} hashes for {content_type}")
            return hashes
            
        except Exception as e:
            logger.error(f"Error generating multi-hash: {str(e)}")
            return {}
    
    def _hash_image(self, image_path: str) -> Dict[str, str]:
        """Generate image hashes"""



        try:
            image = Image.open(image_path)
            
            return {
                'md5': self._file_hash(image_path, 'md5'),
                'sha256': self._file_hash(image_path, 'sha256'),
                'perceptual': str(imagehash.phash(image)),
                'difference': str(imagehash.dhash(image)),
                'average': str(imagehash.average_hash(image)),
                'wavelet': str(imagehash.whash(image)),
                'color_moment': self._color_moment_hash(image)
            }
        except Exception as e:
            logger.error(f"Error hashing image: {str(e)}")
            return {}
    
    def _hash_audio(self, audio_path: str) -> Dict[str, str]:
        """Generate audio hashes"""



        try:
            y, sr = librosa.load(audio_path, duration=30)
            
            # Spectral features
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            chroma = librosa.feature.chroma(y=y, sr=sr)
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
            
            # Create feature signatures
            mfcc_hash = hashlib.sha256(np.mean(mfcc, axis=1).tobytes()).hexdigest()
            chroma_hash = hashlib.sha256(np.mean(chroma, axis=1).tobytes()).hexdigest()
            spectral_hash = hashlib.sha256(np.mean(spectral_centroid).tobytes()).hexdigest()
            
            return {
                'md5': self._file_hash(audio_path, 'md5'),
                'sha256': self._file_hash(audio_path, 'sha256'),
                'mfcc_signature': mfcc_hash,
                'chroma_signature': chroma_hash,
                'spectral_signature': spectral_hash,
                'audio_fingerprint': self._create_audio_fingerprint(y, sr)
            }
        except Exception as e:
            logger.error(f"Error hashing audio: {str(e)}")
            return {}
    
    def _hash_video(self, video_path: str) -> Dict[str, str]:
        """Generate video hashes"""



        try:
            cap = cv2.VideoCapture(video_path)
            frame_hashes = []
            
            # Sample frames
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            sample_count = min(20, frame_count)
            
            for i in range(sample_count):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i * (frame_count // sample_count))
                ret, frame = cap.read()
                if ret:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pil_frame = Image.fromarray(frame_rgb)
                    frame_hash = str(imagehash.phash(pil_frame))
                    frame_hashes.append(frame_hash)
            
            cap.release()
            
            # Create composite hashes
            frame_sequence = ''.join(frame_hashes)
            composite_hash = hashlib.sha256(frame_sequence.encode()).hexdigest()
            
            return {
                'md5': self._file_hash(video_path, 'md5'),
                'sha256': self._file_hash(video_path, 'sha256'),
                'frame_composite': composite_hash,
                'frame_sequence': hashlib.md5(frame_sequence.encode()).hexdigest(),
                'temporal_signature': self._create_temporal_signature(frame_hashes)
            }
        except Exception as e:
            logger.error(f"Error hashing video: {str(e)}")
            return {}
    
    def _hash_text(self, text_content: str) -> Dict[str, str]:
        """Generate text hashes"""



        try:
            # Basic hashes
            hashes = {
                'md5': hashlib.md5(text_content.encode()).hexdigest(),
                'sha256': hashlib.sha256(text_content.encode()).hexdigest()
            }
            
            # Semantic hash using embeddings
            if self.text_model and self.text_tokenizer:
                semantic_hash = self._create_semantic_hash(text_content)
                hashes['semantic'] = semantic_hash
            
            # N-gram hashes
            hashes.update(self._create_ngram_hashes(text_content))
            
            return hashes
        except Exception as e:
            logger.error(f"Error hashing text: {str(e)}")
            return {}
    
    def _file_hash(self, file_path: str, algorithm: str) -> str:
        """Calculate file hash"""
        hash_func = getattr(hashlib, algorithm)()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    
    def _color_moment_hash(self, image: Image) -> str:
        """Create color moment based hash"""



        try:
            img_array = np.array(image)
            if len(img_array.shape) == 3:
                # Calculate moments for each channel
                moments = []
                for channel in range(img_array.shape[2]):
                    channel_data = img_array[:,:,channel].flatten()
                    mean = np.mean(channel_data)
                    std = np.std(channel_data)
                    skew = np.mean(((channel_data - mean) / std) ** 3) if std > 0 else 0
                    moments.extend([mean, std, skew])
                
                moment_bytes = np.array(moments).tobytes()
                return hashlib.md5(moment_bytes).hexdigest()
            return hashlib.md5(img_array.tobytes()).hexdigest()
        except:
            return "color_moment_error"
    
    def _create_audio_fingerprint(self, y: np.ndarray, sr: int) -> str:
        """Create compact audio fingerprint"""



        try:
            # Create spectral fingerprint
            stft = librosa.stft(y, n_fft=2048, hop_length=512)
            magnitude = np.abs(stft)
            
            # Reduce dimensionality
            fingerprint = np.mean(magnitude, axis=1)[:256]  # Take first 256 frequency bins
            
            return hashlib.sha256(fingerprint.tobytes()).hexdigest()
        except:
            return "audio_fingerprint_error"
    
    def _create_temporal_signature(self, frame_hashes: List[str]) -> str:
        """Create temporal signature from frame sequence"""



        try:
            # Analyze hash differences between consecutive frames
            transitions = []
            for i in range(1, len(frame_hashes)):
                # Calculate Hamming distance between consecutive frame hashes
                if len(frame_hashes[i]) == len(frame_hashes[i-1]):
                    distance = sum(c1 != c2 for c1, c2 in zip(frame_hashes[i], frame_hashes[i-1]))
                    transitions.append(str(distance))
            
            transition_signature = ''.join(transitions)
            return hashlib.md5(transition_signature.encode()).hexdigest()
        except:
            return "temporal_signature_error"
    
    def _create_semantic_hash(self, text: str) -> str:
        """Create semantic hash using text embeddings"""



        try:
            inputs = self.text_tokenizer(text, return_tensors='pt', truncate=True, max_length=512)
            with torch.no_grad():
                outputs = self.text_model(**inputs)
                embeddings = outputs.last_hidden_state.mean(dim=1)
                
            # Convert to hash
            embedding_bytes = embeddings.numpy().tobytes()
            return hashlib.sha256(embedding_bytes).hexdigest()
        except:
            return "semantic_hash_error"
    
    def _create_ngram_hashes(self, text: str, n_values: List[int] = [2, 3, 4]) -> Dict[str, str]:
        """Create n-gram based hashes"""



        try:
            hashes = {}
            words = text.lower().split()
            
            for n in n_values:
                if len(words) >= n:
                    ngrams = [' '.join(words[i:i+n]) for i in range(len(words)-n+1)]
                    ngram_signature = '|'.join(sorted(set(ngrams))[:50])  # Top 50 unique n-grams
                    hashes[f'{n}gram'] = hashlib.md5(ngram_signature.encode()).hexdigest()
            
            return hashes
        except:
            return {}


class AnomalyDetectionEngine:
    """ML-based anomaly detection for suspicious activities"""
    
    def __init__(self):
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_columns = [
            'upload_frequency', 'content_similarity', 'account_age', 
            'follower_count', 'engagement_rate', 'content_diversity',
            'upload_time_variance', 'location_changes', 'device_changes'
        ]
    
    def train_model(self, normal_behavior_data: List[Dict[str, float]]):
        """Train anomaly detection model on normal behavior"""



        try:
            if not normal_behavior_data:
                raise ValueError("No training data provided")
            
            # Convert to feature matrix
            feature_matrix = self._extract_features(normal_behavior_data)
            
            # Scale features
            scaled_features = self.scaler.fit_transform(feature_matrix)
            
            # Train isolation forest
            self.isolation_forest.fit(scaled_features)
            self.is_trained = True
            
            logger.info(f"Anomaly detection model trained on {len(normal_behavior_data)} samples")
            
        except Exception as e:
            logger.error(f"Error training anomaly detection model: {str(e)}")
            raise
    
    def detect_anomalies(self, user_behaviors: List[Dict[str, float]]) -> List[Dict[str, Any]]:
        """Detect anomalous user behaviors"""



        try:
            if not self.is_trained:
                raise ValueError("Model not trained yet")
            
            # Extract features
            feature_matrix = self._extract_features(user_behaviors)
            scaled_features = self.scaler.transform(feature_matrix)
            
            # Predict anomalies
            anomaly_scores = self.isolation_forest.decision_function(scaled_features)
            anomaly_predictions = self.isolation_forest.predict(scaled_features)
            
            results = []
            for i, behavior in enumerate(user_behaviors):
                result = {
                    'user_id': behavior.get('user_id'),
                    'is_anomaly': anomaly_predictions[i] == -1,
                    'anomaly_score': float(anomaly_scores[i]),
                    'confidence': self._calculate_confidence(anomaly_scores[i]),
                    'behavior_data': behavior,
                    'flagged_features': self._identify_suspicious_features(behavior)
                }
                results.append(result)
            
            anomaly_count = sum(1 for r in results if r['is_anomaly'])
            logger.info(f"Detected {anomaly_count} anomalies out of {len(results)} behaviors")
            
            return results
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {str(e)}")
            raise
    
    def _extract_features(self, behaviors: List[Dict[str, float]]) -> np.ndarray:
        """Extract feature matrix from behavior data"""
        feature_matrix = []
        
        for behavior in behaviors:
            features = []
            for column in self.feature_columns:
                features.append(behavior.get(column, 0.0))
            feature_matrix.append(features)
        
        return np.array(feature_matrix)
    
    def _calculate_confidence(self, anomaly_score: float) -> float:
        """Calculate confidence score for anomaly detection"""
        # Normalize anomaly score to 0-1 confidence
        normalized_score = 1 / (1 + np.exp(anomaly_score * 5))  # Sigmoid transformation
        return float(normalized_score)
    
    def _identify_suspicious_features(self, behavior: Dict[str, float]) -> List[str]:
        """Identify which features contribute to anomalous behavior"""
        suspicious_features = []
        
        # Define thresholds for suspicious behavior
        thresholds = {
            'upload_frequency': (0, 50),  # uploads per day
            'content_similarity': (0.8, 1.0),  # very high similarity
            'engagement_rate': (0, 0.01),  # very low engagement
            'upload_time_variance': (0, 2),  # very consistent upload times
            'location_changes': (5, float('inf')),  # frequent location changes
            'device_changes': (3, float('inf'))  # frequent device changes
        }
        
        for feature, (min_val, max_val) in thresholds.items():
            value = behavior.get(feature, 0)
            if min_val <= value <= max_val:
                suspicious_features.append(feature)
        
        return suspicious_features


class ContentSimilarityEngine:
    """Advanced content similarity detection"""
    
    def __init__(self):
        self.similarity_thresholds = {
            'identical': 0.98,
            'near_duplicate': 0.90,
            'similar': 0.75,
            'related': 0.60
        }
        self.feature_weights = {
            'perceptual': 0.4,
            'structural': 0.3,
            'semantic': 0.3
        }
    
    def compare_content(self, content1: Dict[str, Any], content2: Dict[str, Any]) -> Dict[str, float]:
        """Compare two pieces of content for similarity"""



        try:
            content_type = content1.get('type', 'unknown')
            
            if content_type == 'image':
                return self._compare_images(content1, content2)
            elif content_type == 'audio':
                return self._compare_audio(content1, content2)
            elif content_type == 'video':
                return self._compare_videos(content1, content2)
            elif content_type == 'text':
                return self._compare_text(content1, content2)
            else:
                raise ValueError(f"Unsupported content type: {content_type}")
                
        except Exception as e:
            logger.error(f"Error comparing content: {str(e)}")
            return {'overall_similarity': 0.0, 'error': str(e)}
    
    def _compare_images(self, img1: Dict[str, Any], img2: Dict[str, Any]) -> Dict[str, float]:
        """Compare image similarity"""



        try:
            # Hash-based comparison
            hash_similarity = self._compare_image_hashes(img1['hashes'], img2['hashes'])
            
            # Feature-based comparison
            feature_similarity = self._compare_image_features(img1['features'], img2['features'])
            
            # Structural comparison (if available)
            structural_similarity = self._compare_image_structure(img1.get('structure', {}), img2.get('structure', {}))
            
            # Weighted combination
            overall_similarity = (
                hash_similarity * 0.5 +
                feature_similarity * 0.3 +
                structural_similarity * 0.2
            )
            
            return {
                'overall_similarity': overall_similarity,
                'hash_similarity': hash_similarity,
                'feature_similarity': feature_similarity,
                'structural_similarity': structural_similarity,
                'similarity_level': self._classify_similarity(overall_similarity)
            }
            
        except Exception as e:
            logger.error(f"Error comparing images: {str(e)}")
            return {'overall_similarity': 0.0, 'error': str(e)}
    
    def _compare_audio(self, audio1: Dict[str, Any], audio2: Dict[str, Any]) -> Dict[str, float]:
        """Compare audio similarity"""



        try:
            # Spectral feature comparison
            spectral_similarity = self._compare_audio_features(audio1['features'], audio2['features'])
            
            # Temporal pattern comparison
            temporal_similarity = self._compare_temporal_patterns(
                audio1.get('temporal_features', {}), 
                audio2.get('temporal_features', {})
            )
            
            # Hash comparison
            hash_similarity = self._compare_audio_hashes(audio1['hashes'], audio2['hashes'])
            
            overall_similarity = (
                spectral_similarity * 0.4 +
                temporal_similarity * 0.3 +
                hash_similarity * 0.3
            )
            
            return {
                'overall_similarity': overall_similarity,
                'spectral_similarity': spectral_similarity,
                'temporal_similarity': temporal_similarity,
                'hash_similarity': hash_similarity,
                'similarity_level': self._classify_similarity(overall_similarity)
            }
            
        except Exception as e:
            logger.error(f"Error comparing audio: {str(e)}")
            return {'overall_similarity': 0.0, 'error': str(e)}
    
    def _compare_videos(self, video1: Dict[str, Any], video2: Dict[str, Any]) -> Dict[str, float]:
        """Compare video similarity"""



        try:
            # Frame-based comparison
            frame_similarity = self._compare_video_frames(video1.get('frames', []), video2.get('frames', []))
            
            # Motion analysis
            motion_similarity = self._compare_motion_patterns(
                video1.get('motion_features', {}),
                video2.get('motion_features', {})
            )
            
            # Audio track comparison (if available)
            audio_similarity = 0.0
            if 'audio_features' in video1 and 'audio_features' in video2:
                audio_similarity = self._compare_audio_features(
                    video1['audio_features'], 
                    video2['audio_features']
                )
            
            overall_similarity = (
                frame_similarity * 0.5 +
                motion_similarity * 0.3 +
                audio_similarity * 0.2
            )
            
            return {
                'overall_similarity': overall_similarity,
                'frame_similarity': frame_similarity,
                'motion_similarity': motion_similarity,
                'audio_similarity': audio_similarity,
                'similarity_level': self._classify_similarity(overall_similarity)
            }
            
        except Exception as e:
            logger.error(f"Error comparing videos: {str(e)}")
            return {'overall_similarity': 0.0, 'error': str(e)}
    
    def _compare_text(self, text1: Dict[str, Any], text2: Dict[str, Any]) -> Dict[str, float]:
        """Compare text similarity"""



        try:
            # Exact matching
            exact_similarity = 1.0 if text1.get('content', '') == text2.get('content', '') else 0.0
            
            # N-gram similarity
            ngram_similarity = self._compare_ngrams(
                text1.get('ngrams', {}), 
                text2.get('ngrams', {})
            )
            
            # Semantic similarity
            semantic_similarity = self._compare_semantic_features(
                text1.get('semantic_features', {}),
                text2.get('semantic_features', {})
            )
            
            # Structural similarity
            structural_similarity = self._compare_text_structure(
                text1.get('structure', {}),
                text2.get('structure', {})
            )
            
            overall_similarity = (
                exact_similarity * 0.3 +
                ngram_similarity * 0.3 +
                semantic_similarity * 0.25 +
                structural_similarity * 0.15
            )
            
            return {
                'overall_similarity': overall_similarity,
                'exact_similarity': exact_similarity,
                'ngram_similarity': ngram_similarity,
                'semantic_similarity': semantic_similarity,
                'structural_similarity': structural_similarity,
                'similarity_level': self._classify_similarity(overall_similarity)
            }
            
        except Exception as e:
            logger.error(f"Error comparing text: {str(e)}")
            return {'overall_similarity': 0.0, 'error': str(e)}
    
    def _compare_image_hashes(self, hashes1: Dict[str, str], hashes2: Dict[str, str]) -> float:
        """Compare image hashes"""



        try:
            similarities = []
            
            # Exact hash matches
            exact_matches = ['md5', 'sha256']
            for hash_type in exact_matches:
                if hash_type in hashes1 and hash_type in hashes2:
                    similarities.append(1.0 if hashes1[hash_type] == hashes2[hash_type] else 0.0)
            
            # Perceptual hash similarity
            perceptual_hashes = ['perceptual', 'difference', 'average', 'wavelet']
            for hash_type in perceptual_hashes:
                if hash_type in hashes1 and hash_type in hashes2:
                    # Calculate Hamming distance for perceptual hashes
                    hamming_distance = sum(c1 != c2 for c1, c2 in zip(hashes1[hash_type], hashes2[hash_type]))
                    max_distance = len(hashes1[hash_type])
                    similarity = 1.0 - (hamming_distance / max_distance) if max_distance > 0 else 0.0
                    similarities.append(similarity)
            
            return np.mean(similarities) if similarities else 0.0
            
        except Exception as e:
            logger.error(f"Error comparing image hashes: {str(e)}")
            return 0.0
    
    def _compare_image_features(self, features1: Dict[str, List[float]], features2: Dict[str, List[float]]) -> float:
        """Compare image feature vectors"""



        try:
            similarities = []
            
            common_features = set(features1.keys()) & set(features2.keys())
            for feature_type in common_features:
                vec1 = np.array(features1[feature_type])
                vec2 = np.array(features2[feature_type])
                
                if len(vec1) == len(vec2) and len(vec1) > 0:
                    # Cosine similarity
                    dot_product = np.dot(vec1, vec2)
                    norm1 = np.linalg.norm(vec1)
                    norm2 = np.linalg.norm(vec2)
                    
                    if norm1 > 0 and norm2 > 0:
                        similarity = dot_product / (norm1 * norm2)
                        similarities.append(max(0, similarity))
            
            return np.mean(similarities) if similarities else 0.0
            
        except Exception as e:
            logger.error(f"Error comparing image features: {str(e)}")
            return 0.0
    
    def _compare_audio_features(self, features1: Dict[str, List[float]], features2: Dict[str, List[float]]) -> float:
        """Compare audio feature vectors"""



        return self._compare_image_features(features1, features2)  # Same logic
    
    def _compare_ngrams(self, ngrams1: Dict[str, str], ngrams2: Dict[str, str]) -> float:
        """Compare n-gram hashes"""



        try:
            similarities = []
            
            common_ngrams = set(ngrams1.keys()) & set(ngrams2.keys())
            for ngram_type in common_ngrams:
                similarity = 1.0 if ngrams1[ngram_type] == ngrams2[ngram_type] else 0.0
                similarities.append(similarity)
            
            return np.mean(similarities) if similarities else 0.0
            
        except Exception as e:
            logger.error(f"Error comparing n-grams: {str(e)}")
            return 0.0
    
    def _classify_similarity(self, similarity_score: float) -> str:
        """Classify similarity level"""
        for level, threshold in self.similarity_thresholds.items():
            if similarity_score >= threshold:
                return level
        return 'different'
    
    # Placeholder methods for advanced comparison features
    def _compare_image_structure(self, struct1: Dict, struct2: Dict) -> float:
        """Compare structural features of images"""



        return 0.5  # Placeholder
    
    def _compare_temporal_patterns(self, temp1: Dict, temp2: Dict) -> float:
        """Compare temporal patterns in audio"""



        return 0.5  # Placeholder
    
    def _compare_audio_hashes(self, hashes1: Dict, hashes2: Dict) -> float:
        """Compare audio-specific hashes"""



        return self._compare_image_hashes(hashes1, hashes2)  # Reuse logic
    
    def _compare_video_frames(self, frames1: List, frames2: List) -> float:
        """Compare video frame sequences"""



        return 0.5  # Placeholder
    
    def _compare_motion_patterns(self, motion1: Dict, motion2: Dict) -> float:
        """Compare motion patterns in video"""



        return 0.5  # Placeholder
    
    def _compare_semantic_features(self, sem1: Dict, sem2: Dict) -> float:
        """Compare semantic text features"""



        return 0.5  # Placeholder
    
    def _compare_text_structure(self, struct1: Dict, struct2: Dict) -> float:
        """Compare text structural features"""



        return 0.5  # Placeholder


class ThreatIntelligenceEngine:
    """Threat intelligence gathering and analysis"""
    
    def __init__(self):
        self.threat_database: List[ThreatIntelligence] = []
        self.known_infringers = set()
        self.suspicious_patterns = {}
    
    def add_threat_intelligence(self, threat: ThreatIntelligence):
        """Add new threat intelligence"""
        self.threat_database.append(threat)
        
        # Update known infringers
        if threat.threat_type == 'copyright_infringer':
            self.known_infringers.update(threat.indicators)
        
        logger.info(f"Added threat intelligence: {threat.threat_id}")
    
    def check_threat_indicators(self, content_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check content against known threat indicators"""



        try:
            matches = []
            
            for threat in self.threat_database:
                for indicator in threat.indicators:
                    if self._matches_indicator(content_data, indicator):
                        match = {
                            'threat_id': threat.threat_id,
                            'threat_type': threat.threat_type,
                            'indicator': indicator,
                            'confidence': threat.confidence_score,
                            'severity': threat.severity,
                            'first_seen': threat.first_seen.isoformat(),
                            'match_details': self._analyze_match(content_data, indicator)
                        }
                        matches.append(match)
            
            return matches
            
        except Exception as e:
            logger.error(f"Error checking threat indicators: {str(e)}")
            return []
    
    def _matches_indicator(self, content_data: Dict[str, Any], indicator: str) -> bool:
        """Check if content matches threat indicator"""



        try:
            # Check various fields for indicator presence
            searchable_fields = [
                'user_id', 'username', 'email', 'ip_address', 
                'user_agent', 'description', 'tags'
            ]
            
            for field in searchable_fields:
                value = content_data.get(field, '')
                if isinstance(value, str) and indicator.lower() in value.lower():
                    return True
                elif isinstance(value, list):
                    if any(indicator.lower() in str(item).lower() for item in value):
                        return True
            
            return False
            
        except Exception:
            return False
    
    def _analyze_match(self, content_data: Dict[str, Any], indicator: str) -> Dict[str, Any]:
        """Analyze details of threat indicator match"""



        return {
            'matched_fields': [
                field for field in content_data.keys() 
                if indicator.lower() in str(content_data.get(field, '')).lower()
            ],
            'match_strength': 'exact' if indicator in str(content_data) else 'partial'
        }


class AdvancedProtectionEngine:
    """Main protection engine coordinating all protection mechanisms"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.hashing_engine = ContentHashingEngine()
        self.anomaly_engine = AnomalyDetectionEngine()
        self.similarity_engine = ContentSimilarityEngine()
        self.threat_intelligence = ThreatIntelligenceEngine()
        
        self.protection_rules: List[ProtectionRule] = []
        self.protection_stats = {
            'content_analyzed': 0,
            'threats_detected': 0,
            'anomalies_found': 0,
            'violations_prevented': 0
        }
    
    async def analyze_content_protection(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive content protection analysis"""



        try:
            analysis_results = {
                'content_id': content_data.get('content_id'),
                'analysis_timestamp': datetime.now(timezone.utc).isoformat(),
                'protection_score': 0.0,
                'threat_level': 'LOW',
                'findings': [],
                'recommendations': []
            }
            
            # Generate content hashes
            content_hashes = self.hashing_engine.generate_multi_hash(
                content_data.get('file_path', ''), 
                content_data.get('content_type', 'unknown')
            )
            analysis_results['content_hashes'] = content_hashes
            
            # Check threat intelligence
            threat_matches = self.threat_intelligence.check_threat_indicators(content_data)
            if threat_matches:
                analysis_results['findings'].extend(threat_matches)
                analysis_results['threat_level'] = 'HIGH'
                analysis_results['protection_score'] -= 0.3
            
            # Analyze user behavior (if available)
            if 'user_behavior' in content_data:
                anomaly_results = self.anomaly_engine.detect_anomalies([content_data['user_behavior']])
                if anomaly_results and anomaly_results[0]['is_anomaly']:
                    analysis_results['findings'].append({
                        'type': 'behavioral_anomaly',
                        'confidence': anomaly_results[0]['confidence'],
                        'suspicious_features': anomaly_results[0]['flagged_features']
                    })
                    analysis_results['protection_score'] -= 0.2
            
            # Apply protection rules
            rule_results = self._apply_protection_rules(content_data, analysis_results)
            analysis_results['rule_matches'] = rule_results
            
            # Calculate final protection score
            base_score = 1.0
            analysis_results['protection_score'] = max(0.0, base_score + analysis_results['protection_score'])
            
            # Generate recommendations
            analysis_results['recommendations'] = self._generate_recommendations(analysis_results)
            
            # Update statistics
            self.protection_stats['content_analyzed'] += 1
            if analysis_results['threat_level'] in ['HIGH', 'CRITICAL']:
                self.protection_stats['threats_detected'] += 1
            
            logger.info(f"Content protection analysis completed for {analysis_results['content_id']}")
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error in content protection analysis: {str(e)}")
            raise
    
    def add_protection_rule(self, rule: ProtectionRule):
        """Add new protection rule"""
        self.protection_rules.append(rule)
        logger.info(f"Added protection rule: {rule.rule_name}")
    
    def _apply_protection_rules(self, content_data: Dict[str, Any], analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply protection rules to content"""
        rule_matches = []
        
        for rule in self.protection_rules:
            if not rule.active:
                continue
            
            if content_data.get('content_type') in rule.content_types:
                # Check rule conditions
                match_result = self._evaluate_protection_rule(rule, content_data, analysis_results)
                if match_result['matches']:
                    rule_matches.append({
                        'rule_id': rule.rule_id,
                        'rule_name': rule.rule_name,
                        'priority': rule.priority_level,
                        'enforcement_actions': rule.enforcement_actions,
                        'match_details': match_result
                    })
        
        return rule_matches
    
    def _evaluate_protection_rule(self, rule: ProtectionRule, content_data: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate if content matches protection rule"""
        # Simplified rule evaluation - can be extended with complex rule engine
        matches = False
        details = {}
        
        # Example rule evaluation logic
        if 'similarity_threshold' in rule.metadata:
            threshold = rule.metadata['similarity_threshold']
            if analysis['protection_score'] < threshold:
                matches = True
                details['reason'] = 'Low protection score'
        
        if analysis['threat_level'] in ['HIGH', 'CRITICAL']:
            matches = True
            details['reason'] = 'High threat level detected'
        
        return {
            'matches': matches,
            'details': details,
            'evaluation_timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    def _generate_recommendations(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate protection recommendations"""
        recommendations = []
        
        if analysis_results['threat_level'] in ['HIGH', 'CRITICAL']:
            recommendations.append("Immediate enforcement action required")
            recommendations.append("Consider blocking or removing content")
        
        if analysis_results['protection_score'] < 0.5:
            recommendations.append("Enhance content protection measures")
            recommendations.append("Monitor for potential copyright violations")
        
        if any(f['type'] == 'behavioral_anomaly' for f in analysis_results['findings']):
            recommendations.append("Investigate user behavior patterns")
            recommendations.append("Consider additional verification requirements")
        
        return recommendations
    
    def get_protection_statistics(self) -> Dict[str, Any]:
        """Get protection engine statistics"""



        return {
            **self.protection_stats,
            'active_rules': len([r for r in self.protection_rules if r.active]),
            'threat_database_size': len(self.threat_intelligence.threat_database),
            'known_infringers': len(self.threat_intelligence.known_infringers)
        }


# Export main classes
__all__ = [
    'ProtectionRule',
    'ThreatIntelligence',
    'ContentHashingEngine',
    'AnomalyDetectionEngine', 
    'ContentSimilarityEngine',
    'ThreatIntelligenceEngine',
    'AdvancedProtectionEngine'
]
