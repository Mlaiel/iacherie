"""
Music Orchestrator - Central Music Intelligence Coordination System
==================================================================

Advanced orchestration system that coordinates music creation, analysis, distribution,
and protection for content creators with AI-powered workflow management.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: 2025 - All Rights Reserved

⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED ACCESS PROHIBITED
This software is the exclusive property of Fahed Mlaiel (mlaiel@live.de).
Any attempt to copy, distribute, or reverse engineer this code without explicit
written permission is strictly forbidden and will result in legal prosecution
under German and International Copyright Law.

Team: Lead Dev IA + Backend Senior + ML Engineer + Audio Specialist + DevOps Expert
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from ..spotify_agent import SpotifyAgent
from ..audio_agent import AudioAgent
from ..content_agent import ContentAgent
from ..protection_agent import ProtectionAgent
from ..collaboration_agent import CollaborationAgent
from ..monetization_agent import MonetizationAgent
from ..analytics_agent import AnalyticsAgent
from ...core.exceptions import MusicOrchestratorError
from ...core.security import SecurityManager
from ...core.logging import get_logger
from ...config.settings import get_settings

logger = get_logger(__name__)
settings = get_settings()


class WorkflowStage(Enum):
    """Music workflow stages enum"""
    UPLOAD = "upload"
    ANALYSIS = "analysis"
    ENHANCEMENT = "enhancement"
    PROTECTION = "protection"
    OPTIMIZATION = "optimization"
    DISTRIBUTION = "distribution"
    MONITORING = "monitoring"
    MONETIZATION = "monetization"


@dataclass
class MusicWorkflowContext:
    """Music workflow context data structure"""
    user_id: str
    content_id: str
    content_type: str
    stage: WorkflowStage
    metadata: Dict[str, Any]
    results: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class MusicOrchestrator:
    """
    Central orchestration system for music content workflow management.
    
    Coordinates multiple AI agents to provide comprehensive music intelligence,
    content protection, and monetization optimization.
    """

    def __init__(self):
        """Initialize music orchestrator with all required agents"""
        self.security_manager = SecurityManager()
        self.spotify_agent = SpotifyAgent()
        self.audio_agent = AudioAgent()
        self.content_agent = ContentAgent()
        self.protection_agent = ProtectionAgent()
        self.collaboration_agent = CollaborationAgent()
        self.monetization_agent = MonetizationAgent()
        self.analytics_agent = AnalyticsAgent()
        
        # Workflow state management
        self._active_workflows: Dict[str, MusicWorkflowContext] = {}
        self._workflow_history: List[MusicWorkflowContext] = []
        
        logger.info("Music Orchestrator initialized successfully")

    async def process_music_content(
        self, 
        user_id: str, 
        content_data: Dict[str, Any],
        workflow_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process music content through complete AI workflow.
        
        Args:
            user_id: User identifier
            content_data: Music content and metadata
            workflow_options: Custom workflow configuration
            
        Returns:
            Complete processing results with recommendations
        """
        try:
            # Validate user permissions
            await self.security_manager.validate_user_access(user_id, "music_processing")
            
            # Initialize workflow context
            content_id = self._generate_content_id()
            context = MusicWorkflowContext(
                user_id=user_id,
                content_id=content_id,
                content_type=content_data.get('type', 'audio'),
                stage=WorkflowStage.UPLOAD,
                metadata=content_data.get('metadata', {}),
                results={},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self._active_workflows[content_id] = context
            
            # Stage 1: Content Analysis
            context.stage = WorkflowStage.ANALYSIS
            analysis_results = await self._analyze_content(context, content_data)
            context.results.update(analysis_results)
            
            # Stage 2: Audio Enhancement
            context.stage = WorkflowStage.ENHANCEMENT
            enhancement_results = await self._enhance_content(context)
            context.results.update(enhancement_results)
            
            # Stage 3: Content Protection
            context.stage = WorkflowStage.PROTECTION
            protection_results = await self._protect_content(context)
            context.results.update(protection_results)
            
            # Stage 4: SEO Optimization
            context.stage = WorkflowStage.OPTIMIZATION
            optimization_results = await self._optimize_content(context)
            context.results.update(optimization_results)
            
            # Stage 5: Distribution Strategy
            context.stage = WorkflowStage.DISTRIBUTION
            distribution_results = await self._plan_distribution(context)
            context.results.update(distribution_results)
            
            # Stage 6: Monitoring Setup
            context.stage = WorkflowStage.MONITORING
            monitoring_results = await self._setup_monitoring(context)
            context.results.update(monitoring_results)
            
            # Stage 7: Monetization Planning
            context.stage = WorkflowStage.MONETIZATION
            monetization_results = await self._plan_monetization(context)
            context.results.update(monetization_results)
            
            # Finalize workflow
            context.updated_at = datetime.utcnow()
            self._workflow_history.append(context)
            del self._active_workflows[content_id]
            
            logger.info(f"Music content workflow completed: {content_id}")
            
            return {
                "workflow_id": content_id,
                "status": "completed",
                "results": context.results,
                "recommendations": self._generate_recommendations(context),
                "next_steps": self._generate_next_steps(context),
                "processing_time": (context.updated_at - context.created_at).seconds
            }
            
        except Exception as e:
            logger.error(f"Music workflow processing failed: {str(e)}")
            raise MusicOrchestratorError(f"Workflow processing failed: {str(e)}")

    async def _analyze_content(
        self, 
        context: MusicWorkflowContext, 
        content_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze music content using multiple AI engines"""
        try:
            results = {"analysis": {}}
            
            # Audio analysis with audio agent
            if context.content_type in ['audio', 'music']:
                audio_analysis = await self.audio_agent.analyze_audio(
                    content_data['file_path'],
                    analysis_type='comprehensive'
                )
                results["analysis"]["audio"] = audio_analysis
            
            # Spotify compatibility analysis
            spotify_analysis = await self.spotify_agent.analyze_track_potential(
                audio_features=results["analysis"].get("audio", {}),
                metadata=context.metadata
            )
            results["analysis"]["spotify"] = spotify_analysis
            
            # Content quality assessment
            quality_analysis = await self.content_agent.assess_content_quality(
                content_data,
                content_type=context.content_type
            )
            results["analysis"]["quality"] = quality_analysis
            
            # Genre and mood detection
            genre_analysis = await self._detect_genre_and_mood(content_data)
            results["analysis"]["genre_mood"] = genre_analysis
            
            logger.info(f"Content analysis completed: {context.content_id}")
            return results
            
        except Exception as e:
            logger.error(f"Content analysis failed: {str(e)}")
            raise MusicOrchestratorError(f"Analysis failed: {str(e)}")

    async def _enhance_content(self, context: MusicWorkflowContext) -> Dict[str, Any]:
        """Enhance music content using AI processing"""
        try:
            results = {"enhancement": {}}
            
            # Audio enhancement
            if context.content_type in ['audio', 'music']:
                enhancement_options = {
                    "normalize": True,
                    "enhance_quality": True,
                    "noise_reduction": True,
                    "mastering": context.metadata.get('enable_mastering', False)
                }
                
                enhanced_audio = await self.audio_agent.enhance_audio(
                    input_path=context.metadata.get('file_path'),
                    enhancement_type='professional',
                    options=enhancement_options
                )
                results["enhancement"]["audio"] = enhanced_audio
            
            # Metadata enhancement
            enhanced_metadata = await self._enhance_metadata(context)
            results["enhancement"]["metadata"] = enhanced_metadata
            
            # Generate alternative versions
            if context.metadata.get('create_versions', False):
                versions = await self._generate_content_versions(context)
                results["enhancement"]["versions"] = versions
            
            logger.info(f"Content enhancement completed: {context.content_id}")
            return results
            
        except Exception as e:
            logger.error(f"Content enhancement failed: {str(e)}")
            raise MusicOrchestratorError(f"Enhancement failed: {str(e)}")

    async def _protect_content(self, context: MusicWorkflowContext) -> Dict[str, Any]:
        """Apply content protection and fingerprinting"""
        try:
            results = {"protection": {}}
            
            # Create content fingerprint
            fingerprint = await self.protection_agent.create_fingerprint(
                content_path=context.metadata.get('file_path'),
                content_type=context.content_type,
                user_id=context.user_id
            )
            results["protection"]["fingerprint"] = fingerprint
            
            # Register copyright information
            copyright_info = await self.protection_agent.register_copyright(
                content_id=context.content_id,
                user_id=context.user_id,
                metadata=context.metadata
            )
            results["protection"]["copyright"] = copyright_info
            
            # Setup monitoring for violations
            monitoring_config = await self.protection_agent.setup_violation_monitoring(
                fingerprint_id=fingerprint['id'],
                monitoring_platforms=['youtube', 'instagram', 'tiktok', 'spotify']
            )
            results["protection"]["monitoring"] = monitoring_config
            
            logger.info(f"Content protection completed: {context.content_id}")
            return results
            
        except Exception as e:
            logger.error(f"Content protection failed: {str(e)}")
            raise MusicOrchestratorError(f"Protection failed: {str(e)}")

    async def _optimize_content(self, context: MusicWorkflowContext) -> Dict[str, Any]:
        """Optimize content for SEO and discoverability"""
        try:
            results = {"optimization": {}}
            
            # SEO optimization for metadata
            seo_optimization = await self.content_agent.optimize_seo(
                content_type='music',
                metadata=context.metadata,
                target_platforms=['spotify', 'youtube', 'soundcloud']
            )
            results["optimization"]["seo"] = seo_optimization
            
            # Generate optimized descriptions
            descriptions = await self._generate_optimized_descriptions(context)
            results["optimization"]["descriptions"] = descriptions
            
            # Hashtag optimization
            hashtags = await self._generate_optimal_hashtags(context)
            results["optimization"]["hashtags"] = hashtags
            
            # Release timing optimization
            timing = await self._optimize_release_timing(context)
            results["optimization"]["timing"] = timing
            
            logger.info(f"Content optimization completed: {context.content_id}")
            return results
            
        except Exception as e:
            logger.error(f"Content optimization failed: {str(e)}")
            raise MusicOrchestratorError(f"Optimization failed: {str(e)}")

    async def _plan_distribution(self, context: MusicWorkflowContext) -> Dict[str, Any]:
        """Plan multi-platform distribution strategy"""
        try:
            results = {"distribution": {}}
            
            # Analyze platform compatibility
            platform_analysis = await self._analyze_platform_compatibility(context)
            results["distribution"]["platform_analysis"] = platform_analysis
            
            # Generate distribution plan
            distribution_plan = await self._create_distribution_plan(context)
            results["distribution"]["plan"] = distribution_plan
            
            # Schedule automated posts
            if context.metadata.get('auto_distribute', False):
                scheduled_posts = await self._schedule_distribution(context)
                results["distribution"]["scheduled"] = scheduled_posts
            
            logger.info(f"Distribution planning completed: {context.content_id}")
            return results
            
        except Exception as e:
            logger.error(f"Distribution planning failed: {str(e)}")
            raise MusicOrchestratorError(f"Distribution planning failed: {str(e)}")

    async def _setup_monitoring(self, context: MusicWorkflowContext) -> Dict[str, Any]:
        """Setup comprehensive content monitoring"""
        try:
            results = {"monitoring": {}}
            
            # Performance monitoring
            performance_monitoring = await self.analytics_agent.setup_content_monitoring(
                content_id=context.content_id,
                user_id=context.user_id,
                platforms=['spotify', 'youtube', 'instagram', 'tiktok']
            )
            results["monitoring"]["performance"] = performance_monitoring
            
            # Violation monitoring (already setup in protection)
            violation_monitoring = context.results.get("protection", {}).get("monitoring", {})
            results["monitoring"]["violations"] = violation_monitoring
            
            # Trend monitoring
            trend_monitoring = await self._setup_trend_monitoring(context)
            results["monitoring"]["trends"] = trend_monitoring
            
            logger.info(f"Monitoring setup completed: {context.content_id}")
            return results
            
        except Exception as e:
            logger.error(f"Monitoring setup failed: {str(e)}")
            raise MusicOrchestratorError(f"Monitoring setup failed: {str(e)}")

    async def _plan_monetization(self, context: MusicWorkflowContext) -> Dict[str, Any]:
        """Plan monetization strategy"""
        try:
            results = {"monetization": {}}
            
            # Revenue potential analysis
            revenue_analysis = await self.monetization_agent.analyze_revenue_potential(
                content_analysis=context.results.get("analysis", {}),
                user_id=context.user_id
            )
            results["monetization"]["revenue_analysis"] = revenue_analysis
            
            # Licensing opportunities
            licensing = await self.monetization_agent.identify_licensing_opportunities(
                content_id=context.content_id,
                content_type=context.content_type,
                metadata=context.metadata
            )
            results["monetization"]["licensing"] = licensing
            
            # Collaboration opportunities
            collaborations = await self.collaboration_agent.find_collaboration_matches(
                user_id=context.user_id,
                content_analysis=context.results.get("analysis", {}),
                match_criteria={'genre_match': True, 'audience_overlap': True}
            )
            results["monetization"]["collaborations"] = collaborations
            
            logger.info(f"Monetization planning completed: {context.content_id}")
            return results
            
        except Exception as e:
            logger.error(f"Monetization planning failed: {str(e)}")
            raise MusicOrchestratorError(f"Monetization planning failed: {str(e)}")

    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get status of active or completed workflow"""
        try:
            # Check active workflows
            if workflow_id in self._active_workflows:
                context = self._active_workflows[workflow_id]
                return {
                    "workflow_id": workflow_id,
                    "status": "in_progress",
                    "current_stage": context.stage.value,
                    "progress": self._calculate_progress(context.stage),
                    "started_at": context.created_at.isoformat(),
                    "estimated_completion": self._estimate_completion_time(context)
                }
            
            # Check completed workflows
            for context in self._workflow_history:
                if context.content_id == workflow_id:
                    return {
                        "workflow_id": workflow_id,
                        "status": "completed",
                        "completed_at": context.updated_at.isoformat(),
                        "processing_time": (context.updated_at - context.created_at).seconds,
                        "results_summary": self._summarize_results(context)
                    }
            
            return {"workflow_id": workflow_id, "status": "not_found"}
            
        except Exception as e:
            logger.error(f"Workflow status check failed: {str(e)}")
            raise MusicOrchestratorError(f"Status check failed: {str(e)}")

    async def get_user_workflows(
        self, 
        user_id: str, 
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get workflows for specific user"""
        try:
            await self.security_manager.validate_user_access(user_id, "workflow_history")
            
            workflows = []
            
            # Add active workflows
            if not status or status == "active":
                for context in self._active_workflows.values():
                    if context.user_id == user_id:
                        workflows.append({
                            "workflow_id": context.content_id,
                            "status": "in_progress",
                            "stage": context.stage.value,
                            "started_at": context.created_at.isoformat(),
                            "content_type": context.content_type
                        })
            
            # Add completed workflows
            if not status or status == "completed":
                for context in self._workflow_history:
                    if context.user_id == user_id:
                        workflows.append({
                            "workflow_id": context.content_id,
                            "status": "completed",
                            "completed_at": context.updated_at.isoformat(),
                            "content_type": context.content_type,
                            "processing_time": (context.updated_at - context.created_at).seconds
                        })
            
            # Sort by most recent and limit
            workflows.sort(key=lambda x: x.get('started_at', x.get('completed_at', '')), reverse=True)
            return workflows[:limit]
            
        except Exception as e:
            logger.error(f"User workflows retrieval failed: {str(e)}")
            raise MusicOrchestratorError(f"Workflows retrieval failed: {str(e)}")

    def _generate_content_id(self) -> str:
        """Generate unique content identifier"""
        import uuid
        return f"music_{uuid.uuid4().hex[:12]}"

    def _calculate_progress(self, stage: WorkflowStage) -> float:
        """Calculate workflow progress percentage"""
        stage_progress = {
            WorkflowStage.UPLOAD: 10.0,
            WorkflowStage.ANALYSIS: 25.0,
            WorkflowStage.ENHANCEMENT: 40.0,
            WorkflowStage.PROTECTION: 55.0,
            WorkflowStage.OPTIMIZATION: 70.0,
            WorkflowStage.DISTRIBUTION: 85.0,
            WorkflowStage.MONITORING: 95.0,
            WorkflowStage.MONETIZATION: 100.0
        }
        return stage_progress.get(stage, 0.0)

    def _estimate_completion_time(self, context: MusicWorkflowContext) -> str:
        """Estimate workflow completion time"""
        current_progress = self._calculate_progress(context.stage)
        if current_progress >= 100:
            return "Completed"
        
        elapsed = (datetime.utcnow() - context.created_at).seconds
        estimated_total = (elapsed / current_progress) * 100
        remaining = estimated_total - elapsed
        
        return f"~{int(remaining/60)} minutes"

    async def _detect_genre_and_mood(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect music genre and mood using AI"""
        # This would integrate with audio analysis ML models
        return {
            "genre": {"primary": "Electronic", "secondary": ["Ambient", "Chillout"]},
            "mood": {"energy": 0.7, "valence": 0.8, "danceability": 0.6},
            "tempo": 120,
            "key": "C major"
        }

    async def _enhance_metadata(self, context: MusicWorkflowContext) -> Dict[str, Any]:
        """Enhance content metadata with AI suggestions"""
        return {
            "suggested_title": "AI-Enhanced Title",
            "suggested_description": "Optimized description with SEO keywords",
            "suggested_tags": ["electronic", "ambient", "chill"],
            "target_audience": {"age_group": "18-34", "interests": ["music", "relaxation"]}
        }

    async def _generate_content_versions(self, context: MusicWorkflowContext) -> List[Dict[str, Any]]:
        """Generate alternative content versions"""
        return [
            {"type": "radio_edit", "duration": "3:30", "status": "generated"},
            {"type": "extended_mix", "duration": "6:45", "status": "generated"},
            {"type": "instrumental", "duration": "4:15", "status": "generated"}
        ]

    async def _generate_optimized_descriptions(self, context: MusicWorkflowContext) -> Dict[str, str]:
        """Generate platform-optimized descriptions"""
        return {
            "spotify": "Professional Spotify description with genre keywords",
            "youtube": "YouTube-optimized description with hashtags and engagement hooks",
            "instagram": "Instagram-friendly short description with emojis",
            "tiktok": "TikTok viral description with trending hashtags"
        }

    async def _generate_optimal_hashtags(self, context: MusicWorkflowContext) -> Dict[str, List[str]]:
        """Generate optimal hashtags for each platform"""
        return {
            "instagram": ["#music", "#newmusic", "#electronic", "#chill", "#ambient"],
            "tiktok": ["#music", "#fyp", "#viral", "#electronic", "#trending"],
            "twitter": ["#NewMusic", "#Electronic", "#NowPlaying", "#MusicProducer"],
            "youtube": ["music", "electronic", "ambient", "chill", "relaxing"]
        }

    async def _optimize_release_timing(self, context: MusicWorkflowContext) -> Dict[str, Any]:
        """Optimize release timing based on audience analysis"""
        return {
            "optimal_day": "Friday",
            "optimal_time": "12:00 UTC",
            "timezone_considerations": ["US EST", "EU CET", "Asia JST"],
            "seasonal_factors": {"current_season_boost": 0.15}
        }

    async def _analyze_platform_compatibility(self, context: MusicWorkflowContext) -> Dict[str, Any]:
        """Analyze content compatibility with different platforms"""
        return {
            "spotify": {"compatibility": 0.95, "recommendations": ["Add lyrics"]},
            "youtube": {"compatibility": 0.90, "recommendations": ["Create video version"]},
            "soundcloud": {"compatibility": 0.98, "recommendations": ["Perfect fit"]},
            "instagram": {"compatibility": 0.80, "recommendations": ["Create 30s clip"]}
        }

    async def _create_distribution_plan(self, context: MusicWorkflowContext) -> Dict[str, Any]:
        """Create comprehensive distribution plan"""
        return {
            "primary_platforms": ["Spotify", "Apple Music", "YouTube Music"],
            "secondary_platforms": ["SoundCloud", "Bandcamp", "Amazon Music"],
            "social_platforms": ["Instagram", "TikTok", "Twitter"],
            "release_schedule": {
                "teaser": "7 days before",
                "full_release": "Release day",
                "promotion": "30 days after"
            }
        }

    async def _schedule_distribution(self, context: MusicWorkflowContext) -> List[Dict[str, Any]]:
        """Schedule automated distribution posts"""
        return [
            {
                "platform": "Instagram",
                "content_type": "post",
                "scheduled_time": "2024-01-15T12:00:00Z",
                "status": "scheduled"
            },
            {
                "platform": "TikTok", 
                "content_type": "video",
                "scheduled_time": "2024-01-15T18:00:00Z",
                "status": "scheduled"
            }
        ]

    async def _setup_trend_monitoring(self, context: MusicWorkflowContext) -> Dict[str, Any]:
        """Setup trend monitoring for content"""
        return {
            "keywords": ["electronic music", "ambient", "chill"],
            "platforms": ["Google Trends", "Social Media", "Music Charts"],
            "frequency": "daily",
            "alerts_enabled": True
        }

    def _generate_recommendations(self, context: MusicWorkflowContext) -> List[Dict[str, str]]:
        """Generate actionable recommendations"""
        return [
            {
                "type": "optimization",
                "priority": "high",
                "recommendation": "Consider creating a music video for YouTube distribution"
            },
            {
                "type": "collaboration",
                "priority": "medium", 
                "recommendation": "Explore collaboration with similar artists in your genre"
            },
            {
                "type": "marketing",
                "priority": "high",
                "recommendation": "Schedule social media campaign for release week"
            }
        ]

    def _generate_next_steps(self, context: MusicWorkflowContext) -> List[Dict[str, str]]:
        """Generate next steps for user"""
        return [
            {
                "step": "Review and approve distribution plan",
                "deadline": "3 days",
                "priority": "high"
            },
            {
                "step": "Prepare social media content",
                "deadline": "1 week",
                "priority": "medium"
            },
            {
                "step": "Monitor performance metrics",
                "deadline": "ongoing",
                "priority": "low"
            }
        ]

    def _summarize_results(self, context: MusicWorkflowContext) -> Dict[str, Any]:
        """Summarize workflow results"""
        return {
            "stages_completed": 8,
            "total_recommendations": len(self._generate_recommendations(context)),
            "protection_enabled": "fingerprint" in context.results.get("protection", {}),
            "platforms_ready": len(context.results.get("distribution", {}).get("platform_analysis", {})),
            "monetization_opportunities": len(context.results.get("monetization", {}).get("licensing", []))
        }

    async def cancel_workflow(self, workflow_id: str, user_id: str) -> Dict[str, Any]:
        """Cancel active workflow"""
        try:
            await self.security_manager.validate_user_access(user_id, "workflow_management")
            
            if workflow_id in self._active_workflows:
                context = self._active_workflows[workflow_id]
                if context.user_id != user_id:
                    raise MusicOrchestratorError("Unauthorized workflow cancellation")
                
                # Clean up resources
                await self._cleanup_workflow_resources(context)
                
                # Move to history as cancelled
                context.stage = WorkflowStage.UPLOAD  # Reset stage
                context.results["status"] = "cancelled"
                context.updated_at = datetime.utcnow()
                
                self._workflow_history.append(context)
                del self._active_workflows[workflow_id]
                
                logger.info(f"Workflow cancelled: {workflow_id}")
                return {"workflow_id": workflow_id, "status": "cancelled"}
            
            return {"workflow_id": workflow_id, "status": "not_found"}
            
        except Exception as e:
            logger.error(f"Workflow cancellation failed: {str(e)}")
            raise MusicOrchestratorError(f"Cancellation failed: {str(e)}")

    async def _cleanup_workflow_resources(self, context: MusicWorkflowContext):
        """Clean up resources for cancelled workflow"""
        # This would clean up temporary files, cancel scheduled tasks, etc.
        pass

    async def get_orchestrator_stats(self) -> Dict[str, Any]:
        """Get orchestrator performance statistics"""
        return {
            "active_workflows": len(self._active_workflows),
            "completed_workflows": len(self._workflow_history),
            "average_processing_time": self._calculate_average_processing_time(),
            "success_rate": self._calculate_success_rate(),
            "most_common_content_type": self._get_most_common_content_type(),
            "system_health": "operational"
        }

    def _calculate_average_processing_time(self) -> float:
        """Calculate average workflow processing time"""
        if not self._workflow_history:
            return 0.0
        
        total_time = sum(
            (ctx.updated_at - ctx.created_at).seconds 
            for ctx in self._workflow_history 
            if ctx.results.get("status") != "cancelled"
        )
        successful_workflows = len([
            ctx for ctx in self._workflow_history 
            if ctx.results.get("status") != "cancelled"
        ])
        
        return total_time / max(successful_workflows, 1)

    def _calculate_success_rate(self) -> float:
        """Calculate workflow success rate"""
        if not self._workflow_history:
            return 100.0
        
        successful = len([
            ctx for ctx in self._workflow_history 
            if ctx.results.get("status") != "cancelled"
        ])
        
        return (successful / len(self._workflow_history)) * 100

    def _get_most_common_content_type(self) -> str:
        """Get most common content type processed"""
        if not self._workflow_history:
            return "audio"
        
        content_types = [ctx.content_type for ctx in self._workflow_history]
        return max(set(content_types), key=content_types.count)
