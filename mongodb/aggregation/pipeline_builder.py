"""Dynamic Aggregation Pipeline Builder
====================================

Advanced pipeline builder for creating optimized MongoDB aggregation pipelines
with dynamic query generation, performance optimization, and caching.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

class AggregationType(Enum):
    """Types of aggregations."""
    COUNT = "count"
    SUM = "sum"
    AVERAGE = "average"
    MIN = "min"
    MAX = "max"
    GROUP = "group"
    SORT = "sort"
    LIMIT = "limit"
    MATCH = "match"
    PROJECT = "project"
    UNWIND = "unwind"
    LOOKUP = "lookup"
    FACET = "facet"

@dataclass
class PipelineStage:
    """Individual pipeline stage."""
    stage_type: AggregationType
    parameters: Dict[str, Any]
    order: int = 0
    cache_key: Optional[str] = None
    estimated_cost: float = 1.0

@dataclass
class PipelineMetrics:
    """Pipeline performance metrics."""
    execution_time_ms: float
    documents_examined: int
    documents_returned: int
    index_usage: Dict[str, Any]
    memory_usage_mb: float
    cache_hit: bool = False

class PipelineBuilder:
    """Dynamic aggregation pipeline builder."""
    
    def __init__(self):
        """Initialize pipeline builder."""
        self._stages: List[PipelineStage] = []
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = 300  # 5 minutes
        self._optimization_rules = self._load_optimization_rules()
    
    def _load_optimization_rules(self) -> Dict[str, Any]:
        """Load pipeline optimization rules."""
        return {
            "early_match": True,  # Move $match stages early
            "early_project": True,  # Move $project stages early when possible
            "combine_matches": True,  # Combine multiple $match stages
            "index_hints": True,  # Add index hints for better performance
            "limit_early": True,  # Apply $limit early when possible
        }
    
    def match(self, conditions: Dict[str, Any]) -> 'PipelineBuilder':
        """Add match stage to filter documents."""
        stage = PipelineStage(
            stage_type=AggregationType.MATCH,
            parameters={"$match": conditions},
            order=len(self._stages),
            estimated_cost=0.1  # Match is typically fast
        )
        self._stages.append(stage)
        return self
    
    def project(self, projection: Dict[str, Any]) -> 'PipelineBuilder':
        """Add projection stage to select/transform fields."""
        stage = PipelineStage(
            stage_type=AggregationType.PROJECT,
            parameters={"$project": projection},
            order=len(self._stages),
            estimated_cost=0.2
        )
        self._stages.append(stage)
        return self
    
    def group(self, group_by: Union[str, Dict[str, Any]], 
             aggregations: Dict[str, Dict[str, Any]]) -> 'PipelineBuilder':
        """Add group stage for aggregation."""
        group_spec = {
            "_id": group_by,
            **aggregations
        }
        
        stage = PipelineStage(
            stage_type=AggregationType.GROUP,
            parameters={"$group": group_spec},
            order=len(self._stages),
            estimated_cost=1.0  # Grouping can be expensive
        )
        self._stages.append(stage)
        return self
    
    def sort(self, sort_spec: Dict[str, int]) -> 'PipelineBuilder':
        """Add sort stage."""
        stage = PipelineStage(
            stage_type=AggregationType.SORT,
            parameters={"$sort": sort_spec},
            order=len(self._stages),
            estimated_cost=0.5
        )
        self._stages.append(stage)
        return self
    
    def limit(self, count: int) -> 'PipelineBuilder':
        """Add limit stage."""
        stage = PipelineStage(
            stage_type=AggregationType.LIMIT,
            parameters={"$limit": count},
            order=len(self._stages),
            estimated_cost=0.1
        )
        self._stages.append(stage)
        return self
    
    def lookup(self, from_collection: str, local_field: str, 
              foreign_field: str, as_field: str) -> 'PipelineBuilder':
        """Add lookup stage for joins."""
        stage = PipelineStage(
            stage_type=AggregationType.LOOKUP,
            parameters={
                "$lookup": {
                    "from": from_collection,
                    "localField": local_field,
                    "foreignField": foreign_field,
                    "as": as_field
                }
            },
            order=len(self._stages),
            estimated_cost=2.0  # Lookups are expensive
        )
        self._stages.append(stage)
        return self
    
    def unwind(self, field: str, preserve_null: bool = False) -> 'PipelineBuilder':
        """Add unwind stage to deconstruct arrays."""
        unwind_spec = {"path": f"${field}"}
        if preserve_null:
            unwind_spec["preserveNullAndEmptyArrays"] = True
        
        stage = PipelineStage(
            stage_type=AggregationType.UNWIND,
            parameters={"$unwind": unwind_spec},
            order=len(self._stages),
            estimated_cost=0.3
        )
        self._stages.append(stage)
        return self
    
    def facet(self, facets: Dict[str, List[Dict[str, Any]]]) -> 'PipelineBuilder':
        """Add facet stage for multi-dimensional aggregation."""
        stage = PipelineStage(
            stage_type=AggregationType.FACET,
            parameters={"$facet": facets},
            order=len(self._stages),
            estimated_cost=1.5
        )
        self._stages.append(stage)
        return self
    
    def optimize(self) -> 'PipelineBuilder':
        """Optimize pipeline stages for better performance."""
        if not self._optimization_rules:
            return self
        
        # Sort stages for optimal execution order
        if self._optimization_rules.get("early_match"):
            self._move_match_stages_early()
        
        if self._optimization_rules.get("combine_matches"):
            self._combine_match_stages()
        
        if self._optimization_rules.get("limit_early"):
            self._move_limit_early()
        
        return self
    
    def _move_match_stages_early(self):
        """Move $match stages as early as possible."""
        match_stages = [s for s in self._stages if s.stage_type == AggregationType.MATCH]
        other_stages = [s for s in self._stages if s.stage_type != AggregationType.MATCH]
        
        # Reorder: matches first, then others
        self._stages = match_stages + other_stages
        
        # Update order numbers
        for i, stage in enumerate(self._stages):
            stage.order = i
    
    def _combine_match_stages(self):
        """Combine multiple consecutive $match stages."""
        combined_stages = []
        current_match = None
        
        for stage in self._stages:
            if stage.stage_type == AggregationType.MATCH:
                if current_match is None:
                    current_match = stage
                else:
                    # Combine with previous match
                    current_match.parameters["$match"].update(stage.parameters["$match"])
            else:
                if current_match:
                    combined_stages.append(current_match)
                    current_match = None
                combined_stages.append(stage)
        
        if current_match:
            combined_stages.append(current_match)
        
        self._stages = combined_stages
    
    def _move_limit_early(self):
        """Move $limit stages earlier when safe to do so."""
        # This is a simplified implementation
        # In practice, this requires complex analysis of stage dependencies
        pass
    
    def build(self) -> List[Dict[str, Any]]:
        """Build the final aggregation pipeline."""
        # Optimize before building
        self.optimize()
        
        # Convert stages to MongoDB pipeline format
        pipeline = []
        for stage in sorted(self._stages, key=lambda x: x.order):
            pipeline.append(stage.parameters)
        
        return pipeline
    
    def build_with_explain(self) -> Dict[str, Any]:
        """Build pipeline with explain information."""
        pipeline = self.build()
        
        # Calculate estimated performance metrics
        total_cost = sum(stage.estimated_cost for stage in self._stages)
        
        return {
            "pipeline": pipeline,
            "stages_count": len(self._stages),
            "estimated_cost": total_cost,
            "optimization_applied": True,
            "cache_eligible": total_cost > 0.5,  # Cache expensive queries
            "performance_hints": self._generate_performance_hints()
        }
    
    def _generate_performance_hints(self) -> List[str]:
        """Generate performance optimization hints."""
        hints = []
        
        # Check for missing indexes
        match_stages = [s for s in self._stages if s.stage_type == AggregationType.MATCH]
        if match_stages:
            hints.append("Ensure indexes exist for $match conditions")
        
        # Check for expensive operations
        lookup_stages = [s for s in self._stages if s.stage_type == AggregationType.LOOKUP]
        if lookup_stages:
            hints.append("Consider denormalization to avoid $lookup operations")
        
        # Check stage order
        total_cost = sum(stage.estimated_cost for stage in self._stages)
        if total_cost > 2.0:
            hints.append("Consider breaking complex pipeline into smaller queries")
        
        return hints
    
    def clear(self) -> 'PipelineBuilder':
        """Clear all stages and start fresh."""
        self._stages.clear()
        return self
    
    def clone(self) -> 'PipelineBuilder':
        """Create a copy of this pipeline builder."""
        new_builder = PipelineBuilder()
        new_builder._stages = [
            PipelineStage(
                stage_type=stage.stage_type,
                parameters=stage.parameters.copy(),
                order=stage.order,
                cache_key=stage.cache_key,
                estimated_cost=stage.estimated_cost
            )
            for stage in self._stages
        ]
        return new_builder
    
    def get_stages_summary(self) -> List[Dict[str, Any]]:
        """Get summary of pipeline stages."""
        return [
            {
                "order": stage.order,
                "type": stage.stage_type.value,
                "estimated_cost": stage.estimated_cost,
                "parameters_keys": list(stage.parameters.keys())
            }
            for stage in self._stages
        ]

# Factory functions for common pipeline patterns
def create_content_analytics_pipeline() -> PipelineBuilder:
    """Create pipeline for content analytics."""
    return (PipelineBuilder()
            .match({"content_type": {"$in": ["image", "video", "audio", "text"]}})
            .project({
                "content_id": 1,
                "user_id": 1,
                "content_type": 1,
                "created_at": 1,
                "views": {"$ifNull": ["$analytics.views", 0]},
                "likes": {"$ifNull": ["$analytics.likes", 0]},
                "shares": {"$ifNull": ["$analytics.shares", 0]}
            }))

def create_user_engagement_pipeline() -> PipelineBuilder:
    """Create pipeline for user engagement analytics."""
    return (PipelineBuilder()
            .match({"last_activity": {"$gte": datetime.utcnow() - timedelta(days=30)}})
            .group(
                "$user_id",
                {
                    "total_sessions": {"$sum": 1},
                    "total_time": {"$sum": "$session_duration"},
                    "avg_session_time": {"$avg": "$session_duration"},
                    "last_activity": {"$max": "$last_activity"}
                }
            ))

def create_revenue_pipeline(start_date: datetime, end_date: datetime) -> PipelineBuilder:
    """Create pipeline for revenue analytics."""
    return (PipelineBuilder()
            .match({
                "transaction_date": {"$gte": start_date, "$lte": end_date},
                "status": "completed"
            })
            .group(
                {"$dateToString": {"format": "%Y-%m-%d", "date": "$transaction_date"}},
                {
                    "daily_revenue": {"$sum": "$amount"},
                    "transaction_count": {"$sum": 1},
                    "avg_transaction": {"$avg": "$amount"}
                }
            )
            .sort({"_id": 1}))

# Global pipeline builder instance
_default_builder: Optional[PipelineBuilder] = None

def get_pipeline_builder() -> PipelineBuilder:
    """Get or create default pipeline builder."""
    global _default_builder
    if _default_builder is None:
        _default_builder = PipelineBuilder()
    return _default_builder

# Export main classes and functions
__all__ = [
    'AggregationType',
    'PipelineStage',
    'PipelineMetrics',
    'PipelineBuilder',
    'create_content_analytics_pipeline',
    'create_user_engagement_pipeline',
    'create_revenue_pipeline',
    'get_pipeline_builder'
]