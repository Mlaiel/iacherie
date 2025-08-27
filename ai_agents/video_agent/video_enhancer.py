"""
Video Enhancer - Advanced Video Quality Enhancement and Frame Stabilization

Industrial-grade video enhancement system with AI-powered quality improvements,
frame stabilization, upscaling, and advanced post-processing capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Video Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""

import asyncio
import logging
import os
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
import json
import numpy as np

import cv2
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as transforms
from PIL import Image, ImageFilter, ImageEnhance
import ffmpeg
from scipy import ndimage, signal
from skimage import restoration, filters, measure, segmentation
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

from ...core.config import settings
from ...utils.performance_monitor import PerformanceMonitor
from ...utils.file_handler import SecureFileHandler
from ...models.video_models import EnhancementJob, QualityMetrics

logger = logging.getLogger(__name__)

class EnhancementType:
    """Types of video enhancement operations"""
    UPSCALE = "upscale"
    DENOISE = "denoise"
    SHARPEN = "sharpen"
    STABILIZE = "stabilize"
    COLOR_CORRECT = "color_correct"
    BRIGHTNESS = "brightness"
    CONTRAST = "contrast"
    SATURATION = "saturation"
    DEBLUR = "deblur"
    ARTIFACT_REMOVAL = "artifact_removal"

class QualityLevel:
    """Quality enhancement levels"""
    LIGHT = {"strength": 0.3, "processing_time": "fast"}
    MEDIUM = {"strength": 0.6, "processing_time": "medium"}
    STRONG = {"strength": 0.9, "processing_time": "slow"}
    EXTREME = {"strength": 1.2, "processing_time": "very_slow"}

class StabilizationMethod:
    """Video stabilization methods"""
    OPTICAL_FLOW = "optical_flow"
    FEATURE_TRACKING = "feature_tracking"
    PHASE_CORRELATION = "phase_correlation"
    BLOCK_MATCHING = "block_matching"
    AI_STABILIZATION = "ai_stabilization"

class VideoEnhancer:
    """
    Advanced video enhancement system with AI-powered quality improvements.
    
    Provides comprehensive video enhancement capabilities including upscaling,
    denoising, sharpening, color correction, and stabilization.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize VideoEnhancer with advanced configuration.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.temp_dir = Path(tempfile.gettempdir()) / "video_enhancer" / str(uuid.uuid4())
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Enhancement parameters
        self.max_resolution = self.config.get("max_resolution", (3840, 2160))  # 4K
        self.upscale_factor_limit = self.config.get("upscale_factor_limit", 4)
        self.batch_size = self.config.get("batch_size", 8)
        
        # Performance monitoring
        self.performance_monitor = PerformanceMonitor("video_enhancer")
        self.file_handler = SecureFileHandler()
        
        # Initialize GPU processing
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.gpu_available = torch.cuda.is_available()
        
        # Initialize enhancement models
        self._initialize_models()
        
        logger.info(f"VideoEnhancer initialized with device: {self.device}")
    
    def _initialize_models(self):
        """Initialize AI models for enhancement"""
        try:
            # Super-resolution model (simplified placeholder)
            if self.gpu_available:
                self.sr_model = self._create_sr_model()
                self.sr_model.to(self.device)
                self.sr_model.eval()
            else:
                self.sr_model = None
            
            # Denoising model
            self.denoising_enabled = True
            
            # Sharpening kernels
            self.sharpen_kernel = np.array([
                [0, -1, 0],
                [-1, 5, -1],
                [0, -1, 0]
            ])
            
            self.unsharp_mask_kernel = np.array([
                [-1, -1, -1],
                [-1, 9, -1],
                [-1, -1, -1]
            ]) / 1.0
            
            logger.info("Enhancement models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing enhancement models: {e}")
            self.sr_model = None
            self.denoising_enabled = False
    
    def _create_sr_model(self) -> nn.Module:
        """Create a simple super-resolution model"""
        class SimpleSRModel(nn.Module):
            def __init__(self, scale_factor=2):
                super(SimpleSRModel, self).__init__()
                self.scale_factor = scale_factor
                
                # Feature extraction
                self.conv1 = nn.Conv2d(3, 64, kernel_size=3, padding=1)
                self.conv2 = nn.Conv2d(64, 64, kernel_size=3, padding=1)
                self.conv3 = nn.Conv2d(64, 32, kernel_size=3, padding=1)
                
                # Upsampling
                self.upconv = nn.ConvTranspose2d(32, 3, kernel_size=scale_factor, stride=scale_factor)
                
                self.relu = nn.ReLU(inplace=True)
            
            def forward(self, x):
                x = self.relu(self.conv1(x))
                x = self.relu(self.conv2(x))
                x = self.relu(self.conv3(x))
                x = torch.tanh(self.upconv(x))
                return x
        
        return SimpleSRModel(scale_factor=2)
    
    async def enhance_video(self, input_path: str,
                          enhancements: List[str],
                          quality_level: str = "medium",
                          output_path: Optional[str] = None,
                          custom_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Enhance video with specified improvements.
        
        Args:
            input_path: Path to input video
            enhancements: List of enhancement types to apply
            quality_level: Quality level for enhancements
            output_path: Optional output path
            custom_params: Custom enhancement parameters
            
        Returns:
            Enhancement result with quality metrics
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input video not found: {input_path}")
        
        if not output_path:
            output_path = str(self.temp_dir / f"enhanced_video_{uuid.uuid4()}.mp4")
        
        start_time = datetime.now(timezone.utc)
        
        try:
            # Get input video properties
            video_info = await self._get_video_info(input_path)
            
            # Validate resolution limits
            width, height = video_info.get("width", 0), video_info.get("height", 0)
            if width * height > self.max_resolution[0] * self.max_resolution[1]:
                raise ValueError(f"Input resolution {width}x{height} exceeds maximum {self.max_resolution}")
            
            # Apply enhancements sequentially
            current_path = input_path
            enhancement_results = {}
            
            for enhancement in enhancements:
                logger.info(f"Applying {enhancement} enhancement")
                
                temp_output = str(self.temp_dir / f"temp_{enhancement}_{uuid.uuid4()}.mp4")
                
                result = await self._apply_enhancement(
                    current_path, temp_output, enhancement, quality_level, custom_params
                )
                
                enhancement_results[enhancement] = result
                current_path = temp_output
            
            # Move final result to output path
            if current_path != output_path:
                os.rename(current_path, output_path)
            
            # Calculate overall enhancement metrics
            end_time = datetime.now(timezone.utc)
            processing_time = (end_time - start_time).total_seconds()
            
            # Analyze quality improvement
            quality_metrics = await self._analyze_quality_improvement(input_path, output_path)
            
            return {
                "success": True,
                "input_path": input_path,
                "output_path": output_path,
                "enhancements": enhancements,
                "quality_level": quality_level,
                "processing_time": processing_time,
                "enhancement_results": enhancement_results,
                "quality_metrics": quality_metrics,
                "file_size_change": os.path.getsize(output_path) - os.path.getsize(input_path),
                "timestamp": end_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Video enhancement failed: {e}")
            raise
    
    async def _apply_enhancement(self, input_path: str, output_path: str,
                               enhancement: str, quality_level: str,
                               custom_params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply specific enhancement to video"""
        
        if enhancement == EnhancementType.UPSCALE:
            return await self._upscale_video(input_path, output_path, quality_level, custom_params)
        elif enhancement == EnhancementType.DENOISE:
            return await self._denoise_video(input_path, output_path, quality_level, custom_params)
        elif enhancement == EnhancementType.SHARPEN:
            return await self._sharpen_video(input_path, output_path, quality_level, custom_params)
        elif enhancement == EnhancementType.STABILIZE:
            return await self._stabilize_video(input_path, output_path, quality_level, custom_params)
        elif enhancement == EnhancementType.COLOR_CORRECT:
            return await self._color_correct_video(input_path, output_path, quality_level, custom_params)
        elif enhancement == EnhancementType.BRIGHTNESS:
            return await self._adjust_brightness(input_path, output_path, quality_level, custom_params)
        elif enhancement == EnhancementType.CONTRAST:
            return await self._adjust_contrast(input_path, output_path, quality_level, custom_params)
        elif enhancement == EnhancementType.SATURATION:
            return await self._adjust_saturation(input_path, output_path, quality_level, custom_params)
        elif enhancement == EnhancementType.DEBLUR:
            return await self._deblur_video(input_path, output_path, quality_level, custom_params)
        else:
            raise ValueError(f"Unsupported enhancement type: {enhancement}")
    
    async def _upscale_video(self, input_path: str, output_path: str,
                           quality_level: str, custom_params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Upscale video resolution using AI super-resolution"""
        upscale_factor = custom_params.get("upscale_factor", 2) if custom_params else 2
        
        if upscale_factor > self.upscale_factor_limit:
            raise ValueError(f"Upscale factor {upscale_factor} exceeds limit {self.upscale_factor_limit}")
        
        try:
            if self.sr_model and self.gpu_available:
                # AI-powered upscaling
                return await self._ai_upscale(input_path, output_path, upscale_factor)
            else:
                # Fallback to traditional upscaling
                return await self._traditional_upscale(input_path, output_path, upscale_factor)
                
        except Exception as e:
            logger.error(f"Video upscaling failed: {e}")
            raise
    
    async def _ai_upscale(self, input_path: str, output_path: str, upscale_factor: int) -> Dict[str, Any]:
        """AI-powered video upscaling"""
        # Extract frames
        frames = await self._extract_frames(input_path)
        if not frames:
            raise ValueError("No frames could be extracted")
        
        enhanced_frames = []
        
        with torch.no_grad():
            for i, frame in enumerate(frames):
                # Convert to tensor
                tensor_frame = transforms.ToTensor()(frame).unsqueeze(0).to(self.device)
                
                # Apply super-resolution
                enhanced_tensor = self.sr_model(tensor_frame)
                
                # Convert back to numpy
                enhanced_frame = enhanced_tensor.squeeze(0).cpu().numpy()
                enhanced_frame = np.transpose(enhanced_frame, (1, 2, 0))
                enhanced_frame = np.clip(enhanced_frame * 255, 0, 255).astype(np.uint8)
                
                enhanced_frames.append(enhanced_frame)
                
                if (i + 1) % 10 == 0:
                    logger.info(f"Upscaled {i + 1}/{len(frames)} frames")
        
        # Create video from enhanced frames
        success = await self._create_video_from_frames(enhanced_frames, output_path, input_path)
        
        return {
            "method": "ai_upscaling",
            "upscale_factor": upscale_factor,
            "frames_processed": len(enhanced_frames),
            "success": success
        }
    
    async def _traditional_upscale(self, input_path: str, output_path: str, upscale_factor: int) -> Dict[str, Any]:
        """Traditional upscaling using ffmpeg"""
        try:
            # Get input video info
            video_info = await self._get_video_info(input_path)
            new_width = int(video_info["width"] * upscale_factor)
            new_height = int(video_info["height"] * upscale_factor)
            
            # Use ffmpeg for upscaling
            input_stream = ffmpeg.input(input_path)
            output_stream = ffmpeg.output(
                input_stream,
                output_path,
                vf=f"scale={new_width}:{new_height}:flags=lanczos",
                vcodec="libx264",
                acodec="aac",
                preset="medium",
                crf=18
            )
            
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: output_stream.overwrite_output().run(quiet=True)
            )
            
            return {
                "method": "traditional_upscaling",
                "upscale_factor": upscale_factor,
                "new_resolution": f"{new_width}x{new_height}",
                "success": os.path.exists(output_path)
            }
            
        except Exception as e:
            logger.error(f"Traditional upscaling failed: {e}")
            raise
    
    async def _denoise_video(self, input_path: str, output_path: str,
                           quality_level: str, custom_params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply denoising to video"""
        try:
            # Determine denoising strength based on quality level
            strength_map = {
                "light": "weak",
                "medium": "medium", 
                "strong": "strong",
                "extreme": "strongest"
            }
            
            denoise_strength = strength_map.get(quality_level, "medium")
            
            # Use ffmpeg hqdn3d filter for denoising
            input_stream = ffmpeg.input(input_path)
            output_stream = ffmpeg.output(
                input_stream,
                output_path,
                vf=f"hqdn3d={denoise_strength}",
                vcodec="libx264",
                acodec="aac",
                preset="medium"
            )
            
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: output_stream.overwrite_output().run(quiet=True)
            )
            
            return {
                "method": "hqdn3d_denoising",
                "strength": denoise_strength,
                "success": os.path.exists(output_path)
            }
            
        except Exception as e:
            logger.error(f"Video denoising failed: {e}")
            raise
    
    async def _sharpen_video(self, input_path: str, output_path: str,
                           quality_level: str, custom_params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply sharpening to video"""
        try:
            # Determine sharpening strength
            strength_map = {
                "light": "0.5:0.5:0.2:0.2",
                "medium": "1.0:1.0:0.5:0.5",
                "strong": "1.5:1.5:0.8:0.8",
                "extreme": "2.0:2.0:1.0:1.0"
            }
            
            sharpen_params = strength_map.get(quality_level, "1.0:1.0:0.5:0.5")
            
            # Use ffmpeg unsharp filter
            input_stream = ffmpeg.input(input_path)
            output_stream = ffmpeg.output(
                input_stream,
                output_path,
                vf=f"unsharp={sharpen_params}",
                vcodec="libx264",
                acodec="aac",
                preset="medium"
            )
            
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: output_stream.overwrite_output().run(quiet=True)
            )
            
            return {
                "method": "unsharp_sharpening",
                "parameters": sharpen_params,
                "success": os.path.exists(output_path)
            }
            
        except Exception as e:
            logger.error(f"Video sharpening failed: {e}")
            raise
    
    async def _color_correct_video(self, input_path: str, output_path: str,
                                 quality_level: str, custom_params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply automatic color correction"""
        try:
            # Color correction parameters based on quality level
            correction_map = {
                "light": {"contrast": 1.05, "brightness": 0.02, "saturation": 1.05},
                "medium": {"contrast": 1.1, "brightness": 0.05, "saturation": 1.1},
                "strong": {"contrast": 1.15, "brightness": 0.08, "saturation": 1.15},
                "extreme": {"contrast": 1.2, "brightness": 0.1, "saturation": 1.2}
            }
            
            params = correction_map.get(quality_level, correction_map["medium"])
            
            # Apply color correction using eq filter
            input_stream = ffmpeg.input(input_path)
            output_stream = ffmpeg.output(
                input_stream,
                output_path,
                vf=f"eq=contrast={params['contrast']}:brightness={params['brightness']}:saturation={params['saturation']}",
                vcodec="libx264",
                acodec="aac",
                preset="medium"
            )
            
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: output_stream.overwrite_output().run(quiet=True)
            )
            
            return {
                "method": "eq_color_correction",
                "parameters": params,
                "success": os.path.exists(output_path)
            }
            
        except Exception as e:
            logger.error(f"Color correction failed: {e}")
            raise
    
    async def _stabilize_video(self, input_path: str, output_path: str,
                             quality_level: str, custom_params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply video stabilization"""
        try:
            # Stabilization parameters
            smoothing_map = {
                "light": 10,
                "medium": 30,
                "strong": 60,
                "extreme": 120
            }
            
            smoothing = smoothing_map.get(quality_level, 30)
            
            # Use ffmpeg deshake filter
            input_stream = ffmpeg.input(input_path)
            output_stream = ffmpeg.output(
                input_stream,
                output_path,
                vf=f"deshake=smoothing={smoothing}",
                vcodec="libx264",
                acodec="aac",
                preset="medium"
            )
            
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: output_stream.overwrite_output().run(quiet=True)
            )
            
            return {
                "method": "deshake_stabilization",
                "smoothing": smoothing,
                "success": os.path.exists(output_path)
            }
            
        except Exception as e:
            logger.error(f"Video stabilization failed: {e}")
            raise
    
    async def _adjust_brightness(self, input_path: str, output_path: str,
                               quality_level: str, custom_params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Adjust video brightness"""
        try:
            brightness_adjustment = custom_params.get("brightness", 0.1) if custom_params else 0.1
            
            input_stream = ffmpeg.input(input_path)
            output_stream = ffmpeg.output(
                input_stream,
                output_path,
                vf=f"eq=brightness={brightness_adjustment}",
                vcodec="libx264",
                acodec="aac"
            )
            
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: output_stream.overwrite_output().run(quiet=True)
            )
            
            return {
                "method": "brightness_adjustment",
                "adjustment": brightness_adjustment,
                "success": os.path.exists(output_path)
            }
            
        except Exception as e:
            logger.error(f"Brightness adjustment failed: {e}")
            raise
    
    async def _adjust_contrast(self, input_path: str, output_path: str,
                             quality_level: str, custom_params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Adjust video contrast"""
        try:
            contrast_adjustment = custom_params.get("contrast", 1.1) if custom_params else 1.1
            
            input_stream = ffmpeg.input(input_path)
            output_stream = ffmpeg.output(
                input_stream,
                output_path,
                vf=f"eq=contrast={contrast_adjustment}",
                vcodec="libx264",
                acodec="aac"
            )
            
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: output_stream.overwrite_output().run(quiet=True)
            )
            
            return {
                "method": "contrast_adjustment",
                "adjustment": contrast_adjustment,
                "success": os.path.exists(output_path)
            }
            
        except Exception as e:
            logger.error(f"Contrast adjustment failed: {e}")
            raise
    
    async def _adjust_saturation(self, input_path: str, output_path: str,
                               quality_level: str, custom_params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Adjust video saturation"""
        try:
            saturation_adjustment = custom_params.get("saturation", 1.1) if custom_params else 1.1
            
            input_stream = ffmpeg.input(input_path)
            output_stream = ffmpeg.output(
                input_stream,
                output_path,
                vf=f"eq=saturation={saturation_adjustment}",
                vcodec="libx264",
                acodec="aac"
            )
            
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: output_stream.overwrite_output().run(quiet=True)
            )
            
            return {
                "method": "saturation_adjustment",
                "adjustment": saturation_adjustment,
                "success": os.path.exists(output_path)
            }
            
        except Exception as e:
            logger.error(f"Saturation adjustment failed: {e}")
            raise
    
    async def _deblur_video(self, input_path: str, output_path: str,
                          quality_level: str, custom_params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply deblurring to video"""
        try:
            # Extract and process frames for deblurring
            frames = await self._extract_frames(input_path)
            if not frames:
                raise ValueError("No frames could be extracted")
            
            deblurred_frames = []
            
            for frame in frames:
                # Apply Wiener filter for deblurring
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
                
                # Estimate point spread function (simplified)
                psf = np.ones((5, 5)) / 25  # Simple box blur PSF
                
                # Apply restoration
                deblurred_gray = restoration.wiener(gray_frame, psf, balance=0.1)
                
                # Convert back to color (simple approach)
                deblurred_frame = frame.copy()
                deblurred_frame = cv2.addWeighted(frame, 0.7, 
                                                cv2.cvtColor((deblurred_gray * 255).astype(np.uint8), 
                                                           cv2.COLOR_GRAY2RGB), 0.3, 0)
                
                deblurred_frames.append(deblurred_frame)
            
            # Create video from deblurred frames
            success = await self._create_video_from_frames(deblurred_frames, output_path, input_path)
            
            return {
                "method": "wiener_deblurring",
                "frames_processed": len(deblurred_frames),
                "success": success
            }
            
        except Exception as e:
            logger.error(f"Video deblurring failed: {e}")
            # Fallback to sharpening
            return await self._sharpen_video(input_path, output_path, quality_level, custom_params)
    
    async def _extract_frames(self, video_path: str) -> List[np.ndarray]:
        """Extract frames from video"""
        frames = []
        
        try:
            cap = cv2.VideoCapture(video_path)
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Convert BGR to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(rgb_frame)
            
            cap.release()
            
        except Exception as e:
            logger.error(f"Frame extraction failed: {e}")
        
        return frames
    
    async def _create_video_from_frames(self, frames: List[np.ndarray], output_path: str, reference_video: str) -> bool:
        """Create video from frames using reference video properties"""
        if not frames:
            return False
        
        try:
            # Get reference video properties
            cap = cv2.VideoCapture(reference_video)
            fps = cap.get(cv2.CAP_PROP_FPS)
            cap.release()
            
            # Create video writer
            height, width = frames[0].shape[:2]
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            for frame in frames:
                # Convert RGB to BGR for OpenCV
                bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                video_writer.write(bgr_frame)
            
            video_writer.release()
            
            return os.path.exists(output_path) and os.path.getsize(output_path) > 0
            
        except Exception as e:
            logger.error(f"Video creation from frames failed: {e}")
            return False
    
    async def _get_video_info(self, video_path: str) -> Dict[str, Any]:
        """Get video information"""
        try:
            probe = ffmpeg.probe(video_path)
            video_stream = next(s for s in probe['streams'] if s['codec_type'] == 'video')
            
            return {
                "width": int(video_stream.get('width', 0)),
                "height": int(video_stream.get('height', 0)),
                "fps": eval(video_stream.get('avg_frame_rate', '0/1')),
                "duration": float(video_stream.get('duration', 0)),
                "codec": video_stream.get('codec_name')
            }
            
        except Exception as e:
            logger.error(f"Failed to get video info: {e}")
            return {}
    
    async def _analyze_quality_improvement(self, original_path: str, enhanced_path: str) -> Dict[str, Any]:
        """Analyze quality improvement between original and enhanced videos"""
        try:
            # Extract sample frames for comparison
            original_frames = await self._extract_sample_frames(original_path, 5)
            enhanced_frames = await self._extract_sample_frames(enhanced_path, 5)
            
            if not original_frames or not enhanced_frames:
                return {"error": "Could not extract frames for comparison"}
            
            # Calculate quality metrics
            sharpness_improvement = 0
            brightness_improvement = 0
            contrast_improvement = 0
            
            for orig, enh in zip(original_frames, enhanced_frames):
                # Sharpness (Laplacian variance)
                orig_sharp = cv2.Laplacian(cv2.cvtColor(orig, cv2.COLOR_RGB2GRAY), cv2.CV_64F).var()
                enh_sharp = cv2.Laplacian(cv2.cvtColor(enh, cv2.COLOR_RGB2GRAY), cv2.CV_64F).var()
                sharpness_improvement += (enh_sharp - orig_sharp) / orig_sharp if orig_sharp > 0 else 0
                
                # Brightness
                orig_bright = np.mean(cv2.cvtColor(orig, cv2.COLOR_RGB2GRAY))
                enh_bright = np.mean(cv2.cvtColor(enh, cv2.COLOR_RGB2GRAY))
                brightness_improvement += abs(enh_bright - 127.5) - abs(orig_bright - 127.5)
                
                # Contrast
                orig_contrast = np.std(cv2.cvtColor(orig, cv2.COLOR_RGB2GRAY))
                enh_contrast = np.std(cv2.cvtColor(enh, cv2.COLOR_RGB2GRAY))
                contrast_improvement += (enh_contrast - orig_contrast) / orig_contrast if orig_contrast > 0 else 0
            
            # Average improvements
            num_frames = len(original_frames)
            
            return {
                "sharpness_improvement_percent": (sharpness_improvement / num_frames) * 100,
                "brightness_improvement": brightness_improvement / num_frames,
                "contrast_improvement_percent": (contrast_improvement / num_frames) * 100,
                "frames_analyzed": num_frames
            }
            
        except Exception as e:
            logger.error(f"Quality analysis failed: {e}")
            return {"error": f"Quality analysis failed: {e}"}
    
    async def _extract_sample_frames(self, video_path: str, num_samples: int) -> List[np.ndarray]:
        """Extract sample frames from video for analysis"""
        frames = []
        
        try:
            cap = cv2.VideoCapture(video_path)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            if frame_count == 0:
                return frames
            
            # Calculate frame indices to sample
            indices = np.linspace(0, frame_count - 1, num_samples, dtype=int)
            
            for idx in indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                
                if ret:
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frames.append(rgb_frame)
            
            cap.release()
            
        except Exception as e:
            logger.error(f"Sample frame extraction failed: {e}")
        
        return frames
    
    async def cleanup(self):
        """Cleanup temporary files and GPU memory"""
        try:
            # Clear GPU memory
            if self.gpu_available:
                torch.cuda.empty_cache()
            
            # Remove temporary directory
            if self.temp_dir.exists():
                import shutil
                shutil.rmtree(self.temp_dir)
            
            logger.info("VideoEnhancer cleanup completed")
            
        except Exception as e:
            logger.error(f"VideoEnhancer cleanup failed: {e}")


class FrameStabilizer:
    """
    Advanced frame stabilization system with multiple stabilization algorithms.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize FrameStabilizer"""
        self.config = config or {}
        self.temp_dir = Path(tempfile.gettempdir()) / "frame_stabilizer" / str(uuid.uuid4())
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("FrameStabilizer initialized")
    
    async def stabilize_video(self, input_path: str,
                            method: str = StabilizationMethod.OPTICAL_FLOW,
                            output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Stabilize video using specified method.
        
        Args:
            input_path: Path to input video
            method: Stabilization method to use
            output_path: Optional output path
            
        Returns:
            Stabilization result
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input video not found: {input_path}")
        
        if not output_path:
            output_path = str(self.temp_dir / f"stabilized_video_{uuid.uuid4()}.mp4")
        
        start_time = datetime.now(timezone.utc)
        
        try:
            if method == StabilizationMethod.OPTICAL_FLOW:
                result = await self._optical_flow_stabilization(input_path, output_path)
            elif method == StabilizationMethod.FEATURE_TRACKING:
                result = await self._feature_tracking_stabilization(input_path, output_path)
            elif method == StabilizationMethod.PHASE_CORRELATION:
                result = await self._phase_correlation_stabilization(input_path, output_path)
            else:
                # Fallback to simple deshake filter
                result = await self._simple_stabilization(input_path, output_path)
            
            stabilization_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            result.update({
                "input_path": input_path,
                "output_path": output_path,
                "method": method,
                "stabilization_time": stabilization_time,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Video stabilization failed: {e}")
            raise
    
    async def _optical_flow_stabilization(self, input_path: str, output_path: str) -> Dict[str, Any]:
        """Stabilize video using optical flow analysis"""
        try:
            # Extract frames
            cap = cv2.VideoCapture(input_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            frames = []
            transforms_smooth = []
            
            # Read all frames
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                frames.append(frame)
            cap.release()
            
            if len(frames) < 2:
                raise ValueError("Video too short for stabilization")
            
            # Calculate transformations between consecutive frames
            transforms = []
            prev_gray = cv2.cvtColor(frames[0], cv2.COLOR_BGR2GRAY)
            
            for i in range(1, len(frames)):
                curr_gray = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
                
                # Calculate optical flow
                flow = cv2.calcOpticalFlowPyrLK(prev_gray, curr_gray, None, None)
                
                # Estimate transformation (simplified)
                dx = np.mean(flow[0][:, :, 0]) if flow[0] is not None else 0
                dy = np.mean(flow[0][:, :, 1]) if flow[0] is not None else 0
                
                transforms.append([dx, dy])
                prev_gray = curr_gray
            
            # Smooth transformations
            trajectory = np.cumsum(transforms, axis=0)
            smoothed_trajectory = self._smooth_trajectory(trajectory)
            smooth_transforms = smoothed_trajectory - trajectory + transforms
            
            # Apply smoothed transformations
            stabilized_frames = []
            for i, frame in enumerate(frames):
                if i == 0:
                    stabilized_frames.append(frame)
                else:
                    dx, dy = smooth_transforms[i-1]
                    M = np.float32([[1, 0, dx], [0, 1, dy]])
                    stabilized_frame = cv2.warpAffine(frame, M, (width, height))
                    stabilized_frames.append(stabilized_frame)
            
            # Create output video
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            for frame in stabilized_frames:
                video_writer.write(frame)
            
            video_writer.release()
            
            return {
                "success": True,
                "method": "optical_flow",
                "frames_processed": len(stabilized_frames),
                "transformation_smoothing": "trajectory_based"
            }
            
        except Exception as e:
            logger.error(f"Optical flow stabilization failed: {e}")
            raise
    
    def _smooth_trajectory(self, trajectory: np.ndarray, window_size: int = 30) -> np.ndarray:
        """Smooth camera trajectory using moving average"""
        smoothed = np.zeros_like(trajectory)
        
        for i in range(len(trajectory)):
            start_idx = max(0, i - window_size // 2)
            end_idx = min(len(trajectory), i + window_size // 2)
            smoothed[i] = np.mean(trajectory[start_idx:end_idx], axis=0)
        
        return smoothed
    
    async def _feature_tracking_stabilization(self, input_path: str, output_path: str) -> Dict[str, Any]:
        """Stabilize using feature point tracking"""
        # Implementation placeholder - would use SIFT/ORB features
        return await self._simple_stabilization(input_path, output_path)
    
    async def _phase_correlation_stabilization(self, input_path: str, output_path: str) -> Dict[str, Any]:
        """Stabilize using phase correlation"""
        # Implementation placeholder - would use FFT-based phase correlation
        return await self._simple_stabilization(input_path, output_path)
    
    async def _simple_stabilization(self, input_path: str, output_path: str) -> Dict[str, Any]:
        """Simple stabilization using ffmpeg deshake filter"""
        try:
            input_stream = ffmpeg.input(input_path)
            output_stream = ffmpeg.output(
                input_stream,
                output_path,
                vf="deshake=smoothing=30",
                vcodec="libx264",
                acodec="aac"
            )
            
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: output_stream.overwrite_output().run(quiet=True)
            )
            
            return {
                "success": True,
                "method": "simple_deshake",
                "filter": "deshake"
            }
            
        except Exception as e:
            logger.error(f"Simple stabilization failed: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup temporary files"""
        try:
            if self.temp_dir.exists():
                import shutil
                shutil.rmtree(self.temp_dir)
            
            logger.info("FrameStabilizer cleanup completed")
            
        except Exception as e:
            logger.error(f"FrameStabilizer cleanup failed: {e}")
