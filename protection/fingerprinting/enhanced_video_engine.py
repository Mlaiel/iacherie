#!/usr/bin/env python3
"""Enhanced Video Fingerprinting Engine with OpenCV + Deep Learning
Production-ready video fingerprinting for content protection

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import hashlib
import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import json
import base64

# Core video processing
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    cv2 = None

try:
    import imagehash
    from PIL import Image
    IMAGEHASH_AVAILABLE = True
except ImportError:
    IMAGEHASH_AVAILABLE = False
    imagehash = None
    Image = None

# For deep learning features (can be enhanced with actual models)
try:
    from sklearn.cluster import KMeans
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    KMeans = None
    cosine_similarity = None

logger = logging.getLogger(__name__)

@dataclass
class VideoFrame:
    """Represents a video frame with extracted features"""
    frame_number: int
    timestamp: float
    perceptual_hash: str
    histogram: np.ndarray
    optical_flow: Optional[np.ndarray]
    edge_density: float
    motion_magnitude: float
    scene_change_score: float

@dataclass
class EnhancedVideoFingerprint:
    """Enhanced video fingerprint with deep learning features"""
    file_id: str
    duration: float
    frame_count: int
    fps: float
    resolution: Tuple[int, int]
    
    # Perceptual hashing
    frame_hashes: List[str]
    temporal_hash: str
    
    # Motion analysis
    optical_flow_features: Dict[str, Any]
    motion_vectors: List[float]
    scene_changes: List[float]
    
    # Visual features
    color_histograms: List[np.ndarray]
    edge_features: Dict[str, Any]
    texture_features: Dict[str, Any]
    
    # Deep learning features (placeholder for future ML models)
    content_features: Optional[np.ndarray]
    object_detections: List[Dict[str, Any]]
    
    # Quality metrics
    confidence_score: float
    quality_score: float
    
    created_at: datetime

class EnhancedVideoFingerprintEngine:
    """Production-ready video fingerprinting engine with OpenCV + Deep Learning"""
    
    def __init__(self,
                 frame_sample_rate: int = 30,
                 max_frames: int = 100,
                 hash_size: int = 8,
                 enable_motion_analysis: bool = True,
                 enable_scene_detection: bool = True):
        """
        Initialize enhanced video fingerprinting engine
        
        Args:
            frame_sample_rate: Sample every N-th frame
            max_frames: Maximum frames to process
            hash_size: Size for perceptual hashing
            enable_motion_analysis: Enable optical flow analysis
            enable_scene_detection: Enable scene change detection
        """
        if not OPENCV_AVAILABLE:
            raise RuntimeError("OpenCV is required for video fingerprinting")
        
        self.frame_sample_rate = frame_sample_rate
        self.max_frames = max_frames
        self.hash_size = hash_size
        self.enable_motion_analysis = enable_motion_analysis
        self.enable_scene_detection = enable_scene_detection
        
        # Initialize OpenCV components
        self.optical_flow = cv2.FarnebackOpticalFlow_create()
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
        
        # Feature detection
        self.orb = cv2.ORB_create(nfeatures=500)
        self.sift = None
        try:
            self.sift = cv2.SIFT_create()
        except:
            logger.warning("SIFT not available, using ORB only")
        
        self.similarity_threshold = 0.85
        
        logger.info(f"Enhanced Video Fingerprinting Engine initialized")
        logger.info(f"OpenCV available: {OPENCV_AVAILABLE}")
        logger.info(f"ImageHash available: {IMAGEHASH_AVAILABLE}")
        logger.info(f"scikit-learn available: {SKLEARN_AVAILABLE}")
    
    async def extract_fingerprint(self, video_path: Union[str, Path]) -> EnhancedVideoFingerprint:
        """
        Extract comprehensive video fingerprint
        
        Args:
            video_path: Path to video file
            
        Returns:
            Enhanced video fingerprint
        """
        cap = cv2.VideoCapture(str(video_path))
        
        if not cap.isOpened():
            raise RuntimeError(f"Could not open video file: {video_path}")
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = frame_count / fps if fps > 0 else 0
        
        # Generate file ID
        file_id = self._generate_file_id(video_path)
        
        # Process frames
        frames_data = await self._process_video_frames(cap)
        
        # Extract features
        features = await self._extract_video_features(frames_data)
        
        cap.release()
        
        return EnhancedVideoFingerprint(
            file_id=file_id,
            duration=duration,
            frame_count=len(frames_data),
            fps=fps,
            resolution=(width, height),
            frame_hashes=features['frame_hashes'],
            temporal_hash=features['temporal_hash'],
            optical_flow_features=features['optical_flow'],
            motion_vectors=features['motion_vectors'],
            scene_changes=features['scene_changes'],
            color_histograms=features['color_histograms'],
            edge_features=features['edge_features'],
            texture_features=features['texture_features'],
            content_features=features.get('content_features'),
            object_detections=features.get('object_detections', []),
            confidence_score=features['confidence_score'],
            quality_score=features['quality_score'],
            created_at=datetime.utcnow()
        )
    
    async def _process_video_frames(self, cap: cv2.VideoCapture) -> List[VideoFrame]:
        """Process video frames and extract frame-level features"""
        frames_data = []
        frame_number = 0
        prev_frame = None
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Sample frames
            if frame_number % self.frame_sample_rate != 0:
                frame_number += 1
                continue
            
            if len(frames_data) >= self.max_frames:
                break
            
            # Convert to grayscale for analysis
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Calculate timestamp
            fps = cap.get(cv2.CAP_PROP_FPS)
            timestamp = frame_number / fps if fps > 0 else 0
            
            # Extract frame features
            frame_data = await self._extract_frame_features(
                frame, gray_frame, prev_frame, frame_number, timestamp
            )
            
            frames_data.append(frame_data)
            prev_frame = gray_frame
            frame_number += 1
        
        return frames_data
    
    async def _extract_frame_features(self,
                                    color_frame: np.ndarray,
                                    gray_frame: np.ndarray,
                                    prev_frame: Optional[np.ndarray],
                                    frame_number: int,
                                    timestamp: float) -> VideoFrame:
        """Extract features from a single frame"""
        
        # Perceptual hash
        perceptual_hash = self._compute_perceptual_hash(gray_frame)
        
        # Color histogram
        histogram = self._compute_color_histogram(color_frame)
        
        # Optical flow
        optical_flow = None
        motion_magnitude = 0.0
        if prev_frame is not None and self.enable_motion_analysis:
            optical_flow = self._compute_optical_flow(prev_frame, gray_frame)
            motion_magnitude = np.mean(np.sqrt(optical_flow[..., 0]**2 + optical_flow[..., 1]**2))
        
        # Edge density
        edge_density = self._compute_edge_density(gray_frame)
        
        # Scene change score
        scene_change_score = 0.0
        if prev_frame is not None and self.enable_scene_detection:
            scene_change_score = self._compute_scene_change_score(prev_frame, gray_frame)
        
        return VideoFrame(
            frame_number=frame_number,
            timestamp=timestamp,
            perceptual_hash=perceptual_hash,
            histogram=histogram,
            optical_flow=optical_flow,
            edge_density=edge_density,
            motion_magnitude=motion_magnitude,
            scene_change_score=scene_change_score
        )
    
    async def _extract_video_features(self, frames_data: List[VideoFrame]) -> Dict[str, Any]:
        """Extract video-level features from frame data"""
        features = {}
        
        # Frame hashes
        features['frame_hashes'] = [frame.perceptual_hash for frame in frames_data]
        
        # Temporal hash (hash of all frame hashes combined)
        combined_hashes = ''.join(features['frame_hashes'])
        features['temporal_hash'] = hashlib.md5(combined_hashes.encode()).hexdigest()
        
        # Motion analysis
        motion_vectors = [frame.motion_magnitude for frame in frames_data]
        features['motion_vectors'] = motion_vectors
        
        # Optical flow features
        if any(frame.optical_flow is not None for frame in frames_data):
            flow_features = self._analyze_optical_flow([f.optical_flow for f in frames_data 
                                                       if f.optical_flow is not None])
            features['optical_flow'] = flow_features
        else:
            features['optical_flow'] = {'mean_magnitude': 0.0, 'dominant_direction': 0.0}
        
        # Scene changes
        scene_changes = [frame.scene_change_score for frame in frames_data]
        features['scene_changes'] = scene_changes
        
        # Color histograms
        features['color_histograms'] = [frame.histogram for frame in frames_data]
        
        # Edge features
        edge_densities = [frame.edge_density for frame in frames_data]
        features['edge_features'] = {
            'mean_edge_density': float(np.mean(edge_densities)),
            'std_edge_density': float(np.std(edge_densities)),
            'edge_variation': float(np.ptp(edge_densities))  # peak-to-peak
        }
        
        # Texture features (simplified)
        features['texture_features'] = {
            'motion_variation': float(np.std(motion_vectors)),
            'scene_complexity': float(np.mean(scene_changes))
        }
        
        # Quality and confidence scores
        features['quality_score'] = self._calculate_quality_score(frames_data)
        features['confidence_score'] = self._calculate_confidence_score(features)
        
        return features
    
    def _compute_perceptual_hash(self, frame: np.ndarray) -> str:
        """Compute perceptual hash for a frame"""
        if IMAGEHASH_AVAILABLE:
            # Convert to PIL Image
            pil_image = Image.fromarray(frame)
            # Use difference hash for better temporal comparison
            dhash = imagehash.dhash(pil_image, hash_size=self.hash_size)
            return str(dhash)
        else:
            # Fallback: simple DCT-based hash
            resized = cv2.resize(frame, (32, 32))
            dct = cv2.dct(np.float32(resized))
            # Use top-left 8x8 coefficients
            dct_low = dct[:8, :8]
            median = np.median(dct_low)
            hash_bits = dct_low > median
            return ''.join(['1' if bit else '0' for bit in hash_bits.flatten()])
    
    def _compute_color_histogram(self, frame: np.ndarray) -> np.ndarray:
        """Compute color histogram for a frame"""
        # Convert BGR to HSV for better color representation
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Calculate histograms for H, S, V channels
        hist_h = cv2.calcHist([hsv], [0], None, [50], [0, 180])
        hist_s = cv2.calcHist([hsv], [1], None, [60], [0, 256])
        hist_v = cv2.calcHist([hsv], [2], None, [60], [0, 256])
        
        # Concatenate and normalize
        histogram = np.concatenate([hist_h.flatten(), hist_s.flatten(), hist_v.flatten()])
        histogram = histogram / (np.sum(histogram) + 1e-10)
        
        return histogram
    
    def _compute_optical_flow(self, prev_frame: np.ndarray, curr_frame: np.ndarray) -> np.ndarray:
        """Compute optical flow between frames"""
        flow = cv2.calcOpticalFlowPyrLK(
            prev_frame, curr_frame, None, None,
            winSize=(15, 15),
            maxLevel=2,
            criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03)
        )
        
        # If Lucas-Kanade fails, use Farneback
        if flow[0] is None:
            flow = cv2.calcOpticalFlowFarneback(
                prev_frame, curr_frame, None, 
                0.5, 3, 15, 3, 5, 1.2, 0
            )
        else:
            flow = flow[0]
        
        return flow
    
    def _compute_edge_density(self, frame: np.ndarray) -> float:
        """Compute edge density using Canny edge detection"""
        edges = cv2.Canny(frame, 50, 150)
        edge_pixels = np.sum(edges > 0)
        total_pixels = frame.shape[0] * frame.shape[1]
        return float(edge_pixels / total_pixels)
    
    def _compute_scene_change_score(self, prev_frame: np.ndarray, curr_frame: np.ndarray) -> float:
        """Compute scene change score between frames"""
        # Histogram comparison
        hist1 = cv2.calcHist([prev_frame], [0], None, [256], [0, 256])
        hist2 = cv2.calcHist([curr_frame], [0], None, [256], [0, 256])
        
        # Chi-square distance
        chi_square = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CHISQR)
        
        # Normalize (higher score = more scene change)
        return float(min(chi_square / 1000000, 1.0))
    
    def _analyze_optical_flow(self, flow_data: List[np.ndarray]) -> Dict[str, Any]:
        """Analyze optical flow patterns across frames"""
        if not flow_data:
            return {'mean_magnitude': 0.0, 'dominant_direction': 0.0}
        
        magnitudes = []
        directions = []
        
        for flow in flow_data:
            if flow is not None:
                if len(flow.shape) == 3:  # Farneback flow
                    mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
                    magnitudes.append(np.mean(mag))
                    directions.append(np.mean(ang))
                else:  # Lucas-Kanade points
                    if flow.shape[0] > 0:
                        mag = np.sqrt(flow[:, 0]**2 + flow[:, 1]**2)
                        ang = np.arctan2(flow[:, 1], flow[:, 0])
                        magnitudes.append(np.mean(mag))
                        directions.append(np.mean(ang))
        
        return {
            'mean_magnitude': float(np.mean(magnitudes)) if magnitudes else 0.0,
            'dominant_direction': float(np.mean(directions)) if directions else 0.0,
            'magnitude_variation': float(np.std(magnitudes)) if magnitudes else 0.0
        }
    
    def _calculate_quality_score(self, frames_data: List[VideoFrame]) -> float:
        """Calculate video quality score"""
        if not frames_data:
            return 0.0
        
        # Factors that indicate good quality
        edge_densities = [frame.edge_density for frame in frames_data]
        motion_mags = [frame.motion_magnitude for frame in frames_data]
        
        # Good quality indicators:
        # - Reasonable edge density (not too low, not too high)
        # - Smooth motion (not too jerky)
        avg_edge_density = np.mean(edge_densities)
        edge_score = 1.0 - abs(avg_edge_density - 0.1) / 0.1  # Optimal around 0.1
        edge_score = max(0.0, min(1.0, edge_score))
        
        motion_consistency = 1.0 - np.std(motion_mags) / (np.mean(motion_mags) + 1e-10)
        motion_consistency = max(0.0, min(1.0, motion_consistency))
        
        return float((edge_score + motion_consistency) / 2.0)
    
    def _calculate_confidence_score(self, features: Dict[str, Any]) -> float:
        """Calculate confidence score for the fingerprint"""
        confidence_factors = []
        
        # Frame count factor
        frame_count = len(features.get('frame_hashes', []))
        frame_factor = min(frame_count / 10.0, 1.0)  # Good if >= 10 frames
        confidence_factors.append(frame_factor)
        
        # Motion analysis factor
        motion_vectors = features.get('motion_vectors', [])
        if motion_vectors:
            motion_variation = np.std(motion_vectors)
            motion_factor = min(motion_variation / 10.0, 1.0)  # Some motion is good
            confidence_factors.append(motion_factor)
        
        # Edge feature factor
        edge_features = features.get('edge_features', {})
        if edge_features:
            edge_variation = edge_features.get('edge_variation', 0)
            edge_factor = min(edge_variation * 10, 1.0)  # Some edge variation is good
            confidence_factors.append(edge_factor)
        
        return float(np.mean(confidence_factors))
    
    def _generate_file_id(self, video_path: Union[str, Path]) -> str:
        """Generate unique file ID"""
        path_str = str(video_path)
        path_hash = hashlib.md5(path_str.encode()).hexdigest()[:16]
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f"video_{path_hash}_{timestamp}"
    
    async def compare_fingerprints(self,
                                 fp1: EnhancedVideoFingerprint,
                                 fp2: EnhancedVideoFingerprint) -> float:
        """
        Compare two video fingerprints
        
        Returns:
            Similarity score between 0 and 1
        """
        similarities = []
        
        # Compare temporal hashes
        temporal_sim = 1.0 if fp1.temporal_hash == fp2.temporal_hash else 0.0
        similarities.append(temporal_sim)
        
        # Compare frame hashes
        frame_sim = self._compare_frame_hashes(fp1.frame_hashes, fp2.frame_hashes)
        similarities.append(frame_sim)
        
        # Compare motion patterns
        motion_sim = self._compare_motion_patterns(fp1.motion_vectors, fp2.motion_vectors)
        similarities.append(motion_sim)
        
        # Compare color histograms
        color_sim = self._compare_color_histograms(fp1.color_histograms, fp2.color_histograms)
        similarities.append(color_sim)
        
        # Compare optical flow features
        flow_sim = self._compare_optical_flow(fp1.optical_flow_features, fp2.optical_flow_features)
        similarities.append(flow_sim)
        
        # Weighted average
        weights = [0.3, 0.3, 0.2, 0.1, 0.1]
        return float(np.average(similarities, weights=weights))
    
    def _compare_frame_hashes(self, hashes1: List[str], hashes2: List[str]) -> float:
        """Compare sequences of frame hashes"""
        if not hashes1 or not hashes2:
            return 0.0
        
        # Use dynamic time warping for sequence comparison
        min_len = min(len(hashes1), len(hashes2))
        max_len = max(len(hashes1), len(hashes2))
        
        # Simple alignment for now
        matches = 0
        for i in range(min_len):
            if hashes1[i] == hashes2[i]:
                matches += 1
            else:
                # Check Hamming distance for perceptual hashes
                if len(hashes1[i]) == len(hashes2[i]):
                    hamming_dist = sum(c1 != c2 for c1, c2 in zip(hashes1[i], hashes2[i]))
                    similarity = 1.0 - (hamming_dist / len(hashes1[i]))
                    if similarity > 0.8:  # Threshold for considering as match
                        matches += similarity
        
        return matches / max_len
    
    def _compare_motion_patterns(self, motion1: List[float], motion2: List[float]) -> float:
        """Compare motion vector patterns"""
        if not motion1 or not motion2:
            return 0.0
        
        # Normalize and compare using correlation
        motion1_norm = np.array(motion1) / (np.max(motion1) + 1e-10)
        motion2_norm = np.array(motion2) / (np.max(motion2) + 1e-10)
        
        min_len = min(len(motion1_norm), len(motion2_norm))
        if min_len == 0:
            return 0.0
        
        corr = np.corrcoef(motion1_norm[:min_len], motion2_norm[:min_len])[0, 1]
        return float(max(0.0, corr))
    
    def _compare_color_histograms(self, hists1: List[np.ndarray], hists2: List[np.ndarray]) -> float:
        """Compare color histogram sequences"""
        if not hists1 or not hists2:
            return 0.0
        
        similarities = []
        min_len = min(len(hists1), len(hists2))
        
        for i in range(min_len):
            # Chi-square distance
            chi_sq = cv2.compareHist(hists1[i], hists2[i], cv2.HISTCMP_CHISQR)
            similarity = 1.0 / (1.0 + chi_sq)  # Convert distance to similarity
            similarities.append(similarity)
        
        return float(np.mean(similarities))
    
    def _compare_optical_flow(self, flow1: Dict[str, Any], flow2: Dict[str, Any]) -> float:
        """Compare optical flow features"""
        if not flow1 or not flow2:
            return 0.0
        
        similarities = []
        
        # Compare mean magnitude
        mag1 = flow1.get('mean_magnitude', 0)
        mag2 = flow2.get('mean_magnitude', 0)
        max_mag = max(mag1, mag2, 1e-10)
        mag_sim = 1.0 - abs(mag1 - mag2) / max_mag
        similarities.append(mag_sim)
        
        # Compare dominant direction
        dir1 = flow1.get('dominant_direction', 0)
        dir2 = flow2.get('dominant_direction', 0)
        dir_diff = abs(dir1 - dir2)
        # Handle circular nature of angles
        dir_diff = min(dir_diff, 2 * np.pi - dir_diff)
        dir_sim = 1.0 - dir_diff / np.pi
        similarities.append(dir_sim)
        
        return float(np.mean(similarities))
    
    def export_fingerprint(self, fingerprint: EnhancedVideoFingerprint) -> Dict[str, Any]:
        """Export fingerprint to serializable format"""
        return {
            'file_id': fingerprint.file_id,
            'duration': fingerprint.duration,
            'frame_count': fingerprint.frame_count,
            'fps': fingerprint.fps,
            'resolution': fingerprint.resolution,
            'frame_hashes': fingerprint.frame_hashes,
            'temporal_hash': fingerprint.temporal_hash,
            'optical_flow_features': fingerprint.optical_flow_features,
            'motion_vectors': fingerprint.motion_vectors,
            'scene_changes': fingerprint.scene_changes,
            'edge_features': fingerprint.edge_features,
            'texture_features': fingerprint.texture_features,
            'confidence_score': fingerprint.confidence_score,
            'quality_score': fingerprint.quality_score,
            'created_at': fingerprint.created_at.isoformat()
        }
    
    def get_engine_info(self) -> Dict[str, Any]:
        """Get engine information and capabilities"""
        return {
            'engine': 'EnhancedVideoFingerprintEngine',
            'version': '1.0.0',
            'capabilities': {
                'opencv': OPENCV_AVAILABLE,
                'imagehash': IMAGEHASH_AVAILABLE,
                'scikit_learn': SKLEARN_AVAILABLE,
                'optical_flow': True,
                'scene_detection': True,
                'perceptual_hashing': True,
                'motion_analysis': True
            },
            'config': {
                'frame_sample_rate': self.frame_sample_rate,
                'max_frames': self.max_frames,
                'hash_size': self.hash_size,
                'enable_motion_analysis': self.enable_motion_analysis,
                'enable_scene_detection': self.enable_scene_detection
            },
            'supported_formats': ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
        }