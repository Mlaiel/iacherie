"""Advanced Video Analytics Engine
Professional video analysis, motion detection, and scene analysis.

This module provides comprehensive video analytics including motion tracking,
scene change detection, quality assessment, and temporal analysis.

Author: Fahed Mlaiel <mlaiel@live.de>
Project Team: Lead AI Developer + Backend Senior Engineer + ML Engineer + 
              Database Administrator + Security Expert + Microservices Architect +
              Multimedia Processing Specialist + DevOps Engineer + AI Prompt Engineer

⚠️ COPYRIGHT PROTECTION ⚠️
This code is proprietary and confidential. Unauthorized use is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import logging
import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path
import asyncio
from datetime import datetime
from skimage.metrics import structural_similarity as ssim
from scipy import ndimage
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

@dataclass
class VideoMetrics:
    """Comprehensive video metrics data structure"""
    file_path: str
    duration: float
    frame_count: int
    fps: float
    resolution: Tuple[int, int]
    codec: Optional[str] = None
    bitrate: Optional[float] = None
    
    # Quality metrics
    quality_score: float = 0.0
    average_psnr: float = 0.0
    average_ssim: float = 0.0
    sharpness_score: float = 0.0
    
    # Motion analysis
    motion_intensity: float = 0.0
    motion_vectors: List[Dict[str, Any]] = field(default_factory=list)
    static_scenes_percentage: float = 0.0
    
    # Scene analysis
    scene_changes: List[Dict[str, Any]] = field(default_factory=list)
    scene_count: int = 0
    average_scene_duration: float = 0.0
    
    # Temporal features
    temporal_stability: float = 0.0
    frame_consistency: float = 0.0
    flicker_detection: List[Dict[str, Any]] = field(default_factory=list)
    
    # Content analysis
    color_distribution: Dict[str, float] = field(default_factory=dict)
    brightness_distribution: Dict[str, float] = field(default_factory=dict)
    contrast_levels: List[float] = field(default_factory=list)
    
    # Technical analysis
    encoding_artifacts: List[Dict[str, Any]] = field(default_factory=list)
    compression_artifacts: float = 0.0
    noise_level: float = 0.0
    
    # Processing metadata
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    processing_time: float = 0.0


class MotionDetector:
    """Advanced motion detection and analysis"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logger.getChild(self.__class__.__name__)
        
        # Motion detection parameters
        self.motion_threshold = self.config.get('motion_threshold', 25)
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2(
            detectShadows=True,
            varThreshold=self.config.get('var_threshold', 16)
        )
        
    async def detect_motion(self, frame1: np.ndarray, frame2: np.ndarray) -> Dict[str, Any]:
        """Detect motion between two consecutive frames"""
        try:
            # Convert to grayscale
            gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
            
            # Calculate optical flow
            flow = cv2.calcOpticalFlowPyrLK(gray1, gray2, None, None)
            
            # Calculate motion magnitude
            diff = cv2.absdiff(gray1, gray2)
            motion_mask = cv2.threshold(diff, self.motion_threshold, 255, cv2.THRESH_BINARY)[1]
            
            # Calculate motion statistics
            motion_percentage = np.sum(motion_mask > 0) / motion_mask.size * 100
            motion_intensity = float(np.mean(diff))
            
            # Detect motion vectors
            motion_vectors = self._calculate_motion_vectors(gray1, gray2)
            
            return {
                'motion_percentage': motion_percentage,
                'motion_intensity': motion_intensity,
                'motion_vectors': motion_vectors,
                'motion_mask': motion_mask
            }
            
        except Exception as e:
            self.logger.error(f"Motion detection failed: {e}")
            return {}
    
    def _calculate_motion_vectors(self, frame1: np.ndarray, frame2: np.ndarray) -> List[Dict[str, Any]]:
        """Calculate dense optical flow motion vectors"""
        try:
            flow = cv2.calcOpticalFlowPyrLK(frame1, frame2, None, None)
            
            # Create grid of points
            h, w = frame1.shape
            y, x = np.mgrid[0:h:20, 0:w:20].reshape(2, -1).astype(int)
            points = np.column_stack([x, y])
            
            # Calculate flow for grid points
            flow_dense = cv2.calcOpticalFlowPyrLK(frame1, frame2, points.astype(np.float32), None)
            
            vectors = []
            if flow_dense[0] is not None:
                for i, (point, new_point) in enumerate(zip(points, flow_dense[0])):
                    if flow_dense[1][i] == 1:  # Good tracking
                        vectors.append({
                            'start_point': point.tolist(),
                            'end_point': new_point.tolist(),
                            'magnitude': float(np.linalg.norm(new_point - point)),
                            'angle': float(np.arctan2(new_point[1] - point[1], new_point[0] - point[0]))
                        })
            
            return vectors
            
        except Exception as e:
            self.logger.error(f"Motion vector calculation failed: {e}")
            return []


class SceneAnalyzer:
    """Scene change detection and analysis"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logger.getChild(self.__class__.__name__)
        
        # Scene detection parameters
        self.scene_threshold = self.config.get('scene_threshold', 0.3)
        self.min_scene_duration = self.config.get('min_scene_duration', 1.0)  # seconds
        
    async def detect_scene_changes(self, frames: List[np.ndarray], fps: float) -> List[Dict[str, Any]]:
        """Detect scene changes in video frames"""
        try:
            scene_changes = []
            
            for i in range(1, len(frames)):
                # Calculate histogram difference
                hist_diff = self._calculate_histogram_difference(frames[i-1], frames[i])
                
                # Calculate structural similarity
                ssim_score = self._calculate_ssim(frames[i-1], frames[i])
                
                # Determine if scene change occurred
                if hist_diff > self.scene_threshold or ssim_score < (1 - self.scene_threshold):
                    timestamp = i / fps
                    scene_changes.append({
                        'frame_index': i,
                        'timestamp': timestamp,
                        'histogram_difference': float(hist_diff),
                        'ssim_score': float(ssim_score),
                        'confidence': float((hist_diff + (1 - ssim_score)) / 2)
                    })
            
            # Filter out scene changes that are too close together
            filtered_changes = self._filter_scene_changes(scene_changes, fps)
            
            return filtered_changes
            
        except Exception as e:
            self.logger.error(f"Scene change detection failed: {e}")
            return []
    
    def _calculate_histogram_difference(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        """Calculate histogram difference between frames"""
        try:
            # Convert to HSV for better color representation
            hsv1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2HSV)
            hsv2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2HSV)
            
            # Calculate histograms
            hist1 = cv2.calcHist([hsv1], [0, 1, 2], None, [50, 60, 60], [0, 180, 0, 256, 0, 256])
            hist2 = cv2.calcHist([hsv2], [0, 1, 2], None, [50, 60, 60], [0, 180, 0, 256, 0, 256])
            
            # Normalize histograms
            cv2.normalize(hist1, hist1, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
            cv2.normalize(hist2, hist2, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
            
            # Calculate correlation
            correlation = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
            
            return 1 - correlation  # Convert to difference
            
        except Exception as e:
            self.logger.error(f"Histogram calculation failed: {e}")
            return 0.0
    
    def _calculate_ssim(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        """Calculate structural similarity between frames"""
        try:
            # Convert to grayscale
            gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
            
            # Resize for faster computation
            height, width = gray1.shape
            if height > 480 or width > 640:
                scale = min(480/height, 640/width)
                new_height, new_width = int(height*scale), int(width*scale)
                gray1 = cv2.resize(gray1, (new_width, new_height))
                gray2 = cv2.resize(gray2, (new_width, new_height))
            
            # Calculate SSIM
            ssim_score = ssim(gray1, gray2)
            return float(ssim_score)
            
        except Exception as e:
            self.logger.error(f"SSIM calculation failed: {e}")
            return 0.0
    
    def _filter_scene_changes(self, scene_changes: List[Dict[str, Any]], fps: float) -> List[Dict[str, Any]]:
        """Filter scene changes that are too close together"""
        if not scene_changes:
            return []
        
        filtered = [scene_changes[0]]
        min_frames = int(self.min_scene_duration * fps)
        
        for change in scene_changes[1:]:
            if change['frame_index'] - filtered[-1]['frame_index'] >= min_frames:
                filtered.append(change)
        
        return filtered


class VideoAnalyzer:
    """Comprehensive video analysis engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logger.getChild(self.__class__.__name__)
        
        # Initialize sub-analyzers
        self.motion_detector = MotionDetector(config)
        self.scene_analyzer = SceneAnalyzer(config)
        
        # Analysis parameters
        self.quality_threshold = self.config.get('quality_threshold', 0.7)
        self.sample_rate = self.config.get('sample_rate', 1.0)  # Analyze every N frames
        
    async def analyze_file(self, file_path: str) -> VideoMetrics:
        """Comprehensive video file analysis"""
        start_time = datetime.now()
        
        try:
            # Open video file
            cap = cv2.VideoCapture(file_path)
            if not cap.isOpened():
                raise ValueError(f"Cannot open video file: {file_path}")
            
            # Get video properties
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Initialize metrics
            metrics = VideoMetrics(
                file_path=file_path,
                duration=frame_count / fps if fps > 0 else 0,
                frame_count=frame_count,
                fps=fps,
                resolution=(width, height)
            )
            
            # Sample frames for analysis
            frames = await self._sample_frames(cap, frame_count)
            cap.release()
            
            if len(frames) < 2:
                raise ValueError("Insufficient frames for analysis")
            
            # Quality analysis
            await self._analyze_quality(frames, metrics)
            
            # Motion analysis
            await self._analyze_motion(frames, metrics)
            
            # Scene analysis
            await self._analyze_scenes(frames, metrics)
            
            # Temporal analysis
            await self._analyze_temporal_features(frames, metrics)
            
            # Content analysis
            await self._analyze_content(frames, metrics)
            
            # Calculate processing time
            metrics.processing_time = (datetime.now() - start_time).total_seconds()
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Video analysis failed for {file_path}: {e}")
            raise
    
    async def _sample_frames(self, cap: cv2.VideoCapture, frame_count: int) -> List[np.ndarray]:
        """Sample frames from video for analysis"""
        try:
            frames = []
            sample_interval = max(1, int(1 / self.sample_rate))
            
            for i in range(0, frame_count, sample_interval):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                if ret:
                    frames.append(frame)
                
                # Limit number of frames to prevent memory issues
                if len(frames) >= 1000:
                    break
            
            return frames
            
        except Exception as e:
            self.logger.error(f"Frame sampling failed: {e}")
            return []
    
    async def _analyze_quality(self, frames: List[np.ndarray], metrics: VideoMetrics) -> None:
        """Analyze video quality metrics"""
        try:
            if len(frames) < 2:
                return
            
            # Calculate average PSNR between consecutive frames
            psnr_values = []
            ssim_values = []
            sharpness_values = []
            
            for i in range(len(frames) - 1):
                # PSNR calculation
                mse = np.mean((frames[i].astype(float) - frames[i+1].astype(float)) ** 2)
                if mse > 0:
                    psnr = 20 * np.log10(255.0 / np.sqrt(mse))
                    psnr_values.append(psnr)
                
                # SSIM calculation
                gray1 = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
                gray2 = cv2.cvtColor(frames[i+1], cv2.COLOR_BGR2GRAY)
                ssim_val = ssim(gray1, gray2)
                ssim_values.append(ssim_val)
            
            # Sharpness analysis
            for frame in frames[::10]:  # Sample every 10th frame
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                laplacian = cv2.Laplacian(gray, cv2.CV_64F)
                sharpness = laplacian.var()
                sharpness_values.append(sharpness)
            
            # Set metrics
            metrics.average_psnr = float(np.mean(psnr_values)) if psnr_values else 0.0
            metrics.average_ssim = float(np.mean(ssim_values)) if ssim_values else 0.0
            metrics.sharpness_score = float(np.mean(sharpness_values)) if sharpness_values else 0.0
            
            # Overall quality score
            quality_factors = [
                min(metrics.average_psnr / 40.0, 1.0),  # Normalize PSNR
                metrics.average_ssim,  # SSIM already 0-1
                min(metrics.sharpness_score / 1000.0, 1.0)  # Normalize sharpness
            ]
            metrics.quality_score = float(np.mean(quality_factors))
            
        except Exception as e:
            self.logger.error(f"Quality analysis failed: {e}")
    
    async def _analyze_motion(self, frames: List[np.ndarray], metrics: VideoMetrics) -> None:
        """Analyze motion characteristics"""
        try:
            motion_data = []
            
            for i in range(len(frames) - 1):
                motion_result = await self.motion_detector.detect_motion(frames[i], frames[i+1])
                motion_data.append(motion_result)
            
            if motion_data:
                # Calculate motion statistics
                motion_intensities = [data.get('motion_intensity', 0) for data in motion_data]
                motion_percentages = [data.get('motion_percentage', 0) for data in motion_data]
                
                metrics.motion_intensity = float(np.mean(motion_intensities))
                metrics.static_scenes_percentage = float(np.mean([p < 1.0 for p in motion_percentages]) * 100)
                
                # Store motion vectors from selected frames
                for i, data in enumerate(motion_data[::10]):  # Sample every 10th frame
                    if 'motion_vectors' in data and data['motion_vectors']:
                        metrics.motion_vectors.extend(data['motion_vectors'][:5])  # Top 5 vectors
            
        except Exception as e:
            self.logger.error(f"Motion analysis failed: {e}")
    
    async def _analyze_scenes(self, frames: List[np.ndarray], metrics: VideoMetrics) -> None:
        """Analyze scene changes and composition"""
        try:
            scene_changes = await self.scene_analyzer.detect_scene_changes(frames, metrics.fps)
            
            metrics.scene_changes = scene_changes
            metrics.scene_count = len(scene_changes) + 1  # +1 for the initial scene
            
            if metrics.scene_count > 1:
                scene_durations = []
                for i, change in enumerate(scene_changes):
                    if i == 0:
                        scene_durations.append(change['timestamp'])
                    else:
                        duration = change['timestamp'] - scene_changes[i-1]['timestamp']
                        scene_durations.append(duration)
                
                # Add duration of last scene
                if scene_changes:
                    last_duration = metrics.duration - scene_changes[-1]['timestamp']
                    scene_durations.append(last_duration)
                
                metrics.average_scene_duration = float(np.mean(scene_durations))
            
        except Exception as e:
            self.logger.error(f"Scene analysis failed: {e}")
    
    async def _analyze_temporal_features(self, frames: List[np.ndarray], metrics: VideoMetrics) -> None:
        """Analyze temporal stability and consistency"""
        try:
            if len(frames) < 3:
                return
            
            # Frame consistency (how similar consecutive frames are)
            consistency_scores = []
            for i in range(len(frames) - 1):
                gray1 = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
                gray2 = cv2.cvtColor(frames[i+1], cv2.COLOR_BGR2GRAY)
                consistency = ssim(gray1, gray2)
                consistency_scores.append(consistency)
            
            metrics.frame_consistency = float(np.mean(consistency_scores))
            
            # Temporal stability (variation in global brightness/contrast)
            brightness_values = []
            for frame in frames:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                brightness_values.append(np.mean(gray))
            
            brightness_stability = 1.0 - (np.std(brightness_values) / 255.0)
            metrics.temporal_stability = float(max(0.0, brightness_stability))
            
            # Flicker detection (rapid brightness changes)
            flicker_events = []
            threshold = 20  # Brightness change threshold
            
            for i in range(1, len(brightness_values)):
                brightness_change = abs(brightness_values[i] - brightness_values[i-1])
                if brightness_change > threshold:
                    flicker_events.append({
                        'frame_index': i,
                        'timestamp': i / metrics.fps if metrics.fps > 0 else i,
                        'brightness_change': float(brightness_change)
                    })
            
            metrics.flicker_detection = flicker_events
            
        except Exception as e:
            self.logger.error(f"Temporal analysis failed: {e}")
    
    async def _analyze_content(self, frames: List[np.ndarray], metrics: VideoMetrics) -> None:
        """Analyze content characteristics"""
        try:
            # Sample frames for content analysis
            sample_frames = frames[::max(1, len(frames)//20)]  # Sample 20 frames max
            
            # Color distribution analysis
            color_stats = {'red': [], 'green': [], 'blue': []}
            brightness_values = []
            contrast_values = []
            
            for frame in sample_frames:
                # Color analysis
                color_stats['blue'].append(np.mean(frame[:, :, 0]))
                color_stats['green'].append(np.mean(frame[:, :, 1]))
                color_stats['red'].append(np.mean(frame[:, :, 2]))
                
                # Brightness analysis
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                brightness_values.append(np.mean(gray))
                
                # Contrast analysis
                contrast = np.std(gray)
                contrast_values.append(contrast)
            
            # Store color distribution
            metrics.color_distribution = {
                'average_red': float(np.mean(color_stats['red'])),
                'average_green': float(np.mean(color_stats['green'])),
                'average_blue': float(np.mean(color_stats['blue'])),
                'red_variance': float(np.var(color_stats['red'])),
                'green_variance': float(np.var(color_stats['green'])),
                'blue_variance': float(np.var(color_stats['blue']))
            }
            
            # Store brightness distribution
            metrics.brightness_distribution = {
                'average_brightness': float(np.mean(brightness_values)),
                'brightness_variance': float(np.var(brightness_values)),
                'min_brightness': float(np.min(brightness_values)),
                'max_brightness': float(np.max(brightness_values))
            }
            
            # Store contrast levels
            metrics.contrast_levels = [float(c) for c in contrast_values]
            
        except Exception as e:
            self.logger.error(f"Content analysis failed: {e}")
    
    async def batch_analyze(self, file_paths: List[str]) -> List[VideoMetrics]:
        """Analyze multiple video files"""
        try:
            tasks = [self.analyze_file(path) for path in file_paths]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            valid_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    self.logger.error(f"Failed to analyze {file_paths[i]}: {result}")
                else:
                    valid_results.append(result)
            
            return valid_results
            
        except Exception as e:
            self.logger.error(f"Batch video analysis failed: {e}")
            return []