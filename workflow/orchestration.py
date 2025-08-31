"""Workflow orchestration engine for content processing and protection.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA-Influencer Project. All rights reserved.
Licensed under proprietary license - reproduction forbidden without written authorization.
"""
import asyncio
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from enum import Enum
import json
import uuid
import logging

from ..core.exceptions import WorkflowException
from ..models.content import ContentItem
from ..services.ai.content_analyzer import ContentAnalyzer
from ..services.protection.fingerprinting import FingerprintService
from ..services.seo.optimizer import SEOOptimizer
from ..services.collaboration.matcher import CollaborationMatcher
from ..services.distribution.publisher import MultiPlatformPublisher


class WorkflowStage(Enum):
    """Content processing workflow stages."""
    INGESTION = "ingestion"
    ANALYSIS = "analysis"
    PROTECTION = "protection"
    SEO_OPTIMIZATION = "seo_optimization"
    COLLABORATION_MATCHING = "collaboration_matching"
    DISTRIBUTION = "distribution"
    MONITORING = "monitoring"


class WorkflowStatus(Enum):
    """Workflow execution status."""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class WorkflowContext:
    """Context object passed through workflow stages."""
    
    def __init__(self, workflow_id: str, user_id: str, content_item: ContentItem):
        self.workflow_id = workflow_id
        self.user_id = user_id
        self.content_item = content_item
        self.metadata = {}
        self.stage_results = {}
        self.errors = []
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def set_stage_result(self, stage: WorkflowStage, result: Dict[str, Any]) -> None:
        """Set result for a workflow stage."""
        self.stage_results[stage.value] = result
        self.updated_at = datetime.utcnow()
    
    def get_stage_result(self, stage: WorkflowStage) -> Optional[Dict[str, Any]]:
        """Get result from a workflow stage."""
        return self.stage_results.get(stage.value)
    
    def add_error(self, stage: WorkflowStage, error: str) -> None:
        """Add error to workflow context."""
        self.errors.append({
            "stage": stage.value,
            "error": error,
            "timestamp": datetime.utcnow().isoformat()
        })


class WorkflowStageHandler:
    """Base class for workflow stage handlers."""
    
    def __init__(self, stage: WorkflowStage):
        self.stage = stage
        self.logger = logging.getLogger(f"workflow.{stage.value}")
    
    async def process(self, context: WorkflowContext) -> bool:
        """Process the workflow stage. Return True if successful."""
        # Default implementation for workflow stage handlers without specific implementation
        logging.warning(f"Workflow stage processing not implemented for {self.stage.value}")
        return False


class IngestionStageHandler(WorkflowStageHandler):
    """Handle content ingestion and initial processing."""
    
    def __init__(self):
        super().__init__(WorkflowStage.INGESTION)
        self.content_analyzer = ContentAnalyzer()
    
    async def process(self, context: WorkflowContext) -> bool:
        """Process content ingestion stage."""
        try:
            # Validate content format and quality
            validation_result = await self.content_analyzer.validate_content(
                context.content_item
            )
            
            if not validation_result.is_valid:
                context.add_error(
                    self.stage, 
                    f"Content validation failed: {validation_result.errors}"
                )
                return False
            
            # Extract metadata and technical specifications
            metadata = await self.content_analyzer.extract_metadata(
                context.content_item
            )
            
            context.set_stage_result(self.stage, {
                "validation": validation_result.to_dict(),
                "metadata": metadata,
                "processing_hints": await self._generate_processing_hints(metadata)
            })
            
            self.logger.info(
                f"Content ingestion completed for workflow {context.workflow_id}"
            )
            return True
            
        except Exception as e:
            context.add_error(self.stage, str(e))
            self.logger.error(
                f"Ingestion failed for workflow {context.workflow_id}: {str(e)}"
            )
            return False
    
    async def _generate_processing_hints(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Generate processing hints based on content metadata."""
        hints = {
            "priority": "normal",
            "processing_complexity": "medium",
            "recommended_quality": "high"
        }
        
        content_type = metadata.get("content_type")
        file_size = metadata.get("file_size", 0)
        
        # Adjust hints based on content characteristics
        if content_type in ["video", "audio"] and file_size > 100 * 1024 * 1024:  # 100MB
            hints["processing_complexity"] = "high"
            hints["priority"] = "high"
        
        if metadata.get("has_commercial_potential", False):
            hints["recommended_quality"] = "premium"
            hints["priority"] = "high"
        
        return hints


class AnalysisStageHandler(WorkflowStageHandler):
    """Handle AI-powered content analysis."""
    
    def __init__(self):
        super().__init__(WorkflowStage.ANALYSIS)
        self.content_analyzer = ContentAnalyzer()
    
    async def process(self, context: WorkflowContext) -> bool:
        """Process content analysis stage."""
        try:
            # Perform comprehensive AI analysis
            analysis_result = await self.content_analyzer.analyze_comprehensive(
                context.content_item,
                context.get_stage_result(WorkflowStage.INGESTION)
            )
            
            # Generate content insights
            insights = await self._generate_content_insights(analysis_result)
            
            # Detect monetization opportunities
            monetization_opportunities = await self._detect_monetization_opportunities(
                analysis_result
            )
            
            context.set_stage_result(self.stage, {
                "analysis": analysis_result,
                "insights": insights,
                "monetization_opportunities": monetization_opportunities,
                "quality_score": analysis_result.get("quality_score", 0.0),
                "commercial_viability": analysis_result.get("commercial_viability", 0.0)
            })
            
            self.logger.info(
                f"Content analysis completed for workflow {context.workflow_id}"
            )
            return True
            
        except Exception as e:
            context.add_error(self.stage, str(e))
            self.logger.error(
                f"Analysis failed for workflow {context.workflow_id}: {str(e)}"
            )
            return False
    
    async def _generate_content_insights(self, analysis_result: Dict) -> Dict[str, Any]:
        """Generate actionable insights from content analysis."""
        insights = {
            "content_category": analysis_result.get("category", "unknown"),
            "target_audience": analysis_result.get("target_audience", []),
            "trending_topics": analysis_result.get("trending_topics", []),
            "optimization_suggestions": []
        }
        
        # Add specific suggestions based on analysis
        quality_score = analysis_result.get("quality_score", 0.0)
        if quality_score < 0.7:
            insights["optimization_suggestions"].append(
                "Consider improving content quality for better engagement"
            )
        
        return insights
    
    async def _detect_monetization_opportunities(self, analysis_result: Dict) -> List[Dict]:
        """Detect potential monetization opportunities."""
        opportunities = []
        
        if analysis_result.get("has_brand_potential", False):
            opportunities.append({
                "type": "brand_partnership",
                "confidence": 0.8,
                "description": "Content suitable for brand collaborations"
            })
        
        if analysis_result.get("viral_potential", 0.0) > 0.7:
            opportunities.append({
                "type": "viral_licensing",
                "confidence": 0.7,
                "description": "High viral potential for content licensing"
            })
        
        return opportunities


class ProtectionStageHandler(WorkflowStageHandler):
    """Handle content protection and fingerprinting."""
    
    def __init__(self):
        super().__init__(WorkflowStage.PROTECTION)
        self.fingerprint_service = FingerprintService()
    
    async def process(self, context: WorkflowContext) -> bool:
        """Process content protection stage."""
        try:
            # Generate content fingerprints
            fingerprints = await self.fingerprint_service.generate_fingerprints(
                context.content_item
            )
            
            # Register content for monitoring
            monitoring_config = await self._setup_content_monitoring(
                context, fingerprints
            )
            
            # Set up protection alerts
            alert_config = await self._configure_protection_alerts(context)
            
            context.set_stage_result(self.stage, {
                "fingerprints": fingerprints,
                "monitoring_config": monitoring_config,
                "alert_config": alert_config,
                "protection_level": self._determine_protection_level(context),
                "monitoring_platforms": self._get_monitoring_platforms(context)
            })
            
            self.logger.info(
                f"Content protection configured for workflow {context.workflow_id}"
            )
            return True
            
        except Exception as e:
            context.add_error(self.stage, str(e))
            self.logger.error(
                f"Protection setup failed for workflow {context.workflow_id}: {str(e)}"
            )
            return False
    
    def _determine_protection_level(self, context: WorkflowContext) -> str:
        """Determine appropriate protection level."""
        analysis_result = context.get_stage_result(WorkflowStage.ANALYSIS)
        if not analysis_result:
            return "standard"
        
        commercial_viability = analysis_result.get("commercial_viability", 0.0)
        if commercial_viability > 0.8:
            return "premium"
        elif commercial_viability > 0.5:
            return "enhanced"
        return "standard"
    
    def _get_monitoring_platforms(self, context: WorkflowContext) -> List[str]:
        """Get list of platforms to monitor for content theft."""
        base_platforms = ["youtube", "instagram", "tiktok"]
        
        # Add more platforms based on content type and user preferences
        content_type = context.content_item.content_type
        if content_type == "audio":
            base_platforms.extend(["spotify", "soundcloud", "apple_music"])
        elif content_type == "video":
            base_platforms.extend(["vimeo", "dailymotion", "twitch"])
        
        return base_platforms
    
    async def _setup_content_monitoring(self, context: WorkflowContext, fingerprints: Dict) -> Dict:
        """Set up monitoring configuration."""
        return {
            "enabled": True,
            "frequency": "daily",
            "sensitivity": 0.85,
            "platforms": self._get_monitoring_platforms(context),
            "fingerprint_ids": list(fingerprints.keys())
        }
    
    async def _configure_protection_alerts(self, context: WorkflowContext) -> Dict:
        """Configure protection alert settings."""
        return {
            "email_notifications": True,
            "slack_notifications": False,
            "sms_notifications": False,
            "threshold": 0.8,
            "auto_takedown": False
        }


class SEOOptimizationStageHandler(WorkflowStageHandler):
    """Handle SEO optimization for content."""
    
    def __init__(self):
        super().__init__(WorkflowStage.SEO_OPTIMIZATION)
        self.seo_optimizer = SEOOptimizer()
    
    async def process(self, context: WorkflowContext) -> bool:
        """Process SEO optimization stage."""
        try:
            analysis_result = context.get_stage_result(WorkflowStage.ANALYSIS)
            if not analysis_result:
                context.add_error(self.stage, "Missing analysis results")
                return False
            
            # Generate SEO-optimized metadata
            seo_metadata = await self.seo_optimizer.optimize_metadata(
                context.content_item,
                analysis_result
            )
            
            # Generate keywords and tags
            keywords = await self.seo_optimizer.generate_keywords(
                context.content_item,
                analysis_result["insights"]
            )
            
            # Create optimized descriptions
            descriptions = await self.seo_optimizer.create_descriptions(
                context.content_item,
                keywords
            )
            
            context.set_stage_result(self.stage, {
                "seo_metadata": seo_metadata,
                "keywords": keywords,
                "descriptions": descriptions,
                "seo_score": await self._calculate_seo_score(seo_metadata, keywords),
                "optimization_suggestions": await self._generate_seo_suggestions(context)
            })
            
            self.logger.info(
                f"SEO optimization completed for workflow {context.workflow_id}"
            )
            return True
            
        except Exception as e:
            context.add_error(self.stage, str(e))
            self.logger.error(
                f"SEO optimization failed for workflow {context.workflow_id}: {str(e)}"
            )
            return False
    
    async def _calculate_seo_score(self, metadata: Dict, keywords: Dict) -> float:
        """Calculate SEO optimization score."""
        score = 0.0
        
        # Check title optimization
        if metadata.get("title") and len(metadata["title"]) > 10:
            score += 0.2
        
        # Check description optimization
        if metadata.get("description") and len(metadata["description"]) > 50:
            score += 0.2
        
        # Check keywords
        if keywords.get("primary_keywords") and len(keywords["primary_keywords"]) >= 3:
            score += 0.3
        
        # Check tags
        if keywords.get("tags") and len(keywords["tags"]) >= 5:
            score += 0.3
        
        return score
    
    async def _generate_seo_suggestions(self, context: WorkflowContext) -> List[str]:
        """Generate SEO improvement suggestions."""
        suggestions = []
        
        # Add generic suggestions that could be customized based on analysis
        suggestions.extend([
            "Consider adding trending hashtags relevant to your content",
            "Optimize posting time based on audience activity",
            "Create engaging thumbnails for better click-through rates"
        ])
        
        return suggestions


class CollaborationMatchingStageHandler(WorkflowStageHandler):
    """Handle collaboration matching and opportunities."""
    
    def __init__(self):
        super().__init__(WorkflowStage.COLLABORATION_MATCHING)
        self.collaboration_matcher = CollaborationMatcher()
    
    async def process(self, context: WorkflowContext) -> bool:
        """Process collaboration matching stage."""
        try:
            analysis_result = context.get_stage_result(WorkflowStage.ANALYSIS)
            if not analysis_result:
                context.add_error(self.stage, "Missing analysis results")
                return False
            
            # Find collaboration opportunities
            collaboration_matches = await self.collaboration_matcher.find_matches(
                context.user_id,
                context.content_item,
                analysis_result
            )
            
            # Score and rank matches
            scored_matches = await self._score_collaboration_matches(
                collaboration_matches,
                context
            )
            
            # Generate collaboration suggestions
            suggestions = await self._generate_collaboration_suggestions(
                scored_matches,
                analysis_result
            )
            
            context.set_stage_result(self.stage, {
                "collaboration_matches": scored_matches,
                "suggestions": suggestions,
                "match_count": len(scored_matches),
                "top_match_score": max([m.get("score", 0) for m in scored_matches], default=0)
            })
            
            self.logger.info(
                f"Collaboration matching completed for workflow {context.workflow_id}"
            )
            return True
            
        except Exception as e:
            context.add_error(self.stage, str(e))
            self.logger.error(
                f"Collaboration matching failed for workflow {context.workflow_id}: {str(e)}"
            )
            return False
    
    async def _score_collaboration_matches(
        self, 
        matches: List[Dict], 
        context: WorkflowContext
    ) -> List[Dict]:
        """Score and rank collaboration matches."""
        scored_matches = []
        
        for match in matches:
            score = 0.0
            
            # Score based on audience overlap
            audience_overlap = match.get("audience_overlap", 0.0)
            score += audience_overlap * 0.4
            
            # Score based on content compatibility
            content_compatibility = match.get("content_compatibility", 0.0)
            score += content_compatibility * 0.3
            
            # Score based on engagement rates
            engagement_compatibility = match.get("engagement_compatibility", 0.0)
            score += engagement_compatibility * 0.3
            
            match["score"] = score
            scored_matches.append(match)
        
        # Sort by score descending
        return sorted(scored_matches, key=lambda x: x["score"], reverse=True)
    
    async def _generate_collaboration_suggestions(
        self, 
        matches: List[Dict],
        analysis_result: Dict
    ) -> List[Dict]:
        """Generate collaboration suggestions."""
        suggestions = []
        
        for match in matches[:5]:  # Top 5 matches
            suggestion = {
                "collaborator_id": match["user_id"],
                "collaboration_type": self._determine_collaboration_type(match, analysis_result),
                "potential_reach": match.get("combined_reach", 0),
                "suggested_action": self._suggest_collaboration_action(match),
                "confidence": match["score"]
            }
            suggestions.append(suggestion)
        
        return suggestions
    
    def _determine_collaboration_type(self, match: Dict, analysis_result: Dict) -> str:
        """Determine the type of collaboration."""
        content_types = [
            analysis_result.get("content_category", ""),
            match.get("primary_content_type", "")
        ]
        
        if "music" in content_types:
            return "musical_collaboration"
        elif "video" in content_types:
            return "video_collaboration"
        elif "brand" in match.get("tags", []):
            return "brand_partnership"
        else:
            return "cross_promotion"
    
    def _suggest_collaboration_action(self, match: Dict) -> str:
        """Suggest specific collaboration action."""
        score = match.get("score", 0)
        
        if score > 0.8:
            return "Send collaboration proposal immediately"
        elif score > 0.6:
            return "Engage with content first, then reach out"
        else:
            return "Monitor for future opportunities"


class DistributionStageHandler(WorkflowStageHandler):
    """Handle multi-platform content distribution."""
    
    def __init__(self):
        super().__init__(WorkflowStage.DISTRIBUTION)
        self.multi_platform_publisher = MultiPlatformPublisher()
    
    async def process(self, context: WorkflowContext) -> bool:
        """Process content distribution stage."""
        try:
            # Get optimized content from previous stages
            seo_result = context.get_stage_result(WorkflowStage.SEO_OPTIMIZATION)
            if not seo_result:
                context.add_error(self.stage, "Missing SEO optimization results")
                return False
            
            # Prepare distribution plan
            distribution_plan = await self._create_distribution_plan(context)
            
            # Execute distribution across platforms
            distribution_results = await self.multi_platform_publisher.distribute_content(
                context.content_item,
                distribution_plan,
                seo_result
            )
            
            # Track distribution metrics
            tracking_setup = await self._setup_distribution_tracking(
                context,
                distribution_results
            )
            
            context.set_stage_result(self.stage, {
                "distribution_plan": distribution_plan,
                "distribution_results": distribution_results,
                "tracking_setup": tracking_setup,
                "published_platforms": [r["platform"] for r in distribution_results if r.get("success")],
                "failed_platforms": [r["platform"] for r in distribution_results if not r.get("success")]
            })
            
            self.logger.info(
                f"Content distribution completed for workflow {context.workflow_id}"
            )
            return True
            
        except Exception as e:
            context.add_error(self.stage, str(e))
            self.logger.error(
                f"Content distribution failed for workflow {context.workflow_id}: {str(e)}"
            )
            return False
    
    async def _create_distribution_plan(self, context: WorkflowContext) -> Dict:
        """Create optimized distribution plan."""
        analysis_result = context.get_stage_result(WorkflowStage.ANALYSIS)
        content_type = context.content_item.content_type
        
        plan = {
            "primary_platforms": [],
            "secondary_platforms": [],
            "scheduling": {},
            "customizations": {}
        }
        
        # Determine primary platforms based on content type
        if content_type == "audio":
            plan["primary_platforms"] = ["spotify", "youtube_music", "soundcloud"]
            plan["secondary_platforms"] = ["instagram", "tiktok"]
        elif content_type == "video":
            plan["primary_platforms"] = ["youtube", "instagram", "tiktok"]
            plan["secondary_platforms"] = ["twitter", "linkedin"]
        elif content_type == "image":
            plan["primary_platforms"] = ["instagram", "pinterest", "twitter"]
            plan["secondary_platforms"] = ["facebook", "linkedin"]
        
        # Add scheduling based on audience insights
        if analysis_result and "target_audience" in analysis_result:
            plan["scheduling"] = await self._optimize_posting_schedule(
                analysis_result["target_audience"]
            )
        
        return plan
    
    async def _optimize_posting_schedule(self, target_audience: List[Dict]) -> Dict:
        """Optimize posting schedule based on audience activity."""
        # Default schedule - would be enhanced with real audience data
        return {
            "instagram": {"time": "18:00", "timezone": "UTC"},
            "youtube": {"time": "20:00", "timezone": "UTC"},
            "tiktok": {"time": "19:00", "timezone": "UTC"},
            "twitter": {"time": "12:00", "timezone": "UTC"}
        }
    
    async def _setup_distribution_tracking(
        self,
        context: WorkflowContext,
        distribution_results: List[Dict]
    ) -> Dict:
        """Set up tracking for distributed content."""
        return {
            "analytics_enabled": True,
            "tracking_metrics": ["views", "engagement", "shares", "revenue"],
            "reporting_frequency": "daily",
            "platforms": [r["platform"] for r in distribution_results if r.get("success")]
        }


class MonitoringStageHandler(WorkflowStageHandler):
    """Handle ongoing content monitoring and analytics."""
    
    def __init__(self):
        super().__init__(WorkflowStage.MONITORING)
    
    async def process(self, context: WorkflowContext) -> bool:
        """Process monitoring setup stage."""
        try:
            # Set up comprehensive monitoring
            monitoring_config = await self._setup_comprehensive_monitoring(context)
            
            # Configure analytics dashboards
            dashboard_config = await self._configure_analytics_dashboards(context)
            
            # Set up automated reporting
            reporting_config = await self._setup_automated_reporting(context)
            
            context.set_stage_result(self.stage, {
                "monitoring_config": monitoring_config,
                "dashboard_config": dashboard_config,
                "reporting_config": reporting_config,
                "monitoring_active": True,
                "next_report": datetime.utcnow().isoformat()
            })
            
            self.logger.info(
                f"Monitoring setup completed for workflow {context.workflow_id}"
            )
            return True
            
        except Exception as e:
            context.add_error(self.stage, str(e))
            self.logger.error(
                f"Monitoring setup failed for workflow {context.workflow_id}: {str(e)}"
            )
            return False
    
    async def _setup_comprehensive_monitoring(self, context: WorkflowContext) -> Dict:
        """Set up comprehensive content monitoring."""
        return {
            "content_protection": True,
            "performance_analytics": True,
            "revenue_tracking": True,
            "collaboration_tracking": True,
            "seo_monitoring": True
        }
    
    async def _configure_analytics_dashboards(self, context: WorkflowContext) -> Dict:
        """Configure analytics dashboards."""
        return {
            "main_dashboard": True,
            "protection_dashboard": True,
            "revenue_dashboard": True,
            "collaboration_dashboard": True,
            "refresh_interval": 300  # 5 minutes
        }
    
    async def _setup_automated_reporting(self, context: WorkflowContext) -> Dict:
        """Set up automated reporting."""
        return {
            "daily_summary": True,
            "weekly_report": True,
            "monthly_analysis": True,
            "alert_thresholds": {
                "protection_violations": 1,
                "revenue_drops": 0.2,
                "engagement_drops": 0.3
            }
        }


class ContentWorkflowOrchestrator:
    """Main orchestrator for content processing workflows."""
    
    def __init__(self):
        self.logger = logging.getLogger("workflow.orchestrator")
        self.active_workflows = {}
        
        # Initialize stage handlers
        self.stage_handlers = {
            WorkflowStage.INGESTION: IngestionStageHandler(),
            WorkflowStage.ANALYSIS: AnalysisStageHandler(),
            WorkflowStage.PROTECTION: ProtectionStageHandler(),
            WorkflowStage.SEO_OPTIMIZATION: SEOOptimizationStageHandler(),
            WorkflowStage.COLLABORATION_MATCHING: CollaborationMatchingStageHandler(),
            WorkflowStage.DISTRIBUTION: DistributionStageHandler(),
            WorkflowStage.MONITORING: MonitoringStageHandler()
        }
    
    async def start_workflow(
        self,
        user_id: str,
        content_item: ContentItem,
        workflow_config: Optional[Dict] = None
    ) -> str:
        """Start a new content processing workflow."""
        workflow_id = f"workflow_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        context = WorkflowContext(workflow_id, user_id, content_item)
        
        # Apply workflow configuration
        if workflow_config:
            context.metadata.update(workflow_config)
        
        self.active_workflows[workflow_id] = {
            "context": context,
            "status": WorkflowStatus.QUEUED,
            "current_stage": None,
            "started_at": datetime.utcnow()
        }
        
        # Start workflow processing asynchronously
        asyncio.create_task(self._execute_workflow(workflow_id))
        
        self.logger.info(f"Started workflow {workflow_id} for user {user_id}")
        return workflow_id
    
    async def _execute_workflow(self, workflow_id: str) -> None:
        """Execute the complete workflow."""
        workflow_info = self.active_workflows.get(workflow_id)
        if not workflow_info:
            self.logger.error(f"Workflow {workflow_id} not found")
            return
        
        context = workflow_info["context"]
        workflow_info["status"] = WorkflowStatus.PROCESSING
        
        # Define workflow stage order
        stages = [
            WorkflowStage.INGESTION,
            WorkflowStage.ANALYSIS,
            WorkflowStage.PROTECTION,
            WorkflowStage.SEO_OPTIMIZATION,
            WorkflowStage.COLLABORATION_MATCHING,
            WorkflowStage.DISTRIBUTION,
            WorkflowStage.MONITORING
        ]
        
        try:
            for stage in stages:
                workflow_info["current_stage"] = stage
                self.logger.info(f"Processing stage {stage.value} for workflow {workflow_id}")
                
                handler = self.stage_handlers[stage]
                success = await handler.process(context)
                
                if not success:
                    self.logger.error(
                        f"Stage {stage.value} failed for workflow {workflow_id}"
                    )
                    workflow_info["status"] = WorkflowStatus.FAILED
                    return
                
                self.logger.info(f"Stage {stage.value} completed for workflow {workflow_id}")
            
            # Workflow completed successfully
            workflow_info["status"] = WorkflowStatus.COMPLETED
            workflow_info["completed_at"] = datetime.utcnow()
            
            self.logger.info(f"Workflow {workflow_id} completed successfully")
            
        except Exception as e:
            self.logger.error(f"Workflow {workflow_id} failed with error: {str(e)}")
            workflow_info["status"] = WorkflowStatus.FAILED
            context.add_error(WorkflowStage.INGESTION, str(e))
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict]:
        """Get current workflow status."""
        workflow_info = self.active_workflows.get(workflow_id)
        if not workflow_info:
            return None
        
        return {
            "workflow_id": workflow_id,
            "status": workflow_info["status"].value,
            "current_stage": workflow_info["current_stage"].value if workflow_info["current_stage"] else None,
            "started_at": workflow_info["started_at"].isoformat(),
            "completed_at": workflow_info.get("completed_at", {}).isoformat() if workflow_info.get("completed_at") else None,
            "errors": workflow_info["context"].errors,
            "stage_results": {k: v for k, v in workflow_info["context"].stage_results.items()}
        }
    
    def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel an active workflow."""
        workflow_info = self.active_workflows.get(workflow_id)
        if not workflow_info:
            return False
        
        workflow_info["status"] = WorkflowStatus.CANCELLED
        self.logger.info(f"Workflow {workflow_id} cancelled")
        return True
    
    def get_active_workflows(self, user_id: Optional[str] = None) -> List[Dict]:
        """Get list of active workflows, optionally filtered by user."""
        workflows = []
        
        for workflow_id, workflow_info in self.active_workflows.items():
            if user_id and workflow_info["context"].user_id != user_id:
                continue
            
            workflows.append(self.get_workflow_status(workflow_id))
        
        return workflows
