"""Advanced Video Fingerprinting Engine
Uses OpenCV, pHash, YOLO frame analysis for video content identification

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All Rights Reserved - Unauthorized use prohibited
Team: Lead Dev IA + Backend Senior + ML Engineer + Video Processing Expert

WARNING: This code is proprietary and confidential. Any unauthorized copying,
distribution, modification or use is strictly prohibited and will be prosecuted
to the full extent of the law.
"""
import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
import hashlib
import imagehash
from PIL import Image
import logging
from dataclasses import dataclass
import torch
from ultralytics import YOLO
import subprocess
import json
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class VideoFingerprint:
    """Video fingerprint data structure"""    frame_hashes: List[str]
    perceptual_hash: str
    temporal_signature: str
    object_signatures: List[Dict]
    motion_vectors: np.ndarray
    duration: float
    fps: float
    resolution: Tuple[int, int]
    confidence_score: float


class VideoFingerprintEngine:
    """    Enterprise-grade video fingerprinting using multiple algorithms
    Combines frame hashing, YOLO object detection, and motion analysis
    """    
    def __init__(self, model_path: Optional[str] = None):
        self.yolo_model = None
        if model_path and Path(model_path).exists():
            try:
                self.yolo_model = YOLO(model_path)
            except Exception as e:
                logger.warning(f"Failed to load YOLO model: {e}")
                
    def extract_fingerprint(self, video_file_path: str, 
                           sample_rate: int = 1) -> VideoFingerprint:
        """Extract comprehensive video fingerprint from file"""        try:
            cap = cv2.VideoCapture(video_file_path)
            if not cap.isOpened():
                raise ValueError(f"Cannot open video file: {video_file_path}")
                
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Extract frame-based features
            frame_hashes = []
            motion_vectors = []
            object_signatures = []
            prev_frame = None
            
            frame_idx = 0
            frames_processed = 0
            
            while cap.isOpened() and frames_processed < 300:  # Limit processing
                ret, frame = cap.read()
                if not ret:
                    break
                    
                # Sample frames based on rate
                if frame_idx % sample_rate == 0:
                    # 1. Frame hash
                    frame_hash = self._compute_frame_hash(frame)
                    frame_hashes.append(frame_hash)
                    
                    # 2. Motion vectors (optical flow)
                    if prev_frame is not None:
                        motion = self._compute_motion_vector(prev_frame, frame)
                        motion_vectors.append(motion)
                        
                    # 3. Object detection signatures
                    if self.yolo_model:
                        objects = self._detect_objects(frame)
                        if objects:
                            object_signatures.append({
                                'frame_idx': frame_idx,
                                'objects': objects
                            })
                            
                    prev_frame = frame.copy()
                    frames_processed += 1
                    
                frame_idx += 1
                
            cap.release()
            
            # 4. Perceptual hash of representative frames
            perceptual_hash = self._compute_perceptual_hash(frame_hashes)
            
            # 5. Temporal signature
            temporal_signature = self._compute_temporal_signature(motion_vectors)
            
            # 6. Confidence score
            confidence_score = self._calculate_confidence(
                frames_processed, duration, len(object_signatures)
            )
            
            return VideoFingerprint(
                frame_hashes=frame_hashes,
                perceptual_hash=perceptual_hash,
                temporal_signature=temporal_signature,
                object_signatures=object_signatures,
                motion_vectors=np.array(motion_vectors) if motion_vectors else np.array([]),
                duration=duration,
                fps=fps,
                resolution=(width, height),
                confidence_score=confidence_score
            )
            
        except Exception as e:
            logger.error(f"Error extracting video fingerprint: {str(e)}")
            raise
            
    def _compute_frame_hash(self, frame: np.ndarray) -> str:
        """Compute hash for a single frame"""        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Resize to standard size for comparison
            resized = cv2.resize(gray, (64, 64))
            
            # Convert to PIL Image for imagehash
            pil_image = Image.fromarray(resized)
            
            # Compute perceptual hash
            hash_value = imagehash.phash(pil_image, hash_size=8)
            
            return str(hash_value)
            
        except Exception as e:
            logger.warning(f"Frame hash computation failed: {str(e)}")
            return ""
            
    def _compute_motion_vector(self, prev_frame: np.ndarray, 
                             curr_frame: np.ndarray) -> float:
        """Compute motion vector between two frames"""        try:
            # Convert to grayscale
            prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
            curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
            
            # Calculate optical flow
            flow = cv2.calcOpticalFlowPyrLK(
                prev_gray, curr_gray, 
                corners=cv2.goodFeaturesToTrack(prev_gray, maxCorners=100, 
                                              qualityLevel=0.3, minDistance=7),
                nextPts=None
            )[0]
            
            if flow is not None and len(flow) > 0:
                # Calculate average motion magnitude
                motion_magnitude = np.mean(np.sqrt(
                    flow[:, 0] ** 2 + flow[:, 1] ** 2
                ))
                return float(motion_magnitude)
                
            return 0.0
            
        except Exception as e:
            logger.warning(f"Motion vector computation failed: {str(e)}")
            return 0.0
            
    def _detect_objects(self, frame: np.ndarray) -> List[Dict]:
        """Detect objects in frame using YOLO"""        try:
            if not self.yolo_model:
                return []
                
            # Run inference
            results = self.yolo_model(frame, verbose=False)
            
            objects = []
            for result in results:
                if result.boxes is not None:
                    for box in result.boxes:
                        objects.append({
                            'class_id': int(box.cls[0]),
                            'confidence': float(box.conf[0]),
                            'bbox': box.xyxy[0].tolist()
                        })
                        
            return objects
            
        except Exception as e:
            logger.warning(f"Object detection failed: {str(e)}")
            return []
            
    def _compute_perceptual_hash(self, frame_hashes: List[str]) -> str:
        """Compute overall perceptual hash from frame hashes"""        try:
            if not frame_hashes:
                return ""
                
            # Sample representative frames
            sample_size = min(10, len(frame_hashes))
            sampled_hashes = frame_hashes[::len(frame_hashes)//sample_size][:sample_size]
            
            # Combine hashes
            combined = ''.join(sampled_hashes)
            
            # Create final hash
            return hashlib.md5(combined.encode()).hexdigest()
            
        except Exception:
            return ""
            
    def _compute_temporal_signature(self, motion_vectors: List[float]) -> str:
        """Compute temporal signature from motion vectors"""        try:
            if not motion_vectors:
                return ""
                
            # Statistical features of motion
            motion_array = np.array(motion_vectors)
            
            features = [
                np.mean(motion_array),
                np.std(motion_array),
                np.max(motion_array),
                np.min(motion_array),
                len(motion_vectors)
            ]
            
            # Create signature string
            signature_str = ''.join([f"{x:.4f}" for x in features])
            
            return hashlib.md5(signature_str.encode()).hexdigest()
            
        except Exception:
            return ""
            
    def _calculate_confidence(self, frames_processed: int, duration: float, 
                            object_count: int) -> float:
        """Calculate confidence score based on video quality metrics"""        try:
            # Frame coverage (more frames = better confidence)
            frame_score = min(1.0, frames_processed / 100.0)
            
            # Duration score (longer videos = better confidence)
            duration_score = min(1.0, duration / 60.0)  # Up to 1 minute
            
            # Object detection score
            object_score = min(1.0, object_count / 50.0)  # Up to 50 objects
            
            # Weighted combination
            confidence = (frame_score * 0.4 + 
                         duration_score * 0.3 + 
                         object_score * 0.3)
            
            return max(0.1, confidence)  # Minimum confidence
            
        except Exception:
            return 0.5
            
    def compare_fingerprints(self, fp1: VideoFingerprint, 
                           fp2: VideoFingerprint) -> float:
        """Compare two video fingerprints and return similarity score (0-1)"""        try:
            scores = []
            
            # 1. Perceptual hash similarity
            if fp1.perceptual_hash and fp2.perceptual_hash:
                perceptual_sim = 1.0 if fp1.perceptual_hash == fp2.perceptual_hash else 0.0
                scores.append(perceptual_sim * 0.3)
                
            # 2. Temporal signature similarity
            if fp1.temporal_signature and fp2.temporal_signature:
                temporal_sim = 1.0 if fp1.temporal_signature == fp2.temporal_signature else 0.0
                scores.append(temporal_sim * 0.2)
                
            # 3. Frame hash similarity
            frame_sim = self._compare_frame_hashes(fp1.frame_hashes, fp2.frame_hashes)
            scores.append(frame_sim * 0.3)
            
            # 4. Motion similarity
            motion_sim = self._compare_motion_vectors(fp1.motion_vectors, fp2.motion_vectors)
            scores.append(motion_sim * 0.1)
            
            # 5. Object similarity
            object_sim = self._compare_object_signatures(fp1.object_signatures, fp2.object_signatures)
            scores.append(object_sim * 0.1)
            
            # Weighted average
            total_similarity = sum(scores) if scores else 0.0
            
            # Apply confidence weighting
            confidence_factor = (fp1.confidence_score + fp2.confidence_score) / 2
            
            return total_similarity * confidence_factor
            
        except Exception as e:
            logger.error(f"Error comparing video fingerprints: {str(e)}")
            return 0.0
            
    def _compare_frame_hashes(self, hashes1: List[str], hashes2: List[str]) -> float:
        """Compare frame hash sequences"""        try:
            if not hashes1 or not hashes2:
                return 0.0
                
            # Sample frames for comparison
            sample_size = min(20, len(hashes1), len(hashes2))
            
            sampled1 = hashes1[::len(hashes1)//sample_size][:sample_size]
            sampled2 = hashes2[::len(hashes2)//sample_size][:sample_size]
            
            # Count matches
            matches = sum(1 for h1, h2 in zip(sampled1, sampled2) if h1 == h2)
            
            return matches / max(len(sampled1), 1)
            
        except Exception:
            return 0.0
            
    def _compare_motion_vectors(self, motion1: np.ndarray, motion2: np.ndarray) -> float:
        """Compare motion vector patterns"""        try:
            if len(motion1) == 0 or len(motion2) == 0:
                return 0.0
                
            # Statistical comparison
            stats1 = [np.mean(motion1), np.std(motion1)]
            stats2 = [np.mean(motion2), np.std(motion2)]
            
            # Normalized difference
            diff = np.abs(np.array(stats1) - np.array(stats2))
            normalized_diff = diff / (np.array(stats1) + np.array(stats2) + 1e-8)
            
            similarity = 1.0 - np.mean(normalized_diff)
            
            return max(0.0, similarity)
            
        except Exception:
            return 0.0
            
    def _compare_object_signatures(self, objects1: List[Dict], objects2: List[Dict]) -> float:
        """Compare object detection signatures"""        try:
            if not objects1 or not objects2:
                return 0.0 if not objects1 and not objects2 else 0.0
                
            # Extract class distributions
            classes1 = [obj['class_id'] for frame in objects1 for obj in frame.get('objects', [])]
            classes2 = [obj['class_id'] for frame in objects2 for obj in frame.get('objects', [])]
            
            if not classes1 or not classes2:
                return 0.0
                
            # Create class histograms
            all_classes = set(classes1 + classes2)
            hist1 = [classes1.count(cls) for cls in all_classes]
            hist2 = [classes2.count(cls) for cls in all_classes]
            
            # Cosine similarity
            dot_product = sum(h1 * h2 for h1, h2 in zip(hist1, hist2))
            norm1 = sum(h ** 2 for h in hist1) ** 0.5
            norm2 = sum(h ** 2 for h in hist2) ** 0.5
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
                
            return dot_product / (norm1 * norm2)
            
        except Exception:
            return 0.0
            
    def batch_extract_fingerprints(self, video_files: List[str]) -> Dict[str, VideoFingerprint]:
        """Extract fingerprints from multiple video files"""        fingerprints = {}
        
        for video_file in video_files:
            try:
                fp = self.extract_fingerprint(video_file)
                fingerprints[video_file] = fp
                logger.info(f"Successfully extracted fingerprint for: {video_file}")
            except Exception as e:
                logger.error(f"Failed to extract fingerprint for {video_file}: {str(e)}")
                
        return fingerprints
        
    def find_similar_videos(self, target_fingerprint: VideoFingerprint,
                          candidate_fingerprints: Dict[str, VideoFingerprint],
                          threshold: float = 0.8) -> List[Tuple[str, float]]:
        """Find similar video files above threshold"""        similar_files = []
        
        for file_path, candidate_fp in candidate_fingerprints.items():
            similarity = self.compare_fingerprints(target_fingerprint, candidate_fp)
            
            if similarity >= threshold:
                similar_files.append((file_path, similarity))
                
        # Sort by similarity score (descending)
        similar_files.sort(key=lambda x: x[1], reverse=True)
        
        return similar_files
