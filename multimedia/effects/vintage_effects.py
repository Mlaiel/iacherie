"""Vintage Effects Engine
Retro and vintage effects for nostalgic content creation.

Created by: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import numpy as np
import cv2
import math
import random
from typing import Dict, Optional, Union, List, Tuple
from pathlib import Path
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class VintageConfig:
    """Configuration for vintage effects."""
    era: str = "70s"  # 60s, 70s, 80s, 90s, polaroid, super8, vhs
    intensity: float = 0.7  # Effect strength 0-1
    grain_amount: float = 0.3  # Film grain intensity
    vignette_strength: float = 0.4  # Vignette darkness
    color_shift: bool = True  # Enable color shifting
    scratches_enabled: bool = True  # Film scratches
    dust_spots: bool = True  # Dust and spots
    light_leaks: bool = True  # Light leak effects

class FilmGrain:
    """Film grain and texture effects."""
    
    def __init__(self, config: VintageConfig):
        self.config = config
    
    def add_film_grain(self, frame: np.ndarray, intensity: float = 0.3) -> np.ndarray:
        """Add realistic film grain to image."""
        h, w = frame.shape[:2]
        
        # Generate different types of noise for realistic grain
        luminance_noise = np.random.normal(0, intensity * 15, (h, w))
        color_noise = np.random.normal(0, intensity * 8, (h, w, 3))
        
        # Convert frame to float for processing
        result = frame.astype(np.float32)
        
        # Add luminance noise to all channels
        for c in range(3):
            result[:, :, c] += luminance_noise
        
        # Add color-specific noise
        result += color_noise
        
        # Simulate grain pattern with frequency modulation
        x, y = np.meshgrid(np.arange(w), np.arange(h))
        grain_pattern = np.sin(x * 0.1 + y * 0.1) * intensity * 5
        
        for c in range(3):
            result[:, :, c] += grain_pattern
        
        return np.clip(result, 0, 255).astype(np.uint8)
    
    def add_dust_and_scratches(self, frame: np.ndarray, intensity: float = 0.2) -> np.ndarray:
        """Add dust spots and film scratches."""
        h, w = frame.shape[:2]
        result = frame.copy()
        
        # Add dust spots
        num_spots = int(intensity * 20)
        for _ in range(num_spots):
            x = random.randint(0, w - 1)
            y = random.randint(0, h - 1)
            size = random.randint(1, 3)
            
            # Dark spots
            if random.random() < 0.7:
                color = (0, 0, 0)
            else:  # Light spots
                color = (255, 255, 255)
            
            cv2.circle(result, (x, y), size, color, -1)
        
        # Add vertical scratches
        num_scratches = int(intensity * 5)
        for _ in range(num_scratches):
            x = random.randint(0, w - 1)
            start_y = random.randint(0, h // 2)
            end_y = random.randint(h // 2, h - 1)
            
            # Create scratch with varying opacity
            scratch_mask = np.zeros((h, w), dtype=np.float32)
            cv2.line(scratch_mask, (x, start_y), (x, end_y), 1.0, random.randint(1, 2))
            
            # Apply scratch
            scratch_intensity = random.uniform(0.3, 0.8)
            for c in range(3):
                result[:, :, c] = result[:, :, c] * (1 - scratch_mask * scratch_intensity)
        
        return result

class ColorGrading:
    """Vintage color grading and processing."""
    
    def __init__(self, config: VintageConfig):
        self.config = config
    
    def apply_vintage_lut(self, frame: np.ndarray, era: str = "70s") -> np.ndarray:
        """Apply era-specific color grading."""
        result = frame.copy().astype(np.float32)
        
        if era == "60s":
            # High contrast, saturated colors
            result = self._apply_sixties_grade(result)
        elif era == "70s":
            # Warm, golden tones
            result = self._apply_seventies_grade(result)
        elif era == "80s":
            # Vibrant, neon-influenced
            result = self._apply_eighties_grade(result)
        elif era == "90s":
            # Slightly desaturated, cool tones
            result = self._apply_nineties_grade(result)
        elif era == "polaroid":
            # High exposure, vintage instant film
            result = self._apply_polaroid_grade(result)
        elif era == "super8":
            # Super 8 film characteristic
            result = self._apply_super8_grade(result)
        elif era == "vhs":
            # VHS tape degradation
            result = self._apply_vhs_grade(result)
        
        return np.clip(result, 0, 255).astype(np.uint8)
    
    def _apply_seventies_grade(self, frame: np.ndarray) -> np.ndarray:
        """Apply 1970s golden hour grading."""
        # Warm color temperature
        frame[:, :, 0] *= 0.8  # Reduce blue
        frame[:, :, 1] *= 1.05  # Slight green
        frame[:, :, 2] *= 1.2  # Increase red/yellow
        
        # Lift shadows with warm tone
        shadows_mask = frame < 100
        frame[shadows_mask] = frame[shadows_mask] * 0.9 + 15
        
        # Add golden glow
        frame += 8
        
        return frame

class VintageEffects:
    """Special vintage effects and distortions."""
    
    def __init__(self, config: VintageConfig):
        self.config = config
    
    def add_vignette(self, frame: np.ndarray, strength: float = 0.4) -> np.ndarray:
        """Add vintage-style vignette."""
        h, w = frame.shape[:2]
        
        # Create vignette mask
        center_x, center_y = w // 2, h // 2
        Y, X = np.ogrid[:h, :w]
        
        # Distance from center
        dist_from_center = np.sqrt((X - center_x)**2 + (Y - center_y)**2)
        max_dist = np.sqrt(center_x**2 + center_y**2)
        
        # Create vignette with smooth falloff
        vignette = 1 - (dist_from_center / max_dist) ** 2 * strength
        vignette = np.clip(vignette, 0.2, 1.0)
        
        # Apply vignette
        result = frame.copy().astype(np.float32)
        for c in range(3):
            result[:, :, c] *= vignette
        
        return np.clip(result, 0, 255).astype(np.uint8)

class VintageEffectsEngine:
    """Enterprise vintage effects engine for retro content creation."""
    
    def __init__(self):
        self.config = VintageConfig()
        self.film_grain = FilmGrain(self.config)
        self.color_grading = ColorGrading(self.config)
        self.vintage_effects = VintageEffects(self.config)
        
    async def apply_vintage_effect(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        vintage_type: str = "film_grain",
        intensity: float = 0.6,
        config: Optional[VintageConfig] = None
    ) -> Dict[str, any]:
        """Apply vintage and retro effects."""
        try:
            if config:
                self.config = config
            else:
                self.config.intensity = intensity
                
            input_path = Path(input_path)
            output_path = Path(output_path)
            
            logger.info(f"Applying {vintage_type} vintage effect: {input_path}")
            
            # Open video
            cap = cv2.VideoCapture(str(input_path))
            if not cap.isOpened():
                raise ValueError(f"Cannot open video file: {input_path}")
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Setup video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
            
            frames_processed = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Apply vintage processing based on type
                if vintage_type == "film_grain":
                    processed_frame = self.film_grain.add_film_grain(frame, intensity)
                elif vintage_type == "70s":
                    processed_frame = self.color_grading.apply_vintage_lut(frame, "70s")
                elif vintage_type == "sepia":
                    # Convert to sepia
                    sepia_filter = np.array([[0.272, 0.534, 0.131],
                                           [0.349, 0.686, 0.168],
                                           [0.393, 0.769, 0.189]])
                    processed_frame = cv2.transform(frame, sepia_filter)
                elif vintage_type == "vignette":
                    processed_frame = self.vintage_effects.add_vignette(frame, intensity)
                else:
                    processed_frame = frame
                
                out.write(processed_frame)
                frames_processed += 1
                
                # Progress logging
                if frames_processed % 100 == 0:
                    progress = (frames_processed / total_frames) * 100
                    logger.info(f"Progress: {progress:.1f}% ({frames_processed}/{total_frames} frames)")
            
            cap.release()
            out.release()
            
            logger.info("Vintage effect applied successfully")
            
            return {
                "success": True,
                "input_path": str(input_path),
                "output_path": str(output_path),
                "vintage_effect_applied": vintage_type,
                "intensity": intensity,
                "frames_processed": frames_processed
            }
            
        except Exception as e:
            logger.error(f"Vintage effect failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "input_path": str(input_path),
                "vintage_type": vintage_type
            }