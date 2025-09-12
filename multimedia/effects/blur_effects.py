"""Blur Effects Engine
Professional blur effects for artistic and cinematic enhancement.

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
class BlurConfig:
    """Configuration for blur effects."""
    blur_type: str = "gaussian"  # gaussian, motion, radial, lens, bokeh
    intensity: float = 5.0  # Blur strength
    quality: str = "high"  # low, medium, high, ultra
    preserve_edges: bool = False  # Edge-preserving blur
    mask_feather: float = 0.1  # Mask edge softness
    iterations: int = 1  # Number of blur passes

class SelectiveBlur:
    """Selective blur effects with masking."""
    
    def __init__(self, config: BlurConfig):
        self.config = config
    
    def depth_of_field_blur(
        self, 
        frame: np.ndarray, 
        focus_point: Tuple[int, int], 
        focus_range: float = 100.0,
        max_blur: float = 15.0
    ) -> np.ndarray:
        """Create depth of field effect with selective focus."""
        h, w = frame.shape[:2]
        fx, fy = focus_point
        
        # Create distance map from focus point
        y, x = np.ogrid[:h, :w]
        distance_map = np.sqrt((x - fx)**2 + (y - fy)**2)
        
        # Normalize distance and create blur strength map
        max_distance = np.sqrt(w**2 + h**2)
        normalized_distance = distance_map / max_distance
        
        # Calculate blur strength based on distance from focus
        blur_strength = np.clip((normalized_distance - focus_range / max_distance) * 3, 0, 1)
        
        # Apply variable blur
        result = frame.copy()
        
        # Create multiple blur levels for smooth transition
        blur_levels = [1, 3, 5, 7, 9, 11, 13, 15]
        
        for i, blur_size in enumerate(blur_levels):
            if blur_size > max_blur:
                break
                
            # Create mask for this blur level
            lower_bound = i / len(blur_levels)
            upper_bound = (i + 1) / len(blur_levels)
            
            mask = (blur_strength >= lower_bound) & (blur_strength < upper_bound)
            
            if np.any(mask):
                # Apply blur to this level
                if blur_size == 1:
                    blurred = frame
                else:
                    blurred = cv2.GaussianBlur(frame, (blur_size*2+1, blur_size*2+1), 0)
                
                result[mask] = blurred[mask]
        
        return result
    
    def tilt_shift_blur(
        self, 
        frame: np.ndarray, 
        focus_line_y: float = 0.5, 
        focus_width: float = 0.2,
        max_blur: float = 12.0
    ) -> np.ndarray:
        """Create tilt-shift miniature effect."""
        h, w = frame.shape[:2]
        
        # Create vertical gradient mask
        center_y = int(focus_line_y * h)
        focus_height = int(focus_width * h)
        
        # Create blur strength map
        y_coords = np.arange(h)
        distance_from_focus = np.abs(y_coords - center_y)
        
        # Normalize and calculate blur strength
        blur_strength = np.clip((distance_from_focus - focus_height/2) / (h/2), 0, 1)
        
        # Apply blur line by line
        result = frame.copy()
        
        for y in range(h):
            blur_level = int(blur_strength[y] * max_blur)
            
            if blur_level > 1:
                # Extract line with padding
                padding = blur_level
                y_start = max(0, y - padding)
                y_end = min(h, y + padding + 1)
                
                line_region = frame[y_start:y_end, :]
                
                # Apply horizontal blur
                if line_region.shape[0] > 0:
                    blurred_region = cv2.GaussianBlur(
                        line_region, (blur_level*2+1, 1), 0
                    )
                    
                    # Extract the target line
                    target_line_idx = y - y_start
                    if 0 <= target_line_idx < blurred_region.shape[0]:
                        result[y, :] = blurred_region[target_line_idx, :]
        
        return result

class MotionBlur:
    """Motion blur effects for dynamic content."""
    
    def __init__(self, config: BlurConfig):
        self.config = config
    
    def linear_motion_blur(
        self, 
        frame: np.ndarray, 
        angle: float, 
        length: int
    ) -> np.ndarray:
        """Apply linear motion blur in specified direction."""
        if length <= 1:
            return frame
        
        # Create motion blur kernel
        kernel = np.zeros((length, length))
        
        # Calculate kernel line based on angle
        center = length // 2
        
        for i in range(length):
            offset_x = int((i - center) * math.cos(math.radians(angle)))
            offset_y = int((i - center) * math.sin(math.radians(angle)))
            
            x = center + offset_x
            y = center + offset_y
            
            if 0 <= x < length and 0 <= y < length:
                kernel[y, x] = 1.0
        
        # Normalize kernel
        kernel = kernel / np.sum(kernel)
        
        # Apply motion blur
        result = cv2.filter2D(frame, -1, kernel)
        
        return result
    
    def radial_motion_blur(
        self, 
        frame: np.ndarray, 
        center: Tuple[int, int], 
        strength: float = 10.0
    ) -> np.ndarray:
        """Apply radial motion blur from center point."""
        h, w = frame.shape[:2]
        cx, cy = center
        
        # Create coordinate grids
        y, x = np.ogrid[:h, :w]
        
        # Calculate angles and distances from center
        angles = np.arctan2(y - cy, x - cx)
        distances = np.sqrt((x - cx)**2 + (y - cy)**2)
        
        # Normalize distances
        max_distance = np.sqrt(w**2 + h**2) / 2
        norm_distances = distances / max_distance
        
        # Apply radial blur
        result = frame.copy().astype(np.float32)
        
        # Create multiple samples along radial lines
        num_samples = max(5, int(strength))
        
        for sample in range(num_samples):
            offset = (sample - num_samples/2) * strength / num_samples
            
            # Calculate offset positions
            offset_x = (offset * np.cos(angles) * norm_distances).astype(int)
            offset_y = (offset * np.sin(angles) * norm_distances).astype(int)
            
            # Clamp to image bounds
            new_x = np.clip(x + offset_x, 0, w - 1)
            new_y = np.clip(y + offset_y, 0, h - 1)
            
            # Sample from offset positions
            for c in range(frame.shape[2]):
                sampled = frame[new_y, new_x, c]
                result[:, :, c] += sampled.astype(np.float32)
        
        # Average all samples
        result = result / num_samples
        
        return np.clip(result, 0, 255).astype(np.uint8)

class ArtisticBlur:
    """Artistic and stylized blur effects."""
    
    def __init__(self, config: BlurConfig):
        self.config = config
    
    def bokeh_blur(
        self, 
        frame: np.ndarray, 
        aperture_shape: str = "hexagon", 
        intensity: float = 10.0
    ) -> np.ndarray:
        """Create bokeh blur effect with custom aperture shapes."""
        # Create custom kernel for bokeh effect
        kernel_size = max(9, int(intensity * 2) | 1)  # Ensure odd size
        
        if aperture_shape == "hexagon":
            kernel = self._create_hexagon_kernel(kernel_size)
        elif aperture_shape == "star":
            kernel = self._create_star_kernel(kernel_size)
        elif aperture_shape == "heart":
            kernel = self._create_heart_kernel(kernel_size)
        else:  # circular (default)
            kernel = self._create_circle_kernel(kernel_size)
        
        # Normalize kernel
        kernel = kernel / np.sum(kernel)
        
        # Apply bokeh blur
        result = cv2.filter2D(frame, -1, kernel)
        
        return result
    
    def _create_hexagon_kernel(self, size: int) -> np.ndarray:
        """Create hexagonal aperture kernel."""
        kernel = np.zeros((size, size))
        center = size // 2
        
        for y in range(size):
            for x in range(size):
                # Hexagon shape approximation
                dx = abs(x - center)
                dy = abs(y - center)
                
                if dx + dy * 0.866 <= center * 0.8:  # Hexagon approximation
                    kernel[y, x] = 1.0
        
        return kernel
    
    def _create_star_kernel(self, size: int) -> np.ndarray:
        """Create star-shaped aperture kernel."""
        kernel = np.zeros((size, size))
        center = size // 2
        
        for y in range(size):
            for x in range(size):
                dx = x - center
                dy = y - center
                angle = math.atan2(dy, dx)
                distance = math.sqrt(dx*dx + dy*dy)
                
                # Create 6-pointed star
                star_radius = center * 0.7 * (1 + 0.3 * math.sin(6 * angle))
                
                if distance <= star_radius:
                    kernel[y, x] = 1.0
        
        return kernel
    
    def _create_heart_kernel(self, size: int) -> np.ndarray:
        """Create heart-shaped aperture kernel."""
        kernel = np.zeros((size, size))
        center = size // 2
        
        for y in range(size):
            for x in range(size):
                # Normalize coordinates to [-1, 1]
                nx = (x - center) / center
                ny = (y - center) / center
                
                # Heart equation: (x²+y²-1)³ - x²y³ = 0
                # Simplified for kernel
                heart_eq = (nx*nx + ny*ny - 0.5)**3 - nx*nx * ny*ny*ny
                
                if heart_eq <= 0 and nx*nx + ny*ny <= 1:
                    kernel[y, x] = 1.0
        
        return kernel
    
    def _create_circle_kernel(self, size: int) -> np.ndarray:
        """Create circular aperture kernel."""
        kernel = np.zeros((size, size))
        center = size // 2
        radius = center * 0.8
        
        for y in range(size):
            for x in range(size):
                distance = math.sqrt((x - center)**2 + (y - center)**2)
                if distance <= radius:
                    kernel[y, x] = 1.0
        
        return kernel
    
    def lens_blur(
        self, 
        frame: np.ndarray, 
        aberration: bool = True, 
        intensity: float = 8.0
    ) -> np.ndarray:
        """Create realistic lens blur with optional chromatic aberration."""
        # Base blur
        blur_size = max(5, int(intensity) | 1)
        result = cv2.GaussianBlur(frame, (blur_size, blur_size), 0)
        
        if aberration:
            # Add chromatic aberration
            h, w = frame.shape[:2]
            
            # Slight channel shifts to simulate chromatic aberration
            shift = max(1, int(intensity * 0.1))
            
            # Split channels
            b, g, r = cv2.split(result)
            
            # Create transformation matrices for slight shifts
            M_r = np.float32([[1, 0, shift], [0, 1, 0]])
            M_b = np.float32([[1, 0, -shift], [0, 1, 0]])
            
            # Apply shifts
            r_shifted = cv2.warpAffine(r, M_r, (w, h))
            b_shifted = cv2.warpAffine(b, M_b, (w, h))
            
            # Recombine channels
            result = cv2.merge([b_shifted, g, r_shifted])
        
        return result

class BlurEffectsEngine:
    """Enterprise blur effects engine for artistic and cinematic enhancement."""
    
    def __init__(self):
        self.config = BlurConfig()
        self.selective = SelectiveBlur(self.config)
        self.motion = MotionBlur(self.config)
        self.artistic = ArtisticBlur(self.config)
        
    async def apply_blur(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        blur_type: str = "gaussian",
        strength: float = 0.5,
        config: Optional[BlurConfig] = None
    ) -> Dict[str, any]:
        """Apply blur effects to video."""
        try:
            if config:
                self.config = config
                
            input_path = Path(input_path)
            output_path = Path(output_path)
            
            # Convert strength to intensity
            intensity = strength * 20.0  # Scale to meaningful blur values
            
            logger.info(f"Applying {blur_type} blur effect: {input_path}")
            
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
                
                # Apply blur effect based on type
                if blur_type == "gaussian":
                    blur_size = max(3, int(intensity) | 1)
                    processed_frame = cv2.GaussianBlur(frame, (blur_size, blur_size), 0)
                    
                elif blur_type == "depth_of_field":
                    focus_point = (width // 2, height // 2)  # Center focus
                    processed_frame = self.selective.depth_of_field_blur(
                        frame, focus_point, focus_range=intensity*10, max_blur=intensity
                    )
                    
                elif blur_type == "tilt_shift":
                    processed_frame = self.selective.tilt_shift_blur(
                        frame, focus_line_y=0.5, focus_width=0.2, max_blur=intensity
                    )
                    
                elif blur_type == "motion_linear":
                    angle = 0  # Horizontal motion blur
                    length = max(3, int(intensity))
                    processed_frame = self.motion.linear_motion_blur(frame, angle, length)
                    
                elif blur_type == "motion_radial":
                    center = (width // 2, height // 2)
                    processed_frame = self.motion.radial_motion_blur(frame, center, intensity)
                    
                elif blur_type == "bokeh":
                    processed_frame = self.artistic.bokeh_blur(
                        frame, aperture_shape="hexagon", intensity=intensity
                    )
                    
                elif blur_type == "bokeh_star":
                    processed_frame = self.artistic.bokeh_blur(
                        frame, aperture_shape="star", intensity=intensity
                    )
                    
                elif blur_type == "lens":
                    processed_frame = self.artistic.lens_blur(
                        frame, aberration=True, intensity=intensity
                    )
                    
                elif blur_type == "median":
                    kernel_size = max(3, int(intensity) | 1)
                    processed_frame = cv2.medianBlur(frame, kernel_size)
                    
                elif blur_type == "surface":
                    # Surface blur (edge-preserving)
                    processed_frame = cv2.bilateralFilter(
                        frame, int(intensity), intensity*10, intensity*10
                    )
                    
                else:
                    logger.warning(f"Unknown blur type: {blur_type}")
                    processed_frame = frame
                
                out.write(processed_frame)
                frames_processed += 1
                
                # Progress logging
                if frames_processed % 100 == 0:
                    progress = (frames_processed / total_frames) * 100
                    logger.info(f"Progress: {progress:.1f}% ({frames_processed}/{total_frames} frames)")
            
            cap.release()
            out.release()
            
            logger.info("Blur effect applied successfully")
            
            return {
                "success": True,
                "input_path": str(input_path),
                "output_path": str(output_path),
                "blur_applied": blur_type,
                "strength": strength,
                "frames_processed": frames_processed
            }
            
        except Exception as e:
            logger.error(f"Blur effect failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "input_path": str(input_path),
                "blur_type": blur_type
            }