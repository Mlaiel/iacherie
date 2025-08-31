"""
Business Context Orchestrator - Intelligent Business Context Management

Advanced business context orchestrator that manages creator-specific business 
contexts, tracks business objectives, coordinates workflow priorities, and 
optimizes cross-functional business processes for content creators.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from collections import defaultdict

from backend.core.database.session import DatabaseManager
from backend.services.ai.business_intelligence import BusinessIntelligenceService
from backend.services.analytics.creator_analytics import CreatorAnalyticsService
from backend.services.workflow.priority_engine import WorkflowPriorityEngine

from .content_creator_flows import CreatorProfile, BusinessObjective, Platform, ContentFormat
from .dialogue_flow_manager import DialogueFlowManager

logger = logging.getLogger(__name__)

class BusinessContextType(Enum):
    """Types of business contexts"""
    ONBOARDING = "onboarding"
    REVENUE_OPTIMIZATION = "revenue_optimization"
    CONTENT_PROTECTION = "content_protection"
    COLLABORATION_SEEKING = "collaboration_seeking"
    PLATFORM_EXPANSION = "platform_expansion"
    CRISIS_MANAGEMENT = "crisis_management"
    GROWTH_SCALING = "growth_scaling"
    LEGAL_COMPLIANCE = "legal_compliance"

class BusinessPriority(Enum):
    """Business priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5

class BusinessPhase(Enum):
    """Business development phases"""
    STARTUP = "startup"
    GROWTH = "growth"
    SCALING = "scaling"
    MATURITY = "maturity"
    TRANSFORMATION = "transformation"
    CRISIS = "crisis"

class ContextStatus(Enum):
    """Business context status"""
    ACTIVE = "active"
    PENDING = "pending"
    SUSPENDED = "suspended"
    COMPLETED = "completed"
    ARCHIVED = "archived"

@dataclass
class BusinessMetrics:
    """Business performance metrics"""
    monthly_revenue: float = 0.0
    revenue_growth_rate: float = 0.0
    audience_size: Dict[Platform, int] = field(default_factory=dict)
    engagement_rate: Dict[Platform, float] = field(default_factory=dict)
    content_performance: Dict[ContentFormat, float] = field(default_factory=dict)
    
    # Protection metrics
    content_protection_coverage: float = 0.0
    infringement_detection_rate: float = 0.0
    
    # Collaboration metrics
    active_collaborations: int = 0
    collaboration_success_rate: float = 0.0
    
    # Platform metrics
    platform_diversification: float = 0.0
    cross_platform_synergy: float = 0.0

@dataclass
class BusinessContext:
    """Comprehensive business context for creators"""
    context_id: str
    creator_id: str
    context_type: BusinessContextType
    priority: BusinessPriority
    status: ContextStatus
    
    # Business objectives
    primary_objectives: List[BusinessObjective] = field(default_factory=list)
    secondary_objectives: List[BusinessObjective] = field(default_factory=list)
    success_criteria: Dict[str, Any] = field(default_factory=dict)
    
    # Context metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    estimated_duration: Optional[timedelta] = None
    deadline: Optional[datetime] = None
    
    # Business intelligence
    market_context: Dict[str, Any] = field(default_factory=dict)
    competitive_landscape: Dict[str, Any] = field(default_factory=dict)
    opportunity_analysis: Dict[str, Any] = field(default_factory=dict)
    
    # Resource allocation
    allocated_budget: float = 0.0
    time_allocation: Dict[str, float] = field(default_factory=dict)
    skill_requirements: List[str] = field(default_factory=list)
    
    # Progress tracking
    milestones: List[Dict[str, Any]] = field(default_factory=list)
    completed_milestones: List[str] = field(default_factory=list)
    blockers: List[Dict[str, Any]] = field(default_factory=list)
    
    # AI insights
    ai_recommendations: List[Dict[str, Any]] = field(default_factory=list)
    predictive_insights: Dict[str, Any] = field(default_factory=dict)
    optimization_opportunities: List[Dict[str, Any]] = field(default_factory=list)

class BusinessContextOrchestrator:
    """Advanced business context orchestrator for content creators"""
    
    def __init__(
        self,
        db_manager: DatabaseManager,
        business_intelligence: BusinessIntelligenceService,
        analytics_service: CreatorAnalyticsService,
        priority_engine: WorkflowPriorityEngine
    ):
        self.db_manager = db_manager
        self.business_intelligence = business_intelligence
        self.analytics_service = analytics_service
        self.priority_engine = priority_engine
        
        # Active business contexts
        self.active_contexts: Dict[str, Dict[str, BusinessContext]] = defaultdict(dict)
        
        # Context orchestration rules
        self.orchestration_rules = self._initialize_orchestration_rules()
        
    def _initialize_orchestration_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize business context orchestration rules"""



        return {
            "priority_matrix": {
                "revenue_impact": {
                    "high": 3,
                    "medium": 2,
                    "low": 1
                },
                "urgency": {
                    "critical": 5,
                    "urgent": 4,
                    "high": 3,
                    "medium": 2,
                    "low": 1
                },
                "resource_availability": {
                    "high": 1,
                    "medium": 2,
                    "low": 3
                }
            },
            
            "context_compatibility": {
                "onboarding": {
                    "compatible": ["revenue_optimization", "content_protection"],
                    "conflicting": ["crisis_management"],
                    "sequential": ["platform_expansion", "collaboration_seeking"]
                },
                "revenue_optimization": {
                    "compatible": ["content_protection", "platform_expansion"],
                    "conflicting": ["crisis_management"],
                    "synergistic": ["collaboration_seeking"]
                },
                "content_protection": {
                    "compatible": ["revenue_optimization", "legal_compliance"],
                    "conflicting": [],
                    "prerequisite": ["onboarding"]
                },
                "collaboration_seeking": {
                    "compatible": ["platform_expansion", "growth_scaling"],
                    "conflicting": ["crisis_management"],
                    "enhances": ["revenue_optimization"]
                },
                "platform_expansion": {
                    "compatible": ["collaboration_seeking", "growth_scaling"],
                    "conflicting": ["crisis_management"],
                    "requires": ["content_protection"]
                },
                "crisis_management": {
                    "compatible": ["legal_compliance"],
                    "conflicting": ["onboarding", "platform_expansion", "collaboration_seeking"],
                    "overrides": "all"
                }
            },
            
            "phase_transitions": {
                "startup": {
                    "next_phases": ["growth"],
                    "duration_months": 3,
                    "success_criteria": ["revenue_threshold", "audience_baseline"]
                },
                "growth": {
                    "next_phases": ["scaling", "maturity"],
                    "duration_months": 12,
                    "success_criteria": ["growth_rate", "platform_diversification"]
                },
                "scaling": {
                    "next_phases": ["maturity"],
                    "duration_months": 18,
                    "success_criteria": ["revenue_scaling", "operational_efficiency"]
                },
                "maturity": {
                    "next_phases": ["transformation"],
                    "duration_months": 24,
                    "success_criteria": ["market_leadership", "innovation_adoption"]
                }
            }
        }

    async def create_business_context(
        self,
        creator_profile: CreatorProfile,
        context_type: BusinessContextType,
        objectives: List[BusinessObjective],
        context_data: Dict[str, Any]
    ) -> BusinessContext:
        """Create a new business context for creator"""



        try:
            # Generate context ID
            context_id = str(uuid.uuid4())
            
            # Analyze business context requirements
            context_analysis = await self._analyze_context_requirements(
                creator_profile, context_type, objectives, context_data
            )
            
            # Determine priority
            priority = await self._calculate_context_priority(
                creator_profile, context_type, objectives, context_analysis
            )
            
            # Create business context
            business_context = BusinessContext(
                context_id=context_id,
                creator_id=creator_profile.creator_id,
                context_type=context_type,
                priority=priority,
                status=ContextStatus.PENDING,
                primary_objectives=objectives[:3],  # Top 3 primary
                secondary_objectives=objectives[3:],  # Rest as secondary
                success_criteria=context_analysis.get("success_criteria", {}),
                market_context=context_analysis.get("market_context", {}),
                competitive_landscape=context_analysis.get("competitive_landscape", {}),
                opportunity_analysis=context_analysis.get("opportunity_analysis", {}),
                estimated_duration=context_analysis.get("estimated_duration"),
                skill_requirements=context_analysis.get("skill_requirements", [])
            )
            
            # Generate AI recommendations
            ai_recommendations = await self._generate_context_recommendations(
                business_context, creator_profile
            )
            business_context.ai_recommendations = ai_recommendations
            
            # Add to active contexts
            self.active_contexts[creator_profile.creator_id][context_id] = business_context
            
            # Store in database
            await self._store_business_context(business_context)
            
            logger.info(f"Created business context {context_id} for creator {creator_profile.creator_id}")
            
            return business_context
            
        except Exception as e:
            logger.error(f"Failed to create business context: {e}")
            raise

    async def orchestrate_contexts(
        self,
        creator_profile: CreatorProfile
    ) -> Dict[str, Any]:
        """Orchestrate multiple business contexts for optimal execution"""



        try:
            creator_contexts = self.active_contexts.get(creator_profile.creator_id, {})
            
            if not creator_contexts:
                return {"orchestrated_contexts": [], "recommendations": []}
            
            # Analyze context interactions
            context_analysis = await self._analyze_context_interactions(
                list(creator_contexts.values())
            )
            
            # Optimize context execution order
            execution_plan = await self._optimize_execution_plan(
                creator_contexts, context_analysis, creator_profile
            )
            
            # Generate orchestration recommendations
            orchestration_recommendations = await self._generate_orchestration_recommendations(
                execution_plan, creator_profile
            )
            
            # Update context priorities based on orchestration
            await self._update_context_priorities(execution_plan)
            
            return {
                "orchestrated_contexts": execution_plan,
                "context_interactions": context_analysis,
                "orchestration_recommendations": orchestration_recommendations,
                "optimization_impact": await self._calculate_optimization_impact(execution_plan)
            }
            
        except Exception as e:
            logger.error(f"Context orchestration failed: {e}")
            return {"error": str(e)}

    async def _analyze_context_requirements(
        self,
        creator_profile: CreatorProfile,
        context_type: BusinessContextType,
        objectives: List[BusinessObjective],
        context_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze business context requirements"""
        # Get creator business metrics
        business_metrics = await self.analytics_service.get_creator_business_metrics(
            creator_profile.creator_id
        )
        
        # Analyze market context
        market_analysis = await self.business_intelligence.analyze_market_context(
            creator_profile, context_type
        )
        
        # Determine success criteria
        success_criteria = await self._define_success_criteria(
            context_type, objectives, business_metrics
        )
        
        # Estimate duration and resources
        resource_analysis = await self._analyze_resource_requirements(
            context_type, objectives, creator_profile
        )
        
        return {
            "success_criteria": success_criteria,
            "market_context": market_analysis,
            "competitive_landscape": market_analysis.get("competitive_landscape", {}),
            "opportunity_analysis": market_analysis.get("opportunities", {}),
            "estimated_duration": resource_analysis.get("estimated_duration"),
            "skill_requirements": resource_analysis.get("skill_requirements", []),
            "resource_requirements": resource_analysis
        }

    async def _calculate_context_priority(
        self,
        creator_profile: CreatorProfile,
        context_type: BusinessContextType,
        objectives: List[BusinessObjective],
        context_analysis: Dict[str, Any]
    ) -> BusinessPriority:
        """Calculate business context priority"""
        # Revenue impact analysis
        revenue_impact = await self._assess_revenue_impact(
            context_type, objectives, creator_profile
        )
        
        # Urgency assessment
        urgency = await self._assess_urgency(
            context_type, context_analysis, creator_profile
        )
        
        # Resource availability
        resource_availability = await self._assess_resource_availability(
            creator_profile, context_analysis.get("resource_requirements", {})
        )
        
        # Calculate weighted priority score
        priority_score = (
            revenue_impact * 0.4 +
            urgency * 0.4 +
            resource_availability * 0.2
        )
        
        # Map to priority enum
        if priority_score >= 4.5:
            return BusinessPriority.CRITICAL
        elif priority_score >= 3.5:
            return BusinessPriority.URGENT
        elif priority_score >= 2.5:
            return BusinessPriority.HIGH
        elif priority_score >= 1.5:
            return BusinessPriority.MEDIUM
        else:
            return BusinessPriority.LOW

    async def _generate_context_recommendations(
        self,
        business_context: BusinessContext,
        creator_profile: CreatorProfile
    ) -> List[Dict[str, Any]]:
        """Generate AI-powered recommendations for business context"""
        recommendations = []
        
        # Context-specific recommendations
        context_recommendations = await self.business_intelligence.generate_context_recommendations(
            business_context, creator_profile
        )
        
        # Cross-functional optimization recommendations
        optimization_recommendations = await self._generate_optimization_recommendations(
            business_context, creator_profile
        )
        
        # Risk mitigation recommendations
        risk_recommendations = await self._generate_risk_recommendations(
            business_context, creator_profile
        )
        
        recommendations.extend(context_recommendations)
        recommendations.extend(optimization_recommendations)
        recommendations.extend(risk_recommendations)
        
        return recommendations

    async def _analyze_context_interactions(
        self,
        contexts: List[BusinessContext]
    ) -> Dict[str, Any]:
        """Analyze interactions between business contexts"""
        interactions = {
            "compatible_pairs": [],
            "conflicting_pairs": [],
            "synergistic_pairs": [],
            "sequential_dependencies": [],
            "resource_conflicts": []
        }
        
        for i, context1 in enumerate(contexts):
            for context2 in contexts[i+1:]:
                interaction_type = self._determine_context_interaction(context1, context2)
                
                if interaction_type == "compatible":
                    interactions["compatible_pairs"].append((context1.context_id, context2.context_id))
                elif interaction_type == "conflicting":
                    interactions["conflicting_pairs"].append((context1.context_id, context2.context_id))
                elif interaction_type == "synergistic":
                    interactions["synergistic_pairs"].append((context1.context_id, context2.context_id))
                elif interaction_type == "sequential":
                    interactions["sequential_dependencies"].append((context1.context_id, context2.context_id))
                
                # Check resource conflicts
                if self._has_resource_conflict(context1, context2):
                    interactions["resource_conflicts"].append((context1.context_id, context2.context_id))
        
        return interactions

    def _determine_context_interaction(
        self,
        context1: BusinessContext,
        context2: BusinessContext
    ) -> str:
        """Determine interaction type between two contexts"""
        type1 = context1.context_type.value
        type2 = context2.context_type.value
        
        compatibility_rules = self.orchestration_rules["context_compatibility"]
        
        if type1 in compatibility_rules:
            if type2 in compatibility_rules[type1].get("compatible", []):
                return "compatible"
            elif type2 in compatibility_rules[type1].get("conflicting", []):
                return "conflicting"
            elif type2 in compatibility_rules[type1].get("synergistic", []):
                return "synergistic"
            elif type2 in compatibility_rules[type1].get("sequential", []):
                return "sequential"
        
        return "neutral"

    def _has_resource_conflict(
        self,
        context1: BusinessContext,
        context2: BusinessContext
    ) -> bool:
        """Check if two contexts have resource conflicts"""
        # Check time allocation conflicts
        total_time_allocation = sum(context1.time_allocation.values()) + sum(context2.time_allocation.values())
        if total_time_allocation > 1.0:  # More than 100% time allocation
            return True
        
        # Check budget conflicts
        total_budget = context1.allocated_budget + context2.allocated_budget
        # This would need creator's available budget information
        
        # Check skill requirement conflicts
        skill_overlap = set(context1.skill_requirements) & set(context2.skill_requirements)
        if len(skill_overlap) > 2:  # Significant skill overlap might indicate conflict
            return True
        
        return False

    async def _optimize_execution_plan(
        self,
        contexts: Dict[str, BusinessContext],
        interactions: Dict[str, Any],
        creator_profile: CreatorProfile
    ) -> List[Dict[str, Any]]:
        """Optimize execution plan for business contexts"""
        execution_plan = []
        
        # Sort contexts by priority
        sorted_contexts = sorted(
            contexts.values(),
            key=lambda x: x.priority.value,
            reverse=True
        )
        
        # Group compatible contexts
        context_groups = await self._group_compatible_contexts(
            sorted_contexts, interactions
        )
        
        # Optimize group execution order
        for group in context_groups:
            group_plan = await self._optimize_group_execution(group, creator_profile)
            execution_plan.extend(group_plan)
        
        return execution_plan

    async def _group_compatible_contexts(
        self,
        contexts: List[BusinessContext],
        interactions: Dict[str, Any]
    ) -> List[List[BusinessContext]]:
        """Group compatible contexts for parallel execution"""
        groups = []
        ungrouped_contexts = contexts.copy()
        
        while ungrouped_contexts:
            current_group = [ungrouped_contexts.pop(0)]
            
            # Find compatible contexts for current group
            for context in ungrouped_contexts[:]:
                can_add = True
                for group_context in current_group:
                    if (context.context_id, group_context.context_id) in interactions["conflicting_pairs"]:
                        can_add = False
                        break
                
                if can_add:
                    current_group.append(context)
                    ungrouped_contexts.remove(context)
            
            groups.append(current_group)
        
        return groups

    async def _optimize_group_execution(
        self,
        group: List[BusinessContext],
        creator_profile: CreatorProfile
    ) -> List[Dict[str, Any]]:
        """Optimize execution within a context group"""
        group_plan = []
        
        for context in group:
            execution_strategy = await self._determine_execution_strategy(
                context, creator_profile
            )
            
            group_plan.append({
                "context_id": context.context_id,
                "context_type": context.context_type.value,
                "priority": context.priority.value,
                "execution_strategy": execution_strategy,
                "estimated_duration": context.estimated_duration,
                "resource_allocation": {
                    "budget": context.allocated_budget,
                    "time": context.time_allocation,
                    "skills": context.skill_requirements
                }
            })
        
        return group_plan

    async def _determine_execution_strategy(
        self,
        context: BusinessContext,
        creator_profile: CreatorProfile
    ) -> Dict[str, Any]:
        """Determine optimal execution strategy for business context"""
        # Analyze creator capabilities
        creator_capabilities = await self.analytics_service.analyze_creator_capabilities(
            creator_profile.creator_id
        )
        
        # Determine automation opportunities
        automation_opportunities = await self._identify_automation_opportunities(
            context, creator_capabilities
        )
        
        # Determine collaboration needs
        collaboration_needs = await self._assess_collaboration_needs(
            context, creator_capabilities
        )
        
        # Generate execution timeline
        execution_timeline = await self._generate_execution_timeline(
            context, automation_opportunities, collaboration_needs
        )
        
        return {
            "automation_level": automation_opportunities.get("automation_level", "medium"),
            "collaboration_required": len(collaboration_needs) > 0,
            "collaboration_needs": collaboration_needs,
            "execution_timeline": execution_timeline,
            "success_probability": await self._calculate_success_probability(context, creator_profile)
        }

    async def update_context_progress(
        self,
        creator_id: str,
        context_id: str,
        progress_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update business context progress"""



        try:
            context = self.active_contexts.get(creator_id, {}).get(context_id)
            if not context:
                raise ValueError(f"Context {context_id} not found for creator {creator_id}")
            
            # Update progress
            if "completed_milestones" in progress_data:
                context.completed_milestones.extend(progress_data["completed_milestones"])
            
            if "new_blockers" in progress_data:
                context.blockers.extend(progress_data["new_blockers"])
            
            # Update last modified timestamp
            context.last_updated = datetime.now(timezone.utc)
            
            # Analyze progress impact
            progress_impact = await self._analyze_progress_impact(context, progress_data)
            
            # Generate updated recommendations
            updated_recommendations = await self._generate_progress_recommendations(
                context, progress_impact
            )
            
            # Update AI insights
            context.ai_recommendations = updated_recommendations
            
            # Store updates
            await self._store_business_context(context)
            
            return {
                "context_updated": True,
                "progress_impact": progress_impact,
                "updated_recommendations": updated_recommendations,
                "next_actions": progress_impact.get("next_actions", [])
            }
            
        except Exception as e:
            logger.error(f"Failed to update context progress: {e}")
            return {"error": str(e)}

    async def get_context_insights(
        self,
        creator_profile: CreatorProfile
    ) -> Dict[str, Any]:
        """Get comprehensive business context insights"""
        creator_contexts = self.active_contexts.get(creator_profile.creator_id, {})
        
        if not creator_contexts:
            return {"insights": [], "recommendations": []}
        
        # Analyze overall context performance
        performance_analysis = await self._analyze_context_performance(
            list(creator_contexts.values())
        )
        
        # Generate strategic insights
        strategic_insights = await self._generate_strategic_insights(
            creator_contexts, creator_profile
        )
        
        # Identify optimization opportunities
        optimization_opportunities = await self._identify_context_optimizations(
            creator_contexts, creator_profile
        )
        
        return {
            "performance_analysis": performance_analysis,
            "strategic_insights": strategic_insights,
            "optimization_opportunities": optimization_opportunities,
            "context_summary": {
                "total_contexts": len(creator_contexts),
                "active_contexts": len([c for c in creator_contexts.values() if c.status == ContextStatus.ACTIVE]),
                "high_priority_contexts": len([c for c in creator_contexts.values() if c.priority.value >= 3])
            }
        }

    async def _store_business_context(self, context: BusinessContext) -> None:
        """Store business context in database"""
        # Implementation for storing business context
        pass

    async def _define_success_criteria(
        self,
        context_type: BusinessContextType,
        objectives: List[BusinessObjective],
        business_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Define success criteria for business context"""
        # Implementation for defining success criteria
        return {}

    async def _analyze_resource_requirements(
        self,
        context_type: BusinessContextType,
        objectives: List[BusinessObjective],
        creator_profile: CreatorProfile
    ) -> Dict[str, Any]:
        """Analyze resource requirements for business context"""
        # Implementation for resource requirement analysis
        return {}

    async def _assess_revenue_impact(
        self,
        context_type: BusinessContextType,
        objectives: List[BusinessObjective],
        creator_profile: CreatorProfile
    ) -> float:
        """Assess revenue impact of business context"""
        # Implementation for revenue impact assessment
        return 3.0

    async def _assess_urgency(
        self,
        context_type: BusinessContextType,
        context_analysis: Dict[str, Any],
        creator_profile: CreatorProfile
    ) -> float:
        """Assess urgency of business context"""
        # Implementation for urgency assessment
        return 3.0

    async def _assess_resource_availability(
        self,
        creator_profile: CreatorProfile,
        resource_requirements: Dict[str, Any]
    ) -> float:
        """Assess resource availability for business context"""
        # Implementation for resource availability assessment
        return 3.0
