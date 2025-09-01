"""🖼️ Enhanced Image Protection with Perceptual Hashing + Watermarking
=====================================================================

Production-grade image protection combining advanced perceptual hashing
with digital watermarking for robust copyright protection.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import hashlib
import json
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Union
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
import io
import base64

# Core image processing
try:
    import cv2
    import imagehash
    from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
    from PIL.ExifTags import TAGS
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    logging.warning("PIL/Pillow dependencies not available")

# Advanced image processing and ML
try:
    from sklearn.cluster import KMeans
    from sklearn.metrics.pairwise import cosine_similarity
    from scipy import ndimage
    from skimage import feature, filters, segmentation
    import matplotlib.pyplot as plt
    HAS_ADVANCED = True
except ImportError:
    HAS_ADVANCED = False
    logging.warning("Advanced image processing dependencies not available")

logger = logging.getLogger(__name__)

@dataclass
class WatermarkConfig:
    """Configuration for watermarking."""
    text: str = "© Protected Content"
    opacity: float = 0.3
    position: str = "bottom_right"  # bottom_right, center, top_left, etc.
    font_size: int = 36
    font_color: Tuple[int, int, int] = (255, 255, 255)
    embed_invisible: bool = True
    steganography_bits: int = 2

@dataclass
class EnhancedImageFingerprint:
    """Enhanced image fingerprint with watermarking capabilities."""
    file_id: str
    perceptual_hashes: Dict[str, str]
    feature_descriptors: Dict[str, Any]
    color_features: Dict[str, Any]
    texture_features: Dict[str, Any]
    geometric_features: Dict[str, Any]
    metadata: Dict[str, Any]
    watermark_signature: Optional[str]
    steganography_hash: Optional[str]
    confidence_score: float
    dimensions: Tuple[int, int]
    file_size: int
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

class ImageProtectionEngine:
    """Production-grade image protection with perceptual hashing + watermarking."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.hash_sizes = self.config.get('hash_sizes', [8, 16, 32])
        self.watermark_config = WatermarkConfig(**self.config.get('watermark', {}))
        self.enable_steganography = self.config.get('enable_steganography', True)
        
        # Feature extraction parameters
        self.sift_features = self.config.get('sift_features', True)
        self.orb_features = self.config.get('orb_features', True)
        self.color_histogram_bins = self.config.get('color_histogram_bins', 256)
        
        logger.info("ImageProtectionEngine initialized with perceptual hashing + watermarking")
    
    async def generate_fingerprint(self, image_file_path: str, apply_watermark: bool = False, metadata: Optional[Dict] = None) -> EnhancedImageFingerprint:
        """Generate enhanced image fingerprint with optional watermarking."""
        try:
            file_path = Path(image_file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"Image file not found: {image_file_path}")
            
            # Load image
            image = await self._load_image(image_file_path)
            original_image = image.copy()
            
            # Apply watermark if requested
            watermark_signature = None
            steganography_hash = None
            
            if apply_watermark:
                image, watermark_signature = await self._apply_watermark(image)
                
                if self.enable_steganography:
                    image, steganography_hash = await self._embed_steganography(image, image_file_path)
            
            # Generate file ID
            file_id = await self._generate_file_id(image_file_path, original_image)
            
            # Parallel feature extraction
            fingerprint_tasks = [
                self._extract_perceptual_hashes(original_image),
                self._extract_feature_descriptors(original_image),
                self._extract_color_features(original_image),
                self._extract_texture_features(original_image),
                self._extract_geometric_features(original_image),
                self._extract_image_metadata(image_file_path)
            ]
            
            results = await asyncio.gather(*fingerprint_tasks)
            (perceptual_hashes, feature_descriptors, color_features,
             texture_features, geometric_features, image_metadata) = results
            
            # Calculate confidence score
            confidence_score = await self._calculate_confidence_score(results)
            
            # Get image dimensions and file size
            dimensions = original_image.size
            file_size = file_path.stat().st_size
            
            fingerprint = EnhancedImageFingerprint(
                file_id=file_id,
                perceptual_hashes=perceptual_hashes,
                feature_descriptors=feature_descriptors,
                color_features=color_features,
                texture_features=texture_features,
                geometric_features=geometric_features,
                metadata=image_metadata,
                watermark_signature=watermark_signature,
                steganography_hash=steganography_hash,
                confidence_score=confidence_score,
                dimensions=dimensions,
                file_size=file_size
            )
            
            # Save watermarked image if watermark was applied
            if apply_watermark and watermark_signature:
                watermarked_path = file_path.with_suffix(f'_watermarked{file_path.suffix}')
                image.save(watermarked_path, quality=95)
                logger.info(f"Watermarked image saved: {watermarked_path}")
            
            logger.info(f"Enhanced image fingerprint generated. Confidence: {confidence_score:.3f}")
            return fingerprint
            
        except Exception as e:
            logger.error(f"Error generating enhanced image fingerprint: {str(e)}")
            raise
    
    async def _load_image(self, image_file_path: str):
        """Load and validate image file."""
        try:
            if HAS_PIL:
                from PIL import Image
                image = Image.open(image_file_path)
                
                # Convert to RGB if necessary
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                return image
            else:
                raise ImportError("PIL not available for image loading")
                
        except Exception as e:
            logger.error(f"Error loading image: {e}")
            raise
    
    async def _extract_perceptual_hashes(self, image) -> Dict[str, str]:
        """Extract multiple perceptual hashes for robust matching."""
        try:
            hashes = {}
            
            for size in self.hash_sizes:
                # Perceptual hash (pHash) - most robust
                hashes[f'phash_{size}'] = str(imagehash.phash(image, hash_size=size))
                
                # Difference hash (dHash) - good for slight modifications
                hashes[f'dhash_{size}'] = str(imagehash.dhash(image, hash_size=size))
                
                # Average hash (aHash) - fast but less robust
                hashes[f'ahash_{size}'] = str(imagehash.average_hash(image, hash_size=size))
            
            # Wavelet hash - robust to compression
            hashes['whash'] = str(imagehash.whash(image))
            
            # Color hash - robust to geometric transforms
            hashes['colorhash'] = str(imagehash.colorhash(image))
            
            # Crop-resistant hash
            hashes['crop_resistant'] = str(imagehash.crop_resistant_hash(image))
            
            return hashes
            
        except Exception as e:
            logger.error(f"Error extracting perceptual hashes: {e}")
            return {}
    
    async def _extract_feature_descriptors(self, image) -> Dict[str, Any]:
        """Extract traditional computer vision feature descriptors."""
        try:
            descriptors = {}
            
            # Convert to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # SIFT features (Scale-Invariant Feature Transform)
            if self.sift_features and cv2:
                try:
                    sift = cv2.SIFT_create()
                    keypoints, sift_descriptors = sift.detectAndCompute(gray, None)
                    
                    if sift_descriptors is not None:
                        # Summarize SIFT descriptors
                        descriptors['sift'] = {
                            'keypoint_count': len(keypoints),
                            'descriptor_mean': np.mean(sift_descriptors, axis=0).tolist(),
                            'descriptor_std': np.std(sift_descriptors, axis=0).tolist(),
                            'descriptor_shape': sift_descriptors.shape
                        }
                except Exception as e:
                    logger.warning(f"SIFT extraction failed: {e}")
            
            # ORB features (Oriented FAST and Rotated BRIEF)
            if self.orb_features and cv2:
                try:
                    orb = cv2.ORB_create()
                    keypoints, orb_descriptors = orb.detectAndCompute(gray, None)
                    
                    if orb_descriptors is not None:
                        descriptors['orb'] = {
                            'keypoint_count': len(keypoints),
                            'descriptor_mean': np.mean(orb_descriptors.astype(float), axis=0).tolist(),
                            'descriptor_std': np.std(orb_descriptors.astype(float), axis=0).tolist(),
                            'descriptor_shape': orb_descriptors.shape
                        }
                except Exception as e:
                    logger.warning(f"ORB extraction failed: {e}")
            
            # HOG features (Histogram of Oriented Gradients)
            if HAS_ADVANCED:
                try:
                    hog_features = feature.hog(gray, orientations=9, pixels_per_cell=(8, 8),
                                           cells_per_block=(2, 2), visualize=False)
                    descriptors['hog'] = {
                        'features': hog_features.tolist(),
                        'feature_count': len(hog_features)
                    }
                except Exception as e:
                    logger.warning(f"HOG extraction failed: {e}")
            
            return descriptors
            
        except Exception as e:
            logger.error(f"Error extracting feature descriptors: {e}")
            return {}
    
    async def _extract_color_features(self, image) -> Dict[str, Any]:
        """Extract comprehensive color features."""
        try:
            color_features = {}
            
            # Convert to numpy array
            img_array = np.array(image)
            
            # Color histograms
            hist_r, _ = np.histogram(img_array[:, :, 0], bins=self.color_histogram_bins, range=[0, 256])
            hist_g, _ = np.histogram(img_array[:, :, 1], bins=self.color_histogram_bins, range=[0, 256])
            hist_b, _ = np.histogram(img_array[:, :, 2], bins=self.color_histogram_bins, range=[0, 256])
            
            color_features['histograms'] = {
                'red': hist_r.tolist(),
                'green': hist_g.tolist(),
                'blue': hist_b.tolist()
            }
            
            # Color moments
            color_features['moments'] = {
                'mean_rgb': np.mean(img_array, axis=(0, 1)).tolist(),
                'std_rgb': np.std(img_array, axis=(0, 1)).tolist(),
                'skew_rgb': [float(np.mean(((img_array[:, :, i] - np.mean(img_array[:, :, i])) / np.std(img_array[:, :, i])) ** 3)) for i in range(3)]
            }
            
            # Dominant colors using clustering
            if HAS_ADVANCED:
                pixels = img_array.reshape(-1, 3)
                sample_size = min(10000, len(pixels))
                sampled_pixels = pixels[::len(pixels)//sample_size]
                
                kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
                kmeans.fit(sampled_pixels)
                
                color_features['dominant_colors'] = kmeans.cluster_centers_.tolist()
                color_features['color_percentages'] = (np.bincount(kmeans.labels_) / len(kmeans.labels_)).tolist()
            
            # Color coherence
            hsv_image = image.convert('HSV')
            hsv_array = np.array(hsv_image)
            
            color_features['hsv_stats'] = {
                'hue_mean': float(np.mean(hsv_array[:, :, 0])),
                'saturation_mean': float(np.mean(hsv_array[:, :, 1])),
                'value_mean': float(np.mean(hsv_array[:, :, 2])),
                'hue_std': float(np.std(hsv_array[:, :, 0])),
                'saturation_std': float(np.std(hsv_array[:, :, 1])),
                'value_std': float(np.std(hsv_array[:, :, 2]))
            }
            
            return color_features
            
        except Exception as e:
            logger.error(f"Error extracting color features: {e}")
            return {}
    
    async def _extract_texture_features(self, image) -> Dict[str, Any]:
        """Extract texture analysis features."""
        try:
            texture_features = {}
            
            # Convert to grayscale
            gray_image = image.convert('L')
            gray_array = np.array(gray_image)
            
            # Basic texture statistics
            texture_features['basic_stats'] = {
                'mean': float(np.mean(gray_array)),
                'std': float(np.std(gray_array)),
                'variance': float(np.var(gray_array)),
                'entropy': float(-np.sum(np.histogram(gray_array, bins=256)[0] * np.log2(np.histogram(gray_array, bins=256)[0] + 1e-7)))
            }
            
            # Edge detection features
            if cv2:
                edges = cv2.Canny(gray_array, 100, 200)
                texture_features['edge_features'] = {
                    'edge_density': float(np.sum(edges > 0) / edges.size),
                    'edge_strength': float(np.mean(edges[edges > 0])) if np.any(edges > 0) else 0.0
                }
            
            # Local Binary Pattern (LBP)
            if HAS_ADVANCED:
                lbp = feature.local_binary_pattern(gray_array, P=8, R=1, method='uniform')
                lbp_hist, _ = np.histogram(lbp, bins=256, range=[0, 256])
                texture_features['lbp'] = {
                    'histogram': lbp_hist.tolist(),
                    'uniformity': float(np.sum(lbp_hist ** 2)),
                    'entropy': float(-np.sum((lbp_hist / np.sum(lbp_hist)) * np.log2((lbp_hist / np.sum(lbp_hist)) + 1e-7)))
                }
            
            # Gabor filters
            if HAS_ADVANCED:
                gabor_responses = []
                for theta in [0, 45, 90, 135]:
                    filtered = filters.gabor(gray_array, frequency=0.1, theta=np.radians(theta))
                    gabor_responses.append(np.mean(filtered[0]))
                
                texture_features['gabor'] = {
                    'responses': gabor_responses,
                    'mean_response': float(np.mean(gabor_responses)),
                    'response_variance': float(np.var(gabor_responses))
                }
            
            return texture_features
            
        except Exception as e:
            logger.error(f"Error extracting texture features: {e}")
            return {}
    
    async def _extract_geometric_features(self, image) -> Dict[str, Any]:
        """Extract geometric and shape features."""
        try:
            geometric_features = {}
            
            # Image dimensions and aspect ratio
            width, height = image.size
            geometric_features['dimensions'] = {
                'width': width,
                'height': height,
                'aspect_ratio': width / height,
                'total_pixels': width * height
            }
            
            # Convert to grayscale for shape analysis
            gray_image = image.convert('L')
            gray_array = np.array(gray_image)
            
            # Edge-based features
            if cv2:
                edges = cv2.Canny(gray_array, 50, 150)
                
                # Find contours
                contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                if contours:
                    # Analyze largest contour
                    largest_contour = max(contours, key=cv2.contourArea)
                    
                    geometric_features['contour_analysis'] = {
                        'contour_count': len(contours),
                        'largest_contour_area': float(cv2.contourArea(largest_contour)),
                        'largest_contour_perimeter': float(cv2.arcLength(largest_contour, True)),
                        'solidity': float(cv2.contourArea(largest_contour) / cv2.contourArea(cv2.convexHull(largest_contour))) if cv2.contourArea(cv2.convexHull(largest_contour)) > 0 else 0.0
                    }
            
            # Moments analysis
            if HAS_ADVANCED:
                moments = cv2.moments(gray_array) if cv2 else {}
                if moments:
                    geometric_features['moments'] = {
                        'spatial_moments': {k: float(v) for k, v in moments.items() if k.startswith('m')},
                        'central_moments': {k: float(v) for k, v in moments.items() if k.startswith('mu')},
                        'normalized_moments': {k: float(v) for k, v in moments.items() if k.startswith('nu')}
                    }
            
            return geometric_features
            
        except Exception as e:
            logger.error(f"Error extracting geometric features: {e}")
            return {}
    
    async def _extract_image_metadata(self, image_file_path: str) -> Dict[str, Any]:
        """Extract image metadata and EXIF data."""
        try:
            metadata = {}
            
            if HAS_PIL:
                image = Image.open(image_file_path)
                
                # Basic image info
                metadata['basic_info'] = {
                    'format': image.format,
                    'mode': image.mode,
                    'size': image.size,
                    'has_transparency': 'transparency' in image.info
                }
                
                # EXIF data
                exif_data = {}
                if hasattr(image, '_getexif') and image._getexif():
                    exif = image._getexif()
                    for tag_id, value in exif.items():
                        tag = TAGS.get(tag_id, tag_id)
                        exif_data[tag] = str(value)  # Convert to string for JSON serialization
                
                metadata['exif'] = exif_data
                
                # File info
                file_path = Path(image_file_path)
                metadata['file_info'] = {
                    'filename': file_path.name,
                    'file_size': file_path.stat().st_size,
                    'creation_time': file_path.stat().st_ctime,
                    'modification_time': file_path.stat().st_mtime
                }
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting image metadata: {e}")
            return {}
    
    async def _apply_watermark(self, image) -> Tuple[Any, str]:
        """Apply visible watermark to image."""
        try:
            if not HAS_PIL:
                logger.warning("PIL not available - watermarking skipped")
                return image, None
            
            from PIL import Image, ImageDraw, ImageFont
            
            # Create a copy to avoid modifying original
            watermarked = image.copy()
            
            # Create drawing context
            draw = ImageDraw.Draw(watermarked)
            
            # Try to load a font
            try:
                # Try to use a TrueType font
                font = ImageFont.truetype("arial.ttf", self.watermark_config.font_size)
            except:
                # Fall back to default font
                font = ImageFont.load_default()
            
            # Calculate text position
            text = self.watermark_config.text
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            width, height = watermarked.size
            
            # Position watermark
            if self.watermark_config.position == "bottom_right":
                x = width - text_width - 20
                y = height - text_height - 20
            elif self.watermark_config.position == "center":
                x = (width - text_width) // 2
                y = (height - text_height) // 2
            elif self.watermark_config.position == "top_left":
                x = 20
                y = 20
            else:  # bottom_right as default
                x = width - text_width - 20
                y = height - text_height - 20
            
            # Create watermark overlay
            overlay = Image.new('RGBA', watermarked.size, (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            
            # Draw text with opacity
            text_color = (*self.watermark_config.font_color, int(255 * self.watermark_config.opacity))
            overlay_draw.text((x, y), text, font=font, fill=text_color)
            
            # Composite with original image
            watermarked = Image.alpha_composite(watermarked.convert('RGBA'), overlay).convert('RGB')
            
            # Generate watermark signature
            watermark_data = f"{text}_{self.watermark_config.position}_{self.watermark_config.opacity}"
            watermark_signature = hashlib.sha256(watermark_data.encode()).hexdigest()[:16]
            
            logger.info("Visible watermark applied successfully")
            return watermarked, watermark_signature
            
        except Exception as e:
            logger.error(f"Error applying watermark: {e}")
            return image, None
    
    async def _embed_steganography(self, image, original_path: str) -> Tuple[Any, str]:
        """Embed invisible steganographic signature."""
        try:
            if not HAS_PIL:
                logger.warning("PIL not available - steganography skipped")
                return image, None
            
            from PIL import Image
            
            # Create steganographic signature
            signature_data = f"{original_path}_{datetime.utcnow().isoformat()}"
            signature_hash = hashlib.sha256(signature_data.encode()).hexdigest()
            
            # Convert to numpy array
            img_array = np.array(image)
            
            # Embed signature in least significant bits
            binary_signature = ''.join(format(ord(char), '08b') for char in signature_hash[:32])  # 32 chars = 256 bits
            
            # Embed in red channel LSBs
            flat_red = img_array[:, :, 0].flatten()
            
            for i, bit in enumerate(binary_signature):
                if i < len(flat_red):
                    # Modify LSB
                    flat_red[i] = (flat_red[i] & 0xFE) | int(bit)
            
            # Reshape back
            img_array[:, :, 0] = flat_red.reshape(img_array.shape[:2])
            
            # Convert back to PIL Image
            stego_image = Image.fromarray(img_array)
            
            logger.info("Steganographic signature embedded successfully")
            return stego_image, signature_hash[:16]
            
        except Exception as e:
            logger.error(f"Error embedding steganography: {e}")
            return image, None
    
    async def extract_steganography(self, image) -> Optional[str]:
        """Extract steganographic signature from image."""
        try:
            # Convert to numpy array
            img_array = np.array(image)
            
            # Extract from red channel LSBs
            flat_red = img_array[:, :, 0].flatten()
            
            # Extract 256 bits (32 characters)
            binary_signature = ''
            for i in range(256):
                if i < len(flat_red):
                    binary_signature += str(flat_red[i] & 1)
            
            # Convert binary to string
            signature = ''
            for i in range(0, len(binary_signature), 8):
                byte = binary_signature[i:i+8]
                if len(byte) == 8:
                    signature += chr(int(byte, 2))
            
            return signature[:16] if signature else None
            
        except Exception as e:
            logger.error(f"Error extracting steganography: {e}")
            return None
    
    async def _calculate_confidence_score(self, results: List[Any]) -> float:
        """Calculate confidence score for image fingerprint."""
        try:
            (perceptual_hashes, feature_descriptors, color_features,
             texture_features, geometric_features, image_metadata) = results
            
            base_confidence = 0.7
            
            # Perceptual hash quality
            if perceptual_hashes and len(perceptual_hashes) > 5:
                base_confidence += 0.1
            
            # Feature descriptor quality
            if feature_descriptors:
                if 'sift' in feature_descriptors:
                    base_confidence += 0.05
                if 'orb' in feature_descriptors:
                    base_confidence += 0.03
                if 'hog' in feature_descriptors:
                    base_confidence += 0.02
            
            # Color feature quality
            if color_features and 'histograms' in color_features:
                base_confidence += 0.05
            
            # Texture feature quality
            if texture_features and 'basic_stats' in texture_features:
                base_confidence += 0.03
            
            # Geometric feature quality
            if geometric_features and 'dimensions' in geometric_features:
                base_confidence += 0.02
            
            return min(base_confidence, 0.98)
            
        except Exception as e:
            logger.error(f"Error calculating confidence score: {e}")
            return 0.7
    
    async def _generate_file_id(self, file_path: str, image) -> str:
        """Generate unique file ID for image."""
        path_hash = hashlib.md5(str(file_path).encode()).hexdigest()[:8]
        
        # Generate content hash from image data
        img_array = np.array(image)
        content_hash = hashlib.sha256(img_array.tobytes()).hexdigest()[:16]
        
        return f"image_{path_hash}_{content_hash}"
    
    async def calculate_similarity(self, fingerprint1: EnhancedImageFingerprint, fingerprint2: EnhancedImageFingerprint) -> float:
        """Calculate similarity between two image fingerprints."""
        try:
            similarity_scores = []
            
            # Perceptual hash similarity (most important)
            hash_sim = self._calculate_hash_similarity(
                fingerprint1.perceptual_hashes,
                fingerprint2.perceptual_hashes
            )
            similarity_scores.append(hash_sim * 0.4)
            
            # Color feature similarity
            color_sim = self._calculate_color_similarity(
                fingerprint1.color_features,
                fingerprint2.color_features
            )
            similarity_scores.append(color_sim * 0.25)
            
            # Texture feature similarity
            texture_sim = self._calculate_texture_similarity(
                fingerprint1.texture_features,
                fingerprint2.texture_features
            )
            similarity_scores.append(texture_sim * 0.15)
            
            # Geometric similarity
            geometric_sim = self._calculate_geometric_similarity(
                fingerprint1.geometric_features,
                fingerprint2.geometric_features
            )
            similarity_scores.append(geometric_sim * 0.1)
            
            # Feature descriptor similarity
            feature_sim = self._calculate_feature_similarity(
                fingerprint1.feature_descriptors,
                fingerprint2.feature_descriptors
            )
            similarity_scores.append(feature_sim * 0.1)
            
            return sum(similarity_scores)
            
        except Exception as e:
            logger.error(f"Error calculating image similarity: {e}")
            return 0.0
    
    def _calculate_hash_similarity(self, hashes1: Dict[str, str], hashes2: Dict[str, str]) -> float:
        """Calculate similarity between perceptual hash sets."""
        if not hashes1 or not hashes2:
            return 0.0
        
        similarities = []
        for hash_type in hashes1:
            if hash_type in hashes2:
                hash1 = hashes1[hash_type]
                hash2 = hashes2[hash_type]
                
                if len(hash1) == len(hash2):
                    # Calculate Hamming distance
                    matches = sum(c1 == c2 for c1, c2 in zip(hash1, hash2))
                    similarity = matches / len(hash1)
                    similarities.append(similarity)
        
        return np.mean(similarities) if similarities else 0.0
    
    def _calculate_color_similarity(self, colors1: Dict, colors2: Dict) -> float:
        """Calculate color feature similarity."""
        if not colors1 or not colors2:
            return 0.0
        
        similarities = []
        
        # Compare color histograms
        if 'histograms' in colors1 and 'histograms' in colors2:
            for channel in ['red', 'green', 'blue']:
                if channel in colors1['histograms'] and channel in colors2['histograms']:
                    hist1 = np.array(colors1['histograms'][channel])
                    hist2 = np.array(colors2['histograms'][channel])
                    
                    # Calculate histogram correlation
                    correlation = np.corrcoef(hist1, hist2)[0, 1]
                    if not np.isnan(correlation):
                        similarities.append(max(0, correlation))
        
        # Compare color moments
        if 'moments' in colors1 and 'moments' in colors2:
            mean1 = np.array(colors1['moments']['mean_rgb'])
            mean2 = np.array(colors2['moments']['mean_rgb'])
            
            # Calculate Euclidean distance in color space
            distance = np.linalg.norm(mean1 - mean2)
            max_distance = np.linalg.norm([255, 255, 255])  # Maximum possible distance
            similarity = max(0, 1 - distance / max_distance)
            similarities.append(similarity)
        
        return np.mean(similarities) if similarities else 0.0
    
    def _calculate_texture_similarity(self, texture1: Dict, texture2: Dict) -> float:
        """Calculate texture feature similarity."""
        if not texture1 or not texture2:
            return 0.0
        
        similarities = []
        
        # Compare basic texture statistics
        if 'basic_stats' in texture1 and 'basic_stats' in texture2:
            stats1 = texture1['basic_stats']
            stats2 = texture2['basic_stats']
            
            for stat in ['mean', 'std', 'variance']:
                if stat in stats1 and stat in stats2:
                    val1, val2 = stats1[stat], stats2[stat]
                    max_val = max(abs(val1), abs(val2), 1.0)  # Avoid division by zero
                    similarity = 1 - abs(val1 - val2) / max_val
                    similarities.append(max(0, similarity))
        
        # Compare LBP histograms
        if 'lbp' in texture1 and 'lbp' in texture2:
            hist1 = np.array(texture1['lbp']['histogram'])
            hist2 = np.array(texture2['lbp']['histogram'])
            
            correlation = np.corrcoef(hist1, hist2)[0, 1]
            if not np.isnan(correlation):
                similarities.append(max(0, correlation))
        
        return np.mean(similarities) if similarities else 0.0
    
    def _calculate_geometric_similarity(self, geo1: Dict, geo2: Dict) -> float:
        """Calculate geometric feature similarity."""
        if not geo1 or not geo2:
            return 0.0
        
        similarities = []
        
        # Compare aspect ratios
        if 'dimensions' in geo1 and 'dimensions' in geo2:
            ar1 = geo1['dimensions']['aspect_ratio']
            ar2 = geo2['dimensions']['aspect_ratio']
            
            # Aspect ratio similarity
            ar_diff = abs(ar1 - ar2)
            ar_similarity = max(0, 1 - ar_diff / 2.0)  # Assume max reasonable difference is 2
            similarities.append(ar_similarity)
        
        # Compare contour features
        if 'contour_analysis' in geo1 and 'contour_analysis' in geo2:
            solidity1 = geo1['contour_analysis'].get('solidity', 0)
            solidity2 = geo2['contour_analysis'].get('solidity', 0)
            
            solidity_diff = abs(solidity1 - solidity2)
            solidity_similarity = max(0, 1 - solidity_diff)
            similarities.append(solidity_similarity)
        
        return np.mean(similarities) if similarities else 0.0
    
    def _calculate_feature_similarity(self, features1: Dict, features2: Dict) -> float:
        """Calculate feature descriptor similarity."""
        if not features1 or not features2:
            return 0.0
        
        similarities = []
        
        # Compare SIFT features
        if 'sift' in features1 and 'sift' in features2:
            mean1 = np.array(features1['sift']['descriptor_mean'])
            mean2 = np.array(features2['sift']['descriptor_mean'])
            
            # Calculate cosine similarity
            if HAS_ADVANCED:
                similarity = cosine_similarity([mean1], [mean2])[0, 0]
            else:
                # Manual cosine similarity
                dot_product = np.dot(mean1, mean2)
                norm1 = np.linalg.norm(mean1)
                norm2 = np.linalg.norm(mean2)
                similarity = dot_product / (norm1 * norm2) if norm1 > 0 and norm2 > 0 else 0
            
            similarities.append(max(0, similarity))
        
        # Compare ORB features
        if 'orb' in features1 and 'orb' in features2:
            count1 = features1['orb']['keypoint_count']
            count2 = features2['orb']['keypoint_count']
            
            # Simple count-based similarity
            max_count = max(count1, count2, 1)
            count_similarity = min(count1, count2) / max_count
            similarities.append(count_similarity)
        
        return np.mean(similarities) if similarities else 0.0