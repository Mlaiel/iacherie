"""
Multi-Intent Resolution System

Advanced system for handling complex scenarios with multiple intentions,
intent conflicts, priority management, and intelligent resolution strategies.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written 
permission is strictly prohibited and will be prosecuted to the full extent of the law.
Contact: mlaiel@live.de
"""

import asyncio
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import logging
import numpy as np

from ...core.base_service import BaseService
from .intent_classifier import IntentCategory, ClassificationResult, IntentConfidence
from .config import IntentRecognitionConfig
from .exceptions import ClassificationError


class IntentPriority(Enum):
    """Intent priority levels for conflict resolution"""
    CRITICAL = 1    # Security, urgent issues
    HIGH = 2        # Core business functions
    MEDIUM = 3      # Standard operations
    LOW = 4         # Optional features
    BACKGROUND = 5  # Background processes


class ResolutionStrategy(Enum):
    """Strategies for resolving intent conflicts"""
    HIGHEST_CONFIDENCE = "highest_confidence"
    PRIORITY_BASED = "priority_based"
    CONTEXT_AWARE = "context_aware"
    USER_PREFERENCE = "user_preference"
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"


@dataclass
class IntentCandidate:
    """Individual intent candidate with metadata"""
    intent: IntentCategory
    confidence: float
    priority: IntentPriority
    context_relevance: float = 0.5
    user_preference_score: float = 0.5
    temporal_relevance: float = 0.5
    dependency_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MultiIntentResult:
    """Result of multi-intent resolution"""
    primary_intent: IntentCategory
    secondary_intents: List[IntentCategory] = field(default_factory=list)
    resolution_strategy: ResolutionStrategy = ResolutionStrategy.HIGHEST_CONFIDENCE
    execution_order: List[IntentCategory] = field(default_factory=list)
    conflicts_detected: List[str] = field(default_factory=list)
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    resolution_metadata: Dict[str, Any] = field(default_factory=dict)


class IntentPriorityManager:
    """
    Manages intent priorities and dependency relationships
    
    Features:
    - Dynamic priority assignment
    - Intent dependency mapping
    - Context-aware priority adjustment
    - User preference integration
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Intent priority mapping
        self.intent_priorities = self._initialize_intent_priorities()
        
        # Intent dependencies
        self.intent_dependencies = self._initialize_intent_dependencies()
        
        # Context priority modifiers
        self.context_modifiers = self._initialize_context_modifiers()
    
    def _initialize_intent_priorities(self) -> Dict[IntentCategory, IntentPriority]:
        """Initialize default intent priorities"""
        return {
            # Critical priorities (security, urgent issues)
            IntentCategory.PROTECTION_REPORT: IntentPriority.CRITICAL,
            IntentCategory.PROTECTION_TAKEDOWN: IntentPriority.CRITICAL,
            IntentCategory.HELP_TROUBLESHOOT: IntentPriority.CRITICAL,
            
            # High priorities (core business functions)
            IntentCategory.CONTENT_UPLOAD: IntentPriority.HIGH,
            IntentCategory.PROTECTION_FINGERPRINT: IntentPriority.HIGH,
            IntentCategory.MONETIZATION_PAYOUT: IntentPriority.HIGH,
            IntentCategory.COLLABORATION_WORKFLOW: IntentPriority.HIGH,
            
            # Medium priorities (standard operations)
            IntentCategory.CONTENT_EDIT: IntentPriority.MEDIUM,
            IntentCategory.CONTENT_ENHANCE: IntentPriority.MEDIUM,
            IntentCategory.ANALYTICS_PERFORMANCE: IntentPriority.MEDIUM,
            IntentCategory.PLATFORM_DISTRIBUTE: IntentPriority.MEDIUM,
            IntentCategory.COLLABORATION_SHARE: IntentPriority.MEDIUM,
            
            # Low priorities (optional features)
            IntentCategory.CONTENT_ORGANIZE: IntentPriority.LOW,
            IntentCategory.ANALYTICS_TRENDS: IntentPriority.LOW,
            IntentCategory.PLATFORM_OPTIMIZE: IntentPriority.LOW,
            
            # Background priorities
            IntentCategory.ANALYTICS_FORECAST: IntentPriority.BACKGROUND,
            IntentCategory.PLATFORM_SYNC: IntentPriority.BACKGROUND
        }
    
    def _initialize_intent_dependencies(self) -> Dict[IntentCategory, List[IntentCategory]]:
        """Initialize intent dependency relationships"""
        return {
            # Content workflow dependencies
            IntentCategory.CONTENT_ENHANCE: [IntentCategory.CONTENT_UPLOAD],
            IntentCategory.PROTECTION_FINGERPRINT: [IntentCategory.CONTENT_UPLOAD],
            IntentCategory.PLATFORM_DISTRIBUTE: [IntentCategory.CONTENT_UPLOAD],
            
            # Protection workflow dependencies
            IntentCategory.PROTECTION_MONITOR: [IntentCategory.PROTECTION_FINGERPRINT],
            IntentCategory.PROTECTION_REPORT: [IntentCategory.PROTECTION_MONITOR],
            IntentCategory.PROTECTION_TAKEDOWN: [IntentCategory.PROTECTION_REPORT],
            
            # Monetization dependencies
            IntentCategory.MONETIZATION_LICENSE: [IntentCategory.PROTECTION_FINGERPRINT],
            IntentCategory.MONETIZATION_TRACK: [IntentCategory.MONETIZATION_LICENSE],
            IntentCategory.MONETIZATION_PAYOUT: [IntentCategory.MONETIZATION_TRACK],
            
            # Analytics dependencies
            IntentCategory.ANALYTICS_AUDIENCE: [IntentCategory.ANALYTICS_PERFORMANCE],
            IntentCategory.ANALYTICS_TRENDS: [IntentCategory.ANALYTICS_PERFORMANCE],
            IntentCategory.ANALYTICS_FORECAST: [IntentCategory.ANALYTICS_TRENDS],
            
            # Collaboration dependencies
            IntentCategory.COLLABORATION_PERMISSION: [IntentCategory.COLLABORATION_INVITE],
            IntentCategory.COLLABORATION_WORKFLOW: [IntentCategory.COLLABORATION_PERMISSION]
        }
    
    def _initialize_context_modifiers(self) -> Dict[str, Dict[IntentCategory, float]]:
        """Initialize context-based priority modifiers"""
        return {
            'urgent_context': {
                IntentCategory.PROTECTION_REPORT: 1.5,
                IntentCategory.PROTECTION_TAKEDOWN: 1.5,
                IntentCategory.HELP_TROUBLESHOOT: 1.3,
                IntentCategory.MONETIZATION_PAYOUT: 1.2
            },
            'creative_session': {
                IntentCategory.CONTENT_UPLOAD: 1.3,
                IntentCategory.CONTENT_EDIT: 1.2,
                IntentCategory.CONTENT_ENHANCE: 1.2,
                IntentCategory.CONTENT_GENERATE: 1.1
            },
            'business_hours': {
                IntentCategory.COLLABORATION_INVITE: 1.2,
                IntentCategory.COLLABORATION_WORKFLOW: 1.2,
                IntentCategory.ANALYTICS_PERFORMANCE: 1.1
            },
            'new_user': {
                IntentCategory.HELP_SUPPORT: 1.4,
                IntentCategory.HELP_TUTORIAL: 1.3,
                IntentCategory.CONTENT_UPLOAD: 1.2
            }
        }
    
    def get_intent_priority(
        self,
        intent: IntentCategory,
        context: Optional[Dict[str, Any]] = None
    ) -> IntentPriority:
        """Get priority for intent with context adjustments"""
        base_priority = self.intent_priorities.get(intent, IntentPriority.MEDIUM)
        
        if not context:
            return base_priority
        
        # Apply context modifiers
        priority_value = base_priority.value
        
        for context_type, modifiers in self.context_modifiers.items():
            if context.get(context_type) and intent in modifiers:
                modifier = modifiers[intent]
                priority_value = max(1, priority_value / modifier)  # Lower value = higher priority
        
        # Convert back to priority enum
        adjusted_value = round(priority_value)
        for priority in IntentPriority:
            if priority.value == adjusted_value:
                return priority
        
        return base_priority
    
    def check_intent_dependencies(
        self,
        target_intent: IntentCategory,
        completed_intents: List[IntentCategory]
    ) -> Tuple[bool, List[IntentCategory]]:
        """Check if intent dependencies are satisfied"""
        dependencies = self.intent_dependencies.get(target_intent, [])
        missing_dependencies = [dep for dep in dependencies if dep not in completed_intents]
        
        return len(missing_dependencies) == 0, missing_dependencies
    
    def calculate_dependency_score(
        self,
        intent: IntentCategory,
        completed_intents: List[IntentCategory],
        pending_intents: List[IntentCategory]
    ) -> float:
        """Calculate dependency satisfaction score"""
        dependencies = self.intent_dependencies.get(intent, [])
        
        if not dependencies:
            return 1.0  # No dependencies = fully satisfied
        
        satisfied_count = sum(1 for dep in dependencies if dep in completed_intents)
        pending_count = sum(1 for dep in dependencies if dep in pending_intents)
        
        # Score based on satisfied and pending dependencies
        total_deps = len(dependencies)
        satisfaction_score = satisfied_count / total_deps
        pending_penalty = (pending_count / total_deps) * 0.5
        
        return max(0.0, satisfaction_score - pending_penalty)


class IntentConflictResolver:
    """
    Resolves conflicts between competing intents
    
    Features:
    - Conflict detection algorithms
    - Multiple resolution strategies
    - Context-aware decision making
    - User preference integration
    """
    
    def __init__(self, priority_manager: IntentPriorityManager):
        self.priority_manager = priority_manager
        self.logger = logging.getLogger(__name__)
        
        # Conflict rules
        self.conflict_rules = self._initialize_conflict_rules()
        
        # Resolution weights
        self.resolution_weights = {
            'confidence': 0.3,
            'priority': 0.25,
            'context': 0.2,
            'user_preference': 0.15,
            'temporal': 0.1
        }
    
    def _initialize_conflict_rules(self) -> Dict[str, List[Tuple[IntentCategory, IntentCategory]]]:
        """Initialize intent conflict rules"""
        return {
            'mutually_exclusive': [
                (IntentCategory.CONTENT_DELETE, IntentCategory.CONTENT_ENHANCE),
                (IntentCategory.CONTENT_DELETE, IntentCategory.PLATFORM_DISTRIBUTE),
                (IntentCategory.PROTECTION_TAKEDOWN, IntentCategory.MONETIZATION_LICENSE)
            ],
            'resource_conflicts': [
                (IntentCategory.CONTENT_UPLOAD, IntentCategory.CONTENT_GENERATE),
                (IntentCategory.ANALYTICS_PERFORMANCE, IntentCategory.ANALYTICS_FORECAST)
            ],
            'timing_conflicts': [
                (IntentCategory.CONTENT_EDIT, IntentCategory.PLATFORM_DISTRIBUTE),
                (IntentCategory.PROTECTION_CONFIGURE, IntentCategory.PROTECTION_MONITOR)
            ]
        }
    
    def detect_conflicts(
        self,
        intent_candidates: List[IntentCandidate]
    ) -> List[str]:
        """Detect conflicts between intent candidates"""
        conflicts = []
        
        for i, candidate1 in enumerate(intent_candidates):
            for j, candidate2 in enumerate(intent_candidates[i+1:], i+1):
                conflict_type = self._check_intent_conflict(
                    candidate1.intent, 
                    candidate2.intent
                )
                
                if conflict_type:
                    conflicts.append(
                        f"{conflict_type}: {candidate1.intent.value} vs {candidate2.intent.value}"
                    )
        
        return conflicts
    
    def _check_intent_conflict(
        self,
        intent1: IntentCategory,
        intent2: IntentCategory
    ) -> Optional[str]:
        """Check if two intents conflict"""
        for conflict_type, conflict_pairs in self.conflict_rules.items():
            for pair in conflict_pairs:
                if (intent1, intent2) in [pair, pair[::-1]]:
                    return conflict_type
        
        return None
    
    def resolve_conflicts(
        self,
        intent_candidates: List[IntentCandidate],
        strategy: ResolutionStrategy,
        context: Optional[Dict[str, Any]] = None
    ) -> MultiIntentResult:
        """Resolve conflicts using specified strategy"""
        
        try:
            if strategy == ResolutionStrategy.HIGHEST_CONFIDENCE:
                return self._resolve_by_confidence(intent_candidates)
            
            elif strategy == ResolutionStrategy.PRIORITY_BASED:
                return self._resolve_by_priority(intent_candidates, context)
            
            elif strategy == ResolutionStrategy.CONTEXT_AWARE:
                return self._resolve_by_context(intent_candidates, context)
            
            elif strategy == ResolutionStrategy.USER_PREFERENCE:
                return self._resolve_by_user_preference(intent_candidates, context)
            
            elif strategy == ResolutionStrategy.SEQUENTIAL:
                return self._resolve_sequential(intent_candidates, context)
            
            elif strategy == ResolutionStrategy.PARALLEL:
                return self._resolve_parallel(intent_candidates, context)
            
            else:
                # Default to confidence-based
                return self._resolve_by_confidence(intent_candidates)
                
        except Exception as e:
            self.logger.error(f"Conflict resolution failed: {str(e)}")
            
            # Fallback to simple resolution
            if intent_candidates:
                primary = max(intent_candidates, key=lambda x: x.confidence)
                return MultiIntentResult(
                    primary_intent=primary.intent,
                    resolution_strategy=strategy,
                    conflicts_detected=["Resolution error - using fallback"]
                )
            else:
                raise ClassificationError("No valid intent candidates for resolution")
    
    def _resolve_by_confidence(
        self,
        candidates: List[IntentCandidate]
    ) -> MultiIntentResult:
        """Resolve by highest confidence scores"""
        sorted_candidates = sorted(candidates, key=lambda x: x.confidence, reverse=True)
        
        primary = sorted_candidates[0]
        secondary = [c.intent for c in sorted_candidates[1:3]]  # Top 2 secondary
        
        confidence_scores = {c.intent.value: c.confidence for c in candidates}
        
        return MultiIntentResult(
            primary_intent=primary.intent,
            secondary_intents=secondary,
            resolution_strategy=ResolutionStrategy.HIGHEST_CONFIDENCE,
            confidence_scores=confidence_scores,
            execution_order=[c.intent for c in sorted_candidates]
        )
    
    def _resolve_by_priority(
        self,
        candidates: List[IntentCandidate],
        context: Optional[Dict[str, Any]] = None
    ) -> MultiIntentResult:
        """Resolve by intent priorities"""
        
        # Update priorities with context
        for candidate in candidates:
            candidate.priority = self.priority_manager.get_intent_priority(
                candidate.intent, context
            )
        
        # Sort by priority (lower value = higher priority)
        sorted_candidates = sorted(candidates, key=lambda x: x.priority.value)
        
        primary = sorted_candidates[0]
        secondary = [c.intent for c in sorted_candidates[1:3]]
        
        conflicts = self.detect_conflicts(candidates)
        
        return MultiIntentResult(
            primary_intent=primary.intent,
            secondary_intents=secondary,
            resolution_strategy=ResolutionStrategy.PRIORITY_BASED,
            conflicts_detected=conflicts,
            execution_order=[c.intent for c in sorted_candidates]
        )
    
    def _resolve_by_context(
        self,
        candidates: List[IntentCandidate],
        context: Optional[Dict[str, Any]] = None
    ) -> MultiIntentResult:
        """Resolve using context-aware scoring"""
        
        # Calculate composite scores
        for candidate in candidates:
            score = (
                candidate.confidence * self.resolution_weights['confidence'] +
                (5 - candidate.priority.value) / 4 * self.resolution_weights['priority'] +
                candidate.context_relevance * self.resolution_weights['context'] +
                candidate.user_preference_score * self.resolution_weights['user_preference'] +
                candidate.temporal_relevance * self.resolution_weights['temporal']
            )
            candidate.metadata['composite_score'] = score
        
        # Sort by composite score
        sorted_candidates = sorted(
            candidates, 
            key=lambda x: x.metadata.get('composite_score', 0), 
            reverse=True
        )
        
        primary = sorted_candidates[0]
        secondary = [c.intent for c in sorted_candidates[1:3]]
        
        return MultiIntentResult(
            primary_intent=primary.intent,
            secondary_intents=secondary,
            resolution_strategy=ResolutionStrategy.CONTEXT_AWARE,
            execution_order=[c.intent for c in sorted_candidates],
            resolution_metadata={
                'composite_scores': {
                    c.intent.value: c.metadata.get('composite_score', 0)
                    for c in candidates
                }
            }
        )
    
    def _resolve_by_user_preference(
        self,
        candidates: List[IntentCandidate],
        context: Optional[Dict[str, Any]] = None
    ) -> MultiIntentResult:
        """Resolve based on user preferences"""
        
        # Sort by user preference scores
        sorted_candidates = sorted(
            candidates, 
            key=lambda x: x.user_preference_score, 
            reverse=True
        )
        
        primary = sorted_candidates[0]
        secondary = [c.intent for c in sorted_candidates[1:3]]
        
        return MultiIntentResult(
            primary_intent=primary.intent,
            secondary_intents=secondary,
            resolution_strategy=ResolutionStrategy.USER_PREFERENCE,
            execution_order=[c.intent for c in sorted_candidates]
        )
    
    def _resolve_sequential(
        self,
        candidates: List[IntentCandidate],
        context: Optional[Dict[str, Any]] = None
    ) -> MultiIntentResult:
        """Resolve for sequential execution"""
        
        # Sort by dependencies and priorities
        completed_intents = context.get('completed_intents', []) if context else []
        
        # Calculate dependency scores
        for candidate in candidates:
            candidate.dependency_score = self.priority_manager.calculate_dependency_score(
                candidate.intent, completed_intents, []
            )
        
        # Sort by dependency satisfaction and priority
        sorted_candidates = sorted(
            candidates,
            key=lambda x: (x.dependency_score, -x.priority.value, x.confidence),
            reverse=True
        )
        
        primary = sorted_candidates[0]
        execution_order = [c.intent for c in sorted_candidates]
        
        return MultiIntentResult(
            primary_intent=primary.intent,
            secondary_intents=[c.intent for c in sorted_candidates[1:]],
            resolution_strategy=ResolutionStrategy.SEQUENTIAL,
            execution_order=execution_order,
            resolution_metadata={
                'dependency_scores': {
                    c.intent.value: c.dependency_score for c in candidates
                }
            }
        )
    
    def _resolve_parallel(
        self,
        candidates: List[IntentCandidate],
        context: Optional[Dict[str, Any]] = None
    ) -> MultiIntentResult:
        """Resolve for parallel execution"""
        
        # Filter out conflicting intents
        non_conflicting = []
        conflicts = []
        
        for candidate in candidates:
            has_conflict = False
            for existing in non_conflicting:
                if self._check_intent_conflict(candidate.intent, existing.intent):
                    has_conflict = True
                    conflicts.append(f"Conflict: {candidate.intent.value} vs {existing.intent.value}")
                    break
            
            if not has_conflict:
                non_conflicting.append(candidate)
        
        if not non_conflicting:
            # Fall back to highest confidence if all conflict
            non_conflicting = [max(candidates, key=lambda x: x.confidence)]
        
        # Sort by composite score
        sorted_candidates = sorted(non_conflicting, key=lambda x: x.confidence, reverse=True)
        
        primary = sorted_candidates[0]
        secondary = [c.intent for c in sorted_candidates[1:]]
        
        return MultiIntentResult(
            primary_intent=primary.intent,
            secondary_intents=secondary,
            resolution_strategy=ResolutionStrategy.PARALLEL,
            execution_order=secondary + [primary.intent],  # Secondary first, then primary
            conflicts_detected=conflicts
        )


class MultiIntentResolver(BaseService):
    """
    Main multi-intent resolution service
    
    Features:
    - Multi-intent detection and analysis
    - Conflict resolution with multiple strategies
    - Execution planning and optimization
    - Performance monitoring and learning
    """
    
    def __init__(self, config: IntentRecognitionConfig):
        super().__init__()
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.priority_manager = IntentPriorityManager()
        self.conflict_resolver = IntentConflictResolver(self.priority_manager)
        
        # Learning and adaptation
        self.resolution_history = []
        self.performance_metrics = {
            'total_resolutions': 0,
            'successful_resolutions': 0,
            'avg_resolution_time': 0.0,
            'strategy_success_rates': {}
        }
    
    async def resolve_multiple_intents(
        self,
        classification_results: List[ClassificationResult],
        strategy: ResolutionStrategy = ResolutionStrategy.CONTEXT_AWARE,
        context: Optional[Dict[str, Any]] = None,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> MultiIntentResult:
        """
        Resolve multiple intent classification results
        
        Args:
            classification_results: List of classification results
            strategy: Resolution strategy to use
            context: Optional conversation context
            user_preferences: Optional user preferences
            
        Returns:
            Multi-intent resolution result
        """
        
        try:
            import time
            start_time = time.time()
            
            # Convert results to candidates
            candidates = await self._create_intent_candidates(
                classification_results, context, user_preferences
            )
            
            if not candidates:
                raise ClassificationError("No valid intent candidates found")
            
            # Detect conflicts
            conflicts = self.conflict_resolver.detect_conflicts(candidates)
            
            # Resolve using specified strategy
            result = self.conflict_resolver.resolve_conflicts(candidates, strategy, context)
            result.conflicts_detected = conflicts
            
            # Update performance metrics
            resolution_time = time.time() - start_time
            await self._update_performance_metrics(strategy, resolution_time, True)
            
            # Store for learning
            self.resolution_history.append({
                'candidates': candidates,
                'result': result,
                'strategy': strategy,
                'context': context,
                'timestamp': time.time()
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Multi-intent resolution failed: {str(e)}")
            await self._update_performance_metrics(strategy, 0, False)
            raise ClassificationError(f"Multi-intent resolution failed: {str(e)}")
    
    async def _create_intent_candidates(
        self,
        classification_results: List[ClassificationResult],
        context: Optional[Dict[str, Any]] = None,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> List[IntentCandidate]:
        """Create intent candidates from classification results"""
        
        candidates = []
        
        for result in classification_results:
            # Primary intent candidate
            primary_candidate = IntentCandidate(
                intent=result.primary_intent,
                confidence=result.confidence.primary_score,
                priority=self.priority_manager.get_intent_priority(result.primary_intent, context),
                context_relevance=self._calculate_context_relevance(result, context),
                user_preference_score=self._calculate_user_preference_score(result, user_preferences),
                temporal_relevance=self._calculate_temporal_relevance(result, context),
                metadata={'source': 'primary', 'original_result': result}
            )
            candidates.append(primary_candidate)
            
            # Secondary intent candidate if available
            if result.secondary_intent and result.confidence.secondary_score:
                secondary_candidate = IntentCandidate(
                    intent=result.secondary_intent,
                    confidence=result.confidence.secondary_score,
                    priority=self.priority_manager.get_intent_priority(result.secondary_intent, context),
                    context_relevance=self._calculate_context_relevance(result, context, secondary=True),
                    user_preference_score=self._calculate_user_preference_score(result, user_preferences, secondary=True),
                    temporal_relevance=self._calculate_temporal_relevance(result, context),
                    metadata={'source': 'secondary', 'original_result': result}
                )
                candidates.append(secondary_candidate)
        
        return candidates
    
    def _calculate_context_relevance(
        self,
        result: ClassificationResult,
        context: Optional[Dict[str, Any]] = None,
        secondary: bool = False
    ) -> float:
        """Calculate context relevance score for intent"""
        if not context:
            return 0.5
        
        intent = result.secondary_intent if secondary else result.primary_intent
        relevance = 0.5  # Base score
        
        # Check conversation stage relevance
        stage = context.get('conversation_stage', '')
        stage_relevance = {
            'content_creation': [
                IntentCategory.CONTENT_UPLOAD, IntentCategory.CONTENT_EDIT,
                IntentCategory.CONTENT_ENHANCE, IntentCategory.CONTENT_GENERATE
            ],
            'protection_setup': [
                IntentCategory.PROTECTION_FINGERPRINT, IntentCategory.PROTECTION_MONITOR,
                IntentCategory.PROTECTION_CONFIGURE
            ],
            'monetization_setup': [
                IntentCategory.MONETIZATION_LICENSE, IntentCategory.MONETIZATION_TRACK,
                IntentCategory.MONETIZATION_ANALYZE
            ]
        }
        
        if stage in stage_relevance and intent in stage_relevance[stage]:
            relevance += 0.3
        
        # Check recent intent patterns
        recent_intents = context.get('recent_intents', [])
        if recent_intents:
            intent_name = intent.value
            if intent_name in recent_intents:
                relevance += 0.2
        
        return min(1.0, relevance)
    
    def _calculate_user_preference_score(
        self,
        result: ClassificationResult,
        user_preferences: Optional[Dict[str, Any]] = None,
        secondary: bool = False
    ) -> float:
        """Calculate user preference score for intent"""
        if not user_preferences:
            return 0.5
        
        intent = result.secondary_intent if secondary else result.primary_intent
        
        # Check intent frequency in user preferences
        intent_freq = user_preferences.get('intent_frequency', {})
        total_uses = sum(intent_freq.values())
        
        if total_uses == 0:
            return 0.5
        
        intent_uses = intent_freq.get(intent.value, 0)
        preference_score = intent_uses / total_uses
        
        # Normalize to 0.1 - 1.0 range
        return 0.1 + (preference_score * 0.9)
    
    def _calculate_temporal_relevance(
        self,
        result: ClassificationResult,
        context: Optional[Dict[str, Any]] = None
    ) -> float:
        """Calculate temporal relevance score"""
        if not context:
            return 0.5
        
        # Simple temporal relevance based on time of day, user activity, etc.
        # In production, this would be more sophisticated
        return 0.7  # Placeholder
    
    async def _update_performance_metrics(
        self,
        strategy: ResolutionStrategy,
        resolution_time: float,
        success: bool
    ) -> None:
        """Update performance metrics"""
        try:
            self.performance_metrics['total_resolutions'] += 1
            
            if success:
                self.performance_metrics['successful_resolutions'] += 1
                
                # Update average resolution time
                current_avg = self.performance_metrics['avg_resolution_time']
                total_resolutions = self.performance_metrics['total_resolutions']
                
                self.performance_metrics['avg_resolution_time'] = (
                    (current_avg * (total_resolutions - 1) + resolution_time) / total_resolutions
                )
            
            # Update strategy success rates
            strategy_name = strategy.value
            if strategy_name not in self.performance_metrics['strategy_success_rates']:
                self.performance_metrics['strategy_success_rates'][strategy_name] = {
                    'attempts': 0, 'successes': 0, 'rate': 0.0
                }
            
            strategy_stats = self.performance_metrics['strategy_success_rates'][strategy_name]
            strategy_stats['attempts'] += 1
            
            if success:
                strategy_stats['successes'] += 1
            
            strategy_stats['rate'] = strategy_stats['successes'] / strategy_stats['attempts']
            
        except Exception as e:
            self.logger.warning(f"Failed to update performance metrics: {str(e)}")
    
    async def suggest_resolution_strategy(
        self,
        classification_results: List[ClassificationResult],
        context: Optional[Dict[str, Any]] = None
    ) -> ResolutionStrategy:
        """Suggest optimal resolution strategy based on situation"""
        
        try:
            # Analyze the situation
            num_intents = len(classification_results)
            max_confidence = max(r.confidence.primary_score for r in classification_results)
            confidence_spread = max_confidence - min(r.confidence.primary_score for r in classification_results)
            
            # Create candidates for conflict analysis
            candidates = await self._create_intent_candidates(classification_results, context)
            conflicts = self.conflict_resolver.detect_conflicts(candidates)
            
            # Decision logic
            if len(conflicts) == 0:
                # No conflicts - consider parallel execution
                return ResolutionStrategy.PARALLEL
            
            elif confidence_spread > 0.3:
                # High confidence spread - use confidence-based
                return ResolutionStrategy.HIGHEST_CONFIDENCE
            
            elif context and context.get('conversation_stage'):
                # Rich context available - use context-aware
                return ResolutionStrategy.CONTEXT_AWARE
            
            elif any('critical' in str(c.priority) for c in candidates):
                # Critical intents present - use priority-based
                return ResolutionStrategy.PRIORITY_BASED
            
            else:
                # Default to sequential for complex scenarios
                return ResolutionStrategy.SEQUENTIAL
                
        except Exception as e:
            self.logger.warning(f"Strategy suggestion failed: {str(e)}")
            return ResolutionStrategy.CONTEXT_AWARE  # Safe default
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for monitoring"""
        return {
            'metrics': self.performance_metrics.copy(),
            'history_size': len(self.resolution_history),
            'recent_strategies': [
                h['strategy'].value for h in self.resolution_history[-10:]
            ],
            'top_performing_strategy': self._get_top_performing_strategy()
        }
    
    def _get_top_performing_strategy(self) -> str:
        """Get the best performing resolution strategy"""
        strategy_rates = self.performance_metrics['strategy_success_rates']
        
        if not strategy_rates:
            return "No data available"
        
        best_strategy = max(
            strategy_rates.items(),
            key=lambda x: x[1]['rate']
        )
        
        return f"{best_strategy[0]} ({best_strategy[1]['rate']:.1%})"
