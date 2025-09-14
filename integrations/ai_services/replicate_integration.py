"""
Replicate API Integration Module
================================

Enterprise-grade integration with Replicate model hosting platform
Specialized for AI model deployment, serving, and creator workflows.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

Role Applied: ML Engineer + Lead Dev IA + DevOps Engineer
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import time

try:
    import httpx
except ImportError:
    httpx = None

logger = logging.getLogger(__name__)


class ReplicateModelType(Enum):
    """Replicate model categories for different use cases."""
    TEXT_GENERATION = "text-generation"
    IMAGE_GENERATION = "image-generation"
    IMAGE_TO_IMAGE = "image-to-image"
    TEXT_TO_IMAGE = "text-to-image"
    AUDIO_GENERATION = "audio-generation"
    VIDEO_GENERATION = "video-generation"
    STYLE_TRANSFER = "style-transfer"
    UPSCALING = "upscaling"
    INPAINTING = "inpainting"
    FACE_RESTORATION = "face-restoration"
    BACKGROUND_REMOVAL = "background-removal"
    VOICE_CLONING = "voice-cloning"


class PredictionStatus(Enum):
    """Replicate prediction status enumeration."""
    STARTING = "starting"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"


@dataclass
class ReplicateModel:
    """Replicate model configuration and metadata."""
    owner: str
    name: str
    version: Optional[str] = None
    model_type: Optional[ReplicateModelType] = None
    description: str = ""
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    cost_per_run: float = 0.0
    avg_runtime: float = 0.0
    creator_friendly: bool = False
    business_tier: bool = False


@dataclass
class ReplicatePrediction:
    """Replicate prediction request and result."""
    id: str = ""
    model: Optional[ReplicateModel] = None
    input: Dict[str, Any] = field(default_factory=dict)
    output: Optional[Any] = None
    status: PredictionStatus = PredictionStatus.STARTING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    logs: str = ""
    metrics: Dict[str, Any] = field(default_factory=dict)
    creator_context: Dict[str, Any] = field(default_factory=dict)
    business_metadata: Dict[str, Any] = field(default_factory=dict)


class ReplicateEnterpriseClient:
    """
    Enterprise Replicate API client with creator workflow integration.
    
    Specialized for Ainflue platform business logic:
    - Multi-model AI deployment and serving
    - Creator-specific model recommendations
    - Cost optimization for business workflows
    - Performance monitoring and analytics
    """
    
    def __init__(
        self,
        api_token -> None: Optional[str] = None,
        base_url -> None: str = "https -> None://api.replicate.com/v1",
        timeout -> None: int = 300,
        max_retries -> None: int = 3,
        enable_cost_optimization -> None: bool = True,
        enable_creator_recommendations -> None: bool = True
    ) -> None:
        """Initialize Replicate client with enterprise configuration."""
        self.api_token = api_token
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.enable_cost_optimization = enable_cost_optimization
        self.enable_creator_recommendations = enable_creator_recommendations
        
        # Enterprise session configuration
        self.session = None
        if httpx:
            self.session = httpx.AsyncClient(
                timeout=httpx.Timeout(timeout),
                headers=self._get_headers()
            )
        
        # Model registry and recommendations
        self.model_registry = self._initialize_model_registry()
        self.creator_model_recommendations = self._initialize_creator_recommendations()
        
        # Performance monitoring
        self.prediction_history = []
        self.cost_tracking = {
            "total_cost": 0.0,
            "predictions_count": 0,
            "avg_cost_per_prediction": 0.0
        }
        
        logger.info("✅ Replicate Enterprise Client initialized")

    def _get_headers(self) -> Dict[str, str]:
        """Generate request headers with authentication."""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Ainflue-Replicate-Integration/1.0"
        }
        
        if self.api_token:
            headers["Authorization"] = f"Token {self.api_token}"
            
        return headers

    def _initialize_model_registry(self) -> Dict[str, ReplicateModel]:
        """Initialize registry of recommended models for creators."""
        return {
            # Image Generation Models
            "stable-diffusion-xl": ReplicateModel(
                owner="stability-ai",
                name="sdxl",
                version="39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
                model_type=ReplicateModelType.TEXT_TO_IMAGE,
                description="High-quality image generation from text",
                cost_per_run=0.00285,
                avg_runtime=4.5,
                creator_friendly=True,
                business_tier=True
            ),
            
            "dall-e-3": ReplicateModel(
                owner="openai",
                name="dall-e-3",
                model_type=ReplicateModelType.TEXT_TO_IMAGE,
                description="OpenAI's DALL-E 3 for creative image generation",
                cost_per_run=0.04,
                avg_runtime=10.0,
                creator_friendly=True,
                business_tier=True
            ),
            
            # Image Enhancement Models
            "real-esrgan": ReplicateModel(
                owner="nightmareai",
                name="real-esrgan",
                version="42fed1c4974146d4d2414e2be2c5277c7fcf05fcc3a73abf41610695738c1d7b",
                model_type=ReplicateModelType.UPSCALING,
                description="4x upscaling for images",
                cost_per_run=0.00348,
                avg_runtime=8.2,
                creator_friendly=True,
                business_tier=False
            ),
            
            # Background Removal
            "rembg": ReplicateModel(
                owner="cjwbw",
                name="rembg",
                version="fb8af171cfa1616ddcf1242c093f9c46bcada5ad4cf6f2fbe8b81b330ec5c003",
                model_type=ReplicateModelType.BACKGROUND_REMOVAL,
                description="Remove background from images",
                cost_per_run=0.00056,
                avg_runtime=2.1,
                creator_friendly=True,
                business_tier=False
            ),
            
            # Style Transfer
            "neural-style-transfer": ReplicateModel(
                owner="riffusion",
                name="neural-style-transfer",
                model_type=ReplicateModelType.STYLE_TRANSFER,
                description="Apply artistic styles to images",
                cost_per_run=0.0023,
                avg_runtime=15.3,
                creator_friendly=True,
                business_tier=False
            ),
            
            # Audio Generation
            "musicgen": ReplicateModel(
                owner="meta",
                name="musicgen",
                version="b05b1dff1d8c6dc63d14b0cdb42135378dcb87f6373b0d3d341ede46e59e2dbe",
                model_type=ReplicateModelType.AUDIO_GENERATION,
                description="Generate music from text descriptions",
                cost_per_run=0.00325,
                avg_runtime=28.7,
                creator_friendly=True,
                business_tier=True
            ),
            
            # Text Generation
            "llama-2-70b": ReplicateModel(
                owner="meta",
                name="llama-2-70b-chat",
                version="02e509c789964a7ea8736978a43525956ef40397be9033abf9fd2badfe68c9e3",
                model_type=ReplicateModelType.TEXT_GENERATION,
                description="Large language model for text generation",
                cost_per_run=0.00065,
                avg_runtime=3.2,
                creator_friendly=True,
                business_tier=True
            ),
            
            # Video Generation
            "stable-video-diffusion": ReplicateModel(
                owner="stability-ai",
                name="stable-video-diffusion",
                model_type=ReplicateModelType.VIDEO_GENERATION,
                description="Generate videos from images",
                cost_per_run=0.0212,
                avg_runtime=120.5,
                creator_friendly=True,
                business_tier=True
            )
        }

    def _initialize_creator_recommendations(self) -> Dict[str, List[str]]:
        """Initialize model recommendations for different creator types."""
        return {
            "musician": [
                "musicgen",
                "stable-diffusion-xl",  # Album covers
                "rembg",                # Clean artist photos
                "real-esrgan"           # High-quality artwork
            ],
            "blogger": [
                "llama-2-70b",         # Content generation
                "stable-diffusion-xl",  # Blog graphics
                "rembg",                # Clean photos
                "neural-style-transfer" # Unique visuals
            ],
            "photographer": [
                "real-esrgan",          # Image enhancement
                "rembg",                # Background removal
                "neural-style-transfer", # Artistic effects
                "stable-diffusion-xl"   # Creative concepts
            ],
            "influencer": [
                "stable-diffusion-xl",  # Social media content
                "rembg",                # Profile photos
                "stable-video-diffusion", # Video content
                "real-esrgan"           # High-quality images
            ],
            "comedian": [
                "stable-diffusion-xl",  # Meme generation
                "llama-2-70b",         # Joke writing
                "stable-video-diffusion", # Comedy videos
                "rembg"                 # Profile photos
            ]
        }

    async def create_prediction(
        self,
        model_name: str,
        input_data: Dict[str, Any],
        webhook_url: Optional[str] = None,
        creator_context: Optional[Dict[str, Any]] = None
    ) -> ReplicatePrediction:
        """
        Create a new prediction with creator workflow integration.
        
        Args:
            model_name: Name of the model to use
            input_data: Input parameters for the model
            webhook_url: Optional webhook URL for completion notification
            creator_context: Creator workflow context
            
        Returns:
            ReplicatePrediction object with prediction details
        """
        try:
            # Get model configuration
            model = self._get_model_config(model_name)
            if not model:
                raise ValueError(f"Model '{model_name}' not found in registry")
            
            # Apply creator workflow optimizations
            if creator_context and self.enable_creator_recommendations:
                input_data = await self._apply_creator_optimizations(
                    model, input_data, creator_context
                )
            
            # Create prediction request
            prediction_data = {
                "version": model.version or f"{model.owner}/{model.name}",
                "input": input_data
            }
            
            if webhook_url:
                prediction_data["webhook"] = webhook_url
            
            # Submit prediction
            if not self.session:
                raise Exception("HTTP session not initialized")
                
            response = await self.session.post(
                f"{self.base_url}/predictions",
                json=prediction_data
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Create prediction object
            prediction = ReplicatePrediction(
                id=data.get("id", ""),
                model=model,
                input=input_data,
                status=PredictionStatus(data.get("status", "starting")),
                created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
                creator_context=creator_context or {},
                business_metadata={
                    "model_cost": model.cost_per_run,
                    "estimated_runtime": model.avg_runtime
                }
            )
            
            # Track for cost optimization
            self._track_prediction(prediction)
            
            logger.info(f"✅ Replicate prediction created: {prediction.id}")
            return prediction
            
        except Exception as e:
            logger.error(f"❌ Failed to create prediction: {e}")
            raise

    async def get_prediction(self, prediction_id: str) -> ReplicatePrediction:
        """Get prediction status and results."""
        try:
            if not self.session:
                raise Exception("HTTP session not initialized")
                
            response = await self.session.get(f"{self.base_url}/predictions/{prediction_id}")
            response.raise_for_status()
            
            data = response.json()
            
            # Update prediction object
            prediction = ReplicatePrediction(
                id=data.get("id", ""),
                input=data.get("input", {}),
                output=data.get("output"),
                status=PredictionStatus(data.get("status", "starting")),
                created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
                error=data.get("error"),
                logs=data.get("logs", ""),
                metrics=data.get("metrics", {})
            )
            
            # Parse timestamps
            if data.get("started_at"):
                prediction.started_at = datetime.fromisoformat(data["started_at"])
            if data.get("completed_at"):
                prediction.completed_at = datetime.fromisoformat(data["completed_at"])
            
            return prediction
            
        except Exception as e:
            logger.error(f"❌ Failed to get prediction: {e}")
            raise

    async def wait_for_prediction(
        self,
        prediction_id: str,
        poll_interval: int = 5,
        timeout: int = 300
    ) -> ReplicatePrediction:
        """Wait for prediction to complete with polling."""
        start_time = time.time()
        
        while (time.time() - start_time) < timeout:
            prediction = await self.get_prediction(prediction_id)
            
            if prediction.status in [PredictionStatus.SUCCEEDED, PredictionStatus.FAILED, PredictionStatus.CANCELED]:
                # Apply post-processing for creators
                if prediction.creator_context:
                    await self._apply_post_processing(prediction)
                    
                return prediction
            
            await asyncio.sleep(poll_interval)
        
        raise TimeoutError(f"Prediction {prediction_id} timed out after {timeout} seconds")

    async def cancel_prediction(self, prediction_id: str) -> bool:
        """Cancel a running prediction."""
        try:
            if not self.session:
                raise Exception("HTTP session not initialized")
                
            response = await self.session.post(f"{self.base_url}/predictions/{prediction_id}/cancel")
            response.raise_for_status()
            
            logger.info(f"✅ Prediction cancelled: {prediction_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to cancel prediction: {e}")
            return False

    async def get_models(self, creator_type: Optional[str] = None) -> List[ReplicateModel]:
        """Get available models, optionally filtered by creator type."""
        if creator_type and creator_type in self.creator_model_recommendations:
            # Return recommended models for creator type
            recommended_names = self.creator_model_recommendations[creator_type]
            return [
                self.model_registry[name] 
                for name in recommended_names 
                if name in self.model_registry
            ]
        
        # Return all models
        return list(self.model_registry.values())

    async def get_model_recommendations(
        self,
        creator_type: str,
        use_case: Optional[str] = None,
        budget_constraint: Optional[float] = None
    ) -> List[ReplicateModel]:
        """Get model recommendations for specific creator and use case."""
        if creator_type not in self.creator_model_recommendations:
            return []
        
        recommended_models = await self.get_models(creator_type)
        
        # Filter by use case
        if use_case:
            use_case_mapping = {
                "content_creation": [ReplicateModelType.TEXT_TO_IMAGE, ReplicateModelType.TEXT_GENERATION],
                "image_enhancement": [ReplicateModelType.UPSCALING, ReplicateModelType.BACKGROUND_REMOVAL],
                "artistic_effects": [ReplicateModelType.STYLE_TRANSFER, ReplicateModelType.IMAGE_TO_IMAGE],
                "music_production": [ReplicateModelType.AUDIO_GENERATION],
                "video_content": [ReplicateModelType.VIDEO_GENERATION]
            }
            
            if use_case in use_case_mapping:
                target_types = use_case_mapping[use_case]
                recommended_models = [
                    model for model in recommended_models 
                    if model.model_type in target_types
                ]
        
        # Filter by budget constraint
        if budget_constraint:
            recommended_models = [
                model for model in recommended_models 
                if model.cost_per_run <= budget_constraint
            ]
        
        # Sort by creator-friendliness and cost
        recommended_models.sort(
            key=lambda m: (not m.creator_friendly, m.cost_per_run)
        )
        
        return recommended_models

    async def _apply_creator_optimizations(
        self,
        model: ReplicateModel,
        input_data: Dict[str, Any],
        creator_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply creator-specific optimizations to input parameters."""
        creator_type = creator_context.get("creator_type", "")
        
        if model.model_type == ReplicateModelType.TEXT_TO_IMAGE:
            if creator_type == "musician":
                # Optimize for album covers
                input_data = self._optimize_for_album_covers(input_data)
            elif creator_type == "blogger":
                # Optimize for blog graphics
                input_data = self._optimize_for_blog_graphics(input_data)
            elif creator_type == "photographer":
                # Optimize for artistic photography
                input_data = self._optimize_for_photography(input_data)
            elif creator_type == "influencer":
                # Optimize for social media
                input_data = self._optimize_for_social_media(input_data)
        
        return input_data

    def _optimize_for_album_covers(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize parameters for album cover generation."""
        # Ensure square aspect ratio for album covers
        if "width" in input_data and "height" in input_data:
            size = max(input_data["width"], input_data["height"])
            input_data["width"] = size
            input_data["height"] = size
        
        # Add professional music artwork styling
        if "prompt" in input_data:
            input_data["prompt"] += " --style professional album cover, music artwork, high quality"
        
        return input_data

    def _optimize_for_blog_graphics(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize parameters for blog graphics."""
        # Optimize for blog header dimensions
        if "width" in input_data and "height" in input_data:
            input_data["width"] = 1200
            input_data["height"] = 630  # Good for social sharing
        
        # Add blog-friendly styling
        if "prompt" in input_data:
            input_data["prompt"] += " --style clean, professional, blog header, readable"
        
        return input_data

    def _optimize_for_photography(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize parameters for photographic content."""
        # Ensure high quality
        if "num_inference_steps" in input_data:
            input_data["num_inference_steps"] = max(input_data["num_inference_steps"], 50)
        
        # Add photographic styling
        if "prompt" in input_data:
            input_data["prompt"] += " --style photorealistic, professional photography, high detail"
        
        return input_data

    def _optimize_for_social_media(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize parameters for social media content."""
        # Multiple aspect ratios for different platforms
        use_case = input_data.get("social_platform", "instagram")
        
        if use_case == "instagram_story":
            input_data["width"] = 1080
            input_data["height"] = 1920
        elif use_case == "instagram_post":
            input_data["width"] = 1080
            input_data["height"] = 1080
        elif use_case == "twitter":
            input_data["width"] = 1200
            input_data["height"] = 675
        
        # Add social media styling
        if "prompt" in input_data:
            input_data["prompt"] += " --style social media ready, engaging, vibrant"
        
        return input_data

    async def _apply_post_processing(self, prediction: ReplicatePrediction) -> None:
        """Apply post-processing for creator workflows."""
        creator_type = prediction.creator_context.get("creator_type")
        
        if creator_type and prediction.status == PredictionStatus.SUCCEEDED:
            # Add creator-specific metadata
            prediction.business_metadata.update({
                "creator_optimized": True,
                "creator_type": creator_type,
                "monetization_ready": True,
                "processing_completed_at": datetime.now().isoformat()
            })
            
            # Calculate actual cost
            if prediction.model:
                actual_cost = prediction.model.cost_per_run
                prediction.business_metadata["actual_cost"] = actual_cost
                self.cost_tracking["total_cost"] += actual_cost

    def _get_model_config(self, model_name: str) -> Optional[ReplicateModel]:
        """Get model configuration from registry."""
        return self.model_registry.get(model_name)

    def _track_prediction(self, prediction: ReplicatePrediction) -> None:
        """Track prediction for analytics and cost optimization."""
        self.prediction_history.append({
            "id": prediction.id,
            "model": prediction.model.name if prediction.model else "unknown",
            "created_at": prediction.created_at.isoformat(),
            "creator_type": prediction.creator_context.get("creator_type"),
            "estimated_cost": prediction.model.cost_per_run if prediction.model else 0.0
        })
        
        # Update cost tracking
        self.cost_tracking["predictions_count"] += 1
        if self.cost_tracking["predictions_count"] > 0:
            self.cost_tracking["avg_cost_per_prediction"] = (
                self.cost_tracking["total_cost"] / self.cost_tracking["predictions_count"]
            )

    async def get_cost_analytics(self) -> Dict[str, Any]:
        """Get cost analytics and usage statistics."""
        return {
            "cost_tracking": self.cost_tracking,
            "prediction_count": len(self.prediction_history),
            "predictions_by_creator_type": self._analyze_usage_by_creator_type(),
            "model_usage_stats": self._analyze_model_usage(),
            "recommendations": await self._generate_cost_optimization_recommendations()
        }

    def _analyze_usage_by_creator_type(self) -> Dict[str, int]:
        """Analyze usage patterns by creator type."""
        usage = {}
        for prediction in self.prediction_history:
            creator_type = prediction.get("creator_type", "unknown")
            usage[creator_type] = usage.get(creator_type, 0) + 1
        return usage

    def _analyze_model_usage(self) -> Dict[str, int]:
        """Analyze usage patterns by model."""
        usage = {}
        for prediction in self.prediction_history:
            model = prediction.get("model", "unknown")
            usage[model] = usage.get(model, 0) + 1
        return usage

    async def _generate_cost_optimization_recommendations(self) -> List[str]:
        """Generate cost optimization recommendations."""
        recommendations = []
        
        # Analyze cost patterns
        if self.cost_tracking["avg_cost_per_prediction"] > 0.01:
            recommendations.append(
                "Consider using lower-cost models for non-critical tasks"
            )
        
        # Analyze model usage
        model_usage = self._analyze_model_usage()
        most_used_model = max(model_usage.items(), key=lambda x: x[1], default=("", 0))[0]
        
        if most_used_model and most_used_model in self.model_registry:
            model = self.model_registry[most_used_model]
            if model.cost_per_run > 0.005:
                recommendations.append(
                    f"'{most_used_model}' is your most used high-cost model. "
                    "Consider batch processing or alternative models."
                )
        
        return recommendations

    async def close(self) -> None:
        """Clean up resources and close connections."""
        if self.session:
            await self.session.aclose()
            self.session = None
            
        logger.info("✅ Replicate client closed")

    async def __aenter__(self) -> None:
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()


# Factory function for easy instantiation
def create_replicate_client(
    api_token: Optional[str] = None,
    enable_cost_optimization: bool = True,
    enable_creator_recommendations: bool = True
) -> ReplicateEnterpriseClient:
    """
    Factory function to create Replicate client with enterprise configuration.
    
    Args:
        api_token: Replicate API token
        enable_cost_optimization: Enable cost optimization features
        enable_creator_recommendations: Enable creator-specific recommendations
        
    Returns:
        Configured ReplicateEnterpriseClient instance
    """
    return ReplicateEnterpriseClient(
        api_token=api_token,
        enable_cost_optimization=enable_cost_optimization,
        enable_creator_recommendations=enable_creator_recommendations
    )


# Example usage for creator workflows
async def example_creator_ai_workflow() -> None:
    """Example of creator-specific AI model usage."""
    try:
        client = create_replicate_client(api_token="your-api-token")
        
        # Get model recommendations for a musician
        musician_models = await client.get_model_recommendations(
            creator_type="musician",
            use_case="content_creation",
            budget_constraint=0.01
        )
        
        print(f"🎵 Recommended models for musicians: {[m.name for m in musician_models]}")
        
        # Generate album cover for musician
        prediction = await client.create_prediction(
            model_name="stable-diffusion-xl",
            input_data={
                "prompt": "synthwave album cover with neon colors",
                "width": 1024,
                "height": 1024,
                "num_inference_steps": 50
            },
            creator_context={
                "creator_type": "musician",
                "creator_id": "musician_123",
                "use_case": "album_cover"
            }
        )
        
        print(f"🎨 Album cover generation started: {prediction.id}")
        
        # Wait for completion
        result = await client.wait_for_prediction(prediction.id)
        
        if result.status == PredictionStatus.SUCCEEDED:
            print(f"✅ Album cover generated: {result.output}")
            print(f"💰 Cost: ${result.business_metadata.get('actual_cost', 0.0):.4f}")
        
        # Get cost analytics
        analytics = await client.get_cost_analytics()
        print(f"📊 Total predictions: {analytics['prediction_count']}")
        print(f"💸 Average cost per prediction: ${analytics['cost_tracking']['avg_cost_per_prediction']:.4f}")
        
        await client.close()
        
    except Exception as e:
        logger.error(f"Example failed: {e}")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_creator_ai_workflow())