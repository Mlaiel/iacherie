"""Image Agent Utilities - Professional Utility Functions & Helpers

Comprehensive utility functions, helpers, and tools for the Image Agent module
providing common operations, validations, and data processing capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""import hashlib
import logging
import mimetypes
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple, Set
import json
import base64
from io import BytesIO

import numpy as np
from PIL import Image, ExifTags
import cv2
import imagehash
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

logger = logging.getLogger(__name__)


class ImageMetrics:
    """Image quality and analysis metrics calculator"""    
    @staticmethod
    def calculate_sharpness(image: np.ndarray) -> float:
        """Calculate image sharpness using Laplacian variance"""        try:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) if len(image.shape) == 3 else image
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            return float(laplacian_var)
        except Exception as e:
            logger.error(f"Error calculating sharpness: {e}")
            return 0.0
    
    @staticmethod
    def calculate_contrast(image: np.ndarray) -> float:
        """Calculate image contrast using RMS contrast"""        try:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) if len(image.shape) == 3 else image
            return float(gray.std())
        except Exception as e:
            logger.error(f"Error calculating contrast: {e}")
            return 0.0
    
    @staticmethod
    def calculate_brightness(image: np.ndarray) -> float:
        """Calculate image brightness"""        try:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) if len(image.shape) == 3 else image
            return float(gray.mean())
        except Exception as e:
            logger.error(f"Error calculating brightness: {e}")
            return 0.0
    
    @staticmethod
    def calculate_color_diversity(image: np.ndarray) -> float:
        """Calculate color diversity using histogram analysis"""        try:
            if len(image.shape) != 3:
                return 0.0
            
            # Calculate histogram for each channel
            histograms = []
            for i in range(3):
                hist = cv2.calcHist([image], [i], None, [256], [0, 256])
                histograms.append(hist.flatten())
            
            # Calculate entropy as diversity measure
            total_pixels = image.shape[0] * image.shape[1]
            diversity = 0.0
            
            for hist in histograms:
                probabilities = hist / total_pixels
                probabilities = probabilities[probabilities > 0]
                entropy = -np.sum(probabilities * np.log2(probabilities))
                diversity += entropy
            
            return float(diversity / 3)  # Average across channels
            
        except Exception as e:
            logger.error(f"Error calculating color diversity: {e}")
            return 0.0
    
    @staticmethod
    def detect_blur(image: np.ndarray, threshold: float = 100.0) -> bool:
        """Detect if image is blurry using Laplacian method"""        try:
            sharpness = ImageMetrics.calculate_sharpness(image)
            return sharpness < threshold
        except Exception as e:
            logger.error(f"Error detecting blur: {e}")
            return False
    
    @staticmethod
    def calculate_noise_level(image: np.ndarray) -> float:
        """Estimate noise level in image"""        try:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) if len(image.shape) == 3 else image
            
            # Use median filter to estimate noise
            filtered = cv2.medianBlur(gray, 5)
            noise = cv2.absdiff(gray, filtered)
            
            return float(noise.mean())
            
        except Exception as e:
            logger.error(f"Error calculating noise level: {e}")
            return 0.0


class ImageHashGenerator:
    """Advanced image hashing for fingerprinting and similarity detection"""    
    @staticmethod
    def generate_perceptual_hash(image_path: str) -> str:
        """Generate perceptual hash using pHash algorithm"""        try:
            with Image.open(image_path) as img:
                phash = imagehash.phash(img)
                return str(phash)
        except Exception as e:
            logger.error(f"Error generating perceptual hash: {e}")
            return ""
    
    @staticmethod
    def generate_difference_hash(image_path: str) -> str:
        """Generate difference hash (dHash)"""        try:
            with Image.open(image_path) as img:
                dhash = imagehash.dhash(img)
                return str(dhash)
        except Exception as e:
            logger.error(f"Error generating difference hash: {e}")
            return ""
    
    @staticmethod
    def generate_average_hash(image_path: str) -> str:
        """Generate average hash (aHash)"""        try:
            with Image.open(image_path) as img:
                ahash = imagehash.average_hash(img)
                return str(ahash)
        except Exception as e:
            logger.error(f"Error generating average hash: {e}")
            return ""
    
    @staticmethod
    def generate_wavelet_hash(image_path: str) -> str:
        """Generate wavelet hash"""        try:
            with Image.open(image_path) as img:
                whash = imagehash.whash(img)
                return str(whash)
        except Exception as e:
            logger.error(f"Error generating wavelet hash: {e}")
            return ""
    
    @staticmethod
    def generate_comprehensive_fingerprint(image_path: str) -> Dict[str, str]:
        """Generate comprehensive image fingerprint with multiple hashes"""        return {
            "perceptual_hash": ImageHashGenerator.generate_perceptual_hash(image_path),
            "difference_hash": ImageHashGenerator.generate_difference_hash(image_path),
            "average_hash": ImageHashGenerator.generate_average_hash(image_path),
            "wavelet_hash": ImageHashGenerator.generate_wavelet_hash(image_path),
            "file_hash": FileUtils.calculate_file_hash(image_path),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    @staticmethod
    def calculate_similarity(hash1: str, hash2: str) -> float:
        """Calculate similarity between two hashes (0.0 = identical, 1.0 = completely different)"""        try:
            if not hash1 or not hash2:
                return 1.0
            
            # Convert hex strings to binary
            bin1 = bin(int(hash1, 16))[2:].zfill(len(hash1) * 4)
            bin2 = bin(int(hash2, 16))[2:].zfill(len(hash2) * 4)
            
            # Calculate Hamming distance
            hamming_distance = sum(b1 != b2 for b1, b2 in zip(bin1, bin2))
            
            # Convert to similarity ratio
            similarity = hamming_distance / len(bin1)
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating hash similarity: {e}")
            return 1.0


class FileUtils:
    """File handling and validation utilities"""    
    SUPPORTED_IMAGE_FORMATS = {
        '.jpg', '.jpeg', '.png', '.webp', '.avif', '.heic', '.heif',
        '.tiff', '.tif', '.bmp', '.gif', '.svg', '.raw', '.ico'
    }
    
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    
    @staticmethod
    def validate_image_file(file_path: str) -> Dict[str, Any]:
        """Comprehensive image file validation"""        result = {
            "valid": False,
            "errors": [],
            "warnings": [],
            "file_info": {}
        }
        
        try:
            path = Path(file_path)
            
            # Check file existence
            if not path.exists():
                result["errors"].append("File does not exist")
                return result
            
            # Check file extension
            if path.suffix.lower() not in FileUtils.SUPPORTED_IMAGE_FORMATS:
                result["errors"].append(f"Unsupported file format: {path.suffix}")
            
            # Check file size
            file_size = path.stat().st_size
            if file_size > FileUtils.MAX_FILE_SIZE:
                result["errors"].append(f"File too large: {file_size / (1024*1024):.1f}MB > 100MB")
            elif file_size == 0:
                result["errors"].append("File is empty")
            
            # Try to open and validate image
            try:
                with Image.open(file_path) as img:
                    result["file_info"] = {
                        "format": img.format,
                        "mode": img.mode,
                        "size": img.size,
                        "has_transparency": img.mode in ('RGBA', 'LA', 'P'),
                        "file_size": file_size,
                        "mime_type": mimetypes.guess_type(file_path)[0]
                    }
                    
                    # Check image dimensions
                    width, height = img.size
                    if width * height > 8192 * 8192:
                        result["warnings"].append("Very large image dimensions may affect processing speed")
                    elif width < 100 or height < 100:
                        result["warnings"].append("Small image dimensions may limit enhancement quality")
                    
                    # Check for EXIF data
                    if hasattr(img, '_getexif') and img._getexif():
                        result["file_info"]["has_exif"] = True
                    else:
                        result["file_info"]["has_exif"] = False
                        
            except Exception as e:
                result["errors"].append(f"Invalid image file: {str(e)}")
            
            # Set valid status
            result["valid"] = len(result["errors"]) == 0
            
        except Exception as e:
            result["errors"].append(f"Validation failed: {str(e)}")
        
        return result
    
    @staticmethod
    def calculate_file_hash(file_path: str, algorithm: str = "sha256") -> str:
        """Calculate file hash"""        try:
            hash_func = hashlib.new(algorithm)
            
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hash_func.update(chunk)
            
            return hash_func.hexdigest()
            
        except Exception as e:
            logger.error(f"Error calculating file hash: {e}")
            return ""
    
    @staticmethod
    def get_image_metadata(file_path: str) -> Dict[str, Any]:
        """Extract comprehensive image metadata"""        metadata = {
            "basic_info": {},
            "exif_data": {},
            "technical_info": {},
            "extracted_at": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            with Image.open(file_path) as img:
                # Basic information
                metadata["basic_info"] = {
                    "filename": Path(file_path).name,
                    "format": img.format,
                    "mode": img.mode,
                    "size": img.size,
                    "width": img.width,
                    "height": img.height,
                    "has_transparency": img.mode in ('RGBA', 'LA', 'P'),
                    "file_size": Path(file_path).stat().st_size
                }
                
                # EXIF data
                if hasattr(img, '_getexif') and img._getexif():
                    exif_data = img._getexif()
                    if exif_data:
                        for tag_id, value in exif_data.items():
                            tag_name = ExifTags.TAGS.get(tag_id, tag_id)
                            metadata["exif_data"][tag_name] = str(value)
                
                # Technical analysis
                img_array = np.array(img.convert('RGB'))
                metadata["technical_info"] = {
                    "sharpness": ImageMetrics.calculate_sharpness(img_array),
                    "contrast": ImageMetrics.calculate_contrast(img_array),
                    "brightness": ImageMetrics.calculate_brightness(img_array),
                    "color_diversity": ImageMetrics.calculate_color_diversity(img_array),
                    "noise_level": ImageMetrics.calculate_noise_level(img_array),
                    "is_blurry": ImageMetrics.detect_blur(img_array)
                }
                
        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
            metadata["error"] = str(e)
        
        return metadata
    
    @staticmethod
    def create_secure_filename(original_filename: str) -> str:
        """Create secure filename with UUID prefix"""        path = Path(original_filename)
        safe_name = "".join(c for c in path.stem if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_name = safe_name[:50]  # Limit length
        
        unique_id = str(uuid.uuid4())[:8]
        timestamp = int(time.time())
        
        return f"{unique_id}_{timestamp}_{safe_name}{path.suffix.lower()}"


class SEOUtils:
    """SEO optimization utilities for images"""    
    @staticmethod
    def generate_alt_text(image_path: str, context: str = "") -> str:
        """Generate SEO-optimized alt text for images"""        try:
            metadata = FileUtils.get_image_metadata(image_path)
            
            # Extract basic characteristics
            width = metadata["basic_info"].get("width", 0)
            height = metadata["basic_info"].get("height", 0)
            
            # Analyze technical qualities
            tech_info = metadata.get("technical_info", {})
            brightness = tech_info.get("brightness", 0)
            contrast = tech_info.get("contrast", 0)
            
            # Generate descriptive terms
            descriptors = []
            
            # Orientation
            if width > height * 1.3:
                descriptors.append("landscape")
            elif height > width * 1.3:
                descriptors.append("portrait")
            else:
                descriptors.append("square")
            
            # Quality indicators
            if brightness > 150:
                descriptors.append("bright")
            elif brightness < 100:
                descriptors.append("dark")
            
            if contrast > 60:
                descriptors.append("high-contrast")
            
            # Size category
            if width >= 1920 or height >= 1080:
                descriptors.append("high-resolution")
            
            # Combine with context
            alt_parts = []
            if context:
                alt_parts.append(context)
            
            alt_parts.extend(descriptors)
            alt_parts.append("image")
            
            return " ".join(alt_parts).strip()
            
        except Exception as e:
            logger.error(f"Error generating alt text: {e}")
            return f"Image - {Path(image_path).stem}"
    
    @staticmethod
    def generate_seo_metadata(image_path: str, keywords: List[str] = None) -> Dict[str, str]:
        """Generate comprehensive SEO metadata"""        try:
            metadata = FileUtils.get_image_metadata(image_path)
            filename = Path(image_path).stem
            
            # Generate title
            title_parts = []
            if keywords:
                title_parts.extend(keywords[:3])  # Use first 3 keywords
            title_parts.append(filename.replace("_", " ").replace("-", " ").title())
            title = " - ".join(title_parts)
            
            # Generate description
            alt_text = SEOUtils.generate_alt_text(image_path)
            size_info = f"{metadata['basic_info']['width']}x{metadata['basic_info']['height']}"
            description = f"{alt_text} ({size_info})"
            
            # Generate keywords
            auto_keywords = [
                metadata["basic_info"]["format"].lower(),
                f"{metadata['basic_info']['width']}x{metadata['basic_info']['height']}",
                "digital image",
                "visual content"
            ]
            
            if keywords:
                auto_keywords.extend(keywords)
            
            return {
                "title": title,
                "description": description,
                "alt_text": alt_text,
                "keywords": ", ".join(set(auto_keywords)),
                "filename": FileUtils.create_secure_filename(Path(image_path).name),
                "size_info": size_info,
                "format": metadata["basic_info"]["format"]
            }
            
        except Exception as e:
            logger.error(f"Error generating SEO metadata: {e}")
            return {
                "title": Path(image_path).stem,
                "description": f"Image: {Path(image_path).name}",
                "alt_text": f"Image: {Path(image_path).stem}",
                "keywords": "image, visual, content",
                "filename": Path(image_path).name,
                "size_info": "unknown",
                "format": "unknown"
            }


class PerformanceTracker:
    """Performance tracking and monitoring utilities"""    
    def __init__(self):
        self.start_time = None
        self.metrics = {}
    
    def start_operation(self, operation_name: str):
        """Start tracking an operation"""        self.start_time = time.perf_counter()
        self.metrics[operation_name] = {
            "start_time": self.start_time,
            "operation": operation_name,
            "status": "running"
        }
    
    def end_operation(self, operation_name: str, success: bool = True, details: Dict[str, Any] = None):
        """End tracking an operation"""        end_time = time.perf_counter()
        
        if operation_name in self.metrics:
            self.metrics[operation_name].update({
                "end_time": end_time,
                "duration": end_time - self.metrics[operation_name]["start_time"],
                "status": "success" if success else "failed",
                "details": details or {}
            })
    
    def get_metrics(self, operation_name: str = None) -> Dict[str, Any]:
        """Get performance metrics"""        if operation_name:
            return self.metrics.get(operation_name, {})
        return self.metrics.copy()
    
    def clear_metrics(self):
        """Clear all metrics"""        self.metrics.clear()


class BatchProcessor:
    """Utilities for batch processing operations"""    
    @staticmethod
    def validate_batch_files(file_paths: List[str]) -> Dict[str, Any]:
        """Validate multiple files for batch processing"""        results = {
            "valid_files": [],
            "invalid_files": [],
            "total_size": 0,
            "warnings": []
        }
        
        for file_path in file_paths:
            validation = FileUtils.validate_image_file(file_path)
            
            if validation["valid"]:
                results["valid_files"].append(file_path)
                results["total_size"] += validation["file_info"].get("file_size", 0)
            else:
                results["invalid_files"].append({
                    "file_path": file_path,
                    "errors": validation["errors"]
                })
            
            results["warnings"].extend(validation["warnings"])
        
        # Check total batch size
        if results["total_size"] > 1024 * 1024 * 1024:  # 1GB
            results["warnings"].append("Large batch size may affect processing performance")
        
        return results
    
    @staticmethod
    def estimate_processing_time(file_count: int, operations: List[str]) -> Dict[str, float]:
        """Estimate processing time for batch operations"""        # Base processing times (in seconds per file)
        operation_times = {
            "analyze": 2.0,
            "enhance": 15.0,
            "generate": 30.0,
            "convert": 3.0,
            "protect": 1.0,
            "optimize": 5.0
        }
        
        total_time = 0
        operation_breakdown = {}
        
        for operation in operations:
            op_time = operation_times.get(operation, 5.0) * file_count
            operation_breakdown[operation] = op_time
            total_time += op_time
        
        return {
            "total_estimated_seconds": total_time,
            "total_estimated_minutes": total_time / 60,
            "operation_breakdown": operation_breakdown,
            "files_processed": file_count
        }
