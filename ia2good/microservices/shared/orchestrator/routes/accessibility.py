"""
Accessibility API Routes
Universal accessibility endpoints for all modules
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional, Dict
from pydantic import BaseModel
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.accessibility_service import accessibility_service

router = APIRouter()


class TTSRequest(BaseModel):
    text: str
    language: str = "fr"
    voice: str = "default"
    speed: float = 1.0


class STTRequest(BaseModel):
    audio_url: str
    language: str = "fr"
    enable_punctuation: bool = True


class CaptionRequest(BaseModel):
    video_url: str
    language: str = "fr"
    format: str = "srt"


class VisualAlertRequest(BaseModel):
    alert_type: str  # notification, warning, error, success, emergency
    message: str
    priority: str = "normal"  # low, normal, high, urgent


class AccessibilityPreferences(BaseModel):
    screen_reader: bool = False
    captions_enabled: bool = False
    high_contrast: bool = False
    large_text: bool = False
    tts_enabled: bool = False
    visual_alerts_only: bool = False
    keyboard_navigation: bool = True
    reduce_motion: bool = False


@router.post("/tts")
async def text_to_speech(request: TTSRequest):
    """
    Convert text to speech (for blind users)
    
    **Example:**
    ```json
    {
        "text": "Bienvenue sur la plateforme éducative",
        "language": "fr",
        "voice": "female",
        "speed": 1.0
    }
    ```
    """
    try:
        result = await accessibility_service.text_to_speech(
            text=request.text,
            language=request.language,
            voice=request.voice,
            speed=request.speed,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stt")
async def speech_to_text(request: STTRequest):
    """
    Convert speech to text (for voice input)
    
    **Example:**
    ```json
    {
        "audio_url": "https://example.com/audio.mp3",
        "language": "fr",
        "enable_punctuation": true
    }
    ```
    """
    try:
        result = await accessibility_service.speech_to_text(
            audio_file=request.audio_url,
            language=request.language,
            enable_punctuation=request.enable_punctuation,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/captions")
async def generate_captions(request: CaptionRequest):
    """
    Generate automatic captions for video (for deaf users)
    
    **Example:**
    ```json
    {
        "video_url": "https://example.com/lecture.mp4",
        "language": "fr",
        "format": "srt"
    }
    ```
    """
    try:
        result = await accessibility_service.generate_captions(
            video_url=request.video_url,
            language=request.language,
            format=request.format,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/visual-alert")
async def create_visual_alert(request: VisualAlertRequest):
    """
    Create visual alert for deaf users (replaces audio notifications)
    
    **Example:**
    ```json
    {
        "alert_type": "emergency",
        "message": "Nouvelle urgence médicale détectée",
        "priority": "urgent"
    }
    ```
    """
    try:
        result = await accessibility_service.generate_visual_alert(
            alert_type=request.alert_type,
            message=request.message,
            priority=request.priority,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize-screen-reader")
async def optimize_for_screen_reader(
    html_content: str = Form(...),
    add_landmarks: bool = Form(True),
    add_aria_labels: bool = Form(True),
):
    """
    Optimize HTML content for screen readers (for blind users)
    
    Adds:
    - ARIA landmarks (nav, main, aside, footer)
    - ARIA labels for interactive elements
    - Proper heading hierarchy
    - Alt text for images
    - Skip navigation links
    """
    try:
        result = await accessibility_service.optimize_for_screen_reader(
            html_content=html_content,
            add_landmarks=add_landmarks,
            add_aria_labels=add_aria_labels,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/audio-description")
async def generate_audio_description(
    video_url: str = Form(...),
    language: str = Form("fr"),
):
    """
    Generate audio descriptions for video content (for blind users)
    
    Describes visual elements happening in the video
    """
    try:
        result = await accessibility_service.generate_audio_description(
            video_url=video_url,
            language=language,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/preferences/{user_id}")
async def get_accessibility_preferences(user_id: str):
    """
    Get user's accessibility preferences
    """
    try:
        preferences = accessibility_service.get_accessibility_preferences(user_id)
        return preferences
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/preferences/{user_id}")
async def save_accessibility_preferences(
    user_id: str,
    preferences: AccessibilityPreferences,
):
    """
    Save user's accessibility preferences
    
    **Example:**
    ```json
    {
        "screen_reader": true,
        "captions_enabled": true,
        "high_contrast": false,
        "large_text": true,
        "tts_enabled": true,
        "visual_alerts_only": true,
        "keyboard_navigation": true,
        "reduce_motion": false
    }
    ```
    """
    try:
        result = await accessibility_service.save_accessibility_preferences(
            user_id=user_id,
            preferences=preferences.dict(),
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/features")
async def list_accessibility_features():
    """
    List all available accessibility features
    """
    return {
        "features": {
            "for_blind_users": [
                {
                    "name": "Text-to-Speech (TTS)",
                    "endpoint": "/accessibility/tts",
                    "description": "Convert text to audio",
                },
                {
                    "name": "Screen Reader Optimization",
                    "endpoint": "/accessibility/optimize-screen-reader",
                    "description": "Add ARIA labels and landmarks",
                },
                {
                    "name": "Audio Descriptions",
                    "endpoint": "/accessibility/audio-description",
                    "description": "Describe visual video content",
                },
                {
                    "name": "Keyboard Navigation",
                    "description": "Full keyboard support for all features",
                },
            ],
            "for_deaf_users": [
                {
                    "name": "Automatic Captions",
                    "endpoint": "/accessibility/captions",
                    "description": "Generate video captions",
                },
                {
                    "name": "Visual Alerts",
                    "endpoint": "/accessibility/visual-alert",
                    "description": "Replace audio notifications",
                },
                {
                    "name": "Live Transcription",
                    "description": "Real-time speech-to-text in chatrooms",
                },
                {
                    "name": "Vibration Patterns",
                    "description": "Tactile feedback on mobile devices",
                },
            ],
            "universal": [
                {
                    "name": "High Contrast Mode",
                    "description": "Improved visibility",
                },
                {
                    "name": "Large Text",
                    "description": "Scalable font sizes",
                },
                {
                    "name": "Reduced Motion",
                    "description": "Minimize animations",
                },
            ],
        },
        "supported_languages": [
            "fr", "en", "ar", "es", "de", "zh"
        ],
    }
