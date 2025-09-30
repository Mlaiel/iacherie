"""Video Effects Engine
Professional video effects including transitions, overlays, and cinematic enhancements.

Created by: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import numpy as np
import cv2
from typing import Dict, Optional, Union, List, Tuple
from pathlib import Path
from dataclasses import dataclass
import logging
import tempfile
import subprocess

logger = logging.getLogger(__name__)

@dataclass
class VideoEffectsConfig:
    """Configuration for video effects."""
    output_fps: int = 30
    output_resolution: Tuple[int, int] = (1920, 1080)
    quality_preset: str = "high"  # low, medium, high, ultra
    transition_duration: float = 1.0  # seconds
    overlay_opacity: float = 0.7  # 0.0 to 1.0
    motion_blur_enabled: bool = True
    color_correction: bool = True
    stabilization: bool = False
    gpu_acceleration: bool = True
    output_format: str = "mp4"
    codec: str = "h264"

class TransitionEngine:
    """Professional transition effects between video clips."""
    
    def __init__(self, config: VideoEffectsConfig):
        self.config = config
        
    def fade_transition(self, frame1: np.ndarray, frame2: np.ndarray, progress: float) -> np.ndarray:
        """Smooth fade transition between two frames."""
        alpha = progress
        return cv2.addWeighted(frame1, 1 - alpha, frame2, alpha, 0)
    
    def slide_transition(self, frame1: np.ndarray, frame2: np.ndarray, progress: float, direction: str = "left") -> np.ndarray:
        """Slide transition with directional movement."""
        h, w = frame1.shape[:2]
        
        if direction == "left":
            offset = int(w * progress)
            result = np.zeros_like(frame1)
            
            # Slide frame2 in from right
            if offset < w:
                result[:, :w-offset] = frame1[:, offset:]
                result[:, w-offset:] = frame2[:, :offset]
            else:
                result = frame2
                
        elif direction == "right":
            offset = int(w * progress)
            result = np.zeros_like(frame1)
            
            # Slide frame2 in from left
            if offset < w:
                result[:, offset:] = frame1[:, :w-offset]
                result[:, :offset] = frame2[:, w-offset:]
            else:
                result = frame2
                
        elif direction == "up":
            offset = int(h * progress)
            result = np.zeros_like(frame1)
            
            if offset < h:
                result[offset:, :] = frame1[:h-offset, :]
                result[:offset, :] = frame2[h-offset:, :]
            else:
                result = frame2
                
        elif direction == "down":
            offset = int(h * progress)
            result = np.zeros_like(frame1)
            
            if offset < h:
                result[:h-offset, :] = frame1[offset:, :]
                result[h-offset:, :] = frame2[:offset, :]
            else:
                result = frame2
        else:
            result = self.fade_transition(frame1, frame2, progress)
            
        return result
    
    def zoom_transition(self, frame1: np.ndarray, frame2: np.ndarray, progress: float) -> np.ndarray:
        """Zoom transition effect."""
        h, w = frame1.shape[:2]
        
        # Zoom out frame1
        zoom_factor1 = 1.0 + progress * 0.5
        new_h1 = int(h * zoom_factor1)
        new_w1 = int(w * zoom_factor1)
        
        if new_h1 > 0 and new_w1 > 0:
            zoomed1 = cv2.resize(frame1, (new_w1, new_h1))
            
            # Center crop
            y_start = max(0, (new_h1 - h) // 2)
            x_start = max(0, (new_w1 - w) // 2)
            cropped1 = zoomed1[y_start:y_start+h, x_start:x_start+w]
        else:
            cropped1 = frame1
        
        # Zoom in frame2
        zoom_factor2 = 0.5 + progress * 0.5
        new_h2 = int(h * zoom_factor2)
        new_w2 = int(w * zoom_factor2)
        
        if new_h2 > 0 and new_w2 > 0:
            resized2 = cv2.resize(frame2, (new_w2, new_h2))
            
            # Center pad
            cropped2 = np.zeros_like(frame2)
            y_start = max(0, (h - new_h2) // 2)
            x_start = max(0, (w - new_w2) // 2)
            cropped2[y_start:y_start+new_h2, x_start:x_start+new_w2] = resized2
        else:
            cropped2 = frame2
        
        # Blend
        alpha = progress
        return cv2.addWeighted(cropped1, 1 - alpha, cropped2, alpha, 0)
    
    def wipe_transition(self, frame1: np.ndarray, frame2: np.ndarray, progress: float, direction: str = "horizontal") -> np.ndarray:
        """Wipe transition effect."""
        h, w = frame1.shape[:2]
        result = frame1.copy()
        
        if direction == "horizontal":
            split_pos = int(w * progress)
            if split_pos > 0:
                result[:, :split_pos] = frame2[:, :split_pos]
        elif direction == "vertical":
            split_pos = int(h * progress)
            if split_pos > 0:
                result[:split_pos, :] = frame2[:split_pos, :]
        elif direction == "diagonal":
            for y in range(h):
                split_pos = int(w * progress + (y / h) * w * 0.2)
                if split_pos > 0 and split_pos <= w:
                    result[y, :split_pos] = frame2[y, :split_pos]
        
        return result

class OverlayEngine:
    """Professional overlay effects for videos."""
    
    def __init__(self, config: VideoEffectsConfig):
        self.config = config
    
    def add_text_overlay(
        self, 
        frame: np.ndarray, 
        text: str, 
        position: Tuple[int, int], 
        font_scale: float = 1.0,
        color: Tuple[int, int, int] = (255, 255, 255),
        thickness: int = 2
    ) -> np.ndarray:
        """Add text overlay to frame."""
        result = frame.copy()
        
        # Add background rectangle for better readability
        (text_width, text_height), baseline = cv2.getTextSize(
            text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness
        )
        
        # Draw background rectangle
        cv2.rectangle(
            result,
            (position[0] - 5, position[1] - text_height - 5),
            (position[0] + text_width + 5, position[1] + baseline + 5),
            (0, 0, 0, 128),  # Semi-transparent black
            -1
        )
        
        # Draw text
        cv2.putText(
            result,
            text,
            position,
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            color,
            thickness,
            cv2.LINE_AA
        )
        
        return result
    
    def add_image_overlay(
        self, 
        background: np.ndarray, 
        overlay: np.ndarray, 
        position: Tuple[int, int],
        opacity: float = 0.7
    ) -> np.ndarray:
        """Add image overlay with alpha blending."""
        result = background.copy()
        h, w = background.shape[:2]
        oh, ow = overlay.shape[:2]
        
        x, y = position
        
        # Check bounds
        if x >= 0 and y >= 0 and x + ow <= w and y + oh <= h:
            # Simple alpha blending
            roi = result[y:y+oh, x:x+ow]
            blended = cv2.addWeighted(roi, 1 - opacity, overlay, opacity, 0)
            result[y:y+oh, x:x+ow] = blended
        
        return result
    
    def add_watermark(
        self, 
        frame: np.ndarray, 
        watermark: np.ndarray, 
        position: str = "bottom_right",
        opacity: float = 0.3,
        margin: int = 20
    ) -> np.ndarray:
        """Add watermark to frame."""
        h, w = frame.shape[:2]
        wh, ww = watermark.shape[:2]
        
        # Calculate position
        if position == "top_left":
            x, y = margin, margin
        elif position == "top_right":
            x, y = w - ww - margin, margin
        elif position == "bottom_left":
            x, y = margin, h - wh - margin
        elif position == "bottom_right":
            x, y = w - ww - margin, h - wh - margin
        elif position == "center":
            x, y = (w - ww) // 2, (h - wh) // 2
        else:
            x, y = margin, h - wh - margin  # default to bottom_left
        
        return self.add_image_overlay(frame, watermark, (x, y), opacity)

class ColorGradingEngine:
    """Professional color grading and correction."""
    
    def __init__(self, config: VideoEffectsConfig):
        self.config = config
    
    def apply_lut(self, frame: np.ndarray, lut: np.ndarray) -> np.ndarray:
        """Apply Look-Up Table for color grading."""
        # Ensure LUT is in correct format
        if lut.shape != (256, 256, 256, 3):
            logger.warning("Invalid LUT format, skipping color grading")
            return frame
        
        # Apply LUT
        result = frame.copy()
        for i in range(3):  # B, G, R channels
            result[:, :, i] = cv2.LUT(result[:, :, i], lut[:, :, :, i].flatten())
        
        return result
    
    def color_temperature_adjustment(self, frame: np.ndarray, temperature: float) -> np.ndarray:
        """Adjust color temperature. Positive values = warmer, negative = cooler."""
        result = frame.copy().astype(np.float32)
        
        # Temperature adjustment matrix
        if temperature > 0:  # Warmer
            result[:, :, 0] *= (1 - temperature * 0.1)  # Reduce blue
            result[:, :, 2] *= (1 + temperature * 0.1)  # Increase red
        else:  # Cooler
            result[:, :, 0] *= (1 - temperature * 0.1)  # Increase blue
            result[:, :, 2] *= (1 + temperature * 0.1)  # Reduce red
        
        return np.clip(result, 0, 255).astype(np.uint8)
    
    def cinematic_grade(self, frame: np.ndarray, intensity: float = 0.5) -> np.ndarray:
        """Apply cinematic color grading."""
        result = frame.copy().astype(np.float32) / 255.0
        
        # Lift shadows, gamma midtones, gain highlights
        lift = np.array([0.05, 0.05, 0.1]) * intensity  # Slightly blue shadows
        gamma = np.array([0.9, 1.0, 1.1]) * intensity + (1 - intensity)  # Warm midtones
        gain = np.array([1.1, 1.0, 0.9]) * intensity + (1 - intensity)  # Orange highlights
        
        # Apply color operations
        result = (result + lift) ** gamma * gain
        
        return np.clip(result * 255, 0, 255).astype(np.uint8)

class MotionEngine:
    """Motion effects and camera movements."""
    
    def __init__(self, config: VideoEffectsConfig):
        self.config = config
    
    def apply_shake(self, frame: np.ndarray, intensity: float = 0.5) -> np.ndarray:
        """Apply camera shake effect."""
        h, w = frame.shape[:2]
        
        # Random shake offsets
        max_offset = int(intensity * 20)
        dx = np.random.randint(-max_offset, max_offset + 1)
        dy = np.random.randint(-max_offset, max_offset + 1)
        
        # Translation matrix
        M = np.float32([[1, 0, dx], [0, 1, dy]])
        
        # Apply transformation
        shaken = cv2.warpAffine(frame, M, (w, h), borderMode=cv2.BORDER_REFLECT)
        
        return shaken
    
    def apply_zoom(self, frame: np.ndarray, zoom_factor: float = 1.2) -> np.ndarray:
        """Apply zoom effect."""
        h, w = frame.shape[:2]
        
        # Calculate new dimensions
        new_h = int(h * zoom_factor)
        new_w = int(w * zoom_factor)
        
        # Resize and crop to original size
        zoomed = cv2.resize(frame, (new_w, new_h))
        
        # Center crop
        y_start = (new_h - h) // 2
        x_start = (new_w - w) // 2
        
        if y_start >= 0 and x_start >= 0:
            result = zoomed[y_start:y_start+h, x_start:x_start+w]
        else:
            result = cv2.resize(zoomed, (w, h))
        
        return result
    
    def apply_rotation(self, frame: np.ndarray, angle: float) -> np.ndarray:
        """Apply rotation effect."""
        h, w = frame.shape[:2]
        center = (w // 2, h // 2)
        
        # Rotation matrix
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        
        # Apply rotation
        rotated = cv2.warpAffine(frame, M, (w, h), borderMode=cv2.BORDER_REFLECT)
        
        return rotated

class VideoEffectsEngine:
    """Enterprise video effects processing engine with professional tools."""
    
    def __init__(self):
        self.config = VideoEffectsConfig()
        self.transition_engine = TransitionEngine(self.config)
        self.overlay_engine = OverlayEngine(self.config)
        self.color_engine = ColorGradingEngine(self.config)
        self.motion_engine = MotionEngine(self.config)
        
    async def apply_transition(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        transition_type: str = "fade",
        duration: float = 1.0,
        config: Optional[VideoEffectsConfig] = None
    ) -> Dict[str, any]:
        """Apply video transition effect between clips."""
        try:
            if config:
                self.config = config
                
            input_path = Path(input_path)
            output_path = Path(output_path)
            
            logger.info(f"Applying {transition_type} transition: {input_path}")
            
            # For single video, apply transition at specified points
            cap = cv2.VideoCapture(str(input_path))
            if not cap.isOpened():
                raise ValueError(f"Cannot open video file: {input_path}")
            
            # Video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Setup writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
            
            transition_frames = int(duration * fps)
            processed_frames = 0
            
            # Read all frames first for transition processing
            frames = []
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                frames.append(frame)
            
            cap.release()
            
            # Apply transitions
            for i, frame in enumerate(frames):
                if i < len(frames) - transition_frames:
                    # Check if this should be a transition point
                    next_frame = frames[min(i + transition_frames, len(frames) - 1)]
                    
                    if i % (total_frames // 3) == 0 and i > 0:  # Transition every third
                        progress = (i % transition_frames) / transition_frames
                        
                        if transition_type == "fade":
                            processed_frame = self.transition_engine.fade_transition(frame, next_frame, progress)
                        elif transition_type == "slide":
                            processed_frame = self.transition_engine.slide_transition(frame, next_frame, progress)
                        elif transition_type == "zoom":
                            processed_frame = self.transition_engine.zoom_transition(frame, next_frame, progress)
                        elif transition_type == "wipe":
                            processed_frame = self.transition_engine.wipe_transition(frame, next_frame, progress)
                        else:
                            processed_frame = frame
                    else:
                        processed_frame = frame
                else:
                    processed_frame = frame
                
                out.write(processed_frame)
                processed_frames += 1
            
            out.release()
            
            logger.info("Transition effect applied successfully")
            
            return {
                "success": True,
                "input_path": str(input_path),
                "output_path": str(output_path),
                "transition_type": transition_type,
                "duration": duration,
                "processed_frames": processed_frames,
                "output_fps": fps,
                "output_resolution": (width, height)
            }
            
        except Exception as e:
            logger.error(f"Transition effect failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "input_path": str(input_path),
                "transition_type": transition_type
            }
    
    async def add_overlay(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        overlay_type: str = "text",
        overlay_data: Dict = None,
        config: Optional[VideoEffectsConfig] = None
    ) -> Dict[str, any]:
        """Add overlay to video (text, image, watermark)."""
        try:
            if config:
                self.config = config
                
            if overlay_data is None:
                overlay_data = {"text": "Sample Text", "position": (50, 50)}
                
            input_path = Path(input_path)
            output_path = Path(output_path)
            
            logger.info(f"Adding {overlay_type} overlay: {input_path}")
            
            cap = cv2.VideoCapture(str(input_path))
            if not cap.isOpened():
                raise ValueError(f"Cannot open video file: {input_path}")
            
            # Video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Setup writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
            
            processed_frames = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Apply overlay based on type
                if overlay_type == "text":
                    text = overlay_data.get("text", "Sample Text")
                    position = overlay_data.get("position", (50, 50))
                    font_scale = overlay_data.get("font_scale", 1.0)
                    color = overlay_data.get("color", (255, 255, 255))
                    
                    processed_frame = self.overlay_engine.add_text_overlay(
                        frame, text, position, font_scale, color
                    )
                    
                elif overlay_type == "watermark":
                    # Create a simple watermark if not provided
                    watermark_text = overlay_data.get("text", "© Ainflue")
                    position = overlay_data.get("position", "bottom_right")
                    opacity = overlay_data.get("opacity", 0.3)
                    
                    # Create text watermark
                    watermark = np.zeros((50, 200, 3), dtype=np.uint8)
                    cv2.putText(watermark, watermark_text, (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    
                    processed_frame = self.overlay_engine.add_watermark(
                        frame, watermark, position, opacity
                    )
                    
                else:
                    processed_frame = frame
                
                out.write(processed_frame)
                processed_frames += 1
            
            cap.release()
            out.release()
            
            logger.info("Overlay added successfully")
            
            return {
                "success": True,
                "input_path": str(input_path),
                "output_path": str(output_path),
                "overlay_type": overlay_type,
                "processed_frames": processed_frames,
                "overlay_data": overlay_data
            }
            
        except Exception as e:
            logger.error(f"Overlay addition failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "input_path": str(input_path),
                "overlay_type": overlay_type
            }
    
    async def apply_motion_effect(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        effect_type: str = "zoom",
        intensity: float = 0.5,
        config: Optional[VideoEffectsConfig] = None
    ) -> Dict[str, any]:
        """Apply motion effects to video."""
        try:
            if config:
                self.config = config
                
            input_path = Path(input_path)
            output_path = Path(output_path)
            
            logger.info(f"Applying {effect_type} motion effect: {input_path}")
            
            cap = cv2.VideoCapture(str(input_path))
            if not cap.isOpened():
                raise ValueError(f"Cannot open video file: {input_path}")
            
            # Video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Setup writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
            
            processed_frames = 0
            frame_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Apply motion effect
                if effect_type == "shake":
                    processed_frame = self.motion_engine.apply_shake(frame, intensity)
                elif effect_type == "zoom":
                    zoom_factor = 1.0 + intensity * 0.5
                    processed_frame = self.motion_engine.apply_zoom(frame, zoom_factor)
                elif effect_type == "rotation":
                    angle = intensity * 10 * np.sin(frame_count * 0.1)  # Oscillating rotation
                    processed_frame = self.motion_engine.apply_rotation(frame, angle)
                else:
                    processed_frame = frame
                
                out.write(processed_frame)
                processed_frames += 1
                frame_count += 1
            
            cap.release()
            out.release()
            
            logger.info("Motion effect applied successfully")
            
            return {
                "success": True,
                "input_path": str(input_path),
                "output_path": str(output_path),
                "effect_type": effect_type,
                "intensity": intensity,
                "processed_frames": processed_frames
            }
            
        except Exception as e:
            logger.error(f"Motion effect failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "input_path": str(input_path),
                "effect_type": effect_type
            }