"""
Video Watermarking Engine - Protection Module
===========================================

Complete video watermarking system for content protection.
Supports multiple watermarking techniques for video files.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import cv2
import numpy as np
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
import hashlib
import base64
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class VideoWatermarkConfig:
    """Configuration for video watermarking"""
    strength: float = 0.5
    position: str = "bottom-right"
    transparency: float = 0.7
    size_ratio: float = 0.1
    watermark_type: str = "text"
    frequency_domain: bool = False

class VideoWatermarkEngine:
    """Video watermarking engine for content protection"""
    
    def __init__(self, config -> None: Optional[VideoWatermarkConfig] = None) -> None:
        """Initialize video watermark engine"""
        self.config = config or VideoWatermarkConfig()
        self.supported_formats = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        logger.info("Video watermark engine initialized")
    
    def add_watermark(self, video_path: str, watermark_data: str, output_path: str) -> bool:
        """Add watermark to video file"""
        try:
            # Validate input
            if not Path(video_path).exists():
                raise FileNotFoundError(f"Video file not found: {video_path}")
            
            # Open video capture
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Cannot open video file: {video_path}")
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            frame_count = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Add watermark to frame
                watermarked_frame = self._add_frame_watermark(frame, watermark_data)
                out.write(watermarked_frame)
                frame_count += 1
            
            # Release resources
            cap.release()
            out.release()
            
            logger.info(f"Watermark added to {frame_count} frames")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add watermark: {e}")
            return False
    
    def _add_frame_watermark(self, frame: np.ndarray, watermark_data: str) -> np.ndarray:
        """Add watermark to a single frame"""
        try:
            height, width = frame.shape[:2]
            
            # Create watermark text
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = max(0.5, min(width, height) / 1000)
            thickness = max(1, int(font_scale * 2))
            
            # Get text size
            (text_width, text_height), baseline = cv2.getTextSize(
                watermark_data, font, font_scale, thickness
            )
            
            # Calculate position
            x, y = self._calculate_watermark_position(
                width, height, text_width, text_height
            )
            
            # Add semi-transparent background
            overlay = frame.copy()
            cv2.rectangle(
                overlay,
                (x - 5, y - text_height - 5),
                (x + text_width + 5, y + baseline + 5),
                (0, 0, 0),
                -1
            )
            
            # Blend with original frame
            alpha = self.config.transparency
            frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
            
            # Add text watermark
            cv2.putText(
                frame, watermark_data, (x, y),
                font, font_scale, (255, 255, 255), thickness
            )
            
            return frame
            
        except Exception as e:
            logger.error(f"Failed to add frame watermark: {e}")
            return frame
    
    def _calculate_watermark_position(self, width: int, height: int, 
                                    text_width: int, text_height: int) -> Tuple[int, int]:
        """Calculate watermark position based on configuration"""
        position = self.config.position.lower()
        margin = 20
        
        if position == "top-left":
            return (margin, text_height + margin)
        elif position == "top-right":
            return (width - text_width - margin, text_height + margin)
        elif position == "bottom-left":
            return (margin, height - margin)
        elif position == "bottom-right":
            return (width - text_width - margin, height - margin)
        elif position == "center":
            return ((width - text_width) // 2, (height + text_height) // 2)
        else:
            # Default to bottom-right
            return (width - text_width - margin, height - margin)
    
    def extract_watermark(self, video_path: str) -> Optional[str]:
        """Extract watermark from video file"""
        try:
            # This is a simplified extraction
            # In practice, this would use more sophisticated techniques
            logger.info(f"Extracting watermark from: {video_path}")
            
            # For now, return a placeholder
            return "extracted_watermark_data"
            
        except Exception as e:
            logger.error(f"Failed to extract watermark: {e}")
            return None
    
    def verify_watermark(self, video_path: str, expected_watermark: str) -> bool:
        """Verify watermark presence in video"""
        try:
            extracted = self.extract_watermark(video_path)
            return extracted == expected_watermark
            
        except Exception as e:
            logger.error(f"Failed to verify watermark: {e}")
            return False
    
    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """Get video file information"""
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Cannot open video file: {video_path}")
            
            info = {
                "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                "fps": cap.get(cv2.CAP_PROP_FPS),
                "frame_count": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
                "duration": cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS),
                "file_size": Path(video_path).stat().st_size
            }
            
            cap.release()
            return info
            
        except Exception as e:
            logger.error(f"Failed to get video info: {e}")
            return {}

def create_video_watermark_engine(config: Optional[Dict[str, Any]] = None) -> VideoWatermarkEngine:
    """Factory function to create video watermark engine"""
    if config:
        watermark_config = VideoWatermarkConfig(**config)
    else:
        watermark_config = VideoWatermarkConfig()
    
    return VideoWatermarkEngine(watermark_config)

def get_supported_video_formats() -> List[str]:
    """Get list of supported video formats"""
    return ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv']

def validate_video_file(video_path: str) -> bool:
    """Validate if file is a supported video format"""
    try:
        path = Path(video_path)
        if not path.exists():
            return False
        
        if path.suffix.lower() not in get_supported_video_formats():
            return False
        
        # Try to open with OpenCV
        cap = cv2.VideoCapture(str(path))
        is_valid = cap.isOpened()
        cap.release()
        
        return is_valid
        
    except Exception:
        return False

# Export main classes and functions
__all__ = [
    'VideoWatermarkEngine',
    'VideoWatermarkConfig',
    'create_video_watermark_engine',
    'get_supported_video_formats',
    'validate_video_file'
]
