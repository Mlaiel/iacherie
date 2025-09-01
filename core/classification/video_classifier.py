"""Video Content Classification System

Advanced AI-powered video classification for content protection and analysis.
Provides scene detection, object recognition, quality assessment, and similarity matching.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import cv2
import numpy as np
import torch
import torchvision.transforms as transforms
from typing import Dict, List, Optional, Tuple, Any
import logging
from pathlib import Path
import hashlib
from PIL import Image
import imagehash
from transformers import CLIPProcessor, CLIPModel
import face_recognition
from scipy.spatial.distance import cosine

from ..engines.ml_engine import MLEngine
from ..processors.video_processor import VideoProcessor
from ...utils.cache_manager import cache_result
from ...utils.metrics import track_performance
from ...config.settings import get_settings

logger = logging.getLogger(__name__)


class VideoContentClassifier:
    """
    Enterprise-grade video content classification system.
    
    Features:
    - Scene and activity detection
    - Object and person recognition
    - Content type classification (music video, vlog, tutorial, etc.)
    - Quality assessment and technical analysis
    - Similarity matching for copyright detection
    - Frame-level analysis and summarization
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
Initialize video classifier with ML models."""
        self.settings = get_settings()
        self.ml_engine = MLEngine()
        self.video_processor = VideoProcessor()
        
        # Model configurations
        self.scene_model = None
        self.object_model = None
        self.content_type_model = None
        self.quality_model = None
        
        # CLIP model for multimodal understanding
        self.clip_processor = None
        self.clip_model = None
        
        # Classification thresholds
        self.confidence_threshold = 0.75
        self.similarity_threshold = 0.85
        self.scene_change_threshold = 0.3
        
        self._initialize_models(model_path)
        self._setup_feature_extractors()
        
    def _initialize_models(self, model_path: Optional[str] = None) -> None:
        """
Load pre-trained classification models."""
        try:
            # Load CLIP model for multimodal analysis
            self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            
            # Initialize YOLO for object detection
            self.yolo_model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
            
            logger.info("Video classification models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading video classification models: {e}")
            self._load_fallback_models()
    
    def _load_fallback_models(self) -> None:
        """Load fallback models if primary models fail."""
        try:
            # Use OpenCV cascades as fallback
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            logger.info("Fallback video models loaded")
            
        except Exception as e:
            logger.error(f"Error loading fallback models: {e}")
    
    def _setup_feature_extractors(self) -> None:
        """Initialize video feature extractors."""
        try:
            # Color histogram extractor
            self.hist_bins = 256
            
            # Optical flow extractor
            self.flow_params = dict(
                pyr_scale=0.5,
                levels=3,
                winsize=15,
                iterations=3,
                poly_n=5,
                poly_sigma=1.2,
                flags=0
            )
            
            # Edge detection parameters
            self.edge_params = {
                'low_threshold': 50,
                'high_threshold': 150,
                'aperture_size': 3
            }
            
            logger.info("Video feature extractors initialized")
            
        except Exception as e:
            logger.error(f"Error setting up video feature extractors: {e}")
    
    @track_performance
    @cache_result(ttl=3600)
    async def classify_video(
        self,
        video_path: str,
        analysis_type: str = "complete",
        sample_rate: int = 1
    ) -> Dict[str, Any]:
        """
        Classify video content with comprehensive analysis.
        
        Args:
            video_path: Path to video file
            analysis_type: Type of analysis ('scene', 'object', 'content', 'quality', 'complete')
            sample_rate: Frame sampling rate (1 = every frame, 2 = every 2nd frame, etc.)
            
        Returns:
            Dictionary containing classification results
        """
        try:
            # Load and preprocess video
            video_data = await self.video_processor.load_video(video_path, sample_rate)
            
            results = {
                'file_path': video_path,
                'analysis_type': analysis_type,
                'timestamp': np.datetime64('now'),
                'video_info': video_data['metadata'],
                'frame_count': len(video_data['frames'])
            }
            
            # Extract frame features
            frame_features = await self._extract_frame_features(video_data['frames'])
            results['frame_features'] = frame_features
            
            # Perform requested analysis
            if analysis_type in ['scene', 'complete']:
                scene_results = await self._detect_scenes(video_data['frames'], frame_features)
                results['scenes'] = scene_results
                
            if analysis_type in ['object', 'complete']:
                object_results = await self._detect_objects(video_data['frames'])
                results['objects'] = object_results
                
            if analysis_type in ['content', 'complete']:
                content_results = await self._classify_content_type(video_data['frames'], frame_features)
                results['content_type'] = content_results
                
            if analysis_type in ['quality', 'complete']:
                quality_results = await self._assess_video_quality(video_data, frame_features)
                results['quality'] = quality_results
                
            if analysis_type in ['similarity', 'complete']:
                similarity_results = await self._compute_video_hash(video_data['frames'])
                results['similarity_hash'] = similarity_results
            
            # Face detection and recognition
            if analysis_type in ['faces', 'complete']:
                face_results = await self._detect_faces(video_data['frames'])
                results['faces'] = face_results
            
            # Motion analysis
            if analysis_type in ['motion', 'complete']:
                motion_results = await self._analyze_motion(video_data['frames'])
                results['motion'] = motion_results
            
            # Overall confidence score
            results['confidence'] = self._calculate_overall_confidence(results)
            
            logger.info(f"Video classification completed for {video_path}")
            return results
            
        except Exception as e:
            logger.error(f"Error classifying video {video_path}: {e}")
            raise
    
    async def _extract_frame_features(self, frames: List[np.ndarray]) -> List[Dict[str, Any]]:
        """Extract features from video frames."""
        frame_features = []
        
        for i, frame in enumerate(frames):
            try:
                features = {}
                
                # Color histogram
                features['color_hist'] = self._extract_color_histogram(frame)
                
                # Edge density
                features['edge_density'] = self._calculate_edge_density(frame)
                
                # Brightness and contrast
                features['brightness'] = float(np.mean(frame))
                features['contrast'] = float(np.std(frame))
                
                # Texture features (Local Binary Pattern)
                features['texture'] = self._extract_texture_features(frame)
                
                # Dominant colors
                features['dominant_colors'] = self._extract_dominant_colors(frame)
                
                # Frame complexity (entropy)
                features['complexity'] = self._calculate_frame_complexity(frame)
                
                frame_features.append(features)
                
            except Exception as e:
                logger.warning(f"Error extracting features from frame {i}: {e}")
                frame_features.append({'error': str(e)})
        
        return frame_features
    
    async def _detect_scenes(
        self,
        frames: List[np.ndarray],
        frame_features: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Detect scene changes and boundaries in video."""
        try:
            scene_changes = []
            scenes = []
            
            if len(frames) < 2:
                return {'scenes': [{'start_frame': 0, 'end_frame': len(frames)-1}]}
            
            # Calculate frame differences
            for i in range(1, len(frames)):
                if 'color_hist' in frame_features[i] and 'color_hist' in frame_features[i-1]:
                    hist1 = frame_features[i-1]['color_hist']
                    hist2 = frame_features[i]['color_hist']
                    
                    # Calculate histogram correlation
                    correlation = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
                    
                    # Detect scene change
                    if correlation < (1 - self.scene_change_threshold):
                        scene_changes.append(i)
            
            # Create scene segments
            start_frame = 0
            for change_frame in scene_changes:
                scenes.append({
                    'start_frame': start_frame,
                    'end_frame': change_frame - 1,
                    'duration_frames': change_frame - start_frame,
                    'scene_type': self._classify_scene_type(frames[start_frame:change_frame])
                })
                start_frame = change_frame
            
            # Add final scene
            scenes.append({
                'start_frame': start_frame,
                'end_frame': len(frames) - 1,
                'duration_frames': len(frames) - start_frame,
                'scene_type': self._classify_scene_type(frames[start_frame:])
            })
            
            return {
                'scene_count': len(scenes),
                'scene_changes': scene_changes,
                'scenes': scenes,
                'average_scene_length': np.mean([s['duration_frames'] for s in scenes])
            }
            
        except Exception as e:
            logger.error(f"Error in scene detection: {e}")
            return {'error': str(e)}
    
    async def _detect_objects(self, frames: List[np.ndarray]) -> Dict[str, Any]:
        """Detect objects in video frames using YOLO."""
        try:
            all_detections = []
            object_counts = {}
            
            # Sample frames for object detection (every 10th frame to reduce computation)
            sample_frames = frames[::max(1, len(frames) // 10)]
            
            for i, frame in enumerate(sample_frames):
                # Convert BGR to RGB for YOLO
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Run YOLO detection
                results = self.yolo_model(rgb_frame)
                
                # Parse results
                detections = []
                for *box, conf, cls in results.xyxy[0].cpu().numpy():
                    if conf > 0.5:  # Confidence threshold
                        class_name = self.yolo_model.names[int(cls)]
                        detections.append({
                            'class': class_name,
                            'confidence': float(conf),
                            'bbox': [float(x) for x in box]
                        })
                        
                        # Count objects
                        object_counts[class_name] = object_counts.get(class_name, 0) + 1
                
                all_detections.append({
                    'frame_index': i * max(1, len(frames) // 10),
                    'detections': detections
                })
            
            # Find most common objects
            most_common = sorted(object_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                'total_detections': sum(len(d['detections']) for d in all_detections),
                'unique_objects': len(object_counts),
                'object_counts': object_counts,
                'most_common_objects': most_common,
                'frame_detections': all_detections
            }
            
        except Exception as e:
            logger.error(f"Error in object detection: {e}")
            return {'error': str(e)}
    
    async def _classify_content_type(
        self,
        frames: List[np.ndarray],
        frame_features: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Classify video content type (music video, vlog, tutorial, etc.)."""
        try:
            # Extract representative frames
            sample_frames = frames[::max(1, len(frames) // 5)]  # 5 sample frames
            
            content_indicators = {
                'music_video': 0,
                'vlog': 0,
                'tutorial': 0,
                'performance': 0,
                'interview': 0,
                'gameplay': 0,
                'animation': 0
            }
            
            # Analyze sample frames
            for frame in sample_frames:
                # Convert to PIL Image for CLIP
                pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                
                # Use CLIP to analyze content
                if self.clip_model and self.clip_processor:
                    # Define content type descriptions
                    descriptions = [
                        "a music video with performers and instruments",
                        "a vlog with a person talking to camera",
                        "an educational tutorial or how-to video",
                        "a live performance or concert",
                        "an interview or conversation",
                        "video game gameplay footage",
                        "animated content or cartoon"
                    ]
                    
                    inputs = self.clip_processor(
                        text=descriptions,
                        images=pil_image,
                        return_tensors="pt",
                        padding=True
                    )
                    
                    outputs = self.clip_model(**inputs)
                    probs = outputs.logits_per_image.softmax(dim=1)[0]
                    
                    # Update content indicators
                    content_types = list(content_indicators.keys())
                    for i, prob in enumerate(probs):
                        content_indicators[content_types[i]] += float(prob)
            
            # Normalize scores
            total_score = sum(content_indicators.values())
            if total_score > 0:
                content_probabilities = {
                    k: v / total_score for k, v in content_indicators.items()
                }
            else:
                content_probabilities = content_indicators
            
            # Determine primary content type
            primary_type = max(content_probabilities, key=content_probabilities.get)
            confidence = content_probabilities[primary_type]
            
            return {
                'primary_type': primary_type,
                'confidence': confidence,
                'probabilities': content_probabilities,
                'secondary_types': sorted(
                    content_probabilities.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[1:4]  # Top 3 secondary types
            }
            
        except Exception as e:
            logger.error(f"Error in content type classification: {e}")
            return {'error': str(e)}
    
    async def _assess_video_quality(
        self,
        video_data: Dict[str, Any],
        frame_features: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Assess video quality and technical characteristics."""
        try:
            quality_metrics = {}
            frames = video_data['frames']
            metadata = video_data['metadata']
            
            # Resolution analysis
            height, width = frames[0].shape[:2]
            quality_metrics['resolution'] = {
                'width': width,
                'height': height,
                'total_pixels': width * height,
                'aspect_ratio': width / height
            }
            
            # Frame rate from metadata
            quality_metrics['frame_rate'] = metadata.get('fps', 30)
            
            # Brightness consistency
            brightness_values = [f.get('brightness', 0) for f in frame_features if 'brightness' in f]
            if brightness_values:
                quality_metrics['brightness'] = {
                    'mean': float(np.mean(brightness_values)),
                    'std': float(np.std(brightness_values)),
                    'consistency': 1.0 - (np.std(brightness_values) / 255.0)
                }
            
            # Contrast analysis
            contrast_values = [f.get('contrast', 0) for f in frame_features if 'contrast' in f]
            if contrast_values:
                quality_metrics['contrast'] = {
                    'mean': float(np.mean(contrast_values)),
                    'std': float(np.std(contrast_values))
                }
            
            # Blur detection
            blur_scores = []
            for frame in frames[::5]:  # Sample every 5th frame
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
                blur_scores.append(blur_score)
            
            quality_metrics['sharpness'] = {
                'mean_blur_score': float(np.mean(blur_scores)),
                'sharpness_grade': self._grade_sharpness(np.mean(blur_scores))
            }
            
            # Noise estimation
            noise_scores = []
            for frame in frames[::10]:  # Sample every 10th frame
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                noise = np.std(gray)
                noise_scores.append(noise)
            
            quality_metrics['noise'] = {
                'mean_noise': float(np.mean(noise_scores)),
                'noise_grade': self._grade_noise(np.mean(noise_scores))
            }
            
            # Overall quality score
            quality_score = self._calculate_video_quality_score(quality_metrics)
            
            return {
                'quality_score': quality_score,
                'quality_grade': self._grade_video_quality(quality_score),
                'metrics': quality_metrics,
                'recommendations': self._generate_video_quality_recommendations(quality_metrics)
            }
            
        except Exception as e:
            logger.error(f"Error in video quality assessment: {e}")
            return {'error': str(e)}
    
    async def _compute_video_hash(self, frames: List[np.ndarray]) -> Dict[str, Any]:
        """Compute perceptual hash for video similarity matching."""
        try:
            # Sample key frames for hashing
            key_frames = frames[::max(1, len(frames) // 8)]  # 8 key frames
            
            frame_hashes = []
            for frame in key_frames:
                # Convert to PIL Image
                pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                
                # Calculate perceptual hash
                phash = imagehash.phash(pil_image)
                dhash = imagehash.dhash(pil_image)
                
                frame_hashes.append({
                    'phash': str(phash),
                    'dhash': str(dhash)
                })
            
            # Create video fingerprint
            video_fingerprint = self._create_video_fingerprint(key_frames)
            
            # Temporal hash based on frame differences
            temporal_hash = self._compute_temporal_hash(frames)
            
            return {
                'frame_hashes': frame_hashes,
                'video_fingerprint': video_fingerprint,
                'temporal_hash': temporal_hash,
                'key_frame_count': len(key_frames),
                'hash_algorithm': 'perceptual_video_hash_v2'
            }
            
        except Exception as e:
            logger.error(f"Error computing video hash: {e}")
            return {'error': str(e)}
    
    async def _detect_faces(self, frames: List[np.ndarray]) -> Dict[str, Any]:
        """Detect and recognize faces in video frames."""
        try:
            face_detections = []
            unique_faces = []
            face_encodings = []
            
            # Sample frames for face detection
            sample_frames = frames[::max(1, len(frames) // 20)]  # Every 20th frame
            
            for i, frame in enumerate(sample_frames):
                # Convert to RGB for face_recognition
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Detect faces
                face_locations = face_recognition.face_locations(rgb_frame)
                encodings = face_recognition.face_encodings(rgb_frame, face_locations)
                
                frame_faces = []
                for location, encoding in zip(face_locations, encodings):
                    # Check if this is a new face
                    is_new_face = True
                    face_id = len(unique_faces)
                    
                    for j, known_encoding in enumerate(face_encodings):
                        if face_recognition.compare_faces([known_encoding], encoding, tolerance=0.6)[0]:
                            is_new_face = False
                            face_id = j
                            break
                    
                    if is_new_face:
                        face_encodings.append(encoding)
                        unique_faces.append({
                            'face_id': face_id,
                            'first_appearance': i * max(1, len(frames) // 20),
                            'encoding': encoding.tolist()
                        })
                    
                    frame_faces.append({
                        'face_id': face_id,
                        'location': location,
                        'confidence': 0.95  # Default confidence for face_recognition
                    })
                
                face_detections.append({
                    'frame_index': i * max(1, len(frames) // 20),
                    'faces': frame_faces
                })
            
            return {
                'unique_face_count': len(unique_faces),
                'total_face_detections': sum(len(d['faces']) for d in face_detections),
                'unique_faces': unique_faces,
                'frame_detections': face_detections
            }
            
        except Exception as e:
            logger.error(f"Error in face detection: {e}")
            return {'error': str(e)}
    
    async def _analyze_motion(self, frames: List[np.ndarray]) -> Dict[str, Any]:
        """Analyze motion and camera movement in video."""
        try:
            if len(frames) < 2:
                return {'error': 'Not enough frames for motion analysis'}
            
            motion_vectors = []
            motion_magnitudes = []
            
            # Convert first frame to grayscale
            prev_gray = cv2.cvtColor(frames[0], cv2.COLOR_BGR2GRAY)
            
            for i in range(1, len(frames)):
                # Convert current frame to grayscale
                curr_gray = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
                
                # Calculate optical flow
                flow = cv2.calcOpticalFlowPyrLK(prev_gray, curr_gray, **self.flow_params)
                
                if flow is not None:
                    # Calculate motion magnitude
                    magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
                    mean_magnitude = np.mean(magnitude)
                    motion_magnitudes.append(mean_magnitude)
                    
                    # Store motion vector summary
                    motion_vectors.append({
                        'frame': i,
                        'mean_magnitude': float(mean_magnitude),
                        'max_magnitude': float(np.max(magnitude)),
                        'motion_density': float(np.sum(magnitude > 1.0) / magnitude.size)
                    })
                
                prev_gray = curr_gray
            
            # Motion statistics
            motion_stats = {
                'mean_motion': float(np.mean(motion_magnitudes)),
                'max_motion': float(np.max(motion_magnitudes)),
                'motion_variance': float(np.var(motion_magnitudes)),
                'high_motion_frames': sum(1 for m in motion_magnitudes if m > np.mean(motion_magnitudes) * 1.5),
                'motion_type': self._classify_motion_type(motion_magnitudes)
            }
            
            return {
                'motion_statistics': motion_stats,
                'motion_vectors': motion_vectors,
                'frame_count_analyzed': len(motion_vectors)
            }
            
        except Exception as e:
            logger.error(f"Error in motion analysis: {e}")
            return {'error': str(e)}
    
    def _extract_color_histogram(self, frame: np.ndarray) -> np.ndarray:
        """Extract color histogram from frame."""
        # Convert to HSV for better color representation
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Calculate histogram
        hist = cv2.calcHist([hsv], [0, 1, 2], None, [50, 60, 60], [0, 180, 0, 256, 0, 256])
        
        # Normalize histogram
        cv2.normalize(hist, hist)
        
        return hist
    
    def _calculate_edge_density(self, frame: np.ndarray) -> float:
        """
Calculate edge density in frame."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, **self.edge_params)
        edge_density = np.sum(edges > 0) / edges.size
        return float(edge_density)
    
    def _extract_texture_features(self, frame: np.ndarray) -> Dict[str, float]:
        """
Extract texture features using Local Binary Pattern."""
        try:
            from skimage import feature
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Local Binary Pattern
            lbp = feature.local_binary_pattern(gray, 24, 3, method='uniform')
            
            # Calculate LBP histogram
            lbp_hist, _ = np.histogram(lbp.ravel(), bins=26, range=(0, 26))
            lbp_hist = lbp_hist.astype(np.float32)
            lbp_hist /= (lbp_hist.sum() + 1e-7)  # Normalize
            
            return {
                'lbp_uniformity': float(np.sum(lbp_hist[:25])),  # Uniform patterns
                'lbp_contrast': float(lbp_hist[25]),  # Non-uniform patterns
                'texture_energy': float(np.sum(lbp_hist**2))
            }
            
        except ImportError:
            # Fallback to simple texture measures
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            return {
                'texture_variance': float(np.var(gray)),
                'texture_energy': float(np.sum(gray**2) / gray.size)
            }
    
    def _extract_dominant_colors(self, frame: np.ndarray, k: int = 5) -> List[List[int]]:
        """
Extract dominant colors using K-means clustering."""
        try:
            from sklearn.cluster import KMeans
            
            # Reshape frame to list of pixels
            pixels = frame.reshape(-1, 3)
            
            # Apply K-means clustering
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(pixels)
            
            # Get dominant colors
            colors = kmeans.cluster_centers_.astype(int)
            
            return colors.tolist()
            
        except ImportError:
            # Fallback to simple color extraction
            mean_color = np.mean(frame, axis=(0, 1)).astype(int)
            return [mean_color.tolist()]
    
    def _calculate_frame_complexity(self, frame: np.ndarray) -> float:
        """
Calculate frame complexity using entropy."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Calculate histogram
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist = hist.flatten()
        
        # Normalize
        hist = hist / np.sum(hist)
        
        # Calculate entropy
        entropy = -np.sum(hist * np.log2(hist + 1e-7))
        
        return float(entropy)
    
    def _classify_scene_type(self, scene_frames: List[np.ndarray]) -> str:
        """
Classify the type of scene based on visual characteristics."""
        if not scene_frames:
            return "unknown"
        
        # Simple scene classification based on visual properties
        avg_brightness = np.mean([np.mean(frame) for frame in scene_frames])
        avg_complexity = np.mean([self._calculate_frame_complexity(frame) for frame in scene_frames])
        
        if avg_brightness < 50:
            return "dark_scene"
        elif avg_brightness > 200:
            return "bright_scene"
        elif avg_complexity > 6:
            return "complex_scene"
        elif avg_complexity < 3:
            return "simple_scene"
        else:
            return "normal_scene"
    
    def _grade_sharpness(self, blur_score: float) -> str:
        """Grade video sharpness based on blur score."""
        if blur_score > 500:
            return "excellent"
        elif blur_score > 200:
            return "good"
        elif blur_score > 100:
            return "fair"
        else:
            return "poor"
    
    def _grade_noise(self, noise_score: float) -> str:
        """Grade video noise level."""
        if noise_score < 10:
            return "low"
        elif noise_score < 20:
            return "moderate"
        elif noise_score < 40:
            return "high"
        else:
            return "very_high"
    
    def _calculate_video_quality_score(self, quality_metrics: Dict[str, Any]) -> float:
        """Calculate overall video quality score."""
        score = 50.0  # Base score
        
        # Resolution contribution
        resolution = quality_metrics.get('resolution', {})
        total_pixels = resolution.get('total_pixels', 0)
        
        if total_pixels >= 1920 * 1080:  # 1080p+
            score += 20
        elif total_pixels >= 1280 * 720:  # 720p
            score += 15
        elif total_pixels >= 640 * 480:   # 480p
            score += 10
        
        # Frame rate contribution
        fps = quality_metrics.get('frame_rate', 30)
        if fps >= 60:
            score += 10
        elif fps >= 30:
            score += 5
        
        # Sharpness contribution
        sharpness = quality_metrics.get('sharpness', {})
        sharpness_grade = sharpness.get('sharpness_grade', 'poor')
        sharpness_scores = {'excellent': 15, 'good': 10, 'fair': 5, 'poor': 0}
        score += sharpness_scores.get(sharpness_grade, 0)
        
        # Noise penalty
        noise = quality_metrics.get('noise', {})
        noise_grade = noise.get('noise_grade', 'moderate')
        noise_penalties = {'low': 0, 'moderate': -5, 'high': -10, 'very_high': -20}
        score += noise_penalties.get(noise_grade, 0)
        
        return float(np.clip(score, 0, 100))
    
    def _grade_video_quality(self, score: float) -> str:
        """
Convert quality score to letter grade."""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _generate_video_quality_recommendations(self, quality_metrics: Dict[str, Any]) -> List[str]:
        """Generate recommendations for improving video quality."""
        recommendations = []
        
        # Resolution recommendations
        resolution = quality_metrics.get('resolution', {})
        if resolution.get('total_pixels', 0) < 1280 * 720:
            recommendations.append("Consider recording in higher resolution (720p minimum)")
        
        # Frame rate recommendations
        fps = quality_metrics.get('frame_rate', 30)
        if fps < 30:
            recommendations.append("Increase frame rate to at least 30fps for smoother video")
        
        # Sharpness recommendations
        sharpness = quality_metrics.get('sharpness', {})
        if sharpness.get('sharpness_grade') == 'poor':
            recommendations.append("Improve focus and camera stability to reduce blur")
        
        # Noise recommendations
        noise = quality_metrics.get('noise', {})
        if noise.get('noise_grade') in ['high', 'very_high']:
            recommendations.append("Improve lighting conditions to reduce video noise")
        
        # Brightness recommendations
        brightness = quality_metrics.get('brightness', {})
        if brightness.get('consistency', 1.0) < 0.8:
            recommendations.append("Maintain consistent lighting throughout the video")
        
        return recommendations
    
    def _create_video_fingerprint(self, key_frames: List[np.ndarray]) -> str:
        """Create a compact fingerprint for the entire video."""
        fingerprint_data = []
        
        for frame in key_frames:
            # Resize frame to standard size
            resized = cv2.resize(frame, (64, 64))
            
            # Convert to grayscale
            gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            
            # Calculate DCT and keep low frequencies
            dct = cv2.dct(np.float32(gray))
            dct_low = dct[:8, :8]
            
            fingerprint_data.extend(dct_low.flatten())
        
        # Create hash from fingerprint data
        fingerprint_bytes = np.array(fingerprint_data).tobytes()
        fingerprint_hash = hashlib.sha256(fingerprint_bytes).hexdigest()[:32]
        
        return fingerprint_hash
    
    def _compute_temporal_hash(self, frames: List[np.ndarray]) -> str:
        """
Compute hash based on temporal characteristics."""
        if len(frames) < 2:
            return "00000000"
        
        temporal_features = []
        
        # Sample frame differences
        for i in range(0, len(frames)-1, max(1, len(frames)//16)):
            if i+1 < len(frames):
                # Calculate frame difference
                diff = cv2.absdiff(frames[i], frames[i+1])
                diff_mean = np.mean(diff)
                temporal_features.append(diff_mean)
        
        # Create hash from temporal features
        temporal_bytes = np.array(temporal_features).tobytes()
        temporal_hash = hashlib.md5(temporal_bytes).hexdigest()[:16]
        
        return temporal_hash
    
    def _classify_motion_type(self, motion_magnitudes: List[float]) -> str:
        """Classify the type of motion in the video."""
        if not motion_magnitudes:
            return "static"
        
        mean_motion = np.mean(motion_magnitudes)
        motion_variance = np.var(motion_magnitudes)
        
        if mean_motion < 5:
            return "static"
        elif mean_motion < 15 and motion_variance < 10:
            return "slow_steady"
        elif mean_motion < 30 and motion_variance < 50:
            return "moderate"
        elif motion_variance > 100:
            return "dynamic"
        else:
            return "fast_motion"
    
    def _calculate_overall_confidence(self, results: Dict[str, Any]) -> float:
        """Calculate overall confidence score for video classification."""
        confidences = []
        
        if 'content_type' in results and 'confidence' in results['content_type']:
            confidences.append(results['content_type']['confidence'])
        
        if 'quality' in results and 'quality_score' in results['quality']:
            confidences.append(results['quality']['quality_score'] / 100.0)
        
        if 'objects' in results and 'total_detections' in results['objects']:
            detection_confidence = min(results['objects']['total_detections'] / 10.0, 1.0)
            confidences.append(detection_confidence)
        
        if confidences:
            return float(np.mean(confidences))
        
        return 0.5  # Default moderate confidence
    
    async def batch_classify(
        self,
        video_files: List[str],
        analysis_type: str = "complete"
    ) -> List[Dict[str, Any]]:
        """Classify multiple video files in batch."""
        results = []
        
        for video_file in video_files:
            try:
                result = await self.classify_video(video_file, analysis_type)
                results.append(result)
                
            except Exception as e:
                logger.error(f"Error processing {video_file}: {e}")
                results.append({
                    'file_path': video_file,
                    'error': str(e),
                    'confidence': 0.0
                })
        
        return results
    
    async def compare_similarity(
        self,
        video_file1: str,
        video_file2: str
    ) -> Dict[str, Any]:
        """Compare similarity between two video files."""
        try:
            # Classify both videos
            result1 = await self.classify_video(video_file1, 'similarity')
            result2 = await self.classify_video(video_file2, 'similarity')
            
            # Extract similarity hashes
            hash1 = result1['similarity_hash']
            hash2 = result2['similarity_hash']
            
            # Calculate frame hash similarities
            frame_similarities = []
            if len(hash1['frame_hashes']) == len(hash2['frame_hashes']):
                for h1, h2 in zip(hash1['frame_hashes'], hash2['frame_hashes']):
                    phash_sim = self._calculate_hash_similarity(h1['phash'], h2['phash'])
                    dhash_sim = self._calculate_hash_similarity(h1['dhash'], h2['dhash'])
                    frame_similarities.append((phash_sim + dhash_sim) / 2)
            
            # Calculate overall similarity
            if frame_similarities:
                overall_similarity = np.mean(frame_similarities)
            else:
                overall_similarity = 0.0
            
            # Temporal similarity
            temporal_sim = self._calculate_hash_similarity(
                hash1['temporal_hash'], 
                hash2['temporal_hash']
            )
            
            # Fingerprint similarity
            fingerprint_sim = self._calculate_hash_similarity(
                hash1['video_fingerprint'],
                hash2['video_fingerprint']
            )
            
            # Combined similarity score
            combined_similarity = (overall_similarity + temporal_sim + fingerprint_sim) / 3
            
            return {
                'video1': video_file1,
                'video2': video_file2,
                'frame_similarity': overall_similarity,
                'temporal_similarity': temporal_sim,
                'fingerprint_similarity': fingerprint_sim,
                'combined_similarity': combined_similarity,
                'is_match': combined_similarity > self.similarity_threshold,
                'confidence': combined_similarity
            }
            
        except Exception as e:
            logger.error(f"Error comparing video similarity: {e}")
            raise
    
    def _calculate_hash_similarity(self, hash1: str, hash2: str) -> float:
        """Calculate similarity between two hashes."""
        if len(hash1) != len(hash2):
            return 0.0
        
        different_chars = sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
        similarity = 1.0 - (different_chars / len(hash1))
        return similarity
    
    def get_supported_formats(self) -> List[str]:
        """
Get list of supported video formats."""
        return ['mp4', 'avi', 'mov', 'mkv', 'webm', 'flv', 'wmv', 'm4v']
    
    def get_classification_categories(self) -> Dict[str, List[str]]:
        """
Get available classification categories."""
        return {
            'content_types': ['music_video', 'vlog', 'tutorial', 'performance', 'interview', 'gameplay', 'animation'],
            'scene_types': ['dark_scene', 'bright_scene', 'complex_scene', 'simple_scene', 'normal_scene'],
            'motion_types': ['static', 'slow_steady', 'moderate', 'dynamic', 'fast_motion'],
            'quality_grades': ['A', 'B', 'C', 'D', 'F']
        }
