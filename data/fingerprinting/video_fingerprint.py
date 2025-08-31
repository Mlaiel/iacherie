"""Video Fingerprinter Implementation
==================================

Professional video fingerprinting system for content protection and similarity detection.
Implements advanced computer vision and perceptual hashing algorithms.

Team Expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel (mlaiel@live.de)
Email: mlaiel@live.de
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

⚠️  CRITICAL WARNING ⚠️
This code is PROPRIETARY and CONFIDENTIAL intellectual property.
Any unauthorized use, reproduction, distribution, or reverse engineering 
is STRICTLY PROHIBITED and will result in immediate legal action.

Unauthorized copying or theft of this concept, code, or methodology 
will be prosecuted to the FULL EXTENT OF THE LAW under German and 
International Copyright Laws.

For licensing inquiries, contact: mlaiel@live.de
"""import asyncio
import cv2
import numpy as np
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import io
import tempfile
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

try:
    import imagehash
    from PIL import Image
    IMAGEHASH_AVAILABLE = True
except ImportError:
    IMAGEHASH_AVAILABLE = False
    logging.warning("imagehash not available, using alternative methods")

try:
    import torch
    import torchvision.transforms as transforms
    from torchvision.models import mobilenet_v3_large
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logging.warning("PyTorch not available, using OpenCV only")


class VideoFingerprintType(Enum):
    """Types of video fingerprints"""    FRAME_HASH = "frame_hash"
    PERCEPTUAL_HASH = "perceptual_hash"
    FEATURE_DESCRIPTOR = "feature_descriptor"
    MOTION_VECTOR = "motion_vector"
    COLOR_HISTOGRAM = "color_histogram"
    EDGE_DENSITY = "edge_density"
    TEMPORAL_SIGNATURE = "temporal_signature"


class FrameSamplingMethod(Enum):
    """Methods for sampling frames from video"""    UNIFORM = "uniform"
    KEYFRAME = "keyframe"
    ADAPTIVE = "adaptive"
    MOTION_BASED = "motion_based"


@dataclass
class VideoFingerprint:
    """Video fingerprint data structure"""    video_id: str
    fingerprint_type: VideoFingerprintType
    fingerprint_data: Union[str, List[str], np.ndarray]
    frame_count: int
    duration_seconds: float
    resolution: Tuple[int, int]
    fps: float
    sampling_method: FrameSamplingMethod
    sampled_frame_count: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class VideoMatchResult:
    """Video similarity match result"""    query_video_id: str
    matched_video_id: str
    similarity_score: float
    fingerprint_type: VideoFingerprintType
    matched_frames: List[Tuple[int, int]]  # (query_frame, matched_frame)
    temporal_alignment: Dict[str, Any]
    confidence_metrics: Dict[str, float]
    match_regions: List[Dict[str, Any]]
    created_at: datetime = field(default_factory=datetime.utcnow)


class VideoFingerprinter:
    """    Professional video fingerprinting system for content protection.
    
    Features:
    - Multiple fingerprinting algorithms
    - Perceptual hashing for robustness
    - Keyframe detection and sampling
    - Motion vector analysis
    - Color histogram comparison
    - Edge density analysis
    - Temporal signature generation
    - GPU acceleration support
    - Batch processing capabilities
    """    
    def __init__(self, 
                 max_workers: int = 4,
                 gpu_acceleration: bool = True,
                 cache_frames: bool = True):
        """        Initialize video fingerprinter.
        
        Args:
            max_workers: Maximum worker threads
            gpu_acceleration: Enable GPU acceleration if available
            cache_frames: Cache extracted frames for performance
        """        self.max_workers = max_workers
        self.gpu_acceleration = gpu_acceleration and TORCH_AVAILABLE
        self.cache_frames = cache_frames
        self.logger = logging.getLogger(__name__)
        
        # Thread pool for parallel processing
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        
        # Frame cache
        self.frame_cache: Dict[str, List[np.ndarray]] = {}
        self.cache_max_size = 100  # Maximum videos to cache
        
        # Performance metrics
        self.processing_count = 0
        self.total_processing_time = 0.0
        
        # Initialize AI models if available
        self.feature_extractor = None
        if self.gpu_acceleration:
            self._initialize_ai_models()
    
    def _initialize_ai_models(self):
        """Initialize AI models for feature extraction"""        try:
            if TORCH_AVAILABLE:
                # Load pre-trained MobileNet for feature extraction
                self.feature_extractor = mobilenet_v3_large(pretrained=True)
                self.feature_extractor.classifier = torch.nn.Identity()  # Remove classifier
                self.feature_extractor.eval()
                
                # Move to GPU if available
                if torch.cuda.is_available():
                    self.feature_extractor = self.feature_extractor.cuda()
                
                # Define image transforms
                self.transform = transforms.Compose([
                    transforms.ToPILImage(),
                    transforms.Resize((224, 224)),
                    transforms.ToTensor(),
                    transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                                       std=[0.229, 0.224, 0.225])
                ])
                
                self.logger.info("Initialized AI models for video fingerprinting")
                
        except Exception as e:
            self.logger.warning(f"Failed to initialize AI models: {str(e)}")
            self.feature_extractor = None
    
    async def extract_fingerprint(self, 
                                video_path: str,
                                video_id: str,
                                fingerprint_types: List[VideoFingerprintType] = None,
                                sampling_method: FrameSamplingMethod = FrameSamplingMethod.ADAPTIVE,
                                max_frames: int = 100) -> List[VideoFingerprint]:
        """        Extract video fingerprints using multiple algorithms.
        
        Args:
            video_path: Path to video file
            video_id: Unique identifier for video
            fingerprint_types: Types of fingerprints to extract
            sampling_method: Method for sampling frames
            max_frames: Maximum number of frames to process
            
        Returns:
            List of video fingerprints
        """        try:
            start_time = datetime.utcnow()
            
            if fingerprint_types is None:
                fingerprint_types = [
                    VideoFingerprintType.PERCEPTUAL_HASH,
                    VideoFingerprintType.COLOR_HISTOGRAM,
                    VideoFingerprintType.EDGE_DENSITY
                ]
            
            # Extract video metadata
            video_info = await self._extract_video_info(video_path)
            
            # Sample frames
            frames, frame_indices = await self._sample_frames(
                video_path, sampling_method, max_frames
            )
            
            # Store frames in cache
            if self.cache_frames:
                self._cache_frames(video_id, frames)
            
            # Extract fingerprints
            fingerprints = []
            for fingerprint_type in fingerprint_types:
                try:
                    fingerprint = await self._extract_single_fingerprint(
                        video_id, frames, frame_indices, fingerprint_type, 
                        video_info, sampling_method
                    )
                    fingerprints.append(fingerprint)
                except Exception as e:
                    self.logger.error(f"Error extracting {fingerprint_type.value}: {str(e)}")
                    continue
            
            # Update metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.processing_count += 1
            self.total_processing_time += processing_time
            
            self.logger.info(f"Extracted {len(fingerprints)} fingerprints for {video_id} in {processing_time:.2f}s")
            return fingerprints
            
        except Exception as e:
            self.logger.error(f"Error extracting video fingerprint for {video_id}: {str(e)}")
            return []
    
    async def compare_fingerprints(self, 
                                 fingerprint1: VideoFingerprint,
                                 fingerprint2: VideoFingerprint) -> VideoMatchResult:
        """        Compare two video fingerprints for similarity.
        
        Args:
            fingerprint1: First video fingerprint
            fingerprint2: Second video fingerprint
            
        Returns:
            Video match result with similarity metrics
        """        try:
            if fingerprint1.fingerprint_type != fingerprint2.fingerprint_type:
                raise ValueError("Cannot compare different fingerprint types")
            
            fingerprint_type = fingerprint1.fingerprint_type
            
            if fingerprint_type == VideoFingerprintType.PERCEPTUAL_HASH:
                similarity_score, matched_frames = await self._compare_perceptual_hashes(
                    fingerprint1, fingerprint2
                )
            elif fingerprint_type == VideoFingerprintType.COLOR_HISTOGRAM:
                similarity_score, matched_frames = await self._compare_color_histograms(
                    fingerprint1, fingerprint2
                )
            elif fingerprint_type == VideoFingerprintType.EDGE_DENSITY:
                similarity_score, matched_frames = await self._compare_edge_densities(
                    fingerprint1, fingerprint2
                )
            elif fingerprint_type == VideoFingerprintType.FEATURE_DESCRIPTOR:
                similarity_score, matched_frames = await self._compare_feature_descriptors(
                    fingerprint1, fingerprint2
                )
            else:
                raise ValueError(f"Unsupported fingerprint type: {fingerprint_type}")
            
            # Calculate temporal alignment
            temporal_alignment = self._calculate_temporal_alignment(
                matched_frames, fingerprint1.duration_seconds, fingerprint2.duration_seconds
            )
            
            # Generate confidence metrics
            confidence_metrics = self._calculate_confidence_metrics(
                similarity_score, matched_frames, fingerprint1, fingerprint2
            )
            
            # Identify match regions
            match_regions = self._identify_match_regions(matched_frames, similarity_score)
            
            result = VideoMatchResult(
                query_video_id=fingerprint1.video_id,
                matched_video_id=fingerprint2.video_id,
                similarity_score=similarity_score,
                fingerprint_type=fingerprint_type,
                matched_frames=matched_frames,
                temporal_alignment=temporal_alignment,
                confidence_metrics=confidence_metrics,
                match_regions=match_regions
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error comparing fingerprints: {str(e)}")
            # Return empty result
            return VideoMatchResult(
                query_video_id=fingerprint1.video_id,
                matched_video_id=fingerprint2.video_id,
                similarity_score=0.0,
                fingerprint_type=fingerprint1.fingerprint_type,
                matched_frames=[],
                temporal_alignment={},
                confidence_metrics={},
                match_regions=[]
            )
    
    async def find_similar_videos(self, 
                                query_fingerprint: VideoFingerprint,
                                candidate_fingerprints: List[VideoFingerprint],
                                similarity_threshold: float = 0.8) -> List[VideoMatchResult]:
        """        Find similar videos from a list of candidates.
        
        Args:
            query_fingerprint: Query video fingerprint
            candidate_fingerprints: List of candidate fingerprints
            similarity_threshold: Minimum similarity threshold
            
        Returns:
            List of matching video results sorted by similarity
        """        try:
            # Filter candidates by fingerprint type
            compatible_candidates = [
                fp for fp in candidate_fingerprints 
                if fp.fingerprint_type == query_fingerprint.fingerprint_type
            ]
            
            # Compare with each candidate
            comparison_tasks = []
            for candidate in compatible_candidates:
                task = asyncio.create_task(
                    self.compare_fingerprints(query_fingerprint, candidate)
                )
                comparison_tasks.append(task)
            
            # Wait for all comparisons
            results = await asyncio.gather(*comparison_tasks)
            
            # Filter by threshold and sort by similarity
            filtered_results = [
                result for result in results 
                if result.similarity_score >= similarity_threshold
            ]
            
            filtered_results.sort(key=lambda x: x.similarity_score, reverse=True)
            
            self.logger.info(f"Found {len(filtered_results)} similar videos above threshold {similarity_threshold}")
            return filtered_results
            
        except Exception as e:
            self.logger.error(f"Error finding similar videos: {str(e)}")
            return []
    
    # Private helper methods
    
    async def _extract_video_info(self, video_path: str) -> Dict[str, Any]:
        """Extract basic video information"""        try:
            cap = cv2.VideoCapture(video_path)
            
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            cap.release()
            
            return {
                'frame_count': frame_count,
                'fps': fps,
                'resolution': (width, height),
                'duration_seconds': duration
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting video info: {str(e)}")
            return {
                'frame_count': 0,
                'fps': 0,
                'resolution': (0, 0),
                'duration_seconds': 0
            }
    
    async def _sample_frames(self, 
                           video_path: str, 
                           sampling_method: FrameSamplingMethod,
                           max_frames: int) -> Tuple[List[np.ndarray], List[int]]:
        """Sample frames from video based on specified method"""        try:
            cap = cv2.VideoCapture(video_path)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            if sampling_method == FrameSamplingMethod.UNIFORM:
                frame_indices = self._get_uniform_frame_indices(frame_count, max_frames)
            elif sampling_method == FrameSamplingMethod.KEYFRAME:
                frame_indices = await self._detect_keyframes(cap, max_frames)
            elif sampling_method == FrameSamplingMethod.ADAPTIVE:
                frame_indices = await self._adaptive_frame_sampling(cap, max_frames)
            elif sampling_method == FrameSamplingMethod.MOTION_BASED:
                frame_indices = await self._motion_based_sampling(cap, max_frames)
            else:
                frame_indices = self._get_uniform_frame_indices(frame_count, max_frames)
            
            # Extract frames at specified indices
            frames = []
            for frame_idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                if ret:
                    frames.append(frame)
                else:
                    self.logger.warning(f"Failed to read frame {frame_idx}")
            
            cap.release()
            
            return frames, frame_indices
            
        except Exception as e:
            self.logger.error(f"Error sampling frames: {str(e)}")
            return [], []
    
    def _get_uniform_frame_indices(self, frame_count: int, max_frames: int) -> List[int]:
        """Get uniformly distributed frame indices"""        if frame_count <= max_frames:
            return list(range(frame_count))
        
        step = frame_count // max_frames
        return [i * step for i in range(max_frames)]
    
    async def _detect_keyframes(self, cap: cv2.VideoCapture, max_frames: int) -> List[int]:
        """Detect keyframes using scene change detection"""        try:
            frame_indices = []
            prev_frame = None
            frame_idx = 0
            threshold = 30.0  # Scene change threshold
            
            while len(frame_indices) < max_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if prev_frame is not None:
                    # Calculate frame difference
                    gray_current = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    gray_prev = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
                    
                    diff = cv2.absdiff(gray_current, gray_prev)
                    mean_diff = np.mean(diff)
                    
                    # If significant change, consider it a keyframe
                    if mean_diff > threshold:
                        frame_indices.append(frame_idx)
                else:
                    # First frame is always a keyframe
                    frame_indices.append(frame_idx)
                
                prev_frame = frame
                frame_idx += 1
            
            return frame_indices
            
        except Exception as e:
            self.logger.error(f"Error detecting keyframes: {str(e)}")
            return self._get_uniform_frame_indices(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), max_frames)
    
    async def _adaptive_frame_sampling(self, cap: cv2.VideoCapture, max_frames: int) -> List[int]:
        """Adaptive frame sampling based on content complexity"""        try:
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            frame_indices = []
            
            # Sample frames and calculate complexity scores
            sample_count = min(frame_count, max_frames * 2)
            sample_indices = self._get_uniform_frame_indices(frame_count, sample_count)
            
            complexity_scores = []
            for idx in sample_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                if ret:
                    # Calculate complexity using edge density
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    edges = cv2.Canny(gray, 50, 150)
                    complexity = np.sum(edges) / (frame.shape[0] * frame.shape[1])
                    complexity_scores.append((idx, complexity))
            
            # Sort by complexity and select top frames
            complexity_scores.sort(key=lambda x: x[1], reverse=True)
            frame_indices = [idx for idx, _ in complexity_scores[:max_frames]]
            frame_indices.sort()  # Maintain temporal order
            
            return frame_indices
            
        except Exception as e:
            self.logger.error(f"Error in adaptive sampling: {str(e)}")
            return self._get_uniform_frame_indices(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), max_frames)
    
    async def _motion_based_sampling(self, cap: cv2.VideoCapture, max_frames: int) -> List[int]:
        """Motion-based frame sampling"""        try:
            frame_indices = []
            prev_frame = None
            frame_idx = 0
            motion_threshold = 1000  # Motion magnitude threshold
            
            while len(frame_indices) < max_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if prev_frame is not None:
                    # Calculate optical flow
                    gray_current = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    gray_prev = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
                    
                    # Use Lucas-Kanade optical flow
                    corners = cv2.goodFeaturesToTrack(gray_prev, maxCorners=100, 
                                                    qualityLevel=0.01, minDistance=10)
                    
                    if corners is not None:
                        flow, status, _ = cv2.calcOpticalFlowPyrLK(
                            gray_prev, gray_current, corners, None
                        )
                        
                        # Calculate motion magnitude
                        motion_magnitude = np.sum(np.linalg.norm(flow - corners, axis=2))
                        
                        if motion_magnitude > motion_threshold:
                            frame_indices.append(frame_idx)
                else:
                    # First frame
                    frame_indices.append(frame_idx)
                
                prev_frame = frame
                frame_idx += 1
            
            return frame_indices
            
        except Exception as e:
            self.logger.error(f"Error in motion-based sampling: {str(e)}")
            return self._get_uniform_frame_indices(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), max_frames)
    
    async def _extract_single_fingerprint(self, 
                                        video_id: str,
                                        frames: List[np.ndarray],
                                        frame_indices: List[int],
                                        fingerprint_type: VideoFingerprintType,
                                        video_info: Dict[str, Any],
                                        sampling_method: FrameSamplingMethod) -> VideoFingerprint:
        """Extract single type of fingerprint"""        try:
            if fingerprint_type == VideoFingerprintType.PERCEPTUAL_HASH:
                fingerprint_data = await self._extract_perceptual_hashes(frames)
            elif fingerprint_type == VideoFingerprintType.COLOR_HISTOGRAM:
                fingerprint_data = await self._extract_color_histograms(frames)
            elif fingerprint_type == VideoFingerprintType.EDGE_DENSITY:
                fingerprint_data = await self._extract_edge_densities(frames)
            elif fingerprint_type == VideoFingerprintType.FEATURE_DESCRIPTOR:
                fingerprint_data = await self._extract_feature_descriptors(frames)
            elif fingerprint_type == VideoFingerprintType.TEMPORAL_SIGNATURE:
                fingerprint_data = await self._extract_temporal_signature(frames, frame_indices)
            else:
                raise ValueError(f"Unsupported fingerprint type: {fingerprint_type}")
            
            return VideoFingerprint(
                video_id=video_id,
                fingerprint_type=fingerprint_type,
                fingerprint_data=fingerprint_data,
                frame_count=video_info['frame_count'],
                duration_seconds=video_info['duration_seconds'],
                resolution=video_info['resolution'],
                fps=video_info['fps'],
                sampling_method=sampling_method,
                sampled_frame_count=len(frames)
            )
            
        except Exception as e:
            self.logger.error(f"Error extracting {fingerprint_type.value}: {str(e)}")
            raise
    
    async def _extract_perceptual_hashes(self, frames: List[np.ndarray]) -> List[str]:
        """Extract perceptual hashes from frames"""        try:
            hashes = []
            
            if IMAGEHASH_AVAILABLE:
                # Use imagehash library for better perceptual hashing
                for frame in frames:
                    # Convert BGR to RGB
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pil_image = Image.fromarray(rgb_frame)
                    
                    # Calculate multiple hash types for robustness
                    avg_hash = str(imagehash.average_hash(pil_image))
                    p_hash = str(imagehash.phash(pil_image))
                    d_hash = str(imagehash.dhash(pil_image))
                    
                    # Combine hashes
                    combined_hash = f"{avg_hash}:{p_hash}:{d_hash}"
                    hashes.append(combined_hash)
            else:
                # Fallback to simple hash
                for frame in frames:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    resized = cv2.resize(gray, (8, 8))
                    hash_value = hashlib.md5(resized.tobytes()).hexdigest()
                    hashes.append(hash_value)
            
            return hashes
            
        except Exception as e:
            self.logger.error(f"Error extracting perceptual hashes: {str(e)}")
            return []
    
    async def _extract_color_histograms(self, frames: List[np.ndarray]) -> List[np.ndarray]:
        """Extract color histograms from frames"""        try:
            histograms = []
            
            for frame in frames:
                # Calculate histogram for each color channel
                hist_b = cv2.calcHist([frame], [0], None, [256], [0, 256])
                hist_g = cv2.calcHist([frame], [1], None, [256], [0, 256])
                hist_r = cv2.calcHist([frame], [2], None, [256], [0, 256])
                
                # Concatenate and normalize
                hist = np.concatenate([hist_b, hist_g, hist_r]).flatten()
                hist = hist / np.sum(hist)  # Normalize
                
                histograms.append(hist)
            
            return histograms
            
        except Exception as e:
            self.logger.error(f"Error extracting color histograms: {str(e)}")
            return []
    
    async def _extract_edge_densities(self, frames: List[np.ndarray]) -> List[float]:
        """Extract edge density features from frames"""        try:
            edge_densities = []
            
            for frame in frames:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Apply Canny edge detection
                edges = cv2.Canny(gray, 50, 150)
                
                # Calculate edge density
                edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
                edge_densities.append(edge_density)
            
            return edge_densities
            
        except Exception as e:
            self.logger.error(f"Error extracting edge densities: {str(e)}")
            return []
    
    async def _extract_feature_descriptors(self, frames: List[np.ndarray]) -> List[np.ndarray]:
        """Extract deep learning feature descriptors"""        try:
            if not self.feature_extractor:
                raise ValueError("Feature extractor not available")
            
            descriptors = []
            
            for frame in frames:
                # Convert to RGB and apply transforms
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                tensor = self.transform(rgb_frame).unsqueeze(0)
                
                # Move to GPU if available
                if torch.cuda.is_available():
                    tensor = tensor.cuda()
                
                # Extract features
                with torch.no_grad():
                    features = self.feature_extractor(tensor)
                    features = features.cpu().numpy().flatten()
                    descriptors.append(features)
            
            return descriptors
            
        except Exception as e:
            self.logger.error(f"Error extracting feature descriptors: {str(e)}")
            return []
    
    async def _extract_temporal_signature(self, frames: List[np.ndarray], 
                                        frame_indices: List[int]) -> Dict[str, Any]:
        """Extract temporal signature from frame sequence"""        try:
            # Calculate frame-to-frame differences
            differences = []
            for i in range(1, len(frames)):
                gray1 = cv2.cvtColor(frames[i-1], cv2.COLOR_BGR2GRAY)
                gray2 = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
                
                diff = cv2.absdiff(gray1, gray2)
                mean_diff = np.mean(diff)
                differences.append(mean_diff)
            
            # Calculate temporal statistics
            temporal_signature = {
                'mean_difference': np.mean(differences),
                'std_difference': np.std(differences),
                'max_difference': np.max(differences),
                'min_difference': np.min(differences),
                'difference_sequence': differences,
                'frame_indices': frame_indices
            }
            
            return temporal_signature
            
        except Exception as e:
            self.logger.error(f"Error extracting temporal signature: {str(e)}")
            return {}
    
    async def _compare_perceptual_hashes(self, 
                                       fingerprint1: VideoFingerprint,
                                       fingerprint2: VideoFingerprint) -> Tuple[float, List[Tuple[int, int]]]:
        """Compare perceptual hashes between two videos"""        try:
            hashes1 = fingerprint1.fingerprint_data
            hashes2 = fingerprint2.fingerprint_data
            
            matched_frames = []
            similarities = []
            
            # Compare each frame hash from video1 with all frame hashes from video2
            for i, hash1 in enumerate(hashes1):
                best_similarity = 0.0
                best_match_idx = -1
                
                for j, hash2 in enumerate(hashes2):
                    if IMAGEHASH_AVAILABLE and ':' in hash1 and ':' in hash2:
                        # Parse combined hashes
                        h1_parts = hash1.split(':')
                        h2_parts = hash2.split(':')
                        
                        # Calculate similarity for each hash type
                        similarities_parts = []
                        for h1_part, h2_part in zip(h1_parts, h2_parts):
                            # Hamming distance for perceptual hashes
                            hamming_dist = sum(c1 != c2 for c1, c2 in zip(h1_part, h2_part))
                            similarity = 1.0 - (hamming_dist / len(h1_part))
                            similarities_parts.append(similarity)
                        
                        # Average similarity across hash types
                        similarity = np.mean(similarities_parts)
                    else:
                        # Simple string comparison for fallback hashes
                        similarity = 1.0 if hash1 == hash2 else 0.0
                    
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match_idx = j
                
                if best_similarity > 0.7:  # Threshold for considering a match
                    matched_frames.append((i, best_match_idx))
                    similarities.append(best_similarity)
            
            # Calculate overall similarity
            overall_similarity = np.mean(similarities) if similarities else 0.0
            
            return overall_similarity, matched_frames
            
        except Exception as e:
            self.logger.error(f"Error comparing perceptual hashes: {str(e)}")
            return 0.0, []
    
    async def _compare_color_histograms(self, 
                                      fingerprint1: VideoFingerprint,
                                      fingerprint2: VideoFingerprint) -> Tuple[float, List[Tuple[int, int]]]:
        """Compare color histograms between two videos"""        try:
            histograms1 = fingerprint1.fingerprint_data
            histograms2 = fingerprint2.fingerprint_data
            
            matched_frames = []
            similarities = []
            
            for i, hist1 in enumerate(histograms1):
                best_similarity = 0.0
                best_match_idx = -1
                
                for j, hist2 in enumerate(histograms2):
                    # Calculate histogram correlation
                    correlation = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
                    
                    if correlation > best_similarity:
                        best_similarity = correlation
                        best_match_idx = j
                
                if best_similarity > 0.8:  # Threshold for histogram similarity
                    matched_frames.append((i, best_match_idx))
                    similarities.append(best_similarity)
            
            overall_similarity = np.mean(similarities) if similarities else 0.0
            
            return overall_similarity, matched_frames
            
        except Exception as e:
            self.logger.error(f"Error comparing color histograms: {str(e)}")
            return 0.0, []
    
    async def _compare_edge_densities(self, 
                                    fingerprint1: VideoFingerprint,
                                    fingerprint2: VideoFingerprint) -> Tuple[float, List[Tuple[int, int]]]:
        """Compare edge densities between two videos"""        try:
            densities1 = fingerprint1.fingerprint_data
            densities2 = fingerprint2.fingerprint_data
            
            matched_frames = []
            similarities = []
            
            for i, density1 in enumerate(densities1):
                best_similarity = 0.0
                best_match_idx = -1
                
                for j, density2 in enumerate(densities2):
                    # Calculate similarity based on density difference
                    diff = abs(density1 - density2)
                    similarity = 1.0 - min(diff, 1.0)  # Clamp to [0, 1]
                    
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match_idx = j
                
                if best_similarity > 0.7:
                    matched_frames.append((i, best_match_idx))
                    similarities.append(best_similarity)
            
            overall_similarity = np.mean(similarities) if similarities else 0.0
            
            return overall_similarity, matched_frames
            
        except Exception as e:
            self.logger.error(f"Error comparing edge densities: {str(e)}")
            return 0.0, []
    
    async def _compare_feature_descriptors(self, 
                                         fingerprint1: VideoFingerprint,
                                         fingerprint2: VideoFingerprint) -> Tuple[float, List[Tuple[int, int]]]:
        """Compare deep learning feature descriptors"""        try:
            descriptors1 = fingerprint1.fingerprint_data
            descriptors2 = fingerprint2.fingerprint_data
            
            matched_frames = []
            similarities = []
            
            for i, desc1 in enumerate(descriptors1):
                best_similarity = 0.0
                best_match_idx = -1
                
                for j, desc2 in enumerate(descriptors2):
                    # Calculate cosine similarity
                    similarity = np.dot(desc1, desc2) / (np.linalg.norm(desc1) * np.linalg.norm(desc2))
                    
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match_idx = j
                
                if best_similarity > 0.8:
                    matched_frames.append((i, best_match_idx))
                    similarities.append(best_similarity)
            
            overall_similarity = np.mean(similarities) if similarities else 0.0
            
            return overall_similarity, matched_frames
            
        except Exception as e:
            self.logger.error(f"Error comparing feature descriptors: {str(e)}")
            return 0.0, []
    
    def _calculate_temporal_alignment(self, 
                                    matched_frames: List[Tuple[int, int]],
                                    duration1: float, 
                                    duration2: float) -> Dict[str, Any]:
        """Calculate temporal alignment between matched frames"""        try:
            if not matched_frames:
                return {}
            
            # Extract frame indices
            indices1 = [frame[0] for frame in matched_frames]
            indices2 = [frame[1] for frame in matched_frames]
            
            # Calculate temporal offsets
            frame_rate_1 = len(indices1) / duration1 if duration1 > 0 else 0
            frame_rate_2 = len(indices2) / duration2 if duration2 > 0 else 0
            
            temporal_alignment = {
                'matched_frame_count': len(matched_frames),
                'temporal_offset': np.mean(np.array(indices2) - np.array(indices1)),
                'temporal_drift': np.std(np.array(indices2) - np.array(indices1)),
                'frame_rate_ratio': frame_rate_2 / frame_rate_1 if frame_rate_1 > 0 else 0,
                'coverage_ratio_1': len(set(indices1)) / max(indices1) if indices1 else 0,
                'coverage_ratio_2': len(set(indices2)) / max(indices2) if indices2 else 0
            }
            
            return temporal_alignment
            
        except Exception as e:
            self.logger.error(f"Error calculating temporal alignment: {str(e)}")
            return {}
    
    def _calculate_confidence_metrics(self, 
                                    similarity_score: float,
                                    matched_frames: List[Tuple[int, int]],
                                    fingerprint1: VideoFingerprint,
                                    fingerprint2: VideoFingerprint) -> Dict[str, float]:
        """Calculate confidence metrics for the match"""        try:
            total_frames_1 = fingerprint1.sampled_frame_count
            total_frames_2 = fingerprint2.sampled_frame_count
            matched_count = len(matched_frames)
            
            confidence_metrics = {
                'similarity_score': similarity_score,
                'match_ratio_1': matched_count / total_frames_1 if total_frames_1 > 0 else 0,
                'match_ratio_2': matched_count / total_frames_2 if total_frames_2 > 0 else 0,
                'overall_match_ratio': matched_count / max(total_frames_1, total_frames_2) if max(total_frames_1, total_frames_2) > 0 else 0,
                'duration_ratio': min(fingerprint1.duration_seconds, fingerprint2.duration_seconds) / max(fingerprint1.duration_seconds, fingerprint2.duration_seconds) if max(fingerprint1.duration_seconds, fingerprint2.duration_seconds) > 0 else 0,
                'resolution_compatibility': self._calculate_resolution_compatibility(fingerprint1.resolution, fingerprint2.resolution)
            }
            
            return confidence_metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating confidence metrics: {str(e)}")
            return {}
    
    def _calculate_resolution_compatibility(self, res1: Tuple[int, int], res2: Tuple[int, int]) -> float:
        """Calculate resolution compatibility score"""        try:
            w1, h1 = res1
            w2, h2 = res2
            
            # Calculate aspect ratio similarity
            aspect_ratio_1 = w1 / h1 if h1 > 0 else 0
            aspect_ratio_2 = w2 / h2 if h2 > 0 else 0
            
            if aspect_ratio_1 > 0 and aspect_ratio_2 > 0:
                aspect_ratio_similarity = min(aspect_ratio_1, aspect_ratio_2) / max(aspect_ratio_1, aspect_ratio_2)
            else:
                aspect_ratio_similarity = 0.0
            
            # Calculate size similarity
            size_1 = w1 * h1
            size_2 = w2 * h2
            
            if size_1 > 0 and size_2 > 0:
                size_similarity = min(size_1, size_2) / max(size_1, size_2)
            else:
                size_similarity = 0.0
            
            # Weighted combination
            compatibility = 0.7 * aspect_ratio_similarity + 0.3 * size_similarity
            
            return compatibility
            
        except Exception as e:
            self.logger.error(f"Error calculating resolution compatibility: {str(e)}")
            return 0.0
    
    def _identify_match_regions(self, 
                              matched_frames: List[Tuple[int, int]], 
                              similarity_score: float) -> List[Dict[str, Any]]:
        """Identify continuous regions of matches"""        try:
            if not matched_frames:
                return []
            
            # Sort by first frame index
            sorted_matches = sorted(matched_frames, key=lambda x: x[0])
            
            # Group continuous regions
            regions = []
            current_region = [sorted_matches[0]]
            
            for i in range(1, len(sorted_matches)):
                prev_frame = sorted_matches[i-1][0]
                curr_frame = sorted_matches[i][0]
                
                # If frames are continuous (within 3 frames), add to current region
                if curr_frame - prev_frame <= 3:
                    current_region.append(sorted_matches[i])
                else:
                    # End current region and start new one
                    if len(current_region) >= 2:  # Minimum region size
                        regions.append(current_region)
                    current_region = [sorted_matches[i]]
            
            # Add last region
            if len(current_region) >= 2:
                regions.append(current_region)
            
            # Convert to region dictionaries
            match_regions = []
            for region in regions:
                start_frame_1 = region[0][0]
                end_frame_1 = region[-1][0]
                start_frame_2 = region[0][1]
                end_frame_2 = region[-1][1]
                
                region_dict = {
                    'start_frame_query': start_frame_1,
                    'end_frame_query': end_frame_1,
                    'start_frame_match': start_frame_2,
                    'end_frame_match': end_frame_2,
                    'region_length': len(region),
                    'region_similarity': similarity_score,  # Could be more specific per region
                    'matched_frames': region
                }
                
                match_regions.append(region_dict)
            
            return match_regions
            
        except Exception as e:
            self.logger.error(f"Error identifying match regions: {str(e)}")
            return []
    
    def _cache_frames(self, video_id: str, frames: List[np.ndarray]):
        """Cache frames for reuse"""        try:
            if len(self.frame_cache) >= self.cache_max_size:
                # Remove oldest entry
                oldest_key = next(iter(self.frame_cache))
                del self.frame_cache[oldest_key]
            
            self.frame_cache[video_id] = frames.copy()
            
        except Exception as e:
            self.logger.warning(f"Error caching frames for {video_id}: {str(e)}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get fingerprinter statistics"""        avg_processing_time = (self.total_processing_time / self.processing_count 
                             if self.processing_count > 0 else 0.0)
        
        return {
            'processing_count': self.processing_count,
            'average_processing_time': avg_processing_time,
            'cached_videos': len(self.frame_cache),
            'gpu_acceleration': self.gpu_acceleration,
            'torch_available': TORCH_AVAILABLE,
            'imagehash_available': IMAGEHASH_AVAILABLE,
            'feature_extractor_loaded': self.feature_extractor is not None
        }
    
    async def close(self):
        """Cleanup resources"""        try:
            if self.thread_pool:
                self.thread_pool.shutdown(wait=True)
            
            # Clear cache
            self.frame_cache.clear()
            
            self.logger.info("Video fingerprinter closed successfully")
            
        except Exception as e:
            self.logger.error(f"Error closing video fingerprinter: {str(e)}")
