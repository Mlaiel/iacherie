"""Image Recognition Engine - Advanced Computer Vision & Analysis
============================================================

Professional image recognition engine for visual content creators providing:
- Deep Learning Image Classification
- Object Detection & Segmentation
- Visual Feature Extraction & Analysis
- Image Quality Assessment & Enhancement
- Perceptual Hashing & Fingerprinting
- Style Transfer & Artistic Analysis
- OCR & Text Recognition
- Face Detection & Recognition
- Scene Understanding & Context Analysis
- Visual Similarity Matching

Created by: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use strictly prohibited
"""import cv2
import numpy as np
import torch
import torchvision.transforms as transforms
from typing import Dict, List, Any, Optional, Tuple, Union
import logging
from dataclasses import dataclass
from PIL import Image, ImageEnhance, ImageFilter
import imagehash
from sklearn.cluster import KMeans
from transformers import CLIPProcessor, CLIPModel, BlipProcessor, BlipForConditionalGeneration
import pytesseract
from scipy.spatial.distance import cosine, euclidean
import hashlib
from skimage import feature, measure, filters
import face_recognition

logger = logging.getLogger(__name__)

@dataclass
class ImageFeatures:
    """Comprehensive image feature representation"""    visual_features: Dict[str, np.ndarray]
    semantic_features: Dict[str, Any]
    quality_metrics: Dict[str, float]
    perceptual_hash: str
    fingerprint: np.ndarray
    metadata: Dict[str, Any]

@dataclass
class ObjectDetection:
    """Object detection results"""    class_name: str
    confidence: float
    bbox: Tuple[int, int, int, int]
    segmentation_mask: Optional[np.ndarray] = None

@dataclass
class FaceAnalysis:
    """Face analysis results"""    face_locations: List[Tuple[int, int, int, int]]
    face_encodings: List[np.ndarray]
    face_landmarks: List[Dict[str, List[Tuple[int, int]]]]
    emotions: List[Dict[str, float]]
    age_estimates: List[int]
    gender_predictions: List[str]
class ObjectDetection:
    """Object detection result"""    class_name: str
    confidence: float
    bbox: Tuple[int, int, int, int]
    mask: Optional[np.ndarray] = None

@dataclass
class FaceDetection:
    """Face detection result"""    bbox: Tuple[int, int, int, int]
    landmarks: np.ndarray
    encoding: np.ndarray
    confidence: float

class ImageRecognitionEngine:
    """    Industrial-grade image recognition engine for content creators
    """    
    def __init__(self, target_size: Tuple[int, int] = (512, 512)):
        self.target_size = target_size
        
        # Initialize AI models
        self._initialize_models()
        
        # Initialize OpenCV components
        self._initialize_opencv()
        
        # Initialize feature extractors
        self._initialize_feature_extractors()
        
        logger.info("ImageRecognitionEngine initialized successfully")
    
    def _initialize_models(self) -> None:
        """Initialize AI models for image analysis"""        try:
            # CLIP model for general image understanding
            self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")
            self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14")
            
            # BLIP model for image captioning
            self.blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            self.blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
            
            # Load object detection models
            self._load_detection_models()
            
            # Load classification models
            self._load_classification_models()
            
        except Exception as e:
            logger.error(f"Failed to initialize AI models: {e}")
            raise
    
    def _initialize_opencv(self) -> None:
        """Initialize OpenCV components"""        try:
            # Feature detectors
            self.sift_detector = cv2.SIFT_create()
            self.orb_detector = cv2.ORB_create()
            self.surf_detector = cv2.xfeatures2d.SURF_create() if hasattr(cv2, 'xfeatures2d') else None
            
            # Face detection
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
            
            # Edge detectors
            self.canny_low = 50
            self.canny_high = 150
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenCV: {e}")
            raise
    
    def _initialize_feature_extractors(self) -> None:
        """Initialize feature extraction components"""        try:
            # Color space converters
            self.color_spaces = ['RGB', 'HSV', 'LAB', 'YUV']
            
            # Texture analysis parameters
            self.lbp_radius = 3
            self.lbp_n_points = 24
            
            # Histogram parameters
            self.hist_bins = {
                'gray': 256,
                'color': 64
            }
            
        except Exception as e:
            logger.error(f"Failed to initialize feature extractors: {e}")
            raise
    
    def _load_detection_models(self) -> None:
        """Load pre-trained object detection models"""        try:
            # YOLOv5 for object detection
            self.yolo_model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
            self.yolo_model.eval()
            
        except Exception as e:
            logger.error(f"Failed to load detection models: {e}")
            raise
    
    def _load_classification_models(self) -> None:
        """Load pre-trained classification models"""        # Load style classification models, artistic style models, etc.
        pass
    
    def recognize(self, image_data: Union[str, np.ndarray, Image.Image], 
                  config: Dict[str, Any]) -> Dict[str, Any]:
        """        Comprehensive image recognition pipeline
        
        Args:
            image_data: Image file path, numpy array, or PIL Image
            config: Recognition configuration parameters
            
        Returns:
            Complete image analysis results
        """        try:
            # Load and preprocess image
            image = self._load_image(image_data)
            if image is None:
                raise ValueError("Could not load image")
            
            # Extract comprehensive features
            features = self._extract_image_features(image, config)
            
            # Perform object detection
            objects = self._detect_objects(image, config)
            
            # Perform face detection
            faces = self._detect_faces(image, config)
            
            # Generate image description
            description = self._generate_description(image, config)
            
            # Assess image quality
            quality_metrics = self._assess_image_quality(image)
            
            # Generate fingerprints
            fingerprints = self._generate_fingerprints(image)
            
            # Extract text (OCR)
            text_content = self._extract_text(image, config)
            
            # Analyze artistic style
            style_analysis = self._analyze_artistic_style(image, config)
            
            # Extract metadata
            metadata = self._extract_image_metadata(image, image_data)
            
            return {
                'features': features,
                'objects': objects,
                'faces': faces,
                'description': description,
                'quality_metrics': quality_metrics,
                'fingerprints': fingerprints,
                'text_content': text_content,
                'style_analysis': style_analysis,
                'metadata': metadata,
                'processing_config': config
            }
            
        except Exception as e:
            logger.error(f"Image recognition failed: {e}")
            raise
    
    def _load_image(self, image_data: Union[str, np.ndarray, Image.Image]) -> Optional[np.ndarray]:
        """Load image from various input formats"""        try:
            if isinstance(image_data, str):
                # Load from file path
                image = cv2.imread(image_data)
                if image is not None:
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            elif isinstance(image_data, np.ndarray):
                # Already a numpy array
                image = image_data.copy()
                if len(image.shape) == 3 and image.shape[2] == 3:
                    # Assume BGR and convert to RGB
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            elif isinstance(image_data, Image.Image):
                # PIL Image
                image = np.array(image_data.convert('RGB'))
            else:
                raise ValueError(f"Unsupported image data type: {type(image_data)}")
            
            return image
            
        except Exception as e:
            logger.error(f"Failed to load image: {e}")
            return None
    
    def _extract_image_features(self, image: np.ndarray, 
                               config: Dict[str, Any]) -> ImageFeatures:
        """Extract comprehensive image features"""        try:
            # Visual features
            visual_features = self._extract_visual_features(image)
            
            # Semantic features
            semantic_features = self._extract_semantic_features(image, config)
            
            # Quality metrics
            quality_metrics = self._assess_detailed_quality(image)
            
            # Perceptual hash
            pil_image = Image.fromarray(image)
            perceptual_hash = str(imagehash.phash(pil_image))
            
            # Fingerprint
            fingerprint = self._generate_feature_fingerprint(image)
            
            # Metadata
            metadata = {
                'shape': image.shape,
                'dtype': str(image.dtype),
                'size_bytes': image.nbytes
            }
            
            return ImageFeatures(
                visual_features=visual_features,
                semantic_features=semantic_features,
                quality_metrics=quality_metrics,
                perceptual_hash=perceptual_hash,
                fingerprint=fingerprint,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            raise
    
    def _extract_visual_features(self, image: np.ndarray) -> Dict[str, np.ndarray]:
        """Extract visual features from image"""        features = {}
        
        # Color features
        features.update(self._extract_color_features(image))
        
        # Texture features
        features.update(self._extract_texture_features(image))
        
        # Shape features
        features.update(self._extract_shape_features(image))
        
        # Edge features
        features.update(self._extract_edge_features(image))
        
        # SIFT features
        features.update(self._extract_sift_features(image))
        
        return features
    
    def _extract_color_features(self, image: np.ndarray) -> Dict[str, np.ndarray]:
        """Extract color-based features"""        features = {}
        
        # RGB histogram
        hist_r = cv2.calcHist([image], [0], None, [256], [0, 256])
        hist_g = cv2.calcHist([image], [1], None, [256], [0, 256])
        hist_b = cv2.calcHist([image], [2], None, [256], [0, 256])
        features['rgb_histogram'] = np.concatenate([hist_r.flatten(), hist_g.flatten(), hist_b.flatten()])
        
        # HSV histogram
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        hist_h = cv2.calcHist([hsv], [0], None, [180], [0, 180])
        hist_s = cv2.calcHist([hsv], [1], None, [256], [0, 256])
        hist_v = cv2.calcHist([hsv], [2], None, [256], [0, 256])
        features['hsv_histogram'] = np.concatenate([hist_h.flatten(), hist_s.flatten(), hist_v.flatten()])
        
        # Color moments
        features['color_moments'] = self._calculate_color_moments(image)
        
        # Dominant colors
        features['dominant_colors'] = self._extract_dominant_colors(image)
        
        return features
    
    def _extract_texture_features(self, image: np.ndarray) -> Dict[str, np.ndarray]:
        """Extract texture-based features"""        features = {}
        
        # Convert to grayscale for texture analysis
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Local Binary Pattern
        lbp = feature.local_binary_pattern(gray, self.lbp_n_points, self.lbp_radius, method='uniform')
        lbp_hist, _ = np.histogram(lbp.ravel(), bins=self.lbp_n_points + 2, range=(0, self.lbp_n_points + 2))
        features['lbp_histogram'] = lbp_hist.astype(float)
        
        # Gabor filter responses
        features['gabor_responses'] = self._extract_gabor_features(gray)
        
        # Haralick texture features
        features['haralick_features'] = self._extract_haralick_features(gray)
        
        # Wavelet features
        features['wavelet_features'] = self._extract_wavelet_features(gray)
        
        return features
    
    def _extract_shape_features(self, image: np.ndarray) -> Dict[str, np.ndarray]:
        """Extract shape-based features"""        features = {}
        
        # Convert to grayscale and binary
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Get largest contour
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Contour features
            area = cv2.contourArea(largest_contour)
            perimeter = cv2.arcLength(largest_contour, True)
            
            # Shape descriptors
            features['contour_area'] = np.array([area])
            features['contour_perimeter'] = np.array([perimeter])
            features['aspect_ratio'] = np.array([self._calculate_aspect_ratio(largest_contour)])
            features['extent'] = np.array([self._calculate_extent(largest_contour, image.shape)])
            features['solidity'] = np.array([self._calculate_solidity(largest_contour)])
            
            # Hu moments
            moments = cv2.moments(largest_contour)
            hu_moments = cv2.HuMoments(moments)
            features['hu_moments'] = hu_moments.flatten()
        else:
            # Default values when no contours found
            features['contour_area'] = np.array([0])
            features['contour_perimeter'] = np.array([0])
            features['aspect_ratio'] = np.array([1])
            features['extent'] = np.array([0])
            features['solidity'] = np.array([0])
            features['hu_moments'] = np.zeros(7)
        
        return features
    
    def _extract_edge_features(self, image: np.ndarray) -> Dict[str, np.ndarray]:
        """Extract edge-based features"""        features = {}
        
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Canny edges
        edges = cv2.Canny(gray, self.canny_low, self.canny_high)
        
        # Edge density
        edge_density = np.sum(edges > 0) / edges.size
        features['edge_density'] = np.array([edge_density])
        
        # Edge direction histogram
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        gradient_direction = np.arctan2(grad_y, grad_x)
        
        # Histogram of gradient directions
        direction_hist, _ = np.histogram(gradient_direction, bins=36, range=(-np.pi, np.pi))
        features['edge_direction_histogram'] = direction_hist.astype(float)
        
        # Edge magnitude histogram
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        magnitude_hist, _ = np.histogram(gradient_magnitude, bins=256, range=(0, 255))
        features['edge_magnitude_histogram'] = magnitude_hist.astype(float)
        
        return features
    
    def _extract_sift_features(self, image: np.ndarray) -> Dict[str, np.ndarray]:
        """Extract SIFT features"""        features = {}
        
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # SIFT keypoints and descriptors
        keypoints, descriptors = self.sift_detector.detectAndCompute(gray, None)
        
        if descriptors is not None and len(descriptors) > 0:
            # Bag of visual words representation
            features['sift_bow'] = np.mean(descriptors, axis=0)
            features['sift_keypoint_count'] = np.array([len(keypoints)])
        else:
            features['sift_bow'] = np.zeros(128)
            features['sift_keypoint_count'] = np.array([0])
        
        return features
    
    def _calculate_color_moments(self, image: np.ndarray) -> np.ndarray:
        """Calculate color moments (mean, std, skewness)"""        moments = []
        
        for channel in range(image.shape[2]):
            channel_data = image[:, :, channel].flatten()
            
            # Mean
            mean = np.mean(channel_data)
            
            # Standard deviation
            std = np.std(channel_data)
            
            # Skewness
            skewness = np.mean(((channel_data - mean) / (std + 1e-10))**3)
            
            moments.extend([mean, std, skewness])
        
        return np.array(moments)
    
    def _extract_dominant_colors(self, image: np.ndarray, n_colors: int = 5) -> np.ndarray:
        """Extract dominant colors using K-means clustering"""        # Reshape image to list of pixels
        pixels = image.reshape(-1, 3)
        
        # Apply K-means
        kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
        kmeans.fit(pixels)
        
        # Get dominant colors
        dominant_colors = kmeans.cluster_centers_.astype(int)
        
        return dominant_colors.flatten()
    
    def _extract_gabor_features(self, gray_image: np.ndarray) -> np.ndarray:
        """Extract Gabor filter responses"""        features = []
        
        # Multiple orientations and frequencies
        orientations = [0, 45, 90, 135]
        frequencies = [0.1, 0.3, 0.5]
        
        for theta in orientations:
            for frequency in frequencies:
                # Apply Gabor filter
                real_response, _ = filters.gabor(gray_image, frequency=frequency, theta=np.deg2rad(theta))
                
                # Calculate statistics
                features.extend([
                    np.mean(real_response),
                    np.std(real_response),
                    np.mean(np.abs(real_response))
                ])
        
        return np.array(features)
    
    def _extract_haralick_features(self, gray_image: np.ndarray) -> np.ndarray:
        """Extract Haralick texture features"""        try:
            from skimage.feature import greycomatrix, greycoprops
            
            # Compute GLCM
            distances = [1, 2, 3]
            angles = [0, 45, 90, 135]
            
            glcm = greycomatrix(gray_image, distances=distances, angles=np.deg2rad(angles), 
                              levels=256, symmetric=True, normed=True)
            
            # Extract properties
            properties = ['contrast', 'dissimilarity', 'homogeneity', 'energy']
            features = []
            
            for prop in properties:
                prop_values = greycoprops(glcm, prop)
                features.extend(prop_values.flatten())
            
            return np.array(features)
            
        except ImportError:
            # Fallback if scikit-image is not available
            return np.zeros(48)  # 4 properties × 4 angles × 3 distances
    
    def _extract_wavelet_features(self, gray_image: np.ndarray) -> np.ndarray:
        """Extract wavelet transform features"""        try:
            import pywt
            
            # Multi-level wavelet decomposition
            coeffs = pywt.wavedec2(gray_image, 'db4', level=3)
            
            features = []
            for coeff in coeffs:
                if isinstance(coeff, tuple):
                    # Detail coefficients (horizontal, vertical, diagonal)
                    for detail in coeff:
                        features.extend([
                            np.mean(detail),
                            np.std(detail),
                            np.mean(np.abs(detail))
                        ])
                else:
                    # Approximation coefficients
                    features.extend([
                        np.mean(coeff),
                        np.std(coeff),
                        np.mean(np.abs(coeff))
                    ])
            
            return np.array(features)
            
        except ImportError:
            # Fallback if PyWavelets is not available
            return np.zeros(30)  # Estimated number of features
    
    def _calculate_aspect_ratio(self, contour: np.ndarray) -> float:
        """Calculate aspect ratio of contour bounding box"""        x, y, w, h = cv2.boundingRect(contour)
        return w / h if h > 0 else 1.0
    
    def _calculate_extent(self, contour: np.ndarray, image_shape: Tuple[int, ...]) -> float:
        """Calculate extent (contour area / bounding box area)"""        area = cv2.contourArea(contour)
        x, y, w, h = cv2.boundingRect(contour)
        bbox_area = w * h
        return area / bbox_area if bbox_area > 0 else 0.0
    
    def _calculate_solidity(self, contour: np.ndarray) -> float:
        """Calculate solidity (contour area / convex hull area)"""        area = cv2.contourArea(contour)
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        return area / hull_area if hull_area > 0 else 0.0
    
    def _extract_semantic_features(self, image: np.ndarray, 
                                  config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract semantic features using AI models"""        features = {}
        
        # CLIP embeddings
        if config.get('extract_clip_features', True):
            features['clip_embedding'] = self._extract_clip_embedding(image)
        
        # Scene classification
        if config.get('classify_scene', True):
            features['scene_classification'] = self._classify_scene(image)
        
        # Content categories
        if config.get('classify_content', True):
            features['content_classification'] = self._classify_content(image)
        
        return features
    
    def _extract_clip_embedding(self, image: np.ndarray) -> np.ndarray:
        """Extract CLIP embedding for image"""        try:
            pil_image = Image.fromarray(image)
            inputs = self.clip_processor(images=pil_image, return_tensors="pt")
            
            with torch.no_grad():
                image_features = self.clip_model.get_image_features(**inputs)
                embedding = image_features.squeeze().numpy()
            
            return embedding
            
        except Exception as e:
            logger.error(f"CLIP embedding extraction failed: {e}")
            return np.zeros(768)  # Default CLIP embedding size
    
    def _classify_scene(self, image: np.ndarray) -> Dict[str, float]:
        """Classify image scene using CLIP"""        try:
            pil_image = Image.fromarray(image)
            
            scene_categories = [
                "indoor scene", "outdoor scene", "nature landscape", "urban environment",
                "concert venue", "recording studio", "performance stage", "home setting",
                "office environment", "artistic studio", "street scene", "architecture"
            ]
            
            inputs = self.clip_processor(
                text=scene_categories, 
                images=pil_image, 
                return_tensors="pt", 
                padding=True
            )
            
            with torch.no_grad():
                outputs = self.clip_model(**inputs)
                logits_per_image = outputs.logits_per_image
                probs = logits_per_image.softmax(dim=1)
            
            return dict(zip(scene_categories, probs[0].numpy().tolist()))
            
        except Exception as e:
            logger.error(f"Scene classification failed: {e}")
            return {}
    
    def _classify_content(self, image: np.ndarray) -> Dict[str, float]:
        """Classify image content type"""        try:
            pil_image = Image.fromarray(image)
            
            content_categories = [
                "musical instrument", "person singing", "band performance", 
                "album cover", "concert photo", "music video frame",
                "artistic portrait", "landscape photo", "abstract art",
                "product photo", "social media content", "promotional material"
            ]
            
            inputs = self.clip_processor(
                text=content_categories, 
                images=pil_image, 
                return_tensors="pt", 
                padding=True
            )
            
            with torch.no_grad():
                outputs = self.clip_model(**inputs)
                logits_per_image = outputs.logits_per_image
                probs = logits_per_image.softmax(dim=1)
            
            return dict(zip(content_categories, probs[0].numpy().tolist()))
            
        except Exception as e:
            logger.error(f"Content classification failed: {e}")
            return {}
    
    def _detect_objects(self, image: np.ndarray, config: Dict[str, Any]) -> List[ObjectDetection]:
        """Detect objects in image using YOLO"""        try:
            # Run YOLO detection
            results = self.yolo_model(image)
            
            objects = []
            for *box, conf, cls in results.xyxy[0].cpu().numpy():
                if conf > config.get('detection_threshold', 0.5):
                    objects.append(ObjectDetection(
                        class_name=self.yolo_model.names[int(cls)],
                        confidence=float(conf),
                        bbox=tuple(int(x) for x in box)
                    ))
            
            return objects
            
        except Exception as e:
            logger.error(f"Object detection failed: {e}")
            return []
    
    def _detect_faces(self, image: np.ndarray, config: Dict[str, Any]) -> List[FaceDetection]:
        """Detect faces in image"""        try:
            faces = []
            
            # Use face_recognition library for better accuracy
            face_locations = face_recognition.face_locations(image)
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            for (top, right, bottom, left), encoding in zip(face_locations, face_encodings):
                faces.append(FaceDetection(
                    bbox=(left, top, right, bottom),
                    landmarks=np.array([]),  # Could add face landmarks here
                    encoding=encoding,
                    confidence=1.0  # face_recognition doesn't provide confidence
                ))
            
            return faces
            
        except Exception as e:
            logger.error(f"Face detection failed: {e}")
            return []
    
    def _generate_description(self, image: np.ndarray, config: Dict[str, Any]) -> str:
        """Generate natural language description of image"""        try:
            if not config.get('generate_description', True):
                return ""
            
            pil_image = Image.fromarray(image)
            inputs = self.blip_processor(images=pil_image, return_tensors="pt")
            
            with torch.no_grad():
                output_ids = self.blip_model.generate(**inputs, max_length=50)
                description = self.blip_processor.decode(output_ids[0], skip_special_tokens=True)
            
            return description
            
        except Exception as e:
            logger.error(f"Description generation failed: {e}")
            return ""
    
    def _assess_image_quality(self, image: np.ndarray) -> Dict[str, float]:
        """Assess overall image quality"""        quality_metrics = {}
        
        # Basic quality metrics
        quality_metrics.update(self._assess_detailed_quality(image))
        
        # Advanced quality metrics
        quality_metrics.update(self._assess_aesthetic_quality(image))
        
        # Technical quality metrics
        quality_metrics.update(self._assess_technical_quality(image))
        
        return quality_metrics
    
    def _assess_detailed_quality(self, image: np.ndarray) -> Dict[str, float]:
        """Assess detailed image quality metrics"""        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        metrics = {}
        
        # Sharpness (Laplacian variance)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        metrics['sharpness'] = min(laplacian_var / 1000.0, 1.0)
        
        # Contrast (standard deviation)
        metrics['contrast'] = min(np.std(gray) / 128.0, 1.0)
        
        # Brightness
        metrics['brightness'] = np.mean(gray) / 255.0
        
        # Noise estimation
        metrics['noise_level'] = self._estimate_noise_level(gray)
        
        # Dynamic range
        metrics['dynamic_range'] = (np.max(gray) - np.min(gray)) / 255.0
        
        return metrics
    
    def _assess_aesthetic_quality(self, image: np.ndarray) -> Dict[str, float]:
        """Assess aesthetic quality of image"""        metrics = {}
        
        # Rule of thirds
        metrics['rule_of_thirds'] = self._calculate_rule_of_thirds_score(image)
        
        # Color harmony
        metrics['color_harmony'] = self._calculate_color_harmony(image)
        
        # Composition balance
        metrics['composition_balance'] = self._calculate_composition_balance(image)
        
        return metrics
    
    def _assess_technical_quality(self, image: np.ndarray) -> Dict[str, float]:
        """Assess technical quality metrics"""        metrics = {}
        
        # Exposure assessment
        metrics['exposure_quality'] = self._assess_exposure(image)
        
        # Color saturation
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        metrics['saturation'] = np.mean(hsv[:, :, 1]) / 255.0
        
        # White balance assessment
        metrics['white_balance'] = self._assess_white_balance(image)
        
        return metrics
    
    def _estimate_noise_level(self, gray_image: np.ndarray) -> float:
        """Estimate noise level in image"""        # Use Laplacian to estimate noise
        laplacian = cv2.Laplacian(gray_image, cv2.CV_64F)
        noise_level = np.var(laplacian) / 10000.0  # Normalize
        return min(noise_level, 1.0)
    
    def _calculate_rule_of_thirds_score(self, image: np.ndarray) -> float:
        """Calculate how well image follows rule of thirds"""        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        height, width = gray.shape
        
        # Define thirds lines
        v_thirds = [width // 3, 2 * width // 3]
        h_thirds = [height // 3, 2 * height // 3]
        
        # Calculate gradient magnitude
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        
        # Score based on content along thirds lines
        score = 0
        for v_line in v_thirds:
            score += np.mean(gradient_magnitude[:, max(0, v_line-2):min(width, v_line+3)])
        for h_line in h_thirds:
            score += np.mean(gradient_magnitude[max(0, h_line-2):min(height, h_line+3), :])
        
        # Normalize score
        return min(score / (np.mean(gradient_magnitude) * 4 + 1e-10), 1.0)
    
    def _calculate_color_harmony(self, image: np.ndarray) -> float:
        """Calculate color harmony score"""        # Convert to HSV for color analysis
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        hue = hsv[:, :, 0]
        
        # Calculate hue distribution
        hue_hist, _ = np.histogram(hue, bins=36, range=(0, 180))
        hue_hist = hue_hist / np.sum(hue_hist)
        
        # Look for complementary and analogous color schemes
        # This is a simplified approach
        dominant_hues = np.argsort(hue_hist)[-3:]  # Top 3 hues
        
        # Check for color harmony patterns
        harmony_score = 0.5  # Base score
        
        # Add bonus for balanced color distribution
        if np.std(hue_hist) < 0.1:  # Monochromatic
            harmony_score += 0.2
        elif len(dominant_hues) >= 2:  # Multiple colors
            hue_differences = np.diff(np.sort(dominant_hues))
            if np.any(np.abs(hue_differences - 18) < 3):  # Complementary colors
                harmony_score += 0.3
        
        return min(harmony_score, 1.0)
    
    def _calculate_composition_balance(self, image: np.ndarray) -> float:
        """Calculate composition balance score"""        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        height, width = gray.shape
        
        # Divide image into quadrants
        mid_h, mid_w = height // 2, width // 2
        
        quadrants = [
            gray[:mid_h, :mid_w],      # Top-left
            gray[:mid_h, mid_w:],      # Top-right
            gray[mid_h:, :mid_w],      # Bottom-left
            gray[mid_h:, mid_w:]       # Bottom-right
        ]
        
        # Calculate visual weight of each quadrant
        weights = [np.mean(quad) for quad in quadrants]
        
        # Calculate balance (lower variance = better balance)
        balance_score = 1.0 - (np.std(weights) / 128.0)
        
        return max(0.0, min(balance_score, 1.0))
    
    def _assess_exposure(self, image: np.ndarray) -> float:
        """Assess exposure quality"""        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Calculate histogram
        hist, _ = np.histogram(gray, bins=256, range=(0, 256))
        hist = hist / np.sum(hist)
        
        # Check for clipping
        shadow_clipping = hist[0]  # Pure black
        highlight_clipping = hist[-1]  # Pure white
        
        # Penalize clipping
        clipping_penalty = (shadow_clipping + highlight_clipping) * 2
        
        # Check for good distribution
        distribution_score = 1.0 - np.std(hist)
        
        exposure_score = distribution_score - clipping_penalty
        
        return max(0.0, min(exposure_score, 1.0))
    
    def _assess_white_balance(self, image: np.ndarray) -> float:
        """Assess white balance quality"""        # Calculate average of each color channel
        avg_r = np.mean(image[:, :, 0])
        avg_g = np.mean(image[:, :, 1])
        avg_b = np.mean(image[:, :, 2])
        
        # Good white balance should have similar averages
        color_diff = max(abs(avg_r - avg_g), abs(avg_g - avg_b), abs(avg_r - avg_b))
        
        # Normalize and invert (lower difference = better white balance)
        white_balance_score = 1.0 - (color_diff / 255.0)
        
        return max(0.0, white_balance_score)
    
    def _generate_fingerprints(self, image: np.ndarray) -> Dict[str, str]:
        """Generate various image fingerprints"""        pil_image = Image.fromarray(image)
        
        fingerprints = {
            'phash': str(imagehash.phash(pil_image)),
            'dhash': str(imagehash.dhash(pil_image)),
            'whash': str(imagehash.whash(pil_image)),
            'average_hash': str(imagehash.average_hash(pil_image))
        }
        
        return fingerprints
    
    def _generate_feature_fingerprint(self, image: np.ndarray) -> np.ndarray:
        """Generate feature-based fingerprint"""        # Resize to standard size
        resized = cv2.resize(image, (64, 64))
        gray = cv2.cvtColor(resized, cv2.COLOR_RGB2GRAY)
        
        # Create DCT-based fingerprint
        dct = cv2.dct(gray.astype(np.float32))
        dct_low = dct[:8, :8]
        
        # Create binary fingerprint
        median = np.median(dct_low)
        fingerprint = (dct_low > median).astype(int)
        
        return fingerprint.flatten()
    
    def _extract_text(self, image: np.ndarray, config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract text from image using OCR"""        try:
            if not config.get('extract_text', True):
                return {'text': '', 'confidence': 0.0}
            
            # Use Tesseract OCR
            text = pytesseract.image_to_string(image)
            
            # Get confidence scores
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = np.mean(confidences) if confidences else 0.0
            
            return {
                'text': text.strip(),
                'confidence': avg_confidence / 100.0,
                'word_count': len(text.split()),
                'detected_words': [word for word in text.split() if word.strip()]
            }
            
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            return {'text': '', 'confidence': 0.0}
    
    def _analyze_artistic_style(self, image: np.ndarray, 
                               config: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze artistic style of image"""        if not config.get('analyze_style', True):
            return {}
        
        style_analysis = {
            'color_palette': self._analyze_color_palette(image),
            'composition_style': self._analyze_composition_style(image),
            'artistic_movement': self._classify_artistic_movement(image),
            'visual_complexity': self._calculate_visual_complexity(image)
        }
        
        return style_analysis
    
    def _analyze_color_palette(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze color palette characteristics"""        # Extract dominant colors
        dominant_colors = self._extract_dominant_colors(image, n_colors=8)
        
        # Analyze color temperature
        avg_color = np.mean(image.reshape(-1, 3), axis=0)
        color_temperature = 'warm' if avg_color[0] > avg_color[2] else 'cool'
        
        # Analyze saturation
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        avg_saturation = np.mean(hsv[:, :, 1]) / 255.0
        
        return {
            'dominant_colors': dominant_colors.tolist(),
            'color_temperature': color_temperature,
            'average_saturation': avg_saturation,
            'color_diversity': len(np.unique(dominant_colors.reshape(-1, 3), axis=0))
        }
    
    def _analyze_composition_style(self, image: np.ndarray) -> Dict[str, float]:
        """Analyze composition style characteristics"""        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Symmetry analysis
        symmetry_score = self._calculate_symmetry(gray)
        
        # Leading lines detection
        leading_lines_score = self._detect_leading_lines(gray)
        
        # Depth of field estimation
        depth_score = self._estimate_depth_of_field(gray)
        
        return {
            'symmetry': symmetry_score,
            'leading_lines': leading_lines_score,
            'depth_of_field': depth_score
        }
    
    def _classify_artistic_movement(self, image: np.ndarray) -> Dict[str, float]:
        """Classify artistic movement/style using CLIP"""        try:
            pil_image = Image.fromarray(image)
            
            artistic_styles = [
                "realistic photography", "abstract art", "impressionist style",
                "modern art", "vintage photography", "minimalist design",
                "street photography", "portrait photography", "landscape photography",
                "digital art", "artistic filter", "professional photography"
            ]
            
            inputs = self.clip_processor(
                text=artistic_styles, 
                images=pil_image, 
                return_tensors="pt", 
                padding=True
            )
            
            with torch.no_grad():
                outputs = self.clip_model(**inputs)
                logits_per_image = outputs.logits_per_image
                probs = logits_per_image.softmax(dim=1)
            
            return dict(zip(artistic_styles, probs[0].numpy().tolist()))
            
        except Exception as e:
            logger.error(f"Artistic movement classification failed: {e}")
            return {}
    
    def _calculate_visual_complexity(self, image: np.ndarray) -> float:
        """Calculate visual complexity score"""        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Edge density
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        # Texture complexity
        lbp = feature.local_binary_pattern(gray, 24, 3, method='uniform')
        texture_complexity = np.std(lbp) / 255.0
        
        # Color complexity
        unique_colors = len(np.unique(image.reshape(-1, 3), axis=0))
        color_complexity = min(unique_colors / 1000.0, 1.0)
        
        # Combined complexity
        complexity = (edge_density * 0.4 + texture_complexity * 0.3 + color_complexity * 0.3)
        
        return min(complexity, 1.0)
    
    def _calculate_symmetry(self, gray_image: np.ndarray) -> float:
        """Calculate symmetry score of image"""        height, width = gray_image.shape
        
        # Vertical symmetry
        left_half = gray_image[:, :width//2]
        right_half = np.fliplr(gray_image[:, width//2:])
        
        # Resize to same size if needed
        min_width = min(left_half.shape[1], right_half.shape[1])
        left_half = left_half[:, :min_width]
        right_half = right_half[:, :min_width]
        
        # Calculate similarity
        vertical_symmetry = 1.0 - np.mean(np.abs(left_half.astype(float) - right_half.astype(float))) / 255.0
        
        # Horizontal symmetry
        top_half = gray_image[:height//2, :]
        bottom_half = np.flipud(gray_image[height//2:, :])
        
        min_height = min(top_half.shape[0], bottom_half.shape[0])
        top_half = top_half[:min_height, :]
        bottom_half = bottom_half[:min_height, :]
        
        horizontal_symmetry = 1.0 - np.mean(np.abs(top_half.astype(float) - bottom_half.astype(float))) / 255.0
        
        return max(vertical_symmetry, horizontal_symmetry)
    
    def _detect_leading_lines(self, gray_image: np.ndarray) -> float:
        """Detect leading lines in image"""        edges = cv2.Canny(gray_image, 50, 150)
        
        # Use Hough line transform
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
        
        if lines is not None:
            # Count strong lines
            strong_lines = len(lines)
            leading_lines_score = min(strong_lines / 20.0, 1.0)  # Normalize
        else:
            leading_lines_score = 0.0
        
        return leading_lines_score
    
    def _estimate_depth_of_field(self, gray_image: np.ndarray) -> float:
        """Estimate depth of field effect"""        # Calculate local variance to detect focus areas
        kernel = np.ones((5, 5)) / 25
        mean_image = cv2.filter2D(gray_image.astype(np.float32), -1, kernel)
        variance_image = cv2.filter2D((gray_image.astype(np.float32) - mean_image)**2, -1, kernel)
        
        # High variance indicates sharp areas (in focus)
        # Low variance indicates blurred areas (out of focus)
        focus_map = variance_image > np.percentile(variance_image, 75)
        
        # Calculate depth of field score based on focus distribution
        focus_ratio = np.sum(focus_map) / focus_map.size
        
        # Good depth of field has focused subject and blurred background
        if 0.2 < focus_ratio < 0.8:
            depth_score = 1.0 - abs(focus_ratio - 0.5) * 2
        else:
            depth_score = 0.5  # Either everything in focus or everything blurred
        
        return depth_score
    
    def _extract_image_metadata(self, image: np.ndarray, 
                               image_data: Union[str, np.ndarray, Image.Image]) -> Dict[str, Any]:
        """Extract image metadata"""        metadata = {
            'dimensions': image.shape[:2],
            'channels': image.shape[2] if len(image.shape) > 2 else 1,
            'dtype': str(image.dtype),
            'size_bytes': image.nbytes,
            'aspect_ratio': image.shape[1] / image.shape[0] if image.shape[0] > 0 else 1.0
        }
        
        # Try to extract EXIF data if from file
        if isinstance(image_data, str):
            try:
                from PIL.ExifTags import TAGS
                pil_image = Image.open(image_data)
                exif_data = pil_image._getexif()
                
                if exif_data:
                    exif_dict = {}
                    for tag_id, value in exif_data.items():
                        tag = TAGS.get(tag_id, tag_id)
                        exif_dict[tag] = value
                    metadata['exif'] = exif_dict
                    
            except Exception as e:
                logger.warning(f"Could not extract EXIF data: {e}")
        
        return metadata
    
    def calculate_similarity(self, fingerprint1: Union[str, np.ndarray], 
                           fingerprint2: Union[str, np.ndarray], 
                           method: str = 'hamming') -> float:
        """Calculate similarity between two image fingerprints"""        try:
            if isinstance(fingerprint1, str) and isinstance(fingerprint2, str):
                # Hash-based similarity
                hash1 = imagehash.hex_to_hash(fingerprint1)
                hash2 = imagehash.hex_to_hash(fingerprint2)
                hamming_distance = hash1 - hash2
                similarity = 1.0 - (hamming_distance / len(hash1.hash.flatten()))
            else:
                # Feature-based similarity
                if method == 'cosine':
                    similarity = 1.0 - cosine(fingerprint1.flatten(), fingerprint2.flatten())
                elif method == 'euclidean':
                    max_distance = np.sqrt(len(fingerprint1.flatten()))
                    distance = euclidean(fingerprint1.flatten(), fingerprint2.flatten())
                    similarity = 1.0 - (distance / max_distance)
                else:  # hamming
                    hamming_distance = np.sum(fingerprint1.flatten() != fingerprint2.flatten()) / len(fingerprint1.flatten())
                    similarity = 1.0 - hamming_distance
            
            return float(max(0.0, min(1.0, similarity)))
            
        except Exception as e:
            logger.error(f"Image similarity calculation failed: {e}")
            return 0.0
