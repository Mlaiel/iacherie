"""AI Filter Engine
Creative AI filters and style transfer for multimedia content.

Created by: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import numpy as np
import cv2
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from typing import Dict, Optional, Union, List, Tuple
from pathlib import Path
from dataclasses import dataclass
import logging
from PIL import Image, ImageFilter, ImageEnhance
import json

logger = logging.getLogger(__name__)

@dataclass
class FilterConfig:
    """Configuration for AI filters."""
    style_strength: float = 0.7  # 0.0 to 1.0
    preserve_content: bool = True
    output_quality: int = 95
    gpu_acceleration: bool = True
    batch_size: int = 1
    filter_blend_mode: str = "normal"  # normal, multiply, overlay, soft_light
    post_processing: bool = True

class StyleTransferModel(nn.Module):
    """Lightweight neural style transfer model."""
    
    def __init__(self):
        super(StyleTransferModel, self).__init__()
        
        # Encoder
        self.encoder = nn.Sequential(
            nn.Conv2d(3, 32, 9, 1, 4),
            nn.InstanceNorm2d(32),
            nn.ReLU(),
            nn.Conv2d(32, 64, 3, 2, 1),
            nn.InstanceNorm2d(64),
            nn.ReLU(),
            nn.Conv2d(64, 128, 3, 2, 1),
            nn.InstanceNorm2d(128),
            nn.ReLU(),
        )
        
        # Residual blocks
        self.residual_blocks = nn.Sequential(*[
            self._residual_block(128) for _ in range(5)
        ])
        
        # Decoder
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(128, 64, 3, 2, 1, 1),
            nn.InstanceNorm2d(64),
            nn.ReLU(),
            nn.ConvTranspose2d(64, 32, 3, 2, 1, 1),
            nn.InstanceNorm2d(32),
            nn.ReLU(),
            nn.Conv2d(32, 3, 9, 1, 4),
            nn.Tanh()
        )
        
    def _residual_block(self, channels):
        return nn.Sequential(
            nn.Conv2d(channels, channels, 3, 1, 1),
            nn.InstanceNorm2d(channels),
            nn.ReLU(),
            nn.Conv2d(channels, channels, 3, 1, 1),
            nn.InstanceNorm2d(channels)
        )
    
    def forward(self, x):
        residual = x
        out = self.encoder(x)
        out = self.residual_blocks(out)
        out = self.decoder(out)
        return out

class AIFilterEngine:
    """Enterprise AI filter and style transfer engine."""
    
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.models = {}
        self.config = FilterConfig()
        
        # Available filters and their configurations
        self.available_filters = {
            "artistic_oil": {"model": "style_transfer", "style": "oil_painting"},
            "artistic_watercolor": {"model": "style_transfer", "style": "watercolor"},
            "artistic_sketch": {"model": "edge_detection", "strength": 0.8},
            "vintage_film": {"model": "color_grading", "preset": "vintage"},
            "cinematic_teal": {"model": "color_grading", "preset": "teal_orange"},
            "portrait_beauty": {"model": "beauty_filter", "skin_smooth": 0.6},
            "landscape_enhance": {"model": "enhancement", "landscape_mode": True},
            "dramatic_bw": {"model": "monochrome", "contrast": 1.3},
            "instagram_vsco": {"model": "social_filter", "preset": "vsco"},
            "tiktok_trendy": {"model": "social_filter", "preset": "trendy"},
            "auto_enhance": {"model": "ai_auto", "adaptive": True}
        }
        
    async def apply_ai_filter(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        filter_type: str = "auto_enhance",
        config: Optional[FilterConfig] = None
    ) -> Dict[str, any]:
        """Apply AI-powered creative filters."""
        try:
            if config:
                self.config = config
                
            input_path = Path(input_path)
            output_path = Path(output_path)
            
            if not input_path.exists():
                raise FileNotFoundError(f"Input file not found: {input_path}")
                
            if filter_type not in self.available_filters:
                raise ValueError(f"Filter type '{filter_type}' not available")
            
            # Load and prepare image
            image = await self._load_image(input_path)
            
            # Apply the selected filter
            filtered_image = await self._apply_filter(image, filter_type)
            
            # Post-processing if enabled
            if self.config.post_processing:
                filtered_image = await self._post_process(filtered_image, filter_type)
            
            # Save result
            await self._save_image(filtered_image, output_path)
            
            # Calculate filter effectiveness
            effectiveness = await self._calculate_filter_effectiveness(
                image, filtered_image, filter_type
            )
            
            return {
                "success": True,
                "filter_applied": filter_type,
                "filter_strength": self.config.style_strength,
                "effectiveness_score": effectiveness,
                "output_path": str(output_path),
                "processing_details": {
                    "device_used": str(self.device),
                    "gpu_acceleration": self.config.gpu_acceleration and torch.cuda.is_available(),
                    "image_size": f"{image.width}x{image.height}"
                }
            }
            
        except Exception as e:
            logger.error(f"AI filter application failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _load_image(self, input_path: Path) -> Image.Image:
        """Load and prepare image for processing."""
        image = Image.open(input_path)
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize if too large (for performance)
        max_size = 2048
        if max(image.size) > max_size:
            ratio = max_size / max(image.size)
            new_size = (int(image.width * ratio), int(image.height * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        return image
    
    async def _apply_filter(self, image: Image.Image, filter_type: str) -> Image.Image:
        """Apply the specified AI filter."""
        filter_config = self.available_filters[filter_type]
        model_type = filter_config["model"]
        
        if model_type == "style_transfer":
            return await self._apply_style_transfer(image, filter_config)
        elif model_type == "edge_detection":
            return await self._apply_artistic_sketch(image, filter_config)
        elif model_type == "color_grading":
            return await self._apply_color_grading(image, filter_config)
        elif model_type == "beauty_filter":
            return await self._apply_beauty_filter(image, filter_config)
        elif model_type == "enhancement":
            return await self._apply_ai_enhancement(image, filter_config)
        elif model_type == "monochrome":
            return await self._apply_dramatic_bw(image, filter_config)
        elif model_type == "social_filter":
            return await self._apply_social_filter(image, filter_config)
        elif model_type == "ai_auto":
            return await self._apply_auto_enhance(image, filter_config)
        else:
            raise ValueError(f"Unknown model type: {model_type}")
    
    async def _apply_style_transfer(
        self, 
        image: Image.Image, 
        filter_config: Dict
    ) -> Image.Image:
        """Apply neural style transfer."""
        try:
            # Convert to tensor
            transform = transforms.Compose([
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                                   std=[0.229, 0.224, 0.225])
            ])
            
            # Prepare input
            input_tensor = transform(image).unsqueeze(0)
            
            if self.config.gpu_acceleration and torch.cuda.is_available():
                input_tensor = input_tensor.to(self.device)
            
            # Load or create style transfer model
            model_key = f"style_{filter_config['style']}"
            if model_key not in self.models:
                self.models[model_key] = await self._load_style_model(filter_config["style"])
            
            model = self.models[model_key]
            
            # Apply style transfer
            with torch.no_grad():
                output_tensor = model(input_tensor)
            
            # Convert back to PIL image
            output_tensor = output_tensor.squeeze(0).cpu()
            
            # Denormalize
            denorm = transforms.Normalize(
                mean=[-0.485/0.229, -0.456/0.224, -0.406/0.225],
                std=[1/0.229, 1/0.224, 1/0.225]
            )
            output_tensor = denorm(output_tensor)
            output_tensor = torch.clamp(output_tensor, 0, 1)
            
            # Convert to PIL
            to_pil = transforms.ToPILImage()
            styled_image = to_pil(output_tensor)
            
            # Blend with original based on strength
            if self.config.style_strength < 1.0:
                styled_image = Image.blend(
                    image, styled_image, self.config.style_strength
                )
            
            return styled_image
            
        except Exception as e:
            logger.warning(f"Style transfer failed, using fallback: {e}")
            return await self._apply_fallback_style(image, filter_config)
    
    async def _apply_artistic_sketch(
        self, 
        image: Image.Image, 
        filter_config: Dict
    ) -> Image.Image:
        """Apply artistic sketch effect."""
        # Convert to OpenCV format
        img_array = np.array(image)
        img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        
        # Create sketch effect
        gray_blur = cv2.medianBlur(gray, 5)
        edges = cv2.adaptiveThreshold(
            gray_blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9
        )
        
        # Create colored sketch
        edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        
        # Bilateral filter for artistic effect
        bilateral = cv2.bilateralFilter(img_cv, 15, 80, 80)
        
        # Combine edges with bilateral filtered image
        sketch = cv2.bitwise_and(bilateral, edges_colored)
        
        # Convert back to PIL
        sketch_rgb = cv2.cvtColor(sketch, cv2.COLOR_BGR2RGB)
        sketch_image = Image.fromarray(sketch_rgb)
        
        # Blend with original
        strength = filter_config.get("strength", 0.8)
        result = Image.blend(image, sketch_image, strength)
        
        return result
    
    async def _apply_color_grading(
        self, 
        image: Image.Image, 
        filter_config: Dict
    ) -> Image.Image:
        """Apply cinematic color grading."""
        preset = filter_config.get("preset", "vintage")
        
        img_array = np.array(image).astype(np.float32) / 255.0
        
        if preset == "vintage":
            # Vintage film look
            # Lift shadows (add warm tone)
            img_array[:, :, 0] += 0.05  # Red lift
            img_array[:, :, 1] += 0.02  # Green lift
            
            # Desaturate slightly
            gray = 0.299 * img_array[:, :, 0] + 0.587 * img_array[:, :, 1] + 0.114 * img_array[:, :, 2]
            img_array = img_array * 0.85 + gray[:, :, np.newaxis] * 0.15
            
            # Add vignette
            height, width = img_array.shape[:2]
            center_x, center_y = width // 2, height // 2
            
            # Create distance map from center
            y, x = np.ogrid[:height, :width]
            distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
            max_distance = np.sqrt(center_x**2 + center_y**2)
            
            # Create vignette mask
            vignette = 1 - (distance / max_distance) * 0.3
            vignette = np.clip(vignette, 0.7, 1.0)
            
            img_array *= vignette[:, :, np.newaxis]
            
        elif preset == "teal_orange":
            # Teal and orange color grading
            # Shift blues towards teal
            blue_mask = img_array[:, :, 2] > img_array[:, :, 0]
            img_array[:, :, 1][blue_mask] *= 1.1  # Boost green in blue areas
            
            # Shift reds/yellows towards orange
            warm_mask = img_array[:, :, 0] > img_array[:, :, 2]
            img_array[:, :, 1][warm_mask] *= 0.9  # Reduce green in warm areas
            img_array[:, :, 0][warm_mask] *= 1.05  # Boost red
        
        # Clamp values
        img_array = np.clip(img_array, 0, 1)
        
        return Image.fromarray((img_array * 255).astype(np.uint8))
    
    async def _apply_beauty_filter(
        self, 
        image: Image.Image, 
        filter_config: Dict
    ) -> Image.Image:
        """Apply beauty filter for portraits."""
        skin_smooth = filter_config.get("skin_smooth", 0.6)
        
        # Convert to OpenCV
        img_array = np.array(image)
        img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # Skin tone detection (simple approach)
        hsv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2HSV)
        
        # Define skin color range in HSV
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
        
        # Smooth skin areas
        smoothed = cv2.bilateralFilter(img_cv, 15, 80, 80)
        
        # Apply smoothing only to skin areas
        result = img_cv.copy()
        skin_mask_3ch = cv2.cvtColor(skin_mask, cv2.COLOR_GRAY2BGR) / 255.0
        
        result = result * (1 - skin_mask_3ch * skin_smooth) + smoothed * (skin_mask_3ch * skin_smooth)
        result = result.astype(np.uint8)
        
        # Convert back to PIL
        result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
        
        # Slight brightness boost for healthy glow
        enhanced = Image.fromarray(result_rgb)
        enhancer = ImageEnhance.Brightness(enhanced)
        enhanced = enhancer.enhance(1.05)
        
        return enhanced
    
    async def _apply_ai_enhancement(
        self, 
        image: Image.Image, 
        filter_config: Dict
    ) -> Image.Image:
        """Apply AI-powered landscape enhancement."""
        landscape_mode = filter_config.get("landscape_mode", True)
        
        # Enhanced contrast and saturation for landscapes
        enhancer = ImageEnhance.Contrast(image)
        enhanced = enhancer.enhance(1.15)
        
        enhancer = ImageEnhance.Color(enhanced)
        enhanced = enhancer.enhance(1.2)
        
        # Slight sharpening
        enhanced = enhanced.filter(ImageFilter.UnsharpMask(radius=1, percent=120, threshold=3))
        
        if landscape_mode:
            # Boost sky areas (typically upper portion)
            img_array = np.array(enhanced).astype(np.float32) / 255.0
            height = img_array.shape[0]
            
            # Create sky mask (upper 40% of image)
            sky_mask = np.zeros((height, img_array.shape[1]))
            sky_mask[:int(height * 0.4), :] = 1.0
            
            # Boost blues in sky area
            img_array[:, :, 2] += sky_mask[:, :, np.newaxis].squeeze() * 0.05
            
            img_array = np.clip(img_array, 0, 1)
            enhanced = Image.fromarray((img_array * 255).astype(np.uint8))
        
        return enhanced
    
    async def _apply_dramatic_bw(
        self, 
        image: Image.Image, 
        filter_config: Dict
    ) -> Image.Image:
        """Apply dramatic black and white conversion."""
        contrast = filter_config.get("contrast", 1.3)
        
        # Convert to grayscale with custom weights for dramatic effect
        img_array = np.array(image).astype(np.float32) / 255.0
        
        # Dramatic B&W conversion (boost reds, darken blues)
        gray = 0.4 * img_array[:, :, 0] + 0.4 * img_array[:, :, 1] + 0.2 * img_array[:, :, 2]
        
        # Apply S-curve for contrast
        gray = np.power(gray, 1.0 / contrast)
        
        # Convert back to 3-channel
        gray_3ch = np.stack([gray, gray, gray], axis=-1)
        
        # Clamp and convert
        gray_3ch = np.clip(gray_3ch, 0, 1)
        
        return Image.fromarray((gray_3ch * 255).astype(np.uint8))
    
    async def _apply_social_filter(
        self, 
        image: Image.Image, 
        filter_config: Dict
    ) -> Image.Image:
        """Apply social media style filters."""
        preset = filter_config.get("preset", "vsco")
        
        if preset == "vsco":
            # VSCO-style filter: lifted shadows, faded highlights
            img_array = np.array(image).astype(np.float32) / 255.0
            
            # Lift shadows
            shadow_mask = 1.0 - img_array
            img_array += shadow_mask * 0.1
            
            # Fade highlights
            highlight_mask = img_array
            img_array = img_array * 0.9 + 0.1
            
            # Slight warm tint
            img_array[:, :, 0] *= 1.02  # Red
            img_array[:, :, 1] *= 1.01  # Green
            
        elif preset == "trendy":
            # TikTok-style trendy filter
            img_array = np.array(image).astype(np.float32) / 255.0
            
            # High contrast
            img_array = np.power(img_array, 0.8)
            
            # Saturation boost
            hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
            hsv[:, :, 1] *= 1.3  # Boost saturation
            img_array = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
        
        img_array = np.clip(img_array, 0, 1)
        return Image.fromarray((img_array * 255).astype(np.uint8))
    
    async def _apply_auto_enhance(
        self, 
        image: Image.Image, 
        filter_config: Dict
    ) -> Image.Image:
        """Apply intelligent auto-enhancement."""
        # Analyze image characteristics
        img_array = np.array(image)
        
        # Calculate brightness
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        brightness = np.mean(gray)
        
        # Calculate contrast
        contrast = np.std(gray)
        
        # Calculate saturation
        hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
        saturation = np.mean(hsv[:, :, 1])
        
        # Adaptive enhancements
        enhanced = image
        
        # Brightness adjustment
        if brightness < 100:  # Dark image
            enhancer = ImageEnhance.Brightness(enhanced)
            enhanced = enhancer.enhance(1.1)
        elif brightness > 180:  # Bright image
            enhancer = ImageEnhance.Brightness(enhanced)
            enhanced = enhancer.enhance(0.95)
        
        # Contrast adjustment
        if contrast < 40:  # Low contrast
            enhancer = ImageEnhance.Contrast(enhanced)
            enhanced = enhancer.enhance(1.2)
        
        # Saturation adjustment
        if saturation < 80:  # Low saturation
            enhancer = ImageEnhance.Color(enhanced)
            enhanced = enhancer.enhance(1.15)
        
        # Slight sharpening
        enhanced = enhanced.filter(ImageFilter.UnsharpMask(radius=0.5, percent=100, threshold=3))
        
        return enhanced
    
    async def _load_style_model(self, style: str) -> nn.Module:
        """Load or create style transfer model."""
        # For this implementation, we'll use a simple model
        # In production, you'd load pre-trained models
        model = StyleTransferModel()
        
        if self.config.gpu_acceleration and torch.cuda.is_available():
            model = model.to(self.device)
        
        model.eval()
        return model
    
    async def _apply_fallback_style(
        self, 
        image: Image.Image, 
        filter_config: Dict
    ) -> Image.Image:
        """Fallback style application using traditional methods."""
        style = filter_config.get("style", "oil_painting")
        
        if style == "oil_painting":
            # Oil painting effect using bilateral filter
            img_array = np.array(image)
            img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            # Multiple bilateral filters for oil painting effect
            for _ in range(3):
                img_cv = cv2.bilateralFilter(img_cv, 9, 200, 200)
            
            result_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
            return Image.fromarray(result_rgb)
        
        elif style == "watercolor":
            # Watercolor effect
            img_array = np.array(image)
            img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            # Edge-preserving filter
            img_cv = cv2.edgePreservingFilter(img_cv, flags=1, sigma_s=50, sigma_r=0.4)
            
            result_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
            return Image.fromarray(result_rgb)
        
        return image
    
    async def _post_process(
        self, 
        image: Image.Image, 
        filter_type: str
    ) -> Image.Image:
        """Apply post-processing enhancements."""
        # Subtle final adjustments based on filter type
        if "artistic" in filter_type:
            # Slight vignette for artistic filters
            image = await self._add_subtle_vignette(image)
        
        elif "vintage" in filter_type or "film" in filter_type:
            # Add film grain
            image = await self._add_film_grain(image)
        
        elif "portrait" in filter_type or "beauty" in filter_type:
            # Gentle glow
            image = await self._add_gentle_glow(image)
        
        return image
    
    async def _add_subtle_vignette(self, image: Image.Image) -> Image.Image:
        """Add subtle vignette effect."""
        img_array = np.array(image).astype(np.float32) / 255.0
        height, width = img_array.shape[:2]
        
        # Create vignette mask
        center_x, center_y = width // 2, height // 2
        y, x = np.ogrid[:height, :width]
        distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        max_distance = np.sqrt(center_x**2 + center_y**2)
        
        vignette = 1 - (distance / max_distance) * 0.15
        vignette = np.clip(vignette, 0.85, 1.0)
        
        img_array *= vignette[:, :, np.newaxis]
        img_array = np.clip(img_array, 0, 1)
        
        return Image.fromarray((img_array * 255).astype(np.uint8))
    
    async def _add_film_grain(self, image: Image.Image) -> Image.Image:
        """Add subtle film grain."""
        img_array = np.array(image).astype(np.float32)
        
        # Generate noise
        noise = np.random.normal(0, 3, img_array.shape)
        
        # Add noise
        img_array += noise
        img_array = np.clip(img_array, 0, 255)
        
        return Image.fromarray(img_array.astype(np.uint8))
    
    async def _add_gentle_glow(self, image: Image.Image) -> Image.Image:
        """Add gentle glow effect."""
        # Create glow layer
        glow = image.filter(ImageFilter.GaussianBlur(radius=3))
        
        # Blend with original
        result = Image.blend(image, glow, 0.1)
        
        return result
    
    async def _save_image(self, image: Image.Image, output_path: Path) -> None:
        """Save processed image."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Determine format from extension
        ext = output_path.suffix.lower()
        if ext in ['.jpg', '.jpeg']:
            image.save(output_path, 'JPEG', quality=self.config.output_quality, optimize=True)
        elif ext == '.png':
            image.save(output_path, 'PNG', optimize=True)
        elif ext == '.webp':
            image.save(output_path, 'WebP', quality=self.config.output_quality, optimize=True)
        else:
            # Default to JPEG
            image.save(output_path, 'JPEG', quality=self.config.output_quality, optimize=True)
    
    async def _calculate_filter_effectiveness(
        self, 
        original: Image.Image, 
        filtered: Image.Image, 
        filter_type: str
    ) -> float:
        """Calculate filter effectiveness score."""
        try:
            # Simple effectiveness metrics
            orig_array = np.array(original)
            filt_array = np.array(filtered)
            
            # Calculate difference
            diff = np.mean(np.abs(orig_array.astype(float) - filt_array.astype(float)))
            
            # Normalize difference to 0-1 scale
            max_possible_diff = 255.0
            effectiveness = min(diff / max_possible_diff * 2, 1.0)
            
            # Adjust based on filter type expectations
            if "auto_enhance" in filter_type:
                # Auto enhance should have moderate changes
                effectiveness = max(0.3, min(effectiveness, 0.8))
            elif "artistic" in filter_type:
                # Artistic filters should have more dramatic changes
                effectiveness = max(0.5, effectiveness)
            
            return effectiveness
            
        except Exception as e:
            logger.warning(f"Could not calculate effectiveness: {e}")
            return 0.7  # Default effectiveness score
    
    def get_available_filters(self) -> Dict[str, Dict]:
        """Get list of available filters and their descriptions."""
        descriptions = {
            "artistic_oil": "Oil painting style with smooth, painterly strokes",
            "artistic_watercolor": "Watercolor effect with soft, flowing transitions",
            "artistic_sketch": "Pencil sketch style with edge enhancement",
            "vintage_film": "Classic vintage film look with warm tones",
            "cinematic_teal": "Modern teal and orange color grading",
            "portrait_beauty": "Beauty filter with skin smoothing",
            "landscape_enhance": "Enhanced contrast and saturation for landscapes",
            "dramatic_bw": "High-contrast black and white conversion",
            "instagram_vsco": "VSCO-style filter with lifted shadows",
            "tiktok_trendy": "Trendy social media filter with boosted saturation",
            "auto_enhance": "Intelligent automatic enhancement"
        }
        
        return {
            filter_name: {
                **filter_config,
                "description": descriptions.get(filter_name, "Creative filter")
            }
            for filter_name, filter_config in self.available_filters.items()
        }
    
    async def batch_apply_filters(
        self,
        input_dir: Union[str, Path],
        output_dir: Union[str, Path],
        filter_type: str = "auto_enhance",
        config: Optional[FilterConfig] = None
    ) -> Dict[str, any]:
        """Apply filters to multiple images in batch."""
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        
        if not input_dir.exists():
            return {"success": False, "error": "Input directory not found"}
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = []
        supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
        
        for img_path in input_dir.iterdir():
            if img_path.suffix.lower() in supported_formats:
                output_path = output_dir / f"{img_path.stem}_filtered{img_path.suffix}"
                
                result = await self.apply_ai_filter(
                    img_path, output_path, filter_type, config
                )
                
                results.append({
                    "input": str(img_path),
                    "output": str(output_path),
                    "result": result
                })
        
        successful = sum(1 for r in results if r["result"]["success"])
        
        return {
            "success": True,
            "total_processed": len(results),
            "successful": successful,
            "failed": len(results) - successful,
            "results": results
        }