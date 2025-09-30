"""Artistic Filters Engine
Creative artistic filters for unique content creation using AI and traditional methods.

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
class ArtisticConfig:
    """Configuration for artistic filters."""
    style: str = "watercolor"  # watercolor, oil_painting, sketch, cartoon, impressionist
    intensity: float = 0.7  # Filter strength
    color_palette: str = "original"  # original, warm, cool, vibrant, muted
    edge_enhancement: bool = True  # Enhance edges
    texture_strength: float = 0.5  # Texture overlay strength
    abstraction_level: float = 0.5  # Level of abstraction 0-1

class WatercolorFilter:
    """Watercolor painting effect."""
    
    def __init__(self, config: ArtisticConfig):
        self.config = config
    
    def apply_watercolor(self, frame: np.ndarray, intensity: float = 0.7) -> np.ndarray:
        """Apply watercolor painting effect."""
        # Edge-preserving smoothing (bilateral filter)
        smooth = frame.copy()
        for _ in range(int(3 * intensity)):
            smooth = cv2.bilateralFilter(smooth, 9, 200, 200)
        
        # Edge detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 7, 7)
        edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        
        # Combine smooth image with edges
        result = cv2.bitwise_and(smooth, edges)
        
        # Add watercolor texture simulation
        texture = self._create_watercolor_texture(frame.shape, intensity)
        result = cv2.addWeighted(result, 0.8, texture, 0.2 * intensity, 0)
        
        return result
    
    def _create_watercolor_texture(self, shape: Tuple, intensity: float) -> np.ndarray:
        """Create watercolor paper texture."""
        h, w = shape[:2]
        
        # Generate random texture
        texture = np.random.normal(0, 20 * intensity, (h, w, 3))
        
        # Add paper grain
        x, y = np.meshgrid(np.arange(w), np.arange(h))
        paper_grain = np.sin(x * 0.1) * np.cos(y * 0.1) * 10 * intensity
        
        for c in range(3):
            texture[:, :, c] += paper_grain
        
        # Convert to uint8
        texture = np.clip(texture + 128, 0, 255).astype(np.uint8)
        
        return texture

class OilPaintingFilter:
    """Oil painting artistic effect."""
    
    def __init__(self, config: ArtisticConfig):
        self.config = config
    
    def apply_oil_painting(self, frame: np.ndarray, intensity: float = 0.7) -> np.ndarray:
        """Apply oil painting effect."""
        # Use OpenCV's oil painting filter if available
        try:
            radius = max(1, int(7 * intensity))
            dynRatio = max(1, int(20 * intensity))
            result = cv2.xphoto.oilPainting(frame, radius, dynRatio)
        except:
            # Fallback to manual implementation
            result = self._manual_oil_painting(frame, intensity)
        
        return result
    
    def _manual_oil_painting(self, frame: np.ndarray, intensity: float) -> np.ndarray:
        """Manual oil painting implementation."""
        # Reduce colors for painting effect
        data = frame.reshape((-1, 3))
        data = np.float32(data)
        
        # K-means clustering for color reduction
        k = max(8, int(64 * (1 - intensity)))
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
        _, labels, centers = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        
        # Convert back to uint8 and reshape
        centers = np.uint8(centers)
        result = centers[labels.flatten()]
        result = result.reshape(frame.shape)
        
        # Apply brush stroke effect
        kernel = np.ones((3, 3), np.float32) / 9
        result = cv2.filter2D(result, -1, kernel)
        
        return result

class SketchFilter:
    """Pencil sketch and drawing effects."""
    
    def __init__(self, config: ArtisticConfig):
        self.config = config
    
    def apply_pencil_sketch(self, frame: np.ndarray, intensity: float = 0.7) -> np.ndarray:
        """Apply pencil sketch effect."""
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Invert the image
        gray_inv = 255 - gray
        
        # Apply Gaussian blur
        blur_value = max(21, int(21 * intensity))
        if blur_value % 2 == 0:
            blur_value += 1
        
        gray_inv_blur = cv2.GaussianBlur(gray_inv, (blur_value, blur_value), 0)
        
        # Create the sketch
        sketch = cv2.divide(gray, 255 - gray_inv_blur, scale=256)
        
        # Convert back to BGR
        sketch_bgr = cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)
        
        # Blend with original for color sketch
        if intensity < 0.8:
            sketch_bgr = cv2.addWeighted(frame, 1 - intensity, sketch_bgr, intensity, 0)
        
        return sketch_bgr
    
    def apply_crosshatch_sketch(self, frame: np.ndarray, intensity: float = 0.7) -> np.ndarray:
        """Apply crosshatch sketch effect."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Create crosshatch patterns
        h, w = gray.shape
        
        # Horizontal lines
        horizontal = np.zeros_like(gray)
        for y in range(0, h, max(1, int(8 / intensity))):
            horizontal[y, :] = 255
        
        # Vertical lines
        vertical = np.zeros_like(gray)
        for x in range(0, w, max(1, int(8 / intensity))):
            vertical[:, x] = 255
        
        # Diagonal lines
        diagonal1 = np.zeros_like(gray)
        diagonal2 = np.zeros_like(gray)
        
        for i in range(min(h, w)):
            step = max(1, int(12 / intensity))
            for j in range(0, max(h, w), step):
                if i + j < h and j < w:
                    diagonal1[i + j, j] = 255
                if j - i >= 0 and j - i < h and j < w:
                    diagonal2[j - i, j] = 255
        
        # Combine patterns based on image intensity
        crosshatch = np.zeros_like(gray)
        
        # Use different patterns for different brightness levels
        dark_mask = gray < 85
        medium_mask = (gray >= 85) & (gray < 170)
        light_mask = gray >= 170
        
        crosshatch[dark_mask] = np.minimum.reduce([
            horizontal[dark_mask], vertical[dark_mask], 
            diagonal1[dark_mask], diagonal2[dark_mask]
        ])
        crosshatch[medium_mask] = np.minimum(
            horizontal[medium_mask], vertical[medium_mask]
        )
        crosshatch[light_mask] = horizontal[light_mask]
        
        # Convert to BGR
        result = cv2.cvtColor(255 - crosshatch, cv2.COLOR_GRAY2BGR)
        
        return result

class ImpressionistFilter:
    """Impressionist painting style effects."""
    
    def __init__(self, config: ArtisticConfig):
        self.config = config
    
    def apply_impressionist(self, frame: np.ndarray, intensity: float = 0.7) -> np.ndarray:
        """Apply impressionist painting effect."""
        # Create brush strokes effect
        h, w = frame.shape[:2]
        result = frame.copy()
        
        # Number of brush strokes
        num_strokes = int(1000 * intensity)
        
        for _ in range(num_strokes):
            # Random brush stroke parameters
            x = np.random.randint(0, w)
            y = np.random.randint(0, h)
            
            # Brush stroke size and direction
            length = np.random.randint(5, 20)
            angle = np.random.uniform(0, 2 * math.pi)
            thickness = np.random.randint(1, 4)
            
            # End point of stroke
            end_x = int(x + length * math.cos(angle))
            end_y = int(y + length * math.sin(angle))
            
            # Ensure within bounds
            end_x = max(0, min(w - 1, end_x))
            end_y = max(0, min(h - 1, end_y))
            
            # Get color from original image
            color = tuple(map(int, frame[y, x]))
            
            # Add some color variation
            color = tuple(max(0, min(255, c + np.random.randint(-20, 21))) for c in color)
            
            # Draw brush stroke
            cv2.line(result, (x, y), (end_x, end_y), color, thickness)
        
        # Blend with original
        result = cv2.addWeighted(frame, 1 - intensity, result, intensity, 0)
        
        return result

class ColorPaletteProcessor:
    """Color palette transformations for artistic effects."""
    
    def __init__(self, config: ArtisticConfig):
        self.config = config
    
    def apply_color_palette(self, frame: np.ndarray, palette_type: str = "warm") -> np.ndarray:
        """Apply artistic color palette."""
        result = frame.copy().astype(np.float32)
        
        if palette_type == "warm":
            # Warm color palette
            result[:, :, 0] *= 0.8   # Reduce blue
            result[:, :, 1] *= 1.1   # Enhance green
            result[:, :, 2] *= 1.3   # Boost red
            
        elif palette_type == "cool":
            # Cool color palette
            result[:, :, 0] *= 1.3   # Boost blue
            result[:, :, 1] *= 1.0   # Keep green
            result[:, :, 2] *= 0.8   # Reduce red
            
        elif palette_type == "vibrant":
            # Vibrant colors
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            hsv[:, :, 1] = cv2.multiply(hsv[:, :, 1], 1.4)  # Increase saturation
            result = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR).astype(np.float32)
            
        elif palette_type == "muted":
            # Muted colors
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            hsv[:, :, 1] = cv2.multiply(hsv[:, :, 1], 0.6)  # Decrease saturation
            result = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR).astype(np.float32)
            
        elif palette_type == "sepia":
            # Sepia tone
            sepia_filter = np.array([[0.272, 0.534, 0.131],
                                   [0.349, 0.686, 0.168],
                                   [0.393, 0.769, 0.189]])
            result = cv2.transform(frame, sepia_filter).astype(np.float32)
        
        return np.clip(result, 0, 255).astype(np.uint8)

class ArtisticFiltersEngine:
    """Enterprise artistic filters engine for creative content enhancement."""
    
    def __init__(self):
        self.config = ArtisticConfig()
        self.watercolor = WatercolorFilter(self.config)
        self.oil_painting = OilPaintingFilter(self.config)
        self.sketch = SketchFilter(self.config)
        self.impressionist = ImpressionistFilter(self.config)
        self.color_palette = ColorPaletteProcessor(self.config)
        
    async def apply_artistic_filter(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        filter_type: str = "watercolor",
        strength: float = 0.7,
        config: Optional[ArtisticConfig] = None
    ) -> Dict[str, any]:
        """Apply artistic filters for creative content."""
        try:
            if config:
                self.config = config
            else:
                self.config.intensity = strength
                
            input_path = Path(input_path)
            output_path = Path(output_path)
            
            logger.info(f"Applying {filter_type} artistic filter: {input_path}")
            
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
                
                # Apply artistic filter based on type
                if filter_type == "watercolor":
                    processed_frame = self.watercolor.apply_watercolor(frame, strength)
                    
                elif filter_type == "oil_painting":
                    processed_frame = self.oil_painting.apply_oil_painting(frame, strength)
                    
                elif filter_type == "pencil_sketch":
                    processed_frame = self.sketch.apply_pencil_sketch(frame, strength)
                    
                elif filter_type == "crosshatch":
                    processed_frame = self.sketch.apply_crosshatch_sketch(frame, strength)
                    
                elif filter_type == "impressionist":
                    processed_frame = self.impressionist.apply_impressionist(frame, strength)
                    
                elif filter_type == "color_reduction":
                    # Posterization effect
                    data = frame.reshape((-1, 3))
                    data = np.float32(data)
                    
                    k = max(4, int(32 * (1 - strength)))
                    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
                    _, labels, centers = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
                    
                    centers = np.uint8(centers)
                    processed_frame = centers[labels.flatten()].reshape(frame.shape)
                    
                else:
                    logger.warning(f"Unknown artistic filter: {filter_type}")
                    processed_frame = frame
                
                # Apply color palette if configured
                if self.config.color_palette != "original":
                    processed_frame = self.color_palette.apply_color_palette(
                        processed_frame, self.config.color_palette
                    )
                
                out.write(processed_frame)
                frames_processed += 1
                
                # Progress logging
                if frames_processed % 100 == 0:
                    progress = (frames_processed / total_frames) * 100
                    logger.info(f"Progress: {progress:.1f}% ({frames_processed}/{total_frames} frames)")
            
            cap.release()
            out.release()
            
            logger.info("Artistic filter applied successfully")
            
            return {
                "success": True,
                "input_path": str(input_path),
                "output_path": str(output_path),
                "artistic_filter_applied": filter_type,
                "strength": strength,
                "frames_processed": frames_processed,
                "color_palette": self.config.color_palette
            }
            
        except Exception as e:
            logger.error(f"Artistic filter failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "input_path": str(input_path),
                "filter_type": filter_type
            }