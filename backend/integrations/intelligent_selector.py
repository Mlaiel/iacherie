"""
🤖 INTELLIGENT API SELECTOR - COST & QUALITY OPTIMIZATION
===============AVAILABLE_MODELS = {
    "image": [
        # 🆓 MODÈLES INTERNES (GRATUITS - Meilleure qualité)
        {"id": "internal-diffusion-xl", "name": "🆓 AI Leader Diffusion XL (GRATUIT)", "provider": ModelProvider.INTERNAL, "cost": 0.0, "quality": "ultra", "speed": "fast", "multilang": True},
        {"id": "internal-sdxl-turbo", "name": "🆓 AI Leader SDXL Turbo (GRATUIT)", "provider": ModelProvider.INTERNAL, "cost": 0.0, "quality": "high", "speed": "very-fast", "multilang": True},
        {"id": "internal-image-pro", "name": "🆓 AI Leader Image Pro (GRATUIT)", "provider": ModelProvider.INTERNAL, "cost": 0.0, "quality": "high", "speed": "fast", "multilang": True},
        {"id": "internal-image-v2", "name": "🆓 AI Leader Image v2 (GRATUIT)", "provider": ModelProvider.INTERNAL, "cost": 0.0, "quality": "medium", "speed": "very-fast", "multilang": True},
        {"id": "internal-photorealistic", "name": "🆓 AI Leader Photo-Réaliste (GRATUIT)", "provider": ModelProvider.INTERNAL, "cost": 0.0, "quality": "ultra", "speed": "medium", "multilang": True},
        {"id": "internal-artistic", "name": "🆓 AI Leader Artistique (GRATUIT)", "provider": ModelProvider.INTERNAL, "cost": 0.0, "quality": "high", "speed": "fast", "multilang": True},
        {"id": "internal-anime", "name": "🆓 AI Leader Anime (GRATUIT)", "provider": ModelProvider.INTERNAL, "cost": 0.0, "quality": "high", "speed": "fast", "multilang": True},
        
        # 💰 APIs EXTERNES (PAYANTES)
        {"id": "dall-e-3", "name": "💰 DALL-E 3 ($0.040)", "provider": ModelProvider.OPENAI, "cost": 0.040, "quality": "high", "speed": "medium", "multilang": True},
        {"id": "dall-e-3-hd", "name": "💰 DALL-E 3 HD ($0.080)", "provider": ModelProvider.OPENAI, "cost": 0.080, "quality": "ultra", "speed": "medium", "multilang": True},
        {"id": "dall-e-2", "name": "💰 DALL-E 2 ($0.020)", "provider": ModelProvider.OPENAI, "cost": 0.020, "quality": "medium", "speed": "fast", "multilang": True},
        {"id": "stability-sd-xl", "name": "💰 Stable Diffusion XL ($0.030)", "provider": ModelProvider.STABILITY, "cost": 0.030, "quality": "high", "speed": "fast", "multilang": True},
        {"id": "leonardo-xl", "name": "💰 Leonardo XL ($0.012)", "provider": "leonardo", "cost": 0.012, "quality": "high", "speed": "fast", "multilang": True},
        {"id": "midjourney-v6", "name": "💰 Midjourney v6 ($0.040)", "provider": ModelProvider.MIDJOURNEY, "cost": 0.040, "quality": "ultra", "speed": "slow", "multilang": True},
    ],====================================
Smart system that chooses between:
- Internal AI Leader models (FREE, trained from APIs)
- External APIs (PAID but high quality)

Strategy:
1. Try internal AI Leader first (FREE)
2. Fallback to external API if quality/confidence is low
3. Track costs and learning progress
4. Auto-switch when internal model is good enough

@author Fahed Mlaiel
@date 2025-10-06
"""

import os
import logging
from typing import Dict, Any, Optional, Literal
from enum import Enum

logger = logging.getLogger(__name__)

# ============================================================================
# COST CONFIGURATION (USD per request)
# ============================================================================

API_COSTS = {
    # Images
    "dall-e-3": 0.040,
    "dall-e-3-hd": 0.080,
    "dall-e-2": 0.020,
    "stability-sd-xl": 0.030,
    "midjourney": 0.040,
    
    # Text
    "gpt-4": 0.030,  # per 1K tokens
    "gpt-4-turbo": 0.010,
    "gpt-3.5-turbo": 0.001,
    "claude-3-opus": 0.015,
    "claude-3-sonnet": 0.003,
    
    # Video - EXPENSIVE! ⚠️
    "runway-gen2": 0.05,  # PER SECOND!
    "runway-gen3": 0.10,  # PER SECOND!
    "pika-labs": 0.08,
    "stable-video": 0.06,
    
    # Audio
    "openai-tts": 0.015,  # per 1K chars
    "elevenlabs": 0.30,  # per 1K chars
    "stability-audio": 0.02,
    
    # 3D
    "stability-3d": 0.10,
    "shap-e": 0.15,
}

# ============================================================================
# MODEL PROVIDERS
# ============================================================================

class ModelProvider(str, Enum):
    INTERNAL = "internal"  # AI Leader (FREE)
    OPENAI = "openai"
    RUNWAY = "runway"
    STABILITY = "stability"
    ELEVENLABS = "elevenlabs"
    PIKA = "pika"
    MIDJOURNEY = "midjourney"
    ANTHROPIC = "anthropic"

# ============================================================================
# MODEL REGISTRY
# ============================================================================

AVAILABLE_MODELS = {
    "image": [
        # 🆓 MODÈLES INTERNES AI LEADER (GRATUITS - STABLE DIFFUSION)
        {"id": "internal-sdxl-turbo", "name": "🆓 AI Leader SDXL Turbo (ULTRA RAPIDE)", "provider": ModelProvider.INTERNAL, "cost": 0.0, "quality": "high", "speed": "very-fast", "steps": 4, "description": "Stable Diffusion XL Turbo - Haute qualité en 4 steps (7.2GB)"},
        {"id": "internal-sd-turbo", "name": "🆓 AI Leader SD Turbo (LE PLUS RAPIDE)", "provider": ModelProvider.INTERNAL, "cost": 0.0, "quality": "medium", "speed": "fastest", "steps": 2, "description": "Stable Diffusion Turbo - Vitesse maximale en 1-2 steps (~4GB)"},
        {"id": "internal-sd-1.5", "name": "🆓 AI Leader SD 1.5 (HAUTE QUALITÉ)", "provider": ModelProvider.INTERNAL, "cost": 0.0, "quality": "high", "speed": "medium", "steps": 50, "description": "Stable Diffusion v1.5 - Qualité maximale en 50 steps (~4GB)"},
        {"id": "internal-image", "name": "🆓 AI Leader Image (DÉFAUT)", "provider": ModelProvider.INTERNAL, "cost": 0.0, "quality": "high", "speed": "very-fast", "steps": 4, "description": "Alias pour SDXL Turbo - Meilleur compromis qualité/vitesse"},
        
        # 💰 APIs EXTERNES (PAYANTES)
        {"id": "dall-e-3", "name": "💰 DALL-E 3 ($0.040/image)", "provider": ModelProvider.OPENAI, "cost": 0.040, "quality": "high", "speed": "medium"},
        {"id": "dall-e-3-hd", "name": "💰 DALL-E 3 HD ($0.080/image)", "provider": ModelProvider.OPENAI, "cost": 0.080, "quality": "ultra", "speed": "medium"},
        {"id": "dall-e-2", "name": "💰 DALL-E 2 ($0.020/image)", "provider": ModelProvider.OPENAI, "cost": 0.020, "quality": "medium", "speed": "fast"},
        {"id": "stability-sd-xl", "name": "💰 Stability SD-XL ($0.030/image)", "provider": ModelProvider.STABILITY, "cost": 0.030, "quality": "high", "speed": "fast"},
    ],
    
    "text": [
        # 🆓 MODÈLES INTERNES (GRATUITS)
        {"id": "internal-gpt-xl", "name": "🆓 AI Leader GPT-XL (GRATUIT)", "provider": ModelProvider.INTERNAL, "cost": 0.0, "quality": "ultra", "speed": "fast", "multilang": True},
        {"id": "internal-text-pro", "name": "🆓 AI Leader Text Pro (GRATUIT)", "provider": ModelProvider.INTERNAL, "cost": 0.0, "quality": "high", "speed": "very-fast", "multilang": True},
        {"id": "internal-code-writer", "name": "🆓 AI Leader Code Writer (GRATUIT)", "provider": ModelProvider.INTERNAL, "cost": 0.0, "quality": "high", "speed": "fast", "multilang": True},
        
        # 💰 APIs EXTERNES (PAYANTES)
        {"id": "gpt-4", "name": "💰 GPT-4 ($0.030/1K tokens)", "provider": ModelProvider.OPENAI, "cost": 0.030, "quality": "ultra", "speed": "slow", "multilang": True},
        {"id": "gpt-4-turbo", "name": "💰 GPT-4 Turbo ($0.010/1K tokens)", "provider": ModelProvider.OPENAI, "cost": 0.010, "quality": "high", "speed": "fast", "multilang": True},
        {"id": "gpt-3.5-turbo", "name": "💰 GPT-3.5 Turbo ($0.001/1K tokens)", "provider": ModelProvider.OPENAI, "cost": 0.001, "quality": "medium", "speed": "very-fast", "multilang": True},
        {"id": "claude-3-opus", "name": "💰 Claude 3 Opus ($0.015/1K tokens)", "provider": ModelProvider.ANTHROPIC, "cost": 0.015, "quality": "ultra", "speed": "medium", "multilang": True},
        {"id": "claude-3-sonnet", "name": "💰 Claude 3 Sonnet ($0.003/1K tokens)", "provider": ModelProvider.ANTHROPIC, "cost": 0.003, "quality": "high", "speed": "fast", "multilang": True},
    ],
    
    "video": [
        # 🆓 MODÈLES INTERNES (GRATUITS)
        {"id": "internal-video-xl", "name": "🆓 AI Leader Video XL (GRATUIT)", "provider": ModelProvider.INTERNAL, "cost": 0.0, "quality": "high", "speed": "medium", "multilang": True},
        {"id": "internal-video-pro", "name": "🆓 AI Leader Video Pro (GRATUIT)", "provider": ModelProvider.INTERNAL, "cost": 0.0, "quality": "medium", "speed": "fast", "multilang": True},
        {"id": "internal-video-turbo", "name": "🆓 AI Leader Video Turbo (GRATUIT)", "provider": ModelProvider.INTERNAL, "cost": 0.0, "quality": "medium", "speed": "very-fast", "multilang": True},
        
        # 💰 APIs EXTERNES (TRÈS CHÈRES ⚠️)
        {"id": "stable-video", "name": "💰 Stable Video ($0.06/sec)", "provider": ModelProvider.STABILITY, "cost": 0.06, "quality": "medium", "speed": "fast", "multilang": True},
        {"id": "runway-gen2", "name": "⚠️ Runway Gen-2 ($0.05/sec)", "provider": ModelProvider.RUNWAY, "cost": 0.05, "quality": "high", "speed": "medium", "warning": "💰 $0.05/second", "multilang": True},
        {"id": "runway-gen3", "name": "⚠️⚠️ Runway Gen-3 ($0.10/sec)", "provider": ModelProvider.RUNWAY, "cost": 0.10, "quality": "ultra", "speed": "slow", "warning": "💰💰 $0.10/second", "multilang": True},
        {"id": "pika-labs", "name": "💰 Pika Labs ($0.08/sec)", "provider": ModelProvider.PIKA, "cost": 0.08, "quality": "high", "speed": "fast", "multilang": True},
    ],
    
    "audio": [
        # 🆓 MODÈLES INTERNES (GRATUITS)
        {"id": "internal-voice-xl", "name": "🆓 AI Leader Voice XL (GRATUIT)", "provider": ModelProvider.INTERNAL, "cost": 0.0, "quality": "ultra", "speed": "fast", "multilang": True},
        {"id": "internal-tts-pro", "name": "🆓 AI Leader TTS Pro (GRATUIT)", "provider": ModelProvider.INTERNAL, "cost": 0.0, "quality": "high", "speed": "very-fast", "multilang": True},
        {"id": "internal-music-gen", "name": "🆓 AI Leader Music Gen (GRATUIT)", "provider": ModelProvider.INTERNAL, "cost": 0.0, "quality": "high", "speed": "fast", "multilang": True},
        {"id": "internal-voice-clone", "name": "🆓 AI Leader Voice Clone (GRATUIT)", "provider": ModelProvider.INTERNAL, "cost": 0.0, "quality": "ultra", "speed": "medium", "multilang": True},
        
        # 💰 APIs EXTERNES (PAYANTES)
        {"id": "openai-tts", "name": "💰 OpenAI TTS ($0.015/1K chars)", "provider": ModelProvider.OPENAI, "cost": 0.015, "quality": "high", "speed": "fast", "multilang": True},
        {"id": "openai-tts-hd", "name": "💰 OpenAI TTS HD ($0.030/1K chars)", "provider": ModelProvider.OPENAI, "cost": 0.030, "quality": "ultra", "speed": "medium", "multilang": True},
        {"id": "elevenlabs", "name": "⚠️ ElevenLabs ($0.30/1K chars)", "provider": ModelProvider.ELEVENLABS, "cost": 0.30, "quality": "ultra", "speed": "medium", "warning": "💰 High cost", "multilang": True},
        {"id": "stability-audio", "name": "💰 Stability Audio ($0.02/1K chars)", "provider": ModelProvider.STABILITY, "cost": 0.02, "quality": "medium", "speed": "fast", "multilang": True},
    ],
    
    "code": [
        # 🆓 MODÈLES INTERNES (GRATUITS)
        {"id": "internal-code-xl", "name": "🆓 AI Leader Code XL (GRATUIT)", "provider": ModelProvider.INTERNAL, "cost": 0.0, "quality": "ultra", "speed": "fast", "multilang": True},
        {"id": "internal-code-pro", "name": "🆓 AI Leader Code Pro (GRATUIT)", "provider": ModelProvider.INTERNAL, "cost": 0.0, "quality": "high", "speed": "very-fast", "multilang": True},
        {"id": "internal-debugger", "name": "🆓 AI Leader Debugger (GRATUIT)", "provider": ModelProvider.INTERNAL, "cost": 0.0, "quality": "high", "speed": "fast", "multilang": True},
        
        # 💰 APIs EXTERNES (PAYANTES)
        {"id": "gpt-4-code", "name": "💰 GPT-4 Code ($0.030/1K tokens)", "provider": ModelProvider.OPENAI, "cost": 0.030, "quality": "ultra", "speed": "medium", "multilang": True},
        {"id": "gpt-3.5-turbo", "name": "💰 GPT-3.5 Turbo ($0.001/1K tokens)", "provider": ModelProvider.OPENAI, "cost": 0.001, "quality": "medium", "speed": "very-fast", "multilang": True},
        {"id": "claude-code", "name": "💰 Claude Code ($0.015/1K tokens)", "provider": ModelProvider.ANTHROPIC, "cost": 0.015, "quality": "ultra", "speed": "medium", "multilang": True},
    ],
    
    "3d": [
        # 🆓 MODÈLES INTERNES (GRATUITS)
        {"id": "internal-3d-xl", "name": "🆓 AI Leader 3D XL (GRATUIT)", "provider": ModelProvider.INTERNAL, "cost": 0.0, "quality": "high", "speed": "medium", "multilang": True},
        {"id": "internal-3d-pro", "name": "🆓 AI Leader 3D Pro (GRATUIT)", "provider": ModelProvider.INTERNAL, "cost": 0.0, "quality": "medium", "speed": "fast", "multilang": True},
        {"id": "internal-mesh-gen", "name": "🆓 AI Leader Mesh Gen (GRATUIT)", "provider": ModelProvider.INTERNAL, "cost": 0.0, "quality": "medium", "speed": "fast", "multilang": True},
        
        # 💰 APIs EXTERNES (PAYANTES)
        {"id": "stability-3d", "name": "💰 Stability 3D ($0.10)", "provider": ModelProvider.STABILITY, "cost": 0.10, "quality": "medium", "speed": "medium", "multilang": False},
        {"id": "shap-e", "name": "💰 Shap-E ($0.15)", "provider": ModelProvider.OPENAI, "cost": 0.15, "quality": "high", "speed": "slow", "multilang": False},
    ],
}

# ============================================================================
# INTELLIGENT MODEL SELECTOR
# ============================================================================

class IntelligentModelSelector:
    """
    Smart model selector that optimizes for:
    1. Cost (prefer internal AI Leader when good enough)
    2. Quality (use external APIs when needed)
    3. Speed (balance between cost and quality)
    """
    
    def __init__(self):
        self.usage_stats = {}
        self.ai_leader_confidence = {
            "image": 0.7,   # 70% confidence
            "text": 0.8,    # 80% confidence
            "video": 0.3,   # 30% confidence (learning)
            "audio": 0.6,   # 60% confidence
            "code": 0.75,   # 75% confidence
            "3d": 0.4,      # 40% confidence (learning)
        }
    
    def select_best_model(
        self,
        type: str,
        prefer_internal: bool = True,
        min_quality: str = "medium",
        max_cost: float = None,
        user_choice: str = None
    ) -> Dict[str, Any]:
        """
        Select the best model based on criteria
        
        Args:
            type: Generation type (image, text, video, etc.)
            prefer_internal: Try AI Leader first
            min_quality: Minimum quality required
            max_cost: Maximum cost per request
            user_choice: User's explicit model choice
        
        Returns:
            Selected model config
        """
        models = AVAILABLE_MODELS.get(type, [])
        
        if not models:
            raise ValueError(f"No models available for type: {type}")
        
        # User explicitly chose a model
        if user_choice:
            for model in models:
                if model["id"] == user_choice:
                    logger.info(f"✅ User selected: {model['name']} (${model['cost']})")
                    return model
        
        # Try AI Leader first if confidence is high enough
        if prefer_internal:
            internal_model = next((m for m in models if m["provider"] == ModelProvider.INTERNAL), None)
            if internal_model:
                confidence = self.ai_leader_confidence.get(type, 0.5)
                
                # Use internal if confidence > 70%
                if confidence >= 0.7:
                    logger.info(f"✅ Using AI Leader (FREE) - Confidence: {confidence*100}%")
                    return internal_model
                else:
                    logger.warning(f"⚠️ AI Leader confidence low ({confidence*100}%), using external API")
        
        # Filter by quality and cost
        candidates = models
        
        # Remove internal from candidates now
        candidates = [m for m in candidates if m["provider"] != ModelProvider.INTERNAL]
        
        # Filter by max cost
        if max_cost is not None:
            candidates = [m for m in candidates if m["cost"] <= max_cost]
        
        # Filter by quality
        quality_order = ["low", "medium", "high", "ultra"]
        min_quality_idx = quality_order.index(min_quality) if min_quality in quality_order else 1
        candidates = [m for m in candidates if quality_order.index(m["quality"]) >= min_quality_idx]
        
        if not candidates:
            # Fallback to cheapest model
            candidates = models[1:]  # Skip internal
        
        # Sort by cost (cheapest first)
        candidates.sort(key=lambda m: m["cost"])
        
        # Get best balance between cost and quality
        selected = candidates[0]
        
        logger.info(f"✅ Selected: {selected['name']} (${selected['cost']}) - Quality: {selected['quality']}")
        
        return selected
    
    def get_models_for_type(self, type: str) -> list:
        """Get all available models for a type"""
        return AVAILABLE_MODELS.get(type, [])
    
    def estimate_cost(self, type: str, model_id: str, duration: int = 1) -> float:
        """
        Estimate cost for a generation
        
        Args:
            type: Generation type
            model_id: Model ID
            duration: For video/audio (seconds)
        
        Returns:
            Estimated cost in USD
        """
        models = AVAILABLE_MODELS.get(type, [])
        model = next((m for m in models if m["id"] == model_id), None)
        
        if not model:
            return 0.0
        
        base_cost = model["cost"]
        
        # For video/audio, multiply by duration
        if type in ["video", "audio"]:
            return base_cost * duration
        
        return base_cost
    
    def update_ai_leader_confidence(self, type: str, success: bool, user_rating: float = None):
        """
        Update AI Leader confidence based on results
        
        Args:
            type: Generation type
            success: Whether generation succeeded
            user_rating: User rating (0-1)
        """
        current = self.ai_leader_confidence.get(type, 0.5)
        
        if success:
            # Increase confidence
            new_confidence = min(current + 0.05, 0.95)
        else:
            # Decrease confidence
            new_confidence = max(current - 0.1, 0.1)
        
        # Factor in user rating if provided
        if user_rating is not None:
            new_confidence = (new_confidence + user_rating) / 2
        
        self.ai_leader_confidence[type] = new_confidence
        
        logger.info(f"📊 AI Leader confidence for {type}: {current*100:.1f}% → {new_confidence*100:.1f}%")

# ============================================================================
# SINGLETON
# ============================================================================

_selector = None

def get_model_selector() -> IntelligentModelSelector:
    """Get singleton instance of model selector"""
    global _selector
    if _selector is None:
        _selector = IntelligentModelSelector()
    return _selector
