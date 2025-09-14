"""Custom Effect Engine
Programmable custom effects and filter combinations for unique content creation.

Created by: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import numpy as np
import cv2
import json
from typing import Dict, Optional, Union, List, Tuple, Any, Callable
from pathlib import Path
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)

@dataclass
class EffectStep:
    """Single effect step in a custom effect chain."""
    effect_type: str  # blur, color, transform, filter, etc.
    parameters: Dict[str, Any] = field(default_factory=dict)
    blend_mode: str = "normal"  # normal, multiply, overlay, screen, etc.
    opacity: float = 1.0  # 0.0 to 1.0
    mask: Optional[str] = None  # Path to mask image or mask type

@dataclass
class CustomEffectConfig:
    """Configuration for custom effects."""
    name: str = "custom_effect"
    description: str = "Custom effect chain"
    steps: List[EffectStep] = field(default_factory=list)
    global_parameters: Dict[str, Any] = field(default_factory=dict)
    keyframes: Dict[int, Dict[str, Any]] = field(default_factory=dict)  # Frame-based animation
    randomization: Dict[str, Tuple[float, float]] = field(default_factory=dict)  # Parameter randomization

class EffectChain:
    """Chain of effects that can be applied sequentially."""
    
    def __init__(self, config -> None: CustomEffectConfig) -> None:
        self.config = config
        self.effect_registry = self._build_effect_registry()
        
    def _build_effect_registry(self) -> Dict[str, Callable]:
        """Build registry of available effects."""
        return {
            # Color effects
            "brightness": self._apply_brightness,
            "contrast": self._apply_contrast,
            "saturation": self._apply_saturation,
            "hue_shift": self._apply_hue_shift,
            "gamma": self._apply_gamma,
            "vignette": self._apply_vignette,
            
            # Blur effects
            "gaussian_blur": self._apply_gaussian_blur,
            "sharpen": self._apply_sharpen,
        }
    
    def apply_effect_chain(self, frame: np.ndarray, frame_number: int = 0) -> np.ndarray:
        """Apply the complete effect chain to a frame."""
        result = frame.copy()
        
        for i, step in enumerate(self.config.steps):
            try:
                # Get parameters for this frame
                params = step.parameters.copy()
                
                # Get the effect function
                effect_func = self.effect_registry.get(step.effect_type)
                if effect_func is None:
                    logger.warning(f"Unknown effect type: {step.effect_type}")
                    continue
                
                # Apply the effect
                effect_result = effect_func(result, **params)
                
                # Apply blending
                result = cv2.addWeighted(result, 1 - step.opacity, effect_result, step.opacity, 0)
                
            except Exception as e:
                logger.error(f"Error applying effect {step.effect_type}: {str(e)}")
                continue
        
        return result
    
    # Effect implementations
    def _apply_brightness(self, frame: np.ndarray, value: float = 0.0) -> np.ndarray:
        """Apply brightness adjustment."""
        return cv2.convertScaleAbs(frame, alpha=1.0, beta=value)
    
    def _apply_contrast(self, frame: np.ndarray, value: float = 1.0) -> np.ndarray:
        """Apply contrast adjustment."""
        return cv2.convertScaleAbs(frame, alpha=value, beta=0)
    
    def _apply_saturation(self, frame: np.ndarray, value: float = 1.0) -> np.ndarray:
        """Apply saturation adjustment."""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        hsv[:, :, 1] = cv2.multiply(hsv[:, :, 1], value)
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    
    def _apply_hue_shift(self, frame: np.ndarray, degrees: float = 0.0) -> np.ndarray:
        """Apply hue shift."""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        hsv[:, :, 0] = (hsv[:, :, 0] + degrees) % 180
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    
    def _apply_gamma(self, frame: np.ndarray, value: float = 1.0) -> np.ndarray:
        """Apply gamma correction."""
        inv_gamma = 1.0 / value
        table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in range(256)]).astype(np.uint8)
        return cv2.LUT(frame, table)
    
    def _apply_gaussian_blur(self, frame: np.ndarray, radius: float = 5.0) -> np.ndarray:
        """Apply Gaussian blur."""
        kernel_size = max(3, int(radius * 2) | 1)
        return cv2.GaussianBlur(frame, (kernel_size, kernel_size), 0)
    
    def _apply_sharpen(self, frame: np.ndarray, strength: float = 1.0) -> np.ndarray:
        """Apply sharpening filter."""
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]]) * strength
        kernel[1, 1] = 8 * strength + 1
        return cv2.filter2D(frame, -1, kernel)
    
    def _apply_vignette(self, frame: np.ndarray, strength: float = 0.5) -> np.ndarray:
        """Apply vignette effect."""
        h, w = frame.shape[:2]
        center_x, center_y = w // 2, h // 2
        Y, X = np.ogrid[:h, :w]
        
        dist_from_center = np.sqrt((X - center_x)**2 + (Y - center_y)**2)
        max_dist = np.sqrt(center_x**2 + center_y**2)
        
        vignette = 1 - (dist_from_center / max_dist) ** 2 * strength
        vignette = np.clip(vignette, 0.2, 1.0)
        
        result = frame.copy().astype(np.float32)
        for c in range(3):
            result[:, :, c] *= vignette
        
        return np.clip(result, 0, 255).astype(np.uint8)

class CustomEffectEngine:
    """Enterprise custom effect engine for programmable video processing."""
    
    def __init__(self) -> None:
        self.presets = {
            "cinematic": CustomEffectConfig(
                name="cinematic",
                description="Cinematic color grading",
                steps=[
                    EffectStep("contrast", {"value": 1.2}),
                    EffectStep("saturation", {"value": 1.1}),
                    EffectStep("vignette", {"strength": 0.3}),
                ]
            ),
            "vintage": CustomEffectConfig(
                name="vintage",
                description="Vintage film look",
                steps=[
                    EffectStep("gamma", {"value": 1.2}),
                    EffectStep("saturation", {"value": 0.8}),
                    EffectStep("vignette", {"strength": 0.4}),
                ]
            )
        }
        
    async def create_custom_effect(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        effect_config: Dict[str, any]
    ) -> Dict[str, any]:
        """Create and apply custom effects."""
        try:
            input_path = Path(input_path)
            output_path = Path(output_path)
            
            # Parse effect configuration
            config_name = effect_config.get("name", "custom")
            
            if config_name in self.presets:
                config = self.presets[config_name]
            else:
                # Create config from provided data
                steps = []
                for step_data in effect_config.get("steps", []):
                    step = EffectStep(
                        effect_type=step_data["effect_type"],
                        parameters=step_data.get("parameters", {}),
                        opacity=step_data.get("opacity", 1.0)
                    )
                    steps.append(step)
                
                config = CustomEffectConfig(
                    name=config_name,
                    steps=steps
                )
            
            logger.info(f"Applying custom effect '{config.name}': {input_path}")
            
            # Create effect chain
            effect_chain = EffectChain(config)
            
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
                
                # Apply custom effect chain
                processed_frame = effect_chain.apply_effect_chain(frame, frames_processed)
                
                out.write(processed_frame)
                frames_processed += 1
                
                # Progress logging
                if frames_processed % 100 == 0:
                    progress = (frames_processed / total_frames) * 100
                    logger.info(f"Progress: {progress:.1f}% ({frames_processed}/{total_frames} frames)")
            
            cap.release()
            out.release()
            
            logger.info("Custom effect applied successfully")
            
            return {
                "success": True,
                "input_path": str(input_path),
                "output_path": str(output_path),
                "custom_effect_applied": True,
                "config_used": effect_config,
                "frames_processed": frames_processed
            }
            
        except Exception as e:
            logger.error(f"Custom effect failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "input_path": str(input_path)
            }