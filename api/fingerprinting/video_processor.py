"""
IA Influencer Agent - Video Fingerprinting Processor
Author: Fahed Mlaiel <mlaiel@live.de>

AVERTISSEMENT LÉGAL STRICT:
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution non autorisée 
sans permission écrite expresse est strictement interdite et 
constituera une violation des droits d'auteur.

Advanced video fingerprinting processor for multi-format content protection
"""

import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
import hashlib
import logging
from PIL import Image
import imagehash

logger = logging.getLogger(__name__)

@dataclass
class VideoFingerprint:
    """Video fingerprint data structure"""
    content_hash: str
    frame_hashes: List[str]
    histogram_features: np.ndarray
    edge_features: np.ndarray
    motion_vectors: np.ndarray
    keyframes: List[int]
    duration: float
    fps: float
    resolution: Tuple[int, int]
    file_format: str
    metadata: Dict[str, Any]

class VideoFingerprintProcessor:
    """
    Professional video fingerprinting processor with advanced computer vision algorithms
    Handles multi-format video content protection and similarity detection
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize video fingerprinting processor"""
        self.config = config or self._get_default_config()
        self.executor = ThreadPoolExecutor(max_workers=2)
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for video processing"""
        return {
            'sample_frames': 30,
            'keyframe_threshold': 0.3,
            'resize_width': 320,
            'resize_height': 240,
            'similarity_threshold': 0.8,
            'hash_size': 16
        }
    
    async def process_video_file(self, file_path: Path) -> VideoFingerprint:
        """
        Process video file and generate comprehensive fingerprint
        
        Args:
            file_path: Path to video file
            
        Returns:
            VideoFingerprint object with extracted features
        """
        try:
            # Load video file asynchronously
            loop = asyncio.get_event_loop()
            
            video_info = await loop.run_in_executor(
                self.executor,
                self._extract_video_info,
                str(file_path)
            )
            
            # Extract frames and features in parallel
            frames_data = await loop.run_in_executor(
                self.executor,
                self._extract_frames,
                str(file_path)
            )
            
            frames, keyframes = frames_data
            
            # Generate content hash
            content_hash = self._generate_content_hash(frames)
            
            # Process features in parallel
            features = await asyncio.gather(
                self._extract_frame_hashes(frames),
                self._extract_histogram_features(frames),
                self._extract_edge_features(frames),
                self._extract_motion_vectors(frames)
            )
            
            frame_hashes, histogram_features, edge_features, motion_vectors = features
            
            # Create fingerprint
            fingerprint = VideoFingerprint(
                content_hash=content_hash,
                frame_hashes=frame_hashes,
                histogram_features=histogram_features,
                edge_features=edge_features,
                motion_vectors=motion_vectors,
                keyframes=keyframes,
                duration=video_info['duration'],
                fps=video_info['fps'],
                resolution=video_info['resolution'],
                file_format=file_path.suffix.lower(),
                metadata=self._extract_metadata(file_path)
            )
            
            logger.info(f"Video fingerprint generated for {file_path.name}")
            return fingerprint
            
        except Exception as e:
            logger.error(f"Error processing video file {file_path}: {str(e)}")
            raise
    
    def _extract_video_info(self, file_path: str) -> Dict[str, Any]:
        """Extract basic video information"""
        cap = cv2.VideoCapture(file_path)
        try:
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            duration = frame_count / fps if fps > 0 else 0
            
            return {
                'fps': fps,
                'frame_count': frame_count,
                'duration': duration,
                'resolution': (width, height)
            }
        finally:
            cap.release()
    
    def _extract_frames(self, file_path: str) -> Tuple[List[np.ndarray], List[int]]:
        """Extract sample frames and detect keyframes"""
        cap = cv2.VideoCapture(file_path)
        frames = []
        keyframes = []
        
        try:
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            sample_interval = max(1, frame_count // self.config['sample_frames'])
            
            prev_frame = None
            frame_idx = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_idx % sample_interval == 0:
                    # Resize frame for processing
                    frame_resized = cv2.resize(
                        frame,
                        (self.config['resize_width'], self.config['resize_height'])
                    )
                    frames.append(frame_resized)
                    
                    # Detect keyframes based on frame difference
                    if prev_frame is not None:
                        diff = cv2.absdiff(frame_resized, prev_frame)
                        diff_score = np.mean(diff) / 255.0
                        
                        if diff_score > self.config['keyframe_threshold']:
                            keyframes.append(len(frames) - 1)
                    
                    prev_frame = frame_resized.copy()
                
                frame_idx += 1
            
            return frames, keyframes
            
        finally:
            cap.release()
    
    def _generate_content_hash(self, frames: List[np.ndarray]) -> str:
        """Generate unique hash for video content"""
        if not frames:
            return ""
        
        # Combine representative frames
        combined_data = b""
        for i, frame in enumerate(frames[::max(1, len(frames) // 10)]):
            combined_data += frame.tobytes()
        
        return hashlib.sha256(combined_data).hexdigest()
    
    async def _extract_frame_hashes(self, frames: List[np.ndarray]) -> List[str]:
        """Extract perceptual hashes for each frame"""
        loop = asyncio.get_event_loop()
        
        def compute_hashes():
            hashes = []
            for frame in frames:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)
                
                # Generate perceptual hash
                phash = str(imagehash.phash(pil_image, hash_size=self.config['hash_size']))
                hashes.append(phash)
            
            return hashes
        
        return await loop.run_in_executor(self.executor, compute_hashes)
    
    async def _extract_histogram_features(self, frames: List[np.ndarray]) -> np.ndarray:
        """Extract color histogram features"""
        loop = asyncio.get_event_loop()
        
        def compute_histograms():
            histograms = []
            for frame in frames:
                # Calculate histogram for each channel
                hist_b = cv2.calcHist([frame], [0], None, [32], [0, 256])
                hist_g = cv2.calcHist([frame], [1], None, [32], [0, 256])
                hist_r = cv2.calcHist([frame], [2], None, [32], [0, 256])
                
                # Normalize and concatenate
                hist_combined = np.concatenate([
                    hist_b.flatten() / hist_b.sum(),
                    hist_g.flatten() / hist_g.sum(),
                    hist_r.flatten() / hist_r.sum()
                ])
                
                histograms.append(hist_combined)
            
            return np.array(histograms).mean(axis=0)
        
        return await loop.run_in_executor(self.executor, compute_histograms)
    
    async def _extract_edge_features(self, frames: List[np.ndarray]) -> np.ndarray:
        """Extract edge detection features"""
        loop = asyncio.get_event_loop()
        
        def compute_edges():
            edge_features = []
            for frame in frames:
                # Convert to grayscale
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Apply Canny edge detection
                edges = cv2.Canny(gray, 50, 150)
                
                # Calculate edge density and distribution
                edge_density = np.sum(edges > 0) / edges.size
                
                # Divide image into quadrants and calculate edge distribution
                h, w = edges.shape
                quadrants = [
                    edges[0:h//2, 0:w//2],
                    edges[0:h//2, w//2:w],
                    edges[h//2:h, 0:w//2],
                    edges[h//2:h, w//2:w]
                ]
                
                quadrant_densities = [
                    np.sum(q > 0) / q.size for q in quadrants
                ]
                
                feature_vector = [edge_density] + quadrant_densities
                edge_features.append(feature_vector)
            
            return np.array(edge_features).mean(axis=0)
        
        return await loop.run_in_executor(self.executor, compute_edges)
    
    async def _extract_motion_vectors(self, frames: List[np.ndarray]) -> np.ndarray:
        """Extract motion vector features"""
        loop = asyncio.get_event_loop()
        
        def compute_motion():
            if len(frames) < 2:
                return np.zeros(8)
            
            motion_vectors = []
            
            for i in range(1, len(frames)):
                prev_gray = cv2.cvtColor(frames[i-1], cv2.COLOR_BGR2GRAY)
                curr_gray = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
                
                # Calculate optical flow
                flow = cv2.calcOpticalFlowPyrLK(
                    prev_gray, curr_gray,
                    np.array([[50, 50], [150, 50], [50, 150], [150, 150]], dtype=np.float32).reshape(-1, 1, 2),
                    None
                )[0]
                
                if flow is not None and len(flow) > 0:
                    # Calculate motion statistics
                    motion_magnitude = np.linalg.norm(flow.reshape(-1, 2), axis=1)
                    motion_vectors.extend([
                        np.mean(motion_magnitude),
                        np.std(motion_magnitude),
                        np.max(motion_magnitude),
                        np.min(motion_magnitude)
                    ])
            
            if not motion_vectors:
                return np.zeros(8)
            
            # Return aggregated motion statistics
            vectors_array = np.array(motion_vectors).reshape(-1, 4)
            return vectors_array.mean(axis=0).tolist() + vectors_array.std(axis=0).tolist()
        
        return await loop.run_in_executor(self.executor, compute_motion)
    
    def _extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract file metadata"""
        return {
            'filename': file_path.name,
            'file_size': file_path.stat().st_size,
            'created_at': file_path.stat().st_ctime,
            'modified_at': file_path.stat().st_mtime
        }
    
    def calculate_similarity(self, fp1: VideoFingerprint, fp2: VideoFingerprint) -> float:
        """
        Calculate similarity score between two video fingerprints
        
        Args:
            fp1: First video fingerprint
            fp2: Second video fingerprint
            
        Returns:
            Similarity score between 0 and 1
        """
        try:
            # Content hash exact match
            if fp1.content_hash == fp2.content_hash:
                return 1.0
            
            # Frame hash similarity
            hash_similarity = self._calculate_hash_similarity(fp1.frame_hashes, fp2.frame_hashes)
            
            # Histogram similarity
            hist_similarity = self._cosine_similarity(fp1.histogram_features, fp2.histogram_features)
            
            # Edge features similarity
            edge_similarity = self._cosine_similarity(fp1.edge_features, fp2.edge_features)
            
            # Motion similarity
            motion_similarity = self._cosine_similarity(fp1.motion_vectors, fp2.motion_vectors)
            
            # Resolution and duration similarity
            resolution_similarity = self._resolution_similarity(fp1.resolution, fp2.resolution)
            duration_diff = abs(fp1.duration - fp2.duration) / max(fp1.duration, fp2.duration)
            duration_similarity = 1.0 - min(duration_diff, 1.0)
            
            # Weighted average
            weights = {
                'hash': 0.3,
                'histogram': 0.25,
                'edge': 0.2,
                'motion': 0.15,
                'resolution': 0.05,
                'duration': 0.05
            }
            
            similarity = (
                weights['hash'] * hash_similarity +
                weights['histogram'] * hist_similarity +
                weights['edge'] * edge_similarity +
                weights['motion'] * motion_similarity +
                weights['resolution'] * resolution_similarity +
                weights['duration'] * duration_similarity
            )
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0
    
    def _calculate_hash_similarity(self, hashes1: List[str], hashes2: List[str]) -> float:
        """Calculate similarity between frame hash sequences"""
        if not hashes1 or not hashes2:
            return 0.0
        
        # Dynamic time warping approach for hash sequence comparison
        max_matches = 0
        total_comparisons = 0
        
        for h1 in hashes1:
            for h2 in hashes2:
                # Calculate Hamming distance between hashes
                if len(h1) == len(h2):
                    hamming_distance = sum(c1 != c2 for c1, c2 in zip(h1, h2))
                    similarity = 1.0 - (hamming_distance / len(h1))
                    if similarity > 0.8:  # High similarity threshold for individual frames
                        max_matches += 1
                    total_comparisons += 1
        
        return max_matches / total_comparisons if total_comparisons > 0 else 0.0
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            if len(vec1) != len(vec2):
                return 0.0
                
            # Normalize vectors
            vec1_norm = vec1 / np.linalg.norm(vec1)
            vec2_norm = vec2 / np.linalg.norm(vec2)
            
            # Calculate cosine similarity
            similarity = np.dot(vec1_norm, vec2_norm)
            return float(np.clip(similarity, 0.0, 1.0))
            
        except Exception:
            return 0.0
    
    def _resolution_similarity(self, res1: Tuple[int, int], res2: Tuple[int, int]) -> float:
        """Calculate resolution similarity"""
        aspect_ratio_1 = res1[0] / res1[1] if res1[1] > 0 else 0
        aspect_ratio_2 = res2[0] / res2[1] if res2[1] > 0 else 0
        
        if aspect_ratio_1 == 0 or aspect_ratio_2 == 0:
            return 0.0
        
        ratio_diff = abs(aspect_ratio_1 - aspect_ratio_2) / max(aspect_ratio_1, aspect_ratio_2)
        return 1.0 - min(ratio_diff, 1.0)
    
    def is_duplicate(self, fp1: VideoFingerprint, fp2: VideoFingerprint) -> bool:
        """Check if two fingerprints represent duplicate content"""
        similarity = self.calculate_similarity(fp1, fp2)
        return similarity >= self.config['similarity_threshold']
    
    async def batch_process(self, file_paths: List[Path]) -> List[VideoFingerprint]:
        """Process multiple video files in parallel"""
        tasks = [self.process_video_file(path) for path in file_paths]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    def __del__(self):
        """Cleanup resources"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=True)
