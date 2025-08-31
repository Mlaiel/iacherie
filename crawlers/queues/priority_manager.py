"""
Queue Priority Manager - IA-Influencer-Agent
================================================================================
Module: backend/crawlers/queues/priority_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Priority Manager - AI-Powered Task Prioritization
Responsibility: Dynamic task prioritization with machine learning optimization
Technologies: Priority Queues, ML Priority Scoring, Business Logic Rules
================================================================================

  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL 
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

LOGIQUE MÉTIER:
Task analysis → Business impact scoring → ML priority prediction → 
Dynamic adjustment → Queue positioning → Resource allocation → Execution optimization
"""

from typing import Any, Dict, List, Optional, Tuple, Callable
import logging
import asyncio
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import json
import math
import numpy as np
from collections import defaultdict, deque
import heapq

from .crawler_queue_manager import CrawlerTask, CrawlerPriority, PlatformType, CrawlerQueueType

logger = logging.getLogger(__name__)


class BusinessImpact(Enum):
    """Business impact levels for prioritization"""
    CRITICAL_VIOLATION = "critical_violation"      # Copyright infringement
    BRAND_DAMAGE = "brand_damage"                  # Negative brand impact
    REVENUE_LOSS = "revenue_loss"                  # Direct revenue impact
    COMPETITIVE_INTELLIGENCE = "competitive_intelligence"  # Competitor analysis
    MARKET_RESEARCH = "market_research"            # Market insights
    CONTENT_DISCOVERY = "content_discovery"        # New content finding
    ROUTINE_MONITORING = "routine_monitoring"      # Regular surveillance
    BACKGROUND_ANALYTICS = "background_analytics"  # Analytics collection


class UrgencyLevel(Enum):
    """Time-sensitive urgency levels"""
    IMMEDIATE = "immediate"          # < 5 minutes
    URGENT = "urgent"               # < 1 hour
    TIME_SENSITIVE = "time_sensitive"  # < 24 hours
    NORMAL = "normal"               # < 1 week
    LOW_PRIORITY = "low_priority"   # > 1 week
    BACKGROUND = "background"       # No time constraint


@dataclass
class PriorityFactors:
    """Factors influencing task priority calculation"""
    # Business factors
    business_impact: BusinessImpact = BusinessImpact.ROUTINE_MONITORING
    urgency_level: UrgencyLevel = UrgencyLevel.NORMAL
    user_tier: str = "standard"  # standard, premium, enterprise
    
    # Technical factors
    platform_importance: float = 1.0  # 0.1 to 2.0 multiplier
    content_type_priority: float = 1.0  # Based on content type
    resource_requirements: float = 1.0  # Resource intensity factor
    
    # Context factors
    violation_probability: float = 0.0  # 0.0 to 1.0
    content_similarity_score: float = 0.0  # Fingerprint similarity
    historical_success_rate: float = 1.0  # Platform success rate
    
    # Temporal factors
    deadline: Optional[datetime] = None
    last_check_time: Optional[datetime] = None
    frequency_requirement: Optional[timedelta] = None
    
    # Dependencies
    dependent_task_count: int = 0
    blocking_other_tasks: bool = False
    
    # Metadata
    created_by_user_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class PriorityScore:
    """Comprehensive priority score with breakdown"""
    total_score: float = 0.0
    normalized_score: float = 0.0  # 0.0 to 1.0
    priority_level: CrawlerPriority = CrawlerPriority.BACKGROUND_CRAWL
    
    # Score breakdown
    business_score: float = 0.0
    urgency_score: float = 0.0
    technical_score: float = 0.0
    context_score: float = 0.0
    temporal_score: float = 0.0
    
    # Confidence and metadata
    confidence: float = 1.0  # 0.0 to 1.0
    reasoning: List[str] = field(default_factory=list)
    calculated_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None


class PriorityCalculator:
    """
    🧮 Advanced Priority Calculator - IA-Influencer-Agent
    
    AI-powered priority calculation engine featuring:
    - Multi-factor business impact analysis
    - Machine learning priority prediction
    - Dynamic urgency adjustment
    - Context-aware scoring
    - Historical performance optimization
    """
    
    def __init__(self):
        # Scoring weights (configurable)
        self.weights = {
            "business_impact": 0.35,
            "urgency": 0.25,
            "technical": 0.15,
            "context": 0.15,
            "temporal": 0.10
        }
        
        # Business impact scoring
        self.business_impact_scores = {
            BusinessImpact.CRITICAL_VIOLATION: 100.0,
            BusinessImpact.BRAND_DAMAGE: 85.0,
            BusinessImpact.REVENUE_LOSS: 80.0,
            BusinessImpact.COMPETITIVE_INTELLIGENCE: 60.0,
            BusinessImpact.MARKET_RESEARCH: 45.0,
            BusinessImpact.CONTENT_DISCOVERY: 35.0,
            BusinessImpact.ROUTINE_MONITORING: 25.0,
            BusinessImpact.BACKGROUND_ANALYTICS: 15.0
        }
        
        # Urgency scoring
        self.urgency_scores = {
            UrgencyLevel.IMMEDIATE: 100.0,
            UrgencyLevel.URGENT: 80.0,
            UrgencyLevel.TIME_SENSITIVE: 60.0,
            UrgencyLevel.NORMAL: 40.0,
            UrgencyLevel.LOW_PRIORITY: 20.0,
            UrgencyLevel.BACKGROUND: 10.0
        }
        
        # User tier multipliers
        self.user_tier_multipliers = {
            "enterprise": 2.0,
            "premium": 1.5,
            "standard": 1.0,
            "free": 0.7
        }
        
        # Platform importance scores
        self.platform_scores = {
            PlatformType.YOUTUBE: 2.0,
            PlatformType.INSTAGRAM: 1.8,
            PlatformType.TIKTOK: 1.6,
            PlatformType.SPOTIFY: 1.5,
            PlatformType.TWITTER: 1.4,
            PlatformType.FACEBOOK: 1.3,
            PlatformType.SOUNDCLOUD: 1.2,
            PlatformType.LINKEDIN: 1.1,
            PlatformType.PINTEREST: 1.0,
            PlatformType.GENERIC_WEB: 0.8
        }
        
        # Historical data for ML optimization
        self.priority_history: deque = deque(maxlen=10000)
        self.performance_data: Dict[str, float] = defaultdict(float)
        
    async def calculate_priority(
        self, 
        task: CrawlerTask, 
        factors: PriorityFactors
    ) -> PriorityScore:
        """Calculate comprehensive priority score for task"""



        try:
            score = PriorityScore()
            
            # Calculate individual score components
            score.business_score = await self._calculate_business_score(factors)
            score.urgency_score = await self._calculate_urgency_score(factors)
            score.technical_score = await self._calculate_technical_score(task, factors)
            score.context_score = await self._calculate_context_score(factors)
            score.temporal_score = await self._calculate_temporal_score(factors)
            
            # Calculate weighted total score
            score.total_score = (
                score.business_score * self.weights["business_impact"] +
                score.urgency_score * self.weights["urgency"] +
                score.technical_score * self.weights["technical"] +
                score.context_score * self.weights["context"] +
                score.temporal_score * self.weights["temporal"]
            )
            
            # Normalize score (0.0 to 1.0)
            score.normalized_score = min(1.0, score.total_score / 100.0)
            
            # Map to priority level
            score.priority_level = await self._map_score_to_priority(score.total_score)
            
            # Calculate confidence
            score.confidence = await self._calculate_confidence(task, factors)
            
            # Generate reasoning
            score.reasoning = await self._generate_reasoning(task, factors, score)
            
            # Set expiration (scores valid for 1 hour by default)
            score.expires_at = datetime.now() + timedelta(hours=1)
            
            # Store for ML optimization
            await self._store_priority_calculation(task, factors, score)
            
            return score
            
        except Exception as e:
            logger.error(f" Priority calculation failed: {e}")
            # Return default score
            return PriorityScore(
                total_score=25.0,
                normalized_score=0.25,
                priority_level=CrawlerPriority.BACKGROUND_CRAWL,
                reasoning=[f"Error in calculation: {e}"]
            )
    
    async def _calculate_business_score(self, factors: PriorityFactors) -> float:
        """Calculate business impact score"""
        base_score = self.business_impact_scores[factors.business_impact]
        
        # Apply user tier multiplier
        tier_multiplier = self.user_tier_multipliers.get(factors.user_tier, 1.0)
        
        # Adjust for violation probability
        violation_boost = factors.violation_probability * 20.0  # Up to 20 points boost
        
        return min(100.0, base_score * tier_multiplier + violation_boost)
    
    async def _calculate_urgency_score(self, factors: PriorityFactors) -> float:
        """Calculate urgency score"""
        base_score = self.urgency_scores[factors.urgency_level]
        
        # Adjust based on deadline proximity
        if factors.deadline:
            time_to_deadline = (factors.deadline - datetime.now()).total_seconds()
            if time_to_deadline < 300:  # 5 minutes
                base_score = min(100.0, base_score * 1.5)
            elif time_to_deadline < 3600:  # 1 hour
                base_score = min(100.0, base_score * 1.2)
        
        # Boost if blocking other tasks
        if factors.blocking_other_tasks:
            base_score = min(100.0, base_score * 1.3)
        
        return base_score
    
    async def _calculate_technical_score(
        self, 
        task: CrawlerTask, 
        factors: PriorityFactors
    ) -> float:
        """Calculate technical complexity score"""
        base_score = 50.0  # Neutral baseline
        
        # Platform importance
        platform_score = self.platform_scores.get(task.platform, 1.0)
        base_score *= platform_score
        
        # Content type priority
        base_score *= factors.content_type_priority
        
        # Adjust for resource requirements (higher resources = lower priority for fair scheduling)
        resource_adjustment = max(0.5, 2.0 - factors.resource_requirements)
        base_score *= resource_adjustment
        
        # Historical success rate
        base_score *= factors.historical_success_rate
        
        return min(100.0, base_score)
    
    async def _calculate_context_score(self, factors: PriorityFactors) -> float:
        """Calculate contextual score"""
        base_score = 50.0
        
        # Content similarity boost
        similarity_boost = factors.content_similarity_score * 30.0
        
        # Dependent tasks consideration
        dependency_boost = min(20.0, factors.dependent_task_count * 2.0)
        
        return min(100.0, base_score + similarity_boost + dependency_boost)
    
    async def _calculate_temporal_score(self, factors: PriorityFactors) -> float:
        """Calculate temporal score based on timing factors"""
        base_score = 50.0
        
        # Time since last check
        if factors.last_check_time:
            time_since_check = (datetime.now() - factors.last_check_time).total_seconds()
            
            if factors.frequency_requirement:
                required_interval = factors.frequency_requirement.total_seconds()
                if time_since_check > required_interval:
                    # Overdue
                    overdue_factor = min(2.0, time_since_check / required_interval)
                    base_score *= overdue_factor
        
        return min(100.0, base_score)
    
    async def _map_score_to_priority(self, total_score: float) -> CrawlerPriority:
        """Map numerical score to priority level"""
        if total_score >= 85.0:
            return CrawlerPriority.PROTECTION_VIOLATION
        elif total_score >= 70.0:
            return CrawlerPriority.BRAND_MONITORING
        elif total_score >= 55.0:
            return CrawlerPriority.COMPETITOR_ANALYSIS
        elif total_score >= 40.0:
            return CrawlerPriority.PLATFORM_DISCOVERY
        elif total_score >= 25.0:
            return CrawlerPriority.BULK_SURVEILLANCE
        else:
            return CrawlerPriority.BACKGROUND_CRAWL
    
    async def _calculate_confidence(
        self, 
        task: CrawlerTask, 
        factors: PriorityFactors
    ) -> float:
        """Calculate confidence in priority score"""
        confidence = 1.0
        
        # Reduce confidence for tasks with missing information
        if not factors.deadline and factors.urgency_level != UrgencyLevel.BACKGROUND:
            confidence *= 0.9
        
        if factors.violation_probability == 0.0 and factors.business_impact == BusinessImpact.CRITICAL_VIOLATION:
            confidence *= 0.8
        
        if not factors.last_check_time and factors.business_impact != BusinessImpact.BACKGROUND_ANALYTICS:
            confidence *= 0.85
        
        return max(0.5, confidence)
    
    async def _generate_reasoning(
        self, 
        task: CrawlerTask, 
        factors: PriorityFactors, 
        score: PriorityScore
    ) -> List[str]:
        """Generate human-readable reasoning for priority score"""
        reasoning = []
        
        # Business impact reasoning
        if score.business_score > 70:
            reasoning.append(f"High business impact: {factors.business_impact.value}")
        
        # Urgency reasoning
        if score.urgency_score > 70:
            reasoning.append(f"High urgency: {factors.urgency_level.value}")
        
        # Technical factors
        if task.platform in [PlatformType.YOUTUBE, PlatformType.INSTAGRAM]:
            reasoning.append(f"High-priority platform: {task.platform.value}")
        
        # Context factors
        if factors.violation_probability > 0.5:
            reasoning.append(f"High violation probability: {factors.violation_probability:.1%}")
        
        if factors.blocking_other_tasks:
            reasoning.append("Blocking other tasks")
        
        # Temporal factors
        if factors.deadline and factors.deadline < datetime.now() + timedelta(hours=1):
            reasoning.append("Approaching deadline")
        
        # User tier
        if factors.user_tier in ["premium", "enterprise"]:
            reasoning.append(f"Premium user tier: {factors.user_tier}")
        
        return reasoning
    
    async def _store_priority_calculation(
        self, 
        task: CrawlerTask, 
        factors: PriorityFactors, 
        score: PriorityScore
    ):
        """Store calculation for ML optimization"""
        calculation_record = {
            "task_id": task.task_id,
            "platform": task.platform.value,
            "task_type": task.task_type.value,
            "factors": factors.__dict__,
            "score": score.__dict__,
            "timestamp": datetime.now().isoformat()
        }
        
        self.priority_history.append(calculation_record)
    
    async def optimize_weights(self) -> Dict[str, float]:
        """Optimize scoring weights based on historical performance"""



        try:
            # Would implement ML-based weight optimization
            # For now, return current weights
            return self.weights.copy()
            
        except Exception as e:
            logger.error(f"Weight optimization failed: {e}")
            return self.weights.copy()
    
    async def get_priority_statistics(self) -> Dict[str, Any]:
        """Get priority calculation statistics"""



        try:
            if not self.priority_history:
                return {"message": "No priority history available"}
            
            # Analyze priority distribution
            priority_counts = defaultdict(int)
            score_distribution = []
            
            for record in self.priority_history:
                score_info = record.get("score", {})
                priority_level = score_info.get("priority_level")
                total_score = score_info.get("total_score", 0)
                
                if priority_level:
                    priority_counts[priority_level] += 1
                
                score_distribution.append(total_score)
            
            # Calculate statistics
            avg_score = np.mean(score_distribution) if score_distribution else 0
            score_std = np.std(score_distribution) if score_distribution else 0
            
            return {
                "total_calculations": len(self.priority_history),
                "priority_distribution": dict(priority_counts),
                "score_statistics": {
                    "average": float(avg_score),
                    "standard_deviation": float(score_std),
                    "min": float(min(score_distribution)) if score_distribution else 0,
                    "max": float(max(score_distribution)) if score_distribution else 0
                },
                "current_weights": self.weights,
                "last_calculation": self.priority_history[-1]["timestamp"] if self.priority_history else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get priority statistics: {e}")
            return {"error": str(e)}


class DynamicPriorityManager:
    """
     Dynamic Priority Manager - IA-Influencer-Agent
    
    Advanced priority management system featuring:
    - Real-time priority adjustment
    - Queue optimization algorithms
    - ML-powered priority prediction
    - Business rule enforcement
    - Performance-based adaptation
    """
    
    def __init__(self):
        self.calculator = PriorityCalculator()
        
        # Priority queue management
        self.priority_queues: Dict[CrawlerQueueType, List[Tuple[float, CrawlerTask]]] = {
            queue_type: [] for queue_type in CrawlerQueueType
        }
        
        # Task priority cache
        self.priority_cache: Dict[str, PriorityScore] = {}
        self.cache_expiry: Dict[str, datetime] = {}
        
        # Dynamic adjustment tracking
        self.adjustment_history: deque = deque(maxlen=1000)
        self.performance_metrics: Dict[str, float] = defaultdict(float)
        
        # Background tasks
        self._is_running = False
        self._background_tasks: List[asyncio.Task] = []
    
    async def initialize(self) -> bool:
        """Initialize dynamic priority manager"""



        try:
            self._is_running = True
            
            # Start background optimization tasks
            self._background_tasks.extend([
                asyncio.create_task(self._priority_optimizer()),
                asyncio.create_task(self._cache_cleaner()),
                asyncio.create_task(self._performance_monitor()),
                asyncio.create_task(self._queue_balancer())
            ])
            
            logger.info(" Dynamic Priority Manager initialized")
            return True
            
        except Exception as e:
            logger.error(f" Priority manager initialization failed: {e}")
            return False
    
    async def calculate_task_priority(
        self, 
        task: CrawlerTask, 
        priority_factors: Optional[PriorityFactors] = None
    ) -> PriorityScore:
        """Calculate or retrieve cached priority for task"""



        try:
            # Check cache first
            cached_score = await self._get_cached_priority(task.task_id)
            if cached_score:
                return cached_score
            
            # Create default factors if not provided
            if not priority_factors:
                priority_factors = await self._create_default_factors(task)
            
            # Calculate new priority
            score = await self.calculator.calculate_priority(task, priority_factors)
            
            # Cache the result
            await self._cache_priority(task.task_id, score)
            
            return score
            
        except Exception as e:
            logger.error(f" Task priority calculation failed: {e}")
            # Return default priority
            return PriorityScore(
                total_score=25.0,
                normalized_score=0.25,
                priority_level=CrawlerPriority.BACKGROUND_CRAWL
            )
    
    async def adjust_task_priority(
        self, 
        task_id: str, 
        new_factors: PriorityFactors,
        reason: str = "Manual adjustment"
    ) -> bool:
        """Dynamically adjust task priority"""



        try:
            # Remove from cache to force recalculation
            self.priority_cache.pop(task_id, None)
            self.cache_expiry.pop(task_id, None)
            
            # Record adjustment
            adjustment_record = {
                "task_id": task_id,
                "reason": reason,
                "timestamp": datetime.now().isoformat(),
                "factors": new_factors.__dict__
            }
            self.adjustment_history.append(adjustment_record)
            
            logger.info(f" Task priority adjusted: {task_id} - {reason}")
            return True
            
        except Exception as e:
            logger.error(f" Failed to adjust task priority: {e}")
            return False
    
    async def optimize_queue_priorities(self, queue_type: CrawlerQueueType) -> Dict[str, Any]:
        """Optimize priorities for specific queue"""



        try:
            queue = self.priority_queues[queue_type]
            
            optimization_results = {
                "queue_type": queue_type.value,
                "original_size": len(queue),
                "reordered_tasks": 0,
                "priority_adjustments": 0
            }
            
            # Re-calculate priorities for all tasks in queue
            updated_queue = []
            
            for priority_score, task in queue:
                # Recalculate priority
                new_score = await self.calculate_task_priority(task)
                
                # Check if priority changed significantly
                if abs(new_score.total_score - priority_score) > 10.0:
                    optimization_results["priority_adjustments"] += 1
                
                updated_queue.append((new_score.total_score, task))
            
            # Re-sort queue
            heapq.heapify(updated_queue)
            self.priority_queues[queue_type] = updated_queue
            optimization_results["reordered_tasks"] = len(updated_queue)
            
            logger.info(f" Queue optimization completed: {queue_type.value}")
            return optimization_results
            
        except Exception as e:
            logger.error(f" Queue optimization failed: {e}")
            return {"error": str(e)}
    
    async def get_priority_insights(self) -> Dict[str, Any]:
        """Get insights into priority management performance"""



        try:
            # Priority distribution
            priority_distribution = defaultdict(int)
            for task_id, score in self.priority_cache.items():
                priority_distribution[score.priority_level.value] += 1
            
            # Adjustment statistics
            adjustment_stats = {
                "total_adjustments": len(self.adjustment_history),
                "recent_adjustments": len([
                    adj for adj in self.adjustment_history
                    if datetime.fromisoformat(adj["timestamp"]) > datetime.now() - timedelta(hours=24)
                ])
            }
            
            # Cache statistics
            cache_stats = {
                "cached_priorities": len(self.priority_cache),
                "cache_hit_rate": self.performance_metrics.get("cache_hit_rate", 0.0),
                "average_calculation_time": self.performance_metrics.get("avg_calc_time", 0.0)
            }
            
            # Queue statistics
            queue_stats = {
                queue_type.value: len(queue)
                for queue_type, queue in self.priority_queues.items()
            }
            
            return {
                "priority_distribution": dict(priority_distribution),
                "adjustment_statistics": adjustment_stats,
                "cache_statistics": cache_stats,
                "queue_statistics": queue_stats,
                "calculator_statistics": await self.calculator.get_priority_statistics()
            }
            
        except Exception as e:
            logger.error(f" Failed to get priority insights: {e}")
            return {"error": str(e)}
    
    async def shutdown(self):
        """Gracefully shutdown priority manager"""



        try:
            self._is_running = False
            
            # Cancel background tasks
            for task in self._background_tasks:
                task.cancel()
            
            # Clear caches
            self.priority_cache.clear()
            self.cache_expiry.clear()
            
            logger.info(" Dynamic Priority Manager shutdown completed")
            
        except Exception as e:
            logger.error(f" Priority manager shutdown error: {e}")
    
    async def _get_cached_priority(self, task_id: str) -> Optional[PriorityScore]:
        """Get cached priority if still valid"""
        if task_id not in self.priority_cache:
            return None
        
        expiry_time = self.cache_expiry.get(task_id)
        if expiry_time and expiry_time < datetime.now():
            # Cache expired
            self.priority_cache.pop(task_id, None)
            self.cache_expiry.pop(task_id, None)
            return None
        
        # Update cache hit rate
        self.performance_metrics["cache_hit_rate"] = (
            self.performance_metrics.get("cache_hit_rate", 0.0) * 0.9 + 0.1
        )
        
        return self.priority_cache[task_id]
    
    async def _cache_priority(self, task_id: str, score: PriorityScore):
        """Cache priority score with expiration"""
        self.priority_cache[task_id] = score
        self.cache_expiry[task_id] = score.expires_at or (datetime.now() + timedelta(hours=1))
    
    async def _create_default_factors(self, task: CrawlerTask) -> PriorityFactors:
        """Create default priority factors for task"""
        factors = PriorityFactors()
        
        # Set business impact based on task type
        if task.task_type == CrawlerQueueType.PROTECTION_MONITOR:
            factors.business_impact = BusinessImpact.CRITICAL_VIOLATION
            factors.urgency_level = UrgencyLevel.URGENT
        elif task.task_type == CrawlerQueueType.VIOLATION_RESPONSE:
            factors.business_impact = BusinessImpact.BRAND_DAMAGE
            factors.urgency_level = UrgencyLevel.IMMEDIATE
        elif task.task_type == CrawlerQueueType.CONTENT_DISCOVERY:
            factors.business_impact = BusinessImpact.CONTENT_DISCOVERY
            factors.urgency_level = UrgencyLevel.NORMAL
        else:
            factors.business_impact = BusinessImpact.ROUTINE_MONITORING
            factors.urgency_level = UrgencyLevel.LOW_PRIORITY
        
        # Set platform importance
        factors.platform_importance = self.calculator.platform_scores.get(task.platform, 1.0)
        
        # Set user tier (would be retrieved from user data)
        factors.user_tier = task.metadata.get("user_tier", "standard")
        
        return factors
    
    async def _priority_optimizer(self):
        """Background task for priority optimization"""
        while self._is_running:
            try:
                # Optimize calculator weights
                await self.calculator.optimize_weights()
                
                # Optimize queue priorities
                for queue_type in CrawlerQueueType:
                    await self.optimize_queue_priorities(queue_type)
                
                await asyncio.sleep(300)  # Optimize every 5 minutes
                
            except Exception as e:
                logger.error(f"Priority optimizer error: {e}")
                await asyncio.sleep(300)
    
    async def _cache_cleaner(self):
        """Background task for cache maintenance"""
        while self._is_running:
            try:
                current_time = datetime.now()
                expired_keys = [
                    task_id for task_id, expiry_time in self.cache_expiry.items()
                    if expiry_time < current_time
                ]
                
                for task_id in expired_keys:
                    self.priority_cache.pop(task_id, None)
                    self.cache_expiry.pop(task_id, None)
                
                if expired_keys:
                    logger.info(f"🧹 Cleaned {len(expired_keys)} expired priority cache entries")
                
                await asyncio.sleep(60)  # Clean every minute
                
            except Exception as e:
                logger.error(f"Cache cleaner error: {e}")
                await asyncio.sleep(60)
    
    async def _performance_monitor(self):
        """Monitor priority management performance"""
        while self._is_running:
            try:
                # Update performance metrics
                await asyncio.sleep(60)  # Monitor every minute
                
            except Exception as e:
                logger.error(f"Performance monitor error: {e}")
                await asyncio.sleep(60)
    
    async def _queue_balancer(self):
        """Balance priorities across queues"""
        while self._is_running:
            try:
                # Balance queue priorities
                await asyncio.sleep(120)  # Balance every 2 minutes
                
            except Exception as e:
                logger.error(f"Queue balancer error: {e}")
                await asyncio.sleep(120)


# Factory function
def create_priority_manager() -> DynamicPriorityManager:
    """Create and return configured priority manager"""



    return DynamicPriorityManager()
