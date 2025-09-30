"""Frame Interpolation Engine
AI-powered frame interpolation for smooth video playback using advanced algorithms.

Created by: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import numpy as np
import cv2
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Optional, Union, List, Tuple
from pathlib import Path
from dataclasses import dataclass
import logging
import tempfile
import subprocess

logger = logging.getLogger(__name__)

@dataclass
class FrameInterpolationConfig:
    """Configuration for frame interpolation."""
    target_fps: int = 60
    interpolation_method: str = "optical_flow"  # optical_flow, ai_rife, ai_dain
    quality_preset: str = "balanced"  # fast, balanced, high_quality
    motion_vector_accuracy: float = 0.8  # 0.0 to 1.0
    temporal_consistency: bool = True
    gpu_acceleration: bool = True
    batch_size: int = 4
    preserve_audio: bool = True
    output_format: str = "mp4"

class OpticalFlowInterpolator:
    """Optical flow-based frame interpolation."""
    
    def __init__(self, config: FrameInterpolationConfig):
        self.config = config
        self.flow_estimator = cv2.FarnebackOpticalFlow_create()
        
    def interpolate_between_frames(self, frame1: np.ndarray, frame2: np.ndarray, alpha: float) -> np.ndarray:
        """Interpolate a frame between two input frames using optical flow."""
        # Convert frames to grayscale for flow calculation
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        
        # Calculate optical flow
        flow = cv2.calcOpticalFlowPyrLK(gray1, gray2, None, None)[0]
        
        # Warp frame1 towards frame2 based on alpha
        h, w = frame1.shape[:2]
        flow_map = np.zeros((h, w, 2), dtype=np.float32)
        
        # Create flow field for warping
        for y in range(h):
            for x in range(w):
                if flow is not None and len(flow) > y * w + x:
                    flow_map[y, x] = flow[y * w + x] * alpha
        
        # Warp the frame
        interpolated_frame = cv2.remap(frame1, flow_map[:,:,0], flow_map[:,:,1], cv2.INTER_LINEAR)
        
        # Blend with direct interpolation for better quality
        direct_blend = cv2.addWeighted(frame1, 1 - alpha, frame2, alpha, 0)
        result = cv2.addWeighted(interpolated_frame, 0.7, direct_blend, 0.3, 0)
        
        return result

class AIFrameInterpolator(nn.Module):
    """AI-based frame interpolation using neural networks."""
    
    def __init__(self):
        super(AIFrameInterpolator, self).__init__()
        
        # Encoder layers
        self.encoder = nn.Sequential(
            nn.Conv2d(6, 64, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.ReLU(inplace=True)
        )
        
        # Decoder layers
        self.decoder = nn.Sequential(
            nn.Conv2d(256, 128, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(128, 64, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(64, 3, kernel_size=3, padding=1),
            nn.Sigmoid()
        )
        
    def forward(self, frame1: torch.Tensor, frame2: torch.Tensor) -> torch.Tensor:
        """Forward pass for frame interpolation."""
        # Concatenate frames
        x = torch.cat([frame1, frame2], dim=1)
        
        # Encode
        encoded = self.encoder(x)
        
        # Decode
        interpolated = self.decoder(encoded)
        
        return interpolated

class FrameInterpolationEngine:
    """Enterprise frame interpolation engine with multiple algorithms."""
    
    def __init__(self):
        self.config = FrameInterpolationConfig()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.ai_interpolator = None
        
    async def initialize_ai_model(self):
        """Initialize AI interpolation model."""
        if self.config.gpu_acceleration and torch.cuda.is_available():
            self.ai_interpolator = AIFrameInterpolator().to(self.device)
            logger.info("AI frame interpolation model initialized on GPU")
        else:
            self.ai_interpolator = AIFrameInterpolator()
            logger.info("AI frame interpolation model initialized on CPU")
    
    async def interpolate_frames(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        config: Optional[FrameInterpolationConfig] = None
    ) -> Dict[str, any]:
        """Interpolate video frames for higher FPS."""
        try:
            if config:
                self.config = config
                
            input_path = Path(input_path)
            output_path = Path(output_path)
            
            logger.info(f"Starting frame interpolation: {input_path}")
            
            # Open video file
            cap = cv2.VideoCapture(str(input_path))
            if not cap.isOpened():
                raise ValueError(f"Cannot open video file: {input_path}")
            
            # Get video properties
            original_fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Calculate interpolation factor
            interpolation_factor = self.config.target_fps / original_fps
            
            logger.info(f"Original FPS: {original_fps}, Target FPS: {self.config.target_fps}")
            logger.info(f"Interpolation factor: {interpolation_factor}")
            
            # Setup video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(str(output_path), fourcc, self.config.target_fps, (width, height))
            
            # Choose interpolation method
            if self.config.interpolation_method == "optical_flow":
                result = await self._interpolate_optical_flow(cap, out, interpolation_factor)
            elif self.config.interpolation_method == "ai_rife":
                await self.initialize_ai_model()
                result = await self._interpolate_ai(cap, out, interpolation_factor)
            else:
                result = await self._interpolate_linear(cap, out, interpolation_factor)
            
            # Cleanup
            cap.release()
            out.release()
            
            # Preserve audio if requested
            if self.config.preserve_audio:
                await self._preserve_audio(input_path, output_path)
            
            result.update({
                "input_path": str(input_path),
                "output_path": str(output_path),
                "original_fps": original_fps,
                "target_fps": self.config.target_fps,
                "interpolation_factor": interpolation_factor,
                "method": self.config.interpolation_method
            })
            
            logger.info("Frame interpolation completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Frame interpolation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "input_path": str(input_path),
                "method": self.config.interpolation_method
            }
    
    async def _interpolate_optical_flow(
        self, 
        cap: cv2.VideoCapture, 
        out: cv2.VideoWriter, 
        factor: float
    ) -> Dict[str, any]:
        """Interpolate frames using optical flow."""
        interpolator = OpticalFlowInterpolator(self.config)
        
        ret, prev_frame = cap.read()
        if not ret:
            raise ValueError("Cannot read first frame")
        
        out.write(prev_frame)
        frames_interpolated = 0
        total_output_frames = 1
        
        while True:
            ret, curr_frame = cap.read()
            if not ret:
                break
            
            # Calculate number of frames to interpolate
            num_interpolated = int(factor) - 1
            
            # Interpolate frames between prev_frame and curr_frame
            for i in range(1, num_interpolated + 1):
                alpha = i / (num_interpolated + 1)
                interpolated = interpolator.interpolate_between_frames(prev_frame, curr_frame, alpha)
                out.write(interpolated)
                frames_interpolated += 1
                total_output_frames += 1
            
            # Write the current frame
            out.write(curr_frame)
            total_output_frames += 1
            prev_frame = curr_frame
        
        return {
            "success": True,
            "frames_interpolated": frames_interpolated,
            "total_output_frames": total_output_frames,
            "method": "optical_flow"
        }
    
    async def _interpolate_ai(
        self, 
        cap: cv2.VideoCapture, 
        out: cv2.VideoWriter, 
        factor: float
    ) -> Dict[str, any]:
        """Interpolate frames using AI model."""
        if self.ai_interpolator is None:
            await self.initialize_ai_model()
        
        ret, prev_frame = cap.read()
        if not ret:
            raise ValueError("Cannot read first frame")
        
        out.write(prev_frame)
        frames_interpolated = 0
        total_output_frames = 1
        
        # Convert frame to tensor
        def frame_to_tensor(frame):
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = frame.astype(np.float32) / 255.0
            frame = torch.from_numpy(frame).permute(2, 0, 1).unsqueeze(0)
            return frame.to(self.device)
        
        def tensor_to_frame(tensor):
            frame = tensor.squeeze(0).permute(1, 2, 0).cpu().numpy()
            frame = (frame * 255).astype(np.uint8)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            return frame
        
        while True:
            ret, curr_frame = cap.read()
            if not ret:
                break
            
            # Convert frames to tensors
            prev_tensor = frame_to_tensor(prev_frame)
            curr_tensor = frame_to_tensor(curr_frame)
            
            # Calculate number of frames to interpolate
            num_interpolated = int(factor) - 1
            
            # Generate interpolated frames using AI
            with torch.no_grad():
                for i in range(1, num_interpolated + 1):
                    # Simple linear interpolation in tensor space
                    alpha = i / (num_interpolated + 1)
                    interpolated_tensor = self.ai_interpolator(
                        prev_tensor * (1 - alpha) + curr_tensor * alpha,
                        curr_tensor * alpha + prev_tensor * (1 - alpha)
                    )
                    
                    interpolated_frame = tensor_to_frame(interpolated_tensor)
                    out.write(interpolated_frame)
                    frames_interpolated += 1
                    total_output_frames += 1
            
            # Write the current frame
            out.write(curr_frame)
            total_output_frames += 1
            prev_frame = curr_frame
        
        return {
            "success": True,
            "frames_interpolated": frames_interpolated,
            "total_output_frames": total_output_frames,
            "method": "ai_rife"
        }
    
    async def _interpolate_linear(
        self, 
        cap: cv2.VideoCapture, 
        out: cv2.VideoWriter, 
        factor: float
    ) -> Dict[str, any]:
        """Simple linear interpolation between frames."""
        ret, prev_frame = cap.read()
        if not ret:
            raise ValueError("Cannot read first frame")
        
        out.write(prev_frame)
        frames_interpolated = 0
        total_output_frames = 1
        
        while True:
            ret, curr_frame = cap.read()
            if not ret:
                break
            
            # Calculate number of frames to interpolate
            num_interpolated = int(factor) - 1
            
            # Linear interpolation
            for i in range(1, num_interpolated + 1):
                alpha = i / (num_interpolated + 1)
                interpolated = cv2.addWeighted(prev_frame, 1 - alpha, curr_frame, alpha, 0)
                out.write(interpolated)
                frames_interpolated += 1
                total_output_frames += 1
            
            # Write the current frame
            out.write(curr_frame)
            total_output_frames += 1
            prev_frame = curr_frame
        
        return {
            "success": True,
            "frames_interpolated": frames_interpolated,
            "total_output_frames": total_output_frames,
            "method": "linear"
        }
    
    async def _preserve_audio(self, input_path: Path, output_path: Path):
        """Preserve audio from original video."""
        try:
            # Use ffmpeg to copy audio track
            temp_video = output_path.with_suffix('.temp.mp4')
            output_path.rename(temp_video)
            
            cmd = [
                'ffmpeg', '-y',
                '-i', str(temp_video),
                '-i', str(input_path),
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-map', '0:v:0',
                '-map', '1:a:0',
                str(output_path)
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            temp_video.unlink()  # Remove temporary file
            
        except Exception as e:
            logger.warning(f"Audio preservation failed: {str(e)}")
    
    async def batch_interpolate(
        self,
        input_paths: List[Union[str, Path]],
        output_dir: Union[str, Path],
        config: Optional[FrameInterpolationConfig] = None
    ) -> Dict[str, any]:
        """Batch frame interpolation for multiple videos."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = []
        
        for input_path in input_paths:
            input_path = Path(input_path)
            output_path = output_dir / f"{input_path.stem}_interpolated{input_path.suffix}"
            
            result = await self.interpolate_frames(input_path, output_path, config)
            results.append(result)
        
        successful = sum(1 for r in results if r.get("success", False))
        
        return {
            "success": True,
            "processed_videos": len(input_paths),
            "successful_interpolations": successful,
            "failed_interpolations": len(input_paths) - successful,
            "results": results
        }