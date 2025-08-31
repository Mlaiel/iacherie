# Live Streaming Computer Vision Processing Engine
# Advanced Industrial-Grade Real-Time Visual Intelligence System
#
# Created by: Fahed Mlaiel (mlaiel@live.de)
# 
#   STRICT COPYRIGHT WARNING  
# This code, concept, and intellectual property belongs exclusively to Fahed Mlaiel.
# ANY unauthorized use, reproduction, distribution, or theft of this code/concept 
# without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is 
# STRICTLY PROHIBITED and will result in immediate legal action.
# All rights reserved. Patent pending.

import cv2
import numpy as np
import torch
import torch.nn as nn
from typing import Dict, List, Tuple, Optional, Union, Any, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
import asyncio
import threading
import queue
import time
from concurrent.futures import ThreadPoolExecutor
import io
import base64
from pathlib import Path
import json
from abc import ABC, abstractmethod
from collections import deque
import psutil
import gc

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Optional imports with fallbacks
try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    logger.warning("websockets not available, WebSocket streaming will be limited")

try:
    import ffmpeg
    FFMPEG_AVAILABLE = True
except ImportError:
    FFMPEG_AVAILABLE = False
    logger.warning("ffmpeg-python not available, advanced encoding will be limited")

@dataclass
class StreamingConfig:
    """Advanced streaming configuration for real-time processing"""
    input_resolution: Tuple[int, int] = (1920, 1080)
    output_resolution: Tuple[int, int] = (1920, 1080)
    fps: int = 30
    bitrate: int = 5000
    codec: str = "h264"
    preset: str = "ultrafast"
    crf: int = 23
    gop_size: int = 30
    max_latency_ms: int = 100
    buffer_size: int = 5
    processing_threads: int = 4
    enable_gpu: bool = True
    enable_realtime_enhancement: bool = True
    enable_realtime_detection: bool = True
    enable_adaptive_bitrate: bool = True
    target_fps: int = 30
    min_fps: int = 15
    max_fps: int = 60
    quality_levels: List[str] = field(default_factory=lambda: ["480p", "720p", "1080p", "4K"])
    
@dataclass
class StreamMetrics:
    """Comprehensive streaming performance metrics"""
    timestamp: datetime = field(default_factory=datetime.now)
    fps_current: float = 0.0
    fps_average: float = 0.0
    latency_ms: float = 0.0
    bitrate_kbps: float = 0.0
    frame_drops: int = 0
    encoding_time_ms: float = 0.0
    processing_time_ms: float = 0.0
    cpu_usage: float = 0.0
    gpu_usage: float = 0.0
    memory_usage_mb: float = 0.0
    bandwidth_usage_mbps: float = 0.0
    quality_score: float = 0.0
    viewer_count: int = 0
    error_count: int = 0
    
@dataclass
class QualityAdaptation:
    """Adaptive quality management for streaming optimization"""
    current_quality: str
    target_quality: str
    adaptation_reason: str
    bandwidth_estimate: float
    cpu_usage: float
    gpu_usage: float
    viewer_feedback_score: float
    network_stability: float
    recommended_settings: Dict[str, Any]

class AdaptiveBitrate:
    """Professional adaptive bitrate streaming controller"""
    
    def __init__(self, config: StreamingConfig):
        self.config = config
        self.quality_levels = {
            "480p": {"width": 854, "height": 480, "bitrate": 1500, "fps": 30},
            "720p": {"width": 1280, "height": 720, "bitrate": 3000, "fps": 30},
            "1080p": {"width": 1920, "height": 1080, "bitrate": 5000, "fps": 30},
            "4K": {"width": 3840, "height": 2160, "bitrate": 15000, "fps": 60}
        }
        self.current_level = "1080p"
        self.metrics_history = deque(maxlen=100)
        self.adaptation_lock = threading.Lock()
        
    def analyze_network_conditions(self) -> Dict[str, float]:
        """Analyze current network and system conditions"""



        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            gpu_usage = self._get_gpu_usage()
            
            # Estimate bandwidth based on recent metrics
            bandwidth_estimate = self._estimate_bandwidth()
            
            # Calculate network stability score
            stability_score = self._calculate_network_stability()
            
            return {
                "cpu_usage": cpu_percent,
                "memory_usage": memory.percent,
                "gpu_usage": gpu_usage,
                "bandwidth_mbps": bandwidth_estimate,
                "network_stability": stability_score,
                "available_memory_gb": memory.available / (1024**3)
            }
        except Exception as e:
            logger.error(f"Error analyzing network conditions: {e}")
            return {"error": str(e)}
    
    def _get_gpu_usage(self) -> float:
        """Get GPU usage percentage"""



        try:
            if torch.cuda.is_available():
                gpu_memory = torch.cuda.memory_allocated() / torch.cuda.max_memory_allocated()
                return gpu_memory * 100
            return 0.0
        except:
            return 0.0
    
    def _estimate_bandwidth(self) -> float:
        """Estimate available bandwidth based on streaming history"""
        if len(self.metrics_history) < 5:
            return 10.0  # Default bandwidth estimate
        
        recent_metrics = list(self.metrics_history)[-10:]
        bitrates = [m.bitrate_kbps for m in recent_metrics]
        return np.mean(bitrates) / 1000  # Convert to Mbps
    
    def _calculate_network_stability(self) -> float:
        """Calculate network stability score (0-1)"""
        if len(self.metrics_history) < 10:
            return 0.8  # Default stability score
        
        recent_metrics = list(self.metrics_history)[-20:]
        latencies = [m.latency_ms for m in recent_metrics]
        frame_drops = [m.frame_drops for m in recent_metrics]
        
        # Calculate variance in latency (lower is better)
        latency_variance = np.var(latencies)
        normalized_latency_score = max(0, 1 - (latency_variance / 1000))
        
        # Calculate frame drop rate (lower is better)
        total_frame_drops = sum(frame_drops)
        frame_drop_score = max(0, 1 - (total_frame_drops / len(frame_drops) / 10))
        
        return (normalized_latency_score + frame_drop_score) / 2
    
    def _get_lower_quality(self, current_quality: str) -> str:
        """Get lower quality level for adaptation"""
        quality_order = ["4K", "1080p", "720p", "480p"]
        try:
            current_index = quality_order.index(current_quality)
            if current_index < len(quality_order) - 1:
                return quality_order[current_index + 1]
            return current_quality
        except ValueError:
            return "720p"  # Default fallback
    
    def _get_higher_quality(self, current_quality: str) -> str:
        """Get higher quality level for adaptation"""
        quality_order = ["480p", "720p", "1080p", "4K"]
        try:
            current_index = quality_order.index(current_quality)
            if current_index > 0:
                return quality_order[current_index - 1]
            return current_quality
        except ValueError:
            return "720p"  # Default fallback

    def recommend_quality_adaptation(self, current_metrics: StreamMetrics) -> QualityAdaptation:
        """Recommend quality adaptation based on current conditions"""
        with self.adaptation_lock:
            conditions = self.analyze_network_conditions()
            
            # Analyze performance indicators
            cpu_overload = conditions["cpu_usage"] > 80
            memory_pressure = conditions["memory_usage"] > 85
            gpu_overload = conditions["gpu_usage"] > 90
            low_bandwidth = conditions["bandwidth_mbps"] < 3.0
            unstable_network = conditions["network_stability"] < 0.6
            high_latency = current_metrics.latency_ms > 200
            frequent_drops = current_metrics.frame_drops > 5
            
            # Determine adaptation strategy
            current_quality = self.current_level
            target_quality = current_quality
            adaptation_reason = "No adaptation needed"
            
            # Downgrade conditions
            if cpu_overload or memory_pressure or gpu_overload:
                target_quality = self._get_lower_quality(current_quality)
                adaptation_reason = "System resource constraints"
            elif low_bandwidth or unstable_network:
                target_quality = self._get_lower_quality(current_quality)
                adaptation_reason = "Network conditions"
            elif high_latency or frequent_drops:
                target_quality = self._get_lower_quality(current_quality)
                adaptation_reason = "Performance issues"
            
            # Upgrade conditions (only if no issues)
            elif (conditions["cpu_usage"] < 50 and 
                  conditions["memory_usage"] < 60 and
                  conditions["bandwidth_mbps"] > 8.0 and
                  conditions["network_stability"] > 0.8 and
                  current_metrics.latency_ms < 50):
                higher_quality = self._get_higher_quality(current_quality)
                if higher_quality != current_quality:
                    target_quality = higher_quality
                    adaptation_reason = "Performance headroom available"
            
            # Generate recommended settings
            recommended_settings = self._generate_optimal_settings(
                target_quality, conditions, current_metrics
            )
            
            return QualityAdaptation(
                current_quality=current_quality,
                target_quality=target_quality,
                adaptation_reason=adaptation_reason,
                bandwidth_estimate=conditions["bandwidth_mbps"],
                cpu_usage=conditions["cpu_usage"],
                gpu_usage=conditions["gpu_usage"],
                viewer_feedback_score=0.8,  # Could be integrated with viewer feedback
                network_stability=conditions["network_stability"],
                recommended_settings=recommended_settings
            )
    
    def _get_lower_quality(self, current: str) -> str:
        """Get the next lower quality level"""
        levels = ["4K", "1080p", "720p", "480p"]
        try:
            current_index = levels.index(current)
            return levels[min(current_index + 1, len(levels) - 1)]
        except ValueError:
            return "720p"
    
    def _get_higher_quality(self, current: str) -> str:
        """Get the next higher quality level"""
        levels = ["480p", "720p", "1080p", "4K"]
        try:
            current_index = levels.index(current)
            return levels[min(current_index + 1, len(levels) - 1)]
        except ValueError:
            return "1080p"
    
    def _generate_optimal_settings(self, quality: str, conditions: Dict, metrics: StreamMetrics) -> Dict[str, Any]:
        """Generate optimal streaming settings for the target quality"""
        base_settings = self.quality_levels[quality].copy()
        
        # Adjust based on system conditions
        if conditions["cpu_usage"] > 70:
            base_settings["preset"] = "ultrafast"
            base_settings["threads"] = max(1, self.config.processing_threads // 2)
        elif conditions["cpu_usage"] < 40:
            base_settings["preset"] = "medium"
            base_settings["threads"] = self.config.processing_threads
        
        # Adjust bitrate based on bandwidth
        bandwidth_factor = min(1.0, conditions["bandwidth_mbps"] / 5.0)
        base_settings["bitrate"] = int(base_settings["bitrate"] * bandwidth_factor)
        
        # Adjust FPS based on performance
        if metrics.fps_current < 25:
            base_settings["fps"] = 24
        elif metrics.fps_current > 55:
            base_settings["fps"] = 60
        
        return base_settings

class RealTimeAnalyzer:
    """Advanced real-time video analysis engine for streaming"""
    
    def __init__(self, config: StreamingConfig):
        self.config = config
        self.analysis_queue = queue.Queue(maxsize=config.buffer_size)
        self.result_queue = queue.Queue(maxsize=config.buffer_size * 2)
        self.is_running = False
        self.analysis_threads = []
        self.frame_processors = []
        self.performance_monitor = PerformanceMonitor()
        
        # Initialize AI models for real-time analysis
        self._initialize_models()
        
    def _initialize_models(self):
        """Initialize optimized models for real-time analysis"""



        try:
            # Load lightweight detection model
            self.object_detector = self._load_optimized_detector()
            
            # Load face detection model
            self.face_detector = self._load_face_detector()
            
            # Load emotion recognition model
            self.emotion_classifier = self._load_emotion_classifier()
            
            # Load content classification model
            self.content_classifier = self._load_content_classifier()
            
            logger.info("Real-time analysis models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing analysis models: {e}")
            raise
    
    def _load_optimized_detector(self):
        """Load optimized object detection model for real-time processing"""



        try:
            # Use lightweight YOLO model optimized for speed - suppress warnings
            import warnings
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=UserWarning)
                model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True, trust_repo=True)
            model.eval()
            
            if self.config.enable_gpu and torch.cuda.is_available():
                model = model.cuda()
                
            # Optimize for inference
            model.conf = 0.4  # Confidence threshold
            model.iou = 0.5   # IoU threshold
            model.max_det = 50  # Maximum detections
            
            return model
        except Exception as e:
            logger.error(f"Error loading object detector: {e}")
            return None
    
    def _load_face_detector(self):
        """Load optimized face detection model"""



        try:
            # Use OpenCV's DNN face detector for speed
            net = cv2.dnn.readNetFromTensorflow(
                'opencv_face_detector_uint8.pb',
                'opencv_face_detector.pbtxt'
            )
            return net
        except Exception as e:
            logger.warning(f"OpenCV face detector not available, using Haar cascades: {e}")
            return cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    def _load_emotion_classifier(self):
        """Load emotion classification model"""



        try:
            # Lightweight emotion recognition model - suppress warnings
            import warnings
            from torchvision.models import mobilenet_v3_small
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=UserWarning)
                model = mobilenet_v3_small(weights=None)  # Use new parameter
            model.classifier[-1] = nn.Linear(model.classifier[-1].in_features, 7)  # 7 emotions
            
            # Load pre-trained weights (would be loaded from file in production)
            # model.load_state_dict(torch.load('emotion_model.pth'))
            model.eval()
            
            if self.config.enable_gpu and torch.cuda.is_available():
                model = model.cuda()
                
            return model
        except Exception as e:
            logger.warning(f"Emotion classifier not available: {e}")
            return None
    
    def _load_content_classifier(self):
        """Load content classification model"""



        try:
            # Lightweight content classification for streaming safety - suppress warnings
            import warnings
            from torchvision.models import efficientnet_b0
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=UserWarning)
                model = efficientnet_b0(weights='DEFAULT')  # Use new parameter
            model.classifier[-1] = nn.Linear(model.classifier[-1].in_features, 10)  # Content categories
            model.eval()
            
            if self.config.enable_gpu and torch.cuda.is_available():
                model = model.cuda()
                
            return model
        except Exception as e:
            logger.warning(f"Content classifier not available: {e}")
            return None
    
    def start_analysis(self):
        """Start real-time analysis threads"""
        if self.is_running:
            return
            
        self.is_running = True
        
        # Start analysis worker threads
        for i in range(self.config.processing_threads):
            thread = threading.Thread(
                target=self._analysis_worker,
                name=f"AnalysisWorker-{i}",
                daemon=True
            )
            thread.start()
            self.analysis_threads.append(thread)
            
        logger.info(f"Started {len(self.analysis_threads)} analysis threads")
    
    def stop_analysis(self):
        """Stop real-time analysis"""
        self.is_running = False
        
        # Wait for threads to finish
        for thread in self.analysis_threads:
            thread.join(timeout=2.0)
            
        self.analysis_threads.clear()
        logger.info("Real-time analysis stopped")
    
    def _analysis_worker(self):
        """Worker thread for real-time frame analysis"""
        while self.is_running:
            try:
                # Get frame from queue with timeout
                frame_data = self.analysis_queue.get(timeout=0.1)
                
                if frame_data is None:
                    continue
                
                start_time = time.time()
                
                # Perform analysis
                analysis_result = self._analyze_frame(frame_data)
                
                # Calculate processing time
                processing_time = (time.time() - start_time) * 1000
                analysis_result['processing_time_ms'] = processing_time
                
                # Put result in queue
                if not self.result_queue.full():
                    self.result_queue.put(analysis_result)
                    
                self.analysis_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error in analysis worker: {e}")
                continue
    
    def _analyze_frame(self, frame_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single frame with multiple AI models"""
        frame = frame_data['frame']
        timestamp = frame_data['timestamp']
        frame_id = frame_data['frame_id']
        
        analysis_result = {
            'frame_id': frame_id,
            'timestamp': timestamp,
            'objects': [],
            'faces': [],
            'emotions': [],
            'content_type': 'unknown',
            'safety_score': 1.0,
            'quality_metrics': {}
        }
        
        try:
            # Object detection
            if self.object_detector and self.config.enable_realtime_detection:
                objects = self._detect_objects(frame)
                analysis_result['objects'] = objects
            
            # Face detection and emotion analysis
            if self.face_detector:
                faces = self._detect_faces(frame)
                analysis_result['faces'] = faces
                
                if faces and self.emotion_classifier:
                    emotions = self._analyze_emotions(frame, faces)
                    analysis_result['emotions'] = emotions
            
            # Content classification
            if self.content_classifier:
                content_info = self._classify_content(frame)
                analysis_result.update(content_info)
            
            # Quality analysis
            quality_metrics = self._analyze_frame_quality(frame)
            analysis_result['quality_metrics'] = quality_metrics
            
        except Exception as e:
            logger.error(f"Error analyzing frame {frame_id}: {e}")
            analysis_result['error'] = str(e)
        
        return analysis_result
    
    def _detect_objects(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Detect objects in frame using YOLO"""



        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Run inference
            results = self.object_detector(rgb_frame)
            
            # Parse results
            objects = []
            for *box, conf, cls in results.xyxy[0].cpu().numpy():
                if conf > 0.4:  # Confidence threshold
                    objects.append({
                        'class': self.object_detector.names[int(cls)],
                        'confidence': float(conf),
                        'bbox': [float(x) for x in box],
                        'center': [(box[0] + box[2]) / 2, (box[1] + box[3]) / 2]
                    })
            
            return objects
            
        except Exception as e:
            logger.error(f"Error in object detection: {e}")
            return []
    
    def _detect_faces(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Detect faces in frame"""



        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            if hasattr(self.face_detector, 'detectMultiScale'):
                # Haar cascade detector
                faces = self.face_detector.detectMultiScale(
                    gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
                )
                
                face_list = []
                for (x, y, w, h) in faces:
                    face_list.append({
                        'bbox': [float(x), float(y), float(x+w), float(y+h)],
                        'confidence': 0.8,  # Haar cascade doesn't provide confidence
                        'center': [float(x + w/2), float(y + h/2)],
                        'size': float(w * h)
                    })
                
                return face_list
            else:
                # DNN-based detector
                blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), [104, 117, 123])
                self.face_detector.setInput(blob)
                detections = self.face_detector.forward()
                
                faces = []
                h, w = frame.shape[:2]
                
                for i in range(detections.shape[2]):
                    confidence = detections[0, 0, i, 2]
                    if confidence > 0.5:
                        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                        (x1, y1, x2, y2) = box.astype("int")
                        
                        faces.append({
                            'bbox': [float(x1), float(y1), float(x2), float(y2)],
                            'confidence': float(confidence),
                            'center': [float((x1 + x2) / 2), float((y1 + y2) / 2)],
                            'size': float((x2 - x1) * (y2 - y1))
                        })
                
                return faces
                
        except Exception as e:
            logger.error(f"Error in face detection: {e}")
            return []
    
    def _analyze_emotions(self, frame: np.ndarray, faces: List[Dict]) -> List[Dict[str, Any]]:
        """Analyze emotions for detected faces"""
        if not self.emotion_classifier:
            return []
        
        emotions = []
        emotion_labels = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
        
        try:
            for face in faces:
                bbox = face['bbox']
                x1, y1, x2, y2 = [int(coord) for coord in bbox]
                
                # Extract face region
                face_region = frame[y1:y2, x1:x2]
                if face_region.size == 0:
                    continue
                
                # Preprocess for emotion model
                face_resized = cv2.resize(face_region, (224, 224))
                face_rgb = cv2.cvtColor(face_resized, cv2.COLOR_BGR2RGB)
                face_tensor = torch.from_numpy(face_rgb).permute(2, 0, 1).float() / 255.0
                face_tensor = face_tensor.unsqueeze(0)
                
                if self.config.enable_gpu and torch.cuda.is_available():
                    face_tensor = face_tensor.cuda()
                
                # Predict emotion
                with torch.no_grad():
                    output = self.emotion_classifier(face_tensor)
                    probabilities = torch.softmax(output, dim=1)
                    predicted_emotion = torch.argmax(probabilities, dim=1).item()
                    confidence = probabilities[0][predicted_emotion].item()
                
                emotions.append({
                    'face_bbox': bbox,
                    'emotion': emotion_labels[predicted_emotion],
                    'confidence': float(confidence),
                    'all_probabilities': {
                        emotion_labels[i]: float(probabilities[0][i])
                        for i in range(len(emotion_labels))
                    }
                })
                
        except Exception as e:
            logger.error(f"Error in emotion analysis: {e}")
        
        return emotions
    
    def _classify_content(self, frame: np.ndarray) -> Dict[str, Any]:
        """Classify content type and safety"""
        if not self.content_classifier:
            return {'content_type': 'unknown', 'safety_score': 1.0}
        
        try:
            # Preprocess frame
            frame_resized = cv2.resize(frame, (224, 224))
            frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
            frame_tensor = torch.from_numpy(frame_rgb).permute(2, 0, 1).float() / 255.0
            frame_tensor = frame_tensor.unsqueeze(0)
            
            if self.config.enable_gpu and torch.cuda.is_available():
                frame_tensor = frame_tensor.cuda()
            
            # Classify content
            with torch.no_grad():
                output = self.content_classifier(frame_tensor)
                probabilities = torch.softmax(output, dim=1)
                predicted_class = torch.argmax(probabilities, dim=1).item()
                confidence = probabilities[0][predicted_class].item()
            
            content_classes = [
                'safe_general', 'educational', 'entertainment', 'music',
                'sports', 'news', 'gaming', 'creative', 'inappropriate', 'unsafe'
            ]
            
            content_type = content_classes[predicted_class] if predicted_class < len(content_classes) else 'unknown'
            
            # Calculate safety score (higher is safer)
            unsafe_categories = ['inappropriate', 'unsafe']
            safety_score = 1.0 - confidence if content_type in unsafe_categories else confidence
            
            return {
                'content_type': content_type,
                'content_confidence': float(confidence),
                'safety_score': float(safety_score)
            }
            
        except Exception as e:
            logger.error(f"Error in content classification: {e}")
            return {'content_type': 'unknown', 'safety_score': 1.0}
    
    def _analyze_frame_quality(self, frame: np.ndarray) -> Dict[str, float]:
        """Analyze frame quality metrics"""



        try:
            # Convert to grayscale for some metrics
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Calculate sharpness (Laplacian variance)
            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Calculate brightness
            brightness = np.mean(gray)
            
            # Calculate contrast (standard deviation)
            contrast = np.std(gray)
            
            # Calculate noise level (estimated)
            noise_level = self._estimate_noise(gray)
            
            # Calculate color saturation
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            saturation = np.mean(hsv[:, :, 1])
            
            # Overall quality score
            quality_score = self._calculate_quality_score(sharpness, brightness, contrast, noise_level)
            
            return {
                'sharpness': float(sharpness),
                'brightness': float(brightness),
                'contrast': float(contrast),
                'noise_level': float(noise_level),
                'saturation': float(saturation),
                'quality_score': float(quality_score)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing frame quality: {e}")
            return {}
    
    def _estimate_noise(self, gray_frame: np.ndarray) -> float:
        """Estimate noise level in grayscale frame"""



        try:
            # Use Laplacian to estimate noise
            laplacian = cv2.Laplacian(gray_frame, cv2.CV_64F)
            noise_estimate = np.sqrt(np.mean(laplacian**2))
            return min(noise_estimate / 100, 1.0)  # Normalize to 0-1
        except:
            return 0.0
    
    def _calculate_quality_score(self, sharpness: float, brightness: float, 
                               contrast: float, noise_level: float) -> float:
        """Calculate overall quality score (0-1)"""



        try:
            # Normalize individual metrics
            sharpness_score = min(sharpness / 1000, 1.0)  # Normalize sharpness
            brightness_score = 1.0 - abs(brightness - 128) / 128  # Optimal brightness around 128
            contrast_score = min(contrast / 80, 1.0)  # Normalize contrast
            noise_score = 1.0 - min(noise_level, 1.0)  # Lower noise is better
            
            # Weighted combination
            quality_score = (
                0.3 * sharpness_score +
                0.2 * brightness_score +
                0.3 * contrast_score +
                0.2 * noise_score
            )
            
            return max(0.0, min(1.0, quality_score))
        except:
            return 0.5  # Default quality score
    
    def analyze_frame_async(self, frame: np.ndarray, frame_id: int) -> bool:
        """Submit frame for asynchronous analysis"""
        if not self.is_running:
            return False
        
        if frame is None:
            logger.warning("Cannot analyze None frame")
            return False
        
        frame_data = {
            'frame': frame.copy(),
            'frame_id': frame_id,
            'timestamp': datetime.now()
        }
        
        try:
            self.analysis_queue.put_nowait(frame_data)
            return True
        except queue.Full:
            logger.warning("Analysis queue full, dropping frame")
            return False
    
    def get_analysis_result(self, timeout: float = 0.1) -> Optional[Dict[str, Any]]:
        """Get analysis result if available"""



        try:
            return self.result_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def get_latest_results(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get latest analysis results"""
        results = []
        try:
            while len(results) < count and not self.result_queue.empty():
                result = self.result_queue.get_nowait()
                results.append(result)
        except queue.Empty:
            pass
        return results

class PerformanceMonitor:
    """Real-time performance monitoring for streaming"""
    
    def __init__(self):
        self.metrics_history = deque(maxlen=1000)
        self.start_time = time.time()
        self.frame_count = 0
        self.last_fps_calculation = time.time()
        self.fps_frame_count = 0
        
    def record_frame_metrics(self, processing_time_ms: float, encoding_time_ms: float,
                           latency_ms: float, frame_drops: int = 0) -> StreamMetrics:
        """Record metrics for a processed frame"""
        # Normalize negative values
        processing_time_ms = max(0.0, processing_time_ms)
        encoding_time_ms = max(0.0, encoding_time_ms)
        latency_ms = max(0.0, latency_ms)
        frame_drops = max(0, frame_drops)
        
        current_time = time.time()
        self.frame_count += 1
        self.fps_frame_count += 1
        
        # Calculate FPS
        time_since_fps_calc = current_time - self.last_fps_calculation
        if time_since_fps_calc >= 1.0:  # Calculate FPS every second
            current_fps = self.fps_frame_count / time_since_fps_calc
            self.last_fps_calculation = current_time
            self.fps_frame_count = 0
        else:
            current_fps = self.fps_frame_count / max(time_since_fps_calc, 0.1)
        
        # Calculate average FPS
        total_time = current_time - self.start_time
        average_fps = self.frame_count / max(total_time, 1.0)
        
        # Get system metrics
        cpu_usage = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory()
        
        # Estimate bitrate (would be more accurate with actual video encoder data)
        estimated_bitrate = self._estimate_bitrate(processing_time_ms)
        
        # Create metrics object
        metrics = StreamMetrics(
            timestamp=datetime.now(),
            fps_current=current_fps,
            fps_average=average_fps,
            latency_ms=latency_ms,
            bitrate_kbps=estimated_bitrate,
            frame_drops=frame_drops,
            encoding_time_ms=encoding_time_ms,
            processing_time_ms=processing_time_ms,
            cpu_usage=cpu_usage,
            gpu_usage=self._get_gpu_usage(),
            memory_usage_mb=memory.used / (1024**2),
            bandwidth_usage_mbps=estimated_bitrate / 1000,
            quality_score=self._calculate_streaming_quality_score(
                current_fps, latency_ms, frame_drops
            )
        )
        
        self.metrics_history.append(metrics)
        return metrics
    
    def _estimate_bitrate(self, processing_time_ms: float) -> float:
        """Estimate bitrate based on processing performance"""
        # This is a simplified estimation - in production, you'd get this from the encoder
        base_bitrate = 5000  # kbps
        performance_factor = max(0.5, min(2.0, 50 / max(processing_time_ms, 1)))
        return base_bitrate * performance_factor
    
    def _get_gpu_usage(self) -> float:
        """Get GPU usage percentage"""



        try:
            if torch.cuda.is_available():
                return torch.cuda.utilization() if hasattr(torch.cuda, 'utilization') else 0.0
            return 0.0
        except:
            return 0.0
    
    def _calculate_streaming_quality_score(self, fps: float, latency: float, drops: int) -> float:
        """Calculate overall streaming quality score"""
        # FPS score (target 30 FPS)
        fps_score = min(fps / 30.0, 1.0)
        
        # Latency score (target <100ms)
        latency_score = max(0.0, 1.0 - latency / 200.0)
        
        # Drop score (target 0 drops)
        drop_score = max(0.0, 1.0 - drops / 10.0)
        
        return (fps_score * 0.4 + latency_score * 0.4 + drop_score * 0.2)
    
    def get_latest_metrics(self) -> Optional[StreamMetrics]:
        """Get the latest recorded metrics"""
        if self.metrics_history:
            return self.metrics_history[-1]
        return None

class LiveStreamProcessor:
    """Advanced live streaming processor with real-time AI analysis"""
    
    def __init__(self, config: StreamingConfig):
        self.config = config
        self.is_streaming = False
        self.stream_thread = None
        self.input_source = None
        self.output_destinations = []
        
        # Initialize components
        self.adaptive_bitrate = AdaptiveBitrate(config)
        self.realtime_analyzer = RealTimeAnalyzer(config)
        self.performance_monitor = PerformanceMonitor()
        
        # Streaming state
        self.current_frame = None
        self.frame_counter = 0
        self.last_adaptation_time = time.time()
        self.enhancement_pipeline = None
        
        # Initialize enhancement pipeline if enabled
        if config.enable_realtime_enhancement:
            self._initialize_enhancement_pipeline()
    
    def _initialize_enhancement_pipeline(self):
        """Initialize real-time enhancement pipeline"""



        try:
            # Import enhancement modules
            from .enhancement import ImageEnhancer, EnhancementSettings
            
            # Create lightweight enhancement settings for real-time processing
            enhancement_settings = EnhancementSettings(
                enable_noise_reduction=True,
                enable_color_correction=True,
                enable_sharpening=True,
                enable_contrast_enhancement=True,
                processing_speed='fast',  # Prioritize speed over quality
                gpu_acceleration=self.config.enable_gpu
            )
            
            self.enhancement_pipeline = ImageEnhancer(enhancement_settings)
            logger.info("Real-time enhancement pipeline initialized")
            
        except Exception as e:
            logger.warning(f"Enhancement pipeline not available: {e}")
            self.enhancement_pipeline = None
    
    def start_streaming(self, input_source: str, output_destinations: List[str]):
        """Start live streaming with real-time processing"""
        if self.is_streaming:
            logger.warning("Streaming already in progress")
            return False
        
        try:
            self.input_source = input_source
            self.output_destinations = output_destinations
            
            # Start real-time analyzer
            self.realtime_analyzer.start_analysis()
            
            # Start streaming thread
            self.is_streaming = True
            self.stream_thread = threading.Thread(
                target=self._streaming_loop,
                name="LiveStreamProcessor",
                daemon=True
            )
            self.stream_thread.start()
            
            logger.info(f"Live streaming started: {input_source} -> {output_destinations}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start streaming: {e}")
            self.stop_streaming()
            return False
    
    def stop_streaming(self):
        """Stop live streaming"""
        self.is_streaming = False
        
        # Stop real-time analyzer
        self.realtime_analyzer.stop_analysis()
        
        # Wait for streaming thread to finish
        if self.stream_thread and self.stream_thread.is_alive():
            self.stream_thread.join(timeout=5.0)
        
        logger.info("Live streaming stopped")
    
    def get_current_metrics(self) -> Optional[StreamMetrics]:
        """Get current streaming metrics"""



        return self.performance_monitor.get_latest_metrics()
    
    def get_analysis_results(self) -> List[Dict]:
        """Get latest analysis results from real-time analyzer"""



        return self.realtime_analyzer.get_latest_results()
    
    def _streaming_loop(self):
        """Main streaming processing loop"""



        try:
            # Initialize video capture
            cap = self._initialize_video_capture()
            if cap is None:
                return
            
            # Initialize video writers for output destinations
            writers = self._initialize_video_writers()
            
            logger.info("Streaming loop started")
            
            while self.is_streaming:
                loop_start_time = time.time()
                
                # Capture frame
                ret, frame = cap.read()
                if not ret:
                    logger.warning("Failed to capture frame")
                    break
                
                self.current_frame = frame
                self.frame_counter += 1
                
                # Process frame
                processed_frame = self._process_frame(frame)
                
                # Submit for AI analysis (non-blocking)
                if self.config.enable_realtime_detection:
                    self.realtime_analyzer.analyze_frame_async(frame, self.frame_counter)
                
                # Write to output destinations
                encoding_start_time = time.time()
                for writer in writers:
                    if writer is not None:
                        writer.write(processed_frame)
                encoding_time = (time.time() - encoding_start_time) * 1000
                
                # Calculate processing time
                processing_time = (time.time() - loop_start_time) * 1000
                
                # Record performance metrics
                latency = processing_time  # Simplified latency calculation
                metrics = self.performance_monitor.record_frame_metrics(
                    processing_time, encoding_time, latency
                )
                
                # Adaptive quality management
                if time.time() - self.last_adaptation_time > 5.0:  # Check every 5 seconds
                    self._adapt_streaming_quality(metrics)
                    self.last_adaptation_time = time.time()
                
                # Frame rate control
                self._control_frame_rate(loop_start_time)
                
                # Memory management
                if self.frame_counter % 100 == 0:
                    gc.collect()
            
        except Exception as e:
            logger.error(f"Error in streaming loop: {e}")
        finally:
            # Cleanup
            if 'cap' in locals() and cap is not None:
                cap.release()
            if 'writers' in locals():
                for writer in writers:
                    if writer is not None:
                        writer.release()
            cv2.destroyAllWindows()
    
    def _initialize_video_capture(self):
        """Initialize video capture from input source"""



        try:
            if self.input_source.isdigit():
                # Camera input
                cap = cv2.VideoCapture(int(self.input_source))
            elif self.input_source.startswith(('rtmp://', 'rtsp://', 'http://')):
                # Network stream
                cap = cv2.VideoCapture(self.input_source)
            else:
                # File input
                cap = cv2.VideoCapture(self.input_source)
            
            if not cap.isOpened():
                logger.error(f"Failed to open input source: {self.input_source}")
                return None
            
            # Configure capture settings
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.input_resolution[0])
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.input_resolution[1])
            cap.set(cv2.CAP_PROP_FPS, self.config.fps)
            
            return cap
            
        except Exception as e:
            logger.error(f"Error initializing video capture: {e}")
            return None
    
    def _initialize_video_writers(self):
        """Initialize video writers for output destinations"""
        writers = []
        
        for destination in self.output_destinations:
            try:
                if destination.startswith('rtmp://'):
                    # RTMP streaming output
                    writer = self._create_rtmp_writer(destination)
                elif destination.endswith('.mp4'):
                    # File output
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                    writer = cv2.VideoWriter(
                        destination, fourcc, self.config.fps,
                        self.config.output_resolution
                    )
                else:
                    logger.warning(f"Unsupported output destination: {destination}")
                    writer = None
                
                writers.append(writer)
                
            except Exception as e:
                logger.error(f"Error creating writer for {destination}: {e}")
                writers.append(None)
        
        return writers
    
    def _create_rtmp_writer(self, rtmp_url: str):
        """Create RTMP writer using FFmpeg"""



        try:
            # This would use FFmpeg for RTMP output
            # For now, return None as it requires FFmpeg integration
            logger.warning("RTMP output requires FFmpeg integration")
            return None
        except Exception as e:
            logger.error(f"Error creating RTMP writer: {e}")
            return None
    
    def _process_frame(self, frame: np.ndarray) -> np.ndarray:
        """Process frame with enhancement and filters"""



        try:
            processed_frame = frame.copy()
            
            # Apply real-time enhancement if enabled
            if self.enhancement_pipeline and self.config.enable_realtime_enhancement:
                processed_frame = self.enhancement_pipeline.enhance_frame_realtime(processed_frame)
            
            # Resize to output resolution if needed
            if frame.shape[:2][::-1] != self.config.output_resolution:
                processed_frame = cv2.resize(processed_frame, self.config.output_resolution)
            
            return processed_frame
            
        except Exception as e:
            logger.error(f"Error processing frame: {e}")
            return frame
    
    def _adapt_streaming_quality(self, metrics: StreamMetrics):
        """Adapt streaming quality based on performance metrics"""



        try:
            # Get quality adaptation recommendation
            adaptation = self.adaptive_bitrate.recommend_quality_adaptation(metrics)
            
            if adaptation.target_quality != adaptation.current_quality:
                logger.info(f"Adapting quality: {adaptation.current_quality} -> {adaptation.target_quality}")
                logger.info(f"Reason: {adaptation.adaptation_reason}")
                
                # Apply new settings
                self._apply_quality_settings(adaptation.recommended_settings)
                self.adaptive_bitrate.current_level = adaptation.target_quality
            
            # Update adaptive bitrate metrics
            self.adaptive_bitrate.metrics_history.append(metrics)
            
        except Exception as e:
            logger.error(f"Error in quality adaptation: {e}")
    
    def _apply_quality_settings(self, settings: Dict[str, Any]):
        """Apply new quality settings to streaming pipeline"""



        try:
            # Update output resolution
            if 'width' in settings and 'height' in settings:
                self.config.output_resolution = (settings['width'], settings['height'])
            
            # Update FPS
            if 'fps' in settings:
                self.config.fps = settings['fps']
            
            # Update bitrate (would be applied to encoder)
            if 'bitrate' in settings:
                self.config.bitrate = settings['bitrate']
            
            logger.info(f"Applied quality settings: {settings}")
            
        except Exception as e:
            logger.error(f"Error applying quality settings: {e}")
    
    def _control_frame_rate(self, loop_start_time: float):
        """Control frame rate to maintain target FPS"""



        try:
            target_frame_time = 1.0 / self.config.fps
            elapsed_time = time.time() - loop_start_time
            
            if elapsed_time < target_frame_time:
                sleep_time = target_frame_time - elapsed_time
                time.sleep(sleep_time)
                
        except Exception as e:
            logger.error(f"Error in frame rate control: {e}")
    
    def get_current_metrics(self) -> Optional[StreamMetrics]:
        """Get current streaming metrics"""
        if self.performance_monitor.metrics_history:
            return self.performance_monitor.metrics_history[-1]
        return None
    
    def get_analysis_results(self) -> List[Dict[str, Any]]:
        """Get latest AI analysis results"""
        results = []
        while True:
            result = self.realtime_analyzer.get_analysis_result(timeout=0.001)
            if result is None:
                break
            results.append(result)
        return results

class StreamOptimizer:
    """Advanced stream optimization engine"""
    
    def __init__(self, config: StreamingConfig):
        self.config = config
        self.optimization_history = deque(maxlen=500)
        self.performance_baselines = {}
        self.optimization_strategies = []
        
        # Initialize optimization strategies
        self._initialize_optimization_strategies()
    
    def _initialize_optimization_strategies(self):
        """Initialize various optimization strategies"""
        self.optimization_strategies = [
            self._cpu_optimization_strategy,
            self._memory_optimization_strategy,
            self._network_optimization_strategy,
            self._gpu_optimization_strategy,
            self._quality_optimization_strategy
        ]
    
    def optimize_stream_settings(self, metrics: StreamMetrics, 
                               analysis_results: List[Dict]) -> Dict[str, Any]:
        """Optimize streaming settings based on performance and content analysis"""



        try:
            optimization_recommendations = {
                'settings_changes': {},
                'performance_improvements': [],
                'quality_adjustments': [],
                'resource_optimizations': []
            }
            
            # Run optimization strategies
            for strategy in self.optimization_strategies:
                strategy_result = strategy(metrics, analysis_results)
                if strategy_result:
                    optimization_recommendations = self._merge_recommendations(
                        optimization_recommendations, strategy_result
                    )
            
            # Apply machine learning-based optimization
            ml_recommendations = self._ml_based_optimization(metrics, analysis_results)
            if ml_recommendations:
                optimization_recommendations = self._merge_recommendations(
                    optimization_recommendations, ml_recommendations
                )
            
            return optimization_recommendations
            
        except Exception as e:
            logger.error(f"Error in stream optimization: {e}")
            return {}
    
    def _cpu_optimization_strategy(self, metrics: StreamMetrics, 
                                 analysis_results: List[Dict]) -> Dict[str, Any]:
        """CPU-focused optimization strategy"""
        if metrics.cpu_usage < 60:
            return {}
        
        recommendations = {
            'settings_changes': {},
            'performance_improvements': ['Reduce CPU load'],
            'resource_optimizations': []
        }
        
        # High CPU usage optimizations
        if metrics.cpu_usage > 85:
            recommendations['settings_changes'].update({
                'processing_threads': max(1, self.config.processing_threads // 2),
                'enable_realtime_enhancement': False,
                'detection_interval': 3  # Process every 3rd frame
            })
            recommendations['resource_optimizations'].append('Reduced processing threads')
            recommendations['resource_optimizations'].append('Disabled real-time enhancement')
        
        elif metrics.cpu_usage > 70:
            recommendations['settings_changes'].update({
                'detection_interval': 2,  # Process every 2nd frame
                'enhancement_quality': 'fast'
            })
            recommendations['resource_optimizations'].append('Reduced detection frequency')
        
        return recommendations
    
    def _memory_optimization_strategy(self, metrics: StreamMetrics, 
                                    analysis_results: List[Dict]) -> Dict[str, Any]:
        """Memory-focused optimization strategy"""
        memory_usage_gb = metrics.memory_usage_mb / 1024
        
        if memory_usage_gb < 4.0:
            return {}
        
        recommendations = {
            'settings_changes': {},
            'performance_improvements': ['Optimize memory usage'],
            'resource_optimizations': []
        }
        
        # High memory usage optimizations
        if memory_usage_gb > 8.0:
            recommendations['settings_changes'].update({
                'buffer_size': max(2, self.config.buffer_size // 2),
                'max_model_cache': 2,
                'gc_frequency': 50  # More frequent garbage collection
            })
            recommendations['resource_optimizations'].append('Reduced buffer sizes')
            recommendations['resource_optimizations'].append('Increased garbage collection')
        
        elif memory_usage_gb > 6.0:
            recommendations['settings_changes'].update({
                'buffer_size': max(3, self.config.buffer_size - 1),
                'gc_frequency': 100
            })
        
        return recommendations
    
    def _network_optimization_strategy(self, metrics: StreamMetrics, 
                                     analysis_results: List[Dict]) -> Dict[str, Any]:
        """Network-focused optimization strategy"""
        if metrics.latency_ms < 150 and metrics.frame_drops < 3:
            return {}
        
        recommendations = {
            'settings_changes': {},
            'performance_improvements': ['Optimize network performance'],
            'quality_adjustments': []
        }
        
        # High latency or frame drops
        if metrics.latency_ms > 300 or metrics.frame_drops > 10:
            recommendations['settings_changes'].update({
                'bitrate': int(self.config.bitrate * 0.7),
                'buffer_size': min(10, self.config.buffer_size + 2),
                'adaptive_bitrate_sensitivity': 'high'
            })
            recommendations['quality_adjustments'].append('Reduced bitrate for stability')
        
        elif metrics.latency_ms > 200 or metrics.frame_drops > 5:
            recommendations['settings_changes'].update({
                'bitrate': int(self.config.bitrate * 0.85),
                'buffer_size': min(8, self.config.buffer_size + 1)
            })
        
        return recommendations
    
    def _gpu_optimization_strategy(self, metrics: StreamMetrics, 
                                 analysis_results: List[Dict]) -> Dict[str, Any]:
        """GPU-focused optimization strategy"""
        if not self.config.enable_gpu or metrics.gpu_usage < 70:
            return {}
        
        recommendations = {
            'settings_changes': {},
            'performance_improvements': ['Optimize GPU usage'],
            'resource_optimizations': []
        }
        
        # High GPU usage optimizations
        if metrics.gpu_usage > 90:
            recommendations['settings_changes'].update({
                'model_batch_size': 1,
                'gpu_memory_fraction': 0.7,
                'model_precision': 'fp16'  # Use half precision
            })
            recommendations['resource_optimizations'].append('Reduced GPU memory usage')
        
        elif metrics.gpu_usage > 80:
            recommendations['settings_changes'].update({
                'model_batch_size': 2,
                'gpu_memory_fraction': 0.8
            })
        
        return recommendations
    
    def _quality_optimization_strategy(self, metrics: StreamMetrics, 
                                     analysis_results: List[Dict]) -> Dict[str, Any]:
        """Content quality-focused optimization strategy"""
        recommendations = {
            'settings_changes': {},
            'quality_adjustments': []
        }
        
        # Analyze content complexity from AI results
        avg_object_count = 0
        avg_face_count = 0
        total_frames = len(analysis_results)
        
        if total_frames > 0:
            for result in analysis_results:
                avg_object_count += len(result.get('objects', []))
                avg_face_count += len(result.get('faces', []))
            
            avg_object_count /= total_frames
            avg_face_count /= total_frames
        
        # Adjust processing based on content complexity
        if avg_object_count > 10 or avg_face_count > 3:
            # Complex content - may need more processing power
            recommendations['settings_changes'].update({
                'detection_confidence_threshold': 0.6,  # Higher threshold
                'max_detections_per_frame': 20
            })
            recommendations['quality_adjustments'].append('Optimized for complex content')
        
        elif avg_object_count < 3 and avg_face_count < 1:
            # Simple content - can use lighter processing
            recommendations['settings_changes'].update({
                'detection_confidence_threshold': 0.4,  # Lower threshold
                'processing_interval': 2  # Process every other frame
            })
            recommendations['quality_adjustments'].append('Optimized for simple content')
        
        return recommendations
    
    def _ml_based_optimization(self, metrics: StreamMetrics, 
                             analysis_results: List[Dict]) -> Dict[str, Any]:
        """Machine learning-based optimization recommendations"""



        try:
            # This would use a trained ML model to predict optimal settings
            # For now, implement rule-based heuristics
            
            # Calculate performance score
            performance_score = (
                min(metrics.fps_current / 30, 1.0) * 0.3 +
                max(0, 1 - metrics.latency_ms / 500) * 0.3 +
                max(0, 1 - metrics.cpu_usage / 100) * 0.2 +
                max(0, 1 - metrics.frame_drops / 20) * 0.2
            )
            
            recommendations = {
                'settings_changes': {},
                'performance_improvements': [f'ML optimization (score: {performance_score:.2f})']
            }
            
            # ML-based recommendations based on performance patterns
            if performance_score < 0.6:
                # Poor performance - aggressive optimization
                recommendations['settings_changes'].update({
                    'aggressive_optimization': True,
                    'quality_preset': 'performance',
                    'ai_processing_mode': 'lightweight'
                })
            elif performance_score > 0.8:
                # Good performance - can enhance quality
                recommendations['settings_changes'].update({
                    'quality_preset': 'balanced',
                    'ai_processing_mode': 'standard',
                    'enable_advanced_features': True
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error in ML-based optimization: {e}")
            return {}
    
    def _merge_recommendations(self, base: Dict, additional: Dict) -> Dict:
        """Merge optimization recommendations"""
        result = base.copy()
        
        for key, value in additional.items():
            if key in result:
                if isinstance(value, dict):
                    result[key].update(value)
                elif isinstance(value, list):
                    result[key].extend(value)
                else:
                    result[key] = value
            else:
                result[key] = value
        
        return result

# Export classes
__all__ = [
    'LiveStreamProcessor',
    'RealTimeAnalyzer', 
    'StreamOptimizer',
    'AdaptiveBitrate',
    'StreamingConfig',
    'StreamMetrics',
    'QualityAdaptation',
    'PerformanceMonitor'
]
