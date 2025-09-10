"""
Midjourney API Integration Module
=================================

Enterprise-grade integration with Midjourney API for AI image generation
Specialized for creator content workflows and business logic integration.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

Role Applied: Lead Dev IA + ML Engineer + AI Prompt Engineer
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import time

# Note: Using httpx instead of requests for async support
try:
    import httpx
except ImportError:
    httpx = None

logger = logging.getLogger(__name__)


class MidjourneyStatus(Enum):
    """Midjourney generation job status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MidjourneyStyle(Enum):
    """Midjourney artistic styles for content creation."""
    REALISTIC = "realistic"
    ARTISTIC = "artistic"
    ANIME = "anime"
    PHOTOGRAPHIC = "photographic"
    DIGITAL_ART = "digital_art"
    CONCEPT_ART = "concept_art"
    ILLUSTRATION = "illustration"
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"


@dataclass
class MidjourneyRequest:
    """Midjourney generation request configuration."""
    prompt: str
    style: MidjourneyStyle = MidjourneyStyle.ARTISTIC
    aspect_ratio: str = "1:1"  # 16:9, 4:3, 1:1, etc.
    quality: float = 1.0  # 0.25, 0.5, 1.0, 2.0
    chaos: int = 0  # 0-100, randomness level
    seed: Optional[int] = None
    no_text: bool = False
    upscale: bool = False
    variation: bool = False
    creator_id: Optional[str] = None
    creator_type: Optional[str] = None
    business_context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MidjourneyResult:
    """Midjourney generation result with business context."""
    job_id: str
    status: MidjourneyStatus
    image_urls: List[str] = field(default_factory=list)
    thumbnail_urls: List[str] = field(default_factory=list)
    progress: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    creator_workflow_status: str = "pending"
    monetization_ready: bool = False
    protection_applied: bool = False


class MidjourneyEnterpriseClient:
    """
    Enterprise Midjourney API client with creator workflow integration.
    
    Specialized for Ainflue platform business logic:
    - Creator content generation workflows
    - Brand-safe image generation
    - Monetization-ready outputs
    - Copyright protection integration
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.midjourney.com/v1",
        timeout: int = 300,
        max_retries: int = 3,
        enable_creator_workflows: bool = True
    ):
        """Initialize Midjourney client with enterprise configuration."""
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.enable_creator_workflows = enable_creator_workflows
        
        # Enterprise session configuration
        self.session = None
        if httpx:
            self.session = httpx.AsyncClient(
                timeout=httpx.Timeout(timeout),
                headers=self._get_headers()
            )
        
        # Rate limiting and monitoring
        self.request_count = 0
        self.last_request_time = None
        self.rate_limit_remaining = 100
        
        # Creator workflow integration
        self.creator_workflows = {
            "musician": self._configure_musician_workflow,
            "blogger": self._configure_blogger_workflow,
            "photographer": self._configure_photographer_workflow,
            "influencer": self._configure_influencer_workflow,
            "comedian": self._configure_comedian_workflow
        }
        
        logger.info("✅ Midjourney Enterprise Client initialized")

    def _get_headers(self) -> Dict[str, str]:
        """Generate request headers with authentication."""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Ainflue-Midjourney-Integration/1.0"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            
        return headers

    async def generate_image(
        self,
        request: MidjourneyRequest,
        monitor_progress: bool = True
    ) -> MidjourneyResult:
        """
        Generate image using Midjourney API with creator workflow integration.
        
        Args:
            request: Midjourney generation request
            monitor_progress: Whether to monitor generation progress
            
        Returns:
            MidjourneyResult with generation status and URLs
        """
        try:
            # Pre-generation creator workflow checks
            if self.enable_creator_workflows:
                await self._apply_creator_workflow_checks(request)
            
            # Rate limiting check
            await self._check_rate_limits()
            
            # Submit generation request
            job_id = await self._submit_generation_request(request)
            
            result = MidjourneyResult(
                job_id=job_id,
                status=MidjourneyStatus.PENDING,
                metadata={
                    "request": request.__dict__,
                    "submitted_at": datetime.now().isoformat()
                }
            )
            
            if monitor_progress:
                # Monitor generation progress
                result = await self._monitor_generation_progress(result)
                
                # Post-generation processing
                if result.status == MidjourneyStatus.COMPLETED:
                    await self._apply_post_generation_processing(result, request)
            
            logger.info(f"✅ Midjourney generation completed: {job_id}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Midjourney generation failed: {e}")
            return MidjourneyResult(
                job_id="",
                status=MidjourneyStatus.FAILED,
                error_message=str(e)
            )

    async def _submit_generation_request(self, request: MidjourneyRequest) -> str:
        """Submit image generation request to Midjourney API."""
        if not self.session:
            raise Exception("HTTP session not initialized")
            
        payload = {
            "prompt": request.prompt,
            "aspect_ratio": request.aspect_ratio,
            "quality": request.quality,
            "chaos": request.chaos,
            "style": request.style.value,
            "no_text": request.no_text
        }
        
        if request.seed:
            payload["seed"] = request.seed
            
        try:
            response = await self.session.post(
                f"{self.base_url}/imagine",
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            job_id = data.get("job_id", "")
            
            self._update_rate_limits(response)
            
            return job_id
            
        except Exception as e:
            logger.error(f"Failed to submit Midjourney request: {e}")
            raise

    async def _monitor_generation_progress(
        self,
        result: MidjourneyResult,
        check_interval: int = 10
    ) -> MidjourneyResult:
        """Monitor generation progress with real-time updates."""
        max_wait_time = 600  # 10 minutes maximum
        start_time = time.time()
        
        while (time.time() - start_time) < max_wait_time:
            try:
                status_data = await self._get_job_status(result.job_id)
                
                result.status = MidjourneyStatus(status_data.get("status", "pending"))
                result.progress = status_data.get("progress", 0.0)
                
                if result.status == MidjourneyStatus.COMPLETED:
                    result.image_urls = status_data.get("image_urls", [])
                    result.thumbnail_urls = status_data.get("thumbnail_urls", [])
                    result.completed_at = datetime.now()
                    break
                elif result.status == MidjourneyStatus.FAILED:
                    result.error_message = status_data.get("error", "Generation failed")
                    break
                    
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                logger.error(f"Error monitoring progress: {e}")
                await asyncio.sleep(check_interval)
        
        return result

    async def _get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get generation job status from Midjourney API."""
        if not self.session:
            return {"status": "pending", "progress": 0.0}
            
        try:
            response = await self.session.get(f"{self.base_url}/jobs/{job_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get job status: {e}")
            return {"status": "pending", "progress": 0.0}

    async def _apply_creator_workflow_checks(self, request: MidjourneyRequest) -> None:
        """Apply creator-specific workflow checks and modifications."""
        creator_type = request.creator_type
        
        if creator_type in self.creator_workflows:
            # Apply creator-specific configurations
            workflow_func = self.creator_workflows[creator_type]
            await workflow_func(request)
            
        # Business logic checks
        await self._apply_brand_safety_checks(request)
        await self._apply_monetization_readiness_checks(request)

    async def _configure_musician_workflow(self, request: MidjourneyRequest) -> None:
        """Configure Midjourney request for musician creators."""
        # Add music-related visual elements
        if "album" in request.prompt.lower() or "music" in request.prompt.lower():
            request.prompt += " --style album cover, professional music artwork"
            request.quality = max(request.quality, 1.0)  # High quality for album covers
            
        # Ensure monetization-friendly aspect ratios
        if request.aspect_ratio == "1:1":
            pass  # Perfect for album covers
        elif "cover" in request.prompt.lower():
            request.aspect_ratio = "1:1"  # Force square for album covers

    async def _configure_blogger_workflow(self, request: MidjourneyRequest) -> None:
        """Configure Midjourney request for blogger creators."""
        # Add blog-friendly visual elements
        request.prompt += " --style blog header, clean professional design"
        
        # Optimize for blog layouts
        if request.aspect_ratio == "1:1":
            request.aspect_ratio = "16:9"  # Better for blog headers

    async def _configure_photographer_workflow(self, request: MidjourneyRequest) -> None:
        """Configure Midjourney request for photographer creators."""
        # Enhance photographic style
        if request.style != MidjourneyStyle.PHOTOGRAPHIC:
            request.style = MidjourneyStyle.PHOTOGRAPHIC
            
        request.prompt += " --style photorealistic, professional photography"
        request.quality = 2.0  # Highest quality for photographers

    async def _configure_influencer_workflow(self, request: MidjourneyRequest) -> None:
        """Configure Midjourney request for influencer creators."""
        # Add social media optimization
        request.prompt += " --style social media ready, engaging visual"
        
        # Multiple aspect ratios for different platforms
        if "story" in request.prompt.lower():
            request.aspect_ratio = "9:16"  # Instagram stories
        elif "post" in request.prompt.lower():
            request.aspect_ratio = "1:1"   # Instagram posts

    async def _configure_comedian_workflow(self, request: MidjourneyRequest) -> None:
        """Configure Midjourney request for comedian creators."""
        # Add comedy-friendly visual elements
        request.prompt += " --style humorous, engaging, comedy content"
        request.chaos = min(request.chaos + 20, 100)  # Add creativity for comedy

    async def _apply_brand_safety_checks(self, request: MidjourneyRequest) -> None:
        """Apply brand safety and content policy checks."""
        # Add safety keywords to prevent inappropriate content
        safety_keywords = [
            "--no violence",
            "--no adult content", 
            "--no offensive material",
            "--brand safe"
        ]
        
        for keyword in safety_keywords:
            if keyword not in request.prompt:
                request.prompt += f" {keyword}"

    async def _apply_monetization_readiness_checks(self, request: MidjourneyRequest) -> None:
        """Ensure generated content is ready for monetization."""
        # Add commercial-ready specifications
        commercial_keywords = [
            "--commercial use",
            "--high resolution",
            "--professional quality"
        ]
        
        for keyword in commercial_keywords:
            if keyword not in request.prompt:
                request.prompt += f" {keyword}"

    async def _apply_post_generation_processing(
        self,
        result: MidjourneyResult,
        request: MidjourneyRequest
    ) -> None:
        """Apply post-generation processing for creator workflows."""
        # Mark as monetization ready if quality criteria met
        if len(result.image_urls) > 0 and request.quality >= 1.0:
            result.monetization_ready = True
            
        # Update creator workflow status
        if request.creator_type:
            result.creator_workflow_status = "completed"
            
        # Add protection metadata
        result.metadata.update({
            "creator_id": request.creator_id,
            "creator_type": request.creator_type,
            "generation_timestamp": datetime.now().isoformat(),
            "business_context": request.business_context
        })

    async def _check_rate_limits(self) -> None:
        """Check and enforce API rate limits."""
        current_time = time.time()
        
        if self.last_request_time:
            time_diff = current_time - self.last_request_time
            if time_diff < 1.0:  # Minimum 1 second between requests
                await asyncio.sleep(1.0 - time_diff)
                
        self.last_request_time = current_time
        self.request_count += 1

    def _update_rate_limits(self, response) -> None:
        """Update rate limit counters from API response."""
        headers = response.headers
        self.rate_limit_remaining = int(headers.get("X-RateLimit-Remaining", 100))

    async def upscale_image(self, job_id: str, image_index: int = 0) -> MidjourneyResult:
        """Upscale a generated image for high-resolution output."""
        try:
            if not self.session:
                raise Exception("HTTP session not initialized")
                
            payload = {
                "job_id": job_id,
                "action": "upscale",
                "index": image_index
            }
            
            response = await self.session.post(
                f"{self.base_url}/actions",
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            upscale_job_id = data.get("job_id", "")
            
            # Monitor upscale progress
            result = MidjourneyResult(
                job_id=upscale_job_id,
                status=MidjourneyStatus.PENDING
            )
            
            result = await self._monitor_generation_progress(result)
            
            logger.info(f"✅ Midjourney upscale completed: {upscale_job_id}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Midjourney upscale failed: {e}")
            return MidjourneyResult(
                job_id="",
                status=MidjourneyStatus.FAILED,
                error_message=str(e)
            )

    async def create_variations(self, job_id: str, image_index: int = 0) -> MidjourneyResult:
        """Create variations of a generated image."""
        try:
            if not self.session:
                raise Exception("HTTP session not initialized")
                
            payload = {
                "job_id": job_id,
                "action": "variation",
                "index": image_index
            }
            
            response = await self.session.post(
                f"{self.base_url}/actions",
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            variation_job_id = data.get("job_id", "")
            
            # Monitor variation progress
            result = MidjourneyResult(
                job_id=variation_job_id,
                status=MidjourneyStatus.PENDING
            )
            
            result = await self._monitor_generation_progress(result)
            
            logger.info(f"✅ Midjourney variations completed: {variation_job_id}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Midjourney variations failed: {e}")
            return MidjourneyResult(
                job_id="",
                status=MidjourneyStatus.FAILED,
                error_message=str(e)
            )

    async def get_account_info(self) -> Dict[str, Any]:
        """Get Midjourney account information and usage stats."""
        try:
            if not self.session:
                return {"error": "HTTP session not initialized"}
                
            response = await self.session.get(f"{self.base_url}/account")
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to get account info: {e}")
            return {"error": str(e)}

    async def close(self) -> None:
        """Clean up resources and close connections."""
        if self.session:
            await self.session.aclose()
            self.session = None
            
        logger.info("✅ Midjourney client closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


# Factory function for easy instantiation
def create_midjourney_client(
    api_key: Optional[str] = None,
    enable_creator_workflows: bool = True
) -> MidjourneyEnterpriseClient:
    """
    Factory function to create Midjourney client with enterprise configuration.
    
    Args:
        api_key: Midjourney API key
        enable_creator_workflows: Enable creator-specific workflows
        
    Returns:
        Configured MidjourneyEnterpriseClient instance
    """
    return MidjourneyEnterpriseClient(
        api_key=api_key,
        enable_creator_workflows=enable_creator_workflows
    )


# Example usage for creator workflows
async def example_creator_image_generation():
    """Example of creator-specific image generation workflow."""
    try:
        client = create_midjourney_client(api_key="your-api-key")
        
        # Musician album cover generation
        musician_request = MidjourneyRequest(
            prompt="electronic music album cover, futuristic synthwave aesthetic",
            style=MidjourneyStyle.DIGITAL_ART,
            aspect_ratio="1:1",
            quality=2.0,
            creator_type="musician",
            creator_id="musician_123",
            business_context={"album_name": "Neon Dreams", "genre": "synthwave"}
        )
        
        result = await client.generate_image(musician_request)
        
        if result.status == MidjourneyStatus.COMPLETED:
            print(f"✅ Album cover generated: {result.image_urls[0]}")
            print(f"📊 Monetization ready: {result.monetization_ready}")
            
            # Upscale for high-resolution album cover
            if result.monetization_ready:
                upscaled = await client.upscale_image(result.job_id, 0)
                print(f"🎯 High-res version: {upscaled.image_urls[0]}")
        
        await client.close()
        
    except Exception as e:
        logger.error(f"Example failed: {e}")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_creator_image_generation())