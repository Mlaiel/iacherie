"""Pattern Recognition Engine - Advanced Pattern Detection & Analysis
=================================================================

Industrial-grade pattern recognition engine for multi-modal content analysis providing:
- Multi-Modal Pattern Detection (Audio, Video, Image, Text)
- Temporal Pattern Analysis
- Content Similarity Pattern Matching
- Anomaly Detection in Content Patterns
- Trend Pattern Recognition
- Behavioral Pattern Analysis
- Cross-Platform Pattern Correlation
- Real-time Pattern Classification

Created by: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use strictly prohibited
"""import numpy as np
import cv2
import librosa
import torch
import torch.nn as nn
from sklearn.cluster import DBSCAN, KMeans
from sklearn.ensemble import IsolationForest
from sklearn.metrics.pairwise import cosine_similarity
from scipy import signal
from scipy.stats import entropy
from typing import Dict, List, Any, Optional, Tuple, Union
import logging
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import json
import pandas as pd

logger = logging.getLogger(__name__)

class PatternType(Enum):
    """Types of patterns that can be detected"""    TEMPORAL = "temporal"           # Time-based patterns
    SPATIAL = "spatial"             # Space-based patterns  
    FREQUENCY = "frequency"         # Frequency domain patterns
    SEMANTIC = "semantic"           # Meaning-based patterns
    BEHAVIORAL = "behavioral"       # User behavior patterns
    STRUCTURAL = "structural"       # Content structure patterns
    ANOMALY = "anomaly"            # Anomalous patterns
    TREND = "trend"                # Trending patterns

class ContentModality(Enum):
    """Content modalities for pattern analysis"""    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    MULTIMODAL = "multimodal"

@dataclass
class PatternConfig:
    """Configuration for pattern recognition"""    pattern_types: List[PatternType]
    modalities: List[ContentModality]
    sensitivity: float = 0.5
    temporal_window: int = 100
    min_pattern_length: int = 3
    max_pattern_length: int = 50
    enable_anomaly_detection: bool = True
    enable_trend_analysis: bool = True

@dataclass
class DetectedPattern:
    """Detected pattern information"""    pattern_id: str
    pattern_type: PatternType
    modality: ContentModality
    confidence_score: float
    pattern_data: Dict[str, Any]
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    spatial_location: Optional[Tuple[int, int]] = None
    metadata: Dict[str, Any] = None

@dataclass
class PatternAnalysisResult:
    """Result of pattern analysis"""    content_id: str
    detected_patterns: List[DetectedPattern]
    pattern_statistics: Dict[str, Any]
    anomalies: List[DetectedPattern]
    trends: List[DetectedPattern]
    processing_time: float

class PatternRecognitionEngine:
    """    Industrial-grade pattern recognition engine for content analysis
    """    
    def __init__(self):
        self.pattern_database: Dict[str, List[DetectedPattern]] = {}
        self.anomaly_detectors: Dict[str, IsolationForest] = {}
        self.clustering_models: Dict[str, Any] = {}
        self.pattern_templates: Dict[str, np.ndarray] = {}
        
        # Initialize pattern recognition models
        self._initialize_models()
        
        logger.info("PatternRecognitionEngine initialized successfully")
    
    def _initialize_models(self) -> None:
        """Initialize pattern recognition models"""        try:
            # Initialize anomaly detectors
            self.anomaly_detectors = {
                'audio': IsolationForest(contamination=0.1, random_state=42),
                'video': IsolationForest(contamination=0.1, random_state=42),
                'image': IsolationForest(contamination=0.1, random_state=42),
                'text': IsolationForest(contamination=0.1, random_state=42)
            }
            
            # Initialize clustering models
            self.clustering_models = {
                'temporal': DBSCAN(eps=0.5, min_samples=3),
                'spatial': KMeans(n_clusters=8, random_state=42),
                'frequency': DBSCAN(eps=0.3, min_samples=2)
            }
            
            logger.info("Pattern recognition models initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize models: {e}")
            raise
    
    def analyze_patterns(self, content_data: Any, content_id: str, 
                        modality: ContentModality, config: PatternConfig) -> PatternAnalysisResult:
        """Analyze patterns in content"""        import time
        start_time = time.time()
        
        try:
            detected_patterns = []
            anomalies = []
            trends = []
            
            # Extract features for pattern analysis
            features = self._extract_pattern_features(content_data, modality)
            
            # Detect patterns for each requested type
            for pattern_type in config.pattern_types:
                patterns = self._detect_patterns_by_type(
                    features, pattern_type, modality, config
                )
                detected_patterns.extend(patterns)
            
            # Detect anomalies if enabled
            if config.enable_anomaly_detection:
                anomalies = self._detect_anomalies(features, modality)
            
            # Analyze trends if enabled
            if config.enable_trend_analysis:
                trends = self._analyze_trends(features, modality)
            
            # Calculate statistics
            pattern_statistics = self._calculate_pattern_statistics(detected_patterns)
            
            # Store patterns in database
            self.pattern_database[content_id] = detected_patterns
            
            processing_time = time.time() - start_time
            
            result = PatternAnalysisResult(
                content_id=content_id,
                detected_patterns=detected_patterns,
                pattern_statistics=pattern_statistics,
                anomalies=anomalies,
                trends=trends,
                processing_time=processing_time
            )
            
            logger.info(f"Pattern analysis completed for {content_id} in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Pattern analysis failed: {e}")
            raise
    
    def _extract_pattern_features(self, content_data: Any, modality: ContentModality) -> Dict[str, np.ndarray]:
        """Extract features for pattern analysis"""        features = {}
        
        try:
            if modality == ContentModality.AUDIO:
                features = self._extract_audio_pattern_features(content_data)
            elif modality == ContentModality.VIDEO:
                features = self._extract_video_pattern_features(content_data)
            elif modality == ContentModality.IMAGE:
                features = self._extract_image_pattern_features(content_data)
            elif modality == ContentModality.TEXT:
                features = self._extract_text_pattern_features(content_data)
            
            return features
            
        except Exception as e:
            logger.error(f"Feature extraction failed for {modality.value}: {e}")
            return {}
    
    def _extract_audio_pattern_features(self, audio_data: Any) -> Dict[str, np.ndarray]:
        """Extract audio features for pattern analysis"""        try:
            if isinstance(audio_data, str):
                y, sr = librosa.load(audio_data, sr=22050)
            else:
                y, sr = audio_data, 22050
            
            features = {}
            
            # Temporal features
            features['amplitude'] = np.abs(y)
            features['energy'] = librosa.feature.rms(y=y, hop_length=512)[0]
            
            # Spectral features
            stft = librosa.stft(y, hop_length=512)
            features['magnitude_spectrum'] = np.abs(stft)
            features['phase_spectrum'] = np.angle(stft)
            
            # Chromagram for harmonic patterns
            features['chromagram'] = librosa.feature.chroma_stft(y=y, sr=sr)
            
            # MFCC for timbral patterns
            features['mfcc'] = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
            
            # Onset detection for rhythmic patterns
            onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
            features['onset_times'] = librosa.frames_to_time(onset_frames, sr=sr)
            
            # Tempo and beat tracking
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            features['tempo'] = np.array([tempo])
            features['beat_times'] = librosa.frames_to_time(beats, sr=sr)
            
            return features
            
        except Exception as e:
            logger.error(f"Audio feature extraction failed: {e}")
            return {}
    
    def _extract_video_pattern_features(self, video_data: Any) -> Dict[str, np.ndarray]:
        """Extract video features for pattern analysis"""        try:
            if isinstance(video_data, str):
                cap = cv2.VideoCapture(video_data)
            else:
                cap = video_data
            
            features = {}
            frame_features = []
            optical_flow_features = []
            
            prev_frame = None
            frame_count = 0
            
            while True:
                if hasattr(cap, 'read'):
                    ret, frame = cap.read()
                    if not ret:
                        break
                else:
                    break
                
                # Convert to grayscale
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Extract frame-level features
                frame_feature = self._extract_frame_features(frame, gray_frame)
                frame_features.append(frame_feature)
                
                # Optical flow for motion patterns
                if prev_frame is not None:
                    flow = cv2.calcOpticalFlowPyrLK(
                        prev_frame, gray_frame, None, None
                    )[0]
                    if flow is not None:
                        flow_magnitude = np.sqrt(flow[:, :, 0]**2 + flow[:, :, 1]**2)
                        optical_flow_features.append(np.mean(flow_magnitude))
                
                prev_frame = gray_frame
                frame_count += 1
                
                # Limit processing for performance
                if frame_count > 100:
                    break
            
            if hasattr(cap, 'release'):
                cap.release()
            
            # Compile features
            if frame_features:
                features['frame_features'] = np.array(frame_features)
            if optical_flow_features:
                features['optical_flow'] = np.array(optical_flow_features)
            
            # Scene change detection
            if len(frame_features) > 1:
                frame_diffs = np.diff(np.array(frame_features), axis=0)
                features['scene_changes'] = np.linalg.norm(frame_diffs, axis=1)
            
            return features
            
        except Exception as e:
            logger.error(f"Video feature extraction failed: {e}")
            return {}
    
    def _extract_frame_features(self, color_frame: np.ndarray, gray_frame: np.ndarray) -> np.ndarray:
        """Extract features from a single video frame"""        features = []
        
        # Color histogram
        for i in range(3):  # RGB channels
            hist = cv2.calcHist([color_frame], [i], None, [32], [0, 256])
            features.extend(hist.flatten())
        
        # Texture features (simplified)
        mean_intensity = np.mean(gray_frame)
        std_intensity = np.std(gray_frame)
        features.extend([mean_intensity, std_intensity])
        
        # Edge density
        edges = cv2.Canny(gray_frame, 50, 150)
        edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
        features.append(edge_density)
        
        return np.array(features)
    
    def _extract_image_pattern_features(self, image_data: Any) -> Dict[str, np.ndarray]:
        """Extract image features for pattern analysis"""        try:
            if isinstance(image_data, str):
                image = cv2.imread(image_data)
            else:
                image = image_data
            
            features = {}
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Spatial patterns
            features['pixel_intensities'] = gray_image.flatten()
            
            # Frequency domain patterns
            fft = np.fft.fft2(gray_image)
            features['frequency_magnitude'] = np.abs(fft).flatten()
            features['frequency_phase'] = np.angle(fft).flatten()
            
            # Edge patterns
            edges = cv2.Canny(gray_image, 50, 150)
            features['edge_map'] = edges.flatten()
            
            # Corner patterns
            corners = cv2.goodFeaturesToTrack(gray_image, maxCorners=100, 
                                            qualityLevel=0.01, minDistance=10)
            if corners is not None:
                features['corner_locations'] = corners.flatten()
            else:
                features['corner_locations'] = np.array([])
            
            # Color patterns
            for i, color in enumerate(['blue', 'green', 'red']):
                channel = image[:, :, i]
                features[f'{color}_channel'] = channel.flatten()
            
            return features
            
        except Exception as e:
            logger.error(f"Image feature extraction failed: {e}")
            return {}
    
    def _extract_text_pattern_features(self, text_data: Any) -> Dict[str, np.ndarray]:
        """Extract text features for pattern analysis"""        try:
            if isinstance(text_data, str):
                if text_data.endswith('.txt'):
                    with open(text_data, 'r', encoding='utf-8') as f:
                        text = f.read()
                else:
                    text = text_data
            else:
                text = str(text_data)
            
            features = {}
            
            # Character-level patterns
            char_frequencies = {}
            for char in text.lower():
                char_frequencies[char] = char_frequencies.get(char, 0) + 1
            
            # Convert to array (top 26 letters + space)
            common_chars = 'abcdefghijklmnopqrstuvwxyz '
            char_freq_array = [char_frequencies.get(char, 0) for char in common_chars]
            features['character_frequencies'] = np.array(char_freq_array)
            
            # Word-level patterns
            words = text.lower().split()
            word_lengths = [len(word) for word in words]
            features['word_lengths'] = np.array(word_lengths)
            
            # Sentence-level patterns
            sentences = text.split('.')
            sentence_lengths = [len(sentence.split()) for sentence in sentences if sentence.strip()]
            features['sentence_lengths'] = np.array(sentence_lengths)
            
            # N-gram patterns
            bigrams = [text[i:i+2] for i in range(len(text)-1)]
            bigram_frequencies = {}
            for bigram in bigrams:
                bigram_frequencies[bigram] = bigram_frequencies.get(bigram, 0) + 1
            
            # Top bigrams
            top_bigrams = sorted(bigram_frequencies.items(), key=lambda x: x[1], reverse=True)[:50]
            features['top_bigram_frequencies'] = np.array([freq for _, freq in top_bigrams])
            
            return features
            
        except Exception as e:
            logger.error(f"Text feature extraction failed: {e}")
            return {}
    
    def _detect_patterns_by_type(self, features: Dict[str, np.ndarray], 
                                pattern_type: PatternType, modality: ContentModality,
                                config: PatternConfig) -> List[DetectedPattern]:
        """Detect patterns of specific type"""        patterns = []
        
        try:
            if pattern_type == PatternType.TEMPORAL:
                patterns = self._detect_temporal_patterns(features, modality, config)
            elif pattern_type == PatternType.SPATIAL:
                patterns = self._detect_spatial_patterns(features, modality, config)
            elif pattern_type == PatternType.FREQUENCY:
                patterns = self._detect_frequency_patterns(features, modality, config)
            elif pattern_type == PatternType.SEMANTIC:
                patterns = self._detect_semantic_patterns(features, modality, config)
            elif pattern_type == PatternType.BEHAVIORAL:
                patterns = self._detect_behavioral_patterns(features, modality, config)
            elif pattern_type == PatternType.STRUCTURAL:
                patterns = self._detect_structural_patterns(features, modality, config)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Pattern detection failed for {pattern_type.value}: {e}")
            return []
    
    def _detect_temporal_patterns(self, features: Dict[str, np.ndarray], 
                                 modality: ContentModality, config: PatternConfig) -> List[DetectedPattern]:
        """Detect temporal patterns in content"""        patterns = []
        
        try:
            # Look for time-series features
            time_series_features = []
            
            if modality == ContentModality.AUDIO:
                if 'energy' in features:
                    time_series_features.append(('energy', features['energy']))
                if 'onset_times' in features:
                    time_series_features.append(('onsets', features['onset_times']))
            
            elif modality == ContentModality.VIDEO:
                if 'optical_flow' in features:
                    time_series_features.append(('motion', features['optical_flow']))
                if 'scene_changes' in features:
                    time_series_features.append(('scene_changes', features['scene_changes']))
            
            # Detect repeating patterns in time series
            for feature_name, time_series in time_series_features:
                repeating_patterns = self._find_repeating_subsequences(
                    time_series, config.min_pattern_length, config.max_pattern_length
                )
                
                for pattern_data in repeating_patterns:
                    pattern = DetectedPattern(
                        pattern_id=f"temporal_{feature_name}_{len(patterns)}",
                        pattern_type=PatternType.TEMPORAL,
                        modality=modality,
                        confidence_score=pattern_data['confidence'],
                        pattern_data={'feature': feature_name, 'pattern': pattern_data},
                        start_time=pattern_data.get('start_time'),
                        end_time=pattern_data.get('end_time')
                    )
                    patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Temporal pattern detection failed: {e}")
            return []
    
    def _detect_spatial_patterns(self, features: Dict[str, np.ndarray], 
                                modality: ContentModality, config: PatternConfig) -> List[DetectedPattern]:
        """Detect spatial patterns in content"""        patterns = []
        
        try:
            if modality in [ContentModality.IMAGE, ContentModality.VIDEO]:
                # Look for spatial clustering in features
                spatial_features = []
                
                if 'pixel_intensities' in features:
                    spatial_features.append(('pixels', features['pixel_intensities']))
                if 'edge_map' in features:
                    spatial_features.append(('edges', features['edge_map']))
                
                for feature_name, feature_data in spatial_features:
                    if len(feature_data) > 100:  # Enough data for clustering
                        # Reshape for clustering
                        reshaped_data = feature_data.reshape(-1, 1)
                        
                        # Apply clustering
                        clustering_model = self.clustering_models['spatial']
                        cluster_labels = clustering_model.fit_predict(reshaped_data[:1000])  # Sample for performance
                        
                        # Analyze clusters
                        unique_clusters = np.unique(cluster_labels)
                        if len(unique_clusters) > 1:
                            pattern = DetectedPattern(
                                pattern_id=f"spatial_{feature_name}_{len(patterns)}",
                                pattern_type=PatternType.SPATIAL,
                                modality=modality,
                                confidence_score=0.7,  # Default confidence
                                pattern_data={
                                    'feature': feature_name,
                                    'num_clusters': len(unique_clusters),
                                    'cluster_distribution': np.bincount(cluster_labels[cluster_labels >= 0])
                                }
                            )
                            patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Spatial pattern detection failed: {e}")
            return []
    
    def _detect_frequency_patterns(self, features: Dict[str, np.ndarray], 
                                  modality: ContentModality, config: PatternConfig) -> List[DetectedPattern]:
        """Detect frequency domain patterns"""        patterns = []
        
        try:
            frequency_features = []
            
            if modality == ContentModality.AUDIO:
                if 'magnitude_spectrum' in features:
                    frequency_features.append(('audio_spectrum', features['magnitude_spectrum']))
            
            elif modality == ContentModality.IMAGE:
                if 'frequency_magnitude' in features:
                    frequency_features.append(('image_fft', features['frequency_magnitude']))
            
            for feature_name, freq_data in frequency_features:
                # Find dominant frequencies
                if len(freq_data.shape) > 1:
                    # For 2D spectrograms, average across time
                    freq_profile = np.mean(freq_data, axis=1)
                else:
                    freq_profile = freq_data
                
                # Find peaks in frequency domain
                if len(freq_profile) > 10:
                    peaks, properties = signal.find_peaks(
                        freq_profile, 
                        height=np.max(freq_profile) * 0.1,  # 10% of max height
                        distance=len(freq_profile) // 20     # Minimum distance between peaks
                    )
                    
                    if len(peaks) > 0:
                        pattern = DetectedPattern(
                            pattern_id=f"frequency_{feature_name}_{len(patterns)}",
                            pattern_type=PatternType.FREQUENCY,
                            modality=modality,
                            confidence_score=0.8,
                            pattern_data={
                                'feature': feature_name,
                                'dominant_frequencies': peaks.tolist(),
                                'peak_magnitudes': freq_profile[peaks].tolist(),
                                'num_peaks': len(peaks)
                            }
                        )
                        patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Frequency pattern detection failed: {e}")
            return []
    
    def _detect_semantic_patterns(self, features: Dict[str, np.ndarray], 
                                 modality: ContentModality, config: PatternConfig) -> List[DetectedPattern]:
        """Detect semantic patterns in content"""        patterns = []
        
        try:
            if modality == ContentModality.TEXT:
                # Analyze text patterns
                if 'word_lengths' in features:
                    word_lengths = features['word_lengths']
                    
                    # Detect pattern in word length variation
                    if len(word_lengths) > 10:
                        # Calculate entropy of word lengths
                        length_counts = np.bincount(word_lengths)
                        length_entropy = entropy(length_counts[length_counts > 0])
                        
                        pattern = DetectedPattern(
                            pattern_id=f"semantic_word_length_{len(patterns)}",
                            pattern_type=PatternType.SEMANTIC,
                            modality=modality,
                            confidence_score=min(length_entropy / 3.0, 1.0),  # Normalize entropy
                            pattern_data={
                                'word_length_entropy': length_entropy,
                                'avg_word_length': np.mean(word_lengths),
                                'word_length_variance': np.var(word_lengths)
                            }
                        )
                        patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Semantic pattern detection failed: {e}")
            return []
    
    def _detect_behavioral_patterns(self, features: Dict[str, np.ndarray], 
                                   modality: ContentModality, config: PatternConfig) -> List[DetectedPattern]:
        """Detect behavioral patterns (user interaction patterns)"""        # This would typically require user interaction data
        # For now, return empty list
        return []
    
    def _detect_structural_patterns(self, features: Dict[str, np.ndarray], 
                                   modality: ContentModality, config: PatternConfig) -> List[DetectedPattern]:
        """Detect structural patterns in content"""        patterns = []
        
        try:
            if modality == ContentModality.TEXT:
                # Analyze sentence structure patterns
                if 'sentence_lengths' in features:
                    sentence_lengths = features['sentence_lengths']
                    
                    if len(sentence_lengths) > 3:
                        # Detect structural regularity
                        length_std = np.std(sentence_lengths)
                        length_mean = np.mean(sentence_lengths)
                        
                        # Low standard deviation indicates regular structure
                        regularity_score = 1.0 - min(length_std / length_mean, 1.0)
                        
                        pattern = DetectedPattern(
                            pattern_id=f"structural_sentence_{len(patterns)}",
                            pattern_type=PatternType.STRUCTURAL,
                            modality=modality,
                            confidence_score=regularity_score,
                            pattern_data={
                                'sentence_count': len(sentence_lengths),
                                'avg_sentence_length': length_mean,
                                'structure_regularity': regularity_score
                            }
                        )
                        patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Structural pattern detection failed: {e}")
            return []
    
    def _find_repeating_subsequences(self, sequence: np.ndarray, 
                                   min_length: int, max_length: int) -> List[Dict[str, Any]]:
        """Find repeating subsequences in a time series"""        repeating_patterns = []
        
        try:
            if len(sequence) < min_length * 2:
                return repeating_patterns
            
            # Search for patterns of different lengths
            for pattern_length in range(min_length, min(max_length, len(sequence) // 2)):
                
                # Extract all subsequences of current length
                subsequences = []
                for i in range(len(sequence) - pattern_length + 1):
                    subseq = sequence[i:i + pattern_length]
                    subsequences.append((i, subseq))
                
                # Find similar subsequences
                for i, (start_idx1, subseq1) in enumerate(subsequences):
                    matches = []
                    
                    for j, (start_idx2, subseq2) in enumerate(subsequences[i+1:], i+1):
                        # Calculate similarity
                        if len(subseq1) == len(subseq2):
                            similarity = self._calculate_sequence_similarity(subseq1, subseq2)
                            
                            if similarity > 0.8:  # High similarity threshold
                                matches.append((start_idx2, similarity))
                    
                    # If we found matches, this is a repeating pattern
                    if len(matches) >= 1:  # At least one repetition
                        pattern_info = {
                            'pattern_length': pattern_length,
                            'first_occurrence': start_idx1,
                            'repetitions': len(matches) + 1,
                            'match_positions': [start_idx1] + [pos for pos, _ in matches],
                            'confidence': np.mean([sim for _, sim in matches]),
                            'start_time': start_idx1,
                            'end_time': start_idx1 + pattern_length
                        }
                        repeating_patterns.append(pattern_info)
                        break  # Found pattern starting at this position
            
            return repeating_patterns
            
        except Exception as e:
            logger.error(f"Repeating subsequence detection failed: {e}")
            return []
    
    def _calculate_sequence_similarity(self, seq1: np.ndarray, seq2: np.ndarray) -> float:
        """Calculate similarity between two sequences"""        try:
            if len(seq1) != len(seq2):
                return 0.0
            
            # Normalize sequences
            seq1_norm = (seq1 - np.mean(seq1)) / (np.std(seq1) + 1e-8)
            seq2_norm = (seq2 - np.mean(seq2)) / (np.std(seq2) + 1e-8)
            
            # Calculate correlation coefficient
            correlation = np.corrcoef(seq1_norm, seq2_norm)[0, 1]
            
            # Return absolute correlation (ignoring phase)
            return abs(correlation) if not np.isnan(correlation) else 0.0
            
        except Exception as e:
            logger.error(f"Sequence similarity calculation failed: {e}")
            return 0.0
    
    def _detect_anomalies(self, features: Dict[str, np.ndarray], 
                         modality: ContentModality) -> List[DetectedPattern]:
        """Detect anomalous patterns in content"""        anomalies = []
        
        try:
            # Select appropriate anomaly detector
            detector_key = modality.value
            if detector_key not in self.anomaly_detectors:
                return anomalies
            
            detector = self.anomaly_detectors[detector_key]
            
            # Prepare features for anomaly detection
            feature_vectors = []
            feature_names = []
            
            for name, feature_data in features.items():
                if len(feature_data) > 0 and len(feature_data.shape) == 1:
                    # Use only 1D features for simplicity
                    feature_vectors.append(feature_data[:100])  # Limit size
                    feature_names.append(name)
            
            if not feature_vectors:
                return anomalies
            
            # Ensure all feature vectors have same length
            min_length = min(len(fv) for fv in feature_vectors)
            feature_matrix = np.array([fv[:min_length] for fv in feature_vectors]).T
            
            # Detect anomalies
            anomaly_scores = detector.fit_predict(feature_matrix)
            anomaly_indices = np.where(anomaly_scores == -1)[0]
            
            # Create anomaly patterns
            for idx in anomaly_indices:
                anomaly = DetectedPattern(
                    pattern_id=f"anomaly_{modality.value}_{len(anomalies)}",
                    pattern_type=PatternType.ANOMALY,
                    modality=modality,
                    confidence_score=0.7,  # Default confidence for anomalies
                    pattern_data={
                        'anomaly_index': int(idx),
                        'affected_features': feature_names,
                        'anomaly_scores': anomaly_scores[idx]
                    }
                )
                anomalies.append(anomaly)
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            return []
    
    def _analyze_trends(self, features: Dict[str, np.ndarray], 
                       modality: ContentModality) -> List[DetectedPattern]:
        """Analyze trending patterns in content"""        trends = []
        
        try:
            # Look for trending patterns in temporal features
            for feature_name, feature_data in features.items():
                if len(feature_data) > 10 and len(feature_data.shape) == 1:
                    # Calculate trend using linear regression
                    x = np.arange(len(feature_data))
                    coeffs = np.polyfit(x, feature_data, 1)
                    trend_slope = coeffs[0]
                    
                    # Significant trend if slope is above threshold
                    if abs(trend_slope) > 0.01:  # Adjust threshold as needed
                        trend = DetectedPattern(
                            pattern_id=f"trend_{feature_name}_{len(trends)}",
                            pattern_type=PatternType.TREND,
                            modality=modality,
                            confidence_score=min(abs(trend_slope) * 10, 1.0),
                            pattern_data={
                                'feature': feature_name,
                                'trend_slope': float(trend_slope),
                                'trend_direction': 'increasing' if trend_slope > 0 else 'decreasing',
                                'trend_strength': abs(trend_slope)
                            }
                        )
                        trends.append(trend)
            
            return trends
            
        except Exception as e:
            logger.error(f"Trend analysis failed: {e}")
            return []
    
    def _calculate_pattern_statistics(self, patterns: List[DetectedPattern]) -> Dict[str, Any]:
        """Calculate statistics for detected patterns"""        if not patterns:
            return {'total_patterns': 0}
        
        stats = {
            'total_patterns': len(patterns),
            'pattern_types': {},
            'modalities': {},
            'average_confidence': np.mean([p.confidence_score for p in patterns]),
            'confidence_distribution': {
                'high_confidence': len([p for p in patterns if p.confidence_score > 0.8]),
                'medium_confidence': len([p for p in patterns if 0.5 < p.confidence_score <= 0.8]),
                'low_confidence': len([p for p in patterns if p.confidence_score <= 0.5])
            }
        }
        
        # Count patterns by type
        for pattern in patterns:
            pattern_type = pattern.pattern_type.value
            modality = pattern.modality.value
            
            stats['pattern_types'][pattern_type] = stats['pattern_types'].get(pattern_type, 0) + 1
            stats['modalities'][modality] = stats['modalities'].get(modality, 0) + 1
        
        return stats
    
    def compare_patterns(self, content_id1: str, content_id2: str) -> Dict[str, Any]:
        """Compare patterns between two pieces of content"""        try:
            if content_id1 not in self.pattern_database or content_id2 not in self.pattern_database:
                return {'error': 'Content not found in pattern database'}
            
            patterns1 = self.pattern_database[content_id1]
            patterns2 = self.pattern_database[content_id2]
            
            # Calculate pattern similarity
            similarity_scores = []
            
            for p1 in patterns1:
                for p2 in patterns2:
                    if p1.pattern_type == p2.pattern_type and p1.modality == p2.modality:
                        # Calculate similarity between pattern data
                        similarity = self._calculate_pattern_similarity(p1, p2)
                        similarity_scores.append(similarity)
            
            comparison_result = {
                'content_1': content_id1,
                'content_2': content_id2,
                'pattern_similarities': similarity_scores,
                'average_similarity': np.mean(similarity_scores) if similarity_scores else 0.0,
                'pattern_overlap': len(similarity_scores),
                'total_patterns_1': len(patterns1),
                'total_patterns_2': len(patterns2)
            }
            
            return comparison_result
            
        except Exception as e:
            logger.error(f"Pattern comparison failed: {e}")
            return {'error': str(e)}
    
    def _calculate_pattern_similarity(self, pattern1: DetectedPattern, 
                                    pattern2: DetectedPattern) -> float:
        """Calculate similarity between two patterns"""        try:
            # Basic similarity based on confidence scores and pattern types
            type_match = 1.0 if pattern1.pattern_type == pattern2.pattern_type else 0.0
            modality_match = 1.0 if pattern1.modality == pattern2.modality else 0.0
            confidence_similarity = 1.0 - abs(pattern1.confidence_score - pattern2.confidence_score)
            
            # Weighted average
            similarity = (type_match * 0.4 + modality_match * 0.3 + confidence_similarity * 0.3)
            
            return similarity
            
        except Exception as e:
            logger.error(f"Pattern similarity calculation failed: {e}")
            return 0.0
    
    def get_pattern_summary(self, content_id: str) -> Dict[str, Any]:
        """Get summary of patterns for content"""        try:
            if content_id not in self.pattern_database:
                return {'error': 'Content not found'}
            
            patterns = self.pattern_database[content_id]
            
            summary = {
                'content_id': content_id,
                'total_patterns': len(patterns),
                'pattern_breakdown': {},
                'dominant_pattern_type': None,
                'quality_score': 0.0
            }
            
            if patterns:
                # Calculate pattern breakdown
                for pattern in patterns:
                    pattern_type = pattern.pattern_type.value
                    summary['pattern_breakdown'][pattern_type] = summary['pattern_breakdown'].get(pattern_type, 0) + 1
                
                # Find dominant pattern type
                summary['dominant_pattern_type'] = max(
                    summary['pattern_breakdown'].items(), 
                    key=lambda x: x[1]
                )[0]
                
                # Calculate quality score based on confidence
                summary['quality_score'] = np.mean([p.confidence_score for p in patterns])
            
            return summary
            
        except Exception as e:
            logger.error(f"Pattern summary generation failed: {e}")
            return {'error': str(e)}
