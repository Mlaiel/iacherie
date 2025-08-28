"""
Core Configuration for AI Agents Business Logic
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Settings:
    """Core settings for the AI agents system"""
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://localhost/ainflue")
    
    # Redis settings  
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    
    # Agent system settings
    MAX_CONCURRENT_WORKFLOWS: int = int(os.getenv("MAX_CONCURRENT_WORKFLOWS", "100"))
    DEFAULT_TIMEOUT: int = int(os.getenv("DEFAULT_TIMEOUT", "300"))
    
    # Content processing settings
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "500"))
    SUPPORTED_FORMATS: Dict[str, list] = None
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    
    def __post_init__(self):
        if self.SUPPORTED_FORMATS is None:
            self.SUPPORTED_FORMATS = {
                'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'],
                'video': ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv'],
                'image': ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp', '.svg'],
                'text': ['.txt', '.md', '.html', '.json', '.xml', '.csv']
            }


# Global settings instance
settings = Settings()