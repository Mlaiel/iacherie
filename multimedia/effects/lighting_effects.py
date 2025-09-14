"""Lighting Effects Engine
Professional lighting effects for cinematic video enhancement.

Created by: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import numpy as np
import cv2
import math
from typing import Dict, Optional, Union, List, Tuple
from pathlib import Path
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class LightSource:
    """Configuration for a light source."""
    position: Tuple[float, float] = (0.5, 0.5)  # Normalized coordinates (0-1)
    intensity: float = 1.0  # 0.0 to 2.0
    color: Tuple[int, int, int] = (255, 255, 255)
    falloff: float = 1.0  # How quickly light fades with distance
    radius: float = 0.3  # Normalized radius (0-1)
    softness: float = 0.5  # Edge softness
    light_type: str = "point"  # point, directional, spot, area

@dataclass
class LightingConfig:
    """Configuration for lighting effects."""
    ambient_light: float = 0.2  # Global ambient lighting
    contrast_boost: float = 1.2  # Contrast enhancement
    saturation_boost: float = 1.1  # Color saturation
    temperature_shift: float = 0.0  # Color temperature (-1 to 1)
    vignette_strength: float = 0.0  # Vignette effect
    bloom_enabled: bool = True  # Bloom effect
    bloom_threshold: float = 200.0  # Brightness threshold for bloom
    bloom_intensity: float = 0.3  # Bloom effect intensity

class VolumetricLighting:
    """Volumetric lighting effects (god rays, fog beams)."""
    
    def __init__(self, config -> None: LightingConfig) -> None:
        self.config = config
    
    def create_god_rays(
        self, 
        frame: np.ndarray, 
        light_source: Tuple[int, int], 
        intensity: float = 0.5,
        num_rays: int = 50,
        ray_length: float = 0.8
    ) -> np.ndarray:
        """Create god rays effect from a light source."""
        h, w = frame.shape[:2]
        result = frame.copy().astype(np.float32)
        
        # Create rays mask
        rays_mask = np.zeros((h, w), dtype=np.float32)
        
        # Light source position
        lx, ly = light_source
        
        # Generate rays
        for i in range(num_rays):
            angle = (i / num_rays) * 2 * math.pi
            
            # Calculate ray endpoints
            ray_end_x = lx + int(math.cos(angle) * ray_length * min(w, h))
            ray_end_y = ly + int(math.sin(angle) * ray_length * min(w, h))
            
            # Draw ray line
            cv2.line(rays_mask, (lx, ly), (ray_end_x, ray_end_y), 1.0, 1)
        
        # Blur the rays for soft effect
        rays_mask = cv2.GaussianBlur(rays_mask, (21, 21), 0)
        
        # Apply rays to frame
        for c in range(3):
            result[:, :, c] += rays_mask * intensity * 50
        
        return np.clip(result, 0, 255).astype(np.uint8)
    
    def create_fog_beams(
        self,
        frame: np.ndarray,
        beam_sources: List[Tuple[int, int]],
        beam_angles: List[float],
        intensity: float = 0.3
    ) -> np.ndarray:
        """Create fog beam effects from multiple sources."""
        h, w = frame.shape[:2]
        result = frame.copy().astype(np.float32)
        
        for (bx, by), angle in zip(beam_sources, beam_angles):
            # Create beam mask
            beam_mask = np.zeros((h, w), dtype=np.float32)
            
            # Beam parameters
            beam_width = 60  # degrees
            beam_length = min(w, h)
            
            # Create beam cone
            for r in range(0, beam_length, 5):
                for a in range(-beam_width//2, beam_width//2, 2):
                    ray_angle = math.radians(angle + a)
                    x = bx + int(r * math.cos(ray_angle))
                    y = by + int(r * math.sin(ray_angle))
                    
                    if 0 <= x < w and 0 <= y < h:
                        # Falloff with distance and angle
                        distance_falloff = 1.0 - (r / beam_length)
                        angle_falloff = 1.0 - (abs(a) / (beam_width/2))
                        beam_mask[y, x] = distance_falloff * angle_falloff
            
            # Blur for soft edges
            beam_mask = cv2.GaussianBlur(beam_mask, (15, 15), 0)
            
            # Apply beam to frame
            for c in range(3):
                result[:, :, c] += beam_mask * intensity * 100
        
        return np.clip(result, 0, 255).astype(np.uint8)

class DynamicLighting:
    """Dynamic lighting effects that change over time."""
    
    def __init__(self, config -> None: LightingConfig) -> None:
        self.config = config
    
    def flickering_light(
        self,
        frame: np.ndarray,
        light_source: LightSource,
        flicker_frequency: float = 5.0,
        time: float = 0.0
    ) -> np.ndarray:
        """Create flickering light effect."""
        # Calculate flicker intensity using sine wave with noise
        base_flicker = math.sin(time * flicker_frequency * 2 * math.pi)
        noise = np.random.normal(0, 0.1)
        flicker_intensity = light_source.intensity * (0.7 + 0.3 * base_flicker + noise)
        flicker_intensity = max(0.1, min(2.0, flicker_intensity))
        
        # Create modified light source
        flickering_source = LightSource(
            position=light_source.position,
            intensity=flicker_intensity,
            color=light_source.color,
            falloff=light_source.falloff,
            radius=light_source.radius,
            softness=light_source.softness
        )
        
        return self.apply_point_light(frame, flickering_source)
    
    def pulsing_light(
        self,
        frame: np.ndarray,
        light_source: LightSource,
        pulse_frequency: float = 2.0,
        time: float = 0.0
    ) -> np.ndarray:
        """Create smooth pulsing light effect."""
        # Calculate pulse intensity
        pulse_value = (math.sin(time * pulse_frequency * 2 * math.pi) + 1) / 2
        pulse_intensity = light_source.intensity * (0.5 + 0.5 * pulse_value)
        
        # Create modified light source
        pulsing_source = LightSource(
            position=light_source.position,
            intensity=pulse_intensity,
            color=light_source.color,
            falloff=light_source.falloff,
            radius=light_source.radius * (0.8 + 0.4 * pulse_value),
            softness=light_source.softness
        )
        
        return self.apply_point_light(frame, pulsing_source)
    
    def apply_point_light(self, frame: np.ndarray, light_source: LightSource) -> np.ndarray:
        """Apply a single point light to the frame."""
        h, w = frame.shape[:2]
        result = frame.copy().astype(np.float32)
        
        # Convert normalized position to pixel coordinates
        lx = int(light_source.position[0] * w)
        ly = int(light_source.position[1] * h)
        
        # Create distance map
        y, x = np.ogrid[:h, :w]
        distance_map = np.sqrt((x - lx)**2 + (y - ly)**2)
        
        # Normalize distance
        max_distance = light_source.radius * min(w, h)
        normalized_distance = np.clip(distance_map / max_distance, 0, 1)
        
        # Calculate light falloff
        light_mask = (1 - normalized_distance) ** light_source.falloff
        light_mask = np.clip(light_mask, 0, 1)
        
        # Apply softness
        if light_source.softness > 0:
            kernel_size = int(light_source.softness * 20) | 1  # Ensure odd
            light_mask = cv2.GaussianBlur(light_mask, (kernel_size, kernel_size), 0)
        
        # Apply light color and intensity
        light_r, light_g, light_b = light_source.color
        intensity = light_source.intensity
        
        result[:, :, 0] += light_mask * light_b * intensity
        result[:, :, 1] += light_mask * light_g * intensity
        result[:, :, 2] += light_mask * light_r * intensity
        
        return np.clip(result, 0, 255).astype(np.uint8)

class ColorTemperature:
    """Color temperature and mood lighting effects."""
    
    def __init__(self, config -> None: LightingConfig) -> None:
        self.config = config
    
    def apply_color_temperature(self, frame: np.ndarray, temperature: float) -> np.ndarray:
        """Apply color temperature shift (-1 = cool, +1 = warm)."""
        result = frame.copy().astype(np.float32)
        
        if temperature > 0:
            # Warm temperature (more red/yellow)
            result[:, :, 0] *= (1 - temperature * 0.2)  # Reduce blue
            result[:, :, 1] *= (1 + temperature * 0.1)  # Slight green
            result[:, :, 2] *= (1 + temperature * 0.3)  # Increase red
        else:
            # Cool temperature (more blue)
            temp = abs(temperature)
            result[:, :, 0] *= (1 + temp * 0.3)  # Increase blue
            result[:, :, 1] *= (1 + temp * 0.1)  # Slight green
            result[:, :, 2] *= (1 - temp * 0.2)  # Reduce red
        
        return np.clip(result, 0, 255).astype(np.uint8)
    
    def golden_hour_effect(self, frame: np.ndarray, intensity: float = 0.7) -> np.ndarray:
        """Apply golden hour lighting effect."""
        # Apply warm color temperature
        warm_frame = self.apply_color_temperature(frame, intensity * 0.8)
        
        # Add soft glow
        blurred = cv2.GaussianBlur(warm_frame, (21, 21), 0)
        result = cv2.addWeighted(warm_frame, 0.8, blurred, 0.2 * intensity, 0)
        
        # Enhance contrast slightly
        result = cv2.convertScaleAbs(result, alpha=1.1, beta=0)
        
        return result
    
    def blue_hour_effect(self, frame: np.ndarray, intensity: float = 0.6) -> np.ndarray:
        """Apply blue hour lighting effect."""
        # Apply cool color temperature
        cool_frame = self.apply_color_temperature(frame, -intensity * 0.7)
        
        # Reduce overall brightness slightly
        result = cv2.convertScaleAbs(cool_frame, alpha=0.9, beta=0)
        
        # Add subtle blue glow
        blue_mask = np.zeros_like(result, dtype=np.float32)
        blue_mask[:, :, 0] = 20 * intensity  # Blue channel
        
        result = cv2.addWeighted(result, 1.0, blue_mask.astype(np.uint8), 1.0, 0)
        
        return result

class AdvancedEffects:
    """Advanced lighting effects and post-processing."""
    
    def __init__(self, config -> None: LightingConfig) -> None:
        self.config = config
    
    def lens_flare_effect(
        self,
        frame: np.ndarray,
        light_position: Tuple[int, int],
        intensity: float = 0.8
    ) -> np.ndarray:
        """Create lens flare effect."""
        h, w = frame.shape[:2]
        result = frame.copy().astype(np.float32)
        
        lx, ly = light_position
        
        # Create multiple flare elements
        flare_elements = [
            {"pos": (lx, ly), "size": 20, "intensity": intensity, "color": (255, 255, 200)},
            {"pos": (lx - 50, ly + 30), "size": 15, "intensity": intensity * 0.6, "color": (200, 150, 255)},
            {"pos": (lx + 80, ly - 20), "size": 10, "intensity": intensity * 0.4, "color": (255, 200, 150)},
            {"pos": (lx - 30, ly - 40), "size": 8, "intensity": intensity * 0.3, "color": (150, 255, 200)}
        ]
        
        for element in flare_elements:
            ex, ey = element["pos"]
            size = element["size"]
            elem_intensity = element["intensity"]
            color = element["color"]
            
            if 0 <= ex < w and 0 <= ey < h:
                # Create flare element
                overlay = np.zeros_like(result)
                cv2.circle(overlay, (ex, ey), size, color, -1)
                
                # Apply Gaussian blur for soft glow
                overlay = cv2.GaussianBlur(overlay, (size*2+1, size*2+1), 0)
                
                # Blend with result
                result = cv2.addWeighted(result, 1.0, overlay, elem_intensity, 0)
        
        return np.clip(result, 0, 255).astype(np.uint8)
    
    def bloom_effect(self, frame: np.ndarray, threshold: float = 200.0, intensity: float = 0.3) -> np.ndarray:
        """Apply bloom effect to bright areas."""
        # Convert to grayscale to find bright areas
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Create mask for bright areas
        _, bright_mask = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
        
        # Apply mask to original frame
        bright_areas = cv2.bitwise_and(frame, frame, mask=bright_mask)
        
        # Create bloom by heavily blurring bright areas
        bloom = cv2.GaussianBlur(bright_areas, (51, 51), 0)
        
        # Blend bloom with original
        result = cv2.addWeighted(frame, 1.0, bloom, intensity, 0)
        
        return result
    
    def vignette_effect(self, frame: np.ndarray, strength: float = 0.5) -> np.ndarray:
        """Apply vignette effect."""
        h, w = frame.shape[:2]
        
        # Create vignette mask
        center_x, center_y = w // 2, h // 2
        Y, X = np.ogrid[:h, :w]
        dist_from_center = np.sqrt((X - center_x)**2 + (Y - center_y)**2)
        max_dist = np.sqrt(center_x**2 + center_y**2)
        
        # Normalize and invert
        vignette = 1 - (dist_from_center / max_dist) * strength
        vignette = np.clip(vignette, 0.2, 1.0)
        
        # Apply vignette
        result = frame.copy().astype(np.float32)
        for c in range(3):
            result[:, :, c] *= vignette
        
        return np.clip(result, 0, 255).astype(np.uint8)

class LightingEffectsEngine:
    """Enterprise lighting effects engine for professional cinematic enhancement."""
    
    def __init__(self) -> None:
        self.config = LightingConfig()
        self.volumetric = VolumetricLighting(self.config)
        self.dynamic = DynamicLighting(self.config)
        self.color_temp = ColorTemperature(self.config)
        self.advanced = AdvancedEffects(self.config)
        
    async def adjust_lighting(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        lighting_type: str = "golden_hour",
        intensity: float = 0.7,
        config: Optional[LightingConfig] = None
    ) -> Dict[str, any]:
        """Apply professional lighting effects to video."""
        try:
            if config:
                self.config = config
                
            input_path = Path(input_path)
            output_path = Path(output_path)
            
            logger.info(f"Applying {lighting_type} lighting effect: {input_path}")
            
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
                
                # Calculate time for animated effects
                time = frames_processed / fps
                
                # Apply lighting effect based on type
                if lighting_type == "golden_hour":
                    processed_frame = self.color_temp.golden_hour_effect(frame, intensity)
                    
                elif lighting_type == "blue_hour":
                    processed_frame = self.color_temp.blue_hour_effect(frame, intensity)
                    
                elif lighting_type == "god_rays":
                    light_pos = (width // 3, height // 4)  # Top-left area
                    processed_frame = self.volumetric.create_god_rays(
                        frame, light_pos, intensity, num_rays=30
                    )
                    
                elif lighting_type == "flickering":
                    light_source = LightSource(
                        position=(0.3, 0.3), intensity=intensity,
                        color=(255, 200, 100), radius=0.4
                    )
                    processed_frame = self.dynamic.flickering_light(
                        frame, light_source, flicker_frequency=8.0, time=time
                    )
                    
                elif lighting_type == "pulsing":
                    light_source = LightSource(
                        position=(0.5, 0.3), intensity=intensity,
                        color=(100, 150, 255), radius=0.5
                    )
                    processed_frame = self.dynamic.pulsing_light(
                        frame, light_source, pulse_frequency=1.5, time=time
                    )
                    
                elif lighting_type == "lens_flare":
                    light_pos = (int(width * 0.8), int(height * 0.2))
                    processed_frame = self.advanced.lens_flare_effect(frame, light_pos, intensity)
                    
                elif lighting_type == "bloom":
                    processed_frame = self.advanced.bloom_effect(
                        frame, threshold=180, intensity=intensity
                    )
                    
                elif lighting_type == "vignette":
                    processed_frame = self.advanced.vignette_effect(frame, intensity)
                    
                elif lighting_type == "warm":
                    processed_frame = self.color_temp.apply_color_temperature(frame, intensity)
                    
                elif lighting_type == "cool":
                    processed_frame = self.color_temp.apply_color_temperature(frame, -intensity)
                    
                elif lighting_type == "fog_beams":
                    beam_sources = [(width // 4, 0), (3 * width // 4, 0)]
                    beam_angles = [45, 135]
                    processed_frame = self.volumetric.create_fog_beams(
                        frame, beam_sources, beam_angles, intensity
                    )
                    
                else:
                    logger.warning(f"Unknown lighting effect: {lighting_type}")
                    processed_frame = frame
                
                # Apply post-processing if enabled
                if self.config.bloom_enabled and lighting_type != "bloom":
                    processed_frame = self.advanced.bloom_effect(
                        processed_frame, self.config.bloom_threshold, self.config.bloom_intensity
                    )
                
                if self.config.vignette_strength > 0:
                    processed_frame = self.advanced.vignette_effect(
                        processed_frame, self.config.vignette_strength
                    )
                
                out.write(processed_frame)
                frames_processed += 1
                
                # Progress logging
                if frames_processed % 100 == 0:
                    progress = (frames_processed / total_frames) * 100
                    logger.info(f"Progress: {progress:.1f}% ({frames_processed}/{total_frames} frames)")
            
            cap.release()
            out.release()
            
            logger.info("Lighting effect applied successfully")
            
            return {
                "success": True,
                "input_path": str(input_path),
                "output_path": str(output_path),
                "lighting_applied": lighting_type,
                "intensity": intensity,
                "frames_processed": frames_processed,
                "config_applied": {
                    "bloom_enabled": self.config.bloom_enabled,
                    "vignette_strength": self.config.vignette_strength,
                    "ambient_light": self.config.ambient_light
                }
            }
            
        except Exception as e:
            logger.error(f"Lighting effect failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "input_path": str(input_path),
                "lighting_type": lighting_type
            }