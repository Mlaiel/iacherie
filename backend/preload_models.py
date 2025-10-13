#!/usr/bin/env python3
"""
Preload All AI Models - Force download at startup
Ensures all internal models are ready before accepting requests

Author: Fahed Mlaiel
"""

import os
import sys
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def preload_internal_models():
    """Force download and cache all internal AI models"""
    logger.info("=" * 80)
    logger.info("🚀 PRELOADING ALL INTERNAL AI MODELS")
    logger.info("=" * 80)
    
    try:
        from backend.api.internal_image_generator import get_internal_generator
        
        generator = get_internal_generator()
        
        if not generator.available:
            logger.warning("⚠️ Internal generator not available")
            return False
        
        # Models to preload
        models_to_load = [
            ("internal-sdxl-turbo", "stabilityai/sdxl-turbo"),
            ("internal-sd-turbo", "stabilityai/sd-turbo"),
            ("internal-sd-1.5", "runwayml/stable-diffusion-v1-5"),
        ]
        
        logger.info(f"📦 Will preload {len(models_to_load)} models:")
        for name, model_id in models_to_load:
            logger.info(f"   • {name} ({model_id})")
        
        logger.info("")
        
        # Preload each model
        for i, (name, model_id) in enumerate(models_to_load, 1):
            logger.info(f"[{i}/{len(models_to_load)}] Loading {name}...")
            logger.info(f"   Model ID: {model_id}")
            
            try:
                pipe = generator._load_model(model_id)
                if pipe:
                    logger.info(f"   ✅ {name} loaded successfully!")
                else:
                    logger.error(f"   ❌ {name} failed to load")
            except Exception as e:
                logger.error(f"   ❌ Error loading {name}: {e}")
                continue
            
            logger.info("")
        
        logger.info("=" * 80)
        logger.info(f"✅ Model preloading complete! {len(generator.models)} models cached")
        logger.info("=" * 80)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Fatal error during model preloading: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = preload_internal_models()
    sys.exit(0 if success else 1)
