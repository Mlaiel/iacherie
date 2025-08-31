"""Image Optimization Pipeline - Content Performance Enhancement
Advanced image processing and optimization for web delivery

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""

import io

import hashlib
from typing import Dict, Any, Optional, List, Tuple, Union
from PIL import Image, ImageOps, ImageFilter
from PIL.ExifTags import TAGS

import base64
import logging

logger = logging.getLogger(__name__)


class ImageOptimizer:
    """
    Comprehensive image optimization pipeline
    
    Features:
    - Multiple output formats (WebP, AVIF, JPEG, PNG)
    - Responsive image generation
    - Quality optimization
    - Lossless compression
    - Metadata stripping
    - Progressive JPEG support
    """
    
    def __init__(self):
        self.supported_formats = ['JPEG', 'PNG', 'WebP', 'AVIF', 'GIF']
        self.quality_settings = {
            'high': 90,
            'medium': 75,
            'low': 60,
            'webp_high': 85,
            'webp_medium': 70,
            'webp_low': 50
        }
        
        # Standard responsive breakpoints
        self.responsive_sizes = [
            {'name': 'thumbnail', 'width': 150, 'height': 150},
            {'name': 'small', 'width': 320, 'height': None},
            {'name': 'medium', 'width': 640, 'height': None},
            {'name': 'large', 'width': 1024, 'height': None},
            {'name': 'xl', 'width': 1920, 'height': None}
        ]
        
        logger.info("Image Optimizer initialized")
    
    def optimize_image(
        self,
        image_data: Union[bytes, str],
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Optimize image with multiple format outputs
        
        Args:
            image_data: Raw image bytes or base64 string
            options: Optimization options
            
        Returns:
            Dictionary with optimized image variants
        """
        
        # Default options
        default_options = {
            'quality': 'medium',
            'generate_webp': True,
            'generate_avif': False,
            'generate_responsive': True,
            'strip_metadata': True,
            'progressive': True,
            'optimize': True
        }
        
        if options:
            default_options.update(options)
        
        try:
            # Load image
            if isinstance(image_data, str):
                # Assume base64 encoded
                image_data = base64.b64decode(image_data)
            
            image = Image.open(io.BytesIO(image_data))
            
            # Get original image info
            original_info = self._get_image_info(image)
            
            # Generate optimized variants
            variants = {}
            
            # Original format optimization
            variants['original'] = self._optimize_original_format(image, default_options)
            
            # WebP optimization
            if default_options['generate_webp']:
                variants['webp'] = self._generate_webp_variants(image, default_options)
            
            # AVIF optimization (if supported)
            if default_options['generate_avif']:
                variants['avif'] = self._generate_avif_variants(image, default_options)
            
            # Responsive variants
            if default_options['generate_responsive']:
                variants['responsive'] = self._generate_responsive_variants(image, default_options)
            
            return {
                'success': True,
                'original_info': original_info,
                'variants': variants,
                'optimization_stats': self._calculate_optimization_stats(image_data, variants)
            }
            
        except Exception as e:
            logger.error(f"Image optimization failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_image_info(self, image: Image.Image) -> Dict[str, Any]:
        """Extract image information"""
        
        info = {
            'format': image.format,
            'mode': image.mode,
            'size': image.size,
            'width': image.width,
            'height': image.height,
            'has_transparency': image.mode in ('RGBA', 'LA') or 'transparency' in image.info
        }
        
        # Get file size estimate
        with io.BytesIO() as buffer:
            image.save(buffer, format=image.format or 'JPEG')
            info['estimated_size'] = len(buffer.getvalue())
        
        # Extract EXIF data if available
        if hasattr(image, '_getexif') and image._getexif():
            exif_data = {}
            for tag, value in image._getexif().items():
                tag_name = TAGS.get(tag, tag)
                exif_data[tag_name] = value
            info['exif'] = exif_data
        
        return info
    
    def _optimize_original_format(self, image: Image.Image, options: Dict[str, Any]) -> Dict[str, Any]:
        """
Optimize image in its original format"""
        
        try:
            # Create copy for optimization
            optimized_image = image.copy()
            
            # Strip metadata if requested
            if options['strip_metadata']:
                optimized_image = self._strip_metadata(optimized_image)
            
            # Convert to RGB if necessary for JPEG
            if image.format == 'JPEG' and optimized_image.mode != 'RGB':
                optimized_image = optimized_image.convert('RGB')
            
            # Save optimized version
            with io.BytesIO() as buffer:
                save_kwargs = {
                    'format': image.format or 'JPEG',
                    'optimize': options['optimize']
                }
                
                # Quality settings
                if image.format in ['JPEG', 'WebP']:
                    save_kwargs['quality'] = self.quality_settings[options['quality']]
                
                # Progressive JPEG
                if image.format == 'JPEG' and options['progressive']:
                    save_kwargs['progressive'] = True
                
                optimized_image.save(buffer, **save_kwargs)
                optimized_data = buffer.getvalue()
            
            return {
                'format': image.format or 'JPEG',
                'size': len(optimized_data),
                'data': base64.b64encode(optimized_data).decode('utf-8'),
                'dimensions': optimized_image.size
            }
            
        except Exception as e:
            logger.error(f"Original format optimization failed: {e}")
            return None
    
    def _generate_webp_variants(self, image: Image.Image, options: Dict[str, Any]) -> Dict[str, Any]:
        """Generate WebP variants"""
        
        try:
            variants = {}
            
            # High quality WebP
            variants['high'] = self._save_webp(image, 'webp_high', options)
            
            # Medium quality WebP
            variants['medium'] = self._save_webp(image, 'webp_medium', options)
            
            # Low quality WebP (for fast loading)
            variants['low'] = self._save_webp(image, 'webp_low', options)
            
            return variants
            
        except Exception as e:
            logger.error(f"WebP generation failed: {e}")
            return None
    
    def _generate_avif_variants(self, image: Image.Image, options: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AVIF variants (if supported)"""
        
        try:
            # AVIF support may not be available in all PIL installations
            # This is a placeholder for AVIF optimization
            logger.info("AVIF generation requested but not implemented")
            return None
            
        except Exception as e:
            logger.error(f"AVIF generation failed: {e}")
            return None
    
    def _generate_responsive_variants(self, image: Image.Image, options: Dict[str, Any]) -> Dict[str, Any]:
        """Generate responsive image variants"""
        
        try:
            variants = {}
            
            for size_config in self.responsive_sizes:
                resized_image = self._resize_image(image, size_config)
                
                if resized_image:
                    # Save in original format
                    original_variant = self._save_resized_image(resized_image, image.format, options)
                    
                    # Save in WebP if enabled
                    webp_variant = None
                    if options['generate_webp']:
                        webp_variant = self._save_webp(resized_image, 'webp_medium', options)
                    
                    variants[size_config['name']] = {
                        'dimensions': resized_image.size,
                        'original': original_variant,
                        'webp': webp_variant
                    }
            
            return variants
            
        except Exception as e:
            logger.error(f"Responsive variants generation failed: {e}")
            return None
    
    def _resize_image(self, image: Image.Image, size_config: Dict[str, Any]) -> Optional[Image.Image]:
        """Resize image according to size configuration"""
        
        try:
            target_width = size_config['width']
            target_height = size_config.get('height')
            
            # Calculate dimensions
            if target_height is None:
                # Maintain aspect ratio
                ratio = target_width / image.width
                target_height = int(image.height * ratio)
            
            # Don't upscale images
            if target_width > image.width and target_height > image.height:
                return image.copy()
            
            # Resize with high quality resampling
            resized = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
            
            return resized
            
        except Exception as e:
            logger.error(f"Image resize failed: {e}")
            return None
    
    def _save_webp(self, image: Image.Image, quality_key: str, options: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Save image as WebP"""
        
        try:
            # Convert to RGB if necessary
            if image.mode == 'P':
                image = image.convert('RGBA')
            
            with io.BytesIO() as buffer:
                save_kwargs = {
                    'format': 'WebP',
                    'quality': self.quality_settings[quality_key],
                    'optimize': options['optimize']
                }
                
                # Enable lossless for PNG-like images with transparency
                if image.mode in ('RGBA', 'LA') and options.get('lossless_transparent', False):
                    save_kwargs['lossless'] = True
                
                image.save(buffer, **save_kwargs)
                webp_data = buffer.getvalue()
            
            return {
                'format': 'WebP',
                'size': len(webp_data),
                'data': base64.b64encode(webp_data).decode('utf-8'),
                'dimensions': image.size
            }
            
        except Exception as e:
            logger.error(f"WebP save failed: {e}")
            return None
    
    def _save_resized_image(self, image: Image.Image, original_format: str, options: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Save resized image in original format"""
        
        try:
            # Strip metadata if requested
            if options['strip_metadata']:
                image = self._strip_metadata(image)
            
            with io.BytesIO() as buffer:
                save_kwargs = {
                    'format': original_format or 'JPEG',
                    'optimize': options['optimize']
                }
                
                # Quality settings
                if original_format in ['JPEG', 'WebP']:
                    save_kwargs['quality'] = self.quality_settings[options['quality']]
                
                # Progressive JPEG
                if original_format == 'JPEG' and options['progressive']:
                    save_kwargs['progressive'] = True
                
                image.save(buffer, **save_kwargs)
                image_data = buffer.getvalue()
            
            return {
                'format': original_format or 'JPEG',
                'size': len(image_data),
                'data': base64.b64encode(image_data).decode('utf-8'),
                'dimensions': image.size
            }
            
        except Exception as e:
            logger.error(f"Resized image save failed: {e}")
            return None
    
    def _strip_metadata(self, image: Image.Image) -> Image.Image:
        """Strip metadata from image"""
        
        try:
            # Create new image without metadata
            stripped_image = Image.new(image.mode, image.size)
            stripped_image.putdata(list(image.getdata()))
            
            return stripped_image
            
        except Exception as e:
            logger.error(f"Metadata stripping failed: {e}")
            return image
    
    def _calculate_optimization_stats(self, original_data: bytes, variants: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate optimization statistics"""
        
        try:
            original_size = len(original_data)
            total_variants = 0
            total_optimized_size = 0
            
            def count_variant_size(variant_data):
                nonlocal total_variants, total_optimized_size
                if isinstance(variant_data, dict):
                    if 'size' in variant_data:
                        total_variants += 1
                        total_optimized_size += variant_data['size']
                    else:
                        for sub_variant in variant_data.values():
                            if sub_variant:
                                count_variant_size(sub_variant)
            
            # Count all variant sizes
            for variant_type, variant_data in variants.items():
                if variant_data:
                    count_variant_size(variant_data)
            
            # Calculate savings
            if original_size > 0 and total_optimized_size > 0:
                average_optimized_size = total_optimized_size / total_variants if total_variants > 0 else original_size
                savings_percentage = ((original_size - average_optimized_size) / original_size) * 100
            else:
                savings_percentage = 0
            
            return {
                'original_size': original_size,
                'total_variants': total_variants,
                'average_optimized_size': int(average_optimized_size) if 'average_optimized_size' in locals() else 0,
                'savings_percentage': round(savings_percentage, 2),
                'total_optimized_size': total_optimized_size
            }
            
        except Exception as e:
            logger.error(f"Stats calculation failed: {e}")
            return {'error': str(e)}


class BatchImageOptimizer:
    """
    Batch processing for multiple images
    """
    
    def __init__(self):
        self.optimizer = ImageOptimizer()
        self.processed_count = 0
        self.failed_count = 0
        
    def optimize_batch(self, images: List[Dict[str, Any]], options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Optimize multiple images in batch
        
        Args:
            images: List of image data dictionaries
            options: Optimization options
            
        Returns:
            Batch optimization results
        """
        
        results = []
        self.processed_count = 0
        self.failed_count = 0
        
        for i, image_info in enumerate(images):
            try:
                image_data = image_info.get('data')
                image_options = image_info.get('options', options)
                
                result = self.optimizer.optimize_image(image_data, image_options)
                
                if result['success']:
                    self.processed_count += 1
                else:
                    self.failed_count += 1
                
                results.append({
                    'index': i,
                    'id': image_info.get('id', f'image_{i}'),
                    'result': result
                })
                
            except Exception as e:
                self.failed_count += 1
                results.append({
                    'index': i,
                    'id': image_info.get('id', f'image_{i}'),
                    'result': {
                        'success': False,
                        'error': str(e)
                    }
                })
        
        return {
            'total_images': len(images),
            'processed_successfully': self.processed_count,
            'failed': self.failed_count,
            'results': results
        }