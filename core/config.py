"""Core Configuration for AI Agents Business Logic
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
    
    # Platform API credentials
    SPOTIFY_CLIENT_ID: Optional[str] = os.getenv("SPOTIFY_CLIENT_ID")
    SPOTIFY_CLIENT_SECRET: Optional[str] = os.getenv("SPOTIFY_CLIENT_SECRET")
    YOUTUBE_API_KEY: Optional[str] = os.getenv("YOUTUBE_API_KEY")
    TWITTER_API_KEY: Optional[str] = os.getenv("TWITTER_API_KEY")
    TWITTER_API_SECRET: Optional[str] = os.getenv("TWITTER_API_SECRET")
    TWITTER_ACCESS_TOKEN: Optional[str] = os.getenv("TWITTER_ACCESS_TOKEN")
    TWITTER_ACCESS_TOKEN_SECRET: Optional[str] = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
    INSTAGRAM_ACCESS_TOKEN: Optional[str] = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    FACEBOOK_ACCESS_TOKEN: Optional[str] = os.getenv("FACEBOOK_ACCESS_TOKEN")
    LINKEDIN_CLIENT_ID: Optional[str] = os.getenv("LINKEDIN_CLIENT_ID")
    LINKEDIN_CLIENT_SECRET: Optional[str] = os.getenv("LINKEDIN_CLIENT_SECRET")
    TIKTOK_ACCESS_TOKEN: Optional[str] = os.getenv("TIKTOK_ACCESS_TOKEN")
    TWITCH_CLIENT_ID: Optional[str] = os.getenv("TWITCH_CLIENT_ID")
    TWITCH_CLIENT_SECRET: Optional[str] = os.getenv("TWITCH_CLIENT_SECRET")
    SOUNDCLOUD_CLIENT_ID: Optional[str] = os.getenv("SOUNDCLOUD_CLIENT_ID")
    APPLE_MUSIC_KEY_ID: Optional[str] = os.getenv("APPLE_MUSIC_KEY_ID")
    APPLE_MUSIC_TEAM_ID: Optional[str] = os.getenv("APPLE_MUSIC_TEAM_ID")
    
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

def get_settings() -> Settings:
    """Get global settings instance"""    return settings