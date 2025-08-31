"""🎬 Video Content Fingerprinting Service
=======================================

Enterprise-grade video fingerprinting with advanced computer vision:
- Frame-based perceptual hashing
- Optical flow analysis
- YOLO object detection
- CNN feature extraction
- Temporal pattern analysis

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code and concept are protected by intellectual property rights.
Any unauthorized use, reproduction, or distribution without explicit written 
permission from Fahed Mlaiel is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for authorization requests.
"""import asyncio
import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Union
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
import math

try:
    import cv2
    import imagehash
    from PIL import Image
    import torch
    import torch.nn as nn
    import torchvision.transforms as transforms
    import torchvision.models as models
    from ultralytics import YOLO
    from sklearn.cluster import KMeans
    from scipy.spatial.distance import cosine
    import ffmpeg
except ImportError as e:
    logging.warning(f"Some video dependencies not available: {e}")

from ..models import FingerprintResult, SimilarityMatch

logger = logging.getLogger(__name__)

@dataclass
class VideoMetadata:
    """Comprehensive video metadata extraction."""    duration: float
    width: int
    height: int
    fps: float
    bitrate: Optional[int]
    codec: Optional[str]
    format: str
    total_frames: int
    avg_motion: Optional[float]
    scene_changes: Optional[List[float]]
    dominant_colors: Optional[List[Tuple[int, int, int]]]
    object_detections: Optional[Dict[str, int]]

class PerceptualHashExtractor:
    """Advanced perceptual hashing for video frames."""    
    def __init__(self, hash_size: int = 16):
        self.hash_size = hash_size
        self.sampling_rate = 1.0  # Sample every second
        
    def extract_frame_hashes(self, video_path: str) -> Dict[str, Any]:
        """        Extract perceptual hashes from video frames.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary containing frame hashes and metadata
        """        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise ValueError(f"Cannot open video: {video_path}")
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            frame_interval = max(1, int(fps * self.sampling_rate))
            
            frame_hashes = []
            frame_numbers = []
            timestamps = []
            
            frame_count = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % frame_interval == 0:
                    # Convert to PIL Image for hashing
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pil_image = Image.fromarray(frame_rgb)
                    
                    # Extract multiple hash types
                    phash = str(imagehash.phash(pil_image, hash_size=self.hash_size))
                    dhash = str(imagehash.dhash(pil_image, hash_size=self.hash_size))
                    ahash = str(imagehash.average_hash(pil_image, hash_size=self.hash_size))
                    whash = str(imagehash.whash(pil_image, hash_size=self.hash_size))
                    
                    frame_hashes.append({
                        "phash": phash,
                        "dhash": dhash,
                        "ahash": ahash,
                        "whash": whash,
                        "combined": self._combine_hashes(phash, dhash, ahash, whash)
                    })
                    
                    frame_numbers.append(frame_count)
                    timestamps.append(frame_count / fps)
                
                frame_count += 1
            
            cap.release()
            
            # Generate sequence fingerprint
            sequence_fingerprint = self._generate_sequence_fingerprint(frame_hashes)
            
            return {
                "frame_hashes": frame_hashes,
                "frame_numbers": frame_numbers,
                "timestamps": timestamps,
                "sequence_fingerprint": sequence_fingerprint,
                "total_frames_processed": len(frame_hashes),
                "sampling_rate": self.sampling_rate,
                "hash_size": self.hash_size,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Frame hash extraction failed for {video_path}: {e}")
            return {"error": str(e)}
    
    def _combine_hashes(self, phash: str, dhash: str, ahash: str, whash: str) -> str:
        """Combine multiple hash types into a single fingerprint."""        combined = f"{phash}|{dhash}|{ahash}|{whash}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _generate_sequence_fingerprint(self, frame_hashes: List[Dict[str, str]]) -> str:
        """Generate fingerprint from frame sequence."""        if not frame_hashes:
            return ""
        
        # Extract combined hashes
        combined_hashes = [fh["combined"] for fh in frame_hashes]
        
        # Create sequence signature
        sequence_string = "|".join(combined_hashes[:50])  # Limit to first 50 frames
        return hashlib.sha256(sequence_string.encode()).hexdigest()

class OpticalFlowAnalyzer:
    """Optical flow analysis for motion-based fingerprinting."""    
    def __init__(self):
        self.flow_method = cv2.optflow.calcOpticalFlowPyrLK
        self.feature_params = {
            'maxCorners': 100,
            'qualityLevel': 0.3,
            'minDistance': 7,
            'blockSize': 7
        }
        
    def analyze_motion(self, video_path: str) -> Dict[str, Any]:
        """        Analyze motion patterns in video using optical flow.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary containing motion analysis results
        """        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise ValueError(f"Cannot open video: {video_path}")
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            motion_vectors = []
            motion_magnitudes = []
            motion_directions = []
            
            # Read first frame
            ret, prev_frame = cap.read()
            if not ret:
                return {"error": "Cannot read first frame"}
            
            prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
            
            frame_count = 1
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Calculate optical flow
                flow = cv2.calcOpticalFlowPyrLK(
                    prev_gray, gray, 
                    cv2.goodFeaturesToTrack(prev_gray, **self.feature_params),
                    None
                )
                
                if flow[0] is not None and len(flow[0]) > 0:
                    # Calculate motion vectors
                    vectors = flow[0] - flow[1] if flow[1] is not None else flow[0]
                    
                    # Motion statistics
                    avg_magnitude = np.mean(np.linalg.norm(vectors, axis=1))
                    avg_direction = np.mean(np.arctan2(vectors[:, 1], vectors[:, 0]))
                    
                    motion_vectors.append(vectors.tolist())
                    motion_magnitudes.append(float(avg_magnitude))
                    motion_directions.append(float(avg_direction))
                
                prev_gray = gray
                frame_count += 1
            
            cap.release()
            
            # Generate motion fingerprint
            motion_fingerprint = self._generate_motion_fingerprint(
                motion_magnitudes, motion_directions
            )
            
            return {
                "motion_vectors": motion_vectors[:100],  # Limit size
                "motion_magnitudes": motion_magnitudes,
                "motion_directions": motion_directions,
                "motion_fingerprint": motion_fingerprint,
                "avg_motion": float(np.mean(motion_magnitudes)) if motion_magnitudes else 0.0,
                "motion_variance": float(np.var(motion_magnitudes)) if motion_magnitudes else 0.0,
                "frames_analyzed": frame_count,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Motion analysis failed for {video_path}: {e}")
            return {"error": str(e)}
    
    def _generate_motion_fingerprint(self, magnitudes: List[float], directions: List[float]) -> str:
        """Generate fingerprint from motion data."""        if not magnitudes or not directions:
            return ""
        
        # Quantize motion data
        mag_quantized = self._quantize_values(magnitudes, bins=16)
        dir_quantized = self._quantize_values(directions, bins=16)
        
        # Combine quantized values
        combined = [f"{m},{d}" for m, d in zip(mag_quantized, dir_quantized)]
        fingerprint_string = "|".join(combined[:50])  # Limit size
        
        return hashlib.md5(fingerprint_string.encode()).hexdigest()
    
    def _quantize_values(self, values: List[float], bins: int = 16) -> List[int]:
        """Quantize continuous values into discrete bins."""        if not values:
            return []
        
        min_val, max_val = min(values), max(values)
        if min_val == max_val:
            return [0] * len(values)
        
        bin_size = (max_val - min_val) / bins
        return [min(int((v - min_val) / bin_size), bins - 1) for v in values]

class ObjectDetectionAnalyzer:
    """YOLO-based object detection for content analysis."""    
    def __init__(self, model_name: str = "yolov8n.pt"):
        self.model_name = model_name
        self.model = None
        self._initialize_model()
        
    def _initialize_model(self):
        """Initialize YOLO model."""        try:
            self.model = YOLO(self.model_name)
        except Exception as e:
            logger.warning(f"YOLO model initialization failed: {e}")
    
    def detect_objects(self, video_path: str) -> Dict[str, Any]:
        """        Detect objects in video frames.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary containing object detection results
        """        if not self.model:
            return {"error": "YOLO model not initialized"}
            
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise ValueError(f"Cannot open video: {video_path}")
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_interval = max(1, int(fps * 2))  # Sample every 2 seconds
            
            object_detections = {}
            frame_detections = []
            
            frame_count = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % frame_interval == 0:
                    # Run YOLO detection
                    results = self.model(frame, verbose=False)
                    
                    frame_objects = []
                    for result in results:
                        for box in result.boxes:
                            if box.conf > 0.5:  # Confidence threshold
                                class_id = int(box.cls)
                                class_name = self.model.names[class_id]
                                confidence = float(box.conf)
                                
                                # Count objects
                                object_detections[class_name] = object_detections.get(class_name, 0) + 1
                                
                                frame_objects.append({
                                    "class": class_name,
                                    "confidence": confidence,
                                    "bbox": box.xyxy[0].tolist()
                                })
                    
                    frame_detections.append({
                        "frame": frame_count,
                        "timestamp": frame_count / fps,
                        "objects": frame_objects
                    })
                
                frame_count += 1
            
            cap.release()
            
            # Generate object fingerprint
            object_fingerprint = self._generate_object_fingerprint(object_detections)
            
            return {
                "object_detections": object_detections,
                "frame_detections": frame_detections[:50],  # Limit size
                "object_fingerprint": object_fingerprint,
                "total_objects": sum(object_detections.values()),
                "unique_objects": len(object_detections),
                "frames_analyzed": len(frame_detections),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Object detection failed for {video_path}: {e}")
            return {"error": str(e)}
    
    def _generate_object_fingerprint(self, object_detections: Dict[str, int]) -> str:
        """Generate fingerprint from object detection data."""        if not object_detections:
            return ""
        
        # Sort by frequency and create signature
        sorted_objects = sorted(object_detections.items(), key=lambda x: x[1], reverse=True)
        fingerprint_string = "|".join([f"{obj}:{count}" for obj, count in sorted_objects[:20]])
        
        return hashlib.md5(fingerprint_string.encode()).hexdigest()

class CNNFeatureExtractor:
    """CNN-based feature extraction for video frames."""    
    def __init__(self, model_name: str = "resnet50"):
        self.model_name = model_name
        self.model = None
        self.transform = None
        self._initialize_model()
        
    def _initialize_model(self):
        """Initialize pre-trained CNN model."""        try:
            if self.model_name == "resnet50":
                self.model = models.resnet50(pretrained=True)
                self.model.fc = nn.Identity()  # Remove final layer
                
            self.model.eval()
            
            self.transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                                   std=[0.229, 0.224, 0.225])
            ])
            
        except Exception as e:
            logger.warning(f"CNN model initialization failed: {e}")
    
    def extract_features(self, video_path: str) -> Dict[str, Any]:
        """        Extract CNN features from video frames.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary containing extracted features
        """        if not self.model or not self.transform:
            return {"error": "CNN model not initialized"}
            
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise ValueError(f"Cannot open video: {video_path}")
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_interval = max(1, int(fps * 3))  # Sample every 3 seconds
            
            frame_features = []
            frame_count = 0
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % frame_interval == 0:
                    # Convert frame to PIL Image
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pil_image = Image.fromarray(frame_rgb)
                    
                    # Extract features
                    with torch.no_grad():
                        input_tensor = self.transform(pil_image).unsqueeze(0)
                        features = self.model(input_tensor)
                        features_np = features.squeeze().numpy()
                        
                    frame_features.append({
                        "frame": frame_count,
                        "timestamp": frame_count / fps,
                        "features": features_np.tolist()
                    })
                
                frame_count += 1
            
            cap.release()
            
            # Generate feature-based fingerprint
            if frame_features:
                feature_fingerprint = self._generate_feature_fingerprint(frame_features)
                avg_features = self._compute_average_features(frame_features)
            else:
                feature_fingerprint = ""
                avg_features = []
            
            return {
                "frame_features": frame_features[:20],  # Limit size
                "feature_fingerprint": feature_fingerprint,
                "average_features": avg_features,
                "features_dimension": len(avg_features) if avg_features else 0,
                "frames_processed": len(frame_features),
                "model_name": self.model_name,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"CNN feature extraction failed for {video_path}: {e}")
            return {"error": str(e)}
    
    def _generate_feature_fingerprint(self, frame_features: List[Dict[str, Any]]) -> str:
        """Generate fingerprint from CNN features."""        if not frame_features:
            return ""
        
        # Extract feature vectors
        features = [ff["features"] for ff in frame_features]
        
        # Compute average feature vector
        avg_features = np.mean(features, axis=0)
        
        # Quantize features
        normalized_features = (avg_features - np.mean(avg_features)) / (np.std(avg_features) + 1e-8)
        binary_features = (normalized_features > 0).astype(int)
        
        # Convert to hash
        hash_string = ''.join([str(bit) for bit in binary_features])
        return hashlib.md5(hash_string.encode()).hexdigest()
    
    def _compute_average_features(self, frame_features: List[Dict[str, Any]]) -> List[float]:
        """Compute average feature vector across all frames."""        if not frame_features:
            return []
        
        features = [ff["features"] for ff in frame_features]
        avg_features = np.mean(features, axis=0)
        return avg_features.tolist()

class SceneChangeDetector:
    """Detect scene changes and transitions in video."""    
    def __init__(self, threshold: float = 0.3):
        self.threshold = threshold
        
    def detect_scenes(self, video_path: str) -> Dict[str, Any]:
        """        Detect scene changes in video.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary containing scene change data
        """        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise ValueError(f"Cannot open video: {video_path}")
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            scene_changes = []
            prev_hist = None
            
            frame_count = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Convert to grayscale and compute histogram
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
                hist = cv2.normalize(hist, hist).flatten()
                
                if prev_hist is not None:
                    # Calculate histogram difference
                    diff = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_CORREL)
                    
                    if diff < (1 - self.threshold):  # Scene change detected
                        scene_changes.append({
                            "frame": frame_count,
                            "timestamp": frame_count / fps,
                            "difference": float(1 - diff)
                        })
                
                prev_hist = hist
                frame_count += 1
            
            cap.release()
            
            # Generate scene fingerprint
            scene_fingerprint = self._generate_scene_fingerprint(scene_changes)
            
            return {
                "scene_changes": scene_changes,
                "scene_fingerprint": scene_fingerprint,
                "total_scenes": len(scene_changes) + 1,
                "avg_scene_length": (frame_count / fps) / (len(scene_changes) + 1) if scene_changes else frame_count / fps,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Scene detection failed for {video_path}: {e}")
            return {"error": str(e)}
    
    def _generate_scene_fingerprint(self, scene_changes: List[Dict[str, Any]]) -> str:
        """Generate fingerprint from scene change data."""        if not scene_changes:
            return ""
        
        # Extract timestamps
        timestamps = [sc["timestamp"] for sc in scene_changes]
        
        # Quantize timestamps
        if len(timestamps) > 1:
            max_time = max(timestamps)
            normalized_times = [t / max_time for t in timestamps]
            quantized_times = [int(t * 100) for t in normalized_times]  # 0-100 scale
            
            fingerprint_string = "|".join(map(str, quantized_times[:20]))  # Limit size
            return hashlib.md5(fingerprint_string.encode()).hexdigest()
        
        return ""

class VideoFingerprintingService:
    """    Comprehensive video fingerprinting service combining multiple techniques.
    
    Features:
    - Perceptual frame hashing
    - Optical flow motion analysis
    - YOLO object detection
    - CNN feature extraction
    - Scene change detection
    - Temporal pattern analysis
    """    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.hash_extractor = PerceptualHashExtractor()
        self.motion_analyzer = OpticalFlowAnalyzer()
        self.object_detector = ObjectDetectionAnalyzer()
        self.cnn_extractor = CNNFeatureExtractor()
        self.scene_detector = SceneChangeDetector()
        
        # Similarity thresholds
        self.similarity_thresholds = {
            "perceptual": 0.85,
            "motion": 0.75,
            "objects": 0.80,
            "cnn": 0.90,
            "scenes": 0.70,
            "combined": 0.78
        }
        
    async def process_video(self, video_path: str, user_id: int) -> FingerprintResult:
        """        Process video file and generate comprehensive fingerprint.
        
        Args:
            video_path: Path to video file
            user_id: User ID for attribution
            
        Returns:
            FingerprintResult containing all fingerprint data
        """        try:
            logger.info(f"Processing video fingerprint for: {video_path}")
            
            # Extract metadata
            metadata = await self._extract_metadata(video_path)
            
            # Run all fingerprinting algorithms in parallel
            tasks = [
                asyncio.create_task(self._run_perceptual_hash(video_path)),
                asyncio.create_task(self._run_motion_analysis(video_path)),
                asyncio.create_task(self._run_object_detection(video_path)),
                asyncio.create_task(self._run_cnn_features(video_path)),
                asyncio.create_task(self._run_scene_detection(video_path))
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            perceptual_result = results[0] if not isinstance(results[0], Exception) else {}
            motion_result = results[1] if not isinstance(results[1], Exception) else {}
            object_result = results[2] if not isinstance(results[2], Exception) else {}
            cnn_result = results[3] if not isinstance(results[3], Exception) else {}
            scene_result = results[4] if not isinstance(results[4], Exception) else {}
            
            # Combine results
            fingerprint_data = {
                "perceptual": perceptual_result,
                "motion": motion_result,
                "objects": object_result,
                "cnn_features": cnn_result,
                "scenes": scene_result,
                "metadata": metadata,
                "processing_timestamp": datetime.utcnow().isoformat()
            }
            
            # Generate combined hash
            combined_hash = self._generate_combined_hash(fingerprint_data)
            
            return FingerprintResult(
                user_id=user_id,
                content_type="video",
                file_path=video_path,
                fingerprint_data=fingerprint_data,
                hash_value=combined_hash,
                processing_time=datetime.utcnow(),
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Video fingerprinting failed for {video_path}: {e}")
            raise
    
    async def _extract_metadata(self, video_path: str) -> VideoMetadata:
        """Extract comprehensive video metadata."""        try:
            # Use OpenCV for basic metadata
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise ValueError(f"Cannot open video: {video_path}")
            
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps > 0 else 0
            
            cap.release()
            
            # Try to get additional metadata with ffprobe
            try:
                probe = ffmpeg.probe(video_path)
                video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
                
                bitrate = int(video_stream.get('bit_rate', 0)) if video_stream and 'bit_rate' in video_stream else None
                codec = video_stream.get('codec_name') if video_stream else None
                format_name = probe['format'].get('format_name', '')
                
            except Exception:
                bitrate = None
                codec = None
                format_name = Path(video_path).suffix.lower()
            
            return VideoMetadata(
                duration=duration,
                width=width,
                height=height,
                fps=fps,
                bitrate=bitrate,
                codec=codec,
                format=format_name,
                total_frames=total_frames,
                avg_motion=None,  # Will be filled by motion analysis
                scene_changes=None,  # Will be filled by scene detection
                dominant_colors=None,  # Could be added
                object_detections=None  # Will be filled by object detection
            )
            
        except Exception as e:
            logger.error(f"Video metadata extraction failed for {video_path}: {e}")
            return VideoMetadata(
                duration=0.0,
                width=0,
                height=0,
                fps=0.0,
                bitrate=None,
                codec=None,
                format="unknown",
                total_frames=0,
                avg_motion=None,
                scene_changes=None,
                dominant_colors=None,
                object_detections=None
            )
    
    async def _run_perceptual_hash(self, video_path: str) -> Dict[str, Any]:
        """Run perceptual hash extraction."""        return await asyncio.get_event_loop().run_in_executor(
            None, self.hash_extractor.extract_frame_hashes, video_path
        )
    
    async def _run_motion_analysis(self, video_path: str) -> Dict[str, Any]:
        """Run motion analysis."""        return await asyncio.get_event_loop().run_in_executor(
            None, self.motion_analyzer.analyze_motion, video_path
        )
    
    async def _run_object_detection(self, video_path: str) -> Dict[str, Any]:
        """Run object detection."""        return await asyncio.get_event_loop().run_in_executor(
            None, self.object_detector.detect_objects, video_path
        )
    
    async def _run_cnn_features(self, video_path: str) -> Dict[str, Any]:
        """Run CNN feature extraction."""        return await asyncio.get_event_loop().run_in_executor(
            None, self.cnn_extractor.extract_features, video_path
        )
    
    async def _run_scene_detection(self, video_path: str) -> Dict[str, Any]:
        """Run scene change detection."""        return await asyncio.get_event_loop().run_in_executor(
            None, self.scene_detector.detect_scenes, video_path
        )
    
    def _generate_combined_hash(self, fingerprint_data: Dict[str, Any]) -> str:
        """Generate combined hash from all fingerprint components."""        hash_components = []
        
        # Extract key hash components
        if "perceptual" in fingerprint_data and "sequence_fingerprint" in fingerprint_data["perceptual"]:
            hash_components.append(fingerprint_data["perceptual"]["sequence_fingerprint"])
            
        if "motion" in fingerprint_data and "motion_fingerprint" in fingerprint_data["motion"]:
            hash_components.append(fingerprint_data["motion"]["motion_fingerprint"])
            
        if "objects" in fingerprint_data and "object_fingerprint" in fingerprint_data["objects"]:
            hash_components.append(fingerprint_data["objects"]["object_fingerprint"])
            
        if "cnn_features" in fingerprint_data and "feature_fingerprint" in fingerprint_data["cnn_features"]:
            hash_components.append(fingerprint_data["cnn_features"]["feature_fingerprint"])
            
        if "scenes" in fingerprint_data and "scene_fingerprint" in fingerprint_data["scenes"]:
            hash_components.append(fingerprint_data["scenes"]["scene_fingerprint"])
        
        # Combine and hash
        combined_string = "|".join(hash_components)
        return hashlib.sha256(combined_string.encode()).hexdigest()
    
    async def find_similar(self, fingerprint_data: Dict[str, Any], threshold: float = 0.8) -> List[SimilarityMatch]:
        """        Find similar video content based on fingerprint data.
        
        Args:
            fingerprint_data: Fingerprint data to match against
            threshold: Similarity threshold (0.0 to 1.0)
            
        Returns:
            List of similarity matches
        """        # This would typically interface with a vector database
        # For now, return empty list (implementation depends on storage backend)
        logger.info(f"Searching for similar video with threshold {threshold}")
        return []
    
    def calculate_similarity(self, fp1: Dict[str, Any], fp2: Dict[str, Any]) -> float:
        """        Calculate similarity score between two video fingerprints.
        
        Args:
            fp1: First fingerprint data
            fp2: Second fingerprint data
            
        Returns:
            Similarity score (0.0 to 1.0)
        """        similarity_scores = []
        
        # Perceptual similarity
        if ("perceptual" in fp1 and "perceptual" in fp2 and
            "sequence_fingerprint" in fp1["perceptual"] and "sequence_fingerprint" in fp2["perceptual"]):
            perceptual_sim = self._hash_similarity(
                fp1["perceptual"]["sequence_fingerprint"],
                fp2["perceptual"]["sequence_fingerprint"]
            )
            similarity_scores.append(perceptual_sim * 0.3)  # 30% weight
        
        # Motion similarity
        if ("motion" in fp1 and "motion" in fp2 and
            "motion_fingerprint" in fp1["motion"] and "motion_fingerprint" in fp2["motion"]):
            motion_sim = self._hash_similarity(
                fp1["motion"]["motion_fingerprint"],
                fp2["motion"]["motion_fingerprint"]
            )
            similarity_scores.append(motion_sim * 0.2)  # 20% weight
        
        # Object similarity
        if ("objects" in fp1 and "objects" in fp2 and
            "object_fingerprint" in fp1["objects"] and "object_fingerprint" in fp2["objects"]):
            object_sim = self._hash_similarity(
                fp1["objects"]["object_fingerprint"],
                fp2["objects"]["object_fingerprint"]
            )
            similarity_scores.append(object_sim * 0.2)  # 20% weight
        
        # CNN features similarity
        if ("cnn_features" in fp1 and "cnn_features" in fp2 and
            "average_features" in fp1["cnn_features"] and "average_features" in fp2["cnn_features"]):
            cnn_sim = self._feature_similarity(
                fp1["cnn_features"]["average_features"],
                fp2["cnn_features"]["average_features"]
            )
            similarity_scores.append(cnn_sim * 0.3)  # 30% weight
        
        return sum(similarity_scores) if similarity_scores else 0.0
    
    def _hash_similarity(self, hash1: str, hash2: str) -> float:
        """Calculate hash similarity using Hamming distance."""        if len(hash1) != len(hash2):
            return 0.0
        
        matches = sum(c1 == c2 for c1, c2 in zip(hash1, hash2))
        return matches / len(hash1)
    
    def _feature_similarity(self, feat1: List[float], feat2: List[float]) -> float:
        """Calculate feature similarity using cosine similarity."""        try:
            feat1_array = np.array(feat1)
            feat2_array = np.array(feat2)
            
            # Cosine similarity
            dot_product = np.dot(feat1_array, feat2_array)
            norm1 = np.linalg.norm(feat1_array)
            norm2 = np.linalg.norm(feat2_array)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
                
            return dot_product / (norm1 * norm2)
            
        except Exception as e:
            logger.error(f"Feature similarity calculation failed: {e}")
            return 0.0
