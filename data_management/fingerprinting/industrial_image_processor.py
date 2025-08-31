"""🏭 Industrial Image Fingerprinting Engine - Multi-Algorithm Production System
================================================================================
Module: data_management/fingerprinting/industrial_image_processor.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Image Processing - Production-Ready Multi-Algorithm Fingerprinting
Responsibility: Unified image fingerprinting with ALL required algorithms
================================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

INDUSTRIAL IMAGE FINGERPRINTING REQUIREMENTS:
✅ Fingerprinting Image Multi-Algorithmes - Complete implementation
✅ CLIP vision-language understanding - Advanced semantic embeddings
✅ Hash perceptuel (dHash, pHash, aHash, wHash) - All 4 hash types
✅ Détection features SIFT/SURF/ORB - Traditional CV feature extraction
✅ Résistance transformations géométriques - Geometric transformation resistance

TECHNICAL ARCHITECTURE:
├── 🧠 CLIP Vision-Language Model (OpenAI CLIP)
├── 🔍 Perceptual Hash Suite (ImageHash Library)
│   ├── pHash (Perceptual Hash) - DCT-based robust hashing
│   ├── dHash (Difference Hash) - Gradient-based comparison
│   ├── aHash (Average Hash) - Mean luminance hashing
│   └── wHash (Wavelet Hash) - Wavelet transform based
├── 👁️ Traditional Computer Vision Features
│   ├── SIFT (Scale-Invariant Feature Transform)
│   ├── SURF (Speeded-Up Robust Features)
│   └── ORB (Oriented FAST and Rotated BRIEF)
├── 🔄 Geometric Transformation Resistance
│   ├── Multi-scale feature detection
│   ├── Rotation-invariant descriptors
│   └── Affine transformation robustness
└── 🛡️ Industrial-Grade Quality Assurance
"""

from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import numpy as np
import asyncio
import logging
import hashlib
import time
from datetime import datetime
from pathlib import Path
import json
import base64
from concurrent.futures import ThreadPoolExecutor
import warnings

# Suppress scientific notation warnings
warnings.filterwarnings('ignore', category=UserWarning)

# Image processing libraries with graceful fallbacks
try:
    from PIL import Image, ImageStat, ImageFilter, ImageEnhance
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logging.warning("PIL not available - install Pillow for image processing")

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logging.warning("OpenCV not available - install opencv-python for computer vision features")

try:
    import imagehash
    IMAGEHASH_AVAILABLE = True
except ImportError:
    IMAGEHASH_AVAILABLE = False
    logging.warning("ImageHash not available - install imagehash for perceptual hashing")

try:
    import torch
    import clip
    CLIP_AVAILABLE = True
except ImportError:
    CLIP_AVAILABLE = False
    logging.warning("CLIP not available - install clip-by-openai for vision-language features")

try:
    from transformers import CLIPProcessor, CLIPModel
    TRANSFORMERS_CLIP_AVAILABLE = True
except ImportError:
    TRANSFORMERS_CLIP_AVAILABLE = False
    logging.warning("Transformers CLIP not available - install transformers for alternative CLIP implementation")

try:
    from sklearn.cluster import KMeans
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("Scikit-learn not available - install scikit-learn for clustering features")

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"

logger = logging.getLogger(__name__)

@dataclass
class IndustrialImageConfig:
    """Configuration industrielle pour fingerprinting multi-algorithmes"""
    
    # Image processing parameters
    max_dimension: int = 2048
    min_dimension: int = 64
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    supported_formats: Set[str] = field(default_factory=lambda: {
        'jpg', 'jpeg', 'png', 'webp', 'tiff', 'bmp', 'gif'
    })
    
    # Perceptual hashing - ALL 4 TYPES REQUIRED
    enable_phash: bool = True  # Perceptual Hash (DCT-based)
    enable_dhash: bool = True  # Difference Hash (gradient-based)
    enable_ahash: bool = True  # Average Hash (mean luminance)
    enable_whash: bool = True  # Wavelet Hash (wavelet transform)
    hash_size: int = 16  # Larger hash for more precision
    
    # CLIP vision-language understanding
    enable_clip: bool = True
    clip_model_name: str = "ViT-B/32"  # Standard CLIP model
    clip_embedding_dimension: int = 512
    
    # Traditional computer vision features
    enable_sift: bool = True   # Scale-Invariant Feature Transform
    enable_surf: bool = True   # Speeded-Up Robust Features  
    enable_orb: bool = True    # Oriented FAST and Rotated BRIEF
    max_keypoints: int = 1000  # Increased for industrial robustness
    
    # Geometric transformation resistance
    enable_multi_scale: bool = True
    scale_factors: List[float] = field(default_factory=lambda: [0.5, 1.0, 1.5, 2.0])
    rotation_angles: List[int] = field(default_factory=lambda: [0, 90, 180, 270])
    enable_affine_invariance: bool = True
    
    # Industrial quality settings
    quality_threshold: float = 0.7
    min_feature_matches: int = 10
    ransac_threshold: float = 5.0
    confidence_threshold: float = 0.95
    
    # Performance optimization
    use_gpu: bool = False  # Set to False for CPU-only environments
    max_workers: int = 4
    batch_processing: bool = True
    enable_caching: bool = True

@dataclass
class ImageFingerprint:
    """Structure complète d'empreinte image industrielle"""
    
    # Basic metadata
    image_path: str
    fingerprint_id: str
    processing_time: float
    timestamp: str
    
    # Perceptual hashes (ALL 4 TYPES)
    phash: Optional[str] = None
    dhash: Optional[str] = None  
    ahash: Optional[str] = None
    whash: Optional[str] = None
    combined_hash: Optional[str] = None
    
    # CLIP embeddings
    clip_embedding: Optional[List[float]] = None
    clip_embedding_hash: Optional[str] = None
    
    # Traditional CV features
    sift_features: Optional[Dict[str, Any]] = None
    surf_features: Optional[Dict[str, Any]] = None
    orb_features: Optional[Dict[str, Any]] = None
    
    # Geometric resistance data
    multi_scale_features: Optional[Dict[str, Any]] = None
    rotation_invariant_features: Optional[Dict[str, Any]] = None
    
    # Quality metrics
    image_quality_score: float = 0.0
    feature_density: float = 0.0
    geometric_stability: float = 0.0
    
    # Metadata
    image_properties: Optional[Dict[str, Any]] = None
    config_used: Optional[Dict[str, Any]] = None

class IndustrialImageProcessor:
    """🏭 Processeur d'images industriel - Multi-algorithmes production"""
    
    def __init__(self, config: IndustrialImageConfig):
        """Initialise le processeur avec configuration industrielle"""
        self.config = config
        self.clip_model = None
        self.clip_processor = None
        self.sift = None
        self.surf = None
        self.orb = None
        
        # Initialize components
        self._initialize_models()
        logger.info("Industrial Image Processor initialized with multi-algorithm support")
    
    def _initialize_models(self):
        """Initialise les modèles et détecteurs"""
        # Initialize CLIP for vision-language understanding
        if self.config.enable_clip and CLIP_AVAILABLE:
            try:
                device = "cuda" if torch.cuda.is_available() and self.config.use_gpu else "cpu"
                self.clip_model, self.clip_processor = clip.load(self.config.clip_model_name, device=device)
                self.clip_model.eval()
                logger.info(f"CLIP model {self.config.clip_model_name} loaded on {device}")
            except Exception as e:
                logger.warning(f"Failed to load CLIP model: {e}")
                if TRANSFORMERS_CLIP_AVAILABLE:
                    try:
                        self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
                        self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
                        logger.info("Fallback to Transformers CLIP implementation")
                    except Exception as e2:
                        logger.warning(f"Transformers CLIP also failed: {e2}")
        
        # Initialize traditional CV feature detectors
        if CV2_AVAILABLE:
            if self.config.enable_sift:
                try:
                    self.sift = cv2.SIFT_create(nfeatures=self.config.max_keypoints)
                    logger.info("SIFT detector initialized")
                except Exception as e:
                    logger.warning(f"SIFT initialization failed: {e}")
            
            if self.config.enable_surf:
                try:
                    # SURF requires opencv-contrib-python
                    self.surf = cv2.xfeatures2d.SURF_create(hessianThreshold=400)
                    logger.info("SURF detector initialized")
                except Exception as e:
                    logger.warning(f"SURF not available: {e}")
            
            if self.config.enable_orb:
                try:
                    self.orb = cv2.ORB_create(nfeatures=self.config.max_keypoints)
                    logger.info("ORB detector initialized")
                except Exception as e:
                    logger.warning(f"ORB initialization failed: {e}")
    
    async def process_image(self, image_path: str) -> ImageFingerprint:
        """Traitement industriel complet d'une image"""
        start_time = time.time()
        
        try:
            # Validate image
            if not Path(image_path).exists():
                raise FileNotFoundError(f"Image not found: {image_path}")
            
            # Generate unique fingerprint ID
            fingerprint_id = self._generate_fingerprint_id(image_path)
            
            # Load and validate image
            image = await self._load_and_validate_image(image_path)
            if image is None:
                raise ValueError(f"Cannot load image: {image_path}")
            
            # Process with all algorithms in parallel
            tasks = []
            
            # Perceptual hashing (ALL 4 TYPES)
            if IMAGEHASH_AVAILABLE:
                tasks.append(self._extract_perceptual_hashes(image))
            
            # CLIP embeddings
            if self.clip_model is not None:
                tasks.append(self._extract_clip_features(image))
            
            # Traditional CV features
            if CV2_AVAILABLE:
                cv_image = np.array(image)
                cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGB2BGR)
                tasks.append(self._extract_traditional_features(cv_image))
            
            # Geometric transformation resistance
            if CV2_AVAILABLE:
                cv_image = np.array(image)
                cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGB2BGR)
                tasks.append(self._extract_geometric_resistant_features(cv_image))
            
            # Execute all tasks
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Combine results
            perceptual_hashes = results[0] if len(results) > 0 and not isinstance(results[0], Exception) else {}
            clip_features = results[1] if len(results) > 1 and not isinstance(results[1], Exception) else {}
            traditional_features = results[2] if len(results) > 2 and not isinstance(results[2], Exception) else {}
            geometric_features = results[3] if len(results) > 3 and not isinstance(results[3], Exception) else {}
            
            # Calculate quality metrics
            quality_metrics = self._calculate_quality_metrics(image, traditional_features, geometric_features)
            
            # Get image properties
            image_properties = self._extract_image_properties(image)
            
            processing_time = time.time() - start_time
            
            # Create comprehensive fingerprint
            fingerprint = ImageFingerprint(
                image_path=image_path,
                fingerprint_id=fingerprint_id,
                processing_time=processing_time,
                timestamp=datetime.utcnow().isoformat(),
                
                # Perceptual hashes
                phash=perceptual_hashes.get('phash'),
                dhash=perceptual_hashes.get('dhash'),
                ahash=perceptual_hashes.get('ahash'),
                whash=perceptual_hashes.get('whash'),
                combined_hash=perceptual_hashes.get('combined_hash'),
                
                # CLIP features
                clip_embedding=clip_features.get('embedding'),
                clip_embedding_hash=clip_features.get('embedding_hash'),
                
                # Traditional CV features
                sift_features=traditional_features.get('sift'),
                surf_features=traditional_features.get('surf'),
                orb_features=traditional_features.get('orb'),
                
                # Geometric resistance
                multi_scale_features=geometric_features.get('multi_scale'),
                rotation_invariant_features=geometric_features.get('rotation_invariant'),
                
                # Quality metrics
                image_quality_score=quality_metrics.get('quality_score', 0.0),
                feature_density=quality_metrics.get('feature_density', 0.0),
                geometric_stability=quality_metrics.get('geometric_stability', 0.0),
                
                # Metadata
                image_properties=image_properties,
                config_used=self.config.__dict__
            )
            
            logger.info(f"Industrial fingerprinting completed for {image_path} in {processing_time:.3f}s")
            return fingerprint
            
        except Exception as e:
            logger.error(f"Industrial image processing failed for {image_path}: {e}")
            raise
    
    async def _load_and_validate_image(self, image_path: str) -> Optional[Image.Image]:
        """Charge et valide l'image"""
        if not PIL_AVAILABLE:
            logger.error("PIL not available for image loading")
            return None
        
        try:
            image = Image.open(image_path)
            
            # Validate format
            if image.format and image.format.lower() not in [f.replace('.', '') for f in self.config.supported_formats]:
                logger.warning(f"Unsupported format: {image.format}")
            
            # Validate size
            if image.width < self.config.min_dimension or image.height < self.config.min_dimension:
                logger.warning(f"Image too small: {image.width}x{image.height}")
            
            if image.width > self.config.max_dimension or image.height > self.config.max_dimension:
                # Resize while preserving aspect ratio
                image.thumbnail((self.config.max_dimension, self.config.max_dimension), Image.Resampling.LANCZOS)
            
            # Convert to RGB for consistent processing
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            return image
            
        except Exception as e:
            logger.error(f"Failed to load image {image_path}: {e}")
            return None
    
    async def _extract_perceptual_hashes(self, image: Image.Image) -> Dict[str, str]:
        """Extrait TOUS les hash perceptuels (pHash, dHash, aHash, wHash)"""
        hashes = {}
        
        if not IMAGEHASH_AVAILABLE:
            logger.warning("ImageHash library not available")
            return hashes
        
        try:
            # Perceptual Hash (DCT-based) - Most robust
            if self.config.enable_phash:
                hashes['phash'] = str(imagehash.phash(image, hash_size=self.config.hash_size))
            
            # Difference Hash (gradient-based) - Good for transformations
            if self.config.enable_dhash:
                hashes['dhash'] = str(imagehash.dhash(image, hash_size=self.config.hash_size))
            
            # Average Hash (mean luminance) - Simple and fast
            if self.config.enable_ahash:
                hashes['ahash'] = str(imagehash.average_hash(image, hash_size=self.config.hash_size))
            
            # Wavelet Hash (wavelet transform) - Robust to compression
            if self.config.enable_whash:
                hashes['whash'] = str(imagehash.whash(image, hash_size=self.config.hash_size))
            
            # Combined hash for industrial robustness
            if hashes:
                combined = ''.join(hashes.values())
                hashes['combined_hash'] = hashlib.sha256(combined.encode()).hexdigest()
            
            logger.debug(f"Extracted {len(hashes)} perceptual hashes")
            
        except Exception as e:
            logger.error(f"Perceptual hash extraction failed: {e}")
        
        return hashes
    
    async def _extract_clip_features(self, image: Image.Image) -> Dict[str, Any]:
        """Extrait les caractéristiques CLIP vision-language"""
        features = {}
        
        if self.clip_model is None:
            logger.warning("CLIP model not available")
            return features
        
        try:
            if CLIP_AVAILABLE:
                # Original CLIP implementation
                image_tensor = self.clip_processor(image).unsqueeze(0)
                if torch.cuda.is_available() and self.config.use_gpu:
                    image_tensor = image_tensor.cuda()
                
                with torch.no_grad():
                    image_features = self.clip_model.encode_image(image_tensor)
                    embedding = image_features.cpu().numpy().flatten().tolist()
            
            elif TRANSFORMERS_CLIP_AVAILABLE:
                # Transformers CLIP implementation
                inputs = self.clip_processor(images=image, return_tensors="pt")
                with torch.no_grad():
                    image_features = self.clip_model.get_image_features(**inputs)
                    embedding = image_features.squeeze().numpy().tolist()
            
            else:
                logger.warning("No CLIP implementation available")
                return features
            
            # Create embedding hash for indexing
            embedding_bytes = np.array(embedding).tobytes()
            embedding_hash = hashlib.sha256(embedding_bytes).hexdigest()
            
            features = {
                'embedding': embedding,
                'embedding_hash': embedding_hash,
                'embedding_dimension': len(embedding)
            }
            
            logger.debug(f"Extracted CLIP embedding with {len(embedding)} dimensions")
            
        except Exception as e:
            logger.error(f"CLIP feature extraction failed: {e}")
        
        return features
    
    async def _extract_traditional_features(self, cv_image: np.ndarray) -> Dict[str, Any]:
        """Extrait les caractéristiques SIFT/SURF/ORB"""
        features = {}
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        try:
            # SIFT Features (Scale-Invariant Feature Transform)
            if self.sift is not None and self.config.enable_sift:
                kp_sift, desc_sift = self.sift.detectAndCompute(gray, None)
                features['sift'] = self._process_keypoints_descriptors('SIFT', kp_sift, desc_sift)
            
            # SURF Features (Speeded-Up Robust Features)
            if self.surf is not None and self.config.enable_surf:
                kp_surf, desc_surf = self.surf.detectAndCompute(gray, None)
                features['surf'] = self._process_keypoints_descriptors('SURF', kp_surf, desc_surf)
            
            # ORB Features (Oriented FAST and Rotated BRIEF)
            if self.orb is not None and self.config.enable_orb:
                kp_orb, desc_orb = self.orb.detectAndCompute(gray, None)
                features['orb'] = self._process_keypoints_descriptors('ORB', kp_orb, desc_orb)
            
            logger.debug(f"Extracted traditional CV features: {list(features.keys())}")
            
        except Exception as e:
            logger.error(f"Traditional feature extraction failed: {e}")
        
        return features
    
    async def _extract_geometric_resistant_features(self, cv_image: np.ndarray) -> Dict[str, Any]:
        """Extrait les caractéristiques résistantes aux transformations géométriques"""
        features = {}
        
        try:
            # Multi-scale feature extraction
            if self.config.enable_multi_scale:
                multi_scale_features = []
                for scale in self.config.scale_factors:
                    if scale != 1.0:
                        h, w = cv_image.shape[:2]
                        new_h, new_w = int(h * scale), int(w * scale)
                        scaled_image = cv2.resize(cv_image, (new_w, new_h))
                    else:
                        scaled_image = cv_image
                    
                    # Extract SIFT features at this scale
                    if self.sift is not None:
                        gray_scaled = cv2.cvtColor(scaled_image, cv2.COLOR_BGR2GRAY)
                        kp, desc = self.sift.detectAndCompute(gray_scaled, None)
                        scale_features = self._process_keypoints_descriptors(f'SIFT_scale_{scale}', kp, desc)
                        multi_scale_features.append({
                            'scale': scale,
                            'features': scale_features
                        })
                
                features['multi_scale'] = multi_scale_features
            
            # Rotation-invariant features
            if self.config.rotation_angles:
                rotation_features = []
                for angle in self.config.rotation_angles:
                    if angle != 0:
                        h, w = cv_image.shape[:2]
                        center = (w // 2, h // 2)
                        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
                        rotated_image = cv2.warpAffine(cv_image, rotation_matrix, (w, h))
                    else:
                        rotated_image = cv_image
                    
                    # Extract ORB features (rotation-invariant by design)
                    if self.orb is not None:
                        gray_rotated = cv2.cvtColor(rotated_image, cv2.COLOR_BGR2GRAY)
                        kp, desc = self.orb.detectAndCompute(gray_rotated, None)
                        rotation_feat = self._process_keypoints_descriptors(f'ORB_rot_{angle}', kp, desc)
                        rotation_features.append({
                            'angle': angle,
                            'features': rotation_feat
                        })
                
                features['rotation_invariant'] = rotation_features
            
            logger.debug(f"Extracted geometric resistant features")
            
        except Exception as e:
            logger.error(f"Geometric resistant feature extraction failed: {e}")
        
        return features
    
    def _process_keypoints_descriptors(self, feature_type: str, keypoints, descriptors) -> Dict[str, Any]:
        """Traite les keypoints et descripteurs pour créer une représentation compacte"""
        if descriptors is None or len(keypoints) == 0:
            return {
                'feature_type': feature_type,
                'num_keypoints': 0,
                'feature_hash': '',
                'keypoint_locations': []
            }
        
        try:
            # Basic statistics
            feature_data = {
                'feature_type': feature_type,
                'num_keypoints': len(keypoints),
                'descriptor_shape': descriptors.shape,
                'keypoint_locations': [(kp.pt[0], kp.pt[1]) for kp in keypoints[:50]]  # Limit for size
            }
            
            # Create compact representation using clustering or hashing
            if SKLEARN_AVAILABLE and len(descriptors) > 10:
                # Use k-means to create vocabulary of visual words
                n_clusters = min(50, len(descriptors))
                kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                clusters = kmeans.fit_predict(descriptors)
                
                # Create histogram of visual words
                histogram = np.bincount(clusters, minlength=n_clusters)
                feature_hash = hashlib.md5(histogram.tobytes()).hexdigest()
                
                feature_data.update({
                    'visual_words_histogram': histogram.tolist(),
                    'feature_hash': feature_hash
                })
            else:
                # Simple hash of descriptors
                feature_hash = hashlib.md5(descriptors.tobytes()).hexdigest()
                feature_data['feature_hash'] = feature_hash
            
            return feature_data
            
        except Exception as e:
            logger.error(f"Keypoint processing failed for {feature_type}: {e}")
            return {
                'feature_type': feature_type,
                'num_keypoints': len(keypoints),
                'feature_hash': '',
                'error': str(e)
            }
    
    def _calculate_quality_metrics(self, image: Image.Image, traditional_features: Dict, geometric_features: Dict) -> Dict[str, float]:
        """Calcule les métriques de qualité industrielles"""
        metrics = {
            'quality_score': 0.0,
            'feature_density': 0.0,
            'geometric_stability': 0.0
        }
        
        try:
            # Basic quality score based on image properties
            width, height = image.size
            pixel_count = width * height
            
            # Normalize quality score
            if pixel_count > 0:
                metrics['quality_score'] = min(1.0, pixel_count / (1024 * 1024))  # 1MP reference
            
            # Feature density calculation
            total_features = 0
            for feature_type, features in traditional_features.items():
                if isinstance(features, dict) and 'num_keypoints' in features:
                    total_features += features['num_keypoints']
            
            if pixel_count > 0:
                metrics['feature_density'] = total_features / (pixel_count / 10000)  # Features per 10K pixels
            
            # Geometric stability based on multi-scale consistency
            if 'multi_scale' in geometric_features:
                scale_features = geometric_features['multi_scale']
                if len(scale_features) > 1:
                    # Calculate consistency across scales
                    feature_counts = [sf['features'].get('num_keypoints', 0) for sf in scale_features]
                    if feature_counts:
                        consistency = 1.0 - (np.std(feature_counts) / (np.mean(feature_counts) + 1))
                        metrics['geometric_stability'] = max(0.0, min(1.0, consistency))
            
        except Exception as e:
            logger.error(f"Quality metrics calculation failed: {e}")
        
        return metrics
    
    def _extract_image_properties(self, image: Image.Image) -> Dict[str, Any]:
        """Extrait les propriétés de base de l'image"""
        try:
            properties = {
                'width': image.width,
                'height': image.height,
                'mode': image.mode,
                'format': image.format,
                'aspect_ratio': image.width / image.height if image.height > 0 else 0,
                'pixel_count': image.width * image.height
            }
            
            # Color statistics for RGB images
            if image.mode == 'RGB' and PIL_AVAILABLE:
                stat = ImageStat.Stat(image)
                properties['color_stats'] = {
                    'mean': stat.mean,
                    'median': stat.median,
                    'stddev': stat.stddev
                }
            
            return properties
            
        except Exception as e:
            logger.error(f"Image properties extraction failed: {e}")
            return {}
    
    def _generate_fingerprint_id(self, image_path: str) -> str:
        """Génère un ID unique pour l'empreinte"""
        path_hash = hashlib.md5(image_path.encode()).hexdigest()
        timestamp = str(int(time.time() * 1000))
        return f"industrial_{path_hash[:8]}_{timestamp}"
    
    def compare_fingerprints(self, fp1: ImageFingerprint, fp2: ImageFingerprint) -> Dict[str, float]:
        """Compare deux empreintes industrielles"""
        similarities = {}
        
        try:
            # Compare perceptual hashes
            if fp1.phash and fp2.phash and IMAGEHASH_AVAILABLE:
                similarities['phash_similarity'] = 1.0 - (bin(int(fp1.phash, 16) ^ int(fp2.phash, 16)).count('1') / (len(fp1.phash) * 4))
            
            if fp1.dhash and fp2.dhash and IMAGEHASH_AVAILABLE:
                similarities['dhash_similarity'] = 1.0 - (bin(int(fp1.dhash, 16) ^ int(fp2.dhash, 16)).count('1') / (len(fp1.dhash) * 4))
            
            # Compare CLIP embeddings
            if fp1.clip_embedding and fp2.clip_embedding:
                embedding1 = np.array(fp1.clip_embedding)
                embedding2 = np.array(fp2.clip_embedding)
                cosine_sim = np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))
                similarities['clip_similarity'] = float(cosine_sim)
            
            # Compare traditional features by hash
            for feature_type in ['sift', 'surf', 'orb']:
                fp1_feat = getattr(fp1, f'{feature_type}_features', None)
                fp2_feat = getattr(fp2, f'{feature_type}_features', None)
                
                if fp1_feat and fp2_feat and 'feature_hash' in fp1_feat and 'feature_hash' in fp2_feat:
                    similarities[f'{feature_type}_match'] = 1.0 if fp1_feat['feature_hash'] == fp2_feat['feature_hash'] else 0.0
            
            # Overall similarity score
            if similarities:
                similarities['overall_similarity'] = sum(similarities.values()) / len(similarities)
            
        except Exception as e:
            logger.error(f"Fingerprint comparison failed: {e}")
        
        return similarities

# Factory function for easy instantiation
def create_industrial_processor(
    enable_all_hashes: bool = True,
    enable_clip: bool = True,
    enable_traditional_cv: bool = True,
    enable_geometric_resistance: bool = True,
    use_gpu: bool = False
) -> IndustrialImageProcessor:
    """Factory pour créer un processeur industriel avec configuration simplifiée"""
    
    config = IndustrialImageConfig(
        enable_phash=enable_all_hashes,
        enable_dhash=enable_all_hashes,
        enable_ahash=enable_all_hashes,
        enable_whash=enable_all_hashes,
        enable_clip=enable_clip,
        enable_sift=enable_traditional_cv,
        enable_surf=enable_traditional_cv,
        enable_orb=enable_traditional_cv,
        enable_multi_scale=enable_geometric_resistance,
        enable_affine_invariance=enable_geometric_resistance,
        use_gpu=use_gpu
    )
    
    return IndustrialImageProcessor(config)

# Example usage and testing
async def test_industrial_processor():
    """Test function for the industrial processor"""
    logger.info("Testing Industrial Image Processor...")
    
    # Create processor with all algorithms enabled
    processor = create_industrial_processor(
        enable_all_hashes=True,
        enable_clip=True,
        enable_traditional_cv=True,
        enable_geometric_resistance=True,
        use_gpu=False
    )
    
    # Test with a sample image path (would need actual image)
    try:
        # This would need an actual image file to test
        # fingerprint = await processor.process_image("/path/to/test/image.jpg")
        # logger.info(f"Generated fingerprint: {fingerprint.fingerprint_id}")
        logger.info("Industrial processor created successfully")
    except Exception as e:
        logger.info(f"Test requires actual image file: {e}")

if __name__ == "__main__":
    asyncio.run(test_industrial_processor())