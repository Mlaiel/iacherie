"""
AI Leader Configuration
Central configuration file for all settings
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
STORAGE_DIR = BASE_DIR / "storage"
MODELS_DIR = STORAGE_DIR / "models"
DATA_DIR = STORAGE_DIR / "data"

# Ensure directories exist
STORAGE_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# Training settings
TRAINING_CONFIG = {
    "min_samples": int(os.getenv("AI_LEADER_MIN_SAMPLES", "100")),
    "accuracy_threshold": float(os.getenv("AI_LEADER_ACCURACY_THRESHOLD", "0.85")),
    "default_epochs": int(os.getenv("AI_LEADER_DEFAULT_EPOCHS", "10")),
    "default_batch_size": int(os.getenv("AI_LEADER_BATCH_SIZE", "32")),
    "default_learning_rate": float(os.getenv("AI_LEADER_LEARNING_RATE", "0.001")),
    "validation_split": float(os.getenv("AI_LEADER_VAL_SPLIT", "0.2"))
}

# API Provider priorities
PROVIDER_PRIORITIES = {
    "text_generation": [
        {"name": "OpenAI GPT-4", "cost": 0.03, "priority": 1},
        {"name": "Anthropic Claude", "cost": 0.02, "priority": 2},
        {"name": "Google Gemini", "cost": 0.01, "priority": 3}
    ],
    "image_generation": [
        {"name": "DALL-E 3", "cost": 0.04, "priority": 1},
        {"name": "Leonardo AI", "cost": 0.03, "priority": 2},
        {"name": "Stable Diffusion", "cost": 0.01, "priority": 3}
    ],
    "video_generation": [
        {"name": "RunwayML Gen-3", "cost": 1.0, "priority": 1},
        {"name": "Pexels Video", "cost": 0.0, "priority": 2}
    ],
    "audio_generation": [
        {"name": "ElevenLabs", "cost": 0.10, "priority": 1},
        {"name": "Google TTS", "cost": 0.01, "priority": 2}
    ]
}

# Monitoring settings
MONITORING_CONFIG = {
    "status_update_interval_seconds": 5,
    "health_check_interval_seconds": 60,
    "metrics_retention_days": 30
}

# Server settings
SERVER_CONFIG = {
    "host": os.getenv("AI_LEADER_HOST", "0.0.0.0"),
    "port": int(os.getenv("AI_LEADER_PORT", "8001")),
    "reload": os.getenv("AI_LEADER_RELOAD", "false").lower() == "true",
    "log_level": os.getenv("AI_LEADER_LOG_LEVEL", "info")
}

# Security settings
SECURITY_CONFIG = {
    "enable_auth": os.getenv("AI_LEADER_ENABLE_AUTH", "false").lower() == "true",
    "api_key": os.getenv("AI_LEADER_API_KEY"),
    "allowed_origins": os.getenv("AI_LEADER_CORS_ORIGINS", "http://localhost:3001,http://localhost:3000").split(",")
}
