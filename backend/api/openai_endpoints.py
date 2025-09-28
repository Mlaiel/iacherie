"""
OpenAI API Routes for Ainfluencer Platform
Provides REST endpoints for OpenAI services integration
"""
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import tempfile
import os
import json
from backend.services.openai_integration_service import (
    openai_service, 
    CompletionRequest, 
    ChatMessage, 
    ImageGenerationRequest,
    AudioTranscriptionRequest
)
from backend.security.auth_manager import get_current_user
from backend.security.permissions_manager import require_permissions
from backend.monitoring.openai_metrics import track_api_usage

router = APIRouter(prefix="/api/openai", tags=["OpenAI Integration"])

class QuickChatRequest(BaseModel):
    """Quick chat request for simple interactions"""
    message: str
    system_prompt: Optional[str] = "You are a helpful AI assistant for the Ainfluencer platform."
    model: Optional[str] = None
    temperature: Optional[float] = None

class ContentGenerationRequest(BaseModel):
    """Content generation for social media"""
    content_type: str  # "post", "caption", "hashtags", "story"
    topic: str
    platform: str  # "instagram", "tiktok", "youtube", "facebook"
    tone: str = "professional"  # "casual", "professional", "humorous", "inspirational"
    target_audience: Optional[str] = None
    keywords: Optional[List[str]] = None

class ScriptGenerationRequest(BaseModel):
    """Video script generation"""
    video_type: str  # "short", "tutorial", "review", "entertainment"
    duration_minutes: int
    topic: str
    style: str = "engaging"
    include_hooks: bool = True
    include_cta: bool = True

@router.get("/health")
async def health_check():
    """Check OpenAI service health"""
    return await openai_service.health_check()

@router.post("/chat")
@require_permissions(["openai_access"])
async def chat_completion(
    request: CompletionRequest,
    current_user = Depends(get_current_user)
):
    """
    Generate chat completion using OpenAI
    Requires openai_access permission
    """
    result = await openai_service.chat_completion(request)
    await track_api_usage("openai_chat", current_user.id, result.get("usage", {}))
    return result

@router.post("/quick-chat")
@require_permissions(["basic_ai_access"])
async def quick_chat(
    request: QuickChatRequest,
    current_user = Depends(get_current_user)
):
    """Quick chat interface for simple AI interactions"""
    messages = [
        ChatMessage(role="system", content=request.system_prompt),
        ChatMessage(role="user", content=request.message)
    ]
    
    completion_request = CompletionRequest(
        messages=messages,
        model=request.model,
        temperature=request.temperature
    )
    
    result = await openai_service.chat_completion(completion_request)
    await track_api_usage("openai_quick_chat", current_user.id, result.get("usage", {}))
    return result

@router.post("/generate-content")
@require_permissions(["content_generation"])
async def generate_content(
    request: ContentGenerationRequest,
    current_user = Depends(get_current_user)
):
    """Generate social media content using AI"""
    
    # Build context-aware prompt
    system_prompt = f"""You are an expert social media content creator for the Ainfluencer platform. 
    Generate engaging {request.content_type} content for {request.platform} with a {request.tone} tone.
    Target audience: {request.target_audience or 'general'}
    Keywords to include: {', '.join(request.keywords) if request.keywords else 'none specified'}
    
    Provide content that is platform-optimized, engaging, and follows best practices."""
    
    user_prompt = f"""Create a {request.content_type} about: {request.topic}
    
    Platform: {request.platform}
    Tone: {request.tone}
    
    Please provide:
    1. Main content text
    2. Suggested hashtags (if applicable)
    3. Engagement tips
    4. Best posting time recommendations"""
    
    messages = [
        ChatMessage(role="system", content=system_prompt),
        ChatMessage(role="user", content=user_prompt)
    ]
    
    completion_request = CompletionRequest(
        messages=messages,
        model="gpt-4o-mini",
        temperature=0.8  # Higher creativity for content generation
    )
    
    result = await openai_service.chat_completion(completion_request)
    await track_api_usage("content_generation", current_user.id, result.get("usage", {}))
    
    return {
        **result,
        "content_type": request.content_type,
        "platform": request.platform,
        "metadata": {
            "topic": request.topic,
            "tone": request.tone,
            "target_audience": request.target_audience
        }
    }

@router.post("/generate-script")
@require_permissions(["script_generation"])
async def generate_script(
    request: ScriptGenerationRequest,
    current_user = Depends(get_current_user)
):
    """Generate video scripts for content creators"""
    
    system_prompt = f"""You are a professional video script writer for the Ainfluencer platform.
    Create engaging {request.video_type} video scripts that are approximately {request.duration_minutes} minutes long.
    Style: {request.style}
    Include attention-grabbing hooks: {request.include_hooks}
    Include call-to-action: {request.include_cta}
    
    Structure your scripts with:
    - Hook/Opening (first 3-5 seconds)
    - Main content sections with timestamps
    - Transition phrases
    - Visual cues and suggestions
    - Call-to-action (if requested)"""
    
    user_prompt = f"""Write a {request.duration_minutes}-minute {request.video_type} video script about: {request.topic}
    
    Please format with:
    [TIMESTAMP] - Action/Dialog
    [VISUAL] - Visual suggestions
    [TRANSITION] - Smooth transitions between sections
    
    Make it engaging, informative, and suitable for social media platforms."""
    
    messages = [
        ChatMessage(role="system", content=system_prompt),
        ChatMessage(role="user", content=user_prompt)
    ]
    
    completion_request = CompletionRequest(
        messages=messages,
        model="gpt-4o-mini",
        temperature=0.7
    )
    
    result = await openai_service.chat_completion(completion_request)
    await track_api_usage("script_generation", current_user.id, result.get("usage", {}))
    
    return {
        **result,
        "script_metadata": {
            "video_type": request.video_type,
            "duration_minutes": request.duration_minutes,
            "topic": request.topic,
            "style": request.style,
            "has_hooks": request.include_hooks,
            "has_cta": request.include_cta
        }
    }

@router.post("/generate-image")
@require_permissions(["image_generation"])
async def generate_image(
    request: ImageGenerationRequest,
    current_user = Depends(get_current_user)
):
    """Generate images using DALL-E"""
    result = await openai_service.generate_image(request)
    await track_api_usage("image_generation", current_user.id, {"images_generated": len(result.get("images", []))})
    return result

@router.post("/transcribe-audio")
@require_permissions(["audio_processing"])
async def transcribe_audio(
    file: UploadFile = File(...),
    model: str = "whisper-1",
    language: Optional[str] = None,
    current_user = Depends(get_current_user)
):
    """Transcribe audio files using Whisper"""
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name
    
    try:
        request = AudioTranscriptionRequest(
            file_path=temp_file_path,
            model=model,
            language=language
        )
        
        result = await openai_service.transcribe_audio(request)
        await track_api_usage("audio_transcription", current_user.id, {"file_size": len(content)})
        
        return {
            **result,
            "file_info": {
                "filename": file.filename,
                "size_bytes": len(content),
                "content_type": file.content_type
            }
        }
        
    finally:
        # Clean up temporary file
        os.unlink(temp_file_path)

@router.post("/embeddings")
@require_permissions(["ai_analysis"])
async def generate_embeddings(
    texts: List[str],
    model: str = "text-embedding-3-small",
    current_user = Depends(get_current_user)
):
    """Generate embeddings for text analysis and similarity search"""
    result = await openai_service.get_embeddings(texts, model)
    await track_api_usage("embeddings", current_user.id, result.get("usage", {}))
    return result

@router.get("/usage-stats")
@require_permissions(["admin_access"])
async def get_usage_statistics(
    operation: Optional[str] = None,
    current_user = Depends(get_current_user)
):
    """Get OpenAI API usage statistics (Admin only)"""
    return await openai_service.get_usage_stats(operation)

@router.post("/analyze-content")
@require_permissions(["content_analysis"])
async def analyze_content(
    content: str,
    analysis_type: str = "engagement",  # "engagement", "sentiment", "seo", "compliance"
    current_user = Depends(get_current_user)
):
    """Analyze content using AI for various metrics"""
    
    analysis_prompts = {
        "engagement": "Analyze this content for engagement potential. Rate likelihood of likes, shares, comments and provide improvement suggestions.",
        "sentiment": "Analyze the sentiment and emotional tone of this content. Identify key emotions and overall sentiment score.",
        "seo": "Analyze this content for SEO optimization. Suggest keywords, meta descriptions, and content improvements.",
        "compliance": "Review this content for brand safety, compliance issues, and potential policy violations."
    }
    
    if analysis_type not in analysis_prompts:
        raise HTTPException(status_code=400, detail="Invalid analysis type")
    
    system_prompt = f"""You are an AI content analyst for the Ainfluencer platform.
    Provide detailed {analysis_type} analysis with actionable insights and recommendations.
    Format your response as JSON with clear metrics and suggestions."""
    
    user_prompt = f"""{analysis_prompts[analysis_type]}
    
    Content to analyze:
    {content}
    
    Provide structured analysis with:
    1. Overall score (1-10)
    2. Key strengths
    3. Areas for improvement
    4. Specific recommendations
    5. Risk factors (if any)"""
    
    messages = [
        ChatMessage(role="system", content=system_prompt),
        ChatMessage(role="user", content=user_prompt)
    ]
    
    completion_request = CompletionRequest(
        messages=messages,
        model="gpt-4o-mini",
        temperature=0.3  # Lower temperature for analytical tasks
    )
    
    result = await openai_service.chat_completion(completion_request)
    await track_api_usage("content_analysis", current_user.id, result.get("usage", {}))
    
    return {
        **result,
        "analysis_type": analysis_type,
        "content_length": len(content),
        "timestamp": openai_service._usage_cache
    }

# Export router
__all__ = ["router"]