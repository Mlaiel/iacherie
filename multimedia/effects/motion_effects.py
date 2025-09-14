"""Motion Effects Engine
Cinematic motion effects and camera movements for professional video content.

Created by: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import numpy as np
import cv2
from typing import Dict, Optional, Union, List, Tuple
from pathlib import Path
from dataclasses import dataclass
import logging
import math

logger = logging.getLogger(__name__)

@dataclass
class MotionEffectsConfig:
    """Configuration for motion effects."""
    output_fps: int = 30
    motion_blur_enabled: bool = True
    stabilization: bool = False
    gpu_acceleration: bool = True
    quality_preset: str = "high"  # low, medium, high, ultra
    easing_type: str = "smooth"  # linear, smooth, bounce, elastic
    keyframe_interpolation: str = "bezier"  # linear, bezier, spline

class CameraMovements:
    """Professional camera movement effects."""
    
    def __init__(self, config -> None: MotionEffectsConfig) -> None:
        self.config = config
    
    def zoom_effect(self, frame: np.ndarray, zoom_factor: float, center: Tuple[int, int] = None) -> np.ndarray:
        """Apply zoom effect with optional custom center point."""
        h, w = frame.shape[:2]
        
        if center is None:
            center = (w // 2, h // 2)
        
        cx, cy = center
        
        # Calculate new dimensions
        new_h = int(h * zoom_factor)
        new_w = int(w * zoom_factor)
        
        if zoom_factor > 1.0:
            # Zoom in - resize and crop
            resized = cv2.resize(frame, (new_w, new_h))
            
            # Calculate crop coordinates
            start_x = max(0, (new_w - w) // 2)
            start_y = max(0, (new_h - h) // 2)
            
            result = resized[start_y:start_y + h, start_x:start_x + w]
            
        else:
            # Zoom out - resize and pad
            resized = cv2.resize(frame, (new_w, new_h))
            
            # Create padded frame
            result = np.zeros_like(frame)
            start_x = (w - new_w) // 2
            start_y = (h - new_h) // 2
            
            result[start_y:start_y + new_h, start_x:start_x + new_w] = resized
        
        return result
    
    def pan_effect(self, frame: np.ndarray, offset_x: int, offset_y: int) -> np.ndarray:
        """Apply panning effect with directional movement."""
        h, w = frame.shape[:2]
        
        # Create transformation matrix
        M = np.float32([[1, 0, offset_x], [0, 1, offset_y]])
        
        # Apply transformation with border reflection
        panned = cv2.warpAffine(frame, M, (w, h), borderMode=cv2.BORDER_REFLECT)
        
        return panned
    
    def tilt_effect(self, frame: np.ndarray, angle: float) -> np.ndarray:
        """Apply tilt/rotation effect."""
        h, w = frame.shape[:2]
        center = (w // 2, h // 2)
        
        # Create rotation matrix
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        
        # Apply rotation
        tilted = cv2.warpAffine(frame, M, (w, h), borderMode=cv2.BORDER_REFLECT)
        
        return tilted
    
    def dolly_zoom_effect(self, frame: np.ndarray, zoom_factor: float, fov_compensation: float = 0.8) -> np.ndarray:
        """Dolly zoom (Vertigo) effect - zoom while maintaining subject size."""
        h, w = frame.shape[:2]
        
        # Apply zoom
        zoomed = self.zoom_effect(frame, zoom_factor)
        
        # Apply barrel distortion to simulate FOV change
        if abs(fov_compensation) > 0.1:
            # Create distortion
            camera_matrix = np.array([[w, 0, w/2], [0, h, h/2], [0, 0, 1]], dtype=np.float32)
            dist_coeffs = np.array([fov_compensation, 0, 0, 0, 0], dtype=np.float32)
            
            undistorted = cv2.undistort(zoomed, camera_matrix, dist_coeffs)
            return undistorted
        
        return zoomed

class KineticEffects:
    """Dynamic kinetic motion effects."""
    
    def __init__(self, config -> None: MotionEffectsConfig) -> None:
        self.config = config
    
    def speed_ramp_effect(self, frames: List[np.ndarray], speed_curve: List[float]) -> List[np.ndarray]:
        """Apply speed ramping with custom speed curves."""
        if len(speed_curve) != len(frames):
            # Interpolate speed curve to match frame count
            speed_curve = np.interp(
                np.linspace(0, len(speed_curve) - 1, len(frames)),
                range(len(speed_curve)),
                speed_curve
            ).tolist()
        
        result_frames = []
        frame_buffer = []
        
        for i, (frame, speed) in enumerate(zip(frames, speed_curve)):
            if speed > 1.0:
                # Fast motion - skip frames
                if i % int(speed) == 0:
                    result_frames.append(frame)
            elif speed < 1.0:
                # Slow motion - interpolate frames
                frame_buffer.append(frame)
                if len(frame_buffer) >= 2:
                    # Create interpolated frames
                    num_interpolated = int(1 / speed) - 1
                    for j in range(num_interpolated + 1):
                        alpha = j / (num_interpolated + 1)
                        interpolated = cv2.addWeighted(
                            frame_buffer[-2], 1 - alpha, frame_buffer[-1], alpha, 0
                        )
                        result_frames.append(interpolated)
                    frame_buffer = [frame_buffer[-1]]
            else:
                # Normal speed
                result_frames.append(frame)
        
        return result_frames
    
    def motion_trail_effect(self, frame: np.ndarray, previous_frames: List[np.ndarray], trail_length: int = 5) -> np.ndarray:
        """Create motion trail effect by blending previous frames."""
        if not previous_frames:
            return frame
        
        result = frame.copy().astype(np.float32)
        
        # Blend with previous frames with decreasing opacity
        for i, prev_frame in enumerate(previous_frames[-trail_length:]):
            alpha = (i + 1) / (trail_length + 1) * 0.3  # Max 30% opacity
            prev_float = prev_frame.astype(np.float32)
            result = cv2.addWeighted(result, 1.0, prev_float, alpha, 0)
        
        return np.clip(result, 0, 255).astype(np.uint8)
    
    def strobe_effect(self, frame: np.ndarray, strobe_intensity: float = 0.5, phase: float = 0.0) -> np.ndarray:
        """Create strobe lighting effect."""
        # Calculate strobe value using sine wave
        strobe_value = (math.sin(phase) + 1) / 2  # Normalize to 0-1
        
        if strobe_value > 0.5:
            # Bright phase
            multiplier = 1.0 + strobe_intensity * (strobe_value - 0.5) * 2
            result = cv2.convertScaleAbs(frame, alpha=multiplier, beta=0)
        else:
            # Dark phase
            multiplier = 1.0 - strobe_intensity * (0.5 - strobe_value) * 2
            result = cv2.convertScaleAbs(frame, alpha=max(multiplier, 0.1), beta=0)
        
        return result

class ParallaxEffects:
    """3D-style parallax and depth effects."""
    
    def __init__(self, config -> None: MotionEffectsConfig) -> None:
        self.config = config
    
    def parallax_effect(self, layers: List[np.ndarray], depths: List[float], movement_x: float, movement_y: float) -> np.ndarray:
        """Create parallax effect with multiple layers at different depths."""
        if not layers or len(layers) != len(depths):
            return layers[0] if layers else np.zeros((480, 640, 3), dtype=np.uint8)
        
        base_layer = layers[0]
        h, w = base_layer.shape[:2]
        result = np.zeros_like(base_layer)
        
        for layer, depth in zip(layers, depths):
            # Calculate offset based on depth (closer objects move more)
            offset_x = int(movement_x * depth)
            offset_y = int(movement_y * depth)
            
            # Apply offset
            M = np.float32([[1, 0, offset_x], [0, 1, offset_y]])
            moved_layer = cv2.warpAffine(layer, M, (w, h), borderMode=cv2.BORDER_TRANSPARENT)
            
            # Blend with result
            mask = cv2.cvtColor(moved_layer, cv2.COLOR_BGR2GRAY)
            mask = mask > 0
            result[mask] = moved_layer[mask]
        
        return result
    
    def depth_of_field_effect(self, frame: np.ndarray, focus_point: Tuple[int, int], focus_range: float = 50.0) -> np.ndarray:
        """Simulate depth of field with selective focus."""
        h, w = frame.shape[:2]
        fx, fy = focus_point
        
        # Create distance map from focus point
        y, x = np.ogrid[:h, :w]
        distance_map = np.sqrt((x - fx)**2 + (y - fy)**2)
        
        # Normalize distance map
        max_distance = np.sqrt(w**2 + h**2)
        normalized_distance = distance_map / max_distance
        
        # Create blur mask (0 = sharp, 1 = blurred)
        blur_strength = np.clip((normalized_distance - focus_range / max_distance) * 3, 0, 1)
        
        # Apply variable blur
        result = frame.copy()
        max_blur = 15
        
        for blur_level in range(1, max_blur + 1, 2):
            mask = (blur_strength >= (blur_level - 1) / max_blur) & (blur_strength < blur_level / max_blur)
            if np.any(mask):
                blurred = cv2.GaussianBlur(frame, (blur_level, blur_level), 0)
                result[mask] = blurred[mask]
        
        return result

class MotionEffectsEngine:
    """Enterprise motion effects engine with cinematic camera movements."""
    
    def __init__(self) -> None:
        self.config = MotionEffectsConfig()
        self.camera_movements = CameraMovements(self.config)
        self.kinetic_effects = KineticEffects(self.config)
        self.parallax_effects = ParallaxEffects(self.config)
        
    async def apply_motion_effect(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        effect_type: str = "zoom",
        intensity: float = 0.5,
        config: Optional[MotionEffectsConfig] = None
    ) -> Dict[str, any]:
        """Apply cinematic motion effects to video."""
        try:
            if config:
                self.config = config
                
            input_path = Path(input_path)
            output_path = Path(output_path)
            
            logger.info(f"Applying {effect_type} motion effect: {input_path}")
            
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
            previous_frames = []
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Calculate animation progress
                progress = frames_processed / max(total_frames - 1, 1)
                
                # Apply easing if configured
                if self.config.easing_type == "smooth":
                    progress = progress * progress * (3.0 - 2.0 * progress)  # Smoothstep
                elif self.config.easing_type == "bounce":
                    progress = 1 - abs(math.sin(progress * math.pi))
                elif self.config.easing_type == "elastic":
                    progress = math.sin(progress * math.pi * 4) * math.exp(-progress * 3) + progress
                
                # Apply motion effect based on type
                if effect_type == "zoom_in":
                    zoom_factor = 1.0 + intensity * progress
                    processed_frame = self.camera_movements.zoom_effect(frame, zoom_factor)
                    
                elif effect_type == "zoom_out":
                    zoom_factor = 1.0 + intensity * (1.0 - progress)
                    processed_frame = self.camera_movements.zoom_effect(frame, zoom_factor)
                    
                elif effect_type == "pan_left":
                    offset_x = int(-intensity * 100 * progress)
                    processed_frame = self.camera_movements.pan_effect(frame, offset_x, 0)
                    
                elif effect_type == "pan_right":
                    offset_x = int(intensity * 100 * progress)
                    processed_frame = self.camera_movements.pan_effect(frame, offset_x, 0)
                    
                elif effect_type == "tilt":
                    angle = intensity * 45 * math.sin(progress * math.pi)
                    processed_frame = self.camera_movements.tilt_effect(frame, angle)
                    
                elif effect_type == "dolly_zoom":
                    zoom_factor = 1.0 + intensity * 0.5 * progress
                    fov_compensation = -intensity * 0.3 * progress
                    processed_frame = self.camera_movements.dolly_zoom_effect(frame, zoom_factor, fov_compensation)
                    
                elif effect_type == "motion_trail":
                    processed_frame = self.kinetic_effects.motion_trail_effect(
                        frame, previous_frames, trail_length=int(5 * intensity)
                    )
                    
                elif effect_type == "strobe":
                    phase = progress * math.pi * 20 * intensity  # More strobes with higher intensity
                    processed_frame = self.kinetic_effects.strobe_effect(frame, intensity, phase)
                    
                elif effect_type == "shake":
                    # Camera shake with random movement
                    max_offset = int(intensity * 20)
                    offset_x = np.random.randint(-max_offset, max_offset + 1)
                    offset_y = np.random.randint(-max_offset, max_offset + 1)
                    processed_frame = self.camera_movements.pan_effect(frame, offset_x, offset_y)
                    
                elif effect_type == "spiral":
                    # Spiral zoom with rotation
                    zoom_factor = 1.0 + intensity * 0.3 * progress
                    angle = intensity * 180 * progress
                    zoomed = self.camera_movements.zoom_effect(frame, zoom_factor)
                    processed_frame = self.camera_movements.tilt_effect(zoomed, angle)
                    
                else:
                    logger.warning(f"Unknown motion effect: {effect_type}")
                    processed_frame = frame
                
                # Add motion blur if enabled
                if self.config.motion_blur_enabled and effect_type in ["pan_left", "pan_right", "shake"]:
                    kernel_size = max(3, int(intensity * 9))
                    kernel = np.ones((1, kernel_size), np.float32) / kernel_size
                    processed_frame = cv2.filter2D(processed_frame, -1, kernel)
                
                out.write(processed_frame)
                
                # Store frame for motion trail effect
                if len(previous_frames) >= 10:
                    previous_frames.pop(0)
                previous_frames.append(frame.copy())
                
                frames_processed += 1
            
            cap.release()
            out.release()
            
            logger.info("Motion effect applied successfully")
            
            return {
                "success": True,
                "input_path": str(input_path),
                "output_path": str(output_path),
                "effect_type": effect_type,
                "intensity": intensity,
                "frames_processed": frames_processed,
                "easing_type": self.config.easing_type,
                "motion_blur_enabled": self.config.motion_blur_enabled
            }
            
        except Exception as e:
            logger.error(f"Motion effect failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "input_path": str(input_path),
                "effect_type": effect_type
            }
    
    async def create_parallax_video(
        self,
        layer_paths: List[Union[str, Path]],
        output_path: Union[str, Path],
        depths: List[float],
        movement_pattern: str = "horizontal",
        config: Optional[MotionEffectsConfig] = None
    ) -> Dict[str, any]:
        """Create parallax effect video from multiple layers."""
        try:
            if config:
                self.config = config
                
            output_path = Path(output_path)
            
            logger.info(f"Creating parallax video: {output_path}")
            
            # Load all layers
            layers = []
            for layer_path in layer_paths:
                layer = cv2.imread(str(layer_path))
                if layer is None:
                    raise ValueError(f"Cannot load layer: {layer_path}")
                layers.append(layer)
            
            if len(layers) != len(depths):
                raise ValueError("Number of layers must match number of depths")
            
            # Get dimensions from first layer
            h, w = layers[0].shape[:2]
            
            # Setup video writer
            fps = self.config.output_fps
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(str(output_path), fourcc, fps, (w, h))
            
            # Generate frames with parallax movement
            duration = 5.0  # 5 seconds
            total_frames = int(fps * duration)
            
            for frame_idx in range(total_frames):
                progress = frame_idx / total_frames
                
                # Calculate movement based on pattern
                if movement_pattern == "horizontal":
                    movement_x = math.sin(progress * math.pi * 2) * 50
                    movement_y = 0
                elif movement_pattern == "vertical":
                    movement_x = 0
                    movement_y = math.sin(progress * math.pi * 2) * 50
                elif movement_pattern == "circular":
                    movement_x = math.sin(progress * math.pi * 2) * 30
                    movement_y = math.cos(progress * math.pi * 2) * 30
                else:
                    movement_x = progress * 100 - 50
                    movement_y = 0
                
                # Generate parallax frame
                frame = self.parallax_effects.parallax_effect(
                    layers, depths, movement_x, movement_y
                )
                
                out.write(frame)
            
            out.release()
            
            logger.info("Parallax video created successfully")
            
            return {
                "success": True,
                "output_path": str(output_path),
                "layers_used": len(layers),
                "movement_pattern": movement_pattern,
                "frames_generated": total_frames,
                "duration": duration
            }
            
        except Exception as e:
            logger.error(f"Parallax video creation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "output_path": str(output_path)
            }