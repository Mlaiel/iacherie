"""
🎬 STABLE VIDEO DIFFUSION - Internal Video Generation
=====================================================
FREE video generation using Stable Video Diffusion (no API costs)
Part of VideoStudio internal models

Author: Fahed Mlaiel
Date: October 13, 2025
"""

import logging
import os
import base64
import io
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class StableVideoDiffusionGenerator:
    """Internal video generation with Stable Video Diffusion"""
    
    def __init__(self):
        self.pipe = None
        self.device = "cpu"  # Will auto-detect GPU if available
        self.available = False
        self._initialize()
    
    def _initialize(self):
        """Initialize Stable Video Diffusion pipeline"""
        try:
            import torch
            from diffusers import StableVideoDiffusionPipeline
            
            logger.info("🎬 Loading Stable Video Diffusion...")
            
            # Check if GPU available
            if torch.cuda.is_available():
                self.device = "cuda"
                dtype = torch.float16
                logger.info("✅ GPU detected, using CUDA")
            else:
                self.device = "cpu"
                dtype = torch.float32
                logger.warning("⚠️ No GPU, using CPU (slower)")
            
            # Load pipeline
            self.pipe = StableVideoDiffusionPipeline.from_pretrained(
                "stabilityai/stable-video-diffusion-img2vid",
                torch_dtype=dtype,
                variant="fp16" if self.device == "cuda" else None
            )
            self.pipe.to(self.device)
            
            # Enable optimizations
            if self.device == "cuda":
                self.pipe.enable_attention_slicing()
                try:
                    self.pipe.enable_xformers_memory_efficient_attention()
                    logger.info("✅ xFormers optimization enabled")
                except:
                    logger.info("⚠️ xFormers not available")
            
            self.available = True
            logger.info("✅ Stable Video Diffusion initialized successfully")
            
        except ImportError as e:
            logger.error(f"❌ Failed to import diffusers: {e}")
            logger.info("💡 Install with: pip install diffusers torch transformers")
            self.available = False
        except Exception as e:
            logger.error(f"❌ Failed to initialize Stable Video Diffusion: {e}")
            self.available = False
    
    async def generate(
        self,
        prompt: str,
        duration: int = 5,
        resolution: str = "1024x576",
        fps: int = 7,  # SVD default: 7 fps
        num_inference_steps: int = 25
    ) -> Dict[str, Any]:
        """
        Generate video from prompt using Stable Video Diffusion
        
        Note: SVD is img2vid (image-to-video), so we first generate an image,
        then animate it
        
        Args:
            prompt: Video generation prompt
            duration: Duration in seconds
            resolution: Video resolution (SVD default: 1024x576)
            fps: Frames per second (SVD default: 7)
            num_inference_steps: Quality steps (25 = good quality)
        
        Returns:
            Dict with video data
        """
        if not self.available:
            return {
                'status': 'error',
                'error': 'Stable Video Diffusion not available',
                'message': 'Please install diffusers: pip install diffusers torch'
            }
        
        try:
            logger.info(f"🎬 Generating video with SVD: {prompt}")
            
            # STEP 1: Generate initial image (we'll use SDXL-Turbo for this)
            init_image = await self._generate_initial_image(prompt, resolution)
            
            # STEP 2: Generate video frames from image
            num_frames = duration * fps
            
            logger.info(f"🎥 Generating {num_frames} frames at {fps} fps...")
            
            video_frames = self.pipe(
                init_image,
                height=int(resolution.split('x')[1]),
                width=int(resolution.split('x')[0]),
                num_frames=num_frames,
                num_inference_steps=num_inference_steps,
                decode_chunk_size=8,  # Memory optimization
            ).frames[0]  # Get first video sequence
            
            # STEP 3: Convert frames to video file
            video_bytes = await self._frames_to_video(video_frames, fps)
            
            # Encode to base64
            video_b64 = base64.b64encode(video_bytes).decode('utf-8')
            
            logger.info(f"✅ Video generated successfully ({len(video_frames)} frames)")
            
            return {
                'status': 'completed',
                'video': video_b64,
                'duration': duration,
                'resolution': resolution,
                'fps': fps,
                'num_frames': len(video_frames),
                'format': 'mp4',
                'cost': 0.0,  # FREE - Internal model
                'api_used': 'stable-video-diffusion-img2vid (internal)'
            }
            
        except Exception as e:
            logger.error(f"❌ SVD generation failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'message': 'Stable Video Diffusion generation failed'
            }
    
    async def _generate_initial_image(self, prompt: str, resolution: str) -> Any:
        """Generate initial image for SVD using SDXL-Turbo"""
        try:
            from PIL import Image
            from backend.api.internal_image_generator import get_internal_generator
            
            logger.info("🖼️ Generating initial image with SDXL-Turbo...")
            
            # Parse resolution
            width, height = map(int, resolution.split('x'))
            
            # Generate image
            generator = get_internal_generator()
            result = generator.generate(
                prompt=prompt,
                model="internal-sdxl-turbo",
                width=width,
                height=height,
                num_images=1,
                num_inference_steps=4  # Turbo: 4 steps
            )
            
            if result['status'] == 'success':
                # Decode base64 image
                image_data = base64.b64decode(result['images'][0]['base64'])
                image = Image.open(io.BytesIO(image_data))
                logger.info("✅ Initial image generated")
                return image
            else:
                raise Exception("Image generation failed")
                
        except Exception as e:
            logger.error(f"Failed to generate initial image: {e}")
            # Fallback: Create blank image
            from PIL import Image
            width, height = map(int, resolution.split('x'))
            return Image.new('RGB', (width, height), color='black')
    
    async def _frames_to_video(self, frames: list, fps: int) -> bytes:
        """Convert frames to video file (MP4)"""
        try:
            import cv2
            import numpy as np
            import tempfile
            
            logger.info(f"📹 Converting {len(frames)} frames to video...")
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
                output_path = tmp.name
            
            # Get frame dimensions
            first_frame = np.array(frames[0])
            height, width = first_frame.shape[:2]
            
            # Initialize video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            # Write frames
            for frame in frames:
                frame_np = np.array(frame)
                frame_bgr = cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR)
                out.write(frame_bgr)
            
            out.release()
            
            # Read video file
            with open(output_path, 'rb') as f:
                video_bytes = f.read()
            
            # Cleanup
            os.unlink(output_path)
            
            logger.info(f"✅ Video file created ({len(video_bytes)} bytes)")
            return video_bytes
            
        except Exception as e:
            logger.error(f"Failed to convert frames to video: {e}")
            raise


# Singleton instance
_svd_generator = None

def get_svd_generator() -> StableVideoDiffusionGenerator:
    """Get singleton SVD generator instance"""
    global _svd_generator
    if _svd_generator is None:
        _svd_generator = StableVideoDiffusionGenerator()
    return _svd_generator
