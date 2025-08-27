"""
IA Influencer Agent - Video Fingerprinting Engine
Advanced video fingerprinting for content protection and identification

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved to Fahed Mlaiel
Warning: Unauthorized use, copying, or distribution of this code is strictly prohibited
"""

import asyncio
import hashlib
import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path
import cv2
import imagehash
from PIL import Image
import json
import time
from concurrent.futures import ThreadPoolExecutor
import base64

logger = logging.getLogger(__name__)


class VideoFingerprintEngine:
    """
    Professional video fingerprinting engine using multiple computer vision
    algorithms for robust content identification and protection
    """
    
    def __init__(
        self, 
        frame_sampling_rate: int = 30,
        hash_size: int = 8,
        max_frames: int = 100
    ):
        """
        Initialize video fingerprinting engine
        
        Args:
            frame_sampling_rate: Extract every Nth frame
            hash_size: Size for perceptual hashing
            max_frames: Maximum frames to process per video
        """
        self.frame_sampling_rate = frame_sampling_rate
        self.hash_size = hash_size
        self.max_frames = max_frames
        self.similarity_threshold = 0.85
        
        # Initialize OpenCV video capture
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        
        logger.info(f"VideoFingerprintEngine initialized with frame_rate={frame_sampling_rate}")
    
    async def extract_fingerprint(
        self, 
        video_path: Union[str, Path],
        methods: List[str] = None
    ) -> Dict[str, any]:
        """
        Extract comprehensive video fingerprint using multiple methods
        
        Args:
            video_path: Path to video file
            methods: List of fingerprinting methods to use
                    ['perceptual_hash', 'histogram', 'optical_flow', 'edge_detection']
        
        Returns:
            Dictionary containing all fingerprint data
        """
        if methods is None:
            methods = ['perceptual_hash', 'histogram', 'optical_flow', 'edge_detection']
        
        try:
            video_path = Path(video_path)
            if not video_path.exists():
                raise FileNotFoundError(f"Video file not found: {video_path}")
            
            # Extract video metadata
            video_info = await self._get_video_info(video_path)
            
            if video_info['frame_count'] == 0:
                raise ValueError(f"Invalid video file: {video_path}")
            
            # Extract frames
            frames = await self._extract_frames(video_path, video_info)
            
            if not frames:
                raise ValueError(f"No frames extracted from video: {video_path}")
            
            fingerprint_data = {
                'file_path': str(video_path),
                'video_info': video_info,
                'frame_count': len(frames),
                'file_size': video_path.stat().st_size,
                'created_at': time.time(),
                'methods': {}
            }
            
            # Execute fingerprinting methods
            if 'perceptual_hash' in methods:
                fingerprint_data['methods']['perceptual_hash'] = await self._extract_perceptual_hash(frames)
            
            if 'histogram' in methods:
                fingerprint_data['methods']['histogram'] = await self._extract_histogram_features(frames)
            
            if 'optical_flow' in methods:
                fingerprint_data['methods']['optical_flow'] = await self._extract_optical_flow(frames)
            
            if 'edge_detection' in methods:
                fingerprint_data['methods']['edge_detection'] = await self._extract_edge_features(frames)
            
            # Generate combined hash
            fingerprint_data['combined_hash'] = self._generate_combined_hash(fingerprint_data['methods'])
            
            logger.info(f"Successfully extracted video fingerprint for {video_path.name}")
            return fingerprint_data
            
        except Exception as e:
            logger.error(f"Error extracting video fingerprint from {video_path}: {str(e)}")
            raise
    
    async def _get_video_info(self, video_path: Path) -> Dict[str, any]:
        """Extract video metadata"""
        try:
            cap = cv2.VideoCapture(str(video_path))
            
            if not cap.isOpened():
                raise ValueError(f"Cannot open video file: {video_path}")
            
            info = {
                'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                'fps': float(cap.get(cv2.CAP_PROP_FPS)),
                'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
                'duration': 0.0,
                'codec': int(cap.get(cv2.CAP_PROP_FOURCC))
            }
            
            if info['fps'] > 0:
                info['duration'] = info['frame_count'] / info['fps']
            
            cap.release()
            return info
            
        except Exception as e:
            logger.error(f"Error getting video info: {str(e)}")
            return {'width': 0, 'height': 0, 'fps': 0, 'frame_count': 0, 'duration': 0.0}
    
    async def _extract_frames(self, video_path: Path, video_info: Dict) -> List[np.ndarray]:
        """Extract frames from video for analysis"""
        try:
            cap = cv2.VideoCapture(str(video_path))
            frames = []
            frame_idx = 0
            
            # Calculate frame sampling strategy
            total_frames = video_info['frame_count']
            if total_frames > self.max_frames:
                step = max(1, total_frames // self.max_frames)
            else:
                step = max(1, self.frame_sampling_rate)
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_idx % step == 0:
                    # Convert BGR to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frames.append(frame_rgb)
                    
                    if len(frames) >= self.max_frames:
                        break
                
                frame_idx += 1
            
            cap.release()
            logger.info(f"Extracted {len(frames)} frames from video")
            return frames
            
        except Exception as e:
            logger.error(f"Error extracting frames: {str(e)}")
            return []
    
    async def _extract_perceptual_hash(self, frames: List[np.ndarray]) -> Dict[str, any]:
        """Extract perceptual hash fingerprints for frames"""
        try:
            hashes = []
            hash_strings = []
            
            for frame in frames:
                # Convert to PIL Image for imagehash
                pil_frame = Image.fromarray(frame)
                
                # Generate different types of perceptual hashes
                ahash = imagehash.average_hash(pil_frame, hash_size=self.hash_size)
                dhash = imagehash.dhash(pil_frame, hash_size=self.hash_size)
                phash = imagehash.phash(pil_frame, hash_size=self.hash_size)
                whash = imagehash.whash(pil_frame, hash_size=self.hash_size)
                
                frame_hashes = {
                    'average_hash': str(ahash),
                    'difference_hash': str(dhash),
                    'perceptual_hash': str(phash),
                    'wavelet_hash': str(whash)
                }
                
                hashes.append(frame_hashes)
                
                # Combine hashes for frame signature
                combined_hash = hashlib.sha256(
                    f"{ahash}{dhash}{phash}{whash}".encode()
                ).hexdigest()
                hash_strings.append(combined_hash)
            
            # Generate video-level hash sequence
            sequence_hash = hashlib.sha256(''.join(hash_strings).encode()).hexdigest()
            
            return {
                'frame_hashes': hashes,
                'hash_sequence': hash_strings,
                'sequence_hash': sequence_hash,
                'frame_count': len(frames),
                'algorithm': 'perceptual_hash',
                'confidence': 0.92
            }
            
        except Exception as e:
            logger.error(f"Error in perceptual hash extraction: {str(e)}")
            return {'error': str(e), 'algorithm': 'perceptual_hash'}
    
    async def _extract_histogram_features(self, frames: List[np.ndarray]) -> Dict[str, any]:
        """Extract color histogram features"""
        try:
            histograms = []
            
            for frame in frames:
                # Convert to HSV for better color representation
                hsv_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
                
                # Calculate histograms for each channel
                h_hist = cv2.calcHist([hsv_frame], [0], None, [50], [0, 180])
                s_hist = cv2.calcHist([hsv_frame], [1], None, [60], [0, 256])
                v_hist = cv2.calcHist([hsv_frame], [2], None, [60], [0, 256])
                
                # Normalize histograms
                h_hist = h_hist.flatten() / np.sum(h_hist)
                s_hist = s_hist.flatten() / np.sum(s_hist)
                v_hist = v_hist.flatten() / np.sum(v_hist)
                
                frame_histogram = {
                    'hue': h_hist.tolist(),
                    'saturation': s_hist.tolist(),
                    'value': v_hist.tolist()
                }
                
                histograms.append(frame_histogram)
            
            # Calculate average histogram for video
            avg_hue = np.mean([h['hue'] for h in histograms], axis=0)
            avg_sat = np.mean([h['saturation'] for h in histograms], axis=0)
            avg_val = np.mean([h['value'] for h in histograms], axis=0)
            
            # Generate hash from average histograms
            combined_hist = np.concatenate([avg_hue, avg_sat, avg_val])
            histogram_hash = hashlib.sha256(combined_hist.tobytes()).hexdigest()
            
            return {
                'frame_histograms': histograms,
                'average_histogram': {
                    'hue': avg_hue.tolist(),
                    'saturation': avg_sat.tolist(),
                    'value': avg_val.tolist()
                },
                'histogram_hash': histogram_hash,
                'algorithm': 'histogram',
                'confidence': 0.85
            }
            
        except Exception as e:
            logger.error(f"Error in histogram extraction: {str(e)}")
            return {'error': str(e), 'algorithm': 'histogram'}
    
    async def _extract_optical_flow(self, frames: List[np.ndarray]) -> Dict[str, any]:
        """Extract optical flow features for motion analysis"""
        try:
            if len(frames) < 2:
                return {'error': 'Need at least 2 frames for optical flow', 'algorithm': 'optical_flow'}
            
            flow_features = []
            
            for i in range(len(frames) - 1):
                # Convert frames to grayscale
                gray1 = cv2.cvtColor(frames[i], cv2.COLOR_RGB2GRAY)
                gray2 = cv2.cvtColor(frames[i + 1], cv2.COLOR_RGB2GRAY)
                
                # Calculate optical flow
                flow = cv2.calcOpticalFlowPyrLK(
                    gray1, gray2, 
                    p0=cv2.goodFeaturesToTrack(gray1, maxCorners=100, qualityLevel=0.3, minDistance=7),
                    p1=None,
                    winSize=(15, 15),
                    maxLevel=2
                )[0]
                
                if flow is not None and len(flow) > 0:
                    # Calculate motion statistics
                    motion_magnitude = np.sqrt(flow[:, 0] ** 2 + flow[:, 1] ** 2)
                    motion_direction = np.arctan2(flow[:, 1], flow[:, 0])
                    
                    flow_stats = {
                        'mean_magnitude': float(np.mean(motion_magnitude)),
                        'max_magnitude': float(np.max(motion_magnitude)),
                        'mean_direction': float(np.mean(motion_direction)),
                        'direction_variance': float(np.var(motion_direction)),
                        'feature_count': len(flow)
                    }
                else:
                    flow_stats = {
                        'mean_magnitude': 0.0,
                        'max_magnitude': 0.0,
                        'mean_direction': 0.0,
                        'direction_variance': 0.0,
                        'feature_count': 0
                    }
                
                flow_features.append(flow_stats)
            
            # Calculate video-level motion characteristics
            avg_magnitude = np.mean([f['mean_magnitude'] for f in flow_features])
            avg_direction_var = np.mean([f['direction_variance'] for f in flow_features])
            
            # Generate motion hash
            motion_data = np.array([
                avg_magnitude, avg_direction_var,
                len(flow_features)
            ])
            motion_hash = hashlib.sha256(motion_data.tobytes()).hexdigest()
            
            return {
                'frame_flows': flow_features,
                'average_magnitude': float(avg_magnitude),
                'average_direction_variance': float(avg_direction_var),
                'motion_hash': motion_hash,
                'algorithm': 'optical_flow',
                'confidence': 0.78
            }
            
        except Exception as e:
            logger.error(f"Error in optical flow extraction: {str(e)}")
            return {'error': str(e), 'algorithm': 'optical_flow'}
    
    async def _extract_edge_features(self, frames: List[np.ndarray]) -> Dict[str, any]:
        """Extract edge detection features"""
        try:
            edge_features = []
            
            for frame in frames:
                # Convert to grayscale
                gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
                
                # Apply Canny edge detection
                edges = cv2.Canny(gray, 50, 150, apertureSize=3)
                
                # Calculate edge statistics
                edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
                
                # Detect lines using Hough transform
                lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
                line_count = len(lines) if lines is not None else 0
                
                # Calculate edge orientation histogram
                sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
                sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
                
                # Edge orientations
                edge_orientations = np.arctan2(sobel_y, sobel_x)
                orientation_hist = np.histogram(edge_orientations.flatten(), bins=18, range=(-np.pi, np.pi))[0]
                orientation_hist = orientation_hist / np.sum(orientation_hist)
                
                frame_edges = {
                    'edge_density': float(edge_density),
                    'line_count': int(line_count),
                    'orientation_histogram': orientation_hist.tolist()
                }
                
                edge_features.append(frame_edges)
            
            # Calculate video-level edge characteristics
            avg_edge_density = np.mean([f['edge_density'] for f in edge_features])
            avg_line_count = np.mean([f['line_count'] for f in edge_features])
            
            # Average orientation histogram
            avg_orientation = np.mean([f['orientation_histogram'] for f in edge_features], axis=0)
            
            # Generate edge hash
            edge_data = np.concatenate([
                [avg_edge_density, avg_line_count],
                avg_orientation
            ])
            edge_hash = hashlib.sha256(edge_data.tobytes()).hexdigest()
            
            return {
                'frame_edges': edge_features,
                'average_edge_density': float(avg_edge_density),
                'average_line_count': float(avg_line_count),
                'average_orientation': avg_orientation.tolist(),
                'edge_hash': edge_hash,
                'algorithm': 'edge_detection',
                'confidence': 0.80
            }
            
        except Exception as e:
            logger.error(f"Error in edge detection: {str(e)}")
            return {'error': str(e), 'algorithm': 'edge_detection'}
    
    def _generate_combined_hash(self, methods_data: Dict[str, any]) -> str:
        """Generate combined hash from all fingerprinting methods"""
        try:
            hash_parts = []
            
            for method, data in methods_data.items():
                if 'error' not in data:
                    # Extract primary hash from each method
                    if method == 'perceptual_hash' and 'sequence_hash' in data:
                        hash_parts.append(data['sequence_hash'])
                    elif method == 'histogram' and 'histogram_hash' in data:
                        hash_parts.append(data['histogram_hash'])
                    elif method == 'optical_flow' and 'motion_hash' in data:
                        hash_parts.append(data['motion_hash'])
                    elif method == 'edge_detection' and 'edge_hash' in data:
                        hash_parts.append(data['edge_hash'])
            
            # Combine all hashes
            combined_string = ''.join(sorted(hash_parts))
            combined_hash = hashlib.sha256(combined_string.encode()).hexdigest()
            
            return combined_hash
            
        except Exception as e:
            logger.error(f"Error generating combined hash: {str(e)}")
            return hashlib.sha256(str(time.time()).encode()).hexdigest()
    
    async def compare_fingerprints(
        self, 
        fingerprint1: Dict[str, any], 
        fingerprint2: Dict[str, any]
    ) -> Dict[str, float]:
        """
        Compare two video fingerprints and return similarity scores
        
        Args:
            fingerprint1: First fingerprint data
            fingerprint2: Second fingerprint data
        
        Returns:
            Dictionary with similarity scores for each method
        """
        similarities = {}
        
        try:
            # Compare each method
            for method in ['perceptual_hash', 'histogram', 'optical_flow', 'edge_detection']:
                if (method in fingerprint1.get('methods', {}) and 
                    method in fingerprint2.get('methods', {})):
                    
                    similarity = await self._compare_method(
                        fingerprint1['methods'][method],
                        fingerprint2['methods'][method],
                        method
                    )
                    similarities[method] = similarity
            
            # Overall similarity (weighted average)
            if similarities:
                weights = {'perceptual_hash': 0.4, 'histogram': 0.3, 'optical_flow': 0.2, 'edge_detection': 0.1}
                overall_similarity = sum(
                    similarities.get(method, 0) * weight 
                    for method, weight in weights.items()
                ) / sum(weights[method] for method in similarities.keys())
                
                similarities['overall'] = overall_similarity
            else:
                similarities['overall'] = 0.0
            
            return similarities
            
        except Exception as e:
            logger.error(f"Error comparing video fingerprints: {str(e)}")
            return {'overall': 0.0, 'error': str(e)}
    
    async def _compare_method(
        self, 
        data1: Dict[str, any], 
        data2: Dict[str, any], 
        method: str
    ) -> float:
        """Compare two fingerprints using specific method"""
        try:
            if 'error' in data1 or 'error' in data2:
                return 0.0
            
            if method == 'perceptual_hash':
                return self._compare_perceptual_hash(data1, data2)
            elif method == 'histogram':
                return self._compare_histogram(data1, data2)
            elif method == 'optical_flow':
                return self._compare_optical_flow(data1, data2)
            elif method == 'edge_detection':
                return self._compare_edge_detection(data1, data2)
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error comparing {method}: {str(e)}")
            return 0.0
    
    def _compare_perceptual_hash(self, data1: Dict, data2: Dict) -> float:
        """Compare perceptual hash sequences"""
        try:
            seq1 = data1.get('hash_sequence', [])
            seq2 = data2.get('hash_sequence', [])
            
            if not seq1 or not seq2:
                return 0.0
            
            # Compare hash sequences using dynamic time warping approximation
            min_len = min(len(seq1), len(seq2))
            max_len = max(len(seq1), len(seq2))
            
            if max_len == 0:
                return 0.0
            
            # Sample sequences for comparison
            if min_len > 0:
                step1 = max(1, len(seq1) // min_len)
                step2 = max(1, len(seq2) // min_len)
                
                sampled_seq1 = seq1[::step1][:min_len]
                sampled_seq2 = seq2[::step2][:min_len]
                
                # Calculate hash similarities
                similarities = []
                for h1, h2 in zip(sampled_seq1, sampled_seq2):
                    if h1 == h2:
                        similarities.append(1.0)
                    else:
                        # Hamming distance for similar hashes
                        if len(h1) == len(h2):
                            hamming_distance = sum(c1 != c2 for c1, c2 in zip(h1, h2))
                            sim = 1.0 - (hamming_distance / len(h1))
                            similarities.append(max(0.0, sim))
                        else:
                            similarities.append(0.0)
                
                avg_similarity = np.mean(similarities) if similarities else 0.0
                
                # Penalize length differences
                length_penalty = min_len / max_len
                
                return avg_similarity * length_penalty
            
            return 0.0
            
        except Exception:
            return 0.0
    
    def _compare_histogram(self, data1: Dict, data2: Dict) -> float:
        """Compare histogram features"""
        try:
            hist1 = data1.get('average_histogram', {})
            hist2 = data2.get('average_histogram', {})
            
            if not hist1 or not hist2:
                return 0.0
            
            # Compare each channel
            similarities = []
            for channel in ['hue', 'saturation', 'value']:
                h1 = np.array(hist1.get(channel, []))
                h2 = np.array(hist2.get(channel, []))
                
                if len(h1) == len(h2) and len(h1) > 0:
                    # Bhattacharyya coefficient for histogram comparison
                    bc = np.sum(np.sqrt(h1 * h2))
                    similarities.append(bc)
            
            return np.mean(similarities) if similarities else 0.0
            
        except Exception:
            return 0.0
    
    def _compare_optical_flow(self, data1: Dict, data2: Dict) -> float:
        """Compare optical flow features"""
        try:
            mag1 = data1.get('average_magnitude', 0)
            mag2 = data2.get('average_magnitude', 0)
            var1 = data1.get('average_direction_variance', 0)
            var2 = data2.get('average_direction_variance', 0)
            
            # Compare motion characteristics
            mag_diff = abs(mag1 - mag2)
            var_diff = abs(var1 - var2)
            
            # Normalize and calculate similarity
            mag_sim = 1.0 - min(1.0, mag_diff / max(1.0, max(mag1, mag2)))
            var_sim = 1.0 - min(1.0, var_diff / max(1.0, max(var1, var2)))
            
            return (mag_sim + var_sim) / 2.0
            
        except Exception:
            return 0.0
    
    def _compare_edge_detection(self, data1: Dict, data2: Dict) -> float:
        """Compare edge detection features"""
        try:
            density1 = data1.get('average_edge_density', 0)
            density2 = data2.get('average_edge_density', 0)
            orientation1 = np.array(data1.get('average_orientation', []))
            orientation2 = np.array(data2.get('average_orientation', []))
            
            # Compare edge density
            density_diff = abs(density1 - density2)
            density_sim = 1.0 - min(1.0, density_diff / max(0.1, max(density1, density2)))
            
            # Compare orientation histograms
            if len(orientation1) == len(orientation2) and len(orientation1) > 0:
                # Cosine similarity for orientation histograms
                dot_product = np.dot(orientation1, orientation2)
                norm1 = np.linalg.norm(orientation1)
                norm2 = np.linalg.norm(orientation2)
                
                if norm1 > 0 and norm2 > 0:
                    orientation_sim = dot_product / (norm1 * norm2)
                    orientation_sim = max(0.0, orientation_sim)
                else:
                    orientation_sim = 0.0
            else:
                orientation_sim = 0.0
            
            return (density_sim * 0.4 + orientation_sim * 0.6)
            
        except Exception:
            return 0.0
    
    async def batch_fingerprint(
        self, 
        video_paths: List[Union[str, Path]], 
        methods: List[str] = None
    ) -> List[Dict[str, any]]:
        """
        Process multiple video files in batch
        
        Args:
            video_paths: List of video file paths
            methods: Fingerprinting methods to use
        
        Returns:
            List of fingerprint data for each file
        """
        tasks = []
        for video_path in video_paths:
            task = self.extract_fingerprint(video_path, methods)
            tasks.append(task)
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and log errors
            fingerprints = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Error processing {video_paths[i]}: {str(result)}")
                    fingerprints.append({'error': str(result), 'file_path': str(video_paths[i])})
                else:
                    fingerprints.append(result)
            
            return fingerprints
            
        except Exception as e:
            logger.error(f"Error in batch video fingerprinting: {str(e)}")
            raise
    
    def get_engine_info(self) -> Dict[str, any]:
        """Get engine configuration and capabilities"""
        return {
            'engine': 'VideoFingerprintEngine',
            'version': '1.0.0',
            'frame_sampling_rate': self.frame_sampling_rate,
            'hash_size': self.hash_size,
            'max_frames': self.max_frames,
            'similarity_threshold': self.similarity_threshold,
            'supported_methods': ['perceptual_hash', 'histogram', 'optical_flow', 'edge_detection'],
            'supported_formats': ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv'],
            'capabilities': {
                'frame_extraction': True,
                'motion_analysis': True,
                'color_analysis': True,
                'edge_detection': True,
                'batch_processing': True,
                'similarity_matching': True
            }
        }
