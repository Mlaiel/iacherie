"""
Video Processor - Advanced Video Processing and Analysis Engine

Industrial-grade video processing engine with comprehensive format support,
quality enhancement, and advanced analysis capabilities.

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
import subprocess
import hashlib

import cv2
import numpy as np
import ffmpeg
from PIL import Image, ImageEnhance
import torch
import torchvision.transforms as transforms
from scipy import ndimage
from skimage import filters, restoration, segmentation
from sklearn.cluster import KMeans

from ...core.config import settings
from ...utils.performance_monitor import PerformanceMonitor
from ...utils.file_handler import SecureFileHandler
from ...models.video_models import VideoContent, ProcessingJob

logger = logging.getLogger(__name__)

class VideoCodec:
    """Video codec specifications and configurations"""
    H264 = {"name": "libx264", "quality": "high", "compatibility": "excellent"}
    H265 = {"name": "libx265", "quality": "highest", "compatibility": "good"}
    VP8 = {"name": "libvpx", "quality": "good", "compatibility": "good"}
    VP9 = {"name": "libvpx-vp9", "quality": "high", "compatibility": "good"}
    AV1 = {"name": "libaom-av1", "quality": "highest", "compatibility": "limited"}

class AudioCodec:
    """Audio codec specifications"""
    AAC = {"name": "aac", "quality": "high", "bitrate": "128k"}
    MP3 = {"name": "mp3", "quality": "good", "bitrate": "128k"}
    OPUS = {"name": "libopus", "quality": "highest", "bitrate": "96k"}
    VORBIS = {"name": "libvorbis", "quality": "good", "bitrate": "128k"}

class ProcessingProfile:
    """Pre-defined processing profiles for different use cases"""
    SOCIAL_MEDIA = {
        "resolution": "1080p",
        "fps": 30,
        "bitrate": "2500k",
        "audio_bitrate": "128k",
        "format": "mp4"
    }
    
    STREAMING = {
        "resolution": "720p",
        "fps": 30,
        "bitrate": "1500k",
        "audio_bitrate": "96k",
        "format": "mp4"
    }
    
    ARCHIVE = {
        "resolution": "original",
        "fps": "original",
        "bitrate": "high",
        "audio_bitrate": "192k",
        "format": "mkv"
    }
    
    MOBILE = {
        "resolution": "720p",
        "fps": 24,
        "bitrate": "1000k",
        "audio_bitrate": "64k",
        "format": "mp4"
    }

class VideoProcessor:
    """
    Advanced video processing engine with comprehensive format support and AI enhancement.
    
    Provides industrial-grade video processing capabilities including format conversion,
    quality enhancement, compression, and advanced analysis.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize VideoProcessor with advanced configuration.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.temp_dir = Path(tempfile.gettempdir()) / "video_processor" / str(uuid.uuid4())
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Processing parameters
        self.max_resolution = self.config.get("max_resolution", (3840, 2160))  # 4K
        self.max_duration = self.config.get("max_duration", 7200)  # 2 hours
        self.max_file_size = self.config.get("max_file_size", 10 * 1024 * 1024 * 1024)  # 10GB
        
        # Performance monitoring
        self.performance_monitor = PerformanceMonitor("video_processor")
        self.file_handler = SecureFileHandler()
        
        # Initialize GPU processing if available
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.gpu_available = torch.cuda.is_available()
        
        logger.info(f"VideoProcessor initialized with device: {self.device}")
    
    async def process_video(self, input_path: str, operations: List[str], 
                          output_path: Optional[str] = None,
                          profile: Optional[str] = None,
                          custom_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process video with specified operations and parameters.
        
        Args:
            input_path: Path to input video file
            operations: List of operations to perform
            output_path: Optional output path (generated if not provided)
            profile: Processing profile to use
            custom_params: Custom processing parameters
            
        Returns:
            Processing results with output information
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input video file not found: {input_path}")
        
        # Validate file size
        file_size = os.path.getsize(input_path)
        if file_size > self.max_file_size:
            raise ValueError(f"File size {file_size} exceeds maximum allowed size {self.max_file_size}")
        
        # Generate output path if not provided
        if not output_path:
            input_name = Path(input_path).stem
            output_path = str(self.temp_dir / f"{input_name}_processed.mp4")
        
        # Start processing
        start_time = datetime.now(timezone.utc)
        
        try:
            # Load video properties
            video_info = await self._get_video_info(input_path)
            
            # Validate duration
            duration = video_info.get("duration", 0)
            if duration > self.max_duration:
                raise ValueError(f"Video duration {duration}s exceeds maximum {self.max_duration}s")
            
            # Apply processing profile
            if profile:
                processing_params = self._get_profile_params(profile)
            else:
                processing_params = custom_params or {}
            
            # Execute operations sequentially
            current_input = input_path
            
            for operation in operations:
                operation_result = await self._execute_operation(
                    operation, current_input, processing_params
                )
                current_input = operation_result["output_path"]
            
            # Move final result to output path
            if current_input != output_path:
                os.rename(current_input, output_path)
            
            # Calculate processing metrics
            end_time = datetime.now(timezone.utc)
            processing_time = (end_time - start_time).total_seconds()
            
            # Get output file info
            output_info = await self._get_video_info(output_path)
            
            result = {
                "success": True,
                "input_path": input_path,
                "output_path": output_path,
                "operations": operations,
                "processing_time": processing_time,
                "input_info": video_info,
                "output_info": output_info,
                "file_size_reduction": max(0, 1 - (os.path.getsize(output_path) / file_size)),
                "timestamp": end_time.isoformat()
            }
            
            logger.info(f"Video processing completed in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Video processing failed: {e}")
            raise
    
    async def _get_video_info(self, video_path: str) -> Dict[str, Any]:
        """
        Extract comprehensive video information using ffprobe.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Video information dictionary
        """
        try:
            probe = ffmpeg.probe(video_path)
            
            # Extract video stream info
            video_stream = next((s for s in probe['streams'] if s['codec_type'] == 'video'), None)
            audio_streams = [s for s in probe['streams'] if s['codec_type'] == 'audio']
            
            info = {
                "format": probe['format'],
                "duration": float(probe['format'].get('duration', 0)),
                "size": int(probe['format'].get('size', 0)),
                "bitrate": int(probe['format'].get('bit_rate', 0)),
                "streams": len(probe['streams'])
            }
            
            if video_stream:
                info.update({
                    "width": int(video_stream.get('width', 0)),
                    "height": int(video_stream.get('height', 0)),
                    "fps": eval(video_stream.get('avg_frame_rate', '0/1')),
                    "video_codec": video_stream.get('codec_name'),
                    "pixel_format": video_stream.get('pix_fmt'),
                    "color_space": video_stream.get('color_space'),
                    "color_range": video_stream.get('color_range')
                })
            
            if audio_streams:
                info.update({
                    "audio_codec": audio_streams[0].get('codec_name'),
                    "audio_sample_rate": int(audio_streams[0].get('sample_rate', 0)),
                    "audio_channels": int(audio_streams[0].get('channels', 0)),
                    "audio_bitrate": int(audio_streams[0].get('bit_rate', 0))
                })
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get video info: {e}")
            raise
    
    async def _execute_operation(self, operation: str, input_path: str, 
                               params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a specific video processing operation.
        
        Args:
            operation: Operation type to execute
            input_path: Input video path
            params: Processing parameters
            
        Returns:
            Operation result with output path
        """
        operation_lower = operation.lower()
        output_path = str(self.temp_dir / f"temp_{uuid.uuid4()}.mp4")
        
        if operation_lower == "convert":
            return await self._convert_format(input_path, output_path, params)
        elif operation_lower == "compress":
            return await self._compress_video(input_path, output_path, params)
        elif operation_lower == "resize":
            return await self._resize_video(input_path, output_path, params)
        elif operation_lower == "enhance":
            return await self._enhance_video(input_path, output_path, params)
        elif operation_lower == "stabilize":
            return await self._stabilize_video(input_path, output_path, params)
        elif operation_lower == "denoise":
            return await self._denoise_video(input_path, output_path, params)
        elif operation_lower == "color_correct":
            return await self._color_correct_video(input_path, output_path, params)
        elif operation_lower == "trim":
            return await self._trim_video(input_path, output_path, params)
        else:
            raise ValueError(f"Unsupported operation: {operation}")
    
    async def _convert_format(self, input_path: str, output_path: str, 
                            params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert video to different format with optimized settings.
        
        Args:
            input_path: Input video path
            output_path: Output video path
            params: Conversion parameters
            
        Returns:
            Conversion result
        """
        target_format = params.get("format", "mp4")
        video_codec = params.get("video_codec", "libx264")
        audio_codec = params.get("audio_codec", "aac")
        quality = params.get("quality", "medium")
        
        # Quality settings
        quality_settings = {
            "low": {"crf": 28, "preset": "fast"},
            "medium": {"crf": 23, "preset": "medium"},
            "high": {"crf": 18, "preset": "slow"},
            "highest": {"crf": 15, "preset": "veryslow"}
        }
        
        settings = quality_settings.get(quality, quality_settings["medium"])
        
        try:
            # Build ffmpeg command
            input_stream = ffmpeg.input(input_path)
            
            output_args = {
                "vcodec": video_codec,
                "acodec": audio_codec,
                "crf": settings["crf"],
                "preset": settings["preset"]
            }
            
            # Add format-specific optimizations
            if target_format == "mp4":
                output_args.update({
                    "movflags": "+faststart",  # Enable streaming
                    "pix_fmt": "yuv420p"
                })
            elif target_format == "webm":
                output_args.update({
                    "vcodec": "libvpx-vp9",
                    "acodec": "libopus"
                })
            
            # Execute conversion
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: ffmpeg.output(input_stream, output_path, **output_args)
                .overwrite_output()
                .run(quiet=True)
            )
            
            return {
                "success": True,
                "output_path": output_path,
                "operation": "convert",
                "format": target_format,
                "quality": quality
            }
            
        except Exception as e:
            logger.error(f"Format conversion failed: {e}")
            raise
    
    async def _compress_video(self, input_path: str, output_path: str, 
                            params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compress video with intelligent quality preservation.
        
        Args:
            input_path: Input video path
            output_path: Output video path
            params: Compression parameters
            
        Returns:
            Compression result
        """
        target_size = params.get("target_size_mb")
        quality_reduction = params.get("quality_reduction", 0.3)
        preserve_resolution = params.get("preserve_resolution", True)
        
        try:
            # Get input video info
            video_info = await self._get_video_info(input_path)
            input_bitrate = video_info.get("bitrate", 5000000)  # Default 5Mbps
            duration = video_info.get("duration", 0)
            
            # Calculate target bitrate
            if target_size:
                # Calculate bitrate for target file size
                target_bits = target_size * 8 * 1024 * 1024  # Convert MB to bits
                target_bitrate = int(target_bits / duration * 0.9)  # 90% for video, 10% for audio
            else:
                # Reduce bitrate by quality_reduction factor
                target_bitrate = int(input_bitrate * (1 - quality_reduction))
            
            # Ensure minimum quality
            min_bitrate = 500000  # 500kbps minimum
            target_bitrate = max(target_bitrate, min_bitrate)
            
            input_stream = ffmpeg.input(input_path)
            
            output_args = {
                "vcodec": "libx264",
                "acodec": "aac",
                "b:v": str(target_bitrate),
                "b:a": "128k",
                "preset": "medium",
                "crf": 23,
                "movflags": "+faststart"
            }
            
            # Add two-pass encoding for better quality at low bitrates
            if target_bitrate < 2000000:  # Less than 2Mbps
                output_args.update({
                    "pass": 1,
                    "f": "null"
                })
                
                # First pass
                first_pass = ffmpeg.output(input_stream, "/dev/null", **output_args)
                await asyncio.get_event_loop().run_in_executor(
                    None, lambda: first_pass.overwrite_output().run(quiet=True)
                )
                
                # Second pass
                output_args.update({
                    "pass": 2
                })
                del output_args["f"]
            
            # Execute compression
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: ffmpeg.output(input_stream, output_path, **output_args)
                .overwrite_output()
                .run(quiet=True)
            )
            
            # Calculate compression ratio
            input_size = os.path.getsize(input_path)
            output_size = os.path.getsize(output_path)
            compression_ratio = 1 - (output_size / input_size)
            
            return {
                "success": True,
                "output_path": output_path,
                "operation": "compress",
                "compression_ratio": compression_ratio,
                "size_reduction_mb": (input_size - output_size) / (1024 * 1024),
                "target_bitrate": target_bitrate
            }
            
        except Exception as e:
            logger.error(f"Video compression failed: {e}")
            raise
    
    async def _enhance_video(self, input_path: str, output_path: str, 
                           params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance video quality using AI-powered algorithms.
        
        Args:
            input_path: Input video path
            output_path: Output video path
            params: Enhancement parameters
            
        Returns:
            Enhancement result
        """
        enhancements = params.get("enhancements", ["sharpen", "denoise"])
        
        try:
            # Use ffmpeg filters for enhancement
            input_stream = ffmpeg.input(input_path)
            filters = []
            
            if "sharpen" in enhancements:
                filters.append("unsharp=5:5:0.8:3:3:0.4")
            
            if "denoise" in enhancements:
                filters.append("hqdn3d")
            
            if "stabilize" in enhancements:
                filters.append("deshake")
            
            if "color_correct" in enhancements:
                filters.append("eq=contrast=1.1:brightness=0.05:saturation=1.1")
            
            # Apply filters
            if filters:
                filter_string = ",".join(filters)
                video = input_stream.video.filter("scale", "trunc(iw/2)*2", "trunc(ih/2)*2")
                video = video.filter("fps", fps=30)
                video = ffmpeg.filter(video, "scale", 1920, 1080)
                
                for filter_str in filters:
                    video = ffmpeg.filter(video, filter_str.split("=")[0], 
                                        *filter_str.split("=")[1:] if "=" in filter_str else [])
                
                audio = input_stream.audio
                
                # Combine video and audio
                output = ffmpeg.output(video, audio, output_path,
                                     vcodec="libx264",
                                     acodec="aac",
                                     preset="medium",
                                     crf=18)
            else:
                # Just copy if no enhancements
                output = ffmpeg.output(input_stream, output_path, 
                                     vcodec="libx264", acodec="aac")
            
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: output.overwrite_output().run(quiet=True)
            )
            
            return {
                "success": True,
                "output_path": output_path,
                "operation": "enhance",
                "enhancements_applied": enhancements
            }
            
        except Exception as e:
            logger.error(f"Video enhancement failed: {e}")
            raise
    
    def _get_profile_params(self, profile: str) -> Dict[str, Any]:
        """Get processing parameters for a specific profile"""
        profiles = {
            "social_media": ProcessingProfile.SOCIAL_MEDIA,
            "streaming": ProcessingProfile.STREAMING,
            "archive": ProcessingProfile.ARCHIVE,
            "mobile": ProcessingProfile.MOBILE
        }
        
        return profiles.get(profile.lower(), {})
    
    async def cleanup(self):
        """Cleanup temporary files and resources"""
        try:
            if self.temp_dir.exists():
                import shutil
                shutil.rmtree(self.temp_dir)
            
            logger.info("VideoProcessor cleanup completed")
            
        except Exception as e:
            logger.error(f"VideoProcessor cleanup failed: {e}")


class VideoAnalyzer:
    """
    Advanced video content analyzer with AI-powered scene detection and content analysis.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize VideoAnalyzer.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.temp_dir = Path(tempfile.gettempdir()) / "video_analyzer" / str(uuid.uuid4())
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Analysis parameters
        self.frame_sample_rate = self.config.get("frame_sample_rate", 1.0)  # seconds
        self.max_frames_analyze = self.config.get("max_frames_analyze", 100)
        
        logger.info("VideoAnalyzer initialized")
    
    async def analyze_content(self, video_path: str, 
                            analysis_types: List[str] = None) -> Dict[str, Any]:
        """
        Perform comprehensive video content analysis.
        
        Args:
            video_path: Path to video file
            analysis_types: Types of analysis to perform
            
        Returns:
            Analysis results
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        analysis_types = analysis_types or [
            "scenes", "objects", "motion", "color", "quality", "audio"
        ]
        
        results = {
            "video_path": video_path,
            "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
            "analysis_types": analysis_types
        }
        
        try:
            # Open video for analysis
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError("Cannot open video file")
            
            # Get basic video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            results["video_properties"] = {
                "fps": fps,
                "frame_count": frame_count,
                "width": width,
                "height": height,
                "duration": frame_count / fps if fps > 0 else 0
            }
            
            # Perform specific analyses
            if "scenes" in analysis_types:
                results["scene_analysis"] = await self._analyze_scenes(cap, fps)
            
            if "motion" in analysis_types:
                results["motion_analysis"] = await self._analyze_motion(cap, fps)
            
            if "color" in analysis_types:
                results["color_analysis"] = await self._analyze_colors(cap, fps)
            
            if "quality" in analysis_types:
                results["quality_analysis"] = await self._analyze_quality(cap)
            
            if "audio" in analysis_types:
                results["audio_analysis"] = await self._analyze_audio(video_path)
            
            cap.release()
            
            return results
            
        except Exception as e:
            if 'cap' in locals():
                cap.release()
            logger.error(f"Video analysis failed: {e}")
            raise
    
    async def _analyze_scenes(self, cap: cv2.VideoCapture, fps: float) -> Dict[str, Any]:
        """Analyze video scenes and detect scene changes"""
        scenes = []
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Sample frames for scene detection
        sample_interval = max(1, int(fps * self.frame_sample_rate))
        prev_frame = None
        scene_start = 0
        scene_threshold = 0.3  # Threshold for scene change detection
        
        for i in range(0, frame_count, sample_interval):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            
            if not ret:
                break
            
            # Convert to grayscale for comparison
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            if prev_frame is not None:
                # Calculate frame difference
                diff = cv2.absdiff(prev_frame, gray_frame)
                non_zero_count = np.count_nonzero(diff)
                total_pixels = diff.shape[0] * diff.shape[1]
                change_ratio = non_zero_count / total_pixels
                
                # Detect scene change
                if change_ratio > scene_threshold:
                    scenes.append({
                        "start_frame": scene_start,
                        "end_frame": i - 1,
                        "start_time": scene_start / fps,
                        "end_time": (i - 1) / fps,
                        "duration": (i - 1 - scene_start) / fps
                    })
                    scene_start = i
            
            prev_frame = gray_frame.copy()
        
        # Add final scene
        if scene_start < frame_count - 1:
            scenes.append({
                "start_frame": scene_start,
                "end_frame": frame_count - 1,
                "start_time": scene_start / fps,
                "end_time": (frame_count - 1) / fps,
                "duration": (frame_count - 1 - scene_start) / fps
            })
        
        return {
            "total_scenes": len(scenes),
            "scenes": scenes,
            "average_scene_duration": np.mean([s["duration"] for s in scenes]) if scenes else 0
        }
    
    async def _analyze_motion(self, cap: cv2.VideoCapture, fps: float) -> Dict[str, Any]:
        """Analyze motion patterns in the video"""
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        sample_interval = max(1, int(fps * 0.5))  # Sample every 0.5 seconds
        
        motion_data = []
        prev_gray = None
        
        for i in range(0, min(frame_count, self.max_frames_analyze * sample_interval), sample_interval):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            
            if not ret:
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            if prev_gray is not None:
                # Calculate optical flow
                flow = cv2.calcOpticalFlowPyrLK(prev_gray, gray, 
                                              np.random.randint(0, gray.shape[1], (100, 1, 2)).astype(np.float32),
                                              None)
                
                if flow[0] is not None:
                    # Calculate motion magnitude
                    motion_vectors = flow[0].reshape(-1, 2)
                    motion_magnitudes = np.linalg.norm(motion_vectors, axis=1)
                    avg_motion = np.mean(motion_magnitudes)
                    
                    motion_data.append({
                        "frame": i,
                        "timestamp": i / fps,
                        "average_motion": float(avg_motion),
                        "max_motion": float(np.max(motion_magnitudes)),
                        "motion_vectors": len(motion_vectors)
                    })
            
            prev_gray = gray.copy()
        
        if motion_data:
            avg_motions = [m["average_motion"] for m in motion_data]
            return {
                "total_samples": len(motion_data),
                "overall_motion": np.mean(avg_motions),
                "motion_variance": np.var(avg_motions),
                "max_motion_frame": max(motion_data, key=lambda x: x["average_motion"]),
                "motion_timeline": motion_data
            }
        else:
            return {"error": "No motion data could be calculated"}
    
    async def _analyze_colors(self, cap: cv2.VideoCapture, fps: float) -> Dict[str, Any]:
        """Analyze color distribution and dominant colors"""
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        sample_interval = max(1, int(fps * 2.0))  # Sample every 2 seconds
        
        color_data = []
        all_colors = []
        
        for i in range(0, min(frame_count, self.max_frames_analyze * sample_interval), sample_interval):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            
            if not ret:
                break
            
            # Resize frame for faster processing
            small_frame = cv2.resize(frame, (64, 64))
            
            # Convert to RGB
            rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            # Flatten to get all pixels
            pixels = rgb_frame.reshape(-1, 3)
            all_colors.extend(pixels)
            
            # Calculate color histogram
            hist_r = cv2.calcHist([rgb_frame], [0], None, [256], [0, 256])
            hist_g = cv2.calcHist([rgb_frame], [1], None, [256], [0, 256])
            hist_b = cv2.calcHist([rgb_frame], [2], None, [256], [0, 256])
            
            # Find dominant colors using k-means
            try:
                kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
                kmeans.fit(pixels)
                dominant_colors = kmeans.cluster_centers_.astype(int)
                
                color_data.append({
                    "frame": i,
                    "timestamp": i / fps,
                    "dominant_colors": dominant_colors.tolist(),
                    "color_variance": np.var(pixels, axis=0).tolist()
                })
            except:
                # Fallback if k-means fails
                mean_color = np.mean(pixels, axis=0).astype(int)
                color_data.append({
                    "frame": i,
                    "timestamp": i / fps,
                    "dominant_colors": [mean_color.tolist()],
                    "color_variance": np.var(pixels, axis=0).tolist()
                })
        
        # Overall color analysis
        if all_colors:
            all_colors = np.array(all_colors)
            
            # Calculate overall dominant colors
            try:
                kmeans = KMeans(n_clusters=10, random_state=42, n_init=10)
                kmeans.fit(all_colors[::100])  # Sample for performance
                overall_dominant = kmeans.cluster_centers_.astype(int)
            except:
                overall_dominant = [np.mean(all_colors, axis=0).astype(int)]
            
            return {
                "total_samples": len(color_data),
                "overall_dominant_colors": overall_dominant.tolist(),
                "color_diversity": float(np.std(all_colors)),
                "color_timeline": color_data,
                "average_brightness": float(np.mean(all_colors))
            }
        else:
            return {"error": "No color data could be analyzed"}
    
    async def _analyze_quality(self, cap: cv2.VideoCapture) -> Dict[str, Any]:
        """Analyze video quality metrics"""
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        sample_frames = min(20, frame_count)  # Analyze up to 20 frames
        
        quality_metrics = {
            "sharpness": [],
            "brightness": [],
            "contrast": [],
            "noise": []
        }
        
        for i in range(0, frame_count, frame_count // sample_frames):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            
            if not ret:
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Sharpness (Laplacian variance)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            sharpness = laplacian.var()
            quality_metrics["sharpness"].append(sharpness)
            
            # Brightness (mean intensity)
            brightness = np.mean(gray)
            quality_metrics["brightness"].append(brightness)
            
            # Contrast (standard deviation)
            contrast = np.std(gray)
            quality_metrics["contrast"].append(contrast)
            
            # Noise estimation
            denoised = cv2.GaussianBlur(gray, (5, 5), 0)
            noise = np.mean(np.abs(gray.astype(float) - denoised.astype(float)))
            quality_metrics["noise"].append(noise)
        
        # Calculate averages
        return {
            "average_sharpness": float(np.mean(quality_metrics["sharpness"])),
            "average_brightness": float(np.mean(quality_metrics["brightness"])),
            "average_contrast": float(np.mean(quality_metrics["contrast"])),
            "average_noise": float(np.mean(quality_metrics["noise"])),
            "sharpness_variance": float(np.var(quality_metrics["sharpness"])),
            "brightness_variance": float(np.var(quality_metrics["brightness"])),
            "contrast_variance": float(np.var(quality_metrics["contrast"])),
            "overall_quality_score": self._calculate_quality_score(quality_metrics)
        }
    
    def _calculate_quality_score(self, metrics: Dict[str, List[float]]) -> float:
        """Calculate overall quality score from individual metrics"""
        if not all(metrics.values()):
            return 0.0
        
        # Normalize metrics to 0-100 scale
        sharpness_score = min(100, np.mean(metrics["sharpness"]) / 1000 * 100)
        brightness_score = 100 - abs(np.mean(metrics["brightness"]) - 127.5) / 127.5 * 100
        contrast_score = min(100, np.mean(metrics["contrast"]) / 64 * 100)
        noise_score = max(0, 100 - np.mean(metrics["noise"]) / 20 * 100)
        
        # Weighted average
        weights = {"sharpness": 0.3, "brightness": 0.2, "contrast": 0.2, "noise": 0.3}
        
        quality_score = (
            sharpness_score * weights["sharpness"] +
            brightness_score * weights["brightness"] + 
            contrast_score * weights["contrast"] +
            noise_score * weights["noise"]
        )
        
        return float(quality_score)
    
    async def _analyze_audio(self, video_path: str) -> Dict[str, Any]:
        """Analyze audio properties and quality"""
        try:
            probe = ffmpeg.probe(video_path)
            audio_streams = [s for s in probe['streams'] if s['codec_type'] == 'audio']
            
            if not audio_streams:
                return {"error": "No audio streams found"}
            
            audio_stream = audio_streams[0]
            
            return {
                "codec": audio_stream.get('codec_name'),
                "sample_rate": int(audio_stream.get('sample_rate', 0)),
                "channels": int(audio_stream.get('channels', 0)),
                "bitrate": int(audio_stream.get('bit_rate', 0)),
                "duration": float(audio_stream.get('duration', 0)),
                "channel_layout": audio_stream.get('channel_layout')
            }
            
        except Exception as e:
            logger.error(f"Audio analysis failed: {e}")
            return {"error": f"Audio analysis failed: {e}"}
    
    async def cleanup(self):
        """Cleanup temporary files"""
        try:
            if self.temp_dir.exists():
                import shutil
                shutil.rmtree(self.temp_dir)
            
            logger.info("VideoAnalyzer cleanup completed")
            
        except Exception as e:
            logger.error(f"VideoAnalyzer cleanup failed: {e}")
