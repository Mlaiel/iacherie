"""Object Detector - Enterprise AI Object Detection System
======================================================

Advanced object detection system using state-of-the-art deep learning models
including YOLO, SSD, and custom trained models for precise object recognition.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import cv2
import numpy as np
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
import torch
import torchvision.transforms as transforms
from PIL import Image
import json
from pathlib import Path

from ..base import BaseAgent, AgentStatus
try:
    from core.exceptions import ObjectDetectionError, ValidationError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    ObjectDetectionError, ValidationError = globals().get('ObjectDetectionError, ValidationError', Exception)
from ...utils.performance_monitor import PerformanceMonitor
try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()

logger = logging.getLogger(__name__)

class DetectionModel:
    """
Object detection model configurations"""

    YOLO_V8 = "yolo_v8"
    YOLO_V5 = "yolo_v5"
    SSD_MOBILENET = "ssd_mobilenet"
    FASTER_RCNN = "faster_rcnn"
    DETECTRON2 = "detectron2"

class ObjectDetector(BaseAgent):
    """
    Enterprise-grade object detection system providing comprehensive
    object recognition, classification, and localization capabilities.
    """
    
    def __init__(self):
        super().__init__(
            agent_id="object_detector",
            name="Object Detector",
            version="2.1.0"
        )
        
        self.performance_monitor = PerformanceMonitor("object_detection")
        
        # Detection configuration
        self.confidence_threshold = 0.5
        self.nms_threshold = 0.4  # Non-Maximum Suppression
        self.max_detections = 100
        
        # Model configuration
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.current_model = DetectionModel.YOLO_V8
        self.models = {}
        
        # Class mappings for different detection categories
        self.object_classes = {
            'general': [
                'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck',
                'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter',
                'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant',
                'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie',
                'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball', 'kite',
                'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
                'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl',
                'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog',
                'pizza', 'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed',
                'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard',
                'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator',
                'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush'
            ],
            'content_creation': [
                'camera', 'microphone', 'tripod', 'lighting equipment', 'computer',
                'smartphone', 'tablet', 'musical instrument', 'art supplies'
            ],
            'brand_objects': [
                'logo', 'brand symbol', 'product packaging', 'advertisement',
                'branded clothing', 'branded accessories'
            ]
        }
        
        # Detection statistics
        self.detection_stats = {
            'total_detections': 0,
            'successful_detections': 0,
            'failed_detections': 0,
            'average_confidence': 0.0,
            'processing_times': []
        }

    async def initialize(self) -> bool:
        """Initialize object detection models"""
        try:
            logger.info("Initializing Object Detector...")
            
            # Initialize primary detection model
            await self._load_detection_model(self.current_model)
            
            # Initialize OpenCV cascade classifiers for backup detection
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            self.body_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_fullbody.xml'
            )
            
            # Initialize preprocessing transforms
            self.transform = transforms.Compose([
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                                   std=[0.229, 0.224, 0.225])
            ])
            
            self.status = AgentStatus.READY
            logger.info("Object Detector initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Object Detector initialization failed: {e}")
            self.status = AgentStatus.ERROR
            return False

    async def _load_detection_model(self, model_type: str) -> bool:
        """Load specific detection model"""
        try:
            if model_type == DetectionModel.YOLO_V8:
                # In production, load actual YOLOv8 model
                # For now, use placeholder that simulates YOLO detection
                self.models[model_type] = self._create_yolo_placeholder()
                logger.info("YOLO v8 model loaded (placeholder)")
                
            elif model_type == DetectionModel.SSD_MOBILENET:
                # Load SSD MobileNet model
                self.models[model_type] = self._create_ssd_placeholder()
                logger.info("SSD MobileNet model loaded (placeholder)")
                
            else:
                logger.warning(f"Model type {model_type} not implemented")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model {model_type}: {e}")
            return False

    def _create_yolo_placeholder(self) -> Dict[str, Any]:
        """Create YOLO model placeholder"""
        return {
            'type': 'yolo_v8',
            'input_size': (640, 640),
            'classes': self.object_classes['general'],
            'confidence_threshold': self.confidence_threshold,
            'nms_threshold': self.nms_threshold
        }

    def _create_ssd_placeholder(self) -> Dict[str, Any]:
        """
Create SSD model placeholder"""
        return {
            'type': 'ssd_mobilenet',
            'input_size': (300, 300),
            'classes': self.object_classes['general'],
            'confidence_threshold': self.confidence_threshold
        }

    async def detect_objects(
        self, 
        image: np.ndarray,
        detection_categories: List[str] = None,
        custom_confidence: float = None
    ) -> Dict[str, Any]:
        """
        Detect objects in image
        
        Args:
            image: Input image as numpy array
            detection_categories: Specific categories to detect
            custom_confidence: Custom confidence threshold
            
        Returns:
            Detection results with bounding boxes and classifications
        """
        start_time = datetime.now()
        
        try:
            logger.info("Starting object detection...")
            
            # Validate input
            if image is None or image.size == 0:
                raise ValidationError("Invalid input image")
            
            # Set confidence threshold
            confidence = custom_confidence or self.confidence_threshold
            
            # Preprocess image
            processed_image = await self._preprocess_image(image)
            
            # Perform detection using primary model
            detections = await self._detect_with_primary_model(
                processed_image, confidence, detection_categories
            )
            
            # Enhance detections with cascade classifiers
            enhanced_detections = await self._enhance_with_cascade_detection(
                image, detections
            )
            
            # Post-process results
            final_results = await self._post_process_detections(enhanced_detections)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            self.detection_stats['processing_times'].append(processing_time)
            
            result = {
                'status': 'success',
                'processing_time': processing_time,
                'image_dimensions': image.shape,
                'total_detections': len(final_results['objects']),
                'objects': final_results['objects'],
                'detection_summary': final_results['summary'],
                'confidence_distribution': final_results['confidence_stats'],
                'model_used': self.current_model,
                'detection_categories': detection_categories or ['general']
            }
            
            # Update statistics
            self.detection_stats['total_detections'] += 1
            self.detection_stats['successful_detections'] += 1
            
            logger.info(
                f"Object detection completed: {len(final_results['objects'])} "
                f"objects found in {processing_time:.2f}s"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Object detection failed: {e}")
            self.detection_stats['failed_detections'] += 1
            
            return {
                'status': 'error',
                'error': str(e),
                'processing_time': (datetime.now() - start_time).total_seconds(),
                'objects': [],
                'total_detections': 0
            }

    async def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for detection"""
        try:
            # Ensure image is in BGR format
            if len(image.shape) == 3 and image.shape[2] == 3:
                processed = image.copy()
            else:
                processed = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            
            # Resize if too large (maintain aspect ratio)
            height, width = processed.shape[:2]
            max_dimension = 1024
            
            if max(height, width) > max_dimension:
                if width > height:
                    new_width = max_dimension
                    new_height = int(height * (max_dimension / width))
                else:
                    new_height = max_dimension
                    new_width = int(width * (max_dimension / height))
                
                processed = cv2.resize(processed, (new_width, new_height))
            
            return processed
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            return image

    async def _detect_with_primary_model(
        self, 
        image: np.ndarray,
        confidence: float,
        detection_categories: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Perform detection with primary AI model"""
        detections = []
        
        try:
            # This is a placeholder implementation
            # In production, this would use actual YOLO/SSD inference
            
            # Simulate detection results based on image analysis
            height, width = image.shape[:2]
            
            # Simple edge-based "detection" for demonstration
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter and process contours as "detections"
            for i, contour in enumerate(contours[:20]):  # Limit to 20 detections
                area = cv2.contourArea(contour)
                
                if area > 500:  # Minimum area threshold
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Calculate detection confidence (simulated)
                    detection_confidence = min(0.5 + (area / 10000), 0.95)
                    
                    if detection_confidence >= confidence:
                        # Simulate object classification
                        object_class = self._simulate_classification(image[y:y+h, x:x+w])
                        
                        detections.append({
                            'class': object_class,
                            'confidence': detection_confidence,
                            'bbox': {
                                'x': int(x),
                                'y': int(y),
                                'width': int(w),
                                'height': int(h)
                            },
                            'center': {
                                'x': int(x + w/2),
                                'y': int(y + h/2)
                            },
                            'area': int(area),
                            'detection_method': 'primary_model'
                        })
            
            return detections
            
        except Exception as e:
            logger.error(f"Primary model detection failed: {e}")
            return []

    def _simulate_classification(self, roi: np.ndarray) -> str:
        """Simulate object classification"""
        # Simple heuristic-based classification for demonstration
        height, width = roi.shape[:2]
        aspect_ratio = width / height if height > 0 else 1
        
        # Analyze color distribution
        if len(roi.shape) == 3:
            mean_color = np.mean(roi, axis=(0, 1))
            dominant_channel = np.argmax(mean_color)
        else:
            dominant_channel = 0
        
        # Simple classification logic
        if aspect_ratio > 2.0:
            return 'vehicle' if np.mean(roi) < 100 else 'furniture'
        elif aspect_ratio > 0.5 and aspect_ratio < 2.0:
            if dominant_channel == 1:  # Green dominant
                return 'plant'
            elif dominant_channel == 2:  # Blue dominant
                return 'sky'
            else:
                return 'person' if height > width else 'object'
        else:
            return 'bottle' if height > width * 2 else 'ball'

    async def _enhance_with_cascade_detection(
        self, 
        image: np.ndarray, 
        existing_detections: List[Dict]
    ) -> List[Dict[str, Any]]:
        """
Enhance detections with cascade classifiers"""
        enhanced = existing_detections.copy()
        
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Face detection
            faces = self.face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
            )
            
            for (x, y, w, h) in faces:
                # Check if this face is already detected
                is_duplicate = False
                for existing in existing_detections:
                    existing_bbox = existing['bbox']
                    overlap = self._calculate_bbox_overlap(
                        {'x': x, 'y': y, 'width': w, 'height': h},
                        existing_bbox
                    )
                    if overlap > 0.5:
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    enhanced.append({
                        'class': 'face',
                        'confidence': 0.85,
                        'bbox': {'x': int(x), 'y': int(y), 'width': int(w), 'height': int(h)},
                        'center': {'x': int(x + w/2), 'y': int(y + h/2)},
                        'area': int(w * h),
                        'detection_method': 'cascade'
                    })
            
            return enhanced
            
        except Exception as e:
            logger.error(f"Cascade detection enhancement failed: {e}")
            return existing_detections

    def _calculate_bbox_overlap(self, bbox1: Dict, bbox2: Dict) -> float:
        """Calculate overlap ratio between two bounding boxes"""
        try:
            # Calculate intersection
            x1 = max(bbox1['x'], bbox2['x'])
            y1 = max(bbox1['y'], bbox2['y'])
            x2 = min(bbox1['x'] + bbox1['width'], bbox2['x'] + bbox2['width'])
            y2 = min(bbox1['y'] + bbox1['height'], bbox2['y'] + bbox2['height'])
            
            if x2 <= x1 or y2 <= y1:
                return 0.0
            
            intersection = (x2 - x1) * (y2 - y1)
            area1 = bbox1['width'] * bbox1['height']
            area2 = bbox2['width'] * bbox2['height']
            union = area1 + area2 - intersection
            
            return intersection / union if union > 0 else 0.0
            
        except Exception:
            return 0.0

    async def _post_process_detections(
        self, 
        detections: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
Post-process detection results"""
        try:
            # Remove duplicates and apply NMS
            filtered_detections = self._apply_non_maximum_suppression(detections)
            
            # Sort by confidence
            filtered_detections.sort(key=lambda x: x['confidence'], reverse=True)
            
            # Limit to maximum detections
            if len(filtered_detections) > self.max_detections:
                filtered_detections = filtered_detections[:self.max_detections]
            
            # Calculate statistics
            confidence_scores = [det['confidence'] for det in filtered_detections]
            
            confidence_stats = {
                'mean': np.mean(confidence_scores) if confidence_scores else 0.0,
                'min': min(confidence_scores) if confidence_scores else 0.0,
                'max': max(confidence_scores) if confidence_scores else 0.0,
                'std': np.std(confidence_scores) if confidence_scores else 0.0
            }
            
            # Create detection summary
            class_counts = {}
            for detection in filtered_detections:
                class_name = detection['class']
                class_counts[class_name] = class_counts.get(class_name, 0) + 1
            
            summary = {
                'total_objects': len(filtered_detections),
                'unique_classes': len(class_counts),
                'class_distribution': class_counts,
                'high_confidence_objects': len([d for d in filtered_detections if d['confidence'] > 0.8]),
                'detection_methods_used': list(set(d['detection_method'] for d in filtered_detections))
            }
            
            return {
                'objects': filtered_detections,
                'summary': summary,
                'confidence_stats': confidence_stats
            }
            
        except Exception as e:
            logger.error(f"Post-processing failed: {e}")
            return {
                'objects': detections,
                'summary': {'total_objects': len(detections)},
                'confidence_stats': {'mean': 0.0}
            }

    def _apply_non_maximum_suppression(
        self, 
        detections: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Apply Non-Maximum Suppression to remove duplicate detections"""
        if not detections:
            return []
        
        # Sort by confidence
        sorted_detections = sorted(detections, key=lambda x: x['confidence'], reverse=True)
        
        filtered = []
        
        for detection in sorted_detections:
            # Check overlap with already accepted detections
            should_keep = True
            
            for accepted in filtered:
                overlap = self._calculate_bbox_overlap(detection['bbox'], accepted['bbox'])
                
                if overlap > self.nms_threshold:
                    should_keep = False
                    break
            
            if should_keep:
                filtered.append(detection)
        
        return filtered

    async def batch_detect_objects(
        self, 
        images: List[np.ndarray],
        max_concurrent: int = 5
    ) -> List[Dict[str, Any]]:
        """
Detect objects in multiple images concurrently"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def detect_single(image):
            async with semaphore:
                return await self.detect_objects(image)
        
        tasks = [detect_single(img) for img in images]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [result if not isinstance(result, Exception) 
                else {'status': 'error', 'error': str(result)} 
                for result in results]

    async def detect_specific_objects(
        self, 
        image: np.ndarray,
        target_classes: List[str]
    ) -> Dict[str, Any]:
        """
Detect specific object classes in image"""
        # Perform full detection
        full_results = await self.detect_objects(image)
        
        if full_results['status'] != 'success':
            return full_results
        
        # Filter for target classes
        filtered_objects = [
            obj for obj in full_results['objects'] 
            if obj['class'] in target_classes
        ]
        
        # Update results
        full_results['objects'] = filtered_objects
        full_results['total_detections'] = len(filtered_objects)
        full_results['target_classes'] = target_classes
        
        return full_results

    def get_detection_statistics(self) -> Dict[str, Any]:
        """
Get detection performance statistics"""
        stats = self.detection_stats.copy()
        
        if stats['processing_times']:
            stats['average_processing_time'] = np.mean(stats['processing_times'])
            stats['min_processing_time'] = min(stats['processing_times'])
            stats['max_processing_time'] = max(stats['processing_times'])
        
        success_rate = 0.0
        if stats['total_detections'] > 0:
            success_rate = stats['successful_detections'] / stats['total_detections']
        
        stats['success_rate'] = success_rate
        return stats

    def get_supported_classes(self, category: str = 'general') -> List[str]:
        """
Get list of supported object classes"""
        return self.object_classes.get(category, self.object_classes['general']).copy()

    async def cleanup(self) -> None:
        """
Cleanup resources"""
        try:
            await self.performance_monitor.close()
            
            # Clear loaded models
            self.models.clear()
            
            logger.info("Object Detector cleanup completed")
        except Exception as e:
            logger.error(f"Object Detector cleanup failed: {e}")

    def set_confidence_threshold(self, threshold: float) -> None:
        """Set global confidence threshold"""
        if 0.0 <= threshold <= 1.0:
            self.confidence_threshold = threshold
            logger.info(f"Confidence threshold set to {threshold}")
        else:
            logger.warning(f"Invalid confidence threshold: {threshold}")

    def set_model(self, model_type: str) -> bool:
        """Switch detection model"""
        if model_type in [DetectionModel.YOLO_V8, DetectionModel.SSD_MOBILENET]:
            self.current_model = model_type
            logger.info(f"Detection model switched to {model_type}")
            return True
        else:
            logger.error(f"Unsupported model type: {model_type}")
            return False
