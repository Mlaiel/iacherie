"""SEO Workflows Module - Advanced Search Engine Optimization for Ainflue Platform.

This module provides comprehensive SEO workflow orchestration including keyword research,
content optimization, technical SEO, competitor analysis, and ranking monitoring
for multi-platform content creators and influencers.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Ainflue Platform. All rights reserved.
Licensed under proprietary license - reproduction forbidden without written authorization.
"""

from typing import Dict, List, Optional, Any, Union
from enum import Enum
from datetime import datetime
from dataclasses import dataclass
import asyncio

# Core SEO Workflow Classes
from .keyword_research_workflow import KeywordResearchWorkflow, KeywordStrategy, SearchVolume
from .content_optimization_workflow import ContentOptimizationWorkflow, OptimizationMetrics, ContentScore
from .metadata_enhancement_workflow import MetadataEnhancementWorkflow, MetadataFields, StructuredData
from .hashtag_optimization_workflow import HashtagOptimizationWorkflow, HashtagStrategy, TrendingScore
from .competitor_analysis_workflow import CompetitorAnalysisWorkflow, CompetitorMetrics, MarketPosition
from .ranking_tracking_workflow import RankingTrackingWorkflow, RankingPosition, SERPAnalysis
from .technical_seo_workflow import TechnicalSEOWorkflow, SEOAudit, TechnicalScore
from .local_seo_workflow import LocalSEOWorkflow, LocalRanking, BusinessListing
from .mobile_seo_workflow import MobileSEOWorkflow, MobileScore, ResponsiveMetrics
from .voice_search_optimization_workflow import VoiceSearchOptimizationWorkflow, VoiceQuery, ConversationalKeywords
from .schema_markup_workflow import SchemaMarkupWorkflow, StructuredMarkup, RichSnippets
from .content_clustering_workflow import ContentClusteringWorkflow, TopicCluster, ContentMapping
from .seo_audit_workflow import SEOAuditWorkflow, ComprehensiveAudit, ActionableInsights


class SEOWorkflowType(Enum):
    """SEO workflow types for comprehensive optimization."""
    KEYWORD_RESEARCH = "keyword_research"
    CONTENT_OPTIMIZATION = "content_optimization"
    METADATA_ENHANCEMENT = "metadata_enhancement"
    HASHTAG_OPTIMIZATION = "hashtag_optimization"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    RANKING_TRACKING = "ranking_tracking"
    TECHNICAL_SEO = "technical_seo"
    LOCAL_SEO = "local_seo"
    MOBILE_SEO = "mobile_seo"
    VOICE_SEARCH = "voice_search_optimization"
    SCHEMA_MARKUP = "schema_markup"
    CONTENT_CLUSTERING = "content_clustering"
    SEO_AUDIT = "seo_audit"


class SEOPriority(Enum):
    """SEO task priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MAINTENANCE = "maintenance"


@dataclass
class SEOWorkflowConfig:
    """Configuration for SEO workflow orchestration."""
    workflow_type: SEOWorkflowType
    priority: SEOPriority
    target_platforms: List[str]
    content_type: str
    language: str = "en"
    region: str = "global"
    enable_ai_optimization: bool = True
    enable_competitor_tracking: bool = True
    enable_real_time_monitoring: bool = True
    max_processing_time: int = 3600
    quality_threshold: float = 0.85


@dataclass
class SEOWorkflowResult:
    """Results from SEO workflow execution."""
    workflow_id: str
    workflow_type: SEOWorkflowType
    status: str
    execution_time: float
    optimization_score: float
    recommendations: List[Dict[str, Any]]
    metrics: Dict[str, Any]
    errors: List[str]
    created_at: datetime
    updated_at: datetime


class SEOWorkflowOrchestrator:
    """Advanced SEO workflow orchestration engine for Ainflue Platform."""
    
    def __init__(self, config -> None: Optional[SEOWorkflowConfig] = None) -> None:
        """Initialize the SEO workflow orchestrator.
        
        Args:
            config: Configuration for SEO workflow operations
        """
        self.config = config or self._get_default_config()
        self.workflows = {
            SEOWorkflowType.KEYWORD_RESEARCH: KeywordResearchWorkflow(),
            SEOWorkflowType.CONTENT_OPTIMIZATION: ContentOptimizationWorkflow(),
            SEOWorkflowType.METADATA_ENHANCEMENT: MetadataEnhancementWorkflow(),
            SEOWorkflowType.HASHTAG_OPTIMIZATION: HashtagOptimizationWorkflow(),
            SEOWorkflowType.COMPETITOR_ANALYSIS: CompetitorAnalysisWorkflow(),
            SEOWorkflowType.RANKING_TRACKING: RankingTrackingWorkflow(),
            SEOWorkflowType.TECHNICAL_SEO: TechnicalSEOWorkflow(),
            SEOWorkflowType.LOCAL_SEO: LocalSEOWorkflow(),
            SEOWorkflowType.MOBILE_SEO: MobileSEOWorkflow(),
            SEOWorkflowType.VOICE_SEARCH: VoiceSearchOptimizationWorkflow(),
            SEOWorkflowType.SCHEMA_MARKUP: SchemaMarkupWorkflow(),
            SEOWorkflowType.CONTENT_CLUSTERING: ContentClusteringWorkflow(),
            SEOWorkflowType.SEO_AUDIT: SEOAuditWorkflow()
        }
        
    def _get_default_config(self) -> SEOWorkflowConfig:
        """Get default SEO workflow configuration."""
        return SEOWorkflowConfig(
            workflow_type=SEOWorkflowType.CONTENT_OPTIMIZATION,
            priority=SEOPriority.HIGH,
            target_platforms=["youtube", "google", "instagram", "tiktok"],
            content_type="mixed",
            language="en",
            region="global"
        )
    
    async def execute_workflow(
        self,
        workflow_type: SEOWorkflowType,
        content_data: Dict[str, Any],
        config_override: Optional[Dict[str, Any]] = None
    ) -> SEOWorkflowResult:
        """Execute a specific SEO workflow.
        
        Args:
            workflow_type: Type of SEO workflow to execute
            content_data: Content data for optimization
            config_override: Configuration overrides
            
        Returns:
            SEOWorkflowResult with optimization results
        """
        start_time = datetime.now()
        workflow_id = f"seo_{workflow_type.value}_{int(start_time.timestamp())}"
        
        try:
            # Get workflow instance
            workflow = self.workflows[workflow_type]
            
            # Apply configuration overrides
            if config_override:
                for key, value in config_override.items():
                    setattr(self.config, key, value)
            
            # Execute workflow
            result = await workflow.execute(content_data, self.config)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return SEOWorkflowResult(
                workflow_id=workflow_id,
                workflow_type=workflow_type,
                status="completed",
                execution_time=execution_time,
                optimization_score=result.get("score", 0.0),
                recommendations=result.get("recommendations", []),
                metrics=result.get("metrics", {}),
                errors=[],
                created_at=start_time,
                updated_at=datetime.now()
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return SEOWorkflowResult(
                workflow_id=workflow_id,
                workflow_type=workflow_type,
                status="failed",
                execution_time=execution_time,
                optimization_score=0.0,
                recommendations=[],
                metrics={},
                errors=[str(e)],
                created_at=start_time,
                updated_at=datetime.now()
            )
    
    async def execute_comprehensive_seo(
        self,
        content_data: Dict[str, Any],
        workflow_types: Optional[List[SEOWorkflowType]] = None
    ) -> Dict[str, SEOWorkflowResult]:
        """Execute comprehensive SEO optimization across multiple workflows.
        
        Args:
            content_data: Content data for optimization
            workflow_types: Specific workflows to execute (default: all)
            
        Returns:
            Dict mapping workflow types to results
        """
        if workflow_types is None:
            workflow_types = list(SEOWorkflowType)
        
        tasks = []
        for workflow_type in workflow_types:
            task = self.execute_workflow(workflow_type, content_data)
            tasks.append((workflow_type, task))
        
        results = {}
        for workflow_type, task in tasks:
            try:
                result = await task
                results[workflow_type.value] = result
            except Exception as e:
                results[workflow_type.value] = SEOWorkflowResult(
                    workflow_id=f"failed_{workflow_type.value}",
                    workflow_type=workflow_type,
                    status="failed",
                    execution_time=0.0,
                    optimization_score=0.0,
                    recommendations=[],
                    metrics={},
                    errors=[str(e)],
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
        
        return results
    
    async def get_optimization_recommendations(
        self,
        content_data: Dict[str, Any],
        priority_level: SEOPriority = SEOPriority.HIGH
    ) -> List[Dict[str, Any]]:
        """Get prioritized SEO optimization recommendations.
        
        Args:
            content_data: Content data for analysis
            priority_level: Minimum priority level for recommendations
            
        Returns:
            List of prioritized recommendations
        """
        # Execute comprehensive SEO analysis
        results = await self.execute_comprehensive_seo(content_data)
        
        # Aggregate recommendations
        all_recommendations = []
        for result in results.values():
            if result.status == "completed":
                for rec in result.recommendations:
                    rec["source_workflow"] = result.workflow_type.value
                    rec["optimization_score"] = result.optimization_score
                    all_recommendations.append(rec)
        
        # Filter by priority and sort
        filtered_recs = [
            rec for rec in all_recommendations 
            if rec.get("priority", "low") in [p.value for p in SEOPriority if p.value >= priority_level.value]
        ]
        
        # Sort by impact score and priority
        filtered_recs.sort(
            key=lambda x: (x.get("impact_score", 0), x.get("priority", "low")),
            reverse=True
        )
        
        return filtered_recs[:50]  # Return top 50 recommendations


# Export main classes and functions
__all__ = [
    "SEOWorkflowOrchestrator",
    "SEOWorkflowType",
    "SEOPriority",
    "SEOWorkflowConfig",
    "SEOWorkflowResult",
    "KeywordResearchWorkflow",
    "ContentOptimizationWorkflow",
    "MetadataEnhancementWorkflow",
    "HashtagOptimizationWorkflow",
    "CompetitorAnalysisWorkflow",
    "RankingTrackingWorkflow",
    "TechnicalSEOWorkflow",
    "LocalSEOWorkflow",
    "MobileSEOWorkflow",
    "VoiceSearchOptimizationWorkflow",
    "SchemaMarkupWorkflow",
    "ContentClusteringWorkflow",
    "SEOAuditWorkflow"
]

# Module metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
__copyright__ = "© 2025 Ainflue Platform. All rights reserved."
__license__ = "Proprietary - Reproduction forbidden without written authorization"