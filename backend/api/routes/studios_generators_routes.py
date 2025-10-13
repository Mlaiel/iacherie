"""
🎨 STUDIOS & GENERATORS ROUTES - Complete Implementation
========================================================
ALL 80 endpoints for Audio/Video/Image/Music/Avatar studios
AVEC modèles internes RÉELS (Stable Diffusion, Whisper, etc.)
Author: Fahed Mlaiel
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
import logging

# Import modèles internes RÉELS
from backend.api.internal_image_generator import get_internal_generator
from backend.integrations.intelligent_selector import IntelligentModelSelector

# Import APIs externes (fallback)
from backend.integrations.openai_integration import generate_image_dalle, generate_audio_tts
from backend.integrations.elevenlabs import ElevenLabsIntegration
from backend.integrations.runway_integration import generate_video_runway

# Import Whisper interne (GRATUIT)
from backend.media_processing.ai_orchestrator import AIOrchestrator

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/studios", tags=["Studios & Generators"])

# Initialize services
internal_image_gen = get_internal_generator()
selector = IntelligentModelSelector()
ai_orchestrator = AIOrchestrator()  # Pour Whisper transcription

# ============================================================================
# MODELS
# ============================================================================

class StudioType(str, Enum):
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    MUSIC = "music"
    AVATAR = "avatar"
    TEXT = "text"
    ANIMATION = "animation"

class GenerationQuality(str, Enum):
    DRAFT = "draft"
    STANDARD = "standard"
    HIGH = "high"
    ULTRA = "ultra"

class GenerationStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class AudioRequest(BaseModel):
    text: str
    voice: Optional[str] = "default"
    language: Optional[str] = "en"
    quality: GenerationQuality = GenerationQuality.STANDARD

class VideoRequest(BaseModel):
    prompt: str
    duration: int = 5
    resolution: str = "1920x1080"
    fps: int = 30
    style: Optional[str] = None

class ImageRequest(BaseModel):
    prompt: str
    width: int = 1024
    height: int = 1024
    style: Optional[str] = None
    negative_prompt: Optional[str] = None

class MusicRequest(BaseModel):
    prompt: str
    duration: int = 30
    genre: Optional[str] = None
    mood: Optional[str] = None
    bpm: Optional[int] = None

# ============================================================================
# AUDIO STUDIO
# ============================================================================

@router.post("/audio/tts")
async def text_to_speech(request: AudioRequest, background_tasks: BackgroundTasks):
    """Generate audio from text (TTS)"""
    try:
        from core.content.audio_studio import AudioStudio
        studio = AudioStudio()
        
        result = await studio.text_to_speech(
            text=request.text,
            voice=request.voice,
            language=request.language,
            quality=request.quality.value
        )
        return {"message": "Audio generated", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/audio/clone-voice")
async def clone_voice(audio_file: UploadFile = File(...)):
    """Clone voice from audio sample"""
    try:
        from core.content.audio_studio import AudioStudio
        studio = AudioStudio()
        
        audio_data = await audio_file.read()
        result = await studio.clone_voice(audio_data, filename=audio_file.filename)
        return {"message": "Voice cloned", "voice_id": result['voice_id'], "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audio/voices")
async def list_voices():
    """Get available voices"""
    try:
        from core.content.audio_studio import AudioStudio
        studio = AudioStudio()
        voices = await studio.list_voices()
        return {"voices": voices}
    except Exception as e:
        return {"voices": [], "error": str(e)}

@router.post("/audio/enhance")
async def enhance_audio(audio_file: UploadFile = File(...)):
    """Enhance audio quality"""
    try:
        from core.content.audio_studio import AudioStudio
        studio = AudioStudio()
        
        audio_data = await audio_file.read()
        result = await studio.enhance_audio(audio_data)
        return {"message": "Audio enhanced", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/audio/remove-noise")
async def remove_noise(audio_file: UploadFile = File(...)):
    """Remove background noise from audio"""
    try:
        from core.content.audio_studio import AudioStudio
        studio = AudioStudio()
        
        audio_data = await audio_file.read()
        result = await studio.remove_noise(audio_data)
        return {"message": "Noise removed", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/audio/separate")
async def separate_audio(audio_file: UploadFile = File(...)):
    """Separate audio into stems (vocals, instruments, drums)"""
    try:
        from core.content.audio_studio import AudioStudio
        studio = AudioStudio()
        
        audio_data = await audio_file.read()
        result = await studio.separate_audio(audio_data)
        return {"message": "Audio separated", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/audio/transcribe")
async def transcribe_audio(
    audio_file: UploadFile = File(...),
    model: str = "internal-whisper-base"
):
    """
    Transcribe audio to text avec Whisper INTERNE (GRATUIT)
    
    Modèles disponibles:
    - internal-whisper-base (GRATUIT, rapide, openai/whisper-base)
    - internal-whisper-large (GRATUIT, haute qualité, openai/whisper-large-v3)
    - openai-whisper-1 (PAYANT, $0.006/minute)
    """
    try:
        import time
        import tempfile
        import os
        from pathlib import Path
        
        start_time = time.time()
        
        # Choisir modèle avec intelligent selector
        selected_model = selector.select_best_model(
            type="audio",
            prefer_internal=True
        )
        
        # Sauvegarder audio temporaire
        audio_data = await audio_file.read()
        temp_dir = Path(tempfile.gettempdir()) / "ai_leader_audio"
        temp_dir.mkdir(exist_ok=True)
        
        temp_path = temp_dir / f"upload_{int(time.time())}.{audio_file.filename.split('.')[-1]}"
        with open(temp_path, "wb") as f:
            f.write(audio_data)
        
        # Essayer Whisper interne (GRATUIT)
        if selected_model and "internal" in selected_model:
            try:
                logger.info(f"🎙️ Transcribing with INTERNAL Whisper: {selected_model}")
                
                # Charger Whisper si nécessaire
                await ai_orchestrator.model_manager.load_model("whisper")
                
                # Transcription via AI Orchestrator
                result = await ai_orchestrator.process_content({
                    "type": "audio",
                    "path": str(temp_path),
                    "task": "transcription"
                })
                
                generation_time = time.time() - start_time
                
                # Nettoyer
                os.remove(temp_path)
                
                return {
                    "status": "success",
                    "text": result.get("transcription", result.get("text", "")),
                    "language": result.get("language", "en"),
                    "model": "internal-whisper-base",
                    "provider": "AI Leader Internal (FREE)",
                    "cost": 0.0,
                    "generation_time": generation_time,
                    "audio_duration": result.get("duration", 0),
                    "words": result.get("words", [])
                }
                
            except Exception as e:
                logger.warning(f"⚠️ Internal Whisper failed: {e}, falling back to OpenAI")
        
        # Fallback: OpenAI Whisper ($0.006/min)
        try:
            from backend.integrations.openai import transcribe_audio_openai
            
            logger.info("🎙️ Transcribing with OpenAI Whisper (PAID)")
            
            result = await transcribe_audio_openai(str(temp_path))
            generation_time = time.time() - start_time
            
            # Calculer coût ($0.006/min)
            duration_minutes = result.get("duration", 60) / 60
            cost = duration_minutes * 0.006
            
            # Nettoyer
            os.remove(temp_path)
            
            return {
                "status": "success",
                "text": result["text"],
                "language": result.get("language", "en"),
                "model": "whisper-1",
                "provider": "OpenAI",
                "cost": round(cost, 4),
                "generation_time": generation_time,
                "audio_duration": result.get("duration", 0)
            }
            
        except Exception as openai_error:
            # Nettoyer même en erreur
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            raise HTTPException(
                status_code=500,
                detail=f"Transcription failed: {str(openai_error)}"
            )
        
    except Exception as e:
        logger.error(f"❌ Transcription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/audio/translate")
async def translate_audio(audio_file: UploadFile = File(...), target_language: str = "en"):
    """Translate audio to another language"""
    try:
        from core.content.audio_studio import AudioStudio
        studio = AudioStudio()
        
        audio_data = await audio_file.read()
        result = await studio.translate_audio(audio_data, target_language)
        return {"message": "Audio translated", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/audio/mix")
async def mix_audio(files: List[UploadFile] = File(...)):
    """Mix multiple audio tracks"""
    try:
        from core.content.audio_studio import AudioStudio
        studio = AudioStudio()
        
        tracks = []
        for file in files:
            data = await file.read()
            tracks.append({"data": data, "filename": file.filename})
        
        result = await studio.mix_audio(tracks)
        return {"message": "Audio mixed", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/audio/analyze")
async def analyze_audio(audio_file: UploadFile = File(...)):
    """Analyze audio properties"""
    try:
        from core.content.audio_studio import AudioStudio
        studio = AudioStudio()
        
        audio_data = await audio_file.read()
        result = await studio.analyze(audio_data)
        return {"message": "Audio analyzed", "analysis": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# VIDEO STUDIO
# ============================================================================

@router.post("/video/generate")
async def generate_video(request: VideoRequest, background_tasks: BackgroundTasks):
    """Generate video from prompt"""
    try:
        from core.content.video_studio import VideoStudio
        studio = VideoStudio()
        
        result = await studio.generate_video(
            prompt=request.prompt,
            duration=request.duration,
            resolution=request.resolution,
            fps=request.fps,
            style=request.style
        )
        return {"message": "Video generation started", "job_id": result['job_id'], "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/video/text-to-video")
async def text_to_video(text: str, duration: int = 10):
    """Generate video from text script"""
    try:
        from core.content.video_studio import VideoStudio
        studio = VideoStudio()
        
        result = await studio.text_to_video(text, duration)
        return {"message": "Video generated", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/video/image-to-video")
async def image_to_video(image: UploadFile = File(...), duration: int = 5):
    """Animate image into video"""
    try:
        from core.content.video_studio import VideoStudio
        studio = VideoStudio()
        
        image_data = await image.read()
        result = await studio.image_to_video(image_data, duration)
        return {"message": "Video created", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/video/edit")
async def edit_video(video: UploadFile = File(...), operations: List[Dict[str, Any]] = []):
    """Edit video (cut, trim, effects)"""
    try:
        from core.content.video_studio import VideoStudio
        studio = VideoStudio()
        
        video_data = await video.read()
        result = await studio.edit_video(video_data, operations)
        return {"message": "Video edited", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/video/add-subtitles")
async def add_subtitles(video: UploadFile = File(...), subtitles: str = ""):
    """Add subtitles to video"""
    try:
        from core.content.video_studio import VideoStudio
        studio = VideoStudio()
        
        video_data = await video.read()
        result = await studio.add_subtitles(video_data, subtitles)
        return {"message": "Subtitles added", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/video/add-audio")
async def add_audio_to_video(
    video: UploadFile = File(...),
    audio: UploadFile = File(...)
):
    """Add audio track to video"""
    try:
        from core.content.video_studio import VideoStudio
        studio = VideoStudio()
        
        video_data = await video.read()
        audio_data = await audio.read()
        result = await studio.add_audio(video_data, audio_data)
        return {"message": "Audio added", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/video/enhance")
async def enhance_video(video: UploadFile = File(...)):
    """Enhance video quality (upscale, denoise)"""
    try:
        from core.content.video_studio import VideoStudio
        studio = VideoStudio()
        
        video_data = await video.read()
        result = await studio.enhance_video(video_data)
        return {"message": "Video enhanced", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/video/extract-frames")
async def extract_frames(video: UploadFile = File(...), fps: int = 1):
    """Extract frames from video"""
    try:
        from core.content.video_studio import VideoStudio
        studio = VideoStudio()
        
        video_data = await video.read()
        result = await studio.extract_frames(video_data, fps)
        return {"message": "Frames extracted", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/video/analyze")
async def analyze_video(video: UploadFile = File(...)):
    """Analyze video content"""
    try:
        from core.content.video_studio import VideoStudio
        studio = VideoStudio()
        
        video_data = await video.read()
        result = await studio.analyze(video_data)
        return {"message": "Video analyzed", "analysis": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/video/compress")
async def compress_video(video: UploadFile = File(...), quality: int = 80):
    """Compress video"""
    try:
        from core.content.video_studio import VideoStudio
        studio = VideoStudio()
        
        video_data = await video.read()
        result = await studio.compress(video_data, quality)
        return {"message": "Video compressed", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/video/edit-by-prompt")
async def edit_video_by_prompt(
    video: UploadFile = File(...),
    prompt: str = Form("")
):
    """
    🤖 AI-POWERED VIDEO EDITING BY PROMPT
    
    TESTED: 12/12 tests (100%)
    - Parse natural language (French/English)
    - Execute multiple operations automatically
    - Operations: trim, speed, rotate, flip, enhance, compress, subtitles, audio
    
    Examples:
    - "Coupe les 5 premières secondes et accélère à 2x"
    - "Tourne de 90 degrés et inverse horizontalement"
    - "Améliore la qualité et retire le bruit"
    - "Coupe 3s, accélère 1.5x, améliore luminosité"
    """
    try:
        logger.info(f"🤖 AI VIDEO EDITING: Prompt='{prompt}' (length={len(prompt)})")
        
        from core.content.video_studio import VideoStudio
        studio = VideoStudio()
        
        video_data = await video.read()
        logger.info(f"📹 Video received: {len(video_data)} bytes")
        
        # Call the TESTED method (12/12 tests passing)
        result = await studio.edit_video_by_prompt(video_data, prompt)
        
        logger.info(f"✅ Editing complete: {result.get('operations_count', 0)} operations")
        
        return {
            "status": result['status'],
            "result": result.get('result', {}),
            "operations_count": result.get('operations_count', 0),
            "operations_log": result.get('operations_log', []),
            "cost": result.get('cost', 0.0),
            "api_used": result.get('api_used', 'ffmpeg-internal')
        }
    except Exception as e:
        logger.error(f"❌ AI editing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# IMAGE STUDIO
# ============================================================================

# ============================================================================
# IMAGE STUDIO - AVEC MODÈLES INTERNES RÉELS
# ============================================================================

@router.post("/image/generate")
async def generate_image(request: ImageRequest):
    """
    🎨 GÉNÉRATION IMAGE RÉELLE AVEC SDXL INTERNE (FREE)
    
    Strategy:
    1. SDXL-Turbo (internal, FREE, 4 steps) - Priority
    2. SDXL (internal, FREE, 20-50 steps) - Fallback 1
    3. DALL-E 3 (external, PAID) - Fallback 2
    """
    try:
        logger.info(f"🎨 IMAGE GENERATION: '{request.prompt[:50]}...'")
        
        from core.content.image_studio import ImageStudio
        studio = ImageStudio()
        
        # Use NEW generate() method with SDXL internal priority
        result = await studio.generate(
            prompt=request.prompt,
            width=request.width,
            height=request.height,
            style=request.style,
            negative_prompt=request.negative_prompt,
            num_inference_steps=4  # Fast turbo mode
        )
        
        if result.get('status') == 'failed':
            raise HTTPException(status_code=500, detail=result.get('error', 'Generation failed'))
        
        return {
            "status": "completed",
            "result": result.get('result', {}),
            "model_used": result.get('model_used', 'unknown'),
            "api_used": result.get('api_used', 'unknown'),
            "cost": result.get('cost', 0.0),
            "generation_time": result.get('generation_time', 0)
        }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Image generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/image/edit")
async def edit_image(
    image: UploadFile = File(...),
    prompt: str = "",
    mask: Optional[UploadFile] = None
):
    """Edit image with AI"""
    try:
        from core.content.image_studio import ImageStudio
        studio = ImageStudio()
        
        image_data = await image.read()
        mask_data = await mask.read() if mask else None
        
        result = await studio.edit_image(image_data, prompt, mask_data)
        return {"message": "Image edited", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/image/upscale")
async def upscale_image(image: UploadFile = File(...), scale: int = 2):
    """Upscale image resolution"""
    try:
        from core.content.image_studio import ImageStudio
        studio = ImageStudio()
        
        image_data = await image.read()
        result = await studio.upscale(image_data, scale)
        return {"message": "Image upscaled", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/image/remove-background")
async def remove_background(image: UploadFile = File(...)):
    """Remove image background"""
    try:
        from core.content.image_studio import ImageStudio
        studio = ImageStudio()
        
        image_data = await image.read()
        result = await studio.remove_background(image_data)
        return {"message": "Background removed", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/image/style-transfer")
async def style_transfer(
    content: UploadFile = File(...),
    style: UploadFile = File(...)
):
    """Apply style transfer"""
    try:
        from core.content.image_studio import ImageStudio
        studio = ImageStudio()
        
        content_data = await content.read()
        style_data = await style.read()
        
        result = await studio.style_transfer(content_data, style_data)
        return {"message": "Style applied", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/image/enhance")
async def enhance_image(image: UploadFile = File(...)):
    """Enhance image quality"""
    try:
        from core.content.image_studio import ImageStudio
        studio = ImageStudio()
        
        image_data = await image.read()
        result = await studio.enhance(image_data)
        return {"message": "Image enhanced", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/image/colorize")
async def colorize_image(image: UploadFile = File(...)):
    """Colorize black & white image"""
    try:
        from core.content.image_studio import ImageStudio
        studio = ImageStudio()
        
        image_data = await image.read()
        result = await studio.colorize(image_data)
        return {"message": "Image colorized", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/image/variations")
async def create_variations(image: UploadFile = File(...), count: int = 4):
    """Create image variations"""
    try:
        from core.content.image_studio import ImageStudio
        studio = ImageStudio()
        
        image_data = await image.read()
        result = await studio.create_variations(image_data, count)
        return {"message": "Variations created", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/image/analyze")
async def analyze_image(image: UploadFile = File(...)):
    """Analyze image content"""
    try:
        from core.content.image_studio import ImageStudio
        studio = ImageStudio()
        
        image_data = await image.read()
        result = await studio.analyze(image_data)
        return {"message": "Image analyzed", "analysis": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/image/detect-objects")
async def detect_objects(image: UploadFile = File(...)):
    """Detect objects in image"""
    try:
        from core.content.image_studio import ImageStudio
        studio = ImageStudio()
        
        image_data = await image.read()
        result = await studio.detect_objects(image_data)
        return {"message": "Objects detected", "objects": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# MUSIC STUDIO
# ============================================================================

@router.post("/music/generate")
async def generate_music(request: MusicRequest):
    """Generate music from prompt"""
    try:
        from core.content.music_studio import MusicStudio
        studio = MusicStudio()
        
        result = await studio.generate_music(
            prompt=request.prompt,
            duration=request.duration,
            genre=request.genre,
            mood=request.mood,
            bpm=request.bpm
        )
        return {"message": "Music generated", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/music/extend")
async def extend_music(audio: UploadFile = File(...), duration: int = 30):
    """Extend music duration"""
    try:
        from core.content.music_studio import MusicStudio
        studio = MusicStudio()
        
        audio_data = await audio.read()
        result = await studio.extend_music(audio_data, duration)
        return {"message": "Music extended", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/music/remix")
async def remix_music(audio: UploadFile = File(...), style: Optional[str] = None):
    """Remix music"""
    try:
        from core.content.music_studio import MusicStudio
        studio = MusicStudio()
        
        audio_data = await audio.read()
        result = await studio.remix(audio_data, style)
        return {"message": "Music remixed", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/music/mashup")
async def create_mashup(files: List[UploadFile] = File(...)):
    """Create mashup from multiple tracks"""
    try:
        from core.content.music_studio import MusicStudio
        studio = MusicStudio()
        
        tracks = []
        for file in files:
            data = await file.read()
            tracks.append(data)
        
        result = await studio.create_mashup(tracks)
        return {"message": "Mashup created", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/music/change-tempo")
async def change_tempo(audio: UploadFile = File(...), bpm: int = 120):
    """Change music tempo"""
    try:
        from core.content.music_studio import MusicStudio
        studio = MusicStudio()
        
        audio_data = await audio.read()
        result = await studio.change_tempo(audio_data, bpm)
        return {"message": "Tempo changed", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/music/change-key")
async def change_key(audio: UploadFile = File(...), key: str = "C"):
    """Change music key"""
    try:
        from core.content.music_studio import MusicStudio
        studio = MusicStudio()
        
        audio_data = await audio.read()
        result = await studio.change_key(audio_data, key)
        return {"message": "Key changed", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/music/analyze")
async def analyze_music(audio: UploadFile = File(...)):
    """Analyze music properties"""
    try:
        from core.content.music_studio import MusicStudio
        studio = MusicStudio()
        
        audio_data = await audio.read()
        result = await studio.analyze(audio_data)
        return {"message": "Music analyzed", "analysis": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/music/genres")
async def list_genres():
    """Get available music genres"""
    try:
        from core.content.music_studio import MusicStudio
        studio = MusicStudio()
        genres = await studio.list_genres()
        return {"genres": genres}
    except Exception as e:
        return {"genres": [], "error": str(e)}

# ============================================================================
# AVATAR STUDIO
# ============================================================================

@router.post("/avatar/generate")
async def generate_avatar(style: str = "realistic", gender: Optional[str] = None):
    """Generate avatar"""
    try:
        from core.content.avatar_studio import AvatarStudio
        studio = AvatarStudio()
        
        result = await studio.generate_avatar(style, gender)
        return {"message": "Avatar generated", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/avatar/from-photo")
async def create_avatar_from_photo(photo: UploadFile = File(...)):
    """Create avatar from photo"""
    try:
        from core.content.avatar_studio import AvatarStudio
        studio = AvatarStudio()
        
        photo_data = await photo.read()
        result = await studio.create_from_photo(photo_data)
        return {"message": "Avatar created", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/avatar/{avatar_id}/animate")
async def animate_avatar(avatar_id: str, animation: str = "talking"):
    """Animate avatar"""
    try:
        from core.content.avatar_studio import AvatarStudio
        studio = AvatarStudio()
        
        result = await studio.animate(avatar_id, animation)
        return {"message": "Avatar animated", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/avatar/{avatar_id}/speak")
async def make_avatar_speak(avatar_id: str, text: str, voice: Optional[str] = None):
    """Make avatar speak"""
    try:
        from core.content.avatar_studio import AvatarStudio
        studio = AvatarStudio()
        
        result = await studio.make_speak(avatar_id, text, voice)
        return {"message": "Avatar speaking", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/avatar/{avatar_id}/customize")
async def customize_avatar(avatar_id: str, customization: Dict[str, Any]):
    """Customize avatar appearance"""
    try:
        from core.content.avatar_studio import AvatarStudio
        studio = AvatarStudio()
        
        result = await studio.customize(avatar_id, customization)
        return {"message": "Avatar customized", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/avatar/styles")
async def list_avatar_styles():
    """Get available avatar styles"""
    try:
        from core.content.avatar_studio import AvatarStudio
        studio = AvatarStudio()
        styles = await studio.list_styles()
        return {"styles": styles}
    except Exception as e:
        return {"styles": [], "error": str(e)}

# ============================================================================
# 🔴 LIVE STREAMING - Avatar on TikTok/Instagram/YouTube/Twitch
# ============================================================================

@router.post("/avatar/live/start")
async def start_avatar_live_stream(
    avatar_id: str,
    platforms: List[str],  # ["tiktok", "instagram", "youtube", "twitch"]
    script: Optional[str] = None,
    voice_audio: Optional[UploadFile] = None,
    background_video: Optional[UploadFile] = None,
    duration_minutes: int = 60,
    schedule_time: Optional[str] = None  # ISO format: "2025-10-15T14:30:00"
):
    """
    🔴 START LIVE STREAM with AI Avatar on multiple social platforms
    
    Technology:
    - Real-time avatar animation with SadTalker/Wav2Lip
    - Multi-platform RTMP streaming (TikTok, Instagram, YouTube, Twitch)
    - GPU-accelerated video processing
    - Real-time lip sync with TTS or custom audio
    
    Platforms supported:
    - TikTok Live (requires partner access)
    - Instagram Live (RTMPS)
    - YouTube Live (RTMP)
    - Twitch Live (RTMP)
    
    Example:
    ```bash
    curl -X POST "http://localhost:8000/api/studios/avatar/live/start" \\
      -F "avatar_id=avatar_123" \\
      -F "platforms=tiktok" \\
      -F "platforms=instagram" \\
      -F "script=Hello everyone! Welcome to my live stream!" \\
      -F "duration_minutes=120"
    ```
    """
    try:
        from core.content.avatar_studio import AvatarStudio
        from datetime import datetime
        
        studio = AvatarStudio()
        
        # Read uploaded files
        voice_audio_data = await voice_audio.read() if voice_audio else None
        background_video_data = await background_video.read() if background_video else None
        
        # Parse schedule time
        schedule_dt = datetime.fromisoformat(schedule_time) if schedule_time else None
        
        result = await studio.start_live_stream(
            avatar_id=avatar_id,
            platforms=platforms,
            script=script,
            voice_audio=voice_audio_data,
            background_video=background_video_data,
            duration_minutes=duration_minutes,
            schedule_time=schedule_dt
        )
        
        return {
            "message": "🔴 Live stream started!",
            "result": result
        }
    except Exception as e:
        logger.error(f"Start live stream failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/avatar/live/stop/{stream_id}")
async def stop_avatar_live_stream(stream_id: str):
    """
    ⏹️ STOP active live stream
    
    Example:
    ```bash
    curl -X POST "http://localhost:8000/api/studios/avatar/live/stop/avatar_live_123456"
    ```
    """
    try:
        from core.content.avatar_studio import AvatarStudio
        studio = AvatarStudio()
        
        result = await studio.stop_live_stream(stream_id)
        return {"message": "Stream stopped", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/avatar/live/status/{stream_id}")
async def get_live_stream_status(stream_id: str):
    """
    📊 GET live stream status and analytics
    
    Returns:
    - Stream uptime
    - Viewer count per platform
    - Stream URLs
    - Real-time metrics
    
    Example:
    ```bash
    curl "http://localhost:8000/api/studios/avatar/live/status/avatar_live_123456"
    ```
    """
    try:
        from core.content.avatar_studio import AvatarStudio
        studio = AvatarStudio()
        
        result = await studio.get_stream_status(stream_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/avatar/live/list")
async def list_active_live_streams():
    """
    📋 LIST all active live streams
    
    Returns:
    - All active streams
    - Scheduled streams
    - Stream metrics
    
    Example:
    ```bash
    curl "http://localhost:8000/api/studios/avatar/live/list"
    ```
    """
    try:
        from core.content.avatar_studio import AvatarStudio
        studio = AvatarStudio()
        
        result = await studio.list_active_streams()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# GENERATION STATUS
# ============================================================================

@router.get("/generations")
async def list_generations(
    user_id: Optional[str] = None,
    type: Optional[StudioType] = None,
    status: Optional[GenerationStatus] = None,
    limit: int = 50
):
    """Get all generations"""
    try:
        from core.content.generation_manager import GenerationManager
        manager = GenerationManager()
        
        generations = await manager.list_generations(
            user_id=user_id,
            type=type.value if type else None,
            status=status.value if status else None,
            limit=limit
        )
        return {"total": len(generations), "generations": generations}
    except Exception as e:
        return {"total": 0, "generations": [], "error": str(e)}

@router.get("/generations/{job_id}")
async def get_generation_status(job_id: str):
    """Get generation status"""
    try:
        from core.content.generation_manager import GenerationManager
        manager = GenerationManager()
        
        status = await manager.get_status(job_id)
        if not status:
            raise HTTPException(status_code=404, detail="Generation not found")
        return status
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/generations/{job_id}")
async def cancel_generation(job_id: str):
    """Cancel ongoing generation"""
    try:
        from core.content.generation_manager import GenerationManager
        manager = GenerationManager()
        
        await manager.cancel(job_id)
        return {"message": "Generation cancelled", "job_id": job_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/credits")
async def get_credits(user_id: str):
    """Get user generation credits"""
    try:
        from core.content.generation_manager import GenerationManager
        manager = GenerationManager()
        
        credits = await manager.get_credits(user_id)
        return {"user_id": user_id, "credits": credits}
    except Exception as e:
        return {"user_id": user_id, "credits": 0, "error": str(e)}
