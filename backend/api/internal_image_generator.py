"""
Internal Image Generator - Free AI Leader Image Generation
Uses Stable Diffusion models for $0.00 cost generation

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

# Set environment variables BEFORE imports
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''  # Force CPU mode

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import uuid
from datetime import datetime
import io
import base64
from PIL import Image

# Import torch
import torch

# Import diffusers (versions: diffusers==0.28.0 transformers==4.41.0)
try:
    from diffusers import DiffusionPipeline, StableDiffusionPipeline, DPMSolverMultistepScheduler
    diffusers_available = True
    logging.info("✅ Diffusers 0.28.0 + Transformers 4.41.0 imported successfully")
except Exception as e:
    logging.error(f"❌ Failed to import diffusers: {e}")
    diffusers_available = False

logger = logging.getLogger(__name__)

class InternalImageGenerator:
    """Professional internal image generation with Stable Diffusion"""
    
    def __init__(self):
        if not diffusers_available:
            logger.warning("⚠️ Diffusers not available")
            self.available = False
            return
        
        self.available = True
        self.device = "cpu"  # Force CPU (no GPU in container)
        self.dtype = torch.float32  # CPU uses float32
        
        # Cache directory for models
        self.cache_dir = Path("/tmp/ai_leader_models")
        self.cache_dir.mkdir(exist_ok=True, parents=True)
        
        # Output directory for generated images
        self.output_dir = Path("/tmp/ai_leader_generated_images")
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Models cache
        self.models = {}
        
        logger.info(f"🎨 Internal Image Generator initialized on {self.device}")
        
    def _get_model_id(self, model_name: str) -> str:
        """Map model names to HuggingFace model IDs"""
        model_map = {
            "internal-sdxl-turbo": "stabilityai/sdxl-turbo",
            "internal-sd-turbo": "stabilityai/sd-turbo",
            "internal-sd-1.5": "runwayml/stable-diffusion-v1-5",
            "internal-image": "stabilityai/sdxl-turbo",  # Default
        }
        return model_map.get(model_name, "stabilityai/sdxl-turbo")
    
    def _load_model(self, model_id: str):
        """Load model with caching"""
        if not diffusers_available:
            return None
            
        if model_id in self.models:
            logger.info(f"♻️ Using cached model: {model_id}")
            return self.models[model_id]
        
        logger.info(f"📥 Loading model: {model_id}")
        
        try:
            # Load pipeline
            if "turbo" in model_id.lower():
                # Turbo models need special handling
                pipe = DiffusionPipeline.from_pretrained(
                    model_id,
                    torch_dtype=self.dtype,
                    cache_dir=str(self.cache_dir),
                    variant="fp16" if self.device == "cuda" else None,
                    low_cpu_mem_usage=True
                )
            else:
                # Standard Stable Diffusion
                pipe = StableDiffusionPipeline.from_pretrained(
                    model_id,
                    torch_dtype=self.dtype,
                    cache_dir=str(self.cache_dir),
                    variant="fp16" if self.device == "cuda" else None,
                    low_cpu_mem_usage=True
                )
            
            # Optimize
            pipe = pipe.to(self.device)
            
            if self.device == "cuda":
                # Enable memory optimizations
                pipe.enable_attention_slicing()
                try:
                    pipe.enable_xformers_memory_efficient_attention()
                    logger.info("✅ xFormers optimization enabled")
                except:
                    logger.info("⚠️ xFormers not available, using standard attention")
            
            # Use fast scheduler for turbo models
            if "turbo" in model_id.lower():
                pipe.scheduler = DPMSolverMultistepScheduler.from_config(
                    pipe.scheduler.config,
                    algorithm_type="sde-dpmsolver++",
                    use_karras_sigmas=True
                )
            
            # Cache the model
            self.models[model_id] = pipe
            logger.info(f"✅ Model loaded and cached: {model_id}")
            
            return pipe
            
        except Exception as e:
            logger.error(f"❌ Failed to load model {model_id}: {e}")
            raise
    
    def generate(
        self,
        prompt: str,
        model: str = "internal-sdxl-turbo",
        width: int = 512,
        height: int = 512,
        num_images: int = 1,
        num_inference_steps: int = 4,  # Turbo models use 4 steps
        guidance_scale: float = 0.0,  # Turbo models don't use guidance
        negative_prompt: Optional[str] = None,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate images using internal models
        
        Args:
            prompt: Text description of the image
            model: Model to use (internal-sdxl-turbo, internal-sd-turbo, etc.)
            width: Image width (default 512)
            height: Image height (default 512)
            num_images: Number of images to generate (default 1)
            num_inference_steps: Number of denoising steps (4 for turbo, 20-50 for standard)
            guidance_scale: Classifier-free guidance scale (0.0 for turbo, 7.5 for standard)
            negative_prompt: What to avoid in the image
            seed: Random seed for reproducibility
            
        Returns:
            Dictionary with generated images data
        """
        try:
            # Get model ID
            model_id = self._get_model_id(model)
            
            # Load model
            pipe = self._load_model(model_id)
            
            # Adjust parameters based on model type
            if "turbo" in model_id.lower():
                num_inference_steps = min(num_inference_steps, 4)
                guidance_scale = 0.0
            else:
                num_inference_steps = max(num_inference_steps, 20)
                guidance_scale = guidance_scale if guidance_scale > 0 else 7.5
            
            # Set seed for reproducibility
            generator = None
            if seed is not None:
                generator = torch.Generator(device=self.device).manual_seed(seed)
            
            # Generate images
            logger.info(f"🎨 Generating {num_images} image(s): {prompt[:50]}...")
            logger.info(f"📐 Size: {width}x{height}, Steps: {num_inference_steps}, Guidance: {guidance_scale}")
            
            generated_images = []
            
            for i in range(num_images):
                # Generate
                result = pipe(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    width=width,
                    height=height,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale,
                    generator=generator,
                    num_images_per_prompt=1
                )
                
                image = result.images[0]
                
                # Save image to file
                image_id = f"{uuid.uuid4().hex[:8]}"
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"ai_leader_{timestamp}_{image_id}.png"
                filepath = self.output_dir / filename
                
                image.save(filepath, format="PNG", optimize=True)
                
                # Convert to base64 for API response
                buffered = io.BytesIO()
                image.save(buffered, format="PNG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode()
                
                generated_images.append({
                    "url": f"data:image/png;base64,{img_base64}",
                    "filepath": str(filepath),
                    "filename": filename,
                    "width": width,
                    "height": height,
                    "seed": seed,
                    "cost": 0.0,
                    "provider": "AI Leader (Internal)"
                })
                
                logger.info(f"✅ Generated image {i+1}/{num_images}: {filename}")
            
            return {
                "success": True,
                "images": generated_images,
                "model": model,
                "model_id": model_id,
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "parameters": {
                    "width": width,
                    "height": height,
                    "num_inference_steps": num_inference_steps,
                    "guidance_scale": guidance_scale,
                    "seed": seed
                },
                "estimated_cost": 0.0,
                "actual_cost": 0.0,
                "generation_time": "~2-5s"
            }
            
        except Exception as e:
            logger.error(f"❌ Image generation failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "model": model,
                "prompt": prompt
            }
    
    def cleanup_old_images(self, max_age_hours: int = 24):
        """Clean up old generated images"""
        try:
            count = 0
            now = datetime.now()
            
            for filepath in self.output_dir.glob("*.png"):
                # Check file age
                file_time = datetime.fromtimestamp(filepath.stat().st_mtime)
                age_hours = (now - file_time).total_seconds() / 3600
                
                if age_hours > max_age_hours:
                    filepath.unlink()
                    count += 1
            
            if count > 0:
                logger.info(f"🧹 Cleaned up {count} old images")
                
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")


# Global instance
_generator = None

def get_internal_generator() -> InternalImageGenerator:
    """Get or create global generator instance"""
    global _generator
    if _generator is None:
        _generator = InternalImageGenerator()
    return _generator
