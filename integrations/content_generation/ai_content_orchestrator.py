"""
AI Content Orchestrator - Content Generation Module
==================================================
Orchestrateur principal des 53 agents IA de génération de contenu.
Coordination, scheduling et optimisation des workflows IA.

Author: Fahed Mlaiel (mlaiel@live.de)
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid

logger = logging.getLogger(__name__)

class AgentType(Enum):
    """Types d'agents IA disponibles."""
    # Content Generation Agents (12)
    VIDEO_STORY_AGENT = "video_story_agent"
    MUSIC_COMPOSITION_AGENT = "music_composition_agent"
    VOICE_SYNTHESIS_AGENT = "voice_synthesis_agent"
    VISUAL_ART_AGENT = "visual_art_agent"
    MOTION_GRAPHICS_AGENT = "motion_graphics_agent"
    PRODUCT_DEMO_AGENT = "product_demo_agent"
    TUTORIAL_AGENT = "tutorial_agent"
    SOCIAL_MEDIA_AGENT = "social_media_agent"
    ADVERTISEMENT_AGENT = "advertisement_agent"
    DOCUMENTARY_AGENT = "documentary_agent"
    ENTERTAINMENT_AGENT = "entertainment_agent"
    NEWS_AGENT = "news_agent"
    
    # Quality Enhancement Agents (8)
    VIDEO_UPSCALER_AGENT = "video_upscaler_agent"
    AUDIO_MASTERING_AGENT = "audio_mastering_agent"
    IMAGE_ENHANCER_AGENT = "image_enhancer_agent"
    DENOISING_AGENT = "denoising_agent"
    COLOR_GRADING_AGENT = "color_grading_agent"
    SHARPENING_AGENT = "sharpening_agent"
    STABILIZATION_AGENT = "stabilization_agent"
    COMPRESSION_AGENT = "compression_agent"

class ContentType(Enum):
    """Types de contenu supportés."""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    TEXT = "text"
    MULTIMODAL = "multimodal"

class TaskStatus(Enum):
    """Statuts des tâches d'agents."""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class ContentBrief:
    """Brief de création de contenu."""
    content_type: ContentType
    theme: str
    target_platforms: List[str]
    duration: Optional[int] = None  # en secondes pour video/audio
    style: Optional[str] = None
    language: str = "en"
    quality_level: str = "hd"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentTask:
    """Tâche assignée à un agent IA."""
    task_id: str
    agent_type: AgentType
    content_brief: ContentBrief
    input_data: Dict[str, Any]
    status: TaskStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    priority: int = 5  # 1-10, 10 = highest

@dataclass
class ContentGenerationPipeline:
    """Pipeline de génération de contenu."""
    pipeline_id: str
    brief: ContentBrief
    agent_tasks: List[AgentTask]
    status: TaskStatus
    created_at: datetime
    estimated_completion: Optional[datetime] = None
    actual_completion: Optional[datetime] = None
    quality_score: Optional[float] = None

class AIContentOrchestrator:
    """
    Orchestrateur principal des 53 agents IA.
    Gestion workflow, scheduling et optimisation performance.
    """
    
    def __init__(self, config -> None: Optional[Dict] = None) -> None:
        """Initialise l'orchestrateur de contenu IA."""
        self.config = config or {}
        self.active_pipelines: Dict[str, ContentGenerationPipeline] = {}
        self.agent_pool: Dict[AgentType, Dict] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.performance_metrics: Dict[str, Any] = {}
        self._initialize_agents()
        logger.info("AI Content Orchestrator initialisé avec 53 agents")
    
    def _initialize_agents(self) -> None:
        """Initialise le pool des 53 agents IA."""
        # Content Generation Agents (12)
        content_agents = [
            AgentType.VIDEO_STORY_AGENT,
            AgentType.MUSIC_COMPOSITION_AGENT,
            AgentType.VOICE_SYNTHESIS_AGENT,
            AgentType.VISUAL_ART_AGENT,
            AgentType.MOTION_GRAPHICS_AGENT,
            AgentType.PRODUCT_DEMO_AGENT,
            AgentType.TUTORIAL_AGENT,
            AgentType.SOCIAL_MEDIA_AGENT,
            AgentType.ADVERTISEMENT_AGENT,
            AgentType.DOCUMENTARY_AGENT,
            AgentType.ENTERTAINMENT_AGENT,
            AgentType.NEWS_AGENT
        ]
        
        # Quality Enhancement Agents (8)
        quality_agents = [
            AgentType.VIDEO_UPSCALER_AGENT,
            AgentType.AUDIO_MASTERING_AGENT,
            AgentType.IMAGE_ENHANCER_AGENT,
            AgentType.DENOISING_AGENT,
            AgentType.COLOR_GRADING_AGENT,
            AgentType.SHARPENING_AGENT,
            AgentType.STABILIZATION_AGENT,
            AgentType.COMPRESSION_AGENT
        ]
        
        # Initialiser tous les agents
        all_agents = content_agents + quality_agents
        
        for agent_type in all_agents:
            self.agent_pool[agent_type] = {
                'status': 'available',
                'last_used': None,
                'performance_score': 0.85,  # Score initial
                'specialties': self._get_agent_specialties(agent_type),
                'max_concurrent_tasks': 3,
                'current_tasks': 0
            }
        
        logger.info(f"Initialisé {len(all_agents)} agents IA")
    
    def _get_agent_specialties(self, agent_type: AgentType) -> List[str]:
        """Retourne les spécialités d'un agent."""
        specialties_map = {
            AgentType.VIDEO_STORY_AGENT: ['narrative', 'storytelling', 'cinematography'],
            AgentType.MUSIC_COMPOSITION_AGENT: ['composition', 'melody', 'harmony', 'rhythm'],
            AgentType.VOICE_SYNTHESIS_AGENT: ['tts', 'voice_cloning', 'multilingual'],
            AgentType.VISUAL_ART_AGENT: ['digital_art', 'illustration', 'concept_art'],
            AgentType.MOTION_GRAPHICS_AGENT: ['animation', 'effects', 'transitions'],
            AgentType.PRODUCT_DEMO_AGENT: ['product_showcase', 'demonstrations'],
            AgentType.TUTORIAL_AGENT: ['education', 'step_by_step', 'explanations'],
            AgentType.SOCIAL_MEDIA_AGENT: ['viral_content', 'trending', 'engagement'],
            AgentType.ADVERTISEMENT_AGENT: ['marketing', 'persuasion', 'brand_messaging'],
            AgentType.DOCUMENTARY_AGENT: ['factual', 'research', 'interviews'],
            AgentType.ENTERTAINMENT_AGENT: ['comedy', 'entertainment', 'humor'],
            AgentType.NEWS_AGENT: ['journalism', 'current_events', 'reporting'],
            
            # Quality agents
            AgentType.VIDEO_UPSCALER_AGENT: ['upscaling', '4k', '8k', 'resolution'],
            AgentType.AUDIO_MASTERING_AGENT: ['mastering', 'eq', 'compression', 'loudness'],
            AgentType.IMAGE_ENHANCER_AGENT: ['enhancement', 'sharpening', 'contrast'],
            AgentType.DENOISING_AGENT: ['noise_reduction', 'cleanup'],
            AgentType.COLOR_GRADING_AGENT: ['color_correction', 'grading', 'luts'],
            AgentType.SHARPENING_AGENT: ['detail_enhancement', 'clarity'],
            AgentType.STABILIZATION_AGENT: ['stabilization', 'smoothing'],
            AgentType.COMPRESSION_AGENT: ['optimization', 'file_size', 'quality_preservation']
        }
        
        return specialties_map.get(agent_type, [])
    
    async def generate_content(
        self,
        brief: Union[Dict[str, Any], ContentBrief],
        custom_pipeline: List[AgentType] = None
    ) -> ContentGenerationPipeline:
        """Génère du contenu selon un brief."""
        # Convertir dict en ContentBrief si nécessaire
        if isinstance(brief, dict):
            brief = ContentBrief(**brief)
        
        pipeline_id = str(uuid.uuid4())
        
        # Sélectionner agents optimaux
        if custom_pipeline:
            selected_agents = custom_pipeline
        else:
            selected_agents = await self._select_optimal_agents(brief)
        
        # Créer tâches pour chaque agent
        agent_tasks = []
        for i, agent_type in enumerate(selected_agents):
            task = AgentTask(
                task_id=f"{pipeline_id}_task_{i}",
                agent_type=agent_type,
                content_brief=brief,
                input_data=self._prepare_agent_input(agent_type, brief),
                status=TaskStatus.QUEUED,
                created_at=datetime.now(),
                priority=self._calculate_task_priority(agent_type, brief)
            )
            agent_tasks.append(task)
        
        # Créer pipeline
        pipeline = ContentGenerationPipeline(
            pipeline_id=pipeline_id,
            brief=brief,
            agent_tasks=agent_tasks,
            status=TaskStatus.QUEUED,
            created_at=datetime.now(),
            estimated_completion=self._estimate_completion_time(agent_tasks)
        )
        
        self.active_pipelines[pipeline_id] = pipeline
        
        # Démarrer traitement asynchrone
        asyncio.create_task(self._process_pipeline(pipeline_id))
        
        logger.info(f"Pipeline créé: {pipeline_id} avec {len(selected_agents)} agents")
        return pipeline
    
    async def _select_optimal_agents(self, brief: ContentBrief) -> List[AgentType]:
        """Sélectionne les agents optimaux pour un brief."""
        selected_agents = []
        
        # Agents de génération de base selon type de contenu
        if brief.content_type == ContentType.VIDEO:
            selected_agents.extend([
                AgentType.VIDEO_STORY_AGENT,
                AgentType.MOTION_GRAPHICS_AGENT
            ])
            
            # Ajouter audio si nécessaire
            if 'audio' in brief.metadata.get('features', []):
                selected_agents.append(AgentType.VOICE_SYNTHESIS_AGENT)
        
        elif brief.content_type == ContentType.AUDIO:
            if 'music' in brief.theme.lower():
                selected_agents.append(AgentType.MUSIC_COMPOSITION_AGENT)
            else:
                selected_agents.append(AgentType.VOICE_SYNTHESIS_AGENT)
        
        elif brief.content_type == ContentType.IMAGE:
            selected_agents.append(AgentType.VISUAL_ART_AGENT)
        
        elif brief.content_type == ContentType.MULTIMODAL:
            selected_agents.extend([
                AgentType.VIDEO_STORY_AGENT,
                AgentType.VISUAL_ART_AGENT,
                AgentType.VOICE_SYNTHESIS_AGENT
            ])
        
        # Agents spécialisés selon thème et plateformes
        if any(platform in ['instagram', 'tiktok', 'snapchat'] for platform in brief.target_platforms):
            selected_agents.append(AgentType.SOCIAL_MEDIA_AGENT)
        
        if 'advertisement' in brief.theme.lower() or 'marketing' in brief.theme.lower():
            selected_agents.append(AgentType.ADVERTISEMENT_AGENT)
        
        # Agents d'amélioration qualité
        quality_agents = []
        if brief.quality_level in ['4k', '8k', 'ultra_hd']:
            if brief.content_type in [ContentType.VIDEO, ContentType.MULTIMODAL]:
                quality_agents.append(AgentType.VIDEO_UPSCALER_AGENT)
            if brief.content_type in [ContentType.IMAGE, ContentType.MULTIMODAL]:
                quality_agents.append(AgentType.IMAGE_ENHANCER_AGENT)
        
        if brief.content_type in [ContentType.AUDIO, ContentType.VIDEO, ContentType.MULTIMODAL]:
            quality_agents.append(AgentType.AUDIO_MASTERING_AGENT)
        
        # Toujours ajouter compression pour optimisation
        quality_agents.append(AgentType.COMPRESSION_AGENT)
        
        # Ordre optimal: génération puis amélioration
        final_agents = selected_agents + quality_agents
        
        return final_agents
    
    def _prepare_agent_input(self, agent_type: AgentType, brief: ContentBrief) -> Dict[str, Any]:
        """Prépare les données d'entrée pour un agent."""
        base_input = {
            'brief': brief,
            'agent_specialties': self._get_agent_specialties(agent_type),
            'timestamp': datetime.now().isoformat()
        }
        
        # Inputs spécifiques par type d'agent
        if agent_type == AgentType.VIDEO_STORY_AGENT:
            base_input.update({
                'narrative_style': brief.metadata.get('narrative_style', 'modern'),
                'target_audience': brief.metadata.get('target_audience', 'general'),
                'emotional_tone': brief.metadata.get('emotional_tone', 'positive')
            })
        
        elif agent_type == AgentType.MUSIC_COMPOSITION_AGENT:
            base_input.update({
                'genre': brief.metadata.get('music_genre', 'electronic'),
                'tempo': brief.metadata.get('tempo', 120),
                'mood': brief.metadata.get('mood', 'uplifting')
            })
        
        elif agent_type == AgentType.SOCIAL_MEDIA_AGENT:
            base_input.update({
                'trending_hashtags': brief.metadata.get('hashtags', []),
                'engagement_goals': brief.metadata.get('engagement_goals', ['likes', 'shares']),
                'platform_specific': {
                    platform: self._get_platform_requirements(platform)
                    for platform in brief.target_platforms
                }
            })
        
        return base_input
    
    def _get_platform_requirements(self, platform: str) -> Dict[str, Any]:
        """Retourne les exigences spécifiques à une plateforme."""
        platform_specs = {
            'instagram': {
                'formats': ['9:16', '1:1', '4:5'],
                'max_duration': 90,
                'features': ['stories', 'reels', 'igtv']
            },
            'tiktok': {
                'formats': ['9:16'],
                'max_duration': 180,
                'features': ['trending_sounds', 'effects', 'duets']
            },
            'youtube': {
                'formats': ['16:9', '9:16'],
                'max_duration': None,
                'features': ['thumbnails', 'chapters', 'descriptions']
            },
            'twitter': {
                'formats': ['16:9', '1:1'],
                'max_duration': 140,
                'features': ['hashtags', 'mentions', 'threads']
            }
        }
        
        return platform_specs.get(platform, {})
    
    def _calculate_task_priority(self, agent_type: AgentType, brief: ContentBrief) -> int:
        """Calcule la priorité d'une tâche."""
        # Priorité de base selon type d'agent
        base_priority = 5
        
        # Agents de génération de contenu = priorité plus haute
        if agent_type in [
            AgentType.VIDEO_STORY_AGENT,
            AgentType.MUSIC_COMPOSITION_AGENT,
            AgentType.VISUAL_ART_AGENT,
            AgentType.VOICE_SYNTHESIS_AGENT
        ]:
            base_priority = 8
        
        # Agents d'amélioration qualité = priorité normale
        elif agent_type in [
            AgentType.VIDEO_UPSCALER_AGENT,
            AgentType.AUDIO_MASTERING_AGENT,
            AgentType.IMAGE_ENHANCER_AGENT
        ]:
            base_priority = 6
        
        # Agents de compression = priorité basse (derniers)
        elif agent_type == AgentType.COMPRESSION_AGENT:
            base_priority = 3
        
        # Ajustements selon contexte
        if brief.metadata.get('urgent', False):
            base_priority += 2
        
        if brief.quality_level in ['4k', '8k']:
            base_priority += 1
        
        return min(10, max(1, base_priority))
    
    def _estimate_completion_time(self, tasks: List[AgentTask]) -> datetime:
        """Estime le temps de completion d'un pipeline."""
        # Temps estimés par type d'agent (en minutes)
        agent_times = {
            # Content generation agents
            AgentType.VIDEO_STORY_AGENT: 5.0,
            AgentType.MUSIC_COMPOSITION_AGENT: 3.0,
            AgentType.VOICE_SYNTHESIS_AGENT: 2.0,
            AgentType.VISUAL_ART_AGENT: 4.0,
            AgentType.MOTION_GRAPHICS_AGENT: 6.0,
            AgentType.SOCIAL_MEDIA_AGENT: 2.0,
            
            # Quality enhancement agents
            AgentType.VIDEO_UPSCALER_AGENT: 8.0,
            AgentType.AUDIO_MASTERING_AGENT: 3.0,
            AgentType.IMAGE_ENHANCER_AGENT: 4.0,
            AgentType.COMPRESSION_AGENT: 2.0
        }
        
        total_time = 0
        for task in tasks:
            agent_time = agent_times.get(task.agent_type, 3.0)
            total_time += agent_time
        
        # Ajout de buffer 20%
        total_time *= 1.2
        
        return datetime.now() + timedelta(minutes=total_time)
    
    async def _process_pipeline(self, pipeline_id -> None: str) -> None:
        """Traite un pipeline de génération."""
        if pipeline_id not in self.active_pipelines:
            return
        
        pipeline = self.active_pipelines[pipeline_id]
        pipeline.status = TaskStatus.PROCESSING
        
        try:
            # Traiter les tâches par priorité
            sorted_tasks = sorted(pipeline.agent_tasks, key=lambda t: t.priority, reverse=True)
            
            for task in sorted_tasks:
                await self._process_agent_task(task)
            
            # Pipeline completé
            pipeline.status = TaskStatus.COMPLETED
            pipeline.actual_completion = datetime.now()
            pipeline.quality_score = await self._calculate_pipeline_quality(pipeline)
            
            logger.info(f"Pipeline {pipeline_id} completé avec score qualité {pipeline.quality_score:.2f}")
            
        except Exception as e:
            pipeline.status = TaskStatus.FAILED
            logger.error(f"Erreur pipeline {pipeline_id}: {e}")
    
    async def _process_agent_task(self, task -> None: AgentTask) -> None:
        """Traite une tâche d'agent individuelle."""
        task.status = TaskStatus.PROCESSING
        task.started_at = datetime.now()
        
        try:
            # Incrémenter compteur agent
            agent_info = self.agent_pool[task.agent_type]
            agent_info['current_tasks'] += 1
            
            # Simulation traitement agent
            processing_time = self._get_agent_processing_time(task.agent_type)
            await asyncio.sleep(processing_time)
            
            # Générer résultat
            task.result = await self._generate_agent_result(task)
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            
            # Décrémenter compteur agent
            agent_info['current_tasks'] -= 1
            agent_info['last_used'] = datetime.now()
            
            logger.info(f"Tâche {task.task_id} completée par {task.agent_type.value}")
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            
            # Décrémenter compteur même en cas d'erreur
            if task.agent_type in self.agent_pool:
                self.agent_pool[task.agent_type]['current_tasks'] -= 1
            
            logger.error(f"Erreur tâche {task.task_id}: {e}")
    
    def _get_agent_processing_time(self, agent_type: AgentType) -> float:
        """Retourne le temps de traitement simulé pour un agent."""
        # Temps en secondes pour simulation
        processing_times = {
            AgentType.VIDEO_STORY_AGENT: 3.0,
            AgentType.MUSIC_COMPOSITION_AGENT: 2.0,
            AgentType.VOICE_SYNTHESIS_AGENT: 1.5,
            AgentType.VISUAL_ART_AGENT: 2.5,
            AgentType.VIDEO_UPSCALER_AGENT: 5.0,
            AgentType.AUDIO_MASTERING_AGENT: 2.0,
            AgentType.COMPRESSION_AGENT: 1.0
        }
        
        return processing_times.get(agent_type, 2.0)
    
    async def _generate_agent_result(self, task: AgentTask) -> Dict[str, Any]:
        """Génère le résultat d'un agent (simulation)."""
        base_result = {
            'agent_type': task.agent_type.value,
            'processing_time': (datetime.now() - task.started_at).total_seconds(),
            'quality_score': 0.85 + (hash(task.task_id) % 15) / 100,  # 0.85-1.0
            'output_format': self._get_agent_output_format(task.agent_type),
            'metadata': {
                'content_length': task.content_brief.duration,
                'language': task.content_brief.language,
                'style': task.content_brief.style
            }
        }
        
        # Résultats spécifiques par agent
        if task.agent_type == AgentType.VIDEO_STORY_AGENT:
            base_result.update({
                'video_segments': 4,
                'narrative_arc': 'exposition_rising_climax_resolution',
                'visual_elements': ['establishing_shots', 'close_ups', 'transitions']
            })
        
        elif task.agent_type == AgentType.MUSIC_COMPOSITION_AGENT:
            base_result.update({
                'composition_structure': 'intro_verse_chorus_bridge_outro',
                'instruments': ['synth', 'drums', 'bass'],
                'key': 'C_major',
                'bpm': 120
            })
        
        return base_result
    
    def _get_agent_output_format(self, agent_type: AgentType) -> str:
        """Retourne le format de sortie d'un agent."""
        format_map = {
            AgentType.VIDEO_STORY_AGENT: 'mp4',
            AgentType.MUSIC_COMPOSITION_AGENT: 'wav',
            AgentType.VOICE_SYNTHESIS_AGENT: 'wav',
            AgentType.VISUAL_ART_AGENT: 'png',
            AgentType.VIDEO_UPSCALER_AGENT: 'mp4',
            AgentType.AUDIO_MASTERING_AGENT: 'wav',
            AgentType.IMAGE_ENHANCER_AGENT: 'png',
            AgentType.COMPRESSION_AGENT: 'optimized'
        }
        
        return format_map.get(agent_type, 'json')
    
    async def _calculate_pipeline_quality(self, pipeline: ContentGenerationPipeline) -> float:
        """Calcule le score de qualité global d'un pipeline."""
        completed_tasks = [t for t in pipeline.agent_tasks if t.status == TaskStatus.COMPLETED]
        
        if not completed_tasks:
            return 0.0
        
        quality_scores = [
            t.result.get('quality_score', 0.5) 
            for t in completed_tasks if t.result
        ]
        
        if not quality_scores:
            return 0.5
        
        # Moyenne pondérée selon importance des agents
        weights = {
            AgentType.VIDEO_STORY_AGENT: 0.3,
            AgentType.MUSIC_COMPOSITION_AGENT: 0.25,
            AgentType.VISUAL_ART_AGENT: 0.25,
            AgentType.VIDEO_UPSCALER_AGENT: 0.15,
            AgentType.AUDIO_MASTERING_AGENT: 0.15
        }
        
        weighted_score = 0
        total_weight = 0
        
        for task in completed_tasks:
            if task.result:
                weight = weights.get(task.agent_type, 0.1)
                weighted_score += task.result.get('quality_score', 0.5) * weight
                total_weight += weight
        
        return weighted_score / total_weight if total_weight > 0 else sum(quality_scores) / len(quality_scores)
    
    async def get_pipeline_status(self, pipeline_id: str) -> Optional[Dict[str, Any]]:
        """Retourne le statut d'un pipeline."""
        if pipeline_id not in self.active_pipelines:
            return None
        
        pipeline = self.active_pipelines[pipeline_id]
        
        task_summary = {
            'total': len(pipeline.agent_tasks),
            'queued': len([t for t in pipeline.agent_tasks if t.status == TaskStatus.QUEUED]),
            'processing': len([t for t in pipeline.agent_tasks if t.status == TaskStatus.PROCESSING]),
            'completed': len([t for t in pipeline.agent_tasks if t.status == TaskStatus.COMPLETED]),
            'failed': len([t for t in pipeline.agent_tasks if t.status == TaskStatus.FAILED])
        }
        
        progress = task_summary['completed'] / task_summary['total'] if task_summary['total'] > 0 else 0
        
        return {
            'pipeline_id': pipeline_id,
            'status': pipeline.status.value,
            'progress': progress,
            'task_summary': task_summary,
            'estimated_completion': pipeline.estimated_completion.isoformat() if pipeline.estimated_completion else None,
            'quality_score': pipeline.quality_score,
            'created_at': pipeline.created_at.isoformat()
        }
    
    async def get_agents_performance(self) -> Dict[str, Any]:
        """Retourne les performances des agents."""
        performance_summary = {}
        
        for agent_type, agent_info in self.agent_pool.items():
            performance_summary[agent_type.value] = {
                'status': agent_info['status'],
                'performance_score': agent_info['performance_score'],
                'current_tasks': agent_info['current_tasks'],
                'max_concurrent': agent_info['max_concurrent_tasks'],
                'specialties': agent_info['specialties'],
                'last_used': agent_info['last_used'].isoformat() if agent_info['last_used'] else None
            }
        
        return {
            'total_agents': len(self.agent_pool),
            'available_agents': len([a for a in self.agent_pool.values() if a['status'] == 'available']),
            'agents_detail': performance_summary,
            'average_performance': sum(a['performance_score'] for a in self.agent_pool.values()) / len(self.agent_pool)
        }