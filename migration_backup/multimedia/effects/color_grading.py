"""Color Grading Engine
Professional color grading and cinematic look development.

Created by: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import numpy as np
import cv2
from typing import Dict, Optional, Union, List, Tuple
from pathlib import Path
from dataclasses import dataclass
import logging
from PIL import Image
from enum import Enum

logger = logging.getLogger(__name__)

class ColorGradingPreset(Enum):
    """Professional color grading presets."""
    CINEMATIC_TEAL_ORANGE = "cinematic_teal_orange"
    FILM_NOIR = "film_noir"
    WARM_SUNSET = "warm_sunset"
    COOL_BLUE = "cool_blue"
    VINTAGE_KODAK = "vintage_kodak"
    FUJI_FILM = "fuji_film"
    BLEACH_BYPASS = "bleach_bypass"
    CROSS_PROCESS = "cross_process"
    DESATURATED_CONTRAST = "desaturated_contrast"
    HOLLYWOOD_GOLDEN = "hollywood_golden"
    NORDIC_NOIR = "nordic_noir"
    CYBERPUNK = "cyberpunk"
    PASTEL_DREAM = "pastel_dream"
    HIGH_CONTRAST_BW = "high_contrast_bw"

@dataclass
class ColorGradingConfig:
    """Configuration for color grading."""
    preset: ColorGradingPreset = ColorGradingPreset.CINEMATIC_TEAL_ORANGE
    intensity: float = 1.0  # 0.0 to 2.0
    
    # Manual adjustments (override preset if specified)
    shadows: Tuple[float, float, float] = None  # RGB lift
    midtones: Tuple[float, float, float] = None  # RGB gamma
    highlights: Tuple[float, float, float] = None  # RGB gain
    
    # Global adjustments
    exposure: float = 0.0  # -2.0 to 2.0 stops
    contrast: float = 0.0  # -1.0 to 1.0
    saturation: float = 0.0  # -1.0 to 1.0
    vibrance: float = 0.0  # -1.0 to 1.0
    
    # Advanced
    curve_adjustment: bool = True
    vignette_strength: float = 0.0  # 0.0 to 1.0
    film_grain: bool = False
    grain_intensity: float = 0.2
    
    # LUT application
    use_custom_lut: bool = False
    lut_path: str = None

class ColorGradingEngine:
    """Professional color grading engine for cinematic looks."""
    
    def __init__(self):
        self.config = ColorGradingConfig()
        self.presets = self._initialize_presets()
        
    async def apply_color_grade(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        grade_type: str = "cinematic",
        intensity: float = 0.8
    ) -> Dict[str, any]:
        """Apply professional color grading with enhanced capabilities."""
        try:
            # Map grade_type to preset
            preset_mapping = {
                "cinematic": ColorGradingPreset.CINEMATIC_TEAL_ORANGE,
                "film_noir": ColorGradingPreset.FILM_NOIR,
                "warm": ColorGradingPreset.WARM_SUNSET,
                "cool": ColorGradingPreset.COOL_BLUE,
                "vintage": ColorGradingPreset.VINTAGE_KODAK,
                "cyberpunk": ColorGradingPreset.CYBERPUNK,
                "pastel": ColorGradingPreset.PASTEL_DREAM
            }
            
            preset = preset_mapping.get(grade_type, ColorGradingPreset.CINEMATIC_TEAL_ORANGE)
            
            return await self.apply_color_grading(input_path, output_path, preset, intensity)
            
        except Exception as e:
            logger.error(f"Color grading failed: {str(e)}")
            return {"success": False, "error": str(e)}
        
    async def apply_color_grading(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        preset: Union[ColorGradingPreset, str] = ColorGradingPreset.CINEMATIC_TEAL_ORANGE,
        intensity: float = 1.0,
        config: Optional[ColorGradingConfig] = None
    ) -> Dict[str, any]:
        """Apply professional color grading to image or video."""
        try:
            if config:
                self.config = config
            else:
                self.config.preset = preset if isinstance(preset, ColorGradingPreset) else ColorGradingPreset(preset)
                self.config.intensity = intensity
            
            input_path = Path(input_path)
            output_path = Path(output_path)
            
            if not input_path.exists():
                raise FileNotFoundError(f"Input file not found: {input_path}")
            
            # Detect file type
            file_ext = input_path.suffix.lower()
            
            if file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']:
                result = await self._grade_image(input_path, output_path)
            elif file_ext in ['.mp4', '.avi', '.mov', '.mkv']:
                result = await self._grade_video(input_path, output_path)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
            
            return {
                "success": True,
                "preset_applied": self.config.preset.value,
                "intensity": self.config.intensity,
                "color_grade_applied": self.config.preset.value,
                "output_path": str(output_path),
                **result
            }
            
        except Exception as e:
            logger.error(f"Color grading failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _grade_image(self, input_path: Path, output_path: Path) -> Dict[str, any]:
        """Apply color grading to image."""
        # Load image
        image = cv2.imread(str(input_path))
        if image is None:
            raise ValueError("Could not load image")
        
        original_image = image.copy()
        
        # Apply color grading
        graded_image = await self._apply_grading_pipeline(image)
        
        # Save result
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(output_path), graded_image)
        
        # Calculate color metrics
        color_metrics = await self._analyze_color_changes(original_image, graded_image)
        
        return {
            "image_processing": True,
            "image_dimensions": image.shape,
            "color_metrics": color_metrics,
            "adjustments_applied": await self._get_applied_adjustments()
        }
    
    async def _apply_grading_pipeline(self, image: np.ndarray) -> np.ndarray:
        """Apply complete color grading pipeline."""
        graded = image.copy().astype(np.float32) / 255.0
        
        # 1. Global exposure adjustment
        if self.config.exposure != 0:
            graded = graded * (2 ** self.config.exposure)
        
        # 2. Apply preset grading
        graded = await self._apply_preset_grading(graded)
        
        # 3. Contrast adjustment
        if self.config.contrast != 0:
            graded = await self._adjust_contrast(graded, self.config.contrast)
        
        # 4. Saturation and vibrance
        if self.config.saturation != 0 or self.config.vibrance != 0:
            graded = await self._adjust_saturation_vibrance(graded)
        
        # 5. Apply intensity scaling
        if self.config.intensity < 1.0:
            original = image.astype(np.float32) / 255.0
            graded = original * (1 - self.config.intensity) + graded * self.config.intensity
        
        # Clamp and convert back
        graded = np.clip(graded, 0, 1)
        return (graded * 255).astype(np.uint8)
    
    async def _apply_preset_grading(self, image: np.ndarray) -> np.ndarray:
        """Apply predefined color grading preset."""
        preset_config = self.presets[self.config.preset]
        
        if self.config.preset == ColorGradingPreset.CINEMATIC_TEAL_ORANGE:
            # Teal and orange look
            image = await self._apply_teal_orange_grading(image)
        elif self.config.preset == ColorGradingPreset.FILM_NOIR:
            image = await self._apply_film_noir_grading(image)
        elif self.config.preset == ColorGradingPreset.WARM_SUNSET:
            image = await self._apply_warm_grading(image)
        elif self.config.preset == ColorGradingPreset.COOL_BLUE:
            image = await self._apply_cool_grading(image)
        elif self.config.preset == ColorGradingPreset.VINTAGE_KODAK:
            image = await self._apply_vintage_grading(image)
        elif self.config.preset == ColorGradingPreset.CYBERPUNK:
            image = await self._apply_cyberpunk_grading(image)
        elif self.config.preset == ColorGradingPreset.PASTEL_DREAM:
            image = await self._apply_pastel_grading(image)
        
        return image
    
    async def _apply_teal_orange_grading(self, image: np.ndarray) -> np.ndarray:
        """Apply cinematic teal and orange grading."""
        # Shift blues towards teal
        blue_mask = image[:, :, 0] > image[:, :, 2]  # BGR format
        image[:, :, 1][blue_mask] *= 1.1  # Boost green in blue areas
        
        # Shift reds/yellows towards orange
        warm_mask = image[:, :, 2] > image[:, :, 0]  # Red > Blue
        image[:, :, 1][warm_mask] *= 0.9  # Reduce green in warm areas
        image[:, :, 2][warm_mask] *= 1.05  # Boost red
        
        return image
    
    async def _apply_film_noir_grading(self, image: np.ndarray) -> np.ndarray:
        """Apply film noir black and white with high contrast."""
        # Convert to grayscale with custom weights
        gray = 0.4 * image[:, :, 2] + 0.4 * image[:, :, 1] + 0.2 * image[:, :, 0]
        
        # High contrast S-curve
        gray = np.power(gray, 0.7)
        
        # Convert back to 3-channel
        return np.stack([gray, gray, gray], axis=-1)
    
    async def _apply_warm_grading(self, image: np.ndarray) -> np.ndarray:
        """Apply warm sunset grading."""
        image[:, :, 2] *= 1.15  # Boost red
        image[:, :, 1] *= 1.05  # Slight green boost
        image[:, :, 0] *= 0.85  # Reduce blue
        return image
    
    async def _apply_cool_grading(self, image: np.ndarray) -> np.ndarray:
        """Apply cool blue grading."""
        image[:, :, 0] *= 1.15  # Boost blue
        image[:, :, 1] *= 1.02  # Slight green boost
        image[:, :, 2] *= 0.9   # Reduce red
        return image
    
    async def _apply_vintage_grading(self, image: np.ndarray) -> np.ndarray:
        """Apply vintage film look."""
        # Lift shadows (add warm tone)
        image[:, :, 2] += 0.05  # Red lift
        image[:, :, 1] += 0.02  # Green lift
        
        # Desaturate slightly
        gray = 0.299 * image[:, :, 2] + 0.587 * image[:, :, 1] + 0.114 * image[:, :, 0]
        image = image * 0.85 + gray[:, :, np.newaxis] * 0.15
        
        return image
    
    async def _apply_cyberpunk_grading(self, image: np.ndarray) -> np.ndarray:
        """Apply cyberpunk neon grading."""
        # Boost cyan and magenta
        image[:, :, 0] *= 1.2   # Blue boost
        image[:, :, 2] *= 1.15  # Red boost
        image[:, :, 1] *= 0.95  # Slight green reduction
        
        # High contrast
        image = np.power(image, 0.8)
        
        return image
    
    async def _apply_pastel_grading(self, image: np.ndarray) -> np.ndarray:
        """Apply soft pastel grading."""
        # Lift all channels slightly
        image += 0.1
        
        # Reduce contrast
        image = np.power(image, 1.3)
        
        # Desaturate
        gray = 0.299 * image[:, :, 2] + 0.587 * image[:, :, 1] + 0.114 * image[:, :, 0]
        image = image * 0.7 + gray[:, :, np.newaxis] * 0.3
        
        return image
    
    async def _adjust_contrast(self, image: np.ndarray, contrast: float) -> np.ndarray:
        """Adjust image contrast."""
        if contrast > 0:
            # Increase contrast
            image = np.power(image, 1.0 - contrast * 0.5)
        else:
            # Decrease contrast
            image = np.power(image, 1.0 + abs(contrast) * 0.5)
        
        return image
    
    async def _adjust_saturation_vibrance(self, image: np.ndarray) -> np.ndarray:
        """Adjust saturation and vibrance."""
        # Convert to HSV for saturation adjustment
        hsv = cv2.cvtColor((image * 255).astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
        
        # Saturation adjustment
        if self.config.saturation != 0:
            hsv[:, :, 1] *= (1.0 + self.config.saturation)
        
        # Vibrance (selective saturation boost)
        if self.config.vibrance != 0:
            saturation_mask = 1.0 - (hsv[:, :, 1] / 255.0)
            vibrance_boost = self.config.vibrance * saturation_mask
            hsv[:, :, 1] += vibrance_boost * 255
        
        # Clamp saturation
        hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)
        
        # Convert back to BGR
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR).astype(np.float32) / 255.0
    
    async def _grade_video(self, input_path: Path, output_path: Path) -> Dict[str, any]:
        """Apply color grading to video."""
        import subprocess
        
        # Create FFmpeg color grading filter based on preset
        filter_string = await self._create_ffmpeg_color_filter()
        
        ffmpeg_cmd = [
            'ffmpeg', '-i', str(input_path),
            '-vf', filter_string,
            '-c:a', 'copy',  # Copy audio
            '-y', str(output_path)
        ]
        
        try:
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    "video_processing": True,
                    "color_filter": filter_string,
                    "audio_preserved": True
                }
            else:
                raise Exception(f"FFmpeg failed: {result.stderr}")
                
        except Exception as e:
            logger.warning(f"FFmpeg video grading failed, using fallback: {e}")
            
            # Fallback: copy file
            import shutil
            shutil.copy2(input_path, output_path)
            
            return {
                "video_processing": False,
                "fallback_used": True,
                "note": "Advanced video grading requires FFmpeg"
            }
    
    async def _create_ffmpeg_color_filter(self) -> str:
        """Create FFmpeg color filter string based on configuration."""
        filters = []
        
        # Preset-specific filters
        if self.config.preset == ColorGradingPreset.CINEMATIC_TEAL_ORANGE:
            filters.append("colorbalance=rs=0.1:gs=-0.1:bs=-0.2:rh=0.2:gh=0.0:bh=-0.3")
        elif self.config.preset == ColorGradingPreset.FILM_NOIR:
            filters.append("eq=contrast=1.3:brightness=-0.1:saturation=0.2")
        elif self.config.preset == ColorGradingPreset.WARM_SUNSET:
            filters.append("colortemperature=temperature=3200:mix=0.7")
        elif self.config.preset == ColorGradingPreset.COOL_BLUE:
            filters.append("colortemperature=temperature=7000:mix=0.6")
        elif self.config.preset == ColorGradingPreset.VINTAGE_KODAK:
            filters.append("eq=saturation=1.2:gamma=1.1")
        elif self.config.preset == ColorGradingPreset.CYBERPUNK:
            filters.append("colorbalance=rs=-0.2:gs=0.0:bs=0.3:rh=0.3:gh=-0.2:bh=0.4")
        elif self.config.preset == ColorGradingPreset.PASTEL_DREAM:
            filters.append("eq=saturation=0.7:brightness=0.15:contrast=0.8")
        
        return ",".join(filters) if filters else "null"
    
    def _initialize_presets(self) -> Dict[ColorGradingPreset, Dict]:
        """Initialize color grading presets."""
        return {preset: {} for preset in ColorGradingPreset}
    
    async def _analyze_color_changes(self, original: np.ndarray, graded: np.ndarray) -> Dict[str, float]:
        """Analyze color changes between original and graded images."""
        # Convert to LAB color space for perceptual analysis
        orig_lab = cv2.cvtColor(original, cv2.COLOR_BGR2LAB)
        graded_lab = cv2.cvtColor(graded, cv2.COLOR_BGR2LAB)
        
        # Calculate differences
        l_diff = np.mean(graded_lab[:, :, 0]) - np.mean(orig_lab[:, :, 0])
        a_diff = np.mean(graded_lab[:, :, 1]) - np.mean(orig_lab[:, :, 1])
        b_diff = np.mean(graded_lab[:, :, 2]) - np.mean(orig_lab[:, :, 2])
        
        # Overall color shift
        color_shift = np.sqrt(l_diff**2 + a_diff**2 + b_diff**2)
        
        return {
            "luminance_change": float(l_diff),
            "green_magenta_shift": float(a_diff),
            "blue_yellow_shift": float(b_diff),
            "overall_color_shift": float(color_shift),
            "intensity_applied": self.config.intensity
        }
    
    async def _get_applied_adjustments(self) -> List[str]:
        """Get list of adjustments that were applied."""
        adjustments = [f"preset_{self.config.preset.value}"]
        
        if self.config.exposure != 0:
            adjustments.append("exposure")
        if self.config.contrast != 0:
            adjustments.append("contrast")
        if self.config.saturation != 0:
            adjustments.append("saturation")
        if self.config.vibrance != 0:
            adjustments.append("vibrance")
        
        return adjustments