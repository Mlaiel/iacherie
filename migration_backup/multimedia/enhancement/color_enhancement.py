"""Color Enhancement Engine
Advanced color correction and enhancement algorithms.

Created by: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import numpy as np
import cv2
from typing import Dict, Optional, Union, Tuple, List
from pathlib import Path
from dataclasses import dataclass
import logging
from PIL import Image, ImageEnhance, ImageFilter
import colorsys

logger = logging.getLogger(__name__)

@dataclass
class ColorEnhancementConfig:
    """Configuration for color enhancement."""
    auto_balance: bool = True
    vibrance_boost: float = 1.2  # 0.0 to 2.0
    saturation_adjust: float = 1.1  # 0.0 to 2.0
    contrast_enhance: float = 1.15  # 0.0 to 2.0
    brightness_adjust: float = 1.05  # 0.0 to 2.0
    gamma_correction: float = 1.0  # 0.1 to 3.0
    temperature_shift: int = 0  # -100 to 100 (blue to warm)
    highlight_recovery: float = 0.8  # 0.0 to 1.0
    shadow_lift: float = 0.2  # 0.0 to 1.0
    color_grading_enabled: bool = True
    hsl_adjustments: Dict[str, Dict[str, float]] = None

class ColorEnhancementEngine:
    """Enterprise color enhancement engine with advanced algorithms."""
    
    def __init__(self):
        self.config = ColorEnhancementConfig()
        
    async def enhance_colors(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        enhancement_type: str = "auto",
        config: Optional[ColorEnhancementConfig] = None
    ) -> Dict[str, any]:
        """Enhance image colors with advanced algorithms."""
        try:
            if config:
                self.config = config
                
            input_path = Path(input_path)
            output_path = Path(output_path)
            
            # Load image
            if not input_path.exists():
                raise FileNotFoundError(f"Input file not found: {input_path}")
                
            # Detect enhancement type if auto
            if enhancement_type == "auto":
                enhancement_type = await self._detect_enhancement_needs(input_path)
            
            # Apply enhancement based on type
            enhancement_result = await self._apply_enhancement(
                input_path, output_path, enhancement_type
            )
            
            return {
                "success": True,
                "enhancement_type": enhancement_type,
                "color_improvement": enhancement_result["improvement_score"],
                "adjustments_applied": enhancement_result["adjustments"],
                "processing_time": enhancement_result["processing_time"],
                "output_path": str(output_path)
            }
            
        except Exception as e:
            logger.error(f"Color enhancement failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _detect_enhancement_needs(self, input_path: Path) -> str:
        """Analyze image and detect optimal enhancement type."""
        try:
            # Load and analyze image
            image = cv2.imread(str(input_path))
            if image is None:
                return "standard"
                
            # Convert to different color spaces for analysis
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            
            # Analyze saturation
            saturation_mean = np.mean(hsv[:, :, 1])
            
            # Analyze brightness distribution
            brightness = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            hist = cv2.calcHist([brightness], [0], None, [256], [0, 256])
            
            # Detect shadows and highlights
            shadows = np.sum(hist[0:85]) / np.sum(hist)
            highlights = np.sum(hist[170:256]) / np.sum(hist)
            
            # Determine enhancement type
            if saturation_mean < 80:
                return "low_saturation"
            elif shadows > 0.4:
                return "underexposed"
            elif highlights > 0.3:
                return "overexposed"
            elif saturation_mean < 120:
                return "vibrant_boost"
            else:
                return "standard"
                
        except Exception as e:
            logger.warning(f"Enhancement detection failed: {e}")
            return "standard"
    
    async def _apply_enhancement(
        self, 
        input_path: Path, 
        output_path: Path, 
        enhancement_type: str
    ) -> Dict[str, any]:
        """Apply specific enhancement based on type."""
        start_time = asyncio.get_event_loop().time()
        adjustments = []
        
        try:
            # Load image with PIL for high-quality processing
            image = Image.open(input_path)
            
            if enhancement_type == "low_saturation":
                image, adj = await self._enhance_low_saturation(image)
                adjustments.extend(adj)
            elif enhancement_type == "underexposed":
                image, adj = await self._fix_underexposure(image)
                adjustments.extend(adj)
            elif enhancement_type == "overexposed":
                image, adj = await self._fix_overexposure(image)
                adjustments.extend(adj)
            elif enhancement_type == "vibrant_boost":
                image, adj = await self._apply_vibrant_boost(image)
                adjustments.extend(adj)
            else:  # standard
                image, adj = await self._apply_standard_enhancement(image)
                adjustments.extend(adj)
            
            # Apply additional enhancements if enabled
            if self.config.auto_balance:
                image, adj = await self._apply_auto_color_balance(image)
                adjustments.extend(adj)
            
            if self.config.color_grading_enabled:
                image, adj = await self._apply_color_grading(image)
                adjustments.extend(adj)
            
            # Save enhanced image
            output_path.parent.mkdir(parents=True, exist_ok=True)
            image.save(output_path, quality=95, optimize=True)
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            # Calculate improvement score
            improvement_score = await self._calculate_improvement_score(
                input_path, output_path
            )
            
            return {
                "improvement_score": improvement_score,
                "adjustments": adjustments,
                "processing_time": processing_time
            }
            
        except Exception as e:
            raise Exception(f"Enhancement application failed: {e}")
    
    async def _enhance_low_saturation(self, image: Image.Image) -> Tuple[Image.Image, List[str]]:
        """Enhance images with low saturation."""
        adjustments = []
        
        # Boost saturation
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(self.config.saturation_adjust * 1.3)
        adjustments.append("saturation_boost")
        
        # Enhance vibrance (selective saturation)
        image = await self._apply_vibrance(image, self.config.vibrance_boost)
        adjustments.append("vibrance_enhancement")
        
        return image, adjustments
    
    async def _fix_underexposure(self, image: Image.Image) -> Tuple[Image.Image, List[str]]:
        """Fix underexposed images."""
        adjustments = []
        
        # Lift shadows
        image = await self._adjust_shadows_highlights(
            image, shadow_lift=self.config.shadow_lift
        )
        adjustments.append("shadow_lift")
        
        # Brightness adjustment
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(self.config.brightness_adjust * 1.2)
        adjustments.append("brightness_correction")
        
        # Gentle contrast boost
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.1)
        adjustments.append("contrast_enhancement")
        
        return image, adjustments
    
    async def _fix_overexposure(self, image: Image.Image) -> Tuple[Image.Image, List[str]]:
        """Fix overexposed images."""
        adjustments = []
        
        # Recover highlights
        image = await self._adjust_shadows_highlights(
            image, highlight_recovery=self.config.highlight_recovery
        )
        adjustments.append("highlight_recovery")
        
        # Reduce brightness slightly
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(0.95)
        adjustments.append("brightness_reduction")
        
        return image, adjustments
    
    async def _apply_vibrant_boost(self, image: Image.Image) -> Tuple[Image.Image, List[str]]:
        """Apply vibrant color boost."""
        adjustments = []
        
        # Selective vibrance boost
        image = await self._apply_vibrance(image, self.config.vibrance_boost * 1.1)
        adjustments.append("vibrance_boost")
        
        # Slight contrast enhancement
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.05)
        adjustments.append("micro_contrast")
        
        return image, adjustments
    
    async def _apply_standard_enhancement(self, image: Image.Image) -> Tuple[Image.Image, List[str]]:
        """Apply standard color enhancement."""
        adjustments = []
        
        # Standard saturation boost
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(self.config.saturation_adjust)
        adjustments.append("saturation_adjustment")
        
        # Contrast enhancement
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(self.config.contrast_enhance)
        adjustments.append("contrast_enhancement")
        
        # Brightness adjustment
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(self.config.brightness_adjust)
        adjustments.append("brightness_adjustment")
        
        return image, adjustments
    
    async def _apply_vibrance(self, image: Image.Image, strength: float) -> Image.Image:
        """Apply selective saturation enhancement (vibrance)."""
        # Convert to numpy array for processing
        img_array = np.array(image)
        
        # Convert to HSV for selective saturation
        hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV).astype(np.float32)
        
        # Apply selective saturation boost
        # Boost saturation for low-saturated areas more than high-saturated areas
        saturation = hsv[:, :, 1]
        saturation_mask = 1.0 - (saturation / 255.0)  # Inverse saturation mask
        
        # Apply vibrance with mask
        hsv[:, :, 1] = np.clip(
            saturation + (saturation * (strength - 1.0) * saturation_mask),
            0, 255
        )
        
        # Convert back to RGB
        enhanced = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
        return Image.fromarray(enhanced)
    
    async def _apply_auto_color_balance(self, image: Image.Image) -> Tuple[Image.Image, List[str]]:
        """Apply automatic color balance."""
        img_array = np.array(image)
        
        # Calculate color balance adjustments
        # Simple Gray World assumption
        avg_b = np.mean(img_array[:, :, 2])  # Blue channel
        avg_g = np.mean(img_array[:, :, 1])  # Green channel
        avg_r = np.mean(img_array[:, :, 0])  # Red channel
        
        avg_gray = (avg_r + avg_g + avg_b) / 3
        
        # Calculate adjustment factors
        scale_r = avg_gray / avg_r if avg_r > 0 else 1.0
        scale_g = avg_gray / avg_g if avg_g > 0 else 1.0
        scale_b = avg_gray / avg_b if avg_b > 0 else 1.0
        
        # Apply color balance
        img_array[:, :, 0] = np.clip(img_array[:, :, 0] * scale_r, 0, 255)
        img_array[:, :, 1] = np.clip(img_array[:, :, 1] * scale_g, 0, 255)
        img_array[:, :, 2] = np.clip(img_array[:, :, 2] * scale_b, 0, 255)
        
        return Image.fromarray(img_array.astype(np.uint8)), ["auto_color_balance"]
    
    async def _apply_color_grading(self, image: Image.Image) -> Tuple[Image.Image, List[str]]:
        """Apply cinematic color grading."""
        img_array = np.array(image).astype(np.float32) / 255.0
        
        # Apply S-curve for contrast
        img_array = np.power(img_array, self.config.gamma_correction)
        
        # Subtle color grading - warm highlights, cool shadows
        height, width = img_array.shape[:2]
        
        # Create luminance mask
        luminance = 0.299 * img_array[:, :, 0] + 0.587 * img_array[:, :, 1] + 0.114 * img_array[:, :, 2]
        
        # Warm highlights (add slight orange/yellow tint to bright areas)
        highlight_mask = np.clip((luminance - 0.6) / 0.4, 0, 1)
        img_array[:, :, 0] += highlight_mask * 0.02  # Red boost
        img_array[:, :, 1] += highlight_mask * 0.01  # Green boost
        
        # Cool shadows (add slight blue tint to dark areas)
        shadow_mask = np.clip((0.4 - luminance) / 0.4, 0, 1)
        img_array[:, :, 2] += shadow_mask * 0.02  # Blue boost
        
        # Clamp values
        img_array = np.clip(img_array, 0, 1)
        
        return Image.fromarray((img_array * 255).astype(np.uint8)), ["cinematic_grading"]
    
    async def _adjust_shadows_highlights(
        self, 
        image: Image.Image, 
        shadow_lift: float = 0.0, 
        highlight_recovery: float = 0.0
    ) -> Image.Image:
        """Adjust shadows and highlights independently."""
        img_array = np.array(image).astype(np.float32) / 255.0
        
        # Calculate luminance
        luminance = 0.299 * img_array[:, :, 0] + 0.587 * img_array[:, :, 1] + 0.114 * img_array[:, :, 2]
        
        if shadow_lift > 0:
            # Create shadow mask (1 for shadows, 0 for highlights)
            shadow_mask = 1.0 - np.power(luminance, 2)
            
            # Lift shadows
            lift_factor = 1.0 + shadow_lift * shadow_mask[:, :, np.newaxis]
            img_array *= lift_factor
        
        if highlight_recovery > 0:
            # Create highlight mask (1 for highlights, 0 for shadows)
            highlight_mask = np.power(luminance, 2)
            
            # Recover highlights
            recovery_factor = 1.0 - highlight_recovery * highlight_mask[:, :, np.newaxis]
            img_array *= recovery_factor
        
        # Clamp values
        img_array = np.clip(img_array, 0, 1)
        
        return Image.fromarray((img_array * 255).astype(np.uint8))
    
    async def _calculate_improvement_score(
        self, 
        input_path: Path, 
        output_path: Path
    ) -> float:
        """Calculate color enhancement improvement score."""
        try:
            # Load both images
            original = cv2.imread(str(input_path))
            enhanced = cv2.imread(str(output_path))
            
            if original is None or enhanced is None:
                return 0.7  # Default score
            
            # Calculate various metrics
            # 1. Saturation improvement
            orig_hsv = cv2.cvtColor(original, cv2.COLOR_BGR2HSV)
            enh_hsv = cv2.cvtColor(enhanced, cv2.COLOR_BGR2HSV)
            
            orig_sat = np.mean(orig_hsv[:, :, 1])
            enh_sat = np.mean(enh_hsv[:, :, 1])
            
            sat_improvement = min((enh_sat / orig_sat) - 1.0, 0.5) if orig_sat > 0 else 0.1
            
            # 2. Contrast improvement
            orig_gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
            enh_gray = cv2.cvtColor(enhanced, cv2.COLOR_BGR2GRAY)
            
            orig_contrast = np.std(orig_gray)
            enh_contrast = np.std(enh_gray)
            
            contrast_improvement = min((enh_contrast / orig_contrast) - 1.0, 0.3) if orig_contrast > 0 else 0.1
            
            # Combined score
            base_score = 0.7
            improvement_score = base_score + sat_improvement + contrast_improvement
            
            return min(improvement_score, 1.0)
            
        except Exception as e:
            logger.warning(f"Could not calculate improvement score: {e}")
            return 0.75  # Default good score
    
    async def batch_enhance_colors(
        self,
        input_dir: Union[str, Path],
        output_dir: Union[str, Path],
        enhancement_type: str = "auto",
        config: Optional[ColorEnhancementConfig] = None
    ) -> Dict[str, any]:
        """Batch enhance colors for multiple images."""
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        
        if not input_dir.exists():
            return {"success": False, "error": "Input directory not found"}
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = []
        supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
        
        for img_path in input_dir.iterdir():
            if img_path.suffix.lower() in supported_formats:
                output_path = output_dir / img_path.name
                
                result = await self.enhance_colors(
                    img_path, output_path, enhancement_type, config
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