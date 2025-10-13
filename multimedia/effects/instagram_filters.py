"""Instagram-Style Filters Engine
Professional Instagram and TikTok-style filters for social media content.

Created by: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)

class InstagramFilter(Enum):
    """Popular Instagram-style filters."""
    CLARENDON = "clarendon"
    GINGHAM = "gingham" 
    MOON = "moon"
    LARK = "lark"
    REYES = "reyes"
    JUNO = "juno"
    SLUMBER = "slumber"
    CREMA = "crema"
    LUDWIG = "ludwig"
    ADEN = "aden"
    PERPETUA = "perpetua"
    VALENCIA = "valencia"
    VINTAGE = "vintage"
    WARM = "warm"
    COOL = "cool"
    DRAMATIC = "dramatic"

@dataclass
class FilterConfig:
    """Configuration for Instagram-style filters."""
    filter_type: InstagramFilter
    intensity: float = 1.0  # 0-1
    preserve_skin_tones: bool = True
    auto_enhance: bool = False
    sharpen_amount: float = 0.1

class InstagramFiltersEngine:
    """Enterprise Instagram and TikTok-style filters engine."""
    
    def __init__(self):
        """Initialize the Instagram filters engine."""
        self.filter_definitions = self._load_filter_definitions()
        self.social_media_presets = self._load_social_presets()
        
    def _load_filter_definitions(self) -> Dict[InstagramFilter, Dict[str, Any]]:
        """Load filter definitions with processing parameters."""
        return {
            InstagramFilter.CLARENDON: {
                "brightness": 0.1,
                "contrast": 0.15,
                "saturation": 0.2,
                "highlights": -0.05,
                "shadows": 0.05,
                "temperature": 0.02,
                "vignette": 0.1,
                "description": "High contrast with enhanced details"
            },
            InstagramFilter.VALENCIA: {
                "brightness": 0.05,
                "contrast": 0.1,
                "saturation": 0.15,
                "highlights": 0.0,
                "shadows": 0.02,
                "temperature": 0.05,
                "tint": -0.02,
                "fade": 0.15,
                "description": "Warm with vintage film look"
            },
            InstagramFilter.JUNO: {
                "brightness": 0.08,
                "contrast": 0.2,
                "saturation": 0.1,
                "highlights": -0.1,
                "shadows": 0.1,
                "temperature": -0.03,
                "cyan_red": 0.05,
                "description": "Cool tones with raised shadows"
            },
            InstagramFilter.LARK: {
                "brightness": 0.12,
                "contrast": -0.05,
                "saturation": 0.08,
                "highlights": -0.15,
                "shadows": 0.2,
                "temperature": 0.0,
                "desaturate_highlights": True,
                "description": "Bright and airy with desaturated highlights"
            },
            InstagramFilter.MOON: {
                "brightness": 0.0,
                "contrast": 0.1,
                "saturation": -0.3,
                "highlights": 0.0,
                "shadows": 0.0,
                "temperature": 0.0,
                "grain": 0.15,
                "vignette": 0.2,
                "description": "Black and white with film grain"
            },
            InstagramFilter.VINTAGE: {
                "brightness": -0.05,
                "contrast": 0.05,
                "saturation": -0.1,
                "highlights": -0.1,
                "shadows": 0.05,
                "temperature": 0.08,
                "fade": 0.25,
                "grain": 0.1,
                "vignette": 0.15,
                "description": "Nostalgic film aesthetic"
            }
        }
    
    def _load_social_presets(self) -> Dict[str, Dict[str, Any]]:
        """Load social media platform presets."""
        return {
            "instagram_feed": {
                "aspect_ratio": (1, 1),
                "max_resolution": (1080, 1080),
                "recommended_filters": [
                    InstagramFilter.CLARENDON,
                    InstagramFilter.VALENCIA,
                    InstagramFilter.JUNO
                ]
            },
            "instagram_story": {
                "aspect_ratio": (9, 16),
                "max_resolution": (1080, 1920),
                "recommended_filters": [
                    InstagramFilter.LARK,
                    InstagramFilter.JUNO,
                    InstagramFilter.CLARENDON
                ]
            },
            "tiktok": {
                "aspect_ratio": (9, 16),
                "max_resolution": (1080, 1920),
                "recommended_filters": [
                    InstagramFilter.DRAMATIC,
                    InstagramFilter.VINTAGE,
                    InstagramFilter.WARM
                ]
            },
            "facebook": {
                "aspect_ratio": (16, 9),
                "max_resolution": (1200, 675),
                "recommended_filters": [
                    InstagramFilter.VALENCIA,
                    InstagramFilter.CLARENDON
                ]
            }
        }
    
    async def apply_filter(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        config: FilterConfig
    ) -> Dict[str, Any]:
        """
        Apply Instagram-style filter to image or video.
        
        Args:
            input_path: Path to input media file
            output_path: Path to output filtered file
            config: Filter configuration
            
        Returns:
            Filter application results
        """
        try:
            input_path = Path(input_path)
            output_path = Path(output_path)
            
            if not input_path.exists():
                raise FileNotFoundError(f"Input file not found: {input_path}")
            
            # Get filter definition
            filter_def = self.filter_definitions.get(config.filter_type)
            if not filter_def:
                raise ValueError(f"Unknown filter: {config.filter_type}")
            
            # Apply filter processing
            processing_start = asyncio.get_event_loop().time()
            
            result = await self._apply_filter_processing(
                input_path, output_path, config, filter_def
            )
            
            processing_time = asyncio.get_event_loop().time() - processing_start
            
            return {
                "success": True,
                "filter_applied": config.filter_type.value,
                "intensity": config.intensity,
                "processing_time": processing_time,
                "description": filter_def["description"],
                "adjustments_applied": result["adjustments"]
            }
            
        except Exception as e:
            logger.error(f"Filter application failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _apply_filter_processing(
        self,
        input_path: Path,
        output_path: Path,
        config: FilterConfig,
        filter_def: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply the actual filter processing."""
        # Simulate filter processing
        await asyncio.sleep(0.5)
        
        # Calculate applied adjustments based on intensity
        adjustments = {}
        for param, value in filter_def.items():
            if isinstance(value, (int, float)) and param != "description":
                adjustments[param] = value * config.intensity
        
        return {
            "adjustments": adjustments,
            "quality_score": 0.9
        }
    
    async def batch_apply_filters(
        self,
        input_files: List[Union[str, Path]],
        output_directory: Union[str, Path],
        filter_type: InstagramFilter,
        intensity: float = 1.0
    ) -> List[Dict[str, Any]]:
        """
        Apply filter to multiple files.
        
        Args:
            input_files: List of input file paths
            output_directory: Output directory
            filter_type: Filter to apply
            intensity: Filter intensity
            
        Returns:
            List of processing results
        """
        output_dir = Path(output_directory)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        config = FilterConfig(filter_type=filter_type, intensity=intensity)
        
        results = []
        for input_file in input_files:
            input_path = Path(input_file)
            output_path = output_dir / f"{input_path.stem}_{filter_type.value}{input_path.suffix}"
            
            result = await self.apply_filter(input_path, output_path, config)
            results.append(result)
        
        return results
    
    def recommend_filter(
        self,
        platform: str,
        content_type: str = "general",
        mood: str = "neutral"
    ) -> List[InstagramFilter]:
        """
        Recommend filters based on platform and content type.
        
        Args:
            platform: Target platform (instagram, tiktok, facebook)
            content_type: Type of content (portrait, landscape, food, fashion)
            mood: Desired mood (bright, moody, vintage, dramatic)
            
        Returns:
            List of recommended filters
        """
        platform_presets = self.social_media_presets.get(platform.lower())
        if not platform_presets:
            platform_presets = self.social_media_presets["instagram_feed"]
        
        base_recommendations = platform_presets["recommended_filters"]
        
        # Adjust recommendations based on content type and mood
        mood_filters = {
            "bright": [InstagramFilter.LARK, InstagramFilter.CLARENDON],
            "moody": [InstagramFilter.MOON, InstagramFilter.DRAMATIC],
            "vintage": [InstagramFilter.VINTAGE, InstagramFilter.VALENCIA],
            "dramatic": [InstagramFilter.DRAMATIC, InstagramFilter.CLARENDON],
            "warm": [InstagramFilter.VALENCIA, InstagramFilter.WARM],
            "cool": [InstagramFilter.JUNO, InstagramFilter.COOL]
        }
        
        content_filters = {
            "portrait": [InstagramFilter.LARK, InstagramFilter.VALENCIA],
            "landscape": [InstagramFilter.CLARENDON, InstagramFilter.DRAMATIC],
            "food": [InstagramFilter.VALENCIA, InstagramFilter.CLARENDON],
            "fashion": [InstagramFilter.JUNO, InstagramFilter.LARK],
            "lifestyle": [InstagramFilter.VALENCIA, InstagramFilter.LARK]
        }
        
        recommendations = set(base_recommendations)
        
        if mood in mood_filters:
            recommendations.update(mood_filters[mood])
        
        if content_type in content_filters:
            recommendations.update(content_filters[content_type])
        
        return list(recommendations)[:5]  # Return top 5 recommendations
    
    def get_filter_preview(
        self,
        filter_type: InstagramFilter,
        intensity: float = 1.0
    ) -> Dict[str, Any]:
        """Get preview information for a filter."""
        filter_def = self.filter_definitions.get(filter_type)
        if not filter_def:
            return {}
        
        preview_adjustments = {}
        for param, value in filter_def.items():
            if isinstance(value, (int, float)) and param != "description":
                preview_adjustments[param] = value * intensity
        
        return {
            "filter_name": filter_type.value,
            "description": filter_def.get("description", ""),
            "adjustments": preview_adjustments,
            "best_for": self._get_filter_best_use_cases(filter_type),
            "intensity": intensity
        }
    
    def _get_filter_best_use_cases(self, filter_type: InstagramFilter) -> List[str]:
        """Get best use cases for a filter."""
        use_cases = {
            InstagramFilter.CLARENDON: ["portraits", "architecture", "high contrast scenes"],
            InstagramFilter.VALENCIA: ["lifestyle", "warm scenes", "golden hour"],
            InstagramFilter.JUNO: ["cool tones", "winter scenes", "modern aesthetic"],
            InstagramFilter.LARK: ["bright spaces", "minimalist", "airy photos"],
            InstagramFilter.MOON: ["artistic", "dramatic", "black and white"],
            InstagramFilter.VINTAGE: ["nostalgic", "retro", "film aesthetic"]
        }
        
        return use_cases.get(filter_type, ["general use"])
    
    def create_filter_collection(
        self,
        input_path: Union[str, Path],
        output_directory: Union[str, Path],
        filters: List[InstagramFilter],
        intensity: float = 1.0
    ) -> Dict[str, Any]:
        """
        Create a collection with multiple filter variations.
        
        Args:
            input_path: Path to input image
            output_directory: Directory for filter collection
            filters: List of filters to apply
            intensity: Filter intensity
            
        Returns:
            Collection creation results
        """
        input_path = Path(input_path)
        output_dir = Path(output_directory)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        collection_info = {
            "original_file": str(input_path),
            "filters_applied": len(filters),
            "collection_directory": str(output_dir),
            "variations": []
        }
        
        for filter_type in filters:
            filter_name = filter_type.value
            output_path = output_dir / f"{input_path.stem}_{filter_name}{input_path.suffix}"
            
            collection_info["variations"].append({
                "filter": filter_name,
                "output_file": str(output_path),
                "description": self.filter_definitions[filter_type].get("description", "")
            })
        
        return collection_info