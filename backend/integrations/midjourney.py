"""Midjourney Integration - AI Image Generation
=============================================

Professional Midjourney API integration for high-quality AI image generation,
style transfers, and creative content creation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass
import json
import aiohttp
import time

logger = logging.getLogger(__name__)


class MidjourneyAction(str, Enum):
    """Midjourney action types."""
    IMAGINE = "imagine"
    UPSCALE = "upscale"
    VARIATION = "variation"
    REROLL = "reroll"
    PAN = "pan"
    ZOOM = "zoom"
    DESCRIBE = "describe"


class ImageQuality(str, Enum):
    """Image quality settings."""
    LOW = "0.25"
    MEDIUM = "0.5"
    HIGH = "1"
    ULTRA = "2"


class AspectRatio(str, Enum):
    """Aspect ratio options."""
    SQUARE = "1:1"
    PORTRAIT = "2:3"
    LANDSCAPE = "3:2"
    WIDE = "16:9"
    ULTRAWIDE = "21:9"
    VERTICAL = "9:16"


class StylePreset(str, Enum):
    """Style preset options."""
    RAW = "raw"
    ANIME = "anime"
    PHOTOGRAPHIC = "photographic"
    DIGITAL_ART = "digital-art"
    COMIC_BOOK = "comic-book"
    FANTASY_ART = "fantasy-art"
    LINE_ART = "line-art"
    ANALOG_FILM = "analog-film"
    NEON_PUNK = "neon-punk"
    ISOMETRIC = "isometric"
    LOW_POLY = "low-poly"
    ORIGAMI = "origami"
    WATERCOLOR = "watercolor"
    PENCIL_SKETCH = "pencil-sketch"


@dataclass
class MidjourneyPrompt:
    """Midjourney prompt configuration."""
    text: str
    aspect_ratio: Optional[AspectRatio] = None
    quality: Optional[ImageQuality] = None
    style: Optional[StylePreset] = None
    chaos: Optional[int] = None  # 0-100
    weird: Optional[int] = None  # 0-3000
    stylize: Optional[int] = None  # 0-1000
    seed: Optional[int] = None
    model_version: Optional[str] = None
    no_words: Optional[List[str]] = None  # Negative prompts
    
    def to_prompt_string(self) -> str:
        """Convert to Midjourney prompt string."""
        prompt = self.text
        
        if self.aspect_ratio:
            prompt += f" --ar {self.aspect_ratio.value}"
        
        if self.quality:
            prompt += f" --q {self.quality.value}"
        
        if self.style:
            prompt += f" --style {self.style.value}"
        
        if self.chaos is not None:
            prompt += f" --chaos {self.chaos}"
        
        if self.weird is not None:
            prompt += f" --weird {self.weird}"
        
        if self.stylize is not None:
            prompt += f" --stylize {self.stylize}"
        
        if self.seed is not None:
            prompt += f" --seed {self.seed}"
        
        if self.model_version:
            prompt += f" --v {self.model_version}"
        
        if self.no_words:
            prompt += f" --no {', '.join(self.no_words)}"
        
        return prompt


@dataclass
class MidjourneyJob:
    """Midjourney job tracking."""
    job_id: str
    action: MidjourneyAction
    prompt: str
    status: str
    progress: int
    image_urls: List[str]
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]
    error_message: Optional[str] = None


@dataclass
class MidjourneyImage:
    """Midjourney generated image."""
    image_id: str
    url: str
    proxy_url: Optional[str]
    filename: str
    width: int
    height: int
    size_bytes: int
    job_id: str
    prompt: str
    index: int  # Position in grid (1-4)
    created_at: datetime
    metadata: Dict[str, Any]


class MidjourneyIntegration:
    """Professional Midjourney API integration."""
    
    def __init__(
        self,
        api_token: str,
        server_id: str,
        channel_id: str,
        base_url: str = "https://api.midjourney.com/v1",
        timeout: int = 300,  # 5 minutes for image generation
        max_retries: int = 3
    ):
        self.api_token = api_token
        self.server_id = server_id
        self.channel_id = channel_id
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Job tracking
        self.active_jobs: Dict[str, MidjourneyJob] = {}
        self.completed_jobs: List[MidjourneyJob] = []
        self.generation_count = 0
        self.request_count = 0
        
        logger.info("Midjourney integration initialized")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def _ensure_session(self):
        """Ensure HTTP session is available."""
        if self.session is None or self.session.closed:
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json",
                "User-Agent": "Ainflue/1.0"
            }
            
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
    
    async def close(self):
        """Close HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def imagine(
        self,
        prompt: Union[str, MidjourneyPrompt],
        wait_for_completion: bool = True,
        polling_interval: int = 10,
        metadata: Optional[Dict[str, Any]] = None
    ) -> MidjourneyJob:
        """Generate images from text prompt."""
        await self._ensure_session()
        
        # Convert prompt to string if needed
        if isinstance(prompt, MidjourneyPrompt):
            prompt_str = prompt.to_prompt_string()
        else:
            prompt_str = prompt
        
        data = {
            "type": "imagine",
            "prompt": prompt_str,
            "server_id": self.server_id,
            "channel_id": self.channel_id
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/submit/imagine",
                json=data
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"Midjourney API error: {error_data}")
                
                result = await response.json()
                job_id = result["messageId"]
                
                # Create job tracking
                job = MidjourneyJob(
                    job_id=job_id,
                    action=MidjourneyAction.IMAGINE,
                    prompt=prompt_str,
                    status="submitted",
                    progress=0,
                    image_urls=[],
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    metadata=metadata or {}
                )
                
                self.active_jobs[job_id] = job
                self.request_count += 1
                
                logger.info(f"Imagine job submitted: {job_id}")
                
                if wait_for_completion:
                    return await self._wait_for_completion(job_id, polling_interval)
                else:
                    return job
        
        except Exception as e:
            logger.error(f"Imagine request failed: {e}")
            raise
    
    async def upscale(
        self,
        job_id: str,
        index: int,
        wait_for_completion: bool = True,
        polling_interval: int = 10,
        metadata: Optional[Dict[str, Any]] = None
    ) -> MidjourneyJob:
        """Upscale a specific image from a grid."""
        await self._ensure_session()
        
        data = {
            "type": "upscale",
            "index": index,
            "messageId": job_id,
            "server_id": self.server_id,
            "channel_id": self.channel_id
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/submit/action",
                json=data
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"Midjourney upscale error: {error_data}")
                
                result = await response.json()
                new_job_id = result["messageId"]
                
                # Create upscale job tracking
                original_job = self.active_jobs.get(job_id) or self._find_completed_job(job_id)
                original_prompt = original_job.prompt if original_job else f"Upscale from {job_id}"
                
                job = MidjourneyJob(
                    job_id=new_job_id,
                    action=MidjourneyAction.UPSCALE,
                    prompt=f"{original_prompt} (upscale {index})",
                    status="submitted",
                    progress=0,
                    image_urls=[],
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    metadata=metadata or {}
                )
                
                self.active_jobs[new_job_id] = job
                self.request_count += 1
                
                logger.info(f"Upscale job submitted: {new_job_id}")
                
                if wait_for_completion:
                    return await self._wait_for_completion(new_job_id, polling_interval)
                else:
                    return job
        
        except Exception as e:
            logger.error(f"Upscale request failed: {e}")
            raise
    
    async def variation(
        self,
        job_id: str,
        index: int,
        wait_for_completion: bool = True,
        polling_interval: int = 10,
        metadata: Optional[Dict[str, Any]] = None
    ) -> MidjourneyJob:
        """Create variations of a specific image."""
        await self._ensure_session()
        
        data = {
            "type": "variation",
            "index": index,
            "messageId": job_id,
            "server_id": self.server_id,
            "channel_id": self.channel_id
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/submit/action",
                json=data
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"Midjourney variation error: {error_data}")
                
                result = await response.json()
                new_job_id = result["messageId"]
                
                # Create variation job tracking
                original_job = self.active_jobs.get(job_id) or self._find_completed_job(job_id)
                original_prompt = original_job.prompt if original_job else f"Variation from {job_id}"
                
                job = MidjourneyJob(
                    job_id=new_job_id,
                    action=MidjourneyAction.VARIATION,
                    prompt=f"{original_prompt} (variation {index})",
                    status="submitted",
                    progress=0,
                    image_urls=[],
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    metadata=metadata or {}
                )
                
                self.active_jobs[new_job_id] = job
                self.request_count += 1
                
                logger.info(f"Variation job submitted: {new_job_id}")
                
                if wait_for_completion:
                    return await self._wait_for_completion(new_job_id, polling_interval)
                else:
                    return job
        
        except Exception as e:
            logger.error(f"Variation request failed: {e}")
            raise
    
    async def describe(
        self,
        image_url: str,
        wait_for_completion: bool = True,
        polling_interval: int = 10,
        metadata: Optional[Dict[str, Any]] = None
    ) -> MidjourneyJob:
        """Generate text description from image."""
        await self._ensure_session()
        
        data = {
            "type": "describe",
            "image_url": image_url,
            "server_id": self.server_id,
            "channel_id": self.channel_id
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/submit/describe",
                json=data
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"Midjourney describe error: {error_data}")
                
                result = await response.json()
                job_id = result["messageId"]
                
                # Create describe job tracking
                job = MidjourneyJob(
                    job_id=job_id,
                    action=MidjourneyAction.DESCRIBE,
                    prompt=f"Describe: {image_url}",
                    status="submitted",
                    progress=0,
                    image_urls=[],
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    metadata=metadata or {}
                )
                
                self.active_jobs[job_id] = job
                self.request_count += 1
                
                logger.info(f"Describe job submitted: {job_id}")
                
                if wait_for_completion:
                    return await self._wait_for_completion(job_id, polling_interval)
                else:
                    return job
        
        except Exception as e:
            logger.error(f"Describe request failed: {e}")
            raise
    
    async def get_job_status(self, job_id: str) -> Optional[MidjourneyJob]:
        """Get current status of a job."""
        await self._ensure_session()
        
        try:
            async with self.session.get(f"{self.base_url}/message/{job_id}") as response:
                if response.status == 404:
                    return None
                elif response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"Midjourney status error: {error_data}")
                
                result = await response.json()
                
                # Update job if we're tracking it
                if job_id in self.active_jobs:
                    job = self.active_jobs[job_id]
                    job.status = result.get("status", "unknown")
                    job.progress = result.get("progress", 0)
                    job.updated_at = datetime.now()
                    
                    if result.get("attachments"):
                        job.image_urls = [att["url"] for att in result["attachments"]]
                    
                    if result.get("content"):
                        job.metadata["content"] = result["content"]
                    
                    # Move to completed if done
                    if job.status in ["completed", "failed"]:
                        self.completed_jobs.append(job)
                        del self.active_jobs[job_id]
                        
                        if job.status == "completed":
                            self.generation_count += len(job.image_urls)
                    
                    return job
                else:
                    # Create job from response
                    return self._job_from_response(job_id, result)
        
        except Exception as e:
            logger.error(f"Failed to get job status: {e}")
            raise
    
    async def _wait_for_completion(
        self,
        job_id: str,
        polling_interval: int = 10,
        max_wait_time: int = 600  # 10 minutes
    ) -> MidjourneyJob:
        """Wait for job completion with polling."""
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            job = await self.get_job_status(job_id)
            
            if job is None:
                raise Exception(f"Job {job_id} not found")
            
            if job.status == "completed":
                logger.info(f"Job completed: {job_id}")
                return job
            elif job.status == "failed":
                error_msg = job.error_message or "Job failed"
                logger.error(f"Job failed: {job_id} - {error_msg}")
                raise Exception(f"Job failed: {error_msg}")
            
            logger.info(f"Job {job_id} progress: {job.progress}%")
            await asyncio.sleep(polling_interval)
        
        raise Exception(f"Job {job_id} timed out after {max_wait_time} seconds")
    
    def _job_from_response(self, job_id: str, response: Dict[str, Any]) -> MidjourneyJob:
        """Create job object from API response."""
        image_urls = []
        if response.get("attachments"):
            image_urls = [att["url"] for att in response["attachments"]]
        
        return MidjourneyJob(
            job_id=job_id,
            action=MidjourneyAction.IMAGINE,  # Default
            prompt=response.get("content", ""),
            status=response.get("status", "unknown"),
            progress=response.get("progress", 0),
            image_urls=image_urls,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={"response": response}
        )
    
    def _find_completed_job(self, job_id: str) -> Optional[MidjourneyJob]:
        """Find job in completed jobs list."""
        for job in self.completed_jobs:
            if job.job_id == job_id:
                return job
        return None
    
    async def get_images_from_job(self, job_id: str) -> List[MidjourneyImage]:
        """Extract individual images from job."""
        job = await self.get_job_status(job_id)
        if not job or not job.image_urls:
            return []
        
        images = []
        for i, url in enumerate(job.image_urls):
            image = MidjourneyImage(
                image_id=f"{job_id}_{i}",
                url=url,
                proxy_url=None,
                filename=f"midjourney_{job_id}_{i}.png",
                width=1024,  # Default, would need to fetch actual dimensions
                height=1024,
                size_bytes=0,  # Would need to fetch actual size
                job_id=job_id,
                prompt=job.prompt,
                index=i + 1,
                created_at=job.created_at,
                metadata=job.metadata
            )
            images.append(image)
        
        return images
    
    async def download_image(self, image_url: str) -> bytes:
        """Download image data from URL."""
        await self._ensure_session()
        
        try:
            async with self.session.get(image_url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to download image: {response.status}")
                
                image_data = await response.read()
                logger.info(f"Downloaded image: {len(image_data)} bytes")
                return image_data
        
        except Exception as e:
            logger.error(f"Image download failed: {e}")
            raise
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return {
            "total_requests": self.request_count,
            "images_generated": self.generation_count,
            "active_jobs": len(self.active_jobs),
            "completed_jobs": len(self.completed_jobs),
            "jobs_by_action": self._get_jobs_breakdown()
        }
    
    def _get_jobs_breakdown(self) -> Dict[str, int]:
        """Get breakdown of jobs by action type."""
        breakdown = {}
        
        for job in list(self.active_jobs.values()) + self.completed_jobs:
            action = job.action.value
            breakdown[action] = breakdown.get(action, 0) + 1
        
        return breakdown
    
    def get_active_jobs(self) -> List[MidjourneyJob]:
        """Get list of currently active jobs."""
        return list(self.active_jobs.values())
    
    def get_completed_jobs(self) -> List[MidjourneyJob]:
        """Get list of completed jobs."""
        return self.completed_jobs.copy()


# Utility functions
async def create_midjourney_integration(
    api_token: str,
    server_id: str,
    channel_id: str
) -> MidjourneyIntegration:
    """Create and initialize Midjourney integration."""
    integration = MidjourneyIntegration(
        api_token=api_token,
        server_id=server_id,
        channel_id=channel_id
    )
    await integration._ensure_session()
    return integration


async def quick_image_generation(
    prompt: str,
    api_token: str,
    server_id: str,
    channel_id: str,
    aspect_ratio: AspectRatio = AspectRatio.SQUARE
) -> List[str]:
    """Quick image generation utility."""
    mj_prompt = MidjourneyPrompt(text=prompt, aspect_ratio=aspect_ratio)
    
    async with MidjourneyIntegration(api_token, server_id, channel_id) as midjourney:
        job = await midjourney.imagine(mj_prompt, wait_for_completion=True)
        return job.image_urls


if __name__ == "__main__":
    # Example usage
    async def main():
        import os
        api_token = os.getenv("MIDJOURNEY_API_TOKEN")
        server_id = os.getenv("MIDJOURNEY_SERVER_ID")
        channel_id = os.getenv("MIDJOURNEY_CHANNEL_ID")
        
        if not all([api_token, server_id, channel_id]):
            print("Please set MIDJOURNEY_API_TOKEN, MIDJOURNEY_SERVER_ID, and MIDJOURNEY_CHANNEL_ID")
            return
        
        async with MidjourneyIntegration(api_token, server_id, channel_id) as midjourney:
            # Test image generation
            prompt = MidjourneyPrompt(
                text="A beautiful sunset over mountains",
                aspect_ratio=AspectRatio.LANDSCAPE,
                quality=ImageQuality.HIGH,
                style=StylePreset.PHOTOGRAPHIC
            )
            
            job = await midjourney.imagine(prompt, wait_for_completion=True)
            print(f"Generated {len(job.image_urls)} images")
            
            # Test usage stats
            stats = midjourney.get_usage_stats()
            print(f"Usage stats: {stats}")
    
    asyncio.run(main())