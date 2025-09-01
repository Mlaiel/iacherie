"""AI Agent API Routes
AI-powered musical and content creation assistant endpoints.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import uuid
import asyncio

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
import json

from ...core.database import database_manager
from ...core.security import security_manager
from ...core.cache import cache_manager
from ...core.logging import logger
from ...ai_agents.musical.composition_engine import CompositionEngine
from ...ai_agents.musical.recommendation_engine import MusicRecommendationEngine
from ...ai_agents.musical.analysis_engine import MusicAnalysisEngine
from ...ai_agents.content.content_generator import ContentGenerator
from ...ai_agents.content.style_transfer import StyleTransferEngine


# Enums
class AgentType(str, Enum):
    MUSIC_COMPOSER = "music_composer"
    MUSIC_ANALYZER = "music_analyzer"
    RECOMMENDATION_ENGINE = "recommendation_engine"
    CONTENT_GENERATOR = "content_generator"
    STYLE_TRANSFER = "style_transfer"
    MASTERING_ASSISTANT = "mastering_assistant"


class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CreativityLevel(str, Enum):
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    CREATIVE = "creative"
    EXPERIMENTAL = "experimental"


# Pydantic models
class MusicCompositionRequest(BaseModel):
    title: Optional[str] = None
    genre: str = Field(..., min_length=1)
    mood: str = Field(..., min_length=1)
    tempo: Optional[int] = Field(None, ge=60, le=200)
    key: Optional[str] = None
    duration_seconds: int = Field(default=120, ge=10, le=600)
    instruments: List[str] = Field(default=["piano", "strings"])
    creativity_level: CreativityLevel = Field(default=CreativityLevel.BALANCED)
    reference_tracks: List[str] = Field(default=[])
    custom_prompts: Optional[str] = None
    composition_style: str = Field(default="original")


class MusicAnalysisRequest(BaseModel):
    audio_file_id: str
    analysis_type: str = Field(..., regex="^(full|structure|harmony|rhythm|melody|style)$")
    include_recommendations: bool = Field(default=True)
    compare_to_library: bool = Field(default=False)
    generate_insights: bool = Field(default=True)


class RecommendationRequest(BaseModel):
    user_preferences: Dict[str, Any]
    content_history: List[str] = Field(default=[])
    collaboration_goals: Optional[str] = None
    target_audience: Optional[str] = None
    platform_focus: List[str] = Field(default=["all"])
    recommendation_type: str = Field(..., regex="^(tracks|artists|genres|collaborators|tools)$")
    max_recommendations: int = Field(default=10, ge=1, le=50)


class ContentGenerationRequest(BaseModel):
    content_type: str = Field(..., regex="^(lyrics|description|social_post|blog_article|press_release)$")
    topic: str = Field(..., min_length=1)
    style: str = Field(default="professional")
    tone: str = Field(default="neutral")
    target_length: int = Field(default=100, ge=10, le=5000)
    keywords: List[str] = Field(default=[])
    target_audience: Optional[str] = None
    platform: Optional[str] = None
    reference_content: Optional[str] = None


class StyleTransferRequest(BaseModel):
    source_content_id: str
    target_style: str
    style_reference_id: Optional[str] = None
    transfer_strength: float = Field(default=0.7, ge=0.1, le=1.0)
    preserve_structure: bool = Field(default=True)
    custom_parameters: Optional[Dict[str, Any]] = None


class AIAgentTask(BaseModel):
    task_id: str
    agent_type: AgentType
    request_data: Dict[str, Any]
    status: TaskStatus
    progress: float = Field(default=0.0, ge=0.0, le=100.0)
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    estimated_completion: Optional[datetime] = None


class AIAgentResponse(BaseModel):
    task_id: str
    agent_type: str
    status: str
    result: Optional[Dict[str, Any]] = None
    processing_time: Optional[float] = None
    confidence_score: Optional[float] = None
    recommendations: List[str] = Field(default=[])
    metadata: Dict[str, Any] = Field(default={})


# Router setup
router = APIRouter()
security = HTTPBearer(auto_error=False)

# Initialize AI agents
composition_engine = CompositionEngine()
recommendation_engine = MusicRecommendationEngine()
analysis_engine = MusicAnalysisEngine()
content_generator = ContentGenerator()
style_transfer_engine = StyleTransferEngine()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    try:
        user_data = await security_manager.verify_token(credentials.credentials)
        return user_data
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )


@router.post("/compose/music", response_model=Dict[str, str])
async def compose_music(
    request: MusicCompositionRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user)
):
    """Generate AI-composed music based on parameters"""
    try:
        task_id = str(uuid.uuid4())
        
        # Create task record
        async with database_manager.get_postgres_session() as session:
            await session.execute("""
                INSERT INTO ai_agent_tasks (task_id, user_id, agent_type, request_data,
                                          status, progress, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                task_id, user['user_id'], AgentType.MUSIC_COMPOSER.value,
                request.dict(), TaskStatus.PENDING.value, 0.0,
                datetime.utcnow(), datetime.utcnow()
            ))
            await session.commit()
        
        # Schedule composition task
        background_tasks.add_task(
            _process_music_composition, task_id, request, user
        )
        
        logger.info(f"Music composition task created: {task_id} by user {user['user_id']}")
        
        return {
            "task_id": task_id,
            "status": "pending",
            "message": "Music composition task queued successfully",
            "estimated_duration": "2-5 minutes"
        }
        
    except Exception as e:
        logger.error(f"Music composition request failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create music composition task"
        )


@router.post("/analyze/music", response_model=Dict[str, str])
async def analyze_music(
    request: MusicAnalysisRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user)
):
    """Analyze music content using AI"""
    try:
        # Verify file ownership
        async with database_manager.get_postgres_session() as session:
            result = await session.execute("""
                SELECT file_path, content_type
                FROM uploaded_files
                WHERE file_id = %s AND user_id = %s AND content_type = 'audio'
            """, (request.audio_file_id, user['user_id']))
            
            file_info = result.fetchone()
            if not file_info:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Audio file not found or access denied"
                )
        
        task_id = str(uuid.uuid4())
        
        # Create task record
        async with database_manager.get_postgres_session() as session:
            await session.execute("""
                INSERT INTO ai_agent_tasks (task_id, user_id, agent_type, request_data,
                                          status, progress, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                task_id, user['user_id'], AgentType.MUSIC_ANALYZER.value,
                request.dict(), TaskStatus.PENDING.value, 0.0,
                datetime.utcnow(), datetime.utcnow()
            ))
            await session.commit()
        
        # Schedule analysis task
        background_tasks.add_task(
            _process_music_analysis, task_id, request, file_info[0], user
        )
        
        logger.info(f"Music analysis task created: {task_id} by user {user['user_id']}")
        
        return {
            "task_id": task_id,
            "status": "pending",
            "message": "Music analysis task queued successfully",
            "estimated_duration": "1-3 minutes"
        }
        
    except Exception as e:
        logger.error(f"Music analysis request failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create music analysis task"
        )


@router.post("/recommend", response_model=Dict[str, Any])
async def get_ai_recommendations(
    request: RecommendationRequest,
    user: dict = Depends(get_current_user)
):
    """Get AI-powered recommendations"""
    try:
        # Get user's content history
        async with database_manager.get_postgres_session() as session:
            result = await session.execute("""
                SELECT file_id, metadata, upload_timestamp
                FROM uploaded_files
                WHERE user_id = %s AND content_type = 'audio'
                ORDER BY upload_timestamp DESC
                LIMIT 50
            """, (user['user_id'],))
            
            user_content = [
                {
                    "file_id": row[0],
                    "metadata": row[1],
                    "upload_timestamp": row[2]
                }
                for row in result.fetchall()
            ]
        
        # Generate recommendations
        recommendations = await recommendation_engine.generate_recommendations(
            user['user_id'], request, user_content
        )
        
        # Store recommendation session
        session_id = str(uuid.uuid4())
        async with database_manager.get_postgres_session() as session:
            await session.execute("""
                INSERT INTO recommendation_sessions (session_id, user_id, request_data,
                                                   recommendations, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                session_id, user['user_id'], request.dict(),
                recommendations, datetime.utcnow()
            ))
            await session.commit()
        
        logger.info(f"AI recommendations generated: {session_id} for user {user['user_id']}")
        
        return {
            "session_id": session_id,
            "recommendation_type": request.recommendation_type,
            "recommendations": recommendations['items'],
            "confidence_score": recommendations['confidence'],
            "personalization_score": recommendations['personalization'],
            "explanation": recommendations['explanation'],
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "algorithm_version": recommendations['algorithm_version'],
                "data_sources": recommendations['data_sources']
            }
        }
        
    except Exception as e:
        logger.error(f"AI recommendations failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate AI recommendations"
        )


@router.post("/generate/content", response_model=Dict[str, str])
async def generate_content(
    request: ContentGenerationRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user)
):
    """Generate AI content (lyrics, descriptions, etc.)"""
    try:
        task_id = str(uuid.uuid4())
        
        # Create task record
        async with database_manager.get_postgres_session() as session:
            await session.execute("""
                INSERT INTO ai_agent_tasks (task_id, user_id, agent_type, request_data,
                                          status, progress, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                task_id, user['user_id'], AgentType.CONTENT_GENERATOR.value,
                request.dict(), TaskStatus.PENDING.value, 0.0,
                datetime.utcnow(), datetime.utcnow()
            ))
            await session.commit()
        
        # Schedule content generation task
        background_tasks.add_task(
            _process_content_generation, task_id, request, user
        )
        
        logger.info(f"Content generation task created: {task_id} by user {user['user_id']}")
        
        return {
            "task_id": task_id,
            "status": "pending",
            "content_type": request.content_type,
            "message": "Content generation task queued successfully",
            "estimated_duration": "30 seconds - 2 minutes"
        }
        
    except Exception as e:
        logger.error(f"Content generation request failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create content generation task"
        )


@router.post("/transfer/style", response_model=Dict[str, str])
async def transfer_style(
    request: StyleTransferRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user)
):
    """Apply style transfer to content"""
    try:
        # Verify source content ownership
        async with database_manager.get_postgres_session() as session:
            result = await session.execute("""
                SELECT file_path, content_type
                FROM uploaded_files
                WHERE file_id = %s AND user_id = %s
            """, (request.source_content_id, user['user_id']))
            
            source_info = result.fetchone()
            if not source_info:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Source content not found or access denied"
                )
            
            # Verify style reference if provided
            if request.style_reference_id:
                result = await session.execute("""
                    SELECT file_path FROM uploaded_files
                    WHERE file_id = %s AND user_id = %s
                """, (request.style_reference_id, user['user_id']))
                
                if not result.fetchone():
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Style reference not found or access denied"
                    )
        
        task_id = str(uuid.uuid4())
        
        # Create task record
        async with database_manager.get_postgres_session() as session:
            await session.execute("""
                INSERT INTO ai_agent_tasks (task_id, user_id, agent_type, request_data,
                                          status, progress, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                task_id, user['user_id'], AgentType.STYLE_TRANSFER.value,
                request.dict(), TaskStatus.PENDING.value, 0.0,
                datetime.utcnow(), datetime.utcnow()
            ))
            await session.commit()
        
        # Schedule style transfer task
        background_tasks.add_task(
            _process_style_transfer, task_id, request, source_info, user
        )
        
        logger.info(f"Style transfer task created: {task_id} by user {user['user_id']}")
        
        return {
            "task_id": task_id,
            "status": "pending",
            "source_content_id": request.source_content_id,
            "target_style": request.target_style,
            "message": "Style transfer task queued successfully",
            "estimated_duration": "3-8 minutes"
        }
        
    except Exception as e:
        logger.error(f"Style transfer request failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create style transfer task"
        )


@router.get("/tasks/{task_id}", response_model=AIAgentTask)
async def get_task_status(
    task_id: str,
    user: dict = Depends(get_current_user)
):
    """Get AI agent task status"""
    try:
        async with database_manager.get_postgres_session() as session:
            result = await session.execute("""
                SELECT task_id, agent_type, request_data, status, progress,
                       result, error_message, created_at, updated_at, estimated_completion
                FROM ai_agent_tasks
                WHERE task_id = %s AND user_id = %s
            """, (task_id, user['user_id']))
            
            task_info = result.fetchone()
            if not task_info:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Task not found or access denied"
                )
        
        return AIAgentTask(
            task_id=task_info[0],
            agent_type=AgentType(task_info[1]),
            request_data=task_info[2],
            status=TaskStatus(task_info[3]),
            progress=task_info[4],
            result=task_info[5],
            error_message=task_info[6],
            created_at=task_info[7],
            updated_at=task_info[8],
            estimated_completion=task_info[9]
        )
        
    except Exception as e:
        logger.error(f"Get task status failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get task status"
        )


@router.get("/tasks", response_model=List[AIAgentTask])
async def get_user_tasks(
    agent_type: Optional[AgentType] = None,
    status: Optional[TaskStatus] = None,
    limit: int = Field(default=20, ge=1, le=100),
    user: dict = Depends(get_current_user)
):
    """Get user's AI agent tasks"""
    try:
        query = """
            SELECT task_id, agent_type, request_data, status, progress,
                   result, error_message, created_at, updated_at, estimated_completion
            FROM ai_agent_tasks
            WHERE user_id = %s
        """
        params = [user['user_id']]
        
        if agent_type:
            query += " AND agent_type = %s"
            params.append(agent_type.value)
        
        if status:
            query += " AND status = %s"
            params.append(status.value)
            
        query += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)
        
        async with database_manager.get_postgres_session() as session:
            result = await session.execute(query, params)
            tasks = result.fetchall()
        
        task_list = []
        for task in tasks:
            task_list.append(AIAgentTask(
                task_id=task[0],
                agent_type=AgentType(task[1]),
                request_data=task[2],
                status=TaskStatus(task[3]),
                progress=task[4],
                result=task[5],
                error_message=task[6],
                created_at=task[7],
                updated_at=task[8],
                estimated_completion=task[9]
            ))
        
        return task_list
        
    except Exception as e:
        logger.error(f"Get user tasks failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user tasks"
        )


@router.delete("/tasks/{task_id}")
async def cancel_task(
    task_id: str,
    user: dict = Depends(get_current_user)
):
    """Cancel an AI agent task"""
    try:
        async with database_manager.get_postgres_session() as session:
            # Check if task exists and belongs to user
            result = await session.execute("""
                SELECT status FROM ai_agent_tasks
                WHERE task_id = %s AND user_id = %s
            """, (task_id, user['user_id']))
            
            task_status = result.fetchone()
            if not task_status:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Task not found or access denied"
                )
            
            if task_status[0] in [TaskStatus.COMPLETED.value, TaskStatus.FAILED.value, TaskStatus.CANCELLED.value]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Task cannot be cancelled in current status"
                )
            
            # Cancel task
            await session.execute("""
                UPDATE ai_agent_tasks 
                SET status = %s, updated_at = %s
                WHERE task_id = %s
            """, (TaskStatus.CANCELLED.value, datetime.utcnow(), task_id))
            await session.commit()
        
        logger.info(f"AI agent task cancelled: {task_id}")
        
        return {"message": "Task cancelled successfully"}
        
    except Exception as e:
        logger.error(f"Cancel task failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel task"
        )


@router.get("/capabilities", response_model=Dict[str, Any])
async def get_ai_capabilities():
    """Get available AI agent capabilities and models"""
    try:
        capabilities = {
            "music_composition": {
                "supported_genres": [
                    "pop", "rock", "hip-hop", "electronic", "classical", "jazz",
                    "folk", "country", "r&b", "indie", "ambient", "experimental"
                ],
                "supported_instruments": [
                    "piano", "guitar", "bass", "drums", "strings", "brass",
                    "woodwinds", "synthesizer", "vocals", "percussion"
                ],
                "duration_range": {"min": 10, "max": 600},
                "tempo_range": {"min": 60, "max": 200},
                "model_version": "v2.1",
                "quality_levels": ["demo", "production", "mastered"]
            },
            "music_analysis": {
                "analysis_types": [
                    "full", "structure", "harmony", "rhythm", "melody", "style"
                ],
                "supported_formats": [".mp3", ".wav", ".flac", ".m4a"],
                "max_file_size": "100MB",
                "features_extracted": [
                    "tempo", "key", "mood", "genre", "instruments", "structure",
                    "dynamics", "harmonic_content", "rhythmic_patterns"
                ],
                "accuracy_score": 0.94
            },
            "content_generation": {
                "content_types": [
                    "lyrics", "description", "social_post", "blog_article", "press_release"
                ],
                "supported_styles": [
                    "professional", "casual", "creative", "technical", "promotional"
                ],
                "supported_tones": [
                    "neutral", "enthusiastic", "serious", "playful", "inspirational"
                ],
                "length_range": {"min": 10, "max": 5000},
                "languages": ["english", "french", "german", "spanish"]
            },
            "style_transfer": {
                "supported_content_types": ["audio", "image", "text"],
                "transfer_strength_range": {"min": 0.1, "max": 1.0},
                "preserve_structure_options": [True, False],
                "style_categories": [
                    "artistic", "musical", "photographic", "literary"
                ]
            },
            "recommendations": {
                "recommendation_types": [
                    "tracks", "artists", "genres", "collaborators", "tools"
                ],
                "personalization_factors": [
                    "listening_history", "creation_patterns", "collaboration_preferences",
                    "genre_preferences", "skill_level", "goals"
                ],
                "max_recommendations": 50,
                "real_time_updates": True
            }
        }
        
        return {
            "capabilities": capabilities,
            "system_info": {
                "ai_engine_version": "3.2.1",
                "last_updated": datetime.utcnow().isoformat(),
                "supported_languages": ["en", "fr", "de", "es"],
                "processing_capacity": "high",
                "average_response_time": "2.3 seconds"
            }
        }
        
    except Exception as e:
        logger.error(f"Get AI capabilities failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get AI capabilities"
        )


# Background processing functions
async def _process_music_composition(task_id: str, request: MusicCompositionRequest, user: dict):
    """Process music composition task"""
    try:
        # Update status to processing
        await _update_task_status(task_id, TaskStatus.PROCESSING, 10.0, "Initializing composition")
        
        # Generate composition using AI
        composition_result = await composition_engine.compose_music(
            genre=request.genre,
            mood=request.mood,
            tempo=request.tempo,
            key=request.key,
            duration=request.duration_seconds,
            instruments=request.instruments,
            creativity_level=request.creativity_level.value,
            reference_tracks=request.reference_tracks,
            custom_prompts=request.custom_prompts
        )
        
        await _update_task_status(task_id, TaskStatus.PROCESSING, 70.0, "Generating audio")
        
        # Render composition to audio file
        audio_file_path = await composition_engine.render_composition(
            composition_result, task_id
        )
        
        await _update_task_status(task_id, TaskStatus.PROCESSING, 90.0, "Finalizing")
        
        # Store result
        result = {
            "composition_id": str(uuid.uuid4()),
            "audio_file_path": audio_file_path,
            "composition_data": composition_result,
            "metadata": {
                "title": request.title or f"AI Composition {datetime.utcnow().strftime('%Y%m%d_%H%M')}",
                "genre": request.genre,
                "mood": request.mood,
                "duration": request.duration_seconds,
                "instruments": request.instruments
            }
        }
        
        await _update_task_status(task_id, TaskStatus.COMPLETED, 100.0, "Completed", result)
        
        logger.info(f"Music composition completed: {task_id}")
        
    except Exception as e:
        logger.error(f"Music composition failed: {e}")
        await _update_task_status(task_id, TaskStatus.FAILED, 0.0, str(e))


async def _process_music_analysis(task_id: str, request: MusicAnalysisRequest, 
                                  file_path: str, user: dict):
    """Process music analysis task"""
    try:
        await _update_task_status(task_id, TaskStatus.PROCESSING, 20.0, "Loading audio file")
        
        # Analyze music using AI
        analysis_result = await analysis_engine.analyze_music(
            file_path, request.analysis_type
        )
        
        await _update_task_status(task_id, TaskStatus.PROCESSING, 70.0, "Generating insights")
        
        # Generate recommendations if requested
        recommendations = []
        if request.include_recommendations:
            recommendations = await analysis_engine.generate_improvement_recommendations(
                analysis_result
            )
        
        await _update_task_status(task_id, TaskStatus.PROCESSING, 90.0, "Finalizing analysis")
        
        # Compare to library if requested
        library_matches = []
        if request.compare_to_library:
            library_matches = await analysis_engine.compare_to_library(
                analysis_result, user['user_id']
            )
        
        result = {
            "analysis_id": str(uuid.uuid4()),
            "analysis_type": request.analysis_type,
            "analysis_results": analysis_result,
            "recommendations": recommendations,
            "library_matches": library_matches,
            "confidence_score": analysis_result.get('confidence', 0.95),
            "processed_at": datetime.utcnow().isoformat()
        }
        
        await _update_task_status(task_id, TaskStatus.COMPLETED, 100.0, "Analysis completed", result)
        
        logger.info(f"Music analysis completed: {task_id}")
        
    except Exception as e:
        logger.error(f"Music analysis failed: {e}")
        await _update_task_status(task_id, TaskStatus.FAILED, 0.0, str(e))


async def _process_content_generation(task_id: str, request: ContentGenerationRequest, user: dict):
    """Process content generation task"""
    try:
        await _update_task_status(task_id, TaskStatus.PROCESSING, 30.0, "Generating content")
        
        # Generate content using AI
        generated_content = await content_generator.generate_content(
            content_type=request.content_type,
            topic=request.topic,
            style=request.style,
            tone=request.tone,
            target_length=request.target_length,
            keywords=request.keywords,
            target_audience=request.target_audience,
            platform=request.platform,
            reference_content=request.reference_content
        )
        
        await _update_task_status(task_id, TaskStatus.PROCESSING, 80.0, "Refining content")
        
        # Post-process and refine content
        refined_content = await content_generator.refine_content(
            generated_content, request.style, request.tone
        )
        
        result = {
            "content_id": str(uuid.uuid4()),
            "content_type": request.content_type,
            "generated_content": refined_content,
            "metadata": {
                "topic": request.topic,
                "style": request.style,
                "tone": request.tone,
                "word_count": len(refined_content.split()),
                "character_count": len(refined_content),
                "keywords_used": request.keywords,
                "generation_model": "GPT-4-Turbo",
                "quality_score": generated_content.get('quality_score', 0.92)
            }
        }
        
        await _update_task_status(task_id, TaskStatus.COMPLETED, 100.0, "Content generated", result)
        
        logger.info(f"Content generation completed: {task_id}")
        
    except Exception as e:
        logger.error(f"Content generation failed: {e}")
        await _update_task_status(task_id, TaskStatus.FAILED, 0.0, str(e))


async def _process_style_transfer(task_id: str, request: StyleTransferRequest, 
                                  source_info: tuple, user: dict):
    """Process style transfer task"""
    try:
        await _update_task_status(task_id, TaskStatus.PROCESSING, 20.0, "Loading source content")
        
        source_path, content_type = source_info
        
        # Apply style transfer using AI
        transfer_result = await style_transfer_engine.transfer_style(
            source_path=source_path,
            target_style=request.target_style,
            style_reference_id=request.style_reference_id,
            transfer_strength=request.transfer_strength,
            preserve_structure=request.preserve_structure,
            custom_parameters=request.custom_parameters
        )
        
        await _update_task_status(task_id, TaskStatus.PROCESSING, 80.0, "Applying style transfer")
        
        # Generate output file
        output_path = await style_transfer_engine.render_styled_content(
            transfer_result, task_id, content_type
        )
        
        result = {
            "transfer_id": str(uuid.uuid4()),
            "source_content_id": request.source_content_id,
            "target_style": request.target_style,
            "output_file_path": output_path,
            "transfer_data": transfer_result,
            "metadata": {
                "transfer_strength": request.transfer_strength,
                "preserve_structure": request.preserve_structure,
                "quality_metrics": transfer_result.get('quality_metrics', {}),
                "processing_time": transfer_result.get('processing_time', 0)
            }
        }
        
        await _update_task_status(task_id, TaskStatus.COMPLETED, 100.0, "Style transfer completed", result)
        
        logger.info(f"Style transfer completed: {task_id}")
        
    except Exception as e:
        logger.error(f"Style transfer failed: {e}")
        await _update_task_status(task_id, TaskStatus.FAILED, 0.0, str(e))


async def _update_task_status(task_id: str, status: TaskStatus, progress: float, 
                             step: str, result: Optional[Dict[str, Any]] = None):
    """Update AI agent task status"""
    try:
        async with database_manager.get_postgres_session() as session:
            if result:
                await session.execute("""
                    UPDATE ai_agent_tasks 
                    SET status = %s, progress = %s, processing_step = %s, 
                        result = %s, updated_at = %s
                    WHERE task_id = %s
                """, (status.value, progress, step, result, datetime.utcnow(), task_id))
            else:
                await session.execute("""
                    UPDATE ai_agent_tasks 
                    SET status = %s, progress = %s, processing_step = %s, 
                        updated_at = %s
                    WHERE task_id = %s
                """, (status.value, progress, step, datetime.utcnow(), task_id))
            await session.commit()
    except Exception as e:
        logger.error(f"Failed to update task status: {e}")