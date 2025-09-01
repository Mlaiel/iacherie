"""IA Influencer Agent - Video Content Filters
===========================================

Ultra-advanced professional video content filtering for multimedia processing.
Implements enterprise-grade video analysis with AI-powered validation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

⚠️ STRICT COPYRIGHT PROTECTION ⚠️
This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de).
UNAUTHORIZED USE STRICTLY PROHIBITED - Legal action will be taken.

Technical Team Expertise:
- Lead IA Developer: Advanced AI/ML algorithms and neural networks
- Backend Senior: Enterprise architecture and microservices
- ML Engineer: Machine learning pipelines and model optimization
- Database Administrator: Data architecture and optimization
- Security Specialist: Cybersecurity and data protection
- Microservices Architect: Distributed systems and scalability
- Audio Engineer: Digital signal processing and audio analysis
- DevOps Engineer: Infrastructure automation and deployment
- IA Prompt Engineer: Prompt optimization and AI interaction

Project Owner: Fahed Mlaiel - mlaiel@live.de
"""
import asyncio
import logging
import time
import hashlib
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass
import numpy as np
from pathlib import Path

try:
    import cv2
    import numpy as np
    from PIL import Image
    HAS_VIDEO_LIBS = True
except ImportError:
    HAS_VIDEO_LIBS = False
    logging.warning("Video processing libraries not available. Install opencv-python, pillow.")

from .config import VideoFilterConfig
from .filter_engine import FilterResponse, FilterResult, FilterType, ContentItem


class VideoQualityAnalyzer:
    """Video quality analysis and metrics calculation."""
    
    def __init__(self):
        """Initialize video quality analyzer."""
        self.logger = logging.getLogger(__name__)
    
    def analyze_frame_quality(self, frame: np.ndarray) -> Dict[str, float]:
        """Analyze quality metrics for a single frame."""
        try:
            quality_metrics = {}
            
            # Convert to grayscale for analysis
            if len(frame.shape) == 3:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            else:
                gray = frame
            
            # Sharpness (Laplacian variance)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            quality_metrics['sharpness'] = float(laplacian_var)
            
            # Brightness
            quality_metrics['brightness'] = float(np.mean(gray))
            
            # Contrast (standard deviation)
            quality_metrics['contrast'] = float(np.std(gray))
            
            # Noise estimation (using high-frequency components)
            blur_kernel = np.ones((5, 5), np.float32) / 25
            blurred = cv2.filter2D(gray, -1, blur_kernel)
            noise_estimate = np.mean(np.abs(gray.astype(float) - blurred.astype(float)))
            quality_metrics['noise_level'] = float(noise_estimate)
            
            # Overall quality score
            sharpness_score = min(1.0, laplacian_var / 1000.0)  # Normalize
            brightness_score = 1.0 - abs(128 - quality_metrics['brightness']) / 128.0
            contrast_score = min(1.0, quality_metrics['contrast'] / 100.0)
            noise_penalty = min(0.5, noise_estimate / 50.0)
            
            overall_score = (sharpness_score + brightness_score + contrast_score) / 3 - noise_penalty
            quality_metrics['overall_score'] = max(0.0, min(1.0, overall_score))
            
            return quality_metrics
            
        except Exception as e:
            self.logger.warning(f"Frame quality analysis failed: {str(e)}")
            return {'error': str(e), 'overall_score': 0.5}
    
    def calculate_motion_metrics(self, frames: List[np.ndarray]) -> Dict[str, float]:
        """Calculate motion-related quality metrics."""
        try:
            if len(frames) < 2:
                return {'motion_score': 0.0, 'stability_score': 1.0}
            
            motion_vectors = []
            
            for i in range(1, len(frames)):
                prev_gray = cv2.cvtColor(frames[i-1], cv2.COLOR_BGR2GRAY) if len(frames[i-1].shape) == 3 else frames[i-1]
                curr_gray = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY) if len(frames[i].shape) == 3 else frames[i]
                
                # Calculate optical flow
                flow = cv2.calcOpticalFlowPyrLK(
                    prev_gray, curr_gray,
                    corners=cv2.goodFeaturesToTrack(prev_gray, maxCorners=100, qualityLevel=0.3, minDistance=7),
                    nextPts=None
                )[1]
                
                if flow is not None and len(flow) > 0:
                    motion_magnitude = np.mean(np.linalg.norm(flow, axis=1))
                    motion_vectors.append(motion_magnitude)
            
            if motion_vectors:
                motion_score = np.mean(motion_vectors)
                motion_stability = 1.0 - np.std(motion_vectors) / (np.mean(motion_vectors) + 1e-6)
            else:
                motion_score = 0.0
                motion_stability = 1.0
            
            return {
                'motion_score': float(motion_score),
                'stability_score': float(max(0.0, min(1.0, motion_stability)))
            }
            
        except Exception as e:
            self.logger.warning(f"Motion analysis failed: {str(e)}")
            return {'motion_score': 0.0, 'stability_score': 0.5}


class VideoSceneDetector:
    """Video scene detection and segmentation."""
    
    def __init__(self):
        """Initialize scene detector."""
        self.logger = logging.getLogger(__name__)
    
    def detect_scenes(self, frames: List[np.ndarray], threshold: float = 0.3) -> List[Dict[str, Any]]:
        """Detect scene changes in video frames."""
        try:
            if len(frames) < 2:
                return [{'start_frame': 0, 'end_frame': len(frames)-1, 'scene_type': 'single'}]
            
            scenes = []
            scene_changes = [0]  # First frame is always a scene start
            
            for i in range(1, len(frames)):
                # Calculate histogram difference between consecutive frames
                hist1 = cv2.calcHist([frames[i-1]], [0, 1, 2], None, [50, 50, 50], [0, 256, 0, 256, 0, 256])
                hist2 = cv2.calcHist([frames[i]], [0, 1, 2], None, [50, 50, 50], [0, 256, 0, 256, 0, 256])
                
                # Compute correlation coefficient
                correlation = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
                
                # Scene change detected if correlation is below threshold
                if correlation < (1.0 - threshold):
                    scene_changes.append(i)
            
            scene_changes.append(len(frames))  # End of video
            
            # Create scene segments
            for i in range(len(scene_changes) - 1):
                start_frame = scene_changes[i]
                end_frame = scene_changes[i + 1] - 1
                
                # Analyze scene characteristics
                scene_frames = frames[start_frame:end_frame+1]
                scene_type = self._classify_scene_type(scene_frames)
                
                scenes.append({
                    'start_frame': start_frame,
                    'end_frame': end_frame,
                    'duration_frames': end_frame - start_frame + 1,
                    'scene_type': scene_type,
                    'confidence': 0.8
                })
            
            return scenes
            
        except Exception as e:
            self.logger.warning(f"Scene detection failed: {str(e)}")
            return [{'start_frame': 0, 'end_frame': len(frames)-1, 'scene_type': 'unknown', 'error': str(e)}]
    
    def _classify_scene_type(self, scene_frames: List[np.ndarray]) -> str:
        """Classify the type of scene based on visual characteristics."""
        try:
            if not scene_frames:
                return 'unknown'
            
            # Analyze color distribution
            avg_brightness = np.mean([np.mean(frame) for frame in scene_frames])
            avg_saturation = np.mean([np.mean(cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)[:,:,1]) for frame in scene_frames])
            
            # Simple scene classification
            if avg_brightness < 50:
                return 'dark'
            elif avg_brightness > 200:
                return 'bright'
            elif avg_saturation > 100:
                return 'colorful'
            else:
                return 'neutral'
                
        except Exception as e:
            self.logger.warning(f"Scene classification failed: {str(e)}")
            return 'unknown'


class VideoObjectDetector:
    """Video object detection using computer vision."""
    
    def __init__(self):
        """Initialize object detector."""
        self.logger = logging.getLogger(__name__)
        self.cascade_classifiers = self._load_cascade_classifiers()
    
    def _load_cascade_classifiers(self) -> Dict[str, Any]:
        """Load OpenCV cascade classifiers."""
        classifiers = {}
        
        try:
            # Face detection
            face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            classifiers['face'] = cv2.CascadeClassifier(face_cascade_path)
            
            # Eye detection
            eye_cascade_path = cv2.data.haarcascades + 'haarcascade_eye.xml'
            classifiers['eye'] = cv2.CascadeClassifier(eye_cascade_path)
            
            # Smile detection
            smile_cascade_path = cv2.data.haarcascades + 'haarcascade_smile.xml'
            classifiers['smile'] = cv2.CascadeClassifier(smile_cascade_path)
            
        except Exception as e:
            self.logger.warning(f"Failed to load cascade classifiers: {str(e)}")
        
        return classifiers
    
    def detect_objects_in_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """Detect objects in a single frame."""
        try:
            detection_results = {
                'faces': [],
                'objects': [],
                'confidence': 0.0
            }
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if len(frame.shape) == 3 else frame
            
            # Face detection
            if 'face' in self.cascade_classifiers:
                faces = self.cascade_classifiers['face'].detectMultiScale(
                    gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
                )
                
                for (x, y, w, h) in faces:
                    detection_results['faces'].append({
                        'x': int(x), 'y': int(y), 'width': int(w), 'height': int(h),
                        'confidence': 0.8,  # Cascade classifiers don't provide confidence
                        'type': 'face'
                    })
            
            # Eye detection within faces
            if 'eye' in self.cascade_classifiers and detection_results['faces']:
                for face in detection_results['faces']:
                    face_roi = gray[face['y']:face['y']+face['height'], face['x']:face['x']+face['width']]
                    eyes = self.cascade_classifiers['eye'].detectMultiScale(face_roi)
                    
                    for (ex, ey, ew, eh) in eyes:
                        detection_results['objects'].append({
                            'x': int(face['x'] + ex), 'y': int(face['y'] + ey),
                            'width': int(ew), 'height': int(eh),
                            'confidence': 0.7,
                            'type': 'eye'
                        })
            
            # Calculate overall confidence
            total_detections = len(detection_results['faces']) + len(detection_results['objects'])
            detection_results['confidence'] = min(1.0, total_detections * 0.2)
            
            return detection_results
            
        except Exception as e:
            self.logger.warning(f"Object detection failed: {str(e)}")
            return {'faces': [], 'objects': [], 'confidence': 0.0, 'error': str(e)}
    
    def detect_objects_in_video(self, frames: List[np.ndarray], sample_rate: int = 5) -> Dict[str, Any]:
        """Detect objects across video frames with sampling."""
        try:
            all_detections = {
                'faces_detected': 0,
                'objects_detected': 0,
                'frames_with_faces': 0,
                'frames_analyzed': 0,
                'detection_confidence': 0.0
            }
            
            # Sample frames for analysis
            sampled_frames = frames[::sample_rate] if len(frames) > sample_rate else frames
            
            face_counts = []
            object_counts = []
            
            for frame in sampled_frames:
                detections = self.detect_objects_in_frame(frame)
                
                face_count = len(detections['faces'])
                object_count = len(detections['objects'])
                
                all_detections['faces_detected'] += face_count
                all_detections['objects_detected'] += object_count
                
                if face_count > 0:
                    all_detections['frames_with_faces'] += 1
                
                face_counts.append(face_count)
                object_counts.append(object_count)
                all_detections['frames_analyzed'] += 1
            
            # Calculate statistics
            if all_detections['frames_analyzed'] > 0:
                avg_faces_per_frame = all_detections['faces_detected'] / all_detections['frames_analyzed']
                face_presence_ratio = all_detections['frames_with_faces'] / all_detections['frames_analyzed']
                
                all_detections.update({
                    'avg_faces_per_frame': avg_faces_per_frame,
                    'face_presence_ratio': face_presence_ratio,
                    'detection_confidence': min(1.0, (avg_faces_per_frame + face_presence_ratio) / 2)
                })
            
            return all_detections
            
        except Exception as e:
            self.logger.warning(f"Video object detection failed: {str(e)}")
            return {'error': str(e), 'detection_confidence': 0.0}


class VideoContentFilter:
    """Enterprise-grade video content filter."""
    
    def __init__(self, config: VideoFilterConfig):
        """Initialize video content filter."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.quality_analyzer = VideoQualityAnalyzer()
        self.scene_detector = VideoSceneDetector()
        self.object_detector = VideoObjectDetector()
        
        self.logger.info("Video content filter initialized")
    
    async def filter_async(
        self,
        content: ContentItem,
        ai_validation: bool = True,
        strict_mode: bool = False
    ) -> FilterResponse:
        """Asynchronously filter video content."""
        return await asyncio.get_event_loop().run_in_executor(
            None, self.filter, content, ai_validation, strict_mode
        )
    
    def filter(
        self,
        content: ContentItem,
        ai_validation: bool = True,
        strict_mode: bool = False
    ) -> FilterResponse:
        """Filter video content with comprehensive analysis."""
        start_time = time.time()
        
        try:
            if not HAS_VIDEO_LIBS:
                return FilterResponse(
                    filter_type=FilterType.VIDEO,
                    result=FilterResult.WARNING,
                    score=0.5,
                    confidence=0.0,
                    metadata={'error': 'Video processing libraries not available'},
                    processing_time=time.time() - start_time,
                    warnings=['Video libraries not installed']
                )
            
            # Load and validate video
            video_data, metadata = self._load_video_content(content)
            
            if video_data is None:
                return FilterResponse(
                    filter_type=FilterType.VIDEO,
                    result=FilterResult.FAILED,
                    score=0.0,
                    confidence=1.0,
                    metadata={'error': 'Failed to load video content'},
                    processing_time=time.time() - start_time,
                    errors=['Video loading failed']
                )
            
            # Perform comprehensive video analysis
            analysis_results = self._analyze_video_content(
                video_data, ai_validation, strict_mode
            )
            
            # Calculate overall score and result
            overall_score = self._calculate_overall_score(analysis_results, strict_mode)
            result = self._determine_filter_result(overall_score, analysis_results, strict_mode)
            
            # Prepare response
            response = FilterResponse(
                filter_type=FilterType.VIDEO,
                result=result,
                score=overall_score,
                confidence=analysis_results.get('confidence', 0.85),
                metadata={
                    'video_properties': metadata,
                    'quality_analysis': analysis_results.get('quality', {}),
                    'scene_analysis': analysis_results.get('scenes', {}),
                    'object_analysis': analysis_results.get('objects', {}),
                    'ai_validation_enabled': ai_validation,
                    'strict_mode': strict_mode
                },
                processing_time=time.time() - start_time,
                warnings=analysis_results.get('warnings', []),
                errors=analysis_results.get('errors', [])
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Video filtering failed: {str(e)}")
            return FilterResponse(
                filter_type=FilterType.VIDEO,
                result=FilterResult.FAILED,
                score=0.0,
                confidence=0.0,
                metadata={'error': str(e)},
                processing_time=time.time() - start_time,
                errors=[str(e)]
            )
    
    def _load_video_content(self, content: ContentItem) -> Tuple[Optional[List[np.ndarray]], Dict[str, Any]]:
        """Load and validate video content."""
        try:
            metadata = {}
            frames = []
            
            if content.file_path:
                # Load from file
                cap = cv2.VideoCapture(content.file_path)
                
                if not cap.isOpened():
                    self.logger.error(f"Failed to open video file: {content.file_path}")
                    return None, {'error': 'Failed to open video file'}
                
                # Get video properties
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                duration = frame_count / fps if fps > 0 else 0
                
                metadata.update({
                    'fps': fps,
                    'frame_count': frame_count,
                    'width': width,
                    'height': height,
                    'duration': duration,
                    'resolution': (width, height)
                })
                
                # Validate against config constraints
                if width < self.config.min_resolution[0] or height < self.config.min_resolution[1]:
                    metadata['validation_error'] = f"Resolution {width}x{height} below minimum {self.config.min_resolution}"
                    cap.release()
                    return None, metadata
                
                if fps < self.config.min_fps:
                    metadata['validation_error'] = f"FPS {fps} below minimum {self.config.min_fps}"
                    cap.release()
                    return None, metadata
                
                if duration < self.config.min_duration:
                    metadata['validation_error'] = f"Duration {duration:.2f}s below minimum {self.config.min_duration}s"
                    cap.release()
                    return None, metadata
                
                # Sample frames for analysis (to avoid memory issues)
                sample_rate = max(1, frame_count // 50)  # Sample up to 50 frames
                frame_indices = range(0, frame_count, sample_rate)
                
                for frame_idx in frame_indices:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                    ret, frame = cap.read()
                    
                    if ret:
                        frames.append(frame)
                    
                    if len(frames) >= 50:  # Limit to 50 frames max
                        break
                
                cap.release()
                
                # Get file metadata
                file_path = Path(content.file_path)
                metadata.update({
                    'filename': file_path.name,
                    'extension': file_path.suffix.lower(),
                    'file_size': file_path.stat().st_size,
                    'frames_sampled': len(frames)
                })
                
            else:
                self.logger.error("Video loading from bytes not implemented")
                return None, {'error': 'Video loading from bytes not supported'}
            
            return frames, metadata
            
        except Exception as e:
            self.logger.error(f"Video loading failed: {str(e)}")
            return None, {'error': str(e)}
    
    def _analyze_video_content(
        self,
        frames: List[np.ndarray],
        ai_validation: bool,
        strict_mode: bool
    ) -> Dict[str, Any]:
        """Perform comprehensive video content analysis."""
        analysis_results = {
            'warnings': [],
            'errors': [],
            'confidence': 0.85
        }
        
        try:
            # Quality analysis
            analysis_results['quality'] = self._analyze_video_quality(frames)
            
            # Scene detection
            if self.config.enable_scene_detection:
                analysis_results['scenes'] = self._analyze_scenes(frames)
            
            # Object detection
            if self.config.enable_object_detection and ai_validation:
                analysis_results['objects'] = self._analyze_objects(frames)
            
            # Face detection
            if self.config.enable_face_detection and ai_validation:
                analysis_results['faces'] = self._analyze_faces(frames)
            
            # Content classification
            if self.config.enable_content_classification and ai_validation:
                analysis_results['classification'] = self._classify_content(frames)
            
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"Video analysis failed: {str(e)}")
            analysis_results['errors'].append(str(e))
            analysis_results['confidence'] = 0.0
            return analysis_results
    
    def _analyze_video_quality(self, frames: List[np.ndarray]) -> Dict[str, Any]:
        """Analyze video quality metrics."""
        try:
            if not frames:
                return {'error': 'No frames to analyze', 'overall_score': 0.0}
            
            # Analyze sample of frames
            sample_frames = frames[::max(1, len(frames) // 10)]  # Sample 10 frames max
            quality_scores = []
            
            for frame in sample_frames:
                frame_quality = self.quality_analyzer.analyze_frame_quality(frame)
                if 'overall_score' in frame_quality:
                    quality_scores.append(frame_quality['overall_score'])
            
            # Calculate motion metrics
            motion_metrics = self.quality_analyzer.calculate_motion_metrics(sample_frames)
            
            # Overall quality assessment
            if quality_scores:
                avg_quality = np.mean(quality_scores)
                quality_consistency = 1.0 - np.std(quality_scores)
            else:
                avg_quality = 0.5
                quality_consistency = 0.5
            
            overall_score = (avg_quality + quality_consistency + motion_metrics.get('stability_score', 0.5)) / 3
            
            return {
                'average_quality': float(avg_quality),
                'quality_consistency': float(quality_consistency),
                'motion_score': motion_metrics.get('motion_score', 0.0),
                'stability_score': motion_metrics.get('stability_score', 0.5),
                'overall_score': float(max(0.0, min(1.0, overall_score))),
                'frames_analyzed': len(sample_frames)
            }
            
        except Exception as e:
            self.logger.warning(f"Video quality analysis failed: {str(e)}")
            return {'error': str(e), 'overall_score': 0.5}
    
    def _analyze_scenes(self, frames: List[np.ndarray]) -> Dict[str, Any]:
        """Analyze video scenes and transitions."""
        try:
            scenes = self.scene_detector.detect_scenes(frames)
            
            return {
                'scene_count': len(scenes),
                'scenes': scenes,
                'avg_scene_duration': np.mean([s['duration_frames'] for s in scenes]) if scenes else 0,
                'scene_variety': len(set(s['scene_type'] for s in scenes)) if scenes else 0
            }
            
        except Exception as e:
            self.logger.warning(f"Scene analysis failed: {str(e)}")
            return {'error': str(e), 'scene_count': 0}
    
    def _analyze_objects(self, frames: List[np.ndarray]) -> Dict[str, Any]:
        """Analyze objects in video."""
        try:
            object_analysis = self.object_detector.detect_objects_in_video(frames)
            return object_analysis
            
        except Exception as e:
            self.logger.warning(f"Object analysis failed: {str(e)}")
            return {'error': str(e), 'detection_confidence': 0.0}
    
    def _analyze_faces(self, frames: List[np.ndarray]) -> Dict[str, Any]:
        """Analyze faces in video."""
        try:
            # Use object detector for face analysis
            face_analysis = self.object_detector.detect_objects_in_video(frames)
            
            return {
                'faces_detected': face_analysis.get('faces_detected', 0),
                'frames_with_faces': face_analysis.get('frames_with_faces', 0),
                'face_presence_ratio': face_analysis.get('face_presence_ratio', 0.0),
                'confidence': face_analysis.get('detection_confidence', 0.0)
            }
            
        except Exception as e:
            self.logger.warning(f"Face analysis failed: {str(e)}")
            return {'error': str(e), 'confidence': 0.0}
    
    def _classify_content(self, frames: List[np.ndarray]) -> Dict[str, Any]:
        """Classify video content type."""
        try:
            # Simplified content classification
            # In real implementation, use specialized models
            
            if not frames:
                return {'content_type': 'unknown', 'confidence': 0.0}
            
            # Analyze visual characteristics
            avg_brightness = np.mean([np.mean(frame) for frame in frames[:10]])
            color_variance = np.mean([np.var(frame) for frame in frames[:10]])
            
            # Simple classification rules
            if avg_brightness < 50:
                content_type = 'dark_video'
                confidence = 0.6
            elif color_variance > 10000:
                content_type = 'dynamic_content'
                confidence = 0.7
            elif avg_brightness > 200:
                content_type = 'bright_video'
                confidence = 0.6
            else:
                content_type = 'general_video'
                confidence = 0.5
            
            return {
                'content_type': content_type,
                'confidence': confidence,
                'avg_brightness': float(avg_brightness),
                'color_variance': float(color_variance)
            }
            
        except Exception as e:
            self.logger.warning(f"Content classification failed: {str(e)}")
            return {'error': str(e), 'content_type': 'unknown', 'confidence': 0.0}
    
    def _calculate_overall_score(self, analysis_results: Dict[str, Any], strict_mode: bool) -> float:
        """Calculate overall video filter score."""
        scores = []
        weights = []
        
        # Quality score
        quality_score = analysis_results.get('quality', {}).get('overall_score')
        if quality_score is not None:
            scores.append(quality_score)
            weights.append(0.4)
        
        # Object detection confidence
        object_confidence = analysis_results.get('objects', {}).get('detection_confidence', 0.0)
        if object_confidence > 0:
            scores.append(object_confidence)
            weights.append(0.2)
        
        # Face detection confidence
        face_confidence = analysis_results.get('faces', {}).get('confidence', 0.0)
        if face_confidence > 0:
            scores.append(face_confidence)
            weights.append(0.2)
        
        # Scene analysis score
        scene_count = analysis_results.get('scenes', {}).get('scene_count', 0)
        if scene_count > 0:
            scene_score = min(1.0, scene_count / 10.0)  # Normalize to 0-1
            scores.append(scene_score)
            weights.append(0.2)
        
        # Calculate weighted average
        if scores and weights:
            weighted_sum = sum(s * w for s, w in zip(scores, weights))
            total_weight = sum(weights)
            return weighted_sum / total_weight
        
        return 0.5  # Default neutral score
    
    def _determine_filter_result(
        self,
        overall_score: float,
        analysis_results: Dict[str, Any],
        strict_mode: bool
    ) -> FilterResult:
        """Determine filter result based on analysis."""
        # Check quality thresholds
        quality_data = analysis_results.get('quality', {})
        if quality_data.get('overall_score', 1.0) < 0.3:  # Very low quality
            return FilterResult.WARNING if not strict_mode else FilterResult.FAILED
        
        # Overall score thresholds
        if strict_mode:
            if overall_score >= 0.8:
                return FilterResult.PASSED
            elif overall_score >= 0.6:
                return FilterResult.WARNING
            else:
                return FilterResult.FAILED
        else:
            if overall_score >= 0.6:
                return FilterResult.PASSED
            elif overall_score >= 0.4:
                return FilterResult.WARNING
            else:
                return FilterResult.FAILED
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on video filter."""
        health_status = {
            'status': 'healthy',
            'libraries': {
                'opencv': HAS_VIDEO_LIBS,
                'pillow': HAS_VIDEO_LIBS,
                'numpy': True
            },
            'config': {
                'scene_detection': self.config.enable_scene_detection,
                'object_detection': self.config.enable_object_detection,
                'face_detection': self.config.enable_face_detection,
                'supported_formats': len(self.config.supported_formats)
            }
        }
        
        if not HAS_VIDEO_LIBS:
            health_status['status'] = 'warning'
            health_status['message'] = 'Video processing libraries not available'
        
        return health_status
