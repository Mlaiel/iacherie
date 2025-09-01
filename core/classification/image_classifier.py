"""Image Content Classification System

Advanced AI-powered image classification for content protection and analysis.
Provides visual recognition, style analysis, quality assessment, and similarity matching.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent with Content Protection
Team: Lead Dev IA + Backend Senior + ML Engineer + DevOps + DBA + Security + Microservices + Audio + IA Prompt Engineer

Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: mlaiel@live.de for licensing and collaboration.

⚠️ STRONG WARNING: This code and concept are the exclusive property of Fahed Mlaiel.
Any unauthorized use, copying, or distribution without explicit written permission
from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will be prosecuted
to the full extent of the law.
"""

import cv2
import numpy as np
import torch
import torchvision.transforms as transforms
from typing import Dict, List, Optional, Tuple, Any, Union
import logging
from pathlib import Path
import hashlib
from PIL import Image, ImageStat, ImageFilter
import imagehash
from transformers import CLIPProcessor, CLIPModel, BlipProcessor, BlipForConditionalGeneration
import face_recognition
from scipy.spatial.distance import cosine
import tensorflow as tf
from sklearn.cluster import KMeans
import colorsys

from ..engines.ml_engine import MLEngine
from ..processors.image_processor import ImageProcessor
from ...utils.cache_manager import cache_result
from ...utils.metrics import track_performance
from ...utils.exceptions import ClassificationError
from ...config.settings import get_settings

logger = logging.getLogger(__name__)


class ImageContentClassifier:
    """
    Enterprise-grade image content classification system.
    
    Features:
    - Visual content recognition and categorization
    - Style and aesthetic analysis
    - Color palette and composition analysis
    - Face and object detection
    - Quality assessment and technical metrics
    - Similarity matching for copyright detection
    - Album cover and artwork classification
    - Brand and logo detection
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
Initialize image classifier with ML models."""
        self.settings = get_settings()
        self.ml_engine = MLEngine()
        self.image_processor = ImageProcessor()
        
        # Load pre-trained models
        self._load_models(model_path)
        
        # Initialize feature extractors
        self._init_feature_extractors()
        
        # Classification thresholds
        self.thresholds = {
            'similarity': 0.85,
            'quality_score': 0.70,
            'face_confidence': 0.80,
            'object_confidence': 0.75,
            'style_confidence': 0.60
        }

    def _load_models(self, model_path: Optional[str]):
        """
Load and initialize ML models."""
        try:
            # CLIP model for general image understanding
            self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            
            # BLIP model for image captioning
            self.blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            self.blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
            
            # Load custom models if available
            if model_path:
                self._load_custom_models(model_path)
                
            logger.info("Image classification models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise ClassificationError(f"Failed to load models: {e}")

    def _load_custom_models(self, model_path: str):
        """Load custom trained models."""
        try:
            model_dir = Path(model_path)
            
            # Load style classifier
            style_model_path = model_dir / "style_classifier.joblib"
            if style_model_path.exists():
                self.style_classifier = joblib.load(style_model_path)
            
            # Load genre classifier for music-related images
            genre_model_path = model_dir / "music_genre_classifier.joblib"
            if genre_model_path.exists():
                self.genre_classifier = joblib.load(genre_model_path)
                
        except Exception as e:
            logger.warning(f"Could not load custom models: {e}")

    def _init_feature_extractors(self):
        """Initialize feature extraction components."""
        # Hash functions for similarity matching
        self.hash_functions = {
            'phash': imagehash.phash,
            'dhash': imagehash.dhash,
            'whash': imagehash.whash,
            'average_hash': imagehash.average_hash
        }
        
        # Color analysis parameters
        self.color_clusters = 8
        
        # Style categories
        self.style_categories = [
            'photography', 'digital_art', 'painting', 'sketch', 'cartoon',
            'abstract', 'minimalist', 'vintage', 'modern', 'album_cover',
            'poster', 'logo', 'illustration', 'graffiti', 'collage'
        ]

    @cache_result(ttl=3600)
    @track_performance
    def classify_image(self, image_path: str, options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Comprehensive image classification and analysis.
        
        Args:
            image_path: Path to image file
            options: Classification options and parameters
            
        Returns:
            Classification results with confidence scores
        """
        try:
            # Load and preprocess image
            image = self._load_image(image_path)
            if image is None:
                raise ClassificationError("Could not load image")
            
            results = {
                'image_path': image_path,
                'timestamp': self._get_timestamp(),
                'image_info': self._get_image_info(image),
                'classifications': {},
                'features': {},
                'quality_metrics': {},
                'similarity_hashes': {}
            }
            
            # Basic image analysis
            results['classifications'].update(self._classify_content_type(image))
            results['classifications'].update(self._classify_style(image))
            results['classifications'].update(self._detect_objects(image))
            results['classifications'].update(self._detect_faces(image))
            
            # Technical analysis
            results['quality_metrics'].update(self._assess_quality(image))
            results['features'].update(self._extract_color_features(image))
            results['features'].update(self._extract_composition_features(image))
            
            # Generate similarity hashes
            results['similarity_hashes'].update(self._generate_hashes(image))
            
            # Advanced analysis (optional)
            if options and options.get('detailed_analysis'):
                results['advanced'] = self._advanced_analysis(image)
            
            return results
            
        except Exception as e:
            logger.error(f"Error classifying image {image_path}: {e}")
            raise ClassificationError(f"Classification failed: {e}")

    def _load_image(self, image_path: str) -> Optional[np.ndarray]:
        """Load and validate image file."""
        try:
            # Load with PIL first
            pil_image = Image.open(image_path)
            
            # Convert to RGB if needed
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Convert to numpy array
            image = np.array(pil_image)
            
            # Validate dimensions
            if len(image.shape) != 3 or image.shape[2] != 3:
                raise ValueError("Invalid image format")
            
            return image
            
        except Exception as e:
            logger.error(f"Error loading image {image_path}: {e}")
            return None

    def _get_image_info(self, image: np.ndarray) -> Dict[str, Any]:
        """Extract basic image information."""
        return {
            'dimensions': {
                'width': image.shape[1],
                'height': image.shape[0],
                'channels': image.shape[2]
            },
            'aspect_ratio': round(image.shape[1] / image.shape[0], 2),
            'pixel_count': image.shape[0] * image.shape[1],
            'file_size_estimate': image.nbytes
        }

    def _classify_content_type(self, image: np.ndarray) -> Dict[str, Any]:
        """
Classify the type of content in the image."""
        try:
            # Convert to PIL for CLIP processing
            pil_image = Image.fromarray(image)
            
            # Define content type labels
            content_labels = [
                "album cover", "music poster", "concert photo", "musician portrait",
                "artwork", "digital art", "photography", "illustration", "logo",
                "social media post", "thumbnail", "promotional material",
                "landscape", "portrait", "abstract art", "text document"
            ]
            
            # Process with CLIP
            inputs = self.clip_processor(
                text=content_labels,
                images=pil_image,
                return_tensors="pt",
                padding=True
            )
            
            with torch.no_grad():
                outputs = self.clip_model(**inputs)
                logits_per_image = outputs.logits_per_image
                probs = logits_per_image.softmax(dim=1)
            
            # Get top predictions
            top_probs, top_indices = torch.topk(probs, k=3)
            
            predictions = []
            for i, (prob, idx) in enumerate(zip(top_probs[0], top_indices[0])):
                predictions.append({
                    'label': content_labels[idx],
                    'confidence': float(prob),
                    'rank': i + 1
                })
            
            return {
                'content_type': {
                    'primary': predictions[0]['label'],
                    'confidence': predictions[0]['confidence'],
                    'alternatives': predictions[1:],
                    'is_music_related': self._is_music_related(predictions[0]['label'])
                }
            }
            
        except Exception as e:
            logger.error(f"Error in content type classification: {e}")
            return {'content_type': {'primary': 'unknown', 'confidence': 0.0}}

    def _classify_style(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze artistic style and aesthetic properties."""
        try:
            # Convert to PIL for processing
            pil_image = Image.fromarray(image)
            
            # Style classification with CLIP
            style_labels = [
                "photographic", "digital art", "painting", "sketch", "cartoon",
                "minimalist", "vintage", "modern", "abstract", "realistic",
                "artistic", "professional", "amateur", "filtered", "retro"
            ]
            
            inputs = self.clip_processor(
                text=style_labels,
                images=pil_image,
                return_tensors="pt",
                padding=True
            )
            
            with torch.no_grad():
                outputs = self.clip_model(**inputs)
                logits_per_image = outputs.logits_per_image
                probs = logits_per_image.softmax(dim=1)
            
            # Get top style predictions
            top_probs, top_indices = torch.topk(probs, k=3)
            
            style_predictions = []
            for prob, idx in zip(top_probs[0], top_indices[0]):
                style_predictions.append({
                    'style': style_labels[idx],
                    'confidence': float(prob)
                })
            
            return {
                'style_analysis': {
                    'primary_style': style_predictions[0]['style'],
                    'confidence': style_predictions[0]['confidence'],
                    'style_variations': style_predictions[1:],
                    'aesthetic_score': self._calculate_aesthetic_score(image)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in style classification: {e}")
            return {'style_analysis': {'primary_style': 'unknown', 'confidence': 0.0}}

    def _detect_objects(self, image: np.ndarray) -> Dict[str, Any]:
        """Detect and classify objects in the image."""
        try:
            # Convert to PIL for CLIP processing
            pil_image = Image.fromarray(image)
            
            # Object detection labels
            object_labels = [
                "person", "musical instrument", "microphone", "guitar", "piano",
                "drums", "stage", "concert", "audience", "performer", "singer",
                "band", "studio", "recording equipment", "headphones", "speaker",
                "logo", "text", "album", "vinyl record", "cd", "digital device"
            ]
            
            inputs = self.clip_processor(
                text=object_labels,
                images=pil_image,
                return_tensors="pt",
                padding=True
            )
            
            with torch.no_grad():
                outputs = self.clip_model(**inputs)
                logits_per_image = outputs.logits_per_image
                probs = logits_per_image.softmax(dim=1)
            
            # Filter objects above threshold
            detected_objects = []
            for i, (label, prob) in enumerate(zip(object_labels, probs[0])):
                if float(prob) > self.thresholds['object_confidence']:
                    detected_objects.append({
                        'object': label,
                        'confidence': float(prob)
                    })
            
            # Sort by confidence
            detected_objects.sort(key=lambda x: x['confidence'], reverse=True)
            
            return {
                'object_detection': {
                    'objects_found': len(detected_objects),
                    'objects': detected_objects[:10],  # Top 10
                    'has_people': any(obj['object'] in ['person', 'singer', 'performer'] 
                                    for obj in detected_objects),
                    'has_instruments': any('instrument' in obj['object'] or 
                                         obj['object'] in ['guitar', 'piano', 'drums'] 
                                         for obj in detected_objects)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in object detection: {e}")
            return {'object_detection': {'objects_found': 0, 'objects': []}}

    def _detect_faces(self, image: np.ndarray) -> Dict[str, Any]:
        """Detect and analyze faces in the image."""
        try:
            # Convert BGR to RGB for face_recognition
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Find face locations
            face_locations = face_recognition.face_locations(rgb_image)
            
            if not face_locations:
                return {
                    'face_analysis': {
                        'faces_detected': 0,
                        'faces': [],
                        'has_faces': False
                    }
                }
            
            # Extract face encodings
            face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
            
            faces_data = []
            for i, (location, encoding) in enumerate(zip(face_locations, face_encodings)):
                top, right, bottom, left = location
                
                face_data = {
                    'face_id': i,
                    'location': {
                        'top': top,
                        'right': right, 
                        'bottom': bottom,
                        'left': left
                    },
                    'size': {
                        'width': right - left,
                        'height': bottom - top
                    },
                    'encoding_hash': hashlib.md5(encoding.tobytes()).hexdigest()
                }
                faces_data.append(face_data)
            
            return {
                'face_analysis': {
                    'faces_detected': len(faces_data),
                    'faces': faces_data,
                    'has_faces': True,
                    'dominant_face': faces_data[0] if faces_data else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error in face detection: {e}")
            return {'face_analysis': {'faces_detected': 0, 'faces': [], 'has_faces': False}}

    def _assess_quality(self, image: np.ndarray) -> Dict[str, Any]:
        """Assess technical quality of the image."""
        try:
            # Convert to PIL for analysis
            pil_image = Image.fromarray(image)
            
            # Basic quality metrics
            quality_metrics = {
                'resolution_score': self._calculate_resolution_score(image),
                'sharpness_score': self._calculate_sharpness(pil_image),
                'brightness_score': self._calculate_brightness(pil_image),
                'contrast_score': self._calculate_contrast(pil_image),
                'saturation_score': self._calculate_saturation(pil_image),
                'noise_level': self._estimate_noise_level(image)
            }
            
            # Overall quality score
            weights = {
                'resolution_score': 0.2,
                'sharpness_score': 0.25,
                'brightness_score': 0.15,
                'contrast_score': 0.15,
                'saturation_score': 0.15,
                'noise_level': 0.1  # Lower is better for noise
            }
            
            overall_score = sum(
                quality_metrics[metric] * weight 
                for metric, weight in weights.items()
                if metric != 'noise_level'
            ) + (1 - quality_metrics['noise_level']) * weights['noise_level']
            
            quality_metrics['overall_quality'] = max(0, min(1, overall_score))
            quality_metrics['quality_grade'] = self._get_quality_grade(overall_score)
            
            return quality_metrics
            
        except Exception as e:
            logger.error(f"Error in quality assessment: {e}")
            return {'overall_quality': 0.0, 'quality_grade': 'unknown'}

    def _extract_color_features(self, image: np.ndarray) -> Dict[str, Any]:
        """Extract color-based features and palette."""
        try:
            # Convert to PIL for easier processing
            pil_image = Image.fromarray(image)
            
            # Resize for faster processing
            small_image = pil_image.resize((100, 100))
            image_array = np.array(small_image)
            
            # Reshape for clustering
            pixels = image_array.reshape(-1, 3)
            
            # Extract dominant colors using K-means
            kmeans = KMeans(n_clusters=self.color_clusters, random_state=42, n_init=10)
            kmeans.fit(pixels)
            
            # Get dominant colors and their percentages
            colors = kmeans.cluster_centers_.astype(int)
            labels = kmeans.labels_
            
            color_percentages = []
            for i in range(self.color_clusters):
                percentage = np.sum(labels == i) / len(labels)
                if percentage > 0.01:  # Only include colors > 1%
                    color_percentages.append({
                        'rgb': colors[i].tolist(),
                        'hex': '#{:02x}{:02x}{:02x}'.format(*colors[i]),
                        'percentage': float(percentage),
                        'hsl': self._rgb_to_hsl(*colors[i])
                    })
            
            # Sort by percentage
            color_percentages.sort(key=lambda x: x['percentage'], reverse=True)
            
            # Calculate color harmony and temperature
            color_harmony = self._calculate_color_harmony(colors)
            color_temperature = self._calculate_color_temperature(colors)
            
            return {
                'color_analysis': {
                    'dominant_colors': color_percentages[:5],  # Top 5 colors
                    'color_count': len(color_percentages),
                    'color_harmony_score': color_harmony,
                    'color_temperature': color_temperature,
                    'is_monochromatic': len(color_percentages) <= 3,
                    'primary_color': color_percentages[0] if color_percentages else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error in color feature extraction: {e}")
            return {'color_analysis': {'dominant_colors': [], 'color_count': 0}}

    def _extract_composition_features(self, image: np.ndarray) -> Dict[str, Any]:
        """Extract composition and layout features."""
        try:
            height, width = image.shape[:2]
            
            # Calculate rule of thirds intersection points
            third_h = height // 3
            third_w = width // 3
            
            # Convert to grayscale for edge detection
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Edge detection
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (height * width)
            
            # Calculate symmetry
            left_half = gray[:, :width//2]
            right_half = cv2.flip(gray[:, width//2:], 1)
            
            # Resize to match if odd width
            min_width = min(left_half.shape[1], right_half.shape[1])
            left_half = left_half[:, :min_width]
            right_half = right_half[:, :min_width]
            
            horizontal_symmetry = np.corrcoef(left_half.flatten(), right_half.flatten())[0, 1]
            horizontal_symmetry = max(0, horizontal_symmetry) if not np.isnan(horizontal_symmetry) else 0
            
            # Vertical symmetry
            top_half = gray[:height//2, :]
            bottom_half = cv2.flip(gray[height//2:, :], 0)
            
            min_height = min(top_half.shape[0], bottom_half.shape[0])
            top_half = top_half[:min_height, :]
            bottom_half = bottom_half[:min_height, :]
            
            vertical_symmetry = np.corrcoef(top_half.flatten(), bottom_half.flatten())[0, 1]
            vertical_symmetry = max(0, vertical_symmetry) if not np.isnan(vertical_symmetry) else 0
            
            return {
                'composition_analysis': {
                    'aspect_ratio': round(width / height, 2),
                    'edge_density': float(edge_density),
                    'horizontal_symmetry': float(horizontal_symmetry),
                    'vertical_symmetry': float(vertical_symmetry),
                    'rule_of_thirds_points': [
                        {'x': third_w, 'y': third_h},
                        {'x': 2 * third_w, 'y': third_h},
                        {'x': third_w, 'y': 2 * third_h},
                        {'x': 2 * third_w, 'y': 2 * third_h}
                    ],
                    'complexity_score': float(edge_density * 2 + (1 - max(horizontal_symmetry, vertical_symmetry)))
                }
            }
            
        except Exception as e:
            logger.error(f"Error in composition analysis: {e}")
            return {'composition_analysis': {'aspect_ratio': 1.0, 'complexity_score': 0.5}}

    def _generate_hashes(self, image: np.ndarray) -> Dict[str, str]:
        """Generate multiple hash signatures for similarity matching."""
        try:
            # Convert to PIL
            pil_image = Image.fromarray(image)
            
            hashes = {}
            for hash_name, hash_func in self.hash_functions.items():
                try:
                    hash_value = hash_func(pil_image)
                    hashes[hash_name] = str(hash_value)
                except Exception as e:
                    logger.warning(f"Error generating {hash_name}: {e}")
                    hashes[hash_name] = None
            
            # Additional custom hash based on color histogram
            hist = cv2.calcHist([image], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
            hist_hash = hashlib.md5(hist.tobytes()).hexdigest()
            hashes['color_histogram_hash'] = hist_hash
            
            return hashes
            
        except Exception as e:
            logger.error(f"Error generating hashes: {e}")
            return {}

    def _advanced_analysis(self, image: np.ndarray) -> Dict[str, Any]:
        """Perform advanced analysis including captioning and scene understanding."""
        try:
            # Convert to PIL for model processing
            pil_image = Image.fromarray(image)
            
            # Generate image caption with BLIP
            inputs = self.blip_processor(pil_image, return_tensors="pt")
            
            with torch.no_grad():
                out = self.blip_model.generate(**inputs, max_length=50)
                caption = self.blip_processor.decode(out[0], skip_special_tokens=True)
            
            # Scene analysis with CLIP
            scene_labels = [
                "indoor scene", "outdoor scene", "studio setting", "concert venue",
                "home environment", "professional setting", "stage performance",
                "recording studio", "natural landscape", "urban environment"
            ]
            
            scene_inputs = self.clip_processor(
                text=scene_labels,
                images=pil_image,
                return_tensors="pt",
                padding=True
            )
            
            with torch.no_grad():
                scene_outputs = self.clip_model(**scene_inputs)
                scene_probs = scene_outputs.logits_per_image.softmax(dim=1)
            
            # Get top scene predictions
            top_scene_probs, top_scene_indices = torch.topk(scene_probs, k=3)
            
            scene_predictions = []
            for prob, idx in zip(top_scene_probs[0], top_scene_indices[0]):
                scene_predictions.append({
                    'scene': scene_labels[idx],
                    'confidence': float(prob)
                })
            
            return {
                'image_caption': caption,
                'scene_analysis': {
                    'primary_scene': scene_predictions[0]['scene'],
                    'confidence': scene_predictions[0]['confidence'],
                    'alternative_scenes': scene_predictions[1:]
                },
                'semantic_features': self._extract_semantic_features(caption)
            }
            
        except Exception as e:
            logger.error(f"Error in advanced analysis: {e}")
            return {'image_caption': 'Analysis failed', 'scene_analysis': {}}

    # Helper methods
    def _is_music_related(self, content_type: str) -> bool:
        """Check if content type is music-related."""
        music_keywords = ['album', 'music', 'concert', 'musician', 'artist', 'song', 'band']
        return any(keyword in content_type.lower() for keyword in music_keywords)

    def _calculate_aesthetic_score(self, image: np.ndarray) -> float:
        """
Calculate aesthetic appeal score based on composition rules."""
        try:
            # Rule of thirds
            height, width = image.shape[:2]
            
            # Calculate image variance (complexity)
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            variance = np.var(gray)
            
            # Normalize variance score
            variance_score = min(1.0, variance / 10000)
            
            # Color distribution score
            colors = cv2.calcHist([image], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
            color_distribution = np.std(colors)
            color_score = min(1.0, color_distribution / 1000)
            
            # Combine scores
            aesthetic_score = (variance_score * 0.4 + color_score * 0.6)
            return float(aesthetic_score)
            
        except Exception:
            return 0.5

    def _calculate_resolution_score(self, image: np.ndarray) -> float:
        """
Calculate resolution quality score."""
        height, width = image.shape[:2]
        total_pixels = height * width
        
        # Score based on common resolution standards
        if total_pixels >= 8000000:  # 4K+
            return 1.0
        elif total_pixels >= 2000000:  # HD+
            return 0.8
        elif total_pixels >= 1000000:  # Good
            return 0.6
        elif total_pixels >= 500000:   # Acceptable
            return 0.4
        else:
            return 0.2

    def _calculate_sharpness(self, pil_image: Image.Image) -> float:
        """
Calculate image sharpness using variance of Laplacian."""
        try:
            # Convert to grayscale
            gray = pil_image.convert('L')
            image_array = np.array(gray)
            
            # Apply Laplacian filter
            laplacian_var = cv2.Laplacian(image_array, cv2.CV_64F).var()
            
            # Normalize to 0-1 range
            return min(1.0, laplacian_var / 1000)
            
        except Exception:
            return 0.5

    def _calculate_brightness(self, pil_image: Image.Image) -> float:
        """
Calculate optimal brightness score."""
        try:
            stat = ImageStat.Stat(pil_image)
            mean_brightness = sum(stat.mean) / len(stat.mean)
            
            # Optimal brightness is around 128 (middle of 0-255 range)
            optimal = 128
            deviation = abs(mean_brightness - optimal) / optimal
            
            return max(0, 1 - deviation)
            
        except Exception:
            return 0.5

    def _calculate_contrast(self, pil_image: Image.Image) -> float:
        """
Calculate image contrast score."""
        try:
            stat = ImageStat.Stat(pil_image)
            contrast = sum(stat.stddev) / len(stat.stddev)
            
            # Normalize contrast (good contrast is around 50-80)
            return min(1.0, contrast / 80)
            
        except Exception:
            return 0.5

    def _calculate_saturation(self, pil_image: Image.Image) -> float:
        """
Calculate color saturation score."""
        try:
            # Convert to HSV to get saturation
            hsv_image = pil_image.convert('HSV')
            stat = ImageStat.Stat(hsv_image)
            
            # Saturation is the second channel in HSV
            saturation = stat.mean[1] if len(stat.mean) > 1 else 128
            
            # Normalize to 0-1 range
            return saturation / 255
            
        except Exception:
            return 0.5

    def _estimate_noise_level(self, image: np.ndarray) -> float:
        """
Estimate noise level in the image."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Apply Gaussian blur and subtract from original
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            noise = cv2.absdiff(gray.astype(np.float32), blurred.astype(np.float32))
            
            # Calculate noise level
            noise_level = np.mean(noise) / 255
            
            return min(1.0, noise_level)
            
        except Exception:
            return 0.1

    def _get_quality_grade(self, score: float) -> str:
        """
Convert quality score to letter grade."""
        if score >= 0.9:
            return 'A+'
        elif score >= 0.8:
            return 'A'
        elif score >= 0.7:
            return 'B+'
        elif score >= 0.6:
            return 'B'
        elif score >= 0.5:
            return 'C+'
        elif score >= 0.4:
            return 'C'
        else:
            return 'D'

    def _rgb_to_hsl(self, r: int, g: int, b: int) -> Tuple[int, int, int]:
        """
Convert RGB to HSL color space."""
        r, g, b = r/255.0, g/255.0, b/255.0
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        return (int(h*360), int(s*100), int(l*100))

    def _calculate_color_harmony(self, colors: np.ndarray) -> float:
        """
Calculate color harmony score based on color theory."""
        try:
            if len(colors) < 2:
                return 0.5
            
            # Convert to HSL for better harmony analysis
            hsl_colors = []
            for color in colors:
                h, s, l = self._rgb_to_hsl(*color)
                hsl_colors.append((h, s, l))
            
            # Calculate hue differences
            hues = [color[0] for color in hsl_colors]
            hue_differences = []
            
            for i in range(len(hues)):
                for j in range(i+1, len(hues)):
                    diff = abs(hues[i] - hues[j])
                    diff = min(diff, 360 - diff)  # Consider circular nature
                    hue_differences.append(diff)
            
            if not hue_differences:
                return 0.5
            
            # Harmony is better when hues are related (complementary, triadic, etc.)
            avg_difference = np.mean(hue_differences)
            
            # Good harmony occurs at specific intervals
            harmony_intervals = [60, 90, 120, 180]  # Triadic, square, complementary
            harmony_score = 0
            
            for interval in harmony_intervals:
                if abs(avg_difference - interval) < 15:
                    harmony_score = max(harmony_score, 1 - abs(avg_difference - interval) / 15)
            
            return float(harmony_score)
            
        except Exception:
            return 0.5

    def _calculate_color_temperature(self, colors: np.ndarray) -> str:
        """
Determine overall color temperature."""
        try:
            # Calculate average color
            avg_color = np.mean(colors, axis=0)
            r, g, b = avg_color
            
            # Simple color temperature classification
            if b > r and b > g:
                return 'cool'
            elif r > b and r > g:
                return 'warm'
            else:
                return 'neutral'
                
        except Exception:
            return 'neutral'

    def _extract_semantic_features(self, caption: str) -> Dict[str, Any]:
        """
Extract semantic features from image caption."""
        try:
            # Simple keyword extraction
            music_keywords = ['music', 'song', 'guitar', 'piano', 'drum', 'singer', 'band', 'concert']
            art_keywords = ['art', 'painting', 'drawing', 'design', 'creative', 'artistic']
            tech_keywords = ['studio', 'microphone', 'equipment', 'recording', 'professional']
            
            caption_lower = caption.lower()
            
            return {
                'contains_music_terms': any(keyword in caption_lower for keyword in music_keywords),
                'contains_art_terms': any(keyword in caption_lower for keyword in art_keywords),
                'contains_tech_terms': any(keyword in caption_lower for keyword in tech_keywords),
                'word_count': len(caption.split()),
                'complexity_score': len(set(caption.lower().split())) / len(caption.split()) if caption.split() else 0
            }
            
        except Exception:
            return {'contains_music_terms': False, 'word_count': 0}

    def _get_timestamp(self) -> str:
        """
Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()

    def compare_images(self, image1_path: str, image2_path: str) -> Dict[str, Any]:
        """
        Compare two images for similarity.
        
        Args:
            image1_path: Path to first image
            image2_path: Path to second image
            
        Returns:
            Similarity analysis results
        """
        try:
            # Load images
            image1 = self._load_image(image1_path)
            image2 = self._load_image(image2_path)
            
            if image1 is None or image2 is None:
                raise ClassificationError("Could not load one or both images")
            
            # Generate hashes for both images
            hashes1 = self._generate_hashes(image1)
            hashes2 = self._generate_hashes(image2)
            
            # Calculate hash similarities
            hash_similarities = {}
            for hash_type in self.hash_functions.keys():
                if hashes1.get(hash_type) and hashes2.get(hash_type):
                    hash1 = imagehash.hex_to_hash(hashes1[hash_type])
                    hash2 = imagehash.hex_to_hash(hashes2[hash_type])
                    similarity = 1 - (hash1 - hash2) / len(hash1.hash) ** 2
                    hash_similarities[hash_type] = float(similarity)
            
            # Calculate overall similarity
            overall_similarity = np.mean(list(hash_similarities.values())) if hash_similarities else 0.0
            
            # Feature-based comparison
            features1 = self._extract_color_features(image1)
            features2 = self._extract_color_features(image2)
            
            # Color similarity
            color_similarity = self._compare_color_features(features1, features2)
            
            return {
                'overall_similarity': float(overall_similarity),
                'hash_similarities': hash_similarities,
                'color_similarity': color_similarity,
                'is_likely_match': overall_similarity > self.thresholds['similarity'],
                'confidence_level': 'high' if overall_similarity > 0.9 else 'medium' if overall_similarity > 0.7 else 'low'
            }
            
        except Exception as e:
            logger.error(f"Error comparing images: {e}")
            raise ClassificationError(f"Image comparison failed: {e}")

    def _compare_color_features(self, features1: Dict, features2: Dict) -> float:
        """Compare color features between two images."""
        try:
            colors1 = features1.get('color_analysis', {}).get('dominant_colors', [])
            colors2 = features2.get('color_analysis', {}).get('dominant_colors', [])
            
            if not colors1 or not colors2:
                return 0.0
            
            # Compare dominant colors
            similarities = []
            for color1 in colors1[:3]:  # Top 3 colors
                best_match = 0
                for color2 in colors2[:3]:
                    # Calculate RGB distance
                    rgb1 = np.array(color1['rgb'])
                    rgb2 = np.array(color2['rgb'])
                    distance = np.linalg.norm(rgb1 - rgb2)
                    similarity = max(0, 1 - distance / (255 * np.sqrt(3)))
                    best_match = max(best_match, similarity)
                similarities.append(best_match)
            
            return float(np.mean(similarities))
            
        except Exception:
            return 0.0

    def get_classification_summary(self, results: Dict[str, Any]) -> str:
        """
Generate a human-readable summary of classification results."""
        try:
            summary_parts = []
            
            # Content type
            content_type = results.get('classifications', {}).get('content_type', {})
            if content_type.get('primary'):
                summary_parts.append(f"Content: {content_type['primary']} ({content_type.get('confidence', 0):.2f})")
            
            # Style
            style = results.get('classifications', {}).get('style_analysis', {})
            if style.get('primary_style'):
                summary_parts.append(f"Style: {style['primary_style']} ({style.get('confidence', 0):.2f})")
            
            # Quality
            quality = results.get('quality_metrics', {})
            if quality.get('overall_quality'):
                grade = quality.get('quality_grade', 'Unknown')
                summary_parts.append(f"Quality: {grade} ({quality['overall_quality']:.2f})")
            
            # Objects
            objects = results.get('classifications', {}).get('object_detection', {})
            if objects.get('objects'):
                top_object = objects['objects'][0]['object']
                summary_parts.append(f"Main object: {top_object}")
            
            # Colors
            colors = results.get('features', {}).get('color_analysis', {})
            if colors.get('dominant_colors'):
                primary_color = colors['dominant_colors'][0]['hex']
                summary_parts.append(f"Primary color: {primary_color}")
            
            return " | ".join(summary_parts) if summary_parts else "No classification data available"
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return "Summary generation failed"
