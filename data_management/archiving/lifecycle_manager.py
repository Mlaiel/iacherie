"""Archival Lifecycle Management Module

Manages the complete lifecycle of archived content including automatic transitions
between storage tiers, lifecycle policies enforcement, and stage management
for optimal cost and performance balance.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL / LEGAL WARNING ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
This code is the exclusive intellectual property of Fahed Mlaiel.
Toute utilisation non autorisée est strictement interdite.
Any unauthorized use is strictly prohibited.

Team Expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + 
Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod

from ..models import ArchiveEntry
from .archival_manager import ArchivalTier, ArchivalStatus
from .exceptions import ArchivalError


logger = logging.getLogger(__name__)


class LifecycleStage(Enum):
    """
Archive lifecycle stages"""

    ACTIVE = "active"
    TRANSITIONING = "transitioning"
    COLD = "cold"
    FROZEN = "frozen"
    DEEP_ARCHIVE = "deep_archive"
    EXPIRED = "expired"


class TransitionTrigger(Enum):
    """Lifecycle transition triggers"""

    AGE_BASED = "age_based"
    ACCESS_BASED = "access_based"
    SIZE_BASED = "size_based"
    COST_BASED = "cost_based"
    COMPLIANCE_BASED = "compliance_based"
    MANUAL = "manual"


@dataclass
class TransitionRule:
    """Defines rules for lifecycle transitions"""
    rule_id: str
    name: str
    description: str
    
    # Source and target
    from_stage: LifecycleStage
    to_stage: LifecycleStage
    
    # Trigger conditions
    trigger_type: TransitionTrigger
    conditions: Dict[str, Any]
    
    # Priority and execution
    priority: int = 100
    enabled: bool = True
    
    # Timing
    min_age_days: Optional[int] = None
    max_idle_days: Optional[int] = None
    
    # Content filters
    content_types: Optional[Set[str]] = None
    size_min_bytes: Optional[int] = None
    size_max_bytes: Optional[int] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


@dataclass
class LifecyclePolicy:
    """
Complete lifecycle management policy"""
    policy_id: str
    name: str
    description: str
    
    # Rules and configuration
    transition_rules: List[TransitionRule] = field(default_factory=list)
    retention_days: Optional[int] = None
    auto_cleanup: bool = True
    
    # Execution settings
    enabled: bool = True
    schedule_cron: str = "0 2 * * *"  # Daily at 2 AM
    max_concurrent_transitions: int = 10
    
    # Cost optimization
    cost_optimization_enabled: bool = True
    target_cost_reduction: float = 0.3  # 30% cost reduction target
    
    # Monitoring
    notification_enabled: bool = True
    notification_channels: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


@dataclass
class LifecycleTransition:
    """Represents an ongoing or completed transition"""
    transition_id: str
    archive_id: str
    rule_id: str
    
    # Transition details
    from_stage: LifecycleStage
    to_stage: LifecycleStage
    from_tier: ArchivalTier
    to_tier: ArchivalTier
    
    # Status and timing
    status: str = "pending"  # pending, in_progress, completed, failed
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Progress and metrics
    progress_percentage: float = 0.0
    estimated_completion: Optional[datetime] = None
    cost_impact: Optional[float] = None
    
    # Error handling
    error_message: Optional[str] = None
    retry_count: int = 0
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)


class LifecycleStageManager(ABC):
    """Abstract base for stage-specific management"""
    
    @abstractmethod
    async def can_transition_to(self, stage: LifecycleStage, entry: ArchiveEntry) -> bool:
        """
Check if transition to stage is possible"""
        pass
    
    @abstractmethod
    async def transition_to_stage(self, entry: ArchiveEntry, target_stage: LifecycleStage) -> bool:
        """
Execute transition to target stage"""
        pass
    
    @abstractmethod
    async def get_stage_cost(self, entry: ArchiveEntry) -> float:
        """
Calculate storage cost for this stage"""
        pass


class ActiveStageManager(LifecycleStageManager):
    """
Manages active stage operations"""
    
    async def can_transition_to(self, stage: LifecycleStage, entry: ArchiveEntry) -> bool:
        """
Active stage can transition to any other stage"""
        return stage in [LifecycleStage.COLD, LifecycleStage.FROZEN, LifecycleStage.DEEP_ARCHIVE]
    
    async def transition_to_stage(self, entry: ArchiveEntry, target_stage: LifecycleStage) -> bool:
        """
Execute transition from active stage"""
        logger.info(f"Transitioning archive {entry.archive_id} from ACTIVE to {target_stage}")
        
        # Update storage tier based on target stage
        tier_mapping = {
            LifecycleStage.COLD: ArchivalTier.COLD,
            LifecycleStage.FROZEN: ArchivalTier.FROZEN,
            LifecycleStage.DEEP_ARCHIVE: ArchivalTier.DEEP_ARCHIVE
        }
        
        if target_stage in tier_mapping:
            entry.storage_tier = tier_mapping[target_stage]
            entry.updated_at = datetime.utcnow()
            return True
        
        return False
    
    async def get_stage_cost(self, entry: ArchiveEntry) -> float:
        """Calculate active stage storage cost"""
        return entry.compressed_size * 0.023 / (1024**3) * 30  # $0.023/GB/month


class ColdStageManager(LifecycleStageManager):
    """
Manages cold storage stage operations"""
    
    async def can_transition_to(self, stage: LifecycleStage, entry: ArchiveEntry) -> bool:
        """
Cold stage can transition to frozen or deep archive"""
        return stage in [LifecycleStage.FROZEN, LifecycleStage.DEEP_ARCHIVE, LifecycleStage.ACTIVE]
    
    async def transition_to_stage(self, entry: ArchiveEntry, target_stage: LifecycleStage) -> bool:
        """
Execute transition from cold stage"""
        logger.info(f"Transitioning archive {entry.archive_id} from COLD to {target_stage}")
        
        tier_mapping = {
            LifecycleStage.ACTIVE: ArchivalTier.HOT,
            LifecycleStage.FROZEN: ArchivalTier.FROZEN,
            LifecycleStage.DEEP_ARCHIVE: ArchivalTier.DEEP_ARCHIVE
        }
        
        if target_stage in tier_mapping:
            entry.storage_tier = tier_mapping[target_stage]
            entry.updated_at = datetime.utcnow()
            return True
        
        return False
    
    async def get_stage_cost(self, entry: ArchiveEntry) -> float:
        """Calculate cold stage storage cost"""
        return entry.compressed_size * 0.0125 / (1024**3) * 30  # $0.0125/GB/month


class FrozenStageManager(LifecycleStageManager):
    """
Manages frozen storage stage operations"""
    
    async def can_transition_to(self, stage: LifecycleStage, entry: ArchiveEntry) -> bool:
        """
Frozen stage can transition to deep archive or back to cold/active"""
        return stage in [LifecycleStage.DEEP_ARCHIVE, LifecycleStage.COLD, LifecycleStage.ACTIVE]
    
    async def transition_to_stage(self, entry: ArchiveEntry, target_stage: LifecycleStage) -> bool:
        """
Execute transition from frozen stage"""
        logger.info(f"Transitioning archive {entry.archive_id} from FROZEN to {target_stage}")
        
        tier_mapping = {
            LifecycleStage.ACTIVE: ArchivalTier.HOT,
            LifecycleStage.COLD: ArchivalTier.COLD,
            LifecycleStage.DEEP_ARCHIVE: ArchivalTier.DEEP_ARCHIVE
        }
        
        if target_stage in tier_mapping:
            entry.storage_tier = tier_mapping[target_stage]
            entry.updated_at = datetime.utcnow()
            return True
        
        return False
    
    async def get_stage_cost(self, entry: ArchiveEntry) -> float:
        """Calculate frozen stage storage cost"""
        return entry.compressed_size * 0.004 / (1024**3) * 30  # $0.004/GB/month


class DeepArchiveStageManager(LifecycleStageManager):
    """
Manages deep archive stage operations"""
    
    async def can_transition_to(self, stage: LifecycleStage, entry: ArchiveEntry) -> bool:
        """
Deep archive can transition back to any stage but with cost implications"""
        return stage in [LifecycleStage.ACTIVE, LifecycleStage.COLD, LifecycleStage.FROZEN, LifecycleStage.EXPIRED]
    
    async def transition_to_stage(self, entry: ArchiveEntry, target_stage: LifecycleStage) -> bool:
        """
Execute transition from deep archive stage"""
        logger.info(f"Transitioning archive {entry.archive_id} from DEEP_ARCHIVE to {target_stage}")
        
        if target_stage == LifecycleStage.EXPIRED:
            entry.status = ArchivalStatus.EXPIRED
            entry.expires_at = datetime.utcnow()
            return True
        
        tier_mapping = {
            LifecycleStage.ACTIVE: ArchivalTier.HOT,
            LifecycleStage.COLD: ArchivalTier.COLD,
            LifecycleStage.FROZEN: ArchivalTier.FROZEN
        }
        
        if target_stage in tier_mapping:
            entry.storage_tier = tier_mapping[target_stage]
            entry.updated_at = datetime.utcnow()
            return True
        
        return False
    
    async def get_stage_cost(self, entry: ArchiveEntry) -> float:
        """Calculate deep archive stage storage cost"""
        return entry.compressed_size * 0.00099 / (1024**3) * 30  # $0.00099/GB/month


class ArchivalLifecycleManager:
    """
    Advanced lifecycle management for archived content.
    
    Handles automated transitions between storage tiers based on access patterns,
    age, cost optimization, and compliance requirements.
    """
    
    def __init__(self):
        self.policies: Dict[str, LifecyclePolicy] = {}
        self.active_transitions: Dict[str, LifecycleTransition] = {}
        
        # Stage managers
        self.stage_managers = {
            LifecycleStage.ACTIVE: ActiveStageManager(),
            LifecycleStage.COLD: ColdStageManager(),
            LifecycleStage.FROZEN: FrozenStageManager(),
            LifecycleStage.DEEP_ARCHIVE: DeepArchiveStageManager()
        }
        
        # Configuration
        self.max_concurrent_transitions = 10
        self.transition_timeout_hours = 24
        
        logger.info("Archival Lifecycle Manager initialized")
    
    async def add_policy(self, policy: LifecyclePolicy) -> bool:
        """Add a new lifecycle policy"""
        try:
            # Validate policy
            if not await self._validate_policy(policy):
                raise ArchivalError(f"Invalid lifecycle policy: {policy.policy_id}")
            
            self.policies[policy.policy_id] = policy
            logger.info(f"Added lifecycle policy: {policy.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add lifecycle policy: {e}")
            return False
    
    async def remove_policy(self, policy_id: str) -> bool:
        """Remove a lifecycle policy"""
        try:
            if policy_id in self.policies:
                del self.policies[policy_id]
                logger.info(f"Removed lifecycle policy: {policy_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to remove lifecycle policy: {e}")
            return False
    
    async def evaluate_transitions(self, entries: List[ArchiveEntry]) -> List[LifecycleTransition]:
        """Evaluate entries for potential lifecycle transitions"""
        try:
            transitions = []
            
            for entry in entries:
                for policy in self.policies.values():
                    if not policy.enabled:
                        continue
                    
                    # Check each transition rule
                    for rule in policy.transition_rules:
                        if not rule.enabled:
                            continue
                        
                        if await self._should_transition(entry, rule):
                            transition = await self._create_transition(entry, rule)
                            transitions.append(transition)
                            break  # Only one transition per entry per evaluation
            
            return transitions
            
        except Exception as e:
            logger.error(f"Failed to evaluate transitions: {e}")
            return []
    
    async def execute_transition(self, transition: LifecycleTransition) -> bool:
        """Execute a lifecycle transition"""
        try:
            transition.status = "in_progress"
            transition.started_at = datetime.utcnow()
            self.active_transitions[transition.transition_id] = transition
            
            # Get source and target stage managers
            source_manager = self.stage_managers.get(transition.from_stage)
            target_manager = self.stage_managers.get(transition.to_stage)
            
            if not source_manager or not target_manager:
                raise ArchivalError(f"No manager found for transition {transition.from_stage} -> {transition.to_stage}")
            
            # Create mock entry for transition (in real implementation, fetch from database)
            entry = ArchiveEntry(
                archive_id=transition.archive_id,
                content_id=f"content_{transition.archive_id}",
                content_type="unknown",
                original_size=0,
                compressed_size=0,
                compression_ratio=1.0,
                storage_tier=transition.from_tier,
                archive_path=f"/archive/{transition.archive_id}"
            )
            
            # Check if transition is possible
            if not await source_manager.can_transition_to(transition.to_stage, entry):
                raise ArchivalError(f"Cannot transition from {transition.from_stage} to {transition.to_stage}")
            
            # Execute the transition
            success = await source_manager.transition_to_stage(entry, transition.to_stage)
            
            if success:
                transition.status = "completed"
                transition.completed_at = datetime.utcnow()
                transition.progress_percentage = 100.0
                
                # Calculate cost impact
                old_cost = await source_manager.get_stage_cost(entry)
                new_cost = await target_manager.get_stage_cost(entry)
                transition.cost_impact = new_cost - old_cost
                
                logger.info(f"Successfully completed transition {transition.transition_id}")
            else:
                transition.status = "failed"
                transition.error_message = "Transition execution failed"
                logger.error(f"Failed to execute transition {transition.transition_id}")
            
            return success
            
        except Exception as e:
            transition.status = "failed"
            transition.error_message = str(e)
            logger.error(f"Failed to execute transition {transition.transition_id}: {e}")
            return False
        
        finally:
            if transition.transition_id in self.active_transitions:
                del self.active_transitions[transition.transition_id]
    
    async def get_lifecycle_status(self, archive_id: str) -> Dict[str, Any]:
        """Get detailed lifecycle status for an archive"""
        try:
            # In real implementation, fetch from database
            return {
                "archive_id": archive_id,
                "current_stage": "active",
                "current_tier": "hot",
                "next_transition": None,
                "cost_per_month": 0.0,
                "access_count_30d": 0,
                "last_accessed": None,
                "eligible_transitions": []
            }
            
        except Exception as e:
            logger.error(f"Failed to get lifecycle status for {archive_id}: {e}")
            return {}
    
    async def optimize_costs(self, target_reduction: float = 0.3) -> Dict[str, Any]:
        """Analyze and recommend cost optimization strategies"""
        try:
            # Analyze current storage costs and usage patterns
            current_cost = 0.0
            potential_savings = 0.0
            recommendations = []
            
            # Mock cost analysis (in real implementation, query database)
            for policy in self.policies.values():
                if policy.cost_optimization_enabled:
                    policy_savings = current_cost * target_reduction * 0.1
                    potential_savings += policy_savings
                    
                    recommendations.append({
                        "policy_id": policy.policy_id,
                        "description": f"Apply {policy.name} for additional cost savings",
                        "estimated_savings": policy_savings,
                        "implementation_effort": "low"
                    })
            
            return {
                "current_monthly_cost": current_cost,
                "target_reduction": target_reduction,
                "potential_savings": potential_savings,
                "recommendations": recommendations,
                "analysis_date": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to optimize costs: {e}")
            return {}
    
    async def _validate_policy(self, policy: LifecyclePolicy) -> bool:
        """Validate lifecycle policy configuration"""
        try:
            # Check basic policy structure
            if not policy.policy_id or not policy.name:
                return False
            
            # Validate transition rules
            for rule in policy.transition_rules:
                if not await self._validate_transition_rule(rule):
                    return False
            
            # Check for rule conflicts
            if await self._has_conflicting_rules(policy.transition_rules):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Policy validation failed: {e}")
            return False
    
    async def _validate_transition_rule(self, rule: TransitionRule) -> bool:
        """Validate individual transition rule"""
        try:
            # Check stage compatibility
            if rule.from_stage == rule.to_stage:
                return False
            
            # Validate stage manager availability
            if rule.from_stage not in self.stage_managers:
                return False
            
            if rule.to_stage not in self.stage_managers:
                return False
            
            # Check rule conditions
            if not rule.conditions:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Rule validation failed: {e}")
            return False
    
    async def _has_conflicting_rules(self, rules: List[TransitionRule]) -> bool:
        """Check for conflicting transition rules"""
        try:
            # Group rules by source stage
            stage_rules = {}
            for rule in rules:
                if rule.from_stage not in stage_rules:
                    stage_rules[rule.from_stage] = []
                stage_rules[rule.from_stage].append(rule)
            
            # Check for conflicts within each stage group
            for stage, stage_rule_list in stage_rules.items():
                if len(stage_rule_list) > 1:
                    # Multiple rules for same source stage - check priorities
                    priorities = [rule.priority for rule in stage_rule_list]
                    if len(set(priorities)) != len(priorities):
                        return True  # Duplicate priorities = conflict
            
            return False
            
        except Exception as e:
            logger.error(f"Conflict detection failed: {e}")
            return True  # Assume conflict on error
    
    async def _should_transition(self, entry: ArchiveEntry, rule: TransitionRule) -> bool:
        """Determine if an entry should transition according to a rule"""
        try:
            # Check content type filter
            if rule.content_types and entry.content_type not in rule.content_types:
                return False
            
            # Check size constraints
            if rule.size_min_bytes and entry.compressed_size < rule.size_min_bytes:
                return False
            if rule.size_max_bytes and entry.compressed_size > rule.size_max_bytes:
                return False
            
            # Check age constraints
            if rule.min_age_days:
                min_age = datetime.utcnow() - timedelta(days=rule.min_age_days)
                if entry.created_at > min_age:
                    return False
            
            # Check idle time
            if rule.max_idle_days and entry.accessed_at:
                max_idle = datetime.utcnow() - timedelta(days=rule.max_idle_days)
                if entry.accessed_at > max_idle:
                    return False
            
            # Check trigger-specific conditions
            return await self._evaluate_trigger_conditions(entry, rule)
            
        except Exception as e:
            logger.error(f"Failed to evaluate transition conditions: {e}")
            return False
    
    async def _evaluate_trigger_conditions(self, entry: ArchiveEntry, rule: TransitionRule) -> bool:
        """Evaluate trigger-specific conditions"""
        try:
            if rule.trigger_type == TransitionTrigger.AGE_BASED:
                return await self._evaluate_age_trigger(entry, rule)
            elif rule.trigger_type == TransitionTrigger.ACCESS_BASED:
                return await self._evaluate_access_trigger(entry, rule)
            elif rule.trigger_type == TransitionTrigger.SIZE_BASED:
                return await self._evaluate_size_trigger(entry, rule)
            elif rule.trigger_type == TransitionTrigger.COST_BASED:
                return await self._evaluate_cost_trigger(entry, rule)
            elif rule.trigger_type == TransitionTrigger.COMPLIANCE_BASED:
                return await self._evaluate_compliance_trigger(entry, rule)
            elif rule.trigger_type == TransitionTrigger.MANUAL:
                return False  # Manual triggers require explicit action
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to evaluate trigger conditions: {e}")
            return False
    
    async def _evaluate_age_trigger(self, entry: ArchiveEntry, rule: TransitionRule) -> bool:
        """Evaluate age-based trigger conditions"""
        age_threshold = rule.conditions.get("age_days", 30)
        entry_age = (datetime.utcnow() - entry.created_at).days
        return entry_age >= age_threshold
    
    async def _evaluate_access_trigger(self, entry: ArchiveEntry, rule: TransitionRule) -> bool:
        """Evaluate access-based trigger conditions"""
        idle_threshold = rule.conditions.get("idle_days", 90)
        if not entry.accessed_at:
            return True  # Never accessed
        
        idle_days = (datetime.utcnow() - entry.accessed_at).days
        return idle_days >= idle_threshold
    
    async def _evaluate_size_trigger(self, entry: ArchiveEntry, rule: TransitionRule) -> bool:
        """Evaluate size-based trigger conditions"""
        size_threshold = rule.conditions.get("size_bytes", 1024**3)  # 1GB default
        return entry.compressed_size >= size_threshold
    
    async def _evaluate_cost_trigger(self, entry: ArchiveEntry, rule: TransitionRule) -> bool:
        """Evaluate cost-based trigger conditions"""
        cost_threshold = rule.conditions.get("monthly_cost", 10.0)
        
        # Calculate current monthly cost (simplified)
        current_cost = entry.compressed_size * 0.023 / (1024**3) * 30
        return current_cost >= cost_threshold
    
    async def _evaluate_compliance_trigger(self, entry: ArchiveEntry, rule: TransitionRule) -> bool:
        """Evaluate compliance-based trigger conditions"""
        retention_days = rule.conditions.get("retention_days", 2555)  # 7 years default
        age_days = (datetime.utcnow() - entry.created_at).days
        return age_days >= retention_days
    
    async def _create_transition(self, entry: ArchiveEntry, rule: TransitionRule) -> LifecycleTransition:
        """Create a lifecycle transition from rule and entry"""
        # Determine current and target stages based on storage tier
        tier_to_stage = {
            ArchivalTier.HOT: LifecycleStage.ACTIVE,
            ArchivalTier.COLD: LifecycleStage.COLD,
            ArchivalTier.FROZEN: LifecycleStage.FROZEN,
            ArchivalTier.DEEP_ARCHIVE: LifecycleStage.DEEP_ARCHIVE
        }
        
        current_stage = tier_to_stage.get(entry.storage_tier, LifecycleStage.ACTIVE)
        
        # Generate transition ID
        transition_id = f"trans_{entry.archive_id}_{rule.rule_id}_{int(datetime.utcnow().timestamp())}"
        
        return LifecycleTransition(
            transition_id=transition_id,
            archive_id=entry.archive_id,
            rule_id=rule.rule_id,
            from_stage=current_stage,
            to_stage=rule.to_stage,
            from_tier=entry.storage_tier,
            to_tier=self._get_tier_for_stage(rule.to_stage)
        )
    
    def _get_tier_for_stage(self, stage: LifecycleStage) -> ArchivalTier:
        """Map lifecycle stage to storage tier"""
        stage_to_tier = {
            LifecycleStage.ACTIVE: ArchivalTier.HOT,
            LifecycleStage.COLD: ArchivalTier.COLD,
            LifecycleStage.FROZEN: ArchivalTier.FROZEN,
            LifecycleStage.DEEP_ARCHIVE: ArchivalTier.DEEP_ARCHIVE
        }
        return stage_to_tier.get(stage, ArchivalTier.HOT)
