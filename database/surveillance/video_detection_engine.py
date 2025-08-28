"""
Video Detection Engine Module
============================

Advanced video fingerprinting and detection engine for visual content surveillance.
Implements state-of-the-art computer vision and video analysis algorithms.

Author: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All Rights Reserved.

WARNING: This code and concept are protected intellectual property.
Any unauthorized use, copying, or distribution without explicit written 
permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.
"""

import asyncio
import logging
import numpy as np
import cv2
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import chromadb
from scipy.spatial.distance import cosine, euclidean
from dataclasses import dataclass
import io
import hashlib
import json
import base64
from PIL import Image
import imagehash

logger = logging.getLogger(__name__)


@dataclass
class VideoFingerprint:
    """Video fingerprint data structure."""
    fingerprint_id: str
    user_id: str
    title: str
    duration: float
    frame_rate: float
    resolution: Tuple[int, int]
    visual_features: Dict[str, Any]
    audio_features: Optional[Dict[str, Any]]
    hash_signature: str
    keyframe_hashes: List[str]
    created_at: datetime
    metadata: Dict[str, Any]


@dataclass
class VideoMatch:
    """Video match result structure."""
    original_fingerprint_id: str
    detected_url: str
    similarity_score: float
    confidence_level: float
    time_segments: List[Tuple[float, float]]  # Start, end times of matching segments
    visual_similarity: float
    audio_similarity: Optional[float]
    platform: str
    detected_at: datetime
    match_details: Dict[str, Any]


class VideoFeatureExtractor:
    """Advanced video feature extraction for fingerprinting."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.keyframe_interval = config.get("keyframe_interval", 1.0)  # Extract keyframes every 1 second
        self.max_keyframes = config.get("max_keyframes", 100)
        self.frame_resize = config.get("frame_resize", (224, 224))
        self.color_histogram_bins = config.get("color_histogram_bins", 32)
        
        # Initialize feature extractors
        self.orb_detector = cv2.ORB_create(nfeatures=500)
        self.sift_detector = cv2.SIFT_create(nfeatures=100)
        
    async def extract_features(self, video_data: bytes) -> Dict[str, Any]:
        """Extract comprehensive video features from video data."""
        try:
            # Save video data to temporary file for OpenCV processing
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
                temp_file.write(video_data)
                temp_file.flush()
                video_path = temp_file.name
            
            # Open video with OpenCV
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise ValueError("Could not open video file")
            
            # Get video properties
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            duration = frame_count / fps if fps > 0 else 0
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            features = {
                "duration": duration,
                "frame_rate": fps,
                "resolution": (width, height),
                "frame_count": frame_count
            }
            
            # Extract keyframes and features
            keyframes = await self._extract_keyframes(cap, fps, duration)
            features["keyframes"] = keyframes
            
            # Visual features from keyframes
            visual_features = await self._extract_visual_features(keyframes)
            features.update(visual_features)
            
            # Temporal features
            temporal_features = await self._extract_temporal_features(keyframes)
            features.update(temporal_features)
            
            # Color analysis
            color_features = await self._extract_color_features(keyframes)
            features.update(color_features)
            
            # Motion analysis
            motion_features = await self._extract_motion_features(cap, fps)
            features.update(motion_features)
            
            cap.release()
            
            # Clean up temporary file
            import os
            os.unlink(video_path)
            
            logger.info(f"Extracted video features: {len(features)} feature sets")
            return features
            
        except Exception as e:
            logger.error(f"Video feature extraction failed: {e}")
            raise
    
    async def _extract_keyframes(self, cap, fps: float, duration: float) -> List[np.ndarray]:
        """Extract keyframes from video at regular intervals."""
        keyframes = []
        
        frame_interval = int(fps * self.keyframe_interval)
        frame_indices = range(0, int(fps * duration), frame_interval)
        
        for frame_idx in frame_indices[:self.max_keyframes]:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            
            if ret:
                # Resize frame for processing
                frame_resized = cv2.resize(frame, self.frame_resize)
                keyframes.append(frame_resized)
        
        return keyframes
    
    async def _extract_visual_features(self, keyframes: List[np.ndarray]) -> Dict[str, Any]:
        """Extract visual features from keyframes."""
        features = {}
        
        # ORB features (keypoint detection)
        orb_descriptors = []
        orb_keypoints_count = []
        
        # SIFT features (scale-invariant feature transform)
        sift_descriptors = []
        sift_keypoints_count = []
        
        # Perceptual hashes
        perceptual_hashes = []
        
        for frame in keyframes:
            # Convert to grayscale
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # ORB features
            orb_kp, orb_desc = self.orb_detector.detectAndCompute(gray_frame, None)
            if orb_desc is not None:
                orb_descriptors.append(orb_desc)
            orb_keypoints_count.append(len(orb_kp) if orb_kp else 0)
            
            # SIFT features
            sift_kp, sift_desc = self.sift_detector.detectAndCompute(gray_frame, None)
            if sift_desc is not None:
                sift_descriptors.append(sift_desc)
            sift_keypoints_count.append(len(sift_kp) if sift_kp else 0)
            
            # Perceptual hash
            pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            phash = str(imagehash.phash(pil_image))
            perceptual_hashes.append(phash)
        
        features["orb_keypoints_count"] = orb_keypoints_count
        features["sift_keypoints_count"] = sift_keypoints_count
        features["perceptual_hashes"] = perceptual_hashes
        
        # Aggregate ORB descriptors
        if orb_descriptors:
            all_orb_desc = np.vstack(orb_descriptors)
            features["orb_descriptor_mean"] = np.mean(all_orb_desc, axis=0)
            features["orb_descriptor_std"] = np.std(all_orb_desc, axis=0)
        
        # Aggregate SIFT descriptors
        if sift_descriptors:
            all_sift_desc = np.vstack(sift_descriptors)
            features["sift_descriptor_mean"] = np.mean(all_sift_desc, axis=0)
            features["sift_descriptor_std"] = np.std(all_sift_desc, axis=0)
        
        return features
    
    async def _extract_temporal_features(self, keyframes: List[np.ndarray]) -> Dict[str, Any]:
        """Extract temporal features analyzing changes between frames."""
        features = {}
        
        if len(keyframes) < 2:
            return features
        
        # Frame difference analysis
        frame_differences = []
        for i in range(1, len(keyframes)):
            diff = cv2.absdiff(
                cv2.cvtColor(keyframes[i-1], cv2.COLOR_BGR2GRAY),
                cv2.cvtColor(keyframes[i], cv2.COLOR_BGR2GRAY)
            )
            frame_differences.append(np.mean(diff))
        
        features["frame_difference_mean"] = np.mean(frame_differences)
        features["frame_difference_std"] = np.std(frame_differences)
        features["scene_change_intensity"] = np.max(frame_differences)
        
        # Optical flow estimation (simplified)
        optical_flow_magnitudes = []
        for i in range(1, len(keyframes)):
            prev_gray = cv2.cvtColor(keyframes[i-1], cv2.COLOR_BGR2GRAY)
            curr_gray = cv2.cvtColor(keyframes[i], cv2.COLOR_BGR2GRAY)
            
            # Calculate dense optical flow
            flow = cv2.calcOpticalFlowPyrLK(
                prev_gray, curr_gray,
                np.array([[100, 100]], dtype=np.float32),
                None
            )[0]
            
            if flow is not None:
                magnitude = np.linalg.norm(flow)
                optical_flow_magnitudes.append(magnitude)
        
        if optical_flow_magnitudes:
            features["optical_flow_mean"] = np.mean(optical_flow_magnitudes)
            features["optical_flow_std"] = np.std(optical_flow_magnitudes)
        
        return features
    
    async def _extract_color_features(self, keyframes: List[np.ndarray]) -> Dict[str, Any]:
        """Extract color-based features from keyframes."""
        features = {}
        
        # Color histograms
        color_histograms = {"blue": [], "green": [], "red": []}
        brightness_values = []
        saturation_values = []
        
        for frame in keyframes:
            # RGB histograms
            for i, color in enumerate(["blue", "green", "red"]):
                hist = cv2.calcHist([frame], [i], None, [self.color_histogram_bins], [0, 256])
                color_histograms[color].append(hist.flatten())
            
            # Brightness analysis
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            brightness_values.append(np.mean(gray))
            
            # Saturation analysis
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            saturation_values.append(np.mean(hsv[:, :, 1]))
        
        # Aggregate color features
        for color in ["blue", "green", "red"]:
            if color_histograms[color]:
                features[f"{color}_histogram_mean"] = np.mean(color_histograms[color], axis=0)
                features[f"{color}_histogram_std"] = np.std(color_histograms[color], axis=0)
        
        features["brightness_mean"] = np.mean(brightness_values)
        features["brightness_std"] = np.std(brightness_values)
        features["saturation_mean"] = np.mean(saturation_values)
        features["saturation_std"] = np.std(saturation_values)
        
        return features
    
    async def _extract_motion_features(self, cap, fps: float) -> Dict[str, Any]:
        """Extract motion-based features from video."""
        features = {}
        
        # Reset video capture
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        
        # Sample frames for motion analysis
        motion_vectors = []
        prev_frame = None
        
        frame_count = 0
        max_frames_for_motion = 50  # Limit for performance
        
        while frame_count < max_frames_for_motion:
            ret, frame = cap.read()
            if not ret:
                break
            
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray_frame = cv2.resize(gray_frame, (320, 240))  # Resize for performance
            
            if prev_frame is not None:
                # Calculate optical flow
                flow = cv2.calcOpticalFlowPyrLK(
                    prev_frame, gray_frame,
                    np.array([[160, 120]], dtype=np.float32),  # Center point
                    None
                )[0]
                
                if flow is not None:
                    motion_magnitude = np.linalg.norm(flow)
                    motion_vectors.append(motion_magnitude)
            
            prev_frame = gray_frame
            frame_count += 1
        
        if motion_vectors:
            features["motion_intensity_mean"] = np.mean(motion_vectors)
            features["motion_intensity_std"] = np.std(motion_vectors)
            features["motion_intensity_max"] = np.max(motion_vectors)
            features["motion_activity_level"] = len([m for m in motion_vectors if m > np.mean(motion_vectors)]) / len(motion_vectors)
        
        return features


class VideoSimilarityCalculator:
    """Advanced video similarity calculation engine."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.feature_weights = config.get("feature_weights", {
            "visual": 0.4,
            "temporal": 0.2,
            "color": 0.2,
            "motion": 0.2
        })
        
    async def calculate_similarity(
        self, 
        features1: Dict[str, Any], 
        features2: Dict[str, Any]
    ) -> Tuple[float, Dict[str, float]]:
        """Calculate comprehensive similarity between two video feature sets."""
        try:
            similarities = {}
            weighted_sum = 0.0
            total_weight = 0.0
            
            # Visual similarity (ORB and SIFT descriptors)
            visual_sim = await self._calculate_visual_similarity(features1, features2)
            if visual_sim is not None:
                similarities["visual"] = visual_sim
                weighted_sum += visual_sim * self.feature_weights.get("visual", 0.4)
                total_weight += self.feature_weights.get("visual", 0.4)
            
            # Temporal similarity
            temporal_sim = await self._calculate_temporal_similarity(features1, features2)
            if temporal_sim is not None:
                similarities["temporal"] = temporal_sim
                weighted_sum += temporal_sim * self.feature_weights.get("temporal", 0.2)
                total_weight += self.feature_weights.get("temporal", 0.2)
            
            # Color similarity
            color_sim = await self._calculate_color_similarity(features1, features2)
            if color_sim is not None:
                similarities["color"] = color_sim
                weighted_sum += color_sim * self.feature_weights.get("color", 0.2)
                total_weight += self.feature_weights.get("color", 0.2)
            
            # Motion similarity
            motion_sim = await self._calculate_motion_similarity(features1, features2)
            if motion_sim is not None:
                similarities["motion"] = motion_sim
                weighted_sum += motion_sim * self.feature_weights.get("motion", 0.2)
                total_weight += self.feature_weights.get("motion", 0.2)
            
            # Calculate overall similarity
            overall_similarity = weighted_sum / total_weight if total_weight > 0 else 0.0
            
            logger.debug(f"Video similarity calculated: {overall_similarity:.4f}")
            return overall_similarity, similarities
            
        except Exception as e:
            logger.error(f"Video similarity calculation failed: {e}")
            return 0.0, {}
    
    async def _calculate_visual_similarity(self, features1: Dict[str, Any], features2: Dict[str, Any]) -> Optional[float]:
        """Calculate visual similarity using ORB and SIFT descriptors."""
        try:
            visual_similarities = []
            
            # ORB descriptor similarity
            if "orb_descriptor_mean" in features1 and "orb_descriptor_mean" in features2:
                orb_sim = 1 - cosine(features1["orb_descriptor_mean"], features2["orb_descriptor_mean"])
                visual_similarities.append(max(0, orb_sim))
            
            # SIFT descriptor similarity
            if "sift_descriptor_mean" in features1 and "sift_descriptor_mean" in features2:
                sift_sim = 1 - cosine(features1["sift_descriptor_mean"], features2["sift_descriptor_mean"])
                visual_similarities.append(max(0, sift_sim))
            
            # Perceptual hash similarity
            if "perceptual_hashes" in features1 and "perceptual_hashes" in features2:
                hash_similarities = []
                for h1 in features1["perceptual_hashes"]:
                    for h2 in features2["perceptual_hashes"]:
                        # Calculate Hamming distance
                        hamming_dist = sum(c1 != c2 for c1, c2 in zip(h1, h2))
                        hash_sim = 1 - (hamming_dist / len(h1))
                        hash_similarities.append(hash_sim)
                
                if hash_similarities:
                    visual_similarities.append(max(hash_similarities))
            
            return np.mean(visual_similarities) if visual_similarities else None
            
        except Exception as e:
            logger.error(f"Visual similarity calculation failed: {e}")
            return None
    
    async def _calculate_temporal_similarity(self, features1: Dict[str, Any], features2: Dict[str, Any]) -> Optional[float]:
        """Calculate temporal similarity using frame difference patterns."""
        try:
            temporal_similarities = []
            
            # Frame difference similarity
            if "frame_difference_mean" in features1 and "frame_difference_mean" in features2:
                diff_sim = 1 - abs(features1["frame_difference_mean"] - features2["frame_difference_mean"]) / 255
                temporal_similarities.append(max(0, diff_sim))
            
            # Optical flow similarity
            if "optical_flow_mean" in features1 and "optical_flow_mean" in features2:
                flow_diff = abs(features1["optical_flow_mean"] - features2["optical_flow_mean"])
                flow_sim = 1 / (1 + flow_diff)
                temporal_similarities.append(flow_sim)
            
            return np.mean(temporal_similarities) if temporal_similarities else None
            
        except Exception as e:
            logger.error(f"Temporal similarity calculation failed: {e}")
            return None
    
    async def _calculate_color_similarity(self, features1: Dict[str, Any], features2: Dict[str, Any]) -> Optional[float]:
        """Calculate color similarity using histograms and color statistics."""
        try:
            color_similarities = []
            
            # Color histogram similarities
            for color in ["blue", "green", "red"]:
                hist_key = f"{color}_histogram_mean"
                if hist_key in features1 and hist_key in features2:
                    hist_sim = 1 - cosine(features1[hist_key], features2[hist_key])
                    color_similarities.append(max(0, hist_sim))
            
            # Brightness similarity
            if "brightness_mean" in features1 and "brightness_mean" in features2:
                brightness_diff = abs(features1["brightness_mean"] - features2["brightness_mean"])
                brightness_sim = 1 - (brightness_diff / 255)
                color_similarities.append(max(0, brightness_sim))
            
            # Saturation similarity
            if "saturation_mean" in features1 and "saturation_mean" in features2:
                saturation_diff = abs(features1["saturation_mean"] - features2["saturation_mean"])
                saturation_sim = 1 - (saturation_diff / 255)
                color_similarities.append(max(0, saturation_sim))
            
            return np.mean(color_similarities) if color_similarities else None
            
        except Exception as e:
            logger.error(f"Color similarity calculation failed: {e}")
            return None
    
    async def _calculate_motion_similarity(self, features1: Dict[str, Any], features2: Dict[str, Any]) -> Optional[float]:
        """Calculate motion similarity using motion intensity patterns."""
        try:
            motion_similarities = []
            
            # Motion intensity similarity
            if "motion_intensity_mean" in features1 and "motion_intensity_mean" in features2:
                motion_diff = abs(features1["motion_intensity_mean"] - features2["motion_intensity_mean"])
                motion_sim = 1 / (1 + motion_diff)
                motion_similarities.append(motion_sim)
            
            # Motion activity level similarity
            if "motion_activity_level" in features1 and "motion_activity_level" in features2:
                activity_diff = abs(features1["motion_activity_level"] - features2["motion_activity_level"])
                activity_sim = 1 - activity_diff
                motion_similarities.append(max(0, activity_sim))
            
            return np.mean(motion_similarities) if motion_similarities else None
            
        except Exception as e:
            logger.error(f"Motion similarity calculation failed: {e}")
            return None


class VideoDetectionEngine:
    """
    Advanced video detection engine for content surveillance.
    
    Implements sophisticated video fingerprinting, matching, and detection
    algorithms for protecting visual content across platforms.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.feature_extractor = VideoFeatureExtractor(config.get("feature_extraction", {}))
        self.similarity_calculator = VideoSimilarityCalculator(config.get("similarity", {}))
        
        # ChromaDB vector store for fast similarity search
        self.chroma_client = None
        self.fingerprint_collection = None
        
        # Detection thresholds
        self.similarity_threshold = config.get("similarity_threshold", 0.75)
        self.confidence_threshold = config.get("confidence_threshold", 0.7)
        
        # Performance metrics
        self.detection_stats = {
            "total_fingerprints": 0,
            "total_detections": 0,
            "false_positives": 0,
            "processing_time_avg": 0.0
        }
        
    async def initialize(self) -> bool:
        """Initialize the video detection engine."""
        try:
            # Initialize ChromaDB client
            self.chroma_client = chromadb.Client()
            
            # Get or create fingerprint collection
            try:
                self.fingerprint_collection = self.chroma_client.get_collection(
                    name="video_fingerprints"
                )
            except:
                self.fingerprint_collection = self.chroma_client.create_collection(
                    name="video_fingerprints",
                    metadata={"description": "Video fingerprint collection for content protection"}
                )
            
            logger.info("VideoDetectionEngine initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize VideoDetectionEngine: {e}")
            return False
    
    async def create_fingerprint(
        self, 
        video_data: bytes, 
        metadata: Dict[str, Any]
    ) -> VideoFingerprint:
        """Create video fingerprint from video data."""
        try:
            start_time = datetime.utcnow()
            
            # Extract video features
            features = await self.feature_extractor.extract_features(video_data)
            
            # Create hash signature
            feature_string = json.dumps({
                k: v.tolist() if isinstance(v, np.ndarray) else v 
                for k, v in features.items() 
                if not k == "keyframes" and not isinstance(v, list)
            }, sort_keys=True)
            hash_signature = hashlib.sha256(feature_string.encode()).hexdigest()
            
            # Extract keyframe hashes
            keyframe_hashes = features.get("perceptual_hashes", [])
            
            # Create fingerprint object
            fingerprint = VideoFingerprint(
                fingerprint_id=hashlib.sha256(f"{metadata.get('user_id', '')}{hash_signature}{start_time.isoformat()}".encode()).hexdigest(),
                user_id=metadata.get("user_id", ""),
                title=metadata.get("title", ""),
                duration=features.get("duration", 0.0),
                frame_rate=features.get("frame_rate", 0.0),
                resolution=features.get("resolution", (0, 0)),
                visual_features=features,
                audio_features=metadata.get("audio_features"),
                hash_signature=hash_signature,
                keyframe_hashes=keyframe_hashes,
                created_at=start_time,
                metadata=metadata
            )
            
            # Store in vector database
            await self._store_fingerprint(fingerprint)
            
            self.detection_stats["total_fingerprints"] += 1
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"Video fingerprint created in {processing_time:.2f}s: {fingerprint.fingerprint_id}")
            
            return fingerprint
            
        except Exception as e:
            logger.error(f"Video fingerprint creation failed: {e}")
            raise
    
    async def _store_fingerprint(self, fingerprint: VideoFingerprint) -> None:
        """Store fingerprint in vector database."""
        try:
            # Create embedding vector from key features
            embedding_features = []
            
            if "orb_descriptor_mean" in fingerprint.visual_features:
                embedding_features.extend(fingerprint.visual_features["orb_descriptor_mean"].tolist())
            
            if "blue_histogram_mean" in fingerprint.visual_features:
                embedding_features.extend(fingerprint.visual_features["blue_histogram_mean"].tolist())
                embedding_features.extend(fingerprint.visual_features["green_histogram_mean"].tolist())
                embedding_features.extend(fingerprint.visual_features["red_histogram_mean"].tolist())
            
            # Pad or truncate to fixed size (512 dimensions)
            target_size = 512
            if len(embedding_features) < target_size:
                embedding_features.extend([0.0] * (target_size - len(embedding_features)))
            else:
                embedding_features = embedding_features[:target_size]
            
            # Store in ChromaDB
            self.fingerprint_collection.add(
                embeddings=[embedding_features],
                documents=[json.dumps({
                    "title": fingerprint.title,
                    "duration": fingerprint.duration,
                    "frame_rate": fingerprint.frame_rate,
                    "resolution": fingerprint.resolution,
                    "hash_signature": fingerprint.hash_signature
                })],
                metadatas=[{
                    "fingerprint_id": fingerprint.fingerprint_id,
                    "user_id": fingerprint.user_id,
                    "created_at": fingerprint.created_at.isoformat()
                }],
                ids=[fingerprint.fingerprint_id]
            )
            
            logger.debug(f"Video fingerprint stored in vector database: {fingerprint.fingerprint_id}")
            
        except Exception as e:
            logger.error(f"Failed to store video fingerprint: {e}")
            raise
    
    async def detect_matches(
        self, 
        video_data: bytes, 
        detection_metadata: Dict[str, Any]
    ) -> List[VideoMatch]:
        """Detect video matches against stored fingerprints."""
        try:
            start_time = datetime.utcnow()
            
            # Extract features from input video
            input_features = await self.feature_extractor.extract_features(video_data)
            
            # Create embedding for similarity search
            embedding_features = []
            if "orb_descriptor_mean" in input_features:
                embedding_features.extend(input_features["orb_descriptor_mean"].tolist())
            
            if "blue_histogram_mean" in input_features:
                embedding_features.extend(input_features["blue_histogram_mean"].tolist())
                embedding_features.extend(input_features["green_histogram_mean"].tolist())
                embedding_features.extend(input_features["red_histogram_mean"].tolist())
            
            # Pad or truncate to fixed size
            target_size = 512
            if len(embedding_features) < target_size:
                embedding_features.extend([0.0] * (target_size - len(embedding_features)))
            else:
                embedding_features = embedding_features[:target_size]
            
            # Search for similar fingerprints
            search_results = self.fingerprint_collection.query(
                query_embeddings=[embedding_features],
                n_results=15,  # Get top 15 candidates
                include=["documents", "metadatas", "distances"]
            )
            
            matches = []
            
            # Process search results
            if search_results['ids'][0]:
                for i, fingerprint_id in enumerate(search_results['ids'][0]):
                    distance = search_results['distances'][0][i]
                    metadata = search_results['metadatas'][0][i]
                    
                    # Convert distance to similarity score
                    initial_similarity = max(0, 1 - distance)
                    
                    # Skip if initial similarity is too low
                    if initial_similarity < self.similarity_threshold * 0.7:
                        continue
                    
                    # Load full fingerprint for detailed comparison
                    stored_fingerprint = await self._load_fingerprint(fingerprint_id)
                    if not stored_fingerprint:
                        continue
                    
                    # Calculate detailed similarity
                    detailed_similarity, feature_similarities = await self.similarity_calculator.calculate_similarity(
                        input_features, stored_fingerprint.visual_features
                    )
                    
                    # Check if similarity meets threshold
                    if detailed_similarity >= self.similarity_threshold:
                        confidence = self._calculate_confidence(
                            detailed_similarity, 
                            feature_similarities,
                            input_features,
                            stored_fingerprint.visual_features
                        )
                        
                        if confidence >= self.confidence_threshold:
                            # Analyze time segments (simplified)
                            time_segments = [(0.0, min(
                                input_features.get("duration", 0.0),
                                stored_fingerprint.duration
                            ))]
                            
                            match = VideoMatch(
                                original_fingerprint_id=fingerprint_id,
                                detected_url=detection_metadata.get("url", ""),
                                similarity_score=detailed_similarity,
                                confidence_level=confidence,
                                time_segments=time_segments,
                                visual_similarity=detailed_similarity,
                                audio_similarity=self._calculate_audio_similarity(
                                    detection_video_features, 
                                    stored_fingerprint.features
                                ),  # Audio comparison implementation
                                platform=detection_metadata.get("platform", ""),
                                detected_at=datetime.utcnow(),
                                match_details=feature_similarities
                            )
                            matches.append(match)
            
            self.detection_stats["total_detections"] += len(matches)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"Video detection completed in {processing_time:.2f}s: {len(matches)} matches found")
            
            return matches
            
        except Exception as e:
            logger.error(f"Video detection failed: {e}")
            return []
    
    async def _load_fingerprint(self, fingerprint_id: str) -> Optional[VideoFingerprint]:
        """Load full fingerprint data (placeholder - implement with your storage system)."""
        # This would load the full fingerprint data from your database
        # For now, return None to indicate not found
        return None
    
    def _calculate_confidence(
        self, 
        similarity_score: float, 
        feature_similarities: Dict[str, float],
        input_features: Dict[str, Any],
        stored_features: Dict[str, Any]
    ) -> float:
        """Calculate confidence level for match."""
        try:
            # Base confidence from overall similarity
            confidence = similarity_score
            
            # Boost confidence if multiple feature types match well
            high_similarity_features = sum(1 for sim in feature_similarities.values() if sim > 0.8)
            feature_boost = min(0.15, high_similarity_features * 0.05)
            confidence += feature_boost
            
            # Check resolution consistency
            if "resolution" in input_features and "resolution" in stored_features:
                input_res = input_features["resolution"]
                stored_res = stored_features["resolution"]
                if input_res == stored_res:
                    confidence += 0.05
            
            # Check duration consistency
            if "duration" in input_features and "duration" in stored_features:
                duration_diff = abs(input_features["duration"] - stored_features["duration"])
                if duration_diff < 5:  # Within 5 seconds
                    confidence += 0.05
            
            # Ensure confidence is between 0 and 1
            return min(1.0, max(0.0, confidence))
            
        except Exception as e:
            logger.error(f"Confidence calculation failed: {e}")
            return similarity_score
    
    async def get_detection_statistics(self) -> Dict[str, Any]:
        """Get detection engine statistics."""
        return {
            "engine_type": "video",
            "status": "active",
            "statistics": self.detection_stats,
            "thresholds": {
                "similarity_threshold": self.similarity_threshold,
                "confidence_threshold": self.confidence_threshold
            },
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def _calculate_audio_similarity(self, detected_features: Dict[str, np.ndarray], 
                                   reference_features: Dict[str, np.ndarray]) -> float:
        """Calculate audio similarity score between detected and reference video."""
        try:
            # Extract audio features if available
            detected_audio = detected_features.get('audio_features')
            reference_audio = reference_features.get('audio_features')
            
            if detected_audio is None or reference_audio is None:
                # Try alternative audio feature keys
                detected_audio = detected_features.get('mfcc')
                reference_audio = reference_features.get('mfcc')
            
            if detected_audio is None or reference_audio is None:
                return 0.0
            
            # Ensure arrays are the same shape for comparison
            min_length = min(len(detected_audio), len(reference_audio))
            if min_length == 0:
                return 0.0
            
            detected_audio = detected_audio[:min_length]
            reference_audio = reference_audio[:min_length]
            
            # Calculate cosine similarity
            detected_flat = detected_audio.flatten()
            reference_flat = reference_audio.flatten()
            
            # Handle edge case where one or both vectors have zero norm
            detected_norm = np.linalg.norm(detected_flat)
            reference_norm = np.linalg.norm(reference_flat)
            
            if detected_norm == 0 or reference_norm == 0:
                return 0.0
            
            # Cosine similarity
            similarity = np.dot(detected_flat, reference_flat) / (detected_norm * reference_norm)
            
            # Ensure similarity is in [0, 1] range
            return max(0.0, min(1.0, float(similarity)))
            
        except Exception as e:
            logger.warning(f"Audio similarity calculation failed: {e}")
            return 0.0
    
    async def cleanup(self) -> None:
        """Cleanup resources."""
        try:
            if self.chroma_client:
                # ChromaDB cleanup if needed
                pass
            logger.info("VideoDetectionEngine cleanup completed")
        except Exception as e:
            logger.error(f"VideoDetectionEngine cleanup failed: {e}")
