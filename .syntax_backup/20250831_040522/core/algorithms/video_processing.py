"""
Video Processing Engine - Advanced Computer Vision & Analysis
===========================================================

Professional video processing engine for content creators providing:
- Frame-by-Frame Analysis & Feature Extraction
- Object Detection & Recognition (YOLO, RCNN)
- Scene Classification & Content Understanding
- Video Fingerprinting & Similarity Matching
- Motion Analysis & Tracking
- Video Quality Assessment
- Temporal Feature Extraction
- Thumbnail Generation & Key Frame Selection
- Video Enhancement & Optimization
- Real-time Video Stream Processing

Created by: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use strictly prohibited
"""

import cv2
import numpy as np
import torch
import torchvision
from typing import Dict, List, Any, Optional, Tuple, Union
import logging
from dataclasses import dataclass
from PIL import Image
import imagehash
from sklearn.cluster import KMeans
from transformers import CLIPProcessor, CLIPModel
import moviepy.editor as mp
from scipy.spatial.distance import cosine
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class VideoFeatures:
    """Comprehensive video feature representation"""
    visual_features: Dict[str, np.ndarray]
    temporal_features: Dict[str, Any]
    motion_features: Dict[str, np.ndarray]
    scene_features: Dict[str, List[str]]
    quality_metrics: Dict[str, float]
    fingerprint: np.ndarray
    metadata: Dict[str, Any]

@dataclass
class FrameAnalysis:
    """Individual frame analysis results"""
    frame_number: int
    timestamp: float
    objects_detected: List[Dict[str, Any]]
    scene_classification: Dict[str, float]
    visual_features: np.ndarray
    quality_score: float
    motion_vectors: Optional[np.ndarray] = None

class VideoProcessingEngine:
    """
    Industrial-grade video processing engine for content creators
    """
    
    def __init__(self, target_fps: int = 30, max_resolution: Tuple[int, int] = (1920, 1080)):
        self.target_fps = target_fps
        self.max_resolution = max_resolution
        
        # Initialize AI models
        self._initialize_models()
        
        # Initialize OpenCV components
        self._initialize_opencv()
        
        logger.info("VideoProcessingEngine initialized successfully")
    
    def _initialize_models(self) -> None:
        """Initialize AI models for video analysis"""
        try:
            # CLIP model for scene understanding
            self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            
            # Object detection models
            self._load_object_detection_models()
            
            # Video classification models
            self._load_video_classification_models()
            
        except Exception as e:
            logger.error(f"Failed to initialize AI models: {e}")
            raise
    
    def _initialize_opencv(self) -> None:
        """Initialize OpenCV components"""
        try:
            # Background subtractor for motion detection
            self.bg_subtractor = cv2.createBackgroundSubtractorMOG2()
            
    def _initialize_opencv(self) -> None:
        """Initialize OpenCV components"""
        try:
            # Background subtractor for motion detection
            self.bg_subtractor = cv2.createBackgroundSubtractorMOG2()
            
            # Optical flow detector
            self.optical_flow = cv2.calcOpticalFlowPyrLK
            
            # Feature detectors
            self.sift_detector = cv2.SIFT_create()
            self.orb_detector = cv2.ORB_create()
            
            # Cascade classifiers
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenCV: {e}")
            raise
    
    def _load_object_detection_models(self) -> None:
        """Load object detection models"""
        try:
            # YOLOv5 model
            self.yolo_model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
            self.yolo_model.eval()
            
            # COCO class names
            self.coco_classes = [
                'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck',
                'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench',
                'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra',
                'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
                'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove',
                'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup',
                'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange',
                'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
                'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse',
                'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink',
                'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier',
                'toothbrush'
            ]
            
            logger.info("Object detection models loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load object detection models: {e}")
            self.yolo_model = None
    
    def _load_video_classification_models(self) -> None:
        """Load video classification models"""
        try:
            # Scene classification labels
            self.scene_labels = [
                'indoor', 'outdoor', 'urban', 'nature', 'beach', 'mountain', 'forest',
                'office', 'home', 'street', 'park', 'building', 'vehicle', 'crowd',
                'performance', 'sports', 'interview', 'presentation', 'tutorial'
            ]
            
            # Content type labels
            self.content_labels = [
                'music_video', 'vlog', 'tutorial', 'gaming', 'review', 'interview',
                'performance', 'documentary', 'comedy', 'drama', 'action', 'news'
            ]
            
            logger.info("Video classification models loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load video classification models: {e}")
            self.scene_labels = []
            self.content_labels = []
    
    def process(self, video_path: str, config: Optional[Dict[str, Any]] = None) -> VideoFeatures:
        """
        Comprehensive video analysis with AI-powered feature extraction
        
        Args:
            video_path: Path to video file
            config: Processing configuration parameters
            
        Returns:
            VideoFeatures: Complete video analysis results
        """
        try:
            # Open video file
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Cannot open video file: {video_path}")
            
            # Extract video metadata
            metadata = self._extract_video_metadata(cap, video_path)
            
            # Process frames
            frame_analyses = self._process_frames(cap, config)
            
            # Extract comprehensive features
            visual_features = self._extract_visual_features(frame_analyses)
            temporal_features = self._extract_temporal_features(frame_analyses, metadata)
            motion_features = self._extract_motion_features(frame_analyses)
            scene_features = self._extract_scene_features(frame_analyses)
            quality_metrics = self._assess_video_quality(frame_analyses, metadata)
            
            # Generate video fingerprint
            fingerprint = self._generate_video_fingerprint(frame_analyses)
            
            cap.release()
            
            return VideoFeatures(
                visual_features=visual_features,
                temporal_features=temporal_features,
                motion_features=motion_features,
                scene_features=scene_features,
                quality_metrics=quality_metrics,
                fingerprint=fingerprint,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Video processing failed: {e}")
            raise
    
    def _extract_video_metadata(self, cap: cv2.VideoCapture, video_path: str) -> Dict[str, Any]:
        """Extract comprehensive video metadata"""
        try:
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            # Additional metadata using MoviePy
            try:
                clip = mp.VideoFileClip(video_path)
                audio_present = clip.audio is not None
                audio_duration = clip.audio.duration if audio_present else 0
                clip.close()
            except:
                audio_present = False
                audio_duration = 0
            
            return {
                'file_path': video_path,
                'fps': fps,
                'frame_count': frame_count,
                'width': width,
                'height': height,
                'duration': duration,
                'resolution': f"{width}x{height}",
                'aspect_ratio': width / height if height > 0 else 0,
                'audio_present': audio_present,
                'audio_duration': audio_duration,
                'file_size_mb': self._get_file_size(video_path),
                'analysis_timestamp': np.datetime64('now')
            }
            
        except Exception as e:
            logger.error(f"Video metadata extraction failed: {e}")
            return {}
    
    def _process_frames(self, cap: cv2.VideoCapture, config: Optional[Dict[str, Any]] = None) -> List[FrameAnalysis]:
        """Process video frames with AI analysis"""
        try:
            frame_analyses = []
            frame_number = 0
            sample_rate = config.get('sample_rate', 30) if config else 30  # Analyze every Nth frame
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Sample frames based on config
                if frame_number % sample_rate == 0:
                    timestamp = frame_number / cap.get(cv2.CAP_PROP_FPS)
                    
                    # Analyze frame
                    analysis = self._analyze_frame(frame, frame_number, timestamp)
                    frame_analyses.append(analysis)
                
                frame_number += 1
                
                # Limit analysis for very long videos
                if len(frame_analyses) > 1000:  # Max 1000 sampled frames
                    break
            
            return frame_analyses
            
        except Exception as e:
            logger.error(f"Frame processing failed: {e}")
            return []
    
    def _analyze_frame(self, frame: np.ndarray, frame_number: int, timestamp: float) -> FrameAnalysis:
        """Comprehensive analysis of a single frame"""
        try:
            # Object detection
            objects_detected = self._detect_objects(frame)
            
            # Scene classification
            scene_classification = self._classify_scene(frame)
            
            # Visual feature extraction
            visual_features = self._extract_frame_features(frame)
            
            # Quality assessment
            quality_score = self._assess_frame_quality(frame)
            
            return FrameAnalysis(
                frame_number=frame_number,
                timestamp=timestamp,
                objects_detected=objects_detected,
                scene_classification=scene_classification,
                visual_features=visual_features,
                quality_score=quality_score
            )
            
        except Exception as e:
            logger.error(f"Frame analysis failed: {e}")
            return FrameAnalysis(
                frame_number=frame_number,
                timestamp=timestamp,
                objects_detected=[],
                scene_classification={},
                visual_features=np.array([]),
                quality_score=0.0
            )
    
    def _detect_objects(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Detect objects in frame using YOLO"""
        try:
            if self.yolo_model is None:
                return []
            
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Run YOLO detection
            results = self.yolo_model(rgb_frame)
            detections = results.pandas().xyxy[0].to_dict('records')
            
            # Format detection results
            objects = []
            for detection in detections:
                if detection['confidence'] > 0.5:  # Confidence threshold
                    objects.append({
                        'class': detection['name'],
                        'confidence': float(detection['confidence']),
                        'bbox': [
                            float(detection['xmin']),
                            float(detection['ymin']),
                            float(detection['xmax']),
                            float(detection['ymax'])
                        ]
                    })
            
            return objects
            
        except Exception as e:
            logger.error(f"Object detection failed: {e}")
            return []
    
    def _classify_scene(self, frame: np.ndarray) -> Dict[str, float]:
        """Classify scene content using CLIP"""
        try:
            # Convert frame to PIL Image
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)
            
            # Process with CLIP
            inputs = self.clip_processor(
                text=self.scene_labels,
                images=pil_image,
                return_tensors="pt",
                padding=True
            )
            
            with torch.no_grad():
                outputs = self.clip_model(**inputs)
                logits_per_image = outputs.logits_per_image
                probs = logits_per_image.softmax(dim=1)
            
            # Convert to dictionary
            scene_scores = {}
            for i, label in enumerate(self.scene_labels):
                scene_scores[label] = float(probs[0][i])
            
            return scene_scores
            
        except Exception as e:
            logger.error(f"Scene classification failed: {e}")
            return {}
    
    def _extract_frame_features(self, frame: np.ndarray) -> np.ndarray:
        """Extract visual features from frame"""
        try:
            # Resize frame for processing
            resized = cv2.resize(frame, (224, 224))
            
            # Color histogram
            hist_b = cv2.calcHist([resized], [0], None, [32], [0, 256])
            hist_g = cv2.calcHist([resized], [1], None, [32], [0, 256])
            hist_r = cv2.calcHist([resized], [2], None, [32], [0, 256])
            
            # Texture features (LBP-like)
            gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            
            # SIFT features
            sift_features = self._extract_sift_features(gray)
            
            # Combine features
            features = np.concatenate([
                hist_b.flatten(),
                hist_g.flatten(),
                hist_r.flatten(),
                sift_features
            ])
            
            return features
            
        except Exception as e:
            logger.error(f"Frame feature extraction failed: {e}")
            return np.array([])
    
    def _extract_sift_features(self, gray_frame: np.ndarray) -> np.ndarray:
        """Extract SIFT features from grayscale frame"""
        try:
            keypoints, descriptors = self.sift_detector.detectAndCompute(gray_frame, None)
            
            if descriptors is not None:
                # Use first 100 descriptors or pad if less
                if len(descriptors) >= 100:
                    return descriptors[:100].flatten()
                else:
                    padded = np.zeros((100, 128))
                    padded[:len(descriptors)] = descriptors
                    return padded.flatten()
            else:
                return np.zeros(100 * 128)  # 100 keypoints * 128 dimensions
                
        except Exception as e:
            logger.error(f"SIFT feature extraction failed: {e}")
            return np.zeros(100 * 128)
    
    def _assess_frame_quality(self, frame: np.ndarray) -> float:
        """Assess frame quality metrics"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Sharpness (Laplacian variance)
            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Brightness
            brightness = np.mean(gray)
            
            # Contrast
            contrast = gray.std()
            
            # Normalize and combine metrics
            normalized_sharpness = min(sharpness / 1000, 1.0)  # Normalize
            normalized_brightness = 1.0 - abs(brightness - 128) / 128  # Optimal around 128
            normalized_contrast = min(contrast / 64, 1.0)  # Normalize
            
            quality_score = (normalized_sharpness + normalized_brightness + normalized_contrast) / 3
            
            return float(quality_score)
            
        except Exception as e:
            logger.error(f"Frame quality assessment failed: {e}")
            return 0.0
    
    def _extract_visual_features(self, frame_analyses: List[FrameAnalysis]) -> Dict[str, np.ndarray]:
        """Extract aggregated visual features from all frames"""
        try:
            if not frame_analyses:
                return {}
            
            # Aggregate visual features
            all_features = np.array([analysis.visual_features for analysis in frame_analyses 
                                   if len(analysis.visual_features) > 0])
            
            if len(all_features) == 0:
                return {}
            
            # Statistical aggregation
            mean_features = np.mean(all_features, axis=0)
            std_features = np.std(all_features, axis=0)
            
            # Dominant colors analysis
            dominant_colors = self._extract_dominant_colors(frame_analyses)
            
            return {
                'mean_features': mean_features,
                'std_features': std_features,
                'dominant_colors': dominant_colors,
                'feature_count': len(all_features)
            }
            
        except Exception as e:
            logger.error(f"Visual feature aggregation failed: {e}")
            return {}
    
    def _extract_dominant_colors(self, frame_analyses: List[FrameAnalysis]) -> np.ndarray:
        """Extract dominant colors from video"""
        try:
            # Sample color histograms from frames
            color_samples = []
            
            for analysis in frame_analyses[:100]:  # Sample first 100 frames
                if len(analysis.visual_features) >= 96:  # RGB histograms
                    color_samples.append(analysis.visual_features[:96])  # RGB histograms
            
            if not color_samples:
                return np.array([])
            
            # Cluster colors to find dominant ones
            color_data = np.array(color_samples)
            kmeans = KMeans(n_clusters=5, random_state=42)
            kmeans.fit(color_data)
            
            return kmeans.cluster_centers_
            
        except Exception as e:
            logger.error(f"Dominant color extraction failed: {e}")
            return np.array([])
    
    def _extract_temporal_features(self, frame_analyses: List[FrameAnalysis], 
                                  metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract temporal features and patterns"""
        try:
            if not frame_analyses:
                return {}
            
            # Scene transitions
            scene_transitions = self._detect_scene_transitions(frame_analyses)
            
            # Activity levels over time
            activity_timeline = [analysis.quality_score for analysis in frame_analyses]
            
            # Object appearance timeline
            object_timeline = self._create_object_timeline(frame_analyses)
            
            return {
                'scene_transitions': scene_transitions,
                'activity_timeline': activity_timeline,
                'object_timeline': object_timeline,
                'total_scenes': len(scene_transitions) + 1,
                'average_scene_length': metadata.get('duration', 0) / (len(scene_transitions) + 1) if scene_transitions else metadata.get('duration', 0)
            }
            
        except Exception as e:
            logger.error(f"Temporal feature extraction failed: {e}")
            return {}
    
    def _detect_scene_transitions(self, frame_analyses: List[FrameAnalysis]) -> List[float]:
        """Detect scene transitions based on visual changes"""
        try:
            transitions = []
            
            for i in range(1, len(frame_analyses)):
                prev_features = frame_analyses[i-1].visual_features
                curr_features = frame_analyses[i].visual_features
                
                if len(prev_features) > 0 and len(curr_features) > 0:
                    # Calculate feature similarity
                    similarity = cosine(prev_features, curr_features)
                    
                    # Detect significant changes (scene transitions)
                    if similarity > 0.7:  # Threshold for scene change
                        transitions.append(frame_analyses[i].timestamp)
            
            return transitions
            
        except Exception as e:
            logger.error(f"Scene transition detection failed: {e}")
            return []
    
    def _create_object_timeline(self, frame_analyses: List[FrameAnalysis]) -> Dict[str, List[float]]:
        """Create timeline of object appearances"""
        try:
            object_timeline = {}
            
            for analysis in frame_analyses:
                for obj in analysis.objects_detected:
                    obj_class = obj['class']
                    if obj_class not in object_timeline:
                        object_timeline[obj_class] = []
                    object_timeline[obj_class].append(analysis.timestamp)
            
            return object_timeline
            
        except Exception as e:
            logger.error(f"Object timeline creation failed: {e}")
            return {}
    
    def _extract_motion_features(self, frame_analyses: List[FrameAnalysis]) -> Dict[str, np.ndarray]:
        """Extract motion and camera movement features"""
        try:
            # Motion intensity over time
            motion_intensity = []
            
            # Camera movement detection (simplified)
            camera_movements = []
            
            for i, analysis in enumerate(frame_analyses):
                # Estimate motion from object count changes and quality variations
                if i > 0:
                    prev_objects = len(frame_analyses[i-1].objects_detected)
                    curr_objects = len(analysis.objects_detected)
                    object_change = abs(curr_objects - prev_objects)
                    
                    quality_change = abs(analysis.quality_score - frame_analyses[i-1].quality_score)
                    
                    motion_estimate = (object_change + quality_change) / 2
                    motion_intensity.append(motion_estimate)
                else:
                    motion_intensity.append(0.0)
            
            return {
                'motion_intensity': np.array(motion_intensity),
                'average_motion': np.mean(motion_intensity) if motion_intensity else 0.0,
                'motion_variance': np.var(motion_intensity) if motion_intensity else 0.0
            }
            
        except Exception as e:
            logger.error(f"Motion feature extraction failed: {e}")
            return {}
    
    def _extract_scene_features(self, frame_analyses: List[FrameAnalysis]) -> Dict[str, List[str]]:
        """Extract scene and content classification features"""
        try:
            # Aggregate scene classifications
            scene_votes = {}
            for analysis in frame_analyses:
                for scene, confidence in analysis.scene_classification.items():
                    if scene not in scene_votes:
                        scene_votes[scene] = []
                    scene_votes[scene].append(confidence)
            
            # Calculate average confidences
            scene_confidences = {}
            for scene, votes in scene_votes.items():
                scene_confidences[scene] = np.mean(votes)
            
            # Get top scenes
            top_scenes = sorted(scene_confidences.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Classify overall content type
            content_type = self._classify_video_content(frame_analyses)
            
            return {
                'top_scenes': [scene[0] for scene in top_scenes],
                'scene_confidences': scene_confidences,
                'content_type': content_type,
                'primary_scene': top_scenes[0][0] if top_scenes else 'unknown'
            }
            
        except Exception as e:
            logger.error(f"Scene feature extraction failed: {e}")
            return {}
    
    def _classify_video_content(self, frame_analyses: List[FrameAnalysis]) -> str:
        """Classify overall video content type"""
        try:
            # Analyze object patterns and scene types
            object_counts = {}
            for analysis in frame_analyses:
                for obj in analysis.objects_detected:
                    obj_class = obj['class']
                    object_counts[obj_class] = object_counts.get(obj_class, 0) + 1
            
            # Simple heuristics for content classification
            if 'person' in object_counts and object_counts['person'] > len(frame_analyses) * 0.5:
                if any(obj in object_counts for obj in ['microphone', 'guitar', 'piano']):
                    return 'music_video'
                elif 'laptop' in object_counts or 'book' in object_counts:
                    return 'tutorial'
                else:
                    return 'vlog'
            elif any(obj in object_counts for obj in ['car', 'bicycle', 'motorcycle']):
                return 'travel'
            else:
                return 'general'
                
        except Exception as e:
            logger.error(f"Video content classification failed: {e}")
            return 'unknown'
    
    def _assess_video_quality(self, frame_analyses: List[FrameAnalysis], 
                             metadata: Dict[str, Any]) -> Dict[str, float]:
        """Assess overall video quality metrics"""
        try:
            # Frame quality statistics
            quality_scores = [analysis.quality_score for analysis in frame_analyses]
            
            # Resolution quality
            width = metadata.get('width', 0)
            height = metadata.get('height', 0)
            resolution_score = min((width * height) / (1920 * 1080), 1.0)  # Normalize to 1080p
            
            # Frame rate quality
            fps = metadata.get('fps', 0)
            fps_score = min(fps / 30, 1.0)  # Normalize to 30fps
            
            # Stability (consistency of quality)
            stability_score = 1.0 - (np.std(quality_scores) if quality_scores else 0.0)
            
            return {
                'average_frame_quality': np.mean(quality_scores) if quality_scores else 0.0,
                'quality_consistency': stability_score,
                'resolution_score': resolution_score,
                'frame_rate_score': fps_score,
                'overall_quality': np.mean([
                    np.mean(quality_scores) if quality_scores else 0.0,
                    resolution_score,
                    fps_score,
                    stability_score
                ])
            }
            
        except Exception as e:
            logger.error(f"Video quality assessment failed: {e}")
            return {}
    
    def _generate_video_fingerprint(self, frame_analyses: List[FrameAnalysis]) -> np.ndarray:
        """Generate unique video fingerprint for content identification"""
        try:
            # Collect key visual features
            key_features = []
            
            # Sample frames at regular intervals
            sample_indices = np.linspace(0, len(frame_analyses)-1, min(20, len(frame_analyses)), dtype=int)
            
            for idx in sample_indices:
                analysis = frame_analyses[idx]
                if len(analysis.visual_features) > 0:
                    # Use subset of features for fingerprint
                    key_features.append(analysis.visual_features[:128])  # First 128 features
            
            if not key_features:
                return np.array([])
            
            # Create compact fingerprint
            features_array = np.array(key_features)
            fingerprint = np.concatenate([
                np.mean(features_array, axis=0),
                np.std(features_array, axis=0)
            ])
            
            return fingerprint
            
        except Exception as e:
            logger.error(f"Video fingerprint generation failed: {e}")
            return np.array([])
    
    def _get_file_size(self, file_path: str) -> float:
        """Get file size in MB"""
        try:
            import os
            size_bytes = os.path.getsize(file_path)
            return size_bytes / (1024 * 1024)  # Convert to MB
        except:
            return 0.0
    
    def compare_video_similarity(self, features1: VideoFeatures, 
                                features2: VideoFeatures) -> Dict[str, float]:
        """
        Compare similarity between two videos
        """
        try:
            similarity_scores = {}
            
            # Fingerprint similarity
            if len(features1.fingerprint) > 0 and len(features2.fingerprint) > 0:
                cosine_sim = 1 - cosine(features1.fingerprint, features2.fingerprint)
                similarity_scores['fingerprint_similarity'] = float(cosine_sim)
            
            # Scene similarity
            scenes1 = set(features1.scene_features.get('top_scenes', []))
            scenes2 = set(features2.scene_features.get('top_scenes', []))
            scene_similarity = len(scenes1.intersection(scenes2)) / len(scenes1.union(scenes2)) if scenes1.union(scenes2) else 0
            similarity_scores['scene_similarity'] = float(scene_similarity)
            
            # Content type similarity
            content1 = features1.scene_features.get('content_type', 'unknown')
            content2 = features2.scene_features.get('content_type', 'unknown')
            content_similarity = 1.0 if content1 == content2 else 0.0
            similarity_scores['content_similarity'] = content_similarity
            
            # Overall similarity
            similarity_scores['overall_similarity'] = np.mean(list(similarity_scores.values()))
            
            return similarity_scores
            
        except Exception as e:
            logger.error(f"Video similarity comparison failed: {e}")
            return {}
    
    def extract_key_frames(self, video_path: str, num_frames: int = 10) -> List[Tuple[float, np.ndarray]]:
        """
        Extract key frames for thumbnail generation
        """
        try:
            cap = cv2.VideoCapture(video_path)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            # Calculate frame indices
            indices = np.linspace(0, frame_count-1, num_frames, dtype=int)
            
            key_frames = []
            for idx in indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                
                if ret:
                    timestamp = idx / fps
                    key_frames.append((timestamp, frame))
            
            cap.release()
            return key_frames
            
        except Exception as e:
            logger.error(f"Key frame extraction failed: {e}")
            return []
    
    def detect_video_anomalies(self, features: VideoFeatures) -> Dict[str, bool]:
        """
        Detect potential issues in video content
        """
        try:
            anomalies = {}
            
            # Quality issues
            avg_quality = features.quality_metrics.get('average_frame_quality', 0)
            anomalies['low_quality'] = avg_quality < 0.3
            
            # Resolution issues
            resolution_score = features.quality_metrics.get('resolution_score', 0)
            anomalies['low_resolution'] = resolution_score < 0.5
            
            # Frame rate issues
            fps_score = features.quality_metrics.get('frame_rate_score', 0)
            anomalies['low_frame_rate'] = fps_score < 0.5
            
            # Stability issues
            consistency = features.quality_metrics.get('quality_consistency', 1)
            anomalies['unstable_quality'] = consistency < 0.7
            
            # Duration issues
            duration = features.metadata.get('duration', 0)
            anomalies['too_short'] = duration < 10  # Less than 10 seconds
            anomalies['too_long'] = duration > 3600  # More than 1 hour
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Video anomaly detection failed: {e}")
            return {}
            self.optical_flow_params = dict(
                maxCorners=100,
                qualityLevel=0.3,
                minDistance=7,
                blockSize=7
            )
            
            # Feature detectors
            self.sift_detector = cv2.SIFT_create()
            self.orb_detector = cv2.ORB_create()
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenCV: {e}")
            raise
    
    def _load_object_detection_models(self) -> None:
        """Load pre-trained object detection models"""
        try:
            # YOLOv5 model
            self.yolo_model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
            self.yolo_model.eval()
            
        except Exception as e:
            logger.error(f"Failed to load object detection models: {e}")
            raise
    
    def _load_video_classification_models(self) -> None:
        """Load pre-trained video classification models"""
        # Implementation for video classification models
        pass
    
    def process(self, video_data: Union[str, np.ndarray], 
                config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive video processing pipeline
        
        Args:
            video_data: Video file path or numpy array
            config: Processing configuration parameters
            
        Returns:
            Complete video analysis results
        """
        try:
            # Load and preprocess video
            if isinstance(video_data, str):
                cap = cv2.VideoCapture(video_data)
                frames = self._extract_frames(cap, config)
                cap.release()
            else:
                frames = video_data
            
            # Extract comprehensive features
            features = self._extract_video_features(frames, config)
            
            # Generate video fingerprint
            fingerprint = self._generate_video_fingerprint(frames)
            
            # Perform scene analysis
            scene_analysis = self._analyze_scenes(frames, config)
            
            # Calculate quality metrics
            quality_metrics = self._assess_video_quality(frames)
            
            # Extract metadata
            metadata = self._extract_video_metadata(frames, video_data if isinstance(video_data, str) else None)
            
            # Generate thumbnails and keyframes
            thumbnails = self._generate_thumbnails(frames, config)
            
            return {
                'features': features,
                'fingerprint': fingerprint,
                'scene_analysis': scene_analysis,
                'quality_metrics': quality_metrics,
                'metadata': metadata,
                'thumbnails': thumbnails,
                'processing_config': config
            }
            
        except Exception as e:
            logger.error(f"Video processing failed: {e}")
            raise
    
    def _extract_frames(self, cap: cv2.VideoCapture, 
                       config: Dict[str, Any]) -> List[np.ndarray]:
        """Extract frames from video capture"""
        frames = []
        frame_skip = config.get('frame_skip', 1)
        max_frames = config.get('max_frames', 1000)
        
        frame_count = 0
        extracted_count = 0
        
        while cap.isOpened() and extracted_count < max_frames:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % frame_skip == 0:
                # Resize if necessary
                if frame.shape[:2] != self.max_resolution[::-1]:
                    frame = cv2.resize(frame, self.max_resolution)
                
                frames.append(frame)
                extracted_count += 1
            
            frame_count += 1
        
        return frames
    
    def _extract_video_features(self, frames: List[np.ndarray], 
                               config: Dict[str, Any]) -> VideoFeatures:
        """Extract comprehensive video features"""
        try:
            # Visual features from individual frames
            visual_features = self._extract_visual_features(frames)
            
            # Temporal features across frames
            temporal_features = self._extract_temporal_features(frames)
            
            # Motion features
            motion_features = self._extract_motion_features(frames)
            
            # Scene features
            scene_features = self._extract_scene_features(frames, config)
            
            # Quality metrics
            quality_metrics = self._assess_frame_quality(frames)
            
            # Generate fingerprint
            fingerprint = self._generate_visual_fingerprint(frames)
            
            # Metadata
            metadata = {
                'total_frames': len(frames),
                'estimated_fps': self.target_fps,
                'resolution': frames[0].shape[:2] if frames else (0, 0)
            }
            
            return VideoFeatures(
                visual_features=visual_features,
                temporal_features=temporal_features,
                motion_features=motion_features,
                scene_features=scene_features,
                quality_metrics=quality_metrics,
                fingerprint=fingerprint,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Video feature extraction failed: {e}")
            raise
    
    def _extract_visual_features(self, frames: List[np.ndarray]) -> Dict[str, np.ndarray]:
        """Extract visual features from frames"""
        features = {}
        
        if not frames:
            return features
        
        # Color histograms
        color_histograms = []
        for frame in frames:
            hist_b = cv2.calcHist([frame], [0], None, [256], [0, 256])
            hist_g = cv2.calcHist([frame], [1], None, [256], [0, 256])
            hist_r = cv2.calcHist([frame], [2], None, [256], [0, 256])
            hist = np.concatenate([hist_b.flatten(), hist_g.flatten(), hist_r.flatten()])
            color_histograms.append(hist)
        
        features['color_histograms'] = np.array(color_histograms)
        
        # Edge histograms
        edge_histograms = []
        for frame in frames:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            edge_hist = cv2.calcHist([edges], [0], None, [256], [0, 256])
            edge_histograms.append(edge_hist.flatten())
        
        features['edge_histograms'] = np.array(edge_histograms)
        
        # SIFT features for key frames
        if len(frames) <= 10:
            sift_features = self._extract_sift_features(frames)
            features['sift_features'] = sift_features
        
        return features
    
    def _extract_sift_features(self, frames: List[np.ndarray]) -> List[np.ndarray]:
        """Extract SIFT features from key frames"""
        sift_features = []
        
        for frame in frames:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            keypoints, descriptors = self.sift_detector.detectAndCompute(gray, None)
            
            if descriptors is not None:
                # Use bag of visual words or aggregate descriptors
                feature_vector = np.mean(descriptors, axis=0) if len(descriptors) > 0 else np.zeros(128)
            else:
                feature_vector = np.zeros(128)
            
            sift_features.append(feature_vector)
        
        return sift_features
    
    def _extract_temporal_features(self, frames: List[np.ndarray]) -> Dict[str, Any]:
        """Extract temporal features across frames"""
        features = {}
        
        if len(frames) < 2:
            return features
        
        # Frame difference analysis
        frame_diffs = []
        for i in range(1, len(frames)):
            diff = cv2.absdiff(
                cv2.cvtColor(frames[i-1], cv2.COLOR_BGR2GRAY),
                cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
            )
            frame_diffs.append(np.mean(diff))
        
        features['frame_differences'] = frame_diffs
        features['average_motion'] = np.mean(frame_diffs)
        features['motion_variance'] = np.var(frame_diffs)
        
        # Scene change detection
        scene_changes = self._detect_scene_changes(frames)
        features['scene_changes'] = scene_changes
        features['scene_count'] = len(scene_changes) + 1
        
        return features
    
    def _extract_motion_features(self, frames: List[np.ndarray]) -> Dict[str, np.ndarray]:
        """Extract motion-related features"""
        features = {}
        
        if len(frames) < 2:
            return features
        
        # Optical flow analysis
        optical_flows = []
        for i in range(1, len(frames)):
            prev_gray = cv2.cvtColor(frames[i-1], cv2.COLOR_BGR2GRAY)
            curr_gray = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
            
            flow = cv2.calcOpticalFlowPyrLK(prev_gray, curr_gray, **self.optical_flow_params)
            if flow[0] is not None:
                # Calculate motion magnitude
                motion_magnitude = np.sqrt(flow[0][:, 0]**2 + flow[0][:, 1]**2)
                optical_flows.append(np.mean(motion_magnitude))
            else:
                optical_flows.append(0.0)
        
        features['optical_flow'] = np.array(optical_flows)
        
        # Background subtraction for motion detection
        motion_areas = []
        for frame in frames:
            fg_mask = self.bg_subtractor.apply(frame)
            motion_area = np.sum(fg_mask > 0) / (frame.shape[0] * frame.shape[1])
            motion_areas.append(motion_area)
        
        features['motion_areas'] = np.array(motion_areas)
        
        return features
    
    def _extract_scene_features(self, frames: List[np.ndarray], 
                               config: Dict[str, Any]) -> Dict[str, List[str]]:
        """Extract scene classification and object detection features"""
        features = {
            'detected_objects': [],
            'scene_classifications': [],
            'frame_analyses': []
        }
        
        # Sample frames for analysis to avoid processing every frame
        sample_indices = np.linspace(0, len(frames)-1, min(10, len(frames)), dtype=int)
        
        for idx in sample_indices:
            frame = frames[idx]
            timestamp = idx / self.target_fps
            
            # Object detection
            objects = self._detect_objects(frame)
            features['detected_objects'].extend(objects)
            
            # Scene classification
            scene_class = self._classify_scene(frame)
            features['scene_classifications'].append(scene_class)
            
            # Create frame analysis
            frame_analysis = FrameAnalysis(
                frame_number=idx,
                timestamp=timestamp,
                objects_detected=objects,
                scene_classification=scene_class,
                visual_features=self._extract_frame_features(frame),
                quality_score=self._assess_single_frame_quality(frame)
            )
            features['frame_analyses'].append(frame_analysis)
        
        return features
    
    def _detect_objects(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Detect objects in a single frame using YOLO"""
        try:
            # Convert BGR to RGB for YOLO
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Run YOLO detection
            results = self.yolo_model(rgb_frame)
            
            # Parse results
            objects = []
            for *box, conf, cls in results.xyxy[0].cpu().numpy():
                if conf > 0.5:  # Confidence threshold
                    objects.append({
                        'class': self.yolo_model.names[int(cls)],
                        'confidence': float(conf),
                        'bbox': [float(x) for x in box]
                    })
            
            return objects
            
        except Exception as e:
            logger.error(f"Object detection failed: {e}")
            return []
    
    def _classify_scene(self, frame: np.ndarray) -> Dict[str, float]:
        """Classify scene content using CLIP"""
        try:
            # Convert frame to PIL Image
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)
            
            # Scene categories
            scene_categories = [
                "indoor scene", "outdoor scene", "nature landscape", 
                "urban environment", "concert hall", "studio recording",
                "street performance", "home setting", "professional stage"
            ]
            
            # Process with CLIP
            inputs = self.clip_processor(
                text=scene_categories, 
                images=pil_image, 
                return_tensors="pt", 
                padding=True
            )
            
            outputs = self.clip_model(**inputs)
            logits_per_image = outputs.logits_per_image
            probs = logits_per_image.softmax(dim=1)
            
            # Return probabilities for each scene category
            return dict(zip(scene_categories, probs[0].detach().numpy().tolist()))
            
        except Exception as e:
            logger.error(f"Scene classification failed: {e}")
            return {}
    
    def _extract_frame_features(self, frame: np.ndarray) -> np.ndarray:
        """Extract features from a single frame"""
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Calculate various features
        features = []
        
        # Mean and std of pixel intensities
        features.extend([np.mean(gray), np.std(gray)])
        
        # Edge density
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
        features.append(edge_density)
        
        # Texture features (LBP-like)
        texture_score = self._calculate_texture_score(gray)
        features.append(texture_score)
        
        return np.array(features)
    
    def _calculate_texture_score(self, gray_image: np.ndarray) -> float:
        """Calculate texture score for image"""
        # Simple texture measure using local variance
        kernel = np.ones((3, 3)) / 9
        mean_image = cv2.filter2D(gray_image.astype(np.float32), -1, kernel)
        variance_image = cv2.filter2D((gray_image.astype(np.float32) - mean_image)**2, -1, kernel)
        
        return float(np.mean(variance_image))
    
    def _detect_scene_changes(self, frames: List[np.ndarray]) -> List[int]:
        """Detect scene changes between frames"""
        scene_changes = []
        threshold = 0.3  # Adjust based on requirements
        
        for i in range(1, len(frames)):
            # Calculate histogram difference
            hist1 = cv2.calcHist([frames[i-1]], [0, 1, 2], None, [50, 50, 50], [0, 256, 0, 256, 0, 256])
            hist2 = cv2.calcHist([frames[i]], [0, 1, 2], None, [50, 50, 50], [0, 256, 0, 256, 0, 256])
            
            # Compare histograms
            correlation = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
            
            if correlation < threshold:
                scene_changes.append(i)
        
        return scene_changes
    
    def _generate_video_fingerprint(self, frames: List[np.ndarray]) -> np.ndarray:
        """Generate video fingerprint for similarity matching"""
        try:
            if not frames:
                return np.array([])
            
            # Sample key frames
            num_samples = min(16, len(frames))
            sample_indices = np.linspace(0, len(frames)-1, num_samples, dtype=int)
            
            fingerprint_parts = []
            
            for idx in sample_indices:
                frame = frames[idx]
                
                # Generate perceptual hash
                pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                phash = imagehash.phash(pil_image, hash_size=8)
                fingerprint_parts.append(phash.hash.flatten())
            
            # Combine all hashes
            fingerprint = np.concatenate(fingerprint_parts)
            
            return fingerprint
            
        except Exception as e:
            logger.error(f"Video fingerprint generation failed: {e}")
            return np.array([])
    
    def _generate_visual_fingerprint(self, frames: List[np.ndarray]) -> np.ndarray:
        """Generate visual fingerprint using advanced techniques"""
        if not frames:
            return np.array([])
        
        # Use first, middle, and last frames for fingerprinting
        key_indices = [0, len(frames)//2, len(frames)-1] if len(frames) > 2 else [0]
        
        fingerprint_components = []
        
        for idx in key_indices:
            frame = frames[idx]
            
            # Resize to standard size for consistent fingerprinting
            resized = cv2.resize(frame, (64, 64))
            
            # Convert to grayscale
            gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            
            # Create binary hash based on DCT
            dct = cv2.dct(gray.astype(np.float32))
            dct_low = dct[:8, :8]
            median = np.median(dct_low)
            binary_hash = (dct_low > median).astype(int).flatten()
            
            fingerprint_components.append(binary_hash)
        
        return np.concatenate(fingerprint_components)
    
    def _assess_video_quality(self, frames: List[np.ndarray]) -> Dict[str, float]:
        """Assess overall video quality"""
        if not frames:
            return {}
        
        quality_metrics = {}
        
        # Average frame quality
        frame_qualities = [self._assess_single_frame_quality(frame) for frame in frames]
        quality_metrics['average_quality'] = np.mean(frame_qualities)
        quality_metrics['quality_variance'] = np.var(frame_qualities)
        
        # Temporal consistency
        temporal_consistency = self._calculate_temporal_consistency(frames)
        quality_metrics['temporal_consistency'] = temporal_consistency
        
        # Motion smoothness
        motion_smoothness = self._calculate_motion_smoothness(frames)
        quality_metrics['motion_smoothness'] = motion_smoothness
        
        # Overall score
        overall_score = (
            quality_metrics['average_quality'] * 0.4 +
            quality_metrics['temporal_consistency'] * 0.3 +
            quality_metrics['motion_smoothness'] * 0.3
        )
        quality_metrics['overall_score'] = overall_score
        
        return quality_metrics
    
    def _assess_single_frame_quality(self, frame: np.ndarray) -> float:
        """Assess quality of a single frame"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Sharpness (Laplacian variance)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        sharpness_score = min(laplacian_var / 1000.0, 1.0)  # Normalize
        
        # Contrast (standard deviation)
        contrast_score = min(np.std(gray) / 128.0, 1.0)  # Normalize
        
        # Brightness distribution
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        brightness_score = 1.0 - abs(0.5 - np.argmax(hist) / 256.0)
        
        # Combined quality score
        quality_score = (sharpness_score * 0.4 + contrast_score * 0.3 + brightness_score * 0.3)
        
        return quality_score
    
    def _calculate_temporal_consistency(self, frames: List[np.ndarray]) -> float:
        """Calculate temporal consistency across frames"""
        if len(frames) < 2:
            return 1.0
        
        consistencies = []
        
        for i in range(1, len(frames)):
            prev_frame = cv2.cvtColor(frames[i-1], cv2.COLOR_BGR2GRAY)
            curr_frame = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
            
            # Calculate structural similarity
            correlation = cv2.matchTemplate(prev_frame, curr_frame, cv2.TM_CCOEFF_NORMED)[0, 0]
            consistencies.append(max(0, correlation))
        
        return np.mean(consistencies)
    
    def _calculate_motion_smoothness(self, frames: List[np.ndarray]) -> float:
        """Calculate motion smoothness across frames"""
        if len(frames) < 3:
            return 1.0
        
        motion_diffs = []
        
        for i in range(2, len(frames)):
            # Calculate motion between consecutive frame pairs
            motion1 = self._calculate_frame_motion(frames[i-2], frames[i-1])
            motion2 = self._calculate_frame_motion(frames[i-1], frames[i])
            
            # Motion difference indicates smoothness
            motion_diff = abs(motion1 - motion2)
            motion_diffs.append(motion_diff)
        
        # Invert and normalize to get smoothness score
        avg_motion_diff = np.mean(motion_diffs)
        smoothness = max(0, 1.0 - avg_motion_diff / 100.0)  # Normalize
        
        return smoothness
    
    def _calculate_frame_motion(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        """Calculate motion between two frames"""
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        
        # Frame difference
        diff = cv2.absdiff(gray1, gray2)
        motion_amount = np.mean(diff)
        
        return motion_amount
    
    def _assess_frame_quality(self, frames: List[np.ndarray]) -> Dict[str, float]:
        """Assess quality metrics for all frames"""
        qualities = [self._assess_single_frame_quality(frame) for frame in frames]
        
        return {
            'min_quality': np.min(qualities) if qualities else 0.0,
            'max_quality': np.max(qualities) if qualities else 0.0,
            'mean_quality': np.mean(qualities) if qualities else 0.0,
            'std_quality': np.std(qualities) if qualities else 0.0
        }
    
    def _extract_video_metadata(self, frames: List[np.ndarray], 
                               video_path: Optional[str] = None) -> Dict[str, Any]:
        """Extract video metadata"""
        metadata = {
            'total_frames': len(frames),
            'estimated_duration': len(frames) / self.target_fps,
            'resolution': frames[0].shape[:2] if frames else (0, 0),
            'channels': frames[0].shape[2] if frames and len(frames[0].shape) > 2 else 0
        }
        
        if video_path and video_path.endswith(('.mp4', '.avi', '.mov', '.mkv')):
            try:
                # Use moviepy for additional metadata
                clip = mp.VideoFileClip(video_path)
                metadata.update({
                    'actual_duration': clip.duration,
                    'actual_fps': clip.fps,
                    'audio_present': clip.audio is not None
                })
                clip.close()
            except Exception as e:
                logger.warning(f"Could not extract video metadata: {e}")
        
        return metadata
    
    def _generate_thumbnails(self, frames: List[np.ndarray], 
                           config: Dict[str, Any]) -> List[np.ndarray]:
        """Generate thumbnails and key frames"""
        if not frames:
            return []
        
        num_thumbnails = config.get('num_thumbnails', 5)
        thumbnail_size = config.get('thumbnail_size', (320, 240))
        
        # Select frames at regular intervals
        if len(frames) <= num_thumbnails:
            selected_frames = frames
        else:
            indices = np.linspace(0, len(frames)-1, num_thumbnails, dtype=int)
            selected_frames = [frames[i] for i in indices]
        
        # Resize to thumbnail size
        thumbnails = []
        for frame in selected_frames:
            thumbnail = cv2.resize(frame, thumbnail_size)
            thumbnails.append(thumbnail)
        
        return thumbnails
    
    def calculate_similarity(self, fingerprint1: np.ndarray, 
                           fingerprint2: np.ndarray) -> float:
        """Calculate similarity between two video fingerprints"""
        try:
            if len(fingerprint1) == 0 or len(fingerprint2) == 0:
                return 0.0
            
            # Ensure same length
            min_length = min(len(fingerprint1), len(fingerprint2))
            fp1 = fingerprint1[:min_length]
            fp2 = fingerprint2[:min_length]
            
            # Calculate Hamming distance for binary fingerprints
            if fp1.dtype == bool or np.all(np.isin(fp1, [0, 1])):
                hamming_distance = np.sum(fp1 != fp2) / min_length
                similarity = 1.0 - hamming_distance
            else:
                # Use cosine similarity for continuous features
                similarity = 1.0 - cosine(fp1, fp2)
            
            return float(max(0.0, similarity))
            
        except Exception as e:
            logger.error(f"Video similarity calculation failed: {e}")
            return 0.0
    
    def _analyze_scenes(self, frames: List[np.ndarray], 
                       config: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive scene analysis"""
        scene_analysis = {
            'scene_boundaries': self._detect_scene_changes(frames),
            'dominant_colors': self._extract_dominant_colors(frames),
            'lighting_analysis': self._analyze_lighting(frames),
            'composition_analysis': self._analyze_composition(frames)
        }
        
        return scene_analysis
    
    def _extract_dominant_colors(self, frames: List[np.ndarray]) -> List[List[Tuple[int, int, int]]]:
        """Extract dominant colors from frames"""
        dominant_colors = []
        
        for frame in frames[::max(1, len(frames)//10)]:  # Sample frames
            # Reshape frame for K-means
            pixel_data = frame.reshape(-1, 3)
            
            # Use K-means to find dominant colors
            kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
            kmeans.fit(pixel_data)
            
            # Get dominant colors
            colors = kmeans.cluster_centers_.astype(int)
            dominant_colors.append([tuple(color) for color in colors])
        
        return dominant_colors
    
    def _analyze_lighting(self, frames: List[np.ndarray]) -> Dict[str, float]:
        """Analyze lighting conditions in video"""
        brightness_values = []
        contrast_values = []
        
        for frame in frames[::max(1, len(frames)//20)]:  # Sample frames
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            brightness = np.mean(gray)
            contrast = np.std(gray)
            
            brightness_values.append(brightness)
            contrast_values.append(contrast)
        
        return {
            'average_brightness': np.mean(brightness_values),
            'brightness_variance': np.var(brightness_values),
            'average_contrast': np.mean(contrast_values),
            'contrast_variance': np.var(contrast_values)
        }
    
    def _analyze_composition(self, frames: List[np.ndarray]) -> Dict[str, Any]:
        """Analyze video composition and framing"""
        composition_analysis = {
            'rule_of_thirds_score': [],
            'center_weighted_score': [],
            'edge_distribution': []
        }
        
        for frame in frames[::max(1, len(frames)//10)]:  # Sample frames
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Rule of thirds analysis
            thirds_score = self._calculate_rule_of_thirds_score(gray)
            composition_analysis['rule_of_thirds_score'].append(thirds_score)
            
            # Center-weighted composition
            center_score = self._calculate_center_weighted_score(gray)
            composition_analysis['center_weighted_score'].append(center_score)
            
            # Edge distribution
            edges = cv2.Canny(gray, 50, 150)
            edge_dist = self._calculate_edge_distribution(edges)
            composition_analysis['edge_distribution'].append(edge_dist)
        
        # Average the scores
        for key in composition_analysis:
            if composition_analysis[key]:
                composition_analysis[key] = np.mean(composition_analysis[key])
        
        return composition_analysis
    
    def _calculate_rule_of_thirds_score(self, gray_image: np.ndarray) -> float:
        """Calculate how well the image follows rule of thirds"""
        height, width = gray_image.shape
        
        # Define thirds lines
        v_thirds = [width // 3, 2 * width // 3]
        h_thirds = [height // 3, 2 * height // 3]
        
        # Calculate gradient magnitude
        grad_x = cv2.Sobel(gray_image, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray_image, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        
        # Score based on content along thirds lines
        score = 0
        for v_line in v_thirds:
            score += np.mean(gradient_magnitude[:, max(0, v_line-2):min(width, v_line+3)])
        for h_line in h_thirds:
            score += np.mean(gradient_magnitude[max(0, h_line-2):min(height, h_line+3), :])
        
        # Normalize score
        return score / (np.mean(gradient_magnitude) * 4 + 1e-10)
    
    def _calculate_center_weighted_score(self, gray_image: np.ndarray) -> float:
        """Calculate center-weighted composition score"""
        height, width = gray_image.shape
        center_y, center_x = height // 2, width // 2
        
        # Create distance mask from center
        y, x = np.ogrid[:height, :width]
        distance_from_center = np.sqrt((y - center_y)**2 + (x - center_x)**2)
        max_distance = np.sqrt(center_y**2 + center_x**2)
        
        # Weight by inverse distance from center
        weights = 1 - (distance_from_center / max_distance)
        
        # Calculate weighted average intensity
        weighted_score = np.sum(gray_image * weights) / np.sum(weights)
        
        return weighted_score / 255.0  # Normalize to 0-1
    
    def _calculate_edge_distribution(self, edge_image: np.ndarray) -> Dict[str, float]:
        """Calculate distribution of edges across image regions"""
        height, width = edge_image.shape
        
        # Divide image into regions
        regions = {
            'top_left': edge_image[:height//2, :width//2],
            'top_right': edge_image[:height//2, width//2:],
            'bottom_left': edge_image[height//2:, :width//2],
            'bottom_right': edge_image[height//2:, width//2:],
            'center': edge_image[height//4:3*height//4, width//4:3*width//4]
        }
        
        # Calculate edge density for each region
        edge_distribution = {}
        for region_name, region in regions.items():
            edge_density = np.sum(region > 0) / region.size
            edge_distribution[region_name] = edge_density
        
        return edge_distribution
